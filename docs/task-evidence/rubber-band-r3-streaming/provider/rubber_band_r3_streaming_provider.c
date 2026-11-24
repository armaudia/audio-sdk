/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local synthetic streaming time-stretch provider.
 *
 * It uses only the public v0 provider/session headers. It is not installed,
 * registered by default or linked into any shared SDK target. The engine is a
 * trial-clock overlap-add time scaler with a bounded, strictly causal backward
 * alignment search in the style of WSOLA. It is not Rubber Band code, a binary,
 * weights, a licensed runtime, a playback actuator or a perceptual measurement.
 *
 * The fixed v0 boundary emits exactly 160 samples per process call; valid_count
 * is the only content-length signal, so this is a fixture adapter and not a
 * playback actuator. Expansion and drain visibility are recorded in the Python
 * report instead of being claimed at this boundary.
 */
#include "audio_sdk/session_v0.h"
#include "rubber_band_r3_streaming_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define GRAIN 512u
#define OVERLAP 384u
#define ANALYSIS_HOP (GRAIN - OVERLAP)
#define DENSITY 2u
#define SYNTH_HOP (ANALYSIS_HOP / DENSITY)
#define PHASE_DENOMINATOR 1000000
#define SEARCH_RANGE 32
#define SEARCH_LEN 128u
#define REF_OFFSET ((GRAIN - SEARCH_LEN) / 2u)
#define RATE_MIN 0.75
#define RATE_MAX 1.50
#define MAX_RATE_STEP 0.02
#define MAX_ABS 1.0
#define EPS 1e-12
#define INPUT_CAPACITY 65536u
#define FIFO_CAPACITY 65536u

static const struct rate_point {
    int64_t start;
    double rate;
} kSchedule[] = {
    {0, 1.0}, {3200, 1.25}, {6400, 1.0}, {9600, 1.5}
};
#define SCHEDULE_COUNT (sizeof(kSchedule) / sizeof(kSchedule[0]))

typedef struct rb3_instance_s {
    float input[INPUT_CAPACITY];
    int64_t input_start;
    int64_t input_end;
    int64_t phase;
    double current_rate;
    double target_rate;
    double pending[GRAIN];
    double pending_norm[GRAIN];
    double window[GRAIN];
    int64_t pending_src[GRAIN];
    int64_t pending_start;
    uint32_t segments;
    float fifo[FIFO_CAPACITY];
    int64_t fifo_src[FIFO_CAPACITY];
    uint32_t fifo_head;
    uint32_t fifo_count;
    uint32_t finalized;
    uint32_t flushed;
    uint64_t epoch;
    int64_t input_position;
    int64_t output_position;
    uint32_t invalid_count;
} rb3_instance;

static double rate_at(int64_t relative_position) {
    double rate = kSchedule[0].rate;
    for (uint32_t index = 0u; index < SCHEDULE_COUNT; ++index) {
        if (relative_position >= kSchedule[index].start) rate = kSchedule[index].rate;
        else break;
    }
    return rate;
}

static void initialize_window(rb3_instance *instance) {
    const uint32_t half = (GRAIN + 1u) / 2u;
    for (uint32_t index = 0u; index < GRAIN; ++index) {
        const uint32_t numerator = index < half ? index + 1u : GRAIN - index;
        instance->window[index] = (double)numerator / (double)half;
    }
}

