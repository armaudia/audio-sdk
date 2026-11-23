/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local, optional block-NLMS acoustic feedback-cancellation reference
 * with a fixed -3 dB output margin.
 *
 * This is a first-party minimal reference compiled only by a caller that
 * opts in. It uses the public provider_v0 registration boundary and does not
 * modify the installed SDK, its descriptor catalog or its default providers.
 * The playback reference is an explicit caller-supplied immutable asset: no
 * capture, model, download, discovery or file access occurs in process/drain.
 * The reference block for frame k must contain the loudspeaker signal that
 * returned during that frame. Processing is causal with zero added delay.
 */
#include "afc_provider.h"
#include "afc_descriptor.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define AFC_FRAME 160u
#define AFC_TAPS 48u
#define AFC_MU 0.02
#define AFC_EPSILON 1.0e-6
#define AFC_MARGIN_GAIN 0.7079457843841379
#define AFC_WEIGHT_CLAMP 8.0

typedef struct afc_instance {
    double weights[AFC_TAPS];
    double history[AFC_TAPS - 1u];
    uint8_t *reference_bytes;
    uint32_t reference_frames;
    uint64_t epoch;
    int64_t first_input_sample;
    int drained;
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

static int afc_read_f32_le(const uint8_t *bytes, float *out) {
    uint32_t bits = (uint32_t)bytes[0] |
                    ((uint32_t)bytes[1] << 8) |
                    ((uint32_t)bytes[2] << 16) |
                    ((uint32_t)bytes[3] << 24);
    memcpy(out, &bits, sizeof(bits));
    return 1;
}

static uint32_t afc_reference_index(const afc_instance *instance,
                                    int64_t first_input_sample) {
    if (first_input_sample < 0 ||
        (first_input_sample % (int64_t)AFC_FRAME) != 0) {
        return UINT32_MAX;
    }
    uint64_t index = (uint64_t)first_input_sample / (uint64_t)AFC_FRAME;
    if (index >= (uint64_t)instance->reference_frames) return UINT32_MAX;
    return (uint32_t)index;
}

static as_status_v0 afc_create(const as_create_config_v0 *config,
                               void **out_instance, as_error_v0 *error) {
    if (out_instance == NULL) {
        afc_error(error, AS_INVALID_ARGUMENT, "instance",
                  "instance output is null");
        return AS_INVALID_ARGUMENT;
    }
    *out_instance = NULL;
    if (config == NULL || config->sample_rate_hz != 16000u ||
        config->channels != 1u || config->frame_samples != AFC_FRAME) {
        afc_error(error, AS_INVALID_ARGUMENT, "config",
                  "unsupported v0 format");
        return AS_INVALID_ARGUMENT;
    }
    if (config->config_json == NULL || config->config_json_length == 0u) {
        afc_error(error, AS_INVALID_ARGUMENT, "config_json",
                  "effective config is required");
        return AS_INVALID_ARGUMENT;
    }
    if (config->asset_count != 1u || config->assets == NULL) {
        afc_error(error, AS_INVALID_ARGUMENT, "assets",
                  "one playback-reference asset is required");
        return AS_INVALID_ARGUMENT;
    }
    const as_asset_v0 *asset = &config->assets[0];
    if (asset->data == NULL || asset->byte_count < (uint64_t)AFC_FRAME * 4u ||
        (asset->byte_count % (uint64_t)(AFC_FRAME * 4u)) != 0u) {
        afc_error(error, AS_INVALID_ARGUMENT, "assets[0]",
                  "playback reference must be whole float32 v0 frames");
        return AS_INVALID_ARGUMENT;
    }

    afc_instance *instance = (afc_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) {
        afc_error(error, AS_RESOURCE_EXHAUSTED, "instance",
                  "allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    instance->reference_frames =
        (uint32_t)(asset->byte_count / (uint64_t)(AFC_FRAME * 4u));
    /* The SDK copies retained control payloads, so this is an owned copy in
     * the provider instance and never a borrowed caller buffer. */
    instance->reference_bytes = (uint8_t *)malloc((size_t)asset->byte_count);
    if (instance->reference_bytes == NULL) {
        free(instance);
        afc_error(error, AS_RESOURCE_EXHAUSTED, "assets[0]",
                  "reference allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    memcpy(instance->reference_bytes, asset->data, (size_t)asset->byte_count);
    if (afc_reference_index(instance, config->first_input_sample) ==
        UINT32_MAX) {
        free(instance->reference_bytes);
        free(instance);
        afc_error(error, AS_INVALID_ARGUMENT, "first_input_sample",
                  "first input must be a nonnegative frame position within the reference asset");
        return AS_INVALID_ARGUMENT;
    }
    instance->epoch = config->epoch;
    instance->first_input_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 afc_process(void *state, const as_frame_v0 *frame,
                                const as_output_v0 *output,
                                as_result_v0 *result) {
    afc_instance *instance = (afc_instance *)state;
    if (instance == NULL || frame == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < AFC_FRAME ||
        frame->input == NULL || frame->input_count != AFC_FRAME ||
        frame->input_valid_count == 0 ||
        frame->input_valid_count > AFC_FRAME) {
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t reference_index =
        afc_reference_index(instance, frame->first_input_sample);
    if (reference_index == UINT32_MAX) return AS_INVALID_ARGUMENT;
    const uint8_t *reference_bytes = instance->reference_bytes +
        (size_t)reference_index * AFC_FRAME * 4u;

    double extended[AFC_TAPS + AFC_FRAME - 1u];
    double reference[AFC_FRAME];
    double error[AFC_FRAME];
    double energy = 0.0;
    for (uint32_t n = 0; n < AFC_FRAME; ++n) {
        float value = 0.0f;
        afc_read_f32_le(reference_bytes + (size_t)n * 4u, &value);
        if (!isfinite((double)value)) return AS_INVALID_ARGUMENT;
        reference[n] = (double)value;
        energy += reference[n] * reference[n];
        extended[AFC_TAPS - 1u + n] = reference[n];
    }
    memcpy(extended, instance->history,
           (AFC_TAPS - 1u) * sizeof(double));
    if (!isfinite(energy)) return AS_INVALID_ARGUMENT;

    const uint32_t valid = frame->input_valid_count;
    for (uint32_t n = 0; n < AFC_FRAME; ++n) {
        double estimate = 0.0;
        const uint32_t base = AFC_TAPS - 1u + n;
        for (uint32_t i = 0; i < AFC_TAPS; ++i) {
            estimate += instance->weights[i] * extended[base - i];
        }
        const double mic = n < valid ? (double)frame->input[n] : 0.0;
        error[n] = mic - estimate;
        if (!isfinite(error[n])) return AS_BACKEND_FAILURE;
    }

    const double denominator = energy + AFC_EPSILON;
    for (uint32_t i = 0; i < AFC_TAPS; ++i) {
        double correlation = 0.0;
        for (uint32_t n = 0; n < valid; ++n) {
            const uint32_t base = AFC_TAPS - 1u + n;
            correlation += error[n] * extended[base - i];
        }
        double weight = instance->weights[i] +
                        AFC_MU * correlation / denominator;
        if (!isfinite(weight)) return AS_BACKEND_FAILURE;
        if (weight > AFC_WEIGHT_CLAMP) weight = AFC_WEIGHT_CLAMP;
        if (weight < -AFC_WEIGHT_CLAMP) weight = -AFC_WEIGHT_CLAMP;
        instance->weights[i] = weight;
    }
    for (uint32_t i = 0; i < AFC_TAPS - 1u; ++i) {
        instance->history[i] = extended[AFC_FRAME + i];
    }

    for (uint32_t n = 0; n < AFC_FRAME; ++n) {
        double value = n < valid ? AFC_MARGIN_GAIN * error[n] : 0.0;
        if (!isfinite(value)) return AS_BACKEND_FAILURE;
        output->samples[n] = (float)value;
    }

    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AFC_FRAME;
    result->produced_count = AFC_FRAME;
    result->valid_offset = 0;
    result->valid_count = valid;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    instance->epoch = frame->epoch;
    instance->first_input_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 afc_reset(void *state, uint64_t epoch,
                              int64_t first_input_sample,
                              as_error_v0 *error) {
    (void)error;
    afc_instance *instance = (afc_instance *)state;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    if (afc_reference_index(instance, first_input_sample) == UINT32_MAX) {
        return AS_INVALID_ARGUMENT;
    }
    memset(instance->weights, 0, sizeof(instance->weights));
    memset(instance->history, 0, sizeof(instance->history));
    instance->epoch = epoch;
    instance->first_input_sample = first_input_sample;
    instance->drained = 0;
    return AS_OK;
}

static as_status_v0 afc_drain(void *state, const as_output_v0 *output,
                              as_result_v0 *result) {
    afc_instance *instance = (afc_instance *)state;
    if (instance == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < AFC_FRAME) {
        return AS_INVALID_ARGUMENT;
    }
    if (output->samples != NULL) {
        memset(output->samples, 0, AFC_FRAME * sizeof(float));
    }
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->first_input_sample;
    instance->drained = 1;
    return AS_END_OF_STREAM;
}

static void afc_destroy(void *state) {
    afc_instance *instance = (afc_instance *)state;
    if (instance == NULL) return;
    free(instance->reference_bytes);
    free(instance);
}

as_status_v0 afc_margin_register_descriptor(as_registry_v0 *registry,
                                            const char *descriptor,
                                            uint32_t length,
                                            as_error_v0 *error) {
    static const as_provider_table_v0 table = {
        sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        afc_create, afc_process, afc_reset, afc_drain, afc_destroy,
        {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, descriptor, length, error);
}

as_status_v0 afc_margin_register(as_registry_v0 *registry,
                                 as_error_v0 *error) {
    return afc_margin_register_descriptor(
        registry, kAfcDescriptor, sizeof(kAfcDescriptor) - 1u, error);
}
