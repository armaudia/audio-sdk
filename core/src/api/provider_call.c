/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "core/as_internal.h"

#include <math.h>
#include <limits.h>
#include <string.h>

static void zero_output(const as_output_v0 *output) {
    if (output != NULL && output->samples != NULL) {
        memset(output->samples, 0, AS_FRAME_SAMPLES * sizeof(float));
    }
}

static int result_header_ok(const as_result_v0 *result) {
    if (result == NULL ||
        !as_valid_struct(result->struct_size, result->abi_major,
                         result->abi_minor, (uint32_t)sizeof(*result)) ||
        !as_tail_is_zero(result, (uint32_t)sizeof(*result),
                         result->struct_size))
        return 0;
    return result->reserved[0] == 0 && result->reserved[1] == 0 &&
           result->reserved[2] == 0;
}

static int samples_finite(const float *samples, uint32_t count) {
    for (uint32_t i = 0; i < count; ++i) {
        if (!isfinite(samples[i])) return 0;
    }
    return 1;
}

static as_status_v0 provider_failure(as_session_v0 *session,
                                     const as_output_v0 *output,
                                     as_result_v0 *result, as_status_v0 status,
                                     const char *message) {
    atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
    atomic_fetch_add(&session->c_backend_failures, 1u);
    zero_output(output);
    as_result_v0_init(result);
    result->status = status;
    result->epoch = session->epoch;
    (void)message;
    return status;
}

as_status_v0 as_provider_process_frame(as_session_v0 *session,
                                       const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result) {
    as_result_v0 provider_result;
    as_result_v0_init(&provider_result);
    const as_status_v0 status = session->table.process(
        session->instance, frame, output, &provider_result);
    if (status != AS_OK) {
        const as_status_v0 mapped = status == AS_BACKEND_FAILURE ||
                                            status == AS_NEEDS_RESET ||
                                            status == AS_RESOURCE_EXHAUSTED
                                        ? status
                                        : AS_BACKEND_FAILURE;
        return provider_failure(session, output, result, mapped,
                                "provider process failed");
    }
    const int64_t expected_source =
        frame->first_input_sample - (int64_t)session->buffering_delay;
    const int counts_valid =
        result_header_ok(&provider_result) &&
        provider_result.consumed_count == AS_FRAME_SAMPLES &&
        provider_result.produced_count == AS_FRAME_SAMPLES &&
        provider_result.valid_offset <= provider_result.produced_count &&
        provider_result.valid_count <=
            provider_result.produced_count - provider_result.valid_offset &&
        provider_result.source_first_sample == expected_source &&
        provider_result.epoch == frame->epoch;
    if (!counts_valid ||
        !samples_finite(output->samples, provider_result.produced_count)) {
        return provider_failure(session, output, result, AS_BACKEND_FAILURE,
                                "provider returned inconsistent process metadata");
    }
    if (provider_result.source_first_sample >
        INT64_MAX - (int64_t)provider_result.produced_count) {
        return provider_failure(session, output, result, AS_BACKEND_FAILURE,
                                "provider output interval overflows int64");
    }
    *result = provider_result;
    return AS_OK;
}

as_status_v0 as_drain_provider_frame(as_session_v0 *session,
                                     const as_output_v0 *output,
                                     as_result_v0 *result) {
    as_result_v0 provider_result;
    as_result_v0_init(&provider_result);
    const as_status_v0 status = session->table.drain(session->instance, output,
                                                     &provider_result);
    if (status == AS_END_OF_STREAM) {
        as_result_v0_init(result);
        result->status = AS_END_OF_STREAM;
        result->epoch = session->epoch;
        result->source_first_sample = session->next_output_sample;
        return AS_END_OF_STREAM;
    }
    if (status != AS_OK) {
        return provider_failure(session, output, result,
                                status == AS_BACKEND_FAILURE ? AS_BACKEND_FAILURE
                                                             : AS_BACKEND_FAILURE,
                                "provider drain failed");
    }
    const int counts_valid =
        result_header_ok(&provider_result) &&
        provider_result.consumed_count == 0 &&
        provider_result.produced_count <= AS_FRAME_SAMPLES &&
        provider_result.valid_offset <= provider_result.produced_count &&
        provider_result.valid_count <=
            provider_result.produced_count - provider_result.valid_offset &&
        provider_result.epoch == session->epoch &&
        provider_result.source_first_sample == session->next_output_sample;
    if (!counts_valid ||
        !samples_finite(output->samples, provider_result.produced_count)) {
        return provider_failure(session, output, result, AS_BACKEND_FAILURE,
                                "provider returned inconsistent drain metadata");
    }
    session->next_output_sample =
        provider_result.source_first_sample + (int64_t)provider_result.produced_count;
    *result = provider_result;
    return AS_OK;
}
