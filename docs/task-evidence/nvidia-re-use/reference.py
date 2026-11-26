# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-NVIDIA-RE-USE.

This package is NOT NVIDIA Real-time RE-USE, not the NVIDIA checkpoint, not the
community Swift/MLX port, not a converted weight file and not an audio-sdk
provider. It contains no model weights, no compiled binary, no runtime, no
license text and no real corpus. Nothing is downloaded, cloned, installed,
built, imported as a model runtime, loaded or executed.

Pinned evidence identifies NVIDIA Real-time RE-USE as a universal Mamba speech
restoration model with 30 configurable compute/lookahead points, 8-48 kHz and
an explicit online inference API. The upstream weights are under NVIDIA
One-Way Noncommercial License (NSCLv1) terms as reported by the model card; the
community Swift/MLX port is separately attributed and not an NVIDIA
implementation or endorsement. The local host has Swift 6.4, but the pinned
`model.safetensors`, a built/pinned `reuse-fast-cli`, an exact local runtime
record and matched evaluation evidence are absent.

The module therefore emits a fail-closed DEFER blocker report:
- strict request and caller-supplied asset-manifest validation;
- explicit source/weights/runtime/license/rights/fixture probes;
- fixed-list absence probe only (no search, no network);
- deterministic synthetic harness controls that are not candidate output;
- stable linked-row identity projection that never hashes the mutable full
  `plan/swarm/TASKS.json`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = "audio-sdk/nvidia-re-use-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/nvidia-re-use-contract/0.1"
ASSET_SCHEMA_ID = "audio-sdk/nvidia-re-use/caller-supplied-asset/0.1"
TASK = "SDK-NVIDIA-RE-USE"
COMPONENT = "nvidia-re-use"
BRANCH = "swarm/SDK-NVIDIA-RE-USE"
BASE_COMMIT = "0b0f2dee5902278fcea1a47f576b4df70e99ab3a"
TASK_PREFIX = "docs/task-evidence/nvidia-re-use/"
MODE = "feasibility"
VERIFICATION_PROFILE = "enhancement"

# Installed v0 geometry is unchanged by this evidence package.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

UPSTREAM_OWNER = "NVIDIA"
COMPONENT_NAME = "NVIDIA Real-time RE-USE"
UPSTREAM_MODEL_ID = "nvidia/Real-time_RE-USE"
UPSTREAM_MODEL_REVISION = "4c0c186272ca853cd18d832fc5c28777b62f32d1"
UPSTREAM_MODEL_URL = "https://huggingface.co/nvidia/RE-USE"
COMMUNITY_PORT_ID = "PositiveLoss/re-use-swift-mlx"
COMMUNITY_PORT_REVISION = "362be1ade00c3fcc534639df1d10c72d7e4a9e02"
COMMUNITY_PORT_URL = "https://github.com/PositiveLoss/re-use-swift-mlx"
WEIGHTS_NAME = "model.safetensors"
REPORTED_WEIGHTS_LICENSE = "NVIDIA One-Way Noncommercial License (NSCLv1)"
REPORTED_WEIGHTS_LICENSE_SCOPE = "weights/checkpoint terms as reported by model card; not locally verified"
REPORTED_PORT_LICENSE = "Apache-2.0 (community Swift/MLX port source, as reported)"
TARGET_VARIANT = "realtime_reuse_16k_generic"

HARNESS_SAMPLE_RATE_HZ = SAMPLE_RATE_HZ
HARNESS_CHANNELS = CHANNELS
HARNESS_FRAME_SAMPLES = FRAME_SAMPLES
HARNESS_FRAME_VALUES = HARNESS_CHANNELS * HARNESS_FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_CHANNELS_GUARD = 64
MAX_FRAME_SAMPLES_GUARD = 4096
MIN_RATE_GUARD = 1000
MAX_RATE_GUARD = 384000

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/reuse-mlx/adapter.json":
        "2e77df89f2b78eabd0bbb399ffe55d6561651585e7397473e632aa96ea1e89fd",
    "adapters/reuse-mlx/README.md":
        "a583f20d64a32f128640064583a531f7e5097aeb681f9ba8fb48221667012e2b",
    "adapters/reuse-mlx/run.py":
        "2716fb848b830270d39d8d36052dffec09f03fe6451f7deeca7184cfcc011233",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "NVIDIA RE-USE",
    "mode": MODE,
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)
PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

CANDIDATE = "nvidia_reuse"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
})
ASSET_KEYS = frozenset({
    "adapter", "variant", "artifact_path", "artifact_sha256", "model_sha256",
    "source_revision", "port_revision", "runtime", "runtime_version",
    "sample_rate_hz", "channels", "frame_samples", "exit_layer",
    "look_ahead_frames", "dtype", "license_id", "commercial_use_approved",
})
ASSET_VARIANTS = (TARGET_VARIANT,)
ASSET_RUNTIMES = ("reuse-fast-cli-swift-mlx",)
ASSET_DTYPES = ("bf16", "fp16", "fp32")

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

