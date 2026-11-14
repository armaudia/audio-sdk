/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "core/as_internal.h"

#include <stdio.h>
#include <string.h>

static int exact_keys(const as_json_doc *doc, uint32_t object,
                      const char *const *keys, uint32_t count) {
    if (object >= doc->node_count || doc->nodes[object].type != AS_JSON_OBJECT)
        return 0;
    if (doc->nodes[object].child_count != count) return 0;
    for (uint32_t i = 0; i < count; ++i) {
        if (as_json_get(doc, object, keys[i]) == AS_JSON_NO_INDEX) return 0;
    }
    return 1;
}

static int string_is(const as_json_doc *doc, uint32_t object, const char *key,
                     const char *expected) {
    const char *text = NULL;
    uint32_t length = 0;
    return as_json_get_string(doc, object, key, &text, &length) == 0 &&
           as_text_equal(text, length, expected);
}

static int int_is(const as_json_doc *doc, uint32_t object, const char *key,
                  int64_t expected) {
    int64_t value = 0;
    return as_json_get_int(doc, object, key, &value) == 0 && value == expected;
}

static int settings_valid(const as_json_doc *doc, uint32_t settings,
                          const char *provider_id) {
    if (settings >= doc->node_count || doc->nodes[settings].type != AS_JSON_OBJECT)
        return 0;
    if (strcmp(provider_id, "speex.ns.v0") == 0) {
        static const char *const keys[] = {"agc",          "denoise", "dereverb",
                                           "suppression_db", "vad_continue",
                                           "vad_start"};
        if (!exact_keys(doc, settings, keys, 6)) return 0;
        int boolean = 0;
        int64_t integer = 0;
        return as_json_get_bool(doc, settings, "agc", &boolean) == 0 && boolean == 0 &&
               as_json_get_bool(doc, settings, "denoise", &boolean) == 0 &&
               boolean == 1 &&
               as_json_get_bool(doc, settings, "dereverb", &boolean) == 0 &&
               boolean == 0 &&
               as_json_get_int(doc, settings, "suppression_db", &integer) == 0 &&
               integer == -20 &&
               as_json_get_int(doc, settings, "vad_continue", &integer) == 0 &&
               integer == 20 &&
               as_json_get_int(doc, settings, "vad_start", &integer) == 0 &&
               integer == 35;
    }
    if (strcmp(provider_id, "dsp.highpass80.v0") == 0) {
        static const char *const keys[] = {"cutoff_hz", "q"};
        if (!exact_keys(doc, settings, keys, 2)) return 0;
        const char *text = NULL;
        uint32_t length = 0;
        return as_json_get_string(doc, settings, "cutoff_hz", &text, &length) == 0 &&
               as_text_equal(text, length, "80") &&
               as_json_get_string(doc, settings, "q", &text, &length) == 0 &&
               as_text_equal(text, length, "0.7071067811865476");
    }
    /* External providers declare their own settings schema; v0 accepts an
     * empty object unless the SDK knows the provider. */
    return doc->nodes[settings].child_count == 0;
}

