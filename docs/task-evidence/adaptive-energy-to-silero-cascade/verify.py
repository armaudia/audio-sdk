"""Verify source pins and byte-identical report regeneration.

Run from any directory. This script only reads task-local files and the pinned
workspace source files; it never modifies anything outside this task directory.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import fixture


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    pins = fixture.read_source_manifest()
    failures: list[str] = []
    for name, expected in pins.items():
        path = fixture.resolve_pin_path(name)
        if not path.is_file():
            failures.append(f"missing pinned source: {name}")
            continue
        actual = digest_bytes(path.read_bytes())
        if actual != expected:
            failures.append(f"pin mismatch: {name}: {actual} != {expected}")

    report_path = fixture.TASK_DIR / "report.json"
    existing = report_path.read_bytes()
    regenerated = fixture.canonical(fixture.build_report()).encode("utf-8")
    if existing != regenerated:
        failures.append("report.json is not byte-identical after regeneration")

    digest_path = fixture.TASK_DIR / "report.json.sha256"
    recorded = digest_path.read_text(encoding="utf-8").strip()
    if recorded != digest_bytes(existing):
        failures.append("report.json.sha256 does not match report.json")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(
        f"verified {len(pins)} source pins and byte-identical report "
        f"sha256={digest_bytes(existing)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
