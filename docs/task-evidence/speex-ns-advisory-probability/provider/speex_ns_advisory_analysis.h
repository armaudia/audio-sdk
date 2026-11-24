/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Task-local analysis side channel. Never installed or declared in a public
 * SDK header. The side output is evidence only and is not a control signal. */
#ifndef SPEEX_NS_ADVISORY_ANALYSIS_H
#define SPEEX_NS_ADVISORY_ANALYSIS_H

#include "audio_sdk/provider_v0.h"

#define AS_SPEEX_NS_ADVISORY_PROVIDER_ID "analysis.speex-ns-advisory-reference.v0"
#define AS_SPEEX_NS_ADVISORY_WINDOW_SAMPLES 320u
#define AS_SPEEX_NS_ADVISORY_MILLI_MAX 1000u
#define AS_SPEEX_NS_ADVISORY_HOP_INPUT 0u
#define AS_SPEEX_NS_ADVISORY_HOP_OUTPUT 1u
#define AS_SPEEX_NS_ADVISORY_VALIDITY_KNOWN 1u
#define AS_SPEEX_NS_ADVISORY_VALIDITY_INVALID 0u

typedef struct as_speex_ns_advisory_event_v0 {
    uint32_t schema_version;
    uint32_t sequence;
    uint32_t hop;
    uint32_t value_milli;
    uint32_t validity;
    uint32_t reserved;
    uint64_t epoch;
    int64_t source_first_sample;
    int64_t source_end_sample;
    int64_t available_monotonic_ns;
    char config_digest[65];
} as_speex_ns_advisory_event_v0;

/* All functions are compiled only into the opt-in consumer. */
const as_provider_table_v0 *as_speex_ns_advisory_table_v0(void);
as_status_v0 as_speex_ns_advisory_register_v0(as_registry_v0 *registry,
                                              as_error_v0 *error);
uint32_t as_speex_ns_advisory_event_count_v0(const void *instance, uint32_t hop);
as_status_v0 as_speex_ns_advisory_event_at_v0(const void *instance, uint32_t hop,
                                              uint32_t index,
                                              as_speex_ns_advisory_event_v0 *out);
uint32_t as_speex_ns_advisory_invalid_count_v0(const void *instance);

#endif /* SPEEX_NS_ADVISORY_ANALYSIS_H */
