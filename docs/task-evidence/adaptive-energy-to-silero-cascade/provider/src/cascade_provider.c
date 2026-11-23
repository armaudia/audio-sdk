/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered adaptive-energy -> Silero-cascade reference on the
 * public v0 provider table. The second stage is an explicitly MODEL-FREE STUB:
 * a smoothed analytic sigmoid on frame RMS. There are no Silero weights,
 * downloads, licensed runtime or real-model claims in this file.
 *
 * Audio is passed through unchanged. The analysis timeline is task-local
 * fixture evidence and is not part of the installed v0 ABI. This source is not
 * built, linked, installed or registered by the SDK unless an opt-in consumer
 * compiles it with AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE=ON.
 */
#include "audio_sdk/session_v0.h"
#include "cascade_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define CASCADE_MIN_DBFS (-55.0)
#define CASCADE_NOISE_MARGIN_DB (8.0)
#define CASCADE_NOISE_ALPHA (0.01)
#define CASCADE_NOISE_INIT_DBFS (-90.0)
#define CASCADE_PROBABILITY_SCALE_DB (3.0)
#define CASCADE_STUB_THRESHOLD_DBFS (-52.0)
#define CASCADE_STUB_SMOOTH_ALPHA (0.35)
#define CASCADE_STUB_ACTIVE_PROBABILITY (0.5)
#define CASCADE_GATE_SLEEP_PROBABILITY (0.10)
#define CASCADE_GATE_WAKE_PROBABILITY (0.50)
#define CASCADE_AGREE_SLEEP_FRAMES 3
#define CASCADE_CROSSCHECK_INTERVAL_FRAMES 50
#define CASCADE_ONSET_FRAMES 2
#define CASCADE_OFFSET_FRAMES 3
#define CASCADE_MAX_ABS_SAMPLE (4.0)
#define CASCADE_POWER_FLOOR 1.0e-12

typedef struct cascade_reference_s {
    double noise_dbfs;
    int agree_run;
    int gate_sleep;
    int sleep_frames;
    double stub_probability;
    int stub_has_state;
    int raw_run;
    int idle_run;
    int active;
    int64_t active_start;
    uint64_t epoch;
    int64_t expected_start;
} cascade_reference;

