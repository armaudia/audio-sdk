#ifndef AS_CORE_SHA256_H
#define AS_CORE_SHA256_H

#include <stddef.h>
#include <stdint.h>

typedef struct as_sha256_ctx {
    uint32_t state[8];
    uint64_t bit_count;
    uint8_t buffer[64];
    size_t buffer_len;
} as_sha256_ctx;

void as_sha256_init(as_sha256_ctx *ctx);
void as_sha256_update(as_sha256_ctx *ctx, const void *data, size_t length);
void as_sha256_final(as_sha256_ctx *ctx, uint8_t out[32]);
void as_sha256(const void *data, size_t length, uint8_t out[32]);
void as_sha256_hex(const uint8_t digest[32], char out[65]);

#endif
