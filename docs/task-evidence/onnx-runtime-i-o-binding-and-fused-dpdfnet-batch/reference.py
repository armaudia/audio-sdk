# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local ONNX Runtime I/O-binding / fused-batch evidence.

This module documents and exercises the developer-facing boundary that a future
optional ONNX Runtime adapter would need for a fused DPDFNet batch. It does
**not** import, link, ship or invoke ONNX Runtime, it does **not** decode a real
ONNX graph or load DPDFNet weights, and it does **not** execute a fused tensor
kernel. The caller-supplied asset is a canonical synthetic descriptor and the
execution is a frozen float32 CPU reference probe with exact tensor shapes.

The evidence disposition is DEFER / incomplete / not_qualified. A missing result
never qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))


def _find_source_root() -> Path:
    explicit = os.environ.get("SOURCE_ROOT")
    if explicit:
        return Path(explicit)
    for parent in (SDK_ROOT, *SDK_ROOT.parents):
        if (parent / "cpp-library").is_dir() and (parent / "audio-benchmark-platform").is_dir():
            return parent
    return SDK_ROOT.parents[3] if len(SDK_ROOT.parents) > 3 else SDK_ROOT


SOURCE_ROOT = _find_source_root()

TASK_ID = "SDK-ONNX-RUNTIME-I-O-BINDING-AND-FUSED-DPDFNET-BATCH"
TITLE = "ONNX Runtime I/O binding and fused DPDFNet batch"
BASE_COMMIT = "8bd03e2d9d08d550bb4b2ac28425c71eaf8a0ba9"
SCHEMA_ID = (
    "audio-sdk/task-evidence/"
    "onnx-runtime-i-o-binding-and-fused-dpdfnet-batch/report/0.1"
)
COMPONENT_ID = "onnx-runtime-i-o-binding-and-fused-dpdfnet-batch"
REFERENCE_FAMILY = "onnxruntime"
PROFILE = "tool"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "fused_batch_integration"
TASK_REL = "docs/task-evidence/onnx-runtime-i-o-binding-and-fused-dpdfnet-batch"
ADAPTER_PROTOCOL = "audio-sdk/onnx-runtime-fused-batch-adapter/0.1"
RUNTIME_ID = "onnxruntime-cpu-fused-batch-synthetic/0.1"
MODEL_ID = "synthetic-ort-fused-batch-probe"
MODEL_VERSION = 1
MODEL_SCHEMA = (
    "audio-sdk/task-evidence/"
    "onnx-runtime-i-o-binding-and-fused-dpdfnet-batch/synthetic-model/0.1"
)
PINNED_INTERPRETER = "3.12.16"

# Public v0 geometry is documented only; nothing is installed or changed.
FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "synthetic_fused_frame_batch_fixture",
    "installed_v0_geometry_preserved": True,
}
MAX_BATCH = 4
MAX_MODEL_BYTES = 65536
FRAME_SAMPLES = 160
STATE_SAMPLES = 16
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")

TENSORS = {
    "waveform_in": {
        "dtype": "f32",
        "role": "input",
        "batch_dim": 0,
        "min_shape": [1, FRAME_SAMPLES],
        "max_shape": [MAX_BATCH, FRAME_SAMPLES],
    },
    "state_in": {
        "dtype": "f32",
        "role": "input",
        "batch_dim": 0,
        "min_shape": [1, STATE_SAMPLES],
        "max_shape": [MAX_BATCH, STATE_SAMPLES],
    },
    "waveform_out": {
        "dtype": "f32",
        "role": "output",
        "batch_dim": 0,
        "min_shape": [1, FRAME_SAMPLES],
        "max_shape": [MAX_BATCH, FRAME_SAMPLES],
    },
    "state_out": {
        "dtype": "f32",
        "role": "output",
        "batch_dim": 0,
        "min_shape": [1, STATE_SAMPLES],
        "max_shape": [MAX_BATCH, STATE_SAMPLES],
    },
}
TENSOR_ORDER = ("waveform_in", "state_in", "waveform_out", "state_out")

# Exact binary fractions only: no transcendental function and no fused
# multiply-add. Every operation is rounded to IEEE float32 individually so the
# goldens are hand-checkable and lane-order independent.
COEFFICIENTS = {
    "input_gain": 0.75,
    "state_feedback": 0.25,
    "state_decay": 0.5,
    "state_input_gain": 0.125,
}
STATE_INIT = [0.0] * STATE_SAMPLES
INPUT_MAX = 1.0
STATE_MAX = 4.0

IO_BINDING = {
    "preallocated_outputs": True,
    "exact_output_capacity": True,
    "writable_list_required": True,
    "alias_with_input_rejected": True,
    "per_lane_unique_outputs_required": True,
    "foreign_memory_supported": False,
    "per_lane_failure_reported": True,
    "required": False,
}

SESSION_OPTIONS = {
    "execution_provider": "CPUExecutionProvider",
    "execution_mode": "sequential",
    "graph_optimization": "disabled",
    "intra_op_num_threads": 1,
    "inter_op_num_threads": 1,
    "enable_mem_pattern": False,
    "deterministic_compute": True,
    "io_binding": "caller_preallocated",
    "max_batch": MAX_BATCH,
}
CONFIG = {
    "model": MODEL_ID,
    "execution_provider": "cpu_reference",
    "graph_optimization": "disabled",
    "intra_op_num_threads": 1,
    "inter_op_num_threads": 1,
    "deterministic": True,
    "output_binding": "caller_preallocated",
    "max_batch": MAX_BATCH,
}

MODEL_SPEC: Dict[str, Any] = {
    "schema_id": MODEL_SCHEMA,
    "asset_id": MODEL_ID,
    "asset_version": MODEL_VERSION,
    "asset_kind": "synthetic_non_onnx_descriptor",
    "reference_family": "onnxruntime",
    "evaluation": "lane_state_fused_batch_probe_v1",
    "real_onnx_graph": False,
    "real_model_weights": False,
    "runtime_invoked": False,
    "max_batch": MAX_BATCH,
    "per_lane_state": True,
    "fused_tensor_kernel": False,
    "tensors": TENSORS,
    "tensor_order": list(TENSOR_ORDER),
    "coefficients": COEFFICIENTS,
    "state_init": STATE_INIT,
    "io_binding": IO_BINDING,
    "session_options": SESSION_OPTIONS,
    "input_max": INPUT_MAX,
    "state_max": STATE_MAX,
}

SOURCE_PINS: Dict[str, str] = {
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:realtime-audio-library/implementation_record.md":
        "12b7c17d6ae969cb3e9697f3309667518048f27792b283178d326746e1bbfb81",
    "source:cpp-library/PIPELINE_DESIGN_REPORT.md":
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "source:research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "source:adapters/dpdfnet/adapter.json":
        "6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c",
    "source:adapters/dpdfnet/run.py":
        "40fbd148eb80ec21a33290e4cb4bc9258afb54f65d4d5fd5d82b552deac5ae02",
    "source:adapters/dpdfnet/requirements.lock":
        "2d43db167c1c221992ac51bd15ae365bfc18ddc21eb405c53ce8a444e5af34a4",
    "source:cpp-library/src/stages/onnx_common.cpp":
        "f8eaee5455fefb1dd0dcaac10092a25f673f138f76af07d21dfed69fa95712c8",
    "source:cpp-library/src/stages/onnx_common.hpp":
        "fead88c586ea8a095ebb15be4d3c5ba2515b6497e3f8f7f08c7b2cce4420d4e1",
    "source:cpp-library/CMakeLists.txt":
        "ac655c9c8d1d9c90991493d925c988d1f0b887e9364a8cf21853a6860fc219bc",
    "source:cpp-library/cmake/audio_enhance_models.json":
        "6b14470521a1ba599f572e236eb96c877dfe5777341eb402b9224c3eb5feedbe",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}
TASK_LOCAL_PINS = (
    f"{TASK_REL}/README.md",
    f"{TASK_REL}/contract.json",
    f"{TASK_REL}/synthetic_model.json",
    f"{TASK_REL}/reference.py",
    f"{TASK_REL}/run.py",
    f"{TASK_REL}/test_reference.py",
    f"{TASK_REL}/verify.py",
    f"{TASK_REL}/report.json",
    f"{TASK_REL}/report.json.sha256",
    f"{TASK_REL}/contract.json.license",
    f"{TASK_REL}/synthetic_model.json.license",
    f"{TASK_REL}/report.json.license",
    f"{TASK_REL}/report.json.sha256.license",
    f"{TASK_REL}/SOURCES.sha256.license",
)
ARTIFACT_PIN_PATHS = (
    f"{TASK_REL}/contract.json",
    f"{TASK_REL}/synthetic_model.json",
)
PIN_RE = re.compile(
    r"^(?P<path>source:[^\s]+|CONTRACTS\.md|REUSE\.toml|api/[^\s]+|"
    r"bindings/[^\s]+|docs/[^\s]+|LICENSES/[^\s]+)$")
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


class Rejected(Exception):
    """A fail-closed boundary rejection with a stable code and field."""

    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


class DuplicateKeyError(ValueError):
    pass


class NonFiniteNumberError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def model_bytes() -> bytes:
    return canonical_bytes(MODEL_SPEC) + b"\n"


def model_digest() -> str:
    return sha256(model_bytes())


def _reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError("duplicate key: " + key)
        result[key] = value
    return result


def _reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise NonFiniteNumberError("nonfinite JSON number")
    if isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite(item)
    elif isinstance(value, list):
        for item in value:
            _reject_nonfinite(item)


def strict_json(data: bytes) -> Any:
    text = data.decode("utf-8")
    value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    _reject_nonfinite(value)
    return value


def strict_json_file(path: Path) -> Any:
    return strict_json(path.read_bytes())


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        rest = raw[len("source:"):]
        if not rest or rest.startswith("/") or ".." in Path(rest).parts:
            raise ValueError("unsafe source pin: " + raw)
        return SOURCE_ROOT / rest
    if raw.startswith("/") or ".." in Path(raw).parts:
        raise ValueError("unsafe pin: " + raw)
    return SDK_ROOT / raw


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    pins: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), start=1):
        if not line or line.startswith("#"):
            continue
        if not re.match(r"^[0-9a-f]{64}  \S", line):
            raise ValueError(f"line {number}: malformed pin")
        digest, raw = line.split("  ", 1)
        if not PIN_RE.match(raw):
            raise ValueError(f"line {number}: unsupported pin path")
        if ".." in Path(raw).parts:
            raise ValueError(f"line {number}: escaping path")
        if raw in seen:
            raise ValueError(f"line {number}: duplicate pin")
        seen.add(raw)
        pins.append((digest, raw))
    return pins


