#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = "docs/task-evidence/f0-contour-smoothing/"
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")


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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(raw: str) -> bool:
    return bool(raw) and not raw.startswith("/") and ".." not in Path(raw).parts


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return {}
    lines = PINS.read_text(encoding="utf-8").splitlines()
    if not lines or not any(line.startswith("#") for line in lines):
        errors.append("SOURCES.sha256 has no provenance header")
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
        path = {"pkg": HERE, "source": SOURCE_ROOT,
                "worktree": SDK}[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file()
        and path.name != "SOURCES.sha256"
        and not path.name.endswith(".pyc")
        and "__pycache__" not in path.name
    }
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            errors.append("unpinned package file: " + name)
    for label in sorted(pins):
        if not label.startswith("pkg:"):
            continue
        if label.split(":", 1)[1] not in authored:
            errors.append("extra package pin: " + label)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]],
                      errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file():
            errors.append("missing pin target: " + label)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            errors.append(
                f"pin mismatch: {label} expected={digest} actual={actual}")
            continue
        checked += 1
    for label, digest in sorted(reference.SOURCE_PINS.items()):
        if "source:" + label not in pins:
            errors.append("missing declared source pin: " + label)
    for label, digest in sorted(reference.BOUNDARY_PINS.items()):
        if "worktree:" + label not in pins:
            errors.append("missing declared boundary pin: " + label)
    return checked


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
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
    fresh_text, fresh_digest = reference.canonical_report(
        reference.build_report())
    if not REPORT.is_file():
        errors.append("report.json missing")
        return False
    if REPORT.read_text(encoding="utf-8") != fresh_text:
        errors.append("report.json is not byte-reproducible")
        ok = False
    if not SIDECAR.is_file():
        errors.append("report.json.sha256 missing")
        ok = False
    elif SIDECAR.read_text(encoding="utf-8") != fresh_digest + "\n":
        errors.append("report.json.sha256 does not match report.json")
        ok = False
    ok &= _expect(report.get("task_id") == reference.TASK_ID,
                  "report task_id mismatch", errors)
    ok &= _expect(report.get("component") == reference.COMPONENT,
                  "report component mismatch", errors)
    ok &= _expect(report.get("title") == reference.TITLE,
                  "report title mismatch", errors)
    ok &= _expect(report.get("repository") == reference.REPOSITORY,
                  "report repository mismatch", errors)
    ok &= _expect(report.get("mode") == reference.MODE,
                  "report mode mismatch", errors)
    ok &= _expect(report.get("profile") == reference.PROFILE,
                  "report profile mismatch", errors)
    ok &= _expect(report.get("status") == "proposal_only_incomplete",
                  "report status must be proposal_only_incomplete", errors)
    ok &= _expect(report.get("evidence_status") == "incomplete",
                  "report evidence_status must be incomplete", errors)
    ok &= _expect(report.get("proposal_only") is True,
                  "report must be proposal_only", errors)
    ok &= _expect(report.get("decision") == "DEFER",
                  "report decision must be DEFER", errors)
    ok &= _expect(report.get("defer_before") == "opt_in_adapter_exposure",
                  "report defer_before mismatch", errors)
    ok &= _expect(report.get("qualification_status") == "not_qualified",
                  "report qualification_status must be not_qualified", errors)
    qualification = report.get("qualification", {})
    ok &= _expect(qualification.get("status") == "not_qualified",
                  "qualification.status must be not_qualified", errors)
    ok &= _expect(qualification.get("candidate_qualified") is False,
                  "candidate must not be qualified", errors)
    ok &= _expect(
        qualification.get("no_missing_result_qualifies_candidate") is True,
        "missing result must never qualify", errors)
    ok &= _expect(qualification.get("real_candidate_metrics") is False,
                  "real candidate metrics must be false", errors)
    gates = report.get("gates", [])
    ok &= _expect(isinstance(gates, list) and len(gates) == 8,
                  "exactly eight release gates are required", errors)
    ok &= _expect(
        [gate.get("id") for gate in gates]
        == [item[0] for item in reference.GATE_REQUIREMENTS],
        "release gate ids/order mismatch", errors)
    ok &= _expect(all(gate.get("status") == "blocked" for gate in gates),
                  "every release gate must be blocked", errors)
    ok &= _expect(
        qualification.get("blocked_gate_count") == 8,
        "blocked_gate_count must be 8", errors)
    ok &= _expect(
        report.get("release_gates") == gates,
        "release_gates must equal gates", errors)
    blockers = report.get("exact_blockers", [])
    ok &= _expect(isinstance(blockers, list) and len(blockers) == 8,
                  "exactly eight exact blockers are required", errors)
    ok &= _expect(
        [item.get("gate") for item in blockers]
        == [item[0] for item in reference.GATE_REQUIREMENTS],
        "blocker gate mapping mismatch", errors)
    candidate = report.get("candidate", {})
    for field in ("source_present", "weights_present",
                  "smoother_parameters_present", "target_contour_present",
                  "voicing_policy_present", "pitch_reference_present",
                  "metric_spec_present", "runtime_present",
                  "geometry_documented", "implemented_here",
                  "adapter_present", "exact_numeric_output_present"):
        ok &= _expect(candidate.get(field) is False,
                      "candidate." + field + " must be false", errors)
    ok &= _expect(candidate.get("source_revision") is None,
                  "candidate source_revision must be null", errors)
    ok &= _expect(candidate.get("smoother_id") is None,
                  "candidate smoother_id must be null", errors)
    audit = report.get("asset_audit", {})
    probes = audit.get("absence_probes", [])
    ok &= _expect(len(probes) == len(reference.ABSENCE_PROBES),
                  "absence probe count mismatch", errors)
    ok &= _expect(all(item.get("exists") is False for item in probes),
                  "every absence probe must be absent", errors)
    ok &= _expect(audit.get("all_absence_probes_absent") is True,
                  "all_absence_probes_absent must be true", errors)
    for field in ("source_checkout_present", "license_file_present",
                  "weights_present", "smoother_config_present",
                  "target_contour_present", "voicing_policy_present",
                  "pitch_reference_present", "metric_spec_present",
                  "rights_record_present", "license_record_present",
                  "runtime_env_present", "runtime_lock_present",
                  "cohort_manifest_present", "parity_manifest_present",
                  "reference_audio_present"):
        ok &= _expect(audit.get(field) is False,
                      "asset_audit." + field + " must be false", errors)
    profile = report.get("voice_profile", {})
    ok &= _expect(profile.get("name") == "voice",
                  "voice profile name mismatch", errors)
    ok &= _expect(profile.get("satisfied_for_qualification") == [],
                  "no voice profile item may be satisfied", errors)
    ok &= _expect(profile.get("real_model_metrics") is None,
                  "real_model_metrics must be null", errors)
    items = profile.get("required_items", [])
    ok &= _expect(len(items) == len(reference.VOICE_REQUIREMENTS),
                  "voice profile item count mismatch", errors)
    ok &= _expect(all(item.get("satisfied_for_qualification") is False
                      for item in items),
                  "every voice profile item must be unsatisfied", errors)
    controls = report.get("controls", {})
    ok &= _expect(controls.get("adverse_all_rejected") is True,
                  "adverse controls must all be rejected", errors)
    ok &= _expect(
        controls.get("adverse_case_count") == len(reference.ADVERSE_CASE_IDS),
        "adverse case count mismatch", errors)
    ok &= _expect(controls.get("identity_baseline_exact") is True,
                  "identity baseline must be exact", errors)
    ok &= _expect(
        controls.get("candidate_target_rejected_before_processing") is True,
        "candidate targets must be rejected", errors)
    ok &= _expect(
        controls.get("incomplete_specification_rejected") is True,
        "incomplete specification must be rejected", errors)
    ok &= _expect(report.get("candidate_metrics") is None,
                  "candidate_metrics must be null", errors)
    boundary = report.get("boundary", {})
    for field in ("public_api_abi_changed", "provider_registered",
                  "provider_intake_complete", "descriptor_registration",
                  "descriptor_default_changed", "enabled_by_default",
                  "registry_changed", "shared_cmake_changed", "ci_changed",
                  "board_or_handoff_changed", "real_corpus_or_weights",
                  "model_or_runtime_loaded", "real_audio_read",
                  "listening_or_device_timing", "benchmark_claim",
                  "release_claim"):
        ok &= _expect(boundary.get(field) is False,
                      "boundary." + field + " must be false", errors)
    for field in ("task_local_only", "installed_v0_unchanged",
                  "opt_in_required"):
        ok &= _expect(boundary.get(field) is True,
                      "boundary." + field + " must be true", errors)
    ok &= _expect(len(report.get("non_claims", [])) >= 10,
                  "non-claims are required", errors)
    ok &= _expect(
        report.get("scope", {}).get("write_scope") == [TASK_PREFIX],
        "write scope must be this directory only", errors)
    ok &= _expect(
        report.get("determinism", {}).get(
            "cold_start_regenerations_required") == 3,
        "three cold-start rounds are required", errors)
    return ok


