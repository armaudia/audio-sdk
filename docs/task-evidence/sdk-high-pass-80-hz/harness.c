/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local installed-consumer probe for dsp.highpass80.v0.
 *
 * This file is evidence tooling only. It links against an installed audio-sdk
 * package and uses only public v0 headers. It does not change the provider,
 * descriptor, registry, default behavior or any shared SDK source.
 *
 * Usage:
 *   harness stream            # line commands on stdin, JSON Lines on stdout
 *   harness control <name>    # one invalid/missing/nonfinite probe
 */
#include <audio_sdk/session_v0.h>

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define FRAME AS_FRAME_SAMPLES
#define LINE_CAPACITY 16384

static const char *kProviderId = "dsp.highpass80.v0";

static void print_string(const char *text) {
    putchar('"');
    for (const unsigned char *p = (const unsigned char *)text; *p != '\0'; ++p) {
        if (*p == '"' || *p == '\\') {
            putchar('\\');
            putchar((char)*p);
        } else if (*p == '\n') {
            fputs("\\n", stdout);
        } else if (*p < 0x20u) {
            printf("\\u%04x", (unsigned)*p);
        } else {
            putchar((char)*p);
        }
    }
    putchar('"');
}

static void print_float(double value) {
    if (isnan(value)) {
        fputs("\"nan\"", stdout);
    } else if (isinf(value)) {
        fputs(value > 0 ? "\"inf\"" : "\"-inf\"", stdout);
    } else {
        printf("%.9g", value);
    }
}

static void begin_event(void) { putchar('{'); }

static void print_status(int name, as_status_v0 status) {
    if (name) fputs("\"status\":", stdout);
    printf("%d,\"status_name\":", (int)status);
    print_string(as_status_name_v0(status));
}

static void print_samples(const float *samples, uint32_t count) {
    putchar('[');
    for (uint32_t i = 0; i < count; ++i) {
        if (i) putchar(',');
        print_float((double)samples[i]);
    }
    putchar(']');
}

static void print_result(const as_result_v0 *result) {
    fputs(",\"result\":{\"status\":", stdout);
    printf("%d,\"status_name\":", (int)result->status);
    print_string(as_status_name_v0(result->status));
    printf(",\"consumed\":%u,\"produced\":%u,\"valid_offset\":%u,\"valid_count\":%u",
           result->consumed_count, result->produced_count, result->valid_offset,
           result->valid_count);
    printf(",\"flags\":%u,\"epoch\":%" PRIu64 ",\"source_first\":%" PRId64,
           result->flags, result->epoch, result->source_first_sample);
    fputs("}", stdout);
}

static int get_config(as_registry_v0 *registry, as_create_config_v0 *config,
                      char *buffer, size_t capacity, uint32_t mode) {
    uint32_t required = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    const as_status_v0 status = as_effective_config_create_v0(
        registry, kProviderId, (uint32_t)strlen(kProviderId), mode, buffer,
        (uint32_t)capacity, &required, &error);
    if (status != AS_OK || required == 0 || required > capacity) return 0;
    as_create_config_v0_init(config);
    config->execution_mode = mode;
    config->config_json = buffer;
    config->config_json_length = required - 1u;
    return 1;
}

static as_session_v0 *make_session(as_registry_v0 *registry, uint64_t epoch,
                                   int64_t first, uint32_t mode) {
    char config[4096];
    as_create_config_v0 create;
    if (!get_config(registry, &create, config, sizeof(config), mode)) return NULL;
    create.epoch = epoch;
    create.first_input_sample = first;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_session_create_v0(registry, kProviderId, (uint32_t)strlen(kProviderId),
                             &create, &session, &error) != AS_OK) return NULL;
    return session;
}

static void fill_frame(as_frame_v0 *frame, const float *input, uint32_t valid,
                       uint32_t flags, int64_t first, uint64_t epoch) {
    as_frame_v0_init(frame);
    frame->input = input;
    frame->input_count = FRAME;
    frame->input_valid_count = valid;
    frame->flags = flags;
    frame->first_input_sample = first;
    frame->epoch = epoch;
}

static int read_float_token(char **cursor, float *out) {
    while (**cursor == ' ' || **cursor == '\t') ++(*cursor);
    if (**cursor == '\0' || **cursor == '\n') return 0;
    char *end = NULL;
    const double value = strtod(*cursor, &end);
    if (end == *cursor) return 0;
    *out = (float)value;
    *cursor = end;
    return 1;
}

