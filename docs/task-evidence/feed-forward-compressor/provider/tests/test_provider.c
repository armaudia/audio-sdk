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
#define PROVIDER_ID "dsp.feed-forward-compressor.ref.v0"
#define TONE_FRAMES 40

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
        const double phase = 2.0 * PI * 1000.0 *
            (double)(start_sample + (int64_t)index) / 16000.0;
        samples[index] = (float)(0.5 * sin(phase));
    }
}

#ifdef AS_ENABLE_FEED_FORWARD_COMPRESSOR
AS_API as_status_v0 AS_CALL feed_forward_compressor_register(
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
    memset(samples, 0, sizeof(samples));
    for (uint32_t frame = 0; frame < 6u; ++frame) {
        CHECK(feed(session, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(frame_rms(output) == 0.0);
    }

    double first_tone_energy = 0.0;
    double last_tone_energy = 0.0;
    for (uint32_t frame = 0; frame < 48u; ++frame) {
        fill_tone(samples, (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(feed(session, 42 + (int64_t)(6u + frame) * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
        }
        if (frame < 3u) first_tone_energy += frame_rms(output);
        if (frame >= 40u) last_tone_energy += frame_rms(output);
    }
    CHECK(first_tone_energy > 0.0);
    /* Steady tone level is ~0.23x the uncompressed 0.5/sqrt(2) RMS. */
    CHECK(last_tone_energy / 8.0 < 0.30 * 0.5 / sqrt(2.0));
    CHECK((last_tone_energy / 8.0) / (first_tone_energy / 3.0) < 0.75);

    /* Rejected frames must not advance the source position or change gain. */
    const int64_t next = 42 + (int64_t)54u * AS_FRAME_SAMPLES;
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
    CHECK(feed(session, next, samples, output, &result) == AS_OK);
    CHECK(result.source_first_sample == next);

    /* Reset and a fresh session must produce identical output for the same tone. */
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

    /* Final partial frame and drain mapping. */
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

    CHECK(as_session_close_v0(&final_session) == AS_OK);
    CHECK(final_session == NULL);
    CHECK(as_session_close_v0(&fresh) == AS_OK);
    CHECK(fresh == NULL);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered; gain reduced, reset/session/drain checks passed");
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
#ifndef AS_ENABLE_FEED_FORWARD_COMPRESSOR
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(feed_forward_compressor_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(feed_forward_compressor_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
