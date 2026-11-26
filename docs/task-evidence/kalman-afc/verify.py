#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local Kalman AFC package.

The original directory is never written. Regeneration runs in three independent
scratch trees with fresh interpreter processes and symlinks to the pinned,
read-only source and boundary files. The branch scope gate resolves the newest
merge-base against an available PR base ref and fails closed as
``base_out_of_scope_change`` or ``scope_base_unavailable``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TASK_PREFIX = reference.TASK_PREFIX
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights",
}


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
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                  str(reference.SOURCE_ROOT))).resolve()


def strict_json(path: Path) -> dict:
    return reference.read_strict_json(path)


def _numbers(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from _numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from _numbers(item)
    else:
        yield value


def check_profile_source(errors: list[str]) -> None:
    try:
        source = reference.profile_source()
    except (OSError, ValueError) as error:
        errors.append("profile_source_failed:" + str(error))
        return
    if source["profile"] != "DSP" or source["key"] != "dsp":
        errors.append("profile_source_not_dsp")
    if not source["row"].startswith("| DSP |"):
        errors.append("profile_row_not_dsp")
    if source["plan_note"] != reference.PLAN_NOTE:
        errors.append("profile_plan_note_mismatch")


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    text = PINS.read_text(encoding="ascii")
    try:
        rows = reference.parse_pin_lines(text)
    except ValueError as error:
        errors.append(str(error))
        return 0
    expected = reference.allowed_pin_keys()
    seen: set[str] = set()
    count = 0
    for digest, label in rows:
        count += 1
        if label not in expected:
            errors.append("unexpected_pin:" + label)
            continue
        if label in seen:
            errors.append("duplicate_pin:" + label)
            continue
        seen.add(label)
        if label.startswith("source:"):
            path = SOURCE_ROOT / label[len("source:"):]
        elif label.startswith("sdk:"):
            path = SDK / label[len("sdk:"):]
        else:
            path = HERE / label[len(TASK_PREFIX):]
        if not path.is_file():
            errors.append("pin_target_missing:" + label)
            continue
        actual = reference.sha256_file(path)
        if actual != digest:
            errors.append("pinned_bytes_changed:" + label)
    for label in sorted(expected - seen):
        errors.append("pin_absent:" + label)
    if reference.BOARD_TASK_ROW in {label for _, label in rows}:
        errors.append("mutable_board_file_pinned")
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("manifest_not_deterministically_generated")
    return count


def check_report(errors: list[str]) -> dict:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + str(error))
        return {}
    try:
        reference.validate_contract(contract)
        if contract != reference.build_contract():
            errors.append("contract_not_recomputed")
        generated = reference.canonical_bytes(reference.build_report())
    except (OSError, ValueError, TypeError) as error:
        errors.append("reference_build_failed:" + str(error))
        return report
    payload = REPORT.read_bytes()
    if payload != generated:
        errors.append("report_not_regenerated_bytes")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical_bytes")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != (
            f"{digest}  report.json\n".encode("ascii")):
        errors.append("report_digest_sidecar_stale")
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    expected_identity = {
        "task_id": reference.TASK,
        "component_id": reference.COMPONENT_ID,
        "title": reference.TITLE,
        "repository": reference.REPOSITORY,
        "mode": "feasibility",
        "profile": "dsp",
        "verification_profile": "DSP",
        "status": reference.STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "decision": "DEFER",
        "defer_before": reference.DEFER_BEFORE,
        "qualification_status": "not_qualified",
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "worktree": reference.CLAIM_WORKTREE,
        "reviewer": reference.REVIEWER,
        "contract_id": reference.CONTRACT_ID,
        "write_scope": TASK_PREFIX,
        "format": reference.FORMAT,
        "plan_note": reference.PLAN_NOTE,
    }
    for key, value in expected_identity.items():
        if report.get(key) != value:
            errors.append("report_identity_mismatch:" + key)
    for key in ("proposal_only", "incomplete"):
        if report.get(key) is not True:
            errors.append("report_" + key + "_not_true")

    disposition = report.get("disposition", {})
    if (disposition.get("promotion") != "defer"
            or disposition.get("production_exposure") != "DEFER"
            or disposition.get("status") != "incomplete"
            or disposition.get("decision") != "DEFER"
            or disposition.get("qualification_status") != "not_qualified"
            or disposition.get("proposal_only") is not True
            or disposition.get("incomplete") is not True
            or disposition.get("not_qualified") is not True
            or disposition.get("defer_before") != "opt_in_adapter_exposure"
            or any(disposition.get(key) is not False for key in
                   ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"))):
        errors.append("disposition_not_defer_incomplete")

    for key, value in report.get("boundary", {}).items():
        if key in ("task_local_only", "installed_v0_unchanged"):
            if value is not True:
                errors.append("boundary." + key + "_not_true")
        elif value is not False:
            errors.append("boundary." + key + "_claim")
    for key, value in report.get("scope", {}).items():
        if key == "task_local_evidence_only":
            if value is not True:
                errors.append("scope.task_local_not_true")
        elif value is not False:
            errors.append("scope." + key + "_claim")

    qualification = report.get("qualification", {})
    if (qualification.get("status") != "not_qualified"
            or qualification.get("readiness") != "incomplete"
            or qualification.get("candidate_qualified") is not False
            or qualification.get("all_release_gates_blocked") is not True
            or qualification.get("blocked_gate_count") != 8
            or qualification.get("blocked_gate_ids") != list(reference.GATE_IDS)
            or not qualification.get("reason")):
        errors.append("qualification_status_or_readiness")
    for key, value in qualification.items():
        if key in ("status", "readiness", "blocked_gate_count",
                   "blocked_gate_ids", "reason"):
            continue
        expected = key in ("all_release_gates_blocked",
                           "no_missing_result_qualifies_candidate",
                           "not_qualified")
        if value is not expected:
            errors.append("qualification." + key)

    geometry = report.get("public_v0_geometry", {})
    if (geometry.get("sample_rate_hz") != 16000
            or geometry.get("channels") != 1
            or geometry.get("sample_format") != "f32"
            or geometry.get("frame_samples") != 160
            or geometry.get("preserved") is not True
            or geometry.get("sdk_callback_invoked") is not False):
        errors.append("public_geometry_changed")
    model = report.get("geometry", {})
    expected_geometry = {
        "task_kind": "acoustic_feedback_cancellation_with_reference",
        "candidate_family":
            "frequency_domain_kalman_feedback_path_estimation",
        "suppressed_quantity": "loudspeaker_to_microphone_feedback_path",
        "requires_playback_reference": True,
        "requires_synchronized_mic_and_reference": True,
        "stateful_recursive": True,
        "per_bin_covariance_update": True,
        "declared_fft_size": None,
        "declared_hop_samples": None,
        "declared_process_noise": None,
        "declared_measurement_noise": None,
        "declared_forgetting_factor": None,
        "declared_regularization": None,
        "declared_delay_alignment": None,
        "declared_reset_policy": None,
        "geometry_verified": False,
        "candidate_output_measured": False,
        "installed_v0": False,
        "provider_registered": False,
    }
    for key, value in expected_geometry.items():
        if model.get(key) != value:
            errors.append("model_geometry_changed:" + key)

    source = report.get("profile_source", {})
    if source != reference.profile_source():
        errors.append("profile_source_mismatch")
    if report.get("profile_mapping") != {
            "sweeps_steps_impulses_silence_clean_speech":
                "partial_synthetic_harness_characterisation_only",
            "task_specific_intelligibility_or_load_control":
                "blocked_no_permitted_cohort",
            "gain_and_frequency_response": "blocked_no_candidate_output",
            "attack_and_release": "blocked_no_candidate_output",
            "headroom_and_peaks": "blocked_no_candidate_output",
            "delay_and_content_mapping": "blocked_no_candidate_output",
            "numerical_behavior": "partial_local_harness_rejection_only",
            "state_transitions": "blocked_no_candidate_instance",
            "interacting_nonlinear_configurations":
                "blocked_no_candidate_instance",
            "candidate_output":
                "blocked_source_parameter_fixture_runtime_and_rights_absent",
            "fixed_margin_comparison":
                "blocked_no_candidate_output_and_no_measured_loop"}:
        errors.append("profile_mapping_changed")

    dsp_profile = report.get("dsp_profile", {})
    if (dsp_profile.get("name") != "dsp"
            or dsp_profile.get("profile") != "DSP"
            or dsp_profile.get("status") != "blocked"
            or dsp_profile.get("real_candidate_metrics") is not None
            or dsp_profile.get("satisfied_for_qualification") != []
            or dsp_profile.get("qualifies") is not False
            or tuple(row.get("id") for row in dsp_profile.get(
                "required_items", [])) != reference.DSP_ITEM_IDS):
        errors.append("dsp_profile_not_blocked")
    for row in dsp_profile.get("required_items", []):
        if (row.get("status") != "blocked"
                or row.get("qualification_effect") != "none"
                or row.get("satisfied_for_qualification") is not False):
            errors.append("dsp_requirement_not_blocked:" +
                          str(row.get("id")))
    for key, value in dsp_profile.items():
        if key in ("name", "profile", "status", "source_path", "plan_note",
                   "required_items", "satisfied_for_qualification",
                   "real_candidate_metrics", "qualifies"):
            continue
        if value is not False:
            errors.append("dsp_profile_result_claimed:" + key)

    requirement = report.get("task_requirement", {})
    expected_requirement = {
        "plan_note": reference.PLAN_NOTE,
        "required_comparison": "candidate gain-before-feedback and recovery "
                               "versus fixed margin at equal output gain",
        "fixed_margin_reference":
            "docs/task-evidence/fixed-feedback-gain-margin/report.json",
        "equal_output_gain_normalization_required": True,
        "gain_before_feedback_measured": False,
        "recovery_measured": False,
        "equal_output_gain_matched": False,
        "fixed_margin_comparison_run_here": False,
        "status": "blocked_no_candidate_and_no_measured_loop",
    }
    for key, value in expected_requirement.items():
        if requirement.get(key) != value:
            errors.append("task_requirement_changed:" + key)
    if not requirement.get("reason"):
        errors.append("task_requirement_reason_missing")

    probe_checks = {
        "source_probe": reference.source_probe,
        "parameter_probe": reference.parameter_probe,
        "checkpoint_probe": reference.checkpoint_probe,
        "fixture_probe": reference.fixture_probe,
        "runtime_probe": reference.runtime_probe,
        "rights_probe": reference.rights_probe,
    }
    for key, builder in probe_checks.items():
        if report.get(key) != builder():
            errors.append(key + "_mismatch")
        if not str(report.get(key, {}).get("status", "")).startswith("blocked"):
            errors.append(key + "_not_blocked")
    for key in ("source_probe", "parameter_probe", "checkpoint_probe",
                "fixture_probe", "runtime_probe"):
        if report.get(key, {}).get("present") not in (None, False):
            errors.append(key + "_unexpectedly_present")
    if report.get("source_probe", {}).get("executed") is not False:
        errors.append("source_executed")
    if report.get("checkpoint_probe", {}).get("admitted_model") is not None:
        errors.append("checkpoint_admitted")
    if report.get("fixture_probe", {}).get("read") is not False:
        errors.append("fixture_read")
    if report.get("runtime_probe", {}).get(
            "imported_or_executed") is not False:
        errors.append("runtime_imported")
    if report.get("rights_probe", {}).get("review") != "blocked":
        errors.append("rights_review_not_blocked")

    probes = report.get("absence_evidence", {}).get("probes")
    if probes != reference.absence_probes():
        errors.append("absence_probes_mismatch")
    summary = report.get("absence_evidence", {}).get("summary", {})
    if (summary.get("present_count") != 0
            or summary.get("all_probes_absent") is not True
            or summary.get("fixed_probe_list_only") is not True
            or summary.get("download_attempted") is not False
            or summary.get("recursive_workspace_walk") is not False
            or summary.get("source_or_runtime_imported") is not False):
        errors.append("absence_summary_invalid")

    artifacts = report.get("required_artifacts", [])
    if tuple(row.get("id") for row in artifacts) != reference.ARTIFACT_IDS:
        errors.append("artifact_ids_mismatch")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True
                or row.get("sha256") is not None or not row.get("requirement")):
            errors.append("artifact_not_blocked:" + str(row.get("id")))

    blockers = report.get("exact_blockers", [])
    if tuple(row.get("id") for row in blockers) != reference.BLOCKER_IDS:
        errors.append("blocker_ids_mismatch")
    artifact_ids = {row["id"] for row in artifacts}
    for row in blockers:
        if (row.get("status") != "open" or row.get("qualifies") is not False
                or row.get("artifact_id") not in artifact_ids
                or not row.get("required_action")):
            errors.append("blocker_not_open:" + str(row.get("id")))
    blocker_text = " ".join(row["statement"] + " " + row["required_action"]
                            for row in blockers)
    for token in reference.BLOCKER_TOKENS:
        if token not in blocker_text:
            errors.append("blocker_token_missing:" + token)

    gates = report.get("gates", [])
    if tuple(row.get("id") for row in gates) != reference.GATE_IDS:
        errors.append("gate_ids_mismatch")
    if len(gates) != 8:
        errors.append("gate_count_not_eight")
    for row in gates:
        if (row.get("status") != "blocked" or row.get("qualifies") is not False
                or not row.get("reopen_condition")
                or row.get("linked_row") != reference._gate_link()):
            errors.append("gate_not_blocked:" + str(row.get("id")))
    if report.get("remaining_gates") != list(reference.GATE_IDS):
        errors.append("remaining_gates_mismatch")

    historical = report.get("historical_evidence", {})
    if historical != reference.historical_pilot_match():
        errors.append("historical_evidence_mismatch")
    if (historical.get("kalman_afc_result_row_present") is not False
            or historical.get("matched_execution") is not False
            or historical.get("admitted_as_result") is not False
            or historical.get("inherited_metrics") is not False):
        errors.append("historical_evidence_inherited")

    identity = report.get("linked_row_identity", {})
    if (identity.get("projection") != reference.board_row_projection()
            or identity.get("sha256") != reference.board_row_digest(
                reference.board_row_projection())
            or identity.get("gating") != "stable_identity_only"
            or identity.get("board_file_pinned") is not False
            or identity.get("board_status_gates_anything") is not False
            or identity.get("linked_rows") != [
                dict(row) for row in reference.linked_rows()]
            or identity.get("linked_rows_sha256") !=
            reference.linked_rows_digest()):
        errors.append("linked_row_identity_invalid")
    row_identity = report.get("task_row_identity", {})
    if (row_identity.get("source") != reference.BOARD_TASK_ROW
            or row_identity.get("whole_file_hashed") is not False
            or row_identity.get("stable_fields") !=
            reference.board_row_projection()
            or row_identity.get("stable_sha256") !=
            reference.board_row_digest(reference.board_row_projection())):
        errors.append("task_row_identity_invalid")
    for text in (payload, reference.canonical_bytes(report)):
        if re.search(rb'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', text):
            errors.append("whole_file_board_digest_present")

    admission = report.get("admission", {})
    expected_admission = reference.admission_controls()
    if admission.get("cases") != expected_admission["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("controls") != expected_admission["controls"]:
        errors.append("admission_controls_mismatch")
    cases = admission.get("cases", [])
    if (len(cases) != 14
            or cases[0].get("accepted_by_schema") is not True
            or cases[0].get("admission") !=
            "deferred_required_artifacts_absent"):
        errors.append("admission_control_invalid")
    for case in cases:
        if case.get("qualifies") is not False or case.get("runtime_invoked") \
                is not False or case.get("audio_read") is not False:
            errors.append("admission_case_not_fail_closed:" +
                          str(case.get("id")))
    for code in ("invalid_json", "duplicate_json_key", "nonfinite_json",
                 "unsafe_path_revision", "invalid_parameter_geometry",
                 "invalid_parameter_type", "invalid_fixture_geometry",
                 "fixture_class_not_matched", "rights_not_cleared",
                 "unknown_field", "invalid_runtime", "invalid_comparison"):
        if not any(case.get("code") == code for case in cases):
            errors.append("admission_case_missing:" + code)

    strictness = report.get("strictness", {})
    if strictness != reference.strictness_controls():
        errors.append("strictness_mismatch")
    if (strictness.get("json_rejected") != strictness.get("json_cases")
            or strictness.get("pin_rejected") != strictness.get("pin_cases")
            or strictness.get("readme_rejected") !=
            strictness.get("readme_cases")
            or strictness.get("all_adverse_parsers_rejected") is not True):
        errors.append("strictness_not_fail_closed")

    stimulus = report.get("stimulus_probe", {})
    if stimulus != reference.stimulus_probe():
        errors.append("stimulus_probe_mismatch")
    if (stimulus.get("candidate_processing") is not False
            or stimulus.get("identity_control", {}).get("bit_exact")
            is not True
            or stimulus.get("fixed_margin_comparison", {}).get("status")
            != "blocked_no_candidate_output"):
        errors.append("stimulus_probe_claims_candidate")

    expected_source = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.BOUNDARY_PINS.items()}
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    if report.get("prohibited_claims") != list(reference.NON_CLAIMS):
        errors.append("prohibited_claims_changed")

    for value in _numbers(report):
        if isinstance(value, float):
            errors.append("report_contains_float")
            break
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse_path = SDK / "REUSE.toml"
    if not reuse_path.is_file():
        errors.append("reuse_toml_missing")
    else:
        reuse = reuse_path.read_text(encoding="utf-8")
        reuse_token = "SPDX-License-" + 'Identifier = "Apache-2.0"'
        if '"docs/**"' not in reuse or reuse_token not in reuse:
            errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


def check_readme(errors: list[str]) -> None:
    if not README.is_file():
        errors.append("README missing")
        return
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "BLK-01", "BLK-06", "DSP", "Kalman", "kalman-afc",
                  "gain-before-feedback", "fixed margin", "equal output gain",
                  "reopen", reference.BASE_COMMIT, reference.TASK):
        if token not in text:
            errors.append("README is missing token: " + token)
    try:
        reference.verify_readme_digests(text)
    except (OSError, ValueError) as error:
        errors.append("readme_digest_table_failed:" + str(error))


def check_sources_reproduction(errors: list[str]) -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("committed_artifacts_not_reproducible:" +
                      (result.stderr.strip() or result.stdout.strip()))


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    workspace = scratch / "audioml"
    sdk = workspace / "worktrees/audio-sdk/SDK-KALMAN-AFC"
    target = sdk / "docs/task-evidence/kalman-afc"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("audio-benchmark-platform", "research", "reports", "data"):
        source = SOURCE_ROOT / name
        if source.exists():
            link = workspace / name
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(source)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    names = ("contract.json", "report.json", "report.json.sha256",
             "SOURCES.sha256", "README.md")
    committed = tuple((HERE / name).read_bytes() for name in names)
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    root_parent = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    with tempfile.TemporaryDirectory(prefix="sdk-kalman-afc-cold-",
                                     dir=root_parent) as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py"],
                                     cwd=target, capture_output=True,
                                     text=True, env=environment)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = tuple((target / name).read_bytes() for name in names)
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    report = check_report(errors)
    check_licensing(errors)
    check_readme(errors)
    check_sources_reproduction(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} checks_ok={bool(report)} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"dsp_items={len(report['dsp_profile']['required_items'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=DSP "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
