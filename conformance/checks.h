/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef AS_CONFORMANCE_CHECKS_H
#define AS_CONFORMANCE_CHECKS_H

#include <stdint.h>

#include "audio_sdk/session_v0.h"

#if defined(__cplusplus)
extern "C" {
#endif

/* Runs the standalone conformance checks for one registered provider.
 * Returns 0 when every required check passed, 1 on a conformance failure and
 * 2 for an invalid environment/invocation. The JSON report is written when
 * report_path is non-NULL. */
int as_run_conformance(as_registry_v0 *registry, const char *provider_id,
                       uint32_t provider_id_length, const char *report_path,
                       char *error, uint32_t error_capacity);

#if defined(__cplusplus)
}
#endif

#endif
