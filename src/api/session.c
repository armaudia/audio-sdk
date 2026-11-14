#include "core/as_internal.h"

#include <math.h>
#include <limits.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ---- small JSON writer ------------------------------------------------- */

typedef struct writer {
    char *buffer;
    uint32_t capacity;
    uint32_t length;
    int overflow;
} writer;

static void w_bytes(writer *w, const char *bytes, uint32_t length) {
    if (w->overflow) return;
    if (w->length + length + 1u > w->capacity) {
        w->overflow = 1;
        return;
    }
    memcpy(w->buffer + w->length, bytes, length);
    w->length += length;
    w->buffer[w->length] = '\0';
}

static void w_text(writer *w, const char *text) {
    w_bytes(w, text, (uint32_t)strlen(text));
}

static void w_string(writer *w, const char *text) {
    w_text(w, "\"");
    /* Configuration/descriptor IDs are ASCII; escape only JSON specials. */
    for (const char *p = text; *p != '\0'; ++p) {
        if (*p == '"' || *p == '\\') {
            char escape[2] = {'\\', *p};
            w_bytes(w, escape, 2);
        } else {
            w_bytes(w, p, 1);
        }
    }
    w_text(w, "\"");
}

static void w_u64(writer *w, uint64_t value) {
    char text[32];
    const int length = snprintf(text, sizeof(text), "%llu", (unsigned long long)value);
    if (length > 0) w_bytes(w, text, (uint32_t)length);
}

static void w_key(writer *w, const char *key) {
    w_string(w, key);
    w_text(w, ":");
}

static void w_q_u64(writer *w, uint64_t value) {
    w_text(w, "\"");
    w_u64(w, value);
    w_text(w, "\"");
}

static const char *lifecycle_name(int lifecycle) {
    switch (lifecycle) {
        case AS_LIFE_PREPARED: return "prepared";
        case AS_LIFE_PROCESSING: return "processing";
        case AS_LIFE_DRAINING: return "draining";
        case AS_LIFE_DRAINED: return "drained";
        case AS_LIFE_NEEDS_RESET: return "needs_reset";
        case AS_LIFE_CLOSED: return "closed";
        default: return "unknown";
    }
}

/* ---- call admission ---------------------------------------------------- */

static int enter_call(as_session_v0 *session) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC) return 0;
    atomic_fetch_add(&session->active_calls, 1u);
    if (atomic_load(&session->closing) || atomic_load(&session->reset_flag)) {
        atomic_fetch_sub(&session->active_calls, 1u);
        return 0;
    }
    return 1;
}

static void exit_call(as_session_v0 *session) {
    atomic_fetch_sub(&session->active_calls, 1u);
}

static int enter_exclusive(as_session_v0 *session) {
    if (!enter_call(session)) return 0;
    int expected = 0;
    if (!atomic_compare_exchange_strong(&session->audio_guard, &expected, 1)) {
        exit_call(session);
        return 0;
    }
    if (atomic_load(&session->closing)) {
        atomic_store(&session->audio_guard, 0);
        exit_call(session);
        return 0;
    }
    return 1;
}

static void exit_exclusive(as_session_v0 *session) {
    atomic_store(&session->audio_guard, 0);
    exit_call(session);
}

/* ---- validation helpers ------------------------------------------------ */

static int result_ready(const as_result_v0 *result) {
    if (result == NULL ||
        !as_valid_struct(result->struct_size, result->abi_major,
                         result->abi_minor, (uint32_t)sizeof(*result)) ||
        !as_tail_is_zero(result, (uint32_t)sizeof(*result),
                         result->struct_size))
        return 0;
    return result->reserved[0] == 0 && result->reserved[1] == 0 &&
           result->reserved[2] == 0;
}

static void reset_result(as_result_v0 *result, as_status_v0 status,
                         const as_session_v0 *session) {
    if (result == NULL) return;
    as_result_v0_init(result);
    result->status = status;
    if (session != NULL) result->epoch = session->epoch;
}

static int output_ready(const as_output_v0 *output, const void *input,
                        uint32_t input_samples) {
    if (output == NULL || output->samples == NULL ||
        output->capacity < AS_FRAME_SAMPLES || output->reserved0 != 0 ||
        !as_valid_struct(output->struct_size, output->abi_major,
                         output->abi_minor, (uint32_t)sizeof(*output)) ||
        !as_tail_is_zero(output, (uint32_t)sizeof(*output),
                         output->struct_size))
        return 0;
    if (((uintptr_t)output->samples % sizeof(float)) != 0) return 0;
    if (input != NULL) {
        const uintptr_t a = (uintptr_t)input;
        const uintptr_t b = (uintptr_t)output->samples;
        const uintptr_t a_bytes = (uintptr_t)input_samples * sizeof(float);
        const uintptr_t b_bytes = (uintptr_t)output->capacity * sizeof(float);
        if (a < b + b_bytes && b < a + a_bytes) return 0;
    }
    return 1;
}

