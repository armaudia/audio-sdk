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
#define LOGISTIC_ID "dsp.logistic-feedback-reference.v0"
#define STATIC_ID "dsp.logistic-feedback-static.v0"
#define STATIC_GAIN 0.5623413251903491

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
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
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
        total += (double)samples[index] * samples[index];
    return sqrt(total / (double)AS_FRAME_SAMPLES);
}

static void tone_frame(uint32_t frame, float *samples) {
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        const double phase = 2.0 * PI * 1200.0 *
            (double)(frame * AS_FRAME_SAMPLES + index) / 16000.0;
        samples[index] = (float)(0.12 * sin(phase));
    }
}

#ifdef AS_ENABLE_LOGISTIC_FEEDBACK
as_status_v0 logistic_feedback_register(as_registry_v0 *registry,
                                        as_error_v0 *error);

static int effective(as_registry_v0 *registry, const char *id, char *buffer,
                     uint32_t capacity, uint32_t *required, as_error_v0 *error) {
    CHECK(as_effective_config_create_v0(registry, id, (uint32_t)strlen(id),
          AS_MODE_INLINE_CALLBACK, buffer, capacity, required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, id, (uint32_t)strlen(id),
          AS_MODE_BUFFERED_WORKER, buffer, capacity, required, error) == AS_UNSUPPORTED);
    return as_effective_config_create_v0(registry, id, (uint32_t)strlen(id),
                                         AS_MODE_PROCESSING_THREAD, buffer, capacity,
                                         required, error);
}

static as_session_v0 *make_session(as_registry_v0 *registry, const char *id,
                                   char *config, int64_t first_sample,
                                   as_error_v0 *error) {
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = first_sample;
    create.config_json = config;
    create.config_json_length = (uint32_t)strlen(config);
    as_session_v0 *session = NULL;
    if (as_session_create_v0(registry, id, (uint32_t)strlen(id), &create,
                             &session, error) != AS_OK) {
        return NULL;
    }
    return session;
}

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char logistic_config[2048];
    char static_config[2048];
    uint32_t logistic_required = 0;
    uint32_t static_required = 0;
    CHECK(effective(registry, LOGISTIC_ID, logistic_config, sizeof(logistic_config),
                    &logistic_required, error) == AS_OK);
    CHECK(effective(registry, STATIC_ID, static_config, sizeof(static_config),
                    &static_required, error) == AS_OK);

    float samples[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(samples, 0, sizeof(samples));

    as_session_v0 *static_session = make_session(
        registry, STATIC_ID, static_config, 42, error);
    CHECK(static_session != NULL);
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
        samples[index] = (float)(0.1 * sin(2.0 * PI * 1000.0 *
                                           (double)index / 16000.0));
    CHECK(feed(static_session, 42, samples, output, &result) == AS_OK);
    CHECK(result.valid_count == AS_FRAME_SAMPLES);
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
        CHECK(fabs((double)output[index] - (double)samples[index] * STATIC_GAIN) < 1e-6);
    CHECK(as_session_close_v0(&static_session) == AS_OK);

    as_session_v0 *logistic_session = make_session(
        registry, LOGISTIC_ID, logistic_config, 42, error);
    CHECK(logistic_session != NULL);
    double first_energy = 0.0;
    double last_energy = 0.0;
    for (uint32_t frame = 0; frame < 80; ++frame) {
        tone_frame(frame, samples);
        CHECK(feed(logistic_session, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
            CHECK(isfinite((double)output[index]));
        if (frame < 3) first_energy += frame_rms(output);
        if (frame >= 70) last_energy += frame_rms(output);
    }
    CHECK(first_energy > 0.0);
    CHECK(last_energy / 10.0 / (first_energy / 3.0) < 0.80);

    tone_frame(0, samples);
    CHECK(feed(logistic_session, 9000, samples, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed_epoch(logistic_session, 2u, 42 + (int64_t)80 * AS_FRAME_SAMPLES,
                     samples, output, &result) == AS_INVALID_ARGUMENT);
    samples[7] = NAN;
    CHECK(feed(logistic_session, 42 + (int64_t)80 * AS_FRAME_SAMPLES,
               samples, output, &result) == AS_INVALID_ARGUMENT);
    tone_frame(0, samples);

    as_session_v0 *replay_session = make_session(
        registry, LOGISTIC_ID, logistic_config, 42, error);
    CHECK(replay_session != NULL);
    float first_output[AS_FRAME_SAMPLES];
    float later_output[AS_FRAME_SAMPLES];
    tone_frame(0, samples);
    CHECK(feed(logistic_session, 42 + (int64_t)80 * AS_FRAME_SAMPLES,
               samples, later_output, &result) == AS_OK);
    CHECK(feed(replay_session, 42, samples, first_output, &result) == AS_OK);
    CHECK(fabs((double)first_output[9] - (double)samples[9]) < 1e-6);
    CHECK(fabs((double)later_output[9]) < fabs((double)first_output[9]));
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
        CHECK(first_output[index] == later_output[index] ||
              fabs((double)first_output[index] - (double)later_output[index]) < 0.25);

    CHECK(as_session_reset_v0(logistic_session, 3u, 4242, error) == AS_OK);
    CHECK(feed_epoch(logistic_session, 3u, 4242, samples, output, &result) == AS_OK);
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
        CHECK(fabs((double)output[index] - (double)samples[index]) < 1e-6);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_begin_drain_v0(logistic_session) == AS_OK);
    CHECK(as_session_drain_next_v0(logistic_session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&logistic_session) == AS_OK);
    CHECK(as_session_close_v0(&replay_session) == AS_OK);
    puts("optional logistic/static providers registered; gain action, fallback, reset/drain/close passed");
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
    CHECK(query(registry, LOGISTIC_ID) == AS_UNSUPPORTED);
    CHECK(query(registry, STATIC_ID) == AS_UNSUPPORTED);
#ifndef AS_ENABLE_LOGISTIC_FEEDBACK
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(logistic_feedback_register(registry, &error) == AS_OK);
    CHECK(query(registry, LOGISTIC_ID) == AS_OK);
    CHECK(query(registry, STATIC_ID) == AS_OK);
    CHECK(logistic_feedback_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, LOGISTIC_ID) == AS_UNSUPPORTED);
    CHECK(query(other, STATIC_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
