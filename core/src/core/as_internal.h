/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#ifndef AS_CORE_INTERNAL_H
#define AS_CORE_INTERNAL_H

#include "audio_sdk/provider_v0.h"
#include "audio_sdk/session_v0.h"
#include "core/json.h"
#include "core/sha256.h"

#include <pthread.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>

#define AS_REGISTRY_MAGIC 0x41535230u /* "ASR0" */
#define AS_SESSION_MAGIC 0x41535330u  /* "ASS0" */
#define AS_MAX_PROVIDERS 16u
#define AS_QUEUE_FRAMES 3u
#define AS_DRAIN_BOUND 1024u

enum as_lifecycle {
    AS_LIFE_PREPARED = 0,
    AS_LIFE_PROCESSING = 1,
    AS_LIFE_DRAINING = 2,
    AS_LIFE_DRAINED = 3,
    AS_LIFE_NEEDS_RESET = 4,
    AS_LIFE_CLOSED = 5
};

typedef struct as_provider_entry {
    char provider_id[AS_MAX_PROVIDER_ID];
    uint32_t provider_id_length;
    char *descriptor;
    uint32_t descriptor_length;
    uint8_t descriptor_digest[32];
    as_json_doc descriptor_doc;
    uint32_t descriptor_root;
    as_provider_table_v0 table;
    uint32_t buffering_delay;
    uint32_t native_hop;
    uint32_t max_drain_calls;
    uint32_t execution_modes; /* bit 1 << mode */
    int callback_safe;
} as_provider_entry;

struct as_registry_v0 {
    uint32_t magic;
    pthread_mutex_t lock;
    as_provider_entry providers[AS_MAX_PROVIDERS];
    uint32_t provider_count;
    int frozen;
    _Atomic uint32_t session_count;
};

typedef struct as_frame_slot {
    float samples[AS_FRAME_SAMPLES];
    uint32_t valid_count;
    uint32_t flags;
    uint64_t epoch;
    int64_t first_input_sample;
    int64_t accepted_end_after;
} as_frame_slot;

typedef struct as_output_slot {
    float samples[AS_FRAME_SAMPLES];
    as_result_v0 result;
} as_output_slot;

struct as_session_v0 {
    uint32_t magic;
    as_registry_v0 *registry;
    as_provider_entry *provider;
    as_provider_table_v0 table;
    void *instance;

    uint32_t execution_mode;
    uint32_t sample_rate_hz;
    uint32_t channels;
    uint32_t frame_samples;
    uint32_t buffering_delay;
    uint32_t max_drain_calls;
    uint32_t native_hop;
    uint32_t edge_start;
    uint32_t edge_end;

    uint64_t epoch;
    int64_t first_input_sample;
    int64_t next_input_sample;
    _Atomic int64_t accepted_end;
    int64_t next_output_sample;
    uint64_t accepted_valid;
    uint64_t submitted_valid;
    uint32_t drain_calls;

    char config_json[AS_MAX_CONTROL_BYTES];
    uint32_t config_json_length;
    uint8_t config_digest[32];
    uint8_t descriptor_digest[32];
    char provider_id[AS_MAX_PROVIDER_ID];
    uint32_t provider_id_length;

    /* owner-copied asset bytes (initial providers require none) */
    uint32_t asset_count;
    void *asset_data[AS_MAX_ASSETS];
    uint64_t asset_bytes[AS_MAX_ASSETS];
    char asset_ids[AS_MAX_ASSETS][64];

    pthread_mutex_t control_mutex;
    _Atomic int audio_guard;
    _Atomic int closing;
    _Atomic int reset_flag;
    int sync_ready;
    _Atomic uint32_t active_calls;
    _Atomic int lifecycle;

