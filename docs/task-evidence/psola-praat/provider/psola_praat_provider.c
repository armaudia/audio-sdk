/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local PSOLA/Praat-style reference provider.
 *
 * It uses only the public v0 provider/session headers. It is not installed,
 * registered by default or linked into any shared SDK target. The engine is a
 * minimal pitch-synchronous overlap/add reference for deterministic synthetic
 * pulse stimuli: absolute-value pitch marks, Hann excision windows, overlap
 * denominator normalization and mark selection from a rate schedule. The v0
 * boundary still emits exactly 160 samples per process call; valid_count is
 * the only content-length signal, so this is a fixture adapter and not a
 * playback actuator. Slow-down is deliberately not exercised through v0.
 */
#include "audio_sdk/session_v0.h"
#include "psola_praat_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define PI 3.14159265358979323846
#define HALF_WINDOW 56
#define WINDOW_SIZE (2 * HALF_WINDOW + 1)
#define MIN_PERIOD 64
#define VOICING_THRESHOLD 0.045
#define PHASE_DENOMINATOR 1000000
#define SLEW_PER_MARK 0.05
#define RATE_MIN 0.75
#define RATE_MAX 1.50
#define MAX_ABS 1.0
#define EPS 1e-12
#define INPUT_CAPACITY 32768u
#define OUTPUT_CAPACITY 65536u
#define FIFO_CAPACITY 65536u
#define MARK_CAPACITY 8192u

static const struct rate_point {
    int64_t start;
    double rate;
} kSchedule[] = {
    {0, 1.0}, {4800, 1.25}, {8000, 1.0}, {11200, 1.5}
};
#define SCHEDULE_COUNT (sizeof(kSchedule) / sizeof(kSchedule[0]))

typedef struct psola_praat_instance_s {
    float input[INPUT_CAPACITY];
    int64_t input_end;
    int64_t input_position;
    int64_t marks[MARK_CAPACITY];
    int64_t periods[MARK_CAPACITY];
    int64_t selected[MARK_CAPACITY];
    double window[WINDOW_SIZE];
    double accumulator[OUTPUT_CAPACITY];
    double denominator[OUTPUT_CAPACITY];
    float fifo[FIFO_CAPACITY];
    uint32_t fifo_head;
    uint32_t fifo_count;
    uint64_t epoch;
    int64_t first_input_sample;
    int64_t emitted;
    uint32_t finalized;
    uint32_t flushed;
    uint32_t invalid_count;
} psola_praat_instance;

static double rate_at(int64_t position) {
    double rate = kSchedule[0].rate;
    for (uint32_t index = 0u; index < SCHEDULE_COUNT; ++index) {
        if (position >= kSchedule[index].start) rate = kSchedule[index].rate;
        else break;
    }
    return rate;
}

static void initialize_window(psola_praat_instance *instance) {
    for (uint32_t index = 0u; index < WINDOW_SIZE; ++index) {
        instance->window[index] =
            0.5 - 0.5 * cos(2.0 * PI * (double)index / (double)(WINDOW_SIZE - 1));
    }
}