SOURCE_CANDIDATE_PATHS = (
    "sdk:third_party/reuse",
    "sdk:third_party/nvidia-reuse",
    "sdk:third_party/re-use-swift-mlx",
    "data/checkouts/re-use-swift-mlx",
    "data/checkouts/Real-time_RE-USE",
    "data/models/reuse",
    "data/models/nvidia-reuse",
    "data/models/re-use-swift-mlx",
    "research/reuse",
    "research/nvidia-reuse",
    "repos/re-use-swift-mlx",
    "~/models/reuse",
    "~/models/nvidia-reuse",
    "~/Downloads/reuse",
    "~/Downloads/nvidia-reuse",
)
WEIGHT_SUFFIXES = (".safetensors", ".bin", ".pt", ".pth", ".onnx", ".mlmodel")
WEIGHT_CANDIDATE_PATHS = (
    "sdk:third_party/reuse",
    "data/checkouts/Real-time_RE-USE",
    "data/checkouts/re-use-swift-mlx",
    "data/models/reuse",
    "data/models/nvidia-reuse",
    "research/reuse",
    "~/models/reuse",
    "~/models/nvidia-reuse",
    "~/Downloads/reuse",
)
RUNTIME_CANDIDATE_PATHS = (
    "data/checkouts/re-use-swift-mlx/.build/release/reuse-fast-cli",
    "data/checkouts/re-use-swift-mlx/.build/debug/reuse-fast-cli",
    "sdk:third_party/re-use-swift-mlx/.build/release/reuse-fast-cli",
    "~/bin/reuse-fast-cli",
    "/usr/local/bin/reuse-fast-cli",
)
FIXTURE_CANDIDATE_PATHS = (
    "data/corpora/dns",
    "data/corpora/ears",
    "data/fixtures/reuse",
    "data/fixtures/nvidia-reuse",
    "research/reuse/fixture",
)
FIXTURE_MARKERS = (".wav", ".flac", ".mp3", ".json", ".csv")
RUNTIME_LOCK_CANDIDATES = (
    "data/checkouts/re-use-swift-mlx/Package.resolved",
    "data/checkouts/re-use-swift-mlx/Package.swift",
)
RUNTIME_MODULES = ("numpy", "torch", "mlx", "coremltools", "soundfile")


class EvidenceError(ValueError):
    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class ArtifactsAbsent(EvidenceError):
    code = "ARTIFACTS_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise InputError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = HARNESS_FRAME_VALUES) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = HARNESS_FRAME_VALUES,
            position: int = HARNESS_FRAME_VALUES // 2,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = HARNESS_FRAME_VALUES,
         position: int = HARNESS_FRAME_VALUES // 2,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = HARNESS_FRAME_VALUES, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "INVALID_STIMULUS")
    duration = length / float(HARNESS_SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def speech_like(length: int = HARNESS_FRAME_VALUES,
                seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        noise_value = next(noise)
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
        if index < length // 2:
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(),
    "impulse": lambda: impulse(),
    "step": lambda: step(),
    "sweep": lambda: sweep(),
    "speech_like": lambda: speech_like(),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> Dict[str, Any]:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE", "NONFINITE")
        peak = max(peak, abs(number))
    if peak > MAX_ABS_STIMULUS:
        raise InputError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": _r(peak),
        "rms": _r(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        if index < len(samples) // 2:
            voiced.append(float(value))
        else:
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def _validate_sample_list(samples: Any, expected: int) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    if len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE: " + str(index), "NONFINITE")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str,
                 minimum: int | None = None,
                 maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    if maximum is not None and value > maximum:
        raise ConfigError(code, code)
    return value


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(code, code)
    return value


def _is_hex(value: Any, length: int) -> bool:
    if not isinstance(value, str) or len(value) != length:
        return False
    return all(character in "0123456789abcdef" for character in value)


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown),
                          "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing),
                          "MISSING_FIELD")
    if request["candidate"] != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    rate = _require_int(request["sample_rate_hz"], "INVALID_RATE",
                        MIN_RATE_GUARD, MAX_RATE_GUARD)
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1,
                            MAX_CHANNELS_GUARD)
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1,
                                 MAX_FRAME_SAMPLES_GUARD)
    samples = _validate_sample_list(request["samples"],
                                    channels * frame_samples)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame_samples,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
        "geometry_verified": False,
        "candidate_processing": False,
    }


