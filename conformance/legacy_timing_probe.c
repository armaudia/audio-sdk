/*
 * Historical baseline timing probe (S02 evidence).
 *
 * Purpose: measure the actual content lag of the legacy v1 Speex and
 * high-pass chains against the buffering delay those chains declare. This
 * probe links the *original* application ABI 1.1 library and is retained as
 * failing-before evidence. It is not part of the installed v0 package and it
 * is not the conformance executable.
 *
 * Fixture: deterministic broadband signed marker bursts generated from the
 * fixed integer seed 20261113, surrounded by digital silence. The lag is the
 * unique normalized-correlation peak within a bounded range; an ambiguous or
 * missing peak fails the mapping rather than guessing.
 *
 * Usage: legacy_timing_probe [output.json]
 */

#include <audio_enhance/audio_enhance.h>

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FRAME 160u
#define FRAMES 40u
#define TOTAL (FRAME * FRAMES)
#define MAX_LAG 640

static uint64_t g_state = 20261113ull;

static uint32_t next_u32(void) {
    /* xorshift64*, integer only, reproducible across platforms. */
    g_state ^= g_state >> 12;
    g_state ^= g_state << 25;
    g_state ^= g_state >> 27;
    return (uint32_t)((g_state * 2685821657736338717ull) >> 32);
}

static void make_fixture(float *out) {
    memset(out, 0, TOTAL * sizeof(float));
    /* Two bursts at different origins exercise non-zero start positions. */
    const uint32_t starts[2] = {640u, 3200u};
    for (int b = 0; b < 2; ++b) {
        for (uint32_t i = 0; i < 320; ++i) {
            const float value = ((float)(next_u32() % 2001u) - 1000.0f) / 1000.0f;
            out[starts[b] + i] = 0.25f * value;
        }
    }
}

static ae_context_v1 *make_context(void) {
    ae_context_config_v1 config;
    ae_context_config_v1_init(&config);
    ae_error_v1 error;
    ae_error_v1_init(&error);
    ae_context_v1 *context = NULL;
    if (ae_context_create_v1(&config, &context, &error) != AE_OK) {
        fprintf(stderr, "context: %s\n", error.message);
        return NULL;
    }
    return context;
}

static ae_session_v1 *make_session(ae_context_v1 *context, uint32_t preset,
                                   const char *stage) {
    ae_recipe_v1 *recipe = NULL;
    ae_error_v1 error;
    ae_error_v1_init(&error);
    const unsigned recipe_stage = preset == AE_PRESET_CUSTOM;
    if (recipe_stage) {
        if (ae_recipe_create_v1(&recipe, &error) != AE_OK) return NULL;
        if (ae_recipe_add_stage_v1(recipe, stage, "probe", "", &error) != AE_OK) {
            fprintf(stderr, "recipe: %s\n", error.message);
            ae_recipe_destroy_v1(&recipe);
            return NULL;
        }
    }
    ae_session_config_v1 config;
    ae_session_config_v1_init(&config);
    config.sample_rate_hz = 16000;
    config.channels = 1;
    config.frames_per_call = FRAME;
    config.execution = AE_EXECUTION_INLINE_PROCESSING_THREAD;
    config.preset_id = preset;
    config.recipe = recipe;
    config.flags = AE_SESSION_ALLOW_EXPERIMENTAL;
    ae_session_v1 *session = NULL;
    const ae_status status = ae_session_create_v1(context, &config, &session, &error);
    if (recipe != NULL) ae_recipe_destroy_v1(&recipe);
    if (status != AE_OK) {
        fprintf(stderr, "create %s: %s %s\n", stage, error.message, error.hint);
        return NULL;
    }
    return session;
}

static int run_chain(ae_context_v1 *context, uint32_t preset, const char *stage,
                     const float *fixture, float *output, uint32_t *declared_delay) {
    ae_session_v1 *session = make_session(context, preset, stage);
    if (session == NULL) return 0;
    ae_session_info_v1 info;
    ae_session_info_v1_init(&info);
    if (ae_session_get_info_v1(session, &info) != AE_OK) return 0;
    *declared_delay = info.content_delay_samples;
    float input[FRAME];
    ae_error_v1 error;
    ae_error_v1_init(&error);
    for (uint32_t f = 0; f < FRAMES; ++f) {
        ae_frame_result_v1 result;
        ae_frame_result_v1_init(&result);
        memcpy(input, fixture + f * FRAME, sizeof(input));
        const ae_status status = ae_session_process_f32_v1(
            session, input, FRAME, output + f * FRAME, FRAME, NULL, &result);
        if (status != AE_OK) {
            fprintf(stderr, "process %s frame %u: %d %s\n", stage, f, (int)status,
                    error.message);
            ae_session_close_v1(&session);
            return 0;
        }
    }
    ae_session_close_v1(&session);
    return 1;
}

