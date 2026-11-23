/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef AUDIO_SDK_NLMS_AEC_PROVIDER_H
#define AUDIO_SDK_NLMS_AEC_PROVIDER_H

#include "audio_sdk/session_v0.h"

/* Task-local direct-instance helpers for paired-reference parity tests.
 * They wrap this provider's own table callbacks; they do not alter v0. */
as_status_v0 nlms_aec_instance_create(const as_create_config_v0 *config,
                                      void **out_instance, as_error_v0 *error);
as_status_v0 nlms_aec_instance_process(void *instance, const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result);
as_status_v0 nlms_aec_instance_reset(void *instance, uint64_t epoch,
                                     int64_t first_input_sample,
                                     as_error_v0 *error);
void nlms_aec_instance_destroy(void *instance);

/* Task-local sidechain helper.  It is NOT part of the public SDK API/ABI:
 * only this optional provider source declares or implements it.  The render
 * reference must be supplied explicitly before each paired process call.
 * Failure to do so is a safe microphone passthrough with no adaptation. */
as_status_v0 nlms_aec_feed_reference(void *instance, const float *reference,
                                     uint32_t count, as_error_v0 *error);

/* Read-only counters for deterministic boundary tests. */
as_status_v0 nlms_aec_snapshot(void *instance, uint64_t *frames,
                               uint64_t *adapted_frames,
                               uint64_t *double_talk_frames,
                               uint64_t *no_reference_frames,
                               uint64_t *invalid_count, double *weight_l1);

as_status_v0 nlms_aec_register(as_registry_v0 *registry, as_error_v0 *error);

#endif
