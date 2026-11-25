/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
   SPDX-License-Identifier: Apache-2.0

   Task-local reference harness for the vendored SpeexDSP resampler.

   This is a thin, offline command-line wrapper around the public documented
   `speex/speex_resampler.h` boundary of the exact vendored source. It does not
   edit, copy, patch or relicense that source. It reads/writes raw little-endian
   float32 mono, frames the input in caller-declared blocks, flushes the
   resampler tail, and prints one deterministic `key=value` summary line.
*/

#include <errno.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "speex_resampler.h"

#define AS_MAX_FLUSH_CALLS 64.0
#define AS_MAX_FRAME 65536u
#define AS_MAX_RATE 192000u

static void fail(int code, const char *status, const char *detail, long value) {
    if (detail != NULL) {
        printf("status=%s detail=%s value=%ld\n", status, detail, value);
    } else {
        printf("status=%s value=%ld\n", status, value);
    }
    fflush(stdout);
    exit(code);
}

static int read_floats(const char *path, float **out, size_t *count) {
    FILE *file = fopen(path, "rb");
    long size;
    float *samples;
    if (file == NULL) {
        return 0;
    }
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return 0;
    }
    size = ftell(file);
    if (size < 0 || (size % 4) != 0) {
        fclose(file);
        return 0;
    }
    if (fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return 0;
    }
    samples = (float *)malloc((size_t)size == 0 ? 4 : (size_t)size);
    if (samples == NULL) {
        fclose(file);
        return 0;
    }
    if (size > 0 && fread(samples, 1, (size_t)size, file) != (size_t)size) {
        free(samples);
        fclose(file);
        return 0;
    }
    fclose(file);
    *out = samples;
    *count = (size_t)size / 4u;
    return 1;
}

static int write_floats(const char *path, const float *samples, size_t count) {
    FILE *file = fopen(path, "wb");
    if (file == NULL) {
        return 0;
    }
    if (count > 0 && fwrite(samples, 4, count, file) != count) {
        fclose(file);
        return 0;
    }
    return fclose(file) == 0;
}

