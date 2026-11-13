#include "core/as_internal.h"

#include <stdlib.h>
#include <string.h>

static void free_entry(as_provider_entry *entry) {
    free(entry->descriptor);
    entry->descriptor = NULL;
    entry->descriptor_length = 0;
}

as_status_v0 as_registry_register_builtin_v0(as_registry_v0 *registry,
                                             const as_provider_table_v0 *table,
                                             const char *descriptor,
                                             uint32_t descriptor_length,
                                             as_error_v0 *error) {
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC) {
        as_error_set(error, AS_INVALID_ARGUMENT, "registry", "registry is invalid");
        return AS_INVALID_ARGUMENT;
    }
    pthread_mutex_lock(&registry->lock);
    as_status_v0 status = AS_OK;
    if (registry->provider_count >= AS_MAX_PROVIDERS) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "registry", "provider limit reached");
        status = AS_RESOURCE_EXHAUSTED;
    } else {
        as_provider_entry *entry = &registry->providers[registry->provider_count];
        memset(entry, 0, sizeof(*entry));
        entry->descriptor = (char *)malloc(descriptor_length + 1u);
        if (entry->descriptor == NULL) {
            as_error_set(error, AS_RESOURCE_EXHAUSTED, "descriptor",
                         "descriptor allocation failed");
            status = AS_RESOURCE_EXHAUSTED;
        } else {
            memcpy(entry->descriptor, descriptor, descriptor_length);
            entry->descriptor[descriptor_length] = '\0';
            entry->descriptor_length = descriptor_length;
            as_sha256(descriptor, descriptor_length, entry->descriptor_digest);
            status = as_descriptor_validate(entry->descriptor, descriptor_length,
                                            entry, error);
            if (status == AS_OK) {
                entry->table = *table;
                registry->provider_count++;
            } else {
                free_entry(entry);
            }
        }
    }
    pthread_mutex_unlock(&registry->lock);
    return status;
}

as_provider_entry *as_registry_lookup(as_registry_v0 *registry,
                                      const char *provider_id,
                                      uint32_t provider_id_length) {
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC) return NULL;
    for (uint32_t i = 0; i < registry->provider_count; ++i) {
        as_provider_entry *entry = &registry->providers[i];
        if (entry->provider_id_length == provider_id_length &&
            memcmp(entry->provider_id, provider_id, provider_id_length) == 0) {
            return entry;
        }
    }
    return NULL;
}

as_status_v0 AS_CALL as_registry_create_v0(as_registry_v0 **out,
                                           as_error_v0 *error) {
    as_error_clear(error);
    if (out == NULL) {
        as_error_set(error, AS_INVALID_ARGUMENT, "out", "out is null");
        return AS_INVALID_ARGUMENT;
    }
    *out = NULL;
    as_registry_v0 *registry = (as_registry_v0 *)calloc(1, sizeof(*registry));
    if (registry == NULL) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "registry",
                     "registry allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    registry->magic = AS_REGISTRY_MAGIC;
    if (pthread_mutex_init(&registry->lock, NULL) != 0) {
        free(registry);
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "registry",
                     "registry mutex initialization failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    as_status_v0 status = as_registry_register_builtin_v0(
        registry, as_speex_provider_table(), as_speex_descriptor,
        as_speex_descriptor_length, error);
    if (status == AS_OK) {
        status = as_registry_register_builtin_v0(
            registry, as_highpass_provider_table(), as_highpass_descriptor,
            as_highpass_descriptor_length, error);
    }
    if (status != AS_OK) {
        for (uint32_t i = 0; i < registry->provider_count; ++i)
            free_entry(&registry->providers[i]);
        pthread_mutex_destroy(&registry->lock);
        free(registry);
        return status;
    }
    *out = registry;
    return AS_OK;
}

as_status_v0 AS_CALL as_registry_close_v0(as_registry_v0 **registry) {
    if (registry == NULL || *registry == NULL) return AS_OK;
    as_registry_v0 *self = *registry;
    if (self->magic != AS_REGISTRY_MAGIC) {
        *registry = NULL;
        return AS_INVALID_ARGUMENT;
    }
    if (atomic_load(&self->session_count) != 0u) return AS_BUSY;
    pthread_mutex_lock(&self->lock);
    for (uint32_t i = 0; i < self->provider_count; ++i)
        free_entry(&self->providers[i]);
    self->provider_count = 0;
    self->magic = 0;
    pthread_mutex_unlock(&self->lock);
    pthread_mutex_destroy(&self->lock);
    free(self);
    *registry = NULL;
    return AS_OK;
}

