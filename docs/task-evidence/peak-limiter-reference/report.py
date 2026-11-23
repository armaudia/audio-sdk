"""Build the canonical DSP report by driving the opt-in adapter boundary."""

import hashlib
import json
import math
from pathlib import Path
import tempfile

import reference
import run

HERE = Path(__file__).resolve().parent
ADAPTER_PATH = HERE / "adapter.json"
FIXTURE_PATH = HERE / "fixtures/stimuli.json"
TASK = "SDK-PEAK-LIMITER-REFERENCE"
CANDIDATE = {"kind": "reference", "id": "dsp.peak-limiter.ref", "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": run.ADAPTER_ID, "revision": 1}
DEFAULT = {"control": "peak_limiter_reference", "ceiling": 0.98, "release_ms": 50.0}


def sha256_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def envelope(samples, window=16):
    return [math.sqrt(sum(value * value for value in samples[i:i + window]) / window)
            for i in range(0, len(samples) - window + 1, window)]


def correlation(left, right):
    if len(left) != len(right):
        raise ValueError("envelope_geometry_mismatch")
    mean_l, mean_r = sum(left) / len(left), sum(right) / len(right)
    centered_l = [value - mean_l for value in left]
    centered_r = [value - mean_r for value in right]
    cross = sum(a * b for a, b in zip(centered_l, centered_r))
    norm_l = math.sqrt(sum(a * a for a in centered_l))
    norm_r = math.sqrt(sum(b * b for b in centered_r))
    return cross / (norm_l * norm_r) if norm_l and norm_r else None


def request(operation, stimulus_id, configuration, attempt_id, reset_frames=()):
    body = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": CANDIDATE,
        "adapter_ref": ADAPTER_REF,
        "configuration": configuration,
    }
    if operation == "run":
        body.update({"attempt_id": attempt_id, "stimulus_id": stimulus_id,
                     "reset_frames": list(reset_frames)})
    return body


def call_run(stimulus_id, configuration, attempt_id, reset_frames=()):
    result = run.run(request("run", stimulus_id, configuration, attempt_id, reset_frames))
    if result["status"] != "complete":
        raise ValueError("adapter_run_incomplete")
    return result


def sample_gain_trace(samples, ceiling, release_ms, resets=()):
    limiter = reference.PeakLimiterReference(ceiling, release_ms)
    gains = []
    for index in range(0, len(samples), reference.FRAME_SAMPLES):
        frame_index = index // reference.FRAME_SAMPLES
        if frame_index in resets:
            limiter.reset()
        block = samples[index:index + reference.FRAME_SAMPLES]
        limiter.process(block, gain_trace=gains)
    return gains


def case_metrics(stimulus_id, configuration, attempt_id, resets=(), ceiling=None):
    samples = run.generate(stimulus_id)
    result = call_run(stimulus_id, configuration, attempt_id, resets)
    output = result["output"]
    ceiling = configuration.get("ceiling") if ceiling is None else ceiling
    finite_input = [math.isfinite(value) for value in samples]
    modified = [index for index, (left, right) in enumerate(zip(samples, output.get("samples", [])))
                if reference._F32.pack(left) != reference._F32.pack(right)]
    peaks = [abs(value) for value in samples if math.isfinite(value)]
    last_limited = max((index for index, value in enumerate(samples)
                        if math.isfinite(value) and abs(value) > ceiling), default=None)
    recovery = None
    if last_limited is not None and ceiling is not None:
        gains = sample_gain_trace(samples, ceiling, configuration["release_ms"], resets)
        for index in range(last_limited, len(gains)):
            if gains[index] >= reference.ENGAGED_THRESHOLD and all(
                    math.isfinite(value) and abs(value) <= ceiling
                    for value in samples[last_limited + 1:index + 1]):
                recovery = index
                break
    return {
        "stimulus_id": stimulus_id,
        "configuration": configuration,
        "attempt_id": attempt_id,
        "reset_frames": list(resets),
        "input_sha256": reference.digest_samples(samples),
        "output_sha256": output["samples_sha256"],
        "sample_count": output["sample_count"],
        "peak_in": max(peaks, default=None),
        "peak_out": output["peak_abs"] if output["nonfinite_count"] == 0 else None,
        "headroom": (ceiling - output["peak_abs"]) if (ceiling is not None and
                     output["nonfinite_count"] == 0) else None,
        "engaged_frames": output["engaged_frames"],
        "fast_path_frames": output["fast_path_frames"],
        "gain_final": output["gain_final"],
        "reset_count": output["reset_count"],
        "finite_input_count": sum(finite_input),
        "nonfinite_input_count": len(finite_input) - sum(finite_input),
        "finite_output_count": output["finite_count"],
        "nonfinite_output_count": output["nonfinite_count"],
        "first_modified_sample": modified[0] if modified else None,
        "last_limited_sample": last_limited,
        "recovery_sample_exact": recovery,
        "frames": output["frames"],
        "status": result["status"],
        "errors": result["errors"],
    }


