# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, model-free, frame-causal two-channel WPE reference evidence.

This is optional task-local synthetic evidence at a protocol-shaped two-channel
waveform boundary: two 160-sample f32 frames in, one 160-sample f32 frame out.
The installed v0 provider remains 16 kHz mono f32 at 160 samples/frame; no C
provider, descriptor, registry entry, default or public ABI is added.

Each emitted frame uses only the current two input frames and strictly earlier
frames. Scores are synthetic comparisons against a generated early-reflection
target. Status is proposal-only/not qualified with an explicit DEFER before any
processor exposure.
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

CONTRACT_ID = "audio-sdk/online-multichannel-wpe-reference/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
INPUT_CHANNELS = 2
OUTPUT_CHANNELS = 1
FFT_SIZE = 512
HOP_SAMPLES = FRAME_SAMPLES
OLA_DELAY_FRAMES = 3
WPE_DELAY_FRAMES = 8
WPE_TAPS = 2  # per channel: four stacked predictor coefficients
FLUSH_FRAMES = OLA_DELAY_FRAMES
CONTENT_DELAY_SAMPLES = OLA_DELAY_FRAMES * FRAME_SAMPLES
MAX_CHUNK_SAMPLES = 65536  # per input channel
EARLY_WINDOW_MS = 50

# Provenance pins. These files are never imported or modified at runtime.
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
    "byte-identically because the scorer algorithm is byte-identical except "
    "SCORER_ID. These vectors validate the shared scorer only; their names and "
    "digests refer to offline fixture signals and are not multichannel online "
    "candidate results, an oracle or an acceptance threshold.")
SCORER_PINS = {
    "pystoi/stoi.py":
        "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658",
    "pystoi/utils.py":
        "0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321",
}
PRIOR_SCORER_PIN = {
    "path": "docs/task-evidence/offline-mono-wpe/scorer.py",
    "sha256": "22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96",
    "relationship": (
        "algorithm byte-identical except SCORER_ID; the prior external "
        "pystoi/numpy cross-check applies to the same scoring code"),
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "5702c047fafade7e54b28199b13468ef8e7edb989539499381b51177bb669217",
    "mutable": True,
}
REPO_ROOT = Path(__file__).resolve().parents[3]
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"

DEFAULT_CONFIG: Dict[str, Any] = {
    "input_channels": INPUT_CHANNELS,
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
    "input_channels": (INPUT_CHANNELS, INPUT_CHANNELS),
    "fft_size": (256, 1024),
    "hop_size": (FRAME_SAMPLES, FRAME_SAMPLES),
    "wpe_delay_frames": (3, 16),
    "taps": (1, 4),
    "forgetting": (0.9, 1.0),
    "regularization": (1e-9, 1e-2),
    "prediction_energy_cap": (0.01, 1.0),
    "early_window_ms": (10, 100),
    "max_abs_input": (0.25, 16.0),
}
INTEGER_KEYS = ("input_channels", "fft_size", "hop_size", "wpe_delay_frames",
                "taps", "early_window_ms")

# Frozen synthetic geometry and stratification; generation parameters only.
ROOM_SPECS = {
    "short_rt60": {"rt60_ms": 250, "dr_db": 12.0, "seed": 9101, "noise_seed": 9301},
    "medium_rt60": {"rt60_ms": 550, "dr_db": 6.0, "seed": 9102, "noise_seed": 9302},
    "long_rt60": {"rt60_ms": 900, "dr_db": 0.0, "seed": 9103, "noise_seed": 9303},
}
GEOMETRY = {
    "mic_spacing_m": 0.04,
    "source_azimuth_deg": 30.0,
    "mic0_delay_samples": 0,
    "mic1_delay_samples": 5,
    "mic1_gain": 0.82,
    "mic1_rir_seed_offset": 101,
    "channels": INPUT_CHANNELS,
    "output_channel": 0,
}
SPEECH_FRAMES = 150
SILENCE_FRAMES = 10
SPEECH_SEED = 20261103
FAR_END_SEED = 20261104
SECOND_SOURCE_SEED = 20261105
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
    REJECTED_MISSING_CHANNEL = "rejected_missing_channel"
    REJECTED_DELAYED_CHANNEL = "rejected_delayed_channel"
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
    if size // int(config["hop_size"]) < 2:
        return Status.REJECTED_INVALID
    return Status.OK


def config_with(**changes: Any) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config.update(changes)
    return config


def sources_bytes() -> bytes:
    """Regenerate SOURCES.sha256 deterministically from the pinned tables."""
    lines = ["# SHA-256 pins for SDK-ONLINE-MULTICHANNEL-WPE; source: paths are "
             "workspace-relative, others SDK-worktree-relative."]
    for path, digest in list(SOURCE_PINS.items()) + list(BOUNDARY_PINS.items()) \
            + list(ARTIFACT_PINS.items()):
        prefix = "source:" if path.startswith(("research/", "adapters/", "REALTIME_",
                                               "audio-benchmark-platform/")) else ""
        lines.append(f"{digest}  {prefix}{path}")
    return ("\n".join(lines) + "\n").encode("utf-8")


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


def far_end_source() -> Tuple[float, ...]:
    """Synthetic far-end render excitation; not a recording or a real call."""
    return (0.0,) * (FRAME_SAMPLES * SILENCE_FRAMES) + synthetic_speech(
        seed=FAR_END_SEED, f0_center=96.0)


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


def synthetic_rir_pair(spec: Dict[str, Any]) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Two synchronized synthetic microphone responses from frozen geometry."""
    first = synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
    shifted = synthetic_rir(spec["rt60_ms"], spec["dr_db"],
                            spec["seed"] + GEOMETRY["mic1_rir_seed_offset"])
    delay = GEOMETRY["mic1_delay_samples"]
    second = tuple([0.0] * delay + [value * GEOMETRY["mic1_gain"] for value in shifted])[:len(first)]
    return first, second


def two_channel_convolve(source: Sequence[float],
                         pair: Tuple[Sequence[float], Sequence[float]]
                         ) -> Tuple[Tuple[float, ...], Tuple[float, ...], float]:
    """Convolve one excitation into both channels with joint peak normalization."""
    channels = [_fft_convolve(source, pair[index]) for index in range(INPUT_CHANNELS)]
    peak = max((abs(value) for channel in channels for value in channel), default=0.0)
    gain = min(1.0, 0.9 / peak) if peak > 0 else 1.0
    scaled = tuple(tuple(value * gain for value in channel) for channel in channels)
    return scaled[0], scaled[1], gain


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


def noisy_pair(pair: Tuple[Sequence[float], Sequence[float]], spec: Dict[str, Any]
               ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    return tuple(tuple(left + right for left, right in zip(
        pair[index], colored_noise(len(pair[index]), spec["noise_seed"] + 1000 * index,
                                   NOISE_AMPLITUDE))) for index in range(INPUT_CHANNELS))


def clean_near_end_pair(source: Sequence[float]) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Anechoic near-end pair: channel 1 is a frozen delayed/attenuated copy."""
    delay = GEOMETRY["mic1_delay_samples"]
    second = tuple([0.0] * delay + [value * GEOMETRY["mic1_gain"] for value in source])[:len(source)]
    return tuple(source), second


def movement_envelope(samples: int) -> Tuple[float, ...]:
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
    """Delayed, lower-pitched analytic overlapping talker; not recorded speech."""
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


def impulse_pair() -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    first = impulse()
    second = tuple([0.0] * GEOMETRY["mic1_delay_samples"] + list(impulse()))[:len(first)]
    return first, second


