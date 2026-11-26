# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the task-local SDK-MADMOM package.

The original directory is never written. Regeneration is performed in three
independent scratch trees with fresh interpreter processes and symlinks to the
pinned, read-only source and boundary files.

Scope verification compares the branch against the newest merge-base between
``HEAD`` and ``origin/main`` (falling back to ``main``), so later sibling
merges on ``main`` do not count as this branch's out-of-scope edits. A missing
base ref fails closed as ``scope_base_unavailable``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
VERIFICATION = (reference.AUDIO_ROOT
                / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
# The contiguous tag is assembled from adjacent literals so no Python string
# literal contains the raw token that REUSE scans for.
SPDX_LICENSE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".h5", ".mat", ".model",
    ".mp3", ".npy", ".npz", ".o", ".ogg", ".onnx", ".pkl", ".pt", ".pth",
    ".pyc", ".so", ".wasm", ".wav", ".weights",
}
PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility "
    "and playback buffering.",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window.",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation.",
)
EXPECTED_CHECK_IDS = (
    "identity_1x_bpm", "rate_0_8_bpm", "rate_1_2_bpm", "rate_duration_error",
    "meter_stable_1x", "meter_beats_1x", "downbeat_count_1x",
    "downbeat_phase_zero", "meter_stable_0_8", "speech_no_stable_tempo",
    "speech_meter_not_stable", "silence_no_onsets", "music_stable",
    "tempo_out_of_range", "low_snr_nonqualifying",
    "rebuffer_gap_suppressed", "rebuffer_stable", "rebuffer_bpm",
    "drift_recorded", "drift_nonqualifying", "final_partial_valid",
    "final_partial_event_within", "mapping_nonnegative", "mapping_exact",
    "transient_proxy", "all_cases_explicit", "eight_blocked_gates",
    "all_gates_blocked", "candidate_not_qualified", "no_source_or_runtime",
    "noncommercial_model_blocker_present",
)
EXPECTED_CHECK_COUNT = 31
REQUIRED_ADVERSE_IDS = {
    "MISS-01", "INV-01", "INV-02", "INV-03", "INV-04", "INV-05", "INV-06",
    "INV-07", "INV-08", "INV-09", "INV-10", "CFG-01", "CFG-02", "CFG-03",
    "CFG-04", "CFG-05", "ADV-low_snr_adverse",
    "ADV-tempo_out_of_range_adverse", "ADV-speech_like_unfamiliar",
    "ADV-silence", "ADV-drift", "ADV-rebuffer", "ADV-final_partial",
}
GATE_IDS = (
    "exact_source_and_asset_identity",
    "runtime_admission",
    "artifact_rights_and_licence",
    "exact_reference_parity",
    "beat_cohort_and_scoring",
    "task_scope_and_geometry",
    "opt_in_provider_intake",
    "public_default_and_release",
)
BLOCKER_IDS = (
    "source_checkout_absent",
    "upstream_revision_unpinned",
    "pretrained_model_rights_noncommercial",
    "inference_models_and_config_absent",
    "task_geometry_and_streaming_unestablished",
    "runtime_absent",
    "source_license_unverified",
    "parity_cohort_and_benchmark_absent",
)


def strict_json(path: Path) -> dict:
    return reference.read_strict_json(path)


