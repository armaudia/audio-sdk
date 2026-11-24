# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, dependency-free guarded RLS acoustic echo cancellation reference.

Everything here is synthetic and model-free.  The fixture emits an explicit
playback/render sidechain, a known sparse linear echo path, an independent
near-end source and deterministic capture noise.  The controller is causal RLS
only; it has no second adaptive processor.  A zero/degenerate-reference guard
prevents the covariance windup that made the historical full-RLS pilot become
nonfinite on near-end-only material, and a finite-state guard freezes adaptation
if any numerical/boundedness violation is detected.  No recording, RIR, model
weight, download, licensed runtime, target-device timing or release claim is
involved.  Measured "reference latency" is only a synthetic fixture lag.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import operator
import struct
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1

# Compact, fixed reference configuration.  These are not production-tuned
# values.  Both frozen synthetic paths fit inside the 24-tap window.
FILTER_TAPS = 24
RLS_LAMBDA = 0.995
RLS_P0 = 1.0
EPSILON = 1e-8
MAX_ABS_INPUT = 4.0
WEIGHT_L1_LIMIT = 8.0
MATRIX_ABS_LIMIT = 1e12
DOUBLE_TALK_THRESHOLD = 0.70
DOUBLE_TALK_HOLD = True

SEED = 20261124
TOTAL_SAMPLES = 51200  # 3.2 s at 16 kHz
SEGMENTS = {
    "silence_end": 6400,
    "single_early_end": 9600,
    "single_end": 22400,
    "double_end": 35200,
    "switch_at": 35200,
    "resingle_end": 41600,
    "single_metric_start": 14400,
    "double_metric_start": 24000,
    "post_switch_metric_start": 36800,
    "late_post_start": 39200,
}

# Tap delays are samples after the current render sample.  Path B is the frozen
# abrupt movement/path-change condition.
PATH_A: Tuple[Tuple[int, float], ...] = (
    (4, 0.50), (9, 0.32), (14, -0.22), (19, 0.15), (22, -0.10),
)
PATH_B: Tuple[Tuple[int, float], ...] = (
    (8, 0.46), (13, 0.30), (18, -0.20), (22, 0.14),
)
PATH_DELAY_CHANGE_SAMPLES = 4
DELAYED_RENDER_SAMPLES = 4
DROPOUT_START = 28800
DROPOUT_END = 31200
BURST_START = SEGMENTS["double_metric_start"]
BURST_END = BURST_START + 1600
BURST_SCALE = 2.5

# Historical control: a zero far-end reference leaves P = P0 * lambda^-n until
# overflow, then 0 * inf produces nonfinite weights.  This longer frozen
# extension reproduces that mechanism without changing the candidate fixture.
LEGACY_SAMPLES = 160000  # 10 s at 16 kHz
LEGACY_LAMBDA = 0.995
LEGACY_P0 = 100.0
LEGACY_VERIFY_STEPS = 160

SOURCE_PINS = {
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/check.py":
        "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
    "research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md":
        "4577d59347d9f48a693228ccbf40a9de77494294e7d0df111c98e8591c3e438e",
    "src/audioml_eval/aec.py":
        "84544219098d2c012da38163d49196379eb4f12094fb09cf106e57295ed69351",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "c7bdd981e0347aa74e32db917fc924303db057ba669e91c2b50d968abe61c950",
    "mutable": True,
}

PHASES = ("rls", "frozen")
SAFETY_REASONS = ("none", "nonfinite_state", "boundedness_violation")


class ConfigError(ValueError):
    pass


class RlsConfig:
    """Validated immutable reference configuration."""

    __slots__ = ("filter_taps", "rls_lambda", "rls_p0", "epsilon",
                 "max_abs_input", "weight_l1_limit", "matrix_abs_limit",
                 "double_talk_threshold", "double_talk_hold")

    def __init__(self, filter_taps: int = FILTER_TAPS,
                 rls_lambda: float = RLS_LAMBDA, rls_p0: float = RLS_P0,
                 epsilon: float = EPSILON, max_abs_input: float = MAX_ABS_INPUT,
                 weight_l1_limit: float = WEIGHT_L1_LIMIT,
                 matrix_abs_limit: float = MATRIX_ABS_LIMIT,
                 double_talk_threshold: float = DOUBLE_TALK_THRESHOLD,
                 double_talk_hold: bool = DOUBLE_TALK_HOLD) -> None:
        if (isinstance(filter_taps, bool) or not isinstance(filter_taps, int)
                or filter_taps <= 0 or filter_taps > 4096):
            raise ConfigError("filter_taps must be a positive bounded integer")
        if (isinstance(rls_lambda, bool)
                or not isinstance(rls_lambda, (int, float))
                or not math.isfinite(rls_lambda) or not 0.5 <= rls_lambda < 1.0):
            raise ConfigError("rls_lambda must be finite and in [0.5, 1)")
        for name, value in (("rls_p0", rls_p0), ("epsilon", epsilon),
                            ("max_abs_input", max_abs_input),
                            ("weight_l1_limit", weight_l1_limit),
                            ("matrix_abs_limit", matrix_abs_limit)):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value <= 0.0):
                raise ConfigError(name + " must be finite and positive")
        if (isinstance(double_talk_threshold, bool)
                or not isinstance(double_talk_threshold, (int, float))
                or not math.isfinite(double_talk_threshold)
                or not 0.0 <= double_talk_threshold <= 1.0):
            raise ConfigError("double_talk_threshold must be in [0, 1]")
        if not isinstance(double_talk_hold, bool):
            raise ConfigError("double_talk_hold must be a bool")
        self.filter_taps = filter_taps
        self.rls_lambda = float(rls_lambda)
        self.rls_p0 = float(rls_p0)
        self.epsilon = float(epsilon)
        self.max_abs_input = float(max_abs_input)
        self.weight_l1_limit = float(weight_l1_limit)
        self.matrix_abs_limit = float(matrix_abs_limit)
        self.double_talk_threshold = float(double_talk_threshold)
        self.double_talk_hold = double_talk_hold

    def as_dict(self) -> Dict[str, object]:
        return {
            "filter_taps": self.filter_taps,
            "rls_lambda": self.rls_lambda,
            "rls_p0": self.rls_p0,
            "epsilon": self.epsilon,
            "max_abs_input": self.max_abs_input,
            "weight_l1_limit": self.weight_l1_limit,
            "matrix_abs_limit": self.matrix_abs_limit,
            "double_talk_threshold": self.double_talk_threshold,
            "double_talk_hold": self.double_talk_hold,
        }


class ProcessResult:
    __slots__ = ("samples", "status", "reference_used")

    def __init__(self, samples: Tuple[float, ...], status: str,
                 reference_used: bool) -> None:
        self.samples = samples
        self.status = status
        self.reference_used = reference_used


