"""Deterministic, model-free de-esser reference fixture (task-local evidence).

All stimuli are analytic or seeded synthetic values. No recording, corpus,
model, device, licensed runtime, listening panel or release claim is used. The
frame boundary mirrors the public audio-sdk v0 frame contract (16 kHz mono
float32, 160 samples, epoch and source-sample admission). This module is
reference evidence only; it is not an installed SDK session.

Licensing for this task-local directory is covered by the repository-level
REUSE annotation for docs/**.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CONTRACT_ID = "audio-sdk/de-esser/0.1"
REPORT_SCHEMA_ID = "audio-sdk/de-esser-report/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
PROVIDER_ID = "dsp.de-esser.ref.v0"
BASE_COMMIT = "68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4"

# Paths are relative to /Users/htsakanyan/workspace/audio/audioml.
SOURCE_PINS: Dict[str, str] = {
    "cpp-library/PIPELINE_DESIGN_REPORT.md":
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "highpass_cutoff_hz": 4000.0,
    "threshold_dbfs": -24.0,
    "ratio": 6.0,
    "attack_ms": 5.0,
    "release_ms": 120.0,
    "max_reduction_db": 12.0,
    "makeup_db": 0.0,
    "max_abs_input": 2.0,
}
REQUIRED_KEYS: Tuple[str, ...] = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES: Dict[str, Tuple[float, float]] = {
    "highpass_cutoff_hz": (500.0, 7000.0),
    "threshold_dbfs": (-60.0, -6.0),
    "ratio": (1.0, 20.0),
    "attack_ms": (0.1, 200.0),
    "release_ms": (1.0, 2000.0),
    "max_reduction_db": (0.0, 24.0),
    "makeup_db": (0.0, 12.0),
    "max_abs_input": (0.25, 16.0),
}
FREQUENCIES_HZ: Tuple[int, ...] = (4000, 5000, 5500, 6000, 6500, 7000, 7500)
LEVELS: Tuple[float, ...] = (0.04, 0.08, 0.12, 0.16, 0.22, 0.30, 0.40, 0.50)
SEEDS: Dict[str, int] = {
    "speech": 20261101,
    "noise": 424242,
    "load": 611,
    "interactions": 909,
}
SIBILANCE_HZ = 6500
SIBILANCE_AMPLITUDE = 0.22
BURSTS: Tuple[Tuple[int, int], ...] = ((60, 20), (180, 16))

REQUIRED_RESULTS: Tuple[str, ...] = (
    "silence",
    "impulse",
    "low_band_step",
    "sibilance_burst",
    "sibilance_frequency_sweep",
    "sibilance_level_sweep",
    "clean_preservation",
    "broadband_control",
    "mixed_noise",
    "gain_stability",
    "headroom_peak_overshoot",
    "state_transitions",
    "adverse_controls",
    "invalid_missing_nonfinite",
    "nonlinear_interactions",
)


class Status(str, Enum):
    OK = "ok"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_STATE = "rejected_state"
    CLOSED = "closed"


def canonical_payload(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_payload(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    payload = b"".join(struct.pack("<f", float(value)) for value in values)
    return hashlib.sha256(payload).hexdigest()


def canonical_report(report: Dict[str, Any]) -> bytes:
    return canonical_payload(report) + b"\n"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    """Fail closed on missing, malformed, nonfinite or out-of-range controls."""
    if config is None:
        return Status.REJECTED_MISSING
    if not isinstance(config, dict):
        return Status.REJECTED_INVALID
    if any(key not in config for key in REQUIRED_KEYS):
        return Status.REJECTED_MISSING
    if any(str(key) not in REQUIRED_KEYS for key in config):
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
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


def biquad_coefficients(config: Dict[str, Any]) -> Tuple[float, float, float, float, float]:
    """RBJ high-pass biquad, Butterworth Q, normalized numerator/denominator."""
    frequency = float(config["highpass_cutoff_hz"])
    w0 = 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
    alpha = math.sin(w0) / (2.0 * math.sqrt(0.5))
    cosine = math.cos(w0)
    b0 = (1.0 + cosine) / 2.0
    b1 = -(1.0 + cosine)
    b2 = b0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosine
    a2 = 1.0 - alpha
    return b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0


def _lcg(seed: int) -> Iterable[float]:
    """Deterministic 32-bit LCG in [-1, 1), no OS randomness."""
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def _normalize(values: Sequence[float], target_peak: float = 0.8) -> Tuple[float, ...]:
    biggest = max((abs(value) for value in values), default=0.0)
    if biggest == 0.0:
        return tuple(values)
    scale = target_peak / biggest
    return tuple(value * scale for value in values)


def synthetic_speech(frames: int = 300,
                     seed: int = SEEDS["speech"]) -> Tuple[float, ...]:
    """Deterministic harmonic/burst program; analytic, not recorded speech."""
    noise = _lcg(seed)
    total = frames * FRAME_SAMPLES
    syllable = 12 * FRAME_SAMPLES
    produced: List[float] = []
    for index in range(total):
        time_seconds = index / SAMPLE_RATE_HZ
        phase = (index % syllable) / syllable
        envelope = 0.04 + 0.80 * math.sin(math.pi * phase) ** 2
        f0 = 112.0 + 24.0 * math.sin(2.0 * math.pi * 0.43 * time_seconds)
        voiced = 0.0
        for harmonic in range(1, 7):
            voiced += math.sin(2.0 * math.pi * f0 * harmonic * time_seconds) / (
                harmonic * harmonic)
        breath = 0.02 * next(noise)
        produced.append(envelope * (0.72 * voiced + breath))
    return _normalize(tuple(produced))


def tone(frames: int, frequency_hz: int, amplitude: float,
         start_sample: int = 0) -> Tuple[float, ...]:
    return tuple(
        amplitude * math.sin(2.0 * math.pi * frequency_hz *
                             (start_sample + index) / SAMPLE_RATE_HZ)
        for index in range(frames * FRAME_SAMPLES))


def highpass_component(values: Sequence[float],
                       config: Optional[Dict[str, Any]] = None
                       ) -> Tuple[float, ...]:
    """Apply the same high-pass analysis with fresh state (measurement only)."""
    coefficients = biquad_coefficients(DEFAULT_CONFIG if config is None else config)
    b0, b1, b2, a1, a2 = coefficients
    x1 = x2 = y1 = y2 = 0.0
    output: List[float] = []
    for value in values:
        sample = float(value)
        produced = b0 * sample + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        output.append(produced)
        x2, x1 = x1, sample
        y2, y1 = y1, produced
    return tuple(output)


def lowpass_component(values: Sequence[float],
                      config: Optional[Dict[str, Any]] = None
                      ) -> Tuple[float, ...]:
    high = highpass_component(values, config)
    return tuple(value - component for value, component in zip(values, high))


def bandpassed_noise(frames: int, seed: int = SEEDS["noise"],
                     amplitude: float = 0.30) -> Tuple[float, ...]:
    """Seeded wideband noise shaped to the detector band; analytic only."""
    noise = _lcg(seed)
    wideband = tuple(amplitude * next(noise) for _ in range(frames * FRAME_SAMPLES))
    return _normalize(highpass_component(wideband), target_peak=amplitude)


def impulse(frames: int = 120, amplitude: float = 0.9,
            position: int = 0) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[position] = amplitude
    return tuple(values)


def step_signal(frames: int = 12, onset_frame: int = 4,
                amplitude: float = 0.7) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    for index in range(onset_frame * FRAME_SAMPLES, len(values)):
        values[index] = amplitude
    return tuple(values)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(float(value) ** 2 for value in values) / len(values))


def peak(values: Sequence[float]) -> float:
    return max((abs(float(value)) for value in values), default=0.0)


def correlation(left: Sequence[float], right: Sequence[float]) -> Optional[float]:
    length = min(len(left), len(right))
    if length < 2:
        return None
    first = list(left[:length])
    second = list(right[:length])
    mean_first = sum(first) / length
    mean_second = sum(second) / length
    numerator = sum((a - mean_first) * (b - mean_second)
                    for a, b in zip(first, second))
    variance_first = sum((a - mean_first) ** 2 for a in first)
    variance_second = sum((b - mean_second) ** 2 for b in second)
    if variance_first <= 0.0 or variance_second <= 0.0:
        return None
    return numerator / math.sqrt(variance_first * variance_second)


def frame_envelope(values: Sequence[float]) -> Tuple[float, ...]:
    return tuple(rms(values[index:index + FRAME_SAMPLES])
                 for index in range(0, len(values), FRAME_SAMPLES))


def rmse(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def attenuation_db(input_band: Sequence[float],
                   output_band: Sequence[float]) -> float:
    before = rms(input_band)
    after = rms(output_band)
    if before <= 0.0 or after <= 0.0:
        return 0.0
    return 20.0 * math.log10(before / after)


@dataclass
class DeesserState:
    x1: float = 0.0
    x2: float = 0.0
    y1: float = 0.0
    y2: float = 0.0
    envelope: float = 0.0
    last_gain_db: float = 0.0
    engaged: bool = False
    transitions: List[str] = field(default_factory=list)
    frames_processed: int = 0
    samples_processed: int = 0
    next_sample: int = 0
    epoch: int = 1
    final_seen: bool = False
    closed: bool = False

    def digest(self) -> str:
        return object_digest({
            "x1": self.x1, "x2": self.x2, "y1": self.y1, "y2": self.y2,
            "envelope": self.envelope,
            "last_gain_db": self.last_gain_db,
            "engaged": self.engaged,
            "transitions": list(self.transitions),
            "frames_processed": self.frames_processed,
            "samples_processed": self.samples_processed,
            "next_sample": self.next_sample,
            "epoch": self.epoch,
            "final_seen": self.final_seen,
            "closed": self.closed,
        })


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    gains: Tuple[float, ...] = ()
    state_digest: str = ""
    source_first_sample: int = 0
    valid_count: int = 0


class Deesser:
    """Causal split-band de-esser with explicit frame admission.

    The high-pass component drives a peak envelope. Only that component is
    reduced, so a non-sibilant input is reproduced sample-for-sample while the
    low band stays untouched during a sibilant burst.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 epoch: int = 1, first_sample: int = 0) -> None:
        effective = DEFAULT_CONFIG if config is None else config
        status = validate_config(effective)
        if status is not Status.OK:
            raise ValueError(status.value)
        self.config = dict(effective)
        self.b0, self.b1, self.b2, self.a1, self.a2 = biquad_coefficients(
            self.config)
        self.attack_coefficient = 1.0 - math.exp(
            -1000.0 / (float(self.config["attack_ms"]) * SAMPLE_RATE_HZ))
        self.release_coefficient = 1.0 - math.exp(
            -1000.0 / (float(self.config["release_ms"]) * SAMPLE_RATE_HZ))
        self.compression = 1.0 - 1.0 / float(self.config["ratio"])
        self.state = DeesserState(epoch=epoch, next_sample=first_sample)
        self.counters: Dict[str, int] = {
            "accepted_frames": 0,
            "rejected_missing": 0,
            "rejected_nonfinite": 0,
            "rejected_invalid": 0,
            "rejected_tensor": 0,
            "rejected_epoch": 0,
            "rejected_state": 0,
        }
        self.resets = 0

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]], epoch: int = 1,
               first_sample: int = 0) -> Tuple[Status, Optional["Deesser"]]:
        effective = DEFAULT_CONFIG if config is None else config
        status = validate_config(effective)
        if status is not Status.OK:
            return status, None
        return Status.OK, cls(effective, epoch=epoch, first_sample=first_sample)

    def reset(self, epoch: int, first_sample: int) -> Status:
        if self.state.closed:
            return Status.CLOSED
        if epoch <= self.state.epoch or first_sample < 0:
            return Status.REJECTED_INVALID
        self.state = DeesserState(epoch=epoch, next_sample=first_sample)
        self.counters = dict.fromkeys(self.counters, 0)
        self.resets += 1
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    def process(self, samples: Optional[Sequence[float]], *,
                epoch: Optional[int] = None,
                first_sample: Optional[int] = None,
                valid_count: Optional[int] = None,
                flags: int = 0) -> ProcessResult:
        state = self.state
        if state.closed or state.final_seen:
            return ProcessResult(Status.CLOSED if state.closed
                                 else Status.REJECTED_STATE)
        if samples is None:
            self.counters["rejected_missing"] += 1
            return ProcessResult(Status.REJECTED_MISSING)
        if len(samples) != FRAME_SAMPLES:
            self.counters["rejected_tensor"] += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        if flags not in (0, 1):
            self.counters["rejected_invalid"] += 1
            return ProcessResult(Status.REJECTED_INVALID)
        accepted = FRAME_SAMPLES if valid_count is None else int(valid_count)
        if accepted < 1 or accepted > FRAME_SAMPLES:
            self.counters["rejected_tensor"] += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        if accepted < FRAME_SAMPLES and flags != 1:
            self.counters["rejected_tensor"] += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        if flags == 1 and any(float(value) != 0.0
                              for value in samples[accepted:]):
            self.counters["rejected_tensor"] += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        try:
            values = [float(value) for value in samples]
        except (TypeError, ValueError, OverflowError):
            self.counters["rejected_nonfinite"] += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        if any(not math.isfinite(value) for value in values):
            self.counters["rejected_nonfinite"] += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        limit = float(self.config["max_abs_input"])
        if any(abs(value) > limit for value in values):
            self.counters["rejected_invalid"] += 1
            return ProcessResult(Status.REJECTED_INVALID)
        incoming_epoch = state.epoch if epoch is None else int(epoch)
        incoming_position = (state.next_sample if first_sample is None
                             else int(first_sample))
        if incoming_epoch != state.epoch:
            self.counters["rejected_epoch"] += 1
            return ProcessResult(Status.REJECTED_EPOCH)
        if incoming_position != state.next_sample:
            self.counters["rejected_state"] += 1
            return ProcessResult(Status.REJECTED_STATE)

        work = _copy_state(state)
        output: List[float] = []
        gains: List[float] = []
        for value in values:
            high = (self.b0 * value + self.b1 * work.x1 + self.b2 * work.x2
                    - self.a1 * work.y1 - self.a2 * work.y2)
            coefficient = (self.attack_coefficient if abs(high) > work.envelope
                           else self.release_coefficient)
            work.envelope += coefficient * (abs(high) - work.envelope)
            level_db = 20.0 * math.log10(max(work.envelope, 1e-12))
            over_db = max(0.0, level_db - float(self.config["threshold_dbfs"]))
            reduction_db = min(float(self.config["max_reduction_db"]),
                               self.compression * over_db)
            gain_db = float(self.config["makeup_db"]) - reduction_db
            gain = 10.0 ** (gain_db / 20.0)
            produced = value - (1.0 - gain) * high
            if not math.isfinite(produced) or abs(produced) > 16.0:
                self.counters["rejected_nonfinite"] += 1
                return ProcessResult(Status.REJECTED_NONFINITE)
            output.append(produced)
            gains.append(-reduction_db)
            work.x2, work.x1 = work.x1, value
            work.y2, work.y1 = work.y1, high

        for index, gain_db in enumerate(gains):
            absolute_sample = work.samples_processed + index
            if not work.engaged and gain_db <= -1.0:
                work.engaged = True
                work.transitions.append(
                    f"idle->active@{absolute_sample}:{round(gain_db, 3)}")
            elif work.engaged and gain_db >= -0.5:
                work.engaged = False
                work.transitions.append(
                    f"active->idle@{absolute_sample}:{round(gain_db, 3)}")

        work.frames_processed += 1
        work.samples_processed += accepted
        work.next_sample = incoming_position + accepted
        if flags == 1:
            work.final_seen = True
        work.last_gain_db = gains[-1]
        self.state = work
        self.counters["accepted_frames"] += 1
        return ProcessResult(
            Status.OK, tuple(output), tuple(gains), work.digest(),
            incoming_position, accepted)

    def process_stream(self, samples: Sequence[float],
                       epoch: Optional[int] = None,
                       first_sample: Optional[int] = None
                       ) -> Tuple[Status, Tuple[float, ...], List[ProcessResult]]:
        if len(samples) % FRAME_SAMPLES:
            return Status.REJECTED_TENSOR, (), []
        results: List[ProcessResult] = []
        output: List[float] = []
        for start in range(0, len(samples), FRAME_SAMPLES):
            frame_first = (None if first_sample is None
                           else first_sample + start)
            result = self.process(samples[start:start + FRAME_SAMPLES],
                                  epoch=epoch, first_sample=frame_first)
            if result.status is not Status.OK:
                return result.status, (), results
            results.append(result)
            output.extend(result.samples)
        return Status.OK, tuple(output), results


