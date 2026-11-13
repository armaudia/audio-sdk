/*
 * audio-sdk session facade v0 — public C contract.
 *
 * Contract revision 0.1. Fixed v0 format: mono float32, 16 000 Hz,
 * exactly 160 samples per call. One provider, one sequential engine.
 *
 * Lifecycle: prepared -> processing -> draining -> drained.
 * Backend failure enters needs_reset. Reset is quiesced control work.
 * Buffered mode owns one input and one output SPSC queue (3 frames each) and
 * one worker. Inline modes create no threads.
 */
#ifndef AUDIO_SDK_SESSION_V0_H
#define AUDIO_SDK_SESSION_V0_H

#include "audio_sdk/provider_v0.h"

#if defined(__cplusplus)
extern "C" {
#endif

/* Build identity for load-time validation by bindings and consumers. */
AS_API const char *AS_CALL as_contract_version_v0(void);
AS_API const char *AS_CALL as_build_id_v0(void);

AS_API as_status_v0 AS_CALL as_session_create_v0(
    as_registry_v0 *registry, const char *provider_id,
    uint32_t provider_id_length, const as_create_config_v0 *config,
    as_session_v0 **out, as_error_v0 *error);

AS_API as_status_v0 AS_CALL as_session_process_v0(
    as_session_v0 *session, const as_frame_v0 *frame,
    const as_output_v0 *output, as_result_v0 *result);

AS_API as_status_v0 AS_CALL as_session_submit_v0(
    as_session_v0 *session, const as_frame_v0 *frame,
    as_result_v0 *acceptance);

AS_API as_status_v0 AS_CALL as_session_pull_v0(
    as_session_v0 *session, const as_output_v0 *output,
    as_result_v0 *result);

AS_API as_status_v0 AS_CALL as_session_begin_drain_v0(as_session_v0 *session);

AS_API as_status_v0 AS_CALL as_session_drain_next_v0(
    as_session_v0 *session, const as_output_v0 *output,
    as_result_v0 *result);

AS_API as_status_v0 AS_CALL as_session_reset_v0(
    as_session_v0 *session, uint64_t epoch, int64_t first_input_sample,
    as_error_v0 *error);

/* Caller-buffer JSON. required_size includes the NUL terminator. */
AS_API as_status_v0 AS_CALL as_session_get_info_v0(
    as_session_v0 *session, char *buffer, uint32_t capacity,
    uint32_t *required_size);

AS_API as_status_v0 AS_CALL as_session_get_stats_v0(
    as_session_v0 *session, char *buffer, uint32_t capacity,
    uint32_t *required_size);

/* Null-safe: *session is set to NULL on success and may already be NULL. */
AS_API as_status_v0 AS_CALL as_session_close_v0(as_session_v0 **session);

/* Control helper: builds the canonical effective-configuration bytes for a
 * registered provider and the supplied format/mode. This removes the need
 * for callers to reproduce the restricted canonical JSON encoding. */
AS_API as_status_v0 AS_CALL as_effective_config_create_v0(
    as_registry_v0 *registry, const char *provider_id,
    uint32_t provider_id_length, uint32_t execution_mode, char *buffer,
    uint32_t capacity, uint32_t *required_size, as_error_v0 *error);

/* SHA-256 of the descriptor bytes, lowercase hex, NUL-terminated (65 bytes). */
AS_API as_status_v0 AS_CALL as_provider_digest_v0(
    as_registry_v0 *registry, const char *provider_id,
    uint32_t provider_id_length, char *hex_out, uint32_t capacity);

#if defined(__cplusplus)
} /* extern "C" */
#endif

#endif /* AUDIO_SDK_SESSION_V0_H */
