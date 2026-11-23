"""Verify all pinned artifacts for the AFC-margin evidence.

Usage (from the task-local directory):
    PYTHONDONTWRITEBYTECODE=1 python3 tools/verify.py

Checks source pins, boundary pins, fixture manifest, report digest, byte-identical
regeneration, completeness, and separation of adaptive/fixed result groups.
Exits nonzero on the first failure.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK))

import fixture  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print("verify: FAIL", message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    contract = json.loads((TASK / "contract.json").read_text())
    report_path = TASK / "report.json"
    report = json.loads(report_path.read_text())

    if report != fixture.build_report():
        fail("report.json differs from the deterministic reference build")
    text, digest = fixture.canonical_report(report)
    if text.encode("utf-8") != report_path.read_bytes():
        fail("report.json is not canonical bytes")
    if digest != contract["report"]["sha256"]:
        fail("report digest does not match contract.json")
    if report["fixture_digest"] != contract["report"]["fixture_digest"]:
        fail("fixture digest does not match contract.json")
    if sha256(report_path) != digest:
        fail("report.json.sha256 does not match report bytes")

    for name, expected in contract["source_pins"].items():
        if report["source_pins"].get(name) != expected:
            fail(f"source pin mismatch: {name}")
    for name, expected in contract["boundary_pins"].items():
        if report["boundary_pins"].get(name) != expected:
            fail(f"boundary pin mismatch: {name}")
    if report["board_snapshot"] != contract["board_snapshot"]:
        fail("board snapshot mismatch")

    manifest = (TASK / "fixtures" / "FIXTURES.sha256").read_text().splitlines()
    expected_digests = fixture.fixture_digests()
    if len(manifest) != len(expected_digests):
        fail("fixture manifest count mismatch")
    for line in manifest:
        expected, name = line.split("  ", 1)
        if expected != expected_digests.get(name):
            fail(f"fixture digest mismatch: {name}")
        if sha256(TASK / "fixtures" / name) != expected:
            fail(f"fixture file digest mismatch: {name}")

    for name, expected in contract["artifact_pins"].items():
        if sha256(TASK / name) != expected:
            fail(f"artifact pin mismatch: {name}")

    results = report["results"]
    if results["completeness"]["missing_sections"]:
        fail("report has missing result sections")
    if not results["completeness"]["all_sections_measured"]:
        fail("report completeness flag is false")
    if "reference_adaptation" not in results or "fixed_attenuation" not in results:
        fail("result groups are not separated")

    # Byte-identical regeneration from the generator itself.
    regenerated = subprocess.run(
        [sys.executable, "report.py"], cwd=TASK, capture_output=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})
    if regenerated.returncode != 0:
        fail("report.py regeneration failed")
    if regenerated.stdout != report_path.read_bytes():
        fail("report.py regeneration is not byte-identical")

    print("verify: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
