/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local identity/noop provider for installed-SDK verification.
 *
 * Fixed v0 format only: 16 kHz mono float32, 160 samples per call. This is a
 * test provider registered explicitly by the consumer; it is not a built-in,
 * not a default, and not a public ABI change. Buffering delay D=0 and every
 * produced sample is a byte-identical copy of its caller-owned input sample.
 */
#include "audio_sdk/provider_v0.h"

#include <stdlib.h>
#include <string.h>

typedef struct identity_instance {
    int64_t first_input_sample;
    int64_t next_output;
    int64_t accepted_end;
    uint64_t epoch;
    uint32_t drain_calls;
} identity_instance;

static as_status_v0 AS_CALL identity_create(const as_create_config_v0 *config,
                                            void **out,
                                            as_error_v0 *error) {
    (void)error;
    if (out == NULL) return AS_INVALID_ARGUMENT;
    *out = NULL;
    if (config == NULL || config->assets != NULL || config->asset_count != 0u)
        return AS_INVALID_ARGUMENT;
    identity_instance *instance = (identity_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->first_input_sample = config->first_input_sample;
    instance->accepted_end = config->first_input_sample;
    instance->next_output = config->first_input_sample;
    instance->epoch = config->epoch;
    *out = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL identity_process(void *opaque,
                                             const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    identity_instance *instance = (identity_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL || result == NULL)
        return AS_INVALID_ARGUMENT;
    memcpy(output->samples, frame->input,
           sizeof(float) * (size_t)AS_FRAME_SAMPLES);
    instance->epoch = frame->epoch;
    instance->accepted_end =
        frame->first_input_sample +
        (int64_t)((frame->flags & AS_FRAME_FINAL_INPUT) != 0u
                      ? frame->input_valid_count
                      : AS_FRAME_SAMPLES);
    instance->next_output = frame->first_input_sample + (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_count = frame->input_valid_count;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL identity_reset(void *opaque, uint64_t epoch,
                                           int64_t first_sample,
                                           as_error_v0 *error) {
    (void)error;
    identity_instance *instance = (identity_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    instance->first_input_sample = first_sample;
    instance->accepted_end = first_sample;
    instance->next_output = first_sample;
    instance->epoch = epoch;
    instance->drain_calls = 0u;
    return AS_OK;
}

static as_status_v0 AS_CALL identity_drain(void *opaque,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    (void)output;
    identity_instance *instance = (identity_instance *)opaque;
    if (instance == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    ++instance->drain_calls;
    if (instance->drain_calls > 1u ||
        instance->next_output >= instance->accepted_end)
        return AS_END_OF_STREAM;
    return AS_BACKEND_FAILURE;
}

static void AS_CALL identity_destroy(void *opaque) { free(opaque); }

static const as_provider_table_v0 kTable = {
    (uint32_t)sizeof(as_provider_table_v0),
    AS_ABI_MAJOR,
    AS_ABI_MINOR,
    identity_create,
    identity_process,
    identity_reset,
    identity_drain,
    identity_destroy,
    {0, 0, 0, 0}};

const as_provider_table_v0 *identity_provider_table(void) { return &kTable; }
