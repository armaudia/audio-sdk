/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"
#include "css_descriptor.h"
#include "css_provider.h"

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

static int query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

static int hex_to_digest(const char *hex, uint8_t *out) {
    if (strlen(hex) != 64) return -1;
    for (size_t i = 0; i < 32; ++i) {
        char pair[3] = {hex[i * 2u], hex[i * 2u + 1u], '\0'};
        char *end = NULL;
        unsigned long value = strtoul(pair, &end, 16);
        if (end != pair + 2 || value > 255u) return -1;
        out[i] = (uint8_t)value;
    }
    return 0;
}

static int read_profile(float **out, size_t *count) {
    FILE *file = fopen(CSS_PROFILE_PATH, "rb");
    if (file == NULL) return -1;
    if (fseek(file, 0, SEEK_END) != 0) return -1;
    long size = ftell(file);
    if (size != 16384 || fseek(file, 0, SEEK_SET) != 0) {
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
    *count = (size_t)size / 4u;
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

static int make_session(as_registry_v0 *registry, uint64_t epoch,
                        int64_t first, const char *config, uint32_t config_len,
                        const void *profile, uint32_t profile_bytes,
                        int omit_asset, int tamper_digest,
                        as_session_v0 **session, as_error_v0 *error) {
    uint8_t digest[32];
    char hex[65];
    if (as_sha256_hex_v0(profile, profile_bytes, hex, sizeof(hex)) != AS_OK ||
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
    asset.asset_id = "css.noise-profile.f32";
    asset.asset_id_length = (uint32_t)strlen(asset.asset_id);
    memcpy(asset.sha256, digest, sizeof(asset.sha256));
    asset.data = profile;
    asset.byte_count = profile_bytes;
    if (tamper_digest) asset.sha256[0] ^= 0xffu;
    if (!omit_asset) {
        create.assets = &asset;
        create.asset_count = 1;
    }
    return as_session_create_v0(registry, "css.reference.v0", 16u, &create,
                                session, error) == AS_OK ? 0 : -1;
}

#ifdef AS_ENABLE_CSS_PROVIDER
static int exercise_css(as_registry_v0 *registry, as_error_v0 *error) {
    float *profile = NULL;
    float *nonfinite_profile = NULL;
    size_t profile_count = 0;
    float input[AS_FRAME_SAMPLES];
    float zero[AS_FRAME_SAMPLES];
    float first_output[AS_FRAME_SAMPLES];
    float second_output[AS_FRAME_SAMPLES];
    float repeat_output[AS_FRAME_SAMPLES];
    float samples[AS_FRAME_SAMPLES];
    char config[2048];
    char modified[4096];
    char descriptor[sizeof(kCssDescriptor) + 1u];
    uint32_t required = 0;
    as_session_v0 *session = NULL;
    as_session_v0 *other = NULL;
    as_registry_v0 *isolated = NULL;
    int code = 1;

    CHECK(read_profile(&profile, &profile_count) == 0);
    nonfinite_profile = (float *)malloc(profile_count * sizeof(float));
    CHECK(nonfinite_profile != NULL);
    memcpy(nonfinite_profile, profile, profile_count * sizeof(float));
    uint32_t nan_bits = 0x7fc00000u;
    memcpy(nonfinite_profile, &nan_bits, sizeof(nan_bits));

    memcpy(descriptor, kCssDescriptor, sizeof(kCssDescriptor));
    char *schema = strstr(descriptor, "\"schema_id\":\"audio-sdk/descriptor/0.1\"");
    CHECK(schema != NULL);
    schema[strlen("\"schema_id\":\"audio-sdk/descriptor/0.1\"") - 2u] = '2';
    CHECK(css_register_descriptor(registry, descriptor, (uint32_t)strlen(descriptor),
                                  error) == AS_INVALID_ARGUMENT);

    CHECK(as_effective_config_create_v0(registry, "css.reference.v0", 16u,
          AS_MODE_INLINE_CALLBACK, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, "css.reference.v0", 16u,
          AS_MODE_BUFFERED_WORKER, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, "css.reference.v0", 16u,
          AS_MODE_PROCESSING_THREAD, config, sizeof(config), &required, error) == AS_OK);

    const char *settings = "\"settings\":{}";
    char *position = strstr(config, settings);
    CHECK(position != NULL);
    const size_t prefix_length = (size_t)(position - config);
    (void)snprintf(modified, sizeof(modified), "%.*s%s%s",
                   (int)prefix_length, config, "\"settings\":{\"alpha\":2}",
                   position + strlen(settings));
    CHECK(make_session(registry, 1, 0, modified, (uint32_t)strlen(modified),
                       profile, (uint32_t)profile_count * 4u, 0, 0,
                       &session, error) != 0);
    CHECK(error->status == AS_UNSUPPORTED);
    CHECK(strcmp(error->field, "processors.settings") == 0);

    char wrong_digest[sizeof(config)];
    memcpy(wrong_digest, config, required);
    CHECK(flip_hex(wrong_digest, "\"descriptor_digest\":\"sha256:") == 0);
    CHECK(make_session(registry, 1, 0, wrong_digest, required - 1u,
                       profile, (uint32_t)profile_count * 4u, 0, 0,
                       &session, error) != 0);
    CHECK(error->status == AS_INVALID_ARGUMENT);
    CHECK(strcmp(error->field, "descriptor_digest") == 0);

    CHECK(make_session(registry, 1, 0, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 1, 0, &session, error) != 0);
    CHECK(strcmp(error->field, "assets") == 0);
    CHECK(make_session(registry, 1, 0, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 0, 1, &session, error) != 0);
    CHECK(strcmp(error->field, "assets.sha256") == 0);
    /* Altering profile bytes changes their digest, so the SDK's asset gate
     * rejects the nonfinite payload before the provider is entered. */
    CHECK(make_session(registry, 1, 0, config, required - 1u, nonfinite_profile,
                       (uint32_t)profile_count * 4u, 0, 0, &session, error) != 0);
    CHECK(strcmp(error->field, "assets.sha256") == 0);

    CHECK(make_session(registry, 7, 100, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 0, 0, &session, error) == 0);
    as_frame_v0 frame;
    as_output_v0 output;
    as_result_v0 result;
    as_frame_v0_init(&frame);
    as_output_v0_init(&output);
    as_result_v0_init(&result);
    memset(zero, 0, sizeof(zero));
    memset(input, 0, sizeof(input));
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        input[i] = (float)(0.25 * sin(2.0 * 3.141592653589793 * 200.0 *
                                      (double)i / 16000.0));
    }
    frame.input = input;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    frame.epoch = 7;
    frame.first_input_sample = 100;
    output.samples = samples;
    output.capacity = AS_FRAME_SAMPLES;

    input[0] = NAN;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    input[0] = 0.25f;
    frame.input_count = 159;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = 37;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.input_valid_count = AS_FRAME_SAMPLES;
    output.capacity = 159;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    output.capacity = AS_FRAME_SAMPLES;
    frame.epoch = 8;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.epoch = 7;

    frame.input = zero;
    frame.first_input_sample = 100;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(result.source_first_sample == -60 && result.produced_count == AS_FRAME_SAMPLES);
    CHECK(result.valid_count == 0);
    frame.first_input_sample = 260;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(result.source_first_sample == 100 && result.valid_count == AS_FRAME_SAMPLES);
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        CHECK(isfinite((double)output.samples[i]) && output.samples[i] == 0.0f);
    }
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(session == NULL);

    /* Reset must clear WOLA, gain and hop state: the same two frames must
     * produce byte-identical samples at a fresh epoch and coordinate. */
    CHECK(make_session(registry, 11, 0, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 0, 0, &session, error) == 0);
    frame.input = input;
    frame.epoch = 11;
    frame.first_input_sample = 0;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    frame.first_input_sample = 160;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    memcpy(first_output, output.samples, sizeof(first_output));
    CHECK(as_session_reset_v0(session, 12, 0, error) == AS_OK);
    frame.epoch = 12;
    frame.first_input_sample = 0;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    frame.first_input_sample = 160;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    memcpy(second_output, output.samples, sizeof(second_output));
    CHECK(memcmp(first_output, second_output, sizeof(first_output)) == 0);
    frame.epoch = 11;
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_INVALID_ARGUMENT);
    frame.epoch = 12;

    /* Final partial frame: accepted content ends at sample 357. */
    memset(input + 37, 0, (AS_FRAME_SAMPLES - 37u) * sizeof(float));
    frame.input_valid_count = 37;
    frame.flags = AS_FRAME_FINAL_INPUT;
    frame.first_input_sample = 320;
    as_status_v0 partial_status = as_session_process_v0(session, &frame, &output, &result);
    CHECK(partial_status == AS_OK);
    /* The delayed output for this call is the previous full frame; the
     * partial frame's own 37 valid samples are emitted by drain. */
    CHECK(result.source_first_sample == 160 && result.valid_count == AS_FRAME_SAMPLES);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &output, &result) == AS_OK);
    CHECK(result.source_first_sample == 320 && result.produced_count == AS_FRAME_SAMPLES);
    CHECK(result.valid_offset == 0 && result.valid_count == 37);
    CHECK((result.flags & AS_RESULT_FINAL_PADDING) != 0);
    CHECK(as_session_drain_next_v0(session, &output, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    frame.flags = 0;

    /* Two live sessions keep independent state. */
    CHECK(make_session(registry, 20, 0, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 0, 0, &session, error) == 0);
    CHECK(make_session(registry, 30, 0, config, required - 1u, profile,
                       (uint32_t)profile_count * 4u, 0, 0, &other, error) == 0);
    frame.input = input;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    for (int pass = 0; pass < 2; ++pass) {
        const int64_t base = (int64_t)pass * 320;
        const uint64_t epoch_a = 21u + (uint64_t)pass;
        const uint64_t epoch_b = 31u + (uint64_t)pass;
        CHECK(as_session_reset_v0(session, epoch_a, base, error) == AS_OK);
        CHECK(as_session_reset_v0(other, epoch_b, base, error) == AS_OK);
        frame.first_input_sample = base;
        frame.epoch = epoch_a;
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        memcpy(first_output, output.samples, sizeof(first_output));
        frame.epoch = epoch_b;
        CHECK(as_session_process_v0(other, &frame, &output, &result) == AS_OK);
        memcpy(second_output, output.samples, sizeof(second_output));
        CHECK(memcmp(first_output, second_output, sizeof(first_output)) == 0);

        frame.first_input_sample = base + 160;
        frame.epoch = epoch_a;
        CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
        memcpy(first_output, output.samples, sizeof(first_output));
        frame.epoch = epoch_b;
        if (pass == 0) {
            for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
                input[i] = -input[i];
            }
        }
        CHECK(as_session_process_v0(other, &frame, &output, &result) == AS_OK);
        memcpy(repeat_output, output.samples, sizeof(repeat_output));
        if (pass == 0) {
            CHECK(memcmp(first_output, repeat_output, sizeof(first_output)) != 0);
            for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
                input[i] = -input[i];
            }
        }
    }
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_session_close_v0(&other) == AS_OK);

    CHECK(as_registry_create_v0(&isolated, error) == AS_OK);
    CHECK(query(isolated, "css.reference.v0") == AS_UNSUPPORTED);
    puts("css provider: controls, reset, partial tail and session isolation passed");
    code = 0;

cleanup:
    if (session != NULL) (void)as_session_close_v0(&session);
    if (other != NULL) (void)as_session_close_v0(&other);
    if (isolated != NULL) (void)as_registry_close_v0(&isolated);
    free(nonfinite_profile);
    free(profile);
    return code;
}
#endif

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) return 1;
    if (query(registry, "speex.ns.v0") != AS_OK ||
        query(registry, "dsp.highpass80.v0") != AS_OK) {
        return 1;
    }
#ifndef AS_ENABLE_CSS_PROVIDER
    if (query(registry, "css.reference.v0") != AS_UNSUPPORTED) {
        fprintf(stderr, "unlinked provider must not be registered\n");
        return 1;
    }
    puts("built-ins present; unlinked CSS provider absent");
#else
    if (query(registry, "css.reference.v0") != AS_UNSUPPORTED) return 1;
    if (css_register(registry, &error) != AS_OK) return 1;
    if (query(registry, "css.reference.v0") != AS_OK) return 1;
    if (css_register(registry, &error) != AS_DUPLICATE) return 1;
    if (exercise_css(registry, &error) != 0) return 1;
#endif
    return as_registry_close_v0(&registry) == AS_OK ? 0 : 1;
}
