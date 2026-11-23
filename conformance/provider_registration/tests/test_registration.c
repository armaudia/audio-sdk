/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "audio_sdk/session_v0.h"

#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { \
    if (!(condition)) { fprintf(stderr, "line %d: %s\n", __LINE__, #condition); return 1; } \
} while (0)

static const char kId[] = "fixture.caller-asset.v0";

static as_status_v0 query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0, NULL);
}

#ifdef AS_ENABLE_FIXTURE_PROVIDER
as_status_v0 fixture_register(as_registry_v0 *registry, as_error_v0 *error);

static int exercise_fixture(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0;
    CHECK(as_effective_config_create_v0(registry, kId, sizeof(kId) - 1u,
          AS_MODE_INLINE_CALLBACK, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, kId, sizeof(kId) - 1u,
          AS_MODE_BUFFERED_WORKER, config, sizeof(config), &required, error) == AS_UNSUPPORTED);
    CHECK(as_effective_config_create_v0(registry, kId, sizeof(kId) - 1u,
          AS_MODE_PROCESSING_THREAD, config, sizeof(config), &required, error) == AS_OK);

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1;
    create.first_input_sample = 42;
    create.config_json = config;
    create.config_json_length = required - 1u;

    as_session_v0 *session = NULL;
    CHECK(as_session_create_v0(registry, kId, sizeof(kId) - 1u,
          &create, &session, error) == AS_INVALID_ARGUMENT);
    CHECK(session == NULL && strcmp(error->field, "assets") == 0);

    static const uint8_t digest[] = {
        0x2d,0x71,0x16,0x42,0xb7,0x26,0xb0,0x44,0x01,0x62,0x7c,0xa9,0xfb,0xac,0x32,0xf5,
        0xc8,0x53,0x0f,0xb1,0x90,0x3c,0xc4,0xdb,0x02,0x25,0x87,0x17,0x92,0x1a,0x48,0x81};
    uint8_t marker = 0;
    as_asset_v0 asset;
    as_asset_v0_init(&asset);
    asset.asset_id = "fixture.marker";
    asset.asset_id_length = sizeof("fixture.marker") - 1u;
    memcpy(asset.sha256, digest, sizeof(digest));
    asset.data = &marker;
    asset.byte_count = sizeof(marker);
    create.assets = &asset;
    create.asset_count = 1;
    CHECK(as_session_create_v0(registry, kId, sizeof(kId) - 1u,
          &create, &session, error) == AS_INVALID_ARGUMENT);
    CHECK(session == NULL && strcmp(error->field, "assets.sha256") == 0);

    marker = 'x';
    CHECK(as_session_create_v0(registry, kId, sizeof(kId) - 1u,
          &create, &session, error) == AS_OK);
    marker = 0; /* Processing must read the session's copy, not the caller's buffer. */

    const float input[AS_FRAME_SAMPLES] = {1.0f, -1.0f};
    float samples[AS_FRAME_SAMPLES];
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = create.epoch;
    frame.first_input_sample = create.first_input_sample;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = samples;
    as_result_v0 result;
    as_result_v0_init(&result);
    CHECK(as_session_process_v0(session, &frame, &output, &result) == AS_OK);
    CHECK(result.valid_offset == 0 && result.valid_count == AS_FRAME_SAMPLES &&
          result.source_first_sample == 42 && result.epoch == 1);
    CHECK(samples[0] == 0.5f && samples[1] == -0.5f);
    CHECK(as_session_begin_drain_v0(session) == AS_OK);
    CHECK(as_session_drain_next_v0(session, &output, &result) == AS_END_OF_STREAM);
    CHECK(as_session_close_v0(&session) == AS_OK);
    puts("fixture processed with a verified caller byte; unadvertised modes, missing byte and tampered byte rejected");
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
    CHECK(query(registry, kId) == AS_UNSUPPORTED);
#ifdef AS_ENABLE_FIXTURE_PROVIDER
    CHECK(fixture_register(registry, &error) == AS_OK);
    CHECK(query(registry, kId) == AS_OK);
    CHECK(fixture_register(registry, &error) == AS_DUPLICATE);

    as_registry_v0 *other = NULL;
    CHECK(as_registry_create_v0(&other, &error) == AS_OK);
    CHECK(query(other, kId) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&other) == AS_OK);
    CHECK(exercise_fixture(registry, &error) == 0);
#else
    puts("both built-ins are available; the unlinked fixture is not registered");
#endif
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
