# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local, dependency-free paired STOI and ESTOI scorers.

Both scorers are deterministic, no-dither ports of the *pinned* pystoi 0.4.1
source (``pystoi/stoi.py`` with ``extended=False`` and ``extended=True`` and
``pystoi/utils.py``) restricted to the 16 kHz mono synthetic fixtures here.
The only intentional difference from upstream is omission of pystoi's
machine-epsilon Gaussian dither in ``row_col_normalize``; this makes repeated
scores byte-identical and is measured against the pinned upstream implementation
in ``crosscheck_vectors.json``.  Neither scorer is an audio-bench metric, a
human intelligibility measurement, or a real-speech claim.

Degenerate comparisons return ``(None, reason)``; no missing score is ever
reported as a candidate result.
"""

from __future__ import annotations

from functools import lru_cache
import math
from typing import Dict, List, Optional, Sequence, Tuple

SCORER_ID = "audio-sdk/stoi-estoi-scoring/0.1"
PYSTOI_VERSION = "0.4.1"
PYSTOI_ALGORITHM_PINS = (
    "pystoi-0.4.1.non-extended.algorithm-port.no-dither",
    "pystoi-0.4.1.extended.algorithm-port.no-dither",
)
PYSTOI_SOURCE_SHA256 = {
    "pystoi/stoi.py": "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658",
    "pystoi/utils.py": "0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321",
}

_EPS = 2.220446049250313e-16  # numpy float64 eps used by pystoi 0.4.1
_STOI_FS = 10000
_STOI_N_FRAME = 256
_STOI_NFFT = 512
_STOI_NUM_BANDS = 15
_STOI_MIN_FREQ = 150.0
_STOI_N = 30
_STOI_BETA = -15.0
_STOI_DYN_RANGE = 40.0


def _pair(reference: Sequence[float], estimate: Sequence[float]) -> Optional[Tuple[List[float], List[float]]]:
    if len(reference) != len(estimate) or not reference:
        return None
    left, right = list(reference), list(estimate)
    if not all(math.isfinite(value) for value in left + right):
        return None
    return left, right


# ---- deterministic DSP helpers (ported from the pinned pystoi algorithm) ----

def _fft(values: Sequence[complex], inverse: bool = False) -> List[complex]:
    """Iterative radix-2 Cooley-Tukey FFT; input length must be a power of two."""
    size = len(values)
    if size == 0 or size & (size - 1):
        raise ValueError("fft length must be a positive power of two")
    result = list(values)
    reverse = 0
    for index in range(1, size):
        bit = size >> 1
        while reverse & bit:
            reverse ^= bit
            bit >>= 1
        reverse |= bit
        if index < reverse:
            result[index], result[reverse] = result[reverse], result[index]
    step = 2
    while step <= size:
        angle = (2.0 * math.pi / step) * (1.0 if inverse else -1.0)
        root = complex(math.cos(angle), math.sin(angle))
        half = step >> 1
        for start in range(0, size, step):
            twiddle = 1.0 + 0.0j
            for offset in range(half):
                even = result[start + offset]
                odd = result[start + offset + half] * twiddle
                result[start + offset] = even + odd
                result[start + offset + half] = even - odd
                twiddle *= root
        step <<= 1
    if inverse:
        result = [value / size for value in result]
    return result


def _hann(length: int) -> List[float]:
    # Equivalent to numpy.hanning(length + 2)[1:-1], used by pystoi.
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * (n + 1) / (length + 1)) for n in range(length)]


def _i0(value: float) -> float:
    """Modified Bessel I0 by its convergent power series (|value| <= 5.7 here)."""
    term = 1.0
    total = 1.0
    quarter = value * value / 4.0
    for index in range(1, 128):
        term *= quarter / (index * index)
        total += term
        if term <= 1e-18 * total:
            break
    return total


def _resample_window(up: int, down: int) -> List[float]:
    rejection_db = 60.0
    stopband = 1.0 / (2 * max(up, down))
    roll_off = stopband / 10.0
    length = int(math.ceil((rejection_db - 8.0) / (28.714 * roll_off)))
    beta = 0.1102 * (rejection_db - 8.7)
    denominator = _i0(beta)
    taps: List[float] = []
    for n in range(-length, length + 1):
        sinc_argument = 2.0 * stopband * n
        ideal = 2.0 * up * stopband * (
            1.0 if sinc_argument == 0.0 else math.sin(math.pi * sinc_argument) / (math.pi * sinc_argument)
        )
        position = n / length
        kaiser = _i0(beta * math.sqrt(max(0.0, 1.0 - position * position))) / denominator
        taps.append(ideal * kaiser)
    # scipy multiplies the normalized pystoi window by the upsampling factor.
    total = math.fsum(taps)
    return [tap * up / total for tap in taps]


def _resample_16k_to_10k(values: Sequence[float]) -> List[float]:
    """Direct polyphase form of scipy.signal.resample_poly(x, 5, 8) with a Kaiser window."""
    up, down = 5, 8
    taps = _resample_window(up, down)
    half_length = (len(taps) - 1) // 2
    pre_pad = (down - half_length % down) % down
    padded = [0.0] * pre_pad + taps
    pre_remove = (half_length + pre_pad) // down
    n_out = (len(values) * up) // down + bool((len(values) * up) % down)
    banks: List[List[Tuple[int, float]]] = [[] for _ in range(up)]
    for index, coefficient in enumerate(padded):
        banks[index % up].append((index // up, coefficient))
    output: List[float] = []
    for sample in range(n_out):
        up_index = (pre_remove + sample) * down
        phase = up_index % up
        base = up_index // up
        total = 0.0
        for delay, coefficient in banks[phase]:
            source_index = base - delay
            if 0 <= source_index < len(values):
                total += coefficient * values[source_index]
        output.append(total)
    return output


def _windowed_frames(values: Sequence[float], window: Sequence[float], hop: int) -> List[List[float]]:
    length = len(window)
    return [
        [values[start + index] * window[index] for index in range(length)]
        for start in range(0, len(values) - length, hop)
    ]


def _overlap_add(frames: Sequence[Sequence[float]], hop: int) -> List[float]:
    if not frames:
        return []
    length = (len(frames) - 1) * hop + len(frames[0])
    output = [0.0] * length
    for index, frame in enumerate(frames):
        start = index * hop
        for offset, value in enumerate(frame):
            output[start + offset] += value
    return output


def _remove_silent_frames(clean: Sequence[float], estimate: Sequence[float]) -> Tuple[List[float], List[float]]:
    window = _hann(_STOI_N_FRAME)
    hop = _STOI_N_FRAME // 2
    clean_frames = _windowed_frames(clean, window, hop)
    estimate_frames = _windowed_frames(estimate, window, hop)
    energies = [
        20.0 * math.log10(math.sqrt(math.fsum(value * value for value in frame)) + _EPS)
        for frame in clean_frames
    ]
    if not energies:
        return [], []
    threshold = max(energies) - _STOI_DYN_RANGE
    keep = [index for index, energy in enumerate(energies) if threshold - energy < 0.0]
    return (
        _overlap_add([clean_frames[index] for index in keep], hop),
        _overlap_add([estimate_frames[index] for index in keep], hop),
    )


def _third_octave_matrix() -> List[List[int]]:
    bins = [_STOI_FS * index / _STOI_NFFT for index in range(_STOI_NFFT // 2 + 1)]

    def nearest(frequency: float) -> int:
        return min(range(len(bins)), key=lambda index: (bins[index] - frequency) ** 2)

    matrix: List[List[int]] = []
    for band in range(_STOI_NUM_BANDS):
        low = _STOI_MIN_FREQ * 2.0 ** ((2 * band - 1) / 6)
        high = _STOI_MIN_FREQ * 2.0 ** ((2 * band + 1) / 6)
        matrix.append(list(range(nearest(low), nearest(high))))
    return matrix


_OCTAVE_BANDS = _third_octave_matrix()


def _band_energies(values: Sequence[float]) -> List[List[float]]:
    window = _hann(_STOI_N_FRAME)
    hop = _STOI_N_FRAME // 2
    output: List[List[float]] = []
    for frame in _windowed_frames(values, window, hop):
        spectrum = _fft([complex(value, 0.0) for value in frame] + [0j] * (_STOI_NFFT - len(frame)))
        magnitudes = [abs(value) ** 2 for value in spectrum[: _STOI_NFFT // 2 + 1]]
        output.append([math.sqrt(math.fsum(magnitudes[index] for index in band)) for band in _OCTAVE_BANDS])
    # pystoi stores spectrograms as (band, frame); transpose for segment slicing.
    bands = len(_OCTAVE_BANDS)
    return [[output[frame][band] for frame in range(len(output))] for band in range(bands)]


@lru_cache(maxsize=128)
def _cached_bands(clean: Tuple[float, ...], output: Tuple[float, ...], rate: int
                  ) -> Tuple[Tuple[Tuple[float, ...], ...], Tuple[Tuple[float, ...], ...]]:
    """Resample and band-analyze a matched pair once; tuples keep repeats exact."""
    if rate == 16000:
        clean_values = _resample_16k_to_10k(clean)
        output_values = _resample_16k_to_10k(output)
    else:
        clean_values, output_values = list(clean), list(output)
    clean_values, output_values = _remove_silent_frames(clean_values, output_values)
    clean_bands = _band_energies(clean_values)
    output_bands = _band_energies(output_values)
    return (
        tuple(tuple(band) for band in clean_bands),
        tuple(tuple(band) for band in output_bands),
    )


def _bands(reference: Sequence[float], estimate: Sequence[float], rate: int
           ) -> Tuple[Optional[Tuple[Tuple[float, ...], ...]], Optional[Tuple[Tuple[float, ...], ...]], Optional[str]]:
    pair = _pair(reference, estimate)
    if pair is None:
        return None, None, "invalid_input"
    clean, output = pair
    if not any(clean):
        return None, None, "insufficient_active_speech"
    if rate not in (16000, _STOI_FS):
        return None, None, "unsupported_rate"
    clean_bands, output_bands = _cached_bands(tuple(clean), tuple(output), rate)
    if not clean_bands or len(clean_bands[0]) < _STOI_N:
        return None, None, "insufficient_active_speech"
    return clean_bands, output_bands, None


def _stoi_bands(clean_bands: Sequence[Sequence[float]],
                output_bands: Sequence[Sequence[float]]) -> float:
    frames = len(clean_bands[0])
    clip_value = 10.0 ** (-_STOI_BETA / 20.0)
    total = 0.0
    segments = 0
    for end in range(_STOI_N, frames + 1):
        start = end - _STOI_N
        x_segment = [band[start:end] for band in clean_bands]
        y_segment = [band[start:end] for band in output_bands]
        for band_index in range(len(x_segment)):
            x_values = x_segment[band_index]
            y_values = y_segment[band_index]
            x_norm = math.sqrt(math.fsum(value * value for value in x_values))
            y_norm = math.sqrt(math.fsum(value * value for value in y_values))
            scale = x_norm / (y_norm + _EPS)
            clipped = [
                min(value * scale, reference_value * (1.0 + clip_value))
                for value, reference_value in zip(y_values, x_values)
            ]
            x_mean = math.fsum(x_values) / _STOI_N
            y_mean = math.fsum(clipped) / _STOI_N
            x_centered = [value - x_mean for value in x_values]
            y_centered = [value - y_mean for value in clipped]
            x_length = math.sqrt(math.fsum(value * value for value in x_centered))
            y_length = math.sqrt(math.fsum(value * value for value in y_centered))
            x_unit = [value / (x_length + _EPS) for value in x_centered]
            y_unit = [value / (y_length + _EPS) for value in y_centered]
            total += math.fsum(a * b for a, b in zip(x_unit, y_unit))
        segments += 1
    # pystoi calls the two remaining axes J (segments) and M (bands).
    return total / (segments * len(clean_bands))


def _row_col_normalize(segment: Sequence[Sequence[float]]) -> Optional[List[List[float]]]:
    """Deterministic no-dither port of pystoi.utils.row_col_normalize."""
    rows = []
    for values in segment:
        mean = math.fsum(values) / len(values)
        centered = [value - mean for value in values]
        norm = math.sqrt(math.fsum(value * value for value in centered))
        if norm == 0.0:
            return None
        rows.append([value / norm for value in centered])
    for index in range(_STOI_N):
        column = [row[index] for row in rows]
        mean = math.fsum(column) / len(column)
        centered = [value - mean for value in column]
        norm = math.sqrt(math.fsum(value * value for value in centered))
        if norm == 0.0:
            return None
        for row_index, row in enumerate(rows):
            row[index] = centered[row_index] / norm
    return rows


def _estoi_bands(clean_bands: Sequence[Sequence[float]],
                 output_bands: Sequence[Sequence[float]]) -> Optional[float]:
    frames = len(clean_bands[0])
    total = 0.0
    segments = 0
    for end in range(_STOI_N, frames + 1):
        start = end - _STOI_N
        x_normalized = _row_col_normalize([band[start:end] for band in clean_bands])
        y_normalized = _row_col_normalize([band[start:end] for band in output_bands])
        if x_normalized is None or y_normalized is None:
            return None
        for x_row, y_row in zip(x_normalized, y_normalized):
            total += math.fsum(a * b for a, b in zip(x_row, y_row))
        segments += 1
    # pystoi: sum(x_n * y_n / N) / J, where x_n shape is (J, M, N).
    # Row normalization makes each band unit-energy; column normalization then
    # makes each time slice unit-energy, so the total is at most N per segment.
    return total / (segments * _STOI_N)


def scores(reference: Sequence[float], estimate: Sequence[float], rate: int = 16000
           ) -> Dict[str, Tuple[Optional[float], Optional[str]]]:
    """Compute both pinned scores from one matched pair, with explicit reasons."""
    clean_bands, output_bands, reason = _bands(reference, estimate, rate)
    if reason or clean_bands is None or output_bands is None:
        return {
            "stoi": (None, reason),
            "estoi": (None, reason),
        }
    estoi = _estoi_bands(clean_bands, output_bands)
    return {
        "stoi": (_stoi_bands(clean_bands, output_bands), None),
        "estoi": (estoi, None if estoi is not None else "degenerate_extended_normalization"),
    }


def stoi(reference: Sequence[float], estimate: Sequence[float],
         rate: int = 16000) -> Tuple[Optional[float], Optional[str]]:
    """Non-extended STOI index on paired synthetic signals, or (None, reason)."""
    return scores(reference, estimate, rate)["stoi"]


def extended_stoi(reference: Sequence[float], estimate: Sequence[float],
                  rate: int = 16000) -> Tuple[Optional[float], Optional[str]]:
    """Extended STOI (ESTOI) index on paired synthetic signals, or (None, reason)."""
    return scores(reference, estimate, rate)["estoi"]
