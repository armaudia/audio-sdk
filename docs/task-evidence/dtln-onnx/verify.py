# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DTLN-ONNX task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, unpinned files,
license gaps, out-of-scope worktree changes, an unpinned interpreter, a
caller-supplied asset gate that is not blocked, or a dirty diff check. Never
writes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license", "contract.json.license",
    "report.json.license", "report.json.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "no_missing_result_qualifies_candidate", "scope",
    "negative_claims", "boundary", "format", "stream", "contract_id",
    "contract_sha256", "source_pins", "boundary_pins", "scorer_pins",
    "model_provenance", "caller_supplied_asset_gate", "licensing_analysis",
    "tool_provenance", "surrogate", "acceptance_profile", "conditions",
    "controls", "adverse", "regressions", "source_reported", "exact_blockers",
    "gates", "missing_evidence", "evidence_classes", "repeatability",
}
ACCEPTANCE_CASES = {
    "identity_noisy_control", "established_task_matched_baseline",
    "paired_si_sdr_stoi", "clean_speech_preservation",
    "peaks_and_invalid_outputs", "unpaired_speech",
    "alignment_state_memory_timing",
}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}


def check_interpreter(errors: List[str]) -> None:
    if not reference.interpreter_is_pinned():
        errors.append("interpreter_not_pinned:" + sys.version.split()[0])


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
    for digest, raw in pins:
        path = reference.pin_path(raw)
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256(path.read_bytes()) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    try:
        generated = reference.sources_bytes()
    except OSError as error:
        errors.append("sources_generation_failed:" + str(error))
        return len(pins)
    if PINS.read_bytes() != generated:
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": _strict_json(CONTRACT, errors, "contract"),
        "report": _strict_json(REPORT, errors, "report"),
    }
    if not payloads["contract"] or not payloads["report"]:
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    report = payloads["report"]
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return payloads
    if REPORT.read_bytes() != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    if b"-0.0" in REPORT.read_bytes() or b"-0.0" in CONTRACT.read_bytes():
        errors.append("negative_zero_in_artifact")
    expected_sidecar = f"{reference.sha256(REPORT.read_bytes())}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    return payloads


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    if report["base_commit"] != reference.BASE_COMMIT:
        errors.append("base_commit_mismatch")
    if report["branch"] != reference.BRANCH or contract.get("branch") != reference.BRANCH:
        errors.append("branch_mismatch")
    if report["profile"] != reference.PROFILE or contract.get("profile") != reference.PROFILE:
        errors.append("enhancement_profile_not_applied")
    for key, expected in (
            ("status", reference.STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("evidence_status", "incomplete"),
            ("defer_before", "processor_exposure")):
        if report.get(key) != expected:
            errors.append("disposition_mismatch:" + key)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    boundary_false = (
        "registered", "enabled_by_default", "default_selected",
        "public_api_abi_change", "provider_registration",
        "descriptor_registry_change", "shared_cmakelists_change",
        "installed_v0_behavior_change", "processor_exposure", "ci_change",
    )
    for key in boundary_false:
        if report["boundary"].get(key) is not False or contract["boundary"].get(key) is not False:
            errors.append("boundary_not_false:" + key)
    if report["boundary"].get("descriptor_settings") != {}:
        errors.append("descriptor_settings_not_empty")
    fmt = report["format"]
    for key, value in (
            ("sample_rate_hz", 16000), ("channels", 1), ("sample_format", "f32"),
            ("frame_samples", 160), ("hop_samples", 160), ("content_delay_samples", 0),
            ("public_v0_geometry_preserved", True), ("sdk_callback_invoked", False)):
        if fmt.get(key) != value:
            errors.append("format_mismatch:" + key)
    stream = report["stream"]
    for key, value in (
            ("sample_rate_hz", 16000), ("channels", 1), ("sample_format", "f32"),
            ("block_samples", 512), ("hop_samples", 128), ("magnitude_bins", 257),
            ("graphs_required", 2), ("delay_samples", 384), ("delay_hops", 3),
            ("installed_v0_geometry_preserved", True),
            ("installed_v0_behavior_changed", False)):
        if stream.get(key) != value:
            errors.append("stream_mismatch:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)
    for key, value in report["scope"].items():
        if value is not False:
            errors.append("scope_claim:" + key)
    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    if contract["source_pins"] != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if contract["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    if report["scorer_pins"] != reference.SCORER_PINS:
        errors.append("report_scorer_pins_mismatch")
    if contract["scorer_pins"] != reference.SCORER_PINS:
        errors.append("contract_scorer_pins_mismatch")
    provenance = report["model_provenance"]
    if provenance != reference.model_provenance():
        errors.append("model_provenance_mismatch")
    if contract.get("model_provenance") != reference.model_provenance():
        errors.append("contract_model_provenance_mismatch")
    if provenance.get("upstream_commit") != reference.UPSTREAM_COMMIT:
        errors.append("upstream_commit_mismatch")
    if provenance.get("upstream_repository") != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_repository_mismatch")
    if provenance.get("upstream_license") != reference.UPSTREAM_LICENSE:
        errors.append("upstream_license_mismatch")
    graphs = provenance.get("graphs", [])
    if len(graphs) != 2:
        errors.append("graph_count_mismatch")
    for graph in graphs:
        if (graph.get("present_in_sdk_worktree") is not False
                or graph.get("loaded_or_executed") is not False
                or graph.get("tracked_in_upstream_commit") is not True):
            errors.append("graph_scope_claim_invalid:" + str(graph.get("role")))
    if provenance.get("runtime_lock", {}).get("installed_in_sdk_worktree") is not False:
        errors.append("runtime_installed_claim_invalid")
    licensing = report["licensing_analysis"]
    if licensing != reference.licensing_analysis():
        errors.append("licensing_analysis_mismatch")
    if contract.get("licensing_analysis") != reference.licensing_analysis():
        errors.append("contract_licensing_analysis_mismatch")
    for key in ("training_data_provenance_established", "separate_weights_terms_established",
                "onnx_runtime_redistribution_terms_established", "redistribution_clearance",
                "product_use_clearance", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    if licensing.get("blocked_gate") != "exact_graphs_runtime_and_rights":
        errors.append("licensing_gate_mismatch")
    gate = report["caller_supplied_asset_gate"]
    if gate.get("status") != "blocked":
        errors.append("asset_gate_not_blocked")
    if gate.get("inference_executed") is not False:
        errors.append("asset_gate_executed_inference")
    if gate.get("validation", {}).get("status") not in ("blocked", "rejected"):
        errors.append("asset_gate_validation_not_fail_closed")
    if gate.get("validation", {}).get("reason") != "blocked_runtime_unavailable":
        errors.append("asset_gate_reason_unexpected")
    if gate.get("onnxruntime_importable") is not False:
        errors.append("onnxruntime_availability_claim_invalid")
    if report["surrogate"].get("is_dtln_source") is not False:
        errors.append("surrogate_promoted_to_dtln_source")
    if report["surrogate"].get("is_spectral_mask") is not False:
        errors.append("surrogate_promoted_to_spectral_mask")
    if report["contract_sha256"] != reference.sha256(reference.contract_bytes()):
        errors.append("contract_digest_mismatch")
    if report["source_reported"].get("status") != "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")
    if report["source_reported"].get("used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")
    if not report["exact_blockers"] or report["exact_blockers"] != contract["exact_blockers"]:
        errors.append("exact_blockers_missing_or_mismatched")
    if len(report["missing_evidence"]) != len(reference.MISSING_EVIDENCE):
        errors.append("missing_evidence_list_changed")
    acceptance = report["acceptance_profile"]
    if acceptance.get("profile") != reference.PROFILE:
        errors.append("acceptance_profile_not_enhancement")
    if set(acceptance.get("mapped_cases", {})) != ACCEPTANCE_CASES:
        errors.append("acceptance_cases_changed")
    if set(report["conditions"]) != set(reference.CONDITIONS):
        errors.append("condition_set_mismatch")
    for name, case in report["conditions"].items():
        prefix = "condition:" + name
        if case["status"] == "excluded_no_reference":
            if case["candidate_metrics"]["status"] != "excluded":
                errors.append("excluded_not_labeled:" + prefix)
            if case["candidate_metrics"]["si_sdr_db"] is not None:
                errors.append("excluded_has_si_sdr:" + prefix)
            continue
        if case["status"] != "measured_synthetic":
            errors.append("condition_not_measured:" + prefix)
        if case["baseline_metrics"]["status"] != "measured_synthetic":
            errors.append("baseline_not_measured:" + prefix)
        if case["candidate_metrics"]["status"] != "measured_synthetic":
            errors.append("candidate_not_measured:" + prefix)
        if case["delay_compensation_samples"] != reference.DELAY_SAMPLES:
            errors.append("delay_compensation_wrong:" + prefix)
        run = case["frame_run"]
        if run["status"] != "ok" or run["rejections"] != 0:
            errors.append("frozen_signal_rejected:" + prefix)
        if run["valid_samples"] != case["samples"]:
            errors.append("valid_sample_count_wrong:" + prefix)
        if run["padded_samples"] != run["final_hop"]["padded_count"]:
            errors.append("padded_count_inconsistent:" + prefix)
        if run["final_hop"]["source"][1] != case["samples"]:
            errors.append("final_hop_end_wrong:" + prefix)
        if name == "tail_partial":
            if (run["final_hop"]["valid_count"] != 91
                    or run["final_hop"]["padded_count"] != 37
                    or case["samples"] != reference.TAIL_SAMPLES):
                errors.append("tail_partial_geometry_wrong")
        else:
            if (run["final_hop"]["valid_count"] != reference.HOP_SAMPLES
                    or run["final_hop"]["padded_count"] != 0
                    or case["samples"] != reference.WINDOW_SAMPLES):
                errors.append("full_condition_geometry_wrong:" + prefix)
        if case["candidate_metrics"]["nonfinite_count"] != 0:
            errors.append("nonfinite_output:" + prefix)
        if case["candidate_metrics"]["peak_abs_output"] > 1.0:
            errors.append("output_exceeds_unity:" + prefix)
    if report["conditions"]["silence"]["status"] != "excluded_no_reference":
        errors.append("silence_not_excluded")
    controls = report["controls"]
    if controls.get("all_present") is not True:
        errors.append("controls_not_present")
    if controls["identity"].get("name") != "identity_no_processing":
        errors.append("identity_control_missing")
    if controls["named_baseline"].get("name") != "noisy_input_no_processing":
        errors.append("named_baseline_missing")
    if controls["candidate"].get("metrics", {}).get("status") != "measured_synthetic":
        errors.append("candidate_control_not_measured")
    if controls["clean_speech_preservation"].get("metrics", {}).get("status") != "measured_synthetic":
        errors.append("clean_preservation_not_measured")
    mismatch = controls["mismatch"]
    if (mismatch.get("all_rejected") is not True
            or mismatch.get("all_state_unchanged") is not True):
        errors.append("mismatch_control_failed")
    adverse = report["adverse"]
    if adverse.get("all_rejected") is not True:
        errors.append("adverse_all_rejected_false")
    for section in ("config_rejections", "frame_rejections"):
        for name, value in adverse[section].items():
            if name == "dsp_state_unchanged":
                continue
            if value["status"] != "rejected":
                errors.append("adverse_not_rejected:" + section + ":" + name)
    for name, value in adverse["frame_rejections"].items():
        if name != "dsp_state_unchanged" and value["state_unchanged"] is not True:
            errors.append("state_changed_on_rejection:" + name)
    if adverse["frame_rejections"].get("dsp_state_unchanged") is not True:
        errors.append("dsp_state_unchanged_not_true")
    for name, value in adverse["lifecycle"].items():
        if name == "valid_reset":
            if value != "ok":
                errors.append("valid_reset_failed")
        elif value["status"] != "rejected":
            errors.append("lifecycle_not_rejected:" + name)
    for name, value in adverse["asset_gate"].items():
        if value["status"] not in ("rejected", "blocked"):
            errors.append("asset_gate_case_not_fail_closed:" + name)
    if adverse["asset_gate"]["hash_mismatch"]["reason"] != "blocked_hash_mismatch":
        errors.append("asset_gate_hash_mismatch_not_detected")
    if adverse["asset_gate"]["absent"]["reason"] != "blocked_asset_absent":
        errors.append("asset_gate_absence_not_detected")
    if adverse["asset_gate"]["runtime_unavailable"]["reason"] != "blocked_runtime_unavailable":
        errors.append("asset_gate_runtime_not_detected")
    if adverse["asset_gate_control"].get("status") != "ready_for_caller_execution":
        errors.append("asset_gate_control_did_not_reach_ready")
    if len(report["gates"]) != len(reference.GATE_NAMES):
        errors.append("gate_count_changed")
    if [gate["name"] for gate in report["gates"]] != list(reference.GATE_NAMES):
        errors.append("report_gate_list_mismatch")
    if contract.get("gates") != list(reference.GATE_NAMES):
        errors.append("contract_gate_list_mismatch")
    for gate in report["gates"]:
        if gate["status"] != "blocked" or not gate["reopen_condition"]:
            errors.append("gate_not_blocked:" + gate["name"])
    repeat = report["repeatability"]
    if (repeat["count"] != 3 or repeat["byte_identical"] is not True
            or len(set(repeat["digests"])) != 1
            or repeat["digests"] != reference.repeatability()["digests"]):
        errors.append("cold_start_repeatability_failed")


def check_scorer(errors: List[str]) -> None:
    prior = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py"
    if not prior.is_file():
        errors.append("prior_scorer_missing")
        return
    expected = prior.read_text(encoding="utf-8").replace(
        'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
        f'SCORER_ID = "{reference.SCORER_ID}"')
    if (HERE / "scorer.py").read_text(encoding="utf-8") != expected:
        errors.append("scorer_not_byte_identical_apart_from_id")
    vectors = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json"
    if not vectors.is_file():
        errors.append("crosscheck_vectors_missing")
    else:
        try:
            payload = reference.json.loads(vectors.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            errors.append("crosscheck_vectors_unreadable:" + str(error))
            return
        if not isinstance(payload, list) or len(payload) != 6:
            errors.append("crosscheck_vectors_changed")


def check_upstream_identity(errors: List[str]) -> None:
    try:
        identity = reference.upstream_git_identity()
    except (OSError, ValueError) as error:
        errors.append("upstream_identity_failed:" + str(error))
        return
    if identity["normalized_remote"] != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_remote_mismatch:" + identity["normalized_remote"])
    if identity["commit"] != reference.UPSTREAM_COMMIT:
        errors.append("upstream_commit_mismatch:" + identity["commit"])
    if identity["pinned_commit_present"] is not True:
        errors.append("upstream_pinned_commit_absent")


def check_strict_rejections(errors: List[str]) -> None:
    bad_inputs = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    for text in bad_inputs:
        try:
            reference.strict_loads(text)
            errors.append("strict_json_accepted:" + repr(text))
        except ValueError:
            pass
    bad_pins = (
        "not-a-line",
        "a" * 64 + "  ../escape",
        "a" * 64 + "  docs/task-evidence/dtln-onnx/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
    )
    for text in bad_pins:
        try:
            reference.parse_pin_lines(text)
            errors.append("strict_pin_parser_accepted:" + repr(text))
        except ValueError:
            pass


def check_readme(errors: List[str]) -> None:
    path = HERE / "README.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("readme_unreadable:" + str(error))
        return
    try:
        rows = reference.readme_artifact_digests(text)
    except ValueError as error:
        errors.append("readme_digest_table_invalid:" + str(error))
    else:
        expected = set(reference.README_ARTIFACT_FILES)
        if set(rows) != expected:
            errors.append("readme_digest_table_files_mismatch")
        for name in reference.README_ARTIFACT_FILES:
            target = HERE / name
            if not target.is_file():
                errors.append("readme_digest_target_missing:" + name)
            elif rows.get(name) != reference.sha256(target.read_bytes()):
                errors.append("readme_digest_stale:" + name)
    try:
        items = reference.readme_gate_items(text)
    except ValueError as error:
        errors.append("readme_gate_list_invalid:" + str(error))
    else:
        if len(items) != len(reference.GATE_NAMES):
            errors.append("readme_gate_count_mismatch:" + str(len(items)))


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("README_spdx_missing")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
            errors.append("missing_license_sidecar:" + name)
    reuse_path = SDK_ROOT / "REUSE.toml"
    reuse = reuse_path.read_text(encoding="utf-8") if reuse_path.is_file() else ""
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")


def check_scope(errors: List[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return 0
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(reference.TASK_PREFIX):
                errors.append("out_of_scope_change:" + path)
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {reference.TASK_PREFIX + name for name in reference.LOCAL_PIN_PATHS}
    pinned.add(reference.TASK_PREFIX + "SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and reference.TASK_PREFIX + path.name not in pinned:
            errors.append("unpinned_task_file:" + path.name)
    return len(changed)


def main() -> int:
    errors: List[str] = []
    check_interpreter(errors)
    pins = check_pins(errors)
    payloads = check_json(errors)
    if len(payloads) == 2 and payloads["contract"] and payloads["report"]:
        check_content(errors, payloads)
    check_scorer(errors)
    check_upstream_identity(errors)
    check_strict_rejections(errors)
    check_readme(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins_ok={pins == len(reference.allowed_pin_keys())} "
              f"report_sha256={digest} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} json_ok=2 interpreter=3.12.16 upstream_identity_ok=1 "
          f"strict_rejections_ok=9 readme_ok=1 reproduction_ok=3 licensing_ok=1 scope_ok=1 "
          f"changed_files={changed} profile=enhancement status={reference.STATUS} "
          f"qualification={reference.QUALIFICATION} decision={reference.DECISION} "
          f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
