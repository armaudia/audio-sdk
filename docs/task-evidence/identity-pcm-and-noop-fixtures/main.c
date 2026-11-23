/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Installed-prefix consumer for the identity PCM/noop baseline.
 *
 * Every PCM array is allocated and owned by this caller. The task-local
 * provider is registered explicitly on a private registry; no SDK default,
 * descriptor, registry or public header is changed.
 */
#include "checks.h"
#include "audio_sdk/session_v0.h"
#include "fixture_descriptor.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const as_provider_table_v0 *identity_provider_table(void);

#define BASE_COMMIT "3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41"
#define PROVIDER_ID "fixture.identity-pcm.v0"
#define UNREGISTERED_ID "fixture.not-registered.v0"
#define FIRST_SAMPLE INT64_C(9007199254740993)
#define EPOCH UINT64_C(7)
#define FRAME_COUNT 3u
#define FINAL_VALID 37u

typedef struct case_record {
    const char *id;
    int ok;
    char detail[192];
} case_record;

static case_record g_cases[8];
static size_t g_case_count = 0u;
static const char *g_archive_sha256 = "";

static void record_case(const char *id, int ok, const char *detail) {
    if (g_case_count >= sizeof(g_cases) / sizeof(g_cases[0])) {
        fprintf(stderr, "case record overflow\n");
        exit(2);
    }
    case_record *entry = &g_cases[g_case_count++];
    entry->id = id;
    entry->ok = ok;
    snprintf(entry->detail, sizeof(entry->detail), "%s", detail);
    printf("%-28s %-4s %s\n", id, ok ? "pass" : "FAIL", detail);
}

static float fixture_sample(uint32_t frame_index, uint32_t position) {
    const uint32_t raw = (position * 37u + frame_index * 17u) % 101u;
    return (float)(((int)raw - 50) / 128.0);
}

static void fill_frame(float *values, uint32_t frame_index, uint32_t valid) {
    for (uint32_t i = 0u; i < AS_FRAME_SAMPLES; ++i)
        values[i] = i < valid ? fixture_sample(frame_index, i) : 0.0f;
}

static int query(as_registry_v0 *registry, const char *id) {
    return as_query_provider_v0(registry, id, (uint32_t)strlen(id), NULL, 0u, NULL);
}

static as_status_v0 effective(as_registry_v0 *registry, const char *id,
                              uint32_t mode, char *buffer, uint32_t capacity,
                              uint32_t *required, as_error_v0 *error) {
    return as_effective_config_create_v0(registry, id, (uint32_t)strlen(id),
                                         mode, buffer, capacity, required, error);
}

static as_status_v0 create_session(as_registry_v0 *registry, const char *id,
                                   as_session_v0 **out, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    as_status_v0 status = effective(registry, id, AS_MODE_PROCESSING_THREAD,
                                    config, (uint32_t)sizeof(config), &required,
                                    error);
    if (status != AS_OK) return status;
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = EPOCH;
    create.first_input_sample = FIRST_SAMPLE;
    create.config_json = config;
    create.config_json_length = required - 1u;
    return as_session_create_v0(registry, id, (uint32_t)strlen(id), &create,
                                out, error);
}

static int test_registration(as_registry_v0 *registry, as_error_v0 *error) {
    as_registry_v0 *other = NULL;
    int ok = query(registry, "speex.ns.v0") == AS_OK
        && query(registry, "dsp.highpass80.v0") == AS_OK
        && query(registry, PROVIDER_ID) == AS_OK
        && as_register_provider_v0(registry, identity_provider_table(),
                                   kDescriptor, (uint32_t)(sizeof(kDescriptor) - 1u),
                                   error) == AS_DUPLICATE
        && as_registry_create_v0(&other, error) == AS_OK
        && query(other, PROVIDER_ID) == AS_UNSUPPORTED
        && as_registry_close_v0(&other) == AS_OK;
    record_case("provider_registration", ok, "builtins present; fixture explicit and registry-local");
    return ok;
}

