# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local report and its digest from frozen synthetic inputs.

Usage (from this directory, with the pinned Python 3.12.16):

    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json

The report is canonical JSON with sorted keys; repeated runs are byte-identical.
The sibling ``<name>.sha256`` file records a sha256sum-style digest line.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import reference


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py <report.json>")
    target = Path(sys.argv[1])
    report_bytes = reference.canonical_report_bytes(reference.build_report())
    target.write_bytes(report_bytes)
    digest = hashlib.sha256(report_bytes).hexdigest()
    target.with_name(target.name + ".sha256").write_bytes(
        f"{digest}  {target.name}\n".encode("ascii"))
    print(f"report_sha256={digest}")
    print(f"report_bytes={len(report_bytes)}")


if __name__ == "__main__":
    main()
