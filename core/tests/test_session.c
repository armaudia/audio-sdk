/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "test_common.h"

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    CHECK(test_open(&registry, &session, "dsp.highpass80.v0",
                    AS_MODE_PROCESSING_THREAD, 1, 0));
    as_result_v0 result;
    CHECK(test_process(session, 1, 0, &result));
    CHECK(result.source_first_sample == 0);
    CHECK(result.consumed_count == AS_FRAME_SAMPLES);
    CHECK(result.produced_count == AS_FRAME_SAMPLES);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
