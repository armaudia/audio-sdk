#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local RT-VC package.

Every check fails closed: missing or stale pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, disposition drift, a promoted missing
result, a stale README digest table, licensing gaps, whitespace damage or any
out-of-scope worktree change is a hard failure.

Scope is checked against the dirty worktree and against the commits this branch
adds relative to the newest merge-base with ``origin/main`` (falling back to
``main``). An unresolved base emits ``scope_base_unavailable`` and any committed
path outside the task directory emits ``base_out_of_scope_change``.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = reference.TASK_PREFIX
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")
NO_ZERO = re.compile(rb"-0\.0(?=[,}\]])")


def sdk_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override and (Path(override) / "REUSE.toml").is_file():
        return Path(override)
    cursor = HERE
    while cursor != cursor.parent:
        if (cursor / "REUSE.toml").is_file() and (cursor / "LICENSES").is_dir():
            return cursor
        cursor = cursor.parent
    return HERE.parents[2]


SDK = sdk_root()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(reference.SOURCE_ROOT)))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
README = HERE / "README.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(raw: str) -> bool:
    return bool(raw) and not raw.startswith("/") and ".." not in Path(raw).parts


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return {}
    lines = PINS.read_text(encoding="utf-8").splitlines()
    if lines[:len(reference.SOURCES_HEADER.splitlines())] != (
            reference.SOURCES_HEADER.splitlines()):
        errors.append("SOURCES.sha256 provenance header mismatch")
    pins: Dict[str, Tuple[str, Path]] = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if "TASKS.json" in line:
            errors.append(
                "SOURCES.sha256 must not pin the mutable full TASKS.json")
        match = PIN_LINE.fullmatch(line)
        if not match:
            errors.append("malformed pin: " + repr(line))
            continue
        digest, label = match.groups()
        prefix, raw = label.split(":", 1)
        if not safe_relative(raw):
            errors.append("unsafe pin path: " + label)
            continue
        if label in pins:
            errors.append("duplicate pin: " + label)
            continue
        path = {"pkg": HERE, "source": SOURCE_ROOT, "worktree": SDK}[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    expected = (
        {"source:" + name for name in reference.SOURCE_PINS}
        | {"worktree:" + name for name in reference.BOUNDARY_PINS}
        | {"pkg:" + name for name in reference.PIN_FILES}
    )
    if set(pins) != expected:
        errors.append("pin set mismatch: missing="
                      + str(sorted(expected - set(pins)))
                      + " extra=" + str(sorted(set(pins) - expected)))
    if "pkg:SOURCES.sha256" in pins:
        errors.append("SOURCES.sha256 must not pin itself")
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file() and path.name != "SOURCES.sha256"
        and not path.name.endswith(".pyc")
    }
    if set(pins) != {"pkg:" + name for name in authored} | {
            label for label in pins if not label.startswith("pkg:")}:
        for name in sorted(authored):
            if "pkg:" + name not in pins:
                errors.append("unpinned package file: " + name)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]],
                      errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file() or path.is_symlink():
            errors.append("missing or non-regular pin target: " + label)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            errors.append(
                f"pin mismatch: {label} expected={digest} actual={actual}")
            continue
        checked += 1
    for label in sorted(reference.SOURCE_PINS):
        if "source:" + label not in pins:
            errors.append("missing declared source pin: " + label)
    for label in sorted(reference.BOUNDARY_PINS):
        if "worktree:" + label not in pins:
            errors.append("missing declared boundary pin: " + label)
    return checked


def strict_json(path: Path, errors: List[str]) -> Optional[Dict[str, Any]]:
    try:
        value = reference.load_strict_json(path)
    except reference.ReferenceRejection as error:
        errors.append(f"{path.name}: {error.code}")
        return None
    if not isinstance(value, dict):
        errors.append(path.name + ": root is not an object")
        return None
    return value


def _expect(condition: bool, message: str, errors: List[str]) -> bool:
    if not condition:
        errors.append(message)
    return condition


