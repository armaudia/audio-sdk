/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local Speex MDF residual postfilter reference adapter.
 *
 * This is a paired render/capture research tool, not an AEC product, not a
 * quality claim and not part of the installed SDK. It uses only the public
 * SpeexDSP boundaries speex/speex_echo.h and speex/speex_preprocess.h. The
 * compiled sources are the exact vendored files pinned by deps/lock.json and
 * legacy commit 3e2446fc58886fc02b099b54651adc9a10a65454.
 *
 * The residual postfilter is OFF unless the caller passes --postfilter. It is
 * wired exactly like the research wrapper: denoise, AGC, VAD and dereverb are
 * disabled, echo suppression levels are pinned, and the preprocessor is bound
 * to the same MDF state. A frame whose render samples are all zero is passed
 * through bit-exactly (the documented missing-render policy of the legacy
 * stage). This preserves a deterministic no-reference control and never
 * invents echo cancellation.
 */
#include <speex/speex_echo.h>
#include <speex/speex_preprocess.h>

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    PF_OK = 0,
    PF_BAD_ARGS = 2,
    PF_BAD_INPUT = 3,
    PF_IO_ERROR = 4,
    PF_BACKEND_ERROR = 5
};

enum {
    PF_FRAME_SAMPLES = 160,
    PF_FILTER_LENGTH = 3200,
    PF_RATE_HZ = 16000,
    PF_ECHO_SUPPRESS_DB = -40,
    PF_ECHO_SUPPRESS_ACTIVE_DB = -15
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
        return PF_BAD_ARGS;
    }
    *out = NULL;
    *out_count = 0;
    file = fopen(path, "rb");
    if (file == NULL) {
        fail(PF_IO_ERROR, "file", "cannot open");
        return PF_IO_ERROR;
    }
    if (fseek(file, 0, SEEK_END) != 0 || (size = ftell(file)) < 0 ||
        fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        fail(PF_IO_ERROR, "file", "cannot seek");
        return PF_IO_ERROR;
    }
    if (size == 0 || (size % 4) != 0) {
        fclose(file);
        fail(PF_BAD_INPUT, "file", "length must be a positive multiple of 4");
        return PF_BAD_INPUT;
    }
    count = (size_t)size / 4u;
    samples = (float *)malloc(count * sizeof(float));
    if (samples == NULL) {
        fclose(file);
        fail(PF_BACKEND_ERROR, "memory", "allocation failed");
        return PF_BACKEND_ERROR;
    }
    if (fread(samples, sizeof(float), count, file) != count) {
        free(samples);
        fclose(file);
        fail(PF_IO_ERROR, "file", "short read");
        return PF_IO_ERROR;
    }
    fclose(file);
    for (i = 0; i < count; ++i) {
        if (!isfinite(samples[i]) || samples[i] < -1.0F || samples[i] > 1.0F) {
            free(samples);
            fail(PF_BAD_INPUT, "samples", "nonfinite or outside [-1, 1]");
            return PF_BAD_INPUT;
        }
    }
    *out = samples;
    *out_count = count;
    return PF_OK;
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
        return PF_BAD_ARGS;
    }
    file = fopen(path, "wb");
    if (file == NULL) {
        fail(PF_IO_ERROR, "output", "cannot open");
        return PF_IO_ERROR;
    }
    if (fwrite(samples, sizeof(float), count, file) != count || fclose(file) != 0) {
        fail(PF_IO_ERROR, "output", "short write");
        return PF_IO_ERROR;
    }
    return PF_OK;
}

static int set_preprocess_control(SpeexPreprocessState *state, int request,
                                  int value)
{
    int setting = value;
    if (speex_preprocess_ctl(state, request, &setting) != 0) {
        fail(PF_BACKEND_ERROR, "preprocess_ctl", "control rejected");
        return PF_BACKEND_ERROR;
    }
    return PF_OK;
}

