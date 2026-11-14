/* SPDX-License-Identifier: Apache-2.0 */
#include <audio_sdk/session_v0.h>
#include <stddef.h>

_Static_assert(AS_ABI_MAJOR == 0, "unexpected API major");
_Static_assert(sizeof(uint64_t) == 8, "sample counters require 64-bit integers");
int main(void) {
    as_frame_v0 frame = {0};
    frame.struct_size = (uint32_t)sizeof(frame);
    return frame.struct_size > 0 && offsetof(as_frame_v0, input) > 0 ? 0 : 1;
}
