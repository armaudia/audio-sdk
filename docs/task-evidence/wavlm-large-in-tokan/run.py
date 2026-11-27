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


def _write(path: Path, payload: bytes, label: str) -> None:
    if path.is_file() and path.read_bytes() == payload:
        print(label + " unchanged " + hashlib.sha256(payload).hexdigest())
        return
    path.write_bytes(payload)
    print(label + " written " + hashlib.sha256(payload).hexdigest())


def build() -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    _write(REPORT, report_payload, "report.json")
    _write(SIDECAR, sidecar_payload, "report.json.sha256")
    _write(CONTRACT, contract_payload, "contract.json")
    _write(SOURCES, sources_payload, "SOURCES.sha256")


def check() -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    for path, payload, name in [(REPORT, report_payload, "report.json"), (SIDECAR, sidecar_payload, "report.json.sha256"), (SOURCES, sources_payload, "SOURCES.sha256"), (CONTRACT, contract_payload, "contract.json")]:
        if not path.is_file() or path.read_bytes() != payload:
            raise SystemExit("stale:" + name)
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
