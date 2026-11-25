# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free paired scorers for the synthetic WebRTC-APM-NS evidence.

``si_sdr`` is the zero-mean, scale-invariant projection measure. ``stoi_style``
is a deterministic, task-local intelligibility *proxy* with STOI-like band
envelopes; it is not pystoi, not extended STOI, not an audio-bench metric and
not a human-listening result. Every degenerate comparison returns
``(None, reason)`` so a missing or invalid score can never qualify a variant.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

SCORER_ID = "audio-sdk/webrtc-apm-ns-scoring/0.1"
SI_SDR_REVISION = "zero-mean.v1"
STOI_STYLE_REVISION = "synthetic-stoi-style.v1"

_SAMPLE_RATE_HZ = 16000
_FFT_SIZE = 512
_HOP_SIZE = 128
_BAND_COUNT = 15
_BAND_LOW_HZ = 150.0
_BAND_HIGH_HZ = 4000.0
_DYNAMIC_RANGE_DB = 40.0
_EPS = 1e-12


def _pair(reference: Sequence[float], estimate: Sequence[float]) -> Optional[Tuple[List[float], List[float]]]:
    if len(reference) != len(estimate) or not reference:
        return None
    left, right = [float(value) for value in reference], [float(value) for value in estimate]
    if not all(math.isfinite(value) for value in left + right):
        return None
    return left, right


def si_sdr(reference: Sequence[float], estimate: Sequence[float]) -> Tuple[Optional[float], Optional[str]]:
    """Zero-mean SI-SDR in dB; perfect reconstruction is explicitly undefined."""
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
    residual = math.fsum(
        (value - projected) ** 2 for value, projected in zip(centered_output, target)
    )
    if residual <= 0.0:
        return None, "perfect_reconstruction"
    return 10.0 * math.log10(target_energy / residual), None


def si_sdr_improvement(
    reference: Sequence[float], estimate: Sequence[float], raw: Sequence[float]
) -> Tuple[Optional[float], Optional[str]]:
    """Paired SI-SDR(output) minus SI-SDR(noisy input), or an explicit reason."""
    output, out_reason = si_sdr(reference, estimate)
    baseline, base_reason = si_sdr(reference, raw)
    if out_reason or base_reason:
        return None, out_reason or base_reason
    assert output is not None and baseline is not None
    return output - baseline, None


