/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "fixture_descriptor.h"

#include <stdlib.h>

typedef struct fixture_instance {
    const uint8_t *marker;
} fixture_instance;

static as_status_v0 AS_CALL create(const as_create_config_v0 *config,
                                   void **out, as_error_v0 *error) {
    (void)error;
    if (out == NULL) return AS_INVALID_ARGUMENT;
    *out = NULL;
    if (config == NULL || config->asset_count != 1 || config->assets == NULL ||
        config->assets[0].byte_count != 1 || config->assets[0].data == NULL)
        return AS_INVALID_ARGUMENT;
    fixture_instance *instance = malloc(sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->marker = config->assets[0].data;
    *out = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL process(void *state, const as_frame_v0 *frame,
                                    const as_output_v0 *output, as_result_v0 *result) {
    const fixture_instance *instance = state;
    const float gain = *instance->marker / 240.0f;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i)
        output->samples[i] = gain * frame->input[i];
    as_result_v0_init(result);
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_count = frame->input_valid_count;
    return AS_OK;
}

static as_status_v0 AS_CALL reset(void *state, uint64_t epoch, int64_t first_sample,
                                  as_error_v0 *error) {
    (void)state; (void)epoch; (void)first_sample; (void)error;
    return AS_OK;
}

static as_status_v0 AS_CALL drain(void *state, const as_output_v0 *output,
                                  as_result_v0 *result) {
    (void)state; (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    return AS_END_OF_STREAM;
}

static void AS_CALL destroy(void *state) { free(state); }

as_status_v0 fixture_register(as_registry_v0 *registry, as_error_v0 *error) {
    static const as_provider_table_v0 table = {
        sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        create, process, reset, drain, destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
