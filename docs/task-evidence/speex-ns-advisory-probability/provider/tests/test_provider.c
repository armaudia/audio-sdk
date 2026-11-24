/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "expected_vectors.h"
#include "speex_ns_advisory_analysis.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        return 1; \
    } \
} while (0)

#define PRIMARY_ID "analysis.speex-ns-advisory-reference.v0"
#define Q15_SCALE_F 32768.0f

static int32_t tri_q15(uint32_t index, uint32_t period, int32_t amplitude) {
    const uint32_t half = period / 2u;
    const uint32_t position = index % period;
    const uint32_t ramp = position <= half ? position : period - position;
    return (int32_t)((2u * ramp * (uint32_t)amplitude) / half) - amplitude;
}

static int32_t scale_q15(int32_t value, uint32_t numerator, uint32_t denominator) {
    if (value >= 0) return (int32_t)(((uint32_t)value * numerator) / denominator);
    return -(int32_t)(((uint32_t)(-value) * numerator) / denominator);
}

static int32_t noise_q15(uint32_t *state, int32_t amplitude) {
    *state = (1664525u * (*state) + 1013904223u) & 0xFFFFFFFFu;
    const uint32_t word = ((*state) >> 16) & 0xFFFFu;
    return (int32_t)((2u * (uint32_t)amplitude * word) / 65536u) - amplitude;
}

static void build_stimulus(int32_t *primary, int32_t *loud) {
    uint32_t quiet_state = 0x51504E53u;
    uint32_t loud_state = 0x4C4F5544u;
    for (uint32_t index = 0u; index < EXPECTED_STIMULUS_LENGTH; ++index) {
        const int32_t quiet = noise_q15(&quiet_state, 200);
        loud[index] = noise_q15(&loud_state, 8000);
        if (index >= 1600u && index < 3200u) {
            primary[index] = scale_q15(tri_q15(index, 160u, 1200) +
                                       tri_q15(index + 40u, 80u, 1200), 3u, 4u);
        } else if (index >= 3200u && index < 4800u) {
            primary[index] = scale_q15(tri_q15(index, 160u, 6000) +
                                       tri_q15(index + 40u, 80u, 6000), 3u, 4u);
        } else if (index >= 4800u && index < 6400u) {
            primary[index] = loud[index];
        } else {
            primary[index] = quiet;
        }
    }
}

static void hex_to_bytes(const char *hex, uint8_t *bytes, size_t count) {
    for (size_t index = 0u; index < count; ++index) {
        unsigned int value = 0u;
        sscanf(hex + index * 2u, "%2x", &value);
        bytes[index] = (uint8_t)value;
    }
}

static as_status_v0 feed(const as_provider_table_v0 *table, void *instance,
                         uint64_t epoch, int64_t first, const float *samples,
                         uint32_t valid, uint32_t flags, float *output,
                         as_result_v0 *result) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = samples;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = valid;
    frame.flags = flags;
    frame.epoch = epoch;
    frame.first_input_sample = first;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return table->process(instance, &frame, &sink, result);
}

static as_status_v0 session_feed(as_session_v0 *session, uint64_t epoch,
                                 int64_t first, const float *samples,
                                 uint32_t valid, uint32_t flags, float *output,
                                 as_result_v0 *result) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = samples;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = valid;
    frame.flags = flags;
    frame.epoch = epoch;
    frame.first_input_sample = first;
    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    return as_session_process_v0(session, &frame, &sink, result);
}

static as_status_v0 create_direct(const as_provider_table_v0 *table,
                                  void **instance) {
    static const char kConfig[] =
        "{\"provider_id\":\"analysis.speex-ns-advisory-reference.v0\"}";
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.sample_rate_hz = AS_SAMPLE_RATE_HZ;
    create.channels = AS_CHANNELS;
    create.frame_samples = AS_FRAME_SAMPLES;
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = kConfig;
    create.config_json_length = (uint32_t)(sizeof(kConfig) - 1u);
    as_error_v0 error;
    as_error_v0_init(&error);
    return table->create(&create, instance, &error);
}

