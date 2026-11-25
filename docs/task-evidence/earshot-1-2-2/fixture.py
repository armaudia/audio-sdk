# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, fully synthetic Earshot 1.2.2 VAD analysis fixture.

Every sample is produced from integer arithmetic and a fixed 64-entry waveform
table.  The stream is 16 kHz mono f32 with the adapter's exact 256-sample
(16 ms) decision cadence.  No real recording, wheel, model, device or licensed
runtime is used anywhere in this package.

The truth table partitions the stream into known speech, known nonspeech and
one explicit unknown span.  Unknown samples are excluded from every scoring
denominator; they are never relabeled nonspeech.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 256
FRAME_DURATION_MS = 16
SAMPLE_NS = 62500
TOTAL_SAMPLES = 32000
TOTAL_FRAMES = TOTAL_SAMPLES // FRAME_SAMPLES
ORIGIN_NS = 1767225600000000000
PROCESSING_DELAY_NS = 1000000
CLOCK = "earshot-1-2-2-fixture-monotonic-v0"

# Content-addressed research inputs.  A missing or changed pin is a hard
# failure, never a skip or a substituted oracle.
SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "adapters/earshot-vad/adapter.json":
        "f3d391cf015cc897be20b19fab563bdef4f63310f4aceaad4d1c0bab0db3d091",
    "adapters/earshot-vad/run.py":
        "541e08619480b63c2a77bd7fd45f454ee8828a90737a65af707a4c017a6fd8a8",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "reports/vad-research/chaining-evaluation.md":
        "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "reports/vad-research/attempt-earshot-20261028-01/findings.md":
        "cefe94dea241e7ce98071f0be336e463cbf2b9f5fa90785b0e4c4b5439f14a8f",
    "reports/vad-research/20261028-synthesis-v6.md":
        "d8bc5d7481ffc40ee7c16caba6b570255e24aef2a99e7f03b0293721c37d8df3",
    "reports/vad-research/chaining-evaluation-status.json":
        "3b66ba722c06673fdcc698e3f10e716e13aae74bc2f2c0ebd046316ed6fd068c",
    "research/plans/F02/vad_sources.md":
        "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}

BOUNDARY_PINS: dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Expected identity of external assets.  Nothing here is present, downloaded,
# copied, loaded or executed by this package.  The wheel path is machine-checked
# for absence: if it appears, this evidence package is stale and must reopen.
EXTERNAL_ASSET_PINS: dict[str, dict[str, Any]] = {
    "asset:wheel": {
        "filename": "earshot-1.2.2-cp38-abi3-macosx_11_0_arm64.whl",
        "expected_path":
            "data/wheels/vad-candidates/"
            "earshot-1.2.2-cp38-abi3-macosx_11_0_arm64.whl",
        "sha256": "bf696faad73a996c40bea8115622a5dcbc9c6da01498885bfd9eae8be1a11ecd",
        "present": False,
        "loaded": False,
        "executed": False,
    },
    "asset:source_archive": {
        "filename": "earshot-1.2.2 source archive",
        "expected_path": None,
        "sha256": "a2aad72917334d2b9e7385b73dc837bd30244714ccf27d45fbfcc0e038cfcaeb",
        "present": False,
        "loaded": False,
        "executed": False,
    },
}

MUTABLE_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_BOARD_SHA256_AT_READ = (
    "d89177e65347d27e274dd12c0c00cb6e46145a5f0c234303e4ff2ec295e7ec8e"
)

CONFIG: dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "decision_threshold": 0.5,
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

