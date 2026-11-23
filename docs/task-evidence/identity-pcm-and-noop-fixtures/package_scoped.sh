#!/bin/sh
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
# Package the SDK with a task-scoped source archive and the shared verification steps.
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: package_scoped.sh <build-dir> <candidate-dir>" >&2
    exit 2
fi
build_dir=$1
requested_candidate_dir=$2
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sdk_root=$(CDPATH= cd -- "$task_dir/../../.." && pwd)

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
python3 "$task_dir/stage_scoped.py" "$build_dir" "$prefix"
if [ "$(uname -s)" = Darwin ]; then
    python3 "$sdk_root/scripts/normalize_macos_archive.py" \
        "$prefix/lib/libaudio_sdk.a" "$(xcrun --find ar)" "$(xcrun --find libtool)"
fi
sh "$sdk_root/scripts/verify_install.sh" "$prefix" "$candidate_dir/verification"
(
    cd "$candidate_dir"
    python3 "$sdk_root/scripts/create_archive.py" audio-sdk-0.1.0 audio-sdk-0.1.0.tar.gz
)
if [ -e "$requested_candidate_dir" ]; then
    echo "refusing to seal over existing candidate: $requested_candidate_dir" >&2
    exit 1
fi
mv "$candidate_dir" "$requested_candidate_dir"
candidate_dir=
echo "candidate: $requested_candidate_dir/audio-sdk-0.1.0.tar.gz"
cat "$requested_candidate_dir/audio-sdk-0.1.0.tar.gz.sha256"
