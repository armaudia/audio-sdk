# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-DUAL-PATH-ECHO-NET evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py            # regenerate, 3x checked
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check    # read-only comparison

The generator writes report.json, report.json.sha256, contract.json and
SOURCES.sha256. Three cold-start rounds must be byte-identical before anything
is written. It never reads audio, downloads anything, loads a weight, invokes a
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


def generate() -> int:
    rounds = [_round() for _ in range(ROUNDS)]
    if any(result != rounds[0] for result in rounds):
        print("FAIL: cold-start rounds are not byte-identical", file=sys.stderr)
        return 1
    result = rounds[0]
    for name, data in result.items():
        (HERE / name).write_bytes(data)
    print(f"report_sha256={reference.sha256_bytes(result['report.json'])} "
          f"contract_sha256={reference.sha256_bytes(result['contract.json'])} "
          f"sources_sha256={reference.sha256_bytes(result['SOURCES.sha256'])} "
          f"rounds={ROUNDS}")
    return 0


def check() -> int:
    expected = _round()
    failures = []
    for name in FILES:
        path = HERE / name
        if not path.is_file():
            failures.append(name + ": missing")
        elif path.read_bytes() != expected[name]:
            failures.append(name + ": stale")
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print(f"check_ok=1 report_sha256="
          f"{reference.sha256_bytes(expected['report.json'])} rounds={ROUNDS}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="compare current files with a fresh build")
    options = parser.parse_args()
    return check() if options.check else generate()


if __name__ == "__main__":
    sys.exit(main())
