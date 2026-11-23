/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered feed-forward compressor reference.
 *
 * Uses only the public v0 provider table from audio_sdk/session_v0.h. This
 * source is NOT part of the installed SDK, its registry or any default build.
 * It embeds the frozen default configuration from the Python DSP fixture and
 * is intended only for caller-local boundary smoke checks.
 */
#include "audio_sdk/session_v0.h"
#include "compressor_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define FFC_PI 3.14159265358979323846
#define FFC_THRESHOLD_DB -24.0
#define FFC_RATIO 4.0
#define FFC_ATTACK_MS 5.0
#define FFC_RELEASE_MS 120.0
#define FFC_MAKEUP_DB 0.0
#define FFC_MAX_ABS_INPUT 2.0
#define FFC_DB_FLOOR 1e-12

typedef struct ffc_instance_s {
    double attack_coefficient;
    double release_coefficient;
    double compression;
    double envelope;
    double last_gain_db;
    int engaged;
    int final_seen;
    int64_t next_sample;
    uint64_t epoch;
} ffc_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL ffc_create(const as_create_config_v0 *config,
                                       void **out_instance,
                                       as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES ||
        config->execution_mode != AS_MODE_PROCESSING_THREAD) {
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        FFC_PROVIDER_ID, strlen(FFC_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    ffc_instance *instance = (ffc_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->attack_coefficient = 1.0 - exp(
        -1000.0 / (FFC_ATTACK_MS * (double)AS_SAMPLE_RATE_HZ));
    instance->release_coefficient = 1.0 - exp(
        -1000.0 / (FFC_RELEASE_MS * (double)AS_SAMPLE_RATE_HZ));
    instance->compression = 1.0 - 1.0 / FFC_RATIO;
    instance->epoch = config->epoch;
    instance->next_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL ffc_process(void *opaque,
                                        const as_frame_v0 *frame,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    ffc_instance *instance = (ffc_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (instance->final_seen) return AS_INVALID_ARGUMENT;
    if (frame->input_count != AS_FRAME_SAMPLES) return AS_INVALID_ARGUMENT;
    if (frame->input_valid_count < 1u ||
        frame->input_valid_count > AS_FRAME_SAMPLES) return AS_INVALID_ARGUMENT;
    if (frame->flags & ~(uint32_t)AS_FRAME_FINAL_INPUT) return AS_INVALID_ARGUMENT;
    if (frame->flags == 0u && frame->input_valid_count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) {
        for (uint32_t index = frame->input_valid_count; index < AS_FRAME_SAMPLES; ++index) {
            if (frame->input[index] != 0.0f) return AS_INVALID_ARGUMENT;
        }
    }
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)frame->input[index];
        if (!isfinite(value) || fabs(value) > FFC_MAX_ABS_INPUT) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->next_sample) {
        return AS_INVALID_ARGUMENT;
    }

    double output_samples[AS_FRAME_SAMPLES];
    double gains[AS_FRAME_SAMPLES];
    double envelope = instance->envelope;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)frame->input[index];
        const double magnitude = fabs(value);
        const double coefficient = magnitude > envelope
                                       ? instance->attack_coefficient
                                       : instance->release_coefficient;
        envelope += coefficient * (magnitude - envelope);
        const double level_db = 20.0 * log10(
            envelope > FFC_DB_FLOOR ? envelope : FFC_DB_FLOOR);
        const double over_db = level_db > FFC_THRESHOLD_DB
                                   ? level_db - FFC_THRESHOLD_DB : 0.0;
        const double gain_db = FFC_MAKEUP_DB - instance->compression * over_db;
        const double gain = pow(10.0, gain_db / 20.0);
        const double produced = value * gain;
        if (!isfinite(produced) || fabs(produced) > 16.0) return AS_BACKEND_FAILURE;
        output_samples[index] = produced;
        gains[index] = gain_db;
    }

    int engaged = instance->engaged;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        if (!engaged && gains[index] <= -1.0) {
            engaged = 1;
        } else if (engaged && gains[index] >= -0.5) {
            engaged = 0;
        }
    }
    instance->envelope = envelope;
    instance->engaged = engaged;
    instance->last_gain_db = gains[AS_FRAME_SAMPLES - 1u];
    instance->next_sample = frame->first_input_sample +
                            (int64_t)frame->input_valid_count;
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) instance->final_seen = 1;

    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = (float)output_samples[index];
    }
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = frame->input_valid_count;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL ffc_reset(void *opaque, uint64_t epoch,
                                      int64_t first_input_sample,
                                      as_error_v0 *error) {
    (void)error;
    ffc_instance *instance = (ffc_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    if (epoch <= instance->epoch || first_input_sample < 0) return AS_INVALID_ARGUMENT;
    instance->envelope = 0.0;
    instance->last_gain_db = FFC_MAKEUP_DB;
    instance->engaged = 0;
    instance->final_seen = 0;
    instance->next_sample = first_input_sample;
    instance->epoch = epoch;
    return AS_OK;
}

static as_status_v0 AS_CALL ffc_drain(void *opaque,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    ffc_instance *instance = (ffc_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL ffc_destroy(void *opaque) { free(opaque); }

AS_API as_status_v0 AS_CALL feed_forward_compressor_register(
    as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        ffc_create, ffc_process, ffc_reset, ffc_drain, ffc_destroy,
        {0u, 0u, 0u, 0u}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                    (uint32_t)(sizeof(kDescriptor) - 1u), error);
}
