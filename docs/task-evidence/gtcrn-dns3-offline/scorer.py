# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local, dependency-free paired scorers for synthetic clean references.

``si_sdr`` follows the zero-mean, scale-invariant projection formula pinned in
``audio-benchmark-platform/audio-bench/src/audio_bench/metrics.py`` (revision
``zero-mean.v1``). ``stoi`` is a deterministic pure-Python port of the
*non-extended* pystoi 0.4.1 algorithm (Taal et al., 2010/2011) restricted to
the pinned 16 kHz synthetic fixtures here. It is not the audio-bench scorer,
is not extended STOI, and carries no real-speech or human-listening claim.

Degenerate comparisons return ``(None, reason)``; no missing score is ever
reported as a candidate result.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

SCORER_ID = "audio-sdk/gtcrn-dns3-offline-scoring/0.1"
PYSTOI_ALGORITHM_PIN = "pystoi-0.4.1.non-extended.algorithm-port"
BENCH_SI_SDR_REVISION = "zero-mean.v1"

_EPS = 2.220446049250313e-16  # numpy float64 eps
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


def si_sdr(reference: Sequence[float], estimate: Sequence[float]) -> Tuple[Optional[float], Optional[str]]:
    """Zero-mean SI-SDR in dB, with explicit reasons for undefined cases."""
    pair = _pair(reference, estimate)
    if pair is None:
        return None, "invalid_input"
    clean, output = pair
    clean_mean = math.fsum(clean) / len(clean)
    output_mean = math.fsum(output) / len(output)
    centered_clean = [value - clean_mean for value in clean]
    centered_output = [value - output_mean for value in output]
    reference_energy = math.fsum(value * value for value in centered_clean)
    if reference_energy <= 0.0:
        return None, "zero_reference_energy"
    alpha = math.fsum(a * b for a, b in zip(centered_output, centered_clean)) / reference_energy
    target = [alpha * value for value in centered_clean]
    target_energy = math.fsum(value * value for value in target)
    if target_energy <= 0.0:
        return None, "zero_output_energy"
    residual_energy = math.fsum(
        (value - projected) ** 2 for value, projected in zip(centered_output, target)
    )
    if residual_energy <= 0.0:
        return None, "perfect_reconstruction"
    return 10.0 * math.log10(target_energy / residual_energy), None


def si_sdr_improvement(
    reference: Sequence[float], estimate: Sequence[float], raw: Sequence[float]
) -> Tuple[Optional[float], Optional[str]]:
    """Paired SI-SDR(output) - SI-SDR(noisy input)."""
    output, output_reason = si_sdr(reference, estimate)
    baseline, baseline_reason = si_sdr(reference, raw)
    if output_reason or baseline_reason:
        return None, output_reason or baseline_reason
    assert output is not None and baseline is not None
    return output - baseline, None


# ---- deterministic DSP helpers ------------------------------------------------

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


def stoi(reference: Sequence[float], estimate: Sequence[float], rate: int = 16000) -> Tuple[Optional[float], Optional[str]]:
    """Non-extended STOI index on paired synthetic signals, or (None, reason)."""
    pair = _pair(reference, estimate)
    if pair is None:
        return None, "invalid_input"
    clean, output = pair
    if not any(clean):
        return None, "insufficient_active_speech"
    if rate == 16000:
        clean = _resample_16k_to_10k(clean)
        output = _resample_16k_to_10k(output)
    elif rate != _STOI_FS:
        return None, "unsupported_rate"
    clean, output = _remove_silent_frames(clean, output)
    clean_bands = _band_energies(clean)
    output_bands = _band_energies(output)
    frames = len(clean_bands[0]) if clean_bands else 0
    if frames < _STOI_N:
        return None, "insufficient_active_speech"
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
    return total / (segments * len(clean_bands)), None