    /* buffered mode */
    pthread_mutex_t queue_mutex;
    pthread_cond_t queue_cond;
    pthread_t worker;
    int worker_started;
    int worker_stop;
    _Atomic int worker_failed;
    _Atomic int drain_complete;
    _Atomic int admission_closed;
    int manual_drain_requested;
    as_frame_slot input_queue[AS_QUEUE_FRAMES];
    _Atomic uint32_t input_read, input_write;
    as_output_slot output_queue[AS_QUEUE_FRAMES];
    _Atomic uint32_t output_read, output_write;
    _Atomic uint32_t input_high_water, output_high_water;

    _Atomic uint64_t c_submitted_valid;
    _Atomic uint64_t c_accepted_valid;
    _Atomic uint64_t c_rejected_valid;
    _Atomic uint64_t c_produced_valid;
    _Atomic uint64_t c_delivered_valid;
    _Atomic uint64_t c_startup_padding;
    _Atomic uint64_t c_final_padding;
    _Atomic uint64_t c_cancelled_intervals;
    _Atomic uint64_t c_cancelled_valid;
    _Atomic uint64_t c_failed_intervals;
    _Atomic uint64_t c_failed_valid;
    _Atomic uint64_t c_backend_failures;
    _Atomic uint64_t c_drain_frames;
};

/* ---- shared helpers ---------------------------------------------------- */

void as_error_set(as_error_v0 *error, as_status_v0 status, const char *field,
                  const char *message);
void as_error_clear(as_error_v0 *error);
int as_valid_struct(uint32_t struct_size, uint32_t major, uint32_t minor,
                    uint32_t known_size);
int as_tail_is_zero(const void *structure, uint32_t known_size,
                    uint32_t struct_size);
int as_valid_id(const char *text, uint32_t length);
int as_text_equal(const char *text, uint32_t length, const char *expected);
void as_hex(const uint8_t digest[32], char out[65]);
int as_status_valid(as_status_v0 status);

/* Provider registration used by the built-in install path. */
as_status_v0 as_registry_register_builtin_v0(as_registry_v0 *registry,
                                             const as_provider_table_v0 *table,
                                             const char *descriptor,
                                             uint32_t descriptor_length,
                                             as_error_v0 *error);

as_provider_entry *as_registry_lookup(as_registry_v0 *registry,
                                      const char *provider_id,
                                      uint32_t provider_id_length);

/* Descriptor parsing/validation against the closed v0 schema. */
as_status_v0 as_descriptor_validate(char *bytes, uint32_t length,
                                    as_provider_entry *entry,
                                    as_error_v0 *error);

/* Effective configuration parsing: canonical + semantic validation. */
as_status_v0 as_effective_config_validate(as_session_v0 *session,
                                          const char *bytes, uint32_t length,
                                          as_error_v0 *error);

/* Worker thread. */
void *as_worker_main(void *argument);
as_status_v0 as_worker_start(as_session_v0 *session, as_error_v0 *error);
as_status_v0 as_worker_stop(as_session_v0 *session);

/* Drain helpers shared by inline and buffered paths. */
as_status_v0 as_drain_provider_frame(as_session_v0 *session,
                                     const as_output_v0 *output,
                                     as_result_v0 *result);

/* Session-facing provider call wrappers (validated metadata). */
as_status_v0 as_provider_process_frame(as_session_v0 *session,
                                       const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result);

/* Validity intersection against accepted content (half-open source range). */
void as_compute_validity(const as_session_v0 *session, int64_t source_first,
                         uint32_t produced, uint32_t provider_offset,
                         uint32_t provider_count, int64_t accepted_end,
                         uint32_t final_flags, as_result_v0 *result);
void as_compute_padding_counts(const as_session_v0 *session,
                               int64_t source_first, uint32_t produced,
                               int64_t accepted_end, int final,
                               uint32_t *startup_count,
                               uint32_t *final_count);

/* Built-in tables/descriptors. */
const as_provider_table_v0 *as_speex_provider_table(void);
const as_provider_table_v0 *as_highpass_provider_table(void);
extern const char as_speex_descriptor[];
extern const uint32_t as_speex_descriptor_length;
extern const char as_highpass_descriptor[];
extern const uint32_t as_highpass_descriptor_length;
extern const char as_build_identity[];

#endif