def control_rejections():
    probes = (
        ("missing_controls", {"control": "peak_limiter_reference"}),
        ("unknown_control", {"control": "peak_limiter_reference", "ceiling": 0.98,
                             "release_ms": 50.0, "lookahead": 0}),
        ("ceiling_zero", {"control": "peak_limiter_reference", "ceiling": 0.0,
                          "release_ms": 50.0}),
        ("ceiling_over_one", {"control": "peak_limiter_reference", "ceiling": 1.5,
                              "release_ms": 50.0}),
        ("release_zero", {"control": "peak_limiter_reference", "ceiling": 0.98,
                          "release_ms": 0.0}),
        ("release_over_limit", {"control": "peak_limiter_reference", "ceiling": 0.98,
                                "release_ms": 5001.0}),
        ("nonfinite_ceiling_string", {"control": "peak_limiter_reference", "ceiling": "nan",
                                      "release_ms": 50.0}),
        ("nonfinite_release_string", {"control": "peak_limiter_reference", "ceiling": 0.98,
                                      "release_ms": float("inf")}),
    )
    results = {}
    for name, config in probes:
        try:
            call_run("subceiling", config, name)
            results[name] = {"status": "unexpectedly_accepted", "reason": None}
        except (reference.ControlError, run.RequestError, ValueError) as error:
            results[name] = {"status": "rejected", "reason": str(error) or error.__class__.__name__}
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "nan.json"
        path.write_text('{"ceiling": NaN}', encoding="ascii")
        try:
            run.read_json(path)
            results["json_nan_constant"] = {"status": "unexpectedly_accepted", "reason": None}
        except run.RequestError as error:
            results["json_nan_constant"] = {"status": "rejected", "reason": str(error)}
    return results


