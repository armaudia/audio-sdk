"""Model-free fixture for the proposed duplex reference/clock interface.

The fixture exercises exact rate/drift mapping, explicit missing and
discontinuous references, layout rejection and teardown. It changes no
installed SDK ABI, descriptor, registry or default behavior.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Optional, Sequence

CONTRACT_ID = "audio-sdk/duplex-reference/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62500
LAYOUT_CHANNELS = {
    "mono": 1,
    "stereo_interleaved": 2,
    "quad_interleaved": 4,
}
ROLES = ("render", "capture")


class Status(str, Enum):
    OK = "ok"
    REJECTED_LAYOUT = "rejected_layout"
    REJECTED_RATE = "rejected_rate"
    REJECTED_CLOCK = "rejected_clock"
    REJECTED_GAP = "rejected_gap"
    REJECTED_MISSING = "rejected_missing"
    REJECTED_ROLE = "rejected_role"
    CLOSED = "closed"


@dataclass(frozen=True)
class Layout:
    id: str
    channels: int

    def check(self) -> Optional[Status]:
        if LAYOUT_CHANNELS.get(self.id) != self.channels:
            return Status.REJECTED_LAYOUT
        return None


@dataclass(frozen=True)
class TraceSegment:
    first_sample: int
    channels: tuple[tuple[float, ...], ...]

    @property
    def length(self) -> int:
        return len(self.channels[0]) if self.channels else 0

    @property
    def end_sample(self) -> int:
        return self.first_sample + self.length

    def check(self) -> Optional[Status]:
        if self.first_sample < 0 or self.length < 1:
            return Status.REJECTED_GAP
        if any(len(channel) != self.length for channel in self.channels):
            return Status.REJECTED_LAYOUT
        if any(not math.isfinite(value) for channel in self.channels
               for value in channel):
            return Status.REJECTED_GAP
        return None


@dataclass(frozen=True)
class ReferenceTrace:
    role: str
    layout: Layout
    sample_rate_hz: int
    segments: tuple[TraceSegment, ...]
    clock_drift_ppm: int = 0

    @property
    def end_sample(self) -> int:
        return self.segments[-1].end_sample

    def check(self) -> Optional[Status]:
        if self.role not in ROLES:
            return Status.REJECTED_ROLE
        bad = self.layout.check()
        if bad is not None:
            return bad
        if self.sample_rate_hz < 1:
            return Status.REJECTED_RATE
        if not self.segments:
            return Status.REJECTED_MISSING
        for segment in self.segments:
            bad = segment.check()
            if bad is not None:
                return bad
            if len(segment.channels) != self.layout.channels:
                return Status.REJECTED_LAYOUT
        for previous, current in zip(self.segments, self.segments[1:]):
            if current.first_sample != previous.end_sample:
                return Status.REJECTED_GAP
        return None


class DuplexSession:
    """Admits render/capture traces and maps exact target frames by role."""

    def __init__(self, render_layout: Layout, capture_layout: Layout,
                 render_rate_hz: int = SAMPLE_RATE_HZ,
                 capture_rate_hz: int = SAMPLE_RATE_HZ,
                 max_drift_ppm: int = 10000,
                 clock_id: str = "monotonic-reference-v0") -> None:
        if render_layout.check() is not None or capture_layout.check() is not None:
            raise ValueError("undeclared layout")
        if render_layout.channels != capture_layout.channels:
            raise ValueError("render/capture layout mismatch")
        if render_rate_hz < 1 or capture_rate_hz < 1 or max_drift_ppm < 0:
            raise ValueError("invalid rate or drift bound")
        self.render_layout = render_layout
        self.capture_layout = capture_layout
        self.render_rate_hz = render_rate_hz
        self.capture_rate_hz = capture_rate_hz
        self.max_drift_ppm = max_drift_ppm
        self.clock_id = clock_id
        self._traces: dict[str, ReferenceTrace] = {}
        self.closed = False

    @property
    def config_digest(self) -> str:
        payload = {
            "contract": CONTRACT_ID,
            "render_layout": self.render_layout.id,
            "capture_layout": self.capture_layout.id,
            "render_rate_hz": self.render_rate_hz,
            "capture_rate_hz": self.capture_rate_hz,
            "max_drift_ppm": self.max_drift_ppm,
            "clock_id": self.clock_id,
        }
        text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def submit(self, trace: ReferenceTrace) -> Status:
        if self.closed:
            return Status.CLOSED
        bad = trace.check()
        if bad is not None:
            return bad
        if trace.role == "render":
            expected_layout = self.render_layout
            expected_rate = self.render_rate_hz
        else:
            expected_layout = self.capture_layout
            expected_rate = self.capture_rate_hz
        if trace.layout != expected_layout:
            return Status.REJECTED_LAYOUT
        if trace.sample_rate_hz != expected_rate:
            return Status.REJECTED_RATE
        if abs(trace.clock_drift_ppm) > self.max_drift_ppm:
            return Status.REJECTED_CLOCK
        self._traces[trace.role] = trace
        return Status.OK

    def _source_position(self, trace: ReferenceTrace,
                         target_sample: int) -> Optional[tuple[TraceSegment, int]]:
        nominal = Fraction(target_sample * trace.sample_rate_hz, SAMPLE_RATE_HZ)
        drift = Fraction(target_sample * trace.clock_drift_ppm, 1_000_000)
        source = int(nominal + drift)
        if source < 0:
            return None
        for segment in trace.segments:
            if segment.first_sample <= source < segment.end_sample:
                return segment, source - segment.first_sample
        return None

    def frame(self, role: str, frame_index: int) -> tuple[tuple[Status, ...], tuple[tuple[float, ...], ...]] | Status:
        if self.closed:
            return Status.CLOSED
        if role not in ROLES or frame_index < 0:
            return Status.REJECTED_ROLE
        trace = self._traces.get(role)
        if trace is None:
            return Status.REJECTED_MISSING
        start = frame_index * FRAME_SAMPLES
        channels: list[list[float]] = [[] for _ in range(trace.layout.channels)]
        for target in range(start, start + FRAME_SAMPLES):
            position = self._source_position(trace, target)
            if position is None:
                return Status.REJECTED_GAP
            segment, offset = position
            for channel_index, channel in enumerate(segment.channels):
                channels[channel_index].append(channel[offset])
        statuses = tuple(Status.OK for _ in channels)
        return statuses, tuple(tuple(channel) for channel in channels)

    def close(self) -> None:
        self.closed = True
        self._traces.clear()


def mono_trace(role: str, values: Sequence[float], rate_hz: int = SAMPLE_RATE_HZ,
               first_sample: int = 0, drift_ppm: int = 0) -> ReferenceTrace:
    return ReferenceTrace(
        role=role,
        layout=Layout("mono", 1),
        sample_rate_hz=rate_hz,
        segments=(TraceSegment(first_sample, (tuple(values),)),),
        clock_drift_ppm=drift_ppm,
    )


def canonical_report(session: DuplexSession,
                     frames: dict[str, tuple[tuple[float, ...], ...]]) -> tuple[str, str]:
    payload: dict[str, Any] = {
        "contract": CONTRACT_ID,
        "config_digest": session.config_digest,
        "frames": {
            role: [[list(channel) for channel in channels]]
            for role, channels in frames.items()
        },
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
