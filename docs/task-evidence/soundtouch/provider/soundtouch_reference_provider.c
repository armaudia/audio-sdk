/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local SoundTouch-named WSOLA-style stretch reference.
 *
 * Uses only the public v0 provider/session headers. It is not installed, not
 * registered by default and not linked into any shared SDK target. The engine
 * mirrors the Python fixture: a fractional source accumulator, a fractional
 * caller-owned output accumulator, window-normalised overlap-add, waveform
 * similarity alignment and transient-aware segment placement. It is NOT the
 * upstream SoundTouch library and vendors no upstream source, binary or asset.
 * It is a proposal-only WSOLA-style synthetic model, not a qualified provider.
 */
#include "audio_sdk/session_v0.h"
#include "soundtouch_reference_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define SEGMENT 512u
#define OVERLAP 448u
#define HOP (SEGMENT - OVERLAP)
#define SEARCH 16
#define SCORE_WINDOW 24
#define PHASE_DENOMINATOR 1000000
#define RATE_MIN 0.75
#define RATE_MAX 1.50
#define RATE_SLEW_PER_SEGMENT 0.005
#define MAX_ABS 1.0
#define EPS 1e-12
#define SCORE_TIE_TOLERANCE 1e-9
#define AMPLITUDE_TIE_TOLERANCE 1e-12
#define TRANSIENT_THRESHOLD 0.18
#define TRANSIENT_RISE 0.06
#define TRANSIENT_LOOKBACK 16
#define TRANSIENT_TARGET_OFFSET (HOP / 2)
#define INPUT_CAPACITY 16384u
#define FIFO_CAPACITY 32768u
#define PEAK_CAPACITY 256u

static const struct rate_point {
    int64_t start;
    double rate;
} kSchedule[] = {
    {0, 1.0}, {4800, 1.25}, {8000, 1.0}, {11200, 1.5}
};
#define SCHEDULE_COUNT (sizeof(kSchedule) / sizeof(kSchedule[0]))

typedef struct stretch_instance_s {
    float input[INPUT_CAPACITY];
    int64_t input_start;
    int64_t input_end;
    int64_t phase;
    double current_rate;
    int64_t last_effective_start;
    double pending[SEGMENT];
    int pending_norm[SEGMENT];
    double pending_src[SEGMENT];
    int64_t pending_start;
    int64_t window[SEGMENT];
    float fifo[FIFO_CAPACITY];
    uint32_t fifo_head;
    uint32_t fifo_count;
    uint32_t segments;
    uint32_t finalized;
    uint32_t flushed;
    uint64_t epoch;
    int64_t input_position;
    int64_t output_position;
    double rate_carry;
    uint32_t invalid_count;
} stretch_instance;

typedef struct key_s {
    double first;
    int second;
    int third;
    int fourth;
} key_type;

static double rate_at(int64_t position) {
    double rate = kSchedule[0].rate;
    for (uint32_t index = 0u; index < SCHEDULE_COUNT; ++index) {
        if (position >= kSchedule[index].start) rate = kSchedule[index].rate;
        else break;
    }
    return rate;
}

static long long llround_local(double value) {
    if (value >= 0.0) return (long long)floor(value + 0.5);
    return (long long)ceil(value - 0.5);
}

static void initialize_window(stretch_instance *instance) {
    for (uint32_t index = 0u; index < SEGMENT; ++index) {
        const uint32_t rising = index + 1u;
        const uint32_t falling = SEGMENT - index;
        instance->window[index] = (int64_t)(rising < falling ? rising : falling);
    }
}

