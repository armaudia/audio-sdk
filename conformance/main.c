#include "checks.h"

#include <stdio.h>
#include <string.h>

static void usage(const char *program) {
    fprintf(stderr,
            "usage: %s --provider <id> [--report <json>]\n"
            "exit: 0 pass, 1 conformance failure, 2 invocation/environment error\n",
            program);
}

int main(int argc, char **argv) {
    const char *provider = NULL;
    const char *report = NULL;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--provider") == 0 && i + 1 < argc) {
            provider = argv[++i];
        } else if (strcmp(argv[i], "--report") == 0 && i + 1 < argc) {
            report = argv[++i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (provider == NULL) {
        usage(argv[0]);
        return 2;
    }

    as_error_v0 error;
    as_error_v0_init(&error);
    as_registry_v0 *registry = NULL;
    const as_status_v0 status = as_registry_create_v0(&registry, &error);
    if (status != AS_OK) {
        fprintf(stderr, "registry creation failed: %s (%s)\n", error.message,
                error.field);
        return 2;
    }

    char detail[256];
    const int result =
        as_run_conformance(registry, provider, (uint32_t)strlen(provider),
                           report, detail, (uint32_t)sizeof(detail));
    if (result != 0 && detail[0] != '\0') {
        fprintf(stderr, "%s\n", detail);
    }
    const as_status_v0 close_status = as_registry_close_v0(&registry);
    if (close_status != AS_OK) {
        fprintf(stderr, "registry close failed: %s\n",
                as_status_name_v0(close_status));
        return 2;
    }
    return result;
}
