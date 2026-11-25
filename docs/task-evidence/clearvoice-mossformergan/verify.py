# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-CLEARVOICE-MOSSFORMERGAN package.

Usage::

    SOURCE_ROOT=/path/to/workspace PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins, stale
digests, a stale README digest table, disposition drift, a promoted missing
result, licensing gaps, vendored assets, out-of-scope worktree changes,
whitespace damage or a dirty diff check. Never writes.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = reference.TASK_PREFIX
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
READINESS = HERE / "readiness.json"
ADAPTER = HERE / "adapter.json"
README = HERE / "README.md"

SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_COPYRIGHT}\n{SPDX_LICENSE}\n"
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".lock", ".license"}

EXPECTED_REASONS = [
    "model_revision_unpinned",
    "download_revision_unrecorded",
    "pointer_artifact_unverified",
    "asset_bytes_absent",
    "runtime_unavailable",
    "rights_not_cleared",
]
EXPECTED_GATES = {
    "exact_asset_identity", "runtime_admission", "artifact_rights",
    "exact_reference_parity", "rights_cleared_cohort",
    "independent_scoring_and_listening", "target_runtime_timing",
    "provider_intake", "public_default_selection",
}
EXPECTED_CONFIG_CASES = {
    "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
    "wrong_model_name", "wrong_package_version", "mode_unsupported",
    "surrogate_without_opt_in", "caller_asset_unavailable",
    "caller_asset_wrong_checkpoint_sha", "caller_asset_admission_control",
}
EXPECTED_FRAME_CASES = {
    "empty_chunk", "oversized_chunk", "nonfinite_sample", "infinite_sample",
    "string_chunk", "boolean_sample", "out_of_range_sample",
    "process_after_finish", "finish_after_finish", "process_after_close",
    "finish_after_close", "reset_after_close",
}
EXPECTED_VARIANTS = {
    "identity_passthrough", "noisy_control",
    "surrogate_offline_chunked_160", "surrogate_offline_whole_clip",
}
BINARY_SUFFIXES = (
    ".dylib", ".so", ".dll", ".onnx", ".tar", ".gz", ".ckpt", ".pt",
    ".pth", ".safetensors", ".wav", ".flac", ".mp3", ".npy", ".npz",
)


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def strict_json(path: Path) -> Dict[str, Any]:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        fail("strict JSON failed for " + path.name + ": " + str(error))


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def read_manifest() -> Dict[str, str]:
    try:
        text = PINS.read_text(encoding="ascii")
    except (OSError, UnicodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    try:
        pairs = reference.parse_pin_lines(text)
    except (ValueError, TypeError) as error:
        fail("strict pin rejection: " + str(error))
    return {raw: digest for digest, raw in pairs}


def check_pins(manifest: Dict[str, str]) -> int:
    expected = reference.allowed_pin_keys()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if PINS.read_bytes() != reference.sources_bytes():
        fail("SOURCES.sha256 is not deterministic bytes")
    for raw, digest in sorted(manifest.items()):
        path = reference.qualify_pin_path(raw)
        if not path.is_file() or path.is_symlink():
            fail("missing or non-regular pin target: " + raw)
        if reference.sha256_file(path) != digest:
            fail("pin mismatch: " + raw)
    return len(manifest)


def check_readme_digest_table() -> int:
    if not README.is_file():
        fail("README.md missing")
    rows = reference.readme_pin_rows()
    if not rows:
        fail("README digest table missing")
    seen: Dict[str, str] = {}
    for path, digest in rows:
        if path in seen:
            fail("README duplicate row: " + path)
        seen[path] = digest
        if (path.startswith(TASK_PREFIX) or path.startswith("worktree:")
                or path.startswith("source:") or path.startswith("/")
                or ":" in path):
            fail("README row must be a plain external path: " + path)
        target = reference.qualify_pin_path(path)
        if not target.is_file() or target.is_symlink():
            fail("README row target missing: " + path)
        if reference.sha256_file(target) != digest:
            fail("README row digest stale: " + path)
    if set(seen) != set(reference.SOURCE_PINS):
        fail("README digest row set mismatch: missing="
             + str(sorted(set(reference.SOURCE_PINS) - set(seen)))
             + " extra=" + str(sorted(set(seen) - set(reference.SOURCE_PINS))))
    for path, digest in reference.SOURCE_PINS.items():
        if seen[path] != digest:
            fail("README row disagrees with SOURCE_PINS: " + path)
    return len(rows)


def check_json() -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": strict_json(CONTRACT),
        "report": strict_json(REPORT),
        "adapter": strict_json(ADAPTER),
        "readiness": strict_json(READINESS),
    }
    for name, path in (("contract", CONTRACT), ("report", REPORT),
                       ("adapter", ADAPTER), ("readiness", READINESS)):
        check_finite(payloads[name], name)
        if reference.has_negative_zero(payloads[name]):
            fail("negative zero in artifact: " + name)
    if CONTRACT.read_bytes() != reference.contract_bytes():
        fail("contract.json is not canonical/reproducible")
    if REPORT.read_bytes() != reference.canonical_report_bytes(payloads["report"]):
        fail("report.json is not canonical/reproducible")
    if ADAPTER.read_bytes() != reference.adapter_bytes():
        fail("adapter.json is not canonical/reproducible")
    if READINESS.read_bytes() != reference.readiness_bytes():
        fail("readiness.json is not canonical/reproducible")
    report_digest = reference.sha256(REPORT.read_bytes())
    if SIDECAR.read_bytes() != f"{report_digest}  report.json\n".encode("ascii"):
        fail("report.json.sha256 is stale")
    contract_digest = reference.sha256(CONTRACT.read_bytes())
    if payloads["report"].get("contract_sha256") != contract_digest:
        fail("report contract digest mismatch")
    if payloads["readiness"].get("report_sha256") != report_digest:
        fail("readiness report digest mismatch")
    if payloads["readiness"].get("contract_sha256") != contract_digest:
        fail("readiness contract digest mismatch")
    return payloads


