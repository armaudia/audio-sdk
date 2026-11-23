# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, dependency-free NLMS acoustic echo cancellation reference.

Everything here is synthetic and model-free.  The fixture emits an explicit
playback/render reference, a known linear synthetic echo path, an independent
near-end source and deterministic capture noise.  No recording, RIR, model
weight, download, licensed runtime, target-device timing or quality claim is
involved.  The measured "reference latency" is the lag between the supplied
render reference and the microphone echo, measured by cross-correlation on an
echo-only interval; it is not a physical device or scheduling latency.
"""

from __future__ import annotations

import hashlib
import json
import math
import operator
import struct
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1

# Optional reference configuration, deliberately small enough for a compact
# time-domain reference implementation.  The synthetic echo path fits inside
# this window both before and after the delay change.
FILTER_TAPS = 96
STEP_SIZE = 0.25
EPSILON = 1e-8
MAX_ABS_INPUT = 4.0
SEED = 20261124

TOTAL_SAMPLES = 51200  # 3.2 s at 16 kHz
SEGMENTS = {
    "silence_end": 6400,       # 0.40 s
    "single_early_end": 9600,  # 0.60 s (early convergence window)
    "single_end": 22400,       # 1.40 s
    "double_end": 35200,       # 2.20 s
    "switch_at": 35200,        # abrupt render/path delay change
    "resingle_end": 41600,     # 2.60 s
    "single_metric_start": 14400,  # 0.90 s: after convergence
    "double_metric_start": 24000,  # 1.50 s
    "post_switch_metric_start": 36800,  # switch + 0.10 s
    "late_post_start": 39200,  # switch + 0.25 s
}

# Primary tap delay is the measurable render-reference latency.  Path B adds
# sixteen samples to every tap to exercise delay change / misalignment.
PATH_A: Tuple[Tuple[int, float], ...] = (
    (32, 0.50), (39, 0.32), (47, -0.22), (58, 0.15), (71, -0.10),
)
PATH_B: Tuple[Tuple[int, float], ...] = (
    (48, 0.46), (55, 0.30), (63, -0.20), (74, 0.14), (87, -0.09),
)
PATH_DELAY_CHANGE_SAMPLES = 16
DELAYED_RENDER_SAMPLES = 32
DROPOUT_START = 28800  # 1.80 s
DROPOUT_END = 31200    # 1.95 s

SOURCE_PINS = {
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "src/audioml_eval/aec.py":
        "84544219098d2c012da38163d49196379eb4f12094fb09cf106e57295ed69351",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "3154212165862651640b2388b4ce8dd62b5a71ad808152820f9b3831488beb89",
    "mutable": True,
}


class ConfigError(ValueError):
    pass


class NlmsConfig:
    """Validated immutable reference configuration."""

    __slots__ = ("filter_taps", "step_size", "epsilon", "max_abs_input",
                 "double_talk_threshold", "double_talk_hold")

    def __init__(self, filter_taps: int = FILTER_TAPS,
                 step_size: float = STEP_SIZE, epsilon: float = EPSILON,
                 max_abs_input: float = MAX_ABS_INPUT,
                 double_talk_threshold: float = 0.40,
                 double_talk_hold: bool = True) -> None:
        if (isinstance(filter_taps, bool) or not isinstance(filter_taps, int)
                or filter_taps <= 0 or filter_taps > 4096):
            raise ConfigError("filter_taps must be a positive bounded integer")
        if (isinstance(step_size, bool) or not isinstance(step_size, (int, float))
                or not math.isfinite(step_size) or not 0.0 < step_size <= 2.0):
            raise ConfigError("step_size must be finite and in (0, 2]")
        if (isinstance(epsilon, bool) or not isinstance(epsilon, (int, float))
                or not math.isfinite(epsilon) or epsilon <= 0.0):
            raise ConfigError("epsilon must be finite and positive")
        if (isinstance(max_abs_input, bool)
                or not isinstance(max_abs_input, (int, float))
                or not math.isfinite(max_abs_input) or max_abs_input <= 0.0):
            raise ConfigError("max_abs_input must be finite and positive")
        if (isinstance(double_talk_threshold, bool)
                or not isinstance(double_talk_threshold, (int, float))
                or not math.isfinite(double_talk_threshold)
                or not 0.0 <= double_talk_threshold <= 1.0):
            raise ConfigError("double_talk_threshold must be in [0, 1]")
        if not isinstance(double_talk_hold, bool):
            raise ConfigError("double_talk_hold must be a bool")
        self.filter_taps = filter_taps
        self.step_size = float(step_size)
        self.epsilon = float(epsilon)
        self.max_abs_input = float(max_abs_input)
        self.double_talk_threshold = float(double_talk_threshold)
        self.double_talk_hold = double_talk_hold

    def as_dict(self) -> Dict[str, object]:
        return {
            "filter_taps": self.filter_taps,
            "step_size": self.step_size,
            "epsilon": self.epsilon,
            "max_abs_input": self.max_abs_input,
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


class NlmsAec:
    """Causal sample-domain NLMS with an explicit per-frame render reference.

    ``process`` takes the microphone frame and, separately, the render frame.
    No reference means no cancellation and no adaptation: the microphone frame
    is passed through unchanged.  A missing result of this kind is never scored
    as an echo-cancellation result.
    """

    def __init__(self, config: Optional[NlmsConfig] = None) -> None:
        self.config = config or NlmsConfig()
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
        self.epoch = epoch
        self.next_sample = first_input_sample
        self.frames = 0
        self.adapted_frames = 0
        self.reference_frames = 0
        self.invalid_count = 0
        self.no_reference_frames = 0
        self.double_talk_frames = 0
        self.last_double_talk = False

    def _double_talk_detected(self, microphone: Sequence[float],
                              reference: Sequence[float]) -> bool:
        """Frame-level normalized cross-correlation hold.

        Far-end-only frames correlate strongly with the render window; an
        independent near-end source lowers the normalized peak.  This is a
        deterministic synthetic detector, not a learned VAD or a claim about
        real double-talk detection.  The hold freezes adaptation only; the
        error output remains available so near-end speech is preserved.
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
            coherence = (cross * cross) / (ref_energy * mic_energy + self.config.epsilon)
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
        padded_mic = tuple(float(value) for value in microphone) + (0.0,) * (FRAME_SAMPLES - length)
        padded_ref = (tuple(float(value) for value in reference) + (0.0,) * (FRAME_SAMPLES - length)
                      if reference is not None else None)
        output: List[float] = []
        adapted = False
        hold = (self.config.double_talk_hold and padded_ref is not None
                and self._double_talk_detected(padded_mic, padded_ref))
        self.last_double_talk = hold
        if hold:
            self.double_talk_frames += 1

        for index in range(FRAME_SAMPLES):
            error, did_adapt = self.process_sample(
                padded_mic[index],
                None if padded_ref is None else padded_ref[index],
                adapt_enabled=not hold)
            adapted = adapted or did_adapt
            if index < length:
                output.append(error if padded_ref is not None else padded_mic[index])

        self.frames += 1
        self.next_sample += length
        if adapted:
            self.adapted_frames += 1
        if padded_ref is None:
            self.no_reference_frames += 1
        status = "ok" if padded_ref is not None else "no_reference_passthrough"
        return ProcessResult(tuple(output), status, padded_ref is not None)

    def process_sample(self, microphone: float, reference: Optional[float],
                       *, adapt_enabled: bool = True) -> Tuple[float, bool]:
        """One causal sample: filter, form error and adapt when referenced."""
        history = self.history
        weights = self.weights
        if reference is not None:
            history.pop()
            history.insert(0, float(reference))
            self.reference_frames += 1
        estimate = sum(map(operator.mul, weights, history))
        error = float(microphone) - estimate
        did_adapt = False
        if reference is not None and adapt_enabled:
            energy = sum(value * value for value in history)
            if energy > self.config.epsilon:
                gain = self.config.step_size * error / (energy + self.config.epsilon)
                for tap in range(self.config.filter_taps):
                    weights[tap] += gain * history[tap]
                did_adapt = True
        return error, did_adapt

    def process_sequence(self, microphone: Sequence[float],
                         reference: Optional[Sequence[float]]) -> Tuple[Tuple[float, ...], str]:
        """Sample-level path used to cross-check the frame-level path."""
        if reference is not None and len(reference) != len(microphone):
            raise ConfigError("reference and microphone lengths differ")
        samples: List[float] = []
        for start in range(0, len(microphone), FRAME_SAMPLES):
            mic_frame = microphone[start:start + FRAME_SAMPLES]
            ref_frame = (None if reference is None
                         else reference[start:start + FRAME_SAMPLES])
            padded_mic = tuple(mic_frame) + (0.0,) * (FRAME_SAMPLES - len(mic_frame))
            padded_ref = (None if ref_frame is None
                          else tuple(ref_frame) + (0.0,) * (FRAME_SAMPLES - len(ref_frame)))
            hold = (self.config.double_talk_hold and padded_ref is not None
                    and self._double_talk_detected(padded_mic, padded_ref))
            if hold:
                self.double_talk_frames += 1
            for index, value in enumerate(mic_frame):
                played = None if padded_ref is None else padded_ref[index]
                samples.append(self.process_sample(float(value), played,
                                                   adapt_enabled=not hold)[0])
        return tuple(samples), "ok"

    def state_digest(self) -> str:
        packed = struct.pack("<%dd" % self.config.filter_taps, *self.weights)
        return hashlib.sha256(packed).hexdigest()

    def weight_l1(self) -> float:
        return sum(abs(value) for value in self.weights)


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
            value += (1.0 / (position + 1.4)) * math.sin(two_pi * frequency * index / SAMPLE_RATE_HZ)
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
    """Return the four deterministic streams for a named condition.

    Keys: ``microphone``, ``reference`` (the *supplied* render reference),
    ``playback`` (the true render signal), ``echo`` and ``near``.  Returning
    both playback and supplied reference makes render latency explicit rather
    than implicit in the cancelled output.
    """
    playback = _speech_like(SEED, TOTAL_SAMPLES, (180.0, 430.0, 900.0), 0.42)
    near_source = _speech_like(SEED + 17, TOTAL_SAMPLES, (220.0, 610.0, 1310.0), 0.36)
    capture_noise = _noise(SEED + 29, TOTAL_SAMPLES, 0.0015)

    if name == "near_only":
        playback = (0.0,) * TOTAL_SAMPLES
        near_gate = _ramp(SEGMENTS["silence_end"], TOTAL_SAMPLES, TOTAL_SAMPLES)
    elif name == "single_talk":
        near_gate = (0.0,) * TOTAL_SAMPLES
    else:
        gate = [0.0] * TOTAL_SAMPLES
        for start, end in ((SEGMENTS["single_end"], SEGMENTS["double_end"]),
                           (SEGMENTS["resingle_end"], TOTAL_SAMPLES)):
            ramp = _ramp(start, end, TOTAL_SAMPLES)
            gate = [max(gate[i], ramp[i]) for i in range(TOTAL_SAMPLES)]
        near_gate = tuple(gate)

    near = tuple(near_source[i] * near_gate[i] for i in range(TOTAL_SAMPLES))
    if name in ("delay_change",):
        echo = list(convolve_path(playback[:SEGMENTS["switch_at"]], PATH_A))
        echo.extend(convolve_path(playback[SEGMENTS["switch_at"]:], PATH_B))
        echo = tuple(echo)
        active_path = PATH_B
    else:
        echo = convolve_path(playback, PATH_A)
        active_path = PATH_A

    microphone = tuple(echo[i] + near[i] + capture_noise[i] for i in range(TOTAL_SAMPLES))
    reference = playback
    reference_mode = "explicit_playback"
    if name == "delayed_render":
        reference = shift_signal(playback, DELAYED_RENDER_SAMPLES)
        reference_mode = "explicit_playback_delayed"
    elif name == "missing_reference":
        reference = None
        reference_mode = "withheld"
    elif name == "reference_dropout":
        reference = list(playback)
        for index in range(DROPOUT_START, DROPOUT_END):
            reference[index] = 0.0
        reference = tuple(reference)
        reference_mode = "explicit_playback_with_zero_render_gap"
    if name in ("silence", "impulse", "step"):
        raise ValueError("use stimulus() for analytic DSP stimuli")
    return {
        "microphone": microphone,
        "reference": reference,
        "playback": playback,
        "echo": echo,
        "near": near,
        "active_path": active_path,
        "reference_mode": reference_mode,
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
        "microphone": tuple(echo),
        "reference": tuple(playback),
        "playback": tuple(playback),
        "echo": echo,
        "near": (0.0,) * TOTAL_SAMPLES,
        "active_path": PATH_A,
        "reference_mode": "explicit_playback",
    }


