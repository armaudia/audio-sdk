#ifndef AS_TEST_COMMON_H
#define AS_TEST_COMMON_H

#include "audio_sdk/session_v0.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition)                                                       \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "%s:%d: check failed: %s\n", __FILE__, __LINE__,  \
                    #condition);                                               \
            return 1;                                                          \
        }                                                                      \
    } while (0)

static inline int test_open(as_registry_v0 **registry, as_session_v0 **session,
                     const char *provider, uint32_t mode, uint64_t epoch,
                     int64_t first) {
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(registry, &error) != AS_OK) return 0;
    char config[4096];
    uint32_t required = 0;
    if (as_effective_config_create_v0(
            *registry, provider, (uint32_t)strlen(provider), mode, config,
            (uint32_t)sizeof(config), &required, &error) != AS_OK)
        return 0;
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = mode;
    create.epoch = epoch;
    create.first_input_sample = first;
    create.config_json = config;
    create.config_json_length = required - 1u;
    return as_session_create_v0(*registry, provider,
                                (uint32_t)strlen(provider), &create, session,
                                &error) == AS_OK;
}

static inline int test_process(as_session_v0 *session, uint64_t epoch, int64_t first,
                        as_result_v0 *result) {
    float input[AS_FRAME_SAMPLES] = {0};
    float output_samples[AS_FRAME_SAMPLES] = {0};
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = epoch;
    frame.first_input_sample = first;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = output_samples;
    as_result_v0_init(result);
    return as_session_process_v0(session, &frame, &output, result) == AS_OK;
}

#endif
