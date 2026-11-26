# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical contract, report, sidecar, README digests and pins."""

from __future__ import annotations

import hashlib
import re
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


def refresh_readme() -> int:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    updated = text
    for name in reference.README_ARTIFACT_FILES:
        digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        pattern = re.compile(r"(\| `" + re.escape(name) + r"` \| `)[0-9a-f]{64}(` \|)")
        updated, count = pattern.subn(
            lambda match: match.group(1) + digest + match.group(2), updated, count=1)
        if count != 1:
            raise SystemExit("README digest row missing or duplicated: " + name)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return 1
    return 0


def write_sources() -> bytes:
    payload = _three_identical([reference.sources_bytes() for _ in range(3)], "manifest")
    (HERE / "SOURCES.sha256").write_bytes(payload)
    return payload


def main(argv: list[str]) -> int:
    commands = {"--all", "--contract", "--report", "--readme", "--sources"}
    if len(argv) != 2 or argv[1] not in commands:
        print("usage: run.py {--all|--contract|--report|--readme|--sources}",
              file=sys.stderr)
        return 2
    command = argv[1]
    if command in ("--all", "--contract"):
        write_contract()
    if command in ("--all", "--report"):
        report = write_report()
        print(f"report_sha256={hashlib.sha256(report).hexdigest()} bytes={len(report)}")
    if command == "--all":
        refresh_readme()
    if command in ("--all", "--sources"):
        manifest = write_sources()
        print(f"sources_sha256={hashlib.sha256(manifest).hexdigest()} bytes={len(manifest)}")
    if command == "--readme":
        print(f"readme_rows_updated={refresh_readme()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
