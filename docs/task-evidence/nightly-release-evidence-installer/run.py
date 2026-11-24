# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the canonical report.json byte-for-byte from frozen inputs.

    PYTHONDONTWRITEBYTECODE=1 <PY312> run.py report.json

No build, install, network or native tool is invoked here. All observed
artifact values are frozen constants in ``fixture.py``; the deterministic
synthetic generator and reference boundary model are recomputed on every run.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

import fixture as fx


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py <report.json>")
    path = pathlib.Path(sys.argv[1])
    report = fx.build_report()
    path.write_bytes(fx.canonical_report_bytes(report))
    print(f"report_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    print(f"spec_digest={report['spec_digest']}")
    print(f"status={report['qualification_status']} "
          f"crosscheck={report['crosscheck']['all_pass']} "
          f"blockers={len(report['blockers'])} "
          f"regressions={len(report['regressions'])}")


if __name__ == "__main__":
    main()
