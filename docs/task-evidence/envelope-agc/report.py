#!/usr/bin/env python3
"""Build the canonical DSP report by driving the task-local adapter boundary."""

import hashlib
import json
import math
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent
ADAPTER_PATH = HERE / "adapter.json"
FIXTURE_PATH = run.FIXTURE_PATH
REPORT_PATH = HERE / "fixtures" / "report.json"
TASK = "SDK-ENVELOPE-AGC"
CANDIDATE = {"kind": "reference", "id": "dsp.envelope-agc.ref", "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": run.ADAPTER_ID, "revision": 1}
DEFAULT_AGC = {
    "control": "envelope_agc_reference",
    "target_dbfs": -24.0,
    "attack_ms": 10.0,
    "release_ms": 250.0,
    "min_gain_db": -18.0,
    "max_gain_db": 18.0,
    "ceiling_dbfs": -1.0,
    "gain_smooth_hz": 8.0,
}
DEFAULT_LIMITER = {"control": "peak_limiter_reference", "ceiling": 0.98, "release_ms": 50.0}
DEFAULT_COMPRESSOR = {
    "control": "compressor_reference", "threshold_dbfs": -18.0, "ratio": 4.0,
    "attack_ms": 5.0, "release_ms": 100.0, "ceiling_dbfs": -1.0,
}
DEFAULT_STATIC = {"control": "static_gain_reference", "gain_db": 0.0, "ceiling_dbfs": -1.0}
IDENTITY = {"control": "identity"}
CEILING = reference.dbfs_to_linear(DEFAULT_AGC["ceiling_dbfs"])


def sha256_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(operation, stimulus_id, configuration, attempt_id, **extra):
    body = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": CANDIDATE,
        "adapter_ref": ADAPTER_REF,
        "configuration": configuration,
    }
    if operation == "run":
        body.update({
            "attempt_id": attempt_id,
            "stimulus_id": stimulus_id,
            "session_id": attempt_id,
            "epoch": 1,
            "reset_frames": [],
        })
    body.update(extra)
    return body


def call_run(stimulus_id, configuration, attempt_id, **extra):
    result = run.run(request("run", stimulus_id, configuration, attempt_id, **extra))
    if result["status"] != "complete":
        raise ValueError("adapter_run_incomplete:" + attempt_id)
    return result


def call_sequence(samples, configuration, attempt_id, resets=(), epoch=1,
                  continue_session=False, trace=False):
    body = request("run", "caller_sequence", configuration, attempt_id,
                   epoch=epoch, reset_frames=list(resets), continue_session=continue_session,
                   trace=trace, stimulus_samples=samples)
    return run.run(body)


def correlation(left, right):
    if len(left) != len(right) or not left:
        raise ValueError("envelope_geometry_mismatch")
    mean_l, mean_r = sum(left) / len(left), sum(right) / len(right)
    centered_l = [value - mean_l for value in left]
    centered_r = [value - mean_r for value in right]
    cross = sum(a * b for a, b in zip(centered_l, centered_r))
    norm_l = math.sqrt(sum(value * value for value in centered_l))
    norm_r = math.sqrt(sum(value * value for value in centered_r))
    return cross / (norm_l * norm_r) if norm_l and norm_r else None


