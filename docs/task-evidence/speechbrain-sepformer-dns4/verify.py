# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-SPEECHBRAIN-SEPFORMER-DNS4 package.

Checks the Enhancement profile phrases, pins, absence evidence, runtime
absence, canonical report bytes and digest, eight blocked gates, seven open
blockers, the recorded-provenance arithmetic, the strict admission and envelope
rejection matrices, licensing/REUSE boundaries, task-local git scope and three
fresh byte-identical regenerations. It writes only to a temporary directory.
"""

from __future__ import annotations

import hashlib
import os
import platform
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
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".yaml", ".yml",
}


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("verifier_interpreter_mismatch:" + observed)


def check_profile_source(errors: list[str]) -> None:
    path = (reference.AUDIO_ROOT /
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        errors.append("enhancement_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Enhancement":
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


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    expected = run.sources_bytes()
    if PINS.read_bytes() != expected:
        errors.append("sources_manifest_drift")


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
    if report.get("profile") != "enhancement":
        errors.append("report_profile_not_enhancement")
    if report.get("decision") != "DEFER":
        errors.append("report_decision_not_defer")
    if report.get("status") != "incomplete":
        errors.append("report_status_not_incomplete")
    if report.get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if report.get("qualification_status") != "not_qualified":
        errors.append("report_qualification_not_not_qualified")
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    copies = (
        ("disposition", "disposition"),
        ("scope", "scope"),
        ("boundary", "boundary"),
        ("public_v0_geometry", "public_v0_geometry"),
        ("model_identity", "model_identity"),
        ("recorded_runtime", "recorded_runtime"),
        ("runtime_overlay", "runtime_overlay"),
        ("reference_execution_policy", "reference_execution_policy"),
        ("speechbrain_wheel_sha256", "speechbrain_wheel_sha256"),
        ("protocol", "protocol"),
        ("required_artifacts", "required_artifacts"),
        ("exact_blockers", "exact_blockers"),
        ("gates", "release_gates"),
        ("non_claims", "non_claims"),
        ("required_results", "required_results"),
        ("reopening_conditions", "reopening_conditions"),
        ("qualification", "qualification"),
    )
    for report_key, contract_key in copies:
        if report.get(report_key) != contract.get(contract_key):
            errors.append("contract_copy_mismatch:" + report_key)
    if report.get("enhancement_profile", {}).get("requirements") != \
            contract.get("enhancement_requirements"):
        errors.append("contract_copy_mismatch:enhancement_requirements")

    qualification = report.get("qualification", {})
    for key in ("not_qualified", "all_release_gates_blocked"):
        if qualification.get(key) is not True:
            errors.append("qualification_flag:" + key)
    for key in ("real_result_present", "runtime_present", "weights_present",
                "corpus_present", "outputs_present",
                "reproduced_inference_result", "enhancement_profile_result",
                "alignment_state_result", "timing_result", "listening_result",
                "benchmark_result", "release_claim", "missing_result_promoted"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag:" + key)

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-%02d" % index:
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
            errors.append("absent_artifact_has_digest:" +
                          str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 7:
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

    profile = report.get("enhancement_profile", {})
    rows = profile.get("requirements", [])
    if len(rows) != 8:
        errors.append("enhancement_row_count")
    for row in rows:
        if row.get("status") != "blocked" \
                or not row.get("reopen_condition"):
            errors.append("enhancement_row_invalid:" + str(row.get("id")))
    summary = profile.get("summary", {})
    if summary.get("requirement_count") != 8 \
            or summary.get("blocked_count") != 8 \
            or summary.get("measured_real_result_count") != 0 \
            or summary.get("profile_satisfied") is not False \
            or summary.get("values_inferred") is not False:
        errors.append("enhancement_summary_invalid")

    presence = report.get("source_presence", {})
    if presence.get("exact_source_runtime_weights_conjunction_present") \
            is not False:
        errors.append("source_presence_conjunction")
    for key in ("runtime_present", "weights_present", "corpus_present",
                "outputs_present", "runtime_imported", "weights_loaded",
                "model_executed", "audio_read", "network_used",
                "download_attempted"):
        if presence.get(key) is not False:
            errors.append("source_presence_used:" + key)
    for key in ("research_reports_present", "checkpoint_lock_present",
                "recorded_result_rows_present", "scorer_source_present"):
        if presence.get(key) is not True:
            errors.append("source_presence_missing:" + key)
    if presence != reference.source_presence():
        errors.append("source_presence_mismatch")

    readiness = report.get("runtime_readiness", {})
    if readiness.get("blocked") is not True \
            or readiness.get("importable") is not False \
            or readiness.get("module_spec_found") is not False \
            or readiness.get("interpreter_matches") is not True \
            or readiness.get("runtime_imported") is not False \
            or readiness.get("weights_loaded") is not False \
            or readiness.get("model_executed") is not False \
            or readiness.get("found_modules") != []:
        errors.append("runtime_readiness_flags")
    if readiness != reference.runtime_readiness():
        errors.append("runtime_readiness_mismatch")
    if readiness.get("exact_error") != \
            "ModuleNotFoundError: No module named 'torch'":
        errors.append("runtime_error_mismatch")

    provenance = report.get("recorded_provenance", {})
    if provenance != reference.recorded_provenance():
        errors.append("recorded_provenance_mismatch")
    if provenance.get("all_agree") is not True \
            or provenance.get("rtf_definition_consistent") is not True \
            or provenance.get("clean_rtf_definition_consistent") is not True \
            or provenance.get("clean_identity_stoi_consistent") is not True:
        errors.append("recorded_provenance_disagrees")
    if provenance.get("provenance_only") is not True \
            or provenance.get("reproduced_here") is not False \
            or provenance.get("used_for_evidence") is not False \
            or provenance.get("qualifies") is not False:
        errors.append("recorded_provenance_flags")
    for key in ("model_executed", "weights_loaded", "audio_read",
                "network_used"):
        if provenance.get(key) is not False:
            errors.append("recorded_provenance_used:" + key)
    if provenance.get("identity", {}).get("row_count") != 30 \
            or provenance.get("identity", {}).get("unique_output_hashes") != 30:
        errors.append("recorded_provenance_identity")

    historical = report.get("historical_execution", {})
    if historical != reference.historical_execution():
        errors.append("historical_execution_mismatch")
    if historical.get("provenance_only") is not True \
            or historical.get("reproduced_here") is not False \
            or historical.get("used_for_evidence") is not False \
            or historical.get("qualifies") is not False:
        errors.append("historical_flags")

    envelope = report.get("protocol_envelope", {})
    if envelope != reference.synthetic_envelope_probe():
        errors.append("protocol_envelope_mismatch")
    use = envelope.get("typical_api_use", {})
    if use.get("status") != "synthetic_pass" \
            or use.get("identity_exact") is not True \
            or use.get("replay_identical") is not True \
            or use.get("reset_replay_identical") is not True \
            or use.get("run_after_close_rejected") is not True \
            or use.get("timing_measured") is not False \
            or use.get("runtime_invoked") is not False \
            or use.get("qualifies") is not False:
        errors.append("envelope_use_invalid")
    if envelope.get("summary", {}).get("case_count") != 18 \
            or envelope.get("summary", {}).get("rejected_count") != 18 \
            or envelope.get("summary", {}).get("qualifying_results") != 0:
        errors.append("envelope_summary_invalid")
    variants = {row.get("variant"): row for row in envelope.get("variants", [])}
    if set(variants) != {"identity", "unit_peak"}:
        errors.append("envelope_variant_set")
    else:
        if variants["identity"].get("identity_exact") is not True:
            errors.append("envelope_identity_not_exact")
        if variants["unit_peak"].get("changed") is not True \
                or variants["unit_peak"].get("peak_within_unit") is not True \
                or variants["unit_peak"].get("length_preserving") is not True:
            errors.append("envelope_unit_peak_invalid")
    for case in envelope.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True \
                or case.get("calls_after_rejection") != 0 \
                or not case.get("code"):
            errors.append("envelope_case_invalid:" + str(case.get("id")))
    lifecycle = envelope.get("lifecycle", {})
    if lifecycle.get("status") != "rejected" \
            or lifecycle.get("code") != "enhancer_closed" \
            or lifecycle.get("qualifies") is not False:
        errors.append("envelope_lifecycle_invalid")

    admission = report.get("admission", {})
    expected_cases = reference.admission_cases()
    if admission.get("cases") != expected_cases:
        errors.append("admission_cases_mismatch")
    admission_summary = admission.get("summary", {})
    if admission_summary.get("case_count") != 95 \
            or admission_summary.get("rejected_count") != 95 \
            or admission_summary.get("accepted_schema_controls") != 1 \
            or admission_summary.get("qualifying_results") != 0:
        errors.append("admission_summary_invalid")
    if admission.get("control", {}).get("qualifies") is not False \
            or admission.get("control", {}).get("accepted") is not True \
            or admission.get("control", {}).get("label") != \
            "synthetic_schema_control_not_evidence":
        errors.append("admission_control_invalid")
    for key in ("state_advanced_on_rejection", "runtime_invoked",
                "weights_loaded", "model_executed", "audio_read",
                "network_used"):
        if admission_summary.get(key) is not False:
            errors.append("admission_" + key)
    for case in admission.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True \
                or not case.get("code"):
            errors.append("admission_case_not_rejected:" +
                          str(case.get("id")))

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != BOARD_ROW:
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.board_row_digest(BOARD_ROW):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only":
        errors.append("linked_gating")
    if identity.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if identity.get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")
    if identity.get("linked_rows") != reference.linked_rows():
        errors.append("linked_rows_mismatch")
    if identity.get("linked_rows_sha256") != \
            reference.linked_rows_digest():
        errors.append("linked_rows_digest")

    model = report.get("model_identity", {})
    if model.get("checkpoint_files") != reference.CHECKPOINT_FILES:
        errors.append("checkpoint_files_mismatch")
    if model.get("checkpoint_byte_counts_recorded") is not False:
        errors.append("checkpoint_byte_counts_claimed")
    if model.get("hub_reported_size_is_exact") is not False:
        errors.append("hub_size_claimed_exact")

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

    evidence = report.get("absence_evidence", {})
    if evidence.get("workspace_probes") != reference.absence_probes(
            reference.AUDIO_ROOT):
        errors.append("absence_workspace_mismatch")
    if evidence.get("worktree_probes") != \
            reference.worktree_absence_probes():
        errors.append("absence_worktree_mismatch")
    if evidence.get("home_probes") != reference.home_absence_probes():
        errors.append("absence_home_mismatch")
    absence = evidence.get("summary", {})
    if absence.get("probe_count") != 19 \
            or absence.get("workspace_probe_count") != 12 \
            or absence.get("worktree_probe_count") != 3 \
            or absence.get("home_probe_count") != 4 \
            or absence.get("present_count") != 0 \
            or absence.get("all_probes_absent") is not True:
        errors.append("absence_summary_invalid")
    for key in ("download_attempted", "network_used",
                "recursive_workspace_walk", "source_or_runtime_imported",
                "weights_loaded", "model_executed", "audio_read"):
        if absence.get(key) is not False:
            errors.append("absence_" + key)

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
                     "SDK-SPEECHBRAIN-SEPFORMER-DNS4")
    target = sdk / "docs/task-evidence/speechbrain-sepformer-dns4"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
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
            prefix="sdk-sepformer-dns4-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True, text=True,
                                     env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
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
    check_interpreter(errors)
    check_profile_source(errors)
    pins = check_pins(errors)
    check_sources_manifest(errors)
    report = check_report(errors)
    check_licensing(errors)
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
          f"enhancement_rows="
          f"{len(report['enhancement_profile']['requirements'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"envelope_cases={len(report['protocol_envelope']['cases'])} "
          f"absence_probes=19 cold_starts=3/3 byte_identical=true "
          f"profile=Enhancement status={report['status']} decision=DEFER "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
