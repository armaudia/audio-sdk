# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of pins, strict JSON, canonical bytes and scope."""

from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tokenize
from typing import Any, Dict, List

import check_licensing
import fixture
import run as runner

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = fixture.SDK_ROOT
TASK_PREFIX = "docs/task-evidence/rubber-band-r3-offline/"
LICENSE_MARKER = "SPDX" "-License-Identifier: Apache-2.0"


class VerificationFailure(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def strict_json(path: Path) -> Any:
    def no_duplicates(pairs):
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r} in {path.name}")
            result[key] = value
        return result

    def reject_constant(value: str):
        raise ValueError(f"nonfinite JSON constant {value!r} in {path.name}")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicates,
                      parse_constant=reject_constant)


def check_spdx() -> List[str]:
    problems: List[str] = []
    for path in sorted(TASK_DIR.glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 2 or "SPDX-FileCopyrightText:" not in lines[0] or LICENSE_MARKER not in lines[1]:
            problems.append(f"SPDX header missing: {path.name}")
        with path.open("rb") as handle:
            for token in tokenize.tokenize(handle.readline):
                if token.type == tokenize.STRING and LICENSE_MARKER in token.string:
                    problems.append(f"literal full license marker in Python string: {path.name}")
    return problems


def check_descriptors(report: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    contract = strict_json(TASK_DIR / "contract.json")
    adapter = strict_json(TASK_DIR / "adapter.json")
    provider = strict_json(TASK_DIR / "provider.json")
    for name, document in (("contract.json", contract), ("adapter.json", adapter),
                           ("provider.json", provider), ("report.json", report)):
        require(document.get("SPDX-FileCopyrightText") == "2026 Tsakanyan Hovhannes",
                f"{name}: wrong SPDX copyright metadata")
        require(document.get("SPDX-License-Identifier") == "Apache-2.0",
                f"{name}: wrong SPDX license metadata")
    require(contract["status"] == "proposal_only_not_qualified", "contract status changed")
    require(contract["decision"] == "DEFER", "contract decision changed")
    require(contract["processor_exposure"] == "none", "processor exposure is not none")
    require(contract["write_scope"] == TASK_PREFIX, "unexpected write scope")
    require(adapter["default_enabled"] is False, "adapter must default to off")
    require(adapter["registered"] is False, "adapter must stay unregistered")
    require(adapter["public_c_boundary"] == "not used", "no C boundary is in scope")
    require(provider["default_enabled"] is False, "provider descriptor must default to off")
    require(provider["registered"] is False, "provider descriptor must stay unregistered")
    require(provider["c_provider"] is False, "no C provider is in scope")
    require(contract["verification_profile"] == "rate", "wrong verification profile")
    return problems


def check_pins(report: Dict[str, Any]) -> None:
    for category in ("source_pins", "boundary_pins"):
        for path, item in report[category].items():
            require(item["verified"] is True, f"{category} not verified: {path}")
            require(item["expected"] == item["actual"], f"{category} hash mismatch: {path}")
    manifest = (TASK_DIR / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    require(manifest == runner.source_manifest_lines(), "SOURCES.sha256 manifest mismatch")
    for line in manifest:
        digest, path = line.split("  ", 1)
        require(len(digest) == 64, f"bad digest in SOURCES.sha256: {path}")
        require((TASK_DIR / path).is_file(), f"missing pinned artifact: {path}")


def check_report(report: Dict[str, Any]) -> None:
    canonical = fixture.canonical_bytes(report)
    require((TASK_DIR / "report.json").read_bytes() == canonical + b"\n",
            "report.json is not canonical bytes plus one trailing newline")
    sidecar = (TASK_DIR / "report.json.sha256").read_text(encoding="ascii").strip()
    require(sidecar == fixture.sha256_bytes(canonical), "digest sidecar mismatch")
    cross = report["crosscheck"]
    digests = cross["cold_start_core_digests"]
    require(len(digests) == 3 and len(set(digests)) == 1, "cold-start digests differ")
    require(cross["byte_identical"] is True, "crosscheck not byte identical")
    require(cross["canonical_core_digest"] == digests[0], "core digest inconsistent")
    require(cross["tolerance_widened"] is False, "tolerance widening claimed")
    require(cross["provider_substituted"] is False, "provider substitution claimed")
    require(report["status"] == "proposal_only_not_qualified", "report status changed")
    require(report["decision"] == "DEFER", "report decision changed")
    require(report["qualification"]["no_missing_result_may_qualify"] is True,
            "missing-result qualification guard disabled")
    require(report["qualification"]["missing_result_promoted"] is False,
            "missing result promoted")
    for name, case in report["cases"].items():
        if not case["all_required_results_present"] or case["adverse_control"]:
            require(case["candidate_qualified"] is False,
                    f"{name}: adverse or incomplete case qualified")
        require(case["signal"]["nonfinite"] == 0, f"{name}: nonfinite output")
    for item in report["invalid_and_missing_cases"]:
        require(item["candidate_qualified"] is False, f"{item['case_id']}: invalid case qualified")
        require(item["missing_result_promoted"] is False, f"{item['case_id']}: missing result promoted")


def check_repeatability() -> None:
    expected_text = (TASK_DIR / "report.json").read_bytes()
    outputs: List[bytes] = []
    for _ in range(3):
        completed = subprocess.run([sys.executable, "run.py", "--report"], cwd=TASK_DIR,
                                   capture_output=True, timeout=180)
        require(completed.returncode == 0,
                f"run.py --report failed: {completed.stderr.decode('utf-8', 'replace')}")
        outputs.append(completed.stdout)
        require((TASK_DIR / "report.json").read_bytes() == expected_text,
                "CLI regeneration changed report.json bytes")
        sidecar = (TASK_DIR / "report.json.sha256").read_bytes()
        require(sidecar == fixture.sha256_bytes(fixture.canonical_bytes(
            strict_json(TASK_DIR / "report.json"))).encode("ascii") + b"\n",
            "CLI regeneration changed sidecar bytes")
    require(len(set(outputs)) == 1, "three CLI report stdout streams differ")


def check_scope() -> None:
    completed = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, timeout=60,
    )
    require(completed.returncode == 0, "git status failed")
    for line in completed.stdout.decode("utf-8").splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        require(path.startswith(TASK_PREFIX), f"change outside task scope: {path}")


def main() -> int:
    try:
        problems = check_spdx() + check_licensing.audit()
        require(not problems, "licensing/SPDX problems: " + "; ".join(problems))
        report = strict_json(TASK_DIR / "report.json")
        check_descriptors(report)
        check_pins(report)
        check_report(report)
        check_repeatability()
        check_scope()
    except (VerificationFailure, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"verify: FAIL - {error}")
        return 1
    print("verify: ok")
    print(f"strict_json_files=4")
    print(f"source_pins={len(report['source_pins'])}")
    print(f"boundary_pins={len(report['boundary_pins'])}")
    print(f"cold_start_repeats=3 byte_identical=true")
    print(f"cases={len(report['cases'])} decision={report['decision']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
