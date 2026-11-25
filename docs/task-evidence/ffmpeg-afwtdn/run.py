# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local canonical report, contract and source manifest."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_report() -> str:
    payload = reference.canonical_report_bytes(reference.build_report())
    (HERE / "report.json").write_bytes(payload)
    digest = sha256(payload)
    (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    print(f"report_sha256={digest} bytes={len(payload)}")
    return digest


def write_contract() -> str:
    payload = reference.canonical_bytes(reference.build_contract()) + b"\n"
    (HERE / "contract.json").write_bytes(payload)
    digest = sha256(payload)
    print(f"contract_sha256={digest} bytes={len(payload)}")
    return digest


def write_sources() -> int:
    entries = reference.pin_entries()
    lines = ["# " + "SPDX-FileCopyrightText" + ": 2026 Tsakanyan Hovhannes",
             "# " + "SPDX-License" + "-Identifier: Apache-2.0"]
    lines.extend(f"{digest}  {raw}" for raw, digest in entries)
    (HERE / "SOURCES.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"pins={len(entries)}")
    return len(entries)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in ("report.json", "contract.json", "SOURCES.sha256", "all"):
        print("usage: run.py {report.json|contract.json|SOURCES.sha256|all}", file=sys.stderr)
        return 2
    mode = argv[1]
    if mode in ("report.json", "all"):
        write_report()
    if mode in ("contract.json", "all"):
        write_contract()
    if mode in ("SOURCES.sha256", "all"):
        write_sources()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
