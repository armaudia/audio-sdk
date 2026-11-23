/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "afc_descriptor.h"
#include "block_nlms_afc_provider.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { \
        fprintf(stderr, "line %d: %s\n", __LINE__, #condition); \
        goto cleanup; \
    } \
} while (0)

#define AFC_ASSET_PREFIX 256u
#define PROVIDER "dsp.block-nlms-afc.afcref.v0"
#define PROVIDER_LEN (sizeof(PROVIDER) - 1u)

static int query(as_registry_v0 *registry, const char *id, uint32_t length) {
    return as_query_provider_v0(registry, id, length, NULL, 0, NULL);
}

static int hex_to_digest(const char *hex, uint8_t *out) {
    if (strlen(hex) != 64u) return -1;
    for (size_t i = 0; i < 32u; ++i) {
        char pair[3] = {hex[i * 2u], hex[i * 2u + 1u], '\0'};
        char *end = NULL;
        unsigned long value = strtoul(pair, &end, 16);
        if (end != pair + 2u || value > 255u) return -1;
        out[i] = (uint8_t)value;
    }
    return 0;
}

static int flip_hex(char *text, const char *prefix) {
    char *position = strstr(text, prefix);
    if (position == NULL) return -1;
    position += strlen(prefix);
    if (*position == '\0') return -1;
    *position = *position == '0' ? '1' : '0';
    return 0;
}

static int read_reference(float **out, uint32_t *bytes) {
    FILE *file = fopen(AFC_REFERENCE_PATH, "rb");
    if (file == NULL) return -1;
    if (fseek(file, 0, SEEK_END) != 0) { fclose(file); return -1; }
    long size = ftell(file);
    if (size < (long)(AFC_ASSET_PREFIX + AS_FRAME_SAMPLES) * 4 ||
        (size % 4) != 0 || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return -1;
    }
    float *samples = (float *)malloc((size_t)size);
    if (samples == NULL || fread(samples, 1, (size_t)size, file) != (size_t)size) {
        free(samples);
        fclose(file);
        return -1;
    }
    fclose(file);
    *out = samples;
    *bytes = (uint32_t)size;
    return 0;
}

static int make_session(as_registry_v0 *registry, uint64_t epoch,
                        int64_t first, const char *config, uint32_t config_len,
                        const float *reference, uint32_t reference_bytes,
                        int omit_asset, int tamper_digest, int wrong_id,
                        int wrong_size, as_session_v0 **session,
                        as_error_v0 *error) {
    uint8_t digest[32];
    char hex[65];
    if (as_sha256_hex_v0(reference, reference_bytes, hex, sizeof(hex)) != AS_OK ||
        hex_to_digest(hex, digest) != 0) {
        return -1;
    }
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = epoch;
    create.first_input_sample = first;
    create.config_json = config;
    create.config_json_length = config_len;

    as_asset_v0 asset;
    as_asset_v0_init(&asset);
    asset.asset_id = "afc.playback-reference.f32";
    asset.asset_id_length = (uint32_t)strlen(asset.asset_id);
    memcpy(asset.sha256, digest, sizeof(asset.sha256));
    asset.data = reference;
    asset.byte_count = reference_bytes;
    if (tamper_digest) asset.sha256[0] ^= 0xffu;
    if (wrong_id) {
        asset.asset_id = "afc.wrong-id.f32";
        asset.asset_id_length = (uint32_t)strlen(asset.asset_id);
    }
    if (wrong_size) asset.byte_count -= 4u;
    if (!omit_asset) {
        create.assets = &asset;
        create.asset_count = 1u;
    }
    return as_session_create_v0(registry, PROVIDER, PROVIDER_LEN, &create,
                                session, error) == AS_OK ? 0 : -1;
}

#ifdef AS_ENABLE_BLOCK_NLMS_AFC
static void echo_frames(const float *reference, int playback_frame,
                        float *input) {
    /* Fixed return path: mic = 0.7*x[n] - 0.35*x[n-1] + 0.18*x[n-2], where
     * playback is delayed by one frame relative to the microphone timeline. */
    static const double path[3] = {0.7, -0.35, 0.18};
    const int64_t base = (int64_t)AFC_ASSET_PREFIX +
                         (int64_t)playback_frame * AS_FRAME_SAMPLES;
    for (uint32_t n = 0; n < AS_FRAME_SAMPLES; ++n) {
        double value = 0.0;
        for (uint32_t k = 0; k < 3u; ++k) {
            const int64_t position = base + (int64_t)n - (int64_t)k;
            if (position >= 0) {
                value += path[k] * (double)reference[position];
            }
        }
        input[n] = (float)value;
    }
}

static double frame_power(const float *samples) {
    double sum = 0.0;
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        sum += (double)samples[i] * (double)samples[i];
    }
    return sum / (double)AS_FRAME_SAMPLES;
}