static void emit_frame(as_session_v0 *session, uint32_t valid, uint32_t flags,
                       int64_t first, uint64_t epoch, const float *input,
                       uint32_t index) {
    float produced[FRAME];
    as_output_v0 output;
    as_result_v0 result;
    as_output_v0_init(&output);
    output.samples = produced;
    output.capacity = FRAME;
    as_result_v0_init(&result);
    as_frame_v0 frame;
    fill_frame(&frame, input, valid, flags, first, epoch);
    const as_status_v0 status = as_session_process_v0(session, &frame, &output, &result);
    begin_event();
    print_status(1, status);
    printf(",\"index\":%u,\"valid_input\":%u,\"flags\":%u,\"first\":%" PRId64,
           index, valid, flags, first);
    if (status == AS_OK) {
        fputs(",\"samples\":", stdout);
        print_samples(produced, FRAME);
        print_result(&result);
    }
    fputs("}\n", stdout);
}

static void emit_drain(as_session_v0 *session) {
    for (unsigned call = 0; call < 8; ++call) {
        float produced[FRAME] = {0};
        as_output_v0 output;
        as_result_v0 result;
        as_output_v0_init(&output);
        output.samples = produced;
        output.capacity = FRAME;
        as_result_v0_init(&result);
        const as_status_v0 status = as_session_drain_next_v0(session, &output, &result);
        begin_event();
        print_status(1, status);
        printf(",\"call\":%u", call);
        if (status == AS_OK) {
            fputs(",\"samples\":", stdout);
            print_samples(produced, FRAME);
        }
        print_result(&result);
        fputs("}\n", stdout);
        if (status == AS_END_OF_STREAM) break;
    }
}

static void emit_stats(as_session_v0 *session) {
    char buffer[8192];
    uint32_t required = 0;
    const as_status_v0 status = as_session_get_stats_v0(session, buffer,
                                                        (uint32_t)sizeof(buffer), &required);
    print_status(1, status);
    printf(",\"required\":%u,\"json\":", required);
    if (status == AS_OK) print_string(buffer);
    else print_string("");
    fputs("}\n", stdout);
}

