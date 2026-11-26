# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free deterministic metrics for the task-local rate evidence.

Every function is pure, single-threaded and standard-library only. Values are
synthetic waveform proxies: no listening score, device measurement, perceptual
pitch judgment or release result is produced here.
"""

from __future__ import annotations

import hashlib
import math
import struct
from typing import Any, Dict, Iterable, List, Sequence, Tuple

MAX_ABS_INPUT = 4.0


class ScorerError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def r6(value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ScorerError("non-numeric value")
    if not math.isfinite(float(value)):
        raise ScorerError("non-finite value")
    return float(f"{float(value):.6f}")


def r9(value: float) -> float:
    if not math.isfinite(float(value)):
        raise ScorerError("non-finite value")
    return float(f"{float(value):.9f}")


def tensor_digest(values: Iterable[float]) -> str:
    parts: List[bytes] = []
    for value in values:
        number = float(value)
        if not math.isfinite(number):
            raise ScorerError("non-finite sample in digest")
        parts.append(struct.pack("<d", number))
    return sha256_bytes(b"".join(parts))


def validate_vector(values: Any, name: str = "samples") -> Tuple[float, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ScorerError(name + " must be a numeric sequence")
    output: List[float] = []
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ScorerError(name + " has a non-numeric value at " + str(index))
        number = float(value)
        if not math.isfinite(number):
            raise ScorerError(name + " has a non-finite value at " + str(index))
        if abs(number) > MAX_ABS_INPUT:
            raise ScorerError(name + " exceeds the synthetic safety ceiling at " + str(index))
        output.append(number)
    if not output:
        raise ScorerError(name + " is empty")
    return tuple(output)


def nonfinite_count(values: Iterable[float]) -> int:
    return sum(0 if math.isfinite(float(value)) else 1 for value in values)


def finite_count(values: Iterable[float]) -> int:
    return sum(1 if math.isfinite(float(value)) else 0 for value in values)


def peak_abs(values: Sequence[float]) -> float:
    return max((abs(float(value)) for value in values), default=0.0)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(math.fsum(float(value) * float(value) for value in values) / len(values))


def goertzel_amplitude(values: Sequence[float], hz: float, sample_rate_hz: float) -> float:
    """Normalized single-bin amplitude (a full-scale sine reads 1.0)."""
    count = len(values)
    if count == 0 or sample_rate_hz <= 0.0 or hz < 0.0:
        raise ScorerError("invalid Goertzel window")
    if hz >= sample_rate_hz / 2.0:
        raise ScorerError("Goertzel bin at or above Nyquist")
    omega = 2.0 * math.pi * hz / sample_rate_hz
    coefficient = 2.0 * math.cos(omega)
    first = 0.0
    second = 0.0
    for value in values:
        current = float(value) + coefficient * first - second
        second = first
        first = current
    power = first * first + second * second - coefficient * first * second
    return 2.0 * math.sqrt(max(power, 0.0)) / count


def _band_peak(values: Sequence[float], sample_rate_hz: float,
               low_hz: float, high_hz: float, step_hz: float) -> Dict[str, float]:
    nyquist = sample_rate_hz / 2.0
    low = max(1.0, low_hz)
    high = min(high_hz, nyquist * 0.999)
    if high <= low:
        raise ScorerError("empty frequency band")
    best_hz = low
    best_amplitude = -1.0
    frequency = low
    while frequency <= high:
        amplitude = goertzel_amplitude(values, frequency, sample_rate_hz)
        if amplitude > best_amplitude:
            best_amplitude = amplitude
            best_hz = frequency
        frequency += step_hz
    coarse = best_hz
    fine_low = max(low, coarse - step_hz)
    fine_high = min(high, coarse + step_hz)
    frequency = fine_low
    fine_step = step_hz / 20.0
    while frequency <= fine_high:
        amplitude = goertzel_amplitude(values, frequency, sample_rate_hz)
        if amplitude > best_amplitude:
            best_amplitude = amplitude
            best_hz = frequency
        frequency += fine_step
    return {"dominant_hz": r6(best_hz), "amplitude": r6(best_amplitude),
            "coarse_step_hz": step_hz}


def dominant_hz(values: Sequence[float], sample_rate_hz: float,
                low_hz: float = 40.0, high_hz: float = 2000.0,
                step_hz: float = 2.5) -> Dict[str, float]:
    return _band_peak(values, sample_rate_hz, low_hz, high_hz, step_hz)


def duration_metrics(source_samples: int, output_samples: int, ratio: float) -> Dict[str, Any]:
    numerator, denominator = ratio.as_integer_ratio()
    expected = (2 * source_samples * numerator + denominator) // (2 * denominator)
    delta = output_samples - expected
    return {
        "expected_output_samples": expected,
        "observed_output_samples": output_samples,
        "delta_samples": delta,
        "exact": delta == 0,
        "rounding_limit_samples": 0.5,
        "ratio": r9(ratio),
        "method": "round_half_up(source_samples * output_rate / input_rate)",
    }


def transient_proxy(source_peak: float, output: Sequence[float],
                    output_positions: Sequence[int],
                    radius: int = 48) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []
    for expected in output_positions:
        low = max(0, expected - radius)
        high = min(len(output), expected + radius + 1)
        if low >= high:
            events.append({"expected_output_sample": expected, "observed_output_sample": None,
                           "timing_error_samples": None, "peak_ratio": None})
            continue
        observed = max(range(low, high), key=lambda index: abs(output[index]))
        peak = abs(output[observed])
        events.append({
            "expected_output_sample": expected,
            "observed_output_sample": observed,
            "timing_error_samples": observed - expected,
            "peak_ratio": r6(peak / source_peak) if source_peak else None,
        })
    return {"proxy": "local_peak_and_timing_not_listening", "events": events}


def envelope_proxy(source: Sequence[float], output: Sequence[float],
                   mapping: Sequence[int], spans: Sequence[Tuple[int, int]]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for start, end in spans:
        source_slice = source[start:end]
        selected = [output[index] for index, source_index in enumerate(mapping)
                    if start <= source_index < end]
        if not source_slice or not selected:
            rows.append({"source_start": start, "source_end": end,
                         "source_rms": None, "output_rms": None, "ratio": None})
            continue
        source_level = rms(source_slice)
        output_level = rms(selected)
        rows.append({
            "source_start": start,
            "source_end": end,
            "source_rms": r6(source_level),
            "output_rms": r6(output_level),
            "ratio": r6(output_level / source_level) if source_level else None,
            "output_samples": len(selected),
        })
    return {"proxy": "source_anchored_rms_span_ratio_not_speech_score", "spans": rows}


def fifo_occupancy(produced: Sequence[int], consumed: Sequence[int],
                   prefill: int, capacity: int) -> Dict[str, Any]:
    if prefill < 0 or capacity <= 0 or prefill > capacity:
        raise ScorerError("invalid FIFO geometry")
    queued = prefill
    occupancy: List[int] = []
    underruns = 0
    overflows = 0
    ticks: List[Dict[str, Any]] = []
    for index, (incoming, outgoing) in enumerate(zip(produced, consumed)):
        if incoming < 0 or outgoing < 0:
            raise ScorerError("negative FIFO traffic")
        event = "normal"
        if queued + incoming > capacity:
            overflows += 1
            incoming = max(0, capacity - queued)
            event = "overflow_clipped"
        queued += incoming
        if queued < outgoing:
            underruns += 1
            outgoing = queued
            event = "underrun" if event == "normal" else event
        queued -= outgoing
        occupancy.append(queued)
        ticks.append({"tick": index, "produced": incoming, "consumed": outgoing,
                      "queued": queued, "event": event})
    return {
        "proxy": "synthetic_sample_counts_not_device_playout",
        "prefill_samples": prefill,
        "capacity_samples": capacity,
        "ticks": ticks,
        "occupancy_samples": occupancy,
        "min_occupancy": min(occupancy) if occupancy else prefill,
        "max_occupancy": max(occupancy) if occupancy else prefill,
        "underrun_ticks": underruns,
        "overflow_ticks": overflows,
    }


def rebuffer_trace(produced: Sequence[int], consumed: Sequence[int],
                   prefill: int, capacity: int) -> Dict[str, Any]:
    trace = fifo_occupancy(produced, consumed, prefill, capacity)
    events = {tick["event"] for tick in trace["ticks"]}
    trace["stall"] = "underrun" in events
    trace["refill_observed"] = any(
        left["queued"] == 0 and right["produced"] > 0
        for left, right in zip(trace["ticks"], trace["ticks"][1:]))
    trace["resume_observed"] = trace["stall"] and any(
        tick["consumed"] > 0 and tick["event"] == "normal"
        for tick in trace["ticks"][-4:])
    trace["stall_refill_resume_observed"] = bool(
        trace["stall"] and trace["refill_observed"] and trace["resume_observed"])
    return trace


def attenuation_db(reference: float, measured: float) -> float:
    if measured <= 0.0:
        return -240.0
    if reference <= 0.0:
        raise ScorerError("non-positive attenuation reference")
    return r6(20.0 * math.log10(measured / reference))


def band_energy_ratio(values: Sequence[float], sample_rate_hz: float,
                      low_hz: float, high_hz: float, step_hz: float = 5.0) -> float:
    peak = _band_peak(values, sample_rate_hz, low_hz, high_hz, step_hz)
    return peak["amplitude"]


def adjacent_delta(values: Sequence[float]) -> Tuple[float, ...]:
    return tuple(values[index + 1] - values[index] for index in range(len(values) - 1))