static void reset_state(psola_praat_instance *instance, uint64_t epoch,
                        int64_t first_input_sample) {
    memset(instance, 0, sizeof(*instance));
    initialize_window(instance);
    instance->epoch = epoch;
    instance->first_input_sample = first_input_sample;
    instance->input_end = first_input_sample;
    instance->input_position = first_input_sample;
}

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0u || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL psola_praat_create(const as_create_config_v0 *config,
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
                        PSOLA_PRAAT_PROVIDER_ID, strlen(PSOLA_PRAAT_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    psola_praat_instance *instance =
        (psola_praat_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

/* Absolute-value local maxima with a minimum pitch period. */
static uint32_t detect_marks(psola_praat_instance *instance, uint32_t count) {
    uint32_t found = 0u;
    int64_t last = INT64_MIN / 4;
    for (uint32_t index = 1u; index + 1u < count; ++index) {
        const double current = fabs((double)instance->input[index]);
        if (current < VOICING_THRESHOLD) continue;
        if (current <= fabs((double)instance->input[index - 1u])) continue;
        if (current < fabs((double)instance->input[index + 1u])) continue;
        if ((int64_t)index - last < MIN_PERIOD) continue;
        if (found >= MARK_CAPACITY) return found;
        instance->marks[found++] = (int64_t)index;
        last = (int64_t)index;
    }
    for (uint32_t index = 0u; index + 1u < found; ++index) {
        instance->periods[index] = instance->marks[index + 1u] - instance->marks[index];
    }
    if (found > 1u) instance->periods[found - 1u] = instance->periods[found - 2u];
    return found;
}

static uint64_t select_marks(psola_praat_instance *instance, uint32_t mark_count,
                             int64_t *total_periods) {
    int64_t phase = 0;
    double current_rate = kSchedule[0].rate;
    uint64_t selected = 0u;
    *total_periods = 0;
    for (uint32_t index = 0u; index < mark_count; ++index) {
        const int64_t mark = instance->marks[index];
        const double target = rate_at(mark - instance->first_input_sample);
        if (target > current_rate) {
            current_rate = target < current_rate + SLEW_PER_MARK
                               ? target : current_rate + SLEW_PER_MARK;
        } else {
            current_rate = target > current_rate - SLEW_PER_MARK
                               ? target : current_rate - SLEW_PER_MARK;
        }
        phase += llround((double)PHASE_DENOMINATOR / current_rate);
        while (phase >= PHASE_DENOMINATOR) {
            phase -= PHASE_DENOMINATOR;
            if (selected >= MARK_CAPACITY) break;
            instance->selected[selected++] = (int64_t)index;
            *total_periods += instance->periods[index];
        }
    }
    return selected;
}

/* Returns the number of normalized output samples and writes them to output. */
static uint32_t synthesize(psola_praat_instance *instance, uint32_t count,
                           float *output, uint32_t capacity) {
    if (count < 2u) return 0u;
    const uint32_t mark_count = detect_marks(instance, count);
    if (mark_count < 2u) return 0u;
    int64_t total_periods = 0;
    const uint64_t selected = select_marks(instance, mark_count, &total_periods);
    if (selected == 0u) return 0u;

    const int64_t first_center = instance->marks[instance->selected[0]];
    const int64_t length = first_center + total_periods + HALF_WINDOW + 1;
    if (length <= 0 || (uint64_t)length > OUTPUT_CAPACITY) return 0u;
    memset(instance->accumulator, 0, (size_t)length * sizeof(double));
    memset(instance->denominator, 0, (size_t)length * sizeof(double));

    int64_t center = first_center;
    for (uint64_t index = 0u; index < selected; ++index) {
        const int64_t mark = instance->marks[instance->selected[index]];
        const int64_t period = instance->periods[instance->selected[index]];
        for (int64_t offset = -(int64_t)HALF_WINDOW; offset <= HALF_WINDOW; ++offset) {
            const int64_t source = mark + offset;
            if (source < 0 || source >= (int64_t)count) continue;
            const int64_t position = center + offset;
            const double weight = instance->window[offset + HALF_WINDOW];
            instance->accumulator[position] += (double)instance->input[source] * weight;
            instance->denominator[position] += weight;
        }
        center += period;
    }

    int64_t first = -1;
    int64_t last = -1;
    for (int64_t index = 0; index < length; ++index) {
        if (instance->denominator[index] > EPS) {
            if (first < 0) first = index;
            last = index;
        }
    }
    if (first < 0) return 0u;
    const int64_t result_count = last - first + 1;
    if (result_count < 0 || result_count > (int64_t)capacity) return 0u;
    for (int64_t index = first; index <= last; ++index) {
        const double weight = instance->denominator[index];
        output[index - first] = (float)(weight > EPS
                                            ? instance->accumulator[index] / weight
                                            : 0.0);
    }
    return (uint32_t)result_count;
}

static void fifo_push(psola_praat_instance *instance, const float *samples, uint32_t count) {
    for (uint32_t index = 0u; index < count; ++index) {
        if (instance->fifo_count >= FIFO_CAPACITY) return;
        instance->fifo[(instance->fifo_head + instance->fifo_count) % FIFO_CAPACITY] =
            samples[index];
        ++instance->fifo_count;
    }
}

static as_status_v0 AS_CALL psola_praat_process(void *opaque,
                                                const as_frame_v0 *frame,
                                                const as_output_v0 *output,
                                                as_result_v0 *result) {
    psola_praat_instance *instance = (psola_praat_instance *)opaque;
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
    const uint32_t appended = (uint32_t)(instance->input_end - instance->first_input_sample);
    if (appended + frame->input_valid_count > INPUT_CAPACITY) return AS_RESOURCE_EXHAUSTED;
    memcpy(instance->input + appended, frame->input,
           frame->input_valid_count * sizeof(float));
    instance->input_end += (int64_t)frame->input_valid_count;
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) instance->finalized = 1u;

    float synthesized[OUTPUT_CAPACITY];
    const uint32_t produced = synthesize(instance, appended + frame->input_valid_count,
                                         synthesized, OUTPUT_CAPACITY);
    if (produced < (uint32_t)instance->emitted) return AS_BACKEND_FAILURE;
    fifo_push(instance, synthesized + instance->emitted, produced - (uint32_t)instance->emitted);
    instance->emitted = produced;

    const double rate = rate_at(frame->first_input_sample - instance->first_input_sample);
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

static as_status_v0 AS_CALL psola_praat_reset(void *opaque, uint64_t epoch,
                                              int64_t first_input_sample,
                                              as_error_v0 *error) {
    (void)error;
    psola_praat_instance *instance = (psola_praat_instance *)opaque;
    if (instance == NULL || instance->finalized || instance->flushed ||
        epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL psola_praat_drain(void *opaque,
                                              const as_output_v0 *output,
                                              as_result_v0 *result) {
    psola_praat_instance *instance = (psola_praat_instance *)opaque;
    if (instance == NULL || output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    if (!instance->finalized) return AS_INVALID_ARGUMENT;
    const int64_t source = instance->input_position;
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
    instance->input_position = source + (int64_t)count;
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

static void AS_CALL psola_praat_destroy(void *opaque) { free(opaque); }

as_status_v0 psola_praat_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        psola_praat_create, psola_praat_process, psola_praat_reset, psola_praat_drain,
        psola_praat_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
