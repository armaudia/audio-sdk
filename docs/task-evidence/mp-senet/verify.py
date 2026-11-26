# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-MP-SENET evidence package.

Checks the Enhancement profile phrases, source and boundary pins, README digest
tables, canonical report bytes and sidecar, seven blocked artifacts, six open
blockers, eight blocked gates, absence probes, asset-register absence,
fail-closed admission cases, licensing/REUSE boundaries, task-local git scope
via the newest merge-base, and three byte-identical cold-start regenerations.
It writes only to a temporary directory.
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
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
PROFILE_SOURCE = (reference.AUDIO_ROOT / reference.PROFILE_SOURCE_REL)

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


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("verifier_interpreter_mismatch:" + observed)


def check_profile_source(errors: list[str]) -> None:
    if not PROFILE_SOURCE.is_file():
        errors.append("profile_source_missing")
        return
    rows = [line for line in PROFILE_SOURCE.read_text(encoding="utf-8")
            .splitlines() if line.startswith("| Enhancement |")]
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
            if reference.sha256_file(path) != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    return checked


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    if PINS.read_bytes() != run.sources_bytes():
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

    expected_fields = {
        "schema_id": reference.REPORT_SCHEMA_ID,
        "task_id": reference.TASK,
        "task": reference.TASK,
        "component_id": reference.COMPONENT_ID,
        "title": reference.TASK_TITLE,
        "mode": reference.MODE,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "contract_id": reference.CONTRACT_ID,
        "profile": reference.PROFILE,
        "status": reference.STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "decision": reference.DECISION,
        "qualification_status": reference.QUALIFICATION_STATUS,
    }
    for key, value in expected_fields.items():
        if report.get(key) != value:
            errors.append("report_field:" + key)
    for key in ("proposal_only", "incomplete"):
        if report.get(key) is not True:
            errors.append("report_flag:" + key)
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    copies = (
        ("disposition", "disposition"),
        ("boundary", "boundary"),
        ("scope", "scope"),
        ("exact_scope", "exact_scope"),
        ("public_v0_geometry", "public_v0_geometry"),
        ("task_geometry", "task_geometry"),
        ("upstream_record", "upstream_record"),
        ("recorded_identity", "recorded_identity"),
        ("reported_metrics", "reported_metrics"),
        ("asset_registry", "asset_registry"),
        ("required_artifacts", "required_artifacts"),
        ("exact_blockers", "exact_blockers"),
        ("gates", "release_gates"),
        ("enhancement_profile", "enhancement_profile"),
        ("rights_gap", "rights_gap"),
        ("qualification", "qualification"),
    )
    for report_key, contract_key in copies:
        if report.get(report_key) != contract.get(contract_key):
            errors.append("contract_copy_mismatch:" + report_key)

    qualification = report.get("qualification", {})
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("qualification_flag:all_release_gates_blocked")
    if qualification.get("recorded_identity_only") is not False:
        errors.append("qualification_flag:recorded_identity_only")
    for key in (
            "real_result_present", "source_present", "exact_source_identity",
            "source_license_verified", "runtime_present", "runtime_pinned",
            "weights_present_locally", "weights_identity_verified",
            "asset_registry_entry_present", "rights_cleared_cohort",
            "offline_geometry_verified", "phase_aware_geometry_verified",
            "implementation_present",
            "reference_execution_result", "output_validity_result",
            "enhancement_profile_result", "listening_result",
            "device_timing_result", "benchmark_result", "release_claim",
            "missing_result_promoted", "peer_result_inherited"):
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
        if gate.get("linked_row") != reference.TASK:
            errors.append("gate_linked_row:" + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 7:
        errors.append("artifact_count")
    for artifact in artifacts:
        if artifact.get("present") is not False \
                or artifact.get("verified") is not False \
                or artifact.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if artifact.get("sha256") is not None \
                or artifact.get("revision") is not None \
                or artifact.get("bytes") is not None:
            errors.append("artifact_identity_invented:" +
                          str(artifact.get("id")))

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
        if not blocker.get("required_action") \
                or not blocker.get("reopen_condition"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("blocker_gate:" + str(blocker.get("id")))

    profile = report.get("enhancement_profile", {})
    rows = profile.get("requirement_rows", [])
    if len(rows) != len(reference.ENHANCEMENT_REQUIREMENTS):
        errors.append("enhancement_row_count")
    for row in rows:
        if row.get("status") not in ("blocked", "documented"):
            errors.append("enhancement_row_status:" + str(row.get("id")))
    summary = profile.get("row_summary", {})
    if summary.get("requirement_count") != len(rows) \
            or summary.get("real_result_count") != 0 \
            or summary.get("profile_satisfied") is not False:
        errors.append("enhancement_summary_invalid")
    if profile.get("profile_source_check") != reference.profile_row_check():
        errors.append("enhancement_profile_source_mismatch")
    if profile.get("paired_si_sdr_stoi") != \
            "blocked_no_rights_cleared_16khz_clean_references":
        errors.append("enhancement_paired_claim")

    geometry = report.get("task_geometry", {})
    if geometry.get("reported_channels") != 1 \
            or geometry.get("reported_sample_rate_hz") != 16000 \
            or geometry.get("reported_mode") != \
            "offline_whole_utterance_non_streaming" \
            or geometry.get("reported_phase_aware") is not True:
        errors.append("task_geometry_reported_mismatch")
    if geometry.get("reported_latency_setting_count") is not None \
            or geometry.get("reported_seed_count") is not None \
            or geometry.get("reported_checkpoint_count") is not None:
        errors.append("task_geometry_counts_invented")
    for key in ("frame_samples", "hop_samples", "chunk_samples",
                "stft_window_samples", "lookahead_samples",
                "state_reset_policy", "pacing_policy",
                "reported_latency_settings_ms"):
        if geometry.get(key) is not None:
            errors.append("task_geometry_invented:" + key)
    if geometry.get("exact_geometry_verified") is not False \
            or geometry.get("sdk_v0_adapter_mapping_present") is not False:
        errors.append("task_geometry_claim")

    upstream = report.get("upstream_record", {})
    if upstream.get("source_repository") != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_source_repository_mismatch")
    if upstream.get("model_repository") != reference.MODEL_REPOSITORY:
        errors.append("upstream_model_repository_mismatch")
    if upstream.get("model_revision") != reference.MODEL_REVISION:
        errors.append("upstream_model_revision_mismatch")
    if upstream.get("source_license_reported") != "MIT" \
            or upstream.get("source_license_status") != \
            "reported_mit_not_locally_verified":
        errors.append("upstream_license_status_mismatch")
    if upstream.get("source_immutable_revision") is not None \
            or upstream.get("source_revision_pin_available") is not False \
            or upstream.get("model_revision_locally_verified") is not False \
            or upstream.get("model_card_license_verified_locally") is not False:
        errors.append("upstream_identity_invented")
    if upstream.get("checkpoint_count_reported") is not None:
        errors.append("upstream_counts_invented")

    recorded = report.get("recorded_identity", {})
    if recorded.get("status") != \
            "no_checkpoint_identity_recorded_in_merged_evidence":
        errors.append("recorded_checkpoint_status_mismatch")
    if recorded.get("checkpoint_sha256") is not None \
            or recorded.get("checkpoint_bytes") is not None \
            or recorded.get("checkpoint_path") is not None:
        errors.append("recorded_checkpoint_identity_invented")
    if recorded.get("model_revision") != reference.MODEL_REVISION:
        errors.append("recorded_model_revision_mismatch")
    for key in ("locally_present", "locally_verified",
                "digest_verified_locally", "byte_count_verified_locally",
                "admitted_as_result", "qualifies"):
        if recorded.get(key) is not False:
            errors.append("recorded_identity_promoted:" + key)

    metrics = report.get("reported_metrics", {})
    if metrics.get("status") != "source_reported_not_measured_here":
        errors.append("reported_metrics_status_mismatch")
    if metrics.get("admitted_as_result") is not False \
            or metrics.get("qualifies") is not False:
        errors.append("reported_metrics_promoted")
    if metrics.get("pesq") != reference.REPORTED_PESQ \
            or metrics.get("stoi") is not None \
            or metrics.get("csig") is not None:
        errors.append("reported_metrics_value_mismatch")

    registry = report.get("asset_registry", {})
    if registry != reference.asset_registry():
        errors.append("asset_registry_mismatch")
    if registry.get("mp_entry_present") is not False \
            or registry.get("asset_identity_available_for_mp") is not False:
        errors.append("asset_registry_claim")

    evidence = report.get("absence_evidence", {})
    expected_absence = {
        "workspace_probes": reference.workspace_probes(),
        "worktree_probes": reference.worktree_probes(),
        "home_probes": reference.home_probes(),
    }
    for key, value in expected_absence.items():
        if evidence.get(key) != value:
            errors.append("absence_" + key + "_mismatch")
    absence = evidence.get("summary", {})
    expected_summary = reference.absence_summary()
    if absence != expected_summary:
        errors.append("absence_summary_mismatch")
    if absence.get("probe_count") != 24 \
            or absence.get("workspace_probe_count") != 15 \
            or absence.get("worktree_probe_count") != 5 \
            or absence.get("home_probe_count") != 4 \
            or absence.get("present_count") != 0 \
            or absence.get("all_probes_absent") is not True:
        errors.append("absence_summary_invalid")

    inputs = report.get("evidence_inputs", [])
    if inputs != reference.evidence_inputs():
        errors.append("evidence_inputs_mismatch")
    if len(inputs) != len(reference.EVIDENCE_INPUT_PATHS):
        errors.append("evidence_input_count_mismatch")
    for row in inputs:
        if row.get("sha256") != reference.SOURCE_PINS.get(row.get("path")):
            errors.append("evidence_input_pin_mismatch:" +
                          str(row.get("path")))
        if row.get("is_result") is not False:
            errors.append("evidence_input_promoted:" + str(row.get("path")))
    if not any(row.get("mentions_mp_senet") for row in inputs):
        errors.append("no_evidence_input_mentions_mp_senet")

    identity = report.get("linked_row_identity", {})
    if identity != reference.linked_identity_block():
        errors.append("linked_identity_mismatch")

    expected_source = reference.pin_rows(reference.SOURCE_PINS,
                                         reference.AUDIO_ROOT)
    expected_boundary = reference.pin_rows(reference.BOUNDARY_PINS,
                                           reference.WORKTREE)
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    admission = report.get("admission", {})
    expected_admission = reference.admission_controls()
    if admission.get("controls") != expected_admission["controls"]:
        errors.append("admission_contract_mismatch")
    if admission.get("cases") != expected_admission["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("summary") != expected_admission["summary"]:
        errors.append("admission_summary_mismatch")
    case_summary = admission.get("summary", {})
    if case_summary.get("accepted_schema_controls") != 1 \
            or case_summary.get("qualifying_results") != 0 \
            or case_summary.get("rejected_count") != \
            case_summary.get("case_count", 0) - 1:
        errors.append("admission_summary_invalid")
    for key in ("state_advanced_on_rejection", "runtime_invoked",
                "weights_loaded", "model_executed", "audio_read",
                "network_used"):
        if case_summary.get(key) is not False:
            errors.append("admission_" + key)
    for case in admission.get("cases", []):
        if case.get("qualifies") is not False:
            errors.append("admission_case_qualifies:" + str(case.get("id")))
        if case.get("status") == "rejected" \
                and (case.get("state_unchanged") is not True
                     or not case.get("code")):
            errors.append("admission_case_invalid:" + str(case.get("id")))

    if len(report.get("prohibited_claims", [])) != 8:
        errors.append("non_claim_count")
    if report.get("prohibited_claims") != reference.NON_CLAIMS:
        errors.append("non_claim_mismatch")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    try:
        reference.assert_no_float(report)
    except ValueError as error:
        errors.append("report_float:" + str(error))
    return report


def check_readme(errors: list[str]) -> int:
    if not (HERE / "README.md").is_file():
        errors.append("readme_missing")
        return 0
    text = (HERE / "README.md").read_text(encoding="utf-8")
    try:
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    if text != reference.update_readme_tables(text):
        errors.append("readme_tables_stale")
    return sum(counts.values())


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    for path in sorted(HERE.glob("*.json")) + sorted(HERE.glob("*.sha256")):
        if not (HERE / (path.name + ".license")).is_file():
            errors.append("missing_sidecar_for:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json",
                         "asset.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual != reference.EXPECTED_DIR_FILES:
        for name in sorted(actual - reference.EXPECTED_DIR_FILES):
            errors.append("unpinned_task_file:" + name)
        for name in sorted(reference.EXPECTED_DIR_FILES - actual):
            errors.append("expected_task_file_missing:" + name)
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode_cache_present")
    if [path.name for path in HERE.iterdir() if path.is_dir()]:
        errors.append("unexpected_subdirectory")


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
        if not path.startswith(reference.TASK_PREFIX):
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
    return changed


def check_tests(errors: list[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 30:
        errors.append("fewer_than_30_reference_tests:" + str(count))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    process = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if process.returncode != 0:
        errors.append("test_suite_failed:" +
                      (process.stderr.strip() or process.stdout.strip()))
    return count


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-MP-SENET"
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("research", "reports", "audio-benchmark-platform"):
        link = scratch / "audioml" / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / name)
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
        ((HERE / "README.md").read_bytes()
         if (HERE / "README.md").is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(
            prefix="sdk-mp-senet-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True,
                                     text=True, env=env, timeout=300)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "README.md").read_bytes(),
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
    readme_rows = check_readme(errors)
    check_licensing(errors)
    tests = check_tests(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} json_ok={bool(report)} "
              f"readme_rows={readme_rows} tests={tests} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"enhancement_rows="
          f"{len(report['enhancement_profile']['requirement_rows'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"readme_rows={readme_rows} tests={tests} "
          f"absence_probes={report['absence_evidence']['summary']['probe_count']} "
          f"cold_starts=3/3 byte_identical=true "
          f"profile={reference.PROFILE} status={reference.STATUS} "
          f"decision={reference.DECISION} report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
