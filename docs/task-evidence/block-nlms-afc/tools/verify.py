#!/usr/bin/env python3
"""Verify pins, evidence coverage and byte-identical report regeneration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

import afc_reference as afc

TASK = Path(__file__).resolve().parents[1]
SOURCES = TASK / "SOURCES.sha256"
FIXTURES = TASK / "fixtures" / "FIXTURES.sha256"
REPORT = TASK / "evidence" / "report.json"

REQUIRED_SECTIONS = (
    "echo_return_loss", "convergence", "tracking", "double_talk",
    "reference_latency", "frequency_sweep", "chirp_sweep", "impulse",
    "silence", "step", "clean_speech", "gain_before_feedback",
    "adverse_loop", "headroom_and_nonlinearity", "numerical_behaviour",
    "state_transitions", "load_proxy",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        value, name = line.split("  ", 1)
        result[name] = value
    return result


def check_manifest(path: Path, root: Path) -> None:
    for name, expected in entries(path).items():
        actual = digest(root / name)
        if actual != expected:
            raise SystemExit("digest mismatch: %s (%s != %s)" % (
                name, actual, expected))


def check_no_missing(value: Any, path: str = "report") -> None:
    if value is None:
        raise SystemExit("missing result: %s" % path)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise SystemExit("nonfinite result: %s" % path)
    elif isinstance(value, dict):
        for key, item in value.items():
            check_no_missing(item, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_no_missing(item, "%s[%d]" % (path, index))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="workspace root containing research/ and plan/")
    args = parser.parse_args()

    check_manifest(SOURCES, TASK)
    check_manifest(FIXTURES, TASK / "fixtures")
    for name, expected in afc.SOURCE_PINS.items():
        actual = digest(args.workspace / name)
        if actual != expected:
            raise SystemExit("external source pin mismatch: %s" % name)
    worktree = TASK.parents[2]
    for name, expected in afc.BOUNDARY_PINS.items():
        actual = digest(worktree / name)
        if actual != expected:
            raise SystemExit("boundary pin mismatch: %s" % name)

    subprocess.run(["python3", str(TASK / "tools" / "generate_fixtures.py"),
                    "--check"], check=True)

    before = REPORT.read_bytes()
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "report.json"
        subprocess.run([
            "python3", str(TASK / "tools" / "evaluate.py"),
            "--fixtures", str(TASK / "fixtures"),
            "--sources-sha", str(SOURCES),
            "--fixture-manifest", str(FIXTURES),
            "--output", str(output),
        ], check=True, stdout=subprocess.DEVNULL)
        after = output.read_bytes()
    if before != after:
        raise SystemExit("report regeneration is not byte-identical")

    report = json.loads(before.decode("utf-8"))
    for section in REQUIRED_SECTIONS:
        if section not in report.get("results", {}):
            raise SystemExit("missing required section: %s" % section)
    for name, gate in report.get("gates", {}).items():
        if not gate.get("evidence_present") or not gate.get("result"):
            raise SystemExit("missing or nonqualifying gate: %s" % name)
    check_no_missing(report)
    print("pins verified; all %d sections present; report regeneration byte-identical"
          % len(REQUIRED_SECTIONS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