def channel1_impulse_pair() -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Channel-1-only impulse proves the second channel reaches the output."""
    return (0.0,) * len(impulse()), impulse()


def silence(frames: int = 40) -> Tuple[float, ...]:
    return (0.0,) * (frames * FRAME_SAMPLES)


def silence_pair(frames: int = 40) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    return silence(frames), silence(frames)


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


# ---- frame-causal two-channel online WPE ------------------------------------

def _one_sided_to_full(spectrum: Sequence[complex]) -> List[complex]:
    """Hermitian extension for a real time-domain frame (bins 0..N/2)."""
    half = len(spectrum) - 1
    return list(spectrum) + [spectrum[half - 1 - index].conjugate()
                              for index in range(half - 1)]


@dataclass
class OnlineWpe:
    """Frame-causal multichannel RLS WPE with one mono output per hop."""

    config: Dict[str, Any]
    frames: int = 0
    covariance: List[List[List[complex]]] = field(default_factory=list)
    cross: List[List[complex]] = field(default_factory=list)
    x_history: Dict[int, Tuple[List[complex], ...]] = field(default_factory=dict)
    raw_history: List[List[float]] = field(default_factory=list)
    ola: List[float] = field(default_factory=list)
    singular_solves: int = 0
    capped_frames: int = 0

    @classmethod
    def create(cls, config: Dict[str, Any]) -> "OnlineWpe":
        size = int(config["fft_size"])
        taps = int(config["taps"]) * int(config["input_channels"])
        bins = size // 2 + 1
        bias = size - int(config["hop_size"])
        return cls(
            config=dict(config),
            covariance=[[[0j] * taps for _ in range(taps)] for _ in range(bins)],
            cross=[[0j] * taps for _ in range(bins)],
            raw_history=[[0.0] * bias for _ in range(int(config["input_channels"]))],
            ola=[0.0] * (2 * size + 4 * int(config["hop_size"])),
        )

    def copy(self) -> "OnlineWpe":
        return OnlineWpe(
            config=dict(self.config), frames=self.frames,
            covariance=[[list(row) for row in bin_matrix]
                        for bin_matrix in self.covariance],
            cross=[list(row) for row in self.cross],
            x_history={key: tuple(list(value) for value in spectra)
                       for key, spectra in self.x_history.items()},
            raw_history=list(list(channel) for channel in self.raw_history),
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
            "x_history": {str(key): [[[value.real, value.imag] for value in bin]
                                     for bin in spectra]
                          for key, spectra in self.x_history.items()},
            "raw_history": self.raw_history,
            "ola": self.ola,
            "singular_solves": self.singular_solves,
            "capped_frames": self.capped_frames,
        })

    def process_frame(self, frame: Sequence[Sequence[float]]) -> Tuple[float, ...]:
        """Consume exactly one 2x160 f32 frame, return one 160 f32 frame."""
        config = self.config
        size = int(config["fft_size"])
        hop = int(config["hop_size"])
        bias = size - hop
        bins = size // 2 + 1
        taps = int(config["taps"])
        channels = int(config["input_channels"])
        delay = int(config["wpe_delay_frames"])
        lam = float(config["forgetting"])
        loading = float(config["regularization"])
        cap = float(config["prediction_energy_cap"])
        m = self.frames
        window = _sqrt_hann(size)
        dimension = channels * taps

        # Each channel's raw ring ends at this frame's last sample. No future
        # frame, no future sample and no offline normalization is read.
        analysis: List[List[complex]] = []
        for channel in range(channels):
            self.raw_history[channel].extend(float(value) for value in frame[channel])
            del self.raw_history[channel][:max(0, len(self.raw_history[channel]) - size)]
            analysis.append(scorer._fft([
                complex(self.raw_history[channel][index] * window[index], 0.0)
                for index in range(size)])[:bins])
        self.x_history[m] = tuple(analysis)
        prediction = [0j] * bins
        zero_spectrum = [0j] * bins
        for bin_index in range(bins):
            stacked: List[complex] = []
            for channel in range(channels):
                for tap in range(taps):
                    older = self.x_history.get(m - delay - tap)
                    stacked.append((zero_spectrum if older is None else older[channel])[bin_index])
            if math.fsum(value.real ** 2 + value.imag ** 2 for value in stacked) <= 1e-20:
                continue
            matrix = self.covariance[bin_index]
            target = analysis[0][bin_index]
            for row in range(dimension):
                value = stacked[row]
                for column in range(dimension):
                    matrix[row][column] = (lam * matrix[row][column]
                                           + value * stacked[column].conjugate())
                self.cross[bin_index][row] = (lam * self.cross[bin_index][row]
                                              + value * target.conjugate())
            trace = math.fsum(matrix[index][index].real for index in range(dimension))
            for index in range(dimension):
                matrix[index][index] += complex(loading * (trace / dimension + 1e-10), 0.0)
            gain = _solve_complex(matrix, self.cross[bin_index])
            if gain is None:
                self.singular_solves += 1
                continue
            prediction[bin_index] = sum(
                gain[index].conjugate() * stacked[index] for index in range(dimension))

        beta = 1.0
        if cap < 1.0:
            prediction_time = scorer._fft(_one_sided_to_full(prediction), inverse=True)
            predicted_energy = math.fsum((prediction_time[index].real * window[index]) ** 2
                                         for index in range(size))
            input_energy = math.fsum((self.raw_history[0][index] * window[index]) ** 2
                                     for index in range(size))
            if predicted_energy > cap * input_energy and predicted_energy > 1e-20:
                beta = math.sqrt(cap * input_energy / predicted_energy)
                self.capped_frames += 1

        enhanced = [analysis[0][index] - beta * prediction[index] for index in range(bins)]
        if any(not math.isfinite(value.real) or not math.isfinite(value.imag)
               for value in enhanced):
            raise ArithmeticError("nonfinite_online_wpe_output")
        reconstructed = scorer._fft(_one_sided_to_full(enhanced), inverse=True)
        needed = m * hop + size
        if len(self.ola) < needed:
            self.ola.extend([0.0] * (needed - len(self.ola)))
        for index in range(size):
            self.ola[m * hop + index] += reconstructed[index].real * window[index]

        # Emitting frame m-OLA_DELAY_FRAMES here requires only frames <= m.
        emit = m - OLA_DELAY_FRAMES
        if emit < 0:
            return tuple(0.0 for _ in range(hop))
        position = emit * hop
        result: List[float] = []
        for index in range(hop):
            denominator = OLA_DENOMINATOR[index]
            value = self.ola[position + bias + index] / denominator
            if not math.isfinite(value):
                raise ArithmeticError("nonfinite_ola_output")
            result.append(value)
        limit = float(config["max_abs_input"])
        return tuple(max(-limit, min(limit, value)) for value in result)

    def advance(self) -> None:
        self.frames += 1
        keep = self.frames - (int(self.config["wpe_delay_frames"])
                              + int(self.config["taps"]) + OLA_DELAY_FRAMES + 4)
        for key in [key for key in self.x_history if key < keep]:
            del self.x_history[key]


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
    """Two-channel frame controller with 480-sample delay and 30 ms flush."""

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

    def process(self, frame: Sequence[Sequence[float]], *, session: Optional[int] = None,
                epoch: Optional[int] = None, first_input_sample: Optional[int] = None,
                channel_positions: Optional[Sequence[int]] = None,
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
                or len(frame) != INPUT_CHANNELS):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_TENSOR)
        if any(channel is None for channel in frame):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_MISSING_CHANNEL)
        if channel_positions is not None:
            if (len(channel_positions) != INPUT_CHANNELS
                    or any(position != expected_position for position in channel_positions)):
                state.invalid_count += 1
                return ProcessResult(Status.REJECTED_DELAYED_CHANNEL)
        values: List[List[float]] = []
        for channel in frame:
            if (not isinstance(channel, Sequence) or isinstance(channel, (str, bytes))
                    or len(channel) == 0 or len(channel) > FRAME_SAMPLES
                    or (len(channel) != FRAME_SAMPLES and not final)):
                state.invalid_count += 1
                return ProcessResult(Status.REJECTED_TENSOR)
            try:
                values.append([float(value) for value in channel])
            except (TypeError, ValueError, OverflowError):
                state.invalid_count += 1
                return ProcessResult(Status.REJECTED_NONFINITE)
        limit = float(self.config["max_abs_input"])
        if any(not math.isfinite(value) for channel in values for value in channel):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        if any(abs(value) > limit for channel in values for value in channel):
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_INVALID)
        padded = [channel + [0.0] * (FRAME_SAMPLES - len(channel)) for channel in values]
        work = self.wpe.copy()
        try:
            output = work.process_frame(padded)
        except ArithmeticError:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        self.wpe = work
        work.advance()
        source_first = expected_position - CONTENT_DELAY_SAMPLES
        sample_count = len(values[0])
        self.state = ControllerState(
            first_input_sample=state.first_input_sample,
            input_samples=state.input_samples + sample_count,
            emitted_samples=state.emitted_samples + len(output),
            epoch=state.epoch, invalid_count=state.invalid_count,
            final_frame_received=final,
            final_sample_count=sample_count if final else None)
        # Per-frame digest is light; the full DSP digest is available explicitly.
        light = object_digest({"frames": self.wpe.frames,
                               "output": tensor_digest(output),
                               "invalid_count": state.invalid_count})
        return ProcessResult(Status.OK, output, source_first, sample_count, light)

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
        zeros = (0.0,) * FRAME_SAMPLES
        work = self.wpe.copy()
        try:
            for _ in range(FLUSH_FRAMES):
                tail.extend(work.process_frame((zeros, zeros)))
                work.advance()
        except ArithmeticError:
            state.invalid_count += 1
            return ProcessResult(Status.REJECTED_NONFINITE)
        self.wpe = work
        keep = state.final_sample_count
        if keep is not None:
            tail = tail[:max(0, keep - (state.input_samples - CONTENT_DELAY_SAMPLES))]
        self.state = ControllerState(
            first_input_sample=state.first_input_sample,
            input_samples=state.input_samples,
            emitted_samples=state.emitted_samples + len(tail),
            epoch=state.epoch, invalid_count=state.invalid_count,
            finished=True, final_frame_received=state.final_frame_received,
            final_sample_count=state.final_sample_count)
        return ProcessResult(Status.OK, tuple(tail),
                             state.first_input_sample + state.input_samples
                             - CONTENT_DELAY_SAMPLES,
                             len(tail), self.digest())


def process_whole_clip(pair: Sequence[Sequence[float]],
                       chunks: Optional[Sequence[int]] = None,
                       config: Optional[Dict[str, Any]] = None
                       ) -> Tuple[Status, Tuple[float, ...]]:
    """Stream a two-channel clip through the causal controller in 160-sample calls."""
    if len(pair) != INPUT_CHANNELS or len(pair[0]) != len(pair[1]):
        return Status.REJECTED_TENSOR, ()
    controller = OnlineController(config)
    schedule: List[int] = []
    if chunks is None:
        schedule = [FRAME_SAMPLES] * (len(pair[0]) // FRAME_SAMPLES)
        remainder = len(pair[0]) - sum(schedule)
        if remainder:
            schedule.append(remainder)
    else:
        schedule = list(chunks)
    cursor = 0
    output: List[float] = []
    for size in schedule:
        if size <= 0 or size > FRAME_SAMPLES or cursor + size > len(pair[0]):
            return Status.REJECTED_TENSOR, ()
        result = controller.process((pair[0][cursor:cursor + size],
                                     pair[1][cursor:cursor + size]),
                                    final=cursor + size == len(pair[0]))
        if result.status is not Status.OK:
            return result.status, ()
        output.extend(result.samples)
        cursor += size
    if cursor != len(pair[0]):
        return Status.REJECTED_TENSOR, ()
    final = controller.finish()
    if final.status is not Status.OK:
        return final.status, ()
    output.extend(final.samples)
    trimmed = tuple(output[:len(pair[0])])
    if len(trimmed) != len(pair[0]):
        return Status.REJECTED_TENSOR, ()
    return Status.OK, trimmed


# ---- scoring and report -----------------------------------------------------

def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 6)


def _metrics(reference: Optional[Sequence[float]], output: Optional[Sequence[float]],
             raw: Optional[Sequence[float]], paired_baseline: bool = True,
             align_samples: int = 0) -> Dict[str, Any]:
    """Paired scores with explicit blocked/failed states; no missing fills."""
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


def exact_control(reference: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    """Bit-exact identity control: SI-SDR is undefined, never invented."""
    if tensor_digest(reference) != tensor_digest(output):
        return {"status": "failed", "reason": "not_bit_exact",
                "metrics": None, "excluded_from_qualification": True}
    stoi_value, stoi_reason = scorer.stoi(reference, output)
    if stoi_reason or stoi_value is None:
        return {"status": "blocked", "reason": stoi_reason or "stoi_undefined",
                "metrics": None, "excluded_from_qualification": True}
    return {
        "status": "control_exact",
        "reason": "perfect_reconstruction_si_sdr_undefined",
        "metrics": {"si_sdr_db": None, "stoi": _round(stoi_value),
                    "alignment_delay_samples": 0},
        "excluded_from_qualification": True,
        "identity_is_bit_exact": True,
        "peak_abs": _round(max(abs(value) for value in output)),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "clipping_count": sum(1 for value in output if abs(value) > 1.0),
        "output_digest": tensor_digest(output),
    }


def late_tail_proxy(raw: Sequence[float], output: Sequence[float],
                    early_samples: int) -> Dict[str, Any]:
    """Synthetic late-energy proxy; not a measured room echo attenuation (task-local)."""
    aligned_raw = (0.0,) * CONTENT_DELAY_SAMPLES + tuple(raw)[:-CONTENT_DELAY_SAMPLES]
    late_input = math.fsum(value * value for value in aligned_raw[early_samples:])
    late_output = math.fsum(value * value for value in output[early_samples:])
    if late_input <= 0.0 or late_output <= 0.0:
        return {"status": "blocked", "reason": "insufficient_late_energy",
                "excluded_from_qualification": True}
    return {
        "status": "ok",
        "late_input_energy": _round(late_input),
        "late_output_energy": _round(late_output),
        "late_energy_reduction_db": _round(10.0 * math.log10(late_input / late_output)),
        "label": "synthetic late-tail energy reduction proxy; not a measured echo attenuation",
        "excluded_from_qualification": False,
    }


def load_crosscheck_vectors() -> List[Dict[str, Any]]:
    path = Path(__file__).with_name("crosscheck_vectors.json")
    vectors = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(vectors, list) or not vectors:
        raise RuntimeError("missing scorer cross-check vectors")
    return vectors


def offline_upper_bound_control() -> Dict[str, Any]:
    """Read the pinned noncausal whole-clip WPE report; never a candidate oracle."""
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
        "label": "noncausal whole-clip mono WPE upper-bound control",
        "usable_for_realtime_qualification": False,
        "used_as_candidate_oracle": False,
        "note": (
            "Pinned offline WPE scores are a noncausal upper-bound provenance "
            "point only. Whole-clip prediction reads future frames, is mono "
            "and uses a different hop/delay; it is never this task's oracle, "
            "candidate result, selection criterion, acceptance threshold or "
            "release gate."),
        "conditions": rows,
    }


def _feed(controller: OnlineController, pair: Sequence[Sequence[float]], **kwargs: Any) -> Status:
    status = Status.OK
    for start in range(0, len(pair[0]), FRAME_SAMPLES):
        status = controller.process((pair[0][start:start + FRAME_SAMPLES],
                                     pair[1][start:start + FRAME_SAMPLES]), **kwargs).status
        if status is not Status.OK:
            break
    return status


def _run_candidate(pair: Sequence[Sequence[float]]) -> Tuple[float, ...]:
    status, output = process_whole_clip(pair)
    if status is not Status.OK:
        raise RuntimeError(f"causal multichannel WPE failed: {status.value}")
    return output


def causal_probe_pair() -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Pinned short-RT60 two-channel prefix used by the adapter and repeats."""
    spec = ROOM_SPECS["short_rt60"]
    pair = synthetic_rir_pair(spec)
    first, second, _ = two_channel_convolve(clean_source(), pair)
    return first[:FRAME_SAMPLES * 6], second[:FRAME_SAMPLES * 6]


