/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "core/json.h"

#include <string.h>
#include <stdint.h>

typedef struct parser {
    const char *bytes;
    uint32_t length;
    uint32_t offset;
    as_json_doc *doc;
} parser;

static uint32_t new_node(parser *p, as_json_type type) {
    if (p->doc->node_count >= AS_JSON_MAX_NODES) return AS_JSON_NO_INDEX;
    const uint32_t index = p->doc->node_count++;
    as_json_value *node = &p->doc->nodes[index];
    memset(node, 0, sizeof(*node));
    node->type = type;
    node->first_child = AS_JSON_NO_INDEX;
    node->next_sibling = AS_JSON_NO_INDEX;
    return index;
}

static int fail(parser *p, const char *message) {
    p->doc->error = message;
    p->doc->error_offset = p->offset;
    return -1;
}

static int peek(const parser *p) {
    return p->offset < p->length ? (unsigned char)p->bytes[p->offset] : -1;
}

static int literal(parser *p, const char *text) {
    const size_t n = strlen(text);
    if ((size_t)(p->length - p->offset) < n) return 0;
    if (memcmp(p->bytes + p->offset, text, n) != 0) return 0;
    p->offset += (uint32_t)n;
    return 1;
}

static int parse_value(parser *p, uint32_t *out, int depth);

static int parse_string(parser *p, const char **out, uint32_t *out_length,
                        int is_key) {
    if (peek(p) != '"') return fail(p, "expected string");
    ++p->offset;
    const uint32_t start = p->doc->string_length;
    for (;;) {
        const int c = peek(p);
        if (c < 0) return fail(p, "unterminated string");
        if (c == '"') {
            ++p->offset;
            break;
        }
        if (c < 0x20) return fail(p, "control character in string");
        if (c == '\\') {
            ++p->offset;
            const int e = peek(p);
            ++p->offset;
            switch (e) {
                case '"': break;
                case '\\': break;
                case '/': break;
                case 'b': break;
                case 'f': break;
                case 'n': break;
                case 'r': break;
                case 't': break;
                case 'u': {
                    /* Only ASCII escapes are admitted. */
                    if (p->length - p->offset < 4) return fail(p, "short \\u escape");
                    int value = 0;
                    for (int i = 0; i < 4; ++i) {
                        const int h = (unsigned char)p->bytes[p->offset + (uint32_t)i];
                        int digit;
                        if (h >= '0' && h <= '9') digit = h - '0';
                        else if (h >= 'a' && h <= 'f') digit = h - 'a' + 10;
                        else if (h >= 'A' && h <= 'F') digit = h - 'A' + 10;
                        else return fail(p, "invalid \\u escape");
                        value = value * 16 + digit;
                    }
                    p->offset += 4;
                    if (value > 0x7e || value < 0x20)
                        return fail(p, "non-ASCII \\u escape");
                    if (p->doc->string_length >= AS_JSON_MAX_STRING)
                        return fail(p, "string arena exhausted");
                    p->doc->strings[p->doc->string_length++] = (char)value;
                    continue;
                }
                default: return fail(p, "invalid escape");
            }
            if (p->doc->string_length >= AS_JSON_MAX_STRING)
                return fail(p, "string arena exhausted");
            switch (e) {
                case '"': p->doc->strings[p->doc->string_length++] = '"'; break;
                case '\\': p->doc->strings[p->doc->string_length++] = '\\'; break;
                case '/': p->doc->strings[p->doc->string_length++] = '/'; break;
                case 'b': p->doc->strings[p->doc->string_length++] = '\b'; break;
                case 'f': p->doc->strings[p->doc->string_length++] = '\f'; break;
                case 'n': p->doc->strings[p->doc->string_length++] = '\n'; break;
                case 'r': p->doc->strings[p->doc->string_length++] = '\r'; break;
                case 't': p->doc->strings[p->doc->string_length++] = '\t'; break;
            }
            continue;
        }
        if (c > 0x7e) return fail(p, "non-ASCII string byte");
        ++p->offset;
        if (p->doc->string_length >= AS_JSON_MAX_STRING)
            return fail(p, "string arena exhausted");
        p->doc->strings[p->doc->string_length++] = (char)c;
    }
    *out = p->doc->strings + start;
    *out_length = p->doc->string_length - start;
    (void)is_key;
    return 0;
}