def case_metrics(stimulus_id, configuration, attempt_id, resets=(), trace=False):
    samples = run.generate(stimulus_id)
    result = call_run(stimulus_id, configuration, attempt_id,
                      reset_frames=list(resets), trace=trace)
    output = result["output"]
    ceiling = configuration.get("ceiling_dbfs")
    ceiling_linear = reference.dbfs_to_linear(ceiling) if ceiling is not None else None
    if ceiling is None and configuration.get("control") == "peak_limiter_reference":
        ceiling_linear = float(configuration["ceiling"])
    modified = [index for index, (left, right) in enumerate(zip(samples, output.get("samples", [])))
                if reference._F32.pack(left) != reference._F32.pack(right)]
    finite_output = output["nonfinite_count"] == 0
    steady = output.get("samples", [])[-1600:]
    metrics = {
        "stimulus_id": stimulus_id,
        "configuration": configuration,
        "attempt_id": attempt_id,
        "reset_frames": list(resets),
        "input_sha256": reference.digest_samples(samples),
        "output_sha256": output["samples_sha256"],
        "sample_count": output["sample_count"],
        "peak_input": output["peak_input_abs"],
        "peak_output": output["peak_abs"] if finite_output else None,
        "ceiling": ceiling_linear,
        "headroom": (ceiling_linear - output["peak_abs"]
                     if ceiling_linear is not None and finite_output else None),
        "clipped_samples": output["clipped_samples"],
        "engaged_frames": output["engaged_frames"],
        "gain_db_initial": output["frames"][0]["gain_db"] if output["frames"] else None,
        "gain_db_final": output["gain_db_final"],
        "gain_db_min": output["gain_db_min"],
        "gain_db_max": output["gain_db_max"],
        "envelope_peak": output["envelope_peak"],
        "steady_state_rms_db": reference.rms_db(steady) if len(steady) == 1600 else None,
        "finite_input_count": output["sample_count"] - output["nonfinite_input_count"],
        "nonfinite_input_count": output["nonfinite_input_count"],
        "finite_output_count": output["finite_count"],
        "nonfinite_output_count": output["nonfinite_count"],
        "first_modified_sample": modified[0] if modified else None,
        "frames": output["frames"],
        "status": result["status"],
        "errors": result["errors"],
    }
    if "gain_trace_sha256" in output:
        metrics["gain_trace_sha256"] = output["gain_trace_sha256"]
        trace_values = output["gain_trace"]
        loud_start = 1600 if stimulus_id == "overshoot" else None
        loud_end = 2400 if stimulus_id == "overshoot" else None
        if loud_start is not None and len(trace_values) > loud_end:
            quiet_gain = trace_values[loud_start - 1]
            attack = next((index for index in range(loud_start, len(trace_values))
                           if trace_values[index] <= quiet_gain - 6.0), None)
            release = next((index for index in range(loud_end, len(trace_values))
                            if trace_values[index] >= quiet_gain - 3.0), None)
            metrics["attack_release"] = {
                "quiet_reference_gain_db": quiet_gain,
                "gain_reduction_threshold_db": 6.0,
                "attack_sample": attack,
                "attack_ms": (attack - loud_start) / 16.0 if attack is not None else None,
                "release_threshold_db": 3.0,
                "release_sample_from_loud_end": (release - loud_end) if release is not None else None,
                "release_status": "observed" if release is not None else "not_reached_within_fixture",
            }
    return metrics


def control_rejections():
    probes = (
        ("missing_target_dbfs", {key: value for key, value in DEFAULT_AGC.items()
                                 if key != "target_dbfs"}),
        ("attack_zero", dict(DEFAULT_AGC, attack_ms=0.0)),
        ("attack_over_range", dict(DEFAULT_AGC, attack_ms=201.0)),
        ("release_zero", dict(DEFAULT_AGC, release_ms=0.0)),
        ("release_over_range", dict(DEFAULT_AGC, release_ms=2001.0)),
        ("target_below_range", dict(DEFAULT_AGC, target_dbfs=-70.0)),
        ("target_positive", dict(DEFAULT_AGC, target_dbfs=3.0)),
        ("ceiling_positive", dict(DEFAULT_AGC, ceiling_dbfs=1.0)),
        ("ceiling_below_range", dict(DEFAULT_AGC, ceiling_dbfs=-20.0)),
        ("unknown_control_key", dict(DEFAULT_AGC, lookahead_ms=0.0)),
        ("boolean_attack", dict(DEFAULT_AGC, attack_ms=True)),
        ("string_release", dict(DEFAULT_AGC, release_ms="250")),
        ("nonfinite_target", dict(DEFAULT_AGC, target_dbfs=math.nan)),
        ("infinite_release", dict(DEFAULT_AGC, release_ms=math.inf)),
        ("inverted_gain_bounds", dict(DEFAULT_AGC, min_gain_db=1.0, max_gain_db=0.0)),
    )
    results = {}
    for name, config in probes:
        try:
            call_run("fixed_tone", config, "reject-" + name)
            results[name] = {"status": "unexpectedly_accepted", "reason": None}
        except (run.RequestError, reference.ControlError, ValueError) as error:
            results[name] = {"status": "rejected", "reason": str(error) or error.__class__.__name__}

    nan_path = Path(__file__).resolve().parent / "fixtures" / "nan-probe.json"
    temporary = nan_path.with_suffix(".json.tmp")
    temporary.write_text('{"target_dbfs": NaN}\n', encoding="ascii")
    try:
        run.read_json(temporary)
        results["json_nan_constant"] = {"status": "unexpectedly_accepted", "reason": None}
    except run.RequestError as error:
        results["json_nan_constant"] = {"status": "rejected", "reason": str(error)}
    finally:
        temporary.unlink(missing_ok=True)
    return results