def erle_db(microphone: Sequence[float], output: Sequence[float],
            start: int, end: int) -> float:
    before = sum(microphone[i] * microphone[i] for i in range(start, end))
    after = sum(output[i] * output[i] for i in range(start, end))
    if before <= 0.0:
        raise ValueError("empty single-talk reference interval")
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
    """Cross-correlation lag on an echo-only interval, searched 0..95 samples."""
    best_lag, best_score = 0, -1.0
    for lag in range(FILTER_TAPS):
        score = 0.0
        for index in range(start, end, 4):
            score += reference[index - lag] * microphone[index]
        if score > best_score:
            best_score, best_lag = score, lag
    return best_lag


def residual_path_l1(path: Sequence[Tuple[int, float]], weights: Sequence[float]) -> float:
    residual = [0.0] * len(weights)
    for delay, gain in path:
        if delay < len(residual):
            residual[delay] += gain
    return sum(abs(residual[i] - weights[i]) for i in range(len(weights)))


def gain_before_feedback_db(path: Sequence[Tuple[int, float]],
                            weights: Sequence[float]) -> float:
    """Synthetic L1 loop-margin proxy, not a measured loudspeaker loop gain."""
    l1 = residual_path_l1(path, weights)
    if l1 <= 1e-12:
        return 120.0
    return max(-120.0, min(120.0, -20.0 * math.log10(l1)))


