# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, model-free synthetic reference for offline mono WPE.

This is an optional task-local reference at the offline waveform adapter
boundary. It uses no weights, downloads, real speech or licensed runtime.
Whole-clip WPE estimates its predictor from the complete utterance; it is
therefore explicitly outside the installed realtime v0 provider path (16 kHz,
mono f32, 160 samples per frame). The v0 grid is used here only to preserve
the fixture format and to exercise deterministic chunking of the offline
buffer. Every score is paired against a generated synthetic early-reflection
target, so all results are synthetic comparisons only.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

import scorer

CONTRACT_ID = "audio-sdk/offline-mono-wpe/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160  # installed v0 grid; never changed by this reference
CHUNK_FRAMES = 8
CHUNK_SAMPLES = FRAME_SAMPLES * CHUNK_FRAMES
STATE_CHUNK_SAMPLES = CHUNK_SAMPLES * 4  # enough STFT frames for a standalone finalize
MAX_CHUNK_SAMPLES = 65536  # permits a whole clip in one call; still finite/bounded
ADAPTER_ID = "offline-mono-wpe-reference-v1"
EARLY_WINDOW_MS = 50

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/wpe/README.md":
        "b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
SCORER_PINS = {
    "pystoi/stoi.py":
        "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658",
    "pystoi/utils.py":
        "0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321",
}
PRIOR_SCORER_PIN = {
    "path": "docs/task-evidence/classical-wiener-denoising/scorer.py",
    "sha256": "1c3e9c97f75b838d1677cb5823d679520d9a40557853e8fb6fec0ca560cf2698",
    "relationship": "algorithm byte-identical except SCORER_ID constant; prior external pystoi/numpy cross-check applies to the same scoring code",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "4f33f1bde5978db569e5079eb77c3ed6c72ea6ce726396419010445064f0e030",
    "mutable": True,
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "fft_size": 512,
    "hop_size": 128,
    "taps": 5,
    "delay": 8,
    "iterations": 3,
    "regularization": 1e-6,
    "early_window_ms": EARLY_WINDOW_MS,
    "max_abs_input": 4.0,
}
REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES = {
    "fft_size": (256, 1024),
    "hop_size": (64, 256),
    "taps": (1, 8),
    "delay": (1, 16),
    "iterations": (1, 5),
    "regularization": (1e-9, 1e-2),
    "early_window_ms": (10, 100),
    "max_abs_input": (0.25, 16.0),
}
VALID_MODES = ("offline_whole_clip",)

# Pinned synthetic-room conditions. RT60 and direct-to-reverb ratios are
# stratification parameters, not measured room properties.
ROOM_SPECS = {
    "short_rt60": {"rt60_ms": 250, "dr_db": 12.0, "seed": 8101, "noise_seed": 8301},
    "medium_rt60": {"rt60_ms": 550, "dr_db": 6.0, "seed": 8102, "noise_seed": 8302},
    "long_rt60": {"rt60_ms": 900, "dr_db": 0.0, "seed": 8103, "noise_seed": 8303},
}
SPEECH_FRAMES = 150
SILENCE_FRAMES = 10
SPEECH_SEED = 20261101
NOISE_AMPLITUDE = 0.008
EARLY_REFLECTION_DELAYS_MS = (0, 7, 13, 23, 37, 56)


class Status(str, Enum):
    OK = "ok"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_SESSION = "rejected_session"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_POSITION = "rejected_position"
    CLOSED = "closed"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Bit-exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(value))
                                   for value in values)).hexdigest()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_config(config: Optional[Dict[str, Any]]) -> Status:
    if config is None:
        return Status.REJECTED_MISSING
    if not isinstance(config, dict):
        return Status.REJECTED_INVALID
    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing or set(config) - set(REQUIRED_KEYS):
        return Status.REJECTED_MISSING if missing else Status.REJECTED_INVALID
    for key, (low, high) in _NUMERIC_RANGES.items():
        value = config[key]
        if not _is_number(value):
            return Status.REJECTED_INVALID
        number = float(value)
        if not math.isfinite(number):
            return Status.REJECTED_NONFINITE
        if number < low or number > high:
            return Status.REJECTED_INVALID
        if key in ("fft_size", "hop_size", "taps", "delay", "iterations",
                   "early_window_ms") and int(number) != number:
            return Status.REJECTED_INVALID
    if config["hop_size"] > config["fft_size"] // 2:
        return Status.REJECTED_INVALID
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


# ---- deterministic DSP ------------------------------------------------------

def _lcg(seed: int):
    value = seed & 0xFFFFFFFF
    while True:
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        yield value / 2147483648.0 - 1.0


def _hann(length: int) -> List[float]:
    """Periodic Hann window, equivalent to numpy.hanning(length + 2)[1:-1]."""
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * n / length) for n in range(length)]


def _next_power_of_two(value: int) -> int:
    result = 1
    while result < value:
        result <<= 1
    return result


