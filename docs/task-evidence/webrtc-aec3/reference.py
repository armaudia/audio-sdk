# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic AEC3-shaped acoustic echo cancellation reference.

This is an original, model-free, frame-causal teaching reference.  It is not
WebRTC AEC3: no upstream source, binary, weight, runtime or recorded corpus is
present.  The architecture is intentionally AEC3-like (shadow filter for
double-talk detection, primary adaptive filter, residual echo suppression with
a hysteresis hangover), but every constant and operation is defined here.

Only render samples already presented on the explicit sidechain are used.  The
double-talk/residual decision for frame k is derived from frame k-1 and earlier
state, so the processor has zero algorithmic delay and never reads a future
frame.  The reported render-to-capture alignment is a fixture property, not a
device or buffering measurement.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Sequence

import fixture
import scorer

TASK = "SDK-WEBRTC-AEC3"
COMPONENT = "webrtc-aec3"
BASE_COMMIT = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-WEBRTC-AEC3"
STATUS = "proposal_only_not_qualified"
QUALIFICATION_STATUS = "incomplete"
DECISION = "DEFER"
PROCESSOR_EXPOSURE = False
LOCAL_IDENTITY = "webrtc-aec3-synthetic-reference-v1"
ADAPTER_ID = "webrtc-aec3-task-local"

SAMPLE_RATE_HZ = fixture.SAMPLE_RATE_HZ
FRAME_SAMPLES = fixture.FRAME_SAMPLES
FRAME_SAMPLES_EXPECTED = FRAME_SAMPLES
FILTER_TAPS = 96
STEP_MAIN = 0.18
STEP_SHADOW = 0.25
EPS = 1e-8
DT_ENTER = 0.35
DT_EXIT = 0.70
DT_HANGOVER = 2
GAIN_LOW = 0.30
GAIN_HIGH = 0.80
GAIN_MIN = 0.22
MAX_ABS_INPUT = 4.0
ALGORITHMIC_DELAY_SAMPLES = 0
BUFFERING_DELAY_SAMPLES = 0

SPDX_ID = "SPDX" "-License-Identifier"
REPORT_KEYS = {
    "SPDX-FileCopyrightText", SPDX_ID, "task", "component",
    "base_commit", "branch", "profile", "status", "qualification_status",
    "decision", "processor_exposure", "public_surface_changed",
    "installed_v0_changed", "acceptance_profile", "fixture_spec",
    "fixture_spec_sha256", "algorithm", "causality", "runs", "controls",
    "failures", "crosscheck", "repeat_runs", "sources", "disclosure",
}


def canonical_bytes(value: Any) -> bytes:
    return fixture.canonical_bytes(value)


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report).decode("utf-8")
    return payload, fixture.sha256_bytes(payload.encode("utf-8"))


def f32(value: float) -> float:
    return fixture.f32(value)


