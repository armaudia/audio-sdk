# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate deterministic SpatialNet task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
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
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"


def generate_once() -> Dict[str, bytes]:
    report = reference.report_bytes()
    sidecar = reference.sidecar_bytes(report)
    sources = reference.sources_bytes(report, sidecar)
    report_obj = reference.strict_loads(report.decode("utf-8"))
    contract = reference.contract_bytes(report, sidecar, sources, report_obj)
    return {
        "report.json": report,
        "report.json.sha256": sidecar,
        "SOURCES.sha256": sources,
        "contract.json": contract,
    }


def write_outputs(outputs: Dict[str, bytes]) -> None:
    for name, data in outputs.items():
        (HERE / name).write_bytes(data)


def check_outputs(outputs: Dict[str, bytes]) -> int:
    failures = []
    for name, data in outputs.items():
        path = HERE / name
        if not path.is_file():
            failures.append(name + ": missing")
        elif path.read_bytes() != data:
            failures.append(name + ": stale")
    if failures:
        for f in failures:
            print("FAIL: " + f, file=sys.stderr)
        return 1
    print("check_ok=1 report_sha256=" + reference.sha256_bytes(outputs["report.json"]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = generate_once()
    if args.check:
        return check_outputs(outputs)
    rounds = [generate_once() for _ in range(ROUNDS)]
    if any(r != rounds[0] for r in rounds):
        print("FAIL: cold-start rounds are not byte-identical", file=sys.stderr)
        return 1
    write_outputs(rounds[0])
    print(
        "report_sha256=" + reference.sha256_bytes(rounds[0]["report.json"]) +
        " contract_sha256=" + reference.sha256_bytes(rounds[0]["contract.json"]) +
        " sources_sha256=" + reference.sha256_bytes(rounds[0]["SOURCES.sha256"]) +
        " rounds=" + str(ROUNDS)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
