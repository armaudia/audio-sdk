/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Standalone conformance checks for one registered provider.
 *
 * This file is compiled both into the installed SDK conformance executable and
 * into external-provider fixture projects that link only against an installed
 * prefix. It must therefore use public headers only and must not reach into
 * src/.
 *
 * The checks are provider-generic: the declared buffering delay, native hop,
 * drain bound, execution modes and edge exclusions are read from the canonical
 * descriptor bytes served by the registry, then verified against observed
 * behaviour on a deterministic seeded fixture. Only the delayed-identity
 * test fixture opts into exact tail PCM checks.
 */
#include "checks.h"

#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define FRAME_SAMPLES 160u
#define TIMING_FRAMES 40u
#define FIXTURE_SEED 20261113ull
#define MAX_BUFFERING_DELAY 16000u

/* ------------------------------------------------------------------ */
/* reporting                                                          */
/* ------------------------------------------------------------------ */

typedef struct reporter {
    FILE *file;
    int first;
    int passed;
    int failed;
    int skipped;
} reporter;

static void json_escape(FILE *file, const char *text) {
    for (const unsigned char *p = (const unsigned char *)text; *p != 0; ++p) {
        switch (*p) {
            case '"': fputs("\\\"", file); break;
            case '\\': fputs("\\\\", file); break;
            case '\n': fputs("\\n", file); break;
            case '\r': fputs("\\r", file); break;
            case '\t': fputs("\\t", file); break;
            default:
                if (*p < 0x20) {
                    fprintf(file, "\\u%04x", (unsigned)*p);
                } else {
                    fputc((int)*p, file);
                }
        }
    }
}

static void record(reporter *r, const char *id, const char *result,
                   const char *detail) {
    if (strcmp(result, "pass") == 0) {
        r->passed++;
    } else if (strcmp(result, "skip") == 0) {
        r->skipped++;
    } else {
        r->failed++;
    }
    if (r->file != NULL) {
        if (!r->first) fputc(',', r->file);
        r->first = 0;
        fputs("{\"id\":\"", r->file);
        json_escape(r->file, id);
        fputs("\",\"result\":\"", r->file);
        fputs(result, r->file);
        fputs("\",\"detail\":\"", r->file);
        json_escape(r->file, detail);
        fputs("\"}", r->file);
    }
    printf("%-28s %-4s %s\n", id, result, detail);
}

static void pass(reporter *r, const char *id, const char *fmt, ...) {
    char detail[512];
    va_list args;
    va_start(args, fmt);
    vsnprintf(detail, sizeof(detail), fmt, args);
    va_end(args);
    record(r, id, "pass", detail);
}

static void fail(reporter *r, const char *id, const char *fmt, ...) {
    char detail[512];
    va_list args;
    va_start(args, fmt);
    vsnprintf(detail, sizeof(detail), fmt, args);
    va_end(args);
    record(r, id, "fail", detail);
}

static void skip(reporter *r, const char *id, const char *fmt, ...) {
    char detail[512];
    va_list args;
    va_start(args, fmt);
    vsnprintf(detail, sizeof(detail), fmt, args);
    va_end(args);
    record(r, id, "skip", detail);
}

static void set_error(char *error, uint32_t capacity, const char *fmt, ...) {
    if (error == NULL || capacity == 0) return;
    va_list args;
    va_start(args, fmt);
    vsnprintf(error, capacity, fmt, args);
    va_end(args);
    error[capacity - 1u] = '\0';
}

/* ------------------------------------------------------------------ */
/* descriptor field extraction (canonical bytes, unique keys)         */
/* ------------------------------------------------------------------ */

static int field_value(const char *json, const char *key, const char **value) {
    char pattern[96];
    const int length = snprintf(pattern, sizeof(pattern), "\"%s\":", key);
    if (length <= 0) return 0;
    const char *found = strstr(json, pattern);
    if (found == NULL) return 0;
    *value = found + (size_t)length;
    return 1;
}

static int field_int(const char *json, const char *key, int64_t *out) {
    const char *value = NULL;
    if (!field_value(json, key, &value)) return 0;
    char *end = NULL;
    const long long parsed = strtoll(value, &end, 10);
    if (end == value) return 0;
    *out = (int64_t)parsed;
    return 1;
}

static int field_bool(const char *json, const char *key, int *out) {
    const char *value = NULL;
    if (!field_value(json, key, &value)) return 0;
    if (strncmp(value, "true", 4) == 0) {
        *out = 1;
        return 1;
    }
    if (strncmp(value, "false", 5) == 0) {
        *out = 0;
        return 1;
    }
    return 0;
}

static int field_string(const char *json, const char *key, char *out,
                        uint32_t capacity) {
    const char *value = NULL;
    if (!field_value(json, key, &value)) return 0;
    if (*value != '"') return 0;
    ++value;
    const char *end = strchr(value, '"');
    if (end == NULL) return 0;
    const size_t length = (size_t)(end - value);
    if (length + 1u > capacity) return 0;
    memcpy(out, value, length);
    out[length] = '\0';
    return 1;
}

