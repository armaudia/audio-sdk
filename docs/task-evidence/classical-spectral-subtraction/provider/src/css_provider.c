/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local, optional classical spectral-subtraction reference.
 *
 * This is a first-party minimal reference compiled only by a caller that
 * opts in. It uses the public provider_v0 registration boundary and does not
 * modify the installed SDK, its descriptor catalog or its default providers.
 * The noise profile is an explicit caller-supplied asset: no whole-clip,
 * model, download or runtime discovery is performed here. Processing is
 * causal with a 160-sample WOLA delay; the 96-sample synthesis tail after the
 * final accepted input is discarded as final padding.
 */
#include "css_provider.h"
#include "css_descriptor.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CSS_N 256u                 /* FFT / analysis window size */
#define CSS_H 160u                 /* fixed v0 hop and output block */
#define CSS_TAIL (CSS_N - CSS_H)   /* 96 overlapping samples */
#define CSS_BINS (CSS_N / 2u + 1u)
#define CSS_ALPHA 2.0              /* over-subtraction factor */
#define CSS_FLOOR 0.05             /* spectral floor, relative to noise PSD */
#define CSS_SMOOTH 0.50            /* temporal gain smoothing */
#define CSS_PSD_EPSILON 1e-20
#define CSS_OUTPUT_EPSILON 1e-12

static const double css_pi = 3.14159265358979323846;

typedef struct css_instance {
    double twiddle_re[CSS_N / 2u];
    double twiddle_im[CSS_N / 2u];
    double analysis_window[CSS_N];
    double window_power[CSS_N];
    double wola_norm[CSS_H];
    double noise_psd[CSS_BINS];
    double gains[CSS_BINS];
    double ola[CSS_N];
    float previous[CSS_H];
    uint32_t previous_valid;
    uint64_t epoch;
    int64_t first_input_sample;
    int64_t next_output_sample;
    int drained;
} css_instance;

static void css_error(as_error_v0 *error, as_status_v0 status,
                      const char *field, const char *message) {
    if (error == NULL) return;
    as_error_v0_init(error);
    error->status = status;
    (void)snprintf(error->message, sizeof(error->message), "%s", message);
    if (field != NULL) {
        (void)snprintf(error->field, sizeof(error->field), "%s", field);
    }
}

static int css_read_f32_le(const uint8_t *bytes, float *out) {
    uint32_t bits = (uint32_t)bytes[0] |
                    ((uint32_t)bytes[1] << 8) |
                    ((uint32_t)bytes[2] << 16) |
                    ((uint32_t)bytes[3] << 24);
    memcpy(out, &bits, sizeof(bits));
    return 1;
}

