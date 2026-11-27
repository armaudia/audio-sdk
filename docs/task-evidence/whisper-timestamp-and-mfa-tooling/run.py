#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic generator for whisper-timestamp-and-mfa-tooling evidence."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_contract_report() -> None:
    contract = reference.build_contract()
    report = reference.build_report()
    (HERE / "contract.json").write_bytes(reference.canonical_bytes(contract))
    report_bytes = reference.canonical_bytes(report)
    (HERE / "report.json").write_bytes(report_bytes)
    (HERE / "report.json.sha256").write_text(
        f"{sha256(HERE / 'report.json')}  report.json\n", encoding="utf-8"
    )


def write_sources() -> None:
    rows = []
    for rel, expected in sorted(reference.SOURCE_PINS.items()):
        p = reference.AUDIO_ROOT / rel
        actual = reference.sha256_file(p)
        if actual != expected:
            raise SystemExit(f"source pin mismatch: {rel}")
        rows.append((f"source:{rel}", actual))
    for rel, expected in sorted(reference.BOUNDARY_PINS.items()):
        p = reference.WORKTREE / rel
        actual = reference.sha256_file(p)
        if actual != expected:
            raise SystemExit(f"boundary pin mismatch: {rel}")
        rows.append((f"worktree:{rel}", actual))
    local = [
        "LICENSES.md",
        "README.md",
        "contract.json",
        "contract.json.license",
        "reference.py",
        "report.json",
        "report.json.license",
        "report.json.sha256",
        "report.json.sha256.license",
        "run.py",
        "test_reference.py",
        "verify.py",
    ]
    for name in local:
        rows.append((f"pkg:{name}", sha256(HERE / name)))
    lines = [
        "# SHA-256 pins for SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING task-local evidence.",
        "# source: paths are relative to AUDIO_ROOT; worktree: relative to SDK worktree.",
        "# The mutable shared board is not pinned; only stable row projection is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines += [f"{digest}  {name}" for name, digest in sorted(rows, key=lambda r: r[0])]
    (HERE / "SOURCES.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default="all", choices=["all", "report.json", "sources"])
    args = ap.parse_args()
    if args.target in ("all", "report.json"):
        write_contract_report()
    if args.target in ("all", "sources"):
        write_sources()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
