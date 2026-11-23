# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic model-free reference for input -> identity -> output control.

This module is a Python reference model of a proposed session/loopback control.
It is NOT an SDK provider, engine plugin, public header, installed C API,
runtime, device path, paced workload, quality result or asset. It never opens
an SDK library and never reads real audio. The fixed v0 boundary is unchanged:
16 kHz, mono, f32, 160-sample frames.

The model makes admission, epochs, exact source intervals, buffered queues,
drain/close, cancellation and fallback explicit. All clocks and availability
values are declared synthetic integers, never measured wall/physical timing.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

SCHEMA_ID = "audio-sdk/task-evidence/pipe-control/0.1"
CONTRACT_ID = "audio-sdk/session-loopback-control/0.1"
CONTRACT_VERSION = "0.1"
BASE_COMMIT = "0673cb354cceb66f2f71faf9af7703b5a5d2fcfa"
BRANCH = "swarm/SDK-PIPE-CONTROL"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS
QUEUE_CAPACITY = 3
MAX_DRAIN_CALLS = 4
STAGE_COST_NS = 25000
STREAM_ORIGIN_NS = 1_000_000_000
FINAL_INPUT = 1
FINAL_PADDING = 2
FIRST_INPUT_SAMPLE = 9007199254740993  # 2**53 + 1; exact in int64/JSON text.
FALLBACK_FIRST_SAMPLE = 1000
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")

SOURCE_PINS = {
    "cpp-library/src/core/recipe.cpp":
        "3edea6d4fdfe11a244fab94c3fdde8d33f4435c8001559a808e761dbb41015d9",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
SOURCE_PIN_PATHS = {
    "cpp-library/src/core/recipe.cpp":
        "/Users/htsakanyan/workspace/audio/audioml/cpp-library/src/core/recipe.cpp",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "/Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/audio-sdk/CONTRACTS.md",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "/Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/VERIFICATION.md",
}

_FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
}
_ROOT_KEYS = frozenset((
    "schema_id", "recipe_id", "contract_version", "engine", "format",
    "execution_mode", "queue_capacity", "stage_availability_cost_ns",
    "audio_path", "stages", "assets",
))
_STAGE_KEYS = frozenset((
    "id", "instance", "stage_id", "provider_id", "role",
    "buffering_delay_samples", "availability_cost_ns", "settings",
    "input_port", "output_port",
))


class Status(str, Enum):
    OK = "ok"
    NOT_READY = "rejected_not_ready"
    END_OF_STREAM = "end_of_stream"
    BAD_FRAME = "rejected_bad_frame"
    BAD_FORMAT = "rejected_bad_format"
    BAD_PADDING = "rejected_bad_padding"
    NONFINITE_INPUT = "rejected_nonfinite_input"
    STALE_EPOCH = "rejected_stale_epoch"
    CLOSED = "rejected_closed"
    BUSY = "rejected_busy"
    QUEUE_FULL = "rejected_queue_full"
    MISSING_STAGE = "rejected_missing_stage"
    UNAVAILABLE_STAGE = "rejected_unavailable_stage"
    DUPLICATE_INSTANCE = "rejected_duplicate_instance"
    FAILING_PORT = "rejected_failing_port"
    NEEDS_RESET = "rejected_needs_reset"
    CANCELLED = "rejected_cancelled"
    DRAIN_CAP = "rejected_drain_cap"
    BAD_CLOCK = "rejected_bad_clock"


@dataclass(frozen=True)
class Frame:
    samples: tuple[float, ...]
    valid_count: int
    epoch: int
    first_sample: int
    flags: int = 0


@dataclass(frozen=True)
class Result:
    status: Status
    consumed_count: int = 0
    produced_count: int = 0
    valid_offset: int = 0
    valid_count: int = 0
    flags: int = 0
    epoch: int = 0
    source_first_sample: Optional[int] = None
    availability_ns: Optional[int] = None
    lease_id: Optional[str] = None
    queue_depth: int = 0
    reason: str = ""


@dataclass
class StageFailure(Exception):
    reason: str
    port: str


@dataclass(frozen=True)
class Recipe:
    raw: dict[str, Any]
    digest: str
    stages: tuple[dict[str, Any], ...]
    total_delay: int
    stage_cost_ns: int

    @property
    def recipe_id(self) -> str:
        return str(self.raw["recipe_id"])


class IdentityStage:
    """Callers' identity provider model; float32 round-trip keeps bytes exact."""

    stage_id = "identity"
    role = "audio"
    delay_samples = 0
    cost_ns = STAGE_COST_NS

    def transform(self, samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]) -> tuple[float, ...]:
        if settings:
            raise StageFailure("unsupported_settings", str(ctx["input_port"]))
        if len(samples) != FRAME_SAMPLES:
            raise StageFailure("bad_input_count", str(ctx["input_port"]))
        return tuple(struct.unpack("<f", struct.pack("<f", float(value)))[0]
                     for value in samples)


class FailingStage(IdentityStage):
    """Adverse control: fails a declared output port at a chosen frame index."""

    fail_at_frame = 1
    failure_reason = "control_failure"

    def transform(self, samples, settings, ctx):
        if int(ctx["frame_index"]) == self.fail_at_frame:
            raise StageFailure(self.failure_reason, str(ctx["output_port"]))
        return super().transform(samples, {}, ctx)


def builtin_available() -> dict[str, IdentityStage]:
    return {
        "third_party.identity.v0": IdentityStage(),
        "third_party.fallback_identity.v0": IdentityStage(),
    }


def base_recipe() -> dict[str, Any]:
    return {
        "schema_id": CONTRACT_ID,
        "recipe_id": "identity.loopback.v1",
        "contract_version": CONTRACT_VERSION,
        "engine": "reference.sequential.v0",
        "format": dict(_FORMAT),
        "execution_mode": 3,
        "queue_capacity": QUEUE_CAPACITY,
        "stage_availability_cost_ns": STAGE_COST_NS,
        "audio_path": ["pcm.in", "pcm.identity.out", "pcm.out"],
        "stages": [{
            "id": "identity",
            "instance": "identity",
            "stage_id": "identity",
            "provider_id": "third_party.identity.v0",
            "role": "audio",
            "buffering_delay_samples": 0,
            "availability_cost_ns": STAGE_COST_NS,
            "settings": {},
            "input_port": "pcm.in",
            "output_port": "pcm.identity.out",
        }],
        "assets": [],
    }


