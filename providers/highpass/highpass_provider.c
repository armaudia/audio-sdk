/*
 * First-party second-order high-pass provider (dsp.highpass80.v0).
 *
 * Frozen for this provider ID: cutoff 80 Hz, Q 0.7071067811865476, double
 * precision filter state, float32 output, no clipping/limiter/VAD, and zero
 * buffering delay. The frequency-dependent phase response is part of the
 * transformation and is not an integer content delay.
 */
#include "audio_sdk/provider_v0.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct highpass_instance {
    double b0, b1, b2, a1, a2;
    double z1, z2;
    int64_t output_start;
    int64_t accepted_end;
    uint64_t epoch;
    int have_position;
} highpass_instance;

static int design(highpass_instance *instance) {
    const double cutoff = 80.0;
    const double q = 0.7071067811865476;
    const double rate = 16000.0;
    const double w0 = 2.0 * 3.14159265358979323846 * cutoff / rate;
    const double cos_w0 = cos(w0);
    const double alpha = sin(w0) / (2.0 * q);
    const double a0 = 1.0 + alpha;
    instance->b0 = ((1.0 + cos_w0) * 0.5) / a0;
    instance->b1 = (-(1.0 + cos_w0)) / a0;
    instance->b2 = ((1.0 + cos_w0) * 0.5) / a0;
    instance->a1 = (-2.0 * cos_w0) / a0;
    instance->a2 = (1.0 - alpha) / a0;
    return 1;
}

static as_status_v0 AS_CALL highpass_create(const as_create_config_v0 *config,
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
    highpass_instance *instance =
        (highpass_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    design(instance);
    instance->epoch = config->epoch;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL highpass_process(void *opaque, const as_frame_v0 *frame,
                                             const as_output_v0 *output,
                                             as_result_v0 *result) {
    highpass_instance *instance = (highpass_instance *)opaque;
    if (instance == NULL || frame == NULL || frame->input == NULL ||
        output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || result == NULL) {
        return AS_INVALID_ARGUMENT;
    }
    const int64_t source_first = frame->first_input_sample;
    if (!instance->have_position) {
        instance->output_start = source_first;
        instance->have_position = 1;
    }
    if (instance->output_start != source_first) return AS_BACKEND_FAILURE;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        const double x = (double)frame->input[i];
        const double y = instance->b0 * x + instance->z1;
        instance->z1 = instance->b1 * x - instance->a1 * y + instance->z2;
        instance->z2 = instance->b2 * x - instance->a2 * y;
        output->samples[i] = (float)y;
    }
    instance->accepted_end =
        frame->first_input_sample +
        (int64_t)((frame->flags & AS_FRAME_FINAL_INPUT)
                      ? frame->input_valid_count
                      : AS_FRAME_SAMPLES);
    instance->output_start += AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = source_first;
    return AS_OK;
}

static as_status_v0 AS_CALL highpass_reset(void *opaque, uint64_t epoch,
                                           int64_t first_input_sample,
                                           as_error_v0 *error) {
    (void)error;
    highpass_instance *instance = (highpass_instance *)opaque;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    instance->z1 = 0.0;
    instance->z2 = 0.0;
    instance->output_start = first_input_sample;
    instance->accepted_end = first_input_sample;
    instance->epoch = epoch;
    instance->have_position = 1;
    return AS_OK;
}

static as_status_v0 AS_CALL highpass_drain(void *opaque, const as_output_v0 *output,
                                           as_result_v0 *result) {
    highpass_instance *instance = (highpass_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL)
        return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL highpass_destroy(void *opaque) {
    free(opaque);
}

static const as_provider_table_v0 kHighpassTable = {
    (uint32_t)sizeof(as_provider_table_v0),
    AS_ABI_MAJOR,
    AS_ABI_MINOR,
    highpass_create,
    highpass_process,
    highpass_reset,
    highpass_drain,
    highpass_destroy,
    {0, 0, 0, 0}};

const as_provider_table_v0 *as_highpass_provider_table(void) {
    return &kHighpassTable;
}
