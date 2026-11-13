#!/bin/sh
set -eu

prefix=${1:?usage: verify_install.sh <install-prefix>}
prefix=$(cd "$prefix" && pwd)
report_dir=${2:-"$prefix/share/audio-sdk/verification"}
mkdir -p "$report_dir"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/audio-sdk-verify.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

cat >"$tmp/consumer.c" <<'EOF'
#include <audio_sdk/session_v0.h>
int main(void) {
    as_registry_v0 *registry = 0;
    as_error_v0 error;
    as_error_v0_init(&error);
    if (as_registry_create_v0(&registry, &error) != AS_OK) return 1;
    return as_registry_close_v0(&registry) == AS_OK ? 0 : 2;
}
EOF
cat >"$tmp/consumer.cpp" <<'EOF'
#include <audio_sdk/session_v0.h>
int main() {
    as_result_v0 result{};
    as_result_v0_init(&result);
    return result.abi_major == AS_ABI_MAJOR ? 0 : 1;
}
EOF

cc -std=c11 -Wall -Wextra -Werror -I"$prefix/include" \
  "$tmp/consumer.c" -L"$prefix/lib" -laudio_sdk \
  -Wl,-rpath,"$prefix/lib" -o "$tmp/consumer-c"
c++ -std=c++20 -Wall -Wextra -Werror -I"$prefix/include" \
  "$tmp/consumer.cpp" -L"$prefix/lib" -laudio_sdk \
  -Wl,-rpath,"$prefix/lib" -o "$tmp/consumer-cpp"
"$tmp/consumer-c"
"$tmp/consumer-cpp"

"$prefix/bin/audio_sdk_conformance" --provider speex.ns.v0 \
  --report "$report_dir/speex-report.json" >"$report_dir/speex.log"
"$prefix/bin/audio_sdk_conformance" --provider dsp.highpass80.v0 \
  --report "$report_dir/highpass-report.json" >"$report_dir/highpass.log"
python3 -m json.tool "$report_dir/speex-report.json" >/dev/null
python3 -m json.tool "$report_dir/highpass-report.json" >/dev/null

echo "installed C11/C++20 consumers and both provider conformance runs passed"
echo "reports: $report_dir/speex-report.json $report_dir/highpass-report.json"
