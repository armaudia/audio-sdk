"""Deterministic synthetic DSP reference for notch plus bounded gain margin.

SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN. This module is a task-local, model-free
reference only. It fixes the installed v0 format (16 kHz, mono, f32, 160
samples) and exercises that format exclusively. No SDK header, descriptor,
registry, default, installed behaviour or shared build file is changed here.

Every stimulus is generated analytically or by a seeded LCG. No recording,
model, download, device or benchmark bundle is read or produced. The closed
loop is recursive: the processed output is returned through a simulated
loudspeaker-to-microphone path, so open-loop tone overlays are never treated as
stability evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CONTRACT_ID = "audio-sdk/adaptive-notch-with-gain-margin/0.1"
TASK_ID = "SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"

MIN_HZ = 200
MAX_HZ = 4000
STEP_HZ = 100
FREQUENCIES_HZ: Tuple[int, ...] = tuple(range(MIN_HZ, MAX_HZ + 1, STEP_HZ))
MAX_NOTCHES_ALLOWED = 4
PROVIDER_ID = "dsp.adaptive-notch-margin.marginref.v0"

# Pinned external evidence. The board is mutable shared state and is recorded
# as a read-time snapshot only; it never qualifies or disqualifies a result.
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
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "5eea8b61fa70c0e3669ceb878aefc96e9005204f97f1970879583bc710689e80",
    "mutable": True,
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "profile": "notch_plus_margin",
    "min_hz": MIN_HZ,
    "max_hz": MAX_HZ,
    "step_hz": STEP_HZ,
    "prominence_db": 10.0,
    "absolute_dbfs": -38.0,
    "persistence_frames": 4,
    "release_frames": 24,
    "cooldown_frames": 60,
    "max_notches": 2,
    "q": 24.0,
    "margin_step_db": 3.0,
    "margin_floor_db": -12.0,
    "recovery_frames": 200,
    "recovery_step_db": 0.1,
    "fixed_gain_db": -5.0,
    "max_abs_input": 4.0,
    "saturation": "none",
    "saturation_threshold": 0.8,
}

PROFILES = ("notch_plus_margin", "notch_only", "fixed_gain", "identity")
REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES = {
    "prominence_db": (6.0, 30.0),
    "absolute_dbfs": (-80.0, -10.0),
    "persistence_frames": (1, 16),
    "release_frames": (1, 400),
    "cooldown_frames": (0, 400),
    "max_notches": (1, MAX_NOTCHES_ALLOWED),
    "q": (4.0, 40.0),
    "margin_step_db": (0.5, 12.0),
    "margin_floor_db": (-24.0, 0.0),
    "recovery_frames": (1, 2000),
    "recovery_step_db": (0.01, 1.0),
    "fixed_gain_db": (-24.0, 0.0),
    "max_abs_input": (0.25, 16.0),
    "saturation_threshold": (0.1, 4.0),
}
_INTEGER_KEYS = ("persistence_frames", "release_frames", "cooldown_frames",
                 "max_notches", "recovery_frames")


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


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    """Fail closed on missing, malformed, nonfinite or out-of-range controls."""
    if config is None:
        return Status.REJECTED_MISSING
    if not isinstance(config, dict):
        return Status.REJECTED_INVALID
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        return Status.REJECTED_MISSING
    unknown = sorted(key for key in config if key not in REQUIRED_KEYS)
    if unknown:
        return Status.REJECTED_INVALID
    if config["profile"] not in PROFILES:
        return Status.REJECTED_INVALID
    if (config["min_hz"] != MIN_HZ or config["max_hz"] != MAX_HZ
            or config["step_hz"] != STEP_HZ):
        return Status.REJECTED_INVALID
    if config["saturation"] not in ("none", "tanh"):
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
        if int(config[key]) != config[key]:
            return Status.REJECTED_INVALID
    if float(config["margin_floor_db"]) > 0.0 or float(config["margin_step_db"]) < 0.0:
        return Status.REJECTED_INVALID
    if float(config["fixed_gain_db"]) > 0.0:
        return Status.REJECTED_INVALID
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


def _window() -> Tuple[float, ...]:
    return tuple(0.5 - 0.5 * math.cos(2.0 * math.pi * n / (FRAME_SAMPLES - 1))
                 for n in range(FRAME_SAMPLES))


WINDOW = _window()
WINDOW_POWER = sum(value * value for value in WINDOW)
_TONE_TABLES = {
    frequency: tuple(
        (math.cos(2.0 * math.pi * frequency * n / SAMPLE_RATE_HZ),
         math.sin(2.0 * math.pi * frequency * n / SAMPLE_RATE_HZ))
        for n in range(FRAME_SAMPLES))
    for frequency in FREQUENCIES_HZ
}


def tone_power(values: Sequence[float], frequency_hz: int) -> float:
    """Mean normalized power at one pinned frequency over whole 160-sample blocks."""
    tables = _TONE_TABLES[frequency_hz]
    total = 0.0
    blocks = 0
    for start in range(0, len(values), FRAME_SAMPLES):
        block = values[start:start + FRAME_SAMPLES]
        if len(block) < FRAME_SAMPLES:
            block = tuple(block) + (0.0,) * (FRAME_SAMPLES - len(block))
        real = sum(value * pair[0] for value, pair in zip(block, tables))
        imag = sum(value * pair[1] for value, pair in zip(block, tables))
        total += (real * real + imag * imag) / (WINDOW_POWER * WINDOW_POWER)
        blocks += 1
    return total / max(blocks, 1)


def _db(power: float) -> float:
    return 10.0 * math.log10(max(power, 1e-30))


@dataclass
class NotchState:
    frequency_hz: int
    bin_index: int
    miss_frames: int = 0
    z1: float = 0.0
    z2: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {"frequency_hz": self.frequency_hz, "bin_index": self.bin_index,
                "miss_frames": self.miss_frames, "z1": self.z1, "z2": self.z2}


@dataclass
class ControllerState:
    epoch: int = 7
    next_input_sample: int = 0
    runs: Dict[int, int] = field(default_factory=dict)
    cooldowns: Dict[int, int] = field(default_factory=dict)
    notches: List[NotchState] = field(default_factory=list)
    gain_db: float = 0.0
    margin_min_db: float = 0.0
    frames_since_detection: int = 0
    frames_processed: int = 0
    activation_count: int = 0
    release_count: int = 0
    margin_reduction_events: int = 0
    margin_recoveries: int = 0
    active_frames: int = 0
    invalid_count: int = 0
    rejected_nonfinite_frames: int = 0
    transitions: List[str] = field(default_factory=list)
    closed: bool = False

    def copy(self) -> "ControllerState":
        return ControllerState(
            epoch=self.epoch, next_input_sample=self.next_input_sample,
            runs=dict(self.runs), cooldowns=dict(self.cooldowns),
            notches=[replace(notch) for notch in self.notches],
            gain_db=self.gain_db,
            margin_min_db=self.margin_min_db,
            frames_since_detection=self.frames_since_detection,
            frames_processed=self.frames_processed,
            activation_count=self.activation_count,
            release_count=self.release_count,
            margin_reduction_events=self.margin_reduction_events,
            margin_recoveries=self.margin_recoveries,
            active_frames=self.active_frames,
            invalid_count=self.invalid_count,
            rejected_nonfinite_frames=self.rejected_nonfinite_frames,
            transitions=list(self.transitions), closed=self.closed)

    def digest(self) -> str:
        return object_digest({
            "epoch": self.epoch,
            "next_input_sample": self.next_input_sample,
            "notches": [notch.as_dict() for notch in self.notches],
            "gain_db": self.gain_db,
            "margin_min_db": self.margin_min_db,
            "frames_processed": self.frames_processed,
            "activation_count": self.activation_count,
            "release_count": self.release_count,
            "margin_reduction_events": self.margin_reduction_events,
        })


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    detected_hz: Tuple[int, ...] = ()
    active_hz: Tuple[int, ...] = ()
    gain_db: float = 0.0
    state_digest: str = ""


class MarginController:
    """Optional reference: tone detector -> narrow notches -> bounded margin."""

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 epoch: int = 7, first_input_sample: int = 0) -> None:
        status = validate_config(config)
        if status is not Status.OK:
            raise ValueError(status.value)
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
            raise ValueError("invalid_epoch")
        if not isinstance(first_input_sample, int) or isinstance(first_input_sample, bool):
            raise ValueError("invalid_first_input_sample")
        self.config = dict(config or DEFAULT_CONFIG)
        self.state = ControllerState(epoch=epoch,
                                     next_input_sample=first_input_sample)

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]]) -> Tuple[Status, Optional["MarginController"]]:
        status = validate_config(config)
        if status is not Status.OK:
            return status, None
        return Status.OK, cls(config)

    @staticmethod
    def _coefficients(frequency_hz: float, quality: float
                      ) -> Tuple[float, float, float, float, float]:
        omega = 2.0 * math.pi * frequency_hz / SAMPLE_RATE_HZ
        cosine = math.cos(omega)
        alpha = math.sin(omega) / (2.0 * quality)
        a0 = 1.0 + alpha
        return (1.0 / a0, -2.0 * cosine / a0, 1.0 / a0,
                -2.0 * cosine / a0, (1.0 - alpha) / a0)

    def _spectrum_db(self, samples: Sequence[float]) -> List[float]:
        return [_db(tone_power(samples, frequency)) for frequency in FREQUENCIES_HZ]

    def _reject(self, status: Status, *, nonfinite: bool = False) -> ProcessResult:
        self.state.invalid_count += 1
        if nonfinite:
            self.state.rejected_nonfinite_frames += 1
        return ProcessResult(status)

    def process(self, frame: Sequence[float], epoch: Optional[int] = None,
                first_input_sample: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if len(frame) != FRAME_SAMPLES:
            return self._reject(Status.REJECTED_TENSOR)
        try:
            values = [float(value) for value in frame]
        except (TypeError, ValueError, OverflowError):
            return self._reject(Status.REJECTED_NONFINITE, nonfinite=True)
        if any(not math.isfinite(value) for value in values):
            return self._reject(Status.REJECTED_NONFINITE, nonfinite=True)
        if any(abs(value) > float(self.config["max_abs_input"]) for value in values):
            return self._reject(Status.REJECTED_INVALID)
        if epoch is not None and epoch != state.epoch:
            return self._reject(Status.REJECTED_EPOCH)
        if (first_input_sample is not None
                and first_input_sample != state.next_input_sample):
            return self._reject(Status.REJECTED_POSITION)

        work = state.copy()
        detected: List[Tuple[int, float]] = []
        levels: List[float] = []
        detecting = self.config["profile"] in ("notch_plus_margin", "notch_only")
        if detecting:
            levels = self._spectrum_db(values)
            for index, level in enumerate(levels):
                left = levels[index - 1] if index > 0 else -300.0
                right = levels[index + 1] if index + 1 < len(levels) else -300.0
                prominent = level - max(left, right) >= float(self.config["prominence_db"])
                if prominent and level >= float(self.config["absolute_dbfs"]):
                    run = work.runs.get(index, 0) + 1
                    work.runs[index] = run
                    if run >= int(self.config["persistence_frames"]):
                        detected.append((index, level))
                else:
                    work.runs[index] = 0

        if detecting and (detected or work.notches):
            work.frames_since_detection = 0
        else:
            work.frames_since_detection += 1

        released: List[int] = []
        kept: List[NotchState] = []
        for notch in work.notches:
            present = any(index == notch.bin_index for index, _ in detected)
            miss = 0 if present else notch.miss_frames + 1
            if miss >= int(self.config["release_frames"]):
                released.append(notch.frequency_hz)
                work.cooldowns[notch.bin_index] = int(self.config["cooldown_frames"])
                continue
            kept.append(replace(notch, miss_frames=miss))
        work.notches = kept
        if released:
            work.release_count += len(released)
            work.transitions.append(
                "active->idle@%d:%s" % (work.frames_processed,
                                        ",".join(str(value) for value in released)))

        for index in list(work.cooldowns):
            work.cooldowns[index] -= 1
            if work.cooldowns[index] <= 0:
                del work.cooldowns[index]

        if detecting:
            ranked = sorted(detected, key=lambda item: (-item[1], item[0]))
            for index, _ in ranked:
                if len(work.notches) >= int(self.config["max_notches"]):
                    break
                if index in work.cooldowns or any(
                        notch.bin_index == index for notch in work.notches):
                    continue
                work.notches.append(NotchState(FREQUENCIES_HZ[index], index))
                work.activation_count += 1
                work.transitions.append(
                    "idle->active@%d:%d" % (work.frames_processed, FREQUENCIES_HZ[index]))

        previous_detected = bool(state.runs) and any(
            run >= int(self.config["persistence_frames"]) for run in state.runs.values())
        newly_detected = bool(detected) and not previous_detected

        gain_db = work.gain_db
        if self.config["profile"] == "fixed_gain":
            gain_db = float(self.config["fixed_gain_db"])
        elif self.config["profile"] == "notch_plus_margin":
            floor = float(self.config["margin_floor_db"])
            step = float(self.config["margin_step_db"])
            if newly_detected or work.activation_count > state.activation_count:
                gain_db = max(floor, gain_db - step)
                if gain_db < state.gain_db:
                    work.margin_reduction_events += 1
            elif (work.frames_since_detection > int(self.config["recovery_frames"])
                  and gain_db < 0.0):
                gain_db = min(0.0, gain_db + float(self.config["recovery_step_db"]))
                if gain_db > state.gain_db:
                    work.margin_recoveries += 1
        else:
            gain_db = 0.0
        work.gain_db = gain_db
        work.margin_min_db = min(work.margin_min_db, gain_db)
        gain = 10.0 ** (gain_db / 20.0)

        output: List[float] = []
        coefficients = [self._coefficients(notch.frequency_hz, float(self.config["q"]))
                        for notch in work.notches]
        # Carry biquad state across frames from the last accepted frame.
        for notch in work.notches:
            for previous in state.notches:
                if previous.frequency_hz == notch.frequency_hz:
                    notch.z1, notch.z2 = previous.z1, previous.z2
                    break
        for sample in values:
            filtered = sample
            for notch_index, notch in enumerate(work.notches):
                b0, b1, b2, a1, a2 = coefficients[notch_index]
                y = b0 * filtered + notch.z1
                notch.z1 = b1 * filtered - a1 * y + notch.z2
                notch.z2 = b2 * filtered - a2 * y
                filtered = y
            if self.config["saturation"] == "tanh":
                threshold = float(self.config["saturation_threshold"])
                filtered = threshold * math.tanh(filtered / threshold)
            result_sample = filtered * gain
            if not math.isfinite(result_sample) or abs(result_sample) > 16.0:
                return self._reject(Status.REJECTED_NONFINITE, nonfinite=True)
            output.append(result_sample)

        if detecting and (detected or work.notches):
            work.active_frames += 1
        work.frames_processed += 1
        work.next_input_sample += FRAME_SAMPLES
        self.state = work
        return ProcessResult(Status.OK, tuple(output),
                             tuple(FREQUENCIES_HZ[index] for index, _ in detected),
                             tuple(notch.frequency_hz for notch in work.notches),
                             gain_db, work.digest())

    def process_stream(self, samples: Sequence[float], epoch: int = 7,
                       first_input_sample: int = 0
                       ) -> Tuple[Status, Tuple[float, ...]]:
        if len(samples) % FRAME_SAMPLES:
            return Status.REJECTED_TENSOR, ()
        chunks: List[float] = []
        for offset in range(0, len(samples), FRAME_SAMPLES):
            result = self.process(
                samples[offset:offset + FRAME_SAMPLES],
                epoch=epoch, first_input_sample=first_input_sample + offset)
            if result.status is not Status.OK:
                return result.status, ()
            chunks.extend(result.samples)
        return Status.OK, tuple(chunks)

    def reset(self, epoch: Optional[int] = None,
              first_input_sample: int = 0) -> Status:
        if self.state.closed:
            return Status.CLOSED
        self.state = ControllerState(
            epoch=self.state.epoch if epoch is None else epoch,
            next_input_sample=first_input_sample)
        return Status.OK

    def close(self) -> None:
        self.state.closed = True


def _lcg(seed: int) -> Iterable[float]:
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def tone(frames: int, frequency_hz: int = 1000, amplitude: float = 0.09,
         seed: int = 7) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(amplitude * math.sin(2.0 * math.pi * frequency_hz * n / SAMPLE_RATE_HZ)
                 + 0.0005 * next(noise)
                 for n in range(frames * FRAME_SAMPLES))


def chirp(frames: int, start_hz: int = 200, end_hz: int = 4000,
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
    """Synthetic voiced/unvoiced, paused, clean program material; not a recording."""
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


def tonal_vowel(frames: int = 300, seed: int = 5150) -> Tuple[float, ...]:
    """Synthetic voiced stress with a sustained 1 kHz harmonic."""
    noise = _lcg(seed)
    samples: List[float] = []
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        f0 = 200.0 + 9.0 * math.sin(2.0 * math.pi * 0.23 * time_s)
        envelope = 0.18 * (0.65 + 0.35 * math.sin(2.0 * math.pi * 1.7 * time_s) ** 2)
        harmonic = sum((0.30 / order) * math.sin(
            2.0 * math.pi * f0 * order * time_s + 0.4 * order)
            for order in range(1, 9))
        samples.append(envelope * harmonic + 0.002 * next(noise))
    return tuple(samples)


def impulse(frames: int = 8) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = 0.5
    return tuple(values)


def step(frames: int = 12, onset_frame: int = 4) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[onset_frame * FRAME_SAMPLES:] = [0.25] * (len(values) - onset_frame * FRAME_SAMPLES)
    return tuple(values)


def rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(len(values), 1))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def frames_of(values: Sequence[float]) -> List[Tuple[float, ...]]:
    return [tuple(values[index:index + FRAME_SAMPLES])
            for index in range(0, len(values), FRAME_SAMPLES)]


def _sdr_db(target: Sequence[float], output: Sequence[float]) -> float:
    error = [right - left for left, right in zip(target, output)]
    return 20.0 * math.log10(max(rms(target), 1e-30) / max(rms(error), 1e-30))


def _tone_to_total_db(values: Sequence[float], frequency_hz: int) -> float:
    total = sum(value * value for value in values) / max(len(values), 1)
    tone_component = tone_power(values, frequency_hz)
    return 10.0 * math.log10(max(tone_component, 1e-30) / max(total, 1e-30))


def closed_loop(controller: MarginController, program: Sequence[float],
                loop_gain: float, path_hz: int = 1000,
                nonlinearity: str = "linear",
                pre_saturation: float = 0.8) -> Dict[str, Any]:
    """Frame-causal recursive loop with a delayed resonant feedback path."""
    omega = 2.0 * math.pi * path_hz / SAMPLE_RATE_HZ
    coefficient = 2.0 * 0.96 * math.cos(omega)
    decay = 0.96 * 0.96
    resonator_a = [0.0, 0.0]
    secondary_a = [0.0, 0.0]
    secondary_omega = 2.0 * math.pi * 2400.0 / SAMPLE_RATE_HZ
    secondary_coefficient = 2.0 * 0.95 * math.cos(secondary_omega)
    secondary_decay = 0.95 * 0.95
    history = [0.0] * FRAME_SAMPLES
    output: List[float] = []
    speech_frames = 200
    speech_rms = rms(program[:speech_frames * FRAME_SAMPLES])
    rejected = 0
    nonfinite = 0
    clipped = 0
    for frame_index, source in enumerate(frames_of(program)):
        mic: List[float] = []
        for sample, feedback_sample in zip(source, history):
            primary = feedback_sample + coefficient * resonator_a[0] - decay * resonator_a[1]
            resonator_a[1], resonator_a[0] = resonator_a[0], primary
            secondary = (feedback_sample + secondary_coefficient * secondary_a[0]
                         - secondary_decay * secondary_a[1])
            secondary_a[1], secondary_a[0] = secondary_a[0], secondary
            dual = path_hz == 1000 and loop_gain == 1.15 and nonlinearity == "dual_paths"
            feedback = loop_gain * 0.04 * (primary + secondary if dual else primary)
            value = sample + feedback
            if nonlinearity == "pre_tanh":
                value = pre_saturation * math.tanh(value / pre_saturation)
            mic.append(value)
        result = controller.process(
            tuple(mic), epoch=7, first_input_sample=frame_index * FRAME_SAMPLES)
        if result.status is not Status.OK:
            rejected += 1
            playback = (0.0,) * FRAME_SAMPLES
        else:
            playback = result.samples
        if nonlinearity == "post_clip":
            playback = tuple(max(-0.8, min(0.8, value)) for value in playback)
            clipped += sum(1 for value in playback if abs(value) >= 0.8)
        output.extend(playback)
        history = list(playback)
        nonfinite += sum(1 for value in playback if not math.isfinite(value))

    tail = output[-100 * FRAME_SAMPLES:]
    speech_out = output[:speech_frames * FRAME_SAMPLES]
    speech_target = program[:speech_frames * FRAME_SAMPLES]
    state = controller.state
    tail_db = 20.0 * math.log10(max(rms(tail), 1e-30) / max(speech_rms, 1e-30))
    if rejected:
        stability_class = "rejected_frames_fail_closed"
    elif tail_db > -10.0:
        stability_class = "sustained_feedback"
    elif tail_db > -30.0:
        stability_class = "decaying"
    else:
        stability_class = "decayed"
    return {
        "control": controller.config["profile"],
        "loop_gain": loop_gain,
        "path_hz": path_hz,
        "nonlinearity": nonlinearity,
        "status": "ok",
        "tail_rms": rms(tail),
        "tail_db_relative_to_program": tail_db,
        "stability_class": stability_class,
        "program_sdr_db": _sdr_db(speech_target, speech_out),
        "peak_abs_output": peak(output),
        "nonfinite_frames": nonfinite,
        "rejected_frames": rejected,
        "clipped_samples": clipped,
        "activations": state.activation_count,
        "releases": state.release_count,
        "margin_reduction_events": state.margin_reduction_events,
        "margin_min_db": state.margin_min_db,
        "margin_final_db": state.gain_db,
        "output_digest": tensor_digest(output),
    }


def build_report() -> Dict[str, Any]:
    """Run every deterministic condition and return the canonical report object."""
    fixture_spec = {
        "contract": CONTRACT_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "frequencies_hz": list(FREQUENCIES_HZ),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "default_config": DEFAULT_CONFIG,
        "seeds": {"speech": 20261028, "tonal_vowel": 5150, "tone": 7},
        "loop": {"feedback_delay_samples": FRAME_SAMPLES,
                 "resonator_decay": 0.96, "feedback_gain": 0.04,
                 "speech_frames": 200, "silence_frames": 100,
                 "pre_saturation": 0.8, "post_clip_ceiling": 0.8},
    }

    # Silence, impulse and step: zero added delay, no activations.
    silence = MarginController(config_with())
    silence_status, silence_output = silence.process_stream((0.0,) * (40 * FRAME_SAMPLES))
    impulse_control = MarginController(config_with())
    impulse_status, impulse_output = impulse_control.process_stream(impulse())
    impulse_peak_index = max(range(len(impulse_output)),
                             key=lambda index: abs(impulse_output[index]))
    step_control = MarginController(config_with())
    step_status, step_output = step_control.process_stream(step())
    onset = 4 * FRAME_SAMPLES
    crossing = next((index - onset for index in range(onset, len(step_output))
                     if abs(step_output[index]) >= 0.025), len(step_output))

    # Gain and frequency response: fixed-gain control plus one fresh controller
    # per frequency for the detector/notch sweep.
    fixed = MarginController(config_with(profile="fixed_gain"))
    fixed_status, fixed_output = fixed.process_stream(tone(40))
    fixed_gain_measured = rms(fixed_output) / rms(tone(40))
    sweep_samples: List[float] = []
    sweep_rows: List[Dict[str, Any]] = []
    for frequency in FREQUENCIES_HZ:
        controller = MarginController(config_with())
        chunk = tone(12, frequency, 0.09, 1000 + frequency)
        status, output = controller.process_stream(chunk)
        if status is not Status.OK:
            raise RuntimeError("sweep failed at %d Hz" % frequency)
        sweep_samples.extend(output)
        sweep_rows.append({
            "frequency_hz": frequency,
            "activated": controller.state.activation_count > 0,
            "active_notches": len(controller.state.notches),
            "steady_gain": round(rms(output[-4 * FRAME_SAMPLES:]) / 0.09, 6),
        })
    chirp_control = MarginController(config_with())
    chirp_status, chirp_output = chirp_control.process_stream(chirp(300))

    # Attack/release and state transitions on a tone burst.
    burst_control = MarginController(config_with())
    burst_source = ((0.0,) * (20 * FRAME_SAMPLES) + tone(100)
                    + (0.0,) * (40 * FRAME_SAMPLES))
    burst_results = [burst_control.process(frame)
                     for frame in frames_of(burst_source)]
    burst_samples = tuple(value for result in burst_results for value in result.samples)
    burst_status = next((result.status for result in burst_results
                         if result.status is not Status.OK), Status.OK)
    active_flags = [bool(result.active_hz) for result in burst_results]
    activated = next((index for index in range(20, 120) if active_flags[index]), None)
    deactivated = next((index for index in range(120, len(active_flags))
                        if not active_flags[index]), None)

    # Clean speech-like material and a tonal-vowel stress case.
    speech = speech_like(300)
    speech_notch_control = MarginController(config_with())
    speech_notch_status, speech_notch_output = speech_notch_control.process_stream(speech)
    speech_margin_control = MarginController(config_with())
    speech_margin_status, speech_margin_output = speech_margin_control.process_stream(speech)
    speech_fixed_control = MarginController(config_with(profile="fixed_gain"))
    speech_fixed_status, speech_fixed_output = speech_fixed_control.process_stream(speech)
    tonal = tonal_vowel()
    tonal_control = MarginController(config_with())
    tonal_status, tonal_output = tonal_control.process_stream(tonal)

    # Tone injected into clean speech: tone reduction versus clean-region damage.
    injection = tuple(
        speech[index] + (0.035 * math.sin(2.0 * math.pi * 1000 * index / SAMPLE_RATE_HZ)
                         if 100 * FRAME_SAMPLES <= index < 200 * FRAME_SAMPLES else 0.0)
        for index in range(len(speech)))
    injection_control = MarginController(config_with())
    injection_status, injection_output = injection_control.process_stream(injection)
    tone_in = injection[100 * FRAME_SAMPLES:200 * FRAME_SAMPLES]
    tone_out = injection_output[100 * FRAME_SAMPLES:200 * FRAME_SAMPLES]
    clean_in = injection[:100 * FRAME_SAMPLES]
    clean_out = injection_output[:100 * FRAME_SAMPLES]
    activation_frames = [int(item.split("@")[1].split(":")[0])
                         for item in injection_control.state.transitions
                         if "->active" in item]

    # Headroom and interacting settings: large input plus in-loop saturation.
    headroom_control = MarginController(config_with(saturation="tanh",
                                                    saturation_threshold=0.8))
    headroom_status, headroom_output = headroom_control.process_stream(
        tone(40, 1000, 3.0, seed=31))

    # Closed-loop comparisons: identical recursive program, paths and delays.
    program = speech_like(200) + (0.0,) * (100 * FRAME_SAMPLES)
    controls = ("identity", "fixed_gain", "notch_only", "notch_plus_margin")
    loop_cases: List[Tuple[float, str]] = [
        (1.05, "linear"), (1.15, "linear"), (1.30, "linear"),
        (1.15, "pre_tanh"), (1.15, "post_clip"), (1.15, "dual_paths"),
    ]
    loop_results: Dict[str, Any] = {}
    for loop_gain, nonlinearity in loop_cases:
        case: Dict[str, Any] = {}
        for control in controls:
            controller = MarginController(config_with(profile=control))
            case[control] = closed_loop(controller, program, loop_gain,
                                        nonlinearity=nonlinearity)
        loop_results["g%s_%s" % (str(loop_gain).replace(".", "_"), nonlinearity)] = case

    # Numerical behaviour, stale session/epoch and invalid settings. All must
    # leave the accepted state byte-for-byte unchanged.
    numerical = MarginController(config_with())
    numerical.process(tone(10)[:FRAME_SAMPLES])
    before = numerical.state.digest()
    statuses = {
        "nonfinite_sample": numerical.process((float("nan"),) * FRAME_SAMPLES).status.value,
        "wrong_shape": numerical.process((0.0,) * 159).status.value,
        "out_of_range_sample": numerical.process((9.0,) * FRAME_SAMPLES).status.value,
        "stale_epoch": numerical.process((0.0,) * FRAME_SAMPLES, epoch=8).status.value,
        "wrong_position": numerical.process((0.0,) * FRAME_SAMPLES,
                                            first_input_sample=999).status.value,
    }
    state_unchanged = numerical.state.digest() == before
    config_statuses = {
        "missing": validate_config(None).value,
        "wrong_type": validate_config(config_with(q="24")).value,
        "nonfinite": validate_config(config_with(q=float("inf"))).value,
        "out_of_range": validate_config(config_with(q=1.0)).value,
        "unknown_key": validate_config(config_with(unexpected=1)).value,
        "stale_profile": validate_config(config_with(profile="legacy")).value,
    }
    reset_control = MarginController(config_with())
    reset_control.process_stream(tone(10)[:10 * FRAME_SAMPLES])
    after_work = reset_control.state.digest()
    reset_status = reset_control.reset(epoch=8, first_input_sample=400)
    after_reset = reset_control.state.digest()
    reset_control.close()
    closed_status = reset_control.process((0.0,) * FRAME_SAMPLES).status.value
    independent = MarginController(config_with())
    independent_digest = independent.state.digest()

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/adaptive-notch-margin-report/0.1",
        "contract": CONTRACT_ID,
        "task": TASK_ID,
        "scope": "synthetic model-free DSP; no real audio, device, model or release claim",
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "config": DEFAULT_CONFIG,
        "results": {
            "silence": {
                "status": silence_status.value,
                "activations": silence.state.activation_count,
                "peak_abs_output": peak(silence_output),
                "output_digest": tensor_digest(silence_output),
            },
            "impulse": {
                "status": impulse_status.value,
                "peak_index": impulse_peak_index,
                "peak_abs_output": peak(impulse_output),
                "added_delay_samples": impulse_peak_index,
                "output_digest": tensor_digest(impulse_output),
            },
            "step": {
                "status": step_status.value,
                "crossing_samples": crossing,
                "peak_abs_output": peak(step_output),
                "output_digest": tensor_digest(step_output),
            },
            "gain_response": {
                "status": fixed_status.value,
                "control": "fixed_gain",
                "configured_gain_db": DEFAULT_CONFIG["fixed_gain_db"],
                "configured_linear_gain": 10.0 ** (DEFAULT_CONFIG["fixed_gain_db"] / 20.0),
                "measured_linear_gain": fixed_gain_measured,
                "output_digest": tensor_digest(fixed_output),
            },
            "sweep": {
                "status": "ok",
                "frames_per_frequency": 12,
                "activated_frequencies": sum(1 for row in sweep_rows if row["activated"]),
                "min_gain": min(row["steady_gain"] for row in sweep_rows),
                "max_gain": max(row["steady_gain"] for row in sweep_rows),
                "per_frequency": sweep_rows,
                "output_digest": tensor_digest(sweep_samples),
            },
            "chirp_sweep": {
                "status": chirp_status.value,
                "frames": 300,
                "activations": chirp_control.state.activation_count,
                "transitions": chirp_control.state.transitions[:8],
                "output_digest": tensor_digest(chirp_output),
            },
            "attack_release": {
                "status": burst_status.value,
                "tone_start_frame": 20,
                "tone_end_frame": 120,
                "activation_frame": activated,
                "attack_frames": None if activated is None else activated - 20,
                "release_frame": deactivated,
                "release_frames": None if deactivated is None else deactivated - 120,
                "activations": burst_control.state.activation_count,
                "releases": burst_control.state.release_count,
                "margin_reduction_events": burst_control.state.margin_reduction_events,
                "margin_min_db": burst_control.state.margin_min_db,
                "transitions": burst_control.state.transitions[:8],
                "output_digest": tensor_digest(burst_samples),
            },
            "clean_speech": {
                "notch_only": {
                    "status": speech_notch_status.value,
                    "frames": 300,
                    "false_activations": speech_notch_control.state.activation_count,
                    "false_activation_rate_per_minute": round(
                        speech_notch_control.state.activation_count * 600.0 / 300.0, 3),
                    "output_digest": tensor_digest(speech_notch_output),
                },
                "notch_plus_margin": {
                    "status": speech_margin_status.value,
                    "frames": 300,
                    "false_activations": speech_margin_control.state.activation_count,
                    "margin_reduction_events":
                        speech_margin_control.state.margin_reduction_events,
                    "output_digest": tensor_digest(speech_margin_output),
                },
                "fixed_gain": {
                    "status": speech_fixed_status.value,
                    "frames": 300,
                    "gain_db": speech_fixed_control.state.gain_db,
                    "output_digest": tensor_digest(speech_fixed_output),
                },
            },
            "tonal_vowel_stress": {
                "status": tonal_status.value,
                "frames": 300,
                "false_activations": tonal_control.state.activation_count,
                "false_activation_rate_per_minute": round(
                    tonal_control.state.activation_count * 600.0 / 300.0, 3),
                "margin_reduction_events": tonal_control.state.margin_reduction_events,
                "margin_min_db": tonal_control.state.margin_min_db,
                "output_digest": tensor_digest(tonal_output),
            },
            "tone_injection": {
                "status": injection_status.value,
                "injected_frequency_hz": 1000,
                "injected_amplitude": 0.035,
                "activations_in_tone_region": sum(
                    1 for frame in activation_frames if 100 <= frame < 200),
                "false_activations_in_clean_region": sum(
                    1 for frame in activation_frames if frame < 100),
                "tone_to_total_db_before": round(_tone_to_total_db(tone_in, 1000), 3),
                "tone_to_total_db_after": round(_tone_to_total_db(tone_out, 1000), 3),
                "tone_power_db_before": round(_db(tone_power(tone_in, 1000)), 3),
                "tone_power_db_after": round(_db(tone_power(tone_out, 1000)), 3),
                "clean_region_tone_db_before": round(_tone_to_total_db(clean_in, 1000), 3),
                "clean_region_tone_db_after": round(_tone_to_total_db(clean_out, 1000), 3),
                "output_digest": tensor_digest(injection_output),
            },
            "headroom_and_nonlinearity": {
                "status": headroom_status.value,
                "input_peak": 3.0,
                "output_peak": peak(headroom_output),
                "headroom_db_to_input_peak": 20.0 * math.log10(
                    max(3.0, 1e-30) / max(peak(headroom_output), 1e-30)),
                "saturation_threshold": 0.8,
                "nonfinite_output_samples": sum(
                    1 for value in headroom_output if not math.isfinite(value)),
                "output_digest": tensor_digest(headroom_output),
            },
            "closed_loop": loop_results,
            "adverse_controls": {
                "frame_statuses": statuses,
                "config_statuses": config_statuses,
                "state_unchanged": state_unchanged,
                "reset_status": reset_status.value,
                "reset_state_digest": after_reset,
                "work_state_digest": after_work,
                "closed_session_status": closed_status,
                "independent_state_digest": independent_digest,
            },
        },
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    text, digest = canonical_report(build_report())
    print(digest)
