/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef AUDIO_SDK_RLS_AEC_PROVIDER_H
#define AUDIO_SDK_RLS_AEC_PROVIDER_H

#include "audio_sdk/session_v0.h"

/* Task-local direct-instance helpers for paired-reference parity tests.
 * They wrap this optional provider's own callbacks; they do not alter v0. */
as_status_v0 rls_aec_instance_create(const as_create_config_v0 *config,
                                    void **out_instance, as_error_v0 *error);
as_status_v0 rls_aec_instance_process(void *instance, const as_frame_v0 *frame,
                                     const as_output_v0 *output,
                                     as_result_v0 *result);
as_status_v0 rls_aec_instance_reset(void *instance, uint64_t epoch,
                                   int64_t first_input_sample,
                                   as_error_v0 *error);
void rls_aec_instance_destroy(void *instance);

/* Task-local sidechain helper.  It is NOT part of the public SDK API/ABI:
 * only this optional provider source declares or implements it.  The render
 * reference must be supplied explicitly before each paired process call.
 * With no reference the microphone is passed through and no state adapts. */
as_status_v0 rls_aec_feed_reference(void *instance, const float *reference,
                                    uint32_t count, as_error_v0 *error);

/* Read-only counters.  Phase 0 = adapting RLS, 1 = frozen after a safety guard.
 * A safety freeze is a non-qualifying event before promotion. */
as_status_v0 rls_aec_snapshot(void *instance, uint64_t *frames,
                             uint64_t *adapted_frames,
                             uint64_t *double_talk_frames,
                             uint64_t *no_reference_frames,
                             uint64_t *invalid_count,
                             uint64_t *safety_freezes,
                             uint64_t *skipped_updates,
                             double *weight_l1, double *max_matrix_abs,
                             uint32_t *phase);
/* Returns "none", "nonfinite_state" or "boundedness_violation"; never NULL. */
const char *rls_aec_safety_reason(void *instance);

/* Task-local test hook: corrupt one weight to verify the finite-state guard.
 * It is not part of the SDK API and exists only in this optional source. */
as_status_v0 rls_aec_inject_nonfinite_state_for_test(void *instance);

as_status_v0 rls_aec_register(as_registry_v0 *registry, as_error_v0 *error);

#endif
