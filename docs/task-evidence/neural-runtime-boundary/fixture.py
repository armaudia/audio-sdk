"""Model-free fixture for the proposed optional neural runtime boundary.

No weights, downloads, native runtime or model result is embedded. The stub
only freezes tensor/state/hook shapes, asset identity, mode separation and
finite-state behavior so later real adapters can be checked against it.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Sequence

CONTRACT_ID = "audio-sdk/neural-runtime-boundary/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
STATE_SAMPLES = 16
STREAMING = "streaming"
OFFLINE = "offline"
RUNTIME_IDS = ("cpu-reference.stub/0.1", "alternate-runtime.stub/0.1")
REQUIRED_HOOKS = ("capability_query", "process_mode", "resume_prepare")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")


class Status(str, Enum):
    OK = "ok"
    REJECTED_MODEL = "rejected_model"
    REJECTED_ASSET_MISSING = "rejected_asset_missing"
    REJECTED_ASSET_CHANGED = "rejected_asset_changed"
    REJECTED_RUNTIME = "rejected_runtime"
    REJECTED_MODE = "rejected_mode"
    REJECTED_STATE = "rejected_state"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_HOOK = "rejected_hook"
    CLOSED = "closed"


@dataclass(frozen=True)
class TensorSpec:
    name: str
    shape: tuple[int, ...]
    dtype: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "shape": list(self.shape), "dtype": self.dtype}


EXPECTED_TENSORS = (
    TensorSpec("waveform_in", (1, FRAME_SAMPLES), "f32"),
    TensorSpec("state_in", (1, STATE_SAMPLES), "f32"),
    TensorSpec("waveform_out", (1, FRAME_SAMPLES), "f32"),
    TensorSpec("state_out", (1, STATE_SAMPLES), "f32"),
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


@dataclass(frozen=True)
class GraphSpec:
    tensors: tuple[TensorSpec, ...]
    hooks: tuple[str, ...]

    @property
    def digest(self) -> str:
        return hashlib.sha256(_canonical_bytes(
            {"tensors": [spec.as_dict() for spec in self.tensors],
             "hooks": list(self.hooks)}
        )).hexdigest()

    def check(self) -> Optional[Status]:
        if set(self.tensors) != set(EXPECTED_TENSORS):
            return Status.REJECTED_TENSOR
        if set(self.hooks) != set(REQUIRED_HOOKS):
            return Status.REJECTED_HOOK
        return None


GRAPH = GraphSpec(EXPECTED_TENSORS, REQUIRED_HOOKS)


@dataclass(frozen=True)
class ModelId:
    model_id: str
    version: str
    asset_sha256: str
    graph_digest: str

    def check(self) -> Optional[Status]:
        if not _ID.match(self.model_id) or not _ID.match(self.version):
            return Status.REJECTED_MODEL
        if not _HEX64.match(self.asset_sha256) or not _HEX64.match(self.graph_digest):
            return Status.REJECTED_MODEL
        if self.graph_digest != GRAPH.digest:
            return Status.REJECTED_MODEL
        return None


@dataclass(frozen=True)
class AssetStub:
    asset_id: str
    declared_sha256: str
    declared_byte_count: int
    provided_sha256: Optional[str] = None
    provided_byte_count: Optional[int] = None

    def verify(self) -> Status:
        if not _ID.match(self.asset_id) or not _HEX64.match(self.declared_sha256):
            return Status.REJECTED_ASSET_CHANGED
        if self.declared_byte_count < 1:
            return Status.REJECTED_ASSET_CHANGED
        if self.provided_sha256 is None or self.provided_byte_count is None:
            return Status.REJECTED_ASSET_MISSING
        if (self.provided_sha256 != self.declared_sha256
                or self.provided_byte_count != self.declared_byte_count):
            return Status.REJECTED_ASSET_CHANGED
        return Status.OK


@dataclass(frozen=True)
class RuntimeStub:
    runtime_id: str
    hooks: tuple[str, ...]

    def check(self) -> Status:
        if self.runtime_id not in RUNTIME_IDS:
            return Status.REJECTED_RUNTIME
        if set(self.hooks) != set(REQUIRED_HOOKS):
            return Status.REJECTED_HOOK
        return Status.OK


class RuntimeRegistry:
    """Loads only declared model-free stub runtimes."""

    def load(self, runtime_id: str) -> tuple[Status, Optional[RuntimeStub]]:
        if runtime_id not in RUNTIME_IDS:
            return Status.REJECTED_RUNTIME, None
        stub = RuntimeStub(runtime_id, REQUIRED_HOOKS)
        status = stub.check()
        return status, stub if status is Status.OK else None


class ModelRegistry:
    """Rejects reuse of a model ID with different immutable identity."""

    def __init__(self) -> None:
        self._models: dict[str, ModelId] = {}

    def register(self, model: ModelId) -> Status:
        bad = model.check()
        if bad is not None:
            return bad
        existing = self._models.get(model.model_id)
        if existing is not None:
            return Status.OK if existing == model else Status.REJECTED_MODEL
        self._models[model.model_id] = model
        return Status.OK

    def resolve(self, model_id: str) -> Optional[ModelId]:
        return self._models.get(model_id)


@dataclass(frozen=True)
class RunResult:
    status: Status
    samples: tuple[float, ...]
    state: tuple[float, ...]
    entrypoint: str


def _finite(values: Sequence[float]) -> bool:
    try:
        return all(math.isfinite(float(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return False


def tensor_digest(samples: Sequence[float]) -> str:
    return hashlib.sha256(b"".join(struct.pack("<f", float(value))
                                   for value in samples)).hexdigest()


class NeuralRunner:
    """Deterministic stub with separate offline and streaming entry points."""

    def __init__(self, model: ModelId, runtime: RuntimeStub, mode: str,
                 gain: float = 0.5) -> None:
        self.model = model
        self.runtime = runtime
        self.mode = mode
        self.gain = gain
        self.state = (0.0,) * STATE_SAMPLES
        self.closed = False

    @classmethod
    def create(cls, model: ModelId, asset: AssetStub, runtime_id: str,
               mode: str, gain: float = 0.5) -> tuple[Status, Optional["NeuralRunner"]]:
        bad = model.check()
        if bad is not None:
            return bad, None
        asset_status = asset.verify()
        if asset_status is not Status.OK:
            return asset_status, None
        runtime_status, runtime = RuntimeRegistry().load(runtime_id)
        if runtime_status is not Status.OK or runtime is None:
            return runtime_status, None
        if mode not in (STREAMING, OFFLINE) or not math.isfinite(gain) or not 0 < gain <= 1:
            return Status.REJECTED_MODE, None
        return Status.OK, cls(model, runtime, mode, gain)

    def capability_query(self) -> dict[str, Any]:
        return {
            "contract": CONTRACT_ID,
            "model_id": self.model.model_id,
            "runtime_id": self.runtime.runtime_id,
            "mode": self.mode,
            "hooks": list(REQUIRED_HOOKS),
            "tensors": [spec.as_dict() for spec in EXPECTED_TENSORS],
            "state_length": STATE_SAMPLES,
        }

    def run_stream(self, frame: Sequence[float],
                   state: Optional[Sequence[float]] = None) -> RunResult:
        if self.closed:
            return RunResult(Status.CLOSED, (), self.state, STREAMING)
        if self.mode != STREAMING:
            return RunResult(Status.REJECTED_MODE, (), self.state, STREAMING)
        if len(frame) != FRAME_SAMPLES or not _finite(frame):
            return RunResult(Status.REJECTED_TENSOR, (), self.state, STREAMING)
        current = self.state if state is None else tuple(state)
        if len(current) != STATE_SAMPLES or not _finite(current):
            return RunResult(Status.REJECTED_STATE, (), self.state, STREAMING)
        samples = tuple(float(value) * self.gain for value in frame)
        new_state = tuple(float(value) + 1.0 for value in current)
        if not _finite(samples) or not _finite(new_state):
            return RunResult(Status.REJECTED_STATE, (), self.state, STREAMING)
        self.state = new_state
        return RunResult(Status.OK, samples, new_state, STREAMING)

    def run_offline(self, samples: Sequence[float]) -> RunResult:
        if self.closed:
            return RunResult(Status.CLOSED, (), self.state, OFFLINE)
        if self.mode != OFFLINE:
            return RunResult(Status.REJECTED_MODE, (), self.state, OFFLINE)
        if not samples or not _finite(samples):
            return RunResult(Status.REJECTED_TENSOR, (), self.state, OFFLINE)
        output = tuple(float(value) * self.gain for value in samples)
        if not _finite(output):
            return RunResult(Status.REJECTED_STATE, (), self.state, OFFLINE)
        return RunResult(Status.OK, output, self.state, OFFLINE)

    def process_mode(self, frame: Sequence[float], mode: str) -> RunResult:
        if mode != "full":
            if self.closed:
                return RunResult(Status.CLOSED, (), self.state, mode)
            return RunResult(Status.REJECTED_MODE, (), self.state, mode)
        return self.run_stream(frame)

    def resume_prepare(self, retained_state: Sequence[float]) -> tuple[Status, int]:
        if self.closed:
            return Status.CLOSED, 0
        if len(retained_state) != STATE_SAMPLES or not _finite(retained_state):
            return Status.REJECTED_STATE, 0
        return Status.OK, 0

    def close(self) -> None:
        self.closed = True


def canonical_report(runner: NeuralRunner, result: RunResult) -> tuple[str, str]:
    payload = {
        "contract": CONTRACT_ID,
        "model_id": runner.model.model_id,
        "runtime_id": runner.runtime.runtime_id,
        "mode": result.entrypoint,
        "status": result.status.value,
        "output_digest": tensor_digest(result.samples) if result.samples else None,
        "state_digest": tensor_digest(result.state) if result.state else None,
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
