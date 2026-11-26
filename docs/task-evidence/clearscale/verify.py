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

import reference

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = "docs/task-evidence/clearscale/"
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  "
    r"((?:pkg|source|worktree|sibling):[A-Za-z0-9_./-]+)$")


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
        path = {
            "pkg": HERE,
            "source": SOURCE_ROOT,
            "worktree": SDK,
            "sibling": SDK,
        }[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file()
        and path.name not in ("SOURCES.sha256",)
        and not path.name.endswith(".pyc")
        and "__pycache__" not in path.name
    }
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            errors.append("unpinned package file: " + name)
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
        else:
            checked += 1
    return checked


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append(f"strict json failed for {path.name}: {error}")
        return None


def _expect(condition: bool, message: str, errors: List[str]) -> bool:
    if not condition:
        errors.append(message)
    return bool(condition)


def check_report(report: Dict[str, Any] | None,
                 errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True
    expected = {
        "schema_id": reference.SCHEMA_ID,
        "task_id": reference.TASK,
        "component": reference.COMPONENT,
        "mode": reference.MODE,
        "profile": reference.PROFILE,
        "status": reference.STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "decision": "DEFER",
        "defer_before": reference.DEFER_BEFORE,
        "qualification_status": "not_qualified",
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "worktree": reference.CLAIM_WORKTREE,
        "reviewer": reference.REVIEWER,
    }
    for field, value in expected.items():
        ok &= _expect(report.get(field) == value,
                      f"report {field} mismatch", errors)
    ok &= _expect(report.get("proposal_only") is True,
                  "report must be proposal_only", errors)
    ok &= _expect(report.get("candidate_metrics") is None,
                  "report must not carry candidate metrics", errors)

    qualification = report.get("qualification")
    ok &= _expect(isinstance(qualification, dict),
                  "qualification missing", errors)
    if isinstance(qualification, dict):
        ok &= _expect(qualification.get("status") == "not_qualified",
                      "qualification status must be not_qualified", errors)
        ok &= _expect(qualification.get("candidate_qualified") is False,
                      "candidate must not be qualified", errors)
        ok &= _expect(
            qualification.get("no_missing_result_qualifies_candidate")
            is True,
            "missing results must never qualify", errors)
        ok &= _expect(qualification.get("blocked_gate_count") == 8,
                      "must record eight blocked gates", errors)
        ok &= _expect(qualification.get("decision") == "DEFER",
                      "qualification decision must be DEFER", errors)

    gates = report.get("gates")
    ok &= _expect(isinstance(gates, list) and len(gates) == 8,
                  "must record eight gates", errors)
    if isinstance(gates, list):
        expected_gates = [gate for gate, _ in reference.GATE_REQUIREMENTS]
        ok &= _expect([gate.get("id") for gate in gates] == expected_gates,
                      "gate ids mismatch", errors)
        for gate in gates:
            ok &= _expect(gate.get("status") == "blocked",
                          "every gate must be blocked", errors)
            ok &= _expect(gate.get("qualifies") is False,
                          "no gate may qualify", errors)

    blockers = report.get("exact_blockers")
    ok &= _expect(isinstance(blockers, list) and len(blockers) == 8,
                  "must record eight exact blockers", errors)
    if isinstance(blockers, list):
        for blocker in blockers:
            ok &= _expect(blocker.get("state") == "absent",
                          "every exact blocker must be absent", errors)

    boundary = report.get("boundary")
    ok &= _expect(isinstance(boundary, dict), "boundary missing", errors)
    if isinstance(boundary, dict):
        for key, value in boundary.items():
            if key == "descriptor_settings":
                ok &= _expect(value == {}, "descriptor settings must be empty",
                              errors)
            else:
                ok &= _expect(value is False,
                              f"boundary {key} must be false", errors)

    scope = report.get("scope")
    ok &= _expect(isinstance(scope, dict), "scope missing", errors)
    if isinstance(scope, dict):
        for key, value in scope.items():
            if key == "task_local_only":
                ok &= _expect(value is True, "scope must be task_local_only",
                              errors)
            else:
                ok &= _expect(value is False,
                              f"scope {key} must be false", errors)

    upstream = report.get("upstream_identity")
    ok &= _expect(isinstance(upstream, dict), "upstream identity missing",
                  errors)
    if isinstance(upstream, dict):
        for field in ("project_url", "repository_url", "revision"):
            ok &= _expect(upstream.get(field) is None,
                          f"upstream {field} must not be fabricated", errors)
        ok &= _expect(upstream.get("revision_pin_available") is False,
                      "revision pin must be unavailable", errors)
        ok &= _expect(upstream.get("pinned_candidate_source_present") is False,
                      "candidate source must be absent", errors)
        ok &= _expect(upstream.get("neural_weights_applicable") is False,
                      "neural weights must not apply", errors)

    audit = report.get("asset_audit")
    ok &= _expect(isinstance(audit, dict), "asset audit missing", errors)
    if isinstance(audit, dict):
        ok &= _expect(audit.get("audit_result") == "absent",
                      "audit result must be absent", errors)
        ok &= _expect(audit.get("qualified") is False,
                      "audit must not qualify", errors)
        ok &= _expect(audit.get("source_present") is False,
                      "source must be absent", errors)
        ok &= _expect(audit.get("implementation_artifact_present") is False,
                      "implementation must be absent", errors)
        ok &= _expect(audit.get("runtime_lock_present") is False,
                      "runtime lock must be absent", errors)
        ok &= _expect(audit.get("rights_record_present") is False,
                      "rights record must be absent", errors)
        ok &= _expect(audit.get("all_absence_probes_absent") is True,
                      "absence probes must all be absent", errors)

    controls = report.get("controls")
    ok &= _expect(isinstance(controls, dict), "controls missing", errors)
    if isinstance(controls, dict):
        for key in ("invalid_values_rejected",
                    "missing_asset_rejected_before_processing",
                    "missing_result_never_qualifies",
                    "nonfinite_rejected",
                    "implementation_absent_and_not_executed",
                    "absence_probes_all_absent",
                    "adverse_all_rejected"):
            ok &= _expect(controls.get(key) is True,
                          f"control {key} must be true", errors)
        adverse = controls.get("adverse")
        ok &= _expect(isinstance(adverse, list)
                      and len(adverse) == len(reference.ADVERSE_CASE_IDS),
                      "adverse case count mismatch", errors)
        if isinstance(adverse, list):
            for item in adverse:
                ok &= _expect(item.get("result") == "rejected",
                              "adverse case must be rejected", errors)

    profile = report.get("rate_profile")
    ok &= _expect(isinstance(profile, dict), "rate profile missing", errors)
    if isinstance(profile, dict):
        ok &= _expect(profile.get("satisfied_for_qualification") == [],
                      "no rate requirement may be satisfied", errors)
        items = profile.get("required_items")
        ok &= _expect(isinstance(items, list)
                      and len(items) == len(reference.RATE_REQUIREMENTS),
                      "rate profile item count mismatch", errors)
        if isinstance(items, list):
            for item in items:
                ok &= _expect(
                    item.get("satisfied_for_qualification") is False,
                    "rate item must not be satisfied", errors)
                ok &= _expect(item.get("qualification_effect") == "none",
                              "rate item must have no effect", errors)

    identity = report.get("task_row_identity")
    ok &= _expect(isinstance(identity, dict), "task identity missing", errors)
    if isinstance(identity, dict):
        ok &= _expect(identity.get("whole_file_hashed") is False,
                      "whole board must not be hashed", errors)
        ok &= _expect(identity.get("source") ==
                      "audio-benchmark-platform/plan/swarm/TASKS.json",
                      "task identity source mismatch", errors)
        ok &= _expect(identity.get("stable_sha256") ==
                      reference.task_row_identity()["stable_sha256"],
                      "task identity digest mismatch", errors)
        claim = identity.get("claim")
        ok &= _expect(isinstance(claim, dict), "task claim missing", errors)
        if isinstance(claim, dict):
            ok &= _expect(claim.get("base_commit") == reference.BASE_COMMIT,
                          "claim base commit mismatch", errors)
            ok &= _expect(claim.get("branch") == reference.BRANCH,
                          "claim branch mismatch", errors)

    source_pins = report.get("source_pins")
    boundary_pins = report.get("boundary_pins")
    sibling_pins = report.get("sibling_pins")
    for name, value in (("source_pins", source_pins),
                        ("boundary_pins", boundary_pins),
                        ("sibling_pins", sibling_pins)):
        ok &= _expect(isinstance(value, dict) and value,
                      f"{name} missing", errors)
        if isinstance(value, dict):
            ok &= _expect("TASKS.json" not in "".join(value),
                          f"{name} must not pin TASKS.json", errors)
    ok &= _expect(source_pins == reference.SOURCE_PINS,
                  "source pins mismatch", errors)
    ok &= _expect(boundary_pins == reference.BOUNDARY_PINS,
                  "boundary pins mismatch", errors)
    ok &= _expect(sibling_pins == reference.SIBLING_PINS,
                  "sibling pins mismatch", errors)

    context = report.get("source_reported_context")
    ok &= _expect(isinstance(context, dict), "source context missing", errors)
    if isinstance(context, dict):
        ok &= _expect(context.get("is_benchmark_report") is False,
                      "note is not a benchmark", errors)
        ok &= _expect(context.get("source_reported_not_reexecuted") is True,
                      "note must not be re-executed", errors)
        quote = context.get("candidate_status_quote", "")
        ok &= _expect("abandoned" in quote and
                      "no usable current licence/status" in quote,
                      "candidate quote mismatch", errors)

    siblings = report.get("sibling_evidence")
    ok &= _expect(isinstance(siblings, list) and len(siblings) >= 6,
                  "sibling evidence missing", errors)
    if isinstance(siblings, list):
        ids = {item.get("id") for item in siblings
               if isinstance(item, dict)}
        ok &= _expect({"audiosr", "gtcrn-dns3-offline",
                       "soundtouch"}.issubset(ids),
                      "expected adjacent sibling packages", errors)
        ok &= _expect("clearscale" not in ids,
                      "candidate must not be a sibling", errors)

    missing = report.get("missing_historical_artifacts")
    ok &= _expect(isinstance(missing, list) and len(missing) >= 8,
                  "missing artifacts must be recorded", errors)
    if isinstance(missing, list):
        for path in missing:
            ok &= _expect(not (SOURCE_ROOT / path).exists(),
                          f"recorded missing artifact exists: {path}", errors)

    determinism = report.get("determinism")
    ok &= _expect(isinstance(determinism, dict), "determinism missing", errors)
    if isinstance(determinism, dict):
        ok &= _expect(determinism.get("cold_start_regenerations_required") == 3,
                      "three cold starts required", errors)
    return bool(ok)


def check_contract(contract: Dict[str, Any] | None,
                   report: Dict[str, Any] | None,
                   errors: List[str]) -> bool:
    if contract is None or report is None:
        return False
    ok = True
    for field, value in (
            ("schema_id", reference.CONTRACT_SCHEMA_ID),
            ("task", reference.TASK),
            ("component", reference.COMPONENT),
            ("mode", reference.MODE),
            ("profile", reference.PROFILE),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("decision", "DEFER"),
            ("defer_before", reference.DEFER_BEFORE),
            ("base_commit", reference.BASE_COMMIT),
            ("branch", reference.BRANCH),
            ("worktree", reference.CLAIM_WORKTREE),
            ("reviewer", reference.REVIEWER),
            ("write_scope", TASK_PREFIX),
            ("repository", "audio-sdk")):
        ok &= _expect(contract.get(field) == value,
                      f"contract {field} mismatch", errors)
    ok &= _expect(contract.get("proposal_only") is True,
                  "contract must be proposal_only", errors)
    ok &= _expect(contract.get("qualification") == report.get("qualification"),
                  "contract qualification differs from report", errors)
    ok &= _expect(contract.get("gates") == report.get("gates"),
                  "contract gates differ from report", errors)
    ok &= _expect(contract.get("exact_blockers") ==
                  report.get("exact_blockers"),
                  "contract blockers differ from report", errors)
    ok &= _expect(contract.get("task_row_identity") ==
                  report.get("task_row_identity"),
                  "contract task identity differs from report", errors)
    ok &= _expect(contract.get("boundary") == report.get("boundary"),
                  "contract boundary differs from report", errors)
    ok &= _expect(contract.get("scope") == report.get("scope"),
                  "contract scope differs from report", errors)
    ok &= _expect(contract.get("source_pins") == reference.SOURCE_PINS,
                  "contract source pins mismatch", errors)
    ok &= _expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS,
                  "contract boundary pins mismatch", errors)
    ok &= _expect(contract.get("sibling_pins") == reference.SIBLING_PINS,
                  "contract sibling pins mismatch", errors)
    ok &= _expect(len(contract.get("rate_profile_requirements", [])) ==
                  len(reference.RATE_REQUIREMENTS),
                  "contract rate profile count mismatch", errors)
    source_checkout = contract.get("source_checkout")
    ok &= _expect(isinstance(source_checkout, dict),
                  "source checkout missing", errors)
    if isinstance(source_checkout, dict):
        ok &= _expect(source_checkout.get("present") is False,
                      "contract source must be absent", errors)
        ok &= _expect(source_checkout.get("revision") is None,
                      "contract revision must be absent", errors)
        ok &= _expect(
            source_checkout.get("revision_pin_available") is False,
            "contract revision pin must be unavailable", errors)
    licensing = contract.get("licensing")
    ok &= _expect(isinstance(licensing, dict), "licensing missing", errors)
    if isinstance(licensing, dict):
        ok &= _expect(licensing.get("license") == "Apache-2.0",
                      "license must be Apache-2.0", errors)
        ok &= _expect(licensing.get("json_sidecars") is True,
                      "JSON sidecars required", errors)
    return bool(ok)


