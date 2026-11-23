/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local OLA/SOLA reference provider.
 *
 * It uses only the public v0 provider/session headers. It is not installed,
 * registered by default or linked into any shared SDK target. The engine is a
 * buffered overlap-add time scaler with waveform-similarity alignment. The v0
 * boundary still emits exactly 160 samples per process call; valid_count is
 * the only content-length signal, so this is a fixture adapter and not a
 * playback actuator.
 */
#include "audio_sdk/session_v0.h"
#include "ola_sola_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define PI 3.14159265358979323846
#define SEGMENT 512u
#define OVERLAP 256u
#define HOP (SEGMENT - OVERLAP)
#define SEARCH 80u
#define PHASE_DENOMINATOR 1000000
#define RATE_MIN 0.75
#define RATE_MAX 1.50
#define SLEW_PER_SEGMENT 0.012
#define MAX_ABS 1.0
#define EPS 1e-12
#define INPUT_CAPACITY 32768u
#define FIFO_CAPACITY 32768u

static const struct rate_point {
    int64_t start;
    double rate;
} kSchedule[] = {
    {0, 1.0}, {4800, 1.25}, {8000, 1.0}, {11200, 1.5}
};
#define SCHEDULE_COUNT (sizeof(kSchedule) / sizeof(kSchedule[0]))

typedef struct ola_sola_instance_s {
    float input[INPUT_CAPACITY];
    int64_t input_start;
    int64_t input_end;
    int64_t phase;
    double current_rate;
    int64_t last_effective_start;
    double pending[SEGMENT];
    double pending_norm[SEGMENT];
    double window[SEGMENT];
    int64_t pending_start;
    int64_t next_synth;
    uint32_t segments;
    float fifo[FIFO_CAPACITY];
    uint32_t fifo_head;
    uint32_t fifo_count;
    uint32_t finalized;
    uint32_t flushed;
    uint64_t epoch;
    int64_t input_position;
    int64_t output_position;
    uint32_t invalid_count;
} ola_sola_instance;

static double rate_at(int64_t position) {
    double rate = kSchedule[0].rate;
    for (uint32_t index = 0u; index < SCHEDULE_COUNT; ++index) {
        if (position >= kSchedule[index].start) rate = kSchedule[index].rate;
        else break;
    }
    return rate;
}

static void initialize_window(ola_sola_instance *instance) {
    for (uint32_t index = 0u; index < SEGMENT; ++index) {
        instance->window[index] =
            0.5 - 0.5 * cos(2.0 * PI * (double)index / (double)(SEGMENT - 1u));
    }
}

