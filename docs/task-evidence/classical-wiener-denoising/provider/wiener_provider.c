/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Optional, unregistered classical Wiener denoising reference.
 *
 * Uses only the public v0 provider/session headers. It is task-local source:
 * not installed, registered by default, or linked into any shared SDK target.
 * The DSP mirrors the deterministic Python fixture's causal 256-point frame
 * filter; it is a boundary smoke reference, not a quality or timing claim.
 */
#include "audio_sdk/session_v0.h"
#include "wiener_descriptor.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define WIENER_FFT 256u
#define WIENER_BINS (WIENER_FFT / 2u + 1u)
#define WIENER_NOISE_FRAMES 10u
#define WIENER_SMOOTHING 0.7
#define WIENER_RISE 1.005
#define WIENER_OVERSUBTRACT 1.0
#define WIENER_GAIN_FLOOR 0.1
#define WIENER_MAX_ABS 4.0
#define WIENER_PI 3.14159265358979323846

typedef struct wiener_complex_s {
    double re;
    double im;
} wiener_complex;

typedef struct wiener_instance_s {
    double noise_psd[WIENER_BINS];
    double power_psd[WIENER_BINS];
    uint32_t frames_processed;
    uint32_t calibration_frames;
    uint32_t invalid_count;
    uint64_t epoch;
    int64_t output_start;
} wiener_instance;

static int contains_bytes(const char *haystack, uint32_t length,
                          const char *needle, size_t needle_length) {
    if (haystack == NULL || needle_length == 0 || needle_length > length) return 0;
    for (uint32_t index = 0; index + needle_length <= length; ++index) {
        if (memcmp(haystack + index, needle, needle_length) == 0) return 1;
    }
    return 0;
}

static void wiener_fft(wiener_complex *values, int inverse) {
    for (uint32_t i = 1u, j = 0u; i < WIENER_FFT; ++i) {
        uint32_t bit = WIENER_FFT >> 1;
        while (j & bit) {
            j ^= bit;
            bit >>= 1;
        }
        j |= bit;
        if (i < j) {
            const wiener_complex swap = values[i];
            values[i] = values[j];
            values[j] = swap;
        }
    }
    for (uint32_t length = 2u; length <= WIENER_FFT; length <<= 1u) {
        const double angle = (2.0 * WIENER_PI / (double)length) * (inverse ? 1.0 : -1.0);
        const wiener_complex root = {cos(angle), sin(angle)};
        const uint32_t half = length >> 1u;
        for (uint32_t start = 0u; start < WIENER_FFT; start += length) {
            wiener_complex twiddle = {1.0, 0.0};
            for (uint32_t offset = 0u; offset < half; ++offset) {
                const wiener_complex even = values[start + offset];
                const wiener_complex odd = {
                    values[start + offset + half].re * twiddle.re -
                        values[start + offset + half].im * twiddle.im,
                    values[start + offset + half].re * twiddle.im +
                        values[start + offset + half].im * twiddle.re
                };
                values[start + offset].re = even.re + odd.re;
                values[start + offset].im = even.im + odd.im;
                values[start + offset + half].re = even.re - odd.re;
                values[start + offset + half].im = even.im - odd.im;
                const double next_re = twiddle.re * root.re - twiddle.im * root.im;
                twiddle.im = twiddle.re * root.im + twiddle.im * root.re;
                twiddle.re = next_re;
            }
        }
    }
    if (inverse) {
        for (uint32_t index = 0u; index < WIENER_FFT; ++index) {
            values[index].re /= (double)WIENER_FFT;
            values[index].im /= (double)WIENER_FFT;
        }
    }
}