def check_task_row_identity(report: Dict[str, Any],
                            contract: Dict[str, Any],
                            errors: List[str]) -> bool:
    try:
        live = reference.task_row_identity()
    except reference.Reject as error:
        errors.append("task identity unavailable: " + str(error))
        return False
    ok = True
    ok &= _expect(report.get("task_row_identity") == live,
                  "report task identity differs from live row", errors)
    ok &= _expect(contract.get("task_row_identity") == live,
                  "contract task identity differs from live row", errors)
    stable = live["stable_fields"]
    ok &= _expect(stable["acceptance"] ==
                  "Apply the rate acceptance profile; record exact scope, "
                  "evidence, failure/control results, and remaining release "
                  "gates.",
                  "acceptance row mismatch", errors)
    ok &= _expect(stable["deliverable"].startswith(
        "Retain or reproduce the comparison"),
        "deliverable row mismatch", errors)
    ok &= _expect(stable["evidence"] ==
                  ["cpp-library/pipeline-validation/"
                   "playback-speed-candidates.md"],
                  "evidence row mismatch", errors)
    return bool(ok)


def check_assets(report: Dict[str, Any], errors: List[str]) -> bool:
    audit = report.get("asset_audit")
    if not isinstance(audit, dict):
        return False
    observed = audit.get("observed", {})
    ok = True
    ok &= _expect(audit.get("audit_result") == "absent",
                  "audit result must be absent", errors)
    for key in ("source_checkout_present", "license_file_present",
                "implementation_artifact_present", "runtime_env_present",
                "runtime_lock_present", "license_record_present",
                "rights_record_present", "output_use_grant_present",
                "cohort_manifest_present", "parity_manifest_present"):
        ok &= _expect(observed.get(key) is False,
                      f"observed {key} must be false", errors)
    ok &= _expect(observed.get("neural_weights_applicable") is False,
                  "neural weights must not apply", errors)
    probes = report.get("absence_probes")
    ok &= _expect(isinstance(probes, list) and probes,
                  "absence probes missing", errors)
    if isinstance(probes, list):
        for probe in probes:
            ok &= _expect(probe.get("exists") is False,
                          "absence probe must be absent", errors)
    return bool(ok)


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "sources", "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append(
            "SOURCES.sha256 is not reproducible: "
            + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    expected_contract = reference.canonical_contract_bytes()
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    if not CONTRACT.is_file() or CONTRACT.read_bytes() != expected_contract:
        errors.append("contract.json is not byte-reproducible")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="clearscale-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), "report.json",
                     "--out", str(target)],
                    cwd=str(HERE), env=environment, capture_output=True,
                    text=True, check=False)
                contract_result = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), "contract.json",
                     "--out", str(target)],
                    cwd=str(HERE), env=environment, capture_output=True,
                    text=True, check=False)
                generated = target / "report.json"
                generated_sidecar = target / "report.json.sha256"
                generated_contract = target / "contract.json"
                if (result.returncode != 0 or contract_result.returncode != 0
                        or not generated.is_file()):
                    errors.append(
                        f"cold regeneration {index} failed: "
                        + (result.stderr.strip() or result.stdout.strip()
                           or contract_result.stderr.strip()))
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
                if (not generated_contract.is_file()
                        or generated_contract.read_bytes() != expected_contract):
                    errors.append(
                        f"cold regeneration {index} contract differs")
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
    for name in ("SOURCES.sha256.license",):
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
        capture_output=True, text=True, check=True)
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append("out of scope change: " + path)
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
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(
            f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} "
            f"report_ok={report_ok} contract_ok={contract_ok} "
            f"identity_ok={identity_ok} assets_ok={assets_ok} "
            f"licensing_ok={licensing_ok} sources_ok={sources_ok} "
            f"scope_ok={scope_ok} reproduction_ok={reproduction_ok} "
            f"report_sha256={digest}")
        return 1
    print(
        f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} "
        f"report_ok={report_ok} contract_ok={contract_ok} "
        f"identity_ok={identity_ok} assets_ok={assets_ok} "
        f"licensing_ok={licensing_ok} sources_ok={sources_ok} "
        f"scope_ok={scope_ok} reproduction_ok={reproduction_ok} "
        f"cold_repeats={len(repeats)} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
