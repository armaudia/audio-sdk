# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen fully synthetic room-fixture generator for SDK-WEBRTC-AEC3.

No WebRTC AEC3 source, binary, weight, model, licensed corpus, recorded room,
device timing or listening result is read.  Everything here is produced from
integer-seeded deterministic arithmetic and analytic tones.  All streams are
16 kHz mono float32 and are divided into 160-sample SDK frames.

The render/reference sidechain is explicit.  Delayed, dropped and missing
render are represented as separate adverse conditions and are never assumed to
be aligned or available.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any

TASK_DIR = Path(__file__).resolve().parent

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
TOTAL_SAMPLES = 32000
TOTAL_FRAMES = TOTAL_SAMPLES // FRAME_SAMPLES
SAMPLE_PERIOD_NS = 62500

NOISE_SEED_FAR = 0x1A2B3C4D
NOISE_SEED_NEAR = 0x5E6F7081
NOISE_SEED_CAPTURE = 0x9ABCDEF0
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345

CAPTURE_NOISE_AMPLITUDE = 0.0025
PATH_CHANGE_SAMPLE = 16000
RESET_FRAME = 100
RESET_EPOCH = 2
DELAYED_RENDER_SAMPLES = 24
DROPOUT_START_FRAME = 76
DROPOUT_END_FRAME = 96

PATH_A: tuple[tuple[int, float], ...] = ((12, 1.0), (24, 0.55), (38, 0.25))
PATH_B: tuple[tuple[int, float], ...] = ((20, 0.9), (44, 0.6))
MAX_PATH_DELAY = max(max(delay for delay, _ in path) for path in (PATH_A, PATH_B))

# Half-open sample intervals.  ``render_env``/``near_env`` are frozen excitation
# gains; ``path`` is the frozen synthetic echo path active in that interval.
SEGMENTS: tuple[dict[str, Any], ...] = (
    {"id": "silence", "start": 0, "end": 1600, "render_env": 0.0, "near_env": 0.0, "path": "A"},
    {"id": "echo_only_a", "start": 1600, "end": 6400, "render_env": 1.0, "near_env": 0.0, "path": "A"},
    {"id": "overlap_a", "start": 6400, "end": 11200, "render_env": 0.8, "near_env": 0.9, "path": "A"},
    {"id": "near_only_a", "start": 11200, "end": 12800, "render_env": 0.0, "near_env": 1.0, "path": "A"},
    {"id": "echo_only_a_late", "start": 12800, "end": 16000, "render_env": 1.0, "near_env": 0.0, "path": "A"},
    {"id": "overlap_b", "start": 16000, "end": 20000, "render_env": 0.9, "near_env": 0.8, "path": "B"},
    {"id": "echo_only_b", "start": 20000, "end": 24000, "render_env": 1.0, "near_env": 0.0, "path": "B"},
    {"id": "near_only_b", "start": 24000, "end": 28000, "render_env": 0.0, "near_env": 1.0, "path": "B"},
    {"id": "overlap_b_late", "start": 28000, "end": 32000, "render_env": 0.7, "near_env": 0.7, "path": "B"},
)

# Frozen scoring windows (half-open sample coordinates).  They are chosen away
# from convergence, path changes and resets, and never influence processing.
WINDOWS: dict[str, tuple[int, int]] = {
    "echo_only_early": (3200, 6080),
    "echo_only_late": (20800, 23680),
    "overlap_early": (7200, 11040),
    "near_only_early": (11200, 12800),
    "overlap_late": (17600, 19840),
    "near_only_late": (24000, 28000),
}

CONDITIONS: tuple[str, ...] = (
    "echo_only", "near_only", "overlap", "no_reference", "delayed_render",
    "reference_dropout", "path_change", "reset",
)
CONTROLS: tuple[str, ...] = ("identity", "fixed_attenuation", "no_reference_passthrough")
STIMULI: tuple[str, ...] = ("impulse", "step", "silence")

# Source pins are content-addressed at authoring time.  A missing or changed
# pin is a hard failure, never a skip or a substituted oracle.
SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/webrtc-aec/README.md":
        "c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/check.py":
        "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# The mutable board is provenance only: a snapshot, never a gate or a result.
MUTABLE_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_BOARD_SHA256_AT_READ = (
    "275f2d6550eb3f7357d41f8749d92489ebb8601e9f9c5f025d67898fa577e106"
)


