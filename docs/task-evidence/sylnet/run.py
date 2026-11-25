# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical contract, report, digest sidecar and source manifest."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def _three_identical(payloads: list[bytes], label: str) -> bytes:
    if len(payloads) != 3 or len(set(payloads)) != 1:
        raise SystemExit("refusing to write: three " + label + " passes differ")
    return payloads[0]


def write_contract() -> bytes:
    payload = _three_identical([reference.contract_bytes() for _ in range(3)], "contract")
    (HERE / "contract.json").write_bytes(payload)
    return payload


def write_report() -> bytes:
    payload = _three_identical(
        [reference.canonical_report_bytes(reference.build_report()) for _ in range(3)],
        "report")
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_bytes(f"{digest}  report.json\n".encode("ascii"))
    return payload


def write_sources() -> bytes:
    payload = _three_identical([reference.sources_bytes() for _ in range(3)], "manifest")
    (HERE / "SOURCES.sha256").write_bytes(payload)
    return payload


def main(argv: list[str]) -> int:
    targets = set(argv[1:])
    if not targets or not targets <= {"contract.json", "report.json", "sources", "all"}:
        print("usage: run.py [contract.json|report.json|sources|all]", file=sys.stderr)
        return 2
    if "all" in targets:
        targets = {"contract.json", "report.json", "sources"}
    if "contract.json" in targets:
        write_contract()
    if "report.json" in targets:
        report = write_report()
        print(f"report_sha256={hashlib.sha256(report).hexdigest()} bytes={len(report)}")
    if "sources" in targets:
        manifest = write_sources()
        print(f"sources_sha256={hashlib.sha256(manifest).hexdigest()} bytes={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
