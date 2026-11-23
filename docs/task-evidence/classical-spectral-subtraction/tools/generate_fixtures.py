#!/usr/bin/env python3
"""Deterministic synthetic fixtures for the CSS task-local reference.

No recorded speech, downloaded asset or model is used. The generator emits
16 kHz mono float32 little-endian raw files. Run with --check to verify the
pinned fixtures without rewriting them.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
import struct

RATE = 16000
SECONDS = 3
LENGTH = RATE * SECONDS
PROFILE_LENGTH = 4096
PAIRS = (("a", 0x43535301, 118.0, 5.0),
         ("b", 0x43535302, 146.0, 5.0),
         ("c", 0x43535303, 172.0, 3.0))
TASK_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = TASK_ROOT / "fixtures"
MANIFEST = FIXTURE_DIR / "FIXTURES.sha256"


class Rng:
    """Explicit 32-bit LCG; no dependence on the host PRNG implementation."""

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
        for harmonic in range(1, 13):
            value += math.sin(phase * harmonic) / harmonic
        value *= 0.30 * envelope
        value += 0.004 * rng.uniform()
        output.append(value)
        phase += 2.0 * math.pi * f0 / RATE
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi
    return output


def rms(samples: list[float]) -> float:
    return math.sqrt(sum(value * value for value in samples) / len(samples))


def write_f32(path: Path, samples: list[float]) -> None:
    path.write_bytes(b"".join(struct.pack("<f", value) for value in samples))


def build() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    profile = pink_noise(Rng(0x50524F46), PROFILE_LENGTH)
    files["noise_profile.f32"] = struct.pack("<%df" % PROFILE_LENGTH, *profile)

    for name, seed, f0, snr_db in PAIRS:
        clean = synthetic_speech(LENGTH, seed, f0)
        noise = pink_noise(Rng(seed ^ 0x4E4F4953), LENGTH)
        scale = rms(clean) / rms(noise) * 10.0 ** (-snr_db / 20.0)
        noisy = [clean[i] + scale * noise[i] for i in range(LENGTH)]
        files[f"clean_{name}.f32"] = struct.pack("<%df" % LENGTH, *clean)
        files[f"noisy_{name}.f32"] = struct.pack("<%df" % LENGTH, *noisy)
    return files


def digest_map(files: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify pinned bytes")
    args = parser.parse_args()
    files = build()
    digests = digest_map(files)
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
        write_f32(FIXTURE_DIR / name, struct.unpack("<%df" % (len(data) // 4), data))
    MANIFEST.write_text(
        "".join(f"{digests[name]}  {name}\n" for name in sorted(digests)),
        encoding="utf-8")
    print(f"wrote {len(files)} synthetic fixtures and {MANIFEST.name}")


if __name__ == "__main__":
    main()
