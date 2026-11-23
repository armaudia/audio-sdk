#!/bin/sh
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
# Build, package, extract and verify the identity PCM baseline outside the worktree.
set -eu

task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sdk_root=$(CDPATH= cd -- "$task_dir/../../.." && pwd)
scratch=${1:-}
sources_root=${2:-$(CDPATH= cd -- "$sdk_root/../../.." && pwd)}

if [ -z "$scratch" ]; then
    echo "usage: run_installed.sh <scratch-dir> [sources-root]" >&2
    exit 2
fi
mkdir -p "$scratch"
scratch=$(CDPATH= cd -- "$scratch" && pwd)
case "$scratch" in
    "$sdk_root"|"$sdk_root"/*|"$task_dir"/*)
        echo "scratch must be outside the SDK worktree: $scratch" >&2
        exit 2
        ;;
esac
for name in sdk-build candidate extracted consumer reports logs; do
    rm -rf -- "$scratch/$name"
done
mkdir -p "$scratch/logs" "$scratch/reports"

run_logged() {
    name=$1
    shift
    echo "+ $*"
    "$@" > "$scratch/logs/$name.log" 2>&1 || {
        status=$?
        echo "FAILED: $name (exit $status); see $scratch/logs/$name.log" >&2
        tail -n 40 "$scratch/logs/$name.log" >&2 || true
        exit "$status"
    }
}

run_logged configure cmake -S "$sdk_root" -B "$scratch/sdk-build" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
run_logged build cmake --build "$scratch/sdk-build" --parallel 2
run_logged native-ctest ctest --test-dir "$scratch/sdk-build" \
    --output-on-failure --timeout 60
run_logged package sh "$sdk_root/scripts/package.sh" \
    "$scratch/sdk-build" "$scratch/candidate"

archive="$scratch/candidate/audio-sdk-0.1.0.tar.gz"
archive_sha=$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$archive")
mkdir -p "$scratch/extracted"
run_logged extract tar -xf "$archive" -C "$scratch/extracted"
prefix="$scratch/extracted/audio-sdk-0.1.0"
conformance="$prefix/share/audio-sdk/conformance"

run_logged consumer-configure cmake -S "$task_dir" -B "$scratch/consumer" \
    -DCMAKE_PREFIX_PATH="$prefix" \
    -DAUDIO_SDK_CONFORMANCE_DIR="$conformance" \
    -DIDENTITY_ARCHIVE_SHA256="$archive_sha" \
    -DCMAKE_BUILD_TYPE=Release
run_logged consumer-build cmake --build "$scratch/consumer" --parallel 2
run_logged consumer-ctest ctest --test-dir "$scratch/consumer" \
    --output-on-failure --timeout 120

run_logged canonicalize python3 "$task_dir/canonicalize.py" \
    --consumer "$scratch/consumer/consumer-report.json" \
    --conformance "$scratch/consumer/conformance-report.json" \
    --out "$scratch/reports" \
    --base 3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41

identity_cpp="$sources_root/cpp-library/src/stages/identity.cpp"
adapter_json="$sources_root/adapters/controls/adapter.json"
if [ -f "$identity_cpp" ] && [ -f "$adapter_json" ]; then
    run_logged fixture-tests env \
        PYTHONDONTWRITEBYTECODE=1 \
        IDENTITY_CPP="$identity_cpp" ADAPTER_JSON="$adapter_json" \
        python3 -m unittest discover -s "$task_dir" -p 'test_*.py' -v
else
    echo "source pins unavailable at $sources_root; fixture tests will skip pin verification"
    run_logged fixture-tests env PYTHONDONTWRITEBYTECODE=1 \
        python3 -m unittest discover -s "$task_dir" -p 'test_*.py' -v
fi

echo "scratch: $scratch"
echo "prefix: $prefix"
echo "archive_sha256: $archive_sha"
echo "reports: $scratch/reports"
