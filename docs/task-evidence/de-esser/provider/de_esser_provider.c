/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered split-band de-esser reference.
 *
 * Uses only the public v0 provider table from audio_sdk/session_v0.h. This
 * source is NOT part of the installed SDK, its registry or any default build.
 * It embeds the frozen default configuration from the Python evidence fixture
 * and exists only for caller-local boundary smoke checks.
 */
#include "audio_sdk/session_v0.h"
#include "deesser_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define DE_PI 3.14159265358979323846
#define DE_HIGHPASS_HZ 4000.0
#define DE_THRESHOLD_DB -24.0
#define DE_RATIO 6.0
#define DE_ATTACK_MS 5.0
#define DE_RELEASE_MS 120.0
#define DE_MAX_REDUCTION_DB 12.0
#define DE_MAKEUP_DB 0.0
#define DE_MAX_ABS_INPUT 2.0
#define DE_DB_FLOOR 1e-12

typedef struct de_instance_s {
    double b0;
    double b1;
    double b2;
    double a1;
    double a2;
    double x1;
    double x2;
    double y1;
    double y2;
    double envelope;
    double attack_coefficient;
    double release_coefficient;
    double compression;
    double last_gain_db;
    int engaged;
    int final_seen;
    int64_t next_sample;
    uint64_t epoch;
} de_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL de_create(const as_create_config_v0 *config,
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
                        DE_PROVIDER_ID, strlen(DE_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    de_instance *instance = (de_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    const double w0 = 2.0 * DE_PI * DE_HIGHPASS_HZ / (double)AS_SAMPLE_RATE_HZ;
    const double alpha = sin(w0) / (2.0 * sqrt(0.5));
    const double cosine = cos(w0);
    const double b0 = (1.0 + cosine) / 2.0;
    const double b1 = -(1.0 + cosine);
    const double a0 = 1.0 + alpha;
    instance->b0 = b0 / a0;
    instance->b1 = b1 / a0;
    instance->b2 = b0 / a0;
    instance->a1 = -2.0 * cosine / a0;
    instance->a2 = (1.0 - alpha) / a0;
    instance->attack_coefficient = 1.0 - exp(
        -1000.0 / (DE_ATTACK_MS * (double)AS_SAMPLE_RATE_HZ));
    instance->release_coefficient = 1.0 - exp(
        -1000.0 / (DE_RELEASE_MS * (double)AS_SAMPLE_RATE_HZ));
    instance->compression = 1.0 - 1.0 / DE_RATIO;
    instance->epoch = config->epoch;
    instance->next_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL de_process(void *opaque,
                                       const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result) {
    de_instance *instance = (de_instance *)opaque;
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
        if (!isfinite(value) || fabs(value) > DE_MAX_ABS_INPUT) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->next_sample) {
        return AS_INVALID_ARGUMENT;
    }

    double output_samples[AS_FRAME_SAMPLES];
    double x1 = instance->x1;
    double x2 = instance->x2;
    double y1 = instance->y1;
    double y2 = instance->y2;
    double envelope = instance->envelope;
    int engaged = instance->engaged;
    double last_gain_db = 0.0;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)frame->input[index];
        const double high = instance->b0 * value + instance->b1 * x1 +
                            instance->b2 * x2 - instance->a1 * y1 -
                            instance->a2 * y2;
        const double coefficient = fabs(high) > envelope
                                       ? instance->attack_coefficient
                                       : instance->release_coefficient;
        envelope += coefficient * (fabs(high) - envelope);
        const double level_db = 20.0 * log10(
            envelope > DE_DB_FLOOR ? envelope : DE_DB_FLOOR);
        const double over_db = level_db > DE_THRESHOLD_DB
                                   ? level_db - DE_THRESHOLD_DB : 0.0;
        const double reduction_db = fmin(DE_MAX_REDUCTION_DB,
                                         instance->compression * over_db);
        const double gain = pow(10.0, (DE_MAKEUP_DB - reduction_db) / 20.0);
        const double produced = value - (1.0 - gain) * high;
        if (!isfinite(produced) || fabs(produced) > 16.0) return AS_BACKEND_FAILURE;
        output_samples[index] = produced;
        last_gain_db = -reduction_db;
        if (!engaged && last_gain_db <= -1.0) engaged = 1;
        else if (engaged && last_gain_db >= -0.5) engaged = 0;
        x2 = x1;
        x1 = value;
        y2 = y1;
        y1 = high;
    }
    instance->x1 = x1;
    instance->x2 = x2;
    instance->y1 = y1;
    instance->y2 = y2;
    instance->envelope = envelope;
    instance->engaged = engaged;
    instance->last_gain_db = last_gain_db;
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

static as_status_v0 AS_CALL de_reset(void *opaque, uint64_t epoch,
                                     int64_t first_input_sample,
                                     as_error_v0 *error) {
    (void)error;
    de_instance *instance = (de_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    if (epoch <= instance->epoch || first_input_sample < 0) return AS_INVALID_ARGUMENT;
    instance->x1 = 0.0;
    instance->x2 = 0.0;
    instance->y1 = 0.0;
    instance->y2 = 0.0;
    instance->envelope = 0.0;
    instance->last_gain_db = 0.0;
    instance->engaged = 0;
    instance->final_seen = 0;
    instance->next_sample = first_input_sample;
    instance->epoch = epoch;
    return AS_OK;
}

static as_status_v0 AS_CALL de_drain(void *opaque,
                                     const as_output_v0 *output,
                                     as_result_v0 *result) {
    de_instance *instance = (de_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL de_destroy(void *opaque) { free(opaque); }

AS_API as_status_v0 AS_CALL de_esser_register(
    as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        de_create, de_process, de_reset, de_drain, de_destroy,
        {0u, 0u, 0u, 0u}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                    (uint32_t)(sizeof(kDescriptor) - 1u), error);
}
