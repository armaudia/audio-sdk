"""Deterministic synthetic Block-NLMS acoustic feedback cancellation reference.

SDK-BLOCK-NLMS-AFC. Task-local, model-free reference only. It uses the frozen
v0 format (16 kHz, mono, f32, 160 samples/frame) exclusively and does not
change any SDK header, descriptor, registry, default or shared build file.

The controller requires an explicit caller-supplied playback reference. There
is no inference, discovery or implicit far-end signal. The reference is the
actual signal sent to the loudspeaker, pinned as an f32 asset with a fixed
alignment prefix before playback sample 0. This module owns both the adaptive
reference/adaptation measurements (ERLE,
convergence, tracking, reference alignment) and the separate closed-loop
attenuation measurements (gain-before-feedback, onset sweep, tail decay).
They are never mixed: ERLE is not an attenuation or stability result, and
simulator gain-before-feedback is not a measured acoustic room value.

All stimuli are analytic or seeded LCG; no recording, model, download, device
or benchmark bundle is read or produced.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CONTRACT_ID = "audio-sdk/block-nlms-afc-reference/0.1"
TASK_ID = "SDK-BLOCK-NLMS-AFC"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
TAPS = 32
BLOCK_SAMPLES = FRAME_SAMPLES
LOOP_DELAY_SAMPLES = 160
MAX_LATENCY_SAMPLES = 32
# Asset layout: zeros(ASSET_PREFIX) followed by playback samples. The extra
# 2*MAX_LATENCY region absorbs positive and negative alignment corrections.
ASSET_PREFIX = TAPS + LOOP_DELAY_SAMPLES + 2 * MAX_LATENCY_SAMPLES
REFERENCE_OFFSET = ASSET_PREFIX - LOOP_DELAY_SAMPLES
PROVIDER_ID = "dsp.block-nlms-afc.afcref.v0"
ASSET_ID = "afc.playback-reference.f32"

# Pinned external evidence. The board is mutable shared state; its digest is a
# read-time snapshot and is not a qualification source.
SOURCE_PINS = {
    "research/feedback_control_20261028.md":
        "47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "schemas/descriptor.schema.json":
        "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "7e27b37f6d53cc76a96bab73b2f24ec7983ea05a03e1562e5963975378e7cbfd",
    "mutable": True,
    "qualification_source": False,
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "profile": "afc",
    "taps": TAPS,
    "block_samples": BLOCK_SAMPLES,
    "step_size": 0.1,
    "normalization_factor": 8.0,
    "epsilon": 0.000001,
    "min_adaptation_power": 0.0001,
    "leakage": 0.9999,
    "reference_latency_samples": 0,
    "double_talk_coherence": 0.35,
    "double_talk_abs": 0.0001,
    "max_abs_input": 4.0,
    "max_abs_reference": 4.0,
    "output_ceiling": 4.0,
    "margin_db": -3.0,
    "fixed_margin_db": -5.0,
    "require_reference": True,
}

PROFILES = ("afc", "afc_margin", "fixed_margin", "identity")
REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES = {
    "step_size": (0.01, 1.0),
    "normalization_factor": (1.0, 64.0),
    "epsilon": (1e-12, 0.1),
    "min_adaptation_power": (1e-8, 0.1),
    "leakage": (0.9, 1.0),
    "double_talk_coherence": (0.05, 0.95),
    "double_talk_abs": (1e-12, 1.0),
    "max_abs_input": (0.25, 16.0),
    "max_abs_reference": (0.25, 16.0),
    "output_ceiling": (0.25, 16.0),
    "margin_db": (-24.0, 0.0),
    "fixed_margin_db": (-24.0, 0.0),
}
_INTEGER_KEYS = ("taps", "block_samples", "reference_latency_samples")


class Status(str, Enum):
    OK = "ok"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_POSITION = "rejected_position"
    CLOSED = "closed"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples (the v0 format)."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(value))
                                   for value in values)).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    """Fail closed on missing, malformed, nonfinite or out-of-range settings."""
    if config is None:
        return Status.REJECTED_MISSING
    if not isinstance(config, dict):
        return Status.REJECTED_INVALID
    if any(key not in config for key in REQUIRED_KEYS):
        return Status.REJECTED_MISSING
    if any(key not in REQUIRED_KEYS for key in config):
        return Status.REJECTED_INVALID
    if config["profile"] not in PROFILES:
        return Status.REJECTED_INVALID
    if config["require_reference"] is not True:
        return Status.REJECTED_INVALID
    if config["taps"] != TAPS or config["block_samples"] != BLOCK_SAMPLES:
        return Status.REJECTED_INVALID
    latency = config["reference_latency_samples"]
    if (not isinstance(latency, int) or isinstance(latency, bool)
            or latency < 0 or latency > MAX_LATENCY_SAMPLES):
        return Status.REJECTED_INVALID
    for key, (low, high) in _NUMERIC_RANGES.items():
        value = config[key]
        if not _is_number(value):
            return Status.REJECTED_INVALID
        number = float(value)
        if not math.isfinite(number):
            return Status.REJECTED_NONFINITE
        if number < low or number > high:
            return Status.REJECTED_INVALID
    for key in _INTEGER_KEYS:
        value = config[key]
        if isinstance(value, bool) or int(value) != value:
            return Status.REJECTED_INVALID
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


@dataclass
class AfcState:
    epoch: int = 7
    next_input_sample: int = 0
    weights: List[float] = field(default_factory=lambda: [0.0] * TAPS)
    frames: int = 0
    adapted_frames: int = 0
    double_talk_frames: int = 0
    transitions: List[str] = field(default_factory=list)
    invalid_count: int = 0
    mode: str = "cold_start"
    closed: bool = False

    def copy(self) -> "AfcState":
        return AfcState(
            epoch=self.epoch, next_input_sample=self.next_input_sample,
            weights=list(self.weights), frames=self.frames,
            adapted_frames=self.adapted_frames,
            double_talk_frames=self.double_talk_frames,
            transitions=list(self.transitions), invalid_count=self.invalid_count,
            mode=self.mode, closed=self.closed)

    def digest(self) -> str:
        return object_digest({
            "epoch": self.epoch,
            "next_input_sample": self.next_input_sample,
            "weights": [round(value, 12) for value in self.weights],
            "frames": self.frames,
            "adapted_frames": self.adapted_frames,
            "double_talk_frames": self.double_talk_frames,
            "mode": self.mode,
        })


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    residual_power: float = 0.0
    mic_power: float = 0.0
    adapted: bool = False
    state_digest: str = ""


class AfcController:
    """Block-NLMS AFC with an explicit, caller-owned playback reference.

    The reference asset is pinned at construction. Playback sample 0 sits at
    asset index ``ASSET_PREFIX``; the first microphone frame reads from
    ``REFERENCE_OFFSET = ASSET_PREFIX - LOOP_DELAY_SAMPLES``.
    ``reference_latency_samples`` is an explicit, bounded alignment correction.
    With no reference the controller refuses to
    be created: no implicit playback signal is ever inferred from the
    microphone input.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 reference: Optional[Sequence[float]] = None,
                 epoch: int = 7, first_input_sample: int = 0) -> None:
        status = validate_config(config)
        if status is not Status.OK:
            raise ValueError(status.value)
        if reference is None or len(reference) == 0:
            raise ValueError(Status.REJECTED_MISSING.value)
        if len(reference) < ASSET_PREFIX:
            raise ValueError(Status.REJECTED_TENSOR.value)
        if any(not math.isfinite(float(value)) for value in reference):
            raise ValueError(Status.REJECTED_NONFINITE.value)
        if any(abs(float(value)) > float(config["max_abs_reference"])
               for value in reference):
            raise ValueError(Status.REJECTED_INVALID.value)
        self.config = dict(config or DEFAULT_CONFIG)
        self.reference = [float(value) for value in reference]
        self.playback_cursor = 0
        self.state = AfcState(epoch=epoch, next_input_sample=first_input_sample)

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]],
               reference: Optional[Sequence[float]],
               epoch: int = 7, first_input_sample: int = 0
               ) -> Tuple[Status, Optional["AfcController"]]:
        status = validate_config(config)
        if status is not Status.OK:
            return status, None
        if reference is None or len(reference) == 0:
            return Status.REJECTED_MISSING, None
        if len(reference) < ASSET_PREFIX:
            return Status.REJECTED_TENSOR, None
        if any(not math.isfinite(float(value)) for value in reference):
            return Status.REJECTED_NONFINITE, None
        if any(abs(float(value)) > float(config["max_abs_reference"])
               for value in reference):
            return Status.REJECTED_INVALID, None
        return Status.OK, cls(config, reference, epoch, first_input_sample)

    def _reject(self, status: Status) -> ProcessResult:
        self.state.invalid_count += 1
        return ProcessResult(status)

    def process(self, frame: Sequence[float], epoch: Optional[int] = None,
                first_input_sample: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if len(frame) != FRAME_SAMPLES:
            return self._reject(Status.REJECTED_TENSOR)
        values = [float(value) for value in frame]
        if any(not math.isfinite(value) for value in values):
            return self._reject(Status.REJECTED_NONFINITE)
        if any(abs(value) > float(self.config["max_abs_input"]) for value in values):
            return self._reject(Status.REJECTED_INVALID)
        if epoch is not None and epoch != state.epoch:
            return self._reject(Status.REJECTED_EPOCH)
        if (first_input_sample is not None
                and first_input_sample != state.next_input_sample):
            return self._reject(Status.REJECTED_POSITION)

        latency = int(self.config["reference_latency_samples"])
        work = state.copy()
        first = state.next_input_sample
        base = first + REFERENCE_OFFSET - latency
        if base < 0 or base + FRAME_SAMPLES - 1 >= len(self.reference):
            return self._reject(Status.REJECTED_POSITION)

        residual: List[float] = []
        residual_power = 0.0
        mic_power = 0.0
        ref_energy = 0.0
        cross_energy = 0.0
        weights = work.weights
        reference = self.reference
        profile = self.config["profile"]
        adaptive = profile in ("afc", "afc_margin")
        double_talk = False
        if adaptive:
            for n in range(FRAME_SAMPLES):
                position = base + n
                acc = 0.0
                for k in range(TAPS):
                    acc += weights[k] * reference[position - k]
                error = values[n] - acc
                residual.append(error)
                residual_power += error * error
                mic_power += values[n] * values[n]
                ref_energy += reference[position] * reference[position]
                cross_energy += values[n] * reference[position]
            residual_power /= FRAME_SAMPLES
            mic_power /= FRAME_SAMPLES
            ref_energy /= FRAME_SAMPLES
            cross_energy /= FRAME_SAMPLES
            denominator = math.sqrt(max(mic_power * ref_energy, 1e-30))
            coherence = (cross_energy / denominator) ** 2
            quiet_reference = ref_energy < float(
                self.config["min_adaptation_power"])
            double_talk = (mic_power > float(self.config["double_talk_abs"])
                           and coherence < float(
                               self.config["double_talk_coherence"]))
            if double_talk or quiet_reference:
                new_mode = "double_talk" if double_talk else "quiet_reference"
                if double_talk:
                    work.double_talk_frames += 1
                if state.mode != new_mode:
                    work.transitions.append(
                        "%s->%s@%d" % (state.mode, new_mode, work.frames))
                work.mode = new_mode
            else:
                # Block-NLMS normalization with an explicit factor for the
                # correlation of synthetic speech (the pin prevents an
                # unbounded step on highly correlated reference material).
                mu = float(self.config["step_size"]) / (
                    float(self.config["normalization_factor"]) * ref_energy
                    * FRAME_SAMPLES + float(self.config["epsilon"]))
                correlation = [0.0] * TAPS
                for n in range(FRAME_SAMPLES):
                    error = residual[n]
                    position = base + n
                    for k in range(TAPS):
                        correlation[k] += error * reference[position - k]
                leakage = float(self.config["leakage"])
                for k in range(TAPS):
                    updated = leakage * weights[k] + mu * correlation[k]
                    if not math.isfinite(updated) or abs(updated) > 16.0:
                        return self._reject(Status.REJECTED_NONFINITE)
                    weights[k] = updated
                work.adapted_frames += 1
                new_mode = "converged" if work.frames >= 8 else "tracking"
                if work.mode != new_mode:
                    work.transitions.append(
                        "%s->%s@%d" % (work.mode, new_mode, work.frames))
                work.mode = new_mode
        else:
            residual = list(values)
            mic_power = sum(value * value for value in values) / FRAME_SAMPLES
            residual_power = mic_power
            work.mode = "passthrough"

        gain_db = 0.0
        if profile == "afc_margin":
            gain_db = float(self.config["margin_db"])
        elif profile == "fixed_margin":
            gain_db = float(self.config["fixed_margin_db"])
        gain = 10.0 ** (gain_db / 20.0)

        output: List[float] = []
        ceiling = float(self.config["output_ceiling"])
        for value in residual:
            sample = value * gain
            if not math.isfinite(sample) or abs(sample) > ceiling:
                return self._reject(Status.REJECTED_NONFINITE)
            output.append(sample)

        work.frames += 1
        work.next_input_sample += FRAME_SAMPLES
        self.state = work
        return ProcessResult(Status.OK, tuple(output), residual_power,
                             mic_power, adaptive and not double_talk,
                             work.digest())

    def process_stream(self, samples: Sequence[float]) -> Tuple[Status, Tuple[float, ...]]:
        if len(samples) % FRAME_SAMPLES:
            return Status.REJECTED_TENSOR, ()
        chunks: List[float] = []
        for offset in range(0, len(samples), FRAME_SAMPLES):
            result = self.process(samples[offset:offset + FRAME_SAMPLES])
            if result.status is not Status.OK:
                return result.status, ()
            chunks.extend(result.samples)
        return Status.OK, tuple(chunks)

    def reset(self, epoch: Optional[int] = None,
              first_input_sample: int = 0) -> Status:
        if self.state.closed:
            return Status.CLOSED
        self.state = AfcState(
            epoch=self.state.epoch if epoch is None else epoch,
            next_input_sample=first_input_sample)
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    def append_playback(self, playback: Sequence[float]) -> None:
        """Write actual playback into its frame slot in the reference array.

        The asset prefix reserves the alignment lead; slots beyond the initially
        pinned asset are zero-filled on demand. Overwriting is intentional: the
        simulation generates the playback itself, frame by frame.
        """
        if len(playback) != FRAME_SAMPLES:
            raise ValueError(Status.REJECTED_TENSOR.value)
        start = ASSET_PREFIX + self.playback_cursor
        required = start + FRAME_SAMPLES
        if required > len(self.reference):
            self.reference.extend([0.0] * (required - len(self.reference)))
        self.reference[start:required] = [float(value) for value in playback]
        self.playback_cursor += FRAME_SAMPLES


def _lcg(seed: int) -> Iterable[float]:
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def tone(frames: int, frequency_hz: float = 1000.0, amplitude: float = 0.09,
         seed: int = 7) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(amplitude * math.sin(
        2.0 * math.pi * frequency_hz * n / SAMPLE_RATE_HZ) + 0.0005 * next(noise)
        for n in range(frames * FRAME_SAMPLES))


def chirp(frames: int, start_hz: float = 200.0, end_hz: float = 4000.0,
          amplitude: float = 0.09) -> Tuple[float, ...]:
    values: List[float] = []
    phase = 0.0
    total = frames * FRAME_SAMPLES
    for index in range(total):
        frequency = start_hz + (end_hz - start_hz) * index / max(total - 1, 1)
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def speech_like(frames: int, seed: int = 20261028) -> Tuple[float, ...]:
    """Clean synthetic voiced/unvoiced, paused program; not a recording."""
    noise = _lcg(seed)
    samples: List[float] = []
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.3 * time_s - 0.6)
        pause = 0.0 if (index // FRAME_SAMPLES) % 37 in (34, 35, 36) else 1.0
        envelope = (0.04 + 0.20 * syllable ** 2) * pause
        f0 = 105.0 + 28.0 * math.sin(2.0 * math.pi * 0.37 * time_s)
        drive = (1.0 if index % int(round(SAMPLE_RATE_HZ / f0)) == 0 else 0.0)
        drive += 0.035 * next(noise)
        formant_a[0], formant_a[1] = (
            0.972 * formant_a[0] - 0.018 * formant_a[1] + drive, formant_a[0])
        formant_b[0], formant_b[1] = (
            0.947 * formant_b[0] - 0.035 * formant_b[1] + drive, formant_b[0])
        samples.append(max(-0.95, min(0.95,
            envelope * (0.45 * formant_a[0] + 0.18 * formant_b[0]))))
    return tuple(samples)


def impulse(frames: int = 8) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = 0.5
    return tuple(values)


def step(frames: int = 12, onset_frame: int = 4) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[onset_frame * FRAME_SAMPLES:] = [0.25] * (
        len(values) - onset_frame * FRAME_SAMPLES)
    return tuple(values)


def make_asset(playback: Sequence[float],
               advance: int = 0) -> Tuple[float, ...]:
    """Reference asset: alignment prefix zeros followed by actual playback.

    ``advance`` shifts the playback earlier inside the asset to model a
    reference clock that leads the nominal playback. It is only used by the
    offline adaptation sweep; a leading reference is not causal in a live v0
    streaming loop.
    """
    if advance < 0 or advance > MAX_LATENCY_SAMPLES:
        raise ValueError(Status.REJECTED_INVALID.value)
    return tuple([0.0] * (ASSET_PREFIX - advance)) + tuple(playback)


def zeros_reference(frames: int) -> Tuple[float, ...]:
    """A pinned silent reference long enough for ``frames`` processed frames."""
    return make_asset((0.0,) * (frames * FRAME_SAMPLES))


def frames_to_threshold(values: Sequence[float], threshold: float,
                        window: int = 5) -> Any:
    """First frame whose trailing mean reaches a threshold, or an explicit miss."""
    for index in range(len(values)):
        chunk = values[max(0, index - window + 1):index + 1]
        if sum(chunk) / len(chunk) >= threshold:
            return index
    return "not_reached_within_%d_frames" % len(values)


def convolve_path(signal: Sequence[float], taps: Sequence[float],
                  delay: int) -> Tuple[float, ...]:
    result = [0.0] * len(signal)
    for n in range(delay, len(signal)):
        total = 0.0
        for k, coefficient in enumerate(taps):
            if n - delay - k >= 0:
                total += coefficient * signal[n - delay - k]
        result[n] = total
    return tuple(result)


def rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(len(values), 1))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def frames_of(values: Sequence[float]) -> List[Tuple[float, ...]]:
    return [tuple(values[index:index + FRAME_SAMPLES])
            for index in range(0, len(values), FRAME_SAMPLES)]


