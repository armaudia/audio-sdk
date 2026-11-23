/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local reference for an explicit biquad notch.
 *
 * It uses only the public v0 provider table and session facade declared in
 * audio_sdk/provider_v0.h and audio_sdk/session_v0.h. This source is not part
 * of the installed SDK, its registry, defaults or any default build. The
 * optional CMake consumer compiles it only when AS_ENABLE_NARROW_NOTCH=ON.
 */
#include "audio_sdk/session_v0.h"
#include "narrow_notch_descriptor.h"
#include "narrow_notch_provider.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NN_PI 3.14159265358979323846
#define NN_MAX_REGISTRATIONS 8u
#define NN_MIN_HZ 20.0
#define NN_MAX_HZ 7800.0
#define NN_MIN_BW 5.0
#define NN_MAX_BW 2000.0
#define NN_MAX_Q 2000.0

typedef struct nn_registration_s {
    char id[96];
    double frequency_hz;
    double bandwidth_hz;
} nn_registration;

static nn_registration nn_registrations[NN_MAX_REGISTRATIONS];
static uint32_t nn_registration_count;

typedef struct nn_instance_s {
    double b0, b1, b2, a1, a2;
    double z1, z2;
    double frequency_hz;
    double bandwidth_hz;
    uint64_t epoch;
    int64_t next_input_sample;
    char id[96];
} nn_instance;

static as_status_v0 AS_CALL nn_create(const as_create_config_v0 *config,
                                      void **out_instance, as_error_v0 *error);
static as_status_v0 AS_CALL nn_process(void *instance, const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result);
static as_status_v0 AS_CALL nn_reset(void *instance, uint64_t epoch,
                                     int64_t first_input_sample, as_error_v0 *error);
static as_status_v0 AS_CALL nn_drain(void *instance, const as_output_v0 *output,
                                     as_result_v0 *result);
static void AS_CALL nn_destroy(void *instance);

