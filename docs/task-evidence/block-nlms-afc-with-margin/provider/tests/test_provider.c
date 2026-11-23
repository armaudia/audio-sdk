/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Opt-in boundary test for the task-local block-NLMS AFC margin provider. */

#include "audio_sdk/session_v0.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef AS_ENABLE_AFC_MARGIN_PROVIDER
#include "afc_descriptor.h"
#include "afc_provider.h"
#endif

#define AFC_TEST_FRAMES 160u
#define AFC_TEST_SAMPLES (30u * AFC_TEST_FRAMES)
#define AFC_PROVIDER_ID "dsp.block-nlms-afc-margin.reference.v0"

static int failures = 0;

static void check(int condition, const char *message) {
    if (condition) return;
    fprintf(stderr, "afc_registration: FAIL %s\n", message);
    ++failures;
}

static int read_f32_le(const char *path, float **out, size_t *out_count) {
    FILE *file = fopen(path, "rb");
    if (file == NULL) return -1;
    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        return -1;
    }
    long size = ftell(file);
    if (size <= 0 || (size % 4) != 0 || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return -1;
    }
    size_t count = (size_t)size / 4u;
    uint8_t *bytes = (uint8_t *)malloc((size_t)size);
    float *samples = (float *)malloc(count * sizeof(float));
    if (bytes == NULL || samples == NULL ||
        fread(bytes, 1, (size_t)size, file) != (size_t)size) {
        free(bytes);
        free(samples);
        fclose(file);
        return -1;
    }
    fclose(file);
    for (size_t i = 0; i < count; ++i) {
        uint32_t bits = (uint32_t)bytes[i * 4u] |
                        ((uint32_t)bytes[i * 4u + 1u] << 8) |
                        ((uint32_t)bytes[i * 4u + 2u] << 16) |
                        ((uint32_t)bytes[i * 4u + 3u] << 24);
        memcpy(&samples[i], &bits, sizeof(bits));
    }
    free(bytes);
    *out = samples;
    *out_count = count;
    return 0;
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

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_session_v0 *second = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    float *mic = NULL;
    float *reference = NULL;
    float *collected = NULL;
    float *first_frame = NULL;
    float *second_frame = NULL;
    float *third_frame = NULL;
    size_t mic_count = 0;
    size_t reference_count = 0;

    check(as_registry_create_v0(&registry, &error) == AS_OK,
          "registry create");
    if (registry == NULL) return 1;

    const uint32_t id_length = (uint32_t)strlen(AFC_PROVIDER_ID);
    uint32_t required = 0;
    as_status_v0 query = as_query_provider_v0(registry, AFC_PROVIDER_ID,
                                              id_length, NULL, 0, &required);
#ifndef AS_ENABLE_AFC_MARGIN_PROVIDER
    check(query == AS_UNSUPPORTED,
          "unlinked provider is absent from an unmodified registry");
    const char *builtin = "speex.ns.v0";
    check(as_query_provider_v0(registry, builtin, (uint32_t)strlen(builtin),
                                NULL, 0, &required) != AS_UNSUPPORTED,
          "built-in provider remains registered");
