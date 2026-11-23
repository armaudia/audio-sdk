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
#define PROVIDER_ID "dsp.adaptive-notch-notchref.v0"

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
    return sqrt(total / AS_FRAME_SAMPLES);
}

#ifdef AS_ENABLE_ADAPTIVE_NOTCH
as_status_v0 adaptive_notch_register(as_registry_v0 *registry, as_error_v0 *error);

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0;
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
    create.epoch = 1;
    create.first_input_sample = 42;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    create.config_json = NULL;
    create.config_json_length = 0;
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
    for (uint32_t frame = 0; frame < 6; ++frame) {
        CHECK(feed(session, 42 + (int64_t)frame * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.source_first_sample == 42 + (int64_t)frame * AS_FRAME_SAMPLES);
        CHECK(frame_rms(output) == 0.0);
    }

    double first_tone_energy = 0.0;
    double last_tone_energy = 0.0;
    for (uint32_t frame = 0; frame < 48; ++frame) {
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            const double phase = 2.0 * PI * 1000.0 *
                                 (double)(frame * AS_FRAME_SAMPLES + index) / 16000.0;
            samples[index] = (float)(0.1 * sin(phase));
        }
        CHECK(feed(session, 42 + (int64_t)(6 + frame) * AS_FRAME_SAMPLES,
                   samples, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index)
            CHECK(isfinite((double)output[index]));
        if (frame < 3) first_tone_energy += frame_rms(output);
        if (frame >= 40) last_tone_energy += frame_rms(output);
    }
    CHECK(first_tone_energy > 0.0);
    CHECK(last_tone_energy / first_tone_energy < 0.20);

    CHECK(as_session_reset_v0(session, 2, 42, error) == AS_OK);
    memset(samples, 0, sizeof(samples));
    CHECK(feed_epoch(session, 2, 42, samples, output, &result) == AS_OK);
    CHECK(frame_rms(output) == 0.0);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);
    puts("optional reference registered, tone attenuated, reset/drain/close passed");
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
#ifndef AS_ENABLE_ADAPTIVE_NOTCH
    puts("optional reference unlinked and unregistered; built-ins unchanged");
#else
    CHECK(adaptive_notch_register(registry, &error) == AS_OK);
    CHECK(query(registry, PROVIDER_ID) == AS_OK);
    CHECK(adaptive_notch_register(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PROVIDER_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
