/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local, optional fixed six-band spectral-tilt reference.
 *
 * First-party C, compiled only by a caller that opts in. It uses the public
 * provider_v0 registration boundary and never modifies the installed SDK, its
 * descriptor catalog or its defaults. Gains, band edges and the energy
 * normalization rule are fixed constants: there are no settings, assets,
 * downloads, models or runtime discovery.
 *
 * The source study applies one whole-clip FFT gain mask followed by total-power
 * restoration. That whole-clip step is noncausal and cannot be reproduced in a
 * v0 streaming provider. This reference applies the same six bin ranges and
 * gain dB values on a 256-point WOLA frame (160-sample hop). A smoothed
 * input/output power follower restores long-term energy with a one-block
 * attack; exact per-clip matching is left to the evaluator's energy-matched
 * control. The 96-sample synthesis tail after the final accepted input is
 * discarded as final padding. The causal approximation is reported as such;
 * no listening benefit is claimed.
 */
#include "sixband_provider.h"
#include "sixband_descriptor.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIXBAND_N 256u                  /* FFT / analysis window */
#define SIXBAND_H 160u                  /* fixed v0 hop and output block */
#define SIXBAND_TAIL (SIXBAND_N - SIXBAND_H)
#define SIXBAND_BINS (SIXBAND_N / 2u + 1u)
#define SIXBAND_BANDS 6u
#define SIXBAND_EPS 1e-18
#define SIXBAND_POWER_AVERAGE 16u   /* 16 blocks = 160 ms */
#define SIXBAND_GAIN_SMOOTH 8u      /* 8 blocks = 80 ms */
#define SIXBAND_MIN_SCALE 0.5
#define SIXBAND_MAX_SCALE 2.0

/* Interior edges from the source study: 250, 500, 1000, 2000, 4000 Hz.
 * At 16 kHz / 256 bins these are FFT bins 4, 8, 16, 32 and 64. */
static const uint32_t sixband_edges[SIXBAND_BANDS - 1u] = {4u, 8u, 16u, 32u, 64u};
/* Source-study gains in dB: six bands, high-frequency tilt. */
static const double sixband_gains_db[SIXBAND_BANDS] =
    {-3.0, -1.5, 0.0, 1.5, 3.0, 4.0};
static const double sixband_pi = 3.14159265358979323846;

typedef struct sixband_instance {
    double twiddle_re[SIXBAND_N / 2u];
    double twiddle_im[SIXBAND_N / 2u];
    double window[SIXBAND_N];
    double wola_norm[SIXBAND_H];
    double band_gain[SIXBAND_BANDS];
    double ola[SIXBAND_N];
    double average_input_power;
    double average_output_power;
    double previous_block_energy;
    double gain_correction;
    uint32_t follower_blocks;
    float previous[SIXBAND_H];
    uint32_t previous_valid;
    uint64_t epoch;
    int64_t first_input_sample;
    int64_t next_output_sample;
    int drained;
} sixband_instance;

static void sixband_error(as_error_v0 *error, as_status_v0 status,
                          const char *field, const char *message) {
    if (error == NULL) return;
    as_error_v0_init(error);
    error->status = status;
    (void)snprintf(error->message, sizeof(error->message), "%s", message);
    if (field != NULL) {
        (void)snprintf(error->field, sizeof(error->field), "%s", field);
    }
}

