# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-FACEBOOK-DENOISER-DNS48 package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-enhancement profile, a promoted metric, a fabricated STOI,
baseline, geometry or licence grant, a qualified claim, an open release gate,
licence gaps, out-of-scope worktree changes, whitespace damage or a failing
``git diff --check``. Never writes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
TEXT_ARTIFACTS = (
    "README.md", "reference.py", "run.py", "report.json",
    "report.json.sha256", "contract.json", "test_reference.py", "verify.py",
    "SOURCES.sha256", "SOURCES.sha256.license", "contract.json.license",
    "report.json.license", "report.json.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "evidence_status", "profile", "acceptance_profile", "profile_blockers",
    "candidate", "reference", "format", "fixtures", "paired_metrics",
    "clean_preservation", "peaks_and_invalid", "pause_attenuation", "stoi",
    "baseline", "alignment", "streaming", "reset", "final_partial",
    "state_and_memory", "runtime_timing", "listening", "nonfinite",
    "adverse_rejections", "adverse_all_rejected", "valid_controls",
    "external_artifacts", "licensing", "license_scope", "caller_asset",
    "board_row", "boundary", "boundary_pins", "source_pins", "scope",
    "qualification", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "surrogate", "repeatability", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile", "candidate",
    "format", "licensing", "license_scope", "artifact_pins", "board_row",
    "boundary", "boundary_pins", "source_pins", "scope", "reference",
    "exact_blockers", "release_gates", "reopen_condition", "negative_claims",
    "caller_asset_contract", "invariants",
}
PROFILE_ITEMS = {
    "identity_noisy_control", "task_matched_baseline", "paired_si_sdr",
    "paired_stoi", "clean_speech_preservation", "peaks_and_invalid_outputs",
    "unpaired_predictive_screen_or_listening", "alignment_content_mapping",
    "runtime_availability_timing", "streaming_state_and_reset",
    "runtime_memory", "task_matched_heldout_qualification",
}
QUALIFICATION_FALSE_KEYS = [
    "qualifies", "all_required_results_present", "missing_result_promoted",
    "exact_source_present", "exact_weights_present",
    "exact_runtime_outputs_present", "checkpoint_lineage_verified",
    "rights_cleared_cohort", "geometry_documented", "paired_control_qualified",
    "baseline_qualified", "si_sdr_qualified", "stoi_qualified",
    "clean_preservation_qualified", "peaks_validated",
    "alignment_qualified", "timing_measured", "memory_measured",
    "hallucination_checked", "listening", "real_corpus_used",
]


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.load_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("JSON root is not an object: " + label)
        return {}
    return payload


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label + " (actual=" + repr(actual) + ")")


def _false(errors: List[str], section: Dict[str, Any], keys: List[str],
           label: str) -> None:
    for key in keys:
        if section.get(key) is not False:
            errors.append(label + " claims true: " + key)


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        expected, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != expected.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        try:
            if SIDECAR.read_text(encoding="ascii") != digest + "\n":
                errors.append("report.json.sha256 is stale")
        except OSError as error:
            errors.append("missing report.json.sha256: " + str(error))
    if contract:
        if CONTRACT.read_bytes() != (
                reference.canonical_text(contract) + "\n").encode("utf-8"):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    count = 0
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, raw_path = parts
        if raw_path.endswith("TASKS.json"):
            errors.append("mutable task board is pinned: " + raw_path)
            continue
        if raw_path.startswith("source:"):
            path = reference.SOURCE_ROOT / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + raw_path)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic generated bytes")
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("pin regeneration failed: " + str(error))
    for path in SOURCE_PIN_KEYS:
        if "source:" + path not in PINS.read_text(encoding="utf-8"):
            errors.append("source pin missing from manifest: " + path)
    for path in reference.BOUNDARY_PINS:
        if "  " + path not in PINS.read_text(encoding="utf-8"):
            errors.append("boundary pin missing from manifest: " + path)
    return count


