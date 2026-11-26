# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate canonical task-local artifacts; never writes outside this directory."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_if_changed(path: Path, payload: bytes, label: str) -> None:
    if path.is_file() and path.read_bytes() == payload:
        print(label + " unchanged " + _digest(payload))
        return
    path.write_bytes(payload)
    print(label + " written " + _digest(payload))


def build() -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    _write_if_changed(REPORT, report_payload, "report.json")
    _write_if_changed(SIDECAR, sidecar_payload, "report.json.sha256")
    _write_if_changed(CONTRACT, contract_payload, "contract.json")
    _write_if_changed(SOURCES, sources_payload, "SOURCES.sha256")


def check() -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    if REPORT.read_bytes() != report_payload:
        raise SystemExit("stale:report.json")
    if SIDECAR.read_bytes() != sidecar_payload:
        raise SystemExit("stale:report.json.sha256")
    if SOURCES.read_bytes() != sources_payload:
        raise SystemExit("stale:SOURCES.sha256")
    if CONTRACT.read_bytes() != contract_payload:
        raise SystemExit("stale:contract.json")
    print("canonical artifacts match fresh build")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"--all", "--check"}:
        print("usage: python3 run.py [--all|--check]", file=sys.stderr)
        return 2
    if sys.argv[1] == "--all":
        build()
    else:
        check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