static int frame_ready(const as_session_v0 *session, const as_frame_v0 *frame,
                       as_status_v0 *status, const char **message) {
    if (frame == NULL || frame->input == NULL) {
        *status = AS_INVALID_ARGUMENT;
        *message = "frame or input pointer is null";
        return 0;
    }
    if (frame->struct_size < sizeof(*frame) || frame->abi_major != AS_ABI_MAJOR ||
        frame->abi_minor != AS_ABI_MINOR || frame->reserved0 != 0 ||
        !as_tail_is_zero(frame, (uint32_t)sizeof(*frame), frame->struct_size)) {
        *status = AS_INVALID_ARGUMENT;
        *message = "frame header is invalid";
        return 0;
    }
    if (((uintptr_t)frame->input % sizeof(float)) != 0) {
        *status = AS_INVALID_ARGUMENT;
        *message = "input is not aligned for float32";
        return 0;
    }
    if (frame->input_count != AS_FRAME_SAMPLES) {
        *status = AS_INVALID_ARGUMENT;
        *message = "input_count must be 160";
        return 0;
    }
    if (frame->first_input_sample < 0 ||
        frame->first_input_sample >
            INT64_MAX - (int64_t)AS_FRAME_SAMPLES) {
        *status = AS_INVALID_ARGUMENT;
        *message = "input sample interval exceeds int64 coordinates";
        return 0;
    }
    if ((frame->flags & ~AS_FRAME_FINAL_INPUT) != 0) {
        *status = AS_INVALID_ARGUMENT;
        *message = "unknown frame flags";
        return 0;
    }
    const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    if (frame->input_valid_count == 0 || frame->input_valid_count > AS_FRAME_SAMPLES) {
        *status = AS_INVALID_ARGUMENT;
        *message = "input_valid_count must be 1..160";
        return 0;
    }
    if (!final && frame->input_valid_count != AS_FRAME_SAMPLES) {
        *status = AS_INVALID_ARGUMENT;
        *message = "a partial frame requires the FINAL_INPUT flag";
        return 0;
    }
    for (uint32_t i = 0; i < AS_FRAME_SAMPLES; ++i) {
        if (!isfinite(frame->input[i])) {
            *status = AS_INVALID_ARGUMENT;
            *message = "input contains a nonfinite sample";
            return 0;
        }
    }
    if (final) {
        for (uint32_t i = frame->input_valid_count; i < AS_FRAME_SAMPLES; ++i) {
            if (frame->input[i] != 0.0f) {
                *status = AS_INVALID_ARGUMENT;
                *message = "final-frame padding must be zero";
                return 0;
            }
        }
    }
    if (frame->epoch != session->epoch) {
        *status = AS_INVALID_ARGUMENT;
        *message = "frame epoch is stale or unknown";
        return 0;
    }
    if (frame->first_input_sample != session->next_input_sample) {
        *status = AS_INVALID_ARGUMENT;
        *message = "frame does not start at the next expected input sample";
        return 0;
    }
    return 1;
}

static int worker_atomics_are_lock_free(as_session_v0 *session) {
    return atomic_is_lock_free(&session->active_calls) &&
           atomic_is_lock_free(&session->closing) &&
           atomic_is_lock_free(&session->reset_flag) &&
           atomic_is_lock_free(&session->lifecycle) &&
           atomic_is_lock_free(&session->admission_closed) &&
           atomic_is_lock_free(&session->drain_complete) &&
           atomic_is_lock_free(&session->accepted_end) &&
           atomic_is_lock_free(&session->input_read) &&
           atomic_is_lock_free(&session->input_write) &&
           atomic_is_lock_free(&session->output_read) &&
           atomic_is_lock_free(&session->output_write) &&
           atomic_is_lock_free(&session->input_high_water) &&
           atomic_is_lock_free(&session->output_high_water) &&
           atomic_is_lock_free(&session->c_submitted_valid) &&
           atomic_is_lock_free(&session->c_accepted_valid) &&
           atomic_is_lock_free(&session->c_rejected_valid) &&
           atomic_is_lock_free(&session->c_delivered_valid);
}

/* ---- argument validation for create ------------------------------------ */

static as_status_v0 validate_create_config(const as_registry_v0 *registry,
                                           const as_provider_entry *entry,
                                           const as_create_config_v0 *config,
                                           as_error_v0 *error) {
    if (!as_valid_struct(config->struct_size, config->abi_major, config->abi_minor,
                         (uint32_t)sizeof(*config)) ||
        !as_tail_is_zero(config, (uint32_t)sizeof(*config), config->struct_size)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config",
                     "create config header is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (config->reserved0 != 0 || config->reserved1 != 0 ||
        config->reserved[0] != 0 || config->reserved[1] != 0 ||
        config->reserved[2] != 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config.reserved",
                     "reserved create-config fields must be zero");
        return AS_INVALID_ARGUMENT;
    }
    if (config->sample_rate_hz != AS_SAMPLE_RATE_HZ ||
        config->channels != AS_CHANNELS || config->frame_samples != AS_FRAME_SAMPLES) {
        as_error_set(error, AS_UNSUPPORTED, "format",
                     "v0 supports only f32/16000/mono/160");
        return AS_UNSUPPORTED;
    }
    if (config->execution_mode < AS_MODE_INLINE_CALLBACK ||
        config->execution_mode > AS_MODE_BUFFERED_WORKER ||
        (entry->execution_modes & (1u << config->execution_mode)) == 0) {
        as_error_set(error, AS_UNSUPPORTED, "execution_mode",
                     "execution mode is not supported by this provider");
        return AS_UNSUPPORTED;
    }
    if (config->execution_mode == AS_MODE_INLINE_CALLBACK && !entry->callback_safe) {
        as_error_set(error, AS_UNSUPPORTED, "execution_mode",
                     "provider is not declared callback-safe");
        return AS_UNSUPPORTED;
    }
    if (config->first_input_sample < 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "first_input_sample",
                     "first_input_sample must be nonnegative");
        return AS_INVALID_ARGUMENT;
    }
    if (config->asset_count > AS_MAX_ASSETS ||
        (config->asset_count > 0 && config->assets == NULL)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "assets",
                     "asset array is invalid");
        return AS_INVALID_ARGUMENT;
    }
    const uint32_t declared = as_json_get(&entry->descriptor_doc,
                                           entry->descriptor_root,
                                           "required_assets");
    if (declared == AS_JSON_NO_INDEX ||
        config->asset_count != entry->descriptor_doc.nodes[declared].child_count) {
        as_error_set(error, AS_INVALID_ARGUMENT, "assets",
                     "supplied assets do not match the descriptor asset count");
        return AS_INVALID_ARGUMENT;
    }
    uint32_t expected = entry->descriptor_doc.nodes[declared].first_child;
    for (uint32_t i = 0; i < config->asset_count; ++i) {
        const as_asset_v0 *asset = &config->assets[i];
        const char *id = NULL, *digest = NULL;
        uint32_t id_length = 0, digest_length = 0;
        int64_t byte_count = -1;
        if (as_json_get_string(&entry->descriptor_doc, expected, "id", &id,
                               &id_length) != 0 ||
            as_json_get_string(&entry->descriptor_doc, expected, "sha256", &digest,
                               &digest_length) != 0 || digest_length != 71u ||
            as_json_get_int(&entry->descriptor_doc, expected, "byte_count",
                            &byte_count) != 0 ||
            !as_valid_struct(asset->struct_size, asset->abi_major,
                             asset->abi_minor, (uint32_t)sizeof(*asset)) ||
            asset->asset_id == NULL || asset->asset_id_length != id_length ||
            memcmp(asset->asset_id, id, id_length) != 0 ||
            asset->byte_count != (uint64_t)byte_count) {
            as_error_set(error, AS_INVALID_ARGUMENT, "assets",
                         "asset ID or size does not match the provider descriptor");
            return AS_INVALID_ARGUMENT;
        }
        for (uint32_t b = 0; b < 32; ++b) {
            unsigned int value = 0;
            if (sscanf(digest + 7u + 2u * b, "%2x", &value) != 1 ||
                asset->sha256[b] != (uint8_t)value) {
                as_error_set(error, AS_INVALID_ARGUMENT, "assets.sha256",
                             "asset digest does not match the provider descriptor");
                return AS_INVALID_ARGUMENT;
            }
        }
        expected = entry->descriptor_doc.nodes[expected].next_sibling;
    }
    if (config->config_json == NULL || config->config_json_length == 0 ||
        config->config_json_length > AS_MAX_CONTROL_BYTES) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config_json",
                     "canonical effective configuration is missing");
        return AS_INVALID_ARGUMENT;
    }
    (void)registry;
    return AS_OK;
}