SOURCE_PIN_KEYS = tuple(reference.SOURCE_PINS)


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    live = reference.board_row()
    _eq(errors, "report board identity is stale", report.get("board_row"), live)
    _eq(errors, "contract board identity is stale", contract.get("board_row"),
        live)
    row = report.get("board_row", {})
    if row.get("full_tasks_json_hashed") is not False:
        errors.append("full task board is hashed")
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    if stable.get("id") != reference.TASK_ID:
        errors.append("stable board task id mismatch")
    for section in ("source_pins", "boundary_pins"):
        for path in report.get(section, {}):
            if path.endswith("TASKS.json"):
                errors.append("mutable task board is pinned in " + section)


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    missing = REQUIRED_REPORT_KEYS - set(report)
    if missing:
        errors.append("report missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected report schema", report["schema_id"],
        reference.REPORT_SCHEMA)
    _eq(errors, "report status", report["status"], reference.STATUS)
    _eq(errors, "report evidence status", report["evidence_status"],
        "incomplete")
    _eq(errors, "report decision", report["decision"], "DEFER")
    _eq(errors, "report defer point", report["defer_before"],
        "opt_in_adapter_exposure")
    _eq(errors, "report profile", report["profile"], "enhancement")
    _eq(errors, "report task", report["task"], reference.TASK_ID)
    _eq(errors, "report component", report["component"], reference.COMPONENT)
    _eq(errors, "report base commit", report["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report["branch"], reference.BRANCH)

    qualification = report["qualification"]
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    _false(errors, qualification, QUALIFICATION_FALSE_KEYS, "qualification")

    gates = report["release_gates"]
    if len(gates) != 8:
        errors.append("expected exactly eight release gates")
    if [gate.get("id") for gate in gates] != [
            f"RG-{index:02d}" for index in range(1, 9)]:
        errors.append("release gate IDs are not RG-01..RG-08")
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("a release gate is not blocked")

    profile = report["acceptance_profile"]
    _eq(errors, "enhancement profile not recorded", profile.get("profile"),
        "enhancement")
    items = profile.get("required_items", {})
    if set(items) != PROFILE_ITEMS:
        errors.append("enhancement profile item set mismatch")
    for name, item in items.items():
        if item.get("status") not in {"synthetic_only", "blocked"}:
            errors.append("profile item promoted: " + name)
    expected_blockers = sorted(
        name for name, item in items.items() if item.get("status") == "blocked")
    _eq(errors, "profile blocker list mismatch", report["profile_blockers"],
        expected_blockers)
    if "task_matched_heldout_qualification" not in expected_blockers:
        errors.append("held-out qualification is not blocked")
    if "runtime_availability_timing" not in expected_blockers:
        errors.append("runtime timing is not blocked")

    candidate = report["candidate"]
    _eq(errors, "candidate hidden channels",
        candidate.get("reported_hidden_channels"), 48)
    _eq(errors, "candidate reported rate",
        candidate.get("reported_input_sample_rate_hz"), 16000)
    _eq(errors, "candidate streaming flag",
        candidate.get("reported_streaming"), True)
    _eq(errors, "candidate offline flag",
        candidate.get("reported_offline_whole_utterance"), False)
    _eq(errors, "candidate reported licence",
        candidate.get("reported_license"), "CC-BY-NC-4.0")
    for key in ("reported_parameter_count", "reported_hop_samples",
                "reported_frame_samples",
                "reported_algorithmic_latency_samples"):
        if candidate.get(key) is not None:
            errors.append("candidate fact is fabricated: " + key)
    _false(errors, candidate, [
        "checkpoint_lineage_verified", "geometry_documented",
        "source_present", "weights_present", "runtime_present",
        "exact_numeric_output_present"], "candidate")
    if candidate.get("reported_upstream_metrics", {}).get("values") is not None:
        errors.append("candidate metrics are fabricated")

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    _eq(errors, "surrogate content delay",
        fmt.get("surrogate_content_delay_samples"), 0)
    _eq(errors, "surrogate lookahead",
        fmt.get("surrogate_lookahead_samples"), 0)
    _eq(errors, "surrogate frame causality",
        fmt.get("surrogate_frame_causal"), True)
    _eq(errors, "candidate reported rate",
        fmt.get("candidate_reported_sample_rate_hz"), 16000)
    _eq(errors, "candidate hidden channels",
        fmt.get("candidate_reported_hidden_channels"), 48)
    _eq(errors, "candidate streaming",
        fmt.get("candidate_streaming_reported"), True)
    _eq(errors, "candidate offline flag",
        fmt.get("candidate_offline_whole_utterance"), False)
    _false(errors, fmt, ["candidate_geometry_documented",
                         "model_asset_in_installed_v0"], "format")

    reference_record = report["reference"]
    for key in ("source_present", "weights_present", "runtime_present",
                "implementation_present", "adapter_present",
                "exact_numeric_output_present", "checkpoint_lineage_verified",
                "surrogate_is_candidate"):
        if reference_record.get(key) is not False:
            errors.append("reference claim is not false: " + key)
    if reference_record.get("status") != "blocked":
        errors.append("reference status is not blocked")
    if reference_record.get("license_identity") is not None:
        errors.append("licence identity is fabricated")

    if len(report["exact_blockers"]) != 6:
        errors.append("expected six exact blockers")
    blocker_ids = {blocker.get("id") for blocker in report["exact_blockers"]}
    for expected in (
            "pinned_facebook_denoiser_source_weights_runtime_absent",
            "license_cc_by_nc_4_0_research_only",
            "candidate_geometry_streaming_and_latency_unverified",
            "sdk_enhancement_boundary_and_provider_integration_absent",
            "rights_cleared_paired_cohort_and_scorer_absent",
            "compute_content_preservation_and_independent_review_absent"):
        if expected not in blocker_ids:
            errors.append("exact blocker missing: " + expected)

    paired = report["paired_metrics"]
    regions = paired["regions"]
    _eq(errors, "paired region count", len(regions), 3)
    for region in regions:
        if region.get("qualifies") is not False:
            errors.append("paired region is promoted: "
                          + region.get("segment", "?"))
        if region.get("surrogate_si_sdr_millidb") != region.get(
                "identity_si_sdr_millidb") + region.get(
                "delta_si_sdr_millidb"):
            errors.append("paired SI-SDR arithmetic mismatch: "
                          + region.get("segment", "?"))
        if region.get("delta_snr_millidb") < -100:
            errors.append("surrogate degrades SNR beyond the fixture design: "
                          + region.get("segment", "?"))
    _eq(errors, "paired min SI-SDR",
        paired.get("min_surrogate_si_sdr_millidb"),
        min(region["surrogate_si_sdr_millidb"] for region in regions))
    _eq(errors, "paired min delta", paired.get("min_delta_si_sdr_millidb"),
        min(region["delta_si_sdr_millidb"] for region in regions))
    _eq(errors, "paired max SI-SDR",
        paired.get("max_surrogate_si_sdr_millidb"),
        max(region["surrogate_si_sdr_millidb"] for region in regions))
    _eq(errors, "paired mean delta",
        paired.get("mean_delta_si_sdr_millidb"),
        sum(region["delta_si_sdr_millidb"] for region in regions)
        // len(regions))
    _eq(errors, "paired no-degradation flag",
        paired.get("no_noisy_region_degraded"), True)
    if paired.get("qualifies") is not False:
        errors.append("paired metrics are promoted")

    clean = report["clean_preservation"]
    clean_regions = clean["regions"]
    _eq(errors, "clean region count", len(clean_regions), 2)
    for region in clean_regions:
        if region.get("qualifies") is not False:
            errors.append("clean region is promoted: "
                          + region.get("segment", "?"))
        if region.get("si_sdr_millidb", 0) <= 30000:
            errors.append("clean preservation SI-SDR is too low: "
                          + region.get("segment", "?"))
        if abs(region.get("level_change_millidb", 0)) >= 500:
            errors.append("clean level change is not small: "
                          + region.get("segment", "?"))
        if region.get("peak_milli", 1000) >= 1000:
            errors.append("clean peak exceeds the bound: "
                          + region.get("segment", "?"))
    _eq(errors, "clean min SI-SDR", clean.get("min_si_sdr_millidb"),
        min(region["si_sdr_millidb"] for region in clean_regions))
    _eq(errors, "clean max level change",
        clean.get("max_abs_level_change_millidb"),
        max(abs(region["level_change_millidb"]) for region in clean_regions))
    _eq(errors, "clean nonfinite count", clean.get("nonfinite_output_count"), 0)
    if clean.get("qualifies") is not False:
        errors.append("clean preservation is promoted")

    peaks = report["peaks_and_invalid"]
    _eq(errors, "peak bound", peaks.get("peak_bound_milli"), 1000)
    if peaks.get("max_peak_milli", 1000) >= 1000:
        errors.append("output peak exceeds the bound")
    _eq(errors, "clipped samples", peaks.get("clipped_samples"), 0)
    _eq(errors, "invalid outputs", peaks.get("invalid_output_count"), 0)
    _eq(errors, "nonfinite outputs", peaks.get("nonfinite_output_count"), 0)
    if peaks.get("qualifies") is not False:
        errors.append("peaks section is promoted")

    pause = report["pause_attenuation"]
    if pause.get("noise_attenuation_millidb", 0) <= 0:
        errors.append("pause attenuation is not positive")
    if pause.get("qualifies") is not False:
        errors.append("pause section is promoted")

    stoi = report["stoi"]
    _eq(errors, "STOI status", stoi.get("status"), "blocked")
    if stoi.get("value_millis") is not None:
        errors.append("STOI value is fabricated")
    if stoi.get("qualifies") is not False:
        errors.append("STOI section is promoted")

    baseline = report["baseline"]
    _eq(errors, "baseline status", baseline.get("status"), "blocked")
    if baseline.get("baseline_id") is not None:
        errors.append("baseline id is fabricated")
    if baseline.get("qualifies") is not False:
        errors.append("baseline section is promoted")

    alignment = report["alignment"]
    _eq(errors, "alignment delay",
        alignment.get("surrogate_content_delay_samples"), 0)
    _eq(errors, "alignment best shift", alignment.get("best_shift_samples"), 0)
    _eq(errors, "alignment zero-shift", alignment.get("zero_shift_best"), True)
    _eq(errors, "alignment probe count", len(alignment.get("probes", [])), 5)
    if alignment.get("candidate_alignment_documented") is not False:
        errors.append("candidate alignment is claimed")
    if alignment.get("qualifies") is not False:
        errors.append("alignment section is promoted")

    streaming = report["streaming"]
    _eq(errors, "streaming match", streaming.get("all_match"), True)
    _eq(errors, "streaming accepted", streaming.get("accepted_samples"),
        reference.FIXTURE_LENGTH)
    if streaming.get("scheduler_measured") is not False:
        errors.append("scheduler timing is claimed")
    if streaming.get("candidate_streaming") is not False:
        errors.append("candidate streaming is claimed")
    if streaming.get("qualifies") is not False:
        errors.append("streaming section is promoted")

    reset = report["reset"]
    _eq(errors, "reset fresh match", reset.get("matches_fresh"), True)
    if reset.get("qualifies") is not False:
        errors.append("reset section is promoted")

    partial = report["final_partial"]
    _eq(errors, "partial valid count", partial.get("valid_count"),
        reference.FINAL_PARTIAL_VALID)
    _eq(errors, "partial padding", partial.get("padding_zero"), True)
    _eq(errors, "partial tail", partial.get("tail_zero"), True)
    _eq(errors, "partial output samples", partial.get("output_samples"), 160)
    _eq(errors, "partial advance", partial.get("advanced_samples"),
        reference.FINAL_PARTIAL_VALID)
    if partial.get("qualifies") is not False:
        errors.append("final partial section is promoted")

    state = report["state_and_memory"]
    _eq(errors, "surrogate state bytes", state.get("surrogate_state_bytes"), 28)
    _eq(errors, "surrogate window", state.get("window_samples"), 160)
    _false(errors, state, ["memory_measured", "candidate_memory_measured",
                           "qualifies"], "state_and_memory")

    timing = report["runtime_timing"]
    _eq(errors, "timing status", timing.get("status"), "blocked_unmeasured")
    _false(errors, timing, ["candidate_content_delay_documented",
                            "availability_modeled", "wall_clock_measured",
                            "qualifies"], "runtime_timing")
    for key in ("real_time_factor", "deadline_ns"):
        if timing.get(key) is not None:
            errors.append("timing value is fabricated: " + key)

    listening = report["listening"]
    _eq(errors, "listening status", listening.get("status"), "not_run")
    _false(errors, listening, ["authorized", "qualifies"], "listening")
    if listening.get("result") is not None:
        errors.append("listening result is fabricated")

    nonfinite = report["nonfinite"]
    _eq(errors, "nonfinite output count",
        nonfinite.get("output_nonfinite_count"), 0)
    _eq(errors, "output finite", nonfinite.get("output_finite"), True)
    if nonfinite.get("rejected_nonfinite_inputs", 0) < 2:
        errors.append("nonfinite inputs were not both rejected")
    if nonfinite.get("qualifies") is not False:
        errors.append("nonfinite section is promoted")

    adverse = report["adverse_rejections"]
    if len(adverse) < 50:
        errors.append("adverse matrix is too small")
    if report.get("adverse_all_rejected") is not True:
        errors.append("adverse matrix is not all rejected")
    for case in adverse:
        if case.get("status") != "rejected":
            errors.append("adverse case was not rejected: "
                          + case.get("case_id", "?"))
        if case.get("state_unchanged") is not True:
            errors.append("adverse case advanced state: "
                          + case.get("case_id", "?"))
        if case.get("expected_code") != case.get("observed_code"):
            errors.append("adverse code mismatch: "
                          + case.get("case_id", "?"))

    controls = report["valid_controls"]
    _eq(errors, "valid controls accepted", controls.get("all_accepted"), True)
    if len(controls.get("cases", [])) != 3:
        errors.append("valid control count mismatch")
    if controls.get("qualifies") is not False:
        errors.append("valid controls are promoted")

    external = report["external_artifacts"]
    _eq(errors, "external artifacts present", external.get("any_present"), False)
    if any(external.get("present", {}).values()):
        errors.append("an external artifact path exists")

    licensing = report["licensing"]
    _eq(errors, "recorded licence",
        licensing.get("reported_upstream_license"), "CC-BY-NC-4.0")
    _eq(errors, "licence review", licensing.get("review_status"), "blocked")
    _eq(errors, "permitted scope", licensing.get("permitted_scope_here"),
        "research_evaluation_only")
    _false(errors, licensing, [
        "license_text_staged", "attribution_notice_staged",
        "weights_terms_staged", "training_data_statement_staged",
        "redistribution_reviewed", "product_use_reviewed",
        "generated_output_terms_staged", "commercial_use_permitted"],
        "licensing")
    if licensing.get("attribution_required") is not True:
        errors.append("attribution requirement is not recorded")

    scope = report["license_scope"]
    _eq(errors, "licence scope status", scope.get("status"), "blocked")
    _eq(errors, "licence permitted scope", scope.get("permitted_scope"),
        "research_evaluation_only")
    _false(errors, scope, ["commercial_or_product_use_permitted",
                           "redistribution_permitted", "qualifies"],
           "license_scope")
    _eq(errors, "licence rejection code", scope.get("rejection_code"),
        "license_scope_not_permitted")

    caller = report["caller_asset"]
    _eq(errors, "caller asset contract", caller.get("contract_id"),
        "audio-sdk/facebook-denoiser-dns48/caller-supplied-asset/0.1")
    _eq(errors, "caller asset status", caller.get("status"), "blocked")
    _false(errors, caller, ["asset_is_vendored", "manifest_present", "loaded",
                            "executed", "imported"], "caller_asset")
    _eq(errors, "caller asset required fields",
        caller.get("required_fields"), sorted(reference.CALLER_MANIFEST_FIELDS))

    _false(errors, report["boundary"], list(report["boundary"]), "boundary")
    _eq(errors, "scope synthetic", report["scope"].get("synthetic_only"), True)
    _eq(errors, "scope task-local", report["scope"].get("task_local_only"), True)
    for key, value in report["scope"].items():
        if key not in {"synthetic_only", "task_local_only"} and value is not False:
            errors.append("scope claims true: " + key)

    surrogate = report["surrogate"]
    _false(errors, surrogate, [
        "is_facebook_denoiser", "is_demucs", "is_learned", "uses_network",
        "uses_weight_file", "uses_convolution", "uses_quantization",
        "uses_float_arithmetic_in_signal_path", "is_generative",
        "qualifies_candidate"], "surrogate")

    repeat = report["repeatability"]
    _eq(errors, "repeat runs", repeat.get("runs"), 3)
    _eq(errors, "repeat identity", repeat.get("byte_identical"), True)
    if len(repeat.get("case_matrix_digests", [])) != 3:
        errors.append("case matrix digest count mismatch")
    elif len(set(repeat["case_matrix_digests"])) != 1:
        errors.append("case matrix digests differ")


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: "
                      + ", ".join(sorted(missing)))
        return
    _eq(errors, "contract task", contract.get("task"), reference.TASK_ID)
    _eq(errors, "contract decision", contract.get("decision"), "DEFER")
    _eq(errors, "contract evidence status", contract.get("evidence_status"),
        "incomplete")
    _eq(errors, "contract qualification", contract.get("qualification_status"),
        "not_qualified")
    _eq(errors, "contract profile", contract.get("profile"), "enhancement")
    _eq(errors, "contract verification profile",
        contract.get("verification_profile"), "enhancement")
    _eq(errors, "contract base commit", contract.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract.get("branch"), reference.BRANCH)
    _eq(errors, "contract task prefix", contract.get("task_prefix"),
        reference.TASK_PREFIX)
    _eq(errors, "contract reviewer", contract.get("reviewer"),
        reference.REVIEWER)
    if len(contract.get("invariants", [])) != 10:
        errors.append("contract invariant count mismatch")
    if len(contract.get("release_gates", [])) != 8:
        errors.append("contract release gate count mismatch")
    if any(gate.get("status") != "blocked"
           for gate in contract.get("release_gates", [])):
        errors.append("contract release gate is not blocked")
    caller = contract.get("caller_asset_contract", {})
    _eq(errors, "contract caller asset",
        caller.get("contract_id"),
        "audio-sdk/facebook-denoiser-dns48/caller-supplied-asset/0.1")
    _false(errors, caller, ["asset_is_vendored"], "caller_asset_contract")
    _eq(errors, "contract caller fields", caller.get("required_fields"),
        sorted(reference.CALLER_MANIFEST_FIELDS))

    pins = contract.get("artifact_pins", {})
    for name in reference.ARTIFACT_FILES:
        path = reference.TASK_PREFIX + name
        if path not in pins:
            errors.append("artifact pin missing: " + path)
            continue
        full = reference.SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact file missing: " + path)
            continue
        if name == "report.json":
            digest = reference.file_digest(REPORT)
        elif name == "report.json.sha256":
            digest = reference.file_digest(SIDECAR)
        else:
            digest = reference.file_digest(full)
        if pins[path] != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256"):
        if reference.TASK_PREFIX + forbidden in pins:
            errors.append("self-referential artifact pin: " + forbidden)

    if report:
        for section in ("acceptance_profile", "candidate", "format",
                        "licensing", "license_scope", "board_row", "boundary",
                        "boundary_pins", "source_pins", "scope", "reference",
                        "exact_blockers", "release_gates", "negative_claims"):
            _eq(errors, "contract/report mismatch: " + section,
                contract.get(section), report.get(section))


def check_repeats(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    texts = []
    for _ in range(3):
        built = reference.build_report()
        text, _ = reference.canonical_report(built)
        texts.append(text)
    if len(set(texts)) != 1:
        errors.append("three fresh report builds differ")
    if texts and texts[0].encode("utf-8") != REPORT.read_bytes():
        errors.append("fresh build does not match report.json")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md is missing its SPDX header")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing license sidecar: " + name)
            continue
        content = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in content or SPDX_COPYRIGHT not in content:
            errors.append("invalid license sidecar: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or (
            'SPDX' '-License-Identifier = "Apache-2.0"') not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "not Facebook Denoiser", "enhancement", "paired",
                  "CC-BY-NC", "16 kHz", "blocked", "48"):
        if token not in text:
            errors.append("README is missing token: " + token)
    for digest in (list(reference.SOURCE_PINS.values())
                   + list(reference.BOUNDARY_PINS.values())):
        if digest not in text:
            errors.append("README is missing pinned digest: " + digest)
    if report:
        for token in (reference.BASE_COMMIT, reference.TASK_ID):
            if token not in text:
                errors.append("README is missing identity: " + token)


def check_text_hygiene(errors: List[str]) -> None:
    for name in TEXT_ARTIFACTS:
        path = HERE / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            errors.append("missing text artifact: " + name)
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if line != line.rstrip():
                errors.append(f"trailing whitespace: {name}:{number}")
            if "\t" in line:
                errors.append(f"tab character: {name}:{number}")
        if not text.endswith("\n"):
            errors.append("missing final newline: " + name)


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: "
                      + diff_check.stdout.strip())
    reference_text = (HERE / "reference.py").read_text(encoding="utf-8")
    for token in ("import torch", "import urllib", "import requests",
                  "import socket", "import http", "from_pretrained",
                  "torch.hub"):
        if token in reference_text:
            errors.append("reference.py contains network/model token: "
                          + token)
    return changed


def main() -> int:
    errors: List[str] = []
    loaded = check_json_files(errors)
    report = loaded.get("report", {})
    contract = loaded.get("contract", {})
    pin_count = check_pins(errors)
    check_report(errors, report)
    check_contract(errors, contract, report)
    if report and contract:
        check_board(errors, report, contract)
    check_repeats(errors, report)
    check_readme(errors, report)
    check_licensing(errors)
    check_text_hygiene(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256="
          f"{reference.file_digest(REPORT)} repeats_ok=3 "
          f"licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