class Aec3Lite:
    """Frame-causal synthetic echo canceller with explicit render sidechain."""

    def __init__(self) -> None:
        self.epoch = 1
        self.first_sample = 0
        self.reset_count = 0
        self._clear()

    def _clear(self) -> None:
        self.main = [0.0] * FILTER_TAPS
        self.shadow = [0.0] * FILTER_TAPS
        self.history = [0.0] * FILTER_TAPS  # index 0 is the newest render sample
        self.last_ratio = 1.0
        self.hold_frames = 0
        self.frames = 0
        self.adapted_frames = 0
        self.double_talk_frames = 0
        self.no_reference_frames = 0
        self.failures = 0
        self.safety_resets = 0

    def reset(self, epoch: int, first_sample: int) -> None:
        if (isinstance(epoch, bool) or not isinstance(epoch, int)
                or epoch <= self.epoch):
            raise ValueError("stale_or_invalid_epoch")
        if (isinstance(first_sample, bool) or not isinstance(first_sample, int)
                or first_sample < 0):
            raise ValueError("invalid_first_sample")
        self._clear()
        self.epoch = epoch
        self.first_sample = first_sample
        self.reset_count += 1

    def state_digest(self) -> str:
        return fixture.sha256_bytes(canonical_bytes([
            [round(value, 12) for value in self.main],
            [round(value, 12) for value in self.shadow],
            [round(value, 12) for value in self.history],
            self.epoch, self.first_sample,
        ]))

    def weight_l1(self) -> float:
        return sum(abs(value) for value in self.main)

    def _gain_for_ratio(self, ratio: float) -> float:
        if ratio <= GAIN_LOW:
            return GAIN_MIN
        if ratio >= GAIN_HIGH:
            return 1.0
        return GAIN_MIN + (ratio - GAIN_LOW) * (1.0 - GAIN_MIN) / (GAIN_HIGH - GAIN_LOW)

    def process_frame(self, microphone: Sequence[float],
                      reference_frame: Sequence[float] | None) -> dict[str, Any]:
        if len(microphone) != FRAME_SAMPLES:
            raise ValueError("invalid_frame_length")
        mic = [f32(float(value)) for value in microphone]
        if any(not math.isfinite(value) or abs(value) > MAX_ABS_INPUT for value in mic):
            raise ValueError("invalid_microphone_frame")
        if reference_frame is None:
            output = tuple(mic)
            self.frames += 1
            self.no_reference_frames += 1
            self.last_ratio = 1.0
            self.hold_frames = 0
            return {"samples": output, "status": "passthrough_no_reference",
                    "held": True, "gain": 1.0, "ratio": 1.0}
        if len(reference_frame) != FRAME_SAMPLES:
            raise ValueError("invalid_reference_length")
        rendered = [f32(float(value)) for value in reference_frame]
        if any(not math.isfinite(value) or abs(value) > MAX_ABS_INPUT
               for value in rendered):
            raise ValueError("invalid_reference_frame")

        ratio = self.last_ratio
        held = ratio >= DT_ENTER or self.hold_frames > 0
        gain = self._gain_for_ratio(ratio)
        output: list[float] = []
        shadow_residual_energy = 0.0
        microphone_energy = 0.0
        frame_adapted = False

        for index in range(FRAME_SAMPLES):
            played = rendered[index]
            if not all(math.isfinite(value) for value in self.main):
                self.main = [0.0] * FILTER_TAPS
                self.safety_resets += 1
            estimate_shadow = 0.0
            estimate_main = 0.0
            render_energy = 0.0
            for tap in range(FILTER_TAPS):
                history = self.history[tap]
                estimate_shadow += self.shadow[tap] * history
                estimate_main += self.main[tap] * history
                render_energy += history * history
            residual_shadow = mic[index] - estimate_shadow
            residual_main = mic[index] - estimate_main
            value = f32(gain * residual_main)
            if not math.isfinite(value) or abs(value) > MAX_ABS_INPUT:
                value = 0.0
                self.failures += 1
            output.append(value)
            shadow_residual_energy += residual_shadow * residual_shadow
            microphone_energy += mic[index] * mic[index]
            if render_energy > EPS:
                step_shadow = STEP_SHADOW * residual_shadow / (render_energy + EPS)
                for tap in range(FILTER_TAPS):
                    self.shadow[tap] += step_shadow * self.history[tap]
                if not held:
                    step_main = STEP_MAIN * residual_main / (render_energy + EPS)
                    for tap in range(FILTER_TAPS):
                        self.main[tap] += step_main * self.history[tap]
                    frame_adapted = True
            for tap in range(FILTER_TAPS - 1, 0, -1):
                self.history[tap] = self.history[tap - 1]
            self.history[0] = played

        ratio = shadow_residual_energy / (microphone_energy + EPS)
        if not math.isfinite(ratio):
            ratio = 1.0
            self.failures += 1
        if ratio >= DT_ENTER:
            self.hold_frames = DT_HANGOVER
        elif ratio <= DT_EXIT:
            self.hold_frames = 0
        elif self.hold_frames > 0:
            self.hold_frames -= 1
        self.last_ratio = ratio
        self.frames += 1
        if frame_adapted:
            self.adapted_frames += 1
        if held:
            self.double_talk_frames += 1
        status = "double_talk_hold" if held else "adaptive"
        return {"samples": tuple(output), "status": status, "held": held,
                "gain": gain, "ratio": ratio}