def check_report(report: Dict[str, Any], errors: List[str]) -> bool:
    ok = True
    try:
        fresh_text, fresh_digest = reference.canonical_report(
            reference.build_report())
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("fresh report build failed: " + str(error))
        fresh_text, fresh_digest = "", ""
        ok = False
    if not REPORT.is_file():
        errors.append("report.json missing")
        ok = False
    elif REPORT.read_text(encoding="utf-8") != fresh_text:
        errors.append("report.json is not byte-reproducible")
        ok = False
    expected_sidecar = fresh_digest + "\n"
    if (not SIDECAR.is_file()
            or SIDECAR.read_text(encoding="utf-8") != expected_sidecar):
        errors.append("report.json.sha256 does not match report.json")
        ok = False
    if fresh_text and NO_ZERO.search(fresh_text.encode("utf-8")):
        errors.append("negative zero in canonical report")

    for key, expected in (
            ("schema_id", reference.REPORT_SCHEMA),
            ("task_id", reference.TASK_ID),
            ("component", reference.COMPONENT),
            ("title", reference.TITLE),
            ("repository", reference.REPOSITORY),
            ("mode", reference.MODE),
            ("profile", reference.PROFILE),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE),
            ("qualification_status", reference.QUALIFICATION),
            ("base_commit", reference.BASE_COMMIT),
            ("branch", reference.BRANCH),
            ("worktree", reference.CLAIM_WORKTREE),
            ("reviewer", reference.REVIEWER),
            ("generated_by", "reference.py")):
        ok &= _expect(report.get(key) == expected,
                      "report field mismatch: " + key, errors)
    ok &= _expect(report.get("proposal_only") is True,
                  "report is not proposal-only", errors)

    qualification = report.get("qualification", {})
    ok &= _expect(qualification.get("status") == reference.QUALIFICATION,
                  "qualification status mismatch", errors)
    ok &= _expect(qualification.get("candidate_qualified") is False,
                  "candidate was qualified", errors)
    ok &= _expect(qualification.get("no_missing_result_qualifies_candidate")
                  is True, "missing-result guard absent", errors)
    ok &= _expect(qualification.get("real_candidate_metrics") is False,
                  "real candidate metrics claimed", errors)
    ok &= _expect(qualification.get("decision") == reference.DECISION,
                  "qualification decision mismatch", errors)
    ok &= _expect(qualification.get("defer_before") == reference.DEFER_BEFORE,
                  "qualification defer point mismatch", errors)
    ok &= _expect(qualification.get("blocked_gate_count") == 8,
                  "blocked gate count mismatch", errors)
    ok &= _expect(qualification.get("blocked_gate_ids")
                  == ["B" + str(index) for index in range(1, 9)],
                  "blocked gate ids mismatch", errors)

    ok &= _expect(report.get("format") == reference.FORMAT,
                  "report format mismatch", errors)
    ok &= _expect(report.get("boundary") == reference.BOUNDARY,
                  "report boundary mismatch", errors)
    ok &= _expect(report.get("scope") == reference.SCOPE,
                  "report scope mismatch", errors)
    ok &= _expect(report.get("source_pins") == reference.SOURCE_PINS,
                  "report source pins mismatch", errors)
    ok &= _expect(report.get("boundary_pins") == reference.BOUNDARY_PINS,
                  "report boundary pins mismatch", errors)
    ok &= _expect(report.get("readme_digest_files")
                  == list(reference.README_DIGEST_FILES),
                  "README digest file list mismatch", errors)

    candidate = report.get("candidate", {})
    for key in ("runtime_present", "weights_present", "checkpoint_present",
                "weight_setup_present", "target_reference_rights_confirmed",
                "geometry_documented", "implemented_here", "adapter_present",
                "exact_numeric_output_present"):
        ok &= _expect(candidate.get(key) is False,
                      "candidate claim not false: " + key, errors)
    ok &= _expect(candidate.get("evidence_status") == "blocked",
                  "candidate is not blocked", errors)
    ok &= _expect(candidate.get("record_name") == "RT-VC",
                  "candidate record name mismatch", errors)
    ok &= _expect(candidate.get("inventory_status") == "blocked",
                  "candidate inventory status mismatch", errors)
    ok &= _expect(candidate.get("source_record_line") == 16,
                  "candidate source line mismatch", errors)
    ok &= _expect(candidate.get("source_revision")
                  == reference.UPSTREAM_REVISION,
                  "candidate source revision mismatch", errors)
    ok &= _expect(candidate.get("source_tree_sha256")
                  == reference.UPSTREAM_TREE,
                  "candidate source tree mismatch", errors)

    audit = report.get("asset_audit", {})
    ok &= _expect(audit.get("source_checkout_present") is True,
                  "source provenance checkout is missing", errors)
    ok &= _expect(audit.get("source_revision_matches") is True,
                  "source revision does not match the pin", errors)
    ok &= _expect(audit.get("source_revision_matches") is True,
                  "source revision drift", errors)
    ok &= _expect(audit.get("source_tree_matches") is True,
                  "source tree drift", errors)
    ok &= _expect(audit.get("source_license") == "unconfirmed",
                  "source license was asserted without evidence", errors)
    ok &= _expect(audit.get("target_reference_present") is True,
                  "the pinned p360 reference disappeared", errors)
    ok &= _expect(audit.get("target_reference_rights_confirmed") is False,
                  "p360 reference rights were asserted", errors)
    ok &= _expect(audit.get("target_reference_read_by_package") is False,
                  "package read real audio", errors)
    for key in ("checkpoint_present", "weight_setup_present",
                "metric_spec_present", "rights_record_present",
                "license_record_present", "target_consent_present",
                "cohort_manifest_present", "parity_manifest_present",
                "runtime_env_present", "runtime_lock_present",
                "reference_audio_present"):
        ok &= _expect(audit.get(key) is False,
                      "candidate artifact is present: " + key, errors)
    ok &= _expect(audit.get("all_absence_probes_absent") is True,
                  "an absence probe found an asset", errors)
    ok &= _expect(audit.get("absence_probes") == [
        dict(item) for item in reference.probe_absence()],
        "absence probe list mismatch", errors)
    ok &= _expect(report.get("absence_probes")
                  == audit.get("absence_probes"),
                  "top-level absence probes mismatch", errors)
    ok &= _expect(report.get("asset_requirements")
                  == [dict(item) for item in reference.ASSET_REQUIREMENTS],
                  "asset requirements mismatch", errors)
    ok &= _expect(report.get("caller_asset_contract")
                  == reference.CALLER_ASSET_CONTRACT,
                  "caller asset contract mismatch", errors)

    profile = report.get("voice_profile", {})
    ok &= _expect(profile.get("name") == reference.PROFILE,
                  "voice profile name mismatch", errors)
    ok &= _expect(profile.get("real_model_metrics") is None,
                  "voice profile claims measured metrics", errors)
    ok &= _expect(profile.get("satisfied_for_qualification") == [],
                  "voice profile has a satisfied gate", errors)
    ok &= _expect([item["id"] for item in profile.get("required_items", [])]
                  == [item[0] for item in reference.VOICE_REQUIREMENTS],
                  "voice profile item ids mismatch", errors)
    ok &= _expect(all(item.get("satisfied_for_qualification") is False
                      for item in profile.get("required_items", [])),
                  "a voice requirement was satisfied", errors)

    control = report.get("reference_protocol", {})
    baseline = control.get("identity_baseline", {})
    ok &= _expect(control.get("model_executed") is False,
                  "reference protocol executed a model", errors)
    ok &= _expect(control.get("audio_read") is False,
                  "reference protocol read audio", errors)
    for key in ("sample_count_equal", "duration_equal", "digest_equal",
                "peak_bounded"):
        ok &= _expect(baseline.get(key) is True,
                      "identity control failed: " + key, errors)
    ok &= _expect(baseline.get("content_delay_samples") == 0,
                  "identity control delay is not zero", errors)
    admission = control.get("request_admission", {})
    ok &= _expect(admission.get("identity_control_accepted") is True,
                  "identity control was not admitted", errors)
    ok &= _expect(admission.get("candidate_smoother_used") is False,
                  "candidate smoother was used", errors)
    ok &= _expect(admission.get("candidate_conversion_used") is False,
                  "candidate conversion was used", errors)
    ok &= _expect(admission.get("rejected_targets") == [
        {"target": reference.CANDIDATE_TARGET,
         "reason": "absent_rt_vc_checkpoint"},
        {"target": reference.TARGET_TARGET,
         "reason": "unconfirmed_p360_reference_rights"},
    ], "candidate targets were not rejected", errors)
    ok &= _expect(control.get("geometry", {}).get(
        "candidate_geometry_asserted") is False,
        "candidate geometry was asserted", errors)
    ok &= _expect(len(control.get("acceptance_outcomes", []))
                  == len(reference.VOICE_REQUIREMENTS),
                  "acceptance outcome count mismatch", errors)
    ok &= _expect(all(item.get("measured") is False
                      for item in control.get("acceptance_outcomes", [])),
                  "a voice outcome was measured", errors)
    adverse = control.get("adverse", [])
    ok &= _expect([item.get("case") for item in adverse]
                  == list(reference.ADVERSE_CASE_IDS),
                  "adverse case set mismatch", errors)
    ok &= _expect(all(item.get("result") == "rejected" for item in adverse),
                  "an adverse case was accepted", errors)
    ok &= _expect(control.get("adverse_all_rejected") is True,
                  "adverse guard is not all-rejected", errors)

    controls = report.get("controls", {})
    for key in ("invalid_values_rejected", "missing_asset_rejected_before_processing",
                "missing_result_never_qualifies", "nonfinite_rejected",
                "offline_streaming_separation_declared", "identity_baseline_exact",
                "candidate_target_rejected_before_processing",
                "incomplete_manifest_rejected", "absence_probes_all_absent",
                "adverse_all_rejected"):
        ok &= _expect(controls.get(key) is True,
                      "control flag not true: " + key, errors)

    gates = report.get("gates", [])
    ok &= _expect([item.get("id") for item in gates]
                  == ["B" + str(index) for index in range(1, 9)],
                  "gate id set mismatch", errors)
    ok &= _expect(all(item.get("status") == "blocked" for item in gates),
                  "a release gate is not blocked", errors)
    ok &= _expect(report.get("release_gates") == gates,
                  "release gates differ from gates", errors)
    ok &= _expect(report.get("exact_blockers")
                  == [dict(item) for item in reference.EXACT_BLOCKERS],
                  "exact blockers drifted", errors)
    ok &= _expect(len(report.get("reopen_conditions", [])) == 8,
                  "reopening condition count mismatch", errors)
    blocker_text = " ".join(str(item) for item in report.get("exact_blockers", []))
    for token in ("No checkpoint in official checkout", "9d9a55d", "p360",
                  "cohort", "opt-in adapter"):
        ok &= _expect(token in blocker_text,
                      "exact blocker token missing: " + token, errors)
    external = str(report.get("external_blocker", ""))
    for token in ("No checkpoint in official checkout", "9d9a55d",
                  "official RT-VC source checkout"):
        ok &= _expect(token in external,
                      "external blocker token missing: " + token, errors)
    reopen = str(report.get("reopen_condition", ""))
    ok &= _expect("DEFER" in reopen and "not qualified" in reopen,
                  "reopening condition lost the fail-closed disposition", errors)
    ok &= _expect(report.get("candidate_metrics") is None,
                  "candidate metrics are not empty", errors)
    ok &= _expect(report.get("non_claims") == list(reference.NON_CLAIMS),
                  "non-claims drifted", errors)
    ok &= _expect(len(report.get("missing_historical_artifacts", [])) >= 8,
                  "missing artifact list is incomplete", errors)
    print("verify: report disposition, geometry, controls and gates strict")
    return ok


