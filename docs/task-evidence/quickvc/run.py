#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic task-local QuickVC evidence.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py            # regenerate 4 artifacts
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --readme   # refresh README table
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check    # read-only comparison

The generator writes report.json, report.json.sha256, contract.json and
SOURCES.sha256. Three cold-start rounds must be byte-identical before anything
is written. It never reads audio, downloads anything, loads a model, invokes a
runtime or hashes the mutable full task board.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
ROUNDS = 3
FILES = ("report.json", "report.json.sha256", "contract.json", "SOURCES.sha256")
README_LINE = r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|"


def _round() -> Dict[str, bytes]:
    report = reference.build_report()
    report_text, report_digest = reference.canonical_report(report)
    contract = reference.build_contract(report, report_digest)
    contract_text = reference.canonical_text(contract) + "\n"
    sidecar = (report_digest + "\n").encode("ascii")
    sources = reference.sources_bytes({
        "report.json": report_text.encode("utf-8"),
        "report.json.sha256": sidecar,
        "contract.json": contract_text.encode("utf-8"),
    })
    return {
        "report.json": report_text.encode("utf-8"),
        "report.json.sha256": sidecar,
        "contract.json": contract_text.encode("utf-8"),
        "SOURCES.sha256": sources,
    }


def _stable_round() -> Dict[str, bytes]:
    rounds = [_round() for _ in range(ROUNDS)]
    if any(result != rounds[0] for result in rounds):
        raise RuntimeError("cold-start rounds are not byte-identical")
    return rounds[0]


def generate() -> int:
    try:
        result = _stable_round()
    except (RuntimeError, reference.ReferenceRejection) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    for name in FILES:
        (HERE / name).write_bytes(result[name])
    print(f"report_sha256={reference.sha256_bytes(result['report.json'])} "
          f"contract_sha256={reference.sha256_bytes(result['contract.json'])} "
          f"sources_sha256={reference.sha256_bytes(result['SOURCES.sha256'])} "
          f"rounds={ROUNDS}")
    return 0


def readme_table() -> str:
    import re

    rows = []
    for name in reference.README_DIGEST_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing README digest target: " + name)
        data = path.read_bytes()
        rows.append(f"| `{name}` | `{reference.sha256_bytes(data)}` "
                    f"| {len(data)} |")
    return "\n".join((
        reference.README_TABLE_START,
        "| Artifact | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
        *rows,
        reference.README_TABLE_END,
    ))


def readme_bytes() -> bytes:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    if text.count(reference.README_TABLE_START) != 1:
        raise RuntimeError("README digest table start marker is not unique")
    if text.count(reference.README_TABLE_END) != 1:
        raise RuntimeError("README digest table end marker is not unique")
    start = text.index(reference.README_TABLE_START)
    end = text.index(reference.README_TABLE_END) + len(
        reference.README_TABLE_END)
    return (text[:start] + readme_table() + text[end:]).encode("utf-8")


def write_readme() -> int:
    try:
        payload = readme_bytes()
    except (OSError, UnicodeDecodeError, RuntimeError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    current = (HERE / "README.md").read_bytes()
    if current == payload:
        print("README.md digest table current")
    else:
        (HERE / "README.md").write_bytes(payload)
        print("README.md digest table updated")
    return 0


def check() -> int:
    try:
        expected = _stable_round()
        readme = readme_bytes()
    except (OSError, UnicodeDecodeError, RuntimeError,
            reference.ReferenceRejection) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    failures = []
    for name in FILES + ("README.md",):
        want = readme if name == "README.md" else expected[name]
        path = HERE / name
        if not path.is_file():
            failures.append(name + ": missing")
        elif path.read_bytes() != want:
            failures.append(name + ": stale")
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print(f"check_ok=1 report_sha256="
          f"{reference.sha256_bytes(expected['report.json'])} rounds={ROUNDS}")
    return 0


def digest() -> int:
    try:
        payload = _stable_round()["report.json"]
    except (RuntimeError, reference.ReferenceRejection) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    print(reference.sha256_bytes(payload))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", action="store_true",
                        help="refresh only the README digest table")
    parser.add_argument("--check", action="store_true",
                        help="compare current files with a fresh build")
    parser.add_argument("--digest", action="store_true",
                        help="print the canonical report digest")
    options = parser.parse_args()
    if options.readme:
        return write_readme()
    if options.check:
        return check()
    if options.digest:
        return digest()
    return generate()


if __name__ == "__main__":
    sys.exit(main())
