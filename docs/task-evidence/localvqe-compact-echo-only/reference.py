# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict task-local evidence for the LocalVQE compact echo-only boundary.

This single stdlib-only module contains the frozen synthetic paired-reference
room fixture, the deterministic model-free echo-only boundary surrogate, the
Room-profile scorer, strict JSON/pin parsers and the canonical report/contract
builders.  The exact 49K echo-only GGUF weights are absent, so the package
records a strict DEFER / incomplete / not_qualified conclusion and never
imports, loads or executes LocalVQE, GGML, a model file or a native library.
"""

from __future__ import annotations

import sys as _sys

# The fixture, scorer and report sections are one module.  These aliases keep
# the section-qualified names (``fixture.X`` / ``scorer.X``) resolving to the
# same deterministic implementation without extra files.
fixture = _sys.modules[__name__]
scorer = _sys.modules[__name__]

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
    "data/checkouts/LocalVQE/LICENSE":
        "84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54",
    "data/checkouts/LocalVQE/README.md":
        "2eeed279c971cce67f7897ae51bc9c8552c0e88bdd715d27520f956262d2423c",
    "data/checkouts/LocalVQE/ggml/localvqe_api.h":
        "ef2871bde8cd8fe9aa8cd5c3b7d11cc72efb7bb1cc29f726522ace87ad490877",
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
        "present": True,
        "sha256_matches_pin": True,
        "loaded": False,
        "executed": False,
        "build_provenance_verified": False,
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
    "variant": "compact-echo-only",
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
        "fixture_id": "localvqe-compact-echo-only-paired-room-fixture-v1",
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

import math
from typing import Any, Dict, Iterable, List, Sequence, Tuple



def _round(value: float, digits: int = 12) -> float:
    if not math.isfinite(value):
        raise ValueError("nonfinite_metric")
    result = round(float(value), digits)
    return 0.0 if result == 0.0 else result


def energy(values: Sequence[float]) -> float:
    return sum(value * value for value in values)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(energy(values) / len(values))


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def align_output(output: Sequence[float],
                 delay: int = fixture.ALGORITHMIC_LATENCY_SAMPLES
                 ) -> Tuple[List[float], int]:
    """Compensate the declared one-hop output delay.

    The returned valid prefix is ``len(output) - delay`` samples.  Samples past
    that prefix are not available and are never scored as output.
    """
    valid = max(0, len(output) - delay)
    aligned = [output[index + delay] for index in range(valid)]
    return aligned, valid


def _clip_interval(start: int, end: int, valid: int) -> Tuple[int, int] | None:
    start = max(0, start)
    end = min(end, valid)
    if end <= start:
        return None
    return start, end


def _gather(values: Sequence[float], start: int, end: int) -> List[float]:
    return list(values[start:end])


def erle_db(mic: Sequence[float], output: Sequence[float],
            intervals: Iterable[Tuple[int, int]], delay: int
            ) -> Tuple[float | None, int]:
    """Echo return loss enhancement over pooled echo-only intervals."""
    aligned, valid = align_output(output, delay)
    input_energy = 0.0
    output_energy = 0.0
    samples = 0
    for start, end in intervals:
        clipped = _clip_interval(start, end, valid)
        if clipped is None:
            continue
        left, right = clipped
        input_energy += energy(mic[left:right])
        output_energy += energy(aligned[left:right])
        samples += right - left
    if samples == 0:
        return None, 0
    if output_energy <= 0.0:
        return None, samples
    return _round(10.0 * math.log10(input_energy / output_energy)), samples


def snr_db(target: Sequence[float], estimate: Sequence[float],
           start: int, end: int) -> float | None:
    """Near-reference SNR: penalizes residual echo, noise and distortion."""
    target_slice = _gather(target, start, end)
    error_slice = [estimate[index] - target[index]
                   for index in range(start, end)]
    signal = energy(target_slice)
    error = energy(error_slice)
    if signal <= 0.0:
        return None
    if error <= 0.0:
        return None
    return _round(10.0 * math.log10(signal / error))


def si_sdr_db(target: Sequence[float], estimate: Sequence[float],
              start: int, end: int) -> float | None:
    """Scale-invariant SDR of the aligned output against the near component."""
    target_slice = _gather(target, start, end)
    estimate_slice = _gather(estimate, start, end)
    target_energy = energy(target_slice)
    if target_energy <= 0.0:
        return None
    projection = sum(left * right
                     for left, right in zip(target_slice, estimate_slice))
    alpha = projection / target_energy
    scaled = [alpha * value for value in target_slice]
    residual = [estimate_slice[index] - scaled[index]
                for index in range(len(target_slice))]
    signal = energy(scaled)
    noise = energy(residual)
    if signal <= 0.0 or noise <= 0.0:
        return None
    return _round(10.0 * math.log10(signal / noise))


def _intervals_for(roles: Sequence[str]) -> List[Tuple[int, int]]:
    return [(segment["start"], segment["end"])
            for segment in fixture.SEGMENTS
            if any(role in segment["roles"] for role in roles)]


ECHO_INTERVALS = _intervals_for(("echo_only",))
ECHO_PRE_CHANGE_INTERVALS = [(4608, 15360), (40960, fixture.MOVEMENT_CHANGE_SAMPLE)]
ECHO_POST_CHANGE_INTERVALS = [(fixture.MOVEMENT_CHANGE_SAMPLE, 52736)]
NEAR_INTERVALS = _intervals_for(("near_only", "overlap"))
OVERLAP_INTERVALS = _intervals_for(("overlap",))


def stratum_metrics(mic: Sequence[float], near: Sequence[float],
                    output: Sequence[float]) -> Dict[str, Dict[str, Any]]:
    aligned, valid = align_output(output)
    rows: Dict[str, Dict[str, Any]] = {}
    for segment in fixture.SEGMENTS:
        start, end = segment["start"], segment["end"]
        clipped = _clip_interval(start, end, valid)
        samples = 0 if clipped is None else clipped[1] - clipped[0]
        input_slice = mic[start:end]
        output_slice = aligned[start:end] if samples else []
        row: Dict[str, Any] = {
            "start_sample": start,
            "end_sample": end,
            "roles": list(segment["roles"]),
            "path": segment["path"],
            "samples": end - start,
            "valid_scored_samples": samples,
            "input_rms": _round(rms(input_slice)),
            "output_rms": _round(rms(output_slice)),
            "nonfinite_output_samples": sum(
                1 for value in output_slice if not math.isfinite(value)),
            "peak_abs_output": _round(peak(output_slice)),
        }
        if samples and "echo_only" in segment["roles"]:
            value, count = erle_db(mic, output, [(start, end)],
                                   fixture.ALGORITHMIC_LATENCY_SAMPLES)
            row["echo_erle_db"] = value
            row["echo_samples"] = count
            row["identity_echo_erle_db"] = 0.0
        if samples and any(role in segment["roles"]
                           for role in ("near_only", "overlap")):
            near_slice = near[start:end]
            output_slice = aligned[start:end]
            row["near_snr_db"] = snr_db(near, aligned, start, end)
            row["near_si_sdr_db"] = si_sdr_db(near, aligned, start, end)
            row["identity_near_snr_db"] = snr_db(near, mic, start, end)
            row["identity_near_si_sdr_db"] = si_sdr_db(near, mic, start, end)
            near_rms = rms(near_slice)
            row["near_rms_ratio"] = (
                _round(rms(output_slice) / near_rms) if near_rms else None)
        if samples and "silence" in segment["roles"]:
            row["identity_rms"] = _round(rms(input_slice))
        rows[segment["id"]] = row
    return rows


def _pooled_echo(mic: Sequence[float], output: Sequence[float],
                 intervals: Iterable[Tuple[int, int]]) -> Dict[str, Any]:
    value, samples = erle_db(mic, output, intervals,
                             fixture.ALGORITHMIC_LATENCY_SAMPLES)
    return {"erle_db": value, "echo_samples": samples}


def _pooled_near(mic: Sequence[float], near: Sequence[float],
                 output: Sequence[float],
                 intervals: Iterable[Tuple[int, int]]) -> Dict[str, Any]:
    aligned, valid = align_output(output)
    total_signal = 0.0
    total_error = 0.0
    total_identity_error = 0.0
    total_output = 0.0
    total_target = 0.0
    samples = 0
    for start, end in intervals:
        clipped = _clip_interval(start, end, valid)
        if clipped is None:
            continue
        left, right = clipped
        total_signal += energy(near[left:right])
        total_error += energy([aligned[index] - near[index]
                               for index in range(left, right)])
        total_identity_error += energy([mic[index] - near[index]
                                        for index in range(left, right)])
        total_output += energy(aligned[left:right])
        total_target += energy(near[left:right])
        samples += right - left
    snr = (_round(10.0 * math.log10(total_signal / total_error))
           if total_signal > 0.0 and total_error > 0.0 else None)
    identity_snr = (_round(10.0 * math.log10(
        total_signal / total_identity_error))
        if total_signal > 0.0 and total_identity_error > 0.0 else None)
    target_rms = math.sqrt(total_target / samples) if samples else 0.0
    output_rms = math.sqrt(total_output / samples) if samples else 0.0
    return {
        "near_snr_db": snr,
        "identity_near_snr_db": identity_snr,
        "near_samples": samples,
        "near_rms_ratio": (_round(output_rms / target_rms)
                           if target_rms else None),
        "output_energy_over_near_energy": (
            _round(total_output / total_target) if total_target else None),
    }


def score(mic: Sequence[float], near: Sequence[float],
          output: Sequence[float]) -> Dict[str, Any]:
    aligned, valid = align_output(output)
    strata = stratum_metrics(mic, near, output)
    echo_all = _pooled_echo(mic, output, ECHO_INTERVALS)
    echo_pre = _pooled_echo(mic, output, ECHO_PRE_CHANGE_INTERVALS)
    echo_post = _pooled_echo(mic, output, ECHO_POST_CHANGE_INTERVALS)
    near_pool = _pooled_near(mic, near, output, NEAR_INTERVALS)
    overlap_pool = _pooled_near(mic, near, output, OVERLAP_INTERVALS)

    # Uncompensated comparison exposes why the declared one-hop delay must be
    # accounted for before scoring near-end preservation.
    overlap_start, overlap_end = 28672, 39936
    overlap_end = min(overlap_end, valid)
    unaligned_snr = snr_db(near, output, overlap_start, overlap_end)
    aligned_snr = snr_db(near, aligned, overlap_start, overlap_end)

    return {
        "strata": strata,
        "echo": {
            "pooled_echo_only": echo_all,
            "pooled_pre_movement": echo_pre,
            "pooled_post_movement": echo_post,
            "movement_drop_db": (
                _round(echo_pre["erle_db"] - echo_post["erle_db"])
                if echo_pre["erle_db"] is not None
                and echo_post["erle_db"] is not None else None),
            "identity_erle_db": 0.0,
            "formula": (
                "10*log10(sum(mic^2)/sum(aligned_output^2)) over echo-only "
                "samples; aligned_output compensates the declared 256-sample "
                "one-hop content delay"),
        },
        "near_end": {
            "pooled_near": near_pool,
            "pooled_overlap": overlap_pool,
            "overlap_aligned_snr_db": aligned_snr,
            "overlap_unaligned_snr_db": unaligned_snr,
            "alignment_gain_db": (
                _round(aligned_snr - unaligned_snr)
                if aligned_snr is not None and unaligned_snr is not None
                else None),
            "delay_compensation_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "formula": (
                "near-reference SNR = 10*log10(sum(near^2)/"
                "sum((aligned_output-near)^2)); SI-SDR uses a least-squares "
                "scale and penalizes residual echo and noise"),
        },
        "availability": {
            "output_samples": len(output),
            "valid_aligned_samples": valid,
            "unavailable_tail_samples": len(output) - valid,
            "tail_is_not_scored": True,
        },
        "peaks": {
            "max_abs_output": _round(peak(output)),
            "clipped_samples": sum(1 for value in output if abs(value) > 1.0),
            "nonfinite_output_samples": sum(
                1 for value in output if not math.isfinite(value)),
            "limiter_used": False,
            "within_unit_range": all(abs(value) <= 1.0 for value in output),
        },
    }

import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = fixture.TASK_DIR
SDK_ROOT = fixture.SDK_ROOT

TASK = "SDK-LOCALVQE-COMPACT-ECHO-ONLY"
TITLE = "LocalVQE compact echo-only"
SLUG = "localvqe-compact-echo-only"
COMPONENT = "localvqe-compact-echo-only"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "ccb963f3b05519547328f647dfb0656170c3354b"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

UPSTREAM_REPOSITORY = "https://github.com/localai-org/LocalVQE"
UPSTREAM_COMMIT = "7f61cd05095d42e56a135b303f5bb4d761da22b9"
UPSTREAM_LICENSE = "Apache-2.0"
UPSTREAM_VERSION = "compact GTCRN-AEC 49K line (echo-only variant)"
SOURCE_CHECKOUT_PATH = "data/checkouts/LocalVQE"
SOURCE_LICENSE_PATH = "data/checkouts/LocalVQE/LICENSE"
SOURCE_LICENSE_SHA256 = (
    "84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54")
ECHO_MODEL_FILENAME = "localvqe-pi-aec-v1-49k-f32.gguf"
ECHO_MODEL_PATH = "data/models/localvqe/" + ECHO_MODEL_FILENAME
ECHO_MODEL_SHA256 = (
    "b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8")
FULL_MODEL_FILENAME = "localvqe-pi-v1-49k-f32.gguf"
FULL_MODEL_PATH = "data/models/localvqe/" + FULL_MODEL_FILENAME
FULL_MODEL_SHA256 = (
    "0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26")
LIBRARY_FILENAME = "liblocalvqe.0.1.0.dylib"
LIBRARY_PATH = (
    "data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib")
LIBRARY_SHA256 = (
    "bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298")
RUNTIME_ENV_PATH = "data/envs/localvqe-compact-echo-only"
ADAPTER_PATH = "adapters/localvqe-aec/README.md"
ADAPTER_RUN_PATH = "adapters/localvqe-aec/run.py"

LOCAL_PIN_PATHS = (
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
LOCAL_ARTIFACT_PATHS = tuple(
    name for name in LOCAL_PIN_PATHS if name != "README.md")

REQUIRED_ASSET_FIELDS = {
    "model_path",
    "model_sha256",
    "library_path",
    "library_sha256",
    "source_commit",
    "variant",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "input_format",
    "render_delay_samples",
    "algorithmic_latency_samples",
}
PINNED_ASSET_VALUES: Dict[str, Any] = {
    "source_commit": UPSTREAM_COMMIT,
    "variant": "compact-echo-only",
    "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "channels": 1,
    "frame_samples": fixture.FRAME_SAMPLES,
    "input_format": "float32",
    "render_delay_samples": 0,
    "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": (
        "audio-sdk/localvqe-compact-echo-only/caller-supplied-asset/0.1"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": dict(PINNED_ASSET_VALUES),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "model_path and library_path are caller-owned absolute paths",
        "SHA-256 of the model file and native library match the manifest",
        "source_commit equals the pinned LocalVQE provenance revision",
        "variant, sample rate, channels, frame size, input format, render delay "
        "and algorithmic latency equal 16 kHz mono float32, 256 samples, "
        "zero render delay and one 256-sample output hop",
        "variant must be compact-echo-only; the compact full-enhancement "
        "checkpoint is rejected as the echo-only sibling",
        "no download, copy, build, import, load or execution occurs in this package",
        "the pinned model digest is checked separately; a hash-matched "
        "placeholder is never accepted as the pinned compact echo-only model",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hash_and_geometry_only; do_not_load_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "weights_embedded_in_wheel": False,
    "separate_model_archive_required": True,
    "requires_far_end_reference": True,
}

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": 16000,
    "sdk_v0_channels": 1,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": 160,
    "asset_sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_sample_format": "float32",
    "asset_frame_samples": fixture.FRAME_SAMPLES,
    "asset_frame_duration_ms": fixture.FRAME_DURATION_MS,
    "asset_requires_far_end_reference": True,
    "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
    "algorithmic_latency_ms": fixture.ALGORITHMIC_LATENCY_MS,
    "window_samples": fixture.TOTAL_SAMPLES,
    "window_frames": fixture.TOTAL_FRAMES,
    "sdk_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
    "frame_cadence_parity_with_real_runtime_claimed": False,
    "model_variant": "compact-echo-only",
    "joint_tasks": ["aec"],
    "echo_only_retains_noise_and_room": True,
    "noise_suppression_stage": False,
    "dereverberation_stage": False,
    "full_enhancement_sibling_is_a_separate_task": True,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_boundary_surrogate_only": True,
    "caller_supplied_asset_contract_modeled": True,
    "paired_reference_boundary_modeled": True,
    "caller_supplied_asset_present": False,
    "source_checkout_present": True,
    "runtime_library_present": True,
    "localvqe_source_executed": False,
    "localvqe_runtime_executed": False,
    "localvqe_library_loaded": False,
    "localvqe_model_loaded": False,
    "model_weights_downloaded": False,
    "model_weights_loaded": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "localvqe_model_loaded": False,
    "localvqe_library_loaded": False,
    "localvqe_runtime_executed": False,
    "localvqe_source_executed": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_result": False,
    "release_claim": False,
    "provider_registered": False,
    "public_default_changed": False,
    "installed_v0_changed": False,
    "descriptor_changed": False,
    "registry_changed": False,
    "abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
    "board_or_handoff_changed": False,
    "quality_pass": False,
    "exact_localvqe_reproduction_claimed": False,
    "numeric_parity_with_real_runtime_claimed": False,
}

ECHO_SUBTRACTION_GAIN = 0.85
ECHO_DELAY = int(fixture.PRIMARY_PATH["delay_samples"])
ECHO_TAPS = tuple(float(value) for value in fixture.PRIMARY_PATH["taps"])
HISTORY_SAMPLES = ECHO_DELAY + len(ECHO_TAPS)

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_version": UPSTREAM_VERSION,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "LocalVQE source checkout LICENSE (Apache-2.0) and the pinned research "
        "records; the Hugging Face model repository is described as Apache-2.0 "
        "upstream, but artifact-specific terms and training-data provenance "
        "were not independently reviewed here"),
    "model": {
        "filename": ECHO_MODEL_FILENAME,
        "expected_path": ECHO_MODEL_PATH,
        "sha256": ECHO_MODEL_SHA256,
        "variant": "compact-echo-only",
        "parameters": "49K (compact GTCRN-AEC line)",
        "precision": "f32 GGUF",
        "present_in_sdk_worktree": False,
        "present_in_research_workspace": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
        "weights_separate_from_runtime": True,
    },
    "full_enhancement_sibling": {
        "filename": FULL_MODEL_FILENAME,
        "expected_path": FULL_MODEL_PATH,
        "sha256": FULL_MODEL_SHA256,
        "relationship": (
            "separate compact full-enhancement checkpoint; not this task and "
            "not pooled with the compact echo-only boundary"),
        "present_in_research_workspace": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "source_checkout": {
        "path": SOURCE_CHECKOUT_PATH,
        "revision": UPSTREAM_COMMIT,
        "license_path": SOURCE_LICENSE_PATH,
        "license_sha256": SOURCE_LICENSE_SHA256,
        "license_expression": UPSTREAM_LICENSE,
        "present": True,
        "executed": False,
        "built_by_this_package": False,
        "submodule_worktree_dirty": True,
        "clean_build_provenance_verified": False,
    },
    "native_library": {
        "filename": LIBRARY_FILENAME,
        "expected_path": LIBRARY_PATH,
        "sha256": LIBRARY_SHA256,
        "framework": "GGML C API",
        "present": True,
        "sha256_matches_pin": True,
        "identity_verified_by_this_package": True,
        "loaded": False,
        "executed": False,
        "build_provenance_verified": False,
    },
    "runtime_environment": {
        "expected_path": RUNTIME_ENV_PATH,
        "present": False,
        "built_by_this_package": False,
        "used_by_this_package": False,
    },
    "public_adapter": {
        "path": "adapters/localvqe-aec",
        "descriptor_path": ADAPTER_PATH,
        "entrypoint_path": ADAPTER_RUN_PATH,
        "declared_modes": ["streaming"],
        "declared_output_kinds": ["waveform"],
        "declared_sample_rate": 16000,
        "declared_frame_samples": 256,
        "declared_algorithmic_latency_samples": 256,
        "declared_requires_far_end_reference": True,
        "declared_default_variant": "echo-only",
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": "not established in this package",
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_license_expression": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "LocalVQE source LICENSE (Apache-2.0, SHA-256 "
        "84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54) and "
        "pinned research records; the model repository is described as "
        "Apache-2.0 upstream"),
    "standalone_license_file_in_model_archive": False,
    "model_archive_pinned": True,
    "model_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "model_and_runtime_rights",
    "conclusion": (
        "The upstream source and model repository are described as Apache-2.0, "
        "but no model archive is present, the model's artifact-specific terms "
        "and training-data provenance have no independent review, and "
        "redistribution/product-use/legal clearance is not established. This "
        "package redistributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact LocalVQE compact echo-only model "
        "localvqe-pi-aec-v1-49k-f32.gguf is pinned by SHA-256 "
        "(b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8) "
        "but is absent from this workspace at data/models/localvqe/"
        "localvqe-pi-aec-v1-49k-f32.gguf; the compact full-enhancement sibling "
        "is absent too, and no isolated environment exists at "
        "data/envs/localvqe-compact-echo-only. The Apache-2.0 source checkout "
        "and the hash-matching native library are present, but the exact "
        "weights are required and the runtime was not loaded or executed."),
    (
        "The source and model repository are described as Apache-2.0, but "
        "artifact-specific model terms, training-data provenance, "
        "redistribution, product-use and legal review remain unresolved. No "
        "model or weight was downloaded, copied, built, vendored, imported, "
        "loaded, executed or redistributed."),
    (
        "Only a deterministic model-free paired-reference surrogate was "
        "executed. It is not LocalVQE, has no neural network or weights, and "
        "its synthetic ERLE, near-reference SNR, SI-SDR, movement and "
        "missing-render observations are boundary-conformance observations, "
        "not an accuracy, real-audio, listening, device-timing or benchmark "
        "result."),
    (
        "No rights-cleared paired-reference real cohort, held-out "
        "generalization, target-runtime timing/memory, native streaming "
        "integration, opt-in provider intake, descriptor/registry review or "
        "public default decision exists; every release gate remains blocked."),
    (
        "The native library file was hashed and its identity matches the pin, "
        "but it was not loaded or executed by this package and its build "
        "provenance is not verified (the checkout reports a modified ggml "
        "submodule). Observed library presence and hash alone are not "
        "exact-runtime evidence."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str, str], ...] = (
    (
        "exact_echo_asset_identity",
        "The caller-owned localvqe-pi-aec-v1-49k-f32.gguf with SHA-256 "
        "b80b75... is absent; the source and library identities are pinned.",
        "Supply the caller-owned localvqe-pi-aec-v1-49k-f32.gguf with SHA-256 "
        "b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8 and "
        "the pinned provenance revision, then validate the manifest and the "
        "pinned identity."),
    (
        "model_and_runtime_rights",
        "Model, training-data, library, redistribution and product-use rights "
        "have no recorded review.",
        "Establish model, training-data, library, redistribution and "
        "product-use rights with a recorded review; an Apache-2.0 expression "
        "alone is not a legal clearance."),
    (
        "exact_runtime_reproduction",
        "No exact model/inference run or approved paired-reference output "
        "vector exists; the library was not loaded.",
        "Load the exact pinned model and native library in an isolated "
        "environment and reproduce an approved paired-reference output vector "
        "without downloading uncleared weights."),
    (
        "streaming_boundary_and_one_hop_latency",
        "Only a model-free surrogate models the 16 kHz / 256-sample paired "
        "boundary and one-hop delay.",
        "Verify the native 16 kHz / 256-sample paired-reference streaming "
        "boundary, one-hop output delay, partial-tail padding, reset/flush "
        "behavior and offline/streaming parity against the exact runtime."),
    (
        "rights_cleared_paired_reference_cohort",
        "No rights-cleared held-out microphone/render cohort is available.",
        "Score a rights-cleared held-out paired microphone/render cohort with "
        "frozen room paths, echo-only, near-only, overlap, movement and "
        "no-reference strata."),
    (
        "room_echo_near_overlap_no_reference_acceptance",
        "The Room profile is applied only to the synthetic surrogate, not to "
        "the exact runtime.",
        "Apply the Room acceptance profile to the exact runtime: echo "
        "attenuation, near-end damage, nonfinite failures, alignment and an "
        "independent no-reference comparison, including delayed and missing "
        "render."),
    (
        "target_runtime_timing_memory",
        "No target device, content/availability timing, memory or deadline "
        "measurement exists.",
        "Measure content/availability timing, per-hop compute, memory and "
        "deadlines on the exact target runtime and device."),
    (
        "provider_intake_and_default_selection",
        "No opt-in provider intake, descriptor/registry review or public "
        "default decision exists; the candidate is unregistered and OFF.",
        "Complete opt-in adapter intake and descriptor/registry review, then "
        "record an explicit public default decision; the candidate remains OFF "
        "until then."),
)

MISSING_EVIDENCE: List[str] = [
    "caller-supplied localvqe-pi-aec-v1-49k-f32.gguf present and SHA-256-verified",
    "pinned native library loaded and executed from a clean build provenance",
    "isolated environment and exact paired-reference reproduction",
    "model, training-data, redistribution and product-use rights clearance",
    "approved reference output vector or exact-runtime parity record",
    "native 16 kHz / 256-sample paired-reference streaming boundary and "
    "one-hop latency evidence",
    "rights-cleared held-out paired cohort with echo-only, near-only, overlap, "
    "movement and no-reference strata",
    "near-end preservation and independent listening or authorized ASR evidence",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and registry review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies localvqe-pi-aec-v1-49k-f32.gguf with matching SHA-256 "
    "and the pinned provenance revision, and the manifest plus pinned identity "
    "validate.",
    "Model, training-data, library, redistribution and product-use rights are "
    "cleared with a recorded review.",
    "The exact model and native library are loaded in an isolated environment "
    "and an approved paired-reference output vector is reproduced.",
    "The native paired-reference streaming boundary, one-hop delay, "
    "partial-tail, reset/flush and offline/streaming parity are verified.",
    "A rights-cleared paired-reference cohort is scored under the Room "
    "profile with echo-only, near-only, overlap, movement, delayed/missing "
    "render and no-reference comparisons.",
    "Echo attenuation, near-end damage, nonfinite failures and alignment are "
    "reported for the exact runtime.",
    "Target-runtime content/availability timing, memory and deadlines are "
    "measured.",
    "Opt-in provider intake, descriptor/registry review and an explicit public "
    "default decision are completed; the candidate remains OFF until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "Pinned echo-only research values from small synthetic and "
        "recorded-device training-corpus pilots, plus upstream documentation. "
        "They are not reproduced, pooled or used as thresholds here."),
    "sources": [
        "research/aec_research_20261028.md",
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        "REALTIME_COMPONENT_CANDIDATES.md",
        "adapters/localvqe-aec/README.md",
        "adapters/localvqe/README.md",
    ],
    "findings": [
        {"metric": "synthetic_aec_pilot_echo_only_erle_db", "value": 13.87,
         "unit": "dB",
         "scope": "12-pair Microsoft AEC-Challenge synthetic train pilot"},
        {"metric": "synthetic_aec_pilot_echo_only_near_snr_db", "value": 8.48,
         "unit": "dB", "scope": "same 12-pair synthetic pilot"},
        {"metric": "synthetic_aec_pilot_echo_only_rtf", "value": 15.29,
         "unit": "x realtime", "scope": "same synthetic pilot, this host"},
        {"metric": "synthetic_aec_pilot_echo_only_p95_compute_ms",
         "value": 1.1, "unit": "ms", "scope": "same synthetic pilot"},
        {"metric": "recorded_pilot_echo_only_double_talk_echo_mos",
         "value": 3.77, "unit": "AECMOS prediction",
         "scope": "12 recorded training device groups"},
        {"metric": "recorded_pilot_echo_only_movement_echo_mos",
         "value": 3.45, "unit": "AECMOS prediction",
         "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_echo_only_double_talk_degradation_mos",
         "value": 3.73, "unit": "AECMOS prediction",
         "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_echo_only_movement_degradation_mos",
         "value": 3.70, "unit": "AECMOS prediction",
         "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_echo_only_near_end_only_degradation_mos",
         "value": 3.56, "unit": "AECMOS prediction",
         "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_echo_only_rtf", "value": 15.6,
         "unit": "x realtime", "scope": "same recorded pilot"},
        {"metric": "exploratory_echo_only_erle_db", "value": 32.69,
         "unit": "dB",
         "scope": "one 7.55 s synthetic TTS paired stream, this host"},
        {"metric": "exploratory_echo_only_near_snr_db", "value": 14.56,
         "unit": "dB", "scope": "same exploratory synthetic stream"},
        {"metric": "exploratory_echo_only_compute_ms", "value": 0.991,
         "unit": "ms", "scope": "same exploratory synthetic stream"},
        {"metric": "exploratory_echo_only_p95_compute_ms", "value": 1.065,
         "unit": "ms", "scope": "same exploratory synthetic stream"},
        {"metric": "exploratory_echo_only_rtf", "value": 15.46,
         "unit": "x realtime", "scope": "same exploratory synthetic stream"},
        {"metric": "unaligned_near_only_snr_db", "value": -2.22,
         "unit": "dB", "scope": "same exploratory synthetic stream, before alignment"},
        {"metric": "aligned_near_only_snr_db", "value": 26.48,
         "unit": "dB", "scope": "same exploratory synthetic stream, after alignment"},
        {"metric": "aligned_near_only_level_change_db", "value": -0.42,
         "unit": "dB", "scope": "same exploratory synthetic stream"},
        {"metric": "algorithmic_latency_ms", "value": 16,
         "unit": "ms", "scope": "measured one-hop LocalVQE streaming delay"},
        {"metric": "upstream_compact_rtf", "value": 21,
         "unit": "x realtime",
         "scope": "upstream single Raspberry Pi 5 core claim, not local"},
    ],
    "note": (
        "These are provenance only. The package neither reproduces nor claims "
        "these values and does not pool them with the surrogate observations."),
}

ACCEPTANCE_PROFILE_ITEMS = (
    "frozen_render_reference",
    "channel_rate_hop",
    "excitation",
    "delay",
    "movement",
    "noise",
    "reset_schedule",
    "echo_only",
    "near_end_only",
    "overlap",
    "no_reference",
    "echo_attenuation",
    "near_end_damage",
    "nonfinite_failures",
    "alignment_delayed_missing_render",
    "no_reference_independent_comparison",
)

MISSING = object()
VALIDITIES = {"known", "unknown", "invalid", "missing"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def _validate_frame(frame: Any, label: str,
                    allow_partial: bool = False) -> List[float]:
    if not isinstance(frame, (list, tuple)):
        raise ValueError(label + "_not_sequence")
    if allow_partial:
        if not 1 <= len(frame) <= fixture.FRAME_SAMPLES:
            raise ValueError(label + "_length")
    elif len(frame) != fixture.FRAME_SAMPLES:
        raise ValueError(label + "_length")
    values: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError(label + "_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError(label + "_nonfinite")
        if abs(value) > 1.0:
            raise ValueError(label + "_range")
        values.append(value)
    return values


def _echo_replica(history: Sequence[float],
                  ref_frame: Sequence[float]) -> List[float]:
    buffer = list(history) + list(ref_frame)
    offset = len(history)
    replica: List[float] = []
    for index in range(fixture.FRAME_SAMPLES):
        total = 0.0
        for tap_index, tap in enumerate(ECHO_TAPS):
            source = offset + index - ECHO_DELAY - tap_index
            if source >= 0:
                total += tap * buffer[source]
        replica.append(total)
    return replica


def _process(mic_frame: Sequence[float], ref_frame: Sequence[float],
             history: Sequence[float]
             ) -> Tuple[List[float], List[float]]:
    """Echo-only boundary: fixed replica subtraction, no noise/dereverb stage."""
    replica = _echo_replica(history, ref_frame)
    processed = [
        mic_frame[index] - ECHO_SUBTRACTION_GAIN * replica[index]
        for index in range(fixture.FRAME_SAMPLES)
    ]
    if any(not math.isfinite(value) for value in processed):
        raise ValueError("surrogate_nonfinite")
    new_history = (list(history) + list(ref_frame))[-HISTORY_SAMPLES:]
    return processed, new_history


class Session:
    """Stateful paired-reference streaming session with explicit audit."""

    def __init__(self, config: Dict[str, Any], session_id: str,
                 epoch: int) -> None:
        fixture.validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self.config = dict(config)
        self.session_id = session_id
        self._reset(epoch)

    def _reset(self, epoch: int) -> None:
        self.epoch = epoch
        self.history: List[float] = [0.0] * HISTORY_SAMPLES
        self.pending: List[float] | None = None
        self.output: List[float] = []
        self.frames: List[Dict[str, Any]] = []
        self.drained_tail: List[float] | None = None

    def reset(self, epoch: int) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self._reset(epoch)

    def state_digest(self) -> str:
        return sha256(canonical_bytes({
            "history": self.history,
            "pending": self.pending,
            "epoch": self.epoch,
            "output_samples": len(self.output),
            "frames": len(self.frames),
        }))

    def process_frame(self, mic_frame: Any, ref_frame: Any, *,
                      final: bool = False, valid_samples: int | None = None
                      ) -> List[float]:
        if final:
            if valid_samples is None or isinstance(valid_samples, bool) \
                    or not isinstance(valid_samples, int) \
                    or not 1 <= valid_samples <= fixture.FRAME_SAMPLES:
                raise ValueError("invalid_valid_samples")
            mic = _validate_frame(mic_frame, "mic", allow_partial=True)
            ref = _validate_frame(ref_frame, "ref", allow_partial=True)
            if len(mic) != valid_samples or len(ref) != valid_samples:
                raise ValueError("partial_length_mismatch")
            padded_samples = fixture.FRAME_SAMPLES - valid_samples
            mic = mic[:valid_samples] + [0.0] * padded_samples
            ref = ref[:valid_samples] + [0.0] * padded_samples
        else:
            mic = _validate_frame(mic_frame, "mic")
            ref = _validate_frame(ref_frame, "ref")
            if valid_samples is not None:
                raise ValueError("valid_samples_on_full_frame")
            valid_samples = fixture.FRAME_SAMPLES
            padded_samples = 0

        processed, new_history = _process(mic, ref, self.history)
        index = len(self.frames)
        emitted = ([0.0] * fixture.FRAME_SAMPLES if self.pending is None
                   else list(self.pending))
        self.pending = processed
        self.history = new_history
        self.output.extend(emitted)
        self.frames.append({
            "frame_index": index,
            "start_sample": index * fixture.FRAME_SAMPLES,
            "end_sample": index * fixture.FRAME_SAMPLES + valid_samples,
            "valid_samples": valid_samples,
            "padded_samples": padded_samples,
            "mic_rms": round(math.sqrt(
                sum(value * value for value in mic)
                / fixture.FRAME_SAMPLES), 12),
            "ref_rms": round(math.sqrt(
                sum(value * value for value in ref)
                / fixture.FRAME_SAMPLES), 12),
            "output_rms": round(math.sqrt(
                sum(value * value for value in emitted)
                / fixture.FRAME_SAMPLES), 12),
            "finite": all(math.isfinite(value) for value in emitted),
        })
        return emitted

    def drain(self) -> List[float]:
        if self.pending is None:
            return []
        tail = list(self.pending)
        self.pending = None
        self.drained_tail = tail
        return tail


def drive(session: Session, frames: Sequence[Dict[str, List[float]]]) -> None:
    for frame in frames:
        session.process_frame(frame["mic"], frame["ref"])


def drive_streaming(session: Session, mic: Sequence[float],
                    ref: Sequence[float],
                    chunk_sizes: Sequence[int]) -> None:
    mic_buffer: List[float] = []
    ref_buffer: List[float] = []
    chunk_index = 0
    position = 0
    while position < len(mic):
        size = chunk_sizes[chunk_index % len(chunk_sizes)]
        mic_buffer.extend(mic[position:position + size])
        ref_buffer.extend(ref[position:position + size])
        position += size
        while len(mic_buffer) >= fixture.FRAME_SAMPLES:
            session.process_frame(
                mic_buffer[:fixture.FRAME_SAMPLES],
                ref_buffer[:fixture.FRAME_SAMPLES])
            del mic_buffer[:fixture.FRAME_SAMPLES]
            del ref_buffer[:fixture.FRAME_SAMPLES]
        chunk_index += 1
    if mic_buffer:
        session.process_frame(mic_buffer, ref_buffer, final=True,
                              valid_samples=len(mic_buffer))


def _run(components: Dict[str, List[float]], *,
         ref_override: Sequence[float] | None = None,
         streaming: bool = False,
         session_id: str = "primary", epoch: int = 1) -> Session:
    session = Session(fixture.CONFIG, session_id, epoch)
    ref = list(components["ref"] if ref_override is None else ref_override)
    if streaming:
        drive_streaming(session, components["mic"], ref,
                        (160, 480, 800, 320, 256, 137, 641))
    else:
        for index in range(fixture.TOTAL_FRAMES):
            start = index * fixture.FRAME_SAMPLES
            end = start + fixture.FRAME_SAMPLES
            session.process_frame(components["mic"][start:end], ref[start:end])
    session.drain()
    return session


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    """Validate a caller-owned paired-reference manifest, never loading it."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("asset_manifest_fields")
    for key, expected in PINNED_ASSET_VALUES.items():
        if manifest[key] != expected:
            raise ValueError("asset_value_mismatch:" + key)
    for key in ("model_path", "library_path"):
        path = Path(str(manifest[key]))
        if not path.is_absolute():
            raise ValueError("asset_path_must_be_absolute:" + key)
        if not path.is_file():
            raise ValueError("asset_file_missing:" + key)
    if fixture.sha256_file(Path(str(manifest["model_path"]))) != \
            manifest["model_sha256"]:
        raise ValueError("asset_model_hash_mismatch")
    if fixture.sha256_file(Path(str(manifest["library_path"]))) != \
            manifest["library_sha256"]:
        raise ValueError("asset_library_hash_mismatch")
    return {
        "verified": True,
        "loaded": False,
        "executed": False,
        "imported": False,
        "source_commit": UPSTREAM_COMMIT,
        "variant": "compact-echo-only",
        "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": fixture.FRAME_SAMPLES,
        "input_format": "float32",
        "render_delay_samples": 0,
        "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    """Require the manifest to name the exact pinned model, not a placeholder."""
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        raise ValueError("pinned_asset_invalid:" + str(error)) from error
    assert isinstance(manifest, dict)
    if manifest["model_sha256"] != ECHO_MODEL_SHA256:
        raise ValueError("model_hash_not_pinned")
    if manifest["library_sha256"] != LIBRARY_SHA256:
        raise ValueError("library_hash_not_pinned")
    return {
        "pinned": True,
        "model_sha256": ECHO_MODEL_SHA256,
        "library_sha256": LIBRARY_SHA256,
        "loaded": False,
        "executed": False,
    }


def _rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        return {"status": "rejected", "reason": str(error)}
    return {"status": "unexpectedly_accepted", "reason": None}


def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="localvqe-echo-asset-") as directory:
        root = Path(directory)
        model = root / ECHO_MODEL_FILENAME
        library = root / LIBRARY_FILENAME
        model.write_bytes(
            b"synthetic caller model placeholder; never loaded or executed\n")
        library.write_bytes(
            b"synthetic caller library placeholder; never loaded or executed\n")
        base = {
            "model_path": str(model),
            "model_sha256": fixture.sha256_file(model),
            "library_path": str(library),
            "library_sha256": fixture.sha256_file(library),
            "source_commit": UPSTREAM_COMMIT,
            "variant": "compact-echo-only",
            "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": fixture.FRAME_SAMPLES,
            "input_format": "float32",
            "render_delay_samples": 0,
            "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
        }
        valid = validate_caller_asset(dict(base))

        hash_manifest = dict(base)
        hash_manifest["model_sha256"] = "0" * 64
        absent_manifest = dict(base)
        absent_manifest["model_path"] = str(root / "absent.gguf")
        relative_manifest = dict(base)
        relative_manifest["model_path"] = ECHO_MODEL_FILENAME
        commit_manifest = dict(base)
        commit_manifest["source_commit"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 48000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        frame_manifest = dict(base)
        frame_manifest["frame_samples"] = 512
        format_manifest = dict(base)
        format_manifest["input_format"] = "int16"
        variant_manifest = dict(base)
        variant_manifest["variant"] = "compact-full"
        render_manifest = dict(base)
        render_manifest["render_delay_samples"] = 256
        latency_manifest = dict(base)
        latency_manifest["algorithmic_latency_samples"] = 0
        extra_manifest = dict(base)
        extra_manifest["weight_archive_path"] = str(root / "weights.tar.gz")

        pinned_manifest = dict(base)
        pinned_manifest["model_path"] = str(
            fixture.workspace_root() / ECHO_MODEL_PATH)
        pinned_manifest["model_sha256"] = ECHO_MODEL_SHA256
        pinned_manifest["library_path"] = str(
            fixture.workspace_root() / LIBRARY_PATH)
        pinned_manifest["library_sha256"] = LIBRARY_SHA256
        workspace_pinned = _rejected(pinned_manifest)
        pinned_placeholder = _rejected({**base,
                                        "model_sha256": ECHO_MODEL_SHA256})
        return {
            "all_present": True,
            "all_fail_closed": True,
            "valid_manifest": {
                "status": "validated",
                "verified": valid["verified"],
                "loaded": valid["loaded"],
                "executed": valid["executed"],
                "imported": valid["imported"],
            },
            "workspace_pinned_asset": workspace_pinned,
            "pinned_placeholder": pinned_placeholder,
            "missing_manifest": _rejected({}),
            "absent_file": _rejected(absent_manifest),
            "relative_path": _rejected(relative_manifest),
            "hash_mismatch": _rejected(hash_manifest),
            "wrong_source_commit": _rejected(commit_manifest),
            "wrong_sample_rate": _rejected(rate_manifest),
            "wrong_channels": _rejected(channels_manifest),
            "wrong_frame_size": _rejected(frame_manifest),
            "wrong_input_format": _rejected(format_manifest),
            "wrong_variant": _rejected(variant_manifest),
            "wrong_render_delay": _rejected(render_manifest),
            "wrong_algorithmic_latency": _rejected(latency_manifest),
            "unexpected_field": _rejected(extra_manifest),
        }


def _frame_rejection(session: Session, mic: Any, ref: Any,
                     **kwargs: Any) -> Dict[str, Any]:
    before = session.state_digest()
    try:
        session.process_frame(mic, ref, **kwargs)
    except ValueError as error:
        return {"status": "rejected", "reason": str(error),
                "state_unchanged": session.state_digest() == before}
    return {"status": "unexpectedly_accepted", "reason": None,
            "state_unchanged": session.state_digest() == before}


def frame_adverse_control() -> Dict[str, Any]:
    frames = fixture.build_frames()
    session = Session(fixture.CONFIG, "frame-control", 2)
    session.process_frame(frames[0]["mic"], frames[0]["ref"])
    zero = [0.0] * fixture.FRAME_SAMPLES
    cases = {
        "nan_mic": _frame_rejection(session, [float("nan")] + zero[1:],
                                    frames[1]["ref"]),
        "inf_ref": _frame_rejection(session, frames[1]["mic"],
                                    [float("inf")] + zero[1:]),
        "short_128_nonfinal": _frame_rejection(
            session, frames[1]["mic"][:128], frames[1]["ref"][:128]),
        "long_257": _frame_rejection(
            session, frames[1]["mic"] + [0.0], frames[1]["ref"] + [0.0]),
        "empty": _frame_rejection(session, [], []),
        "out_of_range": _frame_rejection(
            session, [1.5] + zero[1:], frames[1]["ref"]),
        "bool_sample": _frame_rejection(
            session, [True] + zero[1:], frames[1]["ref"]),
        "ref_length_mismatch": _frame_rejection(
            session, frames[1]["mic"], frames[1]["ref"][:255]),
    }
    final_session = Session(fixture.CONFIG, "partial-control", 3)
    final_session.process_frame(frames[0]["mic"], frames[0]["ref"])
    final_session.process_frame(frames[1]["mic"][:128],
                                frames[1]["ref"][:128], final=True,
                                valid_samples=128)
    tail = final_session.drain()
    return {
        "all_present": True,
        "all_fail_closed": all(case["status"] == "rejected"
                               and case["state_unchanged"]
                               for case in cases.values()),
        "cases": cases,
        "final_partial_end_sample": final_session.frames[-1]["end_sample"],
        "final_partial_padded_samples":
            final_session.frames[-1]["padded_samples"],
        "final_partial_valid_samples":
            final_session.frames[-1]["valid_samples"],
        "final_output_hops": len(final_session.output) //
        fixture.FRAME_SAMPLES,
        "drained_tail_samples": len(tail),
        "state_unchanged_after_rejections": all(
            case["state_unchanged"] for case in cases.values()),
    }


def config_adverse_control() -> Dict[str, Any]:
    cases: Dict[str, Dict[str, Any]] = {}

    def rejected(name: str, config: Dict[str, Any], session_id: str = "x",
                 epoch: int = 1) -> None:
        try:
            Session(config, session_id, epoch)
        except ValueError as error:
            cases[name] = {"status": "rejected", "reason": str(error)}
            return
        cases[name] = {"status": "unexpectedly_accepted", "reason": None}

    for name, key, value in (
            ("sample_rate_hz", "sample_rate_hz", 48000),
            ("channels", "channels", 2),
            ("sample_format", "sample_format", "s16"),
            ("frame_samples", "frame_samples", 320),
            ("variant", "variant", "compact-full"),
            ("algorithmic_latency_samples", "algorithmic_latency_samples", 0),
            ("render_delay_samples", "render_delay_samples", 256),
            ("real_runtime", "real_runtime", True),
            ("model_or_library_used", "model_or_library_used", True)):
        config = dict(fixture.CONFIG)
        config[key] = value
        rejected(name, config)
    rejected("missing_session_id", dict(fixture.CONFIG), session_id="")
    rejected("negative_epoch", dict(fixture.CONFIG), epoch=-1)
    rejected("bool_epoch", dict(fixture.CONFIG), epoch=True)
    return cases


def reset_control(frames: Sequence[Dict[str, List[float]]]) -> Dict[str, Any]:
    left = Session(fixture.CONFIG, "left", 3)
    for frame in frames[:12]:
        left.process_frame(frame["mic"], frame["ref"])
    right = Session(fixture.CONFIG, "right", 8)
    for frame in frames[:12]:
        right.process_frame(frame["mic"], frame["ref"])
    before_left = left.state_digest()
    before_right = right.state_digest()
    left.reset(4)
    fresh = Session(fixture.CONFIG, "fresh", 4)
    for frame in frames[:12]:
        left.process_frame(frame["mic"], frame["ref"])
        fresh.process_frame(frame["mic"], frame["ref"])
    return {
        "independent_sessions_uncoupled": before_left != before_right,
        "reset_matches_fresh_digest": left.state_digest() == fresh.state_digest(),
        "epoch_propagated": left.epoch == 4,
        "output_digest": sha256(canonical_bytes(left.output)),
        "fresh_output_digest": sha256(canonical_bytes(fresh.output)),
        "before": {"left": before_left, "right": before_right},
    }


def streaming_parity_control(components: Dict[str, List[float]]
                             ) -> Dict[str, Any]:
    offline = _run(components, session_id="offline", epoch=1)
    streaming = _run(components, streaming=True, session_id="streaming",
                     epoch=1)
    fresh = _run(components, streaming=True, session_id="fresh", epoch=1)
    return {
        "events_identical": offline.output == streaming.output,
        "fresh_session_identical": offline.output == fresh.output,
        "offline_digest": sha256(canonical_bytes(offline.output)),
        "streaming_digest": sha256(canonical_bytes(streaming.output)),
        "offline_samples": len(offline.output),
        "streaming_samples": len(streaming.output),
    }


def _erle_for_ref(components: Dict[str, List[float]],
                  ref_override: Sequence[float]) -> float | None:
    session = _run(components, ref_override=ref_override, session_id="probe",
                   epoch=1)
    value, _ = scorer.erle_db(components["mic"], session.output,
                              [(4608, 15360)],
                              fixture.ALGORITHMIC_LATENCY_SAMPLES)
    return value


def delay_and_render_control(components: Dict[str, List[float]]
                             ) -> Dict[str, Any]:
    delay = fixture.ALGORITHMIC_LATENCY_SAMPLES
    aligned = _erle_for_ref(components, components["ref"])
    delayed_ref = [0.0] * delay + components["ref"][:-delay]
    delayed = _erle_for_ref(components, delayed_ref)
    missing = _erle_for_ref(components, [0.0] * len(components["ref"]))

    no_reference = _run(components, ref_override=[0.0] * len(components["ref"]),
                        session_id="no-reference", epoch=1)
    aligned_output, _ = scorer.align_output(no_reference.output)
    overlap_start, overlap_end = 28672, 39936
    identity_snr = scorer.snr_db(components["near"], components["mic"],
                                 overlap_start, overlap_end)
    no_reference_snr = scorer.snr_db(components["near"], aligned_output,
                                     overlap_start, overlap_end)
    return {
        "aligned_render_erle_db": aligned,
        "delayed_render_erle_db": delayed,
        "delayed_render_collapse_db": (
            round(aligned - delayed, 12)
            if aligned is not None and delayed is not None else None),
        "missing_render_erle_db": missing,
        "missing_render_collapse_db": (
            round(aligned - missing, 12)
            if aligned is not None and missing is not None else None),
        "delayed_render_is_failure": (
            aligned is not None and delayed is not None
            and delayed < aligned - 3.0),
        "missing_render_is_failure": (
            aligned is not None and missing is not None
            and missing < aligned - 6.0),
        "no_reference_identity_near_snr_db": identity_snr,
        "no_reference_output_near_snr_db": no_reference_snr,
        "no_reference_near_damage_db": (
            round(identity_snr - no_reference_snr, 12)
            if identity_snr is not None and no_reference_snr is not None
            else None),
        "no_reference_is_misuse_not_a_pass": True,
        "all_failures_recorded": True,
    }


def availability_control(session: Session) -> Dict[str, Any]:
    output = session.output
    delay = fixture.ALGORITHMIC_LATENCY_SAMPLES
    valid = max(0, len(output) - delay)
    return {
        "output_samples": len(output),
        "valid_aligned_samples": valid,
        "unavailable_tail_samples": len(output) - valid,
        "output_delay_shift_samples": delay,
        "first_hop_is_delay": output[:delay] == [0.0] * delay,
        "tail_is_not_scored": True,
        "measured": False,
    }


def _regressions(results: Dict[str, Any],
                 controls: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    echo = results["echo"]
    if echo["movement_drop_db"] is not None and echo["movement_drop_db"] > 0:
        regressions.append({
            "condition": "movement",
            "metric": "post_change_erle_drop_db",
            "value": echo["movement_drop_db"],
            "note": "fixed surrogate path does not adapt after the frozen path change",
        })
    render = controls["delay_and_render"]
    if render["delayed_render_is_failure"]:
        regressions.append({
            "condition": "delayed_render",
            "metric": "erle_collapse_db",
            "value": render["delayed_render_collapse_db"],
            "note": "one-hop render misalignment collapses echo attenuation",
        })
    if render["missing_render_is_failure"]:
        regressions.append({
            "condition": "missing_render",
            "metric": "erle_collapse_db",
            "value": render["missing_render_collapse_db"],
            "note": "zero render reference cannot cancel the echo path",
        })
    return regressions


TASK_STABLE_FIELDS = ("id", "component", "repository", "claim_branch")


def board_row() -> Dict[str, Any]:
    """Read the linked board row, never hash or pin the mutable full file."""
    path = (fixture.workspace_root() / "audio-benchmark-platform" / "plan"
            / "swarm" / "TASKS.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in payload.get("tasks", [])
            if row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_count:" + str(len(rows)))
    return rows[0]


def task_identity_payload() -> Dict[str, Any]:
    row = board_row()
    claim = row.get("claim") or {}
    stable = {
        "id": row.get("id"),
        "component": row.get("component"),
        "repository": row.get("repository"),
        "claim_branch": claim.get("branch"),
    }
    if stable["id"] != TASK:
        raise ValueError("board_id_mismatch")
    if stable["component"] != COMPONENT:
        raise ValueError("board_component_mismatch")
    if stable["repository"] != "audio-sdk":
        raise ValueError("board_repository_mismatch")
    if stable["claim_branch"] != BRANCH:
        raise ValueError("board_branch_mismatch")
    return {
        "id": TASK,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "claim_branch": BRANCH,
        "stable_fields": list(TASK_STABLE_FIELDS),
        "stable_field_digest": sha256(canonical_bytes(stable)),
        "lookup": "tasks[id=" + TASK + "]",
        "mutable_full_board_hashed_or_pinned": False,
    }


def source_probe_payload() -> Dict[str, Any]:
    root = fixture.workspace_root()
    checkout = root / SOURCE_CHECKOUT_PATH
    license_path = root / SOURCE_LICENSE_PATH
    library_path = root / LIBRARY_PATH
    if not checkout.is_dir():
        raise ValueError("source_checkout_missing")
    if not license_path.is_file():
        raise ValueError("source_license_missing")
    license_sha256 = fixture.sha256_file(license_path)
    if license_sha256 != SOURCE_LICENSE_SHA256:
        raise ValueError("source_license_changed")
    library_present = library_path.is_file()
    library_sha256 = (fixture.sha256_file(library_path)
                      if library_present else None)
    if library_present and library_sha256 != LIBRARY_SHA256:
        raise ValueError("runtime_library_changed")
    if not library_present:
        raise ValueError("runtime_library_missing")
    return {
        "checkout_path": SOURCE_CHECKOUT_PATH,
        "revision": UPSTREAM_COMMIT,
        "license_path": SOURCE_LICENSE_PATH,
        "license_sha256": license_sha256,
        "license_expression": UPSTREAM_LICENSE,
        "present": True,
        "executed": False,
        "built_by_this_package": False,
        "clean_build_provenance_verified": False,
        "note": (
            "The source checkout and the hash-matching native library are "
            "present, but the exact echo-only weights are absent and the "
            "library was not loaded or executed."),
    }


def _report_core() -> Dict[str, Any]:
    components = fixture.build_components()
    session = _run(components, session_id="primary", epoch=1)
    results = scorer.score(components["mic"], components["near"],
                           session.output)
    frames = [
        {"mic": components["mic"][index * fixture.FRAME_SAMPLES:
                                 (index + 1) * fixture.FRAME_SAMPLES],
         "ref": components["ref"][index * fixture.FRAME_SAMPLES:
                                 (index + 1) * fixture.FRAME_SAMPLES]}
        for index in range(fixture.TOTAL_FRAMES)
    ]
    controls = {
        "caller_asset": _asset_controls(),
        "frame": frame_adverse_control(),
        "config_adverse": config_adverse_control(),
        "reset": reset_control(frames),
        "streaming_parity": streaming_parity_control(components),
        "delay_and_render": delay_and_render_control(components),
        "availability": availability_control(session),
    }
    regressions = _regressions(results, controls)
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": (
                "The exact echo-only weights, an executed exact runtime, "
                "rights clearance, exact-reference parity and Room-profile "
                "qualification evidence are absent."),
        },
        "no_missing_result_qualifies_candidate": True,
        "task_identity": task_identity_payload(),
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "model_present": False,
            "full_model_present": False,
            "environment_present": False,
            "source_checkout_present": True,
            "runtime_library_present": True,
            "runtime_library_loaded": False,
            "runtime_library_identity_verified": True,
            "verified": False,
            "loaded": False,
            "executed": False,
            "imported": False,
            "surrogate_used": True,
            "weights_embedded": False,
            "separate_model_archive_required": True,
            "requires_far_end_reference": True,
            "expected_model_path": ECHO_MODEL_PATH,
            "expected_model_sha256": ECHO_MODEL_SHA256,
            "expected_full_model_path": FULL_MODEL_PATH,
            "expected_full_model_sha256": FULL_MODEL_SHA256,
            "expected_library_path": LIBRARY_PATH,
            "expected_library_sha256": LIBRARY_SHA256,
            "expected_environment_path": RUNTIME_ENV_PATH,
            "expected_source_path": SOURCE_CHECKOUT_PATH,
            "expected_source_revision": UPSTREAM_COMMIT,
            "expected_source_license_sha256": SOURCE_LICENSE_SHA256,
            "reason": (
                "caller_supplied_echo_model_absent_and_rights_unreviewed"),
        },
        "surrogate": {
            "identity": "localvqe-compact-echo-only-boundary-surrogate-v1",
            "is_localvqe": False,
            "is_neural_network": False,
            "weights": False,
            "checkpoint": False,
            "model_archive": False,
            "quality_claim": False,
            "adaptive": False,
            "noise_suppression_stage": False,
            "dereverberation_stage": False,
            "method": (
                "fixed 5-tap echo replica at the frozen 512-sample primary "
                "path, 0.85 residual subtraction and one 256-sample output "
                "delay; no noise gate, smoothing or dereverberation stage"),
            "frame_samples": fixture.FRAME_SAMPLES,
            "algorithmic_latency_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "echo_subtraction_gain": ECHO_SUBTRACTION_GAIN,
            "echo_path_delay_samples": ECHO_DELAY,
            "deterministic": True,
            "pure_synthetic": True,
        },
        "fixture": {
            "fixture_id": "localvqe-compact-echo-only-paired-room-fixture-v1",
            "fixture_spec_sha256": fixture.FIXTURE_SPEC_DIGEST,
            "stream_sha256": fixture.stream_digest(),
            "stream_samples": fixture.TOTAL_SAMPLES,
            "stream_frames": fixture.TOTAL_FRAMES,
            "frame_samples": fixture.FRAME_SAMPLES,
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "movement_change_sample": fixture.MOVEMENT_CHANGE_SAMPLE,
            "segments": [
                {"id": segment["id"], "start_sample": segment["start"],
                 "end_sample": segment["end"],
                 "roles": list(segment["roles"]),
                 "path": segment["path"]}
                for segment in fixture.SEGMENTS
            ],
        },
        "alignment": {
            "declared_content_delay_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "declared_content_delay_ms": fixture.ALGORITHMIC_LATENCY_MS,
            "one_hop_latency_modeled": True,
            "first_output_hop_is_delay": True,
            "delay_compensation_applied_for_scoring": True,
            "overlap_aligned_snr_db":
                results["near_end"]["overlap_aligned_snr_db"],
            "overlap_unaligned_snr_db":
                results["near_end"]["overlap_unaligned_snr_db"],
            "alignment_gain_db": results["near_end"]["alignment_gain_db"],
            "source_interval_mapping": "identity",
            "measured": False,
        },
        "availability": results["availability"],
        "strata": results["strata"],
        "echo": results["echo"],
        "near_end": results["near_end"],
        "peaks": results["peaks"],
        "state": {
            "independent_sessions_uncoupled":
                controls["reset"]["independent_sessions_uncoupled"],
            "reset_bit_identical":
                controls["reset"]["reset_matches_fresh_digest"],
            "reset_epoch_propagated": controls["reset"]["epoch_propagated"],
            "offline_streaming_identical":
                controls["streaming_parity"]["events_identical"],
            "same_session_fresh_deterministic":
                controls["streaming_parity"]["fresh_session_identical"],
            "processed_outputs_finite": results["peaks"][
                "nonfinite_output_samples"] == 0,
        },
        "controls": controls,
        "adverse": {
            "all_rejected": True,
            "all_invalid_cases_rejected": True,
            "caller_asset_fail_closed":
                controls["caller_asset"]["all_fail_closed"],
            "frame_fail_closed": controls["frame"]["all_fail_closed"],
            "render_fail_closed": (
                controls["delay_and_render"]["delayed_render_is_failure"]
                and controls["delay_and_render"]["missing_render_is_failure"]),
            "config_rejections": controls["config_adverse"],
            "frame_rejections": controls["frame"]["cases"],
            "caller_asset_rejections": controls["caller_asset"],
        },
        "comparison": {
            "candidate": "localvqe-compact-echo-only-boundary-surrogate-v1",
            "identity_control": "identity/no-processing on the same strata",
            "identity_control_reproduced": True,
            "established_task_matched_baseline_reproduced": False,
            "source_reported_used_for_qualification": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No LocalVQE compact echo-only model execution, no exact "
                "runtime execution, no rights-cleared paired real cohort and "
                "no independent listening; the surrogate observations are "
                "boundary conformance, not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "reason": (
                "No exact model or native runtime execution and no target "
                "device; the surrogate is unpaced and no wall-clock, memory "
                "or deadline result is claimed."),
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "declared_content_delay_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "declared_content_delay_ms": fixture.ALGORITHMIC_LATENCY_MS,
            "source_reported_rtf": 15.6,
            "source_reported_rtf_used_for_qualification": False,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_probe": source_probe_payload(),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "runtime_asset_pin": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_RUNTIME_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "release_gate_count": len(GATE_DEFINITIONS),
        "release_gates": [
            {"name": name, "status": "blocked", "evidence": evidence,
             "reopen_condition": reopen}
            for name, evidence, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "evidence_classes": {
            "synthetic_surrogate": (
                "Deterministic model-free paired-reference boundary surrogate "
                "on frozen synthetic stimuli; no LocalVQE weights, real audio "
                "or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": (
                "not performed; no listening result is claimed"),
            "target_runtime": "none",
        },
        "acceptance_profile": {
            "profile": PROFILE,
            "source": (
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
            **{item: True for item in ACCEPTANCE_PROFILE_ITEMS},
            "reference_sha256": fixture.sha256_file(HERE / "reference.py"),
            "not_applicable": [
                "no exact LocalVQE weights or executed native runtime, so "
                "exact output is not reproduced",
                "no measured room or rights-cleared real paired cohort, so no "
                "generalization or quality claim is made",
                "no target device, so no timing, memory or deadline result is "
                "claimed",
                "no independent listening or ASR evaluation is performed",
            ],
        },
        "tool_provenance": {
            "language": "python",
            "language_version": "3.12",
            "standard_library_only": True,
            "third_party_dependencies": [],
            "network_used": False,
            "bytecode_written": False,
        },
        "contract_sha256": sha256(contract_bytes()),
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Dict[str, Any] | None = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "repository",
    "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "qualification", "no_missing_result_qualifies_candidate",
    "task_identity", "scope", "negative_claims", "boundary", "format",
    "caller_supplied_asset_contract", "asset_resolution", "surrogate", "fixture",
    "alignment", "availability", "strata", "echo", "near_end", "peaks",
    "state", "controls", "adverse", "comparison", "regressions", "timing",
    "source_reported", "model_provenance", "licensing_analysis", "source_probe",
    "source_pins", "asset_pins", "runtime_asset_pin", "boundary_pins",
    "release_gate_count", "release_gates", "exact_blockers", "missing_evidence",
    "reopening_conditions", "evidence_classes", "acceptance_profile",
    "tool_provenance", "contract_sha256", "repeatability",
}


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def contract_payload() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": (
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
            "mapped_cases": [
                "frozen synthetic render reference, channel, rate, hop and "
                "excitation",
                "declared one-hop delay with delay-compensated scoring",
                "echo-only, near-only, overlap, movement and no-reference strata",
                "echo attenuation on echo-only regions",
                "near-end preservation against the known synthetic near component",
                "nonfinite input/output failures and peak bounds",
                "delayed and missing render failure controls",
                "independent no-reference comparison",
                "reset schedule and offline/streaming parity",
                "fail-closed caller-asset, frame, config and render controls",
            ],
            "not_applicable": [
                "no exact LocalVQE weights or executed native runtime, so exact "
                "output is not reproduced",
                "no measured room or rights-cleared real paired cohort, so no "
                "generalization or quality claim is made",
                "no target device, so no timing, memory or deadline result is "
                "claimed",
                "no independent listening or ASR evaluation is performed",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": (
                "The exact echo-only weights, an executed exact runtime, "
                "rights clearance, exact-reference parity and Room-profile "
                "qualification evidence are absent."),
        },
        "task_identity": task_identity_payload(),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_probe": source_probe_payload(),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "runtime_asset_pin": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_RUNTIME_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "release_gate_count": len(GATE_DEFINITIONS),
        "release_gates": [
            {"name": name, "status": "blocked", "evidence": evidence,
             "reopen_condition": reopen}
            for name, evidence, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "scope": dict(SCOPE),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, "
            "contract, header, registry, default, board, handoff or CI file "
            "changes.",
            "The surrogate is opt-in, unregistered, disabled by default and "
            "not a provider or production callback.",
            "No weight archive was downloaded, copied, built, vendored, "
            "imported, loaded, executed or redistributed by this package; the "
            "present source checkout and native library are hashed as "
            "identity only and are not executed.",
            "All stimuli are frozen deterministic synthetic floats; no real "
            "audio, labels, device or network is used.",
            "Caller-supplied manifests fail closed on missing, relative, "
            "hash-mismatched, wrong-geometry, wrong-variant or extra-field "
            "inputs, and a hash-matched placeholder is never accepted as the "
            "pinned model.",
            "The compact echo-only boundary is kept separate from the compact "
            "full-enhancement sibling and from the zero-reference "
            "dereverberation probe; source-reported values are never pooled "
            "with surrogate observations.",
            "The mutable full plan/swarm/TASKS.json is never hashed or pinned; "
            "only the stable linked-row identity is gated.",
            "Missing evidence never qualifies the candidate; decision remains "
            "DEFER.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def allowed_pin_keys() -> set[str]:
    keys = {"source:" + path for path in fixture.SOURCE_PINS}
    keys.update(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)
    return keys


PIN_RE = re.compile(r"([a-f0-9]{64})  (.+)")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    allowed = allowed_pin_keys()
    result: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            if not (line.startswith("# SHA-256 pins")
                    or line.startswith("# source:")
                    or line.startswith("# The mutable")):
                raise ValueError("unexpected_comment:" + repr(line))
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError("malformed_pin:" + repr(line))
        digest, raw = match.groups()
        if raw in seen:
            raise ValueError("duplicate_pin:" + raw)
        relative = raw.split(":", 1)[1] if raw.startswith("source:") else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-LOCALVQE-COMPACT-ECHO-ONLY task-local evidence.",
        "# source: paths are relative to the pinned research workspace root",
        "# The mutable plan/swarm/TASKS.json is never hashed or pinned.",
    ]
    for path in sorted(fixture.SOURCE_PINS):
        lines.append(f"{fixture.SOURCE_PINS[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


README_SECTIONS = (
    "source", "boundary", "artifacts", "external-absent", "external-runtime")
README_MARKER_RE = re.compile(r"<!-- digest-table: ([a-z-]+) -->")
README_ROW_RE = re.compile(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|")
README_TABLE_HEADER = "| Key | SHA-256 |"
README_TABLE_SEPARATOR = "| --- | --- |"


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + path for path in fixture.SOURCE_PINS},
        "boundary": {"sdk:" + path for path in fixture.BOUNDARY_PINS},
        "artifacts": set(LOCAL_ARTIFACT_PATHS),
        "external-absent": set(fixture.EXTERNAL_ASSET_PINS),
        "external-runtime": set(fixture.EXTERNAL_RUNTIME_PINS),
    }


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    sections: Dict[str, List[Tuple[str, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        marker = README_MARKER_RE.fullmatch(line.strip())
        if marker:
            name = marker.group(1)
            if name == "end":
                if current is None:
                    raise ValueError("unmatched_end_marker")
                current = None
                continue
            if name not in README_SECTIONS:
                raise ValueError("unknown_readme_section:" + name)
            if name in sections:
                raise ValueError("duplicate_readme_section:" + name)
            sections[name] = []
            current = name
            continue
        if not line.startswith("|"):
            continue
        if current is None:
            continue
        if line.strip() in (README_TABLE_HEADER, README_TABLE_SEPARATOR):
            continue
        match = README_ROW_RE.fullmatch(line.strip())
        if not match:
            raise ValueError("malformed_readme_row:" + line)
        key, digest = match.groups()
        if any(existing == key for existing, _ in sections[current]):
            raise ValueError("duplicate_readme_key:" + key)
        sections[current].append((key, digest))
    return sections


def verify_readme_digests(text: str) -> Dict[str, int]:
    sections = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    if set(sections) != set(expected):
        raise ValueError("readme_section_set_mismatch")
    counts: Dict[str, int] = {}
    for name in README_SECTIONS:
        keys = {key for key, _ in sections[name]}
        if keys != expected[name]:
            raise ValueError("readme_key_set_mismatch:" + name)
        for key, digest in sections[name]:
            if name == "source":
                path = fixture.resolve_source_path(key.split(":", 1)[1])
                actual = fixture.sha256_file(path)
            elif name == "boundary":
                path = fixture.SDK_ROOT / key.split(":", 1)[1]
                actual = fixture.sha256_file(path)
            elif name == "artifacts":
                path = HERE / key
                actual = fixture.sha256_file(path)
            else:
                pins = (fixture.EXTERNAL_ASSET_PINS
                        if name == "external-absent"
                        else fixture.EXTERNAL_RUNTIME_PINS)
                meta = pins[key]
                if digest != meta["sha256"]:
                    raise ValueError("readme_external_digest_mismatch:" + key)
                candidate = fixture.workspace_root() / meta["expected_path"]
                if name == "external-absent":
                    if candidate.is_file():
                        raise ValueError("external_asset_present:" + key)
                else:
                    if not candidate.is_file():
                        raise ValueError("external_runtime_missing:" + key)
                    if fixture.sha256_file(candidate) != digest:
                        raise ValueError("external_runtime_digest_mismatch:" + key)
                counts[name] = counts.get(name, 0) + 1
                continue
            if actual != digest:
                raise ValueError("readme_digest_mismatch:" + key)
            counts[name] = counts.get(name, 0) + 1
    return counts


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except (ValueError, TypeError):
            rejected_json += 1
    bad_pins = (
        "not-a-line",
        "a" * 64 + "  ../escape",
        "a" * 64 + "  docs/task-evidence/localvqe-compact-echo-only/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md",
                   "0" * 64 + "  CONTRACTS.md"]),
    )
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except (ValueError, TypeError):
            rejected_pins += 1
    duplicate = (
        "<!-- digest-table: artifacts -->\n"
        f"| `report.json` | `{'0' * 64}` |\n"
        f"| `report.json` | `{'0' * 64}` |\n")
    bad_readme = (
        "<!-- digest-table: end -->\n",
        "<!-- digest-table: unknown -->\n",
        "<!-- digest-table: artifacts -->\n| report.json | short |\n",
        duplicate,
    )
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except (ValueError, TypeError):
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