/* Normalized correlation of output against input at candidate lag. */
static double correlation(const float *output, const float *input, int lag,
                          int *overlap) {
    double dot = 0.0, out_energy = 0.0, in_energy = 0.0;
    int count = 0;
    for (int n = 0; n < (int)TOTAL; ++n) {
        const int m = n - lag;
        if (m < 0 || m >= (int)TOTAL) continue;
        const double o = output[n];
        const double i = input[m];
        dot += o * i;
        out_energy += o * o;
        in_energy += i * i;
        ++count;
    }
    *overlap = count;
    if (out_energy <= 0.0 || in_energy <= 0.0) return 0.0;
    return dot / sqrt(out_energy * in_energy);
}

static int measure_lag(const float *output, const float *input, int *lag_out,
                       double *peak_out, double *second_out) {
    int best_lag = 0;
    double best = -2.0;
    double second = -2.0;
    for (int lag = -MAX_LAG; lag <= MAX_LAG; ++lag) {
        int overlap = 0;
        double r = correlation(output, input, lag, &overlap);
        /* Require at least 10 ms of overlap so edge lags cannot win. */
        if (overlap < (int)FRAME) r = -2.0;
        if (r > best) {
            second = best;
            best = r;
            best_lag = lag;
        } else if (r > second) {
            second = r;
        }
    }
    *lag_out = best_lag;
    *peak_out = best;
    *second_out = second;
    /* A mapping is accepted only with a strong and unique peak. */
    return best >= 0.9 && (best - second) >= 0.05;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : NULL;
    ae_context_v1 *context = make_context();
    if (context == NULL) return 2;

    static float fixture[TOTAL];
    static float identity_out[TOTAL];
    static float speex_out[TOTAL];
    static float highpass_out[TOTAL];
    make_fixture(fixture);

    uint32_t identity_declared = 0, speex_declared = 0, highpass_declared = 0;
    if (!run_chain(context, AE_PRESET_IDENTITY_V1, "identity", fixture, identity_out,
                   &identity_declared)) {
        return 2;
    }
    if (!run_chain(context, AE_PRESET_CUSTOM, "speex.ns_activity", fixture, speex_out,
                   &speex_declared)) {
        return 2;
    }
    if (!run_chain(context, AE_PRESET_CUSTOM, "dsp.highpass", fixture, highpass_out,
                   &highpass_declared)) {
        return 2;
    }
    ae_context_close_v1(&context);

    int identity_lag = 0, speex_lag = 0, highpass_lag = 0;
    double ip = 0, is = 0, sp = 0, ss = 0, hp = 0, hs = 0;
    const int identity_ok = measure_lag(identity_out, fixture, &identity_lag, &ip, &is);
    const int speex_ok = measure_lag(speex_out, fixture, &speex_lag, &sp, &ss);
    const int highpass_ok = measure_lag(highpass_out, fixture, &highpass_lag, &hp, &hs);

    printf("identity   declared=%u measured=%d peak=%.6f second=%.6f %s\n",
           identity_declared, identity_lag, ip, is, identity_ok ? "ok" : "ambiguous");
    printf("speex.ns   declared=%u measured=%d peak=%.6f second=%.6f %s\n",
           speex_declared, speex_lag, sp, ss, speex_ok ? "ok" : "ambiguous");
    printf("highpass   declared=%u measured=%d peak=%.6f second=%.6f %s\n",
           highpass_declared, highpass_lag, hp, hs, highpass_ok ? "ok" : "ambiguous");

    const int consistent = identity_ok && speex_ok && highpass_ok &&
                           identity_lag == (int)identity_declared &&
                           speex_lag == (int)speex_declared &&
                           highpass_lag == (int)highpass_declared;
    printf("timing_consistent=%s\n", consistent ? "true" : "false");

    if (path != NULL) {
        FILE *f = fopen(path, "w");
        if (f == NULL) return 2;
        fprintf(f,
                "{\"probe\":\"legacy_timing_probe\",\"abi\":\"%u.%u\",\"seed\":20261113,"
                "\"frames\":%u,\"max_lag\":%d,\"chains\":[",
                AE_ABI_MAJOR, AE_ABI_MINOR, (unsigned)FRAMES, MAX_LAG);
        fprintf(f,
                "{\"id\":\"identity\",\"declared_delay_samples\":%u,"
                "\"measured_lag_samples\":%d,\"peak\":%.6f,\"second\":%.6f,"
                "\"unique_peak\":%s},",
                identity_declared, identity_lag, ip, is, identity_ok ? "true" : "false");
        fprintf(f,
                "{\"id\":\"speex.ns_activity\",\"declared_delay_samples\":%u,"
                "\"measured_lag_samples\":%d,\"peak\":%.6f,\"second\":%.6f,"
                "\"unique_peak\":%s},",
                speex_declared, speex_lag, sp, ss, speex_ok ? "true" : "false");
        fprintf(f,
                "{\"id\":\"dsp.highpass\",\"declared_delay_samples\":%u,"
                "\"measured_lag_samples\":%d,\"peak\":%.6f,\"second\":%.6f,"
                "\"unique_peak\":%s}],\"timing_consistent\":%s}\n",
                highpass_declared, highpass_lag, hp, hs, highpass_ok ? "true" : "false",
                consistent ? "true" : "false");
        fclose(f);
    }
    return consistent ? 0 : 1;
}
