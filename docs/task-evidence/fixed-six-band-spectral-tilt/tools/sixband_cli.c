/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/*
 * Task-local measurement CLI. It uses only the installed public SDK API and
 * the opt-in task-local provider. No file is written inside the SDK tree.
 */
#include "audio_sdk/session_v0.h"
#include "sixband_descriptor.h"
#include "sixband_provider.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIXBAND_CLI_FRAMES 160u
#define SIXBAND_CLI_GUARD 512

static int sixband_fail(const char *message) {
    fprintf(stderr, "sixband_cli: %s\n", message);
    return 1;
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

static int write_f32_le(const char *path, const float *samples, size_t count) {
    FILE *file = fopen(path, "wb");
    if (file == NULL) return -1;
    for (size_t i = 0; i < count; ++i) {
        uint32_t bits = 0;
        memcpy(&bits, &samples[i], sizeof(bits));
        const uint8_t bytes[4] = {
            (uint8_t)(bits & 0xffu), (uint8_t)((bits >> 8) & 0xffu),
            (uint8_t)((bits >> 16) & 0xffu), (uint8_t)((bits >> 24) & 0xffu)};
        if (fwrite(bytes, 1, 4, file) != 4) {
            fclose(file);
            return -1;
        }
    }
    return fclose(file) == 0 ? 0 : -1;
}

typedef struct collector {
    float *samples;
    unsigned char *covered;
    int64_t base;
    int64_t first;
    size_t length;
    size_t size;
    uint64_t collisions;
    uint64_t out_of_range;
} collector;

static int collector_init(collector *c, int64_t first, size_t length) {
    c->base = first - SIXBAND_CLI_GUARD;
    c->first = first;
    c->length = length;
    c->size = length + (size_t)SIXBAND_CLI_GUARD * 2u;
    c->samples = (float *)calloc(c->size, sizeof(float));
    c->covered = (unsigned char *)calloc(c->size, 1);
    c->collisions = 0;
    c->out_of_range = 0;
    return c->samples != NULL && c->covered != NULL ? 0 : -1;
}

static void collector_add(collector *c, const as_output_v0 *output,
                          const as_result_v0 *result) {
    for (uint32_t i = 0; i < result->valid_count; ++i) {
        const int64_t sample = result->source_first_sample +
                               (int64_t)result->valid_offset + (int64_t)i;
        if (sample < c->first || sample >= c->first + (int64_t)c->length ||
            sample < c->base || sample >= c->base + (int64_t)c->size) {
            ++c->out_of_range;
            continue;
        }
        const size_t index = (size_t)(sample - c->base);
        if (c->covered[index]) {
            ++c->collisions;
            continue;
        }
        c->covered[index] = 1;
        c->samples[(size_t)(sample - c->first)] =
            output->samples[result->valid_offset + i];
    }
}

static int collector_complete(const collector *c) {
    if (c->collisions != 0 || c->out_of_range != 0) return 0;
    for (size_t i = 0; i < c->length; ++i) {
        if (!c->covered[(size_t)(c->first - c->base) + i]) return 0;
    }
    return 1;
}

static void collector_summary(const collector *c, double *peak,
                              uint64_t *nonfinite) {
    *peak = 0.0;
    *nonfinite = 0;
    for (size_t i = 0; i < c->length; ++i) {
        const float value = c->samples[i];
        if (!isfinite((double)value)) {
            ++*nonfinite;
            continue;
        }
        const double magnitude = fabs((double)value);
        if (magnitude > *peak) *peak = magnitude;
    }
}

int main(int argc, char **argv) {
    if (argc != 7) {
        fprintf(stderr,
                "usage: sixband_cli <input.f32> <output.f32> <tilt|identity> "
                "<epoch> <first_sample> <mode_label>\n");
        return 2;
    }
    const char *input_path = argv[1];
    const char *output_path = argv[2];
    const char *mode = argv[3];
    char *end = NULL;
    unsigned long long epoch_value = strtoull(argv[4], &end, 10);
    if (end == argv[4] || *end != '\0') return sixband_fail("invalid epoch");
    long long first_value = strtoll(argv[5], &end, 10);
    if (end == argv[5] || *end != '\0') return sixband_fail("invalid first_sample");

    float *input = NULL;
    size_t input_count = 0;
    collector collected;
    memset(&collected, 0, sizeof(collected));
    int exit_code = 1;
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);

    if (read_f32_le(input_path, &input, &input_count) != 0)
        return sixband_fail("cannot read input fixture");
    if (strcmp(mode, "identity") == 0) {
        if (write_f32_le(output_path, input, input_count) != 0)
            return sixband_fail("cannot write identity output");
        double peak = 0.0;
        for (size_t i = 0; i < input_count; ++i) {
            const double magnitude = fabs((double)input[i]);
            if (magnitude > peak) peak = magnitude;
        }
        printf("INFO {\"schema_id\":\"sixband-cli/0.1\",\"mode\":\"identity\","
               "\"provider_id\":null,\"buffering_delay_samples\":0}\n");
        printf("STATS {\"schema_id\":\"sixband-cli-stats/0.1\","
               "\"delivered_valid_samples\":%llu,\"backend_failures\":0}\n",
               (unsigned long long)input_count);
        printf("RESULT {\"mode\":\"identity\",\"input_samples\":%llu,"
               "\"output_samples\":%llu,\"collisions\":0,\"out_of_range\":0,"
               "\"coverage_ok\":true,\"nonfinite\":0,\"peak\":%.17g}\n",
               (unsigned long long)input_count, (unsigned long long)input_count,
               peak);
        free(input);
        return 0;
    }
    if (strcmp(mode, "tilt") != 0) return sixband_fail("unknown mode");

    if (as_registry_create_v0(&registry, &error) != AS_OK)
        return sixband_fail("registry create failed");
    if (sixband_register(registry, &error) != AS_OK)
        return sixband_fail("provider registration failed");

    const char *provider_id = "sixband.tilt.reference.v0";
    const uint32_t provider_length = 25u;
    char config[2048];
    uint32_t required = 0;
    if (as_effective_config_create_v0(registry, provider_id, provider_length,
                                      AS_MODE_PROCESSING_THREAD, config,
                                      sizeof(config), &required, &error) != AS_OK)
        return sixband_fail("effective config creation failed");

    as_create_config_v0 create;
    as_create_config_v0_init(&create);
    create.execution_mode = AS_MODE_PROCESSING_THREAD;
    create.epoch = (uint64_t)epoch_value;
    create.first_input_sample = (int64_t)first_value;
    create.config_json = config;
    create.config_json_length = required - 1u;

    if (as_session_create_v0(registry, provider_id, provider_length, &create,
                             &session, &error) != AS_OK)
        return sixband_fail("session create failed");
    if (collector_init(&collected, (int64_t)first_value, input_count) != 0)
        return sixband_fail("collector allocation failed");

    float frame_input[SIXBAND_CLI_FRAMES];
    float samples[SIXBAND_CLI_FRAMES];
    as_frame_v0 frame;
    as_output_v0 output;
    as_result_v0 result;
    as_frame_v0_init(&frame);
    as_output_v0_init(&output);
    as_result_v0_init(&result);
    output.samples = samples;
    output.capacity = SIXBAND_CLI_FRAMES;
    frame.input = frame_input;
    frame.input_count = SIXBAND_CLI_FRAMES;
    frame.epoch = (uint64_t)epoch_value;

    for (size_t offset = 0; offset < input_count; offset += SIXBAND_CLI_FRAMES) {
        const size_t count = input_count - offset < SIXBAND_CLI_FRAMES
                                 ? input_count - offset
                                 : (size_t)SIXBAND_CLI_FRAMES;
        memset(frame_input, 0, sizeof(frame_input));
        memcpy(frame_input, input + offset, count * sizeof(float));
        frame.input_valid_count = (uint32_t)count;
        frame.flags = count < SIXBAND_CLI_FRAMES ? AS_FRAME_FINAL_INPUT : 0u;
        frame.first_input_sample = (int64_t)first_value + (int64_t)offset;
        if (as_session_process_v0(session, &frame, &output, &result) != AS_OK)
            return sixband_fail("process failed");
        collector_add(&collected, &output, &result);
    }
    if (as_session_begin_drain_v0(session) != AS_OK)
        return sixband_fail("begin drain failed");
    for (;;) {
        as_status_v0 status = as_session_drain_next_v0(session, &output, &result);
        if (status == AS_END_OF_STREAM) break;
        if (status != AS_OK) return sixband_fail("drain failed");
        collector_add(&collected, &output, &result);
    }

    if (!collector_complete(&collected)) return sixband_fail("output coverage invalid");
    if (write_f32_le(output_path, collected.samples, input_count) != 0)
        return sixband_fail("cannot write output fixture");

    char info[2048];
    char stats[4096];
    uint32_t info_size = 0;
    uint32_t stats_size = 0;
    if (as_session_get_info_v0(session, info, sizeof(info), &info_size) != AS_OK)
        return sixband_fail("session info failed");
    if (as_session_get_stats_v0(session, stats, sizeof(stats), &stats_size) != AS_OK)
        return sixband_fail("session stats failed");

    double peak = 0.0;
    uint64_t nonfinite = 0;
    collector_summary(&collected, &peak, &nonfinite);
    printf("INFO %s\n", info);
    printf("STATS %s\n", stats);
    printf("RESULT {\"mode\":\"%s\",\"input_samples\":%llu,"
           "\"output_samples\":%llu,\"collisions\":%llu,"
           "\"out_of_range\":%llu,\"coverage_ok\":%s,"
           "\"nonfinite\":%llu,\"peak\":%.17g}\n",
           argv[6], (unsigned long long)input_count,
           (unsigned long long)input_count,
           (unsigned long long)collected.collisions,
           (unsigned long long)collected.out_of_range,
           collector_complete(&collected) ? "true" : "false",
           (unsigned long long)nonfinite, peak);
    exit_code = 0;

cleanup:
    if (session != NULL) (void)as_session_close_v0(&session);
    if (registry != NULL) (void)as_registry_close_v0(&registry);
    free(collected.samples);
    free(collected.covered);
    free(input);
    return exit_code;
}
