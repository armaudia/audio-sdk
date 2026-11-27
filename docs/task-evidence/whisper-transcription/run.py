# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the Whisper transcription task-local evidence package."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def write_outputs() -> None:
    contract = reference.build_contract()
    report = reference.build_report(contract)
    report_text, digest = reference.canonical_report(report)
    contract_bytes = reference.canonical_bytes(contract)
    report_bytes = report_text.encode("ascii")
    write_atomic(HERE / "contract.json", contract_bytes)
    write_atomic(HERE / "report.json", report_bytes)
    write_atomic(HERE / "report.json.sha256", (digest + "  report.json\n").encode("ascii"))
    write_atomic(HERE / "SOURCES.sha256", reference.sources_bytes())


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args and args != ["all"]:
        print("usage: python3 run.py [all]", file=sys.stderr)
        return 2
    write_outputs()
    if "--repeat" in args:
        pass
    for _ in range(2):
        before = (HERE / "report.json").read_bytes()
        write_outputs()
        after = (HERE / "report.json").read_bytes()
        if before != after:
            print("FAIL: regeneration not byte-identical", file=sys.stderr)
            return 1
    print("PASS run.py repeat=3 byte_identical=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