def check_contract(contract: Dict[str, Any], report: Dict[str, Any],
                   digest: str, errors: List[str]) -> bool:
    ok = True
    try:
        fresh = reference.build_contract(report, digest)
        fresh_text = reference.canonical_text(fresh) + "\n"
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("fresh contract build failed: " + str(error))
        fresh_text = ""
        fresh = {}
        ok = False
    if not CONTRACT.is_file():
        errors.append("contract.json missing")
        ok = False
    elif CONTRACT.read_text(encoding="utf-8") != fresh_text:
        errors.append("contract.json is not byte-reproducible")
        ok = False

    for key, expected in (
            ("schema_id", reference.CONTRACT_SCHEMA),
            ("task", reference.TASK_ID),
            ("title", reference.TITLE),
            ("component", reference.COMPONENT),
            ("repository", reference.REPOSITORY),
            ("version", reference.VERSION),
            ("mode", reference.MODE),
            ("profile", reference.PROFILE),
            ("verification_profile", reference.PROFILE),
            ("task_prefix", reference.TASK_PREFIX),
            ("write_scope", reference.TASK_PREFIX),
            ("base_commit", reference.BASE_COMMIT),
            ("branch", reference.BRANCH),
            ("worktree", reference.CLAIM_WORKTREE),
            ("reviewer", reference.REVIEWER),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE),
            ("qualification_status", reference.QUALIFICATION),
            ("blocked_release_gate_count", 8)):
        ok &= _expect(contract.get(key) == expected,
                      "contract field mismatch: " + key, errors)
    ok &= _expect(contract.get("qualification") == report.get("qualification"),
                  "contract qualification differs from report", errors)
    ok &= _expect(contract.get("format") == reference.FORMAT,
                  "contract format mismatch", errors)
    ok &= _expect(contract.get("boundary") == reference.BOUNDARY,
                  "contract boundary mismatch", errors)
    ok &= _expect(contract.get("scope") == reference.SCOPE,
                  "contract scope mismatch", errors)
    ok &= _expect(contract.get("candidate") == report.get("candidate"),
                  "contract candidate differs from report", errors)
    ok &= _expect(contract.get("voice_profile") == report.get("voice_profile"),
                  "contract voice profile differs from report", errors)
    ok &= _expect(contract.get("caller_asset_contract")
                  == reference.CALLER_ASSET_CONTRACT,
                  "contract caller asset contract mismatch", errors)
    ok &= _expect(contract.get("source_pins") == reference.SOURCE_PINS,
                  "contract source pins mismatch", errors)
    ok &= _expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS,
                  "contract boundary pins mismatch", errors)
    ok &= _expect(contract.get("readme_digest_files")
                  == list(reference.README_DIGEST_FILES),
                  "contract README digest list mismatch", errors)
    sidecar_digest = sha256((digest + "\n").encode("ascii"))
    expected_pins = reference.artifact_pins(digest, sidecar_digest)
    ok &= _expect(contract.get("artifact_pins") == expected_pins,
                  "contract artifact pins mismatch", errors)
    for label, expected_digest in sorted(expected_pins.items()):
        path = SDK / label
        actual = sha256(path.read_bytes()) if path.is_file() else None
        ok &= _expect(actual == expected_digest,
                      "contract artifact pin stale: " + label, errors)
    ok &= _expect(contract.get("gates") == report.get("gates"),
                  "contract gates differ from report", errors)
    ok &= _expect(contract.get("exact_blockers")
                  == [dict(item) for item in reference.EXACT_BLOCKERS],
                  "contract exact blockers mismatch", errors)
    ok &= _expect(contract.get("negative_claims")
                  == list(reference.NON_CLAIMS),
                  "contract negative claims mismatch", errors)
    required_reproduction = {
        "cold_start_regenerations": 3,
        "generator": "run.py",
        "check_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check",
        "verify_command": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
    }
    ok &= _expect(contract.get("reproduction") == required_reproduction,
                  "contract reproduction commands mismatch", errors)
    invariants = " ".join(contract.get("invariants", []))
    for token in ("decision is DEFER", "not_qualified",
                  "only this task-local evidence directory is written",
                  "merge-base diff must contain no path outside TASK_PREFIX"):
        ok &= _expect(token in invariants,
                      "contract invariant missing: " + token, errors)
    print("verify: contract pins, scope and disposition strict")
    return ok


