#include "audio_sdk/session_v0.h"

#include <cstddef>
#include <type_traits>

static_assert(std::is_standard_layout_v<as_result_v0>);
static_assert(offsetof(as_result_v0, struct_size) == 0);
static_assert(offsetof(as_result_v0, abi_major) == 4);

int main() {
    as_result_v0 result{};
    as_result_v0_init(&result);
    return result.abi_major == AS_ABI_MAJOR ? 0 : 1;
}