static int stream_mode(void) {
    char line[LINE_CAPACITY];
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) {
        fprintf(stderr, "registry_create failed\n");
        return 2;
    }
    uint32_t index = 0;
    while (fgets(line, sizeof(line), stdin) != NULL) {
        char *cursor = line;
        while (*cursor == ' ' || *cursor == '\t') ++cursor;
        char *token = cursor;
        while (*cursor != '\0' && *cursor != ' ' && *cursor != '\t' && *cursor != '\n') ++cursor;
        const size_t length = (size_t)(cursor - token);
        if (*cursor != '\0') *cursor++ = '\0';

        if (length == 6 && memcmp(token, "create", 6) == 0) {
            char *end = NULL;
            const uint64_t epoch = strtoull(cursor, &end, 10);
            cursor = end;
            const int64_t first = strtoll(cursor, &end, 10);
            cursor = end;
            const uint32_t mode = (uint32_t)strtoul(cursor, &end, 10);
            session = make_session(registry, epoch, first, mode);
            fputs("{\"event\":\"create\",\"epoch\":", stdout);
            printf("%" PRIu64 ",\"first\":%" PRId64 ",\"mode\":%u,\"ok\":%d}\n",
                   epoch, first, mode, session != NULL);
            if (session == NULL) {
                as_registry_close_v0(&registry);
                return 2;
            }
            index = 0;
            continue;
        }
        if (length == 5 && memcmp(token, "frame", 5) == 0) {
            char *end = NULL;
            const uint32_t valid = (uint32_t)strtoul(cursor, &end, 10);
            cursor = end;
            const uint32_t flags = (uint32_t)strtoul(cursor, &end, 10);
            cursor = end;
            const int64_t first = strtoll(cursor, &end, 10);
            cursor = end;
            const uint64_t epoch = strtoull(cursor, &end, 10);
            cursor = end;
            float input[FRAME] = {0};
            for (uint32_t i = 0; i < FRAME && i < valid; ++i) {
                if (!read_float_token(&cursor, &input[i])) {
                    fprintf(stderr, "short frame at index %u\n", index);
                    as_session_close_v0(&session);
                    as_registry_close_v0(&registry);
                    return 2;
                }
            }
            emit_frame(session, valid, flags, first, epoch, input, index++);
            continue;
        }
        if (length == 5 && memcmp(token, "reset", 5) == 0) {
            char *end = NULL;
            const uint64_t epoch = strtoull(cursor, &end, 10);
            cursor = end;
            const int64_t first = strtoll(cursor, &end, 10);
            as_error_v0 reset_error;
            as_error_v0_init(&reset_error);
            const as_status_v0 status = as_session_reset_v0(session, epoch, first,
                                                            &reset_error);
            begin_event();
            print_status(1, status);
            printf(",\"event\":\"reset\",\"epoch\":%" PRIu64 ",\"first\":%" PRId64 "}\n",
                   epoch, first);
            index = 0;
            continue;
        }
        if (length == 5 && memcmp(token, "drain", 5) == 0) {
            const as_status_v0 status = as_session_begin_drain_v0(session);
            begin_event();
            print_status(1, status);
            fputs(",\"event\":\"begin_drain\"}\n", stdout);
            emit_drain(session);
            begin_event();
            emit_stats(session);
            continue;
        }
        if (length == 5 && memcmp(token, "stats", 5) == 0) {
            begin_event();
            fputs("\"event\":\"stats_probe\",", stdout);
            emit_stats(session);
            continue;
        }
        if (length == 4 && memcmp(token, "load", 4) == 0) {
            char *end = NULL;
            const uint32_t frames = (uint32_t)strtoul(cursor, &end, 10);
            struct timespec start, stop;
            clock_gettime(CLOCK_MONOTONIC, &start);
            uint64_t finite = 0;
            double peak = 0.0;
            for (uint32_t frame_index = 0; frame_index < frames; ++frame_index) {
                float input[FRAME];
                for (uint32_t i = 0; i < FRAME; ++i) {
                    const double phase = 2.0 * 3.14159265358979323846 * 1000.0 *
                                         (double)(frame_index * FRAME + i) / 16000.0;
                    input[i] = (float)(0.1 * sin(phase));
                }
                float produced[FRAME];
                as_output_v0 output;
                as_result_v0 result;
                as_output_v0_init(&output);
                output.samples = produced;
                output.capacity = FRAME;
                as_result_v0_init(&result);
                as_frame_v0 frame;
                fill_frame(&frame, input, FRAME, 0, (int64_t)frame_index * FRAME, 1);
                if (as_session_process_v0(session, &frame, &output, &result) != AS_OK) {
                    fprintf(stderr, "load process failed at frame %u\n", frame_index);
                    return 2;
                }
                for (uint32_t i = 0; i < FRAME; ++i) {
                    if (isfinite((double)produced[i])) ++finite;
                    const double magnitude = fabs((double)produced[i]);
                    if (magnitude > peak) peak = magnitude;
                }
            }
            clock_gettime(CLOCK_MONOTONIC, &stop);
            const uint64_t elapsed = (uint64_t)(stop.tv_sec - start.tv_sec) * 1000000000ull +
                                     (uint64_t)(stop.tv_nsec - start.tv_nsec);
            const double duration = (double)frames * FRAME / 16000.0;
            fputs("{\"event\":\"load\",", stdout);
            printf("\"frames\":%u,\"elapsed_ns\":%" PRIu64 ",\"audio_seconds\":%.9g,"
                   "\"finite\":%" PRIu64 ",\"peak\":", frames, elapsed, duration, finite);
            print_float(peak);
            printf(",\"rtf\":%.9g}\n", (double)elapsed / 1000000000.0 / duration);
            continue;
        }
        if (length == 4 && memcmp(token, "dual", 4) == 0) {
            char *end = NULL;
            const uint32_t frames = (uint32_t)strtoul(cursor, &end, 10);
            as_session_v0 *other = make_session(registry, 9, 100000, 2);
            if (other == NULL) return 2;
            for (uint32_t frame_index = 0; frame_index < frames; ++frame_index) {
                float input[FRAME];
                for (uint32_t i = 0; i < FRAME; ++i) {
                    const double phase = 2.0 * 3.14159265358979323846 * 1000.0 *
                                         (double)(frame_index * FRAME + i) / 16000.0;
                    input[i] = (float)(0.5 * sin(phase));
                }
                as_session_v0 *sessions[2] = {session, other};
                const int64_t firsts[2] = {(int64_t)frame_index * FRAME,
                                           100000 + (int64_t)frame_index * FRAME};
                const uint64_t epochs[2] = {1, 9};
                for (int which = 0; which < 2; ++which) {
                    float produced[FRAME];
                    as_output_v0 output;
                    as_result_v0 result;
                    as_output_v0_init(&output);
                    output.samples = produced;
                    output.capacity = FRAME;
                    as_result_v0_init(&result);
                    as_frame_v0 frame;
                    fill_frame(&frame, input, FRAME, 0, firsts[which], epochs[which]);
                    const as_status_v0 status =
                        as_session_process_v0(sessions[which], &frame, &output, &result);
                    begin_event();
                    print_status(1, status);
                    printf(",\"event\":\"dual\",\"session\":%d,\"index\":%u,\"sample\":",
                           which, frame_index);
                    print_samples(produced, FRAME);
                    print_result(&result);
                    fputs("}\n", stdout);
                }
            }
            as_session_close_v0(&other);
            continue;
        }
        if (length == 5 && memcmp(token, "close", 5) == 0) {
            const as_status_v0 status = as_session_close_v0(&session);
            const as_status_v0 closed = as_registry_close_v0(&registry);
            begin_event();
            print_status(1, status);
            printf(",\"event\":\"close\",\"registry_status\":%d,\"registry_status_name\":",
                   (int)closed);
            print_string(as_status_name_v0(closed));
            fputs("}\n", stdout);
            return status == AS_OK && closed == AS_OK ? 0 : 2;
        }
        fprintf(stderr, "unknown command: %s\n", token);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 2;
    }
    as_session_close_v0(&session);
    as_registry_close_v0(&registry);
    return 2;
}

