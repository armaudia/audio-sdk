"""Deterministic synthetic paired render/capture fixtures for the MDF reference.

No audio file, corpus, model, download or real recording is used. Every stream
is generated from an explicit LCG and analytic echo/near-end formulas. The
module is dependency-free and is imported by evaluate.py and test_reference.py.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import struct
from typing import Any, Iterable, Sequence

SCHEMA = "audio-sdk/speexdsp-mdf-reference/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FRAMES = 300
SAMPLE_COUNT = FRAMES * FRAME_SAMPLES
FILTER_LENGTH_SAMPLES = 3200
LCG_SEED = 0x51ED270B
ECHO_DELAY_SAMPLES = 480
ECHO_TAPS = (0.35, 0.50, 0.15)
ECHO_GAIN = 0.45
NOISE_SCALE = 0.002
NEAR_BURST_FRAMES = (150, 152)  # 2 x 160 samples = 20 ms of overlap
CONVERGED_FRAMES = (80, 140)
OVERLAP_FRAMES = NEAR_BURST_FRAMES
CASES = (
    "echo_only",
    "near_end_only",
    "overlap_small",
    "no_reference_passthrough",
    "misaligned_reference",
)


def canonical(payload: Any) -> str:
    """Canonical JSON with one trailing newline; no NaN/Infinity allowed."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      allow_nan=False) + "\n"


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pack_f32(values: Sequence[float]) -> bytes:
    return struct.pack("<%df" % len(values), *values)


def digest_f32(values: Sequence[float]) -> str:
    return hashlib.sha256(pack_f32(values)).hexdigest()


def lcg_sequence(seed: int, count: int) -> list[float]:
    """Legacy-style LCG mapped to [-1, 1); identical in every run."""
    state = seed & 0xFFFFFFFF
    out: list[float] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        out.append((state >> 8) / 8388608.0 - 1.0)
    return out


def near_wave(count: int) -> list[float]:
    """Analytic narrow-band speech surrogate; not speech and not a recording."""
    out: list[float] = []
    for n in range(count):
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.0 * n / count)
        carrier = math.sin(2.0 * math.pi * 180.0 * n / SAMPLE_RATE_HZ)
        harmonic = 0.4 * math.sin(2.0 * math.pi * 360.0 * n / SAMPLE_RATE_HZ)
        out.append(0.12 * envelope * (carrier + harmonic))
    return out


def echo_path(render: Sequence[float], delay: int = ECHO_DELAY_SAMPLES,
              gain: float = ECHO_GAIN) -> list[float]:
    """Frozen three-tap delayed render path; movement is explicitly none."""
    out = [0.0] * len(render)
    for n in range(len(render)):
        total = 0.0
        for tap, coefficient in enumerate(ECHO_TAPS):
            index = n - delay + tap
            if 0 <= index < len(render):
                total += coefficient * render[index]
        out[n] = gain * total
    return out


def generate() -> dict[str, dict[str, list[float]]]:
    """Build every case as paired render/capture f32-ready streams."""
    draws = lcg_sequence(LCG_SEED, SAMPLE_COUNT * 2)
    render: list[float] = []
    lowpass = 0.0
    for index in range(SAMPLE_COUNT):
        lowpass = 0.6 * lowpass + 0.4 * draws[index]
        render.append(0.4 * lowpass)
    noise = [NOISE_SCALE * value for value in draws[SAMPLE_COUNT:]]
    echo = echo_path(render)
    near = near_wave(SAMPLE_COUNT)
    zeros = [0.0] * SAMPLE_COUNT

    burst = [0.0] * SAMPLE_COUNT
    burst_start = NEAR_BURST_FRAMES[0] * FRAME_SAMPLES
    burst_end = NEAR_BURST_FRAMES[1] * FRAME_SAMPLES
    burst[burst_start:burst_end] = near[burst_start:burst_end]

    near_full = [0.0] * SAMPLE_COUNT
    near_start = 80 * FRAME_SAMPLES
    near_end = 240 * FRAME_SAMPLES
    near_full[near_start:near_end] = near[near_start:near_end]

    shifted = [0.0] * SAMPLE_COUNT
    shift = FRAME_SAMPLES
    shifted[shift:] = render[:-shift]

    streams = {
        "echo_only": {
            "render": render,
            "capture": [echo[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "near_end_only": {
            "render": zeros,
            "capture": [near_full[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "overlap_small": {
            "render": render,
            "capture": [echo[n] + burst[n] + noise[n]
                        for n in range(SAMPLE_COUNT)],
        },
        "no_reference_passthrough": {
            "render": zeros,
            "capture": [echo[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "misaligned_reference": {
            "render": shifted,
            "capture": [echo[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
    }
    for case in streams.values():
        for key in ("render", "capture"):
            values = case[key]
            if len(values) != SAMPLE_COUNT:
                raise AssertionError("fixture length mismatch")
            if any(not math.isfinite(value) or abs(value) > 1.0
                   for value in values):
                raise AssertionError("fixture outside valid range")
    return streams


def spec() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "frames": FRAMES,
        "filter_length_samples": FILTER_LENGTH_SAMPLES,
        "lcg_seed": LCG_SEED,
        "echo_delay_samples": ECHO_DELAY_SAMPLES,
        "echo_taps": list(ECHO_TAPS),
        "echo_gain": ECHO_GAIN,
        "noise_scale": NOISE_SCALE,
        "near_burst_frames": list(NEAR_BURST_FRAMES),
        "converged_frames": list(CONVERGED_FRAMES),
        "echo_path_movement": "none; frozen three-tap delay/gain",
        "reset_schedule": "none within a case; fresh state per case and repeat",
        "conversion": "float -> lrint(x*32767) int16 -> x/32768 float",
    }


def energy(values: Iterable[float], start: int, end: int) -> float:
    return sum(value * value for value in itertools.islice(values, start, end))


def erle_db(capture: Sequence[float], output: Sequence[float],
            start: int, end: int) -> float:
    before = energy(capture, start, end)
    after = energy(output, start, end)
    return 10.0 * math.log10((before + 1e-12) / (after + 1e-12))


def amplitude_ratio(output: Sequence[float], reference: Sequence[float],
                    start: int, end: int) -> float:
    after = energy(output, start, end)
    expected = energy(reference, start, end)
    return math.sqrt((after + 1e-12) / (expected + 1e-12))


def round6(value: float) -> float:
    return round(float(value), 6)
