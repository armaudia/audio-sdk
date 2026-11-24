# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free metrics for the synthetic receive DRC evidence package.

This module measures gain, steady-state frequency response, step attack and
release, peaks/headroom, sample delay, nonfinite counts, coarse band energy and
instrumented level/masker control quantities. It never imports numpy, scipy,
STOI, a speech corpus or a listening model. None of its outputs is a human
intelligibility, quality or release score.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence

SCORER_ID = "audio-sdk/full-band-receive-drc-scoring/0.1"
BANDS_HZ = {
    "low": (125.0, 250.0, 375.0, 500.0),
    "mid": (750.0, 1000.0, 1500.0, 2000.0),
    "high": (2500.0, 3500.0, 5000.0, 7000.0),
}


class ScorerError(ValueError):
    """Raised for a malformed or nonfinite metric input."""


def r6(value: Optional[float]) -> Optional[float]:
    """Round a finite float for canonical reporting, preserving None."""
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ScorerError("nonfinite_metric")
    return round(number, 6)


def delta_opt(value: Optional[float], baseline: Optional[float]) -> Optional[float]:
    """Rounded difference, preserving None when either operand is undefined."""
    if value is None or baseline is None:
        return None
    return r6(value - baseline)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise ScorerError("empty_signal")
    values = [float(value) for value in samples]
    if any(not math.isfinite(value) for value in values):
        raise ScorerError("nonfinite_input")
    return math.sqrt(sum(value * value for value in values) / len(values))


def peak_abs(samples: Sequence[float]) -> float:
    if not samples:
        raise ScorerError("empty_signal")
    values = [float(value) for value in samples]
    if any(not math.isfinite(value) for value in values):
        raise ScorerError("nonfinite_input")
    return max(abs(value) for value in values)


def nonfinite_count(samples: Sequence[float]) -> int:
    return sum(1 for value in samples if not math.isfinite(float(value)))


def db_from_linear(value: float) -> Optional[float]:
    if value <= 0.0 or not math.isfinite(value):
        return None
    return 20.0 * math.log10(value)


def db_ratio(numerator: float, denominator: float) -> Optional[float]:
    if denominator <= 0.0:
        return None
    return db_from_linear(numerator / denominator)


def scale_to_rms(samples: Sequence[float], target_rms: float) -> tuple:
    if target_rms <= 0.0 or not math.isfinite(target_rms):
        raise ScorerError("invalid_target_rms")
    source_rms = rms(samples)
    if source_rms <= 0.0:
        raise ScorerError("zero_source_rms")
    factor = target_rms / source_rms
    return tuple(float(value) * factor for value in samples)


def gain_metrics(reference_samples: Sequence[float], output_samples: Sequence[float]) -> Dict[str, Any]:
    """Paired RMS/peak gain, correlation and finite-output diagnostics."""
    if len(reference_samples) != len(output_samples):
        raise ScorerError("length_mismatch")
    nonfinite = nonfinite_count(output_samples)
    valid = [(float(a), float(b)) for a, b in zip(reference_samples, output_samples)
             if math.isfinite(float(a)) and math.isfinite(float(b))]
    if not valid:
        return {
            "correlation": None,
            "input_rms": None,
            "max_abs_difference": None,
            "nonfinite_count": nonfinite,
            "output_rms": None,
            "peak_abs_input": None,
            "peak_abs_output": None,
            "peak_gain_db": None,
            "rms_gain_db": None,
            "status": "not_measured",
        }
    inputs = [pair[0] for pair in valid]
    outputs = [pair[1] for pair in valid]
    in_rms = rms(inputs)
    out_rms = rms(outputs)
    in_peak = peak_abs(inputs)
    out_peak = peak_abs(outputs)
    mean_in = sum(inputs) / len(inputs)
    mean_out = sum(outputs) / len(outputs)
    covariance = sum((a - mean_in) * (b - mean_out) for a, b in valid)
    variance_in = sum((a - mean_in) ** 2 for a in inputs)
    variance_out = sum((b - mean_out) ** 2 for b in outputs)
    correlation = None
    if variance_in > 0.0 and variance_out > 0.0:
        correlation = covariance / math.sqrt(variance_in * variance_out)
    return {
        "correlation": r6(correlation),
        "input_rms": r6(in_rms),
        "max_abs_difference": r6(max(abs(a - b) for a, b in valid)),
        "nonfinite_count": nonfinite,
        "output_rms": r6(out_rms),
        "peak_abs_input": r6(in_peak),
        "peak_abs_output": r6(out_peak),
        "peak_gain_db": r6(db_ratio(out_peak, in_peak)),
        "rms_gain_db": r6(db_ratio(out_rms, in_rms)),
        "status": "measured",
    }


