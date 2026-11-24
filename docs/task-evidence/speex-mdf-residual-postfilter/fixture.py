# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic paired render/capture fixtures for this task.

No audio file, corpus, model, download or real recording is used. Every stream
is generated from an explicit LCG and analytic echo/near-end formulas. The
module is dependency-free and is imported by scorer.py, reference.py, run.py
and the unit tests.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import struct
from typing import Any, Iterable, Sequence

SCHEMA_ID = "audio-sdk/speex-mdf-residual-postfilter/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FRAMES = 300
SAMPLE_COUNT = FRAMES * FRAME_SAMPLES
FILTER_LENGTH_SAMPLES = 3200
LCG_SEED = 0x9E3779B9
ECHO_DELAY_SAMPLES = 512
ECHO_TAPS = (0.30, 0.45, 0.25)
ECHO_GAIN = 0.40
NOISE_SCALE = 0.0015
NEAR_BURST_FRAMES = (150, 152)  # 2 x 160 samples = 20 ms of overlap
NEAR_FULL_FRAMES = (80, 240)
CONVERGED_FRAMES = (80, 140)
NEAR_ONLY_WINDOW_FRAMES = (100, 220)
MISALIGNMENT_SHIFT_SAMPLES = FRAME_SAMPLES

CONDITIONS = (
    "echo_only",
    "near_end_only",
    "overlap_20ms",
    "no_reference",
    "misaligned_render",
)


def canonical(payload: Any) -> str:
    """Canonical JSON with one trailing newline; no NaN/Infinity allowed."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      allow_nan=False) + "\n"


def canonical_bytes(payload: Any) -> bytes:
    return canonical(payload).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def pack_f32(values: Sequence[float]) -> bytes:
    return struct.pack("<%df" % len(values), *values)


def digest_f32(values: Sequence[float]) -> str:
    return sha256_bytes(pack_f32(values))


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
        envelope = 0.55 + 0.45 * math.sin(2.0 * math.pi * 3.0 * n / count)
        carrier = math.sin(2.0 * math.pi * 210.0 * n / SAMPLE_RATE_HZ)
        harmonic = 0.35 * math.sin(2.0 * math.pi * 420.0 * n / SAMPLE_RATE_HZ)
        out.append(0.11 * envelope * (carrier + harmonic))
    return out


def echo_path(render: Sequence[float],
              delay: int = ECHO_DELAY_SAMPLES,
              taps: Sequence[float] = ECHO_TAPS,
              gain: float = ECHO_GAIN) -> list[float]:
    """Frozen three-tap delayed render path; movement is explicitly none."""
    out = [0.0] * len(render)
    for n in range(len(render)):
        total = 0.0
        for tap, coefficient in enumerate(taps):
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
        lowpass = 0.55 * lowpass + 0.45 * draws[index]
        render.append(0.42 * lowpass)
    noise = [NOISE_SCALE * value for value in draws[SAMPLE_COUNT:]]
    echo = echo_path(render)
    near = near_wave(SAMPLE_COUNT)
    zeros = [0.0] * SAMPLE_COUNT

    burst = [0.0] * SAMPLE_COUNT
    burst_start = NEAR_BURST_FRAMES[0] * FRAME_SAMPLES
    burst_end = NEAR_BURST_FRAMES[1] * FRAME_SAMPLES
    burst[burst_start:burst_end] = near[burst_start:burst_end]

    near_full = [0.0] * SAMPLE_COUNT
    near_start = NEAR_FULL_FRAMES[0] * FRAME_SAMPLES
    near_end = NEAR_FULL_FRAMES[1] * FRAME_SAMPLES
    near_full[near_start:near_end] = near[near_start:near_end]

    shifted = [0.0] * SAMPLE_COUNT
    shift = MISALIGNMENT_SHIFT_SAMPLES
    shifted[shift:] = render[:-shift]

    streams: dict[str, dict[str, list[float]]] = {
        "echo_only": {
            "render": render,
            "capture": [echo[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "near_end_only": {
            "render": zeros,
            "capture": [near_full[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "overlap_20ms": {
            "render": render,
            "capture": [echo[n] + burst[n] + noise[n]
                        for n in range(SAMPLE_COUNT)],
        },
        "no_reference": {
            "render": zeros,
            "capture": [echo[n] + noise[n] for n in range(SAMPLE_COUNT)],
        },
        "misaligned_render": {
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
        "schema_id": SCHEMA_ID,
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
        "near_full_frames": list(NEAR_FULL_FRAMES),
        "converged_frames": list(CONVERGED_FRAMES),
        "near_only_window_frames": list(NEAR_ONLY_WINDOW_FRAMES),
        "misalignment_shift_samples": MISALIGNMENT_SHIFT_SAMPLES,
        "echo_path_movement": "none; frozen three-tap delay/gain",
        "reset_schedule": "none within a case; fresh state per case and repeat",
        "conversion": "float -> lrint(x*32767) int16 -> x/32768 float",
    }


def stream_digests(streams: dict[str, dict[str, list[float]]] | None = None
                   ) -> dict[str, dict[str, str]]:
    data = streams if streams is not None else generate()
    return {
        case: {
            "render": digest_f32(values["render"]),
            "capture": digest_f32(values["capture"]),
        }
        for case, values in data.items()
    }


def fixture_digest() -> str:
    return digest_text(canonical({"fixture": spec(),
                                  "digests": stream_digests()}))


def energy(values: Iterable[float], start: int, end: int) -> float:
    return sum(value * value for value in itertools.islice(values, start, end))


def erle_db(capture: Sequence[float], output: Sequence[float],
            start: int, end: int) -> float:
    before = energy(capture, start, end)
    after = energy(output, start, end)
    return 10.0 * math.log10((before + 1e-12) / (after + 1e-12))


def rms_ratio(output: Sequence[float], reference: Sequence[float],
              start: int, end: int) -> float:
    after = energy(output, start, end)
    expected = energy(reference, start, end)
    return math.sqrt((after + 1e-12) / (expected + 1e-12))


def attenuation_db(output: Sequence[float], reference: Sequence[float],
                   start: int, end: int) -> float:
    return 20.0 * math.log10(rms_ratio(output, reference, start, end))


def window(frames: Sequence[int]) -> tuple[int, int]:
    return frames[0] * FRAME_SAMPLES, frames[1] * FRAME_SAMPLES


def round6(value: float) -> float:
    return round(float(value), 6)