def build_report():
    fixture_document = run.fixture()
    pins = fixture_document["source_pins"]
    descriptor = ADAPTER_PATH.read_bytes()
    inspect_result = run.inspect(request("inspect", None, dict(DEFAULT), "inspect"))
    cases = {}
    for stimulus_id in ("sweep", "steps", "impulse", "silence", "clean_speech_like",
                        "load_control", "subceiling", "nonfinite"):
        cases[stimulus_id] = case_metrics(stimulus_id, dict(DEFAULT), "baseline-" + stimulus_id)
    cases["sweep_ceiling_0_5"] = case_metrics(
        "sweep", {"control": "peak_limiter_reference", "ceiling": 0.5, "release_ms": 50.0},
        "baseline-sweep-ceiling-0-5")

    identity = call_run("subceiling", {"control": "identity"}, "identity-subceiling")
    subceiling = run.generate("subceiling")
    transparency_bits_equal = reference._F32.pack(subceiling[0]) == reference._F32.pack(
        identity["output"]["samples"][0])
    transparency = {
        "subceiling_input_sha256": reference.digest_samples(subceiling),
        "identity_output_sha256": identity["output"]["samples_sha256"],
        "reference_output_sha256": cases["subceiling"]["output_sha256"],
        "bit_exact": (identity["output"]["samples_sha256"] ==
                      cases["subceiling"]["output_sha256"] and transparency_bits_equal),
        "fast_path_frames": cases["subceiling"]["fast_path_frames"],
        "engaged_frames": cases["subceiling"]["engaged_frames"],
        "note": "Transparency is conditional on gain_ == 1 and a finite sub-ceiling frame.",
    }

    impulse_input = run.generate("impulse")
    impulse_output = call_run("impulse", dict(DEFAULT), "delay-impulse")["output"]["samples"]
    in_peak = max(range(len(impulse_input)), key=lambda index: abs(impulse_input[index]))
    out_peak = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))
    delay = {
        "input_peak_sample": in_peak,
        "output_peak_sample": out_peak,
        "content_delay_samples": out_peak - in_peak,
        "lookahead_samples": 0,
        "note": "Per-sample output depends only on the current input sample; no lookahead buffer.",
    }

    speech = run.generate("clean_speech_like")
    speech_limited = call_run("clean_speech_like", dict(DEFAULT), "speech-limited")["output"]["samples"]
    speech_anchor = reference.hard_clip(speech, 0.2)
    envelope_reference = envelope(speech)
    envelope_correlation = correlation(envelope_reference, envelope(speech_limited))
    envelope_anchor_correlation = correlation(envelope_reference, envelope(speech_anchor))
    intelligibility_proxy = {
        "stimulus": "synthetic clean-speech-like harmonic bursts; no real speech or corpus",
        "envelope_window_samples": 16,
        "envelope_correlation_reference": envelope_correlation,
        "envelope_correlation_degraded_anchor": envelope_anchor_correlation,
        "anchor": "hard clip at 0.2, deliberately degraded control",
        "note": "Envelope correlation is a load-specific developer proxy, not STOI or listening.",
    }

    burst = [2.0] + [0.0] * (reference.FRAME_SAMPLES - 1)
    sequence = run.generate("subceiling") + [reference.f32(value) for value in burst] + \
        run.generate("subceiling")
    transitions = {
        "reset_frames": [3],
        "with_reset": case_metrics_sequence(sequence, dict(DEFAULT), "transitions-reset", [3]),
        "without_reset": case_metrics_sequence(sequence, dict(DEFAULT), "transitions-no-reset", []),
    }

    sweep = run.generate("sweep")
    clipped_sweep = reference.hard_clip(sweep, 0.5)
    clip_first = call_run_sequence(clipped_sweep, dict(DEFAULT), "clip-first")["output"]["samples"]
    interactions = {
        "limiter_only": {
            "peak_out": max(abs(value) for value in call_run(
                "sweep", dict(DEFAULT), "nonlinear-limiter")["output"]["samples"]),
        },
        "clip_then_limiter": {
            "preprocessed_sha256": reference.digest_samples(clipped_sweep),
            "output_sha256": reference.digest_samples(clip_first),
            "peak_out": max(abs(value) for value in clip_first),
            "note": "Upstream hard clip at 0.5 keeps the signal below the 0.98 ceiling; limiter stays transparent.",
        },
        "limiter_then_clip": {
            "output_sha256": reference.digest_samples(reference.hard_clip(
                call_run("sweep", dict(DEFAULT), "nonlinear-tail")["output"]["samples"], 0.5)),
            "limiter_engaged_frames": cases["sweep"]["engaged_frames"],
            "note": "Downstream clip bounds peaks while upstream engaged telemetry remains active.",
        },
        "cascaded_limiters": {
            "first": case_metrics_sequence(sweep, {"control": "peak_limiter_reference",
                                                   "ceiling": 0.9, "release_ms": 50.0},
                                           "cascade-first", []),
            "first_output_sha256": reference.digest_samples(call_run(
                "sweep", {"control": "peak_limiter_reference", "ceiling": 0.9,
                          "release_ms": 50.0}, "cascade-input")["output"]["samples"]),
            "second": case_metrics_sequence(sweep, {"control": "peak_limiter_reference",
                                                    "ceiling": 0.7, "release_ms": 50.0},
                                            "cascade-second", []),
        },
    }

    release_fast = case_metrics("impulse", {"control": "peak_limiter_reference",
                                            "ceiling": 0.98, "release_ms": 1.0}, "release-fast")
    release_slow = case_metrics("impulse", {"control": "peak_limiter_reference",
                                            "ceiling": 0.98, "release_ms": 5000.0}, "release-slow")
    recovery = {
        "fast_release_ms_1": {key: release_fast[key] for key in
                              ("recovery_sample_exact", "gain_final", "engaged_frames")},
        "slow_release_ms_5000": {key: release_slow[key] for key in
                                 ("recovery_sample_exact", "gain_final", "engaged_frames")},
        "engaged_threshold": reference.ENGAGED_THRESHOLD,
        "note": "The pinned stage never sets gain_ back to exactly 1 without reset; recovery "
                "is measured against its 0.999999 engaged threshold.",
    }

    nonfinite = cases["nonfinite"]
    adverse = {
        "nonfinite_input": {
            "status": "adverse_numerical_observed" if nonfinite["nonfinite_input_count"] else "not_observed",
            "input_nonfinite": nonfinite["nonfinite_input_count"],
            "output_nonfinite": nonfinite["nonfinite_output_count"],
            "output_sha256": nonfinite["output_sha256"],
            "note": "C++ std::min/std::max ordering maps NaN/Inf inputs to a finite clamp "
                    "value in the pinned stage; retained as observed behavior, not a quality claim.",
        },
        "control_rejections": control_rejections(),
        "unreached_recovery": {
            "status": "not_reached_within_fixture",
            "cases": ["impulse@release_ms=5000", "sweep/steps/speech_like short tails"],
            "reason": "Output stayed below the 0.999999 engaged threshold for the full "
                      "fixture; no recovery sample is reported for these cases.",
        },
        "missing_baseline": {
            "status": "not_run",
            "reason": "No matched native SDK/bench baseline, corpus or device was built in this task.",
        },
    }

    report = {
        "protocol": "sdk.peak-limiter-reference.dsp.v1",
        "evidence_kind": "synthetic_developer_only",
        "task": TASK,
        "component": "peak-limiter-reference",
        "adapter": {
            "descriptor_sha256": sha256_path(ADAPTER_PATH),
            "identity": inspect_result["identity"],
            "registration": inspect_result["registration"],
            "source_pins": pins,
        },
        "fixture_sha256": sha256_path(FIXTURE_PATH),
        "task_board": fixture_document["task_board"],
        "geometry": {
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "frame_samples": reference.FRAME_SAMPLES,
            "sample_format": "f32",
            "channels": 1,
        },
        "default_controls": dict(DEFAULT),
        "release_coefficient": reference.smoothing_coefficient(DEFAULT["release_ms"],
                                                              reference.SAMPLE_RATE_HZ),
        "cases": cases,
        "comparisons": {
            "peak_protection": {
                "sweep_peak_in": cases["sweep"]["peak_in"],
                "sweep_peak_out": cases["sweep"]["peak_out"],
                "steps_peak_in": cases["steps"]["peak_in"],
                "steps_peak_out": cases["steps"]["peak_out"],
                "impulse_peak_in": cases["impulse"]["peak_in"],
                "impulse_peak_out": cases["impulse"]["peak_out"],
                "headroom_sweep": cases["sweep"]["headroom"],
                "headroom_steps": cases["steps"]["headroom"],
                "ceiling_0_5_peak_out": cases["sweep_ceiling_0_5"]["peak_out"],
                "headroom_note": "The clamp is applied in double precision and stored as float32; "
                                 "f32(0.98) is 0.9800000190734863, so headroom can read "
                                 "-1.9073486e-8 without exceeding the float32 ceiling value.",
            },
            "transparency": transparency,
            "recovery": recovery,
            "delay": delay,
            "intelligibility_load_control": intelligibility_proxy,
            "state_transitions": transitions,
            "interacting_nonlinear": interactions,
        },
        "adverse_and_skipped": adverse,
        "baseline_comparison": {
            "status": "not_run",
            "reason": "No established-baseline parity claim: no matched native/reference "
                      "build, frozen cohort, scoring margin or runtime identity was available.",
        },
    }
    return report


def case_metrics_sequence(samples, configuration, attempt_id, resets=()):
    result = call_run_sequence(samples, configuration, attempt_id, resets)
    output = result["output"]
    return {
        "attempt_id": attempt_id,
        "reset_frames": list(resets),
        "input_sha256": reference.digest_samples(samples),
        "output_sha256": output["samples_sha256"],
        "sample_count": output["sample_count"],
        "engaged_frames": output["engaged_frames"],
        "fast_path_frames": output["fast_path_frames"],
        "gain_final": output["gain_final"],
        "reset_count": output["reset_count"],
        "frames": output["frames"],
    }


def call_run_sequence(samples, configuration, attempt_id, resets=()):
    """Drive the same adapter with a caller-owned in-memory sequence."""
    body = request("run", "caller_sequence", configuration, attempt_id, resets)
    body["stimulus_samples"] = samples
    return run.run(body)


if __name__ == "__main__":
    try:
        print(json.dumps(build_report(), sort_keys=True, separators=(",", ":"),
                         allow_nan=False))
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error) or error.__class__.__name__) from error
