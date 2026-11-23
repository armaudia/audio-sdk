/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "narrow_notch_provider.h"

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
    for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
        total += (double)samples[index] * (double)samples[index];
    }
    return sqrt(total / AS_FRAME_SAMPLES);
}

#ifdef AS_ENABLE_NARROW_NOTCH
static int tone_attenuation(as_session_v0 *session, double frequency_hz,
                            uint64_t epoch, int64_t origin, as_error_v0 *error) {
    float samples[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(samples, 0, sizeof(samples));
    for (uint32_t frame = 0; frame < 6; ++frame) {
        CHECK(feed_epoch(session, epoch, origin + (int64_t)frame * AS_FRAME_SAMPLES,
                         samples, output, &result) == AS_OK);
        CHECK(frame_rms(output) == 0.0);
    }
    double first_energy = 0.0;
    double last_energy = 0.0;
    for (uint32_t frame = 0; frame < 64; ++frame) {
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            const double phase = 2.0 * PI * frequency_hz *
                (double)(frame * AS_FRAME_SAMPLES + index) / 16000.0;
            samples[index] = (float)(0.1 * sin(phase));
        }
        CHECK(feed_epoch(session, epoch, origin + (int64_t)(6 + frame) * AS_FRAME_SAMPLES,
                         samples, output, &result) == AS_OK);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        for (uint32_t index = 0; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
        }
        if (frame < 3) first_energy += frame_rms(output);
        if (frame >= 56) last_energy += frame_rms(output);
    }
    (void)error;
    CHECK(first_energy > 0.0);
    CHECK(last_energy / first_energy < 0.05);
    return 0;
}

