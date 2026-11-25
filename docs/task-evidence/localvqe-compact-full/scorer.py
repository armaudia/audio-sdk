# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic scoring for the LocalVQE compact full room fixture.

All values are exact arithmetic over the frozen synthetic streams.  The scorer
is task-local, model-free and makes no quality claim.  Echo attenuation is
measured on echo-only regions; near-end damage is measured against the known
synthetic near-end component after compensating the declared one-hop content
delay.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import fixture


def _round(value: float, digits: int = 12) -> float:
    if not math.isfinite(value):
        raise ValueError("nonfinite_metric")
    result = round(float(value), digits)
    return 0.0 if result == 0.0 else result


def energy(values: Sequence[float]) -> float:
    return sum(value * value for value in values)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(energy(values) / len(values))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def align_output(output: Sequence[float],
                 delay: int = fixture.ALGORITHMIC_LATENCY_SAMPLES
                 ) -> Tuple[List[float], int]:
    """Compensate the declared one-hop output delay.

    The returned valid prefix is ``len(output) - delay`` samples.  Samples past
    that prefix are not available and are never scored as output.
    """
    valid = max(0, len(output) - delay)
    aligned = [output[index + delay] for index in range(valid)]
    return aligned, valid


def _clip_interval(start: int, end: int, valid: int) -> Tuple[int, int] | None:
    start = max(0, start)
    end = min(end, valid)
    if end <= start:
        return None
    return start, end


def _gather(values: Sequence[float], start: int, end: int) -> List[float]:
    return list(values[start:end])


def erle_db(mic: Sequence[float], output: Sequence[float],
            intervals: Iterable[Tuple[int, int]], delay: int
            ) -> Tuple[float | None, int]:
    """Echo return loss enhancement over pooled echo-only intervals."""
    aligned, valid = align_output(output, delay)
    input_energy = 0.0
    output_energy = 0.0
    samples = 0
    for start, end in intervals:
        clipped = _clip_interval(start, end, valid)
        if clipped is None:
            continue
        left, right = clipped
        input_energy += energy(mic[left:right])
        output_energy += energy(aligned[left:right])
        samples += right - left
    if samples == 0:
        return None, 0
    if output_energy <= 0.0:
        return None, samples
    return _round(10.0 * math.log10(input_energy / output_energy)), samples


def snr_db(target: Sequence[float], estimate: Sequence[float],
           start: int, end: int) -> float | None:
    """Near-reference SNR: penalizes residual echo, noise and distortion."""
    target_slice = _gather(target, start, end)
    error_slice = [estimate[index] - target[index]
                   for index in range(start, end)]
    signal = energy(target_slice)
    error = energy(error_slice)
    if signal <= 0.0:
        return None
    if error <= 0.0:
        return None
    return _round(10.0 * math.log10(signal / error))


def si_sdr_db(target: Sequence[float], estimate: Sequence[float],
              start: int, end: int) -> float | None:
    """Scale-invariant SDR of the aligned output against the near component."""
    target_slice = _gather(target, start, end)
    estimate_slice = _gather(estimate, start, end)
    target_energy = energy(target_slice)
    if target_energy <= 0.0:
        return None
    projection = sum(left * right
                     for left, right in zip(target_slice, estimate_slice))
    alpha = projection / target_energy
    scaled = [alpha * value for value in target_slice]
    residual = [estimate_slice[index] - scaled[index]
                for index in range(len(target_slice))]
    signal = energy(scaled)
    noise = energy(residual)
    if signal <= 0.0 or noise <= 0.0:
        return None
    return _round(10.0 * math.log10(signal / noise))


def _intervals_for(roles: Sequence[str]) -> List[Tuple[int, int]]:
    return [(segment["start"], segment["end"])
            for segment in fixture.SEGMENTS
            if any(role in segment["roles"] for role in roles)]


ECHO_INTERVALS = _intervals_for(("echo_only",))
ECHO_PRE_CHANGE_INTERVALS = [(4608, 15360), (40960, fixture.MOVEMENT_CHANGE_SAMPLE)]
ECHO_POST_CHANGE_INTERVALS = [(fixture.MOVEMENT_CHANGE_SAMPLE, 52736)]
NEAR_INTERVALS = _intervals_for(("near_only", "overlap"))
OVERLAP_INTERVALS = _intervals_for(("overlap",))


def stratum_metrics(mic: Sequence[float], near: Sequence[float],
                    output: Sequence[float]) -> Dict[str, Dict[str, Any]]:
    aligned, valid = align_output(output)
    rows: Dict[str, Dict[str, Any]] = {}
    for segment in fixture.SEGMENTS:
        start, end = segment["start"], segment["end"]
        clipped = _clip_interval(start, end, valid)
        samples = 0 if clipped is None else clipped[1] - clipped[0]
        input_slice = mic[start:end]
        output_slice = aligned[start:end] if samples else []
        row: Dict[str, Any] = {
            "start_sample": start,
            "end_sample": end,
            "roles": list(segment["roles"]),
            "path": segment["path"],
            "samples": end - start,
            "valid_scored_samples": samples,
            "input_rms": _round(rms(input_slice)),
            "output_rms": _round(rms(output_slice)),
            "nonfinite_output_samples": sum(
                1 for value in output_slice if not math.isfinite(value)),
            "peak_abs_output": _round(peak(output_slice)),
        }
        if samples and "echo_only" in segment["roles"]:
            value, count = erle_db(mic, output, [(start, end)],
                                   fixture.ALGORITHMIC_LATENCY_SAMPLES)
            row["echo_erle_db"] = value
            row["echo_samples"] = count
            row["identity_echo_erle_db"] = 0.0
        if samples and any(role in segment["roles"]
                           for role in ("near_only", "overlap")):
            near_slice = near[start:end]
            output_slice = aligned[start:end]
            row["near_snr_db"] = snr_db(near, aligned, start, end)
            row["near_si_sdr_db"] = si_sdr_db(near, aligned, start, end)
            row["identity_near_snr_db"] = snr_db(near, mic, start, end)
            row["identity_near_si_sdr_db"] = si_sdr_db(near, mic, start, end)
            near_rms = rms(near_slice)
            row["near_rms_ratio"] = (
                _round(rms(output_slice) / near_rms) if near_rms else None)
        if samples and "silence" in segment["roles"]:
            row["identity_rms"] = _round(rms(input_slice))
        rows[segment["id"]] = row
    return rows


