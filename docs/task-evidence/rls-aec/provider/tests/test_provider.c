/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "crosscheck_vectors.h"
#include "rls_aec_provider.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define PROVIDER_ID "aec.rls-reference.v0"
/* Kept independent of the provider implementation constants. */
#define RLS_P0_INIT 1.0

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

#ifdef AS_ENABLE_RLS_AEC
static as_status_v0 snapshot(void *instance, uint64_t *frames,
                             uint64_t *adapted, uint64_t *holds,
                             uint64_t *noref, uint64_t *invalid,
                             uint64_t *safety, uint64_t *skipped,
                             double *weight_l1, double *max_matrix,
                             uint32_t *phase) {
    return rls_aec_snapshot(instance, frames, adapted, holds, noref, invalid,
                            safety, skipped, weight_l1, max_matrix, phase);
}

static int parity_check(char *config, uint32_t config_length, as_error_v0 *error) {
    void *instance = NULL;
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = config_length;
    CHECK(rls_aec_instance_create(&create, &instance, error) == AS_OK);
    CHECK(instance != NULL);

    for (uint32_t frame = 0u; frame < CROSSCHECK_FRAMES; ++frame) {
        const uint32_t start = frame * AS_FRAME_SAMPLES;
        CHECK(rls_aec_feed_reference(instance, kCrosscheckRef + start,
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
        CHECK(rls_aec_instance_process(instance, &input, &sink, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(result.source_first_sample == (int64_t)start);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
            CHECK(fabs((double)output[index] -
                       (double)kCrosscheckOutput[start + index]) < 2e-5);
        }
        uint64_t frames = 0u, adapted = 0u, holds = 0u, noref = 0u;
        uint64_t invalid = 0u, safety = 0u, skipped = 0u;
        double weight_l1 = 0.0, max_matrix = 0.0;
        uint32_t phase = 99u;
        CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                       &safety, &skipped, &weight_l1, &max_matrix, &phase) == AS_OK);
        CHECK(frames == (uint64_t)frame + 1u);
        CHECK(adapted > 0u);
        CHECK(invalid == 0u && safety == 0u && noref == 0u);
        CHECK(weight_l1 <= 8.0);
        CHECK(fabs(weight_l1 - kCrosscheckWeightL1[frame]) < 1e-7);
        CHECK(skipped == (uint64_t)kCrosscheckSkippedUpdates[frame]);
        CHECK(max_matrix <= 1e12);
        CHECK(phase == 0u);
        CHECK(strcmp(rls_aec_safety_reason(instance), "none") == 0);
    }

    /* No paired reference: passthrough, no adaptation and unchanged state. */
    uint64_t frames = 0u, adapted = 0u, holds = 0u, noref = 0u;
    uint64_t invalid = 0u, safety = 0u, skipped = 0u;
    double before = 0.0, after = 0.0, max_matrix = 0.0;
    uint32_t phase = 99u;
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped, &before, &max_matrix, &phase) == AS_OK);
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
    CHECK(rls_aec_instance_process(instance, &input, &sink, &result) == AS_OK);
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        CHECK(output[index] == kCrosscheckMic[index]);
    }
    const uint64_t adapted_before = adapted;
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped, &after, &max_matrix, &phase) == AS_OK);
    CHECK(fabs(before - after) < 1e-12);
    CHECK(adapted == adapted_before);
    CHECK(noref == 1u);
    CHECK(phase == 0u);

    /* Zero reference: covariance windup guard skips updates, output finite. */
    const float zeros[AS_FRAME_SAMPLES] = {0};
    CHECK(rls_aec_feed_reference(instance, zeros, AS_FRAME_SAMPLES, error) == AS_OK);
    frame_init(&input, 1u, (int64_t)CROSSCHECK_SAMPLES + AS_FRAME_SAMPLES,
               kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
    CHECK(rls_aec_instance_process(instance, &input, &sink, &result) == AS_OK);
    uint64_t skipped_after = 0u;
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped_after, &after, &max_matrix, &phase) == AS_OK);
    CHECK(skipped_after >= skipped);
    CHECK(safety == 0u && phase == 0u && fabs(before - after) < 1e-12);
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        CHECK(isfinite((double)output[index]));
    }

    /* A fresh all-zero-reference stream has no far-end energy.  Every update
     * is skipped, weights stay at zero and the covariance cannot wind up. */
    void *zero_instance = NULL;
    as_create_config_v0 zero_create;
    as_create_config_v0_init(&zero_create);
    zero_create.execution_mode = AS_MODE_PROCESSING_THREAD;
    zero_create.epoch = 1u;
    zero_create.first_input_sample = 0;
    zero_create.config_json = config;
    zero_create.config_json_length = config_length;
    CHECK(rls_aec_instance_create(&zero_create, &zero_instance, error) == AS_OK);
    CHECK(zero_instance != NULL);
    for (uint32_t frame = 0u; frame < 2u; ++frame) {
        CHECK(rls_aec_feed_reference(zero_instance, zeros, AS_FRAME_SAMPLES,
                                     error) == AS_OK);
        frame_init(&input, 1u, (int64_t)(frame * AS_FRAME_SAMPLES),
                   kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
        CHECK(rls_aec_instance_process(zero_instance, &input, &sink,
                                       &result) == AS_OK);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
        }
    }
    uint64_t zero_frames = 0u, zero_adapted = 0u, zero_holds = 0u;
    uint64_t zero_noref = 0u, zero_invalid = 0u, zero_safety = 0u;
    uint64_t zero_skipped = 0u;
    double zero_weight_l1 = -1.0, zero_matrix = -1.0;
    uint32_t zero_phase = 99u;
    CHECK(snapshot(zero_instance, &zero_frames, &zero_adapted, &zero_holds,
                   &zero_noref, &zero_invalid, &zero_safety, &zero_skipped,
                   &zero_weight_l1, &zero_matrix, &zero_phase) == AS_OK);
    CHECK(zero_frames == 2u && zero_adapted == 0u && zero_invalid == 0u);
    CHECK(zero_skipped == 2u * AS_FRAME_SAMPLES);
    CHECK(zero_safety == 0u && zero_phase == 0u);
    CHECK(zero_weight_l1 == 0.0 && zero_matrix == RLS_P0_INIT);
    rls_aec_instance_destroy(zero_instance);

    /* Invalid sidechain frames do not arm the reference or mutate state. */
    float bad[AS_FRAME_SAMPLES];
    memcpy(bad, kCrosscheckRef, sizeof(bad));
    bad[11] = (float)NAN;
    CHECK(rls_aec_feed_reference(instance, bad, AS_FRAME_SAMPLES, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(rls_aec_feed_reference(instance, kCrosscheckRef, 8u, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(rls_aec_feed_reference(instance, NULL, AS_FRAME_SAMPLES, error) ==
          AS_INVALID_ARGUMENT);
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped_after, &after, &max_matrix, &phase) == AS_OK);
    CHECK(noref == 1u && invalid == 0u && fabs(before - after) < 1e-12);

    /* Frame rejection and epoch-ordered reset are explicit. */
    memcpy(bad, kCrosscheckMic, sizeof(bad));
    bad[3] = (float)INFINITY;
    frame_init(&input, 1u, (int64_t)CROSSCHECK_SAMPLES + 2u * AS_FRAME_SAMPLES,
               bad, AS_FRAME_SAMPLES, 0u);
    CHECK(rls_aec_instance_process(instance, &input, &sink, &result) ==
          AS_INVALID_ARGUMENT);
    frame_init(&input, 2u, (int64_t)CROSSCHECK_SAMPLES + 2u * AS_FRAME_SAMPLES,
               kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
    CHECK(rls_aec_instance_process(instance, &input, &sink, &result) ==
          AS_INVALID_ARGUMENT);
    CHECK(rls_aec_instance_reset(instance, 4u, 9000, error) == AS_OK);
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped_after, &after, &max_matrix, &phase) == AS_OK);
    CHECK(frames == 0u && adapted == 0u && holds == 0u && noref == 0u);
    CHECK(invalid == 0u && safety == 0u && skipped_after == 0u);
    CHECK(after == 0.0 && phase == 0u);
    CHECK(strcmp(rls_aec_safety_reason(instance), "none") == 0);
    CHECK(rls_aec_instance_reset(instance, 4u, 9000, error) ==
          AS_INVALID_ARGUMENT);

    /* Forced nonfinite state: finite output, frozen RLS, finite weights. */
    CHECK(rls_aec_feed_reference(instance, kCrosscheckRef, AS_FRAME_SAMPLES,
                                 error) == AS_OK);
    CHECK(rls_aec_inject_nonfinite_state_for_test(instance) == AS_OK);
    frame_init(&input, 4u, 9000, kCrosscheckMic, AS_FRAME_SAMPLES, 0u);
    CHECK(rls_aec_instance_process(instance, &input, &sink, &result) == AS_OK);
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        CHECK(output[index] == kCrosscheckMic[index]);
    }
    CHECK(snapshot(instance, &frames, &adapted, &holds, &noref, &invalid,
                   &safety, &skipped_after, &after, &max_matrix, &phase) == AS_OK);
    CHECK(safety == 1u && phase == 1u && adapted == 0u);
    CHECK(isfinite(after) && after == 0.0);
    CHECK(strcmp(rls_aec_safety_reason(instance), "nonfinite_state") == 0);

    rls_aec_instance_destroy(instance);
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
#ifndef AS_ENABLE_RLS_AEC
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(rls_aec_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(rls_aec_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
    puts("optional reference registered; Python parity, zero-reference guard, explicit reference, passthrough, safety guard, reset and session checks passed");
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
