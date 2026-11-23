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
TASK = "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING"
CANDIDATE = {"kind": "reference", "id": "dsp.static-target-gain-with-peak-ceiling.ref",
             "revision": 1}
ADAPTER_REF = {"kind": "adapter", "id": run.ADAPTER_ID, "revision": 1}
DEFAULT_TARGET = {
    "control": "static_target_gain_reference",
    "target_dbfs": -24.0,
    "min_gain_db": -18.0,
    "max_gain_db": 18.0,
    "ceiling_dbfs": -1.0,
    "silence_floor_dbfs": -50.0,
}
IDENTITY = {"control": "identity"}
FIXED_MATCHED = {"control": "fixed_gain_reference", "gain_db": -12.0, "ceiling_dbfs": -1.0}
CEILING = reference.dbfs_to_linear(DEFAULT_TARGET["ceiling_dbfs"])


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
    modified = [index for index, (left, right) in enumerate(
        zip(samples, output.get("samples", [])))
        if reference._F32.pack(left) != reference._F32.pack(right)]
    finite_output = output["nonfinite_count"] == 0
    steady = output.get("samples", [])[-1600:]
    plan = output["plans"][0] if output["plans"] else None
    metrics = {
        "stimulus_id": stimulus_id,
        "configuration": configuration,
        "attempt_id": attempt_id,
        "reset_frames": list(resets),
        "input_sha256": reference.digest_samples(samples),
        "output_sha256": output["samples_sha256"],
        "sample_count": output["sample_count"],
        "input_rms_db": reference.rms_db(samples),
        "output_rms_db": (reference.rms_db(output["samples"])
                          if "samples" in output else None),
        "steady_state_rms_db": reference.rms_db(steady) if len(steady) == 1600 else None,
        "peak_input": output["peak_input_abs"],
        "peak_output": output["peak_abs"] if finite_output else None,
        "ceiling": ceiling_linear,
        "headroom": (ceiling_linear - output["peak_abs"]
                     if ceiling_linear is not None and finite_output else None),
        "clipped_samples": output["clipped_samples"],
        "gain_db_plan": plan["gain_db"] if plan else None,
        "gain_db_min": output["gain_db_min"],
        "gain_db_max": output["gain_db_max"],
        "desired_gain_db_unbounded": plan["desired_gain_db_unbounded"] if plan else None,
        "silence_bypass": plan["silence_bypass"] if plan else None,
        "numerical_fallback": plan["numerical_fallback"] if plan else None,
        "finite_input_count": output["sample_count"] - output["nonfinite_input_count"],
        "nonfinite_input_count": output["nonfinite_input_count"],
        "finite_output_count": output["finite_count"],
        "nonfinite_output_count": output["nonfinite_count"],
        "first_modified_sample": modified[0] if modified else None,
        "reset_count": output["reset_count"],
        "frames": output["frames"],
        "plans": output["plans"],
        "status": result["status"],
        "errors": result["errors"],
    }
    if "gain_trace_sha256" in output:
        metrics["gain_trace_sha256"] = output["gain_trace_sha256"]
    return metrics


def expected_gain_db(samples, configuration, respect_silence_floor=False):
    rms = reference.rms_linear(samples)
    if (respect_silence_floor and
            reference.linear_to_dbfs(rms) <= configuration["silence_floor_dbfs"]):
        return 0.0
    target = reference.dbfs_to_linear(configuration["target_dbfs"])
    desired = target / max(rms, reference.RMS_FLOOR_LINEAR)
    gain = reference.cpp_max(reference.dbfs_to_linear(configuration["min_gain_db"]),
                             reference.cpp_min(reference.dbfs_to_linear(configuration["max_gain_db"]),
                                               desired))
    return reference.linear_to_dbfs(gain)


