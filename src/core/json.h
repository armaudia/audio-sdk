/*
 * Restricted canonical JSON (RFC 8785 subset) for runtime configuration.
 *
 * Admitted subset: ASCII object keys, ASCII string values, booleans, null,
 * safe integers (|n| <= 2^53-1) and arrays/objects of these. Floats and
 * exponent notation are rejected; nonintegral configuration values are
 * encoded as decimal strings by the schema. Member names are byte-sorted and
 * unique; the parser accepts only canonical bytes (no whitespace, no
 * duplicate keys, no redundant escapes, sorted members).
 */
#ifndef AS_CORE_JSON_H
#define AS_CORE_JSON_H

#include <stdint.h>

#define AS_JSON_MAX_NODES 256u
#define AS_JSON_MAX_STRING 4096u
#define AS_JSON_NO_INDEX 0xffffffffu
#define AS_JSON_SAFE_MAX 9007199254740991ll

typedef enum as_json_type {
    AS_JSON_NULL = 0,
    AS_JSON_BOOL = 1,
    AS_JSON_INT = 2,
    AS_JSON_STRING = 3,
    AS_JSON_ARRAY = 4,
    AS_JSON_OBJECT = 5
} as_json_type;

typedef struct as_json_value {
    as_json_type type;
    int64_t integer;      /* bool: 0/1; int: value */
    const char *key;      /* object member name, else NULL */
    uint32_t key_length;
    const char *string;   /* string value bytes (no NUL guarantee) */
    uint32_t string_length;
    uint32_t first_child;
    uint32_t child_count;
    uint32_t next_sibling;
} as_json_value;

typedef struct as_json_doc {
    as_json_value nodes[AS_JSON_MAX_NODES];
    uint32_t node_count;
    char strings[AS_JSON_MAX_STRING];
    uint32_t string_length;
    const char *error;
    uint32_t error_offset;
} as_json_doc;

/* Parses canonical subset bytes. Returns 0 on success. On failure doc->error
 * points to a static message. */
int as_json_parse(const char *bytes, uint32_t length, as_json_doc *doc);
/* Copies a parsed document and rebases its arena-backed node pointers. */
void as_json_doc_copy(as_json_doc *destination, const as_json_doc *source);

/* Emits canonical bytes. required includes the NUL terminator. Returns 0 on
 * success, -1 if the buffer is too small (required still written). */
int as_json_emit(const as_json_doc *doc, uint32_t root, char *buffer,
                 uint32_t capacity, uint32_t *required);

/* Object lookup; returns AS_JSON_NO_INDEX when absent. */
uint32_t as_json_get(const as_json_doc *doc, uint32_t object, const char *key);

/* Typed accessors; return 0 on success and -1 when absent/type mismatch. */
int as_json_get_string(const as_json_doc *doc, uint32_t object, const char *key,
                       const char **out, uint32_t *out_length);
int as_json_get_int(const as_json_doc *doc, uint32_t object, const char *key,
                    int64_t *out);
int as_json_get_bool(const as_json_doc *doc, uint32_t object, const char *key,
                     int *out);
int as_json_get_object(const as_json_doc *doc, uint32_t object, const char *key,
                       uint32_t *out);

int as_json_string_equals(const as_json_doc *doc, uint32_t value,
                          const char *text);

#endif
