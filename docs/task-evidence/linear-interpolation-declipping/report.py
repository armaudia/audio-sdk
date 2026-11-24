"""Build the canonical, byte-repeatable restoration report for this fixture.

All candidate numbers are obtained by driving the task-local adapter boundary
(``run.inspect`` / ``run.run``).  Nothing is copied from the source report as if
it had been produced locally; pilot figures stay source-reported evidence only.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import fixtures
import reference
import run

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
ADAPTER_PATH = ROOT / "adapter.json"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
BASE_COMMIT = "68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4"
TASK_ID = "SDK-LINEAR-INTERPOLATION-DECLIPPING"

CANDIDATE_REF = {"kind": "reference", "id": "linear-declip.synthetic.v1", "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": run.ADAPTER_ID, "revision": 1}


def base_config(threshold=0.35, mask_source="derived"):
    return {"threshold": threshold, "mask_source": mask_source}


CASES = [
    {"id": "clean_identity", "stratum": "clean_baseline",
     "stimulus_id": "clean_bandlimited", "control": "identity",
     "configuration": {"control": "identity"}},
    {"id": "clean_clip_no_occupancy", "stratum": "clean_baseline",
     "stimulus_id": "clean_quiet", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clean_linear_no_occupancy", "stratum": "clean_baseline",
     "stimulus_id": "clean_bandlimited", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(threshold=1.0))},
    {"id": "occupancy_very_low", "stratum": "clipping_occupancy",
     "stimulus_id": "very_sparse_transients", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "occupancy_low", "stratum": "clipping_occupancy",
     "stimulus_id": "sparse_transients", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "occupancy_mid", "stratum": "clipping_occupancy",
     "stimulus_id": "speech_like", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(threshold=0.55))},
    {"id": "occupancy_high", "stratum": "clipping_occupancy",
     "stimulus_id": "dense_tones", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "occupancy_saturated", "stratum": "clipping_occupancy",
     "stimulus_id": "clean_bandlimited", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(threshold=0.01))},
    {"id": "clipped_very_low", "stratum": "control",
     "stimulus_id": "very_sparse_transients", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clipped_low", "stratum": "control",
     "stimulus_id": "sparse_transients", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clipped_mid", "stratum": "control",
     "stimulus_id": "speech_like", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config(threshold=0.55))},
    {"id": "clipped_high", "stratum": "control",
     "stimulus_id": "dense_tones", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clipped_saturated", "stratum": "control",
     "stimulus_id": "clean_bandlimited", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config(threshold=0.01))},
    {"id": "boundary_leading", "stratum": "boundary",
     "stimulus_id": "head_clip", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "boundary_trailing", "stratum": "boundary",
     "stimulus_id": "tail_clip", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "boundary_single_interior", "stratum": "boundary",
     "stimulus_id": "single_interior", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "boundary_two_anchors", "stratum": "boundary",
     "stimulus_id": "two_anchors", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "boundary_minimal_anchors", "stratum": "boundary",
     "stimulus_id": "minimal_anchors", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "boundary_all_clipped", "stratum": "boundary",
     "stimulus_id": "all_clipped", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "caller_mask_exact", "stratum": "mask_contract",
     "stimulus_id": "speech_like", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(
         threshold=0.55, mask_source="caller"))},
    {"id": "nonfinite_input", "stratum": "adverse",
     "stimulus_id": "nonfinite", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(threshold=0.55))},
]


def request_for(case, attempt_id="linear-declip-fixture-20261124"):
    request = {
        "protocol_version": 1,
        "operation": "run",
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": dict(case["configuration"]),
        "attempt_id": attempt_id,
        "stimulus_id": case["stimulus_id"],
    }
    if case["configuration"].get("mask_source") == "caller":
        clean = fixtures.build_samples(case["stimulus_id"])
        clipped = reference.hard_clip(clean, case["configuration"]["threshold"])
        request["clip_mask"] = reference.clip_mask(clipped,
                                                   case["configuration"]["threshold"])
    return request


def sha256_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins():
    observed = {}
    for relative, expected in fixtures.SOURCE_PINS.items():
        path = AUDIOML_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("required pinned source missing: " + relative)
        digest = sha256_path(path)
        if digest != expected:
            raise ValueError("pinned source digest mismatch: " + relative)
        observed[relative] = digest
    return observed


def _round(value, places=9):
    return round(float(value), places)


def rejections():
    """Every rejection is a real adapter-boundary call that raised."""
    cases = []
    templates = []
    base = base_config()

    def config_case(name, mutate):
        config = dict(control="linear_interp", **base)
        mutate(config)
        request = request_for({"stimulus_id": "speech_like", "configuration": config})
        templates.append((name, request))

    config_case("missing_threshold", lambda cfg: cfg.pop("threshold"))
    config_case("unknown_control", lambda cfg: cfg.update(control="not_a_control"))
    config_case("threshold_zero", lambda cfg: cfg.update(threshold=0.0))
    config_case("threshold_above_one", lambda cfg: cfg.update(threshold=1.5))
    config_case("threshold_not_numeric", lambda cfg: cfg.update(threshold="0.35"))
    config_case("threshold_nonfinite", lambda cfg: cfg.update(threshold=float("nan")))
    config_case("mask_source_invalid", lambda cfg: cfg.update(mask_source="detected"))
    config_case("unknown_control_key", lambda cfg: cfg.update(unexpected=1))

    def caller_case(name, mask_value=None, include_mask=True):
        config = dict(control="linear_interp", **base_config(mask_source="caller"))
        request = request_for({"stimulus_id": "speech_like", "configuration": config})
        if not include_mask:
            request.pop("clip_mask", None)
        else:
            request["clip_mask"] = mask_value
        templates.append((name, request))

    caller_case("missing_clip_mask", include_mask=False)
    caller_case("clip_mask_wrong_length", mask_value=[True] * 160)
    caller_case("clip_mask_not_boolean", mask_value=[0.5] * reference.OFFLINE_BLOCK_SAMPLES)
    bad_float_mask = [0.0] * reference.OFFLINE_BLOCK_SAMPLES
    bad_float_mask[17] = float("nan")
    caller_case("clip_mask_nonfinite", mask_value=bad_float_mask)
    clean = fixtures.build_samples("speech_like")
    clipped = reference.hard_clip(clean, 0.35)
    derived_mask = reference.clip_mask(clipped, 0.35)
    mismatched = list(derived_mask)
    mismatched[24] = not mismatched[24]
    caller_case("clip_mask_mismatch", mask_value=mismatched)

    with_mask = request_for({"stimulus_id": "speech_like",
                             "configuration": dict(control="linear_interp", **base)})
    with_mask["clip_mask"] = derived_mask
    templates.append(("unexpected_clip_mask", with_mask))

    bad_ref = request_for({"stimulus_id": "speech_like",
                           "configuration": dict(control="linear_interp", **base)})
    bad_ref["candidate_ref"] = {"kind": "reference", "id": "bad", "revision": 0}
    templates.append(("invalid_candidate_ref", bad_ref))
    bad_version = request_for({"stimulus_id": "speech_like",
                               "configuration": dict(control="linear_interp", **base)})
    bad_version["protocol_version"] = 2
    templates.append(("wrong_protocol_version", bad_version))
    bad_length = request_for({"stimulus_id": "speech_like",
                              "configuration": dict(control="linear_interp", **base)})
    bad_length["stimulus_samples"] = [0.0] * 160
    templates.append(("override_wrong_block_length", bad_length))
    for name, mutate in (
        ("missing_attempt_id", lambda item: item.pop("attempt_id")),
        ("missing_configuration", lambda item: item.pop("configuration")),
        ("unknown_stimulus_id", lambda item: item.update(stimulus_id="missing_stimulus")),
    ):
        request = request_for({"stimulus_id": "speech_like",
                               "configuration": dict(control="linear_interp", **base)})
        mutate(request)
        templates.append((name, request))
    for name, request in templates:
        try:
            run.run(request)
        except (run.RequestError, reference.ControlError, ValueError) as error:
            cases.append({"case": name, "status": "rejected", "reason": str(error)})
        else:
            cases.append({"case": name, "status": "accepted", "reason": None})
    with tempfile.TemporaryDirectory(prefix="linear-declip-rejections-") as scratch:
        for name, text in (
            ("duplicate_json_key",
             '{"protocol_version":1,"protocol_version":1,"operation":"inspect"}'),
            ("nonfinite_json_constant",
             '{"protocol_version":NaN,"operation":"inspect"}'),
        ):
            path = Path(scratch) / (name + ".json")
            path.write_text(text, encoding="utf-8")
            try:
                run.read_json(path)
            except run.RequestError as error:
                cases.append({"case": name, "status": "rejected", "reason": str(error)})
            else:
                cases.append({"case": name, "status": "accepted", "reason": None})
    return cases


def summarise(case, result):
    mask = result["mask"]
    return {
        "id": case["id"],
        "stratum": case["stratum"],
        "stimulus_id": case["stimulus_id"],
        "control": case["control"],
        "configuration": dict(case["configuration"]),
        "status": result["status"],
        "input": {
            "peak_abs": result["input"]["peak_abs"],
            "nonfinite_count": result["input"]["nonfinite_count"],
            "samples_sha256": result["input"]["samples_sha256"],
            "clean_sha256": result["input"]["clean_sha256"],
        },
        "mask": dict(mask),
        "output": {
            "peak_abs": result["output"]["peak_abs"],
            "nonfinite_count": result["output"]["nonfinite_count"],
            "samples_sha256": result["output"]["samples_sha256"],
            "sample_count": result["output"]["sample_count"],
        },
        "reconstruction": result["reconstruction"],
        "scoring": dict(result["scoring"]),
        "errors": list(result["errors"]),
    }


def _check_boundary_runs(case, result):
    """Recompute each boundary rule against the adapter output samples."""
    config = case["configuration"]
    if case["id"] == "nonfinite_input" or config.get("control") != "linear_interp":
        return None
    clean = fixtures.build_samples(case["stimulus_id"])
    threshold = config["threshold"]
    clipped = reference.hard_clip(clean, threshold)
    output = result["output"]["samples"]
    runs = result["reconstruction"]["runs"]
    leading_hold = []
    trailing_hold = []
    interior_ramp = []
    no_anchor_unchanged = []
    for item in runs:
        start, end = item["start"], item["end"]
        if item["kind"] in ("leading", "trailing"):
            anchor = item["left_anchor"]
            holds = all(output[index] == output[anchor] for index in range(start, end))
            (leading_hold if item["kind"] == "leading" else trailing_hold).append(holds)
        elif item["kind"] == "interior":
            left, right = item["left_anchor"], item["right_anchor"]
            span = right - left
            ramp = all(abs(output[index] - (output[left] + ((index - left) / span)
                                             * (output[right] - output[left]))) <= 1e-6
                       for index in range(start, end))
            interior_ramp.append(ramp)
        elif item["kind"] == "no_reliable_anchor":
            no_anchor_unchanged.append(
                all(output[index] == clipped[index] for index in range(start, end)))
    return {
        "run_count": len(runs),
        "kinds": [item["kind"] for item in runs],
        "leading_hold_exact": bool(leading_hold) and all(leading_hold),
        "trailing_hold_exact": bool(trailing_hold) and all(trailing_hold),
        "interior_ramp_valid": bool(interior_ramp) and all(interior_ramp),
        "no_anchor_unchanged": bool(no_anchor_unchanged) and all(no_anchor_unchanged),
        "reliable_samples_preserved": result["reconstruction"]["reliable_samples_preserved"],
        "replacement_mode": result["reconstruction"]["replacement_mode"],
        "max_output_deviation_from_anchor_or_ramp": _round(max(
            [abs(output[index] - output[item["left_anchor"]])
             for item in runs if item["kind"] in ("leading", "trailing")
             for index in range(item["start"], item["end"])] or [0.0])),
    }


def build_report():
    pins = verify_pins()
    results = {case["id"]: run.run(request_for(case)) for case in CASES}
    cases = [summarise(case, results[case["id"]]) for case in CASES]
    by_id = {case["id"]: case for case in cases}
    reject = rejections()
    clean = fixtures.build_samples("clean_bandlimited")
    identity_output = results["clean_identity"]["output"]["samples"]
    interior_boundary = by_id["boundary_single_interior"]
    interior_runs = interior_boundary["reconstruction"]["runs"]
    mask_checked = [case for case in cases
                    if case["mask"]["exact_saturation_verified"] is True]
    missing_results = [
        {"item": "paired real speech / EARS cohort scored by this adapter",
         "status": "not_run", "reason": "Synthetic deterministic fixtures only; no corpus, "
         "rights clearance or paired clip set is staged in this task-local fixture."},
        {"item": "STOI / perceptual scoring and blinded listening",
         "status": "not_run", "reason": "No external scorer or listening panel is available "
         "here; SI-SDR/RMSE are descriptive synthetic numbers only."},
        {"item": "installed native provider / descriptor conformance",
         "status": "not_run", "reason": "No public ABI, registry or CMake change is in scope."},
        {"item": "target-device timing and realtime availability",
         "status": "not_run", "reason": "Offline 2048-sample block comparator; no host, device "
         "or realtime claim is made."},
        {"item": "release qualification and benchmark ingestion",
         "status": "not_run", "reason": "No Bench bundle, submission or release gate is produced."},
        {"item": "SPADE / social-sparsity / C-OMP parity",
         "status": "not_run", "reason": "Established next comparison from source evidence; "
         "not implemented or scored here."},
        {"item": "pilot 12-clip mean SI-SDR reproduction",
         "status": "not_run", "reason": "NumPy/SciPy pilot and its EARS clips are not part of "
         "this stdlib offline comparator; pilot values stay source-reported only."},
        {"item": "blind clipping detection / unknown-mask operation",
         "status": "not_run", "reason": "By design this comparator consumes the exact known "
         "clipping mask. Detection, threshold estimation and false-mask robustness are outside "
         "this evidence and cannot be inferred from it."},
    ]
    comparisons = {}
    for name, candidate, anchor in (
        ("very_low", "occupancy_very_low", "clipped_very_low"),
        ("low", "occupancy_low", "clipped_low"),
        ("mid", "occupancy_mid", "clipped_mid"),
        ("high", "occupancy_high", "clipped_high"),
        ("saturated", "occupancy_saturated", "clipped_saturated"),
    ):
        linear_db = by_id[candidate]["scoring"]["si_sdr_db"]
        clipped_db = by_id[anchor]["scoring"]["si_sdr_db"]
        comparisons[name] = {
            "clipped_si_sdr_db": clipped_db,
            "linear_interp_si_sdr_db": linear_db,
            "linear_interp_delta_db": _round(linear_db - clipped_db, 6),
        }
    return {
        "protocol": "sdk.linear-interpolation-declipping.restoration.v1",
        "contract": "sdk.task-evidence.protocol-v1-shape",
        "task": TASK_ID,
        "component": "linear-interpolation-declipping",
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic",
        "qualification": {
            "status": "incomplete",
            "release_decision": "not_qualified",
            "reason": "Deterministic synthetic offline comparator only; no paired real speech, "
            "listening, native provider, target-device timing or release gate.",
            "missing_result_policy": "Every unrun, missing or rejected result is recorded "
            "explicitly and never counted as a pass or as partial qualification.",
            "no_missing_result_qualifies_candidate": True,
        },
        "geometry": {
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "f32",
            "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
            "offline_block_samples": reference.OFFLINE_BLOCK_SAMPLES,
            "execution_profile": "offline_only",
            "realtime_claim": False,
            "installed_v0_changed": False,
            "content_delay_samples": 0,
            "source_time_mapping": "identity within each offline block",
        },
        "source_pins": pins,
        "digests": {
            "fixture_spec": reference.canonical_digest(fixtures.seed_spec()),
            "adapter_descriptor": sha256_path(ADAPTER_PATH),
            "clean_bandlimited_f32": by_id["clean_identity"]["input"]["clean_sha256"],
            "identity_output_f32": by_id["clean_identity"]["output"]["samples_sha256"],
            "linear_no_occupancy_output_f32":
                by_id["clean_linear_no_occupancy"]["output"]["samples_sha256"],
        },
        "counts": {
            "cases": len(cases),
            "complete_cases": sum(1 for case in cases if case["status"] == "complete"),
            "adverse_cases": sum(1 for case in cases if case["status"] != "complete"),
            "rejection_checks": len(reject),
            "rejections_observed": sum(1 for item in reject if item["status"] == "rejected"),
            "missing_results": len(missing_results),
            "source_pins": len(pins),
            "exact_mask_verified_cases": len(mask_checked),
        },
        "strata": {
            "clipping_occupancy_percent": {
                case["id"]: case["mask"]["clipping_occupancy"] * 100.0
                for case in cases if case["stratum"] == "clipping_occupancy"
            },
            "mask_origin": sorted({case["mask"]["origin"] for case in cases}),
        },
        "cases": cases,
        "exact_clipping_mask": {
            "rule": "masked iff abs(clipped) == abs(f32(threshold)); otherwise clipped == clean",
            "float64_pilot_rule": "abs(clipped) >= threshold - 1e-10",
            "binary32_abs_tolerance": reference.MASK_ABS_TOL,
            "verified_cases": [case["id"] for case in mask_checked],
            "caller_mask_exact_case": by_id["caller_mask_exact"]["mask"]["origin"],
            "caller_mask_mismatch_rejected": any(
                item["case"] == "clip_mask_mismatch" and item["status"] == "rejected"
                for item in reject),
        },
        "linear_interpolation": {
            "anchor_rule": "numpy_interp_reliable_endpoints_constant_hold",
            "boundary": {case["id"]: _check_boundary_runs(
                case, results[case["id"]]) for case in CASES if case["stratum"] == "boundary"},
            "single_interior_anchors": {
                "left": interior_runs[0]["left_anchor"],
                "right": interior_runs[0]["right_anchor"],
                "left_anchor_value": interior_runs[0]["left_anchor_value"],
                "right_anchor_value": interior_runs[0]["right_anchor_value"],
                "reconstructed_value": interior_runs[0]["first_output"],
            },
            "all_masked_replacement_mode":
                by_id["boundary_all_clipped"]["reconstruction"]["replacement_mode"],
            "reliable_samples_preserved_in_all_complete_cases": all(
                case["reconstruction"].get("reliable_samples_preserved", True)
                for case in cases if case["status"] == "complete"),
        },
        "clean_transparency": {
            "identity_exact": (reference.digest_samples(identity_output)
                               == by_id["clean_identity"]["input"]["clean_sha256"]),
            "identity_max_abs_diff": _round(reference.max_abs_diff(clean, identity_output)),
            "clipped_input_no_occupancy_occupancy":
                by_id["clean_clip_no_occupancy"]["mask"]["clipping_occupancy"],
            "clipped_input_no_occupancy_exact":
                by_id["clean_clip_no_occupancy"]["output"]["samples_sha256"]
                == by_id["clean_clip_no_occupancy"]["input"]["clean_sha256"],
            "linear_interp_no_occupancy_occupancy":
                by_id["clean_linear_no_occupancy"]["mask"]["clipping_occupancy"],
            "linear_interp_no_occupancy_exact":
                by_id["clean_linear_no_occupancy"]["output"]["samples_sha256"]
                == by_id["clean_linear_no_occupancy"]["input"]["clean_sha256"],
            "status": "measured_synthetic",
        },
        "controls": {
            "by_occupancy": comparisons,
            "comparison_note": "All SI-SDR values are against the frozen synthetic clean "
            "source; no real-speech, perceptual or cross-task comparison is implied.",
        },
        "output_peaks": {
            case["id"]: {
                "input_peak": case["input"]["peak_abs"],
                "output_peak": case["output"]["peak_abs"],
                "nonfinite_output": case["output"]["nonfinite_count"],
            } for case in cases
        },
        "peak_behavior": {
            "complete_cases_with_finite_output": sum(
                1 for case in cases if case["status"] == "complete"
                and case["output"]["nonfinite_count"] == 0),
            "max_output_peak_observed": max(case["output"]["peak_abs"] for case in cases
                                            if case["status"] == "complete"),
            "outputs_within_input_peak": all(
                case["output"]["peak_abs"] <= case["input"]["peak_abs"] + 1e-9
                for case in cases if case["status"] == "complete"),
            "claim": "descriptive bound on this synthetic cohort only; linear interpolation "
            "between in-range anchors is not a limiter guarantee",
        },
        "adverse_and_skipped": {
            "control_rejections": reject,
            "numerical": {
                "case": "nonfinite_input",
                "status": results["nonfinite_input"]["status"],
                "input_nonfinite_count": results["nonfinite_input"]["input"]["nonfinite_count"],
                "output_samples_serialized": False,
                "errors": results["nonfinite_input"]["errors"],
            },
            "missing_results": missing_results,
            "not_applicable_checks": [
                {"item": "consumer opt-in OFF/ON build matrix",
                 "status": "not_applicable",
                 "reason": "No opt-in provider, CMake option or consumer surface was added; "
                 "the unchanged SDK baseline ctest suite is the relevant local check."},
                {"item": "generated C headers and REUSE header text",
                 "status": "not_applicable",
                 "reason": "No C header is generated by this task; docs/** is covered by the "
                 "repository REUSE.toml aggregate annotation."},
            ],
        },
        "processor_decision": {
            "decision": "defer",
            "recorded_before_processor_exposure": True,
            "public_processor_exposed": False,
            "reason": "Keep linear interpolation as an offline comparator on the exact "
            "clipping mask. The source RST-01 screen reports 10.99 dB SI-SDR for linear "
            "interpolation at threshold 0.35 versus 15.05 dB for band-limited POCS, and "
            "this synthetic cohort is scored only against the frozen clean source. No "
            "quality, listening, native-provider or timing evidence supports a processor.",
            "local_comparisons": comparisons,
            "conditions_to_reopen": [
                "Paired rights-cleared speech with fixed threshold, mask and clean reference.",
                "Independent perceptual scoring and blinded listening with held-out speakers.",
                "Native provider frame-for-frame parity under an agreed quality margin.",
                "Target-device paced timing and installed-archive evidence under an explicit "
                "workload.",
                "Separate SDK contract, conformance and release-gate work for any public "
                "registration, descriptor, default provider or CMake change.",
            ],
        },
        "scope": {
            "public_abi_or_api_changed": False,
            "descriptor_registry_changed": False,
            "cmake_or_contract_changed": False,
            "defaults_or_installed_v0_changed": False,
            "files_outside_task_directory_changed": False,
            "real_corpora_or_listening_claimed": False,
            "target_device_or_release_claimed": False,
            "bench_bundle_or_ingestion_claimed": False,
            "opt_in_provider_added": False,
            "generated_headers_added": False,
        },
        "reopen_conditions": [
            "Build and pin a native/SDK provider at a fixed revision with descriptor and "
            "installed-archive digests, then compare frame-for-frame on a frozen paired cohort.",
            "Agree clipping-occupancy, mask-fidelity, transparency and output-peak margins "
            "before any quality claim.",
            "Score rights-cleared real speech with an independent perceptual metric and "
            "blinded listening; report held-out speaker and bandwidth strata.",
            "Validate blind clipping detection or threshold estimation separately; this "
            "comparator assumes the exact known mask.",
            "Add SPADE/social-sparsity/C-OMP and band-limited POCS parity plus target-device "
            "timing under an explicit workload before any best-baseline claim.",
            "Any public registration, descriptor, default-provider or CMake change requires "
            "separate SDK contract, conformance and release-gate work outside this task scope.",
        ],
    }


def main():
    canonical = reference.canonical_bytes(build_report())
    REPORT_PATH.write_bytes(canonical)
    print("wrote", REPORT_PATH, len(canonical), "bytes")


if __name__ == "__main__":
    main()