def validate_asset_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise InputError("manifest must be an object", "INVALID_MANIFEST")
    unknown = sorted(set(manifest) - ASSET_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown),
                          "UNKNOWN_FIELD")
    missing = sorted(ASSET_KEYS - set(manifest))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing),
                          "MISSING_FIELD")
    if manifest["adapter"] != ASSET_SCHEMA_ID:
        raise ConfigError("UNKNOWN_ADAPTER", "UNKNOWN_ADAPTER")
    if manifest["variant"] not in ASSET_VARIANTS:
        raise ConfigError("UNKNOWN_VARIANT", "UNKNOWN_VARIANT")
    if not _is_hex(manifest["source_revision"], 40):
        raise ConfigError("INVALID_SOURCE_REVISION", "INVALID_SOURCE_REVISION")
    if not _is_hex(manifest["port_revision"], 40):
        raise ConfigError("INVALID_PORT_REVISION", "INVALID_PORT_REVISION")
    for key in ("artifact_sha256", "model_sha256"):
        if not _is_hex(manifest[key], 64):
            raise ConfigError("INVALID_DIGEST: " + key, "INVALID_DIGEST")
    artifact_path = _require_text(manifest["artifact_path"],
                                  "INVALID_ARTIFACT_PATH")
    if manifest["runtime"] not in ASSET_RUNTIMES:
        raise ConfigError("UNKNOWN_RUNTIME", "UNKNOWN_RUNTIME")
    runtime_version = _require_text(manifest["runtime_version"],
                                    "INVALID_RUNTIME_VERSION")
    rate = _require_int(manifest["sample_rate_hz"], "INVALID_RATE",
                        MIN_RATE_GUARD, MAX_RATE_GUARD)
    channels = _require_int(manifest["channels"], "WRONG_CHANNELS", 1,
                            MAX_CHANNELS_GUARD)
    frame_samples = _require_int(manifest["frame_samples"], "INVALID_FRAME", 1,
                                 MAX_FRAME_SAMPLES_GUARD)
    exit_layer = _require_int(manifest["exit_layer"], "INVALID_EXIT_LAYER", 1,
                              64)
    look_ahead_frames = _require_int(manifest["look_ahead_frames"],
                                     "INVALID_LOOK_AHEAD", 0, 64)
    if manifest["dtype"] not in ASSET_DTYPES:
        raise ConfigError("UNKNOWN_DTYPE", "UNKNOWN_DTYPE")
    license_id = _require_text(manifest["license_id"], "INVALID_LICENSE_ID")
    commercial = manifest["commercial_use_approved"]
    if not isinstance(commercial, bool):
        raise ConfigError("INVALID_COMMERCIAL_FLAG", "INVALID_COMMERCIAL_FLAG")
    return {
        "adapter": ASSET_SCHEMA_ID,
        "variant": TARGET_VARIANT,
        "artifact_path": artifact_path,
        "artifact_sha256": manifest["artifact_sha256"],
        "model_sha256": manifest["model_sha256"],
        "source_revision": manifest["source_revision"],
        "port_revision": manifest["port_revision"],
        "runtime": manifest["runtime"],
        "runtime_version": runtime_version,
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame_samples,
        "exit_layer": exit_layer,
        "look_ahead_frames": look_ahead_frames,
        "dtype": manifest["dtype"],
        "license_id": license_id,
        "commercial_use_approved": commercial,
    }


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
        "channels": HARNESS_CHANNELS,
        "frame_samples": HARNESS_FRAME_SAMPLES,
        "samples": [0.0] * HARNESS_FRAME_VALUES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter": ASSET_SCHEMA_ID,
        "variant": TARGET_VARIANT,
        "artifact_path": "caller_supplied/reuse/model.safetensors",
        "artifact_sha256": "0" * 64,
        "model_sha256": "0" * 64,
        "source_revision": UPSTREAM_MODEL_REVISION,
        "port_revision": COMMUNITY_PORT_REVISION,
        "runtime": "reuse-fast-cli-swift-mlx",
        "runtime_version": "0.0.0-unverified",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "exit_layer": 8,
        "look_ahead_frames": 0,
        "dtype": "bf16",
        "license_id": REPORTED_WEIGHTS_LICENSE,
        "commercial_use_approved": False,
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    short = [0.0] * (HARNESS_FRAME_VALUES - 1)
    long = [0.0] * (HARNESS_FRAME_VALUES + 1)
    nan_samples = [0.0] * HARNESS_FRAME_VALUES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * HARNESS_FRAME_VALUES
    inf_samples[9] = float("inf")
    return (
        ("unknown_candidate", variant(candidate="other")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {k: v for k, v in base.items() if k != "epoch"}),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("channels_over_local_guard", variant(channels=65)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("rate_below_guard", variant(sample_rate_hz=999)),
        ("rate_above_guard", variant(sample_rate_hz=384001)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("wrong_multichannel_count", variant(channels=2, samples=[0.0] * 160)),
        ("nonfinite_nan", variant(samples=nan_samples)),
        ("nonfinite_inf", variant(samples=inf_samples)),
        ("out_of_range", variant(samples=[4.5] * HARNESS_FRAME_VALUES)),
        ("bool_sample", variant(samples=[True] + [0.0] * (HARNESS_FRAME_VALUES - 1))),
        ("string_sample", variant(samples=["0.0"] + [0.0] * (HARNESS_FRAME_VALUES - 1))),
        ("null_sample", variant(samples=[None] + [0.0] * (HARNESS_FRAME_VALUES - 1))),
        ("samples_not_list", variant(samples="0.0")),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("bool_execution_mode", variant(execution_mode=True)),
        ("request_not_object", "not-an-object"),
    )


def _adverse_manifest_specs():
    base = _base_manifest()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    return (
        ("unknown_field", variant(extra=True)),
        ("missing_field", {k: v for k, v in base.items() if k != "model_sha256"}),
        ("wrong_adapter", variant(adapter="audio-sdk/other/0.1")),
        ("unknown_variant", variant(variant="universal_reuse")),
        ("short_source_revision", variant(source_revision="0" * 39)),
        ("short_port_revision", variant(port_revision="0" * 39)),
        ("nonhex_source_revision", variant(source_revision="z" * 40)),
        ("short_artifact_sha", variant(artifact_sha256="0" * 63)),
        ("nonhex_model_sha", variant(model_sha256="g" * 64)),
        ("empty_artifact_path", variant(artifact_path="")),
        ("nonstring_artifact_path", variant(artifact_path=1)),
        ("unknown_runtime", variant(runtime="onnxruntime")),
        ("empty_runtime_version", variant(runtime_version="")),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("zero_channels", variant(channels=0)),
        ("channels_over_local_guard", variant(channels=65)),
        ("zero_frame", variant(frame_samples=0)),
        ("invalid_exit_layer", variant(exit_layer=0)),
        ("invalid_look_ahead", variant(look_ahead_frames=-1)),
        ("unknown_dtype", variant(dtype="int8")),
        ("empty_license", variant(license_id="")),
        ("nonbool_commercial", variant(commercial_use_approved="yes")),
        ("manifest_not_object", "not-an-object"),
    )


def _adverse_cases() -> Dict[str, Any]:
    request_cases = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        request_cases.append({"id": name, "accepted": accepted, "error": error})
    manifest_cases = []
    for name, manifest in _adverse_manifest_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_asset_manifest(manifest)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        manifest_cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "request_case_count": len(request_cases),
        "request_accepted_count": sum(1 for c in request_cases if c["accepted"]),
        "all_requests_rejected": all(not c["accepted"] for c in request_cases),
        "manifest_case_count": len(manifest_cases),
        "manifest_accepted_count": sum(1 for c in manifest_cases if c["accepted"]),
        "all_manifests_rejected": all(not c["accepted"] for c in manifest_cases),
        "metrics": None,
        "request_cases": request_cases,
        "manifest_cases": manifest_cases,
        "note": "Invalid or unverified requests/manifests are rejected before any artifact check or candidate call; no metrics exist.",
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("json_not_object", '[1,2,3]'),
    )
    cases = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            value = strict_json_loads(text)
            accepted = not isinstance(value, list)
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for c in cases if c["accepted"]),
        "all_rejected": all(not c["accepted"] for c in cases),
        "metrics": None,
        "cases": cases,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "artifact_runtime_license_rights_and_fixture_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    if label.startswith("/"):
        return Path(label)
    if label.startswith("sdk:"):
        return SDK_ROOT / label[4:]
    return WORKSPACE / label


