/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered adaptive-energy VAD reference on the public v0
 * provider table. It passes audio through unchanged and keeps a per-instance
 * adaptive noise estimate plus a two-frame onset / three-frame offset state.
 * The observation helper is task-local: analysis events are not v0 ABI.
 * This source is not part of the installed SDK, its registry or any default.
 */
#include "audio_sdk/session_v0.h"
#include "adaptive_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define VAD_MIN_DBFS (-55.0)
#define VAD_NOISE_MARGIN_DB (8.0)
#define VAD_NOISE_ALPHA (0.01)
#define VAD_NOISE_INIT_DBFS (-90.0)
#define VAD_PROBABILITY_SCALE_DB (3.0)
#define VAD_ONSET_FRAMES 2
#define VAD_OFFSET_FRAMES 3
#define VAD_MAX_ABS_SAMPLE (4.0)

typedef struct adaptive_vad_s {
    double noise_dbfs;
    int raw_run;
    int idle_run;
    int active;
    int64_t active_start;
    uint64_t epoch;
    int64_t expected_start;
    int have_position;
} adaptive_vad;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL vad_create(const as_create_config_v0 *config,
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
                        ADAPTIVE_VAD_PROVIDER_ID,
                        strlen(ADAPTIVE_VAD_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    adaptive_vad *instance = (adaptive_vad *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->noise_dbfs = VAD_NOISE_INIT_DBFS;
    instance->epoch = config->epoch;
    instance->expected_start = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static double compute_probability(adaptive_vad *instance, double dbfs) {
    const double threshold = fmax(VAD_MIN_DBFS,
                                  instance->noise_dbfs + VAD_NOISE_MARGIN_DB);
    const double excess = (dbfs - threshold) / VAD_PROBABILITY_SCALE_DB;
    if (excess >= 40.0) return 1.0;
    if (excess <= -40.0) return 0.0;
    return 1.0 / (1.0 + exp(-excess));
}

static as_status_v0 AS_CALL vad_process(void *opaque,
                                        const as_frame_v0 *frame,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    adaptive_vad *instance = (adaptive_vad *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    const uint32_t count = frame->input_valid_count;
    if (frame->input_count != AS_FRAME_SAMPLES || count == 0 ||
        count > AS_FRAME_SAMPLES || (count < AS_FRAME_SAMPLES && !final)) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < count; ++index) {
        const double sample = (double)frame->input[index];
        if (!isfinite(sample) || sample > VAD_MAX_ABS_SAMPLE ||
            sample < -VAD_MAX_ABS_SAMPLE) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch) return AS_INVALID_ARGUMENT;
    if (!instance->have_position) {
        instance->expected_start = frame->first_input_sample;
        instance->have_position = 1;
    }
    if (frame->first_input_sample != instance->expected_start) {
        return AS_BACKEND_FAILURE;
    }

    double power = 0.0;
    for (uint32_t index = 0; index < count; ++index) {
        const double sample = (double)frame->input[index];
        power += sample * sample;
    }
    power /= (double)count;
    const double dbfs = 20.0 * log10(sqrt(power) > 1e-6 ? sqrt(power) : 1e-6);
    const double probability = compute_probability(instance, dbfs);
    const int raw_active = probability >= 0.5;
    if (!raw_active) {
        instance->noise_dbfs += VAD_NOISE_ALPHA * (dbfs - instance->noise_dbfs);
    }
    if (raw_active) {
        ++instance->raw_run;
        instance->idle_run = 0;
        if (!instance->active && instance->raw_run >= VAD_ONSET_FRAMES) {
            instance->active = 1;
            instance->active_start = frame->first_input_sample;
        }
    } else {
        ++instance->idle_run;
        instance->raw_run = 0;
        if (instance->active && instance->idle_run >= VAD_OFFSET_FRAMES) {
            instance->active = 0;
            instance->active_start = 0;
        }
    }
    if (final && instance->active) {
        instance->active = 0;
        instance->active_start = 0;
    }

    for (uint32_t index = 0; index < count; ++index) {
        output->samples[index] = frame->input[index];
    }
    for (uint32_t index = count; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = 0.0f;
    }
    instance->expected_start = frame->first_input_sample + (int64_t)count;
    as_result_v0_init(result);
    result->status = AS_OK;
    /* v0 always reports a full 160-sample output frame; validity marks the
       accepted prefix for a short final input. */
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = count;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL vad_reset(void *opaque, uint64_t epoch,
                                      int64_t first_input_sample,
                                      as_error_v0 *error) {
    (void)error;
    adaptive_vad *instance = (adaptive_vad *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    instance->noise_dbfs = VAD_NOISE_INIT_DBFS;
    instance->raw_run = 0;
    instance->idle_run = 0;
    instance->active = 0;
    instance->active_start = 0;
    instance->epoch = epoch;
    instance->expected_start = first_input_sample;
    instance->have_position = 1;
    return AS_OK;
}

static as_status_v0 AS_CALL vad_drain(void *opaque,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    adaptive_vad *instance = (adaptive_vad *)opaque;
    (void)output;
    if (instance == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->expected_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL vad_destroy(void *opaque) { free(opaque); }

as_status_v0 adaptive_energy_vad_register(as_registry_v0 *registry,
                                          as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        vad_create, vad_process, vad_reset, vad_drain, vad_destroy,
        {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
