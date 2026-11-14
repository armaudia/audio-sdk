#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Refuse packaging when compilation inputs differ from configure-time bytes."""
from __future__ import annotations

import hashlib
import sys
from itertools import zip_longest
from pathlib import Path


def runtime_inputs(root: Path) -> list[Path]:
    paths = {
        root / "CMakeLists.txt",
        root / "api/CMakeLists.txt",
        root / "deps/lock.json",
        root / "docs/migration/source-allocation.csv",
    }
    for directory, suffixes in (
        ("core/src", {".c", ".h"}),
        ("core/providers", {".c", ".h"}),
        ("api/include/audio_sdk", {".h"}),
        ("third_party/speexdsp", {".c", ".h"}),
    ):
        paths.update(
            path
            for path in (root / directory).rglob("*")
            if path.is_file() and path.suffix in suffixes
        )
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def expected_manifest(root: Path) -> bytes:
    lines = []
    for path in runtime_inputs(root):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root).as_posix()}\n")
    return "".join(lines).encode("utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify_build_inputs.py <source-root> <build-dir>", file=sys.stderr)
        return 2
    root, build = (Path(arg).resolve() for arg in sys.argv[1:])
    manifest = build / "runtime-inputs.sha256"
    if not manifest.is_file():
        print(f"missing frozen build-input manifest: {manifest}", file=sys.stderr)
        return 1
    actual = manifest.read_bytes()
    expected = expected_manifest(root)
    if actual != expected:
        print("source compilation inputs changed since CMake configure; reconfigure and rebuild", file=sys.stderr)
        for number, (configured, current) in enumerate(zip_longest(
                actual.decode("utf-8").splitlines(),
                expected.decode("utf-8").splitlines()), start=1):
            if configured != current:
                print(f"first manifest difference at line {number}: "
                      f"configured={configured!r}; current={current!r}", file=sys.stderr)
                break
        return 1
    print(f"verified {len(runtime_inputs(root))} frozen compilation inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