def level_sweep():
    fixture = run.fixture()
    parameters = fixture["parameters"]
    rows = []
    for level_db in parameters["level_sweep_db"]:
        amplitude = 10.0 ** (level_db / 20.0)
        samples = [reference.f32(amplitude * math.sin(2.0 * math.pi * 1000.0 * i / 16000.0))
                   for i in range(3200)]
        output = call_sequence(samples, dict(DEFAULT_TARGET),
                               "level-sweep-" + str(level_db))["output"]
        plan = output["plans"][0]
        rows.append({
            "level_db": level_db,
            "input_rms_db": reference.rms_db(samples),
            "desired_gain_db_unbounded": plan["desired_gain_db_unbounded"],
            "gain_db": plan["gain_db"],
            "gain_db_expected": expected_gain_db(samples, DEFAULT_TARGET,
                                                  respect_silence_floor=True),
            "output_rms_db": reference.rms_db(output["samples"]),
            "clipped_samples": output["clipped_samples"],
            "peak_output": output["peak_abs"],
            "headroom": CEILING - output["peak_abs"],
            "output_sha256": output["samples_sha256"],
        })
    return {
        "rows": rows,
        "target_dbfs": DEFAULT_TARGET["target_dbfs"],
        "bounds_db": [DEFAULT_TARGET["min_gain_db"], DEFAULT_TARGET["max_gain_db"]],
        "note": ("Independent deterministic 1 kHz tone levels; gain is recomputed per call. "
                 "Rows at the bounds demonstrate bounded scaling, not target convergence; "
                 "the lowest row is suppressed by the explicit silence floor."),
    }


def target_sweep():
    fixture = run.fixture()
    samples = run.generate("fixed_tone")
    rows = []
    for target_dbfs in fixture["parameters"]["target_sweep_dbfs"]:
        config = dict(DEFAULT_TARGET, target_dbfs=target_dbfs)
        output = call_run("fixed_tone", config,
                          "target-sweep-" + str(target_dbfs))["output"]
        plan = output["plans"][0]
        rows.append({
            "target_dbfs": target_dbfs,
            "input_rms_db": reference.rms_db(samples),
            "gain_db": plan["gain_db"],
            "gain_db_expected": expected_gain_db(samples, config),
            "output_rms_db": reference.rms_db(output["samples"]),
            "clipped_samples": output["clipped_samples"],
            "peak_output": output["peak_abs"],
            "headroom": CEILING - output["peak_abs"],
            "output_sha256": output["samples_sha256"],
        })
    return {
        "rows": rows,
        "bounds_db": [DEFAULT_TARGET["min_gain_db"], DEFAULT_TARGET["max_gain_db"]],
        "note": ("Fixed synthetic tone with varied explicit target; bound-limited rows are "
                 "reported as limit cases and never promoted as converged targets."),
    }


def ceiling_sweep():
    fixture = run.fixture()
    rows = []
    for stimulus_id in ("impulse", "overshoot"):
        samples = run.generate(stimulus_id)
        for ceiling_dbfs in fixture["parameters"]["ceiling_sweep_dbfs"]:
            config = dict(DEFAULT_TARGET, ceiling_dbfs=ceiling_dbfs)
            output = call_run(stimulus_id, config,
                              "ceiling-" + stimulus_id + "-" + str(ceiling_dbfs))["output"]
            ceiling = reference.dbfs_to_linear(ceiling_dbfs)
            rows.append({
                "stimulus_id": stimulus_id,
                "ceiling_dbfs": ceiling_dbfs,
                "ceiling": ceiling,
                "peak_output": output["peak_abs"],
                "headroom": ceiling - output["peak_abs"],
                "clipped_samples": output["clipped_samples"],
                "input_rms_db": reference.rms_db(samples),
                "gain_db": output["plans"][0]["gain_db"],
                "output_sha256": output["samples_sha256"],
            })
    return {
        "rows": rows,
        "note": ("Hard clamp after scaling; impulse and overshoot cases include limiting. "
                 "Float32 rounding may leave a few 1e-8 units of measured headroom."),
    }


def response():
    samples = run.generate("sweep")
    output = call_run("sweep", dict(DEFAULT_TARGET), "sweep-response")["output"]["samples"]
    bands = []
    width = len(samples) // 8
    for index in range(8):
        begin, end = index * width, (index + 1) * width
        in_rms = reference.rms_db(samples[begin:end])
        out_rms = reference.rms_db(output[begin:end])
        bands.append({"band": index, "samples": [begin, end],
                      "input_rms_db": in_rms, "output_rms_db": out_rms,
                      "rms_ratio_db": out_rms - in_rms})
    return {"bands": bands,
            "note": ("Chirp band RMS ratios describe a static gain over nonlinear clipping; "
                     "not a linear transfer function or EQ measurement.")}