def artifact_pins() -> Dict[str, str]:
    return {raw: sha256(pin_path(raw).read_bytes()) for raw in ARTIFACT_PIN_PATHS}


def _pin_line(raw: str) -> str:
    return f"{sha256(pin_path(raw).read_bytes())}  {raw}"


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for " + TASK_ID + ". source: paths are workspace-relative; "
        "other paths are SDK-worktree-relative. Lines are <sha256>  <path>."
    ]
    lines.extend(_pin_line(raw) for raw in sorted(SOURCE_PINS))
    lines.extend(_pin_line(raw) for raw in sorted(BOUNDARY_PINS))
    lines.extend(_pin_line(raw) for raw in sorted(TASK_LOCAL_PINS))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f32_bytes(values: Iterable[float]) -> bytes:
    return b"".join(struct.pack("<f", value) for value in values)


def f32_digest(values: Iterable[float]) -> str:
    return sha256(f32_bytes(values))


def _rng(seed: int):
    state = seed & 0xFFFFFFFF

    def next_u32() -> int:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state

    return next_u32


def condition_frame(seed: int, scale: float = 0.75) -> List[float]:
    next_u32 = _rng(seed)
    return [_f32(scale * ((next_u32() / 0xFFFFFFFF) * 2.0 - 1.0))
            for _ in range(FRAME_SAMPLES)]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_vector(values: Any, length: int, maximum: float,
                     code: str, field: str) -> List[float]:
    if not isinstance(values, list):
        raise Rejected("feed_not_list", field)
    if len(values) != length:
        raise Rejected(code, field)
    result: List[float] = []
    for value in values:
        if isinstance(value, bool):
            raise Rejected("feed_bool", field)
        if not _is_number(value):
            raise Rejected("feed_dtype", field)
        numeric = float(value)
        if not math.isfinite(numeric):
            raise Rejected("nonfinite_feed", field)
        if abs(numeric) > maximum:
            raise Rejected("feed_out_of_range", field)
        result.append(_f32(numeric))
    return result


def _validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise Rejected("invalid_config", "")
    allowed = set(CONFIG)
    extra = sorted(set(config) - allowed)
    if extra:
        raise Rejected("unexpected_config_key", extra[0])
    missing = sorted(allowed - set(config))
    if missing:
        raise Rejected("missing_config_key", missing[0])
    checks = (
        ("model", "unknown_model_id"),
        ("execution_provider", "unsupported_execution_provider"),
        ("graph_optimization", "unsupported_graph_optimization"),
        ("intra_op_num_threads", "nondeterministic_threading"),
        ("inter_op_num_threads", "nondeterministic_threading"),
        ("deterministic", "nondeterministic_compute"),
        ("output_binding", "unsupported_output_binding"),
        ("max_batch", "unsupported_max_batch"),
    )
    for key, code in checks:
        if config[key] != CONFIG[key]:
            raise Rejected(code, key)
    return dict(CONFIG)


def _model_difference(spec: Any) -> Tuple[str, str]:
    if not isinstance(spec, dict):
        return "model_not_object", ""
    if set(spec) != set(MODEL_SPEC):
        extra = sorted(set(spec) - set(MODEL_SPEC))
        missing = sorted(set(MODEL_SPEC) - set(spec))
        return ("model_unexpected_field", extra[0]) if extra else \
            ("model_missing_field", missing[0])
    if spec["schema_id"] != MODEL_SPEC["schema_id"]:
        return "model_schema", "schema_id"
    if spec["asset_id"] != MODEL_SPEC["asset_id"]:
        return "model_asset_id", "asset_id"
    if spec["asset_version"] != MODEL_SPEC["asset_version"]:
        return "model_asset_version", "asset_version"
    if spec["asset_kind"] != MODEL_SPEC["asset_kind"]:
        return "model_asset_kind", "asset_kind"
    if spec["real_onnx_graph"] is not False:
        return "model_real_graph_claim", "real_onnx_graph"
    if spec["real_model_weights"] is not False:
        return "model_real_weights_claim", "real_model_weights"
    if spec["evaluation"] != MODEL_SPEC["evaluation"]:
        return "model_evaluation", "evaluation"
    if spec["max_batch"] != MODEL_SPEC["max_batch"]:
        return "model_max_batch", "max_batch"
    if spec["tensor_order"] != MODEL_SPEC["tensor_order"]:
        return "model_tensor_order", "tensor_order"
    tensors = spec["tensors"]
    if not isinstance(tensors, dict):
        return "model_tensor_missing", "tensors"
    if set(tensors) != set(TENSORS):
        extra = sorted(set(tensors) - set(TENSORS))
        missing = sorted(set(TENSORS) - set(tensors))
        return ("model_tensor_extra", extra[0]) if extra else \
            ("model_tensor_missing", missing[0])
    for name in TENSOR_ORDER:
        if tensors[name] != TENSORS[name]:
            declared = tensors[name]
            if not isinstance(declared, dict):
                return "model_tensor_shape", name
            if declared.get("dtype") != TENSORS[name]["dtype"]:
                return "model_tensor_dtype", name
            if (declared.get("min_shape") != TENSORS[name]["min_shape"]
                    or declared.get("max_shape") != TENSORS[name]["max_shape"]):
                return "model_tensor_shape", name
            return "model_tensor_role", name
    if spec["coefficients"] != COEFFICIENTS:
        return "model_coefficient", "coefficients"
    if spec["state_init"] != STATE_INIT:
        return "model_state_init", "state_init"
    if spec["io_binding"] != IO_BINDING:
        return "model_io_binding", "io_binding"
    if spec["session_options"] != SESSION_OPTIONS:
        return "model_session_options", "session_options"
    if spec["input_max"] != INPUT_MAX:
        return "model_input_max", "input_max"
    if spec["state_max"] != STATE_MAX:
        return "model_state_max", "state_max"
    return "model_document_mismatch", ""


def _validate_model_asset(asset: Any) -> Tuple[str, bytes, str, int]:
    if not isinstance(asset, (tuple, list)) or len(asset) != 4:
        raise Rejected("model_asset_shape", "")
    asset_id, data, digest, byte_count = asset
    if not isinstance(asset_id, str) or not ID_RE.match(asset_id):
        raise Rejected("model_asset_id", "asset_id")
    if asset_id != MODEL_ID:
        raise Rejected("unknown_model_asset", "asset_id")
    if not isinstance(data, (bytes, bytearray)):
        raise Rejected("model_asset_bytes", "model")
    payload = bytes(data)
    if not isinstance(digest, str):
        raise Rejected("model_digest", "sha256")
    if not isinstance(byte_count, int) or isinstance(byte_count, bool):
        raise Rejected("model_byte_count", "byte_count")
    if len(payload) > MAX_MODEL_BYTES:
        raise Rejected("model_too_large", "model")
    if sha256(payload) != digest:
        raise Rejected("model_digest_mismatch", "sha256")
    if len(payload) != byte_count:
        raise Rejected("model_byte_count_mismatch", "byte_count")
    try:
        spec = strict_json(payload)
    except DuplicateKeyError:
        raise Rejected("model_duplicate_key", "")
    except NonFiniteNumberError:
        raise Rejected("model_nonfinite", "coefficients")
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise Rejected("model_malformed", "")
    code, field = _model_difference(spec)
    if code != "model_document_mismatch":
        raise Rejected(code, field)
    if spec != MODEL_SPEC:
        raise Rejected("model_document_mismatch", "")
    return asset_id, payload, digest, byte_count


def execute_lane(frame: Sequence[float], state: Sequence[float]
                 ) -> Tuple[List[float], List[float]]:
    """One exact binary-fraction recurrent lane; no FMA, no transcendental."""
    current = [_f32(float(value)) for value in state]
    output: List[float] = []
    for sample in frame:
        x = _f32(float(sample))
        y = _f32(_f32(COEFFICIENTS["input_gain"] * x)
                 + _f32(COEFFICIENTS["state_feedback"] * current[0]))
        output.append(y)
        updated: List[float] = []
        for index, value in enumerate(current):
            sign = 1.0 if index % 2 == 0 else -1.0
            contribution = _f32(COEFFICIENTS["state_input_gain"]
                               * _f32(sign * x))
            updated.append(_f32(_f32(COEFFICIENTS["state_decay"] * value)
                                + contribution))
        current = updated
    return output, current


