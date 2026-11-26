# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the task-local MLX/MPS/Core ML package.

The original directory is never written. Regeneration runs in three independent
scratch trees with fresh interpreter processes and symlinks to the pinned,
read-only source and boundary files.
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
# Concatenated so this Python literal never contains a contiguous SPDX token.
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
    ".mlmodel", ".mlpackage", ".mlmodelc", ".model", ".mp3", ".mp4", ".o",
    ".onnx", ".opus", ".pcap", ".pcapng", ".pt", ".pth", ".pyc",
    ".safetensors", ".so", ".wasm", ".wav", ".weights",
}
GATE_IDS = ("RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06", "RG-07",
            "RG-08")
ARTIFACT_IDS = tuple(row["id"] for row in reference.REQUIRED_ARTIFACTS)
BLOCKER_IDS = tuple(row["id"] for row in reference.EXACT_BLOCKERS)
TOOL_IDS = tuple(row["id"] for row in reference.TOOL_REQUIREMENTS)
BLOCKER_TOKENS = (
    "ml-explore/mlx", "PyTorch", "MPS backend", "Core ML", "40-hex",
    "SHA-256", "CPU parity", "availability", "device-timing", "malformed",
    "caller-owned", "license", "rights", "model", "concurrent",
)
SOURCE_ROOTS = ("adapters", "audio-benchmark-platform", "research",
                "realtime-audio-library")


def strict_json(path: Path) -> dict:
    return reference.read_strict_json(path)