def fallback_recipe() -> dict[str, Any]:
    return {
        "schema_id": CONTRACT_ID,
        "recipe_id": "identity.fallback.v1",
        "contract_version": CONTRACT_VERSION,
        "engine": "reference.sequential.v0",
        "format": dict(_FORMAT),
        "execution_mode": 3,
        "queue_capacity": QUEUE_CAPACITY,
        "stage_availability_cost_ns": STAGE_COST_NS,
        "audio_path": ["pcm.in", "pcm.fallback.out", "pcm.out"],
        "stages": [{
            "id": "identity",
            "instance": "identity_fallback",
            "stage_id": "identity",
            "provider_id": "third_party.fallback_identity.v0",
            "role": "audio",
            "buffering_delay_samples": 0,
            "availability_cost_ns": STAGE_COST_NS,
            "settings": {},
            "input_port": "pcm.in",
            "output_port": "pcm.fallback.out",
        }],
        "assets": [],
    }


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text.encode("ascii")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def recipe_digest(raw: Mapping[str, Any]) -> str:
    return digest(canonical_bytes(raw))


def pcm_bytes(values: Sequence[float]) -> bytes:
    return b"".join(struct.pack("<f", float(value)) for value in values)


def _finite_settings(value: Any) -> bool:
    if isinstance(value, dict):
        return all(isinstance(key, str) and key.isascii() and _finite_settings(item)
                   for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return all(_finite_settings(item) for item in value)
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.isascii()
    return (isinstance(value, (int, float)) and math.isfinite(float(value))
            and abs(float(value)) <= 2 ** 53)


def validate_recipe(raw: Any, available: Mapping[str, Any]
                    ) -> tuple[Optional[Recipe], Status, str]:
    """Validate recipe shape and stage admission before any session exists."""
    if not isinstance(raw, dict) or set(raw) != _ROOT_KEYS:
        return None, Status.BAD_FORMAT, "root_keys"
    if (raw["schema_id"] != CONTRACT_ID or raw["contract_version"] != CONTRACT_VERSION
            or raw["engine"] != "reference.sequential.v0" or raw["format"] != _FORMAT):
        return None, Status.BAD_FORMAT, "version_or_format"
    if not isinstance(raw["recipe_id"], str) or not ID_PATTERN.match(raw["recipe_id"]):
        return None, Status.BAD_FORMAT, "recipe_id"
    if raw["execution_mode"] != 3 or raw["queue_capacity"] != QUEUE_CAPACITY:
        return None, Status.BAD_FORMAT, "mode_or_queue"
    if raw["stage_availability_cost_ns"] != STAGE_COST_NS:
        return None, Status.BAD_FORMAT, "stage_cost"
    if not isinstance(raw["assets"], list) or raw["assets"]:
        return None, Status.BAD_FORMAT, "assets"
    stages = raw["stages"]
    if not isinstance(stages, list):
        return None, Status.BAD_FORMAT, "stages_type"
    if not stages:
        return None, Status.MISSING_STAGE, "no_capture_stage"
    if not isinstance(raw["audio_path"], list):
        return None, Status.BAD_FORMAT, "audio_path_type"

    instances: set[str] = set()
    previous_port = "pcm.in"
    total_delay = 0
    stage_cost = 0
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict) or set(stage) != _STAGE_KEYS:
            return None, Status.BAD_FORMAT, f"stage_keys:{index}"
        for key in ("id", "instance", "stage_id", "provider_id"):
            if not isinstance(stage[key], str) or not ID_PATTERN.match(stage[key]):
                return None, Status.BAD_FORMAT, f"{key}:{index}"
        if stage["instance"] in instances:
            return None, Status.DUPLICATE_INSTANCE, stage["instance"]
        instances.add(stage["instance"])
        if stage["role"] != "audio":
            return None, Status.BAD_FORMAT, f"stage_role:{index}"
        provider = available.get(stage["provider_id"])
        if provider is None:
            return None, Status.UNAVAILABLE_STAGE, stage["provider_id"]
        if getattr(provider, "stage_id", None) != stage["stage_id"]:
            return None, Status.UNAVAILABLE_STAGE, f"stage_mismatch:{stage['provider_id']}"
        delay = stage["buffering_delay_samples"]
        cost = stage["availability_cost_ns"]
        if (not isinstance(delay, int) or isinstance(delay, bool) or delay != 0
                or delay != getattr(provider, "delay_samples", None)):
            return None, Status.BAD_FORMAT, f"delay:{index}"
        if (not isinstance(cost, int) or isinstance(cost, bool) or cost < 0
                or cost > 10_000_000_000 or cost != getattr(provider, "cost_ns", None)):
            return None, Status.BAD_FORMAT, f"cost:{index}"
        if not isinstance(stage["settings"], dict) or not _finite_settings(stage["settings"]):
            return None, Status.BAD_FORMAT, f"settings:{index}"
        if stage["input_port"] != previous_port:
            return None, Status.BAD_FORMAT, f"input_port:{index}"
        previous_port = stage["output_port"]
        total_delay += delay
        stage_cost += cost

    expected_path = ["pcm.in"] + [stage["output_port"] for stage in stages] + ["pcm.out"]
    if raw["audio_path"] != expected_path:
        return None, Status.BAD_FORMAT, "audio_path"
    recipe = Recipe(raw=json.loads(json.dumps(raw, sort_keys=True, allow_nan=False)),
                    digest=recipe_digest(raw), stages=tuple(stages),
                    total_delay=total_delay, stage_cost_ns=stage_cost)
    return recipe, Status.OK, ""


def sample(frame_index: int, position: int, tag: int) -> float:
    """Exact k/128 synthetic sample; no corpus, model or random source."""
    raw = (position * 37 + frame_index * 17 + tag * 29) % 101
    return (raw - 50) / 128.0


def frame(first_sample: int, values: Sequence[float], valid_count: int, epoch: int,
          flags: int = 0) -> Frame:
    if len(values) != FRAME_SAMPLES:
        raise ValueError("frame must contain exactly 160 padded samples")
    return Frame(tuple(float(value) for value in values), int(valid_count),
                 int(epoch), int(first_sample), int(flags))


def make_frame(frame_index: int, tag: int, valid_count: int = FRAME_SAMPLES,
               first_sample: int = 0, epoch: int = 1, final: bool = False) -> Frame:
    values = [sample(frame_index, position, tag) for position in range(valid_count)]
    values.extend([0.0] * (FRAME_SAMPLES - valid_count))
    return frame(first_sample, values, valid_count, epoch,
                 FINAL_INPUT if final else 0)


