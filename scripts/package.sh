#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: package.sh <build-dir> <candidate-dir>" >&2
  exit 2
fi

build_dir=$1
candidate_dir=$2
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$candidate_dir"
prefix="$candidate_dir/audio-sdk-0.1.0"
if [ -e "$prefix/share/audio-sdk/conformance/legacy_timing_probe.c" ]; then
  rm -f "$prefix/share/audio-sdk/conformance/legacy_timing_probe.c"
fi
cmake --install "$build_dir" --prefix "$prefix"
if [ "$(uname -s)" = Darwin ]; then
  "$script_dir/normalize_macos_archive.py" \
    "$prefix/lib/libaudio_sdk.a" "$(xcrun --find ar)" "$(xcrun --find libtool)"
fi
"$script_dir/verify_install.sh" "$prefix" "$candidate_dir/verification"

(
  cd "$candidate_dir"
  python3 "$script_dir/create_archive.py" \
      audio-sdk-0.1.0 audio-sdk-0.1.0.tar.gz
)
echo "candidate: $candidate_dir/audio-sdk-0.1.0.tar.gz"
cat "$candidate_dir/audio-sdk-0.1.0.tar.gz.sha256"
