# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the PodcastFillers package.

Checks profile phrases, source/boundary pins, absence evidence, canonical
report bytes and digest, eight blocked gates, seven required artifacts,
licensing/REUSE boundaries, task-local git scope and three fresh byte-identical
regenerations. It writes only to a temporary directory.
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
BOARD_ROW = reference.board_row_projection(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARDS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".joblib", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".zip", ".dict", ".TextGrid", ".csv",
}


def check_profile_source(errors: list[str]) -> None:
    path = reference.AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    if len(rows) != 1:
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in ("Measure source/output mapping, duration", "pitch, transient audibility",
                   "playback buffering", "1×, rate changes", "music, silence",
                   "rebuffer, drift", "final partial window", "source timestamps",
                   "speech preservation"):
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


def check_report(errors: list[str]) -> dict:
    if not CONTRACT.is_file() or not REPORT.is_file() or not SIDECAR.is_file() or not PINS.is_file():
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

    for field in ("disposition", "qualification", "required_artifacts", "exact_blockers",
                  "scope", "boundary", "public_v0_geometry", "non_claims", "required_results",
                  "exact_models", "historical_recipe"):
        if report.get(field) != contract.get(field):
            errors.append("contract_copy_mismatch:" + field)
    if report.get("gates") != contract.get("release_gates"):
        errors.append("contract_copy_mismatch:release_gates")
    if report.get("rate_profile", {}).get("rows") != contract.get("rate_profile_requirements"):
        errors.append("contract_copy_mismatch:rate_profile")
    if report.get("quality_outcomes", {}).get("rows") != contract.get("quality_outcomes"):
        errors.append("contract_copy_mismatch:quality_outcomes")
    if report.get("timing", {}).get("rows") != contract.get("timing_requirements"):
        errors.append("contract_copy_mismatch:timing")

    qualification = report.get("qualification", {})
    for key in ("not_qualified", "all_release_gates_blocked"):
        if qualification.get(key) is not True:
            errors.append("qualification_flag:" + key)
    for key in ("real_result_present", "dataset_present", "annotations_present", "runtime_present",
                "model_present", "commercial_license_granted", "filler_detection_result",
                "boundary_result", "finite_output_result", "baseline_result", "device_timing_result",
                "rate_profile_result", "listening_result", "benchmark_result", "release_claim",
                "missing_result_promoted"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag:" + key)
    if qualification.get("source_present") is not True:
        errors.append("qualification_flag:source_present")

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
    if len(artifacts) != len(reference.REQUIRED_ARTIFACTS):
        errors.append("artifact_count")
    elif not (artifacts[0].get("present") is True and artifacts[0].get("verified") is True
              and artifacts[0].get("blocked") is False):
        errors.append("source_artifact_not_present")
    for artifact in artifacts[1:]:
        if artifact.get("present") is not False or artifact.get("verified") is not False \
                or artifact.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if artifact.get("sha256") is not None:
            errors.append("absent_artifact_has_digest:" + str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != len(reference.EXACT_BLOCKERS):
        errors.append("blocker_count")
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if not blocker.get("required_action"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))

    for section, expected_count, row_key in (
            ("rate_profile", len(reference.RATE_PROFILE_ROWS), "rows"),
            ("quality_outcomes", len(reference.QUALITY_ROWS), "rows"),
            ("timing", len(reference.TIMING_ROWS), "rows")):
        rows = report.get(section, {}).get(row_key, [])
        if len(rows) != expected_count:
            errors.append(section + "_count")
        for row in rows:
            if row.get("status") != "blocked":
                errors.append(section + "_not_blocked:" + str(row.get("id")))

    evidence = report.get("absence_evidence", {})
    summary = evidence.get("summary", {})
    expected_probes = len(reference.WORKSPACE_ABSENCE_PROBES) + len(reference.EXTERNAL_ABSENCE_PROBES)
    if summary.get("probe_count") != expected_probes:
        errors.append("absence_probe_count")
    if summary.get("present_count") != 0:
        errors.append("absence_present_count")
    if summary.get("all_probes_absent") is not True:
        errors.append("absence_all_probes_absent")
    for key in ("download_attempted", "network_used", "recursive_workspace_walk",
                "dataset_loaded", "model_executed", "audio_read"):
        if summary.get(key) is not False:
            errors.append("absence_" + key)

    presence = report.get("source_presence", {})
    for key in ("dataset_present", "annotations_present", "model_or_runtime_present",
                "terms_bundle_present", "rights_review_present",
                "exact_dataset_terms_conjunction_present", "dataset_used",
                "audio_read", "model_executed"):
        if presence.get(key) is not False:
            errors.append("source_presence:" + key)
    if presence.get("candidate_note_and_inventory_present") is not True:
        errors.append("source_presence_missing:candidate_note")

    documented = report.get("documented_context", {})
    if documented.get("provenance_only") is not True:
        errors.append("documented_not_provenance")
    for key in ("reproduced_here", "used_for_evidence", "qualifies"):
        if documented.get(key) is not False:
            errors.append("documented_flag:" + key)
    if documented.get("source_reported_claims_not_reproduced") != reference.documented_claims():
        errors.append("documented_claims_mismatch")
    if report.get("recipe_provenance") != reference.recipe_provenance():
        errors.append("recipe_provenance_mismatch")

    admission = report.get("admission", {})
    admission_summary = admission.get("summary", {})
    expected_cases = reference.admission_cases()
    if admission.get("cases") != expected_cases:
        errors.append("admission_cases_mismatch")
    if admission_summary.get("case_count") != len(expected_cases) \
            or admission_summary.get("rejected_count") != len(expected_cases) \
            or admission_summary.get("accepted_schema_controls") != 1 \
            or admission_summary.get("qualifying_results") != 0:
        errors.append("admission_summary_invalid")
    if admission.get("control", {}).get("qualifies") is not False \
            or admission.get("control", {}).get("accepted") is not True:
        errors.append("admission_control_invalid")
    for key in ("state_advanced_on_rejection", "runtime_invoked", "audio_read",
                "dataset_loaded", "model_executed", "network_used"):
        if admission_summary.get(key) is not False:
            errors.append("admission_" + key)

    if report.get("scorer_control") != reference.scorer_control():
        errors.append("scorer_control_mismatch")

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
    if identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_digest")

    expected_source = {path: {"sha256": digest, "actual": digest, "verified": True}
                       for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {path: {"sha256": digest, "actual": digest, "verified": True}
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

    pins_payload = PINS.read_text(encoding="ascii")
    if "plan/swarm/TASKS.json" in pins_payload:
        errors.append("mutable_board_pinned")
    if not pins_payload.startswith("# SHA-256 pins for SDK-PODCASTFILLERS readiness evidence."):
        errors.append("sources_header")
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARDS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
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
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
    for path in changed:
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    return changed


def check_cold_regeneration(errors: list[str]) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for name in sorted(p.name for p in HERE.iterdir() if p.is_file()):
            shutil.copy2(HERE / name, tmp_path / name)
        observed = []
        for _ in range(3):
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["SOURCE_ROOT"] = str(reference.AUDIO_ROOT)
            env["SDK_ROOT"] = str(reference.WORKTREE)
            for cmd in (["python3", "run.py", "all"],
                        ["python3", "run.py", "report.json"],
                        ["python3", "run.py", "sources"]):
                result = subprocess.run(cmd, cwd=tmp_path, env=env, capture_output=True, text=True)
                if result.returncode != 0:
                    errors.append("cold_regeneration_failed:" + " ".join(cmd) + ":" + result.stdout + result.stderr)
                    return False
            observed.append((
                hashlib.sha256((tmp_path / "report.json").read_bytes()).hexdigest(),
                hashlib.sha256((tmp_path / "SOURCES.sha256").read_bytes()).hexdigest(),
            ))
        if len(set(observed)) != 1:
            errors.append("cold_regeneration_not_byte_identical")
            return False
        committed = (
            hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest(),
            hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest(),
        )
        if observed[0] != committed:
            errors.append("cold_regeneration_differs_from_committed")
            return False
    return True


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pin_count = check_pins(errors)
    check_report(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    identical = check_cold_regeneration(errors)

    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1

    report = reference.read_strict_json(REPORT)
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    print(
        "PASS",
        f"task={reference.TASK}",
        f"decision={report['decision']}",
        f"status={report['status']}",
        f"qualification={report['qualification_status']}",
        f"profile={reference.PROFILE_LABEL}",
        f"gates={len(report['gates'])}/8-blocked",
        f"artifacts={len(report['required_artifacts'])}",
        f"blockers={len(report['exact_blockers'])}",
        f"pinned_inputs={pin_count}",
        f"changed_files={len(changed)}",
        f"cold_starts=3/3",
        f"byte_identical={str(identical).lower()}",
        f"report_sha256={digest}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
