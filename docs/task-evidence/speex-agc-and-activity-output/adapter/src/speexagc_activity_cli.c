/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local SpeexDSP AGC + advisory activity reference CLI.
 *
 * This is a deterministic developer fixture, not an SDK provider, ABI change,
 * quality claim or release artifact. It uses only the public
 * speex/speex_preprocess.h boundary and the exact vendored SpeexDSP sources.
 * One SpeexPreprocessState serves the whole stream. The AGC changes audio;
 * the VAD only changes the return value of speex_preprocess_run() and is
 * exported as advisory metadata. Denoise and dereverb stay off so that the
 * combined AGC + activity configuration can be measured without a third
 * nonlinear stage. Every accepted frame takes the same conversion path:
 * float -> PCM16 (clamp, lrintf under FE_TONEAREST) -> Speex -> float / 32768.
 */
#include <speex/speex_preprocess.h>

#include <fenv.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    ACT_OK = 0,
    ACT_BAD_ARGS = 2,
    ACT_BAD_INPUT = 3,
    ACT_IO_ERROR = 4,
    ACT_BACKEND_ERROR = 5
};

#define ACT_FRAME_SAMPLES 160
#define ACT_RATE_HZ 16000

typedef struct act_config {
    int agc;
    int vad;
    int denoise;
    int target;
    int increment;
    int decrement;
    int max_gain;
    int prob_start;
    int prob_continue;
    int noise_suppress;
    int reset_count;
    size_t resets[256];
} act_config;

static void fail(int code, const char *field, const char *detail)
{
    fprintf(stderr, "ERROR %d %s %s\n", code, field, detail);
}

static int parse_int(const char *text, int *out)
{
    char *end = NULL;
    long value = 0;
    if (text == NULL || *text == '\0') {
        return 0;
    }
    value = strtol(text, &end, 10);
    if (end == NULL || *end != '\0' || value < INT32_MIN || value > INT32_MAX) {
        return 0;
    }
    *out = (int)value;
    return 1;
}

static int parse_flag(const char *text, int *out)
{
    int value = 0;
    if (!parse_int(text, &value) || (value != 0 && value != 1)) {
        return 0;
    }
    *out = value;
    return 1;
}

static int parse_resets(const char *text, act_config *config)
{
    const char *cursor = text;
    config->reset_count = 0;
    if (cursor == NULL || *cursor == '\0') {
        return 1;
    }
    while (*cursor != '\0') {
        char *end = NULL;
        long value = strtol(cursor, &end, 10);
        size_t index = 0;
        int duplicate = 0;
        if (end == cursor || value < 1 || value > INT32_MAX) {
            return 0;
        }
        if (*end != '\0' && *end != ',') {
            return 0;
        }
        if (config->reset_count >= (int)(sizeof(config->resets) / sizeof(config->resets[0]))) {
            return 0;
        }
        for (index = 0; index < (size_t)config->reset_count; ++index) {
            if (config->resets[index] == (size_t)value) {
                duplicate = 1;
            }
        }
        if (!duplicate) {
            config->resets[config->reset_count++] = (size_t)value;
        }
        cursor = (*end == ',') ? end + 1 : end;
    }
    return 1;
}

static SpeexPreprocessState *make_state(const act_config *config)
{
    SpeexPreprocessState *state = speex_preprocess_state_init(ACT_FRAME_SAMPLES, ACT_RATE_HZ);
    int value = 0;
    float level = 0.0F;
    if (state == NULL) {
        return NULL;
    }
    value = config->denoise;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_DENOISE, &value) != 0) {
        goto failed;
    }
    value = 0;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_DEREVERB, &value) != 0) {
        goto failed;
    }
    value = config->agc;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_AGC, &value) != 0) {
        goto failed;
    }
    value = config->vad;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_VAD, &value) != 0) {
        goto failed;
    }
    level = (float)config->target;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_AGC_LEVEL, &level) != 0) {
        goto failed;
    }
    value = config->increment;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_AGC_INCREMENT, &value) != 0) {
        goto failed;
    }
    value = config->decrement;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_AGC_DECREMENT, &value) != 0) {
        goto failed;
    }
    value = config->max_gain;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_AGC_MAX_GAIN, &value) != 0) {
        goto failed;
    }
    value = config->prob_start;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_PROB_START, &value) != 0) {
        goto failed;
    }
    value = config->prob_continue;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_PROB_CONTINUE, &value) != 0) {
        goto failed;
    }
    value = config->noise_suppress;
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_SET_NOISE_SUPPRESS, &value) != 0) {
        goto failed;
    }
    return state;

failed:
    speex_preprocess_state_destroy(state);
    return NULL;
}

