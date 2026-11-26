#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the BIC evidence package.

This script never writes into the package. It recomputes every artifact from
its pinned inputs, checks canonical bytes and digests, verifies licensing and
task-local git scope, repeats regeneration in three fresh processes, and
rejects invalid, missing, non-finite or overclaiming evidence.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TASK_PREFIX = reference.TASK_PREFIX
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:local|source|worktree):[A-Za-z0-9_./-]+)$"
)
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode"
)


class VerifyError(Exception):
    pass


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyError(message)


def _check_spdx_header(name: str) -> None:
    head = "\n".join(
        (HERE / name).read_text(encoding="utf-8").splitlines()[:5]
    )
    _check(
        "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes" in head,
        "missing copyright in " + name,
    )
    _check(
        "SPDX-License-" + "Identifier: Apache-2.0" in head,
        "missing license in " + name,
    )


def _check_licenses() -> None:
    for name in (
        "README.md",
        "reference.py",
        "run.py",
        "test_reference.py",
        "verify.py",
    ):
        _check_spdx_header(name)
    for name, sidecar in sorted(run.LICENSE_SIDECARS.items()):
        path = HERE / sidecar
        _check(path.is_file(), "missing SPDX sidecar: " + sidecar)
        _check(
            path.read_text(encoding="utf-8") == reference.LICENSE_TEXT,
            "invalid SPDX sidecar: " + sidecar,
        )
    reuse = reference.SDK_ROOT / "REUSE.toml"
    _check(reuse.is_file(), "REUSE.toml missing")
    _check(
        "docs/**" in reuse.read_text(encoding="utf-8"),
        "REUSE.toml does not cover docs/**",
    )


def _check_unexpected_files() -> None:
    expected = set(run.LOCAL_FILES)
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    _check(not unexpected, "unexpected task-local files: " + ",".join(unexpected))
    _check(not missing, "missing task-local files: " + ",".join(missing))