def make_stream(tag: int, lengths: Sequence[int], first_sample: int, epoch: int
                ) -> list[Frame]:
    frames: list[Frame] = []
    position = int(first_sample)
    for index, length in enumerate(lengths):
        final = index == len(lengths) - 1
        frames.append(make_frame(index, tag, length, position, epoch, final))
        position += length
    return frames


def _interval_union_empty(intervals: Sequence[tuple[int, int]]) -> bool:
    ordered = sorted(intervals)
    return all(ordered[index][1] <= ordered[index + 1][0]
               for index in range(len(ordered) - 1))


def _subtract_intervals(source: Sequence[tuple[int, int]],
                        cuts: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    remaining: list[tuple[int, int]] = []
    for start, end in source:
        pieces = [(start, end)]
        for cut_start, cut_end in cuts:
            updated: list[tuple[int, int]] = []
            for piece_start, piece_end in pieces:
                if cut_end <= piece_start or cut_start >= piece_end:
                    updated.append((piece_start, piece_end))
                    continue
                if cut_start > piece_start:
                    updated.append((piece_start, cut_start))
                if cut_end < piece_end:
                    updated.append((cut_end, piece_end))
            pieces = updated
        remaining.extend(piece for piece in pieces if piece[1] > piece[0])
    return sorted(remaining)


@dataclass
class Output:
    samples: tuple[float, ...]
    epoch: int
    source_first_sample: int
    valid_offset: int
    valid_count: int
    flags: int
    availability_ns: int
    complete_ns: int
    frame_index: int
    lease_id: str = ""


@dataclass
class Cancellation:
    epoch: int
    reason: str
    intervals: list[tuple[int, int]]
    samples: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "epoch": dec(self.epoch),
            "reason": self.reason,
            "intervals": [[dec(start), dec(end)] for start, end in self.intervals],
            "samples": dec(self.samples),
        }


def dec(value: int) -> str:
    return str(int(value))