def check_task_row_identity(report: Dict[str, Any], contract: Dict[str, Any],
                            errors: List[str]) -> bool:
    ok = True
    try:
        fresh = reference.task_row_identity()
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("task row identity is unavailable: " + str(error))
        return False
    for name, document in (("report", report), ("contract", contract)):
        actual = document.get("task_row_identity", {})
        ok &= _expect(actual.get("stable_fields") == fresh["stable_fields"],
                      name + " stable task fields mismatch", errors)
        ok &= _expect(actual.get("stable_sha256") == fresh["stable_sha256"],
                      name + " stable task digest mismatch", errors)
        ok &= _expect(actual.get("full_tasks_json_hashed") is False,
                      name + " hashed the mutable task board", errors)
        ok &= _expect(actual.get("whole_file_hashed") is False,
                      name + " hashed the whole task board", errors)
    if contract.get("board_row") != report.get("task_row_identity"):
        errors.append("contract board row differs from report")
        ok = False
    print("verify: linked task row identity exact without hashing board")
    return ok


def check_readme(errors: List[str]) -> bool:
    ok = True
    try:
        text = README.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        errors.append("README.md unreadable: " + str(error))
        return False
    if text.count(reference.README_TABLE_START) != 1:
        errors.append("README digest table start marker is not unique")
        ok = False
    if text.count(reference.README_TABLE_END) != 1:
        errors.append("README digest table end marker is not unique")
        ok = False
    start = text.find(reference.README_TABLE_START)
    end = text.find(reference.README_TABLE_END)
    if start >= 0 and end > start:
        block = text[start + len(reference.README_TABLE_START):end].strip(
        ).splitlines()
        if block[:2] != ["| Artifact | SHA-256 | Bytes |",
                         "| --- | --- | ---: |"]:
            errors.append("README digest table header mismatch")
            ok = False
        rows: List[Tuple[str, str, int]] = []
        for line in block[2:]:
            match = re.fullmatch(
                r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|", line)
            if match is None:
                errors.append("malformed README digest row: " + repr(line))
                ok = False
                continue
            rows.append((match.group(1), match.group(2), int(match.group(3))))
        expected = [
            (name, sha256((HERE / name).read_bytes()),
             (HERE / name).stat().st_size)
            for name in reference.README_DIGEST_FILES
        ]
        if rows != expected:
            errors.append("README digest table is stale or incomplete")
            ok = False
        table = text[start:end]
        for name in ("contract.json", "SOURCES.sha256"):
            if name in table:
                errors.append("README digest table must exclude " + name)
                ok = False
    else:
        errors.append("README digest table markers are ordered incorrectly")
        ok = False
    for token in ("DEFER", "incomplete", "not qualified",
                  "opt_in_adapter_exposure", "origin/main", "main",
                  "scope_base_unavailable", "base_out_of_scope_change",
                  "No RT-VC conversion was executed"):
        if token not in text:
            errors.append("README token missing: " + token)
            ok = False
    print(f"verify: README digest table exact for "
          f"{len(reference.README_DIGEST_FILES)} artifacts")
    return ok


def check_licensing(errors: List[str]) -> bool:
    copyright_line = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX-" + "License-Identifier: Apache-2.0"
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:6])
            if copyright_line not in head or license_line not in head:
                errors.append("missing SPDX header: " + path.name)
                ok = False
        elif path.suffix in (".json", ".sha256") and not path.name.endswith(
                ".license"):
            sidecar = path.with_name(path.name + ".license")
            if not sidecar.is_file():
                errors.append("missing SPDX sidecar: " + sidecar.name)
                ok = False
                continue
            text = sidecar.read_text(encoding="utf-8")
            if copyright_line not in text or license_line not in text:
                errors.append("invalid SPDX sidecar: " + sidecar.name)
                ok = False
    sidecar = HERE / "SOURCES.sha256.license"
    if not sidecar.is_file():
        errors.append("missing SPDX sidecar: SOURCES.sha256.license")
        ok = False
    else:
        text = sidecar.read_text(encoding="utf-8")
        if copyright_line not in text or license_line not in text:
            errors.append("invalid SPDX sidecar: SOURCES.sha256.license")
            ok = False
    reuse = SDK / "REUSE.toml"
    if not reuse.is_file():
        errors.append("REUSE.toml missing")
        ok = False
    elif "docs/**" not in reuse.read_text(encoding="utf-8"):
        errors.append("REUSE.toml does not cover docs/**")
        ok = False
    print("verify: SPDX headers and sidecars exact")
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append("package is not reproducible: "
                      + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report(reference.build_report())[0].encode(
        "utf-8")
    digest = sha256(expected)
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = (digest + "\n").encode("utf-8")
    if (not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar):
        errors.append("report.json.sha256 mismatch")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="rtvc-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                shutil.copytree(HERE, target)
                environment = dict(
                    os.environ, PYTHONDONTWRITEBYTECODE="1",
                    SDK_ROOT=str(SDK), SOURCE_ROOT=str(SOURCE_ROOT))
                result = subprocess.run(
                    [sys.executable, str(target / "run.py")],
                    cwd=str(target), env=environment, capture_output=True,
                    text=True, check=False)
                generated = target / "report.json"
                if result.returncode != 0 or not generated.is_file():
                    errors.append(
                        f"cold regeneration {index} failed: "
                        + (result.stderr.strip() or result.stdout.strip()))
                    ok = False
                    continue
                data = generated.read_bytes()
                repeats.append(sha256(data))
                if data != expected:
                    errors.append(
                        f"cold regeneration {index} is not byte-identical")
                    ok = False
                if (not (target / "report.json.sha256").is_file()
                        or (target / "report.json.sha256").read_bytes()
                        != sidecar):
                    errors.append(
                        f"cold regeneration {index} sidecar differs")
                    ok = False
                for name in ("contract.json", "SOURCES.sha256"):
                    if (not (target / name).is_file()
                            or (target / name).read_bytes()
                            != (HERE / name).read_bytes()):
                        errors.append(
                            f"cold regeneration {index} differs: {name}")
                        ok = False
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
        ok = False
    ok &= _expect(len(repeats) == 3
                  and len(set(repeats)) == 1
                  and repeats[0] == digest,
                  "cold-start digests are not identical", errors)
    print(f"verify: 3 cold regenerations byte-identical report_sha256={digest}")
    return ok, digest, repeats


def scope_findings(worktree: Path) -> List[str]:
    """Return fail-closed scope errors for a worktree."""
    errors: List[str] = []
    if not (worktree / ".git").exists():
        return ["scope_git_unavailable"]
    status = subprocess.run(
        ["git", "-C", str(worktree), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if status.returncode != 0:
        errors.append("git_status_failed: " + status.stderr.strip())
    else:
        for line in status.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path and not path.startswith(TASK_PREFIX):
                errors.append("out_of_scope_change: " + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(worktree), *arguments],
                              capture_output=True, text=True, check=False)
        if diff.returncode != 0 or diff.stdout.strip():
            label = "git_" + "_".join(arguments).replace("--", "").strip("_")
            errors.append(label + "_failed: " + diff.stdout.strip())
    branch = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=False)
    if branch.returncode != 0:
        errors.append("git_branch_unavailable")
    elif branch.stdout.strip() != reference.BRANCH:
        errors.append("unexpected_branch: " + branch.stdout.strip())
    base = reference.scope_base(worktree)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            changed = reference.scope_changed_paths(worktree, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(changed):
                errors.append("base_out_of_scope_change: " + path)
    return errors


def check_scope(errors: List[str]) -> bool:
    findings = scope_findings(SDK)
    errors.extend(findings)
    if not findings:
        print("verify: dirty and merge-base scope confined to " + TASK_PREFIX)
    return not findings


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    verified = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    report_ok = check_report(report, errors) if report is not None else False
    digest = (reference.sha256_bytes(
        reference.canonical_report(report)[0].encode("utf-8"))
        if report is not None else "")
    contract_ok = (
        check_contract(contract, report, digest, errors)
        if contract is not None and report is not None else False)
    identity_ok = (
        check_task_row_identity(report, contract, errors)
        if report is not None and contract is not None else False)
    readme_ok = check_readme(errors)
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        return 1
    if not all((report_ok, contract_ok, identity_ok, readme_ok, licensing_ok,
                sources_ok, reproduction_ok, scope_ok, verified > 0)):
        print("FAIL: a verification stage did not pass", file=sys.stderr)
        return 1
    print(
        f"PASS pins={verified} gates=8 blockers=8 "
        f"cold_starts={len(repeats)}/3 report_sha256={digest} "
        f"decision={report['decision']} "
        f"qualification={report['qualification_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