def run_stream(data: dict[str, Any], mode: str = "adaptive",
               chunk_samples: int = FRAME_SAMPLES,
               fixed_gain: float = 0.5,
               withhold_from_frame: int | None = None) -> dict[str, Any]:
    """Process one frozen stream framewise, independent of caller chunk size."""
    if mode not in ("adaptive", "identity", "fixed_attenuation",
                    "no_reference_passthrough"):
        raise ValueError("unknown_mode")
    if chunk_samples < FRAME_SAMPLES or chunk_samples % FRAME_SAMPLES:
        raise ValueError("chunk_not_frame_aligned")
    microphone = data["microphone"]
    total = len(microphone)
    if total % FRAME_SAMPLES:
        raise ValueError("stream_not_frame_aligned")
    engine = Aec3Lite()
    output: list[float] = []
    statuses: list[str] = []
    gains: list[float] = []
    ratios: list[float] = []
    resets: list[dict[str, Any]] = []
    total_frames = total // FRAME_SAMPLES
    dropout = data.get("dropout")
    for frame_index in range(total_frames):
        if data.get("reset_frame") == frame_index:
            engine.reset(engine.epoch + 1, frame_index * FRAME_SAMPLES)
            resets.append({"frame": frame_index,
                           "sample": frame_index * FRAME_SAMPLES,
                           "epoch": engine.epoch})
        start = frame_index * FRAME_SAMPLES
        mic_frame = tuple(microphone[start:start + FRAME_SAMPLES])
        if mode in ("identity", "fixed_attenuation"):
            factor = 1.0 if mode == "identity" else fixed_gain
            result = {"samples": tuple(f32(factor * value) for value in mic_frame),
                      "status": mode, "held": False, "gain": factor, "ratio": 0.0}
        else:
            render = data.get("reference")
            withheld = (render is None or mode == "no_reference_passthrough"
                        or (dropout is not None and dropout[0] <= frame_index < dropout[1])
                        or (withhold_from_frame is not None
                            and frame_index >= withhold_from_frame))
            reference_frame = None if withheld else tuple(
                render[start:start + FRAME_SAMPLES])
            result = engine.process_frame(mic_frame, reference_frame)
        output.extend(result["samples"])
        statuses.append(result["status"])
        gains.append(round(float(result["gain"]), 9))
        ratios.append(round(float(result["ratio"]), 9))
    return {
        "output": tuple(output),
        "statuses": tuple(statuses),
        "gains": tuple(gains),
        "ratios": tuple(ratios),
        "frames": engine.frames,
        "adapted_frames": engine.adapted_frames,
        "double_talk_frames": engine.double_talk_frames,
        "no_reference_frames": engine.no_reference_frames,
        "safety_resets": engine.safety_resets,
        "failures": engine.failures,
        "reset_count": engine.reset_count,
        "resets": tuple(resets),
        "epoch": engine.epoch,
        "weight_l1": engine.weight_l1(),
        "state_digest": engine.state_digest(),
        "chunk_samples": chunk_samples,
        "output_sha256": scorer.digest(output),
    }


def _run_payload(condition: str, mode: str = "adaptive",
                 withhold_from_frame: int | None = None) -> dict[str, Any]:
    data = fixture.build_stream(condition)
    result = run_stream(data, mode=mode, withhold_from_frame=withhold_from_frame)
    metrics = scorer.summarize(data["microphone"], result["output"],
                               data["near"], data["render"], data["reference"])
    if condition == "no_reference" or mode == "no_reference_passthrough":
        status = "blocked_no_reference"
        qualifies = False
    elif condition == "delayed_render":
        status = "misaligned_reference"
        qualifies = False
    elif condition == "reference_dropout":
        status = "partial_reference"
        qualifies = False
    elif result["failures"] or result["safety_resets"]:
        status = "nonfinite_failure"
        qualifies = False
    else:
        status = "ok_synthetic"
        qualifies = False  # synthetic evidence never qualifies a candidate
    return {
        "condition": condition,
        "control": mode,
        "status": status,
        "qualifies": qualifies,
        "metrics": metrics,
        "output_sha256": result["output_sha256"],
        "state_digest": result["state_digest"],
        "frames": result["frames"],
        "adapted_frames": result["adapted_frames"],
        "double_talk_frames": result["double_talk_frames"],
        "no_reference_frames": result["no_reference_frames"],
        "safety_resets": result["safety_resets"],
        "failures": result["failures"],
        "resets": list(result["resets"]),
        "epoch": result["epoch"],
        "weight_l1": round(result["weight_l1"], 9),
    }


