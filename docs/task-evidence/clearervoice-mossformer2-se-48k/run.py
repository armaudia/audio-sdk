# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-CLEARERVOICE-MOSSFORMER2-SE-48K package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py

Writes contract.json, report.json, report.json.sha256, SOURCES.sha256 and the
README tables.  The contract and report are each built three times and must be
byte-identical before anything is written.  The script never reads real audio,
downloads a model, loads a weight, imports ClearerVoice, executes a runtime or
hashes the mutable full task board.
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
    contracts = [reference.contract_bytes() for _ in range(ROUNDS)]
    if any(payload != contracts[0] for payload in contracts[1:]):
        raise SystemExit("contract regeneration is not byte-identical")
    contract = contracts[0]
    contract_digest = hashlib.sha256(contract).hexdigest()

    reports = [
        reference.canonical_report_bytes(
            reference.build_report(contract_sha256=contract_digest)
        )
        for _ in range(ROUNDS)
    ]
    if any(payload != reports[0] for payload in reports[1:]):
        raise SystemExit("report regeneration is not byte-identical")
    report = reports[0]
    report_digest = hashlib.sha256(report).hexdigest()

    _write("contract.json", contract)
    _write("report.json", report)
    _write("report.json.sha256", f"{report_digest}  report.json\n".encode("ascii"))

    readme = (HERE / "README.md").read_text(encoding="utf-8")
    report_payload = reference.strict_object_loads(report.decode("utf-8"))
    _write(
        "README.md",
        reference.update_readme_tables(readme, report_payload).encode("utf-8"),
    )
    _write("SOURCES.sha256", reference.sources_bytes())

    print(
        "wrote contract.json report.json report.json.sha256 SOURCES.sha256 "
        f"and README tables after {ROUNDS} byte-identical builds; "
        f"contract_sha256={contract_digest} report_sha256={report_digest} "
        f"decision={reference.DECISION} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} "
        f"gates={len(reference.GATE_REQUIREMENTS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