def frequency_response(rows: Sequence[Dict[str, Any]], rate_hz: int,
                       skip_fraction: float = 0.2) -> List[Dict[str, Any]]:
    """Steady-state gain at each probe tone, skipping startup samples."""
    measured: List[Dict[str, Any]] = []
    for row in rows:
        signal = tuple(float(value) for value in row["input"])
        output = tuple(float(value) for value in row["output"])
        if len(signal) != len(output) or nonfinite_count(output):
            raise ScorerError("invalid_frequency_response_row")
        start = int(len(signal) * skip_fraction)
        if start >= len(signal) - 1:
            raise ScorerError("frequency_response_window_too_short")
        in_rms = rms(signal[start:])
        out_rms = rms(output[start:])
        gain_db = db_ratio(out_rms, in_rms)
        entry = {
            "amplitude": r6(float(row["amplitude"])),
            "frequency_hz": float(row["frequency_hz"]),
            "gain_db": r6(gain_db),
            "input_rms": r6(in_rms),
            "output_rms": r6(out_rms),
            "sample_rate_hz": int(rate_hz),
            "samples": len(signal),
        }
        if "expected_gain_db" in row:
            expected = float(row["expected_gain_db"])
            entry["expected_gain_db"] = r6(expected)
            entry["error_db"] = r6(gain_db - expected if gain_db is not None else None)
        measured.append(entry)
    return sorted(measured, key=lambda item: item["frequency_hz"])


def _moving_gain(signal: Sequence[float], output: Sequence[float], window: int) -> List[float]:
    """Windowed mean of |output/input| where the probe input is nonzero."""
    ratios: List[float] = []
    for value, result in zip(signal, output):
        value = float(value)
        result = float(result)
        if math.isfinite(value) and math.isfinite(result) and abs(value) > 1e-5:
            ratios.append(abs(result / value))
        else:
            ratios.append(math.nan)
    smoothed: List[float] = []
    running = 0.0
    count = 0
    history: List[float] = []
    for ratio in ratios:
        if math.isfinite(ratio):
            running += ratio
            count += 1
        history.append(ratio)
        if len(history) > window:
            old = history.pop(0)
            if math.isfinite(old):
                running -= old
                count -= 1
        smoothed.append(running / count if count else math.nan)
    return smoothed


def _first_crossing(values: Sequence[float], start: int, end: int, target: float,
                    falling: bool) -> Optional[int]:
    previous: Optional[float] = None
    for index in range(start, min(end, len(values))):
        value = values[index]
        if not math.isfinite(value):
            continue
        if previous is not None:
            if falling and previous >= target and value <= target:
                return index
            if not falling and previous <= target and value >= target:
                return index
        previous = value
    return None