static as_status_v0 copy_assets(as_session_v0 *session,
                                const as_create_config_v0 *config,
                                as_asset_v0 *resolved_assets,
                                as_error_v0 *error) {
    uint64_t total = 0;
    for (uint32_t i = 0; i < config->asset_count; ++i) {
        const as_asset_v0 *asset = &config->assets[i];
        if (!as_valid_struct(asset->struct_size, asset->abi_major, asset->abi_minor,
                             (uint32_t)sizeof(*asset)) ||
            asset->reserved0 != 0 || asset->data == NULL ||
            !as_valid_id(asset->asset_id, asset->asset_id_length) ||
            asset->asset_id_length >= sizeof(session->asset_ids[i])) {
            as_error_set(error, AS_INVALID_ARGUMENT, "assets",
                         "asset header or ID is invalid");
            return AS_INVALID_ARGUMENT;
        }
        uint8_t digest[32];
        as_sha256(asset->data, (size_t)asset->byte_count, digest);
        if (memcmp(digest, asset->sha256, 32) != 0) {
            as_error_set(error, AS_INVALID_ARGUMENT, "assets.sha256",
                         "asset digest does not match its bytes");
            return AS_INVALID_ARGUMENT;
        }
        if (asset->byte_count > AS_MAX_ASSET_BYTES - total) {
            as_error_set(error, AS_RESOURCE_EXHAUSTED, "assets",
                         "asset total exceeds 512 MiB");
            return AS_RESOURCE_EXHAUSTED;
        }
        total += asset->byte_count;
        void *copy = malloc((size_t)asset->byte_count == 0 ? 1
                                                           : (size_t)asset->byte_count);
        if (copy == NULL) {
            as_error_set(error, AS_RESOURCE_EXHAUSTED, "assets",
                         "asset allocation failed");
            return AS_RESOURCE_EXHAUSTED;
        }
        memcpy(copy, asset->data, (size_t)asset->byte_count);
        session->asset_data[i] = copy;
        session->asset_bytes[i] = asset->byte_count;
        memcpy(session->asset_ids[i], asset->asset_id, asset->asset_id_length);
        session->asset_ids[i][asset->asset_id_length] = '\0';
        resolved_assets[i] = *asset;
        resolved_assets[i].asset_id = session->asset_ids[i];
        resolved_assets[i].data = copy;
    }
    session->asset_count = config->asset_count;
    return AS_OK;
}

static void release_session(as_session_v0 *session) {
    if (session->instance != NULL && session->table.destroy != NULL) {
        session->table.destroy(session->instance);
        session->instance = NULL;
    }
    for (uint32_t i = 0; i < session->asset_count; ++i) free(session->asset_data[i]);
    if (session->sync_ready) {
        pthread_mutex_destroy(&session->control_mutex);
        pthread_mutex_destroy(&session->queue_mutex);
        pthread_cond_destroy(&session->queue_cond);
    }
    session->magic = 0;
    free(session);
}

static void account_queued_cancellation(as_session_v0 *session) {
    uint64_t intervals = 0;
    uint64_t samples = 0;
    const uint32_t input_read = atomic_load(&session->input_read);
    const uint32_t input_write = atomic_load(&session->input_write);
    for (uint32_t cursor = input_read; cursor != input_write; ++cursor) {
        const as_frame_slot *slot =
            &session->input_queue[cursor % AS_QUEUE_FRAMES];
        if (slot->valid_count > 0) {
            intervals++;
            samples += slot->valid_count;
        }
    }
    const uint32_t output_read = atomic_load(&session->output_read);
    const uint32_t output_write = atomic_load(&session->output_write);
    for (uint32_t cursor = output_read; cursor != output_write; ++cursor) {
        const as_output_slot *slot =
            &session->output_queue[cursor % AS_QUEUE_FRAMES];
        if (slot->result.valid_count > 0) {
            intervals++;
            samples += slot->result.valid_count;
        }
    }
    atomic_fetch_add(&session->c_cancelled_intervals, intervals);
    atomic_fetch_add(&session->c_cancelled_valid, samples);
}

/* ---- create/close ------------------------------------------------------ */

