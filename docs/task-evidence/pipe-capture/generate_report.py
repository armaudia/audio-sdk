# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the canonical SDK-PIPE-CAPTURE report and SHA-256 sidecar."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import host  # noqa: E402


def write_report(root: Path = HERE) -> Path:
    root = Path(root).resolve()
    payload = host.canonical_bytes(host.build_report())
    report = root / "report.json"
    sidecar = root / "report.json.sha256"
    report.write_bytes(payload)
    sidecar.write_text(f"{host.sha256(payload)}  report.json\n", encoding="ascii")
    return report


if __name__ == "__main__":
    target = write_report()
    print(f"{target}\nsha256:{host.sha256(target.read_bytes())}")