static int16_t clamp_to_pcm16(float value)
{
    if (value > 1.0F) {
        value = 1.0F;
    }
    if (value < -1.0F) {
        value = -1.0F;
    }
    return (int16_t)lrintf(value * 32767.0F);
}

static int read_f32(const char *path, float **out, size_t *out_count)
{
    FILE *file = NULL;
    long size = 0;
    float *samples = NULL;
    size_t count = 0;
    size_t index = 0;

    if (path == NULL || out == NULL || out_count == NULL) {
        return ACT_BAD_ARGS;
    }
    *out = NULL;
    *out_count = 0;
    file = fopen(path, "rb");
    if (file == NULL) {
        fail(ACT_IO_ERROR, "input", "cannot open");
        return ACT_IO_ERROR;
    }
    if (fseek(file, 0, SEEK_END) != 0 || (size = ftell(file)) < 0 ||
            fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        fail(ACT_IO_ERROR, "input", "cannot seek");
        return ACT_IO_ERROR;
    }
    if (size == 0 || (size % 4) != 0) {
        fclose(file);
        fail(ACT_BAD_INPUT, "input", "length must be a positive multiple of 4");
        return ACT_BAD_INPUT;
    }
    count = (size_t)size / 4u;
    if ((count % ACT_FRAME_SAMPLES) != 0) {
        fclose(file);
        fail(ACT_BAD_INPUT, "input", "length must be frame aligned");
        return ACT_BAD_INPUT;
    }
    samples = (float *)malloc(count * sizeof(float));
    if (samples == NULL) {
        fclose(file);
        fail(ACT_BACKEND_ERROR, "memory", "allocation failed");
        return ACT_BACKEND_ERROR;
    }
    if (fread(samples, sizeof(float), count, file) != count) {
        free(samples);
        fclose(file);
        fail(ACT_IO_ERROR, "input", "short read");
        return ACT_IO_ERROR;
    }
    fclose(file);
    for (index = 0; index < count; ++index) {
        /* Fail closed on unusable input instead of invoking undefined lrintf. */
        if (!isfinite(samples[index]) || samples[index] < -1.0F || samples[index] > 1.0F) {
            free(samples);
            fail(ACT_BAD_INPUT, "samples", "nonfinite or outside [-1, 1]");
            return ACT_BAD_INPUT;
        }
    }
    *out = samples;
    *out_count = count;
    return ACT_OK;
}

static int write_f32(const char *path, const float *samples, size_t count)
{
    FILE *file = NULL;
    if (path == NULL || samples == NULL) {
        return ACT_BAD_ARGS;
    }
    file = fopen(path, "wb");
    if (file == NULL) {
        fail(ACT_IO_ERROR, "output", "cannot open");
        return ACT_IO_ERROR;
    }
    if (fwrite(samples, sizeof(float), count, file) != count || fclose(file) != 0) {
        fail(ACT_IO_ERROR, "output", "short write");
        return ACT_IO_ERROR;
    }
    return ACT_OK;
}

static int write_meta(const char *path, const act_config *config, size_t frames,
                      const int *vad, const int *gain, const int *prob,
                      const int *loudness, const int *reset)
{
    FILE *file = NULL;
    size_t frame = 0;
    if (path == NULL || vad == NULL || gain == NULL || prob == NULL ||
            loudness == NULL || reset == NULL) {
        return ACT_BAD_ARGS;
    }
    file = fopen(path, "wb");
    if (file == NULL) {
        fail(ACT_IO_ERROR, "meta", "cannot open");
        return ACT_IO_ERROR;
    }
    fprintf(file,
            "{\"schema\":\"speex-agc-activity-cli/1\",\"frames\":%zu,"
            "\"config\":{\"agc\":%d,\"vad\":%d,\"denoise\":%d,\"target\":%d,"
            "\"increment\":%d,\"decrement\":%d,\"max_gain\":%d,"
            "\"prob_start\":%d,\"prob_continue\":%d,\"noise_suppress\":%d},"
            "\"records\":[",
            frames, config->agc, config->vad, config->denoise, config->target,
            config->increment, config->decrement, config->max_gain,
            config->prob_start, config->prob_continue, config->noise_suppress);
    for (frame = 0; frame < frames; ++frame) {
        fprintf(file,
                "%s{\"frame\":%zu,\"reset\":%d,\"vad\":%d,"
                "\"agc_gain_db\":%d,\"prob_percent\":%d,\"agc_loudness\":%d}",
                (frame == 0) ? "" : ",", frame, reset[frame], vad[frame],
                gain[frame], prob[frame], loudness[frame]);
    }
    fputs("]}\n", file);
    if (ferror(file) || fclose(file) != 0) {
        fail(ACT_IO_ERROR, "meta", "short write");
        return ACT_IO_ERROR;
    }
    return ACT_OK;
}