def check_profile_source(errors: list[str]) -> None:
    expected = reference.SOURCE_PINS.get(
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not VERIFICATION.is_file():
        errors.append("verification_source_missing")
        return
    if reference.sha256_file(VERIFICATION) != expected:
        errors.append("verification_source_unpinned")
    text = VERIFICATION.read_text(encoding="utf-8")
    rate_rows = [line for line in text.splitlines()
                 if line.startswith("| Rate |")]
    if len(rate_rows) != 1:
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in PROFILE_PHRASES:
        if phrase not in rate_rows[0]:
            errors.append("rate_profile_phrase_missing:" + phrase[:32])


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    expected: dict[str, str | None] = {}
    for relative, digest in sorted(reference.SOURCE_PINS.items()):
        expected["source:" + relative] = digest
    for relative, digest in sorted(reference.BOUNDARY_PINS.items()):
        expected[relative] = digest
    for name in run.LOCAL_PIN_FILES:
        expected[run.TASK_PREFIX + name] = None
    seen: set[str] = set()
    count = 0
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        parts = line.split("  ", 1)
        if (len(parts) != 2 or len(parts[0]) != 64
                or any(char not in "0123456789abcdef" for char in parts[0])):
            errors.append("malformed_pin:" + repr(line))
            continue
        digest, name = parts
        if name not in expected:
            errors.append("unexpected_pin:" + name)
            continue
        if name in seen:
            errors.append("duplicate_pin:" + name)
            continue
        seen.add(name)
        if expected[name] is not None and expected[name] != digest:
            errors.append("pinned_digest_mismatch:" + name)
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name.split(":", 1)[1]
        else:
            path = SDK_ROOT / name
        if not path.is_file():
            errors.append("pin_target_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + name)
    for name in sorted(set(expected) - seen):
        errors.append("pin_absent:" + name)
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("manifest_not_deterministically_generated")
    if b"plan/swarm/TASKS.json" in PINS.read_bytes():
        errors.append("mutable_board_full_file_pinned")
    return count


def check_contract(errors: list[str]) -> dict:
    try:
        contract = strict_json(CONTRACT)
        reference.validate_contract(contract)
    except (OSError, ValueError, TypeError) as error:
        errors.append("contract_invalid:" + str(error))
        return {}
    if CONTRACT.read_bytes() != reference.canonical_contract_bytes():
        errors.append("contract_not_regenerated_bytes")
    if contract["decision"] != "DEFER":
        errors.append("contract_decision_not_defer")
    if contract["status"] != "proposal_only_incomplete":
        errors.append("contract_status_not_proposal_incomplete")
    if contract["qualification"]["status"] != "not_qualified":
        errors.append("contract_not_qualified")
    if len(contract["gates"]) != 8 or len(contract["exact_blockers"]) != 8:
        errors.append("contract_gate_count_not_eight")
    if len(contract["artifact_requirements"]) != 10:
        errors.append("contract_artifact_count_not_ten")
    licensing = contract["licensing"]
    if (licensing["commercial_use_permitted"] is not False
            or licensing["commercial_grant_present"] is not False
            or licensing["model_license_text_present"] is not False
            or licensing["license_verified"] is not False):
        errors.append("contract_model_rights_overclaim")
    upstream = contract["upstream_identity"]
    if (upstream["reported_models_license"]
            != reference.UPSTREAM_REPORTED_MODELS_LICENSE
            or upstream["reported_commercial_use"] != "No with shipped models"
            or upstream["revision"] is not None):
        errors.append("contract_upstream_identity_wrong")
    return contract


def check_report(errors: list[str]) -> dict:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
        reference.validate_contract(contract)
        generated = reference.canonical_report_bytes(reference.build_report())
    except (OSError, ValueError, TypeError) as error:
        errors.append("report_build_failed:" + str(error))
        return {}
    payload = REPORT.read_bytes()
    if payload != generated:
        errors.append("report_not_regenerated_bytes")
    if payload != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != (
            f"{digest}  report.json\n".encode("ascii")):
        errors.append("report_digest_sidecar_stale")
    if report["contract_sha256"] != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    if (report["protocol"] != reference.PROTOCOL
            or report["schema_id"] != reference.REPORT_SCHEMA_ID
            or report["task"] != reference.TASK
            or report["title"] != reference.TITLE
            or report["component"] != reference.COMPONENT):
        errors.append("report_identity_mismatch")
    if report["verification_profile"] != reference.PROFILE:
        errors.append("rate_profile_not_applied")
    if report["status"] != reference.STATUS:
        errors.append("proposal_status_mismatch")
    if report["decision"] != "DEFER":
        errors.append("report_decision_not_defer")
    if report["evidence_status"] != "incomplete":
        errors.append("evidence_status_not_incomplete")
    if report["proposal_only"] is not True:
        errors.append("proposal_only_not_true")

    for key in ("exact_scope", "installed_v0", "licensing", "scope",
                "upstream_identity", "artifact_requirements", "board_row",
                "gates", "remaining_gates", "non_claims", "reproduction",
                "caller_asset_contract"):
        if report[key] != contract[key]:
            errors.append("contract_copy_mismatch:" + key)
    if report["blockers"] != contract["exact_blockers"]:
        errors.append("contract_copy_mismatch:blockers")
    if report["licensing"] != reference._licensing():
        errors.append("licensing_disposition_mismatch")
    if report["upstream_identity"] != reference._upstream_identity():
        errors.append("upstream_identity_disposition_mismatch")

    scope = report["exact_scope"]
    if scope["write_scope"] != reference.TASK_PREFIX + " only":
        errors.append("write_scope_mismatch")
    if scope["task_local_only"] is not True:
        errors.append("task_local_scope_mismatch")
    for key in reference._SCOPE_FALSE_FLAGS:
        if scope[key] is not False:
            errors.append("scope_claim_not_false:" + key)
    claim_scope = report["scope"]
    if claim_scope["task_local_only"] is not True:
        errors.append("claim_scope_not_task_local")
    for key, value in claim_scope.items():
        if key != "task_local_only" and value is not False:
            errors.append("claim_scope_overclaim:" + key)

    if report["installed_v0"] != reference._installed_v0():
        errors.append("installed_v0_mismatch")
    upstream = report["upstream_identity"]
    if (upstream["revision"] is not None
            or upstream["revision_pin_available"] is not False
            or upstream["license_verified"] is not False
            or upstream["license_file_present"] is not False
            or upstream["model_license_file_present"] is not False
            or upstream["task_geometry_status"] != "unestablished"
            or upstream["reported_geometry_asserted"] is not False
            or upstream["reported_sample_rate_hz"] is not None
            or upstream["reported_channels"] is not None):
        errors.append("upstream_identity_overclaim")
    if (upstream["reported_models_license"]
            != "CC BY-NC-SA 4.0 (models, source-reported)"):
        errors.append("model_license_provenance_wrong")
    if upstream["reported_commercial_use"] != "No with shipped models":
        errors.append("commercial_use_provenance_wrong")

    live = reference.task_row_identity()
    board = report["board_row"]
    if (board["stable_fields"] != live["stable_fields"]
            or board["stable_sha256"] != live["stable_sha256"]
            or board["stable_sha256"] != reference.STABLE_SHA256
            or board["whole_file_hashed"] is not False
            or board["excluded_mutable_fields"]
            != list(reference.MUTABLE_TASK_FIELDS)
            or board["claim"] != live["claim"]):
        errors.append("stable_task_row_identity_mismatch")
    if board["source"] != live["source"]:
        errors.append("task_row_source_mismatch")

    audit = reference.audit_assets()
    if report["absence_audit"] != audit:
        errors.append("absence_audit_mismatch")
    if audit["all_absence_probes_absent"] is not True:
        errors.append("candidate_asset_present")
    if audit["probe_count"] != len(reference.ABSENCE_PROBES):
        errors.append("absence_probe_count_mismatch")

    expected_source = {
        path: {"sha256": digest_value, "actual": digest_value,
               "verified": True}
        for path, digest_value in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest_value, "actual": digest_value,
               "verified": True}
        for path, digest_value in reference.BOUNDARY_PINS.items()}
    if report["source_pins"] != expected_source:
        errors.append("report_source_pins_mismatch")
    if report["boundary_pins"] != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    qualification = report["qualification"]
    try:
        reference._exact_keys(qualification, reference._QUALIFICATION_KEYS,
                              "report.qualification")
    except reference.Reject as error:
        errors.append("qualification_shape_invalid:" + str(error))
    if (qualification["status"] != "not_qualified"
            or qualification["candidate_qualified"] is not False
            or qualification["decision"] != "DEFER"
            or qualification["evidence_status"] != "incomplete"
            or qualification["blocked_gate_count"] != 8
            or qualification["blocked_gate_ids"] != list(GATE_IDS)
            or qualification["all_release_gates_blocked"] is not True
            or qualification["synthetic_profile_checks_passed"] is not True
            or qualification["no_missing_result_qualifies_candidate"] is not True
            or any(qualification[key] is not False for key in
                   ("release_results_present", "missing_result_promoted",
                    "real_source_or_runtime_used",
                    "listening_or_device_timing_claim"))):
        errors.append("qualification_not_blocked")

    gates = report["gates"]
    if (len(gates) != 8
            or tuple(gate["id"] for gate in gates) != GATE_IDS
            or any(gate["status"] != "blocked" for gate in gates)):
        errors.append("eight_release_gates_not_blocked")
    blockers = report["blockers"]
    if (len(blockers) != 8
            or tuple(row["id"] for row in blockers) != BLOCKER_IDS
            or any(row["status"] != "blocked"
                   or row["qualifies"] is not False
                   or not row["requirement"] for row in blockers)):
        errors.append("eight_exact_blockers_not_blocked")
    if any(row["id"] == "pretrained_model_rights_noncommercial"
           and (row["state"] != "restrictive"
                or "CC BY-NC-SA 4.0" not in row["requirement"]
                or "JKU" not in row["requirement"])
           for row in blockers):
        errors.append("noncommercial_model_blocker_weakened")

    scoring = report["profile_scoring"]
    if tuple(row["id"] for row in scoring["checks"]) != EXPECTED_CHECK_IDS:
        errors.append("profile_check_ids_mismatch")
    if len(scoring["checks"]) != EXPECTED_CHECK_COUNT:
        errors.append("profile_check_count_mismatch")
    if (scoring["passed"] is not True or scoring["failed_checks"]
            or any(row["passed"] is not True for row in scoring["checks"])):
        errors.append("profile_scoring_not_passed")
    if scoring["scope"] != "synthetic fixture only; not release qualification":
        errors.append("profile_scope_not_synthetic")

    rate = report["rate_profile"]
    if rate["identity_1x"] != {
            "stimulus": "music_like_1x", "bpm_x100": "10000"}:
        errors.append("identity_rate_wrong")
    if rate["rate_changes"] != [
            {"stimulus": "rate_0_8", "expected_bpm_x100": "8000",
             "observed_bpm_x100": "8000"},
            {"stimulus": "music_like_1x", "expected_bpm_x100": "10000",
             "observed_bpm_x100": "10000"},
            {"stimulus": "rate_1_2", "expected_bpm_x100": "12000",
             "observed_bpm_x100": "12000"}]:
        errors.append("rate_changes_wrong")
    if rate["duration"]["max_error_samples"] != 0 or any(
            row["error_samples"] != "0"
            for row in rate["duration"]["cases"].values()):
        errors.append("duration_mapping_not_exact")
    mapping = rate["source_output_mapping"]
    if (mapping["audio_output_produced"] is not False
            or mapping["analysis_event_source_anchor"] is not True
            or mapping["frame_hop_samples"] != "160"
            or mapping["available_ns_per_frame"] != "10000000"
            or mapping["min_availability_margin_ns"] != 10000000):
        errors.append("source_output_mapping_invalid")
    if (rate["pitch"]["status"] != "not_measurable_analysis_only"
            or rate["pitch"]["qualifies"] is not False):
        errors.append("pitch_not_left_unmeasured")
    if rate["transient_proxy"]["final_partial_error_samples"] != -30:
        errors.append("transient_proxy_wrong")
    buffering = rate["playback_buffering"]
    if (buffering["device_buffer_measured"] is not False
            or buffering["sdk_worker_count"] != "0"
            or buffering["sdk_queue_depth"] != "0"
            or buffering["analysis_frame_aggregation_samples"] != "160"
            or buffering["final_partial_valid_count"] != "37"
            or buffering["final_padding_zero_verified"] is not True):
        errors.append("playback_buffering_claim_invalid")
    if (rate["speech_unfamiliar"]["status"] == "stable"
            or rate["speech_unfamiliar"]["qualifies"] is not False):
        errors.append("unfamiliar_speech_promoted")
    if (rate["speech_preservation"]["status"] != "not_measured"
            or rate["speech_preservation"]["qualifies"] is not False):
        errors.append("speech_preservation_promoted")
    if (rate["music"]["status"] != "stable"
            or rate["music"]["bpm_x100"] != "10000"
            or rate["silence"]["status"] != "no_onsets"):
        errors.append("music_or_silence_wrong")
    meter = rate["meter"]
    if (meter["status"] != "stable_meter"
            or meter["meter_beats"] != "4"
            or meter["downbeat_count"] != "3"
            or meter["downbeat_phase_onset_frame"] != "0"
            or meter["accent_period_onsets"] != ["4", "4"]):
        errors.append("meter_surrogate_wrong")
    if (rate["rebuffer"]["excluded_ioi_count"] != "1"
            or rate["rebuffer"]["cross_gap_ioi_suppressed"] is not True
            or rate["rebuffer"]["status"] != "stable"
            or rate["rebuffer"]["bpm_x100"] != "10000"):
        errors.append("rebuffer_gap_not_suppressed")
    if (rate["drift"]["monotonic_ioi_decrease"] is not True
            or rate["drift"]["status"] == "stable"):
        errors.append("drift_not_recorded")
    final = rate["final_partial_window"]
    if (final["valid_count"] != "37"
            or final["event_source_end"] != "96037"
            or final["event_beyond_source_end"] is not False
            or len(final["event_digest"]) != 64):
        errors.append("final_partial_window_invalid")
    if rate["low_snr_adverse"]["qualifies"] is not False:
        errors.append("low_snr_adverse_promoted")

    try:
        adverse = reference._adverse_cases()
    except (ValueError, TypeError) as error:
        errors.append("adverse_cases_not_reproduced:" + str(error))
        adverse = []
    if adverse != report["adverse_cases"]:
        errors.append("adverse_cases_mismatch")
    ids = {case["id"] for case in report["adverse_cases"]}
    if not REQUIRED_ADVERSE_IDS <= ids:
        errors.append("adverse_ids_missing:"
                      + ",".join(sorted(REQUIRED_ADVERSE_IDS - ids)))
    for case in report["adverse_cases"]:
        if (case["qualifies"] is not False
                or case["status"] not in ("rejected", "recorded")):
            errors.append("adverse_case_qualifies:" + case["id"])
        if case["status"] == "rejected" and (
                case["state_unchanged"] is not True
                or case["onset_count"] != "0"
                or not case["code"]):
            errors.append("rejection_advanced_state:" + case["id"])

    synthetic = report["synthetic_reference"]
    if (synthetic["not_upstream_madmom"] is not True
            or synthetic["upstream_source_weights_or_runtime_present"]
            is not False
            or synthetic["real_audio_or_corpus_used"] is not False
            or synthetic["listening_or_device_timing_claim"] is not False
            or synthetic["network_used"] is not False):
        errors.append("synthetic_reference_overclaim")
    if report["licensing"]["license_verified"] is not False:
        errors.append("upstream_license_claimed_verified")
    if report["licensing"]["commercial_use_permitted"] is not False:
        errors.append("commercial_model_use_claimed")
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8")
                if (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = "SPDX-License-" 'Identifier = "Apache-2.0"'
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
        if path.is_file() and path.name.startswith("LICENSE"):
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
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
            for path in base_paths:
                if path not in changed:
                    changed.append(path)
        committed = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--check", base + "..HEAD"],
            capture_output=True, text=True)
        if committed.returncode != 0 or committed.stdout.strip():
            errors.append("committed_git_diff_check_failed:"
                          + committed.stdout.strip())
    allowed = {name for name in run.LOCAL_PIN_FILES}
    allowed.add("SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-MADMOM"
    target = sdk / "docs/task-evidence/madmom"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.SDK_ROOT / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = (
        REPORT.read_bytes() if REPORT.is_file() else b"",
        SIDECAR.read_bytes() if SIDECAR.is_file() else b"",
        CONTRACT.read_bytes() if CONTRACT.is_file() else b"",
        PINS.read_bytes() if PINS.is_file() else b"",
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-madmom-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "all"], cwd=target,
                capture_output=True, text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:"
                              + process.stderr.strip())
                continue
            generated = (
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "contract.json").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[0]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    check_contract(errors)
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
    print(f"PASS pins={pins} checks={len(report['profile_scoring']['checks'])} "
          f"cold_starts=3/3 byte_identical=true profile=Rate "
          f"status={report['status']} decision=DEFER "
          f"qualification={report['qualification']['status']} "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