static void reset_state(rb3_instance *instance, uint64_t epoch,
                        int64_t first_input_sample) {
    memset(instance, 0, sizeof(*instance));
    initialize_window(instance);
    instance->input_start = first_input_sample;
    instance->input_end = first_input_sample;
    instance->current_rate = kSchedule[0].rate;
    instance->target_rate = kSchedule[0].rate;
    instance->pending_start = first_input_sample;
    for (uint32_t index = 0u; index < GRAIN; ++index) {
        instance->pending_src[index] = first_input_sample + (int64_t)index;
    }
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

static as_status_v0 AS_CALL rb3_create(const as_create_config_v0 *config,
                                       void **out_instance,
                                       as_error_v0 *error) {
    (void)error;
    if (config == NULL || out_instance == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    const char *json = config->config_json;
    const uint32_t length = config->config_json_length;
    if (!contains_bytes(json, length, RB3_PROVIDER_ID,
                        strlen(RB3_PROVIDER_ID))) return AS_INVALID_ARGUMENT;
    rb3_instance *instance = (rb3_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static void emit_samples(rb3_instance *instance, uint32_t count) {
    if (count == 0u || instance->flushed) return;
    for (uint32_t offset = 0u; offset < count; ++offset) {
        const double norm = instance->pending_norm[offset] > EPS
                                ? instance->pending_norm[offset]
                                : EPS;
        const double value = instance->pending[offset] / norm;
        if (instance->fifo_count < FIFO_CAPACITY) {
            const uint32_t tail =
                (instance->fifo_head + instance->fifo_count) % FIFO_CAPACITY;
            instance->fifo[tail] = (float)value;
            instance->fifo_src[tail] = instance->pending_src[offset];
            ++instance->fifo_count;
        }
    }
    if (count < GRAIN) {
        const uint32_t kept = GRAIN - count;
        memmove(instance->pending, instance->pending + count,
                kept * sizeof(double));
        memmove(instance->pending_norm, instance->pending_norm + count,
                kept * sizeof(double));
        memmove(instance->pending_src, instance->pending_src + count,
                kept * sizeof(int64_t));
        memset(instance->pending + kept, 0, count * sizeof(double));
        memset(instance->pending_norm + kept, 0, count * sizeof(double));
        for (uint32_t index = 0u; index < count; ++index) {
            instance->pending_src[kept + index] =
                instance->pending_start + (int64_t)GRAIN + (int64_t)index;
        }
    } else {
        memset(instance->pending, 0, sizeof(instance->pending));
        memset(instance->pending_norm, 0, sizeof(instance->pending_norm));
        memset(instance->pending_src, 0, sizeof(instance->pending_src));
    }
    instance->pending_start += (int64_t)count;
}

static int64_t search_delta(const rb3_instance *instance, int64_t base) {
    int have_best = 0;
    int64_t best_delta = 0;
    double best_score = 0.0;
    for (int64_t delta = 0; delta >= -SEARCH_RANGE; --delta) {
        const int64_t candidate = base + delta;
        if (candidate < 0) continue;
        double score = 0.0;
        for (uint32_t offset = 0u; offset < SEARCH_LEN; ++offset) {
            score += (double)instance->input[candidate + REF_OFFSET + offset] *
                     (double)instance->input[base + REF_OFFSET + offset];
        }
        if (!have_best || score > best_score) {
            have_best = 1;
            best_score = score;
            best_delta = delta;
        }
    }
    return best_delta;
}

static void synthesize(rb3_instance *instance) {
    for (;;) {
        const int64_t nominal =
            instance->phase / PHASE_DENOMINATOR + instance->input_start;
        const int64_t base = nominal - instance->input_start;
        if (nominal + (int64_t)GRAIN > instance->input_end) return;
        if (instance->segments > 0u) emit_samples(instance, SYNTH_HOP);
        const int64_t delta = search_delta(instance, base);
        const int64_t candidate = base + delta;
        for (uint32_t index = 0u; index < GRAIN; ++index) {
            const double weight = instance->window[index];
            instance->pending[index] +=
                (double)instance->input[candidate + index] * weight;
            instance->pending_norm[index] += weight;
            instance->pending_src[index] =
                instance->input_start + candidate + (int64_t)index;
        }
        const double previous_rate = instance->current_rate;
        const double target = rate_at(base);
        const double difference = target - previous_rate;
        if (fabs(difference) <= MAX_RATE_STEP) {
            instance->current_rate = target;
        } else {
            instance->current_rate = previous_rate +
                (difference > 0.0 ? MAX_RATE_STEP : -MAX_RATE_STEP);
        }
        instance->target_rate = target;
        instance->phase += llround((double)SYNTH_HOP * instance->current_rate *
                                   (double)PHASE_DENOMINATOR);
        ++instance->segments;
    }
}

static void flush_engine(rb3_instance *instance) {
    if (instance->flushed) return;
    emit_samples(instance, GRAIN);
    instance->flushed = 1u;
}

static as_status_v0 AS_CALL rb3_process(void *opaque,
                                        const as_frame_v0 *frame,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    rb3_instance *instance = (rb3_instance *)opaque;
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
    if (appended + frame->input_valid_count > INPUT_CAPACITY) {
        return AS_RESOURCE_EXHAUSTED;
    }
    memcpy(instance->input + appended, frame->input,
           frame->input_valid_count * sizeof(float));
    instance->input_end += (int64_t)frame->input_valid_count;
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) instance->finalized = 1u;
    synthesize(instance);
    if (instance->finalized) flush_engine(instance);

    const int64_t relative_first = frame->first_input_sample - instance->input_start;
    const double rate = rate_at(relative_first);
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

static as_status_v0 AS_CALL rb3_reset(void *opaque, uint64_t epoch,
                                      int64_t first_input_sample,
                                      as_error_v0 *error) {
    (void)error;
    rb3_instance *instance = (rb3_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL rb3_drain(void *opaque,
                                      const as_output_v0 *output,
                                      as_result_v0 *result) {
    rb3_instance *instance = (rb3_instance *)opaque;
    if (instance == NULL || output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (!instance->finalized) return AS_INVALID_ARGUMENT;
    /* The fixed v0 boundary cannot emit r<1 expansion or synthesized tail as
     * variable-length content. Python records the remaining FIFO depth as
     * drain_non_content_samples; drain reports completion without inventing a
     * playback actuator. */
    (void)instance;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_position;
    return AS_END_OF_STREAM;
}

static void AS_CALL rb3_destroy(void *opaque) { free(opaque); }

as_status_v0 rubber_band_r3_streaming_register(as_registry_v0 *registry,
                                               as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        rb3_create, rb3_process, rb3_reset, rb3_drain, rb3_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