static void probe_status(const char *name, as_status_v0 status, const char *detail) {
    begin_event();
    print_status(1, status);
    fputs(",\"event\":\"control\",\"name\":", stdout);
    print_string(name);
    fputs(",\"detail\":", stdout);
    print_string(detail);
    fputs("}\n", stdout);
}

static int control_mode(const char *name) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) return 2;
    char config[4096];
    as_create_config_v0 create;
    if (!get_config(registry, &create, config, sizeof(config), 2)) return 2;

    if (strcmp(name, "create_bad_rate") == 0 ||
        strcmp(name, "create_bad_channels") == 0 ||
        strcmp(name, "create_bad_frame") == 0 ||
        strcmp(name, "create_bad_mode") == 0) {
        if (strcmp(name, "create_bad_rate") == 0) create.sample_rate_hz = 48000;
        if (strcmp(name, "create_bad_channels") == 0) create.channels = 2;
        if (strcmp(name, "create_bad_frame") == 0) create.frame_samples = 320;
        if (strcmp(name, "create_bad_mode") == 0) create.execution_mode = 1;
        as_session_v0 *session = NULL;
        as_error_v0 local_error;
        as_error_v0_init(&local_error);
        const as_status_v0 status = as_session_create_v0(
            registry, kProviderId, (uint32_t)strlen(kProviderId), &create, &session,
            &local_error);
        probe_status(name, status, local_error.field);
        as_registry_close_v0(&registry);
        return 0;
    }
    if (strcmp(name, "create_null_config") == 0 ||
        strcmp(name, "create_null_out") == 0 ||
        strcmp(name, "create_null_id") == 0) {
        as_session_v0 *session = NULL;
        as_error_v0 local_error;
        as_error_v0_init(&local_error);
        const as_create_config_v0 *cfg = strcmp(name, "create_null_config") == 0 ? NULL : &create;
        as_session_v0 **out = strcmp(name, "create_null_out") == 0 ? NULL : &session;
        const char *id = strcmp(name, "create_null_id") == 0 ? NULL : kProviderId;
        const as_status_v0 status = as_session_create_v0(
            registry, id, id == NULL ? 0u : (uint32_t)strlen(id), cfg, out, &local_error);
        probe_status(name, status, local_error.field);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }

    as_session_v0 *session = make_session(registry, 1, 0, 2);
    if (session == NULL) return 2;
    float input[FRAME] = {0};
    input[0] = 0.25f;
    float produced[FRAME] = {0};
    as_frame_v0 frame;
    as_output_v0 output;
    as_result_v0 result;
    fill_frame(&frame, input, FRAME, 0, 0, 1);
    as_output_v0_init(&output);
    output.samples = produced;
    output.capacity = FRAME;
    as_result_v0_init(&result);

    if (strcmp(name, "process_null_frame") == 0 ||
        strcmp(name, "process_null_input") == 0 ||
        strcmp(name, "process_null_output") == 0 ||
        strcmp(name, "process_null_samples") == 0 ||
        strcmp(name, "process_small_capacity") == 0 ||
        strcmp(name, "process_null_result") == 0) {
        as_frame_v0 *frame_arg = &frame;
        const float *input_arg = input;
        as_output_v0 *output_arg = &output;
        as_result_v0 *result_arg = &result;
        if (strcmp(name, "process_null_frame") == 0) frame_arg = NULL;
        if (strcmp(name, "process_null_input") == 0) input_arg = NULL;
        if (strcmp(name, "process_null_output") == 0) output_arg = NULL;
        if (strcmp(name, "process_null_samples") == 0) output.samples = NULL;
        if (strcmp(name, "process_small_capacity") == 0) output.capacity = FRAME - 1u;
        if (strcmp(name, "process_null_result") == 0) result_arg = NULL;
        frame.input = input_arg;
        const as_status_v0 status =
            as_session_process_v0(session, frame_arg, output_arg, result_arg);
        probe_status(name, status, "");
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }
    if (strcmp(name, "process_bad_position") == 0 ||
        strcmp(name, "recover_after_bad_position") == 0) {
        fill_frame(&frame, input, FRAME, 0, 160, 1);
        const as_status_v0 bad = as_session_process_v0(session, &frame, &output, &result);
        as_status_v0 recovered = AS_NOT_READY;
        as_status_v0 reset_status = AS_NOT_READY;
        if (strcmp(name, "recover_after_bad_position") == 0) {
            as_error_v0 reset_error;
            as_error_v0_init(&reset_error);
            reset_status = as_session_reset_v0(session, 2, 320, &reset_error);
            fill_frame(&frame, input, FRAME, 0, 320, 2);
            as_output_v0_init(&output);
            output.samples = produced;
            output.capacity = FRAME;
            as_result_v0_init(&result);
            recovered = as_session_process_v0(session, &frame, &output, &result);
        }
        begin_event();
        print_status(1, bad);
        fputs(",\"event\":\"control\",\"name\":", stdout);
        print_string(name);
        printf(",\"reset_status\":%d,\"recovered_status\":%d,\"samples\":",
               (int)reset_status, (int)recovered);
        print_samples(produced, FRAME);
        fputs("}\n", stdout);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }
    if (strcmp(name, "reset_negative_first") == 0) {
        as_error_v0 reset_error;
        as_error_v0_init(&reset_error);
        const as_status_v0 status = as_session_reset_v0(session, 3, -1, &reset_error);
        probe_status(name, status, reset_error.field);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }
    if (strcmp(name, "drain_null_output") == 0 ||
        strcmp(name, "drain_null_result") == 0) {
        const as_status_v0 begin = as_session_begin_drain_v0(session);
        as_output_v0 *output_arg = &output;
        as_result_v0 *result_arg = &result;
        if (strcmp(name, "drain_null_output") == 0) output_arg = NULL;
        if (strcmp(name, "drain_null_result") == 0) result_arg = NULL;
        const as_status_v0 status =
            as_session_drain_next_v0(session, output_arg, result_arg);
        begin_event();
        print_status(1, status);
        fputs(",\"event\":\"control\",\"name\":", stdout);
        print_string(name);
        printf(",\"begin_status\":%d}\n", (int)begin);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }
    if (strcmp(name, "nonfinite_nan") == 0 || strcmp(name, "nonfinite_inf") == 0) {
        if (strcmp(name, "nonfinite_nan") == 0) input[5] = (float)NAN;
        else input[7] = (float)INFINITY;
        const as_status_v0 status = as_session_process_v0(session, &frame, &output, &result);
        begin_event();
        print_status(1, status);
        fputs(",\"event\":\"control\",\"name\":", stdout);
        print_string(name);
        fputs(",\"samples\":", stdout);
        print_samples(produced, 12);
        fputs("}\n", stdout);
        as_session_close_v0(&session);
        as_registry_close_v0(&registry);
        return 0;
    }
    fprintf(stderr, "unknown control: %s\n", name);
    as_session_close_v0(&session);
    as_registry_close_v0(&registry);
    return 2;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "stream") == 0) return stream_mode();
    if (argc == 3 && strcmp(argv[1], "control") == 0) return control_mode(argv[2]);
    fprintf(stderr, "usage: %s stream | control <name>\n", argv[0]);
    return 2;
}
