#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict verifier for the deterministic SDK-SURVEY-ENG-02 evidence map."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import build

TASK_DIR = Path(__file__).resolve().parent
WORKSPACE = build.find_workspace(build.SDK_ROOT)

REQUIRED_FILES = {
    "README.md",
    "README.md.license",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "build.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "test_evidence_map.py",
    "verify.py",
}

LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX" "-License-Identifier: Apache-2.0\n"
)

README_MARKERS = (
    "Status: survey only",
    "S27",
    "S41",
    "Delay estimation",
    "Rate adjustment",
    "Drift compensation",
    "Learned estimation",
    "Feasibility follow-up",
    "report.json",
    "SOURCES.sha256",
    "PYTHONDONTWRITEBYTECODE=1",
    "reuse lint",
    "git diff --check",
    "No public benchmark claim",
)

BANNED_CLAIMS = (
    "achieves public benchmark",
    "device qualification passed",
    "listening test passed",
    "release approved",
    "live clock drift implemented",
    "provider enabled by this survey",
    "ABI changed by this survey",
)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_file_set() -> None:
    actual = {path.name for path in TASK_DIR.iterdir()}
    ensure(actual == REQUIRED_FILES, f"unexpected task-local files: {sorted(actual ^ REQUIRED_FILES)}")
    for name in ("build.py", "verify.py", "test_evidence_map.py"):
        head = (TASK_DIR / name).read_text(encoding="utf-8").splitlines()[:3]
        ensure(any("SPDX" "-License-Identifier: Apache-2.0" in line for line in head),
               f"missing SPDX header in {name}")
    for name in ("README.md.license", "report.json.license",
                 "report.json.sha256.license", "SOURCES.sha256.license"):
        ensure((TASK_DIR / name).read_text(encoding="utf-8") == LICENSE_TEXT,
               f"incorrect license sidecar: {name}")


def check_scope() -> None:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=build.SDK_ROOT,
        capture_output=True,
        check=True,
    )
    records = [item for item in proc.stdout.decode("utf-8", "replace").split("\0") if item]
    prefix = "docs/task-evidence/survey-eng-02/"
    index = 0
    while index < len(records):
        record = records[index]
        status, path = record[:2], record[3:]
        if status.startswith(("R", "C")):
            index += 1
            ensure(index < len(records), "malformed git rename/copy status")
            path = records[index]
        ensure(path == prefix.rstrip("/") or path.startswith(prefix),
               f"worktree change outside task scope: {path}")
        index += 1


