#include "test_common.h"

int main(void) {
    as_registry_v0 *registry = NULL;
    as_error_v0 error;
    as_error_v0_init(&error);
    CHECK(as_registry_create_v0(&registry, &error) == AS_OK);
    uint32_t required = 0;
    CHECK(as_query_provider_v0(registry, "speex.ns.v0", 11, NULL, 0,
                               &required) == AS_OK);
    CHECK(required > 2);
    CHECK(as_query_provider_v0(registry, "not.registered", 14, NULL, 0,
                               NULL) == AS_UNSUPPORTED);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    CHECK(registry == NULL);
    return 0;
}