def frame_shape_controls():
    results = {}
    samples = run.generate("fixed_tone")[:159]
    try:
        call_sequence(samples, DEFAULT_AGC, "reject-short-boundary")
        results["boundary_short_frame"] = {"status": "unexpectedly_accepted"}
    except (run.RequestError, ValueError) as error:
        results["boundary_short_frame"] = {"status": "rejected", "reason": str(error)}
    try:
        reference.EnvelopeAGC(DEFAULT_AGC).process([0.0] * 159)
        results["reference_short_frame"] = {"status": "unexpectedly_accepted"}
    except ValueError as error:
        results["reference_short_frame"] = {"status": "rejected", "reason": str(error)}
    return results


def epoch_and_session_controls():
    samples = run.generate("fixed_tone")
    first, second = samples[:1600], samples[1600:]
    one_shot = call_sequence(samples, DEFAULT_AGC, "session-one-shot")
    body = request("run", "caller_sequence", DEFAULT_AGC, "session-split",
                   epoch=5, reset_frames=[], stimulus_samples=first)
    split_first = run.run(body)
    stale_rejected = False
    stale_reason = None
    try:
        run.run(request("run", "caller_sequence", DEFAULT_AGC, "session-split",
                        epoch=4, reset_frames=[], stimulus_samples=second))
    except run.RequestError as error:
        stale_rejected = True
        stale_reason = str(error)
    split_second = run.run(request(
        "run", "caller_sequence", DEFAULT_AGC, "session-split",
        epoch=5, reset_frames=[], continue_session=True, stimulus_samples=second))
    epoch_advance = run.run(request(
        "run", "caller_sequence", DEFAULT_AGC, "session-split",
        epoch=6, reset_frames=[], continue_session=True, stimulus_samples=first))

    # Cross-session leakage: finish a different session in between, then resume
    # session A at its advanced epoch; the rejoined digest must still match the
    # uninterrupted one-shot.
    call_sequence(run.generate("steps"), DEFAULT_AGC, "session-other")
    resumed = run.run(request(
        "run", "caller_sequence", DEFAULT_AGC, "session-split",
        epoch=6, reset_frames=[], continue_session=True, stimulus_samples=second))
    rejoined_digest = reference.digest_samples(
        split_first["output"]["samples"] + resumed["output"]["samples"])

    expected_second = one_shot["output"]["samples"][len(first):]
    return {
        "stale_epoch": {
            "status": "rejected" if stale_rejected else "unexpectedly_accepted",
            "reason": stale_reason,
            "state_unchanged_digest_match": (split_second["output"]["samples_sha256"] ==
                                             reference.digest_samples(expected_second)),
        },
        "epoch_advance": {
            "status": "observed",
            "epoch": epoch_advance["session_state"]["epoch"],
            "transition": epoch_advance["session_state"]["transitions"][-1],
            "digest": epoch_advance["output"]["samples_sha256"],
        },
        "state_leakage_across_sessions": {
            "status": "observed" if rejoined_digest == one_shot["output"]["samples_sha256"] else "failed",
            "one_shot_sha256": one_shot["output"]["samples_sha256"],
            "split_first_sha256": split_first["output"]["samples_sha256"],
            "resumed_second_segment_sha256": resumed["output"]["samples_sha256"],
            "rejoined_sha256": rejoined_digest,
            "note": "Sessions are keyed by session_id plus canonical control digest.",
        },
    }


def state_transition_control():
    quiet = [reference.f32(0.005 * math.sin(2.0 * math.pi * 1000.0 * i / 16000.0))
             for i in range(800)]
    loud = [reference.f32(1.2 * math.sin(2.0 * math.pi * 1000.0 * i / 16000.0))
            for i in range(800)]
    sequence = quiet + loud + quiet
    with_reset = call_sequence(sequence, DEFAULT_AGC, "transition-reset", resets=[10])
    without_reset = call_sequence(sequence, DEFAULT_AGC, "transition-no-reset")
    return {
        "reset_frames": [10],
        "with_reset": {
            "output_sha256": with_reset["output"]["samples_sha256"],
            "reset_count": with_reset["output"]["reset_count"],
            "gain_db_final": with_reset["output"]["gain_db_final"],
            "clipped_samples": with_reset["output"]["clipped_samples"],
        },
        "without_reset": {
            "output_sha256": without_reset["output"]["samples_sha256"],
            "reset_count": without_reset["output"]["reset_count"],
            "gain_db_final": without_reset["output"]["gain_db_final"],
            "clipped_samples": without_reset["output"]["clipped_samples"],
        },
        "distinct": (with_reset["output"]["samples_sha256"] !=
                     without_reset["output"]["samples_sha256"]),
    }