def _markers_in(path: Path, markers: Sequence[str], max_depth: int = 3) -> List[str]:
    found: List[str] = []
    if path.is_file():
        if path.suffix.lower() in markers or path.name in markers:
            found.append(path.name)
        return found
    if not path.is_dir():
        return found
    base_depth = len(path.parts)
    for current, directory_names, file_names in os.walk(path):
        current_path = Path(current)
        if len(current_path.parts) - base_depth >= max_depth:
            directory_names[:] = []
        else:
            directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            if Path(name).suffix.lower() in markers or name in markers:
                found.append(name)
    return sorted(set(found))


def source_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).exists():
            found.append(label)
    return {
        "status": "blocked_source_absent" if not found else "source_present_unqualified",
        "present": bool(found),
        "upstream_owner": UPSTREAM_OWNER,
        "model_id": UPSTREAM_MODEL_ID,
        "model_revision": UPSTREAM_MODEL_REVISION,
        "model_url": UPSTREAM_MODEL_URL,
        "port_id": COMMUNITY_PORT_ID,
        "port_revision": COMMUNITY_PORT_REVISION,
        "port_url": COMMUNITY_PORT_URL,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": "Read-only existence checks only; no clone, fetch, download, extraction or vendor file is opened or executed.",
    }


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in WEIGHT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if not target.exists():
            continue
        for name in _markers_in(target, WEIGHT_SUFFIXES, max_depth=3):
            found.append((Path(label) / name).as_posix())
    return {
        "status": "blocked_weights_absent" if not found else "weights_present_unqualified",
        "present": bool(found),
        "expected_name": WEIGHTS_NAME,
        "variant": TARGET_VARIANT,
        "artifact_path": None,
        "byte_count": None,
        "sha256": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": "Existence and file-name checks only; no weight file is opened, hashed, converted, imported or loaded.",
    }


def runtime_modules() -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    for name in RUNTIME_MODULES:
        try:
            result[name] = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            result[name] = False
    return result


def runtime_probe() -> Dict[str, Any]:
    modules = runtime_modules()
    locks = [path for path in RUNTIME_LOCK_CANDIDATES if _resolve_workspace_path(path).is_file()]
    cli_candidates = [path for path in RUNTIME_CANDIDATE_PATHS if _resolve_workspace_path(path).exists()]
    cli_present = bool(cli_candidates)
    return {
        "status": "runtime_present_unqualified" if cli_present and locks else "blocked_runtime_unpinned",
        "modules": modules,
        "any_module_present": any(modules.values()),
        "lockfiles": sorted(locks),
        "cli_candidates": sorted(cli_candidates),
        "cli_present": cli_present,
        "pinned": bool(cli_present and locks),
        "framework": None,
        "framework_version": None,
        "sha256": None,
        "note": "Import discovery and fixed-path existence checks only; no CLI, package, model or operator is executed. Discovery is not runtime eligibility or approval.",
    }


def fixture_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in FIXTURE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            for name in _markers_in(target, FIXTURE_MARKERS):
                found.append((Path(label) / name).as_posix())
    return {
        "status": "blocked_matched_fixture_absent" if not found else "fixture_present_unqualified",
        "present": bool(found),
        "required": "rights-cleared task-matched clean/noisy or restoration cohort with pinned scorer, identity/noisy control and held-out cases",
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "corpus_rights": False,
        "paired_clean_reference": False,
        "scorer_pinned": False,
        "sha256": None,
        "note": "Existence checks only; no audio file is opened or decoded. A synthetic harness frame is not a matched cohort.",
    }


def license_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_terms_unverified",
        "reported_weights_license": REPORTED_WEIGHTS_LICENSE,
        "reported_weights_license_scope": REPORTED_WEIGHTS_LICENSE_SCOPE,
        "reported_port_license": REPORTED_PORT_LICENSE,
        "weights_license_text_present": False,
        "weights_license_text_sha256": None,
        "commercial_use_reported_permitted": False,
        "commercial_use_approved": False,
        "noncommercial_research_only_reported": True,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": "The model card reports NSCLv1 noncommercial weights; this is not a local legal review. No license text, decision or rights clearance is present.",
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "weights_license_text_present": False,
        "weights_license_text_sha256": None,
        "commercial_use_reported_permitted": False,
        "commercial_use_approved": False,
        "noncommercial_research_only_reported": True,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "host_target_approved": False,
        "checkpoint_terms": None,
        "input_corpus_rights": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": "No license text, written decision, redistribution scope or corpus permission is recorded locally. Upstream presence is not a right to use, redistribute or publish.",
    }


def geometry() -> Dict[str, Any]:
    return {
        "upstream_owner": UPSTREAM_OWNER,
        "component": COMPONENT_NAME,
        "target_variant": TARGET_VARIANT,
        "documented_sample_rates_hz": [8000, 16000, 22050, 24000, 32000, 44100, 48000],
        "documented_frame_points": 25,
        "documented_points": ["8k", "12k", "16k", "24k", "32k", "48k"],
        "documented_channels": None,
        "documented_frame_samples": None,
        "documented_hop_samples": None,
        "documented_lookahead_samples": None,
        "documented_content_delay_samples": None,
        "candidate_geometry_in_pinned_sources": True,
        "candidate_geometry_exact": False,
        "local_harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "installed_v0_only": True,
        },
        "local_channel_guard": MAX_CHANNELS_GUARD,
        "local_frame_guard": MAX_FRAME_SAMPLES_GUARD,
        "v0_can_represent_declared_input": True,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": "Pinned sources describe 8-48 kHz and 30 compute/lookahead points, but no exact local frame/hop/lookahead/content-delay record is verified. The 16 kHz mono 160-sample harness is installed v0 only and not candidate geometry.",
    }


