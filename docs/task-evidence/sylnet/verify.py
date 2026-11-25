# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SYLNET task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, unpinned files,
license gaps, out-of-scope worktree changes or a dirty diff check. Never writes.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
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
    "negative_claims", "boundary", "format", "contract_id", "contract_sha256",
    "source_pins", "boundary_pins", "model_provenance", "licensing_analysis",
    "tool_provenance", "surrogate", "rate_profile",
    "conditions", "controls", "adverse", "playback_buffering", "regressions",
    "source_reported", "exact_blockers", "gates", "missing_evidence",
    "evidence_classes", "repeatability",
}
MISSING_FRAME_REASONS = {"rejected_incomplete_window"}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}


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
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
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
    if report["profile"] != reference.PROFILE or contract.get("profile") != reference.PROFILE:
        errors.append("rate_profile_not_applied")
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
            ("frame_samples", 160), ("window_samples", 64000),
            ("final_partial_samples", 37), ("public_v0_geometry_preserved", True),
            ("sdk_callback_invoked", False)):
        if fmt.get(key) != value:
            errors.append("format_mismatch:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)
    for key in ("sylnet_source", "sylnet_checkpoint_loaded", "model_weights",
                "real_audio", "real_labels", "vendor_runtime_invoked", "device_timing",
                "listening_result", "rendered_playback", "benchmark_claim",
                "release_claim", "registered_provider"):
        if report["scope"].get(key) is not False:
            errors.append("scope_claim:" + key)
    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if contract["source_pins"] != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if contract["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    provenance = report["model_provenance"]
    if provenance != reference.MODEL_PROVENANCE:
        errors.append("model_provenance_mismatch")
    if contract.get("model_provenance") != reference.MODEL_PROVENANCE:
        errors.append("contract_model_provenance_mismatch")
    licensing = report["licensing_analysis"]
    if licensing != reference.LICENSING_ANALYSIS:
        errors.append("licensing_analysis_mismatch")
    if contract.get("licensing_analysis") != reference.LICENSING_ANALYSIS:
        errors.append("contract_licensing_analysis_mismatch")
    if provenance.get("upstream_commit") != reference.UPSTREAM_COMMIT:
        errors.append("upstream_commit_mismatch")
    if provenance.get("upstream_license") != reference.UPSTREAM_LICENSE:
        errors.append("upstream_license_mismatch")
    if provenance.get("upstream_repository") != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_repository_mismatch")
    correction = provenance.get("identity_correction", {})
    if (correction.get("source_reported_repository")
            != reference.UPSTREAM_REPOSITORY_STALE
            or correction.get("source_reported_repository_status")
            != "404_not_found"
            or correction.get("corrected_repository")
            != reference.UPSTREAM_REPOSITORY
            or correction.get("corrected_repository_resolves_pinned_commit")
            is not True
            or correction.get("corrected_repository_resolves_pinned_bytes")
            is not True):
        errors.append("upstream_identity_correction_invalid")
    resolution = provenance.get("repository_resolution", {})
    if (resolution.get("expected_remote") != reference.UPSTREAM_REPOSITORY
            or resolution.get("expected_commit") != reference.UPSTREAM_COMMIT
            or resolution.get("snapshot") != reference.UPSTREAM_SNAPSHOT):
        errors.append("upstream_resolution_expectation_invalid")
    checkpoint = provenance.get("checkpoint", {})
    if (checkpoint.get("present_in_sdk_worktree") is not False
            or checkpoint.get("loaded_or_executed") is not False
            or checkpoint.get("tracked_in_upstream_commit") is not True):
        errors.append("checkpoint_scope_claim_invalid")
    if checkpoint.get("bytes") != reference.UPSTREAM_CHECKPOINT_BYTES:
        errors.append("checkpoint_size_mismatch")
    for key in ("training_data_provenance_established",
                "separate_weights_terms_established", "redistribution_clearance",
                "product_use_clearance", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    if licensing.get("upstream_license_sha256") != reference.SOURCE_PINS[
            reference.UPSTREAM_LICENSE_PATH]:
        errors.append("licensing_license_pin_mismatch")
    if licensing.get("blocked_gate") != "exact_checkpoint_config_rights":
        errors.append("licensing_gate_mismatch")
    if report["contract_sha256"] != reference.sha256(reference.contract_bytes()):
        errors.append("contract_digest_mismatch")
    if report["surrogate"].get("is_sylnet_source") is not False:
        errors.append("surrogate_promoted_to_sylnet_source")
    if report["source_reported"].get("status") != "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")
    if report["source_reported"].get("used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")
    detailed = report["source_reported"].get("detailed_pilot", {})
    if (detailed.get("status") != "source_reported_not_reproduced"
            or detailed.get("used_for_qualification") is not False):
        errors.append("detailed_pilot_not_labeled_provenance_only")
    if not report["exact_blockers"] or report["exact_blockers"] != contract["exact_blockers"]:
        errors.append("exact_blockers_missing_or_mismatched")
    if len(report["missing_evidence"]) != len(reference.MISSING_EVIDENCE):
        errors.append("missing_evidence_list_changed")
    rate = report["rate_profile"]
    if (rate["profile"] != reference.PROFILE
            or rate["renderer_executed"] is not False
            or rate["duration_measured"] is not False
            or rate["rate_cases"] != {name: str(value)
                                      for name, value in reference.RATE_CASES.items()}):
        errors.append("rate_profile_claim_invalid")
    if set(report["conditions"]) != set(reference.CONDITIONS):
        errors.append("condition_set_mismatch")
    for condition, cases in report["conditions"].items():
        if set(cases) != set(reference.RATE_CASES):
            errors.append("rate_case_set_mismatch:" + condition)
        for name, case in cases.items():
            prefix = condition + ":" + name
            stop = reference.WINDOW_SAMPLES
            if case["source_interval"] != [0, stop]:
                errors.append("source_interval_wrong:" + prefix)
            starts = [pair[0] for pair in case["event_intervals"]]
            if starts != list(range(0, stop, reference.FRAME_SAMPLES)):
                errors.append("event_starts_not_exact:" + prefix)
            if case["event_intervals"][-1][1] != stop:
                errors.append("event_end_wrong:" + prefix)
            if case["available_ns_last"] != reference.FIXTURE_EPOCH_NS + stop * reference.NS_PER_SAMPLE:
                errors.append("fixture_clock_wrong:" + prefix)
            partial = case["final_partial"]
            expected_valid = (37 if condition == "tail_partial"
                              else reference.FRAME_SAMPLES)
            if (partial["source"] != [stop - reference.FRAME_SAMPLES, stop]
                    or partial["valid_count"] != expected_valid
                    or partial["final_flag"] is not True):
                errors.append("final_partial_wrong:" + prefix)
            if case["renderer_executed"] is not False or case["duration_measured"] is not False:
                errors.append("render_claimed:" + prefix)
            if case["nuclei_count"] != len(case["nuclei_intervals"]):
                errors.append("nuclei_count_inconsistent:" + prefix)
            if case["count_abs_error"] != abs(case["nuclei_count"] - case["frozen_target_count"]):
                errors.append("count_error_wrong:" + prefix)
            if case["rate_estimate"] != str(reference.Fraction(
                    case["nuclei_count"] * reference.SAMPLE_RATE_HZ, stop)):
                errors.append("rate_estimate_wrong:" + prefix)
            if case["target_output_samples"] != str(
                    reference.Fraction(stop, 1) / reference.RATE_CASES[name]):
                errors.append("target_duration_wrong:" + prefix)
            if case["rejections"]:
                errors.append("frozen_frame_rejected:" + prefix)
            if case["unknown_counted"] > case["unknown_frames"]:
                errors.append("unknown_counted:" + prefix)
    controls = report["controls"]
    if controls.get("all_present") is not True:
        errors.append("controls_not_present")
    if controls["identity"].get("count_abs_error") != 0:
        errors.append("identity_control_not_exact")
    if controls["named_baseline"].get("name") != "frozen_constant_count_control":
        errors.append("named_baseline_missing")
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
    if adverse["missing_frame"]["status"] != "rejected" or adverse[
            "missing_frame"]["reason"] not in MISSING_FRAME_REASONS:
        errors.append("missing_frame_not_rejected")
    if not all(value["status"] == "rejected" for value in adverse["lifecycle"].values()):
        errors.append("lifecycle_not_rejected")
    validity = adverse["validity"]
    if validity["unknown_frames"] <= 0 or validity["unknown_counted"] != 0:
        errors.append("unknown_validity_not_retained")
    for model in report["playback_buffering"].values():
        if (model["clock_id"] != reference.CLOCK_ID
                or model["deadline_measured"] is not False
                or model["device_clock_drift_measured"] is not False):
            errors.append("device_timing_claimed")
    if len(report["gates"]) != len(reference.GATE_NAMES):
        errors.append("gate_count_changed")
    for gate in report["gates"]:
        if gate["status"] != "blocked" or not gate["reopen_condition"]:
            errors.append("gate_not_blocked:" + gate["name"])
    repeat = report["repeatability"]
    if (repeat["count"] != 3 or repeat["byte_identical"] is not True
            or len(set(repeat["digests"])) != 1
            or repeat["digests"] != reference.repeatability()["digests"]):
        errors.append("cold_start_repeatability_failed")


def check_upstream_identity(errors: List[str]) -> None:
    """Pinned URL and commit must agree in the checkout supplying pinned bytes."""
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
    correction = reference.MODEL_PROVENANCE["identity_correction"]
    if correction["corrected_repository"] != identity["normalized_remote"]:
        errors.append("upstream_identity_correction_mismatch")
    if correction["source_reported_repository"] != reference.UPSTREAM_REPOSITORY_STALE:
        errors.append("upstream_stale_repository_mismatch")


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
        "a" * 64 + "  docs/task-evidence/sylnet/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
    )
    for text in bad_pins:
        try:
            reference.parse_pin_lines(text)
            errors.append("strict_pin_parser_accepted:" + repr(text))
        except ValueError:
            pass


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    if (f"<!-- {SPDX_COPYRIGHT} -->" not in readme
            or f"<!-- {SPDX_LICENSE} -->" not in readme):
        errors.append("README_spdx_missing")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
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
    pins = check_pins(errors)
    payloads = check_json(errors)
    if len(payloads) == 2 and payloads["contract"] and payloads["report"]:
        check_content(errors, payloads)
    check_upstream_identity(errors)
    check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        pin_failures = [error for error in errors if (
            error.startswith(("strict_pin", "pin_", "pinned_", "SOURCES", "incomplete_pin")))]
        json_failures = [error for error in errors if (
            error.startswith("strict_json")
            or error.endswith("canonical_bytes")
            or error.endswith("sidecar_stale")
            or error.startswith("report_missing_keys")
            or error == "negative_zero_in_artifact")]
        print(f"pins_ok={pins == len(reference.allowed_pin_keys()) and not pin_failures} "
              f"json_ok={not json_failures} report_sha256={digest} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} json_ok=2 upstream_identity_ok=1 "
          f"strict_rejections_ok=9 reproduction_ok=3 "
          f"licensing_ok=1 scope_ok=1 changed_files={changed} profile=rate "
          f"status={reference.STATUS} qualification={reference.QUALIFICATION} "
          f"decision={reference.DECISION} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
