# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate deterministic SDK-TARGET-SPEAKER-EXTRACTION-FAMILY blocker package."""

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
    contract = reference.contract_bytes()
    reports = [reference.canonical_report_bytes(reference.build_report()) for _ in range(ROUNDS)]
    if any(payload != reports[0] for payload in reports[1:]):
        raise SystemExit("report regeneration is not byte-identical")
    report = reports[0]
    digest = hashlib.sha256(report).hexdigest()
    _write("contract.json", contract)
    _write("report.json", report)
    _write("report.json.sha256", f"{digest}  report.json\n".encode("ascii"))
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    _write("README.md", reference.update_readme_artifact_table(readme).encode("utf-8"))
    _write("SOURCES.sha256", reference.sources_bytes())
    print(f"wrote package; report_sha256={digest} decision={reference.DECISION} status={reference.STATUS} qualification={reference.QUALIFICATION} gates={len(reference.GATE_REQUIREMENTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