static as_status_v0 create_custom(const as_provider_table_v0 *table,
                                  uint32_t rate, uint32_t channels,
                                  uint32_t frame, uint32_t mode,
                                  const char *json, uint32_t length,
                                  const as_asset_v0 *assets,
                                  uint32_t asset_count,
                                  void **instance) {
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.sample_rate_hz = rate;
    create.channels = channels;
    create.frame_samples = frame;
    create.execution_mode = mode;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = json;
    create.config_json_length = length;
    create.assets = assets;
    create.asset_count = asset_count;
    as_error_v0 error;
    as_error_v0_init(&error);
    return table->create(&create, instance, &error);
}

static int event_digest(void *instance, uint32_t hop, char *hex) {
    const uint32_t count = as_speex_ns_advisory_event_count_v0(instance, hop);
    CHECK(count == EXPECTED_EVENT_COUNT / 2u);
    uint8_t config_bytes[32u];
    hex_to_bytes(EXPECTED_CONFIG_DIGEST, config_bytes, sizeof(config_bytes));
    uint8_t all[sizeof(uint64_t) * 8u * 128u + 32u * 128u];
    size_t used = 0u;
    for (uint32_t index = 0u; index < count; ++index) {
        as_speex_ns_advisory_event_v0 event;
        CHECK(as_speex_ns_advisory_event_at_v0(instance, hop, index, &event) == AS_OK);
        const uint64_t fields[8u] = {
            event.sequence, event.hop, event.epoch,
            (uint64_t)event.source_first_sample, (uint64_t)event.source_end_sample,
            event.value_milli, event.validity, (uint64_t)event.available_monotonic_ns
        };
        memcpy(all + used, fields, sizeof(fields));
        used += sizeof(fields);
        memcpy(all + used, config_bytes, sizeof(config_bytes));
        used += sizeof(config_bytes);
    }
    return as_sha256_hex_v0(all, (uint64_t)used, hex, 65u);
}

static int parity_repeat(const as_provider_table_v0 *table,
                         const int32_t *primary, char pcm_hex[65],
                         char hop0_hex[65], char hop1_hex[65]) {
    void *instance = NULL;
    CHECK(create_direct(table, &instance) == AS_OK);
    CHECK(instance != NULL);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    float content[EXPECTED_PCM_BYTE_COUNT / sizeof(float)];
    as_result_v0 result;
    size_t count = 0u;
    for (uint32_t frame = 0u; frame < EXPECTED_FRAME_COUNT; ++frame) {
        const uint32_t start = frame * AS_FRAME_SAMPLES;
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            input[index] = (float)primary[start + index] / Q15_SCALE_F;
        }
        as_result_v0_init(&result);
        CHECK(feed(table, instance, 1u, (int64_t)start, input, AS_FRAME_SAMPLES,
                   0u, output, &result) == AS_OK);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.valid_count == AS_FRAME_SAMPLES);
        CHECK(result.source_first_sample == (int64_t)start);
        CHECK(result.epoch == 1u);
        for (uint32_t index = 0u; index < AS_FRAME_SAMPLES; ++index) {
            CHECK(isfinite((double)output[index]));
            CHECK(count < EXPECTED_PCM_BYTE_COUNT / sizeof(float));
            content[count++] = output[index];
        }
    }
    CHECK(count == EXPECTED_PCM_BYTE_COUNT / sizeof(float));
    CHECK(as_sha256_hex_v0(content, (uint64_t)EXPECTED_PCM_BYTE_COUNT,
                           pcm_hex, 65u) == AS_OK);
    CHECK(event_digest(instance, AS_SPEEX_NS_ADVISORY_HOP_INPUT, hop0_hex) == AS_OK);
    CHECK(event_digest(instance, AS_SPEEX_NS_ADVISORY_HOP_OUTPUT, hop1_hex) == AS_OK);
    CHECK(as_speex_ns_advisory_invalid_count_v0(instance) == 0u);
    table->destroy(instance);
    return 0;
}