def _near(value: Any, expected: float, tolerance: float = 1e-5) -> bool:
    return isinstance(value, (int, float)) and abs(float(value) - expected) <= tolerance


def check_disposition(contract: Dict[str, Any], adapter: Dict[str, Any],
                      readiness: Dict[str, Any]) -> None:
    for name, document in (("contract", contract), ("adapter", adapter),
                           ("readiness", readiness)):
        if document.get("decision") != reference.DECISION:
            fail(name + " decision is not DEFER")
    if contract.get("status") != reference.STATUS:
        fail("contract status mismatch")
    if contract.get("evidence_status") != reference.EVIDENCE_STATUS:
        fail("contract evidence status mismatch")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("contract qualification status mismatch")
    qualification = contract["qualification"]
    required = {
        "status": reference.EVIDENCE_STATUS,
        "decision": reference.DECISION,
        "qualifies": False,
        "missing_result_promoted": False,
        "processor_exposure": False,
        "real_runtime_used": False,
        "quality_claim": False,
        "release_claim": False,
    }
    if any(qualification.get(key) != value for key, value in required.items()):
        fail("contract qualification is not incomplete/DEFER")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("public surface flag is not false")
    required_false = {
        key: value for key, value in reference.BOUNDARY.items()
        if key not in ("descriptor_settings", "installed_v0_geometry_preserved")}
    if any(value is not False for value in required_false.values()):
        fail("boundary flag is not false")
    if reference.BOUNDARY["descriptor_settings"] != {}:
        fail("descriptor settings are not empty")
    if contract["boundary"] != reference.BOUNDARY:
        fail("contract boundary differs from the frozen boundary")
    if contract["offline_boundary"] != reference.OFFLINE_BOUNDARY:
        fail("contract offline boundary differs")
    if adapter["registration"] != {
        "registered": False, "enabled_by_default": False,
        "default_selected": False, "descriptor_registry_change": False,
        "public_api_abi_change": False,
    }:
        fail("adapter registration block is not fail-closed")
    for key in ("implemented", "registered", "enabled_by_default",
                "default_selected", "public_api_abi_change",
                "provider_registration", "descriptor_registry_change",
                "installed_v0_behavior_change", "real_runtime_used",
                "weights_accessed", "attention_or_gan_executed", "quality_claim"):
        if adapter.get(key) is not False:
            fail("adapter claim flag is not false: " + key)
    if adapter.get("descriptor_settings") != {}:
        fail("adapter descriptor settings are not empty")
    if adapter.get("asset_readiness") != "blocked":
        fail("adapter reports a ready asset")
    if adapter.get("modes") != ["offline"]:
        fail("adapter mode is not the offline boundary")
    if adapter.get("tasks") != ["CLN-01"]:
        fail("adapter task is not CLN-01")
    if adapter.get("entrypoint") != [
            "python", "docs/task-evidence/" + reference.SLUG + "/reference.py"]:
        fail("adapter entrypoint is not the task-local reference")
    if readiness["status"] != "blocked" or readiness["qualified"] is not False:
        fail("readiness is not blocked/not qualified")
    for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                "ready_for_release", "quality_pass", "processor_exposure"):
        if readiness.get(key) is not False:
            fail("readiness claim is not false: " + key)
    if readiness["admission"]["status"] != "blocked":
        fail("readiness admission is not blocked")
    if readiness["admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("readiness reason codes drifted")
    for key in ("download_attempted", "vendor_runtime_invoked", "asset_bytes_read"):
        if readiness["admission"][key] is not False:
            fail("readiness admission performed a forbidden action: " + key)
    if readiness["blocked_gates"] != [gate["name"] for gate in reference.GATES]:
        fail("readiness blocked gate list mismatch")
    if readiness["exact_blocker"] != reference.EXACT_BLOCKERS[0]:
        fail("readiness exact blocker mismatch")
    if readiness["reopen_condition"] != reference.REOPEN_CONDITIONS[0]:
        fail("readiness reopen condition mismatch")
    for token in ("not ready", "clearvoice 0.1.2",
                  "no immutable model artifact revision",
                  "pointer content is unverified"):
        if token not in readiness["readiness_conclusion"]:
            fail("readiness conclusion is missing: " + token)
    print("verify: contract, adapter and readiness are blocked/DEFER and OFF")


def check_report(report: Dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT:
        fail("report base commit mismatch")
    if report["branch"] != reference.BRANCH:
        fail("report branch mismatch")
    if report["task_id"] != reference.TASK:
        fail("report task mismatch")
    if report["component"] != reference.COMPONENT or report["slug"] != reference.SLUG:
        fail("report component or slug mismatch")
    if report["profile"] != reference.PROFILE:
        fail("report profile mismatch")
    for key, expected in (
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION_STATUS),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        if report.get(key) != expected:
            fail("report disposition mismatch: " + key)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("missing-result qualification guard is absent")
    if report["format"] != reference.FORMAT:
        fail("installed v0 geometry mismatch")
    if report["boundary"] != reference.BOUNDARY:
        fail("report boundary mismatch")
    if report["offline_boundary"] != reference.OFFLINE_BOUNDARY:
        fail("report offline boundary mismatch")
    for key in ("task_local_only", "synthetic_boundary_surrogate_only",
                "caller_supplied_asset_contract_modeled"):
        if report["scope"].get(key) is not True:
            fail("scope true flag missing: " + key)
    for key in ("caller_supplied_asset_present",
                "checkpoint_present_in_sdk_worktree",
                "pointer_present_in_sdk_worktree", "model_revision_pinned",
                "runtime_installed", "clearvoice_source_executed",
                "weights_downloaded", "weights_loaded", "attention_or_gan_executed",
                "real_audio", "real_labels", "network_used", "device_timing",
                "listening_result", "benchmark_claim", "release_claim",
                "registered_provider"):
        if report["scope"].get(key) is not False:
            fail("scope claim is not false: " + key)
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")
    surrogate = report["surrogate"]
    if surrogate.get("identity") != "mossformergan-offline-boundary-surrogate-v0":
        fail("surrogate identity mismatch")
    for key in ("is_candidate", "is_neural_network", "attention_blocks",
                "gan_generator_or_discriminator", "weights", "checkpoint",
                "vendor_runtime", "quality_claim"):
        if surrogate.get(key) is not False:
            fail("surrogate claim is not false: " + key)
    if surrogate.get("deterministic") is not True:
        fail("surrogate is not marked deterministic")
    if report["stimuli"]["conditions"] != list(reference.CONDITIONS):
        fail("stimuli condition list mismatch")
    for key in ("real_audio", "real_labels", "network"):
        if report["stimuli"].get(key) is not False:
            fail("stimuli claim is not false: " + key)

    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for name, block in report["conditions"].items():
        tail = block["tail_validity"]
        if tail["output_samples"] != tail["input_samples"]:
            fail("output length is not the input length in " + name)
        if tail["valid_samples"] != tail["input_samples"]:
            fail("valid sample accounting mismatch in " + name)
        if tail["internal_frame_padding_samples"] != (
                (-tail["input_samples"]) % reference.FRAME_SAMPLES):
            fail("internal frame padding mismatch in " + name)
        if tail["padded_samples_emitted"] != 0:
            fail("padding was emitted in " + name)
        if tail["delay_compensation_samples"] != 0:
            fail("delay compensation is not zero in " + name)
        if tail["source_time_mapping"] != "identity":
            fail("source time mapping is not identity in " + name)
        if block["scored_samples"] != tail["input_samples"]:
            fail("scored sample count mismatch in " + name)
        if block["whole_clip_matches_chunked"] is not True:
            fail("whole clip does not match the chunked feed in " + name)
        if block["chunk_invariance_digest"] != block["whole_clip_output_digest"]:
            fail("chunk and whole-clip digests differ in " + name)
        variants = block["variants"]
        if set(variants) != EXPECTED_VARIANTS:
            fail("variant set mismatch in " + name)
        for variant in variants.values():
            if variant["nonfinite_samples"] != 0:
                fail("nonfinite output in condition " + name)
            if variant["clipped_samples"] != 0:
                fail("clipped output in condition " + name)
            if not math.isfinite(variant["peak_abs_output"]):
                fail("nonfinite peak in " + name)
            if variant["peak_abs_output"] > reference.PEAK_LIMIT:
                fail("output peak exceeds the fixture limit in " + name)
            if variant["scored_samples"] != tail["input_samples"]:
                fail("variant scored samples mismatch in " + name)
            for metric in ("snr_db", "si_sdr_db", "stoi"):
                entry = variant[metric]
                if entry["valid"] is True and entry["value"] is None:
                    fail("valid metric has no value: " + name + ":" + metric)
                if entry["valid"] is False and not entry["invalid_reason"]:
                    fail("invalid metric has no reason: " + name + ":" + metric)
        identity = variants["identity_passthrough"]
        noisy = variants["noisy_control"]
        if identity["exact_passthrough"] is not True:
            fail("identity control is not exact in " + name)
        for metric in ("snr_db", "si_sdr_db", "stoi"):
            if identity[metric] != noisy[metric]:
                fail("identity and noisy controls differ in " + name + ":" + metric)
        candidate = variants["surrogate_offline_chunked_160"]
        for metric in ("snr_db", "si_sdr_db", "stoi"):
            expected = None
            if candidate[metric]["value"] is not None and noisy[metric]["value"] is not None:
                expected = reference.norm(
                    candidate[metric]["value"] - noisy[metric]["value"])
            if block["improvements"][metric] != expected:
                fail("improvement arithmetic mismatch in " + name + ":" + metric)
        if noisy["output_rms"] > 0.0:
            expected_gain = reference.norm(candidate["output_rms"] / noisy["output_rms"])
            if block["preservation"]["rms_gain_ratio"] != expected_gain:
                fail("rms gain ratio mismatch in " + name)
            expected_atten = reference.norm(
                reference._db((candidate["output_rms"] / noisy["output_rms"]) ** 2))
            if block["noise_attenuation_db"] != expected_atten:
                fail("noise attenuation mismatch in " + name)
        if block["reference"] == "zero_reference":
            for metric in ("snr_db", "si_sdr_db", "stoi"):
                if candidate[metric]["valid"] is not False:
                    fail("zero-reference condition was scored as speech: "
                         + name + ":" + metric)
        projection = block["preservation"]
        if projection["target_retention"] is None and projection[
                "target_projection_snr_reason"] not in (
                    "zero_reference_energy", "zero_error_identity_exact"):
            fail("projection missing without reason in " + name)
        expected_projection_delta = None
        if (projection["target_projection_snr_db"] is not None
                and projection["identity_target_projection_snr_db"] is not None):
            expected_projection_delta = reference.norm(
                projection["target_projection_snr_db"]
                - projection["identity_target_projection_snr_db"])
        if projection["target_projection_snr_delta_db"] != expected_projection_delta:
            fail("projection delta mismatch in " + name)

    if report["regressions"] != reference._regressions(report["conditions"]):
        fail("regressions are not recomputable")
    if not report["regressions"]:
        fail("no synthetic regression was recorded")
    for item in report["regressions"]:
        if item["metric"] not in ("snr_db", "si_sdr_db", "stoi"):
            fail("unknown regression metric")
        if item["surrogate_value"] >= item["control_value"]:
            fail("recorded regression is not a regression")
    if report["comparison"]["regression_count"] != len(report["regressions"]):
        fail("regression count mismatch")
    for key in ("established_task_matched_baseline_reproduced",
                "source_reported_used_for_qualification", "real_cohort_scored",
                "quality_pass"):
        if report["comparison"].get(key) is not False:
            fail("comparison claim is not false: " + key)

    boundary = report["offline_processing"]
    if boundary["declared_algorithmic_lag_samples"] != 0:
        fail("declared lag is not zero")
    if boundary["declared_algorithmic_lag_ns"] != 0:
        fail("declared lag nanoseconds are not zero")
    if boundary["lag_measured_here"] is not False:
        fail("lag is claimed as measured")
    if boundary["lag_modeled_in_fixture"] is not True:
        fail("lag is not marked modelled")
    if boundary["clock_id"] != reference.CLOCK_ID:
        fail("fixture clock identity mismatch")
    if boundary["upstream_config_fields"] != list(reference.CALLER_CONFIG_FIELDS):
        fail("upstream config fields mismatch")
    if boundary["pointer_requirement"]["required_content"] != reference.POINTER_REQUIRED_CONTENT:
        fail("pointer requirement mismatch")
    if boundary["pointer_requirement"]["content_verified_here"] is not False:
        fail("pointer is claimed as verified")
    cross = boundary["chunk_invariance"]
    if not cross["output_chunk_invariant"] or not cross["whole_call_matches_chunked"]:
        fail("chunk invariance failed")
    if set(cross["chunk_sizes_tested"]) != set(reference.CHUNK_SIZES):
        fail("chunk size set mismatch")
    if set(cross["records"]) != {str(size) for size in reference.CHUNK_SIZES}:
        fail("chunk record set mismatch")
    for size, record in cross["records"].items():
        if record["output_length"] != reference.SAMPLES:
            fail("chunk output length mismatch at " + size)
        if record["valid_samples"] != reference.SAMPLES:
            fail("chunk valid samples mismatch at " + size)
        if record["emitted_before_finish"] != 0:
            fail("offline session emitted before finish at " + size)
        if record["finish_emitted"] != record["output_length"]:
            fail("finish emission accounting mismatch at " + size)
    alignment = boundary["alignment_probe"]
    if (alignment["output_peak_sample"] != 4000
            or alignment["output_lag_samples"] != 0
            or alignment["residual_lag_samples"] != 0
            or alignment["measured_latency"] is not False):
        fail("alignment probe is not the modelled zero-lag boundary")
    state = boundary["state"]
    for key in ("reset_replay_identical", "independent_session_identical",
                "cross_stream_reset_identical"):
        if state[key] is not True:
            fail("offline state/reset evidence failed: " + key)
    if state["real_recurrent_state_loaded"] is not False:
        fail("real recurrent state is claimed")
    if state["state_is_synthetic"] is not True:
        fail("state is not marked synthetic")
    tail_probe = boundary["tail_probe"]
    if (tail_probe["input_samples"] != 32123
            or tail_probe["output_samples"] != 32123
            or tail_probe["internal_frame_padding_samples"] != 37
            or tail_probe["padded_samples_emitted"] != 0
            or tail_probe["exact_length"] is not True):
        fail("partial final frame probe failed")

    asset = report["asset_boundary"]
    if asset["readiness"] != "blocked" or asset["reason_codes"] != EXPECTED_REASONS:
        fail("asset boundary is not blocked with the exact reasons")
    if asset["asset"]["sha256"] != reference.CHECKPOINT_SHA256:
        fail("asset digest mismatch")
    if asset["asset"]["byte_count"] != reference.CHECKPOINT_BYTES:
        fail("asset byte count mismatch")
    if asset["asset"]["source_revision"] != reference.SOURCE_REVISION:
        fail("asset source revision mismatch")
    if asset["asset"]["model_revision"] is not None:
        fail("unpinned model revision was replaced")
    if asset["asset"]["model_download_revision"] is not None:
        fail("unrecorded download revision was replaced")
    pointer = asset["auxiliary_assets"][0]
    if pointer["sha256"] != reference.POINTER_SHA256:
        fail("pointer digest mismatch")
    if pointer["byte_count"] != reference.POINTER_BYTES:
        fail("pointer byte count mismatch")
    if pointer["content_verified"] is not False:
        fail("pointer content is claimed as verified")
    if asset["download_attempted"] is not False:
        fail("asset boundary attempted a download")
    if asset["asset_bytes_read"] is not False:
        fail("asset boundary read bytes")
    if asset["vendor_runtime_invoked"] is not False:
        fail("asset boundary invoked a vendor runtime")
    if asset["synthetic_admission_control"]["status"] != "admitted":
        fail("synthetic admission control did not exercise admission")
    if asset["synthetic_admission_control"]["not_the_pinned_candidate"] is not True:
        fail("synthetic admission control is presented as the candidate")
    if asset["surrogate_policy"]["substitutes_for_candidate"] is not False:
        fail("surrogate is presented as the candidate")

    profile = report["enhancement_profile"]
    if profile["name"] != "enhancement":
        fail("enhancement profile name mismatch")
    if profile["identity_and_noisy_controls"] is not True:
        fail("identity/noisy controls missing")
    if profile["stoi"]["status"] != "synthetic_reference_only":
        fail("STOI is not labelled synthetic-only")
    if profile["stoi"]["real_cohort"] is not False:
        fail("STOI claims a real cohort")
    if profile["real_runtime"] is not False:
        fail("real runtime is claimed")
    if profile["real_clean_references"] is not False:
        fail("real clean references are claimed")
    if profile["content_and_availability_timing"]["measured"] is not False:
        fail("timing is claimed as measured")
    if profile["content_and_availability_timing"]["device_clock"] is not False:
        fail("device clock is claimed")
    if profile["listening"]["status"] != "not_run":
        fail("listening is claimed")
    if profile["alignment"]["status"] != "modelled_zero_lag":
        fail("alignment status is not the modelled zero-lag boundary")
    if profile["state_and_memory"]["real_memory_measured"] is not False:
        fail("real memory is claimed")

    adverse = report["adverse"]
    configs = adverse["config_rejections"]
    if set(configs) != EXPECTED_CONFIG_CASES:
        fail("config adverse case set mismatch")
    for name, case in configs.items():
        if name == "caller_asset_admission_control":
            if case["status"] != "created" or case["session_created"] is not True:
                fail("synthetic admission control was not created")
        elif case["status"] != "rejected" or case["session_created"] is not False:
            fail("config case did not fail closed: " + name)
    frames = adverse["frame_cases"]["cases"]
    if set(frames) != EXPECTED_FRAME_CASES:
        fail("frame adverse case set mismatch")
    for name, case in frames.items():
        if not case["status"].startswith("rejected"):
            fail("frame case did not fail closed: " + name)
        if case["state_unchanged"] is not True:
            fail("frame case changed state: " + name)
    if adverse["frame_cases"]["state_after_finish_unchanged_by_rejected_calls"] is not True:
        fail("state changed after a rejected post-finish call")
    if adverse["frame_cases"]["state_after_close_unchanged_by_rejected_calls"] is not True:
        fail("state changed after rejected post-close calls")
    lifecycle = adverse["lifecycle"]
    if (not lifecycle["finish_returns_samples"] or not lifecycle["reset_finish_empty"]
            or not lifecycle["close_idempotent"] or not lifecycle["zero_length_finish"]):
        fail("lifecycle evidence failed")
    if not lifecycle["second_finish"].startswith("rejected"):
        fail("second finish did not fail closed")
    for key in ("process_after_close", "finish_after_close", "reset_after_close"):
        if not lifecycle[key].startswith("rejected"):
            fail("post-close lifecycle did not fail closed: " + key)

    if set(gate["name"] for gate in report["gates"]) != EXPECTED_GATES:
        fail("release gate set mismatch")
    for gate in report["gates"]:
        if gate["status"] != "blocked" or not gate["evidence"] or not gate["reopen"]:
            fail("a release gate is not blocked with evidence and reopening")
    if report["gates"] != [dict(gate) for gate in reference.GATES]:
        fail("release gate text drifted")
    blockers = " ".join(report["exact_blockers"])
    for token in ("38,845,593", reference.CHECKPOINT_SHA256,
                  "model_revision is absent", "clearvoice 0.1.2",
                  "Apache-2.0", "open and private", "No rights-cleared"):
        if token not in blockers:
            fail("exact blocker text missing: " + token)
    for token in ("immutable model artifact revision",
                  "pinned clearvoice 0.1.2 runtime",
                  "written artifact-specific", "rights-cleared"):
        if token not in " ".join(report["reopen_conditions"]):
            fail("reopening condition missing: " + token)
    if len(report["missing_evidence"]) < 8:
        fail("missing evidence list is incomplete")

    context = report["source_reported_context"]
    full30 = context["full30"]
    if full30["requested_pairs"] != 30 or full30["valid_outputs"] != 30:
        fail("source-reported 30-pair count drifted")
    if full30["missing_outputs"] != 0:
        fail("source-reported missing output count drifted")
    if not _near(full30["quality_means"]["mossformer"]["si_sdr_db"], 20.687954):
        fail("source-reported MossFormerGAN SI-SDR drifted")
    if not _near(full30["paired_deltas"]["vs_identity"]["si_sdr_db"], 10.618209):
        fail("source-reported identity SI-SDR delta drifted")
    if not _near(full30["tail_adapter_seconds"]["49"], 117.586727):
        fail("source-reported tail timing drifted")
    if context["census_five_clip_screen"]["clips"] != 5:
        fail("source-reported census clip count drifted")
    if not _near(context["census_five_clip_screen"]["mean_delta_snr_db"], 7.91):
        fail("source-reported census delta drifted")
    if not _near(
            context["upstream_author_reported_dns2020"]["PESQ"], 3.57):
        fail("upstream author PESQ drifted")
    if "not reproduced" not in context["scope"]:
        fail("source context is not separated as provenance")
    if "not reproduced" not in context["disclaimer"]:
        fail("source context disclaimer is missing")

    provenance = report["model_provenance"]
    if provenance["candidate"] != reference.CANDIDATE_ID:
        fail("candidate identity mismatch")
    if provenance["source_revision"] != reference.SOURCE_REVISION:
        fail("source revision mismatch")
    if provenance["checkpoint"]["sha256"] != reference.CHECKPOINT_SHA256:
        fail("model provenance checkpoint digest mismatch")
    if provenance["checkpoint"]["bytes"] != reference.CHECKPOINT_BYTES:
        fail("model provenance checkpoint byte count mismatch")
    for key in ("present_in_sdk_worktree", "hashed_in_this_package",
                "downloaded_by_this_package", "loaded_or_executed"):
        if provenance["checkpoint"].get(key) is not False:
            fail("checkpoint provenance claim is not false: " + key)
    if provenance["pointer"]["content_verified"] is not False:
        fail("pointer content is claimed as verified")
    if provenance["model_card"]["accessed_by_this_package"] is not False:
        fail("model card access is claimed")
    if provenance["model_card"]["declared_revision"] is not None:
        fail("model card revision was invented")
    if provenance["package"]["installed"] is not False:
        fail("package is claimed as installed")
    if provenance["runtime"]["invoked"] is not False:
        fail("runtime is claimed as invoked")

    licensing = report["licensing_analysis"]
    for key in ("checkpoint_redistribution_clearance",
                "runtime_redistribution_clearance", "product_use_clearance",
                "training_data_provenance_established", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            fail("licensing rights claimed: " + key)
    if licensing["blocked_gate"] != "artifact_rights":
        fail("licensing gate mismatch")

    if report["source_pins"] != reference.SOURCE_PINS:
        fail("report source pins mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        fail("report boundary pins mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("local file names mismatch")
    if report["readme_digest_files"] != sorted(reference.SOURCE_PINS):
        fail("README digest file list mismatch")
    if report["exact_blockers"] != list(reference.EXACT_BLOCKERS):
        fail("exact blocker text mismatch")
    if report["reopen_conditions"] != list(reference.REOPEN_CONDITIONS):
        fail("reopen condition text mismatch")
    if report["missing_evidence"] != list(reference.MISSING_EVIDENCE):
        fail("missing evidence text mismatch")

    repeat = report["repeatability"]
    if repeat["count"] != 3 or repeat["byte_identical"] is not True:
        fail("repeatability is not byte-identical")
    if len(set(repeat["digests"])) != 1:
        fail("repeatability digests differ")
    core = {key: value for key, value in report.items() if key != "repeatability"}
    if repeat["digests"][0] != reference.sha256(reference.canonical_bytes(core)):
        fail("repeatability digest does not describe the report core")

    if re.search(rb"-0\.0(?=[,}\]])", reference.canonical_report_bytes(report)):
        fail("negative zero in canonical report")
    if SIDECAR.read_text(encoding="ascii").strip() != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report boundary, accounting, adverse cases and gates strict")


def check_source_files() -> None:
    for path, digest in {**reference.SOURCE_PINS}.items():
        target = reference.SOURCE_ROOT / path
        if not target.is_file() or target.is_symlink():
            fail("source pin missing: " + path)
        if reference.sha256_file(target) != digest:
            fail("source pin changed: " + path)
    for path, digest in reference.BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or target.is_symlink():
            fail("boundary pin missing: " + path)
        if reference.sha256_file(target) != digest:
            fail("boundary pin changed: " + path)

    for path in (reference.CHECKPOINT_DIR + "/" + reference.CHECKPOINT_FILE,
                 reference.CHECKPOINT_DIR + "/last_best_checkpoint"):
        if (SDK_ROOT / path).exists():
            fail("caller asset present but report says absent: " + path)
    if (SDK_ROOT / "adapters/clearvoice").exists():
        fail("research adapter was copied into the SDK worktree")

    record = reference.asset_ledger_record()
    if record.get("id") != reference.CANDIDATE_ID:
        fail("ledger candidate id mismatch")
    if record.get("source") != reference.PACKAGE_SOURCE:
        fail("ledger source mismatch")
    if record.get("source_revision") != reference.SOURCE_REVISION:
        fail("ledger source revision mismatch")
    if record.get("code_license") != reference.CODE_LICENSE_METADATA:
        fail("ledger code license mismatch")
    if record.get("model_license") != reference.MODEL_LICENSE_METADATA:
        fail("ledger model license mismatch")
    if record.get("training_data_note") != reference.TRAINING_DATA_NOTE:
        fail("ledger training data note mismatch")
    artifacts = {item["path"]: item for item in record.get("artifacts", [])}
    expected = {
        reference.CHECKPOINT_DIR + "/" + reference.CHECKPOINT_FILE: (
            reference.CHECKPOINT_BYTES, reference.CHECKPOINT_SHA256),
        reference.CHECKPOINT_DIR + "/last_best_checkpoint": (
            reference.POINTER_BYTES, reference.POINTER_SHA256),
    }
    for path, (size, digest) in expected.items():
        item = artifacts.get(path)
        if item is None:
            fail("ledger artifact missing: " + path)
        if item.get("bytes") != size or item.get("sha256") != digest:
            fail("ledger artifact drift: " + path)

    descriptor = reference.adapter_descriptor()
    if descriptor.get("identity") != reference.PACKAGE_IDENTITY:
        fail("research adapter identity mismatch")
    if descriptor.get("input_kind") != "waveform":
        fail("research adapter input kind mismatch")
    if descriptor.get("output_kinds") != ["waveform"]:
        fail("research adapter output kinds mismatch")
    if descriptor.get("tasks") != ["CLN-01"]:
        fail("research adapter task mismatch")
    if descriptor.get("modes") != ["offline"]:
        fail("research adapter mode mismatch")
    if descriptor.get("entrypoint") != ["python", "adapters/clearvoice/run.py"]:
        fail("research adapter entrypoint mismatch")

    results = reference.mossformer_results()
    if "MossFormerGAN_SE_16K" not in results.get("candidate", ""):
        fail("research results candidate mismatch")
    if results.get("source_commit") != reference.SOURCE_REVISION:
        fail("research results source revision mismatch")
    if results.get("checkpoint_sha256") != reference.CHECKPOINT_SHA256:
        fail("research results checkpoint mismatch")
    if results.get("requested_pairs") != 30 or results.get("valid_outputs") != 30:
        fail("research results pair counts drifted")
    if results.get("missing_outputs") != 0:
        fail("research results missing outputs drifted")
    quality = results["quality_aggregate"]["mossformer"]
    context = reference.SOURCE_REPORTED_CONTEXT["full30"]["quality_means"]["mossformer"]
    for key in ("snr_db", "si_sdr_db", "stoi"):
        if not _near(quality[key]["mean"], context[key], 1e-5):
            fail("research quality mean mismatch: " + key)
    deltas = results["paired_comparisons"]["identity"]
    context_delta = reference.SOURCE_REPORTED_CONTEXT["full30"]["paired_deltas"][
        "vs_identity"]
    for key, context_key in (("si_sdr_db_mossformer_minus_identity", "si_sdr_db"),
                             ("stoi_mossformer_minus_identity", "stoi")):
        if not _near(deltas[key]["mean"], context_delta[context_key], 1e-5):
            fail("research paired delta mismatch: " + key)
    tail = results["tail_four_adapter_seconds"]
    for pair in ("47", "48", "49", "50"):
        if not _near(tail[pair],
                     reference.SOURCE_REPORTED_CONTEXT["full30"][
                         "tail_adapter_seconds"][pair], 1e-5):
            fail("research tail timing mismatch: " + pair)

    if reference.vendored_binary_files():
        fail("vendored asset file: " + ",".join(reference.vendored_binary_files()))
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
            fail("binary file in task directory: " + path.name)
    print("verify: external identity, ledger, adapter and research results exact")


def check_strict_rejections() -> int:
    result = reference.strict_rejection_examples()
    if result["bad_json_rejected"] != result["bad_json_total"]:
        fail("strict JSON accepted bad input")
    if result["bad_pins_rejected"] != result["bad_pins_total"]:
        fail("strict pin parser accepted bad input")
    return result["bad_json_rejected"] + result["bad_pins_rejected"]


def check_licensing() -> None:
    explicit = 0
    annotated = 0
    expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if path.is_dir():
            fail("unexpected subdirectory: " + path.name)
        name = path.relative_to(HERE).as_posix()
        if "__pycache__" in path.parts:
            fail("unexpected __pycache__ in evidence directory")
        if name not in expected:
            fail("file outside the fail-closed local set: " + name)
        if path.suffix == ".py":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["# " + SPDX_COPYRIGHT, "# " + SPDX_LICENSE]:
                fail("missing explicit Python SPDX header: " + name)
            if path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("repeated SPDX identifier token: " + name)
            explicit += 1
        elif path.suffix == ".md":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["<!-- " + SPDX_COPYRIGHT + " -->",
                             "<!-- " + SPDX_LICENSE + " -->"]:
                fail("missing Markdown SPDX header: " + name)
            explicit += 1
        elif name.endswith(".license"):
            if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("invalid license sidecar: " + name)
            annotated += 1
        else:
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file() or sidecar.read_text(
                    encoding="utf-8") != SIDECAR_TEXT:
                fail("missing or invalid license sidecar: " + name + ".license")
            annotated += 1
    present = {path.relative_to(HERE).as_posix()
               for path in HERE.rglob("*") if path.is_file()}
    for name in sorted(expected - present):
        fail("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail("git status failed: " + result.stderr.strip())
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        fail("git diff --check failed: " + diff.stdout.strip())
    pinned = {TASK_PREFIX + name for name in reference.LOCAL_FILES}
    pinned.add(TASK_PREFIX + "SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and TASK_PREFIX + path.name not in pinned:
            fail("unpinned task file: " + path.name)
        if path.is_dir():
            fail("unexpected subdirectory: " + path.name)
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            data = path.read_bytes()
            if b"\r" in data:
                fail("CRLF in text file: " + path.name)
            for number, line in enumerate(
                    data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    fail(f"trailing whitespace: {path.name}:{number}")
    print("verify: write scope limited to the task-local evidence directory")
    return len(changed)


def check_readme() -> None:
    text = README.read_text(encoding="utf-8")
    if reference.readme_test_count_token() not in text:
        fail("README test count token is stale")
    for token in ("DEFER", "incomplete", "not_qualified",
                  "38,845,593", reference.CHECKPOINT_SHA256,
                  "clearvoice 0.1.2", "model_revision is absent",
                  "caller-supplied", "not MossFormerGAN",
                  reference.TASK_PREFIX.rstrip("/")):
        if token not in text:
            fail("README is missing required token: " + token)
    print("verify: README scope, blocker and count tokens present")


def check_reproduction(manifest: Dict[str, str], report_digest: str) -> None:
    if REPORT.read_bytes() != cli.report_bytes():
        fail("report.json is not byte-reproducible")
    if CONTRACT.read_bytes() != reference.contract_bytes():
        fail("contract.json is not byte-reproducible")
    if ADAPTER.read_bytes() != reference.adapter_bytes():
        fail("adapter.json is not byte-reproducible")
    if READINESS.read_bytes() != reference.readiness_bytes():
        fail("readiness.json is not byte-reproducible")
    if PINS.read_bytes() != reference.sources_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    if hashlib.sha256(cli.report_bytes()).hexdigest() != report_digest:
        fail("canonical report digest mismatch")
    code = "import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != report_digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical artifacts, sidecar, manifest and three cold starts exact")


def main() -> int:
    manifest = read_manifest()
    pins = check_pins(manifest)
    readme_rows = check_readme_digest_table()
    payloads = check_json()
    check_disposition(payloads["contract"], payloads["adapter"],
                      payloads["readiness"])
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    check_report(payloads["report"], digest)
    check_source_files()
    strict_count = check_strict_rejections()
    check_readme()
    check_reproduction(manifest, digest)
    check_licensing()
    changed = check_scope()
    print(
        f"verify: PASS pins={pins} readme_digest_rows={readme_rows} json_ok=4 "
        f"strict_rejections_ok={strict_count} reproduction_ok=3 licensing_ok=1 "
        f"scope_ok=1 changed_files={changed} profile={reference.PROFILE} "
        f"status={reference.STATUS} qualification={reference.QUALIFICATION_STATUS} "
        f"decision={reference.DECISION} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
