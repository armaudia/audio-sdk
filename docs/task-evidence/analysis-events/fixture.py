"""Model-free fixture for the proposed versioned analysis-event interface.

The fixture is intentionally standalone. It demonstrates source-interval
placement, epoch staleness, read-only PCM access and validity-aware VAD
aggregation without changing the installed v0 ABI or adding a runtime.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/analysis-events/0.1"
SAMPLE_RATE_HZ = 16000
HOP_SAMPLES = 160
_NS_PER_SAMPLE = 62500
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class EventKind(str, Enum):
    SPEECH_PROBABILITY = "speech_probability"
    SPEECH_EVENT = "speech_event"
    RATE_EVENT = "rate_event"
    TRANSCRIPT_EVENT = "transcript_event"


class Validity(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    INVALID = "invalid"


class Status(str, Enum):
    OK = "ok"
    REJECTED_STALE_EPOCH = "rejected_stale_epoch"
    REJECTED_INVALID_EVENT = "rejected_invalid_event"
    REJECTED_BAD_INTERVAL = "rejected_bad_interval"
    REJECTED_BAD_CLOCK = "rejected_bad_clock"
    CLOSED = "closed"


@dataclass(frozen=True)
class AnalysisEvent:
    event_id: str
    kind: EventKind
    producer_id: str
    tap_id: str
    epoch: int
    source_start: int
    source_end: int
    value: Any
    validity: Validity
    available_ns: Optional[int]
    availability_clock_id: str
    config_digest: str
    decision_resolution_samples: int = 1
    lookahead_samples: int = 0

    def check(self, total_samples: Optional[int] = None) -> Optional[Status]:
        if not isinstance(self.event_id, str) or not self.event_id:
            return Status.REJECTED_INVALID_EVENT
        if self.epoch < 0:
            return Status.REJECTED_INVALID_EVENT
        if self.source_end <= self.source_start or self.source_start < 0:
            return Status.REJECTED_BAD_INTERVAL
        if total_samples is not None and self.source_end > total_samples:
            return Status.REJECTED_BAD_INTERVAL
        if not isinstance(self.validity, Validity):
            return Status.REJECTED_INVALID_EVENT
        if not _HEX64.match(self.config_digest):
            return Status.REJECTED_INVALID_EVENT
        if self.decision_resolution_samples < 1 or self.lookahead_samples < 0:
            return Status.REJECTED_INVALID_EVENT
        if self.validity is Validity.KNOWN:
            if self.available_ns is None or self.available_ns < 0:
                return Status.REJECTED_BAD_CLOCK
            if not self.availability_clock_id:
                return Status.REJECTED_BAD_CLOCK
            if self.kind is EventKind.SPEECH_PROBABILITY:
                if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
                    return Status.REJECTED_INVALID_EVENT
                if not math.isfinite(float(self.value)) or not 0.0 <= float(self.value) <= 1.0:
                    return Status.REJECTED_INVALID_EVENT
        if self.validity is Validity.INVALID:
            return Status.REJECTED_INVALID_EVENT
        return None


@dataclass(frozen=True)
class FrameCoverage:
    frame_index: int
    overlap_samples: int


@dataclass(frozen=True)
class AccuracyResult:
    status: Status
    reason: Optional[str]
    tp: int
    fn: int
    fp: int
    tn: int
    speech_miss_rate: Optional[float]
    false_alarm_rate: Optional[float]
    unknown_samples: int
    scored_samples: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "tp": self.tp,
            "fn": self.fn,
            "fp": self.fp,
            "tn": self.tn,
            "speech_miss_rate": self.speech_miss_rate,
            "false_alarm_rate": self.false_alarm_rate,
            "unknown_samples": self.unknown_samples,
            "scored_samples": self.scored_samples,
        }


class AnalysisBus:
    """A single stream's read-only PCM view and admitted analysis events."""

    def __init__(self, epoch: int, first_sample: int, audio: Sequence[float],
                 clock_id: str = "monotonic-reference-v0") -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self._audio = tuple(float(x) for x in audio)
        self.clock_id = clock_id
        self.events: list[AnalysisEvent] = []
        self._last_available_ns: dict[str, int] = {}
        self.closed = False

    @property
    def audio_digest(self) -> str:
        packed = b"".join(x.hex().encode("ascii") for x in self._audio)
        return hashlib.sha256(packed).hexdigest()

    def audio_snapshot(self) -> tuple[float, ...]:
        return self._audio

    def publish(self, event: AnalysisEvent) -> Status:
        if self.closed:
            return Status.CLOSED
        bad = event.check(len(self._audio))
        if bad is not None:
            return bad
        if event.epoch < self.epoch:
            return Status.REJECTED_STALE_EPOCH
        if event.epoch == self.epoch and event.source_start < self.first_sample:
            return Status.REJECTED_STALE_EPOCH
        if event.validity is Validity.KNOWN and event.availability_clock_id != self.clock_id:
            return Status.REJECTED_BAD_CLOCK
        if event.available_ns is not None:
            previous = self._last_available_ns.get(self.clock_id)
            if previous is not None and event.available_ns < previous:
                return Status.REJECTED_BAD_CLOCK
            self._last_available_ns[self.clock_id] = event.available_ns
        self.events.append(event)
        return Status.OK

    def reset(self, new_epoch: int, first_sample: int,
              audio: Sequence[float]) -> Status:
        if new_epoch <= self.epoch or first_sample < 0:
            return Status.REJECTED_STALE_EPOCH
        self.epoch = new_epoch
        self.first_sample = first_sample
        self._audio = tuple(float(x) for x in audio)
        self.events.clear()
        self._last_available_ns.clear()
        self.closed = False
        return Status.OK

    def close(self) -> None:
        self.closed = True