static SpeexPreprocessState *init_postfilter(SpeexEchoState *echo,
                                             int echo_suppress_db,
                                             int echo_suppress_active_db)
{
    SpeexPreprocessState *state = NULL;
    static const int disabled_controls[] = {
        SPEEX_PREPROCESS_SET_DENOISE,
        SPEEX_PREPROCESS_SET_AGC,
        SPEEX_PREPROCESS_SET_VAD,
        SPEEX_PREPROCESS_SET_DEREVERB
    };
    size_t index = 0;
    int setting = 0;

    state = speex_preprocess_state_init(PF_FRAME_SAMPLES, PF_RATE_HZ);
    if (state == NULL) {
        fail(PF_BACKEND_ERROR, "preprocess", "init failed");
        return NULL;
    }
    for (index = 0; index < sizeof(disabled_controls) / sizeof(disabled_controls[0]);
         ++index) {
        if (set_preprocess_control(state, disabled_controls[index], 0) != PF_OK) {
            speex_preprocess_state_destroy(state);
            return NULL;
        }
    }
    if (set_preprocess_control(state, SPEEX_PREPROCESS_SET_ECHO_SUPPRESS,
                               echo_suppress_db) != PF_OK ||
        set_preprocess_control(state, SPEEX_PREPROCESS_SET_ECHO_SUPPRESS_ACTIVE,
                               echo_suppress_active_db) != PF_OK) {
        speex_preprocess_state_destroy(state);
        return NULL;
    }
    setting = speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_ECHO_STATE, echo);
    if (setting != 0) {
        fail(PF_BACKEND_ERROR, "preprocess_ctl", "echo state rejected");
        speex_preprocess_state_destroy(state);
        return NULL;
    }
    return state;
}

