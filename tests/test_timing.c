#include "test_common.h"

int main(void) {
    as_registry_v0 *registry = NULL;
    as_session_v0 *session = NULL;
    CHECK(test_open(&registry, &session, "speex.ns.v0",
                    AS_MODE_PROCESSING_THREAD, 1, 123456));
    as_result_v0 result;
    CHECK(test_process(session, 1, 123456, &result));
    CHECK(result.source_first_sample == 123296);
    CHECK((result.flags & AS_RESULT_STARTUP_PADDING) != 0);
    CHECK(as_session_close_v0(&session) == AS_OK);
    CHECK(as_registry_close_v0(&registry) == AS_OK);
    return 0;
}