def check_profile_source(errors: list[str]) -> None:
    try:
        source = reference.profile_source()
    except (OSError, ValueError) as error:
        errors.append("profile_source_failed:" + str(error))
        return
    if source["profile"] != "Tool" or source["key"] != "tool":
        errors.append("profile_source_not_tool")
    if not source["row"].startswith("| Tool |"):
        errors.append("profile_row_not_tool")


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
    if reference.BOARD_TASK_ROW in expected:
        errors.append("mutable_board_file_pinned")
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
        path = (reference.AUDIO_ROOT / name.split(":", 1)[1]
                if name.startswith("source:") else SDK_ROOT / name)
        if not path.is_file():
            errors.append("pin_target_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + name)
    for name in sorted(set(expected) - seen):
        errors.append("pin_absent:" + name)
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("manifest_not_deterministically_generated")
    return count


def _numbers(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from _numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from _numbers(item)
    else:
        yield value


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

    if report.get("task_id") != reference.TASK:
        errors.append("report_task_mismatch")
    if report.get("component_id") != reference.COMPONENT_ID:
        errors.append("report_component_mismatch")
    if report.get("contract_id") != reference.CONTRACT_ID:
        errors.append("report_contract_id_mismatch")
    if report.get("profile") != "tool":
        errors.append("tool_profile_not_applied")
    if report.get("mode") != "feasibility":
        errors.append("mode_mismatch")
    if report.get("status") != reference.STATUS:
        errors.append("status_mismatch")
    if report.get("evidence_status") != reference.EVIDENCE_STATUS:
        errors.append("evidence_status_mismatch")
    if report.get("decision") != "DEFER":
        errors.append("decision_not_defer")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification_status_mismatch")
    if report.get("proposal_only") is not True:
        errors.append("proposal_only_not_true")
    if report.get("incomplete") is not True:
        errors.append("incomplete_not_true")

    disposition = report.get("disposition", {})
    if (disposition.get("promotion") != "defer"
            or disposition.get("production_exposure") != "DEFER"
            or disposition.get("status") != "incomplete"
            or disposition.get("decision") != "DEFER"
            or disposition.get("qualification_status") != "not_qualified"
            or disposition.get("proposal_only") is not True
            or disposition.get("incomplete") is not True
            or disposition.get("not_qualified") is not True
            or disposition.get("defer_before") !=
            "opt_in_tool_or_provider_exposure"
            or any(disposition.get(key) is not False for key in
                   ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"))):
        errors.append("disposition_not_defer_incomplete")

    for key, value in report.get("boundary", {}).items():
        if key == "task_local_only":
            if value is not True:
                errors.append("boundary.task_local_only_not_true")
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
            or qualification.get("all_release_gates_blocked") is not True
            or qualification.get("not_qualified") is not True
            or qualification.get("admitted_runtime_count") != 0
            or qualification.get("required_runtime_count") != 3
            or qualification.get("qualifying_results") != 0
            or qualification.get("missing_result_qualifies") is not False
            or qualification.get("conditional_implementation_closed")
            is not False):
        errors.append("qualification_status_or_readiness")

    geometry = report.get("public_v0_geometry", {})
    if (geometry.get("sample_rate_hz") != 16000
            or geometry.get("channels") != 1
            or geometry.get("sample_format") != "f32"
            or geometry.get("frame_samples") != 160
            or geometry.get("preserved") is not True
            or geometry.get("sdk_callback_invoked") is not False):
        errors.append("public_geometry_changed")
    model = report.get("geometry", {})
    if (model.get("runtime_ids") != list(reference.RUNTIME_IDS)
            or model.get("runtime_count") != 3
            or model.get("separate_runtime_reporting_required") is not True
            or model.get("cpu_parity_required_per_runtime") is not True
            or model.get("availability_required_per_runtime") is not True
            or model.get("pooled_runtime_result_permitted") is not False
            or model.get("os_framework_observation_is_admission") is not False
            or any(model.get(key) is not False for key in (
                "runtime_identity_pinned", "model_present", "runtime_present",
                "executed", "version_pinned", "device_timing_measured",
                "workload_support_measured", "cpu_parity_measured",
                "installed_v0", "provider_registered"))):
        errors.append("accelerator_geometry_changed")
    if report.get("write_scope") != reference.WRITE_SCOPE:
        errors.append("write_scope_mismatch")
    if report.get("exact_scope", {}).get("task_local_evidence_only") is not True:
        errors.append("exact_scope_not_task_local")
    scope = report.get("exact_scope", {})
    if (scope.get("runtimes") != list(reference.RUNTIME_IDS)
            or scope.get("pooled_runtime_result_permitted") is not False
            or scope.get("os_framework_observation_is_admission") is not False
            or scope.get("provided_adapter_entry_point") is not False):
        errors.append("exact_scope_runtime_boundary")

    upstream = report.get("upstream_record", {})
    expected_upstream = {
        "evidence_path": "adapters/reuse-mlx/README.md",
        "adapter_protocol_version": 1,
        "adapter_identity": "nvidia-reuse-swift-mlx-cli-v1",
        "adapter_observed": True,
        "adapter_admitted": False,
        "runtime_pinned": False,
        "runtime_lock_sha256": None,
        "pinned_model_sha256": None,
        "model_present": False,
        "executed": False,
        "digest_asserted": False,
        "rights_cleared": False,
        "evidence_is_adjacent_adapter_only": True,
        "reproduced_here": False,
        "admitted_as_result": False,
    }
    for key, value in expected_upstream.items():
        if upstream.get(key) != value:
            errors.append("upstream_record_mismatch:" + key)

    runtime = report.get("runtime_probe", {})
    if runtime != reference.runtime_probe():
        errors.append("runtime_probe_mismatch")
    if (runtime.get("status") != "blocked_pinned_runtimes_absent"
            or runtime.get("required_runtime_count") != 3
            or runtime.get("admitted_runtime_count") != 0
            or runtime.get("any_runtime_admitted") is not False
            or runtime.get("imported_or_executed") is not False
            or runtime.get("device_timing_measured") is not False):
        errors.append("pinned_runtime_unexpectedly_present")
    accelerators = runtime.get("accelerators", [])
    if [row.get("runtime_id") for row in accelerators] != list(
            reference.RUNTIME_IDS):
        errors.append("runtime_ids_mismatch")
    for row in accelerators:
        if (row.get("status") != "blocked_exact_runtime_absent"
                or row.get("admitted") is not False
                or row.get("pinned_install_present") is not False
                or row.get("imported_or_executed") is not False
                or row.get("version_verified") is not False
                or row.get("lock_present") is not False
                or row.get("license_verified") is not False
                or row.get("device_timing_measured") is not False):
            errors.append("runtime_not_absent:" + str(row.get("runtime_id")))
    host = runtime.get("host_observation", {})
    if (host.get("observation_is_admission") is not False
            or host.get("metal_device_query_executed") is not False
            or host.get("device_timing_measured") is not False
            or host.get("network_used") is not False
            or host.get("coreml_toolchain_observation") not in (
                "observed_not_admitted", "not_observed")):
        errors.append("host_observation_invalid")

    probes = report.get("absence_evidence", {}).get("probes")
    if probes != reference.absence_probes():
        errors.append("absence_probes_mismatch")
    summary = report.get("absence_evidence", {}).get("summary", {})
    if (summary.get("admitted_count") != 0
            or summary.get("all_admitted_absent") is not True
            or summary.get("fixed_probe_list_only") is not True
            or summary.get("download_attempted") is not False
            or summary.get("recursive_workspace_walk") is not False
            or summary.get("runtime_imported_or_executed") is not False
            or summary.get("model_loaded") is not False):
        errors.append("absence_summary_invalid")

    artifacts = report.get("required_artifacts", [])
    if tuple(row.get("id") for row in artifacts) != ARTIFACT_IDS:
        errors.append("artifact_ids_mismatch")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True
                or row.get("sha256") is not None or not row.get("requirement")):
            errors.append("artifact_not_blocked:" + str(row.get("id")))

    blockers = report.get("exact_blockers", [])
    if tuple(row.get("id") for row in blockers) != BLOCKER_IDS:
        errors.append("blocker_ids_mismatch")
    artifact_ids = {row["id"] for row in artifacts}
    gate_ids = {row["id"] for row in reference.RELEASE_GATES}
    for row in blockers:
        if (row.get("status") != "open" or row.get("qualifies") is not False
                or row.get("artifact_id") not in artifact_ids
                or not row.get("linked_gates")
                or not set(row.get("linked_gates", [])) <= gate_ids
                or not row.get("required_action")):
            errors.append("blocker_not_open:" + str(row.get("id")))
    blocker_text = " ".join(row["statement"] + " " + row["required_action"]
                            for row in blockers)
    for token in BLOCKER_TOKENS:
        if token not in blocker_text:
            errors.append("blocker_token_missing:" + token)

    gates = report.get("gates", [])
    if tuple(row.get("id") for row in gates) != GATE_IDS:
        errors.append("gate_ids_mismatch")
    if len(gates) != 8:
        errors.append("gate_count_not_eight")
    for row in gates:
        if (row.get("status") != "blocked" or row.get("qualifies") is not False
                or not row.get("reopen_condition")
                or row.get("linked_row") != reference._gate_link()):
            errors.append("gate_not_blocked:" + str(row.get("id")))
    if report.get("remaining_gates") != list(GATE_IDS):
        errors.append("remaining_gates_mismatch")

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
    board_path = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
    if not board_path.is_file():
        errors.append("board_row_missing")
    else:
        try:
            projection = reference.board_row_projection(board_path)
        except (OSError, ValueError) as error:
            errors.append("board_row_unreadable:" + str(error))
        else:
            if projection != reference.board_row_projection():
                errors.append("board_row_identity_drift")

    profile = report.get("tool_profile", {})
    if (profile.get("profile") != "Tool"
            or profile.get("status") != "blocked"
            or profile.get("qualifies") is not False
            or tuple(row.get("id") for row in profile.get("rows", [])) !=
            TOOL_IDS
            or any(row.get("status") != "blocked"
                   for row in profile.get("rows", []))):
        errors.append("tool_profile_not_blocked")
    for key, value in profile.items():
        if key in ("profile", "rows", "status", "qualifies",
                   "cross_runtime_pooling_prohibited"):
            continue
        if value is not False:
            errors.append("tool_profile_result_claimed:" + key)
    if profile.get("cross_runtime_pooling_prohibited") is not True:
        errors.append("cross_runtime_pooling_not_prohibited")
    if report.get("prohibited_claims") != list(reference.NON_CLAIMS):
        errors.append("prohibited_claims_changed")

    historical = report.get("historical_evidence", {})
    if (historical.get("status") !=
            "sibling_coreml_ep_trial_rejected_no_qualifying_execution"
            or historical.get("qualifies") is not False
            or historical.get("no_values_inferred_from_adjacent_tasks")
            is not True
            or [row.get("id") for row in historical.get("entries", [])] !=
            ["HIST-01", "HIST-02", "HIST-03"]):
        errors.append("historical_evidence_not_labeled")
    for row in historical.get("entries", []):
        if (row.get("admitted_as_result") is not False
                or row.get("qualifies") is not False
                or row.get("paired_cpu_baseline") is not False):
            errors.append("historical_evidence_admitted:" + str(row.get("id")))
    coreml = historical.get("entries", [{}])[0]
    if (coreml.get("runtime") != "coreml"
            or coreml.get("single_stream_clean") is not True
            or coreml.get("eight_stream_clean") is not False
            or coreml.get("sixteen_stream_clean") is not False
            or coreml.get("concurrent_use_rejected") is not True
            or coreml.get("reproducible_library_build") is not False):
        errors.append("coreml_trial_label_mismatch")
    peers = report.get("peer_evidence", [])
    if peers != [dict(row) for row in reference.PEER_EVIDENCE]:
        errors.append("peer_evidence_mismatch")
    for row in peers:
        if (row.get("admitted_as_result") is not False
                or row.get("inherited_metrics") is not False):
            errors.append("peer_evidence_inherited:" + str(row.get("task")))

    admission = report.get("admission", {})
    cases = admission.get("cases", [])
    expected_cases = reference.admission_controls()
    if cases != expected_cases["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("controls") != expected_cases["controls"]:
        errors.append("admission_controls_mismatch")
    summary = admission.get("summary", {})
    if (summary.get("case_count") != len(cases)
            or summary.get("rejected_count") != len(cases) - 1
            or summary.get("accepted_schema_controls") != 1
            or summary.get("qualifying_results") != 0
            or summary.get("state_advanced_on_rejection") is not False
            or summary.get("accepted_control_qualifies") is not False
            or summary.get("all_adverse_cases_rejected") is not True
            or summary.get("runtime_invoked") is not False
            or summary.get("model_loaded") is not False
            or summary.get("audio_read") is not False
            or summary.get("device_timing_measured") is not False):
        errors.append("admission_summary_invalid")
    for case in cases:
        if (case.get("qualifies") is not False
                or not case.get("code")
                or not case.get("status")):
            errors.append("admission_case_not_fail_closed:" +
                          str(case.get("id")))
    codes = {case.get("code", "") for case in cases}
    for expected in ("nonfinite_json", "duplicate_json_key",
                     "accelerator_unavailable", "parity_not_exact",
                     "availability_not_measured", "rights_not_cleared",
                     "control_not_verified", "unsafe_path"):
        if expected not in codes:
            errors.append("admission_case_missing:" + expected)

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

    expected_contract_keys = (
        "disposition", "boundary", "scope", "public_v0_geometry",
        "exact_scope", "qualification", "upstream_record", "geometry",
        "required_artifacts", "exact_blockers", "profile_source",
        "historical_evidence", "rights_gap", "tool_profile",
        "tool_profile_requirements",
    )
    for key in expected_contract_keys:
        if report.get(key) != contract.get(key):
            errors.append("contract_copy_mismatch:" + key)
    if report.get("gates") != contract.get("release_gates"):
        errors.append("contract_copy_mismatch:release_gates")
    if report.get("prohibited_claims") != contract.get("non_claims"):
        errors.append("contract_copy_mismatch:non_claims")
    if contract.get("admission_contract") != \
            reference.admission_contract_block():
        errors.append("contract_admission_contract_mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")

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
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    reuse_token = "SPDX-License-" + 'Identifier = "Apache-2.0"'
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json",
                         "model.json"}:
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
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    workspace = scratch / "audioml"
    sdk = workspace / "worktrees/audio-sdk/SDK-MLX-MPS-CORE-ML-EXECUTION"
    target = sdk / "docs/task-evidence/mlx-mps-core-ml-execution"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in SOURCE_ROOTS:
        link = workspace / name
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
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-mlx-mps-coreml-cold-") as \
            temporary:
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
          f"artifacts={len(report['required_artifacts'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Tool "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
