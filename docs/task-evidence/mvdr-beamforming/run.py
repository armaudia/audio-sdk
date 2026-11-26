# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-MVDR-BEAMFORMING package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py            # regenerate, 3x checked
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check    # read-only comparison

The generator writes report.json, report.json.sha256, contract.json and
SOURCES.sha256.  Three cold-start rounds must be byte-identical before the
result is accepted.  It never reads audio, downloads anything, loads a model,
estimates a covariance, applies a mask, invokes a runtime or hashes the
mutable full task board.
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


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def generate_round() -> Dict[str, str]:
    report = reference.build_report()
    report_text, report_digest = reference.canonical_report(report)
    _write("report.json", report_text.encode("utf-8"))
    _write("report.json.sha256", (report_digest + "\n").encode("ascii"))

    contract = reference.build_contract()
    contract_text = reference.canonical_text(contract) + "\n"
    _write("contract.json", contract_text.encode("utf-8"))

    sources = reference.sources_bytes()
    _write("SOURCES.sha256", sources)

    return {
        "report_sha256": reference.sha256_bytes(report_text.encode("utf-8")),
        "contract_sha256": reference.sha256_bytes(contract_text.encode("utf-8")),
        "sources_sha256": reference.sha256_bytes(sources),
    }


def generate() -> int:
    rounds = [generate_round() for _ in range(ROUNDS)]
    if any(result != rounds[0] for result in rounds):
        print("FAIL: cold-start rounds are not byte-identical", file=sys.stderr)
        return 1
    result = rounds[0]
    print(f"report_sha256={result['report_sha256']} "
          f"contract_sha256={result['contract_sha256']} "
          f"sources_sha256={result['sources_sha256']} rounds={ROUNDS}")
    return 0


def check() -> int:
    report = reference.build_report()
    report_text, report_digest = reference.canonical_report(report)
    contract = reference.build_contract()
    contract_text = reference.canonical_text(contract) + "\n"
    sources = reference.sources_bytes()
    expected = {
        "report.json": report_text.encode("utf-8"),
        "report.json.sha256": (report_digest + "\n").encode("ascii"),
        "contract.json": contract_text.encode("utf-8"),
        "SOURCES.sha256": sources,
    }
    failures = []
    for name, data in expected.items():
        path = HERE / name
        if not path.is_file():
            failures.append(name + ": missing")
        elif path.read_bytes() != data:
            failures.append(name + ": stale")
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print(f"check_ok=1 report_sha256={report_digest} rounds={ROUNDS}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="compare current files with a fresh deterministic build")
    options = parser.parse_args()
    return check() if options.check else generate()


if __name__ == "__main__":
    sys.exit(main())