static void css_fft(css_instance *instance, double *re, double *im,
                    int inverse) {
    uint32_t j = 0;
    for (uint32_t i = 1; i < CSS_N; ++i) {
        uint32_t bit = CSS_N >> 1;
        while ((j & bit) != 0) {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if (i < j) {
            double tre = re[i];
            double tim = im[i];
            re[i] = re[j];
            im[i] = im[j];
            re[j] = tre;
            im[j] = tim;
        }
    }
    for (uint32_t length = 2; length <= CSS_N; length <<= 1) {
        const uint32_t half = length >> 1;
        const uint32_t step = CSS_N / length;
        for (uint32_t base = 0; base < CSS_N; base += length) {
            for (uint32_t k = 0; k < half; ++k) {
                const uint32_t twiddle = k * step;
                const double wr = instance->twiddle_re[twiddle];
                const double wi = inverse ? -instance->twiddle_im[twiddle]
                                          : instance->twiddle_im[twiddle];
                const uint32_t a = base + k;
                const uint32_t b = a + half;
                const double tre = wr * re[b] - wi * im[b];
                const double tim = wr * im[b] + wi * re[b];
                re[b] = re[a] - tre;
                im[b] = im[a] - tim;
                re[a] += tre;
                im[a] += tim;
            }
        }
    }
    if (inverse) {
        for (uint32_t i = 0; i < CSS_N; ++i) {
            re[i] /= (double)CSS_N;
            im[i] /= (double)CSS_N;
        }
    }
}

static as_status_v0 css_prepare_windows(css_instance *instance) {
    for (uint32_t i = 0; i < CSS_N / 2u; ++i) {
        const double angle = -2.0 * css_pi * (double)i / (double)CSS_N;
        instance->twiddle_re[i] = cos(angle);
        instance->twiddle_im[i] = sin(angle);
    }
    for (uint32_t i = 0; i < CSS_N; ++i) {
        const double hann = 0.5 - 0.5 * cos(2.0 * css_pi * (double)i /
                                            (double)CSS_N);
        if (!(hann >= 0.0)) return AS_BACKEND_FAILURE;
        instance->window_power[i] = hann;
        instance->analysis_window[i] = sqrt(hann);
    }
    for (uint32_t i = 0; i < CSS_H; ++i) {
        double norm = instance->window_power[i];
        if (i + CSS_H < CSS_N) norm += instance->window_power[i + CSS_H];
        if (!(norm > CSS_OUTPUT_EPSILON)) return AS_BACKEND_FAILURE;
        instance->wola_norm[i] = norm;
    }
    return AS_OK;
}

static as_status_v0 css_estimate_noise(css_instance *instance,
                                       const as_asset_v0 *asset,
                                       as_error_v0 *error) {
    const uint8_t *bytes = (const uint8_t *)asset->data;
    const uint32_t samples = (uint32_t)(asset->byte_count / 4u);
    double sums[CSS_BINS];
    uint32_t frames = 0;
    double re[CSS_N];
    double im[CSS_N];
    memset(sums, 0, sizeof(sums));

    for (uint32_t offset = 0; offset + CSS_N <= samples; offset += CSS_H) {
        for (uint32_t i = 0; i < CSS_N; ++i) {
            float value = 0.0f;
            css_read_f32_le(bytes + (size_t)(offset + i) * 4u, &value);
            if (!isfinite((double)value)) {
                css_error(error, AS_INVALID_ARGUMENT, "assets[0]",
                          "noise profile contains a nonfinite sample");
                return AS_INVALID_ARGUMENT;
            }
            re[i] = (double)value * instance->analysis_window[i];
            im[i] = 0.0;
        }
        css_fft(instance, re, im, 0);
        for (uint32_t k = 0; k < CSS_BINS; ++k) {
            sums[k] += re[k] * re[k] + im[k] * im[k];
        }
        ++frames;
    }
    if (frames == 0) {
        css_error(error, AS_INVALID_ARGUMENT, "assets[0]",
                  "noise profile is shorter than one analysis window");
        return AS_INVALID_ARGUMENT;
    }
    for (uint32_t k = 0; k < CSS_BINS; ++k) {
        instance->noise_psd[k] = sums[k] / (double)frames;
        if (!(instance->noise_psd[k] > CSS_PSD_EPSILON)) {
            instance->noise_psd[k] = CSS_PSD_EPSILON;
        }
    }
    return AS_OK;
}

static as_status_v0 css_create(const as_create_config_v0 *config,
                               void **out_instance, as_error_v0 *error) {
    if (out_instance == NULL) {
        css_error(error, AS_INVALID_ARGUMENT, "instance", "instance output is null");
        return AS_INVALID_ARGUMENT;
    }
    *out_instance = NULL;
    if (config == NULL || config->sample_rate_hz != 16000u ||
        config->channels != 1u || config->frame_samples != CSS_H) {
        css_error(error, AS_INVALID_ARGUMENT, "config", "unsupported v0 format");
        return AS_INVALID_ARGUMENT;
    }
    if (config->asset_count != 1u || config->assets == NULL) {
        css_error(error, AS_INVALID_ARGUMENT, "assets",
                  "one noise-profile asset is required");
        return AS_INVALID_ARGUMENT;
    }
    const as_asset_v0 *asset = &config->assets[0];
    if (asset->data == NULL || asset->byte_count < (uint64_t)CSS_N * 4u ||
        (asset->byte_count % 4u) != 0u) {
        css_error(error, AS_INVALID_ARGUMENT, "assets[0]",
                  "noise profile must be float32 and at least 256 samples");
        return AS_INVALID_ARGUMENT;
    }

    css_instance *instance = (css_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) {
        css_error(error, AS_RESOURCE_EXHAUSTED, "instance", "allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    as_status_v0 status = css_prepare_windows(instance);
    if (status != AS_OK) {
        free(instance);
        css_error(error, AS_BACKEND_FAILURE, "windows", "window setup failed");
        return AS_BACKEND_FAILURE;
    }
    status = css_estimate_noise(instance, asset, error);
    if (status != AS_OK) {
        free(instance);
        return status;
    }
    instance->epoch = config->epoch;
    instance->first_input_sample = config->first_input_sample;
    instance->next_output_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

/* Analyze frame k-1 (buffered previous hop plus the first 96 samples of the
 * current hop), subtract noise, and emit the ready 160-sample OLA block. */
static as_status_v0 css_synthesize(css_instance *instance,
                                   const float *current, uint32_t valid_count,
                                   int have_current) {
    double re[CSS_N];
    double im[CSS_N];
    for (uint32_t i = 0; i < CSS_N; ++i) {
        const double sample = i < CSS_H
                                  ? (double)instance->previous[i]
                                  : (have_current ? (double)current[i - CSS_H]
                                                  : 0.0);
        re[i] = sample * instance->analysis_window[i];
        im[i] = 0.0;
    }
    css_fft(instance, re, im, 0);
    for (uint32_t k = 0; k < CSS_BINS; ++k) {
        const double power = re[k] * re[k] + im[k] * im[k];
        double target = power - CSS_ALPHA * instance->noise_psd[k];
        const double floor = CSS_FLOOR * instance->noise_psd[k];
        if (target < floor) target = floor;
        double gain = power > CSS_OUTPUT_EPSILON ? sqrt(target / power) : 0.0;
        if (gain > 1.0) gain = 1.0;
        gain = CSS_SMOOTH * instance->gains[k] + (1.0 - CSS_SMOOTH) * gain;
        instance->gains[k] = gain;
        re[k] *= gain;
        im[k] *= gain;
    }
    css_fft(instance, re, im, 1);
    for (uint32_t i = 0; i < CSS_N; ++i) {
        instance->ola[i] += re[i] * instance->analysis_window[i];
    }
    if (have_current && current != NULL) {
        memcpy(instance->previous, current, CSS_H * sizeof(float));
        instance->previous_valid = valid_count;
        for (uint32_t i = valid_count; i < CSS_H; ++i) {
            instance->previous[i] = 0.0f;
        }
    }
    return AS_OK;
}

static as_status_v0 css_emit(css_instance *instance,
                             const as_output_v0 *output, as_result_v0 *result) {
    for (uint32_t i = 0; i < CSS_H; ++i) {
        const double value = instance->ola[i] / instance->wola_norm[i];
        if (!isfinite(value)) return AS_BACKEND_FAILURE;
        output->samples[i] = (float)value;
    }
    memmove(instance->ola, instance->ola + CSS_H, CSS_TAIL * sizeof(double));
    memset(instance->ola + CSS_TAIL, 0, (CSS_N - CSS_TAIL) * sizeof(double));
    return AS_OK;
}

static void css_zero_output(const as_output_v0 *output) {
    if (output != NULL && output->samples != NULL) {
        memset(output->samples, 0, CSS_H * sizeof(float));
    }
}

static as_status_v0 css_process(void *state, const as_frame_v0 *frame,
                                const as_output_v0 *output,
                                as_result_v0 *result) {
    css_instance *instance = (css_instance *)state;
    if (instance == NULL || frame == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < CSS_H ||
        frame->input == NULL || frame->input_count != CSS_H ||
        frame->input_valid_count == 0 || frame->input_valid_count > CSS_H) {
        return AS_INVALID_ARGUMENT;
    }
    as_status_v0 status = css_synthesize(instance, frame->input,
                                         frame->input_valid_count, 1);
    if (status != AS_OK) {
        css_zero_output(output);
        return status;
    }
    status = css_emit(instance, output, result);
    if (status != AS_OK) {
        css_zero_output(output);
        return status;
    }
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = CSS_H;
    result->produced_count = CSS_H;
    result->valid_offset = 0;
    result->valid_count = CSS_H;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample - (int64_t)CSS_H;
    instance->next_output_sample = frame->first_input_sample;
    instance->epoch = frame->epoch;
    return AS_OK;
}

static as_status_v0 css_reset(void *state, uint64_t epoch,
                              int64_t first_input_sample, as_error_v0 *error) {
    (void)error;
    css_instance *instance = (css_instance *)state;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->gains, 0, sizeof(instance->gains));
    memset(instance->ola, 0, sizeof(instance->ola));
    memset(instance->previous, 0, sizeof(instance->previous));
    instance->previous_valid = 0;
    instance->epoch = epoch;
    instance->first_input_sample = first_input_sample;
    instance->next_output_sample = first_input_sample;
    instance->drained = 0;
    return AS_OK;
}

static as_status_v0 css_drain(void *state, const as_output_v0 *output,
                              as_result_v0 *result) {
    css_instance *instance = (css_instance *)state;
    if (instance == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < CSS_H) {
        return AS_INVALID_ARGUMENT;
    }
    as_result_v0_init(result);
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_output_sample;
    if (instance->drained) {
        result->status = AS_END_OF_STREAM;
        return AS_END_OF_STREAM;
    }
    as_status_v0 status = css_synthesize(instance, NULL, instance->previous_valid, 0);
    if (status != AS_OK) {
        css_zero_output(output);
        return status;
    }
    status = css_emit(instance, output, result);
    if (status != AS_OK) {
        css_zero_output(output);
        return status;
    }
    result->status = AS_OK;
    result->consumed_count = 0;
    result->produced_count = CSS_H;
    result->valid_offset = 0;
    result->valid_count = CSS_H;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_output_sample;
    instance->drained = 1;
    return AS_OK;
}

static void css_destroy(void *state) { free(state); }

as_status_v0 css_register_descriptor(as_registry_v0 *registry,
                                     const char *descriptor, uint32_t length,
                                     as_error_v0 *error) {
    static const as_provider_table_v0 table = {
        sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        css_create, css_process, css_reset, css_drain, css_destroy,
        {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, descriptor, length, error);
}

as_status_v0 css_register(as_registry_v0 *registry, as_error_v0 *error) {
    return css_register_descriptor(registry, kCssDescriptor,
                                   sizeof(kCssDescriptor) - 1u, error);
}
