/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered guarded RLS acoustic echo cancellation reference.
 *
 * Task-local source only.  It uses the public v0 provider/session headers for
 * the engine boundary and a task-local sidechain helper for the explicit
 * playback/render reference, because v0 frames carry a single mono stream.
 * No installed registry, public API, descriptor or default is changed.  The
 * constants, operation order and sample order mirror
 * docs/task-evidence/rls-aec/reference.py.
 */
#include "audio_sdk/session_v0.h"
#include "rls_aec_provider.h"
#include "rls_aec_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define RLS_TAPS 24u
#define RLS_LAMBDA 0.995
#define RLS_P0 1.0
#define RLS_EPSILON 1e-8
#define RLS_MAX_ABS_INPUT 4.0
#define RLS_WEIGHT_L1_LIMIT 8.0
#define RLS_MATRIX_ABS_LIMIT 1e12
#define RLS_DOUBLE_TALK_THRESHOLD 0.70

enum rls_phase_code { RLS_PHASE_ADAPTING = 0, RLS_PHASE_FROZEN = 1 };
enum rls_safety_code {
    RLS_SAFETY_NONE = 0,
    RLS_SAFETY_NONFINITE = 1,
    RLS_SAFETY_BOUNDEDNESS = 2
};

typedef struct rls_instance_s {
    double weights[RLS_TAPS];
    double history[RLS_TAPS]; /* index 0 = most recent render sample */
    double matrix[RLS_TAPS][RLS_TAPS];
    int matrix_valid;
    float pending_ref[AS_FRAME_SAMPLES];
    int reference_ready;
    uint64_t epoch;
    int64_t next_sample;
    uint64_t processed_samples;
    uint64_t frames;
    uint64_t adapted_frames;
    uint64_t double_talk_frames;
    uint64_t reference_frames; /* reference samples supplied */
    uint64_t no_reference_frames;
    uint64_t invalid_count;
    uint64_t safety_freezes;
    uint64_t skipped_updates;
    uint32_t phase;
    uint32_t safety_reason;
    double max_weight_l1;
    double max_abs_weight;
    double max_matrix_abs;
} rls_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void clear_state(rls_instance *instance) {
    memset(instance->weights, 0, sizeof(instance->weights));
    memset(instance->history, 0, sizeof(instance->history));
    memset(instance->matrix, 0, sizeof(instance->matrix));
    memset(instance->pending_ref, 0, sizeof(instance->pending_ref));
    for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
        instance->matrix[index][index] = RLS_P0;
    }
    instance->matrix_valid = 1;
    instance->reference_ready = 0;
    instance->processed_samples = 0u;
    instance->frames = 0u;
    instance->adapted_frames = 0u;
    instance->double_talk_frames = 0u;
    instance->reference_frames = 0u;
    instance->no_reference_frames = 0u;
    instance->invalid_count = 0u;
    instance->safety_freezes = 0u;
    instance->skipped_updates = 0u;
    instance->phase = RLS_PHASE_ADAPTING;
    instance->safety_reason = RLS_SAFETY_NONE;
    instance->max_weight_l1 = 0.0;
    instance->max_abs_weight = 0.0;
    instance->max_matrix_abs = 0.0;
}

static double weight_l1(const rls_instance *instance) {
    double total = 0.0;
    for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
        total += fabs(instance->weights[index]);
    }
    return total;
}

static void track_state(rls_instance *instance) {
    const double total = weight_l1(instance);
    double peak = 0.0;
    double matrix_peak = 0.0;
    for (uint32_t row = 0u; row < RLS_TAPS; ++row) {
        for (uint32_t column = 0u; column < RLS_TAPS; ++column) {
            const double value = fabs(instance->matrix[row][column]);
            if (value > matrix_peak) matrix_peak = value;
        }
    }
    for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
        const double value = fabs(instance->weights[index]);
        if (value > peak) peak = value;
    }
    if (total > instance->max_weight_l1) instance->max_weight_l1 = total;
    if (peak > instance->max_abs_weight) instance->max_abs_weight = peak;
    if (matrix_peak > instance->max_matrix_abs) {
        instance->max_matrix_abs = matrix_peak;
    }
}

static void freeze(rls_instance *instance, uint32_t reason) {
    memset(instance->weights, 0, sizeof(instance->weights));
    instance->matrix_valid = 0;
    instance->phase = RLS_PHASE_FROZEN;
    instance->safety_reason = reason;
    ++instance->safety_freezes;
}

static int double_talk_detected(const rls_instance *instance,
                                const float *microphone) {
    double window[RLS_TAPS + AS_FRAME_SAMPLES];
    double mic_energy = 0.0;
    double ref_energy = 0.0;
    double best = 0.0;
    for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
        window[RLS_TAPS - 1u - index] = instance->history[index];
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        window[RLS_TAPS + index] = (double)instance->pending_ref[index];
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)microphone[index];
        mic_energy += value * value;
    }
    for (uint32_t index = 0u; index < RLS_TAPS + AS_FRAME_SAMPLES; ++index) {
        ref_energy += window[index] * window[index];
    }
    if (mic_energy <= RLS_EPSILON || ref_energy <= RLS_EPSILON) return 0;
    for (uint32_t lag = 0u; lag < RLS_TAPS; ++lag) {
        double cross = 0.0;
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            cross += window[lag + index] * (double)microphone[index];
        }
        const double coherence = (cross * cross) /
                                 (ref_energy * mic_energy + RLS_EPSILON);
        if (coherence > best) best = coherence;
    }
    return best < RLS_DOUBLE_TALK_THRESHOLD;
}