def _fft_convolve(signal: Sequence[float], kernel: Sequence[float]) -> Tuple[float, ...]:
    """Deterministic overlap-add FFT convolution; no external packages."""
    if not signal or not kernel:
        return tuple()
    block = 4096
    fft_size = _next_power_of_two(len(kernel) + block - 1)
    if fft_size < 2 * block:
        fft_size = _next_power_of_two(2 * block)
    block = min(block, fft_size - len(kernel) + 1)
    kernel_spectrum = scorer._fft([complex(value, 0.0) for value in kernel]
                                  + [0j] * (fft_size - len(kernel)))
    output = [0.0] * (len(signal) + len(kernel) - 1)
    for start in range(0, len(signal), block):
        chunk = signal[start:start + block]
        spectrum = scorer._fft([complex(value, 0.0) for value in chunk]
                               + [0j] * (fft_size - len(chunk)))
        shaped = [left * right for left, right in zip(spectrum, kernel_spectrum)]
        time_domain = scorer._fft(shaped, inverse=True)
        reach = min(len(chunk) + len(kernel) - 1, len(time_domain))
        for index in range(reach):
            output[start + index] += time_domain[index].real
    return tuple(output[:len(signal)])


def _stft(samples: Sequence[float], fft_size: int, hop: int) -> List[List[complex]]:
    """scipy.signal.stft geometry: Hann, zeros boundary, padded=True."""
    length = len(samples)
    padding = fft_size // 2
    nadd = (-length % hop) % fft_size
    extended = ([0.0] * padding + list(samples) + [0.0] * padding
                + [0.0] * nadd)
    frames = 1 + (len(extended) - fft_size) // hop
    window = _hann(fft_size)
    result: List[List[complex]] = []
    for frame in range(frames):
        start = frame * hop
        block = [complex(extended[start + index] * window[index], 0.0)
                 for index in range(fft_size)]
        result.append(scorer._fft(block))
    bins = fft_size // 2 + 1
    return [[result[frame][bin] for frame in range(frames)] for bin in range(bins)]


def _istft(spectrum: Sequence[Sequence[complex]], length: int,
           fft_size: int, hop: int) -> Tuple[float, ...]:
    """Inverse of _stft with OLA normalization and boundary trimming."""
    if not spectrum or not spectrum[0]:
        return tuple()
    frames = len(spectrum[0])
    window = _hann(fft_size)
    total = fft_size + (frames - 1) * hop
    accumulation = [0.0] * total
    norm = [0.0] * total
    for frame in range(frames):
        half = fft_size // 2
        symmetric = ([spectrum[bin][frame] for bin in range(half + 1)]
                     + [spectrum[bin][frame].conjugate()
                        for bin in range(half - 1, 0, -1)])
        time_domain = scorer._fft(symmetric, inverse=True)
        start = frame * hop
        for index in range(fft_size):
            weighted = time_domain[index].real * window[index]
            accumulation[start + index] += weighted
            norm[start + index] += window[index] * window[index]
    padding = fft_size // 2
    result: List[float] = []
    for index in range(padding, padding + length):
        denominator = norm[index] if norm[index] > 1e-10 else 1.0
        value = accumulation[index] / denominator
        if not math.isfinite(value):
            raise ArithmeticError("nonfinite_istft_output")
        result.append(value)
    return tuple(result)


def _solve_complex(matrix: List[List[complex]], vector: List[complex]) -> List[complex]:
    """Complex Gaussian elimination with partial pivoting."""
    size = len(vector)
    rows = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(rows[row][column]))
        if abs(rows[pivot][column]) < 1e-300:
            raise ArithmeticError("singular_wpe_covariance")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        inverse = 1.0 / rows[column][column]
        for row in range(column + 1, size):
            factor = rows[row][column] * inverse
            if factor == 0:
                continue
            for index in range(column, size + 1):
                rows[row][index] -= factor * rows[column][index]
    solution = [0j] * size
    for row in range(size - 1, -1, -1):
        value = rows[row][size]
        for column in range(row + 1, size):
            value -= rows[row][column] * solution[column]
        solution[row] = value / rows[row][row]
    return solution