static int exercise_afc(as_registry_v0 *registry, as_error_v0 *error) {
    float *reference = NULL;
    uint32_t reference_bytes = 0;
    float input[AS_FRAME_SAMPLES];
    float zero[AS_FRAME_SAMPLES];
    float first_output[AS_FRAME_SAMPLES];
    float second_output[AS_FRAME_SAMPLES];
    float repeat_output[AS_FRAME_SAMPLES];
    float samples[AS_FRAME_SAMPLES];
    char config[2048];
    char modified[4096];
    char descriptor[sizeof(kAfcDescriptor) + 1u];
    uint32_t required = 0;
    as_session_v0 *session = NULL;
    as_session_v0 *other = NULL;
    as_registry_v0 *isolated = NULL;
    int code = 1;

    CHECK(read_reference(&reference, &reference_bytes) == 0);

    memcpy(descriptor, kAfcDescriptor, sizeof(kAfcDescriptor));
    char *asset = strstr(descriptor, "\"required_assets\":[{\"byte_count\":");
    CHECK(asset != NULL);
    CHECK(strstr(descriptor, "afc.playback-reference.f32") != NULL);
    CHECK(strstr(descriptor, "\"storage\":\"external\"") != NULL);

    CHECK(as_effective_config_create_v0(registry, PROVIDER, PROVIDER_LEN,
          AS_MODE_INLINE_CALLBACK, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER, PROVIDER_LEN,
          AS_MODE_BUFFERED_WORKER, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, PROVIDER, PROVIDER_LEN,
          AS_MODE_PROCESSING_THREAD, config, sizeof(config), &required, error) == AS_OK);
    CHECK(required == strlen(config) + 1u);
    CHECK(strstr(config, PROVIDER) != NULL);

    const char *settings = "\"settings\":{}";
    char *position = strstr(config, settings);
    CHECK(position != NULL);
    const size_t prefix_length = (size_t)(position - config);
    (void)snprintf(modified, sizeof(modified), "%.*s%s%s",
                   (int)prefix_length, config, "\"settings\":{\"step_size\":1}",
                   position + strlen(settings));
    CHECK(make_session(registry, 1, 0, modified, (uint32_t)strlen(modified),
                       reference, reference_bytes, 0, 0, 0, 0,
                       &session, error) != 0);
    CHECK(error->status == AS_UNSUPPORTED);
    CHECK(strcmp(error->field, "processors.settings") == 0);

    char wrong_digest[sizeof(config)];
    memcpy(wrong_digest, config, required);
    CHECK(flip_hex(wrong_digest, "\"descriptor_digest\":\"sha256:") == 0);
    CHECK(make_session(registry, 1, 0, wrong_digest, required - 1u,
                       reference, reference_bytes, 0, 0, 0, 0,
                       &session, error) != 0);
    CHECK(strcmp(error->field, "descriptor_digest") == 0);

    CHECK(make_session(registry, 1, 0, config, required - 1u, reference,
                       reference_bytes, 1, 0, 0, 0, &session, error) != 0);
    CHECK(strcmp(error->field, "assets") == 0);
    CHECK(make_session(registry, 1, 0, config, required - 1u, reference,
                       reference_bytes, 0, 1, 0, 0, &session, error) != 0);
    CHECK(strcmp(error->field, "assets.sha256") == 0);
    CHECK(make_session(registry, 1, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 1, 0, &session, error) != 0);
    CHECK(strcmp(error->field, "assets") == 0);
    CHECK(make_session(registry, 1, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 0, 1, &session, error) != 0);
    CHECK(strcmp(error->field, "assets") == 0);

    CHECK(make_session(registry, 7, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 0, 0, &session, error) == 0);
    as_frame_v0 frame;
    as_output_v0 output;
    as_result_v0 result;
    as_frame_v0_init(&frame);
    as_output_v0_init(&output);
    as_result_v0_init(&result);
    memset(zero, 0, sizeof(zero));
    frame.input = input;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    frame.epoch = 7;
    frame.first_input_sample = 0;
    output.samples = samples;
    output.capacity = AS_FRAME_SAMPLES;

    echo_frames(reference, -1, input);
    input[17] = NAN;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    echo_frames(reference, -1, input);
    frame.input_count = 159;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = 0;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.input_valid_count = AS_FRAME_SAMPLES;
    output.capacity = 159;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    output.capacity = AS_FRAME_SAMPLES;
    frame.epoch = 8;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.epoch = 7;
    frame.first_input_sample = 160;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.first_input_sample = 0;

    /* One silent prefix frame then twelve echo frames; residual must fall. */
    double first_power = 0.0;
    double last_power = 0.0;
    double last_mic_power = 0.0;
    for (int index = 0; index <= 12; ++index) {
        echo_frames(reference, index - 1, input);
        frame.first_input_sample = (int64_t)index * AS_FRAME_SAMPLES;
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        CHECK(result.consumed_count == AS_FRAME_SAMPLES);
        CHECK(result.produced_count == AS_FRAME_SAMPLES);
        CHECK(result.source_first_sample == frame.first_input_sample);
        if (index == 1) first_power = frame_power(samples);
        if (index == 12) {
            last_power = frame_power(samples);
            last_mic_power = frame_power(input);
        }
    }
    CHECK(first_power > 0.0 && last_power < last_mic_power);

    /* Final partial frame: 37 valid samples, then EOS without backend fault. */
    echo_frames(reference, 12, input);
    memset(input + 37, 0, (AS_FRAME_SAMPLES - 37u) * sizeof(float));
    frame.input_valid_count = 37;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.first_input_sample = 13 * (int64_t)AS_FRAME_SAMPLES;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(result.valid_count == 37);
    CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &output, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    frame.flags = 0;
    frame.input_valid_count = AS_FRAME_SAMPLES;

    /* Reset makes the same two frames byte-identical at a fresh epoch. */
    CHECK(make_session(registry, 11, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 0, 0, &session, error) == 0);
    frame.epoch = 11;
    frame.first_input_sample = 0;
    for (int index = 0; index < 2; ++index) {
        echo_frames(reference, index - 1, input);
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        if (index == 1) memcpy(first_output, samples, sizeof(first_output));
        frame.first_input_sample += AS_FRAME_SAMPLES;
    }
    CHECK(as_session_reset_v0(session, 12, 0, error) == AS_OK);
    frame.epoch = 12;
    frame.first_input_sample = 0;
    for (int index = 0; index < 2; ++index) {
        echo_frames(reference, index - 1, input);
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        if (index == 1) memcpy(second_output, samples, sizeof(second_output));
        frame.first_input_sample += AS_FRAME_SAMPLES;
    }
    CHECK(memcmp(first_output, second_output, sizeof(first_output)) == 0);
    CHECK(as_session_close_v0(&session) == AS_OK);

    /* Two live sessions keep independent adaptive state. */
    CHECK(make_session(registry, 20, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 0, 0, &session, error) == 0);
    CHECK(make_session(registry, 30, 0, config, required - 1u, reference,
                       reference_bytes, 0, 0, 0, 0, &other, error) == 0);
    for (int pass = 0; pass < 2; ++pass) {
        const int64_t base = (int64_t)pass * AS_FRAME_SAMPLES;
        CHECK(as_session_reset_v0(session, 21u + (uint64_t)pass, base, error) == AS_OK);
        CHECK(as_session_reset_v0(other, 31u + (uint64_t)pass, base, error) == AS_OK);
        echo_frames(reference, pass - 1, input);
        frame.first_input_sample = base;
        frame.epoch = 21u + (uint32_t)pass;
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        memcpy(first_output, samples, sizeof(first_output));
        frame.epoch = 31u + (uint32_t)pass;
        CHECK(as_session_process_v0(other, &frame, &output, &result) == AS_OK);
        memcpy(repeat_output, samples, sizeof(repeat_output));
        CHECK(memcmp(first_output, repeat_output, sizeof(first_output)) == 0);
    }
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_session_close_v0(&other) == AS_OK);

    CHECK(as_registry_create_v0(&isolated, error) == AS_OK);
    CHECK(query(isolated, PROVIDER, PROVIDER_LEN) == AS_UNSUPPORTED);
    puts("afc provider: asset gates, controls, adaptation, reset and isolation passed");
    code = 0;

