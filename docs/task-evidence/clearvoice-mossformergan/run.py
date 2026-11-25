# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-CLEARVOICE-MOSSFORMERGAN evidence artifacts.

Usage::

    SOURCE_ROOT=/path/to/workspace PYTHONDONTWRITEBYTECODE=1 python3 run.py

Writes contract.json, adapter.json, readiness.json, report.json,
report.json.sha256 and SOURCES.sha256. It never reads audio, downloads weights,
loads a native library or executes ClearerVoice.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def report_bytes() -> bytes:
    return reference.canonical_report_bytes(reference.build_report())


def main() -> int:
    _write("contract.json", reference.contract_bytes())
    _write("adapter.json", reference.adapter_bytes())
    report = report_bytes()
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
