"""Model-free reference executor for the proposed ordered audio chain.

This is a deterministic Python model of the versioned recipe/executor contract in
``contract.json``. It is not an SDK provider, engine plugin, installed API or
runtime. Fixed v0 remains 16 kHz mono f32 with 160-sample frames. Nothing here
changes public headers, descriptors, registry or default behavior.

The model keeps three independent facts separate:

* stage order is the ordered application of transforms to produced samples;
* content delay is an integer source-coordinate offset over audio nodes only;
* availability is a declared monotonic nanosecond value, never inferred from
  source timestamps or delay.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Optional, Sequence

CONTRACT_ID = "audio-sdk/ordered-chain-graph/0.1"
CONTRACT_VERSION = "0.1"
ENGINE = "reference.sequential.v0"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62500
NS_PER_FRAME = FRAME_SAMPLES * NS_PER_SAMPLE
MAX_NODES = 16
MAX_DELAY_SAMPLES = 16000
MAX_COST_NS = 10_000_000_000
FINAL_INPUT = 1
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
_FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
}
_ROOT_KEYS = frozenset(
    ("schema_id", "recipe_id", "contract_version", "engine", "format", "audio_path", "nodes")
)
_AUDIO_KEYS = frozenset(
    ("id", "provider_id", "role", "delay_samples", "availability_cost_ns",
     "settings", "depends_on", "input_port", "output_port")
)
_ANALYSIS_KEYS = frozenset(
    ("id", "provider_id", "role", "delay_samples", "availability_cost_ns",
     "settings", "depends_on", "tap_port", "max_age_samples")
)


class Status(str, Enum):
    OK = "ok"
    END_OF_STREAM = "end_of_stream"
    REJECTED_BAD_SHAPE = "rejected_bad_shape"
    REJECTED_CYCLE = "rejected_cycle"
    REJECTED_DUPLICATE_ID = "rejected_duplicate_id"
    REJECTED_UNAVAILABLE_STAGE = "rejected_unavailable_stage"
    REJECTED_AMBIGUOUS_PORT = "rejected_ambiguous_port"
    REJECTED_UNKNOWN_PORT = "rejected_unknown_port"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_STALE_EPOCH = "rejected_stale_epoch"
    REJECTED_BAD_FRAME = "rejected_bad_frame"
    REJECTED_NONFINITE_INPUT = "rejected_nonfinite_input"
    REJECTED_BAD_PADDING = "rejected_bad_padding"
    REJECTED_BAD_CLOCK = "rejected_bad_clock"
    REJECTED_FAILING_PORT = "rejected_failing_port"
    REJECTED_INVALID_EVENT = "rejected_invalid_event"
    REJECTED_STALE_EVENT = "rejected_stale_event"
    REJECTED_NEEDS_RESET = "rejected_needs_reset"
    REJECTED_BUSY = "rejected_busy"
    REJECTED_CANCELLED = "rejected_cancelled"
    REJECTED_DRAIN_CAP = "rejected_drain_cap"


class Validity(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    INVALID = "invalid"


class StageFailure(Exception):
    """A declared port failed; the executor records the interval and stops."""

    def __init__(self, reason: str, port: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.port = port


class Stage:
    """Duck-typed stage contract shared with an installed third-party fixture."""

    role: str = "audio"

    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return 0

    def cost_ns(self, settings: Mapping[str, Any]) -> int:
        return int(settings.get("availability_cost_ns", 0))

    def transform(self, samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]) -> tuple[tuple[float, ...], tuple[dict, ...]]:
        return tuple(samples), ()


class IdentityStage(Stage):
    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return 0


class DelayStage(Stage):
    """Buffering delay only; samples are selected by source coordinates."""

    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return int(settings["delay_samples"])


class GainStage(Stage):
    def transform(self, samples, settings, ctx):
        gain = settings["gain"]
        if not _finite_number(gain):
            raise StageFailure("nonfinite_setting", ctx["input_port"])
        return tuple(float(x) * float(gain) for x in samples), ()


class LimiterStage(Stage):
    def transform(self, samples, settings, ctx):
        peak = settings["peak"]
        if not _finite_number(peak) or float(peak) < 0.0:
            raise StageFailure("invalid_peak", ctx["input_port"])
        return tuple(max(-float(peak), min(float(peak), float(x))) for x in samples), ()


class ActivityStage(Stage):
    """Built-in analysis probe; mirrors the installed third-party event script."""

    role = "analysis"

    def transform(self, samples, settings, ctx):
        index = int(ctx["frame_index"])
        if index > 3:
            return tuple(samples), ()
        availability = (int(ctx["availability_ns"])
                        + int(settings.get("event_offset_ns", 0)))
        start = max(0, int(ctx["source_first"]))
        end = int(ctx["source_first"]) + int(ctx["valid_count_in"])
        if index == 1:
            return tuple(samples), ()
        value: Optional[float]
        validity: str
        if index == 0:
            value, validity = 0.75, Validity.KNOWN.value
        elif index == 2:
            value, validity = None, Validity.UNKNOWN.value
        else:
            value, validity = float("nan"), Validity.KNOWN.value
        event = {
            "source_start": start,
            "source_end": end,
            "value": value,
            "validity": validity,
            "available_ns": availability,
            "epoch": ctx["epoch"],
        }
        return tuple(samples), (event,)


class FailingStage(Stage):
    """Negative control: fails a declared output port on a chosen frame index."""

    def transform(self, samples, settings, ctx):
        if int(ctx["frame_index"]) == int(settings["fail_at_frame"]):
            raise StageFailure(settings.get("reason", "backend_failure"), ctx["output_port"])
        return tuple(samples), ()


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


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Restricted canonical JSON used for recipe identity and reports."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text.encode("ascii")


def recipe_digest(raw: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(raw)).hexdigest()


@dataclass(frozen=True)
class Recipe:
    raw: dict[str, Any]
    digest: str
    audio_nodes: tuple[dict[str, Any], ...]
    analysis_nodes: tuple[dict[str, Any], ...]
    total_delay: int
    audio_cost_ns: int
    analysis_cost_ns: int

    @property
    def stage_order(self) -> tuple[str, ...]:
        return tuple(node["id"] for node in self.audio_nodes)


@dataclass(frozen=True)
class Frame:
    samples: tuple[float, ...]
    valid_count: int
    epoch: int
    first_sample: int
    flags: int = 0


@dataclass(frozen=True)
class SideEvent:
    tap_port: str
    node_id: str
    source_start: int
    source_end: int
    value: Optional[float]
    validity: str
    available_ns: Optional[int]
    epoch: int
    status: str = Status.OK.value

    def as_dict(self) -> dict[str, Any]:
        return {
            "tap_port": self.tap_port,
            "node_id": self.node_id,
            "source_start": self.source_start,
            "source_end": self.source_end,
            "value": self.value,
            "validity": self.validity,
            "available_ns": self.available_ns,
            "epoch": self.epoch,
            "status": self.status,
        }


@dataclass(frozen=True)
class Lease:
    lease_id: str
    samples: tuple[float, ...]
    source_first_sample: int
    valid_offset: int
    valid_count: int
    availability_ns: int
    stage_order: tuple[str, ...]
    events: tuple[SideEvent, ...]
    recipe_digest: str
    drain: bool = False


@dataclass(frozen=True)
class ProcessResult:
    status: Status
    lease: Optional[Lease] = None
    reason: Optional[str] = None
    port: Optional[str] = None
    failed_interval: Optional[tuple[int, int]] = None


@dataclass(frozen=True)
class CancellationRecord:
    epoch: int
    reason: str
    lease_id: Optional[str]
    abandoned_start: int
    abandoned_end: int
    abandoned_valid_samples: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "epoch": self.epoch,
            "reason": self.reason,
            "lease_id": self.lease_id,
            "abandoned_start": self.abandoned_start,
            "abandoned_end": self.abandoned_end,
            "abandoned_valid_samples": self.abandoned_valid_samples,
        }


def validate_recipe(raw: Any, available: Mapping[str, Stage]
                    ) -> tuple[Optional[Recipe], Status, str]:
    """Validate shape, identity inputs, topology, ports and stage availability."""
    if not isinstance(raw, dict) or set(raw) != _ROOT_KEYS:
        return None, Status.REJECTED_BAD_SHAPE, "root_keys"
    if (raw["schema_id"] != CONTRACT_ID or raw["contract_version"] != CONTRACT_VERSION
            or raw["engine"] != ENGINE or raw["format"] != _FORMAT):
        return None, Status.REJECTED_BAD_SHAPE, "version_or_format"
    if not isinstance(raw["recipe_id"], str) or not _ID.match(raw["recipe_id"]):
        return None, Status.REJECTED_BAD_SHAPE, "recipe_id"
    nodes = raw["nodes"]
    path = raw["audio_path"]
    if not isinstance(nodes, list) or not isinstance(path, list):
        return None, Status.REJECTED_BAD_SHAPE, "nodes_or_path_type"
    if not 1 <= len(nodes) <= MAX_NODES or not 1 <= len(path) <= MAX_NODES:
        return None, Status.REJECTED_BAD_SHAPE, "node_count"

    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            return None, Status.REJECTED_BAD_SHAPE, "node_type"
        role = node.get("role")
        expected = _AUDIO_KEYS if role == "audio" else _ANALYSIS_KEYS if role == "analysis" else frozenset()
        if not expected or set(node) != expected:
            return None, Status.REJECTED_BAD_SHAPE, "node_keys"
        node_id = node["id"]
        if (not isinstance(node_id, str) or not _ID.match(node_id)
                or not isinstance(node["provider_id"], str) or not _ID.match(node["provider_id"])):
            return None, Status.REJECTED_BAD_SHAPE, "node_id"
        if node_id in by_id:
            return None, Status.REJECTED_DUPLICATE_ID, node_id
        by_id[node_id] = node
        if not isinstance(node["delay_samples"], int) or isinstance(node["delay_samples"], bool):
            return None, Status.REJECTED_BAD_SHAPE, "delay_type"
        if not 0 <= node["delay_samples"] <= MAX_DELAY_SAMPLES:
            return None, Status.REJECTED_BAD_SHAPE, "delay_range"
        if (not isinstance(node["availability_cost_ns"], int)
                or isinstance(node["availability_cost_ns"], bool)
                or not 0 <= node["availability_cost_ns"] <= MAX_COST_NS):
            return None, Status.REJECTED_BAD_SHAPE, "cost_range"
        if not isinstance(node["settings"], dict) or not _finite_settings(node["settings"]):
            return None, Status.REJECTED_NONFINITE, node_id
        if (not isinstance(node["depends_on"], list) or len(node["depends_on"]) > MAX_NODES
                or any(not isinstance(item, str) for item in node["depends_on"])):
            return None, Status.REJECTED_BAD_SHAPE, "depends_on"

    # depends_on may reference a later node; check all references once ids are known.
    for node in nodes:
        if any(item not in by_id for item in node["depends_on"]):
            return None, Status.REJECTED_BAD_SHAPE, "depends_on_unknown"

    audio_nodes = [by_id.get(node_id) for node_id in path]
    if any(node is None for node in audio_nodes):
        return None, Status.REJECTED_UNKNOWN_PORT, "audio_path"
    audio_nodes = [node for node in audio_nodes if node is not None]
    if any(node["role"] != "audio" for node in audio_nodes):
        return None, Status.REJECTED_BAD_SHAPE, "audio_path_role"
    audio_ids = {node["id"] for node in audio_nodes}
    declared_audio = {node["id"] for node in nodes if node["role"] == "audio"}
    if len(audio_ids) != len(audio_nodes) or audio_ids != declared_audio:
        return None, Status.REJECTED_BAD_SHAPE, "audio_path_coverage"

    analysis_nodes = [node for node in nodes if node["role"] == "analysis"]
    inputs = [node["input_port"] for node in audio_nodes]
    outputs = [node["output_port"] for node in audio_nodes]
    if any(not isinstance(port, str) or not _ID.match(port) for port in inputs + outputs):
        return None, Status.REJECTED_BAD_SHAPE, "port_id"
    if len(inputs) != len(set(inputs)) or len(outputs) != len(set(outputs)):
        return None, Status.REJECTED_AMBIGUOUS_PORT, "duplicate_producer_or_consumer"
    for index, node in enumerate(audio_nodes):
        expected_in = "pcm.in" if index == 0 else audio_nodes[index - 1]["output_port"]
        if node["input_port"] != expected_in:
            return None, Status.REJECTED_AMBIGUOUS_PORT, node["id"]

    outputs = {node["output_port"]: node["id"] for node in audio_nodes}
    for node in analysis_nodes:
        tap_port = node["tap_port"]
        if not isinstance(tap_port, str) or tap_port not in outputs:
            return None, Status.REJECTED_UNKNOWN_PORT, node["id"]
        if outputs[tap_port] not in node["depends_on"]:
            return None, Status.REJECTED_BAD_SHAPE, "tap_dependency"
        if not isinstance(node["max_age_samples"], int) or not 0 <= node["max_age_samples"] <= MAX_DELAY_SAMPLES:
            return None, Status.REJECTED_BAD_SHAPE, "max_age"

    edges: dict[str, list[str]] = {node_id: list(node["depends_on"]) for node_id, node in by_id.items()}
    for node in analysis_nodes:
        edges[node["id"]].append(outputs[node["tap_port"]])
    color: dict[str, int] = {}

    def visit(node_id: str) -> bool:
        if color.get(node_id) == 1:
            return True
        if color.get(node_id) == 2:
            return False
        color[node_id] = 1
        for child in edges[node_id]:
            if child not in by_id or visit(child):
                return True
        color[node_id] = 2
        return False

    if any(visit(node_id) for node_id in by_id):
        return None, Status.REJECTED_CYCLE, "depends_on_or_tap"

    for node in nodes:
        stage = available.get(node["provider_id"])
        if stage is None:
            return None, Status.REJECTED_UNAVAILABLE_STAGE, node["provider_id"]
        if getattr(stage, "role", "audio") != node["role"]:
            return None, Status.REJECTED_BAD_SHAPE, "stage_role"
        try:
            declared_delay = stage.delay_samples(node["settings"])
            declared_cost = stage.cost_ns({
                **node["settings"],
                "availability_cost_ns": node["availability_cost_ns"],
            })
        except (KeyError, TypeError, ValueError) as exc:
            return None, Status.REJECTED_BAD_SHAPE, f"stage_settings:{exc}"
        if declared_delay != node["delay_samples"] or declared_cost != node["availability_cost_ns"]:
            return None, Status.REJECTED_BAD_SHAPE, "stage_metadata_mismatch"

    recipe = Recipe(
        raw=json.loads(json.dumps(raw, sort_keys=True, allow_nan=False)),
        digest=recipe_digest(raw),
        audio_nodes=tuple(audio_nodes),
        analysis_nodes=tuple(analysis_nodes),
        total_delay=sum(node["delay_samples"] for node in audio_nodes),
        audio_cost_ns=sum(node["availability_cost_ns"] for node in audio_nodes),
        analysis_cost_ns=sum(node["availability_cost_ns"] for node in analysis_nodes),
    )
    return recipe, Status.OK, ""


class SequentialExecutor:
    """One ordered audio path with read-only analysis taps and exact bookkeeping."""

    def __init__(self, recipe: Recipe, available: Mapping[str, Stage],
                 max_drain_calls: int = 4,
                 stream_origin_ns: int = 1_000_000_000) -> None:
        if max_drain_calls < 1:
            raise ValueError("max_drain_calls must be positive")
        self.recipe = recipe
        self.available = dict(available)
        self.max_drain_calls = max_drain_calls
        self.stream_origin_ns = stream_origin_ns
        self.epoch = 1
        self.stream_start = 0
        self.next_input_sample = 0
        self.accepted: dict[int, float] = {}
        self.accepted_end = 0
        self.produced_frames = 0
        self.drain_calls = 0
        self.final_input = False
        self.draining = False
        self.needs_reset = False
        self.cancelled: Optional[str] = None
        self.lease: Optional[Lease] = None
        self.last_audio_availability_ns = stream_origin_ns - 1
        self.events: list[SideEvent] = []
        self.hold_last: dict[str, Optional[float]] = {
            node["tap_port"]: None for node in recipe.analysis_nodes
        }
        self.cancellations: list[CancellationRecord] = []
        self.failed_ports: list[dict[str, Any]] = []
        self.valid_intervals: list[tuple[int, int]] = []
        self.output_samples: list[float] = []
        self.tap_outputs: dict[str, tuple[float, ...]] = {}
        self.trace: list[list[str]] = []
        self.counters = {
            "submitted_frames": 0,
            "accepted_samples": 0,
            "produced_samples": 0,
            "delivered_valid_samples": 0,
            "rejected_frames": 0,
            "known_events": 0,
            "unknown_events": 0,
            "invalid_events": 0,
            "stale_events": 0,
            "cancelled_intervals": 0,
            "cancelled_samples": 0,
            "failed_ports": 0,
            "drain_calls": 0,
        }
        self.epoch_transitions: list[dict[str, Any]] = []

    def _reject(self, status: Status, reason: str, **extra: Any) -> ProcessResult:
        self.counters["rejected_frames"] += 1
        return ProcessResult(status, reason=reason, **extra)

    def process(self, frame: Frame) -> ProcessResult:
        if self.cancelled:
            return self._reject(Status.REJECTED_CANCELLED, "cancelled")
        if self.needs_reset:
            return self._reject(Status.REJECTED_NEEDS_RESET, "backend_failure")
        if self.draining:
            return self._reject(Status.REJECTED_BAD_FRAME, "drain_started")
        if self.lease is not None:
            return self._reject(Status.REJECTED_BUSY, "outstanding_lease")
        if frame.epoch != self.epoch:
            return self._reject(Status.REJECTED_STALE_EPOCH, "epoch")
        if frame.first_sample != self.next_input_sample:
            return self._reject(Status.REJECTED_BAD_FRAME, "first_sample")
        if len(frame.samples) != FRAME_SAMPLES or not 0 <= frame.valid_count <= FRAME_SAMPLES:
            return self._reject(Status.REJECTED_BAD_FRAME, "counts")
        if frame.flags & ~FINAL_INPUT:
            return self._reject(Status.REJECTED_BAD_FRAME, "flags")
        if self.final_input:
            return self._reject(Status.REJECTED_BAD_FRAME, "after_final")
        if any(not math.isfinite(float(x)) for x in frame.samples[:frame.valid_count]):
            return self._reject(Status.REJECTED_NONFINITE_INPUT, "nonfinite_input")
        if any(float(x) != 0.0 for x in frame.samples[frame.valid_count:]):
            return self._reject(Status.REJECTED_BAD_PADDING, "nonzero_padding")
        if frame.valid_count == 0 and not frame.flags & FINAL_INPUT:
            return self._reject(Status.REJECTED_BAD_FRAME, "empty_not_final")

        for index in range(frame.valid_count):
            self.accepted[frame.first_sample + index] = float(frame.samples[index])
        self.accepted_end = frame.first_sample + frame.valid_count
        self.next_input_sample = frame.first_sample + FRAME_SAMPLES
        self.counters["submitted_frames"] += 1
        self.counters["accepted_samples"] += frame.valid_count
        final = bool(frame.flags & FINAL_INPUT)
        if final:
            self.final_input = True
        if frame.valid_count == 0:
            return ProcessResult(Status.OK)

        self.produced_frames += 1
        return self._produce(frame.first_sample, frame.valid_count, drain=False)

    def _produce(self, source_first: int, valid_count_in: int, drain: bool) -> ProcessResult:
        recipe = self.recipe
        frame_index = (self.produced_frames + self.drain_calls if drain
                       else self.produced_frames - 1)
        source_first -= recipe.total_delay if not drain else 0
        samples = tuple(self.accepted.get(source_first + i, 0.0) for i in range(FRAME_SAMPLES))
        valid_offset = max(0, self.stream_start - source_first)
        valid_end = min(FRAME_SAMPLES, self.accepted_end - source_first)
        valid_count_out = max(0, valid_end - valid_offset)
        availability_ns = (self.stream_origin_ns + frame_index * NS_PER_FRAME
                           + recipe.audio_cost_ns)
        if availability_ns <= self.last_audio_availability_ns:
            return self._reject(Status.REJECTED_BAD_CLOCK, "nonmonotonic_availability")
        ctx_base: dict[str, Any] = {
            "frame_index": frame_index,
            "source_first": source_first,
            "valid_count_in": valid_count_in,
            "epoch": self.epoch,
            "availability_ns": availability_ns,
        }

        current = samples
        order: list[str] = []
        for node in recipe.audio_nodes:
            ctx = {**ctx_base, "input_port": node["input_port"],
                   "output_port": node["output_port"], "node_id": node["id"]}
            try:
                current, _ = self.available[node["provider_id"]].transform(
                    current, node["settings"], ctx)
            except Exception as exc:
                reason = str(getattr(exc, "reason", exc))
                port = str(getattr(exc, "port", node["output_port"]))
                interval = (source_first, source_first + FRAME_SAMPLES)
                self.needs_reset = True
                self.counters["failed_ports"] += 1
                self.failed_ports.append({
                    "epoch": self.epoch, "port": port, "reason": reason,
                    "start": interval[0], "end": interval[1],
                })
                return ProcessResult(Status.REJECTED_FAILING_PORT, reason,
                                     port=port, failed_interval=interval)
            if len(current) != FRAME_SAMPLES:
                return self._reject(Status.REJECTED_FAILING_PORT, "bad_port_count", port=node["output_port"])
            order.append(node["id"])
            self.tap_outputs[node["output_port"]] = current

        accepted_events: list[SideEvent] = []
        for node in recipe.analysis_nodes:
            tap_samples = self.tap_outputs.get(node["tap_port"], ())
            ctx = {**ctx_base,
                   "source_first": source_first + recipe.total_delay,
                   "availability_ns": availability_ns + recipe.analysis_cost_ns,
                   "node_id": node["id"], "tap_port": node["tap_port"]}
            try:
                _, produced = self.available[node["provider_id"]].transform(
                    tap_samples, node["settings"], ctx)
            except Exception:
                produced = ()
                self.counters["invalid_events"] += 1
            for raw_event in produced:
                status = self._admit_event(node, raw_event, source_first)
                value = raw_event["value"]
                if not _finite_number(value):
                    value = None  # rejects never enter a canonical report as NaN/Inf
                event = SideEvent(
                    tap_port=node["tap_port"], node_id=node["id"],
                    source_start=int(raw_event["source_start"]),
                    source_end=int(raw_event["source_end"]),
                    value=value, validity=str(raw_event["validity"]),
                    available_ns=raw_event["available_ns"],
                    epoch=int(raw_event["epoch"]), status=status.value,
                )
                accepted_events.append(event)
                self.events.append(event)

        self.last_audio_availability_ns = availability_ns
        self.output_samples.extend(current)
        self.trace.append(order)
        if valid_count_out:
            start = source_first + valid_offset
            self.valid_intervals.append((start, start + valid_count_out))
        self.counters["produced_samples"] += FRAME_SAMPLES
        if drain:
            self.drain_calls += 1
            self.counters["drain_calls"] += 1
        lease = Lease(
            lease_id=f"L{self.epoch}-{frame_index}",
            samples=current,
            source_first_sample=source_first,
            valid_offset=valid_offset,
            valid_count=valid_count_out,
            availability_ns=availability_ns,
            stage_order=tuple(order),
            events=tuple(accepted_events),
            recipe_digest=recipe.digest,
            drain=drain,
        )
        self.lease = lease
        return ProcessResult(Status.OK, lease=lease)

    def _admit_event(self, node: dict[str, Any], raw: Mapping[str, Any],
                     source_first: int) -> Status:
        if int(raw["epoch"]) != self.epoch:
            self.counters["stale_events"] += 1
            return Status.REJECTED_STALE_EVENT
        if (int(raw["source_end"]) <= int(raw["source_start"])
                or int(raw["source_end"]) < source_first
                or int(raw["source_start"]) > source_first + FRAME_SAMPLES
                or source_first - int(raw["source_end"]) > int(node["max_age_samples"])):
            self.counters["stale_events"] += 1
            return Status.REJECTED_STALE_EVENT
        validity = raw["validity"]
        if validity == Validity.KNOWN.value:
            value = raw["value"]
            if (not _finite_number(value) or not 0.0 <= float(value) <= 1.0
                    or not isinstance(raw["available_ns"], int)):
                self.counters["invalid_events"] += 1
                return Status.REJECTED_INVALID_EVENT
            self.counters["known_events"] += 1
            self.hold_last[node["tap_port"]] = float(value)
            return Status.OK
        if validity == Validity.UNKNOWN.value:
            if raw["value"] is not None:
                self.counters["invalid_events"] += 1
                return Status.REJECTED_BAD_SHAPE
            self.counters["unknown_events"] += 1
            return Status.OK
        self.counters["invalid_events"] += 1
        return Status.REJECTED_BAD_SHAPE

    def release(self, lease_id: str) -> Status:
        if self.lease is None or self.lease.lease_id != lease_id:
            return Status.REJECTED_BAD_FRAME
        self.counters["delivered_valid_samples"] += self.lease.valid_count
        self.lease = None
        return Status.OK

    def begin_drain(self) -> Status:
        if self.cancelled:
            return Status.REJECTED_CANCELLED
        if self.needs_reset:
            return Status.REJECTED_NEEDS_RESET
        if self.lease is not None:
            return Status.REJECTED_BUSY
        if not self.final_input or self.draining:
            return Status.REJECTED_BAD_FRAME
        self.draining = True
        return Status.OK

    def drain_next(self) -> ProcessResult:
        if self.cancelled:
            return self._reject(Status.REJECTED_CANCELLED, "cancelled")
        if self.needs_reset:
            return self._reject(Status.REJECTED_NEEDS_RESET, "backend_failure")
        if self.lease is not None:
            return self._reject(Status.REJECTED_BUSY, "outstanding_lease")
        if not self.draining:
            return self._reject(Status.REJECTED_BAD_FRAME, "drain_not_started")
        covered_end = (self.stream_start
                       + (self.produced_frames + self.drain_calls) * FRAME_SAMPLES
                       - self.recipe.total_delay)
        if covered_end >= self.accepted_end:
            return ProcessResult(Status.END_OF_STREAM)
        if self.drain_calls >= self.max_drain_calls:
            return self._reject(Status.REJECTED_DRAIN_CAP, "drain_cap")
        return self._produce(covered_end, 0, drain=True)

    def cancel(self, reason: str) -> CancellationRecord:
        if self.cancelled:
            raise RuntimeError("already_cancelled")
        self.cancelled = reason
        lease = self.lease
        start = lease.source_first_sample if lease else self.accepted_end
        end = start + FRAME_SAMPLES if lease else start
        record = CancellationRecord(
            epoch=self.epoch, reason=reason, lease_id=lease.lease_id if lease else None,
            abandoned_start=start, abandoned_end=end,
            abandoned_valid_samples=lease.valid_count if lease else 0,
        )
        self.cancellations.append(record)
        self.counters["cancelled_intervals"] += 1
        self.counters["cancelled_samples"] += end - start
        self.lease = None
        return record

    def reset(self, new_epoch: int, first_sample: int) -> Status:
        if new_epoch <= self.epoch:
            return Status.REJECTED_STALE_EPOCH
        if first_sample < 0:
            return Status.REJECTED_BAD_FRAME
        if self.lease is not None:
            return Status.REJECTED_BUSY
        if self.draining and self.cancelled is None:
            return Status.REJECTED_BUSY
        self.epoch_transitions.append({"from": self.epoch, "to": new_epoch,
                                       "cancelled": self.cancelled})
        self.epoch = new_epoch
        self.stream_start = first_sample
        self.next_input_sample = first_sample
        self.accepted = {}
        self.accepted_end = first_sample
        self.produced_frames = 0
        self.drain_calls = 0
        self.final_input = False
        self.draining = False
        self.needs_reset = False
        self.cancelled = None
        self.last_audio_availability_ns = self.stream_origin_ns - 1
        self.events = []
        self.hold_last = {node["tap_port"]: None for node in self.recipe.analysis_nodes}
        self.valid_intervals = []
        self.output_samples = []
        self.tap_outputs = {}
        self.trace = []
        for key in ("submitted_frames", "accepted_samples", "produced_samples",
                    "delivered_valid_samples", "rejected_frames", "known_events",
                    "unknown_events", "invalid_events", "stale_events", "failed_ports",
                    "drain_calls"):
            self.counters[key] = 0
        return Status.OK

    def output_digest(self) -> str:
        packed = b"".join(struct.pack("<f", float(x)) for x in self.output_samples)
        return hashlib.sha256(packed).hexdigest()

    def counters_dict(self) -> dict[str, Any]:
        return {key: int(value) for key, value in sorted(self.counters.items())}


def canonical_report(recipe: Recipe, executor: SequentialExecutor,
                     terminal_status: Status) -> tuple[str, str]:
    payload = {
        "contract": CONTRACT_ID,
        "recipe_id": recipe.raw["recipe_id"],
        "recipe_digest": recipe.digest,
        "epoch": executor.epoch,
        "status": terminal_status.value,
        "stage_order": list(recipe.stage_order),
        "observed_stage_order": executor.trace,
        "delay_samples": recipe.total_delay,
        "audio_availability_ns": executor.last_audio_availability_ns,
        "output_f32_digest": executor.output_digest(),
        "source_intervals": [list(item) for item in executor.valid_intervals],
        "side_events": [event.as_dict() for event in executor.events],
        "hold_last": dict(executor.hold_last),
        "counters": executor.counters_dict(),
        "cancellations": [item.as_dict() for item in executor.cancellations],
        "failed_ports": executor.failed_ports,
        "epoch_transitions": executor.epoch_transitions,
    }
    data = canonical_bytes(payload)
    return data.decode("ascii"), hashlib.sha256(data).hexdigest()


def builtin_available() -> dict[str, Stage]:
    return {
        "fixture.identity.v0": IdentityStage(),
        "fixture.delay.v0": DelayStage(),
        "fixture.gain.v0": GainStage(),
        "fixture.limiter.v0": LimiterStage(),
        "fixture.activity.v0": ActivityStage(),
        "fixture.failing.v0": FailingStage(),
    }
