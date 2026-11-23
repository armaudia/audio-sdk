#!/usr/bin/env python3
"""Verify pinned blobs, source digests, oracle digest and exact regeneration."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

TASK_DIR = pathlib.Path(__file__).resolve().parent.parent
LEGACY_COMMIT = "3e2446fc58886fc02b099b54651adc9a10a65454"


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def resolve(spec: str, sdk_root: pathlib.Path, ws_root: pathlib.Path) -> pathlib.Path:
    if spec.startswith("sdk:"):
        return sdk_root / spec[4:]
    if spec.startswith("ws:"):
        return ws_root / spec[3:]
    raise ValueError("manifest name must use sdk: or ws: prefix")


def check_blobs(manifest: pathlib.Path, sdk_root: pathlib.Path,
                ws_root: pathlib.Path,
                legacy_repo: pathlib.Path | None) -> int:
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, spec = line.split(None, 1)
        spec = spec.strip()
        data = resolve(spec, sdk_root, ws_root).read_bytes()
        actual = git_blob_id(data)
        if actual != expected:
            raise SystemExit("blob mismatch %s: %s != %s" % (spec, actual, expected))
        if legacy_repo is not None:
            path = spec[4:]
            result = subprocess.run(
                ["git", "-C", str(legacy_repo), "rev-parse",
                 "%s:%s" % (LEGACY_COMMIT, path)],
                capture_output=True, text=True)
            if result.returncode != 0 or result.stdout.strip() != expected:
                raise SystemExit("legacy checkout mismatch for " + spec)
        checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=pathlib.Path)
    parser.add_argument("--work", required=True, type=pathlib.Path)
    parser.add_argument("--sdk-root", type=pathlib.Path,
                        default=TASK_DIR.parents[2])
    parser.add_argument("--ws-root", type=pathlib.Path,
                        default=pathlib.Path("/Users/htsakanyan/workspace/audio/audioml"))
    parser.add_argument("--legacy-repo", type=pathlib.Path, default=None,
                        help="optional legacy cpp-library checkout for direct rev-parse")
    parser.add_argument("--oracle", type=pathlib.Path,
                        default=TASK_DIR / "evidence" / "oracle.json")
    args = parser.parse_args()

    blob_count = check_blobs(TASK_DIR / "LEGACY_BLOBS.sha1", args.sdk_root,
                             args.ws_root, args.legacy_repo)
    oracle_bytes = args.oracle.read_bytes()
    sidecar = args.oracle.with_suffix(".json.sha256").read_text(encoding="utf-8").split()[0]
    oracle_digest = hashlib.sha256(oracle_bytes).hexdigest()
    if oracle_digest != sidecar:
        raise SystemExit("oracle sidecar mismatch: %s != %s" % (oracle_digest, sidecar))

    command = [sys.executable, str(TASK_DIR / "tools" / "evaluate.py"),
               "--cli", str(args.cli), "--work", str(args.work),
               "--repeat", "3", "--oracle", str(args.oracle),
               "--sources-sha", str(TASK_DIR / "SOURCES.sha256"),
               "--sdk-root", str(args.sdk_root), "--source-root", str(args.ws_root)]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print("verified_blobs=%d oracle_sha256=%s" % (blob_count, oracle_digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
