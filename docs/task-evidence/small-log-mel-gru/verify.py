# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-SMALL-LOG-MEL-GRU package.

Checks the Rate profile phrases, source/boundary pins, absence evidence,
canonical report bytes and digest, eight blocked gates, eight required
artifacts, six blockers, the deterministic GRU parameter and log-mel geometry
references, the fail-closed admission boundary, licensing/REUSE boundaries,
task-local git scope and three fresh byte-identical regenerations. It writes
only to a temporary directory.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = reference.WORKTREE
BOARD_ROW = reference.board_row_projection(
    reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus", ".pcap",
    ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm",
    ".wav", ".weights",
}


def check_profile_source(errors: list[str]) -> None:
    path = (reference.AUDIO_ROOT
            / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    if len(rows) != 1:
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Rate":
        errors.append("profile_label_mismatch")


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in (
            (reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
            (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    return checked


def check_sources_manifest(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return 0
    expected: dict[str, Path] = {}
    for relative in reference.SOURCE_PINS:
        expected["source:" + relative] = reference.AUDIO_ROOT / relative
    for relative in reference.BOUNDARY_PINS:
        expected[relative] = reference.WORKTREE / relative
    for name in run.LOCAL_PIN_FILES:
        expected[reference.TASK_PREFIX + name] = HERE / name
    observed: dict[str, str] = {}
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            errors.append("sources_manifest_line:" + line)
            continue
        digest, name = parts
        if len(digest) != 64 or any(ch not in "0123456789abcdef"
                                     for ch in digest):
            errors.append("sources_manifest_digest:" + name)
        if name in observed:
            errors.append("sources_manifest_duplicate:" + name)
        observed[name] = digest
    for name in sorted(set(expected) - set(observed)):
        errors.append("sources_manifest_missing_row:" + name)
    for name in sorted(set(observed) - set(expected)):
        errors.append("sources_manifest_extra_row:" + name)
    if any("TASKS.json" in name for name in observed):
        errors.append("sources_manifest_pins_mutable_board")
    if reference.BOARD_TASK_ROW in observed:
        errors.append("sources_manifest_pins_board_row")
    for name, path in sorted(expected.items()):
        if not path.is_file():
            errors.append("sources_manifest_target_missing:" + name)
            continue
        if observed.get(name) != reference.sha256_file(path):
            errors.append("sources_manifest_mismatch:" + name)
    return len(observed)


def check_report(errors: list[str]) -> dict:
    if not CONTRACT.is_file() or not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}
    try:
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))

    if report.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report_schema_mismatch")
    if report.get("task") != reference.TASK:
        errors.append("report_task_mismatch")
    if report.get("component") != reference.COMPONENT_ID:
        errors.append("report_component_mismatch")
    if report.get("decision") != "DEFER":
        errors.append("report_decision_not_defer")
    if report.get("status") != "incomplete":
        errors.append("report_status_not_incomplete")
    if report.get("qualification_status") != "not_qualified":
        errors.append("report_qualification_not_not_qualified")
    if report.get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")
    if report.get("disposition") != contract.get("disposition"):
        errors.append("contract_copy_mismatch:disposition")
    if report.get("qualification") != contract.get("qualification"):
        errors.append("contract_copy_mismatch:qualification")
    if report.get("required_artifacts") != contract.get("required_artifacts"):
        errors.append("contract_copy_mismatch:required_artifacts")
    if report.get("exact_blockers") != contract.get("exact_blockers"):
        errors.append("contract_copy_mismatch:exact_blockers")
    if report.get("gates") != contract.get("release_gates"):
        errors.append("contract_copy_mismatch:release_gates")
    if report.get("rate_profile", {}).get("rows") != \
            contract.get("rate_profile_requirements"):
        errors.append("contract_copy_mismatch:rate_profile")
    if report.get("quality_outcomes", {}).get("rows") != \
            contract.get("quality_outcomes"):
        errors.append("contract_copy_mismatch:quality_outcomes")
    if report.get("timing", {}).get("rows") != \
            contract.get("timing_requirements"):
        errors.append("contract_copy_mismatch:timing")
    if report.get("scope") != contract.get("scope"):
        errors.append("contract_copy_mismatch:scope")
    if report.get("boundary") != contract.get("boundary"):
        errors.append("contract_copy_mismatch:boundary")
    if report.get("public_v0_geometry") != contract.get("public_v0_geometry"):
        errors.append("contract_copy_mismatch:public_v0_geometry")
    if report.get("non_claims") != contract.get("non_claims"):
        errors.append("contract_copy_mismatch:non_claims")
    if report.get("required_results") != contract.get("required_results"):
        errors.append("contract_copy_mismatch:required_results")
    if report.get("exact_model") != contract.get("exact_model"):
        errors.append("contract_copy_mismatch:exact_model")
    if report.get("checkpoint_provenance") != \
            contract.get("checkpoint_provenance"):
        errors.append("contract_copy_mismatch:checkpoint_provenance")
    if report.get("frontend_contract") != contract.get("frontend_contract"):
        errors.append("contract_copy_mismatch:frontend_contract")
    if report.get("runtime_recorded") != contract.get("runtime_recorded"):
        errors.append("contract_copy_mismatch:runtime_recorded")
    if report.get("training_recipe_recorded") != \
            contract.get("training_recipe_recorded"):
        errors.append("contract_copy_mismatch:training_recipe")

    qualification = report.get("qualification", {})
    for key in ("not_qualified", "all_release_gates_blocked",
                "last_fold_checkpoint_present"):
        if qualification.get(key) is not True:
            errors.append("qualification_flag:" + key)
    for key in ("weights_present", "checkpoint_present",
                "feature_cache_present", "runtime_present", "license_present",
                "real_result_present", "cv_result", "rate_profile_result",
                "device_timing_result", "listening_result",
                "benchmark_result", "release_claim", "missing_result_promoted"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag:" + key)
    if qualification.get("status") != "not_qualified" \
            or qualification.get("readiness") != "incomplete":
        errors.append("qualification_status_block")

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            errors.append("gate_id:" + str(index))
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(gate.get("id")))
        if gate.get("linked_row") != BOARD_ROW:
            errors.append("gate_linked_row:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 8:
        errors.append("artifact_count")
    elif not (artifacts[0].get("present") is True
              and artifacts[0].get("verified") is True
              and artifacts[0].get("blocked") is False):
        errors.append("source_artifact_not_present")
    for artifact in artifacts[1:]:
        if artifact.get("present") is not False \
                or artifact.get("verified") is not False \
                or artifact.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if artifact.get("sha256") is not None:
            errors.append("absent_artifact_has_digest:" + str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("blocker_gate:" + str(blocker.get("id")))

    rate_rows = report.get("rate_profile", {}).get("rows", [])
    if len(rate_rows) != 8:
        errors.append("rate_row_count")
    for row in rate_rows:
        if row.get("status") != "blocked":
            errors.append("rate_row_not_blocked:" + str(row.get("id")))
    quality_rows = report.get("quality_outcomes", {}).get("rows", [])
    if len(quality_rows) != 4:
        errors.append("quality_row_count")
    for row in quality_rows:
        if row.get("status") != "blocked" or row.get("value") is not None:
            errors.append("quality_row_not_blocked:" + str(row.get("id")))
    timing_rows = report.get("timing", {}).get("rows", [])
    if len(timing_rows) != 4:
        errors.append("timing_row_count")
    for row in timing_rows:
        if row.get("status") != "blocked" or row.get("value") is not None:
            errors.append("timing_row_not_blocked:" + str(row.get("id")))

    evidence = report.get("absence_evidence", {})
    summary = evidence.get("summary", {})
    if summary.get("probe_count") != 20:
        errors.append("absence_probe_count")
    if summary.get("workspace_probe_count") != 16:
        errors.append("absence_workspace_probe_count")
    if summary.get("home_probe_count") != 4:
        errors.append("absence_home_probe_count")
    if summary.get("present_count") != 0:
        errors.append("absence_present_count")
    if summary.get("all_probes_absent") is not True:
        errors.append("absence_all_probes_absent")
    for key in ("download_attempted", "network_used", "recursive_workspace_walk",
                "source_or_runtime_imported", "weights_loaded",
                "model_executed", "audio_read"):
        if summary.get(key) is not False:
            errors.append("absence_" + key)

    checkpoint = evidence.get("documented_checkpoint", {})
    if checkpoint.get("documented_in_report") is not True:
        errors.append("checkpoint_not_documented")
    if checkpoint.get("present") is not True:
        errors.append("last_fold_checkpoint_missing")
    if checkpoint.get("sha256") != reference.CHECKPOINT_SHA256:
        errors.append("last_fold_checkpoint_digest")
    if checkpoint.get("byte_count") != reference.CHECKPOINT_BYTE_COUNT:
        errors.append("last_fold_checkpoint_bytes")
    if checkpoint.get("contradiction") is not False:
        errors.append("checkpoint_contradiction")
    if checkpoint.get("all_five_fold_checkpoints_present") is not False:
        errors.append("checkpoint_fold_claim")
    if checkpoint.get("loaded") is not False \
            or checkpoint.get("decoded") is not False:
        errors.append("checkpoint_loaded_or_decoded")

    presence = report.get("source_presence", {})
    for key in ("fold_checkpoints_present", "feature_cache_present",
                "runtime_present", "license_files_present",
                "exact_source_weights_runtime_conjunction_present"):
        if presence.get(key) is not False:
            errors.append("source_presence_conjunction:" + key)
    for key in ("weights_used", "runtime_imported", "audio_read",
                "audio_decoded", "model_executed",
                "declared_recording_digest_verified_here"):
        if presence.get(key) is not False:
            errors.append("source_presence_used:" + key)
    for key in ("research_scripts_present", "recorded_results_present",
                "detailed_report_present", "cohort_manifest_present",
                "final_fold_checkpoint_present", "corpus_clip_files_present"):
        if presence.get(key) is not True:
            errors.append("source_presence_missing:" + key)
    if presence.get("cohort_meeting_count") != 1:
        errors.append("source_presence_meeting_count")
    if presence.get("cohort_window_count") != 210:
        errors.append("source_presence_window_count")
    if presence.get("corpus_clip_files_present_count") != 210:
        errors.append("source_presence_clip_count")

    documented = report.get("documented_provenance", {})
    if documented.get("provenance_only") is not True:
        errors.append("documented_not_provenance")
    for key in ("reproduced_here", "used_for_evidence", "qualifies"):
        if documented.get(key) is not False:
            errors.append("documented_flag:" + key)
    if documented.get("cv_recorded", {}).get("n") != 210:
        errors.append("documented_cohort_size")
    if documented.get("model_recorded", {}).get("parameter_count") != 6113:
        errors.append("documented_parameter_count")

    if report.get("recipe_provenance") != reference.recipe_provenance():
        errors.append("recipe_provenance_mismatch")
    recipe = report.get("recipe_provenance", {})
    if recipe.get("executed_here") is not False \
            or recipe.get("checkpoint_present") is not False \
            or recipe.get("last_fold_checkpoint_present") is not True \
            or recipe.get("last_fold_checkpoint_loaded") is not False \
            or recipe.get("pretrained_weights_used") is not False \
            or recipe.get("feature_cache_persisted") is not False \
            or recipe.get("runtime_pinned") is not False:
        errors.append("recipe_flags")

    if report.get("architecture_reference") != \
            reference.architecture_reference():
        errors.append("architecture_reference_mismatch")
    architecture = report.get("architecture_reference", {})
    if architecture.get("all_checks_pass") is not True:
        errors.append("architecture_checks")
    if architecture.get("computed_parameter_count") != 6113 \
            or architecture.get("recorded_parameter_count") != 6113 \
            or architecture.get("matches_recorded") is not True:
        errors.append("architecture_parameters")
    if architecture.get("executed_here") is not False \
            or architecture.get("weights_loaded") is not False:
        errors.append("architecture_flags")

    if report.get("frontend_reference") != reference.frontend_reference():
        errors.append("frontend_reference_mismatch")
    frontend = report.get("frontend_reference", {})
    if frontend.get("all_checks_pass") is not True:
        errors.append("frontend_checks")
    if frontend.get("executed_here") is not False \
            or frontend.get("is_feature_reproduction") is not False \
            or frontend.get("feature_cache_present") is not False \
            or frontend.get("frontend_runtime_pinned") is not False:
        errors.append("frontend_flags")
    geometry = frontend.get("geometry", {})
    if geometry.get("frames") != 401 \
            or geometry.get("fft_bins") != 201 \
            or geometry.get("values_per_window") != 9624 \
            or geometry.get("cohort_values") != 2021040:
        errors.append("frontend_geometry")

    predictions = report.get("recorded_prediction_reference", {})
    if predictions != reference.recorded_prediction_reference():
        errors.append("recorded_prediction_reference_mismatch")
    if predictions.get("recomputed_matches_recorded") is not True:
        errors.append("recorded_prediction_mismatch")
    if predictions.get("row_count") != 210 \
            or predictions.get("fold_counts") != [42, 42, 42, 42, 42] \
            or predictions.get("nonfinite_count") != 0:
        errors.append("recorded_prediction_counts")
    if predictions.get("provenance_only") is not True \
            or predictions.get("reproduced_here") is not False \
            or predictions.get("used_for_evidence") is not False \
            or predictions.get("qualifies") is not False:
        errors.append("recorded_prediction_flags")

    admission = report.get("admission", {})
    expected_cases = reference.admission_cases()
    if admission.get("cases") != expected_cases:
        errors.append("admission_cases_mismatch")
    admission_summary = admission.get("summary", {})
    if admission_summary.get("case_count") != len(expected_cases) \
            or admission_summary.get("rejected_count") != len(expected_cases) \
            or admission_summary.get("accepted_schema_controls") != 1 \
            or admission_summary.get("qualifying_results") != 0:
        errors.append("admission_summary_invalid")
    if admission.get("control") != reference.admission_control():
        errors.append("admission_control_mismatch")
    if admission.get("control", {}).get("qualifies") is not False \
            or admission.get("control", {}).get("accepted") is not True \
            or admission.get("control", {}).get(
                "synthetic_schema_control_not_evidence") is not True:
        errors.append("admission_control_invalid")
    for key in ("state_advanced_on_rejection", "runtime_invoked", "audio_read",
                "weights_loaded", "model_executed", "network_used"):
        if admission_summary.get(key) is not False:
            errors.append("admission_" + key)
    for case in admission.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True \
                or not case.get("code"):
            errors.append("admission_case_not_rejected:" + str(case.get("id")))

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != BOARD_ROW:
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.object_digest(BOARD_ROW):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only":
        errors.append("linked_gating")
    if identity.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if identity.get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")
    if identity.get("linked_rows") != reference.linked_rows():
        errors.append("linked_rows_mismatch")
    if identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_digest")

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
    if report.get("input_inventory_digest") != \
            reference.object_digest(reference.input_inventory()):
        errors.append("input_inventory_digest")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    try:
        reference._no_floats(report)
    except ValueError as error:
        errors.append("report_float:" + str(error))
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
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
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


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
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
        if not path.startswith(run.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base_diff = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--name-only",
         reference.BASE_COMMIT, "--", "."],
        capture_output=True, text=True)
    if base_diff.returncode != 0:
        errors.append("git_base_diff_failed:" + base_diff.stderr.strip())
    else:
        for path in base_diff.stdout.splitlines():
            if path and not path.startswith(run.TASK_PREFIX):
                errors.append("base_out_of_scope_change:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / ("audioml/worktrees/audio-sdk/"
                     "SDK-SMALL-LOG-MEL-GRU")
    target = sdk / "docs/task-evidence/small-log-mel-gru"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    clip_dir = (scratch / "audioml/research/tsm-followup-20261101/"
                "agent-neural/run/data")
    source_clip_dir = (reference.AUDIO_ROOT / "research/"
                       "tsm-followup-20261101/agent-neural/run/data")
    if source_clip_dir.is_dir() and not clip_dir.exists():
        clip_dir.symlink_to(source_clip_dir)
    board = scratch / "audioml" / reference.BOARD_TASK_ROW
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = (
        (CONTRACT.read_bytes() if CONTRACT.is_file() else b""),
        (REPORT.read_bytes() if REPORT.is_file() else b""),
        (SIDECAR.read_bytes() if SIDECAR.is_file() else b""),
        (PINS.read_bytes() if PINS.is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(
            prefix="sdk-small-log-mel-gru-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True, text=True,
                                     env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:"
                              + process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
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
    manifest_rows = check_sources_manifest(errors)
    report = check_report(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} manifest_rows={manifest_rows} "
              f"checks_ok={bool(report)} cold_starts={len(digests)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} manifest_rows={manifest_rows} "
          f"gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Rate "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
