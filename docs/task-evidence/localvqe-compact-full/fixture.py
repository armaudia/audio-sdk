# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic paired-reference room fixture for LocalVQE compact full.

Every sample is produced from integer arithmetic, a fixed 64-entry waveform
table and a deterministic LCG noise source.  The stream is 16 kHz mono f32 with
the caller contract's exact 256-sample (16 ms) hop and a synchronized far-end
render reference.  No real recording, model, weight, device or native runtime
is used anywhere in this package.

The fixture exposes the exact decomposition ``mic = echo + near + noise`` over a
frozen render path.  A path change is applied inside one echo-only stratum so
that movement is represented without pretending that the surrogate adapts.
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
TOTAL_SAMPLES = 64000
TOTAL_FRAMES = TOTAL_SAMPLES // FRAME_SAMPLES
ALGORITHMIC_LATENCY_SAMPLES = 256
ALGORITHMIC_LATENCY_MS = 16
MOVEMENT_CHANGE_SAMPLE = 45056

# Content-addressed research inputs.  A missing or changed pin is a hard
# failure, never a skip or a substituted oracle.
SOURCE_PINS: dict[str, str] = {
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/localvqe-aec/README.md":
        "61240419dc9d46af2056316f2a7167b833fb80e9d6a4ce8470b94a8cde488cd1",
    "adapters/localvqe-aec/run.py":
        "c4b8b5077e01bf8b7b736ea2e784087a6e811e5aec54f18c922dcda8a240fb5a",
    "adapters/localvqe/README.md":
        "b964486bb1f823f9ce6ad52b10210d04b596a8642bda5b46aedb0532eea808e0",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/joint-aec-profile/report.md":
        "d3d9b2d0c03245cb1b4f6e11a18093393fc9ed6e11076c32cb94f3aed7f4d7ad",
    "cpp-library/pipeline-validation/run_aec_denoise.py":
        "f6242f3af34d331996b114d537ebf99ed3d86507508a92003b94dfcca4d17336",
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS: dict[str, str] = {
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Expected identity of external assets.  Nothing here is downloaded, copied,
# imported, loaded or executed by this package.  The model paths are
# machine-checked for absence: if either appears, this package is stale.
EXTERNAL_ASSET_PINS: dict[str, dict[str, Any]] = {
    "asset:full_model": {
        "filename": "localvqe-pi-v1-49k-f32.gguf",
        "expected_path": "data/models/localvqe/localvqe-pi-v1-49k-f32.gguf",
        "sha256": "0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26",
        "present": False,
        "loaded": False,
        "executed": False,
    },
    "asset:echo_model": {
        "filename": "localvqe-pi-aec-v1-49k-f32.gguf",
        "expected_path": "data/models/localvqe/localvqe-pi-aec-v1-49k-f32.gguf",
        "sha256": "b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8",
        "present": False,
        "loaded": False,
        "executed": False,
    },
}

EXTERNAL_RUNTIME_PINS: dict[str, dict[str, Any]] = {
    "asset:native_library": {
        "filename": "liblocalvqe.0.1.0.dylib",
        "expected_path":
            "data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib",
        "sha256": "bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298",
        "loaded": False,
        "executed": False,
        "presence_checked": False,
    },
}

CONFIG: dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "algorithmic_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
    "render_delay_samples": 0,
    "real_runtime": False,
    "model_or_library_used": False,
}

# Frozen truth intervals: half-open sample coordinates.  Every boundary is a
# multiple of 256 samples.  ``path`` names the true render path in the region;
# the surrogate is never told about the secondary path.
SEGMENTS: tuple[dict[str, Any], ...] = (
    {"id": "silence-a", "start": 0, "end": 4608, "ref_amplitude": 0,
     "near_amplitude": 0, "noise_amplitude": 120, "path": "primary",
     "roles": ["silence"]},
    {"id": "echo-only-a", "start": 4608, "end": 15360,
     "ref_amplitude": 28000, "near_amplitude": 0, "noise_amplitude": 90,
     "path": "primary", "roles": ["echo_only"]},
    {"id": "echo-tail-a", "start": 15360, "end": 16384,
     "ref_amplitude": 0, "near_amplitude": 0, "noise_amplitude": 90,
     "path": "primary", "roles": ["render_tail"]},
    {"id": "near-only-quiet", "start": 16384, "end": 18432,
     "ref_amplitude": 0, "near_amplitude": 1500, "noise_amplitude": 140,
     "path": "primary", "roles": ["near_only", "quiet"]},
    {"id": "near-only-a", "start": 18432, "end": 28672,
     "ref_amplitude": 0, "near_amplitude": 22000, "noise_amplitude": 140,
     "path": "primary", "roles": ["near_only"]},
    {"id": "overlap-a", "start": 28672, "end": 39936,
     "ref_amplitude": 26000, "near_amplitude": 18000, "noise_amplitude": 200,
     "path": "primary", "roles": ["overlap"]},
    {"id": "echo-tail-a2", "start": 39936, "end": 40960,
     "ref_amplitude": 0, "near_amplitude": 0, "noise_amplitude": 200,
     "path": "primary", "roles": ["render_tail"]},
    {"id": "echo-only-b-change", "start": 40960, "end": 52736,
     "ref_amplitude": 28000, "near_amplitude": 0, "noise_amplitude": 110,
     "path": "primary_then_secondary", "roles": ["echo_only", "movement"]},
    {"id": "echo-tail-b", "start": 52736, "end": 53248,
     "ref_amplitude": 0, "near_amplitude": 0, "noise_amplitude": 110,
     "path": "secondary", "roles": ["render_tail"]},
    {"id": "overlap-b-noisy", "start": 53248, "end": 60928,
     "ref_amplitude": 24000, "near_amplitude": 16000, "noise_amplitude": 900,
     "path": "secondary", "roles": ["overlap", "noisy"]},
    {"id": "echo-tail-b2", "start": 60928, "end": 61440,
     "ref_amplitude": 0, "near_amplitude": 0, "noise_amplitude": 900,
     "path": "secondary", "roles": ["render_tail"]},
    {"id": "silence-b", "start": 61440, "end": 64000,
     "ref_amplitude": 0, "near_amplitude": 0, "noise_amplitude": 80,
     "path": "primary", "roles": ["silence"]},
)

# The surrogate is built for this frozen primary path only.  The secondary path
# is a movement stressor that the surrogate never adapts to.
PRIMARY_PATH: dict[str, Any] = {
    "delay_samples": 512,
    "taps": (0.55, 0.28, -0.18, 0.10, -0.05),
}
SECONDARY_PATH: dict[str, Any] = {
    "delay_samples": 320,
    "taps": (0.42, -0.22, 0.16, 0.09, 0.04),
}

_WAVE: tuple[int, ...] = tuple(
    int(round(32767.0 * math.sin(2.0 * math.pi * k / 64.0))) for k in range(64)
)
MIX_GAIN = 0.68


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


def path_for_sample(index: int, segment: dict[str, Any]) -> str:
    if segment["path"] == "primary_then_secondary":
        return "primary" if index < MOVEMENT_CHANGE_SAMPLE else "secondary"
    return str(segment["path"])


def _q16(value: float) -> int:
    return max(-32768, min(32767, int(round(value * 32768.0))))


def _wave_sample(index: int, frequency: int, phase: int) -> float:
    phase_acc = (index * frequency * 64 + phase) % (SAMPLE_RATE_HZ * 64)
    table_index = (phase_acc // SAMPLE_RATE_HZ) % 64
    return _WAVE[table_index] / 32768.0


def _build_reference() -> list[float]:
    out: list[float] = []
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        amplitude = segment["ref_amplitude"]
        if amplitude == 0:
            out.append(0.0)
            continue
        # A two-part harmonic source with a slow envelope so the render is not
        # a single stationary tone.
        base = _wave_sample(index, 160, 0)
        high = _wave_sample(index, 320, 11)
        envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * index / 3200.0)
        value = amplitude * envelope * (base + high / 3.0) / 32768.0
        out.append(_q16(value * MIX_GAIN) / 32768.0)
    return out


def _build_near() -> list[float]:
    out: list[float] = []
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        amplitude = segment["near_amplitude"]
        if amplitude == 0:
            out.append(0.0)
            continue
        base = _wave_sample(index, 220, 21)
        high = _wave_sample(index, 440, 5)
        envelope = 0.55 + 0.45 * math.sin(2.0 * math.pi * index / 2400.0)
        value = amplitude * envelope * (base + high / 4.0) / 32768.0
        out.append(_q16(value * MIX_GAIN) / 32768.0)
    return out


def _build_noise() -> list[float]:
    out: list[float] = []
    state = 0x2468ACE1
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        noise = (state >> 16) - 16384
        value = segment["noise_amplitude"] * noise / 32768.0 / 16384.0
        out.append(_q16(value * MIX_GAIN) / 32768.0)
    return out


def _build_echo(ref: list[float]) -> list[float]:
    out: list[float] = []
    for index in range(TOTAL_SAMPLES):
        segment = segment_for_sample(index)
        path = PRIMARY_PATH if path_for_sample(index, segment) == "primary" \
            else SECONDARY_PATH
        delay = int(path["delay_samples"])
        total = 0.0
        for tap_index, tap in enumerate(path["taps"]):
            source = index - delay - tap_index
            if source >= 0:
                total += tap * ref[source]
        out.append(_q16(total) / 32768.0)
    return out


def build_components() -> dict[str, list[float]]:
    """Return the exact frozen decomposition and the microphone mixture."""
    ref = _build_reference()
    near = _build_near()
    noise = _build_noise()
    echo = _build_echo(ref)
    mic = [echo[index] + near[index] + noise[index]
           for index in range(TOTAL_SAMPLES)]
    if any(not math.isfinite(value) for value in mic):
        raise AssertionError("fixture_nonfinite")
    if max(abs(value) for value in mic) > 1.0:
        raise AssertionError(
            "fixture_out_of_range:" + repr(max(abs(value) for value in mic)))
    return {"ref": ref, "near": near, "noise": noise, "echo": echo, "mic": mic}


def build_frames() -> list[dict[str, list[float]]]:
    components = build_components()
    return [
        {
            "mic": components["mic"][index * FRAME_SAMPLES:
                                     (index + 1) * FRAME_SAMPLES],
            "ref": components["ref"][index * FRAME_SAMPLES:
                                     (index + 1) * FRAME_SAMPLES],
        }
        for index in range(TOTAL_FRAMES)
    ]


def stream_digest() -> str:
    components = build_components()
    return sha256_bytes(canonical_bytes({
        key: components[key] for key in ("ref", "echo", "near", "noise", "mic")
    }))


def segment_totals() -> dict[str, int]:
    totals: dict[str, int] = {}
    for segment in SEGMENTS:
        totals[segment["id"]] = segment["end"] - segment["start"]
    return totals


def fixture_spec() -> dict[str, Any]:
    return {
        "fixture_id": "localvqe-compact-full-paired-room-fixture-v1",
        "stream_sha256": stream_digest(),
        "stream_samples": TOTAL_SAMPLES,
        "stream_frames": TOTAL_FRAMES,
        "frame_samples": FRAME_SAMPLES,
        "frame_duration_ms": FRAME_DURATION_MS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "algorithmic_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
        "movement_change_sample": MOVEMENT_CHANGE_SAMPLE,
        "primary_path": {
            "delay_samples": PRIMARY_PATH["delay_samples"],
            "taps": list(PRIMARY_PATH["taps"]),
        },
        "secondary_path": {
            "delay_samples": SECONDARY_PATH["delay_samples"],
            "taps": list(SECONDARY_PATH["taps"]),
        },
        "config": dict(CONFIG),
        "segments": [dict(segment) for segment in SEGMENTS],
        "segment_totals": segment_totals(),
    }


FIXTURE_SPEC_DIGEST = sha256_bytes(canonical_bytes(fixture_spec()))
