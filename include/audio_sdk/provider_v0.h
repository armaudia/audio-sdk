/*
 * audio-sdk provider ABI v0 — public C contract.
 *
 * Contract revision 0.1. This header is normative for source-linked and
 * independently built providers. It is not a stable binary plugin ABI:
 * providers are compiled against the same SDK build (see CONTRACTS.md).
 *
 * Rules:
 *  - C11, no C++/STL/exceptions/bool/long/bitfields across the boundary.
 *  - Every request/result/table begins with
 *      uint32_t struct_size, abi_major, abi_minor.
 *  - ABI major/minor for this contract are 0 and 1.
 *  - Structures are not packed. Reserved fields must be zero on input.
 *  - All strings are (pointer,length); length excludes a NUL terminator.
 *  - Callers may release control-payload bytes after a successful call; the
 *    registry/session copies everything it retains.
 */
#ifndef AUDIO_SDK_PROVIDER_V0_H
#define AUDIO_SDK_PROVIDER_V0_H

#include <stdint.h>

#if defined(_WIN32)
#  if defined(AS_BUILDING_LIBRARY)
#    define AS_API __declspec(dllexport)
#  elif defined(AS_STATIC)
#    define AS_API
#  else
#    define AS_API __declspec(dllimport)
#  endif
#  define AS_CALL __cdecl
#else
#  define AS_API __attribute__((visibility("default")))
#  define AS_CALL
#endif

#if defined(__cplusplus)
extern "C" {
#endif

#define AS_ABI_MAJOR 0u
#define AS_ABI_MINOR 1u
#define AS_CONTRACT_VERSION "0.1"

#define AS_SAMPLE_RATE_HZ 16000u
#define AS_CHANNELS 1u
#define AS_FRAME_SAMPLES 160u
#define AS_MAX_CONTROL_BYTES 65536u
#define AS_MAX_ASSETS 16u
#define AS_MAX_ASSET_BYTES (512ull * 1024ull * 1024ull)
#define AS_MAX_PROVIDER_ID 96u
#define AS_MAX_DRAIN_CALLS 1024u

/* Execution modes (as_create_config_v0.execution_mode). */
#define AS_MODE_INLINE_CALLBACK 1u
#define AS_MODE_PROCESSING_THREAD 2u
#define AS_MODE_BUFFERED_WORKER 3u

/* as_frame_v0.flags */
#define AS_FRAME_FINAL_INPUT 1u

/* as_result_v0.flags */
#define AS_RESULT_STARTUP_PADDING 1u
#define AS_RESULT_FINAL_PADDING 2u
#define AS_RESULT_CONCEALMENT 4u

typedef int32_t as_status_v0;

/* Status values are part of the contract and must not be renumbered. */
enum as_status_code_v0 {
    AS_OK = 0,
    AS_INVALID_ARGUMENT = 1,
    AS_UNSUPPORTED = 2,
    AS_RESOURCE_EXHAUSTED = 3,
    AS_BACKEND_FAILURE = 4,
    AS_NEEDS_RESET = 5,
    AS_NOT_READY = 6,
    AS_END_OF_STREAM = 7,
    AS_BUSY = 8,
    AS_CLOSED = 9,
    AS_DUPLICATE = 10
};

typedef struct as_error_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    as_status_v0 status;
    /* NUL-terminated, truncated safely; never contains paths or secrets. */
    char message[256];
    /* NUL-terminated field name when the failure identifies one input. */
    char field[96];
} as_error_v0;

typedef struct as_asset_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    const char *asset_id;      /* ASCII; retained only for this call */
    uint32_t asset_id_length;
    uint32_t reserved0;
    uint8_t sha256[32];        /* raw digest of data[0..byte_count) */
    const void *data;          /* immutable; copied during create */
    uint64_t byte_count;
} as_asset_v0;

typedef struct as_create_config_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t sample_rate_hz;     /* v0: exactly 16000 */
    uint32_t channels;           /* v0: exactly 1 */
    uint32_t frame_samples;      /* v0: exactly 160 */
    uint32_t execution_mode;     /* AS_MODE_* */
    uint32_t reserved0;
    uint64_t epoch;
    int64_t first_input_sample;
    /* Canonical effective-configuration bytes (UTF-8/ASCII subset). */
    const char *config_json;
    uint32_t config_json_length;
    uint32_t reserved1;
    const as_asset_v0 *assets;
    uint32_t asset_count;
    uint32_t reserved[3];
} as_create_config_v0;