def workspace_root() -> Path:
    """Locate the pinned workspace without relying on the process CWD."""
    for parent in TASK_DIR.parents:
        if ((parent / "research" / "voice-enhancement-20261101" / "candidate_matrix.csv").is_file()
                and (parent / "audio-benchmark-platform" / "plan" / "swarm"
                     / "VERIFICATION.md").is_file()):
            return parent
    raise FileNotFoundError("workspace_root_not_found")


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


def f32(value: float) -> float:
    """Round to IEEE-754 binary32 so Python and the C boundary agree exactly."""
    return struct.unpack("<f", struct.pack("<f", value))[0]


def lcg_next(state: int) -> int:
    return (LCG_MULTIPLIER * state + LCG_INCREMENT) & 0x7FFFFFFF


def lcg_noise(state: int) -> float:
    state = lcg_next(state)
    return ((state >> 16) - 32768) / 65536.0


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


def path_for_sample(index: int) -> tuple[tuple[int, float], ...]:
    return PATH_B if index >= PATH_CHANGE_SAMPLE else PATH_A


def shift_signal(samples: Any, delay_samples: int) -> tuple[float, ...]:
    """Delay render by inserting leading zeros; never look into the future."""
    if delay_samples < 0 or delay_samples > len(samples):
        raise ValueError("invalid_delay")
    values = [f32(float(value)) for value in samples]
    return tuple([0.0] * delay_samples + values[:len(values) - delay_samples])


