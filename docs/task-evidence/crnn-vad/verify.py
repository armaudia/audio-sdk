# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-CRNN-VAD package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-analysis profile, a promoted VAD result, a qualified claim, an
open release gate, license gaps, out-of-scope worktree changes, whitespace
damage or a dirty ``git diff --check``. Never writes.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
ALLOWED_FILES = {
    "README.md", "contract.json", "contract.json.license", "reference.py",
    "report.json", "report.json.license", "report.json.sha256",
    "report.json.sha256.license", "run.py", "SOURCES.sha256",
    "SOURCES.sha256.license", "test_reference.py", "verify.py",
}
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "evidence_status", "profile", "acceptance_profile", "profile_blockers",
    "candidate", "reference", "format", "fixture", "surrogate_model",
    "scorer", "results", "controls", "adverse_rejections",
    "adverse_all_rejected", "external_artifacts", "licensing", "caller_asset",
    "board_row", "boundary", "source_pins", "boundary_pins", "scope",
    "qualification", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "repeatability", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile", "candidate",
    "format", "licensing", "surrogate_model", "scorer", "artifact_pins",
    "board_row", "boundary", "boundary_pins", "source_pins", "scope",
    "reference", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "caller_asset_contract", "invariants",
}
REQUIRED_ADVERSE = {
    "duplicate_json_key", "nan_json_constant", "json_root_array",
    "config_8000_hz", "config_stereo", "config_256_frame",
    "frame_nonfinite_nan", "frame_nonfinite_inf", "frame_nonzero_padding",
    "frame_after_final", "manifest_bad_hash", "event_bad_validity",
    "reset_epoch_zero", "chunk_plan_zero",
}
ALLOWED_IMPORTS = {
    "__future__", "argparse", "ast", "hashlib", "json", "math", "os",
    "pathlib", "re", "subprocess", "sys", "typing", "unittest", "reference",
    "run", "fixture", "scorer",
}


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


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label + " (actual=" + repr(actual)
                      + ", expected=" + repr(expected) + ")")


def _false(errors: List[str], label: str, value: Any) -> None:
    if value is not False:
        errors.append(label + " is not false")


def _true(errors: List[str], label: str, value: Any) -> None:
    if value is not True:
        errors.append(label + " is not true")


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        expected, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != expected.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if SIDECAR.read_text(encoding="ascii") != digest + "\n":
            errors.append("report.json.sha256 is stale")
    if contract:
        if CONTRACT.read_bytes() != (
                reference.canonical_text(contract) + "\n").encode("utf-8"):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    count = 0
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, raw_path = parts
        if raw_path.startswith("source:"):
            path = reference.SOURCE_ROOT / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + raw_path)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic generated bytes")
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("pin regeneration failed: " + str(error))
    if "TASKS.json" in PINS.read_text(encoding="utf-8"):
        errors.append("mutable task board is pinned")
    return count


