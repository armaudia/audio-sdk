"""Deterministic, model-free feed-forward compressor DSP fixture.

Scope: task-local reference evidence only. All stimuli are generated from
analytic functions and fixed seeds; no recording, model, corpus, device,
licensed runtime or listening result is read or claimed. The frame API below
mirrors the public audio-sdk v0 frame boundary (16 kHz, mono f32, 160 samples,
epoch and source-sample admission) but is not itself an installed SDK session.
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

CONTRACT_ID = "audio-sdk/feed-forward-compressor/0.1"
REPORT_SCHEMA_ID = "audio-sdk/feed-forward-compressor-report/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
PROVIDER_ID = "dsp.feed-forward-compressor.ref.v0"
BASE_COMMIT = "0673cb354cceb66f2f71faf9af7703b5a5d2fcfa"

# Paths are relative to /Users/htsakanyan/workspace/audio/audioml.
SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "threshold_dbfs": -24.0,
    "ratio": 4.0,
    "attack_ms": 5.0,
    "release_ms": 120.0,
    "makeup_db": 0.0,
    "max_abs_input": 2.0,
}
REQUIRED_KEYS: Tuple[str, ...] = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES: Dict[str, Tuple[float, float]] = {
    "threshold_dbfs": (-60.0, 0.0),
    "ratio": (1.0, 20.0),
    "attack_ms": (0.1, 200.0),
    "release_ms": (1.0, 2000.0),
    "makeup_db": (0.0, 24.0),
    "max_abs_input": (0.25, 16.0),
}
FREQUENCIES_HZ: Tuple[int, ...] = tuple(range(200, 4001, 100))
AMPLITUDES: Tuple[float, ...] = tuple(
    round(0.02 + (0.95 - 0.02) * index / 99.0, 10) for index in range(100))
SEEDS: Dict[str, int] = {
    "speech": 20261101,
    "load": 611,
    "impulse": 17,
    "step": 19,
    "sweep": 1000,
    "interactions": 909,
}

REQUIRED_RESULTS: Tuple[str, ...] = (
    "silence", "impulse", "step", "amplitude_sweep", "frequency_response",
    "attack_release", "clean_speechlike", "load_control",
    "headroom_peak_overshoot", "state_transitions", "adverse_controls",
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
    missing = sorted(key for key in REQUIRED_KEYS if key not in config)
    if missing:
        return Status.REJECTED_MISSING
    unknown = sorted(str(key) for key in config if key not in REQUIRED_KEYS)
    if unknown:
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


def synthetic_speech(frames: int = 300, seed: int = SEEDS["speech"]) -> Tuple[float, ...]:
    """Deterministic speech-like harmonic/burst program; not recorded speech."""
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
        breath = 0.10 * next(noise)
        produced.append(envelope * (0.72 * voiced + breath))
    return _normalize(tuple(produced))


def dense_load(frames: int = 100, seed: int = SEEDS["load"]) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(0.55 * next(noise) for _ in range(frames * FRAME_SAMPLES))


def tone(frames: int, frequency_hz: int, amplitude: float,
         start_sample: int = 0) -> Tuple[float, ...]:
    return tuple(
        amplitude * math.sin(2.0 * math.pi * frequency_hz *
                             (start_sample + index) / SAMPLE_RATE_HZ)
        for index in range(frames * FRAME_SAMPLES))


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


def ideal_gain_db(amplitude: float, config: Dict[str, Any]) -> float:
    """Static gain law for a sinusoid of the given peak amplitude."""
    level_db = 20.0 * math.log10(max(float(amplitude), 1e-12))
    over_db = max(0.0, level_db - float(config["threshold_dbfs"]))
    reduction_db = (1.0 - 1.0 / float(config["ratio"])) * over_db
    return float(config["makeup_db"]) - reduction_db


@dataclass
class CompressorState:
    envelope: float = 0.0
    frames_processed: int = 0
    samples_processed: int = 0
    next_sample: int = 0
    epoch: int = 1
    engaged: bool = False
    last_gain_db: float = 0.0
    transitions: List[str] = field(default_factory=list)
    final_seen: bool = False
    closed: bool = False

    def digest(self) -> str:
        return object_digest({
            "envelope": self.envelope,
            "frames_processed": self.frames_processed,
            "samples_processed": self.samples_processed,
            "next_sample": self.next_sample,
            "epoch": self.epoch,
            "engaged": self.engaged,
            "last_gain_db": self.last_gain_db,
            "transitions": list(self.transitions),
            "final_seen": self.final_seen,
            "closed": self.closed,
        })


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    gain_db: Tuple[float, ...] = ()
    state_digest: str = ""
    source_first_sample: int = 0
    valid_count: int = 0


class Compressor:
    """Feed-forward peak-envelope compressor with explicit frame admission."""

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 epoch: int = 1, first_sample: int = 0) -> None:
        # None selects the frozen reference defaults; validate_config(None)
        # separately records the explicit "missing controls" adverse case.
        effective = DEFAULT_CONFIG if config is None else config
        status = validate_config(effective)
        if status is not Status.OK:
            raise ValueError(status.value)
        self.config = dict(effective)
        self.attack_coefficient = 1.0 - math.exp(
            -1000.0 / (float(self.config["attack_ms"]) * SAMPLE_RATE_HZ))
        self.release_coefficient = 1.0 - math.exp(
            -1000.0 / (float(self.config["release_ms"]) * SAMPLE_RATE_HZ))
        self.compression = 1.0 - 1.0 / float(self.config["ratio"])
        self.state = CompressorState(epoch=epoch, next_sample=first_sample)
        self.counters: Dict[str, int] = {
            "accepted_frames": 0,
            "rejected_nonfinite": 0,
            "rejected_invalid": 0,
            "rejected_tensor": 0,
            "rejected_epoch": 0,
            "rejected_state": 0,
        }
        self.resets = 0

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]], epoch: int = 1,
               first_sample: int = 0) -> Tuple[Status, Optional["Compressor"]]:
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
        self.state = CompressorState(epoch=epoch, next_sample=first_sample)
        self.counters = dict.fromkeys(self.counters, 0)
        self.resets += 1
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    def process(self, samples: Sequence[float], *, epoch: Optional[int] = None,
                first_sample: Optional[int] = None,
                valid_count: Optional[int] = None,
                flags: int = 0) -> ProcessResult:
        state = self.state
        if state.closed or state.final_seen:
            return ProcessResult(Status.CLOSED if state.closed else Status.REJECTED_STATE)
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
            magnitude = abs(value)
            coefficient = (self.attack_coefficient if magnitude > work.envelope
                           else self.release_coefficient)
            work.envelope += coefficient * (magnitude - work.envelope)
            level_db = 20.0 * math.log10(max(work.envelope, 1e-12))
            over_db = max(0.0, level_db - float(self.config["threshold_dbfs"]))
            gain_db = float(self.config["makeup_db"]) - self.compression * over_db
            gain = 10.0 ** (gain_db / 20.0)
            produced = value * gain
            if not math.isfinite(produced) or abs(produced) > 16.0:
                self.counters["rejected_nonfinite"] += 1
                return ProcessResult(Status.REJECTED_NONFINITE)
            output.append(produced)
            gains.append(gain_db)

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
                       first_sample: Optional[int] = None) -> Tuple[Status, Tuple[float, ...], List[ProcessResult]]:
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


def _copy_state(state: CompressorState) -> CompressorState:
    return CompressorState(
        envelope=state.envelope,
        frames_processed=state.frames_processed,
        samples_processed=state.samples_processed,
        next_sample=state.next_sample,
        epoch=state.epoch,
        engaged=state.engaged,
        last_gain_db=state.last_gain_db,
        transitions=list(state.transitions),
        final_seen=state.final_seen,
        closed=state.closed,
    )


def hard_clip(values: Sequence[float], ceiling: float) -> Tuple[float, ...]:
    return tuple(max(-ceiling, min(ceiling, float(value))) for value in values)


def limiter(values: Sequence[float], ceiling: float = 0.98,
            release_ms: float = 50.0) -> Tuple[float, ...]:
    """Deterministic feed-forward peak ceiling used only in interaction controls."""
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
        release_ms: float = 150.0, gain_ceiling: float = 4.0) -> Tuple[float, ...]:
    """Deterministic slow level control used only in interaction controls."""
    coefficient = 1.0 - math.exp(-1000.0 / (release_ms * SAMPLE_RATE_HZ))
    envelope = 0.0
    gain = 1.0
    output: List[float] = []
    for value in values:
        magnitude = abs(float(value))
        envelope += coefficient * (magnitude - envelope)
        target = min(gain_ceiling, max(0.25, target_rms / max(envelope, 0.01)))
        gain += coefficient * (target - gain)
        produced = float(value) * gain
        output.append(produced)
    return tuple(output)


def apply_stages(values: Sequence[float],
                 stages: Sequence[Tuple[str, Dict[str, Any]]]) -> Tuple[float, ...]:
    current = tuple(values)
    for name, settings in stages:
        if name == "compressor":
            status, produced, _ = Compressor(settings).process_stream(current)
            if status is not Status.OK:
                raise RuntimeError(f"compressor stage failed: {status.value}")
            current = produced
        elif name == "limiter":
            current = limiter(current, **settings)
        elif name == "agc":
            current = agc(current, **settings)
        else:
            raise ValueError(f"unknown stage {name}")
    return current


def _gain_ratio_db(input_block: Sequence[float],
                   output_block: Sequence[float]) -> float:
    input_power = rms(input_block)
    output_power = rms(output_block)
    if input_power <= 0.0 or output_power <= 0.0:
        return 0.0
    return 20.0 * math.log10(output_power / input_power)


def build_report() -> Dict[str, Any]:
    """Run all deterministic conditions and return the canonical report object."""
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
        "amplitude_count": len(AMPLITUDES),
        "detector": "feed-forward peak envelope, symmetric one-pole attack/release",
        "gain_law": "makeup_db - (1 - 1/ratio) * max(0, level_dbfs - threshold_dbfs)",
    }
    fixture_digest = object_digest(fixture_spec)

    # Silence: unity gain at default makeup, no state drift.
    silence = Compressor()
    silence_status, silence_output, _ = silence.process_stream(
        (0.0,) * (FRAME_SAMPLES * 40))

    # Impulse: content delay and tail behaviour.
    impulse_input = impulse()
    impulse_compressor = Compressor()
    impulse_status, impulse_output, _ = impulse_compressor.process_stream(impulse_input)
    impulse_peak_index = max(range(len(impulse_output)),
                             key=lambda index: abs(impulse_output[index]))
    tail_10ms = peak(impulse_output[FRAME_SAMPLES:2 * FRAME_SAMPLES])
    tail_100ms = peak(impulse_output[10 * FRAME_SAMPLES:11 * FRAME_SAMPLES])

    # Step: first modified sample relative to step onset.
    step_input = step_signal()
    step_compressor = Compressor()
    step_status, step_output, step_results = step_compressor.process_stream(step_input)
    step_onset = 4 * FRAME_SAMPLES
    step_crossing = next(
        (index - step_onset for index in range(step_onset, len(step_output))
         if abs(step_output[index]) >= 0.05), len(step_output))

    # Amplitude sweep: measured gain law against the analytic static target.
    sweep_outputs: List[float] = []
    sweep_inputs: List[float] = []
    sweep_errors: List[float] = []
    identity_errors: List[float] = []
    sweep_points: List[Dict[str, Any]] = []
    for index, amplitude in enumerate(AMPLITUDES):
        source = tone(4, 1000, amplitude, start_sample=index * FRAME_SAMPLES * 4)
        local = Compressor()
        status, produced, _ = local.process_stream(source)
        if status is not Status.OK:
            raise RuntimeError(f"amplitude sweep failed at {amplitude}")
        measured = _gain_ratio_db(source[-2 * FRAME_SAMPLES:],
                                  produced[-2 * FRAME_SAMPLES:])
        expected = ideal_gain_db(amplitude, DEFAULT_CONFIG)
        sweep_errors.append(measured - expected)
        identity_errors.append(-expected)
        sweep_inputs.extend(source)
        sweep_outputs.extend(produced)
        sweep_points.append({
            "amplitude": amplitude,
            "ideal_gain_db": round(expected, 6),
            "measured_gain_db": round(measured, 6),
        })

    # Frequency response: fresh state per frequency, settled gain only.
    frequency_outputs: List[float] = []
    frequency_points: List[Dict[str, Any]] = []
    expected_frequency_gain = ideal_gain_db(0.3, DEFAULT_CONFIG)
    for frequency in FREQUENCIES_HZ:
        source = tone(8, frequency, 0.3)
        local = Compressor()
        status, produced, _ = local.process_stream(source)
        if status is not Status.OK:
            raise RuntimeError(f"frequency sweep failed at {frequency} Hz")
        measured = _gain_ratio_db(source[-4 * FRAME_SAMPLES:],
                                  produced[-4 * FRAME_SAMPLES:])
        frequency_outputs.extend(produced)
        frequency_points.append({
            "frequency_hz": frequency,
            "gain_db": round(measured, 6),
            "deviation_db": round(measured - expected_frequency_gain, 6),
        })
    frequency_gains = [point["gain_db"] for point in frequency_points]

    # Attack/release on a 1 kHz burst, with sample-level gate crossings.
    burst_start_frame = 20
    burst_end_frame = 120
    burst_source = (
        (0.0,) * (FRAME_SAMPLES * burst_start_frame)
        + tone(burst_end_frame - burst_start_frame, 1000, 0.5)
        + (0.0,) * (FRAME_SAMPLES * 40))
    burst_compressor = Compressor()
    burst_status, burst_output, burst_results = burst_compressor.process_stream(burst_source)
    burst_gains = [gain for result in burst_results for gain in result.gain_db]
    burst_onset_sample = burst_start_frame * FRAME_SAMPLES
    burst_end_sample = burst_end_frame * FRAME_SAMPLES
    attack_sample = next(
        (index for index in range(burst_onset_sample, burst_end_sample)
         if burst_gains[index] <= -1.0), None)
    release_sample = next(
        (index for index in range(burst_end_sample, len(burst_gains))
         if burst_gains[index] >= -0.5), None)

    # Clean, synthetic speech-like program plus a deliberately degraded control.
    speech = synthetic_speech()
    speech_compressor = Compressor()
    speech_status, speech_output, speech_results = speech_compressor.process_stream(speech)
    speech_envelope = frame_envelope(speech)
    compressed_envelope = frame_envelope(speech_output)
    clip_anchor = hard_clip(speech, 0.16)
    anchor_envelope = frame_envelope(clip_anchor)
    speech_correlation = correlation(speech_envelope, compressed_envelope)
    anchor_correlation = correlation(speech_envelope, anchor_envelope)
    speech_gain_reduction_frames = sum(
        1 for result in speech_results
        if min(result.gain_db) <= -1.0)

    # Dense load-specific control (no host timing claim).
    load_source = dense_load()
    load_compressor = Compressor()
    load_status, load_output, load_results = load_compressor.process_stream(load_source)
    load_reduced_frames = sum(
        1 for result in load_results if min(result.gain_db) <= -1.0)

    # Headroom and peak overshoot; limiter caps the deliberate makeup boost.
    overshoot_input = impulse(frames=12, amplitude=0.9)
    boost_config = config_with(ratio=1.0, makeup_db=6.0)
    boosted_compressor = Compressor(boost_config)
    boost_status, boosted_output, _ = boosted_compressor.process_stream(overshoot_input)
    limited_output = limiter(boosted_output, ceiling=0.98)
    overshoot_samples = sum(1 for value in boosted_output if abs(value) > 1.0)

    # State transitions, reset and cross-session isolation.
    state_source = tone(40, 1000, 0.5) + (0.0,) * (FRAME_SAMPLES * 20)
    session_a = Compressor()
    state_status, state_output_a, _ = session_a.process_stream(state_source)
    state_digest_after_tone = session_a.state.digest()
    rejected_reset = session_a.reset(1, 0)
    accepted_reset = session_a.reset(2, 0)
    state_status_reset, state_output_reset, _ = session_a.process_stream(
        state_source[:FRAME_SAMPLES * 40], epoch=2, first_sample=0)
    session_b = Compressor()
    state_status_b, state_output_b, _ = session_b.process_stream(
        state_source[:FRAME_SAMPLES * 40])
    session_c = Compressor()
    state_status_c, state_output_c, _ = session_c.process_stream(
        state_source[:FRAME_SAMPLES * 10])
    reset_matches_fresh = tensor_digest(state_output_reset) == tensor_digest(state_output_b)
    isolation_matches_fresh = tensor_digest(state_output_c) == tensor_digest(
        state_output_b[:FRAME_SAMPLES * 10])

    final_frame = [0.0] * FRAME_SAMPLES
    final_frame[4] = 0.25
    final_result = session_b.process(final_frame, valid_count=5, flags=1)
    after_final = session_b.process(final_frame[:FRAME_SAMPLES])

    # Adverse controls: every expected result is recorded, none is implied.
    bad_configs: Dict[str, Tuple[Any, Status]] = {
        "null_config": (None, validate_config(None)),
        "missing_threshold": (
            {key: value for key, value in DEFAULT_CONFIG.items()
             if key != "threshold_dbfs"},
            validate_config({key: value for key, value in DEFAULT_CONFIG.items()
                             if key != "threshold_dbfs"})),
        "threshold_below_range": (config_with(threshold_dbfs=-60.1),
                                  validate_config(config_with(threshold_dbfs=-60.1))),
        "threshold_above_range": (config_with(threshold_dbfs=0.1),
                                  validate_config(config_with(threshold_dbfs=0.1))),
        "threshold_nonfinite": (config_with(threshold_dbfs=float("nan")),
                                validate_config(config_with(threshold_dbfs=float("nan")))),
        "ratio_below_range": (config_with(ratio=0.5),
                              validate_config(config_with(ratio=0.5))),
        "ratio_above_range": (config_with(ratio=20.1),
                              validate_config(config_with(ratio=20.1))),
        "attack_zero": (config_with(attack_ms=0.0),
                        validate_config(config_with(attack_ms=0.0))),
        "attack_above_range": (config_with(attack_ms=200.1),
                               validate_config(config_with(attack_ms=200.1))),
        "attack_nonfinite": (config_with(attack_ms=float("inf")),
                             validate_config(config_with(attack_ms=float("inf")))),
        "release_zero": (config_with(release_ms=0.0),
                         validate_config(config_with(release_ms=0.0))),
        "release_above_range": (config_with(release_ms=2000.1),
                                validate_config(config_with(release_ms=2000.1))),
        "makeup_negative": (config_with(makeup_db=-0.1),
                            validate_config(config_with(makeup_db=-0.1))),
        "makeup_above_range": (config_with(makeup_db=24.1),
                               validate_config(config_with(makeup_db=24.1))),
        "makeup_nonfinite": (config_with(makeup_db=float("nan")),
                             validate_config(config_with(makeup_db=float("nan")))),
        "unknown_key": (config_with(unknown_setting=1),
                        validate_config(config_with(unknown_setting=1))),
        "wrong_type": (config_with(ratio="4"),
                       validate_config(config_with(ratio="4"))),
        "bool_type": (config_with(ratio=True),
                      validate_config(config_with(ratio=True))),
    }
    config_rejections = {name: status.value for name, (_, status)
                         in sorted(bad_configs.items())}

    adverse = Compressor()
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

    # Interacting nonlinear configurations (synthetic only).
    interaction_source = _normalize(
        tuple(a + b for a, b in zip(
            synthetic_speech(frames=120, seed=SEEDS["interactions"]),
            impulse(frames=120, amplitude=0.55, position=10 * FRAME_SAMPLES + 3))),
        target_peak=1.3)
    boost_stage: Tuple[str, Dict[str, Any]] = ("compressor", boost_config)
    default_stage: Tuple[str, Dict[str, Any]] = ("compressor", dict(DEFAULT_CONFIG))
    second_stage: Tuple[str, Dict[str, Any]] = (
        "compressor", config_with(threshold_dbfs=-12.0, ratio=2.0))
    limiter_stage: Tuple[str, Dict[str, Any]] = (
        "limiter", {"ceiling": 0.98, "release_ms": 50.0})
    agc_stage: Tuple[str, Dict[str, Any]] = (
        "agc", {"target_rms": 0.25, "release_ms": 150.0, "gain_ceiling": 1.5})
    interaction_configs: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {
        "compressor_only": [default_stage],
        "compressor_to_limiter": [boost_stage, limiter_stage],
        "limiter_to_compressor": [limiter_stage, default_stage],
        "compressor_to_agc": [default_stage, agc_stage],
        "agc_to_compressor": [agc_stage, default_stage],
        "compressor_to_compressor": [default_stage, second_stage],
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
        "scope": ("proposal-only synthetic DSP fixture; no real speech, model, "
                  "device, listening or release qualification"),
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
                "tail_peak_10_to_20_ms": round(tail_10ms, 9),
                "tail_peak_100_to_110_ms": round(tail_100ms, 9),
                "output_digest": tensor_digest(impulse_output),
            },
            "step": {
                "status": step_status.value,
                "onset_sample": step_onset,
                "crossing_samples_from_onset": step_crossing,
                "peak_abs_output": peak(step_output),
                "steady_gain_db": round(step_results[-1].gain_db[-1], 6),
                "output_digest": tensor_digest(step_output),
            },
            "amplitude_sweep": {
                "status": "ok",
                "tone_hz": 1000,
                "points": len(AMPLITUDES),
                "gain_law_rmse_db": round(rmse(sweep_errors), 6),
                "identity_rmse_db": round(rmse(identity_errors), 6),
                "input_digest": tensor_digest(sweep_inputs),
                "output_digest": tensor_digest(sweep_outputs),
                "per_point": sweep_points,
            },
            "frequency_response": {
                "status": "ok",
                "frequencies_hz": len(FREQUENCIES_HZ),
                "amplitude": 0.3,
                "expected_gain_db": round(expected_frequency_gain, 6),
                "min_gain_db": round(min(frequency_gains), 6),
                "max_gain_db": round(max(frequency_gains), 6),
                "max_deviation_db": round(
                    max(abs(point["deviation_db"]) for point in frequency_points), 6),
                "output_digest": tensor_digest(frequency_outputs),
                "per_frequency": frequency_points,
            },
            "attack_release": {
                "status": burst_status.value,
                "tone_hz": 1000,
                "tone_amplitude": 0.5,
                "tone_start_frame": burst_start_frame,
                "tone_end_frame": burst_end_frame,
                "attack_sample": attack_sample,
                "attack_ms": (None if attack_sample is None else round(
                    (attack_sample - burst_onset_sample) * 1000.0 / SAMPLE_RATE_HZ, 6)),
                "release_sample": release_sample,
                "release_ms": (None if release_sample is None else round(
                    (release_sample - burst_end_sample) * 1000.0 / SAMPLE_RATE_HZ, 6)),
                "transitions": list(burst_compressor.state.transitions[:8]),
                "output_digest": tensor_digest(burst_output),
            },
            "clean_speechlike": {
                "status": speech_status.value,
                "source": "synthetic harmonic/burst program, not recorded speech",
                "frames": len(speech) // FRAME_SAMPLES,
                "peak_abs_input": round(peak(speech), 9),
                "peak_abs_output": round(peak(speech_output), 9),
                "reduced_frames": speech_gain_reduction_frames,
                "envelope_correlation": (None if speech_correlation is None
                                         else round(speech_correlation, 6)),
                "hard_clip_control_correlation": (None if anchor_correlation is None
                                                   else round(anchor_correlation, 6)),
                "intelligibility_claim": "none; synthetic envelope proxy only",
                "output_digest": tensor_digest(speech_output),
            },
            "load_control": {
                "status": load_status.value,
                "source": "seeded dense LCG noise, no host timing measurement",
                "frames": len(load_source) // FRAME_SAMPLES,
                "reduced_frames": load_reduced_frames,
                "peak_abs_output": round(peak(load_output), 9),
                "nonfinite_output_samples": sum(
                    1 for value in load_output if not math.isfinite(value)),
                "output_digest": tensor_digest(load_output),
            },
            "headroom_peak_overshoot": {
                "status": boost_status.value,
                "makeup_db": boost_config["makeup_db"],
                "ratio": boost_config["ratio"],
                "input_peak": round(peak(overshoot_input), 9),
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
                "output_digest": tensor_digest(state_output_a),
            },
            "adverse_controls": {
                "config_rejections": config_rejections,
                "config_rejection_count": len(config_rejections),
                "input_rejections": input_rejections,
            },
            "nonlinear_interactions": interactions,
        },
        "counts": {
            "source_pins": len(SOURCE_PINS),
            "boundary_pins": len(BOUNDARY_PINS),
            "required_results": len(REQUIRED_RESULTS),
            "sweep_points": len(AMPLITUDES),
            "frequency_points": len(FREQUENCIES_HZ),
            "speech_frames": len(speech) // FRAME_SAMPLES,
            "load_frames": len(load_source) // FRAME_SAMPLES,
            "interaction_configurations": len(interaction_configs),
            "expected_unittest_cases": 26,
            "expected_ctest_runs": 2,
        },
        "completeness": {
            "required_results": list(REQUIRED_RESULTS),
            "present_results": list(REQUIRED_RESULTS),
            "missing_results": [],
            "all_present": True,
            "rule": "No missing result qualifies a candidate; absent results are failures.",
        },
        "qualification": {
            "candidate_qualification": "not_qualified",
            "real_speech_listening": {
                "status": "incomplete",
                "blocker": ("No rights-cleared real speech, reference transcripts, "
                            "listener panel, scoring harness or permitted corpus is "
                            "available in this task-local fixture."),
                "deferral": "Frozen; no STOI/MOS/preference claim is made.",
                "reopen_trigger": ("Pinned cohort and independent scoring with "
                                   "authorization and listener protocol."),
            },
            "nonlinear_interaction_release": {
                "status": "incomplete",
                "blocker": ("Synthetic limiter/AGC/compressor cascades are described, "
                            "but no matched native baseline, measured workload, "
                            "production config or release gate was available."),
                "deferral": "Synthetic interactions only; no chain-release claim.",
                "reopen_trigger": ("Exact pinned runtime chain, defined margins and "
                                   "independent review on the intended workload."),
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
