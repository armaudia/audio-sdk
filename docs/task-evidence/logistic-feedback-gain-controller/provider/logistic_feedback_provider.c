/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered reference for the pinned logistic feedback gain
 * controller and its static fallback. Uses only the public v0 provider table.
 * Coefficients are the deterministic synthetic-fixture model in ../model.json;
 * no real weights, downloads, assets or default registration are involved.
 */
#include "audio_sdk/session_v0.h"
#include "logistic_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define LOGISTIC_PI 3.14159265358979323846
#define LOGISTIC_FEATURES 7u
#define LOGISTIC_LOW_BIN 2u
#define LOGISTIC_HIGH_BIN 40u
#define LOGISTIC_BINS (LOGISTIC_HIGH_BIN - LOGISTIC_LOW_BIN)
#define LOGISTIC_PERSISTENCE 2
#define LOGISTIC_HOLD_FRAMES 75
#define LOGISTIC_REDUCTION_GAIN 0.7079457843841379
#define LOGISTIC_FLOOR_GAIN 0.2511886431509580
#define LOGISTIC_RECOVERY_GAIN 1.0146118723545769
#define LOGISTIC_STATIC_GAIN 0.5623413251903491

/* ../model.json, fixture a9bac04e5968ffdcb9d6c532236bd731f28a94a303135006fe6402474d0d62cc */
static const double kWeights[LOGISTIC_FEATURES] = {
    0.7667732539826794, -1.1174053814839557, 1.2945712042056907,
    -1.0269547087197997, -0.16540311079738135, -0.19675024004271233,
    0.6588895929072249};
static const double kMean[LOGISTIC_FEATURES] = {
    23.771106844101524, 0.06026974290918224, -3.7278799612962414,
    6.947502426591286, -0.08271422563840002, 0.8951851851851852,
    0.1659953703703665};
static const double kScale[LOGISTIC_FEATURES] = {
    14.396587347889014, 0.10315843882211546, 2.496205570256803,
    3.0330023079496304, 3.6725313656847733, 0.30631465751764836,
    0.08022100535887564};
static const double kIntercept = 1.8145658912377405;
static const double kThreshold = 0.04;

typedef struct logistic_instance_s {
    int static_only;
    double cosine[LOGISTIC_BINS][AS_FRAME_SAMPLES];
    double sine[LOGISTIC_BINS][AS_FRAME_SAMPLES];
    double window[AS_FRAME_SAMPLES];
    int previous_peak_bin;
    double previous_rms;
    int consecutive;
    int hold;
    double gain;
    uint64_t epoch;
    int64_t output_start;
    uint32_t detection_events;
    uint32_t gain_actions;
    int have_position;
} logistic_instance;

