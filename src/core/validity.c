#include "core/as_internal.h"

#include <limits.h>

static int64_t add_u32_saturating(int64_t value, uint32_t amount) {
    if (value > INT64_MAX - (int64_t)amount) return INT64_MAX;
    return value + (int64_t)amount;
}

static int64_t subtract_u32_saturating(int64_t value, uint32_t amount) {
    if (value < INT64_MIN + (int64_t)amount) return INT64_MIN;
    return value - (int64_t)amount;
}

/* Return the coordinate's position relative to source_first, clipped to output. */
static uint32_t local_offset(int64_t coordinate, int64_t source_first,
                             uint32_t produced) {
    if (coordinate <= source_first) return 0;
    const uint64_t distance =
        (uint64_t)coordinate - (uint64_t)source_first;
    return distance >= produced ? produced : (uint32_t)distance;
}

void as_compute_padding_counts(const as_session_v0 *session,
                               int64_t source_first, uint32_t produced,
                               int64_t accepted_end, int final,
                               uint32_t *startup_count,
                               uint32_t *final_count) {
    const int64_t content_start =
        add_u32_saturating(session->first_input_sample, session->edge_start);
    int64_t content_end =
        subtract_u32_saturating(accepted_end, session->edge_end);
    if (content_end < content_start) content_end = content_start;
    if (startup_count != NULL)
        *startup_count = local_offset(content_start, source_first, produced);
    if (final_count != NULL) {
        *final_count = final
                           ? produced -
                                 local_offset(content_end, source_first,
                                              produced)
                           : 0u;
    }
}

void as_compute_validity(const as_session_v0 *session, int64_t source_first,
                         uint32_t produced, uint32_t provider_offset,
                         uint32_t provider_count, int64_t accepted_end,
                         uint32_t final_flags, as_result_v0 *result) {
    if (result == NULL) return;
    const int64_t content_start =
        add_u32_saturating(session->first_input_sample, session->edge_start);
    int64_t content_end =
        subtract_u32_saturating(accepted_end, session->edge_end);
    if (content_end < content_start) content_end = content_start;

    uint32_t provider_begin = provider_offset < produced
                                  ? provider_offset
                                  : produced;
    const uint64_t provider_end_wide =
        (uint64_t)provider_offset + (uint64_t)provider_count;
    uint32_t provider_end = provider_end_wide < produced
                                ? (uint32_t)provider_end_wide
                                : produced;
    if (provider_end < provider_begin) provider_end = provider_begin;

    const uint32_t content_begin =
        local_offset(content_start, source_first, produced);
    const uint32_t content_limit =
        local_offset(content_end, source_first, produced);
    uint32_t begin = provider_begin > content_begin
                         ? provider_begin
                         : content_begin;
    uint32_t end = provider_end < content_limit
                       ? provider_end
                       : content_limit;
    if (end < begin) end = begin;

    result->valid_offset = begin;
    result->valid_count = end - begin;
    result->produced_count = produced;
    result->flags = 0;
    if (source_first < content_start) result->flags |= AS_RESULT_STARTUP_PADDING;
    if ((final_flags & AS_RESULT_FINAL_PADDING) != 0 &&
        content_limit < produced) {
        result->flags |= AS_RESULT_FINAL_PADDING;
    }
}