#else
    check(afc_margin_register(registry, &error) == AS_OK,
          "opt-in provider registers explicitly");
    query = as_query_provider_v0(registry, AFC_PROVIDER_ID, id_length,
                                 NULL, 0, &required);
    check((query == AS_OK || query == AS_RESOURCE_EXHAUSTED) && required > 0u,
          "opt-in provider is registered and queryable");

    check(afc_margin_register(registry, &error) == AS_DUPLICATE,
          "duplicate provider ID is rejected");
    check(afc_margin_register_descriptor(registry, "{}", 2u, &error) != AS_OK,
          "invalid descriptor is rejected");

    check(read_f32_le(AFC_MIC_PATH, &mic, &mic_count) == 0,
          "read mic fixture");
    check(read_f32_le(AFC_REFERENCE_PATH, &reference, &reference_count) == 0,
          "read reference fixture");
    check(mic_count == AFC_TEST_SAMPLES && reference_count == AFC_TEST_SAMPLES,
          "fixture sizes match the frozen 30-frame cohort");
    if (mic == NULL || reference == NULL ||
        mic_count != AFC_TEST_SAMPLES || reference_count != AFC_TEST_SAMPLES) {
        goto cleanup;
    }

    collected = (float *)calloc(AFC_TEST_SAMPLES, sizeof(float));
    first_frame = (float *)calloc(AFC_TEST_FRAMES, sizeof(float));
    second_frame = (float *)calloc(AFC_TEST_FRAMES, sizeof(float));
    third_frame = (float *)calloc(AFC_TEST_FRAMES, sizeof(float));
    if (collected == NULL || first_frame == NULL || second_frame == NULL ||
        third_frame == NULL) {
        check(0, "scratch allocation");
        goto cleanup;
    }

    char config[2048];
    uint32_t config_required = 0;
    check(as_effective_config_create_v0(
              registry, AFC_PROVIDER_ID, id_length, AS_MODE_PROCESSING_THREAD,
              config, sizeof(config), &config_required, &error) == AS_OK,
          "effective config creation");

    as_asset_v0 asset;
    as_asset_v0_init(&asset);
    char digest_hex[65];
    uint8_t digest[32];
    check(as_sha256_hex_v0(reference,
                           (uint64_t)reference_count * 4u,
                           digest_hex, sizeof(digest_hex)) == AS_OK,
          "reference digest");
    check(hex_to_digest(digest_hex, digest) == 0, "reference digest decode");
    asset.asset_id = "afc.playback-reference.f32";
    asset.asset_id_length = (uint32_t)strlen(asset.asset_id);
    memcpy(asset.sha256, digest, sizeof(asset.sha256));
    asset.data = reference;
    asset.byte_count = (uint64_t)reference_count * 4u;

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1u;
    create.first_input_sample = 0;
    create.config_json = config;
    create.config_json_length = config_required - 1u;
    create.assets = &asset;
    create.asset_count = 1u;

    as_session_v0 *bad = NULL;
    create.asset_count = 0u;
    check(as_session_create_v0(registry, AFC_PROVIDER_ID, id_length, &create,
                               &bad, &error) != AS_OK,
          "missing reference asset is rejected");
    create.asset_count = 1u;
    const uint8_t saved_byte = asset.sha256[0];
    asset.sha256[0] ^= 1u;
    check(as_session_create_v0(registry, AFC_PROVIDER_ID, id_length, &create,
                               &bad, &error) != AS_OK,
          "wrong reference digest is rejected");
    asset.sha256[0] = saved_byte;

    create.execution_mode = AS_MODE_INLINE_CALLBACK;
    check(as_session_create_v0(registry, AFC_PROVIDER_ID, id_length, &create,
                               &bad, &error) != AS_OK,
          "unadvertised execution mode is rejected");
    create.execution_mode = AS_MODE_PROCESSING_THREAD;

    check(as_session_create_v0(registry, AFC_PROVIDER_ID, id_length, &create,
                               &session, &error) == AS_OK,
          "session create");
    if (session == NULL) goto cleanup;

    char info[2048];
    uint32_t info_required = 0;
    check(as_session_get_info_v0(session, info, sizeof(info),
                                 &info_required) == AS_OK,
          "session info");
    check(strstr(info, AFC_PROVIDER_ID) != NULL, "info names the provider");
    check(strstr(info, "\"buffering_delay_samples\":0") != NULL,
          "info reports zero buffering delay");

    float frame_input[AFC_TEST_FRAMES];
    float output[AFC_TEST_FRAMES];
    as_frame_v0 frame;
    as_output_v0 output_desc;
    as_result_v0 result;
    as_frame_v0_init(&frame);
    as_output_v0_init(&output_desc);
    as_result_v0_init(&result);
    frame.input = frame_input;
    frame.input_count = AFC_TEST_FRAMES;
    frame.input_valid_count = AFC_TEST_FRAMES;
    frame.epoch = 1u;
    output_desc.samples = output;
    output_desc.capacity = AFC_TEST_FRAMES;

    for (uint32_t offset = 0; offset < AFC_TEST_SAMPLES;
         offset += AFC_TEST_FRAMES) {
        memcpy(frame_input, mic + offset, AFC_TEST_FRAMES * sizeof(float));
        frame.first_input_sample = (int64_t)offset;

        if (offset == AFC_TEST_FRAMES) {
            const uint32_t saved_valid = frame.input_valid_count;
            frame.input_valid_count = 159u;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_INVALID_ARGUMENT,
                  "partial frame without FINAL_INPUT is rejected");
            frame.input_valid_count = saved_valid;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_OK,
                  "valid frame after wrong-shape rejection");
        } else if (offset == 2u * AFC_TEST_FRAMES) {
            frame.epoch = 0u;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_INVALID_ARGUMENT,
                  "stale epoch is rejected");
            frame.epoch = 1u;
            frame_input[0] = NAN;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_INVALID_ARGUMENT,
                  "nonfinite input is rejected");
            memcpy(frame_input, mic + offset, AFC_TEST_FRAMES * sizeof(float));
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_OK,
                  "valid frame after nonfinite rejection");
        } else if (offset == 3u * AFC_TEST_FRAMES) {
            frame.first_input_sample = (int64_t)offset + 1;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_INVALID_ARGUMENT,
                  "wrong input position is rejected");
            frame.first_input_sample = (int64_t)offset;
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_OK,
                  "valid frame after wrong-position rejection");
        } else {
            check(as_session_process_v0(session, &frame, &output_desc,
                                        &result) == AS_OK,
                  "process frame");
        }
        check(result.status == AS_OK && result.consumed_count == AFC_TEST_FRAMES &&
                  result.produced_count == AFC_TEST_FRAMES &&
                  result.valid_offset == 0u &&
                  result.valid_count == AFC_TEST_FRAMES &&
                  result.epoch == 1u &&
                  result.source_first_sample == (int64_t)offset,
              "result counts and alignment");
        memcpy(collected + offset, output, AFC_TEST_FRAMES * sizeof(float));
        if (offset == 0u) memcpy(first_frame, output, AFC_TEST_FRAMES * sizeof(float));
        if (offset == AFC_TEST_FRAMES)
            memcpy(second_frame, output, AFC_TEST_FRAMES * sizeof(float));
        if (offset == 2u * AFC_TEST_FRAMES)
            memcpy(third_frame, output, AFC_TEST_FRAMES * sizeof(float));
    }

    double peak = 0.0;
    for (size_t i = 0; i < AFC_TEST_SAMPLES; ++i) {
        check(isfinite((double)collected[i]), "finite output sample");
        const double magnitude = fabs((double)collected[i]);
        if (magnitude > peak) peak = magnitude;
    }
    check(peak < 1.0, "bounded output peak");
    check(fabs((double)collected[0] - (double)mic[0]) > 1.0e-9,
          "adaptive filter changes the microphone signal on the first frame");

    char output_hex[65];
    check(as_sha256_hex_v0(collected, (uint64_t)AFC_TEST_SAMPLES * 4u,
                           output_hex, sizeof(output_hex)) == AS_OK,
          "output digest");
    check(strcmp(output_hex, AFC_EXPECTED_OUTPUT_DIGEST) == 0,
          "output matches the pinned C-provider f32 digest");

    check(as_session_create_v0(registry, AFC_PROVIDER_ID, id_length, &create,
                               &second, &error) == AS_OK,
          "independent session create");
    if (second != NULL) {
        float second_output[AFC_TEST_FRAMES];
        as_output_v0 second_desc;
        as_frame_v0 second_frame;
        as_result_v0 second_result;
        as_output_v0_init(&second_desc);
        as_frame_v0_init(&second_frame);
        as_result_v0_init(&second_result);
        second_desc.samples = second_output;
        second_desc.capacity = AFC_TEST_FRAMES;
        second_frame.input = mic;
        second_frame.input_count = AFC_TEST_FRAMES;
        second_frame.input_valid_count = AFC_TEST_FRAMES;
        second_frame.epoch = 1u;
        second_frame.first_input_sample = 0;
        check(as_session_process_v0(second, &second_frame, &second_desc,
                                    &second_result) == AS_OK,
              "independent session process");
        check(memcmp(second_output, first_frame,
                     AFC_TEST_FRAMES * sizeof(float)) == 0,
              "independent sessions produce identical state");
    }

    check(as_session_reset_v0(session, 2u, 0, &error) == AS_OK,
          "reset with a strictly greater epoch");
    frame.epoch = 2u;
    frame.first_input_sample = 0;
    memcpy(frame_input, mic, AFC_TEST_FRAMES * sizeof(float));
    check(as_session_process_v0(session, &frame, &output_desc, &result) == AS_OK,
          "process after reset");
    check(memcmp(output, first_frame, AFC_TEST_FRAMES * sizeof(float)) == 0,
          "reset restores the initial adaptive state");

    check(as_session_begin_drain_v0(session) == AS_OK, "begin drain");
    as_result_v0 drain_result;
    as_result_v0_init(&drain_result);
    check(as_session_drain_next_v0(session, &output_desc, &drain_result) ==
              AS_END_OF_STREAM,
          "drain has no pending samples and ends immediately");
    check(drain_result.produced_count == 0u && drain_result.valid_count == 0u,
          "drain produces no content");
#endif

cleanup:
    if (session != NULL) (void)as_session_close_v0(&session);
    if (second != NULL) (void)as_session_close_v0(&second);
    if (registry != NULL) (void)as_registry_close_v0(&registry);
    free(collected);
    free(first_frame);
    free(second_frame);
    free(third_frame);
    free(mic);
    free(reference);
    if (failures != 0) {
        fprintf(stderr, "afc_registration: %d check(s) failed\n", failures);
        return 1;
    }
    printf("afc_registration: all checks passed\n");
    return 0;
}