typedef struct as_frame_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    const float *input;
    uint32_t input_count;        /* exactly 160 */
    uint32_t input_valid_count;  /* 160, or 1..159 only with FINAL_INPUT */
    uint32_t flags;              /* AS_FRAME_FINAL_INPUT or 0 */
    uint32_t reserved0;
    uint64_t epoch;
    int64_t first_input_sample;
} as_frame_v0;

typedef struct as_output_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    float *samples;              /* capacity >= 160, naturally aligned */
    uint32_t capacity;
    uint32_t reserved0;
} as_output_v0;

typedef struct as_result_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    as_status_v0 status;
    uint32_t consumed_count;
    uint32_t produced_count;
    uint32_t valid_offset;
    uint32_t valid_count;
    uint32_t flags;              /* AS_RESULT_* */
    uint64_t epoch;
    int64_t source_first_sample;
    uint32_t queue_depth;
    uint32_t reserved[3];
} as_result_v0;

/* Opaque registry/session handles. */
typedef struct as_registry_v0 as_registry_v0;
typedef struct as_session_v0 as_session_v0;

typedef struct as_provider_table_v0 {
    uint32_t struct_size;
    uint32_t abi_major;
    uint32_t abi_minor;
    as_status_v0 (AS_CALL *create)(const as_create_config_v0 *config,
                                   void **out_instance, as_error_v0 *error);
    as_status_v0 (AS_CALL *process)(void *instance, const as_frame_v0 *frame,
                                    const as_output_v0 *output,
                                    as_result_v0 *result);
    as_status_v0 (AS_CALL *reset)(void *instance, uint64_t epoch,
                                  int64_t first_input_sample, as_error_v0 *error);
    as_status_v0 (AS_CALL *drain)(void *instance, const as_output_v0 *output,
                                  as_result_v0 *result);
    void (AS_CALL *destroy)(void *instance);
    uint32_t reserved[4];
} as_provider_table_v0;

/* ---- initializers ------------------------------------------------------ */

AS_API void AS_CALL as_error_v0_init(as_error_v0 *error);
AS_API void AS_CALL as_asset_v0_init(as_asset_v0 *asset);
AS_API void AS_CALL as_create_config_v0_init(as_create_config_v0 *config);
AS_API void AS_CALL as_frame_v0_init(as_frame_v0 *frame);
AS_API void AS_CALL as_output_v0_init(as_output_v0 *output);
AS_API void AS_CALL as_result_v0_init(as_result_v0 *result);
AS_API void AS_CALL as_provider_table_v0_init(as_provider_table_v0 *table);

/* Human-readable status name; never NULL. */
AS_API const char *AS_CALL as_status_name_v0(as_status_v0 status);
/* Utility functions for deterministic conformance tooling. */
AS_API int AS_CALL as_valid_provider_id_v0(const char *text, uint32_t length);
AS_API as_status_v0 AS_CALL as_sha256_hex_v0(const void *bytes, uint64_t length,
                                             char *hex_out,
                                             uint32_t capacity);

/* ---- registry ---------------------------------------------------------- */

/* Creates an empty registry and installs the SDK reference providers.
 * No mutable global default registry exists. */
AS_API as_status_v0 AS_CALL as_registry_create_v0(as_registry_v0 **out,
                                                  as_error_v0 *error);
/* AS_BUSY while any session created from this registry is alive. */
AS_API as_status_v0 AS_CALL as_registry_close_v0(as_registry_v0 **registry);

/* Copies the descriptor bytes and table. Duplicate IDs are rejected with
 * AS_DUPLICATE even when the bytes are identical. */
AS_API as_status_v0 AS_CALL as_register_provider_v0(
    as_registry_v0 *registry, const as_provider_table_v0 *table,
    const char *descriptor_bytes, uint32_t descriptor_length,
    as_error_v0 *error);

/* Returns the immutable descriptor JSON bytes plus a NUL terminator.
 * required_size includes the terminator. Insufficient capacity returns
 * AS_RESOURCE_EXHAUSTED and writes no partial output. */
AS_API as_status_v0 AS_CALL as_query_provider_v0(
    as_registry_v0 *registry, const char *provider_id,
    uint32_t provider_id_length, char *buffer, uint32_t capacity,
    uint32_t *required_size);

/* The session facade is declared in audio_sdk/session_v0.h, which includes
 * this header. */

#if defined(__cplusplus)
} /* extern "C" */
#endif

#endif /* AUDIO_SDK_PROVIDER_V0_H */
