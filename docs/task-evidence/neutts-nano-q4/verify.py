# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-NEUTTS-NANO-Q4 evidence package.

Checks the Voice profile phrases, source/boundary pins, absence evidence,
canonical report bytes and digest, eight blocked gates, licensing/REUSE
boundaries, task-local git scope and three fresh byte-identical regenerations.
It writes only to a temporary directory.
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
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".so", ".wasm", ".wav", ".weights",
}


def check_profile_source(errors: list[str]) -> None:
    path = (reference.AUDIO_ROOT /
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Voice |")]
    if len(rows) != 1:
        errors.append("voice_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Voice":
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
    if reference.BOARD_TASK_ROW in reference.SOURCE_PINS:
        errors.append("mutable_board_pinned")
    return checked


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))
        return {}
    if contract.get("decision") != "DEFER" \
            or contract.get("status") != "incomplete" \
            or contract.get("qualification_status") != "not_qualified" \
            or contract.get("proposal_only") is not True:
        errors.append("contract_disposition")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")
    return contract


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}

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
    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key, source in (
                ("disposition", "disposition"),
                ("qualification", "qualification"),
                ("required_artifacts", "required_artifacts"),
                ("exact_blockers", "exact_blockers"),
                ("required_results", "required_results"),
                ("scope", "scope"),
                ("boundary", "boundary"),
                ("public_v0_geometry", "public_v0_geometry"),
                ("non_claims", "non_claims"),
                ("reproduction", "reproduction")):
            if report.get(key) != contract.get(source):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")
        if report.get("voice_profile", {}).get("rows") != \
                contract.get("voice_profile_requirements"):
            errors.append("contract_copy_mismatch:voice_profile")
        if report.get("quality_outcomes", {}).get("rows") != \
                contract.get("quality_outcomes"):
            errors.append("contract_copy_mismatch:quality_outcomes")
        if report.get("timing", {}).get("rows") != \
                contract.get("timing_requirements"):
            errors.append("contract_copy_mismatch:timing")
        if report.get("historical_execution") != \
                contract.get("historical_execution"):
            errors.append("contract_copy_mismatch:historical_execution")

    if report.get("source_presence") != reference.SOURCE_PRESENCE:
        errors.append("source_presence_mismatch")
    presence = report.get("source_presence", {})
    if presence.get("present") is not True or presence.get("verified") is not True:
        errors.append("source_presence_not_verified")
    if presence.get("admitted") is not False \
            or presence.get("model_executed") is not False \
            or presence.get("weights_used") is not False:
        errors.append("source_presence_used")
    if presence.get("exact_source_weights_runtime_conjunction_present") is not False:
        errors.append("source_presence_conjunction")

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
        if gate.get("linked_row") != reference.BOARD_ROW_PROJECTION:
            errors.append("gate_linked_row:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 6:
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
    if len(blockers) != 5:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))

    voice_rows = report.get("voice_profile", {}).get("rows", [])
    if len(voice_rows) != 8:
        errors.append("voice_row_count")
    for row in voice_rows:
        if row.get("status") != "blocked":
            errors.append("voice_row_not_blocked:" + str(row.get("id")))
    quality_rows = report.get("quality_outcomes", {}).get("rows", [])
    if len(quality_rows) != 3:
        errors.append("quality_row_count")
    for row in quality_rows:
        if row.get("status") != "blocked" or row.get("value") is not None:
            errors.append("quality_row_not_blocked:" + str(row.get("id")))
    timing_rows = report.get("timing", {}).get("rows", [])
    if len(timing_rows) != 3:
        errors.append("timing_row_count")
    for row in timing_rows:
        if row.get("status") != "blocked" or row.get("value") is not None:
            errors.append("timing_row_not_blocked:" + str(row.get("id")))

    evidence = report.get("absence_evidence", {})
    summary = evidence.get("summary", {})
    expected_workspace = len(reference.ABSENCE_PROBES)
    expected_home = len(reference.HOME_ABSENCE_PROBES)
    if summary.get("probe_count") != expected_workspace + expected_home:
        errors.append("absence_probe_count")
    if summary.get("workspace_probe_count") != expected_workspace:
        errors.append("absence_workspace_probe_count")
    if summary.get("home_probe_count") != expected_home:
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

    cache = evidence.get("observed_hf_cache", {})
    if cache.get("weights_present") is not False \
            or cache.get("blobs_present") is not False \
            or cache.get("snapshots_present") is not False \
            or cache.get("admitted") is not False:
        errors.append("hf_cache_weights_present")
    media = evidence.get("repository_bundled_assets", {})
    if media.get("admitted") is not False \
            or media.get("used_for_evidence") is not False \
            or media.get("audio_read") is not False \
            or media.get("decoded") is not False \
            or media.get("signal_loaded") is not False:
        errors.append("repository_assets_used")
    if media.get("byte_hash_only") is not True:
        errors.append("repository_assets_not_hash_only")
    media_path = reference.AUDIO_ROOT / reference.SOURCE_ROOT / "output.wav"
    if media_path.is_file():
        actual = reference.sha256_file(media_path)
        if actual != media.get("output_audio_sha256"):
            errors.append("repository_output_hash_mismatch")
        if media_path.stat().st_size != media.get("output_audio_byte_count"):
            errors.append("repository_output_size_mismatch")
    else:
        errors.append("repository_output_missing")

    admission = report.get("admission", {})
    try:
        expected_admission = reference.admission_controls()
    except ValueError as error:
        errors.append("admission_rebuild:" + str(error))
        expected_admission = {}
    if expected_admission and admission != expected_admission:
        errors.append("admission_mismatch")
    admission_summary = admission.get("summary", {})
    if admission_summary.get("qualifying_results") != 0 \
            or admission_summary.get("accepted_schema_controls") != 1:
        errors.append("admission_summary_invalid")
    if admission_summary.get("rejected_count") != \
            admission_summary.get("case_count"):
        errors.append("admission_not_all_rejected")
    for key in ("state_advanced_on_rejection", "runtime_invoked", "audio_read",
                "weights_loaded", "model_executed", "network_used"):
        if admission_summary.get(key) is not False:
            errors.append("admission_" + key)
    if admission.get("control", {}).get("accepted") is not True \
            or admission.get("control", {}).get("qualifies") is not False:
        errors.append("admission_control")
    for case in admission.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True \
                or not case.get("code"):
            errors.append("admission_case_not_rejected:" + str(case.get("id")))

    execution = report.get("historical_execution", {})
    expected_flags = {
        "acquisition_succeeded": False,
        "inference_attempted": False,
        "output_present": False,
        "runtime_present": False,
        "seed_recorded": False,
        "streaming_chunks_present": False,
        "first_audio_latency_present": False,
        "identity_similarity_measured": False,
        "naturalness_measured": False,
        "manual_transcript_present": False,
        "device_timing_present": False,
        "not_rerun": True,
        "merged_task_evidence": False,
        "used_for_evidence": False,
        "qualifies": False,
    }
    for key, expected in expected_flags.items():
        if execution.get(key) is not expected:
            errors.append("historical_execution_flag:" + key)
    if execution.get("acquisition_http_status") != 401:
        errors.append("historical_execution_http_status")

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != reference.BOARD_ROW_PROJECTION:
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.board_row_digest(
            reference.BOARD_ROW_PROJECTION):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only":
        errors.append("linked_gating")
    if identity.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if identity.get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")
    if identity.get("linked_rows") != [dict(row)
                                        for row in reference.LINKED_ROWS]:
        errors.append("linked_rows_mismatch")
    if identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_digest")

    board = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
    if board.is_file():
        try:
            projection = reference.board_row_projection(board)
        except ValueError as error:
            errors.append("board_projection:" + str(error))
        else:
            if projection != reference.BOARD_ROW_PROJECTION:
                errors.append("board_projection_mismatch")
    else:
        errors.append("board_missing")

    required = report.get("required_results", {})
    for key, value in required.items():
        if key == "no_result_qualifies":
            if value is not True:
                errors.append("required_results_no_result_qualifies")
        elif value is not False:
            errors.append("required_results_present:" + key)

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
    if PINS.is_file():
        try:
            expected_pins = run.sources_bytes()
        except ValueError as error:
            errors.append("sources_rebuild:" + str(error))
        else:
            if PINS.read_bytes() != expected_pins:
                errors.append("sources_manifest_mismatch")
    else:
        errors.append("sources_manifest_missing")
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
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-NEUTTS-NANO-Q4"
    target = sdk / "docs/task-evidence/neutts-nano-q4"
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
    # The repository demo output is hashed by verification, not by the report.
    media = scratch / "audioml" / reference.SOURCE_ROOT / "output.wav"
    media.parent.mkdir(parents=True, exist_ok=True)
    media.symlink_to(reference.AUDIO_ROOT / reference.SOURCE_ROOT / "output.wav")
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
    with tempfile.TemporaryDirectory(prefix="sdk-neutts-nano-q4-cold-") as temporary:
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
    check_profile_source(errors)
    pins = check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors, contract)
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
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Voice "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