def wpe_offline(samples: Sequence[float], config: Optional[Dict[str, Any]] = None) -> Tuple[float, ...]:
    """Classical iterative offline WPE over the complete utterance.

    Noncausal by construction: every frequency bin solves one predictor from
    all STFT frames. No realtime provider, streaming STFT or timing claim.
    """
    settings = dict(DEFAULT_CONFIG if config is None else config)
    status = validate_config(settings)
    if status is not Status.OK:
        raise ValueError(status.value)
    fft_size = int(settings["fft_size"])
    hop = int(settings["hop_size"])
    taps = int(settings["taps"])
    delay = int(settings["delay"])
    iterations = int(settings["iterations"])
    regularization = float(settings["regularization"])
    limit = float(settings["max_abs_input"])
    if any(not math.isfinite(value) or abs(value) > limit for value in samples):
        raise ValueError("nonfinite_or_out_of_range_input")
    if len(samples) < fft_size:
        raise ValueError("clip_shorter_than_stft_window")

    spectrum = _stft(samples, fft_size, hop)
    frames = len(spectrum[0])
    if frames <= delay + taps:
        raise ValueError("clip_has_too_few_stft_frames")
    # Frequency-major layout avoids transposing the spectrum on every iteration.
    delayed: List[List[List[complex]]] = [[[0j for _ in range(taps)]
                                           for _ in range(frames)]
                                          for _ in range(len(spectrum))]
    for tap in range(taps):
        shift = delay + tap
        for frame in range(shift, frames):
            source = frame - shift
            for bin_index in range(len(spectrum)):
                delayed[bin_index][frame][tap] = spectrum[bin_index][source]

    output = [list(values) for values in spectrum]
    for _ in range(iterations):
        power = []
        for values in output:
            average = math.fsum((value.real ** 2 + value.imag ** 2)
                                for value in values) / frames
            power.append(max(average, 1e-10))
        for bin_index in range(len(output)):
            weight = 1.0 / power[bin_index]
            covariance = [[0j] * taps for _ in range(taps)]
            rhs = [0j] * taps
            for frame in range(frames):
                vector = delayed[bin_index][frame]
                observed = output[bin_index][frame]
                for row in range(taps):
                    weighted = vector[row] * weight
                    rhs[row] += weighted * observed.conjugate()
                    for column in range(taps):
                        covariance[row][column] += weighted * vector[column].conjugate()
            trace = math.fsum(covariance[index][index].real for index in range(taps))
            loading = regularization * (trace / taps + 1e-10)
            for index in range(taps):
                covariance[index][index] += complex(loading, 0.0)
            filt = _solve_complex(covariance, rhs)
            for frame in range(frames):
                vector = delayed[bin_index][frame]
                prediction = 0j
                for tap in range(taps):
                    prediction += filt[tap].conjugate() * vector[tap]
                output[bin_index][frame] = spectrum[bin_index][frame] - prediction

    reconstructed = _istft(output, len(samples), fft_size, hop)
    if len(reconstructed) != len(samples):
        raise ArithmeticError("wpe_output_length_mismatch")
    if any(not math.isfinite(value) for value in reconstructed):
        raise ArithmeticError("nonfinite_wpe_output")
    return tuple(max(-limit, min(limit, value)) for value in reconstructed)


# ---- pinned synthetic fixtures ---------------------------------------------