static int parse_int(parser *p, int64_t *out) {
    int negative = 0;
    if (peek(p) == '-') {
        negative = 1;
        ++p->offset;
    }
    if (peek(p) < '0' || peek(p) > '9') return fail(p, "expected digit");
    if (peek(p) == '0') {
        ++p->offset;
        if (negative) return fail(p, "negative zero is not canonical");
        if (peek(p) >= '0' && peek(p) <= '9')
            return fail(p, "leading zero");
        *out = 0;
        return 0;
    }
    uint64_t value = 0;
    while (peek(p) >= '0' && peek(p) <= '9') {
        if (value > (uint64_t)AS_JSON_SAFE_MAX / 10u) return fail(p, "unsafe integer");
        value = value * 10u + (uint64_t)(peek(p) - '0');
        if (value > (uint64_t)AS_JSON_SAFE_MAX) return fail(p, "unsafe integer");
        ++p->offset;
    }
    *out = negative ? -(int64_t)value : (int64_t)value;
    return 0;
}

static int parse_value(parser *p, uint32_t *out, int depth) {
    if (depth > 8) return fail(p, "nesting too deep");
    const int c = peek(p);
    if (c == '{') {
        ++p->offset;
        const uint32_t node = new_node(p, AS_JSON_OBJECT);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        uint32_t last = AS_JSON_NO_INDEX;
        const char *previous_key = NULL;
        uint32_t previous_key_length = 0;
        if (peek(p) != '}') {
            for (;;) {
                const char *key = NULL;
                uint32_t key_length = 0;
                if (parse_string(p, &key, &key_length, 1) != 0) return -1;
                if (previous_key != NULL) {
                    const uint32_t common =
                        key_length < previous_key_length ? key_length : previous_key_length;
                    const int cmp = memcmp(previous_key, key, common);
                    if (cmp > 0 || (cmp == 0 && key_length <= previous_key_length))
                        return fail(p, "object keys are not sorted/unique");
                }
                previous_key = key;
                previous_key_length = key_length;
                if (peek(p) != ':') return fail(p, "expected ':'");
                ++p->offset;
                uint32_t child = AS_JSON_NO_INDEX;
                if (parse_value(p, &child, depth + 1) != 0) return -1;
                p->doc->nodes[child].key = key;
                p->doc->nodes[child].key_length = key_length;
                if (last == AS_JSON_NO_INDEX) {
                    p->doc->nodes[node].first_child = child;
                } else {
                    p->doc->nodes[last].next_sibling = child;
                }
                last = child;
                p->doc->nodes[node].child_count++;
                if (peek(p) == ',') {
                    ++p->offset;
                    continue;
                }
                break;
            }
        }
        if (peek(p) != '}') return fail(p, "expected '}'");
        ++p->offset;
        *out = node;
        return 0;
    }
    if (c == '[') {
        ++p->offset;
        const uint32_t node = new_node(p, AS_JSON_ARRAY);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        uint32_t last = AS_JSON_NO_INDEX;
        if (peek(p) != ']') {
            for (;;) {
                uint32_t child = AS_JSON_NO_INDEX;
                if (parse_value(p, &child, depth + 1) != 0) return -1;
                if (last == AS_JSON_NO_INDEX) {
                    p->doc->nodes[node].first_child = child;
                } else {
                    p->doc->nodes[last].next_sibling = child;
                }
                last = child;
                p->doc->nodes[node].child_count++;
                if (peek(p) == ',') {
                    ++p->offset;
                    continue;
                }
                break;
            }
        }
        if (peek(p) != ']') return fail(p, "expected ']'");
        ++p->offset;
        *out = node;
        return 0;
    }
    if (c == '"') {
        const uint32_t node = new_node(p, AS_JSON_STRING);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        if (parse_string(p, &p->doc->nodes[node].string,
                         &p->doc->nodes[node].string_length, 0) != 0)
            return -1;
        *out = node;
        return 0;
    }
    if (c == 't' || c == 'f') {
        const uint32_t node = new_node(p, AS_JSON_BOOL);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        if (c == 't') {
            if (!literal(p, "true")) return fail(p, "expected true");
            p->doc->nodes[node].integer = 1;
        } else {
            if (!literal(p, "false")) return fail(p, "expected false");
            p->doc->nodes[node].integer = 0;
        }
        *out = node;
        return 0;
    }
    if (c == 'n') {
        const uint32_t node = new_node(p, AS_JSON_NULL);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        if (!literal(p, "null")) return fail(p, "expected null");
        *out = node;
        return 0;
    }
    if (c == '-' || (c >= '0' && c <= '9')) {
        const uint32_t node = new_node(p, AS_JSON_INT);
        if (node == AS_JSON_NO_INDEX) return fail(p, "too many values");
        if (parse_int(p, &p->doc->nodes[node].integer) != 0) return -1;
        *out = node;
        return 0;
    }
    return fail(p, "invalid value");
}

