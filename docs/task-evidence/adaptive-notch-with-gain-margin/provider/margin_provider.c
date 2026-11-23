/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered reference for adaptive notch plus bounded margin.
 *
 * Only the public v0 provider table in audio_sdk/provider_v0.h is used. This
 * file is NOT part of the installed SDK, its registry, any default build or
 * any public catalog. It is a boundary smoke check: the Python fixture in the
 * parent directory owns the full DSP report and the fixed-gain comparison.
 */
#include "audio_sdk/session_v0.h"
#include "margin_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define MARGIN_BINS 39u
#define MARGIN_MIN_BIN 2u
#define MARGIN_MAX_NOTCHES 4u
#define MARGIN_PERSISTENCE 4
#define MARGIN_RELEASE 24
#define MARGIN_COOLDOWN 60
#define MARGIN_RECOVERY_FRAMES 200
#define MARGIN_PROMINENCE_DB 10.0
#define MARGIN_ABSOLUTE_DBFS -38.0
#define MARGIN_Q 24.0
#define MARGIN_STEP_DB 3.0
#define MARGIN_FLOOR_DB -12.0
#define MARGIN_RECOVERY_DB 0.1
#define MARGIN_RATE 16000.0
#define MARGIN_PI 3.14159265358979323846

typedef struct margin_notch_s {
    int bin_index;
    int frequency_hz;
    int miss_frames;
    double b0, b1, b2, a1, a2;
    double z1, z2;
} margin_notch;

typedef struct margin_instance_s {
    double cos_table[MARGIN_BINS][AS_FRAME_SAMPLES];
    double sin_table[MARGIN_BINS][AS_FRAME_SAMPLES];
    double window_power;
    int runs[MARGIN_BINS];
    int cooldowns[MARGIN_BINS];
    margin_notch notches[MARGIN_MAX_NOTCHES];
    uint32_t notch_count;
    uint32_t previous_runs;
    double gain_db;
    int quiet_frames;
    uint64_t epoch;
    int64_t next_input_sample;
    int have_position;
} margin_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void design_tables(margin_instance *instance) {
    instance->window_power = 0.0;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        const double window = 0.5 - 0.5 * cos(
            2.0 * MARGIN_PI * (double)n / (double)(AS_FRAME_SAMPLES - 1u));
        instance->window_power += window * window;
    }
    for (uint32_t bin = 0; bin < MARGIN_BINS; ++bin) {
        const double frequency = (double)(MARGIN_MIN_BIN + bin) * 100.0;
        for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
            const double phase = 2.0 * MARGIN_PI * frequency *
                                 (double)n / MARGIN_RATE;
            instance->cos_table[bin][n] = cos(phase);
            instance->sin_table[bin][n] = sin(phase);
        }
    }
}

static void design_notch(margin_notch *notch) {
    const double frequency = (double)notch->frequency_hz;
    const double omega = 2.0 * MARGIN_PI * frequency / MARGIN_RATE;
    const double cosine = cos(omega);
    const double alpha = sin(omega) / (2.0 * MARGIN_Q);
    const double a0 = 1.0 + alpha;
    notch->b0 = 1.0 / a0;
    notch->b1 = (-2.0 * cosine) / a0;
    notch->b2 = 1.0 / a0;
    notch->a1 = (-2.0 * cosine) / a0;
    notch->a2 = (1.0 - alpha) / a0;
}

static double frame_db(const margin_instance *instance,
                       const float *input, uint32_t bin) {
    double real = 0.0;
    double imag = 0.0;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        const double sample = (double)input[n];
        real += sample * instance->cos_table[bin][n];
        imag += sample * instance->sin_table[bin][n];
    }
    const double power = (real * real + imag * imag) /
                         (instance->window_power * instance->window_power);
    return 10.0 * log10(power > 1e-30 ? power : 1e-30);
}