def build_stream(condition: str = "overlap") -> dict[str, Any]:
    """Return the frozen capture/render/near/noise streams for one condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown_condition")
    far_state = NOISE_SEED_FAR
    near_state = NOISE_SEED_NEAR
    capture_state = NOISE_SEED_CAPTURE
    render_raw: list[float] = []
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        far = segment["render_env"]
        if condition == "near_only":
            far = 0.0
        far_state = lcg_next(far_state)
        white = ((far_state >> 16) - 32768) / 65536.0
        phase = 2.0 * math.pi * index / SAMPLE_RATE_HZ
        render_raw.append(far * (0.22 * math.sin(137.0 * phase)
                                 + 0.09 * math.sin(311.0 * phase)
                                 + 0.025 * white))

    microphone: list[float] = []
    near: list[float] = []
    render: list[float] = []
    capture_noise: list[float] = []
    path_ids: list[str] = []
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        path = PATH_B if index >= PATH_CHANGE_SAMPLE else PATH_A
        path_ids.append(segment["path"])
        near_env = segment["near_env"]
        if condition == "echo_only":
            near_env = 0.0
        near_state = lcg_next(near_state)
        near_white = ((near_state >> 16) - 32768) / 65536.0
        phase = 2.0 * math.pi * index / SAMPLE_RATE_HZ
        near_sample = near_env * (0.16 * math.sin(183.0 * phase)
                                  + 0.06 * math.sin(271.0 * phase)
                                  + 0.02 * near_white)
        echo = 0.0
        for delay, gain in path:
            if index >= delay:
                echo += gain * render_raw[index - delay]
        capture_state = lcg_next(capture_state)
        noise = CAPTURE_NOISE_AMPLITUDE * ((capture_state >> 16) - 32768) / 32768.0
        render.append(f32(render_raw[index]))
        near.append(f32(near_sample))
        capture_noise.append(f32(noise))
        microphone.append(f32(echo + near_sample + noise))

    reference_stream: tuple[float, ...] | None = tuple(render)
    if condition == "delayed_render":
        reference_stream = shift_signal(render, DELAYED_RENDER_SAMPLES)
    if condition == "no_reference":
        reference_stream = None
    return {
        "condition": condition,
        "microphone": tuple(microphone),
        "reference": reference_stream,
        "render": tuple(render),
        "near": tuple(near),
        "capture_noise": tuple(capture_noise),
        "path_ids": tuple(path_ids),
        "reset_frame": RESET_FRAME if condition == "reset" else None,
        "dropout": (DROPOUT_START_FRAME, DROPOUT_END_FRAME)
                   if condition == "reference_dropout" else None,
    }


def stimulus(name: str) -> dict[str, Any]:
    """Small deterministic causality probes (not room-profile qualification)."""
    if name not in STIMULI:
        raise ValueError("unknown_stimulus")
    if name == "silence":
        samples = tuple([0.0] * TOTAL_SAMPLES)
    elif name == "impulse":
        values = [0.0] * TOTAL_SAMPLES
        values[1600] = 0.5
        samples = tuple(f32(value) for value in values)
    else:
        samples = tuple(f32(0.1 if index >= 1600 else 0.0) for index in range(TOTAL_SAMPLES))
    return {
        "condition": name,
        "microphone": samples,
        "reference": samples,
        "render": samples,
        "near": tuple([0.0] * TOTAL_SAMPLES),
        "capture_noise": tuple([0.0] * TOTAL_SAMPLES),
        "path_ids": tuple(["A"] * TOTAL_FRAMES),
        "reset_frame": None,
        "dropout": None,
    }


def stream_spec() -> dict[str, Any]:
    """Frozen geometry, excitation, noise, delay, movement and reset schedule."""
    digests: dict[str, str] = {}
    for condition in CONDITIONS:
        data = build_stream(condition)
        digests[condition] = {
            "microphone": sha256_bytes(canonical_bytes(list(data["microphone"]))),
            "reference": ("none" if data["reference"] is None else
                          sha256_bytes(canonical_bytes(list(data["reference"])))),
            "near": sha256_bytes(canonical_bytes(list(data["near"]))),
        }
    return {
        "fixture_id": "webrtc-aec3-synthetic-room-v1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_format": "f32",
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": FRAME_SAMPLES,
        "total_samples": TOTAL_SAMPLES,
        "total_frames": TOTAL_FRAMES,
        "geometry": {
            "path_a_taps": {str(delay): gain for delay, gain in PATH_A},
            "path_b_taps": {str(delay): gain for delay, gain in PATH_B},
            "max_path_delay_samples": MAX_PATH_DELAY,
        },
        "signal_model": {
            "far_end": "render = f32(render_env * (0.22 sin(137 Hz) + 0.09 sin(311 Hz) + 0.025 seeded white)); far-end-only condition is echo_only",
            "near_end": "near = f32(near_env * (0.16 sin(183 Hz) + 0.06 sin(271 Hz) + 0.02 seeded white)); near-end-only condition is near_only; never supplied to the processor",
            "capture_noise": "f32(0.0025 * seeded white, independent of render and near)",
            "microphone": "f32(sum(path taps applied to far_end) + near_end + capture_noise)",
            "echo_path": "PATH_A before sample 16000, PATH_B at and after sample 16000; sum of frozen delay/gain taps",
            "double_talk": "overlap condition, both far_end and near_end active",
            "reference_sidechain": "explicit render stream supplied one frame per mic frame, frame k before mic frame k; delayed/withheld/dropout are separate adverse conditions",
        },
        "metrics": {
            "erle_proxy": "10log10(energy(microphone)/energy(output)) in frozen echo-only windows; synthetic echo-return-loss proxy only, not WebRTC ERLE or accepted quality",
            "near_snr": "10log10(energy(near)/energy(output-near)) in frozen windows from synthetic ground truth never given to the processor",
            "alignment": "normalized cross-correlation lag between the supplied render/reference and microphone; fixture alignment only, not device or buffering timing",
            "matched_controls": "identity, fixed_attenuation(0.5) and no_reference_passthrough run on the same frozen overlap stream with no adaptation",
        },
        "excitation": {
            "render_hz": [137, 311], "near_hz": [183, 271],
            "render_amplitudes": [0.22, 0.09, 0.025],
            "near_amplitudes": [0.16, 0.06, 0.02],
            "seeds": {"render": NOISE_SEED_FAR, "near": NOISE_SEED_NEAR},
        },
        "noise": {
            "capture_amplitude": CAPTURE_NOISE_AMPLITUDE,
            "seed": NOISE_SEED_CAPTURE,
        },
        "delay": {
            "reference_delay_samples": 0,
            "delayed_render_shift_samples": DELAYED_RENDER_SAMPLES,
            "algorithmic_delay_samples": 0,
            "buffering_delay_samples": 0,
        },
        "movement": {
            "path_change_sample": PATH_CHANGE_SAMPLE,
            "from_path": "A", "to_path": "B",
        },
        "reset": {
            "initial_epoch": 1,
            "reset_frame": RESET_FRAME,
            "reset_sample": RESET_FRAME * FRAME_SAMPLES,
            "reset_epoch": RESET_EPOCH,
        },
        "reference_dropout": {
            "start_frame": DROPOUT_START_FRAME,
            "end_frame": DROPOUT_END_FRAME,
        },
        "segments": [dict(segment) for segment in SEGMENTS],
        "metric_windows": {name: list(window) for name, window in WINDOWS.items()},
        "stream_sha256": digests,
    }


FIXTURE_SPEC_DIGEST = sha256_bytes(canonical_bytes(stream_spec()))
