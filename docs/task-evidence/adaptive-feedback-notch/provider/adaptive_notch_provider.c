/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered reference for adaptive feedback notch control.
 *
 * It uses only the public v0 provider table in audio_sdk/provider_v0.h. This
 * source is NOT part of the installed SDK, its registry or any default build.
 * It mirrors the detector/notch portion of the Python fixture for boundary
 * smoke checks only; it does not claim parity with the full DSP report.
 */
#include "audio_sdk/session_v0.h"
#include "adaptive_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define ADAPTIVE_BINS 39u
#define ADAPTIVE_MIN_BIN 2u
#define ADAPTIVE_MAX_NOTCHES 4u
#define ADAPTIVE_PERSISTENCE 4
#define ADAPTIVE_RELEASE 24
#define ADAPTIVE_COOLDOWN 60
#define ADAPTIVE_PROMINENCE_DB 14.0
#define ADAPTIVE_ABSOLUTE_DBFS -38.0
#define ADAPTIVE_Q 24.0
#define ADAPTIVE_RATE 16000.0

typedef struct adaptive_notch_s {
    int active;
    int frequency_hz;
    int bin_index;
    int age_frames;
    int miss_frames;
    double b0, b1, b2, a1, a2;
    double z1, z2;
} adaptive_notch;

typedef struct adaptive_instance_s {
    double cos_table[ADAPTIVE_BINS][AS_FRAME_SAMPLES];
    double sin_table[ADAPTIVE_BINS][AS_FRAME_SAMPLES];
    double window_power;
    int runs[ADAPTIVE_BINS];
    int cooldowns[ADAPTIVE_BINS];
    adaptive_notch notches[ADAPTIVE_MAX_NOTCHES];
    uint32_t notch_count;
    int64_t output_start;
    int64_t accepted_end;
    uint64_t epoch;
    int have_position;
} adaptive_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void design_tables(adaptive_instance *instance) {
    instance->window_power = 0.0;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        const double window = 0.5 - 0.5 * cos(
            2.0 * 3.14159265358979323846 * (double)n /
            (double)(AS_FRAME_SAMPLES - 1u));
        instance->window_power += window * window;
    }
    for (uint32_t bin = 0; bin < ADAPTIVE_BINS; ++bin) {
        const double frequency = (double)(ADAPTIVE_MIN_BIN + bin) * 100.0;
        for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
            const double phase = 2.0 * 3.14159265358979323846 * frequency *
                                 (double)n / ADAPTIVE_RATE;
            instance->cos_table[bin][n] = cos(phase);
            instance->sin_table[bin][n] = sin(phase);
        }
    }
}

static void design_notch(adaptive_notch *notch) {
    const double frequency = (double)notch->frequency_hz;
    const double omega = 2.0 * 3.14159265358979323846 * frequency / ADAPTIVE_RATE;
    const double cosine = cos(omega);
    const double alpha = sin(omega) / (2.0 * ADAPTIVE_Q);
    const double a0 = 1.0 + alpha;
    notch->b0 = 1.0 / a0;
    notch->b1 = (-2.0 * cosine) / a0;
    notch->b2 = 1.0 / a0;
    notch->a1 = (-2.0 * cosine) / a0;
    notch->a2 = (1.0 - alpha) / a0;
}

static double frame_db(const adaptive_instance *instance,
                       const float *input, uint32_t bin) {
    double real = 0.0;
    double imag = 0.0;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        const double sample = (double)input[n];
        real += sample * instance->cos_table[bin][n];
        imag += sample * instance->sin_table[bin][n];
    }
    const double normalization = instance->window_power * instance->window_power;
    const double power = (real * real + imag * imag) / normalization;
    return 10.0 * log10(power > 1e-30 ? power : 1e-30);
}