def step_response(signal: Sequence[float], output: Sequence[float], rate_hz: int,
                  step_on: int, step_off: int, window_ms: float = 5.0) -> Dict[str, Any]:
    """Estimate gain change attack/release from a two-level step fixture."""
    if len(signal) != len(output) or nonfinite_count(output):
        raise ScorerError("invalid_step_response")
    if not 0 < step_on < step_off < len(signal):
        raise ScorerError("invalid_step_boundaries")
    window = max(2, int(rate_hz * window_ms / 1000.0))
    gains = _moving_gain(signal, output, window)
    before = [value for value in gains[:step_on] if math.isfinite(value)]
    during_end = min(step_off, step_on + int(0.5 * rate_hz))
    during = [value for value in gains[step_on + window:during_end] if math.isfinite(value)]
    after = [value for value in gains[step_off + window:] if math.isfinite(value)]
    if not before or not during or not after:
        raise ScorerError("insufficient_step_windows")
    initial = sum(before) / len(before)
    settled = sum(during) / len(during)
    recovered = sum(after) / len(after)
    falling = settled < initial
    attack_target = initial + 0.9 * (settled - initial)
    release_target = settled + 0.9 * (recovered - settled)
    attack_index = _first_crossing(gains, step_on, during_end, attack_target, falling)
    release_index = _first_crossing(gains, step_off, len(gains), release_target, not falling)
    return {
        "attack_ms": r6((attack_index - step_on) * 1000.0 / rate_hz)
        if attack_index is not None else None,
        "gain_db_before": r6(db_from_linear(initial)),
        "gain_db_during": r6(db_from_linear(settled)),
        "gain_db_after": r6(db_from_linear(recovered)),
        "release_ms": r6((release_index - step_off) * 1000.0 / rate_hz)
        if release_index is not None else None,
        "status": "measured" if attack_index is not None and release_index is not None
        else "not_measured",
        "window_ms": r6(window_ms),
    }


def headroom(samples: Sequence[float], ceiling: float = 1.0) -> Dict[str, Any]:
    peak = peak_abs(samples)
    return {
        "ceiling": r6(ceiling),
        "ceiling_exceed_count": sum(1 for value in samples if abs(float(value)) > ceiling),
        "headroom_to_ceiling_db": r6(db_ratio(ceiling, peak)),
        "headroom_to_full_scale_db": r6(db_ratio(1.0, peak)),
        "nonfinite_count": nonfinite_count(samples),
        "peak_abs": r6(peak),
        "status": "measured",
    }


def delay_samples(signal: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    if len(signal) != len(output):
        raise ScorerError("length_mismatch")
    input_index = max(range(len(signal)), key=lambda index: abs(float(signal[index])))
    output_index = max(range(len(output)), key=lambda index: abs(float(output[index])))
    return {
        "input_peak_index": input_index,
        "output_peak_index": output_index,
        "peak_delay_samples": output_index - input_index,
        "status": "measured",
    }


def _goertzel(samples: Sequence[float], frequency_hz: float, rate_hz: int) -> float:
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency_hz / rate_hz)
    s1 = 0.0
    s2 = 0.0
    for value in samples:
        current = float(value) + coefficient * s1 - s2
        s2 = s1
        s1 = current
    return s1 * s1 + s2 * s2 - coefficient * s1 * s2


def band_energy(samples: Sequence[float], rate_hz: int) -> Dict[str, Any]:
    """Coarse Goertzel band energies at fixed synthetic probe frequencies."""
    if nonfinite_count(samples):
        raise ScorerError("nonfinite_band_input")
    energies = {name: sum(_goertzel(samples, frequency, rate_hz) for frequency in frequencies)
                for name, frequencies in BANDS_HZ.items()}
    ratios = {
        "high_over_low_db": r6(db_ratio(energies["high"], energies["low"])),
        "mid_over_low_db": r6(db_ratio(energies["mid"], energies["low"])),
    }
    return {
        "bands": {name: r6(energy) for name, energy in energies.items()},
        **ratios,
        "status": "measured",
    }


def envelope_modulation_index(samples: Sequence[float], frame_samples: int = 160) -> Optional[float]:
    """Instrumented envelope variability proxy; not a speech-quality score."""
    if not samples:
        return None
    frames: List[float] = []
    for start in range(0, len(samples), frame_samples):
        block = samples[start:start + frame_samples]
        if block:
            frames.append(rms(block))
    if not frames or sum(frames) <= 0.0:
        return None
    mean = sum(frames) / len(frames)
    variance = sum((value - mean) ** 2 for value in frames) / len(frames)
    return math.sqrt(variance) / mean