def synthetic_speech(frames: int = SPEECH_FRAMES, seed: int = SPEECH_SEED) -> Tuple[float, ...]:
    """Vowel-like analytic program material; not recorded speech."""
    noise = _lcg(seed)
    output: List[float] = []
    resonator_a = [0.0, 0.0]
    resonator_b = [0.0, 0.0]
    for index in range(frames * FRAME_SAMPLES):
        time_s = index / SAMPLE_RATE_HZ
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.1 * time_s - 0.4)
        pause = 0.0 if (index // FRAME_SAMPLES) % 41 >= 38 else 1.0
        envelope = (0.05 + 0.22 * syllable ** 2) * pause
        f0 = 112.0 + 24.0 * math.sin(2.0 * math.pi * 0.31 * time_s)
        drive = (1.0 if index % int(round(SAMPLE_RATE_HZ / f0)) == 0 else 0.0) + 0.04 * next(noise)
        resonator_a[0], resonator_a[1] = (
            0.975 * resonator_a[0] - 0.020 * resonator_a[1] + drive, resonator_a[0])
        resonator_b[0], resonator_b[1] = (
            0.951 * resonator_b[0] - 0.037 * resonator_b[1] + drive, resonator_b[0])
        value = envelope * (0.42 * resonator_a[0] + 0.20 * resonator_b[0])
        output.append(max(-0.9, min(0.9, value)))
    return tuple(output)


def clean_source() -> Tuple[float, ...]:
    """Anechoic synthetic source with a noise-free leading silence prefix."""
    return (0.0,) * (FRAME_SAMPLES * SILENCE_FRAMES) + synthetic_speech()


def synthetic_rir(rt60_ms: int, dr_db: float, seed: int) -> Tuple[float, ...]:
    """Pinned synthetic RIR: direct tap, six early taps, exponentially decayed tail.

    The tail gain is solved so the direct/early-to-late energy ratio equals
    ``dr_db``. The tail is one-pole low-passed to create measurable spectral
    tilt. These are generated parameters, not measured room properties.
    """
    if rt60_ms <= 0:
        raise ValueError("rt60_ms must be positive")
    rt60_s = rt60_ms / 1000.0
    length = int(round(rt60_s * 1.15 * SAMPLE_RATE_HZ)) + 1
    noise = _lcg(seed)
    impulse: List[float] = [0.0] * length
    impulse[0] = 1.0
    for index, delay_ms in enumerate(EARLY_REFLECTION_DELAYS_MS):
        position = int(round(delay_ms * SAMPLE_RATE_HZ / 1000.0))
        if position >= length:
            continue
        amplitude = (0.42 / (index + 1) ** 0.8) * (1.0 if index % 2 == 0 else -1.0)
        impulse[position] += amplitude * (1.0 + 0.1 * next(noise))
    lowpass = 0.0
    tail = [0.0] * length
    for index in range(length):
        time_s = index / SAMPLE_RATE_HZ
        envelope = 10.0 ** (-3.0 * time_s / rt60_s)
        lowpass = 0.55 * lowpass + 0.45 * next(noise)
        tail[index] = lowpass * envelope
    early_energy = math.fsum(value * value for value in impulse)
    tail_energy = math.fsum(value * value for value in tail)
    tail_gain = math.sqrt(early_energy / (tail_energy * 10.0 ** (dr_db / 10.0)))
    return tuple(impulse[index] + tail_gain * tail[index] for index in range(length))


def early_target(source: Sequence[float], rir: Sequence[float],
                 early_window_ms: int = EARLY_WINDOW_MS) -> Tuple[float, ...]:
    """Convention: clean target keeps the direct response plus 50 ms of early reflections."""
    window = max(1, int(round(early_window_ms * SAMPLE_RATE_HZ / 1000.0)))
    return _fft_convolve(source, rir[:window])


def colored_noise(samples: int, seed: int, amplitude: float) -> Tuple[float, ...]:
    noise = _lcg(seed)
    state = 0.0
    output: List[float] = []
    for _ in range(samples):
        state = 0.55 * state + 0.45 * next(noise)
        output.append(amplitude * state)
    return tuple(output)


def impulse(frames: int = 12) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = 0.5
    return tuple(values)


def silence(frames: int = 40) -> Tuple[float, ...]:
    return (0.0,) * (frames * FRAME_SAMPLES)


def spectral_tilt(values: Sequence[float], fft_size: int = 1024) -> Dict[str, Any]:
    """Welch-style band energies: low <1 kHz, mid 1-4 kHz, high 4-8 kHz."""
    hop = fft_size // 2
    window = _hann(fft_size)
    bins = fft_size // 2 + 1
    band_bins = {
        "low": [index for index in range(bins)
                if 0.0 <= index * SAMPLE_RATE_HZ / fft_size < 1000.0],
        "mid": [index for index in range(bins)
                if 1000.0 <= index * SAMPLE_RATE_HZ / fft_size < 4000.0],
        "high": [index for index in range(bins)
                 if 4000.0 <= index * SAMPLE_RATE_HZ / fft_size < 8000.0],
    }
    energy = {name: 0.0 for name in band_bins}
    blocks = 0
    for start in range(0, max(0, len(values) - fft_size + 1), hop):
        spectrum = scorer._fft([complex(values[start + index] * window[index], 0.0)
                                for index in range(fft_size)])
        for name, indexes in band_bins.items():
            energy[name] += math.fsum(abs(spectrum[index]) ** 2 for index in indexes)
        blocks += 1
    if blocks == 0 or any(value <= 0.0 for value in energy.values()):
        return {"status": "blocked", "reason": "insufficient_spectral_energy"}
    return {
        "status": "ok",
        "blocks": blocks,
        "band_energy": {name: round(value, 6) for name, value in energy.items()},
        "mid_over_low_db": round(10.0 * math.log10(energy["mid"] / energy["low"]), 6),
        "high_over_low_db": round(10.0 * math.log10(energy["high"] / energy["low"]), 6),
    }


# ---- offline controller (chunked buffer, whole-clip estimate at finalize) ---

@dataclass
class ControllerState:
    buffered: List[float] = field(default_factory=list)
    first_input_sample: int = 0
    epoch: int = 1
    invalid_count: int = 0
    finished: bool = False
    closed: bool = False

    def copy(self) -> "ControllerState":
        return ControllerState(
            buffered=list(self.buffered), first_input_sample=self.first_input_sample,
            epoch=self.epoch, invalid_count=self.invalid_count,
            finished=self.finished, closed=self.closed)

    def dsp_digest(self) -> str:
        """Signal/alignment state only; rejections do not mutate it."""
        return object_digest({
            "buffered_f32": tensor_digest(self.buffered),
            "buffered_samples": len(self.buffered),
            "first_input_sample": self.first_input_sample,
            "epoch": self.epoch,
            "finished": self.finished,
        })

    def digest(self) -> str:
        return object_digest({"dsp_state": self.dsp_digest(),
                              "invalid_count": self.invalid_count,
                              "closed": self.closed})


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    source_first_sample: int = 0
    valid_count: int = 0
    state_digest: str = ""


class OfflineController:
    """Buffers chunks; only ``finish()`` runs the whole-clip WPE estimate."""

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 epoch: int = 1, first_input_sample: int = 0) -> None:
        settings = dict(DEFAULT_CONFIG if config is None else config)
        status = validate_config(settings)
        if status is not Status.OK:
            raise ValueError(status.value)
        self.config = settings
        self.state = ControllerState(epoch=epoch,
                                     first_input_sample=first_input_sample)

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]], epoch: int = 1,
               first_input_sample: int = 0) -> Tuple[Status, Optional["OfflineController"]]:
        status = validate_config(config)
        if status is not Status.OK:
            return status, None
        return Status.OK, cls(config, epoch, first_input_sample)

    def reset(self, epoch: int, first_input_sample: int) -> Status:
        if self.state.closed:
            return Status.CLOSED
        if epoch <= self.state.epoch:
            return Status.REJECTED_EPOCH
        self.state = ControllerState(epoch=epoch,
                                     first_input_sample=first_input_sample)
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    def process(self, chunk: Sequence[float], *, session: Optional[int] = None,
                epoch: Optional[int] = None,
                first_input_sample: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if state.finished:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if session is not None and session != 1:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if epoch is not None and epoch != state.epoch:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_EPOCH)
        if first_input_sample is not None and first_input_sample != state.first_input_sample + len(state.buffered):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_POSITION)
        if (not isinstance(chunk, Sequence) or isinstance(chunk, (str, bytes))
                or len(chunk) == 0 or len(chunk) > MAX_CHUNK_SAMPLES):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        try:
            values = [float(value) for value in chunk]
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
        source_first = state.first_input_sample + len(state.buffered)
        work = state.copy()
        work.buffered.extend(values)
        self.state = work
        return ProcessResult(Status.OK, (), source_first, len(values),
                             work.digest())

    def finish(self, *, session: Optional[int] = None,
               epoch: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if state.finished:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if session is not None and session != 1:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if epoch is not None and epoch != state.epoch:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_EPOCH)
        first = state.first_input_sample
        try:
            output = wpe_offline(state.buffered, self.config)
        except (ArithmeticError, ValueError):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        work = state.copy()
        work.finished = True
        self.state = work
        return ProcessResult(Status.OK, output, first, len(output),
                             work.digest())