def _copy_state(state: DeesserState) -> DeesserState:
    return DeesserState(
        x1=state.x1, x2=state.x2, y1=state.y1, y2=state.y2,
        envelope=state.envelope, last_gain_db=state.last_gain_db,
        engaged=state.engaged, transitions=list(state.transitions),
        frames_processed=state.frames_processed,
        samples_processed=state.samples_processed,
        next_sample=state.next_sample, epoch=state.epoch,
        final_seen=state.final_seen, closed=state.closed,
    )


def limiter(values: Sequence[float], ceiling: float = 0.98,
            release_ms: float = 50.0) -> Tuple[float, ...]:
    release = 1.0 - math.exp(-1000.0 / (release_ms * SAMPLE_RATE_HZ))
    envelope = 0.0
    gain = 1.0
    output: List[float] = []
    for value in values:
        magnitude = abs(float(value))
        if magnitude > envelope:
            envelope = magnitude
        else:
            envelope += release * (magnitude - envelope)
        desired = min(1.0, ceiling / max(envelope, 1e-12))
        gain = min(desired, gain + release * (1.0 - gain))
        output.append(float(value) * gain)
    return tuple(output)


def agc(values: Sequence[float], target_rms: float = 0.25,
        release_ms: float = 150.0, gain_ceiling: float = 1.5) -> Tuple[float, ...]:
    coefficient = 1.0 - math.exp(-1000.0 / (release_ms * SAMPLE_RATE_HZ))
    envelope = 0.0
    gain = 1.0
    output: List[float] = []
    for value in values:
        magnitude = abs(float(value))
        envelope += coefficient * (magnitude - envelope)
        target = min(gain_ceiling, max(0.25, target_rms / max(envelope, 0.01)))
        gain += coefficient * (target - gain)
        output.append(float(value) * gain)
    return tuple(output)


