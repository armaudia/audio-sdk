# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-UI-CONTAINER-RATE blocker package."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
ROUNDS = 3


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def main() -> int:
    for _ in range(ROUNDS):
        contract = reference.contract_bytes()
        report = reference.canonical_report_bytes(reference.build_report())
        digest = hashlib.sha256(report).hexdigest()
        sidecar = f"{digest}  report.json\n".encode("ascii")
        _write("contract.json", contract)
        _write("report.json", report)
        _write("report.json.sha256", sidecar)
        readme_path = HERE / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        readme_path.write_text(reference.update_readme_artifact_table(readme), encoding="utf-8")
        _write("SOURCES.sha256", reference.sources_bytes())
    reports = [reference.canonical_report_bytes(reference.build_report()) for _ in range(ROUNDS)]
    if any(r != reports[0] for r in reports[1:]):
        raise SystemExit("report regeneration is not byte-identical")
    final_digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    print(
        f"wrote contract.json report.json report.json.sha256 SOURCES.sha256 and README tables after {ROUNDS} deterministic rounds; "
        f"report_sha256={final_digest} decision={reference.DECISION} status={reference.STATUS} qualification={reference.QUALIFICATION_STATUS} gates={len(reference.GATES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
