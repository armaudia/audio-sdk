/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "expected_vectors.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define RB3_PROVIDER_ID "rate.rubber-band-r3-streaming-reference.v0"
#define STIMULUS_LENGTH 12457u
#define FINAL_VALID 137u

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

static float arithmetic_stimulus(uint32_t sample) {
    const uint32_t residue = (sample * 41u + (sample / 19u) * 7u) % 199u;
    return (float)((int)residue - 99) / 512.0f;
}

static void frame_init(as_frame_v0 *frame, uint64_t epoch, int64_t first,
                       const float *samples, uint32_t valid, uint32_t flags) {
    as_frame_v0_init(frame);
    frame->input = samples;
    frame->input_count = AS_FRAME_SAMPLES;
    frame->input_valid_count = valid;
    frame->flags = flags;
    frame->epoch = epoch;
    frame->first_input_sample = first;
}

static as_status_v0 feed(as_session_v0 *session, uint64_t epoch, int64_t first,
                         const float *samples, uint32_t valid, uint32_t flags,
                         float *output, as_result_v0 *result) {
    as_frame_v0 frame;
    frame_init(&frame, epoch, first, samples, valid, flags);
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return as_session_process_v0(session, &frame, &sink, result);
}

static void content_hex(const float *samples, size_t count, char *hex) {
    (void)as_sha256_hex_v0(samples, (uint64_t)count * sizeof(float), hex, 65u);
}

#ifdef AS_ENABLE_RUBBER_BAND_R3_STREAMING
as_status_v0 rubber_band_r3_streaming_register(as_registry_v0 *registry,
                                               as_error_v0 *error);