int main(int argc, char **argv) {
    uint32_t in_rate = 0, out_rate = 0, frame = 0;
    int quality = -1, option;
    const char *in_path = NULL, *out_path = NULL;
    float *input = NULL, *output = NULL, *scratch = NULL;
    size_t input_count = 0, input_pos = 0, output_count = 0, capacity;
    uint32_t flush_calls = 0, f;
    int init_error = 0, rc = 0, input_latency, output_latency;
    SpeexResamplerState *state = NULL;

    for (option = 1; option + 1 < argc; option += 2) {
        if (strcmp(argv[option], "--in-rate") == 0) {
            in_rate = (uint32_t)strtoul(argv[option + 1], NULL, 10);
        } else if (strcmp(argv[option], "--out-rate") == 0) {
            out_rate = (uint32_t)strtoul(argv[option + 1], NULL, 10);
        } else if (strcmp(argv[option], "--quality") == 0) {
            quality = (int)strtol(argv[option + 1], NULL, 10);
        } else if (strcmp(argv[option], "--frame") == 0) {
            frame = (uint32_t)strtoul(argv[option + 1], NULL, 10);
        } else if (strcmp(argv[option], "--in") == 0) {
            in_path = argv[option + 1];
        } else if (strcmp(argv[option], "--out") == 0) {
            out_path = argv[option + 1];
        } else {
            fail(2, "invalid_argument", "unknown_option", 0);
        }
    }
    if (in_path == NULL || out_path == NULL) {
        fail(2, "invalid_argument", "missing_path", 0);
    }
    if (in_rate == 0 || out_rate == 0 || in_rate > AS_MAX_RATE
            || out_rate > AS_MAX_RATE) {
        fail(2, "invalid_rate", "rate_out_of_range", (long)in_rate);
    }
    if (quality < 0 || quality > SPEEX_RESAMPLER_QUALITY_MAX) {
        fail(2, "invalid_quality", "quality_out_of_range", (long)quality);
    }
    if (frame == 0 || frame > AS_MAX_FRAME) {
        fail(2, "invalid_frame", "frame_out_of_range", (long)frame);
    }
    if (!read_floats(in_path, &input, &input_count)) {
        fail(2, "invalid_input", "cannot_read_raw_f32", (long)errno);
    }
    for (input_pos = 0; input_pos < input_count; ++input_pos) {
        if (!isfinite(input[input_pos])) {
            free(input);
            fail(3, "nonfinite_input", "nonfinite_sample", (long)input_pos);
        }
    }

    state = speex_resampler_init_frac(1, in_rate, out_rate, in_rate, out_rate,
                                      quality, &init_error);
    if (state == NULL || init_error != 0) {
        free(input);
        fail(4, "init_failed", "resampler_init", (long)init_error);
    }
    input_latency = speex_resampler_get_input_latency(state);
    output_latency = speex_resampler_get_output_latency(state);

    /* Worst-case ratio is bounded by the declared 0.5x..2.0x task range. */
    capacity = (size_t)((double)input_count * 2.0) + (size_t)frame * 4u + 4096u;
    output = (float *)calloc(capacity, sizeof(float));
    scratch = (float *)calloc((size_t)frame * 4u + 4096u, sizeof(float));
    if (output == NULL || scratch == NULL) {
        speex_resampler_destroy(state);
        free(input);
        free(output);
        free(scratch);
        fail(5, "resource_exhausted", "allocation", 0);
    }

    input_pos = 0;
    while (input_pos < input_count) {
        uint32_t take = frame;
        spx_uint32_t available, produced;
        if ((size_t)take > input_count - input_pos) {
            take = (uint32_t)(input_count - input_pos);
        }
        available = take;
        produced = (spx_uint32_t)((size_t)frame * 4u + 4096u);
        rc = speex_resampler_process_float(state, 0, input + input_pos,
                                           &available, scratch, &produced);
        if (rc != 0) {
            fail(6, "process_failed", "process_float", (long)rc);
        }
        if (available != take) {
            fail(6, "process_failed", "unconsumed_input", (long)available);
        }
        if ((size_t)produced > capacity - output_count) {
            fail(5, "resource_exhausted", "output_capacity", 0);
        }
        memcpy(output + output_count, scratch, (size_t)produced * sizeof(float));
        output_count += produced;
        input_pos += take;
    }

    for (flush_calls = 0; flush_calls < (uint32_t)AS_MAX_FLUSH_CALLS;
            ++flush_calls) {
        spx_uint32_t produced = (spx_uint32_t)((size_t)frame * 4u + 4096u);
        spx_uint32_t available = 0;
        rc = speex_resampler_process_float(state, 0, NULL, &available,
                                           scratch, &produced);
        if (rc != 0) {
            fail(6, "process_failed", "flush", (long)rc);
        }
        if ((size_t)produced > capacity - output_count) {
            fail(5, "resource_exhausted", "output_capacity", 0);
        }
        memcpy(output + output_count, scratch, (size_t)produced * sizeof(float));
        output_count += produced;
        if (produced == 0) {
            break;
        }
    }
    if (flush_calls == (uint32_t)AS_MAX_FLUSH_CALLS) {
        fail(7, "flush_limit", "flush_not_terminating", 0);
    }
    for (f = 0; f < output_count; ++f) {
        if (!isfinite(output[f])) {
            fail(8, "nonfinite_output", "nonfinite_sample", (long)f);
        }
    }
    if (!write_floats(out_path, output, output_count)) {
        fail(9, "write_failed", "cannot_write_raw_f32", (long)errno);
    }

    printf("status=ok in_rate=%u out_rate=%u quality=%d frame=%u "
           "input_samples=%zu consumed=%zu output_samples=%zu "
           "flush_calls=%u input_latency=%d output_latency=%d\n",
           in_rate, out_rate, quality, frame, input_count, input_pos,
           output_count, flush_calls, input_latency, output_latency);
    fflush(stdout);

    speex_resampler_destroy(state);
    free(input);
    free(output);
    free(scratch);
    return 0;
}