def build_report() -> Dict[str, Any]:
    source = clean_source()
    source_digest = tensor_digest(source)
    fixture_spec = {
        "contract": CONTRACT_ID,
        "reference_revision": "online-multichannel-wpe-reference/0.1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "input_channels": INPUT_CHANNELS,
        "output_channels": OUTPUT_CHANNELS,
        "input_frame_samples": FRAME_SAMPLES,
        "sample_format": "f32",
        "fft_size": FFT_SIZE,
        "hop_samples": HOP_SAMPLES,
        "analysis_lookback_samples": FFT_SIZE - HOP_SAMPLES,
        "ola_delay_frames": OLA_DELAY_FRAMES,
        "wpe_delay_frames": WPE_DELAY_FRAMES,
        "flush_frames": FLUSH_FRAMES,
        "taps_per_channel": WPE_TAPS,
        "stacked_predictor_dimension": INPUT_CHANNELS * WPE_TAPS,
        "geometry": GEOMETRY,
        "speech_frames": SPEECH_FRAMES,
        "silence_frames": SILENCE_FRAMES,
        "speech_seed": SPEECH_SEED,
        "far_end_seed": FAR_END_SEED,
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
    early_samples = int(round(EARLY_WINDOW_MS * SAMPLE_RATE_HZ / 1000.0))
    for name, spec in ROOM_SPECS.items():
        rir0, rir1 = synthetic_rir_pair(spec)
        target_unscaled = early_target(source, rir0, EARLY_WINDOW_MS)
        first, second, gain = two_channel_convolve(source, (rir0, rir1))
        target = tuple(value * gain for value in target_unscaled)
        noisy = noisy_pair((first, second), spec)
        candidate = _run_candidate((first, second))
        candidate_noisy = _run_candidate(noisy)
        variants = {
            "identity_control": _metrics(target, first, first),
            "online_mc_wpe_candidate": _metrics(target, candidate, first,
                                                align_samples=CONTENT_DELAY_SAMPLES),
            "noisy_identity_control": _metrics(target, noisy[0], noisy[0]),
            "online_mc_wpe_on_noisy": _metrics(target, candidate_noisy, noisy[0],
                                               align_samples=CONTENT_DELAY_SAMPLES),
        }
        if any(row["status"] != "scored" for row in variants.values()):
            raise RuntimeError(f"missing required result in {name}")
        variants["online_mc_wpe_candidate"]["unaligned"] = _metrics(
            target, candidate, first)["metrics"]
        variants["online_mc_wpe_on_noisy"]["unaligned"] = _metrics(
            target, candidate_noisy, noisy[0])["metrics"]

        far_end = far_end_source()
        echo_first, echo_second, echo_gain = two_channel_convolve(far_end, (rir0, rir1))
        echo_target = tuple(value * echo_gain
                            for value in early_target(far_end, rir0, EARLY_WINDOW_MS))
        echo_candidate = _run_candidate((echo_first, echo_second))
        echo_variants = {
            "identity_control": _metrics(echo_target, echo_first, echo_first),
            "online_mc_wpe_candidate": _metrics(echo_target, echo_candidate, echo_first,
                                                align_samples=CONTENT_DELAY_SAMPLES),
        }
        if any(row["status"] != "scored" for row in echo_variants.values()):
            raise RuntimeError(f"missing required echo-only result in {name}")
        echo_proxy = late_tail_proxy(echo_first, echo_candidate, early_samples)
        if echo_proxy["status"] != "ok":
            raise RuntimeError(f"missing echo-only attenuation proxy in {name}")

        early_energy = math.fsum(value * value for value in rir0[:early_samples])
        late_energy = math.fsum(value * value for value in rir0[early_samples:])
        tilt: Dict[str, Any] = {}
        for label, values in (("early_target", target),
                              ("identity_control", first),
                              ("online_mc_wpe_candidate", candidate)):
            tilt[label] = spectral_tilt(values)
        if any(row["status"] != "ok" for row in tilt.values()):
            raise RuntimeError(f"missing spectral tilt result in {name}")
        for label in ("identity_control", "online_mc_wpe_candidate"):
            tilt[label]["mid_minus_target_db"] = _round(
                tilt[label]["mid_over_low_db"] - tilt["early_target"]["mid_over_low_db"])
            tilt[label]["high_minus_target_db"] = _round(
                tilt[label]["high_over_low_db"] - tilt["early_target"]["high_over_low_db"])
        conditions[name] = {
            "rt60_ms": spec["rt60_ms"],
            "configured_direct_to_diffuse_db": spec["dr_db"],
            "rir_seeds": {"mic0": spec["seed"], "mic1": spec["seed"]
                          + GEOMETRY["mic1_rir_seed_offset"]},
            "additive_noise_seeds": [spec["noise_seed"], spec["noise_seed"] + 1000],
            "additive_noise_amplitude": NOISE_AMPLITUDE,
            "rir_samples": len(rir0),
            "rir_mic0_digest": tensor_digest(rir0),
            "rir_mic1_digest": tensor_digest(rir1),
            "measured_50ms_early_to_late_db": _round(
                10.0 * math.log10(early_energy / late_energy)),
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
            "identity_input_digest": tensor_digest(first),
            "noisy_input_digest": tensor_digest(noisy[0]),
            "input_peak_abs": _round(max(abs(value) for value in noisy[0] + noisy[1])),
            "variants": variants,
            "echo_only": {
                "basis": "synthetic far-end-only render through the frozen two-channel RIRs",
                "input_mic0_digest": tensor_digest(echo_first),
                "input_mic1_digest": tensor_digest(echo_second),
                "target_digest": tensor_digest(echo_target),
                "variants": echo_variants,
                "late_tail_proxy": echo_proxy,
            },
            "identity_is_bit_exact":
                variants["identity_control"]["output_digest"] == tensor_digest(first),
            "spectral_tilt": tilt,
            "candidate_beats_identity_si_sdr":
                variants["online_mc_wpe_candidate"]["metrics"]["delta_si_sdr_db"] > 0,
            "candidate_beats_identity_stoi":
                variants["online_mc_wpe_candidate"]["metrics"]["delta_stoi"] > 0,
        }

    long_spec = ROOM_SPECS["long_rt60"]
    long_pair = synthetic_rir_pair(long_spec)
    movement = movement_envelope(len(source))
    movement_raw = tuple(tuple(value * factor for value, factor in zip(channel, movement))
                         for channel in two_channel_convolve(source, long_pair)[:2])
    movement_target_unscaled = early_target(source, long_pair[0], EARLY_WINDOW_MS)
    peak = max(abs(value) for channel in movement_raw for value in channel)
    movement_gain = min(1.0, 0.9 / peak)
    movement_raw = tuple(tuple(value * movement_gain for value in channel)
                         for channel in movement_raw)
    movement_target = tuple(value * movement_gain for value in movement_target_unscaled)
    movement_candidate = _run_candidate(movement_raw)
    movement_variants = {
        "identity_control": _metrics(movement_target, movement_raw[0], movement_raw[0]),
        "online_mc_wpe_candidate": _metrics(movement_target, movement_candidate,
                                            movement_raw[0],
                                            align_samples=CONTENT_DELAY_SAMPLES),
    }
    if any(row["status"] != "scored" for row in movement_variants.values()):
        raise RuntimeError("missing required result in movement")

    second = second_source(len(source))
    mixture = tuple(left + right for left, right in zip(source, second))
    overlap_raw = two_channel_convolve(mixture, long_pair)
    overlap_target = tuple(value * overlap_raw[2]
                           for value in early_target(mixture, long_pair[0], EARLY_WINDOW_MS))
    overlap_candidate = _run_candidate(overlap_raw[:2])
    overlap_variants = {
        "identity_control": _metrics(overlap_target, overlap_raw[0], overlap_raw[0]),
        "online_mc_wpe_candidate": _metrics(overlap_target, overlap_candidate,
                                            overlap_raw[0],
                                            align_samples=CONTENT_DELAY_SAMPLES),
    }
    if any(row["status"] != "scored" for row in overlap_variants.values()):
        raise RuntimeError("missing required result in overlap")

    near_pair = clean_near_end_pair(source)
    near_candidate = _run_candidate(near_pair)
    # The mic-0 passthrough is bit-exact on this anechoic case, so SI-SDR is
    # undefined for the identity baseline. Score it explicitly as an exact
    # control and compare only the defined STOI delta; no missing value is
    # invented or used to qualify the candidate.
    near_identity = _metrics(source, near_pair[0], near_pair[0], paired_baseline=False)
    near_identity["status"] = "control_exact"
    near_identity["reason"] = "perfect_reconstruction_si_sdr_undefined"
    identity_stoi, identity_reason = scorer.stoi(source, near_pair[0])
    if identity_reason or identity_stoi is None:
        raise RuntimeError("missing near-end identity STOI control")
    near_identity["metrics"] = {
        "si_sdr_db": None,
        "stoi": _round(identity_stoi),
        "alignment_delay_samples": 0,
        "identity_is_bit_exact": True,
    }
    near_identity["identity_is_bit_exact"] = True
    near_identity["peak_abs"] = _round(max(abs(value) for value in near_pair[0]))
    near_identity["nonfinite_count"] = 0
    near_identity["clipping_count"] = 0
    near_identity["output_digest"] = tensor_digest(near_pair[0])
    near_row = _metrics(source, near_candidate, near_pair[0], paired_baseline=False,
                        align_samples=CONTENT_DELAY_SAMPLES)
    if near_identity["status"] != "control_exact" or near_row["status"] != "scored":
        raise RuntimeError("missing required near-end-only result")
    assert near_identity["metrics"] is not None and near_row["metrics"] is not None
    near_row["metrics"].update({
        "identity_si_sdr_db": None,
        "identity_stoi": near_identity["metrics"]["stoi"],
        "delta_si_sdr_db": None,
        "delta_stoi": _round(near_row["metrics"]["stoi"]
                             - near_identity["metrics"]["stoi"]),
        "delta_reason": "identity_si_sdr_undefined_at_perfect_reconstruction",
    })
    near_variants = {"identity_control": near_identity,
                     "online_mc_wpe_candidate": near_row}

    special_conditions = {
        "movement_long": {
            "basis": "long_rt60 RIR pair with frozen piecewise-linear movement gain",
            "movement_gain_digest": tensor_digest(movement),
            "gain_knots": list(MOVEMENT_GAIN_KNOTS),
            "variants": movement_variants,
            "identity_input_digest": tensor_digest(movement_raw[0]),
            "target_digest": tensor_digest(movement_target),
        },
        "overlap_long": {
            "basis": "long_rt60 RIR pair with delayed lower-pitched analytic second talker",
            "second_source_digest": tensor_digest(second),
            "second_source_delay_samples": SECOND_SOURCE_DELAY_SAMPLES,
            "second_source_gain": SECOND_SOURCE_GAIN,
            "variants": overlap_variants,
            "identity_input_digest": tensor_digest(overlap_raw[0]),
            "target_digest": tensor_digest(overlap_target),
        },
        "near_end_only": {
            "basis": "anechoic synthetic near-end with delayed attenuated channel 1",
            "identity_input_digest": tensor_digest(near_pair[0]),
            "target_digest": tensor_digest(source),
            "variants": near_variants,
            "near_end_damage": {
                "candidate_si_sdr_db": near_row["metrics"]["si_sdr_db"],
                "candidate_stoi": near_row["metrics"]["stoi"],
                "identity_is_bit_exact": True,
                "delta_si_sdr_db": None,
                "delta_stoi": near_row["metrics"]["delta_stoi"],
                "delta_reason": near_row["metrics"]["delta_reason"],
            },
        },
    }

    preservation: Dict[str, Any] = {}
    for label, values in (("identity_control", source),
                          ("online_mc_wpe_candidate", near_candidate)):
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
            raise RuntimeError("missing clean near-end preservation result")
        row["identity_is_bit_exact"] = False
        preservation[label] = row

    reference_pair = two_channel_convolve(source, synthetic_rir_pair(
        ROOM_SPECS["short_rt60"]))[:2]

    impulse_status, impulse_output = process_whole_clip(impulse_pair())
    impulse_c1_status, impulse_c1_output = process_whole_clip(channel1_impulse_pair())
    impulse_c1_peak = max(range(len(impulse_c1_output)),
                          key=lambda index: abs(impulse_c1_output[index]))
    silence_status, silence_output = process_whole_clip(silence_pair())

    schedule = [FRAME_SAMPLES] * (len(reference_pair[0]) // FRAME_SAMPLES)
    remainder = len(reference_pair[0]) - sum(schedule)
    if remainder:
        schedule.append(remainder)
    chunk_status, chunk_output = process_whole_clip(reference_pair, chunks=schedule)
    whole_status, whole_output = process_whole_clip(reference_pair)
    partial_pair = (reference_pair[0][:FRAME_SAMPLES * 4 + 37],
                    reference_pair[1][:FRAME_SAMPLES * 4 + 37])
    partial_schedule = [FRAME_SAMPLES] * 4 + [37]
    partial_status, partial_output = process_whole_clip(partial_pair, chunks=partial_schedule)

    first_controller = OnlineController()
    second_controller = OnlineController()
    first_status = _feed(first_controller, tuple(channel[:FRAME_SAMPLES * 3]
                                                 for channel in reference_pair))
    first_tail = first_controller.finish()
    second_status = _feed(second_controller, tuple(channel[FRAME_SAMPLES * 3:FRAME_SAMPLES * 6]
                                                    for channel in reference_pair))
    second_tail = second_controller.finish()

    reset_controller = OnlineController()
    reset_clip = tuple(channel[:FRAME_SAMPLES * 12] for channel in reference_pair)
    _feed(reset_controller, tuple(channel[:FRAME_SAMPLES * 3]
                                  for channel in reference_pair))
    stale_reset = reset_controller.reset(RESET_SCHEDULE["initial_epoch"],
                                         RESET_SCHEDULE["reset_first_input_sample"])
    reset_status = reset_controller.reset(RESET_SCHEDULE["reset_epoch"],
                                          RESET_SCHEDULE["reset_first_input_sample"])
    reset_position = reset_controller.process(
        tuple(channel[:FRAME_SAMPLES] for channel in reset_clip),
        epoch=RESET_SCHEDULE["reset_epoch"], first_input_sample=0).status
    reset_emitted: List[float] = []
    refresh_status = Status.OK
    for frame_start in range(0, len(reset_clip[0]), FRAME_SAMPLES):
        result = reset_controller.process(
            tuple(channel[frame_start:frame_start + FRAME_SAMPLES] for channel in reset_clip),
            epoch=RESET_SCHEDULE["reset_epoch"],
            first_input_sample=(RESET_SCHEDULE["reset_first_input_sample"] + frame_start
                                if frame_start == 0 else None),
            final=frame_start + FRAME_SAMPLES == len(reset_clip[0]))
        refresh_status = result.status
        reset_emitted.extend(result.samples)
    reset_result = reset_controller.finish(epoch=RESET_SCHEDULE["reset_epoch"])
    reset_full = tuple(reset_emitted + list(reset_result.samples))[:len(reset_clip[0])]
    replay_status, replay_expected = process_whole_clip(reset_clip)

    numerical = OnlineController()
    _feed(numerical, tuple((0.01,) * FRAME_SAMPLES * 3 for _ in range(INPUT_CHANNELS)))
    before = numerical.dsp_digest()
    good = tuple((0.01,) * FRAME_SAMPLES for _ in range(INPUT_CHANNELS))
    nonfinite = numerical.process(((math.nan,) * FRAME_SAMPLES, good[1]))
    nonfinite_c1 = numerical.process((good[0], (math.nan,) * FRAME_SAMPLES))
    missing_channel = numerical.process((good[0], None))
    delayed_channel = numerical.process(good, channel_positions=(0, FRAME_SAMPLES))
    wrong_shape = numerical.process((good[0], (0.0,) * (FRAME_SAMPLES + 1)))
    out_of_range = numerical.process(((9.0,) * FRAME_SAMPLES, good[1]))
    stale_epoch = numerical.process(good, epoch=99)
    stale_position = numerical.process(good, first_input_sample=123456)
    stale_session = numerical.process(good, session=2)
    after = numerical.dsp_digest()
    dsp_unchanged = before == after == numerical.dsp_digest()
    invalid_delta = numerical.state.invalid_count
    first_finalize = numerical.finish()
    finished_reuse = numerical.finish()
    process_after_finish = numerical.process(good).status

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
        ("wrong_channel_count", config_with(input_channels=1)),
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

    probe = causal_probe_pair()
    provider_off = probe[0]
    provider_on = _run_candidate(probe)
    upper_bound = offline_upper_bound_control()

    repeat_digests = [tensor_digest(_run_candidate(probe)) for _ in range(3)]
    if len(set(repeat_digests)) != 1:
        raise RuntimeError("three repeat passes are not byte-identical")
    repeatability = {
        "input_samples": len(probe[0]),
        "input_channels": INPUT_CHANNELS,
        "input_digests": [tensor_digest(probe[0]), tensor_digest(probe[1])],
        "runs": 3,
        "output_digests": repeat_digests,
        "byte_identical": len(set(repeat_digests)) == 1,
        "note": ("three fresh causal two-channel controllers over one pinned "
                 "synthetic probe; exact little-endian f32 digests, no "
                 "tolerance, no provider substitution"),
    }

    # The stacked predictor must actually use channel 1: with channel 0 held
    # fixed, changing only channel 1 must change the mono output. Forty frames
    # are needed because the eight-frame predictor delay and the three-frame
    # overlap-add delay must both elapse before the effect is emitted.
    influence_pair = two_channel_convolve(source, synthetic_rir_pair(
        ROOM_SPECS["short_rt60"]))[:2]
    channel0_fixed = influence_pair[0][:FRAME_SAMPLES * 40]
    channel1_zero = (0.0,) * len(channel0_fixed)
    channel1_alt = influence_pair[1][:FRAME_SAMPLES * 40]
    channel1_off_output = _run_candidate((channel0_fixed, channel1_zero))
    channel1_on_output = _run_candidate((channel0_fixed, channel1_alt))
    channel1_influence = {
        "channel0_digest": tensor_digest(channel0_fixed),
        "channel1_zero_digest": tensor_digest(channel1_zero),
        "channel1_active_digest": tensor_digest(channel1_alt),
        "output_with_silent_channel1": tensor_digest(channel1_off_output),
        "output_with_active_channel1": tensor_digest(channel1_on_output),
        "channel1_changes_output":
            tensor_digest(channel1_off_output) != tensor_digest(channel1_on_output),
        "note": ("the same channel-0 signal with a different channel-1 signal "
                 "produces a different mono output; no model or external asset"),
    }
    if not channel1_influence["channel1_changes_output"]:
        raise RuntimeError("channel 1 does not influence the multichannel output")

    causal_a = OnlineController()
    causal_b = OnlineController()
    prefix_a: List[Tuple[float, ...]] = []
    prefix_b: List[Tuple[float, ...]] = []
    shared_frames = 8
    for index in range(shared_frames):
        shared = tuple(channel[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
                       for channel in reference_pair)
        prefix_a.append(causal_a.process(shared).samples)
        prefix_b.append(causal_b.process(shared).samples)
    divergent = tuple(0.75 if index % 2 else -0.75 for index in range(FRAME_SAMPLES))
    future_pair = tuple(channel[shared_frames * FRAME_SAMPLES:
                                (shared_frames + 1) * FRAME_SAMPLES]
                        for channel in reference_pair)
    future_a = causal_a.process(future_pair).samples
    future_b = causal_b.process((future_pair[0], divergent)).samples
    trailing_a: List[Tuple[float, ...]] = []
    trailing_b: List[Tuple[float, ...]] = []
    trailing_frames = 16
    for index in range(shared_frames + 1, shared_frames + 1 + trailing_frames):
        shared = tuple(channel[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
                       for channel in reference_pair)
        trailing_a.append(causal_a.process(shared).samples)
        trailing_b.append(causal_b.process(shared).samples)
    later_digests = [tensor_digest(value) for value in (future_a, *trailing_a)]
    other_later_digests = [tensor_digest(value) for value in (future_b, *trailing_b)]
    first_divergent_later_frame = next(
        (index for index, (left, right) in enumerate(zip(later_digests, other_later_digests))
         if left != right), None)
    causality_probe = {
        "shared_input_frames": shared_frames,
        "divergent_channel": 1,
        "divergent_input_frame_index": shared_frames,
        "divergent_input_frame_samples": FRAME_SAMPLES,
        "trailing_identical_input_frames": trailing_frames,
        "emitted_frames_compared_before_divergence": len(prefix_a),
        "prefix_byte_identical": all(
            tensor_digest(left) == tensor_digest(right)
            for left, right in zip(prefix_a, prefix_b)),
        "future_frame_differs": first_divergent_later_frame is not None,
        "first_divergent_later_frame": first_divergent_later_frame,
        "emitted_frames_compared_after_divergence": len(later_digests),
        "note": ("identical stereo prefixes produce byte-identical emitted "
                 "frames even when the next channel-1 frame differs; the later "
                 "output diverges only after the eight-frame predictor delay "
                 "and three-frame overlap-add delay. Neither the stacked "
                 "predictor nor the WOLA path reads future input"),
    }
    if not (causality_probe["prefix_byte_identical"]
            and causality_probe["future_frame_differs"]):
        raise RuntimeError("causality probe failed")

    required_results = {
        "identity_noisy_controls": all(
            condition["variants"][label]["status"] == "scored"
            for condition in conditions.values()
            for label in ("identity_control", "noisy_identity_control")),
        "paired_si_sdr_stoi": all(
            condition["variants"][label]["status"] == "scored"
            for condition in conditions.values()
            for label in ("online_mc_wpe_candidate", "online_mc_wpe_on_noisy")),
        "synthetic_rir_stratification": len(conditions) == len(ROOM_SPECS),
        "early_reflection_target": all(
            condition["early_target_window_samples"] > 0
            for condition in conditions.values()),
        "echo_only_proxy": all(condition["echo_only"]["late_tail_proxy"]["status"] == "ok"
                               for condition in conditions.values()),
        "near_end_only_damage": all(row["status"] in ("scored", "control_exact")
                                    for row in near_variants.values()),
        "movement_control": all(row["status"] == "scored"
                                for row in movement_variants.values()),
        "overlap_control": all(row["status"] == "scored"
                               for row in overlap_variants.values()),
        "clean_near_end_preservation": preservation["online_mc_wpe_candidate"]["status"] == "scored",
        "peaks_and_invalid_outputs": True,
        "alignment_state_duration": (
            impulse_status is Status.OK and impulse_c1_status is Status.OK
            and silence_status is Status.OK and whole_status is Status.OK
            and chunk_status is Status.OK and partial_status is Status.OK),
        "multichannel_influence": channel1_influence["channel1_changes_output"],
        "causality_probe": (causality_probe["prefix_byte_identical"]
                            and causality_probe["future_frame_differs"]),
        "adverse_controls": dsp_unchanged and invalid_delta == 9,
    }
    all_present = all(required_results.values())
    if not all_present:
        raise RuntimeError("no missing result may qualify a candidate: " +
                           ", ".join(key for key, value in required_results.items() if not value))

    room_profile = {
        "profile": "room",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "claim": "acceptance structure applied to synthetic frozen fixtures only",
        "frozen": {
            "rir": {name: {"rt60_ms": spec["rt60_ms"],
                           "configured_direct_to_diffuse_db": spec["dr_db"],
                           "mic0_seed": spec["seed"],
                           "mic1_seed": spec["seed"] + GEOMETRY["mic1_rir_seed_offset"]}
                    for name, spec in ROOM_SPECS.items()},
            "geometry": GEOMETRY,
            "rate_hz": SAMPLE_RATE_HZ,
            "input_channels": INPUT_CHANNELS,
            "output_channels": OUTPUT_CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "excitation": "seeded analytic vowel-like near-end and far-end sources; not recorded speech",
            "noise_amplitude": NOISE_AMPLITUDE,
            "movement_gain_knots": list(MOVEMENT_GAIN_KNOTS),
            "reset_schedule": RESET_SCHEDULE,
            "early_target_window_ms": EARLY_WINDOW_MS,
            "content_delay_samples": CONTENT_DELAY_SAMPLES,
        },
        "mapped_cases": {
            "echo_only": {
                "fixture": "synthetic far-end-only excitation through both RIRs; no near-end",
                "evidence": ["conditions.*.echo_only"],
                "proxy_measure": "paired synthetic SI-SDR/STOI plus late-tail energy reduction; not measured echo attenuation",
            },
            "near_end_only": {
                "fixture": "anechoic synthetic near-end pair with delayed channel 1",
                "evidence": ["special_conditions.near_end_only", "clean_near_end_preservation"],
                "proxy_measure": "paired synthetic SI-SDR/STOI delta against the clean near-end",
            },
            "overlap": {
                "fixture": "delayed lower-pitched analytic second talker through both RIRs",
                "evidence": ["special_conditions.overlap_long"],
                "proxy_measure": "paired synthetic SI-SDR/STOI against the frozen early target",
            },
            "no_reference": {
                "fixture": "reference omitted from the scorer call",
                "evidence": ["adverse.missing_reference"],
                "proxy_measure": "explicit blocked status with null metrics; excluded from qualification",
            },
        },
        "reported": {
            "alignment": {"content_delay_samples": CONTENT_DELAY_SAMPLES,
                          "impulse_peak_index": impulse_peak_index(impulse_output),
                          "chunked_equals_stream": tensor_digest(whole_output)
                          == tensor_digest(chunk_output)},
            "echo_attenuation_proxy": {
                name: condition["echo_only"]["late_tail_proxy"]["late_energy_reduction_db"]
                for name, condition in conditions.items()},
            "near_end_damage": special_conditions["near_end_only"]["near_end_damage"],
            "nonfinite_failures": {"nonfinite_channel0": nonfinite.status.value,
                                   "nonfinite_channel1": nonfinite_c1.status.value,
                                   "nonfinite_count_in_scored_outputs": 0},
            "reset_behavior": {"status": reset_status.value,
                               "replay_matches_original":
                                   tensor_digest(reset_full) == tensor_digest(replay_expected)},
            "delayed_missing_channel": {
                "missing_channel": missing_channel.status.value,
                "delayed_channel": delayed_channel.status.value},
        },
        "not_applicable": {
            "delayed_or_missing_render": (
                "the far-end render in the echo-only fixture is a synthetic "
                "excitation with no render/echo-return timing calibration and no "
                "AEC-style cancellation target; delayed/missing render remains "
                "an explicit open gate for any AEC-style qualification"),
        },
        "not_reported": [
            "real RIRs or rooms", "measured room gain or echo attenuation",
            "listening or MOS", "target-device pacing or deadline results",
        ],
    }

    comparison: Dict[str, Any] = {}
    for name, condition in conditions.items():
        online_row = condition["variants"]["online_mc_wpe_candidate"]["metrics"]
        offline_row = upper_bound["conditions"][name]
        comparison[name] = {
            "causal_delta_si_sdr_db": online_row["delta_si_sdr_db"],
            "causal_delta_stoi": online_row["delta_stoi"],
            "noncausal_delta_si_sdr_db": offline_row["noncausal_delta_si_sdr_db"],
            "noncausal_delta_stoi": offline_row["noncausal_delta_stoi"],
            "note": (
                "Noncausal whole-clip mono WPE reads future frames and uses "
                "different geometry/hop/delay; it is an explicitly noncausal "
                "upper-bound reference point, not a like-for-like realtime result."),
        }

    report: Dict[str, Any] = {
        "schema_id": "audio-sdk/online-multichannel-wpe-report/0.1",
        "contract": CONTRACT_ID,
        "task": "SDK-ONLINE-MULTICHANNEL-WPE",
        "status": "proposal_only_not_qualified",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "processor_exposure",
        "scope": (
            "synthetic frame-causal two-channel WPE comparison against a "
            "generated early-reflection target; no real room, no listening, no "
            "model, no device timing and no release qualification"),
        "fixture_digest": object_digest(fixture_spec),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "input_channels": INPUT_CHANNELS,
            "output_channels": OUTPUT_CHANNELS,
            "input_frame_shape": [INPUT_CHANNELS, FRAME_SAMPLES],
            "output_frame_shape": [FRAME_SAMPLES],
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "processing_mode": "causal_frame_streaming",
            "realtime_v0_provider": False,
            "content_delay_samples": CONTENT_DELAY_SAMPLES,
            "content_delay_ms": CONTENT_DELAY_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "predictor_history_ms_min":
                WPE_DELAY_FRAMES * FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "predictor_history_ms_max":
                (WPE_DELAY_FRAMES + WPE_TAPS) * FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "flush_frames": FLUSH_FRAMES,
            "scoring_alignment": (
                "Candidate scores use a 480-sample (30 ms) content delay: the "
                "reference and mic-0 identity control are delayed by that amount "
                "and the candidate output is scored unshifted. Unaligned scores "
                "are recorded separately and are not used for comparison."),
            "note": (
                "One 160-sample mono output frame is returned per 2x160-sample "
                "input call. The first three output frames are causal priming "
                "silence; three final zero frames flush the overlap-add "
                "accumulator without reading future input."),
            "installed_v0_note": (
                "Installed v0 stays 16 kHz mono f32 at 160 samples/frame. This "
                "two-channel shape exists only at the opt-in task-local boundary."),
        },
        "provider": {
            "manifest": "provider.json",
            "identity": "online-multichannel-wpe-reference-provider/0.1",
            "default_enabled": False,
            "opt_in_required": True,
            "registered": False,
            "descriptor_settings": {},
            "c_abi_or_sdk_default_change": False,
            "c_boundary_included": False,
            "off_on_probe": {
                "input_samples": len(probe[0]),
                "input_channels": INPUT_CHANNELS,
                "input_digests": [tensor_digest(probe[0]), tensor_digest(probe[1])],
                "off_output_digest": tensor_digest(provider_off),
                "on_output_digest": tensor_digest(provider_on),
                "off_is_bit_exact_mic0_passthrough":
                    tensor_digest(provider_off) == tensor_digest(probe[0]),
                "on_differs_from_off":
                    tensor_digest(provider_on) != tensor_digest(provider_off),
            },
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "artifact_pins": ARTIFACT_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "base_commit": BASE_COMMIT,
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
                "external venv; synthetic scorer validation only, not a "
                "multichannel online oracle or real-speech MOS/STOI"),
        },
        "config": DEFAULT_CONFIG,
        "conditions": conditions,
        "special_conditions": special_conditions,
        "clean_near_end_preservation": preservation,
        "alignment_and_state": {
            "impulse": {"status": impulse_status.value,
                        "peak_index": impulse_peak_index(impulse_output),
                        "peak_abs": _round(max(abs(value) for value in impulse_output)),
                        "source_first_sample": 0,
                        "content_delay_samples": CONTENT_DELAY_SAMPLES,
                        "output_digest": tensor_digest(impulse_output)},
            "channel1_only_impulse": {
                "status": impulse_c1_status.value,
                "peak_index": impulse_c1_peak,
                "peak_abs": _round(max(abs(value) for value in impulse_c1_output)),
                "note": ("channel 1 has the impulse while channel 0 is silent; a "
                         "zero output is the expected non-injecting behavior, so "
                         "channel influence is probed separately"),
                "output_digest": tensor_digest(impulse_c1_output)},
            "channel1_influence": channel1_influence,
            "silence": {"status": silence_status.value, "frames": 40,
                        "peak_abs": _round(max(abs(value) for value in silence_output)),
                        "output_digest": tensor_digest(silence_output)},
            "duration": {"input_samples": len(reference_pair[0]),
                         "output_samples": len(whole_output),
                         "equal": len(reference_pair[0]) == len(whole_output)},
            "chunking_equivalence": {
                "chunk_sizes": schedule,
                "status": chunk_status.value,
                "stream_digest": tensor_digest(whole_output),
                "chunked_digest": tensor_digest(chunk_output),
                "equal": tensor_digest(whole_output) == tensor_digest(chunk_output),
            },
            "session_independence": {
                "first_digest": tensor_digest(first_tail.samples),
                "second_digest": tensor_digest(second_tail.samples),
                "independent": tensor_digest(first_tail.samples)
                               != tensor_digest(second_tail.samples),
                "statuses": [first_status.value, second_status.value],
            },
            "reset": {"stale_epoch_status": stale_reset.value,
                      "clip_samples": len(reset_clip[0]),
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
                "input_samples": len(partial_pair[0]),
                "output_samples": len(partial_output),
                "status": partial_status.value,
                "chunk_sizes": partial_schedule,
                "equal_duration": len(partial_pair[0]) == len(partial_output),
                "output_digest": tensor_digest(partial_output),
            },
            "buffering": {
                "ola_accumulator_samples": len(OnlineWpe.create(DEFAULT_CONFIG).ola),
                "history_frames_retained": OLA_DELAY_FRAMES + 4,
                "covariance_complex_values": (FFT_SIZE // 2 + 1)
                                             * (INPUT_CHANNELS * WPE_TAPS) ** 2,
                "description": ("host Python counts only; no target-device timing, "
                                "CPU, memory, pacing or deadline result"),
            },
            "causality_probe": causality_probe,
        },
        "adverse": {
            "frame_rejections": {
                "nonfinite_channel0": nonfinite.status.value,
                "nonfinite_channel1": nonfinite_c1.status.value,
                "missing_channel": missing_channel.status.value,
                "delayed_channel": delayed_channel.status.value,
                "wrong_shape": wrong_shape.status.value,
                "out_of_range": out_of_range.status.value,
                "stale_epoch": stale_epoch.status.value,
                "stale_position": stale_position.status.value,
                "stale_session": stale_session.status.value,
                "dsp_state_unchanged": dsp_unchanged,
                "invalid_count_delta": invalid_delta,
                "finalize_status": first_finalize.status.value,
                "finished_reuse": finished_reuse.status.value,
                "process_after_finish": process_after_finish.value,
            },
            "config_rejections": config_errors,
            "missing_reference": _metrics(None, (0.0,) * FRAME_SAMPLES,
                                          (0.0,) * FRAME_SAMPLES),
            "noisy_input_variants": "conditions.*.variants.online_mc_wpe_on_noisy",
        },
        "repeatability": repeatability,
        "room_profile": room_profile,
        "noncausal_upper_bound_control": upper_bound,
        "causal_vs_noncausal_comparison": comparison,
        "qualification": {
            "status": "not_qualified",
            "decision": "DEFER",
            "defer_before": "processor_exposure",
            "required_results": required_results,
            "all_required_results_present": all_present,
            "no_missing_result_may_qualify": True,
            "excluded_from_qualification": [
                "missing_reference control", "all adverse controls",
                "identity controls (bit-exact sanity checks)",
                "noncausal whole-clip WPE upper-bound control",
                "synthetic echo-attenuation proxy",
            ],
            "reasons": [
                "synthetic analytic excitation and synthetic RIR pairs only",
                "candidate regresses in multiple measured conditions",
                "no real-room/speech cohort, listening/MOS or real-speech STOI",
                "no target-device timing, CPU, memory or deadline result",
                "no render/echo-return timing evidence for AEC-style qualification",
                "provider is opt-in, unregistered and disabled by default",
            ],
            "reopen_gates": [
                "held-out real-room paired SI-SDR/STOI with pinned RIR provenance",
                "licensed-speech listening/MOS with a declared protocol",
                "target-device causal CPU, memory, pacing and deadline evidence",
                "render/echo-return delayed/missing case for any AEC-style scope",
                "provider intake, license, descriptor and catalog review",
            ],
        },
    }
    return report


def impulse_peak_index(values: Sequence[float]) -> int:
    return max(range(len(values)), key=lambda index: abs(values[index]))


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
