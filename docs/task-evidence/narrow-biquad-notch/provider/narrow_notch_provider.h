/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef AUDIO_SDK_TASK_NARROW_NOTCH_PROVIDER_H
#define AUDIO_SDK_TASK_NARROW_NOTCH_PROVIDER_H

#include "audio_sdk/session_v0.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Task-local helper: register one optional notch provider on a caller registry.
 *
 * The centre frequency and bandwidth are explicit integer Hz values. They are
 * encoded into a caller-local provider ID (`dsp.narrow-notch-<f0>-<bw>.v0`),
 * which lets the public session facade's canonical effective-config helper
 * carry the selection without changing the frozen settings schema. This is
 * not an installed provider, descriptor, registry default or public API.
 */
as_status_v0 narrow_notch_register_v0(as_registry_v0 *registry,
                                      double frequency_hz,
                                      double bandwidth_hz,
                                      char *provider_id_out,
                                      uint32_t provider_id_capacity,
                                      as_error_v0 *error);

#define NN_EXPECTED_ID_1000_100 "dsp.narrow-notch-1000-100.v0"
#define NN_EXPECTED_ID_120_12 "dsp.narrow-notch-120-12.v0"

#ifdef __cplusplus
}
#endif

#endif
