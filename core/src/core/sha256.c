/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
/* Minimal SHA-256 (FIPS 180-4). Used for descriptor/config/asset identities. */
#include "core/sha256.h"

#include <string.h>

static const uint32_t kK[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu,
    0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u, 0xd807aa98u, 0x12835b01u,
    0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u,
    0xc19bf174u, 0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau, 0x983e5152u,
    0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u,
    0x06ca6351u, 0x14292967u, 0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu,
    0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u,
    0xd6990624u, 0xf40e3585u, 0x106aa070u, 0x19a4c116u, 0x1e376c08u,
    0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu,
    0x682e6ff3u, 0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32u - (n))))

static void compress(as_sha256_ctx *ctx, const uint8_t block[64]) {
    uint32_t w[64];
    for (int i = 0; i < 16; ++i) {
        w[i] = ((uint32_t)block[i * 4] << 24) | ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) | (uint32_t)block[i * 4 + 3];
    }
    for (int i = 16; i < 64; ++i) {
        const uint32_t s0 = ROTR(w[i - 15], 7) ^ ROTR(w[i - 15], 18) ^ (w[i - 15] >> 3);
        const uint32_t s1 = ROTR(w[i - 2], 17) ^ ROTR(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    uint32_t a = ctx->state[0], b = ctx->state[1], c = ctx->state[2], d = ctx->state[3];
    uint32_t e = ctx->state[4], f = ctx->state[5], g = ctx->state[6], h = ctx->state[7];
    for (int i = 0; i < 64; ++i) {
        const uint32_t s1 = ROTR(e, 6) ^ ROTR(e, 11) ^ ROTR(e, 25);
        const uint32_t ch = (e & f) ^ ((~e) & g);
        const uint32_t t1 = h + s1 + ch + kK[i] + w[i];
        const uint32_t s0 = ROTR(a, 2) ^ ROTR(a, 13) ^ ROTR(a, 22);
        const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        const uint32_t t2 = s0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }
    ctx->state[0] += a;
    ctx->state[1] += b;
    ctx->state[2] += c;
    ctx->state[3] += d;
    ctx->state[4] += e;
    ctx->state[5] += f;
    ctx->state[6] += g;
    ctx->state[7] += h;
}

void as_sha256_init(as_sha256_ctx *ctx) {
    static const uint32_t initial[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u,
                                        0xa54ff53au, 0x510e527fu, 0x9b05688cu,
                                        0x1f83d9abu, 0x5be0cd19u};
    memcpy(ctx->state, initial, sizeof(initial));
    ctx->bit_count = 0;
    ctx->buffer_len = 0;
}

void as_sha256_update(as_sha256_ctx *ctx, const void *data, size_t length) {
    const uint8_t *bytes = (const uint8_t *)data;
    ctx->bit_count += (uint64_t)length * 8u;
    while (length > 0) {
        const size_t room = 64u - ctx->buffer_len;
        const size_t take = length < room ? length : room;
        memcpy(ctx->buffer + ctx->buffer_len, bytes, take);
        ctx->buffer_len += take;
        bytes += take;
        length -= take;
        if (ctx->buffer_len == 64) {
            compress(ctx, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
}

void as_sha256_final(as_sha256_ctx *ctx, uint8_t out[32]) {
    const uint64_t bits = ctx->bit_count;
    uint8_t pad = 0x80;
    as_sha256_update(ctx, &pad, 1);
    ctx->bit_count = bits; /* padding is not part of the message length */
    uint8_t zero = 0;
    while (ctx->buffer_len != 56) as_sha256_update(ctx, &zero, 1);
    ctx->bit_count = bits;
    uint8_t length_bytes[8];
    for (int i = 0; i < 8; ++i) length_bytes[7 - i] = (uint8_t)(bits >> (i * 8));
    as_sha256_update(ctx, length_bytes, 8);
    for (int i = 0; i < 8; ++i) {
        out[i * 4] = (uint8_t)(ctx->state[i] >> 24);
        out[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        out[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        out[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

void as_sha256(const void *data, size_t length, uint8_t out[32]) {
    as_sha256_ctx ctx;
    as_sha256_init(&ctx);
    as_sha256_update(&ctx, data, length);
    as_sha256_final(&ctx, out);
}

void as_sha256_hex(const uint8_t digest[32], char out[65]) {
    static const char hex[] = "0123456789abcdef";
    for (int i = 0; i < 32; ++i) {
        out[i * 2] = hex[digest[i] >> 4];
        out[i * 2 + 1] = hex[digest[i] & 0x0f];
    }
    out[64] = '\0';
}
