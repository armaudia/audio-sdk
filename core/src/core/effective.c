/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
/*
 * Canonical effective-configuration builder.
 *
 * The emitted object is the restricted canonical JSON subset described in
 * docs/provider-v0.md: ASCII keys, byte-sorted members, safe integers, no
 * whitespace, decimal-string settings. Consumers can pass these bytes
 * directly to as_session_create_v0; the facade rejects any non-canonical or
 * semantically mismatched configuration.
 */
#include "core/as_internal.h"

#include <stdio.h>
#include <string.h>

typedef struct bw {
    char *buffer;
    uint32_t capacity;
    uint32_t length;
    int overflow;
} bw;

static void b_bytes(bw *w, const char *bytes, uint32_t length) {
    if (w->overflow) return;
    if (w->length + length + 1u > w->capacity) {
        w->overflow = 1;
        return;
    }
    memcpy(w->buffer + w->length, bytes, length);
    w->length += length;
    w->buffer[w->length] = '\0';
}

static void b_text(bw *w, const char *text) {
    b_bytes(w, text, (uint32_t)strlen(text));
}

static void b_u64(bw *w, uint64_t value) {
    char text[32];
    const int length = snprintf(text, sizeof(text), "%llu", (unsigned long long)value);
    if (length > 0) b_bytes(w, text, (uint32_t)length);
}

static void b_quote(bw *w, const char *text) {
    b_text(w, "\"");
    b_text(w, text);
    b_text(w, "\"");
}

as_status_v0 AS_CALL as_effective_config_create_v0(
    as_registry_v0 *registry, const char *provider_id,
    uint32_t provider_id_length, uint32_t execution_mode, char *buffer,
    uint32_t capacity, uint32_t *required_size, as_error_v0 *error) {
    as_error_clear(error);
    if (required_size != NULL) *required_size = 0;
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC ||
        !as_valid_id(provider_id, provider_id_length)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "provider_id",
                     "registry or provider ID is invalid");
        return AS_INVALID_ARGUMENT;
    }
    as_provider_entry *entry =
        as_registry_lookup(registry, provider_id, provider_id_length);
    if (entry == NULL) {
        as_error_set(error, AS_UNSUPPORTED, "provider_id",
                     "provider is not registered");
        return AS_UNSUPPORTED;
    }
    if (execution_mode < AS_MODE_INLINE_CALLBACK ||
        execution_mode > AS_MODE_BUFFERED_WORKER ||
        (entry->execution_modes & (1u << execution_mode)) == 0) {
        as_error_set(error, AS_UNSUPPORTED, "execution_mode",
                     "execution mode is not supported by this provider");
        return AS_UNSUPPORTED;
    }
    const int buffered = execution_mode == AS_MODE_BUFFERED_WORKER;
    const int speex = strcmp(entry->provider_id, "speex.ns.v0") == 0;
    const int highpass = strcmp(entry->provider_id, "dsp.highpass80.v0") == 0;
    char descriptor_hex[65];
    as_hex(entry->descriptor_digest, descriptor_hex);

    char text[4096];
    bw w = {text, (uint32_t)sizeof(text), 0, 0};
    text[0] = '\0';
    b_text(&w, "{\"adaptation\":\"off\",\"application_contract\":\"audio-sdk/application/0.1\",");
    b_text(&w, "\"batching\":false,\"clipping_policy\":");
    b_quote(&w, speex ? "pcm16_saturation" : "none");
    b_text(&w, ",\"descriptor_digest\":\"sha256:");
    b_text(&w, descriptor_hex);
    b_text(&w, "\",\"engine\":\"reference.sequential.v0\",\"execution_mode\":");
    b_u64(&w, execution_mode);
    b_text(&w, ",\"float_to_int_policy\":");
    b_quote(&w, speex ? "speex_pcm16_lrint_clamp_div32768" : "none");
    b_text(&w, ",\"input\":{\"channels\":1,\"frame_samples\":160,");
    b_text(&w, "\"sample_format\":\"f32\",\"sample_rate_hz\":16000},");
    b_text(&w, "\"input_queue_capacity\":");
    b_u64(&w, buffered ? 3u : 0u);
    b_text(&w, ",\"output_queue_capacity\":");
    b_u64(&w, buffered ? 3u : 0u);
    b_text(&w, ",\"precision\":\"f32\",\"processors\":[{\"asset_hashes\":[");
    const uint32_t assets = as_json_get(&entry->descriptor_doc,
                                        entry->descriptor_root,
                                        "required_assets");
    uint32_t asset = assets == AS_JSON_NO_INDEX
                         ? AS_JSON_NO_INDEX
                         : entry->descriptor_doc.nodes[assets].first_child;
    for (uint32_t i = 0; assets != AS_JSON_NO_INDEX &&
                         i < entry->descriptor_doc.nodes[assets].child_count; ++i) {
        const char *digest = NULL;
        uint32_t digest_length = 0;
        if (i != 0) b_text(&w, ",");
        if (as_json_get_string(&entry->descriptor_doc, asset, "sha256",
                               &digest, &digest_length) != 0 || digest_length != 71u) {
            as_error_set(error, AS_BACKEND_FAILURE, "required_assets",
                         "registered descriptor asset is malformed");
            return AS_BACKEND_FAILURE;
        }
        b_text(&w, "\"");
        b_bytes(&w, digest, digest_length);
        b_text(&w, "\"");
        asset = entry->descriptor_doc.nodes[asset].next_sibling;
    }
    b_text(&w, "],\"id\":");
    b_quote(&w, entry->provider_id);
    b_text(&w, ",\"settings\":");
    if (speex) {
        b_text(&w, "{\"agc\":false,\"denoise\":true,\"dereverb\":false,");
        b_text(&w, "\"suppression_db\":-20,\"vad_continue\":20,\"vad_start\":35}");
    } else if (highpass) {
        b_text(&w, "{\"cutoff_hz\":\"80\",\"q\":\"0.7071067811865476\"}");
    } else {
        b_text(&w, "{}");
    }
    b_text(&w, "}],\"provider_contract\":\"0.1\",\"resampling\":\"none\",");
    b_text(&w, "\"schema_id\":\"audio-sdk/effective-config/0.1\",\"worker_count\":");
    b_u64(&w, buffered ? 1u : 0u);
    b_text(&w, "}");

    if (required_size != NULL) *required_size = w.length + 1u;
    /* Verify the generated bytes are canonical before returning them. */
    as_json_doc doc;
    if (w.overflow || as_json_parse(text, w.length, &doc) != 0) {
        as_error_set(error, AS_BACKEND_FAILURE, "config_json",
                     "effective configuration generation failed");
        return AS_BACKEND_FAILURE;
    }
    if (buffer == NULL || capacity == 0) return AS_OK;
    if (capacity < w.length + 1u) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "buffer",
                     "buffer is too small for the configuration");
        return AS_RESOURCE_EXHAUSTED;
    }
    memcpy(buffer, text, w.length + 1u);
    return AS_OK;
}
