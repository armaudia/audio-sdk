# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, synthetic-only stimuli for the SpeexDSP VAD reference.

No corpus, model, weights, download, licensed runtime, device or listening
result is used. Every sample comes from a version-stable integer LCG and
analytic tones. The historical adapter uses 320-sample frames at 16 kHz; the
frozen SDK v0 format is 160 samples per call and is not changed here. The
frame-size divergence is recorded, not papered over.
"""
from __future__ import annotations

import hashlib
import math
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TASK_ID = "SDK-SPEEXDSP-VAD"
CONTRACT_ID = "audio-sdk/speexdsp-vad/0.1"
BASE_COMMIT = "941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
ADAPTER_FRAME_SAMPLES = 320
NS_PER_SAMPLE = 62500
AVAILABILITY_OFFSET_NS = 5_000_000
CLOCK_ID = "monotonic-reference-v0"
PRODUCER_ID = "detection.speexdsp-vad.reference"
TAP_ID = "capture"

# Declared by the historical public adapter. Its own run.py emits raw binary
# SpeexDSP labels and does not consume these two fields; this task-local model
# uses them as explicit onset/continue thresholds and records that divergence.
PROBABILITY_START = 0.35
PROBABILITY_CONTINUE = 0.20
ONSET_FRAMES = 2
OFFSET_FRAMES = 3
MAX_ABS_SAMPLE = 4.0

LCG_SEED = 0x5EED5A17
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345
LCG_MODULUS = 1 << 31

AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

# Paths are relative to the workspace root above. Digests are exact SHA-256;
# no tolerance, substitution or pooling with historical results is used.
SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/plans/F02/vad_accuracy_contract.md":
        "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "adapters/speexdsp-vad/adapter.json":
        "ded307574ef9531e4e9232fec82f55e013daf19c931f62dfda07e1e3b070fcc9",
    "adapters/speexdsp-vad/run.py":
        "c211f51e9952c52ea634e8c24ea421c17cabf40e32dbe91b6f56c2a4fedc21c1",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "audio-benchmark-platform/audio-sdk/third_party/speexdsp/UPSTREAM.md":
        "3fc7e105de52b75abc65bae310de9066faabbdb7e13a17c3c9dd42f9f1f7bf1d",
    "audio-benchmark-platform/audio-sdk/deps/speexdsp-files.sha256":
        "3ff2b43a21b28a10a87f5a30b3c0339bef67a6b491c22f0f90c45696bd8f7a29",
    "audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c":
        "d1a98e3aff897375db4f0fc7668329be5254faa361ccaba1635a5089ea8a71e6",
}

PIN_NOTES: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "VAD row 7: source-reported held-out AMI FN 2.45% / FP 77.03%; not rerun or reused as a local score.",
    "research/plans/F02/vad_accuracy_contract.md":
        "Decision intervals, scored/unknown regions, denominators and stale/invalid handling.",
    "adapters/speexdsp-vad/adapter.json":
        "Public adapter identity, 320-sample frame, 16 kHz and declared probability thresholds.",
    "adapters/speexdsp-vad/run.py":
        "Public adapter drives native int16 SpeexDSP preprocess VAD with enhancement disabled; emits binary labels.",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "Component inventory and chained-policy context; no result from it is claimed here.",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "Analysis acceptance profile: probabilities, boundaries, detections, validity and availability controls.",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "Frozen v0 provider/session contract, epochs, source intervals and read-only PCM boundary.",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "Public provider table boundary; unchanged.",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "Public session lifecycle and source coordinates; unchanged.",
    "audio-benchmark-platform/audio-sdk/third_party/speexdsp/UPSTREAM.md":
        "Vendored Xiph SpeexDSP revision 7a158783, BSD-3-Clause-style notices; VAD is not enabled in installed v0.",
    "audio-benchmark-platform/audio-sdk/deps/speexdsp-files.sha256":
        "Exact vendored SpeexDSP source file digests; no source substitution.",
    "audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c":
        "Installed speex.ns.v0 computes VAD but does not export it; this task does not change that behavior.",
}


@dataclass(frozen=True)
class Segment:
    name: str
    start_frame: int
    end_frame: int
    label: str
    rms: float
    validity: str


SEGMENTS: tuple[Segment, ...] = (
    Segment("idle-a", 0, 60, "nonspeech", 0.02, "known"),
    Segment("quiet-a", 60, 120, "speech", 0.26, "known"),
    Segment("idle-b", 120, 150, "nonspeech", 0.02, "known"),
    Segment("active-a", 150, 210, "speech", 0.55, "known"),
    Segment("noise-burst", 210, 240, "nonspeech", 0.40, "known"),
    Segment("quiet-b", 240, 270, "speech", 0.15, "known"),
    Segment("idle-c", 270, 300, "nonspeech", 0.02, "known"),
    Segment("unknown-tail", 300, 330, "unknown", 0.02, "unknown"),
)
TOTAL_FRAMES = SEGMENTS[-1].end_frame
SCORED_END_FRAME = 300
SCORED_END_SAMPLE = SCORED_END_FRAME * SDK_FRAME_SAMPLES
TOTAL_SAMPLES = TOTAL_FRAMES * SDK_FRAME_SAMPLES


class LCG:
    """Version-stable 32-bit LCG; independent of Python's random internals."""

    def __init__(self, seed: int = LCG_SEED) -> None:
        self.state = seed & (LCG_MODULUS - 1)

    def uniform(self) -> float:
        self.state = (LCG_MULTIPLIER * self.state + LCG_INCREMENT) % LCG_MODULUS
        return (self.state / (LCG_MODULUS - 1.0)) * 2.0 - 1.0


def segment_for_frame(index: int) -> Segment:
    for segment in SEGMENTS:
        if segment.start_frame <= index < segment.end_frame:
            return segment
    raise ValueError(f"frame {index} is outside the fixture")


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_f32(samples: Iterable[float]) -> str:
    return sha256_bytes(b"".join(struct.pack("<f", float(value)) for value in samples))


def build_frames() -> tuple[list[tuple[float, ...]], str]:
    """Return 330 deterministic 160-sample frames and their f32 stream digest."""
    noise = LCG()
    frames: list[tuple[float, ...]] = []
    for index in range(TOTAL_FRAMES):
        segment = segment_for_frame(index)
        values: list[float] = []
        for offset in range(SDK_FRAME_SAMPLES):
            sample_index = index * SDK_FRAME_SAMPLES + offset
            if segment.label == "speech":
                phase = 2.0 * math.pi / SAMPLE_RATE_HZ
                value = (0.62 * math.sin(phase * 130.0 * sample_index)
                         + 0.27 * math.sin(phase * 263.0 * sample_index)
                         + 0.11 * math.sin(phase * 401.0 * sample_index))
            else:
                value = noise.uniform()
            values.append(value)
        power = sum(value * value for value in values) / SDK_FRAME_SAMPLES
        scale = segment.rms / math.sqrt(power)
        frames.append(tuple(f32(value * scale) for value in values))
    flat = [sample for frame in frames for sample in frame]
    return frames, sha256_f32(flat)


def verify_pins() -> dict[str, str]:
    """Fail closed when any exact pinned source is missing or changed."""
    observed: dict[str, str] = {}
    for relative, expected in SOURCE_PINS.items():
        path = AUDIOML_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("required pinned source missing: " + relative)
        digest = sha256_bytes(path.read_bytes())
        if digest != expected:
            raise ValueError("pinned source digest mismatch: " + relative)
        observed[relative] = digest
    return observed
