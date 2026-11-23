/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered NLMS acoustic echo cancellation reference.
 *
 * Task-local source only.  It uses the public v0 provider/session headers for
 * the engine boundary and a task-local sidechain helper for the explicit
 * playback/render reference, because v0 frames carry a single mono stream.
 * No installed registry, public API, descriptor or default is changed.  The
 * constants and sample order mirror docs/task-evidence/nlms-aec/reference.py.
 */
#include "audio_sdk/session_v0.h"
#include "nlms_aec_provider.h"
#include "nlms_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define NLMS_TAPS 96u
#define NLMS_STEP 0.25
#define NLMS_EPSILON 1e-8
#define NLMS_MAX_ABS 4.0
#define NLMS_DT_THRESHOLD 0.40

typedef struct nlms_instance_s {
    double weights[NLMS_TAPS];
    double history[NLMS_TAPS]; /* index 0 = most recent render sample */
    float pending_ref[AS_FRAME_SAMPLES];
    uint64_t epoch;
    int64_t output_start;
    uint64_t frames;
    uint64_t adapted_frames;
    uint64_t double_talk_frames;
    uint64_t reference_frames;
    uint64_t no_reference_frames;
    uint64_t invalid_count;
    int reference_ready;
} nlms_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void clear_state(nlms_instance *instance) {
    memset(instance->weights, 0, sizeof(instance->weights));
    memset(instance->history, 0, sizeof(instance->history));
    memset(instance->pending_ref, 0, sizeof(instance->pending_ref));
    instance->frames = 0u;
    instance->adapted_frames = 0u;
    instance->double_talk_frames = 0u;
    instance->reference_frames = 0u;
    instance->no_reference_frames = 0u;
    instance->invalid_count = 0u;
    instance->reference_ready = 0;
}

/* Deterministic frame-level normalized cross-correlation double-talk hold. */
static int double_talk_detected(const nlms_instance *instance,
                                const float *microphone) {
    double window[NLMS_TAPS + AS_FRAME_SAMPLES];
    double mic_energy = 0.0;
    double ref_energy = 0.0;
    double best = 0.0;
    for (uint32_t index = 0u; index < NLMS_TAPS; ++index) {
        window[NLMS_TAPS - 1u - index] = instance->history[index];
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        window[NLMS_TAPS + index] = (double)instance->pending_ref[index];
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)microphone[index];
        mic_energy += value * value;
    }
    for (uint32_t index = 0u; index < NLMS_TAPS + AS_FRAME_SAMPLES; ++index) {
        ref_energy += window[index] * window[index];
    }
    if (mic_energy <= NLMS_EPSILON || ref_energy <= NLMS_EPSILON) return 0;
    for (uint32_t lag = 0u; lag < NLMS_TAPS; ++lag) {
        double cross = 0.0;
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            cross += window[lag + index] * (double)microphone[index];
        }
        const double coherence = (cross * cross) /
                                 (ref_energy * mic_energy + NLMS_EPSILON);
        if (coherence > best) best = coherence;
    }
    return best < NLMS_DT_THRESHOLD;
}

as_status_v0 nlms_aec_feed_reference(void *instance, const float *reference,
                                     uint32_t count, as_error_v0 *error) {
    (void)error;
    nlms_instance *state = (nlms_instance *)instance;
    if (state == NULL || reference == NULL || count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)reference[index];
        if (!isfinite(value) || fabs(value) > NLMS_MAX_ABS) return AS_INVALID_ARGUMENT;
    }
    memcpy(state->pending_ref, reference, sizeof(state->pending_ref));
    state->reference_ready = 1;
    ++state->reference_frames;
    return AS_OK;
}

