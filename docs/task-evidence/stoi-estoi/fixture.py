# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, asset-free synthetic cohort for the STOI/ESTOI screen.

No recording, corpus, model, device or network input is read.  Every sample is
generated from the pinned constants and seed below.  The same target and the
same masker realization are reused across every variant of an item so that all
comparisons are paired.  This is synthetic developer evidence, not an
intelligibility or listening result.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import math
from typing import Dict, List, Sequence, Tuple

import scorer

RATE_HZ = 16000
SAMPLES = 9600
SEED = 20261124
MASKER_KINDS = ("steady", "modulated")
SNR_DB = (-5, 0, 5)
VARIANTS = ("identity_noisy", "less_masker", "more_masker", "tilt",
            "gain_only", "missing", "nonfinite", "short")
TILT_GAINS = (0.85, 0.90, 1.00, 1.10, 1.20, 1.30)
GAIN_ONLY_FACTOR = 0.90
FIXTURE_ID = "stoi-estoi-synthetic-target-masker-v1"


def digest(values: Sequence[float]) -> str:
    """SHA-256 of IEEE-754 little-endian binary64 samples (no text encoding)."""
    import struct
    return hashlib.sha256(b"".join(struct.pack("<d", float(value)) for value in values)).hexdigest()


def rms(values: Sequence[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in values) / len(values))


def peak(values: Sequence[float]) -> float:
    return max(abs(value) for value in values)


@lru_cache(maxsize=1)
def target() -> List[float]:
    """Deterministic vowel-like harmonic source; no speech recording is used."""
    harmonics = []
    for index in range(1, 25):
        frequency = 110.0 * index
        amplitude = (
            math.exp(-0.5 * ((frequency - 700.0) / 180.0) ** 2)
            + 0.7 * math.exp(-0.5 * ((frequency - 1200.0) / 220.0) ** 2)
            + 0.4 * math.exp(-0.5 * ((frequency - 2600.0) / 300.0) ** 2)
        )
        harmonics.append((frequency, amplitude, index * 0.37))
    random = _lcg(SEED + 1)
    broadband = [next(random) * 2.0 - 1.0 for _ in range(SAMPLES)]
    values = []
    for sample in range(SAMPLES):
        time = sample / RATE_HZ
        envelope = 0.8 + 0.2 * math.sin(2.0 * math.pi * 3.0 * time)
        total = math.fsum(
            amplitude * math.sin(2.0 * math.pi * frequency * time + phase)
            for frequency, amplitude, phase in harmonics
        )
        # A small deterministic broadband component keeps every 1/3-octave band
        # active so the pinned extended-normalization dither is immaterial.
        values.append(envelope * (total + 0.18 * broadband[sample]))
    scale = 0.5 / peak(values)
    return [value * scale for value in values]


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 0x100000000


@lru_cache(maxsize=2)
def masker(kind: str) -> List[float]:
    """One pinned low-pass noise realization, either steady or 4 Hz modulated."""
    if kind not in MASKER_KINDS:
        raise ValueError("unknown_masker_kind")
    random = _lcg(SEED)
    filtered = 0.0
    values: List[float] = []
    for sample in range(SAMPLES):
        filtered += 0.7 * (next(random) * 2.0 - 1.0 - filtered)
        gate = 1.0 if kind == "steady" else (1.0 if (sample // 2000) % 2 == 0 else 0.05)
        values.append(gate * filtered)
    level = rms(values)
    return [value / level for value in values]


def fixed_tilt(values: Sequence[float]) -> List[float]:
    """Irreversible six-band high-frequency tilt with target-RMS restoration."""
    size = 16384  # radix-2, >= SAMPLES
    spectrum = scorer._fft([complex(value, 0.0) for value in values] + [0j] * (size - len(values)))
    bin_size = (size // 2) // len(TILT_GAINS)
    gains: List[float] = []
    for index in range(size // 2 + 1):
        band = min(index // max(bin_size, 1), len(TILT_GAINS) - 1)
        gains.append(TILT_GAINS[band])
    shaped = scorer._fft(
        [spectrum[index] * gains[index if index < size // 2 else size - index]
         for index in range(size)],
        inverse=True,
    )
    result = [value.real for value in shaped[:len(values)]]
    factor = rms(values) / rms(result)
    return [value * factor for value in result]


def mix(clean: Sequence[float], noise: Sequence[float], snr_db: float,
        noise_multiplier: float = 1.0) -> List[float]:
    if len(clean) != len(noise):
        raise ValueError("length_mismatch")
    scale = rms(clean) / (rms(noise) * 10.0 ** (snr_db / 20.0))
    return [value + noise_multiplier * scale * item for value, item in zip(clean, noise)]


def item(kind: str, snr_db: float, clean: Sequence[float],
         noise: Sequence[float]) -> Dict[str, object]:
    """One matched item: identical clean target and masker across all variants."""
    if len(clean) != SAMPLES or len(noise) != SAMPLES:
        raise ValueError("invalid_cohort_geometry")
    tilted = fixed_tilt(clean)
    scale = rms(clean) / (rms(noise) * 10.0 ** (snr_db / 20.0))
    scaled_noise = [scale * value for value in noise]
    scored = mix(clean, noise, snr_db)
    invalid = list(scored)
    invalid[SAMPLES // 2] = float("nan")
    variants = {
        "identity_noisy": scored,
        "less_masker": mix(clean, noise, snr_db, 0.5),
        "more_masker": mix(clean, noise, snr_db, 1.5),
        "tilt": [value + added for value, added in zip(tilted, scaled_noise)],
        "gain_only": [GAIN_ONLY_FACTOR * value + added for value, added in zip(clean, scaled_noise)],
        "missing": None,
        "nonfinite": invalid,
        "short": scored[:-1],
    }
    return {
        "item_id": f"{kind}-snr{snr_db:+d}",
        "masker_kind": kind,
        "snr_db": snr_db,
        "clean_digest": digest(clean),
        "masker_digest": digest(noise),
        "clean_rms": rms(clean),
        "masker_rms": rms(noise),
        "mixture_rms": rms(scored),
        "mixture_peak": peak(scored),
        "variants": {
            name: None if samples is None else {
                "digest": digest(samples),
                "samples": len(samples),
                "values": samples,
            }
            for name, samples in variants.items()
        },
    }


@lru_cache(maxsize=1)
def cohort() -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    """Six paired items and the single shared synthetic clean target."""
    clean = target()
    noises = {kind: masker(kind) for kind in MASKER_KINDS}
    items = [item(kind, snr, clean, noises[kind]) for kind in MASKER_KINDS for snr in SNR_DB]
    pinned = {
        "fixture_id": FIXTURE_ID,
        "sample_rate_hz": RATE_HZ,
        "samples_per_item": SAMPLES,
        "seed": SEED,
        "masker_kinds": list(MASKER_KINDS),
        "snr_db": list(SNR_DB),
        "variants": list(VARIANTS),
        "tilt_gains": list(TILT_GAINS),
        "gain_only_factor": GAIN_ONLY_FACTOR,
        "clean_digest": digest(clean),
        "masker_digests": {kind: digest(values) for kind, values in noises.items()},
    }
    return items, pinned
