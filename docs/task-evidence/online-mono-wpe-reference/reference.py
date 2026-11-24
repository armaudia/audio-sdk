# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, model-free causal single-channel WPE reference evidence.

This is an optional task-local reference at a protocol-shaped waveform adapter
boundary. Every new sample is produced from the current 16 kHz/mono/f32
160-sample frame and strictly earlier frames. The installed v0 provider table,
descriptor registry, defaults and ABI are unchanged; no provider is registered
and the task-local opt-in provider manifest is disabled by default.

The implementation deliberately reports regressions. It is proposal-only
synthetic evidence, not a quality claim, selection, or release qualification.
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

CONTRACT_ID = "audio-sdk/online-mono-wpe-reference/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160  # installed v0 grid; never changed by this reference
FFT_SIZE = 512
HOP_SAMPLES = FRAME_SAMPLES
OLA_DELAY_FRAMES = 3  # frames needed before a 160-sample block is fully summed
WPE_DELAY_FRAMES = 8  # 80 ms prediction delay; history depth 80-100 ms
WPE_TAPS = 3
FLUSH_FRAMES = OLA_DELAY_FRAMES
CONTENT_DELAY_SAMPLES = OLA_DELAY_FRAMES * FRAME_SAMPLES
MAX_CHUNK_SAMPLES = 65536
EARLY_WINDOW_MS = 50

# Pinned sources: task evidence provenance, not runtime dependencies.
SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/wpe/README.md":
        "b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
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
ARTIFACT_PINS = {
    "docs/task-evidence/offline-mono-wpe/report.json":
        "2b9be2488c4b0f82f417abd3e131c840729856937ed8239f2645beeaa30d7e61",
    "docs/task-evidence/offline-mono-wpe/reference.py":
        "3a54465d8a20f81507ce1d5c2d47401274dee550aa0570bcd0257c6285f7778c",
    "docs/task-evidence/offline-mono-wpe/scorer.py":
        "22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96",
    "docs/task-evidence/offline-mono-wpe/crosscheck_vectors.json":
        "7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2",
}
CROSSCHECK_ORIGIN = (
    "docs/task-evidence/offline-mono-wpe/crosscheck_vectors.json; inherited "
    "byte-identically because the scorer implementation is byte-identical "
    "except SCORER_ID. These vectors validate the shared scorer only; their "
    "names and digests refer to offline fixture signals and are not online "
    "candidate results or an online oracle.")
SCORER_PINS = {
    "pystoi/stoi.py":
        "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658",
    "pystoi/utils.py":
        "0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321",
}
PRIOR_SCORER_PIN = {
    "path": "docs/task-evidence/offline-mono-wpe/scorer.py",
    "sha256": "22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96",
    "relationship": "algorithm byte-identical except SCORER_ID; prior external pystoi/numpy cross-check applies to the same scoring code",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "4f33f1bde5978db569e5079eb77c3ed6c72ea6ce726396419010445064f0e030",
    "mutable": True,
}
REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CONFIG: Dict[str, Any] = {
    "fft_size": FFT_SIZE,
    "hop_size": HOP_SAMPLES,
    "wpe_delay_frames": WPE_DELAY_FRAMES,
    "taps": WPE_TAPS,
    "forgetting": 0.999,
    "regularization": 1e-6,
    "prediction_energy_cap": 0.1,
    "early_window_ms": EARLY_WINDOW_MS,
    "max_abs_input": 4.0,
}
REQUIRED_KEYS = tuple(DEFAULT_CONFIG)
_NUMERIC_RANGES = {
    "fft_size": (256, 1024),
    "hop_size": (FRAME_SAMPLES, FRAME_SAMPLES),
    "wpe_delay_frames": (3, 16),
    "taps": (1, 6),
    "forgetting": (0.9, 1.0),
    "regularization": (1e-9, 1e-2),
    "prediction_energy_cap": (0.01, 1.0),
    "early_window_ms": (10, 100),
    "max_abs_input": (0.25, 16.0),
}
INTEGER_KEYS = ("fft_size", "hop_size", "wpe_delay_frames", "taps", "early_window_ms")

# Frozen synthetic-room stratification. RT60 / D-R are generation parameters,
# not measured room properties.
ROOM_SPECS = {
    "short_rt60": {"rt60_ms": 250, "dr_db": 12.0, "seed": 8101, "noise_seed": 8301},
    "medium_rt60": {"rt60_ms": 550, "dr_db": 6.0, "seed": 8102, "noise_seed": 8302},
    "long_rt60": {"rt60_ms": 900, "dr_db": 0.0, "seed": 8103, "noise_seed": 8303},
}
SPEECH_FRAMES = 150
SILENCE_FRAMES = 10
SPEECH_SEED = 20261101
SECOND_SOURCE_SEED = 20261102
NOISE_AMPLITUDE = 0.008
EARLY_REFLECTION_DELAYS_MS = (0, 7, 13, 23, 37, 56)
MOVEMENT_GAIN_KNOTS = ((0.0, 1.0), (0.4, 0.72), (0.7, 1.0), (1.0, 0.85))
SECOND_SOURCE_DELAY_SAMPLES = 400
SECOND_SOURCE_GAIN = 0.35
RESET_SCHEDULE = {"initial_epoch": 1, "reset_epoch": 3,
                  "reset_first_input_sample": 9000, "session_id": 1}


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


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        if key in INTEGER_KEYS and int(number) != number:
            return Status.REJECTED_INVALID
    size = int(config["fft_size"])
    if size & (size - 1):
        return Status.REJECTED_INVALID
    if int(config["fft_size"]) // int(config["hop_size"]) < 2:
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
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * n / length) for n in range(length)]


def _sqrt_hann(length: int) -> List[float]:
    return [math.sqrt(max(0.0, value)) for value in _hann(length)]


# At emit frame e = m - OLA_DELAY_FRAMES, global sample e*hop+i has already
# received contributions from synthesis frames m-3, m-4, m-5 and (for i < 32)
# m-6. Each contribution is analysis_window * synthesis_window at its local
# offset, so the normalization is the sum of squared rooted-Hann values at
# i, i+hop, i+2*hop and i+3*hop. Precomputing this periodic denominator keeps
# the per-frame path deterministic and avoids repeated trigonometry.
OLA_DENOMINATOR = tuple(
    math.fsum(_sqrt_hann(FFT_SIZE)[index + delay * HOP_SAMPLES] ** 2
              for delay in range(OLA_DELAY_FRAMES + 1)
              if index + delay * HOP_SAMPLES < FFT_SIZE)
    for index in range(HOP_SAMPLES))


def _next_power_of_two(value: int) -> int:
    result = 1
    while result < value:
        result <<= 1
    return result


def _fft_convolve(signal: Sequence[float], kernel: Sequence[float]) -> Tuple[float, ...]:
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