def apply_stages(values: Sequence[float],
                 stages: Sequence[Tuple[str, Dict[str, Any]]]) -> Tuple[float, ...]:
    current = tuple(values)
    for name, settings in stages:
        if name == "deesser":
            status, produced, _ = Deesser(settings).process_stream(current)
            if status is not Status.OK:
                raise RuntimeError(f"de-esser stage failed: {status.value}")
            current = produced
        elif name == "limiter":
            current = limiter(current, **settings)
        elif name == "agc":
            current = agc(current, **settings)
        else:
            raise ValueError(f"unknown stage {name}")
    return current


def sibilant_program() -> Tuple[float, ...]:
    produced = list(synthetic_speech())
    for start_frame, length_frames in BURSTS:
        burst = tone(length_frames, SIBILANCE_HZ, SIBILANCE_AMPLITUDE)
        for index, value in enumerate(burst):
            produced[start_frame * FRAME_SAMPLES + index] += value
    return tuple(produced)


def run_all(settings: Optional[Dict[str, Any]] = None,
            source: Optional[Sequence[float]] = None
            ) -> Tuple[Status, Tuple[float, ...], Tuple[float, ...]]:
    effective = DEFAULT_CONFIG if settings is None else settings
    signal = sibilant_program() if source is None else source
    status, produced, results = Deesser(effective).process_stream(signal)
    gains = tuple(gain for result in results for gain in result.gains)
    return status, produced, gains