int as_json_parse(const char *bytes, uint32_t length, as_json_doc *doc) {
    if (bytes == NULL || doc == NULL) return -1;
    memset(doc, 0, sizeof(*doc));
    parser p = {bytes, length, 0, doc};
    uint32_t root = AS_JSON_NO_INDEX;
    if (length == 0) {
        doc->error = "empty document";
        return -1;
    }
    if (parse_value(&p, &root, 0) != 0) return -1;
    if (p.offset != length) {
        doc->error = "trailing bytes";
        doc->error_offset = p.offset;
        return -1;
    }
    /* Re-emit and require byte equality: rejects non-canonical forms. */
    char buffer[AS_JSON_MAX_STRING + 1024];
    uint32_t required = 0;
    if (as_json_emit(doc, root, buffer, (uint32_t)sizeof(buffer), &required) != 0) {
        doc->error = "document too large";
        return -1;
    }
    if (required - 1u != length || memcmp(buffer, bytes, length) != 0) {
        doc->error = "input is not canonical";
        return -1;
    }
    return 0;
}

void as_json_doc_copy(as_json_doc *destination, const as_json_doc *source) {
    if (destination == NULL || source == NULL || destination == source) return;
    *destination = *source;
    const uintptr_t source_start = (uintptr_t)source->strings;
    const uintptr_t source_end = source_start + sizeof(source->strings);
    const uintptr_t target_start = (uintptr_t)destination->strings;
    for (uint32_t i = 0; i < source->node_count; ++i) {
        as_json_value *target = &destination->nodes[i];
        const as_json_value *original = &source->nodes[i];
        if (original->key != NULL) {
            const uintptr_t pointer = (uintptr_t)original->key;
            if (pointer >= source_start && pointer < source_end)
                target->key = (const char *)(target_start + pointer - source_start);
        }
        if (original->string != NULL) {
            const uintptr_t pointer = (uintptr_t)original->string;
            if (pointer >= source_start && pointer < source_end)
                target->string =
                    (const char *)(target_start + pointer - source_start);
        }
    }
}

static int emit_value(const as_json_doc *doc, uint32_t index, char *buffer,
                      uint32_t capacity, uint32_t *cursor) {
    const as_json_value *node = &doc->nodes[index];
    uint32_t length = 0;
    switch (node->type) {
        case AS_JSON_NULL: {
            static const char text[] = "null";
            length = 4;
            if (*cursor + length + 1u > capacity) return -1;
            memcpy(buffer + *cursor, text, length);
            break;
        }
        case AS_JSON_BOOL: {
            const char *text = node->integer ? "true" : "false";
            length = (uint32_t)strlen(text);
            if (*cursor + length + 1u > capacity) return -1;
            memcpy(buffer + *cursor, text, length);
            break;
        }
        case AS_JSON_INT: {
            uint64_t value = node->integer < 0 ? (uint64_t)(-node->integer)
                                               : (uint64_t)node->integer;
            char digits[24];
            uint32_t count = 0;
            do {
                digits[count++] = (char)('0' + (value % 10u));
                value /= 10u;
            } while (value != 0);
            if (node->integer < 0) digits[count++] = '-';
            length = count;
            if (*cursor + length + 1u > capacity) return -1;
            for (uint32_t i = 0; i < count; ++i)
                buffer[*cursor + i] = digits[count - 1u - i];
            break;
        }
        case AS_JSON_STRING: {
            if (*cursor + 2u * node->string_length + 3u > capacity) return -1;
            buffer[(*cursor)++] = '"';
            for (uint32_t i = 0; i < node->string_length; ++i) {
                const char c = node->string[i];
                if (c == '"' || c == '\\') buffer[(*cursor)++] = '\\';
                buffer[(*cursor)++] = c;
            }
            buffer[(*cursor)++] = '"';
            length = 0;
            break;
        }
        case AS_JSON_ARRAY:
        case AS_JSON_OBJECT: {
            const char open = node->type == AS_JSON_ARRAY ? '[' : '{';
            const char close = node->type == AS_JSON_ARRAY ? ']' : '}';
            if (*cursor + 2u > capacity) return -1;
            buffer[(*cursor)++] = open;
            uint32_t child = node->first_child;
            for (uint32_t i = 0; i < node->child_count; ++i) {
                if (i != 0) {
                    if (*cursor + 1u > capacity) return -1;
                    buffer[(*cursor)++] = ',';
                }
                if (node->type == AS_JSON_OBJECT) {
                    const as_json_value *member = &doc->nodes[child];
                    if (*cursor + member->key_length + 4u > capacity) return -1;
                    buffer[(*cursor)++] = '"';
                    memcpy(buffer + *cursor, member->key, member->key_length);
                    *cursor += member->key_length;
                    buffer[(*cursor)++] = '"';
                    buffer[(*cursor)++] = ':';
                }
                if (emit_value(doc, child, buffer, capacity, cursor) != 0) return -1;
                child = doc->nodes[child].next_sibling;
            }
            if (*cursor + 1u > capacity) return -1;
            buffer[(*cursor)++] = close;
            length = 0;
            break;
        }
        default: return -1;
    }
    if (length != 0) *cursor += length;
    return 0;
}