def _solve_complex(matrix: List[List[complex]], vector: List[complex]) -> Optional[List[complex]]:
    """Complex Gaussian elimination with partial pivoting; None if singular."""
    size = len(vector)
    rows = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(rows[row][column]))
        if abs(rows[pivot][column]) < 1e-300:
            return None
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
        if not all(math.isfinite(part) for part in (solution[row].real, solution[row].imag)):
            return None
    return solution


# ---- pinned synthetic fixtures ---------------------------------------------

def synthetic_speech(frames: int = SPEECH_FRAMES, seed: int = SPEECH_SEED,
                     f0_center: float = 112.0) -> Tuple[float, ...]:
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
        f0 = f0_center + 24.0 * math.sin(2.0 * math.pi * 0.31 * time_s)
        drive = (1.0 if index % int(round(SAMPLE_RATE_HZ / f0)) == 0 else 0.0) + 0.04 * next(noise)
        resonator_a[0], resonator_a[1] = (
            0.975 * resonator_a[0] - 0.020 * resonator_a[1] + drive, resonator_a[0])
        resonator_b[0], resonator_b[1] = (
            0.951 * resonator_b[0] - 0.037 * resonator_b[1] + drive, resonator_b[0])
        value = envelope * (0.42 * resonator_a[0] + 0.20 * resonator_b[0])
        output.append(max(-0.9, min(0.9, value)))
    return tuple(output)


def clean_source() -> Tuple[float, ...]:
    """Anechoic synthetic near-end source with a noise-free leading prefix."""
    return (0.0,) * (FRAME_SAMPLES * SILENCE_FRAMES) + synthetic_speech()


def synthetic_rir(rt60_ms: int, dr_db: float, seed: int) -> Tuple[float, ...]:
    """Pinned synthetic RIR: direct tap, six early taps, low-passed tail."""
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


def movement_envelope(samples: int) -> Tuple[float, ...]:
    """Frozen piecewise-linear movement schedule over the fixture duration."""
    knots = MOVEMENT_GAIN_KNOTS
    output: List[float] = []
    for index in range(samples):
        position = index / max(1, samples - 1)
        for (left_x, left_y), (right_x, right_y) in zip(knots, knots[1:]):
            if position <= right_x:
                ratio = (position - left_x) / (right_x - left_x)
                output.append(left_y + ratio * (right_y - left_y))
                break
        else:
            output.append(knots[-1][1])
    return tuple(output)


def second_source(length: int) -> Tuple[float, ...]:
    """Delayed, lower-pitched analytic overlap talker; not recorded speech."""
    voice = synthetic_speech(SPEECH_FRAMES, SECOND_SOURCE_SEED, f0_center=86.0)
    values = [0.0] * length
    for index, value in enumerate(voice):
        position = index + SECOND_SOURCE_DELAY_SAMPLES
        if position < length:
            values[position] = SECOND_SOURCE_GAIN * value
    return tuple(values)


def impulse(frames: int = 12) -> Tuple[float, ...]:
    values = [0.0] * (frames * FRAME_SAMPLES)
    values[0] = 0.5
    return tuple(values)


def silence(frames: int = 40) -> Tuple[float, ...]:
    return (0.0,) * (frames * FRAME_SAMPLES)


def spectral_tilt(values: Sequence[float], fft_size: int = 1024) -> Dict[str, Any]:
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


# ---- causal online WPE ------------------------------------------------------

def _one_sided_to_full(spectrum: Sequence[complex]) -> List[complex]:
    """Hermitian extension for a real time-domain frame (bins 0..N/2)."""
    half = len(spectrum) - 1
    return list(spectrum) + [spectrum[half - 1 - index].conjugate()
                             for index in range(half - 1)]


