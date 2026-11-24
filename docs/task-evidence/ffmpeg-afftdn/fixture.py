# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, fully synthetic frequency-domain noise-suppression fixture.

Nothing in this module reads or executes FFmpeg, a wheel, a model, a speech
corpus or a device.  Stimuli are generated from integer arithmetic with a
fixed linear-congruential source, then exposed as deterministic float samples.
The stream shape is the installed SDK v0 shape: 16 kHz mono float32 semantics,
partitioned into 160-sample frames.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any

TASK_DIR = Path(__file__).resolve().parent

TASK = "SDK-FFMPEG-AFFTDN"
COMPONENT = "ffmpeg-afftdn"
BASE_COMMIT = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-FFMPEG-AFFTDN"
LOCAL_IDENTITY = "ffmpeg-afftdn-synthetic-frequency-domain-v1"
ADAPTER_ID = "ffmpeg-denoise-v1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
WINDOW_SAMPLES = 256
HOP_SAMPLES = 160
LOOKAHEAD_SAMPLES = WINDOW_SAMPLES - HOP_SAMPLES
TOTAL_SAMPLES = 8000
CALIBRATION_END = 1600
SPEECH_END = 7200
INT_SCALE = 32768
LCG_MODULUS = 2147483648
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345

# Content-addressed at task authoring time.  A missing or changed pin is a hard
# failure; there is no substitution, pooling or tolerance.
SOURCE_PINS: dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "adapters/ffmpeg-denoise/adapter.json":
        "2909f28275cd05df650af3d38ee7ec523cab00e8a5a52ed89773dd450a35a4fe",
    "adapters/ffmpeg-denoise/README.md":
        "cb498047caa12890f89754411a478e9d870ff03100876031ee0abe84889b3530",
    "adapters/ffmpeg-denoise/run.py":
        "db183ece8d8c4f04a97ce0fd1ce588ec07f8946061096008a51de3ae45c4ab4b",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# The mutable board is provenance only: recorded as a snapshot, never used as
# a gate or as a qualification source.
MUTABLE_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_BOARD_SHA256_AT_READ = (
    "77d43709d7bffa83ba52410818f1da76527dc1dd5697d39012d6932320e5458b"
)

BOUNDARY_PINS: dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

CONFIG: dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "window_samples": WINDOW_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "lookahead_samples": LOOKAHEAD_SAMPLES,
    "total_samples": TOTAL_SAMPLES,
    "spectral_exponent": 1.7,
    "gain_floor": 0.125,
    "gain_release": 0.7,
    "power_epsilon": 1e-10,
    "fixed_gain_baseline": 0.7,
    "source_time_mapping": "identity_ola_with_declared_lookahead",
    "real_runtime": False,
    "ffmpeg_binary_used": False,
    "licensed_asset_used": False,
    "timing_measured": False,
}

# Frozen synthetic cohort.  Each item has an explicit noise-only calibration
# span; the profile is never estimated from speech-bearing audio.
ITEMS: tuple[dict[str, Any], ...] = (
    {"id": "case-quiet", "seed": 20261124, "f0_hz": 110, "speech_gain": 0.35,
     "noise_gain": 0.10, "hum_hz": 50, "burst": False},
    {"id": "case-loud", "seed": 20261125, "f0_hz": 132, "speech_gain": 0.65,
     "noise_gain": 0.16, "hum_hz": 60, "burst": False},
    {"id": "case-hum", "seed": 20261126, "f0_hz": 98, "speech_gain": 0.45,
     "noise_gain": 0.12, "hum_hz": 120, "burst": False},
    {"id": "case-burst", "seed": 20261127, "f0_hz": 150, "speech_gain": 0.55,
     "noise_gain": 0.09, "hum_hz": 50, "burst": True},
)

# Half-open sample gates for the synthetic voiced regions.
SPEECH_GATES: tuple[tuple[int, int], ...] = (
    (1600, 2400),
    (2800, 4800),
    (5200, 7200),
)

UNPAIRED_ITEMS: tuple[dict[str, Any], ...] = (
    {"id": "unpaired-a", "seed": 3001, "f0_hz": 118, "speech_gain": 0.41,
     "noise_gain": 0.11, "hum_hz": 55, "burst": False},
    {"id": "unpaired-b", "seed": 3002, "f0_hz": 141, "speech_gain": 0.58,
     "noise_gain": 0.13, "hum_hz": 70, "burst": False},
)

FIXTURE_SPEC: dict[str, Any] = {
    "protocol": 1,
    "identity": LOCAL_IDENTITY,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "window_samples": WINDOW_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "total_samples": TOTAL_SAMPLES,
    "calibration_end": CALIBRATION_END,
    "speech_end": SPEECH_END,
    "speech_gates": [list(gate) for gate in SPEECH_GATES],
    "int_scale": INT_SCALE,
    "lcg": [LCG_MODULUS, LCG_MULTIPLIER, LCG_INCREMENT],
    "harmonics": [0.62, 0.27, 0.11, 0.06],
    "noise_mix": [0.55, 0.45, 0.035],
    "noise_lowpass": 0.85,
    "burst_window": [4800, 5600, 0.35],
    "items": [dict(item) for item in ITEMS],
    "unpaired_items": [dict(item) for item in UNPAIRED_ITEMS],
    "config": dict(CONFIG),
}