class RlsAec:
    """Causal guarded RLS with an explicit per-frame render sidechain.

    ``process`` takes the microphone frame and, separately, the render frame.
    No reference means no cancellation and no adaptation: the microphone frame
    is passed through unchanged.  Such a result is never scored as cancellation.
    Zero/degenerate reference energy skips RLS updates, which is the specific
    prevention for historical near-end-only covariance windup.  Any nonfinite or
    boundedness violation restores finite state and freezes adaptation; it never
    emits a nonfinite sample.
    """

    __slots__ = ("config", "epoch", "weights", "history", "matrix",
                 "matrix_valid", "phase", "safety_reason", "safety_freezes",
                 "skipped_updates", "processed_samples", "next_sample",
                 "frames", "adapted_frames", "reference_frames",
                 "no_reference_frames", "double_talk_frames", "invalid_count",
                 "last_double_talk", "max_weight_l1", "max_abs_weight",
                 "max_matrix_abs")

    def __init__(self, config: Optional[RlsConfig] = None) -> None:
        self.config = config or RlsConfig()
        self.epoch = 0
        self.reset(1, 0)

    def reset(self, epoch: int, first_input_sample: int) -> None:
        if (isinstance(epoch, bool) or not isinstance(epoch, int)
                or epoch <= self.epoch or isinstance(first_input_sample, bool)
                or not isinstance(first_input_sample, int)
                or first_input_sample < 0):
            raise ConfigError("invalid reset arguments")
        taps = self.config.filter_taps
        self.weights = [0.0] * taps
        self.history = [0.0] * taps  # index 0 = most recent render sample
        scale = self.config.rls_p0
        self.matrix = [[scale if row == column else 0.0
                        for column in range(taps)] for row in range(taps)]
        self.matrix_valid = True
        self.phase = "rls"
        self.safety_reason = "none"
        self.safety_freezes = 0
        self.skipped_updates = 0
        self.processed_samples = 0
        self.next_sample = first_input_sample
        self.frames = 0
        self.adapted_frames = 0
        self.reference_frames = 0
        self.no_reference_frames = 0
        self.double_talk_frames = 0
        self.invalid_count = 0
        self.last_double_talk = False
        self.max_weight_l1 = 0.0
        self.max_abs_weight = 0.0
        self.max_matrix_abs = 0.0
        self.epoch = epoch

    def drain(self) -> ProcessResult:
        """End-of-stream check: no samples and no state mutation."""
        return ProcessResult((), "end_of_stream", False)

    def _double_talk_detected(self, microphone: Sequence[float],
                              reference: Sequence[float]) -> bool:
        """Frame-level normalized cross-correlation adaptation hold.

        Far-end-only frames correlate strongly with the render window; an
        independent near-end source lowers the normalized peak.  This holds
        adaptation only; the error output remains available so near-end speech
        is preserved.  It is a deterministic synthetic detector, not a learned
        VAD or a claim about real double talk.
        """
        window = list(reversed(self.history)) + list(reference)
        mic_energy = sum(value * value for value in microphone)
        ref_energy = sum(value * value for value in window)
        if mic_energy <= self.config.epsilon or ref_energy <= self.config.epsilon:
            return False
        best = 0.0
        for lag in range(self.config.filter_taps):
            cross = 0.0
            for index in range(FRAME_SAMPLES):
                cross += window[lag + index] * microphone[index]
            coherence = (cross * cross) / (ref_energy * mic_energy
                                           + self.config.epsilon)
            if coherence > best:
                best = coherence
        return best < self.config.double_talk_threshold

    def _valid_frame(self, values: Sequence[float], allow_partial: bool) -> bool:
        if not isinstance(values, (tuple, list)) or not values:
            return False
        if len(values) > FRAME_SAMPLES:
            return False
        if not allow_partial and len(values) != FRAME_SAMPLES:
            return False
        limit = self.config.max_abs_input
        return all((not isinstance(value, bool) and isinstance(value, (int, float))
                    and math.isfinite(value) and abs(value) <= limit)
                   for value in values)

    def _track_state(self) -> None:
        total = sum(abs(value) for value in self.weights)
        peak = max((abs(value) for value in self.weights), default=0.0)
        matrix_peak = max((abs(value) for row in self.matrix for value in row),
                          default=0.0)
        self.max_weight_l1 = max(self.max_weight_l1, total)
        self.max_abs_weight = max(self.max_abs_weight, peak)
        self.max_matrix_abs = max(self.max_matrix_abs, matrix_peak)

    def _freeze(self, reason: str) -> None:
        """Restore finite state and stop adapting for the rest of this stream."""
        self.weights = [0.0] * self.config.filter_taps
        self.matrix_valid = False
        self.phase = "frozen"
        self.safety_reason = reason
        self.safety_freezes += 1

    def process(self, microphone: Sequence[float],
                reference: Optional[Sequence[float]] = None,
                *, epoch: Optional[int] = None,
                first_sample: Optional[int] = None,
                final: bool = False) -> ProcessResult:
        if ((epoch is not None and epoch != self.epoch)
                or (first_sample is not None and first_sample != self.next_sample)):
            self.invalid_count += 1
            return ProcessResult((), "rejected_stale_frame", False)
        if not self._valid_frame(microphone, final):
            self.invalid_count += 1
            return ProcessResult((), "rejected_invalid_microphone", False)
        if reference is not None and not self._valid_frame(reference, final):
            self.invalid_count += 1
            return ProcessResult((), "rejected_invalid_reference", False)
        if reference is not None and len(reference) != len(microphone):
            self.invalid_count += 1
            return ProcessResult((), "rejected_reference_length", False)

        length = len(microphone)
        padded_mic = (tuple(float(value) for value in microphone)
                      + (0.0,) * (FRAME_SAMPLES - length))
        padded_ref = (tuple(float(value) for value in reference)
                      + (0.0,) * (FRAME_SAMPLES - length)
                      if reference is not None else None)
        hold = (self.config.double_talk_hold and padded_ref is not None
                and self._double_talk_detected(padded_mic, padded_ref))
        self.last_double_talk = hold
        if hold:
            self.double_talk_frames += 1

        output: List[float] = []
        adapted = False
        for index in range(FRAME_SAMPLES):
            error, did_adapt = self.process_sample(
                padded_mic[index],
                None if padded_ref is None else padded_ref[index],
                adapt_enabled=not hold)
            adapted = adapted or did_adapt
            if index < length:
                output.append(error if padded_ref is not None else padded_mic[index])

        self.frames += 1
        self.processed_samples += length
        self.next_sample += length
        if adapted:
            self.adapted_frames += 1
        if padded_ref is None:
            self.no_reference_frames += 1
        self._track_state()
        status = "ok" if padded_ref is not None else "no_reference_passthrough"
        return ProcessResult(tuple(output), status, padded_ref is not None)

    def process_sample(self, microphone: float, reference: Optional[float],
                       *, adapt_enabled: bool = True) -> Tuple[float, bool]:
        """One causal sample: filter, form error, adapt only when it is safe."""
        history = self.history
        weights = self.weights
        if reference is not None:
            history.pop()
            history.insert(0, float(reference))
            self.reference_frames += 1

        estimate = sum(map(operator.mul, weights, history))
        error = float(microphone) - estimate
        if not math.isfinite(error):
            self._freeze("nonfinite_state")
            error = float(microphone)
        if (reference is None or not adapt_enabled
                or self.phase == "frozen" or not math.isfinite(error)):
            return error, False

        energy = sum(value * value for value in history)
        if not math.isfinite(energy) or energy <= self.config.epsilon:
            # This is the near-end-only/zero-reference guard: P is not divided
            # by lambda here, so it cannot wind up to infinity.
            self.skipped_updates += 1
            return error, False

        taps = self.config.filter_taps
        safe_weights = list(weights)
        safe_matrix = self.matrix
        unsafe = False
        matrix = self.matrix
        if matrix is None or self.phase == "frozen":
            unsafe = True
        else:
            px = [sum(matrix[i][j] * history[j] for j in range(taps))
                  for i in range(taps)]
            denominator = self.config.rls_lambda + sum(
                history[i] * px[i] for i in range(taps))
            if (not math.isfinite(denominator)
                    or denominator <= self.config.epsilon
                    or not all(math.isfinite(value) for value in px)):
                unsafe = True
            else:
                gain = [value / denominator for value in px]
                candidate = [safe_weights[i] + gain[i] * error
                             for i in range(taps)]
                unsafe = (not all(math.isfinite(value) for value in gain)
                          or not all(math.isfinite(value) for value in candidate)
                          or sum(abs(value) for value in candidate)
                          > self.config.weight_l1_limit)
                if not unsafe:
                    xtp = [sum(matrix[j][i] * history[j]
                               for j in range(taps)) for i in range(taps)]
                    updated = [[(matrix[i][j] - gain[i] * xtp[j])
                                / self.config.rls_lambda
                                for j in range(taps)] for i in range(taps)]
                    peak = max((abs(value) for row in updated for value in row),
                               default=0.0)
                    unsafe = (not all(math.isfinite(value)
                                      for row in updated for value in row)
                              or peak > self.config.matrix_abs_limit)
                    if not unsafe:
                        self.matrix = updated
                        self.weights = candidate

        if unsafe:
            self.weights = safe_weights
            self.matrix = safe_matrix
            self._freeze("boundedness_violation")
            return error, False
        return error, True

    def process_sequence(self, microphone: Sequence[float],
                         reference: Optional[Sequence[float]]
                         ) -> Tuple[Tuple[float, ...], str]:
        """Frame-level replay used to cross-check the direct sample path."""
        if reference is not None and len(reference) != len(microphone):
            raise ConfigError("reference and microphone lengths differ")
        samples: List[float] = []
        for start in range(0, len(microphone), FRAME_SAMPLES):
            frame = microphone[start:start + FRAME_SAMPLES]
            ref = (None if reference is None
                   else reference[start:start + FRAME_SAMPLES])
            result = self.process(frame, ref)
            if result.status.startswith("rejected"):
                raise ConfigError("rejected frame in sample replay")
            samples.extend(result.samples)
        return tuple(samples), "ok"

    def state_digest(self) -> str:
        payload = struct.pack("<%dd" % self.config.filter_taps, *self.weights)
        payload += struct.pack("<3q", PHASES.index(self.phase),
                               self.safety_freezes, self.skipped_updates)
        return hashlib.sha256(payload).hexdigest()

    def weight_l1(self) -> float:
        return math.fsum(abs(value) for value in self.weights)


