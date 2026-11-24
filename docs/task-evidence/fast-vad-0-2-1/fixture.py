# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, fully synthetic VAD analysis fixture (no real speech or runtime).

Every value is produced from integer arithmetic and a fixed 64-entry waveform
table.  The frozen stream is 16 kHz mono f32 with 160-sample SDK frames.  The
truth table partitions the stream into known speech, known nonspeech and one
explicit unknown span; no real recording, wheel, model or licensed runtime is
used anywhere in this package.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

TASK_DIR = Path(__file__).resolve().parent

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
SAMPLE_NS = 62500
TOTAL_SAMPLES = 16000
TOTAL_FRAMES = TOTAL_SAMPLES // FRAME_SAMPLES
ORIGIN_NS = 1700000000000000000
PROCESSING_DELAY_NS = 5000000
CLOCK = "fast-vad-0-2-1-fixture-monotonic-v0"

# Source pins are content-addressed at task authoring time.  A missing or
# changed pin is a hard failure, never a skip or a substituted oracle.
SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "reports/vad-research/chaining-evaluation.md":
        "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "adapters/fast-vad/adapter.json":
        "003d2f568bf27e590b03a083c8ccf4251b0b40933cdd5c2aa116123366350ee8",
    "adapters/fast-vad/README.md":
        "18f3386925e241f00e6e1a7c07f400073918192ae724f09b80fb07d6da5e0d30",
    "adapters/fast-vad/requirements.lock":
        "3a0b7c528e8d044aa116081daf890f67542bf0b5461fd4c6b0ed442f487b2d95",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/fast-vad/run.py":
        "779e628c79b71ea9dee2c881a07739c914b4534de1bcc9dd463a318d81f64140",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# The mutable board is provenance only; it is printed as a snapshot and never
# used as a gate or as a qualification source.
MUTABLE_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_BOARD_SHA256_AT_READ = (
    "275f2d6550eb3f7357d41f8749d92489ebb8601e9f9c5f025d67898fa577e106"
)

CONFIG: dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "decision_threshold": 0.5,
    "hangover_frames": 1,
    "probability_gain": 3.45,
    "probability_offset": 5.35,
    "probability_zcr_weight": 3.0,
    "clock": CLOCK,
    "origin_ns": ORIGIN_NS,
    "sample_period_ns": SAMPLE_NS,
    "processing_delay_ns": PROCESSING_DELAY_NS,
    "source_time_mapping": "identity",
    "declared_analysis_delay_samples": 0,
    "real_runtime": False,
    "wheel_or_licensed_runtime_used": False,
}

# Fixed truth intervals: half-open sample coordinates on the exact source
# clock.  "known" samples are scored; "unknown" samples are excluded from every
# denominator.  Invalid samples are represented only by adverse controls.
SEGMENTS: tuple[dict[str, Any], ...] = (
    {"id": "idle-a", "start": 0, "end": 960, "truth": "nonspeech", "condition": "idle",
     "tone_amplitude": 0, "noise_amplitude": 90},
    {"id": "quiet-a", "start": 960, "end": 2560, "truth": "speech", "condition": "quiet_speech",
     "tone_amplitude": 650, "tone_amplitude_end": 1500, "noise_amplitude": 55},
    {"id": "idle-b", "start": 2560, "end": 3520, "truth": "nonspeech", "condition": "idle",
     "tone_amplitude": 0, "noise_amplitude": 120},
    {"id": "active-a", "start": 3520, "end": 6080, "truth": "speech", "condition": "active_speech",
     "tone_amplitude": 19000, "noise_amplitude": 115},
    {"id": "noise-burst", "start": 6080, "end": 7040, "truth": "nonspeech", "condition": "idle_noise",
     "tone_amplitude": 0, "noise_amplitude": 2600, "noise_amplitude_end": 12500},
    {"id": "quiet-b", "start": 7040, "end": 7840, "truth": "speech", "condition": "quiet_speech",
     "tone_amplitude": 470, "noise_amplitude": 55},
    {"id": "idle-c", "start": 7840, "end": 8640, "truth": "nonspeech", "condition": "idle",
     "tone_amplitude": 0, "noise_amplitude": 90},
    {"id": "unknown-tail", "start": 8640, "end": 9920, "truth": "unknown", "condition": "unknown",
     "tone_amplitude": 950, "noise_amplitude": 210},
    {"id": "idle-d", "start": 9920, "end": 16000, "truth": "nonspeech", "condition": "idle",
     "tone_amplitude": 0, "noise_amplitude": 75},
)

_WAVE: tuple[int, ...] = tuple(
    int(round(32767.0 * math.sin(2.0 * math.pi * k / 64.0))) for k in range(64)
)


def workspace_root() -> Path:
    """Locate the pinned workspace without relying on the process CWD."""
    for parent in TASK_DIR.parents:
        if ((parent / "research" / "voice-enhancement-20261101" / "candidate_matrix.csv").is_file()
                and (parent / "audio-benchmark-platform" / "plan" / "swarm"
                     / "VERIFICATION.md").is_file()):
            return parent
    raise FileNotFoundError("workspace root with pinned sources not found")


