# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence core for SDK-CLEARERVOICE-MOSSFORMER2-SE-48K.

The pinned candidate (ClearerVoice ``MossFormer2_SE_48K``) is absent.  This
module therefore builds a bounded, task-local *boundary probe* only:

* a deterministic 48 kHz mono fixture made with integer arithmetic;
* a strict caller-supplied-asset manifest validator;
* a strict whole-clip session contract with adverse-input rejection;
* a model-free first-order DC-blocker mechanism probe (not the candidate);
* canonical contract/report generation and README/table/pin helpers.

It never downloads, imports, loads or executes ClearerVoice, PyTorch, a
checkpoint, a wheel or a native runtime.  It never reads or hashes the mutable
full ``plan/swarm/TASKS.json``.
"""

from __future__ import annotations

import array
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

TASK = "SDK-CLEARERVOICE-MOSSFORMER2-SE-48K"
TITLE = "ClearerVoice MossFormer2_SE_48K"
COMPONENT = "clearervoice-mossformer2-se-48k"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "38f502b8e67a4cfef7dd72425aae6b0044846aad"
BRANCH = "swarm/SDK-CLEARERVOICE-MOSSFORMER2-SE-48K"
REVIEWER = "reviewer-CLEARERVOICE-MOSSFORMER2-SE-48K"
WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-CLEARERVOICE-MOSSFORMER2-SE-48K"
)
TASK_PREFIX = "docs/task-evidence/" + COMPONENT
DEFAULT_SOURCE_ROOT = "/Users/htsakanyan/workspace/audio/audioml"

SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_REPORT = "audio-sdk/task-evidence/" + COMPONENT + "/report/0.1"
SCHEMA_CONFIG = "audio-sdk/task-evidence/" + COMPONENT + "/session-config/0.1"
SCHEMA_ASSET = "audio-sdk/" + COMPONENT + "/caller-supplied-asset/0.1"

# --------------------------------------------------------------------------
# Pinned provenance (exact, copied from the merged sibling evidence)
# --------------------------------------------------------------------------

UPSTREAM_REPOSITORY = "https://github.com/modelscope/ClearerVoice-Studio"
UPSTREAM_SOURCE_REVISION = "dcb1b20e1e44d435090072ab9b223c792ea1f624"
UPSTREAM_PACKAGE_VERSION = "0.1.2"
UPSTREAM_PACKAGE_IDENTITY = "ClearerVoice-Studio-clearvoice-0.1.2"
UPSTREAM_CODE_LICENSE = "Apache-2.0"
MODEL_NAME = "MossFormer2_SE_48K"
MODEL_REPOSITORY = "https://huggingface.co/alibabasglab/MossFormer2_SE_48K"
MODEL_CARD_LICENSE_REPORTED = "Apache-2.0"
MODEL_FILENAME_HINT = "last_best_checkpoint.pt"

# No pinned local ledger records the exact checkpoint identity, so these are
# deliberately None.  They must be filled only from a verified external record.
PINNED_MODEL_SHA256: Optional[str] = None
PINNED_MODEL_BYTES: Optional[int] = None

MODEL_PATH = (
    "data/models/clearvoice/MossFormer2_SE_48K/" + MODEL_FILENAME_HINT
)
SOURCE_CHECKOUT_PATH = "data/checkouts/ClearerVoice-Studio"
RUNTIME_ENV_PATH = "data/envs/clearvoice"

SOURCE_PINS: Dict[str, str] = {
    "source:adapters/clearvoice/README.md":
        "9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5",
    "source:adapters/clearvoice/adapter.json":
        "ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff",
    "source:adapters/clearvoice/requirements.lock":
        "3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91",
    "source:adapters/clearvoice/run.py":
        "c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "source:research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "source:research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS: Dict[str, str] = {
    "sdk:CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "sdk:CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "sdk:REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "sdk:api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "sdk:api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "sdk:docs/task-evidence/clearvoice-frcrn-16khz/README.md":
        "2ba56bbe54c825818143aa27859f2e001077bf0024932321a45e764fd40ef75d",
    "sdk:docs/task-evidence/clearvoice-mossformergan/README.md":
        "4cce8370c8af8bd2a5a83f05bf15e540756f1f7d61f63170b6a9626f65d6bbce",
    "sdk:docs/task-evidence/clearvoice-mossformergan/contract.json":
        "cd98bc7b615b0861923d2a53a24ec91fd939c6dcade0818022912a5a5e34869c",
    "sdk:docs/task-evidence/clearvoice-mossformergan/report.json":
        "5c806186d35c1f39021617dc5649bf32d87030a1a059d26e35492a69ee1a7afc",
    "sdk:scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# --------------------------------------------------------------------------
# Board identity: stable linked-row only, never the mutable full file
# --------------------------------------------------------------------------

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "id": TASK,
    "mode": MODE,
    "repository": REPOSITORY,
    "title": TITLE,
}


def _stable_sha256() -> str:
    payload = json.dumps(
        BOARD_ROW_STABLE_FIELDS,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


BOARD_ROW_STABLE_SHA256 = _stable_sha256()

# --------------------------------------------------------------------------
# Fixture geometry
# --------------------------------------------------------------------------

SAMPLE_RATE_HZ = 48000
CHANNELS = 1
INSTALLED_SAMPLE_RATE_HZ = 16000
INSTALLED_CHANNELS = 1
INSTALLED_FRAME_SAMPLES = 160
FRAME_SAMPLES = 480
TOTAL_SAMPLES = 192000  # 4 s at 48 kHz
MAX_CHUNK_SAMPLES = 192000
MAX_TOTAL_SAMPLES = 1920000

# id, kind, start, end, f0, harmonic amplitudes, noise amplitude
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "kind": "silence", "start": 0, "end": 24000,
     "f0": 0, "amplitudes": [], "noise_amp": 0},
    {"id": "quiet-speech", "kind": "speech", "start": 24000, "end": 72000,
     "f0": 140, "amplitudes": [900, 300, 180], "noise_amp": 120},
    {"id": "active-speech", "kind": "speech", "start": 72000, "end": 120000,
     "f0": 190, "amplitudes": [4200, 1800, 900], "noise_amp": 450},
    {"id": "low-snr-speech", "kind": "speech", "start": 120000, "end": 168000,
     "f0": 230, "amplitudes": [2600, 1100, 500], "noise_amp": 2200},
    {"id": "tail-silence", "kind": "silence", "start": 168000, "end": 192000,
     "f0": 0, "amplitudes": [], "noise_amp": 0},
)

FIXTURE_ID = COMPONENT + "-offline-whole-clip-fixture-v1"
SCENARIO_ID = COMPONENT + "-offline-whole-clip-v1"

DC_COEFFICIENT_NUM = 32000
DC_COEFFICIENT_DEN = 32768

# --------------------------------------------------------------------------
# Strict JSON and hashing helpers
# --------------------------------------------------------------------------


class Reject(ValueError):
    """A deterministic, reason-coded rejection."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _duplicate_guard(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    seen: Dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("duplicate_key:" + key)
        seen[key] = value
    return seen


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def strict_loads(text: str) -> Any:
    """Parse strict JSON: no duplicate keys, no NaN/Infinity, no trailing data."""
    return json.loads(
        text,
        object_pairs_hook=_duplicate_guard,
        parse_constant=_reject_constant,
    )


