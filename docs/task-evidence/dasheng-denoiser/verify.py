# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DASHENG-DENOISER package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-enhancement profile, a promoted metric, a fabricated STOI,
baseline or candidate geometry, a qualified claim, an open release gate,
license gaps, out-of-scope worktree changes, whitespace damage or a dirty
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
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "evidence_status", "profile", "acceptance_profile", "profile_blockers",
    "candidate", "reference", "format", "fixtures", "paired_metrics",
    "clean_preservation", "peaks_and_invalid", "pause_attenuation", "stoi",
    "baseline", "alignment", "streaming", "reset", "final_partial",
    "state_and_memory", "runtime_timing", "listening", "nonfinite",
    "adverse_rejections", "adverse_all_rejected", "external_artifacts",
    "licensing", "caller_asset", "board_row", "boundary", "boundary_pins",
    "source_pins", "scope", "qualification", "exact_blockers",
    "release_gates", "reopen_condition", "negative_claims", "surrogate",
    "repeatability", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile", "candidate",
    "format", "licensing", "artifact_pins", "board_row", "boundary",
    "boundary_pins", "source_pins", "scope", "reference", "exact_blockers",
    "release_gates", "reopen_condition", "negative_claims",
    "caller_asset_contract", "invariants",
}
PROFILE_ITEMS = {
    "identity_noisy_control", "task_matched_baseline", "paired_si_sdr",
    "paired_stoi", "clean_speech_preservation", "peaks_and_invalid_outputs",
    "unpaired_predictive_screen_or_listening", "alignment_content_mapping",
    "runtime_availability_timing", "streaming_state_and_reset",
    "runtime_memory", "task_matched_heldout_qualification",
}


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
        errors.append(label)


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
        if SIDECAR.read_text(encoding="ascii") != digest + "\n":
            errors.append("report.json.sha256 is stale")
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
    return count


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    live = reference.board_row()
    _eq(errors, "report board identity is stale", report.get("board_row"), live)
    _eq(errors, "contract board identity is stale", contract.get("board_row"), live)
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
    _false(errors, qualification, [
        "qualifies", "all_required_results_present", "missing_result_promoted",
        "exact_source_present", "exact_weights_present",
        "exact_runtime_outputs_present", "checkpoint_lineage_verified",
        "rights_cleared_cohort", "geometry_documented",
        "paired_control_qualified", "baseline_qualified", "si_sdr_qualified",
        "stoi_qualified", "clean_preservation_qualified", "peaks_validated",
        "alignment_qualified", "timing_measured", "memory_measured",
        "hallucination_checked", "listening", "real_corpus_used"],
        "qualification")

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
    if "streaming_state_and_reset" not in expected_blockers:
        errors.append("offline candidate streaming is not blocked")

    candidate = report["candidate"]
    _eq(errors, "candidate parameter count",
        candidate.get("reported_parameter_count"), 100000000)
    _eq(errors, "candidate reported rate",
        candidate.get("reported_input_sample_rate_hz"), 16000)
    _eq(errors, "candidate offline flag",
        candidate.get("reported_offline_whole_utterance"), True)
    for key in ("reported_hop_samples", "reported_frame_samples",
                "reported_algorithmic_latency_samples"):
        if candidate.get(key) is not None:
            errors.append("candidate geometry is fabricated: " + key)
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
    _eq(errors, "surrogate block lookahead",
        fmt.get("surrogate_block_lookahead_samples"), 160)
    _eq(errors, "candidate reported rate",
        fmt.get("candidate_reported_sample_rate_hz"), 16000)
    _eq(errors, "candidate offline flag",
        fmt.get("candidate_offline_whole_utterance"), True)
    _eq(errors, "surrogate streaming flag",
        fmt.get("surrogate_streaming_supported"), False)
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

    if len(report["exact_blockers"]) != 6:
        errors.append("expected six exact blockers")

    paired = report["paired_metrics"]
    regions = paired["regions"]
    _eq(errors, "paired region count", len(regions), 3)
    for region in regions:
        if region.get("qualifies") is not False:
            errors.append("paired region is promoted: " + region.get("segment", "?"))
        if region.get("surrogate_si_sdr_millidb") != region.get(
                "identity_si_sdr_millidb") + region.get(
                "delta_si_sdr_millidb"):
            errors.append("paired SI-SDR arithmetic mismatch: "
                          + region.get("segment", "?"))
        if region.get("delta_snr_millidb") < -100:
            errors.append("surrogate degrades SNR beyond the fixture design: "
                          + region.get("segment", "?"))
    _eq(errors, "paired min SI-SDR", paired.get("min_surrogate_si_sdr_millidb"),
        min(region["surrogate_si_sdr_millidb"] for region in regions))
    _eq(errors, "paired min delta", paired.get("min_delta_si_sdr_millidb"),
        min(region["delta_si_sdr_millidb"] for region in regions))
    _eq(errors, "paired no-degradation flag",
        paired.get("no_noisy_region_degraded"), True)

    clean = report["clean_preservation"]
    clean_regions = clean["regions"]
    _eq(errors, "clean region count", len(clean_regions), 2)
    for region in clean_regions:
        if region.get("qualifies") is not False:
            errors.append("clean region is promoted: " + region.get("segment", "?"))
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
    _eq(errors, "clean nonfinite count", clean.get("nonfinite_output_count"), 0)

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
        errors.append("baseline is fabricated")
    if baseline.get("qualifies") is not False:
        errors.append("baseline section is promoted")

    alignment = report["alignment"]
    _eq(errors, "alignment content delay",
        alignment.get("surrogate_content_delay_samples"), 0)
    _eq(errors, "alignment best shift", alignment.get("best_shift_samples"), 0)
    _eq(errors, "alignment zero-shift flag", alignment.get("zero_shift_best"),
        True)
    _eq(errors, "alignment probe count", len(alignment.get("probes", [])), 5)
    _eq(errors, "alignment candidate flag",
        alignment.get("candidate_alignment_documented"), False)
    if alignment.get("qualifies") is not False:
        errors.append("alignment is promoted")

    streaming = report["streaming"]
    _eq(errors, "streaming status", streaming.get("status"),
        "synthetic_surrogate_only")
    _eq(errors, "streaming match", streaming.get("all_match"), True)
    _eq(errors, "streaming accepted", streaming.get("accepted_samples"), 12000)
    _eq(errors, "streaming chunk sum", sum(streaming.get("chunks", [])), 12000)
    _eq(errors, "streaming scheduler", streaming.get("scheduler_measured"), False)
    _eq(errors, "candidate streaming", streaming.get("candidate_streaming"),
        False)
    if streaming.get("qualifies") is not False:
        errors.append("streaming is promoted")

    reset = report["reset"]
    _eq(errors, "reset freshness", reset.get("matches_fresh"), True)
    _eq(errors, "reset epoch", reset.get("epoch"), 2)

    partial = report["final_partial"]
    _eq(errors, "final partial valid count", partial.get("valid_count"), 137)
    _eq(errors, "final partial output count", partial.get("output_samples"), 160)
    _eq(errors, "final partial advance", partial.get("advanced_samples"), 137)
    _eq(errors, "final partial padding", partial.get("padding_zero"), True)
    _eq(errors, "final partial tail", partial.get("tail_zero"), True)

    state = report["state_and_memory"]
    _eq(errors, "surrogate state bytes", state.get("surrogate_state_bytes"), 32)
    _eq(errors, "surrogate window", state.get("window_samples"), 160)
    _eq(errors, "lookahead declared", state.get("lookahead_stated"), True)
    _false(errors, state, ["memory_measured", "candidate_memory_measured"],
           "state_and_memory")
    if state.get("qualifies") is not False:
        errors.append("state section is promoted")

    timing = report["runtime_timing"]
    _eq(errors, "timing status", timing.get("status"), "blocked_unmeasured")
    if timing.get("real_time_factor") is not None:
        errors.append("RTF is fabricated")
    if timing.get("deadline_ns") is not None:
        errors.append("deadline is fabricated")
    _false(errors, timing, ["availability_modeled", "wall_clock_measured",
                            "candidate_content_delay_documented"],
           "runtime_timing")
    if timing.get("qualifies") is not False:
        errors.append("timing section is promoted")

    listening = report["listening"]
    _eq(errors, "listening status", listening.get("status"), "not_run")
    _false(errors, listening, ["authorized"], "listening")
    if listening.get("result") is not None:
        errors.append("listening result is fabricated")

    nonfinite = report["nonfinite"]
    _eq(errors, "nonfinite output count",
        nonfinite.get("output_nonfinite_count"), 0)
    _eq(errors, "output finite", nonfinite.get("output_finite"), True)
    _eq(errors, "rejected nonfinite inputs",
        nonfinite.get("rejected_nonfinite_inputs"), 2)

    adverse = report["adverse_rejections"]
    expected_cases = reference.adverse_rejections()
    _eq(errors, "adverse rejection count", len(adverse), len(expected_cases))
    _eq(errors, "adverse rejection flag", report.get("adverse_all_rejected"),
        True)
    for item in adverse:
        if item.get("status") != "rejected":
            errors.append("adverse case not rejected exactly: "
                          + item.get("case_id", "?"))
        if item.get("expected_code") != item.get("observed_code"):
            errors.append("adverse code mismatch: " + item.get("case_id", "?"))
        if item.get("state_unchanged") is not True:
            errors.append("adverse case changed state: "
                          + item.get("case_id", "?"))

    external = report["external_artifacts"]
    _eq(errors, "external artifact status", external.get("status"), "blocked")
    _eq(errors, "external artifact presence", external.get("any_present"),
        False)

    licensing = report["licensing"]
    if licensing.get("reported_upstream_license") is not None:
        errors.append("an upstream license is asserted")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    _false(errors, licensing, [
        "license_text_staged", "attribution_notice_staged",
        "weights_terms_staged", "training_data_statement_staged",
        "redistribution_reviewed", "product_use_reviewed",
        "generated_output_terms_staged"], "licensing")

    surrogate = report["surrogate"]
    _false(errors, surrogate, [
        "is_dasheng", "is_learned", "uses_network", "uses_weight_file",
        "uses_quantization", "uses_float_arithmetic_in_signal_path",
        "is_generative", "qualifies_candidate"], "surrogate")

    repeat = report["repeatability"]
    _eq(errors, "repeatability runs", repeat.get("runs"), 3)
    _eq(errors, "repeatability byte identity", repeat.get("byte_identical"),
        True)
    digests = repeat.get("case_matrix_digests", [])
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("case-matrix repeat digests differ")

    boundary = report["boundary"]
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("a boundary flag claims a change")
    scope = report["scope"]
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("scope flag is not false: " + key)

    text = reference.canonical_text(report)
    if '"qualifies":true' in text or '"status":"qualified"' in text:
        errors.append("canonical report contains a qualified claim")
    if "TASKS.json" in reference.canonical_text(report["source_pins"]):
        errors.append("mutable task board appears in source pins")


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected contract schema", contract["schema_id"],
        reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract["task"], reference.TASK_ID)
    _eq(errors, "contract component", contract["component"],
        reference.COMPONENT)
    _eq(errors, "contract base commit", contract["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract["branch"], reference.BRANCH)
    _eq(errors, "contract decision", contract["decision"], "DEFER")
    _eq(errors, "contract evidence status", contract["evidence_status"],
        "incomplete")
    _eq(errors, "contract qualification", contract["qualification_status"],
        "not_qualified")
    _eq(errors, "contract verification profile",
        contract["verification_profile"], "enhancement")
    _eq(errors, "contract/report release gates differ",
        contract.get("release_gates"), report.get("release_gates"))
    _eq(errors, "contract/report blockers differ",
        contract.get("exact_blockers"), report.get("exact_blockers"))
    _eq(errors, "contract/report source pins differ",
        contract.get("source_pins"), report.get("source_pins"))
    _eq(errors, "contract/report boundary pins differ",
        contract.get("boundary_pins"), report.get("boundary_pins"))
    _eq(errors, "contract/report candidate differ",
        contract.get("candidate"), report.get("candidate"))
    _eq(errors, "contract/report format differ",
        contract.get("format"), report.get("format"))
    _eq(errors, "contract/report licensing differ",
        contract.get("licensing"), report.get("licensing"))

    boundary = contract.get("boundary", {})
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("contract boundary flag claims a change")
    scope = contract.get("scope", {})
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("contract scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("contract scope flag is not false: " + key)

    pins = contract.get("artifact_pins", {})
    expected_names = {reference.TASK_PREFIX + name
                      for name in reference.ARTIFACT_FILES}
    if set(pins) != expected_names:
        errors.append("artifact pin set mismatch")
    for path, digest in pins.items():
        full = SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact pin missing: " + path)
        elif reference.file_digest(full) != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256"):
        if reference.TASK_PREFIX + forbidden in pins:
            errors.append("self-referential artifact pin: " + forbidden)


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
                  "not Dasheng", "enhancement", "paired", "100M", "16 kHz",
                  "offline", "blocked"):
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
        errors.append("git diff --check failed: " + diff_check.stdout.strip())
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
