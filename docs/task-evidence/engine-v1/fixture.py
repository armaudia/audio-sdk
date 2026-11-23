"""Model-free reference scheduler for the proposed engine_v1 contract.

This is a deterministic Python model of the versioned proposal in
``contract.json``. It is not an SDK engine plugin, public ABI, provider,
runtime, device result or audio-quality result. Fixed v0 remains 16 kHz mono
f32 with 160-sample frames. Nothing here changes public headers, descriptors,
registry, providers, installed behavior or default processing.

All time is a virtual monotonic integer domain owned by the fixture. No thread,
wall clock, real device, real audio, model or pacing is involved. The scheduler
is single-owner and steps only when the caller asks it to step.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

CONTRACT_ID = "audio-sdk/engine-v1/0.1"
CONTRACT_VERSION = "0.1"
ENGINE = "reference.engine.v1"
ABI_VERSION = "1.0"
STATS_ID = "audio-sdk/engine-v1/stats/0.1"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62500
NS_PER_FRAME = FRAME_SAMPLES * NS_PER_SAMPLE
MAX_NODES = 16
INPUT_CAPACITY = 3
OUTPUT_CAPACITY = 3
FINAL_INPUT = 1
QUIESCE_DRAIN = 0
QUIESCE_CANCEL = 1
SUBMIT_OWNER = "submit.owner.1"
PULL_OWNER = "pull.owner.1"
CONTROL_OWNER = "control.owner.1"
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
_FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
}
_ROOT_KEYS = frozenset(
    ("schema_id", "graph_id", "contract_version", "engine", "format", "audio_path", "nodes")
)
_DOMAIN_KEYS = frozenset((
    "schema_id", "domain_id", "contract_version", "engine", "worker_count", "max_streams",
    "input_frame_capacity", "output_frame_capacity", "max_nodes_per_graph", "max_drain_calls",
    "quiesce_timeout_ms", "policy_digest", "policy", "allowed_provider_ids",
))
_POLICY_KEYS = frozenset((
    "chosen_producer", "chosen_tap", "signal_kind", "calibration_digest", "max_age_samples",
    "auto_transition",
))
_AUDIO_KEYS = frozenset((
    "id", "provider_id", "descriptor_digest", "role", "delay_samples", "settings",
    "depends_on", "input_port", "output_port", "hooks",
))
_ANALYSIS_KEYS = frozenset((
    "id", "provider_id", "descriptor_digest", "role", "delay_samples", "settings",
    "depends_on", "tap_port", "max_age_samples",
))
_HOOK_KEYS = frozenset(("policy_query", "process_mode", "resume_prepare", "process_batch"))
_FORMAT_KEYS = frozenset(("epoch", "first_input_sample", "assets"))
_ASSET_KEYS = frozenset(("id", "sha256", "byte_count"))


class Status(str, Enum):
    OK = "ok"
    NOT_READY = "not_ready"
    END_OF_STREAM = "end_of_stream"
    INVALID_ARGUMENT = "invalid_argument"
    BUSY = "busy"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    NEEDS_RESET = "needs_reset"
    BACKEND_FAILURE = "backend_failure"
    QUIESCE_TIMEOUT = "quiesce_timeout"


class Lifecycle(str, Enum):
    PREPARED = "prepared"
    PROCESSING = "processing"
    DRAINING = "draining"
    DRAINED = "drained"
    NEEDS_RESET = "needs_reset"
    REMOVED = "removed"


class ProviderFailure(Exception):
    """A declared provider hook or lane failed; the engine records it."""

    def __init__(self, reason: str, lane: Optional[str] = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.lane = lane


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Restricted canonical JSON used for identities, stats and reports."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text.encode("ascii")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def descriptor_digest(provider_id: str) -> str:
    """Fixture convention for a provider descriptor identity."""
    return sha256_hex(provider_id.encode("ascii"))


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and abs(float(value)) <= 2 ** 53
    )


def _finite_settings(value: Any) -> bool:
    if isinstance(value, dict):
        return all(isinstance(k, str) and k.isascii() and _finite_settings(v)
                   for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return all(_finite_settings(v) for v in value)
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.isascii()
    return _finite_number(value)


# ---------------------------------------------------------------------------
# Duck-typed provider interface and source-independent test providers.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderOutcome:
    samples: tuple[float, ...]
    events: tuple[dict[str, Any], ...] = ()
    work_ns: int = 0
    validity: str = "known"
    reason: Optional[str] = None
    failure: Optional[str] = None


class Provider:
    """Minimal provider hook shape; third-party fixtures need only duck-type it."""

    role = "audio"

    def __init__(self, provider_id: str, instance_id: str = "fixture.instance") -> None:
        self.provider_id = provider_id
        self.instance_id = instance_id
        self.state: Any = 0.0
        self.version = 0
        self.in_batch = False
        self.lane_states: dict[str, Any] = {}

    def capabilities(self) -> dict[str, Any]:
        return {
            "policy_query": False, "process_mode": False, "resume_prepare": False,
            "process_batch": False, "max_batch": 0,
        }

    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return int(settings.get("delay_samples", 0))

    def work_ns(self, settings: Mapping[str, Any]) -> int:
        return int(settings.get("work_ns", 1_000_000))

    def process(self, samples: Sequence[float], settings: Mapping[str, Any],
                ctx: Mapping[str, Any]) -> ProviderOutcome:
        return ProviderOutcome(tuple(float(x) for x in samples), work_ns=self.work_ns(settings))

    def reset(self) -> None:
        self.state = 0.0
        self.version += 1
        self.in_batch = False
        self.lane_states.clear()

    def state_digest(self) -> str:
        return sha256_hex(f"{self.instance_id}:{self.version}:{self.state!r}".encode("ascii"))

    def policy_query(self) -> dict[str, Any]:
        raise ProviderFailure("hook_unsupported")

    def process_mode(self, samples: Sequence[float], settings: Mapping[str, Any],
                     ctx: Mapping[str, Any], mode: str) -> ProviderOutcome:
        raise ProviderFailure("hook_unsupported")

    def resume_prepare(self, retained_history: Sequence[float],
                       warm_samples: int) -> dict[str, Any]:
        raise ProviderFailure("hook_unsupported")

    def process_batch(self, lanes: Sequence[Mapping[str, Any]]) -> tuple[ProviderOutcome, ...]:
        raise ProviderFailure("hook_unsupported")


class IdentityProvider(Provider):
    pass


class DelayProvider(Provider):
    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return int(settings["delay_samples"])


class GainProvider(Provider):
    def process(self, samples, settings, ctx):
        gain = float(settings["gain"])
        if not math.isfinite(gain):
            raise ProviderFailure("nonfinite_gain")
        return ProviderOutcome(tuple(float(x) * gain for x in samples),
                               work_ns=self.work_ns(settings))


class AnalysisProvider(Provider):
    role = "analysis"

    def process(self, samples, settings, ctx):
        index = int(ctx["frame_index"])
        if index % 2 == 1:
            return ProviderOutcome(tuple(samples), work_ns=self.work_ns(settings))
        value: Optional[float] = None if index % 4 == 2 else float(settings["event_value"])
        event = {
            "producer_id": self.provider_id,
            "tap_id": ctx["tap_port"],
            "stream_id": int(ctx["stream_id"]),
            "epoch": int(ctx["epoch"]),
            "source_start": max(0, int(ctx["source_first"])),
            "source_end": int(ctx["source_first"]) + int(ctx["valid_count_in"]),
            "available_ns": int(ctx["ready_ns"]) + int(settings.get("event_offset_ns", 0)),
            "signal_kind": settings.get("signal_kind", "speech_probability"),
            "value": value,
            "validity": "unknown" if value is None else "known",
            "calibration_digest": settings.get("calibration_digest", descriptor_digest(self.provider_id)),
        }
        return ProviderOutcome(tuple(samples), (event,), work_ns=self.work_ns(settings))


class PublicOnlyProvider(Provider):
    """Provider with no transition or batch hooks; scalar path is always used."""

    def process(self, samples, settings, ctx):
        return ProviderOutcome(tuple(float(x) * float(settings.get("gain", 1.0)) for x in samples),
                               work_ns=self.work_ns(settings))


class TransitionProvider(Provider):
    """Cheap hook performs the same full state update; no performance claim."""

    def capabilities(self):
        return {"policy_query": True, "process_mode": True, "resume_prepare": True,
                "process_batch": False, "max_batch": 0}

    def policy_query(self):
        return {
            "cheap_state_semantics": "full_state_update",
            "history_samples": 0,
            "warm_frames": 0,
            "crossfade_compatible": True,
            "invariant_delay": True,
        }

    def process(self, samples, settings, ctx):
        return self.process_mode(samples, settings, ctx, "full")

    def process_mode(self, samples, settings, ctx, mode):
        if mode not in ("full", "cheap", "observe"):
            raise ProviderFailure("unknown_mode")
        current = float(self.state)
        mean = sum(float(x) for x in samples) / len(samples)
        output = tuple(float(x) + current for x in samples)
        updated = 0.5 * current + mean
        if mode != "observe":
            self.state = updated
        return ProviderOutcome(output, work_ns=self.work_ns(settings))

    def resume_prepare(self, retained_history, warm_samples):
        history = tuple(float(x) for x in retained_history)
        prepared = sha256_hex(canonical_bytes({
            "history": list(history), "state": float(self.state), "warm_samples": int(warm_samples),
        }))
        if not hasattr(self, "_buffer"):
            self._buffer = [0.0] * FRAME_SAMPLES
        return {"prepared_digest": prepared, "warm_frames": int(warm_samples),
                "buffer": self._buffer}


class ResetRequiredProvider(TransitionProvider):
    def policy_query(self):
        return {
            "cheap_state_semantics": "reset_required",
            "history_samples": 0,
            "warm_frames": 0,
            "crossfade_compatible": False,
            "invariant_delay": True,
        }

    def process_mode(self, samples, settings, ctx, mode):
        if mode == "cheap":
            raise ProviderFailure("cheap_requires_reset")
        return super().process_mode(samples, settings, ctx, mode)


class FailingProvider(Provider):
    def process(self, samples, settings, ctx):
        if int(ctx["frame_index"]) == int(settings["fail_at_frame"]):
            raise ProviderFailure(str(settings.get("reason", "control_failure")))
        return ProviderOutcome(tuple(samples), work_ns=self.work_ns(settings))


class BatchProvider(Provider):
    """Two-lane fixture with pre-lane validation and per-lane outcomes."""

    def capabilities(self):
        return {"policy_query": False, "process_mode": False, "resume_prepare": False,
                "process_batch": True, "max_batch": int(self._max_batch)}

    def __init__(self, provider_id: str, instance_id: str = "fixture.batch") -> None:
        super().__init__(provider_id, instance_id)
        self._max_batch = 2

    def process(self, samples, settings, ctx):
        if self.in_batch:
            raise ProviderFailure("concurrent_scalar_call")
        return ProviderOutcome(tuple(samples), work_ns=self.work_ns(settings))

    def process_batch(self, lanes):
        if self.in_batch:
            raise ProviderFailure("concurrent_scalar_call")
        if not 1 <= len(lanes) <= self._max_batch:
            raise ProviderFailure("batch_count")
        state_ids = [str(lane["state_id"]) for lane in lanes]
        if len(set(state_ids)) != len(state_ids):
            raise ProviderFailure("aliased_lane_state")
        configs = {str(lane["config_digest"]) for lane in lanes}
        if len(configs) != 1:
            raise ProviderFailure("incompatible_lane_state")
        if any(bool(lane.get("scalar_in_flight", False)) for lane in lanes):
            raise ProviderFailure("concurrent_scalar_call")
        self.in_batch = True
        outcomes: list[ProviderOutcome] = []
        try:
            for index, lane in enumerate(lanes):
                state_id = state_ids[index]
                gain = float(lane.get("gain", 1.0))
                if not math.isfinite(gain):
                    outcomes.append(ProviderOutcome((), work_ns=0, validity="failed",
                                                    reason="nonfinite_gain", failure="nonfinite_gain"))
                    continue
                if int(lane.get("fail_lane", -1)) == index:
                    reason = str(lane.get("failure_reason", "lane_failure"))
                    outcomes.append(ProviderOutcome((), work_ns=0, validity="failed",
                                                    reason=reason, failure=reason))
                    continue
                state = float(self.lane_states.get(state_id, 0.0))
                samples = tuple(float(x) * gain + state for x in lane["samples"])
                self.lane_states[state_id] = 0.5 * state + (sum(samples) / len(samples))
                validity = "known" if int(lane["valid_count"]) > 0 else "unknown"
                outcomes.append(ProviderOutcome(samples, work_ns=int(lane.get("work_ns", 1_000_000)),
                                                validity=validity))
        finally:
            self.in_batch = False
        return tuple(outcomes)


def builtin_provider_factories() -> dict[str, Callable[[str], Provider]]:
    return {
        "fixture.identity.v0": lambda instance_id: IdentityProvider("fixture.identity.v0", instance_id),
        "fixture.delay.v0": lambda instance_id: DelayProvider("fixture.delay.v0", instance_id),
        "fixture.public.v0": lambda instance_id: PublicOnlyProvider("fixture.public.v0", instance_id),
        "fixture.transition.v0": lambda instance_id: TransitionProvider("fixture.transition.v0", instance_id),
        "fixture.reset_required.v0": lambda instance_id: ResetRequiredProvider(
            "fixture.reset_required.v0", instance_id),
        "fixture.failing.v0": lambda instance_id: FailingProvider("fixture.failing.v0", instance_id),
        "fixture.batch.v0": lambda instance_id: BatchProvider("fixture.batch.v0", instance_id),
        "fixture.gain.v0": lambda instance_id: GainProvider("fixture.gain.v0", instance_id),
        "fixture.activity.v0": lambda instance_id: AnalysisProvider("fixture.activity.v0", instance_id),
        "third_party.gain.v0": lambda instance_id: GainProvider("third_party.gain.v0", instance_id),
        "third_party.transition.v0": lambda instance_id: TransitionProvider(
            "third_party.transition.v0", instance_id),
        "third_party.activity.v0": lambda instance_id: AnalysisProvider(
            "third_party.activity.v0", instance_id),
    }


# ---------------------------------------------------------------------------
# Validated config, graph and value objects.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Graph:
    raw: dict[str, Any]
    digest: str
    audio_nodes: tuple[dict[str, Any], ...]
    analysis_nodes: tuple[dict[str, Any], ...]
    nodes_by_id: dict[str, dict[str, Any]]
    total_delay: int
    total_work_ns: int
    max_drain_calls: int


@dataclass(frozen=True)
class DomainConfig:
    raw: dict[str, Any]
    digest: str
    domain_id: str
    max_streams: int
    input_capacity: int
    output_capacity: int
    max_nodes: int
    max_drain_calls: int
    quiesce_timeout_ms: int
    policy: dict[str, Any]
    allowed: frozenset[str]


@dataclass(frozen=True)
class Frame:
    samples: tuple[float, ...]
    valid_count: int
    epoch: int
    first_sample: int
    flags: int = 0


@dataclass(frozen=True)
class Acceptance:
    status: Status
    accepted_samples: int = 0
    consumed_count: int = 0
    sequence: Optional[int] = None
    reason: str = ""


@dataclass(frozen=True)
class QueuedFrame:
    sequence: int
    frame: Frame
    capture_first_ns: int
    deadline_ns: int


@dataclass(frozen=True)
class OutputFrame:
    sequence: int
    epoch: int
    samples: tuple[float, ...]
    source_first_sample: int
    valid_offset: int
    valid_count: int
    ready_ns: int
    capture_first_ns: int
    deadline_ns: int
    deadline_miss: bool
    events: tuple[dict[str, Any], ...]
    drain: bool = False
    validity: str = "known"
    reason: str = ""


@dataclass(frozen=True)
class Lease:
    lease_id: str
    domain_id: str
    stream_id: int
    sequence: int
    epoch: int
    samples: tuple[float, ...]
    source_first_sample: int
    valid_offset: int
    valid_count: int
    available_ready_ns: int
    deadline_miss: bool
    events: tuple[dict[str, Any], ...]
    drain: bool = False
    validity: str = "known"
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id, "domain_id": self.domain_id,
            "stream_id": self.stream_id, "sequence": self.sequence,
            "epoch": self.epoch,
            "source_first_sample": str(self.source_first_sample),
            "valid_offset": str(self.valid_offset), "valid_count": str(self.valid_count),
            "available_ready_ns": str(self.available_ready_ns),
            "deadline_miss": self.deadline_miss, "drain": self.drain,
            "validity": self.validity, "reason": self.reason,
            "events": [dict(event) for event in self.events],
        }


@dataclass(frozen=True)
class PullResult:
    status: Status
    lease: Optional[Lease] = None
    reason: str = ""


@dataclass(frozen=True)
class CancellationRecord:
    stream_id: int
    epoch: int
    reason: str
    queued_sequences: tuple[int, ...]
    in_flight_sequence: Optional[int]
    abandoned_start: int
    abandoned_end: int
    abandoned_samples: int
    discarded_output: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id, "epoch": self.epoch, "reason": self.reason,
            "queued_sequences": list(self.queued_sequences),
            "in_flight_sequence": self.in_flight_sequence,
            "abandoned_start": str(self.abandoned_start),
            "abandoned_end": str(self.abandoned_end),
            "abandoned_samples": str(self.abandoned_samples),
            "discarded_output": self.discarded_output,
        }


@dataclass(frozen=True)
class FailureRecord:
    stream_id: int
    epoch: int
    lane: str
    reason: str
    sequence: Optional[int]
    start: int
    end: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id, "epoch": self.epoch, "lane": self.lane,
            "reason": self.reason, "sequence": self.sequence,
            "start": str(self.start), "end": str(self.end),
        }


@dataclass(frozen=True)
class BatchResult:
    lane_id: str
    stream_id: int
    status: Status
    validity: str
    source_first_sample: int
    valid_offset: int
    valid_count: int
    available_ready_ns: int
    deadline_miss: bool
    samples_digest: str
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id, "stream_id": self.stream_id,
            "status": self.status.value, "validity": self.validity,
            "source_first_sample": str(self.source_first_sample),
            "valid_offset": str(self.valid_offset), "valid_count": str(self.valid_count),
            "available_ready_ns": str(self.available_ready_ns),
            "deadline_miss": self.deadline_miss,
            "samples_digest": self.samples_digest, "reason": self.reason,
        }


@dataclass(frozen=True)
class EventRecord:
    status: str
    reason: str
    event: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reason": self.reason, "event": dict(self.event)}


def validate_domain(raw: Any) -> tuple[Optional[DomainConfig], Status, str]:
    if not isinstance(raw, dict) or set(raw) != _DOMAIN_KEYS:
        return None, Status.INVALID_ARGUMENT, "domain_keys"
    if (raw["schema_id"] != "audio-sdk/engine-v1/domain/0.1"
            or raw["contract_version"] != CONTRACT_VERSION
            or raw["engine"] != ENGINE):
        return None, Status.INVALID_ARGUMENT, "domain_version"
    config = DomainConfig(
        raw=json.loads(json.dumps(raw, sort_keys=True, allow_nan=False)),
        digest=sha256_hex(canonical_bytes(raw)),
        domain_id=raw["domain_id"],
        max_streams=raw["max_streams"],
        input_capacity=raw["input_frame_capacity"],
        output_capacity=raw["output_frame_capacity"],
        max_nodes=raw["max_nodes_per_graph"],
        max_drain_calls=raw["max_drain_calls"],
        quiesce_timeout_ms=raw["quiesce_timeout_ms"],
        policy=dict(raw["policy"]),
        allowed=frozenset(raw["allowed_provider_ids"]),
    )
    if not isinstance(config.domain_id, str) or not _ID.match(config.domain_id):
        return None, Status.INVALID_ARGUMENT, "domain_id"
    if config.max_streams != 2:  # fixture config freezes this value; one owner, two streams
        return None, Status.INVALID_ARGUMENT, "max_streams"
    if (config.input_capacity != INPUT_CAPACITY or config.output_capacity != OUTPUT_CAPACITY
            or config.max_nodes != MAX_NODES or config.max_drain_calls < 1
            or config.max_drain_calls > 1024 or config.quiesce_timeout_ms <= 0):
        return None, Status.INVALID_ARGUMENT, "bounds"
    if raw["worker_count"] != 1:
        return None, Status.INVALID_ARGUMENT, "single_scheduler_owner"
    if set(config.policy) != _POLICY_KEYS or not _finite_settings(config.policy):
        return None, Status.INVALID_ARGUMENT, "policy_shape"
    if sha256_hex(canonical_bytes(config.policy)) != raw["policy_digest"]:
        return None, Status.INVALID_ARGUMENT, "policy_digest"
    if config.policy["auto_transition"] not in ("off", "proven"):
        return None, Status.INVALID_ARGUMENT, "auto_transition"
    if not isinstance(raw["allowed_provider_ids"], list) or not raw["allowed_provider_ids"]:
        return None, Status.INVALID_ARGUMENT, "allowed_providers"
    if any(not isinstance(item, str) or not _ID.match(item) for item in raw["allowed_provider_ids"]):
        return None, Status.INVALID_ARGUMENT, "allowed_providers"
    return config, Status.OK, ""


def validate_graph(raw: Any, config: DomainConfig,
                   factories: Mapping[str, Callable[[str], Any]]
                   ) -> tuple[Optional[Graph], Status, str]:
    """Validate the control-plane graph before any stream state is allocated."""
    if not isinstance(raw, dict) or set(raw) != _ROOT_KEYS:
        return None, Status.INVALID_ARGUMENT, "graph_keys"
    if (raw["schema_id"] != CONTRACT_ID or raw["contract_version"] != CONTRACT_VERSION
            or raw["engine"] != ENGINE or raw["format"] != _FORMAT):
        return None, Status.INVALID_ARGUMENT, "graph_version_or_format"
    if not isinstance(raw["graph_id"], str) or not _ID.match(raw["graph_id"]):
        return None, Status.INVALID_ARGUMENT, "graph_id"
    nodes = raw["nodes"]
    path = raw["audio_path"]
    if not isinstance(nodes, list) or not isinstance(path, list):
        return None, Status.INVALID_ARGUMENT, "graph_lists"
    if not 1 <= len(nodes) <= config.max_nodes or not 1 <= len(path) <= config.max_nodes:
        return None, Status.INVALID_ARGUMENT, "node_count"

    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            return None, Status.INVALID_ARGUMENT, "node_shape"
        role = node.get("role")
        expected = _AUDIO_KEYS if role == "audio" else _ANALYSIS_KEYS if role == "analysis" else frozenset()
        if not expected or set(node) != expected:
            return None, Status.INVALID_ARGUMENT, "node_keys"
        node_id, provider_id = node["id"], node["provider_id"]
        if (not isinstance(node_id, str) or not _ID.match(node_id)
                or not isinstance(provider_id, str) or not _ID.match(provider_id)):
            return None, Status.INVALID_ARGUMENT, "node_id"
        if node_id in by_id:
            return None, Status.INVALID_ARGUMENT, "duplicate_node_id"
        by_id[node_id] = node
        if provider_id not in config.allowed:
            return None, Status.INVALID_ARGUMENT, "provider_not_allowed"
        if node["descriptor_digest"] != descriptor_digest(provider_id):
            return None, Status.INVALID_ARGUMENT, "descriptor_digest"
        if (not isinstance(node["delay_samples"], int) or isinstance(node["delay_samples"], bool)
                or not 0 <= node["delay_samples"] <= 16000):
            return None, Status.INVALID_ARGUMENT, "delay_range"
        if not isinstance(node["settings"], dict) or not _finite_settings(node["settings"]):
            return None, Status.INVALID_ARGUMENT, "settings"
        if (not isinstance(node["depends_on"], list) or len(node["depends_on"]) > config.max_nodes
                or any(not isinstance(item, str) or item not in by_id for item in node["depends_on"])):
            return None, Status.INVALID_ARGUMENT, "depends_on"
        if role == "audio":
            hooks = node["hooks"]
            if (not isinstance(hooks, dict) or set(hooks) != _HOOK_KEYS
                    or any(not isinstance(value, bool) for value in hooks.values())):
                return None, Status.INVALID_ARGUMENT, "hooks_shape"
            ports = (node["input_port"], node["output_port"])
            if any(not isinstance(port, str) or not _ID.match(port) for port in ports):
                return None, Status.INVALID_ARGUMENT, "port_id"
            if int(node["settings"].get("max_batch", 0)) not in (0, 2, 4):
                return None, Status.INVALID_ARGUMENT, "max_batch"
        else:
            if (not isinstance(node["tap_port"], str)
                    or not isinstance(node["max_age_samples"], int)
                    or isinstance(node["max_age_samples"], bool)
                    or not 0 <= node["max_age_samples"] <= 16000):
                return None, Status.INVALID_ARGUMENT, "tap_shape"

    audio_nodes = [by_id.get(node_id) for node_id in path]
    if any(node is None for node in audio_nodes) or any(node["role"] != "audio" for node in audio_nodes):
        return None, Status.INVALID_ARGUMENT, "audio_path"
    audio_nodes = [node for node in audio_nodes if node is not None]
    audio_ids = {node["id"] for node in audio_nodes}
    if audio_ids != {node["id"] for node in nodes if node["role"] == "audio"}:
        return None, Status.INVALID_ARGUMENT, "audio_path_coverage"
    inputs = [node["input_port"] for node in audio_nodes]
    outputs = [node["output_port"] for node in audio_nodes]
    if len(set(inputs)) != len(inputs) or len(set(outputs)) != len(outputs):
        return None, Status.INVALID_ARGUMENT, "duplicate_port"
    for index, node in enumerate(audio_nodes):
        expected = "pcm.in" if index == 0 else audio_nodes[index - 1]["output_port"]
        if node["input_port"] != expected:
            return None, Status.INVALID_ARGUMENT, "ambiguous_port"
        expected_deps = [] if index == 0 else [audio_nodes[index - 1]["id"]]
        if node["depends_on"] != expected_deps:
            return None, Status.INVALID_ARGUMENT, "audio_fan_in"

    analysis_nodes = [node for node in nodes if node["role"] == "analysis"]
    producing = {node["output_port"]: node["id"] for node in audio_nodes}
    for node in analysis_nodes:
        tap = node["tap_port"]
        if tap not in producing or set(node["depends_on"]) != {producing[tap]}:
            return None, Status.INVALID_ARGUMENT, "unknown_or_undeclared_tap"

    edges: dict[str, list[str]] = {node_id: list(node["depends_on"]) for node_id, node in by_id.items()}
    for node in analysis_nodes:
        edges[node["id"]].append(producing[node["tap_port"]])
    color: dict[str, int] = {}

    def visit(node_id: str) -> bool:
        if color.get(node_id) == 1:
            return True
        if color.get(node_id) == 2:
            return False
        color[node_id] = 1
        if any(child not in by_id or visit(child) for child in edges[node_id]):
            return True
        color[node_id] = 2
        return False

    if any(visit(node_id) for node_id in by_id):
        return None, Status.INVALID_ARGUMENT, "cycle"

    for node in nodes:
        factory = factories.get(node["provider_id"])
        if factory is None:
            return None, Status.INVALID_ARGUMENT, "provider_unavailable"
        probe = factory("validate.probe")
        if getattr(probe, "role", "audio") != node["role"]:
            return None, Status.INVALID_ARGUMENT, "provider_role"
        if int(probe.delay_samples(node["settings"])) != node["delay_samples"]:
            return None, Status.INVALID_ARGUMENT, "delay_mismatch"
        capabilities = probe.capabilities()
        if node["role"] == "audio":
            for hook in _HOOK_KEYS:
                if bool(capabilities.get(hook, False)) != bool(node["hooks"][hook]):
                    return None, Status.INVALID_ARGUMENT, f"hook_mismatch:{hook}"
            if capabilities.get("process_batch") and int(capabilities.get("max_batch", 0)) not in (2, 4):
                return None, Status.INVALID_ARGUMENT, "batch_capability"
        if node["role"] == "analysis" and node["settings"].get("signal_kind", "speech_probability") != "speech_probability":
            return None, Status.INVALID_ARGUMENT, "unknown_signal"

    graph = Graph(
        raw=json.loads(json.dumps(raw, sort_keys=True, allow_nan=False)),
        digest=sha256_hex(canonical_bytes(raw)),
        audio_nodes=tuple(audio_nodes),
        analysis_nodes=tuple(analysis_nodes),
        nodes_by_id=by_id,
        total_delay=sum(int(node["delay_samples"]) for node in audio_nodes),
        total_work_ns=sum(int(node["settings"].get("work_ns", 1_000_000)) for node in nodes),
        max_drain_calls=config.max_drain_calls,
    )
    return graph, Status.OK, ""


def validate_format(raw: Any) -> tuple[Optional[int], Optional[int], tuple[str, ...], Status, str]:
    if not isinstance(raw, dict) or set(raw) != _FORMAT_KEYS:
        return None, None, (), Status.INVALID_ARGUMENT, "format_keys"
    epoch = raw["epoch"]
    first = raw["first_input_sample"]
    assets = raw["assets"]
    if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1
            or not isinstance(first, int) or isinstance(first, bool) or first < 0):
        return None, None, (), Status.INVALID_ARGUMENT, "epoch_or_first"
    if not isinstance(assets, list) or len(assets) > 16:
        return None, None, (), Status.INVALID_ARGUMENT, "assets"
    ids: list[str] = []
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != _ASSET_KEYS:
            return None, None, (), Status.INVALID_ARGUMENT, "asset_keys"
        if (not isinstance(asset["id"], str) or not _ID.match(asset["id"])
                or not isinstance(asset["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", asset["sha256"])
                or not isinstance(asset["byte_count"], int) or asset["byte_count"] < 0):
            return None, None, (), Status.INVALID_ARGUMENT, "asset_shape"
        ids.append(asset["id"])
    if len(set(ids)) != len(ids):
        return None, None, (), Status.INVALID_ARGUMENT, "duplicate_asset"
    return epoch, first, tuple(ids), Status.OK, ""


# ---------------------------------------------------------------------------
# Deterministic single-owner scheduler, streams and domain.
# ---------------------------------------------------------------------------

class Clock:
    def __init__(self, origin_ns: int = 1_000_000_000) -> None:
        self.origin_ns = origin_ns
        self.now_ns = origin_ns

    def advance(self, amount_ns: int) -> int:
        if amount_ns < 0:
            raise ValueError("negative_clock_advance")
        self.now_ns += amount_ns
        return self.now_ns


class Stream:
    def __init__(self, domain: "Domain", stream_id: int, graph: Graph,
                 epoch: int, first_sample: int, assets: tuple[str, ...],
                 providers: dict[str, Any]) -> None:
        self.domain = domain
        self.stream_id = stream_id
        self.graph = graph
        self.epoch = epoch
        self.first_sample = first_sample
        self.assets = assets
        self.providers = providers
        self.instance_ids = {node_id: provider.instance_id for node_id, provider in providers.items()}
        self.scheduler_id = domain.scheduler.owner
        self.lifecycle = Lifecycle.PREPARED
        self.input_queue: list[QueuedFrame] = []
        self.output_queue: list[OutputFrame] = []
        self.active_lease: Optional[Lease] = None
        self.delivered_leases: list[Lease] = []
        self.produced_samples_list: list[float] = []
        self.accepted_end = first_sample
        self.next_input_sample = first_sample
        self.delivered_end = first_sample
        self.end_input_closed = False
        self.accepted_source_end: Optional[int] = None
        self.drain_complete = False
        self.drain_calls = 0
        self.cancelled: Optional[str] = None
        self.cancel_requested = False
        self.in_flight_sequence: Optional[int] = None
        self.cancellations: list[CancellationRecord] = []
        self.failures: list[FailureRecord] = []
        self.deadline_misses: list[dict[str, Any]] = []
        self.analysis_records: list[EventRecord] = []
        self.last_analysis_ns: Optional[int] = None
        self.mode = "full"
        self.sequence_ids: list[int] = []
        self.counters: dict[str, int] = {
            "submitted_frames": 0, "accepted_samples": 0, "produced_frames": 0,
            "produced_samples": 0, "delivered_valid_samples": 0, "lease_acquires": 0,
            "lease_releases": 0, "bad_lease_releases": 0, "rejected_frames": 0,
            "discarded_frames": 0, "cancelled_samples": 0, "deadline_misses": 0,
            "failed_lanes": 0, "analysis_accepted": 0, "analysis_rejected": 0,
            "input_high_water": 0, "output_high_water": 0, "quiesce_timeouts": 0,
            "batch_lanes": 0, "transition_cheap_calls": 0, "transition_observe_calls": 0,
        }
        self.admitted = True

    def _state_ok(self) -> Optional[Status]:
        if not self.admitted or self.lifecycle is Lifecycle.REMOVED:
            return Status.INVALID_ARGUMENT
        if self.lifecycle is Lifecycle.NEEDS_RESET or self.domain.admission_closed:
            return Status.NEEDS_RESET
        return None

    def enqueue(self, frame: Frame, capture_first_ns: int, deadline_ns: int,
                owner: str = SUBMIT_OWNER) -> Acceptance:
        if owner != SUBMIT_OWNER:
            return Acceptance(Status.INVALID_ARGUMENT, reason="wrong_submit_owner")
        blocked = self._state_ok()
        if blocked is not None:
            return Acceptance(blocked, reason=blocked.value)
        if self.scheduler_id != self.domain.scheduler.owner:
            return Acceptance(Status.INVALID_ARGUMENT, reason="scheduler_ownership")
        if self.end_input_closed:
            return Acceptance(Status.INVALID_ARGUMENT, reason="input_closed")
        if len(self.input_queue) >= self.domain.config.input_capacity:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.RESOURCE_EXHAUSTED, reason="input_queue_full")
        if frame.epoch != self.epoch:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="stale_epoch")
        if frame.first_sample != self.next_input_sample:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="first_sample")
        if len(frame.samples) != FRAME_SAMPLES or not 0 <= frame.valid_count <= FRAME_SAMPLES:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="counts")
        if frame.flags & ~FINAL_INPUT:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="flags")
        if any(not math.isfinite(float(x)) for x in frame.samples[:frame.valid_count]):
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="nonfinite_input")
        if any(float(x) != 0.0 for x in frame.samples[frame.valid_count:]):
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="nonzero_padding")
        if frame.valid_count == 0 and not frame.flags & FINAL_INPUT:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="empty_not_final")
        if deadline_ns < capture_first_ns:
            self.counters["rejected_frames"] += 1
            return Acceptance(Status.INVALID_ARGUMENT, reason="deadline_before_capture")
        copied = Frame(tuple(float(x) for x in frame.samples), frame.valid_count,
                       frame.epoch, frame.first_sample, frame.flags)
        sequence = self.domain.scheduler.next_sequence()
        self.input_queue.append(QueuedFrame(sequence, copied, capture_first_ns, deadline_ns))
        self.sequence_ids.append(sequence)
        self.domain.scheduler.enqueue_job(sequence, self.stream_id)
        self.counters["submitted_frames"] += 1
        self.counters["accepted_samples"] += frame.valid_count
        self.counters["input_high_water"] = max(self.counters["input_high_water"], len(self.input_queue))
        self.accepted_end = frame.first_sample + frame.valid_count
        self.next_input_sample = frame.first_sample + FRAME_SAMPLES
        if frame.flags & FINAL_INPUT:
            self.end_input_closed = True
            self.accepted_source_end = self.accepted_end
            self.lifecycle = Lifecycle.DRAINING
        elif self.lifecycle is Lifecycle.PREPARED:
            self.lifecycle = Lifecycle.PROCESSING
        return Acceptance(Status.OK, frame.valid_count, FRAME_SAMPLES, sequence)

    def pull(self, owner: str = PULL_OWNER) -> PullResult:
        if owner != PULL_OWNER:
            return PullResult(Status.INVALID_ARGUMENT, reason="wrong_pull_owner")
        if self.active_lease is not None:
            return PullResult(Status.BUSY, reason="lease_outstanding")
        blocked = self._state_ok()
        if blocked is not None:
            return PullResult(blocked, reason=blocked.value)
        if self.output_queue:
            output = self.output_queue.pop(0)
            lease = Lease(
                lease_id=f"L{self.stream_id}-{output.sequence}",
                domain_id=self.domain.config.domain_id, stream_id=self.stream_id,
                sequence=output.sequence, epoch=output.epoch, samples=output.samples,
                source_first_sample=output.source_first_sample,
                valid_offset=output.valid_offset, valid_count=output.valid_count,
                available_ready_ns=output.ready_ns, deadline_miss=output.deadline_miss,
                events=output.events, drain=output.drain, validity=output.validity,
                reason=output.reason,
            )
            self.active_lease = lease
            self.counters["lease_acquires"] += 1
            return PullResult(Status.OK, lease)
        pending = (self.domain.scheduler.pending_for(self.stream_id)
                   or self.domain.scheduler.in_flight_stream() == self.stream_id
                   or bool(self.input_queue))
        if self.drain_complete and not pending:
            return PullResult(Status.END_OF_STREAM)
        return PullResult(Status.NOT_READY)

    def release(self, lease_id: str) -> Status:
        lease = self.active_lease
        if lease is None or lease.lease_id != lease_id:
            self.counters["bad_lease_releases"] += 1
            return Status.INVALID_ARGUMENT
        self.counters["lease_releases"] += 1
        self.counters["delivered_valid_samples"] += lease.valid_count
        self.delivered_leases.append(lease)
        end = lease.source_first_sample + lease.valid_offset + lease.valid_count
        self.delivered_end = max(self.delivered_end, end)
        self.active_lease = None
        return Status.OK

    @property
    def produced_frames(self) -> int:
        return self.counters["produced_frames"]

    def produced_samples(self) -> tuple[float, ...]:
        return tuple(self.produced_samples_list)

    def output_digest(self) -> str:
        import struct
        packed = b"".join(struct.pack("<f", float(x)) for x in self.produced_samples_list)
        return sha256_hex(packed)

    def end_input(self, accepted_source_end: int, owner: str = SUBMIT_OWNER) -> Status:
        if owner != SUBMIT_OWNER:
            return Status.INVALID_ARGUMENT
        blocked = self._state_ok()
        if blocked is not None:
            return blocked
        if self.end_input_closed:
            return Status.OK if self.accepted_source_end == accepted_source_end else Status.INVALID_ARGUMENT
        if (not isinstance(accepted_source_end, int) or isinstance(accepted_source_end, bool)
                or accepted_source_end < self.first_sample or accepted_source_end > self.accepted_end):
            return Status.INVALID_ARGUMENT
        self.end_input_closed = True
        self.accepted_source_end = accepted_source_end
        self.lifecycle = Lifecycle.DRAINING
        return Status.OK

    def set_mode(self, mode: str, owner: str = CONTROL_OWNER) -> Status:
        if owner != CONTROL_OWNER:
            return Status.INVALID_ARGUMENT
        if mode not in ("full", "cheap", "observe"):
            return Status.INVALID_ARGUMENT
        if mode == "full":
            self.mode = mode
            return Status.OK
        for node in self.graph.audio_nodes:
            provider = self.providers[node["id"]]
            if not bool(node["hooks"]["process_mode"]) or not bool(provider.capabilities().get("process_mode")):
                return Status.INVALID_ARGUMENT
            if mode == "cheap":
                bounds = provider.policy_query()
                if bounds.get("cheap_state_semantics") != "full_state_update":
                    return Status.INVALID_ARGUMENT
                if bounds.get("history_samples", 1) != 0 or bounds.get("warm_frames", 1) != 0:
                    return Status.INVALID_ARGUMENT
                if not bool(bounds.get("invariant_delay", False)):
                    return Status.INVALID_ARGUMENT
        self.mode = mode
        return Status.OK

    def resume_prepare(self, node_id: str, retained_history: Sequence[float],
                       warm_samples: int) -> dict[str, Any]:
        node = self.graph.nodes_by_id.get(node_id)
        if node is None or not bool(node.get("hooks", {}).get("resume_prepare")):
            raise ProviderFailure("hook_unsupported")
        return self.providers[node_id].resume_prepare(retained_history, warm_samples)

    def submit_analysis(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        policy = self.domain.config.policy
        expected_keys = frozenset((
            "producer_id", "tap_id", "stream_id", "epoch", "source_start", "source_end",
            "available_ns", "signal_kind", "value", "validity", "calibration_digest",
        ))
        if not isinstance(raw, dict) or set(raw) != expected_keys:
            status = "rejected_bad_analysis_shape"
        elif (raw["producer_id"] != policy["chosen_producer"]
              or raw["tap_id"] != policy["chosen_tap"]
              or raw["signal_kind"] != policy["signal_kind"]
              or raw["calibration_digest"] != policy["calibration_digest"]):
            status = "rejected_unselected_source"
        elif int(raw["stream_id"]) != self.stream_id or int(raw["epoch"]) != self.epoch:
            status = "rejected_stale_analysis"
        elif not (self.first_sample <= int(raw["source_start"]) < int(raw["source_end"])
                  <= self.accepted_end):
            status = "rejected_out_of_range_analysis"
        elif self.accepted_end - int(raw["source_end"]) > int(policy["max_age_samples"]):
            status = "rejected_stale_analysis"
        elif not isinstance(raw["available_ns"], int) or (
                self.last_analysis_ns is not None and int(raw["available_ns"]) <= self.last_analysis_ns):
            status = "rejected_bad_analysis_clock"
        elif raw["validity"] == "known" and (
                not _finite_number(raw["value"]) or not 0.0 <= float(raw["value"]) <= 1.0):
            status = "rejected_invalid_analysis"
        elif raw["validity"] == "unknown" and raw["value"] is not None:
            status = "rejected_invalid_analysis"
        elif raw["validity"] not in ("known", "unknown"):
            status = "rejected_invalid_analysis"
        else:
            status = "ok"
        if status == "ok":
            self.counters["analysis_accepted"] += 1
            self.last_analysis_ns = int(raw["available_ns"])
        else:
            self.counters["analysis_rejected"] += 1
        self.analysis_records.append(EventRecord(status, "" if status == "ok" else status, dict(raw)))
        out = dict(raw)
        out["status"] = status
        return out

    def quiesce(self, policy: int, owner: str = CONTROL_OWNER) -> tuple[Status, str]:
        if owner != CONTROL_OWNER:
            return Status.INVALID_ARGUMENT, "control_thread_only"
        blocked = self._state_ok()
        if blocked is not None:
            return blocked, blocked.value
        if self.active_lease is not None:
            return Status.BUSY, "lease_outstanding"
        if policy == QUIESCE_CANCEL:
            self.cancel_requested = True
            self.cancelled = "quiesce_cancel"
            if self.domain.scheduler.in_flight_stream() == self.stream_id:
                self.domain.counters["quiesce_barrier_waits"] += 1
            self._discard_queued("quiesce_cancel")
            self.lifecycle = Lifecycle.DRAINED
            return Status.OK, ""
        if policy != QUIESCE_DRAIN:
            return Status.INVALID_ARGUMENT, "policy"
        deadline_ns = self.domain.clock.now_ns + self.domain.config.quiesce_timeout_ms * 1_000_000
        while self.domain.clock.now_ns <= deadline_ns:
            if self.drain_complete and not self.domain.scheduler.pending_for(self.stream_id):
                return Status.OK, ""
            before = self.domain.clock.now_ns
            self.domain.scheduler.step(pull_callback=self.domain.pull_and_release)
            if self.drain_complete and not self.domain.scheduler.pending_for(self.stream_id):
                return Status.OK, ""
            if self.domain.clock.now_ns == before:
                break
        self.counters["quiesce_timeouts"] += 1
        return Status.QUIESCE_TIMEOUT, "quiesce_timeout"

    def _discard_queued(self, reason: str) -> None:
        sequences = tuple(item.sequence for item in self.input_queue)
        self.domain.scheduler.drop_stream(self.stream_id, sequences)
        self.input_queue.clear()
        start = self.delivered_end
        end = self.accepted_end
        record = CancellationRecord(
            stream_id=self.stream_id, epoch=self.epoch, reason=reason,
            queued_sequences=sequences,
            in_flight_sequence=self.domain.scheduler.in_flight_sequence_for(self.stream_id),
            abandoned_start=start, abandoned_end=end,
            abandoned_samples=max(0, end - start), discarded_output=False,
        )
        self.cancellations.append(record)
        self.counters["cancelled_samples"] += record.abandoned_samples
        self.domain.counters["cancelled_intervals"] += 1
        self.domain.counters["cancelled_samples"] += record.abandoned_samples

    def reset(self, new_epoch: int, first_sample: int,
              owner: str = CONTROL_OWNER) -> Status:
        if owner != CONTROL_OWNER:
            return Status.INVALID_ARGUMENT
        if self.active_lease is not None:
            return Status.BUSY
        if self.lifecycle not in (Lifecycle.DRAINED, Lifecycle.NEEDS_RESET):
            return Status.BUSY
        if (not isinstance(new_epoch, int) or isinstance(new_epoch, bool)
                or not isinstance(first_sample, int) or isinstance(first_sample, bool)):
            return Status.INVALID_ARGUMENT
        if new_epoch <= self.epoch or first_sample < 0:
            return Status.INVALID_ARGUMENT
        if (self.domain.scheduler.pending_for(self.stream_id)
                or self.domain.scheduler.in_flight_stream() == self.stream_id
                or self.input_queue):
            return Status.BUSY
        if self.delivered_end < self.accepted_end:
            self._discard_queued("reset")
        for node_id, provider in self.providers.items():
            provider.reset()
        self.domain.counters["epoch_transitions"].append({
            "stream_id": self.stream_id, "from": self.epoch, "to": new_epoch,
            "cancelled": self.cancelled,
        })
        self.epoch = new_epoch
        self.first_sample = first_sample
        self.accepted_end = first_sample
        self.next_input_sample = first_sample
        self.delivered_end = first_sample
        self.end_input_closed = False
        self.accepted_source_end = None
        self.drain_complete = False
        self.drain_calls = 0
        self.cancelled = None
        self.cancel_requested = False
        self.output_queue.clear()
        self.produced_samples_list.clear()
        self.delivered_leases.clear()
        self.analysis_records.clear()
        self.last_analysis_ns = None
        self.deadline_misses.clear()
        self.mode = "full"
        self.lifecycle = Lifecycle.PREPARED
        for key in ("submitted_frames", "accepted_samples", "produced_frames", "produced_samples",
                    "delivered_valid_samples", "lease_acquires", "lease_releases",
                    "bad_lease_releases", "rejected_frames", "discarded_frames",
                    "cancelled_samples", "deadline_misses", "failed_lanes", "analysis_accepted",
                    "analysis_rejected", "input_high_water", "output_high_water",
                    "quiesce_timeouts", "batch_lanes", "transition_cheap_calls",
                    "transition_observe_calls"):
            self.counters[key] = 0
        return Status.OK

    def remove(self, owner: str = CONTROL_OWNER) -> Status:
        if owner != CONTROL_OWNER:
            return Status.INVALID_ARGUMENT
        if self.active_lease is not None:
            return Status.BUSY
        if (self.domain.scheduler.pending_for(self.stream_id)
                or self.domain.scheduler.in_flight_stream() == self.stream_id):
            return Status.BUSY
        self._discard_queued("remove")
        self.providers.clear()
        self.admitted = False
        self.lifecycle = Lifecycle.REMOVED
        self.domain.drop_stream(self.stream_id)
        return Status.OK


class Scheduler:
    """The only scheduler in the domain; all streams are serviced in FIFO order."""

    def __init__(self, domain: "Domain", owner: str = "scheduler.1") -> None:
        self.domain = domain
        self.owner = owner
        self.sequence = 0
        self.ready: list[tuple[int, int]] = []
        self._in_flight: Optional[dict[str, Any]] = None
        self.steps = 0

    def next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def enqueue_job(self, sequence: int, stream_id: int) -> None:
        self.ready.append((sequence, stream_id))

    def drop_stream(self, stream_id: int, sequences: Iterable[int] = ()) -> None:
        doomed = set(sequences)
        self.ready = [item for item in self.ready
                      if item[1] != stream_id and item[0] not in doomed]

    def pending_for(self, stream_id: int) -> int:
        return sum(1 for _, sid in self.ready if sid == stream_id)

    def in_flight_stream(self) -> Optional[int]:
        return self._in_flight["stream_id"] if self._in_flight else None

    def in_flight_sequence_for(self, stream_id: int) -> Optional[int]:
        if self._in_flight and self._in_flight["stream_id"] == stream_id:
            return self._in_flight["sequence"]
        return None

    def begin_step(self) -> Optional[QueuedFrame]:
        if self._in_flight is not None:
            return None
        for index, (sequence, stream_id) in enumerate(self.ready):
            stream = self.domain.streams.get(stream_id)
            if (stream is None or len(stream.output_queue) >= self.domain.config.output_capacity
                    or stream.lifecycle in (Lifecycle.NEEDS_RESET, Lifecycle.REMOVED)):
                continue
            if not stream.input_queue or stream.input_queue[0].sequence != sequence:
                continue
            self.ready.pop(index)
            item = stream.input_queue[0]
            self._in_flight = {
                "stream_id": stream_id, "sequence": sequence, "epoch": stream.epoch,
                "frame": item,
            }
            stream.in_flight_sequence = sequence
            return item
        return None

    def finish_step(self) -> Status:
        job = self._in_flight
        if job is None:
            return Status.NOT_READY
        stream = self.domain.streams[job["stream_id"]]
        item: QueuedFrame = job["frame"]
        self._in_flight = None
        stream.in_flight_sequence = None
        self.steps += 1
        if stream.input_queue and stream.input_queue[0].sequence == item.sequence:
            stream.input_queue.pop(0)
        else:
            stream.input_queue = [q for q in stream.input_queue if q.sequence != item.sequence]
        if (stream.cancel_requested or stream.cancelled
                or job["epoch"] != stream.epoch or not stream.admitted):
            self._discard_in_flight(stream, item)
            return Status.OK
        status = self._process_frame(stream, item, drain=False)
        self._maybe_finish_drain(stream)
        return status

    def _discard_in_flight(self, stream: Stream, item: QueuedFrame) -> None:
        self.drop_stream(stream.stream_id, [q.sequence for q in stream.input_queue])
        stream.input_queue.clear()
        start = stream.delivered_end
        end = stream.accepted_end
        record = CancellationRecord(
            stream_id=stream.stream_id, epoch=job_epoch(stream, item),
            reason=stream.cancelled or "obsolete_epoch",
            queued_sequences=tuple(q.sequence for q in []),
            in_flight_sequence=item.sequence,
            abandoned_start=start, abandoned_end=end,
            abandoned_samples=max(0, end - start), discarded_output=True,
        )
        stream.cancellations.append(record)
        stream.counters["discarded_frames"] += 1
        stream.counters["cancelled_samples"] += record.abandoned_samples
        self.domain.counters["cancelled_intervals"] += 1
        self.domain.counters["cancelled_samples"] += record.abandoned_samples

    def _process_frame(self, stream: Stream, item: QueuedFrame,
                       drain: bool) -> Status:
        frame = item.frame
        source_first = frame.first_sample - stream.graph.total_delay
        ctx_base: dict[str, Any] = {
            "frame_index": stream.produced_frames + stream.drain_calls,
            "source_first": source_first,
            "valid_count_in": frame.valid_count,
            "epoch": stream.epoch,
            "stream_id": stream.stream_id,
            "tap_port": "",
            "ready_ns": 0,
        }
        current = tuple(float(x) for x in frame.samples)
        raw_events: list[dict[str, Any]] = []
        work_ns = 0
        for node in stream.graph.audio_nodes:
            provider = stream.providers[node["id"]]
            mode = stream.mode if stream.mode != "full" else "full"
            try:
                if mode != "full" and bool(provider.capabilities().get("process_mode")):
                    outcome = provider.process_mode(current, node["settings"], ctx_base, mode)
                    if mode == "cheap":
                        stream.counters["transition_cheap_calls"] += 1
                    else:
                        stream.counters["transition_observe_calls"] += 1
                else:
                    outcome = provider.process(current, node["settings"], ctx_base)
            except ProviderFailure as exc:
                return self._record_failure(stream, node["id"], exc.reason, item.sequence,
                                            source_first)
            if outcome.failure or len(outcome.samples) != FRAME_SAMPLES:
                return self._record_failure(
                    stream, node["id"], outcome.failure or "bad_output_count", item.sequence,
                    source_first)
            current = outcome.samples
            work_ns += outcome.work_ns
        if work_ns < 0:
            return self._record_failure(stream, "work", "negative_work", item.sequence, source_first)
        ready_ns = self.domain.clock.advance(work_ns)
        ctx_base["ready_ns"] = ready_ns
        for node in stream.graph.analysis_nodes:
            provider = stream.providers[node["id"]]
            ctx = dict(ctx_base, tap_port=node["tap_port"])
            try:
                outcome = provider.process(current, node["settings"], ctx)
            except ProviderFailure:
                continue
            work_ns += outcome.work_ns
            if outcome.work_ns:
                ready_ns = self.domain.clock.advance(outcome.work_ns)
            for raw in outcome.events:
                admitted = stream.submit_analysis(raw)
                if admitted.get("status") == "ok":
                    raw_events.append(admitted)
        if len(stream.output_queue) >= self.domain.config.output_capacity:
            return Status.RESOURCE_EXHAUSTED
        valid_offset = max(0, stream.first_sample - source_first)
        valid_end = min(FRAME_SAMPLES, stream.accepted_end - source_first)
        valid_count = max(0, valid_end - valid_offset)
        if drain and stream.accepted_source_end is not None:
            valid_end = min(valid_end, stream.accepted_source_end - source_first)
            valid_count = max(0, valid_end - valid_offset)
        miss = ready_ns > item.deadline_ns
        if miss:
            stream.counters["deadline_misses"] += 1
            self.domain.counters["deadline_misses"] += 1
            stream.deadline_misses.append({
                "stream_id": stream.stream_id, "sequence": item.sequence,
                "deadline_ns": str(item.deadline_ns), "ready_ns": str(ready_ns),
            })
        output = OutputFrame(
            sequence=item.sequence, epoch=stream.epoch, samples=current,
            source_first_sample=source_first, valid_offset=valid_offset,
            valid_count=valid_count, ready_ns=ready_ns,
            capture_first_ns=item.capture_first_ns, deadline_ns=item.deadline_ns,
            deadline_miss=miss, events=tuple(raw_events), drain=drain,
        )
        stream.output_queue.append(output)
        stream.produced_samples_list.extend(current)
        stream.counters["produced_frames"] += 1
        stream.counters["produced_samples"] += FRAME_SAMPLES
        stream.counters["output_high_water"] = max(stream.counters["output_high_water"],
                                                   len(stream.output_queue))
        self.domain.counters["produced_frames"] += 1
        return Status.OK

    def _record_failure(self, stream: Stream, lane: str, reason: str,
                        sequence: Optional[int], source_first: int) -> Status:
        record = FailureRecord(
            stream_id=stream.stream_id, epoch=stream.epoch, lane=lane, reason=reason,
            sequence=sequence, start=source_first, end=source_first + FRAME_SAMPLES,
        )
        stream.failures.append(record)
        stream.counters["failed_lanes"] += 1
        stream.lifecycle = Lifecycle.NEEDS_RESET
        self.domain.counters["failed_lanes"] += 1
        self.domain.counters["domain_failures"] += 1
        self.domain.failures.append(record)
        self.drop_stream(stream.stream_id, [q.sequence for q in stream.input_queue])
        stream.input_queue.clear()
        return Status.BACKEND_FAILURE

    def _maybe_finish_drain(self, stream: Stream) -> Status:
        if not stream.end_input_closed or stream.drain_complete:
            return Status.OK
        pending = self.pending_for(stream.stream_id) or bool(stream.input_queue)
        if pending or stream.output_queue:
            return Status.OK
        covered_end = stream.first_sample + stream.produced_frames * FRAME_SAMPLES - stream.graph.total_delay
        accepted_end = stream.accepted_source_end or stream.accepted_end
        if covered_end < accepted_end:
            if stream.drain_calls >= stream.graph.max_drain_calls:
                return self._record_failure(stream, "drain", "drain_cap", None, covered_end)
            stream.drain_calls += 1
            stream.lifecycle = Lifecycle.DRAINING
            values = [0.0] * FRAME_SAMPLES
            item = QueuedFrame(self.domain.scheduler.next_sequence(),
                               Frame(tuple(values), min(FRAME_SAMPLES, accepted_end - covered_end),
                                     stream.epoch, covered_end, 0),
                               self.domain.clock.now_ns,
                               self.domain.clock.now_ns + stream.graph.total_work_ns + 1)
            self.domain.counters["drain_frames"] += 1
            return self._process_frame(stream, item, drain=True)
        stream.drain_complete = True
        stream.lifecycle = Lifecycle.DRAINED
        return Status.OK

    def step(self, pull_callback: Optional[Callable[[], None]] = None) -> Status:
        if self.begin_step() is not None:
            status = self.finish_step()
        else:
            progressed = False
            for stream_id in sorted(self.domain.streams):
                stream = self.domain.streams[stream_id]
                if (stream.end_input_closed and not stream.drain_complete
                        and len(stream.output_queue) < self.domain.config.output_capacity
                        and not self.pending_for(stream_id) and not stream.input_queue):
                    before = stream.drain_calls, stream.produced_frames
                    status = self._maybe_finish_drain(stream)
                    self.steps += 1
                    progressed = (before != (stream.drain_calls, stream.produced_frames)
                                  or stream.drain_complete or status is not Status.OK)
                    break
            if not progressed:
                return Status.NOT_READY
        if pull_callback is not None:
            pull_callback()
        return status


def job_epoch(stream: Stream, item: QueuedFrame) -> int:
    return item.frame.epoch


class Domain:
    def __init__(self, raw_config: Mapping[str, Any],
                 factories: Optional[Mapping[str, Callable[[str], Any]]] = None,
                 clock: Optional[Clock] = None) -> None:
        config, status, reason = validate_domain(dict(raw_config))
        if status is not Status.OK or config is None:
            raise ValueError(f"invalid_domain_config:{reason}")
        self.config = config
        self.factories = dict(factories or builtin_provider_factories())
        self.clock = clock or Clock()
        self.streams: dict[int, Stream] = {}
        self.next_stream_id = 1
        self.resources: dict[str, int] = {}
        self.scheduler = Scheduler(self)
        self.closed = False
        self.admission_closed = False
        self.failures: list[FailureRecord] = []
        self.counters: dict[str, Any] = {
            "admissions": 0, "admission_rejections": 0, "cancelled_intervals": 0,
            "cancelled_samples": 0, "deadline_misses": 0, "failed_lanes": 0,
            "domain_failures": 0, "produced_frames": 0, "drain_frames": 0,
            "quiesce_barrier_waits": 0, "fatal_worker_failures": 0,
            "epoch_transitions": [],
        }

    def create_scheduler(self) -> None:
        raise ValueError("second_scheduler_rejected")

    def admit(self, graph_raw: Mapping[str, Any], format_raw: Mapping[str, Any]
              ) -> tuple[Optional[Stream], Status, str, Acceptance]:
        if self.closed or self.admission_closed:
            return None, Status.NEEDS_RESET, "admission_closed", Acceptance(Status.NEEDS_RESET)
        epoch, first, assets, status, reason = validate_format(format_raw)
        if status is not Status.OK or epoch is None or first is None:
            self.counters["admission_rejections"] += 1
            return None, Status.INVALID_ARGUMENT, reason, Acceptance(Status.INVALID_ARGUMENT, reason=reason)
        graph, status, reason = validate_graph(graph_raw, self.config, self.factories)
        if status is not Status.OK or graph is None:
            self.counters["admission_rejections"] += 1
            return None, status, reason, Acceptance(status, reason=reason)
        resource_keys = (
            f"graph:{graph.raw['graph_id']}",
            *[f"instance:{graph.raw['graph_id']}:{node['id']}:{node['provider_id']}"
              for node in graph.raw["nodes"]],
            *[f"asset:{asset_id}" for asset_id in assets],
        )
        if any(key in self.resources for key in resource_keys):
            self.counters["admission_rejections"] += 1
            return None, Status.RESOURCE_EXHAUSTED, "resource_already_admitted", Acceptance(
                Status.RESOURCE_EXHAUSTED, reason="resource_already_admitted")
        if len(self.streams) >= self.config.max_streams:
            self.counters["admission_rejections"] += 1
            return None, Status.RESOURCE_EXHAUSTED, "max_streams", Acceptance(
                Status.RESOURCE_EXHAUSTED, reason="max_streams")
        providers: dict[str, Any] = {}
        try:
            for node in graph.raw["nodes"]:
                instance_id = f"s{self.next_stream_id}.{node['id']}"
                providers[node["id"]] = self.factories[node["provider_id"]](instance_id)
        except Exception as exc:  # admission failure must not leave partial state
            return None, Status.RESOURCE_EXHAUSTED, f"provider_alloc:{exc}", Acceptance(
                Status.RESOURCE_EXHAUSTED, reason="provider_alloc")
        stream_id = self.next_stream_id
        self.next_stream_id += 1
        stream = Stream(self, stream_id, graph, epoch, first, assets, providers)
        self.streams[stream_id] = stream
        for key in resource_keys:
            self.resources[key] = stream_id
        self.counters["admissions"] += 1
        return stream, Status.OK, "", Acceptance(Status.OK, 0, FRAME_SAMPLES)

    def remove_stream(self, stream_id: Optional[int], owner: str = CONTROL_OWNER) -> Status:
        if owner != CONTROL_OWNER:
            return Status.INVALID_ARGUMENT
        if stream_id is None:
            return Status.OK
        stream = self.streams.get(stream_id)
        if stream is None:
            return Status.OK  # repeated remove of an empty handle is harmless
        return stream.remove(owner)

    def drop_stream(self, stream_id: int) -> None:
        self.streams.pop(stream_id, None)
        self.resources = {key: owner for key, owner in self.resources.items() if owner != stream_id}
        self.scheduler.drop_stream(stream_id)

    def close(self) -> Status:
        if self.closed:
            return Status.INVALID_ARGUMENT
        if self.streams:
            return Status.BUSY
        self.closed = True
        return Status.OK

    def inject_fatal_worker_failure(self, reason: str = "worker_fatal") -> Status:
        self.admission_closed = True
        self.counters["fatal_worker_failures"] += 1
        for stream_id in sorted(self.streams):
            stream = self.streams[stream_id]
            record = FailureRecord(
                stream_id=stream_id, epoch=stream.epoch, lane="worker", reason=reason,
                sequence=None, start=stream.delivered_end, end=stream.accepted_end,
            )
            stream.failures.append(record)
            stream.lifecycle = Lifecycle.NEEDS_RESET
            self.failures.append(record)
        return Status.NEEDS_RESET

    def pull_and_release(self) -> None:
        for stream_id in sorted(self.streams):
            stream = self.streams[stream_id]
            pulled = stream.pull()
            if pulled.status is Status.OK and pulled.lease is not None:
                stream.release(pulled.lease.lease_id)

    def process_batch(self, stream: Stream, node_id: str,
                      lanes: Sequence[Mapping[str, Any]]) -> list[BatchResult]:
        node = stream.graph.nodes_by_id.get(node_id)
        if node is None or not bool(node.get("hooks", {}).get("process_batch")):
            return [BatchResult("invalid", stream.stream_id, Status.INVALID_ARGUMENT,
                                "failed", 0, 0, 0, 0, False, "", "hook_unsupported")]
        provider = stream.providers[node_id]
        state_ids = [str(lane["state_id"]) for lane in lanes]
        configs = {str(lane["config_digest"]) for lane in lanes}
        structural_reason = ""
        if len(set(state_ids)) != len(state_ids):
            structural_reason = "aliased_lane_state"
        elif len(configs) != 1:
            structural_reason = "incompatible_lane_state"
        if structural_reason:
            return [BatchResult(state_id, stream.stream_id, Status.INVALID_ARGUMENT,
                                "failed", 0, 0, 0, 0, False, "", structural_reason)
                    for state_id in state_ids]
        payload = [dict(lane) for lane in lanes]
        try:
            outcomes = provider.process_batch(payload)
        except ProviderFailure as exc:
            return [BatchResult(state_ids[0], stream.stream_id, Status.INVALID_ARGUMENT,
                                "failed", 0, 0, 0, 0, False, "", exc.reason)]
        results: list[BatchResult] = []
        for index, (lane, outcome) in enumerate(zip(payload, outcomes)):
            valid_count = int(lane["valid_count"])
            source_first = int(lane["first_sample"]) - int(node["delay_samples"])
            valid_offset = max(0, stream.first_sample - source_first)
            valid_end = min(FRAME_SAMPLES, int(lane["accepted_end"]) - source_first)
            valid_count = max(0, min(valid_count, valid_end - valid_offset))
            now = self.clock.now_ns + int(outcome.work_ns)
            if outcome.failure:
                results.append(BatchResult(
                    str(lane["state_id"]), stream.stream_id, Status.BACKEND_FAILURE, "failed",
                    source_first, valid_offset, valid_count, now, False, "", outcome.failure))
                stream.counters["failed_lanes"] += 1
                self.counters["failed_lanes"] += 1
                continue
            miss = now > int(lane["deadline_ns"])
            results.append(BatchResult(
                str(lane["state_id"]), stream.stream_id, Status.OK, outcome.validity,
                source_first, valid_offset, valid_count, now, miss,
                sha256_hex(canonical_bytes([float(x) for x in outcome.samples])),
            ))
            stream.counters["batch_lanes"] += 1
            if miss:
                stream.counters["deadline_misses"] += 1
                self.counters["deadline_misses"] += 1
        self.clock.advance(max((item.work_ns for item in outcomes), default=0))
        return results

    def stats_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_id": STATS_ID, "contract": CONTRACT_ID, "engine": ENGINE,
            "domain_id": self.config.domain_id, "domain_digest": self.config.digest,
            "worker_count": str(1), "max_streams": str(self.config.max_streams),
            "active_streams": str(len(self.streams)), "scheduler_owner": self.scheduler.owner,
            "scheduler_steps": str(self.scheduler.steps),
            "admissions": str(self.counters["admissions"]),
            "admission_rejections": str(self.counters["admission_rejections"]),
            "cancelled_intervals": str(self.counters["cancelled_intervals"]),
            "cancelled_samples": str(self.counters["cancelled_samples"]),
            "deadline_misses": str(self.counters["deadline_misses"]),
            "failed_lanes": str(self.counters["failed_lanes"]),
            "domain_failures": str(self.counters["domain_failures"]),
            "produced_frames": str(self.counters["produced_frames"]),
            "drain_frames": str(self.counters["drain_frames"]),
            "quiesce_barrier_waits": str(self.counters["quiesce_barrier_waits"]),
            "fatal_worker_failures": str(self.counters["fatal_worker_failures"]),
            "admission_closed": self.admission_closed,
            "epoch_transitions": self.counters["epoch_transitions"],
            "lifecycle": "closed" if self.closed else "open",
        }
        return payload

    def query_stats(self, stream_id: Optional[int] = None, capacity: int = 4096
                    ) -> tuple[Status, int, Optional[str]]:
        payload = self.stats_payload()
        if stream_id is not None:
            stream = self.streams.get(stream_id)
            if stream is None:
                return Status.INVALID_ARGUMENT, 0, None
            payload.update({
                "stream_id": str(stream.stream_id), "graph_id": stream.graph.raw["graph_id"],
                "graph_digest": stream.graph.digest, "epoch": str(stream.epoch),
                "first_sample": str(stream.first_sample),
                "accepted_end": str(stream.accepted_end),
                "delivered_end": str(stream.delivered_end),
                "lifecycle": stream.lifecycle.value, "mode": stream.mode,
                "scheduler_id": stream.scheduler_id,
                "input_occupancy": str(len(stream.input_queue)),
                "output_occupancy": str(len(stream.output_queue)),
                "active_lease": stream.active_lease.lease_id if stream.active_lease else None,
                "drain_calls": str(stream.drain_calls),
                "cancelled": stream.cancelled,
                "transition_calls": str(stream.counters["transition_cheap_calls"]),
            })
            for key in ("submitted_frames", "accepted_samples", "produced_frames", "produced_samples",
                        "delivered_valid_samples", "lease_acquires", "lease_releases",
                        "bad_lease_releases", "rejected_frames", "discarded_frames",
                        "cancelled_samples", "deadline_misses", "failed_lanes",
                        "analysis_accepted", "analysis_rejected", "input_high_water",
                        "output_high_water", "quiesce_timeouts", "batch_lanes",
                        "transition_cheap_calls", "transition_observe_calls"):
                payload[key] = str(stream.counters[key])
        data = canonical_bytes(payload)
        required = len(data) + 1
        if capacity < required:
            return Status.RESOURCE_EXHAUSTED, required, None
        return Status.OK, required, data.decode("ascii")


def canonical_report(domain: Domain, stream: Stream,
                     terminal_status: Status = Status.END_OF_STREAM
                     ) -> tuple[str, str]:
    status, _, text = domain.query_stats(stream.stream_id, capacity=1 << 20)
    if status is not Status.OK or text is None:
        raise RuntimeError("stats_query_failed")
    payload = {
        "contract": CONTRACT_ID,
        "engine": ENGINE,
        "abi_version": ABI_VERSION,
        "domain_id": domain.config.domain_id,
        "domain_digest": domain.config.digest,
        "graph_id": stream.graph.raw["graph_id"],
        "graph_digest": stream.graph.digest,
        "stream_id": stream.stream_id,
        "epoch": stream.epoch,
        "status": terminal_status.value,
        "stream_lifecycle": stream.lifecycle.value,
        "output_f32_digest": stream.output_digest(),
        "source_intervals": [[lease.source_first_sample + lease.valid_offset,
                              lease.source_first_sample + lease.valid_offset + lease.valid_count]
                             for lease in stream.delivered_leases],
        "lease_ids": [lease.lease_id for lease in stream.delivered_leases],
        "analysis_events": [record.as_dict() for record in stream.analysis_records],
        "deadline_misses": list(stream.deadline_misses),
        "cancellations": [record.as_dict() for record in stream.cancellations],
        "failures": [record.as_dict() for record in stream.failures],
        "epoch_transitions": domain.counters["epoch_transitions"],
        "monotonic_ns": str(domain.clock.now_ns),
        "stats": json.loads(text),
    }
    data = canonical_bytes(payload)
    return data.decode("ascii"), sha256_hex(data)
