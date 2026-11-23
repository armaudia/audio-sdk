"""Deterministic, model-free fixed-RMS VAD reference for SDK v0 analysis.

This module is an opt-in developer reference. It mirrors the public
``adapters/rms-energy-vad`` waveform-to-annotation boundary (fixed -42 dBFS
RMS threshold, 320-sample analysis window, identity source mapping) while
consuming the immutable SDK v0 geometry: 16 kHz mono float32, 160-sample
frames. Two SDK frames form one analysis window; each frame still carries its
own exact half-open source interval.

No SDK header, ABI, descriptor, registry default or installed behavior is
changed here. There are no weights, downloads, corpora or timing claims.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/fixed-rms-vad/0.1"
IDENTITY = "fixed-rms-vad-reference-v1"
ADAPTER_ID = "fixed-rms-vad-reference"
ADAPTER_IDENTITY = "rms-energy-vad-1-threshold-minus-42dbfs"
SAMPLE_RATE_HZ = 16000
SDK_FRAME_SAMPLES = 160
ADAPTER_FRAME_SAMPLES = 320
CHANNELS = 1
THRESHOLD_DBFS = -42.0
SOFTNESS_DB = 2.0
NS_PER_SAMPLE = 62500
AVAILABILITY_ORIGIN_NS = 1_700_000_000_000_000
CLOCK_ID = "fixture-monotonic-v0"
_F32 = struct.Struct("<f")

DEFAULT_CONFIG = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "sdk_frame_samples": SDK_FRAME_SAMPLES,
    "adapter_frame_samples": ADAPTER_FRAME_SAMPLES,
    "threshold_dbfs": THRESHOLD_DBFS,
    "softness_db": SOFTNESS_DB,
}


class ReferenceError(ValueError):
    """A fail-closed rejection with an explicit machine-readable reason."""


def f32(value: float) -> float:
    """Round a Python double to IEEE-754 binary32."""
    return _F32.unpack(_F32.pack(float(value)))[0]


def f32_bytes(samples: Iterable[float]) -> bytes:
    return b"".join(_F32.pack(f32(value)) for value in samples)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_samples(samples: Iterable[float]) -> str:
    return sha256_bytes(f32_bytes(samples))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def validate_config(config: Any) -> dict[str, Any]:
    """Validate the fixed geometry and threshold; never silently default."""
    if not isinstance(config, dict):
        raise ReferenceError("config_not_object")
    unknown = sorted(set(config) - set(DEFAULT_CONFIG))
    missing = sorted(set(DEFAULT_CONFIG) - set(config))
    if unknown:
        raise ReferenceError("unknown_config:" + ",".join(unknown))
    if missing:
        raise ReferenceError("missing_config:" + ",".join(missing))
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ReferenceError("unsupported_sample_rate")
    if config["channels"] != CHANNELS:
        raise ReferenceError("unsupported_channels")
    if config["sample_format"] != "f32":
        raise ReferenceError("unsupported_sample_format")
    if config["sdk_frame_samples"] != SDK_FRAME_SAMPLES:
        raise ReferenceError("unsupported_sdk_frame_samples")
    if config["adapter_frame_samples"] != ADAPTER_FRAME_SAMPLES:
        raise ReferenceError("unsupported_adapter_frame_samples")
    if config["adapter_frame_samples"] != 2 * config["sdk_frame_samples"]:
        raise ReferenceError("window_frame_geometry_mismatch")
    for name in ("threshold_dbfs", "softness_db"):
        value = config[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceError("nonnumeric_config:" + name)
        if not math.isfinite(value):
            raise ReferenceError("nonfinite_config:" + name)
    if not -100.0 <= float(config["threshold_dbfs"]) <= 0.0:
        raise ReferenceError("threshold_out_of_range")
    if not 0.1 <= float(config["softness_db"]) <= 20.0:
        raise ReferenceError("softness_out_of_range")
    return dict(config)


@dataclass(frozen=True)
class AnalysisEvent:
    event_id: str
    kind: str
    producer_id: str
    tap_id: str
    epoch: int
    source_start: int
    source_end: int
    value: float
    validity: str
    available_ns: int
    availability_clock_id: str
    config_digest: str
    sequence: int

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
            "sequence": self.sequence,
        }


def merge_intervals(intervals: Sequence[Sequence[int]]) -> list[list[int]]:
    """Merge half-open intervals; adjacency is merged, overlaps are unioned."""
    ordered = sorted((int(start), int(end)) for start, end in intervals)
    merged: list[list[int]] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def intersection_length(left: Sequence[Sequence[int]],
                        right: Sequence[Sequence[int]]) -> int:
    total = 0
    for a_start, a_end in left:
        for b_start, b_end in right:
            total += max(0, min(a_end, b_end) - max(a_start, b_start))
    return total


class Session:
    """One independent fixed-RMS detection state with a strict event channel."""

    def __init__(self, config: Optional[dict[str, Any]] = None, *, epoch: int = 1,
                 session_id: str = "session-a", first_sample: int = 0) -> None:
        self.config = validate_config(dict(DEFAULT_CONFIG if config is None else config))
        self.config_digest = canonical_digest(self.config)
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ReferenceError("invalid_epoch")
        if isinstance(first_sample, bool) or not isinstance(first_sample, int) or first_sample < 0:
            raise ReferenceError("invalid_first_sample")
        if not session_id:
            raise ReferenceError("invalid_session_id")
        self.session_id = session_id
        self.epoch = epoch
        self.first_sample = first_sample
        self.next_sample = first_sample
        self.reset_count = 0
        self.windows: list[dict[str, Any]] = []
        self.frame_decisions: list[dict[str, Any]] = []
        self.events: list[AnalysisEvent] = []
        self.rejections: list[dict[str, Any]] = []
        self.delivered_events: list[AnalysisEvent] = []
        self._pending: list[dict[str, Any]] = []
        self._open_event: Optional[dict[str, Any]] = None
        self._expected_sequence = 0
        self._last_available_ns: Optional[int] = None
        self.closed = False

    def _reject(self, reason: str, **detail: Any) -> dict[str, Any]:
        record = {"reason": reason, "epoch": self.epoch}
        record.update(detail)
        self.rejections.append(record)
        return record

    def reset(self, new_epoch: int, first_sample: int = 0) -> dict[str, Any]:
        if (isinstance(new_epoch, bool) or not isinstance(new_epoch, int)
                or new_epoch <= self.epoch):
            return self._reject("stale_or_equal_reset_epoch", attempted_epoch=new_epoch)
        if (isinstance(first_sample, bool) or not isinstance(first_sample, int)
                or first_sample < 0):
            return self._reject("invalid_first_sample", attempted_first_sample=first_sample)
        self.epoch = new_epoch
        self.first_sample = first_sample
        self.next_sample = first_sample
        self.reset_count += 1
        self.windows = []
        self.frame_decisions = []
        self.events = []
        self.rejections = []
        self.delivered_events = []
        self._pending = []
        self._open_event = None
        self._expected_sequence = 0
        self._last_available_ns = None
        self.closed = False
        return {"status": "ok", "epoch": self.epoch, "first_sample": self.first_sample}

    def _new_event(self, kind: str, source_start: int, source_end: int,
                   value: float, available_ns: int) -> AnalysisEvent:
        event = AnalysisEvent(
            event_id=f"{self.session_id}:e{self.epoch}:{self._expected_sequence:06d}",
            kind=kind,
            producer_id=self.session_id,
            tap_id="rms-energy-vad-1",
            epoch=self.epoch,
            source_start=source_start,
            source_end=source_end,
            value=f32(value),
            validity="known",
            available_ns=available_ns,
            availability_clock_id=CLOCK_ID,
            config_digest=self.config_digest,
            sequence=self._expected_sequence,
        )
        self._expected_sequence += 1
        self.events.append(event)
        return event

    def _close_active_run(self, available_ns: int) -> None:
        if self._open_event is None:
            return
        start, end = self._open_event["start"], self._open_event["end"]
        self._new_event("speech_event", start, end, 1.0, available_ns)
        self._open_event = None

    def _emit_frame_decisions(self, frames: Sequence[dict[str, Any]], *, window_start: int,
                              window_end: int, probability: float, label: bool) -> None:
        for frame in frames:
            frame_start = frame["first_input_sample"]
            frame_end = frame_start + frame["valid_count"]
            decision = {
                "source_start": frame_start,
                "source_end": frame_end,
                "window_start": window_start,
                "window_end": window_end,
                "probability": f32(probability),
                "label": label,
                "padded_samples": 0 if frame["valid_count"] == SDK_FRAME_SAMPLES
                else SDK_FRAME_SAMPLES - frame["valid_count"],
            }
            self.frame_decisions.append(decision)
            if label:
                if self._open_event is None:
                    self._open_event = {"start": frame_start, "end": frame_end}
                else:
                    self._open_event["end"] = frame_end
            else:
                self._close_active_run(AVAILABILITY_ORIGIN_NS + frame_end * NS_PER_SAMPLE)

    def _process_window(self, padded: Sequence[float], frames: Sequence[dict[str, Any]]) -> dict[str, Any]:
        window_start = frames[0]["first_input_sample"]
        valid_count = sum(frame["valid_count"] for frame in frames)
        window_end = window_start + valid_count
        if len(padded) != ADAPTER_FRAME_SAMPLES:
            raise ReferenceError("window_shape_mismatch")
        squared = 0.0
        for value in padded:
            sample = float(value)
            squared += sample * sample
        rms = math.sqrt(squared / ADAPTER_FRAME_SAMPLES)
        dbfs = 20.0 * math.log10(max(rms, 1e-12))
        threshold = float(self.config["threshold_dbfs"])
        softness = float(self.config["softness_db"])
        probability = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, (dbfs - threshold) / softness))))
        label = bool(probability >= 0.5)
        available_ns = AVAILABILITY_ORIGIN_NS + window_end * NS_PER_SAMPLE
        if self._last_available_ns is not None and available_ns <= self._last_available_ns:
            self._reject("nonmonotonic_availability", available_ns=available_ns)
            raise ReferenceError("nonmonotonic_availability")
        self._last_available_ns = available_ns
        self._new_event("speech_probability", window_start, window_end,
                        probability, available_ns)
        self._emit_frame_decisions(frames, window_start=window_start,
                                   window_end=window_end,
                                   probability=probability, label=label)
        record = {
            "source_start": window_start,
            "source_end": window_end,
            "padded_samples": sum(SDK_FRAME_SAMPLES - frame["valid_count"] for frame in frames),
            "rms": f32(rms),
            "dbfs": f32(dbfs),
            "probability": f32(probability),
            "label": label,
            "available_ns": available_ns,
        }
        self.windows.append(record)
        return record

    def process_frame(self, frame: Sequence[float], *, epoch: Optional[int] = None,
                      first_input_sample: Optional[int] = None,
                      sample_rate_hz: int = SAMPLE_RATE_HZ, channels: int = CHANNELS,
                      sample_format: str = "f32", valid_count: int = SDK_FRAME_SAMPLES,
                      final: bool = False) -> dict[str, Any]:
        """Consume exactly one padded 160-sample frame; return a status record."""
        if self.closed:
            return self._reject("session_closed")
        frame_epoch = self.epoch if epoch is None else epoch
        if isinstance(frame_epoch, bool) or not isinstance(frame_epoch, int):
            return self._reject("invalid_epoch")
        if frame_epoch < self.epoch:
            return self._reject("stale_epoch", attempted_epoch=frame_epoch)
        if frame_epoch > self.epoch:
            return self._reject("future_epoch", attempted_epoch=frame_epoch)
        if sample_rate_hz != SAMPLE_RATE_HZ:
            return self._reject("invalid_sample_rate", observed=sample_rate_hz)
        if channels != CHANNELS:
            return self._reject("invalid_channels", observed=channels)
        if sample_format != "f32":
            return self._reject("invalid_sample_format", observed=sample_format)
        if not isinstance(frame, (list, tuple)) or len(frame) != SDK_FRAME_SAMPLES:
            observed = len(frame) if hasattr(frame, "__len__") else None
            return self._reject("invalid_frame_length", observed=observed)
        if (isinstance(valid_count, bool) or not isinstance(valid_count, int)
                or not 1 <= valid_count <= SDK_FRAME_SAMPLES):
            return self._reject("invalid_valid_count", observed=valid_count)
        if valid_count < SDK_FRAME_SAMPLES and not final:
            return self._reject("short_frame_without_final", observed=valid_count)
        converted: list[float] = []
        for value in frame:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return self._reject("nonnumeric_sample")
            number = float(value)
            if not math.isfinite(number):
                return self._reject("nonfinite_window")
            converted.append(f32(number))
        for index in range(valid_count, SDK_FRAME_SAMPLES):
            if converted[index] != 0.0:
                return self._reject("nonzero_final_padding", index=index)
        position = self.next_sample if first_input_sample is None else first_input_sample
        if (isinstance(position, bool) or not isinstance(position, int)
                or position != self.next_sample):
            return self._reject("invalid_source_interval", observed=position,
                                expected=self.next_sample)
        self._pending.append({
            "samples": converted,
            "valid_count": valid_count,
            "first_input_sample": position,
        })
        self.next_sample += SDK_FRAME_SAMPLES
        produced = None
        if len(self._pending) == ADAPTER_FRAME_SAMPLES // SDK_FRAME_SAMPLES:
            frames = list(self._pending)
            padded: list[float] = []
            for item in frames:
                padded.extend(item["samples"])
            self._pending = []
            produced = self._process_window(padded, frames)
        return {
            "status": "ok",
            "consumed_samples": SDK_FRAME_SAMPLES,
            "accepted_samples": valid_count,
            "source_start": position,
            "source_end": position + valid_count,
            "window": produced,
            "rejections": len(self.rejections),
        }

    def drain(self) -> dict[str, Any]:
        """Release a single pending padded frame, then close the session."""
        if self.closed:
            return self._reject("session_closed")
        if not self._pending:
            self.closed = True
            self._close_active_run(AVAILABILITY_ORIGIN_NS +
                                   self.next_sample * NS_PER_SAMPLE)
            return {"status": "end_of_stream", "produced_windows": 0,
                    "source_end": self.next_sample}
        frames = list(self._pending)
        padded = list(frames[0]["samples"])
        padded.extend([0.0] * (ADAPTER_FRAME_SAMPLES - len(padded)))
        self._pending = []
        record = self._process_window(padded, frames)
        self.closed = True
        self._close_active_run(AVAILABILITY_ORIGIN_NS + self.next_sample * NS_PER_SAMPLE)
        return {"status": "end_of_stream", "produced_windows": 1,
                "source_end": self.next_sample, "window": record}

    def publish_external(self, event: AnalysisEvent) -> dict[str, Any]:
        """Admit an externally produced event; stale/invalid never becomes speech."""
        if event.epoch < self.epoch:
            return self._reject("stale_event_epoch", event_id=event.event_id,
                                event_epoch=event.epoch)
        if event.epoch > self.epoch:
            return self._reject("future_event_epoch", event_id=event.event_id,
                                event_epoch=event.epoch)
        if event.validity != "known":
            return self._reject("invalid_event_validity", event_id=event.event_id,
                                validity=event.validity)
        if not isinstance(event.value, (int, float)) or not math.isfinite(float(event.value)):
            return self._reject("nonfinite_event_value", event_id=event.event_id)
        if (event.source_start < self.first_sample or event.source_end <= event.source_start
                or event.source_end > self.next_sample):
            return self._reject("invalid_event_interval", event_id=event.event_id)
        if event.availability_clock_id != CLOCK_ID:
            return self._reject("invalid_event_clock", event_id=event.event_id)
        if self._last_available_ns is not None and event.available_ns < self._last_available_ns:
            return self._reject("stale_event_availability", event_id=event.event_id)
        if event.config_digest != self.config_digest:
            return self._reject("event_config_mismatch", event_id=event.event_id)
        self.events.append(event)
        return {"status": "ok", "event_id": event.event_id}

    def deliver(self, skip_sequences: Sequence[int] = ()) -> dict[str, Any]:
        """Deliver events in sequence order; record gaps instead of filling them."""
        skipped = set(int(value) for value in skip_sequences)
        delivered: list[AnalysisEvent] = []
        gaps: list[dict[str, Any]] = []
        expected = 0
        for event in self.events:
            if event.sequence in skipped:
                continue
            if event.sequence != expected:
                gaps.append({
                    "expected_sequence": expected,
                    "received_sequence": event.sequence,
                    "missing_sequences": list(range(expected, event.sequence)),
                })
            delivered.append(event)
            expected = event.sequence + 1
        self.delivered_events = delivered
        return {
            "published_count": len(self.events),
            "skipped_count": len(skipped),
            "delivered_count": len(delivered),
            "gaps": gaps,
            "dropped_sequence_count": sum(len(gap["missing_sequences"]) for gap in gaps),
            "delivered_digest": canonical_digest([event.as_dict() for event in delivered]),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "first_sample": self.first_sample,
            "config_digest": self.config_digest,
            "reset_count": self.reset_count,
            "window_count": len(self.windows),
            "frame_count": len(self.frame_decisions),
            "event_count": len(self.events),
            "probability_event_count": sum(1 for event in self.events
                                           if event.kind == "speech_probability"),
            "speech_event_count": sum(1 for event in self.events
                                      if event.kind == "speech_event"),
            "rejection_count": len(self.rejections),
            "next_sample": self.next_sample,
            "events_sha256": canonical_digest([event.as_dict() for event in self.events]),
            "windows_sha256": canonical_digest(self.windows),
        }


def score_stream(segments: Sequence[dict[str, Any]], session: Session,
                 total_samples: int) -> dict[str, Any]:
    """Score exact, gap-free frame decisions inside a fully known stream.

    Invalid and unknown samples are never converted into nonspeech here: the
    primary stream is entirely known, and adverse controls are scored in a
    separate report block with their own denominators.
    """
    decisions = session.frame_decisions
    coverage = [[item["source_start"], item["source_end"]] for item in decisions]
    merged_coverage = merge_intervals(coverage)
    coverage_ok = (len(decisions) * SDK_FRAME_SAMPLES == total_samples
                   and merged_coverage == [[0, total_samples]])
    hypothesis = merge_intervals(
        (item["source_start"], item["source_end"]) for item in decisions if item["label"]
    )
    probability_events = [event for event in session.events
                          if event.kind == "speech_probability" and event.validity == "known"]
    probability_values = [event.value for event in probability_events]
    probability_coverage_ok = merge_intervals(
        (event.source_start, event.source_end) for event in probability_events
    ) == [[0, total_samples]]
    availability_ok = all(
        event.available_ns == AVAILABILITY_ORIGIN_NS + event.source_end * NS_PER_SAMPLE
        for event in probability_events
    ) and all(
        a.available_ns <= b.available_ns
        for a, b in zip(probability_events, probability_events[1:])
    )
    finite_probabilities = all(math.isfinite(value) and 0.0 <= value <= 1.0
                               for value in probability_values)
    threshold_consistent = all(
        (item["probability"] >= 0.5) == item["label"] for item in decisions
    )

    total_tp = total_fn = total_fp = total_tn = 0
    per_segment: list[dict[str, Any]] = []
    for segment in segments:
        start, end = segment["start"], segment["end"]
        span = [[start, end]]
        overlap = intersection_length(hypothesis, span)
        if segment["speech"]:
            tp, fn, fp, tn = overlap, end - start - overlap, 0, 0
        else:
            tp, fn, fp, tn = 0, 0, overlap, end - start - overlap
        total_tp += tp
        total_fn += fn
        total_fp += fp
        total_tn += tn
        relevant = [event.value for event in probability_events
                    if event.source_start < end and event.source_end > start]
        onset = offset = None
        detection_start = detection_end = None
        if segment["speech"] and overlap:
            active = [item for item in decisions if item["label"]
                      and item["source_start"] < end and item["source_end"] > start]
            if active:
                detection_start = active[0]["source_start"]
                detection_end = active[-1]["source_end"]
                onset = active[0]["source_end"] - start
                offset = active[-1]["source_end"] - end
        per_segment.append({
            "id": segment["id"],
            "kind": segment["kind"],
            "speech": segment["speech"],
            "source_start": start,
            "source_end": end,
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "tn": tn,
            "detection_start": detection_start,
            "detection_end": detection_end,
            "onset_delay_samples": onset,
            "offset_delay_samples": offset,
            "probability_window_count": len(relevant),
            "probability_min": f32(min(relevant)) if relevant else None,
            "probability_max": f32(max(relevant)) if relevant else None,
            "probability_mean": f32(sum(relevant) / len(relevant)) if relevant else None,
        })

    speech_total = total_tp + total_fn
    nonspeech_total = total_fp + total_tn
    return {
        "status": "ok" if all((coverage_ok, probability_coverage_ok, availability_ok,
                               finite_probabilities, threshold_consistent,
                               total_samples == sum(seg["end"] - seg["start"]
                                                    for seg in segments))) else "invalid",
        "frame_count": len(decisions),
        "coverage_ok": coverage_ok,
        "probability_event_count": len(probability_events),
        "probability_coverage_ok": probability_coverage_ok,
        "availability_ok": availability_ok,
        "finite_probabilities": finite_probabilities,
        "threshold_decision_consistent": threshold_consistent,
        "hypothesis_intervals": hypothesis,
        "tp": total_tp,
        "fn": total_fn,
        "fp": total_fp,
        "tn": total_tn,
        "speech_samples": speech_total,
        "nonspeech_samples": nonspeech_total,
        "speech_miss_rate": total_fn / speech_total if speech_total else None,
        "false_alarm_rate": total_fp / nonspeech_total if nonspeech_total else None,
        "known_samples": total_samples,
        "unknown_samples": 0,
        "invalid_samples": 0,
        "per_segment": per_segment,
    }