def tensor_digest(values: Iterable[float]) -> str:
    packed = struct.pack("<%dd" % len(values), *[float(value) for value in values])
    return hashlib.sha256(packed).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _rng(seed: int):
    state = seed & 0xFFFFFFFF

    def next_value() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296.0

    return next_value


def _speech_like(seed: int, n: int, formants: Sequence[float],
                 amplitude: float) -> Tuple[float, ...]:
    rand = _rng(seed)
    envelope = 0.25
    out: List[float] = []
    two_pi = 2.0 * math.pi
    for index in range(n):
        envelope = 0.985 * envelope + 0.015 * rand()
        env = 0.35 + 1.15 * envelope
        value = 0.0
        for position, frequency in enumerate(formants):
            value += (1.0 / (position + 1.4)) * math.sin(
                two_pi * frequency * index / SAMPLE_RATE_HZ)
        value += 0.28 * (2.0 * rand() - 1.0)
        out.append(amplitude * env * value)
    peak = max(abs(value) for value in out) or 1.0
    scale = min(1.0, 0.38 / peak)
    return tuple(value * scale for value in out)


def _ramp(start: int, end: int, n: int, ramp: int = 320) -> Tuple[float, ...]:
    gate = [0.0] * n
    for index in range(max(0, start), min(n, end)):
        rise = min(1.0, (index - start) / ramp) if ramp else 1.0
        fall = min(1.0, (end - index) / ramp) if ramp else 1.0
        gate[index] = max(0.0, min(rise, fall))
    return tuple(gate)


def convolve_path(signal: Sequence[float],
                  path: Sequence[Tuple[int, float]]) -> Tuple[float, ...]:
    out = [0.0] * len(signal)
    for delay, gain in path:
        for index in range(delay, len(signal)):
            out[index] += gain * signal[index - delay]
    return tuple(out)


def shift_signal(signal: Sequence[float], delay: int) -> Tuple[float, ...]:
    if delay <= 0:
        return tuple(signal)
    return (0.0,) * delay + tuple(signal[:len(signal) - delay])


def _noise(seed: int, n: int, level: float) -> Tuple[float, ...]:
    rand = _rng(seed)
    return tuple(level * (2.0 * rand() - 1.0) for _ in range(n))


