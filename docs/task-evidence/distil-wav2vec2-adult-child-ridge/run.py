# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate deterministic report.json and report.json.sha256."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] != "report.json":
        print("usage: run.py report.json", file=sys.stderr)
        return 2
    report = reference.build_report()
    payload = reference.canonical_report_bytes(report)
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    print(f"report_sha256={digest} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