def delay():
    samples = run.generate("impulse")
    output = call_run("impulse", dict(DEFAULT_TARGET), "delay-impulse")["output"]["samples"]
    in_peak = max(range(len(samples)), key=lambda i: abs(samples[i]))
    out_peak = max(range(len(output)), key=lambda i: abs(output[i]))
    return {
        "input_peak_sample": in_peak,
        "output_peak_sample": out_peak,
        "content_delay_samples": out_peak - in_peak,
        "lookahead_samples": 0,
        "note": ("Static per-segment scaling with a hard clamp has no lookahead; content "
                 "delay is not availability latency or acoustic phase/group delay."),
    }


def control_rejections():
    probes = (
        ("missing_target_dbfs", {key: value for key, value in DEFAULT_TARGET.items()
                                 if key != "target_dbfs"}),
        ("missing_silence_floor_dbfs", {key: value for key, value in DEFAULT_TARGET.items()
                                        if key != "silence_floor_dbfs"}),
        ("target_below_range", dict(DEFAULT_TARGET, target_dbfs=-70.0)),
        ("target_positive", dict(DEFAULT_TARGET, target_dbfs=3.0)),
        ("min_gain_below_range", dict(DEFAULT_TARGET, min_gain_db=-40.0)),
        ("max_gain_above_range", dict(DEFAULT_TARGET, max_gain_db=40.0)),
        ("inverted_gain_bounds", dict(DEFAULT_TARGET, min_gain_db=1.0, max_gain_db=0.0)),
        ("ceiling_positive", dict(DEFAULT_TARGET, ceiling_dbfs=1.0)),
        ("ceiling_below_range", dict(DEFAULT_TARGET, ceiling_dbfs=-20.0)),
        ("silence_floor_below_range", dict(DEFAULT_TARGET, silence_floor_dbfs=-90.0)),
        ("unknown_control_key", dict(DEFAULT_TARGET, lookahead_ms=0.0)),
        ("boolean_target", dict(DEFAULT_TARGET, target_dbfs=True)),
        ("string_max_gain", dict(DEFAULT_TARGET, max_gain_db="18")),
        ("nonfinite_target", dict(DEFAULT_TARGET, target_dbfs=math.nan)),
        ("infinite_ceiling", dict(DEFAULT_TARGET, ceiling_dbfs=math.inf)),
        ("control_mismatch", dict(DEFAULT_TARGET, control="identity")),
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
        call_sequence(samples, dict(DEFAULT_TARGET), "reject-short-boundary")
        results["boundary_short_frame"] = {"status": "unexpectedly_accepted"}
    except (run.RequestError, ValueError) as error:
        results["boundary_short_frame"] = {"status": "rejected", "reason": str(error)}
    try:
        processor = reference.StaticTargetGain(dict(DEFAULT_TARGET))
        processor.process_frame([0.0] * 159, processor.plan([0.0] * 159))
        results["reference_short_frame"] = {"status": "unexpectedly_accepted"}
    except ValueError as error:
        results["reference_short_frame"] = {"status": "rejected", "reason": str(error)}
    return results


def epoch_and_sessions():
    samples = run.generate("fixed_tone")
    first, second = samples[:1600], samples[1600:]
    one_shot = call_sequence(samples, dict(DEFAULT_TARGET), "session-one-shot")
    split_first = call_sequence(first, dict(DEFAULT_TARGET), "session-split", epoch=5)
    stale_rejected = False
    stale_reason = None
    try:
        call_sequence(second, dict(DEFAULT_TARGET), "session-split", epoch=4,
                      continue_session=True)
    except run.RequestError as error:
        stale_rejected = True
        stale_reason = str(error)
    split_second = call_sequence(second, dict(DEFAULT_TARGET), "session-split", epoch=5,
                                 continue_session=True)
    epoch_advance = call_sequence(first, dict(DEFAULT_TARGET), "session-split", epoch=6,
                                  continue_session=True)

    call_sequence(run.generate("steps"), dict(DEFAULT_TARGET), "session-other")
    resumed = call_sequence(second, dict(DEFAULT_TARGET), "session-split", epoch=6,
                            continue_session=True)
    rejoined_digest = reference.digest_samples(
        split_first["output"]["samples"] + resumed["output"]["samples"])
    expected_second = one_shot["output"]["samples"][len(first):]
    expected_second_digest = reference.digest_samples(expected_second)
    resumed_digest = resumed["output"]["samples_sha256"]
    split_second_digest = split_second["output"]["samples_sha256"]
    no_leakage = split_second_digest == expected_second_digest == resumed_digest
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
            "buffered_frames": epoch_advance["session_state"]["buffered_frames"],
            "transition": epoch_advance["session_state"]["transitions"][-1],
            "digest": epoch_advance["output"]["samples_sha256"],
        },
        "state_leakage_across_sessions": {
            "status": "observed" if no_leakage else "failed",
            "one_shot_sha256": one_shot["output"]["samples_sha256"],
            "split_first_sha256": split_first["output"]["samples_sha256"],
            "split_second_segment_sha256": split_second_digest,
            "expected_second_segment_sha256": expected_second_digest,
            "resumed_second_segment_sha256": resumed_digest,
            "rejoined_sha256": rejoined_digest,
            "full_rejoined_matches_one_shot": (rejoined_digest ==
                                              one_shot["output"]["samples_sha256"]),
            "note": ("Sessions are keyed by session_id plus canonical control digest; "
                     "continued calls replay buffered samples before emitting the new suffix. "
                     "The first segment of a split call is provisional because its gain was "
                     "computed before the later samples existed; only the replayed suffix is "
                     "expected to match the one-shot result."),
        },
    }


