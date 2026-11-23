/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered reference for a fixed feedback gain margin.
 *
 * Uses only the public v0 provider table in audio_sdk/provider_v0.h. This file
 * is NOT part of the installed SDK, its registry, any default build or any
 * public catalog. It is a boundary smoke check: the Python fixture in the
 * parent directory owns the full DSP report and the recursive path trials.
 */
#include "audio_sdk/session_v0.h"
#include "fixed_margin_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define FIXED_MARGIN_GAIN_DB (-5.0)
#define FIXED_MARGIN_MIN_GAIN_DB (-24.0)
#define FIXED_MARGIN_MAX_GAIN_DB (0.0)
#define FIXED_MARGIN_MAX_ABS_INPUT (4.0)
#define FIXED_MARGIN_OUTPUT_CEILING (4.0)

typedef struct fixed_margin_instance_s {
    uint64_t epoch;
    int64_t next_input_sample;
    int have_position;
    uint64_t frames_processed;
} fixed_margin_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL fixed_margin_create(const as_create_config_v0 *config,
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
                        FIXED_MARGIN_PROVIDER_ID,
                        strlen(FIXED_MARGIN_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    if (FIXED_MARGIN_GAIN_DB < FIXED_MARGIN_MIN_GAIN_DB ||
        FIXED_MARGIN_GAIN_DB > FIXED_MARGIN_MAX_GAIN_DB) {
        return AS_BACKEND_FAILURE;
    }
    fixed_margin_instance *instance = (fixed_margin_instance *)calloc(
        1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->epoch = config->epoch;
    instance->next_input_sample = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL fixed_margin_process(void *opaque,
                                                 const as_frame_v0 *frame,
                                                 const as_output_v0 *output,
                                                 as_result_v0 *result) {
    fixed_margin_instance *instance = (fixed_margin_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES) return AS_INVALID_ARGUMENT;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double sample = (double)frame->input[index];
        if (!isfinite(sample) || fabs(sample) > FIXED_MARGIN_MAX_ABS_INPUT) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (!instance->have_position) {
        instance->epoch = frame->epoch;
        instance->next_input_sample = frame->first_input_sample;
        instance->have_position = 1;
    }
    if (frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->next_input_sample) {
        /* Session facade rejects epoch/position before the provider; keep the
         * same rule here for direct table callers. */
        return AS_INVALID_ARGUMENT;
    }
    const double gain = pow(10.0, FIXED_MARGIN_GAIN_DB / 20.0);
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double sample = (double)frame->input[index] * gain;
        if (!isfinite(sample) || fabs(sample) > FIXED_MARGIN_OUTPUT_CEILING) {
            return AS_BACKEND_FAILURE;
        }
        output->samples[index] = (float)sample;
    }
    instance->next_input_sample += AS_FRAME_SAMPLES;
    instance->frames_processed += 1u;
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

static as_status_v0 AS_CALL fixed_margin_reset(void *opaque, uint64_t epoch,
                                               int64_t first_input_sample,
                                               as_error_v0 *error) {
    (void)error;
    fixed_margin_instance *instance = (fixed_margin_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    instance->epoch = epoch;
    instance->next_input_sample = first_input_sample;
    instance->have_position = 1;
    instance->frames_processed = 0u;
    return AS_OK;
}

static as_status_v0 AS_CALL fixed_margin_drain(void *opaque,
                                               const as_output_v0 *output,
                                               as_result_v0 *result) {
    fixed_margin_instance *instance = (fixed_margin_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_input_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL fixed_margin_destroy(void *opaque) { free(opaque); }

as_status_v0 fixed_margin_provider_register(as_registry_v0 *registry,
                                            as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        fixed_margin_create, fixed_margin_process, fixed_margin_reset,
        fixed_margin_drain, fixed_margin_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