def process_whole_clip(samples: Sequence[float],
                       chunks: Optional[Sequence[int]] = None,
                       config: Optional[Dict[str, Any]] = None) -> Tuple[Status, Tuple[float, ...]]:
    """Whole-clip entry point; optional explicit chunk schedule for state checks."""
    controller = OfflineController(config)
    schedule = [size for size in chunks if size > 0] if chunks is not None else [len(samples)]
    cursor = 0
    for size in schedule:
        if size <= 0 or cursor + size > len(samples):
            return Status.REJECTED_TENSOR, ()
        result = controller.process(samples[cursor:cursor + size])
        if result.status is not Status.OK:
            return result.status, ()
        cursor += size
    if cursor != len(samples):
        return Status.REJECTED_TENSOR, ()
    final = controller.finish()
    return final.status, final.samples


# ---- scoring and report -----------------------------------------------------

def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 6)


def _metrics(reference: Optional[Sequence[float]], output: Optional[Sequence[float]],
             raw: Optional[Sequence[float]], paired_baseline: bool = True) -> Dict[str, Any]:
    """Paired scores plus validity checks; no missing score is silently filled."""
    if reference is None:
        return {"status": "blocked", "reason": "missing_reference",
                "metrics": None, "excluded_from_qualification": True}
    if output is None:
        return {"status": "blocked", "reason": "missing_output",
                "metrics": None, "excluded_from_qualification": True}
    if len(reference) != len(output) or len(raw or ()) != len(reference):
        return {"status": "failed", "reason": "shape_mismatch",
                "metrics": None, "excluded_from_qualification": True}
    if any(not math.isfinite(value) for value in output):
        return {"status": "failed", "reason": "nonfinite_output",
                "metrics": None, "excluded_from_qualification": True}
    raw_values = tuple(raw) if raw is not None else tuple(output)
    si, si_reason = scorer.si_sdr(reference, output)
    stoi_value, stoi_reason = scorer.stoi(reference, output)
    metrics: Dict[str, Any] = {"si_sdr_db": _round(si), "stoi": _round(stoi_value)}
    reasons = [si_reason, stoi_reason]
    if paired_baseline:
        si_raw, si_raw_reason = scorer.si_sdr(reference, raw_values)
        stoi_raw, stoi_raw_reason = scorer.stoi(reference, raw_values)
        reasons.extend((si_raw_reason, stoi_raw_reason))
        if not any((si_raw_reason, stoi_raw_reason)):
            assert si_raw is not None and stoi_raw is not None
            metrics.update({
                "identity_si_sdr_db": _round(si_raw),
                "identity_stoi": _round(stoi_raw),
                "delta_si_sdr_db": _round(si - si_raw),
                "delta_stoi": _round(stoi_value - stoi_raw),
            })
    if any(reasons):
        return {"status": "blocked", "reason": next(reason for reason in reasons if reason),
                "metrics": None, "excluded_from_qualification": True}
    assert si is not None and stoi_value is not None
    return {
        "status": "scored",
        "reason": None,
        "excluded_from_qualification": False,
        "metrics": metrics,
        "peak_abs": _round(max(abs(value) for value in output)),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "clipping_count": sum(1 for value in output if abs(value) > 1.0),
        "output_digest": tensor_digest(output),
    }


def load_crosscheck_vectors() -> List[Dict[str, Any]]:
    path = Path(__file__).with_name("crosscheck_vectors.json")
    vectors = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(vectors, list) or not vectors:
        raise RuntimeError("missing scorer cross-check vectors")
    return vectors


def _run_wpe(samples: Sequence[float]) -> Tuple[float, ...]:
    status, output = process_whole_clip(samples)
    if status is not Status.OK:
        raise RuntimeError(f"offline WPE failed: {status.value}")
    return output


