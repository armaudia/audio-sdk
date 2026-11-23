/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local SpeexDSP MDF reference adapter.
 *
 * This is a paired render/capture research tool, not an AEC product, not a
 * quality claim and not part of the installed SDK. It uses only the public
 * SpeexDSP echo API (speex/speex_echo.h). The compiled sources are the exact
 * vendored files pinned by deps/lock.json and legacy commit
 * 3e2446fc58886fc02b099b54651adc9a10a65454.
 *
 * A frame whose render samples are all zero is passed through bit-exactly
 * (the documented missing-render policy of the legacy stage). This preserves
 * a deterministic no-reference control and never invents echo cancellation.
 */
#include <speex/speex_echo.h>

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    MDF_OK = 0,
    MDF_BAD_ARGS = 2,
    MDF_BAD_INPUT = 3,
    MDF_IO_ERROR = 4,
    MDF_BACKEND_ERROR = 5
};

static void fail(int code, const char *field, const char *detail)
{
    fprintf(stderr, "ERROR %d %s %s\n", code, field, detail);
}

static int read_f32(const char *path, float **out, size_t *out_count)
{
    FILE *file = NULL;
    long size = 0;
    float *samples = NULL;
    size_t count = 0;
    size_t i = 0;

    if (path == NULL || out == NULL || out_count == NULL) {
        return MDF_BAD_ARGS;
    }
    *out = NULL;
    *out_count = 0;
    file = fopen(path, "rb");
    if (file == NULL) {
        fail(MDF_IO_ERROR, "file", "cannot open");
        return MDF_IO_ERROR;
    }
    if (fseek(file, 0, SEEK_END) != 0 || (size = ftell(file)) < 0 ||
        fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        fail(MDF_IO_ERROR, "file", "cannot seek");
        return MDF_IO_ERROR;
    }
    if (size == 0 || (size % 4) != 0) {
        fclose(file);
        fail(MDF_BAD_INPUT, "file", "length must be a positive multiple of 4");
        return MDF_BAD_INPUT;
    }
    count = (size_t)size / 4u;
    samples = (float *)malloc(count * sizeof(float));
    if (samples == NULL) {
        fclose(file);
        fail(MDF_BACKEND_ERROR, "memory", "allocation failed");
        return MDF_BACKEND_ERROR;
    }
    if (fread(samples, sizeof(float), count, file) != count) {
        free(samples);
        fclose(file);
        fail(MDF_IO_ERROR, "file", "short read");
        return MDF_IO_ERROR;
    }
    fclose(file);
    for (i = 0; i < count; ++i) {
        if (!isfinite(samples[i]) || samples[i] < -1.0F || samples[i] > 1.0F) {
            free(samples);
            fail(MDF_BAD_INPUT, "samples", "nonfinite or outside [-1, 1]");
            return MDF_BAD_INPUT;
        }
    }
    *out = samples;
    *out_count = count;
    return MDF_OK;
}

static int16_t float_to_i16(float value)
{
    const float clamped = value < -1.0F ? -1.0F : (value > 1.0F ? 1.0F : value);
    const double scaled = (double)clamped * 32767.0;
    const long rounded = lrint(scaled);
    if (rounded > 32767L) {
        return 32767;
    }
    if (rounded < -32768L) {
        return -32768;
    }
    return (int16_t)rounded;
}

static float i16_to_float(int16_t value)
{
    return (float)value / 32768.0F;
}

static int write_f32(const char *path, const float *samples, size_t count)
{
    FILE *file = NULL;
    if (path == NULL || samples == NULL) {
        return MDF_BAD_ARGS;
    }
    file = fopen(path, "wb");
    if (file == NULL) {
        fail(MDF_IO_ERROR, "output", "cannot open");
        return MDF_IO_ERROR;
    }
    if (fwrite(samples, sizeof(float), count, file) != count || fclose(file) != 0) {
        fail(MDF_IO_ERROR, "output", "short write");
        return MDF_IO_ERROR;
    }
    return MDF_OK;
}

static int self_test(void)
{
    float capture[160];
    float render[160];
    float output[160];
    int16_t rec[160];
    int16_t play[160];
    int16_t out[160];
    SpeexEchoState *state = NULL;
    int rate = 16000;
    int i = 0;
    int status = MDF_OK;

    for (i = 0; i < 160; ++i) {
        render[i] = (i % 7 == 0) ? 0.1F : 0.0F;
        capture[i] = (i % 11 == 0) ? 0.05F : 0.0F;
    }
    state = speex_echo_state_init(160, 3200);
    if (state == NULL || speex_echo_ctl(state, SPEEX_ECHO_SET_SAMPLING_RATE, &rate) != 0) {
        fail(MDF_BACKEND_ERROR, "state", "init failed");
        return MDF_BACKEND_ERROR;
    }
    for (i = 0; i < 160; ++i) {
        rec[i] = float_to_i16(capture[i]);
        play[i] = float_to_i16(render[i]);
    }
    speex_echo_cancellation(state, rec, play, out);
    for (i = 0; i < 160; ++i) {
        output[i] = i16_to_float(out[i]);
        if (!isfinite(output[i])) {
            status = MDF_BACKEND_ERROR;
        }
    }
    speex_echo_state_destroy(state);
    if (status == MDF_OK) {
        puts("SELFTEST OK");
    } else {
        fail(status, "output", "nonfinite");
    }
    return status;
}