cleanup:
    if (session != NULL) (void)as_session_close_v0(&session);
    if (other != NULL) (void)as_session_close_v0(&other);
    if (isolated != NULL) (void)as_registry_close_v0(&isolated);
    free(reference);
    return code;
}
#endif

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) return 1;
    if (query(registry, "speex.ns.v0", sizeof("speex.ns.v0") - 1u) != AS_OK ||
        query(registry, "dsp.highpass80.v0",
              sizeof("dsp.highpass80.v0") - 1u) != AS_OK) {
        return 1;
    }
#ifndef AS_ENABLE_BLOCK_NLMS_AFC
    if (query(registry, PROVIDER, PROVIDER_LEN) != AS_UNSUPPORTED) {
        fprintf(stderr, "unlinked provider must not be registered\n");
        return 1;
    }
    puts("built-ins present; unlinked Block-NLMS AFC provider absent");
#else
    if (query(registry, PROVIDER, PROVIDER_LEN) != AS_UNSUPPORTED) return 1;
    if (afc_provider_register(registry, &error) != AS_OK) return 1;
    if (query(registry, PROVIDER, PROVIDER_LEN) != AS_OK) return 1;
    if (afc_provider_register(registry, &error) != AS_DUPLICATE) return 1;
    if (exercise_afc(registry, &error) != 0) return 1;
#endif
    return as_registry_close_v0(&registry) == AS_OK ? 0 : 1;
}
