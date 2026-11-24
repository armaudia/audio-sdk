# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, fully synthetic fixtures for the WebRTC-APM-NS task evidence.

Every sample is computed from an explicit LCG and analytic harmonic speech;
no recording, corpus, WAV, model or downloaded asset is read. Digests are
frozen in ``report.json`` and checked by ``verify.py`` and the tests.
"""

from __future__ import annotations

import hashlib
import math
import struct
from typing import Dict, List, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
SAMPLES = 16000
NOISE_PREFIX_SAMPLES = 1600
GENERATOR_ID = "synthetic-lcg-harmonic-v1"
MASTER_SEED = 0x57455254434E53  # deterministic, task-local constant
_LCG_MULTIPLIER = 6364136223846793005
_LCG_INCREMENT = 1442695040888963407
_LCG_MODULUS = 1 << 64

CONDITIONS: Tuple[Dict[str, object], ...] = (
    {"item_id": "mild-snr+6", "snr_db": 6.0, "noise_seed": 0x4D494C44},
    {"item_id": "hard-snr-3", "snr_db": -3.0, "noise_seed": 0x48415244},
)
UNCALIBRATED_ITEM = "unpaired-synthetic-speech"


class LCG:
    """Minimal deterministic 64-bit linear congruential generator."""

    def __init__(self, seed: int) -> None:
        self.state = seed & (_LCG_MODULUS - 1)

    def uniform(self) -> float:
        self.state = (self.state * _LCG_MULTIPLIER + _LCG_INCREMENT) % _LCG_MODULUS
        return (self.state >> 11) * (1.0 / (1 << 53))

    def signed(self) -> float:
        return 2.0 * self.uniform() - 1.0


def digest(values: Sequence[float]) -> str:
    """SHA-256 of little-endian binary64 values, used for frozen vectors."""
    payload = struct.pack("<%dd" % len(values), *[float(value) for value in values])
    return hashlib.sha256(payload).hexdigest()


def analytic_speech(seed: int, count: int = SAMPLES) -> List[float]:
    """Silent calibration prefix followed by deterministic harmonic speech."""
    breath = LCG(seed)
    phases = [0.0] * 6
    output: List[float] = []
    for index in range(count):
        time = index / SAMPLE_RATE_HZ
        pitch = 96.0 + 17.0 * math.sin(2.0 * math.pi * 0.83 * time) + 7.0 * math.sin(2.0 * math.pi * 2.1 * time)
        syllable = max(0.0, math.sin(2.0 * math.pi * 2.4 * time - 0.4)) ** 1.6
        gate = 0.12 + 0.88 * syllable
        if time < NOISE_PREFIX_SAMPLES / SAMPLE_RATE_HZ:
            gate = 0.0
        else:
            ramp = min(1.0, (time - NOISE_PREFIX_SAMPLES / SAMPLE_RATE_HZ) / 0.02)
            gate *= ramp
        voiced = 0.0
        for harmonic in range(1, 6):
            phases[harmonic] = (phases[harmonic] + 2.0 * math.pi * harmonic * pitch / SAMPLE_RATE_HZ) % (2.0 * math.pi)
            voiced += math.sin(phases[harmonic]) / harmonic
        noise = breath.signed()
        output.append(0.30 * gate * voiced + 0.008 * gate * noise)
    return output


def shaped_noise(seed: int, count: int = SAMPLES) -> List[float]:
    """Deterministic low-pass plus hiss noise; no acoustic source is involved."""
    generator = LCG(seed)
    lowpass = 0.0
    output: List[float] = []
    for _ in range(count):
        white = generator.signed()
        lowpass = 0.94 * lowpass + 0.06 * white
        output.append(0.80 * lowpass + 0.20 * (white - lowpass))
    return output


def _rms(values: Sequence[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in values) / len(values))


def _scale_to_snr(clean: Sequence[float], noise: Sequence[float], snr_db: float) -> Tuple[List[float], float]:
    speech = clean[NOISE_PREFIX_SAMPLES:]
    speech_rms = _rms(speech)
    noise_rms = _rms(noise)
    if speech_rms <= 0.0 or noise_rms <= 0.0:
        raise ValueError("invalid_fixture_energy")
    gain = speech_rms / (noise_rms * 10.0 ** (snr_db / 20.0))
    return [float(value) + gain * float(n) for value, n in zip(clean, noise)], gain


def cohort() -> Tuple[List[Dict[str, object]], Dict[str, str]]:
    """Return the two paired synthetic conditions and their frozen digests."""
    clean_reference = analytic_speech(MASTER_SEED)
    items: List[Dict[str, object]] = []
    pinned: Dict[str, str] = {"clean": digest(clean_reference)}
    for description in CONDITIONS:
        item_id = str(description["item_id"])
        snr_db = float(description["snr_db"])
        noise_seed = int(description["noise_seed"])
        noise = shaped_noise(noise_seed)
        noisy, noise_gain = _scale_to_snr(clean_reference, noise, snr_db)
        noise_digest = digest(noise)
        noisy_digest = digest(noisy)
        pinned[item_id + ".noisy"] = noisy_digest
        pinned[item_id + ".noise"] = noise_digest
        items.append({
            "item_id": item_id,
            "snr_db": snr_db,
            "samples": SAMPLES,
            "noise_prefix_samples": NOISE_PREFIX_SAMPLES,
            "noise_seed": noise_seed,
            "noise_gain": noise_gain,
            "clean": list(clean_reference),
            "noisy": noisy,
            "noise": noise,
            "digests": {"clean": pinned["clean"], "noisy": noisy_digest, "noise": noise_digest},
        })
    return items, pinned


def unpaired() -> Dict[str, object]:
    """Synthetic speech with no clean reference; predictive screen only."""
    seed = MASTER_SEED ^ 0x55AA55
    speech = analytic_speech(seed)
    noise = shaped_noise(seed ^ 0x1234)
    noisy, gain = _scale_to_snr(speech, noise, 2.0)
    return {
        "item_id": UNCALIBRATED_ITEM,
        "samples": len(noisy),
        "noise_gain": gain,
        "noisy": noisy,
        "digest": digest(noisy),
        "has_clean_reference": False,
    }


def frame_view(values: Sequence[float]) -> List[List[float]]:
    """Split into the installed-v0 frame size without resampling or padding."""
    if len(values) % FRAME_SAMPLES:
        raise ValueError("partial_frame")
    return [list(values[start:start + FRAME_SAMPLES]) for start in range(0, len(values), FRAME_SAMPLES)]