def run_stream(fixture_data: Dict[str, object], config: Optional[NlmsConfig] = None,
               mode: str = "adaptive", fixed_gain: float = 0.5,
               dropout: bool = False) -> Dict[str, object]:
    """Process one fixture through the public-shape framewise controller."""
    microphone = fixture_data["microphone"]
    reference = fixture_data["reference"]
    engine = NlmsAec(config)
    output: List[float] = []
    statuses: Dict[str, int] = {}
    supplied = 0
    for start in range(0, len(microphone), FRAME_SAMPLES):
        frame = microphone[start:start + FRAME_SAMPLES]
        final = start + FRAME_SAMPLES >= len(microphone)
        ref_frame = (None if reference is None
                     else reference[start:start + FRAME_SAMPLES])
        if dropout and DROPOUT_START <= start < DROPOUT_END:
            ref_frame = None
        if ref_frame is not None:
            supplied += 1
        result = engine.process(frame, ref_frame, final=final)
        statuses[result.status] = statuses.get(result.status, 0) + 1
        if result.status.startswith("rejected"):
            raise AssertionError("fixture produced rejected frame: " + result.status)
        if mode == "adaptive":
            output.extend(result.samples)
        else:
            gain = fixed_gain if mode == "fixed_attenuation" else 1.0
            output.extend(value * gain for value in frame[:len(result.samples)])
    result_output = tuple(output)
    return {
        "output": result_output,
        "output_digest": tensor_digest(result_output),
        "statuses": statuses,
        "supplied_reference_frames": supplied,
        "state_digest": engine.state_digest(),
        "frames": engine.frames,
        "adapted_frames": engine.adapted_frames,
        "reference_frames": engine.reference_frames,
        "invalid_count": engine.invalid_count,
        "no_reference_frames": engine.no_reference_frames,
        "double_talk_frames": engine.double_talk_frames,
        "final_weights": tuple(engine.weights),
    }


