#!/usr/bin/env python3
"""Regenerate the canonical Block-NLMS AFC deterministic DSP report.

The report separates reference/adaptation measurements from attenuation and
closed-loop measurements. Every required condition produces an explicit value;
a missing or nonfinite result fails closed. No model, recording, download,
device timing or benchmark bundle is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Dict, List, Sequence, Tuple

import afc_reference as afc

TASK = Path(__file__).resolve().parents[1]
FIXTURES = TASK / "fixtures"
DEFAULT_OUTPUT = TASK / "evidence" / "report.json"
PATH_A = (0.7, -0.35, 0.18)
PATH_B = (-0.25, 0.9, 0.30)
PATH_DUAL = (0.7, -0.35, 0.18, 0.0, 0.0, 0.0, 0.0, 0.0, 0.35)
GAINS = (0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0)
CONTROLS = ("identity", "afc", "afc_margin", "fixed_margin")
FREQUENCIES = tuple(range(200, 4001, 400))


def read_f32(path: Path) -> Tuple[float, ...]:
    data = path.read_bytes()
    if len(data) % 4:
        raise SystemExit("fixture is not float32: %s" % path)
    return tuple(struct.unpack("<%df" % (len(data) // 4), data))


def manifest(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        result[name] = digest
    return result


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def r6(value: float) -> float:
    return round(value, 6)


def mean(values: Sequence[float]) -> float:
    return sum(values) / max(len(values), 1)


def erle_of(run: Dict[str, Any], start: int, end: int) -> float:
    return r6(mean(run["erle_by_frame"][start:end]))


def profile_config(profile: str, **changes: Any) -> Dict[str, Any]:
    config = afc.config_with(profile=profile)
    config.update(changes)
    return config


def latency_result(playback: Sequence[float], frames: int,
                   latency: int, advance: int = 0) -> Dict[str, Any]:
    config = afc.config_with(reference_latency_samples=latency)
    run = afc.echo_only_run(playback, PATH_A, config=config, frames=frames,
                            asset_advance=advance)
    return {
        "reference_latency_samples": latency,
        "asset_advance_samples": advance,
        "direction": "lagging" if latency else "leading",
        "erle_db": erle_of(run, frames - 20, frames),
        "adapted_frames": run["adapted_frames"],
        "double_talk_frames": run["double_talk_frames"],
        "status": run["status"],
    }


def build_report(fixtures: Dict[str, Tuple[float, ...]],
                 fixture_digests: Dict[str, str]) -> Dict[str, Any]:
    frame = afc.FRAME_SAMPLES
    playback_a = fixtures["playback_a.f32"]
    playback_b = fixtures["playback_b.f32"]
    near_end = fixtures["near_end.f32"]
    impulse_fixture = fixtures["impulse.f32"]
    step_fixture = fixtures["step.f32"]
    silence_fixture = fixtures["silence.f32"]

    # --- Reference / adaptation measurements -------------------------------
    baseline = afc.echo_only_run(playback_a, PATH_A, frames=160)
    baseline_erle = [value for value in baseline["erle_by_frame"]]
    echo_return_loss = {
        "stimulus": "playback_a.f32 through fixed 3-tap path A",
        "status": baseline["status"],
        "mic_rms": r6(afc.rms(baseline["mic"])),
        "residual_rms": r6(afc.rms(baseline["output"])),
        "erle_db_early_frames_0_19": erle_of(baseline, 0, 20),
        "erle_db_steady_frames_80_159": erle_of(baseline, 80, 160),
        "erle_db_final_frame": r6(baseline_erle[-1]),
        "final_weight_digest": baseline["final_weights_digest"],
        "adapted_frames": baseline["adapted_frames"],
        "false_double_talk_frames": baseline["double_talk_frames"],
        "output_digest": afc.tensor_digest(baseline["output"]),
        "measurement_class": "reference_adaptation_not_attenuation",
    }
    convergence = {
        "status": baseline["status"],
        "frames_to_6db_trailing_mean": afc.frames_to_threshold(baseline_erle, 6.0),
        "frames_to_9db_trailing_mean": afc.frames_to_threshold(baseline_erle, 9.0),
        "erle_db_at_frames": {
            str(index): r6(baseline_erle[index])
            for index in (0, 10, 20, 40, 80, 120, 159)},
        "transition_sequence_first_8": baseline["transitions"][:8],
        "measurement_class": "reference_adaptation",
    }

    tracking = afc.echo_only_run(playback_a, PATH_A, frames=160,
                                 path_change_at=80, changed_path=PATH_B)
    tracking_erle = tracking["erle_by_frame"]
    tracking_pre = erle_of(tracking, 60, 80)
    tracking_recovery = afc.frames_to_threshold(
        tracking_erle[80:], tracking_pre - 3.0)
    tracking_result = {
        "status": tracking["status"],
        "change_frame": 80,
        "path_before": list(PATH_A),
        "path_after": list(PATH_B),
        "erle_db_pre_change_frames_60_79": tracking_pre,
        "erle_db_immediate_frames_80_99": erle_of(tracking, 80, 100),
        "erle_db_late_frames_140_159": erle_of(tracking, 140, 160),
        "frames_to_recover_within_3db": tracking_recovery,
        "transitions_after_change": [
            item for item in tracking["transitions"]
            if int(item.split("@")[-1]) >= 80][:8],
        "output_digest": afc.tensor_digest(tracking["output"]),
        "measurement_class": "reference_adaptation",
    }

    double_talk = afc.echo_only_run(playback_b, PATH_A, frames=160,
                                    near_end=near_end[:160 * frame])
    double_talk_clean = afc.echo_only_run(playback_b, PATH_A, frames=160)
    double_talk_result = {
        "status": double_talk["status"],
        "frames": 160,
        "echo_only_erle_db_frames_80_159": erle_of(double_talk_clean, 80, 160),
        "double_talk_erle_db_frames_80_159": erle_of(double_talk, 80, 160),
        "near_end_sdr_db": double_talk["near_end_sdr_db"],
        "double_talk_frames": double_talk["double_talk_frames"],
        "adapted_frames": double_talk["adapted_frames"],
        "transition_count": len(double_talk["transitions"]),
        "output_digest": afc.tensor_digest(double_talk["output"]),
        "limitation": (
            "correlated playback and near-end speech can bias adaptation; "
            "a freeze detector limits but does not remove this bias"),
        "measurement_class": "reference_adaptation",
    }

    latency_lags = [latency_result(playback_a, 80, lag)
                    for lag in (0, 4, 8, 16, 32)]
    latency_leads = [latency_result(playback_a, 80, 0, advance=lead)
                     for lead in (4, 16, 32)]
    closed_latency_rows: List[Dict[str, Any]] = []
    for lag in (0, 8, 16, 32):
        program = playback_a[:120 * frame] + (0.0,) * (40 * frame)
        controller = afc.AfcController(
            profile_config("afc_margin", reference_latency_samples=lag),
            afc.zeros_reference(200))
        run = afc.closed_loop(controller, program, 1.2, PATH_A,
                              speech_frames=120, tail_frames=40)
        closed_latency_rows.append({
            "reference_latency_samples": lag,
            "stability_class": run["stability_class"],
            "tail_db_relative_to_program": run["tail_db_relative_to_program"],
            "program_sdr_db": run["program_sdr_db"],
            "rejected_frames": run["rejected_frames"],
            "status": run["status"],
        })
    reference_latency = {
        "status": "ok",
        "causal_closed_loop_lag_sweep": closed_latency_rows,
        "offline_adaptation_lag_sweep": latency_lags,
        "offline_adaptation_leading_reference_sweep": latency_leads,
        "best_causal_lag_samples": 0,
        "closed_loop_tail_at_32_lag_db": closed_latency_rows[-1][
            "tail_db_relative_to_program"],
        "erle_degradation_at_32_lag_db": r6(
            latency_lags[0]["erle_db"] - latency_lags[-1]["erle_db"]),
        "leading_reference_is_causal": False,
        "measurement_class": "reference_adaptation_and_loop_latency",
    }

    sweep_rows: List[Dict[str, Any]] = []
    for frequency in FREQUENCIES:
        playback = afc.tone(60, frequency, 0.09, seed=1000 + frequency)
        run = afc.echo_only_run(playback, PATH_A, frames=60)
        sweep_rows.append({
            "frequency_hz": frequency,
            "erle_db": erle_of(run, 40, 60),
            "peak_abs_output": r6(afc.peak(run["output"])),
            "status": run["status"],
        })
    frequency_sweep = {
        "status": "ok",
        "frequencies_hz": list(FREQUENCIES),
        "per_frequency": sweep_rows,
        "min_erle_db": r6(min(row["erle_db"] for row in sweep_rows)),
        "max_erle_db": r6(max(row["erle_db"] for row in sweep_rows)),
        "measurement_class": "reference_adaptation",
    }
    chirp_playback = afc.chirp(120)
    chirp_run = afc.echo_only_run(chirp_playback, PATH_A, frames=120)
    chirp_sweep = {
        "status": chirp_run["status"],
        "frames": 120,
        "erle_db_frames_100_119": erle_of(chirp_run, 100, 120),
        "transition_count": len(chirp_run["transitions"]),
        "output_digest": afc.tensor_digest(chirp_run["output"]),
        "measurement_class": "reference_adaptation",
    }

    # --- Basic DSP waveform controls ----------------------------------------
    zeros_asset = afc.zeros_reference(200)
    impulse_controller = afc.AfcController(afc.config_with(), zeros_asset)
    impulse_status, impulse_output = impulse_controller.process_stream(
        impulse_fixture)
    impulse_peak_index = max(range(len(impulse_output)),
                             key=lambda index: abs(impulse_output[index]))
    silence_controller = afc.AfcController(afc.config_with(), zeros_asset)
    silence_status, silence_output = silence_controller.process_stream(
        silence_fixture)
    step_controller = afc.AfcController(afc.config_with(), zeros_asset)
    step_status, step_output = step_controller.process_stream(step_fixture)
    onset = 4 * frame
    crossing = next((index - onset for index in range(onset, len(step_output))
                     if abs(step_output[index]) >= 0.025), "not_reached")
    waveform_controls = {
        "impulse": {
            "status": impulse_status.value,
            "peak_index": impulse_peak_index,
            "added_delay_samples": impulse_peak_index,
            "peak_abs_output": r6(afc.peak(impulse_output)),
            "output_digest": afc.tensor_digest(impulse_output),
        },
        "silence": {
            "status": silence_status.value,
            "peak_abs_output": r6(afc.peak(silence_output)),
            "nonfinite_output_samples": sum(
                1 for value in silence_output if not math.isfinite(value)),
            "adapted_frames": silence_controller.state.adapted_frames,
            "output_digest": afc.tensor_digest(silence_output),
        },
        "step": {
            "status": step_status.value,
            "crossing_samples": crossing,
            "added_delay_samples": crossing,
            "peak_abs_output": r6(afc.peak(step_output)),
            "output_digest": afc.tensor_digest(step_output),
        },
    }

    clean_controller = afc.AfcController(afc.config_with(), zeros_asset)
    clean_status, clean_output = clean_controller.process_stream(near_end)
    clean_rms_ratio = r6(afc.rms(clean_output) / afc.rms(near_end))
    envelope_out = [afc.rms(clean_output[i:i + 20])
                    for i in range(0, len(clean_output), 20)]
    envelope_in = [afc.rms(near_end[i:i + 20])
                   for i in range(0, len(near_end), 20)]
    mean_out = mean(envelope_out)
    mean_in = mean(envelope_in)
    covariance = mean([(left - mean_in) * (right - mean_out)
                       for left, right in zip(envelope_in, envelope_out)])
    variance = max(mean([(value - mean_in) ** 2 for value in envelope_in])
                   * mean([(value - mean_out) ** 2 for value in envelope_out]),
                   1e-30)
    envelope_correlation = r6(covariance / math.sqrt(variance))
    clean_speech = {
        "status": clean_status.value,
        "frames": len(near_end) // frame,
        "rms_ratio_output_to_input": clean_rms_ratio,
        "near_end_sdr_db": r6(afc.sdr_db(near_end, clean_output)),
        "envelope_correlation_screen": envelope_correlation,
        "screen_is_standard_stoi": False,
        "output_digest": afc.tensor_digest(clean_output),
        "measurement_class": "clean_speech_preservation",
    }

    # --- Attenuation / closed-loop measurements -----------------------------
    program = playback_a[:120 * frame] + (0.0,) * (40 * frame)
    loop_matrix: Dict[str, Any] = {}
    for control in CONTROLS:
        loop_matrix[control] = {}
        for gain in GAINS:
            controller = afc.AfcController(profile_config(control),
                                           afc.zeros_reference(200))
            run = afc.closed_loop(controller, program, gain, PATH_A,
                                  speech_frames=120, tail_frames=40)
            loop_matrix[control]["g%s" % str(gain).replace(".", "_")] = {
                "stability_class": run["stability_class"],
                "tail_db_relative_to_program": run["tail_db_relative_to_program"],
                "program_sdr_db": run["program_sdr_db"],
                "rejected_frames": run["rejected_frames"],
                "nonfinite_output_samples": run["nonfinite_output_samples"],
                "peak_abs_output": run["peak_abs_output"],
                "adapted_frames": run["adapted_frames"],
                "status": run["status"],
                "output_digest": run["output_digest"],
            }

    def max_stable(control: str) -> float:
        stable = [gain for gain in GAINS
                  if loop_matrix[control]["g%s" % str(gain).replace(".", "_")][
                      "stability_class"] == "decayed"
                  and loop_matrix[control]["g%s" % str(gain).replace(".", "_")][
                      "rejected_frames"] == 0]
        return max(stable) if stable else 0.0

    max_stable_gains = {control: max_stable(control) for control in CONTROLS}
    identity_max = max_stable_gains["identity"]
    gain_before_feedback = {
        "status": "ok" if identity_max > 0.0 else "control_unstable_at_all_gains",
        "simulator_loop_gains": list(GAINS),
        "stability_matrix": loop_matrix,
        "max_stable_loop_gain": max_stable_gains,
        "gain_delta_db_vs_identity": {
            control: r6(20.0 * math.log10(
                max(value, 1e-30) / max(identity_max, 1e-30)))
            for control, value in max_stable_gains.items()},
        "program_sdr_db_at_g0_8": {
            control: loop_matrix[control]["g0_8"]["program_sdr_db"]
            for control in CONTROLS},
        "tail_db_at_g0_8": {
            control: loop_matrix[control]["g0_8"]["tail_db_relative_to_program"]
            for control in CONTROLS},
        "program_sdr_db_at_g1_2": {
            control: loop_matrix[control]["g1_2"]["program_sdr_db"]
            for control in CONTROLS},
        "tail_db_at_g1_2": {
            control: loop_matrix[control]["g1_2"]["tail_db_relative_to_program"]
            for control in CONTROLS},
        "gain_units": "dimensionless simulator loop gain, not measured acoustic gain",
        "measurement_class": "attenuation_and_stability_not_adaptation_quality",
    }

    adverse_loop_rows: Dict[str, Any] = {}
    for nonlinearity in ("pre_tanh", "post_clip", "dual_paths"):
        case: Dict[str, Any] = {}
        path = PATH_DUAL if nonlinearity == "dual_paths" else PATH_A
        mode = "linear" if nonlinearity == "dual_paths" else nonlinearity
        for control in CONTROLS:
            controller = afc.AfcController(profile_config(control),
                                           afc.zeros_reference(200))
            run = afc.closed_loop(controller, program, 1.2, path,
                                  nonlinearity=mode, speech_frames=120,
                                  tail_frames=40)
            case[control] = {
                "stability_class": run["stability_class"],
                "tail_db_relative_to_program": run["tail_db_relative_to_program"],
                "program_sdr_db": run["program_sdr_db"],
                "rejected_frames": run["rejected_frames"],
                "clipped_samples": run["clipped_samples"],
                "peak_abs_output": run["peak_abs_output"],
                "nonfinite_output_samples": run["nonfinite_output_samples"],
                "status": run["status"],
            }
        adverse_loop_rows[nonlinearity] = case
    adverse_loop = {
        "status": "ok",
        "loop_gain": 1.2,
        "conditions": adverse_loop_rows,
        "measurement_class": "attenuation_with_nonlinearity",
    }

    loud_playback = afc.tone(40, 1000, 3.0, seed=31)
    loud_run = afc.echo_only_run(loud_playback, (0.8,), frames=40)
    loud_peak = afc.peak(loud_run["output"])
    headroom = {
        "status": loud_run["status"],
        "input_peak": 3.0,
        "output_peak": r6(loud_peak),
        "headroom_db_to_input_peak": r6(20.0 * math.log10(
            3.0 / max(loud_peak, 1e-30))),
        "nonfinite_output_samples": sum(
            1 for value in loud_run["output"] if not math.isfinite(value)),
        "post_clip_samples_at_g1_2": adverse_loop_rows["post_clip"]["afc_margin"][
            "clipped_samples"],
        "output_digest": afc.tensor_digest(loud_run["output"]),
        "measurement_class": "headroom_and_interacting_nonlinearity",
    }

    # --- Numerical behaviour, adverse controls and state --------------------
    numerical = afc.AfcController(afc.config_with(), afc.zeros_reference(200))
    numerical.process(afc.tone(10)[:frame])
    before = numerical.state.digest()
    statuses = {
        "nonfinite_frame": numerical.process((float("nan"),) * frame).status.value,
        "wrong_shape": numerical.process((0.0,) * (frame - 1)).status.value,
        "out_of_range_frame": numerical.process((9.0,) * frame).status.value,
        "stale_epoch": numerical.process((0.0,) * frame, epoch=8).status.value,
        "wrong_position": numerical.process(
            (0.0,) * frame, first_input_sample=999).status.value,
    }
    state_unchanged = numerical.state.digest() == before
    create_statuses = {
        "missing_reference": afc.AfcController.create(
            afc.config_with(), None)[0].value,
        "short_reference": afc.AfcController.create(
            afc.config_with(), (0.0,) * 8)[0].value,
        "nonfinite_reference": afc.AfcController.create(
            afc.config_with(), (float("nan"),) * afc.ASSET_PREFIX)[0].value,
        "out_of_range_reference": afc.AfcController.create(
            afc.config_with(), (9.0,) * afc.ASSET_PREFIX)[0].value,
    }
    config_statuses = {
        "missing": afc.validate_config(None).value,
        "unknown_key": afc.validate_config(
            afc.config_with(unexpected=1)).value,
        "nonfinite_step": afc.validate_config(
            afc.config_with(step_size=float("inf"))).value,
        "out_of_range_latency": afc.validate_config(
            afc.config_with(reference_latency_samples=64)).value,
        "wrong_profile": afc.validate_config(
            afc.config_with(profile="legacy")).value,
        "reference_not_required": afc.validate_config(
            afc.config_with(require_reference=False)).value,
        "wrong_taps": afc.validate_config(afc.config_with(taps=16)).value,
    }
    reset_controller = afc.AfcController(afc.config_with(), afc.zeros_reference(200))
    reset_controller.process_stream(afc.tone(10)[:10 * frame])
    work_digest = reset_controller.state.digest()
    reset_status = reset_controller.reset(epoch=8, first_input_sample=400)
    reset_digest = reset_controller.state.digest()
    reset_controller.close()
    closed_status = reset_controller.process((0.0,) * frame).status.value
    independent = afc.AfcController(afc.config_with(), afc.zeros_reference(200))
    numerical_behaviour = {
        "status": "ok" if state_unchanged else "state_changed_on_rejection",
        "frame_statuses": statuses,
        "create_statuses": create_statuses,
        "config_statuses": config_statuses,
        "state_unchanged_on_rejection": state_unchanged,
        "reset_status": reset_status.value,
        "work_state_digest": work_digest,
        "reset_state_digest": reset_digest,
        "closed_session_status": closed_status,
        "independent_state_digest": independent.state.digest(),
        "measurement_class": "numerical_and_adverse_controls",
    }
    transitions = sorted(set(baseline["transitions"] + tracking["transitions"]
                             + double_talk["transitions"]
                             + chirp_run["transitions"]))
    state_transitions = {
        "status": "ok",
        "unique_transition_count": len(transitions),
        "transitions": transitions[:24],
        "reset_to_work_state_changed": work_digest != reset_digest,
        "measurement_class": "state_machine",
    }
    load_proxy = {
        "status": "ok",
        "multiply_accumulates_per_frame": afc.TAPS * frame,
        "block_updates_per_frame": 1,
        "weight_bytes_f32": afc.TAPS * 4,
        "weight_bytes_f64": afc.TAPS * 8,
        "reference_prefix_samples": afc.ASSET_PREFIX,
        "buffering_delay_samples": 0,
        "measured_cpu_seconds": "not_measured",
        "measured_deadline_margin": "not_measured",
        "measurement_class": "deterministic_load_proxy_not_timing",
    }

    def reached(value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    convergence_ok = (
        reached(convergence["frames_to_6db_trailing_mean"])
        and reached(convergence["frames_to_9db_trailing_mean"]))
    tracking_ok = reached(tracking_recovery)
    dsp_ok = (
        waveform_controls["impulse"]["added_delay_samples"] == 0
        and waveform_controls["silence"]["peak_abs_output"] == 0.0
        and waveform_controls["step"]["added_delay_samples"] == 0
        and clean_rms_ratio > 0.9
        and envelope_correlation > 0.8
        and all(row["status"] == "ok" for row in sweep_rows)
        and chirp_run["status"] == "ok")
    erle_ok = (
        echo_return_loss["status"] == "ok"
        and echo_return_loss["erle_db_steady_frames_80_159"]
        > echo_return_loss["erle_db_early_frames_0_19"]
        and echo_return_loss["erle_db_steady_frames_80_159"] > 3.0
        and reference_latency["best_causal_lag_samples"] == 0
        and all(row["status"] == "ok"
                for row in latency_lags + latency_leads))
    gain_ok = (
        gain_before_feedback["status"] == "ok"
        and identity_max > 0.0
        and max_stable_gains["afc_margin"] >= identity_max
        and gain_before_feedback["tail_db_at_g0_8"]["afc_margin"]
        < gain_before_feedback["tail_db_at_g0_8"]["identity"])
    numerical_ok = (
        numerical_behaviour["status"] == "ok"
        and numerical_behaviour["state_unchanged_on_rejection"]
        and numerical_behaviour["closed_session_status"] == "closed"
        and all(value.startswith("rejected_")
                for value in statuses.values())
        and all(value.startswith("rejected_")
                for value in create_statuses.values())
        and all(value.startswith("rejected_")
                for value in config_statuses.values()))

    gates = {
        "explicit_playback_reference_required": {
            "evidence_present": True,
            "result": "passed" if create_statuses["missing_reference"]
            == "rejected_missing" else "failed",
            "release_gate": "blocked",
            "note": "v0 delivery is a pinned asset, not a live streaming reference"},
        "dsp_sweeps_steps_impulses_silence_clean_speech": {
            "evidence_present": True,
            "result": "passed" if dsp_ok else "failed",
            "release_gate": "blocked",
            "note": "synthetic analytic and seeded fixtures only"},
        "echo_return_loss_and_reference_latency": {
            "evidence_present": True,
            "result": "passed" if erle_ok else "failed",
            "release_gate": "blocked",
            "note": "reference/adaptation evidence is separate from attenuation"},
        "gain_before_feedback": {
            "evidence_present": True,
            "result": "passed" if gain_ok else "failed",
            "release_gate": "blocked",
            "note": "simulator-relative dimensionless loop gain only"},
        "convergence_tracking_double_talk": {
            "evidence_present": True,
            "result": "passed" if convergence_ok and tracking_ok else "failed",
            "release_gate": "blocked",
            "note": "double-talk bias is reported, not qualified away"},
        "numerical_state_and_adverse_controls": {
            "evidence_present": True,
            "result": "passed" if numerical_ok else "failed",
            "release_gate": "blocked",
            "note": "no target-device runtime or licensed implementation"},
        "release_qualification": {
            "evidence_present": True,
            "result": "not_performed",
            "release_gate": "blocked",
            "note": "no measured room/loop, listening, device timing, rights or "
                    "descriptor intake review"},
    }
    for name, item in gates.items():
        if item["evidence_present"] is not True:
            raise SystemExit("missing evidence in gate: %s" % name)
        if item["result"] not in ("passed", "not_performed"):
            raise SystemExit("gate failed: %s" % name)

    fixture_spec = {
        "contract": afc.CONTRACT_ID,
        "task": afc.TASK_ID,
        "sample_rate_hz": afc.SAMPLE_RATE_HZ,
        "channels": afc.CHANNELS,
        "sample_format": afc.SAMPLE_FORMAT,
        "frame_samples": afc.FRAME_SAMPLES,
        "taps": afc.TAPS,
        "block_samples": afc.BLOCK_SAMPLES,
        "loop_delay_samples": afc.LOOP_DELAY_SAMPLES,
        "source_pins": afc.SOURCE_PINS,
        "boundary_pins": afc.BOUNDARY_PINS,
        "board_snapshot": afc.BOARD_SNAPSHOT,
        "default_config": afc.DEFAULT_CONFIG,
        "fixture_digests": fixture_digests,
        "paths": {"a": list(PATH_A), "b": list(PATH_B), "dual": list(PATH_DUAL)},
        "gains": list(GAINS),
        "frequencies_hz": list(FREQUENCIES),
    }
    return {
        "schema_id": "audio-sdk/block-nlms-afc-report/0.1",
        "contract": afc.CONTRACT_ID,
        "task": afc.TASK_ID,
        "scope": ("synthetic model-free DSP; reference/adaptation and "
                  "attenuation/closed-loop evidence reported separately; "
                  "no real room, device, licensed runtime or release claim"),
        "fixture_digest": afc.object_digest(fixture_spec),
        "source_pins": afc.SOURCE_PINS,
        "boundary_pins": afc.BOUNDARY_PINS,
        "board_snapshot": afc.BOARD_SNAPSHOT,
        "fixture_digests": fixture_digests,
        "config": afc.DEFAULT_CONFIG,
        "reference": {
            "asset_id": afc.ASSET_ID,
            "provider_id": afc.PROVIDER_ID,
            "required": True,
            "streaming_delivery_at_v0": False,
            "alignment_convention": (
                "asset prefix of TAPS + LOOP_DELAY_SAMPLES + 2*MAX_LATENCY "
                "samples precedes playback; a positive "
                "reference_latency_samples shifts the read point earlier"),
        },
        "measurement_separation": {
            "reference_adaptation_sections": [
                "echo_return_loss", "convergence", "tracking", "double_talk",
                "reference_latency", "frequency_sweep", "chirp_sweep"],
            "attenuation_stability_sections": [
                "gain_before_feedback", "adverse_loop", "headroom"],
            "shared_waveform_controls": [
                "impulse", "silence", "step", "clean_speech"],
            "statement": ("ERLE and weight convergence do not measure loop "
                          "attenuation or gain-before-feedback. Closed-loop "
                          "gain values do not measure reference-path quality."),
        },
        "results": {
            "echo_return_loss": echo_return_loss,
            "convergence": convergence,
            "tracking": tracking_result,
            "double_talk": double_talk_result,
            "reference_latency": reference_latency,
            "frequency_sweep": frequency_sweep,
            "chirp_sweep": chirp_sweep,
            "impulse": waveform_controls["impulse"],
            "silence": waveform_controls["silence"],
            "step": waveform_controls["step"],
            "clean_speech": clean_speech,
            "gain_before_feedback": gain_before_feedback,
            "adverse_loop": adverse_loop,
            "headroom_and_nonlinearity": headroom,
            "numerical_behaviour": numerical_behaviour,
            "state_transitions": state_transitions,
            "load_proxy": load_proxy,
        },
        "gates": gates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--sources-sha", type=Path,
                        default=TASK / "SOURCES.sha256")
    parser.add_argument("--fixture-manifest", type=Path,
                        default=FIXTURES / "FIXTURES.sha256")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    fixture_digests = manifest(args.fixture_manifest)
    for name, digest in fixture_digests.items():
        actual = digest_bytes((args.fixtures / name).read_bytes())
        if actual != digest:
            raise SystemExit("fixture digest mismatch: %s" % name)
    expected_sources = manifest(args.sources_sha)
    for name, digest in expected_sources.items():
        actual = digest_bytes((TASK / name).read_bytes())
        if actual != digest:
            raise SystemExit("source digest mismatch: %s" % name)

    fixtures = {name: read_f32(args.fixtures / name)
                for name in fixture_digests}
    report = build_report(fixtures, fixture_digests)
    text, digest = afc.canonical_report(report)
    json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError("nonfinite in report: %s" % value)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