def workspace_root() -> Path:
    """Locate the pinned workspace without relying on the process CWD."""
    for parent in TASK_DIR.parents:
        if ((parent / "research" / "voice-enhancement-20261101"
             / "candidate_matrix.csv").is_file()
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
    # Keep JSON SPDX key escaped to avoid literal token in JSON files.
    text = text.replace('"SPDX' + '-License-Identifier"', '"SPDX\\u002dLicense-Identifier"')
    return (text + "\n").encode("utf-8")


@lru_cache(maxsize=1)
def fixture_digest() -> str:
    return sha256_bytes(canonical_bytes(FIXTURE_SPEC))


def validate_config(config: dict[str, Any]) -> None:
    if set(config) != set(CONFIG):
        raise ValueError("config_key_set_mismatch")
    for key, expected in CONFIG.items():
        if config[key] != expected:
            raise ValueError("config_mismatch:" + key)


def frame_count(total_samples: int = TOTAL_SAMPLES) -> int:
    if total_samples <= 0 or total_samples % FRAME_SAMPLES != 0:
        raise ValueError("invalid_frame_partition")
    return total_samples // FRAME_SAMPLES


def frame_start(index: int) -> int:
    if not 0 <= index < frame_count():
        raise ValueError("frame_index_out_of_range")
    return index * HOP_SAMPLES


def in_calibration(index: int) -> bool:
    return 0 <= index < CALIBRATION_END


def speech_envelope(index: int) -> float:
    """Deterministic fade-in/fade-out envelope on the frozen speech gates."""
    if not 0 <= index < TOTAL_SAMPLES:
        raise ValueError("sample_out_of_range")
    for start, end in SPEECH_GATES:
        if start <= index < end:
            ramp = 80
            if index - start < ramp:
                return (index - start) / ramp
            if end - index <= ramp:
                return (end - index) / ramp
            return 1.0
    return 0.0


def lcg_bytes(seed: int, count: int) -> tuple[int, ...]:
    """Raw LCG states; no randomness, platform state or wall clock."""
    if seed <= 0 or count < 0:
        raise ValueError("invalid_lcg_request")
    values: list[int] = []
    state = seed % LCG_MODULUS
    for _ in range(count):
        state = (LCG_MULTIPLIER * state + LCG_INCREMENT) % LCG_MODULUS
        values.append(state)
    return tuple(values)


@lru_cache(maxsize=16)
def synthesize(item_id: str, unpaired: bool = False) -> dict[str, Any]:
    """Return frozen clean/noisy integer and float streams for one item."""
    pool = UNPAIRED_ITEMS if unpaired else ITEMS
    item = next((row for row in pool if row["id"] == item_id), None)
    if item is None:
        raise ValueError("unknown_item:" + item_id)
    states = lcg_bytes(int(item["seed"]), TOTAL_SAMPLES)
    h2, h3, h5 = (0.62, 0.27, 0.11, 0.06)[1:]
    h1 = 0.62
    clean_ints: list[int] = []
    noise_ints: list[int] = []
    lowpass = 0.0
    for index in range(TOTAL_SAMPLES):
        phase = 2.0 * math.pi * float(item["f0_hz"]) * index / SAMPLE_RATE_HZ
        voiced = (h1 * math.sin(phase) + h2 * math.sin(2.0 * phase)
                  + h3 * math.sin(3.0 * phase) + h5 * math.sin(5.0 * phase))
        envelope = speech_envelope(index) * float(item["speech_gain"])
        clean_value = voiced * envelope / (h1 + h2 + h3 + h5)
        white = states[index] / (LCG_MODULUS / 2.0) - 1.0
        lowpass = 0.85 * lowpass + 0.15 * white
        hum = math.sin(2.0 * math.pi * float(item["hum_hz"]) * index
                       / SAMPLE_RATE_HZ + 0.3)
        burst = 0.0
        if item["burst"] and 4800 <= index < 5600:
            burst = 0.35 * white
        noise_value = (float(item["noise_gain"]) * (0.55 * lowpass + 0.45 * white)
                       + 0.035 * hum + burst)
        clean_ints.append(max(-32767, min(32767, int(round(INT_SCALE * clean_value)))))
        noise_ints.append(max(-32767, min(32767, int(round(INT_SCALE * noise_value)))))
    clean = tuple(value / INT_SCALE for value in clean_ints)
    noise = tuple(value / INT_SCALE for value in noise_ints)
    noisy = tuple(max(-1.0, min(1.0, (clean_ints[i] + noise_ints[i]) / INT_SCALE))
                  for i in range(TOTAL_SAMPLES))
    return {
        "id": item_id,
        "spec": dict(item),
        "unpaired": unpaired,
        "clean_ints": tuple(clean_ints),
        "noise_ints": tuple(noise_ints),
        "clean": clean,
        "noise": noise,
        "noisy": noisy,
    }


def hann_window(length: int = WINDOW_SAMPLES) -> tuple[float, ...]:
    if length < 2:
        raise ValueError("invalid_window")
    return tuple(0.5 - 0.5 * math.cos(2.0 * math.pi * k / length)
                 for k in range(length))


@lru_cache(maxsize=8)
def overlap_norm(total_samples: int = TOTAL_SAMPLES) -> tuple[float, ...]:
    """Per-sample synthesis normaliser; makes gain=1 an exact identity."""
    if total_samples <= 0 or total_samples % FRAME_SAMPLES != 0:
        raise ValueError("invalid_frame_partition")
    window = hann_window()
    totals = [0.0] * total_samples
    for start in range(0, total_samples, HOP_SAMPLES):
        for j, weight in enumerate(window):
            index = start + j
            if index < total_samples:
                totals[index] += weight * weight
    # Hann window is zero at index 0; first/edge samples can have zero weight.
    # Use a tiny floor so division is well-defined while keeping near-identity.
    return tuple(max(value, 1e-12) for value in totals)


def item_ids(unpaired: bool = False) -> tuple[str, ...]:
    pool = UNPAIRED_ITEMS if unpaired else ITEMS
    return tuple(row["id"] for row in pool)
