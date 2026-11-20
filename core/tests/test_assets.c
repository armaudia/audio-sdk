/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "test_common.h"

static const char kBytes[] = "x";
static const char kId[] = "model.f32";
static const uint8_t kDigest[32] = {
    0x2d,0x71,0x16,0x42,0xb7,0x26,0xb0,0x44,0x01,0x62,0x7c,0xa9,0xfb,0xac,0x32,0xf5,
    0xc8,0x53,0x0f,0xb1,0x90,0x3c,0xc4,0xdb,0x02,0x25,0x87,0x17,0x92,0x1a,0x48,0x81};

static as_status_v0 AS_CALL create(const as_create_config_v0 *config,
                                    void **out, as_error_v0 *error) {
    (void)error;
    if (config->asset_count != 1 || config->assets == NULL ||
        config->assets[0].data == kBytes || config->assets[0].byte_count != 1 ||
        ((const char *)config->assets[0].data)[0] != 'x') return AS_INVALID_ARGUMENT;
    *out = malloc(1);
    return *out == NULL ? AS_RESOURCE_EXHAUSTED : AS_OK;
}
static as_status_v0 AS_CALL process(void *p, const as_frame_v0 *f,
                                    const as_output_v0 *o, as_result_v0 *r) {
    (void)p; (void)f; (void)o; (void)r; return AS_UNSUPPORTED;
}
static as_status_v0 AS_CALL reset(void *p, uint64_t e, int64_t s,
                                  as_error_v0 *error) {
    (void)p; (void)e; (void)s; (void)error; return AS_OK;
}
static as_status_v0 AS_CALL drain(void *p, const as_output_v0 *o,
                                  as_result_v0 *r) {
    (void)p; (void)o; (void)r; return AS_END_OF_STREAM;
}
static void AS_CALL destroy(void *p) { free(p); }
static const as_provider_table_v0 kTable = {
    sizeof(as_provider_table_v0), AS_ABI_MAJOR, AS_ABI_MINOR,
    create, process, reset, drain, destroy, {0,0,0,0}};
static const char kDescriptor[] =
    "{\"buffering_delay_samples\":0,\"callback_safe\":false,"
    "\"configuration_schema_digest\":\"sha256:0000000000000000000000000000000000000000000000000000000000000000\","
    "\"contract_version\":\"0.1\",\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},"
    "\"execution_modes\":[2],\"implementation_id\":\"test.asset\",\"implementation_version\":\"1.0.0\","
    "\"max_drain_calls\":1,\"native_hop_samples\":160,\"platform\":{\"architectures\":[\"x86_64\"],\"cpu_requirements\":\"baseline\"},"
    "\"provider_id\":\"test.asset.v0\",\"required_assets\":[{\"byte_count\":1,\"id\":\"model.f32\","
    "\"sha256\":\"sha256:2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881\",\"storage\":\"external\"}],"
    "\"schema_id\":\"audio-sdk/descriptor/0.1\",\"source_digest\":\"sha256:1111111111111111111111111111111111111111111111111111111111111111\","
    "\"source_revision\":null,\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,\"sample_format\":\"f32\",\"sample_rate_hz\":16000}],"
    "\"upstream\":{\"license\":\"MIT\",\"name\":\"test\",\"notice_path\":\"LICENSE\"}}";

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    CHECK(as_register_provider_v0(registry, &kTable, kDescriptor,
          (uint32_t)sizeof(kDescriptor) - 1u, &error) == AS_OK);
    char config[4096]; uint32_t required = 0;
    CHECK(as_effective_config_create_v0(registry, "test.asset.v0", 13,
          AS_MODE_PROCESSING_THREAD, config, sizeof(config), &required,
          &error) == AS_OK);
    CHECK(strstr(config, "sha256:2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881") != NULL);
    as_asset_v0 asset; as_asset_v0_init(&asset);
    asset.asset_id = kId; asset.asset_id_length = sizeof(kId) - 1;
    memcpy(asset.sha256, kDigest, sizeof(kDigest));
    asset.data = kBytes; asset.byte_count = sizeof(kBytes) - 1;
    as_create_config_v0 create_config; as_create_config_v0_init(&create_config);
    create_config.execution_mode = AS_MODE_PROCESSING_THREAD;
    create_config.epoch = 1; create_config.config_json = config;
    create_config.config_json_length = required - 1; create_config.assets = &asset;
    create_config.asset_count = 1;
    CHECK(as_session_create_v0(registry, "test.asset.v0", 13, &create_config,
          &session, &error) == AS_OK);
    CHECK(as_session_close_v0(&session) == AS_OK);
    /* A declared external asset that the caller omits fails before creation. */
    as_error_v0_init(&error);
    create_config.assets = NULL;
    create_config.asset_count = 0;
    CHECK(as_session_create_v0(registry, "test.asset.v0", 13, &create_config,
          &session, &error) == AS_INVALID_ARGUMENT);
    CHECK(strcmp(error.field, "assets") == 0);
    CHECK(strstr(error.message, "asset") != NULL);
    create_config.assets = &asset;
    create_config.asset_count = 1;
    asset.asset_id = "wrong"; asset.asset_id_length = 5;
    CHECK(as_session_create_v0(registry, "test.asset.v0", 13, &create_config,
          &session, &error) == AS_INVALID_ARGUMENT);
    asset.asset_id = kId; asset.asset_id_length = sizeof(kId) - 1;
    asset.sha256[0] ^= 1;
    CHECK(as_session_create_v0(registry, "test.asset.v0", 13, &create_config,
          &session, &error) == AS_INVALID_ARGUMENT);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