def check_report(report: dict) -> None:
    board = json.loads(build.read_text(WORKSPACE, "audio-benchmark-platform/plan/swarm/TASKS.json"))
    task = next(item for item in board["tasks"] if item["id"] == "SDK-SURVEY-ENG-02")
    report_keys = {"id": "task_id", "title": "task_title"}
    for key in ("id", "title", "mode", "repository", "owner"):
        report_key = report_keys.get(key, key)
        ensure(report[report_key] == task[key], f"board drift for task.{key}")
    ensure(report["reviewer"] == task["claim"]["reviewer"], "board drift for task.claim.reviewer")
    for key in ("depends_on", "write_scope", "deliverable", "acceptance"):
        report_key = "dependencies" if key == "depends_on" else (
            "board_deliverable" if key == "deliverable" else (
                "board_acceptance" if key == "acceptance" else key))
        ensure(report[report_key] == task[key], f"board drift for task.{key}")
    ensure(report["base_commit"] == build.BASE_COMMIT, "wrong base commit")
    ensure(report["branch"] == build.BRANCH, "wrong branch")
    ensure(report["worktree"] == build.WORKTREE, "wrong worktree")
    ensure(report["schema_id"] == build.SCHEMA_ID, "wrong schema id")
    ensure(report["disposition"].startswith("survey_only:"), "survey-only disposition missing")

    category = report["catalogue"]["category"]
    ensure(category["id"] == "ENG-02", "wrong catalog category")
    ensure(category["source_ids"] == ["S27", "S41"], "source leads differ from registry")
    ensure(category["method_families"]["classic"] == "Delay estimation; rate adjustment; drift compensation",
           "classic family text differs from registry")
    ensure("Learned estimation is optional research, not required" in category["method_families"]["ml"],
           "ML family text differs from registry")

    leads = report["source_leads"]
    ensure([lead["id"] for lead in leads] == ["S27", "S41"], "source lead coverage mismatch")
    registry = json.loads(build.read_text(WORKSPACE, "research/category_registry.json"))
    registry_sources = {item["id"]: item for item in registry["sources"]}
    for lead in leads:
        source = registry_sources[lead["id"]]
        for key in ("title", "url", "researcher", "access_scope"):
            ensure(lead[key] == source[key], f"source lead drift: {lead['id']}.{key}")
        ensure(bool(lead["historical_executions"]) and bool(lead["limits"]),
               f"source lead {lead['id']} lacks mapping detail")

    inventory = json.loads(build.read_text(WORKSPACE, "audio-benchmark-platform/plan/INVENTORY.json"))
    components = {item["id"]: item for item in inventory["components"]}
    ensure([item["component_id"] for item in report["component_matches"]] == list(build.COMPONENTS),
           "component mapping set changed")
    for item in report["component_matches"]:
        record = components[item["component_id"]]
        for key in ("name", "task", "evidence_status", "verification_profile",
                    "repository", "disposition"):
            ensure(item[key] == record[key], f"inventory drift: {item['component_id']}.{key}")

    classic = report["method_families"]["classic"]
    ensure([entry["family"] for entry in classic["entries"]] ==
           ["Delay estimation", "Rate adjustment", "Drift compensation"],
           "classic family audit incomplete")
    for entry in classic["entries"]:
        for key in ("comparison_inputs", "controls", "assets", "local_outcomes", "reported_outcomes", "limits"):
            ensure(bool(entry[key]), f"empty {key} for {entry['family']}")
    ensure(report["method_families"]["ml"] == build.ML_AUDIT, "ML audit changed")
    ensure(report["method_families"]["ml"]["audited"] is True, "ML family was not audited")

    audit = report["coverage_audit"]
    ensure(audit["classical_families_audited"] == [entry["family"] for entry in classic["entries"]],
           "coverage audit disagrees with classic entries")
    ensure(audit["source_leads_covered"] == ["S27", "S41"], "coverage audit source mismatch")
    ensure(audit["ml_family_audited"] is True and audit["historical_executions_covered"] is True,
           "coverage audit is incomplete")
    ensure(len(audit["missing_evidence_reasons"]) >= 5, "missing evidence is not explained")

    ensure(report["gap"] == build.GAP, "feasibility gap changed")
    ensure(report["gap"]["status"] == "proposed_unassigned_not_run", "gap is not feasibility-only")
    ensure(report["gap"]["owner"] is None and report["gap"]["board_entry"] is False,
           "gap wrongly assigned or boarded")
    ensure("No real audio" in report["gap"]["smallest_check"]["exclusions"],
           "gap bounds are incomplete")

    ensure(set(report["prohibited_claims"].values()) == {"not_made"},
           "a prohibited claim was promoted")
    ensure(report["source_pin_policy"]["sidecar"] == "SOURCES.sha256", "wrong pin sidecar")
    ensure(report["reproduction"] == {
        "python": "3.12.16",
        "env": "PYTHONDONTWRITEBYTECODE=1",
        "builder": "python3 build.py",
        "verifier": "python3 verify.py",
        "tests": "python3 docs/task-evidence/survey-eng-02/test_evidence_map.py -v",
        "repo_checks": ["scripts/ci.py --output build/ci", "reuse lint", "git diff --check"],
    }, "reproduction recipe changed")


def check_artifacts() -> str:
    expected_bytes, digests = build.build_report(WORKSPACE)
    report_bytes = (TASK_DIR / "report.json").read_bytes()
    ensure(report_bytes == expected_bytes, "report.json is not reproducible from pinned sources")
    ensure(build.canonical(json.loads(report_bytes)) == report_bytes, "report.json is not canonical")

    report_digest = build.sha256_bytes(report_bytes)
    digest_line = (TASK_DIR / "report.json.sha256").read_text(encoding="utf-8")
    ensure(digest_line == f"{report_digest}  report.json\n", "report digest sidecar is stale")

    expected_sources = "".join(f"{digests[path]}  {path}\n" for path in sorted(digests))
    sources_text = (TASK_DIR / "SOURCES.sha256").read_text(encoding="utf-8")
    ensure(sources_text == expected_sources, "SOURCES.sha256 is stale")

    report = json.loads(report_bytes)
    ensure(report["source_pins"] == [
        {"path": path, "sha256": digests[path], "use": build.PINS[path]}
        for path in sorted(build.PINS)
    ], "report source pins disagree with the sidecar")
    return report_digest


def check_readme() -> None:
    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    for marker in README_MARKERS:
        ensure(marker in text, f"README marker missing: {marker}")
    lowered = text.lower()
    for phrase in BANNED_CLAIMS:
        ensure(phrase not in lowered, f"README contains prohibited claim: {phrase}")


def main() -> None:
    check_file_set()
    check_scope()
    check_artifacts()
    report = json.loads((TASK_DIR / "report.json").read_bytes())
    check_report(report)
    check_readme()
    digest = build.sha256_bytes((TASK_DIR / "report.json").read_bytes())
    print(f"OK: ENG-02 evidence map is strict and reproducible")
    print(f"report.json  {digest}")


if __name__ == "__main__":
    main()
