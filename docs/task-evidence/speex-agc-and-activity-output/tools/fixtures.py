# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, synthetic stimuli for the Speex AGC + advisory activity probe.

No corpus, model, weights, download or real speech is used. Every generator is
pure Python stdlib arithmetic; raw f32 fixtures are written only to a caller
scratch directory and are never committed.
"""
from __future__ import annotations

import hashlib
import math
import struct

RATE = 16000
FRAME = 160
SAMPLES = 16000  # 1 s, 100 frames
TAU = 2.0 * math.pi
NAN = struct.unpack("<f", struct.pack("<I", 0x7FC00000))[0]
INF = struct.unpack("<f", struct.pack("<I", 0x7F800000))[0]


class LCG:
    """Version-stable 32-bit LCG; no dependence on Python's random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def f32_bytes(values: list[float]) -> bytes:
    return b"".join(struct.pack("<f", value) for value in values)


def chirp(n: int = SAMPLES) -> list[float]:
    phase = 0.0
    out = []
    for i in range(n):
        fraction = i / (n - 1)
        frequency = 200.0 + 3800.0 * fraction
        amplitude = 0.20 + 0.30 * fraction
        phase += TAU * frequency / RATE
        out.append(amplitude * math.sin(phase))
    return out


def steps(n: int = SAMPLES) -> list[float]:
    out = []
    for i in range(n):
        frame = i // FRAME
        amplitude = 0.0 if frame < 20 else (0.04 if frame < 40 else
                                             (0.60 if frame < 70 else 0.04))
        out.append(amplitude * math.sin(TAU * 220.0 * i / RATE))
    return out


def impulse(n: int = SAMPLES) -> list[float]:
    out = [0.012 * math.sin(TAU * 300.0 * i / RATE) for i in range(n)]
    out[400] += 0.80
    return out


def silence(n: int = SAMPLES) -> list[float]:
    return [0.0] * n


def speech_like(n: int = SAMPLES) -> list[float]:
    out = []
    burst, gap, period = 1600, 640, 2240
    amplitudes = (0.55, 0.42, 0.50, 0.30, 0.52, 0.45)
    for i in range(n):
        slot, within = divmod(i, period)
        if slot >= len(amplitudes) or within >= burst:
            out.append(0.0)
            continue
        envelope = 0.5 - 0.5 * math.cos(TAU * within / burst)
        voiced = (math.sin(TAU * 120.0 * i / RATE)
                  + 0.5 * math.sin(TAU * 240.0 * i / RATE)
                  + 0.25 * math.sin(TAU * 360.0 * i / RATE))
        out.append(amplitudes[slot] * envelope * voiced / 1.75)
    return out


def noise_only(n: int = SAMPLES) -> list[float]:
    rng = LCG(0x53505841)  # "SPA"
    return [0.25 * rng.uniform() for _ in range(n)]


def gain_step(n: int = SAMPLES) -> list[float]:
    base = speech_like(n)
    return [value * (0.08 if i < n // 2 else 0.60) for i, value in enumerate(base)]


def nonfinite(n: int = SAMPLES) -> list[float]:
    out = speech_like(n)
    out[5] = NAN
    out[165] = INF
    return out


GENERATORS = {
    "chirp": (chirp, "200-4000 Hz amplitude ramp; response and headroom"),
    "steps": (steps, "silence -> quiet -> loud -> quiet tone; attack/release and state"),
    "impulse": (impulse, "isolated impulse on a low tone; content delay"),
    "silence": (silence, "all-zero; floor behavior"),
    "speech_like": (speech_like, "band-limited voiced surrogate bursts; intelligibility/load control"),
    "noise_only": (noise_only, "LCG noise; non-speech control"),
    "gain_step": (gain_step, "quiet-to-loud synthetic speech; level tracking"),
    "nonfinite": (nonfinite, "NaN at 5 and +Inf at 165; fail-closed numerical control"),
}


def all_stimuli() -> dict[str, list[float]]:
    return {name: generator() for name, (generator, _) in GENERATORS.items()}


def write_fixtures(work) -> dict[str, dict]:
    """Write raw f32 fixtures to the scratch directory and describe them."""
    descriptions = {}
    for name, values in all_stimuli().items():
        raw = f32_bytes(values)
        if len(raw) % (FRAME * 4):
            raise AssertionError("stimulus not frame aligned: " + name)
        path = work / (name + ".f32")
        path.write_bytes(raw)
        descriptions[name] = {
            "generator": GENERATORS[name][0].__name__,
            "use": GENERATORS[name][1],
            "samples": len(values),
            "frames": len(values) // FRAME,
            "byte_count": len(raw),
            "input_sha256": hashlib.sha256(raw).hexdigest(),
        }
    return descriptions
