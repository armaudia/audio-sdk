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

#define DE_PI 3.14159265358979323846
#define PROVIDER_ID "dsp.de-esser.ref.v0"
#define TONE_FRAMES 20
#define TONE_FRAMES_LONG 48

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0u, NULL);
}

static as_status_v0 feed_epoch(as_session_v0 *session, uint64_t epoch,
                               int64_t first_sample, const float *samples,
                               float *output, as_result_v0 *result) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = samples;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    frame.epoch = epoch;
    frame.first_input_sample = first_sample;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return as_session_process_v0(session, &frame, &sink, result);
}

static as_status_v0 feed(as_session_v0 *session, int64_t first_sample,
                         const float *samples, float *output,
                         as_result_v0 *result) {
    return feed_epoch(session, 1u, first_sample, samples, output, result);
}

static double frame_rms(const float *samples) {
    double total = 0.0;
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        total += (double)samples[index] * samples[index];
    }
    return sqrt(total / (double)AS_FRAME_SAMPLES);
}

static void fill_tone(float *samples, int64_t start_sample) {
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double phase = 2.0 * DE_PI * 6500.0 *
            (double)(start_sample + (int64_t)index) / 16000.0;
        samples[index] = (float)(0.22 * sin(phase));
    }
}

#ifdef AS_ENABLE_DE_ESSER
AS_API as_status_v0 AS_CALL de_esser_register(
    as_registry_v0 *registry, as_error_v0 *error);

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

    float samples[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);

    /* Silence is reproduced exactly, with no state-driven offset. */
    memset(samples, 0, sizeof(samples));
    for (uint32_t frame = 0; frame < 6u; ++frame) {
        CHECK(feed(session, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(frame_rms(output) == 0.0);
    }

    /* A low-band step is preserved at steady state. */
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) samples[index] = 0.7f;
    double steady_step = 0.0;
    for (uint32_t frame = 0; frame < 12u; ++frame) {
        CHECK(feed(session, 42 + (int64_t)(6u + frame) * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        if (frame >= 8u) steady_step += frame_rms(output);
    }
    CHECK(fabs(steady_step / 4.0 - 0.7) < 0.01);

    /* Sibilance-band tone is attenuated; no nonfinite samples appear. */
    double early_tone_energy = 0.0;
    double late_tone_energy = 0.0;
    for (uint32_t frame = 0; frame < TONE_FRAMES_LONG; ++frame) {
        fill_tone(samples, (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(feed(session, 42 + (int64_t)(18u + frame) * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
        }
        if (frame < 3u) early_tone_energy += frame_rms(output);
        if (frame >= 40u) late_tone_energy += frame_rms(output);
    }
    CHECK(early_tone_energy > 0.0);
    const double unmodified_tone_rms = 0.22 / sqrt(2.0);
    CHECK(late_tone_energy / 8.0 < 0.85 * unmodified_tone_rms);
    CHECK((late_tone_energy / 8.0) < (early_tone_energy / 3.0));

    int64_t next = 42 + (int64_t)(18u + TONE_FRAMES_LONG) * AS_FRAME_SAMPLES;
    fill_tone(samples, 0);
    samples[7] = NAN;
    CHECK(feed(session, next, samples, output, &result) == AS_INVALID_ARGUMENT);
    samples[7] = 0.5f;
    CHECK(feed_epoch(session, 2u, next, samples, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, next + 1000, samples, output, &result) == AS_INVALID_ARGUMENT);
    as_frame_v0 short_frame;
    as_frame_v0_init(&short_frame);
    short_frame.input = samples;
    short_frame.input_count = AS_FRAME_SAMPLES - 1u;
    short_frame.input_valid_count = AS_FRAME_SAMPLES - 1u;
    short_frame.epoch = 1u;
    short_frame.first_input_sample = next;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_process_v0(session, &short_frame, &sink, &result) == AS_INVALID_ARGUMENT);

    /* Rejection did not advance the source position. */
    fill_tone(samples, 0);
    CHECK(feed(session, next, samples, output, &result) == AS_OK);
    CHECK(result.source_first_sample == next);

    /* Reset and a fresh session produce identical output for the same tone. */
    float reset_outputs[TONE_FRAMES * AS_FRAME_SAMPLES];
    float fresh_outputs[TONE_FRAMES * AS_FRAME_SAMPLES];
    CHECK(as_session_reset_v0(session, 2u, 0, error) == AS_OK);
    CHECK(as_session_reset_v0(session, 2u, 0, error) == AS_INVALID_ARGUMENT);
    for (uint32_t frame = 0; frame < TONE_FRAMES; ++frame) {
        fill_tone(samples, (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(feed_epoch(session, 2u, (int64_t)frame * AS_FRAME_SAMPLES,
                         samples, output, &result) == AS_OK);
        memcpy(reset_outputs + frame * AS_FRAME_SAMPLES, output, sizeof(output));
    }
    as_session_v0 *fresh = NULL;
    create.first_input_sample = 0;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &fresh, error) == AS_OK);
    for (uint32_t frame = 0; frame < TONE_FRAMES; ++frame) {
        fill_tone(samples, (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(feed(fresh, (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        memcpy(fresh_outputs + frame * AS_FRAME_SAMPLES, output, sizeof(output));
    }
    CHECK(memcmp(reset_outputs, fresh_outputs, sizeof(reset_outputs)) == 0);

    /* Final partial frame, bad padding, drain and lifecycle mapping. */
    as_session_v0 *final_session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &final_session, error) == AS_OK);
    memset(samples, 0, sizeof(samples));
    samples[4] = 0.25f;
    as_frame_v0 final_frame;
    as_frame_v0_init(&final_frame);
    final_frame.input = samples;
    final_frame.input_count = AS_FRAME_SAMPLES;
    final_frame.input_valid_count = 5u;
    final_frame.flags = AS_FRAME_FINAL_INPUT;
    final_frame.epoch = 1u;
    final_frame.first_input_sample = 0;
    CHECK(as_session_process_v0(final_session, &final_frame, &sink, &result) == AS_OK);
    CHECK(result.valid_count == 5u);
    CHECK(result.source_first_sample == 0);
    CHECK(as_session_begin_drain_v0(final_session) == AS_OK);
    CHECK(as_session_process_v0(final_session, &final_frame, &sink, &result) == AS_INVALID_ARGUMENT);
    CHECK(as_session_drain_next_v0(final_session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_drain_next_v0(final_session, &sink, &result) == AS_END_OF_STREAM);

    /* Out-of-range input reaches the provider and fails closed there; the SDK
     * maps that rejection to a backend failure and requires a reset. */
    as_session_v0 *range_session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &range_session, error) == AS_OK);
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) samples[index] = 9.0f;
    CHECK(feed(range_session, 0, samples, output, &result) == AS_BACKEND_FAILURE);
    CHECK(feed(range_session, 0, samples, output, &result) == AS_NEEDS_RESET);
    CHECK(as_session_reset_v0(range_session, 2u, 0, error) == AS_OK);
    memset(samples, 0, sizeof(samples));
    CHECK(feed_epoch(range_session, 2u, 0, samples, output, &result) == AS_OK);
    CHECK(as_session_close_v0(&range_session) == AS_OK);
    CHECK(range_session == NULL);

    as_session_v0 *padding_session = NULL;
    CHECK(as_session_create_v0(registry, PROVIDER_ID,
           (uint32_t)strlen(PROVIDER_ID), &create, &padding_session, error) == AS_OK);
    memset(samples, 0, sizeof(samples));
    samples[4] = 0.25f;
    samples[159] = 0.5f;
    CHECK(as_session_process_v0(padding_session, &final_frame, &sink, &result) == AS_INVALID_ARGUMENT);

    CHECK(as_session_close_v0(&padding_session) == AS_OK);
    CHECK(padding_session == NULL);
    CHECK(as_session_close_v0(&final_session) == AS_OK);
    CHECK(final_session == NULL);
    CHECK(as_session_close_v0(&fresh) == AS_OK);
    CHECK(fresh == NULL);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered; sibilance reduced, preservation and boundary checks passed");
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
#ifndef AS_ENABLE_DE_ESSER
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(de_esser_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(de_esser_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
