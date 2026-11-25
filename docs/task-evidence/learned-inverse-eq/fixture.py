# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Synthetic, deterministic DSP fixtures for SDK-LEARNED-INVERSE-EQ.

All signals are generated analytically or from a fixed-seed LCG.  No corpus,
recording, WAV, model asset or external runtime is read.  The fixtures are a
controlled EQ-identification experiment, not real speech evidence.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Tuple

import reference
import scorer

SEED = reference.FIXTURE_SEED
SAMPLE_RATE_HZ = reference.SAMPLE_RATE_HZ
FRAME_SAMPLES = reference.FRAME_SAMPLES
COMPARISON_LENGTH = FRAME_SAMPLES * 100
DSP_LENGTH = FRAME_SAMPLES * 60
COMPARISON_CONDITIONS = ("sweep", "step", "clean_speech")
DSP_CONDITIONS = ("sweep_log", "step", "impulse", "silence", "level_tone",
                  "tone_interference", "out_of_band_noise", "near_clip", "clipped_input")


def _sine(frequency_hz: float, length: int, amplitude: float = 1.0,
          phase: float = 0.0) -> Tuple[float, ...]:
    return tuple(amplitude * math.sin(2.0 * math.pi * frequency_hz
                                      * index / SAMPLE_RATE_HZ + phase)
                 for index in range(length))


def _fade(values: Tuple[float, ...], ramp: int = 160) -> Tuple[float, ...]:
    length = len(values)
    return tuple(value * min(1.0, index / ramp, (length - 1 - index) / ramp)
                 for index, value in enumerate(values))


def log_sweep(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    phase = 0.0
    output = []
    for index in range(length):
        fraction = index / max(length - 1, 1)
        frequency = 100.0 * (80.0 ** fraction)
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
        output.append(0.20 * math.sin(phase))
    return _fade(tuple(output))


def step_signal(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    noise = reference.lcg(SEED + 11)
    values = []
    for index in range(length):
        base = 0.05 if index < length // 4 else 0.30
        values.append(base + 0.002 * next(noise) + 0.06 * math.sin(
            2.0 * math.pi * 180.0 * index / SAMPLE_RATE_HZ))
    return _fade(tuple(values))


def impulse(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    values = [0.0] * length
    values[16] = 0.5
    return tuple(values)


def silence(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    return (0.0,) * length


def clean_speech(length: int = COMPARISON_LENGTH) -> Tuple[float, ...]:
    """Formant/harmonic synthetic speech-like excitation with syllable envelope."""
    noise = reference.lcg(SEED + 21)
    values = []
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 3.1 * time - 1.1)
        syllable **= 1.6
        pitch = 135.0 + 9.0 * math.sin(2.0 * math.pi * 0.7 * time)
        voiced = 0.0
        for harmonic in range(1, 9):
            amplitude = 1.0 / (harmonic ** 1.25)
            voiced += amplitude * math.sin(2.0 * math.pi * pitch * harmonic * time
                                           + 0.3 * harmonic)
        formant = (math.sin(2.0 * math.pi * 620.0 * time)
                   + 0.55 * math.sin(2.0 * math.pi * 1180.0 * time)
                   + 0.25 * math.sin(2.0 * math.pi * 2550.0 * time))
        sample = 0.11 * syllable * (voiced + 0.35 * formant) + 0.004 * next(noise)
        values.append(sample)
    return _fade(tuple(values), ramp=320)


def level_tone(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    """Speech-like signal with level steps plus a 1 kHz interfering tone."""
    base = clean_speech(length)
    tone = _sine(1000.0, length, amplitude=0.035)
    noise = reference.lcg(SEED + 31)
    values = []
    for index, (speech, sinusoid) in enumerate(zip(base, tone)):
        if index < length // 3:
            scale = 0.45
        elif index < 2 * length // 3:
            scale = 1.25
        else:
            scale = 0.70
        values.append(scale * speech + sinusoid + 0.001 * next(noise))
    return tuple(values)


def tone_interference(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    base = clean_speech(length)
    tone = _sine(1000.0, length, amplitude=0.08)
    return tuple(speech + sinusoid for speech, sinusoid in zip(base, tone))


def out_of_band_noise(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    noise = reference.lcg(SEED + 41)
    values = []
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        high = sum(0.010 * math.sin(2.0 * math.pi * frequency * time + phase)
                   for frequency, phase in ((12000.0, 0.1), (13250.0, 1.2),
                                            (14100.0, 2.3), (14900.0, 0.7)))
        values.append(high + 0.002 * next(noise))
    return _fade(tuple(values))


def _scaled_to_peak(values: Tuple[float, ...], target: float) -> Tuple[float, ...]:
    observed = scorer.peak(values)
    if observed <= 0.0:
        return values
    scale = target / observed
    return tuple(value * scale for value in values)


def near_clip(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    return _scaled_to_peak(clean_speech(length), 0.98)


def clipped_input(length: int = DSP_LENGTH) -> Tuple[float, ...]:
    """Explicit adverse case with samples beyond nominal full scale."""
    values = []
    noise = reference.lcg(SEED + 51)
    for index in range(length):
        base = 1.35 * math.sin(2.0 * math.pi * 440.0 * index / SAMPLE_RATE_HZ)
        values.append(max(-1.4, min(1.4, base + 0.01 * next(noise))))
    return tuple(values)


def _perturb(clean: Tuple[float, ...], salt: int) -> Tuple[float, ...]:
    forward = reference.apply_cascade(clean, reference.FORWARD_COEFFICIENTS)
    noise = reference.lcg(SEED + salt)
    return tuple(value + 1e-5 * next(noise) for value in forward)


def cohort() -> Dict[str, Tuple[float, ...]]:
    items: Dict[str, Tuple[float, ...]] = {
        "sweep_log": log_sweep(),
        "step": step_signal(),
        "impulse": impulse(),
        "silence": silence(),
        "level_tone": level_tone(),
        "tone_interference": tone_interference(),
        "out_of_band_noise": out_of_band_noise(),
        "near_clip": near_clip(),
        "clipped_input": clipped_input(),
    }
    long_sweep = log_sweep(COMPARISON_LENGTH)
    long_step = step_signal(COMPARISON_LENGTH)
    long_speech = clean_speech(COMPARISON_LENGTH)
    # Only the speech clean reference is used directly by the report; the
    # sweep/step base signals are retained as paired clean members below.
    items["clean_speech"] = long_speech
    for name, clean in (("sweep", long_sweep), ("step", long_step),
                        ("clean_speech", long_speech)):
        items[name + "_clean"] = clean
        items[name + "_perturbed"] = _perturb(clean, 61 + len(name))
    return items


def fixture_spec() -> Dict[str, Any]:
    items = cohort()
    records = []
    for name in sorted(items):
        values = items[name]
        records.append({
            "name": name,
            "sample_count": len(values),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "finite": scorer.is_finite(values),
            "peak": scorer.round_float(scorer.peak(values), 12),
            "rms": scorer.round_float(scorer.rms(values), 12),
            "digest": scorer.digest_json([scorer.round_float(value, 12)
                                          for value in values]),
        })
    core = {
        "fixture_version": "learned-inverse-eq-signals-v1",
        "seed": SEED,
        "comparison_conditions": list(COMPARISON_CONDITIONS),
        "dsp_conditions": list(DSP_CONDITIONS),
        "perturbation_noise_amplitude": 1e-5,
        "signals": records,
    }
    core["sha256"] = scorer.digest_json(core)
    return core
