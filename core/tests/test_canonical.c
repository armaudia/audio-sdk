/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: MPL-2.0
 */
#include "core/json.h"
#include "test_common.h"

int main(void) {
    as_json_doc doc;
    const char canonical[] = "{\"a\":1,\"b\":[false,\"x\"]}";
    CHECK(as_json_parse(canonical, (uint32_t)strlen(canonical), &doc) == 0);
    CHECK(as_json_get(&doc, 0, "a") != AS_JSON_NO_INDEX);
    const char noncanonical[] = "{\"b\":1,\"a\":2}";
    CHECK(as_json_parse(noncanonical, (uint32_t)strlen(noncanonical), &doc) != 0);
    const char whitespace[] = "{\"a\": 1}";
    CHECK(as_json_parse(whitespace, (uint32_t)strlen(whitespace), &doc) != 0);
    return 0;
}