def _pooled_echo(mic: Sequence[float], output: Sequence[float],
                 intervals: Iterable[Tuple[int, int]]) -> Dict[str, Any]:
    value, samples = erle_db(mic, output, intervals,
                             fixture.ALGORITHMIC_LATENCY_SAMPLES)
    return {"erle_db": value, "echo_samples": samples}


def _pooled_near(mic: Sequence[float], near: Sequence[float],
                 output: Sequence[float],
                 intervals: Iterable[Tuple[int, int]]) -> Dict[str, Any]:
    aligned, valid = align_output(output)
    total_signal = 0.0
    total_error = 0.0
    total_identity_error = 0.0
    total_output = 0.0
    total_target = 0.0
    samples = 0
    for start, end in intervals:
        clipped = _clip_interval(start, end, valid)
        if clipped is None:
            continue
        left, right = clipped
        total_signal += energy(near[left:right])
        total_error += energy([aligned[index] - near[index]
                               for index in range(left, right)])
        total_identity_error += energy([mic[index] - near[index]
                                        for index in range(left, right)])
        total_output += energy(aligned[left:right])
        total_target += energy(near[left:right])
        samples += right - left
    snr = (_round(10.0 * math.log10(total_signal / total_error))
           if total_signal > 0.0 and total_error > 0.0 else None)
    identity_snr = (_round(10.0 * math.log10(
        total_signal / total_identity_error))
        if total_signal > 0.0 and total_identity_error > 0.0 else None)
    target_rms = math.sqrt(total_target / samples) if samples else 0.0
    output_rms = math.sqrt(total_output / samples) if samples else 0.0
    return {
        "near_snr_db": snr,
        "identity_near_snr_db": identity_snr,
        "near_samples": samples,
        "near_rms_ratio": (_round(output_rms / target_rms)
                           if target_rms else None),
        "output_energy_over_near_energy": (
            _round(total_output / total_target) if total_target else None),
    }


def score(mic: Sequence[float], near: Sequence[float],
          output: Sequence[float]) -> Dict[str, Any]:
    aligned, valid = align_output(output)
    strata = stratum_metrics(mic, near, output)
    echo_all = _pooled_echo(mic, output, ECHO_INTERVALS)
    echo_pre = _pooled_echo(mic, output, ECHO_PRE_CHANGE_INTERVALS)
    echo_post = _pooled_echo(mic, output, ECHO_POST_CHANGE_INTERVALS)
    near_pool = _pooled_near(mic, near, output, NEAR_INTERVALS)
    overlap_pool = _pooled_near(mic, near, output, OVERLAP_INTERVALS)

    # Uncompensated comparison exposes why the declared one-hop delay must be
    # accounted for before scoring near-end preservation.
    overlap_start, overlap_end = 28672, 39936
    overlap_end = min(overlap_end, valid)
    unaligned_snr = snr_db(near, output, overlap_start, overlap_end)
    aligned_snr = snr_db(near, aligned, overlap_start, overlap_end)

    return {
        "strata": strata,
        "echo": {
            "pooled_echo_only": echo_all,
            "pooled_pre_movement": echo_pre,
            "pooled_post_movement": echo_post,
            "movement_drop_db": (
                _round(echo_pre["erle_db"] - echo_post["erle_db"])
                if echo_pre["erle_db"] is not None
                and echo_post["erle_db"] is not None else None),
            "identity_erle_db": 0.0,
            "formula": (
                "10*log10(sum(mic^2)/sum(aligned_output^2)) over echo-only "
                "samples; aligned_output compensates the declared 256-sample "
                "one-hop content delay"),
        },
        "near_end": {
            "pooled_near": near_pool,
            "pooled_overlap": overlap_pool,
            "overlap_aligned_snr_db": aligned_snr,
            "overlap_unaligned_snr_db": unaligned_snr,
            "alignment_gain_db": (
                _round(aligned_snr - unaligned_snr)
                if aligned_snr is not None and unaligned_snr is not None
                else None),
            "delay_compensation_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "formula": (
                "near-reference SNR = 10*log10(sum(near^2)/"
                "sum((aligned_output-near)^2)); SI-SDR uses a least-squares "
                "scale and penalizes residual echo and noise"),
        },
        "availability": {
            "output_samples": len(output),
            "valid_aligned_samples": valid,
            "unavailable_tail_samples": len(output) - valid,
            "tail_is_not_scored": True,
        },
        "peaks": {
            "max_abs_output": _round(peak(output)),
            "clipped_samples": sum(1 for value in output if abs(value) > 1.0),
            "nonfinite_output_samples": sum(
                1 for value in output if not math.isfinite(value)),
            "limiter_used": False,
            "within_unit_range": all(abs(value) <= 1.0 for value in output),
        },
    }
