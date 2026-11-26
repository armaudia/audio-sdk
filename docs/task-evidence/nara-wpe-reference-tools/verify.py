# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the task-local SDK-NARA-WPE-REFERENCE-TOOLS package.

Checks exact pins, strict JSON, canonical bytes, contract/report regeneration,
the report digest sidecar, README digest tables, disposition and gate status,
external-artifact absence, caller-manifest strictness, geometry control,
SPDX sidecars, task-local scope with the newest merge-base, whitespace and
three cold-start regenerations. Never writes and never hashes the mutable full
``plan/swarm/TASKS.json``.

Scope verification compares the branch against the newest merge-base between
``HEAD`` and ``origin/main`` (falling back to ``main``), so later sibling merges
on ``main`` do not count as this branch's out-of-scope edits. A missing base ref
fails closed as ``scope_base_unavailable``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
README = HERE / "README.md"
VERIFICATION = (
    reference.AUDIO_ROOT
    / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
SPDX_LICENSE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
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
    "Freeze render/reference or measured RIRs, channel/rate/hop, excitation, "
    "delay, movement, noise and reset schedule.",
    "Include echo-only, near-end-only, overlap and no-reference cases.",
    "Report echo attenuation, near-end damage, nonfinite failures and "
    "alignments, including delayed/missing render.",
    "A no-reference suppressor gets its own independent comparison.",
)

EXPECTED_PROFILE_CHECKS = (
    "source_absence_audited",
    "upstream_revision_not_fabricated",
    "upstream_license_not_fabricated",
    "upstream_geometry_not_asserted",
    "project_geometry_pinned",
    "matched_config_required",
    "caller_schema_accepts_structural_control",
    "caller_manifest_rejections_fail_closed",
    "pinned_admission_blocked",
    "identity_control_bit_exact",
    "frame_grid_half_open",
    "early_window_50ms_exact",
    "declared_latency_80ms_exact",
    "final_partial_37",
    "nonfinite_rejected",
    "config_mismatch_rejected",
    "no_real_audio",
    "no_listening_or_device_timing",
    "no_benchmark_or_release_claim",
    "no_downloads",
    "no_provider_or_default_change",
    "sibling_evidence_not_pooled",
    "room_profile_applied",
    "all_eight_gates_blocked",
    "candidate_not_qualified",
)
EXPECTED_ROOM_CHECKS = (
    "frozen_render_reference",
    "channel_rate_hop",
    "excitation",
    "delay",
    "movement",
    "noise",
    "reset_schedule",
    "echo_only",
    "near_end_only",
    "overlap",
    "no_reference",
    "echo_attenuation",
    "near_end_damage",
    "nonfinite_failures",
    "alignment",
    "delayed_or_missing_render",
    "no_reference_independent_comparison",
)


def _strict_json(path: Path) -> Dict[str, Any]:
    return reference.strict_loads(path.read_text(encoding="utf-8"))


