# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-CONVERT-AND-SPEAK package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-voice profile, a promoted missing result, a qualified claim,
an open release gate, license gaps, out-of-scope worktree changes, whitespace
damage or a dirty ``git diff --check``. Never writes the package.
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

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = reference.SOURCE_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:source|worktree|pkg):[A-Za-z0-9_./-]+)$")
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "component", "title", "repository", "version",
    "profile", "status", "evidence_status", "decision", "defer_before",
    "qualification_status", "qualification", "base_commit", "branch",
    "worktree", "reviewer", "format", "boundary", "scope",
    "task_row_identity", "source_pins", "boundary_pins",
    "source_reported_context", "candidate", "reference", "asset_requirements",
    "asset_audit", "external_artifacts", "caller_asset_contract",
    "acceptance_profile", "licensing", "reference_protocol", "controls",
    "release_gates", "exact_blockers", "reopen_conditions", "candidate_metrics",
    "missing_historical_artifacts", "non_claims", "tool_provenance",
    "repeatability", "determinism", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "mode", "version",
    "base_commit", "branch", "worktree", "reviewer", "status", "decision",
    "defer_before", "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "write_scope", "acceptance_profile",
    "candidate", "format", "licensing", "artifact_pins", "board_row",
    "boundary", "boundary_pins", "source_pins", "scope", "reference",
    "exact_blockers", "release_gates", "reopen_condition", "negative_claims",
    "caller_asset_contract", "source_reported_context", "qualification",
    "invariants",
}


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.load_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("JSON root is not an object: " + label)
        return {}
    return payload


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        text, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != text.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if not SIDECAR.is_file():
            errors.append("report.json.sha256 is missing")
        elif SIDECAR.read_text(encoding="ascii") != (
                f"{digest}  report.json\n"):
            errors.append("report.json.sha256 is stale or not sha256sum-style")
    if contract:
        if CONTRACT.read_bytes() != (
                reference.canonical_text(contract) + "\n").encode("utf-8"):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    if not any(line.startswith("#") for line in lines):
        errors.append("SOURCES.sha256 has no provenance header")
    count = 0
    seen: set[str] = set()
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        if "TASKS.json" in raw:
            errors.append("mutable full task board appears in pins")
        match = PIN_LINE.fullmatch(raw)
        if not match:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, label = match.groups()
        if label in seen:
            errors.append("duplicate pin: " + label)
            continue
        seen.add(label)
        prefix, relative = label.split(":", 1)
        if relative.startswith("/") or ".." in Path(relative).parts:
            errors.append("unsafe pin path: " + label)
            continue
        base = {"source": SOURCE_ROOT, "worktree": SDK_ROOT, "pkg": HERE}[prefix]
        path = base / relative
        if not path.is_file():
            errors.append("pinned file missing: " + label)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + label)
    for name in reference.PIN_FILES:
        if "pkg:" + name not in seen:
            errors.append("unpinned package file: " + name)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic bytes")
    except (OSError, reference.Reject) as error:
        errors.append("pin regeneration failed: " + str(error))
    return count


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    live = reference.task_row_identity()
    _eq(errors, "report board identity is stale",
        report.get("task_row_identity"), live)
    _eq(errors, "contract board identity is stale",
        contract.get("board_row"), live)
    row = report.get("task_row_identity", {})
    if row.get("whole_file_hashed") is not False:
        errors.append("full task board is hashed")
    stable = row.get("stable_fields", {})
    if reference.sha256(reference.canonical_bytes(stable)) != row.get(
            "stable_sha256"):
        errors.append("stable board hash mismatch")
    if stable.get("id") != reference.TASK:
        errors.append("stable board task id mismatch")
    if stable.get("mode") != "feasibility":
        errors.append("stable board mode mismatch")
    for section in ("source_pins", "boundary_pins"):
        for path in report.get(section, {}):
            if path.endswith("TASKS.json"):
                errors.append("mutable task board is pinned in " + section)


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    missing = REQUIRED_REPORT_KEYS - set(report)
    if missing:
        errors.append("report missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected report schema", report["schema_id"],
        reference.SCHEMA_ID)
    _eq(errors, "report status", report["status"], reference.STATUS)
    _eq(errors, "report evidence status", report["evidence_status"],
        "incomplete")
    _eq(errors, "report decision", report["decision"], "DEFER")
    _eq(errors, "report defer point", report["defer_before"],
        "opt_in_adapter_exposure")
    _eq(errors, "report profile", report["profile"], "voice")
    _eq(errors, "report task", report["task_id"], reference.TASK)
    _eq(errors, "report component", report["component"], reference.COMPONENT)
    _eq(errors, "report base commit", report["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report["branch"], reference.BRANCH)
    _eq(errors, "report worktree", report["worktree"], reference.CLAIM_WORKTREE)
    _eq(errors, "report reviewer", report["reviewer"], reference.REVIEWER)

    qualification = report["qualification"]
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    _eq(errors, "nested decision", qualification.get("decision"), "DEFER")
    if qualification.get("candidate_qualified") is not False:
        errors.append("candidate_qualified is not false")
    if qualification.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing-result guard is absent")
    if qualification.get("missing_result_promoted") is not False:
        errors.append("a missing result is promoted")
    for key in ("exact_source_present", "exact_weights_present",
                "exact_runtime_outputs_present", "rights_cleared_cohort",
                "geometry_documented", "parity_measured", "timing_measured",
                "listening", "real_corpus_used"):
        if qualification.get(key) is not False:
            errors.append("qualification promotes a missing result: " + key)

    gates = report["release_gates"]
    _eq(errors, "release gate count", len(gates), 8)
    _eq(errors, "release gate IDs", [gate.get("id") for gate in gates],
        [f"RG-{index:02d}" for index in range(1, 9)])
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("a release gate is not blocked")
    _eq(errors, "nested blocked gate count",
        qualification.get("blocked_gate_count"), 8)
    _eq(errors, "nested blocked gate IDs",
        qualification.get("blocked_gate_ids"),
        [gate["id"] for gate in gates])

    profile = report["acceptance_profile"]
    _eq(errors, "voice profile not recorded", profile.get("profile"), "voice")
    items = profile.get("required_items", {})
    _eq(errors, "voice profile item count", len(items), 7)
    _eq(errors, "voice satisfied list",
        profile.get("satisfied_for_qualification"), [])
    for name, item in items.items():
        if item.get("status") not in {"absent", "not_measured",
                                      "structural_only"}:
            errors.append("voice item promoted: " + name)
        if item.get("qualification_effect") != "none":
            errors.append("voice item has a qualification effect: " + name)
    expected_blocked = sorted(
        name for name, item in items.items()
        if item.get("status") in {"absent", "not_measured"})
    _eq(errors, "voice blocked list mismatch", profile.get("blocked_items"),
        expected_blocked)

    candidate = report["candidate"]
    for key in ("reported_input_sample_rate_hz",
                "reported_output_sample_rate_hz", "reported_hop_samples",
                "reported_parameter_count"):
        if candidate.get(key) is not None:
            errors.append("candidate geometry is fabricated: " + key)
    for key in ("geometry_documented", "source_present", "weights_present",
                "runtime_present", "exact_numeric_output_present"):
        if candidate.get(key) is not False:
            errors.append("candidate claim is not false: " + key)

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    for key in ("candidate_geometry_documented", "candidate_mode_asserted",
                "surrogate_incremental_streaming",
                "sdk_v0_geometry_preserved"):
        expected = True if key == "sdk_v0_geometry_preserved" else False
        if fmt.get(key) is not expected:
            errors.append("format flag mismatch: " + key)
    if fmt.get("candidate_input_sample_rate_hz") is not None:
        errors.append("format invents a candidate input rate")
    if fmt.get("candidate_output_sample_rate_hz") is not None:
        errors.append("format invents a candidate output rate")

    ref = report["reference"]
    for key in ("source_present", "weights_present", "runtime_present",
                "implementation_present", "adapter_present",
                "exact_numeric_output_present", "surrogate_is_candidate"):
        if ref.get(key) is not False:
            errors.append("reference claim is not false: " + key)
    _eq(errors, "reference status", ref.get("status"), "blocked")
    if ref.get("pinned_revision") is not None:
        errors.append("a candidate revision is fabricated")
    if ref.get("license_identity") is not None:
        errors.append("a candidate license identity is fabricated")

    audit = report["asset_audit"]
    _eq(errors, "audit result", audit.get("audit_result"), "absent")
    if audit.get("qualified") is not False:
        errors.append("asset audit claims qualification")
    for key in ("source_present", "weights_present", "runtime_env_present",
                "runtime_lock_present", "rights_record_present",
                "consent_record_present", "cohort_manifest_present"):
        if audit.get(key) is not False:
            errors.append("asset audit claims presence: " + key)
    _eq(errors, "sample clip count", audit.get("sample_clip_count"), 3)
    _eq(errors, "live audit is stale", audit.get("observed"),
        reference.audit_assets())

    requirements = {item.get("id"): item
                    for item in report["asset_requirements"]}
    for key in ("candidate_source", "candidate_weights"):
        if requirements.get(key, {}).get("sha256") is not None:
            errors.append("fabricated asset digest: " + key)
    if requirements.get("exact_runtime", {}).get(
            "runtime_lock_sha256") is not None:
        errors.append("fabricated runtime lock digest")
    if requirements.get("approved_reference_parity_vector", {}).get(
            "sha256") is not None:
        errors.append("fabricated parity digest")

    contract_data = report["caller_asset_contract"]
    _eq(errors, "caller absent behavior",
        contract_data.get("absent_behavior"), "reject_before_processing")
    if contract_data.get("asset_is_vendored") is not False:
        errors.append("caller asset is marked vendored")
    if contract_data.get("positive_admission_possible") is not False:
        errors.append("caller admission claims a possible positive path")
    _eq(errors, "caller admission status",
        contract_data.get("admission_status"),
        "blocked_no_approved_identity")
    if contract_data.get("approved_source_revision") is not None:
        errors.append("caller contract fabricates a revision")
    if contract_data.get("approved_weights_sha256") is not None:
        errors.append("caller contract fabricates a weight digest")

    control = report["reference_protocol"]
    if control.get("model_executed") is not False:
        errors.append("reference protocol claims model execution")
    _eq(errors, "reference executor", control.get("executor"), "absent")
    _eq(errors, "control plan source", control.get("plan_source"),
        reference.CONTROL_PLAN_PROVENANCE)
    _eq(errors, "control qualification effect",
        control.get("qualification_effect"), "none")
    _eq(errors, "control duration ratio",
        control.get("duration", {}).get("duration_ratio"), "1")
    alignment = control.get("alignment", {})
    if alignment.get("streaming_supported") is not False:
        errors.append("control claims streaming")
    _eq(errors, "control alignment mode", alignment.get("mode"),
        "offline_whole_utterance")
    if alignment.get("candidate_alignment_asserted") is not False:
        errors.append("control asserts candidate alignment")
    if control.get("surrogate", {}).get("uses_target_reference") is not False:
        errors.append("surrogate claims target-reference use")
    if control.get("reset", {}).get("matches_fresh") is not True:
        errors.append("surrogate reset does not match fresh state")
    if control.get("reset", {}).get("candidate_reset_asserted") is not False:
        errors.append("surrogate asserts candidate reset")
    for outcome in control.get("acceptance_outcomes", []):
        if outcome.get("measured") is not False or outcome.get("value") is not None:
            errors.append("an acceptance outcome claims a measurement")

    adverse = report["controls"]["adverse"]
    _eq(errors, "adverse case count", len(adverse),
        len(reference.ADVERSE_CASE_IDS))
    _eq(errors, "adverse case IDs", [item.get("case_id") for item in adverse],
        list(reference.ADVERSE_CASE_IDS))
    for item in adverse:
        if item.get("status") != "rejected":
            errors.append("adverse case not rejected: "
                          + item.get("case_id", "?"))
        if item.get("state_unchanged") is not True:
            errors.append("adverse case changed state: "
                          + item.get("case_id", "?"))
    _eq(errors, "adverse case count field",
        report["controls"].get("adverse_case_count"), len(adverse))
    if report["controls"].get("adverse_all_rejected") is not True:
        errors.append("adverse_all_rejected is not true")
    if report["controls"].get("missing_asset_rejected_before_processing") is not True:
        errors.append("missing-asset control missing")
    if report["controls"].get("missing_result_never_qualifies") is not True:
        errors.append("missing-result control missing")

    licensing = report["licensing"]
    if licensing.get("source_license_identity") is not None:
        errors.append("an upstream license is asserted")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    for key in ("source_license_present", "weight_terms_present",
                "model_card_present", "attribution_notice_staged",
                "training_data_statement_staged", "redistribution_reviewed",
                "product_use_reviewed"):
        if licensing.get(key) is not False:
            errors.append("license claim is not false: " + key)

    context = report["source_reported_context"]
    _eq(errors, "source-reported label", context.get("label"),
        "source_reported_not_measured_here")
    _eq(errors, "source-reported line", context.get("source_line"), 172)
    _eq(errors, "source-reported local run", context.get("local_run"),
        "not_run")
    if context.get("reported_latency") is not None:
        errors.append("source-reported latency is fabricated")

    if len(report["exact_blockers"]) != 8:
        errors.append("expected exactly eight exact blockers")
    if len(report["reopen_conditions"]) != 8:
        errors.append("expected exactly eight reopen conditions")
    _eq(errors, "repeatability runs",
        report["repeatability"].get("runs"), 3)
    _eq(errors, "cold-start requirement",
        report["determinism"].get("cold_start_regenerations_required"), 3)

    boundary = report["boundary"]
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("a boundary flag claims a change")
    scope = report["scope"]
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("scope flag is not false: " + key)

    text = reference.canonical_text(report)
    if '"status":"qualified"' in text or '"candidate_qualified":true' in text:
        errors.append("canonical report contains a qualified claim")
    if "TASKS.json" in reference.canonical_text(report["source_pins"]):
        errors.append("mutable task board appears in source pins")


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected contract schema", contract["schema_id"],
        reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract["task"], reference.TASK)
    _eq(errors, "contract component", contract["component"],
        reference.COMPONENT)
    _eq(errors, "contract mode", contract["mode"], "feasibility")
    _eq(errors, "contract base commit", contract["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract["branch"], reference.BRANCH)
    _eq(errors, "contract worktree", contract["worktree"],
        reference.CLAIM_WORKTREE)
    _eq(errors, "contract reviewer", contract["reviewer"],
        reference.REVIEWER)
    _eq(errors, "contract decision", contract["decision"], "DEFER")
    _eq(errors, "contract evidence status", contract["evidence_status"],
        "incomplete")
    _eq(errors, "contract qualification", contract["qualification_status"],
        "not_qualified")
    _eq(errors, "contract verification profile",
        contract["verification_profile"], "voice")
    _eq(errors, "contract write scope", contract["write_scope"],
        reference.TASK_PREFIX)
    for key in ("release_gates", "exact_blockers", "source_pins",
                "boundary_pins", "candidate", "format", "licensing",
                "acceptance_profile", "qualification", "boundary", "scope",
                "reference", "caller_asset_contract"):
        _eq(errors, "contract/report differ: " + key,
            contract.get(key), report.get(key))
    _eq(errors, "contract/report board identity differ",
        contract.get("board_row"), report.get("task_row_identity"))
    _eq(errors, "contract/report source context differ",
        contract.get("source_reported_context"),
        report.get("source_reported_context"))

    boundary = contract.get("boundary", {})
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("contract boundary flag claims a change")
    scope = contract.get("scope", {})
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("contract scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("contract scope flag is not false: " + key)

    pins = contract.get("artifact_pins", {})
    expected_names = {reference.TASK_PREFIX + name
                      for name in reference.ARTIFACT_FILES}
    if set(pins) != expected_names:
        errors.append("artifact pin set mismatch")
    for path, digest in pins.items():
        full = SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact pin missing: " + path)
        elif reference.file_digest(full) != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256"):
        if reference.TASK_PREFIX + forbidden in pins:
            errors.append("self-referential artifact pin: " + forbidden)
    if len(contract.get("release_gates", [])) != 8:
        errors.append("contract gate count is not eight")
    if any(gate.get("status") != "blocked"
           for gate in contract.get("release_gates", [])):
        errors.append("contract has a non-blocked gate")
    if len(contract.get("exact_blockers", [])) != 8:
        errors.append("contract blocker count is not eight")
    if not contract.get("reopen_condition"):
        errors.append("contract reopen condition missing")


def check_repeats(errors: List[str]) -> None:
    texts = [reference.canonical_report(reference.build_report())[0]
             for _ in range(3)]
    if len(set(texts)) != 1:
        errors.append("three fresh report builds differ")
    if texts and texts[0].encode("utf-8") != REPORT.read_bytes():
        errors.append("fresh build does not match report.json")


def check_cold_starts(errors: List[str]) -> List[str]:
    expected = reference.canonical_report(reference.build_report())[0].encode(
        "utf-8")
    base = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    digests: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="convert-and-speak-verify-",
                                     dir=base))
    except OSError as error:
        errors.append("cold-start scratch unavailable: " + str(error))
        return digests
    try:
        for index in range(3):
            target = work / f"cold-{index}"
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--out", str(target)],
                cwd=str(HERE), env=environment, capture_output=True, text=True,
                check=False)
            generated = target / "report.json"
            if result.returncode != 0 or not generated.is_file():
                errors.append(f"cold regeneration {index} failed: "
                              + (result.stderr.strip()
                                 or result.stdout.strip()))
                continue
            data = generated.read_bytes()
            digests.append(reference.sha256(data))
            if data != expected:
                errors.append(
                    f"cold regeneration {index} is not byte-identical")
            sidecar = target / "report.json.sha256"
            if not sidecar.is_file() or sidecar.read_bytes() != (
                    f"{reference.sha256(data)}  report.json\n").encode("ascii"):
                errors.append(f"cold regeneration {index} sidecar differs")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if len(digests) == 3 and len(set(digests)) != 1:
        errors.append("cold-start report digests differ")
    return digests


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "voice", "Convert and Speak", "not Convert and Speak",
                  "blocked", "no runnable local checkpoint"):
        if token not in text:
            errors.append("README is missing token: " + token)
    for digest in (list(reference.SOURCE_PINS.values())
                   + list(reference.BOUNDARY_PINS.values())):
        if digest not in text:
            errors.append("README is missing pinned digest: " + digest)
    if report:
        for token in (reference.BASE_COMMIT, reference.TASK):
            if token not in text:
                errors.append("README is missing identity: " + token)


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md is missing its SPDX header")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing license sidecar: " + name)
            continue
        content = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in content or SPDX_COPYRIGHT not in content:
            errors.append("invalid license sidecar: " + name)
    reuse_path = SDK_ROOT / "REUSE.toml"
    if not reuse_path.is_file():
        errors.append("REUSE.toml missing")
        return
    reuse = reuse_path.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or (
            'SPDX' '-License-Identifier = "Apache-2.0"') not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: "
                      + (diff_check.stdout.strip()
                         or diff_check.stderr.strip()))
    return changed


def main() -> int:
    errors: List[str] = []
    loaded = check_json_files(errors)
    report = loaded.get("report", {})
    contract = loaded.get("contract", {})
    pin_count = check_pins(errors)
    check_report(errors, report)
    check_contract(errors, contract, report)
    if report and contract:
        check_board(errors, report, contract)
    check_repeats(errors)
    cold = check_cold_starts(errors)
    check_readme(errors, report)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256="
          f"{reference.file_digest(REPORT)} repeats_ok=3 "
          f"cold_starts_ok={len(cold)} licensing_ok=1 scope_ok=1 "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