def state_transitions():
    samples = run.generate("overshoot")
    with_reset = call_sequence(samples, dict(DEFAULT_TARGET), "transition-reset",
                               resets=[10])
    without_reset = call_sequence(samples, dict(DEFAULT_TARGET), "transition-no-reset")
    return {
        "reset_frames": [10],
        "with_reset": {
            "output_sha256": with_reset["output"]["samples_sha256"],
            "reset_count": with_reset["output"]["reset_count"],
            "segments": with_reset["output"]["plans"],
            "clipped_samples": with_reset["output"]["clipped_samples"],
        },
        "without_reset": {
            "output_sha256": without_reset["output"]["samples_sha256"],
            "reset_count": without_reset["output"]["reset_count"],
            "segments": without_reset["output"]["plans"],
            "clipped_samples": without_reset["output"]["clipped_samples"],
        },
        "distinct": (with_reset["output"]["samples_sha256"] !=
                     without_reset["output"]["samples_sha256"]),
        "note": ("A reset splits the static measurement window. There is no adaptive state "
                 "inside a segment; reset changes the measured RMS and the resulting gain."),
    }


def interaction_summary(result):
    output = result["output"]
    return {
        "output_sha256": output["samples_sha256"],
        "peak_output": output["peak_abs"],
        "clipped_samples": output["clipped_samples"],
        "gain_db_final": output["gain_db_final"],
        "nonfinite_output_count": output["nonfinite_count"],
        "reset_count": output["reset_count"],
        "segment_count": len(output["plans"]),
    }


def interacting_nonlinear_controls():
    samples = run.generate("overshoot")
    target_only = call_sequence(samples, dict(DEFAULT_TARGET), "nonlinear-target-only")
    fixed_only = call_sequence(samples, dict(FIXED_MATCHED), "nonlinear-fixed-only")
    low_ceiling = dict(DEFAULT_TARGET, ceiling_dbfs=-12.0)
    stages = {
        "target_only": target_only,
        "fixed_only": fixed_only,
        "target_then_fixed": call_sequence(
            target_only["output"]["samples"], dict(FIXED_MATCHED),
            "nonlinear-target-then-fixed"),
        "fixed_then_target": call_sequence(
            fixed_only["output"]["samples"], dict(DEFAULT_TARGET),
            "nonlinear-fixed-then-target"),
        "low_ceiling_target_then_target": call_sequence(
            call_sequence(samples, low_ceiling, "nonlinear-low-ceiling")["output"]["samples"],
            dict(DEFAULT_TARGET), "nonlinear-low-ceiling-then-target"),
        "identity_then_target": call_sequence(
            call_sequence(samples, dict(IDENTITY), "nonlinear-identity")["output"]["samples"],
            dict(DEFAULT_TARGET), "nonlinear-identity-then-target"),
    }
    result = {name: interaction_summary(item) for name, item in stages.items()}
    digests = [item["output_sha256"] for item in result.values()]
    result["input_sha256"] = reference.digest_samples(samples)
    result["configuration_count"] = len(digests)
    result["distinct_output_count"] = len(set(digests))
    result["all_present"] = len(digests) == 6 and all(len(item) == 64 for item in digests)
    result["identity_transparent"] = (
        result["identity_then_target"]["output_sha256"] ==
        result["target_only"]["output_sha256"])
    result["note"] = ("Static chaining through the adapter boundary only. The hard ceiling "
                      "and sequence-static RMS make stage order observable; no native chain, "
                      "real-time interaction or listening claim is made.")
    return result


