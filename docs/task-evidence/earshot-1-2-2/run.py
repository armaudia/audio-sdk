# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-EARSHOT-1-2-2 evidence artifacts.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py

Writes contract.json, adapter.json, readiness.json, report.json,
report.json.sha256 and SOURCES.sha256. It never reads audio, downloads a wheel,
imports Earshot or executes a native runtime.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def main() -> int:
    _write("contract.json", reference.contract_bytes())
    _write("adapter.json", reference.adapter_bytes())
    report = reference.canonical_report_bytes(reference.build_report())
    _write("report.json", report)
    digest = hashlib.sha256(report).hexdigest()
    _write("report.json.sha256", f"{digest}  report.json\n".encode("ascii"))
    _write("readiness.json", reference.readiness_bytes())
    _write("SOURCES.sha256", reference.sources_bytes())
    print(
        "wrote contract.json adapter.json readiness.json report.json "
        f"report.json.sha256 SOURCES.sha256 report_sha256={digest} "
        f"decision={reference.DECISION} status={reference.STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
