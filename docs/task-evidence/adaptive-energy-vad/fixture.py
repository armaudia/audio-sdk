"""Model-free deterministic fixture for an optional adaptive-energy VAD reference.

This module is task-local evidence. It wraps the historical adaptive-energy VAD
idea behind the public v0 provider format (16 kHz / mono / f32 / 160 samples)
and the proposed typed analysis-event model, without changing the installed SDK,
its ABI, descriptors, registry or defaults. Every signal is generated locally
from a seeded integer LCG and analytic speech-like tones; no corpus, weights,
download, licensed runtime or device is used.
"""

from __future__ import annotations

import hashlib
import json
import math
import numbers
import re
import struct
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/adaptive-energy-vad/0.1"
TASK_ID = "SDK-ADAPTIVE-ENERGY-VAD"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
HOP_SAMPLES = 160
NS_PER_SAMPLE = 62500
AVAILABILITY_OFFSET_NS = 5_000_000

# Historical adapter declaration. Its 320-sample frame is intentionally NOT
# used: v0 is fixed at 160 samples/frame. This divergence is a recorded blocker.
ADAPTER_FRAME_SAMPLES = 320
MIN_DBFS = -55.0
NOISE_MARGIN_DB = 8.0
NOISE_UPDATE_ALPHA = 0.01

NOISE_INIT_DBFS = -90.0
POWER_FLOOR = 1.0e-12
PROBABILITY_SCALE_DB = 3.0
ONSET_FRAMES = 2
OFFSET_FRAMES = 3
MAX_ABS_SAMPLE = 4.0
LCG_SEED = 0x5EED1234
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345
LCG_MODULUS = 1 << 31