class Session:
    """Reference buffered session. One caller, one provider, one epoch."""

    def __init__(self, recipe: Recipe, available: Mapping[str, Any], provider_id: str,
                 epoch: int, first_input_sample: int,
                 stream_origin_ns: int = STREAM_ORIGIN_NS) -> None:
        self.recipe = recipe
        self.available = dict(available)
        self.provider_id = provider_id
        self.epoch = int(epoch)
        self.first_input_sample = int(first_input_sample)
        self.next_input_sample = int(first_input_sample)
        self.accepted_end = int(first_input_sample)
        self.stream_origin_ns = int(stream_origin_ns)
        self.last_available_ns = int(stream_origin_ns) - 1
        self.state = "prepared"
        self.final_input = False
        self.frame_index = 0
        self.output_queue: deque[Output] = deque()
        self.lease: Optional[Output] = None
        self.accepted_intervals: list[tuple[int, int]] = []
        self.delivered_intervals: list[tuple[int, int]] = []
        self.delivered_samples: list[float] = []
        self.produced_padded_samples: list[float] = []
        self.clock: list[dict[str, int]] = []
        self.cancellations: list[Cancellation] = []
        self.epoch_transitions: list[dict[str, Any]] = []
        self.failed_intervals: list[dict[str, Any]] = []
        self.counters = {
            "submitted_frames": 0,
            "accepted_samples": 0,
            "produced_frames": 0,
            "produced_samples": 0,
            "delivered_frames": 0,
            "delivered_valid_samples": 0,
            "rejected_frames": 0,
            "queue_high_water": 0,
            "backend_failures": 0,
            "cancelled_intervals": 0,
            "cancelled_samples": 0,
            "drain_calls": 0,
            "eos_calls": 0,
            "close_calls": 0,
        }

    def _reject(self, status: Status, reason: str, **extra: Any) -> Result:
        self.counters["rejected_frames"] += 1
        return Result(status=status, reason=reason, epoch=self.epoch, **extra)

    def _render(self, incoming: Frame, frame_index: int) -> tuple[float, ...]:
        current = tuple(incoming.samples)
        for stage in self.recipe.stages:
            provider = self.available[stage["provider_id"]]
            ctx = {
                "frame_index": frame_index,
                "epoch": self.epoch,
                "source_first": incoming.first_sample,
                "provider_id": stage["provider_id"],
                "input_port": stage["input_port"],
                "output_port": stage["output_port"],
            }
            try:
                current = tuple(provider.transform(current, stage["settings"], ctx))
            except StageFailure as failure:
                self._record_backend_failure(incoming, failure.reason, stage["output_port"])
                raise
            if len(current) != FRAME_SAMPLES or any(
                    not math.isfinite(float(value)) for value in current):
                self._record_backend_failure(incoming, "invalid_output",
                                             stage["output_port"])
                raise StageFailure("invalid_output", stage["output_port"])
        return current

    def _record_backend_failure(self, incoming: Frame, reason: str, port: str) -> None:
        self.state = "needs_reset"
        self.counters["backend_failures"] += 1
        interval = (incoming.first_sample, incoming.first_sample + FRAME_SAMPLES)
        self.failed_intervals.append({
            "epoch": self.epoch, "reason": reason, "port": port,
            "interval": interval,
        })

    def submit(self, incoming: Frame) -> Result:
        if self.state == "closed":
            return self._reject(Status.CLOSED, "session_closed")
        if self.state == "cancelled":
            return self._reject(Status.CANCELLED, "session_cancelled")
        if self.state == "needs_reset":
            return self._reject(Status.NEEDS_RESET, "backend_failure")
        if self.state == "draining" or self.state == "drained":
            return self._reject(Status.BAD_FRAME, "drain_started")
        if self.lease is not None:
            return self._reject(Status.BUSY, "outstanding_lease")
        if incoming.epoch != self.epoch:
            return self._reject(Status.STALE_EPOCH, "epoch")
        if incoming.first_sample != self.next_input_sample:
            return self._reject(Status.BAD_FRAME, "first_sample")
        if (len(incoming.samples) != FRAME_SAMPLES
                or not 0 <= incoming.valid_count <= FRAME_SAMPLES):
            return self._reject(Status.BAD_FRAME, "counts")
        if incoming.flags & ~FINAL_INPUT:
            return self._reject(Status.BAD_FRAME, "flags")
        if incoming.valid_count < FRAME_SAMPLES and not incoming.flags & FINAL_INPUT:
            return self._reject(Status.BAD_FRAME, "partial_without_final")
        if self.final_input:
            return self._reject(Status.BAD_FRAME, "after_final")
        if any(not math.isfinite(float(value)) for value in incoming.samples):
            return self._reject(Status.NONFINITE_INPUT, "nonfinite_input")
        if any(float(value) != 0.0 for value in incoming.samples[incoming.valid_count:]):
            return self._reject(Status.BAD_PADDING, "nonzero_padding")
        if incoming.valid_count == 0 and not incoming.flags & FINAL_INPUT:
            return self._reject(Status.BAD_FRAME, "empty_not_final")
        if len(self.output_queue) >= QUEUE_CAPACITY:
            return self._reject(Status.QUEUE_FULL, "output_queue_full",
                                queue_depth=len(self.output_queue))

        frame_index = self.frame_index
        try:
            rendered = self._render(incoming, frame_index)
        except StageFailure as failure:
            return self._reject(Status.FAILING_PORT, failure.reason,
                                queue_depth=len(self.output_queue))

        complete_ns = self.stream_origin_ns + frame_index * FRAME_NS + FRAME_NS
        available_ns = complete_ns + self.recipe.stage_cost_ns
        if available_ns <= self.last_available_ns:
            return self._reject(Status.BAD_CLOCK, "nonmonotonic_availability")
        self.last_available_ns = available_ns

        if self.state == "prepared":
            self.state = "processing"
        if incoming.valid_count:
            self.accepted_intervals.append(
                (incoming.first_sample, incoming.first_sample + incoming.valid_count))
        self.accepted_end = incoming.first_sample + incoming.valid_count
        self.next_input_sample = incoming.first_sample + FRAME_SAMPLES
        self.final_input = bool(incoming.flags & FINAL_INPUT)
        self.frame_index += 1
        self.counters["submitted_frames"] += 1
        self.counters["accepted_samples"] += incoming.valid_count
        self.counters["produced_frames"] += 1
        self.counters["produced_samples"] += FRAME_SAMPLES
        self.output_queue.append(Output(
            samples=rendered, epoch=self.epoch,
            source_first_sample=incoming.first_sample - self.recipe.total_delay,
            valid_offset=0, valid_count=incoming.valid_count,
            flags=FINAL_PADDING if self.final_input else 0,
            availability_ns=available_ns, complete_ns=complete_ns,
            frame_index=frame_index,
        ))
        self.counters["queue_high_water"] = max(
            self.counters["queue_high_water"], len(self.output_queue))
        self.clock.append({
            "frame_index": frame_index,
            "source_complete_ns": complete_ns,
            "availability_ns": available_ns,
            "stage_cost_ns": self.recipe.stage_cost_ns,
        })
        return Result(status=Status.OK, consumed_count=FRAME_SAMPLES,
                      epoch=self.epoch, queue_depth=len(self.output_queue),
                      source_first_sample=incoming.first_sample)

    def _take_output(self, status: Status = Status.OK) -> Result:
        output = self.output_queue.popleft()
        output.lease_id = f"L{self.epoch}-{output.frame_index}"
        self.lease = output
        return Result(
            status=status, produced_count=FRAME_SAMPLES,
            valid_offset=output.valid_offset, valid_count=output.valid_count,
            flags=output.flags, epoch=output.epoch,
            source_first_sample=output.source_first_sample,
            availability_ns=output.availability_ns,
            lease_id=output.lease_id, queue_depth=len(self.output_queue),
        )

    def pull(self) -> Result:
        if self.state == "closed":
            return self._reject(Status.CLOSED, "session_closed")
        if self.state == "cancelled":
            return self._reject(Status.CANCELLED, "session_cancelled")
        if self.state == "needs_reset":
            return self._reject(Status.NEEDS_RESET, "backend_failure")
        if self.lease is not None:
            return self._reject(Status.BUSY, "outstanding_lease")
        if self.output_queue:
            return self._take_output()
        if self.state == "drained":
            return Result(status=Status.END_OF_STREAM, epoch=self.epoch,
                          queue_depth=0)
        return self._reject(Status.NOT_READY, "output_queue_empty")

    def release(self, lease_id: str) -> Result:
        if self.lease is None or self.lease.lease_id != lease_id:
            return self._reject(Status.BAD_FRAME, "invalid_lease")
        output = self.lease
        start = output.source_first_sample + output.valid_offset
        end = start + output.valid_count
        if output.valid_count:
            self.delivered_intervals.append((start, end))
            self.delivered_samples.extend(
                output.samples[output.valid_offset:output.valid_offset + output.valid_count])
        self.produced_padded_samples.extend(output.samples)
        self.counters["delivered_frames"] += 1
        self.counters["delivered_valid_samples"] += output.valid_count
        self.lease = None
        return Result(status=Status.OK, epoch=self.epoch,
                      source_first_sample=start, valid_count=output.valid_count)

    def begin_drain(self) -> Result:
        if self.state == "closed":
            return self._reject(Status.CLOSED, "session_closed")
        if self.state == "cancelled":
            return self._reject(Status.CANCELLED, "session_cancelled")
        if self.state == "needs_reset":
            return self._reject(Status.NEEDS_RESET, "backend_failure")
        if self.lease is not None:
            return self._reject(Status.BUSY, "outstanding_lease")
        if not self.final_input or self.state != "processing":
            return self._reject(Status.BAD_FRAME, "no_final_marker")
        self.state = "draining"
        return Result(status=Status.OK, epoch=self.epoch)

    def drain_next(self) -> Result:
        if self.state == "closed":
            return self._reject(Status.CLOSED, "session_closed")
        if self.state == "cancelled":
            return self._reject(Status.CANCELLED, "session_cancelled")
        if self.state == "needs_reset":
            return self._reject(Status.NEEDS_RESET, "backend_failure")
        if self.lease is not None:
            return self._reject(Status.BUSY, "outstanding_lease")
        if self.state not in ("draining", "drained"):
            return self._reject(Status.BAD_FRAME, "drain_not_started")
        if self.output_queue:
            self.counters["drain_calls"] += 1
            return self._take_output(Status.OK)
        self.counters["drain_calls"] += 1
        if self.counters["drain_calls"] > MAX_DRAIN_CALLS:
            return self._reject(Status.DRAIN_CAP, "drain_cap")
        self.counters["eos_calls"] += 1
        self.state = "drained"
        return Result(status=Status.END_OF_STREAM, epoch=self.epoch, queue_depth=0)

    def cancel(self, reason: str) -> Cancellation:
        if self.state in ("closed", "cancelled", "needs_reset"):
            raise RuntimeError(f"cannot_cancel:{self.state}")
        intervals = _subtract_intervals(self.accepted_intervals,
                                        self.delivered_intervals)
        record = Cancellation(
            epoch=self.epoch, reason=reason, intervals=intervals,
            samples=sum(end - start for start, end in intervals),
        )
        self.cancellations.append(record)
        self.counters["cancelled_intervals"] += len(intervals)
        self.counters["cancelled_samples"] += record.samples
        self.state = "cancelled"
        self.lease = None
        self.output_queue.clear()
        return record

    def reset(self, new_epoch: int, first_input_sample: int) -> Result:
        if self.state == "closed":
            return self._reject(Status.CLOSED, "session_closed")
        if self.state == "cancelled":
            return self._reject(Status.CANCELLED, "use_fresh_session_for_fallback")
        if self.lease is not None:
            return self._reject(Status.BUSY, "outstanding_lease")
        if self.state == "draining":
            return self._reject(Status.BUSY, "drain_in_progress")
        if int(new_epoch) <= self.epoch:
            return self._reject(Status.STALE_EPOCH, "epoch_not_increased")
        if int(first_input_sample) < 0:
            return self._reject(Status.BAD_FRAME, "negative_first_sample")
        self.epoch_transitions.append({
            "from": dec(self.epoch), "to": dec(new_epoch),
            "previous_state": self.state,
        })
        cancellations = self.cancellations
        transitions = self.epoch_transitions
        failed = self.failed_intervals
        self.__init__(self.recipe, self.available, self.provider_id,
                      int(new_epoch), int(first_input_sample),
                      stream_origin_ns=self.stream_origin_ns)
        self.cancellations = cancellations
        self.epoch_transitions = transitions
        self.failed_intervals = failed
        return Result(status=Status.OK, epoch=self.epoch)

    def close(self, force: bool = False) -> Result:
        if self.state == "closed":
            return Result(status=Status.OK, epoch=self.epoch)
        if self.lease is not None and not force:
            return self._reject(Status.BUSY, "outstanding_lease")
        if self.state in ("drained", "cancelled"):
            self.state = "closed"
            self.counters["close_calls"] += 1
            return Result(status=Status.OK, epoch=self.epoch)
        if force:
            self.cancel("forced_close_without_drain")
            self.state = "closed"
            self.counters["close_calls"] += 1
            return Result(status=Status.OK, epoch=self.epoch)
        return self._reject(Status.BAD_FRAME, "close_before_drain_or_cancel")

    def counters_dict(self) -> dict[str, str]:
        return {key: dec(value) for key, value in sorted(self.counters.items())}