def strict_object_loads(text: str) -> Dict[str, Any]:
    value = strict_loads(text)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def _normalize(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(
        _normalize(value),
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def round9(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    result = round(float(value), 9)
    if result == 0.0:
        return 0.0
    return result


# --------------------------------------------------------------------------
# Deterministic integer fixture
# --------------------------------------------------------------------------


def clamp16(value: int) -> int:
    if value < -32768:
        return -32768
    if value > 32767:
        return 32767
    return int(value)


def triangle(phase: int) -> int:
    """Integer triangle wave in [-16384, 16384]."""
    point = phase & 0xFFFF
    if point < 0x8000:
        return point - 16384
    return 0x10000 - point - 16384


class Lcg:
    """Fixed 31-bit LCG; no platform-dependent randomness."""

    def __init__(self, seed: int = 0x12345678) -> None:
        self.state = seed & 0x7FFFFFFF

    def next(self) -> int:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def symmetric(self, amplitude: int) -> int:
        if amplitude <= 0:
            return 0
        return (self.next() % (2 * amplitude + 1)) - amplitude


def _envelope(index: int, length: int) -> int:
    ramp = 2400
    if length <= 0:
        return 0
    if index < ramp:
        return (index * 1024) // ramp
    if index >= length - ramp:
        return ((length - 1 - index) * 1024) // ramp
    return 1024


_FIXTURE_CACHE: Optional[Dict[str, Any]] = None


def build_fixture() -> Dict[str, Any]:
    """Return the frozen int16 fixture: clean, additive noise and observation."""
    global _FIXTURE_CACHE
    if _FIXTURE_CACHE is not None:
        return _FIXTURE_CACHE

    clean = [0] * TOTAL_SAMPLES
    noise = [0] * TOTAL_SAMPLES
    observed = [0] * TOTAL_SAMPLES
    lcg = Lcg()

    for segment in SEGMENTS:
        start = int(segment["start"])
        end = int(segment["end"])
        length = end - start
        f0 = int(segment["f0"])
        amplitudes = [int(item) for item in segment["amplitudes"]]
        noise_amp = int(segment["noise_amp"])
        phases = [0 for _ in amplitudes]
        steps = [
            (f0 * (index + 1) * 0x10000) // SAMPLE_RATE_HZ
            for index in range(len(amplitudes))
        ]
        for local in range(length):
            index = start + local
            envelope = _envelope(local, length)
            sample = 0
            for harmonic, amplitude in enumerate(amplitudes):
                sample += amplitude * triangle(phases[harmonic])
                phases[harmonic] = (phases[harmonic] + steps[harmonic]) & 0xFFFF
            sample = (sample // 16384) * envelope // 1024
            if amplitudes and local % 9600 == 0 and local + 24 < length:
                sample += 5000
            elif amplitudes and 0 < local % 9600 <= 24:
                sample += (5000 * (25 - (local % 9600))) // 25
            clean[index] = clamp16(sample)
            noise[index] = clamp16(lcg.symmetric(noise_amp))
            observed[index] = clamp16(clean[index] + noise[index])

    fixture = {
        "clean": clean,
        "noise": noise,
        "observed": observed,
    }
    _FIXTURE_CACHE = fixture
    return fixture


def int16_bytes(values: Iterable[int]) -> bytes:
    packed = array.array("h", values)
    if sys.byteorder != "little":
        packed.byteswap()
    return packed.tobytes()


def float_samples(values: Iterable[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def fixture_digests() -> Dict[str, str]:
    fixture = build_fixture()
    return {
        "clean": sha256_bytes(int16_bytes(fixture["clean"])),
        "noise": sha256_bytes(int16_bytes(fixture["noise"])),
        "observed": sha256_bytes(int16_bytes(fixture["observed"])),
    }


def fixture_spec() -> List[Dict[str, Any]]:
    return [
        {
            "id": segment["id"],
            "kind": segment["kind"],
            "start_sample": segment["start"],
            "end_sample": segment["end"],
            "samples": segment["end"] - segment["start"],
            "f0_hz": segment["f0"],
            "harmonic_amplitudes": list(segment["amplitudes"]),
            "noise_amplitude": segment["noise_amp"],
        }
        for segment in SEGMENTS
    ]


def fixture_spec_digest() -> str:
    return sha256_bytes(canonical_bytes(fixture_spec()))


FIXTURE_SPEC_DIGEST = fixture_spec_digest()
FIXTURE_DIGESTS = fixture_digests()

# --------------------------------------------------------------------------
# Model-free mechanism probe
# --------------------------------------------------------------------------


def dc_block(values: Sequence[int]) -> Tuple[List[int], int]:
    """Fixed first-order DC blocker; exact integer arithmetic.

    Returns the output and the number of samples clamped at int16 bounds.
    This is a boundary mechanism probe, not MossFormer2_SE_48K.
    """
    output: List[int] = []
    previous_input = 0
    previous_output = 0
    clipped = 0
    for value in values:
        raw = (
            value
            - previous_input
            + (DC_COEFFICIENT_NUM * previous_output) // DC_COEFFICIENT_DEN
        )
        bounded = clamp16(raw)
        if bounded != raw:
            clipped += 1
        output.append(bounded)
        previous_input = value
        previous_output = bounded
    return output, clipped


# --------------------------------------------------------------------------
# Strict caller-asset manifest
# --------------------------------------------------------------------------

ASSET_FIELDS = {
    "channels",
    "checkpoint_file",
    "checkpoint_pointer_path",
    "checkpoint_pointer_sha256",
    "input_format",
    "license_decision",
    "mode",
    "model_bytes",
    "model_name",
    "model_path",
    "model_sha256",
    "package_version",
    "sample_rate_hz",
    "source_revision",
}

ASSET_VALUES = {
    "channels": CHANNELS,
    "input_format": "float32",
    "mode": "offline",
    "model_name": MODEL_NAME,
    "package_version": UPSTREAM_PACKAGE_VERSION,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "source_revision": UPSTREAM_SOURCE_REVISION,
}


def _absolute_file(field: str, raw: Any) -> Path:
    if not isinstance(raw, str) or not raw:
        raise Reject("asset_type:" + field)
    path = Path(raw)
    if not path.is_absolute():
        raise Reject("asset_path_not_absolute:" + field)
    if not path.is_file():
        raise Reject("asset_file_missing:" + field)
    return path


def validate_asset_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-owned asset mechanics only; never load or execute.

    A successful validation means the supplied bytes match the supplied
    digests and the declared geometry.  It does not mean the pinned
    MossFormer2_SE_48K identity is present; see :func:`admit_candidate_asset`.
    """
    if not isinstance(manifest, dict):
        raise Reject("asset_not_object")
    if set(manifest) != ASSET_FIELDS:
        raise Reject("asset_field_set_mismatch")
    for field, expected in ASSET_VALUES.items():
        if manifest[field] != expected:
            raise Reject("asset_value_mismatch:" + field)
    if manifest["license_decision"] not in ("cleared", "not_cleared"):
        raise Reject("asset_value_mismatch:license_decision")

    model_path = _absolute_file("model_path", manifest["model_path"])
    pointer_path = _absolute_file(
        "checkpoint_pointer_path", manifest["checkpoint_pointer_path"]
    )
    model_bytes = manifest["model_bytes"]
    if isinstance(model_bytes, bool) or not isinstance(model_bytes, int):
        raise Reject("asset_type:model_bytes")
    if model_bytes <= 0:
        raise Reject("asset_value_mismatch:model_bytes")
    if model_path.stat().st_size != model_bytes:
        raise Reject("asset_byte_count_mismatch")
    if sha256_file(model_path) != manifest["model_sha256"]:
        raise Reject("asset_model_hash_mismatch")
    if sha256_file(pointer_path) != manifest["checkpoint_pointer_sha256"]:
        raise Reject("asset_pointer_hash_mismatch")
    pointer_text = pointer_path.read_text(encoding="utf-8").strip()
    if pointer_text != manifest["checkpoint_file"]:
        raise Reject("asset_pointer_content_mismatch")
    checkpoint_file = manifest["checkpoint_file"]
    if (
        not isinstance(checkpoint_file, str)
        or not checkpoint_file.endswith(".pt")
        or "/" in checkpoint_file
        or "\\" in checkpoint_file
    ):
        raise Reject("asset_value_mismatch:checkpoint_file")

    return {
        "valid": True,
        "pinned_model": False,
        "loaded": False,
        "executed": False,
        "imported": False,
        "model_bytes": model_bytes,
        "model_sha256": manifest["model_sha256"],
    }


def admit_candidate_asset(manifest: Any) -> Dict[str, Any]:
    """Fail closed until both the rights decision and exact identity are pinned."""
    details = validate_asset_manifest(manifest)
    if manifest["license_decision"] != "cleared":
        raise Reject("asset_rights_not_cleared")
    if PINNED_MODEL_SHA256 is None or PINNED_MODEL_BYTES is None:
        raise Reject("asset_model_identity_unrecorded")
    if manifest["model_sha256"] != PINNED_MODEL_SHA256:
        raise Reject("asset_model_hash_mismatch")
    if manifest["model_bytes"] != PINNED_MODEL_BYTES:
        raise Reject("asset_byte_count_mismatch")
    details["pinned_model"] = True
    return details


# --------------------------------------------------------------------------
# Strict whole-clip configuration and session
# --------------------------------------------------------------------------

CONFIG_FIELDS = {
    "channels",
    "epoch",
    "first_input_sample",
    "frame_samples",
    "input_format",
    "mode",
    "model_used",
    "real_runtime",
    "resampling",
    "sample_rate_hz",
    "schema_id",
}


def default_config(epoch: int = 0) -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_CONFIG,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "input_format": "float32",
        "frame_samples": FRAME_SAMPLES,
        "mode": "offline",
        "epoch": epoch,
        "first_input_sample": 0,
        "real_runtime": False,
        "model_used": False,
        "resampling": "none",
    }


def validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise Reject("config_not_object")
    if set(config) != CONFIG_FIELDS:
        raise Reject("config_key_set_mismatch")
    expected = {
        "schema_id": SCHEMA_CONFIG,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "input_format": "float32",
        "frame_samples": FRAME_SAMPLES,
        "mode": "offline",
        "real_runtime": False,
        "model_used": False,
        "resampling": "none",
    }
    for field, value in expected.items():
        if config[field] != value:
            raise Reject("config_mismatch:" + field)
    epoch = config["epoch"]
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise Reject("invalid_epoch")
    first = config["first_input_sample"]
    if isinstance(first, bool) or not isinstance(first, int) or first != 0:
        raise Reject("invalid_first_input_sample")
    return dict(config)


def _validate_chunk(chunk: Any) -> List[float]:
    if isinstance(chunk, (str, bytes, bytearray)):
        raise Reject("chunk_not_sequence")
    if not isinstance(chunk, (list, tuple)):
        raise Reject("chunk_type")
    if not chunk:
        raise Reject("chunk_empty")
    if len(chunk) > MAX_CHUNK_SAMPLES:
        raise Reject("chunk_too_long")
    values: List[float] = []
    for item in chunk:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise Reject("chunk_type")
        value = float(item)
        if not math.isfinite(value):
            raise Reject("chunk_nonfinite")
        if value < -1.0 or value > 1.0:
            raise Reject("chunk_range")
        values.append(value)
    return values


class Session:
    """Whole-clip buffering session used only for boundary evidence."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = validate_config(config or default_config())
        self.mode = "dc_block"
        self.epoch = int(self.config["epoch"])
        self._samples: List[int] = []
        self._finished = False
        self._closed = False

    @property
    def accepted_samples(self) -> int:
        return len(self._samples)

    def _guard_open(self) -> None:
        if self._closed:
            raise Reject("session_closed")
        if self._finished:
            raise Reject("session_already_finished")

    def push(self, chunk: Any) -> int:
        self._guard_open()
        values = _validate_chunk(chunk)
        if len(self._samples) + len(values) > MAX_TOTAL_SAMPLES:
            raise Reject("session_too_long")
        converted = [clamp16(int(round(value * 32768.0))) for value in values]
        self._samples.extend(converted)
        return len(converted)

    def finish(self) -> List[int]:
        self._guard_open()
        output, _ = dc_block(self._samples)
        self._finished = True
        return output

    def reset(self, epoch: int, first_input_sample: int = 0) -> None:
        if self._closed:
            raise Reject("session_closed")
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise Reject("invalid_epoch")
        if epoch <= self.epoch:
            raise Reject("epoch_not_greater")
        if first_input_sample != 0:
            raise Reject("invalid_first_input_sample")
        self.epoch = epoch
        self._samples = []
        self._finished = False

    def close(self) -> None:
        self._closed = True

    def state_digest(self) -> str:
        payload = canonical_bytes(
            {
                "mode": self.mode,
                "epoch": self.epoch,
                "finished": self._finished,
                "closed": self._closed,
                "samples": int16_bytes(self._samples).hex(),
            }
        )
        return sha256_bytes(payload)


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def _energy(values: Sequence[float]) -> float:
    return float(sum(value * value for value in values))


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return float(sum(a * b for a, b in zip(left, right)))


def snr_db(clean: Sequence[float], estimate: Sequence[float]) -> Optional[float]:
    clean_energy = _energy(clean)
    if clean_energy == 0.0:
        return None
    error = [a - b for a, b in zip(clean, estimate)]
    error_energy = _energy(error)
    if error_energy == 0.0:
        return None
    return round9(10.0 * math.log10(clean_energy / error_energy))


def si_sdr_db(clean: Sequence[float], estimate: Sequence[float]) -> Optional[float]:
    clean_energy = _energy(clean)
    if clean_energy == 0.0:
        return None
    scale = _dot(estimate, clean) / clean_energy
    target = [scale * value for value in clean]
    residual = [a - b for a, b in zip(estimate, target)]
    target_energy = _energy(target)
    residual_energy = _energy(residual)
    if target_energy == 0.0 or residual_energy == 0.0:
        return None
    return round9(10.0 * math.log10(target_energy / residual_energy))


def target_retention(clean: Sequence[float],
                     estimate: Sequence[float]) -> Optional[float]:
    clean_energy = _energy(clean)
    if clean_energy == 0.0:
        return None
    return round9(_dot(estimate, clean) / clean_energy)


def _score(clean: Sequence[float], estimate: Sequence[float]) -> Dict[str, Any]:
    return {
        "snr_db": snr_db(clean, estimate),
        "si_sdr_db": si_sdr_db(clean, estimate),
        "target_retention": target_retention(clean, estimate),
        "samples": len(clean),
    }


def build_metrics() -> Dict[str, Any]:
    fixture = build_fixture()
    clean = float_samples(fixture["clean"])
    observed = float_samples(fixture["observed"])
    probe_int, clipped = dc_block(fixture["observed"])
    probe = float_samples(probe_int)

    identity = _score(clean, observed)
    surrogate = _score(clean, probe)
    delta = None
    if identity["si_sdr_db"] is not None and surrogate["si_sdr_db"] is not None:
        delta = round9(surrogate["si_sdr_db"] - identity["si_sdr_db"])

    strata: Dict[str, Any] = {}
    for segment in SEGMENTS:
        start = int(segment["start"])
        end = int(segment["end"])
        strata[str(segment["id"])] = {
            "kind": segment["kind"],
            "identity": _score(clean[start:end], observed[start:end]),
            "surrogate": _score(clean[start:end], probe[start:end]),
        }

    return {
        "identity": identity,
        "surrogate": surrogate,
        "delta_si_sdr_db": delta,
        "strata": strata,
        "max_abs_output": round9(max(abs(value) for value in probe)),
        "nonfinite_output_samples": sum(
            1 for value in probe if not math.isfinite(value)
        ),
        "output_peak_clipped_samples": clipped,
        "silence_exact_zero": all(
            value == 0.0 for value in probe[: SEGMENTS[0]["end"]]
        ),
        "scored_samples": len(clean),
        "metric_scope": "synthetic_surrogate_only_not_candidate",
    }


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------


def _control_asset() -> Dict[str, Any]:
    import tempfile

    rejections: Dict[str, str] = {}
    generic: Dict[str, Any] = {}
    candidate_reason = ""
    with tempfile.TemporaryDirectory(prefix="mossformer2-asset-") as raw_dir:
        root = Path(raw_dir)
        model = root / MODEL_FILENAME_HINT
        pointer = root / "last_best_checkpoint"
        model.write_bytes(b"caller-owned-placeholder-model-bytes")
        pointer.write_text(MODEL_FILENAME_HINT + "\n", encoding="utf-8")
        body = {
            "checkpoint_file": MODEL_FILENAME_HINT,
            "checkpoint_pointer_path": str(pointer),
            "checkpoint_pointer_sha256": sha256_file(pointer),
            "channels": CHANNELS,
            "input_format": "float32",
            "license_decision": "not_cleared",
            "mode": "offline",
            "model_bytes": model.stat().st_size,
            "model_name": MODEL_NAME,
            "model_path": str(model),
            "model_sha256": sha256_file(model),
            "package_version": UPSTREAM_PACKAGE_VERSION,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "source_revision": UPSTREAM_SOURCE_REVISION,
        }

        def expect(name: str, override: Dict[str, Any]) -> None:
            current = dict(body)
            current.update(override)
            try:
                validate_asset_manifest(current)
            except Reject as error:
                rejections[name] = error.reason
            else:
                rejections[name] = "accepted_unexpectedly"

        generic = validate_asset_manifest(body)
        try:
            admit_candidate_asset(body)
        except Reject as error:
            rejections["candidate_not_cleared"] = error.reason

        cleared = dict(body)
        cleared["license_decision"] = "cleared"
        try:
            admit_candidate_asset(cleared)
        except Reject as error:
            candidate_reason = error.reason

        expect("absent_model", {"model_path": str(root / "missing.pt")})
        expect("relative_path", {"model_path": MODEL_FILENAME_HINT})
        expect("model_hash", {"model_sha256": "0" * 64})
        expect("pointer_hash", {"checkpoint_pointer_sha256": "0" * 64})
        expect("byte_count", {"model_bytes": body["model_bytes"] + 1})
        expect("extra_field", {"extra": True})
        missing = dict(body)
        missing.pop("model_name")
        rejections["missing_field"] = _reason_for_manifest(missing)
        expect("wrong_source", {"source_revision": "0" * 40})
        expect("wrong_package", {"package_version": "0.0.0"})
        expect("wrong_model", {"model_name": "MossFormer2_SE_16K"})
        expect("wrong_rate", {"sample_rate_hz": 16000})
        expect("wrong_channels", {"channels": 2})
        expect("wrong_format", {"input_format": "int16"})
        expect("wrong_mode", {"mode": "streaming"})
        expect("wrong_license", {"license_decision": "unknown"})
        expect("pointer_content", {"checkpoint_file": "other.pt"})
        expect("placeholder_pinned", {"model_sha256": "f" * 64})

    accepted = {
        name: reason
        for name, reason in rejections.items()
        if name != "candidate_not_cleared"
    }
    return {
        "generic_admission": generic,
        "candidate_admission": {
            "accepted": False,
            "reason": candidate_reason,
            "rights_reason": rejections.get("candidate_not_cleared"),
        },
        "workspace_model_present": (
            workspace_root() / MODEL_PATH
        ).exists(),
        "rejected_all": all(
            reason not in ("accepted_unexpectedly", "") for reason in accepted.values()
        ) and candidate_reason == "asset_model_identity_unrecorded",
        "rejections": rejections,
    }


def _reason_for_manifest(manifest: Dict[str, Any]) -> str:
    try:
        validate_asset_manifest(manifest)
    except Reject as error:
        return error.reason
    return "accepted_unexpectedly"


def _control_config() -> Dict[str, Any]:
    rejections: Dict[str, str] = {}

    def expect(name: str, override: Dict[str, Any]) -> None:
        current = default_config()
        current.update(override)
        try:
            validate_config(current)
        except Reject as error:
            rejections[name] = error.reason
        else:
            rejections[name] = "accepted_unexpectedly"

    expect("sample_rate_16k", {"sample_rate_hz": INSTALLED_SAMPLE_RATE_HZ})
    expect("channels_stereo", {"channels": 2})
    expect("format_int16", {"input_format": "int16"})
    expect("frame_zero", {"frame_samples": 0})
    expect("frame_160", {"frame_samples": INSTALLED_FRAME_SAMPLES})
    expect("mode_streaming", {"mode": "streaming"})
    expect("real_runtime", {"real_runtime": True})
    expect("model_used", {"model_used": True})
    expect("resampling", {"resampling": "48k_to_16k"})
    expect("extra", {"extra": True})
    expect("negative_epoch", {"epoch": -1})
    expect("bool_epoch", {"epoch": True})
    expect("first_nonzero", {"first_input_sample": 1})
    expect("schema", {"schema_id": "audio-sdk/other"})
    return {
        "rejected_all": all(
            reason != "accepted_unexpectedly" for reason in rejections.values()
        ),
        "rejections": rejections,
        "accepted_config_digest": sha256_bytes(canonical_bytes(default_config())),
    }


def _control_chunks() -> Dict[str, Any]:
    session = Session()
    digest_before = session.state_digest()
    rejections: Dict[str, str] = {}
    cases: Dict[str, Any] = {
        "empty": [],
        "string": "abcd",
        "none": None,
        "nested": [[0.0]],
        "bool": [True],
        "nan": [float("nan")],
        "inf": [float("inf")],
        "neg_inf": [float("-inf")],
        "range": [1.5],
        "neg_range": [-1.5],
    }
    for name, chunk in cases.items():
        try:
            session.push(chunk)
        except Reject as error:
            rejections[name] = error.reason
        else:
            rejections[name] = "accepted_unexpectedly"
    digest_after = session.state_digest()
    accepted_after = session.accepted_samples
    session.push([0.0] * 480)
    return {
        "rejected_all": all(
            reason != "accepted_unexpectedly" for reason in rejections.values()
        ),
        "rejections": rejections,
        "state_unchanged": digest_before == digest_after,
        "accepted_after_rejections": accepted_after,
        "counter_after_accept": session.accepted_samples,
    }


def _control_silence() -> Dict[str, Any]:
    session = Session()
    session.push([0.0] * 2048)
    output = session.finish()
    return {
        "length": len(output),
        "exact_zero": all(value == 0 for value in output),
        "finite": True,
    }


def _control_chunking() -> Dict[str, Any]:
    fixture = build_fixture()
    values = float_samples(fixture["observed"][:12000])
    sizes = [1, 7, 160, 480, 481, 4096, 12000]
    results: Dict[str, Any] = {}
    reference_bytes: Optional[bytes] = None
    all_identical = True
    for size in sizes:
        session = Session()
        for start in range(0, len(values), size):
            session.push(values[start:start + size])
        output = session.finish()
        payload = int16_bytes(output)
        if reference_bytes is None:
            reference_bytes = payload
        identical = payload == reference_bytes
        all_identical = all_identical and identical
        results[str(size)] = {"byte_identical": identical, "samples": len(output)}
    return {"all_identical": all_identical, "chunks": results}


def _control_partial_tail() -> Dict[str, Any]:
    fixture = build_fixture()
    values = float_samples(fixture["observed"][:48123])
    full = Session()
    full.push(values)
    full_output = full.finish()
    split = Session()
    split.push(values[:24000])
    split.push(values[24000:])
    split_output = split.finish()
    return {
        "input_samples": len(values),
        "output_samples": len(full_output),
        "length_preserved": len(full_output) == len(values),
        "chunked_prefix_matches": int16_bytes(full_output) == int16_bytes(split_output),
    }


def _control_reset() -> Dict[str, Any]:
    fixture = build_fixture()
    values = float_samples(fixture["observed"][:4000])
    session = Session()
    session.push(values)
    first = session.state_digest()
    session.reset(1)
    session.push(values)
    after = int16_bytes(session.finish())
    fresh = Session(default_config(1))
    fresh.push(values)
    fresh_bytes = int16_bytes(fresh.finish())
    rejections: Dict[str, str] = {}
    digest_before_rejections = session.state_digest()
    for name, epoch in (("same", 1), ("lower", 0), ("negative", -1), ("bool", True)):
        try:
            session.reset(epoch)
        except Reject as error:
            rejections[name] = error.reason
        else:
            rejections[name] = "accepted_unexpectedly"
    stale_unchanged = session.state_digest() == digest_before_rejections
    session.reset(2)
    return {
        "fresh_matches_reset": after == fresh_bytes,
        "higher_epoch_accepted": session.epoch == 2,
        "epoch_rejections": rejections,
        "stale_digest_unchanged": stale_unchanged,
        "first_digest": first,
    }


def _control_nonfinite() -> Dict[str, Any]:
    session = Session()
    session.push([0.25] * 480)
    before = session.state_digest()
    accepted_before = session.accepted_samples
    try:
        session.push([float("nan")] * 160)
    except Reject as error:
        reason = error.reason
    else:
        reason = "accepted_unexpectedly"
    return {
        "reason": reason,
        "accepted_counter_unchanged": session.accepted_samples == accepted_before,
        "state_digest_unchanged": session.state_digest() == before,
        "counted_as_silence": False,
    }


def build_controls() -> Dict[str, Any]:
    return {
        "asset": _control_asset(),
        "config": _control_config(),
        "chunk": _control_chunks(),
        "silence": _control_silence(),
        "streaming_parity": _control_chunking(),
        "partial_tail": _control_partial_tail(),
        "reset": _control_reset(),
        "nonfinite_counter": _control_nonfinite(),
    }


# --------------------------------------------------------------------------
# Static report/contract payloads
# --------------------------------------------------------------------------

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "network_used": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "real_asset_read": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "surrogate_is_candidate": False,
    "task_board_or_handoff_write": False,
    "weights_vendored": False,
}

FORMAT: Dict[str, Any] = {
    "installed_v0_sample_rate_hz": INSTALLED_SAMPLE_RATE_HZ,
    "installed_v0_channels": INSTALLED_CHANNELS,
    "installed_v0_frame_samples": INSTALLED_FRAME_SAMPLES,
    "installed_v0_sample_format": "f32",
    "installed_v0_geometry_preserved": True,
    "candidate_declared_sample_rate_hz": SAMPLE_RATE_HZ,
    "candidate_declared_channels": CHANNELS,
    "candidate_declared_input_format": "float32",
    "candidate_proposed_hop_samples": FRAME_SAMPLES,
    "candidate_proposed_hop_ms": 10.0,
    "candidate_hop_is_proposal_only": True,
    "candidate_algorithmic_latency_samples": None,
    "candidate_algorithmic_delay_measured": False,
    "resampling_required_for_installed_v0": True,
    "resampling_implemented": False,
    "session_model": "offline_whole_clip",
}

SCENARIO: Dict[str, Any] = {
    "id": SCENARIO_ID,
    "task": "CLN-01",
    "mode": "offline",
    "is_streaming": False,
    "is_candidate": False,
    "is_aec": False,
    "note": (
        "Whole-utterance enhancement boundary probe only; the surrogate is not "
        "MossFormer2_SE_48K and no candidate output exists."
    ),
}

SURROGATE: Dict[str, Any] = {
    "type": "fixed_first_order_dc_blocker",
    "is_mossformer2": False,
    "model_free": True,
    "coefficient_num": DC_COEFFICIENT_NUM,
    "coefficient_den": DC_COEFFICIENT_DEN,
    "delay_samples": 0,
    "note": (
        "Mechanism probe for finite, deterministic, length-preserving whole-clip "
        "processing. It has no neural network, attention block, checkpoint or "
        "weights and cannot qualify the candidate."
    ),
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": SCHEMA_ASSET,
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "asset_is_loaded": False,
    "asset_is_executed": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_byte_count_sha256_pointer_and_geometry_only; "
        "do_not_load_or_execute_in_this_package"
    ),
    "required_fields": sorted(ASSET_FIELDS),
    "pinned_model_identity_recorded": False,
    "expected_model_path": MODEL_PATH,
    "expected_source_checkout": SOURCE_CHECKOUT_PATH,
    "expected_runtime_env": RUNTIME_ENV_PATH,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "model_path and checkpoint_pointer_path are caller-owned absolute paths",
        "model_bytes and SHA-256 equal the caller's model file",
        "checkpoint pointer SHA-256 matches and its stripped text names checkpoint_file",
        "source_revision, package_version, model_name, sample rate, channels, format and mode are pinned",
        "license_decision must be cleared only after a written artifact-rights decision",
        "the exact model artifact revision, byte count and SHA-256 must be recorded in a verified ledger",
        "no download, copy, build, import, load or execution occurs in this package",
    ],
    "weights_embedded_in_sdk": False,
}

EXACT_BLOCKERS: List[Dict[str, str]] = [
    {
        "id": "source_absent",
        "requirement": (
            "Supply the ClearerVoice-Studio source at pinned revision "
            "dcb1b20e1e44d435090072ab9b223c792ea1f624 as a caller-owned "
            "checkout or reproducible archive with its own SHA-256, without a "
            "network download."
        ),
        "state": (
            "data/checkouts/ClearerVoice-Studio is absent. No ClearerVoice "
            "source tree, submodule, wheel or sdist is present in this "
            "workspace, so no 48 kHz model code was read or executed."
        ),
    },
    {
        "id": "model_identity_unrecorded_and_absent",
        "requirement": (
            "Record the exact MossFormer2_SE_48K checkpoint identity: immutable "
            "model-card or artifact revision, filename, byte count and SHA-256, "
            "with the checkpoint pointer verified. Then supply the bytes as a "
            "caller-owned external asset."
        ),
        "state": (
            "No pinned local ledger records a MossFormer2_SE_48K checkpoint "
            "revision, filename, byte count or SHA-256. "
            "data/models/clearvoice/MossFormer2_SE_48K/last_best_checkpoint.pt "
            "is absent. A hash-matched placeholder is never accepted as the "
            "pinned model."
        ),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Admit an isolated, hash-pinned CPython runtime with the pinned "
            "clearvoice 0.1.2 package, PyTorch and the requirements lock; "
            "record wheel/sdist hashes, ABI, platform and product-use terms."
        ),
        "state": (
            "data/envs/clearvoice and the clearvoice package are absent. "
            "adapters/clearvoice/run.py is not imported or executed, and no "
            "runtime, ABI or timing evidence exists."
        ),
    },
    {
        "id": "rights_unresolved",
        "requirement": (
            "Supply written model-weight, training-data, corpus, "
            "redistribution, product-use and derivative-output terms plus the "
            "complete notice bundle for the exact checkpoint, runtime and "
            "48 kHz output, with a recorded legal review."
        ),
        "state": (
            "The code and model card are reported Apache-2.0, but upstream "
            "states open and private training data with undisclosed corpus "
            "exposure. Artifact-specific terms, redistribution and product-use "
            "clearance are not recorded."
        ),
    },
    {
        "id": "geometry_and_resampling_unqualified",
        "requirement": (
            "Establish the exact 48 kHz mono whole-utterance geometry, content "
            "delay, finite drain and any 48 kHz to installed 16 kHz mapping, "
            "including edge exclusions and output length."
        ),
        "state": (
            "No resampling, content-delay, drain or edge-exclusion "
            "implementation is present. Installed v0 remains 16 kHz mono f32 "
            "at 160 samples and was not changed."
        ),
    },
    {
        "id": "qualification_evidence_absent",
        "requirement": (
            "Reproduce approved exact-runtime outputs for frozen inputs, then "
            "score a rights-cleared paired 48 kHz clean/noisy cohort with "
            "independent SI-SDR/STOI or permitted listening, clean-preservation, "
            "peak/nonfinite controls, target-device timing and opt-in provider "
            "intake."
        ),
        "state": (
            "No exact output vector, rights-cleared cohort, independent score, "
            "listening result, target timing, provider intake or default "
            "decision exists."
        ),
    },
]

GATE_REQUIREMENTS: List[Tuple[str, str]] = [
    (
        "exact_source_and_model_identity",
        "Pinned ClearerVoice source revision plus an immutable MossFormer2_SE_48K "
        "artifact revision, byte count and SHA-256, verified pointer and "
        "caller-held bytes.",
    ),
    (
        "runtime_admission",
        "Hash-pinned isolated CPython/clearvoice 0.1.2/PyTorch runtime with "
        "archive, wheels, ABI, platform and distribution terms recorded.",
    ),
    (
        "artifact_and_training_rights",
        "Weight, training-data, corpus, runtime, redistribution, product-use and "
        "derivative-output rights cleared with complete notices and legal review.",
    ),
    (
        "exact_reference_parity_48k",
        "Approved exact-runtime MossFormer2_SE_48K output vectors and byte-level "
        "parity on the declared 48 kHz mono geometry.",
    ),
    (
        "rights_cleared_paired_cohort",
        "Frozen rights-cleared paired 48 kHz clean/noisy corpus, strata, edge "
        "exclusions, content delay and reset schedule.",
    ),
    (
        "independent_scoring_and_listening",
        "Independent SI-SDR/STOI or permitted listening, identity and "
        "task-matched baselines, failure/nonfinite controls and clean preservation.",
    ),
    (
        "target_runtime_timing_and_resampling",
        "Target-device p50/p95/p99, RTF, memory, deadline, whole-clip availability "
        "and the exact 48 kHz to installed 16 kHz mapping.",
    ),
    (
        "opt_in_provider_intake_and_default",
        "Opt-in provider intake, descriptor/asset review, OFF default and an "
        "explicit owner default decision.",
    ),
]


def gates() -> List[Dict[str, str]]:
    return [
        {"id": gate_id, "requirement": requirement, "status": "blocked"}
        for gate_id, requirement in GATE_REQUIREMENTS
    ]


def release_gate_ids() -> List[str]:
    return [gate_id for gate_id, _ in GATE_REQUIREMENTS]


NEGATIVE_CLAIMS = [
    "No MossFormer2_SE_48K output, checkpoint, derived weight, import or runtime call was produced.",
    "No enhancement, quality, intelligibility, latency, device, benchmark or release result is claimed.",
    "The synthetic DC-blocker surrogate is not MossFormer2_SE_48K and cannot qualify the candidate.",
    "No real corpus, clean reference, audio, device clock or listener was used.",
    "No provider, descriptor, registry, installed v0 path, shared build, dependency lock or CI was changed.",
    "No source, wheel, checkpoint or model card was downloaded, copied, vendored or redistributed.",
    "Identity is the only paired control; no surrogate or source-reported value is promoted to a pass.",
]

MISSING_RESULTS = [
    "exact MossFormer2_SE_48K inference output",
    "verified checkpoint identity and bytes",
    "admitted clearvoice/PyTorch runtime",
    "artifact-specific rights decision",
    "rights-cleared paired 48 kHz clean/noisy cohort",
    "independent SI-SDR/STOI score or permitted listening",
    "target-device timing, memory and deadline",
    "48 kHz to installed 16 kHz mapping and opt-in provider intake",
]

INVARIANTS = [
    "decision is DEFER and qualification is not_qualified",
    "no missing, blocked or rejected result is promoted to a pass",
    "no candidate artifact is downloaded, copied, loaded or executed",
    "no model, runtime or corpus claim is made from observed presence",
    "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
    "only this task-local evidence directory is written",
    "the mutable full task board is never hashed or read into this package",
]

REOPEN_CONDITION = (
    "Supply the pinned ClearerVoice source and the exact MossFormer2_SE_48K "
    "checkpoint identity and bytes, admit a hash-pinned clearvoice/PyTorch "
    "runtime, clear all artifact and corpus rights, establish the 48 kHz mono "
    "geometry and installed-16-kHz mapping, reproduce exact outputs, score a "
    "rights-cleared paired cohort independently, measure target timing and "
    "complete opt-in provider intake with an OFF default. Until then the "
    "candidate stays DEFER, incomplete and not qualified."
)

LOCAL_FILES = sorted(
    [
        "README.md",
        "SOURCES.sha256",
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
    ]
)

EXPECTED_DIR_FILES = set(LOCAL_FILES)


def acceptance_profile() -> Dict[str, Any]:
    return {
        "name": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "mapped_cases": [
            "identity/noisy control on the same frozen 48 kHz synthetic clip",
            "clean-speech preservation, peak and nonfinite-output bounds",
            "silence exactness and length preservation",
            "arbitrary chunking and reset replay parity",
            "fail-closed caller-asset, configuration and nonfinite rejection",
        ],
        "not_applicable": [
            "no MossFormer2_SE_48K checkpoint or admitted runtime, so no exact output is reproduced",
            "no rights-cleared real cohort, so no generalization or quality claim is made",
            "no paired baseline result, so the mechanism probe is not a task-matched baseline",
            "no target device, so no timing, memory or deadline result is claimed",
            "no independent listening, ASR or intrusive perceptual score is performed",
        ],
    }


def board_row() -> Dict[str, Any]:
    return {
        "full_tasks_json_hashed": False,
        "stable_fields": dict(BOARD_ROW_STABLE_FIELDS),
        "stable_sha256": BOARD_ROW_STABLE_SHA256,
        "note": (
            "Only the stable linked-row identity is gated. The mutable full "
            "plan/swarm/TASKS.json is never read into, hashed by or pinned to "
            "this package."
        ),
    }


def upstream() -> Dict[str, Any]:
    return {
        "repository": UPSTREAM_REPOSITORY,
        "source_revision": UPSTREAM_SOURCE_REVISION,
        "package": UPSTREAM_PACKAGE_IDENTITY,
        "package_version": UPSTREAM_PACKAGE_VERSION,
        "code_license": UPSTREAM_CODE_LICENSE,
        "model_name": MODEL_NAME,
        "model_repository": MODEL_REPOSITORY,
        "model_card_license_reported": MODEL_CARD_LICENSE_REPORTED,
        "model_checkpoint_filename_hint": MODEL_FILENAME_HINT,
        "model_artifact_identity_recorded": False,
        "training_data_disclosure": "open_and_private_undisclosed_exposure",
    }


def asset_pins() -> Dict[str, Any]:
    workspace = workspace_root()
    return {
        "model_checkpoint": {
            "present": (workspace / MODEL_PATH).exists(),
            "loaded": False,
            "executed": False,
            "expected_path": MODEL_PATH,
            "filename_hint": MODEL_FILENAME_HINT,
            "identity_recorded": False,
            "byte_count": None,
            "sha256": None,
        },
        "source_checkout": {
            "present": (workspace / SOURCE_CHECKOUT_PATH).exists(),
            "imported": False,
            "executed": False,
            "expected_path": SOURCE_CHECKOUT_PATH,
            "source_revision": UPSTREAM_SOURCE_REVISION,
        },
        "runtime_environment": {
            "present": (workspace / RUNTIME_ENV_PATH).exists(),
            "admitted": False,
            "imported": False,
            "executed": False,
            "expected_path": RUNTIME_ENV_PATH,
        },
    }


def claim() -> Dict[str, Any]:
    return {
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": WORKTREE,
    }


def task_row_identity() -> Dict[str, Any]:
    return {
        "stable_fields": dict(BOARD_ROW_STABLE_FIELDS),
        "stable_sha256": BOARD_ROW_STABLE_SHA256,
        "full_tasks_json_hashed": False,
        "full_tasks_json_read": False,
        "gate": "stable linked-row identity only",
    }


def contract_dict() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "acceptance_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "release_gate_count": len(GATE_REQUIREMENTS),
            "all_blocked": True,
            "release_gates": release_gate_ids(),
        },
        "qualification_status": QUALIFICATION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX + " and its own fixtures only",
        "task_row_identity": task_row_identity(),
        "board_row": board_row(),
        "scope": {
            "task_local_only": True,
            "writes": [TASK_PREFIX],
            "reads_real_audio": False,
            "reads_model_or_runtime": False,
            "network_used": False,
        },
        "boundary": BOUNDARY,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream": upstream(),
        "asset_requirements": {
            "model_path": MODEL_PATH,
            "model_identity_recorded": False,
            "model_sha256": None,
            "model_bytes": None,
            "source_checkout_path": SOURCE_CHECKOUT_PATH,
            "runtime_env_path": RUNTIME_ENV_PATH,
            "rights_decision_required": True,
        },
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "release_gates": gates(),
        "gates": gates(),
        "format": FORMAT,
        "scenario": SCENARIO,
        "invariants": list(INVARIANTS),
        "local_files": list(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "reopen_condition": REOPEN_CONDITION,
        "reproduction": {
            "python": "3.12",
            "third_party_dependencies": [],
            "regeneration_rounds": 3,
            "entrypoints": ["run.py", "test_reference.py", "verify.py"],
            "source_root_env": "SOURCE_ROOT",
        },
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_dict())


def build_report(contract_sha256: Optional[str] = None) -> Dict[str, Any]:
    if contract_sha256 is None:
        contract_sha256 = sha256_bytes(contract_bytes())
    metrics = build_metrics()
    controls = build_controls()
    fixture = build_fixture()
    return {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "claim": claim(),
        "profile": PROFILE,
        "acceptance_profile": acceptance_profile(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "release_gate_count": len(GATE_REQUIREMENTS),
            "all_blocked": True,
            "release_gates": release_gate_ids(),
        },
        "qualification_status": QUALIFICATION,
        "board_row": board_row(),
        "boundary": BOUNDARY,
        "upstream": upstream(),
        "asset_pins": asset_pins(),
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": gates(),
        "format": FORMAT,
        "scenario": SCENARIO,
        "surrogate": SURROGATE,
        "fixture": {
            "fixture_id": FIXTURE_ID,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": "int16_boundary_float32_exposed",
            "total_samples": TOTAL_SAMPLES,
            "duration_ms": 4000,
            "segments": fixture_spec(),
            "spec_digest": FIXTURE_SPEC_DIGEST,
            "component_digests": FIXTURE_DIGESTS,
            "clean_samples": len(fixture["clean"]),
            "noise_samples": len(fixture["noise"]),
            "observed_samples": len(fixture["observed"]),
        },
        "metrics": metrics,
        "controls": controls,
        "missing_results": list(MISSING_RESULTS),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "reopen_condition": REOPEN_CONDITION,
        "contract_sha256": contract_sha256,
    }


def canonical_report_bytes(report: Optional[Dict[str, Any]] = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)


# --------------------------------------------------------------------------
# Pin manifest helpers
# --------------------------------------------------------------------------

PIN_PATTERN = re.compile(r"^([0-9a-f]{64})  ([^ ].+)$")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    pins: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        match = PIN_PATTERN.match(line)
        if match is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, key = match.groups()
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        seen.add(key)
        pins.append((digest, key))
    if not pins:
        raise ValueError("empty_pin_manifest")
    return pins


def resolve_source_path(relative: str) -> Path:
    if relative.startswith("/") or ".." in Path(relative).parts:
        raise ValueError("unsafe_source_path:" + relative)
    root = workspace_root()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("outside_source_root:" + relative)
    return path


def workspace_root() -> Path:
    raw = os.environ.get("SOURCE_ROOT", DEFAULT_SOURCE_ROOT)
    return Path(raw).resolve()


def artifact_files() -> List[str]:
    return [
        name for name in sorted(EXPECTED_DIR_FILES)
        if name != "SOURCES.sha256"
    ]


def allowed_pin_keys() -> set:
    keys = {TASK_PREFIX + "/" + name for name in artifact_files()}
    keys.update(BOUNDARY_PINS)
    keys.update(SOURCE_PINS)
    return keys


def sources_bytes() -> bytes:
    here = Path(__file__).resolve().parent
    lines = [
        "# SHA-256 pins for " + TASK + " task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# Full mutable plan/swarm/TASKS.json is never hashed; only "
        "board_row.stable_sha256=" + BOARD_ROW_STABLE_SHA256 + " is gated.",
    ]
    for name in artifact_files():
        path = here / name
        if not path.is_file():
            raise FileNotFoundError(name)
        lines.append(
            f"{sha256_file(path)}  {TASK_PREFIX}/{name}"
        )
    for key in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[key]}  {key}")
    for key in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[key]}  {key}")
    return ("\n".join(lines) + "\n").encode("ascii")