static void reset_state(ola_sola_instance *instance, uint64_t epoch,
                        int64_t first_input_sample) {
    memset(instance, 0, sizeof(*instance));
    initialize_window(instance);
    instance->input_start = first_input_sample;
    instance->input_end = first_input_sample;
    instance->last_effective_start = INT64_MIN / 4;
    instance->current_rate = kSchedule[0].rate;
    instance->epoch = epoch;
    instance->input_position = first_input_sample;
    instance->output_position = first_input_sample;
}

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0u || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL ola_sola_create(const as_create_config_v0 *config,
                                            void **out_instance,
                                            as_error_v0 *error) {
    (void)error;
    if (config == NULL || out_instance == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        OLA_SOLA_PROVIDER_ID, strlen(OLA_SOLA_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    ola_sola_instance *instance =
        (ola_sola_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static void delta_bounds(const ola_sola_instance *instance, int64_t nominal,
                         int64_t *low, int64_t *high) {
    *low = -(int64_t)SEARCH;
    if (instance->input_start - nominal > *low) *low = instance->input_start - nominal;
    *high = (int64_t)SEARCH;
    const int64_t input_limit = instance->input_end - (nominal + (int64_t)SEGMENT);
    if (input_limit < *high) *high = input_limit;
    if (instance->last_effective_start > INT64_MIN / 8 &&
        instance->last_effective_start - nominal > *low) {
        *low = instance->last_effective_start - nominal;
    }
}

static double similarity(const ola_sola_instance *instance, int64_t effective_start) {
    double mean_a = 0.0;
    double mean_b = 0.0;
    const int64_t base = effective_start - instance->input_start;
    for (uint32_t offset = 0u; offset < OVERLAP; ++offset) {
        mean_a += (double)instance->input[base + offset] * instance->window[offset];
        mean_b += instance->pending[offset] / fmax(instance->pending_norm[offset], EPS);
    }
    mean_a /= (double)OVERLAP;
    mean_b /= (double)OVERLAP;
    double numerator = 0.0;
    double energy_a = 0.0;
    double energy_b = 0.0;
    for (uint32_t offset = 0u; offset < OVERLAP; ++offset) {
        const double a = (double)instance->input[base + offset] * instance->window[offset] - mean_a;
        const double b = instance->pending[offset] / fmax(instance->pending_norm[offset], EPS) - mean_b;
        numerator += a * b;
        energy_a += a * a;
        energy_b += b * b;
    }
    return numerator / sqrt(energy_a * energy_b + EPS);
}

static int64_t choose_delta(const ola_sola_instance *instance, int64_t nominal,
                            int64_t low, int64_t high) {
    int64_t best = low;
    double best_score = 0.0;
    int have_best = 0;
    /* Python breaks ties by (abs(delta), delta); iterate the same way. */
    for (int64_t delta = low; delta <= high; ++delta) {
        const double score = instance->segments ? similarity(instance, nominal + delta) : 0.0;
        const int64_t abs_delta = delta < 0 ? -delta : delta;
        const int64_t best_abs = best < 0 ? -best : best;
        if (!have_best || score > best_score ||
            (score == best_score && (abs_delta < best_abs ||
                                     (abs_delta == best_abs && delta < best)))) {
            best = delta;
            best_score = score;
            have_best = 1;
        }
    }
    return best;
}

static void emit_samples(ola_sola_instance *instance, uint32_t count) {
    if (count == 0u || instance->flushed) return;
    for (uint32_t offset = 0u; offset < count; ++offset) {
        const double norm = instance->pending_norm[offset] > EPS
                                ? instance->pending_norm[offset]
                                : EPS;
        const double value = instance->pending[offset] / norm;
        if (instance->fifo_count < FIFO_CAPACITY) {
            instance->fifo[(instance->fifo_head + instance->fifo_count) % FIFO_CAPACITY] =
                (float)value;
            ++instance->fifo_count;
        }
    }
    if (count < SEGMENT) {
        memmove(instance->pending, instance->pending + count,
                (SEGMENT - count) * sizeof(double));
        memmove(instance->pending_norm, instance->pending_norm + count,
                (SEGMENT - count) * sizeof(double));
        memset(instance->pending + (SEGMENT - count), 0, count * sizeof(double));
        memset(instance->pending_norm + (SEGMENT - count), 0, count * sizeof(double));
    } else {
        memset(instance->pending, 0, sizeof(instance->pending));
        memset(instance->pending_norm, 0, sizeof(instance->pending_norm));
    }
    instance->pending_start += (int64_t)count;
}

static void synthesize(ola_sola_instance *instance) {
    for (;;) {
        int64_t low = 0;
        int64_t high = 0;
        int64_t nominal = instance->phase / PHASE_DENOMINATOR + instance->input_start;
        delta_bounds(instance, nominal, &low, &high);
        if (low > high) return;
        if (instance->segments > 0u) emit_samples(instance, HOP);
        const int64_t effective_start = nominal + choose_delta(instance, nominal, low, high);
        const int64_t base = effective_start - instance->input_start;
        for (uint32_t index = 0u; index < SEGMENT; ++index) {
            const double value = (double)instance->input[base + index] * instance->window[index];
            instance->pending[index] += value;
            instance->pending_norm[index] += instance->window[index];
        }
        const double previous_rate = instance->current_rate;
        const double target = rate_at(effective_start - instance->input_start);
        const double step = SLEW_PER_SEGMENT;
        if (target > previous_rate) {
            instance->current_rate = target < previous_rate + step ? target : previous_rate + step;
        } else {
            instance->current_rate = target > previous_rate - step ? target : previous_rate - step;
        }
        instance->phase += llround((double)HOP * instance->current_rate * PHASE_DENOMINATOR);
        instance->last_effective_start = effective_start;
        ++instance->segments;
        instance->next_synth += (int64_t)HOP;
    }
}

static void flush_engine(ola_sola_instance *instance) {
    if (instance->flushed) return;
    emit_samples(instance, SEGMENT);
    instance->flushed = 1;
}

static as_status_v0 AS_CALL ola_sola_process(void *opaque,
                                             const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    ola_sola_instance *instance = (ola_sola_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES ||
        frame->input_valid_count == 0u ||
        frame->input_valid_count > AS_FRAME_SAMPLES ||
        (frame->flags & ~AS_FRAME_FINAL_INPUT) != 0u ||
        frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->input_position ||
        instance->finalized) {
        ++instance->invalid_count;
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0u; index < frame->input_valid_count; ++index) {
        const double sample = (double)frame->input[index];
        if (!isfinite(sample) || fabs(sample) > MAX_ABS) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
    }
    const size_t appended = (size_t)(instance->input_end - instance->input_start);
    if (appended + frame->input_valid_count > INPUT_CAPACITY) return AS_RESOURCE_EXHAUSTED;
    memcpy(instance->input + appended, frame->input,
           frame->input_valid_count * sizeof(float));
    instance->input_end += (int64_t)frame->input_valid_count;
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) instance->finalized = 1u;
    synthesize(instance);
    if (instance->finalized) flush_engine(instance);

    const double rate = rate_at(frame->first_input_sample);
    uint32_t target = (uint32_t)llround((double)frame->input_valid_count / rate);
    if (target > AS_FRAME_SAMPLES) target = AS_FRAME_SAMPLES;
    if (target > instance->fifo_count) target = instance->fifo_count;
    for (uint32_t index = 0u; index < target; ++index) {
        output->samples[index] = instance->fifo[instance->fifo_head];
        instance->fifo_head = (instance->fifo_head + 1u) % FIFO_CAPACITY;
        --instance->fifo_count;
    }
    for (uint32_t index = target; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = 0.0f;
    }

    instance->input_position += (int64_t)AS_FRAME_SAMPLES;
    instance->output_position += (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = target;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL ola_sola_reset(void *opaque, uint64_t epoch,
                                           int64_t first_input_sample,
                                           as_error_v0 *error) {
    (void)error;
    ola_sola_instance *instance = (ola_sola_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL ola_sola_drain(void *opaque,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    ola_sola_instance *instance = (ola_sola_instance *)opaque;
    if (instance == NULL || output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (!instance->finalized) return AS_INVALID_ARGUMENT;
    const int64_t source = instance->output_position;
    uint32_t count = instance->fifo_count;
    if (count > AS_FRAME_SAMPLES) count = AS_FRAME_SAMPLES;
    for (uint32_t index = 0u; index < count; ++index) {
        output->samples[index] = instance->fifo[instance->fifo_head];
        instance->fifo_head = (instance->fifo_head + 1u) % FIFO_CAPACITY;
        --instance->fifo_count;
    }
    for (uint32_t index = count; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = 0.0f;
    }
    instance->output_position = source + (int64_t)count;
    as_result_v0_init(result);
    result->status = count ? AS_OK : AS_END_OF_STREAM;
    result->consumed_count = 0u;
    result->produced_count = count;
    result->valid_offset = 0u;
    result->valid_count = count;
    result->epoch = instance->epoch;
    result->source_first_sample = source;
    return result->status;
}

static void AS_CALL ola_sola_destroy(void *opaque) { free(opaque); }

as_status_v0 ola_sola_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        ola_sola_create, ola_sola_process, ola_sola_reset, ola_sola_drain,
        ola_sola_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