as_status_v0 AS_CALL as_session_create_v0(as_registry_v0 *registry,
                                          const char *provider_id,
                                          uint32_t provider_id_length,
                                          const as_create_config_v0 *config,
                                          as_session_v0 **out,
                                          as_error_v0 *error) {
    as_error_clear(error);
    if (out == NULL) {
        as_error_set(error, AS_INVALID_ARGUMENT, "out", "out is null");
        return AS_INVALID_ARGUMENT;
    }
    *out = NULL;
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC) {
        as_error_set(error, AS_INVALID_ARGUMENT, "registry", "registry is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (config == NULL) {
        as_error_set(error, AS_INVALID_ARGUMENT, "config", "config is null");
        return AS_INVALID_ARGUMENT;
    }
    if (!as_valid_id(provider_id, provider_id_length)) {
        as_error_set(error, AS_INVALID_ARGUMENT, "provider_id",
                     "provider_id must match [a-z0-9][a-z0-9._-]{0,95}");
        return AS_INVALID_ARGUMENT;
    }
    as_provider_entry *entry =
        as_registry_lookup(registry, provider_id, provider_id_length);
    if (entry == NULL) {
        as_error_set(error, AS_UNSUPPORTED, "provider_id",
                     "provider is not registered");
        return AS_UNSUPPORTED;
    }
    as_status_v0 status = validate_create_config(registry, entry, config, error);
    if (status != AS_OK) return status;

    as_session_v0 *session = (as_session_v0 *)calloc(1, sizeof(*session));
    if (session == NULL) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "session",
                     "session allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    session->magic = AS_SESSION_MAGIC;
    session->registry = registry;
    session->provider = entry;
    session->table = entry->table;
    session->execution_mode = config->execution_mode;
    session->sample_rate_hz = config->sample_rate_hz;
    session->channels = config->channels;
    session->frame_samples = config->frame_samples;
    session->buffering_delay = entry->buffering_delay;
    session->native_hop = entry->native_hop;
    session->max_drain_calls = entry->max_drain_calls;
    session->epoch = config->epoch;
    session->first_input_sample = config->first_input_sample;
    session->next_input_sample = config->first_input_sample;
    session->accepted_end = config->first_input_sample;
    session->next_output_sample =
        config->first_input_sample - (int64_t)session->buffering_delay;
    session->provider_id_length = entry->provider_id_length;
    memcpy(session->provider_id, entry->provider_id, entry->provider_id_length + 1u);
    memcpy(session->descriptor_digest, entry->descriptor_digest, 32);
    memcpy(session->config_json, config->config_json, config->config_json_length);
    session->config_json[config->config_json_length] = '\0';
    session->config_json_length = config->config_json_length;
    as_sha256(config->config_json, config->config_json_length, session->config_digest);
    {
        int64_t edge = 0;
        const uint32_t exclusions =
            as_json_get(&entry->descriptor_doc, entry->descriptor_root,
                        "edge_exclusions");
        if (exclusions != AS_JSON_NO_INDEX) {
            if (as_json_get_int(&entry->descriptor_doc, exclusions, "start_samples",
                                &edge) == 0 && edge >= 0)
                session->edge_start = (uint32_t)edge;
            if (as_json_get_int(&entry->descriptor_doc, exclusions, "end_samples",
                                &edge) == 0 && edge >= 0)
                session->edge_end = (uint32_t)edge;
        }
    }
    if (pthread_mutex_init(&session->control_mutex, NULL) != 0 ||
        pthread_mutex_init(&session->queue_mutex, NULL) != 0 ||
        pthread_cond_init(&session->queue_cond, NULL) != 0) {
        release_session(session);
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "session",
                     "session synchronization initialization failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    session->sync_ready = 1;
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER &&
        !worker_atomics_are_lock_free(session)) {
        release_session(session);
        as_error_set(error, AS_UNSUPPORTED, "execution_mode",
                     "buffered mode requires lock-free callback atomics");
        return AS_UNSUPPORTED;
    }
    status = as_effective_config_validate(session, config->config_json,
                                          config->config_json_length, error);
    if (status != AS_OK) {
        release_session(session);
        return status;
    }
    as_asset_v0 assets[AS_MAX_ASSETS];
    memset(assets, 0, sizeof(assets));
    status = copy_assets(session, config, assets, error);
    if (status != AS_OK) {
        release_session(session);
        return status;
    }
    as_create_config_v0 resolved = *config;
    resolved.config_json = session->config_json;
    resolved.config_json_length = session->config_json_length;
    resolved.assets = config->asset_count > 0 ? assets : NULL;
    void *instance = NULL;
    status = session->table.create(&resolved, &instance, error);
    if (status != AS_OK || instance == NULL) {
        if (status == AS_OK) {
            status = AS_BACKEND_FAILURE;
            as_error_set(error, status, "provider", "provider create failed");
        }
        release_session(session);
        return status;
    }
    session->instance = instance;
    atomic_store(&session->lifecycle, AS_LIFE_PREPARED);
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        status = as_worker_start(session, error);
        if (status != AS_OK) {
            release_session(session);
            return status;
        }
    }
    pthread_mutex_lock(&registry->lock);
    registry->frozen = 1;
    pthread_mutex_unlock(&registry->lock);
    atomic_fetch_add(&registry->session_count, 1u);
    *out = session;
    return AS_OK;
}

as_status_v0 AS_CALL as_session_close_v0(as_session_v0 **session) {
    if (session == NULL || *session == NULL) return AS_OK;
    as_session_v0 *self = *session;
    if (self->magic != AS_SESSION_MAGIC) return AS_INVALID_ARGUMENT;
    atomic_store(&self->closing, 1);
    /* Stop new callbacks and wait for in-flight ones (control thread). */
    const struct timespec pause = {0, 1000000L};
    uint64_t waited_ns = 0;
    while (atomic_load(&self->active_calls) != 0u) {
        nanosleep(&pause, NULL);
        waited_ns += 1000000u;
        if (waited_ns > 5000000000ull) return AS_BUSY;
    }
    if (self->worker_started) {
        as_worker_stop(self);
        self->worker_started = 0;
    }
    if (self->execution_mode == AS_MODE_BUFFERED_WORKER)
        account_queued_cancellation(self);
    as_registry_v0 *registry = self->registry;
    atomic_store(&self->lifecycle, AS_LIFE_CLOSED);
    release_session(self);
    if (registry != NULL) atomic_fetch_sub(&registry->session_count, 1u);
    *session = NULL;
    return AS_OK;
}

/* ---- inline processing ------------------------------------------------- */

