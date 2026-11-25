# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free deterministic metrics for the synthetic offline TSM evidence.

All perceptual-named fields are numeric proxies on synthetic signals. They are
not listening scores, not intelligibility scores and not release thresholds.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

SCORER_ID = "rubber-band-r3-offline-tSM-proxy/0.1"
MIN_RATE = 0.8
MAX_RATE = 1.5


def is_finite(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def finite_count(values: Sequence[float]) -> int:
    return sum(1 for value in values if is_finite(value))


def nonfinite_count(values: Sequence[float]) -> int:
    return len(values) - finite_count(values)


def peak(values: Sequence[float]) -> float:
    return max((abs(float(v)) for v in values if is_finite(v)), default=0.0)


def clip_count(values: Sequence[float], ceiling: float = 1.0) -> int:
    return sum(1 for value in values if is_finite(value) and abs(float(value)) > ceiling)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(float(v) * float(v) for v in values) / len(values))


def db_ratio(numerator: float, denominator: float) -> float | None:
    if not (is_finite(numerator) and is_finite(denominator)):
        return None
    if numerator <= 0.0 or denominator <= 0.0:
        return None
    return 20.0 * math.log10(numerator / denominator)


def dominant_frequency(values: Sequence[float], sample_rate: int,
                       low_hz: int = 120, high_hz: int = 400) -> float | None:
    """Autocorrelation pitch proxy on a stationary synthetic segment."""
    if len(values) < 4 * sample_rate // high_hz:
        return None
    segment = [float(v) for v in values if is_finite(v)]
    if len(segment) != len(values) or rms(segment) < 1e-6:
        return None
    mean = sum(segment) / len(segment)
    centered = [value - mean for value in segment]
    energy = sum(value * value for value in centered)
    if energy <= 0.0:
        return None
    best_lag = 0
    best_score = -2.0
    for lag in range(max(2, sample_rate // high_hz), min(len(centered) - 2, sample_rate // low_hz) + 1):
        score = sum(centered[i] * centered[i + lag] for i in range(len(centered) - lag)) / (energy - 0.0)
        if score > best_score:
            best_score = score
            best_lag = lag
    if best_lag <= 0 or best_score < 0.25:
        return None
    return float(sample_rate) / best_lag


def transient_proxy(values: Sequence[float], mapped_clicks: Sequence[int],
                    radius: int = 70, search_radius: int = 180) -> Dict[str, Any]:
    """Local peak/onset-width proxy for synthetic clicks; never an audibility claim."""
    results: List[Dict[str, Any]] = []
    for expected in mapped_clicks:
        expected_index = int(round(expected))
        search_center = max(search_radius, min(len(values) - search_radius - 1, expected_index))
        coarse = [abs(float(values[i]))
                  for i in range(search_center - search_radius, search_center + search_radius + 1)]
        coarse_peak = max(coarse, default=0.0)
        coarse_index = max(range(len(coarse)), key=lambda i: coarse[i])
        center = search_center - search_radius + coarse_index
        low_bound = max(0, center - radius)
        high_bound = min(len(values) - 1, center + radius)
        window = [float(values[i]) for i in range(low_bound, high_bound + 1)]
        local_peak = max((abs(v) for v in window), default=0.0)
        peak_index = max(range(len(window)), key=lambda i: abs(window[i]))
        threshold = 0.25 * local_peak
        width = sum(1 for v in window if abs(v) >= threshold)
        low = 0.0 if peak_index < 20 else rms(window[max(0, peak_index - 25):peak_index - 5])
        high = 0.0 if peak_index > len(window) - 21 else rms(window[peak_index + 6:peak_index + 26])
        baseline = max(low, high, 1e-9)
        results.append({
            "expected_output_sample": expected_index,
            "observed_peak_output_sample": center,
            "peak_offset_samples": center - expected_index,
            "coarse_search_radius": search_radius,
            "local_peak": local_peak,
            "coarse_peak": coarse_peak,
            "peak_to_local_rms": local_peak / baseline,
            "threshold_crossing_width": width,
            "radius": radius,
        })
    return {
        "metric": "synthetic_click_local_peak_and_width",
        "qualifies_listening": False,
        "clicks": results,
        "mean_peak_to_local_rms": sum(r["peak_to_local_rms"] for r in results) / len(results) if results else None,
        "max_threshold_crossing_width": max((r["threshold_crossing_width"] for r in results), default=None),
    }


def speech_preservation(source: Sequence[float], output: Sequence[float],
                        prefix: Sequence[float], labels: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Energy preservation on frozen source-timestamped synthetic labels."""
    entries: List[Dict[str, Any]] = []
    for label in labels:
        start = int(label["source_start"])
        end = int(label["source_end"])
        out_start = int(round(prefix[start]))
        out_end = int(round(prefix[end]))
        src_rms = rms(source[start:end])
        out_rms = rms(output[out_start:out_end])
        entries.append({
            "source_start": start,
            "source_end": end,
            "source_start_ns": start * 62500,
            "label": label["label"],
            "decision": label["decision"],
            "mapped_output_start": out_start,
            "mapped_output_end": out_end,
            "source_rms": src_rms,
            "output_rms": out_rms,
            "rms_ratio_db": db_ratio(out_rms, src_rms),
            "source_timestamped": True,
        })
    speech = [item for item in entries if item["decision"] == "protect"]
    flex = [item for item in entries if item["decision"] == "flex"]
    return {
        "metric": "synthetic_labelled_energy_preservation",
        "qualifies_intelligibility": False,
        "entries": entries,
        "speech_intervals": len(speech),
        "speech_rms_db_min": min((item["rms_ratio_db"] for item in speech
                                  if item["rms_ratio_db"] is not None), default=None),
        "speech_rms_db_max": max((item["rms_ratio_db"] for item in speech
                                  if item["rms_ratio_db"] is not None), default=None),
        "flex_residual_rms": max((item["output_rms"] for item in flex), default=None),
    }


def mapping_check(records: Sequence[Dict[str, Any]], source_length: int,
                  target_length: int) -> Dict[str, Any]:
    """Validate nominal source coverage and monotone output placement."""
    nominal = [int(record["nominal_source_start"]) for record in records]
    gaps: List[int] = []
    for index in range(1, len(nominal)):
        if nominal[index] <= nominal[index - 1]:
            gaps.append(nominal[index])
    coverage_ok = bool(nominal) and nominal[0] == 0 and gaps == [] and nominal[-1] < source_length
    centers = [int(record["output_center"]) for record in records]
    monotone = all(b >= a for a, b in zip(centers, centers[1:]))
    within = all(0 <= center <= target_length for center in centers)
    return {
        "nominal_source_starts": nominal,
        "source_interval_covered": coverage_ok,
        "nonmonotone_starts": gaps,
        "output_centers_monotone": monotone,
        "output_centers_within_target": within,
        "window_count": len(records),
        "qualifies": coverage_ok and monotone and within,
    }


def buffering_metrics(prefix: Sequence[float], target: int, frame: int,
                      rebuffer: Dict[str, Any] | None) -> Dict[str, Any]:
    """Model caller-owned playback buffering; no device or fill/flush measurement."""
    checkpoints = [0, len(prefix) // 4, len(prefix) // 2, (3 * len(prefix)) // 4, len(prefix) - 1]
    timeline = []
    for index in checkpoints:
        available = float(prefix[max(0, min(index, len(prefix) - 1))])
        timeline.append({
            "source_sample": index,
            "source_ns": index * 62500,
            "ideal_output_samples": available,
            "full_output_frames": int(available // frame),
        })
    final_valid = target % frame
    if final_valid == 0 and target:
        final_valid = frame
    result: Dict[str, Any] = {
        "model": "caller-owned FIFO over whole-clip synthetic source; no device pacing",
        "source_lookahead_samples": len(prefix),
        "checkpoints": timeline,
        "target_output_samples": target,
        "final_partial_window_valid_samples": final_valid,
        "final_partial_window_frames": int(math.ceil(target / frame)) if target else 0,
        "qualifies_device_claim": False,
    }
    if rebuffer is not None:
        anchor = int(rebuffer["source_sample"])
        gap = int(rebuffer["gap_output_samples"])
        available = float(prefix[anchor])
        result["rebuffer"] = {
            "source_sample": anchor,
            "source_ns": anchor * 62500,
            "gap_output_samples": gap,
            "available_before_gap": available,
            "required_after_gap": available + gap,
            "uncompensated_deficit": gap,
            "decision_tied_to_source_timestamp": True,
        }
    else:
        result["rebuffer"] = None
    return result


def rate_bounds(schedule: Sequence[tuple[int, float]]) -> Dict[str, Any]:
    rates = [float(rate) for _, rate in schedule]
    return {
        "min": min(rates) if rates else None,
        "max": max(rates) if rates else None,
        "within_proxy_bounds": all(MIN_RATE <= value <= MAX_RATE for value in rates),
        "changes": [
            {"source_sample": int(sample), "source_ns": int(sample) * 62500, "rate": float(rate)}
            for sample, rate in schedule
        ],
    }