def mix_at_tmr(target: Sequence[float], masker: Sequence[float], tmr_db: float,
               target_rms: Optional[float] = None) -> Dict[str, Any]:
    """Restore target power, scale a synthetic masker to the requested TMR, mix."""
    if len(target) != len(masker) or not target:
        raise ScorerError("invalid_mix_shape")
    if target_rms is not None:
        restored = scale_to_rms(target, target_rms)
    else:
        restored = tuple(float(value) for value in target)
    target_power = rms(restored)
    masker_power = rms(masker)
    if masker_power <= 0.0:
        raise ScorerError("zero_masker_rms")
    masker_scale = target_power / (masker_power * (10.0 ** (tmr_db / 20.0)))
    scaled_masker = tuple(float(value) * masker_scale for value in masker)
    mixture = tuple(float(a) + float(b) for a, b in zip(restored, scaled_masker))
    measured_tmr = db_ratio(target_power, rms(scaled_masker))
    return {
        "masker_scaled": scaled_masker,
        "measured_tmr_db": measured_tmr,
        "mixture": mixture,
        "restored_target": restored,
        "restored_target_rms": target_power,
        "requested_tmr_db": float(tmr_db),
    }


def masker_control_metrics(target: Sequence[float], masker: Sequence[float], tmr_db: float,
                           reference_rms: float, identity_target: Sequence[float]) -> Dict[str, Any]:
    """Level/masker control metrics; explicitly not STOI, ESTOI, MOS or listening."""
    mixed = mix_at_tmr(target, masker, tmr_db, target_rms=reference_rms)
    identity_mixed = mix_at_tmr(identity_target, masker, tmr_db, target_rms=reference_rms)
    mixture = mixed["mixture"]
    if nonfinite_count(mixture) or nonfinite_count(mixed["restored_target"]):
        raise ScorerError("nonfinite_masker_control")
    target_bands = band_energy(mixed["restored_target"], 16000)
    mixture_bands = band_energy(mixture, 16000)
    identity_target_bands = band_energy(identity_mixed["restored_target"], 16000)
    identity_mixture_bands = band_energy(identity_mixed["mixture"], 16000)
    target_emi = envelope_modulation_index(mixed["restored_target"])
    mixture_emi = envelope_modulation_index(mixture)
    identity_target_emi = envelope_modulation_index(identity_mixed["restored_target"])
    identity_mixture_emi = envelope_modulation_index(identity_mixed["mixture"])
    return {
        "identity_measured_tmr_db": r6(identity_mixed["measured_tmr_db"]),
        "measured_tmr_db": r6(mixed["measured_tmr_db"]),
        "identity_mixture_peak_abs": r6(peak_abs(identity_mixed["mixture"])),
        "mixture_headroom_to_full_scale_db": headroom(mixture)["headroom_to_full_scale_db"],
        "mixture_nonfinite_count": nonfinite_count(mixture),
        "mixture_peak_abs": r6(peak_abs(mixture)),
        "delta_mixture_peak_abs": delta_opt(peak_abs(mixture),
                                           peak_abs(identity_mixed["mixture"])),
        "requested_tmr_db": r6(tmr_db),
        "restoration_error_db": r6(db_ratio(mixed["restored_target_rms"], reference_rms)),
        "status": "measured",
        "target_band_energy_db": {
            "high_over_low_db": target_bands["high_over_low_db"],
            "mid_over_low_db": target_bands["mid_over_low_db"],
        },
        "mixture_band_energy_db": {
            "high_over_low_db": mixture_bands["high_over_low_db"],
            "mid_over_low_db": mixture_bands["mid_over_low_db"],
        },
        "identity_target_band_energy_db": {
            "high_over_low_db": identity_target_bands["high_over_low_db"],
            "mid_over_low_db": identity_target_bands["mid_over_low_db"],
        },
        "identity_mixture_band_energy_db": {
            "high_over_low_db": identity_mixture_bands["high_over_low_db"],
            "mid_over_low_db": identity_mixture_bands["mid_over_low_db"],
        },
        "delta_target_high_over_low_db": delta_opt(
            target_bands["high_over_low_db"], identity_target_bands["high_over_low_db"]),
        "delta_mixture_high_over_low_db": delta_opt(
            mixture_bands["high_over_low_db"], identity_mixture_bands["high_over_low_db"]),
        "target_envelope_modulation_index": r6(target_emi),
        "mixture_envelope_modulation_index": r6(mixture_emi),
        "identity_target_envelope_modulation_index": r6(identity_target_emi),
        "identity_mixture_envelope_modulation_index": r6(identity_mixture_emi),
        "delta_mixture_envelope_modulation_index": delta_opt(mixture_emi, identity_mixture_emi),
    }
