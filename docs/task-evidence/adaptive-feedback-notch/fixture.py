"""Deterministic synthetic reference for the optional adaptive feedback notch.

This is a model-free, file-free DSP fixture. It fixes the v0 format (16 kHz,
mono f32, 160 samples), a small adaptive-notch/gain-margin controller, the
closed-loop simulator and the canonical metrics used by ``test_fixture.py``.
Nothing here is a real-audio, device, model or release qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CONTRACT_ID = "audio-sdk/adaptive-feedback-notch/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MIN_HZ = 200
MAX_HZ = 4000
STEP_HZ = 100
FREQUENCIES_HZ: Tuple[int, ...] = tuple(range(MIN_HZ, MAX_HZ + 1, STEP_HZ))
MAX_NOTCHES_ALLOWED = 4
PROVIDER_ID = "dsp.adaptive-notch-notchref.v0"

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
# The board is mutable shared state, not pinned qualification evidence. Its
# digest is recorded as a read-time snapshot only and must not gate results.
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "5eea8b61fa70c0e3669ceb878aefc96e9005204f97f1970879583bc710689e80",
    "mutable": True,
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "profile": "full",
    "min_hz": MIN_HZ,
    "max_hz": MAX_HZ,
    "step_hz": STEP_HZ,
    "prominence_db": 14.0,
    "absolute_dbfs": -38.0,
    "persistence_frames": 4,
    "release_frames": 24,
    "cooldown_frames": 60,
    "max_notches": 2,
    "q": 24.0,
    "gain_reduction_db": 0.0,
    "floor_gain_db": -12.0,
    "recovery_frames": 200,
    "max_abs_input": 4.0,
    "saturation": "none",
    "saturation_threshold": 1.0,
}

REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES = {
    "prominence_db": (6.0, 30.0),
    "absolute_dbfs": (-80.0, -10.0),
    "persistence_frames": (1, 16),
    "release_frames": (1, 400),
    "cooldown_frames": (0, 400),
    "max_notches": (1, MAX_NOTCHES_ALLOWED),
    "q": (4.0, 40.0),
    "gain_reduction_db": (0.0, 12.0),
    "floor_gain_db": (-24.0, 0.0),
    "recovery_frames": (1, 2000),
    "max_abs_input": (0.25, 16.0),
    "saturation_threshold": (0.1, 4.0),
}

_HEX64 = set("0123456789abcdef")


class Status(str, Enum):
    OK = "ok"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_STATE = "rejected_state"
    REJECTED_MODE = "rejected_mode"
    CLOSED = "closed"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    """Fail closed on missing, malformed or nonfinite control values."""
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
    if config["profile"] not in ("full", "no_detector", "fixed_only"):
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
        if not math.isfinite(number) or number < low or number > high:
            return (Status.REJECTED_NONFINITE if not math.isfinite(number)
                    else Status.REJECTED_INVALID)
    for key in ("persistence_frames", "release_frames", "cooldown_frames",
                "max_notches", "recovery_frames"):
        if int(config[key]) != config[key]:
            return Status.REJECTED_INVALID
    if config["floor_gain_db"] > 0.0 or config["gain_reduction_db"] < 0.0:
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
    """Mean normalized tone power over complete 160-sample blocks."""
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
    age_frames: int
    miss_frames: int
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    z1: float = 0.0
    z2: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "frequency_hz": self.frequency_hz,
            "bin_index": self.bin_index,
            "age_frames": self.age_frames,
            "miss_frames": self.miss_frames,
            "z1": self.z1,
            "z2": self.z2,
        }


@dataclass
class ControllerState:
    candidate_runs: Dict[int, int] = field(default_factory=dict)
    notches: List[NotchState] = field(default_factory=list)
    cooldowns: Dict[int, int] = field(default_factory=dict)
    gain_db: float = 0.0
    frames_since_detection: int = 0
    frames_processed: int = 0
    activation_count: int = 0
    release_count: int = 0
    invalid_count: int = 0
    active_frames: int = 0
    transitions: List[str] = field(default_factory=list)
    closed: bool = False

    def copy(self) -> "ControllerState":
        return ControllerState(
            candidate_runs=dict(self.candidate_runs),
            notches=[replace(notch) for notch in self.notches],
            cooldowns=dict(self.cooldowns),
            gain_db=self.gain_db,
            frames_since_detection=self.frames_since_detection,
            frames_processed=self.frames_processed,
            activation_count=self.activation_count,
            release_count=self.release_count,
            invalid_count=self.invalid_count,
            active_frames=self.active_frames,
            transitions=list(self.transitions),
            closed=self.closed,
        )

    def digest(self) -> str:
        payload = {
            "notches": [notch.as_dict() for notch in self.notches],
            "gain_db": self.gain_db,
            "frames_processed": self.frames_processed,
            "activation_count": self.activation_count,
            "release_count": self.release_count,
        }
        return object_digest(payload)


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    detected_hz: Tuple[int, ...] = ()
    active_hz: Tuple[int, ...] = ()
    state_digest: str = ""


class AdaptiveNotchController:
    """Opt-in reference controller: detector -> up to two notches -> margin."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        status = validate_config(config)
        if status is not Status.OK:
            raise ValueError(status.value)
        self.config = dict(config or DEFAULT_CONFIG)
        self.state = ControllerState()

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]]) -> Tuple[Status, Optional["AdaptiveNotchController"]]:
        if validate_config(config) is not Status.OK:
            return validate_config(config), None
        return Status.OK, cls(config)

    def reset(self) -> Status:
        if self.state.closed:
            return Status.CLOSED
        self.state = ControllerState()
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    @staticmethod
    def _coefficients(frequency_hz: float, quality: float) -> Tuple[float, float, float, float, float]:
        omega = 2.0 * math.pi * frequency_hz / SAMPLE_RATE_HZ
        cosine = math.cos(omega)
        alpha = math.sin(omega) / (2.0 * quality)
        a0 = 1.0 + alpha
        return (1.0 / a0, (-2.0 * cosine) / a0, 1.0 / a0,
                (-2.0 * cosine) / a0, (1.0 - alpha) / a0)

    def _spectrum_db(self, samples: Sequence[float]) -> List[float]:
        powers = [tone_power(samples, frequency) for frequency in FREQUENCIES_HZ]
        return [_db(power) for power in powers]

    def process(self, frame: Sequence[float]) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if len(frame) != FRAME_SAMPLES:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        try:
            values = [float(value) for value in frame]
        except (TypeError, ValueError, OverflowError):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        limit = float(self.config["max_abs_input"])
        if any(not math.isfinite(value) for value in values):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        if any(abs(value) > limit for value in values):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_INVALID)

        work = state.copy()
        if self.config["profile"] != "full":
            detected: List[Tuple[int, float]] = []
            levels = [0.0] * len(FREQUENCIES_HZ)
        else:
            levels = self._spectrum_db(values)
            detected = []
            for index, level in enumerate(levels):
                left = levels[index - 1] if index > 0 else -300.0
                right = levels[index + 1] if index + 1 < len(levels) else -300.0
                prominence = level - max(left, right)
                if (prominence >= float(self.config["prominence_db"])
                        and level >= float(self.config["absolute_dbfs"])):
                    run = work.candidate_runs.get(index, 0) + 1
                    work.candidate_runs[index] = run
                    if run >= int(self.config["persistence_frames"]):
                        detected.append((index, level))
                else:
                    work.candidate_runs[index] = 0

        active_now = bool(work.notches) or bool(detected)
        if active_now:
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
            coefficients = self._coefficients(notch.frequency_hz, float(self.config["q"]))
            kept.append(replace(notch, age_frames=notch.age_frames + 1,
                                miss_frames=miss,
                                b0=coefficients[0], b1=coefficients[1], b2=coefficients[2],
                                a1=coefficients[3], a2=coefficients[4]))
        work.notches = kept
        if released:
            work.release_count += len(released)
            work.transitions.append(f"active->idle@{work.frames_processed}:{','.join(map(str, released))}")

        for index in list(work.cooldowns):
            work.cooldowns[index] -= 1
            if work.cooldowns[index] <= 0:
                del work.cooldowns[index]

        if self.config["profile"] == "full":
            ranked = sorted(detected, key=lambda item: (-item[1], item[0]))
            for index, _ in ranked:
                if len(work.notches) >= int(self.config["max_notches"]):
                    break
                if index in work.cooldowns or any(notch.bin_index == index for notch in work.notches):
                    continue
                frequency = FREQUENCIES_HZ[index]
                coefficients = self._coefficients(frequency, float(self.config["q"]))
                notch = NotchState(
                    frequency_hz=frequency, bin_index=index, age_frames=0,
                    miss_frames=0, b0=coefficients[0], b1=coefficients[1],
                    b2=coefficients[2], a1=coefficients[3], a2=coefficients[4])
                work.notches.append(notch)
                work.activation_count += 1
                work.transitions.append(f"idle->active@{work.frames_processed}:{frequency}")

        gain_db = work.gain_db
        reduction = float(self.config["gain_reduction_db"])
        if self.config["profile"] == "fixed_only":
            gain_db = -abs(reduction)
        elif reduction > 0.0:
            floor = float(self.config["floor_gain_db"])
            if detected or work.notches:
                gain_db = max(floor, gain_db - reduction)
            elif work.frames_since_detection > int(self.config["recovery_frames"]):
                gain_db = min(0.0, gain_db + 0.1)
        else:
            gain_db = 0.0
        work.gain_db = gain_db
        gain = 10.0 ** (gain_db / 20.0)

        output: List[float] = []
        for sample in values:
            filtered = sample
            for notch in work.notches:
                y = notch.b0 * filtered + notch.z1
                notch.z1 = notch.b1 * filtered - notch.a1 * y + notch.z2
                notch.z2 = notch.b2 * filtered - notch.a2 * y
                filtered = y
            if self.config["saturation"] == "tanh":
                threshold = float(self.config["saturation_threshold"])
                filtered = threshold * math.tanh(filtered / threshold)
            result_sample = filtered * gain
            if not math.isfinite(result_sample) or abs(result_sample) > 16.0:
                state.invalid_count += 1
                return ProcessResult(Status.REJECTED_NONFINITE)
            output.append(result_sample)

        if work.notches or detected:
            work.active_frames += 1
        work.frames_processed += 1
        self.state = work
        return ProcessResult(
            Status.OK, tuple(output),
            tuple(FREQUENCIES_HZ[index] for index, _ in detected),
            tuple(notch.frequency_hz for notch in work.notches),
            work.digest())

    def process_stream(self, samples: Sequence[float]) -> Tuple[Status, Tuple[float, ...]]:
        if len(samples) % FRAME_SAMPLES:
            return Status.REJECTED_TENSOR, ()
        chunks: List[float] = []
        for start in range(0, len(samples), FRAME_SAMPLES):
            result = self.process(samples[start:start + FRAME_SAMPLES])
            if result.status is not Status.OK:
                return result.status, ()
            chunks.extend(result.samples)
        return Status.OK, tuple(chunks)


