# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Generate canonical SDK-VOSK blocker evidence artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def write(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    contract = reference.build_contract()
    report = reference.build_report()
    write(HERE / "contract.json", reference.canonical_bytes(contract))
    report_bytes = reference.canonical_bytes(report)
    write(HERE / "report.json", report_bytes)
    digest = reference.report_digest(report)
    write(HERE / "report.json.sha256", (digest + "  report.json\n").encode("utf-8"))
    write(HERE / "SOURCES.sha256", reference.sources_manifest().encode("utf-8"))
    write(HERE / "SOURCES.sha256", reference.sources_manifest().encode("utf-8"))
    print(f"wrote contract/report/sources report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