static int self_test(int with_postfilter)
{
    float capture[PF_FRAME_SAMPLES];
    float render[PF_FRAME_SAMPLES];
    float output[PF_FRAME_SAMPLES];
    int16_t rec[PF_FRAME_SAMPLES];
    int16_t play[PF_FRAME_SAMPLES];
    int16_t out[PF_FRAME_SAMPLES];
    SpeexEchoState *echo = NULL;
    SpeexPreprocessState *postfilter = NULL;
    int rate = PF_RATE_HZ;
    int i = 0;
    int status = PF_OK;

    for (i = 0; i < PF_FRAME_SAMPLES; ++i) {
        render[i] = (i % 7 == 0) ? 0.1F : 0.0F;
        capture[i] = (i % 11 == 0) ? 0.05F : 0.0F;
    }
    echo = speex_echo_state_init(PF_FRAME_SAMPLES, PF_FILTER_LENGTH);
    if (echo == NULL ||
        speex_echo_ctl(echo, SPEEX_ECHO_SET_SAMPLING_RATE, &rate) != 0) {
        fail(PF_BACKEND_ERROR, "state", "init failed");
        return PF_BACKEND_ERROR;
    }
    if (with_postfilter) {
        postfilter = init_postfilter(echo, PF_ECHO_SUPPRESS_DB,
                                     PF_ECHO_SUPPRESS_ACTIVE_DB);
        if (postfilter == NULL) {
            speex_echo_state_destroy(echo);
            return PF_BACKEND_ERROR;
        }
    }
    for (i = 0; i < PF_FRAME_SAMPLES; ++i) {
        rec[i] = float_to_i16(capture[i]);
        play[i] = float_to_i16(render[i]);
    }
    speex_echo_cancellation(echo, rec, play, out);
    if (postfilter != NULL) {
        speex_preprocess_run(postfilter, out);
    }
    for (i = 0; i < PF_FRAME_SAMPLES; ++i) {
        output[i] = i16_to_float(out[i]);
        if (!isfinite(output[i])) {
            status = PF_BACKEND_ERROR;
        }
    }
    if (postfilter != NULL) {
        speex_preprocess_state_destroy(postfilter);
    }
    speex_echo_state_destroy(echo);
    if (status == PF_OK) {
        puts(with_postfilter ? "SELFTEST POSTFILTER OK" : "SELFTEST OK");
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
    int frame_samples = PF_FRAME_SAMPLES;
    int filter_length = PF_FILTER_LENGTH;
    int rate = PF_RATE_HZ;
    int reset_every = 0;
    int postfilter_enabled = 0;
    int echo_suppress_db = PF_ECHO_SUPPRESS_DB;
    int echo_suppress_active_db = PF_ECHO_SUPPRESS_ACTIVE_DB;
    float *render = NULL;
    float *capture = NULL;
    float *output = NULL;
    int16_t *rec = NULL;
    int16_t *play = NULL;
    int16_t *out = NULL;
    SpeexEchoState *echo = NULL;
    SpeexPreprocessState *postfilter = NULL;
    size_t count = 0;
    size_t frames = 0;
    size_t frame = 0;
    size_t i = 0;
    int status = PF_OK;
    int arg = 1;

    if (argc == 2 && strcmp(argv[1], "--self-test") == 0) {
        return self_test(0);
    }
    if (argc == 2 && strcmp(argv[1], "--self-test-postfilter") == 0) {
        return self_test(1);
    }
    while (arg < argc) {
        const char *key = argv[arg];
        if (strcmp(key, "--postfilter") == 0) {
            postfilter_enabled = 1;
            ++arg;
            continue;
        }
        if (strcmp(key, "--render") == 0 || strcmp(key, "--capture") == 0 ||
            strcmp(key, "--output") == 0 || strcmp(key, "--frame-samples") == 0 ||
            strcmp(key, "--filter-length") == 0 || strcmp(key, "--rate") == 0 ||
            strcmp(key, "--reset-every") == 0 ||
            strcmp(key, "--echo-suppress-db") == 0 ||
            strcmp(key, "--echo-suppress-active-db") == 0) {
            if (arg + 1 >= argc) {
                fail(PF_BAD_ARGS, key, "missing value");
                return PF_BAD_ARGS;
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
            } else if (strcmp(key, "--reset-every") == 0) {
                reset_every = atoi(argv[++arg]);
            } else if (strcmp(key, "--echo-suppress-db") == 0) {
                echo_suppress_db = atoi(argv[++arg]);
            } else {
                echo_suppress_active_db = atoi(argv[++arg]);
            }
            ++arg;
        } else {
            fail(PF_BAD_ARGS, key, "unknown option");
            return PF_BAD_ARGS;
        }
    }
    if (render_path == NULL || capture_path == NULL || output_path == NULL ||
        frame_samples != PF_FRAME_SAMPLES || rate != PF_RATE_HZ ||
        filter_length < 320 || filter_length > 12000 || reset_every < 0 ||
        echo_suppress_db > 0 || echo_suppress_active_db > 0 ||
        echo_suppress_db < -100 || echo_suppress_active_db < -100) {
        fail(PF_BAD_ARGS, "config",
             "requires --render/--capture/--output, 160-frame, 16000-Hz, "
             "320..12000 filter, nonnegative reset and nonpositive suppression levels");
        return PF_BAD_ARGS;
    }

    status = read_f32(render_path, &render, &count);
    if (status != PF_OK) {
        return status;
    }
    {
        size_t capture_count = 0;
        status = read_f32(capture_path, &capture, &capture_count);
        if (status != PF_OK) {
            free(render);
            return status;
        }
        if (capture_count != count || count % (size_t)frame_samples != 0) {
            free(render);
            free(capture);
            fail(PF_BAD_INPUT, "length", "render/capture length mismatch or partial frame");
            return PF_BAD_INPUT;
        }
    }
    frames = count / (size_t)frame_samples;
    output = (float *)malloc(count * sizeof(float));
    rec = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    play = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    out = (int16_t *)malloc((size_t)frame_samples * sizeof(int16_t));
    if (output == NULL || rec == NULL || play == NULL || out == NULL) {
        fail(PF_BACKEND_ERROR, "memory", "allocation failed");
        status = PF_BACKEND_ERROR;
        goto cleanup;
    }
    echo = speex_echo_state_init(frame_samples, filter_length);
    if (echo == NULL ||
        speex_echo_ctl(echo, SPEEX_ECHO_SET_SAMPLING_RATE, &rate) != 0) {
        fail(PF_BACKEND_ERROR, "state", "init failed");
        status = PF_BACKEND_ERROR;
        goto cleanup;
    }
    if (postfilter_enabled) {
        postfilter = init_postfilter(echo, echo_suppress_db,
                                     echo_suppress_active_db);
        if (postfilter == NULL) {
            status = PF_BACKEND_ERROR;
            goto cleanup;
        }
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
            speex_echo_state_reset(echo);
            if (postfilter != NULL) {
                speex_preprocess_state_destroy(postfilter);
                postfilter = init_postfilter(echo, echo_suppress_db,
                                             echo_suppress_active_db);
                if (postfilter == NULL) {
                    status = PF_BACKEND_ERROR;
                    goto cleanup;
                }
            }
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
        speex_echo_cancellation(echo, rec, play, out);
        if (postfilter != NULL) {
            speex_preprocess_run(postfilter, out);
        }
        for (i = 0; i < (size_t)frame_samples; ++i) {
            output[base + i] = i16_to_float(out[i]);
            if (!isfinite(output[base + i])) {
                fail(PF_BACKEND_ERROR, "output", "nonfinite");
                status = PF_BACKEND_ERROR;
                goto cleanup;
            }
        }
    }
    status = write_f32(output_path, output, count);
    if (status == PF_OK) {
        printf("OK %zu postfilter=%d\n", count, postfilter_enabled);
    }

cleanup:
    if (postfilter != NULL) {
        speex_preprocess_state_destroy(postfilter);
    }
    if (echo != NULL) {
        speex_echo_state_destroy(echo);
    }
    free(out);
    free(play);
    free(rec);
    free(output);
    free(capture);
    free(render);
    return status;
}
