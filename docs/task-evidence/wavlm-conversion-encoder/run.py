# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical generator for the WavLM conversion encoder feasibility evidence package.

Writes only contract.json, report.json, report.json.sha256, README digest tables
and SOURCES.sha256 inside this task-local directory. No model asset is read,
downloaded, reconstructed or executed.
"""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

CONTRACT_PATH = HERE / "contract.json"
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
SOURCES_PATH = HERE / "SOURCES.sha256"
README_PATH = HERE / "README.md"
REPEAT_COUNT = 3


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(
            "run.py requires CPython " + reference.REQUIRED_INTERPRETER
            + " (observed " + observed + ")")


def contract_payload() -> bytes:
    contract = reference.build_contract()
    reference.validate_contract(contract)
    return reference.canonical_bytes(contract) + b"\n"


def report_payload() -> bytes:
    payload = reference.report_bytes()
    report = reference.strict_json_loads(payload.decode("utf-8"))
    reference.validate_report(report)
    return payload


def sidecar_payload(report: bytes) -> bytes:
    return (reference.sha256_bytes(report) + "  report.json\n").encode("ascii")


def refresh_readme() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    README_PATH.write_text(reference.update_readme_tables(text), encoding="utf-8")


def write_once() -> tuple[str, str]:
    CONTRACT_PATH.write_bytes(contract_payload())
    report = report_payload()
    REPORT_PATH.write_bytes(report)
    SIDECAR_PATH.write_bytes(sidecar_payload(report))
    refresh_readme()
    SOURCES_PATH.write_bytes(reference.sources_bytes())
    return reference.sha256_bytes(report), reference.sha256_bytes(SOURCES_PATH.read_bytes())


def verify_reproduction() -> int:
    checks = (
        (CONTRACT_PATH, contract_payload()),
        (REPORT_PATH, report_payload()),
        (SIDECAR_PATH, sidecar_payload(report_payload())),
        (SOURCES_PATH, reference.sources_bytes()),
    )
    failed = 0
    for path, expected in checks:
        if not path.is_file() or path.read_bytes() != expected:
            print("mismatch=" + path.name)
            failed += 1
    text = README_PATH.read_text(encoding="utf-8") if README_PATH.is_file() else ""
    if text != reference.update_readme_tables(text):
        print("mismatch=README.md")
        failed += 1
    print("report_sha256=" + reference.sha256_bytes(report_payload()))
    print("sources_sha256=" + reference.sha256_bytes(reference.sources_bytes()))
    print("ok=" + ("1" if failed == 0 else "0"))
    return 0 if failed == 0 else 1


def main(argv: list[str]) -> int:
    require_interpreter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", choices=("all",))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true")
    group.add_argument("--report", action="store_true")
    group.add_argument("--sources", action="store_true")
    group.add_argument("--stdout-report", action="store_true")
    group.add_argument("--verify-repro", action="store_true")
    args = parser.parse_args(argv[1:])
    if args.stdout_report:
        sys.stdout.buffer.write(report_payload())
        return 0
    if args.verify_repro:
        return verify_reproduction()
    if args.target == "all":
        args.all = True
    if args.report:
        report = report_payload()
        CONTRACT_PATH.write_bytes(contract_payload())
        REPORT_PATH.write_bytes(report)
        SIDECAR_PATH.write_bytes(sidecar_payload(report))
        refresh_readme()
        return 0
    if args.sources:
        SOURCES_PATH.write_bytes(reference.sources_bytes())
        return 0
    observed: set[tuple[str, str]] = set()
    for _ in range(REPEAT_COUNT):
        observed.add(write_once())
    if len(observed) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    report_digest, sources_digest = next(iter(observed))
    print("repeat=" + str(REPEAT_COUNT) + " byte_identical=true report_sha256=" + report_digest + " sources_sha256=" + sources_digest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
