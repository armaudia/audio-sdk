/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define PROVIDER_ID "detection.adaptive-energy-to-silero-cascade.refv0"

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

static as_status_v0 feed(as_session_v0 *session, uint64_t epoch,
                         int64_t first_sample, const float *samples,
                         uint32_t valid_count, uint32_t flags,
                         float *output, as_result_v0 *result) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = samples;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = valid_count;
    frame.flags = flags;
    frame.epoch = epoch;
    frame.first_input_sample = first_sample;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return as_session_process_v0(session, &frame, &sink, result);
}

static void fill(float *samples, double amplitude) {
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        samples[index] = (float)(amplitude * ((index & 1u) ? 1.0 : -1.0));
    }
}

#ifdef AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE
as_status_v0 adaptive_energy_to_silero_cascade_register(as_registry_v0 *registry,
                                                        as_error_v0 *error);

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0;
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_INLINE_CALLBACK,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_BUFFERED_WORKER,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_PROCESSING_THREAD,
          config, sizeof(config), &required, error) == AS_OK);

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 11;
    create.first_input_sample = 42;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), &create, &session, error) == AS_OK);
    CHECK(session != NULL);

    float samples[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);

    /* 60 quiet frames exercise the sleep gate and a 50-frame stub cross-check.
       Output and exact source coordinates must remain unchanged. */
    memset(samples, 0, sizeof(samples));
    for (uint32_t frame = 0; frame < 60; ++frame) {
        CHECK(feed(session, 11, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(memcmp(samples, output, sizeof(samples)) == 0);
    }
    /* Loud frames wake the gate; passthrough and intervals remain exact. */
    fill(samples, 0.15);
    for (uint32_t frame = 0; frame < 6; ++frame) {
        CHECK(feed(session, 11, 42 + (int64_t)(60 + frame) * AS_FRAME_SAMPLES,
                   samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_OK);
        CHECK(result.source_first_sample ==
              42 + (int64_t)(60 + frame) * AS_FRAME_SAMPLES);
        CHECK(memcmp(samples, output, sizeof(samples)) == 0);
    }

    /* Bad frames and stale coordinates are rejected without changing position. */
    float bad[AS_FRAME_SAMPLES];
    memcpy(bad, samples, sizeof(bad));
    bad[7] = NAN;
    CHECK(feed(session, 11, 42 + (int64_t)66 * AS_FRAME_SAMPLES,
               bad, AS_FRAME_SAMPLES, 0, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 10, 42 + (int64_t)66 * AS_FRAME_SAMPLES,
               samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_INVALID_ARGUMENT);
    /* The session facade rejects non-contiguous intervals before the provider. */
    CHECK(feed(session, 11, 42 + (int64_t)67 * AS_FRAME_SAMPLES,
               samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 11, 42 + (int64_t)66 * AS_FRAME_SAMPLES,
               samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_OK);

    /* Reset starts a fresh epoch and fresh cascade/stub state. */
    CHECK(as_session_reset_v0(session, 12, 42, error) == AS_OK);
    CHECK(feed(session, 12, 42, samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_OK);
    CHECK(result.epoch == 12);
    CHECK(result.source_first_sample == 42);
    CHECK(memcmp(samples, output, sizeof(samples)) == 0);
    CHECK(feed(session, 12, 42 + (int64_t)AS_FRAME_SAMPLES,
               samples, AS_FRAME_SAMPLES, 0, output, &result) == AS_OK);

    /* Short final input maps exactly 80 accepted samples; tail is zero. */
    for (uint32_t index = 80; index < AS_FRAME_SAMPLES; ++index) samples[index] = 0.0f;
    CHECK(feed(session, 12, 42 + (int64_t)2 * AS_FRAME_SAMPLES,
               samples, 80, AS_FRAME_FINAL_INPUT, output, &result) == AS_OK);
    CHECK(result.valid_count == 80);
    CHECK(result.source_first_sample == 42 + (int64_t)2 * AS_FRAME_SAMPLES);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional cascade stub registered; passthrough/reset/drain passed");
    return 0;
}
#endif

int main(void) {
    as_registry_v0 *registry = NULL;
    as_registry_v0 *other = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(query(registry, "speex.ns.v0") == AS_OK);
    CHECK(query(registry, "dsp.highpass80.v0") == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_UNSUPPORTED);
#ifndef AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(adaptive_energy_to_silero_cascade_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(adaptive_energy_to_silero_cascade_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
