# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""CLI entry point for the synthetic bridge-protocol evidence package."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Dict, Optional

import crosscheck
import fixture
import reference

ROOT = Path(__file__).resolve().parent


def write_report(out_dir: Path) -> Dict[str, str]:
    """Write a byte-deterministic report and its SHA-256 sidecar."""
    out_dir.mkdir(parents=True, exist_ok=True)
    data = reference.report_bytes()
    (out_dir / reference.REPORT).write_bytes(data)
    sidecar = reference.sidecar_bytes(data)
    (out_dir / reference.SIDECAR).write_bytes(sidecar)
    return {
        "report_sha256": reference.sha256_bytes(data),
        "sidecar_sha256": reference.sha256_bytes(sidecar),
        "out_dir": str(out_dir),
    }


def demo() -> str:
    """One typical API use: validate a caller-owned synthetic request."""
    item = fixture.build_fixture("valid_without_optional")
    reference.validate_descriptor(item["descriptor"])
    request_status = reference.validate_request(item["request"], item["descriptor"])
    reference.validate_result(item["result"], item["request"], item["descriptor"], request_status)
    decision = reference.evaluate_case(item)
    return "%s -> %s/%s, qualified=%s" % (
        decision["case_id"], decision["actual_status"],
        decision["actual_reason"], str(decision["qualified"]).lower())


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="write report.json and its sidecar")
    parser.add_argument("--sources", action="store_true", help="verify SOURCES.sha256 pins")
    parser.add_argument("--crosscheck", action="store_true", help="regenerate and byte-compare the report")
    parser.add_argument("--demo", action="store_true", help="show one typical API validation use")
    parser.add_argument("--version", action="store_true", help="print tool version and authoring runtime")
    parser.add_argument("--out", default=str(ROOT), help="output directory for --report")
    parser.add_argument("--workspace", default=None, help="workspace root for --sources")
    args = parser.parse_args(argv)

    selected = [args.report, args.sources, args.crosscheck, args.demo, args.version]
    if sum(bool(flag) for flag in selected) != 1:
        parser.error("select exactly one of --report, --sources, --crosscheck, --demo, --version")

    if args.version:
        contract = reference.load_package_json(reference.CONTRACT)
        tool = contract["tool_profile"]
        print("%s %s | authoring python %s | install %s" % (
            tool["name"], tool["version"], tool["authoring_runtime"]["python"],
            tool["install_location"]))
        return 0
    if args.demo:
        print(demo())
        return 0
    if args.report:
        result = write_report(Path(args.out).expanduser().resolve())
        print("report_sha256=" + result["report_sha256"])
        print("sidecar_sha256=" + result["sidecar_sha256"])
        return 0
    if args.sources:
        result = reference.check_sources(args.workspace)
        print("sources_status=" + result["status"])
        print("pins_total=" + str(result["pins_total"]))
        print("pins_checked=" + str(result["pins_checked"]))
        print("adapters_readme_sha256=" + str(result["adapters_readme_sha256"]))
        for problem in result["problems"]:
            print("problem=" + problem, file=sys.stderr)
        return 0 if result["status"] == "ok" else 1
    result = crosscheck.run(repeats=3)
    print("crosscheck_status=" + result["status"])
    print("repeats=" + str(result["repeats"]))
    for problem in result["problems"]:
        print("problem=" + problem, file=sys.stderr)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