/* One causal sample.  Returns 1 when weights were adapted. */
static int process_sample(rls_instance *instance, double microphone,
                          int has_reference, double reference, int adapt_enabled,
                          double *error_out) {
    if (has_reference) {
        for (uint32_t tap = RLS_TAPS - 1u; tap > 0u; --tap) {
            instance->history[tap] = instance->history[tap - 1u];
        }
        instance->history[0] = reference;
        ++instance->reference_frames;
    }

    double estimate = 0.0;
    for (uint32_t tap = 0u; tap < RLS_TAPS; ++tap) {
        estimate += instance->weights[tap] * instance->history[tap];
    }
    double error = microphone - estimate;
    if (!isfinite(error)) {
        freeze(instance, RLS_SAFETY_NONFINITE);
        error = microphone;
    }
    *error_out = error;
    if (!has_reference || !adapt_enabled ||
        instance->phase == RLS_PHASE_FROZEN || !isfinite(error)) {
        return 0;
    }

    double energy = 0.0;
    for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
        energy += instance->history[index] * instance->history[index];
    }
    if (!isfinite(energy) || energy <= RLS_EPSILON) {
        /* The near-end-only guard: P is never divided by lambda here. */
        ++instance->skipped_updates;
        return 0;
    }

    double safe_weights[RLS_TAPS];
    memcpy(safe_weights, instance->weights, sizeof(safe_weights));
    int unsafe = 0;
    if (!instance->matrix_valid) {
        unsafe = 1;
    } else {
        double px[RLS_TAPS];
        for (uint32_t row = 0u; row < RLS_TAPS; ++row) {
            double value = 0.0;
            for (uint32_t column = 0u; column < RLS_TAPS; ++column) {
                value += instance->matrix[row][column] * instance->history[column];
            }
            px[row] = value;
            if (!isfinite(value)) unsafe = 1;
        }
        double denominator = RLS_LAMBDA;
        for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
            denominator += instance->history[index] * px[index];
        }
        if (!isfinite(denominator) || denominator <= RLS_EPSILON || unsafe) {
            unsafe = 1;
        } else {
            double gain[RLS_TAPS];
            double candidate[RLS_TAPS];
            double total = 0.0;
            for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
                gain[index] = px[index] / denominator;
                candidate[index] = safe_weights[index] + gain[index] * error;
                total += fabs(candidate[index]);
                if (!isfinite(candidate[index]) || !isfinite(gain[index])) {
                    unsafe = 1;
                }
            }
            if (total > RLS_WEIGHT_L1_LIMIT) unsafe = 1;
            if (!unsafe) {
                double xtp[RLS_TAPS];
                for (uint32_t index = 0u; index < RLS_TAPS; ++index) {
                    double value = 0.0;
                    for (uint32_t row = 0u; row < RLS_TAPS; ++row) {
                        value += instance->matrix[row][index] * instance->history[row];
                    }
                    xtp[index] = value;
                }
                double updated[RLS_TAPS][RLS_TAPS];
                double peak = 0.0;
                for (uint32_t row = 0u; row < RLS_TAPS; ++row) {
                    for (uint32_t column = 0u; column < RLS_TAPS; ++column) {
                        const double value = (instance->matrix[row][column] -
                                              gain[row] * xtp[column]) /
                                             RLS_LAMBDA;
                        updated[row][column] = value;
                        if (!isfinite(value)) unsafe = 1;
                        const double magnitude = fabs(value);
                        if (magnitude > peak) peak = magnitude;
                    }
                }
                if (peak > RLS_MATRIX_ABS_LIMIT) unsafe = 1;
                if (!unsafe) {
                    memcpy(instance->matrix, updated, sizeof(instance->matrix));
                    memcpy(instance->weights, candidate, sizeof(instance->weights));
                }
            }
        }
    }

    if (unsafe) {
        memcpy(instance->weights, safe_weights, sizeof(instance->weights));
        freeze(instance, RLS_SAFETY_BOUNDEDNESS);
        return 0;
    }
    return 1;
}

as_status_v0 rls_aec_feed_reference(void *instance, const float *reference,
                                    uint32_t count, as_error_v0 *error) {
    (void)error;
    rls_instance *state = (rls_instance *)instance;
    if (state == NULL || reference == NULL || count != AS_FRAME_SAMPLES) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = (double)reference[index];
        if (!isfinite(value) || fabs(value) > RLS_MAX_ABS_INPUT) {
            return AS_INVALID_ARGUMENT;
        }
    }
    memcpy(state->pending_ref, reference, sizeof(state->pending_ref));
    state->reference_ready = 1;
    return AS_OK;
}