def check_pin_targets() -> Dict[str, str]:
    here = Path(__file__).resolve().parent
    sdk_root = here.parents[2]
    results: Dict[str, str] = {}
    for name in artifact_files():
        results[TASK_PREFIX + "/" + name] = sha256_file(here / name)
    for key, digest in BOUNDARY_PINS.items():
        path = sdk_root / key.split(":", 1)[1]
        results[key] = sha256_file(path) if path.is_file() else "missing"
        if results[key] != digest:
            results[key] += " (stale)"
    for key, digest in SOURCE_PINS.items():
        try:
            path = resolve_source_path(key.split(":", 1)[1])
        except ValueError:
            results[key] = "unsafe"
            continue
        results[key] = sha256_file(path) if path.is_file() else "missing"
        if results[key] != digest:
            results[key] += " (stale)"
    return results


# --------------------------------------------------------------------------
# README table generation
# --------------------------------------------------------------------------

SOURCE_TABLE_START = "<!-- DIGEST_TABLE_SOURCE_START -->"
SOURCE_TABLE_END = "<!-- DIGEST_TABLE_SOURCE_END -->"
BOUNDARY_TABLE_START = "<!-- DIGEST_TABLE_BOUNDARY_START -->"
BOUNDARY_TABLE_END = "<!-- DIGEST_TABLE_BOUNDARY_END -->"
ARTIFACT_TABLE_START = "<!-- DIGEST_TABLE_ARTIFACTS_START -->"
ARTIFACT_TABLE_END = "<!-- DIGEST_TABLE_ARTIFACTS_END -->"
RESULTS_TABLE_START = "<!-- RESULTS_TABLE_START -->"
RESULTS_TABLE_END = "<!-- RESULTS_TABLE_END -->"
GATES_TABLE_START = "<!-- GATES_TABLE_START -->"
GATES_TABLE_END = "<!-- GATES_TABLE_END -->"

