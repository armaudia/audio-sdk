/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef AUDIO_SDK_SIXBAND_PROVIDER_H
#define AUDIO_SDK_SIXBAND_PROVIDER_H

#include "audio_sdk/session_v0.h"

/* Task-local optional reference provider. Not installed or registered by the
 * SDK; a caller links this source into its own consumer and registers it
 * explicitly on a registry it owns. */
as_status_v0 sixband_register(as_registry_v0 *registry, as_error_v0 *error);
/* Test-only boundary: register the same table with caller-supplied descriptor
 * bytes so invalid-descriptor admission can be exercised. */
as_status_v0 sixband_register_descriptor(as_registry_v0 *registry,
                                         const char *descriptor, uint32_t length,
                                         as_error_v0 *error);

#endif /* AUDIO_SDK_SIXBAND_PROVIDER_H */
