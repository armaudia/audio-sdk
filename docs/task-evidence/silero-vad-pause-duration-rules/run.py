# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical report.json, its digest sidecar and SOURCES.sha256."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def write_report() -> str:
    payload = reference.canonical_report_bytes(reference.build_report())
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_bytes(f"{digest}  report.json\n".encode("ascii"))
    return digest


def write_sources() -> None:
    (HERE / "SOURCES.sha256").write_bytes(reference.sources_bytes())


def main(argv: list[str]) -> int:
    targets = set(argv[1:])
    if not targets <= {"report.json", "sources", "all"} or not targets:
        print("usage: run.py [report.json|sources|all]", file=sys.stderr)
        return 2
    if "all" in targets:
        targets = {"report.json", "sources"}
    digest = ""
    if "report.json" in targets:
        digest = write_report()
        print(f"report_sha256={digest}")
    if "sources" in targets:
        write_sources()
        payload = (HERE / "SOURCES.sha256").read_bytes()
        print(f"sources_sha256={hashlib.sha256(payload).hexdigest()} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
