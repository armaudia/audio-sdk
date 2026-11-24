# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free paired scores for the synthetic enhancement fixture.

The SI-SDR implementation is the standard scale-invariant projection score
with an explicit finite cap for exact reconstruction.  The STOI-style value is
a *non-standard, non-authoritative* short-time band cosine surrogate defined
entirely here; it is not STOI, not an intelligibility measurement and not a
human listening result.  No corpus, model, native library or FFmpeg tool is
used by this module.
"""

from __future__ import annotations

from functools import lru_cache
import math
from typing import Any, Sequence

SISDR_CAP_DB = 120.0
ENERGY_EPS = 1e-12
BAND_EDGE_BINS: tuple[int, ...] = (1, 3, 6, 12, 24, 40, 65)
FRAME_SAMPLES = 256
HOP_SAMPLES = 160
WINDOW_SAMPLES = 256
ACTIVE_BAND_ENERGY = 1e-10


def _validate(reference: Sequence[float], estimate: Sequence[float]) -> None:
    if len(reference) != len(estimate):
        raise ValueError("length_mismatch")
    if not reference:
        raise ValueError("empty_signal")
    for value in reference:
        if not math.isfinite(value):
            raise ValueError("nonfinite_reference")
    for value in estimate:
        if not math.isfinite(value):
            raise ValueError("nonfinite_estimate")


def sisdr_db(reference: Sequence[float], estimate: Sequence[float]) -> float:
    """Scale-invariant signal-to-distortion ratio in dB, capped at 120 dB."""
    _validate(reference, estimate)
    reference_energy = sum(value * value for value in reference)
    if reference_energy <= ENERGY_EPS:
        raise ValueError("zero_reference_energy")
    dot = sum(a * b for a, b in zip(reference, estimate))
    alpha = dot / reference_energy
    residual = sum((value - alpha * target) ** 2
                   for value, target in zip(estimate, reference))
    if residual <= ENERGY_EPS:
        return SISDR_CAP_DB
    projected = alpha * alpha * reference_energy
    if projected <= ENERGY_EPS:
        return -SISDR_CAP_DB
    return max(-SISDR_CAP_DB, min(SISDR_CAP_DB, 10.0 * math.log10(projected / residual)))


def peak(signal: Sequence[float]) -> float:
    if not signal:
        raise ValueError("empty_signal")
    return max(abs(float(value)) for value in signal)


def all_finite(signal: Sequence[float]) -> bool:
    return bool(signal) and all(math.isfinite(float(value)) for value in signal)


@lru_cache(maxsize=1)
def _tables() -> tuple[tuple[float, ...], tuple[tuple[float, ...], ...],
                       tuple[tuple[float, ...], ...]]:
    window = tuple(0.5 - 0.5 * math.cos(2.0 * math.pi * k / WINDOW_SAMPLES)
                   for k in range(WINDOW_SAMPLES))
    cosines = tuple(
        tuple(math.cos(2.0 * math.pi * bin_index * k / WINDOW_SAMPLES)
              for k in range(WINDOW_SAMPLES))
        for bin_index in range(BAND_EDGE_BINS[-1])
    )
    sines = tuple(
        tuple(math.sin(2.0 * math.pi * bin_index * k / WINDOW_SAMPLES)
              for k in range(WINDOW_SAMPLES))
        for bin_index in range(BAND_EDGE_BINS[-1])
    )
    return window, cosines, sines


@lru_cache(maxsize=32)
def _band_energies(signal: tuple[float, ...]) -> tuple[tuple[float, ...], ...]:
    window, cosines, sines = _tables()
    frames: list[list[float]] = []
    total = len(signal)
    start = 0
    while start + WINDOW_SAMPLES <= total:
        weighted = [signal[start + k] * window[k] for k in range(WINDOW_SAMPLES)]
        band_powers: list[float] = []
        for low, high in zip(BAND_EDGE_BINS, BAND_EDGE_BINS[1:]):
            power = 0.0
            for bin_index in range(low, high):
                real = sum(value * cosines[bin_index][k]
                           for k, value in enumerate(weighted))
                imag = -sum(value * sines[bin_index][k]
                            for k, value in enumerate(weighted))
                power += real * real + imag * imag
            band_powers.append(math.sqrt(power))
        frames.append(tuple(band_powers))
        start += HOP_SAMPLES
    if not frames:
        raise ValueError("too_few_frames_for_stoi_style")
    return tuple(frames)


def stoi_style(reference: Sequence[float], estimate: Sequence[float]) -> dict[str, Any]:
    """Return a non-standard short-time band-similarity surrogate in [0, 1]."""
    _validate(reference, estimate)
    ref_frames = _band_energies(tuple(reference))
    est_frames = _band_energies(tuple(estimate))
    if len(ref_frames) != len(est_frames):
        raise ValueError("stoi_frame_count_mismatch")
    ref_max = [max(frame[index] for frame in ref_frames)
               for index in range(len(BAND_EDGE_BINS) - 1)]
    scores: list[float] = []
    for ref_frame, est_frame in zip(ref_frames, est_frames):
        if max(ref_frame) <= ACTIVE_BAND_ENERGY:
            continue
        ref_vector = [min(1.0, value / max(norm, ACTIVE_BAND_ENERGY))
                      for value, norm in zip(ref_frame, ref_max)]
        est_vector = [min(1.0, value / max(norm, ACTIVE_BAND_ENERGY))
                      for value, norm in zip(est_frame, ref_max)]
        ref_norm = math.sqrt(sum(value * value for value in ref_vector))
        est_norm = math.sqrt(sum(value * value for value in est_vector))
        if ref_norm <= ACTIVE_BAND_ENERGY or est_norm <= ACTIVE_BAND_ENERGY:
            continue
        cosine = sum(a * b for a, b in zip(ref_vector, est_vector)) / (ref_norm * est_norm)
        scores.append(max(0.0, min(1.0, cosine)))
    if not scores:
        raise ValueError("no_active_speech_frames")
    return {
        "score": round(sum(scores) / len(scores), 12),
        "frames_scored": len(scores),
        "frames_total": len(ref_frames),
        "bands": len(BAND_EDGE_BINS) - 1,
        "method": "nonstandard_band_cosine_surrogate_not_stoi",
    }


def paired_scores(reference: Sequence[float], estimate: Sequence[float]) -> dict[str, Any]:
    """Score one paired synthetic item against its frozen clean reference."""
    _validate(reference, estimate)
    style = stoi_style(reference, estimate)
    return {
        "sisdr_db": round(sisdr_db(reference, estimate), 12),
        "stoi_style": style,
        "peak": round(peak(estimate), 12),
        "samples": len(estimate),
        "all_finite": all_finite(estimate),
        "valid": all_finite(estimate) and peak(estimate) <= 1.0,
    }


def invalid_output(reference: Sequence[float], estimate: Sequence[float]) -> dict[str, Any]:
    """Explicit invalid-output control; nonfinite samples are rejected, not scored."""
    rejected: list[str] = []
    if len(reference) != len(estimate):
        rejected.append("length_mismatch")
    for index, value in enumerate(estimate):
        if not math.isfinite(float(value)):
            rejected.append("nonfinite_at_" + str(index))
            break
    if not rejected and peak(estimate) > 1.0:
        rejected.append("peak_above_one")
    return {
        "accepted": not rejected,
        "reasons": rejected,
        "missing_result_promoted": False,
    }
