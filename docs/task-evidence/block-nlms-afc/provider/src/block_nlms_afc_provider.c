/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered Block-NLMS acoustic feedback cancellation reference.
 *
 * Only the public v0 provider table is used. This file is NOT part of the
 * installed SDK, its registry, any default build or any public catalog. It is
 * a boundary reference: the explicit playback reference is a caller-owned,
 * descriptor-pinned f32 asset; a missing or malformed asset fails create.
 * The Python fixture in the parent directory owns the DSP report.
 */
#include "block_nlms_afc_provider.h"
#include "afc_descriptor.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define AFC_TAPS 32u
#define AFC_LOOP_DELAY 160u
#define AFC_GUARD (2u * 32u)
#define AFC_ASSET_PREFIX (AFC_TAPS + AFC_LOOP_DELAY + AFC_GUARD)
#define AFC_REF_OFFSET (AFC_ASSET_PREFIX - AFC_LOOP_DELAY)
#define AFC_STEP 0.1
#define AFC_NORM 8.0
#define AFC_EPSILON 1e-6
#define AFC_MIN_POWER 1e-4
#define AFC_DT_ABS 1e-4
#define AFC_DT_COHERENCE 0.35
#define AFC_LEAKAGE 0.9999
#define AFC_MAX_ABS 4.0

typedef struct afc_instance {
    float *reference;
    uint32_t reference_samples;
    double weights[AFC_TAPS];
    double correlation[AFC_TAPS];
    double residual[AS_FRAME_SAMPLES];
    uint64_t epoch;
    int64_t origin_input_sample;
    int64_t first_input_sample;
    uint64_t frames;
    uint64_t adapted_frames;
    uint64_t double_talk_frames;
} afc_instance;