def check_artifact_pins(errors: List[str], report: Dict[str, Any],
                        contract: Dict[str, Any]) -> None:
    if not report or not contract:
        return
    report_text, report_digest = reference.canonical_report(report)
    sidecar_digest = reference.sha256_bytes((report_digest + "\n").encode("ascii"))
    expected = reference.artifact_pins(report_digest, sidecar_digest)
    _eq(errors, "artifact pins are stale", contract.get("artifact_pins"), expected)
    for name in reference.ARTIFACT_FILES:
        path = HERE / name
        if not path.is_file():
            errors.append("artifact file missing: " + name)
    for path in report.get("source_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("mutable task board is pinned in source_pins")
    for path in report.get("boundary_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("mutable task board is pinned in boundary_pins")


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    try:
        live = reference.board_row()
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("board identity failed: " + str(error))
        return
    _eq(errors, "report board identity is stale", report.get("board_row"), live)
    _eq(errors, "contract board identity is stale",
        contract.get("board_row"), live)
    row = report.get("board_row", {})
    _false(errors, "full task board hashed", row.get("full_tasks_json_hashed"))
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    _eq(errors, "stable board task id mismatch", stable.get("id"),
        reference.TASK_ID)
    _eq(errors, "stable board component mismatch", stable.get("component"),
        reference.COMPONENT)


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    missing = REQUIRED_REPORT_KEYS - set(report)
    if missing:
        errors.append("report missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "report schema", report["schema_id"], reference.REPORT_SCHEMA)
    _eq(errors, "report task", report["task"], reference.TASK_ID)
    _eq(errors, "report component", report["component"], reference.COMPONENT)
    _eq(errors, "report base commit", report["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report["branch"], reference.BRANCH)
    _eq(errors, "report status", report["status"], reference.STATUS)
    _eq(errors, "report decision", report["decision"], "DEFER")
    _eq(errors, "report defer point", report["defer_before"],
        "opt_in_adapter_exposure")
    _eq(errors, "report evidence status", report["evidence_status"],
        "incomplete")
    _eq(errors, "report profile", report["profile"], "analysis")

    profile = report["acceptance_profile"]
    _eq(errors, "profile name", profile.get("profile"), "analysis")
    items = profile.get("required_items", {})
    _eq(errors, "analysis item count", len(items), 13)
    for name, item in items.items():
        if item.get("status") != "synthetic_only":
            errors.append("analysis item promoted: " + name)
        if not item.get("evidence"):
            errors.append("analysis item lacks evidence: " + name)
    _eq(errors, "profile blockers", report["profile_blockers"], [])

    candidate = report["candidate"]
    for key in ("architecture", "checkpoint", "source_revision",
                "source_sha256", "weights_sha256", "parameter_count",
                "reported_sample_rate_hz", "reported_hop_samples",
                "reported_window_samples", "reported_output_geometry",
                "license", "paper_reference"):
        if candidate.get(key) is not None:
            errors.append("candidate geometry is fabricated: " + key)
    for key in ("source_present", "weights_present", "runtime_present",
                "adapter_present", "geometry_documented",
                "exact_numeric_output_present", "implemented_here"):
        _false(errors, "candidate claim " + key, candidate.get(key))

    reference_record = report["reference"]
    _eq(errors, "reference status", reference_record.get("status"), "blocked")
    for key in ("source_present", "weights_present", "runtime_present",
                "implementation_present", "adapter_present",
                "exact_numeric_output_present", "surrogate_is_candidate",
                "surrogate_is_crnn"):
        _false(errors, "reference claim " + key, reference_record.get(key))

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    for key in ("candidate_reported_sample_rate_hz",
                "candidate_reported_hop_samples"):
        if fmt.get(key) is not None:
            errors.append("format invents a candidate value: " + key)
    _false(errors, "candidate geometry documented",
           fmt.get("candidate_geometry_documented"))

    fixture = report["fixture"]
    _eq(errors, "fixture length", fixture.get("stream_samples"),
        reference.STREAM_SAMPLES)
    _eq(errors, "fixture frame count", fixture.get("frame_count"), 260)
    _eq(errors, "fixture digest", fixture.get("signal_sha256"),
        "878c40a0674885f39010a97a121bc5ebe5883eb95e557e2d8a0d90f1fc81862a")
    _true(errors, "fixture synthetic", fixture.get("synthetic"))
    _false(errors, "fixture real speech", fixture.get("real_speech"))
    _false(errors, "fixture candidate audio", fixture.get("candidate_audio"))

    model = report["surrogate_model"]
    _eq(errors, "surrogate pin", model.get("sha256"),
        reference.surrogate_model_digest())
    _eq(errors, "surrogate digest mismatch",
        reference.object_digest(model.get("spec", {})), model.get("sha256"))
    for key in ("is_crnn", "is_learned", "has_convolution", "has_recurrence",
                "uses_weights", "uses_checkpoint"):
        _false(errors, "surrogate claim " + key, model.get("spec", {}).get(key))
    _false(errors, "surrogate qualified", model.get("qualifies"))

    scorer = report["scorer"]
    _eq(errors, "scorer pin", scorer.get("sha256"),
        reference.scoring_protocol_digest())
    _eq(errors, "scorer digest mismatch",
        reference.object_digest(scorer.get("spec", {})), scorer.get("sha256"))
    if model.get("sha256") == scorer.get("sha256"):
        errors.append("surrogate and scorer pins are not independent")
    _false(errors, "scorer oracle", scorer.get("oracle_used_for_score"))
    _false(errors, "scorer qualified", scorer.get("qualifies"))

    results = report["results"]
    _eq(errors, "event count", results["events"].get("total"), 260)
    _true(errors, "event sequence contiguous",
          results["events"].get("sequence_contiguous"))
    _eq(errors, "speech event count", results["events"].get("speech_events"), 3)
    _eq(errors, "scored frame count", results["probabilities"].get(
        "scored_frames"), 260)
    _eq(errors, "brier micro", results["probabilities"].get("brier_micro"), 9879)
    _eq(errors, "accuracy ppm", results["probabilities"].get("accuracy_ppm"),
        1000000)
    detections = results["detections"]
    _eq(errors, "positives", detections.get("positives"), 170)
    _eq(errors, "negatives", detections.get("negatives"), 90)
    _eq(errors, "false negatives", detections.get("false_negatives"), 0)
    _eq(errors, "false positives", detections.get("false_positives"), 0)
    _eq(errors, "fn ppm", detections.get("fn_ppm"), 0)
    _eq(errors, "fp ppm", detections.get("fp_ppm"), 0)
    _false(errors, "held-out detection claimed", detections.get("heldout"))
    boundaries = results["boundaries"]
    _eq(errors, "truth runs", boundaries.get("truth_runs"), 3)
    _eq(errors, "detected runs", boundaries.get("detected_runs"), 3)
    _true(errors, "boundaries matched", boundaries.get("all_matched"))
    _eq(errors, "onset delay", boundaries.get("max_abs_onset_delay_frames"), 0)
    _eq(errors, "offset delay", boundaries.get("max_abs_offset_delay_frames"), 0)
    _false(errors, "candidate boundary parity",
           boundaries.get("candidate_boundary_parity"))
    validity = results["validity"]
    _eq(errors, "validity known", validity.get("known"), 260)
    _eq(errors, "validity invalid", validity.get("invalid"), 0)
    _eq(errors, "validity missing", validity.get("missing"), 0)
    _true(errors, "invalid probability null",
          validity.get("invalid_probability_null"))
    _false(errors, "invalid scored as nonspeech",
           validity.get("invalid_scored_as_nonspeech"))
    availability = results["availability"]
    _true(errors, "availability monotone", availability.get("monotone"))
    _true(errors, "availability formula",
          availability.get("formula_matches"))
    _true(errors, "availability intervals",
          availability.get("exact_half_open_intervals"))
    _false(errors, "device timing", availability.get("device_timing_measured"))
    hopping = results["cross_hop"]
    _true(errors, "cross-hop match", hopping.get("all_match"))
    _eq(errors, "cross-hop accepted samples",
        hopping.get("accepted_samples"), reference.STREAM_SAMPLES)
    _false(errors, "scheduler measured", hopping.get("scheduler_measured"))
    for section in ("probabilities", "boundaries", "detections", "validity",
                    "availability", "events", "cross_hop"):
        _false(errors, "result promoted: " + section,
               results[section].get("qualifies"))

    controls = report["controls"]
    for name in ("independent_state", "reset", "final_partial", "event_bus",
                 "invalid_vs_nonspeech", "threshold_sensitivity"):
        _false(errors, "control promoted: " + name,
               controls[name].get("qualifies"))
    _true(errors, "independent speech digest",
          controls["independent_state"].get("speech_digest_matches_solo"))
    _true(errors, "independent quiet digest",
          controls["independent_state"].get("quiet_digest_matches_solo"))
    _true(errors, "reset freshness", controls["reset"].get("matches_fresh"))
    _eq(errors, "reset epoch", controls["reset"].get("reset_epoch"), 2)
    partial = controls["final_partial"]
    _eq(errors, "partial valid count", partial.get("valid_count"), 137)
    _eq(errors, "partial padding", partial.get("padding_samples"), 23)
    _true(errors, "partial advanced by valid",
          partial.get("advanced_by_valid_count"))
    _true(errors, "partial interval exact", partial.get("interval_exact"))
    _true(errors, "post-final rejected", partial.get("post_final_rejected"))
    bus = controls["event_bus"]
    _eq(errors, "bus capacity", bus.get("capacity"), 4)
    _eq(errors, "bus overflow accepted", bus.get("overflow_accepted"), 4)
    _eq(errors, "bus overflow dropped", bus.get("overflow_dropped"), 2)
    _true(errors, "bus stale epoch", bus.get("stale_epoch_dropped"))
    _true(errors, "bus stale sequence", bus.get("stale_sequence_dropped"))
    _true(errors, "bus epoch clear", bus.get("epoch_advance_clears_queue"))
    invalid = controls["invalid_vs_nonspeech"]
    _eq(errors, "invalid known", invalid.get("known_events"), 2)
    _eq(errors, "invalid invalid", invalid.get("invalid_events"), 1)
    _eq(errors, "invalid missing", invalid.get("missing_events"), 1)
    _true(errors, "invalid denominator",
          invalid.get("denominator_excludes_invalid"))
    _true(errors, "threshold strata respond",
          controls["threshold_sensitivity"].get("strata_respond_to_threshold"))

    adverse = report["adverse_rejections"]
    _eq(errors, "adverse count", len(adverse), 73)
    _true(errors, "adverse flag", report.get("adverse_all_rejected"))
    present = set()
    for item in adverse:
        case_id = str(item.get("case_id"))
        before = item.get("state_digest_before")
        after = item.get("state_digest_after")
        if item.get("status") != "rejected":
            errors.append("adverse case not rejected: " + case_id)
        if (not isinstance(before, str) or len(before) != 64
                or not isinstance(after, str) or len(after) != 64):
            errors.append("adverse case lacks measured state digests: "
                          + case_id)
            continue
        measured = before == after
        if item.get("state_unchanged") is not measured:
            errors.append("adverse state_unchanged is not the measured result: "
                          + case_id)
        if not measured:
            errors.append("adverse rejection mutated state: " + case_id)
        present.add(item.get("case_id"))
    if not REQUIRED_ADVERSE <= present:
        errors.append("required adverse cases missing: "
                      + ", ".join(sorted(REQUIRED_ADVERSE - present)))

    external = report["external_artifacts"]
    _eq(errors, "external artifact status", external.get("status"), "blocked")
    _false(errors, "external artifact presence", external.get("any_present"))
    for key in ("source_present", "weights_present", "runtime_present",
                "adapter_present", "corpus_present"):
        _false(errors, "external artifact " + key, external.get(key))

    licensing = report["licensing"]
    if licensing.get("reported_upstream_license") is not None:
        errors.append("an upstream license is asserted")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    for key in ("license_text_staged", "attribution_notice_staged",
                "weights_terms_staged", "training_data_statement_staged",
                "corpus_rights_reviewed", "redistribution_reviewed",
                "product_use_reviewed"):
        _false(errors, "licensing claim " + key, licensing.get(key))

    caller = report["caller_asset"]
    _true(errors, "caller ownership", caller.get("asset_is_caller_owned"))
    _false(errors, "vendored asset", caller.get("asset_is_vendored"))
    _eq(errors, "caller status", caller.get("status"),
        "shape_only_not_qualified")
    _false(errors, "candidate asset validated",
           caller.get("real_candidate_asset_validated"))

    qualification = report["qualification"]
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    for key, value in qualification.items():
        if key == "status":
            continue
        _false(errors, "qualification promoted: " + key, value)

    blockers = report["exact_blockers"]
    _eq(errors, "exact blocker count", len(blockers), 8)
    _eq(errors, "exact blocker ids", [item.get("id") for item in blockers],
        ["EB-0" + str(index) for index in range(1, 9)])
    for item in blockers:
        _eq(errors, "blocker status " + str(item.get("id")),
            item.get("status"), "blocked")
        _false(errors, "blocker present " + str(item.get("id")),
               item.get("present"))
        if not item.get("requirement"):
            errors.append("blocker lacks requirement: " + str(item.get("id")))

    gates = report["release_gates"]
    _eq(errors, "release gate count", len(gates), 8)
    _eq(errors, "release gate ids", [gate.get("id") for gate in gates],
        ["RG-0" + str(index) for index in range(1, 9)])
    for gate in gates:
        _eq(errors, "gate status " + str(gate.get("id")), gate.get("status"),
            "blocked")
        if not gate.get("requirement"):
            errors.append("gate lacks requirement: " + str(gate.get("id")))

    for key, value in report["boundary"].items():
        _false(errors, "boundary claim " + key, value)
    scope = report["scope"]
    _eq(errors, "write scope", scope.get("write_scope"),
        "docs/task-evidence/crnn-vad/ only")
    for key, value in scope.items():
        if key != "write_scope":
            _false(errors, "scope claim " + key, value)
    _eq(errors, "repeat rounds", report["repeatability"].get("rounds"), 3)
    _true(errors, "repeat identity",
          report["repeatability"].get("byte_identical"))


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: "
                      + ", ".join(sorted(missing)))
        return
    _eq(errors, "contract schema", contract["schema_id"],
        reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract["task"], reference.TASK_ID)
    _eq(errors, "contract decision", contract["decision"], "DEFER")
    _eq(errors, "contract status", contract["status"], reference.STATUS)
    _eq(errors, "contract evidence", contract["evidence_status"], "incomplete")
    _eq(errors, "contract qualification", contract["qualification_status"],
        "not_qualified")
    _eq(errors, "contract profile", contract["profile"], "analysis")
    _eq(errors, "contract base", contract["base_commit"], reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract["branch"], reference.BRANCH)
    _eq(errors, "contract reviewer", contract["reviewer"], reference.REVIEWER)
    _eq(errors, "contract surrogate", contract["surrogate_model"],
        report.get("surrogate_model"))
    _eq(errors, "contract scorer", contract["scorer"], report.get("scorer"))
    _eq(errors, "contract candidate", contract["candidate"],
        report.get("candidate"))
    _eq(errors, "contract gates", contract["release_gates"],
        report.get("release_gates"))
    _eq(errors, "contract blockers", contract["exact_blockers"],
        report.get("exact_blockers"))
    if len(contract.get("invariants", [])) < 6:
        errors.append("contract invariants are too few")
    if "TASKS.json" in reference.canonical_text(contract.get("source_pins", {})):
        errors.append("contract pins the mutable full task board")
    if "TASKS.json" in reference.canonical_text(contract.get("boundary_pins", {})):
        errors.append("contract boundary-pins the mutable full task board")
    for path in contract.get("artifact_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("contract artifact-pins the mutable full task board")


def check_files(errors: List[str]) -> None:
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    unexpected = present - ALLOWED_FILES
    missing = ALLOWED_FILES - present
    if unexpected:
        errors.append("unexpected files: " + ", ".join(sorted(unexpected)))
    if missing:
        errors.append("missing files: " + ", ".join(sorted(missing)))
    expected_sidecar = (SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n").encode()
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if path.is_file() and path.read_bytes() != expected_sidecar:
            errors.append("bad SPDX sidecar: " + name)
    for name in ("README.md", "reference.py", "run.py", "test_reference.py",
                 "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing SPDX header: " + name)
    for path in HERE.glob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as error:
            errors.append("python syntax error: " + path.name + ": " + str(error))
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            for name in names:
                if name and name not in ALLOWED_IMPORTS:
                    errors.append("unexpected import in " + path.name + ": " + name)
    for name in ("report.json", "contract.json", "SOURCES.sha256"):
        if "/Users/" in (HERE / name).read_text(encoding="utf-8"):
            errors.append("absolute path leaked into " + name)


def check_readme(errors: List[str]) -> None:
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "not_qualified", "incomplete", "proposal",
                  "RG-01", "RG-08", "260", "3x", "SOURCES.sha256"):
        if token not in text:
            errors.append("README lacks required token: " + token)
    rows = re.findall(r"\| `source:([^`]+)` \| `([0-9a-f]{64})` \|", text)
    found_source = dict(rows)
    if found_source != reference.SOURCE_PINS:
        errors.append("README source digest table does not match pins")
    rows = re.findall(r"\| `sdk:([^`]+)` \| `([0-9a-f]{64})` \|", text)
    found_boundary = dict(rows)
    if found_boundary != reference.BOUNDARY_PINS:
        errors.append("README boundary digest table does not match pins")


def check_rounds(errors: List[str]) -> None:
    payloads = []
    for _ in range(3):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        payloads.append((text, digest,
                         reference.canonical_text(contract) + "\n"))
    if not payloads[0] == payloads[1] == payloads[2]:
        errors.append("three cold-start rounds are not byte-identical")
    if REPORT.is_file():
        if REPORT.read_text(encoding="utf-8") != payloads[0][0]:
            errors.append("committed report.json is stale")
        if CONTRACT.read_text(encoding="utf-8") != payloads[0][2]:
            errors.append("committed contract.json is stale")
        if SIDECAR.read_text(encoding="ascii") != payloads[0][1] + "\n":
            errors.append("committed report.json.sha256 is stale")


def check_git(errors: List[str]) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--check"],
            capture_output=True, text=True, check=False)
    except OSError as error:
        errors.append("git diff --check failed to run: " + str(error))
        return
    if result.stdout.strip() or result.returncode != 0:
        errors.append("git diff --check is not clean: "
                      + (result.stdout.strip() or result.stderr.strip()))


def main() -> int:
    errors: List[str] = []
    parsed = check_json_files(errors)
    report = parsed["report"]
    contract = parsed["contract"]
    count = check_pins(errors)
    check_artifact_pins(errors, report, contract)
    check_board(errors, report, contract)
    check_report(errors, report)
    check_contract(errors, contract, report)
    check_files(errors)
    check_readme(errors)
    check_rounds(errors)
    check_git(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        print(f"verify_failed={len(errors)}", file=sys.stderr)
        return 1
    print(f"verify_ok=1 pins={count} "
          f"report_sha256={reference.file_digest(REPORT)} "
          f"decision=DEFER qualification=not_qualified "
          f"gates_blocked=8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