def build_report() -> Dict[str, Any]:
    source = clean_source()
    source_digest = tensor_digest(source)
    condition_specs = ROOM_SPECS
    fixture_spec = {
        "contract": CONTRACT_ID,
        "reference_revision": "offline-mono-wpe-reference/0.1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "speech_frames": SPEECH_FRAMES,
        "silence_frames": SILENCE_FRAMES,
        "speech_seed": SPEECH_SEED,
        "noise_amplitude": NOISE_AMPLITUDE,
        "rir_generation": {
            "early_reflection_delays_ms": list(EARLY_REFLECTION_DELAYS_MS),
            "early_tap_base_amplitude": 0.42,
            "late_tail_lowpass": [0.55, 0.45],
            "late_decay": "10^(-3*t/RT60); length=round(1.15*RT60*fs)+1",
            "tail_gain": "sqrt(early_tap_energy/(late_tail_energy*10^(D_R/10)))",
            "lcg": "1664525*x+1013904223 mod 2^32; uniform [-1,1)",
        },
        "conditions": condition_specs,
        "default_config": DEFAULT_CONFIG,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "scorer_pins": SCORER_PINS,
        "source_digest": source_digest,
    }

    conditions: Dict[str, Any] = {}
    condition_inputs: Dict[str, Dict[str, Tuple[float, ...]]] = {}
    for name, spec in condition_specs.items():
        rir = synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
        target_unscaled = early_target(source, rir,
                                       int(DEFAULT_CONFIG["early_window_ms"]))
        reverberant_unscaled = _fft_convolve(source, rir)
        peak = max(abs(value) for value in reverberant_unscaled)
        gain = min(1.0, 0.9 / peak) if peak > 0 else 1.0
        target = tuple(value * gain for value in target_unscaled)
        reverberant = tuple(value * gain for value in reverberant_unscaled)
        noise = colored_noise(len(source), spec["noise_seed"], NOISE_AMPLITUDE)
        noisy = tuple(left + right for left, right in zip(reverberant, noise))
        early_samples = int(round(DEFAULT_CONFIG["early_window_ms"] * SAMPLE_RATE_HZ / 1000.0))
        early_energy = math.fsum(value * value for value in rir[:early_samples])
        late_energy = math.fsum(value * value for value in rir[early_samples:])
        wpe_output = _run_wpe(reverberant)
        wpe_noisy_output = _run_wpe(noisy)
        variants = {
            "identity_control": _metrics(target, reverberant, reverberant),
            "wpe_candidate": _metrics(target, wpe_output, reverberant),
            "noisy_identity_control": _metrics(target, noisy, noisy),
            "wpe_on_noisy": _metrics(target, wpe_noisy_output, noisy),
        }
        if any(row["status"] != "scored" for row in variants.values()):
            raise RuntimeError(f"missing required result in {name}")
        condition_inputs[name] = {"target": target, "reverberant": reverberant,
                                  "noisy": noisy, "wpe": wpe_output}
        tilt: Dict[str, Any] = {}
        for label, values in (("early_target", target),
                              ("identity_control", reverberant),
                              ("wpe_candidate", wpe_output)):
            tilt[label] = spectral_tilt(values)
        if any(row["status"] != "ok" for row in tilt.values()):
            raise RuntimeError(f"missing spectral tilt result in {name}")
        for label in ("identity_control", "wpe_candidate"):
            tilt[label]["mid_minus_target_db"] = _round(
                tilt[label]["mid_over_low_db"] - tilt["early_target"]["mid_over_low_db"])
            tilt[label]["high_minus_target_db"] = _round(
                tilt[label]["high_over_low_db"] - tilt["early_target"]["high_over_low_db"])
        conditions[name] = {
            "rt60_ms": spec["rt60_ms"],
            "configured_direct_to_diffuse_db": spec["dr_db"],
            "rir_seed": spec["seed"],
            "additive_noise_seed": spec["noise_seed"],
            "additive_noise_amplitude": NOISE_AMPLITUDE,
            "rir_samples": len(rir),
            "rir_digest": tensor_digest(rir),
            "measured_50ms_early_to_late_db": _round(10.0 * math.log10(early_energy / late_energy)),
            "energy_ratio_note": (
                "configured_direct_to_diffuse_db is direct/early taps versus the whole "
                "diffuse tail; measured_50ms_early_to_late_db also includes tail energy "
                "inside the 50 ms target window, so the two differ by definition"),
            "early_target_window_samples": early_samples,
            "clip_gain": _round(gain),
            "samples": len(source),
            "frames_on_v0_grid": len(source) // FRAME_SAMPLES,
            "scored_region": [0, len(source)],
            "source_digest": source_digest,
            "target_digest": tensor_digest(target),
            "identity_input_digest": tensor_digest(reverberant),
            "noisy_input_digest": tensor_digest(noisy),
            "input_peak_abs": _round(max(abs(value) for value in noisy)),
            "variants": variants,
            "identity_is_bit_exact":
                variants["identity_control"]["output_digest"] == tensor_digest(reverberant),
            "spectral_tilt": tilt,
            "wpe_beats_identity_si_sdr": variants["wpe_candidate"]["metrics"]["delta_si_sdr_db"] > 0,
            "wpe_beats_identity_stoi": variants["wpe_candidate"]["metrics"]["delta_stoi"] > 0,
        }

    preservation: Dict[str, Any] = {}
    for label, values in (("identity_control", source),
                          ("wpe_candidate", _run_wpe(source))):
        exact = tensor_digest(values) == tensor_digest(source)
        if exact:
            # SI-SDR is undefined for perfect reconstruction by definition;
            # report the bit-exact control explicitly instead of scoring it.
            stoi_value, stoi_reason = scorer.stoi(source, values)
            if stoi_reason or stoi_value is None:
                raise RuntimeError("identity STOI control missing")
            preservation[label] = {
                "status": "control_exact",
                "reason": "perfect_reconstruction_si_sdr_undefined",
                "excluded_from_qualification": True,
                "identity_is_bit_exact": True,
                "stoi": _round(stoi_value),
                "peak_abs": _round(max(abs(value) for value in values)),
                "nonfinite_count": sum(1 for value in values if not math.isfinite(value)),
                "clipping_count": sum(1 for value in values if abs(value) > 1.0),
                "output_digest": tensor_digest(values),
            }
            continue
        row = _metrics(source, values, source, paired_baseline=False)
        if row["status"] != "scored":
            raise RuntimeError("missing clean source preservation result")
        row["identity_is_bit_exact"] = False
        preservation[label] = row

    # The first pinned condition supplies the deterministic stream-state clip.
    reference_noisy = condition_inputs[next(iter(condition_specs))]["noisy"]

    impulse_status, impulse_output = process_whole_clip(impulse())
    impulse_peak = max(range(len(impulse_output)),
                       key=lambda index: abs(impulse_output[index]))
    silence_status, silence_output = process_whole_clip(silence())

    chunks = [CHUNK_SAMPLES] * (len(reference_noisy) // CHUNK_SAMPLES)
    remainder = len(reference_noisy) - sum(chunks)
    if remainder:
        chunks.append(remainder)
    chunk_status, chunk_output = process_whole_clip(reference_noisy, chunks=chunks)
    whole_status, whole_output = process_whole_clip(reference_noisy)
    partial = reference_noisy[:CHUNK_SAMPLES * 4 + 37]
    partial_status, partial_output = process_whole_clip(partial,
                                                        chunks=[CHUNK_SAMPLES] * 4 + [37])

    first_controller = OfflineController()
    second_controller = OfflineController()
    first_status = first_controller.process(
        reference_noisy[:STATE_CHUNK_SAMPLES]).status
    first_result = (first_controller.finish() if first_status is Status.OK
                    else ProcessResult(first_status))
    second_status = second_controller.process(
        reference_noisy[STATE_CHUNK_SAMPLES:STATE_CHUNK_SAMPLES * 2]).status
    second_result = (second_controller.finish() if second_status is Status.OK
                     else ProcessResult(second_status))

    reset_controller = OfflineController()
    reset_controller.process(reference_noisy[:STATE_CHUNK_SAMPLES])
    stale_reset = reset_controller.reset(1, 9000)
    reset_status = reset_controller.reset(3, 9000)
    reset_position = reset_controller.process(reference_noisy[:STATE_CHUNK_SAMPLES],
                                              epoch=3, first_input_sample=0).status
    refresh_status = reset_controller.process(reference_noisy[:STATE_CHUNK_SAMPLES],
                                              epoch=3,
                                              first_input_sample=9000).status
    reset_result = reset_controller.finish(epoch=3)
    replay_status, replay_expected = process_whole_clip(
        reference_noisy[:STATE_CHUNK_SAMPLES])

    numerical = OfflineController()
    numerical.process((0.01,) * STATE_CHUNK_SAMPLES)
    before = numerical.state.dsp_digest()
    nonfinite = numerical.process((math.nan,) * CHUNK_SAMPLES)
    stale_session = numerical.process((0.0,) * CHUNK_SAMPLES, session=2)
    wrong_shape = numerical.process((0.0,) * (MAX_CHUNK_SAMPLES + 1))
    out_of_range = numerical.process((9.0,) * CHUNK_SAMPLES)
    stale_epoch = numerical.process((0.0,) * CHUNK_SAMPLES, epoch=99)
    stale_position = numerical.process((0.0,) * CHUNK_SAMPLES,
                                       first_input_sample=123456)
    after = numerical.state.dsp_digest()
    dsp_unchanged = before == after == numerical.state.dsp_digest()
    invalid_delta = numerical.state.invalid_count
    first_finalize = numerical.finish()
    finished_reuse = numerical.finish()
    process_after_finish = numerical.process((0.0,) * CHUNK_SAMPLES).status

    config_errors = {}
    for label, config in (
        ("missing_key", {key: value for key, value in DEFAULT_CONFIG.items()
                         if key != "taps"}),
        ("unknown_key", config_with(unknown=1)),
        ("nonfinite", config_with(regularization=float("inf"))),
        ("out_of_range", config_with(taps=0)),
        ("wrong_type", config_with(delay="8")),
        ("bad_stft_geometry", config_with(hop_size=512)),
    ):
        status, controller = OfflineController.create(config)
        config_errors[label] = {"status": status.value,
                                "controller_created": controller is not None}
    null_status, null_controller = OfflineController.create(None)
    config_errors["none"] = {"status": null_status.value,
                             "controller_created": null_controller is not None}

    crosscheck = load_crosscheck_vectors()
    expected_estimate_digests = {
        f"{name}_{label}": row["output_digest"]
        for name, condition in conditions.items()
        for label, row in condition["variants"].items()
        if label in ("wpe_candidate", "wpe_on_noisy")
    }
    for vector in crosscheck:
        if vector["estimate_digest"] != expected_estimate_digests[vector["name"]]:
            raise RuntimeError("scorer cross-check vector is stale: " + vector["name"])

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/offline-mono-wpe-report/0.1",
        "contract": CONTRACT_ID,
        "scope": (
            "synthetic offline whole-clip mono WPE comparison against a generated "
            "early-reflection target; no real room, no listening, no model, no "
            "device timing and no release qualification"),
        "fixture_digest": object_digest(fixture_spec),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "processing_mode": "offline_whole_clip_only",
            "realtime_v0_provider": False,
            "note": (
                "Whole-clip predictor estimation needs the complete utterance and "
                "is outside the installed 16 kHz/mono/f32/160-sample realtime v0 path."),
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "scorer": {
            "scorer_id": scorer.SCORER_ID,
            "si_sdr_revision": scorer.BENCH_SI_SDR_REVISION,
            "stoi_algorithm": scorer.PYSTOI_ALGORITHM_PIN,
            "source_pins": SCORER_PINS,
            "prior_scorer_pin": PRIOR_SCORER_PIN,
            "crosscheck_vectors_digest": object_digest(crosscheck),
            "crosscheck_vectors": crosscheck,
            "pystoi_crosscheck_max_abs_delta": max(
                vector["stoi_abs_delta"] for vector in crosscheck),
            "si_sdr_numpy_crosscheck_max_abs_delta": max(
                vector["si_sdr_abs_delta"] for vector in crosscheck),
            "crosscheck_context": (
                f"{len(crosscheck)} synthetic paired signals; dependency-free port vs "
                "pystoi 0.4.1 and the benchmark zero-mean SI-SDR formula in an "
                "external venv; synthetic scorer validation only, not real-speech "
                "MOS/STOI or bench scorer parity"),
        },
        "config": DEFAULT_CONFIG,
        "conditions": conditions,
        "clean_source_preservation": preservation,
        "alignment_and_state": {
            "impulse": {"status": impulse_status.value, "peak_index": impulse_peak,
                        "peak_abs": _round(max(abs(value) for value in impulse_output)),
                        "source_first_sample": 0, "content_delay_samples": 0,
                        "output_digest": tensor_digest(impulse_output)},
            "silence": {"status": silence_status.value, "frames": 40,
                        "peak_abs": _round(max(abs(value) for value in silence_output)),
                        "output_digest": tensor_digest(silence_output)},
            "duration": {"input_samples": len(reference_noisy),
                         "output_samples": len(whole_output),
                         "equal": len(reference_noisy) == len(whole_output)},
            "chunking_equivalence": {
                "chunk_sizes": chunks,
                "status": chunk_status.value,
                "stream_digest": tensor_digest(whole_output),
                "chunked_digest": tensor_digest(chunk_output),
                "equal": tensor_digest(whole_output) == tensor_digest(chunk_output),
            },
            "session_independence": {
                "first_digest": tensor_digest(first_result.samples),
                "second_digest": tensor_digest(second_result.samples),
                "independent": (tensor_digest(first_result.samples)
                                != tensor_digest(second_result.samples)),
                "statuses": [first_status.value, second_status.value],
            },
            "reset": {"stale_epoch_status": stale_reset.value,
                      "status": reset_status.value,
                      "stale_position_status": reset_position.value,
                      "epoch": reset_controller.state.epoch,
                      "first_input_sample": 9000,
                      "refresh_status": refresh_status.value,
                      "finalize_status": reset_result.status.value,
                      "replay_status": replay_status.value,
                      "replayed_digest": tensor_digest(reset_result.samples),
                      "replay_matches_original":
                          tensor_digest(reset_result.samples) == tensor_digest(replay_expected)},
            "partial_final_frame": {
                "input_samples": len(partial), "output_samples": len(partial_output),
                "status": partial_status.value,
                "equal_duration": len(partial) == len(partial_output),
                "output_digest": tensor_digest(partial_output),
            },
        },
        "adverse": {
            "frame_rejections": {
                "nonfinite": nonfinite.status.value,
                "stale_session": stale_session.status.value,
                "wrong_shape": wrong_shape.status.value,
                "out_of_range": out_of_range.status.value,
                "stale_epoch": stale_epoch.status.value,
                "stale_position": stale_position.status.value,
                "dsp_state_unchanged": dsp_unchanged,
                "invalid_count_delta": invalid_delta,
                "finalize_status": first_finalize.status.value,
                "finished_reuse": finished_reuse.status.value,
                "process_after_finish": process_after_finish.value,
            },
            "config_rejections": config_errors,
            "missing_reference": _metrics(None, (0.0,) * FRAME_SAMPLES,
                                          (0.0,) * FRAME_SAMPLES),
        },
        "qualification": {
            "status": "synthetic_reference_only",
            "required_results": [
                "identity_noisy_controls", "paired_si_sdr_stoi", "synthetic_rir_stratification",
                "early_reflection_target", "spectral_tilt", "clean_source_preservation",
                "peaks_and_invalid_outputs", "alignment_state_duration", "adverse_controls",
            ],
            "all_required_results_present": (
                all(row["status"] == "scored"
                    for condition in conditions.values()
                    for row in condition["variants"].values())
                and preservation["wpe_candidate"]["status"] == "scored"
                and preservation["identity_control"]["status"] == "control_exact"
                and all(condition["spectral_tilt"][label]["status"] == "ok"
                        for condition in conditions.values()
                        for label in ("early_target", "identity_control", "wpe_candidate"))
                and all(condition["identity_is_bit_exact"]
                        for condition in conditions.values())
                and len(conditions) == len(ROOM_SPECS)
            ),
            "excluded_from_qualification": [
                "missing_reference control", "all adverse controls",
                "identity clean-source control (bit-exact sanity check)",
            ],
        },
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