def load_control():
    clean = run.generate("clean_speech_like")
    stepped = run.generate("gain_step_speech")
    target_output = call_run("gain_step_speech", dict(DEFAULT_TARGET),
                             "load-target")["output"]["samples"]
    identity_output = call_run("gain_step_speech", dict(IDENTITY),
                               "load-identity")["output"]["samples"]
    matched_gain = max(-36.0, min(36.0, reference.rms_db(clean) - reference.rms_db(stepped)))
    matched_config = {"control": "fixed_gain_reference", "gain_db": matched_gain,
                      "ceiling_dbfs": -1.0}
    matched_output = call_run("gain_step_speech", matched_config,
                              "load-energy-matched")["output"]["samples"]
    window = run.fixture()["parameters"]["window_samples"]

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
        "energy_matched_gain_db": matched_gain,
        "windowed_rms_abs_error_db_target": rms_error(target_output),
        "windowed_rms_abs_error_db_identity": rms_error(identity_output),
        "windowed_rms_abs_error_db_energy_matched": rms_error(matched_output),
        "envelope_correlation_clean_vs_stepped_input": correlation(
            envelope_input, reference.windowed_rms_db(stepped, 320)),
        "envelope_correlation_clean_vs_target_output": correlation(
            envelope_input, reference.windowed_rms_db(target_output, 320)),
        "envelope_correlation_clean_vs_identity": correlation(
            envelope_input, reference.windowed_rms_db(identity_output, 320)),
        "note": ("Synthetic energy-matched and identity controls only. Not STOI, SI-SDR, "
                 "intelligibility, loudness-standard conformance, listening, CPU load or "
                 "deadline evidence."),
    }


