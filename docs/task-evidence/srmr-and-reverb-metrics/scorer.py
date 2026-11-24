# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free SRMR scorer for the pinned synthetic evidence cohort.

This is a deterministic pure-Python port of the *fast* SRMR path in SRMRpy
(commit ``fee009779cef96bed34db3a7e31d10f3ad1ea133``; MIT) and its Gammatone
1.0.3 FFT-filterbank dependency (BSD-3-Clause). Exact upstream URLs, archive
digests and per-file digests are pinned in ``SOURCES.sha256`` and the report.
The port is scoped to 16 kHz mono f32-shaped clips and is not an SDK provider,
not the audio-bench scorer and not a real-speech or human-listening claim.

Degenerate or missing inputs return ``(None, reason)``; no missing score is
ever reported as a candidate result.
"""

from __future__ import annotations

import cmath
import math
from typing import Dict, List, Optional, Sequence, Tuple

SCORER_ID = "audio-sdk/srmr-reverb-evidence-scoring/0.1"
UPSTREAM_SCORER_ID = "SRMRpy/fee009779cef96bed34db3a7e31d10f3ad1ea133.fast"
UPSTREAM_GAMMATONE_ID = "Gammatone/1.0.3.fft-gtgram"
SAMPLE_RATE_HZ = 16000
MIN_SAMPLES = 8192
EAR_Q = 9.26449
MIN_BW = 24.7
N_COCHLEAR_FILTERS = 23
LOW_FREQ_HZ = 125.0
MIN_MODULATION_CF_HZ = 4.0
MAX_MODULATION_CF_HZ = 128.0
N_MODULATION_FILTERS = 8
MODULATION_SAMPLE_RATE_HZ = 400.0
FFT_WINDOW_S = 0.010
FFT_HOP_S = 0.0025
MODULATION_WINDOW_S = 0.256
MODULATION_HOP_S = 0.064
FILTER_Q = 2.0
CROSSCHECK_ABS_TOLERANCE = 1e-9
Matrix = List[List[float]]


def _erb_point(low_freq: float, high_freq: float, fraction: float) -> float:
    offset = EAR_Q * MIN_BW
    return -offset + math.exp(
        fraction * (-math.log(high_freq + offset) + math.log(low_freq + offset))
    ) * (high_freq + offset)


def erb_space(low_freq: float, high_freq: float, count: int) -> List[float]:
    return [_erb_point(low_freq, high_freq, index / count) for index in range(1, count + 1)]


def centre_freqs(sample_rate_hz: float, count: int, cutoff_hz: float) -> List[float]:
    return erb_space(cutoff_hz, sample_rate_hz / 2.0, count)


def _make_erb_filters(sample_rate_hz: float, cfs: Sequence[float],
                      width: float = 1.0) -> Dict[str, List[float]]:
    t = 1.0 / sample_rate_hz
    erbs = [width * ((cf / EAR_Q) + MIN_BW) for cf in cfs]
    bandwidths = [1.019 * 2.0 * math.pi * erb for erb in erbs]
    args = [2.0 * cf * math.pi * t for cf in cfs]
    vectors = [cmath.exp(2j * arg) for arg in args]
    rt_pos = math.sqrt(3.0 + 2.0 ** 1.5)
    rt_neg = math.sqrt(3.0 - 2.0 ** 1.5)
    b1 = [-2.0 * math.cos(arg) / math.exp(bw * t) for arg, bw in zip(args, bandwidths)]
    b2 = [math.exp(-2.0 * bw * t) for bw in bandwidths]
    common = [-t * math.exp(-bw * t) for bw in bandwidths]
    k11 = [math.cos(arg) + rt_pos * math.sin(arg) for arg in args]
    k12 = [math.cos(arg) - rt_pos * math.sin(arg) for arg in args]
    k13 = [math.cos(arg) + rt_neg * math.sin(arg) for arg in args]
    k14 = [math.cos(arg) - rt_neg * math.sin(arg) for arg in args]
    gain: List[float] = []
    for vector, arg, bw, k1, k2, k3, k4 in zip(
            vectors, args, bandwidths, k11, k12, k13, k14):
        gain_arg = cmath.exp(1j * arg - bw * t)
        numerator = ((vector - gain_arg * k1) * (vector - gain_arg * k2)
                     * (vector - gain_arg * k3) * (vector - gain_arg * k4))
        denominator = (
            t * cmath.exp(bw * t)
            / (-1.0 / cmath.exp(bw * t) + 1.0 + vector * (1.0 - cmath.exp(bw * t)))
        ) ** 4
        gain.append(abs(numerator * denominator))
    return {
        "a11": [value * k for value, k in zip(common, k11)],
        "a12": [value * k for value, k in zip(common, k12)],
        "a13": [value * k for value, k in zip(common, k13)],
        "a14": [value * k for value, k in zip(common, k14)],
        "b1": b1,
        "b2": b2,
        "gain": gain,
    }


def _fft_weights(sample_rate_hz: float, nfft: int, channels: int,
                 low_freq_hz: float) -> Matrix:
    ucirc = [cmath.exp(1j * 2.0 * math.pi * k / nfft) for k in range(nfft // 2 + 1)]
    cfs = erb_space(low_freq_hz, sample_rate_hz / 2.0, channels)[::-1]
    coefs = _make_erb_filters(sample_rate_hz, cfs)
    poles = [
        math.sqrt(b2) * cmath.exp(1j * 2.0 * math.pi * cf / sample_rate_hz)
        for cf, b2 in zip(cfs, coefs["b2"])
    ]
    weights: Matrix = []
    for index in range(channels):
        row: List[float] = []
        pole = poles[index]
        a11 = coefs["a11"][index] * sample_rate_hz
        a12 = coefs["a12"][index] * sample_rate_hz
        a13 = coefs["a13"][index] * sample_rate_hz
        a14 = coefs["a14"][index] * sample_rate_hz
        for unit in ucirc:
            numerator = (abs(unit + a11) * abs(unit + a12)
                         * abs(unit + a13) * abs(unit + a14))
            denominator = abs(sample_rate_hz * (pole - unit)
                              * (pole.conjugate() - unit)) ** 4
            row.append(numerator / denominator / coefs["gain"][index])
        weights.append(row)
    return weights


def fft(values: Sequence[complex], inverse: bool = False) -> List[complex]:
    """Iterative radix-2 Cooley-Tukey transform; length must be a power of two."""
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
    return [value / size for value in result] if inverse else result


def fft_convolve(source: Sequence[float], taps: Sequence[float],
                 count: int) -> List[float]:
    """Round f64 inverse-FFT output to 15 decimals for pinned reproducibility."""
    size = 1
    while size < len(source) + len(taps) - 1:
        size <<= 1
    left = fft(list(source) + [0j] * (size - len(source)))
    right = fft(list(taps) + [0j] * (size - len(taps)))
    result = fft([a * b for a, b in zip(left, right)], inverse=True)
    return [round(value.real, 15) for value in result[:count]]


def _round_half_away_from_zero(value: float) -> int:
    return int(math.copysign(math.floor(abs(value) + 0.5), value))


def _specgram_window(nfft: int, window_samples: int) -> List[float]:
    halflen = window_samples // 2
    halff = nfft // 2
    active = int(math.floor(min(halff, halflen)))
    halfwin = [0.5 * (1.0 + math.cos(math.pi * n / halflen))
               for n in range(halflen + 1)]
    window = [0.0] * nfft
    for index in range(active):
        window[halff + index] = halfwin[index]
        window[halff - index] = halfwin[index]
    return window


def _specgram(values: Sequence[float], nfft: int, window_samples: int,
              hop_samples: int) -> List[List[complex]]:
    columns = 1 + int(math.floor((len(values) - nfft) / hop_samples))
    result = [[0j] * columns for _ in range(nfft // 2 + 1)]
    window = _specgram_window(nfft, window_samples)
    column = 0
    for start in range(0, len(values) - nfft, hop_samples):
        spectrum = fft([window[index] * values[start + index]
                        for index in range(nfft)])
        for bin_index in range(nfft // 2 + 1):
            result[bin_index][column] = spectrum[bin_index]
        column += 1
    return result


def _fft_gtgram(values: Sequence[float], sample_rate_hz: float) -> Matrix:
    window_samples = _round_half_away_from_zero(FFT_WINDOW_S * sample_rate_hz)
    hop_samples = _round_half_away_from_zero(FFT_HOP_S * sample_rate_hz)
    nfft = int(2 ** math.ceil(math.log2(2.0 * FFT_WINDOW_S * sample_rate_hz)))
    weights = _fft_weights(sample_rate_hz, nfft, N_COCHLEAR_FILTERS, LOW_FREQ_HZ)
    spectrogram = _specgram(values, nfft, window_samples, hop_samples)
    columns = len(spectrogram[0])
    result: Matrix = []
    for row in weights:
        result.append([
            math.fsum(row[index] * abs(spectrogram[index][column])
                      for index in range(len(row))) / nfft
            for column in range(columns)
        ])
    return result


def _compute_modulation_cfs() -> List[float]:
    spacing = (MAX_MODULATION_CF_HZ / MIN_MODULATION_CF_HZ) ** (
        1.0 / (N_MODULATION_FILTERS - 1))
    cfs = [MIN_MODULATION_CF_HZ]
    for _ in range(1, N_MODULATION_FILTERS):
        cfs.append(cfs[-1] * spacing)
    return cfs


def _modulation_filterbank(cfs: Sequence[float]) -> List[Tuple[List[float], List[float]]]:
    filters: List[Tuple[List[float], List[float]]] = []
    for cf in cfs:
        w0 = 2.0 * math.pi * cf / MODULATION_SAMPLE_RATE_HZ
        w = math.tan(w0 / 2.0)
        b0 = w / FILTER_Q
        numerator = [b0, 0.0, -b0]
        denominator = [1.0 + b0 + w * w, 2.0 * w * w - 2.0, 1.0 - b0 + w * w]
        filters.append((numerator, denominator))
    return filters


def _lfilter(numerator: Sequence[float], denominator: Sequence[float],
             values: Sequence[float]) -> List[float]:
    b = [value / denominator[0] for value in numerator]
    a1 = denominator[1] / denominator[0]
    a2 = denominator[2] / denominator[0]
    output = [0.0] * len(values)
    z1 = z2 = 0.0
    for index, value in enumerate(values):
        current = b[0] * value + z1
        z1 = b[1] * value - a1 * current + z2
        z2 = b[2] * value - a2 * current
        output[index] = current
    return output


def _calc_erbs(sample_rate_hz: float) -> List[float]:
    return [((cf / EAR_Q) + MIN_BW)
            for cf in centre_freqs(sample_rate_hz, N_COCHLEAR_FILTERS, LOW_FREQ_HZ)]


def _calc_cutoffs(cfs: Sequence[float], sample_rate_hz: float) -> List[float]:
    cutoffs: List[float] = []
    for cf in cfs:
        w0 = 2.0 * math.pi * cf / sample_rate_hz
        half_bandwidth = (math.tan(w0 / 2.0) / FILTER_Q) * sample_rate_hz / (2.0 * math.pi)
        cutoffs.append(cf - half_bandwidth)
    return cutoffs


def _srmr_unchecked(values: Sequence[float], sample_rate_hz: float) -> Tuple[float, int, float]:
    gt_env = _fft_gtgram(values, sample_rate_hz)
    window_length = int(math.ceil(MODULATION_WINDOW_S * MODULATION_SAMPLE_RATE_HZ))
    window_inc = int(math.ceil(MODULATION_HOP_S * MODULATION_SAMPLE_RATE_HZ))
    modulation_cfs = _compute_modulation_cfs()
    filters = _modulation_filterbank(modulation_cfs)
    frame_count = 1 + (len(gt_env[0]) - window_length) // window_inc
    if frame_count < 1:
        raise ValueError("insufficient_modulation_frames")
    # scipy.signal.windows.hamming(104)[:-1] with its default sym=True.
    window = [
        0.54 - 0.46 * math.cos(2.0 * math.pi * n / window_length)
        for n in range(window_length)
    ]
    average: Matrix = []
    for acoustic_channel in gt_env:
        modulated = [_lfilter(numerator, denominator, acoustic_channel)
                     for numerator, denominator in filters]
        acoustic_average: List[float] = []
        for channel in modulated:
            energies: List[float] = []
            for frame in range(frame_count):
                start = frame * window_inc
                energies.append(math.fsum(
                    (window[index] * channel[start + index]
                     if start + index < len(channel) else 0.0) ** 2
                    for index in range(window_length)
                ))
            acoustic_average.append(math.fsum(energies) / frame_count)
        average.append(acoustic_average)

    erbs = _calc_erbs(sample_rate_hz)[::-1]
    total = math.fsum(math.fsum(row) for row in average)
    if total <= 0.0:
        raise ValueError("zero_modulation_energy")
    acoustic_energy = [math.fsum(row) for row in average]
    cumulative = 0.0
    bandwidth_index: Optional[int] = None
    for index, value in enumerate([energy * 100.0 / total for energy in acoustic_energy][::-1]):
        cumulative += value
        if cumulative > 90.0:
            bandwidth_index = index
            break
    if bandwidth_index is None:
        raise ValueError("undefined_acoustic_bandwidth")
    bandwidth = erbs[bandwidth_index]
    cutoffs = _calc_cutoffs(modulation_cfs, sample_rate_hz)
    if cutoffs[4] < bandwidth < cutoffs[5]:
        k_star = 5
    elif cutoffs[5] < bandwidth < cutoffs[6]:
        k_star = 6
    elif cutoffs[6] < bandwidth < cutoffs[7]:
        k_star = 7
    elif bandwidth > cutoffs[7]:
        k_star = 8
    else:
        raise ValueError("undefined_modulation_bandwidth")
    numerator = math.fsum(math.fsum(row[:4]) for row in average)
    denominator = math.fsum(math.fsum(row[4:k_star]) for row in average)
    if denominator <= 0.0:
        raise ValueError("zero_denominator_energy")
    return numerator / denominator, k_star, bandwidth


def srmr(samples: Optional[Sequence[float]],
         sample_rate_hz: float = SAMPLE_RATE_HZ) -> Tuple[Optional[float], Optional[str]]:
    """Return the pinned SRMR value or ``(None, reason)`` for invalid inputs."""
    if samples is None:
        return None, "missing_samples"
    if isinstance(samples, (str, bytes)):
        return None, "invalid_samples"
    try:
        values = list(samples)
    except TypeError:
        return None, "invalid_samples"
    if not values:
        return None, "empty_samples"
    if len(values) < MIN_SAMPLES:
        return None, "short_samples"
    if sample_rate_hz != SAMPLE_RATE_HZ:
        return None, "unsupported_sample_rate"
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           for value in values):
        return None, "invalid_samples"
    if any(not math.isfinite(float(value)) for value in values):
        return None, "nonfinite_samples"
    floats = [float(value) for value in values]
    if math.fsum(value * value for value in floats) <= 0.0:
        return None, "zero_energy"
    try:
        score, _, _ = _srmr_unchecked(floats, float(sample_rate_hz))
    except ValueError as error:
        return None, str(error)
    if not math.isfinite(score):
        return None, "nonfinite_score"
    return score, None
