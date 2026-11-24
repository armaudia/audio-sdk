/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Task-local synthetic C11 harness for the pinned v0 C ABI.
 *
 * This is compile/runtime evidence for the documented RAII ownership model.
 * It adds no provider, descriptor, registry entry, default or installed
 * artifact. All PCM and control storage is caller-owned stack memory.
 */
#include "audio_sdk/session_v0.h"
#include "raii_model.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define AS_RAII_MAX_EVENTS 12u
#define AS_RAII_EVENT_LEN 80u
#define AS_RAII_LINE_LEN 1024u
#define AS_RAII_EFFECTIVE_BYTES 4096u
#define AS_RAII_SEED 20261124u
#define AS_RAII_DENOMINATOR 8192u

enum mutation_id {
    M_NONE = 0,
    M_ASSETS_NULL,
    M_PARTIAL_FINAL,
    M_ABI_MAJOR,
    M_INPUT_COUNT,
    M_PARTIAL_NO_FINAL,
    M_NONFINITE,
    M_OUTPUT_NULL,
    M_PROVIDER_EMPTY,
    M_CONFIG_NULL,
    M_UNKNOWN_PROVIDER
};

typedef struct {
    const char *case_id;
    const char *kind;
    const char *mutation;
    int mutation_id;
} case_spec;

static const case_spec SPECS[] = {
    {"valid_full_frame", "valid", "none", M_NONE},
    {"assets_omitted", "missing_optional", "assets_null_count_zero", M_ASSETS_NULL},
    {"partial_final_frame", "valid", "valid_count_80_final", M_PARTIAL_FINAL},
    {"malformed_struct_tag", "malformed", "abi_major_1", M_ABI_MAJOR},
    {"wrong_input_count", "malformed", "input_count_159", M_INPUT_COUNT},
    {"partial_without_final", "malformed", "valid_count_80_no_final", M_PARTIAL_NO_FINAL},
    {"nonfinite_input", "nonfinite", "sample_20_nan", M_NONFINITE},
    {"missing_output_buffer", "missing_optional", "output_samples_null", M_OUTPUT_NULL},
    {"missing_provider_selection", "missing_optional", "provider_id_empty", M_PROVIDER_EMPTY},
    {"missing_config_json", "missing_optional", "config_json_null", M_CONFIG_NULL},
    {"unknown_provider", "invalid", "unknown_provider_id", M_UNKNOWN_PROVIDER}
};

typedef struct {
    char items[AS_RAII_MAX_EVENTS][AS_RAII_EVENT_LEN];
    size_t count;
} events_t;

typedef struct {
    const char *case_id;
    const char *kind;
    const char *mutation;
    const char *create_status;
    const char *process_status;
    uint64_t input_digest;
    events_t events;
    int has_result;
    as_result_v0 result;
} case_trace;

static const char *status_name(as_status_v0 status) {
    switch (status) {
    case AS_OK: return "OK";
    case AS_INVALID_ARGUMENT: return "INVALID_ARGUMENT";
    case AS_UNSUPPORTED: return "UNSUPPORTED";
    case AS_RESOURCE_EXHAUSTED: return "RESOURCE_EXHAUSTED";
    case AS_BACKEND_FAILURE: return "BACKEND_FAILURE";
    case AS_NEEDS_RESET: return "NEEDS_RESET";
    case AS_NOT_READY: return "NOT_READY";
    case AS_END_OF_STREAM: return "END_OF_STREAM";
    case AS_BUSY: return "BUSY";
    case AS_CLOSED: return "CLOSED";
    case AS_DUPLICATE: return "DUPLICATE";
    default: return "UNKNOWN_STATUS";
    }
}

static void add_event(events_t *events, const char *name, as_status_v0 status) {
    if (events->count >= AS_RAII_MAX_EVENTS) {
        return;
    }
    snprintf(events->items[events->count], AS_RAII_EVENT_LEN, "%s:%s",
             name, status_name(status));
    events->count += 1u;
}

