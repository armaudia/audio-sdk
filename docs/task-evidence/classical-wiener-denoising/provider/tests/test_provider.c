/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define PI 3.14159265358979323846
#define PROVIDER_ID "enh.wiener-reference.v0"
#define NOISE_FRAMES 10u

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

static void frame_init(as_frame_v0 *frame, uint64_t epoch, int64_t first,
                       const float *samples, uint32_t valid, uint32_t flags) {
    as_frame_v0_init(frame);
    frame->input = samples;
    frame->input_count = AS_FRAME_SAMPLES;
    frame->input_valid_count = valid;
    frame->flags = flags;
    frame->epoch = epoch;
    frame->first_input_sample = first;
}

static as_status_v0 feed(as_session_v0 *session, uint64_t epoch, int64_t first,
                         const float *samples, uint32_t valid, uint32_t flags,
                         float *output, as_result_v0 *result) {
    as_frame_v0 frame;
    frame_init(&frame, epoch, first, samples, valid, flags);
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return as_session_process_v0(session, &frame, &sink, result);
}

static double frame_rms(const float *samples, uint32_t count) {
    double total = 0.0;
    for (uint32_t index = 0u; index < count; ++index)
        total += (double)samples[index] * (double)samples[index];
    return sqrt(total / (double)count);
}

static uint32_t lcg_state = 7102u;
static double next_noise(void) {
    lcg_state = (uint32_t)((1664525ull * lcg_state + 1013904223ull) & 0xffffffffull);
    return (double)lcg_state / 2147483648.0 - 1.0;
}

static void noisy_frame(uint32_t frame, float *samples, int include_tone) {
    static double lowpass = 0.0;
    for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        const uint64_t sample = (uint64_t)frame * AS_FRAME_SAMPLES + index;
        lowpass = 0.55 * lowpass + 0.45 * next_noise();
        const double tone = include_tone
                                ? 0.06 * sin(2.0 * PI * 220.0 * (double)sample / 16000.0)
                                : 0.0;
        samples[index] = (float)(tone + 0.085 * lowpass);
    }
}

#ifdef AS_ENABLE_WIENER
as_status_v0 wiener_register(as_registry_v0 *registry, as_error_v0 *error);

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_INLINE_CALLBACK,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_BUFFERED_WORKER,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), AS_MODE_PROCESSING_THREAD,
          config, sizeof(config), &required, error) == AS_OK);

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 42;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    create.config_json = NULL;
    create.config_json_length = 0u;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), &create, &session, error) == AS_INVALID_ARGUMENT);
    create.config_json = config;
    create.config_json_length = required - 1u;

    CHECK(as_session_create_v0(registry, PROVIDER_ID,
          (uint32_t)strlen(PROVIDER_ID), &create, &session, error) == AS_OK);
    CHECK(session != NULL);

    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);

    /* Noise-only calibration frames pass through bit-exactly while the PSD is estimated. */
    for (uint32_t frame = 0u; frame < NOISE_FRAMES; ++frame) {
        noisy_frame(frame, input, 0);
        CHECK(feed(session, 1u, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index)
            CHECK(output[index] == input[index]);
    }

    double noisy_early = 0.0;
    double clean_early = 0.0;
    double noisy_late = 0.0;
    double clean_late = 0.0;
    for (uint32_t frame = 0u; frame < 40u; ++frame) {
        noisy_frame(NOISE_FRAMES + frame, input, 1);
        CHECK(feed(session, 1u, 42 + (int64_t)(NOISE_FRAMES + frame) * AS_FRAME_SAMPLES,
                   input, AS_FRAME_SAMPLES, 0u, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index)
            CHECK(isfinite((double)output[index]) && fabs((double)output[index]) <= 1.0);
        if (frame < 5u) {
            noisy_early += frame_rms(input, AS_FRAME_SAMPLES);
            clean_early += frame_rms(output, AS_FRAME_SAMPLES);
        }
        if (frame >= 35u) {
            noisy_late += frame_rms(input, AS_FRAME_SAMPLES);
            clean_late += frame_rms(output, AS_FRAME_SAMPLES);
        }
    }
    CHECK(noisy_early > 0.0 && noisy_late > 0.0);
    CHECK(clean_late / noisy_late < 0.95);

    /* Every rejection leaves the next expected sample unchanged. */
    const int64_t next = 42 + (int64_t)(NOISE_FRAMES + 40u) * AS_FRAME_SAMPLES;
    memset(input, 0, sizeof(input));
    input[7] = (float)NAN;
    CHECK(feed(session, 1u, next, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    input[7] = 0.0f;
    CHECK(feed(session, 1u, next, input, AS_FRAME_SAMPLES - 1u, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 2u, next, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 1u, next + 1, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(as_session_reset_v0(session, 1u, 42, error) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 1u, next, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_OK);

    /* Reset is strictly epoch-ordered and replays from the new coordinate. */
    CHECK(as_session_reset_v0(session, 3u, 9000, error) == AS_OK);
    memset(input, 0, sizeof(input));
    CHECK(feed(session, 3u, 9000, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_OK);
    CHECK(frame_rms(output, AS_FRAME_SAMPLES) == 0.0);

    /* Final framing yields exactly the accepted valid samples. */
    memset(input, 0, sizeof(input));
    for (uint32_t index = 0u; index < 37u; ++index) input[index] = 0.01f;
    CHECK(feed(session, 3u, 9000 + (int64_t)AS_FRAME_SAMPLES, input, 37u,
               AS_FRAME_FINAL_INPUT, output, &result) == AS_OK);
    CHECK(result.produced_count == AS_FRAME_SAMPLES);
    CHECK(result.valid_count == 37u);
    CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0u);

    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_drain_next_v0(session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered; calibration, attenuation, rejections, reset, final frame, drain/close passed");
    return 0;
}
#endif

int main(void) {
    as_registry_v0 *registry = NULL;
    as_registry_v0 *other = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(query(registry, "speex.ns.v0") == AS_OK);
    CHECK(query(registry, "dsp.highpass80.v0") == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_UNSUPPORTED);
#ifndef AS_ENABLE_WIENER
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(wiener_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(wiener_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