as_status_v0 AS_CALL as_session_process_v0(as_session_v0 *session,
                                           const as_frame_v0 *frame,
                                           const as_output_v0 *output,
                                           as_result_v0 *result) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    if (!result_ready(result)) return AS_INVALID_ARGUMENT;
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        reset_result(result, AS_UNSUPPORTED, session);
        return AS_UNSUPPORTED;
    }
    if (!enter_exclusive(session)) {
        reset_result(result, AS_BUSY, session);
        return AS_BUSY;
    }
    as_status_v0 status = AS_OK;
    const char *message = NULL;
    const int lifecycle = atomic_load(&session->lifecycle);
    if (lifecycle == AS_LIFE_NEEDS_RESET) {
        status = AS_NEEDS_RESET;
        message = "session requires reset";
    } else if (lifecycle == AS_LIFE_DRAINING || lifecycle == AS_LIFE_DRAINED ||
               lifecycle == AS_LIFE_CLOSED) {
        status = AS_INVALID_ARGUMENT;
        message = "process is not admissible after drain";
    } else if (session->admission_closed) {
        status = AS_INVALID_ARGUMENT;
        message = "input was already marked final";
    } else if (!frame_ready(session, frame, &status, &message)) {
        /* status/message set by the validator */
    } else if (!output_ready(output, frame->input, AS_FRAME_SAMPLES)) {
        status = AS_INVALID_ARGUMENT;
        message = "output is invalid, misaligned, too small or overlaps input";
    }
    if (status != AS_OK) {
        reset_result(result, status, session);
        exit_exclusive(session);
        (void)message;
        return status;
    }

    const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
    const int64_t accepted_end =
        frame->first_input_sample + (int64_t)(final ? frame->input_valid_count
                                                    : AS_FRAME_SAMPLES);
    as_status_v0 call = as_provider_process_frame(session, frame, output, result);
    if (call == AS_OK) {
        as_compute_validity(session, result->source_first_sample,
                            result->produced_count, result->valid_offset,
                            result->valid_count, accepted_end,
                            final ? AS_RESULT_FINAL_PADDING : 0u, result);
        result->status = AS_OK;
        result->consumed_count = AS_FRAME_SAMPLES;
        result->epoch = session->epoch;
        session->next_output_sample =
            result->source_first_sample + (int64_t)result->produced_count;
        session->accepted_end = accepted_end;
        session->next_input_sample = frame->first_input_sample + AS_FRAME_SAMPLES;
        if (final) session->admission_closed = 1;
        atomic_fetch_add(&session->c_submitted_valid, frame->input_valid_count);
        atomic_fetch_add(&session->c_accepted_valid, frame->input_valid_count);
        atomic_fetch_add(&session->c_produced_valid, result->valid_count);
        atomic_fetch_add(&session->c_delivered_valid, result->valid_count);
        uint32_t startup_padding = 0;
        uint32_t final_padding = 0;
        as_compute_padding_counts(session, result->source_first_sample,
                                  result->produced_count, accepted_end, final,
                                  &startup_padding, &final_padding);
        atomic_fetch_add(&session->c_startup_padding, startup_padding);
        atomic_fetch_add(&session->c_final_padding, final_padding);
        atomic_store(&session->lifecycle, AS_LIFE_PROCESSING);
        result->queue_depth = 0;
    } else {
        reset_result(result, call, session);
        atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
    }
    exit_exclusive(session);
    return call;
}

/* ---- drain ------------------------------------------------------------- */

as_status_v0 AS_CALL as_session_begin_drain_v0(as_session_v0 *session) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    if (!enter_exclusive(session)) return AS_BUSY;
    const int lifecycle = atomic_load(&session->lifecycle);
    as_status_v0 status = AS_OK;
    if (lifecycle == AS_LIFE_DRAINED) {
        status = AS_END_OF_STREAM;
    } else if (lifecycle == AS_LIFE_DRAINING) {
        status = AS_OK;
    } else if (lifecycle == AS_LIFE_PREPARED || lifecycle == AS_LIFE_PROCESSING) {
        if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
            pthread_mutex_lock(&session->queue_mutex);
            session->admission_closed = 1;
            if (session->next_input_sample > session->accepted_end)
                session->accepted_end = session->next_input_sample;
            pthread_cond_broadcast(&session->queue_cond);
            pthread_mutex_unlock(&session->queue_mutex);
        } else {
            /* accepted_end already excludes any zero-padded final-frame tail. */
        }
        atomic_store(&session->lifecycle, AS_LIFE_DRAINING);
    } else {
        status = AS_NEEDS_RESET;
    }
    exit_exclusive(session);
    return status;
}

as_status_v0 AS_CALL as_session_drain_next_v0(as_session_v0 *session,
                                              const as_output_v0 *output,
                                              as_result_v0 *result) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    if (!result_ready(result)) return AS_INVALID_ARGUMENT;
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        return as_session_pull_v0(session, output, result);
    }
    if (!output_ready(output, NULL, 0)) {
        reset_result(result, AS_INVALID_ARGUMENT, session);
        return AS_INVALID_ARGUMENT;
    }
    if (!enter_exclusive(session)) {
        reset_result(result, AS_BUSY, session);
        return AS_BUSY;
    }
    as_status_v0 status = AS_OK;
    for (;;) {
        const int lifecycle = atomic_load(&session->lifecycle);
        if (lifecycle == AS_LIFE_NEEDS_RESET) {
            status = AS_NEEDS_RESET;
            reset_result(result, status, session);
            break;
        }
        if (lifecycle == AS_LIFE_DRAINED) {
            status = AS_END_OF_STREAM;
            reset_result(result, status, session);
            break;
        }
        if (lifecycle != AS_LIFE_DRAINING) {
            status = AS_INVALID_ARGUMENT;
            reset_result(result, status, session);
            break;
        }
        if (session->drain_calls >= session->max_drain_calls) {
            atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
            atomic_fetch_add(&session->c_backend_failures, 1u);
            status = AS_BACKEND_FAILURE;
            reset_result(result, status, session);
            break;
        }
        session->drain_calls++;
        as_status_v0 call = as_drain_provider_frame(session, output, result);
        if (call == AS_END_OF_STREAM) {
            atomic_store(&session->lifecycle, AS_LIFE_DRAINED);
            status = AS_END_OF_STREAM;
            reset_result(result, status, session);
            break;
        }
        if (call != AS_OK) {
            atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
            status = call;
            reset_result(result, status, session);
            break;
        }
        as_compute_validity(session, result->source_first_sample,
                            result->produced_count, result->valid_offset,
                            result->valid_count, session->accepted_end,
                            AS_RESULT_FINAL_PADDING, result);
        result->status = AS_OK;
        result->consumed_count = 0;
        result->epoch = session->epoch;
        result->queue_depth = 0;
        if (result->valid_count > 0) {
            atomic_fetch_add(&session->c_produced_valid, result->valid_count);
            atomic_fetch_add(&session->c_delivered_valid, result->valid_count);
            atomic_fetch_add(&session->c_drain_frames, 1u);
            uint32_t final_padding = 0;
            as_compute_padding_counts(
                session, result->source_first_sample, result->produced_count,
                session->accepted_end, 1, NULL, &final_padding);
            atomic_fetch_add(&session->c_final_padding, final_padding);
            status = AS_OK;
            break;
        }
    }
    exit_exclusive(session);
    return status;
}