def _metrics(fixture_data: Dict[str, object], run: Dict[str, object],
             condition: str, variant: str = "adaptive") -> Dict[str, object]:
    microphone = fixture_data["microphone"]
    near = fixture_data["near"]
    output = run["output"]
    active_path = fixture_data["active_path"]
    # Fixed gain and identity controls do not estimate an echo path at all.
    weights = (run["final_weights"] if variant.startswith("nlms")
               else [0.0] * FILTER_TAPS)
    seg = SEGMENTS
    single = (seg["single_metric_start"], seg["single_end"])
    double = (seg["double_metric_start"], seg["double_end"])
    late_double = (seg["resingle_end"], TOTAL_SAMPLES)
    metrics: Dict[str, object] = {
        "single_talk_erle_db": erle_db(microphone, output, *single),
        "early_single_talk_erle_db": erle_db(
            microphone, output, seg["silence_end"], seg["single_early_end"]),
        "echo_return_loss_db": erle_db(microphone, output, *single),
        "gain_before_feedback_db": gain_before_feedback_db(active_path, weights),
        "peak_abs": peak_abs(output),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "output_samples": len(output),
    }
    if any(near[i] != 0.0 for i in range(*double)):
        metrics["double_talk_near_snr_db"] = near_snr_db(near, output, *double)
        metrics["late_double_talk_near_snr_db"] = near_snr_db(near, output, *late_double)
    else:
        metrics["double_talk_near_snr_db"] = None
        metrics["near_end_note"] = "far-end-only condition; no near-end speech to preserve"
    if condition in ("delay_change",):
        pre = (seg["single_metric_start"], seg["single_end"])
        post_early = (seg["post_switch_metric_start"], seg["late_post_start"])
        post_late = (seg["late_post_start"], seg["resingle_end"])
        metrics.update({
            "pre_change_erle_db": erle_db(microphone, output, *pre),
            "post_change_early_erle_db": erle_db(microphone, output, *post_early),
            "post_change_late_erle_db": erle_db(microphone, output, *post_late),
            "reconvergence_delta_db":
                erle_db(microphone, output, *post_late) -
                erle_db(microphone, output, *post_early),
        })
    return metrics