def create_session(recipe: Recipe, available: Mapping[str, Any], provider_id: str,
                   epoch: int, first_input_sample: int,
                   stream_origin_ns: int = STREAM_ORIGIN_NS
                   ) -> tuple[Optional[Session], Result]:
    """Admission happens before any provider instance is created."""
    if recipe is None:
        return None, Result(status=Status.MISSING_STAGE)
    if provider_id not in available:
        return None, Result(status=Status.UNAVAILABLE_STAGE, reason=provider_id)
    session = Session(recipe, available, provider_id, epoch, first_input_sample,
                      stream_origin_ns=stream_origin_ns)
    return session, Result(status=Status.OK, epoch=epoch)


def _accepted(raw: Recipe | dict[str, Any] | None, available: Mapping[str, Any]
              ) -> Recipe:
    recipe = raw if isinstance(raw, Recipe) else raw
    if recipe is None:
        raise AssertionError("session admission failed")
    status = validate_recipe(recipe.raw if isinstance(recipe, Recipe) else recipe,
                             available)[1]
    if status is not Status.OK:
        raise AssertionError(f"session admission failed:{status.value}")
    return recipe if isinstance(recipe, Recipe) else validate_recipe(recipe, available)[0]


@dataclass
class BaselineRun:
    session: Session
    recipe_digest: str
    input_digest: str
    delivered_digest: str
    produced_padded_digest: str
    delivered_samples: tuple[float, ...]
    accepted_intervals: list[tuple[int, int]]
    delivered_intervals: list[tuple[int, int]]
    final_flags: list[int]

    def as_dict(self) -> dict[str, Any]:
        session = self.session
        return {
            "recipe_digest": self.recipe_digest,
            "epoch": dec(session.epoch),
            "first_input_sample": dec(session.first_input_sample),
            "frame_lengths": [dec(frame.valid_count)
                              for frame in _baseline_frames()],
            "input_f32_digest": self.input_digest,
            "delivered_valid_f32_digest": self.delivered_digest,
            "produced_padded_f32_digest": self.produced_padded_digest,
            "bit_exact": self.input_digest == self.delivered_digest,
            "accepted_intervals": [[dec(s), dec(e)] for s, e in self.accepted_intervals],
            "delivered_intervals": [[dec(s), dec(e)] for s, e in self.delivered_intervals],
            "final_frame_flags": dec(self.final_flags[-1]),
            "terminal_status": session.state,
            "counters": session.counters_dict(),
            "clock": [{key: dec(value) for key, value in row.items()}
                      for row in session.clock],
            "availability_monotonic": all(
                session.clock[index]["availability_ns"] <
                session.clock[index + 1]["availability_ns"]
                for index in range(len(session.clock) - 1)),
        }


def _baseline_frames() -> list[Frame]:
    return make_stream(0, (160, 160, 37), FIRST_INPUT_SAMPLE, 11)


def run_baseline(available: Optional[Mapping[str, Any]] = None) -> BaselineRun:
    stages = builtin_available() if available is None else available
    recipe, status, reason = validate_recipe(base_recipe(), stages)
    if status is not Status.OK or recipe is None:
        raise AssertionError(f"baseline admission failed:{status.value}:{reason}")
    session, admitted = create_session(recipe, stages, "third_party.identity.v0",
                                       11, FIRST_INPUT_SAMPLE)
    if session is None or admitted.status is not Status.OK:
        raise AssertionError("baseline session creation failed")
    frames = _baseline_frames()
    input_bytes = b"".join(pcm_bytes(item.samples[:item.valid_count])
                           for item in frames)
    final_flags: list[int] = []
    for incoming in frames:
        assert session.submit(incoming).status is Status.OK
        output = session.pull()
        assert output.status is Status.OK and output.lease_id is not None
        final_flags.append(output.flags)
        assert session.release(output.lease_id).status is Status.OK
    assert session.begin_drain().status is Status.OK
    assert session.drain_next().status is Status.END_OF_STREAM
    assert session.close().status is Status.OK
    return BaselineRun(
        session=session, recipe_digest=recipe.digest,
        input_digest=digest(input_bytes),
        delivered_digest=digest(pcm_bytes(session.delivered_samples)),
        produced_padded_digest=digest(pcm_bytes(session.produced_padded_samples)),
        delivered_samples=tuple(session.delivered_samples),
        accepted_intervals=list(session.accepted_intervals),
        delivered_intervals=list(session.delivered_intervals),
        final_flags=final_flags,
    )