static int modes_contain(const char *json, uint32_t mode) {
    const char *value = NULL;
    if (!field_value(json, "execution_modes", &value)) return 0;
    if (*value != '[') return 0;
    ++value;
    while (*value != ']' && *value != '\0') {
        char *end = NULL;
        const long parsed = strtol(value, &end, 10);
        if (end == value) break;
        if (parsed == (long)mode) return 1;
        value = end;
        while (*value == ',' || *value == ' ') ++value;
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/* deterministic fixture                                              */
/* ------------------------------------------------------------------ */

static uint64_t g_rng_state = FIXTURE_SEED;

static uint32_t next_u32(void) {
    g_rng_state ^= g_rng_state >> 12;
    g_rng_state ^= g_rng_state << 25;
    g_rng_state ^= g_rng_state >> 27;
    return (uint32_t)((g_rng_state * 2685821657736338717ull) >> 32);
}

static void make_fixture(float *out, uint32_t samples) {
    memset(out, 0, (size_t)samples * sizeof(float));
    const uint32_t starts[2] = {640u, 3200u};
    for (int burst = 0; burst < 2; ++burst) {
        for (uint32_t i = 0; i < 320u && starts[burst] + i < samples; ++i) {
            const float value =
                ((float)(next_u32() % 2001u) - 1000.0f) / 1000.0f;
            out[starts[burst] + i] = 0.25f * value;
        }
    }
}

/* ------------------------------------------------------------------ */
/* collector: interval conservation and raw output by emission order  */
/* ------------------------------------------------------------------ */

typedef struct collector {
    int64_t origin;
    uint32_t source_capacity;
    int64_t next_source;
    float *raw;
    uint32_t raw_capacity;
    uint32_t raw_length;
    int have_valid;
    int64_t next_valid;
    int64_t first_valid;
    uint32_t valid_total;
    int exact_tail_pcm;
    uint32_t tail_samples_checked;
    int failed;
    char error[256];
} collector;

static void collector_init(collector *c, int64_t origin,
                           uint32_t source_capacity, float *raw,
                           uint32_t raw_capacity) {
    memset(c, 0, sizeof(*c));
    c->origin = origin;
    c->next_source = origin;
    c->source_capacity = source_capacity;
    c->raw = raw;
    c->raw_capacity = raw_capacity;
}

static void collector_fail(collector *c, const char *fmt, ...) {
    if (c->failed) return;
    c->failed = 1;
    va_list args;
    va_start(args, fmt);
    vsnprintf(c->error, sizeof(c->error), fmt, args);
    va_end(args);
}

static void collector_add(collector *c, int64_t source_first,
                          const float *produced, uint32_t produced_count,
                          const as_result_v0 *result, uint32_t expected_consumed) {
    if (c->failed) return;
    const uint64_t offset = (uint64_t)source_first - (uint64_t)c->origin;
    if (source_first < c->next_source || offset > c->source_capacity ||
        produced_count > c->source_capacity - offset) {
        collector_fail(c, "output at %lld (%u samples) overlaps or is outside "
                          "the collector window",
                       (long long)source_first, produced_count);
        return;
    }
    c->next_source = source_first + produced_count;
    if (c->raw_length + produced_count > c->raw_capacity) {
        collector_fail(c, "raw output exceeds its capacity");
        return;
    }
    memcpy(c->raw + c->raw_length, produced,
           (size_t)produced_count * sizeof(float));
    c->raw_length += produced_count;

    if (result->valid_offset > produced_count ||
        result->valid_count > produced_count - result->valid_offset) {
        collector_fail(c, "valid range exceeds produced samples");
        return;
    }
    if (result->consumed_count != expected_consumed) {
        collector_fail(c, "consumed %u samples, expected %u",
                       result->consumed_count, expected_consumed);
        return;
    }
    if (result->valid_count > 0) {
        const int64_t start = source_first + (int64_t)result->valid_offset;
        if (c->have_valid && start != c->next_valid) {
            collector_fail(c,
                           "valid intervals are not contiguous: expected "
                           "%lld, got %lld (%llu)",
                           (long long)c->next_valid, (long long)start,
                           (unsigned long long)result->valid_count);
            return;
        }
        if (!c->have_valid) c->first_valid = start;
        c->have_valid = 1;
        c->next_valid = start + (int64_t)result->valid_count;
        c->valid_total += result->valid_count;
    }
}

/* ------------------------------------------------------------------ */
/* session setup                                                      */
/* ------------------------------------------------------------------ */

typedef struct session_info {
    uint32_t buffering_delay;
    uint32_t native_hop;
    uint32_t max_drain_calls;
    uint32_t edge_start;
    uint32_t edge_end;
    int callback_safe;
    int exact_tail_pcm;
} session_info;

static as_status_v0 create_session(as_registry_v0 *registry,
                                   const char *provider_id,
                                   uint32_t provider_id_length,
                                   uint32_t execution_mode, uint64_t epoch,
                                   int64_t first_input_sample,
                                   as_session_v0 **out, char *error,
                                   uint32_t error_capacity) {
    *out = NULL;
    char config[4096];
    uint32_t required = 0;
    as_error_v0 as_error;
    as_error_v0_init(&as_error);
    as_status_v0 status = as_effective_config_create_v0(
        registry, provider_id, provider_id_length, execution_mode, config,
        (uint32_t)sizeof(config), &required, &as_error);
    if (status != AS_OK) {
        set_error(error, error_capacity, "effective config: %s (%s)",
                  as_error.message, as_error.field);
        return status;
    }
    if (required == 0 || required > sizeof(config)) {
        set_error(error, error_capacity, "effective config size is invalid");
        return AS_BACKEND_FAILURE;
    }
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = execution_mode;
    create.epoch = epoch;
    create.first_input_sample = first_input_sample;
    create.config_json = config;
    create.config_json_length = required - 1u;
    as_session_v0 *session = NULL;
    as_error_v0_init(&as_error);
    status = as_session_create_v0(registry, provider_id, provider_id_length,
                                  &create, &session, &as_error);
    if (status != AS_OK) {
        set_error(error, error_capacity, "session create: %s (%s)",
                  as_error.message, as_error.field);
        return status;
    }
    *out = session;
    return AS_OK;
}

typedef struct frame_call {
    float produced[FRAME_SAMPLES];
    as_result_v0 result;
} frame_call;

static as_status_v0 process_frame(as_session_v0 *session, float *input,
                                  uint32_t input_valid, uint32_t flags,
                                  uint64_t epoch, int64_t first_sample,
                                  frame_call *call) {
    as_frame_v0 frame;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.input_count = FRAME_SAMPLES;
    frame.input_valid_count = input_valid;
    frame.flags = flags;
    frame.epoch = epoch;
    frame.first_input_sample = first_sample;
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = call->produced;
    output.capacity = FRAME_SAMPLES;
    as_result_v0_init(&call->result);
    return as_session_process_v0(session, &frame, &output, &call->result);
}

static as_status_v0 drain_frame(as_session_v0 *session, frame_call *call) {
    as_output_v0 output;
    as_output_v0_init(&output);
    output.samples = call->produced;
    output.capacity = FRAME_SAMPLES;
    as_result_v0_init(&call->result);
    return as_session_drain_next_v0(session, &output, &call->result);
}

static as_status_v0 wait_frame(as_session_v0 *session, frame_call *call) {
    const struct timespec pause = {0, 1000000L};
    for (unsigned attempt = 0; attempt < 2000; ++attempt) {
        const as_status_v0 status = drain_frame(session, call);
        if (status != AS_NOT_READY) return status;
        nanosleep(&pause, NULL);
    }
    return AS_NOT_READY;
}

/* Test one input/output at a time here; check_buffered covers queue saturation. */
static int run_stream(as_session_v0 *session, const float *fixture,
                      uint32_t length, uint64_t epoch, int64_t first_sample,
                      uint32_t buffering_delay, uint32_t mode, collector *c,
                      char *error, uint32_t error_capacity) {
    const int buffered = mode == AS_MODE_BUFFERED_WORKER;
    for (uint32_t offset = 0; offset < length; offset += FRAME_SAMPLES) {
        float input[FRAME_SAMPLES] = {0};
        const uint32_t remaining = length - offset;
        const uint32_t valid = remaining < FRAME_SAMPLES ? remaining : FRAME_SAMPLES;
        const uint32_t flags = valid < FRAME_SAMPLES ? AS_FRAME_FINAL_INPUT : 0;
        const int64_t first = first_sample + offset;
        memcpy(input, fixture + offset, valid * sizeof(float));
        frame_call call;
        as_status_v0 status;
        if (buffered) {
            as_frame_v0 frame;
            as_frame_v0_init(&frame);
            frame.input = input;
            frame.input_valid_count = valid;
            frame.flags = flags;
            frame.epoch = epoch;
            frame.first_input_sample = first;
            as_result_v0_init(&call.result);
            status = as_session_submit_v0(session, &frame, &call.result);
            if (status != AS_OK || call.result.status != AS_OK ||
                call.result.epoch != epoch || call.result.source_first_sample != first ||
                call.result.consumed_count != FRAME_SAMPLES ||
                call.result.produced_count != 0 || call.result.valid_count != 0) {
                set_error(error, error_capacity, "submit at %u: %s or bad metadata",
                          offset, as_status_name_v0(status));
                return 0;
            }
            status = wait_frame(session, &call);
        } else {
            status = process_frame(session, input, valid, flags, epoch, first, &call);
        }
        if (status != AS_OK) {
            set_error(error, error_capacity, "output at %u failed: %s",
                      offset, as_status_name_v0(status));
            return 0;
        }
        if (call.result.status != AS_OK || call.result.epoch != epoch ||
            call.result.source_first_sample != first - buffering_delay ||
            call.result.produced_count != FRAME_SAMPLES) {
            set_error(error, error_capacity,
                      "process metadata mismatch at offset %u", offset);
            return 0;
        }
        collector_add(c, call.result.source_first_sample,
                      call.produced, call.result.produced_count, &call.result,
                      buffered ? 0 : FRAME_SAMPLES);
        if (c->failed) {
            set_error(error, error_capacity, "%s", c->error);
            return 0;
        }
    }
    if (!buffered || length % FRAME_SAMPLES == 0) {
        const as_status_v0 begin = as_session_begin_drain_v0(session);
        if (begin != AS_OK) {
            set_error(error, error_capacity, "begin_drain failed: %s",
                      as_status_name_v0(begin));
            return 0;
        }
    }
    for (unsigned calls = 0; calls < 4096; ++calls) {
        frame_call call;
        const as_status_v0 status = buffered ? wait_frame(session, &call)
                                             : drain_frame(session, &call);
        if (status == AS_END_OF_STREAM) {
            if (call.result.status == AS_END_OF_STREAM && call.result.epoch == epoch &&
                call.result.consumed_count == 0 && call.result.produced_count == 0 &&
                call.result.valid_count == 0) return 1;
            set_error(error, error_capacity, "EOS metadata mismatch");
            return 0;
        }
        if (status != AS_OK) {
            set_error(error, error_capacity, "drain failed: %s",
                      as_status_name_v0(status));
            return 0;
        }
        if (call.result.status != AS_OK || call.result.epoch != epoch) {
            set_error(error, error_capacity, "drain metadata mismatch");
            return 0;
        }
        collector_add(c, call.result.source_first_sample,
                      call.produced, call.result.produced_count, &call.result,
                      0);
        if (c->failed) {
            set_error(error, error_capacity, "%s", c->error);
            return 0;
        }
        if (c->exact_tail_pcm && call.result.valid_count > 0) {
            const int64_t first_valid =
                call.result.source_first_sample + call.result.valid_offset - first_sample;
            if (first_valid < 0 || first_valid + call.result.valid_count > length) {
                set_error(error, error_capacity, "drain validity is outside the input");
                return 0;
            }
            for (uint32_t i = 0; i < call.result.valid_count; ++i) {
                if (call.produced[call.result.valid_offset + i] != fixture[first_valid + i]) {
                    set_error(error, error_capacity, "drain PCM mismatch at input offset %lld",
                              (long long)(first_valid + i));
                    return 0;
                }
            }
            c->tail_samples_checked += call.result.valid_count;
        }
    }
    set_error(error, error_capacity, "drain did not terminate within 4096 calls");
    return 0;
}

/* ------------------------------------------------------------------ */
/* Measure lag from samples in emission order, never source metadata.  */
/* ------------------------------------------------------------------ */

static double correlation_at(const float *output, const float *input,
                             uint32_t count) {
    double dot = 0.0;
    double out_energy = 0.0;
    double in_energy = 0.0;
    for (uint32_t k = 0; k < count; ++k) {
        const double out = output[k];
        const double in = input[k];
        dot += out * in;
        out_energy += out * out;
        in_energy += in * in;
    }
    if (out_energy <= 0.0 || in_energy <= 0.0) return 0.0;
    return dot / sqrt(out_energy * in_energy);
}

static int measure_raw_lag(const float *raw, uint32_t raw_count,
                           const float *input, uint32_t count,
                           uint32_t *lag_out, double *peak_out, double *second_out) {
    uint32_t best_lag = 0;
    double best = -2.0;
    double second = -2.0;
    for (uint32_t lag = 0; lag <= MAX_BUFFERING_DELAY && lag + count <= raw_count;
         ++lag) {
        const double value = correlation_at(raw + lag, input, count);
        if (value > best) {
            second = best;
            best = value;
            best_lag = lag;
        } else if (value > second) {
            second = value;
        }
    }
    *lag_out = best_lag;
    *peak_out = best;
    *second_out = second;
    return best >= 0.85 && (best - second) >= 0.03;
}

/* ------------------------------------------------------------------ */
/* individual checks                                                  */
/* ------------------------------------------------------------------ */

static int check_descriptor(as_registry_v0 *registry, reporter *r,
                            const char *provider_id,
                            uint32_t provider_id_length, char *descriptor,
                            uint32_t descriptor_capacity, session_info *info,
                            char *error, uint32_t error_capacity) {
    char small[8];
    uint32_t required = 0;
    as_status_v0 status = as_query_provider_v0(
        registry, provider_id, provider_id_length, small, (uint32_t)sizeof(small),
        &required);
    if (status != AS_RESOURCE_EXHAUSTED) {
        fail(r, "descriptor.query",
             "small-buffer query returned %s, expected resource_exhausted",
             as_status_name_v0(status));
        return 0;
    }
    if (required < 2 || required > descriptor_capacity) {
        fail(r, "descriptor.query", "required size %u is out of range",
             required);
        return 0;
    }
    status = as_query_provider_v0(registry, provider_id, provider_id_length,
                                  descriptor, descriptor_capacity, &required);
    if (status != AS_OK) {
        fail(r, "descriptor.query", "query failed: %s",
             as_status_name_v0(status));
        return 0;
    }
    if (descriptor[required - 1u] != '\0') {
        fail(r, "descriptor.query", "descriptor is not NUL-terminated");
        return 0;
    }
    pass(r, "descriptor.query", "%u bytes including terminator", required);

    uint32_t too_small = required - 1u;
    status = as_query_provider_v0(registry, provider_id, provider_id_length,
                                  descriptor, too_small, &too_small);
    if (status != AS_RESOURCE_EXHAUSTED || too_small != required) {
        fail(r, "descriptor.truncation",
             "truncated query returned %s and required %u",
             as_status_name_v0(status), too_small);
    } else {
        pass(r, "descriptor.truncation",
             "no partial output; required size reported");
    }

    char hex[65];
    status = as_provider_digest_v0(registry, provider_id, provider_id_length,
                                   hex, (uint32_t)sizeof(hex));
    if (status != AS_OK) {
        fail(r, "descriptor.digest", "digest query failed: %s",
             as_status_name_v0(status));
        return 0;
    }
    char expected[65];
    as_sha256_hex_v0(descriptor, required - 1u, expected,
                     (uint32_t)sizeof(expected));
    if (memcmp(hex, expected, 65) != 0) {
        fail(r, "descriptor.digest", "reported digest %s != bytes digest %s",
             hex, expected);
        return 0;
    }
    pass(r, "descriptor.digest", "%s", hex);

    char schema[96];
    char contract[32];
    char declared_id[128];
    if (!field_string(descriptor, "schema_id", schema, sizeof(schema)) ||
        strcmp(schema, "audio-sdk/descriptor/0.1") != 0) {
        fail(r, "descriptor.schema", "schema_id is missing or unsupported");
        return 0;
    }
    if (!field_string(descriptor, "contract_version", contract,
                      sizeof(contract))) {
        fail(r, "descriptor.schema", "contract_version is missing");
        return 0;
    }
    if (!field_string(descriptor, "provider_id", declared_id,
                      sizeof(declared_id)) ||
        strlen(declared_id) != (size_t)provider_id_length ||
        memcmp(declared_id, provider_id, provider_id_length) != 0) {
        fail(r, "descriptor.schema", "descriptor provider_id does not match");
        return 0;
    }
    pass(r, "descriptor.schema", "schema 0.1; contract %s", contract);

    char implementation[128];
    info->exact_tail_pcm =
        field_string(descriptor, "implementation_id", implementation, sizeof(implementation)) &&
        strcmp(implementation, "fixture.delayed_identity") == 0;

    int64_t value = 0;
    if (!field_int(descriptor, "buffering_delay_samples", &value) ||
        value < 0 || value > 16000) {
        fail(r, "descriptor.delay", "buffering_delay_samples is invalid");
        return 0;
    }
    info->buffering_delay = (uint32_t)value;
    if (!field_int(descriptor, "native_hop_samples", &value) || value < 1 ||
        value > 16000) {
        fail(r, "descriptor.delay", "native_hop_samples is invalid");
        return 0;
    }
    info->native_hop = (uint32_t)value;
    if (!field_int(descriptor, "max_drain_calls", &value) || value < 1 ||
        value > 1024) {
        fail(r, "descriptor.drain", "max_drain_calls is invalid");
        return 0;
    }
    info->max_drain_calls = (uint32_t)value;
    int boolean = 0;
    if (!field_bool(descriptor, "callback_safe", &boolean)) {
        fail(r, "descriptor.modes", "callback_safe is missing");
        return 0;
    }
    info->callback_safe = boolean;
    const char *exclusions = NULL;
    if (!field_value(descriptor, "edge_exclusions", &exclusions) ||
        *exclusions != '{') {
        fail(r, "descriptor.edges", "edge_exclusions is missing");
        return 0;
    }
    char edges[256];
    const char *end = strchr(exclusions, '}');
    if (end == NULL || (size_t)(end - exclusions) + 2u > sizeof(edges)) {
        fail(r, "descriptor.edges", "edge_exclusions is malformed");
        return 0;
    }
    const size_t edge_length = (size_t)(end - exclusions) + 1u;
    memcpy(edges, exclusions, edge_length);
    edges[edge_length] = '\0';
    if (!field_int(edges, "start_samples", &value) || value < 0 ||
        value > 16000) {
        fail(r, "descriptor.edges", "edge start is invalid");
        return 0;
    }
    info->edge_start = (uint32_t)value;
    if (!field_int(edges, "end_samples", &value) || value < 0 ||
        value > 16000) {
        fail(r, "descriptor.edges", "edge end is invalid");
        return 0;
    }
    info->edge_end = (uint32_t)value;
    pass(r, "descriptor.delay", "delay=%u hop=%u drain<=%u edges=%u/%u",
         info->buffering_delay, info->native_hop, info->max_drain_calls,
         info->edge_start, info->edge_end);
    (void)error;
    (void)error_capacity;
    return 1;
}

static void check_create_modes(as_registry_v0 *registry, reporter *r,
                               const char *provider_id,
                               uint32_t provider_id_length,
                               const char *descriptor,
                               const session_info *info) {
    for (uint32_t mode = AS_MODE_INLINE_CALLBACK;
         mode <= AS_MODE_BUFFERED_WORKER; ++mode) {
        char id[64];
        snprintf(id, sizeof(id), "create.mode%u", mode);
        const int declared = modes_contain(descriptor, mode);
        char error[256];
        as_session_v0 *session = NULL;
        const as_status_v0 status = create_session(
            registry, provider_id, provider_id_length, mode, 1, 0, &session,
            error, sizeof(error));
        if (declared) {
            if (status == AS_OK) {
                pass(r, id, "created");
                as_session_close_v0(&session);
            } else {
                fail(r, id, "declared mode failed to create: %s", error);
            }
        } else if (status == AS_UNSUPPORTED) {
            pass(r, id, "undeclared mode rejected with unsupported");
        } else {
            fail(r, id, "undeclared mode returned %s",
                 as_status_name_v0(status));
        }
    }
    if (info->callback_safe) {
        pass(r, "create.callback", "provider declares callback_safe");
    } else if (modes_contain(descriptor, AS_MODE_INLINE_CALLBACK)) {
        fail(r, "create.callback",
             "mode 1 is declared without callback_safe");
    } else {
        pass(r, "create.callback",
             "mode 1 not advertised (callback_safe false)");
    }
}

static void check_invalid_create(as_registry_v0 *registry, reporter *r,
                                 const char *provider_id,
                                 uint32_t provider_id_length,
                                 const char *descriptor,
                                 const session_info *info) {
    char config[4096];
    uint32_t required = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    const uint32_t mode = modes_contain(descriptor, AS_MODE_PROCESSING_THREAD)
                              ? AS_MODE_PROCESSING_THREAD
                              : AS_MODE_BUFFERED_WORKER;
    if (as_effective_config_create_v0(registry, provider_id,
                                      provider_id_length, mode, config,
                                      (uint32_t)sizeof(config), &required,
                                      &error) != AS_OK) {
        fail(r, "create.invalid", "could not build a reference configuration");
        return;
    }

    struct {
        uint32_t sample_rate_hz;
        uint32_t channels;
        uint32_t frame_samples;
        uint32_t execution_mode;
        as_status_v0 expected;
        const char *name;
    } cases[] = {
        {44100u, 1u, 160u, mode, AS_UNSUPPORTED, "sample_rate"},
        {16000u, 2u, 160u, mode, AS_UNSUPPORTED, "channels"},
        {16000u, 1u, 320u, mode, AS_UNSUPPORTED, "frame_samples"},
    };
    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.sample_rate_hz = cases[i].sample_rate_hz;
        create.channels = cases[i].channels;
        create.frame_samples = cases[i].frame_samples;
        create.execution_mode = cases[i].execution_mode;
        create.epoch = 1;
        create.config_json = config;
        create.config_json_length = required - 1u;
        as_error_v0_init(&error);
        as_session_v0 *session = NULL;
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        char id[64];
        snprintf(id, sizeof(id), "create.reject.%s", cases[i].name);
        if (status == cases[i].expected && session == NULL) {
            pass(r, id, "rejected with %s", as_status_name_v0(status));
        } else {
            fail(r, id, "returned %s, expected %s",
                 as_status_name_v0(status),
                 as_status_name_v0(cases[i].expected));
        }
    }

    /* Execution mode 1 is only valid when declared and callback-safe. */
    if (!modes_contain(descriptor, AS_MODE_INLINE_CALLBACK)) {
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.execution_mode = AS_MODE_INLINE_CALLBACK;
        create.epoch = 1;
        create.config_json = config;
        create.config_json_length = required - 1u;
        as_error_v0_init(&error);
        as_session_v0 *session = NULL;
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        if (status == AS_UNSUPPORTED) {
            pass(r, "create.reject.mode1",
                 "undeclared mode 1 rejected");
        } else {
            fail(r, "create.reject.mode1", "returned %s",
                 as_status_name_v0(status));
        }
    }

    /* Reserved fields and trailing bytes must be rejected. */
    {
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.execution_mode = mode;
        create.epoch = 1;
        create.config_json = config;
        create.config_json_length = required - 1u;
        create.reserved0 = 1;
        as_session_v0 *session = NULL;
        as_error_v0_init(&error);
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        if (status == AS_INVALID_ARGUMENT) {
            pass(r, "create.reject.reserved", "nonzero reserved field rejected");
        } else {
            fail(r, "create.reject.reserved", "returned %s",
                 as_status_name_v0(status));
        }
    }
    {
        struct {
            as_create_config_v0 config;
            uint64_t tail;
        } extended;
        memset(&extended, 0, sizeof(extended));
        as_create_config_v0_init(&extended.config);
        extended.config.struct_size = (uint32_t)sizeof(extended);
        extended.config.execution_mode = mode;
        extended.config.epoch = 1;
        extended.config.config_json = config;
        extended.config.config_json_length = required - 1u;
        extended.tail = 1;
        as_session_v0 *session = NULL;
        as_error_v0_init(&error);
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &extended.config,
            &session, &error);
        if (status == AS_INVALID_ARGUMENT) {
            pass(r, "create.reject.tail", "nonzero trailing bytes rejected");
        } else {
            fail(r, "create.reject.tail", "returned %s",
                 as_status_name_v0(status));
        }
    }

    /* Non-canonical or semantically mismatched effective configuration. */
    {
        char tampered[4096];
        memcpy(tampered, config, required);
        memmove(tampered + 1, tampered, required);
        tampered[0] = ' ';
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.execution_mode = mode;
        create.epoch = 1;
        create.config_json = tampered;
        create.config_json_length = required;
        as_session_v0 *session = NULL;
        as_error_v0_init(&error);
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        if (status == AS_INVALID_ARGUMENT) {
            pass(r, "create.reject.canonical",
                 "non-canonical configuration rejected");
        } else {
            fail(r, "create.reject.canonical", "returned %s",
                 as_status_name_v0(status));
        }
    }
    {
        char tampered[4096];
        memcpy(tampered, config, required);
        char *digest = strstr(tampered, "\"descriptor_digest\":\"sha256:");
        if (digest != NULL) {
            digest += strlen("\"descriptor_digest\":\"sha256:");
            digest[0] = digest[0] == '0' ? '1' : '0';
        }
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.execution_mode = mode;
        create.epoch = 1;
        create.config_json = tampered;
        create.config_json_length = required - 1u;
        as_session_v0 *session = NULL;
        as_error_v0_init(&error);
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        if (status == AS_INVALID_ARGUMENT) {
            pass(r, "create.reject.digest",
                 "descriptor digest mismatch rejected");
        } else {
            fail(r, "create.reject.digest", "returned %s",
                 as_status_name_v0(status));
        }
    }
    {
        char tampered[4096];
        memcpy(tampered, config, required);
        char marker[160];
        snprintf(marker, sizeof(marker), "\"id\":\"%s\"", provider_id);
        char *id = strstr(tampered, marker);
        if (id != NULL) {
            id += strlen("\"id\":\"");
            id[0] = id[0] == 'z' ? 'y' : 'z';
        }
        as_create_config_v0 create;
        as_create_config_v0_init(&create);
        create.execution_mode = mode;
        create.epoch = 1;
        create.config_json = tampered;
        create.config_json_length = required - 1u;
        as_session_v0 *session = NULL;
        as_error_v0_init(&error);
        const as_status_v0 status = as_session_create_v0(
            registry, provider_id, provider_id_length, &create, &session,
            &error);
        if (status == AS_INVALID_ARGUMENT) {
            pass(r, "create.reject.processor",
                 "processor identity mismatch rejected");
        } else {
            fail(r, "create.reject.processor", "returned %s",
                 as_status_name_v0(status));
        }
    }
    (void)info;
}