static int exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    char custom[2048];
    char id[96];
    uint32_t required = 0;

    CHECK(narrow_notch_register_v0(registry, 0.0, 100.0, id, sizeof(id), error) == AS_INVALID_ARGUMENT);
    CHECK(narrow_notch_register_v0(registry, 1000.0, 0.0, id, sizeof(id), error) == AS_INVALID_ARGUMENT);
    CHECK(narrow_notch_register_v0(registry, 1000.0, NAN, id, sizeof(id), error) == AS_INVALID_ARGUMENT);
    CHECK(narrow_notch_register_v0(registry, NAN, 100.0, id, sizeof(id), error) == AS_INVALID_ARGUMENT);
    CHECK(narrow_notch_register_v0(registry, 100.0, 200.0, id, sizeof(id), error) == AS_INVALID_ARGUMENT);

    CHECK(narrow_notch_register_v0(registry, 1000.0, 100.0, id, sizeof(id), error) == AS_OK);
    CHECK(strcmp(id, NN_EXPECTED_ID_1000_100) == 0);
    CHECK(query(registry, NN_EXPECTED_ID_1000_100) == AS_OK);
    CHECK(narrow_notch_register_v0(registry, 1000.0, 100.0, id, sizeof(id), error) == AS_DUPLICATE);

    /* Register the second explicit pair before any session closes registry
     * mutation; the facade freezes registration after first session create. */
    if (narrow_notch_register_v0(registry, 120.0, 12.0, id, sizeof(id), error) != AS_OK) {
        fprintf(stderr, "second register failed: %s / %s\n", error->message, error->field);
        return 1;
    }
    CHECK(strcmp(id, NN_EXPECTED_ID_120_12) == 0);
    CHECK(query(registry, NN_EXPECTED_ID_120_12) == AS_OK);

    as_registry_v0 *other = NULL;
    CHECK(as_registry_create_v0(&other, error) == AS_OK);
    CHECK(query(other, NN_EXPECTED_ID_1000_100) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);

    CHECK(as_effective_config_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), AS_MODE_INLINE_CALLBACK,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), AS_MODE_BUFFERED_WORKER,
          config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), AS_MODE_PROCESSING_THREAD,
          config, sizeof(config), &required, error) == AS_OK);

    /* Frozen facade settings schema: explicit settings are not admitted here;
     * the selection travels in the caller-local provider ID instead. */
    const char *needle = "\"settings\":{}";
    char *position = strstr(config, needle);
    CHECK(position != NULL);
    const char *replacement = "\"settings\":{\"frequency_hz\":\"1000\"}";
    const size_t prefix = (size_t)(position - config);
    const size_t suffix = strlen(position + strlen(needle));
    CHECK(snprintf(custom, sizeof(custom), "%.*s%s%.*s", (int)prefix, config,
                   replacement, (int)suffix, position + strlen(needle)) > 0);
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 42;
    create.config_json = custom;
    create.config_json_length = (uint32_t)strlen(custom);
    as_session_v0 *rejected_session = NULL;
    CHECK(as_session_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), &create,
          &rejected_session, error) == AS_UNSUPPORTED);
    CHECK(rejected_session == NULL);

    create.config_json = config;
    create.config_json_length = required - 1u;
    create.config_json = NULL;
    as_session_v0 *missing_session = NULL;
    CHECK(as_session_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), &create,
          &missing_session, error) == AS_INVALID_ARGUMENT);
    create.config_json = config;
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, NN_EXPECTED_ID_1000_100,
          (uint32_t)strlen(NN_EXPECTED_ID_1000_100), &create, &session, error) == AS_OK);
    CHECK(session != NULL);
    CHECK(tone_attenuation(session, 1000.0, 1u, 42, error) == 0);

    float samples[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(samples, 0, sizeof(samples));
    CHECK(feed_epoch(session, 1u, 42, samples, output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(session, 9999, samples, output, &result) == AS_INVALID_ARGUMENT);
    samples[0] = NAN;
    CHECK(feed(session, 42 + (int64_t)70 * AS_FRAME_SAMPLES,
               samples, output, &result) == AS_INVALID_ARGUMENT);
    samples[0] = 0.0f;
    as_frame_v0 short_frame;
    as_frame_v0_init(&short_frame);
    short_frame.input = samples;
    short_frame.input_count = AS_FRAME_SAMPLES - 1u;
    short_frame.input_valid_count = AS_FRAME_SAMPLES - 1u;
    short_frame.epoch = 1u;
    short_frame.first_input_sample = 42 + (int64_t)70 * AS_FRAME_SAMPLES;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(as_session_process_v0(session, &short_frame, &sink, &result) == AS_INVALID_ARGUMENT);

    CHECK(as_session_reset_v0(session, 2u, 42, error) == AS_OK);
    memset(samples, 0, sizeof(samples));
    CHECK(feed_epoch(session, 2u, 42, samples, output, &result) == AS_OK);
    CHECK(frame_rms(output) == 0.0);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &sink, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);

    /* A second explicit centre/bandwidth pair uses the pre-registered ID. */
    CHECK(as_effective_config_create_v0(registry, NN_EXPECTED_ID_120_12,
          (uint32_t)strlen(NN_EXPECTED_ID_120_12), AS_MODE_PROCESSING_THREAD,
          config, sizeof(config), &required, error) == AS_OK);
    create.epoch = 3u;
    create.first_input_sample = 7;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *low_session = NULL;
    CHECK(as_session_create_v0(registry, NN_EXPECTED_ID_120_12,
          (uint32_t)strlen(NN_EXPECTED_ID_120_12), &create, &low_session, error) == AS_OK);
    as_result_v0_init(&result);
    CHECK(feed_epoch(low_session, 3u, 7, samples, output, &result) == AS_OK);
    CHECK(as_session_reset_v0(low_session, 4u, 7, error) == AS_OK);
    CHECK(tone_attenuation(low_session, 120.0, 4u, 7, error) == 0);
    CHECK(as_session_close_v0(&low_session) == AS_OK);
    puts("optional notch registered with explicit f0/bw; tone attenuation, "
         "adverse controls, reset/drain/close passed");
    return 0;
}
#endif

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(query(registry, "speex.ns.v0") == AS_OK);
    CHECK(query(registry, "dsp.highpass80.v0") == AS_OK);
    CHECK(query(registry, NN_EXPECTED_ID_1000_100) == AS_UNSUPPORTED);
#ifndef AS_ENABLE_NARROW_NOTCH
    puts("optional notch unlinked and unregistered; built-ins unchanged");
#else
    CHECK(exercise(registry, &error) == 0);
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