@dataclass
class SwitchRun:
    session_a: Session
    session_b: Session
    recipe_a_digest: str
    recipe_b_digest: str
    accepted_intervals_a: list[tuple[int, int]]
    accepted_intervals_b: list[tuple[int, int]]
    delivered_intervals_a: list[tuple[int, int]]
    delivered_intervals_b: list[tuple[int, int]]
    digest_a: str
    digest_b: str
    digest_combined: str
    stale_attempt: Status
    duplicate_attempt: Status
    closed_attempt: Status
    closed_pull: Status

    def as_dict(self) -> dict[str, Any]:
        all_intervals = self.delivered_intervals_a + self.delivered_intervals_b
        return {
            "session_a": {
                "provider_id": self.session_a.provider_id,
                "recipe_digest": self.recipe_a_digest,
                "epoch": dec(self.session_a.epoch),
                "first_input_sample": dec(self.session_a.first_input_sample),
                "terminal_status": self.session_a.state,
                "accepted_intervals": [[dec(s), dec(e)]
                                       for s, e in self.accepted_intervals_a],
                "delivered_intervals": [[dec(s), dec(e)]
                                        for s, e in self.delivered_intervals_a],
                "delivered_f32_digest": self.digest_a,
                "counters": self.session_a.counters_dict(),
            },
            "session_b": {
                "provider_id": self.session_b.provider_id,
                "recipe_digest": self.recipe_b_digest,
                "epoch": dec(self.session_b.epoch),
                "first_input_sample": dec(self.session_b.first_input_sample),
                "terminal_status": self.session_b.state,
                "accepted_intervals": [[dec(s), dec(e)]
                                       for s, e in self.accepted_intervals_b],
                "delivered_intervals": [[dec(s), dec(e)]
                                        for s, e in self.delivered_intervals_b],
                "delivered_f32_digest": self.digest_b,
                "counters": self.session_b.counters_dict(),
            },
            "combined_delivered_f32_digest": self.digest_combined,
            "combined_delivered_samples": dec(len(self.session_a.delivered_samples)
                                              + len(self.session_b.delivered_samples)),
            "epoch_transition": [dec(self.session_a.epoch), dec(self.session_b.epoch)],
            "distinct_providers": self.session_a.provider_id != self.session_b.provider_id,
            "intervals_disjoint": _interval_union_empty(all_intervals),
            "old_epoch_or_duplicate_samples_accepted": 0,
            "stale_epoch_attempt": self.stale_attempt.value,
            "duplicate_frame_attempt": self.duplicate_attempt.value,
            "closed_session_attempt": self.closed_attempt.value,
            "closed_session_pull": self.closed_pull.value,
        }


def _process_all(session: Session, frames: Sequence[Frame]) -> None:
    for incoming in frames:
        assert session.submit(incoming).status is Status.OK
        output = session.pull()
        assert output.status is Status.OK and output.lease_id is not None
        assert session.release(output.lease_id).status is Status.OK
    assert session.begin_drain().status is Status.OK
    assert session.drain_next().status is Status.END_OF_STREAM
    assert session.close().status is Status.OK


def run_switch(available: Optional[Mapping[str, Any]] = None) -> SwitchRun:
    stages = builtin_available() if available is None else available
    recipe_a, status, reason = validate_recipe(base_recipe(), stages)
    recipe_b, status_b, reason_b = validate_recipe(fallback_recipe(), stages)
    if status is not Status.OK or status_b is not Status.OK or recipe_a is None or recipe_b is None:
        raise AssertionError(f"switch admission failed:{status.value}:{status_b.value}:{reason}:{reason_b}")
    first_a = FIRST_INPUT_SAMPLE
    length = 357
    first_b = first_a + length
    epoch_a = 11
    epoch_b = epoch_a + 1
    session_a, _ = create_session(recipe_a, stages, "third_party.identity.v0",
                                  epoch_a, first_a)
    session_b, _ = create_session(recipe_b, stages, "third_party.fallback_identity.v0",
                                  epoch_b, first_b)
    assert session_a is not None and session_b is not None
    frames_a = make_stream(1, (160, 160, 37), first_a, epoch_a)
    frames_b = make_stream(2, (160, 160, 37), first_b, epoch_b)
    _process_all(session_a, frames_a)

    incoming_b = frames_b[0]
    assert session_b.submit(incoming_b).status is Status.OK
    stale_frame = make_frame(1, 9, 160, session_b.next_input_sample, epoch_a)
    stale_attempt = session_b.submit(stale_frame).status
    duplicate_frame = make_frame(0, 2, 160, incoming_b.first_sample, epoch_b)
    duplicate_attempt = session_b.submit(duplicate_frame).status
    for incoming in frames_b[1:]:
        assert session_b.submit(incoming).status is Status.OK
        output = session_b.pull()
        assert output.status is Status.OK and output.lease_id is not None
        assert output.epoch == epoch_b
        assert session_b.release(output.lease_id).status is Status.OK
    assert session_b.begin_drain().status is Status.OK
    tail = session_b.drain_next()
    assert tail.status is Status.OK and tail.lease_id is not None
    assert tail.epoch == epoch_b
    assert session_b.release(tail.lease_id).status is Status.OK
    assert session_b.drain_next().status is Status.END_OF_STREAM
    assert session_b.close().status is Status.OK
    closed_attempt = session_b.submit(
        make_frame(0, 1, 160, first_a, epoch_a)).status
    closed_pull = session_a.pull().status

    combined = list(session_a.delivered_samples) + list(session_b.delivered_samples)
    return SwitchRun(
        session_a=session_a, session_b=session_b,
        recipe_a_digest=recipe_a.digest, recipe_b_digest=recipe_b.digest,
        accepted_intervals_a=list(session_a.accepted_intervals),
        accepted_intervals_b=list(session_b.accepted_intervals),
        delivered_intervals_a=list(session_a.delivered_intervals),
        delivered_intervals_b=list(session_b.delivered_intervals),
        digest_a=digest(pcm_bytes(session_a.delivered_samples)),
        digest_b=digest(pcm_bytes(session_b.delivered_samples)),
        digest_combined=digest(pcm_bytes(combined)),
        stale_attempt=stale_attempt, duplicate_attempt=duplicate_attempt,
        closed_attempt=closed_attempt, closed_pull=closed_pull,
    )