static uint64_t generated_input_digest(void) {
    uint32_t state = AS_RAII_SEED;
    uint64_t value = UINT64_C(0xcbf29ce484222325);
    unsigned int index;
    for (index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        int coefficient;
        float sample;
        uint32_t bits;
        unsigned char bytes[4];
        size_t byte_index;
        state = (uint32_t)((uint64_t)1103515245u * state + 12345u) & UINT32_C(0x7fffffff);
        coefficient = (int)(state % (2u * AS_RAII_DENOMINATOR)) - (int)AS_RAII_DENOMINATOR;
        sample = (float)coefficient / (float)AS_RAII_DENOMINATOR;
        memcpy(&bits, &sample, sizeof(bits));
        memcpy(bytes, &bits, sizeof(bytes));
        for (byte_index = 0u; byte_index < sizeof(bytes); ++byte_index) {
            value ^= (uint64_t)bytes[byte_index];
            value *= UINT64_C(0x100000001b3);
        }
    }
    return value;
}

static void fill_input(float input[AS_FRAME_SAMPLES]) {
    uint32_t state = AS_RAII_SEED;
    unsigned int index;
    for (index = 0u; index < AS_FRAME_SAMPLES; ++index) {
        state = (uint32_t)((uint64_t)1103515245u * state + 12345u) & UINT32_C(0x7fffffff);
        input[index] = (float)((int)(state % (2u * AS_RAII_DENOMINATOR)) -
                               (int)AS_RAII_DENOMINATOR) / (float)AS_RAII_DENOMINATOR;
    }
}

static uint64_t observed_model_digest(const case_trace *traces, size_t count) {
    uint64_t value = UINT64_C(0xcbf29ce484222325);
    size_t trace_index;
    for (trace_index = 0u; trace_index < count; ++trace_index) {
        char events_text[AS_RAII_LINE_LEN];
        char line[AS_RAII_LINE_LEN];
        char digest_text[17];
        size_t offset = 0u;
        size_t event_index;
        size_t byte_index;
        events_text[0] = '\0';
        for (event_index = 0u; event_index < traces[trace_index].events.count; ++event_index) {
            int written;
            if (offset >= sizeof(events_text)) {
                break;
            }
            written = snprintf(events_text + offset, sizeof(events_text) - offset, "%s%s",
                               event_index == 0u ? "" : ",",
                               traces[trace_index].events.items[event_index]);
            if (written <= 0) {
                break;
            }
            offset += (size_t)written;
            if (offset >= sizeof(events_text)) {
                offset = sizeof(events_text) - 1u;
            }
        }
        snprintf(digest_text, sizeof(digest_text), "%016llx",
                 (unsigned long long)traces[trace_index].input_digest);
        snprintf(line, sizeof(line), "%s|%s|%s|%s|%s\n",
                 traces[trace_index].case_id,
                 traces[trace_index].create_status,
                 traces[trace_index].process_status,
                 digest_text, events_text);
        for (byte_index = 0u; byte_index < strlen(line); ++byte_index) {
            value ^= (unsigned char)line[byte_index];
            value *= UINT64_C(0x100000001b3);
        }
    }
    return value;
}