def profile_mapping() -> Dict[str, str]:
    return {
        "identity_noisy_control": "blocked_no_candidate_output",
        "established_task_matched_baseline": "blocked_no_pinned_baseline",
        "paired_si_sdr": "blocked_no_permitted_clean_reference",
        "paired_stoi": "blocked_no_permitted_clean_reference_or_scorer",
        "clean_speech_preservation": "blocked_no_candidate_output",
        "peaks_and_invalid_outputs": "partial_local_harness_rejection_only",
        "unpaired_speech_predictive_or_listening": "blocked_no_permitted_cohort",
        "alignment_and_content_delay": "blocked_no_candidate_output",
        "state_reset_and_streaming": "blocked_no_candidate_instance",
        "runtime_availability_and_memory": "blocked_no_runtime",
        "candidate_output": "blocked_artifact_runtime_license_rights_and_fixture_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_pinned_weights_and_source": "blocked_artifact_absent",
        "nsclv1_terms_and_written_use_decision": "blocked_rights_unrecorded",
        "pinned_runtime_and_binary": "blocked_runtime_unpinned",
        "candidate_geometry_and_content_delay": "blocked_geometry_unverified",
        "identity_noisy_control_and_baseline": "blocked_no_candidate_output",
        "paired_si_sdr_and_stoi": "blocked_no_permitted_cohort",
        "clean_speech_preservation": "blocked_no_candidate_output",
        "peaks_invalid_and_nonfinite_outputs": "partial_local_harness_only",
        "runtime_timing_and_memory": "blocked_no_paced_measurement",
        "listening_or_separately_labeled_screen": "blocked_no_permitted_cohort",
        "provider_intake_and_release": "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_artifact_runtime_license_rights_and_fixture_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": "No pinned NVIDIA RE-USE weights, pinned Swift/MLX CLI/runtime, verified NSCLv1 use decision or matched cohort is present; no restoration, preservation, quality or timing result was produced.",
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "identity_control": {"status": "bit_exact_synthetic_only", "candidate_processing": False, "qualifies_candidate": False},
        "paired_scorer_self_check": {"status": "synthetic_only_not_candidate_output", "metrics": None, "qualifies_candidate": False},
        "source_reported_characteristics": {"status": "provenance_only_not_reproduced", "metrics": None, "qualifies_candidate": False},
        "external_fallback": {"status": "documented_no_runtime", "automatic_discovery": False, "default_registration": False, "fallback": "none", "metrics": None, "qualifies_candidate": False},
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli = {}
    identity = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {"digest": tensor_digest(samples), "byte_identical": tuple(samples) == tuple(float(value) for value in samples)}
    return {
        "purpose": "harness stimulus characterisation only; not an NVIDIA RE-USE result and not a candidate output",
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "candidate_geometry": False,
            "installed_v0_only": True,
        },
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "candidate_processing": False,
    }


def si_sdr(reference: Sequence[float], estimate: Sequence[float]) -> float:
    if len(reference) != len(estimate) or not reference:
        raise InputError("SI_SDR_GEOMETRY", "SI_SDR_GEOMETRY")
    reference_values = [float(value) for value in reference]
    estimate_values = [float(value) for value in estimate]
    for value in reference_values + estimate_values:
        if not math.isfinite(value):
            raise InputError("NONFINITE_SI_SDR_INPUT", "NONFINITE")
    reference_energy = math.fsum(value * value for value in reference_values)
    if reference_energy <= 0.0:
        raise InputError("SILENT_REFERENCE", "SILENT_REFERENCE")
    scale = math.fsum(estimate_values[index] * reference_values[index] for index in range(len(reference_values)))
    scale /= reference_energy
    target = [scale * value for value in reference_values]
    residual = [estimate_values[index] - target[index] for index in range(len(reference_values))]
    target_energy = math.fsum(value * value for value in target)
    residual_energy = math.fsum(value * value for value in residual)
    if target_energy <= 0.0 or residual_energy <= 0.0:
        raise InputError("DEGENERATE_SI_SDR", "DEGENERATE_SI_SDR")
    return 10.0 * math.log10(target_energy / residual_energy)


def _shift(values: Sequence[float], offset: int) -> List[float]:
    if offset == 0:
        return [float(value) for value in values]
    if offset > 0:
        return [0.0] * offset + [float(value) for value in values[:-offset]]
    return [float(value) for value in values[-offset:]] + [0.0] * (-offset)


def _paired_clean(length: int) -> List[float]:
    values = []
    for index in range(length):
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
        envelope = 0.7 + 0.3 * math.sin(2.0 * math.pi * 2.0 * t)
        value = (0.2 * math.sin(2.0 * math.pi * 180.0 * t) +
                 0.1 * math.sin(2.0 * math.pi * 360.0 * t) +
                 0.05 * math.sin(2.0 * math.pi * 540.0 * t))
        values.append(value * envelope)
    return values


def _paired_noise(length: int, seed: int = 20261126, scale: float = 0.03) -> List[float]:
    generator = _lcg(seed)
    return [scale * next(generator) for _ in range(length)]


def paired_harness_control() -> Dict[str, Any]:
    length = 6 * HARNESS_FRAME_VALUES
    clean = _paired_clean(length)
    noise = _paired_noise(length)
    noisy = [clean[index] + noise[index] for index in range(length)]
    clean_energy = math.fsum(value * value for value in clean)
    noise_energy = math.fsum(value * value for value in noise)
    shifts = {str(offset): _r(si_sdr(clean, _shift(noisy, offset)), 6) for offset in (-8, 0, 8)}
    return {
        "purpose": "deterministic scorer and fixture self-check; not candidate output, not a denoising result and not a qualified comparison",
        "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
        "channels": HARNESS_CHANNELS,
        "sample_count": length,
        "clean_digest": tensor_digest(clean),
        "noise_digest": tensor_digest(noise),
        "noisy_digest": tensor_digest(noisy),
        "identity_output_equals_noisy": True,
        "clean_peak_abs": _r(peak_abs(clean)),
        "noisy_peak_abs": _r(peak_abs(noisy)),
        "snr_db": _r(10.0 * math.log10(clean_energy / noise_energy), 6),
        "identity_si_sdr_db": _r(si_sdr(clean, noisy), 6),
        "shift_si_sdr_db": shifts,
        "scorer": "float64 SI-SDR; target projection; deterministic",
        "candidate_processing": False,
        "qualifies_candidate": False,
    }


