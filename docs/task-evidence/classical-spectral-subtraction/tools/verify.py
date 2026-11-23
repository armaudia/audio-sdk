#!/usr/bin/env python3
"""Verify pinned digests and deterministic, byte-identical report regeneration."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess

TASK = Path(__file__).resolve().parents[1]
SOURCES = TASK / "SOURCES.sha256"
FIXTURES = TASK / "fixtures" / "FIXTURES.sha256"
REPORT = TASK / "evidence" / "report.json"


def entries(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        result[name] = digest
    return result


def check_manifest(path: Path, root: Path) -> None:
    for name, digest in entries(path).items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != digest:
            raise SystemExit(f"digest mismatch: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--build-info", type=Path, required=True)
    parser.add_argument("--controls-ok", choices=("true", "false"), required=True)
    args = parser.parse_args()

    check_manifest(SOURCES, TASK)
    check_manifest(FIXTURES, TASK / "fixtures")
    before = REPORT.read_bytes()
    subprocess.run([
        "python3", str(TASK / "tools" / "generate_fixtures.py"), "--check",
    ], check=True)
    subprocess.run([
        "python3", str(TASK / "tools" / "evaluate.py"),
        "--cli", str(args.cli),
        "--profile", str(TASK / "fixtures" / "noise_profile.f32"),
        "--work", str(args.work),
        "--sources-sha", str(SOURCES),
        "--fixture-manifest", str(FIXTURES),
        "--build-info", str(args.build_info),
        "--controls-ok", args.controls_ok,
    ], check=True, stdout=subprocess.DEVNULL)
    after = REPORT.read_bytes()
    if before != after:
        raise SystemExit("report regeneration is not byte-identical")
    print("digests verified; report regeneration is byte-identical")
    return 0


if __name__ == "__main__":
    main()
