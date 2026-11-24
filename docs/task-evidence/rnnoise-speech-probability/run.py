# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic Analysis report and its digest.

Usage from this directory (pinned Python 3.12.16):

    PYTHONDONTWRITEBYTECODE=1 python3.12 run.py report.json
    PYTHONDONTWRITEBYTECODE=1 python3.12 run.py runtime-measurements.json

``report.json`` is byte-reproducible; ``report.json.sha256`` is refreshed from
it.  ``runtime-measurements.json`` is an intentionally unpaced, non-qualifying
wall-clock pointer: regenerating it is expected to change its bytes and is
never used as evidence of quality, pacing or availability.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402 - task-local deterministic module


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2,
                       separators=(",", ": "), allow_nan=False) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in ("report.json", "runtime-measurements.json"):
        print("usage: run.py report.json|runtime-measurements.json", file=sys.stderr)
        return 2
    target = argv[1]
    if target == "report.json":
        payload = reference.canonical_report_bytes(reference.build_report())
        (HERE / "report.json").write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n",
                                                 encoding="utf-8")
        print(f"report_sha256={digest} bytes={len(payload)}")
        return 0
    payload = pretty_bytes(reference.run_measures())
    (HERE / "runtime-measurements.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    print(f"runtime_measurements_sha256={digest} bytes={len(payload)} "
          "qualification_status=blocked non_qualifying=true")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
