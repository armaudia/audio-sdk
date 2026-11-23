"""Regenerate the canonical synthetic report for the narrow-notch fixture.

Usage (from this directory):
    PYTHONDONTWRITEBYTECODE=1 python3 generate.py

The script is deterministic and writes only report.json in this directory.
It reads no audio, model, network or device input.
"""

from __future__ import annotations

import json
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent


def main() -> None:
    report = fixture.build_report()
    text, digest = fixture.canonical_report(report)
    (HERE / "report.json").write_text(text, encoding="utf-8")
    print(f"wrote report.json ({len(text)} bytes, sha256:{digest})")


if __name__ == "__main__":
    main()