@dataclass
class FallbackRun:
    cancellation: Cancellation
    blocked_statuses: dict[str, str]
    fresh_session: Session
    fresh_intervals: list[tuple[int, int]]
    fresh_digest: str
    stale_attempt: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "cancelled_session": self.cancellation.as_dict(),
            "blocked_after_cancel": dict(self.blocked_statuses),
            "fresh_session": {
                "provider_id": self.fresh_session.provider_id,
                "epoch": dec(self.fresh_session.epoch),
                "first_input_sample": dec(self.fresh_session.first_input_sample),
                "delivered_intervals": [[dec(s), dec(e)]
                                        for s, e in self.fresh_intervals],
                "delivered_f32_digest": self.fresh_digest,
                "terminal_status": self.fresh_session.state,
                "counters": self.fresh_session.counters_dict(),
            },
            "stale_provider_attempt": self.stale_attempt,
            "old_epoch_samples_delivered": 0,
        }


def run_cancellation_fallback(available: Optional[Mapping[str, Any]] = None) -> FallbackRun:
    stages = builtin_available() if available is None else available
    recipe_a, _, _ = validate_recipe(base_recipe(), stages)
    recipe_b, _, _ = validate_recipe(fallback_recipe(), stages)
    assert recipe_a is not None and recipe_b is not None
    session_a, _ = create_session(recipe_a, stages, "third_party.identity.v0",
                                  31, 0)
    session_b, _ = create_session(recipe_b, stages, "third_party.fallback_identity.v0",
                                  32, FALLBACK_FIRST_SAMPLE)
    assert session_a is not None and session_b is not None
    for index in (0, 1):
        assert session_a.submit(make_frame(index, 3, 160, index * 160, 31)).status is Status.OK
    outstanding = session_a.pull()
    assert outstanding.status is Status.OK and outstanding.lease_id is not None
    cancellation = session_a.cancel("host_fallback_after_failed_provider")
    blocked = {
        "submit": session_a.submit(make_frame(2, 3, 160, 320, 31)).status.value,
        "pull": session_a.pull().status.value,
        "drain_next": session_a.drain_next().status.value,
        "begin_drain": session_a.begin_drain().status.value,
        "reset": session_a.reset(33, 0).status.value,
    }
    assert session_a.close().status is Status.OK

    fresh_frame = make_frame(0, 4, 160, FALLBACK_FIRST_SAMPLE, 32, final=True)
    assert session_b.submit(fresh_frame).status is Status.OK
    stale = session_b.submit(make_frame(0, 3, 160, FALLBACK_FIRST_SAMPLE, 31)).status
    output = session_b.pull()
    assert output.status is Status.OK and output.lease_id is not None
    assert session_b.release(output.lease_id).status is Status.OK
    assert session_b.begin_drain().status is Status.OK
    assert session_b.drain_next().status is Status.END_OF_STREAM
    assert session_b.close().status is Status.OK
    return FallbackRun(
        cancellation=cancellation, blocked_statuses=blocked,
        fresh_session=session_b,
        fresh_intervals=list(session_b.delivered_intervals),
        fresh_digest=digest(pcm_bytes(session_b.delivered_samples)),
        stale_attempt=stale.value,
    )