def _lcg(seed: int) -> Iterable[float]:
    """Deterministic 32-bit LCG returning samples in [-1, 1)."""
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def synthetic_speech(frames: int, seed: int = 20261028) -> Tuple[float, ...]:
    """Speech-like synthetic program material; not recorded speech."""
    noise = _lcg(seed)
    samples: List[float] = []
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.3 * time_s - 0.6)
        pause = 1.0 if (index // FRAME_SAMPLES) % 37 not in (34, 35, 36) else 0.0
        envelope = (0.04 + 0.20 * syllable ** 2) * pause
        f0 = 105.0 + 28.0 * math.sin(2.0 * math.pi * 0.37 * time_s)
        pulse = (index % int(round(SAMPLE_RATE_HZ / f0))) == 0
        drive = (1.0 if pulse else 0.0) + 0.035 * next(noise)
        # Two lightly damped resonators give vowel-like harmonics without a model.
        formant_a[0], formant_a[1] = (
            0.972 * formant_a[0] - 0.018 * formant_a[1] + drive,
            formant_a[0])
        formant_b[0], formant_b[1] = (
            0.947 * formant_b[0] - 0.035 * formant_b[1] + drive,
            formant_b[0])
        value = envelope * (0.45 * formant_a[0] + 0.18 * formant_b[0])
        samples.append(max(-0.95, min(0.95, value)))
    return tuple(samples)


def tonal_vowel_speech(frames: int = 300, seed: int = 5150) -> Tuple[float, ...]:
    """Stress material: a synthetic voiced vowel with a strong 1 kHz harmonic.

    This is still synthetic, but its narrow sustained harmonic is the
    speech-like condition most likely to cause a false notch activation.
    """
    noise = _lcg(seed)
    samples: List[float] = []
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        f0 = 200.0 + 9.0 * math.sin(2.0 * math.pi * 0.23 * time_s)
        envelope = 0.18 * (0.65 + 0.35 * math.sin(2.0 * math.pi * 1.7 * time_s) ** 2)
        harmonic = sum(
            (0.30 / harmonic_index) * math.sin(
                2.0 * math.pi * f0 * harmonic_index * time_s + 0.4 * harmonic_index)
            for harmonic_index in range(1, 9))
        samples.append(envelope * harmonic + 0.002 * next(noise))
    return tuple(samples)


def tone(frames: int, frequency_hz: int = 1000, amplitude: float = 0.09,
         seed: int = 7) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(amplitude * math.sin(2.0 * math.pi * frequency_hz * n / SAMPLE_RATE_HZ)
                 + 0.0005 * next(noise)
                 for n in range(frames * FRAME_SAMPLES))


def impulse(frames: int = 8) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = 0.5
    return tuple(values)


def step(frames: int = 12, onset_frame: int = 4) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[onset_frame * FRAME_SAMPLES:] = [0.25] * (
        len(values) - onset_frame * FRAME_SAMPLES)
    return tuple(values)


def sweep(frames_per_frequency: int = 12) -> Tuple[float, ...]:
    values: List[float] = []
    for frequency in FREQUENCIES_HZ:
        values.extend(tone(frames_per_frequency, frequency, 0.09,
                           seed=1000 + frequency))
    return tuple(values)


def rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(len(values), 1))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def mean_square(values: Sequence[float]) -> float:
    blocks = [values[index:index + FRAME_SAMPLES]
              for index in range(0, len(values), FRAME_SAMPLES)]
    return sum(sum(value * value for value in block) / FRAME_SAMPLES
               for block in blocks) / max(len(blocks), 1)