static int cascade_contains_bytes(const char *haystack, uint32_t length,
                                  const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static double cascade_sigmoid(double x) {
    if (x >= 40.0) return 1.0;
    if (x <= -40.0) return 0.0;
    return 1.0 / (1.0 + exp(-x));
}

static void cascade_reset_state(cascade_reference *instance, uint64_t epoch,
                                int64_t first_input_sample) {
    instance->noise_dbfs = CASCADE_NOISE_INIT_DBFS;
    instance->agree_run = 0;
    instance->gate_sleep = 0;
    instance->sleep_frames = 0;
    instance->stub_probability = 0.0;
    instance->stub_has_state = 0;
    instance->raw_run = 0;
    instance->idle_run = 0;
    instance->active = 0;
    instance->active_start = 0;
    instance->epoch = epoch;
    instance->expected_start = first_input_sample;
}

static as_status_v0 AS_CALL cascade_create(const as_create_config_v0 *config,
                                           void **out_instance,
                                           as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) {
        return AS_UNSUPPORTED;
    }
    if (config->asset_count != 0 || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!cascade_contains_bytes(config->config_json, config->config_json_length,
                                CASCADE_PROVIDER_ID, strlen(CASCADE_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    cascade_reference *instance = (cascade_reference *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    cascade_reset_state(instance, config->epoch, config->first_input_sample);
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL cascade_process(void *opaque,
                                            const as_frame_v0 *frame,
                                            const as_output_v0 *output,
                                            as_result_v0 *result) {
    cascade_reference *instance = (cascade_reference *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    const uint32_t count = frame->input_valid_count;
    if (frame->input_count != AS_FRAME_SAMPLES || count == 0 ||
        count > AS_FRAME_SAMPLES || (count < AS_FRAME_SAMPLES && !final)) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < count; ++index) {
        const double sample = (double)frame->input[index];
        if (!isfinite(sample) || sample > CASCADE_MAX_ABS_SAMPLE ||
            sample < -CASCADE_MAX_ABS_SAMPLE) {
            return AS_INVALID_ARGUMENT;
        }
    }
    if (frame->epoch != instance->epoch) return AS_INVALID_ARGUMENT;
    if (frame->first_input_sample != instance->expected_start) {
        return AS_BACKEND_FAILURE;
    }

    double power = 0.0;
    for (uint32_t index = 0; index < count; ++index) {
        const double sample = (double)frame->input[index];
        power += sample * sample;
    }
    power /= (double)count;
    const double rms = sqrt(power > CASCADE_POWER_FLOOR ? power : CASCADE_POWER_FLOOR);
    const double dbfs = 20.0 * log10(rms);
    const double threshold = fmax(CASCADE_MIN_DBFS,
                                  instance->noise_dbfs + CASCADE_NOISE_MARGIN_DB);
    const double gate_probability = cascade_sigmoid(
        (dbfs - threshold) / CASCADE_PROBABILITY_SCALE_DB);

    if (gate_probability <= CASCADE_GATE_SLEEP_PROBABILITY) {
        ++instance->agree_run;
    } else {
        instance->agree_run = 0;
    }
    if (instance->agree_run >= CASCADE_AGREE_SLEEP_FRAMES) {
        instance->gate_sleep = 1;
    }

    const int wake = gate_probability >= CASCADE_GATE_WAKE_PROBABILITY;
    if (wake) {
        instance->gate_sleep = 0;
        instance->sleep_frames = 0;
        instance->agree_run = 0;
    }

    int crosscheck = 0;
    if (instance->gate_sleep && !wake) {
        ++instance->sleep_frames;
        crosscheck = (instance->sleep_frames %
                      CASCADE_CROSSCHECK_INTERVAL_FRAMES) == 1;
    }

    const int stub_invoked = wake || crosscheck || !instance->gate_sleep;
    if (stub_invoked) {
        const double instantaneous = cascade_sigmoid(
            (dbfs - CASCADE_STUB_THRESHOLD_DBFS) / CASCADE_PROBABILITY_SCALE_DB);
        if (instance->stub_has_state) {
            instance->stub_probability =
                CASCADE_STUB_SMOOTH_ALPHA * instantaneous
                + (1.0 - CASCADE_STUB_SMOOTH_ALPHA) * instance->stub_probability;
        } else {
            instance->stub_probability = instantaneous;
            instance->stub_has_state = 1;
        }
    }
    const double cascade_probability =
        instance->gate_sleep ? 0.0 : instance->stub_probability;

    const int gate_active = gate_probability >= CASCADE_GATE_WAKE_PROBABILITY;
    if (!gate_active) {
        instance->noise_dbfs += CASCADE_NOISE_ALPHA * (dbfs - instance->noise_dbfs);
    }
    const int raw_active = cascade_probability >= CASCADE_STUB_ACTIVE_PROBABILITY;
    if (raw_active) {
        ++instance->raw_run;
        instance->idle_run = 0;
        if (!instance->active && instance->raw_run >= CASCADE_ONSET_FRAMES) {
            instance->active = 1;
            instance->active_start = frame->first_input_sample;
        }
    } else {
        ++instance->idle_run;
        instance->raw_run = 0;
        if (instance->active && instance->idle_run >= CASCADE_OFFSET_FRAMES) {
            instance->active = 0;
            instance->active_start = 0;
        }
    }
    if (final && instance->active) {
        instance->active = 0;
        instance->active_start = 0;
    }

    for (uint32_t index = 0; index < count; ++index) {
        output->samples[index] = frame->input[index];
    }
    for (uint32_t index = count; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = 0.0f;
    }
    instance->expected_start = frame->first_input_sample + (int64_t)count;

    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = count;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL cascade_reset(void *opaque, uint64_t epoch,
                                          int64_t first_input_sample,
                                          as_error_v0 *error) {
    (void)error;
    cascade_reference *instance = (cascade_reference *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    cascade_reset_state(instance, epoch, first_input_sample);
    return AS_OK;
}

static as_status_v0 AS_CALL cascade_drain(void *opaque,
                                          const as_output_v0 *output,
                                          as_result_v0 *result) {
    cascade_reference *instance = (cascade_reference *)opaque;
    (void)output;
    if (instance == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->expected_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL cascade_destroy(void *opaque) { free(opaque); }

as_status_v0 adaptive_energy_to_silero_cascade_register(as_registry_v0 *registry,
                                                        as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        cascade_create, cascade_process, cascade_reset, cascade_drain,
        cascade_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kCascadeDescriptor,
                                   sizeof(kCascadeDescriptor) - 1u, error);
}
