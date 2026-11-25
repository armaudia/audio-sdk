/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered synthetic AEC3-shaped reference.
 *
 * Task-local source only.  It uses the public v0 provider/session headers for
 * the engine boundary and a task-local sidechain helper for the explicit
 * playback/render reference, because v0 frames carry a single mono stream.
 * No installed registry, public API, descriptor or default is changed.  The
 * constants and sample order mirror docs/task-evidence/webrtc-aec3/reference.py.
 * This is NOT WebRTC AEC3 source/binary/weights.
 */
#include "audio_sdk/session_v0.h"
#include "webrtc_aec3_provider.h"
#include "webrtc_aec3_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define AEC3_TAPS 96u
#define AEC3_STEP_MAIN 0.18
#define AEC3_STEP_SHADOW 0.25
#define AEC3_EPS 1e-8
#define AEC3_DT_ENTER 0.35
#define AEC3_DT_EXIT 0.70
#define AEC3_DT_HANGOVER 2u
#define AEC3_GAIN_LOW 0.30
#define AEC3_GAIN_HIGH 0.80
#define AEC3_GAIN_MIN 0.22
#define AEC3_MAX_ABS 4.0

typedef struct webrtc_aec3_instance_s {
    double main[AEC3_TAPS];
    double shadow[AEC3_TAPS];
    double history[AEC3_TAPS]; /* index 0 = most recent render sample */
    float pending_ref[AS_FRAME_SAMPLES];
    uint64_t epoch;
    int64_t output_start;
    uint64_t frames;
    uint64_t adapted_frames;
    uint64_t double_talk_frames;
    uint64_t reference_frames;
    uint64_t no_reference_frames;
    uint64_t invalid_count;
    uint64_t safety_resets;
    double last_ratio;
    uint32_t hold_frames;
    int reference_ready;
} webrtc_aec3_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void clear_state(webrtc_aec3_instance *instance) {
    memset(instance->main, 0, sizeof(instance->main));
    memset(instance->shadow, 0, sizeof(instance->shadow));
    memset(instance->history, 0, sizeof(instance->history));
    memset(instance->pending_ref, 0, sizeof(instance->pending_ref));
    instance->frames = 0u;
    instance->adapted_frames = 0u;
    instance->double_talk_frames = 0u;
    instance->reference_frames = 0u;
    instance->no_reference_frames = 0u;
    instance->invalid_count = 0u;
    instance->safety_resets = 0u;
    instance->last_ratio = 1.0;
    instance->hold_frames = 0u;
    instance->reference_ready = 0;
}

static double gain_for_ratio(double ratio) {
    if (ratio <= AEC3_GAIN_LOW) return AEC3_GAIN_MIN;
    if (ratio >= AEC3_GAIN_HIGH) return 1.0;
    return AEC3_GAIN_MIN + (ratio - AEC3_GAIN_LOW) * (1.0 - AEC3_GAIN_MIN) /
           (AEC3_GAIN_HIGH - AEC3_GAIN_LOW);
}

as_status_v0 webrtc_aec3_feed_reference(void *instance, const float *reference,
                                        uint32_t count, as_error_v0 *error) {
    (void)error;
    webrtc_aec3_instance *state = (webrtc_aec3_instance *)instance;
    if (state == NULL || reference == NULL || count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)reference[index];
        if (!isfinite(value) || fabs(value) > AEC3_MAX_ABS) return AS_INVALID_ARGUMENT;
    }
    memcpy(state->pending_ref, reference, sizeof(state->pending_ref));
    state->reference_ready = 1;
    ++state->reference_frames;
    return AS_OK;
}

as_status_v0 webrtc_aec3_snapshot(void *instance, uint64_t *frames,
                                  uint64_t *adapted_frames,
                                  uint64_t *double_talk_frames,
                                  uint64_t *no_reference_frames,
                                  uint64_t *invalid_count, double *weight_l1) {
    webrtc_aec3_instance *state = (webrtc_aec3_instance *)instance;
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
    for (uint32_t index = 0u; index < AEC3_TAPS; ++index) {
        total += fabs(state->main[index]);
    }
    *weight_l1 = total;
    return AS_OK;
}