def check_contract(contract: Dict[str, Any], report: Dict[str, Any],
                   errors: List[str]) -> bool:
    ok = True
    report_text, report_digest = reference.canonical_report(report)
    fresh = reference.canonical_text(
        reference.build_contract(report, report_digest)) + "\n"
    if not CONTRACT.is_file():
        errors.append("contract.json missing")
        return False
    if CONTRACT.read_text(encoding="utf-8") != fresh:
        errors.append("contract.json is not byte-reproducible")
        ok = False
    for field, expected in (
            ("task", reference.TASK_ID),
            ("component", reference.COMPONENT),
            ("title", reference.TITLE),
            ("decision", "DEFER"),
            ("evidence_status", "incomplete"),
            ("qualification_status", "not_qualified"),
            ("blocked_release_gate_count", 8),
            ("task_prefix", TASK_PREFIX),
            ("write_scope", TASK_PREFIX)):
        ok &= _expect(contract.get(field) == expected,
                      "contract." + field + " mismatch", errors)
    ok &= _expect(contract.get("qualification") == report.get("qualification"),
                  "contract qualification mismatch", errors)
    ok &= _expect(contract.get("gates") == report.get("gates"),
                  "contract gates mismatch", errors)
    ok &= _expect(contract.get("release_gates") == report.get("release_gates"),
                  "contract release_gates mismatch", errors)
    ok &= _expect(contract.get("task_row_identity")
                  == report.get("task_row_identity"),
                  "contract board identity mismatch", errors)
    pins = contract.get("artifact_pins", {})
    for name in reference.ARTIFACT_FILES:
        ok &= _expect(TASK_PREFIX + name in pins,
                      "contract misses artifact pin: " + name, errors)
    ok &= _expect(pins.get(TASK_PREFIX + "report.json") == report_digest,
                  "contract report digest mismatch", errors)
    ok &= _expect(len(contract.get("invariants", [])) >= 8,
                  "contract invariants missing", errors)
    ok &= _expect(contract.get("SPDX-License-Identifier") == "Apache-2.0",
                  "contract license mismatch", errors)
    return ok


