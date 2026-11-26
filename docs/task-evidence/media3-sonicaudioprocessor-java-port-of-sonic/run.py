# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local CLI for canonical regeneration and inspection.

``--report`` rebuilds the canonical report three times in one process and
writes only when the bytes are identical.  ``--contract`` regenerates the
pinned contract from the current local artifacts.  ``--sources`` prints the
local SHA-256 manifest.  ``--inspect`` prints a small canonical summary.
``--all`` writes report, contract and sources in the required order.
Nothing outside this evidence directory is written.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import reference

ROOT = Path(__file__).resolve().parent
EXCLUDED = {"SOURCES.sha256"}


def local_artifacts() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        paths.append(path)
    return paths


def render_sources() -> bytes:
    lines = []
    for path in local_artifacts():
        relative = path.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, relative))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_report() -> str:
    payload, digest, canonical_digest = reference.render_report()
    (ROOT / "report.json").write_bytes(payload)
    (ROOT / "report.json.sha256").write_text(digest + "\n", encoding="ascii")
    return canonical_digest


def write_contract() -> str:
    payload = reference.canonical_bytes(reference.contract_payload()) + b"\n"
    (ROOT / "contract.json").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def write_sources() -> str:
    payload = render_sources()
    (ROOT / "SOURCES.sha256").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and report.json.sha256")
    group.add_argument("--contract", action="store_true",
                       help="regenerate contract.json from local pins")
    group.add_argument("--sources", action="store_true",
                       help="print the local SOURCES.sha256 manifest")
    group.add_argument("--inspect", action="store_true",
                       help="print a canonical boundary summary")
    group.add_argument("--all", action="store_true",
                       help="write report, contract and sources in order")
    args = parser.parse_args(argv)
    if args.report:
        print(write_report())
        return 0
    if args.contract:
        print(write_contract())
        return 0
    if args.sources:
        sys.stdout.buffer.write(render_sources())
        return 0
    if args.all:
        canonical = write_report()
        contract = write_contract()
        sources = write_sources()
        print("report " + canonical)
        print("contract " + contract)
        print("sources " + sources)
        return 0
    payload = reference.canonical_bytes(reference.inspect_payload())
    sys.stdout.buffer.write(payload + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
