# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic fixtures for the task-local rate-change reference.

No audio corpus, FFmpeg binary, FFmpeg source, model, device trace or listening
result is used.  All waveforms come from fixed integer tables and a 32-bit
linear congruential generator.  Source pins are provenance only: they are
hashed and never imported or executed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

TASK = "SDK-FFMPEG-ATEMPO"
COMPONENT = "ffmpeg-atempo"
BASE_COMMIT = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-FFMPEG-ATEMPO"
STATUS = "proposal_only_not_qualified"
QUALIFICATION_STATUS = "incomplete"
DECISION = "DEFER"
PROFILE = "rate"

WORKSPACE = Path("/Users/htsakanyan/workspace/audio/audioml")
TASK_DIR = Path(__file__).resolve().parent

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
ANALYSIS_HOP = 160
WINDOW_SAMPLES = 640
SAMPLE_NS = 62500

SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
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
}

MUTABLE_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_BOARD_SHA256_AT_READ = (
    "0c443df7655e040679e48f39524af549deb355569050217a7fb05e4352b2ec74"
)

VOICE_TABLE = (0, 9000, 18000, 12000, 3000, -6000, -15000, -19000,
               -11000, -3000, 4000, 11000, 17000, 10000, 2000, -5000)
MUSIC_TABLE = (0, 4000, 8000, 12000, 8000, 4000, 0, -4000,
               -8000, -12000, -8000, -4000, 0, 2000, 6000, 9000)
MELODY_STEPS = (0, 2, 4, 2, 5, 4, 2, 0, 3, 5, 7, 5, 4, 2, 1, 0)
CHUNK_PATTERN = (37, 91, 160, 123, 53, 160, 211)
CHUNK_SCHEDULE_NAMES = ("single", "sdk_frames", "irregular", "tiny")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def resolve_pin_path(name: str) -> Path:
    return WORKSPACE / name


def verify_source_pins() -> dict[str, str]:
    actual: dict[str, str] = {}
    for name, expected in SOURCE_PINS.items():
        path = resolve_pin_path(name)
        if not path.is_file():
            raise ValueError("missing_pinned_source:" + name)
        digest = sha256_file(path)
        if digest != expected:
            raise ValueError("pinned_source_changed:" + name)
        actual[name] = digest
    return actual


def lcg(seed: int, count: int) -> list[int]:
    state = seed & 0xFFFFFFFF
    result: list[int] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        result.append(state)
    return result


def clamp_sample(value: int) -> int:
    return max(-32768, min(32767, value))