def check_task_row_identity(report: Dict[str, Any],
                            contract: Dict[str, Any],
                            errors: List[str]) -> bool:
    identity = reference.task_row_identity()
    ok = _expect(report.get("task_row_identity") == identity,
                 "report board identity mismatch", errors)
    ok &= _expect(contract.get("task_row_identity") == identity,
                  "contract board identity mismatch", errors)
    stable = identity.get("stable_fields", {})
    ok &= _expect(stable.get("id") == reference.TASK_ID,
                  "stable row id mismatch", errors)
    ok &= _expect(stable.get("component") == reference.COMPONENT,
                  "stable row component mismatch", errors)
    ok &= _expect(identity.get("full_tasks_json_hashed") is False,
                  "the full task board must not be hashed", errors)
    ok &= _expect(identity.get("whole_file_hashed") is False,
                  "the whole task board must not be hashed", errors)
    ok &= _expect(
        identity.get("stable_sha256")
        == sha256(reference.canonical_text(stable).encode("utf-8")),
        "stable identity digest is inconsistent", errors)
    return ok


def check_assets(report: Dict[str, Any], errors: List[str]) -> bool:
    audit = report.get("asset_audit", {})
    ok = _expect(audit.get("all_absence_probes_absent") is True,
                 "an absence probe is present", errors)
    ok &= _expect(
        all(item.get("exists") is False
            for item in audit.get("absence_probes", [])),
        "every absence probe must be absent", errors)
    return ok