static int self_test(void)
{
    act_config config;
    SpeexPreprocessState *state = NULL;
    int16_t pcm[ACT_FRAME_SAMPLES];
    int gain = 0;
    int frame = 0;
    int speech = 0;
    int status = ACT_OK;

    memset(&config, 0, sizeof(config));
    config.agc = 1;
    config.vad = 1;
    config.target = 8192;
    config.increment = 12;
    config.decrement = 40;
    config.max_gain = 30;
    config.prob_start = 35;
    config.prob_continue = 20;
    config.noise_suppress = -20;
    state = make_state(&config);
    if (state == NULL) {
        fail(ACT_BACKEND_ERROR, "state", "init failed");
        return ACT_BACKEND_ERROR;
    }
    for (frame = 0; frame < 4; ++frame) {
        int i = 0;
        for (i = 0; i < ACT_FRAME_SAMPLES; ++i) {
            pcm[i] = clamp_to_pcm16(0.25F * (float)sin(2.0 * 3.14159265358979323846 * 220.0 *
                                                     (double)(frame * ACT_FRAME_SAMPLES + i) /
                                                     (double)ACT_RATE_HZ));
        }
        speech = speex_preprocess_run(state, pcm);
        for (i = 0; i < ACT_FRAME_SAMPLES; ++i) {
            if (!isfinite((float)pcm[i])) {
                status = ACT_BACKEND_ERROR;
            }
        }
    }
    if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_GET_AGC_GAIN, &gain) != 0) {
        status = ACT_BACKEND_ERROR;
    }
    speex_preprocess_state_destroy(state);
    if (status == ACT_OK) {
        printf("SELFTEST OK gain_db=%d vad=%d\n", gain, speech);
    } else {
        fail(status, "output", "nonfinite");
    }
    return status;
}