as_status_v0 AS_CALL as_register_provider_v0(as_registry_v0 *registry,
                                             const as_provider_table_v0 *table,
                                             const char *descriptor_bytes,
                                             uint32_t descriptor_length,
                                             as_error_v0 *error) {
    as_error_clear(error);
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC) {
        as_error_set(error, AS_INVALID_ARGUMENT, "registry", "registry is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (table == NULL || descriptor_bytes == NULL || descriptor_length == 0 ||
        descriptor_length > AS_MAX_CONTROL_BYTES) {
        as_error_set(error, AS_INVALID_ARGUMENT, "descriptor",
                     "provider table or descriptor is invalid");
        return AS_INVALID_ARGUMENT;
    }
    if (!as_valid_struct(table->struct_size, table->abi_major, table->abi_minor,
                         (uint32_t)sizeof(*table)) ||
        !as_tail_is_zero(table, (uint32_t)sizeof(*table), table->struct_size) ||
        table->create == NULL || table->process == NULL || table->reset == NULL ||
        table->drain == NULL || table->destroy == NULL) {
        as_error_set(error, AS_INVALID_ARGUMENT, "table",
                     "provider table header or operations are invalid");
        return AS_INVALID_ARGUMENT;
    }
    for (int i = 0; i < 4; ++i) {
        if (table->reserved[i] != 0) {
            as_error_set(error, AS_INVALID_ARGUMENT, "table.reserved",
                         "provider table reserved fields must be zero");
            return AS_INVALID_ARGUMENT;
        }
    }
    as_provider_entry parsed;
    memset(&parsed, 0, sizeof(parsed));
    char *copy = (char *)malloc(descriptor_length + 1u);
    if (copy == NULL) {
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "descriptor",
                     "descriptor allocation failed");
        return AS_RESOURCE_EXHAUSTED;
    }
    memcpy(copy, descriptor_bytes, descriptor_length);
    copy[descriptor_length] = '\0';
    as_status_v0 status =
        as_descriptor_validate(copy, descriptor_length, &parsed, error);
    if (status != AS_OK) {
        free(copy);
        return status;
    }

    pthread_mutex_lock(&registry->lock);
    if (registry->frozen) {
        pthread_mutex_unlock(&registry->lock);
        free(copy);
        as_error_set(error, AS_BUSY, "registry",
                     "registry mutation is closed after the first session");
        return AS_BUSY;
    }
    if (as_registry_lookup(registry, parsed.provider_id,
                           parsed.provider_id_length) != NULL) {
        pthread_mutex_unlock(&registry->lock);
        free(copy);
        as_error_set(error, AS_DUPLICATE, "provider_id",
                     "provider ID is already registered");
        return AS_DUPLICATE;
    }
    if (registry->provider_count >= AS_MAX_PROVIDERS) {
        pthread_mutex_unlock(&registry->lock);
        free(copy);
        as_error_set(error, AS_RESOURCE_EXHAUSTED, "registry",
                     "provider limit reached");
        return AS_RESOURCE_EXHAUSTED;
    }
    as_provider_entry *entry = &registry->providers[registry->provider_count];
    parsed.descriptor = copy;
    parsed.descriptor_length = descriptor_length;
    parsed.table = *table;
    as_sha256(copy, descriptor_length, parsed.descriptor_digest);
    *entry = parsed;
    as_json_doc_copy(&entry->descriptor_doc, &parsed.descriptor_doc);
    registry->provider_count++;
    pthread_mutex_unlock(&registry->lock);
    return AS_OK;
}

as_status_v0 AS_CALL as_query_provider_v0(as_registry_v0 *registry,
                                          const char *provider_id,
                                          uint32_t provider_id_length,
                                          char *buffer, uint32_t capacity,
                                          uint32_t *required_size) {
    if (required_size != NULL) *required_size = 0;
    if (registry == NULL || registry->magic != AS_REGISTRY_MAGIC ||
        !as_valid_id(provider_id, provider_id_length)) {
        return AS_INVALID_ARGUMENT;
    }
    as_provider_entry *entry =
        as_registry_lookup(registry, provider_id, provider_id_length);
    if (entry == NULL) return AS_UNSUPPORTED;
    const uint32_t required = entry->descriptor_length + 1u;
    if (required_size != NULL) *required_size = required;
    if (buffer == NULL || capacity == 0) return AS_OK;
    if (capacity < required) return AS_RESOURCE_EXHAUSTED;
    memcpy(buffer, entry->descriptor, entry->descriptor_length);
    buffer[entry->descriptor_length] = '\0';
    return AS_OK;
}

as_status_v0 AS_CALL as_provider_digest_v0(as_registry_v0 *registry,
                                           const char *provider_id,
                                           uint32_t provider_id_length,
                                           char *hex_out, uint32_t capacity) {
    if (hex_out == NULL || capacity < 65u || registry == NULL ||
        registry->magic != AS_REGISTRY_MAGIC ||
        !as_valid_id(provider_id, provider_id_length)) {
        return AS_INVALID_ARGUMENT;
    }
    as_provider_entry *entry =
        as_registry_lookup(registry, provider_id, provider_id_length);
    if (entry == NULL) return AS_UNSUPPORTED;
    as_hex(entry->descriptor_digest, hex_out);
    return AS_OK;
}