static void sixband_fft(sixband_instance *instance, double *re, double *im,
                        int inverse) {
    uint32_t j = 0;
    for (uint32_t i = 1; i < SIXBAND_N; ++i) {
        uint32_t bit = SIXBAND_N >> 1;
        while ((j & bit) != 0) {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if (i < j) {
            const double tre = re[i];
            const double tim = im[i];
            re[i] = re[j];
            im[i] = im[j];
            re[j] = tre;
            im[j] = tim;
        }
    }
    for (uint32_t length = 2; length <= SIXBAND_N; length <<= 1) {
        const uint32_t half = length >> 1;
        const uint32_t step = SIXBAND_N / length;
        for (uint32_t base = 0; base < SIXBAND_N; base += length) {
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
        for (uint32_t i = 0; i < SIXBAND_N; ++i) {
            re[i] /= (double)SIXBAND_N;
            im[i] /= (double)SIXBAND_N;
        }
    }
}

static as_status_v0 sixband_prepare(sixband_instance *instance) {
    for (uint32_t i = 0; i < SIXBAND_N / 2u; ++i) {
        const double angle = -2.0 * sixband_pi * (double)i / (double)SIXBAND_N;
        instance->twiddle_re[i] = cos(angle);
        instance->twiddle_im[i] = sin(angle);
    }
    for (uint32_t i = 0; i < SIXBAND_N; ++i) {
        const double hann = 0.5 - 0.5 * cos(2.0 * sixband_pi * (double)i /
                                            (double)SIXBAND_N);
        if (!(hann >= 0.0)) return AS_BACKEND_FAILURE;
        instance->window[i] = sqrt(hann);
    }
    for (uint32_t i = 0; i < SIXBAND_H; ++i) {
        double norm = instance->window[i] * instance->window[i];
        if (i + SIXBAND_H < SIXBAND_N) {
            norm += instance->window[i + SIXBAND_H] *
                    instance->window[i + SIXBAND_H];
        }
        if (!(norm > 1e-12)) return AS_BACKEND_FAILURE;
        instance->wola_norm[i] = norm;
    }
    for (uint32_t band = 0; band < SIXBAND_BANDS; ++band) {
        const double gain = pow(10.0, sixband_gains_db[band] / 20.0);
        if (!isfinite(gain) || !(gain > 0.0)) return AS_BACKEND_FAILURE;
        instance->band_gain[band] = gain;
    }
    return AS_OK;
}

static uint32_t sixband_bin_band(uint32_t bin) {
    uint32_t band = 0;
    while (band < SIXBAND_BANDS - 1u && bin >= sixband_edges[band]) ++band;
    return band;
}

static as_status_v0 sixband_synthesize(sixband_instance *instance,
                                       const float *current,
                                       uint32_t valid_count, int have_current) {
    double re[SIXBAND_N];
    double im[SIXBAND_N];

    /* The emitted block corresponds to the input hop held in `previous`
     * before this call replaces it; retain its energy for the follower. */
    instance->previous_block_energy = 0.0;
    for (uint32_t i = 0; i < SIXBAND_H; ++i) {
        const double sample = (double)instance->previous[i];
        instance->previous_block_energy += sample * sample;
    }
    for (uint32_t i = 0; i < SIXBAND_N; ++i) {
        const double sample = i < SIXBAND_H
                                  ? (double)instance->previous[i]
                                  : (have_current ? (double)current[i - SIXBAND_H]
                                                  : 0.0);
        re[i] = sample * instance->window[i];
        im[i] = 0.0;
    }

    sixband_fft(instance, re, im, 0);
    for (uint32_t k = 0; k < SIXBAND_N; ++k) {
        const uint32_t mirror = k <= SIXBAND_N / 2u ? k : SIXBAND_N - k;
        const double gain = instance->band_gain[sixband_bin_band(mirror)];
        re[k] *= gain;
        im[k] *= gain;
    }
    sixband_fft(instance, re, im, 1);

    for (uint32_t i = 0; i < SIXBAND_N; ++i) {
        re[i] *= instance->window[i] * instance->gain_correction;
    }
    for (uint32_t i = 0; i < SIXBAND_N; ++i) {
        instance->ola[i] += re[i];
    }
    if (have_current && current != NULL) {
        memcpy(instance->previous, current, SIXBAND_H * sizeof(float));
        instance->previous_valid = valid_count;
        for (uint32_t i = valid_count; i < SIXBAND_H; ++i) {
            instance->previous[i] = 0.0f;
        }
    }
    return AS_OK;
}

static as_status_v0 sixband_emit(sixband_instance *instance,
                                 const as_output_v0 *output) {
    double output_energy = 0.0;
    for (uint32_t i = 0; i < SIXBAND_H; ++i) {
        const double value = instance->ola[i] / instance->wola_norm[i];
        if (!isfinite(value)) return AS_BACKEND_FAILURE;
        output->samples[i] = (float)value;
        output_energy += value * value;
    }

    /* Smoothed power follower. It acts on whole emitted blocks, so exact
     * short-window energy equality is not claimed; see the report's
     * energy-matched control for the clip-level comparison. */
    const double input_power = instance->previous_block_energy /
                               (double)SIXBAND_H;
    const double measured_output_power = output_energy / (double)SIXBAND_H;
    if (input_power > SIXBAND_EPS && measured_output_power > SIXBAND_EPS) {
        if (instance->follower_blocks == 0u) {
            instance->average_input_power = input_power;
            instance->average_output_power = measured_output_power;
        } else {
            instance->average_input_power +=
                (input_power - instance->average_input_power) /
                (double)SIXBAND_POWER_AVERAGE;
            instance->average_output_power +=
                (measured_output_power - instance->average_output_power) /
                (double)SIXBAND_POWER_AVERAGE;
        }
        ++instance->follower_blocks;
        /* Neutral startup; silence holds the present gain instead of driving
         * it to a floor and causing a slow recovery on the next voice burst. */
        if (instance->follower_blocks > 4u) {
            /* Divide out the correction already present in the measurement;
             * otherwise the loop settles at sqrt() of the raw gain error. */
            double target = instance->gain_correction *
                            sqrt(instance->average_input_power /
                                 instance->average_output_power);
            if (!isfinite(target)) return AS_BACKEND_FAILURE;
            if (target < SIXBAND_MIN_SCALE) target = SIXBAND_MIN_SCALE;
            if (target > SIXBAND_MAX_SCALE) target = SIXBAND_MAX_SCALE;
            instance->gain_correction +=
                (target - instance->gain_correction) /
                (double)SIXBAND_GAIN_SMOOTH;
        }
    }

    memmove(instance->ola, instance->ola + SIXBAND_H,
            SIXBAND_TAIL * sizeof(double));
    memset(instance->ola + SIXBAND_TAIL, 0,
            (SIXBAND_N - SIXBAND_TAIL) * sizeof(double));
    return AS_OK;
}

static void sixband_zero_output(const as_output_v0 *output) {
    if (output != NULL && output->samples != NULL) {
        memset(output->samples, 0, SIXBAND_H * sizeof(float));
    }
}

static as_status_v0 sixband_create(const as_create_config_v0 *config,
                                   void **out_instance, as_error_v0 *error) {
    if (out_instance == NULL) {
        sixband_error(error, AS_INVALID_ARGUMENT, "instance",
                      "instance output is null");
        return AS_INVALID_ARGUMENT;
    }
    *out_instance = NULL;
    if (config == NULL || config->sample_rate_hz != 16000u ||
        config->channels != 1u || config->frame_samples != SIXBAND_H) {
        sixband_error(error, AS_INVALID_ARGUMENT, "config",
                      "unsupported v0 format");
        return AS_INVALID_ARGUMENT;
    }
    if (config->asset_count != 0u) {
        sixband_error(error, AS_UNSUPPORTED, "assets",
                      "fixed reference takes no caller assets");
        return AS_UNSUPPORTED;
    }

    sixband_instance *instance = (sixband_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL) {
        sixband_error(error, AS_RESOURCE_EXHAUSTED, "instance",
                      "allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    if (sixband_prepare(instance) != AS_OK) {
        free(instance);
        sixband_error(error, AS_BACKEND_FAILURE, "tables",
                      "window or gain table setup failed");
        return AS_BACKEND_FAILURE;
    }
    instance->average_input_power = SIXBAND_EPS;
    instance->average_output_power = SIXBAND_EPS;
    instance->gain_correction = 1.0;
    instance->follower_blocks = 0;
    instance->epoch = config->epoch;
    instance->first_input_sample = config->first_input_sample;
    instance->next_output_sample = config->first_input_sample;
    *out_instance = instance;
    return AS_OK;
}

static as_status_v0 sixband_process(void *state, const as_frame_v0 *frame,
                                    const as_output_v0 *output,
                                    as_result_v0 *result) {
    sixband_instance *instance = (sixband_instance *)state;
    if (instance == NULL || frame == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < SIXBAND_H ||
        frame->input == NULL || frame->input_count != SIXBAND_H ||
        frame->input_valid_count == 0 || frame->input_valid_count > SIXBAND_H) {
        return AS_INVALID_ARGUMENT;
    }
    as_status_v0 status = sixband_synthesize(instance, frame->input,
                                             frame->input_valid_count, 1);
    if (status != AS_OK) {
        sixband_zero_output(output);
        return status;
    }
    status = sixband_emit(instance, output);
    if (status != AS_OK) {
        sixband_zero_output(output);
        return status;
    }
    as_result_v0_init(result);
    result->status = AS_OK;
    result->consumed_count = SIXBAND_H;
    result->produced_count = SIXBAND_H;
    result->valid_offset = 0;
    result->valid_count = SIXBAND_H;
    result->epoch = frame->epoch;
    result->source_first_sample = frame->first_input_sample - (int64_t)SIXBAND_H;
    instance->next_output_sample = frame->first_input_sample;
    instance->epoch = frame->epoch;
    return AS_OK;
}

static as_status_v0 sixband_reset(void *state, uint64_t epoch,
                                  int64_t first_input_sample,
                                  as_error_v0 *error) {
    (void)error;
    sixband_instance *instance = (sixband_instance *)state;
    if (instance == NULL) return AS_INVALID_ARGUMENT;
    memset(instance->ola, 0, sizeof(instance->ola));
    memset(instance->previous, 0, sizeof(instance->previous));
    instance->previous_valid = 0;
    instance->previous_block_energy = 0.0;
    instance->average_input_power = SIXBAND_EPS;
    instance->average_output_power = SIXBAND_EPS;
    instance->gain_correction = 1.0;
    instance->follower_blocks = 0;
    instance->epoch = epoch;
    instance->first_input_sample = first_input_sample;
    instance->next_output_sample = first_input_sample;
    instance->drained = 0;
    return AS_OK;
}

static as_status_v0 sixband_drain(void *state, const as_output_v0 *output,
                                  as_result_v0 *result) {
    sixband_instance *instance = (sixband_instance *)state;
    if (instance == NULL || output == NULL || result == NULL ||
        output->samples == NULL || output->capacity < SIXBAND_H) {
        return AS_INVALID_ARGUMENT;
    }
    as_result_v0_init(result);
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_output_sample;
    if (instance->drained) {
        result->status = AS_END_OF_STREAM;
        return AS_END_OF_STREAM;
    }
    as_status_v0 status = sixband_synthesize(instance, NULL,
                                             instance->previous_valid, 0);
    if (status != AS_OK) {
        sixband_zero_output(output);
        return status;
    }
    status = sixband_emit(instance, output);
    if (status != AS_OK) {
        sixband_zero_output(output);
        return status;
    }
    result->status = AS_OK;
    result->consumed_count = 0;
    result->produced_count = SIXBAND_H;
    result->valid_offset = 0;
    result->valid_count = SIXBAND_H;
    result->epoch = instance->epoch;
    result->source_first_sample = instance->next_output_sample;
    instance->drained = 1;
    return AS_OK;
}

static void sixband_destroy(void *state) { free(state); }

as_status_v0 sixband_register_descriptor(as_registry_v0 *registry,
                                         const char *descriptor, uint32_t length,
                                         as_error_v0 *error) {
    static const as_provider_table_v0 table = {
        sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
        sixband_create, sixband_process, sixband_reset, sixband_drain,
        sixband_destroy, {0, 0, 0, 0}};
    return as_register_provider_v0(registry, &table, descriptor, length, error);
}

as_status_v0 sixband_register(as_registry_v0 *registry, as_error_v0 *error) {
    return sixband_register_descriptor(registry, kSixBandDescriptor,
                                       sizeof(kSixBandDescriptor) - 1u, error);
}