def _fft_inplace(real: List[float], imag: List[float], inverse: bool = False) -> None:
    """In-place radix-2 Cooley-Tukey transform; length must be a power of two."""
    size = len(real)
    if size == 0 or size & (size - 1) or len(imag) != size:
        raise ValueError("invalid_fft_size")
    index = 0
    for position in range(1, size):
        bit = size >> 1
        while index & bit:
            index ^= bit
            bit >>= 1
        index |= bit
        if position < index:
            real[position], real[index] = real[index], real[position]
            imag[position], imag[index] = imag[index], imag[position]
    step = 2
    while step <= size:
        angle = (-2.0 if inverse else 2.0) * math.pi / step
        step_real, step_imag = math.cos(angle), math.sin(angle)
        for start in range(0, size, step):
            root_real, root_imag = 1.0, 0.0
            for offset in range(step // 2):
                left, right = start + offset, start + offset + step // 2
                prod_real = real[right] * root_real - imag[right] * root_imag
                prod_imag = real[right] * root_imag + imag[right] * root_real
                real[right] = real[left] - prod_real
                imag[right] = imag[left] - prod_imag
                real[left] += prod_real
                imag[left] += prod_imag
                root_real, root_imag = (
                    root_real * step_real - root_imag * step_imag,
                    root_real * step_imag + root_imag * step_real,
                )
        step <<= 1
    if inverse:
        for position in range(size):
            real[position] /= size
            imag[position] /= size


def _band_edges() -> List[float]:
    ratio = _BAND_HIGH_HZ / _BAND_LOW_HZ
    return [_BAND_LOW_HZ * ratio ** (index / _BAND_COUNT) for index in range(_BAND_COUNT + 1)]


_EDGES = _band_edges()


def _envelopes(values: Sequence[float]) -> List[List[float]]:
    """Per-band temporal envelopes from 32 ms / 16 ms frames."""
    count = max(0, (len(values) - _FFT_SIZE) // _HOP_SIZE + 1)
    envelopes: List[List[float]] = [[] for _ in range(_BAND_COUNT)]
    if count == 0:
        return envelopes
    window = [0.5 - 0.5 * math.cos(2.0 * math.pi * (index + 0.5) / _FFT_SIZE)
              for index in range(_FFT_SIZE)]
    bin_hz = _SAMPLE_RATE_HZ / _FFT_SIZE
    bands: List[List[int]] = []
    for low, high in zip(_EDGES, _EDGES[1:]):
        indices = [bin_index for bin_index in range(1, _FFT_SIZE // 2 + 1)
                   if low <= bin_index * bin_hz < high]
        bands.append(indices or [max(1, int(round(low / bin_hz)))])
    for frame_index in range(count):
        start = frame_index * _HOP_SIZE
        real = [values[start + offset] * window[offset] for offset in range(_FFT_SIZE)]
        imag = [0.0] * _FFT_SIZE
        _fft_inplace(real, imag)
        power = [real[bin_index] ** 2 + imag[bin_index] ** 2 for bin_index in range(_FFT_SIZE // 2 + 1)]
        for band_index, indices in enumerate(bands):
            envelopes[band_index].append(math.fsum(power[bin_index] for bin_index in indices))
    return envelopes


def _clipped_envelope(envelope: Sequence[float]) -> List[float]:
    peak = max(envelope) if envelope else 0.0
    floor = peak * 10.0 ** (-_DYNAMIC_RANGE_DB / 20.0)
    return [max(value, floor) for value in envelope]


def _correlation(left: Sequence[float], right: Sequence[float]) -> Optional[float]:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = math.fsum(left) / len(left)
    right_mean = math.fsum(right) / len(right)
    centered_left = [value - left_mean for value in left]
    centered_right = [value - right_mean for value in right]
    left_energy = math.fsum(value * value for value in centered_left)
    right_energy = math.fsum(value * value for value in centered_right)
    if left_energy <= _EPS or right_energy <= _EPS:
        return None
    cross = math.fsum(a * b for a, b in zip(centered_left, centered_right))
    return max(-1.0, min(1.0, cross / math.sqrt(left_energy * right_energy)))


def stoi_style(reference: Sequence[float], estimate: Sequence[float]) -> Tuple[Optional[float], Optional[str]]:
    """Deterministic STOI-style proxy in [0, 1]; identity returns exactly 1.0."""
    pair = _pair(reference, estimate)
    if pair is None:
        return None, "invalid_input"
    clean, output = pair
    if math.fsum(value * value for value in clean) <= _EPS:
        return None, "zero_reference_energy"
    if len(clean) < _FFT_SIZE:
        return None, "too_short"
    if clean == output:
        return 1.0, None
    clean_env = _envelopes(clean)
    output_env = _envelopes(output)
    if not clean_env or not any(clean_env):
        return None, "no_analysis_frames"
    correlations: List[float] = []
    for clean_band, output_band in zip(clean_env, output_env):
        peak = max(clean_band) if clean_band else 0.0
        active = [index for index, value in enumerate(clean_band) if value > peak * 1e-3]
        if len(active) < 2:
            continue
        clean_clipped = _clipped_envelope([clean_band[index] for index in active])
        output_clipped = _clipped_envelope([output_band[index] for index in active])
        coefficient = _correlation(clean_clipped, output_clipped)
        if coefficient is not None:
            correlations.append(max(0.0, coefficient))
    if not correlations:
        return None, "no_scorable_bands"
    return max(0.0, min(1.0, math.fsum(correlations) / len(correlations))), None
