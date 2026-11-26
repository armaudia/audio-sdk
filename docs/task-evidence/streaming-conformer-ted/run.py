# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate and check SDK-STREAMING-CONFORMER-TED evidence artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import reference

FILES = ("report.json", "report.json.sha256", "SOURCES.sha256", "contract.json")


def build() -> dict[str, bytes]:
    report = reference.report_bytes()
    sidecar = reference.sidecar_bytes(report)
    sources = reference.sources_bytes(report, sidecar)
    contract = reference.contract_bytes(report, sidecar, sources, reference.strict_loads(report.decode("utf-8")))
    return {
        "report.json": report,
        "report.json.sha256": sidecar,
        "SOURCES.sha256": sources,
        "contract.json": contract,
    }


def write_all(directory: Path) -> None:
    for name, payload in sorted(build().items()):
        (directory / name).write_bytes(payload)


def check_all(directory: Path) -> list[str]:
    errors: list[str] = []
    expected = build()
    for name in FILES:
        path = directory / name
        if not path.exists():
            errors.append("missing:" + name)
            continue
        actual = path.read_bytes()
        if actual != expected[name]:
            errors.append("stale:" + name)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.all == args.check:
        parser.error("choose exactly one of --all or --check")
    directory = Path(__file__).resolve().parent
    if args.all:
        write_all(directory)
        for name in FILES:
            print(name)
        return 0
    errors = check_all(directory)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