static int run_case(const case_spec *spec, case_trace *trace) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_create_config_v0 config;
    as_frame_v0 frame;
    as_output_v0 output;
    as_result_v0 result;
    float input[AS_FRAME_SAMPLES];
    float output_samples[AS_FRAME_SAMPLES];
    char effective[AS_RAII_EFFECTIVE_BYTES];
    uint32_t required = 0u;
    as_status_v0 status;
    const char *provider_id = AS_RAII_EVIDENCE_PROVIDER_ID;

    memset(trace, 0, sizeof(*trace));
    trace->case_id = spec->case_id;
    trace->kind = spec->kind;
    trace->mutation = spec->mutation;
    trace->input_digest = generated_input_digest();

    as_error_v0_init(&error);
    status = as_registry_create_v0(&registry, &error);
    add_event(&trace->events, "registry_create", status);
    if (status != AS_OK || registry == NULL) {
        return 0;
    }

    if (spec->mutation_id == M_PROVIDER_EMPTY) {
        provider_id = "";
    } else if (spec->mutation_id == M_UNKNOWN_PROVIDER) {
        provider_id = "no.such.provider.v0";
    }

    if (spec->mutation_id == M_PROVIDER_EMPTY ||
            spec->mutation_id == M_UNKNOWN_PROVIDER) {
        as_create_config_v0_init(&config);
        status = as_session_create_v0(registry, provider_id,
                                      (uint32_t)strlen(provider_id), &config,
                                      &session, &error);
        add_event(&trace->events, "session_create", status);
        trace->create_status = status_name(status);
        trace->process_status = "-";
    } else {
        status = as_effective_config_create_v0(
            registry, AS_RAII_EVIDENCE_PROVIDER_ID,
            (uint32_t)strlen(AS_RAII_EVIDENCE_PROVIDER_ID),
            AS_MODE_PROCESSING_THREAD, effective, (uint32_t)sizeof(effective),
            &required, &error);
        add_event(&trace->events, "effective_config_create", status);
        if (status != AS_OK || required == 0u) {
            return 0;
        }

        as_create_config_v0_init(&config);
        config.execution_mode = AS_MODE_PROCESSING_THREAD;
        config.epoch = 1u;
        config.config_json = effective;
        config.config_json_length = required - 1u;
        if (spec->mutation_id == M_CONFIG_NULL) {
            config.config_json = NULL;
            config.config_json_length = 0u;
        }
        status = as_session_create_v0(registry, AS_RAII_EVIDENCE_PROVIDER_ID,
                                      (uint32_t)strlen(AS_RAII_EVIDENCE_PROVIDER_ID),
                                      &config, &session, &error);
        add_event(&trace->events, "session_create", status);
        trace->create_status = status_name(status);

        if (status == AS_OK && session != NULL) {
            fill_input(input);
            memset(output_samples, 0, sizeof(output_samples));
            as_frame_v0_init(&frame);
            frame.input = input;
            frame.input_count = AS_FRAME_SAMPLES;
            frame.input_valid_count = AS_FRAME_SAMPLES;
            frame.epoch = 1u;
            frame.first_input_sample = 0;
            as_output_v0_init(&output);
            output.samples = output_samples;
            output.capacity = AS_FRAME_SAMPLES;
            as_result_v0_init(&result);

            switch (spec->mutation_id) {
            case M_ABI_MAJOR:
                frame.abi_major = 1u;
                break;
            case M_INPUT_COUNT:
                frame.input_count = AS_FRAME_SAMPLES - 1u;
                break;
            case M_PARTIAL_FINAL:
                frame.input_valid_count = 80u;
                frame.flags = AS_FRAME_FINAL_INPUT;
                memset(input + 80u, 0, sizeof(float) * (AS_FRAME_SAMPLES - 80u));
                break;
            case M_PARTIAL_NO_FINAL:
                frame.input_valid_count = 80u;
                break;
            case M_NONFINITE:
                input[20u] = NAN;
                break;
            case M_OUTPUT_NULL:
                output.samples = NULL;
                break;
            default:
                break;
            }

            status = as_session_process_v0(session, &frame, &output, &result);
            add_event(&trace->events, "process", status);
            trace->process_status = status_name(status);
            if (status == AS_OK) {
                trace->has_result = 1;
                trace->result = result;
            }

            status = as_session_close_v0(&session);
            add_event(&trace->events, "session_close", status);
            if (session != NULL) {
                return 0;
            }
            status = as_session_close_v0(&session);
            add_event(&trace->events, "session_close_double", status);
            if (session != NULL) {
                return 0;
            }
        } else {
            trace->process_status = "-";
        }
    }

    status = as_registry_close_v0(&registry);
    add_event(&trace->events, "registry_close", status);
    if (registry != NULL) {
        return 0;
    }
    status = as_registry_close_v0(&registry);
    add_event(&trace->events, "registry_close_double", status);
    return registry == NULL ? 1 : 0;
}