README_SECTIONS = ("source", "boundary", "artifacts")


def _replace_block(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end), re.DOTALL
    )
    if pattern.search(text) is None:
        raise ValueError("missing_readme_markers:" + start)
    return pattern.sub(start + "\n" + body.rstrip("\n") + "\n" + end, text)


def _pin_table(pins: Dict[str, str]) -> str:
    rows = ["| Key | SHA-256 |", "| --- | --- |"]
    for key in sorted(pins):
        rows.append(f"| `{key}` | `{pins[key]}` |")
    return "\n".join(rows)


def _artifact_table() -> str:
    here = Path(__file__).resolve().parent
    rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    for name in sorted(EXPECTED_DIR_FILES):
        if name in ("README.md", "SOURCES.sha256"):
            continue
        path = here / name
        if not path.is_file():
            raise FileNotFoundError(name)
        rows.append(
            f"| `{name}` | `{sha256_file(path)}` | {path.stat().st_size} |"
        )
    return "\n".join(rows)


def _result_table(report: Dict[str, Any]) -> str:
    metrics = report["metrics"]
    rows = [
        "| Metric | Identity (noisy) | DC-blocker probe |",
        "| --- | ---: | ---: |",
    ]

    def cell(value: Any) -> str:
        if value is None:
            return "n/a"
        return f"{value:.9f}" if isinstance(value, float) else str(value)

    rows.append(
        f"| SNR vs clean (dB) | {cell(metrics['identity']['snr_db'])} | "
        f"{cell(metrics['surrogate']['snr_db'])} |"
    )
    rows.append(
        f"| SI-SDR vs clean (dB) | {cell(metrics['identity']['si_sdr_db'])} | "
        f"{cell(metrics['surrogate']['si_sdr_db'])} |"
    )
    rows.append(
        f"| Target retention | {cell(metrics['identity']['target_retention'])} | "
        f"{cell(metrics['surrogate']['target_retention'])} |"
    )
    rows.append(
        f"| Delta SI-SDR (dB) | n/a | {cell(metrics['delta_si_sdr_db'])} |"
    )
    rows.append("")
    rows.append("| Stratum | Identity SI-SDR (dB) | Probe SI-SDR (dB) |")
    rows.append("| --- | ---: | ---: |")
    for name, stratum in metrics["strata"].items():
        rows.append(
            f"| `{name}` | {cell(stratum['identity']['si_sdr_db'])} | "
            f"{cell(stratum['surrogate']['si_sdr_db'])} |"
        )
    return "\n".join(rows)


