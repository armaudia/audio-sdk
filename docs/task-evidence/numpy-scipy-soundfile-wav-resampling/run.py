# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regeneration entry points for this task-local offline tooling fixture.

    python run.py report.json            # deterministic, byte-identical
    python run.py --measure runtime-measurements.json
    python run.py --pins                 # regenerate SOURCES.sha256

The measured workload file is an unpaced, non-qualifying pointer and is never
part of SDK runtime timing. The report is fully deterministic from frozen
synthetic inputs and pinned installed libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    if len(argv) == 1 and argv[0] == "--pins":
        (HERE / "SOURCES.sha256").write_text(fixture.sources_text(),
                                             encoding="utf-8")
        print(fixture.file_digest(HERE / "SOURCES.sha256"))
        return 0
    if len(argv) == 2 and argv[0] == "--measure":
        payload = fixture.canonical_bytes(fixture.measure_workload()) + b"\n"
        Path(argv[1]).write_bytes(payload)
        print(fixture.file_digest(Path(argv[1])))
        return 0
    if len(argv) == 1 and argv[0] not in ("--measure", "--pins"):
        print(fixture.write_report(Path(argv[0])))
        return 0
    print("usage: run.py <report.json> | --measure <file> | --pins",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