static as_status_v0 AS_CALL margin_create(const as_create_config_v0 *config,
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
                        MARGIN_PROVIDER_ID, strlen(MARGIN_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    margin_instance *instance = (margin_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    design_tables(instance);
    instance->epoch = config->epoch;
    instance->next_input_sample = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL margin_process(void *opaque,
                                           const as_frame_v0 *frame,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    margin_instance *instance = (margin_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES) return AS_INVALID_ARGUMENT;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        if (!isfinite((double)frame->input[i])) return AS_INVALID_ARGUMENT;
    }
    if (!instance->have_position) {
        instance->epoch = frame->epoch;
        instance->next_input_sample = frame->first_input_sample;
        instance->have_position = 1;
    }
    if (frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->next_input_sample) {
        return AS_BACKEND_FAILURE;
    }

    double levels[MARGIN_BINS];
    int detected[MARGIN_BINS];
    for (uint32_t bin = 0; bin < MARGIN_BINS; ++bin) {
        levels[bin] = frame_db(instance, frame->input, bin);
        detected[bin] = 0;
    }
    uint32_t detected_count = 0;
    for (uint32_t bin = 0; bin < MARGIN_BINS; ++bin) {
        const double left = bin > 0 ? levels[bin - 1] : -300.0;
        const double right = bin + 1 < MARGIN_BINS ? levels[bin + 1] : -300.0;
        if (levels[bin] - (left > right ? left : right) >= MARGIN_PROMINENCE_DB &&
            levels[bin] >= MARGIN_ABSOLUTE_DBFS) {
            ++instance->runs[bin];
            if (instance->runs[bin] >= MARGIN_PERSISTENCE) detected[bin] = 1;
        } else {
            instance->runs[bin] = 0;
        }
        detected_count += (uint32_t)detected[bin];
    }

    uint32_t activations = 0;
    for (uint32_t index = 0; index < instance->notch_count;) {
        margin_notch *notch = &instance->notches[index];
        notch->miss_frames = detected[notch->bin_index] ? 0 : notch->miss_frames + 1;
        if (notch->miss_frames >= MARGIN_RELEASE) {
            instance->cooldowns[notch->bin_index] = MARGIN_COOLDOWN;
            for (uint32_t tail = index + 1; tail < instance->notch_count; ++tail)
                instance->notches[tail - 1u] = instance->notches[tail];
            --instance->notch_count;
        } else {
            design_notch(notch);
            ++index;
        }
    }
    for (uint32_t bin = 0; bin < MARGIN_BINS; ++bin) {
        if (instance->cooldowns[bin] > 0) --instance->cooldowns[bin];
    }
    for (uint32_t bin = 0; bin < MARGIN_BINS; ++bin) {
        int active = 0;
        for (uint32_t index = 0; index < instance->notch_count; ++index) {
            if (instance->notches[index].bin_index == (int)bin) active = 1;
        }
        if (!detected[bin] || active || instance->notch_count >= MARGIN_MAX_NOTCHES ||
            instance->cooldowns[bin] > 0) {
            continue;
        }
        margin_notch *notch = &instance->notches[instance->notch_count++];
        memset(notch, 0, sizeof(*notch));
        notch->bin_index = (int)bin;
        notch->frequency_hz = (int)(MARGIN_MIN_BIN + bin) * 100;
        design_notch(notch);
        ++activations;
    }

    if (detected_count > 0 || instance->notch_count > 0 || activations > 0)
        instance->quiet_frames = 0;
    else
        ++instance->quiet_frames;

    if (activations > 0 || (detected_count > 0 && instance->previous_runs == 0)) {
        instance->gain_db = instance->gain_db - MARGIN_STEP_DB;
        if (instance->gain_db < MARGIN_FLOOR_DB) instance->gain_db = MARGIN_FLOOR_DB;
    } else if (instance->quiet_frames > MARGIN_RECOVERY_FRAMES &&
               instance->gain_db < 0.0) {
        instance->gain_db = instance->gain_db + MARGIN_RECOVERY_DB;
        if (instance->gain_db > 0.0) instance->gain_db = 0.0;
    }
    instance->previous_runs = detected_count;
    const double gain = pow(10.0, instance->gain_db / 20.0);

    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        double filtered = (double)frame->input[i];
        for (uint32_t index = 0; index < instance->notch_count; ++index) {
            margin_notch *notch = &instance->notches[index];
            const double y = notch->b0 * filtered + notch->z1;
            notch->z1 = notch->b1 * filtered - notch->a1 * y + notch->z2;
            notch->z2 = notch->b2 * filtered - notch->a2 * y;
            filtered = y;
        }
        output->samples[i] = (float)(filtered * gain);
        if (!isfinite((double)output->samples[i])) return AS_BACKEND_FAILURE;
    }
    instance->next_input_sample += AS_FRAME_SAMPLES;
    instance->epoch = frame->epoch;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL margin_reset(void *opaque, uint64_t epoch,
                                         int64_t first_input_sample,
                                         as_error_v0 *error) {
    (void)error;
    margin_instance *instance = (margin_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->runs, 0, sizeof(instance->runs));
    memset(instance->cooldowns, 0, sizeof(instance->cooldowns));
    memset(instance->notches, 0, sizeof(instance->notches));
    instance->notch_count = 0;
    instance->previous_runs = 0;
    instance->gain_db = 0.0;
    instance->quiet_frames = 0;
    instance->epoch = epoch;
    instance->next_input_sample = first_input_sample;
    instance->have_position = 1;
    return AS_OK;
}

static as_status_v0 AS_CALL margin_drain(void *opaque,
                                         const as_output_v0 *output,
                                         as_result_v0 *result) {
    margin_instance *instance = (margin_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_input_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL margin_destroy(void *opaque) { free(opaque); }

as_status_v0 margin_provider_register(as_registry_v0 *registry,
                                      as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        margin_create, margin_process, margin_reset, margin_drain,
        margin_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