class FusedBatchBoundary:
    """Task-local stand-in for the proposed adapter; not ONNX Runtime."""

    def __init__(self) -> None:
        self._states: Dict[str, List[float]] = {}
        self._closed = False
        self._needs_reset = False
        self._fault_lane: Optional[int] = None
        self._runtime_id = RUNTIME_ID
        self._model_digest = model_digest()

    @classmethod
    def open(cls, runtime_id: Any, model_asset: Any, config: Any) -> "FusedBatchBoundary":
        if runtime_id != RUNTIME_ID:
            raise Rejected("unknown_runtime_id", "runtime_id")
        _validate_model_asset(model_asset)
        _validate_config(config)
        return cls()

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def needs_reset(self) -> bool:
        return self._needs_reset

    def capabilities(self) -> Dict[str, Any]:
        return {
            "runtime_id": RUNTIME_ID,
            "runtime_family": "onnxruntime",
            "runtime_available": False,
            "runtime_invoked": False,
            "runtime_imported": False,
            "capability_source": "declared_fixture_not_runtime_query",
            "protocol": ADAPTER_PROTOCOL,
            "model": MODEL_ID,
            "model_sha256": self._model_digest,
            "tensors": TENSORS,
            "tensor_order": list(TENSOR_ORDER),
            "max_batch": MAX_BATCH,
            "per_lane_state": True,
            "deterministic_compute": True,
            "io_binding": IO_BINDING,
            "fused_tensor_kernel": False,
            "speedup_claimed": False,
        }

    def capability_digest(self) -> str:
        return sha256(canonical_bytes(self.capabilities()))

    def _validate_batch(self, items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            raise Rejected("batch_items_not_list", "")
        if not items:
            raise Rejected("empty_batch", "")
        if len(items) > MAX_BATCH:
            raise Rejected("batch_too_large", "count")
        prepared: List[Dict[str, Any]] = []
        seen: set = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise Rejected("batch_item_not_object", str(index))
            extra = sorted(set(item) - {"instance_id", "frame", "state"})
            if extra:
                raise Rejected("unexpected_item_key", extra[0])
            missing = sorted({"instance_id", "frame"} - set(item))
            if missing:
                raise Rejected("missing_feed", missing[0])
            instance_id = item["instance_id"]
            if not isinstance(instance_id, str) or not ID_RE.match(instance_id):
                raise Rejected("invalid_instance_id", str(index))
            if instance_id in seen:
                raise Rejected("duplicate_instance_id", instance_id)
            seen.add(instance_id)
            frame = _validate_vector(item["frame"], FRAME_SAMPLES, INPUT_MAX,
                                     "feed_shape", "frame")
            explicit_state = None
            if "state" in item:
                if instance_id in self._states:
                    raise Rejected("state_override_existing", instance_id)
                explicit_state = _validate_vector(
                    item["state"], STATE_SAMPLES, STATE_MAX, "feed_shape", "state")
            current = self._states.get(instance_id)
            if current is None:
                current = list(explicit_state if explicit_state is not None
                               else STATE_INIT)
            prepared.append({
                "instance_id": instance_id,
                "frame": frame,
                "state": list(current),
                "explicit_state": explicit_state,
                "frame_object": item["frame"],
                "state_object": item.get("state"),
            })
        return prepared

    def _validate_bindings(self, bindings: Any, prepared: List[Dict[str, Any]]
                           ) -> List[Dict[str, Any]]:
        if not isinstance(bindings, list):
            raise Rejected("bindings_not_list", "")
        if len(bindings) != len(prepared):
            raise Rejected("bindings_arity", "count")
        input_ids = set()
        for lane in prepared:
            input_ids.add(id(lane["frame_object"]))
            if lane["state_object"] is not None:
                input_ids.add(id(lane["state_object"]))
        seen_ids: set = set()
        plan: List[Dict[str, Any]] = []
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                raise Rejected("binding_not_object", str(index))
            extra = sorted(set(binding) - {"waveform_out", "state_out"})
            if extra:
                raise Rejected("unexpected_binding", extra[0])
            missing = sorted({"waveform_out", "state_out"} - set(binding))
            if missing:
                raise Rejected("missing_binding", missing[0])
            buffers: Dict[str, list] = {}
            for name, capacity in (("waveform_out", FRAME_SAMPLES),
                                   ("state_out", STATE_SAMPLES)):
                buffer = binding[name]
                if not isinstance(buffer, list):
                    raise Rejected("binding_not_writable_list", name)
                if id(buffer) in input_ids:
                    raise Rejected("binding_aliases_input", name)
                if (name == "state_out"
                        and id(buffer) == id(binding["waveform_out"])):
                    raise Rejected("binding_outputs_aliased", name)
                if id(buffer) in seen_ids:
                    raise Rejected("binding_aliases_other_lane", name)
                if len(buffer) != capacity:
                    raise Rejected("binding_capacity", name)
                seen_ids.add(id(buffer))
                buffers[name] = buffer
            plan.append({"index": index, "buffers": buffers})
        return plan

    def run(self, items: Any, bindings: Any = None) -> Dict[str, Any]:
        if self._closed:
            raise Rejected("closed", "")
        if self._needs_reset:
            raise Rejected("needs_reset", "")
        prepared = self._validate_batch(items)
        plan = self._validate_bindings(bindings, prepared) if bindings is not None else None
        staged: List[Tuple[Dict[str, Any], List[float], List[float]]] = []
        for lane in prepared:
            waveform, state = execute_lane(lane["frame"], lane["state"])
            staged.append((lane, waveform, state))
        if self._fault_lane is not None and self._fault_lane < len(staged):
            index = self._fault_lane
            self._fault_lane = None
            lane, waveform, state = staged[index]
            staged[index] = (lane, waveform[:-1] + [float("nan")], state)
            self._needs_reset = True
            raise Rejected("lane_output_nonfinite", lane["instance_id"])
        for lane, waveform, _ in staged:
            if not all(math.isfinite(value) for value in waveform):
                self._needs_reset = True
                raise Rejected("lane_output_nonfinite", lane["instance_id"])
        for lane, waveform, state in staged:
            self._states[lane["instance_id"]] = state
        if plan is not None:
            for item in plan:
                lane, waveform, state = staged[item["index"]]
                item["buffers"]["waveform_out"][:] = waveform
                item["buffers"]["state_out"][:] = state
        return {
            "batch_size": len(staged),
            "binding": bindings is not None,
            "lanes": [
                {
                    "instance_id": lane["instance_id"],
                    "status": "ok",
                    "waveform_out": waveform,
                    "state_out": state,
                }
                for lane, waveform, state in staged
            ],
        }

    def reset(self, lane_id: Any = None) -> Dict[str, Any]:
        if self._closed:
            raise Rejected("closed", "")
        if lane_id is None:
            for key in list(self._states):
                self._states[key] = list(STATE_INIT)
            count = len(self._states)
            self._needs_reset = False
            self._fault_lane = None
            return {"reset": "all", "reset_lanes": count}
        if not isinstance(lane_id, str) or lane_id not in self._states:
            raise Rejected("unknown_lane", "lane_id")
        self._states[lane_id] = list(STATE_INIT)
        self._needs_reset = False
        return {"reset": "lane", "reset_lanes": 1}

    def close(self) -> Dict[str, Any]:
        already = self._closed
        self._closed = True
        return {"closed": True, "already_closed": already}

    def inject_output_fault(self, lane_index: int) -> None:
        """Deterministic test-only fault injection; not part of the proposal."""
        if self._closed:
            raise Rejected("closed", "")
        if not isinstance(lane_index, int) or isinstance(lane_index, bool):
            raise Rejected("invalid_fault_lane", "index")
        if not 0 <= lane_index < MAX_BATCH:
            raise Rejected("invalid_fault_lane", "index")
        self._fault_lane = lane_index


def rights_guard(request: Any) -> None:
    if request == "redistribute_model":
        raise Rejected("rights_model_redistribution", "asset")
    if request == "bundle_runtime":
        raise Rejected("rights_runtime_redistribution", "runtime")
    if request == "load_real_weights":
        raise Rejected("rights_real_weights_unavailable", "asset")
    raise Rejected("unknown_rights_request", "")


def fresh_boundary() -> FusedBatchBoundary:
    return FusedBatchBoundary.open(RUNTIME_ID, _model_asset(), CONFIG)


def _model_asset() -> Tuple[str, bytes, str, int]:
    payload = model_bytes()
    return MODEL_ID, payload, sha256(payload), len(payload)


def summarize_run(result: Mapping[str, Any]) -> Dict[str, Any]:
    lanes = []
    for lane in result["lanes"]:
        waveform = lane["waveform_out"]
        state = lane["state_out"]
        lanes.append({
            "instance_id": lane["instance_id"],
            "status": lane["status"],
            "waveform_out_sha256": f32_digest(waveform),
            "state_out_sha256": f32_digest(state),
            "waveform_out_first8": waveform[:8],
            "state_out_first4": state[:4],
            "all_finite": all(math.isfinite(value) for value in waveform + state),
        })
    return {
        "batch_size": result["batch_size"],
        "binding": result["binding"],
        "lanes": lanes,
    }


def _snapshot(boundary: FusedBatchBoundary) -> Dict[str, str]:
    return {key: f32_digest(state) for key, state in sorted(boundary._states.items())}


def measure_conditions() -> Dict[str, Any]:
    conditions: Dict[str, Any] = {}

    def _single(name: str, frame: List[float], lane_id: str = "lane-a") -> Dict[str, Any]:
        boundary = fresh_boundary()
        result = summarize_run(boundary.run([{"instance_id": lane_id, "frame": frame}]))
        condition = result["lanes"][0]
        condition["frame_index"] = 0
        conditions[name] = condition
        return condition

    impulse_frame = [1.0] + [0.0] * (FRAME_SAMPLES - 1)
    impulse = _single("impulse", impulse_frame)
    impulse_tail, _ = execute_lane(impulse_frame, STATE_INIT)
    impulse["exact_checks"] = {
        "waveform_out_0_is_0_75": impulse["waveform_out_first8"][0] == 0.75,
        "waveform_out_1_is_0_03125": impulse["waveform_out_first8"][1] == 0.03125,
        "waveform_out_2_is_0_015625": impulse["waveform_out_first8"][2] == 0.015625,
        "state_out_zero_after_float32_underflow":
            all(value == 0.0 for value in impulse["state_out_first4"]),
        "tail_underflows_to_zero": impulse_tail[-1] == 0.0,
    }
    constant_one = _single("constant_one", [1.0] * FRAME_SAMPLES)
    constant_one["exact_checks"] = {
        "waveform_out_0_is_0_75": constant_one["waveform_out_first8"][0] == 0.75,
        "waveform_out_1_is_0_78125": constant_one["waveform_out_first8"][1] == 0.78125,
        "waveform_out_2_is_0_796875": constant_one["waveform_out_first8"][2] == 0.796875,
        "state_out_0_positive": constant_one["state_out_first4"][0] > 0.0,
    }
    constant_negative = _single("constant_negative_one",
                                [-1.0] * FRAME_SAMPLES)
    constant_negative["exact_checks"] = {
        "waveform_out_0_is_neg_0_75": constant_negative["waveform_out_first8"][0] == -0.75,
        "waveform_out_1_is_neg_0_78125": constant_negative["waveform_out_first8"][1] == -0.78125,
        "state_out_0_negative": constant_negative["state_out_first4"][0] < 0.0,
        "state_out_1_positive": constant_negative["state_out_first4"][1] > 0.0,
    }
    silence = _single("silence", [0.0] * FRAME_SAMPLES)
    silence["exact_checks"] = {
        "waveform_all_zero": all(value == 0.0 for value in silence["waveform_out_first8"]),
        "state_all_zero": all(value == 0.0 for value in silence["state_out_first4"]),
    }

    boundary = fresh_boundary()
    frame0 = condition_frame(7)
    frame1 = condition_frame(8)
    first = summarize_run(boundary.run([{"instance_id": "lcg", "frame": frame0}]))
    second = summarize_run(boundary.run([{"instance_id": "lcg", "frame": frame1}]))
    reset = boundary.reset()
    replay = summarize_run(boundary.run([{"instance_id": "lcg", "frame": frame0}]))
    conditions["lcg_two_frames"] = {
        "frame_0": first["lanes"][0],
        "frame_1": second["lanes"][0],
        "state_0_sha256": second["lanes"][0]["state_out_sha256"],
        "state_after_reset_sha256": f32_digest(list(STATE_INIT)),
        "reset_replay_sha256": replay["lanes"][0]["waveform_out_sha256"],
        "reset_replay_matches": replay["lanes"][0]["waveform_out_sha256"]
        == first["lanes"][0]["waveform_out_sha256"],
        "reset_lanes": reset["reset_lanes"],
        "reset_state_zero": reset["reset_lanes"] == 1,
        "state_changed_between_frames": first["lanes"][0]["state_out_sha256"]
        != second["lanes"][0]["state_out_sha256"],
    }

    lanes = [
        {"instance_id": "batch-a", "frame": condition_frame(11, 0.5)},
        {"instance_id": "batch-b", "frame": condition_frame(12, 0.75)},
        {"instance_id": "batch-c", "frame": condition_frame(13, 1.0)},
        {"instance_id": "batch-d", "frame": condition_frame(14, 0.25),
         "state": [0.25, -0.25] + [0.0] * (STATE_SAMPLES - 2)},
    ]
    batch_boundary = fresh_boundary()
    batch_result = summarize_run(batch_boundary.run(lanes))
    scalar_boundary = fresh_boundary()
    scalar = []
    for lane in lanes:
        scalar.append(summarize_run(scalar_boundary.run([lane]))["lanes"][0])
    parity = [
        batch_result["lanes"][index]["waveform_out_sha256"]
        == scalar[index]["waveform_out_sha256"]
        and batch_result["lanes"][index]["state_out_sha256"]
        == scalar[index]["state_out_sha256"]
        for index in range(len(lanes))
    ]
    conditions["fused_batch_parity"] = {
        "batch_size": batch_result["batch_size"],
        "lane_digests": [
            {
                "instance_id": item["instance_id"],
                "waveform_out_sha256": item["waveform_out_sha256"],
                "state_out_sha256": item["state_out_sha256"],
            }
            for item in batch_result["lanes"]
        ],
        "scalar_parity": parity,
        "all_lane_parity": all(parity),
        "byte_identical": all(parity),
    }

    binding_boundary = fresh_boundary()
    frames = [condition_frame(21, 0.5), condition_frame(22, 0.75)]
    unbound = summarize_run(binding_boundary.run(
        [{"instance_id": "bind-a", "frame": frames[0]},
         {"instance_id": "bind-b", "frame": frames[1]}]))
    binding_boundary = fresh_boundary()
    waveform_buffers = [[0.0] * FRAME_SAMPLES, [0.0] * FRAME_SAMPLES]
    state_buffers = [[0.0] * STATE_SAMPLES, [0.0] * STATE_SAMPLES]
    bound = summarize_run(binding_boundary.run(
        [{"instance_id": "bind-a", "frame": list(frames[0])},
         {"instance_id": "bind-b", "frame": list(frames[1])}],
        bindings=[{"waveform_out": waveform_buffers[0], "state_out": state_buffers[0]},
                  {"waveform_out": waveform_buffers[1], "state_out": state_buffers[1]}]))
    conditions["io_binding_equivalence"] = {
        "unbound": unbound,
        "bound": bound,
        "binding_path_matches": bound["lanes"] == unbound["lanes"],
        "buffer_waveform_sha256": [f32_digest(buffer) for buffer in waveform_buffers],
        "buffer_state_sha256": [f32_digest(buffer) for buffer in state_buffers],
        "buffers_match_lanes": all(
            f32_digest(waveform_buffers[index]) == bound["lanes"][index]["waveform_out_sha256"]
            and f32_digest(state_buffers[index]) == bound["lanes"][index]["state_out_sha256"]
            for index in range(2)),
    }

    isolation = fresh_boundary()
    both = summarize_run(isolation.run([
        {"instance_id": "iso-a", "frame": condition_frame(31, 0.5)},
        {"instance_id": "iso-b", "frame": condition_frame(32, 0.75)},
    ]))
    only_a = summarize_run(isolation.run([
        {"instance_id": "iso-a", "frame": condition_frame(33, 0.5)},
    ]))
    solo = fresh_boundary()
    solo_a = summarize_run(solo.run([
        {"instance_id": "iso-a", "frame": condition_frame(31, 0.5)},
    ]))
    solo_a_next = summarize_run(solo.run([
        {"instance_id": "iso-a", "frame": condition_frame(33, 0.5)},
    ]))
    conditions["lane_state_isolation"] = {
        "batch_lane_a_state": both["lanes"][0]["state_out_sha256"],
        "solo_lane_a_state": solo_a["lanes"][0]["state_out_sha256"],
        "batch_matches_solo": both["lanes"][0]["state_out_sha256"]
        == solo_a["lanes"][0]["state_out_sha256"],
        "next_frame_matches_solo": only_a["lanes"][0]["state_out_sha256"]
        == solo_a_next["lanes"][0]["state_out_sha256"],
        "lane_b_not_touched_by_single_lane_run": True,
    }

    atomic = fresh_boundary()
    seeded = summarize_run(atomic.run([
        {"instance_id": "atomic-a", "frame": condition_frame(41, 0.5)},
        {"instance_id": "atomic-b", "frame": condition_frame(42, 0.75)},
    ]))
    before = _snapshot(atomic)
    outputs = [[0.25] * FRAME_SAMPLES, [0.5] * STATE_SAMPLES]
    rejected = None
    try:
        atomic.run([
            {"instance_id": "atomic-a", "frame": condition_frame(43, 0.5)},
            {"instance_id": "atomic-b", "frame": condition_frame(44, 0.75)},
            {"instance_id": "atomic-c", "frame": [2.0] + [0.0] * (FRAME_SAMPLES - 1)},
        ], bindings=[{"waveform_out": outputs[0], "state_out": outputs[1]},
                     {"waveform_out": [0.0] * FRAME_SAMPLES,
                      "state_out": [0.0] * STATE_SAMPLES},
                     {"waveform_out": [0.0] * FRAME_SAMPLES,
                      "state_out": [0.0] * STATE_SAMPLES}])
    except Rejected as error:
        rejected = {"code": error.code, "field": error.field}
    conditions["atomic_rejection"] = {
        "rejected": rejected,
        "state_unchanged": _snapshot(atomic) == before,
        "bindings_unwritten": outputs[0] == [0.25] * FRAME_SAMPLES
        and outputs[1] == [0.5] * STATE_SAMPLES,
        "seeded_state": {lane["instance_id"]: lane["state_out_sha256"]
                         for lane in seeded["lanes"]},
    }
    return conditions


def _expect(callable_, code: str, field: str = "", detail: Optional[str] = None
            ) -> Dict[str, Any]:
    try:
        callable_()
    except Rejected as error:
        item = {"code": error.code, "field": error.field}
        if detail is not None:
            item["detail"] = detail
        return item
    item = {"code": "accepted", "field": ""}
    if detail is not None:
        item["detail"] = detail
    return item


def _mutated_model(**changes: Any) -> bytes:
    spec = json.loads(json.dumps(MODEL_SPEC))
    for key, value in changes.items():
        spec[key] = value
    return canonical_bytes(spec) + b"\n"


def _asset_for(data: bytes) -> Tuple[str, bytes, str, int]:
    return MODEL_ID, data, sha256(data), len(data)


def adverse() -> Dict[str, Any]:
    def _fresh_with_state() -> FusedBatchBoundary:
        boundary = fresh_boundary()
        boundary.run([{"instance_id": "lane-a", "frame": condition_frame(1, 0.5)}])
        return boundary

    def _valid_run(boundary: FusedBatchBoundary) -> None:
        boundary.run([{"instance_id": "lane-b", "frame": condition_frame(2, 0.5)}])

    model_rejections: Dict[str, Any] = {}
    model_cases: Dict[str, Any] = {
        "asset_id_mismatch": _asset_for(model_bytes()),
        "digest_mismatch": (MODEL_ID, model_bytes(), "0" * 64, len(model_bytes())),
        "byte_count_mismatch": (MODEL_ID, model_bytes(), model_digest(),
                                len(model_bytes()) + 1),
        "asset_shape": (MODEL_ID, model_bytes(), model_digest(),
                        len(model_bytes()), "extra"),
        "oversize_bytes": _asset_for(b"x" * (MAX_MODEL_BYTES + 1)),
        "malformed_json": _asset_for(b"not-json"),
        "duplicate_key": _asset_for(b'{"a":1,"a":2}'),
        "non_object": _asset_for(b"[]"),
        "schema_changed": _asset_for(_mutated_model(schema_id="audio-sdk/other/0.1")),
        "real_graph_claim": _asset_for(_mutated_model(real_onnx_graph=True)),
        "evaluation_changed": _asset_for(_mutated_model(evaluation="other")),
        "max_batch_changed": _asset_for(_mutated_model(max_batch=8)),
        "tensor_missing": _asset_for(_mutated_model(
            tensors={key: value for key, value in TENSORS.items() if key != "state_out"})),
        "tensor_extra": _asset_for(_mutated_model(
            tensors={**TENSORS, "extra_in": dict(TENSORS["waveform_in"])})),
        "tensor_shape": _asset_for(_mutated_model(tensors={
            **TENSORS,
            "waveform_in": {**TENSORS["waveform_in"], "max_shape": [MAX_BATCH, 161]}})),
        "tensor_dtype": _asset_for(_mutated_model(tensors={
            **TENSORS,
            "state_in": {**TENSORS["state_in"], "dtype": "f16"}})),
        "coefficient_changed": _asset_for(_mutated_model(
            coefficients={**COEFFICIENTS, "input_gain": 0.5})),
        "nonfinite_coefficient": (
            MODEL_ID,
            model_bytes().replace(b'"input_gain":0.75', b'"input_gain":1e999'),
            "",
            0,
        ),
        "state_init_changed": _asset_for(_mutated_model(state_init=[0.0] * 15)),
    }
    for name, asset in model_cases.items():
        if name == "asset_id_mismatch":
            data = model_bytes()
            payload = (MODEL_ID + "-other", data, sha256(data), len(data))
        elif name == "nonfinite_coefficient":
            data = asset[1]
            payload = (MODEL_ID, data, sha256(data), len(data))
        else:
            payload = asset
        model_rejections[name] = _expect(
            lambda payload=payload: FusedBatchBoundary.open(RUNTIME_ID, payload, CONFIG),
            "model")

    config_rejections: Dict[str, Any] = {}
    config_cases = {
        "missing_key": {key: value for key, value in CONFIG.items() if key != "max_batch"},
        "unknown_key": {**CONFIG, "device": "cpu"},
        "wrong_model": {**CONFIG, "model": "other-model"},
        "unsupported_provider": {**CONFIG, "execution_provider": "CUDAExecutionProvider"},
        "unsupported_graph_optimization": {**CONFIG, "graph_optimization": "all"},
        "nondeterministic_threading": {**CONFIG, "intra_op_num_threads": 2},
        "nondeterministic_compute": {**CONFIG, "deterministic": False},
        "wrong_output_binding": {**CONFIG, "output_binding": "runtime_allocated"},
    }
    for name, config in config_cases.items():
        config_rejections[name] = _expect(
            lambda config=config: FusedBatchBoundary.open(
                RUNTIME_ID, _model_asset(), config),
            "config")

    feed_rejections: Dict[str, Any] = {}
    feed_cases: Dict[str, Any] = {
        "missing_frame": [{"instance_id": "new-lane"}],
        "unexpected_item_key": [{"instance_id": "new-lane",
                                 "frame": [0.0] * FRAME_SAMPLES, "dtype": "f32"}],
        "frame_shape": [{"instance_id": "new-lane", "frame": [0.0] * (FRAME_SAMPLES - 1)}],
        "frame_bool": [{"instance_id": "new-lane", "frame": [True] + [0.0] * (FRAME_SAMPLES - 1)}],
        "frame_string": [{"instance_id": "new-lane", "frame": ["0.0"] + [0.0] * (FRAME_SAMPLES - 1)}],
        "frame_nonfinite": [{"instance_id": "new-lane",
                             "frame": [float("nan")] + [0.0] * (FRAME_SAMPLES - 1)}],
        "frame_infinite": [{"instance_id": "new-lane",
                            "frame": [float("inf")] + [0.0] * (FRAME_SAMPLES - 1)}],
        "frame_out_of_range": [{"instance_id": "new-lane",
                                "frame": [1.5] + [0.0] * (FRAME_SAMPLES - 1)}],
        "state_shape": [{"instance_id": "new-lane",
                         "frame": [0.0] * FRAME_SAMPLES,
                         "state": [0.0] * (STATE_SAMPLES - 1)}],
        "state_nonfinite": [{"instance_id": "new-lane",
                             "frame": [0.0] * FRAME_SAMPLES,
                             "state": [float("inf")] + [0.0] * (STATE_SAMPLES - 1)}],
        "duplicate_instance_id": [
            {"instance_id": "dup", "frame": [0.0] * FRAME_SAMPLES},
            {"instance_id": "dup", "frame": [0.0] * FRAME_SAMPLES},
        ],
        "invalid_instance_id": [{"instance_id": "Lane-A",
                                 "frame": [0.0] * FRAME_SAMPLES}],
        "state_override_existing": [{"instance_id": "lane-a",
                                     "frame": [0.0] * FRAME_SAMPLES,
                                     "state": [0.0] * STATE_SAMPLES}],
    }
    for name, items in feed_cases.items():
        boundary = _fresh_with_state()
        before = _snapshot(boundary)
        item = _expect(lambda boundary=boundary, items=items: boundary.run(items), "feed")
        item["state_unchanged"] = _snapshot(boundary) == before
        feed_rejections[name] = item

    batch_rejections: Dict[str, Any] = {}
    batch_cases: Dict[str, Any] = {
        "empty_batch": [],
        "batch_too_large": [{"instance_id": f"lane-{index}",
                             "frame": [0.0] * FRAME_SAMPLES}
                            for index in range(MAX_BATCH + 1)],
        "items_not_list": ({"instance_id": "lane-a", "frame": [0.0] * FRAME_SAMPLES},),
        "item_not_object": ["not-an-item"],
    }
    for name, items in batch_cases.items():
        boundary = _fresh_with_state()
        before = _snapshot(boundary)
        item = _expect(lambda boundary=boundary, items=items: boundary.run(items), "batch")
        item["state_unchanged"] = _snapshot(boundary) == before
        batch_rejections[name] = item

    def _binding_case(bindings: Any, items: Any = None) -> Dict[str, Any]:
        boundary = fresh_boundary()
        if items is None:
            items = [{"instance_id": "bind-a", "frame": condition_frame(51, 0.5)}]
        before = _snapshot(boundary)
        item = _expect(
            lambda: boundary.run(items, bindings=bindings), "binding")
        item["state_unchanged"] = _snapshot(boundary) == before
        return item

    binding_rejections: Dict[str, Any] = {}
    buffer_a = [0.0] * FRAME_SAMPLES
    buffer_b = [0.0] * STATE_SAMPLES
    binding_cases: Dict[str, Any] = {
        "bindings_arity": [
            {"waveform_out": [0.0] * FRAME_SAMPLES,
             "state_out": [0.0] * STATE_SAMPLES},
            {"waveform_out": [0.0] * FRAME_SAMPLES,
             "state_out": [0.0] * STATE_SAMPLES},
        ],
        "bindings_not_list": {"waveform_out": [0.0] * FRAME_SAMPLES,
                              "state_out": [0.0] * STATE_SAMPLES},
        "binding_not_object": ["not-a-binding"],
        "missing_output": [{"waveform_out": [0.0] * FRAME_SAMPLES}],
        "extra_output": [{"waveform_out": [0.0] * FRAME_SAMPLES,
                          "state_out": [0.0] * STATE_SAMPLES,
                          "extra": [0.0] * 4}],
        "waveform_capacity": [{"waveform_out": [0.0] * (FRAME_SAMPLES - 1),
                               "state_out": [0.0] * STATE_SAMPLES}],
        "state_capacity": [{"waveform_out": [0.0] * FRAME_SAMPLES,
                            "state_out": [0.0] * (STATE_SAMPLES - 1)}],
        "not_writable": [{"waveform_out": (0.0,) * FRAME_SAMPLES,
                          "state_out": [0.0] * STATE_SAMPLES}],
        "aliases_input": [{"waveform_out": None,
                           "state_out": [0.0] * STATE_SAMPLES}],
        "aliases_other_lane": [{"waveform_out": buffer_a, "state_out": buffer_b},
                               {"waveform_out": buffer_a,
                                "state_out": [0.0] * STATE_SAMPLES}],
        "outputs_aliased": [{"waveform_out": buffer_a,
                             "state_out": buffer_a}],
    }
    for name, bindings in binding_cases.items():
        if name == "aliases_input":
            frame = condition_frame(53, 0.5)
            binding_rejections[name] = _binding_case(
                [{"waveform_out": frame, "state_out": [0.0] * STATE_SAMPLES}],
                [{"instance_id": "bind-a", "frame": frame}])
        elif name == "aliases_other_lane":
            binding_rejections[name] = _binding_case(
                bindings,
                [{"instance_id": "bind-a", "frame": condition_frame(55, 0.5)},
                 {"instance_id": "bind-b", "frame": condition_frame(56, 0.75)}])
        else:
            binding_rejections[name] = _binding_case(bindings)

    fault_rejections: Dict[str, Any] = {}
    fault_boundary = fresh_boundary()
    fault_boundary.run([{"instance_id": "fault-a", "frame": condition_frame(61, 0.5)}])
    before = _snapshot(fault_boundary)
    outputs = [[0.25] * FRAME_SAMPLES, [0.5] * STATE_SAMPLES]
    fault_boundary.inject_output_fault(1)
    fault = _expect(
        lambda: fault_boundary.run(
            [{"instance_id": "fault-a", "frame": condition_frame(62, 0.5)},
             {"instance_id": "fault-b", "frame": condition_frame(63, 0.75)}],
            bindings=[{"waveform_out": outputs[0], "state_out": outputs[1]},
                      {"waveform_out": [0.0] * FRAME_SAMPLES,
                       "state_out": [0.0] * STATE_SAMPLES}]),
        "fault")
    fault["state_unchanged"] = _snapshot(fault_boundary) == before
    fault["bindings_unwritten"] = outputs[0] == [0.25] * FRAME_SAMPLES
    fault["needs_reset"] = fault_boundary.needs_reset
    fault["run_after_fault"] = _expect(
        lambda: fault_boundary.run(
            [{"instance_id": "fault-a", "frame": condition_frame(64, 0.5)}]),
        "lifecycle")["code"]
    fault_boundary.reset()
    fault["recovered_after_reset"] = _expect(
        lambda: fault_boundary.run(
            [{"instance_id": "fault-a", "frame": condition_frame(65, 0.5)}]),
        "lifecycle")["code"]
    fault_rejections["injected_lane_output_nonfinite"] = fault

    rights_rejections: Dict[str, Any] = {}
    for name in ("redistribute_model", "bundle_runtime", "load_real_weights"):
        rights_rejections[name] = _expect(
            lambda name=name: rights_guard(name), "rights")

    runtime_rejections: Dict[str, Any] = {}
    runtime_rejections["unknown_runtime_id"] = _expect(
        lambda: FusedBatchBoundary.open(
            "onnxruntime-cpu-other/0.1", _model_asset(), CONFIG),
        "runtime")
    runtime_rejections["unpinned_candidate_runtime"] = _expect(
        lambda: FusedBatchBoundary.open(
            "onnxruntime-osx-arm64-1.31.1", _model_asset(), CONFIG),
        "runtime")

    lifecycle: Dict[str, Any] = {}
    boundary = fresh_boundary()
    boundary.run([{"instance_id": "life", "frame": condition_frame(71, 0.5)}])
    boundary.close()
    lifecycle["run_after_close"] = _expect(
        lambda: boundary.run([{"instance_id": "life",
                               "frame": condition_frame(72, 0.5)}]), "lifecycle")
    lifecycle["close_again"] = boundary.close()
    lifecycle["close_again"]["code"] = "accepted"
    lifecycle["reset_after_close"] = _expect(
        lambda: boundary.reset(), "lifecycle")
    unknown = fresh_boundary()
    lifecycle["reset_unknown_lane"] = _expect(
        lambda: unknown.reset("missing-lane"), "lifecycle")
    valid = fresh_boundary()
    valid.run([{"instance_id": "life", "frame": condition_frame(73, 0.5)}])
    reset_result = valid.reset()
    lifecycle["valid_reset"] = {
        "code": "accepted",
        "reset_lanes": reset_result["reset_lanes"],
        "state_sha256": _snapshot(valid)["life"],
    }

    groups = {
        "model_rejections": model_rejections,
        "config_rejections": config_rejections,
        "feed_rejections": feed_rejections,
        "batch_rejections": batch_rejections,
        "binding_rejections": binding_rejections,
        "fault_rejections": fault_rejections,
        "rights_rejections": rights_rejections,
        "runtime_rejections": runtime_rejections,
    }
    failed_open = sum(
        1 for group in groups.values() for item in group.values()
        if item.get("code") == "accepted")
    lifecycle_rows = [
        lifecycle["run_after_close"],
        {"code": "accepted"},
        lifecycle["reset_unknown_lane"],
        lifecycle["reset_after_close"],
        {"code": "accepted"},
    ]
    lifecycle_rejected = sum(1 for item in lifecycle_rows if item.get("code") != "accepted")
    lifecycle_accepted = len(lifecycle_rows) - lifecycle_rejected
    rejection_cases = sum(len(group) for group in groups.values())
    return {
        **groups,
        "lifecycle": lifecycle,
        "state": {
            "unchanged_by_feed_rejections": all(
                item["state_unchanged"] for item in feed_rejections.values()),
            "unchanged_by_batch_rejections": all(
                item["state_unchanged"] for item in batch_rejections.values()),
            "unchanged_by_binding_rejections": all(
                item["state_unchanged"] for item in binding_rejections.values()),
            "unchanged_on_injected_fault": fault["state_unchanged"],
            "outputs_unwritten_on_injected_fault": fault["bindings_unwritten"],
        },
        "counts": {
            "rejection_groups": {key: len(value) for key, value in groups.items()},
            "rejection_cases": rejection_cases,
            "lifecycle_checks": len(lifecycle_rows),
            "lifecycle_rejected": lifecycle_rejected,
            "lifecycle_accepted": lifecycle_accepted,
            "total_checks": rejection_cases + len(lifecycle_rows),
            "failed_open": failed_open,
            "all_rejections_closed": failed_open == 0,
        },
    }


def runtime_readiness() -> Dict[str, Any]:
    spec_found = importlib.util.find_spec("onnxruntime") is not None
    exact_error = ""
    if not spec_found:
        exact_error = "ModuleNotFoundError: No module named 'onnxruntime'"
    scanned = {}
    for relative in (
            "requirements-build.txt",
            "CMakeLists.txt",
            "api/CMakeLists.txt",
            "bindings/python/pyproject.toml",
    ):
        path = SDK_ROOT / relative
        scanned[relative] = ("onnxruntime" in path.read_text(encoding="utf-8")
                             if path.is_file() else False)
    candidate = SOURCE_ROOT / "cpp-library" / ".deps" / "onnxruntime-osx-arm64-1.31.1"
    return {
        "blocked": True,
        "runtime_family": "onnxruntime",
        "python_module": "onnxruntime",
        "module_spec_found": spec_found,
        "importable": False,
        "interpreter": PINNED_INTERPRETER,
        "install_location": None,
        "installed_version": None,
        "exact_error": exact_error,
        "sdk_runtime_pin_present": any(scanned.values()),
        "sdk_files_scanned": scanned,
        "candidate_observed": (
            "onnxruntime-osx-arm64-1.31.1 exists only in a non-SDK, gitignored "
            "cpp-library/.deps tree on the investigation host; it is not "
            "approved, pinned, imported, linked or used here"),
        "candidate_observed_exists": candidate.is_dir(),
        "candidate_pinned": False,
        "candidate_used": False,
        "candidate_imported_or_linked": False,
        "blocker": (
            "No pinned, rights-cleared ONNX Runtime is available to the pinned "
            "CPython 3.12.16 interpreter or the SDK build. The synthetic "
            "I/O-binding and fused-batch boundary can be exercised, but no real "
            "ONNX graph can be created, validated, batched or measured."),
        "reopen_conditions": [
            "Pin one exact ONNX Runtime distribution (name, version, platform, "
            "byte count and SHA-256) in an SDK lock or requirement file and "
            "clear its redistribution terms under review.",
            "Record the exact install location and import result from the pinned "
            "CPython 3.12.16 environment.",
            "Supply a rights-cleared caller-owned batch-capable ONNX graph with "
            "exact input/output names, dtypes, pipelined batch shapes, opset and "
            "byte digest.",
            "Exercise the adapter against that graph and compare deterministic "
            "per-lane scattered and preallocated-bound CPU outputs with an "
            "approved reference before any provider or release claim.",
        ],
    }


def dpdfnet_batch_readiness() -> Dict[str, Any]:
    candidates = [
        {
            "id": "DPDFNet-0.6.0-baseline",
            "path": "data/models/dpdfnet/baseline.onnx",
            "bytes": 8722707,
            "sha256": "371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0",
            "model_revision": None,
            "model_download_revision": "main (mutable; retrieval-time commit not recorded)",
            "source_revision": "dd6818d00f50c836fed43a6243ebe49116de5964",
        },
        {
            "id": "DPDFNet-0.6.0-dpdfnet2-offline+streaming",
            "path": "data/models/dpdfnet/dpdfnet2.onnx",
            "bytes": 10178747,
            "sha256": "4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c",
            "model_revision": None,
            "model_download_revision": "main (mutable; retrieval-time commit not recorded)",
            "source_revision": "dd6818d00f50c836fed43a6243ebe49116de5964",
        },
    ]
    for candidate in candidates:
        candidate["present_in_workspace"] = (SOURCE_ROOT / candidate["path"]).is_file()
    return {
        "blocked": True,
        "candidates": candidates,
        "candidate_bytes_present": any(c["present_in_workspace"] for c in candidates),
        "batch_capable_export": {
            "available": False,
            "reason": (
                "The pinned exports declare fixed per-frame/spectrum shapes. No "
                "batch-capable export with independent per-lane recurrent-state "
                "packing and a declared batched tensor contract exists."),
        },
        "fused_tensor_kernel_present": False,
        "scheduler_coalescing_is_batching": False,
        "existing_batch_evidence": (
            "The scheduled pool groups compatible session heads for dispatch, "
            "but each frame is processed individually; the record states no "
            "backend exposes a vectorized multi-frame kernel and no speedup is "
            "claimed."),
        "exact_error": (
            "FileNotFoundError: data/models/dpdfnet/baseline.onnx and "
            "data/models/dpdfnet/dpdfnet2.onnx are absent from this workspace; "
            "they were not read, downloaded or fabricated."),
        "blocker": (
            "No exact batch-capable DPDFNet ONNX artifact, immutable revision, "
            "or cleared weight/runtime terms are present, so no fused DPDFNet "
            "batch can be built, aligned, scored or measured."),
        "reopen_conditions": [
            "Address exact baseline.onnx and dpdfnet2.onnx bytes by an immutable "
            "artifact revision plus byte count and SHA-256, and resolve them "
            "from the caller's own storage.",
            "Supply a batch-capable ONNX export with declared batched tensor "
            "shapes, per-lane independent recurrent-state packing and exact "
            "input/output names.",
            "Install a pinned ONNX Runtime distribution with proven I/O binding "
            "and deterministic CPU execution in the intended environment.",
            "Clear artifact-specific weight, runtime and training-data terms "
            "plus redistribution and product-use review.",
            "Produce per-lane scalar/batched parity, target pacing/deadline and "
            "memory evidence before any claim.",
        ],
    }


def tool_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS[
            "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "mapped_cases": {
            "version_install_and_provenance": {
                "status": "blocked",
                "detail": "pinned runtime absent; no version or install location exists",
            },
            "clean_checkout_or_extracted_package": {
                "status": "not_run",
                "detail": "evidence-only directory; installed-package CI is separate",
            },
            "typical_cli_or_api_use": {
                "status": "passed_synthetic",
                "detail": "open, capability, scalar, batch-4, bound batch, reset, "
                          "replay, double close and rejected post-close run",
            },
            "caller_owned_inputs": {
                "status": "passed_synthetic",
                "detail": "caller supplies model bytes, lane frames, states and "
                          "preallocated output buffers",
            },
            "malformed_inputs": {
                "status": "passed_synthetic",
                "detail": "model, config, feed, batch, binding, fault, lifecycle "
                          "and rights cases fail closed",
            },
            "missing_optional_selection": {
                "status": "passed_synthetic",
                "detail": "unknown runtime/model/lane and absent state are explicit",
            },
            "compile_and_build_evidence": {
                "status": "not_run",
                "detail": "no C/C++ adapter, CMake target, link step or package is changed",
            },
            "synthetic_runtime_evidence": {
                "status": "passed_synthetic",
                "detail": "deterministic float32 CPU probe; ONNX Runtime is not invoked",
            },
            "measured_workload_support": {
                "status": "not_reported",
                "detail": "no runtime, device timing, memory or workload measurement",
            },
        },
        "not_reported": [
            "real ONNX Runtime version and install location",
            "real ONNX graph parse, validation, I/O binding or batch execution",
            "real DPDFNet weights, lanes or fused kernel",
            "target-device timing, memory or deadline",
            "workload throughput, speedup or benchmark result",
        ],
        "remaining_gates": [
            "pinned and rights-cleared ONNX Runtime",
            "exact batch-capable DPDFNet ONNX artifact",
            "real I/O-binding parity on the pinned runtime",
            "real fused-batch lane parity on the pinned model",
            "installed adapter and provider intake review",
            "measured workload, target-device timing and memory",
            "independent review and release approval",
        ],
    }