static const as_provider_table_v0 kNnTable = {
    (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
    nn_create, nn_process, nn_reset, nn_drain, nn_destroy, {0, 0, 0, 0}
};

static int nn_in_range(double value, double low, double high) {
    return isfinite(value) && value >= low && value <= high;
}

static int nn_integer_hz(double value) {
    return nn_in_range(value, NN_MIN_HZ, NN_MAX_HZ) && value == floor(value);
}

static nn_registration *nn_find(const char *id) {
    for (uint32_t index = 0; index < nn_registration_count; ++index) {
        if (strcmp(nn_registrations[index].id, id) == 0) {
            return &nn_registrations[index];
        }
    }
    return NULL;
}

static int nn_contains(const char *haystack, uint32_t length, const char *needle) {
    const size_t needle_length = strlen(needle);
    if (needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void nn_design(nn_instance *instance) {
    const double omega = 2.0 * NN_PI * instance->frequency_hz / (double)AS_SAMPLE_RATE_HZ;
    const double cosine = cos(omega);
    const double quality = instance->frequency_hz / instance->bandwidth_hz;
    const double alpha = sin(omega) / (2.0 * quality);
    const double a0 = 1.0 + alpha;
    instance->b0 = 1.0 / a0;
    instance->b1 = -2.0 * cosine / a0;
    instance->b2 = 1.0 / a0;
    instance->a1 = -2.0 * cosine / a0;
    instance->a2 = (1.0 - alpha) / a0;
    instance->z1 = 0.0;
    instance->z2 = 0.0;
}

static const char *nn_descriptor_format(void) {
    return "{\"buffering_delay_samples\":0,\"callback_safe\":false,"
           "\"configuration_schema_digest\":\"sha256:%s\","
           "\"contract_version\":\"0.1\",\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},"
           "\"execution_modes\":[2],\"implementation_id\":\"dsp.narrow-notch.reference\","
           "\"implementation_version\":\"0.1.0-reference\",\"max_drain_calls\":1,\"native_hop_samples\":160,"
           "\"platform\":{\"architectures\":[\"arm64\",\"x86_64\"],\"cpu_requirements\":\"baseline\"},"
           "\"provider_id\":\"%s\",\"required_assets\":[],"
           "\"schema_id\":\"audio-sdk/descriptor/0.1\","
           "\"source_digest\":\"sha256:%s\",\"source_revision\":null,"
           "\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,\"sample_format\":\"f32\",\"sample_rate_hz\":16000}],"
           "\"upstream\":{\"license\":\"Apache-2.0\",\"name\":\"audio-sdk narrow notch reference\","
           "\"notice_path\":\"licenses/Apache-2.0.txt\"}}";
}

as_status_v0 narrow_notch_register_v0(as_registry_v0 *registry,
                                      double frequency_hz,
                                      double bandwidth_hz,
                                      char *provider_id_out,
                                      uint32_t provider_id_capacity,
                                      as_error_v0 *error) {
    if (registry == NULL || provider_id_out == NULL || provider_id_capacity < 48u) {
        if (error != NULL) error->status = AS_INVALID_ARGUMENT;
        return AS_INVALID_ARGUMENT;
    }
    if (!nn_integer_hz(frequency_hz) || !nn_in_range(bandwidth_hz, NN_MIN_BW, NN_MAX_BW)
            || bandwidth_hz > frequency_hz
            || frequency_hz / bandwidth_hz > NN_MAX_Q) {
        if (error != NULL) error->status = AS_INVALID_ARGUMENT;
        return AS_INVALID_ARGUMENT;
    }
    char id[96];
    const int written = snprintf(id, sizeof(id), "dsp.narrow-notch-%.0f-%.0f.v0",
                                 frequency_hz, bandwidth_hz);
    if (written <= 0 || (size_t)written >= sizeof(id)) {
        if (error != NULL) error->status = AS_INVALID_ARGUMENT;
        return AS_INVALID_ARGUMENT;
    }
    nn_registration *registration = nn_find(id);
    if (registration != NULL) {
        if (registration->frequency_hz != frequency_hz
                || registration->bandwidth_hz != bandwidth_hz) {
            if (error != NULL) error->status = AS_INVALID_ARGUMENT;
            return AS_INVALID_ARGUMENT;
        }
    } else {
        if (nn_registration_count >= NN_MAX_REGISTRATIONS) {
            if (error != NULL) error->status = AS_RESOURCE_EXHAUSTED;
            return AS_RESOURCE_EXHAUSTED;
        }
        registration = &nn_registrations[nn_registration_count++];
        memcpy(registration->id, id, (size_t)written + 1u);
        registration->frequency_hz = frequency_hz;
        registration->bandwidth_hz = bandwidth_hz;
    }
    char descriptor[2048];
    const int descriptor_length = snprintf(descriptor, sizeof(descriptor),
                                           nn_descriptor_format(),
                                           NN_CONFIG_DIGEST, id, NN_SOURCE_DIGEST);
    if (descriptor_length <= 0 || (size_t)descriptor_length >= sizeof(descriptor)) {
        if (error != NULL) error->status = AS_BACKEND_FAILURE;
        return AS_BACKEND_FAILURE;
    }
    const as_status_v0 status = as_register_provider_v0(
        registry, &kNnTable, descriptor, (uint32_t)descriptor_length, error);
    if (status == AS_OK) {
        snprintf(provider_id_out, provider_id_capacity, "%s", id);
    }
    return status;
}

static as_status_v0 AS_CALL nn_create(const as_create_config_v0 *config,
                                      void **out_instance, as_error_v0 *error) {
    (void)error;
    if (config == NULL || out_instance == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ
            || config->channels != AS_CHANNELS
            || config->frame_samples != AS_FRAME_SAMPLES) {
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (config->config_json == NULL || config->config_json_length == 0u) {
        return AS_INVALID_ARGUMENT;
    }
    nn_registration *selected = NULL;
    for (uint32_t index = 0; index < nn_registration_count; ++index) {
        char needle[128];
        snprintf(needle, sizeof(needle), "\"id\":\"%s\"", nn_registrations[index].id);
        if (nn_contains(config->config_json, config->config_json_length, needle)) {
            selected = &nn_registrations[index];
            break;
        }
    }
    if (selected == NULL) return AS_INVALID_ARGUMENT;
    nn_instance *instance = (nn_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    memcpy(instance->id, selected->id, sizeof(instance->id));
    instance->frequency_hz = selected->frequency_hz;
    instance->bandwidth_hz = selected->bandwidth_hz;
    nn_design(instance);
    instance->epoch = config->epoch;
    instance->next_input_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL nn_process(void *opaque, const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result) {
    nn_instance *instance = (nn_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL
            || output == NULL || output->samples == NULL
            || output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES
            || frame->input_valid_count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->epoch != instance->epoch
            || frame->first_input_sample != instance->next_input_sample) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        if (!isfinite((double)frame->input[index])) return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double sample = (double)frame->input[index];
        const double filtered = instance->b0 * sample + instance->z1;
        instance->z1 = instance->b1 * sample - instance->a1 * filtered + instance->z2;
        instance->z2 = instance->b2 * sample - instance->a2 * filtered;
        if (!isfinite(filtered) || fabs(filtered) > 16.0) return AS_BACKEND_FAILURE;
        output->samples[index] = (float)filtered;
    }
    instance->next_input_sample += (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL nn_reset(void *opaque, uint64_t epoch,
                                     int64_t first_input_sample, as_error_v0 *error) {
    (void)error;
    nn_instance *instance = (nn_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    instance->epoch = epoch;
    instance->next_input_sample = first_input_sample;
    nn_design(instance);
    return AS_OK;
}

static as_status_v0 AS_CALL nn_drain(void *opaque, const as_output_v0 *output,
                                     as_result_v0 *result) {
    nn_instance *instance = (nn_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_input_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL nn_destroy(void *opaque) { free(opaque); }
