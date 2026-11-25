# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free scoring helpers for the synthetic Sonic rate evidence.

All functions here operate on caller-owned Python sequences. They compute
explicit source/output mapping, duration, pitch proxies, transient proxies,
speech-envelope preservation proxies and playback-buffer accounting. Nothing in
this module listens to audio, downloads an asset, measures a device or turns a
synthetic proxy into a perceptual or release claim.
"""

from __future__ import annotations

from bisect import bisect_left
import hashlib
import math
import struct
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class ScorerError(ValueError):
    """Raised for malformed synthetic inputs or impossible score requests."""


MAX_ABS_INPUT = 4.0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tensor_digest(values: Iterable[float]) -> str:
    """Digest of little-endian float32 bytes, one deterministic tensor digest."""
    digest = hashlib.sha256()
    for value in values:
        number = float(value)
        if not math.isfinite(number):
            raise ScorerError("nonfinite_tensor_value")
        digest.update(struct.pack("<f", number))
    return digest.hexdigest()


def r6(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ScorerError("nonfinite_score")
    result = round(number, 6)
    return 0.0 if result == 0.0 else result


def validate_vector(values: Iterable[float], name: str = "samples") -> Tuple[float, ...]:
    result = []
    for value in values:
        if type(value) not in (int, float):
            raise ScorerError("invalid_" + name + "_type")
        if isinstance(value, float) and not math.isfinite(value):
            raise ScorerError("nonfinite_" + name)
        if abs(value) > MAX_ABS_INPUT:
            raise ScorerError("out_of_range_" + name)
        result.append(float(value))
    return tuple(result)


def finite_count(values: Iterable[float]) -> int:
    return sum(1 for value in values if math.isfinite(float(value)))


def nonfinite_count(values: Iterable[float]) -> int:
    return sum(1 for value in values if not math.isfinite(float(value)))


def peak_abs(values: Iterable[float]) -> float:
    values = tuple(values)
    return max((abs(float(value)) for value in values), default=0.0)


def rms(values: Iterable[float]) -> float:
    values = tuple(values)
    if not values:
        return 0.0
    return math.sqrt(sum(float(value) ** 2 for value in values) / len(values))


def hann(length: int) -> Tuple[float, ...]:
    if length < 1:
        raise ScorerError("bad_window_length")
    if length == 1:
        return (1.0,)
    return tuple(0.5 - 0.5 * math.cos(2.0 * math.pi * index / (length - 1))
                 for index in range(length))


def ola_render(grains: Sequence[Mapping[str, int]], source: Sequence[float],
               target_len: int) -> Dict[str, Any]:
    """Independent OLA renderer used only by the crosscheck path.

    ``reference.stretch`` uses its own incremental accumulation loop. This
    renderer takes the same frozen grain table and sums by output index, so an
    exact digest match checks the renderer without reusing its control flow.
    """
    if target_len < 0:
        raise ScorerError("negative_target_length")
    accumulator = [0.0] * target_len
    weight = [0.0] * target_len
    mapping = [-1] * target_len
    source = tuple(float(value) for value in source)
    for grain in grains:
        start = int(grain["source_start"])
        place = int(grain["output_start"])
        period = int(grain["period"])
        available = int(grain["available"])
        if period < 1 or available < 0 or available > 2 * period:
            raise ScorerError("bad_grain")
        window = hann(2 * period)
        for offset in range(2 * period):
            index = place + offset
            if index < 0 or index >= target_len:
                continue
            sample = source[start + offset] if offset < available else 0.0
            accumulator[index] += sample * window[offset]
            weight[index] += window[offset]
            if offset < available:
                mapping[index] = max(mapping[index], start + offset)
    output: List[float] = []
    holes = 0
    monotone_map: List[int] = []
    previous = 0
    for index in range(target_len):
        if weight[index] <= 1e-12:
            output.append(0.0)
            holes += 1
        else:
            output.append(accumulator[index] / weight[index])
        source_index = mapping[index] if mapping[index] >= 0 else previous
        previous = max(previous, source_index)
        monotone_map.append(previous)
    return {
        "samples": tuple(output),
        "mapping": tuple(monotone_map),
        "holes": holes,
    }


def duration_metrics(source_samples: int, output_samples: int, rate: float) -> Dict[str, Any]:
    expected = int(round(source_samples / rate))
    return {
        "source_samples": int(source_samples),
        "output_samples": int(output_samples),
        "expected_samples": expected,
        "error_samples": int(output_samples - expected),
        "exact": output_samples == expected,
        "output_per_source": r6(output_samples / source_samples) if source_samples else 0.0,
        "inverse_rate": r6(1.0 / rate),
        "caller_clock": "fractional target clock rounds cumulative source/rate",
    }


def dominant_hz(values: Sequence[float], sample_rate_hz: int,
                low_hz: float = 90.0, high_hz: float = 420.0) -> Dict[str, Any]:
    """Grid Goertzel pitch proxy on a deterministic centred analysis window."""
    samples = tuple(float(value) for value in values)
    if not samples:
        return {"dominant_hz": 0.0, "magnitude": 0.0, "proxy": "empty"}
    start = max(0, (len(samples) - 4096) // 2)
    window = samples[start:start + 4096]
    window = tuple(value * (0.5 - 0.5 * math.cos(2.0 * math.pi * index
                                                 / (len(window) - 1)))
                   for index, value in enumerate(window))
    best_hz = 0.0
    best_magnitude = -1.0
    candidate = int(math.ceil(low_hz))
    while candidate <= high_hz:
        omega = 2.0 * math.pi * candidate / sample_rate_hz
        real = 0.0
        imaginary = 0.0
        cosine = math.cos(omega)
        sine = math.sin(omega)
        rotation_cosine = cosine
        rotation_sine = sine
        for value in window:
            real += value * cosine
            imaginary += value * sine
            cosine, sine = (cosine * rotation_cosine - sine * rotation_sine,
                            cosine * rotation_sine + sine * rotation_cosine)
        magnitude = math.hypot(real, imaginary)
        if magnitude > best_magnitude:
            best_magnitude = magnitude
            best_hz = float(candidate)
        candidate += 1
    return {
        "dominant_hz": r6(best_hz),
        "magnitude": r6(best_magnitude / len(window)),
        "proxy": "grid_goertzel_hann_not_listening",
    }


def adjacent_delta(values: Sequence[float]) -> Tuple[float, ...]:
    sequence = tuple(float(value) for value in values)
    return tuple(abs(sequence[index] - sequence[index - 1])
                 for index in range(1, len(sequence)))


def transient_proxy(source: Sequence[float], output: Sequence[float], rate: float,
                    positions: Sequence[int], mapping: Sequence[int],
                    source_radius: int = 24,
                    output_radius: int = 48) -> Dict[str, Any]:
    """Score peaks at the renderer's mapped output position for each transient.

    ``position / rate`` is only a caller-clock estimate. The renderer's
    output-to-source map is the authoritative source-to-output index mapping;
    using the estimate here silently scores the wrong output region after
    pitch-synchronous grain repetition or dropping.
    """
    mapping = tuple(int(value) for value in mapping)
    if any(left > right for left, right in zip(mapping, mapping[1:])):
        raise ScorerError("nonmonotonic_mapping")
    source_delta = adjacent_delta(source)
    output_delta = adjacent_delta(output)
    events: List[Dict[str, Any]] = []
    for position in positions:
        source_left = max(0, position - source_radius)
        source_right = min(len(source_delta), position + source_radius + 1)
        source_slice = source_delta[source_left:source_right]
        source_peak = max(source_slice, default=0.0)
        source_at = source_left + source_slice.index(source_peak) + 1 if source_slice else position
        # First output sample whose recorded source index reaches the transient.
        expected = min(bisect_left(mapping, position), max(len(output_delta) - 1, 0))
        mapped_source = mapping[expected] if mapping else None
        output_left = max(0, expected - output_radius)
        output_right = min(len(output_delta), expected + output_radius + 1)
        output_slice = output_delta[output_left:output_right]
        output_peak = max(output_slice, default=0.0)
        output_at = output_left + output_slice.index(output_peak) + 1 if output_slice else expected
        events.append({
            "source_sample": int(position),
            "source_peak_sample": int(source_at),
            "expected_output_sample": int(expected),
            "mapped_source_sample": mapped_source,
            "caller_clock_estimate": int(round(position / rate)),
            "observed_output_sample": int(output_at),
            "timing_error_samples": int(output_at - expected),
            "peak_retention": r6(output_peak / source_peak) if source_peak > 0.0 else None,
        })
    retentions = [event["peak_retention"] for event in events
                  if event["peak_retention"] is not None]
    retentions.sort()
    median = retentions[len(retentions) // 2] if retentions else None
    return {
        "events": events,
        "median_peak_retention": median,
        "max_abs_timing_error_samples": max(
            (abs(int(event["timing_error_samples"])) for event in events), default=0),
        "proxy": "adjacent_delta_peak_at_mapped_output_not_audibility",
    }


def envelope_proxy(source: Sequence[float], output: Sequence[float],
                   mapping: Sequence[int], spans: Sequence[Tuple[int, int]],
                   frame_samples: int = 160) -> Dict[str, Any]:
    """Compare RMS in source-anchored spans using the recorded output map."""
    output = tuple(float(value) for value in output)
    mapping = tuple(int(value) for value in mapping)
    rows: List[Dict[str, Any]] = []
    for start, end in spans:
        source_rms = rms(source[start:end])
        indices = [index for index, source_index in enumerate(mapping)
                   if start <= source_index < end]
        output_rms = rms(output[index] for index in indices)
        ratio = output_rms / source_rms if source_rms > 1e-12 else None
        rows.append({
            "source_start": int(start),
            "source_end": int(end),
            "mapped_output_samples": len(indices),
            "source_rms": r6(source_rms),
            "output_rms": r6(output_rms),
            "rms_ratio": r6(ratio) if ratio is not None else None,
        })
    ratios = [row["rms_ratio"] for row in rows if row["rms_ratio"] is not None]
    return {
        "spans": rows,
        "min_rms_ratio": r6(min(ratios)) if ratios else None,
        "max_rms_ratio": r6(max(ratios)) if ratios else None,
        "proxy": "source_anchored_rms_not_wer_or_listening",
    }


def buffer_occupancy(consumed: Sequence[int], produced: Sequence[int],
                     frame_samples: int = 160,
                     prefill_samples: int = 0) -> Dict[str, Any]:
    """Caller-clock FIFO accounting; no device pacing or deadline claim."""
    if len(consumed) != len(produced):
        raise ScorerError("buffer_clock_length_mismatch")
    occupancy: List[int] = []
    running = int(prefill_samples)
    underruns = 0
    for input_samples, output_samples in zip(consumed, produced):
        running += int(input_samples) - int(output_samples)
        occupancy.append(running)
        if running < -frame_samples:
            underruns += 1
    return {
        "prefill_samples": int(prefill_samples),
        "occupancy_samples": occupancy,
        "min_occupancy_samples": min(occupancy) if occupancy else running,
        "final_occupancy_samples": occupancy[-1] if occupancy else running,
        "underrun_blocks": underruns,
        "proxy": "caller_owned_fifo_accounting_not_device_fill_or_flush",
    }


def boundary_jump_ratio(output: Sequence[float], boundaries: Sequence[int]) -> Dict[str, Any]:
    delta = adjacent_delta(output)
    overall = sorted(delta)
    p99 = overall[int(0.99 * (len(overall) - 1))] if overall else 0.0
    rows: List[Dict[str, Any]] = []
    for boundary in boundaries:
        centre = min(max(boundary - 1, 0), max(len(delta) - 1, 0))
        local = delta[max(0, centre - 8):centre + 9]
        peak = max(local, default=0.0)
        rows.append({
            "output_boundary_sample": int(boundary),
            "local_adjacent_delta_peak": r6(peak),
            "ratio_to_clip_p99": r6(peak / p99) if p99 > 0.0 else None,
        })
    return {
        "boundaries": rows,
        "clip_p99_adjacent_delta": r6(p99),
        "proxy": "waveform_discontinuity_not_audible_click_score",
    }