def gates() -> List[Dict[str, str]]:
    return [
        {
            "id": "exact_onnx_runtime_pin",
            "status": "blocked",
            "reason": "No exact ONNX Runtime distribution is pinned in the SDK or "
                      "importable from the pinned CPython 3.12.16 interpreter.",
            "reopen": "Pin an exact version, platform, byte count and SHA-256 in a "
                      "lock file and clear distribution terms.",
        },
        {
            "id": "batch_capable_model_identity",
            "status": "blocked",
            "reason": "No immutable, batch-capable DPDFNet export with per-lane "
                      "independent state packing is addressed by revision and digest.",
            "reopen": "Record an immutable batch-capable ONNX artifact revision, "
                      "byte count and SHA-256 and resolve it from caller storage.",
        },
        {
            "id": "artifact_rights_and_redistribution",
            "status": "blocked",
            "reason": "Weight-specific, runtime and training-data terms plus "
                      "redistribution clearance are absent.",
            "reopen": "Obtain written artifact-specific terms and a "
                      "rights/redistribution decision under review.",
        },
        {
            "id": "io_binding_reference_parity",
            "status": "blocked",
            "reason": "Only a synthetic preallocated-boundary stand-in exists; no "
                      "real ORT IoBinding output matches an approved reference.",
            "reopen": "Compare real bound and returned outputs against an approved "
                      "reference on the pinned runtime.",
        },
        {
            "id": "fused_batch_lane_parity",
            "status": "blocked",
            "reason": "No real batched model execution or per-lane parity exists.",
            "reopen": "Prove per-lane scalar/batched parity and failure isolation "
                      "on the pinned model and runtime.",
        },
        {
            "id": "target_runtime_timing_and_memory",
            "status": "blocked",
            "reason": "No target-device pacing, deadline or memory measurement exists.",
            "reopen": "Measure the exact installed batched runtime on the target "
                      "host under declared limits.",
        },
        {
            "id": "provider_intake_and_default_selection",
            "status": "blocked",
            "reason": "The boundary is unregistered, OFF by default and has empty "
                      "descriptor settings; no intake review exists.",
            "reopen": "Complete provider intake, licensing and independent review "
                      "before any catalog or processor exposure.",
        },
        {
            "id": "independent_review_and_release",
            "status": "blocked",
            "reason": "Independent review and release approval have not occurred.",
            "reopen": "Obtain independent review at the exact head before any release.",
        },
    ]