def causality_payload() -> dict[str, Any]:
    impulse = fixture.stimulus("impulse")
    impulse_result = run_stream(impulse)
    step = fixture.stimulus("step")
    step_result = run_stream(step)
    silence = fixture.stimulus("silence")
    silence_result = run_stream(silence)
    impulse_first = next((index for index, value in enumerate(impulse_result["output"])
                          if value != 0.0), -1)
    step_first = next((index for index, value in enumerate(step_result["output"])
                       if value != 0.0), -1)
    return {
        "algorithmic_delay_samples": ALGORITHMIC_DELAY_SAMPLES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "dtl_decision_source": "frame k uses frame k-1 shadow/mic energy ratio and state",
        "future_frame_reads": False,
        "impulse_first_nonzero_sample": impulse_first,
        "step_first_nonzero_sample": step_first,
        "silence_peak_abs": scorer.peak_abs(silence_result["output"]),
        "impulse_peak_abs": round(scorer.peak_abs(impulse_result["output"]), 9),
        "chunk_identity": {
            "frame_chunks": run_stream(fixture.build_stream("overlap"),
                                       chunk_samples=FRAME_SAMPLES)["output_sha256"],
            "five_frame_chunks": run_stream(fixture.build_stream("overlap"),
                                            chunk_samples=5 * FRAME_SAMPLES)["output_sha256"],
            "whole_stream": run_stream(fixture.build_stream("overlap"),
                                       chunk_samples=fixture.TOTAL_SAMPLES)["output_sha256"],
        },
    }


