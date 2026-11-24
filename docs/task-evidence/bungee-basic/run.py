# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical report.json and its sidecar."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run.py OUTPUT_REPORT", file=sys.stderr)
        return 2
    output = Path(argv[1])
    payload = reference.canonical_report_bytes(reference.build_report())
    output.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    output.with_name(output.name + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8")
    print(f"report_sha256={digest} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
