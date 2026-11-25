/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#if !(defined(PROBE_APPLE) && defined(__APPLE__) && defined(__MACH__)) && \
    !(defined(PROBE_NODE) && defined(__EMSCRIPTEN__) && defined(__wasm32__))
#error Wrong compiler target for this smoke test
#endif

#define CHECK(expr) do { \
    if (!(expr)) { fprintf(stderr, "line %d: %s\n", __LINE__, #expr); return 1; } \
} while (0)

static int reject(as_registry_v0 *registry, const char *id, uint32_t length,
                  const as_create_config_v0 *config, as_status_v0 expected,
                  const char *label) {
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_session_create_v0(registry, id, length, config, &session, &error) == expected);
    CHECK(session == NULL);
    printf("%s: %s; no session\n", label, as_status_name_v0(expected));
    return 0;
}

static int smoke(as_registry_v0 *registry, const char *id, int delay) {
    uint32_t length = (uint32_t)strlen(id), required = 0;
    char effective[4096];
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_effective_config_create_v0(registry, id, length, AS_MODE_PROCESSING_THREAD,
                                        effective, sizeof(effective), &required, &error) == AS_OK);
    CHECK(required > 1 && required <= sizeof(effective));
    as_create_config_v0 config;
    as_create_config_v0_init(&config);
    config.epoch = 1;
    config.config_json = effective;
    config.config_json_length = required - 1;
    config.execution_mode = AS_MODE_PROCESSING_THREAD;

    CHECK(reject(registry, "BAD ID", 6, &config, AS_INVALID_ARGUMENT, "malformed provider") == 0);
    CHECK(reject(registry, NULL, 0, &config, AS_INVALID_ARGUMENT, "omitted provider") == 0);
    CHECK(reject(registry, "optional.absent.v0", 18, &config, AS_UNSUPPORTED,
                 "unregistered optional provider") == 0);
    config.execution_mode = AS_MODE_INLINE_CALLBACK;
    CHECK(reject(registry, id, length, &config, AS_UNSUPPORTED, "unavailable callback mode") == 0);
    config.execution_mode = AS_MODE_PROCESSING_THREAD;

    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, id, length, &config, &session, &error) == AS_OK);
    float input[AS_FRAME_SAMPLES] = {0}, samples[AS_FRAME_SAMPLES] = {0};
    input[20] = 0.5f;
    float original[AS_FRAME_SAMPLES];
    memcpy(original, input, sizeof(input));
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 1;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(memcmp(input, original, sizeof(input)) == 0);
    CHECK(result.consumed_count == AS_FRAME_SAMPLES && result.produced_count == AS_FRAME_SAMPLES);
    CHECK(result.epoch == 1 && result.source_first_sample == -delay);
    CHECK(result.valid_count == (uint32_t)(AS_FRAME_SAMPLES - delay));
    if (!delay) CHECK(result.valid_offset == 0);
    for (size_t i = 0; i < AS_FRAME_SAMPLES; ++i) CHECK(isfinite(samples[i]));

    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    if (delay) {
        CHECK(as_session_drain_next_v0(session, &output, &result) == AS_OK);
        CHECK(result.consumed_count == 0 && result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.epoch == 1 && result.source_first_sample == 0 && result.valid_offset == 0);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (size_t i = 0; i < AS_FRAME_SAMPLES; ++i) CHECK(isfinite(samples[i]));
    }
    CHECK(as_session_drain_next_v0(session, &output, &result) == AS_END_OF_STREAM);
    CHECK(result.valid_count == 0);
    CHECK(as_session_close_v0(&session) == AS_OK && session == NULL);
    printf("%s: mode 2; buffering=%d samples; valid source=[0,160); drained\n", id, delay);
    return 0;
}

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(smoke(registry, "speex.ns.v0", 160) == 0);
    CHECK(smoke(registry, "dsp.highpass80.v0", 0) == 0);
    CHECK(as_registry_close_v0(&registry) == AS_OK && registry == NULL);
    return 0;
}