def failures_payload() -> dict[str, Any]:
    overlap = fixture.build_stream("overlap")
    delayed = fixture.build_stream("delayed_render")
    dropout = fixture.build_stream("reference_dropout")
    reset = fixture.build_stream("reset")
    overlap_result = run_stream(overlap)
    delayed_metrics = scorer.summarize(
        delayed["microphone"], run_stream(delayed)["output"],
        delayed["near"], delayed["render"], delayed["reference"])
    dropout_result = run_stream(dropout)
    reset_result = run_stream(reset)
    engine = Aec3Lite()
    clean_frame = tuple(overlap["microphone"][:FRAME_SAMPLES])
    clean_ref = tuple(overlap["reference"][:FRAME_SAMPLES])
    rejected: list[str] = []
    for label, mic_frame, ref_frame in (
        ("nonfinite_microphone", tuple([float("nan")] + list(clean_frame[1:])), clean_ref),
        ("out_of_range_microphone", tuple([9.0] + list(clean_frame[1:])), clean_ref),
        ("short_microphone", clean_frame[:8], clean_ref),
        ("nonfinite_reference", clean_frame, tuple([float("inf")] + list(clean_ref[1:]))),
        ("short_reference", clean_frame, clean_ref[:8]),
    ):
        try:
            engine.process_frame(mic_frame, ref_frame)
        except ValueError as error:
            rejected.append(str(error))
    before = engine.weight_l1()
    clean_frame_result = engine.process_frame(clean_frame, clean_ref)
    after = engine.weight_l1()
    engine.main[0] = float("nan")
    engine.process_frame(clean_frame, clean_ref)

    # Replay: a reset engine and a fresh epoch-2 engine must produce the same
    # post-reset samples and the same internal state for the same frozen frames.
    replay_start = fixture.RESET_FRAME * FRAME_SAMPLES
    replay_frames = 20
    continued = Aec3Lite()
    for frame_index in range(fixture.RESET_FRAME):
        start = frame_index * FRAME_SAMPLES
        continued.process_frame(
            tuple(overlap["microphone"][start:start + FRAME_SAMPLES]),
            tuple(overlap["reference"][start:start + FRAME_SAMPLES]))
    continued.reset(fixture.RESET_EPOCH, replay_start)
    fresh = Aec3Lite()
    fresh.reset(fixture.RESET_EPOCH, replay_start)
    continued_output: list[float] = []
    fresh_output: list[float] = []
    for start in range(replay_start, replay_start + replay_frames * FRAME_SAMPLES,
                       FRAME_SAMPLES):
        mic_frame = tuple(reset["microphone"][start:start + FRAME_SAMPLES])
        ref_frame = tuple(reset["reference"][start:start + FRAME_SAMPLES])
        continued_output.extend(continued.process_frame(mic_frame, ref_frame)["samples"])
        fresh_output.extend(fresh.process_frame(mic_frame, ref_frame)["samples"])
    invalid_reset_rejections: list[str] = []
    for bad_epoch, bad_first in ((fixture.RESET_EPOCH, replay_start),
                                 (fixture.RESET_EPOCH + 1, -1)):
        try:
            fresh.reset(bad_epoch, bad_first)
        except ValueError as error:
            invalid_reset_rejections.append(str(error))
    return {
        "rejected_frame_digests": rejected,
        "rejected_count": len(rejected),
        "invalid_frame_left_state_unchanged": abs(before - 0.0) < 1e-12,
        "clean_frame_after_rejections_finite": all(
            math.isfinite(value) for value in clean_frame_result["samples"]),
        "weight_l1_before_clean_frame": round(before, 12),
        "weight_l1_after_clean_frame": round(after, 12),
        "forced_nonfinite_weight_safety_resets": engine.safety_resets,
        "forced_nonfinite_weight_output_finite": all(
            math.isfinite(value) for value in engine.process_frame(
                clean_frame, clean_ref)["samples"]),
        "alignment_direct_path_tap_samples": min(
            delay for delay, _ in fixture.PATH_A),
        "alignment_early_measured_samples": scorer.alignment_lag(
            overlap["render"], overlap["microphone"]),
        "alignment_measurement": (
            "normalized cross-correlation composite echo peak over the frozen "
            "echo-only window; may exceed the earliest synthetic path tap and "
            "is not a device or buffering measurement"
        ),
        "alignment_delayed_render_samples": delayed_metrics["alignment_lag_samples"],
        "dropout_frames_withheld": dropout_result["no_reference_frames"],
        "dropout_expected_frames": (fixture.DROPOUT_END_FRAME
                                    - fixture.DROPOUT_START_FRAME),
        "reset_events": list(reset_result["resets"]),
        "reset_state_digest": reset_result["state_digest"],
        "reset_safety_resets": reset_result["safety_resets"],
        "reset_failures": reset_result["failures"],
        "reset_replay": {
            "frames": replay_frames,
            "start_sample": replay_start,
            "continued_output_sha256": scorer.digest(continued_output),
            "fresh_output_sha256": scorer.digest(fresh_output),
            "byte_identical": tuple(continued_output) == tuple(fresh_output),
            "continued_state_digest": continued.state_digest(),
            "fresh_state_digest": fresh.state_digest(),
            "state_digest_identical": (continued.state_digest()
                                       == fresh.state_digest()),
            "invalid_reset_rejections": invalid_reset_rejections,
        },
    }