def interaction_summary(result):
    output = result["output"]
    return {
        "output_sha256": output["samples_sha256"],
        "peak_output": output["peak_abs"],
        "clipped_samples": output["clipped_samples"],
        "engaged_frames": output["engaged_frames"],
        "gain_db_final": output["gain_db_final"],
        "nonfinite_output_count": output["nonfinite_count"],
        "reset_count": output["reset_count"],
    }


def interacting_nonlinear_controls():
    samples = run.generate("overshoot")
    agc = call_run("overshoot", DEFAULT_AGC, "nonlinear-agc-only")
    limiter = call_run("overshoot", DEFAULT_LIMITER, "nonlinear-limiter-only")
    compressor = call_run("overshoot", DEFAULT_COMPRESSOR, "nonlinear-compressor-only")
    stages = {
        "agc_only": (DEFAULT_AGC, agc),
        "limiter_only": (DEFAULT_LIMITER, limiter),
        "compressor_only": (DEFAULT_COMPRESSOR, compressor),
    }
    for name, first_config, first_result in (
            ("agc_then_limiter", DEFAULT_AGC, agc),
            ("agc_then_compressor", DEFAULT_AGC, agc),
            ("limiter_then_agc", DEFAULT_LIMITER, limiter),
            ("compressor_then_agc", DEFAULT_COMPRESSOR, compressor)):
        first_output = first_result["output"]["samples"]
        if name.endswith("limiter"):
            second_config = DEFAULT_LIMITER
        elif name.endswith("compressor"):
            second_config = DEFAULT_COMPRESSOR
        else:
            second_config = DEFAULT_AGC
        second = call_sequence(first_output, second_config, "nonlinear-" + name)
        stages[name] = (second_config, second)
    result = {name: interaction_summary(item[1]) for name, item in stages.items()}
    result["input_sha256"] = reference.digest_samples(samples)
    digests = [item["output_sha256"] for item in result.values()
               if isinstance(item, dict) and "output_sha256" in item]
    result["configuration_count"] = len(digests)
    result["distinct_output_count"] = len(set(digests))
    result["all_present"] = len(digests) == 7 and all(len(item) == 64 for item in digests)
    result["note"] = ("Static sequence chaining through the adapter boundary only; "
                      "agc_then_limiter is expected to equal agc_only when the AGC ceiling "
                      "already keeps every sample below the limiter ceiling. No native "
                      "chain, real-time interaction or listening claim.")
    return result


def load_control():
    clean = run.generate("clean_speech_like")
    stepped = run.generate("gain_step_speech")
    agc_output = call_run("gain_step_speech", DEFAULT_AGC, "load-agc")["output"]["samples"]
    identity_output = call_run("gain_step_speech", IDENTITY, "load-identity")["output"]["samples"]
    static_output = call_run("gain_step_speech", DEFAULT_STATIC, "load-static")["output"]["samples"]
    window = 6400  # 400 ms, matching the published synthetic gain-step protocol

    def rms_error(output):
        target = reference.windowed_rms_db(clean, window)
        measured = reference.windowed_rms_db(output, window)
        pairs = [(abs(left - right), weight) for left, right, weight in
                 zip(target, measured, reference.windowed_rms_db(clean, window))]
        usable = [(error, weight) for error, weight in pairs if weight > -55.0]
        return sum(error for error, _ in usable) / len(usable) if usable else None

    envelope_input = reference.windowed_rms_db(clean, 320)
    return {
        "stimulus": "deterministic harmonic-burst synthetic speech with +/-9 dB gain steps",
        "control_window_samples": window,
        "windowed_rms_abs_error_db_agc": rms_error(agc_output),
        "windowed_rms_abs_error_db_identity": rms_error(identity_output),
        "windowed_rms_abs_error_db_static_gain": rms_error(static_output),
        "envelope_correlation_clean_vs_stepped_input": correlation(
            envelope_input, reference.windowed_rms_db(stepped, 320)),
        "envelope_correlation_clean_vs_agc_output": correlation(
            envelope_input, reference.windowed_rms_db(agc_output, 320)),
        "envelope_correlation_clean_vs_identity": correlation(
            envelope_input, reference.windowed_rms_db(identity_output, 320)),
        "note": ("Load-specific gain-step tracking proxy only. Not STOI, SI-SDR, "
                 "intelligibility, listening, CPU load or deadline evidence."),
    }