static void afc_error(as_error_v0 *error, as_status_v0 status,
                      const char *field, const char *message) {
    if (error == NULL) return;
    as_error_v0_init(error);
    error->status = status;
    (void)snprintf(error->message, sizeof(error->message), "%s", message);
    if (field != NULL) {
        (void)snprintf(error->field, sizeof(error->field), "%s", field);
    }
}

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 afc_create(const as_create_config_v0 *config,
                               void **out_instance, as_error_v0 *error) {
    if (out_instance == NULL) {
        afc_error(error, AS_INVALID_ARGUMENT, "instance", "instance output is null");
        return AS_INVALID_ARGUMENT;
    }
    *out_instance = NULL;
    if (config == NULL || config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) {
        afc_error(error, AS_UNSUPPORTED, "config", "unsupported v0 format");
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 1u || config->assets == NULL ||
        config->assets[0].data == NULL) {
        afc_error(error, AS_INVALID_ARGUMENT, "assets",
                  "explicit playback reference asset is required");
        return AS_INVALID_ARGUMENT;
    }
    const as_asset_v0 *asset = &config->assets[0];
    if (asset->asset_id_length != strlen(AFC_ASSET_ID) ||
        memcmp(asset->asset_id, AFC_ASSET_ID, asset->asset_id_length) != 0) {
        afc_error(error, AS_INVALID_ARGUMENT, "assets[0].id",
                  "unexpected playback reference asset id");
        return AS_INVALID_ARGUMENT;
    }
    if (asset->byte_count < (uint64_t)AFC_ASSET_PREFIX + AS_FRAME_SAMPLES ||
        (asset->byte_count % 4u) != 0u ||
        asset->byte_count > (uint64_t)AS_MAX_ASSET_BYTES) {
        afc_error(error, AS_INVALID_ARGUMENT, "assets[0].byte_count",
                  "playback reference must be a sufficiently long f32 array");
        return AS_INVALID_ARGUMENT;
    }
    if (!contains_bytes(config->config_json, config->config_json_length,
                        AFC_PROVIDER_ID, strlen(AFC_PROVIDER_ID))) {
        afc_error(error, AS_INVALID_ARGUMENT, "config_json",
                  "config does not identify this provider");
        return AS_INVALID_ARGUMENT;
    }
    uint32_t bytes = (uint32_t)asset->byte_count;
    afc_instance *instance = (afc_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) {
        afc_error(error, AS_RESOURCE_EXHAUSTED, "instance", "allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    instance->reference = (float *)malloc(bytes);
    if (instance->reference == NULL) {
        free(instance);
        afc_error(error, AS_RESOURCE_EXHAUSTED, "assets[0]", "asset copy failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    memcpy(instance->reference, asset->data, bytes);
    instance->reference_samples = bytes / 4u;
    for (uint32_t index = 0; index < instance->reference_samples; ++index) {
        if (!isfinite((double)instance->reference[index]) ||
            fabs((double)instance->reference[index]) > AFC_MAX_ABS) {
            free(instance->reference);
            free(instance);
            afc_error(error, AS_INVALID_ARGUMENT, "assets[0]",
                      "playback reference contains an invalid sample");
            return AS_INVALID_ARGUMENT;
        }
    }
    instance->epoch = config->epoch;
    instance->origin_input_sample = config->first_input_sample;
    instance->first_input_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 afc_process(void *opaque, const as_frame_v0 *frame,
                                const as_output_v0 *output,
                                as_result_v0 *result) {
    afc_instance *instance = (afc_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES ||
        frame->input_valid_count == 0 ||
        frame->input_valid_count > AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    /* A final partial frame is zero-padded for the block update; the SDK
     * validity layer marks the tail as final padding. */
    float input[AS_FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    for (uint32_t i = 0; i < frame->input_valid_count; ++i) {
        if (!isfinite((double)frame->input[i]) ||
            fabs((double)frame->input[i]) > AFC_MAX_ABS) {
            return AS_INVALID_ARGUMENT;
        }
        input[i] = frame->input[i];
    }
    if (frame->epoch != instance->epoch ||
        frame->first_input_sample < instance->first_input_sample) {
        return AS_BACKEND_FAILURE;
    }
    int64_t relative = frame->first_input_sample - instance->origin_input_sample;
    if (relative < 0) return AS_BACKEND_FAILURE;
    uint32_t base = (uint32_t)relative + AFC_REF_OFFSET;
    if (base < AFC_TAPS ||
        (uint64_t)base + AS_FRAME_SAMPLES > instance->reference_samples) {
        return AS_BACKEND_FAILURE;
    }

    double mic_power = 0.0;
    double ref_power = 0.0;
    double cross_power = 0.0;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        uint32_t position = base + n;
        double accumulator = 0.0;
        for (uint32_t k = 0; k < AFC_TAPS; ++k) {
            accumulator += instance->weights[k] *
                           (double)instance->reference[position - k];
        }
        double error = (double)input[n] - accumulator;
        if (!isfinite(error)) return AS_BACKEND_FAILURE;
        instance->residual[n] = error;
        mic_power += (double)input[n] * (double)input[n];
        ref_power += (double)instance->reference[position] *
                     (double)instance->reference[position];
        cross_power += (double)input[n] *
                       (double)instance->reference[position];
    }
    const double frames = (double)AS_FRAME_SAMPLES;
    const double mic_mean = mic_power / frames;
    const double ref_mean = ref_power / frames;
    const double cross_mean = cross_power / frames;
    const double denominator = sqrt(fmax(mic_mean * ref_mean, 1e-30));
    const double coherence = (cross_mean / denominator) *
                             (cross_mean / denominator);
    int double_talk = mic_mean > AFC_DT_ABS && coherence < AFC_DT_COHERENCE;
    int quiet_reference = ref_mean < AFC_MIN_POWER;
    if (double_talk) ++instance->double_talk_frames;

    if (!double_talk && !quiet_reference) {
        const double mu = AFC_STEP / (AFC_NORM * ref_power + AFC_EPSILON);
        memset(instance->correlation, 0, sizeof(instance->correlation));
        for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
            uint32_t position = base + n;
            double error = instance->residual[n];
            for (uint32_t k = 0; k < AFC_TAPS; ++k) {
                instance->correlation[k] += error *
                    (double)instance->reference[position - k];
            }
        }
        for (uint32_t k = 0; k < AFC_TAPS; ++k) {
            double updated = AFC_LEAKAGE * instance->weights[k] +
                             mu * instance->correlation[k];
            if (!isfinite(updated) || fabs(updated) > 16.0) {
                return AS_BACKEND_FAILURE;
            }
            instance->weights[k] = updated;
        }
        ++instance->adapted_frames;
    }

    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        output->samples[i] = (float)instance->residual[i];
        if (!isfinite((double)output->samples[i])) return AS_BACKEND_FAILURE;
    }
    ++instance->frames;
    instance->first_input_sample = frame->first_input_sample + AS_FRAME_SAMPLES;
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

static as_status_v0 afc_reset(void *opaque, uint64_t epoch,
                              int64_t first_input_sample, as_error_v0 *error) {
    (void)error;
    afc_instance *instance = (afc_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->weights, 0, sizeof(instance->weights));
    memset(instance->correlation, 0, sizeof(instance->correlation));
    memset(instance->residual, 0, sizeof(instance->residual));
    instance->frames = 0;
    instance->adapted_frames = 0;
    instance->double_talk_frames = 0;
    instance->epoch = epoch;
    instance->origin_input_sample = first_input_sample;
    instance->first_input_sample = first_input_sample;
    return AS_OK;
}

static as_status_v0 afc_drain(void *opaque, const as_output_v0 *output,
                              as_result_v0 *result) {
    afc_instance *instance = (afc_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->first_input_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL afc_destroy(void *opaque) {
    afc_instance *instance = (afc_instance *)opaque;
    if (instance != NULL) free(instance->reference);
    free(opaque);
}

as_status_v0 afc_provider_register(as_registry_v0 *registry,
                                   as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        afc_create, afc_process, afc_reset, afc_drain, afc_destroy,
        {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kAfcDescriptor,
                                   sizeof(kAfcDescriptor) - 1u, error);
}