def fixture(name: str) -> Dict[str, object]:
    """Return deterministic streams for a named frozen condition.

    ``reference`` is the *supplied* render stream; ``playback`` is the true
    render signal.  Returning both makes sidechain latency explicit.
    """
    playback = _speech_like(SEED, TOTAL_SAMPLES, (180.0, 430.0, 900.0), 0.42)
    near_source = _speech_like(SEED + 17, TOTAL_SAMPLES,
                               (220.0, 610.0, 1310.0), 0.36)
    capture_noise = _noise(SEED + 29, TOTAL_SAMPLES, 0.0015)

    if name == "near_only":
        playback = (0.0,) * TOTAL_SAMPLES
        near_gate = _ramp(SEGMENTS["silence_end"], TOTAL_SAMPLES, TOTAL_SAMPLES)
    elif name == "single_talk":
        near_gate = (0.0,) * TOTAL_SAMPLES
    elif name in ("double_talk", "delay_change", "delayed_render",
                  "reference_dropout", "missing_reference", "near_burst"):
        gate = [0.0] * TOTAL_SAMPLES
        for start, end in ((SEGMENTS["single_end"], SEGMENTS["double_end"]),
                           (SEGMENTS["resingle_end"], TOTAL_SAMPLES)):
            ramp = _ramp(start, end, TOTAL_SAMPLES)
            gate = [max(gate[i], ramp[i]) for i in range(TOTAL_SAMPLES)]
        near_gate = tuple(gate)
    else:
        raise ValueError("use stimulus() for analytic DSP stimuli: " + name)

    near = list(near_source[i] * near_gate[i] for i in range(TOTAL_SAMPLES))
    if name == "near_burst":
        for index in range(BURST_START, BURST_END):
            near[index] *= BURST_SCALE
    near = tuple(near)

    if name == "delay_change":
        echo = list(convolve_path(playback[:SEGMENTS["switch_at"]], PATH_A))
        echo.extend(convolve_path(playback[SEGMENTS["switch_at"]:], PATH_B))
        echo = tuple(echo)
        active_path = PATH_B
    else:
        echo = convolve_path(playback, PATH_A)
        active_path = PATH_A

    microphone = tuple(echo[i] + near[i] + capture_noise[i]
                       for i in range(TOTAL_SAMPLES))
    reference: Optional[Tuple[float, ...]] = playback
    reference_mode = "explicit_playback"
    if name == "delayed_render":
        reference = shift_signal(playback, DELAYED_RENDER_SAMPLES)
        reference_mode = "explicit_playback_shifted"
    elif name == "missing_reference":
        reference = None
        reference_mode = "withheld"
    elif name == "reference_dropout":
        reference_mode = "explicit_playback_with_sidechain_gap"

    return {
        "microphone": microphone,
        "reference": reference,
        "playback": playback,
        "echo": echo,
        "near": near,
        "active_path": active_path,
        "reference_mode": reference_mode,
        "dropout_interval": ((DROPOUT_START, DROPOUT_END)
                             if name == "reference_dropout" else None),
    }


def stimulus(name: str) -> Dict[str, object]:
    """Analytic DSP stimuli: impulse, step and digital silence."""
    playback = [0.0] * TOTAL_SAMPLES
    if name == "impulse":
        playback[10 * FRAME_SAMPLES] = 0.5
    elif name == "step":
        for index in range(10 * FRAME_SAMPLES, TOTAL_SAMPLES):
            playback[index] = 0.25
    elif name == "silence":
        pass
    else:
        raise ValueError("unknown stimulus: " + name)
    echo = convolve_path(playback, PATH_A)
    return {
        "microphone": echo,
        "reference": tuple(playback),
        "playback": tuple(playback),
        "echo": echo,
        "near": (0.0,) * TOTAL_SAMPLES,
        "active_path": PATH_A,
        "reference_mode": "explicit_playback",
        "dropout_interval": None,
    }


def erle_db(microphone: Sequence[float], output: Sequence[float],
            start: int, end: int) -> float:
    """Echo return loss enhancement on a far-end-only interval."""
    before = sum(microphone[i] * microphone[i] for i in range(start, end))
    after = sum(output[i] * output[i] for i in range(start, end))
    if before <= 0.0:
        raise ValueError("empty far-end-only reference interval")
    if after <= 1e-24:
        return 120.0
    return max(-120.0, min(120.0, 10.0 * math.log10(before / after)))


def near_snr_db(near: Sequence[float], output: Sequence[float],
                start: int, end: int) -> float:
    wanted = sum(near[i] * near[i] for i in range(start, end))
    error = sum((output[i] - near[i]) ** 2 for i in range(start, end))
    if wanted <= 0.0:
        raise ValueError("empty near-end interval")
    if error <= 1e-24:
        return 120.0
    return max(-120.0, min(120.0, 10.0 * math.log10(wanted / error)))