static void check_process_metadata(as_registry_v0 *registry, reporter *r,
                                   const char *provider_id,
                                   uint32_t provider_id_length,
                                   const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    const uint32_t mode = modes_contain(
                              (const char *)"", 0)
                              ? 0
                              : 0;
    (void)mode;
    const as_status_v0 created =
        create_session(registry, provider_id, provider_id_length,
                       AS_MODE_PROCESSING_THREAD, 7, 0, &session, error,
                       sizeof(error));
    if (created != AS_OK) {
        fail(r, "process.metadata", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    make_fixture(input, FRAME_SAMPLES);
    frame_call call;
    as_status_v0 status = process_frame(session, input, FRAME_SAMPLES, 0, 7, 0,
                                        &call);
    if (status != AS_OK) {
        fail(r, "process.metadata", "process failed: %s",
             as_status_name_v0(status));
        as_session_close_v0(&session);
        return;
    }
    const as_result_v0 *result = &call.result;
    const int64_t expected_source =
        -(int64_t)info->buffering_delay;
    const int checks_ok =
        result->status == AS_OK && result->consumed_count == FRAME_SAMPLES &&
        result->produced_count == FRAME_SAMPLES && result->epoch == 7 &&
        result->source_first_sample == expected_source &&
        result->valid_offset <= result->produced_count &&
        result->valid_count <= result->produced_count - result->valid_offset &&
        result->queue_depth == 0;
    if (!checks_ok) {
        fail(r, "process.metadata",
             "consumed=%u produced=%u source=%lld epoch=%llu valid=%u+%u",
             result->consumed_count, result->produced_count,
             (long long)result->source_first_sample,
             (unsigned long long)result->epoch, result->valid_offset,
             result->valid_count);
    } else if (info->buffering_delay > 0 &&
               (result->flags & AS_RESULT_STARTUP_PADDING) == 0) {
        fail(r, "process.metadata",
             "delay %u but no STARTUP_PADDING flag", info->buffering_delay);
    } else {
        pass(r, "process.metadata",
             "consumed=160 produced=160 source=%lld flags=0x%x",
             (long long)result->source_first_sample, result->flags);
    }
    as_session_close_v0(&session);
}

static void check_timing(as_registry_v0 *registry, reporter *r,
                         const char *provider_id,
                         uint32_t provider_id_length,
                         const session_info *info, uint32_t mode) {
    char error[256];
    const uint32_t frames = TIMING_FRAMES + info->buffering_delay / FRAME_SAMPLES;
    const uint32_t length = frames * FRAME_SAMPLES + 7u;
    float *fixture = (float *)malloc(length * sizeof(float));
    const uint32_t source_capacity = info->buffering_delay + length + FRAME_SAMPLES;
    const uint32_t raw_capacity_frames = frames + info->max_drain_calls + 2u;
    float *raw = (float *)malloc(
        (size_t)raw_capacity_frames * FRAME_SAMPLES * sizeof(float));
    const int buffered = mode == AS_MODE_BUFFERED_WORKER;
    const char *delay_id = buffered ? "buffered.delay" : "timing.delay";
    if (fixture == NULL || raw == NULL) {
        free(fixture);
        free(raw);
        fail(r, delay_id, "fixture allocation failed");
        return;
    }
    g_rng_state = FIXTURE_SEED;
    make_fixture(fixture, length);

    for (int epoch_case = 0; epoch_case < 2; ++epoch_case) {
        const uint64_t epoch = epoch_case == 0 ? 11 : UINT64_C(9007199254740993);
        const int64_t first = epoch_case == 0 ? 0 : INT64_C(9007199254740993);
        const char *id = epoch_case == 0 ? delay_id :
                         buffered ? "buffered.start" : "timing.start";
        as_session_v0 *session = NULL;
        const as_status_v0 created = create_session(
            registry, provider_id, provider_id_length, mode,
            epoch, first, &session, error, sizeof(error));
        if (created != AS_OK) {
            fail(r, id, "create failed: %s", error);
            continue;
        }
        collector c;
        collector_init(&c, first - info->buffering_delay, source_capacity, raw,
                         raw_capacity_frames * FRAME_SAMPLES);
        const int ok = run_stream(session, fixture, length, epoch, first,
                                  info->buffering_delay, mode, &c, error, sizeof(error));
        as_session_close_v0(&session);
        if (!ok) {
            fail(r, id, "stream failed: %s", error);
            continue;
        }
        double peak = 0.0;
        double second = 0.0;
        uint32_t raw_lag = 0;
        /* 640 is the first broadband burst's input index. Use process PCM only. */
        const int unique = measure_raw_lag(raw + 640, frames * FRAME_SAMPLES - 640,
                                           fixture + 640, 320, &raw_lag, &peak, &second);
        const int residual = (int)raw_lag - (int)info->buffering_delay;
        if (!unique || abs(residual) > 1) {
            fail(r, id,
                 "first=%lld declared=%u raw=%u residual=%d peak=%.6f second=%.6f unique=%d",
                 (long long)first, info->buffering_delay, raw_lag, residual, peak,
                 second, unique);
            continue;
        }
        pass(r, id,
             "first=%lld epoch=%llu length=%u declared=%u raw=%u residual=%d peak=%.6f second=%.6f",
             (long long)first, (unsigned long long)epoch, length,
             info->buffering_delay, raw_lag, residual, peak, second);
    }
    free(fixture);
    free(raw);
}

static void check_boundaries(as_registry_v0 *registry, reporter *r,
                              const char *provider_id,
                              uint32_t provider_id_length,
                              const session_info *info, uint32_t mode) {
    const char *id = mode == AS_MODE_BUFFERED_WORKER ? "buffered.lengths"
                                                     : "boundary.lengths";
    const int64_t first = INT64_C(9007199254740993);
    uint32_t tested = 0;
    uint32_t failures = 0;
    uint32_t tail_samples_checked = 0;
    char detail[512];
    detail[0] = '\0';
    size_t detail_length = 0;
    const uint32_t source_capacity =
        info->buffering_delay + 3u * FRAME_SAMPLES + 160u;
    float fixture[3u * FRAME_SAMPLES];
    const uint32_t raw_capacity_frames = 3u + info->max_drain_calls + 2u;
    float *raw =
        (float *)malloc((size_t)raw_capacity_frames * FRAME_SAMPLES *
                        sizeof(float));
    if (raw == NULL) {
        fail(r, id, "fixture allocation failed");
        return;
    }
    g_rng_state = FIXTURE_SEED;
    for (uint32_t i = 0; i < 3u * FRAME_SAMPLES; ++i)
        fixture[i] = (2.0f * (float)(next_u32() % 1024u) - 1023.0f) / 8192.0f;

    /* Exercise empty input, every partial-frame remainder, and the explicit
     * frame-crossing boundaries called out in TEST_PLAN.md. */
    uint32_t lengths[168];
    uint32_t length_count = 0;
    lengths[length_count++] = 0;
    for (uint32_t remainder = 1; remainder <= 159; ++remainder)
        lengths[length_count++] = remainder;
    const uint32_t explicit_lengths[] = {160u, 161u, 165u, 319u, 320u, 321u};
    for (size_t i = 0; i < sizeof(explicit_lengths) / sizeof(explicit_lengths[0]);
         ++i)
        lengths[length_count++] = explicit_lengths[i];

    for (uint32_t index = 0; index < length_count; ++index) {
        const uint32_t length = lengths[index];
        const uint64_t epoch = UINT64_C(9007199254740993) + index;
        char error[256];
        as_session_v0 *session = NULL;
        const as_status_v0 created = create_session(
            registry, provider_id, provider_id_length, mode, epoch, first, &session, error,
            (uint32_t)sizeof(error));
        if (created != AS_OK) {
            ++failures;
            if (detail_length < sizeof(detail) - 80u)
                detail_length += (size_t)snprintf(
                    detail + detail_length, sizeof(detail) - detail_length,
                    "L=%u create:%s; ", length,
                    as_status_name_v0(created));
            continue;
        }
        collector c;
        collector_init(&c, first - info->buffering_delay, source_capacity, raw,
                         raw_capacity_frames * FRAME_SAMPLES);
        c.exact_tail_pcm = info->exact_tail_pcm;
        int ok = run_stream(session, fixture, length, epoch, first,
                            info->buffering_delay, mode, &c, error, sizeof(error));
        tail_samples_checked += c.tail_samples_checked;
        if (ok && (info->edge_start || info->edge_end)) {
            as_error_v0 reset_error;
            as_error_v0_init(&reset_error);
            char stats[4096];
            char samples[32], intervals[32];
            uint32_t required = 0;
            ok = as_session_reset_v0(session, epoch + 1, first, &reset_error) == AS_OK &&
                 as_session_get_stats_v0(session, stats, sizeof(stats), &required) == AS_OK &&
                 field_string(stats, "cancelled_valid_samples", samples, sizeof(samples)) &&
                 field_string(stats, "cancelled_intervals", intervals, sizeof(intervals)) &&
                 strcmp(samples, "0") == 0 && strcmp(intervals, "0") == 0;
            if (!ok)
                set_error(error, sizeof(error), "clean EOS reset did not report zero cancellation");
        }
        as_session_close_v0(&session);
        ++tested;
        const uint32_t expected_valid =
            length > info->edge_start + info->edge_end
                ? length - info->edge_start - info->edge_end
                : 0u;
        const int exact_range = expected_valid == 0 ? !c.have_valid :
            c.have_valid && c.first_valid == first + info->edge_start &&
            c.next_valid == first + length - info->edge_end;
        if (!ok || !exact_range || c.valid_total != expected_valid ||
            (length == 0 && c.raw_length != 0)) {
            ++failures;
            if (detail_length < sizeof(detail) - 120u)
                detail_length += (size_t)snprintf(
                    detail + detail_length, sizeof(detail) - detail_length,
                    "L=%u valid=%u/%u range=%d%s%s; ", length, c.valid_total,
                    expected_valid, exact_range, ok ? "" : " ", ok ? "" : error);
        }
    }
    free(raw);
    if (failures == 0) {
        if (info->exact_tail_pcm) {
            pass(r, id, "%u lengths conserved exactly at source %lld; %u drain PCM samples matched exactly",
                 tested, (long long)first, tail_samples_checked);
        } else {
            pass(r, id, "%u lengths conserved exactly at source %lld",
                 tested, (long long)first);
        }
    } else {
        fail(r, id, "%u/%u failed: %s", failures, tested,
             detail);
    }
}

static void check_eos_repeat(as_registry_v0 *registry, reporter *r,
                             const char *provider_id,
                             uint32_t provider_id_length,
                             const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    if (create_session(registry, provider_id, provider_id_length,
                       AS_MODE_PROCESSING_THREAD, 31, 0, &session, error,
                       sizeof(error)) != AS_OK) {
        fail(r, "drain.eos", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    frame_call call;
    if (process_frame(session, input, FRAME_SAMPLES, 0, 31, 0, &call) != AS_OK) {
        fail(r, "drain.eos", "process failed");
        as_session_close_v0(&session);
        return;
    }
    if (as_session_begin_drain_v0(session) != AS_OK) {
        fail(r, "drain.eos", "begin_drain failed");
        as_session_close_v0(&session);
        return;
    }
    uint32_t calls = 0;
    as_status_v0 status = AS_OK;
    while (calls < 64u) {
        status = drain_frame(session, &call);
        ++calls;
        if (status != AS_OK) break;
    }
    if (status != AS_END_OF_STREAM) {
        fail(r, "drain.eos", "first drain ended with %s after %u calls",
             as_status_name_v0(status), calls);
        as_session_close_v0(&session);
        return;
    }
    if (calls > info->max_drain_calls) {
        fail(r, "drain.eos", "%u drain calls exceed declared bound %u", calls,
             info->max_drain_calls);
        as_session_close_v0(&session);
        return;
    }
    for (int repeat = 0; repeat < 2; ++repeat) {
        const as_status_v0 again = drain_frame(session, &call);
        if (again != AS_END_OF_STREAM) {
            fail(r, "drain.eos", "repeated drain returned %s",
                 as_status_name_v0(again));
            as_session_close_v0(&session);
            return;
        }
    }
    if (process_frame(session, input, FRAME_SAMPLES, 0, 31, FRAME_SAMPLES,
                      &call) != AS_INVALID_ARGUMENT) {
        fail(r, "drain.eos", "process after drain was not rejected");
        as_session_close_v0(&session);
        return;
    }
    pass(r, "drain.eos", "stable end-of-stream after %u calls", calls);
    as_session_close_v0(&session);
}

static void check_reset(as_registry_v0 *registry, reporter *r,
                        const char *provider_id,
                        uint32_t provider_id_length,
                        const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    if (create_session(registry, provider_id, provider_id_length,
                       AS_MODE_PROCESSING_THREAD, 41, 0, &session, error,
                       sizeof(error)) != AS_OK) {
        fail(r, "reset.epoch", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    input[3] = 0.5f;
    frame_call call;
    if (process_frame(session, input, FRAME_SAMPLES, 0, 41, 0, &call) != AS_OK) {
        fail(r, "reset.epoch", "initial process failed");
        as_session_close_v0(&session);
        return;
    }
    as_error_v0 as_error;
    as_error_v0_init(&as_error);
    const as_status_v0 stale =
        as_session_reset_v0(session, 41, 0, &as_error);
    if (stale != AS_INVALID_ARGUMENT) {
        fail(r, "reset.epoch", "non-increasing epoch returned %s",
             as_status_name_v0(stale));
    } else {
        pass(r, "reset.epoch", "non-increasing epoch rejected");
    }
    as_error_v0_init(&as_error);
    if (as_session_reset_v0(session, 42, 123456, &as_error) != AS_OK) {
        fail(r, "reset.epoch", "reset to epoch 42 failed: %s",
             as_error.message);
        as_session_close_v0(&session);
        return;
    }
    const as_status_v0 status =
        process_frame(session, input, FRAME_SAMPLES, 0, 42, 123456, &call);
    const int64_t expected =
        123456 - (int64_t)info->buffering_delay;
    if (status != AS_OK || call.result.epoch != 42 ||
        call.result.source_first_sample != expected) {
        fail(r, "reset.epoch", "post-reset metadata mismatch (status %s)",
             as_status_name_v0(status));
    } else {
        pass(r, "reset.epoch", "epoch 42 at sample 123456");
    }
    as_session_close_v0(&session);
}

static void check_invalid_process(as_registry_v0 *registry, reporter *r,
                                  const char *provider_id,
                                  uint32_t provider_id_length,
                                  const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    if (create_session(registry, provider_id, provider_id_length,
                       AS_MODE_PROCESSING_THREAD, 51, 0, &session, error,
                       sizeof(error)) != AS_OK) {
        fail(r, "args.invalid", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    float output[FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    memset(output, 0, sizeof(output));
    int failures = 0;
    char detail[512];
    detail[0] = '\0';
    size_t detail_length = 0;
    int cases = 0;

#define EXPECT_INVALID(name, statement)                                        \
    do {                                                                       \
        ++cases;                                                               \
        const as_status_v0 actual = (statement);                               \
        if (actual != AS_INVALID_ARGUMENT) {                                   \
            ++failures;                                                        \
            if (detail_length < sizeof(detail) - 64u) {                        \
                detail_length += (size_t)snprintf(                             \
                    detail + detail_length, sizeof(detail) - detail_length,    \
                    "%s:%s; ", name, as_status_name_v0(actual));               \
            }                                                                  \
        }                                                                      \
    } while (0)

    as_frame_v0 frame;
    as_output_v0 out;
    as_result_v0 result;

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    out.capacity = FRAME_SAMPLES - 1u;
    EXPECT_INVALID("output_capacity",
                   as_session_process_v0(session, &frame, &out, &result));

    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    frame.input_count = FRAME_SAMPLES - 1u;
    EXPECT_INVALID("input_count",
                   as_session_process_v0(session, &frame, &out, &result));

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 52;
    frame.first_input_sample = 0;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    EXPECT_INVALID("stale_epoch",
                   as_session_process_v0(session, &frame, &out, &result));

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 5;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    EXPECT_INVALID("wrong_position",
                   as_session_process_v0(session, &frame, &out, &result));

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    frame.input_valid_count = 100u;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    EXPECT_INVALID("partial_without_flag",
                   as_session_process_v0(session, &frame, &out, &result));

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    frame.flags = 8u;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    EXPECT_INVALID("unknown_flag",
                   as_session_process_v0(session, &frame, &out, &result));

    {
        float bad[FRAME_SAMPLES];
        memcpy(bad, input, sizeof(bad));
        bad[7] = NAN;
        as_frame_v0_init(&frame);
        frame.input = bad;
        frame.epoch = 51;
        frame.first_input_sample = 0;
        as_output_v0_init(&out);
        out.samples = output;
        as_result_v0_init(&result);
        EXPECT_INVALID("nan_input",
                       as_session_process_v0(session, &frame, &out, &result));
    }

    {
        float final_input[FRAME_SAMPLES];
        memset(final_input, 0, sizeof(final_input));
        final_input[FRAME_SAMPLES - 1u] = 1.0f;
        as_frame_v0_init(&frame);
        frame.input = final_input;
        frame.epoch = 51;
        frame.first_input_sample = 0;
        frame.input_valid_count = 10u;
        frame.flags = AS_FRAME_FINAL_INPUT;
        as_output_v0_init(&out);
        out.samples = output;
        as_result_v0_init(&result);
        EXPECT_INVALID("final_padding",
                       as_session_process_v0(session, &frame, &out, &result));
    }

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    as_output_v0_init(&out);
    out.samples = input;
    as_result_v0_init(&result);
    EXPECT_INVALID("overlap",
                   as_session_process_v0(session, &frame, &out, &result));

    {
        unsigned char storage[FRAME_SAMPLES * sizeof(float) + 4u];
        const uintptr_t address = (uintptr_t)storage;
        const uintptr_t aligned_address =
            (address + sizeof(float) - 1u) & ~(uintptr_t)(sizeof(float) - 1u);
        float *misaligned = (float *)(void *)(aligned_address + 1u);
        as_output_v0_init(&out);
        out.samples = misaligned;
        as_result_v0_init(&result);
        as_frame_v0_init(&frame);
        frame.input = input;
        frame.epoch = 51;
        frame.first_input_sample = 0;
        EXPECT_INVALID("misaligned",
                       as_session_process_v0(session, &frame, &out, &result));
    }

    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    result.struct_size = 8u;
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    EXPECT_INVALID("short_result",
                   as_session_process_v0(session, &frame, &out, &result));

    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    EXPECT_INVALID("drain_before_begin",
                   as_session_drain_next_v0(session, &out, &result));

    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    as_result_v0_init(&result);
    ++cases;
    if (as_session_submit_v0(session, &frame, &result) == AS_UNSUPPORTED) {
        /* expected: this session was created in mode 2 */
    } else {
        ++failures;
        (void)snprintf(detail + detail_length, sizeof(detail) - detail_length,
                       "submit_inline:unexpected status; ");
        detail_length = strlen(detail);
    }
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    ++cases;
    if (as_session_pull_v0(session, &out, &result) != AS_UNSUPPORTED) {
        ++failures;
        (void)snprintf(detail + detail_length, sizeof(detail) - detail_length,
                       "pull_inline:unexpected status; ");
        detail_length = strlen(detail);
    }

    as_error_v0 as_error;
    as_error_v0_init(&as_error);
    EXPECT_INVALID("reset_epoch",
                   as_session_reset_v0(session, 51, 0, &as_error));
    as_error_v0_init(&as_error);
    EXPECT_INVALID("reset_position",
                   as_session_reset_v0(session, 52, -1, &as_error));

    /* The session must remain usable after rejected calls. */
    as_frame_v0_init(&frame);
    frame.input = input;
    frame.epoch = 51;
    frame.first_input_sample = 0;
    as_output_v0_init(&out);
    out.samples = output;
    as_result_v0_init(&result);
    const as_status_v0 valid =
        as_session_process_v0(session, &frame, &out, &result);
    if (valid != AS_OK) {
        ++failures;
        if (detail_length < sizeof(detail) - 64u) {
            detail_length += (size_t)snprintf(
                detail + detail_length, sizeof(detail) - detail_length,
                "post_valid:%s; ", as_status_name_v0(valid));
        }
    }

    {
        float final_input[FRAME_SAMPLES] = {0};
        as_frame_v0_init(&frame);
        frame.input = final_input;
        frame.input_valid_count = 1;
        frame.flags = AS_FRAME_FINAL_INPUT;
        frame.epoch = 51;
        frame.first_input_sample = FRAME_SAMPLES;
        as_output_v0_init(&out);
        out.samples = output;
        as_result_v0_init(&result);
        const as_status_v0 final_status =
            as_session_process_v0(session, &frame, &out, &result);
        if (final_status != AS_OK) {
            ++failures;
            if (detail_length < sizeof(detail) - 64u) {
                detail_length += (size_t)snprintf(
                    detail + detail_length, sizeof(detail) - detail_length,
                    "final_input:%s; ", as_status_name_v0(final_status));
            }
        } else {
            frame.first_input_sample = 2 * FRAME_SAMPLES;
            as_result_v0_init(&result);
            const as_status_v0 after_final =
                as_session_process_v0(session, &frame, &out, &result);
            if (after_final != AS_INVALID_ARGUMENT) {
                ++failures;
                if (detail_length < sizeof(detail) - 64u) {
                    detail_length += (size_t)snprintf(
                        detail + detail_length,
                        sizeof(detail) - detail_length,
                        "after_final:%s; ",
                        as_status_name_v0(after_final));
                }
            }
        }
    }

    if (failures == 0) {
        pass(r, "args.invalid", "%d invalid calls rejected", cases);
    } else {
        fail(r, "args.invalid", "%d/%d: %s", failures, cases + 1, detail);
    }
    (void)info;
    as_session_close_v0(&session);
#undef EXPECT_INVALID
}

static int contains(const char *text, const char *needle) {
    return strstr(text, needle) != NULL;
}

static void check_json_queries(as_registry_v0 *registry, reporter *r,
                               const char *provider_id,
                               uint32_t provider_id_length,
                               const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    if (create_session(registry, provider_id, provider_id_length,
                       AS_MODE_PROCESSING_THREAD, 61, 0, &session, error,
                       sizeof(error)) != AS_OK) {
        fail(r, "info.json", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    input[0] = 0.25f;
    frame_call call;
    if (process_frame(session, input, FRAME_SAMPLES, 0, 61, 0, &call) != AS_OK) {
        fail(r, "info.json", "process failed");
        as_session_close_v0(&session);
        return;
    }

    uint32_t required = 0;
    as_status_v0 status = as_session_get_info_v0(session, NULL, 0, &required);
    char *info_json = (char *)malloc(required == 0 ? 1u : required);
    if (status != AS_OK || info_json == NULL || required < 2u) {
        fail(r, "info.json", "size query failed (%s, %u)",
             as_status_name_v0(status), required);
        free(info_json);
        as_session_close_v0(&session);
        return;
    }
    char one = 0;
    if (as_session_get_info_v0(session, &one, 1u, &required) !=
            AS_RESOURCE_EXHAUSTED) {
        fail(r, "info.json", "one-byte buffer was not rejected");
    }
    status = as_session_get_info_v0(session, info_json, required, &required);
    const int info_ok =
        status == AS_OK && info_json[required - 1u] == '\0' &&
        info_json[0] == '{' && info_json[required - 2u] == '}' &&
        contains(info_json, "\"schema_id\":\"audio-sdk/session-info/0.1\"") &&
        contains(info_json, "\"provider_id\":\"") &&
        contains(info_json, "\"descriptor_digest\":\"") &&
        contains(info_json, "\"buffering_delay_samples\":") &&
        contains(info_json, "\"native_hop_samples\":") &&
        contains(info_json, "\"execution_mode\":2") &&
        contains(info_json, "\"lifecycle\":\"processing\"");
    if (info_ok) {
        pass(r, "info.json", "%u bytes, mandatory fields present", required);
    } else {
        fail(r, "info.json", "response is missing mandatory fields");
    }
    free(info_json);

    uint32_t stats_required = 0;
    status = as_session_get_stats_v0(session, NULL, 0, &stats_required);
    char *stats_json =
        (char *)malloc(stats_required == 0 ? 1u : stats_required);
    if (status != AS_OK || stats_json == NULL || stats_required < 2u) {
        fail(r, "stats.json", "size query failed (%s, %u)",
             as_status_name_v0(status), stats_required);
        free(stats_json);
        as_session_close_v0(&session);
        return;
    }
    status = as_session_get_stats_v0(session, stats_json, stats_required,
                                     &stats_required);
    const int stats_ok =
        status == AS_OK && stats_json[stats_required - 1u] == '\0' &&
        stats_json[0] == '{' && stats_json[stats_required - 2u] == '}' &&
        contains(stats_json, "\"schema_id\":\"audio-sdk/session-stats/0.1\"") &&
        contains(stats_json, "\"epoch\":\"61\"") &&
        contains(stats_json, "\"submitted_valid_samples\"") &&
        contains(stats_json, "\"accepted_valid_samples\"") &&
        contains(stats_json, "\"produced_valid_samples\"") &&
        contains(stats_json, "\"delivered_valid_samples\"") &&
        contains(stats_json, "\"input_queue_capacity\"") == 0 &&
        contains(stats_json, "\"backend_failures\":") &&
        contains(stats_json, "\"input_queue_depth\":") &&
        contains(stats_json, "\"output_queue_depth\":");
    if (stats_ok) {
        pass(r, "stats.json", "%u bytes, counters present", stats_required);
    } else {
        fail(r, "stats.json", "response is missing mandatory counters");
    }
    free(stats_json);
    (void)info;
    as_session_close_v0(&session);
}

static void check_determinism(as_registry_v0 *registry, reporter *r,
                              const char *provider_id,
                              uint32_t provider_id_length,
                              const session_info *info) {
    enum { FRAMES = 8u };
    float fixture[FRAMES * FRAME_SAMPLES];
    g_rng_state = FIXTURE_SEED;
    make_fixture(fixture, FRAMES * FRAME_SAMPLES);
    const uint32_t source_capacity =
        info->buffering_delay + FRAMES * FRAME_SAMPLES + 160u;
    char first_hash[65];
    char second_hash[65];
    for (int run = 0; run < 2; ++run) {
        const uint32_t raw_capacity_frames =
            FRAMES + info->max_drain_calls + 2u;
        float *raw = (float *)malloc(
            (size_t)raw_capacity_frames * FRAME_SAMPLES * sizeof(float));
        if (raw == NULL) {
            fail(r, "determinism.output", "allocation failed");
            return;
        }
        char error[256];
        as_session_v0 *session = NULL;
        if (create_session(registry, provider_id, provider_id_length,
                           AS_MODE_PROCESSING_THREAD, 71, 0, &session, error,
                           sizeof(error)) != AS_OK) {
            free(raw);
            fail(r, "determinism.output", "create failed: %s", error);
            return;
        }
        collector c;
        collector_init(&c, -(int64_t)info->buffering_delay, source_capacity, raw,
                        raw_capacity_frames * FRAME_SAMPLES);
        const int ok = run_stream(session, fixture, FRAMES * FRAME_SAMPLES, 71, 0,
                                  info->buffering_delay, AS_MODE_PROCESSING_THREAD, &c,
                                  error, sizeof(error));
        as_session_close_v0(&session);
        if (!ok) {
            free(raw);
            fail(r, "determinism.output", "run %d failed: %s", run, error);
            return;
        }
        char *hash = run == 0 ? first_hash : second_hash;
        as_sha256_hex_v0(raw, c.raw_length * (uint32_t)sizeof(float), hash,
                         65u);
        free(raw);
    }
    if (memcmp(first_hash, second_hash, 65) == 0) {
        pass(r, "determinism.output", "%s", first_hash);
    } else {
        fail(r, "determinism.output", "%s != %s", first_hash, second_hash);
    }
}

static void check_buffered(as_registry_v0 *registry, reporter *r,
                           const char *provider_id,
                           uint32_t provider_id_length,
                           const session_info *info) {
    char error[256];
    as_session_v0 *session = NULL;
    if (create_session(registry, provider_id, provider_id_length,
                       AS_MODE_BUFFERED_WORKER, 81, 0, &session, error,
                       sizeof(error)) != AS_OK) {
        fail(r, "buffered.flow", "create failed: %s", error);
        return;
    }
    float input[FRAME_SAMPLES];
    memset(input, 0, sizeof(input));
    input[0] = 0.1f;
    uint32_t accepted = 0;
    for (uint32_t i = 0; i < 3u; ++i) {
        as_frame_v0 frame;
        as_frame_v0_init(&frame);
        frame.input = input;
        frame.epoch = 81;
        frame.first_input_sample = (int64_t)i * FRAME_SAMPLES;
        as_result_v0 acceptance;
        as_result_v0_init(&acceptance);
        const as_status_v0 status =
            as_session_submit_v0(session, &frame, &acceptance);
        if (status == AS_OK) {
            ++accepted;
        } else {
            fail(r, "buffered.flow", "submit %u returned %s", i,
                 as_status_name_v0(status));
            as_session_close_v0(&session);
            return;
        }
    }
    uint32_t delivered_frames = 0;
    uint32_t pulls = 0;
    uint64_t valid = 0;
    uint32_t guard = 0;
    while (pulls < accepted && guard < 2000u) {
        float output[FRAME_SAMPLES];
        as_output_v0 out;
        as_output_v0_init(&out);
        out.samples = output;
        as_result_v0 result;
        as_result_v0_init(&result);
        const as_status_v0 status = as_session_pull_v0(session, &out, &result);
        ++guard;
        if (status == AS_NOT_READY) {
            const struct timespec pause = {0, 1000000L};
            nanosleep(&pause, NULL);
            continue;
        }
        if (status != AS_OK) {
            fail(r, "buffered.flow", "pull returned %s",
                 as_status_name_v0(status));
            as_session_close_v0(&session);
            return;
        }
        ++pulls;
        valid += result.valid_count;
        ++delivered_frames;
    }
    if (as_session_begin_drain_v0(session) != AS_OK) {
        fail(r, "buffered.flow", "begin_drain failed");
        as_session_close_v0(&session);
        return;
    }
    guard = 0;
    int ended = 0;
    while (guard < 4000u) {
        float output[FRAME_SAMPLES];
        as_output_v0 out;
        as_output_v0_init(&out);
        out.samples = output;
        as_result_v0 result;
        as_result_v0_init(&result);
        const as_status_v0 status = as_session_pull_v0(session, &out, &result);
        ++guard;
        if (status == AS_NOT_READY) {
            const struct timespec pause = {0, 1000000L};
            nanosleep(&pause, NULL);
            continue;
        }
        if (status == AS_END_OF_STREAM) {
            ended = 1;
            break;
        }
        if (status != AS_OK) {
            fail(r, "buffered.flow", "drain pull returned %s",
                 as_status_name_v0(status));
            as_session_close_v0(&session);
            return;
        }
        valid += result.valid_count;
    }
    uint32_t required = 0;
    char stats[4096];
    (void)as_session_get_stats_v0(session, stats, (uint32_t)sizeof(stats),
                                  &required);
    if (!ended || pulls != accepted || delivered_frames != accepted) {
        fail(r, "buffered.flow", "ended=%d pulls=%u/%u delivered=%u",
             ended, pulls, accepted, delivered_frames);
    } else if (!contains(stats, "\"input_queue_high_water\":\"") ||
               !contains(stats, "\"output_queue_high_water\":\"")) {
        fail(r, "buffered.flow", "queue high-water counters are missing");
    } else {
        pass(r, "buffered.flow",
             "accepted=%u pushed=%u valid=%llu bounded queues", accepted,
             pulls, (unsigned long long)valid);
    }
    (void)info;
    as_session_close_v0(&session);
}

static as_status_v0 dummy_create(const as_create_config_v0 *config,
                                 void **out_instance, as_error_v0 *error) {
    (void)config;
    (void)error;
    *out_instance = NULL;
    return AS_BACKEND_FAILURE;
}
static as_status_v0 dummy_process(void *instance, const as_frame_v0 *frame,
                                  const as_output_v0 *output,
                                  as_result_v0 *result) {
    (void)instance;
    (void)frame;
    (void)output;
    (void)result;
    return AS_BACKEND_FAILURE;
}
static as_status_v0 dummy_reset(void *instance, uint64_t epoch,
                                int64_t first, as_error_v0 *error) {
    (void)instance;
    (void)epoch;
    (void)first;
    (void)error;
    return AS_OK;
}
static as_status_v0 dummy_drain(void *instance, const as_output_v0 *output,
                                as_result_v0 *result) {
    (void)instance;
    (void)output;
    (void)result;
    return AS_END_OF_STREAM;
}
static void dummy_destroy(void *instance) { (void)instance; }

static void fill_dummy_table(as_provider_table_v0 *table) {
    as_provider_table_v0_init(table);
    table->create = dummy_create;
    table->process = dummy_process;
    table->reset = dummy_reset;
    table->drain = dummy_drain;
    table->destroy = dummy_destroy;
}

static void check_registry(as_registry_v0 *registry, reporter *r,
                           const char *provider_id,
                           uint32_t provider_id_length) {
    static const char invalid_id[] = "Invalid.Provider";
    if (as_query_provider_v0(registry, invalid_id,
                             (uint32_t)sizeof(invalid_id) - 1u, NULL, 0,
                             NULL) != AS_INVALID_ARGUMENT) {
        fail(r, "registry.ids", "uppercase provider ID was accepted");
    } else {
        pass(r, "registry.ids", "invalid provider ID rejected");
    }

    const char missing[] = "no.such.provider.v0";
    if (as_query_provider_v0(registry, missing,
                             (uint32_t)sizeof(missing) - 1u, NULL, 0,
                             NULL) != AS_UNSUPPORTED) {
        fail(r, "registry.missing", "unknown provider lookup was not rejected");
    } else {
        pass(r, "registry.missing", "unknown provider returns unsupported");
    }

    /* Duplicate registration uses the provider's own canonical descriptor
     * with a structurally valid but non-executing table. */
    static const char duplicate_id[] = "speex.ns.v0";
    uint32_t required = 0;
    if (as_query_provider_v0(registry, duplicate_id,
                             (uint32_t)sizeof(duplicate_id) - 1u, NULL,
                             0, &required) != AS_OK ||
        required < 2u) {
        fail(r, "registry.duplicate", "descriptor size query failed");
        return;
    }
    char *descriptor = (char *)malloc(required);
    if (descriptor == NULL) {
        fail(r, "registry.duplicate", "allocation failed");
        return;
    }
    if (as_query_provider_v0(registry, duplicate_id,
                             (uint32_t)sizeof(duplicate_id) - 1u,
                             descriptor, required, &required) != AS_OK) {
        free(descriptor);
        fail(r, "registry.duplicate", "descriptor query failed");
        return;
    }
    as_registry_v0 *second = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&second, &error) != AS_OK) {
        free(descriptor);
        fail(r, "registry.duplicate", "second registry create failed");
        return;
    }
    as_provider_table_v0 table;
    fill_dummy_table(&table);
    const as_status_v0 duplicate = as_register_provider_v0(
        second, &table, descriptor, required - 1u, &error);
    if (duplicate != AS_DUPLICATE) {
        fail(r, "registry.duplicate", "duplicate returned %s",
             as_status_name_v0(duplicate));
    } else {
        pass(r, "registry.duplicate", "duplicate ID rejected");
    }

    as_provider_table_v0 bad;
    fill_dummy_table(&bad);
    bad.create = NULL;
    as_error_v0_init(&error);
    char modified[4096];
    if (required <= sizeof(modified)) {
        memcpy(modified, descriptor, required);
        char *id = strstr(modified, "\"provider_id\":\"");
        if (id != NULL) {
            id += strlen("\"provider_id\":\"");
            id[0] = id[0] == 'a' ? 'b' : 'a';
        }
        if (as_register_provider_v0(second, &bad, modified, required - 1u,
                                    &error) != AS_INVALID_ARGUMENT) {
            fail(r, "registry.table", "null operation table was accepted");
        } else {
            pass(r, "registry.table", "incomplete provider table rejected");
        }
    } else {
        skip(r, "registry.table", "descriptor too large for the test buffer");
    }

    as_registry_v0 *third = NULL;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&third, &error) != AS_OK) {
        fail(r, "registry.close", "third registry create failed");
    } else if (as_registry_close_v0(&third) != AS_OK || third != NULL) {
        fail(r, "registry.close", "empty registry did not close");
    } else {
        pass(r, "registry.close", "empty registry closes normally");
    }
    as_registry_close_v0(&second);
    free(descriptor);

    /* BUSY: a live session prevents registry close. Only possible when the
     * provider is one of the registry's installed built-ins. */
    if (strcmp(provider_id, "speex.ns.v0") == 0 ||
        strcmp(provider_id, "dsp.highpass80.v0") == 0) {
        as_registry_v0 *busy = NULL;
        as_error_v0_init(&error);
        if (as_registry_create_v0(&busy, &error) != AS_OK) {
            fail(r, "registry.busy", "registry create failed");
            return;
        }
        char create_error[256];
        as_session_v0 *session = NULL;
        if (create_session(busy, provider_id, provider_id_length,
                           AS_MODE_PROCESSING_THREAD, 91, 0, &session,
                           create_error, sizeof(create_error)) != AS_OK) {
            fail(r, "registry.busy", "session create failed: %s",
                 create_error);
            as_registry_close_v0(&busy);
            return;
        }
        if (as_registry_close_v0(&busy) != AS_BUSY) {
            fail(r, "registry.busy", "close with a live session was allowed");
        } else {
            pass(r, "registry.busy", "close with live session returns busy");
        }
        as_session_close_v0(&session);
        if (as_registry_close_v0(&busy) != AS_OK) {
            fail(r, "registry.busy", "close after session release failed");
        }
    } else {
        skip(r, "registry.busy",
             "external providers are not installed in a second registry");
    }
}

static void check_invalid_assets(as_registry_v0 *registry, reporter *r,
                                 const char *provider_id,
                                 uint32_t provider_id_length) {
    char config[4096];
    uint32_t required = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_effective_config_create_v0(registry, provider_id,
                                      provider_id_length,
                                      AS_MODE_PROCESSING_THREAD, config,
                                      (uint32_t)sizeof(config), &required,
                                      &error) != AS_OK) {
        fail(r, "create.reject.assets", "configuration generation failed");
        return;
    }
    uint8_t payload[4] = {1u, 2u, 3u, 4u};
    as_asset_v0 asset;
    as_asset_v0_init(&asset);
    asset.asset_id = "blob";
    asset.asset_id_length = 4;
    asset.data = payload;
    asset.byte_count = sizeof(payload);
    memset(asset.sha256, 0xaa, sizeof(asset.sha256));
    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = 1;
    create.config_json = config;
    create.config_json_length = required - 1u;
    create.assets = &asset;
    create.asset_count = 1;
    as_session_v0 *session = NULL;
    as_error_v0_init(&error);
    const as_status_v0 status = as_session_create_v0(
        registry, provider_id, provider_id_length, &create, &session, &error);
    if (status == AS_INVALID_ARGUMENT) {
        pass(r, "create.reject.assets", "asset digest mismatch rejected");
    } else {
        fail(r, "create.reject.assets", "returned %s",
             as_status_name_v0(status));
    }
}

/* ------------------------------------------------------------------ */
/* entry point                                                        */
/* ------------------------------------------------------------------ */

int as_run_conformance(as_registry_v0 *registry, const char *provider_id,
                       uint32_t provider_id_length, const char *report_path,
                       char *error, uint32_t error_capacity) {
    if (error != NULL && error_capacity > 0) error[0] = '\0';
    if (registry == NULL || !as_valid_provider_id_v0(provider_id,
                                                     provider_id_length)) {
        set_error(error, error_capacity, "registry or provider ID is invalid");
        return 2;
    }
    char dummy[8];
    uint32_t required = 0;
    const as_status_v0 found = as_query_provider_v0(
        registry, provider_id, provider_id_length, dummy,
        (uint32_t)sizeof(dummy), &required);
    if (found == AS_UNSUPPORTED) {
        set_error(error, error_capacity, "provider is not registered");
        return 2;
    }
    if (required < 2u || required > 65536u) {
        set_error(error, error_capacity, "descriptor size is invalid");
        return 2;
    }
    char *descriptor = (char *)malloc(required);
    if (descriptor == NULL) {
        set_error(error, error_capacity, "descriptor allocation failed");
        return 2;
    }
    if (as_query_provider_v0(registry, provider_id, provider_id_length,
                             descriptor, required, &required) != AS_OK) {
        free(descriptor);
        set_error(error, error_capacity, "descriptor query failed");
        return 2;
    }

    reporter r;
    memset(&r, 0, sizeof(r));
    r.first = 1;
    if (report_path != NULL) {
        r.file = fopen(report_path, "w");
        if (r.file == NULL) {
            free(descriptor);
            set_error(error, error_capacity, "cannot open report path %s",
                      report_path);
            return 2;
        }
        fputs("{\"schema_id\":\"audio-sdk/conformance/0.1\","
              "\"provider_id\":\"",
              r.file);
        json_escape(r.file, provider_id);
        fputs("\",\"contract_version\":\"", r.file);
        fputs(as_contract_version_v0(), r.file);
        fputs("\",\"build_id\":\"", r.file);
        json_escape(r.file, as_build_id_v0());
        fputs("\",\"descriptor_digest\":\"", r.file);
        char digest[65];
        as_sha256_hex_v0(descriptor, required - 1u, digest,
                         (uint32_t)sizeof(digest));
        fputs(digest, r.file);
        fputs("\",\"checks\":[", r.file);
    }

    session_info info;
    memset(&info, 0, sizeof(info));
    printf("provider %s\n", provider_id);
    printf("contract %s build %s\n", as_contract_version_v0(),
           as_build_id_v0());

    if (!check_descriptor(registry, &r, provider_id, provider_id_length,
                          descriptor, required, &info, error,
                          error_capacity)) {
        if (r.file != NULL) {
            fputs("],\"summary\":{\"pass\":", r.file);
            fprintf(r.file, "%d,\"fail\":%d,\"skip\":%d},\"result\":\"fail\"}\n",
                    r.passed, r.failed, r.skipped);
            fclose(r.file);
        }
        free(descriptor);
        return 1;
    }

    check_create_modes(registry, &r, provider_id, provider_id_length,
                       descriptor, &info);
    check_invalid_create(registry, &r, provider_id, provider_id_length,
                         descriptor, &info);
    check_process_metadata(registry, &r, provider_id, provider_id_length,
                           &info);
    check_timing(registry, &r, provider_id, provider_id_length, &info,
                 AS_MODE_PROCESSING_THREAD);
    check_boundaries(registry, &r, provider_id, provider_id_length, &info,
                     AS_MODE_PROCESSING_THREAD);
    check_eos_repeat(registry, &r, provider_id, provider_id_length, &info);
    check_reset(registry, &r, provider_id, provider_id_length, &info);
    check_invalid_process(registry, &r, provider_id, provider_id_length,
                          &info);
    check_json_queries(registry, &r, provider_id, provider_id_length, &info);
    check_determinism(registry, &r, provider_id, provider_id_length, &info);
    check_invalid_assets(registry, &r, provider_id, provider_id_length);
    check_registry(registry, &r, provider_id, provider_id_length);
    if (modes_contain(descriptor, AS_MODE_BUFFERED_WORKER)) {
        check_buffered(registry, &r, provider_id, provider_id_length, &info);
        check_timing(registry, &r, provider_id, provider_id_length, &info,
                     AS_MODE_BUFFERED_WORKER);
        check_boundaries(registry, &r, provider_id, provider_id_length, &info,
                         AS_MODE_BUFFERED_WORKER);
    } else {
        skip(&r, "buffered.flow", "mode 3 is not declared");
    }

    printf("summary pass=%d fail=%d skip=%d\n", r.passed, r.failed,
           r.skipped);
    if (r.file != NULL) {
        fputs("],\"summary\":{\"pass\":", r.file);
        fprintf(r.file, "%d,\"fail\":%d,\"skip\":%d},\"result\":\"%s\"}\n",
                r.passed, r.failed, r.skipped,
                r.failed == 0 && r.passed > 0 ? "pass" : "fail");
        fclose(r.file);
    }
    free(descriptor);
    if (r.failed != 0) {
        set_error(error, error_capacity, "%d conformance checks failed",
                  r.failed);
        return 1;
    }
    return 0;
}
