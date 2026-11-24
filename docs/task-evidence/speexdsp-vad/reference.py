# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic SpeexDSP VAD reference model and canonical evidence builder.

This is task-local analysis evidence. It wraps the public
``adapters/speexdsp-vad`` request/result boundary in a v0-shaped local model and
records the analysis acceptance profile with synthetic stimuli only. It is not
the native SpeexDSP library, not the historical 320-sample adapter, not an SDK
provider in the default build and not a VAD accuracy result.
"""
from __future__ import annotations

import hashlib
import json
import math
import numbers
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import fixtures

ROOT = Path(__file__).resolve().parent
ADAPTER_PATH = ROOT / "adapter.json"
CONTRACT_ID = fixtures.CONTRACT_ID
TASK_ID = fixtures.TASK_ID
BASE_COMMIT = fixtures.BASE_COMMIT
ADAPTER_ID = "speexdsp-vad-7a158783df74efe7c2d1c6ee8363c1e695c71226"
ADAPTER_SOURCE_COMMIT = "7a158783df74efe7c2d1c6ee8363c1e695c71226"
CONTROL = "speexdsp_vad_reference"
SCENARIOS = ("primary", "independent_state", "event_bus", "adverse")
PUBLIC_BOUNDARY = "adapters/speexdsp-vad (protocol_version 1, inspect/run)"

VALIDITY_KNOWN = "known"
VALIDITY_UNKNOWN = "unknown"
VALIDITY_INVALID = "invalid"

KIND_PROBABILITY = "speech_probability"
KIND_SPEECH = "speech_event"

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    text = canonical_json(report)
    return text, sha256_text(text)


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def q16(value: float) -> int:
    """Match the public adapter's f32 -> int16 conversion exactly."""
    scaled = max(-1.0, min(1.0, float(value))) * 32767.0
    return int(round(scaled))


def q16_rms(samples: Sequence[float]) -> tuple[float, int]:
    values = [q16(value) for value in samples]
    clipped = sum(1 for value in samples
                  if round(float(value) * 32768.0) < -32768
                  or round(float(value) * 32768.0) > 32767)
    power = sum(value * value for value in values) / (32768.0 ** 2 * max(1, len(values)))
    return math.sqrt(power), clipped


def validate_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("configuration_not_object")
    allowed = {"frame_samples", "sample_rate", "probability_start", "probability_continue"}
    if set(config) != allowed:
        raise ValueError("invalid_configuration_fields")
    if config["frame_samples"] != fixtures.ADAPTER_FRAME_SAMPLES:
        raise ValueError("unsupported_adapter_frame_samples")
    if config["sample_rate"] != fixtures.SAMPLE_RATE_HZ:
        raise ValueError("unsupported_sample_rate")
    if config["probability_start"] != fixtures.PROBABILITY_START:
        raise ValueError("unsupported_probability_start")
    if config["probability_continue"] != fixtures.PROBABILITY_CONTINUE:
        raise ValueError("unsupported_probability_continue")
    return dict(config)


def adapter_descriptor() -> dict[str, Any]:
    document = json.loads(ADAPTER_PATH.read_text(encoding="utf-8"))
    if document.get("identity") != ADAPTER_ID:
        raise ValueError("unexpected_adapter_identity")
    validate_config(document["configuration"])
    return document


def config_digest() -> str:
    return sha256_text(canonical_json({
        "frame_samples": fixtures.ADAPTER_FRAME_SAMPLES,
        "sample_rate": fixtures.SAMPLE_RATE_HZ,
        "probability_start": fixtures.PROBABILITY_START,
        "probability_continue": fixtures.PROBABILITY_CONTINUE,
        "onset_frames": fixtures.ONSET_FRAMES,
        "offset_frames": fixtures.OFFSET_FRAMES,
    }))


def check_frame(frame: Any, final: bool = False) -> tuple[str, int]:
    if frame is None:
        return "rejected_missing_frame", 0
    if not isinstance(frame, (list, tuple)):
        return "rejected_tensor", 0
    count = len(frame)
    if count < 1 or count > fixtures.SDK_FRAME_SAMPLES:
        return "rejected_tensor", 0
    if not all(isinstance(value, numbers.Real) and not isinstance(value, bool)
               for value in frame):
        return "rejected_tensor", 0
    if count < fixtures.SDK_FRAME_SAMPLES and not final:
        return "rejected_short_frame", 0
    values = [float(value) for value in frame]
    if any(not math.isfinite(value) for value in values):
        return "rejected_nonfinite", 0
    if any(abs(value) > fixtures.MAX_ABS_SAMPLE for value in values):
        return "rejected_out_of_range", 0
    return "ok", count