static int parity_check(const as_provider_table_v0 *table, const int32_t *primary) {
    char pcm[3u][65u];
    char hop0[3u][65u];
    char hop1[3u][65u];
    for (uint32_t repeat = 0u; repeat < EXPECTED_REPEATS; ++repeat) {
        CHECK(parity_repeat(table, primary, pcm[repeat], hop0[repeat], hop1[repeat]) == 0);
        CHECK(strcmp(pcm[repeat], EXPECTED_PCM_DIGEST) == 0);
        CHECK(strcmp(hop0[repeat], EXPECTED_EVENT_HOP0_BINARY_DIGEST) == 0);
        CHECK(strcmp(hop1[repeat], EXPECTED_EVENT_HOP1_BINARY_DIGEST) == 0);
        if (repeat > 0u) {
            CHECK(strcmp(pcm[0], pcm[repeat]) == 0);
            CHECK(strcmp(hop0[0], hop0[repeat]) == 0);
            CHECK(strcmp(hop1[0], hop1[repeat]) == 0);
        }
    }
    puts("three byte-identical pinned Python/C parity repeats passed");
    return 0;
}

static int boundary_rejection(const as_provider_table_v0 *table) {
    static const char kConfig[] =
        "{\"provider_id\":\"analysis.speex-ns-advisory-reference.v0\"}";
    const uint32_t config_length = (uint32_t)(sizeof(kConfig) - 1u);
    void *instance = NULL;
    void *bad = NULL;
    as_asset_v0 asset;
    as_asset_v0_init(&asset);

    CHECK(create_custom(table, 48000u, AS_CHANNELS, AS_FRAME_SAMPLES,
                        AS_MODE_PROCESSING_THREAD, kConfig, config_length,
                        NULL, 0u, &bad) == AS_UNSUPPORTED);
    CHECK(bad == NULL);
    CHECK(create_custom(table, AS_SAMPLE_RATE_HZ, 2u, AS_FRAME_SAMPLES,
                        AS_MODE_PROCESSING_THREAD, kConfig, config_length,
                        NULL, 0u, &bad) == AS_UNSUPPORTED);
    CHECK(create_custom(table, AS_SAMPLE_RATE_HZ, AS_CHANNELS, 320u,
                        AS_MODE_PROCESSING_THREAD, kConfig, config_length,
                        NULL, 0u, &bad) == AS_UNSUPPORTED);
    CHECK(create_custom(table, AS_SAMPLE_RATE_HZ, AS_CHANNELS, AS_FRAME_SAMPLES,
                        AS_MODE_INLINE_CALLBACK, kConfig, config_length,
                        NULL, 0u, &bad) == AS_UNSUPPORTED);
    CHECK(create_custom(table, AS_SAMPLE_RATE_HZ, AS_CHANNELS, AS_FRAME_SAMPLES,
                        AS_MODE_PROCESSING_THREAD, "{}", 2u,
                        NULL, 0u, &bad) == AS_INVALID_ARGUMENT);
    CHECK(create_custom(table, AS_SAMPLE_RATE_HZ, AS_CHANNELS, AS_FRAME_SAMPLES,
                        AS_MODE_PROCESSING_THREAD, kConfig, config_length,
                        &asset, 1u, &bad) == AS_INVALID_ARGUMENT);

    CHECK(create_direct(table, &instance) == AS_OK);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    as_result_v0_init(&result);
    memset(input, 0, sizeof(input));
    memset(output, 0, sizeof(output));

    input[3] = NAN;
    CHECK(feed(table, instance, 1u, 0, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(as_speex_ns_advisory_invalid_count_v0(instance) == 1u);
    CHECK(as_speex_ns_advisory_event_count_v0(instance, 0u) == 0u);
    input[3] = 0.0f;
    CHECK(feed(table, instance, 1u, 0, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_OK);
    CHECK(as_speex_ns_advisory_event_count_v0(instance, 0u) == 0u);

    CHECK(feed(table, instance, 0u, 160, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(table, instance, 1u, 320, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(table, instance, 1u, 160, input, 159u, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    input[159] = 1.0f;
    CHECK(feed(table, instance, 1u, 160, input, 159u, AS_FRAME_FINAL_INPUT,
               output, &result) == AS_INVALID_ARGUMENT);
    input[159] = 0.0f;
    CHECK(feed(table, instance, 1u, 160, input, 159u, AS_FRAME_FINAL_INPUT,
               output, &result) == AS_OK);
    CHECK(result.valid_count == 159u);
    CHECK(as_speex_ns_advisory_event_count_v0(instance, 0u) == 1u);

    CHECK(table->reset(instance, 2u, 9000, NULL) == AS_OK);
    CHECK(as_speex_ns_advisory_event_count_v0(instance, 0u) == 0u);
    CHECK(feed(table, instance, 1u, 160, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_INVALID_ARGUMENT);
    CHECK(feed(table, instance, 2u, 9000, input, AS_FRAME_SAMPLES, 0u,
               output, &result) == AS_OK);
    CHECK(as_speex_ns_advisory_invalid_count_v0(instance) == 1u);

    as_output_v0 sink;
    as_output_v0_init(&sink);
    sink.samples = output;
    sink.capacity = AS_FRAME_SAMPLES;
    CHECK(table->drain(instance, &sink, &result) == AS_END_OF_STREAM);
    table->destroy(instance);
    return 0;
}

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0u, NULL);
}

static int session_exercise(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    CHECK(as_effective_config_create_v0(registry, PRIMARY_ID,
           (uint32_t)strlen(PRIMARY_ID), AS_MODE_INLINE_CALLBACK,
           config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PRIMARY_ID,
           (uint32_t)strlen(PRIMARY_ID), AS_MODE_PROCESSING_THREAD,
           config, sizeof(config), &required, error) == AS_OK);
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.sample_rate_hz = AS_SAMPLE_RATE_HZ;
    create.channels = AS_CHANNELS;
    create.frame_samples = AS_FRAME_SAMPLES;
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, PRIMARY_ID, (uint32_t)strlen(PRIMARY_ID),
                               &create, &session, error) == AS_OK);
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    as_result_v0 result;
    memset(input, 0, sizeof(input));
    as_result_v0_init(&result);
    CHECK(session_feed(session, 1u, 0, input, AS_FRAME_SAMPLES, 0u,
                       output, &result) == AS_OK);
    CHECK(result.valid_count == AS_FRAME_SAMPLES);
    CHECK(as_session_reset_v0(session, 2u, 0, error) == AS_OK);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &(as_output_v0){
              sizeof(as_output_v0), AS_ABI_MAJOR, AS_ABI_MINOR, output,
              AS_FRAME_SAMPLES, 0u}, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    return 0;
}

int main(void) {
    as_registry_v0 *registry = NULL;
    as_registry_v0 *other = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(query(registry, "speex.ns.v0") == AS_OK);
    CHECK(query(registry, "dsp.highpass80.v0") == AS_OK);
    CHECK(query(registry, PRIMARY_ID) == AS_UNSUPPORTED);

#ifdef AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY
    const as_provider_table_v0 *table = as_speex_ns_advisory_table_v0();
    CHECK(table != NULL);
    int32_t primary[EXPECTED_STIMULUS_LENGTH];
    int32_t loud[EXPECTED_STIMULUS_LENGTH];
    build_stimulus(primary, loud);
    CHECK(parity_check(table, primary) == 0);
    CHECK(boundary_rejection(table) == 0);

    CHECK(as_speex_ns_advisory_register_v0(registry, &error) == AS_OK);
    CHECK(query(registry, PRIMARY_ID) == AS_OK);
    CHECK(as_speex_ns_advisory_register_v0(registry, &error) == AS_DUPLICATE);
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, PRIMARY_ID) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(session_exercise(registry, &error) == 0);
    puts("optional advisory reference registered; boundary, reset and drain passed");
#else
    (void)session_exercise;
    puts("optional advisory reference unlinked and unregistered; built-ins unchanged");
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