static as_status_v0 AS_CALL wiener_create(const as_create_config_v0 *config,
                                          void **out_instance,
                                          as_error_v0 *error) {
    (void)error;
    if (out_instance == NULL || config == NULL) return AS_INVALID_ARGUMENT;
    *out_instance = NULL;
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS ||
        config->frame_samples != AS_FRAME_SAMPLES) return AS_UNSUPPORTED;
    if (config->asset_count != 0u || config->assets != NULL) return AS_INVALID_ARGUMENT;
    if (!contains_bytes(config->config_json, config->config_json_length,
                        WIENER_PROVIDER_ID, strlen(WIENER_PROVIDER_ID))) {
        return AS_INVALID_ARGUMENT;
    }
    wiener_instance *instance = (wiener_instance *)calloc(1u, sizeof(*instance));
    if (instance == NULL) return AS_RESOURCE_EXHAUSTED;
    for (uint32_t bin = 0u; bin < WIENER_BINS; ++bin) instance->noise_psd[bin] = 1e-10;
    instance->epoch = config->epoch;
    instance->output_start = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 AS_CALL wiener_process(void *opaque,
                                           const as_frame_v0 *frame,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    wiener_instance *instance = (wiener_instance *)opaque;
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
        frame->first_input_sample != instance->output_start) {
        ++instance->invalid_count;
        return AS_INVALID_ARGUMENT;
    }

    wiener_complex spectrum[WIENER_FFT];
    for (uint32_t index = 0u; index < WIENER_FFT; ++index) {
        const double sample = index < AS_FRAME_SAMPLES ? (double)frame->input[index] : 0.0;
        if (!isfinite(sample) || fabs(sample) > WIENER_MAX_ABS) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
        spectrum[index].re = sample;
        spectrum[index].im = 0.0;
    }
    wiener_fft(spectrum, 0);

    double power[WIENER_BINS];
    double smoothed[WIENER_BINS];
    for (uint32_t bin = 0u; bin < WIENER_BINS; ++bin) {
        power[bin] = spectrum[bin].re * spectrum[bin].re +
                     spectrum[bin].im * spectrum[bin].im;
        smoothed[bin] = instance->frames_processed == 0u
                            ? power[bin]
                            : WIENER_SMOOTHING * power[bin] +
                                  (1.0 - WIENER_SMOOTHING) * instance->power_psd[bin];
    }
    memcpy(instance->power_psd, smoothed, sizeof(smoothed));

    double gains[WIENER_FFT];
    if (instance->frames_processed < WIENER_NOISE_FRAMES) {
        const double blend = 1.0 / (double)(instance->frames_processed + 1u);
        for (uint32_t bin = 0u; bin < WIENER_BINS; ++bin) {
            instance->noise_psd[bin] += blend * (smoothed[bin] - instance->noise_psd[bin]);
            gains[bin] = 1.0;
        }
        ++instance->calibration_frames;
    } else {
        for (uint32_t bin = 0u; bin < WIENER_BINS; ++bin) {
            const double fresh = smoothed[bin] > 1e-12 ? smoothed[bin] : 1e-12;
            const double tracked = instance->noise_psd[bin] * WIENER_RISE;
            instance->noise_psd[bin] = tracked < fresh ? tracked : fresh;
            double gain = 1.0 - WIENER_OVERSUBTRACT * instance->noise_psd[bin] /
                                    (smoothed[bin] + 1e-20);
            if (gain < WIENER_GAIN_FLOOR) gain = WIENER_GAIN_FLOOR;
            if (gain > 1.0) gain = 1.0;
            gains[bin] = gain;
        }
    }
    for (uint32_t bin = WIENER_BINS; bin < WIENER_FFT; ++bin) {
        gains[bin] = gains[WIENER_FFT - bin];
    }
    for (uint32_t bin = 0u; bin < WIENER_FFT; ++bin) {
        spectrum[bin].re *= gains[bin];
        spectrum[bin].im *= gains[bin];
    }
    wiener_fft(spectrum, 1);

    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const double value = spectrum[index].re;
        if (!isfinite(value) || fabs(value) > WIENER_MAX_ABS) {
            ++instance->invalid_count;
            return AS_INVALID_ARGUMENT;
        }
        output->samples[index] = (float)value;
    }

    ++instance->frames_processed;
    instance->output_start += (int64_t)AS_FRAME_SAMPLES;
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = AS_FRAME_SAMPLES;
    result->produced_count = AS_FRAME_SAMPLES;
    result->valid_offset = 0u;
    result->valid_count = AS_FRAME_SAMPLES;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL wiener_reset(void *opaque, uint64_t epoch,
                                         int64_t first_input_sample,
                                         as_error_v0 *error) {
    (void)error;
    wiener_instance *instance = (wiener_instance *)opaque;
    if (instance == NULL || epoch <= instance->epoch || first_input_sample < 0) {
        return AS_INVALID_ARGUMENT;
    }
    memset(instance->noise_psd, 0, sizeof(instance->noise_psd));
    for (uint32_t bin = 0u; bin < WIENER_BINS; ++bin) instance->noise_psd[bin] = 1e-10;
    memset(instance->power_psd, 0, sizeof(instance->power_psd));
    instance->frames_processed = 0u;
    instance->calibration_frames = 0u;
    instance->invalid_count = 0u;
    instance->epoch = epoch;
    instance->output_start = first_input_sample;
    return AS_OK;
}

static as_status_v0 AS_CALL wiener_drain(void *opaque,
                                         const as_output_v0 *output,
                                         as_result_v0 *result) {
    wiener_instance *instance = (wiener_instance *)opaque;
    if (instance == NULL || output == NULL || result == NULL) return AS_INVALID_ARGUMENT;
    (void)output;
    as_result_v0_init(result);
    result->status = AS_END_OF_STREAM;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->output_start;
    return AS_END_OF_STREAM;
}

static void AS_CALL wiener_destroy(void *opaque) { free(opaque); }

as_status_v0 wiener_register(as_registry_v0 *registry, as_error_v0 *error) {
    if (registry == NULL) return AS_INVALID_ARGUMENT;
    static const as_provider_table_v0 table = {
        (uint32_t)sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        wiener_create, wiener_process, wiener_reset, wiener_drain,
        wiener_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, kDescriptor,
                                   sizeof(kDescriptor) - 1u, error);
}