@dataclass(frozen=True)
class AnalysisEvent:
    event_id: str
    kind: str
    producer_id: str
    tap_id: str
    epoch: int
    source_start: int
    source_end: int
    value: Optional[float]
    validity: str
    available_ns: Optional[int]
    availability_clock_id: str
    config_digest: str
    decision_resolution_samples: int = fixtures.SDK_FRAME_SAMPLES
    lookahead_samples: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind,
            "producer_id": self.producer_id,
            "tap_id": self.tap_id,
            "epoch": self.epoch,
            "source_start": self.source_start,
            "source_end": self.source_end,
            "value": self.value,
            "validity": self.validity,
            "available_ns": self.available_ns,
            "availability_clock_id": self.availability_clock_id,
            "config_digest": self.config_digest,
            "decision_resolution_samples": self.decision_resolution_samples,
            "lookahead_samples": self.lookahead_samples,
        }

    def check(self, total_samples: Optional[int] = None) -> Optional[str]:
        if not self.event_id or self.epoch < 0:
            return "rejected_invalid_event"
        if self.source_start < 0 or self.source_end <= self.source_start:
            return "rejected_bad_interval"
        if total_samples is not None and self.source_end > total_samples:
            return "rejected_bad_interval"
        if self.validity not in (VALIDITY_KNOWN, VALIDITY_UNKNOWN, VALIDITY_INVALID):
            return "rejected_invalid_event"
        if not isinstance(self.config_digest, str) or not _HEX64.match(self.config_digest):
            return "rejected_invalid_event"
        if self.decision_resolution_samples < 1 or self.lookahead_samples < 0:
            return "rejected_invalid_event"
        if self.validity == VALIDITY_INVALID:
            return "rejected_invalid_event"
        if self.validity == VALIDITY_KNOWN:
            if self.available_ns is None or self.available_ns < 0:
                return "rejected_bad_clock"
            if not self.availability_clock_id:
                return "rejected_bad_clock"
            if self.kind == KIND_PROBABILITY:
                if (not isinstance(self.value, numbers.Real) or isinstance(self.value, bool)
                        or not math.isfinite(float(self.value)) or not 0.0 <= float(self.value) <= 1.0):
                    return "rejected_invalid_event"
            elif self.value is not None:
                return "rejected_invalid_event"
        return None


class AnalysisBus:
    """One stream's immutable PCM view, admitted events and dropped audit."""

    def __init__(self, epoch: int, first_sample: int, audio: Sequence[float]) -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self._audio = tuple(float(value) for value in audio)
        self.events: list[AnalysisEvent] = []
        self.dropped: list[dict[str, Any]] = []
        self.resets: list[dict[str, Any]] = []
        self._last_available_ns: dict[str, int] = {}
        self.closed = False

    @property
    def audio_digest(self) -> str:
        return fixtures.sha256_f32(self._audio)

    def audio_snapshot(self) -> tuple[float, ...]:
        return self._audio

    def publish(self, event: AnalysisEvent) -> str:
        if self.closed:
            return self._drop(event, "closed")
        bad = event.check(len(self._audio))
        if bad is not None:
            return self._drop(event, bad)
        if event.epoch < self.epoch:
            return self._drop(event, "rejected_stale_epoch")
        if event.epoch == self.epoch and event.source_start < self.first_sample:
            return self._drop(event, "rejected_stale_epoch")
        if event.validity == VALIDITY_KNOWN and event.availability_clock_id != fixtures.CLOCK_ID:
            return self._drop(event, "rejected_bad_clock")
        if event.available_ns is not None:
            previous = self._last_available_ns.get(event.availability_clock_id)
            if previous is not None and event.available_ns < previous:
                return self._drop(event, "rejected_bad_clock")
            self._last_available_ns[event.availability_clock_id] = event.available_ns
        self.events.append(event)
        return "ok"

    def _drop(self, event: AnalysisEvent, reason: str) -> str:
        self.dropped.append({
            "event_id": event.event_id,
            "reason": reason,
            "epoch": event.epoch,
            "source_start": event.source_start,
            "source_end": event.source_end,
        })
        return reason

    def reset(self, epoch: int, first_sample: int, audio: Sequence[float]) -> str:
        if epoch <= self.epoch or first_sample < 0:
            return "rejected_stale_epoch"
        self.resets.append({
            "old_epoch": self.epoch,
            "new_epoch": epoch,
            "cancelled_events": len(self.events),
        })
        self.epoch = epoch
        self.first_sample = first_sample
        self._audio = tuple(float(value) for value in audio)
        self.events.clear()
        self.dropped.clear()
        self._last_available_ns.clear()
        self.closed = False
        return "ok"

    def close(self) -> None:
        self.closed = True