int as_json_emit(const as_json_doc *doc, uint32_t root, char *buffer,
                 uint32_t capacity, uint32_t *required) {
    uint32_t cursor = 0;
    /* Emit with a NULL-sized probe first when buffer is absent. */
    if (buffer == NULL || capacity == 0) {
        uint32_t scratch_cursor = 0;
        char scratch[AS_JSON_MAX_STRING + 1024];
        if (emit_value(doc, root, scratch, (uint32_t)sizeof(scratch), &scratch_cursor) != 0)
            return -1;
        *required = scratch_cursor + 1u;
        return 0;
    }
    if (emit_value(doc, root, buffer, capacity, &cursor) != 0) {
        /* Compute the required size. */
        uint32_t scratch_cursor = 0;
        char scratch[AS_JSON_MAX_STRING + 1024];
        if (emit_value(doc, root, scratch, (uint32_t)sizeof(scratch), &scratch_cursor) != 0)
            return -1;
        *required = scratch_cursor + 1u;
        return -1;
    }
    buffer[cursor] = '\0';
    *required = cursor + 1u;
    return 0;
}

uint32_t as_json_get(const as_json_doc *doc, uint32_t object, const char *key) {
    if (object >= doc->node_count || doc->nodes[object].type != AS_JSON_OBJECT)
        return AS_JSON_NO_INDEX;
    const size_t key_length = strlen(key);
    uint32_t child = doc->nodes[object].first_child;
    for (uint32_t i = 0; i < doc->nodes[object].child_count; ++i) {
        const as_json_value *member = &doc->nodes[child];
        if (member->key_length == key_length &&
            memcmp(member->key, key, key_length) == 0) {
            return child;
        }
        child = member->next_sibling;
    }
    return AS_JSON_NO_INDEX;
}

int as_json_string_equals(const as_json_doc *doc, uint32_t value,
                          const char *text) {
    if (value >= doc->node_count || doc->nodes[value].type != AS_JSON_STRING)
        return 0;
    const size_t length = strlen(text);
    return doc->nodes[value].string_length == length &&
           memcmp(doc->nodes[value].string, text, length) == 0;
}

int as_json_get_string(const as_json_doc *doc, uint32_t object, const char *key,
                       const char **out, uint32_t *out_length) {
    const uint32_t value = as_json_get(doc, object, key);
    if (value == AS_JSON_NO_INDEX || doc->nodes[value].type != AS_JSON_STRING)
        return -1;
    *out = doc->nodes[value].string;
    *out_length = doc->nodes[value].string_length;
    return 0;
}

int as_json_get_int(const as_json_doc *doc, uint32_t object, const char *key,
                    int64_t *out) {
    const uint32_t value = as_json_get(doc, object, key);
    if (value == AS_JSON_NO_INDEX || doc->nodes[value].type != AS_JSON_INT) return -1;
    *out = doc->nodes[value].integer;
    return 0;
}

int as_json_get_bool(const as_json_doc *doc, uint32_t object, const char *key,
                     int *out) {
    const uint32_t value = as_json_get(doc, object, key);
    if (value == AS_JSON_NO_INDEX || doc->nodes[value].type != AS_JSON_BOOL) return -1;
    *out = (int)doc->nodes[value].integer;
    return 0;
}

int as_json_get_object(const as_json_doc *doc, uint32_t object, const char *key,
                       uint32_t *out) {
    const uint32_t value = as_json_get(doc, object, key);
    if (value == AS_JSON_NO_INDEX || doc->nodes[value].type != AS_JSON_OBJECT) return -1;
    *out = value;
    return 0;
}