# Frozen truth intervals: half-open sample coordinates on the exact source
# clock.  Every boundary is a multiple of 256 samples, so each frame has one
# unambiguous source label.
SEGMENTS: tuple[dict[str, Any], ...] = (
    {"id": "idle-a", "start": 0, "end": 2048, "truth": "nonspeech",
     "condition": "idle", "tone_amplitude": 0, "noise_amplitude": 90},
    {"id": "quiet-a", "start": 2048, "end": 6144, "truth": "speech",
     "condition": "quiet_speech", "tone_amplitude": 300,
     "tone_amplitude_end": 2800, "noise_amplitude": 55},
    {"id": "idle-b", "start": 6144, "end": 8192, "truth": "nonspeech",
     "condition": "idle", "tone_amplitude": 0, "noise_amplitude": 140},
    {"id": "active-a", "start": 8192, "end": 16128, "truth": "speech",
     "condition": "active_speech", "tone_amplitude": 18000, "noise_amplitude": 120},
    {"id": "noise-burst", "start": 16128, "end": 18688, "truth": "nonspeech",
     "condition": "idle_noise", "tone_amplitude": 0,
     "noise_amplitude": 700, "noise_amplitude_end": 15000},
    {"id": "quiet-b", "start": 18688, "end": 22016, "truth": "speech",
     "condition": "quiet_speech", "tone_amplitude": 340, "noise_amplitude": 55},
    {"id": "idle-c", "start": 22016, "end": 24576, "truth": "nonspeech",
     "condition": "idle", "tone_amplitude": 0, "noise_amplitude": 90},
    {"id": "unknown-tail", "start": 24576, "end": 27904, "truth": "unknown",
     "condition": "unknown", "tone_amplitude": 800, "noise_amplitude": 210},
    {"id": "idle-d", "start": 27904, "end": 32000, "truth": "nonspeech",
     "condition": "idle", "tone_amplitude": 0, "noise_amplitude": 75},
)

_WAVE: tuple[int, ...] = tuple(
    int(round(32767.0 * math.sin(2.0 * math.pi * k / 64.0))) for k in range(64)
)


def workspace_root() -> Path:
    """Locate the pinned research workspace without relying on the CWD."""
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override)
    for parent in TASK_DIR.parents:
        if ((parent / "research" / "voice-enhancement-20261101"
             / "candidate_matrix.csv").is_file()
                and (parent / "audio-benchmark-platform" / "plan" / "swarm"
                     / "VERIFICATION.md").is_file()):
            return parent
    raise FileNotFoundError("workspace root with pinned sources not found")


def resolve_source_path(name: str) -> Path:
    return workspace_root() / name


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      indent=2)
    return (text + "\n").encode("utf-8")


def validate_config(config: dict[str, Any]) -> None:
    if set(config) != set(CONFIG):
        raise ValueError("config_key_set_mismatch")
    for key, expected in CONFIG.items():
        if config[key] != expected:
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
    phase_acc_high = 0
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        noise_state = (1103515245 * noise_state + 12345) & 0x7FFFFFFF
        noise = (noise_state >> 16) - 16384
        phase_acc += 112 * 64
        phase_acc_high += 224 * 64
        table_index = (phase_acc // SAMPLE_RATE_HZ) % 64
        table_index_high = (phase_acc_high // SAMPLE_RATE_HZ) % 64
        tone = _WAVE[table_index] + _WAVE[table_index_high] // 3
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
    if len(frame) == 1:
        zcr = 0.0
    else:
        zcr = sum(1 for left, right in zip(frame, frame[1:])
                  if (left < 0.0) != (right < 0.0)) / (len(frame) - 1)
    return {"rms": rms, "zcr": zcr}


def probability_for_features(features: dict[str, float]) -> float:
    score = (CONFIG["probability_gain"] * math.log10(features["rms"] + 1e-9)
             + CONFIG["probability_offset"]
             - CONFIG["probability_zcr_weight"] * features["zcr"])
    value = 1.0 / (1.0 + math.exp(-score))
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("surrogate_probability_out_of_range")
    return value


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


def truth_totals() -> dict[str, int]:
    totals = {"speech": 0, "nonspeech": 0, "unknown": 0}
    for segment in SEGMENTS:
        totals[segment["truth"]] += segment["end"] - segment["start"]
    return totals


def fixture_spec() -> dict[str, Any]:
    pcm_int = build_pcm_int()
    frames = build_frames()
    probabilities = [probability_for_frame(frame) for frame in frames]
    return {
        "fixture_id": "earshot-1-2-2-synthetic-fixture-v1",
        "stream_sha256": sha256_bytes(canonical_bytes(pcm_int)),
        "stream_samples": TOTAL_SAMPLES,
        "stream_frames": TOTAL_FRAMES,
        "frame_samples": FRAME_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "config": dict(CONFIG),
        "segments": [dict(segment) for segment in SEGMENTS],
        "truth_totals": truth_totals(),
        "probability_digest": sha256_bytes(canonical_bytes(probabilities)),
    }


FIXTURE_SPEC_DIGEST = sha256_bytes(canonical_bytes(fixture_spec()))