def make_event(event_id: str, kind: str, start: int, end: int,
               value: Optional[float], validity: str,
               available_ns: Optional[int], epoch: int = 1,
               clock_id: str = fixtures.CLOCK_ID) -> AnalysisEvent:
    return AnalysisEvent(
        event_id=event_id,
        kind=kind,
        producer_id=fixtures.PRODUCER_ID,
        tap_id=fixtures.TAP_ID,
        epoch=epoch,
        source_start=start,
        source_end=end,
        value=value,
        validity=validity,
        available_ns=available_ns,
        availability_clock_id=clock_id,
        config_digest=config_digest(),
    )


def place_events(events: Iterable[AnalysisEvent], hop: int = fixtures.SDK_FRAME_SAMPLES,
                 total_samples: Optional[int] = None) -> dict[str, list[tuple[int, int]]]:
    """Place known events on exact source intervals, never rounded to a hop."""
    if hop < 1:
        raise ValueError("hop must be positive")
    placed: dict[str, list[tuple[int, int]]] = {}
    for event in events:
        if event.check(total_samples) is not None or event.validity != VALIDITY_KNOWN:
            continue
        limit = total_samples if total_samples is not None else event.source_end
        spans: list[tuple[int, int]] = []
        for start in range(0, limit, hop):
            overlap = min(event.source_end, start + hop) - max(event.source_start, start)
            if overlap > 0:
                spans.append((start // hop, overlap))
        placed[event.event_id] = spans
    return placed


class Session:
    """Per-session advisory VAD state; no globals and no cross-session sharing."""

    def __init__(self, config: Optional[dict[str, Any]] = None,
                 session_id: str = "local", epoch: int = 1,
                 first_input_sample: int = 0) -> None:
        self.config = validate_config(config) if config is not None else {
            "frame_samples": fixtures.ADAPTER_FRAME_SAMPLES,
            "sample_rate": fixtures.SAMPLE_RATE_HZ,
            "probability_start": fixtures.PROBABILITY_START,
            "probability_continue": fixtures.PROBABILITY_CONTINUE,
        }
        self.session_id = session_id
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.expected_start = first_input_sample
        self.raw_run = 0
        self.idle_run = 0
        self.active = False
        self.records: list[dict[str, Any]] = []
        self.drain_status: Optional[str] = None

    def state(self) -> dict[str, Any]:
        return {
            "epoch": self.epoch,
            "expected_start": self.expected_start,
            "raw_run": self.raw_run,
            "idle_run": self.idle_run,
            "active": self.active,
            "frame_count": len(self.records),
        }

    def reset(self, epoch: int, first_input_sample: int) -> None:
        self.__init__(self.config, self.session_id, epoch, first_input_sample)  # type: ignore[misc]

    def process_frame(self, frame: Any, epoch: Optional[int] = None,
                      first_input_sample: Optional[int] = None, final: bool = False,
                      validity: str = VALIDITY_KNOWN) -> dict[str, Any]:
        status, count = check_frame(frame, final=final)
        if status != "ok":
            return {"status": status, "accepted_count": count}
        if first_input_sample is None:
            first_input_sample = self.expected_start
        if epoch is None:
            epoch = self.epoch
        if epoch != self.epoch:
            return {"status": "rejected_epoch", "accepted_count": 0}
        if first_input_sample != self.expected_start:
            return {"status": "rejected_interval", "accepted_count": 0}
        if validity not in (VALIDITY_KNOWN, VALIDITY_UNKNOWN, VALIDITY_INVALID):
            return {"status": "rejected_validity", "accepted_count": 0}

        samples = [f32(float(value)) for value in frame[:count]]
        rms, clipped = q16_rms(samples)
        raw_active = rms >= fixtures.PROBABILITY_START
        sustain = rms >= fixtures.PROBABILITY_CONTINUE
        if raw_active:
            self.raw_run += 1
            self.idle_run = 0
            if not self.active and self.raw_run >= fixtures.ONSET_FRAMES:
                self.active = True
        else:
            self.raw_run = 0
            self.idle_run = 0 if sustain else self.idle_run + 1
            if self.active and self.idle_run >= fixtures.OFFSET_FRAMES:
                self.active = False
        if final:
            self.active = False

        source_end = first_input_sample + count
        record = {
            "status": "ok",
            "accepted_count": count,
            "source_start": first_input_sample,
            "source_end": source_end,
            "rms": round(rms, 9),
            "activity": round(min(1.0, rms / fixtures.PROBABILITY_START), 9),
            "raw_active": raw_active,
            "sustain": sustain,
            "detected": self.active,
            "pcm16_clipped_samples": clipped,
            "validity": validity,
        }
        self.records.append(record)
        self.expected_start = source_end
        return record

    def drain(self) -> str:
        self.drain_status = "end_of_stream"
        return self.drain_status

    def summary(self) -> dict[str, Any]:
        probability = [row for row in self.records]
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "frame_count": len(self.records),
            "window_count": len(self.records),
            "probability_event_count": len(probability),
            "speech_event_count": 0,
            "event_count": len(probability),
            "events_sha256": sha256_text(canonical_json(probability)),
            "windows_sha256": sha256_text(canonical_json([r for r in self.records])),
            "drain_status": self.drain_status,
        }


def detection_runs(records: Sequence[dict[str, Any]]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: Optional[int] = None
    for index, record in enumerate(records):
        active = bool(record["detected"]) and record["validity"] == VALIDITY_KNOWN
        if active and start is None:
            start = index
        elif not active and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(records)))
    return runs


