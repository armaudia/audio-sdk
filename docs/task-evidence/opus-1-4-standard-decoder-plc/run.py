# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the canonical report.json byte-for-byte from frozen inputs.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
    PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json runtime-measurements.json

With one argument the unpaced measurements file is written next to the report
as ``runtime-measurements.json``. The report is deterministic; the
measurements file is intentionally non-deterministic and never used as a
qualification result.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import reference as ref


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: run.py <report.json> [runtime-measurements.json]")
    report_path = Path(sys.argv[1])
    if len(sys.argv) == 3:
        measurements_path = Path(sys.argv[2])
    else:
        measurements_path = report_path.parent / "runtime-measurements.json"

    report = ref.build_report()
    report_path.write_bytes(ref.canonical_report_bytes(report))

    measurements = ref.build_runtime_measurements()
    measurements_path.write_bytes(
        json.dumps(measurements, sort_keys=True, indent=2, ensure_ascii=False,
                   allow_nan=False).encode("utf-8") + b"\n")

    print(f"report_sha256={hashlib.sha256(report_path.read_bytes()).hexdigest()}")
    print(f"fixture_digest={report['fixture_digest']}")
    print(f"qualification_status={report['qualification_status']} "
          f"all_metrics_available={report['all_metrics_available']} "
          f"controls_all_pass={report['controls_all_pass']} "
          f"regressions={len(report['regressions'])}")


if __name__ == "__main__":
    main()
