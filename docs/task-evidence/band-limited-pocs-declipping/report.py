"""Build the canonical, byte-repeatable restoration report for the POCS fixture.

All candidate numbers are obtained by driving the task-local adapter boundary
(``run.inspect`` / ``run.run``).  No result is read from the pilot report as if
it were produced here; the pilot figures remain source evidence only.
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
BASE_COMMIT = "9677040cba2929f9936eaa565f200f585d5270a8"
TASK_ID = "SDK-BAND-LIMITED-POCS-DECLIPPING"

CANDIDATE_REF = {"kind": "reference", "id": "band-limited-pocs.synthetic.v1", "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": run.ADAPTER_ID, "revision": 1}


def base_config(threshold=0.35, cutoff_hz=7600.0, iterations=60):
    return {"threshold": threshold, "cutoff_hz": cutoff_hz, "iterations": iterations}


CASES = [
    {"id": "clean_identity", "stratum": "clean_baseline",
     "stimulus_id": "clean_bandlimited", "control": "identity",
     "configuration": {"control": "identity"}},
    {"id": "clean_clip_no_occupancy", "stratum": "clean_baseline",
     "stimulus_id": "clean_quiet", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config(threshold=0.35))},
    {"id": "clean_pocs_transparency", "stratum": "clean_baseline",
     "stimulus_id": "clean_bandlimited", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(
         threshold=1.0, cutoff_hz=3500.0))},
    {"id": "occupancy_very_low", "stratum": "clipping_occupancy",
     "stimulus_id": "very_sparse_transients", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config())},
    {"id": "occupancy_low", "stratum": "clipping_occupancy",
     "stimulus_id": "sparse_transients", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config())},
    {"id": "occupancy_mid", "stratum": "clipping_occupancy",
     "stimulus_id": "speech_like", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(threshold=0.55))},
    {"id": "occupancy_high", "stratum": "clipping_occupancy",
     "stimulus_id": "dense_tones", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config())},
    {"id": "occupancy_saturated", "stratum": "clipping_occupancy",
     "stimulus_id": "clean_bandlimited", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(threshold=0.01))},
    {"id": "clipped_very_low", "stratum": "control",
     "stimulus_id": "very_sparse_transients", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clipped_low", "stratum": "control",
     "stimulus_id": "sparse_transients", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "clipped_high", "stratum": "control",
     "stimulus_id": "dense_tones", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config())},
    {"id": "linear_high", "stratum": "control",
     "stimulus_id": "dense_tones", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config())},
    {"id": "clipped_anchor", "stratum": "control",
     "stimulus_id": "speech_like", "control": "clipped_input",
     "configuration": dict(control="clipped_input", **base_config(threshold=0.55))},
    {"id": "linear_interp_anchor", "stratum": "control",
     "stimulus_id": "speech_like", "control": "linear_interp",
     "configuration": dict(control="linear_interp", **base_config(threshold=0.55))},
    {"id": "bandwidth_narrow", "stratum": "bandwidth",
     "stimulus_id": "speech_like", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(
         threshold=0.55, cutoff_hz=2000.0))},
    {"id": "bandwidth_mid", "stratum": "bandwidth",
     "stimulus_id": "speech_like", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(
         threshold=0.55, cutoff_hz=3500.0))},
    {"id": "iterations_min", "stratum": "bounded_iterations",
     "stimulus_id": "speech_like", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(
         threshold=0.55, iterations=1))},
    {"id": "nonfinite_input", "stratum": "adverse",
     "stimulus_id": "nonfinite", "control": "pocs_declip",
     "configuration": dict(control="pocs_declip", **base_config(threshold=0.55))},
]


def request_for(case, attempt_id="pocs-fixture-20261124"):
    return {
        "protocol_version": 1,
        "operation": "run",
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": dict(case["configuration"]),
        "attempt_id": attempt_id,
        "stimulus_id": case["stimulus_id"],
    }


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
    for name, mutate in (
        ("missing_threshold", lambda cfg: cfg.pop("threshold")),
        ("unknown_control", lambda cfg: cfg.update(control="not_a_control")),
        ("threshold_zero", lambda cfg: cfg.update(threshold=0.0)),
        ("threshold_above_one", lambda cfg: cfg.update(threshold=1.5)),
        ("cutoff_below_min", lambda cfg: cfg.update(cutoff_hz=99.0)),
        ("cutoff_above_nyquist_margin", lambda cfg: cfg.update(cutoff_hz=8000.0)),
        ("iterations_zero", lambda cfg: cfg.update(iterations=0)),
        ("iterations_above_cap", lambda cfg: cfg.update(iterations=61)),
        ("iterations_not_integer", lambda cfg: cfg.update(iterations=1.5)),
        ("threshold_not_numeric", lambda cfg: cfg.update(threshold="0.35")),
        ("threshold_nonfinite", lambda cfg: cfg.update(threshold=float("nan"))),
        ("unknown_control_key", lambda cfg: cfg.update(unexpected=1)),
    ):
        config = base_config()
        config["control"] = "pocs_declip"
        mutate(config)
        request = request_for({"stimulus_id": "speech_like", "configuration": config})
        templates.append((name, request))
    bad_ref = request_for({"stimulus_id": "speech_like",
                           "configuration": dict(control="pocs_declip",
                                                 **base_config())})
    bad_ref["candidate_ref"] = {"kind": "reference", "id": "bad", "revision": 0}
    templates.append(("invalid_candidate_ref", bad_ref))
    bad_version = request_for({"stimulus_id": "speech_like",
                               "configuration": dict(control="pocs_declip",
                                                     **base_config())})
    bad_version["protocol_version"] = 2
    templates.append(("wrong_protocol_version", bad_version))
    bad_length = request_for({"stimulus_id": "speech_like",
                              "configuration": dict(control="pocs_declip",
                                                    **base_config())})
    bad_length["stimulus_samples"] = [0.0] * 160
    templates.append(("override_wrong_block_length", bad_length))
    for name, request in templates:
        try:
            run.run(request)
        except (run.RequestError, reference.ControlError, ValueError) as error:
            cases.append({"case": name, "status": "rejected", "reason": str(error)})
        else:
            cases.append({"case": name, "status": "accepted", "reason": None})
    with tempfile.TemporaryDirectory(prefix="pocs-rejections-") as scratch:
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
    scoring = result["scoring"]
    trace = result["iteration_trace"]
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
            "clipping_occupancy": result["input"]["clipping_occupancy"],
            "clipped_samples": result["input"]["clipped_samples"],
            "samples_sha256": result["input"]["samples_sha256"],
            "clean_sha256": result["input"]["clean_sha256"],
        },
        "output": {
            "peak_abs": result["output"]["peak_abs"],
            "nonfinite_count": result["output"]["nonfinite_count"],
            "samples_sha256": result["output"]["samples_sha256"],
            "sample_count": result["output"]["sample_count"],
        },
        "scoring": dict(scoring),
        "projection_metadata": dict(result["projection_metadata"]),
        "final_max_delta": trace[-1]["max_delta"] if trace else None,
        "first_max_delta": trace[0]["max_delta"] if trace else None,
        "errors": list(result["errors"]),
    }


def build_report():
    pins = verify_pins()
    results = {case["id"]: run.run(request_for(case)) for case in CASES}
    cases = [summarise(case, results[case["id"]]) for case in CASES]
    by_id = {case["id"]: case for case in cases}
    reject = rejections()
    clean = fixtures.build_samples("clean_bandlimited")
    identity_result = results["clean_identity"]
    identity_output = identity_result["output"]["samples"]
    transparency = by_id["clean_pocs_transparency"]
    pocs_clean_fixture = fixtures.build_samples("clean_bandlimited")
    clipped_for_transparency = reference.hard_clip(
        pocs_clean_fixture, CASES[2]["configuration"]["threshold"])
    transparency_mask = reference.clip_mask(
        clipped_for_transparency, CASES[2]["configuration"]["threshold"])
    transparency_pocs = reference.pocs_declip(
        clipped_for_transparency, transparency_mask, 3500.0, 60)

    iteration_cases = ("iterations_min", "occupancy_mid")
    iteration_behavior = {}
    for case_id in iteration_cases:
        trace = results[case_id]["iteration_trace"]
        deltas = [item["max_delta"] for item in trace]
        iteration_behavior[case_id] = {
            "configured_iterations": results[case_id]["configuration"]["iterations"],
            "projection_count": results[case_id]["projection_metadata"]["projection_count"],
            "trace_length": len(trace),
            "first_max_delta": deltas[0],
            "last_max_delta": deltas[-1],
            "max_delta_nonincreasing": all(right <= left + 1e-12
                                           for left, right in zip(deltas, deltas[1:])),
            "all_deltas_finite": all(value == value and abs(value) != float("inf")
                                     for value in deltas),
            "projections": trace,
        }

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
         "status": "not_run", "reason": "Offline 2048-sample block reference; no host, device "
         "or realtime claim is made."},
        {"item": "release qualification and benchmark ingestion",
         "status": "not_run", "reason": "No Bench bundle, submission or release gate is produced."},
        {"item": "SPADE / social-sparsity / C-OMP parity",
         "status": "not_run", "reason": "Established next comparison from source evidence; "
         "not implemented or scored here."},
        {"item": "pilot 12-clip mean SI-SDR reproduction",
         "status": "not_run", "reason": "NumPy/SciPy pilot and its EARS clips are not part of "
         "this stdlib offline reference; pilot values stay source-reported only."},
    ]
    return {
        "protocol": "sdk.band-limited-pocs-declipping.restoration.v1",
        "contract": "sdk.task-evidence.protocol-v1-shape",
        "task": TASK_ID,
        "component": "band-limited-pocs-declipping",
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic",
        "qualification": {
            "status": "incomplete",
            "release_decision": "not_qualified",
            "reason": "Deterministic synthetic offline boundary fixture only; no paired real "
            "speech, listening, native provider, target-device timing or release gate.",
            "missing_result_policy": "Every unrun, missing or rejected result is recorded "
            "explicitly and never counted as a pass or as partial qualification.",
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
            "clean_bandlimited_f32": identity_result["input"]["clean_sha256"],
            "identity_output_f32": identity_result["output"]["samples_sha256"],
            "pocs_clean_output_f32": reference.digest_samples(transparency_pocs["samples"]),
        },
        "counts": {
            "cases": len(cases),
            "pocs_cases": sum(1 for case in cases if case["control"] == "pocs_declip"
                              and case["status"] == "complete"),
            "complete_cases": sum(1 for case in cases if case["status"] == "complete"),
            "adverse_cases": sum(1 for case in cases if case["status"] != "complete"),
            "rejection_checks": len(reject),
            "rejections_observed": sum(1 for item in reject if item["status"] == "rejected"),
            "missing_results": len(missing_results),
            "source_pins": len(pins),
        },
        "strata": {
            "clipping_occupancy_percent": {
                case["id"]: case["input"]["clipping_occupancy"] * 100.0
                for case in cases if case["stratum"] == "clipping_occupancy"
            },
            "bandwidth_cutoff_hz": {
                case["id"]: case["configuration"]["cutoff_hz"]
                for case in cases if case["stratum"] == "bandwidth"
            },
        },
        "cases": cases,
        "clean_transparency": {
            "identity_exact": (reference.digest_samples(identity_output)
                               == identity_result["input"]["clean_sha256"]),
            "identity_max_abs_diff": _round(reference.max_abs_diff(clean, identity_output)),
            "clip_control_no_occupancy_occupancy":
                by_id["clean_clip_no_occupancy"]["input"]["clipping_occupancy"],
            "clip_control_no_occupancy_exact":
                by_id["clean_clip_no_occupancy"]["output"]["samples_sha256"]
                == by_id["clean_clip_no_occupancy"]["input"]["clean_sha256"],
            "pocs_bandlimited_max_abs_diff": transparency["scoring"]["max_abs_diff"],
            "pocs_bandlimited_si_sdr_db": transparency["scoring"]["si_sdr_db"],
            "pocs_bandlimited_output_peak": transparency["output"]["peak_abs"],
            "status": "measured_synthetic",
        },
        "iteration_behavior": iteration_behavior,
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
            "claim": "descriptive bound on this synthetic cohort only; no universal "
            "peak-overshoot guarantee or limiter behavior is claimed",
        },
        "adverse_and_skipped": {
            "control_rejections": reject,
            "numerical": {
                "case": "nonfinite_input",
                "status": results["nonfinite_input"]["status"],
                "input_nonfinite_count":
                    results["nonfinite_input"]["input"]["nonfinite_count"],
                "output_samples_serialized": False,
                "errors": results["nonfinite_input"]["errors"],
            },
            "missing_results": missing_results,
        },
        "controls": {
            "clipped_anchor_si_sdr_db": by_id["clipped_anchor"]["scoring"]["si_sdr_db"],
            "linear_interp_si_sdr_db": by_id["linear_interp_anchor"]["scoring"]["si_sdr_db"],
            "pocs_mid_occupancy_si_sdr_db": by_id["occupancy_mid"]["scoring"]["si_sdr_db"],
            "by_occupancy_si_sdr_db": {
                name: {
                    "clipped": by_id[anchor]["scoring"]["si_sdr_db"],
                    "pocs": by_id[candidate]["scoring"]["si_sdr_db"],
                } for name, candidate, anchor in (
                    ("very_low", "occupancy_very_low", "clipped_very_low"),
                    ("low", "occupancy_low", "clipped_low"),
                    ("mid", "occupancy_mid", "clipped_anchor"),
                    ("high", "occupancy_high", "clipped_high"),
                )
            },
            "high_occupancy_linear_interp_si_sdr_db":
                by_id["linear_high"]["scoring"]["si_sdr_db"],
            "comparison_note": "All SI-SDR values are against the frozen synthetic clean "
            "source; no real-speech or perceptual comparison is implied.",
        },
        "scope": {
            "public_abi_or_api_changed": False,
            "descriptor_registry_changed": False,
            "cmake_or_contract_changed": False,
            "defaults_or_installed_v0_changed": False,
            "files_outside_task_directory_changed": False,
            "real corpora_or_listening_claimed": False,
            "target_device_or_release_claimed": False,
            "bench_bundle_or_ingestion_claimed": False,
        },
        "reopen_conditions": [
            "Build and pin a native/SDK provider at a fixed revision with descriptor and "
            "installed-archive digests, then compare frame-for-frame on a frozen paired cohort.",
            "Agree clipping-occupancy, bandwidth, transparency, peak and iteration margins plus "
            "content-delay/availability budgets before any qualification claim.",
            "Score rights-cleared real speech with an independent perceptual metric and blinded "
            "listening; report held-out speaker and bandwidth strata.",
            "Add SPADE/social-sparsity/C-OMP comparisons and target-device timing under an "
            "explicit workload before any best-baseline claim.",
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