def _gates_table() -> str:
    rows = ["| Gate | Status | Requirement |", "| --- | --- | --- |"]
    for gate in gates():
        rows.append(
            f"| `{gate['id']}` | `{gate['status']}` | {gate['requirement']} |"
        )
    return "\n".join(rows)


def update_readme_tables(text: str,
                         report: Optional[Dict[str, Any]] = None,
                         sections: Sequence[str] = README_SECTIONS) -> str:
    if report is None:
        report = build_report()
    if "source" in sections:
        text = _replace_block(
            text, SOURCE_TABLE_START, SOURCE_TABLE_END, _pin_table(SOURCE_PINS)
        )
    if "boundary" in sections:
        text = _replace_block(
            text, BOUNDARY_TABLE_START, BOUNDARY_TABLE_END,
            _pin_table(BOUNDARY_PINS)
        )
    if "artifacts" in sections:
        text = _replace_block(
            text, ARTIFACT_TABLE_START, ARTIFACT_TABLE_END, _artifact_table()
        )
    text = _replace_block(
        text, RESULTS_TABLE_START, RESULTS_TABLE_END, _result_table(report)
    )
    text = _replace_block(
        text, GATES_TABLE_START, GATES_TABLE_END, _gates_table()
    )
    return text


def _parse_readme_table(text: str, start: str, end: str) -> List[str]:
    pattern = re.compile(
        re.escape(start) + r"(.*?)" + re.escape(end), re.DOTALL
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError("missing_readme_markers:" + start)
    rows = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("| `") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            rows.append(cells[0].strip("`"))
    return rows


def expected_readme_keys() -> Dict[str, set]:
    return {
        "source": set(SOURCE_PINS),
        "boundary": set(BOUNDARY_PINS),
        "artifacts": {
            name for name in EXPECTED_DIR_FILES
            if name not in ("README.md", "SOURCES.sha256")
        },
    }


def verify_readme_digests(text: str,
                          sections: Sequence[str] = README_SECTIONS
                          ) -> Dict[str, int]:
    expected = expected_readme_keys()
    counts: Dict[str, int] = {}
    parsers = {
        "source": (SOURCE_TABLE_START, SOURCE_TABLE_END),
        "boundary": (BOUNDARY_TABLE_START, BOUNDARY_TABLE_END),
        "artifacts": (ARTIFACT_TABLE_START, ARTIFACT_TABLE_END),
    }
    for section in sections:
        start, end = parsers[section]
        counts[section] = len(_parse_readme_table(text, start, end))
    for section, count in counts.items():
        keys = expected[section]
        if count != len(keys):
            raise ValueError("readme_section_count:" + section)
    return counts


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a": 1, "a": 2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '{"a": 1} trailing',
        "[]",
        '{"a": 1,}',
    ]
    bad_pins = [
        "deadbeef  key",
        "0" * 64 + "  key\n" + "1" * 64 + "  key",
        "0" * 64 + " key",
    ]
    bad_readme = [
        "no markers here",
        SOURCE_TABLE_START + "\n" + SOURCE_TABLE_END,
        ARTIFACT_TABLE_START + "\n" + ARTIFACT_TABLE_END,
    ]
    json_rejected = 0
    for text in bad_json:
        try:
            strict_object_loads(text)
        except (ValueError, TypeError):
            json_rejected += 1
    pin_rejected = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            pin_rejected += 1
    readme_rejected = 0
    for text in bad_readme:
        try:
            verify_readme_digests(text)
        except (ValueError, TypeError):
            readme_rejected += 1
    return {
        "bad_json_total": len(bad_json),
        "bad_json_rejected": json_rejected,
        "bad_pins_total": len(bad_pins),
        "bad_pins_rejected": pin_rejected,
        "bad_readme_total": len(bad_readme),
        "bad_readme_rejected": readme_rejected,
    }