def sdr_db(target: Sequence[float], output: Sequence[float]) -> float:
    error = [right - left for left, right in zip(target, output)]
    return 20.0 * math.log10(max(rms(target), 1e-30) / max(rms(error), 1e-30))


def erle_db(mic: Sequence[float], residual: Sequence[float]) -> float:
    return 20.0 * math.log10(max(rms(mic), 1e-30) / max(rms(residual), 1e-30))


def _r6(value: float) -> float:
    return round(value, 6)


def echo_only_run(playback: Sequence[float], path: Sequence[float],
                  config: Optional[Dict[str, Any]] = None,
                  frames: Optional[int] = None,
                  path_change_at: Optional[int] = None,
                  changed_path: Optional[Sequence[float]] = None,
                  near_end: Optional[Sequence[float]] = None,
                  asset_advance: int = 0) -> Dict[str, Any]:
    """Frame-causal echo path with optional near-end speech or path change."""
    count = frames or len(playback) // FRAME_SAMPLES
    effective = convolve_path(playback, path, LOOP_DELAY_SAMPLES)
    near = tuple(near_end or (0.0,) * (count * FRAME_SAMPLES))
    mic = tuple(left + right for left, right in zip(
        effective[:count * FRAME_SAMPLES],
        near[:count * FRAME_SAMPLES]))
    asset = make_asset(playback[:count * FRAME_SAMPLES], advance=asset_advance)
    cfg = config or config_with()
    controller = AfcController(cfg, asset)
    outputs: List[float] = []
    erle_by_frame: List[float] = []
    mode_by_frame: List[str] = []
    for index, frame in enumerate(frames_of(mic)):
        if (path_change_at is not None and index == path_change_at
                and changed_path is not None):
            changed = convolve_path(playback[:count * FRAME_SAMPLES],
                                    changed_path, LOOP_DELAY_SAMPLES)
            mic = tuple(left + right for left, right in zip(
                changed[:count * FRAME_SAMPLES], near[:count * FRAME_SAMPLES]))
            frame = frames_of(mic)[index]
        result = controller.process(frame, first_input_sample=index * FRAME_SAMPLES)
        if result.status is not Status.OK:
            raise RuntimeError("echo_only_run failed: %s" % result.status.value)
        outputs.extend(result.samples)
        erle_by_frame.append(erle_db(frame, result.samples))
        mode_by_frame.append(controller.state.mode)
    return {
        "status": "ok",
        "erle_by_frame": [_r6(value) for value in erle_by_frame],
        "modes": mode_by_frame,
        "output": tuple(outputs),
        "mic": mic,
        "transitions": list(controller.state.transitions),
        "final_weights_digest": object_digest(
            [round(value, 12) for value in controller.state.weights]),
        "adapted_frames": controller.state.adapted_frames,
        "double_talk_frames": controller.state.double_talk_frames,
        "near_end_sdr_db": _r6(sdr_db(
            near[:count * FRAME_SAMPLES], tuple(outputs)))
            if any(abs(value) > 1e-12 for value in near) else 0.0,
        "ref_energy_out_of_range_frames": 0,
    }