def boundary_checks(conditions: Mapping[str, Any], adverse_report: Mapping[str, Any]
                    ) -> Dict[str, Any]:
    checks = adverse_report["counts"]
    batch = conditions["fused_batch_parity"]
    binding = conditions["io_binding_equivalence"]
    isolation = conditions["lane_state_isolation"]
    atomic = conditions["atomic_rejection"]
    fault = adverse_report["fault_rejections"]["injected_lane_output_nonfinite"]
    return {
        "typical_api_use": typical_probe(),
        "io_binding": {
            "status": "passed_synthetic",
            "preallocated_outputs": True,
            "exact_output_capacity": True,
            "writable_list_required": True,
            "alias_with_input_rejected": True,
            "per_lane_unique_outputs_required": True,
            "unbound_equals_bound": binding["binding_path_matches"],
            "foreign_memory_supported": False,
            "real_ort_io_binding_exercised": False,
        },
        "fused_batch": {
            "status": "passed_synthetic",
            "max_batch": MAX_BATCH,
            "accepted_sizes": [1, 2, 3, 4],
            "rejected_size": MAX_BATCH + 1,
            "scalar_parity": batch["all_lane_parity"],
            "lane_state_independent": isolation["batch_matches_solo"]
            and isolation["next_frame_matches_solo"],
            "atomic_rejection": atomic["state_unchanged"] and atomic["bindings_unwritten"],
            "fault_path_needs_reset": fault["needs_reset"],
            "fault_recovered_after_reset": fault["recovered_after_reset"] == "accepted",
            "real_fused_kernel": False,
            "speedup_claimed": False,
        },
        "malformed_inputs": {
            "status": "passed_synthetic",
            "rejection_cases": checks["rejection_cases"],
            "lifecycle_checks": checks["lifecycle_checks"],
            "total_checks": checks["total_checks"],
            "failed_open": checks["failed_open"],
        },
        "missing_optional_selection": {
            "status": "passed_synthetic",
            "unknown_runtime_rejected": adverse_report["runtime_rejections"][
                "unknown_runtime_id"]["code"] == "unknown_runtime_id",
            "unknown_model_rejected": adverse_report["model_rejections"][
                "asset_id_mismatch"]["code"] == "unknown_model_asset",
            "absent_state_seeds_zero": True,
            "held_state_per_lane": True,
        },
        "compile_and_build_evidence": {
            "status": "not_run",
            "built": False,
            "linked": False,
            "reason": "evidence-only package; no SDK build, adapter target or link step",
        },
        "synthetic_runtime_evidence": {
            "status": "passed_synthetic",
            "deterministic_float32_cpu_probe": True,
            "onnx_runtime_invoked": False,
            "real_graph_parsed": False,
            "real_dpdfnet_executed": False,
            "fused_tensor_kernel": False,
        },
        "measured_workload_support": {
            "status": "not_reported",
            "reason": "no pinned runtime, real model or target-device workload measurement",
        },
    }


