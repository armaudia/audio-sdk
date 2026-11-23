# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the canonical synthetic report and its SHA-256 sidecar."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixture as ref  # noqa: E402


def write_report(root: Path = HERE) -> Path:
    root = Path(root).resolve()
    text = ref.canonical_bytes(ref.build_report()).decode("ascii")
    report = root / "report.json"
    sidecar = root / "report.json.sha256"
    report.write_text(text, encoding="ascii")
    sidecar.write_text(f"{ref.digest(text.encode('ascii'))}  report.json\n",
                       encoding="ascii")
    return report


if __name__ == "__main__":
    target = write_report()
    print(f"{target}\nsha256:{ref.digest(target.read_bytes())}")
