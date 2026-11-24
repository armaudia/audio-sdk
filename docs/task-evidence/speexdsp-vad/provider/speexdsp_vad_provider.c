/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered SpeexDSP VAD reference on the public v0 provider
 * table. It links the vendored Xiph SpeexDSP 7a158783 preprocessing library,
 * enables only its VAD (denoise, AGC and dereverb stay disabled), passes audio
 * through unchanged and exposes the binary decision as a task-local advisory
 * observation. The decision is not part of the v0 ABI and never gates audio.
 *
 * This source is NOT compiled, linked, installed or registered by the SDK by
 * default. The historical public adapter uses 320-sample int16 frames; v0 is
 * fixed at 160 f32 samples, so no numeric parity is claimed.
 */
#include "audio_sdk/session_v0.h"
#include "speex/speex_preprocess.h"
#include "speexdsp_vad_descriptor.h"
#include "speexdsp_vad_observe.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define VAD_MAX_ABS_SAMPLE (4.0f)
#define VAD_FRAME_SAMPLES ((int)AS_FRAME_SAMPLES)

typedef struct speexdsp_vad_s {
    SpeexPreprocessState *state;
    uint64_t epoch;
    int64_t expected_start;
    int have_position;
    uint64_t frame_count;
    uint64_t decision_calls;
    uint32_t pcm16_clipped_samples;
    int last_vad;
} speexdsp_vad;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void destroy_state(speexdsp_vad *instance) {
    if (instance != NULL && instance->state != NULL) {
        speex_preprocess_state_destroy(instance->state);
        instance->state = NULL;
    }
}

static as_status_v0 create_state(speexdsp_vad *instance) {
    int enabled = 1;
    int disabled = 0;
    instance->state = speex_preprocess_state_init(VAD_FRAME_SAMPLES, (int)AS_SAMPLE_RATE_HZ);
    if (instance->state == NULL) return AS_RESOURCE_EXHAUSTED;
    if (speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_DENOISE, &disabled) != 0 ||
        speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_AGC, &disabled) != 0 ||
        speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_DEREVERB, &disabled) != 0 ||
        speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_VAD, &enabled) != 0) {
        destroy_state(instance);
        return AS_BACKEND_FAILURE;
    }
    return AS_OK;
}

static as_status_v0 AS_CALL vad_create(const as_create_config_v0 *config,
                                       void **out_instance,
                                       as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) {
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 0 || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        SPEEXDSP_VAD_PROVIDER_ID,
                        strlen(SPEEXDSP_VAD_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    speexdsp_vad *instance = (speexdsp_vad *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    as_status_v0 status = create_state(instance);
    if (status != AS_OK) {
        free(instance);
        return status;
    }
    instance->epoch = config->epoch;
    instance->expected_start = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL vad_process(void *opaque,
                                        const as_frame_v0 *frame,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    speexdsp_vad *instance = (speexdsp_vad *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL ||
        instance->state == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    const uint32_t count = frame->input_valid_count;
    if (frame->input_count != AS_FRAME_SAMPLES || count == 0 ||
        count > AS_FRAME_SAMPLES || (count < AS_FRAME_SAMPLES && !final)) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < count; ++index) {
        const float sample = frame->input[index];
        if (!isfinite(sample) || sample > VAD_MAX_ABS_SAMPLE ||
            sample < -VAD_MAX_ABS_SAMPLE) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch) return AS_INVALID_ARGUMENT;
    if (!instance->have_position) {
        instance->expected_start = frame->first_input_sample;
        instance->have_position = 1;
    }
    if (frame->first_input_sample != instance->expected_start) {
        return AS_BACKEND_FAILURE;
    }

    spx_int16_t pcm[AS_FRAME_SAMPLES];
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const float sample = index < count ? frame->input[index] : 0.0f;
        const double scaled = (double)sample * 32767.0;
        if (round(scaled) < -32768.0 || round(scaled) > 32767.0) {
            ++instance->pcm16_clipped_samples;
        }
        const double clipped = scaled < -32768.0 ? -32768.0 :
                               scaled > 32767.0 ? 32767.0 : scaled;
        pcm[index] = (spx_int16_t)round(clipped);
    }

    (void)speex_preprocess_run(instance->state, pcm);
    int vad = 0;
    if (speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_GET_VAD, &vad) != 0) {
        return AS_BACKEND_FAILURE;
    }
    instance->last_vad = vad != 0 ? 1 : 0;
    ++instance->frame_count;
    ++instance->decision_calls;

    for (uint32_t index = 0; index < count; ++index) {
        output->samples[index] = frame->input[index];
    }
    for (uint32_t index = count; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = 0.0f;
    }
    instance->expected_start = frame->first_input_sample + (int64_t)count;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = count;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL vad_reset(void *opaque, uint64_t epoch,
                                      int64_t first_input_sample,
                                      as_error_v0 *error) {
    (void)error;
    speexdsp_vad *instance = (speexdsp_vad *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    destroy_state(instance);
    as_status_v0 status = create_state(instance);
    if (status != AS_OK) return status;
    instance->epoch = epoch;
    instance->expected_start = first_input_sample;
    instance->have_position = 1;
    instance->frame_count = 0;
    instance->decision_calls = 0;
    instance->pcm16_clipped_samples = 0;
    instance->last_vad = 0;
    return AS_OK;
}

static as_status_v0 AS_CALL vad_drain(void *opaque,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    speexdsp_vad *instance = (speexdsp_vad *)opaque;
    (void)output;
    if (instance == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->expected_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL vad_destroy(void *opaque) {
    speexdsp_vad *instance = (speexdsp_vad *)opaque;
    if (instance == NULL) return;
    destroy_state(instance);
    free(instance);
}

as_status_v0 speexdsp_vad_register(as_registry_v0 *registry,
                                   as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        vad_create, vad_process, vad_reset, vad_drain, vad_destroy,
        {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}

as_status_v0 as_speexdsp_vad_test_create(const as_create_config_v0 *config,
                                         void **out_instance,
                                         as_error_v0 *error) {
    return vad_create(config, out_instance, error);
}

as_status_v0 as_speexdsp_vad_test_process(void *instance,
                                          const as_frame_v0 *frame,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    return vad_process(instance, frame, output, result);
}

as_status_v0 as_speexdsp_vad_observe(void *instance,
                                     as_speexdsp_vad_observe_v0 *out) {
    speexdsp_vad *state = (speexdsp_vad *)instance;
    if (state == NULL || out == NULL) return AS_INVALID_ARGUMENT;
    out->frame_count = state->frame_count;
    out->decision_calls = state->decision_calls;
    out->pcm16_clipped_samples = state->pcm16_clipped_samples;
    out->last_vad = state->last_vad;
    return AS_OK;
}

void as_speexdsp_vad_test_destroy(void *instance) { vad_destroy(instance); }
