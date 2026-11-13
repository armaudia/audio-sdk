#include "core/as_internal.h"
#include "test_common.h"

#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

static int expect(as_session_v0 *session, int64_t source_first,
                  uint32_t produced, uint32_t provider_offset,
                  uint32_t provider_count, int64_t accepted_end,
                  uint32_t expected_offset, uint32_t expected_count,
                  const char *label) {
    as_result_v0 result;
    as_result_v0_init(&result);
    as_compute_validity(session, source_first, produced, provider_offset,
                        provider_count, accepted_end, 0, &result);
    if (result.valid_offset != expected_offset ||
        result.valid_count != expected_count ||
        result.valid_offset > produced ||
        result.valid_count > produced - result.valid_offset) {
        fprintf(stderr,
                "%s: got offset=%" PRIu32 " count=%" PRIu32
                " produced=%" PRIu32 ", expected offset=%" PRIu32
                " count=%" PRIu32 "\n",
                label, result.valid_offset, result.valid_count, produced,
                expected_offset, expected_count);
        return 0;
    }
    return 1;
}

int main(void) {
    as_session_v0 session;
    memset(&session, 0, sizeof(session));

    /* Reproduces the reviewed invalid range exactly. */
    session.first_input_sample = 0;
    if (!expect(&session, -256, 160, 160, 0, 160, 160, 0,
                "empty-provider-range-before-content"))
        return 1;

    const uint32_t delays[] = {0, 1, 159, 160, 161, 256, 512};
    const int64_t origin = 123456;
    for (size_t i = 0; i < sizeof(delays) / sizeof(delays[0]); ++i) {
        const uint32_t delay = delays[i];
        session.first_input_sample = origin;
        const uint32_t offset = delay < 160 ? delay : 160;
        const uint32_t count = delay < 160 ? 160 - delay : 0;
        if (!expect(&session, origin - (int64_t)delay, 160, 0, 160,
                    origin + 160, offset, count, "delay-boundary"))
            return 1;
    }

    /* Every final-frame remainder, including every supported delay. */
    for (uint32_t remainder = 1; remainder < 160; ++remainder) {
        for (size_t i = 0; i < sizeof(delays) / sizeof(delays[0]); ++i) {
            const int64_t source = origin + 160 - (int64_t)delays[i];
            const int64_t local_start = source - origin;
            int64_t valid_begin = local_start < 0 ? 0 : local_start;
            int64_t valid_end = local_start + 160;
            const int64_t accepted_end = origin + 160 + remainder;
            if (valid_end > accepted_end - origin)
                valid_end = accepted_end - origin;
            if (valid_begin > 160) valid_begin = 160;
            uint32_t expected_offset =
                (uint32_t)(valid_begin > local_start
                               ? valid_begin - local_start
                               : 0);
            if (expected_offset > 160) expected_offset = 160;
            const uint32_t expected_count =
                valid_end > valid_begin
                    ? (uint32_t)(valid_end - valid_begin)
                    : 0;
            if (!expect(&session, source, 160, 0, 160, accepted_end,
                        expected_offset, expected_count,
                        "final-remainder"))
                return 1;
        }
    }

    /* Empty input and provider intervals outside the produced buffer. */
    session.first_input_sample = origin;
    if (!expect(&session, origin - 1, 160, 0, 160, origin, 1, 0,
                "empty-stream") ||
        !expect(&session, origin, 160, UINT32_MAX, UINT32_MAX, origin + 160,
                160, 0, "provider-range-overflow"))
        return 1;

    /* Saturation at signed-coordinate limits must not wrap into valid audio. */
    session.first_input_sample = INT64_MAX - 10;
    session.edge_start = 256;
    if (!expect(&session, INT64_MAX - 160, 160, 0, 160, INT64_MAX,
                160, 0, "content-start-overflow"))
        return 1;
    session.first_input_sample = INT64_MAX - 200;
    session.edge_start = 0;
    if (!expect(&session, INT64_MAX - 10, 160, 0, 160, INT64_MAX,
                0, 10, "output-end-overflow"))
        return 1;
    session.first_input_sample = 0;
    session.edge_end = 512;
    if (!expect(&session, INT64_MIN, 160, 0, 160, INT64_MIN,
                160, 0, "negative-end-underflow"))
        return 1;

    /* Public stats must count actual partial-frame padding, not full hops. */
    as_registry_v0 *registry = NULL;
    as_session_v0 *runtime = NULL;
    CHECK(test_open(&registry, &runtime, "dsp.highpass80.v0",
                    AS_MODE_PROCESSING_THREAD, 1, 0));
    float input[AS_FRAME_SAMPLES] = {0};
    float output_samples[AS_FRAME_SAMPLES] = {0};
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.input_valid_count = 1;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.epoch = 1;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = output_samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    CHECK(as_session_process_v0(runtime, &frame, &output, &result) == AS_OK);
    char stats[4096];
    uint32_t required = 0;
    CHECK(as_session_get_stats_v0(runtime, stats, sizeof(stats), &required) ==
          AS_OK);
    CHECK(strstr(stats, "\"final_padding_samples\":\"159\"") != NULL);
    CHECK(strstr(stats, "\"startup_padding_samples\":\"0\"") != NULL);
    CHECK(as_session_close_v0(&runtime) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);

    return 0;
}