static int parity_stream(as_session_v0 *session, as_error_v0 *error) {
    (void)error;
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    float content[65536];
    size_t content_count = 0u;
    uint32_t first_output_frame = 0u;
    int saw_output = 0;
    as_result_v0 result;
    as_result_v0_init(&result);

    for (uint32_t frame = 0u; frame < RB3_EXPECTED_FRAME_COUNT; ++frame) {
        const uint32_t start = frame * AS_FRAME_SAMPLES;
        uint32_t valid = AS_FRAME_SAMPLES;
        uint32_t flags = 0u;
        if (start + AS_FRAME_SAMPLES >= STIMULUS_LENGTH) {
            valid = STIMULUS_LENGTH - start;
            flags = AS_FRAME_FINAL_INPUT;
        }
        for (uint32_t index = 0u; index < valid; ++index)
            input[index] = arithmetic_stimulus(start + index);
        for (uint32_t index = valid; index < AS_FRAME_SAMPLES; ++index)
            input[index] = 0.0f;

        if (frame == 10u) {
            const int64_t next = (int64_t)start;
            as_result_v0 rejected;
            float bad_input[AS_FRAME_SAMPLES];
            memset(bad_input, 0, sizeof(bad_input));
            bad_input[3] = (float)NAN;
            as_result_v0_init(&rejected);
            CHECK(feed(session, 1u, next, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            bad_input[3] = arithmetic_stimulus(start + 3u);
            CHECK(feed(session, 2u, next, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(feed(session, 1u, next + 1, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(feed(session, 1u, next, bad_input, 0u, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(feed(session, 1u, next, bad_input, AS_FRAME_SAMPLES - 1u, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
        }

        CHECK(feed(session, 1u, (int64_t)start, input, valid, flags,
                   output, &result) == AS_OK);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.consumed_count == AS_FRAME_SAMPLES);
        CHECK(result.valid_offset == 0u);
        CHECK(result.valid_count == kExpectedValidCounts[frame]);
        CHECK(result.source_first_sample == (int64_t)start);
        CHECK(result.epoch == 1u);
        if (result.valid_count && !saw_output) {
            saw_output = 1;
            first_output_frame = frame;
        }
        for (uint32_t index = 0u; index < result.valid_count; ++index) {
            CHECK(isfinite((double)output[index]));
            CHECK(fabs((double)output[index]) <= 1.0);
            CHECK(content_count < sizeof(content) / sizeof(content[0]));
            content[content_count++] = output[index];
        }
        if (flags != 0u) {
            CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0u);
            CHECK(valid == FINAL_VALID);
        }
    }
    CHECK(saw_output == 1);
    CHECK(first_output_frame == RB3_EXPECTED_FIRST_OUTPUT_FRAME);
    CHECK(content_count == RB3_EXPECTED_CONTENT_SAMPLES);
    char digest[65];
    content_hex(content, content_count, digest);
    CHECK(strcmp(digest, RB3_EXPECTED_CONTENT_DIGEST) == 0);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    as_status_v0 status = as_session_drain_next_v0(session, &sink, &result);
    CHECK(status == AS_END_OF_STREAM);
    CHECK(result.status == AS_END_OF_STREAM);
    CHECK(result.produced_count == 0u);
    CHECK(result.valid_count == 0u);
    CHECK(RB3_EXPECTED_DRAIN_NON_CONTENT_SAMPLES > 0u);
    return 0;
}

static int replay_digest(as_session_v0 *session, uint64_t epoch, int64_t first,
                         char *digest) {
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    float content[5u * AS_FRAME_SAMPLES];
    size_t count = 0u;
    as_result_v0 result;
    as_result_v0_init(&result);
    for (uint32_t frame = 0u; frame < 5u; ++frame) {
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index)
            input[index] = arithmetic_stimulus((uint32_t)first + frame * AS_FRAME_SAMPLES + index);
        CHECK(feed(session, epoch, first + (int64_t)(frame * AS_FRAME_SAMPLES),
                   input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
        for (uint32_t index = 0u; index < result.valid_count; ++index)
            content[count++] = output[index];
    }
    content_hex(content, count, digest);
    return 0;
}

static int descriptor_pins(as_registry_v0 *registry, as_error_v0 *error) {
    char descriptor[4096];
    uint32_t required = 0u;
    CHECK(as_query_provider_v0(registry, RB3_PROVIDER_ID,
        (uint32_t)strlen(RB3_PROVIDER_ID), descriptor, sizeof(descriptor),
        &required) == AS_OK);
    char pinned[256];
    (void)error;
    snprintf(pinned, sizeof(pinned), "sha256:%s", RB3_EXPECTED_CONFIG_DIGEST);
    CHECK(strstr(descriptor, pinned) != NULL);
    snprintf(pinned, sizeof(pinned), "sha256:%s", RB3_EXPECTED_PROVIDER_SOURCE_DIGEST);
    CHECK(strstr(descriptor, pinned) != NULL);
    return 0;
}

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    CHECK(as_effective_config_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), AS_MODE_INLINE_CALLBACK,
            config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), AS_MODE_BUFFERED_WORKER,
            config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), AS_MODE_PROCESSING_THREAD,
            config, sizeof(config), &required, error) == AS_OK);
    CHECK(descriptor_pins(registry, error) == 0);

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), &create, &session, error) == AS_OK);
    CHECK(session != NULL);
    CHECK(parity_stream(session, error) == 0);

    CHECK(as_session_reset_v0(session, 3u, 9000, error) == AS_OK);
    char first_digest[65];
    char second_digest[65];
    CHECK(replay_digest(session, 3u, 9000, first_digest) == 0);
    CHECK(as_session_reset_v0(session, 4u, 9000, error) == AS_OK);
    CHECK(replay_digest(session, 4u, 9000, second_digest) == 0);
    CHECK(strcmp(first_digest, second_digest) == 0);

    as_session_v0 *other = NULL;
    CHECK(as_session_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), &create, &other, error) == AS_OK);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(input, 0, sizeof(input));
    CHECK(feed(other, 1u, 0, input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
    CHECK(result.valid_count == 0u);
    CHECK(as_session_close_v0(&other) == AS_OK);

    as_session_v0 *final_session = NULL;
    CHECK(as_session_create_v0(registry, RB3_PROVIDER_ID,
            (uint32_t)strlen(RB3_PROVIDER_ID), &create, &final_session, error) == AS_OK);
    CHECK(feed(final_session, 1u, 0, input, AS_FRAME_SAMPLES,
               AS_FRAME_FINAL_INPUT, output, &result) == AS_OK);
    CHECK(feed(final_session, 1u, AS_FRAME_SAMPLES, input, AS_FRAME_SAMPLES,
               0u, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(as_session_close_v0(&final_session) == AS_OK);

    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered; parity, rate mapping, final frame, drain, rejections and reset passed");
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
    CHECK(query(registry, RB3_PROVIDER_ID) == AS_UNSUPPORTED);
#ifndef AS_ENABLE_RUBBER_BAND_R3_STREAMING
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(rubber_band_r3_streaming_register(registry, &error) == AS_OK);
    CHECK(query(registry, RB3_PROVIDER_ID) == AS_OK);
    CHECK(rubber_band_r3_streaming_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, RB3_PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