as_status_v0 rls_aec_snapshot(void *instance, uint64_t *frames,
                             uint64_t *adapted_frames,
                             uint64_t *double_talk_frames,
                             uint64_t *no_reference_frames,
                             uint64_t *invalid_count,
                             uint64_t *safety_freezes,
                             uint64_t *skipped_updates,
                             double *weight_l1_out, double *max_matrix_abs,
                             uint32_t *phase) {
    rls_instance *state = (rls_instance *)instance;
    if (state == NULL || frames == NULL || adapted_frames == NULL ||
        double_talk_frames == NULL || no_reference_frames == NULL ||
        invalid_count == NULL || safety_freezes == NULL ||
        skipped_updates == NULL || weight_l1_out == NULL ||
        max_matrix_abs == NULL || phase == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    *frames = state->frames;
    *adapted_frames = state->adapted_frames;
    *double_talk_frames = state->double_talk_frames;
    *no_reference_frames = state->no_reference_frames;
    *invalid_count = state->invalid_count;
    *safety_freezes = state->safety_freezes;
    *skipped_updates = state->skipped_updates;
    *weight_l1_out = weight_l1(state);
    *max_matrix_abs = state->max_matrix_abs;
    *phase = state->phase;
    return AS_OK;
}

const char *rls_aec_safety_reason(void *instance) {
    rls_instance *state = (rls_instance *)instance;
    if (state == NULL) return "invalid_instance";
    switch (state->safety_reason) {
        case RLS_SAFETY_NONFINITE: return "nonfinite_state";
        case RLS_SAFETY_BOUNDEDNESS: return "boundedness_violation";
        case RLS_SAFETY_NONE:
        default: return "none";
    }
}

static as_status_v0 AS_CALL rls_create(const as_create_config_v0 *config,
                                       void **out_instance, as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        RLS_AEC_PROVIDER_ID, strlen(RLS_AEC_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    rls_instance *instance = (rls_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    clear_state(instance);
    instance->epoch = config->epoch;
    instance->next_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL rls_process(void *opaque,
                                        const as_frame_v0 *frame,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    rls_instance *instance = (rls_instance *)opaque;
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
        frame->first_input_sample != instance->next_sample) {
        ++instance->invalid_count;
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < frame->input_valid_count; ++index) {
        const double value = (double)frame->input[index];
        if (!isfinite(value) || fabs(value) > RLS_MAX_ABS_INPUT) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
    }

    float microphone_frame[AS_FRAME_SAMPLES];
    memset(microphone_frame, 0, sizeof(microphone_frame));
    memcpy(microphone_frame, frame->input,
           (size_t)frame->input_valid_count * sizeof(float));
    const int referenced = instance->reference_ready;
    int hold = 0;
    if (referenced) {
        hold = double_talk_detected(instance, microphone_frame);
        if (hold) ++instance->double_talk_frames;
    }

    int frame_adapted = 0;
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double microphone = (double)microphone_frame[index];
        double value = microphone;
        if (referenced) {
            double error = 0.0;
            if (process_sample(instance, microphone, 1,
                               (double)instance->pending_ref[index], !hold, &error)) {
                frame_adapted = 1;
            }
            value = error;
        }
        if (!isfinite(value) || fabs(value) > RLS_MAX_ABS_INPUT) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
        if (index < frame->input_valid_count) {
            output->samples[index] = (float)value;
        }
    }

    ++instance->frames;
    instance->processed_samples += frame->input_valid_count;
    instance->next_sample += (int64_t)frame->input_valid_count;
    if (frame_adapted) ++instance->adapted_frames;
    track_state(instance);
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

static as_status_v0 AS_CALL rls_reset(void *opaque, uint64_t epoch,
                                      int64_t first_input_sample,
                                      as_error_v0 *error) {
    (void)error;
    rls_instance *instance = (rls_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    clear_state(instance);
    instance->epoch = epoch;
    instance->next_sample = first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL rls_drain(void *opaque,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    rls_instance *instance = (rls_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_sample;
    return AS_END_OF_STREAM;
}

static void AS_CALL rls_destroy(void *opaque) { free(opaque); }

as_status_v0 rls_aec_instance_create(const as_create_config_v0 *config,
                                     void **out_instance, as_error_v0 *error) {
    return rls_create(config, out_instance, error);
}

as_status_v0 rls_aec_instance_process(void *instance, const as_frame_v0 *frame,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    return rls_process(instance, frame, output, result);
}

as_status_v0 rls_aec_instance_reset(void *instance, uint64_t epoch,
                                    int64_t first_input_sample,
                                    as_error_v0 *error) {
    return rls_reset(instance, epoch, first_input_sample, error);
}

void rls_aec_instance_destroy(void *instance) { rls_destroy(instance); }

as_status_v0 rls_aec_inject_nonfinite_state_for_test(void *instance) {
    rls_instance *state = (rls_instance *)instance;
    if (state == NULL) return AS_INVALID_ARGUMENT;
    state->weights[0] = INFINITY;
    return AS_OK;
}

as_status_v0 rls_aec_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        rls_create, rls_process, rls_reset, rls_drain,
        rls_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