def check_profile_source(errors: List[str]) -> None:
    expected = reference.SOURCE_PINS.get(
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not VERIFICATION.is_file():
        errors.append("verification_source_missing")
        return
    if reference.sha256_file(VERIFICATION) != expected:
        errors.append("verification_source_unpinned")
    text = VERIFICATION.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Room |")]
    if len(rows) != 1:
        errors.append("room_profile_row_not_unique")
        return
    for phrase in PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("room_profile_phrase_missing:" + phrase[:32])


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if len(pins) != len(expected):
        errors.append("incomplete_pin_manifest")
    seen = set()
    for digest, raw in pins:
        if raw.startswith("source:"):
            path = reference._resolve_source_path(raw.split(":", 1)[1])
        elif raw.startswith("sdk:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if raw in seen:
            errors.append("duplicate_pin:" + raw)
        seen.add(raw)
        if raw not in expected:
            errors.append("unexpected_pin:" + raw)
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if expected - seen:
        errors.append("pin_absent:" + ",".join(sorted(expected - seen)))
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("manifest_not_deterministically_generated")
    except (OSError, ValueError) as error:
        errors.append("manifest_generation_failed:" + str(error))
    if b"plan/swarm/TASKS.json" in PINS.read_bytes():
        errors.append("mutable_board_full_file_pinned")
    return len(pins)


def check_contract(errors: List[str]) -> Dict[str, Any]:
    try:
        contract = _strict_json(CONTRACT)
        reference.validate_contract(contract)
    except (OSError, ValueError, TypeError) as error:
        errors.append("contract_invalid:" + str(error))
        return {}
    try:
        generated = reference.canonical_contract_bytes()
    except (OSError, ValueError, TypeError) as error:
        errors.append("contract_build_failed:" + str(error))
        return contract
    if CONTRACT.read_bytes() != generated:
        errors.append("contract_not_regenerated_bytes")
    if contract["decision"] != "DEFER":
        errors.append("contract_decision_not_defer")
    if contract["status"] != reference.STATUS:
        errors.append("contract_status_wrong")
    if contract["qualification"]["status"] != "not_qualified":
        errors.append("contract_not_qualified")
    if contract["verification_profile"] != "Room":
        errors.append("room_profile_not_declared")
    if len(contract["gates"]) != 8 or len(contract["exact_blockers"]) != 8:
        errors.append("contract_gate_count_not_eight")
    if tuple(row["id"] for row in contract["gates"]) != reference.GATE_IDS:
        errors.append("contract_gate_ids_wrong")
    if tuple(row["id"] for row in contract["exact_blockers"]) != \
            reference.BLOCKER_IDS:
        errors.append("contract_blocker_ids_wrong")
    if any(row["status"] != "blocked" for row in contract["gates"]):
        errors.append("gate_not_blocked")
    if any(row["qualifies"] is not False
           for row in contract["exact_blockers"]):
        errors.append("blocker_qualifies")
    if contract["asset_audit"]["all_absence_probes_absent"] is not True:
        errors.append("contract_absence_not_audited")
    if contract["caller_asset_contract"]["all_rejections_fail_closed"] \
            is not True:
        errors.append("caller_contract_not_fail_closed")
    licensing = contract["licensing"]
    if (licensing["license_verified"] is not False
            or licensing["commercial_use_permitted"] is not None
            or licensing["source_license"] is not None):
        errors.append("contract_license_overclaim")
    upstream = contract["upstream_identity"]
    if (upstream["revision"] is not None
            or upstream["license"] is not None
            or upstream["revision_pin_available"] is not False
            or upstream["license_verified"] is not False
            or upstream["package_metadata_present"] is not False
            or upstream["task_geometry_status"] != "unestablished"):
        errors.append("contract_upstream_identity_overclaim")
    scope = contract["exact_scope"]
    if scope["write_scope"] != reference.TASK_PREFIX + " only":
        errors.append("contract_write_scope_wrong")
    if scope["task_local_only"] is not True:
        errors.append("contract_not_task_local")
    for key in reference.SCOPE_FALSE_FLAGS:
        if scope[key] is not False:
            errors.append("contract_scope_claim:" + key)
    return contract


def check_report(errors: List[str], contract: Dict[str, Any]) -> Dict[str, Any]:
    try:
        report = _strict_json(REPORT)
        reference.validate_report(report, contract)
    except (OSError, ValueError, TypeError) as error:
        errors.append("report_invalid:" + str(error))
        return {}
    try:
        generated = reference.canonical_report_bytes()
    except (OSError, ValueError, TypeError) as error:
        errors.append("report_build_failed:" + str(error))
        return report
    payload = REPORT.read_bytes()
    if payload != generated:
        errors.append("report_not_regenerated_bytes")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical_bytes")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != \
            f"{digest}  report.json\n".encode("ascii"):
        errors.append("report_digest_sidecar_stale")
    if contract and report["contract_sha256"] != reference.object_digest(
            contract):
        errors.append("contract_digest_mismatch")
    if report["contract_sha256"] != reference.object_digest(
            reference.build_contract()):
        errors.append("contract_regeneration_digest_mismatch")

    if (report["task"] != reference.TASK
            or report["title"] != reference.TITLE
            or report["component"] != reference.COMPONENT
            or report["schema_id"] != reference.REPORT_SCHEMA_ID):
        errors.append("report_identity_mismatch")
    if report["verification_profile"] != "Room":
        errors.append("room_profile_not_applied")
    if report["status"] != reference.STATUS:
        errors.append("report_status_wrong")
    if report["decision"] != "DEFER" or report["evidence_status"] != \
            "incomplete":
        errors.append("report_disposition_wrong")
    if report["proposal_only"] is not True:
        errors.append("proposal_only_not_true")
    for key in ("exact_scope", "installed_v0", "upstream_identity",
                "task_geometry", "geometry_control", "caller_asset_contract",
                "matched_evidence", "room_profile", "licensing", "gates",
                "remaining_gates", "non_claims", "reproduction",
                "profile_scoring", "qualification"):
        if report.get(key) != contract.get(key):
            errors.append("contract_copy_mismatch:" + key)
    if report["blockers"] != contract["exact_blockers"]:
        errors.append("contract_copy_mismatch:blockers")
    if report["absence_audit"] != contract["asset_audit"]:
        errors.append("contract_copy_mismatch:absence")

    board = report["board_row"]
    if (board["stable_fields"] != reference.BOARD_ROW_STABLE_FIELDS
            or board["stable_sha256"] != reference.BOARD_ROW_STABLE_SHA256
            or board["whole_file_hashed"] is not False
            or board["excluded_mutable_fields"] !=
            list(reference.MUTABLE_TASK_FIELDS)
            or board["claim"] != reference.BOARD_ROW_CLAIM):
        errors.append("stable_task_row_identity_mismatch")
    if reference.board_row_digest() != reference.BOARD_ROW_STABLE_SHA256:
        errors.append("stable_task_row_digest_drift")

    audit = reference.audit_assets()
    if report["absence_audit"] != audit:
        errors.append("absence_audit_mismatch")
    if audit["all_absence_probes_absent"] is not True:
        errors.append("candidate_asset_present")
    if audit["probe_count"] != len(reference.ABSENCE_PROBES):
        errors.append("absence_probe_count_mismatch")

    upstream = report["upstream_identity"]
    if (upstream["revision"] is not None
            or upstream["license"] is not None
            or upstream["license_verified"] is not False
            or upstream["revision_pin_available"] is not False
            or upstream["package_metadata_present"] is not False
            or upstream["reported_geometry_asserted"] is not False
            or upstream["reported_sample_rate_hz"] is not None
            or upstream["reported_channels"] is not None):
        errors.append("upstream_identity_overclaim")
    if upstream["task_geometry_status"] != "unestablished":
        errors.append("upstream_geometry_not_unestablished")

    geometry = report["task_geometry"]
    project = geometry["project_reference"]
    for key, expected in (
        ("sample_rate_hz", 16000), ("channels", 1), ("fft_size", 512),
        ("hop_size", 128), ("taps", 5), ("prediction_delay_frames", 8),
        ("iterations", 3), ("early_target_window_ms", 50),
        ("early_target_window_samples", 800),
        ("stft_lookahead_samples", 256),
        ("predictor_delay_samples", 1024),
        ("declared_algorithmic_latency_samples", 1280),
        ("declared_algorithmic_latency_ms", 80),
    ):
        if project[key] != expected:
            errors.append("project_geometry_wrong:" + key)
    if geometry["upstream_matched_geometry"]["status"] != "unestablished":
        errors.append("upstream_geometry_asserted")
    if geometry["matched_configuration"]["must_equal_project_reference"] \
            is not True:
        errors.append("matched_configuration_not_required")

    control = report["geometry_control"]
    if (control["kind"] != "synthetic_geometry_control_not_nara_wpe"
            or control["not_nara_wpe"] is not True
            or control["dereverberation_performed"] is not False
            or control["real_audio_used"] is not False
            or control["qualifies"] is not False):
        errors.append("geometry_control_overclaim")
    for key, expected in (
        ("source_samples", 64037), ("frame_hop_samples", 128),
        ("frame_count", 501), ("final_frame_source_valid", 37),
        ("early_target_window_samples", 800),
        ("stft_lookahead_samples", 256),
        ("predictor_delay_samples", 1024),
        ("declared_algorithmic_latency_samples", 1280),
        ("declared_algorithmic_latency_ms", 80),
        ("config_rejections", 20), ("nonfinite_rejections", 3),
    ):
        if control[key] != expected:
            errors.append("geometry_control_wrong:" + key)
    if (control["contiguous_half_open_intervals"] is not True
            or control["identity_bit_exact"] is not True
            or control["partial_tail_matches_prefix"] is not True
            or control["config_accepted"] is not True):
        errors.append("geometry_control_failed")

    caller = report["caller_asset_contract"]
    if (caller["accepted"] != 1
            or caller["accepted_is_synthetic_not_evidence"] is not True
            or caller["rejected"] != caller["rejected_total"]
            or caller["all_rejections_fail_closed"] is not True
            or caller["pinned_admission_status"] != "blocked"
            or caller["pinned_admission_reason"] != "upstream_source_absent"
            or caller["loaded"] is not False
            or caller["executed"] is not False
            or caller["imported"] is not False
            or caller["qualifies"] is not False):
        errors.append("caller_asset_contract_not_fail_closed")

    matched = report["matched_evidence"]
    if (matched["upstream_nara_wpe_outputs_present"] is not False
            or matched["project_wpe_functions_present"] is not True
            or matched["matched_comparison_status"] != "blocked"
            or matched["pooling_allowed"] is not False):
        errors.append("matched_evidence_overclaim")
    if len(matched["project_wpe_evidence"]) != 2:
        errors.append("sibling_evidence_count")

    room = report["room_profile"]
    if room["profile"] != "Room" or room["qualifies"] is not False:
        errors.append("room_profile_claim")
    if tuple(row["id"] for row in room["checks"]) != EXPECTED_ROOM_CHECKS:
        errors.append("room_profile_check_ids")
    if "delayed_or_missing_render" not in room["not_applicable"]:
        errors.append("missing_render_gap_not_disclosed")

    qualification = report["qualification"]
    if (qualification["status"] != "not_qualified"
            or qualification["candidate_qualified"] is not False
            or qualification["decision"] != "DEFER"
            or qualification["blocked_gate_count"] != 8
            or qualification["blocked_gate_ids"] != list(reference.GATE_IDS)
            or qualification["all_release_gates_blocked"] is not True
            or qualification["no_missing_result_qualifies_candidate"]
            is not True
            or any(qualification[key] is not False for key in
                   ("release_results_present", "missing_result_promoted",
                    "real_source_or_runtime_used",
                    "listening_or_device_timing_claim"))):
        errors.append("qualification_not_blocked")

    if report["profile_scoring"]["passed"] is not True:
        errors.append("profile_scoring_not_passed")
    if tuple(row["id"] for row in report["profile_scoring"]["checks"]) != \
            EXPECTED_PROFILE_CHECKS:
        errors.append("profile_check_ids")
    if report["profile_scoring"]["failed_checks"]:
        errors.append("profile_check_failed")
    if report["profile_scoring"]["scope"] != (
            "synthetic geometry control only; not release qualification"):
        errors.append("profile_scope_not_synthetic")

    expected_source = {
        path: {"sha256": digest, "verified": True}
        for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest, "verified": True}
        for path, digest in reference.BOUNDARY_PINS.items()}
    if report["source_pins"] != expected_source:
        errors.append("report_source_pins_mismatch")
    if report["boundary_pins"] != expected_boundary:
        errors.append("report_boundary_pins_mismatch")
    return report


def check_readme(errors: List[str]) -> int:
    try:
        text = README.read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    if text != reference.update_readme_artifact_table(text):
        errors.append("readme_artifact_table_stale")
    return sum(counts.values())


def check_strict_rejections(errors: List[str]) -> int:
    result = reference.strict_rejection_examples()
    for key, total in (("bad_json", "bad_json_total"),
                       ("bad_pins", "bad_pins_total"),
                       ("bad_readme", "bad_readme_total")):
        if result[key + "_rejected"] != result[total]:
            errors.append("strict_parser_accepted_bad_" + key)
    return (result["bad_json_rejected"] + result["bad_pins_rejected"] +
            result["bad_readme_rejected"])


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or \
            f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
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
    for name in sorted(reference.EXPECTED_DIR_FILES):
        if not (HERE / name).is_file():
            errors.append("expected_file_missing:" + name)


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: List[str] = []
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
    allowed = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-NARA-WPE-REFERENCE-TOOLS"
    target = sdk / reference.TASK_PREFIX
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


def check_cold_start_regeneration(errors: List[str]) -> List[str]:
    committed = (
        REPORT.read_bytes() if REPORT.is_file() else b"",
        SIDECAR.read_bytes() if SIDECAR.is_file() else b"",
        CONTRACT.read_bytes() if CONTRACT.is_file() else b"",
        PINS.read_bytes() if PINS.is_file() else b"",
        README.read_bytes() if README.is_file() else b"",
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: List[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-nara-wpe-cold-") as temporary:
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
                (target / "README.md").read_bytes(),
            )
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[0]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: List[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors, contract)
    readme_rows = check_readme(errors)
    rejections = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} readme_rows={readme_rows} "
              f"strict_rejections={rejections} cold_starts={len(digests)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates=8/8 blocked blockers=8/8 "
          f"profile=Room readme_rows={readme_rows} "
          f"strict_rejections={rejections} cold_starts=3/3 "
          f"byte_identical=true status={report['status']} decision=DEFER "
          f"qualification={report['qualification']['status']} "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