static void print_json(const case_trace *traces, size_t count) {
    size_t index;
    size_t event_index;
    printf("{\n");
    printf("  \"protocol\":\"%s\",\n", AS_RAII_EVIDENCE_PROTOCOL);
    printf("  \"harness\":\"c-raii-lifetime-v1\",\n");
    printf("  \"provider_id\":\"%s\",\n", AS_RAII_EVIDENCE_PROVIDER_ID);
    printf("  \"frame_samples\":%u,\n", (unsigned int)AS_RAII_EVIDENCE_FRAME_SAMPLES);
    printf("  \"base_commit\":\"%s\",\n", AS_RAII_EVIDENCE_BASE_COMMIT);
    printf("  \"cases\":[\n");
    for (index = 0u; index < count; ++index) {
        const case_trace *trace = &traces[index];
        char digest_text[17];
        snprintf(digest_text, sizeof(digest_text), "%016llx",
                 (unsigned long long)trace->input_digest);
        printf("    {\"case_id\":\"%s\",\"kind\":\"%s\",\"mutation\":\"%s\",",
               trace->case_id, trace->kind, trace->mutation);
        printf("\"create_status\":\"%s\",\"process_status\":\"%s\",",
               trace->create_status, trace->process_status);
        printf("\"input_digest\":\"%s\",\"events\":[", digest_text);
        for (event_index = 0u; event_index < trace->events.count; ++event_index) {
            printf("%s\"%s\"", event_index == 0u ? "" : ",",
                   trace->events.items[event_index]);
        }
        printf("],\"result\":");
        if (trace->has_result) {
            printf("{\"status\":%d,\"consumed_count\":%u,\"produced_count\":%u,"
                   "\"valid_offset\":%u,\"valid_count\":%u,\"flags\":%u,"
                   "\"epoch\":%llu,\"source_first_sample\":%lld,\"queue_depth\":%u}",
                   (int)trace->result.status,
                   (unsigned int)trace->result.consumed_count,
                   (unsigned int)trace->result.produced_count,
                   (unsigned int)trace->result.valid_offset,
                   (unsigned int)trace->result.valid_count,
                   (unsigned int)trace->result.flags,
                   (unsigned long long)trace->result.epoch,
                   (long long)trace->result.source_first_sample,
                   (unsigned int)trace->result.queue_depth);
        } else {
            printf("null");
        }
        printf("}%s\n", index + 1u == count ? "" : ",");
    }
    printf("  ]\n}\n");
}

int main(void) {
    case_trace traces[AS_RAII_EVIDENCE_CASE_COUNT];
    size_t spec_count = sizeof(SPECS) / sizeof(SPECS[0]);
    size_t index;
    if (spec_count != (size_t)AS_RAII_EVIDENCE_CASE_COUNT) {
        fprintf(stderr, "spec count does not match generated header\n");
        return 1;
    }
    if (generated_input_digest() != AS_RAII_EVIDENCE_INPUT_DIGEST) {
        fprintf(stderr, "input digest does not match pinned model\n");
        return 1;
    }
    for (index = 0u; index < spec_count; ++index) {
        if (!run_case(&SPECS[index], &traces[index])) {
            fprintf(stderr, "case failed: %s\n", SPECS[index].case_id);
            return 1;
        }
    }
    if (observed_model_digest(traces, spec_count) != AS_RAII_EVIDENCE_MODEL_DIGEST) {
        fprintf(stderr, "observed trace does not match pinned contract model\n");
        return 1;
    }
    print_json(traces, spec_count);
    return 0;
}