def closed_loop(controller: AfcController, program: Sequence[float],
                loop_gain: float, path: Sequence[float],
                nonlinearity: str = "linear",
                saturation: float = 0.8,
                speech_frames: int = 120,
                tail_frames: int = 80) -> Dict[str, Any]:
    """Recursive loop: processed playback is actually returned to the mic."""
    total_frames = speech_frames + tail_frames
    history = [0.0] * (LOOP_DELAY_SAMPLES + len(path) + FRAME_SAMPLES)
    output: List[float] = []
    mic_all: List[float] = []
    rejected = 0
    nonfinite = 0
    clipped = 0
    for frame_index in range(total_frames):
        source = program[frame_index * FRAME_SAMPLES:
                         (frame_index + 1) * FRAME_SAMPLES]
        source = tuple(source) + (0.0,) * (FRAME_SAMPLES - len(source))
        mic_frame: List[float] = []
        for n in range(FRAME_SAMPLES):
            absolute = frame_index * FRAME_SAMPLES + n
            # history[k] is playback[absolute - LOOP_DELAY_SAMPLES - k].
            feedback = 0.0
            for k, coefficient in enumerate(path):
                index = LOOP_DELAY_SAMPLES + k - n
                if 0 <= index < len(history):
                    feedback += coefficient * history[index]
            value = source[n] + loop_gain * feedback
            if nonlinearity == "pre_tanh":
                value = saturation * math.tanh(value / saturation)
            mic_frame.append(value)
        result = controller.process(
            tuple(mic_frame), first_input_sample=frame_index * FRAME_SAMPLES)
        if result.status is not Status.OK:
            rejected += 1
            playback = (0.0,) * FRAME_SAMPLES
        else:
            playback = result.samples
        if nonlinearity == "post_clip":
            playback = tuple(max(-saturation, min(saturation, value))
                             for value in playback)
            clipped += sum(1 for value in playback
                           if abs(value) >= saturation - 1e-12)
        output.extend(playback)
        mic_all.extend(mic_frame)
        nonfinite += sum(1 for value in playback if not math.isfinite(value))
        history_length = len(history)
        history = [playback[FRAME_SAMPLES - 1 - index]
                   for index in range(FRAME_SAMPLES)] + history[
                       :history_length - FRAME_SAMPLES]
        controller.append_playback(playback)

    tail = output[-tail_frames * FRAME_SAMPLES:]
    speech_out = output[:speech_frames * FRAME_SAMPLES]
    speech_target = program[:speech_frames * FRAME_SAMPLES]
    program_rms = rms(speech_target)
    tail_db = 20.0 * math.log10(max(rms(tail), 1e-30) / max(program_rms, 1e-30))
    if rejected:
        stability = "rejected_frames_fail_closed"
    elif tail_db > -10.0:
        stability = "sustained_feedback"
    elif tail_db > -30.0:
        stability = "decaying"
    else:
        stability = "decayed"
    return {
        "control": controller.config["profile"],
        "loop_gain": loop_gain,
        "nonlinearity": nonlinearity,
        "status": "ok",
        "stability_class": stability,
        "tail_db_relative_to_program": _r6(tail_db),
        "program_sdr_db": _r6(sdr_db(speech_target, speech_out)),
        "peak_abs_output": _r6(peak(output)),
        "nonfinite_output_samples": nonfinite,
        "rejected_frames": rejected,
        "clipped_samples": clipped,
        "adapted_frames": controller.state.adapted_frames,
        "double_talk_frames": controller.state.double_talk_frames,
        "output_digest": tensor_digest(output),
        "mic_digest": tensor_digest(mic_all),
    }


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print("use tools/evaluate.py to regenerate the canonical report")
