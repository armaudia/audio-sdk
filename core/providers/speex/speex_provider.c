/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
/*
 * SpeexDSP noise-suppression provider for the v0 table.
 *
 * Policy (frozen for this provider ID):
 *  - denoise on, AGC off, dereverb off, Speex VAD computed but not exported;
 *  - fixed settings: suppression -20 dB, VAD start 35, continue 20;
 *  - every accepted frame executes the same path (no quiet-frame shortcut);
 *  - float -> PCM16 uses lrint(clamp(x, -1, 1) * 32767) under FE_TONEAREST,
 *    and PCM16 -> float divides by 32768; this is declared quantization;
 *  - the WOLA filterbank buffers one 160-sample frame, so the content
 *    buffering delay D is 160 samples (verified by the isolated timing
 *    fixture; the legacy adapter declared 0 and was wrong).
 */
#include "audio_sdk/provider_v0.h"

#include <fenv.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <speex/speex_preprocess.h>

#define SPEEX_DELAY_SAMPLES 160

typedef struct speex_instance {
    SpeexPreprocessState *state;
    int16_t pcm[AS_FRAME_SAMPLES];
    int64_t output_start;
    int64_t accepted_end;
    uint64_t epoch;
    int have_position;
} speex_instance;

static int16_t clamp_to_pcm16(float value) {
    if (value > 1.0f) value = 1.0f;
    if (value < -1.0f) value = -1.0f;
    return (int16_t)lrintf(value * 32767.0f);
}

static int init_state(speex_instance *instance) {
    if (instance->state != NULL) speex_preprocess_state_destroy(instance->state);
    instance->state = speex_preprocess_state_init(AS_FRAME_SAMPLES, 16000);
    if (instance->state == NULL) return 0;
    int one = 1;
    int zero = 0;
    int suppression = -20;
    int start = 35;
    int cont = 20;
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_DENOISE, &one);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_AGC, &zero);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_DEREVERB, &zero);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_VAD, &one);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_NOISE_SUPPRESS,
                         &suppression);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_PROB_START, &start);
    speex_preprocess_ctl(instance->state, SPEEX_PREPROCESS_SET_PROB_CONTINUE, &cont);
    return 1;
}

static as_status_v0 AS_CALL speex_create(const as_create_config_v0 *config,
                                         void **out_instance,
                                         as_error_v0 *error) {
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES ||
        config->execution_mode < AS_MODE_INLINE_CALLBACK ||
        config->execution_mode > AS_MODE_BUFFERED_WORKER) {
        return AS_UNSUPPORTED;
    }
    speex_instance *instance = (speex_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->output_start = 0;
    instance->accepted_end = 0;
    instance->epoch = config->epoch;
    instance->have_position = 0;
    if (!init_state(instance)) {
        free(instance);
        if (error != NULL) {
            error->status = AS_BACKEND_FAILURE;
            strncpy(error->message, "SpeexDSP state initialization failed",
                    sizeof(error->message) - 1u);
        }
        return AS_BACKEND_FAILURE;
    }
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL speex_process(void *opaque, const as_frame_v0 *frame,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    speex_instance *instance = (speex_instance *)opaque;
    if (instance == NULL || instance->state == NULL || frame == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL ||
        frame->input == NULL || frame->input_count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    if (fegetround() != FE_TONEAREST) return AS_BACKEND_FAILURE;
    const int64_t source_first =
        frame->first_input_sample - (int64_t)SPEEX_DELAY_SAMPLES;
    if (!instance->have_position) {
        instance->output_start = source_first;
        instance->have_position = 1;
    }
    if (instance->output_start != source_first) return AS_BACKEND_FAILURE;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i)
        instance->pcm[i] = clamp_to_pcm16(frame->input[i]);
    const int speech = speex_preprocess_run(instance->state, instance->pcm);
    (void)speech;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i)
        output->samples[i] = (float)instance->pcm[i] / 32768.0f;
    instance->accepted_end =
        frame->first_input_sample +
        (int64_t)((frame->flags & AS_FRAME_FINAL_INPUT)
                      ? frame->input_valid_count
                      : AS_FRAME_SAMPLES);
    instance->output_start += AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = source_first;
    return AS_OK;
}

static as_status_v0 AS_CALL speex_reset(void *opaque, uint64_t epoch,
                                        int64_t first_input_sample,
                                        as_error_v0 *error) {
    speex_instance *instance = (speex_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    if (!init_state(instance)) {
        if (error != NULL) {
            error->status = AS_BACKEND_FAILURE;
            strncpy(error->message, "SpeexDSP reset initialization failed",
                    sizeof(error->message) - 1u);
        }
        return AS_BACKEND_FAILURE;
    }
    instance->output_start = first_input_sample - (int64_t)SPEEX_DELAY_SAMPLES;
    instance->accepted_end = first_input_sample;
    instance->epoch = epoch;
    instance->have_position = 0;
    return AS_OK;
}

static as_status_v0 AS_CALL speex_drain(void *opaque, const as_output_v0 *output,
                                        as_result_v0 *result) {
    speex_instance *instance = (speex_instance *)opaque;
    if (instance == NULL || instance->state == NULL || output == NULL ||
        output->samples == NULL || output->capacity < AS_FRAME_SAMPLES ||
        result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (instance->output_start >= instance->accepted_end) return AS_END_OF_STREAM;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) instance->pcm[i] = 0;
    speex_preprocess_run(instance->state, instance->pcm);
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i)
        output->samples[i] = (float)instance->pcm[i] / 32768.0f;
    int64_t remaining = instance->accepted_end - instance->output_start;
    uint32_t valid = remaining >= (int64_t)AS_FRAME_SAMPLES
                         ? AS_FRAME_SAMPLES
                         : (uint32_t)remaining;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = 0;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = valid;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    instance->output_start += AS_FRAME_SAMPLES;
    return AS_OK;
}

static void AS_CALL speex_destroy(void *opaque) {
    speex_instance *instance = (speex_instance *)opaque;
    if (instance == NULL) return;
    if (instance->state != NULL) speex_preprocess_state_destroy(instance->state);
    free(instance);
}

static const as_provider_table_v0 kSpeexTable = {
    (uint32_t)sizeof(as_provider_table_v0),
    AS_ABI_MAJOR,
    AS_ABI_MINOR,
    speex_create,
    speex_process,
    speex_reset,
    speex_drain,
    speex_destroy,
    {0, 0, 0, 0}};

const as_provider_table_v0 *as_speex_provider_table(void) {
    return &kSpeexTable;
}