def place_events(events: Iterable[AnalysisEvent], hop: int = HOP_SAMPLES,
                 total_samples: Optional[int] = None) -> dict[str, tuple[FrameCoverage, ...]]:
    """Place known events on exact frame boundaries using source intervals."""
    if hop < 1:
        raise ValueError("hop must be positive")
    placed: dict[str, tuple[FrameCoverage, ...]] = {}
    for event in events:
        bad = event.check(total_samples)
        if bad is not None or event.validity is not Validity.KNOWN:
            continue
        limit = total_samples if total_samples is not None else event.source_end
        spans: list[FrameCoverage] = []
        for start in range(0, limit, hop):
            overlap = min(event.source_end, start + hop) - max(event.source_start, start)
            if overlap > 0:
                spans.append(FrameCoverage(start // hop, overlap))
        placed[event.event_id] = tuple(spans)
    return placed


def _validate_intervals(intervals: Sequence[tuple[int, int]], total_samples: int,
                        allow_adjacent: bool, with_decision: bool = False) -> Optional[str]:
    previous_end = 0
    for index, interval in enumerate(intervals):
        expected_length = 3 if with_decision else 2
        if len(interval) != expected_length:
            return "malformed_interval"
        start, end = interval[:2]
        if not isinstance(start, int) or not isinstance(end, int):
            return "malformed_interval"
        if start < 0 or end <= start or end > total_samples:
            return "out_of_range"
        if with_decision and not isinstance(interval[2], bool):
            return "malformed_interval"
        if index and start < previous_end:
            if allow_adjacent and start == previous_end:
                pass
            else:
                return "overlap"
        previous_end = end
    return None


def _merge(intervals: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    merged: list[list[int]] = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return tuple((start, end) for start, end in merged)


def _intersection_length(a: Sequence[tuple[int, int]],
                         b: Sequence[tuple[int, int]]) -> int:
    total = 0
    for a_start, a_end in a:
        for b_start, b_end in b:
            total += max(0, min(a_end, b_end) - max(a_start, b_start))
    return total


def vad_accuracy(reference_speech: Sequence[tuple[int, int]],
                 scored_regions: Sequence[tuple[int, int]],
                 hypothesis: Sequence[tuple[int, int, bool]],
                 total_samples: int) -> AccuracyResult:
    """Score only fully known, gap-free Boolean decisions inside scored regions."""
    for name, intervals, with_value in (
        ("reference", reference_speech, False),
        ("scored", scored_regions, False),
        ("hypothesis", hypothesis, True),
    ):
        bad = _validate_intervals(intervals, total_samples,
                                  name != "hypothesis", with_value)
        if bad is not None:
            return AccuracyResult(Status.REJECTED_BAD_INTERVAL, bad, 0, 0, 0, 0,
                                  None, None, 0, 0)

    scored = _merge(scored_regions)
    if not scored:
        return AccuracyResult(Status.REJECTED_BAD_INTERVAL, "no_scored_region",
                              0, 0, 0, 0, None, None, total_samples, 0)
    scored_samples = sum(end - start for start, end in scored)
    unknown_samples = total_samples - scored_samples
    if not hypothesis:
        return AccuracyResult(Status.REJECTED_BAD_INTERVAL,
                              "gap_or_outside_scored_region", 0, 0, 0, 0,
                              None, None, unknown_samples, scored_samples)

    def rejected(reason: str) -> AccuracyResult:
        return AccuracyResult(Status.REJECTED_BAD_INTERVAL, reason, 0, 0, 0, 0,
                              None, None, unknown_samples, scored_samples)

    cursor = 0
    for start, end in scored:
        if hypothesis[cursor][0] != start:
            return rejected("gap_or_outside_scored_region")
        inside = 0
        while cursor < len(hypothesis) and hypothesis[cursor][0] < end:
            h_start, h_end, _ = hypothesis[cursor]
            if h_end > end:
                return rejected("gap_or_outside_scored_region")
            inside += h_end - h_start
            cursor += 1
        if inside != end - start:
            return rejected("gap_or_outside_scored_region")
    if cursor != len(hypothesis):
        return rejected("gap_or_outside_scored_region")

    speech = _merge(reference_speech)
    hypothesis_speech = _merge(
        (start, end) for start, end, is_speech in hypothesis if is_speech
    )
    tp = _intersection_length(speech, hypothesis_speech)
    speech_total = _intersection_length(speech, scored)
    hyp_speech_total = sum(end - start for start, end in hypothesis_speech)
    fn = speech_total - tp
    fp = hyp_speech_total - tp
    tn = scored_samples - tp - fn - fp
    miss = fn / speech_total if speech_total else None
    false_alarm = fp / (fp + tn) if (fp + tn) else None
    reason = None
    if miss is None:
        reason = "no_scored_speech"
    elif false_alarm is None:
        reason = "no_scored_nonspeech"
    return AccuracyResult(Status.OK, reason, tp, fn, fp, tn, miss, false_alarm,
                          unknown_samples, scored_samples)


def canonical_report(bus: AnalysisBus, accuracy: AccuracyResult) -> tuple[str, str]:
    payload = {
        "contract": CONTRACT_ID,
        "epoch": bus.epoch,
        "audio_digest": bus.audio_digest,
        "events": [
            {
                "event_id": e.event_id,
                "kind": e.kind.value,
                "source_start": e.source_start,
                "source_end": e.source_end,
                "validity": e.validity.value,
            }
            for e in bus.events
        ],
        "accuracy": accuracy.as_dict(),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