def check_control(report: Dict[str, Any], errors: List[str]) -> bool:
    control = report.get("reference_protocol", {})
    baseline = control.get("identity_baseline", {})
    ok = _expect(control.get("model_executed") is False,
                 "no model may be executed", errors)
    ok &= _expect(control.get("executor") == "absent",
                  "candidate executor must be absent", errors)
    ok &= _expect(baseline.get("digest_equal") is True,
                  "identity baseline digest must be exact", errors)
    ok &= _expect(baseline.get("sample_count_equal") is True,
                  "identity baseline sample count must be preserved", errors)
    ok &= _expect(baseline.get("duration_equal") is True,
                  "identity baseline duration must be preserved", errors)
    ok &= _expect(baseline.get("qualification_effect") == "none",
                  "identity control must not qualify", errors)
    admission = control.get("request_admission", {})
    ok &= _expect(admission.get("identity_control_accepted") is True,
                  "identity control must be admitted", errors)
    ok &= _expect(admission.get("candidate_smoother_used") is False,
                  "candidate smoother must not be used", errors)
    ok &= _expect(len(admission.get("rejected_targets", [])) == 2,
                  "both candidate targets must be rejected", errors)
    spec = control.get("smoother_specification_gate", {})
    ok &= _expect(spec.get("complete_example_accepted") is True,
                  "complete specification probe must be admissible", errors)
    ok &= _expect(spec.get("incomplete_rejected_count") == 3,
                  "incomplete specification probes must be rejected", errors)
    ok &= _expect(spec.get("candidate_executed") is False,
                  "specification probe must not execute a candidate", errors)
    adverse = control.get("adverse", [])
    ok &= _expect(len(adverse) == len(reference.ADVERSE_CASE_IDS),
                  "adverse case count mismatch", errors)
    ok &= _expect([item.get("case") for item in adverse]
                  == list(reference.ADVERSE_CASE_IDS),
                  "adverse case ids mismatch", errors)
    ok &= _expect(all(item.get("result") == "rejected" for item in adverse),
                  "an adverse case was not rejected", errors)
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append(
            "package is not reproducible: "
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
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="f0-contour-verify-", dir=root))
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
                generated_sidecar = target / "report.json.sha256"
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
                if (not generated_sidecar.is_file()
                        or generated_sidecar.read_bytes() != sidecar):
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
    return ok, digest, repeats


def check_licensing(errors: List[str]) -> bool:
    copyright_line = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX-" + "License-Identifier: Apache-2.0"
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:6])
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
    name = "SOURCES.sha256.license"
    path = HERE / name
    if not path.is_file():
        errors.append("missing SPDX sidecar: " + name)
        ok = False
    else:
        text = path.read_text(encoding="utf-8")
        if copyright_line not in text or license_line not in text:
            errors.append("invalid SPDX sidecar: " + name)
            ok = False
    reuse = SDK / "REUSE.toml"
    if reuse.is_file():
        text = reuse.read_text(encoding="utf-8")
        if '"docs/**"' not in text and "docs/**" not in text:
            errors.append("REUSE.toml does not cover docs/**")
            ok = False
    else:
        errors.append("REUSE.toml missing")
        ok = False
    return ok


def check_scope(errors: List[str]) -> bool:
    if not (SDK / ".git").exists():
        return True
    result = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append("out of scope change: " + path)
            ok = False
    branch = subprocess.run(
        ["git", "-C", str(SDK), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=False)
    if branch.returncode == 0 and branch.stdout.strip() != reference.BRANCH:
        errors.append("unexpected branch: " + branch.stdout.strip())
        ok = False
    ancestor = subprocess.run(
        ["git", "-C", str(SDK), "merge-base", "--is-ancestor",
         reference.BASE_COMMIT, "HEAD"],
        capture_output=True, text=True, check=False)
    if ancestor.returncode != 0:
        errors.append("base commit is not an ancestor of HEAD")
        ok = False
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    verified = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    json_ok = report is not None and contract is not None
    report_ok = check_report(report, errors) if report is not None else False
    contract_ok = (
        check_contract(contract, report, errors)
        if contract is not None and report is not None else False)
    identity_ok = (
        check_task_row_identity(report, contract, errors)
        if report is not None and contract is not None else False)
    assets_ok = check_assets(report, errors) if report is not None else False
    control_ok = check_control(report, errors) if report is not None else False
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        return 1
    if not all((json_ok, report_ok, contract_ok, identity_ok, assets_ok,
                control_ok, licensing_ok, sources_ok, reproduction_ok,
                scope_ok)):
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