def resolve_pin_path(name: str) -> Path:
    return workspace_root() / name


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)
    return (text + "\n").encode("utf-8")


def validate_config(config: dict[str, Any]) -> None:
    if set(config) != set(CONFIG):
        raise ValueError("config_key_set_mismatch")
    for key in ("sample_rate_hz", "channels", "sample_format", "frame_samples",
                "decision_threshold", "hangover_frames", "probability_gain",
                "probability_offset", "probability_zcr_weight", "clock", "origin_ns",
                "sample_period_ns", "processing_delay_ns", "source_time_mapping",
                "declared_analysis_delay_samples", "real_runtime",
                "wheel_or_licensed_runtime_used"):
        if config[key] != CONFIG[key]:
            raise ValueError("config_mismatch:" + key)


def segment_for_sample(index: int) -> dict[str, Any]:
    if not 0 <= index < TOTAL_SAMPLES:
        raise ValueError("sample_out_of_range")
    for segment in SEGMENTS:
        if segment["start"] <= index < segment["end"]:
            return segment
    raise AssertionError("segment_table_has_a_gap")


def segment_for_frame(index: int) -> dict[str, Any]:
    if not 0 <= index < TOTAL_FRAMES:
        raise ValueError("frame_out_of_range")
    return segment_for_sample(index * FRAME_SAMPLES)


def build_pcm_int() -> list[int]:
    """Return the frozen quantized stream; all arithmetic is integer-only."""
    out: list[int] = []
    noise_state = 0x13579BDF
    phase_acc = 0
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        noise_state = (1103515245 * noise_state + 12345) & 0x7FFFFFFF
        noise = (noise_state >> 16) - 16384
        phase_acc += 112 * 64
        table_index = (phase_acc // SAMPLE_RATE_HZ) % 64
        tone = _WAVE[table_index] + _WAVE[(table_index * 2) % 64] // 2
        fraction = (index - segment["start"]) / (segment["end"] - segment["start"])
        tone_amplitude = segment["tone_amplitude"] + round(
            fraction * (segment.get("tone_amplitude_end", segment["tone_amplitude"])
                        - segment["tone_amplitude"]))
        noise_amplitude = segment["noise_amplitude"] + round(
            fraction * (segment.get("noise_amplitude_end", segment["noise_amplitude"])
                        - segment["noise_amplitude"]))
        sample = (tone_amplitude * tone + noise_amplitude * noise) >> 15
        out.append(max(-32768, min(32767, sample)))
    return out


def build_pcm() -> list[float]:
    return [value / 32768.0 for value in build_pcm_int()]


def build_frames() -> list[list[float]]:
    pcm = build_pcm()
    return [pcm[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
            for index in range(TOTAL_FRAMES)]


def frame_features(frame: list[float]) -> dict[str, float]:
    if len(frame) == 0:
        raise ValueError("empty_frame")
    if any(not math.isfinite(value) for value in frame):
        raise ValueError("nonfinite_frame")
    energy = sum(value * value for value in frame) / len(frame)
    rms = math.sqrt(energy)
    zcr = sum(1 for left, right in zip(frame, frame[1:])
              if (left < 0.0) != (right < 0.0)) / (len(frame) - 1)
    return {"rms": rms, "zcr": zcr}


def probability_for_features(features: dict[str, float]) -> float:
    rms = features["rms"]
    zcr = features["zcr"]
    score = (CONFIG["probability_gain"] * math.log10(rms + 1e-9)
             + CONFIG["probability_offset"]
             - CONFIG["probability_zcr_weight"] * zcr)
    return 1.0 / (1.0 + math.exp(-score))


def probability_for_frame(frame: list[float]) -> float:
    return probability_for_features(frame_features(frame))


def truth_intervals(truth: str = "speech") -> list[tuple[int, int]]:
    return [(segment["start"], segment["end"])
            for segment in SEGMENTS if segment["truth"] == truth]


def truth_by_sample(start: int, end: int) -> str:
    if start < 0 or end > TOTAL_SAMPLES or start >= end:
        raise ValueError("invalid_truth_interval")
    labels = {segment_for_sample(index)["truth"] for index in range(start, end)}
    if labels == {"speech"}:
        return "speech"
    if labels == {"nonspeech"}:
        return "nonspeech"
    if labels == {"unknown"}:
        return "unknown"
    return "mixed"


def fixture_spec() -> dict[str, Any]:
    pcm_int = build_pcm_int()
    frames = build_frames()
    probabilities = [probability_for_frame(frame) for frame in frames]
    return {
        "fixture_id": "fast-vad-0-2-1-synthetic-fixture-v1",
        "stream_sha256": sha256_bytes(canonical_bytes(pcm_int)),
        "stream_samples": TOTAL_SAMPLES,
        "config": CONFIG,
        "segments": [dict(segment) for segment in SEGMENTS],
        "probability_digest": sha256_bytes(canonical_bytes(probabilities)),
    }


FIXTURE_SPEC_DIGEST = sha256_bytes(canonical_bytes(fixture_spec()))