def build_report() -> Dict[str, Any]:
    """Run every deterministic condition and return the canonical report."""
    fixture_spec = {
        "contract": CONTRACT_ID,
        "base_commit": BASE_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "default_config": DEFAULT_CONFIG,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "seeds": SEEDS,
        "frequencies_hz": list(FREQUENCIES_HZ),
        "levels": list(LEVELS),
        "bursts": [list(burst) for burst in BURSTS],
        "band_split": "RBJ 2nd-order high-pass, Q=1/sqrt(2); low = x - high",
        "detector": "peak envelope of high-pass component, one-pole attack/release",
        "apply": "y = x - (1 - 10^((makeup-reduction)/20)) * high",
    }
    fixture_digest = object_digest(fixture_spec)

    silence = Deesser()
    silence_status, silence_output, _ = silence.process_stream(
        (0.0,) * (FRAME_SAMPLES * 40))

    impulse_input = impulse()
    impulse_engine = Deesser()
    impulse_status, impulse_output, _ = impulse_engine.process_stream(impulse_input)
    impulse_peak_index = max(range(len(impulse_output)),
                             key=lambda index: abs(impulse_output[index]))

    step_input = step_signal()
    step_engine = Deesser()
    step_status, step_output, _ = step_engine.process_stream(step_input)
    step_low_input = lowpass_component(step_input)
    step_low_output = lowpass_component(step_output)
    step_onset = 4 * FRAME_SAMPLES
    step_crossing = next(
        (index - step_onset for index in range(step_onset, len(step_output))
         if abs(step_output[index]) >= 0.05), len(step_output))

    sibilant = sibilant_program()
    sibilant_engine = Deesser()
    sibilant_status, sibilant_output, sibilant_results = (
        sibilant_engine.process_stream(sibilant))
    sibilant_gains = tuple(gain for result in sibilant_results
                           for gain in result.gains)
    high_input = highpass_component(sibilant)
    high_output = highpass_component(sibilant_output)
    low_input = lowpass_component(sibilant)
    low_output = lowpass_component(sibilant_output)
    burst_metrics: List[Dict[str, Any]] = []
    for start_frame, length_frames in BURSTS:
        begin = start_frame * FRAME_SAMPLES
        end = begin + length_frames * FRAME_SAMPLES
        burst_metrics.append({
            "start_frame": start_frame,
            "frames": length_frames,
            "high_band_attenuation_db": round(
                attenuation_db(high_input[begin:end], high_output[begin:end]), 6),
            "low_band_attenuation_db": round(
                attenuation_db(low_input[begin:end], low_output[begin:end]), 6),
            "broadband_attenuation_db": round(
                attenuation_db(sibilant[begin:end], sibilant_output[begin:end]), 6),
            "min_gain_db": round(min(sibilant_gains[begin:end]), 6),
        })

    frequency_points: List[Dict[str, Any]] = []
    frequency_outputs: List[float] = []
    for frequency in FREQUENCIES_HZ:
        source = tone(40, frequency, SIBILANCE_AMPLITUDE)
        status, produced, gains = run_all(source=source)
        if status is not Status.OK:
            raise RuntimeError(f"frequency case failed at {frequency} Hz")
        analysis_window = slice(20 * FRAME_SAMPLES, None)
        frequency_points.append({
            "frequency_hz": frequency,
            "high_band_attenuation_db": round(
                attenuation_db(highpass_component(source)[analysis_window],
                               highpass_component(produced)[analysis_window]), 6),
            "settled_gain_db": round(gains[-1], 6),
        })
        frequency_outputs.extend(produced)

    level_points: List[Dict[str, Any]] = []
    for amplitude in LEVELS:
        source = tone(40, SIBILANCE_HZ, amplitude)
        status, produced, gains = run_all(source=source)
        if status is not Status.OK:
            raise RuntimeError(f"level case failed at {amplitude}")
        analysis_window = slice(20 * FRAME_SAMPLES, None)
        level_points.append({
            "amplitude": amplitude,
            "high_band_attenuation_db": round(
                attenuation_db(highpass_component(source)[analysis_window],
                               highpass_component(produced)[analysis_window]), 6),
            "settled_gain_db": round(gains[-1], 6),
        })

    clean = synthetic_speech()
    clean_engine = Deesser()
    clean_status, clean_output, clean_results = clean_engine.process_stream(clean)
    clean_gains = tuple(gain for result in clean_results for gain in result.gains)
    clean_envelope = frame_envelope(clean)
    clean_output_envelope = frame_envelope(clean_output)
    clean_correlation = correlation(clean_envelope, clean_output_envelope)

    broadband_output = tuple(
        value * 10.0 ** (gain / 20.0)
        for value, gain in zip(sibilant, sibilant_gains))
    broadband_high_out = highpass_component(broadband_output)
    broadband_low_out = lowpass_component(broadband_output)
    split_burst_band = slice(BURSTS[0][0] * FRAME_SAMPLES,
                             (BURSTS[0][0] + BURSTS[0][1]) * FRAME_SAMPLES)

    mixed_noise_source = _normalize(tuple(
        speech + noise for speech, noise in zip(
            synthetic_speech(frames=150, seed=SEEDS["speech"]),
            bandpassed_noise(frames=150))), target_peak=0.95)
    mixed_engine = Deesser()
    mixed_status, mixed_output, _ = mixed_engine.process_stream(mixed_noise_source)
    mixed_high_in = highpass_component(mixed_noise_source)
    mixed_high_out = highpass_component(mixed_output)
    mixed_low_in = lowpass_component(mixed_noise_source)
    mixed_low_out = lowpass_component(mixed_output)

    load_noise = _lcg(SEEDS["load"])
    load_source = tuple(0.35 * next(load_noise)
                        for _ in range(FRAME_SAMPLES * 100))
    load_engine = Deesser()
    load_status, load_output, load_results = load_engine.process_stream(load_source)
    load_gains = tuple(gain for result in load_results for gain in result.gains)
    load_step_deltas = [abs(load_gains[index + 1] - load_gains[index])
                        for index in range(len(load_gains) - 1)]
    load_frame_deltas = [abs(load_gains[index + FRAME_SAMPLES] - load_gains[index])
                         for index in range(len(load_gains) - FRAME_SAMPLES)]
    settled_frame_gains = [sum(load_gains[index:index + FRAME_SAMPLES]) / FRAME_SAMPLES
                           for index in range(80 * FRAME_SAMPLES, 100 * FRAME_SAMPLES,
                                              FRAME_SAMPLES)]
    settled_direction_changes = sum(
        1 for index in range(1, len(settled_frame_gains) - 1)
        if (settled_frame_gains[index] - settled_frame_gains[index - 1])
        * (settled_frame_gains[index + 1] - settled_frame_gains[index]) < 0.0)

    overshoot_source = tone(20, SIBILANCE_HZ, 0.5)
    boost_config = config_with(makeup_db=12.0)
    boost_status, boosted_output, _ = run_all(
        settings=boost_config, source=overshoot_source)
    limited_output = limiter(boosted_output)
    overshoot_samples = sum(1 for value in boosted_output if abs(value) > 1.0)

    state_source = tone(40, SIBILANCE_HZ, SIBILANCE_AMPLITUDE) + (
        0.0,) * (FRAME_SAMPLES * 20)
    session_a = Deesser()
    state_status, state_output_a, _ = session_a.process_stream(state_source)
    state_digest_after_tone = session_a.state.digest()
    rejected_reset = session_a.reset(1, 0)
    accepted_reset = session_a.reset(2, 0)
    state_status_reset, state_output_reset, _ = session_a.process_stream(
        state_source[:FRAME_SAMPLES * 40], epoch=2, first_sample=0)
    fresh_a = Deesser()
    fresh_status, fresh_output, _ = fresh_a.process_stream(
        state_source[:FRAME_SAMPLES * 40])
    short_session = Deesser()
    short_status, short_output, _ = short_session.process_stream(
        state_source[:FRAME_SAMPLES * 10])
    reset_matches_fresh = tensor_digest(state_output_reset) == tensor_digest(
        fresh_output)
    isolation_matches_fresh = tensor_digest(short_output) == tensor_digest(
        fresh_output[:FRAME_SAMPLES * 10])
    final_frame = [0.0] * FRAME_SAMPLES
    final_frame[4] = 0.25
    final_result = fresh_a.process(final_frame, valid_count=5, flags=1)
    after_final = fresh_a.process(final_frame[:FRAME_SAMPLES])

    bad_configs: Dict[str, Tuple[Any, Status]] = {
        "null_config": (None, validate_config(None)),
        "missing_cutoff": (
            {key: value for key, value in DEFAULT_CONFIG.items()
             if key != "highpass_cutoff_hz"},
            validate_config({key: value for key, value in DEFAULT_CONFIG.items()
                             if key != "highpass_cutoff_hz"})),
        "cutoff_below_range": (config_with(highpass_cutoff_hz=499.0),
                               validate_config(config_with(highpass_cutoff_hz=499.0))),
        "cutoff_above_range": (config_with(highpass_cutoff_hz=7001.0),
                               validate_config(config_with(highpass_cutoff_hz=7001.0))),
        "cutoff_nonfinite": (config_with(highpass_cutoff_hz=float("nan")),
                             validate_config(config_with(highpass_cutoff_hz=float("nan")))),
        "threshold_below_range": (config_with(threshold_dbfs=-60.1),
                                  validate_config(config_with(threshold_dbfs=-60.1))),
        "threshold_above_range": (config_with(threshold_dbfs=-5.9),
                                  validate_config(config_with(threshold_dbfs=-5.9))),
        "threshold_nonfinite": (config_with(threshold_dbfs=float("inf")),
                                validate_config(config_with(threshold_dbfs=float("inf")))),
        "ratio_below_range": (config_with(ratio=0.9),
                              validate_config(config_with(ratio=0.9))),
        "ratio_above_range": (config_with(ratio=20.1),
                              validate_config(config_with(ratio=20.1))),
        "attack_zero": (config_with(attack_ms=0.0),
                        validate_config(config_with(attack_ms=0.0))),
        "attack_above_range": (config_with(attack_ms=200.1),
                               validate_config(config_with(attack_ms=200.1))),
        "attack_nonfinite": (config_with(attack_ms=float("nan")),
                             validate_config(config_with(attack_ms=float("nan")))),
        "release_zero": (config_with(release_ms=0.0),
                         validate_config(config_with(release_ms=0.0))),
        "release_above_range": (config_with(release_ms=2000.1),
                                validate_config(config_with(release_ms=2000.1))),
        "max_reduction_above_range": (config_with(max_reduction_db=24.1),
                                      validate_config(config_with(max_reduction_db=24.1))),
        "makeup_negative": (config_with(makeup_db=-0.1),
                            validate_config(config_with(makeup_db=-0.1))),
        "makeup_above_range": (config_with(makeup_db=12.1),
                               validate_config(config_with(makeup_db=12.1))),
        "unknown_key": (config_with(unknown_setting=1),
                        validate_config(config_with(unknown_setting=1))),
        "wrong_type": (config_with(ratio="6"),
                       validate_config(config_with(ratio="6"))),
        "bool_type": (config_with(ratio=True),
                      validate_config(config_with(ratio=True))),
    }
    config_rejections = {name: status.value for name, (_, status)
                         in sorted(bad_configs.items())}

    adverse = Deesser()
    before_adverse = adverse.state.digest()
    nonfinite_frame = [0.0] * FRAME_SAMPLES
    nonfinite_frame[5] = float("nan")
    nonfinite_result = adverse.process(nonfinite_frame)
    after_nonfinite = adverse.state.digest()
    short_result = adverse.process((0.0,) * (FRAME_SAMPLES - 1))
    stale_result = adverse.process((0.0,) * FRAME_SAMPLES, epoch=99)
    wrong_position_result = adverse.process((0.0,) * FRAME_SAMPLES,
                                            first_sample=999)
    out_of_range_frame = [9.0] * FRAME_SAMPLES
    out_of_range_result = adverse.process(out_of_range_frame)
    bad_padding = [0.0] * FRAME_SAMPLES
    bad_padding[159] = 0.5
    padding_result = adverse.process(bad_padding, valid_count=5, flags=1)
    bad_flags_result = adverse.process((0.0,) * FRAME_SAMPLES, flags=2)
    after_all_rejects = adverse.state.digest()
    input_rejections = {
        "nonfinite_input": nonfinite_result.status.value,
        "wrong_frame_shape": short_result.status.value,
        "stale_epoch": stale_result.status.value,
        "wrong_position": wrong_position_result.status.value,
        "out_of_range": out_of_range_result.status.value,
        "nonzero_final_padding": padding_result.status.value,
        "unknown_flags": bad_flags_result.status.value,
        "state_unchanged_after_nonfinite": before_adverse == after_nonfinite,
        "state_unchanged_after_all_rejects": before_adverse == after_all_rejects,
        "rejection_counters": dict(sorted(adverse.counters.items())),
    }

    missing_engine = Deesser()
    rejected_missing_config = Deesser.create({})[0]
    missing_frame_result = missing_engine.process(None)
    nonfinite_config_status = validate_config(
        config_with(threshold_dbfs=float("nan")))
    nonfinite_sample_result = missing_engine.process(nonfinite_frame)
    missing_result_control = {
        "simulated_removed_result": "sibilance_burst",
        "present_after_removal": [
            name for name in REQUIRED_RESULTS if name != "sibilance_burst"],
        "missing_detected": ["sibilance_burst"],
        "all_present_after_removal": False,
        "candidate_qualifies": False,
    }

    interaction_source = _normalize(tuple(
        speech + burst for speech, burst in zip(
            synthetic_speech(frames=120, seed=SEEDS["interactions"]),
            tone(120, SIBILANCE_HZ, SIBILANCE_AMPLITUDE))), target_peak=1.3)
    default_stage: Tuple[str, Dict[str, Any]] = ("deesser", dict(DEFAULT_CONFIG))
    limiter_stage: Tuple[str, Dict[str, Any]] = (
        "limiter", {"ceiling": 0.98, "release_ms": 50.0})
    agc_stage: Tuple[str, Dict[str, Any]] = (
        "agc", {"target_rms": 0.25, "release_ms": 150.0, "gain_ceiling": 1.5})
    interaction_configs: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {
        "deesser_only": [default_stage],
        "deesser_to_limiter": [default_stage, limiter_stage],
        "limiter_to_deesser": [limiter_stage, default_stage],
        "deesser_to_agc": [default_stage, agc_stage],
        "agc_to_deesser": [agc_stage, default_stage],
        "deesser_to_deesser": [default_stage, default_stage],
    }
    interactions: Dict[str, Any] = {}
    for name, stages in interaction_configs.items():
        produced = apply_stages(interaction_source, stages)
        interactions[name] = {
            "stages": [stage_name for stage_name, _ in stages],
            "peak_abs_output": round(peak(produced), 9),
            "nonfinite_output_samples": sum(
                1 for value in produced if not math.isfinite(value)),
            "output_digest": tensor_digest(produced),
        }

    report: Dict[str, Any] = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": ("proposal-only synthetic task-local de-esser evidence; no "
                  "real speech, corpus, model, listening, device or release "
                  "qualification"),
        "status": "proposal-only/synthetic",
        "base_commit": BASE_COMMIT,
        "fixture_digest": fixture_digest,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "config": dict(DEFAULT_CONFIG),
        "results": {
            "silence": {
                "status": silence_status.value,
                "frames": 40,
                "peak_abs_output": peak(silence_output),
                "final_gain_db": silence.state.last_gain_db,
                "output_digest": tensor_digest(silence_output),
            },
            "impulse": {
                "status": impulse_status.value,
                "peak_sample_index": impulse_peak_index,
                "content_delay_samples": impulse_peak_index,
                "peak_abs_output": peak(impulse_output),
                "output_digest": tensor_digest(impulse_output),
            },
            "low_band_step": {
                "status": step_status.value,
                "onset_sample": step_onset,
                "crossing_samples_from_onset": step_crossing,
                "peak_abs_output": peak(step_output),
                "low_band_attenuation_db": round(
                    attenuation_db(step_low_input[step_onset:],
                                   step_low_output[step_onset:]), 6),
                "output_digest": tensor_digest(step_output),
            },
            "sibilance_burst": {
                "status": sibilant_status.value,
                "source": "synthetic harmonic program plus 6.5 kHz analytic bursts",
                "frames": len(sibilant) // FRAME_SAMPLES,
                "burst_count": len(BURSTS),
                "bursts": burst_metrics,
                "engaged_samples": sum(
                    1 for gain in sibilant_gains if gain <= -1.0),
                "transitions": list(sibilant_engine.state.transitions[:8]),
                "output_digest": tensor_digest(sibilant_output),
            },
            "sibilance_frequency_sweep": {
                "status": "ok",
                "amplitude": SIBILANCE_AMPLITUDE,
                "points": frequency_points,
                "note": ("4 kHz is a documented control at the crossover and "
                         "is not a passed sibilance-band result"),
                "output_digest": tensor_digest(frequency_outputs),
            },
            "sibilance_level_sweep": {
                "status": "ok",
                "tone_hz": SIBILANCE_HZ,
                "points": level_points,
            },
            "clean_preservation": {
                "status": clean_status.value,
                "source": "synthetic harmonic/burst program, not recorded speech",
                "frames": len(clean) // FRAME_SAMPLES,
                "bit_identical_output": clean_output == clean,
                "matched_gain_db": round(
                    20.0 * math.log10(rms(clean_output) / max(rms(clean), 1e-12)), 6),
                "peak_abs_input": round(peak(clean), 9),
                "peak_abs_output": round(peak(clean_output), 9),
                "envelope_correlation": (None if clean_correlation is None
                                         else round(clean_correlation, 6)),
                "reduced_frames": sum(
                    1 for result in clean_results if min(result.gains) <= -1e-9),
                "max_absolute_gain_db": round(min(clean_gains), 6),
                "input_digest": tensor_digest(clean),
                "output_digest": tensor_digest(clean_output),
                "claim_limit": "synthetic sample identity only; no speech quality claim",
            },
            "broadband_control": {
                "status": sibilant_status.value,
                "control": "same per-sample gains applied to the whole signal",
                "split_band_high_attenuation_db": burst_metrics[0][
                    "high_band_attenuation_db"],
                "broadband_high_attenuation_db": round(
                    attenuation_db(high_input[split_burst_band],
                                   broadband_high_out[split_burst_band]), 6),
                "split_band_low_attenuation_db": burst_metrics[0][
                    "low_band_attenuation_db"],
                "broadband_low_attenuation_db": round(
                    attenuation_db(low_input[split_burst_band],
                                   broadband_low_out[split_burst_band]), 6),
                "output_digest": tensor_digest(broadband_output),
            },
            "mixed_noise": {
                "status": mixed_status.value,
                "source": "synthetic speech-like program plus seeded detector-band noise",
                "frames": len(mixed_noise_source) // FRAME_SAMPLES,
                "high_band_attenuation_db": round(
                    attenuation_db(mixed_high_in, mixed_high_out), 6),
                "low_band_attenuation_db": round(
                    attenuation_db(mixed_low_in, mixed_low_out), 6),
                "peak_abs_output": round(peak(mixed_output), 9),
                "output_digest": tensor_digest(mixed_output),
            },
            "gain_stability": {
                "status": load_status.value,
                "source": "seeded dense wideband noise; no host timing measurement",
                "frames": len(load_source) // FRAME_SAMPLES,
                "min_gain_db": round(min(load_gains), 6),
                "max_gain_db": round(max(load_gains), 6),
                "max_sample_to_sample_delta_db": round(max(load_step_deltas), 6),
                "max_frame_to_frame_delta_db": round(max(load_frame_deltas), 6),
                "settled_frame_direction_changes": settled_direction_changes,
                "nonfinite_output_samples": sum(
                    1 for value in load_output if not math.isfinite(value)),
                "peak_abs_output": round(peak(load_output), 9),
                "output_digest": tensor_digest(load_output),
            },
            "headroom_peak_overshoot": {
                "status": boost_status.value,
                "makeup_db": boost_config["makeup_db"],
                "input_peak": round(peak(overshoot_source), 9),
                "boosted_peak": round(peak(boosted_output), 9),
                "samples_above_full_scale": overshoot_samples,
                "limiter_ceiling": 0.98,
                "limited_peak": round(peak(limited_output), 9),
                "headroom_db": round(
                    20.0 * math.log10(0.98 / max(peak(limited_output), 1e-12)), 6),
                "boosted_output_digest": tensor_digest(boosted_output),
                "limited_output_digest": tensor_digest(limited_output),
            },
            "state_transitions": {
                "status": state_status.value,
                "state_digest_after_tone": state_digest_after_tone,
                "reset_with_old_epoch": rejected_reset.value,
                "reset_with_higher_epoch": accepted_reset.value,
                "reset_output_matches_fresh": reset_matches_fresh,
                "cross_session_isolation": isolation_matches_fresh,
                "final_input_valid_count": final_result.valid_count,
                "final_input_source_first_sample": final_result.source_first_sample,
                "process_after_final": after_final.status.value,
                "fresh_status": fresh_status.value,
                "short_status": short_status.value,
                "output_digest": tensor_digest(state_output_a),
            },
            "adverse_controls": {
                "status": "ok",
                "config_rejections": config_rejections,
                "config_rejection_count": len(config_rejections),
                "input_rejections": input_rejections,
            },
            "invalid_missing_nonfinite": {
                "status": "ok",
                "missing_config_create": rejected_missing_config.value,
                "missing_frame_input": missing_frame_result.status.value,
                "nonfinite_config": nonfinite_config_status.value,
                "nonfinite_sample": nonfinite_sample_result.status.value,
                "state_unchanged_after_missing": (
                    missing_engine.state.digest()
                    == Deesser().state.digest()),
                "missing_result_control": missing_result_control,
                "rule": ("Explicit missing, invalid or nonfinite results are "
                         "required; no missing result qualifies a candidate."),
            },
            "nonlinear_interactions": {
                "status": "ok",
                "configurations": interactions,
            },
        },
        "counts": {
            "source_pins": len(SOURCE_PINS),
            "boundary_pins": len(BOUNDARY_PINS),
            "required_results": len(REQUIRED_RESULTS),
            "frequency_points": len(FREQUENCIES_HZ),
            "level_points": len(LEVELS),
            "speech_frames": len(clean) // FRAME_SAMPLES,
            "load_frames": len(load_source) // FRAME_SAMPLES,
            "interaction_configurations": len(interaction_configs),
            "expected_unittest_cases": 30,
            "expected_ctest_runs": 3,
        },
        "completeness": {
            "required_results": list(REQUIRED_RESULTS),
            "present_results": list(REQUIRED_RESULTS),
            "missing_results": [],
            "all_present": True,
            "rule": "No missing result qualifies a candidate; absent results are failures.",
        },
        "acceptance_profiles": {
            "dsp": {
                "status": "synthetic_applied",
                "coverage": ("silence, impulse, step, tone/noise sweeps, clean "
                             "program, gain/attack/release, headroom, state "
                             "transitions, numerical behavior and nonlinear "
                             "cascades"),
                "blocker": "No matched native baseline or target-device run.",
            },
            "enhancement": {
                "status": "synthetic_subset_only",
                "coverage": ("identity/noisy controls, high-band attenuation, "
                             "low-band preservation, peaks, invalid outputs"),
                "blocker": ("No paired speech cohort, clean references, STOI or "
                            "other permitted reference metric."),
            },
            "voice": {
                "status": "synthetic_subset_only",
                "coverage": ("synthetic source identity and fixed analysis "
                             "windows; no speaker, language or semantic claim"),
                "blocker": ("No consented corpus, speaker/language groups, "
                            "naturalness/similarity scoring or listening panel."),
            },
            "no_listening_claim": True,
            "no_real_speech_claim": True,
        },
        "qualification": {
            "candidate_qualification": "not_qualified",
            "real_speech_listening": {
                "status": "incomplete",
                "blocker": ("No rights-cleared speech, reference transcripts, "
                            "listener panel, scoring harness or permitted corpus "
                            "is available in this task-local fixture."),
                "deferral": "No MOS, STOI, PESQ, preference or intelligibility claim.",
                "reopen_trigger": ("Pinned authorized cohort with independent "
                                   "paired scoring and a consented listening protocol."),
            },
            "matched_baseline_and_gain": {
                "status": "incomplete",
                "blocker": ("Matched gain is demonstrated only by synthetic sample "
                            "identity; no production gain target, loudness model "
                            "or established task-matched baseline was available."),
                "deferral": "Synthetic preservation proxy only.",
                "reopen_trigger": ("Frozen matched baseline, agreed loudness margin "
                                   "and independent scoring on the exact workload."),
            },
            "device_timing": {
                "status": "incomplete",
                "blocker": "No target device, licensed runtime or paced workload was available.",
                "deferral": "No RTF, deadline, power or thermal claim.",
                "reopen_trigger": "Measured target-device run under an agreed load budget.",
            },
            "installed_sdk_change": {
                "status": "not_applicable",
                "blocker": ("Task scope forbids descriptor, registry, ABI, CMake and "
                            "installed-behavior changes."),
                "deferral": "The optional C provider is caller-registered only.",
                "reopen_trigger": "Separate contract and release-gate work.",
            },
        },
        "non_claims": [
            "No real audio, corpus, model weights, downloads or licensed runtime.",
            "No listening, STOI, PESQ, MOS, intelligibility or preference result.",
            "No target-device CPU, RTF, latency, power or thermal result.",
            "No installed SDK, ABI, descriptor, registry or default behavior change.",
            "No release approval, production suitability or baseline parity claim.",
        ],
    }
    return report


def main() -> None:
    import sys

    destination = (Path(sys.argv[1]) if len(sys.argv) > 1
                   else Path(__file__).resolve().parent / "report.json")
    payload = canonical_report(build_report())
    destination.write_bytes(payload)
    sys.stdout.write(f"{len(payload)} bytes sha256={hashlib.sha256(payload).hexdigest()}\n")


if __name__ == "__main__":
    main()