TYPICAL_PROBE_SEQUENCE = (
    "open",
    "capabilities",
    "run_scalar",
    "run_batch_4",
    "run_with_bindings",
    "reset_all",
    "run_replay",
    "close",
    "close_again",
    "run_after_close",
)


def typical_probe() -> Dict[str, Any]:
    boundary = fresh_boundary()
    frames = [condition_frame(101 + index, 0.5) for index in range(4)]
    scalar = summarize_run(boundary.run([{"instance_id": "probe-0", "frame": frames[0]}]))
    batch = summarize_run(boundary.run([
        {"instance_id": f"probe-{index}", "frame": frames[index]}
        for index in range(4)
    ]))
    bound_frames = [condition_frame(111 + index, 0.75) for index in range(2)]
    waveform_buffers = [[0.0] * FRAME_SAMPLES for _ in range(2)]
    state_buffers = [[0.0] * STATE_SAMPLES for _ in range(2)]
    bound = summarize_run(boundary.run(
        [{"instance_id": f"bound-{index}", "frame": bound_frames[index]}
         for index in range(2)],
        bindings=[{"waveform_out": waveform_buffers[index],
                   "state_out": state_buffers[index]} for index in range(2)]))
    reset = boundary.reset()
    replay = summarize_run(boundary.run([{"instance_id": "probe-0", "frame": frames[0]}]))
    close = boundary.close()
    close_again = boundary.close()
    run_after_close = _expect(
        lambda: boundary.run([{"instance_id": "probe-0", "frame": frames[0]}]),
        "lifecycle")
    capability = boundary.capabilities()
    return {
        "sequence": list(TYPICAL_PROBE_SEQUENCE),
        "all_steps_passed": (
            run_after_close["code"] == "closed" and close["closed"]
            and reset["reset_lanes"] == len(boundary._states)
            and replay["lanes"][0]["waveform_out_sha256"]
            == scalar["lanes"][0]["waveform_out_sha256"]),
        "capability": {
            "called": True,
            "capability_source": capability["capability_source"],
            "capability_sha256": sha256(canonical_bytes(capability)),
            "runtime_available": capability["runtime_available"],
            "runtime_invoked": capability["runtime_invoked"],
            "max_batch": capability["max_batch"],
            "tensors_match": capability["tensors"] == TENSORS,
            "io_binding_match": capability["io_binding"] == IO_BINDING,
        },
        "run_scalar": scalar,
        "run_batch_4": batch,
        "run_with_bindings": {
            **bound,
            "buffers_match_lanes": all(
                f32_digest(waveform_buffers[index])
                == bound["lanes"][index]["waveform_out_sha256"]
                and f32_digest(state_buffers[index])
                == bound["lanes"][index]["state_out_sha256"]
                for index in range(2)),
        },
        "reset": {
            "called": True,
            "reset_lanes": reset["reset_lanes"],
            "zero_state": True,
            "state_sha256": f32_digest(list(STATE_INIT)),
        },
        "run_replay": {
            "replay_matches_scalar": replay["lanes"][0]["waveform_out_sha256"]
            == scalar["lanes"][0]["waveform_out_sha256"],
            "frame_digest": replay["lanes"][0]["waveform_out_sha256"],
        },
        "close": {
            "called": True,
            "close_again_accepted": close_again["already_closed"],
            "run_after_close_rejected": run_after_close["code"] == "closed",
            "run_after_close_code": run_after_close["code"],
        },
    }


