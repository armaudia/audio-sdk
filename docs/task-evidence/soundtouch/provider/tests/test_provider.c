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

#define PROVIDER_ID "rate.soundtouch-reference.v0"
#define STIMULUS_LENGTH 12457u
#define FINAL_VALID 137u

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

static float arithmetic_stimulus(uint32_t sample) {
    const uint32_t residue = (sample * 37u + (sample / 17u) * 13u) % 201u;
    return (float)((int)residue - 100) / 512.0f;
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

#ifdef AS_ENABLE_SOUNDTOUCH_REFERENCE
as_status_v0 soundtouch_reference_register(as_registry_v0 *registry,
                                          as_error_v0 *error);

static int parity_stream(as_session_v0 *session, as_error_v0 *error) {
    (void)error;
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    float content[65536];
    size_t content_count = 0u;
    as_result_v0 result;
    as_result_v0_init(&result);

    for (uint32_t frame = 0u; frame < EXPECTED_FRAME_COUNT; ++frame) {
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
            /* Invalid/missing/nonfinite cases must fail closed and leave state intact. */
            const int64_t next = (int64_t)start;
            as_result_v0 rejected;
            float bad_input[AS_FRAME_SAMPLES];
            memset(bad_input, 0, sizeof(bad_input));
            bad_input[3] = (float)NAN;
            as_result_v0_init(&rejected);
            CHECK(feed(session, 1u, next, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            bad_input[3] = 0.0f;
            CHECK(feed(session, 2u, next, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(feed(session, 1u, next + 1, bad_input, AS_FRAME_SAMPLES, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(feed(session, 1u, next, bad_input, AS_FRAME_SAMPLES - 1u, 0u,
                       output, &rejected) == AS_INVALID_ARGUMENT);
            CHECK(as_session_reset_v0(session, 1u, 0, error) == AS_INVALID_ARGUMENT);
        }

        CHECK(feed(session, 1u, (int64_t)start, input, valid, flags,
                   output, &result) == AS_OK);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.consumed_count == AS_FRAME_SAMPLES);
        CHECK(result.valid_offset == 0u);
        CHECK(result.valid_count == kExpectedValidCounts[frame]);
        CHECK(result.source_first_sample == (int64_t)start);
        CHECK(result.epoch == 1u);
        for (uint32_t index = 0u; index < result.valid_count; ++index) {
            CHECK(isfinite((double)output[index]));
            CHECK(fabs((double)output[index]) <= 1.0);
            CHECK(content_count < sizeof(content) / sizeof(content[0]));
            content[content_count++] = output[index];
        }
        for (uint32_t index = result.valid_count; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(output[index] == 0.0f);
        }
        if (flags != 0u) {
            CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0u);
            CHECK(valid == FINAL_VALID);
        }
    }
    CHECK(content_count == EXPECTED_CONTENT_SAMPLES);
    char digest[65];
    content_hex(content, content_count, digest);
    CHECK(strcmp(digest, EXPECTED_CONTENT_DIGEST) == 0);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    uint32_t calls = 0u;
    as_status_v0 status = AS_OK;
    while (calls < 16u) {
        status = as_session_drain_next_v0(session, &sink, &result);
        CHECK(status == AS_OK || status == AS_END_OF_STREAM);
        ++calls;
        if (status == AS_END_OF_STREAM) break;
    }
    CHECK(status == AS_END_OF_STREAM);
    CHECK(calls == 1u);
    CHECK(result.status == AS_END_OF_STREAM);
    CHECK(EXPECTED_DRAIN_NON_CONTENT_SAMPLES > 0u);
    return 0;
}

static int reset_replay(as_session_v0 *session, uint64_t epoch, int64_t first,
                        char *digest) {
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    float content[5u * AS_FRAME_SAMPLES];
    size_t count = 0u;
    as_result_v0 result;
    as_result_v0_init(&result);
    for (uint32_t frame = 0u; frame < 5u; ++frame) {
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index)
            input[index] = arithmetic_stimulus(frame * AS_FRAME_SAMPLES + index);
        CHECK(feed(session, epoch, first + (int64_t)(frame * AS_FRAME_SAMPLES),
                   input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
        for (uint32_t index = 0u; index < result.valid_count; ++index)
            content[count++] = output[index];
    }
    content_hex(content, count, digest);
    return 0;
}

/* A provider-originated rejection moves the session to NEEDS_RESET, so the
 * out-of-range case uses a throwaway session instead of the parity stream. */
static int range_rejection(as_registry_v0 *registry,
                           const as_create_config_v0 *create,
                           as_error_v0 *error) {
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), create, &session, error) == AS_OK);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(input, 0, sizeof(input));
    memset(output, 0, sizeof(output));
    input[3] = 2.0f;
    /* Provider-level rejection is mapped to AS_BACKEND_FAILURE by the session
     * boundary; the provider itself rejects with AS_INVALID_ARGUMENT. */
    CHECK(feed(session, create->epoch, create->first_input_sample, input,
               AS_FRAME_SAMPLES, 0u, output, &result) == AS_BACKEND_FAILURE);
    CHECK(as_session_close_v0(&session) == AS_OK);
    return 0;
}

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
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
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &session, error) == AS_OK);
    CHECK(session != NULL);
    CHECK(parity_stream(session, error) == 0);

    /* Ordered resets replay a deterministic prefix at a new source offset. */
    CHECK(as_session_reset_v0(session, 3u, 9000, error) == AS_OK);
    char first_digest[65];
    char second_digest[65];
    CHECK(reset_replay(session, 3u, 9000, first_digest) == 0);
    CHECK(as_session_reset_v0(session, 4u, 9000, error) == AS_OK);
    CHECK(reset_replay(session, 4u, 9000, second_digest) == 0);
    CHECK(strcmp(first_digest, second_digest) == 0);

    /* A fresh session starts with empty buffered state. */
    as_session_v0 *other = NULL;
    CHECK(range_rejection(registry, &create, error) == 0);
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &other, error) == AS_OK);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(input, 0, sizeof(input));
    CHECK(feed(other, 1u, 0, input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
    CHECK(result.valid_count == 0u);
    CHECK(as_session_close_v0(&other) == AS_OK);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered; parity, rate clock, final frame, drain, rejections and reset passed");
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
#ifndef AS_ENABLE_SOUNDTOUCH_REFERENCE
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(soundtouch_reference_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(soundtouch_reference_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