static int test_caller_owned(as_registry_v0 *registry, as_error_v0 *error) {
    as_session_v0 *session = NULL;
    if (create_session(registry, PROVIDER_ID, &session, error) != AS_OK) {
        record_case("caller_owned_exact_pcm", 0, "session create failed");
        return 0;
    }
    float input[AS_FRAME_SAMPLES];
    float expected[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    int ok = 1;
    for (uint32_t frame = 0u; frame < FRAME_COUNT && ok; ++frame) {
        const uint32_t valid = frame + 1u < FRAME_COUNT
            ? AS_FRAME_SAMPLES : FINAL_VALID;
        fill_frame(input, frame, valid);
        fill_frame(expected, frame, valid);
        as_frame_v0 req;
        as_output_v0 out;
        as_result_v0 result;
        as_frame_v0_init(&req);
        as_output_v0_init(&out);
        as_result_v0_init(&result);
        req.input = input;
        req.input_count = AS_FRAME_SAMPLES;
        req.input_valid_count = valid;
        req.epoch = EPOCH;
        req.first_input_sample = FIRST_SAMPLE + (int64_t)frame * AS_FRAME_SAMPLES;
        if (frame + 1u == FRAME_COUNT) req.flags = AS_FRAME_FINAL_INPUT;
        out.samples = output;
        out.capacity = AS_FRAME_SAMPLES;
        ok = as_session_process_v0(session, &req, &out, &result) == AS_OK
            && memcmp(output, expected, sizeof(output)) == 0
            && result.consumed_count == AS_FRAME_SAMPLES
            && result.produced_count == AS_FRAME_SAMPLES
            && result.valid_offset == 0u
            && result.valid_count == valid
            && result.epoch == EPOCH
            && result.source_first_sample == req.first_input_sample;
    }
    if (ok && as_session_begin_drain_v0(session) != AS_OK) ok = 0;
    if (ok) {
        as_output_v0 out;
        as_result_v0 result;
        as_output_v0_init(&out);
        as_result_v0_init(&result);
        out.samples = output;
        out.capacity = AS_FRAME_SAMPLES;
        ok = as_session_drain_next_v0(session, &out, &result) == AS_END_OF_STREAM
            && result.produced_count == 0u && result.valid_count == 0u;
    }
    if (as_session_close_v0(&session) != AS_OK || session != NULL) ok = 0;
    record_case("caller_owned_exact_pcm", ok,
                "357 samples in 160/160/37 frames; bit-exact, D=0, EOS at drain");
    return ok;
}

static int expect_invalid(as_session_v0 *session, const as_frame_v0 *frame,
                          const as_output_v0 *output, const char *label,
                          char *detail, size_t capacity) {
    as_result_v0 result;
    as_result_v0_init(&result);
    const as_status_v0 status = as_session_process_v0(session, frame, output, &result);
    if (status != AS_INVALID_ARGUMENT || result.valid_count != 0u) {
        snprintf(detail, capacity, "%s returned %s", label,
                 as_status_name_v0(status));
        return 0;
    }
    return 1;
}

static int test_malformed(as_registry_v0 *registry, as_error_v0 *error) {
    as_session_v0 *session = NULL;
    char detail[192] = {0};
    int ok = create_session(registry, PROVIDER_ID, &session, error) == AS_OK;
    if (!ok) {
        record_case("malformed_inputs", 0, "session create failed");
        return 0;
    }
    float input[AS_FRAME_SAMPLES];
    float output[AS_FRAME_SAMPLES];
    fill_frame(input, 0u, AS_FRAME_SAMPLES);
    as_frame_v0 frame;
    as_output_v0 out;
    as_frame_v0_init(&frame);
    as_output_v0_init(&out);
    frame.input = input;
    frame.input_count = AS_FRAME_SAMPLES;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    frame.epoch = EPOCH;
    frame.first_input_sample = FIRST_SAMPLE;
    out.samples = output;
    out.capacity = AS_FRAME_SAMPLES;

    frame.input_valid_count = 159u;
    ok = ok && expect_invalid(session, &frame, &out, "partial-without-final",
                              detail, sizeof(detail));
    frame.input_valid_count = AS_FRAME_SAMPLES;
    input[7] = NAN;
    ok = ok && expect_invalid(session, &frame, &out, "nonfinite",
                              detail, sizeof(detail));
    fill_frame(input, 0u, AS_FRAME_SAMPLES);
    frame.epoch = EPOCH - 1u;
    ok = ok && expect_invalid(session, &frame, &out, "stale-epoch",
                              detail, sizeof(detail));
    frame.epoch = EPOCH;
    frame.first_input_sample = FIRST_SAMPLE + 1;
    ok = ok && expect_invalid(session, &frame, &out, "wrong-position",
                              detail, sizeof(detail));
    frame.first_input_sample = FIRST_SAMPLE;
    frame.input = NULL;
    ok = ok && expect_invalid(session, &frame, &out, "null-input",
                              detail, sizeof(detail));
    frame.input = input;
    out.capacity = 159u;
    ok = ok && expect_invalid(session, &frame, &out, "short-capacity",
                              detail, sizeof(detail));
    out.capacity = AS_FRAME_SAMPLES;
    frame.struct_size = (uint32_t)sizeof(frame) - 1u;
    ok = ok && expect_invalid(session, &frame, &out, "short-header",
                              detail, sizeof(detail));
    frame.struct_size = (uint32_t)sizeof(frame);

    as_result_v0 result;
    as_result_v0_init(&result);
    frame.input_valid_count = FINAL_VALID;
    frame.flags = AS_FRAME_FINAL_INPUT;
    fill_frame(input, 0u, FINAL_VALID); /* caller zero-pads the final frame */
    const as_status_v0 final_status = as_session_process_v0(session, &frame, &out, &result);
    if (final_status != AS_OK)
        snprintf(detail, sizeof(detail), "final process returned %s",
                 as_status_name_v0(final_status));
    ok = ok && final_status == AS_OK;
    frame.flags = 0u;
    frame.input_valid_count = AS_FRAME_SAMPLES;
    ok = ok && expect_invalid(session, &frame, &out, "after-final",
                              detail, sizeof(detail));
    const as_status_v0 close_status = as_session_close_v0(&session);
    if (close_status != AS_OK) {
        snprintf(detail, sizeof(detail), "close returned %s",
                 as_status_name_v0(close_status));
        ok = 0;
    }
    record_case("malformed_inputs", ok,
                ok ? "eight malformed/lifecycle probes returned zero-valid INVALID_ARGUMENT"
                   : detail);
    return ok;
}

static int test_missing_selections(as_registry_v0 *registry, as_error_v0 *error) {
    char config[2048];
    uint32_t required = 0u;
    as_session_v0 *session = NULL;
    uint8_t marker = 0u;
    as_asset_v0 asset;
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    as_asset_v0_init(&asset);
    const int ok =
        query(registry, UNREGISTERED_ID) == AS_UNSUPPORTED
        && effective(registry, UNREGISTERED_ID, AS_MODE_PROCESSING_THREAD,
                     config, (uint32_t)sizeof(config), &required, error) == AS_UNSUPPORTED
        && effective(registry, PROVIDER_ID, AS_MODE_INLINE_CALLBACK,
                     config, (uint32_t)sizeof(config), &required, error) == AS_UNSUPPORTED
        && effective(registry, PROVIDER_ID, AS_MODE_BUFFERED_WORKER,
                     config, (uint32_t)sizeof(config), &required, error) == AS_UNSUPPORTED
        && create_session(registry, UNREGISTERED_ID, &session, error) == AS_UNSUPPORTED
        && session == NULL
        && create_session(registry, PROVIDER_ID, &session, error) == AS_OK
        && (as_session_close_v0(&session) == AS_OK)
        && effective(registry, PROVIDER_ID, AS_MODE_PROCESSING_THREAD,
                     config, (uint32_t)sizeof(config), &required, error) == AS_OK;
    (void)marker;
    (void)asset;
    if (!ok) {
        record_case("missing_optional_selections", 0, "unregistered/unadvertised selection was accepted");
        return 0;
    }
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = EPOCH;
    create.first_input_sample = FIRST_SAMPLE;
    create.config_json = config;
    create.config_json_length = required - 1u;
    asset.asset_id = "fixture.unused";
    asset.asset_id_length = (uint32_t)strlen(asset.asset_id);
    asset.data = &marker;
    asset.byte_count = 1u;
    create.assets = &asset;
    create.asset_count = 1u;
    const int extra_rejected =
        as_session_create_v0(registry, PROVIDER_ID,
                             (uint32_t)strlen(PROVIDER_ID), &create, &session,
                             error) == AS_INVALID_ARGUMENT && session == NULL;
    record_case("missing_optional_selections", extra_rejected,
                extra_rejected
                    ? "unregistered ID, unadvertised modes and unrequested asset rejected"
                    : "unrequested asset was accepted");
    return extra_rejected;
}

static int write_report(const char *path, const char *conformance_path,
                        int conformance_exit) {
    FILE *file = fopen(path, "w");
    if (file == NULL) return 0;
    int passed = 0;
    for (size_t i = 0u; i < g_case_count; ++i)
        if (g_cases[i].ok) ++passed;
    fprintf(file,
            "{\"schema_id\":\"audio-sdk/task-evidence/identity-pcm/0.1\","
            "\"base_commit\":\"%s\",\"version\":\"0.1.0\","
            "\"build_id\":\"%s\",\"install_location\":\"extracted-prefix\","
            "\"archive_sha256\":\"%s\",\"provider_id\":\"%s\","
            "\"descriptor_source_digest\":\"%s\","
            "\"descriptor_config_digest\":\"%s\","
            "\"conformance_report\":\"%s\",\"conformance_exit\":%d,"
            "\"cases\":[",
            BASE_COMMIT, as_build_id_v0(), g_archive_sha256, PROVIDER_ID,
            kIdentitySourceDigest, kIdentityConfigDigest, conformance_path,
            conformance_exit);
    for (size_t i = 0u; i < g_case_count; ++i) {
        if (i != 0u) fputc(',', file);
        fprintf(file, "{\"id\":\"%s\",\"result\":\"%s\",\"detail\":\"%s\"}",
                g_cases[i].id, g_cases[i].ok ? "pass" : "fail",
                g_cases[i].detail);
    }
    fprintf(file, "],\"counts\":{\"total\":%zu,\"passed\":%d,\"failed\":%zu},"
                  "\"result\":\"%s\"}\n",
            g_case_count, passed, g_case_count - (size_t)passed,
            passed == (int)g_case_count && g_case_count == 5u ? "pass" : "fail");
    return fclose(file) == 0;
}

static void usage(const char *program) {
    fprintf(stderr,
            "usage: %s --report <path> --conformance-report <path> "
            "[--archive-sha256 <hex>]\n", program);
}

int main(int argc, char **argv) {
    const char *report_path = NULL;
    const char *conformance_path = NULL;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--report") == 0 && i + 1 < argc) {
            report_path = argv[++i];
        } else if (strcmp(argv[i], "--conformance-report") == 0 && i + 1 < argc) {
            conformance_path = argv[++i];
        } else if (strcmp(argv[i], "--archive-sha256") == 0 && i + 1 < argc) {
            g_archive_sha256 = argv[++i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (report_path == NULL || conformance_path == NULL) {
        usage(argv[0]);
        return 2;
    }

    as_error_v0 error;
    as_error_v0_init(&error);
    as_registry_v0 *registry = NULL;
    if (as_registry_create_v0(&registry, &error) != AS_OK) {
        fprintf(stderr, "registry: %s\n", error.message);
        return 2;
    }
    if (as_register_provider_v0(registry, identity_provider_table(), kDescriptor,
                                (uint32_t)(sizeof(kDescriptor) - 1u), &error) != AS_OK) {
        fprintf(stderr, "register: %s (%s)\n", error.message, error.field);
        as_registry_close_v0(&registry);
        return 2;
    }

    test_registration(registry, &error);
    test_caller_owned(registry, &error);
    test_malformed(registry, &error);
    test_missing_selections(registry, &error);

    char detail[256] = {0};
    const int conformance_exit = as_run_conformance(
        registry, PROVIDER_ID, (uint32_t)strlen(PROVIDER_ID), conformance_path,
        detail, (uint32_t)sizeof(detail));
    record_case("installed_conformance", conformance_exit == 0,
                conformance_exit == 0 ? "installed checks.c suite exited 0" : detail);

    const int report_written = write_report(report_path, "conformance-report.json",
                                            conformance_exit);
    if (as_registry_close_v0(&registry) != AS_OK) return 2;
    if (!report_written) return 2;
    for (size_t i = 0u; i < g_case_count; ++i)
        if (!g_cases[i].ok) return 1;
    return 0;
}