/* ---- buffered submit/pull --------------------------------------------- */

as_status_v0 AS_CALL as_session_submit_v0(as_session_v0 *session,
                                          const as_frame_v0 *frame,
                                          as_result_v0 *acceptance) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    if (!result_ready(acceptance)) return AS_INVALID_ARGUMENT;
    if (session->execution_mode != AS_MODE_BUFFERED_WORKER) {
        reset_result(acceptance, AS_UNSUPPORTED, session);
        return AS_UNSUPPORTED;
    }
    if (!enter_call(session)) {
        reset_result(acceptance, AS_CLOSED, session);
        return AS_CLOSED;
    }
    as_status_v0 status = AS_OK;
    const char *message = NULL;
    const int lifecycle = atomic_load(&session->lifecycle);
    if (lifecycle == AS_LIFE_NEEDS_RESET) {
        status = AS_NEEDS_RESET;
    } else if (lifecycle != AS_LIFE_PREPARED && lifecycle != AS_LIFE_PROCESSING) {
        status = AS_INVALID_ARGUMENT;
    } else if (!frame_ready(session, frame, &status, &message)) {
        /* validator set status */
    }
    if (status == AS_OK) {
        if (session->admission_closed) {
            status = AS_INVALID_ARGUMENT;
        } else {
            const uint32_t write =
                atomic_load_explicit(&session->input_write,
                                     memory_order_relaxed);
            const uint32_t read =
                atomic_load_explicit(&session->input_read,
                                     memory_order_acquire);
            if (write - read >= AS_QUEUE_FRAMES) {
                status = AS_RESOURCE_EXHAUSTED;
            } else {
                const uint32_t index = write % AS_QUEUE_FRAMES;
                as_frame_slot *slot = &session->input_queue[index];
                memcpy(slot->samples, frame->input, sizeof(slot->samples));
                slot->valid_count = frame->input_valid_count;
                slot->flags = frame->flags;
                slot->epoch = frame->epoch;
                slot->first_input_sample = frame->first_input_sample;
                const int final = (frame->flags & AS_FRAME_FINAL_INPUT) != 0;
                slot->accepted_end_after =
                    frame->first_input_sample +
                    (int64_t)(final ? frame->input_valid_count
                                    : AS_FRAME_SAMPLES);
                session->accepted_end = slot->accepted_end_after;
                session->next_input_sample =
                    frame->first_input_sample + AS_FRAME_SAMPLES;
                if (final) session->admission_closed = 1;
                atomic_store_explicit(&session->input_write, write + 1u,
                                      memory_order_release);
                const uint32_t depth = write + 1u - read;
                const uint32_t high = atomic_load_explicit(
                    &session->input_high_water, memory_order_relaxed);
                if (depth > high)
                    atomic_store_explicit(&session->input_high_water, depth,
                                          memory_order_relaxed);
                atomic_fetch_add(&session->c_submitted_valid,
                                 frame->input_valid_count);
                atomic_fetch_add(&session->c_accepted_valid,
                                 frame->input_valid_count);
                atomic_store(&session->lifecycle, AS_LIFE_PROCESSING);
            }
        }
    }
    if (status == AS_OK) {
        reset_result(acceptance, AS_OK, session);
        acceptance->consumed_count = AS_FRAME_SAMPLES;
        acceptance->source_first_sample = frame->first_input_sample;
    } else {
        if (status == AS_RESOURCE_EXHAUSTED) {
            atomic_fetch_add(&session->c_rejected_valid, frame->input_valid_count);
        }
        reset_result(acceptance, status, session);
    }
    exit_call(session);
    return status;
}

as_status_v0 AS_CALL as_session_pull_v0(as_session_v0 *session,
                                        const as_output_v0 *output,
                                        as_result_v0 *result) {
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    if (!result_ready(result)) return AS_INVALID_ARGUMENT;
    if (session->execution_mode != AS_MODE_BUFFERED_WORKER) {
        reset_result(result, AS_UNSUPPORTED, session);
        return AS_UNSUPPORTED;
    }
    if (!output_ready(output, NULL, 0)) {
        reset_result(result, AS_INVALID_ARGUMENT, session);
        return AS_INVALID_ARGUMENT;
    }
    if (!enter_call(session)) {
        reset_result(result, AS_CLOSED, session);
        return AS_CLOSED;
    }
    as_status_v0 status = AS_NOT_READY;
    const int lifecycle = atomic_load(&session->lifecycle);
    if (lifecycle == AS_LIFE_NEEDS_RESET) {
        status = AS_NEEDS_RESET;
    } else {
        const uint32_t read =
            atomic_load_explicit(&session->output_read, memory_order_relaxed);
        const uint32_t write =
            atomic_load_explicit(&session->output_write, memory_order_acquire);
        if (read != write) {
        as_output_slot *slot =
            &session->output_queue[read % AS_QUEUE_FRAMES];
        memcpy(output->samples, slot->samples, sizeof(slot->samples));
        *result = slot->result;
        atomic_store_explicit(&session->output_read, read + 1u,
                              memory_order_release);
        status = AS_OK;
        atomic_fetch_add(&session->c_delivered_valid, result->valid_count);
        } else if (session->drain_complete) {
            status = AS_END_OF_STREAM;
            atomic_store(&session->lifecycle, AS_LIFE_DRAINED);
        }
    }
    if (status == AS_END_OF_STREAM || status == AS_NEEDS_RESET) {
        reset_result(result, status, session);
    } else if (status == AS_NOT_READY) {
        reset_result(result, AS_NOT_READY, session);
    }
    exit_call(session);
    return status;
}