def _check_git_scope() -> None:
    process = subprocess.run(
        [
            "git",
            "-C",
            str(reference.SDK_ROOT),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "-z",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    _check(process.returncode == 0, "git status failed")
    for entry in process.stdout.split("\0"):
        if not entry:
            continue
        path = entry[3:]
        _check(
            path.startswith(TASK_PREFIX),
            "out-of-scope git change: " + path,
        )


def _check_pins() -> None:
    reference.verify_document_pins()
    for relative in reference.SOURCE_PINS:
        _check(
            (reference.SOURCE_ROOT / relative).is_file(),
            "source pin target missing: " + relative,
        )
    for relative in reference.BOUNDARY_PINS:
        _check(
            (reference.SDK_ROOT / relative).is_file(),
            "worktree pin target missing: " + relative,
        )
    _check(
        reference.BOARD_PATH not in reference.SOURCE_PINS,
        "mutable board is pinned as source",
    )
    _check(
        reference.BOARD_PATH not in reference.BOUNDARY_PINS,
        "mutable board is pinned as boundary",
    )


def _check_sources_manifest() -> None:
    raw = (HERE / "SOURCES.sha256").read_bytes()
    _check(raw == run.sources_bytes(), "SOURCES.sha256 is not byte-identical")
    lines = raw.decode("ascii").splitlines()
    parsed: List[Tuple[str, str]] = []
    for line in lines:
        match = PIN_LINE.fullmatch(line)
        _check(match is not None, "malformed SOURCES line: " + line)
        digest, label = match.groups()
        kind, path = label.split(":", 1)
        _check(".." not in Path(path).parts, "traversing pin: " + label)
        parsed.append((label, digest))
    labels = [label for label, _ in parsed]
    _check(labels == sorted(labels), "SOURCES.sha256 is not sorted")
    _check(len(labels) == len(set(labels)), "SOURCES.sha256 has duplicates")
    _check(
        "local:" + run.SOURCES not in labels,
        "SOURCES.sha256 pins itself",
    )
    _check(
        "source:" + reference.BOARD_PATH not in labels
        and "worktree:" + reference.BOARD_PATH not in labels,
        "mutable board is present in SOURCES.sha256",
    )
    expected = set()
    for name in run.LOCAL_FILES:
        if name not in run.SOURCES_EXCLUDED:
            expected.add("local:" + name)
    for path in reference.SOURCE_PINS:
        expected.add("source:" + path)
    for path in reference.BOUNDARY_PINS:
        expected.add("worktree:" + path)
    _check(set(labels) == expected, "SOURCES.sha256 coverage mismatch")
    for label, digest in parsed:
        kind, path = label.split(":", 1)
        if kind == "local":
            actual = reference.sha256_file(HERE / path)
        elif kind == "source":
            actual = reference.sha256_file(reference.SOURCE_ROOT / path)
        else:
            actual = reference.sha256_file(reference.SDK_ROOT / path)
        _check(actual == digest, "SOURCES digest mismatch: " + label)


def _check_contract() -> None:
    raw = (HERE / "contract.json").read_bytes()
    _check(raw == run.build_contract(), "contract.json is not byte-identical")
    contract = reference.strict_loads(raw.decode("utf-8"))
    _check(contract["SPDX-License-Identifier"] == "Apache-2.0", "contract licence")
    _check(contract["task_id"] == reference.TASK, "contract task")
    _check(contract["component"] == reference.COMPONENT, "contract component")
    _check(contract["category_id"] == reference.CATEGORY_ID, "contract category")
    _check(contract["base_commit"] == reference.BASE_COMMIT, "contract base")
    _check(contract["branch"] == reference.BRANCH, "contract branch")
    _check(contract["worktree"] == reference.CLAIM_WORKTREE, "contract worktree")
    _check(contract["reviewer"] == reference.REVIEWER, "contract reviewer")
    _check(contract["profile"] == reference.PROFILE, "contract profile")
    _check(contract["mode"] == reference.MODE, "contract mode")
    _check(contract["status"] == reference.STATUS, "contract status")
    _check(contract["decision"] == "DEFER", "contract decision")
    _check(
        contract["qualification_status"] == "not_qualified",
        "contract qualification",
    )
    _check(contract["evidence_status"] == "incomplete", "contract evidence")
    _check(contract["proposal_only"] is True, "contract proposal-only")
    qualification = contract["qualification"]
    _check(qualification["decision"] == "DEFER", "contract nested decision")
    _check(
        qualification["status"] == "not_qualified",
        "contract nested qualification",
    )
    _check(
        qualification["candidate_qualified"] is False,
        "contract claims qualification",
    )
    _check(
        qualification["no_missing_result_qualifies_candidate"] is True,
        "contract missing-result rule",
    )
    _check(
        qualification["synthetic_control_is_not_candidate_evidence"] is True,
        "contract promotes synthetic control",
    )
    _check(
        contract["bic_implementation_contract"]["qualification"]
        == "not_qualified",
        "implementation contract qualifies",
    )
    _check(
        contract["caller_asset_contract"]["qualification"] == "not_qualified",
        "caller contract qualifies",
    )
    _check(
        contract["caller_asset_contract"]["required_variant"]
        == reference.REQUIRED_VARIANT,
        "caller variant",
    )
    _check(
        contract["bic_reference_formula"]["qualifies_candidate"] is False,
        "formula qualifies candidate",
    )
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["boundary"] == reference.BOUNDARY, "contract boundary")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract pins")
    _check(
        contract["boundary_pins"] == reference.BOUNDARY_PINS,
        "contract boundary pins",
    )
    _check(
        reference.BOARD_PATH not in contract["source_pins"],
        "contract pins mutable board",
    )
    _check(
        reference.BOARD_PATH not in contract["boundary_pins"],
        "contract pins mutable board as boundary",
    )
    _check(
        contract["mutable_provenance"]["gate"] is False,
        "mutable provenance is gated",
    )
    _check(len(contract["release_gates"]) == 8, "contract gate count")
    _check(
        contract["task_row_identity"] == reference.task_row_identity(),
        "contract task identity",
    )
    expected_artifacts = set(run.LOCAL_FILES) - set(run.CONTRACT_EXCLUDED)
    _check(
        set(contract["artifact_pins"]) == expected_artifacts,
        "contract artifact coverage",
    )
    _check(
        "contract.json" not in contract["artifact_pins"],
        "contract pins itself",
    )
    _check(
        "SOURCES.sha256" not in contract["artifact_pins"],
        "contract pins SOURCES",
    )


def _check_report() -> str:
    raw = (HERE / "report.json").read_bytes()
    expected = reference.canonical_report_bytes(reference.build_report())
    _check(raw == expected, "report.json is not byte-identical")
    report = reference.strict_loads(raw.decode("utf-8"))
    _check(report["task_id"] == reference.TASK, "report task")
    _check(report["component"] == reference.COMPONENT, "report component")
    _check(report["category_id"] == reference.CATEGORY_ID, "report category")
    _check(report["profile"] == "spatial", "report profile")
    _check(report["mode"] == "feasibility", "report mode")
    _check(report["decision"] == "DEFER", "decision is not DEFER")
    _check(report["status"] == reference.STATUS, "status changed")
    _check("incomplete" in report["status"], "status is not incomplete")
    _check(
        report["qualification_status"] == "not_qualified",
        "qualification is not not_qualified",
    )
    _check(report["evidence_status"] == "incomplete", "evidence is not incomplete")
    _check(report["proposal_only"] is True, "proposal-only flag")
    qualification = report["qualification"]
    _check(qualification["status"] == "not_qualified", "nested status")
    _check(
        qualification["qualification_status"] == "not_qualified",
        "nested qualification",
    )
    _check(qualification["candidate_qualified"] is False, "candidate qualified")
    _check(qualification["proposal_only"] is True, "nested proposal-only")
    _check(
        qualification["no_missing_result_qualifies_candidate"] is True,
        "missing-result rule",
    )
    _check(
        qualification["synthetic_control_is_not_candidate_evidence"] is True,
        "synthetic control promoted",
    )
    _check(
        qualification["release_qualification_present"] is False,
        "release claimed",
    )
    _check(len(report["gates"]) == 8, "release gate count is not eight")
    _check(
        all(gate["blocked"] is True for gate in report["gates"]),
        "a release gate is open",
    )
    _check(
        [gate["id"] for gate in report["gates"]]
        == [gate_id for gate_id, _ in reference.GATE_REQUIREMENTS],
        "release gate ids changed",
    )
    blockers = report["exact_blockers"]
    _check(len(blockers) == 8, "exact blocker count")
    _check(
        all(row["state"] == "absent" for row in blockers),
        "an exact blocker is not absent",
    )
    _check(len(report["reopen_conditions"]) == 8, "reopen condition count")
    _check(
        report["task_row_identity"] == reference.task_row_identity(),
        "task row identity mismatch",
    )
    _check(
        report["task_row_identity"]["whole_file_hashed"] is False,
        "whole board hashed",
    )
    _check(
        len(report["task_row_identity"]["stable_sha256"]) == 64,
        "stable identity digest",
    )
    _check(
        "status" in report["task_row_identity"]["excluded_mutable_fields"],
        "mutable status is gated",
    )
    _check(
        report["mutable_provenance"]["gate"] is False,
        "mutable provenance is gated",
    )
    _check(
        "sha256_at_read" not in report["mutable_provenance"],
        "mutable board hash is gated",
    )
    _check(
        report["source_pins"] == reference.SOURCE_PINS,
        "report source pins",
    )
    _check(
        report["boundary_pins"] == reference.BOUNDARY_PINS,
        "report boundary pins",
    )
    _check(
        reference.BOARD_PATH not in report["source_pins"],
        "report pins mutable board",
    )
    _check(
        reference.BOARD_PATH not in report["boundary_pins"],
        "report pins mutable board as boundary",
    )
    _check(report["scope"] == reference.SCOPE, "report scope")
    _check(report["boundary"] == reference.BOUNDARY, "report boundary")
    for key, value in report["boundary"].items():
        _check(value is False, "boundary flag is not false: " + key)
    metrics = report["candidate_metrics"]
    _check(metrics["derived_from_synthetic_control"] is False, "metric promotion")
    for name in (
        "boundary_precision",
        "boundary_recall",
        "false_alarm_rate",
        "miss_rate",
        "boundary_deviation_ms",
        "segment_purity",
    ):
        row = metrics[name]
        _check(row["value"] is None, "candidate metric is not null: " + name)
        _check(row["measured"] is False, "candidate metric measured: " + name)
    control = report["synthetic_control"]
    _check(control["qualifies_candidate"] is False, "control qualifies")
    _check(control["not_audio"] is True, "control is audio")
    _check(control["not_speaker_evidence"] is True, "control is speaker evidence")
    _check(
        control["metric_scope"]
        == "synthetic_feature_domain_not_a_segmentation_result",
        "control metric scope",
    )
    _check(control["detected_boundaries"] == [30, 60], "control boundaries")
    _check(control["false_alarms"] == [], "control false alarms")
    _check(control["misses"] == [], "control misses")
    _check(
        control["negative_control"]["result"] == "no_change",
        "negative control",
    )
    _check(
        control["singular_control"]["result"] == "rejected",
        "singular control",
    )
    adverse = report["controls"]["adverse"]
    _check(len(adverse) >= 30, "adverse control count")
    _check(
        all(row["result"] == "rejected" for row in adverse),
        "an adverse control was accepted",
    )
    cases = {row["case"] for row in adverse}
    for required in (
        "feature_nan",
        "feature_pos_inf",
        "feature_neg_inf",
        "feature_bool",
        "feature_string",
        "singular_covariance",
        "manifest_missing_field",
        "manifest_extra_field",
        "manifest_relative_path",
        "manifest_bad_sha",
        "manifest_short_revision",
        "manifest_wrong_variant",
        "json_duplicate_key",
        "json_nan",
        "json_infinity",
    ):
        _check(required in cases, "missing adverse case: " + required)
    probes = report["controls"]["absence_probes"]
    _check(bool(probes), "no absence probes")
    _check(
        all(row["exists"] is False for row in probes),
        "an absence probe exists",
    )
    _check(
        report["asset_audit"]["all_absence_probes_absent"] is True,
        "asset audit is not absent",
    )
    _check(
        report["upstream_identity"]["implementation_present"] is False,
        "implementation claimed",
    )
    _check(
        report["upstream_identity"]["source_checkout_present"] is False,
        "source checkout claimed",
    )
    _check(
        report["upstream_identity"]["revision_pin_available"] is False,
        "upstream revision pinned",
    )
    _check(
        report["source_lead"]["implementation_acquired"] is False,
        "source lead acquired",
    )
    _check(
        report["bic_reference"]["qualifies_candidate"] is False,
        "reference qualifies candidate",
    )
    _check(
        report["task_geometry"]["status"] == "unestablished",
        "task geometry is established",
    )
    _check(
        report["matched_evidence"]["present"] is False,
        "matched evidence claimed",
    )
    _check(
        report["merged_sibling_evidence"]["not_pooled"] is True,
        "sibling evidence pooled",
    )
    for key in (
        "speaker_change_execution_present",
        "bic_execution_present",
        "diarization_execution_present",
    ):
        _check(
            report["merged_sibling_evidence"][key] is False,
            "sibling execution claimed: " + key,
        )
    for row in report["merged_sibling_evidence"]["packages"]:
        _check(
            row["attributed_to_this_task"] is False,
            "sibling package attributed",
        )
    digest = reference.sha256(raw)
    _check(
        (HERE / "report.json.sha256").read_bytes()
        == (digest + "  report.json\n").encode("ascii"),
        "report.json.sha256 mismatch",
    )
    return digest


def _check_cold_start(expected_report: bytes, expected_contract: bytes) -> None:
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    work = Path(tempfile.mkdtemp(prefix="bic-evidence-verify-", dir=root))
    try:
        for index in range(3):
            target = work / ("cold-%d" % index)
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            report_run = subprocess.run(
                [
                    sys.executable,
                    str(HERE / "run.py"),
                    "report",
                    "--out",
                    str(target),
                ],
                cwd=str(HERE),
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            contract_run = subprocess.run(
                [
                    sys.executable,
                    str(HERE / "run.py"),
                    "contract",
                    "--out",
                    str(target),
                ],
                cwd=str(HERE),
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            _check(
                report_run.returncode == 0,
                "cold report %d failed: %s"
                % (index, report_run.stderr.strip()),
            )
            _check(
                contract_run.returncode == 0,
                "cold contract %d failed: %s"
                % (index, contract_run.stderr.strip()),
            )
            _check(
                (target / "report.json").read_bytes() == expected_report,
                "cold report %d is not byte-identical" % index,
            )
            _check(
                (target / "contract.json").read_bytes() == expected_contract,
                "cold contract %d is not byte-identical" % index,
            )
            digest = reference.sha256(expected_report)
            _check(
                (target / "report.json.sha256").read_bytes()
                == (digest + "  report.json\n").encode("ascii"),
                "cold sidecar %d differs" % index,
            )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _check_adverse_in_process() -> None:
    rows = reference.run_adverse_controls()
    _check(rows, "no adverse controls")
    _check(
        all(row["result"] == "rejected" for row in rows),
        "an adverse control was accepted",
    )
    _check(
        reference.qualification_gate(reference._base_manifest())[
            "qualifies"
        ]
        is False,
        "manifest gate qualified",
    )


def main() -> int:
    try:
        _check_pins()
        _check_unexpected_files()
        _check_licenses()
        _check_git_scope()
        _check_sources_manifest()
        _check_contract()
        digest = _check_report()
        _check_adverse_in_process()
        expected_contract = (HERE / "contract.json").read_bytes()
        _check_cold_start((HERE / "report.json").read_bytes(), expected_contract)
    except (
        VerifyError,
        reference.Reject,
        OSError,
        ValueError,
    ) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS decision=DEFER status=proposal_only_incomplete qualification=not_qualified")
    print("PASS profile=spatial gates=8-blocked exact_blockers=8-absent")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete cold_start=3x-byte-identical scope=task-local-only")
    print("PASS mutable_board_gate=false stable_linked_row_identity_only")
    print("PASS synthetic_control=feature-domain-only candidate_metrics=null")
    print("PASS adverse_missing_invalid_nonfinite=rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
