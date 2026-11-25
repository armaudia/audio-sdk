# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local ONNX Runtime adapter boundary evidence.

This module documents and exercises the developer-facing boundary that a future
optional ONNX Runtime adapter must satisfy. It does **not** import, link, ship or
invoke ONNX Runtime, and it does **not** decode a real ONNX graph or load model
weights. The caller-supplied asset is a canonical synthetic descriptor and the
execution is a frozen float32 CPU reference probe with exact tensor shapes.

The evidence disposition is DEFER / incomplete / not_qualified. Missing results
never qualify a candidate.
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
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

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

TASK_ID = "SDK-ONNX-RUNTIME-REFERENCE-RUNTIME"
TITLE = "ONNX Runtime reference runtime"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
SCHEMA_ID = "audio-sdk/task-evidence/onnx-runtime-reference-runtime/report/0.1"
COMPONENT_ID = "onnx-runtime-reference-runtime"
REFERENCE_FAMILY = "onnxruntime"
PROFILE = "tool"
STATUS = "synthetic_boundary_incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "runtime_integration"
TASK_REL = "docs/task-evidence/onnx-runtime-reference-runtime"
ADAPTER_PROTOCOL = "audio-sdk/onnx-runtime-adapter/0.1"
RUNTIME_ID = "onnxruntime-cpu-reference-synthetic/0.1"
MODEL_ID = "synthetic-ort-adapter-probe"
MODEL_VERSION = 1
MODEL_SCHEMA = "audio-sdk/onnx-runtime-reference-runtime/synthetic-model/0.1"

# Public v0 geometry is documented only; nothing is installed or changed.
FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "offline_synthetic_frame_fixture",
    "installed_v0_geometry_preserved": True,
}
TENSORS = {
    "waveform_in": {"dtype": "f32", "shape": [1, 160], "role": "input"},
    "state_in": {"dtype": "f32", "shape": [1, 16], "role": "input"},
    "waveform_out": {"dtype": "f32", "shape": [1, 160], "role": "output"},
    "state_out": {"dtype": "f32", "shape": [1, 16], "role": "output"},
}
TENSOR_ORDER = ("waveform_in", "state_in", "waveform_out", "state_out")
INPUT_MAX = 1.0
STATE_MAX = 4.0
MAX_MODEL_BYTES = 65536
FRAME_COUNT = 3

SESSION_OPTIONS = {
    "execution_provider": "CPUExecutionProvider",
    "execution_mode": "sequential",
    "graph_optimization": "disabled",
    "intra_op_num_threads": 1,
    "inter_op_num_threads": 1,
    "enable_mem_pattern": False,
    "deterministic_compute": True,
}
CONFIG = {
    "model": MODEL_ID,
    "execution_provider": "cpu_reference",
    "graph_optimization": "disabled",
    "intra_op_num_threads": 1,
    "inter_op_num_threads": 1,
    "deterministic": True,
}

SOURCE_PINS: Dict[str, str] = {
    "source:cpp-library/src/stages/onnx_common.cpp":
        "f8eaee5455fefb1dd0dcaac10092a25f673f138f76af07d21dfed69fa95712c8",
    "source:cpp-library/src/stages/onnx_common.hpp":
        "fead88c586ea8a095ebb15be4d3c5ba2515b6497e3f8f7f08c7b2cce4420d4e1",
    "source:cpp-library/CMakeLists.txt":
        "ac655c9c8d1d9c90991493d925c988d1f0b887e9364a8cf21853a6860fc219bc",
    "source:cpp-library/cmake/audio_enhance_models.json":
        "6b14470521a1ba599f572e236eb96c877dfe5777341eb402b9224c3eb5feedbe",
    "source:adapters/README.md":
        "24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
}
ARTIFACT_PIN_PATHS = (
    f"{TASK_REL}/contract.json",
    f"{TASK_REL}/adapter.json",
    f"{TASK_REL}/provider.json",
    f"{TASK_REL}/synthetic_model.json",
)
PIN_RE = re.compile(
    r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|worktree:[^\s]+|CONTRACTS\.md|"
    r"api/[^\s]+|bindings/[^\s]+|docs/[^\s]+)$")
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"