/* ---- reset ------------------------------------------------------------- */

as_status_v0 AS_CALL as_session_reset_v0(as_session_v0 *session, uint64_t epoch,
                                         int64_t first_input_sample,
                                         as_error_v0 *error) {
    as_error_clear(error);
    if (session == NULL || session->magic != AS_SESSION_MAGIC) {
        as_error_set(error, AS_INVALID_ARGUMENT, "session", "session is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (!enter_exclusive(session)) {
        as_error_set(error, AS_BUSY, "session", "session is busy");
        return AS_BUSY;
    }
    as_status_v0 status = AS_OK;
    if (epoch <= session->epoch) {
        as_error_set(error, AS_INVALID_ARGUMENT, "epoch",
                     "reset epoch must be strictly greater");
        status = AS_INVALID_ARGUMENT;
    } else if (first_input_sample < 0) {
        as_error_set(error, AS_INVALID_ARGUMENT, "first_input_sample",
                     "first_input_sample must be nonnegative");
        status = AS_INVALID_ARGUMENT;
    }
    if (status != AS_OK) {
        exit_exclusive(session);
        return status;
    }
    atomic_store(&session->reset_flag, 1);
    /* Wait for in-flight submit/pull calls to leave (reset is quiesced). */
    const struct timespec pause = {0, 1000000L};
    uint64_t waited_ns = 0;
    while (atomic_load(&session->active_calls) > 1u) {
        nanosleep(&pause, NULL);
        waited_ns += 1000000u;
        if (waited_ns > 5000000000ull) {
            atomic_store(&session->reset_flag, 0);
            exit_exclusive(session);
            as_error_set(error, AS_BUSY, "session", "session has in-flight calls");
            return AS_BUSY;
        }
    }
    pthread_mutex_lock(&session->control_mutex);
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        as_worker_stop(session);
    }
    /* A reset during draining or with queued work cancels those intervals. */
    uint64_t cancelled = 0;
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        account_queued_cancellation(session);
        atomic_store(&session->input_read, 0);
        atomic_store(&session->input_write, 0);
        atomic_store(&session->output_read, 0);
        atomic_store(&session->output_write, 0);
        session->admission_closed = 0;
        session->drain_complete = 0;
        session->worker_failed = 0;
        session->manual_drain_requested = 0;
    } else if (atomic_load(&session->lifecycle) == AS_LIFE_DRAINING) {
        cancelled = 1;
        const int64_t remaining =
            session->accepted_end > session->next_output_sample
                ? session->accepted_end - session->next_output_sample
                : 0;
        atomic_fetch_add(&session->c_cancelled_valid, (uint64_t)remaining);
        atomic_fetch_add(&session->c_cancelled_intervals, cancelled);
    }
    status = session->table.reset(session->instance, epoch, first_input_sample, error);
    if (status != AS_OK) {
        atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
        as_error_set(error, status, "provider", "provider reset failed");
        atomic_store(&session->reset_flag, 0);
        pthread_mutex_unlock(&session->control_mutex);
        exit_exclusive(session);
        return status;
    }
    session->epoch = epoch;
    session->first_input_sample = first_input_sample;
    session->next_input_sample = first_input_sample;
    session->accepted_end = first_input_sample;
    session->next_output_sample = first_input_sample - (int64_t)session->buffering_delay;
    session->drain_calls = 0;
    atomic_store(&session->c_submitted_valid, 0);
    atomic_store(&session->c_accepted_valid, 0);
    atomic_store(&session->c_rejected_valid, 0);
    atomic_store(&session->c_produced_valid, 0);
    atomic_store(&session->c_delivered_valid, 0);
    atomic_store(&session->c_startup_padding, 0);
    atomic_store(&session->c_final_padding, 0);
    atomic_store(&session->c_backend_failures, 0);
    atomic_store(&session->c_drain_frames, 0);
    atomic_store(&session->lifecycle, AS_LIFE_PREPARED);
    if (session->execution_mode == AS_MODE_BUFFERED_WORKER) {
        as_status_v0 restart = as_worker_start(session, error);
        if (restart != AS_OK) {
            atomic_store(&session->lifecycle, AS_LIFE_NEEDS_RESET);
            status = restart;
        }
    }
    pthread_mutex_unlock(&session->control_mutex);
    atomic_store(&session->reset_flag, 0);
    exit_exclusive(session);
    return status;
}

/* ---- info/stats -------------------------------------------------------- */

static as_status_v0 copy_json(char *buffer, uint32_t capacity, uint32_t *required,
                              writer *w) {
    if (required != NULL) *required = w->length + 1u;
    if (buffer == NULL || capacity == 0) return AS_OK;
    if (w->overflow || capacity < w->length + 1u) return AS_RESOURCE_EXHAUSTED;
    memcpy(buffer, w->buffer, w->length + 1u);
    return AS_OK;
}