static void design_tables(logistic_instance *instance) {
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        instance->window[index] = 0.5 - 0.5 * cos(
            2.0 * LOGISTIC_PI * (double)index /
            (double)(AS_FRAME_SAMPLES - 1u));
    }
    for (uint32_t offset = 0; offset < LOGISTIC_BINS; ++offset) {
        const uint32_t bin = LOGISTIC_LOW_BIN + offset;
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            const double phase = 2.0 * LOGISTIC_PI * (double)bin *
                                 (double)index / (double)AS_FRAME_SAMPLES;
            instance->cosine[offset][index] = cos(phase);
            instance->sine[offset][index] = sin(phase);
        }
    }
}

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static as_status_v0 AS_CALL logistic_create(const as_create_config_v0 *config,
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
    if (!contains_bytes(config->config_json, config->config_json_length,
                        LOGISTIC_PROVIDER_ID, strlen(LOGISTIC_PROVIDER_ID)) &&
        !contains_bytes(config->config_json, config->config_json_length,
                        STATIC_PROVIDER_ID, strlen(STATIC_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    logistic_instance *instance = (logistic_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    instance->static_only = contains_bytes(
        config->config_json, config->config_json_length,
        STATIC_PROVIDER_ID, strlen(STATIC_PROVIDER_ID));
    design_tables(instance);
    instance->previous_peak_bin = -1;
    instance->gain = 1.0;
    instance->epoch = config->epoch;
    instance->output_start = config->first_input_sample;
    instance->have_position = 1;
    *out_instance = instance;
    return AS_OK;
}

static void frame_features(const logistic_instance *instance,
                           const float *input, double features[LOGISTIC_FEATURES],
                           int *peak_bin, double *rms) {
    double sum_squares = 0.0;
    double windowed[AS_FRAME_SAMPLES];
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double sample = (double)input[index];
        sum_squares += sample * sample;
        windowed[index] = sample * instance->window[index];
    }
    *rms = sqrt(sum_squares / (double)AS_FRAME_SAMPLES + 1e-18);

    double power[LOGISTIC_BINS];
    for (uint32_t offset = 0; offset < LOGISTIC_BINS; ++offset) {
        double real = 0.0;
        double imag = 0.0;
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            real += windowed[index] * instance->cosine[offset][index];
            imag -= windowed[index] * instance->sine[offset][index];
        }
        power[offset] = real * real + imag * imag;
    }
    uint32_t peak_offset = 0;
    for (uint32_t offset = 1; offset < LOGISTIC_BINS; ++offset) {
        if (power[offset] > power[peak_offset]) peak_offset = offset;
    }
    const uint32_t bin = LOGISTIC_LOW_BIN + peak_offset;
    *peak_bin = (int)bin;
    const double peak_power = power[peak_offset];

    double shoulders[8];
    uint32_t shoulder_count = 0;
    int left_start = (int)bin - 4;
    if (left_start < (int)LOGISTIC_LOW_BIN) left_start = (int)LOGISTIC_LOW_BIN;
    int left_stop = (int)bin - 1;
    if (left_stop < (int)LOGISTIC_LOW_BIN) left_stop = (int)LOGISTIC_LOW_BIN;
    for (int index = left_start; index < left_stop && shoulder_count < 8u; ++index)
        shoulders[shoulder_count++] = power[(uint32_t)index - LOGISTIC_LOW_BIN];
    int right_start = (int)bin + 2;
    if (right_start > (int)LOGISTIC_HIGH_BIN) right_start = (int)LOGISTIC_HIGH_BIN;
    int right_stop = (int)bin + 5;
    if (right_stop > (int)LOGISTIC_HIGH_BIN) right_stop = (int)LOGISTIC_HIGH_BIN;
    for (int index = right_start; index < right_stop && shoulder_count < 8u; ++index)
        shoulders[shoulder_count++] = power[(uint32_t)index - LOGISTIC_LOW_BIN];
    double shoulder_sum = 0.0;
    for (uint32_t index = 0; index < shoulder_count; ++index) shoulder_sum += shoulders[index];
    const double shoulder_mean = shoulder_count ? shoulder_sum / (double)shoulder_count : 1e-18;

    double band_sum = 0.0;
    double band_log_sum = 0.0;
    for (uint32_t offset = 0; offset < LOGISTIC_BINS; ++offset) {
        const double value = power[offset] > 1e-18 ? power[offset] : 1e-18;
        band_sum += value;
        band_log_sum += log(value);
    }
    double maximum_sample = 0.0;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double magnitude = fabs((double)input[index]);
        if (magnitude > maximum_sample) maximum_sample = magnitude;
    }
    const double growth = instance->previous_rms > 0.0
        ? 20.0 * log10((*rms + 1e-9) / (instance->previous_rms + 1e-9)) : 0.0;
    const int bin_difference = (int)bin - instance->previous_peak_bin;
    const double persistent = instance->previous_peak_bin >= 0 &&
        (bin_difference >= -1 && bin_difference <= 1) ? 1.0 : 0.0;

    features[0] = 10.0 * log10((peak_power + 1e-18) / (shoulder_mean + 1e-18));
    features[1] = exp(band_log_sum / (double)LOGISTIC_BINS) /
                  (band_sum / (double)LOGISTIC_BINS + 1e-18);
    features[2] = 10.0 * log10((peak_power + 1e-18) / (band_sum + 1e-18));
    features[3] = 20.0 * log10((maximum_sample + 1e-9) / (*rms + 1e-9));
    features[4] = growth;
    features[5] = persistent;
    features[6] = (double)bin / (double)(AS_FRAME_SAMPLES / 2u);
}

static as_status_v0 AS_CALL logistic_process(void *opaque,
                                             const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    logistic_instance *instance = (logistic_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        if (!isfinite((double)frame->input[index])) return AS_INVALID_ARGUMENT;
    }
    if (frame->input_count != AS_FRAME_SAMPLES ||
        frame->input_valid_count != AS_FRAME_SAMPLES ||
        !instance->have_position || frame->epoch != instance->epoch ||
        frame->first_input_sample != instance->output_start) {
        return AS_BACKEND_FAILURE;
    }

    if (!instance->static_only) {
        double features[LOGISTIC_FEATURES];
        int peak_bin = 0;
        double rms = 0.0;
        frame_features(instance, frame->input, features, &peak_bin, &rms);
        double z = kIntercept;
        for (uint32_t index = 0; index < LOGISTIC_FEATURES; ++index) {
            const double standardized = (features[index] - kMean[index]) / kScale[index];
            z += standardized * kWeights[index];
        }
        if (z > 40.0) z = 40.0;
        if (z < -40.0) z = -40.0;
        const double probability = 1.0 / (1.0 + exp(-z));
        if (probability >= kThreshold) {
            ++instance->consecutive;
        } else {
            instance->consecutive = 0;
        }
        if (instance->consecutive >= LOGISTIC_PERSISTENCE) {
            instance->gain *= LOGISTIC_REDUCTION_GAIN;
            if (instance->gain < LOGISTIC_FLOOR_GAIN) instance->gain = LOGISTIC_FLOOR_GAIN;
            instance->hold = LOGISTIC_HOLD_FRAMES;
            ++instance->detection_events;
            ++instance->gain_actions;
            instance->consecutive = 0;
        } else if (instance->hold) {
            --instance->hold;
        } else {
            instance->gain *= LOGISTIC_RECOVERY_GAIN;
            if (instance->gain > 1.0) instance->gain = 1.0;
        }
        instance->previous_peak_bin = peak_bin;
        instance->previous_rms = rms;
    }

    const double gain = instance->static_only ? LOGISTIC_STATIC_GAIN : instance->gain;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        output->samples[index] = (float)((double)frame->input[index] * gain);
    }
    instance->output_start += (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL logistic_reset(void *opaque, uint64_t epoch,
                                           int64_t first_input_sample,
                                           as_error_v0 *error) {
    (void)error;
    logistic_instance *instance = (logistic_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    instance->previous_peak_bin = -1;
    instance->previous_rms = 0.0;
    instance->consecutive = 0;
    instance->hold = 0;
    instance->gain = 1.0;
    instance->detection_events = 0;
    instance->gain_actions = 0;
    instance->epoch = epoch;
    instance->output_start = first_input_sample;
    instance->have_position = 1;
    return AS_OK;
}

static as_status_v0 AS_CALL logistic_drain(void *opaque,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    logistic_instance *instance = (logistic_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL logistic_destroy(void *opaque) { free(opaque); }

static as_status_v0 register_one(as_registry_v0 *registry,
                                 const char *descriptor, uint32_t descriptor_length,
                                 as_error_v0 *error) {
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        logistic_create, logistic_process, logistic_reset, logistic_drain,
        logistic_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, descriptor,
                                   descriptor_length, error);
}

as_status_v0 logistic_feedback_register(as_registry_v0 *registry,
                                        as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    as_status_v0 status = register_one(registry, kLogisticDescriptor,
                                       (uint32_t)(sizeof(kLogisticDescriptor) - 1u), error);
    if (status != AS_OK) return status;
    return register_one(registry, kStaticDescriptor,
                        (uint32_t)(sizeof(kStaticDescriptor) - 1u), error);
}