# The caller-supplied fixture is a synthetic descriptor, not an ONNX binary.
MODEL_SPEC: Dict[str, Any] = {
    "schema_id": MODEL_SCHEMA,
    "model_id": MODEL_ID,
    "model_version": MODEL_VERSION,
    "runtime_family": "onnxruntime",
    "not_a_real_onnx_graph": True,
    "evaluation": "linear_state_probe_v1",
    "coefficients": {
        "waveform_input": 0.75,
        "waveform_state": 0.25,
        "state_scale": 0.125,
        "state_input_signs": [1, -1, 1, -1, 1, -1, 1, -1, 1, -1],
    },
    "state_init": [0.0] * 16,
    "tensors": [
        {"name": name, "role": TENSORS[name]["role"],
         "dtype": TENSORS[name]["dtype"], "shape": TENSORS[name]["shape"]}
        for name in TENSOR_ORDER
    ],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def model_bytes() -> bytes:
    return canonical_bytes(MODEL_SPEC) + b"\n"


def model_digest() -> str:
    return sha256(model_bytes())


def strict_json(data: bytes) -> Any:
    def reject_object_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def reject_constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("malformed_json:utf8") from error
    try:
        return json.loads(text, object_pairs_hook=reject_object_pairs,
                          parse_constant=reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("malformed_json:" + error.msg) from error


def strict_json_file(path: Path) -> Any:
    return strict_json(path.read_bytes())


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return SOURCE_ROOT / raw.split(":", 1)[1]
    if raw.startswith("worktree:"):
        return SDK_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Fail closed on malformed, duplicated or out-of-scope manifest entries."""
    pins: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + repr(line))
        raw_path = match.group("path")
        if ".." in Path(raw_path.split(":", 1)[-1]).parts:
            raise ValueError("path_traversal_pin:" + raw_path)
        if raw_path in seen:
            raise ValueError("duplicate_pin:" + raw_path)
        seen.add(raw_path)
        pins.append((line[:64], raw_path))
    return pins


def artifact_pins() -> Dict[str, str]:
    return {path: sha256(pin_path(path).read_bytes()) for path in ARTIFACT_PIN_PATHS}


def sources_bytes() -> bytes:
    """Deterministic manifest; excludes SOURCES.sha256 itself to avoid self-reference."""
    pins: Dict[str, str] = dict(SOURCE_PINS)
    pins.update(BOUNDARY_PINS)
    pins.update(artifact_pins())
    for path in sorted(HERE.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SOURCES.sha256":
            pins[f"{TASK_REL}/{path.name}"] = sha256(path.read_bytes())
    lines = [f"{digest}  {path}" for path, digest in sorted(pins.items())]
    header = (f"# SHA-256 pins for {TASK_ID}. "
              "source: paths are workspace-relative; worktree: and plain paths are "
              "SDK-worktree-relative. Lines are <sha256>  <path>.\n")
    return (header + "\n".join(lines) + "\n").encode("utf-8")


class Rejected(Exception):
    """A documented boundary rejection; carries a stable code and field."""

    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code + (":" + field if field else ""))
        self.code = code
        self.field = field


def reject(code: str, field: str = "") -> None:
    raise Rejected(code, field)


def _f32(value: float) -> float:
    try:
        return struct.unpack("<f", struct.pack("<f", value))[0]
    except (OverflowError, struct.error) as error:
        raise Rejected("nonfinite_value") from error


def f32_bytes(values: Iterable[float]) -> bytes:
    return b"".join(struct.pack("<f", _f32(float(value))) for value in values)


def f32_digest(values: Iterable[float]) -> str:
    return sha256(f32_bytes(values))


def _rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _validate_vector(values: Any, length: int, maximum: float, code: str) -> List[float]:
    if not isinstance(values, (list, tuple)) or len(values) != length:
        reject(code, "length")
    result: List[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            reject("feed_dtype")
        converted = _f32(float(value))
        if not math.isfinite(converted) or not math.isfinite(float(value)):
            reject("nonfinite_feed")
        if abs(converted) > maximum:
            reject("feed_range")
        result.append(converted)
    return result


def _validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        reject("invalid_config")
    allowed = set(CONFIG)
    for key in config:
        if key not in allowed:
            reject("unexpected_config_key", key)
    for key in CONFIG:
        if key not in config:
            reject("missing_config_key", key)
    if config["model"] != MODEL_ID:
        reject("unknown_model_id", "model")
    if config["execution_provider"] != "cpu_reference":
        reject("unsupported_execution_provider", "execution_provider")
    if config["graph_optimization"] != "disabled":
        reject("unsupported_graph_optimization", "graph_optimization")
    if config["intra_op_num_threads"] != 1 or config["inter_op_num_threads"] != 1:
        reject("nondeterministic_threading", "threads")
    if config["deterministic"] is not True:
        reject("nondeterministic_compute", "deterministic")
    return dict(config)


def _validate_model(model_id: str, data: bytes, digest: str, byte_count: int,
                    extra_assets: int = 0) -> Dict[str, Any]:
    if extra_assets:
        reject("extra_asset")
    if model_id != MODEL_ID:
        reject("unknown_model_id", "model_id")
    if not isinstance(data, (bytes, bytearray)):
        reject("invalid_asset")
    payload = bytes(data)
    if len(payload) > MAX_MODEL_BYTES:
        reject("oversized_model_asset")
    if len(payload) != byte_count:
        reject("byte_count_mismatch", "byte_count")
    if sha256(payload) != digest:
        reject("digest_mismatch", "sha256")
    try:
        model = strict_json(payload)
    except ValueError as error:
        reject(str(error).split(":", 1)[0], "model_json")
    if not isinstance(model, dict):
        reject("invalid_model_document")
    if set(model) != set(MODEL_SPEC):
        reject("unexpected_model_field")
    if model["schema_id"] != MODEL_SCHEMA:
        reject("wrong_schema", "schema_id")
    if model["model_id"] != MODEL_ID or model["model_version"] != MODEL_VERSION:
        reject("unknown_model_id", "model_id")
    if model["runtime_family"] != "onnxruntime":
        reject("wrong_runtime_family")
    if model["not_a_real_onnx_graph"] is not True:
        reject("real_graph_not_permitted")
    if model["evaluation"] != "linear_state_probe_v1":
        reject("unsupported_evaluation")
    if model["tensors"] != MODEL_SPEC["tensors"]:
        reject("tensor_definition_mismatch", "tensors")
    coefficients = model["coefficients"]
    if not isinstance(coefficients, dict) or set(coefficients) != set(MODEL_SPEC["coefficients"]):
        reject("coefficient_mismatch", "coefficients")
    for key, expected in MODEL_SPEC["coefficients"].items():
        value = coefficients[key]
        if expected.__class__ is list:
            if value != expected:
                reject("coefficient_mismatch", key)
        elif isinstance(value, bool) or not isinstance(value, (int, float)):
            reject("coefficient_mismatch", key)
        elif not math.isfinite(float(value)) or float(value) != float(expected):
            reject("coefficient_mismatch", key)
    state = model["state_init"]
    if not isinstance(state, list) or len(state) != 16:
        reject("state_init_shape", "state_init")
    for value in state:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            reject("coefficient_mismatch", "state_init")
        if not math.isfinite(float(value)):
            reject("nonfinite_state_init", "state_init")
        if _f32(float(value)) != 0.0:
            reject("state_init_not_zero", "state_init")
    return model


def execute_frame(waveform: List[float], state: List[float]) -> Tuple[List[float], List[float]]:
    """Exact float32 arithmetic; no transcendental or platform-dependent ops."""
    output: List[float] = []
    for index in range(160):
        value = _f32(0.75 * waveform[index] + 0.25 * state[index % 16])
        output.append(0.0 if value == 0.0 else value)
    next_state: List[float] = []
    signs = MODEL_SPEC["coefficients"]["state_input_signs"]
    for index in range(16):
        total = state[index]
        for step, sign in enumerate(signs):
            total += sign * waveform[index + 16 * step]
        value = _f32(0.125 * total)
        next_state.append(0.0 if value == 0.0 else value)
    return output, next_state


class ReferenceBoundary:
    """Task-local stand-in for the proposed ONNX Runtime adapter boundary."""

    def __init__(self, runtime_id: str = RUNTIME_ID, config: Optional[Dict[str, Any]] = None,
                 model_id: str = MODEL_ID, data: Optional[bytes] = None,
                 digest: Optional[str] = None, byte_count: Optional[int] = None,
                 extra_assets: int = 0, packaging_requested: bool = False,
                 download_requested: bool = False, real_model_requested: bool = False) -> None:
        if runtime_id != RUNTIME_ID:
            reject("unsupported_runtime", "runtime_id")
        if packaging_requested:
            reject("packaging_not_permitted")
        if download_requested:
            reject("download_not_permitted")
        if real_model_requested:
            reject("real_model_not_permitted")
        self.config = _validate_config(CONFIG if config is None else config)
        payload = model_bytes() if data is None else data
        self.model = _validate_model(
            model_id, payload,
            model_digest() if digest is None else digest,
            len(model_bytes()) if byte_count is None else byte_count,
            extra_assets)
        self.runtime_id = runtime_id
        self.model_digest = sha256(bytes(payload))
        self.model_byte_count = len(bytes(payload))
        self._state = [0.0] * 16
        self._closed = False
        self._frames = 0
        self._resets = 0
        self._last_record: Optional[Dict[str, Any]] = None

    def capability(self) -> Dict[str, Any]:
        if self._closed:
            reject("closed")
        return {
            "protocol": ADAPTER_PROTOCOL,
            "runtime_family": "onnxruntime",
            "runtime_id": self.runtime_id,
            "runtime_available": False,
            "runtime_invoked": False,
            "capability_source": "declared_fixture_not_runtime_query",
            "model_id": self.model["model_id"],
            "model_version": self.model["model_version"],
            "model_digest": self.model_digest,
            "model_byte_count": self.model_byte_count,
            "tensors": {name: dict(TENSORS[name]) for name in TENSOR_ORDER},
            "session_options": dict(SESSION_OPTIONS),
            "io_binding": {
                "preallocated_outputs_supported": True,
                "output_capacity_must_be_exact": True,
                "input_output_alias_rejected": True,
                "foreign_memory_not_supported": True,
            },
        }

    def reset(self, state: Optional[Any] = None) -> List[float]:
        if self._closed:
            reject("closed")
        values = [0.0] * 16 if state is None else state
        if not isinstance(values, (list, tuple)) or len(values) != 16:
            reject("reset_shape", "state")
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                reject("reset_dtype", "state")
            if not math.isfinite(float(value)):
                reject("nonfinite_state", "state")
            if abs(_f32(float(value))) > STATE_MAX:
                reject("state_range", "state")
        self._state = [_f32(float(value)) for value in values]
        self._frames = 0
        self._resets += 1
        return list(self._state)

    def close(self) -> None:
        self._closed = True

    def run(self, feeds: Any, bindings: Any = None) -> Dict[str, Any]:
        if self._closed:
            reject("closed")
        if not isinstance(feeds, dict):
            reject("invalid_feeds")
        allowed = {"waveform_in", "state_in"}
        for key in feeds:
            if key not in allowed:
                reject("unexpected_feed", key)
        if "waveform_in" not in feeds:
            reject("missing_feed", "waveform_in")
        waveform = _validate_vector(feeds["waveform_in"], 160, INPUT_MAX, "feed_shape")
        if "state_in" in feeds:
            state = _validate_vector(feeds["state_in"], 16, STATE_MAX, "feed_shape")
        else:
            state = list(self._state)
        if bindings is None:
            waveform_buffer = [0.0] * 160
            state_buffer = [0.0] * 16
        else:
            waveform_buffer, state_buffer = _validate_bindings(bindings, feeds)
        before = list(self._state)
        output, next_state = execute_frame(waveform, state)
        waveform_buffer[:] = output
        state_buffer[:] = next_state
        self._state = list(next_state)
        self._frames += 1
        record = {
            "frame_index": self._frames - 1,
            "waveform_in_sha256": f32_digest(waveform),
            "state_in_sha256": f32_digest(state),
            "waveform_out_sha256": f32_digest(output),
            "state_out_sha256": f32_digest(next_state),
            "state_before_sha256": f32_digest(before),
            "all_finite": all(math.isfinite(value) for value in output + next_state),
        }
        self._last_record = record
        return {
            "waveform_out": list(waveform_buffer),
            "state_out": list(state_buffer),
            "record": dict(record),
        }

    @property
    def state(self) -> List[float]:
        return list(self._state)

    @property
    def frames(self) -> int:
        return self._frames


def _validate_bindings(bindings: Any, feeds: Mapping[str, Any]) -> Tuple[List[float], List[float]]:
    if not isinstance(bindings, dict):
        reject("invalid_bindings")
    allowed = {"waveform_out", "state_out"}
    for key in bindings:
        if key not in allowed:
            reject("unexpected_binding", key)
    for key, length in (("waveform_out", 160), ("state_out", 16)):
        if key not in bindings:
            reject("missing_binding", key)
        buffer = bindings[key]
        if not isinstance(buffer, list):
            reject("binding_not_writable_list", key)
        if len(buffer) != length:
            reject("binding_shape", key)
        for feed in feeds.values():
            if buffer is feed:
                reject("binding_aliases_input", key)
    return bindings["waveform_out"], bindings["state_out"]


def _condition_frame(seed: int) -> List[float]:
    random = _rng(seed)
    return [_f32((next(random) - 0.5)) for _ in range(160)]


def summarize_run(result: Mapping[str, Any]) -> Dict[str, Any]:
    output = result["waveform_out"]
    state = result["state_out"]
    return {
        "waveform_out_sha256": f32_digest(output),
        "state_out_sha256": f32_digest(state),
        "waveform_out_first8": output[:8],
        "state_out_first4": state[:4],
        "all_finite": all(math.isfinite(value) for value in output + state),
        "frame_index": result["record"]["frame_index"],
    }


def measure_conditions() -> Dict[str, Any]:
    conditions: Dict[str, Any] = {}

    impulse = [0.0] * 160
    impulse[0] = 1.0
    adapter = ReferenceBoundary()
    result = adapter.run({"waveform_in": impulse})
    conditions["impulse"] = summarize_run(result)
    conditions["impulse"]["exact_checks"] = {
        "waveform_out_0": result["waveform_out"][0] == 0.75,
        "waveform_out_rest_zero": all(value == 0.0 for value in result["waveform_out"][1:]),
        "state_out_0": result["state_out"][0] == 0.125,
        "state_out_rest_zero": all(value == 0.0 for value in result["state_out"][1:]),
    }
    adapter.close()

    adapter = ReferenceBoundary()
    result = adapter.run({"waveform_in": [1.0] * 160})
    conditions["constant_one"] = summarize_run(result)
    conditions["constant_one"]["exact_checks"] = {
        "waveform_all_0_75": all(value == 0.75 for value in result["waveform_out"]),
        "state_all_zero": all(value == 0.0 for value in result["state_out"]),
    }
    adapter.close()

    adapter = ReferenceBoundary()
    result = adapter.run({"waveform_in": [-1.0] * 160})
    conditions["constant_negative_one"] = summarize_run(result)
    conditions["constant_negative_one"]["exact_checks"] = {
        "waveform_all_neg_0_75": all(value == -0.75 for value in result["waveform_out"]),
        "state_all_zero": all(value == 0.0 for value in result["state_out"]),
    }
    adapter.close()

    adapter = ReferenceBoundary()
    result = adapter.run({"waveform_in": [0.0] * 160})
    conditions["silence"] = summarize_run(result)
    conditions["silence"]["exact_checks"] = {
        "waveform_all_zero": all(value == 0.0 for value in result["waveform_out"]),
        "state_all_zero": all(value == 0.0 for value in result["state_out"]),
    }
    adapter.close()

    adapter = ReferenceBoundary()
    frames = []
    for index in range(FRAME_COUNT):
        frame = _condition_frame(20261125 + index)
        outcome = adapter.run({"waveform_in": frame})
        record = dict(outcome["record"])
        record["waveform_out_sha256"] = f32_digest(outcome["waveform_out"])
        record["state_out_sha256"] = f32_digest(outcome["state_out"])
        frames.append(record)
    final_state = adapter.state
    first_frame_digest = frames[0]["waveform_out_sha256"]
    zeroed = adapter.reset()
    replay = adapter.run({"waveform_in": _condition_frame(20261125)})
    conditions["lcg_three_frames"] = {
        "frames": frames,
        "held_state_sha256": f32_digest(final_state),
        "held_state_first4": final_state[:4],
        "all_finite": all(record["all_finite"] for record in frames),
        "reset_replay_matches": f32_digest(replay["waveform_out"]) == first_frame_digest,
        "reset_state_zero": all(value == 0.0 for value in zeroed),
        "waveform_out_sha256": f32_digest(replay["waveform_out"]),
        "state_out_sha256": f32_digest(replay["state_out"]),
        "waveform_out_first8": replay["waveform_out"][:8],
        "state_out_first4": replay["state_out"][:4],
        "frame_index": 0,
    }
    adapter.close()

    adapter = ReferenceBoundary()
    waveform = _condition_frame(20261201)
    state = _condition_frame(20261202)[:16]
    bound_waveform = [0.0] * 160
    bound_state = [0.0] * 16
    bound = adapter.run({"waveform_in": waveform, "state_in": state},
                        {"waveform_out": bound_waveform, "state_out": bound_state})
    unbound = ReferenceBoundary().run({"waveform_in": waveform, "state_in": state})
    conditions["explicit_state_and_bindings"] = summarize_run(bound)
    conditions["explicit_state_and_bindings"]["binding_path_matches"] = (
        f32_digest(bound["waveform_out"]) == f32_digest(unbound["waveform_out"])
        and f32_digest(bound["state_out"]) == f32_digest(unbound["state_out"])
        and f32_digest(bound_waveform) == f32_digest(unbound["waveform_out"])
        and f32_digest(bound_state) == f32_digest(unbound["state_out"]))
    adapter.close()

    return conditions


def _expect(callable_, code: str) -> Dict[str, Any]:
    try:
        result = callable_()
    except Rejected as error:
        if error.code != code:
            raise RuntimeError(f"expected {code}, got {error.code}:{error.field}") from error
        return {"code": error.code, "field": error.field}
    if code == "accepted":
        if hasattr(result, "close"):
            result.close()
        return {"code": "accepted", "field": ""}
    raise RuntimeError(f"expected rejection {code}, call was accepted")


def _mutated_model(**changes: Any) -> bytes:
    model = json.loads(json.dumps(MODEL_SPEC))
    for key, value in changes.items():
        model[key] = value
    return canonical_bytes(model) + b"\n"


def _adapter_for(data: bytes, **kwargs: Any) -> ReferenceBoundary:
    return ReferenceBoundary(data=data, digest=sha256(data), byte_count=len(data), **kwargs)


def adverse() -> Dict[str, Any]:
    """Exercise every documented fail-closed case; raise if any fails open."""
    model = model_bytes()
    bad_shape = json.loads(json.dumps(MODEL_SPEC))
    bad_shape["tensors"][0]["shape"] = [1, 159]
    bad_shape_bytes = canonical_bytes(bad_shape) + b"\n"
    bad_dtype = json.loads(json.dumps(MODEL_SPEC))
    bad_dtype["tensors"][0]["dtype"] = "f16"
    bad_dtype_bytes = canonical_bytes(bad_dtype) + b"\n"
    swapped = json.loads(json.dumps(MODEL_SPEC))
    swapped["tensors"] = [swapped["tensors"][1], swapped["tensors"][0],
                          swapped["tensors"][2], swapped["tensors"][3]]
    swapped_bytes = canonical_bytes(swapped) + b"\n"
    extra_tensor = json.loads(json.dumps(MODEL_SPEC))
    extra_tensor["tensors"].append(dict(extra_tensor["tensors"][0]))
    extra_tensor_bytes = canonical_bytes(extra_tensor) + b"\n"
    bad_coefficient = json.loads(json.dumps(MODEL_SPEC))
    bad_coefficient["coefficients"]["waveform_input"] = 0.5
    bad_coefficient_bytes = canonical_bytes(bad_coefficient) + b"\n"
    bad_state = json.loads(json.dumps(MODEL_SPEC))
    bad_state["state_init"] = [1.0] + [0.0] * 15
    bad_state_bytes = canonical_bytes(bad_state) + b"\n"
    short_state = json.loads(json.dumps(MODEL_SPEC))
    short_state["state_init"] = [0.0] * 15
    short_state_bytes = canonical_bytes(short_state) + b"\n"
    nonfinite = model.replace(b'"waveform_input":0.75', b'"waveform_input":1e999')
    duplicate = b'{"schema_id":"' + MODEL_SCHEMA.encode() + b'","schema_id":"x"}'
    oversize = b"{" + b" " * MAX_MODEL_BYTES + b"}"

    model_rejections = {
        "digest_mismatch": _expect(
            lambda: ReferenceBoundary(model_id=MODEL_ID, data=model,
                                      digest="0" * 64, byte_count=len(model)),
            "digest_mismatch"),
        "byte_count_mismatch": _expect(
            lambda: ReferenceBoundary(model_id=MODEL_ID, data=model,
                                      digest=sha256(model), byte_count=len(model) + 1),
            "byte_count_mismatch"),
        "asset_id_mismatch": _expect(
            lambda: ReferenceBoundary(model_id="unknown-model", data=model,
                                      digest=sha256(model), byte_count=len(model)),
            "unknown_model_id"),
        "extra_asset": _expect(
            lambda: ReferenceBoundary(model_id=MODEL_ID, data=model,
                                      digest=sha256(model), byte_count=len(model),
                                      extra_assets=1),
            "extra_asset"),
        "oversized_asset": _expect(
            lambda: _adapter_for(oversize), "oversized_model_asset"),
        "malformed_json": _expect(lambda: _adapter_for(b"{"), "malformed_json"),
        "duplicate_json_key": _expect(lambda: _adapter_for(duplicate), "duplicate_json_key"),
        "wrong_schema": _expect(
            lambda: _adapter_for(_mutated_model(schema_id="audio-sdk/other/0.1")),
            "wrong_schema"),
        "real_graph_claim": _expect(
            lambda: _adapter_for(_mutated_model(not_a_real_onnx_graph=False)),
            "real_graph_not_permitted"),
        "unsupported_evaluation": _expect(
            lambda: _adapter_for(_mutated_model(evaluation="onnx_runtime_graph_v1")),
            "unsupported_evaluation"),
        "tensor_shape_mismatch": _expect(
            lambda: _adapter_for(bad_shape_bytes), "tensor_definition_mismatch"),
        "tensor_dtype_mismatch": _expect(
            lambda: _adapter_for(bad_dtype_bytes), "tensor_definition_mismatch"),
        "tensor_order_mismatch": _expect(
            lambda: _adapter_for(swapped_bytes), "tensor_definition_mismatch"),
        "tensor_extra": _expect(
            lambda: _adapter_for(extra_tensor_bytes), "tensor_definition_mismatch"),
        "coefficient_mismatch": _expect(
            lambda: _adapter_for(bad_coefficient_bytes), "coefficient_mismatch"),
        "nonfinite_coefficient": _expect(
            lambda: _adapter_for(nonfinite), "coefficient_mismatch"),
        "state_init_nonzero": _expect(
            lambda: _adapter_for(bad_state_bytes), "state_init_not_zero"),
        "state_init_short": _expect(
            lambda: _adapter_for(short_state_bytes), "state_init_shape"),
    }

    config_rejections = {
        "missing_selection": _expect(lambda: ReferenceBoundary(config={}), "missing_config_key"),
        "unknown_key": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "device": "gpu"}),
            "unexpected_config_key"),
        "wrong_model": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "model": "other"}),
            "unknown_model_id"),
        "unsupported_provider": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "execution_provider": "cuda"}),
            "unsupported_execution_provider"),
        "unsupported_graph_optimization": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "graph_optimization": "all"}),
            "unsupported_graph_optimization"),
        "nondeterministic_threading": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "intra_op_num_threads": 2}),
            "nondeterministic_threading"),
        "nondeterministic_compute": _expect(
            lambda: ReferenceBoundary(config={**CONFIG, "deterministic": False}),
            "nondeterministic_compute"),
        "invalid_config": _expect(lambda: ReferenceBoundary(config=[]), "invalid_config"),
    }

    adapter = ReferenceBoundary()
    baseline_state = adapter.state
    nan = float("nan")

    def feed_case(feeds: Any) -> Dict[str, Any]:
        try:
            adapter.run(feeds)
        except Rejected as error:
            unchanged = adapter.state == baseline_state
            return {"code": error.code, "field": error.field, "state_unchanged": unchanged}
        raise RuntimeError("feed rejection accepted")

    feed_rejections = {
        "missing_waveform": feed_case({}),
        "unexpected_feed": feed_case({"waveform_in": [0.0] * 160, "extra": [0.0]}),
        "waveform_shape": feed_case({"waveform_in": [0.0] * 159}),
        "waveform_dtype": feed_case({"waveform_in": ["x"] * 160}),
        "waveform_bool": feed_case({"waveform_in": [True] * 160}),
        "waveform_nonfinite": feed_case({"waveform_in": [nan] * 160}),
        "waveform_range": feed_case({"waveform_in": [2.0] * 160}),
        "state_shape": feed_case({"waveform_in": [0.0] * 160, "state_in": [0.0] * 15}),
        "state_nonfinite": feed_case({"waveform_in": [0.0] * 160,
                                      "state_in": [nan] * 16}),
    }
    state_after_feed_rejections = list(adapter.state)

    def binding_case(bindings: Any, feeds: Any) -> Dict[str, Any]:
        try:
            adapter.run(feeds, bindings)
        except Rejected as error:
            return {"code": error.code, "field": error.field}
        raise RuntimeError("binding rejection accepted")

    shared = [0.0] * 160
    binding_rejections = {
        "missing_output": binding_case({"waveform_out": [0.0] * 160},
                                       {"waveform_in": [0.0] * 160}),
        "unexpected_output": binding_case({"waveform_out": [0.0] * 160,
                                           "state_out": [0.0] * 16,
                                           "extra": [0.0]},
                                          {"waveform_in": [0.0] * 160}),
        "waveform_binding_shape": binding_case({"waveform_out": [0.0] * 159,
                                                "state_out": [0.0] * 16},
                                               {"waveform_in": [0.0] * 160}),
        "state_binding_shape": binding_case({"waveform_out": [0.0] * 160,
                                             "state_out": [0.0] * 15},
                                            {"waveform_in": [0.0] * 160}),
        "tuple_not_writable": binding_case({"waveform_out": (0.0,) * 160,
                                            "state_out": [0.0] * 16},
                                           {"waveform_in": [0.0] * 160}),
        "binding_aliases_input": binding_case({"waveform_out": shared,
                                               "state_out": [0.0] * 16},
                                              {"waveform_in": shared}),
    }
    state_after_binding_rejections = list(adapter.state)

    closed = ReferenceBoundary()
    closed.close()
    close_again = _expect(closed.close, "accepted")
    run_after_close = _expect(lambda: closed.run({"waveform_in": [0.0] * 160}), "closed")
    reset_short = _expect(lambda: adapter.reset([0.0] * 15), "reset_shape")
    reset_nonfinite = _expect(lambda: adapter.reset([nan] * 16), "nonfinite_state")
    reset_state_unchanged = adapter.state == state_after_binding_rejections
    reset_valid = adapter.reset()
    valid_reset = {
        "code": "accepted",
        "state_zero": all(value == 0.0 for value in reset_valid),
        "reset_state_unchanged_by_invalid": reset_state_unchanged,
    }
    adapter.close()

    rights_rejections = {
        "packaging_requested": _expect(
            lambda: ReferenceBoundary(packaging_requested=True), "packaging_not_permitted"),
        "download_requested": _expect(
            lambda: ReferenceBoundary(download_requested=True), "download_not_permitted"),
        "real_model_requested": _expect(
            lambda: ReferenceBoundary(real_model_requested=True), "real_model_not_permitted"),
    }
    runtime_rejections = {
        "unknown_runtime": _expect(
            lambda: ReferenceBoundary(runtime_id="onnxruntime/1.31.1"),
            "unsupported_runtime"),
        "candidate_runtime_not_pinned": _expect(
            lambda: ReferenceBoundary(runtime_id="onnxruntime-osx-arm64-1.31.1/1.31.1"),
            "unsupported_runtime"),
    }

    groups = {
        "model_rejections": model_rejections,
        "config_rejections": config_rejections,
        "feed_rejections": feed_rejections,
        "binding_rejections": binding_rejections,
        "rights_rejections": rights_rejections,
        "runtime_rejections": runtime_rejections,
        "lifecycle": {
            "run_after_close": run_after_close,
            "double_close": close_again,
            "reset_shape": reset_short,
            "reset_nonfinite": reset_nonfinite,
            "valid_reset": valid_reset,
        },
        "state": {
            "unchanged_by_feed_rejections": state_after_feed_rejections == baseline_state,
            "unchanged_by_binding_rejections":
                state_after_binding_rejections == state_after_feed_rejections,
        },
    }
    failures: List[str] = []
    for name, cases in groups.items():
        if not isinstance(cases, dict):
            continue
        for case_name, value in cases.items():
            if not isinstance(value, dict):
                continue
            code = value.get("code")
            if name == "lifecycle":
                if case_name == "valid_reset":
                    if code != "accepted" or not value.get("state_zero"):
                        failures.append(f"{name}.{case_name}")
                elif case_name == "double_close":
                    if code != "accepted":
                        failures.append(f"{name}.{case_name}")
                elif code not in {"closed", "reset_shape", "nonfinite_state"}:
                    failures.append(f"{name}.{case_name}")
                continue
            if name == "state":
                if value is not True:
                    failures.append(f"{name}.{case_name}")
                continue
            if not isinstance(code, str) or code == "accepted":
                failures.append(f"{name}.{case_name}")
            if name in ("feed_rejections", "binding_rejections") and \
                    value.get("state_unchanged") is False:
                failures.append(f"{name}.{case_name}.state_changed")
    if failures:
        raise RuntimeError("fail-open boundary cases: " + ", ".join(failures))
    rejection_groups = {
        "model_rejections": len(model_rejections),
        "config_rejections": len(config_rejections),
        "feed_rejections": len(feed_rejections),
        "binding_rejections": len(binding_rejections),
        "rights_rejections": len(rights_rejections),
        "runtime_rejections": len(runtime_rejections),
    }
    rejection_cases = sum(rejection_groups.values())
    lifecycle_checks = len(groups["lifecycle"])
    lifecycle_rejected = sum(
        1 for value in groups["lifecycle"].values() if value.get("code") != "accepted")
    lifecycle_accepted = lifecycle_checks - lifecycle_rejected
    if lifecycle_rejected + lifecycle_accepted != lifecycle_checks:
        raise RuntimeError("lifecycle counts do not add up")
    groups["counts"] = {
        "rejection_groups": rejection_groups,
        "rejection_cases": rejection_cases,
        "lifecycle_checks": lifecycle_checks,
        "lifecycle_rejected": lifecycle_rejected,
        "lifecycle_accepted": lifecycle_accepted,
        "total_checks": rejection_cases + lifecycle_checks,
        "failed_open": 0,
        "all_rejections_closed": True,
    }
    return groups


def runtime_readiness() -> Dict[str, Any]:
    spec = importlib.util.find_spec("onnxruntime")
    available = spec is not None
    sdk_scan = ["requirements-build.txt", "CMakeLists.txt", "api/CMakeLists.txt",
                "bindings/python/pyproject.toml"]
    scanned: Dict[str, bool] = {}
    for relative in sdk_scan:
        path = SDK_ROOT / relative
        try:
            text = path.read_text(encoding="utf-8").lower()
        except OSError:
            scanned[relative] = False
            continue
        scanned[relative] = "onnxruntime" in text
    pin_present = any(scanned.values())
    interpreter = ".".join(str(part) for part in sys.version_info[:3])
    return {
        "runtime_family": "onnxruntime",
        "python_module": "onnxruntime",
        "interpreter": interpreter,
        "module_spec_found": available,
        "importable": available,
        "installed_version": None,
        "install_location": None,
        "exact_error": (None if available
                        else "ModuleNotFoundError: No module named 'onnxruntime'"),
        "sdk_files_scanned": scanned,
        "sdk_runtime_pin_present": pin_present,
        "candidate_observed": ("onnxruntime-osx-arm64-1.31.1 exists only in a "
                               "non-SDK local .deps tree; it is not approved, pinned, "
                               "imported, invoked, linked or used here"),
        "candidate_observed_version": "1.31.1",
        "candidate_used": False,
        "blocked": True,
        "blocker": ("No pinned, rights-cleared ONNX Runtime is available to the pinned "
                    "CPython 3.12.16 interpreter or the SDK build. The synthetic adapter "
                    "boundary can be exercised, but no real ONNX graph can be created, "
                    "validated, run or measured."),
        "reopen_conditions": [
            "Pin one exact ONNX Runtime distribution (name, version, platform, byte "
            "count and SHA-256) in an SDK lock or requirement file and clear its "
            "redistribution terms under review.",
            "Record the exact install location and import result from the pinned "
            "CPython 3.12.16 environment.",
            "Supply a rights-cleared caller-owned ONNX graph with exact input/output "
            "names, dtypes, shapes, opset and byte digest.",
            "Exercise the adapter against that graph and compare deterministic CPU "
            "outputs with an approved reference before any provider or release claim.",
        ],
    }


def tool_profile() -> Dict[str, Any]:
    return {
        "profile": "tool",
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
                "detail": ("create, capability, two runs, reset, replay, double close "
                           "and rejected post-close run on the frozen adapter boundary"),
            },
            "caller_owned_inputs": {
                "status": "passed_synthetic",
                "detail": "caller supplies model bytes, feeds and preallocated outputs",
            },
            "malformed_inputs": {
                "status": "passed_synthetic",
                "detail": "model, config, feed, binding, lifecycle and rights cases fail closed",
            },
            "missing_optional_selection": {
                "status": "passed_synthetic",
                "detail": "unknown runtime/provider/model and absent state selection are explicit",
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
            "real ONNX graph parse, validation or execution",
            "target-device timing, memory or deadline",
            "workload throughput or benchmark result",
        ],
        "remaining_gates": [
            "pinned and rights-cleared ONNX Runtime",
            "rights-cleared caller-owned ONNX graph",
            "real graph output parity on the pinned runtime",
            "installed adapter and provider intake review",
            "measured workload and target-device timing",
            "independent review and release approval",
        ],
    }


def artifact_contract() -> Dict[str, Any]:
    return {
        "schema_id": "audio-sdk/onnx-runtime-reference-runtime/contract/0.1",
        "contract_version": "0.1",
        "task": TASK_ID,
        "component": COMPONENT_ID,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": "swarm/SDK-ONNX-RUNTIME-REFERENCE-RUNTIME",
        "status": "task_local_proposed_boundary",
        "evidence_status": "incomplete",
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "verification_profile": PROFILE,
        "reference_family": REFERENCE_FAMILY,
        "adapter_protocol": ADAPTER_PROTOCOL,
        "scope": ("Task-local synthetic documentation and exercise of the proposed "
                  "developer-facing ONNX Runtime adapter boundary. No SDK adapter, "
                  "public provider, ONNX Runtime import, real graph, weights, audio, "
                  "device measurement or release claim is added."),
        "source_identity": {
            "path": "cpp-library/src/stages/onnx_common.cpp",
            "sha256": SOURCE_PINS["source:cpp-library/src/stages/onnx_common.cpp"],
            "documented_constraints": [
                "ONNX Runtime is optional and guarded by AE_ENABLE_ONNXRUNTIME",
                "a shared Ort::Env is created only when the optional runtime is enabled",
                "model assets are resolved by logical id from prepare-time caller assets",
                "missing asset lists and unknown model ids fail with AE_NOT_READY",
                "no network, download or filesystem model lookup is performed in stages",
            ],
            "note": ("Source inspection is a boundary anchor only. No C++ stage is "
                     "built, no ONNX session is created and no model weight is loaded."),
        },
        "frontend_contract": {
            "identity": "audio-sdk/v0-f32-16k-mono-160",
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "hop_samples": 160,
            "content_delay_samples": 0,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "provider_registration": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_settings": {},
        },
        "model_fixture": {
            "asset_id": MODEL_ID,
            "schema_id": MODEL_SCHEMA,
            "asset_kind": "synthetic_non_onnx_descriptor",
            "real_onnx_graph": False,
            "real_model_weights": False,
            "storage": "external_caller_supplied",
            "rights": {
                "asset_class": "synthetic",
                "acquisition": "generated_in_this_evidence_directory",
                "evaluation": "allowed_synthetic_only",
                "redistribution": "not_applicable_no_external_bytes",
                "public_playback": "not_applicable",
            },
        },
        "session_requirements": {
            "runtime_id": RUNTIME_ID,
            "runtime_family": "onnxruntime",
            "execution_provider": "CPUExecutionProvider",
            "deterministic_compute": True,
            "options": SESSION_OPTIONS,
            "configuration": CONFIG,
            "exact_config_only": True,
            "note": ("These are declared requirements for a future adapter, not "
                     "values queried from an installed runtime."),
        },
        "tensors": {name: dict(TENSORS[name]) for name in TENSOR_ORDER},
        "io_binding": {
            "required": False,
            "preallocated_outputs_supported": True,
            "output_capacity_must_be_exact": True,
            "alias_with_input_rejected": True,
            "foreign_memory_supported": False,
            "writable_list_required": True,
        },
        "fail_closed": [
            "unknown or unpinned runtime id",
            "missing, unknown or extra model asset",
            "asset byte-count or SHA-256 mismatch",
            "oversized, malformed, duplicate-key or non-object model document",
            "wrong schema, runtime family, real-graph claim or evaluation",
            "tensor name, order, role, dtype or shape mismatch",
            "coefficient mismatch, nonfinite coefficient or invalid state init",
            "missing, extra or invalid configuration key",
            "unsupported execution provider, graph optimization or threading",
            "missing, extra, wrong-shape, wrong-dtype, nonfinite or out-of-range feed",
            "missing, extra, wrong-capacity, non-writable or aliased output binding",
            "run after close; invalid reset; packaging, download or real-model request",
        ],
        "rights_gap": {
            "blocked": True,
            "exact_runtime_pinned": False,
            "runtime_terms_verified": False,
            "real_model_terms_verified": False,
            "consequence": ("No ONNX Runtime import, vendoring, linking, installed "
                            "adapter, public provider or release claim is permitted "
                            "until the exact runtime and any model asset are pinned "
                            "and rights are cleared."),
        },
        "invariants": [
            "Only this task evidence directory is written.",
            "No shared C++, CMake, CI, contract, public header, registry, default, "
            "board or handoff file is modified.",
            "No ONNX Runtime package, library, header or graph is imported, linked, "
            "shipped or invoked.",
            "No model weights, real audio, download or external asset is used.",
            "The synthetic fixture is a deterministic caller-supplied descriptor, "
            "not an ONNX protobuf or executable graph.",
            "All boundary rejections fail closed without advancing adapter state.",
            "Three cold-start report regenerations are byte-identical.",
            "No device timing, listening, benchmark or release result is claimed.",
        ],
        "reopening_conditions": [
            "Pin one exact ONNX Runtime distribution and clear its redistribution terms.",
            "Add a rights-cleared caller-owned ONNX graph with exact tensor metadata.",
            "Implement the optional adapter behind an off-by-default build flag without "
            "changing installed v0 geometry or shared defaults.",
            "Compare deterministic CPU outputs with an approved reference and record "
            "negative, malformed and missing-asset cases.",
            "Measure the exact installed runtime on the target host before any "
            "availability or benchmark claim.",
            "Complete provider intake and independent review before any public exposure.",
        ],
    }


def artifact_adapter() -> Dict[str, Any]:
    return {
        "adapter_id": "onnx-runtime-reference-runtime-synthetic-boundary-v1",
        "adapter_protocol": ADAPTER_PROTOCOL,
        "component_id": COMPONENT_ID,
        "task": TASK_ID,
        "reference_family": REFERENCE_FAMILY,
        "runtime_family": "onnxruntime",
        "runtime_id": RUNTIME_ID,
        "runtime_available": False,
        "runtime_invoked": False,
        "runtime_pinned": False,
        "model_id": MODEL_ID,
        "model_digest": model_digest(),
        "model_byte_count": len(model_bytes()),
        "model_kind": "synthetic_non_onnx_descriptor",
        "real_onnx_graph": False,
        "real_model_weights": False,
        "evaluation_path": "task_local_python_fixture",
        "production_adapter_path": "not_implemented",
        "entrypoint": ["python3", f"{TASK_REL}/run.py", "--all"],
        "tensors": {name: dict(TENSORS[name]) for name in TENSOR_ORDER},
        "session_options": dict(SESSION_OPTIONS),
        "configuration_keys": sorted(CONFIG),
        "configuration": dict(CONFIG),
        "io_binding": {
            "preallocated_outputs_supported": True,
            "exact_capacity_required": True,
            "alias_rejected": True,
        },
        "registered": False,
        "registration": "unregistered-evidence-only",
        "enabled_by_default": False,
        "default_enabled": False,
        "processor_exposure": False,
        "c_public_boundary": "not_used",
        "public_api_abi_changed": False,
        "installed_v0_behavior_changed": False,
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "hop_samples": 160,
        "content_delay_samples": 0,
        "decision": DECISION,
    }


def artifact_provider() -> Dict[str, Any]:
    return {
        "schema_id": "audio-sdk/onnx-runtime-reference-runtime/provider/0.1",
        "identity": "onnx-runtime-reference-runtime-synthetic-provider/0.1",
        "task": TASK_ID,
        "reference_family": REFERENCE_FAMILY,
        "manifest": "task-local-only",
        "purpose": ("documents the proposed, opt-in, unregistered and disabled-by-default "
                    "developer adapter boundary; never selected by the SDK registry, "
                    "defaults, build or installed behavior"),
        "registered": False,
        "default_enabled": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_changed": False,
        "installed_v0_behavior_changed": False,
        "processor_exposure": False,
        "c_provider": False,
        "c_boundary_included": False,
        "asset_or_weight_dependency": False,
        "real_model_weights": False,
        "vendor_runtime_invoked": False,
        "runtime_downloaded": False,
        "opt_in_required": True,
        "sample_rate_hz": 16000,
        "channels": 1,
        "input_frame_shape": [160],
        "output_frame_shape": [160],
        "decision": DECISION,
    }


TYPICAL_PROBE_SEQUENCE = ("create", "capability", "run_frame_0", "run_frame_1",
                          "reset", "run_after_reset", "close", "close_again",
                          "run_after_close")


def typical_probe() -> Dict[str, Any]:
    """Execute the claimed create -> capability -> run -> reset -> close path."""
    adapter = ReferenceBoundary()
    capability = adapter.capability()
    frame_zero = _condition_frame(20261203)
    first = summarize_run(adapter.run({"waveform_in": frame_zero}))
    second = summarize_run(adapter.run({"waveform_in": _condition_frame(20261204)}))
    state_before_reset = f32_digest(adapter.state)
    reset_returned = adapter.reset()
    reset_digest = f32_digest(reset_returned)
    replay = summarize_run(adapter.run({"waveform_in": frame_zero}))
    adapter.close()
    adapter.close()
    run_after_close = "accepted"
    try:
        adapter.run({"waveform_in": frame_zero})
    except Rejected as error:
        run_after_close = error.code
    capability_ok = (
        capability["runtime_id"] == RUNTIME_ID
        and capability["tensors"] == TENSORS
        and capability["session_options"] == SESSION_OPTIONS
        and capability["runtime_available"] is False
        and capability["runtime_invoked"] is False)
    reset_ok = (all(value == 0.0 for value in reset_returned)
                and reset_digest == f32_digest([0.0] * 16))
    replay_ok = (replay["waveform_out_sha256"] == first["waveform_out_sha256"]
                 and replay["state_out_sha256"] == first["state_out_sha256"])
    close_ok = run_after_close == "closed"
    all_passed = capability_ok and reset_ok and replay_ok and close_ok
    return {
        "status": "passed_synthetic" if all_passed else "failed",
        "sequence": list(TYPICAL_PROBE_SEQUENCE),
        "steps_completed": len(TYPICAL_PROBE_SEQUENCE),
        "capability": {
            "called": True,
            "capability_sha256": sha256(canonical_bytes(capability)),
            "runtime_id": capability["runtime_id"],
            "capability_source": capability["capability_source"],
            "runtime_available": capability["runtime_available"],
            "runtime_invoked": capability["runtime_invoked"],
            "tensors_match": capability["tensors"] == TENSORS,
            "session_options_match": capability["session_options"] == SESSION_OPTIONS,
        },
        "run_before_reset": {
            "frames": 2,
            "frame_digests": [first["waveform_out_sha256"], second["waveform_out_sha256"]],
            "held_state_sha256": state_before_reset,
            "state_advanced": first["state_out_sha256"] != second["state_out_sha256"],
        },
        "reset": {
            "called": True,
            "returned_state_sha256": reset_digest,
            "zero_state": reset_ok,
        },
        "run_after_reset": {
            "frame_digest": replay["waveform_out_sha256"],
            "state_sha256": replay["state_out_sha256"],
            "replay_matches_first_frame": replay_ok,
            "all_finite": replay["all_finite"],
        },
        "close": {
            "called": True,
            "close_again_accepted": True,
            "run_after_close_code": run_after_close,
            "run_after_close_rejected": close_ok,
        },
        "create_capability_run_reset_close": all_passed,
        "all_steps_passed": all_passed,
    }


def build_report() -> Dict[str, Any]:
    conditions = measure_conditions()
    adverse_cases = adverse()
    probe = typical_probe()
    if not probe["all_steps_passed"]:
        raise RuntimeError("canonical typical probe did not complete every step")
    repeats = []
    for _ in range(3):
        adapter = ReferenceBoundary()
        result = adapter.run({"waveform_in": _condition_frame(20261203)})
        repeats.append(f32_digest(result["waveform_out"]))
        adapter.close()
    readiness = runtime_readiness()
    if not readiness["blocked"] or readiness["module_spec_found"]:
        raise RuntimeError("runtime readiness is not blocked; evidence package must be revisited")
    model = model_bytes()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT_ID,
        "reference_family": REFERENCE_FAMILY,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": "incomplete",
        "scope": ("Task-local, deterministic, synthetic exercise of the proposed "
                  "developer-facing ONNX Runtime adapter boundary. No SDK adapter, "
                  "public provider, runtime import, real graph, weights, media, "
                  "timing, listening, benchmark or release result is produced."),
        "boundary": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_settings": {},
            "public_api_abi_change": False,
            "provider_registration": False,
            "processor_exposure": False,
            "c_public_boundary": False,
            "installed_v0_geometry_preserved": True,
            "evaluation_path": "task_local_python_fixture",
            "production_adapter_path": "not_implemented",
        },
        "format": dict(FORMAT),
        "adapter_contract": {
            "protocol": ADAPTER_PROTOCOL,
            "runtime_id": RUNTIME_ID,
            "runtime_family": "onnxruntime",
            "tensors": {name: dict(TENSORS[name]) for name in TENSOR_ORDER},
            "session_options": dict(SESSION_OPTIONS),
            "configuration": dict(CONFIG),
            "io_binding": {
                "preallocated_outputs_supported": True,
                "exact_capacity_required": True,
                "alias_rejected": True,
                "foreign_memory_supported": False,
            },
            "capability_source": "declared_fixture_not_runtime_query",
        },
        "model_asset": {
            "asset_id": MODEL_ID,
            "schema_id": MODEL_SCHEMA,
            "asset_kind": "synthetic_non_onnx_descriptor",
            "sha256": sha256(model),
            "byte_count": len(model),
            "storage": "external_caller_supplied",
            "real_onnx_graph": False,
            "real_model_weights": False,
            "rights": artifact_contract()["model_fixture"]["rights"],
        },
        "runtime_readiness": readiness,
        "conditions": conditions,
        "tool_profile": tool_profile(),
        "boundary_checks": {
            "typical_api_use": probe,
            "caller_owned_inputs": {
                "status": "passed_synthetic",
                "model_supplied_by_caller": True,
                "feeds_copied_before_run": True,
                "preallocated_outputs_validated": True,
                "binding_path_matches_unbound_path": conditions[
                    "explicit_state_and_bindings"]["binding_path_matches"],
            },
            "malformed_inputs": {
                "status": "passed_synthetic",
                "cases": adverse_cases["counts"]["rejection_cases"],
                "rejection_cases": adverse_cases["counts"]["rejection_cases"],
                "lifecycle_checks": adverse_cases["counts"]["lifecycle_checks"],
                "total_checks": adverse_cases["counts"]["total_checks"],
                "failed_open": adverse_cases["counts"]["failed_open"],
            },
            "missing_optional_selection": {
                "status": "passed_synthetic",
                "unknown_runtime_rejected": adverse_cases[
                    "runtime_rejections"]["unknown_runtime"]["code"] == "unsupported_runtime",
                "missing_config_rejected": adverse_cases[
                    "config_rejections"]["missing_selection"]["code"] == "missing_config_key",
                "held_state_fallback": True,
            },
            "compile_and_build_evidence": {
                "status": "not_run",
                "built": False,
                "linked": False,
                "reason": "evidence-only package; no SDK build, adapter target or link step",
            },
            "synthetic_runtime_evidence": {
                "status": "passed_synthetic",
                "onnx_runtime_invoked": False,
                "real_graph_parsed": False,
                "deterministic_float32_cpu_probe": True,
            },
            "measured_workload_support": {
                "status": "not_reported",
                "reason": "no pinned runtime and no target-device workload measurement",
            },
        },
        "adverse": adverse_cases,
        "repeatability": {
            "count": 3,
            "byte_identical": len(set(repeats)) == 1,
            "digests": repeats,
            "note": ("Three fresh adapter instances over one frozen probe; report "
                     "generation is also repeated three times byte-identically."),
        },
        "gates": [
            {
                "id": "pinned_runtime",
                "status": "blocked",
                "reason": ("No exact ONNX Runtime distribution is pinned in the SDK or "
                           "importable from the pinned CPython 3.12.16 interpreter."),
                "reopen": ("Pin an exact version, platform, byte count and SHA-256 in a "
                           "lock file and clear distribution terms."),
            },
            {
                "id": "real_graph_parity",
                "status": "blocked",
                "reason": ("Only a synthetic non-ONNX descriptor exists; no rights-cleared "
                           "ONNX graph or approved reference output is available."),
                "reopen": ("Supply a rights-cleared caller-owned ONNX graph and compare "
                           "deterministic outputs with an approved reference."),
            },
            {
                "id": "installed_adapter",
                "status": "blocked",
                "reason": ("No optional adapter, build target, package or installed "
                           "consumer is implemented or reviewed."),
                "reopen": ("Implement the off-by-default adapter, build and install it, "
                           "and run the tool acceptance profile."),
            },
            {
                "id": "provider_intake",
                "status": "blocked",
                "reason": ("The boundary is unregistered, OFF by default and has empty "
                           "descriptor settings; no intake review exists."),
                "reopen": ("Complete provider intake, licensing and independent review "
                           "before any catalog or processor exposure."),
            },
            {
                "id": "workload_timing",
                "status": "blocked",
                "reason": ("No runtime or target-device load, memory, pacing or deadline "
                           "measurement exists."),
                "reopen": ("Measure the exact installed runtime on the target host under "
                           "a declared workload and limits."),
            },
            {
                "id": "release_approval",
                "status": "blocked",
                "reason": "Independent review and release approval have not occurred.",
                "reopen": "Obtain independent review at the exact head before any release.",
            },
        ],
        "rights_gap": artifact_contract()["rights_gap"],
        "negative_claims": {
            "onnx_runtime_invoked": False,
            "onnx_runtime_imported": False,
            "real_onnx_graph": False,
            "real_model_weights": False,
            "real_media": False,
            "runtime_download": False,
            "device_timing": False,
            "listening_result": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "no_missing_result_qualifies_candidate": True,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "missing_evidence": [
            "pinned and rights-cleared ONNX Runtime distribution",
            "rights-cleared caller-owned ONNX graph",
            "real graph output parity on the pinned runtime",
            "installed adapter build and package evidence",
            "provider intake and independent review",
            "target-device workload, memory and deadline measurement",
        ],
        "evidence_classes": [
            "documented_adapter_boundary",
            "synthetic_caller_supplied_model_descriptor",
            "frozen_float32_cpu_golden_vectors",
            "runtime_unavailability_probe",
        ],
        "invariants": artifact_contract()["invariants"],
    }


def contract_bytes() -> bytes:
    return (json.dumps(artifact_contract(), indent=2, sort_keys=True) + "\n").encode("utf-8")


def adapter_bytes() -> bytes:
    return canonical_bytes(artifact_adapter()) + b"\n"


def provider_bytes() -> bytes:
    return canonical_bytes(artifact_provider()) + b"\n"