@dataclass
class OnlineWpe:
    """Frame-causal RLS WPE with 160-sample analysis/synthesis hop."""

    config: Dict[str, Any]
    frames: int = 0
    covariance: List[List[List[complex]]] = field(default_factory=list)
    cross: List[List[complex]] = field(default_factory=list)
    x_history: Dict[int, List[complex]] = field(default_factory=dict)
    y_history: Dict[int, List[complex]] = field(default_factory=dict)
    raw_history: List[float] = field(default_factory=list)
    ola: List[float] = field(default_factory=list)
    singular_solves: int = 0
    capped_frames: int = 0

    @classmethod
    def create(cls, config: Dict[str, Any]) -> "OnlineWpe":
        size = int(config["fft_size"])
        taps = int(config["taps"])
        bins = size // 2 + 1
        bias = size - int(config["hop_size"])
        return cls(
            config=dict(config),
            covariance=[[[0j] * taps for _ in range(taps)] for _ in range(bins)],
            cross=[[0j] * taps for _ in range(bins)],
            raw_history=[0.0] * bias,
            ola=[0.0] * (2 * size + 4 * int(config["hop_size"])),
        )

    def copy(self) -> "OnlineWpe":
        return OnlineWpe(
            config=dict(self.config), frames=self.frames,
            covariance=[[list(row) for row in bin_matrix]
                        for bin_matrix in self.covariance],
            cross=[list(row) for row in self.cross],
            x_history={key: list(value) for key, value in self.x_history.items()},
            y_history={key: list(value) for key, value in self.y_history.items()},
            raw_history=list(self.raw_history),
            ola=list(self.ola), singular_solves=self.singular_solves,
            capped_frames=self.capped_frames,
        )

    def digest(self) -> str:
        def complex_pairs(value: complex) -> List[float]:
            return [value.real, value.imag]
        return object_digest({
            "frames": self.frames,
            "covariance": [[[complex_pairs(value) for value in row]
                            for row in bin_matrix] for bin_matrix in self.covariance],
            "cross": [[complex_pairs(value) for value in row] for row in self.cross],
            "x_history": {str(key): [[value.real, value.imag] for value in row]
                          for key, row in self.x_history.items()},
            "y_history": {str(key): [[value.real, value.imag] for value in row]
                          for key, row in self.y_history.items()},
            "raw_history": self.raw_history,
            "ola": self.ola,
            "singular_solves": self.singular_solves,
            "capped_frames": self.capped_frames,
        })

    def process_frame(self, frame: Sequence[float]) -> Tuple[float, ...]:
        """Consume exactly one 160-sample frame, return one 160-sample frame."""
        config = self.config
        size = int(config["fft_size"])
        hop = int(config["hop_size"])
        bias = size - hop
        bins = size // 2 + 1
        taps = int(config["taps"])
        delay = int(config["wpe_delay_frames"])
        lam = float(config["forgetting"])
        loading = float(config["regularization"])
        cap = float(config["prediction_energy_cap"])
        m = self.frames
        window = _sqrt_hann(size)

        # The raw ring holds exactly the samples ending at this frame's last
        # sample: (size - hop) earlier samples followed by this 160-sample
        # frame. No future input is read.
        self.raw_history.extend(float(value) for value in frame)
        if len(self.raw_history) > size:
            del self.raw_history[:len(self.raw_history) - size]
        analysis = [complex(self.raw_history[index] * window[index], 0.0)
                    for index in range(size)]

        spectrum = scorer._fft(analysis)[:bins]
        self.x_history[m] = spectrum
        prediction = [0j] * bins
        for bin_index in range(bins):
            delayed = [self.x_history.get(m - delay - tap, [0j] * bins)[bin_index]
                       for tap in range(taps)]
            if math.fsum(value.real ** 2 + value.imag ** 2 for value in delayed) <= 1e-20:
                continue
            matrix = self.covariance[bin_index]
            target = spectrum[bin_index]
            for row in range(taps):
                value = delayed[row]
                for column in range(taps):
                    matrix[row][column] = (lam * matrix[row][column]
                                           + value * delayed[column].conjugate())
                self.cross[bin_index][row] = (lam * self.cross[bin_index][row]
                                              + value * target.conjugate())
            trace = math.fsum(matrix[index][index].real for index in range(taps))
            for index in range(taps):
                matrix[index][index] += complex(loading * (trace / taps + 1e-10), 0.0)
            gain = _solve_complex(matrix, self.cross[bin_index])
            if gain is None:
                self.singular_solves += 1
                continue
            prediction[bin_index] = sum(
                gain[tap].conjugate() * delayed[tap] for tap in range(taps))

        beta = 1.0
        if cap < 1.0:
            prediction_time = scorer._fft(_one_sided_to_full(prediction), inverse=True)
            predicted_energy = math.fsum((prediction_time[index].real * window[index]) ** 2
                                         for index in range(size))
            input_energy = math.fsum((analysis[index].real) ** 2 for index in range(size))
            if predicted_energy > cap * input_energy and predicted_energy > 1e-20:
                beta = math.sqrt(cap * input_energy / predicted_energy)
                self.capped_frames += 1

        enhanced = [spectrum[index] - beta * prediction[index] for index in range(bins)]
        if any(not math.isfinite(value.real) or not math.isfinite(value.imag)
               for value in enhanced):
            raise ArithmeticError("nonfinite_online_wpe_output")
        self.y_history[m] = enhanced
        reconstructed = scorer._fft(_one_sided_to_full(enhanced), inverse=True)
        needed = m * hop + size
        if len(self.ola) < needed:
            self.ola.extend([0.0] * (needed - len(self.ola)))
        for index in range(size):
            self.ola[m * hop + index] += reconstructed[index].real * window[index]

        # The current frame completes the analysis windows that cover block
        # m-OLA_DELAY_FRAMES; emitting it here uses no future input.
        emit = m - OLA_DELAY_FRAMES
        if emit < 0:
            return tuple(0.0 for _ in range(hop))
        position = emit * hop
        result: List[float] = []
        for index in range(hop):
            denominator = self._ola_denominator(index)
            value = self.ola[position + bias + index] / denominator
            if not math.isfinite(value):
                raise ArithmeticError("nonfinite_ola_output")
            result.append(value)
        limit = float(config["max_abs_input"])
        return tuple(max(-limit, min(limit, value)) for value in result)

    @staticmethod
    def _ola_denominator(index: int) -> float:
        return OLA_DENOMINATOR[index]

    def advance(self) -> None:
        self.frames += 1
        keep = self.frames - (int(self.config["wpe_delay_frames"])
                              + int(self.config["taps"]) + OLA_DELAY_FRAMES + 4)
        for key in [key for key in self.x_history if key < keep]:
            del self.x_history[key]
        for key in [key for key in self.y_history if key < keep]:
            del self.y_history[key]


@dataclass
class ControllerState:
    first_input_sample: int = 0
    input_samples: int = 0
    emitted_samples: int = 0
    epoch: int = 1
    invalid_count: int = 0
    finished: bool = False
    closed: bool = False
    final_frame_received: bool = False
    final_sample_count: Optional[int] = None


@dataclass
class ProcessResult:
    status: Status
    samples: Tuple[float, ...] = ()
    source_first_sample: int = 0
    valid_count: int = 0
    state_digest: str = ""


