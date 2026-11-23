#!/bin/sh
set -eu

target=${3:---native}
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ] || { [ "$target" != --native ] && [ "$target" != --wasm ]; }; then
  echo "usage: package.sh <build-dir> <candidate-dir> [--wasm]" >&2
  exit 2
fi

build_dir=$1
requested_candidate_dir=$2
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
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
python3 "$script_dir/stage_release.py" "$build_dir" "$prefix"
if [ "$target" = --wasm ]; then
  archive=audio-sdk-0.1.0-wasm32-emscripten.zip
else
  archive=audio-sdk-0.1.0.tar.gz
  if [ "$(uname -s)" = Darwin ]; then
    "$script_dir/normalize_macos_archive.py" \
      "$prefix/lib/libaudio_sdk.a" "$(xcrun --find ar)" "$(xcrun --find libtool)"
  fi
  "$script_dir/verify_install.sh" "$prefix" "$candidate_dir/verification"
fi

(
  cd "$candidate_dir"
  python3 "$script_dir/create_archive.py" audio-sdk-0.1.0 "$archive"
)
if [ -e "$requested_candidate_dir" ]; then
  echo "refusing to seal over existing candidate: $requested_candidate_dir" >&2
  exit 1
fi
mv "$candidate_dir" "$requested_candidate_dir"
candidate_dir=
echo "candidate: $requested_candidate_dir/$archive"
cat "$requested_candidate_dir/$archive.sha256"
