/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local granular time-stretch reference provider.
 *
 * It uses only the public v0 provider/session headers. It is not installed,
 * registered by default or linked into any shared SDK target. The engine is a
 * windowed-grain overlap-add time scaler with grain size, overlap and density
 * fixed by the caller's validated config. The v0 boundary still emits exactly
 * 160 samples per process call; valid_count is the only content-length signal,
 * so this is a fixture adapter and not a playback actuator.
 */
#include "audio_sdk/session_v0.h"
#include "granular_tsm_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define PI 3.14159265358979323846
#define GRAIN 512u
#define OVERLAP 384u
#define ANALYSIS_HOP (GRAIN - OVERLAP)
#define DENSITY 2u
#define SYNTH_HOP (ANALYSIS_HOP / DENSITY)
#define PHASE_DENOMINATOR 1000000
#define RATE_MIN 0.75
#define RATE_MAX 1.50
#define MAX_RATE_STEP 0.006
#define MAX_ABS 1.0
#define EPS 1e-12
#define INPUT_CAPACITY 65536u
#define FIFO_CAPACITY 65536u

static const struct rate_point {
    int64_t start;
    double rate;
} kSchedule[] = {
    {0, 1.0}, {3600, 1.25}, {7200, 1.0}, {10000, 1.5}
};
#define SCHEDULE_COUNT (sizeof(kSchedule) / sizeof(kSchedule[0]))

typedef struct granular_tsm_instance_s {
    float input[INPUT_CAPACITY];
    int64_t input_start;
    int64_t input_end;
    int64_t phase;
    double current_rate;
    double target_rate;
    double pending[GRAIN];
    double pending_norm[GRAIN];
    double window[GRAIN];
    int64_t pending_start;
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
} granular_tsm_instance;

static double rate_at(int64_t relative_position) {
    double rate = kSchedule[0].rate;
    for (uint32_t index = 0u; index < SCHEDULE_COUNT; ++index) {
        if (relative_position >= kSchedule[index].start) rate = kSchedule[index].rate;
        else break;
    }
    return rate;
}

static void initialize_window(granular_tsm_instance *instance) {
    for (uint32_t index = 0u; index < GRAIN; ++index) {
        instance->window[index] =
            0.5 - 0.5 * cos(2.0 * PI * (double)index / (double)(GRAIN - 1u));
    }
}

static void reset_state(granular_tsm_instance *instance, uint64_t epoch,
                        int64_t first_input_sample) {
    memset(instance, 0, sizeof(*instance));
    initialize_window(instance);
    instance->input_start = first_input_sample;
    instance->input_end = first_input_sample;
    instance->current_rate = kSchedule[0].rate;
    instance->target_rate = kSchedule[0].rate;
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

static as_status_v0 AS_CALL granular_tsm_create(const as_create_config_v0 *config,
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
    if (!contains_bytes(json, length, GRANULAR_TSM_PROVIDER_ID,
                        strlen(GRANULAR_TSM_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    /* Parameter validation lives in the task-local config/reference layer;
       the effective v0 config carries the pinned descriptor digest, not a
       user-settings object. The engine constants are fixed by this fixture. */
    granular_tsm_instance *instance =
        (granular_tsm_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static void emit_samples(granular_tsm_instance *instance, uint32_t count) {
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
    if (count < GRAIN) {
        memmove(instance->pending, instance->pending + count,
                (GRAIN - count) * sizeof(double));
        memmove(instance->pending_norm, instance->pending_norm + count,
                (GRAIN - count) * sizeof(double));
        memset(instance->pending + (GRAIN - count), 0, count * sizeof(double));
        memset(instance->pending_norm + (GRAIN - count), 0, count * sizeof(double));
    } else {
        memset(instance->pending, 0, sizeof(instance->pending));
        memset(instance->pending_norm, 0, sizeof(instance->pending_norm));
    }
    instance->pending_start += (int64_t)count;
}

static void synthesize(granular_tsm_instance *instance) {
    for (;;) {
        const int64_t nominal =
            instance->phase / PHASE_DENOMINATOR + instance->input_start;
        if (nominal + (int64_t)GRAIN > instance->input_end) return;
        if (instance->segments > 0u) emit_samples(instance, SYNTH_HOP);
        const int64_t base = nominal - instance->input_start;
        for (uint32_t index = 0u; index < GRAIN; ++index) {
            const double value = (double)instance->input[base + index] *
                                 instance->window[index];
            instance->pending[index] += value;
            instance->pending_norm[index] += instance->window[index];
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
                                   PHASE_DENOMINATOR);
        ++instance->segments;
    }
}

static void flush_engine(granular_tsm_instance *instance) {
    if (instance->flushed) return;
    emit_samples(instance, GRAIN);
    instance->flushed = 1u;
}

static as_status_v0 AS_CALL granular_tsm_process(void *opaque,
                                                const as_frame_v0 *frame,
                                                const as_output_v0 *output,
                                                as_result_v0 *result) {
    granular_tsm_instance *instance = (granular_tsm_instance *)opaque;
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

static as_status_v0 AS_CALL granular_tsm_reset(void *opaque, uint64_t epoch,
                                               int64_t first_input_sample,
                                               as_error_v0 *error) {
    (void)error;
    granular_tsm_instance *instance = (granular_tsm_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL granular_tsm_drain(void *opaque,
                                              const as_output_v0 *output,
                                              as_result_v0 *result) {
    granular_tsm_instance *instance = (granular_tsm_instance *)opaque;
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

static void AS_CALL granular_tsm_destroy(void *opaque) { free(opaque); }

as_status_v0 granular_tsm_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        granular_tsm_create, granular_tsm_process, granular_tsm_reset,
        granular_tsm_drain, granular_tsm_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