def peak_abs(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def measure_reference_lag(reference: Sequence[float],
                          microphone: Sequence[float],
                          start: int = 6400, end: int = 22400) -> int:
    """Cross-correlation lag on an echo-only interval, searched 0..taps-1."""
    best_lag, best_score = 0, -1.0
    for lag in range(FILTER_TAPS):
        score = 0.0
        for index in range(start, end, 4):
            score += reference[index - lag] * microphone[index]
        if score > best_score:
            best_score, best_lag = score, lag
    return best_lag


def residual_path_l1(path: Sequence[Tuple[int, float]],
                     weights: Sequence[float]) -> float:
    residual = [0.0] * len(weights)
    for delay, gain in path:
        if delay < len(residual):
            residual[delay] += gain
    return sum(abs(residual[i] - weights[i]) for i in range(len(weights)))


def gain_before_feedback_db(path: Sequence[Tuple[int, float]],
                            weights: Sequence[float]) -> float:
    """Synthetic L1 loop-margin proxy, never a measured loudspeaker loop gain."""
    residual = residual_path_l1(path, weights)
    if residual <= 1e-12:
        return 120.0
    return max(-120.0, min(120.0, -20.0 * math.log10(residual)))


def run_stream(fixture_data: Dict[str, object],
               config: Optional[RlsConfig] = None,
               mode: str = "rls_adaptive", fixed_gain: float = 0.5) -> Dict[str, object]:
    """Process one fixture through the framewise controller."""
    microphone = fixture_data["microphone"]
    reference = fixture_data["reference"]
    dropout = fixture_data.get("dropout_interval")
    if mode in ("fixed_attenuation", "identity"):
        gain = fixed_gain if mode == "fixed_attenuation" else 1.0
        output = tuple(float(value) * gain for value in microphone)
        frames = (len(microphone) + FRAME_SAMPLES - 1) // FRAME_SAMPLES
        return {
            "output": output,
            "output_digest": tensor_digest(output),
            "statuses": {"no_reference_passthrough": frames},
            "supplied_reference_frames": 0,
            "state_digest": hashlib.sha256(b"\x00" * 8 * FILTER_TAPS).hexdigest(),
            "final_weights": tuple([0.0] * FILTER_TAPS),
            "frames": frames,
            "adapted_frames": 0,
            "reference_frames": 0,
            "invalid_count": 0,
            "no_reference_frames": frames,
            "double_talk_frames": 0,
            "safety_freezes": 0,
            "skipped_updates": 0,
            "safety_reason": "none",
            "phase": "rls",
            "max_weight_l1": 0.0,
            "max_abs_weight": 0.0,
            "max_matrix_abs": 0.0,
        }
    if mode not in ("rls_adaptive", "rls_no_hold"):
        raise ConfigError("unknown run mode: " + mode)
    if config is None:
        config = RlsConfig()
    if mode == "rls_no_hold":
        config = RlsConfig(double_talk_hold=False)

    engine = RlsAec(config)
    output: List[float] = []
    statuses: Dict[str, int] = {}
    supplied = 0
    for start in range(0, len(microphone), FRAME_SAMPLES):
        frame = microphone[start:start + FRAME_SAMPLES]
        ref_frame = (None if reference is None
                     else reference[start:start + FRAME_SAMPLES])
        if (dropout is not None and reference is not None
                and dropout[0] <= start < dropout[1]):
            ref_frame = None
        if ref_frame is not None:
            supplied += 1
        result = engine.process(frame, ref_frame)
        statuses[result.status] = statuses.get(result.status, 0) + 1
        if result.status.startswith("rejected"):
            raise AssertionError("fixture produced rejected frame: " + result.status)
        output.extend(result.samples)

    return {
        "output": tuple(output),
        "output_digest": tensor_digest(output),
        "statuses": statuses,
        "supplied_reference_frames": supplied,
        "state_digest": engine.state_digest(),
        "final_weights": tuple(engine.weights),
        "frames": engine.frames,
        "adapted_frames": engine.adapted_frames,
        "reference_frames": engine.reference_frames,
        "invalid_count": engine.invalid_count,
        "no_reference_frames": engine.no_reference_frames,
        "double_talk_frames": engine.double_talk_frames,
        "safety_freezes": engine.safety_freezes,
        "skipped_updates": engine.skipped_updates,
        "safety_reason": engine.safety_reason,
        "phase": engine.phase,
        "max_weight_l1": engine.max_weight_l1,
        "max_abs_weight": engine.max_abs_weight,
        "max_matrix_abs": engine.max_matrix_abs,
    }


def legacy_rls_near_only() -> Dict[str, object]:
    """Closed-form reproduction of historical unguarded full-RLS blow-up.

    With an all-zero reference the RLS gain is exactly zero while P is finite,
    and the inverse covariance evolves as P0 * lambda^-n.  Once that value
    overflows, the next 0 * inf gain produces nonfinite weights.  The first
    160 iterative steps are checked against the closed form.
    """
    limit = sys.float_info.max
    exponent = math.log(limit / LEGACY_P0) / -math.log(LEGACY_LAMBDA)
    first_nonfinite = int(math.ceil(exponent))
    value = LEGACY_P0
    max_relative_error = 0.0
    for step in range(1, LEGACY_VERIFY_STEPS + 1):
        value /= LEGACY_LAMBDA
        expected = LEGACY_P0 * LEGACY_LAMBDA ** (-step)
        max_relative_error = max(max_relative_error,
                                 abs(value - expected) / expected)
    return {
        "status": "historical_failure_reproduced",
        "qualifies": False,
        "samples": LEGACY_SAMPLES,
        "lambda": LEGACY_LAMBDA,
        "p0": LEGACY_P0,
        "recursion": "P_n = P_0 * lambda^-n for an all-zero far-end reference",
        "first_nonfinite_sample": first_nonfinite,
        "first_nonfinite_seconds": round(first_nonfinite / SAMPLE_RATE_HZ, 3),
        "overflow_within_fixture": first_nonfinite < LEGACY_SAMPLES,
        "iterative_steps_checked": LEGACY_VERIFY_STEPS,
        "max_relative_error_vs_closed_form": max_relative_error,
        "failure_mechanism": "zero-reference covariance windup then 0 * inf gain",
        "historical_source": (
            "agent-hybrid-aec-real/REPORT.md: full RLS was nonfinite on "
            "near-end-only recordings"),
        "candidate_prevention": (
            "skip RLS updates when reference energy <= epsilon; restore finite "
            "state and freeze on any nonfinite or boundedness violation"),
    }


def _metrics(fixture_data: Dict[str, object], run: Dict[str, object],
             condition: str, variant: str) -> Dict[str, object]:
    microphone = fixture_data["microphone"]
    near = fixture_data["near"]
    playback = fixture_data["playback"]
    output = run["output"]
    seg = SEGMENTS
    adaptive = variant in ("rls_adaptive", "rls_no_hold")
    weights = run["final_weights"] if adaptive else tuple([0.0] * FILTER_TAPS)
    single = (seg["single_metric_start"], seg["single_end"])
    far_energy = sum(playback[i] * playback[i] for i in range(*single))
    echo_attenuation: Dict[str, object] = {
        "valid_far_end_only_window_samples": list(single),
        "far_end_energy_in_window": far_energy,
        "gain_before_feedback_db": gain_before_feedback_db(
            fixture_data["active_path"], weights),
        "peak_abs": peak_abs(output),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "output_samples": len(output),
        "max_weight_l1": run["max_weight_l1"],
        "max_abs_weight": run["max_abs_weight"],
        "max_matrix_abs": run["max_matrix_abs"],
        "weight_l1_limit": WEIGHT_L1_LIMIT,
        "matrix_abs_limit": MATRIX_ABS_LIMIT,
        "weights_bounded": run["max_weight_l1"] <= WEIGHT_L1_LIMIT,
        "safety_freezes": run["safety_freezes"],
        "skipped_updates": run["skipped_updates"],
        "final_phase": run["phase"],
    }
    if far_energy > 1e-24:
        echo_attenuation.update({
            "early_single_talk_erle_db": erle_db(
                microphone, output, seg["silence_end"], seg["single_early_end"]),
            "single_talk_erle_db": erle_db(microphone, output, *single),
            "echo_return_loss_db": erle_db(microphone, output, *single),
        })
    else:
        echo_attenuation.update({
            "early_single_talk_erle_db": None,
            "single_talk_erle_db": None,
            "echo_return_loss_db": None,
            "note": "silent render in the far-end-only window; ERLE is not defined",
        })

    near_preservation: Dict[str, object] = {}
    double = (seg["double_metric_start"], seg["double_end"])
    late = (seg["resingle_end"], TOTAL_SAMPLES)
    if any(near[index] != 0.0 for index in range(*double)):
        near_preservation = {
            "double_talk_window_samples": list(double),
            "double_talk_near_snr_db": near_snr_db(near, output, *double),
            "late_double_talk_near_snr_db": near_snr_db(near, output, *late),
            "double_talk_hold_frames": run["double_talk_frames"],
        }
    else:
        near_preservation = {
            "double_talk_window_samples": list(double),
            "double_talk_near_snr_db": None,
            "note": "far-end-only condition; no near-end speech to preserve",
        }
    if condition == "delay_change":
        echo_attenuation.update({
            "path_change_sample": seg["switch_at"],
            "pre_change_erle_db": erle_db(
                microphone, output, seg["single_metric_start"], seg["single_end"]),
            "post_change_early_erle_db": erle_db(
                microphone, output, seg["post_switch_metric_start"],
                seg["late_post_start"]),
            "post_change_late_erle_db": erle_db(
                microphone, output, seg["late_post_start"], seg["resingle_end"]),
        })
        echo_attenuation["reconvergence_delta_db"] = (
            echo_attenuation["post_change_late_erle_db"]
            - echo_attenuation["post_change_early_erle_db"])
    return {
        "echo_attenuation": echo_attenuation,
        "near_end_preservation": near_preservation,
        "far_end_only_erle_excludes_double_talk": True,
    }


def _run_record(name: str, fixture_data: Dict[str, object],
                run: Dict[str, object], *, variant: str,
                status_override: Optional[str] = None,
                note: str = "") -> Dict[str, object]:
    """Every run is recorded; nothing here is promoted to a release candidate."""
    metrics = None
    if fixture_data["reference"] is not None:
        metrics = _metrics(fixture_data, run, name, variant)
    status = status_override or "ok_synthetic"
    return {
        "condition": name,
        "variant": variant,
        "status": status,
        "qualifies": False,  # proposal-only: no processor is exposed
        "reference_mode": fixture_data["reference_mode"],
        "metrics": metrics,
        "output_digest": run["output_digest"],
        "state_digest": run["state_digest"],
        "frame_status_counts": run["statuses"],
        "supplied_reference_frames": run["supplied_reference_frames"],
        "adapted_frames": run["adapted_frames"],
        "no_reference_frames": run["no_reference_frames"],
        "double_talk_hold_frames": run["double_talk_frames"],
        "safety_freezes": run["safety_freezes"],
        "skipped_updates": run["skipped_updates"],
        "safety_reason": run["safety_reason"],
        "final_phase": run["phase"],
        "invalid_frames": run["invalid_count"],
        "note": note,
    }


def _config_rejection_errors() -> List[Exception]:
    errors: List[Exception] = []
    for kwargs in ({"filter_taps": 0}, {"filter_taps": 1.5},
                   {"rls_lambda": 1.0}, {"rls_lambda": float("nan")},
                   {"rls_p0": 0.0}, {"epsilon": -1.0},
                   {"max_abs_input": 0.0}, {"weight_l1_limit": 0.0},
                   {"matrix_abs_limit": float("inf")},
                   {"double_talk_threshold": 1.5},
                   {"double_talk_hold": "yes"}):
        try:
            RlsConfig(**kwargs)
        except ConfigError as error:
            errors.append(error)
        else:
            raise AssertionError("invalid config accepted: %r" % (kwargs,))
    return errors


@functools.lru_cache(maxsize=1)
def build_report() -> Dict[str, object]:
    fixtures = {name: fixture(name) for name in (
        "single_talk", "double_talk", "delay_change", "near_only",
        "delayed_render", "reference_dropout", "missing_reference",
        "near_burst")}
    config = RlsConfig()

    notes = {
        "delayed_render": ("Reference shifted %d samples; scored but excluded "
                           "from qualification." % DELAYED_RENDER_SAMPLES),
        "reference_dropout": ("Reference sidechain withheld for %d samples; "
                              "scored but excluded from qualification."
                              % (DROPOUT_END - DROPOUT_START)),
        "missing_reference": ("No render reference supplied: passthrough only, "
                              "not a cancellation result."),
        "near_burst": ("Adversarial amplified near-end burst under active "
                       "far-end; scored as an adverse case, never as release "
                       "evidence."),
    }
    overrides = {
        "delayed_render": "misaligned_reference",
        "reference_dropout": "partial_reference",
        "missing_reference": "blocked_no_reference",
        "near_burst": "adversarial_near_burst",
    }
    runs: Dict[str, object] = {}
    for name, data in fixtures.items():
        run = run_stream(data, config)
        runs[name] = _run_record(
            name, data, run, variant="rls_adaptive",
            status_override=overrides.get(name), note=notes.get(name, ""))

    controls: Dict[str, object] = {}
    for mode, conditions in (
            ("fixed_attenuation", ("single_talk", "double_talk")),
            ("identity", ("single_talk", "double_talk")),
            ("rls_no_hold", ("double_talk",))):
        for name in conditions:
            data = fixtures[name]
            run = run_stream(data, config, mode=mode)
            controls[mode + "_" + name] = _run_record(
                name, data, run, variant=mode,
                note="Control measured separately; double-talk preservation is not a release gate.")

    legacy = legacy_rls_near_only()
    extended = {
        "microphone": _noise(SEED + 29, LEGACY_SAMPLES, 0.0015),
        "reference": (0.0,) * LEGACY_SAMPLES,
        "playback": (0.0,) * LEGACY_SAMPLES,
        "echo": (0.0,) * LEGACY_SAMPLES,
        "near": (0.0,) * LEGACY_SAMPLES,
        "active_path": PATH_A,
        "reference_mode": "explicit_zero_render_extended",
        "dropout_interval": None,
    }
    extended_run = run_stream(extended, config)
    near_only_stability = {
        "status": "synthetic_pass_not_release",
        "qualifies": False,
        "samples": LEGACY_SAMPLES,
        "output_digest": extended_run["output_digest"],
        "nonfinite_count": sum(1 for value in extended_run["output"]
                               if not math.isfinite(value)),
        "peak_abs": peak_abs(extended_run["output"]),
        "max_weight_l1": extended_run["max_weight_l1"],
        "weight_l1_limit": WEIGHT_L1_LIMIT,
        "weights_bounded": extended_run["max_weight_l1"] <= WEIGHT_L1_LIMIT,
        "max_matrix_abs": extended_run["max_matrix_abs"],
        "matrix_abs_limit": MATRIX_ABS_LIMIT,
        "skipped_updates": extended_run["skipped_updates"],
        "safety_freezes": extended_run["safety_freezes"],
        "final_phase": extended_run["phase"],
        "note": ("Zero-reference extension that is nonfinite under the legacy "
                 "unguarded recursion stays finite; RLS updates are skipped."),
    }

    dsp = {name: stimulus(name) for name in ("impulse", "step", "silence")}
    dsp_controls: Dict[str, object] = {}
    for name, data in dsp.items():
        run = run_stream(data, config)
        output = run["output"]
        if name == "impulse":
            index = max(range(len(output)), key=lambda i: abs(output[i]))
            detail = {"peak_sample_index": index,
                      "peak_magnitude": output[index],
                      "primary_tap_delay_samples": PATH_A[0][0],
                      "algorithmic_delay_samples": 0}
        elif name == "step":
            first = next((i for i, value in enumerate(output) if value != 0.0), -1)
            detail = {"first_nonzero_sample_index": first,
                      "expected_sample_index": 10 * FRAME_SAMPLES + PATH_A[0][0]}
        else:
            detail = {"peak_abs": peak_abs(output),
                      "nonzero_count": sum(1 for value in output if value != 0.0)}
        dsp_controls[name] = {
            "output_digest": run["output_digest"],
            "input_digest": tensor_digest(data["microphone"]),
            "echo_digest": tensor_digest(data["echo"]),
            "state_digest": run["state_digest"],
            "detail": detail,
            "status": "ok",
        }

    clean = fixture("near_only")
    clean_run = run_stream(clean, config)
    clean_detail = {
        "status": "ok",
        "near_snr_db": near_snr_db(
            clean["near"], clean_run["output"],
            SEGMENTS["silence_end"], TOTAL_SAMPLES),
        "output_digest": clean_run["output_digest"],
        "near_digest": tensor_digest(clean["near"]),
        "nonfinite_count": sum(1 for value in clean_run["output"]
                               if not math.isfinite(value)),
        "skipped_updates": clean_run["skipped_updates"],
        "note": "Silent render with active near-end speech-like source; no RLS update.",
    }
    dsp_controls["clean_speech_like_near_only"] = clean_detail

    lag = measure_reference_lag(fixtures["single_talk"]["reference"],
                                fixtures["single_talk"]["microphone"])
    delayed_lag = measure_reference_lag(
        fixtures["delayed_render"]["reference"],
        fixtures["delayed_render"]["microphone"])
    alignment = {
        "method": "cross-correlation of supplied render with echo-only microphone interval",
        "search_lags_samples": [0, FILTER_TAPS - 1],
        "echo_only_interval_samples": [SEGMENTS["silence_end"], SEGMENTS["single_end"]],
        "measured_lag_samples": lag,
        "intended_primary_tap_delay_samples": PATH_A[0][0],
        "alignment_error_samples": lag - PATH_A[0][0],
        "delayed_render_measured_lag_samples": delayed_lag,
        "delayed_render_misalignment_samples": lag - delayed_lag,
        "algorithmic_delay_samples": 0,
        "buffering_delay_samples": 0,
        "note": "Fixture alignment only; no device, scheduling or playback-buffer latency claim.",
    }

    engine = RlsAec(config)
    frame = (0.1,) * FRAME_SAMPLES
    reference_frame = (0.05,) * FRAME_SAMPLES
    ok = engine.process(frame, reference_frame)
    before = engine.state_digest()
    invalid_results = {
        "nonfinite_microphone": engine.process(
            tuple(float("nan") if i == 0 else 0.1 for i in range(FRAME_SAMPLES)),
            reference_frame).status,
        "out_of_range_microphone": engine.process(
            (9.0,) * FRAME_SAMPLES, reference_frame).status,
        "short_microphone": engine.process((0.1,) * 8, reference_frame).status,
        "nonfinite_reference": engine.process(
            frame, (float("inf"),) * FRAME_SAMPLES).status,
        "stale_epoch": engine.process(
            frame, reference_frame, epoch=engine.epoch + 1,
            first_sample=engine.next_sample).status,
        "stale_position": engine.process(
            frame, reference_frame,
            first_sample=engine.next_sample + 1).status,
    }
    after_invalid = engine.state_digest()
    no_ref = engine.process(frame, None)

    injected = RlsAec(config)
    injected.process(frame, reference_frame)
    injected.weights[0] = float("inf")
    injected_result = injected.process(frame, reference_frame)

    replay = RlsAec(config)
    replay.reset(7, 0)
    deterministic_a = run_stream(fixtures["single_talk"], config)
    deterministic_b = run_stream(fixtures["single_talk"], config)
    proof_mic = fixtures["single_talk"]["microphone"][:20 * FRAME_SAMPLES]
    proof_ref = fixtures["single_talk"]["reference"][:20 * FRAME_SAMPLES]
    framewise = RlsAec(config)
    framewise_out: List[float] = []
    for start in range(0, len(proof_mic), FRAME_SAMPLES):
        framewise_out.extend(framewise.process(
            proof_mic[start:start + FRAME_SAMPLES],
            proof_ref[start:start + FRAME_SAMPLES]).samples)
    samplewise = RlsAec(config)
    samplewise_out, _ = samplewise.process_sequence(proof_mic, proof_ref)
    state = {
        "deterministic_output_digest": (
            deterministic_a["output_digest"] == deterministic_b["output_digest"]),
        "deterministic_state_digest": (
            deterministic_a["state_digest"] == deterministic_b["state_digest"]),
        "framewise_equals_samplewise": (
            tensor_digest(framewise_out) == tensor_digest(samplewise_out)),
        "framewise_equals_samplewise_state": (
            framewise.state_digest() == samplewise.state_digest()),
        "reset_epoch_accepted": replay.epoch == 7 and replay.next_sample == 0,
        "reset_rejects_stale_epoch": replay.process(
            frame, reference_frame, epoch=6).status.startswith("rejected"),
        "final_partial_frame_length": len(
            RlsAec(config).process((0.1,) * 37, (0.05,) * 37,
                                   final=True).samples),
        "drain_returns_end_of_stream": RlsAec(config).drain().status
                                        == "end_of_stream",
        "drain_returns_no_samples": RlsAec(config).drain().samples == (),
        "safety_guard_status": injected_result.status,
        "safety_guard_output_finite": all(math.isfinite(value)
                                          for value in injected_result.samples),
        "safety_guard_freeze": injected.phase == "frozen"
                               and injected.safety_freezes == 1
                               and injected.safety_reason == "nonfinite_state",
        "safety_guard_weights_finite": all(math.isfinite(value)
                                           for value in injected.weights),
    }
    adverse = {
        "invalid_statuses": invalid_results,
        "invalid_count": engine.invalid_count,
        "state_unchanged_after_invalid": before == after_invalid,
        "no_reference_status": no_ref.status,
        "no_reference_is_passthrough": no_ref.samples == frame,
        "no_reference_weights_unchanged": engine.state_digest() == after_invalid,
        "accepted_frame_status": ok.status,
        "config_rejections": [type(error).__name__
                              for error in _config_rejection_errors()],
        "legacy_divergence_nonfinite": legacy,
        "adversarial_near_burst_status":
            runs["near_burst"]["status"],
        "adversarial_near_burst_nonfinite_count":
            runs["near_burst"]["metrics"]["echo_attenuation"]["nonfinite_count"],
        "no_result_missing": all(record["status"] is not None
                                 for record in runs.values()),
    }

    double_talk = runs["double_talk"]["metrics"]["near_end_preservation"]
    fixed_double = controls["fixed_attenuation_double_talk"]["metrics"][
        "near_end_preservation"]
    identity_double = controls["identity_double_talk"]["metrics"][
        "near_end_preservation"]
    no_hold_double = controls["rls_no_hold_double_talk"]["metrics"][
        "near_end_preservation"]
    double_talk_preservation = {
        "status": "control_only_not_release",
        "qualifies": False,
        "guarded_rls_near_snr_db": double_talk["double_talk_near_snr_db"],
        "fixed_attenuation_near_snr_db": fixed_double["double_talk_near_snr_db"],
        "identity_near_snr_db": identity_double["double_talk_near_snr_db"],
        "rls_without_hold_near_snr_db": no_hold_double["double_talk_near_snr_db"],
        "guarded_rls_hold_frames": runs["double_talk"]["double_talk_hold_frames"],
        "interpretation": ("Double talk is a preservation control on this "
                           "synthetic fixture, not a release qualification."),
    }

    fixture_digests = {}
    for name, data in {**fixtures, **dsp}.items():
        fixture_digests[name] = {
            "microphone": tensor_digest(data["microphone"]),
            "reference": (tensor_digest(data["reference"])
                          if data["reference"] is not None else None),
            "playback": tensor_digest(data["playback"]),
            "near": tensor_digest(data["near"]),
            "echo": tensor_digest(data["echo"]),
        }
    fixture_digests["legacy_zero_reference_extension"] = {
        "samples": LEGACY_SAMPLES,
        "microphone": tensor_digest(extended["microphone"]),
        "reference": tensor_digest(extended["reference"]),
    }

    fixture_spec = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "f32",
        "frame_samples": FRAME_SAMPLES,
        "total_samples": TOTAL_SAMPLES,
        "seed": SEED,
        "filter_taps": FILTER_TAPS,
        "rls_lambda": RLS_LAMBDA,
        "rls_p0": RLS_P0,
        "epsilon": EPSILON,
        "max_abs_input": MAX_ABS_INPUT,
        "weight_l1_limit": WEIGHT_L1_LIMIT,
        "matrix_abs_limit": MATRIX_ABS_LIMIT,
        "double_talk_threshold": DOUBLE_TALK_THRESHOLD,
        "double_talk_hold": config.double_talk_hold,
        "path_a": list(PATH_A),
        "path_b": list(PATH_B),
        "delay_change_samples": PATH_DELAY_CHANGE_SAMPLES,
        "delayed_render_samples": DELAYED_RENDER_SAMPLES,
        "segments": SEGMENTS,
        "sidechain_dropout_samples": [DROPOUT_START, DROPOUT_END],
        "near_burst": {"interval_samples": [BURST_START, BURST_END],
                       "near_scale": BURST_SCALE},
        "fixed_attenuation_gain": 0.5,
        "excitation": {
            "far_end": "seeded speech-like harmonic/noise source (analytic, no corpus)",
            "near_end": "independent seeded speech-like source, gated in double-talk windows",
            "dsp": "impulse, step and digital silence",
        },
        "noise": "deterministic LCG capture noise, level 0.0015 full scale",
        "movement": "abrupt synthetic echo-path tap shift at switch_at",
        "reset_schedule": {
            "stream_start_epoch": 1,
            "first_input_sample": 0,
            "explicit_reset_test_epoch": 7,
            "stale_epoch_and_position_rejected": True,
        },
        "legacy_zero_reference_extension": {
            "samples": LEGACY_SAMPLES,
            "lambda": LEGACY_LAMBDA,
            "p0": LEGACY_P0,
            "seed": SEED + 29,
        },
        "room_acoustics_measured": False,
        "real_device_claim": False,
    }
    fixture_digest = hashlib.sha256(canonical_bytes(fixture_spec)).hexdigest()

    return {
        "schema_id": "audio-sdk/rls-aec/report/0.1",
        "task": "SDK-RLS-AEC",
        "component": "rls-aec",
        "verification_profile": "room",
        "profile_interpretation": (
            "DSP-adjacent synthetic evidence under the Room profile; no measured "
            "room acoustics or real-device claim"),
        "status": "proposal_only",
        "completeness": "incomplete",
        "qualification": "not_qualified",
        "disposition": "optional-task-local-developer-evidence",
        "decision": {
            "promotion": "defer",
            "expose_as_processor": False,
            "reason": ("Synthetic guarded RLS evidence establishes finite output "
                       "and near-only stability in-fixture, but recorded room, "
                       "double-talk, loop-gain, device and rights gates remain open."),
        },
        "no_missing_result_may_qualify": True,
        "fixed_attenuation_separate_from_adaptive": True,
        "metric_separation": {
            "echo_attenuation": "far-end-only windows only",
            "near_end_preservation": "double-talk and adverse windows only",
            "gain_before_feedback": "synthetic L1 residual-path proxy, not measured loop gain",
        },
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
        },
        "fixture_spec": fixture_spec,
        "fixture_digest": fixture_digest,
        "fixture_digests": fixture_digests,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "runs": runs,
        "controls": controls,
        "legacy_rls_only": legacy,
        "near_only_stability": near_only_stability,
        "double_talk_preservation": double_talk_preservation,
        "dsp_controls": dsp_controls,
        "alignment": alignment,
        "adverse": adverse,
        "state": state,
        "release_gates": [
            "Paired licensed render/capture recordings with known loop timing and held-out speech rights",
            "Measured loudspeaker-loop gain-before-feedback and device timing with buffers, clock drift and target-device CPU/memory/deadline measurement",
            "Double-talk, path-change and nonlinear-loudspeaker assessment with AECMOS, ASR and listening preservation gates",
            "Provider/license/catalog intake before any default, installed or production processor",
        ],
        "non_claims": [
            "No measured room impulse response, real recording, licensed corpus or AECMOS model",
            "No loudspeaker loop, gain-before-feedback measurement or target-device timing",
            "No listening, ASR, real-speech MOS/STOI, release approval or installed-provider change",
            "Missing, delayed, misaligned, partial, adversarial or nonfinite runs never qualify a candidate",
        ],
    }


def canonical_report(report: Dict[str, object]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
