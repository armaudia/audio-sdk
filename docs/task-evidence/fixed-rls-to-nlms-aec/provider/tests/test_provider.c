/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "crosscheck_vectors.h"
#include "fixed_rls_nlms_provider.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define PROVIDER_ID "aec.fixed-rls-nlms-reference.v0"
#define HANDOFF_FRAME (FIXED_HANDOFF_SAMPLE_TEST / AS_FRAME_SAMPLES)

/* Kept independent of the provider implementation constants. */
#define FIXED_HANDOFF_SAMPLE_TEST 4000

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
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

#ifdef AS_ENABLE_FIXED_RLS_NLMS_AEC
static int parity_check(char *config, uint32_t config_length, as_error_v0 *error) {
    void *instance = NULL;
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = config_length;
    CHECK(fixed_rls_nlms_instance_create(&create, &instance, error) == AS_OK);
    CHECK(instance != NULL);

    for (uint32_t frame = 0u; frame < CROSSCHECK_FRAMES; ++frame) {
        const uint32_t start = frame * AS_FRAME_SAMPLES;
        CHECK(fixed_rls_nlms_feed_reference(instance, kCrosscheckRef + start,
                                            AS_FRAME_SAMPLES, error) == AS_OK);
        as_frame_v0 input;
        frame_init(&input, 1u, (int64_t)start,
                   kCrosscheckMic + start, AS_FRAME_SAMPLES, 0u);
        float output[AS_FRAME_SAMPLES];
        as_output_v0 sink;
        as_output_v0_init(&sink);
        sink.samples = output;
        sink.capacity = AS_FRAME_SAMPLES;
        as_result_v0 result;
        as_result_v0_init(&result);
        CHECK(fixed_rls_nlms_instance_process(instance, &input, &sink, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(result.source_first_sample == (int64_t)start);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
            CHECK(fabs((double)output[index] -
                       (double)kCrosscheckOutput[start + index]) < 2e-5);
        }
        uint64_t frames = 0u, adapted = 0u, holds = 0u, noref = 0u, invalid = 0u;
        uint64_t safety = 0u;
        double weight_l1 = 0.0;
        uint32_t phase = 99u;
        int64_t handoff = -2;
        CHECK(fixed_rls_nlms_snapshot(instance, &frames, &adapted, &holds, &noref,
                                      &invalid, &safety, &weight_l1, &phase,
                                      &handoff) == AS_OK);
        CHECK(frames == (uint64_t)frame + 1u);
        CHECK(adapted > 0u);
        CHECK(invalid == 0u);
        CHECK(safety == 0u);
        CHECK(noref == 0u);
        CHECK(weight_l1 <= 8.0);
        CHECK(fabs(weight_l1 - kCrosscheckWeightL1[frame]) < 1e-7);
        CHECK(phase == (uint32_t)kCrosscheckPhase[frame]);
        CHECK(handoff == (int64_t)kCrosscheckHandoffSample[frame]);
        if (frame < HANDOFF_FRAME) {
            CHECK(strcmp(fixed_rls_nlms_handoff_reason(instance), "none") == 0);
        } else {
            CHECK(handoff == (int64_t)FIXED_HANDOFF_SAMPLE_TEST);
            CHECK(strcmp(fixed_rls_nlms_handoff_reason(instance), "scheduled") == 0);
        }
    }

    /* No paired reference: bit-exact passthrough and no adaptation. */
    uint64_t frames = 0u, adapted = 0u, holds = 0u, noref = 0u, invalid = 0u;
    uint64_t safety = 0u;
    double before = 0.0, after = 0.0;
    uint32_t phase = 99u;
    int64_t handoff = -2;
    CHECK(fixed_rls_nlms_snapshot(instance, &frames, &adapted, &holds, &noref,
                                  &invalid, &safety, &before, &phase,
                                  &handoff) == AS_OK);
    as_frame_v0 input;
    frame_init(&input, 1u, (int64_t)CROSSCHECK_SAMPLES,
               kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
    float output[AS_FRAME_SAMPLES];
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    as_result_v0 result;
    as_result_v0_init(&result);
    CHECK(fixed_rls_nlms_instance_process(instance, &input, &sink, &result) == AS_OK);
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        CHECK(output[index] == kCrosscheckMic[index]);
    }
    const uint64_t adapted_before = adapted;
    CHECK(fixed_rls_nlms_snapshot(instance, &frames, &adapted, &holds, &noref,
                                  &invalid, &safety, &after, &phase,
                                  &handoff) == AS_OK);
    CHECK(fabs(before - after) < 1e-12);
    CHECK(adapted == adapted_before);
    CHECK(noref == 1u);
    CHECK(phase == 1u);
    CHECK(handoff == (int64_t)FIXED_HANDOFF_SAMPLE_TEST);

    /* Invalid sidechain frames do not arm the reference or mutate state. */
    float bad[AS_FRAME_SAMPLES];
    memcpy(bad, kCrosscheckRef, sizeof(bad));
    bad[11] = (float)NAN;
    CHECK(fixed_rls_nlms_feed_reference(instance, bad, AS_FRAME_SAMPLES, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(fixed_rls_nlms_feed_reference(instance, kCrosscheckRef, 8u, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(fixed_rls_nlms_feed_reference(instance, NULL, AS_FRAME_SAMPLES, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(fixed_rls_nlms_snapshot(instance, &frames, &adapted, &holds, &noref,
                                  &invalid, &safety, &after, &phase,
                                  &handoff) == AS_OK);
    CHECK(fabs(before - after) < 1e-12);
    CHECK(noref == 1u);
    CHECK(invalid == 0u);

    /* Frame rejection and epoch-ordered reset are explicit. */
    memcpy(bad, kCrosscheckMic, sizeof(bad));
    bad[3] = (float)INFINITY;
    frame_init(&input, 1u, (int64_t)CROSSCHECK_SAMPLES + AS_FRAME_SAMPLES,
               bad, AS_FRAME_SAMPLES, 0u);
    CHECK(fixed_rls_nlms_instance_process(instance, &input, &sink, &result) ==
          AS_INVALID_ARGUMENT);
    frame_init(&input, 2u, (int64_t)CROSSCHECK_SAMPLES + AS_FRAME_SAMPLES,
               kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
    CHECK(fixed_rls_nlms_instance_process(instance, &input, &sink, &result) ==
          AS_INVALID_ARGUMENT);
    CHECK(fixed_rls_nlms_instance_reset(instance, 4u, 9000, error) == AS_OK);
    CHECK(fixed_rls_nlms_snapshot(instance, &frames, &adapted, &holds, &noref,
                                  &invalid, &safety, &after, &phase,
                                  &handoff) == AS_OK);
    CHECK(frames == 0u && adapted == 0u && holds == 0u && noref == 0u);
    CHECK(invalid == 0u && safety == 0u);
    CHECK(after == 0.0);
    CHECK(phase == 0u);
    CHECK(handoff == -1);
    CHECK(strcmp(fixed_rls_nlms_handoff_reason(instance), "none") == 0);
    CHECK(fixed_rls_nlms_instance_reset(instance, 4u, 9000, error) ==
          AS_INVALID_ARGUMENT);
    fixed_rls_nlms_instance_destroy(instance);
    return 0;
}

static int session_check(as_registry_v0 *registry, as_error_v0 *error) {
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
    create.first_input_sample = 42;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    create.config_json = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &session, error) ==
           AS_INVALID_ARGUMENT);
    create.config_json = config;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &session, error) == AS_OK);
    CHECK(session != NULL);

    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    /* Sessions have no sidechain: microphone passthrough, never adaptation. */
    CHECK(feed(session, 1u, 42, kCrosscheckMic, AS_FRAME_SAMPLES,
               0u, output, &result) == AS_OK);
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        CHECK(output[index] == kCrosscheckMic[index]);
    }
    CHECK(result.valid_count == AS_FRAME_SAMPLES);

    float partial[AS_FRAME_SAMPLES];
    memset(partial, 0, sizeof(partial));
    for (uint32_t index = 0u; index < 37u; ++index) partial[index] = 0.01f;
    CHECK(feed(session, 1u, 42 + AS_FRAME_SAMPLES, partial, 37u,
               AS_FRAME_FINAL_INPUT, output, &result) == AS_OK);
    CHECK(result.valid_count == 37u);
    CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0u);
    CHECK(as_session_reset_v0(session, 1u, 42, error) == AS_INVALID_ARGUMENT);
    CHECK(as_session_reset_v0(session, 2u, 9000, error) == AS_OK);
    CHECK(feed(session, 2u, 9000, kCrosscheckMic, AS_FRAME_SAMPLES,
               0u, output, &result) == AS_OK);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_drain_next_v0(session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    return 0;
}

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), AS_MODE_PROCESSING_THREAD,
           config, sizeof(config), &required, error) == AS_OK);
    CHECK(parity_check(config, required - 1u, error) == 0);
    CHECK(session_check(registry, error) == 0);
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
#ifndef AS_ENABLE_FIXED_RLS_NLMS_AEC
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(fixed_rls_nlms_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(fixed_rls_nlms_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
    puts("optional reference registered; Python parity, fixed handoff, explicit reference, passthrough, reset and session checks passed");
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