def build_report():
    fixture_document = run.fixture()
    inspect_result = run.inspect(request("inspect", None, dict(DEFAULT_TARGET), "inspect"))
    cases = {}
    for stimulus_id in fixture_document["stimuli"]:
        cases[stimulus_id] = case_metrics(
            stimulus_id, dict(DEFAULT_TARGET), "case-" + stimulus_id,
            trace=stimulus_id in ("impulse", "fixed_tone"))

    blockers = [
        {
            "id": "real_speech_qualification",
            "status": "blocked",
            "reason": ("No rights-cleared matched real-speech cohort, natural microphone "
                       "capture or independently scored quality/intelligibility run exists."),
            "reopening_condition": ("Freeze a paired real-speech cohort with natural gain "
                                    "variation and pauses; split by speaker/session and score "
                                    "against an agreed task-matched baseline."),
        },
        {
            "id": "listening_and_loudness_standard",
            "status": "blocked",
            "reason": ("No listening panel, STOI/SI-SDR protocol, loudness-standard meter or "
                       "true-peak qualified measurement is available in this fixture."),
            "reopening_condition": ("Run an authorized listening or validated objective protocol "
                                    "with agreed margins; separately pin and qualify any "
                                    "loudness/true-peak standard before making such a claim."),
        },
        {
            "id": "native_provider_and_baseline",
            "status": "blocked",
            "reason": ("No matched native SDK provider build, installed archive or frame-by-frame "
                       "parity check was built here."),
            "reopening_condition": ("Build an optional native provider outside this fixture, "
                                    "verify installed-archive behavior and prove parity with "
                                    "this reference on the frozen synthetic cohort."),
        },
        {
            "id": "target_device_and_deadline",
            "status": "blocked",
            "reason": "No target device, paced callback run, CPU/memory budget or deadline budget exists.",
            "reopening_condition": ("Measure paced availability, CPU/memory, content delay and "
                                    "failure/deadline accounting on the intended target runtime."),
        },
        {
            "id": "pause_noise_and_interaction_realtime",
            "status": "blocked",
            "reason": ("Whole-segment silence bypass does not gate near-silence spans inside an "
                       "active segment, and interacting stages were only replayed in memory."),
            "reopening_condition": ("Define and qualify pause/noise-floor behavior on real pauses, "
                                    "then verify static-gain/ceiling chain interactions in the "
                                    "native real-time runtime."),
        },
    ]

    return {
        "protocol": "sdk.static-target-gain-with-peak-ceiling.dsp.v1",
        "evidence_kind": "synthetic_developer_only",
        "status": "proposal_only_synthetic",
        "qualification_status": "incomplete",
        "task": TASK,
        "component": "static-target-gain-with-peak-ceiling",
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
        "default_controls": dict(DEFAULT_TARGET),
        "exact_gain_arithmetic": {
            "input_rms": "sqrt(sum(finite_sample^2) / finite_sample_count)",
            "desired_gain_linear": "target_dbfs_to_linear / max(input_rms, 1e-8)",
            "applied_gain_linear": "clamp(desired_gain_linear, min_gain_db_to_linear, max_gain_db_to_linear)",
            "gain_db": "20 * log10(applied_gain_linear)",
            "output_sample": "f32(clamp(sample * applied_gain_linear, -ceiling, +ceiling))",
            "silence_bypass": "if input_rms_db <= silence_floor_dbfs, emit zeros and do not amplify",
            "nonfinite_policy": "finite-only RMS; C++-style min/max ordering maps nonfinite products to the ceiling",
        },
        "missing_result_policy": ("No missing, rejected, not_run or incomplete result qualifies "
                                  "a candidate; every absent real/listening/native/device "
                                  "qualification remains blocked."),
        "cases": cases,
        "comparisons": {
            "level_sweep": level_sweep(),
            "target_sweep": target_sweep(),
            "ceiling_sweep": ceiling_sweep(),
            "response": response(),
            "delay": delay(),
            "load_and_energy_matched_control": load_control(),
            "state_transitions": state_transitions(),
            "interacting_nonlinear": interacting_nonlinear_controls(),
        },
        "adverse_and_skipped": {
            "control_rejections": control_rejections(),
            "frame_shape": frame_shape_controls(),
            "epoch_and_sessions": epoch_and_sessions(),
            "nonfinite_input": {
                "status": "adverse_numerical_observed",
                "input_nonfinite": cases["nonfinite"]["nonfinite_input_count"],
                "output_nonfinite": cases["nonfinite"]["nonfinite_output_count"],
                "output_sha256": cases["nonfinite"]["output_sha256"],
                "note": ("Finite-only RMS planning plus C++-style min/max ordering maps NaN/Inf "
                         "inputs to the finite ceiling. This is an observation, not a robustness "
                         "endorsement."),
            },
            "silence_and_near_silence": {
                "status": "observed",
                "silence_peak": cases["silence"]["peak_output"],
                "silence_bypass": cases["silence"]["silence_bypass"],
                "below_floor_peak": cases["near_silence_below"]["peak_output"],
                "below_floor_bypass": cases["near_silence_below"]["silence_bypass"],
                "above_floor_peak": cases["near_silence_above"]["peak_output"],
                "above_floor_bypass": cases["near_silence_above"]["silence_bypass"],
                "note": ("Whole-segment floor bypass is explicit. Quiet spans inside an active "
                         "segment are still scaled by the bounded static gain and are not gated."),
            },
            "peak_overshoot": {
                "status": "observed",
                "clipped_samples": cases["overshoot"]["clipped_samples"],
                "peak_output": cases["overshoot"]["peak_output"],
                "ceiling": CEILING,
                "note": ("Overshoot and impulse cases demand a static scale that exceeds the "
                         "ceiling; the hard clamp is the observable guard."),
            },
            "missing_native_or_real_qualification": {"status": "not_run", "blockers": blockers},
        },
        "baseline_comparison": {
            "status": "not_qualified",
            "reason": ("Identity and energy-matched synthetic controls are reported; no "
                       "established baseline parity, frozen cohort, listening acceptance or "
                       "loudness-standard conformance is claimed."),
        },
        "blockers": blockers,
        "counts": {
            "stimuli": len(fixture_document["stimuli"]),
            "cases": len(cases),
            "source_pins": len(fixture_document["source_pins"]),
            "control_rejection_probes": 17,
            "frame_shape_probes": 2,
            "epoch_session_probes": 4,
            "level_sweep_points": len(fixture_document["parameters"]["level_sweep_db"]),
            "target_sweep_points": len(fixture_document["parameters"]["target_sweep_dbfs"]),
            "ceiling_sweep_points": (2 * len(
                fixture_document["parameters"]["ceiling_sweep_dbfs"])),
            "interaction_configurations": 6,
            "blockers": len(blockers),
        },
    }


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


if __name__ == "__main__":
    try:
        import sys
        sys.stdout.buffer.write(canonical_bytes(build_report()))
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error) or error.__class__.__name__) from error
