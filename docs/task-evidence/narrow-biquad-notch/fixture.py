"""Deterministic synthetic reference for an explicit narrow biquad notch.

This module is model-free and file-free. It fixes the SDK v0 format (16 kHz,
mono f32, 160 samples/frame), designs an RBJ notch from an explicit centre
frequency and bandwidth, and generates every stimulus and metric used by
``test_fixture.py``. No audio file, download, model, device or listening result
is read or claimed.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CONTRACT_ID = "audio-sdk/narrow-biquad-notch/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
MIN_FREQUENCY_HZ = 20.0
MAX_FREQUENCY_HZ = 7800.0
MIN_BANDWIDTH_HZ = 5.0
MAX_BANDWIDTH_HZ = 2000.0
MAX_Q = 2000.0
PROVIDER_ID = "dsp.narrow-notch-reference.v0"

SOURCE_PINS = {
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "frequency_hz": 1000.0,
    "bandwidth_hz": 100.0,
    "q": None,
    "profile": "notch",
    "max_abs_input": 4.0,
    "saturation": "none",
    "saturation_threshold": 1.0,
}
REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
NUMERIC_RANGES = {
    "frequency_hz": (MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ),
    "bandwidth_hz": (MIN_BANDWIDTH_HZ, MAX_BANDWIDTH_HZ),
    "q": (1e-12, MAX_Q),
    "max_abs_input": (0.25, 16.0),
    "saturation_threshold": (0.1, 4.0),
}
CENTER_CONFIGS: Tuple[Tuple[float, float], ...] = (
    (1000.0, 100.0), (120.0, 12.0), (250.0, 25.0), (4000.0, 400.0),
)
SWEEP_FREQUENCIES_HZ: Tuple[int, ...] = tuple(range(100, 7801, 100))


class Status(str, Enum):
    OK = "ok"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_POSITION = "rejected_position"
    REJECTED_STATE = "rejected_state"
    CLOSED = "closed"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(value))
                                   for value in values)).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    """Fail closed on missing, malformed, nonfinite or inconsistent controls."""
    if config is None:
        return Status.REJECTED_MISSING
    if not isinstance(config, dict):
        return Status.REJECTED_INVALID
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        return Status.REJECTED_MISSING
    unknown = sorted(str(key) for key in config if key not in REQUIRED_KEYS)
    if unknown:
        return Status.REJECTED_INVALID
    if config["profile"] not in ("notch", "bypass"):
        return Status.REJECTED_INVALID
    if config["saturation"] not in ("none", "tanh"):
        return Status.REJECTED_INVALID
    for key in ("frequency_hz", "bandwidth_hz", "max_abs_input",
                "saturation_threshold"):
        value = config[key]
        if not _is_number(value):
            return Status.REJECTED_INVALID
        number = float(value)
        if not math.isfinite(number):
            return Status.REJECTED_NONFINITE
        low, high = NUMERIC_RANGES[key]
        if number < low or number > high:
            return Status.REJECTED_INVALID
    if config["frequency_hz"] > MAX_FREQUENCY_HZ or config["bandwidth_hz"] <= MIN_BANDWIDTH_HZ:
        return Status.REJECTED_INVALID
    if config["bandwidth_hz"] > config["frequency_hz"]:
        return Status.REJECTED_INVALID
    q_value = config["q"]
    if q_value is not None:
        if not _is_number(q_value):
            return Status.REJECTED_INVALID
        number = float(q_value)
        if not math.isfinite(number):
            return Status.REJECTED_NONFINITE
        low, high = NUMERIC_RANGES["q"]
        if number < low or number > high:
            return Status.REJECTED_INVALID
        derived = float(config["frequency_hz"]) / float(config["bandwidth_hz"])
        if abs(number - derived) > 1e-9 * derived:
            return Status.REJECTED_INVALID
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


def effective_q(config: Dict[str, Any]) -> float:
    if validate_config(config) is not Status.OK:
        raise ValueError(validate_config(config).value)
    if config["q"] is not None:
        return float(config["q"])
    return float(config["frequency_hz"]) / float(config["bandwidth_hz"])


def design_coefficients(frequency_hz: float, bandwidth_hz: float,
                        q: Optional[float] = None) -> Tuple[float, float, float, float, float]:
    """RBJ notch coefficients; Q is f0/bandwidth unless explicitly supplied."""
    for name, value in (("frequency_hz", frequency_hz),
                        ("bandwidth_hz", bandwidth_hz)):
        if not _is_number(value) or not math.isfinite(float(value)):
            raise ValueError(f"nonfinite {name}")
    frequency = float(frequency_hz)
    bandwidth = float(bandwidth_hz)
    if frequency < MIN_FREQUENCY_HZ or frequency > MAX_FREQUENCY_HZ:
        raise ValueError("frequency_hz out of range")
    if bandwidth < MIN_BANDWIDTH_HZ or bandwidth > MAX_BANDWIDTH_HZ or bandwidth > frequency:
        raise ValueError("bandwidth_hz out of range")
    quality = effective_q(config_with(frequency_hz=frequency, bandwidth_hz=bandwidth, q=q))
    omega = 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
    cosine = math.cos(omega)
    alpha = math.sin(omega) / (2.0 * quality)
    a0 = 1.0 + alpha
    return (1.0 / a0, -2.0 * cosine / a0, 1.0 / a0,
            -2.0 * cosine / a0, (1.0 - alpha) / a0)


def analytic_gain(coefficients: Tuple[float, float, float, float, float],
                  frequency_hz: float) -> float:
    """Exact magnitude response of the pinned biquad at a real frequency."""
    b0, b1, b2, a1, a2 = coefficients
    omega = 2.0 * math.pi * float(frequency_hz) / SAMPLE_RATE_HZ
    cos1, sin1 = math.cos(omega), math.sin(omega)
    cos2, sin2 = math.cos(2.0 * omega), math.sin(2.0 * omega)
    numerator = (b0 + b1 * cos1 + b2 * cos2) ** 2 + (b1 * sin1 + b2 * sin2) ** 2
    denominator = (1.0 + a1 * cos1 + a2 * cos2) ** 2 + (a1 * sin1 + a2 * sin2) ** 2
    return math.sqrt(numerator / denominator)


@dataclass
class NotchState:
    frequency_hz: float
    bandwidth_hz: float
    coefficients: Tuple[float, float, float, float, float]
    z1: float = 0.0
    z2: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "frequency_hz": self.frequency_hz,
            "bandwidth_hz": self.bandwidth_hz,
            "coefficients": list(self.coefficients),
            "z1": self.z1,
            "z2": self.z2,
        }


@dataclass
class SessionState:
    epoch: int
    next_input_sample: int
    frames_processed: int = 0
    frames_rejected: int = 0
    active_frames: int = 0
    transitions: List[str] = field(default_factory=list)
    closed: bool = False
    notch: Optional[NotchState] = None

    def copy(self) -> "SessionState":
        notch = None
        if self.notch is not None:
            notch = NotchState(self.notch.frequency_hz, self.notch.bandwidth_hz,
                               self.notch.coefficients, self.notch.z1, self.notch.z2)
        return SessionState(self.epoch, self.next_input_sample,
                            self.frames_processed, self.frames_rejected,
                            self.active_frames, list(self.transitions),
                            self.closed, notch)

    def digest(self) -> str:
        # Rejected inputs increment frames_rejected but are deliberately absent
        # from the state digest so fail-closed behavior is directly checkable.
        return object_digest({
            "epoch": self.epoch,
            "next_input_sample": self.next_input_sample,
            "frames_processed": self.frames_processed,
            "active_frames": self.active_frames,
            "transitions": self.transitions,
            "closed": self.closed,
            "notch": None if self.notch is None else self.notch.as_dict(),
        })


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    state_digest: str = ""


class NotchSession:
    """Task-local reference session with explicit v0-like control semantics."""

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 epoch: int = 1, first_input_sample: int = 0) -> None:
        status, instance = self.create(config, epoch, first_input_sample)
        if status is not Status.OK or instance is None:
            raise ValueError(status.value)
        self.config = instance.config
        self.state = instance.state

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]], epoch: int = 1,
               first_input_sample: int = 0) -> Tuple[Status, Optional["NotchSession"]]:
        status = validate_config(config)
        if status is not Status.OK:
            return status, None
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0
                or not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool) or first_input_sample < 0):
            return Status.REJECTED_INVALID, None
        instance = cls.__new__(cls)
        instance.config = dict(config or DEFAULT_CONFIG)
        coefficients = design_coefficients(
            float(instance.config["frequency_hz"]),
            float(instance.config["bandwidth_hz"]),
            instance.config["q"])
        notch = NotchState(float(instance.config["frequency_hz"]),
                           float(instance.config["bandwidth_hz"]), coefficients)
        instance.state = SessionState(
            epoch=epoch, next_input_sample=first_input_sample,
            transitions=[f"created@epoch:{epoch}:start:{first_input_sample}:"
                         f"f0:{instance.config['frequency_hz']}:"
                         f"bw:{instance.config['bandwidth_hz']}"],
            notch=notch)
        return Status.OK, instance

    def reset(self, epoch: int, first_input_sample: int = 0) -> Status:
        if self.state.closed:
            return Status.CLOSED
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch <= self.state.epoch
                or not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool) or first_input_sample < 0):
            self.state.frames_rejected += 1
            return Status.REJECTED_EPOCH
        coefficients = design_coefficients(
            float(self.config["frequency_hz"]), float(self.config["bandwidth_hz"]),
            self.config["q"])
        self.state = SessionState(
            epoch=epoch, next_input_sample=first_input_sample,
            transitions=[f"reset@epoch:{epoch}:start:{first_input_sample}"],
            notch=NotchState(float(self.config["frequency_hz"]),
                             float(self.config["bandwidth_hz"]), coefficients))
        return Status.OK

    def close(self) -> Status:
        if self.state.closed:
            return Status.CLOSED
        self.state.closed = True
        self.state.transitions.append("closed")
        return Status.OK

    def _reject(self, status: Status) -> ProcessResult:
        self.state.frames_rejected += 1
        return ProcessResult(status, state_digest=self.state.digest())

    def process(self, frame: Sequence[float], epoch: Optional[int] = None,
                first_input_sample: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED, state_digest=state.digest())
        if len(frame) != FRAME_SAMPLES:
            return self._reject(Status.REJECTED_TENSOR)
        try:
            values = [float(value) for value in frame]
        except (TypeError, ValueError, OverflowError):
            return self._reject(Status.REJECTED_NONFINITE)
        if any(not math.isfinite(value) for value in values):
            return self._reject(Status.REJECTED_NONFINITE)
        if any(abs(value) > float(self.config["max_abs_input"]) for value in values):
            return self._reject(Status.REJECTED_INVALID)
        if epoch is not None and (not isinstance(epoch, int) or epoch != state.epoch):
            return self._reject(Status.REJECTED_EPOCH)
        expected_start = state.next_input_sample
        if first_input_sample is not None and (
                not isinstance(first_input_sample, int)
                or first_input_sample != expected_start):
            return self._reject(Status.REJECTED_POSITION)
        if state.notch is None:
            return self._reject(Status.REJECTED_STATE)

        work = state.copy()
        notch = work.notch
        assert notch is not None
        output: List[float] = []
        for value in values:
            if self.config["profile"] == "bypass":
                filtered = value
            else:
                b0, b1, b2, a1, a2 = notch.coefficients
                filtered = b0 * value + notch.z1
                notch.z1 = b1 * value - a1 * filtered + notch.z2
                notch.z2 = b2 * value - a2 * filtered
            if self.config["saturation"] == "tanh":
                threshold = float(self.config["saturation_threshold"])
                filtered = threshold * math.tanh(filtered / threshold)
            if not math.isfinite(filtered) or abs(filtered) > 16.0:
                return self._reject(Status.REJECTED_NONFINITE)
            output.append(filtered)
        work.frames_processed += 1
        work.active_frames += 1
        work.next_input_sample = expected_start + FRAME_SAMPLES
        self.state = work
        return ProcessResult(Status.OK, tuple(output), work.digest())

    def process_stream(self, samples: Sequence[float], epoch: Optional[int] = None,
                       first_input_sample: Optional[int] = None
                       ) -> Tuple[Status, Tuple[float, ...]]:
        if len(samples) % FRAME_SAMPLES:
            return Status.REJECTED_TENSOR, ()
        chunks: List[float] = []
        for offset in range(0, len(samples), FRAME_SAMPLES):
            expected = None if first_input_sample is None else first_input_sample + offset
            result = self.process(samples[offset:offset + FRAME_SAMPLES],
                                  epoch=epoch, first_input_sample=expected)
            if result.status is not Status.OK:
                return result.status, ()
            chunks.extend(result.samples)
        return Status.OK, tuple(chunks)


def _lcg(seed: int) -> Iterable[float]:
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def synthetic_speech(frames: int, seed: int = 20261124) -> Tuple[float, ...]:
    """Synthetic formant/harmonic program material; never recorded speech."""
    noise = _lcg(seed)
    samples: List[float] = []
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.1 * time_s - 0.4)
        pause = 0.0 if (index // FRAME_SAMPLES) % 41 in (38, 39, 40) else 1.0
        envelope = (0.035 + 0.18 * syllable ** 2) * pause
        f0 = 110.0 + 22.0 * math.sin(2.0 * math.pi * 0.31 * time_s)
        pulse_period = max(2, int(round(SAMPLE_RATE_HZ / f0)))
        drive = (1.0 if index % pulse_period == 0 else 0.0) + 0.025 * next(noise)
        formant_a[0], formant_a[1] = (
            0.974 * formant_a[0] - 0.016 * formant_a[1] + drive, formant_a[0])
        formant_b[0], formant_b[1] = (
            0.949 * formant_b[0] - 0.033 * formant_b[1] + drive, formant_b[0])
        samples.append(max(-0.95, min(0.95,
                           envelope * (0.42 * formant_a[0] + 0.20 * formant_b[0]))))
    return tuple(samples)


def tone(frames: int, frequency_hz: float, amplitude: float = 0.09,
         seed: int = 7) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(amplitude * math.sin(2.0 * math.pi * frequency_hz
                                      * index / SAMPLE_RATE_HZ)
                 + 0.0005 * next(noise)
                 for index in range(frames * FRAME_SAMPLES))


def chirp(frames: int, start_hz: float = 100.0, end_hz: float = 7000.0) -> Tuple[float, ...]:
    total = frames * FRAME_SAMPLES
    phase = 0.0
    output: List[float] = []
    for index in range(total):
        frequency = start_hz + (end_hz - start_hz) * index / max(total - 1, 1)
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
        output.append(0.08 * math.sin(phase))
    return tuple(output)


def silence(frames: int) -> Tuple[float, ...]:
    return (0.0,) * (frames * FRAME_SAMPLES)


def impulse(frames: int = 8, amplitude: float = 0.5) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = amplitude
    return tuple(values)


def step(frames: int = 12, onset_frame: int = 4, amplitude: float = 0.25) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    onset = onset_frame * FRAME_SAMPLES
    values[onset:] = [amplitude] * (len(values) - onset)
    return tuple(values)


def impulse_train(frames: int = 120, period: int = 37,
                  amplitude: float = 0.4) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    for index in range(0, len(values), period):
        values[index] = amplitude if (index // period) % 2 == 0 else -amplitude
    return tuple(values)


def rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(len(values), 1))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def db(value: float) -> float:
    return 10.0 * math.log10(max(value, 1e-30))


def tone_power(values: Sequence[float], frequency_hz: float) -> float:
    """Mean normalized single-frequency power over full 160-sample blocks."""
    cosines = tuple(math.cos(2.0 * math.pi * frequency_hz * n / SAMPLE_RATE_HZ)
                    for n in range(FRAME_SAMPLES))
    sines = tuple(math.sin(2.0 * math.pi * frequency_hz * n / SAMPLE_RATE_HZ)
                  for n in range(FRAME_SAMPLES))
    total = 0.0
    blocks = 0
    for start in range(0, len(values), FRAME_SAMPLES):
        block = tuple(values[start:start + FRAME_SAMPLES])
        if len(block) < FRAME_SAMPLES:
            block += (0.0,) * (FRAME_SAMPLES - len(block))
        real = sum(value * cosine for value, cosine in zip(block, cosines))
        imag = sum(value * sine for value, sine in zip(block, sines))
        total += (real * real + imag * imag) / (FRAME_SAMPLES * FRAME_SAMPLES)
        blocks += 1
    return total / max(blocks, 1)


def tone_to_total_db(values: Sequence[float], frequency_hz: float) -> float:
    return db(tone_power(values, frequency_hz)) - db(rms(values) ** 2)


def envelope(values: Sequence[float]) -> Tuple[float, ...]:
    return tuple(rms(values[index:index + FRAME_SAMPLES])
                 for index in range(0, len(values), FRAME_SAMPLES))


def correlation(left: Sequence[float], right: Sequence[float]) -> float:
    count = min(len(left), len(right))
    first = left[:count]
    second = right[:count]
    mean_a = sum(first) / max(count, 1)
    mean_b = sum(second) / max(count, 1)
    centered_a = [value - mean_a for value in first]
    centered_b = [value - mean_b for value in second]
    numerator = sum(a * b for a, b in zip(centered_a, centered_b))
    denominator = math.sqrt(sum(a * a for a in centered_a)
                            * sum(b * b for b in centered_b))
    return 0.0 if denominator == 0.0 else numerator / denominator


def closed_loop(program: Sequence[float], loop_gain: float,
                config: Dict[str, Any], resonator_hz: float = 1000.0,
                resonance: float = 0.96, resonance_gain: float = 0.04,
                loop_saturation: Optional[float] = None) -> Dict[str, Any]:
    """Frame-causal feedback loop with a resonator and optional nonlinearity."""
    session, = [NotchSession(config)]
    omega = 2.0 * math.pi * resonator_hz / SAMPLE_RATE_HZ
    coefficient = 2.0 * resonance * math.cos(omega)
    decay = resonance * resonance
    state_a = [0.0, 0.0]
    history = (0.0,) * FRAME_SAMPLES
    output: List[float] = []
    rejected = 0
    nonfinite = 0
    program_rms = rms(program[:len(program) // 2])
    for offset in range(0, len(program), FRAME_SAMPLES):
        mic: List[float] = []
        for sample, feedback in zip(program[offset:offset + FRAME_SAMPLES], history):
            resonator_value = feedback + coefficient * state_a[0] - decay * state_a[1]
            state_a[1], state_a[0] = state_a[0], resonator_value
            value = sample + loop_gain * resonance_gain * resonator_value
            if loop_saturation is not None:
                value = loop_saturation * math.tanh(value / loop_saturation)
            mic.append(value)
        result = session.process(tuple(mic))
        if result.status is not Status.OK:
            rejected += 1
            playback = (0.0,) * FRAME_SAMPLES
        else:
            playback = result.samples
        output.extend(playback)
        history = playback
        nonfinite += sum(1 for value in playback if not math.isfinite(value))
    tail = output[-FRAME_SAMPLES * 10:]
    tail_rms = rms(tail)
    return {
        "loop_gain": loop_gain,
        "tail_rms": round(tail_rms, 9),
        "tail_db_relative_to_program": round(
            20.0 * math.log10(max(tail_rms, 1e-30) / max(program_rms, 1e-30)), 3),
        "peak_abs_output": round(peak(output), 6),
        "rejected_frames": rejected,
        "nonfinite_frames": nonfinite,
        "frames_processed": session.state.frames_processed,
        "output_digest": tensor_digest(output),
    }


def build_report() -> Dict[str, Any]:
    """Run every deterministic condition and return the canonical report object."""
    frame_counts: List[int] = []

    def counted(session: NotchSession) -> NotchSession:
        frame_counts.append(session.state.frames_processed)
        return session

    coefficients = design_coefficients(
        float(DEFAULT_CONFIG["frequency_hz"]), float(DEFAULT_CONFIG["bandwidth_hz"]))
    tone_rms = 0.09 / math.sqrt(2.0)
    fixture_spec = {
        "contract": CONTRACT_ID,
        "format": {"channels": CHANNELS, "frame_samples": FRAME_SAMPLES,
                   "sample_format": "f32", "sample_rate_hz": SAMPLE_RATE_HZ},
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "default_config": DEFAULT_CONFIG,
        "center_configs": [list(pair) for pair in CENTER_CONFIGS],
        "sweep_frequencies_hz": list(SWEEP_FREQUENCIES_HZ),
        "seeds": {"speech": 20261124, "tone": 7, "sweep": 1000, "load": 4242},
        "stages": {"speech_frames": 300, "load_frames": 2000,
                   "silence_frames": 1000, "impulse_train_frames": 120},
        "loop": {"resonator_hz": 1000.0, "resonance": 0.96,
                 "resonance_gain": 0.04, "gains": [1.05, 1.15, 1.30]},
    }

    # Deterministic baseline stimuli.
    silence_session = NotchSession(config_with())
    silence_status, silence_samples = silence_session.process_stream(silence(40))
    counted(silence_session)
    impulse_session = NotchSession(config_with())
    impulse_status, impulse_samples = impulse_session.process_stream(impulse())
    counted(impulse_session)
    impulse_peak_index = max(range(len(impulse_samples)),
                             key=lambda index: abs(impulse_samples[index]))
    step_session = NotchSession(config_with())
    step_status, step_samples = step_session.process_stream(step())
    counted(step_session)
    step_onset = 4 * FRAME_SAMPLES
    crossing = next((index - step_onset for index in range(step_onset, len(step_samples))
                     if abs(step_samples[index] - 0.25) <= 0.001), len(step_samples))
    step_tail_mean = sum(step_samples[-FRAME_SAMPLES:]) / FRAME_SAMPLES
    chirp_session = NotchSession(config_with())
    chirp_status, chirp_samples = chirp_session.process_stream(chirp(40))
    counted(chirp_session)

    # Steady-state transfer sweep at the fixed default notch.
    sweep_rows: List[Dict[str, Any]] = []
    sweep_samples: List[float] = []
    for frequency in SWEEP_FREQUENCIES_HZ:
        session = NotchSession(config_with())
        status, output = session.process_stream(
            tone(12, frequency, 0.09, seed=1000 + frequency))
        if status is not Status.OK:
            raise RuntimeError(f"sweep failed at {frequency} Hz: {status}")
        counted(session)
        sweep_samples.extend(output)
        tail = output[-FRAME_SAMPLES * 4:]
        measured = rms(tail) / tone_rms
        expected = analytic_gain(coefficients, float(frequency))
        sweep_rows.append({
            "frequency_hz": frequency,
            "measured_gain": round(measured, 6),
            "analytic_gain": round(expected, 6),
            "gain_error_db": round(20.0 * math.log10(max(measured, 1e-30)
                                                    / max(expected, 1e-30)), 3),
        })

    # Explicit centre/bandwidth acceptance: centre rejection and skirt passthrough.
    center_rows: List[Dict[str, Any]] = []
    for center_hz, bandwidth_hz in CENTER_CONFIGS:
        pair_config = config_with(frequency_hz=center_hz, bandwidth_hz=bandwidth_hz)
        pair_coefficients = design_coefficients(center_hz, bandwidth_hz)
        session = NotchSession(pair_config)
        status, output = session.process_stream(tone(16, center_hz, 0.09,
                                                     seed=2000 + int(center_hz)))
        center_gain = rms(output[-FRAME_SAMPLES * 4:]) / tone_rms
        skirt_hz = min(MAX_FREQUENCY_HZ, center_hz + 5.0 * bandwidth_hz)
        skirt_session = NotchSession(pair_config)
        skirt_status, skirt_output = skirt_session.process_stream(
            tone(16, skirt_hz, 0.09, seed=3000 + int(center_hz)))
        skirt_gain = rms(skirt_output[-FRAME_SAMPLES * 4:]) / tone_rms
        counted(session)
        counted(skirt_session)
        center_rows.append({
            "frequency_hz": center_hz,
            "bandwidth_hz": bandwidth_hz,
            "quality": round(effective_q(pair_config), 6),
            "status": status.value,
            "center_measured_gain": round(center_gain, 6),
            "center_analytic_gain": round(analytic_gain(pair_coefficients, center_hz), 6),
            "skirt_frequency_hz": skirt_hz,
            "skirt_measured_gain": round(skirt_gain, 6),
            "skirt_analytic_gain": round(analytic_gain(pair_coefficients, skirt_hz), 6),
            "skirt_status": skirt_status.value,
            "output_digest": tensor_digest(output),
        })

    # Attack/release with a static notch: immediate onset, finite IIR decay.
    attack_session = NotchSession(config_with())
    tone_start_frame = 20
    tone_end_frame = 120
    attack_frequency_hz = 700.0
    burst_source = (silence(tone_start_frame)
                    + tone(100, attack_frequency_hz, 0.09, seed=7)
                    + silence(40))
    burst_status, burst_output = attack_session.process_stream(burst_source)
    counted(attack_session)
    frame_envelopes = envelope(burst_output)
    attack_frame = next((index - tone_start_frame
                         for index in range(tone_start_frame, tone_end_frame)
                         if frame_envelopes[index] >= 0.01), None)
    release_frame = next((index - tone_end_frame
                          for index in range(tone_end_frame, len(frame_envelopes))
                          if frame_envelopes[index] <= 0.0009), None)

    # Clean synthetic speech: notch-vs-bypass preservation and load control.
    speech = synthetic_speech(300)
    notch_speech_session = NotchSession(config_with())
    speech_status, notch_speech = notch_speech_session.process_stream(speech)
    counted(notch_speech_session)
    bypass_session = NotchSession(config_with(profile="bypass"))
    bypass_status, bypass_speech = bypass_session.process_stream(speech)
    counted(bypass_session)
    speech_rms_delta_db = 20.0 * math.log10(
        max(rms(notch_speech), 1e-30) / max(rms(bypass_speech), 1e-30))

    injection = tuple(
        value + (0.035 * math.sin(2.0 * math.pi * 1000.0 * index / SAMPLE_RATE_HZ)
                 if FRAME_SAMPLES * 100 <= index < FRAME_SAMPLES * 200 else 0.0)
        for index, value in enumerate(speech))
    injection_session = NotchSession(config_with())
    injection_status, injection_output = injection_session.process_stream(injection)
    counted(injection_session)
    tone_region_in = injection[FRAME_SAMPLES * 100:FRAME_SAMPLES * 200]
    tone_region_out = injection_output[FRAME_SAMPLES * 100:FRAME_SAMPLES * 200]
    clean_region_in = injection[:FRAME_SAMPLES * 100]
    clean_region_out = injection_output[:FRAME_SAMPLES * 100]
    tone_db_before = db(tone_power(tone_region_in, 1000.0))
    tone_db_after = db(tone_power(tone_region_out, 1000.0))
    clean_db_before = db(tone_power(clean_region_in, 1000.0))
    clean_db_after = db(tone_power(clean_region_out, 1000.0))

    load_samples = tone(2000, 1000.0, 0.06, seed=4242)
    load_session = NotchSession(config_with())
    load_status, load_output = load_session.process_stream(load_samples)
    counted(load_session)

    # Interacting nonlinear configurations in a frame-causal feedback loop.
    loop_program = synthetic_speech(200) + silence(100)
    loop_results: Dict[str, Any] = {}
    for loop_gain in (1.05, 1.15, 1.30):
        loop_results[str(loop_gain)] = {
            "bypass": closed_loop(loop_program, loop_gain, config_with(profile="bypass")),
            "notch": closed_loop(loop_program, loop_gain, config_with()),
            "notch_plus_saturation": closed_loop(
                loop_program, loop_gain, config_with(saturation="tanh",
                                                     saturation_threshold=0.8),
                loop_saturation=0.9),
        }
        frame_counts.extend(item["frames_processed"]
                            for item in loop_results[str(loop_gain)].values())

    # Long silence and alternating impulse trains stay finite and bounded.
    long_session = NotchSession(config_with())
    long_status, long_output = long_session.process_stream(
        silence(1000) + impulse_train(120) + silence(200))
    counted(long_session)
    long_tail = long_output[-FRAME_SAMPLES * 40:]

    # State isolation, epoch/position controls, and adverse inputs.
    session_a = NotchSession(config_with())
    session_b = NotchSession(config_with(frequency_hz=120.0, bandwidth_hz=12.0))
    probe = tone(10, 1000.0, 0.09)
    status_a, output_a = session_a.process_stream(probe)
    status_b, output_b = session_b.process_stream(probe)
    counted(session_a)
    counted(session_b)
    digest_before_a = session_a.state.digest()
    digest_before_b = session_b.state.digest()
    reset_status = session_a.reset(2, 160)
    status_a_reset, output_a_reset = session_a.process_stream(probe, epoch=2,
                                                              first_input_sample=160)
    counted(session_a)
    isolation = {
        "status_a": status_a.value,
        "status_b": status_b.value,
        "distinct_states": digest_before_a != digest_before_b,
        "distinct_outputs": tensor_digest(output_a) != tensor_digest(output_b),
        "digest_a": tensor_digest(output_a),
        "digest_b": tensor_digest(output_b),
        "reset_status": reset_status.value,
        "status_a_after_reset": status_a_reset.value,
        "reset_output_matches_fresh": tensor_digest(output_a_reset) == tensor_digest(output_a),
        "session_b_state_unchanged": session_b.state.digest() == digest_before_b,
        "digest_a_after_reset": session_a.state.digest(),
    }

    epoch_session = NotchSession(config_with(), epoch=5, first_input_sample=320)
    epoch_session.process(tone(1, 1000.0, 0.05))
    stale_epoch = epoch_session.process(tone(1, 1000.0, 0.05), epoch=4)
    stale_position = epoch_session.process(tone(1, 1000.0, 0.05),
                                           first_input_sample=320)
    epoch_valid = epoch_session.process(tone(1, 1000.0, 0.05), epoch=5,
                                        first_input_sample=480)
    counted(epoch_session)
    epoch_digest = epoch_session.state.digest()
    epoch_controls = {
        "stale_epoch_status": stale_epoch.status.value,
        "stale_position_status": stale_position.status.value,
        "valid_epoch_status": epoch_valid.status.value,
        "state_unchanged_after_rejects":
            stale_epoch.state_digest == stale_position.state_digest,
        "frames_processed": epoch_session.state.frames_processed,
        "digest": epoch_digest,
    }

    adverse_session = NotchSession(config_with())
    adverse_session.process_stream(tone(5, 1000.0, 0.05))
    counted(adverse_session)
    adverse_before = adverse_session.state.digest()
    nan_frame = adverse_session.process((float("nan"),) * FRAME_SAMPLES)
    inf_frame = adverse_session.process(tuple([float("inf")] + [0.0] * (FRAME_SAMPLES - 1)))
    short_frame = adverse_session.process((0.0,) * 159)
    long_frame = adverse_session.process((0.0,) * 161)
    oversized = adverse_session.process((9.0,) * FRAME_SAMPLES)
    adverse_after = adverse_session.state.digest()
    nonfinite_configs = {
        "nan_frequency": validate_config(config_with(frequency_hz=float("nan"))).value,
        "inf_frequency": validate_config(config_with(frequency_hz=float("inf"))).value,
        "nan_bandwidth": validate_config(config_with(bandwidth_hz=float("nan"))).value,
        "zero_bandwidth": validate_config(config_with(bandwidth_hz=0.0)).value,
        "zero_q": validate_config(config_with(q=0.0)).value,
        "nan_q": validate_config(config_with(q=float("nan"))).value,
        "inf_q": validate_config(config_with(q=float("inf"))).value,
        "mismatched_q": validate_config(config_with(q=5.0)).value,
        "high_frequency": validate_config(config_with(frequency_hz=8100.0)).value,
        "bandwidth_above_frequency": validate_config(
            config_with(frequency_hz=100.0, bandwidth_hz=200.0)).value,
        "missing_frequency": validate_config(
            {key: value for key, value in config_with().items()
             if key != "frequency_hz"}).value,
        "wrong_type": validate_config(config_with(frequency_hz="1000")).value,
    }
    coefficient_errors: Dict[str, str] = {}
    for name, arguments in (("nan_frequency", (float("nan"), 100.0, None)),
                            ("zero_bandwidth", (1000.0, 0.0, None)),
                            ("nan_q", (1000.0, 100.0, float("nan"))),
                            ("zero_q", (1000.0, 100.0, 0.0))):
        try:
            design_coefficients(*arguments)
            coefficient_errors[name] = "accepted"
        except ValueError:
            coefficient_errors[name] = "rejected"

    adverse = {
        "config_statuses": nonfinite_configs,
        "coefficient_statuses": coefficient_errors,
        "nan_frame_status": nan_frame.status.value,
        "inf_frame_status": inf_frame.status.value,
        "short_frame_status": short_frame.status.value,
        "long_frame_status": long_frame.status.value,
        "out_of_range_frame_status": oversized.status.value,
        "state_unchanged": adverse_before == adverse_after,
        "frames_processed": adverse_session.state.frames_processed,
    }

    closed_session = NotchSession(config_with())
    closed_session.process_stream(tone(2, 1000.0, 0.05))
    counted(closed_session)
    close_status = closed_session.close()
    double_close_status = closed_session.close()
    closed_process_status = closed_session.process(tone(1, 1000.0, 0.05)).status
    closed_reset_status = closed_session.reset(2, 0)
    lifecycle = {
        "close_status": close_status.value,
        "double_close_status": double_close_status.value,
        "process_after_close": closed_process_status.value,
        "reset_after_close": closed_reset_status.value,
        "transitions": closed_session.state.transitions,
    }

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/narrow-biquad-notch-report/0.1",
        "contract": CONTRACT_ID,
        "status": "proposal-only-synthetic",
        "scope": "Deterministic model-free DSP fixture; no real audio, device, "
                 "listening or release qualification.",
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "config": DEFAULT_CONFIG,
        "counts": {
            "conditions": 16,
            "source_pins": len(SOURCE_PINS),
            "boundary_pins": len(BOUNDARY_PINS),
            "center_bandwidth_pairs": len(CENTER_CONFIGS),
            "sweep_frequencies": len(SWEEP_FREQUENCIES_HZ),
            "adverse_config_cases": len(nonfinite_configs),
            "adverse_frame_cases": 5,
            "load_frames": load_session.state.frames_processed,
            "long_stability_frames": long_session.state.frames_processed,
            "processed_frames": sum(frame_counts),
            "processed_samples": sum(frame_counts) * FRAME_SAMPLES,
        },
        "results": {
            "silence": {
                "status": silence_status.value,
                "peak_abs_output": peak(silence_samples),
                "output_digest": tensor_digest(silence_samples),
            },
            "impulse": {
                "status": impulse_status.value,
                "peak_index": impulse_peak_index,
                "peak_abs_output": round(peak(impulse_samples), 6),
                "output_digest": tensor_digest(impulse_samples),
            },
            "step": {
                "status": step_status.value,
                "crossing_samples": crossing,
                "steady_state_mean": round(step_tail_mean, 6),
                "peak_abs_output": round(peak(step_samples), 6),
                "output_digest": tensor_digest(step_samples),
            },
            "chirp": {
                "status": chirp_status.value,
                "frames": len(chirp_samples) // FRAME_SAMPLES,
                "peak_abs_output": round(peak(chirp_samples), 6),
                "finite": all(math.isfinite(value) for value in chirp_samples),
                "output_digest": tensor_digest(chirp_samples),
            },
            "frequency_sweep": {
                "status": "ok",
                "frames_per_frequency": 12,
                "center_frequency_hz": DEFAULT_CONFIG["frequency_hz"],
                "bandwidth_hz": DEFAULT_CONFIG["bandwidth_hz"],
                "rows": sweep_rows,
                "min_gain": min(row["measured_gain"] for row in sweep_rows),
                "max_gain": max(row["measured_gain"] for row in sweep_rows),
                "max_gain_error_db": max(row["gain_error_db"] for row in sweep_rows
                                         if row["analytic_gain"] >= 0.01),
                "center_measured_gain": next(row["measured_gain"] for row in sweep_rows
                                             if row["frequency_hz"] == 1000),
                "output_digest": tensor_digest(sweep_samples),
            },
            "center_bandwidth_controls": {
                "status": "ok",
                "rows": center_rows,
                "output_digest": object_digest(center_rows),
            },
            "attack_release": {
                "status": burst_status.value,
                "tone_start_frame": tone_start_frame,
                "tone_end_frame": tone_end_frame,
                "probe_frequency_hz": attack_frequency_hz,
                "attack_frames": attack_frame,
                "release_frames": release_frame,
                "peak_abs_output": round(peak(burst_output), 6),
                "output_digest": tensor_digest(burst_output),
            },
            "clean_speech": {
                "status": speech_status.value,
                "bypass_status": bypass_status.value,
                "frames": len(speech) // FRAME_SAMPLES,
                "rms_delta_db": round(speech_rms_delta_db, 3),
                "envelope_correlation": round(
                    correlation(envelope(notch_speech), envelope(bypass_speech)), 6),
                "output_digest": tensor_digest(notch_speech),
                "bypass_output_digest": tensor_digest(bypass_speech),
                "qualification": "synthetic-formant proxy only",
            },
            "tone_in_speech": {
                "status": injection_status.value,
                "injected_frequency_hz": 1000,
                "injected_amplitude": 0.035,
                "injected_frames": 100,
                "tone_power_db_before": round(tone_db_before, 3),
                "tone_power_db_after": round(tone_db_after, 3),
                "tone_reduction_db": round(tone_db_before - tone_db_after, 3),
                "clean_region_tone_db_before": round(clean_db_before, 3),
                "clean_region_tone_db_after": round(clean_db_after, 3),
                "output_digest": tensor_digest(injection_output),
            },
            "load_control": {
                "status": load_status.value,
                "frames": load_session.state.frames_processed,
                "samples": len(load_output),
                "finite": all(math.isfinite(value) for value in load_output),
                "peak_abs_output": round(peak(load_output), 6),
                "output_digest": tensor_digest(load_output),
                "timing_claim": "none; unpaced deterministic count only",
            },
            "loop_nonlinear": loop_results,
            "long_stability": {
                "status": long_status.value,
                "silence_frames": 1000,
                "impulse_train_frames": 120,
                "tail_silence_frames": 200,
                "frames": long_session.state.frames_processed,
                "peak_abs_output": round(peak(long_output), 6),
                "tail_rms": round(rms(long_tail), 9),
                "all_finite": all(math.isfinite(value) for value in long_output),
                "frames_rejected": long_session.state.frames_rejected,
                "output_digest": tensor_digest(long_output),
            },
            "state_isolation": isolation,
            "epoch_and_position": epoch_controls,
            "adverse": adverse,
            "lifecycle": lifecycle,
        },
        "qualification": {
            "status": "incomplete",
            "real_speech": {"status": "blocked",
                            "reason": "no authorized recorded speech or clean references"},
            "listening": {"status": "blocked",
                          "reason": "no listening panel, room or target playback path"},
            "nonlinear_interaction": {"status": "incomplete",
                                      "reason": "synthetic loop only; no measured amplifier, "
                                                "loudspeaker or microphone nonlinearity"},
            "device": {"status": "blocked",
                       "reason": "no target-device CPU, memory, deadline or timing run"},
            "release": {"status": "blocked",
                        "reason": "optional reference only; not installed or registered by default"},
        },
        "blockers": [
            "Real-speech and listening qualification requires an authorized corpus, "
            "clean references and a blinded protocol.",
            "Real nonlinear-interaction qualification requires a measured playback/"
            "capture path with pinned gain, delay and saturation.",
            "Production readiness requires target-device CPU, memory, latency and "
            "availability measurement plus provider intake.",
        ],
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