static void reset_state(stretch_instance *instance, uint64_t epoch,
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

static as_status_v0 AS_CALL stretch_create(const as_create_config_v0 *config,
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
                        SOUNDTOUCH_REFERENCE_PROVIDER_ID,
                        strlen(SOUNDTOUCH_REFERENCE_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    stretch_instance *instance = (stretch_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static void delta_bounds(const stretch_instance *instance, int64_t nominal,
                         int64_t *low, int64_t *high) {
    *low = -SEARCH;
    if (instance->input_start - nominal > *low) *low = instance->input_start - nominal;
    *high = (int64_t)SEARCH;
    const int64_t limit = instance->input_end - nominal - (int64_t)SEGMENT;
    if (limit < *high) *high = limit;
    if (instance->last_effective_start > INT64_MIN / 8 &&
        instance->last_effective_start + 1 - nominal > *low) {
        *low = instance->last_effective_start + 1 - nominal;
    }
}

static double similarity(const stretch_instance *instance, int64_t effective_start) {
    double a[SCORE_WINDOW];
    double b[SCORE_WINDOW];
    double mean_a = 0.0;
    double mean_b = 0.0;
    const int64_t base = effective_start - instance->input_start;
    for (uint32_t offset = 0u; offset < SCORE_WINDOW; ++offset) {
        a[offset] = (double)instance->input[base + offset] *
                    (double)instance->window[offset];
        const int norm = instance->pending_norm[offset] > 1
                             ? instance->pending_norm[offset]
                             : 1;
        b[offset] = instance->pending[offset] / (double)norm;
        mean_a += a[offset];
        mean_b += b[offset];
    }
    mean_a /= (double)SCORE_WINDOW;
    mean_b /= (double)SCORE_WINDOW;
    double numerator = 0.0;
    double energy_a = 0.0;
    double energy_b = 0.0;
    for (uint32_t offset = 0u; offset < SCORE_WINDOW; ++offset) {
        const double da = a[offset] - mean_a;
        const double db = b[offset] - mean_b;
        numerator += da * db;
        energy_a += da * da;
        energy_b += db * db;
    }
    return numerator / sqrt(energy_a * energy_b + EPS);
}

static void transient_table(const stretch_instance *instance, int64_t nominal,
                            int64_t low, int64_t high,
                            int64_t *peak_index, double *peak_amplitude,
                            uint32_t *peak_count) {
    *peak_count = 0u;
    int64_t start = nominal + low;
    if (start < instance->input_start) start = instance->input_start;
    int64_t stop = nominal + high + (int64_t)HOP;
    if (stop > instance->input_end) stop = instance->input_end;
    for (int64_t sample_index = start; sample_index < stop; ++sample_index) {
        const double amplitude = fabs((double)instance->input[sample_index -
                                                               instance->input_start]);
        if (amplitude < TRANSIENT_THRESHOLD) continue;
        int64_t lookback = sample_index - TRANSIENT_LOOKBACK;
        if (lookback < instance->input_start) lookback = instance->input_start;
        double previous = 0.0;
        for (int64_t j = lookback; j < sample_index; ++j) {
            previous += fabs((double)instance->input[j - instance->input_start]);
        }
        previous /= (double)(sample_index - lookback > 0 ? sample_index - lookback : 1);
        if (previous < TRANSIENT_RISE && *peak_count < PEAK_CAPACITY) {
            peak_index[*peak_count] = sample_index;
            peak_amplitude[*peak_count] = amplitude;
            ++*peak_count;
        }
    }
}

static int key_less(const key_type *left, const key_type *right) {
    if (left->first < right->first - SCORE_TIE_TOLERANCE) return 1;
    if (left->first > right->first + SCORE_TIE_TOLERANCE) return 0;
    if (left->second != right->second) return left->second < right->second;
    if (left->third != right->third) return left->third < right->third;
    return left->fourth < right->fourth;
}

static int64_t choose_delta(const stretch_instance *instance, int64_t nominal,
                            int64_t low, int64_t high) {
    int64_t peak_index[PEAK_CAPACITY];
    double peak_amplitude[PEAK_CAPACITY];
    uint32_t peak_count = 0u;
    transient_table(instance, nominal, low, high, peak_index, peak_amplitude,
                    &peak_count);
    int have_transient = 0;
    key_type best_key = {0.0, 0, 0, 0};
    int64_t best_delta = low;
    for (int64_t delta = low; delta <= high; ++delta) {
        const int64_t start = nominal + delta;
        double amplitude = -1.0;
        int64_t index = -1;
        for (uint32_t peak = 0u; peak < peak_count; ++peak) {
            if (peak_index[peak] < start || peak_index[peak] >= start + (int64_t)HOP) {
                continue;
            }
            if (peak_amplitude[peak] > amplitude + AMPLITUDE_TIE_TOLERANCE ||
                (fabs(peak_amplitude[peak] - amplitude) <= AMPLITUDE_TIE_TOLERANCE &&
                 (index < 0 || peak_index[peak] < index))) {
                amplitude = peak_amplitude[peak];
                index = peak_index[peak];
            }
        }
        if (index < 0) continue;
        int64_t second = llabs(index - (start + (int64_t)TRANSIENT_TARGET_OFFSET));
        int64_t third = llabs((int64_t)delta);
        key_type candidate = {-amplitude, (int)second, (int)third, (int)delta};
        if (!have_transient || key_less(&candidate, &best_key)) {
            best_key = candidate;
            best_delta = delta;
            have_transient = 1;
        }
    }
    if (have_transient) return best_delta;

    int64_t chosen = low;
    double best_score = -1e300;
    for (int64_t delta = low; delta <= high; ++delta) {
        const double score = instance->segments
                                 ? similarity(instance, nominal + delta)
                                 : 0.0;
        int64_t third = llabs((int64_t)delta);
        if (score > best_score + SCORE_TIE_TOLERANCE ||
            (fabs(score - best_score) <= SCORE_TIE_TOLERANCE &&
             (third < llabs((int64_t)chosen) ||
              (third == llabs((int64_t)chosen) && delta < chosen)))) {
            best_score = score;
            chosen = delta;
        }
    }
    return chosen;
}

static void emit_samples(stretch_instance *instance, uint32_t count) {
    if (count == 0u || instance->flushed) return;
    for (uint32_t offset = 0u; offset < count; ++offset) {
        const int norm = instance->pending_norm[offset] > 1
                             ? instance->pending_norm[offset]
                             : 1;
        const double value = instance->pending[offset] / (double)norm;
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
                (SEGMENT - count) * sizeof(int));
        memmove(instance->pending_src, instance->pending_src + count,
                (SEGMENT - count) * sizeof(double));
        memset(instance->pending + (SEGMENT - count), 0, count * sizeof(double));
        memset(instance->pending_norm + (SEGMENT - count), 0, count * sizeof(int));
        for (uint32_t index = 0u; index < count; ++index) {
            instance->pending_src[SEGMENT - count + index] =
                (double)(instance->pending_start + (int64_t)SEGMENT + (int64_t)index);
        }
    } else {
        memset(instance->pending, 0, sizeof(instance->pending));
        memset(instance->pending_norm, 0, sizeof(instance->pending_norm));
        for (uint32_t index = 0u; index < SEGMENT; ++index) {
            instance->pending_src[index] =
                (double)(instance->pending_start + (int64_t)SEGMENT + (int64_t)index);
        }
    }
    instance->pending_start += (int64_t)count;
}

static void synthesize(stretch_instance *instance) {
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
            const int64_t source_index = base + (int64_t)index;
            if (source_index >= 0 &&
                source_index < instance->input_end - instance->input_start) {
                const double value = (double)instance->input[source_index];
                instance->pending[index] += value * (double)instance->window[index];
                instance->pending_norm[index] += (int)instance->window[index];
            }
            instance->pending_src[index] = (double)(effective_start + (int64_t)index);
        }
        const double previous_rate = instance->current_rate;
        const double target = rate_at(effective_start - instance->input_start);
        if (target > previous_rate) {
            const double advanced = previous_rate + RATE_SLEW_PER_SEGMENT;
            instance->current_rate = target < advanced ? target : advanced;
        } else {
            const double reduced = previous_rate - RATE_SLEW_PER_SEGMENT;
            instance->current_rate = target > reduced ? target : reduced;
        }
        instance->phase += llround_local((double)HOP * instance->current_rate *
                                         (double)PHASE_DENOMINATOR);
        instance->last_effective_start = effective_start;
        ++instance->segments;
    }
}

static void flush_engine(stretch_instance *instance) {
    if (instance->flushed) return;
    emit_samples(instance, SEGMENT);
    instance->flushed = 1u;
}

static as_status_v0 AS_CALL stretch_process(void *opaque,
                                            const as_frame_v0 *frame,
                                            const as_output_v0 *output,
                                            as_result_v0 *result) {
    stretch_instance *instance = (stretch_instance *)opaque;
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

    const double scaled = (double)frame->input_valid_count /
                          rate_at(frame->first_input_sample) + instance->rate_carry;
    long long wanted = llround_local(scaled);
    instance->rate_carry = scaled - (double)wanted;
    uint32_t target = wanted < 0 ? 0u : (uint32_t)wanted;
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

static as_status_v0 AS_CALL stretch_reset(void *opaque, uint64_t epoch,
                                          int64_t first_input_sample,
                                          as_error_v0 *error) {
    (void)error;
    stretch_instance *instance = (stretch_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL stretch_drain(void *opaque,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    stretch_instance *instance = (stretch_instance *)opaque;
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

static void AS_CALL stretch_destroy(void *opaque) { free(opaque); }

as_status_v0 soundtouch_reference_register(as_registry_v0 *registry,
                                          as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        stretch_create, stretch_process, stretch_reset, stretch_drain,
        stretch_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
