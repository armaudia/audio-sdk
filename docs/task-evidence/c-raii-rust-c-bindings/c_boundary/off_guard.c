/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
 * SPDX-License-Identifier: Apache-2.0
 */
/* Default-OFF proof: no SDK header, link, provider table or registration. */
#include <stdio.h>

#ifndef AS_RAII_EVIDENCE_OPTION
#define AS_RAII_EVIDENCE_OPTION 0
#endif

int main(void) {
    if (AS_RAII_EVIDENCE_OPTION != 0) {
        fprintf(stderr, "raii boundary option must be OFF for the guard target\n");
        return 1;
    }
    printf("raii_boundary=off linked_sdk=no registered=no\n");
    return 0;
}
