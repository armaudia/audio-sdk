#!/usr/bin/env python3
"""Deterministic synthetic DSP fixtures for the six-band tilt task.

No recorded speech, downloaded asset, model or listening data is used. Every
file is 16 kHz mono float32 little-endian raw samples. Run with --check to
verify the pinned fixture bytes without rewriting them.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
import struct

RATE = 16000
LONG = RATE * 3
SHORT = 4800
LEVELS = 9600
SMALL = 1600
TASK_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = TASK_ROOT / "fixtures"
MANIFEST = FIXTURE_DIR / "FIXTURES.sha256"

ANCHOR_HZ = 750.0  # band index 2 (500-1000 Hz), the 0 dB reference band
PROBES = (
    (0, 125.0), (0, 200.0),
    (1, 320.0), (1, 450.0),
    (2, 550.0), (2, 950.0),
    (3, 1100.0),
    (4, 2500.0), (4, 3500.0),
    (5, 4800.0), (5, 7000.0),
)
CLEAN = (("a", 0x5348541A, 118.0),
         ("b", 0x5348542B, 146.0),
         ("c", 0x5348543C, 172.0))


class Rng:
    """Explicit 32-bit LCG; independent of the host PRNG implementation."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def uniform(self) -> float:
        return self.next_u32() / 4294967296.0 * 2.0 - 1.0


def pink_noise(rng: Rng, count: int) -> list[float]:
    b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
    output = []
    for _ in range(count):
        white = rng.uniform()
        b0 = 0.99886 * b0 + white * 0.0555179
        b1 = 0.99332 * b1 + white * 0.0750759
        b2 = 0.96900 * b2 + white * 0.1538520
        b3 = 0.86650 * b3 + white * 0.3104856
        b4 = 0.55000 * b4 + white * 0.5329522
        b5 = -0.7616 * b5 - white * 0.0168980
        value = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11
        b6 = white * 0.115926
        output.append(value)
    return output


def synthetic_speech(count: int, seed: int, f0_base: float) -> list[float]:
    rng = Rng(seed)
    phase = 0.0
    output = []
    for i in range(count):
        t = i / RATE
        f0 = f0_base * (1.0 + 0.08 * math.sin(2.0 * math.pi * 0.7 * t))
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 1.7 * t + 0.4)
        envelope *= 0.7 + 0.3 * math.sin(2.0 * math.pi * 0.23 * t)
        if (t % 2.0) > 1.72:
            envelope *= 0.12
        value = 0.0
        for harmonic in range(1, 17):
            value += math.sin(phase * harmonic) / (harmonic ** 0.85)
        value *= 0.24 * envelope
        value += 0.006 * rng.uniform()
        output.append(value)
        phase += 2.0 * math.pi * f0 / RATE
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi
    return output


def receiver_masker(count: int, seed: int) -> list[float]:
    """Deterministic ambient-like masker: pink noise plus two babble voices."""
    rng = Rng(seed)
    noise = pink_noise(rng, count)
    output = []
    for i in range(count):
        t = i / RATE
        modulation = 0.75 + 0.25 * math.sin(2.0 * math.pi * 0.31 * t + 0.7)
        voice = 0.0
        for voice_index, (f0, rate) in enumerate(((112.0, 2.3), (137.0, 1.9))):
            envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * rate * t +
                                            voice_index * 1.3)
            for h in range(1, 9):
                voice += 0.10 * envelope * math.sin(
                    2.0 * math.pi * f0 * h * t + h * 0.41 + voice_index)
        output.append(modulation * noise[i] + 0.08 * voice)
    return output


def two_tone(probe_hz: float) -> list[float]:
    """Probe sine plus a fixed 0 dB-band anchor, with fade edges."""
    output = []
    fade = 320
    for i in range(SHORT):
        window = 1.0
        if i < fade:
            window = 0.5 - 0.5 * math.cos(math.pi * i / fade)
        elif i >= SHORT - fade:
            window = 0.5 - 0.5 * math.cos(math.pi * (SHORT - 1 - i) / fade)
        t = i / RATE
        output.append(window * 0.09 * (
            math.sin(2.0 * math.pi * probe_hz * t) +
            math.sin(2.0 * math.pi * ANCHOR_HZ * t + 0.3)))
    return output


def impulse() -> list[float]:
    output = [0.0] * SHORT
    output[800] = 0.8
    return output


def step() -> list[float]:
    output = [0.0] * SHORT
    for i in range(800, 2400):
        output[i] = 0.25
    return output


def level_steps() -> list[float]:
    source = pink_noise(Rng(0x4C45564C), LEVELS)
    amplitudes = (0.02, 0.05, 0.10, 0.20, 0.40, 0.20, 0.10, 0.05)
    segment = LEVELS // len(amplitudes)
    output = []
    for index, value in enumerate(source):
        amplitude = amplitudes[min(index // segment, len(amplitudes) - 1)]
        output.append(amplitude * value / 0.11)
    return output


def peak(samples: list[float]) -> float:
    return max(abs(value) for value in samples)


def scale_to(values: list[float], target_peak: float) -> list[float]:
    factor = target_peak / peak(values)
    return [factor * value for value in values]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def build() -> dict[str, bytes]:
    files: dict[str, list[float]] = {}
    for band, hz in PROBES:
        files[f"sweep_b{band + 1}_{int(hz)}.f32"] = two_tone(hz)
    files["impulse.f32"] = impulse()
    files["step.f32"] = step()
    files["silence.f32"] = [0.0] * SMALL
    tiny_rng = Rng(0x54494E59)
    files["tiny.f32"] = [(1e-38 if tiny_rng.uniform() > 0.0 else -1e-38)
                         for _ in range(SMALL)]
    files["level_steps.f32"] = level_steps()

    clean_signals = {}
    for name, seed, f0 in CLEAN:
        signal = synthetic_speech(LONG, seed, f0)
        clean_signals[name] = signal
        files[f"clean_{name}.f32"] = signal
    files["masker_receiver.f32"] = receiver_masker(LONG, 0x4D41534B)
    files["near_clip.f32"] = scale_to(clean_signals["a"], 0.985)
    files["clipped.f32"] = [max(-0.28, min(0.28, value))
                            for value in clean_signals["b"]]

    # Confirm a deterministic, nondegenerate setup before any file is written.
    assert 0.0 < rms(clean_signals["a"]) < 1.0
    assert 0.0 < rms(files["masker_receiver.f32"]) < 1.0
    assert peak(files["near_clip.f32"]) <= 0.9850001
    return {name: struct.pack("<%df" % len(samples), *samples)
            for name, samples in sorted(files.items())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify pinned bytes")
    args = parser.parse_args()
    files = build()
    digests = {name: hashlib.sha256(data).hexdigest()
               for name, data in files.items()}
    if args.check:
        expected = {}
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            value, name = line.split("  ", 1)
            expected[name] = value
        if expected != digests:
            raise SystemExit("fixture digest mismatch")
        for name, data in files.items():
            if (FIXTURE_DIR / name).read_bytes() != data:
                raise SystemExit(f"fixture bytes differ: {name}")
        print(f"verified {len(files)} synthetic fixtures")
        return
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (FIXTURE_DIR / name).write_bytes(data)
    MANIFEST.write_text(
        "".join(f"{digests[name]}  {name}\n" for name in sorted(digests)),
        encoding="utf-8")
    print(f"wrote {len(files)} synthetic fixtures and {MANIFEST.name}")


if __name__ == "__main__":
    main()