def voice(seed: int, length: int, period: int, amplitude: int) -> list[int]:
    noise = lcg(seed, length)
    out: list[int] = []
    for index in range(length):
        table_index = (index * len(VOICE_TABLE) // period) % len(VOICE_TABLE)
        breath = ((noise[index] >> 21) - 1024) // 8
        out.append(clamp_sample(VOICE_TABLE[table_index] * amplitude // 16 + breath))
    return out


def music(seed: int, length: int, period: int, amplitude: int) -> list[int]:
    noise = lcg(seed, length)
    out: list[int] = []
    for index in range(length):
        step = MELODY_STEPS[(index // 400) % len(MELODY_STEPS)]
        table_index = (index * len(MUSIC_TABLE) // period) % len(MUSIC_TABLE)
        value = MUSIC_TABLE[table_index] * (step + 3) // 8
        breath = ((noise[index] >> 22) - 512) // 16
        out.append(clamp_sample(value * amplitude // 16 + breath))
    return out


def fill_noise(seed: int, length: int, amplitude: int) -> list[int]:
    noise = lcg(seed, length)
    return [clamp_sample(((state >> 18) - 8192) * amplitude // 4096) for state in noise]


def add_impulses(samples: list[int], positions: list[int], amplitude: int) -> None:
    for position in positions:
        for offset in range(-8, 9):
            index = position + offset
            if 0 <= index < len(samples):
                weight = 9 - abs(offset)
                samples[index] = clamp_sample(samples[index] + amplitude * weight // 9)


def segment(start: int, end: int, kind: str) -> dict[str, Any]:
    return {"start": start, "end": end, "kind": kind}


def make_scenario(name: str, length: int, segments: list[dict[str, Any]],
                  rates: list[list[int]], stalls: list[list[int]],
                  transients: list[int], generator: str, seed: int) -> dict[str, Any]:
    if segments and segments[0]["start"] != 0:
        raise ValueError("segments_must_start_at_zero")
    previous = 0
    for item in segments:
        if item["start"] != previous or item["end"] <= item["start"]:
            raise ValueError("segments_must_be_contiguous")
        previous = item["end"]
    if previous != length:
        raise ValueError("segments_must_cover_source")
    for rate in rates:
        if rate[0] % ANALYSIS_HOP != 0 or rate[0] >= length:
            raise ValueError("rate_change_must_be_frame_aligned")
    for stall in stalls:
        if stall[0] % ANALYSIS_HOP != 0 or stall[1] <= stall[0]:
            raise ValueError("stall_must_be_frame_aligned")
    return {
        "name": name,
        "length": length,
        "segments": segments,
        "rate_schedule": rates,
        "stalls": stalls,
        "transients": transients,
        "generator": generator,
        "seed": seed,
        "samples": tuple(_render(segments, generator, seed, length, transients)),
    }


def _render(segments: list[dict[str, Any]], generator: str, seed: int,
            length: int, transients: list[int]) -> list[int]:
    samples = [0] * length
    for index, item in enumerate(segments):
        count = item["end"] - item["start"]
        kind = item["kind"]
        if kind.startswith("speech"):
            wave = voice(seed + index * 17, count, 128 + index * 13, 12 + index)
        elif kind.startswith("music"):
            wave = music(seed + index * 23, count, 96 + index * 7, 11 + index)
        elif kind in ("filler", "pause"):
            wave = fill_noise(seed + index * 31, count, 3 if kind == "filler" else 1)
        else:
            wave = [0] * count
        samples[item["start"]:item["end"]] = wave
    add_impulses(samples, transients, 26000)
    return samples


SCENARIOS: tuple[dict[str, Any], ...] = (
    make_scenario(
        "identity_1x_speech", 4000,
        [segment(0, 1600, "speech_unfamiliar"), segment(1600, 1920, "pause"),
         segment(1920, 2240, "filler"), segment(2240, 3840, "speech_alt"),
         segment(3840, 4000, "silence")],
        [[0, 1, 1]], [], [640, 2560], "mixed", 101),
    make_scenario(
        "faster_1_25_speech", 4000,
        [segment(0, 1440, "speech_unfamiliar"), segment(1440, 1760, "pause"),
         segment(1760, 4000, "speech_alt")],
        [[0, 5, 4]], [], [480, 2880], "mixed", 202),
    make_scenario(
        "slower_0_8_speech", 4000,
        [segment(0, 1280, "speech_alt"), segment(1280, 1920, "filler"),
         segment(1920, 4000, "speech_unfamiliar")],
        [[0, 4, 5]], [], [800, 2720], "mixed", 303),
    make_scenario(
        "unfamiliar_music_1_5", 4800,
        [segment(0, 1600, "music_unfamiliar"), segment(1600, 1920, "silence"),
         segment(1920, 4800, "music_alt")],
        [[0, 3, 2]], [], [960, 3520], "music", 404),
    make_scenario(
        "silence_filler_1x", 3200,
        [segment(0, 480, "silence"), segment(480, 960, "filler"),
         segment(960, 2240, "speech_unfamiliar"), segment(2240, 2720, "pause"),
         segment(2720, 3200, "speech_alt")],
        [[0, 1, 1]], [], [1440, 2880], "mixed", 505),
    make_scenario(
        "rebuffer_step", 6400,
        [segment(0, 2400, "speech_unfamiliar"), segment(2400, 2720, "pause"),
         segment(2720, 4800, "speech_alt"), segment(4800, 5120, "filler"),
         segment(5120, 6400, "speech_unfamiliar")],
        [[0, 1, 1], [3200, 5, 4], [4800, 4, 5]], [[2400, 2720]],
        [800, 3840, 5760], "mixed", 606),
    make_scenario(
        "drift_partial_tail", 1797,
        [segment(0, 1120, "speech_alt"), segment(1120, 1440, "filler"),
         segment(1440, 1797, "speech_unfamiliar")],
        [[0, 1, 1], [480, 11, 10], [960, 9, 8], [1440, 4, 5]], [],
        [320, 1600], "mixed", 707),
    make_scenario(
        "music_slow_0_75", 3600,
        [segment(0, 960, "music_alt"), segment(960, 1280, "silence"),
         segment(1280, 3600, "music_unfamiliar")],
        [[0, 3, 4]], [], [640, 2240], "music", 808),
)


def scenario_by_name(name: str) -> dict[str, Any]:
    for scenario in SCENARIOS:
        if scenario["name"] == name:
            return scenario
    raise KeyError("unknown_scenario:" + name)


def chunk_sizes(scenario: dict[str, Any], schedule: str) -> list[int]:
    length = int(scenario["length"])
    if schedule == "single":
        return [length]
    if schedule == "sdk_frames":
        sizes = [FRAME_SAMPLES] * (length // FRAME_SAMPLES)
        if length % FRAME_SAMPLES:
            sizes.append(length % FRAME_SAMPLES)
        return sizes
    if schedule == "irregular":
        sizes: list[int] = []
        remaining = length
        index = 0
        while remaining:
            size = min(CHUNK_PATTERN[index % len(CHUNK_PATTERN)], remaining)
            sizes.append(size)
            remaining -= size
            index += 1
        return sizes
    if schedule == "tiny":
        return [1] * length
    raise ValueError("unknown_chunk_schedule:" + schedule)


def samples_digest(samples: list[int] | tuple[int, ...]) -> str:
    payload = ",".join(str(value) for value in samples).encode("ascii")
    return sha256_bytes(payload)
