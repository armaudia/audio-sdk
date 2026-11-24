# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""One-command verification of the task-local synthetic evidence package."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import check_licensing
import crosscheck
import reference

ROOT = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TEST_NAME = "test_reference.py"
MIN_TESTS = 30


def _environment() -> Dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def run_tests(cwd: Path) -> Dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", TEST_NAME], cwd=str(cwd),
        env=_environment(), capture_output=True, text=True, check=False)
    output = completed.stdout + completed.stderr
    match = re.search(r"^Ran (\d+) tests?", output, re.MULTILINE)
    count = int(match.group(1)) if match else 0
    ok = completed.returncode == 0 and "OK" in output and count >= MIN_TESTS
    return {"status": "ok" if ok else "failed", "tests": count,
            "summary": output.strip().splitlines()[-1] if output.strip() else "",
            "stderr": completed.stderr.strip()}


def _ignore_pycache(directory: str, names: List[str]) -> List[str]:
    return [name for name in names if name in {"__pycache__", "*.pyc"}]


def extracted_package_check(workspace: Path) -> Dict[str, Any]:
    """Copy only the package and reproduce tests, report and source pins."""
    work = Path(tempfile.mkdtemp(prefix="bench-subprocess-extracted-", dir=TEMP_ROOT
                                 if TEMP_ROOT.is_dir() else None))
    copy = work / "bench-subprocess-protocol"
    try:
        shutil.copytree(ROOT, copy, ignore=_ignore_pycache)
        environment = _environment()
        environment["AUDIOML_WORKSPACE"] = str(workspace)
        tests = subprocess.run(
            [sys.executable, "-m", "unittest", TEST_NAME], cwd=str(copy),
            env=environment, capture_output=True, text=True, check=False)
        out = work / "generated"
        report = subprocess.run(
            [sys.executable, "run.py", "--report", "--out", str(out)], cwd=str(copy),
            env=environment, capture_output=True, text=True, check=False)
        sources = subprocess.run(
            [sys.executable, "run.py", "--sources", "--workspace", str(workspace)],
            cwd=str(copy), env=environment, capture_output=True, text=True, check=False)
        expected_report = (ROOT / reference.REPORT).read_bytes()
        expected_sidecar = (ROOT / reference.SIDECAR).read_bytes()
        byte_match = ((out / reference.REPORT).is_file()
                      and (out / reference.REPORT).read_bytes() == expected_report
                      and (out / reference.SIDECAR).read_bytes() == expected_sidecar)
        problems: List[str] = []
        if tests.returncode != 0 or "OK" not in (tests.stdout + tests.stderr):
            problems.append("extracted unit tests failed")
        if report.returncode != 0:
            problems.append("extracted report generation failed: " + report.stderr.strip())
        if sources.returncode != 0 or "sources_status=ok" not in sources.stdout:
            problems.append("extracted source pin check failed: " + sources.stderr.strip())
        if not byte_match:
            problems.append("extracted report is not byte-identical")
        return {"status": "ok" if not problems else "failed", "problems": problems}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    checks: List[Tuple[str, bool, str]] = []
    workspace: Optional[Path] = reference.find_workspace()

    tests = run_tests(ROOT)
    checks.append(("unit_tests", tests["status"] == "ok",
                   "%d tests, %s" % (tests["tests"], tests["summary"])))

    sources = reference.check_sources(str(workspace) if workspace else None)
    checks.append(("source_pins", sources["status"] == "ok",
                   "%d/%d pins verified" % (sources["pins_checked"], sources["pins_total"])))

    strict = True
    json_count = 0
    for path in sorted(ROOT.rglob("*.json")):
        if "__pycache__" in path.parts:
            continue
        json_count += 1
        try:
            reference.strict_loads(path.read_text(encoding="utf-8"))
        except reference.Reject:
            strict = False
    checks.append(("strict_json", strict, "%d JSON files" % json_count))

    data = reference.report_bytes()
    report_match = ((ROOT / reference.REPORT).read_bytes() == data
                    and (ROOT / reference.SIDECAR).read_bytes() == reference.sidecar_bytes(data))
    checks.append(("report_model", report_match,
                   "report_sha256=" + reference.sha256_bytes(data)))

    cross = crosscheck.run(repeats=3)
    checks.append(("cold_start_crosscheck", cross["status"] == "ok",
                   "%d repeats, %d problem(s)" % (cross["repeats"], len(cross["problems"]))))

    licensing = check_licensing.check()
    checks.append(("spdx_reuse", licensing["status"] == "ok",
                   "%d tagged files" % licensing["explicitly_tagged_files"]))

    report = reference.build_report()
    boundary = report["boundary"]
    boundary_ok = (boundary["status"] == "proposal_only_not_qualified"
                   and boundary["release_gate"] == "DEFER"
                   and not boundary["public_api_abi_changed"]
                   and not boundary["installed_v0_behavior_changed"]
                   and not boundary["provider_registered"]
                   and not boundary["provider_linked"]
                   and not boundary["production_callback_registered"]
                   and report["summary"]["all_checks_green"])
    checks.append(("boundary_and_controls", boundary_ok,
                   "status=%s, gate=%s, qualified=%d" % (
                       boundary["status"], boundary["release_gate"],
                       report["summary"]["qualified_candidates"])))

    if workspace is None:
        extracted = {"status": "failed", "problems": ["workspace root unavailable"]}
    else:
        extracted = extracted_package_check(workspace)
    checks.append(("extracted_package", extracted["status"] == "ok",
                   "%d problem(s)" % len(extracted["problems"])))

    contract = reference.load_package_json(reference.CONTRACT)
    version_ok = (contract["tool_profile"]["version"] == "0.1.0"
                  and contract["tool_profile"]["authoring_runtime"]["python"] == "3.11.5")
    checks.append(("tool_profile", version_ok,
                   "%s %s, python>=%s" % (
                       contract["tool_profile"]["name"], contract["tool_profile"]["version"],
                       contract["tool_profile"]["minimum_python"])))

    for name, ok, detail in checks:
        print("%s: %s (%s)" % ("PASS" if ok else "FAIL", name, detail))
    failed = [name for name, ok, _ in checks if not ok]
    if failed:
        print("verify_result=FAILED " + ",".join(failed))
        return 1
    print("verify_result=OK %d checks" % len(checks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
