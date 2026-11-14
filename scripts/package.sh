#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: package.sh <build-dir> <candidate-dir>" >&2
  exit 2
fi

build_dir=$1
requested_candidate_dir=$2
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$script_dir/verify_build_inputs.py" "$script_dir/.." "$build_dir"
if [ -e "$requested_candidate_dir" ]; then
  echo "refusing to overwrite existing candidate: $requested_candidate_dir" >&2
  exit 1
fi
candidate_parent=$(dirname -- "$requested_candidate_dir")
candidate_name=$(basename -- "$requested_candidate_dir")
mkdir -p "$candidate_parent"
candidate_dir=$(mktemp -d "$candidate_parent/.${candidate_name}.staging.XXXXXX")
cleanup() {
  if [ -n "${candidate_dir:-}" ] && [ -d "$candidate_dir" ]; then
    rm -rf -- "$candidate_dir"
  fi
}
trap cleanup EXIT HUP INT TERM
prefix="$candidate_dir/audio-sdk-0.1.0"
if [ -e "$prefix/share/audio-sdk/conformance/legacy_timing_probe.c" ]; then
  rm -f "$prefix/share/audio-sdk/conformance/legacy_timing_probe.c"
fi
cmake --install "$build_dir" --prefix "$prefix"
python3 "$script_dir/install_source.py" "$prefix/share/audio-sdk/source"
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
if [ -e "$requested_candidate_dir" ]; then
  echo "refusing to seal over existing candidate: $requested_candidate_dir" >&2
  exit 1
fi
mv "$candidate_dir" "$requested_candidate_dir"
candidate_dir=
echo "candidate: $requested_candidate_dir/audio-sdk-0.1.0.tar.gz"
cat "$requested_candidate_dir/audio-sdk-0.1.0.tar.gz.sha256"