def crosscheck_payload() -> dict[str, Any]:
    data = fixture.build_stream("overlap")
    engine = Aec3Lite()
    digests: list[str] = []
    weight_l1: list[float] = []
    for frame_index in range(4):
        start = frame_index * FRAME_SAMPLES
        result = engine.process_frame(
            tuple(data["microphone"][start:start + FRAME_SAMPLES]),
            tuple(data["reference"][start:start + FRAME_SAMPLES]))
        digests.append(scorer.digest(result["samples"]))
        weight_l1.append(round(engine.weight_l1(), 9))
    return {
        "frames": 4,
        "samples": 4 * FRAME_SAMPLES,
        "filter_taps": FILTER_TAPS,
        "step_main": STEP_MAIN,
        "step_shadow": STEP_SHADOW,
        "dt_enter": DT_ENTER,
        "dt_exit": DT_EXIT,
        "dt_hangover": DT_HANGOVER,
        "gain_min": GAIN_MIN,
        "output_sha256_per_frame": digests,
        "weight_l1_per_frame": weight_l1,
        "combined_sha256": fixture.sha256_bytes(canonical_bytes({
            "digests": digests, "weight_l1": weight_l1})),
    }


def build_report() -> dict[str, Any]:
    spec = fixture.stream_spec()
    runs = {condition: _run_payload(condition) for condition in fixture.CONDITIONS}
    controls = {}
    for control in fixture.CONTROLS:
        if control == "no_reference_passthrough":
            controls[control] = _run_payload("overlap", mode="no_reference_passthrough")
        else:
            controls[control] = _run_payload("overlap", mode=control)
    profile = {
        "profile": "room",
        "frozen_render_or_rir": True,
        "channels_rate_hop_frozen": True,
        "excitation_noise_delay_movement_reset_frozen": True,
        "echo_only": True,
        "near_end_only": True,
        "overlap": True,
        "no_reference": True,
        "alignment": True,
        "echo_attenuation": True,
        "near_end_damage": True,
        "nonfinite_failures": True,
        "reset": True,
        "delayed_render": True,
        "missing_render": True,
        "independent_no_reference_comparison": True,
        "chunked_single_digest_identity": True,
        "no_missing_result_promoted": True,
        "synthetic_only": True,
    }
    core: dict[str, Any] = {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        SPDX_ID: "Apache-2.0",
        "task": TASK,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": "room",
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "processor_exposure": PROCESSOR_EXPOSURE,
        "public_surface_changed": False,
        "installed_v0_changed": False,
        "acceptance_profile": profile,
        "fixture_spec": spec,
        "fixture_spec_sha256": fixture.FIXTURE_SPEC_DIGEST,
        "algorithm": {
            "identity": LOCAL_IDENTITY,
            "description": "AEC3-shaped synthetic shadow-filter DTL + primary NLMS + residual gain",
            "filter_taps": FILTER_TAPS,
            "step_main": STEP_MAIN,
            "step_shadow": STEP_SHADOW,
            "dt_enter": DT_ENTER,
            "dt_exit": DT_EXIT,
            "dt_hangover_frames": DT_HANGOVER,
            "residual_gain_min": GAIN_MIN,
            "real_webrtc_source_or_weights": False,
            "real_webrtc_runtime": False,
            "real_webrtc_model_or_weights": False,
            "provenance_gap": (
                "BLOCKED: no pinned WebRTC AEC3 source, binary, runtime, model "
                "weights or licensed render/capture corpus exists here; no "
                "parity, device-timing, listening or qualification claim is made"
            ),
        },
        "causality": causality_payload(),
        "runs": runs,
        "controls": controls,
        "failures": failures_payload(),
        "crosscheck": crosscheck_payload(),
        "sources": {
            "pins": dict(fixture.SOURCE_PINS),
            "mutable_board": {
                "path": fixture.MUTABLE_BOARD,
                "sha256_at_read": fixture.MUTABLE_BOARD_SHA256_AT_READ,
                "gate": False,
            },
        },
        "disclosure": (
            "Synthetic-only proposal evidence. No WebRTC AEC3 code, binary, "
            "weights, licensed corpus, device timing, listening test, quality "
            "acceptance or release claim is included. Missing or blocked cases "
            "are not promoted to a result."
        ),
    }
    if set(core) != REPORT_KEYS - {"repeat_runs"}:
        raise AssertionError("report_key_set_mismatch")
    core_digest = fixture.sha256_bytes(canonical_bytes(core))
    core["repeat_runs"] = {
        "three_repeats": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest] * 3,
    }
    return core