as_status_v0 nlms_aec_snapshot(void *instance, uint64_t *frames,
                               uint64_t *adapted_frames,
                               uint64_t *double_talk_frames,
                               uint64_t *no_reference_frames,
                               uint64_t *invalid_count, double *weight_l1) {
    nlms_instance *state = (nlms_instance *)instance;
    if (state == NULL || frames == NULL || adapted_frames == NULL ||
        double_talk_frames == NULL || no_reference_frames == NULL ||
        invalid_count == NULL || weight_l1 == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    *frames = state->frames;
    *adapted_frames = state->adapted_frames;
    *double_talk_frames = state->double_talk_frames;
    *no_reference_frames = state->no_reference_frames;
    *invalid_count = state->invalid_count;
    double total = 0.0;
    for (uint32_t index = 0u; index < NLMS_TAPS; ++index) {
        total += fabs(state->weights[index]);
    }
    *weight_l1 = total;
    return AS_OK;
}

static as_status_v0 AS_CALL nlms_create(const as_create_config_v0 *config,
                                        void **out_instance,
                                        as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        NLMS_PROVIDER_ID, strlen(NLMS_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    nlms_instance *instance = (nlms_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    clear_state(instance);
    instance->epoch = config->epoch;
    instance->output_start = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL nlms_process(void *opaque,
                                         const as_frame_v0 *frame,
                                         const as_output_v0 *output,
                                         as_result_v0 *result) {
    nlms_instance *instance = (nlms_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const int final_frame = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    if (frame->input_count != AS_FRAME_SAMPLES ||
        frame->input_valid_count == 0u ||
        frame->input_valid_count > AS_FRAME_SAMPLES ||
        (!final_frame && frame->input_valid_count != AS_FRAME_SAMPLES) ||
        (frame->flags & ~(uint32_t)AS_FRAME_FINAL_INPUT) != 0u ||
        frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->output_start) {
        ++instance->invalid_count;
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < frame->input_valid_count; ++index) {
        const double value = (double)frame->input[index];
        if (!isfinite(value) || fabs(value) > NLMS_MAX_ABS) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
    }

    float microphone_frame[AS_FRAME_SAMPLES];
    memset(microphone_frame, 0, sizeof(microphone_frame));
    memcpy(microphone_frame, frame->input,
           (size_t)frame->input_valid_count * sizeof(float));
    const int referenced = instance->reference_ready;
    int frame_adapted = 0;
    int hold = 0;
    if (referenced) {
        hold = double_talk_detected(instance, microphone_frame);
        if (hold) ++instance->double_talk_frames;
    }

    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double microphone = (double)microphone_frame[index];
        double value = microphone;
        if (referenced) {
            const double played = (double)instance->pending_ref[index];
            for (uint32_t tap = NLMS_TAPS - 1u; tap > 0u; --tap) {
                instance->history[tap] = instance->history[tap - 1u];
            }
            instance->history[0] = played;
            double estimate = 0.0;
            double energy = 0.0;
            for (uint32_t tap = 0u; tap < NLMS_TAPS; ++tap) {
                estimate += instance->weights[tap] * instance->history[tap];
                energy += instance->history[tap] * instance->history[tap];
            }
            value = microphone - estimate;
            if (!hold && energy > NLMS_EPSILON) {
                const double gain = NLMS_STEP * value / (energy + NLMS_EPSILON);
                for (uint32_t tap = 0u; tap < NLMS_TAPS; ++tap) {
                    instance->weights[tap] += gain * instance->history[tap];
                }
                frame_adapted = 1;
            }
            if (!isfinite(value) || fabs(value) > NLMS_MAX_ABS) {
                ++instance->invalid_count;
                return AS_INVALID_ARGUMENT;
            }
        }
        if (index < frame->input_valid_count) output->samples[index] = (float)value;
    }

    ++instance->frames;
    if (frame_adapted) ++instance->adapted_frames;
    instance->output_start += (int64_t)AS_FRAME_SAMPLES;
    instance->reference_ready = 0;
    if (!referenced) ++instance->no_reference_frames;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = frame->input_valid_count;
    result->flags = final_frame ? AS_RESULT_FINAL_PADDING : 0u;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL nlms_reset(void *opaque, uint64_t epoch,
                                       int64_t first_input_sample,
                                       as_error_v0 *error) {
    (void)error;
    nlms_instance *instance = (nlms_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    clear_state(instance);
    instance->epoch = epoch;
    instance->output_start = first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL nlms_drain(void *opaque,
                                       const as_output_v0 *output,
                                       as_result_v0 *result) {
    nlms_instance *instance = (nlms_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL nlms_destroy(void *opaque) { free(opaque); }

as_status_v0 nlms_aec_instance_create(const as_create_config_v0 *config,
                                      void **out_instance, as_error_v0 *error) {
    return nlms_create(config, out_instance, error);
}

as_status_v0 nlms_aec_instance_process(void *instance, const as_frame_v0 *frame,
                                       const as_output_v0 *output,
                                       as_result_v0 *result) {
    return nlms_process(instance, frame, output, result);
}

as_status_v0 nlms_aec_instance_reset(void *instance, uint64_t epoch,
                                     int64_t first_input_sample,
                                     as_error_v0 *error) {
    return nlms_reset(instance, epoch, first_input_sample, error);
}

void nlms_aec_instance_destroy(void *instance) { nlms_destroy(instance); }

as_status_v0 nlms_aec_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        nlms_create, nlms_process, nlms_reset, nlms_drain,
        nlms_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