CLOCK_ID = "monotonic-reference-v0"
PRODUCER_ID = "detection.adaptive-energy-vad.reference"
TAP_ID = "capture"
CONFIG_DIGEST = hashlib.sha256(
    json.dumps(
        {
            "minimum_dbfs": MIN_DBFS,
            "noise_margin_db": NOISE_MARGIN_DB,
            "noise_update_alpha": NOISE_UPDATE_ALPHA,
            "frame_samples": FRAME_SAMPLES,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

_HEX64 = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/adaptive-energy-vad/adapter.json":
        "b2b10b8fcfb7d54b30d4090111a251060ab4de534c59672d8c9b28528e3993f3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

BLOCKERS = [
    "adapter.json declares frame_samples=320; v0 is fixed at 160 and was not changed, so numeric parity with the historical 20 ms adapter is not claimed",
    "no held-out AMI or other frozen matched cohort with per-frame labels and rights clearance is staged in this worktree",
    "no licensed/native VAD runtime or target-device execution profile is available; no CPU, latency, availability or power claim is made",
    "analysis events are a proposal from SDK-FND-ANALYSIS, not part of the frozen v0 ABI, descriptor set or installed behavior",
]

NON_CLAIMS = [
    "No real speech, recordings, downloads, weights, corpora or licensed runtimes were used.",
    "No target-device, listening, production latency, availability, accuracy or release qualification is claimed.",
    "No SDK public API, ABI, CONTRACTS.md, CMakeLists.txt, descriptor, registry default or installed behavior was changed.",
    "Synthetic probabilities and detections are reference behavior only, not a candidate score.",
]


class Validity(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    INVALID = "invalid"


class EventKind(str, Enum):
    SPEECH_PROBABILITY = "speech_probability"
    SPEECH_EVENT = "speech_event"


class Status(str, Enum):
    OK = "ok"
    CLOSED = "closed"
    REJECTED_STALE_EPOCH = "rejected_stale_epoch"
    REJECTED_INVALID_EVENT = "rejected_invalid_event"
    REJECTED_BAD_INTERVAL = "rejected_bad_interval"
    REJECTED_BAD_CLOCK = "rejected_bad_clock"


class FrameStatus(str, Enum):
    OK = "ok"
    REJECTED_MISSING_FRAME = "rejected_missing_frame"
    REJECTED_SHORT_FRAME = "rejected_short_frame"
    REJECTED_TENSOR = "rejected_tensor"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_OUT_OF_RANGE = "rejected_out_of_range"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_INTERVAL = "rejected_interval"


@dataclass(frozen=True)
class Segment:
    name: str
    start_frame: int
    end_frame: int
    label: str
    rms_dbfs: float
    validity: Validity


SEGMENTS: tuple[Segment, ...] = (
    Segment("idle-a", 0, 60, "nonspeech", -65.0, Validity.KNOWN),
    Segment("quiet-a", 60, 120, "speech", -48.0, Validity.KNOWN),
    Segment("idle-b", 120, 150, "nonspeech", -65.0, Validity.KNOWN),
    Segment("active-a", 150, 210, "speech", -30.0, Validity.KNOWN),
    Segment("noise-burst", 210, 240, "nonspeech", -60.0, Validity.KNOWN),
    Segment("quiet-b", 240, 270, "speech", -48.0, Validity.KNOWN),
    Segment("idle-c", 270, 300, "nonspeech", -65.0, Validity.KNOWN),
    Segment("unknown-tail", 300, 330, "unknown", -65.0, Validity.UNKNOWN),
)
TOTAL_FRAMES = SEGMENTS[-1].end_frame
SCORED_END_FRAME = 300
SCORED_END_SAMPLE = SCORED_END_FRAME * FRAME_SAMPLES
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES


@dataclass(frozen=True)
class AnalysisEvent:
    event_id: str
    kind: EventKind
    producer_id: str
    tap_id: str
    epoch: int
    source_start: int
    source_end: int
    value: Optional[float]
    validity: Validity
    available_ns: Optional[int]
    availability_clock_id: str
    config_digest: str
    decision_resolution_samples: int = FRAME_SAMPLES
    lookahead_samples: int = 0

    def check(self, total_samples: Optional[int] = None) -> Optional[Status]:
        if not isinstance(self.event_id, str) or not self.event_id:
            return Status.REJECTED_INVALID_EVENT
        if self.epoch < 0:
            return Status.REJECTED_INVALID_EVENT
        if self.source_start < 0 or self.source_end <= self.source_start:
            return Status.REJECTED_BAD_INTERVAL
        if total_samples is not None and self.source_end > total_samples:
            return Status.REJECTED_BAD_INTERVAL
        if not isinstance(self.validity, Validity):
            return Status.REJECTED_INVALID_EVENT
        if not isinstance(self.config_digest, str) or not _HEX64.match(self.config_digest):
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
                value = float(self.value)
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    return Status.REJECTED_INVALID_EVENT
            elif self.value is not None:
                return Status.REJECTED_INVALID_EVENT
        if self.validity is Validity.INVALID:
            return Status.REJECTED_INVALID_EVENT
        return None


@dataclass(frozen=True)
class FrameCoverage:
    frame_index: int
    overlap_samples: int


class AnalysisBus:
    """One stream's read-only PCM view, events and dropped-event audit."""

    def __init__(self, epoch: int, first_sample: int, audio: Sequence[float],
                 clock_id: str = CLOCK_ID) -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self._audio = tuple(float(x) for x in audio)
        self.clock_id = clock_id
        self.events: list[AnalysisEvent] = []
        self.dropped: list[dict[str, Any]] = []
        self.resets: list[dict[str, Any]] = []
        self._last_available_ns: dict[str, int] = {}
        self.closed = False

    @property
    def audio_digest(self) -> str:
        return sha256_f32(self._audio)

    def audio_snapshot(self) -> tuple[float, ...]:
        return self._audio

    def publish(self, event: AnalysisEvent) -> Status:
        if self.closed:
            return self._drop(event, Status.CLOSED)
        bad = event.check(len(self._audio))
        if bad is not None:
            return self._drop(event, bad)
        if event.epoch < self.epoch:
            return self._drop(event, Status.REJECTED_STALE_EPOCH)
        if event.epoch == self.epoch and event.source_start < self.first_sample:
            return self._drop(event, Status.REJECTED_STALE_EPOCH)
        if event.validity is Validity.KNOWN and event.availability_clock_id != self.clock_id:
            return self._drop(event, Status.REJECTED_BAD_CLOCK)
        if event.available_ns is not None:
            previous = self._last_available_ns.get(event.availability_clock_id)
            if previous is not None and event.available_ns < previous:
                return self._drop(event, Status.REJECTED_BAD_CLOCK)
            self._last_available_ns[event.availability_clock_id] = event.available_ns
        self.events.append(event)
        return Status.OK

    def _drop(self, event: AnalysisEvent, reason: Status) -> Status:
        self.dropped.append({
            "event_id": event.event_id,
            "reason": reason.value,
            "epoch": event.epoch,
            "source_start": event.source_start,
            "source_end": event.source_end,
        })
        return reason

    def reset(self, new_epoch: int, first_sample: int,
              audio: Sequence[float]) -> Status:
        if new_epoch <= self.epoch or first_sample < 0:
            return Status.REJECTED_STALE_EPOCH
        self.resets.append({
            "old_epoch": self.epoch,
            "new_epoch": new_epoch,
            "cancelled_events": len(self.events),
        })
        self.epoch = new_epoch
        self.first_sample = first_sample
        self._audio = tuple(float(x) for x in audio)
        self.events.clear()
        self.dropped.clear()
        self._last_available_ns.clear()
        self.closed = False
        return Status.OK

    def close(self) -> None:
        self.closed = True


def place_events(events: Iterable[AnalysisEvent], hop: int = HOP_SAMPLES,
                 total_samples: Optional[int] = None
                 ) -> dict[str, tuple[FrameCoverage, ...]]:
    """Place known events on exact source intervals, never rounded to a hop."""
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


def sha256_f32(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for sample in samples:
        digest.update(struct.pack("<f", float(sample)))
    return digest.hexdigest()


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _is_number(value: Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def check_frame(frame: Any, final: bool = False) -> tuple[FrameStatus, int]:
    """Validate a v0-shaped frame; return status and accepted sample count."""
    if frame is None:
        return FrameStatus.REJECTED_MISSING_FRAME, 0
    if not isinstance(frame, (list, tuple)):
        return FrameStatus.REJECTED_TENSOR, 0
    count = len(frame)
    if count > FRAME_SAMPLES or count < 1:
        return FrameStatus.REJECTED_TENSOR, 0
    if not all(_is_number(x) for x in frame):
        return FrameStatus.REJECTED_TENSOR, 0
    if count < FRAME_SAMPLES and not final:
        return FrameStatus.REJECTED_SHORT_FRAME, 0
    values = [float(x) for x in frame]
    if any(not math.isfinite(x) for x in values):
        return FrameStatus.REJECTED_NONFINITE, 0
    if any(abs(x) > MAX_ABS_SAMPLE for x in values):
        return FrameStatus.REJECTED_OUT_OF_RANGE, 0
    return FrameStatus.OK, count


def frame_dbfs(samples: Sequence[float]) -> float:
    power = sum(float(x) * float(x) for x in samples) / max(1, len(samples))
    return 20.0 * math.log10(max(math.sqrt(power), math.sqrt(POWER_FLOOR)))


def speech_probability(dbfs: float, threshold_dbfs: float) -> float:
    excess = (dbfs - threshold_dbfs) / PROBABILITY_SCALE_DB
    if excess >= 40.0:
        return 1.0
    if excess <= -40.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-excess))


class AdaptiveEnergyVAD:
    """Per-session reference state; no globals and no cross-session sharing."""

    def __init__(self, epoch: int = 1, first_sample: int = 0) -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self.expected_start = first_sample
        self.noise_dbfs = NOISE_INIT_DBFS
        self.raw_run = 0
        self.idle_run = 0
        self.active = False
        self.active_start: Optional[int] = None
        self.frames: list[dict[str, Any]] = []

    def state(self) -> dict[str, Any]:
        return {
            "epoch": self.epoch,
            "expected_start": self.expected_start,
            "noise_dbfs": self.noise_dbfs,
            "raw_run": self.raw_run,
            "idle_run": self.idle_run,
            "active": self.active,
            "active_start": self.active_start,
            "frame_count": len(self.frames),
        }

    def reset(self, epoch: int, first_sample: int) -> None:
        self.__init__(epoch=epoch, first_sample=first_sample)  # type: ignore[misc]

    def process(self, frame: Any, first_sample: Optional[int] = None,
                epoch: Optional[int] = None, final: bool = False,
                validity: Validity = Validity.KNOWN) -> dict[str, Any]:
        status, count = check_frame(frame, final=final)
        if status is not FrameStatus.OK:
            return {"status": status.value, "accepted_count": count}
        if first_sample is None:
            first_sample = self.expected_start
        if epoch is None:
            epoch = self.epoch
        if epoch != self.epoch:
            return {"status": FrameStatus.REJECTED_EPOCH.value, "accepted_count": 0}
        if first_sample != self.expected_start:
            return {"status": FrameStatus.REJECTED_INTERVAL.value, "accepted_count": 0}

        samples = [f32(float(x)) for x in frame[:count]]
        source_end = first_sample + count
        dbfs = frame_dbfs(samples)
        threshold = max(MIN_DBFS, self.noise_dbfs + NOISE_MARGIN_DB)
        probability = speech_probability(dbfs, threshold)
        raw_active = probability >= 0.5
        if not raw_active:
            self.noise_dbfs += NOISE_UPDATE_ALPHA * (dbfs - self.noise_dbfs)

        if raw_active:
            self.raw_run += 1
            self.idle_run = 0
            if not self.active and self.raw_run >= ONSET_FRAMES:
                self.active = True
                self.active_start = first_sample
        else:
            self.idle_run += 1
            self.raw_run = 0
            if self.active and self.idle_run >= OFFSET_FRAMES:
                self.active = False
                self.active_start = None
        if final and self.active:
            self.active = False
            self.active_start = None

        record = {
            "status": FrameStatus.OK.value,
            "accepted_count": count,
            "source_start": first_sample,
            "source_end": source_end,
            "dbfs": dbfs,
            "noise_dbfs": self.noise_dbfs,
            "threshold_dbfs": threshold,
            "probability": probability,
            "raw_active": raw_active,
            "detected": self.active,
            "validity": validity.value,
        }
        self.frames.append(record)
        self.expected_start = source_end
        return record


class _LCG:
    def __init__(self, seed: int = LCG_SEED) -> None:
        self.state = seed & (LCG_MODULUS - 1)

    def uniform(self) -> float:
        self.state = (LCG_MULTIPLIER * self.state + LCG_INCREMENT) % LCG_MODULUS
        return (self.state / (LCG_MODULUS - 1.0)) * 2.0 - 1.0


def _segment_for_frame(index: int) -> Segment:
    for segment in SEGMENTS:
        if segment.start_frame <= index < segment.end_frame:
            return segment
    raise ValueError(f"frame {index} outside fixture")


def _generate_pcm() -> tuple[list[tuple[float, ...]], str]:
    generator = _LCG()
    frames: list[tuple[float, ...]] = []
    for index in range(TOTAL_FRAMES):
        segment = _segment_for_frame(index)
        absolute = index * FRAME_SAMPLES
        values: list[float] = []
        for offset in range(FRAME_SAMPLES):
            sample_index = absolute + offset
            if segment.label == "speech":
                phase = 2.0 * math.pi / SAMPLE_RATE_HZ
                value = (0.62 * math.sin(phase * 130.0 * sample_index)
                         + 0.27 * math.sin(phase * 263.0 * sample_index)
                         + 0.11 * math.sin(phase * 401.0 * sample_index))
            else:
                value = generator.uniform()
            values.append(value)
    # Rescale per frame to the declared RMS; the LCG keeps noise deterministic.
        power = sum(value * value for value in values) / FRAME_SAMPLES
        target = 10.0 ** (segment.rms_dbfs / 20.0)
        scale = target / math.sqrt(power)
        frames.append(tuple(f32(value * scale) for value in values))
    flat = [sample for frame in frames for sample in frame]
    return frames, sha256_f32(flat)


def _make_event(event_id: str, kind: EventKind, start: int, end: int,
                value: Optional[float], validity: Validity,
                available_ns: Optional[int], epoch: int = 1) -> AnalysisEvent:
    return AnalysisEvent(
        event_id=event_id,
        kind=kind,
        producer_id=PRODUCER_ID,
        tap_id=TAP_ID,
        epoch=epoch,
        source_start=start,
        source_end=end,
        value=value,
        validity=validity,
        available_ns=available_ns,
        availability_clock_id=CLOCK_ID,
        config_digest=CONFIG_DIGEST,
        decision_resolution_samples=FRAME_SAMPLES,
        lookahead_samples=0,
    )


def _detection_runs(records: Sequence[dict[str, Any]]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: Optional[int] = None
    for index, record in enumerate(records):
        active = record["detected"] and record["validity"] == Validity.KNOWN.value
        if active and start is None:
            start = index
        elif not active and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(records)))
    return runs


def _score(records: Sequence[dict[str, Any]],
           runs: Sequence[tuple[int, int]]) -> dict[str, Any]:
    stratified: dict[str, dict[str, int]] = {
        segment.name: {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
        for segment in SEGMENTS if segment.validity is Validity.KNOWN
    }
    totals = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for index in range(SCORED_END_FRAME):
        record = records[index]
        truth = _segment_for_frame(index).label == "speech"
        detected = bool(record["detected"])
        key = ("tp" if truth and detected else
               "fn" if truth else "fp" if detected else "tn")
        totals[key] += 1
        stratified[_segment_for_frame(index).name][key] += 1

    timings: list[dict[str, Any]] = []
    for segment in SEGMENTS:
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
            "onset_delay_samples": (onset - segment.start_frame) * FRAME_SAMPLES,
            "offset_delay_samples": (offset - segment.end_frame) * FRAME_SAMPLES,
            "detected_frames": offset - onset,
            "truth_frames": segment.end_frame - segment.start_frame,
        })

    speech_total = totals["tp"] + totals["fn"]
    nonspeech_total = totals["tn"] + totals["fp"]
    return {
        "totals": totals,
        "stratified": stratified,
        "timings": timings,
        "speech_miss_rate": totals["fn"] / speech_total if speech_total else None,
        "false_alarm_rate": totals["fp"] / nonspeech_total if nonspeech_total else None,
        "scored_samples": SCORED_END_SAMPLE,
        "unknown_samples": TOTAL_SAMPLES - SCORED_END_SAMPLE,
        "unknown_validity_events": sum(
            1 for record in records if record["validity"] == Validity.UNKNOWN.value),
    }


def invalid_vs_nonspeech_control() -> dict[str, Any]:
    """Known zero is nonspeech; invalid and unknown are never nonspeech."""
    bus = AnalysisBus(epoch=1, first_sample=0, audio=[0.0] * (2 * FRAME_SAMPLES))
    known_zero = _make_event("known-zero", EventKind.SPEECH_PROBABILITY,
                             0, FRAME_SAMPLES, 0.0, Validity.KNOWN,
                             AVAILABILITY_OFFSET_NS)
    nan = _make_event("nan", EventKind.SPEECH_PROBABILITY,
                      FRAME_SAMPLES, 2 * FRAME_SAMPLES, float("nan"),
                      Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS)
    out_of_range = _make_event("range", EventKind.SPEECH_PROBABILITY,
                               FRAME_SAMPLES, 2 * FRAME_SAMPLES, 1.5,
                               Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS)
    unknown = _make_event("unknown", EventKind.SPEECH_PROBABILITY,
                          FRAME_SAMPLES, 2 * FRAME_SAMPLES, 0.9,
                          Validity.UNKNOWN, None)
    statuses = {
        "known_zero": bus.publish(known_zero).value,
        "nan_probability": bus.publish(nan).value,
        "out_of_range_probability": bus.publish(out_of_range).value,
        "unknown_probability": bus.publish(unknown).value,
    }
    known = [event for event in bus.events if event.validity is Validity.KNOWN]
    return {
        "statuses": statuses,
        "known_nonspeech_events": len(known),
        "invalid_events_excluded": 2,
        "unknown_events_excluded": 1,
        "invalid_counted_as_nonspeech": False,
        "admitted_event_ids": [event.event_id for event in bus.events],
    }


def frame_adverse_control() -> dict[str, Any]:
    vad = AdaptiveEnergyVAD(epoch=1, first_sample=0)
    baseline = vad.state()
    cases: dict[str, Any] = {}
    probes = {
        "missing": None,
        "nonfinite": [float("nan")] + [0.0] * (FRAME_SAMPLES - 1),
        "infinite": [float("inf")] + [0.0] * (FRAME_SAMPLES - 1),
        "short": [0.0] * (FRAME_SAMPLES - 1),
        "long": [0.0] * (FRAME_SAMPLES + 1),
        "wrong_shape": [[0.0] * FRAME_SAMPLES],
    }
    for name, frame in probes.items():
        cases[name] = vad.process(frame, first_sample=0, epoch=1)["status"]
    cases["state_unchanged"] = vad.state() == baseline
    short_final = vad.process([0.0] * 80, first_sample=0, epoch=1, final=True)
    cases["short_final_status"] = short_final["status"]
    cases["short_final_valid_count"] = short_final["accepted_count"]
    cases["short_final_source_end"] = short_final["source_end"]
    cases["stale_epoch"] = vad.process([0.0] * FRAME_SAMPLES,
                                       first_sample=0, epoch=0)["status"]
    cases["wrong_interval"] = vad.process([0.0] * FRAME_SAMPLES,
                                          first_sample=320, epoch=1)["status"]
    return cases


def event_adverse_control() -> dict[str, Any]:
    # The stream starts at sample 160, so interval 0..160 is stale for epoch 1.
    bus = AnalysisBus(epoch=1, first_sample=FRAME_SAMPLES,
                      audio=[0.0] * (3 * FRAME_SAMPLES))
    baseline = _make_event("baseline", EventKind.SPEECH_PROBABILITY,
                           FRAME_SAMPLES, 2 * FRAME_SAMPLES, 0.2,
                           Validity.KNOWN, AVAILABILITY_OFFSET_NS)
    if bus.publish(baseline) is not Status.OK:
        raise AssertionError("baseline event rejected")
    before = len(bus.events)
    stale = _make_event("stale", EventKind.SPEECH_PROBABILITY, 0,
                        FRAME_SAMPLES, 0.5, Validity.KNOWN,
                        AVAILABILITY_OFFSET_NS, epoch=0)
    before_start = _make_event("before-start", EventKind.SPEECH_PROBABILITY,
                               0, FRAME_SAMPLES, 0.5, Validity.KNOWN,
                               AVAILABILITY_OFFSET_NS, epoch=1)
    stale_availability = _make_event("old-availability",
                                     EventKind.SPEECH_PROBABILITY,
                                     FRAME_SAMPLES, 2 * FRAME_SAMPLES,
                                     0.5, Validity.KNOWN, 0, epoch=1)
    bad_clock = _make_event("bad-clock", EventKind.SPEECH_PROBABILITY,
                            FRAME_SAMPLES, 2 * FRAME_SAMPLES, 0.5,
                            Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS,
                            epoch=1)
    bad_clock = AnalysisEvent(**{**bad_clock.__dict__,
                                 "availability_clock_id": "other-clock"})
    statuses = {
        "stale_epoch": bus.publish(stale).value,
        "before_first_sample": bus.publish(before_start).value,
        "stale_availability": bus.publish(stale_availability).value,
        "wrong_clock": bus.publish(bad_clock).value,
    }
    return {
        "statuses": statuses,
        "events_unchanged": len(bus.events) == before,
        "dropped_reasons": [item["reason"] for item in bus.dropped],
    }


def independence_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    left = AdaptiveEnergyVAD(epoch=1, first_sample=0)
    right = AdaptiveEnergyVAD(epoch=7, first_sample=3200)
    for frame in frames[:10]:
        left.process(frame, epoch=1)
        right.process(frame, epoch=7)
    for frame in frames[60:65]:
        left.process(frame, epoch=1)
    for frame in frames[210:215]:
        right.process(frame, epoch=7)
    before = (left.noise_dbfs, right.noise_dbfs)
    left.reset(epoch=2, first_sample=0)
    for frame in frames[:10]:
        left.process(frame, epoch=2)
    for frame in frames[60:65]:
        left.process(frame, epoch=2)
    return {
        "left_noise_before_reset": before[0],
        "right_noise_before_reset": before[1],
        "independent_noise_estimates": before[0] != before[1],
        "reset_matches_fresh_run": math.isclose(left.noise_dbfs, before[0],
                                                rel_tol=0.0, abs_tol=1e-12),
        "left_epoch": left.epoch,
        "right_epoch": right.epoch,
        "left_frames": len(left.frames),
        "right_frames": len(right.frames),
    }


def overlapping_session_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    first = AnalysisBus(epoch=1, first_sample=0, audio=[x for f in frames[:160] for x in f])
    second = AnalysisBus(epoch=2, first_sample=160 * FRAME_SAMPLES,
                         audio=[x for f in frames[160:320] for x in f])
    event = _make_event("first-only", EventKind.SPEECH_PROBABILITY, 0,
                        FRAME_SAMPLES, 0.25, Validity.KNOWN,
                        AVAILABILITY_OFFSET_NS, epoch=1)
    accepted = first.publish(event).value
    rejected = second.publish(event).value
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
    event = _make_event("cross-hop", EventKind.SPEECH_PROBABILITY, 150, 330,
                        0.75, Validity.KNOWN, AVAILABILITY_OFFSET_NS)
    placed = place_events([event], total_samples=480)["cross-hop"]
    return {
        "source_interval": [150, 330],
        "placement": [[item.frame_index, item.overlap_samples] for item in placed],
        "exact": [(item.frame_index, item.overlap_samples) for item in placed]
                 == [(0, 10), (1, 160), (2, 10)],
        "total_overlap": sum(item.overlap_samples for item in placed),
    }


def build_report() -> dict[str, Any]:
    frames, pcm_digest = _generate_pcm()
    vad = AdaptiveEnergyVAD(epoch=1, first_sample=0)
    records: list[dict[str, Any]] = []
    for index, frame in enumerate(frames):
        segment = _segment_for_frame(index)
        record = vad.process(list(frame), first_sample=index * FRAME_SAMPLES,
                             epoch=1, validity=segment.validity)
        if record["status"] != FrameStatus.OK.value:
            raise AssertionError(f"fixture frame {index} rejected: {record}")
        record["segment"] = segment.name
        record["label"] = segment.label
        records.append(record)

    flat = [sample for frame in frames for sample in frame]
    bus = AnalysisBus(epoch=1, first_sample=0, audio=flat)
    probability_rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        validity = Validity(record["validity"])
        available = (None if validity is Validity.UNKNOWN else
                     record["source_end"] * NS_PER_SAMPLE + AVAILABILITY_OFFSET_NS)
        event = _make_event(f"p-{index:04d}", EventKind.SPEECH_PROBABILITY,
                            record["source_start"], record["source_end"],
                            record["probability"], validity, available)
        status = bus.publish(event)
        if status is not Status.OK:
            raise AssertionError(f"probability event {index} rejected: {status}")
        probability_rows.append({
            "event_id": event.event_id,
            "source_start": event.source_start,
            "source_end": event.source_end,
            "value": event.value,
            "validity": event.validity.value,
            "available_ns": event.available_ns,
        })

    runs = _detection_runs(records)
    speech_rows: list[dict[str, Any]] = []
    for run_index, (start, end) in enumerate(runs):
        start_sample = start * FRAME_SAMPLES
        end_sample = end * FRAME_SAMPLES
        # Boundary events are emitted after the probability stream is reviewed;
        # their availability is the decision finalization time, not source time.
        event = _make_event(
            f"speech-{run_index:02d}", EventKind.SPEECH_EVENT,
            start_sample, end_sample, None, Validity.KNOWN,
            (TOTAL_SAMPLES + run_index + 1) * NS_PER_SAMPLE
            + AVAILABILITY_OFFSET_NS)
        status = bus.publish(event)
        if status is not Status.OK:
            raise AssertionError(f"speech event {run_index} rejected: {status}")
        speech_rows.append({
            "event_id": event.event_id,
            "source_start": start_sample,
            "source_end": end_sample,
            "onset_frame": start,
            "offset_frame": end,
        })

    score = _score(records, runs)
    spec = {
        "contract": CONTRACT_ID,
        "generator": "task-local-lcg-v1",
        "lcg_seed": LCG_SEED,
        "frame_samples": FRAME_SAMPLES,
        "segments": [
            {
                "name": segment.name,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "label": segment.label,
                "rms_dbfs": segment.rms_dbfs,
                "validity": segment.validity.value,
            }
            for segment in SEGMENTS
        ],
        "config": {
            "minimum_dbfs": MIN_DBFS,
            "noise_margin_db": NOISE_MARGIN_DB,
            "noise_update_alpha": NOISE_UPDATE_ALPHA,
            "noise_init_dbfs": NOISE_INIT_DBFS,
            "onset_frames": ONSET_FRAMES,
            "offset_frames": OFFSET_FRAMES,
            "probability_scale_db": PROBABILITY_SCALE_DB,
            "adapter_frame_samples": ADAPTER_FRAME_SAMPLES,
        },
    }
    spec_digest = sha256_text(canonical(spec))
    controls = {
        "invalid_vs_nonspeech": invalid_vs_nonspeech_control(),
        "frame_adverse": frame_adverse_control(),
        "event_adverse": event_adverse_control(),
        "independent_state": independence_control(frames),
        "overlapping_sessions": overlapping_session_control(frames),
        "cross_hop": cross_hop_control(),
        "source_intervals": {
            "probability_intervals_contiguous": all(
                row["source_start"] == index * FRAME_SAMPLES
                and row["source_end"] == (index + 1) * FRAME_SAMPLES
                for index, row in enumerate(probability_rows)),
            "speech_events_frame_aligned": all(
                row["source_start"] % FRAME_SAMPLES == 0
                and row["source_end"] % FRAME_SAMPLES == 0
                for row in speech_rows),
            "speech_events_inside_scored_region": all(
                row["source_end"] <= SCORED_END_SAMPLE for row in speech_rows),
        },
        "availability": {
            "offset_ns": AVAILABILITY_OFFSET_NS,
            "probability_availability_monotonic": all(
                left["available_ns"] < right["available_ns"]
                for left, right in zip(probability_rows, probability_rows[1:])
                if left["available_ns"] is not None
                and right["available_ns"] is not None),
            "unknown_events_have_no_availability": all(
                row["available_ns"] is None for row in probability_rows
                if row["validity"] == Validity.UNKNOWN.value),
        },
    }
    return {
        "contract": CONTRACT_ID,
        "task": TASK_ID,
        "status": {
            "claim": "proposal-only-synthetic",
            "qualification": "incomplete",
            "installed_sdk_changed": False,
        },
        "source_pins": SOURCE_PINS,
        "fixture": {
            "generator": spec["generator"],
            "spec_digest": spec_digest,
            "config_digest": CONFIG_DIGEST,
            "total_frames": TOTAL_FRAMES,
            "total_samples": TOTAL_SAMPLES,
            "scored_end_frame": SCORED_END_FRAME,
            "scored_end_sample": SCORED_END_SAMPLE,
            "segments": spec["segments"],
        },
        "digests": {
            "pcm_f32_sha256": pcm_digest,
            "probability_stream_sha256": sha256_text(canonical(probability_rows)),
            "speech_events_sha256": sha256_text(canonical(speech_rows)),
            "audio_view_sha256": bus.audio_digest,
        },
        "counts": {
            "probability_events_known": sum(
                1 for row in probability_rows if row["validity"] == "known"),
            "probability_events_unknown": sum(
                1 for row in probability_rows if row["validity"] == "unknown"),
            "speech_events": len(speech_rows),
            "bus_events": len(bus.events),
            "bus_dropped_events": len(bus.dropped),
            **score["totals"],
        },
        "scoring": score,
        "probability_stream": probability_rows,
        "speech_events": speech_rows,
        "adverse_controls": controls,
        "blockers": BLOCKERS,
        "non_claims": NON_CLAIMS,
    }


def main() -> None:
    report = build_report()
    text = canonical(report)
    Path(__file__).with_name("report.json").write_text(text, encoding="utf-8")
    counts = report["counts"]
    print(
        "report.json: "
        f"frames={report['fixture']['total_frames']} "
        f"tp={counts['tp']} fn={counts['fn']} fp={counts['fp']} tn={counts['tn']} "
        f"pcm={report['digests']['pcm_f32_sha256']} "
        f"report={sha256_text(text)}"
    )


if __name__ == "__main__":
    main()