static as_status_v0 AS_CALL adaptive_create(const as_create_config_v0 *config,
                                            void **out_instance,
                                            as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) {
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 0 || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        ADAPTIVE_PROVIDER_ID, strlen(ADAPTIVE_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    adaptive_instance *instance = (adaptive_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    design_tables(instance);
    instance->epoch = config->epoch;
    instance->output_start = config->first_input_sample;
    instance->accepted_end = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL adaptive_process(void *opaque,
                                             const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    adaptive_instance *instance = (adaptive_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        if (!isfinite((double)frame->input[i])) return AS_INVALID_ARGUMENT;
    }
    const int64_t source_first = frame->first_input_sample;
    if (!instance->have_position) {
        instance->output_start = source_first;
        instance->have_position = 1;
    }
    if (instance->output_start != source_first) return AS_BACKEND_FAILURE;

    double levels[ADAPTIVE_BINS];
    int detected[ADAPTIVE_BINS];
    for (uint32_t bin = 0; bin < ADAPTIVE_BINS; ++bin) {
        levels[bin] = frame_db(instance, frame->input, bin);
        detected[bin] = 0;
    }
    for (uint32_t bin = 0; bin < ADAPTIVE_BINS; ++bin) {
        const double left = bin > 0 ? levels[bin - 1] : -300.0;
        const double right = bin + 1 < ADAPTIVE_BINS ? levels[bin + 1] : -300.0;
        const double maximum_neighbor = left > right ? left : right;
        if (levels[bin] - maximum_neighbor >= ADAPTIVE_PROMINENCE_DB &&
            levels[bin] >= ADAPTIVE_ABSOLUTE_DBFS) {
            ++instance->runs[bin];
            if (instance->runs[bin] >= ADAPTIVE_PERSISTENCE) detected[bin] = 1;
        } else {
            instance->runs[bin] = 0;
        }
    }

    for (uint32_t index = 0; index < instance->notch_count;) {
        adaptive_notch *notch = &instance->notches[index];
        const int present = detected[notch->bin_index];
        notch->miss_frames = present ? 0 : notch->miss_frames + 1;
        if (notch->miss_frames >= ADAPTIVE_RELEASE) {
            instance->cooldowns[notch->bin_index] = ADAPTIVE_COOLDOWN;
            for (uint32_t tail = index + 1; tail < instance->notch_count; ++tail)
                instance->notches[tail - 1u] = instance->notches[tail];
            --instance->notch_count;
        } else {
            ++notch->age_frames;
            design_notch(notch);
            ++index;
        }
    }
    for (uint32_t bin = 0; bin < ADAPTIVE_BINS; ++bin) {
        if (instance->cooldowns[bin] > 0) --instance->cooldowns[bin];
    }

    for (uint32_t bin = 0; bin < ADAPTIVE_BINS; ++bin) {
        if (!detected[bin] || instance->notch_count >= ADAPTIVE_MAX_NOTCHES ||
            instance->cooldowns[bin] > 0) {
            continue;
        }
        int already_active = 0;
        for (uint32_t index = 0; index < instance->notch_count; ++index) {
            if (instance->notches[index].bin_index == (int)bin) already_active = 1;
        }
        if (already_active) continue;
        adaptive_notch *notch = &instance->notches[instance->notch_count++];
        memset(notch, 0, sizeof(*notch));
        notch->active = 1;
        notch->bin_index = (int)bin;
        notch->frequency_hz = (int)(ADAPTIVE_MIN_BIN + bin) * 100;
        design_notch(notch);
    }

    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        double filtered = (double)frame->input[i];
        for (uint32_t index = 0; index < instance->notch_count; ++index) {
            adaptive_notch *notch = &instance->notches[index];
            const double y = notch->b0 * filtered + notch->z1;
            notch->z1 = notch->b1 * filtered - notch->a1 * y + notch->z2;
            notch->z2 = notch->b2 * filtered - notch->a2 * y;
            filtered = y;
        }
        output->samples[i] = (float)filtered;
    }
    instance->accepted_end = source_first + (int64_t)(
        (frame->flags & AS_FRAME_FINAL_INPUT) ? frame->input_valid_count
                                               : AS_FRAME_SAMPLES);
    instance->output_start += AS_FRAME_SAMPLES;
    instance->epoch = frame->epoch;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = source_first;
    return AS_OK;
}

static as_status_v0 AS_CALL adaptive_reset(void *opaque, uint64_t epoch,
                                           int64_t first_input_sample,
                                           as_error_v0 *error) {
    (void)error;
    adaptive_instance *instance = (adaptive_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->runs, 0, sizeof(instance->runs));
    memset(instance->cooldowns, 0, sizeof(instance->cooldowns));
    memset(instance->notches, 0, sizeof(instance->notches));
    instance->notch_count = 0;
    instance->output_start = first_input_sample;
    instance->accepted_end = first_input_sample;
    instance->epoch = epoch;
    instance->have_position = 1;
    return AS_OK;
}

static as_status_v0 AS_CALL adaptive_drain(void *opaque,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    adaptive_instance *instance = (adaptive_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL adaptive_destroy(void *opaque) { free(opaque); }

as_status_v0 adaptive_notch_register(as_registry_v0 *registry,
                                     as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        adaptive_create, adaptive_process, adaptive_reset, adaptive_drain,
        adaptive_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