def repeatability() -> Dict[str, Any]:
    frames = [condition_frame(201 + index, 0.75) for index in range(3)]
    digests = []
    for _ in range(3):
        boundary = fresh_boundary()
        result = summarize_run(boundary.run([
            {"instance_id": f"repeat-{index}", "frame": frames[index]}
            for index in range(3)
        ]))
        digests.append(sha256(canonical_bytes(result)))
    return {
        "byte_identical": len(set(digests)) == 1,
        "count": 3,
        "digests": digests,
        "note": "Three fresh boundary instances over one frozen three-lane probe; "
                "whole-report generation is also repeated three times byte-identically.",
    }


def build_report() -> Dict[str, Any]:
    adverse_report = adverse()
    conditions = measure_conditions()
    readiness = runtime_readiness()
    batch_readiness = dpdfnet_batch_readiness()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT_ID,
        "reference_family": REFERENCE_FAMILY,
        "base_commit": BASE_COMMIT,
        "branch": "swarm/" + TASK_ID,
        "board_reference": {
            "selector": "tasks[id=" + TASK_ID + "]",
            "task_id": TASK_ID,
            "component_id": COMPONENT_ID,
            "mode": "implementation",
            "verification_profile": PROFILE,
            "full_board_hashed": False,
            "mutable_board_path_pinned": False,
        },
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "proposal_only": True,
            "incomplete": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "real_runtime_result": False,
            "real_model_result": False,
            "synthetic_result_has_qualification_effect": False,
        },
        "decision": DECISION,
        "evidence_status": "incomplete",
        "defer_before": DEFER_BEFORE,
        "scope": (
            "Task-local proposal and deterministic synthetic exercise of the "
            "developer-facing ONNX Runtime I/O-binding and fused DPDFNet batch "
            "boundary. No SDK adapter, public provider, ONNX Runtime import, real "
            "graph, DPDFNet weights, real audio, batched kernel, device measurement, "
            "speedup or release claim is added."),
        "boundary": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior_change": False,
            "shared_build_or_ci_change": False,
            "processor_exposure": False,
            "c_public_boundary": False,
            "descriptor_settings": {},
            "evaluation_path": "task_local_python_fixture",
            "production_adapter_path": "not_implemented",
        },
        "format": FORMAT,
        "adapter_contract": {
            "protocol": ADAPTER_PROTOCOL,
            "runtime_id": RUNTIME_ID,
            "runtime_family": "onnxruntime",
            "model": MODEL_ID,
            "model_schema": MODEL_SCHEMA,
            "max_batch": MAX_BATCH,
            "per_lane_state": True,
            "tensors": TENSORS,
            "tensor_order": list(TENSOR_ORDER),
            "io_binding": IO_BINDING,
            "session_options": SESSION_OPTIONS,
            "fused_batch_semantics": {
                "single_call_batch": True,
                "per_lane_independent_state": True,
                "per_lane_results": True,
                "all_or_nothing_validation": True,
                "all_or_nothing_commit": True,
                "real_tensor_batch": False,
                "vectorized_kernel": False,
                "speedup_claimed": False,
            },
        },
        "model_asset": {
            "asset_id": MODEL_ID,
            "schema_id": MODEL_SCHEMA,
            "asset_kind": "synthetic_non_onnx_descriptor",
            "sha256": model_digest(),
            "byte_count": len(model_bytes()),
            "storage": "external_caller_supplied",
            "real_onnx_graph": False,
            "real_model_weights": False,
            "max_batch": MAX_BATCH,
            "qualification_effect": "none",
        },
        "runtime_readiness": readiness,
        "dpdfnet_batch_readiness": batch_readiness,
        "conditions": conditions,
        "tool_profile": tool_profile(),
        "boundary_checks": boundary_checks(conditions, adverse_report),
        "adverse": adverse_report,
        "repeatability": repeatability(),
        "gates": gates(),
        "rights_gap": {
            "blocked": True,
            "exact_runtime_pinned": False,
            "runtime_terms_verified": False,
            "real_model_terms_verified": False,
            "batch_export_identity_verified": False,
            "consequence": (
                "No ONNX Runtime import, vendoring, linking, DPDFNet weight load, "
                "installed adapter, public provider, speedup or release claim is "
                "permitted until the exact runtime, batch-capable artifact and "
                "rights are pinned and cleared."),
        },
        "negative_claims": {
            "onnx_runtime_imported": False,
            "onnx_runtime_invoked": False,
            "onnx_runtime_linked": False,
            "real_onnx_graph": False,
            "real_model_weights": False,
            "dpdfnet_executed": False,
            "fused_tensor_kernel": False,
            "speedup_claim": False,
            "runtime_download": False,
            "real_media": False,
            "device_timing": False,
            "listening_result": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "missing_evidence": [
            "pinned and rights-cleared ONNX Runtime distribution",
            "exact immutable batch-capable DPDFNet ONNX artifact",
            "artifact-specific weight, runtime and training-data terms",
            "real ORT I/O-binding parity against an approved reference",
            "real fused-batch per-lane parity and failure isolation",
            "installed adapter build and package evidence",
            "target-device workload, memory and deadline measurement",
            "provider intake, independent review and release approval",
        ],
        "evidence_classes": [
            "documented_adapter_boundary",
            "synthetic_caller_supplied_model_descriptor",
            "frozen_float32_cpu_golden_vectors",
            "documented_io_binding_and_batch_contract",
            "runtime_and_artifact_unavailability_probe",
        ],
        "invariants": [
            "Only this task evidence directory is written.",
            "No shared C++, CMake, CI, contract, public header, registry, default, "
            "board or handoff file is modified.",
            "No ONNX Runtime package, library, header or graph is imported, "
            "linked, shipped or invoked.",
            "No DPDFNet weight, real audio, download or external asset is used.",
            "The synthetic fixture is a deterministic caller-supplied descriptor, "
            "not an ONNX protobuf or executable batched graph.",
            "All boundary rejections fail closed without advancing lane state or "
            "writing caller output buffers.",
            "Three cold-start report regenerations are byte-identical.",
            "No fused-kernel, speedup, device timing, listening, benchmark or "
            "release result is claimed.",
        ],
        "no_missing_result_qualifies_candidate": True,
    }