def _run_record(name: str, fixture_data: Dict[str, object],
                run: Dict[str, object], *, variant: str,
                qualifies: bool, status_override: Optional[str] = None,
                note: str = "") -> Dict[str, object]:
    supplied = fixture_data["reference"] is not None
    metrics = None
    if supplied and not name.startswith("dsp_"):
        metrics = _metrics(fixture_data, run, name, variant=variant)
    status = status_override or ("ok" if metrics is not None else "blocked")
    record: Dict[str, object] = {
        "condition": name,
        "variant": variant,
        "status": status,
        "qualifies": bool(qualifies and metrics is not None),
        "reference_mode": fixture_data["reference_mode"],
        "metrics": metrics,
        "output_digest": tensor_digest(run["output"]),
        "state_digest": run["state_digest"],
        "frame_status_counts": run["statuses"],
        "supplied_reference_frames": run["supplied_reference_frames"],
        "adapted_frames": run["adapted_frames"],
        "no_reference_frames": run["no_reference_frames"],
        "double_talk_hold_frames": run["double_talk_frames"],
        "invalid_frames": run["invalid_count"],
        "note": note,
    }
    return record


def build_report() -> Dict[str, object]:
    fixtures = {name: fixture(name) for name in (
        "single_talk", "double_talk", "delay_change", "near_only",
        "delayed_render", "reference_dropout", "missing_reference")}
    dsp = {name: stimulus(name) for name in ("impulse", "step", "silence")}
    config = NlmsConfig()

    runs: Dict[str, object] = {}
    for name, data in fixtures.items():
        adaptive = run_stream(data, config)
        if name == "missing_reference":
            runs[name] = _run_record(
                name, data, adaptive, variant="nlms_adaptive", qualifies=False,
                status_override="blocked_no_reference",
                note="No playback reference supplied; passthrough only, not a cancellation result.")
        elif name == "delayed_render":
            runs[name] = _run_record(
                name, data, adaptive, variant="nlms_adaptive", qualifies=False,
                status_override="misaligned_reference",
                note="Reference delayed %d samples; score reported but excluded from qualification."
                     % DELAYED_RENDER_SAMPLES)
        elif name == "reference_dropout":
            runs[name] = _run_record(
                name, data, adaptive, variant="nlms_adaptive", qualifies=False,
                status_override="partial_reference",
                note="Reference zeroed for %d samples; score reported but excluded from qualification."
                     % (DROPOUT_END - DROPOUT_START))
        else:
            runs[name] = _run_record(name, data, adaptive, variant="nlms_adaptive",
                                     qualifies=True)

    controls: Dict[str, object] = {}
    for control in ("fixed_attenuation", "identity"):
        for name in ("single_talk", "double_talk", "delay_change"):
            data = fixtures[name]
            run = run_stream(data, config, mode=control)
            controls[control + "_" + name] = _run_record(
                name, data, run, variant=control, qualifies=False,
                note="Fixed/identity control, measured separately from adaptive-reference metrics.")

    dsp_controls: Dict[str, object] = {}
    for name, data in dsp.items():
        run = run_stream(data, config)
        output = run["output"]
        exp = data["echo"]
        if name == "impulse":
            peak_index = max(range(len(output)), key=lambda i: abs(output[i]))
            detail = {"peak_sample_index": peak_index,
                      "peak_magnitude": output[peak_index],
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
            "echo_digest": tensor_digest(exp),
            "state_digest": run["state_digest"],
            "detail": detail,
            "status": "ok",
        }

    clean = fixture("near_only")
    clean_run = run_stream(clean, config)
    clean_out = clean_run["output"]
    clean_near = clean["near"]
    clean_detail = {
        "status": "ok",
        "near_snr_db": near_snr_db(clean_near, clean_out,
                                   SEGMENTS["silence_end"], TOTAL_SAMPLES),
        "output_digest": clean_run["output_digest"],
        "near_digest": tensor_digest(clean_near),
        "reference_frames": clean_run["reference_frames"],
        "note": "Silent render with active near-end speech-like source; no adaptation expected.",
    }
    dsp_controls["clean_speech_like_near_only"] = clean_detail

    lag = measure_reference_lag(fixtures["single_talk"]["reference"],
                                fixtures["single_talk"]["microphone"])
    delayed_lag = measure_reference_lag(fixtures["delayed_render"]["reference"],
                                        fixtures["delayed_render"]["microphone"])
    alignment = {
        "method": "cross-correlation of supplied render reference with echo-only microphone interval",
        "search_lags_samples": [0, FILTER_TAPS - 1],
        "echo_only_interval_samples": [SEGMENTS["silence_end"], SEGMENTS["single_end"]],
        "measured_lag_samples": lag,
        "intended_primary_tap_delay_samples": PATH_A[0][0],
        "alignment_error_samples": lag - PATH_A[0][0],
        "delayed_render_measured_lag_samples": delayed_lag,
        "delayed_render_misalignment_samples": lag - delayed_lag,
        "algorithmic_delay_samples": 0,
        "buffering_delay_samples": 0,
        "note": "Reference latency is a synthetic fixture alignment, not device, scheduling or playback-buffer latency.",
    }

    adverse: Dict[str, object] = {}
    engine = NlmsAec(config)
    frame = (0.1,) * FRAME_SAMPLES
    reference = (0.05,) * FRAME_SAMPLES
    ok = engine.process(frame, reference)
    before = engine.state_digest()
    invalid_results = {}
    invalid_results["nonfinite_microphone"] = engine.process(
        tuple(float("nan") if i == 0 else 0.1 for i in range(FRAME_SAMPLES)), reference).status
    invalid_results["out_of_range_microphone"] = engine.process(
        (9.0,) * FRAME_SAMPLES, reference).status
    invalid_results["short_microphone"] = engine.process((0.1,) * 8, reference).status
    invalid_results["nonfinite_reference"] = engine.process(
        frame, (float("inf"),) * FRAME_SAMPLES).status
    invalid_results["stale_epoch"] = engine.process(
        frame, reference, epoch=engine.epoch + 1, first_sample=engine.next_sample).status
    invalid_results["stale_position"] = engine.process(
        frame, reference, first_sample=engine.next_sample + 1).status
    after = engine.state_digest()
    no_ref = engine.process(frame, None)
    adverse = {
        "invalid_statuses": invalid_results,
        "invalid_count": engine.invalid_count,
        "state_unchanged_after_invalid": before == after,
        "no_reference_status": no_ref.status,
        "no_reference_is_passthrough": no_ref.samples == frame,
        "accepted_frame_status": ok.status,
        "config_rejections": [
            str(type(error).__name__) for error in _config_rejection_errors()
        ],
    }

    independent_a = run_stream(fixtures["single_talk"], config)
    independent_b = run_stream(fixtures["single_talk"], config)
    proof_mic = fixtures["single_talk"]["microphone"][:20 * FRAME_SAMPLES]
    proof_ref = fixtures["single_talk"]["reference"][:20 * FRAME_SAMPLES]
    framewise_engine = NlmsAec(config)
    framewise_out: List[float] = []
    for start in range(0, len(proof_mic), FRAME_SAMPLES):
        framewise_out.extend(framewise_engine.process(
            proof_mic[start:start + FRAME_SAMPLES],
            proof_ref[start:start + FRAME_SAMPLES]).samples)
    samplewise_engine = NlmsAec(config)
    samplewise_out, _ = samplewise_engine.process_sequence(proof_mic, proof_ref)
    replay = NlmsAec(config)
    replay.reset(7, 0)
    state = {
        "deterministic_output_digest": independent_a["output_digest"] == independent_b["output_digest"],
        "deterministic_state_digest": independent_a["state_digest"] == independent_b["state_digest"],
        "framewise_equals_samplewise": tensor_digest(framewise_out) == tensor_digest(samplewise_out),
        "framewise_equals_samplewise_state":
            framewise_engine.state_digest() == samplewise_engine.state_digest(),
        "reset_epoch_accepted": replay.epoch == 7 and replay.next_sample == 0,
        "reset_rejects_stale_epoch": replay.process(frame, reference, epoch=6).status.startswith("rejected"),
        "final_partial_frame_length": len(NlmsAec(config).process((0.1,) * 37, (0.05,) * 37,
                                                                 final=True).samples),
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

    fixture_spec = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "total_samples": TOTAL_SAMPLES,
        "seed": SEED,
        "filter_taps": FILTER_TAPS,
        "step_size": STEP_SIZE,
        "epsilon": EPSILON,
        "double_talk_threshold": config.double_talk_threshold,
        "double_talk_hold": config.double_talk_hold,
        "path_a": list(PATH_A),
        "path_b": list(PATH_B),
        "delay_change_samples": PATH_DELAY_CHANGE_SAMPLES,
        "delayed_render_samples": DELAYED_RENDER_SAMPLES,
        "segments": SEGMENTS,
        "dropout_interval_samples": [DROPOUT_START, DROPOUT_END],
        "fixed_attenuation_gain": 0.5,
        "sample_format": "f32",
        "render_reference": "explicit synthetic playback stream returned alongside microphone",
        "excitation": {
            "far_end": "seeded speech-like harmonic/noise source (analytic, no corpus)",
            "near_end": "independent seeded speech-like source, gated in double-talk windows",
            "dsp": "impulse, step and digital silence",
        },
        "noise": "deterministic LCG capture noise, level 0.0015 full scale",
        "movement": "abrupt synthetic echo-path tap shift at switch_at (PATH_A to PATH_B)",
        "reset_schedule": {
            "stream_start_epoch": 1,
            "first_input_sample": 0,
            "explicit_reset_test_epoch": 7,
            "stale_epoch_and_position_rejected": True,
        },
        "room_acoustics_measured": False,
        "real_device_claim": False,
    }
    fixture_digest = hashlib.sha256(canonical_bytes(fixture_spec)).hexdigest()

    return {
        "schema_id": "audio-sdk/nlms-aec/report/0.1",
        "task": "SDK-NLMS-AEC",
        "component": "nlms-aec",
        "verification_profile": "room",
        "status": "synthetic-reference-evaluated",
        "disposition": "optional-task-local-reference",
        "scope": "DSP-adjacent synthetic AEC evidence; no measured room acoustics or real-device claim",
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
        "board_snapshot": BOARD_SNAPSHOT,
        "runs": runs,
        "controls": controls,
        "fixed_attenuation_separate_from_adaptive": True,
        "dsp_controls": dsp_controls,
        "alignment": alignment,
        "adverse": adverse,
        "state": state,
        "non_claims": [
            "No measured room impulse response, real recording, licensed corpus or AECMOS model",
            "No loudspeaker/microphone loop, gain-before-feedback measurement or target-device timing",
            "No listening, MOS, STOI on real speech, release approval or installed-provider change",
            "Missing, delayed, misaligned and partial-reference runs never qualify a candidate",
        ],
    }


def _config_rejection_errors() -> List[Exception]:
    errors: List[Exception] = []
    for kwargs in ({"filter_taps": 0}, {"filter_taps": 1.5},
                   {"step_size": 0.0}, {"step_size": float("nan")},
                   {"epsilon": -1.0}, {"max_abs_input": 0.0},
                   {"double_talk_threshold": 1.5},
                   {"double_talk_hold": "yes"}):
        try:
            NlmsConfig(**kwargs)
        except ConfigError as error:
            errors.append(error)
        else:
            raise AssertionError("invalid config accepted: %r" % (kwargs,))
    return errors


def canonical_report(report: Dict[str, object]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