def score_stream(records: Sequence[dict[str, Any]],
                 runs: Sequence[tuple[int, int]]) -> dict[str, Any]:
    stratified: dict[str, dict[str, int]] = {
        segment.name: {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
        for segment in fixtures.SEGMENTS if segment.validity == VALIDITY_KNOWN
    }
    totals = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for index in range(fixtures.SCORED_END_FRAME):
        record = records[index]
        segment = fixtures.segment_for_frame(index)
        truth = segment.label == "speech"
        detected = bool(record["detected"])
        key = ("tp" if truth and detected else
               "fn" if truth else "fp" if detected else "tn")
        totals[key] += 1
        stratified[segment.name][key] += 1

    timings: list[dict[str, Any]] = []
    for segment in fixtures.SEGMENTS:
        if segment.label != "speech":
            continue
        candidates = [run for run in runs
                      if segment.start_frame <= run[0] < segment.end_frame]
        if not candidates:
            timings.append({"segment": segment.name, "status": "missed"})
            continue
        onset, offset = candidates[0]
        timings.append({
            "segment": segment.name,
            "status": "ok",
            "onset_frame": onset,
            "offset_frame": offset,
            "onset_delay_samples": (onset - segment.start_frame) * fixtures.SDK_FRAME_SAMPLES,
            "offset_delay_samples": (offset - segment.end_frame) * fixtures.SDK_FRAME_SAMPLES,
            "detected_frames": offset - onset,
            "truth_frames": segment.end_frame - segment.start_frame,
        })

    speech_total = totals["tp"] + totals["fn"]
    nonspeech_total = totals["tn"] + totals["fp"]
    return {
        "totals": totals,
        "stratified": stratified,
        "timings": timings,
        "speech_miss_rate": round(totals["fn"] / speech_total, 9) if speech_total else None,
        "false_alarm_rate": round(totals["fp"] / nonspeech_total, 9) if nonspeech_total else None,
        "scored_samples": fixtures.SCORED_END_SAMPLE,
        "known_positive_samples": sum(
            (segment.end_frame - segment.start_frame) * fixtures.SDK_FRAME_SAMPLES
            for segment in fixtures.SEGMENTS if segment.label == "speech"),
        "known_negative_samples": sum(
            (segment.end_frame - segment.start_frame) * fixtures.SDK_FRAME_SAMPLES
            for segment in fixtures.SEGMENTS if segment.label == "nonspeech"),
        "unknown_samples": fixtures.TOTAL_SAMPLES - fixtures.SCORED_END_SAMPLE,
        "invalid_samples": 0,
        "no_scored_speech_reason": None if speech_total else "no_scored_speech",
        "no_scored_nonspeech_reason": None if nonspeech_total else "no_scored_nonspeech",
    }


def invalid_vs_nonspeech_control() -> dict[str, Any]:
    bus = AnalysisBus(epoch=1, first_sample=0, audio=[0.0] * (2 * fixtures.SDK_FRAME_SAMPLES))
    known_zero = make_event("known-zero", KIND_PROBABILITY, 0, fixtures.SDK_FRAME_SAMPLES,
                            0.0, VALIDITY_KNOWN, fixtures.AVAILABILITY_OFFSET_NS)
    nan = make_event("nan", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                     2 * fixtures.SDK_FRAME_SAMPLES, float("nan"), VALIDITY_KNOWN,
                     2 * fixtures.AVAILABILITY_OFFSET_NS)
    out_of_range = make_event("range", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                              2 * fixtures.SDK_FRAME_SAMPLES, 1.5, VALIDITY_KNOWN,
                              2 * fixtures.AVAILABILITY_OFFSET_NS)
    invalid = AnalysisEvent(**{**nan.__dict__, "event_id": "invalid", "value": 0.0,
                               "validity": VALIDITY_INVALID})
    unknown = make_event("unknown", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                         2 * fixtures.SDK_FRAME_SAMPLES, 0.9, VALIDITY_UNKNOWN, None)
    statuses = {
        "known_zero": bus.publish(known_zero),
        "nan_probability": bus.publish(nan),
        "out_of_range_probability": bus.publish(out_of_range),
        "invalid_validity": bus.publish(invalid),
        "unknown_probability": bus.publish(unknown),
    }
    known = [event for event in bus.events if event.validity == VALIDITY_KNOWN]
    return {
        "statuses": statuses,
        "known_nonspeech_events": len(known),
        "invalid_events_excluded": 3,
        "unknown_events_excluded": 1,
        "invalid_counted_as_nonspeech": False,
        "admitted_event_ids": [event.event_id for event in bus.events],
    }


def frame_adverse_control() -> dict[str, Any]:
    session = Session()
    baseline = session.state()
    cases: dict[str, Any] = {}
    probes = {
        "missing": None,
        "nonfinite": [float("nan")] + [0.0] * (fixtures.SDK_FRAME_SAMPLES - 1),
        "infinite": [float("inf")] + [0.0] * (fixtures.SDK_FRAME_SAMPLES - 1),
        "short": [0.0] * (fixtures.SDK_FRAME_SAMPLES - 1),
        "long": [0.0] * (fixtures.SDK_FRAME_SAMPLES + 1),
        "wrong_shape": [[0.0] * fixtures.SDK_FRAME_SAMPLES],
    }
    for name, frame in probes.items():
        cases[name] = session.process_frame(frame, epoch=1)["status"]
    cases["state_unchanged"] = session.state() == baseline
    short_final = session.process_frame([0.0] * 80, epoch=1, final=True)
    cases["short_final_status"] = short_final["status"]
    cases["short_final_valid_count"] = short_final["accepted_count"]
    cases["short_final_source_end"] = short_final["source_end"]
    cases["stale_epoch"] = session.process_frame(
        [0.0] * fixtures.SDK_FRAME_SAMPLES, epoch=0)["status"]
    cases["wrong_interval"] = session.process_frame(
        [0.0] * fixtures.SDK_FRAME_SAMPLES, epoch=1,
        first_input_sample=320)["status"]
    return cases


def event_adverse_control() -> dict[str, Any]:
    bus = AnalysisBus(epoch=1, first_sample=fixtures.SDK_FRAME_SAMPLES,
                      audio=[0.0] * (3 * fixtures.SDK_FRAME_SAMPLES))
    baseline = make_event("baseline", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                          2 * fixtures.SDK_FRAME_SAMPLES, 0.2, VALIDITY_KNOWN,
                          fixtures.AVAILABILITY_OFFSET_NS)
    if bus.publish(baseline) != "ok":
        raise AssertionError("baseline event rejected")
    before = len(bus.events)
    stale = make_event("stale", KIND_PROBABILITY, 0, fixtures.SDK_FRAME_SAMPLES,
                       0.5, VALIDITY_KNOWN, fixtures.AVAILABILITY_OFFSET_NS, epoch=0)
    before_start = make_event("before-start", KIND_PROBABILITY, 0, fixtures.SDK_FRAME_SAMPLES,
                              0.5, VALIDITY_KNOWN, fixtures.AVAILABILITY_OFFSET_NS, epoch=1)
    stale_clock = make_event("old-availability", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                             2 * fixtures.SDK_FRAME_SAMPLES, 0.5, VALIDITY_KNOWN, 0, epoch=1)
    wrong_clock = make_event("bad-clock", KIND_PROBABILITY, fixtures.SDK_FRAME_SAMPLES,
                             2 * fixtures.SDK_FRAME_SAMPLES, 0.5, VALIDITY_KNOWN,
                             2 * fixtures.AVAILABILITY_OFFSET_NS, epoch=1,
                             clock_id="other-clock")
    statuses = {
        "stale_epoch": bus.publish(stale),
        "before_first_sample": bus.publish(before_start),
        "stale_availability": bus.publish(stale_clock),
        "wrong_clock": bus.publish(wrong_clock),
    }
    return {
        "statuses": statuses,
        "events_unchanged": len(bus.events) == before,
        "dropped_reasons": [item["reason"] for item in bus.dropped],
    }


def independent_state_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    left = Session(epoch=1, first_input_sample=0)
    right = Session(epoch=7, first_input_sample=3200)
    for frame in frames[:10]:
        left.process_frame(frame, epoch=1)
        right.process_frame(frame, epoch=7)
    for frame in frames[60:65]:
        left.process_frame(frame, epoch=1)
    for frame in frames[210:215]:
        right.process_frame(frame, epoch=7)
    before = (left.summary()["events_sha256"], right.summary()["events_sha256"])
    left.reset(epoch=2, first_input_sample=0)
    for frame in frames[:10]:
        left.process_frame(frame, epoch=2)
    for frame in frames[60:65]:
        left.process_frame(frame, epoch=2)
    replay = Session(epoch=2, first_input_sample=0)
    for frame in frames[:10]:
        replay.process_frame(frame, epoch=2)
    for frame in frames[60:65]:
        replay.process_frame(frame, epoch=2)
    return {
        "distinct_event_digests": before[0] != before[1],
        "left_digest": before[0],
        "right_digest": before[1],
        "reset_matches_fresh_run": left.summary()["events_sha256"] == replay.summary()["events_sha256"],
        "right_unchanged": right.summary()["events_sha256"] == before[1],
        "left_epoch": left.epoch,
        "right_epoch": right.epoch,
    }


def overlapping_session_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    first = AnalysisBus(epoch=1, first_sample=0,
                        audio=[x for frame in frames[:160] for x in frame])
    second = AnalysisBus(epoch=2, first_sample=160 * fixtures.SDK_FRAME_SAMPLES,
                         audio=[x for frame in frames[160:320] for x in frame])
    event = make_event("first-only", KIND_PROBABILITY, 0, fixtures.SDK_FRAME_SAMPLES,
                       0.25, VALIDITY_KNOWN, fixtures.AVAILABILITY_OFFSET_NS, epoch=1)
    accepted = first.publish(event)
    rejected = second.publish(event)
    return {
        "first_accept": accepted,
        "second_reject": rejected,
        "first_events": len(first.events),
        "second_events": len(second.events),
        "distinct_audio": first.audio_digest != second.audio_digest,
        "first_audio_digest": first.audio_digest,
        "second_audio_digest": second.audio_digest,
    }


def cross_hop_control() -> dict[str, Any]:
    event = make_event("cross-hop", KIND_PROBABILITY, 150, 330,
                       0.75, VALIDITY_KNOWN, fixtures.AVAILABILITY_OFFSET_NS)
    placed = place_events([event], total_samples=480)["cross-hop"]
    return {
        "source_interval": [150, 330],
        "placement": [[frame, overlap] for frame, overlap in placed],
        "exact": placed == [(0, 10), (1, 160), (2, 10)],
        "total_overlap": sum(overlap for _, overlap in placed),
    }


def build_report() -> dict[str, Any]:
    pins = fixtures.verify_pins()
    adapter = adapter_descriptor()
    frames, pcm_digest = fixtures.build_frames()

    session = Session(config=adapter["configuration"], session_id="primary")
    records: list[dict[str, Any]] = []
    for index, frame in enumerate(frames):
        segment = fixtures.segment_for_frame(index)
        record = session.process_frame(list(frame), epoch=1, validity=segment.validity)
        if record["status"] != "ok":
            raise AssertionError(f"fixture frame {index} rejected: {record}")
        record["segment"] = segment.name
        record["label"] = segment.label
        records.append(record)
    session.drain()

    flat = [sample for frame in frames for sample in frame]
    bus = AnalysisBus(epoch=1, first_sample=0, audio=flat)
    probability_rows: list[dict[str, Any]] = []
    for record in records:
        validity = record["validity"]
        available = (None if validity == VALIDITY_UNKNOWN else
                     record["source_end"] * fixtures.NS_PER_SAMPLE
                     + fixtures.AVAILABILITY_OFFSET_NS)
        event = make_event(f"p-{record['source_start']:06d}", KIND_PROBABILITY,
                           record["source_start"], record["source_end"],
                           record["activity"], validity, available)
        status = bus.publish(event)
        if status != "ok":
            raise AssertionError(f"probability event rejected: {status}")
        probability_rows.append(event.as_dict())

    runs = detection_runs(records)
    speech_rows: list[dict[str, Any]] = []
    for run_index, (start, end) in enumerate(runs):
        event = make_event(
            f"speech-{run_index:02d}", KIND_SPEECH,
            start * fixtures.SDK_FRAME_SAMPLES, end * fixtures.SDK_FRAME_SAMPLES,
            None, VALIDITY_KNOWN,
            (fixtures.TOTAL_SAMPLES + run_index + 1) * fixtures.NS_PER_SAMPLE
            + fixtures.AVAILABILITY_OFFSET_NS)
        status = bus.publish(event)
        if status != "ok":
            raise AssertionError(f"speech event rejected: {status}")
        speech_rows.append(event.as_dict())

    score = score_stream(records, runs)
    spec = {
        "contract": CONTRACT_ID,
        "generator": "task-local-lcg-speexdsp-vad-v1",
        "lcg_seed": fixtures.LCG_SEED,
        "sdk_frame_samples": fixtures.SDK_FRAME_SAMPLES,
        "adapter_frame_samples": fixtures.ADAPTER_FRAME_SAMPLES,
        "probability_start": fixtures.PROBABILITY_START,
        "probability_continue": fixtures.PROBABILITY_CONTINUE,
        "onset_frames": fixtures.ONSET_FRAMES,
        "offset_frames": fixtures.OFFSET_FRAMES,
        "segments": [
            {
                "name": segment.name,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "label": segment.label,
                "rms": segment.rms,
                "validity": segment.validity,
            }
            for segment in fixtures.SEGMENTS
        ],
    }
    spec_digest = sha256_text(canonical_json(spec))
    controls = {
        "invalid_vs_nonspeech": invalid_vs_nonspeech_control(),
        "frame_adverse": frame_adverse_control(),
        "event_adverse": event_adverse_control(),
        "independent_state": independent_state_control(frames),
        "overlapping_sessions": overlapping_session_control(frames),
        "cross_hop": cross_hop_control(),
        "source_intervals": {
            "probability_intervals_contiguous": all(
                row["source_start"] == index * fixtures.SDK_FRAME_SAMPLES
                and row["source_end"] == (index + 1) * fixtures.SDK_FRAME_SAMPLES
                for index, row in enumerate(probability_rows)),
            "speech_events_frame_aligned": all(
                row["source_start"] % fixtures.SDK_FRAME_SAMPLES == 0
                and row["source_end"] % fixtures.SDK_FRAME_SAMPLES == 0
                for row in speech_rows),
            "speech_events_inside_scored_region": all(
                row["source_end"] <= fixtures.SCORED_END_SAMPLE for row in speech_rows),
        },
        "availability": {
            "offset_ns": fixtures.AVAILABILITY_OFFSET_NS,
            "nanoseconds_per_sample": fixtures.NS_PER_SAMPLE,
            "clock_id": fixtures.CLOCK_ID,
            "probability_availability_monotonic": all(
                left["available_ns"] < right["available_ns"]
                for left, right in zip(probability_rows, probability_rows[1:])
                if left["available_ns"] is not None and right["available_ns"] is not None),
            "unknown_events_have_no_availability": all(
                row["available_ns"] is None for row in probability_rows
                if row["validity"] == VALIDITY_UNKNOWN),
        },
    }

    return {
        "schema_id": "audio-sdk/task-evidence/speexdsp-vad/0.1",
        "contract": CONTRACT_ID,
        "task": TASK_ID,
        "base_commit": BASE_COMMIT,
        "status": {
            "claim": "proposal-only-synthetic",
            "qualification": "incomplete",
            "release_decision": "not_qualified",
            "activity_decision": "advisory_only_no_gating_claim",
            "installed_sdk_changed": False,
            "missing_result_policy": "Missing, rejected, unrun or blocked results are recorded as failures or incomplete and never counted as passes.",
        },
        "boundary": {
            "public_adapter": PUBLIC_BOUNDARY,
            "adapter_identity": adapter["identity"],
            "adapter_source_commit": ADAPTER_SOURCE_COMMIT,
            "adapter_configuration": adapter["configuration"],
            "sdk_frame_samples": fixtures.SDK_FRAME_SAMPLES,
            "adapter_frame_samples": fixtures.ADAPTER_FRAME_SAMPLES,
            "frame_divergence": "Historical adapter declares 320 samples; frozen v0 uses 160. No numeric parity is claimed.",
            "public_abi_changed": False,
            "provider_default": "off_unregistered",
            "provider_option": "AS_ENABLE_SPEEXDSP_VAD",
            "provider_id_when_opted_in": "detection.speexdsp-vad.refv0",
        },
        "acceptance_profile": "Analysis",
        "source_pins": pins,
        "pin_notes": fixtures.PIN_NOTES,
        "fixture": {
            "generator": spec["generator"],
            "spec_digest": spec_digest,
            "config_digest": config_digest(),
            "total_frames": fixtures.TOTAL_FRAMES,
            "total_samples": fixtures.TOTAL_SAMPLES,
            "scored_end_frame": fixtures.SCORED_END_FRAME,
            "scored_end_sample": fixtures.SCORED_END_SAMPLE,
            "segments": spec["segments"],
        },
        "digests": {
            "pcm_f32_sha256": pcm_digest,
            "probability_stream_sha256": sha256_text(canonical_json(probability_rows)),
            "speech_events_sha256": sha256_text(canonical_json(speech_rows)),
            "audio_view_sha256": bus.audio_digest,
            "primary_session_events_sha256": session.summary()["events_sha256"],
        },
        "counts": {
            "sdk_frames": len(records),
            "probability_events_known": sum(
                1 for row in probability_rows if row["validity"] == VALIDITY_KNOWN),
            "probability_events_unknown": sum(
                1 for row in probability_rows if row["validity"] == VALIDITY_UNKNOWN),
            "speech_events": len(speech_rows),
            "bus_events": len(bus.events),
            "bus_dropped_events": len(bus.dropped),
            "pcm16_clipped_samples": sum(row["pcm16_clipped_samples"] for row in records),
            **score["totals"],
        },
        "scoring": score,
        "adverse_controls": controls,
        "probabilities": probability_rows,
        "speech_events": speech_rows,
        "regeneration": {
            "required_repeats": 3,
            "comparison": "byte_identical",
            "tolerance": "none",
        },
        "blockers": [
            "No rights-cleared, label-complete held-out VAD cohort with per-frame labels is staged here; historical AMI percentages are source-reported only.",
            "No native VAD target-runtime execution profile, target device, CPU/memory budget, availability clock or deadline budget is available.",
            "The historical adapter uses 320-sample frames and raw int16 SpeexDSP labels; v0 is fixed at 160 samples and this model uses explicit thresholds. No numeric parity is claimed.",
            "Typed analysis events are a proposal from SDK-FND-ANALYSIS, not installed v0 behavior; activity output remains advisory.",
            "No adverse Tiny16 comparison was run: there is no S10/protocol clearance, approved independent reference adapter or permitted case manifest.",
        ],
        "non_claims": [
            "No real speech, recordings, downloads, model weights, corpora, licensed runtimes or device results were used.",
            "No listening, quality, intelligibility, pacing, power, production availability or release qualification is claimed.",
            "No SDK public API, ABI, CONTRACTS.md, CMakeLists.txt, descriptor, registry default or installed behavior was changed.",
            "Synthetic probabilities and detections are advisory references only, not a candidate score or a gating decision.",
        ],
    }