class OnlineController:
    """Per-frame controller with a 30 ms causal content delay and 30 ms flush."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, epoch: int = 1,
                 first_input_sample: int = 0) -> None:
        settings = dict(DEFAULT_CONFIG if config is None else config)
        status = validate_config(settings)
        if status is not Status.OK:
            raise ValueError(status.value)
        self.config = settings
        self.wpe = OnlineWpe.create(settings)
        self.state = ControllerState(epoch=epoch,
                                     first_input_sample=first_input_sample)

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]], epoch: int = 1,
               first_input_sample: int = 0) -> Tuple[Status, Optional["OnlineController"]]:
        status = validate_config(config)
        if status is not Status.OK:
            return status, None
        return Status.OK, cls(config, epoch, first_input_sample)

    def reset(self, epoch: int, first_input_sample: int) -> Status:
        if self.state.closed:
            return Status.CLOSED
        if epoch <= self.state.epoch:
            return Status.REJECTED_EPOCH
        self.wpe = OnlineWpe.create(self.config)
        self.state = ControllerState(epoch=epoch,
                                     first_input_sample=first_input_sample)
        return Status.OK

    def close(self) -> None:
        self.state.closed = True

    def dsp_digest(self) -> str:
        return object_digest({
            "wpe": self.wpe.digest(),
            "input_samples": self.state.input_samples,
            "emitted_samples": self.state.emitted_samples,
            "first_input_sample": self.state.first_input_sample,
            "epoch": self.state.epoch,
            "finished": self.state.finished,
        })

    def digest(self) -> str:
        return object_digest({"dsp_state": self.dsp_digest(),
                              "invalid_count": self.state.invalid_count,
                              "closed": self.state.closed})

    def process(self, frame: Sequence[float], *, session: Optional[int] = None,
                epoch: Optional[int] = None,
                first_input_sample: Optional[int] = None,
                final: bool = False) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if state.finished or state.final_frame_received:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if session is not None and session != RESET_SCHEDULE["session_id"]:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if epoch is not None and epoch != state.epoch:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_EPOCH)
        expected_position = state.first_input_sample + state.input_samples
        if first_input_sample is not None and first_input_sample != expected_position:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_POSITION)
        if (not isinstance(frame, Sequence) or isinstance(frame, (str, bytes))
                or len(frame) == 0 or len(frame) > FRAME_SAMPLES
                or (len(frame) != FRAME_SAMPLES and not final)):
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
        padded = values + [0.0] * (FRAME_SAMPLES - len(values))
        work = self.wpe.copy()
        try:
            output = work.process_frame(padded)
        except ArithmeticError:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        self.wpe = work
        work.advance()
        source_first = expected_position - OLA_DELAY_FRAMES * FRAME_SAMPLES
        work_state = ControllerState(
            first_input_sample=state.first_input_sample,
            input_samples=state.input_samples + len(values),
            emitted_samples=state.emitted_samples + len(output),
            epoch=state.epoch, invalid_count=state.invalid_count,
            final_frame_received=final,
            final_sample_count=len(values) if final else None)
        self.state = work_state
        return ProcessResult(Status.OK, output, source_first, len(values),
                             self.digest())

    def finish(self, *, session: Optional[int] = None,
               epoch: Optional[int] = None) -> ProcessResult:
        state = self.state
        if state.closed:
            return ProcessResult(Status.CLOSED)
        if state.finished:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if session is not None and session != RESET_SCHEDULE["session_id"]:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_SESSION)
        if epoch is not None and epoch != state.epoch:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_EPOCH)
        tail: List[float] = []
        work = self.wpe.copy()
        try:
            for _ in range(FLUSH_FRAMES):
                tail.extend(work.process_frame((0.0,) * FRAME_SAMPLES))
                work.advance()
        except ArithmeticError:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        self.wpe = work
        keep = state.final_sample_count
        if keep is not None:
            tail = tail[:max(0, keep - (state.input_samples - OLA_DELAY_FRAMES * FRAME_SAMPLES))]
        self.state = ControllerState(
            first_input_sample=state.first_input_sample,
            input_samples=state.input_samples,
            emitted_samples=state.emitted_samples + len(tail),
            epoch=state.epoch, invalid_count=state.invalid_count,
            finished=True, final_frame_received=state.final_frame_received,
            final_sample_count=state.final_sample_count)
        return ProcessResult(Status.OK, tuple(tail),
                             state.first_input_sample + state.input_samples
                             - OLA_DELAY_FRAMES * FRAME_SAMPLES,
                             len(tail), self.digest())


def process_whole_clip(samples: Sequence[float],
                       chunks: Optional[Sequence[int]] = None,
                       config: Optional[Dict[str, Any]] = None
                       ) -> Tuple[Status, Tuple[float, ...]]:
    """Stream the whole clip through the causal controller in 160-sample calls."""
    controller = OnlineController(config)
    schedule: List[int] = []
    if chunks is None:
        schedule = [FRAME_SAMPLES] * (len(samples) // FRAME_SAMPLES)
        remainder = len(samples) - sum(schedule)
        if remainder:
            schedule.append(remainder)
    else:
        schedule = list(chunks)
    cursor = 0
    output: List[float] = []
    for size in schedule:
        if size <= 0 or size > FRAME_SAMPLES or cursor + size > len(samples):
            return Status.REJECTED_TENSOR, ()
        result = controller.process(samples[cursor:cursor + size],
                                    final=cursor + size == len(samples))
        if result.status is not Status.OK:
            return result.status, ()
        output.extend(result.samples)
        cursor += size
    if cursor != len(samples):
        return Status.REJECTED_TENSOR, ()
    final = controller.finish()
    if final.status is not Status.OK:
        return final.status, ()
    output.extend(final.samples)
    trimmed = tuple(output[:len(samples)])
    if len(trimmed) != len(samples):
        return Status.REJECTED_TENSOR, ()
    return Status.OK, trimmed


# ---- scoring and report -----------------------------------------------------

def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 6)


def _metrics(reference: Optional[Sequence[float]], output: Optional[Sequence[float]],
             raw: Optional[Sequence[float]], paired_baseline: bool = True,
             align_samples: int = 0) -> Dict[str, Any]:
    """Paired scores plus validity checks; no missing score is silently filled.

    ``align_samples`` delays the reference and identity control to match the
    measured causal content delay of the candidate output. The unshifted
    candidate is always scored as produced; no time warping is applied.
    """
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
    if align_samples:
        if align_samples >= len(reference):
            return {"status": "failed", "reason": "alignment_exceeds_clip",
                    "metrics": None, "excluded_from_qualification": True}
        reference = (0.0,) * align_samples + tuple(reference)[:-align_samples]
        raw_values = (0.0,) * align_samples + raw_values[:-align_samples]
    si, si_reason = scorer.si_sdr(reference, output)
    stoi_value, stoi_reason = scorer.stoi(reference, output)
    metrics: Dict[str, Any] = {"si_sdr_db": _round(si), "stoi": _round(stoi_value),
                               "alignment_delay_samples": align_samples}
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


def offline_upper_bound_control() -> Dict[str, Any]:
    """Read the pinned noncausal WPE report; never used to qualify this candidate."""
    relative = "docs/task-evidence/offline-mono-wpe/report.json"
    path = REPO_ROOT / relative
    digest = file_digest(path)
    if digest != ARTIFACT_PINS[relative]:
        raise RuntimeError("offline WPE artifact pin is stale")
    report = json.loads(path.read_text(encoding="utf-8"))
    rows: Dict[str, Any] = {}
    for name, condition in report["conditions"].items():
        candidate = condition["variants"]["wpe_candidate"]
        if candidate["status"] != "scored":
            raise RuntimeError("offline upper-bound result missing: " + name)
        rows[name] = {
            "noncausal_delta_si_sdr_db": candidate["metrics"]["delta_si_sdr_db"],
            "noncausal_delta_stoi": candidate["metrics"]["delta_stoi"],
            "offline_output_digest": candidate["output_digest"],
        }
    return {
        "source": relative,
        "source_sha256": digest,
        "label": "noncausal whole-clip WPE upper-bound control",
        "usable_for_realtime_qualification": False,
        "used_as_candidate_oracle": False,
        "note": (
            "Pinned offline WPE fixture scores are read verbatim as provenance "
            "for a noncausal upper-bound control only. Whole-clip prediction "
            "uses future frames and is outside the 160-sample causal boundary. "
            "It is never this task's oracle, candidate result, selection "
            "criterion, acceptance threshold or release gate."),
        "conditions": rows,
    }


def _feed(controller: OnlineController, samples: Sequence[float], **kwargs: Any) -> Status:
    """Feed one or more complete 160-sample frames to a live controller."""
    status = Status.OK
    for start in range(0, len(samples), FRAME_SAMPLES):
        status = controller.process(samples[start:start + FRAME_SAMPLES], **kwargs).status
        if status is not Status.OK:
            break
    return status


def _run_candidate(samples: Sequence[float]) -> Tuple[float, ...]:
    status, output = process_whole_clip(samples)
    if status is not Status.OK:
        raise RuntimeError(f"causal online WPE failed: {status.value}")
    return output


def causal_probe_signal() -> Tuple[float, ...]:
    """Pinned short-RT60 reverberant prefix used by the provider and repeats."""
    spec = ROOM_SPECS["short_rt60"]
    rir = synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
    unscaled = _fft_convolve(clean_source(), rir)
    peak = max(abs(value) for value in unscaled)
    gain = min(1.0, 0.9 / peak) if peak > 0 else 1.0
    return tuple(value * gain for value in unscaled[:FRAME_SAMPLES * 6])


def build_report() -> Dict[str, Any]:
    source = clean_source()
    source_digest = tensor_digest(source)
    fixture_spec = {
        "contract": CONTRACT_ID,
        "reference_revision": "online-mono-wpe-reference/0.1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": FRAME_SAMPLES,
        "fft_size": FFT_SIZE,
        "hop_samples": HOP_SAMPLES,
        "analysis_lookback_samples": FFT_SIZE - HOP_SAMPLES,
        "ola_delay_frames": OLA_DELAY_FRAMES,
        "wpe_delay_frames": WPE_DELAY_FRAMES,
        "flush_frames": FLUSH_FRAMES,
        "taps": WPE_TAPS,
        "speech_frames": SPEECH_FRAMES,
        "silence_frames": SILENCE_FRAMES,
        "speech_seed": SPEECH_SEED,
        "second_source_seed": SECOND_SOURCE_SEED,
        "second_source_delay_samples": SECOND_SOURCE_DELAY_SAMPLES,
        "second_source_gain": SECOND_SOURCE_GAIN,
        "noise_amplitude": NOISE_AMPLITUDE,
        "movement_gain_knots": list(MOVEMENT_GAIN_KNOTS),
        "reset_schedule": RESET_SCHEDULE,
        "rir_generation": {
            "early_reflection_delays_ms": list(EARLY_REFLECTION_DELAYS_MS),
            "early_tap_base_amplitude": 0.42,
            "late_tail_lowpass": [0.55, 0.45],
            "late_decay": "10^(-3*t/RT60); length=round(1.15*RT60*fs)+1",
            "tail_gain": "sqrt(early_tap_energy/(late_tail_energy*10^(D_R/10)))",
            "lcg": "1664525*x+1013904223 mod 2^32; uniform [-1,1)",
        },
        "conditions": ROOM_SPECS,
        "default_config": DEFAULT_CONFIG,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "artifact_pins": ARTIFACT_PINS,
        "source_digest": source_digest,
    }

    conditions: Dict[str, Any] = {}
    for name, spec in ROOM_SPECS.items():
        rir = synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
        target_unscaled = early_target(source, rir, EARLY_WINDOW_MS)
        reverberant_unscaled = _fft_convolve(source, rir)
        peak = max(abs(value) for value in reverberant_unscaled)
        gain = min(1.0, 0.9 / peak) if peak > 0 else 1.0
        target = tuple(value * gain for value in target_unscaled)
        reverberant = tuple(value * gain for value in reverberant_unscaled)
        noise = colored_noise(len(source), spec["noise_seed"], NOISE_AMPLITUDE)
        noisy = tuple(left + right for left, right in zip(reverberant, noise))
        candidate = _run_candidate(reverberant)
        candidate_noisy = _run_candidate(noisy)
        variants = {
            "identity_control": _metrics(target, reverberant, reverberant),
            "online_wpe_candidate": _metrics(target, candidate, reverberant,
                                             align_samples=CONTENT_DELAY_SAMPLES),
            "noisy_identity_control": _metrics(target, noisy, noisy),
            "online_wpe_on_noisy": _metrics(target, candidate_noisy, noisy,
                                            align_samples=CONTENT_DELAY_SAMPLES),
        }
        if any(row["status"] != "scored" for row in variants.values()):
            raise RuntimeError(f"missing required result in {name}")
        variants["online_wpe_candidate"]["unaligned"] = _metrics(
            target, candidate, reverberant)["metrics"]
        variants["online_wpe_on_noisy"]["unaligned"] = _metrics(
            target, candidate_noisy, noisy)["metrics"]
        early_samples = int(round(EARLY_WINDOW_MS * SAMPLE_RATE_HZ / 1000.0))
        early_energy = math.fsum(value * value for value in rir[:early_samples])
        late_energy = math.fsum(value * value for value in rir[early_samples:])
        tilt: Dict[str, Any] = {}
        for label, values in (("early_target", target),
                              ("identity_control", reverberant),
                              ("online_wpe_candidate", candidate)):
            tilt[label] = spectral_tilt(values)
        if any(row["status"] != "ok" for row in tilt.values()):
            raise RuntimeError(f"missing spectral tilt result in {name}")
        for label in ("identity_control", "online_wpe_candidate"):
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
            "candidate_beats_identity_si_sdr":
                variants["online_wpe_candidate"]["metrics"]["delta_si_sdr_db"] > 0,
            "candidate_beats_identity_stoi":
                variants["online_wpe_candidate"]["metrics"]["delta_stoi"] > 0,
        }

    # Frozen movement schedule on the long-RT60 room.
    long_spec = ROOM_SPECS["long_rt60"]
    long_rir = synthetic_rir(long_spec["rt60_ms"], long_spec["dr_db"], long_spec["seed"])
    movement = movement_envelope(len(source))
    movement_raw = tuple(value * gain for value, gain in
                         zip(_fft_convolve(source, long_rir), movement))
    movement_target = tuple(value * gain for value, gain in
                            zip(early_target(source, long_rir), movement))
    movement_peak = max(abs(value) for value in movement_raw)
    movement_gain = min(1.0, 0.9 / movement_peak)
    movement_raw = tuple(value * movement_gain for value in movement_raw)
    movement_target = tuple(value * movement_gain for value in movement_target)
    movement_candidate = _run_candidate(movement_raw)
    movement_variants = {
        "identity_control": _metrics(movement_target, movement_raw, movement_raw),
        "online_wpe_candidate": _metrics(movement_target, movement_candidate, movement_raw,
                                         align_samples=CONTENT_DELAY_SAMPLES),
    }
    if any(row["status"] != "scored" for row in movement_variants.values()):
        raise RuntimeError("missing required result in movement")

    # Frozen overlapping second talker on the same long-RT60 room.
    second = second_source(len(source))
    mixture = tuple(left + right for left, right in zip(source, second))
    overlap_raw_unscaled = _fft_convolve(mixture, long_rir)
    overlap_target_unscaled = early_target(mixture, long_rir)
    overlap_peak = max(abs(value) for value in overlap_raw_unscaled)
    overlap_gain = min(1.0, 0.9 / overlap_peak)
    overlap_raw = tuple(value * overlap_gain for value in overlap_raw_unscaled)
    overlap_target = tuple(value * overlap_gain for value in overlap_target_unscaled)
    overlap_candidate = _run_candidate(overlap_raw)
    overlap_variants = {
        "identity_control": _metrics(overlap_target, overlap_raw, overlap_raw),
        "online_wpe_candidate": _metrics(overlap_target, overlap_candidate, overlap_raw,
                                         align_samples=CONTENT_DELAY_SAMPLES),
    }
    if any(row["status"] != "scored" for row in overlap_variants.values()):
        raise RuntimeError("missing required result in overlap")

    special_conditions = {
        "movement_long": {
            "basis": "long_rt60 RIR with frozen piecewise-linear movement gain",
            "movement_gain_digest": tensor_digest(movement),
            "gain_knots": list(MOVEMENT_GAIN_KNOTS),
            "variants": movement_variants,
            "identity_input_digest": tensor_digest(movement_raw),
            "target_digest": tensor_digest(movement_target),
        },
        "overlap_long": {
            "basis": "long_rt60 RIR with delayed lower-pitched analytic second talker",
            "second_source_digest": tensor_digest(second),
            "second_source_delay_samples": SECOND_SOURCE_DELAY_SAMPLES,
            "second_source_gain": SECOND_SOURCE_GAIN,
            "variants": overlap_variants,
            "identity_input_digest": tensor_digest(overlap_raw),
            "target_digest": tensor_digest(overlap_target),
        },
    }

    preservation: Dict[str, Any] = {}
    for label, values in (("identity_control", source),
                          ("online_wpe_candidate", _run_candidate(source))):
        exact = tensor_digest(values) == tensor_digest(source)
        if exact:
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
        row = _metrics(source, values, source, paired_baseline=False,
                       align_samples=CONTENT_DELAY_SAMPLES)
        if row["status"] != "scored":
            raise RuntimeError("missing clean source preservation result")
        row["identity_is_bit_exact"] = False
        preservation[label] = row

    reference_noisy = _fft_convolve(source, synthetic_rir(
        ROOM_SPECS["short_rt60"]["rt60_ms"], ROOM_SPECS["short_rt60"]["dr_db"],
        ROOM_SPECS["short_rt60"]["seed"]))
    peak = max(abs(value) for value in reference_noisy)
    reference_noisy = tuple(value * min(1.0, 0.9 / peak) for value in reference_noisy)

    impulse_status, impulse_output = process_whole_clip(impulse())
    impulse_peak = max(range(len(impulse_output)),
                       key=lambda index: abs(impulse_output[index]))
    silence_status, silence_output = process_whole_clip(silence())

    schedule = [FRAME_SAMPLES] * (len(reference_noisy) // FRAME_SAMPLES)
    remainder = len(reference_noisy) - sum(schedule)
    if remainder:
        schedule.append(remainder)
    chunk_status, chunk_output = process_whole_clip(reference_noisy, chunks=schedule)
    whole_status, whole_output = process_whole_clip(reference_noisy)
    partial = reference_noisy[:FRAME_SAMPLES * 4 + 37]
    partial_schedule = [FRAME_SAMPLES] * 4 + [37]
    partial_status, partial_output = process_whole_clip(partial, chunks=partial_schedule)

    first_controller = OnlineController()
    second_controller = OnlineController()
    first_status = _feed(first_controller, reference_noisy[:FRAME_SAMPLES * 3])
    first_tail = first_controller.finish()
    second_status = _feed(second_controller,
                          reference_noisy[FRAME_SAMPLES * 3:FRAME_SAMPLES * 6])
    second_tail = second_controller.finish()

    reset_controller = OnlineController()
    reset_clip = reference_noisy[:FRAME_SAMPLES * 12]
    _feed(reset_controller, reference_noisy[:FRAME_SAMPLES * 3])
    stale_reset = reset_controller.reset(RESET_SCHEDULE["initial_epoch"],
                                         RESET_SCHEDULE["reset_first_input_sample"])
    reset_status = reset_controller.reset(RESET_SCHEDULE["reset_epoch"],
                                          RESET_SCHEDULE["reset_first_input_sample"])
    reset_position = reset_controller.process(
        reset_clip[:FRAME_SAMPLES], epoch=RESET_SCHEDULE["reset_epoch"],
        first_input_sample=0).status
    reset_emitted: List[float] = []
    refresh_status = Status.OK
    for frame_start in range(0, len(reset_clip), FRAME_SAMPLES):
        result = reset_controller.process(
            reset_clip[frame_start:frame_start + FRAME_SAMPLES],
            epoch=RESET_SCHEDULE["reset_epoch"],
            first_input_sample=(RESET_SCHEDULE["reset_first_input_sample"] + frame_start
                                if frame_start == 0 else None),
            final=frame_start + FRAME_SAMPLES == len(reset_clip))
        refresh_status = result.status
        reset_emitted.extend(result.samples)
    reset_result = reset_controller.finish(epoch=RESET_SCHEDULE["reset_epoch"])
    reset_full = tuple(reset_emitted + list(reset_result.samples))[:len(reset_clip)]
    replay_status, replay_expected = process_whole_clip(reset_clip)

    numerical = OnlineController()
    _feed(numerical, (0.01,) * FRAME_SAMPLES * 3)
    before = numerical.dsp_digest()
    nonfinite = numerical.process((math.nan,) * FRAME_SAMPLES)
    stale_session = numerical.process((0.0,) * FRAME_SAMPLES, session=2)
    wrong_shape = numerical.process((0.0,) * (FRAME_SAMPLES + 1))
    out_of_range = numerical.process((9.0,) * FRAME_SAMPLES)
    stale_epoch = numerical.process((0.0,) * FRAME_SAMPLES, epoch=99)
    stale_position = numerical.process((0.0,) * FRAME_SAMPLES, first_input_sample=123456)
    after = numerical.dsp_digest()
    dsp_unchanged = before == after == numerical.dsp_digest()
    invalid_delta = numerical.state.invalid_count
    first_finalize = numerical.finish()
    finished_reuse = numerical.finish()
    process_after_finish = numerical.process((0.0,) * FRAME_SAMPLES).status

    config_errors = {}
    for label, config in (
        ("missing_key", {key: value for key, value in DEFAULT_CONFIG.items()
                         if key != "taps"}),
        ("unknown_key", config_with(unknown=1)),
        ("nonfinite", config_with(forgetting=float("inf"))),
        ("out_of_range", config_with(taps=0)),
        ("wrong_type", config_with(wpe_delay_frames="8")),
        ("bad_stft_geometry", config_with(fft_size=512, hop_size=512)),
        ("bad_prediction_cap", config_with(prediction_energy_cap=2.0)),
    ):
        status, controller = OnlineController.create(config)
        config_errors[label] = {"status": status.value,
                                "controller_created": controller is not None}
    null_status, null_controller = OnlineController.create(None)
    config_errors["none"] = {"status": null_status.value,
                             "controller_created": null_controller is not None}

    crosscheck = load_crosscheck_vectors()
    crosscheck_path = Path(__file__).with_name("crosscheck_vectors.json")
    if file_digest(crosscheck_path) != ARTIFACT_PINS[
            "docs/task-evidence/offline-mono-wpe/crosscheck_vectors.json"]:
        raise RuntimeError("inherited scorer cross-check file is stale")
    if any("online" in vector["name"] for vector in crosscheck):
        raise RuntimeError("inherited cross-check must not claim online results")

    probe = causal_probe_signal()
    provider_off = probe
    provider_on = _run_candidate(probe)
    upper_bound = offline_upper_bound_control()

    # Three independent cold-start passes over the same pinned probe. Every
    # digest is over little-endian f32 bytes; no tolerance or substitution is
    # used, and any mismatch fails the report build.
    repeat_digests = [tensor_digest(_run_candidate(probe)) for _ in range(3)]
    if len(set(repeat_digests)) != 1:
        raise RuntimeError("three repeat passes are not byte-identical")
    repeatability = {
        "input_samples": len(probe),
        "input_digest": tensor_digest(probe),
        "runs": 3,
        "output_digests": repeat_digests,
        "byte_identical": len(set(repeat_digests)) == 1,
        "note": ("three fresh causal controllers over one pinned synthetic "
                 "probe; exact f32 tensor digests, no tolerance and no "
                 "provider substitution"),
    }

    # Strict frame causality: a later input frame must not change any frame
    # already emitted. The divergent frame is deliberately large but bounded.
    causal_a = OnlineController()
    causal_b = OnlineController()
    prefix_a: List[Tuple[float, ...]] = []
    prefix_b: List[Tuple[float, ...]] = []
    shared_frames = 8
    for index in range(shared_frames):
        shared = reference_noisy[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
        prefix_a.append(causal_a.process(shared).samples)
        prefix_b.append(causal_b.process(shared).samples)
    divergent = tuple(0.75 if index % 2 else -0.75 for index in range(FRAME_SAMPLES))
    future_a = causal_a.process(reference_noisy[
        shared_frames * FRAME_SAMPLES:(shared_frames + 1) * FRAME_SAMPLES]).samples
    future_b = causal_b.process(divergent).samples
    causality_probe = {
        "shared_input_frames": shared_frames,
        "divergent_input_frame_samples": FRAME_SAMPLES,
        "emitted_frames_compared": len(prefix_a),
        "prefix_byte_identical": all(
            tensor_digest(left) == tensor_digest(right)
            for left, right in zip(prefix_a, prefix_b)),
        "future_frame_differs": tensor_digest(future_a) != tensor_digest(future_b),
        "note": ("identical prefix frames produce identical emitted frames "
                 "even when the next input frame differs; no future sample "
                 "is read by the causal WPE or overlap-add path"),
    }

    room_profile = {
        "profile": "room",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "claim": "acceptance structure applied to synthetic frozen fixtures only",
        "frozen": {
            "rir": {name: {"rt60_ms": spec["rt60_ms"],
                           "configured_direct_to_diffuse_db": spec["dr_db"],
                           "seed": spec["seed"]}
                    for name, spec in ROOM_SPECS.items()},
            "rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "excitation": "seeded analytic vowel-like source; not recorded speech",
            "movement_gain_knots": list(MOVEMENT_GAIN_KNOTS),
            "noise_amplitude": NOISE_AMPLITUDE,
            "reset_schedule": RESET_SCHEDULE,
            "early_target_window_ms": EARLY_WINDOW_MS,
        },
        "mapped_cases": {
            "echo_only": {
                "fixture": "reverberant tail against the frozen 50 ms early-reflection target",
                "evidence": ["conditions.*.variants.identity_control",
                             "conditions.*.variants.online_wpe_candidate"],
                "proxy_measure": "paired synthetic SI-SDR/STOI delta, not measured echo attenuation",
            },
            "near_end_only": {
                "fixture": "clean synthetic near-end source",
                "evidence": ["clean_near_end_preservation"],
                "proxy_measure": "bit-exact identity control plus paired WPE scores",
            },
            "overlap": {
                "fixture": "delayed lower-pitched analytic second talker",
                "evidence": ["special_conditions.overlap_long"],
                "proxy_measure": "paired synthetic SI-SDR/STOI against the frozen target",
            },
            "no_reference": {
                "fixture": "reference omitted from the scorer call",
                "evidence": ["adverse.missing_reference"],
                "proxy_measure": "explicit blocked status with null metrics",
            },
        },
        "not_applicable": {
            "delayed_or_missing_render": (
                "this mono dereverberation fixture has no separate render/"
                "echo-return channel; the requirement stays open for any "
                "future AEC-style qualification"),
        },
        "reported": [
            "alignment and causal content delay", "nonfinite and shape failures",
            "reset and stale-state controls", "peak and clipping counts",
            "per-condition regressions as measured",
        ],
        "not_reported": [
            "real RIRs or rooms", "measured room gain or echo attenuation",
            "listening or MOS", "target-device pacing or deadline results",
        ],
    }

    comparison: Dict[str, Any] = {}
    for name, condition in conditions.items():
        online_row = condition["variants"]["online_wpe_candidate"]["metrics"]
        offline_row = upper_bound["conditions"][name]
        comparison[name] = {
            "causal_delta_si_sdr_db": online_row["delta_si_sdr_db"],
            "causal_delta_stoi": online_row["delta_stoi"],
            "noncausal_delta_si_sdr_db": offline_row["noncausal_delta_si_sdr_db"],
            "noncausal_delta_stoi": offline_row["noncausal_delta_stoi"],
            "note": (
                "Noncausal whole-clip control uses future frames and different "
                "STFT hop/delay settings; it is an upper-bound reference point, "
                "not a like-for-like realtime result."),
        }

    required_results = {
        "identity_noisy_controls": all(
            condition["variants"][label]["status"] == "scored"
            for condition in conditions.values()
            for label in ("identity_control", "noisy_identity_control")),
        "paired_si_sdr_stoi": all(
            condition["variants"][label]["status"] == "scored"
            for condition in conditions.values()
            for label in ("online_wpe_candidate", "online_wpe_on_noisy")),
        "synthetic_rir_stratification": len(conditions) == len(ROOM_SPECS),
        "early_reflection_target": all(
            condition["early_target_window_samples"] > 0
            for condition in conditions.values()),
        "movement_control": all(row["status"] == "scored"
                                for row in movement_variants.values()),
        "overlap_control": all(row["status"] == "scored"
                               for row in overlap_variants.values()),
        "clean_near_end_preservation": preservation["online_wpe_candidate"]["status"] == "scored",
        "peaks_and_invalid_outputs": True,
        "alignment_state_duration": (
            impulse_status is Status.OK and silence_status is Status.OK
            and whole_status is Status.OK and chunk_status is Status.OK
            and partial_status is Status.OK),
        "adverse_controls": dsp_unchanged and invalid_delta == 6,
    }
    all_present = all(required_results.values())
    if not all_present:
        raise RuntimeError("no missing result may qualify a candidate: " +
                           ", ".join(key for key, value in required_results.items() if not value))

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/online-mono-wpe-report/0.1",
        "contract": CONTRACT_ID,
        "status": "proposal_only_not_qualified",
        "scope": (
            "synthetic causal/online mono WPE comparison against a generated "
            "early-reflection target; no real room, no listening, no model, no "
            "device timing and no release qualification"),
        "fixture_digest": object_digest(fixture_spec),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "processing_mode": "causal_frame_streaming",
            "realtime_v0_provider": False,
            "content_delay_samples": OLA_DELAY_FRAMES * FRAME_SAMPLES,
            "content_delay_ms": OLA_DELAY_FRAMES * FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "predictor_history_ms_min": WPE_DELAY_FRAMES * FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "predictor_history_ms_max": (WPE_DELAY_FRAMES + WPE_TAPS) * FRAME_SAMPLES
                                        * 1000.0 / SAMPLE_RATE_HZ,
            "flush_frames": FLUSH_FRAMES,
            "scoring_alignment": (
                "Candidate scores use a 480-sample (30 ms) content delay: the "
                "reference and identity control are delayed by that amount and "
                "the candidate output is scored unshifted. Unaligned scores are "
                "also recorded separately and are not used for comparison."),
            "note": (
                "One 160-sample output frame is returned per input call. The "
                "first three output frames are causal priming silence; content "
                "is delayed by three frames. Three final zero frames flush the "
                "overlap-add accumulator without reading future input."),
        },
        "provider": {
            "manifest": "provider.json",
            "identity": "online-mono-wpe-reference-provider/0.1",
            "default_enabled": False,
            "opt_in_required": True,
            "registered": False,
            "descriptor_settings": {},
            "c_abi_or_sdk_default_change": False,
            "off_on_probe": {
                "input_samples": len(probe),
                "input_digest": tensor_digest(probe),
                "off_output_digest": tensor_digest(provider_off),
                "on_output_digest": tensor_digest(provider_on),
                "off_is_bit_exact_identity": tensor_digest(provider_off) == tensor_digest(probe),
                "on_differs_from_off": tensor_digest(provider_on) != tensor_digest(provider_off),
            },
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "artifact_pins": ARTIFACT_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "scorer": {
            "scorer_id": scorer.SCORER_ID,
            "si_sdr_revision": scorer.BENCH_SI_SDR_REVISION,
            "stoi_algorithm": scorer.PYSTOI_ALGORITHM_PIN,
            "source_pins": SCORER_PINS,
            "prior_scorer_pin": PRIOR_SCORER_PIN,
            "crosscheck_vectors_digest": object_digest(crosscheck),
            "crosscheck_vectors_file_sha256": file_digest(crosscheck_path),
            "crosscheck_vectors_origin": CROSSCHECK_ORIGIN,
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
        "special_conditions": special_conditions,
        "clean_near_end_preservation": preservation,
        "alignment_and_state": {
            "impulse": {"status": impulse_status.value, "peak_index": impulse_peak,
                        "peak_abs": _round(max(abs(value) for value in impulse_output)),
                        "source_first_sample": 0, "content_delay_samples":
                            OLA_DELAY_FRAMES * FRAME_SAMPLES,
                        "output_digest": tensor_digest(impulse_output)},
            "silence": {"status": silence_status.value, "frames": 40,
                        "peak_abs": _round(max(abs(value) for value in silence_output)),
                        "output_digest": tensor_digest(silence_output)},
            "duration": {"input_samples": len(reference_noisy),
                         "output_samples": len(whole_output),
                         "equal": len(reference_noisy) == len(whole_output)},
            "chunking_equivalence": {
                "chunk_sizes": schedule,
                "status": chunk_status.value,
                "stream_digest": tensor_digest(whole_output),
                "chunked_digest": tensor_digest(chunk_output),
                "equal": tensor_digest(whole_output) == tensor_digest(chunk_output),
            },
            "session_independence": {
                "first_digest": tensor_digest(first_result_samples := first_tail.samples),
                "second_digest": tensor_digest(second_tail.samples),
                "independent": (tensor_digest(first_result_samples)
                                != tensor_digest(second_tail.samples)),
                "statuses": [first_status.value, second_status.value],
            },
            "reset": {"stale_epoch_status": stale_reset.value,
                      "clip_samples": len(reset_clip),
                      "status": reset_status.value,
                      "stale_position_status": reset_position.value,
                      "epoch": reset_controller.state.epoch,
                      "first_input_sample": RESET_SCHEDULE["reset_first_input_sample"],
                      "refresh_status": refresh_status.value,
                      "finalize_status": reset_result.status.value,
                      "replay_status": replay_status.value,
                      "replayed_digest": tensor_digest(reset_full),
                      "replay_matches_original":
                          tensor_digest(reset_full) == tensor_digest(replay_expected)},
            "partial_final_frame": {
                "input_samples": len(partial), "output_samples": len(partial_output),
                "status": partial_status.value,
                "chunk_sizes": partial_schedule,
                "equal_duration": len(partial) == len(partial_output),
                "output_digest": tensor_digest(partial_output),
            },
            "buffering": {
                "ola_accumulator_samples": len(OnlineWpe.create(DEFAULT_CONFIG).ola),
                "history_frames_retained": OLA_DELAY_FRAMES + 4,
                "covariance_complex_values": (FFT_SIZE // 2 + 1) * WPE_TAPS * WPE_TAPS,
                "description": ("host Python counts only; no target-device timing, "
                                "CPU, memory, pacing or deadline result"),
            },
            "causality_probe": causality_probe,
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
        "repeatability": repeatability,
        "room_profile": room_profile,
        "noncausal_upper_bound_control": upper_bound,
        "causal_vs_noncausal_comparison": comparison,
        "qualification": {
            "status": "not_qualified",
            "required_results": required_results,
            "all_required_results_present": all_present,
            "no_missing_result_may_qualify": True,
            "excluded_from_qualification": [
                "missing_reference control", "all adverse controls",
                "identity clean-source control (bit-exact sanity check)",
                "noncausal whole-clip WPE upper-bound control",
            ],
            "reasons": [
                "synthetic analytic excitation and synthetic RIRs only",
                "causal candidate regresses in multiple measured conditions",
                "no real-room/speech cohort, listening/MOS or real-speech STOI",
                "no target-device timing, CPU, memory or deadline result",
                "provider is opt-in, unregistered and disabled by default",
            ],
        },
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
