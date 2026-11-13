#include "core/as_internal.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

void as_error_clear(as_error_v0 *error) {
    if (error == NULL) return;
    memset(error, 0, sizeof(*error));
    error->struct_size = sizeof(*error);
    error->abi_major = AS_ABI_MAJOR;
    error->abi_minor = AS_ABI_MINOR;
    error->status = AS_OK;
}

void as_error_set(as_error_v0 *error, as_status_v0 status, const char *field,
                  const char *message) {
    if (error == NULL) return;
    as_error_clear(error);
    error->status = status;
    if (message != NULL) {
        strncpy(error->message, message, sizeof(error->message) - 1u);
        error->message[sizeof(error->message) - 1u] = '\0';
    }
    if (field != NULL) {
        strncpy(error->field, field, sizeof(error->field) - 1u);
        error->field[sizeof(error->field) - 1u] = '\0';
    }
}

int as_valid_struct(uint32_t struct_size, uint32_t major, uint32_t minor,
                    uint32_t known_size) {
    return struct_size >= known_size && major == AS_ABI_MAJOR &&
           minor == AS_ABI_MINOR;
}

int as_tail_is_zero(const void *structure, uint32_t known_size,
                    uint32_t struct_size) {
    if (struct_size <= known_size) return 1;
    const unsigned char *bytes = (const unsigned char *)structure;
    for (uint32_t i = known_size; i < struct_size; ++i) {
        if (bytes[i] != 0) return 0;
    }
    return 1;
}

int as_valid_id(const char *text, uint32_t length) {
    if (text == NULL || length == 0 || length > AS_MAX_PROVIDER_ID) return 0;
    const unsigned char first = (unsigned char)text[0];
    if (!(first >= 'a' && first <= 'z') && !(first >= '0' && first <= '9')) return 0;
    for (uint32_t i = 1; i < length; ++i) {
        const unsigned char c = (unsigned char)text[i];
        const int lower = c >= 'a' && c <= 'z';
        const int digit = c >= '0' && c <= '9';
        const int punct = c == '.' || c == '_' || c == '-';
        if (!lower && !digit && !punct) return 0;
    }
    return 1;
}

int as_text_equal(const char *text, uint32_t length, const char *expected) {
    const size_t expected_length = strlen(expected);
    return text != NULL && length == expected_length &&
           memcmp(text, expected, length) == 0;
}

void as_hex(const uint8_t digest[32], char out[65]) { as_sha256_hex(digest, out); }

int as_status_valid(as_status_v0 status) {
    return status >= AS_OK && status <= AS_DUPLICATE;
}

const char *AS_CALL as_status_name_v0(as_status_v0 status) {
    switch (status) {
        case AS_OK: return "ok";
        case AS_INVALID_ARGUMENT: return "invalid_argument";
        case AS_UNSUPPORTED: return "unsupported";
        case AS_RESOURCE_EXHAUSTED: return "resource_exhausted";
        case AS_BACKEND_FAILURE: return "backend_failure";
        case AS_NEEDS_RESET: return "needs_reset";
        case AS_NOT_READY: return "not_ready";
        case AS_END_OF_STREAM: return "end_of_stream";
        case AS_BUSY: return "busy";
        case AS_CLOSED: return "closed";
        case AS_DUPLICATE: return "duplicate";
        default: return "unknown";
    }
}

int AS_CALL as_valid_provider_id_v0(const char *text, uint32_t length) {
    return as_valid_id(text, length);
}

as_status_v0 AS_CALL as_sha256_hex_v0(const void *bytes, uint64_t length,
                                      char *hex_out, uint32_t capacity) {
    if ((bytes == NULL && length != 0) || hex_out == NULL || capacity < 65u ||
        length > SIZE_MAX) {
        return AS_INVALID_ARGUMENT;
    }
    uint8_t digest[32];
    as_sha256(bytes, (size_t)length, digest);
    as_sha256_hex(digest, hex_out);
    return AS_OK;
}

void AS_CALL as_error_v0_init(as_error_v0 *error) {
    if (error != NULL) as_error_clear(error);
}

void AS_CALL as_asset_v0_init(as_asset_v0 *asset) {
    if (asset == NULL) return;
    memset(asset, 0, sizeof(*asset));
    asset->struct_size = sizeof(*asset);
    asset->abi_major = AS_ABI_MAJOR;
    asset->abi_minor = AS_ABI_MINOR;
}

void AS_CALL as_create_config_v0_init(as_create_config_v0 *config) {
    if (config == NULL) return;
    memset(config, 0, sizeof(*config));
    config->struct_size = sizeof(*config);
    config->abi_major = AS_ABI_MAJOR;
    config->abi_minor = AS_ABI_MINOR;
    config->sample_rate_hz = AS_SAMPLE_RATE_HZ;
    config->channels = AS_CHANNELS;
    config->frame_samples = AS_FRAME_SAMPLES;
    config->execution_mode = AS_MODE_PROCESSING_THREAD;
    config->epoch = 1;
    config->first_input_sample = 0;
}

void AS_CALL as_frame_v0_init(as_frame_v0 *frame) {
    if (frame == NULL) return;
    memset(frame, 0, sizeof(*frame));
    frame->struct_size = sizeof(*frame);
    frame->abi_major = AS_ABI_MAJOR;
    frame->abi_minor = AS_ABI_MINOR;
    frame->input_count = AS_FRAME_SAMPLES;
    frame->input_valid_count = AS_FRAME_SAMPLES;
}

void AS_CALL as_output_v0_init(as_output_v0 *output) {
    if (output == NULL) return;
    memset(output, 0, sizeof(*output));
    output->struct_size = sizeof(*output);
    output->abi_major = AS_ABI_MAJOR;
    output->abi_minor = AS_ABI_MINOR;
    output->capacity = AS_FRAME_SAMPLES;
}

void AS_CALL as_result_v0_init(as_result_v0 *result) {
    if (result == NULL) return;
    memset(result, 0, sizeof(*result));
    result->struct_size = sizeof(*result);
    result->abi_major = AS_ABI_MAJOR;
    result->abi_minor = AS_ABI_MINOR;
    result->status = AS_OK;
}

void AS_CALL as_provider_table_v0_init(as_provider_table_v0 *table) {
    if (table == NULL) return;
    memset(table, 0, sizeof(*table));
    table->struct_size = sizeof(*table);
    table->abi_major = AS_ABI_MAJOR;
    table->abi_minor = AS_ABI_MINOR;
}

const char *AS_CALL as_contract_version_v0(void) { return AS_CONTRACT_VERSION; }

const char *AS_CALL as_build_id_v0(void) { return as_build_identity; }