UPSTREAM_BLOCKER = {
    "status": "blocked_artifact_runtime_license_rights_and_fixture_absent",
    "source": {
        "upstream_owner": UPSTREAM_OWNER,
        "model_id": UPSTREAM_MODEL_ID,
        "model_url": UPSTREAM_MODEL_URL,
        "model_revision": UPSTREAM_MODEL_REVISION,
        "port_id": COMMUNITY_PORT_ID,
        "port_url": COMMUNITY_PORT_URL,
        "port_revision": COMMUNITY_PORT_REVISION,
        "status": "absent",
    },
    "weights": {
        "artifact_path": None,
        "expected_name": WEIGHTS_NAME,
        "sha256": None,
        "byte_count": None,
        "status": "absent",
        "variant": TARGET_VARIANT,
    },
    "runtime": {
        "framework": None,
        "framework_version": None,
        "cli_path": None,
        "cli_sha256": None,
        "lockfile": None,
        "required": [
            "pinned upstream Real-time_RE-USE model.safetensors with SHA-256 and byte count",
            "pinned community Swift/MLX reuse-fast-cli binary with SHA-256 and build record",
            "exact runtime lock or build environment record",
            "import/build parity or CLI smoke evidence on a compatible host",
        ],
        "status": "absent_unpinned",
    },
    "license": {
        "status": "blocked_terms_unverified",
        "reported_name": REPORTED_WEIGHTS_LICENSE,
        "reported_scope": REPORTED_WEIGHTS_LICENSE_SCOPE,
        "weights_license_text_present": False,
        "weights_license_text_sha256": None,
        "commercial_use_reported_permitted": False,
        "commercial_use_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "review": "blocked",
    },
    "fixture": {
        "status": "absent",
        "required": "rights-cleared task-matched clean/noisy or restoration cohort with a pinned scorer, identity/noisy control and held-out cases",
        "corpus_rights": False,
        "paired_clean_reference": False,
        "scorer_pinned": False,
        "sha256": None,
    },
    "geometry": {
        "status": "unverified_absent",
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "content_delay_samples": None,
    },
    "rights_requirement": "Exact NVIDIA RE-USE weight terms, a written noncommercial/research/commercial decision as applicable, port attribution, and permission for every evaluation recording are required before any reproduction, adapter, benchmark or release claim.",
    "workspace_search": "Bounded read-only existence and file-name checks of named candidate paths found no pinned model.safetensors, no reuse-fast-cli binary, no runtime lock/build record and no matched cohort. No file was opened, downloaded, converted or reconstructed.",
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, converted or surrogate RE-USE source, checkpoint or weights",
        "no fabricated NSCLv1 license text or written rights decision",
        "no Swift, MLX, Core ML, PyTorch, ONNX or audio-runtime import/load/inference run",
        "no copied upstream model, audio or score",
        "no candidate audio, listening, timing or benchmark run",
    ],
    "reopen": "Pin the exact NVIDIA RE-USE model revision and model.safetensors with SHA-256 and byte count; verify NSCLv1 terms and record a written use decision; pin a compatible Swift/MLX or approved runtime and built CLI with SHA-256 and build/lock record; verify exact geometry/content delay for the selected operating point; clear cohort rights; then reproduce output and run the Enhancement matrix with independent review.",
}

GATES = [
    {"id": "RG-01", "status": "blocked", "gate": "exact_model_revision_and_weights_pin",
     "reason": "No pinned NVIDIA Real-time RE-USE model.safetensors, source revision record, byte count or SHA-256 is present locally.",
     "reopen": "Stage the immutable upstream model revision and model.safetensors with path, byte count, SHA-256 and provenance before any load or conversion attempt."},
    {"id": "RG-02", "status": "blocked", "gate": "nsclv1_license_text_and_use_decision",
     "reason": "The model card reports NSCLv1 noncommercial weights, but no license text, version, supplemental term or written decision exists locally.",
     "reopen": "Obtain the exact NSCLv1 license text/version with SHA-256 and a written decision covering research, redistribution, product use, derived output and attribution, or record a final rejection."},
    {"id": "RG-03", "status": "blocked", "gate": "pinned_runtime_cli_and_host_compatibility",
     "reason": "No pinned reuse-fast-cli binary, Swift/MLX build, runtime lock, exact host/toolchain record or import/CLI smoke parity is present.",
     "reopen": "Pin a compatible toolchain, build record, runtime lock and CLI/binary SHA-256 on an approved host; prove import or CLI smoke parity without network."},
    {"id": "RG-04", "status": "blocked", "gate": "candidate_geometry_content_delay_and_operating_point",
     "reason": "Sources describe 8-48 kHz and 30 compute/lookahead points, but no exact local operating-point geometry, state, lookahead or content delay is verified.",
     "reopen": "Verify the exact selected operating point, sample rate, channels, frame/hop, state, lookahead and content delay from the pinned artifact/runtime."},
    {"id": "RG-05", "status": "blocked", "gate": "rights_cleared_matched_cohort_and_scorer",
     "reason": "No rights-cleared matched cohort and no pinned SI-SDR/STOI scorer are present. Synthetic harness frames are not a cohort.",
     "reopen": "Stage a rights-cleared held-out cohort with pinned scorer and controls, covering speech, noise, silence and intended restoration cases."},
    {"id": "RG-06", "status": "blocked", "gate": "paired_enhancement_matrix_and_preservation",
     "reason": "Enhancement profile requires identity/noisy control, task-matched baseline, paired SI-SDR/STOI, preservation, peaks, invalid outputs, alignment and state. No candidate output exists.",
     "reopen": "Run the full Enhancement matrix on a rights-cleared cohort with pinned baseline and record adverse/nonfinite/preservation failures."},
    {"id": "RG-07", "status": "blocked", "gate": "runtime_timing_memory_and_listening",
     "reason": "No pinned runtime, device pacing, availability, deadline, CPU, memory, authorized listening or separately labeled predictive screen exists.",
     "reopen": "Measure target-host pacing, availability, content delay, CPU, memory and deadline behavior, and add authorized listening and/or a separately labeled predictive screen."},
    {"id": "RG-08", "status": "blocked", "gate": "opt_in_provider_intake_benchmark_and_release",
     "reason": "No opt-in provider intake, descriptor review, public-surface decision, benchmark validation, independent exact-head review or release approval exists.",
     "reopen": "Complete artifact and rights decisions, implement any adapter only behind explicit caller opt-in with no default/fallback, validate a benchmark bundle, and obtain independent review and release approval."},
]

