# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-ROSE-CD-RMS-MATCHED package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py

Writes contract.json, report.json, report.json.sha256 and SOURCES.sha256 and
refreshes the README artifact table.  The report is built three times from a
cold start and every payload must be byte-identical before anything is written.
The script never reads real audio, downloads a model, loads a weight, imports a
neural runtime, measures a device clock or hashes the mutable full task board.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
ROUNDS = 3


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def main() -> int:
    contract = reference.contract_bytes()
    reports = [reference.canonical_report_bytes(reference.build_report())
               for _ in range(ROUNDS)]
    if any(payload != reports[0] for payload in reports[1:]):
        raise SystemExit("report regeneration is not byte-identical")
    report = reports[0]
    digest = hashlib.sha256(report).hexdigest()
    _write("contract.json", contract)
    _write("report.json", report)
    _write("report.json.sha256", f"{digest}  report.json\n".encode("ascii"))
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    _write("README.md",
           reference.update_readme_artifact_table(readme).encode("utf-8"))
    _write("SOURCES.sha256", reference.sources_bytes())
    print(
        "wrote contract.json report.json report.json.sha256 SOURCES.sha256 "
        f"and README table after {ROUNDS} byte-identical report builds; "
        f"report_sha256={digest} decision={reference.DECISION} "
        f"status={reference.STATUS} qualification={reference.QUALIFICATION} "
        f"gates={len(reference.GATE_REQUIREMENTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
