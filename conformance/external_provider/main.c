/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
#include "checks.h"
#include "audio_sdk/session_v0.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const as_provider_table_v0 *fixture_provider_table(void);

static void usage(const char *program) {
    fprintf(stderr,
            "usage: %s --provider fixture.delayed.v0|fixture.fault.v0|"
            "fixture.drainbound.v0|fixture.delay{0,1,159,160,161,256hop,512}.v0 "
            "[--report path]\n",
            program);
}

static uint32_t fixture_delay(const char *provider_id) {
    if (strcmp(provider_id, "fixture.delayed.v0") == 0 ||
        strcmp(provider_id, "fixture.fault.v0") == 0 ||
        strcmp(provider_id, "fixture.drainbound.v0") == 0 ||
        strcmp(provider_id, "fixture.delay160.v0") == 0)
        return 160u;
    if (strcmp(provider_id, "fixture.delay0.v0") == 0) return 0u;
    if (strcmp(provider_id, "fixture.delay1.v0") == 0) return 1u;
    if (strcmp(provider_id, "fixture.delay159.v0") == 0) return 159u;
    if (strcmp(provider_id, "fixture.delay161.v0") == 0) return 161u;
    if (strcmp(provider_id, "fixture.delay256hop.v0") == 0) return 256u;
    if (strcmp(provider_id, "fixture.delay512.v0") == 0) return 512u;
    return UINT32_MAX;
}

static char *make_descriptor(const char *provider_id, uint32_t *length) {
    const uint32_t delay = fixture_delay(provider_id);
    const uint32_t hop =
        strcmp(provider_id, "fixture.delay256hop.v0") == 0 ? 256u : 160u;
    const uint32_t max_drain = (delay + 159u) / 160u + 1u;
    static const char format[] =
        "\"supported_formats\":[{\"channels\":1,\"frame_samples\":160,"
        "\"sample_format\":\"f32\",\"sample_rate_hz\":16000}]";
    char *json = (char *)malloc(2048);
    if (json == NULL) return NULL;
    const int written = snprintf(
        json, 2048,
        "{\"buffering_delay_samples\":%u,\"callback_safe\":false,"
        "\"configuration_schema_digest\":\"sha256:"
        "0000000000000000000000000000000000000000000000000000000000000000\","
        "\"contract_version\":\"0.1\","
        "\"edge_exclusions\":{\"end_samples\":0,\"start_samples\":0},"
        "\"execution_modes\":[2,3],"
        "\"implementation_id\":\"fixture.delayed_identity\","
        "\"implementation_version\":\"1.0.0\",\"max_drain_calls\":%u,"
        "\"native_hop_samples\":%u,"
        "\"platform\":{\"architectures\":[\"arm64\",\"x86_64\"],"
        "\"cpu_requirements\":\"baseline\"},"
        "\"provider_id\":\"%s\",\"required_assets\":[],"
        "\"schema_id\":\"audio-sdk/descriptor/0.1\","
        "\"source_digest\":\"sha256:"
        "1111111111111111111111111111111111111111111111111111111111111111\","
        "\"source_revision\":null,%s,"
        "\"upstream\":{\"license\":\"MIT fixture\","
        "\"name\":\"audio-sdk conformance fixture\","
        "\"notice_path\":\"licenses/first-party-MIT.txt\"}}",
        delay, max_drain, hop, provider_id, format);
    if (written <= 0 || written >= 2048) {
        free(json);
        return NULL;
    }
    *length = (uint32_t)written;
    return json;
}

int main(int argc, char **argv) {
    const char *provider = NULL;
    const char *report = NULL;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--provider") == 0 && i + 1 < argc) {
            provider = argv[++i];
        } else if (strcmp(argv[i], "--report") == 0 && i + 1 < argc) {
            report = argv[++i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (provider == NULL) {
        usage(argv[0]);
        return 2;
    }
    if (fixture_delay(provider) == UINT32_MAX) {
        usage(argv[0]);
        return 2;
    }

    as_error_v0 error;
    as_error_v0_init(&error);
    as_registry_v0 *registry = NULL;
    as_status_v0 status = as_registry_create_v0(&registry, &error);
    if (status != AS_OK) {
        fprintf(stderr, "registry: %s\n", error.message);
        return 2;
    }
    uint32_t descriptor_length = 0;
    char *descriptor = make_descriptor(provider, &descriptor_length);
    if (descriptor == NULL) {
        as_registry_close_v0(&registry);
        return 2;
    }
    status = as_register_provider_v0(registry, fixture_provider_table(),
                                     descriptor, descriptor_length, &error);
    if (status != AS_OK) fprintf(stderr, "fixture descriptor: %s\n", descriptor);
    free(descriptor);
    if (status != AS_OK) {
        fprintf(stderr, "register fixture: %s (%s)\n", error.message,
                error.field);
        as_registry_close_v0(&registry);
        return 2;
    }
    char detail[256] = {0};
    const int result =
        as_run_conformance(registry, provider, (uint32_t)strlen(provider),
                           report, detail, (uint32_t)sizeof(detail));
    if (result != 0 && detail[0] != '\0') fprintf(stderr, "%s\n", detail);
    as_registry_close_v0(&registry);
    return result;
}
