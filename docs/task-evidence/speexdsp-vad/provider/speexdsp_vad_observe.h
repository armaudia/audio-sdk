/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Task-local observation surface. Not public SDK API and not v0 ABI. */
#ifndef AUDIO_SDK_SPEEXDSP_VAD_OBSERVE_H
#define AUDIO_SDK_SPEEXDSP_VAD_OBSERVE_H

#include "audio_sdk/provider_v0.h"

typedef struct as_speexdsp_vad_observe_v0 {
    uint64_t frame_count;
    uint64_t decision_calls;
    uint32_t pcm16_clipped_samples;
    int last_vad;
} as_speexdsp_vad_observe_v0;

/* Direct, task-local instance access for advisory-decision observation. */
as_status_v0 as_speexdsp_vad_test_create(const as_create_config_v0 *config,
                                         void **out_instance, as_error_v0 *error);
as_status_v0 as_speexdsp_vad_test_process(void *instance,
                                          const as_frame_v0 *frame,
                                          const as_output_v0 *output,
                                          as_result_v0 *result);
as_status_v0 as_speexdsp_vad_observe(void *instance,
                                     as_speexdsp_vad_observe_v0 *out);
void as_speexdsp_vad_test_destroy(void *instance);

#endif /* AUDIO_SDK_SPEEXDSP_VAD_OBSERVE_H */
