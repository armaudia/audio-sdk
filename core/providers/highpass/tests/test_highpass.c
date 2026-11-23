/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "test_common.h"

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    CHECK(test_open(&registry, &session, "dsp.highpass80.v0",
                    AS_MODE_PROCESSING_THREAD, 1, 0));
    float input[AS_FRAME_SAMPLES] = {0};
    float output_samples[AS_FRAME_SAMPLES] = {0};
    input[0] = 1.0f;
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 1;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = output_samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(output_samples[0] > 0.0f);
    CHECK(output_samples[0] < 1.0f);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