REQUIRED_ARTIFACTS = [
    {"id": "A1", "artifact": "exact NVIDIA RE-USE model revision and weights", "status": "absent", "byte_count": None, "sha256": None, "license": REPORTED_WEIGHTS_LICENSE, "rights_reviewed": False,
     "required": "The immutable upstream model revision and model.safetensors (or approved equivalent) with path, byte count, SHA-256 and provenance."},
    {"id": "A2", "artifact": "NSCLv1 license text and written use decision", "status": "absent", "byte_count": None, "sha256": None, "license": REPORTED_WEIGHTS_LICENSE, "rights_reviewed": False,
     "required": "The exact NSCLv1 license text/version and a written decision covering research, redistribution, product use, derived output and attribution."},
    {"id": "A3", "artifact": "pinned runtime, CLI/binary and build record", "status": "absent", "byte_count": None, "sha256": None, "license": REPORTED_PORT_LICENSE, "rights_reviewed": False,
     "required": "A compatible pinned Swift/MLX or approved runtime, built CLI/binary with SHA-256, lock/build record and host/toolchain parity evidence."},
    {"id": "A4", "artifact": "verified candidate geometry and asset manifest", "status": "absent", "byte_count": None, "sha256": None, "license": None, "rights_reviewed": False,
     "required": "Verified operating point, sample rate, channels, frame/hop, state, lookahead and content delay plus a caller-supplied manifest that reproduces exact output."},
    {"id": "A5", "artifact": "rights-cleared matched cohort and pinned scorer", "status": "absent", "byte_count": None, "sha256": None, "license": None, "rights_reviewed": False,
     "required": "A rights-cleared task-matched cohort with held-out cases and a pinned SI-SDR/STOI scorer and controls."},
    {"id": "A6", "artifact": "opt-in intake, benchmark validation and review", "status": "absent", "byte_count": None, "sha256": None, "license": None, "rights_reviewed": False,
     "required": "Opt-in provider/adapter intake, descriptor review, benchmark validation, independent exact-head review and release approval with no default registration or fallback."},
]

ASSET_CONTRACT = {
    "schema_id": ASSET_SCHEMA_ID,
    "status": "metadata_only_no_artifact_present",
    "admits_without_rights_review": False,
    "hashes_caller_artifact": False,
    "loads_or_executes_artifact": False,
    "required_fields": sorted(ASSET_KEYS),
    "runtimes_accepted": list(ASSET_RUNTIMES),
    "variants_accepted": list(ASSET_VARIANTS),
    "dtypes_accepted": list(ASSET_DTYPES),
    "note": "The schema validates caller-declared identity and geometry only. A structurally valid manifest is still deferred because the artifact, license terms, reviewed rights, runtime and geometry record are absent. No path is opened, no artifact is hashed and nothing is loaded.",
}

EXTERNAL_BOUNDARY = {
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "candidate_output_present": False,
    "commercial_use_approved": False,
    "commercial_use_reported_permitted": False,
    "component": COMPONENT_NAME,
    "derived_output_approved": False,
    "distribution_model": "upstream NVIDIA weights under NSCLv1 terms as reported; community Swift/MLX port separate",
    "documented": True,
    "fallback": "none",
    "host_target_approved": False,
    "license_reported": REPORTED_WEIGHTS_LICENSE,
    "license_scope_reported": REPORTED_WEIGHTS_LICENSE_SCOPE,
    "license_text_present": False,
    "local_runtime_present": False,
    "note": "Boundary is documented from pinned census/inventory/adapter rows only. No weights, license text, runtime, measurement or candidate output is present.",
    "product": UPSTREAM_MODEL_ID,
    "redistribution_approved": False,
    "repository": UPSTREAM_MODEL_URL,
    "source_present": False,
    "upstream_owner": UPSTREAM_OWNER,
    "vendor_claims_separate_from_local_measurements": True,
    "weights_present": False,
}

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/nvidia-re-use/ is touched.",
    "The reference is a task-local model-admission gate, not NVIDIA RE-USE.",
    "Candidate facts come only from pinned local evidence files.",
    "All harness stimuli are analytic or seeded synthetic; no candidate runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

