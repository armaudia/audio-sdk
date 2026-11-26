# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Regenerate deterministic blocker evidence for SDK-RESEMBLE-ENHANCE-DENOISE-ONLY."""

from __future__ import annotations

import hashlib
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def main() -> int:
    _write("contract.json", reference.contract_bytes())
    report = reference.canonical_report_bytes(reference.build_report())
    _write("report.json", report)
    digest = hashlib.sha256(report).hexdigest()
    _write("report.json.sha256", f"{digest}  report.json\n".encode("ascii"))
    _write("SOURCES.sha256", reference.sources_bytes())
    print(
        "wrote contract.json report.json report.json.sha256 SOURCES.sha256 "
        f"report_sha256={digest} decision={reference.DECISION} status={reference.STATUS}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