as_status_v0 AS_CALL as_session_get_info_v0(as_session_v0 *session, char *buffer,
                                            uint32_t capacity,
                                            uint32_t *required_size) {
    if (required_size != NULL) *required_size = 0;
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    char text[4096];
    writer w = {text, (uint32_t)sizeof(text), 0, 0};
    text[0] = '\0';
    const as_json_doc *doc = &session->provider->descriptor_doc;
    const char *implementation_id = NULL;
    uint32_t implementation_length = 0;
    (void)as_json_get_string(doc, session->provider->descriptor_root,
                             "implementation_id", &implementation_id,
                             &implementation_length);
    char descriptor_hex[65];
    char config_hex[65];
    as_hex(session->descriptor_digest, descriptor_hex);
    as_hex(session->config_digest, config_hex);
    pthread_mutex_lock(&session->control_mutex);
    w_text(&w, "{");
    w_key(&w, "schema_id");
    w_string(&w, "audio-sdk/session-info/0.1");
    w_text(&w, ",");
    w_key(&w, "contract_version");
    w_string(&w, AS_CONTRACT_VERSION);
    w_text(&w, ",");
    w_key(&w, "provider_id");
    w_string(&w, session->provider_id);
    w_text(&w, ",");
    w_key(&w, "implementation_id");
    if (implementation_id != NULL) {
        char copy[128];
        const uint32_t length = implementation_length < sizeof(copy) - 1u
                                    ? implementation_length
                                    : (uint32_t)sizeof(copy) - 1u;
        memcpy(copy, implementation_id, length);
        copy[length] = '\0';
        w_string(&w, copy);
    } else {
        w_string(&w, "");
    }
    w_text(&w, ",");
    w_key(&w, "descriptor_digest");
    w_string(&w, descriptor_hex);
    w_text(&w, ",");
    w_key(&w, "config_digest");
    w_string(&w, config_hex);
    w_text(&w, ",");
    w_key(&w, "engine");
    w_string(&w, "reference.sequential.v0");
    w_text(&w, ",");
    w_key(&w, "lifecycle");
    w_string(&w, lifecycle_name(atomic_load(&session->lifecycle)));
    w_text(&w, ",");
    w_key(&w, "execution_mode");
    w_u64(&w, session->execution_mode);
    w_text(&w, ",");
    w_key(&w, "sample_format");
    w_string(&w, "f32");
    w_text(&w, ",");
    w_key(&w, "sample_rate_hz");
    w_u64(&w, session->sample_rate_hz);
    w_text(&w, ",");
    w_key(&w, "channels");
    w_u64(&w, session->channels);
    w_text(&w, ",");
    w_key(&w, "frame_samples");
    w_u64(&w, session->frame_samples);
    w_text(&w, ",");
    w_key(&w, "native_hop_samples");
    w_u64(&w, session->native_hop);
    w_text(&w, ",");
    w_key(&w, "buffering_delay_samples");
    w_u64(&w, session->buffering_delay);
    w_text(&w, ",");
    w_key(&w, "edge_exclusions");
    w_text(&w, "{\"start_samples\":");
    w_u64(&w, session->edge_start);
    w_text(&w, ",\"end_samples\":");
    w_u64(&w, session->edge_end);
    w_text(&w, "}");
    w_text(&w, ",");
    w_key(&w, "max_drain_calls");
    w_u64(&w, session->max_drain_calls);
    w_text(&w, ",");
    w_key(&w, "callback_safe");
    w_text(&w, session->provider->callback_safe ? "true" : "false");
    w_text(&w, "}");
    pthread_mutex_unlock(&session->control_mutex);
    return copy_json(buffer, capacity, required_size, &w);
}

as_status_v0 AS_CALL as_session_get_stats_v0(as_session_v0 *session, char *buffer,
                                             uint32_t capacity,
                                             uint32_t *required_size) {
    if (required_size != NULL) *required_size = 0;
    if (session == NULL || session->magic != AS_SESSION_MAGIC)
        return AS_INVALID_ARGUMENT;
    char text[4096];
    writer w = {text, (uint32_t)sizeof(text), 0, 0};
    text[0] = '\0';
    uint32_t input_depth = 0;
    uint32_t output_depth = 0;
    const uint32_t input_read = atomic_load(&session->input_read);
    const uint32_t input_write = atomic_load(&session->input_write);
    const uint32_t output_read = atomic_load(&session->output_read);
    const uint32_t output_write = atomic_load(&session->output_write);
    input_depth = input_write - input_read;
    output_depth = output_write - output_read;
    pthread_mutex_lock(&session->control_mutex);
    w_text(&w, "{");
    w_key(&w, "schema_id");
    w_string(&w, "audio-sdk/session-stats/0.1");
    w_text(&w, ",");
    w_key(&w, "epoch");
    w_q_u64(&w, session->epoch);
    w_text(&w, ",");
    w_key(&w, "lifecycle");
    w_string(&w, lifecycle_name(atomic_load(&session->lifecycle)));
    w_text(&w, ",");
    w_key(&w, "submitted_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_submitted_valid));
    w_text(&w, ",");
    w_key(&w, "accepted_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_accepted_valid));
    w_text(&w, ",");
    w_key(&w, "rejected_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_rejected_valid));
    w_text(&w, ",");
    w_key(&w, "produced_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_produced_valid));
    w_text(&w, ",");
    w_key(&w, "delivered_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_delivered_valid));
    w_text(&w, ",");
    w_key(&w, "startup_padding_samples");
    w_q_u64(&w, atomic_load(&session->c_startup_padding));
    w_text(&w, ",");
    w_key(&w, "final_padding_samples");
    w_q_u64(&w, atomic_load(&session->c_final_padding));
    w_text(&w, ",");
    w_key(&w, "cancelled_intervals");
    w_q_u64(&w, atomic_load(&session->c_cancelled_intervals));
    w_text(&w, ",");
    w_key(&w, "cancelled_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_cancelled_valid));
    w_text(&w, ",");
    w_key(&w, "failed_intervals");
    w_q_u64(&w, atomic_load(&session->c_failed_intervals));
    w_text(&w, ",");
    w_key(&w, "failed_valid_samples");
    w_q_u64(&w, atomic_load(&session->c_failed_valid));
    w_text(&w, ",");
    w_key(&w, "backend_failures");
    w_q_u64(&w, atomic_load(&session->c_backend_failures));
    w_text(&w, ",");
    w_key(&w, "drain_frames");
    w_q_u64(&w, atomic_load(&session->c_drain_frames));
    w_text(&w, ",");
    w_key(&w, "input_queue_depth");
    w_q_u64(&w, input_depth);
    w_text(&w, ",");
    w_key(&w, "input_queue_high_water");
    w_q_u64(&w, atomic_load(&session->input_high_water));
    w_text(&w, ",");
    w_key(&w, "output_queue_depth");
    w_q_u64(&w, output_depth);
    w_text(&w, ",");
    w_key(&w, "output_queue_high_water");
    w_q_u64(&w, atomic_load(&session->output_high_water));
    w_text(&w, "}");
    pthread_mutex_unlock(&session->control_mutex);
    return copy_json(buffer, capacity, required_size, &w);
}
