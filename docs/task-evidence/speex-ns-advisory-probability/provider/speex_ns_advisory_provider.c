/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered task-local advisory-probability reference.
 *
 * It uses only the public v0 provider/session headers for audio processing.
 * The advisory probability is fixed-point evidence carried by a task-local
 * side channel; it is NOT a control signal, a detector, a calibrated posterior
 * or upstream SpeexDSP code. No upstream source is vendored here.
 */
#include "audio_sdk/session_v0.h"
#include "speex_ns_advisory_analysis.h"
#include "speex_ns_advisory_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define Q15_SCALE 32768.0f
#define NOISE_FLOOR 2000000ull
#define PROBABILITY_SPAN 8000000ull
#define MILLI_MAX 1000u
#define EVENT_CAPACITY 128u

typedef struct advisory_instance_s {
    float previous[AS_FRAME_SAMPLES];
    uint32_t have_previous;
    uint32_t sequence;
    uint32_t invalid_count;
    uint64_t epoch;
    int64_t expected_first;
    uint32_t have_position;
    as_speex_ns_advisory_event_v0 events[2u][EVENT_CAPACITY];
    uint32_t event_count[2u];
} advisory_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0u || needle_length > length) return 0;
    for (uint32_t index = 0u; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void reset_state(advisory_instance *instance, uint64_t epoch,
                        int64_t first_input_sample) {
    memset(instance, 0, sizeof(*instance));
    instance->epoch = epoch;
    instance->expected_first = first_input_sample;
    instance->have_position = 1u;
    instance->sequence = 1u;
}

static as_status_v0 AS_CALL advisory_create(const as_create_config_v0 *config,
                                            void **out_instance,
                                            as_error_v0 *error) {
    (void)error;
    if (config == NULL || out_instance == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES ||
        config->execution_mode != AS_MODE_PROCESSING_THREAD) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        AS_SPEEX_NS_ADVISORY_PROVIDER_ID,
                        strlen(AS_SPEEX_NS_ADVISORY_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    advisory_instance *instance = (advisory_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static uint32_t advisory_probability_milli(const float *window) {
    uint64_t energy = 0u;
    for (uint32_t index = 0u; index < AS_SPEEX_NS_ADVISORY_WINDOW_SAMPLES; ++index) {
        const int32_t q15 = (int32_t)(window[index] * Q15_SCALE);
        const int64_t squared = (int64_t)q15 * (int64_t)q15;
        energy += (uint64_t)squared;
    }
    const uint64_t mean = energy / (uint64_t)AS_SPEEX_NS_ADVISORY_WINDOW_SAMPLES;
    if (mean <= NOISE_FLOOR) return 0u;
    const uint64_t raw = ((mean - NOISE_FLOOR) * 1000ull) / PROBABILITY_SPAN;
    return raw > (uint64_t)MILLI_MAX ? MILLI_MAX : (uint32_t)raw;
}

static void emit_events(advisory_instance *instance, const float *window,
                        uint64_t epoch, int64_t first, int64_t end) {
    if (instance->sequence >= EVENT_CAPACITY) return;
    const uint32_t value = advisory_probability_milli(window);
    const int64_t available = 1000000000ll + end * (int64_t)62500;
    for (uint32_t hop = 0u; hop < 2u; ++hop) {
        as_speex_ns_advisory_event_v0 *event =
            &instance->events[hop][instance->event_count[hop]];
        memset(event, 0, sizeof(*event));
        event->schema_version = 1u;
        event->sequence = instance->sequence;
        event->hop = hop;
        event->value_milli = value;
        event->validity = AS_SPEEX_NS_ADVISORY_VALIDITY_KNOWN;
        event->epoch = epoch;
        event->source_first_sample = first;
        event->source_end_sample = end;
        event->available_monotonic_ns =
            available + (hop == 0u ? 0 : (int64_t)AS_FRAME_SAMPLES * 62500);
        memcpy(event->config_digest, SPEEX_NS_ADVISORY_CONFIG_DIGEST,
               sizeof(event->config_digest) - 1u);
        ++instance->event_count[hop];
    }
    ++instance->sequence;
}

static as_status_v0 AS_CALL advisory_process(void *opaque, const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    advisory_instance *instance = (advisory_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t valid = frame->input_valid_count;
    if (frame->input_count != AS_FRAME_SAMPLES || valid == 0u || valid > AS_FRAME_SAMPLES) {
        instance->invalid_count++;
        return AS_INVALID_ARGUMENT;
    }
    if ((frame->flags & ~AS_FRAME_FINAL_INPUT) != 0u) {
        instance->invalid_count++;
        return AS_INVALID_ARGUMENT;
    }
    if ((frame->flags & AS_FRAME_FINAL_INPUT) == 0u && valid != AS_FRAME_SAMPLES) {
        instance->invalid_count++;
        return AS_INVALID_ARGUMENT;
    }
    if ((frame->flags & AS_FRAME_FINAL_INPUT) != 0u) {
        for (uint32_t index = valid; index < AS_FRAME_SAMPLES; ++index) {
            if (frame->input[index] != 0.0f) {
                instance->invalid_count++;
                return AS_INVALID_ARGUMENT;
            }
        }
    }
    for (uint32_t index = 0u; index < valid; ++index) {
        if (!isfinite((double)frame->input[index])) {
            instance->invalid_count++;
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch) {
        instance->invalid_count++;
        return AS_INVALID_ARGUMENT;
    }
    if (!instance->have_position || frame->first_input_sample != instance->expected_first) {
        instance->invalid_count++;
        return AS_INVALID_ARGUMENT;
    }

    float current[AS_FRAME_SAMPLES];
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        current[index] = index < valid ? frame->input[index] : 0.0f;
        output->samples[index] = current[index];
    }
    const uint32_t emit = instance->have_previous;
    if (emit) {
        float window[AS_SPEEX_NS_ADVISORY_WINDOW_SAMPLES];
        memcpy(window, instance->previous, sizeof(instance->previous));
        memcpy(window + AS_FRAME_SAMPLES, current, sizeof(current));
        emit_events(instance, window, frame->epoch,
                    frame->first_input_sample - (int64_t)AS_FRAME_SAMPLES,
                    frame->first_input_sample + (int64_t)AS_FRAME_SAMPLES);
        instance->have_previous = 0u;
    }
    memcpy(instance->previous, current, sizeof(current));
    if (!emit) instance->have_previous = 1u;
    instance->expected_first = frame->first_input_sample + (int64_t)AS_FRAME_SAMPLES;

    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = valid;
    result->flags = 0u;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL advisory_reset(void *opaque, uint64_t epoch,
                                           int64_t first_input_sample,
                                           as_error_v0 *error) {
    (void)error;
    advisory_instance *instance = (advisory_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL advisory_drain(void *opaque, const as_output_v0 *output,
                                           as_result_v0 *result) {
    advisory_instance *instance = (advisory_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->expected_first;
    return AS_END_OF_STREAM;
}

static void AS_CALL advisory_destroy(void *opaque) {
    free(opaque);
}

static const as_provider_table_v0 kAdvisoryTable = {
    (uint32_t)sizeof(as_provider_table_v0),
    AS_ABI_MAJOR,
    AS_ABI_MINOR,
    advisory_create,
    advisory_process,
    advisory_reset,
    advisory_drain,
    advisory_destroy,
    {0, 0, 0, 0}};

const as_provider_table_v0 *as_speex_ns_advisory_table_v0(void) {
    return &kAdvisoryTable;
}

as_status_v0 as_speex_ns_advisory_register_v0(as_registry_v0 *registry,
                                              as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    return as_register_provider_v0(registry, &kAdvisoryTable,
                                   kDescriptor, (uint32_t)(sizeof(kDescriptor) - 1u),
                                   error);
}

uint32_t as_speex_ns_advisory_event_count_v0(const void *instance, uint32_t hop) {
    const advisory_instance *state = (const advisory_instance *)instance;
    if (state == NULL || hop > 1u) return 0u;
    return state->event_count[hop];
}

as_status_v0 as_speex_ns_advisory_event_at_v0(const void *instance, uint32_t hop,
                                              uint32_t index,
                                              as_speex_ns_advisory_event_v0 *out) {
    const advisory_instance *state = (const advisory_instance *)instance;
    if (state == NULL || out == NULL || hop > 1u || index >= state->event_count[hop]) {
        return AS_INVALID_ARGUMENT;
    }
    *out = state->events[hop][index];
    return AS_OK;
}

uint32_t as_speex_ns_advisory_invalid_count_v0(const void *instance) {
    const advisory_instance *state = (const advisory_instance *)instance;
    return state == NULL ? 0u : state->invalid_count;
}
