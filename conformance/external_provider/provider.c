#include "audio_sdk/provider_v0.h"

#include <stdlib.h>
#include <string.h>

typedef struct fixture_instance {
    float history[512];
    uint32_t delay;
    int64_t first_input_sample;
    int64_t next_output;
    int64_t accepted_end;
    uint64_t epoch;
    uint32_t drain_count;
    int fault;
    int unbounded_drain;
} fixture_instance;

static uint32_t delay_from_config(const char *json) {
    const char *key = "\"id\":\"fixture.delay";
    const char *match = json != NULL ? strstr(json, key) : NULL;
    if (match == NULL) return AS_FRAME_SAMPLES;
    const char *number = match + strlen(key);
    char *end = NULL;
    const unsigned long parsed = strtoul(number, &end, 10);
    if (end != number && parsed <= 512ul) return (uint32_t)parsed;
    if (strncmp(number, "256hop", 6) == 0) return 256u;
    return AS_FRAME_SAMPLES;
}

static as_status_v0 AS_CALL fixture_create(const as_create_config_v0 *config,
                                           void **out,
                                           as_error_v0 *error) {
    (void)error;
    if (config == NULL || out == NULL) return AS_INVALID_ARGUMENT;
    fixture_instance *instance =
        (fixture_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->delay = delay_from_config(config->config_json);
    instance->first_input_sample = config->first_input_sample;
    instance->next_output =
        config->first_input_sample - (int64_t)instance->delay;
    instance->epoch = config->epoch;
    if (config->config_json != NULL &&
        strstr(config->config_json, "fixture.fault.v0") != NULL)
        instance->fault = 1;
    if (config->config_json != NULL &&
        strstr(config->config_json, "fixture.drainbound.v0") != NULL)
        instance->unbounded_drain = 1;
    *out = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL fixture_process(void *opaque,
                                            const as_frame_v0 *frame,
                                            const as_output_v0 *output,
                                            as_result_v0 *result) {
    fixture_instance *instance = (fixture_instance *)opaque;
    if (instance == NULL || frame == NULL || output == NULL ||
        output->samples == NULL || result == NULL)
        return AS_INVALID_ARGUMENT;
    const int64_t source =
        frame->first_input_sample - (int64_t)instance->delay;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        const int64_t source_sample = source + (int64_t)i;
        const int64_t current_sample =
            frame->first_input_sample + (int64_t)i;
        if (instance->fault) {
            output->samples[i] = 0.0f;
        } else if (instance->delay == 0) {
            output->samples[i] = frame->input[i];
        } else if (source_sample >= instance->first_input_sample &&
                   source_sample < current_sample) {
            output->samples[i] =
                instance->history[(uint64_t)source_sample % 512u];
        } else {
            output->samples[i] = 0.0f;
        }
        instance->history[(uint64_t)current_sample % 512u] =
            frame->input[i];
    }
    instance->epoch = frame->epoch;
    instance->accepted_end =
        frame->first_input_sample +
        (int64_t)((frame->flags & AS_FRAME_FINAL_INPUT)
                      ? frame->input_valid_count
                      : AS_FRAME_SAMPLES);
    instance->next_output = source + (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = source + (instance->fault ? 1 : 0);
    return AS_OK;
}

static as_status_v0 AS_CALL fixture_reset(void *opaque, uint64_t epoch,
                                          int64_t first,
                                          as_error_v0 *error) {
    (void)error;
    fixture_instance *instance = (fixture_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->history, 0, sizeof(instance->history));
    instance->first_input_sample = first;
    instance->next_output = first - (int64_t)instance->delay;
    instance->accepted_end = first;
    instance->epoch = epoch;
    instance->drain_count = 0;
    return AS_OK;
}

static as_status_v0 AS_CALL fixture_drain(void *opaque,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    fixture_instance *instance = (fixture_instance *)opaque;
    if (instance == NULL || output == NULL || output->samples == NULL ||
        result == NULL)
        return AS_INVALID_ARGUMENT;
    if (instance->unbounded_drain) {
        memset(output->samples, 0, AS_FRAME_SAMPLES * sizeof(float));
        as_result_v0_init(result);
        result->status = AS_OK;
        result->produced_count = AS_FRAME_SAMPLES;
        result->valid_count = AS_FRAME_SAMPLES;
        result->epoch = instance->epoch;
        result->source_first_sample = instance->next_output;
        instance->next_output += AS_FRAME_SAMPLES;
        ++instance->drain_count;
        return AS_OK;
    }
    if (instance->next_output >= instance->accepted_end)
        return AS_END_OF_STREAM;
    uint32_t produced =
        (uint32_t)(instance->accepted_end - instance->next_output);
    if (produced > AS_FRAME_SAMPLES) produced = AS_FRAME_SAMPLES;
    for (uint32_t i = 0; i < produced; ++i) {
        const int64_t sample = instance->next_output + (int64_t)i;
        output->samples[i] =
            sample >= instance->first_input_sample
                ? instance->history[(uint64_t)sample % 512u]
                : 0.0f;
    }
    as_result_v0_init(result);
    result->status = AS_OK;
    result->produced_count = produced;
    result->valid_count = produced;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_output;
    instance->next_output += produced;
    ++instance->drain_count;
    return AS_OK;
}

static void AS_CALL fixture_destroy(void *opaque) { free(opaque); }

static const as_provider_table_v0 kTable = {
    (uint32_t)sizeof(as_provider_table_v0),
    AS_ABI_MAJOR,
    AS_ABI_MINOR,
    fixture_create,
    fixture_process,
    fixture_reset,
    fixture_drain,
    fixture_destroy,
    {0, 0, 0, 0}};

const as_provider_table_v0 *fixture_provider_table(void) { return &kTable; }