int main(int argc, char **argv)
{
    const char *render_path = NULL;
    const char *capture_path = NULL;
    const char *output_path = NULL;
    int frame_samples = 160;
    int filter_length = 3200;
    int rate = 16000;
    int reset_every = 0;
    float *render = NULL;
    float *capture = NULL;
    float *output = NULL;
    int16_t *rec = NULL;
    int16_t *play = NULL;
    int16_t *out = NULL;
    SpeexEchoState *state = NULL;
    size_t count = 0;
    size_t frames = 0;
    size_t frame = 0;
    size_t i = 0;
    int status = MDF_OK;
    int arg = 1;

    if (argc == 2 && strcmp(argv[1], "--self-test") == 0) {
        return self_test();
    }
    while (arg < argc) {
        const char *key = argv[arg];
        if (strcmp(key, "--render") == 0 || strcmp(key, "--capture") == 0 ||
            strcmp(key, "--output") == 0 || strcmp(key, "--frame-samples") == 0 ||
            strcmp(key, "--filter-length") == 0 || strcmp(key, "--rate") == 0 ||
            strcmp(key, "--reset-every") == 0) {
            if (arg + 1 >= argc) {
                fail(MDF_BAD_ARGS, key, "missing value");
                return MDF_BAD_ARGS;
            }
            if (strcmp(key, "--render") == 0) {
                render_path = argv[++arg];
            } else if (strcmp(key, "--capture") == 0) {
                capture_path = argv[++arg];
            } else if (strcmp(key, "--output") == 0) {
                output_path = argv[++arg];
            } else if (strcmp(key, "--frame-samples") == 0) {
                frame_samples = atoi(argv[++arg]);
            } else if (strcmp(key, "--filter-length") == 0) {
                filter_length = atoi(argv[++arg]);
            } else if (strcmp(key, "--rate") == 0) {
                rate = atoi(argv[++arg]);
            } else {
                reset_every = atoi(argv[++arg]);
            }
            ++arg;
        } else {
            fail(MDF_BAD_ARGS, key, "unknown option");
            return MDF_BAD_ARGS;
        }
    }
    if (render_path == NULL || capture_path == NULL || output_path == NULL ||
        frame_samples != 160 || rate != 16000 || filter_length < 320 ||
        filter_length > 12000 || reset_every < 0) {
        fail(MDF_BAD_ARGS, "config",
             "requires --render/--capture/--output, 160-frame, 16000-Hz, "
             "320..12000 filter and nonnegative reset");
        return MDF_BAD_ARGS;
    }

    status = read_f32(render_path, &render, &count);
    if (status != MDF_OK) {
        return status;
    }
    {
        size_t capture_count = 0;
        status = read_f32(capture_path, &capture, &capture_count);
        if (status != MDF_OK) {
            free(render);
            return status;
        }
        if (capture_count != count || count % (size_t)frame_samples != 0) {
            free(render);
            free(capture);
            fail(MDF_BAD_INPUT, "length", "render/capture length mismatch or partial frame");
            return MDF_BAD_INPUT;
        }
    }
    frames = count / (size_t)frame_samples;
    output = (float *)malloc(count * sizeof(float));
    rec = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    play = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    out = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    if (output == NULL || rec == NULL || play == NULL || out == NULL) {
        fail(MDF_BACKEND_ERROR, "memory", "allocation failed");
        status = MDF_BACKEND_ERROR;
        goto cleanup;
    }
    state = speex_echo_state_init(frame_samples, filter_length);
    if (state == NULL || speex_echo_ctl(state, SPEEX_ECHO_SET_SAMPLING_RATE, &rate) != 0) {
        fail(MDF_BACKEND_ERROR, "state", "init failed");
        status = MDF_BACKEND_ERROR;
        goto cleanup;
    }
    for (frame = 0; frame < frames; ++frame) {
        const size_t base = frame * (size_t)frame_samples;
        int render_active = 0;
        for (i = 0; i < (size_t)frame_samples; ++i) {
            if (render[base + i] != 0.0F) {
                render_active = 1;
            }
        }
        if (reset_every > 0 && frame > 0 && (frame % (size_t)reset_every) == 0) {
            speex_echo_state_reset(state);
        }
        if (!render_active) {
            for (i = 0; i < (size_t)frame_samples; ++i) {
                output[base + i] = capture[base + i];
            }
            continue;
        }
        for (i = 0; i < (size_t)frame_samples; ++i) {
            rec[i] = float_to_i16(capture[base + i]);
            play[i] = float_to_i16(render[base + i]);
        }
        speex_echo_cancellation(state, rec, play, out);
        for (i = 0; i < (size_t)frame_samples; ++i) {
            output[base + i] = i16_to_float(out[i]);
            if (!isfinite(output[base + i])) {
                fail(MDF_BACKEND_ERROR, "output", "nonfinite");
                status = MDF_BACKEND_ERROR;
                goto cleanup;
            }
        }
    }
    status = write_f32(output_path, output, count);
    if (status == MDF_OK) {
        printf("OK %zu\n", count);
    }

cleanup:
    if (state != NULL) {
        speex_echo_state_destroy(state);
    }
    free(out);
    free(play);
    free(rec);
    free(output);
    free(capture);
    free(render);
    return status;
}
