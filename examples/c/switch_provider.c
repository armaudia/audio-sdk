/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Build with the installed CMake package; see examples/README.md. */
#include "audio_sdk/session_v0.h"

#include <stdio.h>
#include <string.h>

static int run_provider(as_registry_v0 *registry, const char *provider_id) {
    char effective[4096];
    uint32_t required = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    as_status_v0 status = as_effective_config_create_v0(
        registry, provider_id, (uint32_t)strlen(provider_id),
        AS_MODE_PROCESSING_THREAD, effective, (uint32_t)sizeof(effective),
        &required, &error);
    if (status != AS_OK) {
        fprintf(stderr, "%s config: %s\n", provider_id, error.message);
        return 0;
    }

    as_create_config_v0 config;
    as_create_config_v0_init(&config);
    config.execution_mode = AS_MODE_PROCESSING_THREAD;
    config.epoch = 1;
    config.config_json = effective;
    config.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    status = as_session_create_v0(registry, provider_id,
                                  (uint32_t)strlen(provider_id), &config,
                                  &session, &error);
    if (status != AS_OK) {
        fprintf(stderr, "%s create: %s\n", provider_id, error.message);
        return 0;
    }

    float input[AS_FRAME_SAMPLES] = {0};
    float output_samples[AS_FRAME_SAMPLES] = {0};
    input[20] = 0.5f;
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 1;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = output_samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    status = as_session_process_v0(session, &frame, &output, &result);
    if (status == AS_OK) {
        printf("%-20s source=[%lld,%lld), valid=%u+%u\n", provider_id,
               (long long)result.source_first_sample,
               (long long)result.source_first_sample + result.produced_count,
               result.valid_offset, result.valid_count);
    } else {
        fprintf(stderr, "%s process: %s\n", provider_id,
                as_status_name_v0(status));
    }
    as_session_close_v0(&session);
    return status == AS_OK;
}

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    as_status_v0 status = as_registry_create_v0(&registry, &error);
    if (status != AS_OK) {
        fprintf(stderr, "registry: %s\n", error.message);
        return 1;
    }
    int ok = run_provider(registry, "speex.ns.v0");
    ok &= run_provider(registry, "dsp.highpass80.v0");
    as_registry_close_v0(&registry);
    return ok ? 0 : 1;
}