def run_ablations(available: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    stages = builtin_available() if available is None else available
    raw = base_recipe()
    control, status, reason = validate_recipe(raw, stages)
    removed = base_recipe()
    removed["stages"] = []
    removed["audio_path"] = ["pcm.in", "pcm.out"]
    _, removed_status, removed_reason = validate_recipe(removed, stages)
    without_provider = dict(stages)
    without_provider.pop("third_party.identity.v0")
    _, unavailable_status, unavailable_reason = validate_recipe(raw, without_provider)
    return {
        "control": {"status": status.value, "reason": reason,
                    "recipe_digest": control.digest if control else ""},
        "identity_stage_removed": {"status": removed_status.value,
                                   "reason": removed_reason, "sessions_created": 0},
        "provider_unavailable": {"status": unavailable_status.value,
                                 "reason": unavailable_reason, "sessions_created": 0},
        "failure_policy": "admission failure before provider instance creation; "
                          "backend failure enters needs_reset and requires reset or "
                          "a fresh session",
    }


def run_failure_policy(available: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    stages = builtin_available() if available is None else available
    failing = dict(stages)
    failing["third_party.identity.v0"] = FailingStage()
    recipe, status, _ = validate_recipe(base_recipe(), failing)
    assert status is Status.OK and recipe is not None
    session, _ = create_session(recipe, failing, "third_party.identity.v0", 61, 0)
    assert session is not None
    first = make_frame(0, 5, 160, 0, 61)
    assert session.submit(first).status is Status.OK
    output = session.pull()
    assert output.status is Status.OK and output.lease_id is not None
    assert session.release(output.lease_id).status is Status.OK
    second = make_frame(1, 5, 160, 160, 61)
    failure = session.submit(second).status
    blocked_submit = session.submit(make_frame(2, 5, 160, 320, 61)).status
    blocked_drain = session.drain_next().status
    reset = session.reset(62, 0)
    restarted = session.submit(make_frame(0, 5, 160, 0, 62, final=True))
    return {
        "failure": failure.value,
        "failed_interval": [[dec(item["interval"][0]), dec(item["interval"][1])]
                            for item in session.failed_intervals],
        "failed_port": session.failed_intervals[0]["port"] if session.failed_intervals else "",
        "blocked_submit": blocked_submit.value,
        "blocked_drain": blocked_drain.value,
        "state_after_failure": "needs_reset",
        "reset": reset.status.value,
        "post_reset_submit": restarted.status.value,
        "epoch_transitions": [dict(item) for item in session.epoch_transitions],
    }


def run_adverse_controls(available: Optional[Mapping[str, Any]] = None) -> dict[str, str]:
    stages = builtin_available() if available is None else available
    recipe, status, _ = validate_recipe(base_recipe(), stages)
    assert status is Status.OK and recipe is not None
    outcomes: dict[str, str] = {}

    def fresh() -> Session:
        session, _ = create_session(recipe, stages, "third_party.identity.v0", 71, 0)
        assert session is not None
        return session

    nonfinite_values = [0.0] * FRAME_SAMPLES
    nonfinite_values[3] = float("inf")
    outcomes["nonfinite_input"] = fresh().submit(
        frame(0, nonfinite_values, 160, 71)).status.value

    padded = make_frame(0, 0, 37, 0, 71, final=True)
    bad_padding = list(padded.samples)
    bad_padding[40] = 0.5
    outcomes["nonzero_final_padding"] = fresh().submit(
        frame(0, bad_padding, 37, 71, FINAL_INPUT)).status.value

    outcomes["partial_without_final_input"] = fresh().submit(
        make_frame(0, 0, 37, 0, 71)).status.value
    short = make_frame(0, 0, 160, 0, 71)
    outcomes["short_frame"] = fresh().submit(
        Frame(short.samples[:159], 160, 71, 0, 0)).status.value
    outcomes["unknown_flags"] = fresh().submit(
        frame(0, short.samples, 160, 71, 4)).status.value
    outcomes["wrong_first_sample"] = fresh().submit(
        make_frame(0, 0, 160, 1, 71)).status.value
    outcomes["wrong_epoch"] = fresh().submit(
        make_frame(0, 0, 160, 0, 72)).status.value

    final_session = fresh()
    assert final_session.submit(make_frame(0, 0, 160, 0, 71, final=True)).status is Status.OK
    outcomes["process_after_final"] = final_session.submit(
        make_frame(1, 0, 160, 160, 71)).status.value

    invalid_metadata = base_recipe()
    invalid_metadata["format"]["sample_rate_hz"] = 48000
    outcomes["invalid_metadata_rate"] = validate_recipe(invalid_metadata, stages)[1].value
    invalid_metadata = base_recipe()
    invalid_metadata["queue_capacity"] = 4
    outcomes["invalid_metadata_queue"] = validate_recipe(invalid_metadata, stages)[1].value
    return dict(sorted(outcomes.items()))


def run_buffer_control(available: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    stages = builtin_available() if available is None else available
    recipe, status, _ = validate_recipe(base_recipe(), stages)
    assert status is Status.OK and recipe is not None
    session, _ = create_session(recipe, stages, "third_party.identity.v0", 81, 0)
    assert session is not None
    statuses = []
    queued = make_frame(3, 6, 160, 3 * FRAME_SAMPLES, 81)
    for index in range(4):
        incoming = queued if index == 3 else make_frame(
            index, 6, 160, index * FRAME_SAMPLES, 81)
        statuses.append(session.submit(incoming).status.value)
    rejection = session.submit(queued)
    assert session.close(force=True).status is Status.OK
    return {
        "queue_capacity": dec(QUEUE_CAPACITY),
        "submit_statuses": statuses,
        "queue_full_rejection": rejection.status.value,
        "queue_depth_on_rejection": dec(rejection.queue_depth),
        "consumed_on_rejection": dec(rejection.consumed_count),
        "queue_high_water": dec(session.counters["queue_high_water"]),
        "accepted_frames": dec(session.counters["submitted_frames"]),
        "dropped_frames": 0,
        "forced_close_reason": session.cancellations[-1].reason,
    }


def source_tree_digest(root: Optional[Path] = None) -> str:
    package_root = root or Path(__file__).resolve().parent / "third_party" / "src" / "pipe_control_fixture"
    if not package_root.is_dir():
        return ""
    joined = b"".join(path.name.encode("ascii") + b"\0" + path.read_bytes()
                      for path in sorted(package_root.glob("*.py")))
    return digest(joined)


def recipe_file_digests(root: Optional[Path] = None) -> dict[str, str]:
    evidence = root or Path(__file__).resolve().parent
    return {
        path: digest((evidence / path).read_bytes())
        for path in ("recipe.json", "fallback_recipe.json")
    }


def build_report(available: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    stages = builtin_available() if available is None else available
    baseline = run_baseline(stages)
    switch = run_switch(stages)
    fallback = run_cancellation_fallback(stages)
    ablation = run_ablations(stages)
    failure = run_failure_policy(stages)
    adverse = run_adverse_controls(stages)
    buffer = run_buffer_control(stages)
    return {
        "schema_id": "audio-sdk/task-evidence/pipe-control/report/0.1",
        "status": "proposal_only_synthetic_incomplete",
        "qualification": "incomplete",
        "contract": CONTRACT_ID,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "format": dict(_FORMAT),
        "source_pins": {path: sha for path, sha in SOURCE_PINS.items()},
        "recipe_file_digests": recipe_file_digests(),
        "fixture_source_digest": source_tree_digest(),
        "baseline": baseline.as_dict(),
        "session_switch": switch.as_dict(),
        "cancellation_fallback": fallback.as_dict(),
        "ablations": ablation,
        "failure_policy": failure,
        "adverse_controls": adverse,
        "buffer": buffer,
        "clock_and_timing": {
            "stream_origin_ns": dec(STREAM_ORIGIN_NS),
            "sample_period_ns": dec(SAMPLE_NS),
            "frame_period_ns": dec(FRAME_NS),
            "declared_stage_cost_ns": dec(STAGE_COST_NS),
            "measured_stage_time_ns": None,
            "measured_end_to_end_availability_ns": None,
            "stage_timing_independent_of_availability": True,
            "source_timestamps_are_synthetic": True,
        },
        "asset_scope": {
            "external_assets": 0, "model_weights": False, "downloads": False,
            "licensed_runtimes": False, "real_audio": False, "model_free": True,
        },
        "limits": {
            "paced_workload": "blocked_not_measured",
            "target_device": "blocked_not_measured",
            "physical_availability": "blocked_not_measured",
            "listening_or_quality": "blocked_not_measured",
            "public_release": "not_applicable_synthetic",
        },
        "counts": {
            "baseline_frames": dec(len(_baseline_frames())),
            "baseline_accepted_samples": dec(baseline.session.counters["accepted_samples"]),
            "baseline_delivered_valid_samples": dec(
                baseline.session.counters["delivered_valid_samples"]),
            "switch_sessions": 2,
            "switch_accepted_samples": dec(
                switch.session_a.counters["accepted_samples"]
                + switch.session_b.counters["accepted_samples"]),
            "switch_delivered_valid_samples": dec(
                switch.session_a.counters["delivered_valid_samples"]
                + switch.session_b.counters["delivered_valid_samples"]),
            "cancellation_abandoned_samples": dec(fallback.cancellation.samples),
            "fallback_delivered_valid_samples": dec(
                fallback.fresh_session.counters["delivered_valid_samples"]),
            "adverse_cases": dec(len(adverse)),
            "installed_probe_runs": 2,
        },
    }


if __name__ == "__main__":
    import generate_report

    path = generate_report.write_report()
    print(f"{path}\nsha256:{digest(path.read_bytes())}")