def sweep_response():
    samples = run.generate("sweep")
    output = call_run("sweep", DEFAULT_AGC, "sweep-response")["output"]["samples"]
    bands = []
    width = len(samples) // 8
    for index in range(8):
        begin, end = index * width, (index + 1) * width
        in_rms = reference.rms_db(samples[begin:end])
        out_rms = reference.rms_db(output[begin:end])
        bands.append({"band": index, "samples": [begin, end],
                      "input_rms_db": in_rms, "output_rms_db": out_rms,
                      "rms_ratio_db": out_rms - in_rms})
    return {"bands": bands, "note": "Chirp band RMS ratios are nonlinear response summaries, not a linear transfer function."}


def build_report():
    fixture_document = run.fixture()
    inspect_result = run.inspect(request("inspect", None, dict(DEFAULT_AGC), "inspect"))
    cases = {}
    stimulus_configs = {
        "sweep": dict(DEFAULT_AGC),
        "steps": dict(DEFAULT_AGC),
        "impulse": dict(DEFAULT_AGC),
        "silence": dict(DEFAULT_AGC),
        "fixed_tone": dict(DEFAULT_AGC),
        "clean_speech_like": dict(DEFAULT_AGC),
        "gain_step_speech": dict(DEFAULT_AGC),
        "overshoot": dict(DEFAULT_AGC),
        "nonfinite": dict(DEFAULT_AGC),
    }
    for stimulus_id, config in stimulus_configs.items():
        cases[stimulus_id] = case_metrics(
            stimulus_id, config, "case-" + stimulus_id,
            trace=stimulus_id in ("overshoot", "impulse", "fixed_tone"))
    cases["sweep_ceiling_minus_6"] = case_metrics(
        "sweep", dict(DEFAULT_AGC, ceiling_dbfs=-6.0), "case-sweep-ceiling-minus-6")
    cases["impulse_fast_attack"] = case_metrics(
        "impulse", dict(DEFAULT_AGC, attack_ms=0.5), "case-impulse-fast-attack")
    cases["impulse_slow_release"] = case_metrics(
        "impulse", dict(DEFAULT_AGC, release_ms=1000.0), "case-impulse-slow-release")

    impulse_input = run.generate("impulse")
    impulse_output = call_run("impulse", DEFAULT_AGC, "delay-impulse")["output"]["samples"]
    in_peak = max(range(len(impulse_input)), key=lambda i: abs(impulse_input[i]))
    out_peak = max(range(len(impulse_output)), key=lambda i: abs(impulse_output[i]))
    delay = {
        "input_peak_sample": in_peak,
        "output_peak_sample": out_peak,
        "content_delay_samples": out_peak - in_peak,
        "lookahead_samples": 0,
        "note": ("Per-sample causal AGC plus hard ceiling; content delay is not "
                 "availability latency or acoustic phase/group delay."),
    }

    blockers = [
        {
            "id": "real_speech_qualification",
            "status": "blocked",
            "reason": ("No rights-cleared, matched real-speech cohort, natural microphone "
                       "capture or independently scored quality/intelligibility run is available."),
        },
        {
            "id": "listening_and_stoi",
            "status": "blocked",
            "reason": "No listening panel, listener rating or STOI scoring runtime is available in this fixture.",
        },
        {
            "id": "native_provider_and_baseline",
            "status": "blocked",
            "reason": ("No matched native SDK provider build, installed archive or established "
                       "AGC baseline was built here; no parity claim is made."),
        },
        {
            "id": "target_device_and_deadline",
            "status": "blocked",
            "reason": "No target device, paced callback run, CPU/RTF budget or deadline budget is available.",
        },
        {
            "id": "nonlinear_interaction_realtime",
            "status": "blocked",
            "reason": ("Only in-memory static chains of reference controls were exercised; "
                       "native limiter/compressor interaction and real-time qualification are frozen."),
        },
    ]

    report = {
        "protocol": "sdk.envelope-agc.dsp.v1",
        "evidence_kind": "synthetic_developer_only",
        "status": "proposal_only_synthetic",
        "qualification_status": "incomplete",
        "task": TASK,
        "component": "envelope-agc",
        "adapter": {
            "descriptor_sha256": sha256_path(ADAPTER_PATH),
            "identity": inspect_result["identity"],
            "registration": inspect_result["registration"],
            "supported_controls": inspect_result["supported_controls"],
            "source_pins": fixture_document["source_pins"],
        },
        "fixture_sha256": sha256_path(FIXTURE_PATH),
        "task_board": fixture_document["task_board"],
        "geometry": fixture_document["geometry"],
        "default_controls": dict(DEFAULT_AGC),
        "attack_coefficient": math.exp(-1000.0 / (16000.0 * DEFAULT_AGC["attack_ms"])),
        "release_coefficient": math.exp(-1000.0 / (16000.0 * DEFAULT_AGC["release_ms"])),
        "gain_smoothing_section": {
            "b0": math.tan(math.pi * DEFAULT_AGC["gain_smooth_hz"] / 16000.0) /
                  (1.0 + math.tan(math.pi * DEFAULT_AGC["gain_smooth_hz"] / 16000.0)),
            "note": "First-order bilinear-transformed lowpass in the log-gain domain.",
        },
        "cases": cases,
        "comparisons": {
            "response": sweep_response(),
            "delay": delay,
            "load_and_gain_step_control": load_control(),
            "state_transitions": state_transition_control(),
            "interacting_nonlinear": interacting_nonlinear_controls(),
        },
        "adverse_and_skipped": {
            "control_rejections": control_rejections(),
            "frame_shape": frame_shape_controls(),
            "epoch_and_sessions": epoch_and_session_controls(),
            "nonfinite_input": {
                "status": "adverse_numerical_observed",
                "input_nonfinite": cases["nonfinite"]["nonfinite_input_count"],
                "output_nonfinite": cases["nonfinite"]["nonfinite_output_count"],
                "output_sha256": cases["nonfinite"]["output_sha256"],
                "note": ("C++-style min/max ordering maps NaN/Inf inputs to the finite hard "
                         "ceiling. This is an observation, not a robustness endorsement."),
            },
            "silence_handling": {
                "status": "observed",
                "peak_output": cases["silence"]["peak_output"],
                "gain_db_final": cases["silence"]["gain_db_final"],
                "note": ("Silence drives the envelope to zero and the desired gain to its "
                         "18 dB bound with zero output; raising gain during pauses is a known risk."),
            },
            "peak_overshoot": {
                "status": "observed",
                "clipped_samples": cases["overshoot"]["clipped_samples"],
                "peak_output": cases["overshoot"]["peak_output"],
                "ceiling": CEILING,
                "attack_release": cases["overshoot"].get("attack_release"),
                "note": ("Level bursts can demand more gain reduction than the 8 Hz log-domain "
                         "smoother can apply immediately; the hard ceiling is the observable guard."),
            },
            "unreached_recovery": {
                "status": "not_reached_within_fixture",
                "cases": ["overshoot@release_ms=250", "impulse@release_ms=1000"],
                "reason": "Gain did not return to the quiet reference within the fixed-length fixture.",
            },
            "missing_native_or_real_qualification": {"status": "not_run", "blockers": blockers},
        },
        "baseline_comparison": {
            "status": "not_qualified",
            "reason": ("Identity and static-gain synthetic controls are reported; no established "
                       "baseline parity, frozen cohort or listening acceptance is claimed."),
        },
        "blockers": blockers,
        "counts": {
            "stimuli": len(fixture_document["stimuli"]),
            "cases": len(cases),
            "source_pins": len(fixture_document["source_pins"]),
            "control_rejection_probes": 16,
            "frame_shape_probes": 2,
            "epoch_session_probes": 4,
            "interaction_configurations": 7,
            "blockers": len(blockers),
        },
    }
    return report


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


if __name__ == "__main__":
    try:
        import sys
        sys.stdout.buffer.write(canonical_bytes(build_report()))
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error) or error.__class__.__name__) from error