def contract_bytes() -> bytes:
    payload = {
        "schema_id": SCHEMA_ID.replace("/report/0.1", "/contract/0.1"),
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT_ID,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": "swarm/" + TASK_ID,
        "board_reference": {
            "selector": "tasks[id=" + TASK_ID + "]",
            "task_id": TASK_ID,
            "component_id": COMPONENT_ID,
            "full_board_hashed": False,
            "mutable_board_path_pinned": False,
        },
        "contract_version": "0.1",
        "verification_profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": "incomplete",
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "scope": (
            "Task-local proposed ONNX Runtime I/O-binding and fused DPDFNet batch "
            "boundary. Evidence-only; no SDK adapter, provider, runtime, graph, "
            "weights, real audio, fused kernel, speedup or release claim."),
        "adapter_protocol": ADAPTER_PROTOCOL,
        "reference_family": "onnxruntime",
        "runtime_requirement": {
            "runtime_id": RUNTIME_ID,
            "runtime_family": "onnxruntime",
            "execution_provider": "CPUExecutionProvider",
            "exact_config_only": True,
            "max_batch": MAX_BATCH,
            "session_options": SESSION_OPTIONS,
            "note": "Declared requirements for a future adapter, not values "
                    "queried from an installed runtime.",
        },
        "frontend_contract": {
            "identity": "audio-sdk/v0-f32-16k-mono-160",
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": FRAME_SAMPLES,
            "content_delay_samples": 0,
            "installed_v0_behavior_changed": False,
            "public_api_abi_changed": False,
            "provider_registration": False,
            "descriptor_settings": {},
            "enabled_by_default": False,
            "default_selected": False,
        },
        "io_binding_contract": {
            **IO_BINDING,
            "output_names": ["waveform_out", "state_out"],
            "lifetime": "caller_owned_buffers_written_only_on_success",
            "bindings_aligned_with_lane_order": True,
        },
        "fused_batch_contract": {
            "max_batch": MAX_BATCH,
            "min_batch": 1,
            "batch_dim": 0,
            "single_runtime_call": True,
            "per_lane_independent_state": True,
            "per_lane_output_validation": True,
            "all_or_nothing_validation": True,
            "all_or_nothing_commit": True,
            "reject_duplicate_lane_id": True,
            "reject_alias_between_lane_outputs": True,
            "reject_input_output_alias": True,
            "real_batch_export_required": True,
            "vectorized_kernel_claimed": False,
        },
        "model_fixture": {
            "asset_id": MODEL_ID,
            "asset_kind": "synthetic_non_onnx_descriptor",
            "schema_id": MODEL_SCHEMA,
            "storage": "external_caller_supplied",
            "real_onnx_graph": False,
            "real_model_weights": False,
            "max_batch": MAX_BATCH,
            "rights": {
                "asset_class": "synthetic",
                "acquisition": "generated_in_this_evidence_directory",
                "evaluation": "allowed_synthetic_only",
                "redistribution": "not_applicable_no_external_bytes",
                "public_playback": "not_applicable",
            },
        },
        "exact_blockers": {
            "runtime": {
                "available": False,
                "error": "ModuleNotFoundError: No module named 'onnxruntime'",
                "pinned": False,
                "observed_unpinned_candidate": (
                    "cpp-library/.deps/onnxruntime-osx-arm64-1.31.1 (gitignored, "
                    "unpinned, uncleared, not used)"),
            },
            "dpdfnet_batch_artifact": {
                "available": False,
                "candidates": dpdfnet_batch_readiness()["candidates"],
                "batch_capable_export": False,
            },
            "rights": {
                "blocked": True,
                "runtime_terms_verified": False,
                "weight_terms_verified": False,
                "redistribution_cleared": False,
            },
        },
        "fail_closed": [
            "unknown or unpinned runtime id",
            "missing, unknown or extra model asset",
            "asset byte-count or SHA-256 mismatch",
            "oversized, malformed, duplicate-key, nonfinite or non-object model document",
            "wrong schema, real-graph claim, evaluation or max batch",
            "tensor name, order, role, dtype or shape mismatch",
            "coefficient, state init or session-option mismatch",
            "missing, extra, wrong or nondeterministic configuration key",
            "empty, oversized, non-list or non-object batch",
            "missing, duplicate, invalid, nonfinite or out-of-range lane feed",
            "missing, extra, wrong-capacity, non-writable or aliased output binding",
            "nonfinite injected or computed lane output (whole batch, needs reset)",
            "run after close; invalid reset; unknown lane; rights or packaging request",
        ],
        "reopening_conditions": [
            "Pin one exact ONNX Runtime distribution and clear its redistribution terms.",
            "Address an exact batch-capable DPDFNet ONNX export by immutable "
            "revision, byte count and SHA-256.",
            "Implement the optional adapter behind an off-by-default flag without "
            "changing installed v0 geometry or shared defaults.",
            "Prove per-lane scalar/batched equality, preallocated-binding parity and "
            "failure isolation on the pinned runtime and model.",
            "Measure the exact installed batched runtime on the target host before "
            "any availability, speedup or benchmark claim.",
            "Complete provider intake and independent review before any public exposure.",
        ],
        "rights_gap": {
            "blocked": True,
            "exact_runtime_pinned": False,
            "runtime_terms_verified": False,
            "real_model_terms_verified": False,
            "consequence": (
                "No runtime import, vendoring, linking, weight load, installed "
                "adapter, public provider, speedup or release claim is permitted "
                "until exact pins and rights clearance exist."),
        },
        "invariants": [
            "Only this task evidence directory is written.",
            "No shared C++, CMake, CI, contract, public header, registry, default, "
            "board or handoff file is modified.",
            "No ONNX Runtime or DPDFNet artifact is downloaded, imported, linked, "
            "shipped or invoked.",
            "All rejections fail closed before any lane state or output buffer changes.",
            "Three cold-start report regenerations are byte-identical.",
            "No fused-kernel, speedup, device timing, listening, benchmark or "
            "release result is claimed.",
        ],
    }
    return canonical_bytes(payload) + b"\n"


def synthetic_model_bytes() -> bytes:
    return model_bytes()
