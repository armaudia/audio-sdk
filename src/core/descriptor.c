#include "core/as_internal.h"

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

static int digest_string(const as_json_doc *doc, uint32_t object,
                         const char *field) {
    const char *text = NULL;
    uint32_t length = 0;
    if (as_json_get_string(doc, object, field, &text, &length) != 0) return 0;
    if (length != 71u || memcmp(text, "sha256:", 7) != 0) return 0;
    for (uint32_t i = 7; i < 71u; ++i) {
        const char c = text[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return 0;
    }
    return 1;
}

static int supported_format(const as_json_doc *doc, uint32_t array) {
    static const char *const keys[] = {"channels", "frame_samples", "sample_format",
                                       "sample_rate_hz"};
    if (array >= doc->node_count || doc->nodes[array].type != AS_JSON_ARRAY)
        return 0;
    if (doc->nodes[array].child_count != 1) return 0;
    const uint32_t format = doc->nodes[array].first_child;
    if (!exact_keys(doc, format, keys, 4)) return 0;
    const char *text = NULL;
    uint32_t length = 0;
    int64_t integer = 0;
    if (as_json_get_string(doc, format, "sample_format", &text, &length) != 0 ||
        !as_text_equal(text, length, "f32"))
        return 0;
    if (as_json_get_int(doc, format, "sample_rate_hz", &integer) != 0 ||
        integer != (int64_t)AS_SAMPLE_RATE_HZ)
        return 0;
    if (as_json_get_int(doc, format, "channels", &integer) != 0 ||
        integer != (int64_t)AS_CHANNELS)
        return 0;
    if (as_json_get_int(doc, format, "frame_samples", &integer) != 0 ||
        integer != (int64_t)AS_FRAME_SAMPLES)
        return 0;
    return 1;
}

static int modes_valid(const as_json_doc *doc, uint32_t array,
                       uint32_t *bitmask) {
    if (array >= doc->node_count || doc->nodes[array].type != AS_JSON_ARRAY)
        return 0;
    if (doc->nodes[array].child_count == 0) return 0;
    uint32_t mask = 0;
    int64_t previous = 0;
    uint32_t child = doc->nodes[array].first_child;
    for (uint32_t i = 0; i < doc->nodes[array].child_count; ++i) {
        const as_json_value *value = &doc->nodes[child];
        if (value->type != AS_JSON_INT) return 0;
        if (value->integer < 1 || value->integer > 3) return 0;
        if (i > 0 && value->integer <= previous) return 0;
        previous = value->integer;
        mask |= 1u << (uint32_t)value->integer;
        child = value->next_sibling;
    }
    *bitmask = mask;
    return 1;
}

as_status_v0 as_descriptor_validate(char *bytes, uint32_t length,
                                    as_provider_entry *entry,
                                    as_error_v0 *error) {
    static const char *const top_keys[] = {
        "buffering_delay_samples", "callback_safe", "configuration_schema_digest",
        "contract_version",        "edge_exclusions", "execution_modes",
        "implementation_id",       "implementation_version", "max_drain_calls",
        "native_hop_samples",      "platform",             "provider_id",
        "required_assets",         "schema_id",            "source_digest",
        "source_revision",         "supported_formats",    "upstream"};
    if (bytes == NULL || entry == NULL) {
        as_error_set(error, AS_INVALID_ARGUMENT, "descriptor", "descriptor is null");
        return AS_INVALID_ARGUMENT;
    }
    as_json_doc doc;
    if (as_json_parse(bytes, length, &doc) != 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "descriptor",
                     doc.error != NULL ? doc.error : "descriptor is not canonical JSON");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t root = 0;
    if (!exact_keys(&doc, root, top_keys, (uint32_t)(sizeof(top_keys) / sizeof(top_keys[0])))) {
        as_error_set(error, AS_INVALID_ARGUMENT, "descriptor",
                     "descriptor fields are incomplete or unknown");
        return AS_INVALID_ARGUMENT;
    }
    const char *text = NULL;
    uint32_t text_length = 0;
    int64_t integer = 0;
    if (as_json_get_string(&doc, root, "schema_id", &text, &text_length) != 0 ||
        !as_text_equal(text, text_length, "audio-sdk/descriptor/0.1")) {
        as_error_set(error, AS_INVALID_ARGUMENT, "schema_id",
                     "schema_id must be audio-sdk/descriptor/0.1");
        return AS_INVALID_ARGUMENT;
    }
    if (as_json_get_string(&doc, root, "contract_version", &text, &text_length) != 0 ||
        !as_text_equal(text, text_length, AS_CONTRACT_VERSION)) {
        as_error_set(error, AS_UNSUPPORTED, "contract_version",
                     "descriptor contract version is unsupported");
        return AS_UNSUPPORTED;
    }
    if (as_json_get_string(&doc, root, "provider_id", &text, &text_length) != 0 ||
        !as_valid_id(text, text_length)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "provider_id",
                     "provider_id must match [a-z0-9][a-z0-9._-]{0,95}");
        return AS_INVALID_ARGUMENT;
    }
    memcpy(entry->provider_id, text, text_length);
    entry->provider_id[text_length] = '\0';
    entry->provider_id_length = text_length;

    if (as_json_get_string(&doc, root, "implementation_id", &text, &text_length) != 0 ||
        text_length == 0 || text_length > AS_MAX_PROVIDER_ID) {
        as_error_set(error, AS_INVALID_ARGUMENT, "implementation_id",
                     "implementation_id is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (as_json_get_string(&doc, root, "implementation_version", &text,
                           &text_length) != 0 ||
        text_length == 0 || text_length > 64u) {
        as_error_set(error, AS_INVALID_ARGUMENT, "implementation_version",
                     "implementation_version is invalid");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t revision = as_json_get(&doc, root, "source_revision");
    if (revision == AS_JSON_NO_INDEX ||
        (doc.nodes[revision].type != AS_JSON_STRING &&
         doc.nodes[revision].type != AS_JSON_NULL)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "source_revision",
                     "source_revision must be a string or null");
        return AS_INVALID_ARGUMENT;
    }
    if (!digest_string(&doc, root, "source_digest") ||
        !digest_string(&doc, root, "configuration_schema_digest")) {
        as_error_set(error, AS_INVALID_ARGUMENT, "source_digest",
                     "digests must be sha256:<64 lowercase hex>");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t formats = as_json_get(&doc, root, "supported_formats");
    if (!supported_format(&doc, formats)) {
        as_error_set(error, AS_UNSUPPORTED, "supported_formats",
                     "v0 supports only f32/16000/mono/160");
        return AS_UNSUPPORTED;
    }
    if (as_json_get_int(&doc, root, "native_hop_samples", &integer) != 0 ||
        integer < 1 || integer > 16000) {
        as_error_set(error, AS_INVALID_ARGUMENT, "native_hop_samples",
                     "native_hop_samples must be 1..16000");
        return AS_INVALID_ARGUMENT;
    }
    entry->native_hop = (uint32_t)integer;
    if (as_json_get_int(&doc, root, "buffering_delay_samples", &integer) != 0 ||
        integer < 0 || integer > 16000) {
        as_error_set(error, AS_INVALID_ARGUMENT, "buffering_delay_samples",
                     "buffering_delay_samples must be 0..16000");
        return AS_INVALID_ARGUMENT;
    }
    entry->buffering_delay = (uint32_t)integer;
    const uint32_t exclusions = as_json_get(&doc, root, "edge_exclusions");
    if (exclusions == AS_JSON_NO_INDEX ||
        doc.nodes[exclusions].type != AS_JSON_OBJECT ||
        doc.nodes[exclusions].child_count != 2 ||
        as_json_get_int(&doc, exclusions, "start_samples", &integer) != 0 ||
        integer < 0 || integer > 16000 ||
        as_json_get_int(&doc, exclusions, "end_samples", &integer) != 0 ||
        integer < 0 || integer > 16000) {
        as_error_set(error, AS_INVALID_ARGUMENT, "edge_exclusions",
                     "edge_exclusions are invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (as_json_get_int(&doc, root, "max_drain_calls", &integer) != 0 ||
        integer < 1 || integer > (int64_t)AS_MAX_DRAIN_CALLS) {
        as_error_set(error, AS_INVALID_ARGUMENT, "max_drain_calls",
                     "max_drain_calls must be 1..1024");
        return AS_INVALID_ARGUMENT;
    }
    entry->max_drain_calls = (uint32_t)integer;
    int boolean = 0;
    if (as_json_get_bool(&doc, root, "callback_safe", &boolean) != 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "callback_safe",
                     "callback_safe must be a boolean");
        return AS_INVALID_ARGUMENT;
    }
    entry->callback_safe = boolean;
    if (!modes_valid(&doc, as_json_get(&doc, root, "execution_modes"),
                     &entry->execution_modes) ||
        entry->execution_modes == 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "execution_modes",
                     "execution_modes must be a non-empty sorted subset of 1..3");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t assets = as_json_get(&doc, root, "required_assets");
    if (assets == AS_JSON_NO_INDEX || doc.nodes[assets].type != AS_JSON_ARRAY ||
        doc.nodes[assets].child_count != 0) {
        as_error_set(error, AS_UNSUPPORTED, "required_assets",
                     "v0 providers must declare no required assets");
        return AS_UNSUPPORTED;
    }
    const uint32_t upstream = as_json_get(&doc, root, "upstream");
    if (upstream == AS_JSON_NO_INDEX ||
        doc.nodes[upstream].type != AS_JSON_OBJECT ||
        doc.nodes[upstream].child_count != 3 ||
        as_json_get_string(&doc, upstream, "name", &text, &text_length) != 0 ||
        as_json_get_string(&doc, upstream, "license", &text, &text_length) != 0 ||
        as_json_get_string(&doc, upstream, "notice_path", &text, &text_length) != 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "upstream",
                     "upstream attribution is incomplete");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t platform = as_json_get(&doc, root, "platform");
    if (platform == AS_JSON_NO_INDEX || doc.nodes[platform].type != AS_JSON_OBJECT ||
        doc.nodes[platform].child_count != 2 ||
        as_json_get_string(&doc, platform, "cpu_requirements", &text, &text_length) != 0 ||
        as_json_get(&doc, platform, "architectures") == AS_JSON_NO_INDEX ||
        doc.nodes[as_json_get(&doc, platform, "architectures")].type != AS_JSON_ARRAY ||
        doc.nodes[as_json_get(&doc, platform, "architectures")].child_count == 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "platform",
                     "platform requirements are incomplete");
        return AS_INVALID_ARGUMENT;
    }
    as_json_doc_copy(&entry->descriptor_doc, &doc);
    entry->descriptor_root = root;
    return AS_OK;
}
