# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-CLEANUMAMBA evidence artifacts.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py all

Writes contract.json, report.json, report.json.sha256, SOURCES.sha256 and the
README artifact digest table. It never reads audio, downloads a checkpoint,
imports PyTorch/Mamba or executes CleanUMamba.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
TASK_PREFIX = reference.TASK_PREFIX


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def _generate_once() -> dict[str, bytes]:
    contract = reference.build_contract()
    contract_payload = reference.canonical_bytes(contract)
    report_payload = reference.report_bytes(contract)
    sidecar = f"{hashlib.sha256(report_payload).hexdigest()}  report.json\n"
    _write("contract.json", contract_payload)
    _write("report.json", report_payload)
    _write("report.json.sha256", sidecar.encode("ascii"))
    readme = reference.render_readme(
        (HERE / "README.md").read_text(encoding="utf-8"))
    _write("README.md", readme.encode("utf-8"))
    sources = reference.sources_bytes()
    _write("SOURCES.sha256", sources)
    return {
        "README.md": readme.encode("utf-8"),
        "SOURCES.sha256": sources,
        "contract.json": contract_payload,
        "report.json": report_payload,
        "report.json.sha256": sidecar.encode("ascii"),
    }


def main() -> int:
    snapshots = [_generate_once() for _ in range(3)]
    if not all(snapshot == snapshots[0] for snapshot in snapshots[1:]):
        raise SystemExit("non-deterministic regeneration")
    report = snapshots[0]["report.json"]
    print(
        "wrote README.md SOURCES.sha256 contract.json report.json "
        f"report.json.sha256 report_sha256={hashlib.sha256(report).hexdigest()} "
        f"decision=DEFER status=incomplete profile=Enhancement "
        f"repeat_count=3 byte_identical=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