def tone_to_total_db(values: Sequence[float], frequency_hz: int) -> float:
    total = mean_square(values)
    tone_power_value = tone_power(values, frequency_hz)
    return 10.0 * math.log10(max(tone_power_value, 1e-30) / max(total, 1e-30))


def closed_loop(controller: AdaptiveNotchController,
                program: Sequence[float], loop_gain: float,
                feedback_delay_hz: int = 1000, resonance: float = 0.96,
                resonance_gain: float = 0.04,
                pre_saturation: Optional[float] = None) -> Dict[str, Any]:
    """Frame-causal recursive loop: playback returns through a resonator."""
    omega = 2.0 * math.pi * feedback_delay_hz / SAMPLE_RATE_HZ
    coefficient = 2.0 * resonance * math.cos(omega)
    decay = resonance * resonance
    state_a = [0.0, 0.0]
    history: List[float] = [0.0] * FRAME_SAMPLES
    output: List[float] = []
    speech_rms = rms(program[:len(program) // 2])
    rejected = 0
    nonfinite = 0
    for frame_index in range(0, len(program), FRAME_SAMPLES):
        source = program[frame_index:frame_index + FRAME_SAMPLES]
        mic: List[float] = []
        for sample, feedback_sample in zip(source, history):
            resonator = feedback_sample + coefficient * state_a[0] - decay * state_a[1]
            state_a[1], state_a[0] = state_a[0], resonator
            value = sample + loop_gain * resonance_gain * resonator
            if pre_saturation is not None:
                value = pre_saturation * math.tanh(value / pre_saturation)
            mic.append(value)
        result = controller.process(tuple(mic))
        if result.status is not Status.OK:
            rejected += 1
            playback = (0.0,) * FRAME_SAMPLES
        else:
            playback = result.samples
        output.extend(playback)
        history = list(playback)
        for value in playback:
            if not math.isfinite(value):
                nonfinite += 1
    tail = output[-FRAME_SAMPLES * 10:]
    return {
        "loop_gain": loop_gain,
        "tail_rms": rms(tail),
        "tail_db_relative_to_program": 20.0 * math.log10(
            max(rms(tail), 1e-30) / max(speech_rms, 1e-30)),
        "peak_abs_output": peak(output),
        "rejected_frames": rejected,
        "nonfinite_frames": nonfinite,
        "activations": controller.state.activation_count,
        "releases": controller.state.release_count,
    }


def _frames(samples: Sequence[float]) -> List[Tuple[float, ...]]:
    return [tuple(samples[index:index + FRAME_SAMPLES])
            for index in range(0, len(samples), FRAME_SAMPLES)]


def _count_active(results: Sequence[ProcessResult]) -> int:
    return sum(1 for result in results if result.detected_hz)


def build_report() -> Dict[str, Any]:
    """Run every deterministic condition and return a canonical report object."""
    fixture_spec = {
        "contract": CONTRACT_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "frequencies_hz": list(FREQUENCIES_HZ),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "default_config": DEFAULT_CONFIG,
        "synthetic_seeds": {"speech": 20261028, "tonal_vowel": 5150,
                            "tone": 7, "sweep": 1000},
        "loop": {"feedback_delay_samples": FRAME_SAMPLES,
                 "resonator_hz": 1000, "resonance": 0.96,
                 "resonance_gain": 0.04},
    }
    speech = synthetic_speech(300)
    tone_only = tone(100)
    injection = tuple(
        speech[index] + (0.035 * math.sin(2.0 * math.pi * 1000 * index / SAMPLE_RATE_HZ)
                         if FRAME_SAMPLES * 100 <= index < FRAME_SAMPLES * 200 else 0.0)
        for index in range(len(speech)))

    silence_controller = AdaptiveNotchController(config_with())
    silence_result, silence_samples = silence_controller.process_stream((0.0,) * (FRAME_SAMPLES * 40))

    impulse_controller = AdaptiveNotchController(config_with())
    impulse_status, impulse_samples = impulse_controller.process_stream(impulse())
    impulse_peak_index = max(range(len(impulse_samples)),
                             key=lambda index: abs(impulse_samples[index]))

    step_controller = AdaptiveNotchController(config_with())
    step_status, step_samples = step_controller.process_stream(step())
    step_onset = 4 * FRAME_SAMPLES
    crossing = next((index - step_onset for index in range(step_onset, len(step_samples))
                     if abs(step_samples[index]) >= 0.025), len(step_samples))

    attack_controller = AdaptiveNotchController(config_with())
    tone_start_frame = 20
    tone_end_frame = 120
    attack_source = ((0.0,) * (FRAME_SAMPLES * tone_start_frame) + tone_only
                     + (0.0,) * (FRAME_SAMPLES * 40))
    attack_results = [attack_controller.process(frame)
                      for frame in _frames(attack_source)]
    attack_samples = tuple(value for result in attack_results for value in result.samples)
    attack_status = next((result.status for result in attack_results
                          if result.status is not Status.OK), Status.OK)
    active_flags = [bool(result.active_hz) for result in attack_results]
    activated = next((index for index in range(tone_start_frame, tone_end_frame)
                      if active_flags[index]), None)
    deactivated = next((index for index in range(tone_end_frame, len(active_flags))
                        if not active_flags[index]), None)

    sweep_samples: List[float] = []
    activated_frequencies = 0
    per_frequency: List[Dict[str, Any]] = []
    for frequency in FREQUENCIES_HZ:
        sweep_controller = AdaptiveNotchController(config_with())
        chunk = tone(12, frequency, 0.09, 1000 + frequency)
        status, output = sweep_controller.process_stream(chunk)
        if status is not Status.OK:
            raise RuntimeError(f"sweep failed at {frequency} Hz: {status}")
        sweep_samples.extend(output)
        segment = output[-FRAME_SAMPLES * 4:]
        activated_this_frequency = sweep_controller.state.activation_count > 0
        activated_frequencies += int(activated_this_frequency)
        per_frequency.append({
            "frequency_hz": frequency,
            "gain": round(rms(segment) / 0.09, 6),
            "active_notches": len(sweep_controller.state.notches),
            "activated": activated_this_frequency,
        })

    speech_notch_only = AdaptiveNotchController(config_with())
    speech_status, speech_output = speech_notch_only.process_stream(speech)
    speech_results = [speech_notch_only.process(frame) for frame in _frames(speech)]

    speech_margin = AdaptiveNotchController(config_with(gain_reduction_db=3.0))
    margin_status, margin_output = speech_margin.process_stream(speech)

    tonal_speech = tonal_vowel_speech()
    tonal_controller = AdaptiveNotchController(config_with())
    tonal_status, tonal_output = tonal_controller.process_stream(tonal_speech)

    injection_controller = AdaptiveNotchController(config_with(gain_reduction_db=3.0))
    injection_status, injection_output = injection_controller.process_stream(injection)
    injection_tone_start = 100
    injection_tone_end = 200
    tone_region = injection[FRAME_SAMPLES * injection_tone_start:
                            FRAME_SAMPLES * injection_tone_end]
    tone_out_region = injection_output[FRAME_SAMPLES * injection_tone_start:
                                       FRAME_SAMPLES * injection_tone_end]
    clean_in_region = injection[:FRAME_SAMPLES * injection_tone_start]
    clean_out_region = injection_output[:FRAME_SAMPLES * injection_tone_start]
    activation_frames = [
        int(event.split("@")[1].split(":")[0])
        for event in injection_controller.state.transitions
        if "->active" in event
    ]
    tone_ratio_before = tone_to_total_db(tone_region, 1000)
    tone_ratio_after = tone_to_total_db(tone_out_region, 1000)
    clean_ratio_before = tone_to_total_db(clean_in_region, 1000)
    clean_ratio_after = tone_to_total_db(clean_out_region, 1000)
    tone_power_before_db = _db(tone_power(tone_region, 1000))
    tone_power_after_db = _db(tone_power(tone_out_region, 1000))

    loop_program = synthetic_speech(200) + (0.0,) * (FRAME_SAMPLES * 100)
    loop_results: Dict[str, Any] = {}
    for gain in (1.05, 1.15, 1.30):
        controls: Dict[str, Dict[str, Any]] = {}
        for name, controller in (
            ("identity", AdaptiveNotchController(config_with(profile="fixed_only"))),
            ("fixed_margin", AdaptiveNotchController(config_with(profile="fixed_only",
                                                                 gain_reduction_db=5.0,
                                                                 recovery_frames=2000))),
            ("notch_only", AdaptiveNotchController(config_with())),
            ("notch_plus_margin", AdaptiveNotchController(config_with(gain_reduction_db=3.0))),
            ("notch_plus_saturation", AdaptiveNotchController(config_with(
                gain_reduction_db=3.0, saturation="tanh", saturation_threshold=0.8))),
        ):
            controls[name] = closed_loop(controller, loop_program, gain)
        loop_results[str(gain)] = controls

    numerical_controller = AdaptiveNotchController(config_with())
    before_state = numerical_controller.state.digest()
    nonfinite_result = numerical_controller.process((float("nan"),) * FRAME_SAMPLES)
    after_state = numerical_controller.state.digest()
    out_of_range_result = numerical_controller.process((9.0,) * FRAME_SAMPLES)
    short_result = numerical_controller.process((0.0,) * 159)

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/adaptive-feedback-notch-report/0.1",
        "contract": CONTRACT_ID,
        "scope": "synthetic model-free DSP fixture; no real audio, device or release claim",
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": SOURCE_PINS,
        "config": DEFAULT_CONFIG,
        "results": {
            "silence": {
                "status": silence_result.value,
                "activations": silence_controller.state.activation_count,
                "peak_abs_output": peak(silence_samples),
                "output_digest": tensor_digest(silence_samples),
            },
            "impulse": {
                "status": impulse_status.value,
                "peak_index": impulse_peak_index,
                "peak_abs_output": peak(impulse_samples),
                "output_digest": tensor_digest(impulse_samples),
            },
            "step": {
                "status": step_status.value,
                "crossing_samples": crossing,
                "peak_abs_output": peak(step_samples),
                "output_digest": tensor_digest(step_samples),
            },
            "sweep": {
                "frames_per_frequency": 12,
                "min_gain": min(item["gain"] for item in per_frequency),
                "max_gain": max(item["gain"] for item in per_frequency),
                "activated_frequencies": activated_frequencies,
                "per_frequency": per_frequency,
                "output_digest": tensor_digest(sweep_samples),
            },
            "attack_release": {
                "status": attack_status.value,
                "tone_start_frame": tone_start_frame,
                "tone_end_frame": tone_end_frame,
                "attack_frames": None if activated is None else activated - tone_start_frame,
                "release_frames": None if deactivated is None else deactivated - tone_end_frame,
                "activations": attack_controller.state.activation_count,
                "releases": attack_controller.state.release_count,
                "transitions": attack_controller.state.transitions[:8],
                "output_digest": tensor_digest(attack_samples),
            },
            "clean_speech": {
                "status": speech_status.value,
                "frames": len(speech) // FRAME_SAMPLES,
                "false_activations": speech_notch_only.state.activation_count,
                "false_activation_rate_per_minute": round(
                    speech_notch_only.state.activation_count * 600.0 /
                    (len(speech) // FRAME_SAMPLES), 3),
                "active_frames": speech_notch_only.state.active_frames,
                "gain_margin_activations": speech_margin.state.activation_count,
                "gain_margin_output_digest": tensor_digest(margin_output),
                "output_digest": tensor_digest(speech_output),
            },
            "tonal_vowel_stress": {
                "status": tonal_status.value,
                "frames": len(tonal_speech) // FRAME_SAMPLES,
                "false_activations": tonal_controller.state.activation_count,
                "false_activation_rate_per_minute": round(
                    tonal_controller.state.activation_count * 600.0 /
                    (len(tonal_speech) // FRAME_SAMPLES), 3),
                "active_frames": tonal_controller.state.active_frames,
                "output_digest": tensor_digest(tonal_output),
            },
            "tone_artifacts": {
                "status": injection_status.value,
                "injected_frequency_hz": 1000,
                "injected_amplitude": 0.035,
                "activations_in_tone_region": sum(
                    1 for frame in activation_frames
                    if injection_tone_start <= frame < injection_tone_end),
                "false_activations_clean_region": sum(
                    1 for frame in activation_frames
                    if frame < injection_tone_start),
                "tone_to_total_db_before": round(tone_ratio_before, 3),
                "tone_to_total_db_after": round(tone_ratio_after, 3),
                "tone_power_db_before": round(tone_power_before_db, 3),
                "tone_power_db_after": round(tone_power_after_db, 3),
                "tone_absolute_db_reduction": round(
                    tone_power_before_db - tone_power_after_db, 3),
                "clean_region_tone_db_before": round(clean_ratio_before, 3),
                "clean_region_tone_db_after": round(clean_ratio_after, 3),
                "output_digest": tensor_digest(injection_output),
            },
            "loop_stability": loop_results,
            "invalid_controls": {
                "nonfinite_status": nonfinite_result.status.value,
                "out_of_range_status": out_of_range_result.status.value,
                "short_frame_status": short_result.status.value,
                "state_unchanged": before_state == after_state,
            },
        },
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
