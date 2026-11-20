/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "test_common.h"

#include <time.h>

static as_status_v0 wait_output(as_session_v0 *session,
                                const as_output_v0 *output, as_result_v0 *result) {
    const struct timespec pause = {0, 1000000L};
    for (unsigned attempt = 0; attempt < 2000; ++attempt) {
        as_result_v0_init(result);
        const as_status_v0 status = as_session_drain_next_v0(session, output, result);
        if (status != AS_NOT_READY) return status;
        nanosleep(&pause, NULL);
    }
    return AS_NOT_READY;
}

static int check_partial(uint32_t mode) {
    const uint64_t epoch = UINT64_C(9007199254740993);
    const int64_t first = INT64_C(9007199254740993);
    const int buffered = mode == AS_MODE_BUFFERED_WORKER;
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    CHECK(test_open(&registry, &session, "speex.ns.v0", mode, epoch, first));
    float input[AS_FRAME_SAMPLES] = {0.25f};
    float output_samples[AS_FRAME_SAMPLES];
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.input_valid_count = 1;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.first_input_sample = first;
    frame.epoch = epoch;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = output_samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    if (buffered) {
        CHECK(as_session_submit_v0(session, &frame, &result) == AS_OK);
        CHECK(result.epoch == epoch && result.source_first_sample == first);
        CHECK(result.consumed_count == 160 && result.produced_count == 0);
        CHECK(result.valid_count == 0);
        CHECK(as_session_begin_drain_v0(session) == AS_OK);
        CHECK(wait_output(session, &output, &result) == AS_OK);
        CHECK(result.consumed_count == 0);
    } else {
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        CHECK(result.consumed_count == 160);
        CHECK(as_session_begin_drain_v0(session) == AS_OK);
    }
    CHECK(result.epoch == epoch && result.source_first_sample == first - 160);
    CHECK(result.produced_count == 160 && result.valid_count == 0);
    CHECK(result.valid_offset == 160 && result.flags == AS_RESULT_STARTUP_PADDING);
    CHECK(wait_output(session, &output, &result) == AS_OK);
    CHECK(result.epoch == epoch && result.source_first_sample == first);
    CHECK(result.produced_count == 160 && result.consumed_count == 0);
    CHECK(result.valid_offset == 0 && result.valid_count == 1);
    CHECK(result.flags == AS_RESULT_FINAL_PADDING);
    for (int i = 0; i < 2; ++i) {
        CHECK(wait_output(session, &output, &result) == AS_END_OF_STREAM);
        CHECK(result.produced_count == 0 && result.valid_count == 0);
    }
    char stats[4096];
    uint32_t required = 0;
    CHECK(as_session_get_stats_v0(session, stats, sizeof(stats), &required) == AS_OK);
    CHECK(strstr(stats, "\"epoch\":\"9007199254740993\"") != NULL);
    CHECK(strstr(stats, "\"accepted_valid_samples\":\"1\"") != NULL);
    CHECK(strstr(stats, "\"delivered_valid_samples\":\"1\"") != NULL);
    CHECK(strstr(stats, "\"startup_padding_samples\":\"160\"") != NULL);
    CHECK(strstr(stats, "\"final_padding_samples\":\"159\"") != NULL);

    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_session_reset_v0(session, epoch + 1, INT64_MAX - 160, &error) == AS_OK);
    frame.epoch = epoch + 1;
    for (int i = 0; i < 3; ++i) {
        /* Reject stale epoch, a one-sample offset above 2^53, and padded overflow. */
        frame.epoch = i == 0 ? epoch : epoch + 1;
        frame.first_input_sample = i == 0 ? INT64_MAX - 160 :
                                   i == 1 ? INT64_MAX - 161 : INT64_MAX - 159;
        as_result_v0_init(&result);
        const as_status_v0 status = buffered
            ? as_session_submit_v0(session, &frame, &result)
            : as_session_process_v0(session, &frame, &output, &result);
        CHECK(status == AS_INVALID_ARGUMENT && result.consumed_count == 0);
        CHECK(result.produced_count == 0 && result.valid_count == 0);
    }
    frame.first_input_sample = INT64_MAX - 160;
    as_result_v0_init(&result);
    CHECK((buffered ? as_session_submit_v0(session, &frame, &result)
                    : as_session_process_v0(session, &frame, &output, &result)) == AS_OK);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    if (buffered) CHECK(wait_output(session, &output, &result) == AS_OK);
    CHECK(wait_output(session, &output, &result) == AS_OK);
    CHECK(result.epoch == epoch + 1 && result.source_first_sample == INT64_MAX - 160);
    CHECK(result.valid_offset == 0 && result.valid_count == 1);
    CHECK(wait_output(session, &output, &result) == AS_END_OF_STREAM);

    CHECK(as_session_reset_v0(session, epoch + 2, first, &error) == AS_OK);
    frame.epoch = epoch + 2;
    frame.first_input_sample = first;
    as_result_v0_init(&result);
    if (buffered) {
        CHECK(as_session_submit_v0(session, &frame, &result) == AS_OK);
        CHECK(wait_output(session, &output, &result) == AS_OK);
    } else {
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    }
    CHECK(result.source_first_sample == first - 160 && result.valid_count == 0);
    if (buffered) {
        as_result_v0_init(&result);
        CHECK(as_session_pull_v0(session, &output, &result) == AS_NOT_READY);
        CHECK(result.produced_count == 0 && result.valid_count == 0);
    }
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    /* Only the padded startup output was delivered; [first, first+1) is pending
     * whether the worker has produced the tail or it still lives in Speex. */
    CHECK(as_session_reset_v0(session, epoch + 3, first + 500, &error) == AS_OK);
    CHECK(as_session_get_stats_v0(session, stats, sizeof(stats), &required) == AS_OK);
    CHECK(strstr(stats, "\"cancelled_valid_samples\":\"1\"") != NULL);
    CHECK(strstr(stats, "\"cancelled_intervals\":\"1\"") != NULL);
    CHECK(strstr(stats, "\"delivered_valid_samples\":\"0\"") != NULL);
    as_result_v0_init(&result);
    CHECK(as_session_drain_next_v0(session, &output, &result) ==
          (buffered ? AS_NOT_READY : AS_INVALID_ARGUMENT));
    CHECK(result.epoch == epoch + 3 && result.valid_count == 0);

    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}

int main(void) {
    int inline_result = check_partial(AS_MODE_PROCESSING_THREAD);
    int buffered_result = check_partial(AS_MODE_BUFFERED_WORKER);
    return inline_result || buffered_result;
}