int main(int argc, char **argv)
{
    act_config config;
    const char *input_path = NULL;
    const char *output_path = NULL;
    const char *meta_path = NULL;
    float *samples = NULL;
    float *output = NULL;
    int *vad = NULL;
    int *gain = NULL;
    int *prob = NULL;
    int *loudness = NULL;
    int *reset = NULL;
    SpeexPreprocessState *state = NULL;
    size_t count = 0;
    size_t frames = 0;
    size_t frame = 0;
    size_t index = 0;
    int arg = 1;
    int status = ACT_OK;
    int reset_index = 0;

    memset(&config, 0, sizeof(config));
    config.agc = 1;
    config.vad = 1;
    config.target = 8192;
    config.increment = 12;
    config.decrement = 40;
    config.max_gain = 30;
    config.prob_start = 35;
    config.prob_continue = 20;
    config.noise_suppress = -20;

    if (argc == 2 && strcmp(argv[1], "--self-test") == 0) {
        return self_test();
    }
    while (arg < argc) {
        const char *key = argv[arg];
        if (arg + 1 >= argc) {
            fail(ACT_BAD_ARGS, key, "missing value");
            return ACT_BAD_ARGS;
        }
        if (strcmp(key, "--input") == 0) {
            input_path = argv[++arg];
        } else if (strcmp(key, "--output") == 0) {
            output_path = argv[++arg];
        } else if (strcmp(key, "--meta") == 0) {
            meta_path = argv[++arg];
        } else if (strcmp(key, "--agc") == 0) {
            if (!parse_flag(argv[++arg], &config.agc)) {
                fail(ACT_BAD_ARGS, "--agc", "expected 0 or 1");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--vad") == 0) {
            if (!parse_flag(argv[++arg], &config.vad)) {
                fail(ACT_BAD_ARGS, "--vad", "expected 0 or 1");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--denoise") == 0) {
            if (!parse_flag(argv[++arg], &config.denoise)) {
                fail(ACT_BAD_ARGS, "--denoise", "expected 0 or 1");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--target") == 0) {
            if (!parse_int(argv[++arg], &config.target) || config.target < 1 ||
                    config.target > 32768) {
                fail(ACT_BAD_ARGS, "--target", "expected 1..32768");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--increment") == 0) {
            if (!parse_int(argv[++arg], &config.increment) || config.increment < 1 ||
                    config.increment > 120) {
                fail(ACT_BAD_ARGS, "--increment", "expected 1..120");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--decrement") == 0) {
            if (!parse_int(argv[++arg], &config.decrement) || config.decrement < 1 ||
                    config.decrement > 120) {
                fail(ACT_BAD_ARGS, "--decrement", "expected 1..120");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--max-gain") == 0) {
            if (!parse_int(argv[++arg], &config.max_gain) || config.max_gain < 1 ||
                    config.max_gain > 60) {
                fail(ACT_BAD_ARGS, "--max-gain", "expected 1..60");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--prob-start") == 0) {
            if (!parse_int(argv[++arg], &config.prob_start) || config.prob_start < 0 ||
                    config.prob_start > 100) {
                fail(ACT_BAD_ARGS, "--prob-start", "expected 0..100");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--prob-continue") == 0) {
            if (!parse_int(argv[++arg], &config.prob_continue) || config.prob_continue < 0 ||
                    config.prob_continue > 100) {
                fail(ACT_BAD_ARGS, "--prob-continue", "expected 0..100");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--noise-suppress") == 0) {
            if (!parse_int(argv[++arg], &config.noise_suppress) || config.noise_suppress < -40 ||
                    config.noise_suppress > 0) {
                fail(ACT_BAD_ARGS, "--noise-suppress", "expected -40..0");
                return ACT_BAD_ARGS;
            }
        } else if (strcmp(key, "--reset-frames") == 0) {
            if (!parse_resets(argv[++arg], &config)) {
                fail(ACT_BAD_ARGS, "--reset-frames", "expected ascending frame indices");
                return ACT_BAD_ARGS;
            }
        } else {
            fail(ACT_BAD_ARGS, key, "unknown option");
            return ACT_BAD_ARGS;
        }
        ++arg;
    }
    if (input_path == NULL || output_path == NULL || meta_path == NULL) {
        fail(ACT_BAD_ARGS, "arguments", "--input, --output and --meta are required");
        return ACT_BAD_ARGS;
    }
    if (fesetround(FE_TONEAREST) != 0 || fegetround() != FE_TONEAREST) {
        fail(ACT_BACKEND_ERROR, "fenv", "FE_TONEAREST unavailable");
        return ACT_BACKEND_ERROR;
    }
    status = read_f32(input_path, &samples, &count);
    if (status != ACT_OK) {
        return status;
    }
    frames = count / ACT_FRAME_SAMPLES;
    output = (float *)malloc(count * sizeof(float));
    vad = (int *)malloc(frames * sizeof(int));
    gain = (int *)malloc(frames * sizeof(int));
    prob = (int *)malloc(frames * sizeof(int));
    loudness = (int *)malloc(frames * sizeof(int));
    reset = (int *)calloc(frames, sizeof(int));
    if (output == NULL || vad == NULL || gain == NULL || prob == NULL ||
            loudness == NULL || reset == NULL) {
        fail(ACT_BACKEND_ERROR, "memory", "allocation failed");
        status = ACT_BACKEND_ERROR;
        goto done;
    }
    state = make_state(&config);
    if (state == NULL) {
        fail(ACT_BACKEND_ERROR, "state", "init failed");
        status = ACT_BACKEND_ERROR;
        goto done;
    }
    for (frame = 0; frame < frames; ++frame) {
        int16_t pcm[ACT_FRAME_SAMPLES];
        if (reset_index < config.reset_count && config.resets[reset_index] == frame) {
            speex_preprocess_state_destroy(state);
            state = make_state(&config);
            if (state == NULL) {
                fail(ACT_BACKEND_ERROR, "state", "reset failed");
                status = ACT_BACKEND_ERROR;
                goto done;
            }
            reset[frame] = 1;
            ++reset_index;
        }
        for (index = 0; index < ACT_FRAME_SAMPLES; ++index) {
            pcm[index] = clamp_to_pcm16(samples[frame * ACT_FRAME_SAMPLES + index]);
        }
        vad[frame] = speex_preprocess_run(state, pcm);
        if (vad[frame] != 0 && vad[frame] != 1) {
            fail(ACT_BACKEND_ERROR, "vad", "unexpected return value");
            status = ACT_BACKEND_ERROR;
            goto done;
        }
        if (speex_preprocess_ctl(state, SPEEX_PREPROCESS_GET_AGC_GAIN, &gain[frame]) != 0 ||
                speex_preprocess_ctl(state, SPEEX_PREPROCESS_GET_PROB, &prob[frame]) != 0 ||
                speex_preprocess_ctl(state, SPEEX_PREPROCESS_GET_AGC_LOUDNESS,
                                     &loudness[frame]) != 0) {
            fail(ACT_BACKEND_ERROR, "ctl", "getter failed");
            status = ACT_BACKEND_ERROR;
            goto done;
        }
        for (index = 0; index < ACT_FRAME_SAMPLES; ++index) {
            output[frame * ACT_FRAME_SAMPLES + index] = (float)pcm[index] / 32768.0F;
        }
    }
    status = write_f32(output_path, output, count);
    if (status != ACT_OK) {
        goto done;
    }
    status = write_meta(meta_path, &config, frames, vad, gain, prob, loudness, reset);

done:
    if (state != NULL) {
        speex_preprocess_state_destroy(state);
    }
    free(samples);
    free(output);
    free(vad);
    free(gain);
    free(prob);
    free(loudness);
    free(reset);
    return status;
}