as_status_v0 as_effective_config_validate(as_session_v0 *session,
                                          const char *bytes, uint32_t length,
                                          as_error_v0 *error) {
    static const char *const top_keys[] = {
        "adaptation",         "application_contract", "batching",
        "clipping_policy",    "descriptor_digest",    "engine",
        "execution_mode",     "float_to_int_policy",  "input",
        "input_queue_capacity", "output_queue_capacity", "precision",
        "processors",         "provider_contract",    "resampling",
        "schema_id",          "worker_count"};
    as_json_doc doc;
    if (bytes == NULL || length == 0 || length > AS_MAX_CONTROL_BYTES) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config_json",
                     "effective configuration is missing or oversized");
        return AS_INVALID_ARGUMENT;
    }
    if (as_json_parse(bytes, length, &doc) != 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config_json",
                     doc.error != NULL ? doc.error
                                       : "effective configuration is invalid");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t root = 0;
    if (!exact_keys(&doc, root, top_keys,
                    (uint32_t)(sizeof(top_keys) / sizeof(top_keys[0])))) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config_json",
                     "effective configuration fields are missing or unknown");
        return AS_INVALID_ARGUMENT;
    }
    if (!string_is(&doc, root, "schema_id", "audio-sdk/effective-config/0.1")) {
        as_error_set(error, AS_INVALID_ARGUMENT, "schema_id",
                     "effective configuration schema is unsupported");
        return AS_INVALID_ARGUMENT;
    }
    if (!string_is(&doc, root, "application_contract", "audio-sdk/application/0.1")) {
        as_error_set(error, AS_INVALID_ARGUMENT, "application_contract",
                     "application contract is unsupported");
        return AS_INVALID_ARGUMENT;
    }
    if (!string_is(&doc, root, "provider_contract", AS_CONTRACT_VERSION)) {
        as_error_set(error, AS_UNSUPPORTED, "provider_contract",
                     "provider contract is unsupported");
        return AS_UNSUPPORTED;
    }
    char digest[80];
    char hex[65];
    as_hex(session->descriptor_digest, hex);
    snprintf(digest, sizeof(digest), "sha256:%s", hex);
    if (!string_is(&doc, root, "descriptor_digest", digest)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "descriptor_digest",
                     "effective configuration does not match the provider descriptor");
        return AS_INVALID_ARGUMENT;
    }
    if (!string_is(&doc, root, "engine", "reference.sequential.v0")) {
        as_error_set(error, AS_UNSUPPORTED, "engine",
                     "only reference.sequential.v0 is supported");
        return AS_UNSUPPORTED;
    }
    if (!int_is(&doc, root, "execution_mode", session->execution_mode)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "execution_mode",
                     "effective configuration mode does not match create config");
        return AS_INVALID_ARGUMENT;
    }
    const int buffered = session->execution_mode == AS_MODE_BUFFERED_WORKER;
    if (!int_is(&doc, root, "worker_count", buffered ? 1 : 0)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "worker_count",
                     "worker_count must be 0, or 1 in buffered mode");
        return AS_INVALID_ARGUMENT;
    }
    if (!int_is(&doc, root, "input_queue_capacity", buffered ? 3 : 0) ||
        !int_is(&doc, root, "output_queue_capacity", buffered ? 3 : 0)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "queue_capacity",
                     "queue capacities must be 0, or 3 in buffered mode");
        return AS_INVALID_ARGUMENT;
    }
    if (!string_is(&doc, root, "precision", "f32") ||
        !string_is(&doc, root, "adaptation", "off") ||
        !string_is(&doc, root, "resampling", "none")) {
        as_error_set(error, AS_UNSUPPORTED, "precision",
                     "v0 supports only f32, adaptation off, no resampling");
        return AS_UNSUPPORTED;
    }
    int batching = 1;
    if (as_json_get_bool(&doc, root, "batching", &batching) != 0 || batching != 0) {
        as_error_set(error, AS_UNSUPPORTED, "batching",
                     "v0 does not support batching");
        return AS_UNSUPPORTED;
    }
    const uint32_t input = as_json_get(&doc, root, "input");
    if (!exact_keys(&doc, input,
                    (const char *const[]){"channels", "frame_samples",
                                          "sample_format", "sample_rate_hz"},
                    4) ||
        !string_is(&doc, input, "sample_format", "f32") ||
        !int_is(&doc, input, "sample_rate_hz", AS_SAMPLE_RATE_HZ) ||
        !int_is(&doc, input, "channels", AS_CHANNELS) ||
        !int_is(&doc, input, "frame_samples", AS_FRAME_SAMPLES)) {
        as_error_set(error, AS_UNSUPPORTED, "input",
                     "v0 supports only f32/16000/mono/160");
        return AS_UNSUPPORTED;
    }
    const uint32_t processors = as_json_get(&doc, root, "processors");
    if (processors == AS_JSON_NO_INDEX ||
        doc.nodes[processors].type != AS_JSON_ARRAY ||
        doc.nodes[processors].child_count != 1) {
        as_error_set(error, AS_UNSUPPORTED, "processors",
                     "v0 supports exactly one provider per session");
        return AS_UNSUPPORTED;
    }
    const uint32_t processor = doc.nodes[processors].first_child;
    if (!exact_keys(&doc, processor,
                    (const char *const[]){"asset_hashes", "id", "settings"}, 3)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "processors",
                     "processor entry is incomplete or unknown");
        return AS_INVALID_ARGUMENT;
    }
    const char *text = NULL;
    uint32_t text_length = 0;
    if (as_json_get_string(&doc, processor, "id", &text, &text_length) != 0 ||
        !as_text_equal(text, text_length, session->provider_id)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "processors.id",
                     "processor ID does not match the session provider");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t hashes = as_json_get(&doc, processor, "asset_hashes");
    const uint32_t declared = as_json_get(&session->provider->descriptor_doc,
        session->provider->descriptor_root, "required_assets");
    if (hashes == AS_JSON_NO_INDEX || doc.nodes[hashes].type != AS_JSON_ARRAY ||
        declared == AS_JSON_NO_INDEX ||
        doc.nodes[hashes].child_count !=
            session->provider->descriptor_doc.nodes[declared].child_count) {
        as_error_set(error, AS_INVALID_ARGUMENT, "processors.asset_hashes",
                     "asset digest list does not match provider descriptor");
        return AS_INVALID_ARGUMENT;
    }
    uint32_t hash_item = doc.nodes[hashes].first_child;
    uint32_t asset_item = session->provider->descriptor_doc.nodes[declared].first_child;
    for (uint32_t i = 0; i < doc.nodes[hashes].child_count; ++i) {
        const char *expected_hash = NULL;
        uint32_t expected_length = 0;
        if (doc.nodes[hash_item].type != AS_JSON_STRING ||
            as_json_get_string(&session->provider->descriptor_doc, asset_item,
                               "sha256", &expected_hash, &expected_length) != 0 ||
            doc.nodes[hash_item].string_length != expected_length ||
            memcmp(doc.nodes[hash_item].string, expected_hash,
                   expected_length) != 0) {
            as_error_set(error, AS_INVALID_ARGUMENT, "processors.asset_hashes",
                         "asset digest list does not match provider descriptor");
            return AS_INVALID_ARGUMENT;
        }
        hash_item = doc.nodes[hash_item].next_sibling;
        asset_item = session->provider->descriptor_doc.nodes[asset_item].next_sibling;
    }
    const uint32_t settings = as_json_get(&doc, processor, "settings");
    if (!settings_valid(&doc, settings, session->provider_id)) {
        as_error_set(error, AS_UNSUPPORTED, "processors.settings",
                     "settings do not match the frozen provider configuration");
        return AS_UNSUPPORTED;
    }
    /* Policy strings are provider-specific and declared, not inferred. */
    const char *clip = strcmp(session->provider_id, "speex.ns.v0") == 0
                           ? "pcm16_saturation"
                           : "none";
    const char *convert = strcmp(session->provider_id, "speex.ns.v0") == 0
                              ? "speex_pcm16_lrint_clamp_div32768"
                              : "none";
    if (!string_is(&doc, root, "clipping_policy", clip) ||
        !string_is(&doc, root, "float_to_int_policy", convert)) {
        as_error_set(error, AS_UNSUPPORTED, "clipping_policy",
                     "clipping/conversion policy does not match the provider");
        return AS_UNSUPPORTED;
    }
    return AS_OK;
}
