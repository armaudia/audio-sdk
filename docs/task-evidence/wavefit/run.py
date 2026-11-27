# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate SDK-WAVEFIT blocker evidence deterministically."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

LOCAL_PIN_FILES = (
    "LICENSES.md", "README.md", "README.md.license", "SOURCES.sha256.license", "contract.json",
    "contract.json.license", "reference.py", "report.json", "report.json.license",
    "report.json.sha256", "report.json.sha256.license", "run.py", "test_reference.py", "verify.py",
)


def main(argv: list[str]) -> int:
    args = set(argv[1:]) or {"all"}
    if not args <= {"all"}:
        print("usage: run.py [all]", file=sys.stderr)
        return 2
    digests = []
    for _ in range(3):
        written = reference.write_artifacts()
        digests.append((written["report.json"], written["SOURCES.sha256"]))
    if len(set(digests)) != 1:
        print("FAIL: non-deterministic regeneration", file=sys.stderr)
        return 1
    print(f"repeat=3 byte_identical=true report_sha256={digests[0][0]} sources_sha256={digests[0][1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