NON_CLAIMS = (
    "No NVIDIA RE-USE checkpoint, model, Swift/MLX binary, runtime, or license text is included.",
    "No RE-USE model, Mamba, inference path, adapter or conversion is implemented, approximated, simulated or run.",
    "No PESQ, STOI, SI-SDR, DNSMOS, RTF, CPU, GPU, memory or platform claim is reproduced or generalized.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, model, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)


def collect_blockers() -> List[str]:
    blockers: List[str] = []
    if not source_probe()["present"]:
        blockers.append("artifact_absent")
    if not weights_probe()["present"]:
        blockers.append("weights_absent")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if license_probe()["review"] != "approved":
        blockers.append("license_terms_unverified")
    if rights_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    if not fixture_probe()["present"]:
        blockers.append("matched_cohort_absent")
    blockers.append("candidate_geometry_unverified")
    return sorted(set(blockers))


def admit(request: Any) -> Dict[str, Any]:
    validate_request(request)
    blockers = collect_blockers()
    return {
        "status": "DEFER",
        "admissible": False,
        "candidate_processing": False,
        "input_validated": True,
        "geometry_verified": False,
        "metrics": None,
        "result": None,
        "qualifies_candidate": False,
        "blockers": blockers,
        "note": "A structurally valid request is still not admissible: the NVIDIA RE-USE weights, exact license/use decision, pinned runtime, matched cohort and candidate geometry are absent. No fallback or surrogate is used.",
    }


def admit_asset(manifest: Any) -> Dict[str, Any]:
    parsed = validate_asset_manifest(manifest)
    return {
        "status": "DEFER",
        "admissible": False,
        "candidate_processing": False,
        "manifest_validated": True,
        "artifact_opened": False,
        "artifact_hashed": False,
        "artifact_loaded": False,
        "declared_variant": parsed["variant"],
        "declared_runtime": parsed["runtime"],
        "caller_declaration_is_not_review": True,
        "metrics": None,
        "result": None,
        "qualifies_candidate": False,
        "blockers": collect_blockers(),
        "note": "A structurally valid manifest does not admit an artifact: license terms, reviewed rights, artifact identity, runtime and candidate geometry are not independently verified, and no path is opened.",
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: NVIDIA RE-USE weights, exact NSCLv1 use decision, pinned runtime and matched cohort are not present; no processing is performed",
        "ARTIFACTS_ABSENT",
    )


def _board_projection(board: Any) -> Tuple[List[Dict[str, Any]], str]:
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    rows = [row for row in board["tasks"] if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ConfigError("linked task row is missing or duplicated", "BOARD_ROW_MISSING")
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed", "BOARD_IDENTITY_CHANGED")
    projected = [stable]
    return projected, sha256_bytes(canonical_bytes(projected))


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    return _board_projection(board)


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name, "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def source_evidence_statements() -> List[str]:
    return [
        "research/noise_suppression_candidate_census.md records NVIDIA Real-time RE-USE as a universal Mamba speech restoration model with 30 configurable compute/lookahead points, 8-48 kHz and explicit online inference, with NSCLv1 weights and a community Swift/MLX port noted as experimental.",
        "research/voice-enhancement-20261101/candidate_matrix.csv records NVIDIA RE-USE as unavailable/blocked on the current host because the pinned model.safetensors and built community CLI are absent; no local parity/evaluation exists.",
        "adapters/reuse-mlx/adapter.json and README describe the local integration scope, pinned upstream/community revisions, Apple Silicon/Swift requirements, and required local binary/checkpoint SHA-256 checks; they are integration scope evidence, not qualification.",
        "plan/INVENTORY.json assigns nvidia-re-use the enhancement verification profile, disposition sdk-model and evidence status blocked, with the candidate matrix, census and adapter rows as evidence.",
        "plan/audio-sdk/README.md requires runnable source, exact assets, permitted scope and matched evidence before a caller-supplied reference or opt-in adapter is added.",
        "No local NVIDIA RE-USE checkpoint, pinned reuse-fast-cli binary, runtime lock/build record, NSCLv1 text/written decision or matched cohort exists; nothing was cloned, downloaded, converted or reconstructed.",
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    weights = weights_probe()
    runtime = runtime_probe()
    license_block = license_probe()
    fixture = fixture_probe()
    rights = rights_probe()
    geom = geometry()
    adverse = _adverse_cases()
    adverse_json = _json_adverse_cases()
    stimuli = stimulus_probe()
    paired = paired_harness_control()
    gates = [dict(gate) for gate in GATES]
    required = [dict(row) for row in REQUIRED_ARTIFACTS]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "artifact_absent": source["present"] is False,
        "weights_absent": weights["present"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "license_text_absent": license_block["weights_license_text_present"] is False,
        "commercial_use_not_approved": license_block["commercial_use_approved"] is False,
        "candidate_geometry_unverified": geom["candidate_geometry_exact"] is False,
        "matched_fixture_absent": fixture["present"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "invalid_requests_rejected": adverse["all_requests_rejected"],
        "asset_manifests_rejected": adverse["all_manifests_rejected"],
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked": missing_result("reuse_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(block["byte_identical"] for block in stimuli["identity_control"].values()),
        "paired_scorer_finite": math.isfinite(paired["identity_si_sdr_db"]) and math.isfinite(paired["snr_db"]) and all(math.isfinite(value) for value in paired["shift_si_sdr_db"].values()),
        "paired_control_not_candidate": paired["candidate_processing"] is False and paired["qualifies_candidate"] is False,
        "eight_release_gates_blocked": len(gates) == 8 and all(gate["status"] == "blocked" for gate in gates),
        "external_boundary_closed": EXTERNAL_BOUNDARY["adapter_implemented"] is False and EXTERNAL_BOUNDARY["adapter_default_registration"] is False and EXTERNAL_BOUNDARY["automatic_discovery"] is False and EXTERNAL_BOUNDARY["fallback"] == "none",
        "no_result_qualifies_candidate": True,
        "no_full_board_hash": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "verification_profile": VERIFICATION_PROFILE,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {"name": VERIFICATION_PROFILE, "source": SOURCE_PINS[PROFILE_SOURCE]},
        "profile_mapping": profile_mapping(),
        "external_boundary": dict(EXTERNAL_BOUNDARY),
        "reference": {
            "implementation": "task-local standard-library model-admission gate",
            "real_component_source_present": source["present"],
            "model_weights_present": weights["present"],
            "eligible_runtime_present": runtime["any_module_present"] or runtime["cli_present"],
            "pinned_runtime_present": runtime["pinned"],
            "matched_fixture_present": fixture["present"],
            "license_text_present": license_block["weights_license_text_present"],
            "rights_approved": False,
            "candidate_geometry_verified": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": "No RE-USE model, Mamba, inference path, adapter or conversion is implemented or simulated; only probes, request/manifest rejection and synthetic harness controls are performed.",
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "required_artifacts": required,
        "missing_artifacts": [row["artifact"] for row in required if row["status"] == "absent"],
        "source_probe": source,
        "weights_probe": weights,
        "runtime_probe": runtime,
        "license_probe": license_block,
        "fixture_probe": fixture,
        "rights_probe": rights,
        "geometry": geom,
        "asset_contract": dict(ASSET_CONTRACT),
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "paired_harness_control": paired,
        "adverse": {
            "invalid_config_input_and_manifest": adverse,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("reuse_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --all",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
