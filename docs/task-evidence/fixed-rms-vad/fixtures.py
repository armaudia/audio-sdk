"""Deterministic synthetic stimulus generator for the fixed-RMS VAD fixture.

Everything is generated in memory from integer arithmetic and analytic tones.
No WAV file, corpus, checkpoint, download or licensed runtime is involved.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import reference

CONTRACT_ID = reference.CONTRACT_ID
FIXTURE_SCHEMA = "sdk.fixed-rms-vad.fixtures.v1"
STREAM_SAMPLES = 16000
NOISE_MODULUS = 0x7FFFFFFF

# Half-open source intervals. Speech labels are the ground truth for scoring;
# loud idle noise is an explicit known negative with a deliberate alarm risk.
SEGMENTS: tuple[dict[str, Any], ...] = (
    {"id": "idle_quiet_0", "kind": "idle_noise", "speech": False,
     "start": 0, "end": 320, "amplitude": 0.004, "seed": 1001},
    {"id": "quiet_speech", "kind": "quiet_speech", "speech": True,
     "start": 320, "end": 1120, "amplitude": 0.030, "f0_hz": 140, "seed": 1002},
    {"id": "idle_between", "kind": "silence", "speech": False,
     "start": 1120, "end": 1920, "amplitude": 0.0, "seed": 1003},
    {"id": "active_speech", "kind": "active_speech", "speech": True,
     "start": 1920, "end": 3040, "amplitude": 0.300, "f0_hz": 150, "seed": 1004},
    {"id": "idle_loud", "kind": "idle_noise", "speech": False,
     "start": 3040, "end": 3520, "amplitude": 0.180, "seed": 1005},
    {"id": "threshold_speech", "kind": "quiet_speech", "speech": True,
     "start": 3520, "end": 4320, "amplitude": 0.0125, "f0_hz": 145, "seed": 1006},
    {"id": "idle_tail", "kind": "silence", "speech": False,
     "start": 4320, "end": 16000, "amplitude": 0.0, "seed": 1007},
)

SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/rms-energy-vad/adapter.json":
        "b4801bbce2a9278940d107e43d696c5e0b5c0ee23f84967a5479be3c5767fc9e",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}


def _noise(seed: int, count: int, amplitude: float) -> list[float]:
    state = int(seed) & 0x7FFFFFFF
    values: list[float] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(reference.f32((2.0 * state / NOISE_MODULUS - 1.0) * amplitude))
    return values


def _speech(seed: int, start: int, end: int, amplitude: float,
            f0_hz: float) -> list[float]:
    """Harmonic voiced burst with a raised-cosine envelope; seed fixes phase."""
    count = end - start
    if count < 2:
        return [0.0] * count
    state = int(seed) & 0x7FFFFFFF
    state = (1103515245 * state + 12345) & 0x7FFFFFFF
    phase_offset = (state / NOISE_MODULUS) * 2.0 * math.pi
    weights = (1.0, 0.5, 0.25, 0.125)
    values: list[float] = []
    for index in range(count):
        envelope = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / (count - 1))
        voiced = 0.0
        for harmonic, weight in enumerate(weights, start=1):
            voiced += weight * math.sin(
                harmonic * 2.0 * math.pi * f0_hz * index / reference.SAMPLE_RATE_HZ
                + phase_offset / harmonic
            )
        values.append(reference.f32(amplitude * envelope * voiced / sum(weights)))
    return values


def build_samples(seed_shift: int = 0, amplitude_scale: float = 1.0) -> list[float]:
    """Return the frozen float32 stream; segments cover every sample exactly once."""
    values = [0.0] * STREAM_SAMPLES
    cursor = 0
    for segment in SEGMENTS:
        start, end = int(segment["start"]), int(segment["end"])
        if start != cursor or end <= start or end > STREAM_SAMPLES:
            raise ValueError("segment_layout_invalid")
        if segment["kind"] == "silence":
            generated = [0.0] * (end - start)
        elif segment["kind"] == "idle_noise":
            generated = _noise(int(segment["seed"]) + seed_shift, end - start,
                               float(segment["amplitude"]) * amplitude_scale)
        else:
            generated = _speech(int(segment["seed"]) + seed_shift, start, end,
                                float(segment["amplitude"]) * amplitude_scale,
                                float(segment["f0_hz"]))
        values[start:end] = generated
        cursor = end
    if cursor != STREAM_SAMPLES:
        raise ValueError("segment_layout_incomplete")
    return [reference.f32(value) for value in values]


def seed_spec() -> dict[str, Any]:
    """Canonical fixture identity, independent of mutable board state."""
    return {
        "schema": FIXTURE_SCHEMA,
        "contract": CONTRACT_ID,
        "geometry": {
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": reference.CHANNELS,
            "sample_format": "f32",
            "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
            "adapter_frame_samples": reference.ADAPTER_FRAME_SAMPLES,
        },
        "config": dict(reference.DEFAULT_CONFIG),
        "stream_samples": STREAM_SAMPLES,
        "stream_sha256": reference.digest_samples(build_samples()),
        "segments": [dict(segment) for segment in SEGMENTS],
        "source_pins": dict(SOURCE_PINS),
        "availability_origin_ns": reference.AVAILABILITY_ORIGIN_NS,
        "clock_id": reference.CLOCK_ID,
    }


def feed_stream(session: reference.Session, samples: Sequence[float]) -> dict[str, Any]:
    """Feed the stream through one 160-sample frame call per SDK frame."""
    if len(samples) != STREAM_SAMPLES:
        raise ValueError("stream_length_mismatch")
    rejections = 0
    for offset in range(0, STREAM_SAMPLES, reference.SDK_FRAME_SAMPLES):
        frame = samples[offset:offset + reference.SDK_FRAME_SAMPLES]
        result = session.process_frame(
            frame,
            epoch=session.epoch,
            first_input_sample=session.first_sample + offset,
        )
        if result["status"] != "ok":
            rejections += 1
    drain = session.drain()
    return {"drain": drain, "unexpected_rejections": rejections,
            "frame_count": STREAM_SAMPLES // reference.SDK_FRAME_SAMPLES}