static as_status_v0 AS_CALL webrtc_aec3_create(const as_create_config_v0 *config,
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
                        WEBRTC_AEC3_PROVIDER_ID, strlen(WEBRTC_AEC3_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    webrtc_aec3_instance *instance = (webrtc_aec3_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    clear_state(instance);
    instance->epoch = config->epoch;
    instance->output_start = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL webrtc_aec3_process(void *opaque,
                                                const as_frame_v0 *frame,
                                                const as_output_v0 *output,
                                                as_result_v0 *result) {
    webrtc_aec3_instance *instance = (webrtc_aec3_instance *)opaque;
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
        if (!isfinite(value) || fabs(value) > AEC3_MAX_ABS) {
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
    double ratio = instance->last_ratio;
    int held = (ratio >= AEC3_DT_ENTER) || (instance->hold_frames > 0u);
    double gain = gain_for_ratio(ratio);
    double shadow_residual_energy = 0.0;
    double microphone_energy = 0.0;

    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double microphone = (double)microphone_frame[index];
        double value = microphone;
        if (referenced) {
            const double played = (double)instance->pending_ref[index];
            int finite_main = 1;
            for (uint32_t tap = 0u; tap < AEC3_TAPS; ++tap) {
                if (!isfinite(instance->main[tap])) { finite_main = 0; break; }
            }
            if (!finite_main) {
                memset(instance->main, 0, sizeof(instance->main));
                ++instance->safety_resets;
            }
            double estimate_shadow = 0.0;
            double estimate_main = 0.0;
            double render_energy = 0.0;
            for (uint32_t tap = 0u; tap < AEC3_TAPS; ++tap) {
                estimate_shadow += instance->shadow[tap] * instance->history[tap];
                estimate_main += instance->main[tap] * instance->history[tap];
                render_energy += instance->history[tap] * instance->history[tap];
            }
            const double residual_shadow = microphone - estimate_shadow;
            const double residual_main = microphone - estimate_main;
            value = gain * residual_main;
            shadow_residual_energy += residual_shadow * residual_shadow;
            microphone_energy += microphone * microphone;
            if (render_energy > AEC3_EPS) {
                const double step_shadow = AEC3_STEP_SHADOW * residual_shadow /
                                           (render_energy + AEC3_EPS);
                for (uint32_t tap = 0u; tap < AEC3_TAPS; ++tap) {
                    instance->shadow[tap] += step_shadow * instance->history[tap];
                }
                if (!held) {
                    const double step_main = AEC3_STEP_MAIN * residual_main /
                                             (render_energy + AEC3_EPS);
                    for (uint32_t tap = 0u; tap < AEC3_TAPS; ++tap) {
                        instance->main[tap] += step_main * instance->history[tap];
                    }
                    frame_adapted = 1;
                }
            }
            for (uint32_t tap = AEC3_TAPS - 1u; tap > 0u; --tap) {
                instance->history[tap] = instance->history[tap - 1u];
            }
            instance->history[0] = played;
            if (!isfinite(value) || fabs(value) > AEC3_MAX_ABS) {
                value = 0.0;
                ++instance->invalid_count;
            }
        }
        if (index < frame->input_valid_count) output->samples[index] = (float)value;
    }

    if (referenced) {
        ratio = shadow_residual_energy / (microphone_energy + AEC3_EPS);
        if (!isfinite(ratio)) ratio = 1.0;
        if (ratio >= AEC3_DT_ENTER) {
            instance->hold_frames = AEC3_DT_HANGOVER;
        } else if (ratio <= AEC3_DT_EXIT) {
            instance->hold_frames = 0u;
        } else if (instance->hold_frames > 0u) {
            instance->hold_frames -= 1u;
        }
        instance->last_ratio = ratio;
    } else {
        instance->last_ratio = 1.0;
        instance->hold_frames = 0u;
    }

    ++instance->frames;
    if (frame_adapted) ++instance->adapted_frames;
    if (held && referenced) ++instance->double_talk_frames;
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

static as_status_v0 AS_CALL webrtc_aec3_reset(void *opaque, uint64_t epoch,
                                              int64_t first_input_sample,
                                              as_error_v0 *error) {
    (void)error;
    webrtc_aec3_instance *instance = (webrtc_aec3_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    clear_state(instance);
    instance->epoch = epoch;
    instance->output_start = first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL webrtc_aec3_drain(void *opaque,
                                              const as_output_v0 *output,
                                              as_result_v0 *result) {
    webrtc_aec3_instance *instance = (webrtc_aec3_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL webrtc_aec3_destroy(void *opaque) { free(opaque); }

as_status_v0 webrtc_aec3_instance_create(const as_create_config_v0 *config,
                                         void **out_instance, as_error_v0 *error) {
    return webrtc_aec3_create(config, out_instance, error);
}

as_status_v0 webrtc_aec3_instance_process(void *instance, const as_frame_v0 *frame,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    return webrtc_aec3_process(instance, frame, output, result);
}

as_status_v0 webrtc_aec3_instance_reset(void *instance, uint64_t epoch,
                                        int64_t first_input_sample,
                                        as_error_v0 *error) {
    return webrtc_aec3_reset(instance, epoch, first_input_sample, error);
}

void webrtc_aec3_instance_destroy(void *instance) { webrtc_aec3_destroy(instance); }

as_status_v0 webrtc_aec3_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        webrtc_aec3_create, webrtc_aec3_process, webrtc_aec3_reset, webrtc_aec3_drain,
        webrtc_aec3_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
