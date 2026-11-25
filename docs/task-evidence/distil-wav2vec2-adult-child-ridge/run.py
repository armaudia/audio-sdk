# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate a deterministic rate-profile report.json and its sha256 sidecar."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2 or Path(argv[1]).name != "report.json":
        print("usage: run.py report.json", file=sys.stderr)
        return 2
    given = Path(argv[1])
    output = given if given.is_absolute() else HERE / given
    runtime = reference.require_supported_runtime()
    payload = reference.canonical_report_bytes(reference.build_report())
    output.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    output.with_suffix(".json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    print(f"report_sha256={digest} bytes={len(payload)} runtime={'.'.join(map(str, runtime))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
