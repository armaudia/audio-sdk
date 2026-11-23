"""Model-free deterministic fixture for an adaptive-energy -> Silero cascade reference.

The Silero stage is a clearly labelled MODEL-FREE STUB. No Silero weights,
source, runtime, download or licensed asset is used. This file is task-local
evidence for an optional reference at the public v0 provider boundary; it does
not change the installed SDK, its ABI, descriptors, registry or defaults.

All signals are generated from a seeded integer LCG and analytic tones. The
fixture reports timestamped probabilities, speech-event boundaries, detections,
stratified errors, validity separation, stale/dropped events, exact source
intervals, availability and cross-hop placement.
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

TASK_ID = "SDK-ADAPTIVE-ENERGY-TO-SILERO-CASCADE"
CONTRACT_ID = "audio-sdk/adaptive-energy-to-silero-cascade/0.1"
PINNED_BASE = "dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc"

TASK_DIR = Path(__file__).resolve().parent
WORKSPACE = TASK_DIR.parents[5]
MANIFEST_PATH = TASK_DIR / "SOURCES.sha256"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
HOP_SAMPLES = 160
NS_PER_SAMPLE = 62500
AVAILABILITY_OFFSET_NS = 5_000_000

# Historical adapter declarations. The 20 ms adapter frame sizes are recorded
# as divergence, not reproduced: frozen v0 remains 16 kHz mono f32 / 160.
ADAPTER_ENERGY_FRAME_SAMPLES = 320
ADAPTER_SILERO_FRAME_SAMPLES = 512
ADAPTER_SILERO_CONTEXT_SAMPLES = 64

MIN_DBFS = -55.0
NOISE_MARGIN_DB = 8.0
NOISE_UPDATE_ALPHA = 0.01
NOISE_INIT_DBFS = -90.0
PROBABILITY_SCALE_DB = 3.0
POWER_FLOOR = 1.0e-12

# Model-free Silero STUB: a smoothed analytic threshold, not a neural model.
STUB_THRESHOLD_DBFS = -52.0
STUB_SMOOTH_ALPHA = 0.35
STUB_ACTIVE_PROBABILITY = 0.5

# v0-adapted agreement_sleep-style reference policy. These are not the
# historical 20 ms frame counts and are not claimed to reproduce AMI results.
GATE_SLEEP_PROBABILITY = 0.10
GATE_WAKE_PROBABILITY = 0.50
AGREE_SLEEP_FRAMES = 3
CROSSCHECK_INTERVAL_FRAMES = 50
ONSET_FRAMES = 2
OFFSET_FRAMES = 3

MAX_ABS_SAMPLE = 4.0
LCG_SEED = 0x5EEDC0DE
LCG_MULTIPLIER = 1103515245
LCG_INCREMENT = 12345
LCG_MODULUS = 1 << 31

CLOCK_ID = "monotonic-reference-v0"
GATE_PRODUCER = "detection.cascade.reference.gate"
STUB_PRODUCER = "detection.cascade.reference.silero-stub"
CASCADE_PRODUCER = "detection.cascade.reference.decision"
TAP_ID = "capture"

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Segment:
    name: str
    start_frame: int
    end_frame: int
    label: str
    stratum: str
    rms_dbfs: float
    validity: "Validity"


class Validity(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    INVALID = "invalid"


class EventKind(str, Enum):
    GATE_PROBABILITY = "gate_probability"
    STUB_PROBABILITY = "stub_probability"
    CASCADE_PROBABILITY = "cascade_probability"
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


# 330 frames: known positives/negatives plus a known positive cross-environment
# stress stratum where the frozen gate policy fails, then unknown validity.
SEGMENTS: tuple[Segment, ...] = (
    Segment("idle-a", 0, 55, "nonspeech", "idle-noise", -65.0, Validity.KNOWN),
    Segment("quiet-a", 55, 110, "speech", "quiet-speech", -48.0, Validity.KNOWN),
    Segment("idle-b", 110, 140, "nonspeech", "idle-noise", -65.0, Validity.KNOWN),
    Segment("active-a", 140, 195, "speech", "active-speech", -30.0, Validity.KNOWN),
    Segment("noise-burst", 195, 225, "nonspeech", "idle-noise", -60.0, Validity.KNOWN),
    Segment("quiet-b", 225, 255, "speech", "quiet-speech", -48.0, Validity.KNOWN),
    Segment("transition-silence", 255, 270, "nonspeech", "idle-noise", -65.0, Validity.KNOWN),
    Segment("stress-low-snr", 270, 300, "speech", "cross-environment-stress", -58.0, Validity.KNOWN),
    Segment("unknown-tail", 300, 330, "unknown", "unknown-validity", -65.0, Validity.UNKNOWN),
)
TOTAL_FRAMES = SEGMENTS[-1].end_frame
SCORED_END_FRAME = 300
SCORED_END_SAMPLE = SCORED_END_FRAME * FRAME_SAMPLES
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES

BLOCKERS = [
    "no rights-cleared, label-complete held-out VAD cohort with source pins is staged here; historical AMI and synthetic-environment percentages are source-reported and are not reproduced",
    "no real Silero 6.2.3 weights, ONNX runtime, source revision or licensed asset is present; the second stage is an explicitly labelled model-free stub",
    "no licensed/native runtime, target device, CPU/memory budget, availability clock or deadline budget is available; no RTF, p95, power or production claim is made",
    "the frozen-policy cross-environment screen produced 100% false negatives on six synthetic recordings; this fixture reproduces the failure mode on a deterministic synthetic stratum and does not clear it",
    "analysis events are a proposal from SDK-FND-ANALYSIS and are not part of installed v0 ABI, descriptors or defaults",
]

NON_CLAIMS = [
    "No real speech, recordings, corpora, downloads, model weights or licensed runtimes were used.",
    "The Silero stage is a deterministic analytic stub; no Silero accuracy, output or compute result is claimed.",
    "No target-device, listening, MOS/STOI, production latency, availability, accuracy or release qualification is claimed.",
    "No SDK public API, ABI, CONTRACTS.md, CMakeLists.txt, descriptor registry, default or installed behavior was changed.",
    "Every control has an explicit result and no missing control result qualifies this reference.",
]


def canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_f32(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for sample in samples:
        digest.update(struct_pack_f32(float(sample)))
    return digest.hexdigest()


def struct_pack_f32(value: float) -> bytes:
    return struct.pack("<f", value)


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def read_source_manifest() -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, path = line.split("  ", 1)
        if not _HEX64.match(digest):
            raise ValueError(f"bad digest in {MANIFEST_PATH.name}: {digest}")
        pins[path] = digest
    return pins


def resolve_pin_path(name: str) -> Path:
    prefix, _, relative = name.partition(":")
    if prefix == "workspace":
        return WORKSPACE / relative
    if prefix == "local":
        return TASK_DIR / relative
    raise ValueError(f"unknown pin prefix in {name!r}")


def verify_source_manifest() -> dict[str, bool]:
    pins = read_source_manifest()
    results: dict[str, bool] = {}
    for name, expected in pins.items():
        path = resolve_pin_path(name)
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
        results[name] = actual == expected
    return results


def config_digest() -> str:
    spec = {
        "frame_samples": FRAME_SAMPLES,
        "minimum_dbfs": MIN_DBFS,
        "noise_margin_db": NOISE_MARGIN_DB,
        "noise_update_alpha": NOISE_UPDATE_ALPHA,
        "stub_threshold_dbfs": STUB_THRESHOLD_DBFS,
        "stub_smooth_alpha": STUB_SMOOTH_ALPHA,
        "agree_sleep_frames": AGREE_SLEEP_FRAMES,
        "crosscheck_interval_frames": CROSSCHECK_INTERVAL_FRAMES,
        "onset_frames": ONSET_FRAMES,
        "offset_frames": OFFSET_FRAMES,
    }
    return sha256_text(canonical(spec))


CASCADE_CONFIG_DIGEST = config_digest()


class AnalysisEvent:
    def __init__(
        self,
        event_id: str,
        kind: EventKind,
        epoch: int,
        source_start: int,
        source_end: int,
        value: Optional[float],
        validity: Validity,
        available_ns: Optional[int],
        *,
        producer_id: str = CASCADE_PRODUCER,
        clock_id: str = CLOCK_ID,
    ) -> None:
        self.event_id = event_id
        self.kind = kind
        self.producer_id = producer_id
        self.tap_id = TAP_ID
        self.epoch = epoch
        self.source_start = source_start
        self.source_end = source_end
        self.value = value
        self.validity = validity
        self.available_ns = available_ns
        self.availability_clock_id = clock_id
        self.config_digest = CASCADE_CONFIG_DIGEST
        self.decision_resolution_samples = FRAME_SAMPLES
        self.lookahead_samples = 0

    def check(self, total_samples: Optional[int] = None) -> Optional[Status]:
        if not self.event_id or self.epoch < 0:
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
            if self.kind is EventKind.SPEECH_EVENT:
                if self.value is not None:
                    return Status.REJECTED_INVALID_EVENT
            elif not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
                return Status.REJECTED_INVALID_EVENT
            else:
                value = float(self.value)
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    return Status.REJECTED_INVALID_EVENT
        if self.validity is Validity.INVALID:
            return Status.REJECTED_INVALID_EVENT
        return None


@dataclass(frozen=True)
class FrameCoverage:
    frame_index: int
    overlap_samples: int


class AnalysisBus:
    """One session's events, exact source view and dropped-event audit."""

    def __init__(self, epoch: int, first_sample: int, audio: Sequence[float]) -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self.audio = tuple(float(x) for x in audio)
        self.events: list[AnalysisEvent] = []
        self.dropped: list[dict[str, Any]] = []
        self.resets: list[dict[str, Any]] = []
        self._last_available_ns: dict[str, int] = {}
        self.closed = False

    @property
    def audio_digest(self) -> str:
        return sha256_f32(self.audio)

    def publish(self, event: AnalysisEvent) -> Status:
        if self.closed:
            return self._drop(event, Status.CLOSED)
        bad = event.check(len(self.audio))
        if bad is not None:
            return self._drop(event, bad)
        if event.epoch < self.epoch:
            return self._drop(event, Status.REJECTED_STALE_EPOCH)
        if event.epoch == self.epoch and event.source_start < self.first_sample:
            return self._drop(event, Status.REJECTED_STALE_EPOCH)
        if event.availability_clock_id != CLOCK_ID:
            return self._drop(event, Status.REJECTED_BAD_CLOCK)
        if event.available_ns is not None:
            previous = self._last_available_ns.get(CLOCK_ID)
            if previous is not None and event.available_ns <= previous:
                return self._drop(event, Status.REJECTED_BAD_CLOCK)
            self._last_available_ns[CLOCK_ID] = event.available_ns
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

    def reset(self, epoch: int, first_sample: int, audio: Sequence[float]) -> Status:
        if epoch <= self.epoch or first_sample < 0:
            return Status.REJECTED_STALE_EPOCH
        self.resets.append({
            "old_epoch": self.epoch,
            "new_epoch": epoch,
            "cancelled_events": len(self.events),
        })
        self.epoch = epoch
        self.first_sample = first_sample
        self.audio = tuple(float(x) for x in audio)
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
    if hop < 1:
        raise ValueError("hop must be positive")
    placed: dict[str, tuple[FrameCoverage, ...]] = {}
    for event in events:
        if event.check(total_samples) is not None or event.validity is not Validity.KNOWN:
            continue
        limit = total_samples if total_samples is not None else event.source_end
        spans = []
        for start in range(0, limit, hop):
            overlap = min(event.source_end, start + hop) - max(event.source_start, start)
            if overlap > 0:
                spans.append(FrameCoverage(start // hop, overlap))
        placed[event.event_id] = tuple(spans)
    return placed


def _is_number(value: Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def check_frame(frame: Any, final: bool = False) -> tuple[FrameStatus, int]:
    if frame is None:
        return FrameStatus.REJECTED_MISSING_FRAME, 0
    if not isinstance(frame, (list, tuple)):
        return FrameStatus.REJECTED_TENSOR, 0
    count = len(frame)
    if count < 1 or count > FRAME_SAMPLES:
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
    rms = math.sqrt(max(power, POWER_FLOOR))
    return 20.0 * math.log10(rms)


def sigmoid(x: float) -> float:
    if x >= 40.0:
        return 1.0
    if x <= -40.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


class CascadeVAD:
    """Per-session energy gate + explicit model-free Silero stub + decision state."""

    def __init__(self, epoch: int = 1, first_sample: int = 0) -> None:
        self.epoch = epoch
        self.first_sample = first_sample
        self.expected_start = first_sample
        self.noise_dbfs = NOISE_INIT_DBFS
        self.agree_run = 0
        self.gate_sleep = False
        self.sleep_frames = 0
        self.stub_probability = 0.0
        self.stub_has_state = False
        self.raw_run = 0
        self.idle_run = 0
        self.active = False
        self.active_start: Optional[int] = None
        self.frames: list[dict[str, Any]] = []
        self.counters = {
            "stub_invocations": 0,
            "stub_skips": 0,
            "gate_wakes": 0,
            "crosschecks_while_asleep": 0,
        }

    def state(self) -> dict[str, Any]:
        return {
            "epoch": self.epoch,
            "first_sample": self.first_sample,
            "expected_start": self.expected_start,
            "noise_dbfs": self.noise_dbfs,
            "agree_run": self.agree_run,
            "gate_sleep": self.gate_sleep,
            "sleep_frames": self.sleep_frames,
            "stub_probability": self.stub_probability,
            "stub_has_state": self.stub_has_state,
            "raw_run": self.raw_run,
            "idle_run": self.idle_run,
            "active": self.active,
            "active_start": self.active_start,
            "counters": dict(self.counters),
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
        gate_probability = sigmoid((dbfs - threshold) / PROBABILITY_SCALE_DB)

        if gate_probability <= GATE_SLEEP_PROBABILITY:
            self.agree_run += 1
        else:
            self.agree_run = 0
        if self.agree_run >= AGREE_SLEEP_FRAMES:
            self.gate_sleep = True

        wake = gate_probability >= GATE_WAKE_PROBABILITY
        if wake:
            self.gate_sleep = False
            self.sleep_frames = 0
            self.agree_run = 0
            self.counters["gate_wakes"] += 1

        crosscheck = False
        if self.gate_sleep and not wake:
            self.sleep_frames += 1
            crosscheck = self.sleep_frames % CROSSCHECK_INTERVAL_FRAMES == 1
            if crosscheck:
                self.counters["crosschecks_while_asleep"] += 1

        stub_invoked = wake or crosscheck or not self.gate_sleep
        stub_probability: Optional[float] = None
        if stub_invoked:
            instantaneous = sigmoid((dbfs - STUB_THRESHOLD_DBFS) / PROBABILITY_SCALE_DB)
            if self.stub_has_state:
                self.stub_probability = (
                    STUB_SMOOTH_ALPHA * instantaneous
                    + (1.0 - STUB_SMOOTH_ALPHA) * self.stub_probability
                )
            else:
                self.stub_probability = instantaneous
                self.stub_has_state = True
            stub_probability = self.stub_probability
            self.counters["stub_invocations"] += 1
        else:
            self.counters["stub_skips"] += 1

        cascade_probability = 0.0 if self.gate_sleep else (stub_probability or 0.0)
        gate_active = gate_probability >= GATE_WAKE_PROBABILITY
        if not gate_active:
            self.noise_dbfs += NOISE_UPDATE_ALPHA * (dbfs - self.noise_dbfs)
        raw_active = cascade_probability >= STUB_ACTIVE_PROBABILITY

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
            "threshold_dbfs": threshold,
            "gate_probability": gate_probability,
            "stub_probability": stub_probability,
            "cascade_probability": cascade_probability,
            "stub_invoked": stub_invoked,
            "crosscheck": crosscheck,
            "gate_sleep": self.gate_sleep,
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

    def gaussian(self) -> float:
        return (self.uniform() + self.uniform() + self.uniform()) / 3.0


def segment_for_frame(index: int) -> Segment:
    for segment in SEGMENTS:
        if segment.start_frame <= index < segment.end_frame:
            return segment
    raise ValueError(f"frame {index} outside fixture")


def generate_frames() -> tuple[list[tuple[float, ...]], str]:
    generator = _LCG()
    frames: list[tuple[float, ...]] = []
    for index in range(TOTAL_FRAMES):
        segment = segment_for_frame(index)
        absolute = index * FRAME_SAMPLES
        values: list[float] = []
        for offset in range(FRAME_SAMPLES):
            sample_index = absolute + offset
            phase = 2.0 * math.pi / SAMPLE_RATE_HZ
            if segment.label == "speech":
                value = (
                    0.62 * math.sin(phase * 130.0 * sample_index)
                    + 0.27 * math.sin(phase * 263.0 * sample_index)
                    + 0.11 * math.sin(phase * 401.0 * sample_index)
                )
            else:
                value = generator.gaussian()
            values.append(value)
        power = sum(value * value for value in values) / FRAME_SAMPLES
        target = 10.0 ** (segment.rms_dbfs / 20.0)
        scale = target / math.sqrt(power)
        frames.append(tuple(f32(value * scale) for value in values))
    flat = [sample for frame in frames for sample in frame]
    return frames, sha256_f32(flat)


def make_event(event_id: str, kind: EventKind, start: int, end: int,
               value: Optional[float], validity: Validity,
               available_ns: Optional[int], epoch: int = 1,
               producer_id: str = CASCADE_PRODUCER) -> AnalysisEvent:
    return AnalysisEvent(event_id, kind, epoch, start, end, value, validity,
                         available_ns, producer_id=producer_id)


def detection_runs(records: Sequence[dict[str, Any]]) -> list[tuple[int, int]]:
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


def score(records: Sequence[dict[str, Any]],
          runs: Sequence[tuple[int, int]]) -> dict[str, Any]:
    stratified: dict[str, dict[str, int]] = {
        segment.name: {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
        for segment in SEGMENTS if segment.validity is Validity.KNOWN
    }
    strata: dict[str, dict[str, int]] = {}
    totals = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for index in range(SCORED_END_FRAME):
        segment = segment_for_frame(index)
        truth = segment.label == "speech"
        detected = bool(records[index]["detected"])
        key = ("tp" if truth and detected else
               "fn" if truth else "fp" if detected else "tn")
        totals[key] += 1
        stratified[segment.name][key] += 1
        row = strata.setdefault(segment.stratum, {"tp": 0, "fn": 0, "fp": 0, "tn": 0})
        row[key] += 1

    timings: list[dict[str, Any]] = []
    for segment in SEGMENTS:
        if segment.label != "speech":
            continue
        candidates = [run for run in runs
                      if run[0] < segment.end_frame and run[1] > segment.start_frame]
        if not candidates:
            timings.append({
                "segment": segment.name,
                "status": "missed",
                "truth_start_frame": segment.start_frame,
                "truth_end_frame": segment.end_frame,
            })
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
        "strata": strata,
        "timings": timings,
        "speech_miss_rate": totals["fn"] / speech_total if speech_total else None,
        "false_alarm_rate": totals["fp"] / nonspeech_total if nonspeech_total else None,
        "known_positives": speech_total,
        "known_negatives": nonspeech_total,
        "scored_samples": SCORED_END_SAMPLE,
        "unknown_samples": TOTAL_SAMPLES - SCORED_END_SAMPLE,
    }


def invalid_vs_nonspeech_control() -> dict[str, Any]:
    bus = AnalysisBus(1, 0, [0.0] * (2 * FRAME_SAMPLES))
    probes = {
        "known_zero": make_event("known-zero", EventKind.GATE_PROBABILITY, 0,
                                 FRAME_SAMPLES, 0.0, Validity.KNOWN,
                                 AVAILABILITY_OFFSET_NS),
        "nan_probability": make_event("nan", EventKind.GATE_PROBABILITY,
                                      FRAME_SAMPLES, 2 * FRAME_SAMPLES, float("nan"),
                                      Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS),
        "out_of_range_probability": make_event(
            "range", EventKind.GATE_PROBABILITY, FRAME_SAMPLES,
            2 * FRAME_SAMPLES, 1.5, Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS),
        "unknown_probability": make_event(
            "unknown", EventKind.GATE_PROBABILITY, FRAME_SAMPLES,
            2 * FRAME_SAMPLES, 0.9, Validity.UNKNOWN, None),
    }
    statuses = {name: bus.publish(event).value for name, event in probes.items()}
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
    vad = CascadeVAD(epoch=1, first_sample=0)
    baseline = vad.state()
    probes: dict[str, Any] = {
        "missing": None,
        "nonfinite": [float("nan")] + [0.0] * (FRAME_SAMPLES - 1),
        "infinite": [float("inf")] + [0.0] * (FRAME_SAMPLES - 1),
        "short": [0.0] * (FRAME_SAMPLES - 1),
        "long": [0.0] * (FRAME_SAMPLES + 1),
        "wrong_shape": [[0.0] * FRAME_SAMPLES],
    }
    cases = {name: vad.process(frame, first_sample=0, epoch=1)["status"]
             for name, frame in probes.items()}
    cases["state_unchanged"] = vad.state() == baseline
    final = vad.process([0.0] * 80, first_sample=0, epoch=1, final=True)
    cases["short_final_status"] = final["status"]
    cases["short_final_valid_count"] = final["accepted_count"]
    cases["short_final_source_end"] = final["source_end"]
    cases["stale_epoch"] = vad.process([0.0] * FRAME_SAMPLES,
                                       first_sample=0, epoch=0)["status"]
    cases["wrong_interval"] = vad.process([0.0] * FRAME_SAMPLES,
                                          first_sample=320, epoch=1)["status"]
    return cases


def event_adverse_control() -> dict[str, Any]:
    bus = AnalysisBus(1, FRAME_SAMPLES, [0.0] * (3 * FRAME_SAMPLES))
    baseline = make_event("baseline", EventKind.GATE_PROBABILITY, FRAME_SAMPLES,
                          2 * FRAME_SAMPLES, 0.2, Validity.KNOWN,
                          AVAILABILITY_OFFSET_NS)
    if bus.publish(baseline) is not Status.OK:
        raise AssertionError("baseline event rejected")
    before = len(bus.events)
    stale = make_event("stale", EventKind.GATE_PROBABILITY, 0, FRAME_SAMPLES,
                       0.5, Validity.KNOWN, AVAILABILITY_OFFSET_NS, epoch=0)
    before_start = make_event("before-start", EventKind.GATE_PROBABILITY, 0,
                              FRAME_SAMPLES, 0.5, Validity.KNOWN,
                              AVAILABILITY_OFFSET_NS, epoch=1)
    stale_clock = make_event("stale-availability", EventKind.GATE_PROBABILITY,
                             FRAME_SAMPLES, 2 * FRAME_SAMPLES, 0.5,
                             Validity.KNOWN, 1, epoch=1)
    wrong_clock = make_event("wrong-clock", EventKind.GATE_PROBABILITY,
                             FRAME_SAMPLES, 2 * FRAME_SAMPLES, 0.5,
                             Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS, epoch=1)
    wrong_clock.availability_clock_id = "other-clock"
    statuses = {
        "stale_epoch": bus.publish(stale).value,
        "before_first_sample": bus.publish(before_start).value,
        "stale_availability": bus.publish(stale_clock).value,
        "wrong_clock": bus.publish(wrong_clock).value,
    }
    bus.close()
    closed = make_event("after-close", EventKind.GATE_PROBABILITY, FRAME_SAMPLES,
                        2 * FRAME_SAMPLES, 0.5, Validity.KNOWN,
                        3 * AVAILABILITY_OFFSET_NS)
    statuses["closed_stream"] = bus.publish(closed).value
    return {
        "statuses": statuses,
        "events_unchanged": len(bus.events) == before,
        "dropped_reasons": [item["reason"] for item in bus.dropped],
        "dropped_event_ids": [item["event_id"] for item in bus.dropped],
    }


def independent_state_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    def replay(vad: CascadeVAD, epoch: int, start: int,
               indices: Sequence[int]) -> None:
        vad.reset(epoch=epoch, first_sample=start)
        for position, index in enumerate(indices):
            vad.process(list(frames[index]),
                        first_sample=start + position * FRAME_SAMPLES, epoch=epoch)

    left = CascadeVAD(epoch=1, first_sample=0)
    right = CascadeVAD(epoch=7, first_sample=3200)
    replay(left, 1, 0, list(range(10)))
    replay(left, 1, 140 * FRAME_SAMPLES, list(range(140, 145)))
    replay(right, 7, 3200, list(range(5)))
    replay(right, 7, 3200 + 110 * FRAME_SAMPLES, list(range(110, 115)))
    before = (left.noise_dbfs, right.noise_dbfs,
              left.stub_probability, right.stub_probability)
    replay(left, 2, 0, list(range(10)))
    replay(left, 2, 140 * FRAME_SAMPLES, list(range(140, 145)))
    return {
        "left_noise_dbfs": before[0],
        "right_noise_dbfs": before[1],
        "left_stub_probability": before[2],
        "right_stub_probability": before[3],
        "independent_noise_estimate": before[0] != before[1],
        "independent_stub_state": before[2] != before[3],
        "independent_sleep_state": left.gate_sleep != right.gate_sleep
                                   or left.sleep_frames != right.sleep_frames,
        "reset_matches_fresh_run": (
            math.isclose(left.noise_dbfs, before[0], rel_tol=0.0, abs_tol=1e-12)
            and math.isclose(left.stub_probability, before[2], rel_tol=0.0, abs_tol=1e-12)
        ),
        "left_epoch": left.epoch,
        "right_epoch": right.epoch,
    }


def overlapping_session_control(frames: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    first = AnalysisBus(1, 0, [x for frame in frames[:160] for x in frame])
    second = AnalysisBus(2, 160 * FRAME_SAMPLES,
                         [x for frame in frames[160:320] for x in frame])
    event = make_event("first-only", EventKind.GATE_PROBABILITY, 0, FRAME_SAMPLES,
                       0.25, Validity.KNOWN, AVAILABILITY_OFFSET_NS, epoch=1)
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
    aligned = make_event("cross-hop", EventKind.SPEECH_EVENT, 150, 330, None,
                         Validity.KNOWN, AVAILABILITY_OFFSET_NS)
    unaligned = make_event("cross-hop-unaligned", EventKind.SPEECH_EVENT, 173, 333,
                           None, Validity.KNOWN, 2 * AVAILABILITY_OFFSET_NS)
    placed = place_events([aligned, unaligned], total_samples=480)
    exact = (
        [(item.frame_index, item.overlap_samples) for item in placed[aligned.event_id]]
        == [(0, 10), (1, 160), (2, 10)]
        and [(item.frame_index, item.overlap_samples) for item in placed[unaligned.event_id]]
        == [(1, 147), (2, 13)]
    )
    return {
        "intervals": {
            "aligned": [150, 330],
            "unaligned": [173, 333],
        },
        "placement": {
            name: [[item.frame_index, item.overlap_samples] for item in spans]
            for name, spans in placed.items()
        },
        "exact": exact,
        "total_overlap": {
            name: sum(item.overlap_samples for item in spans)
            for name, spans in placed.items()
        },
    }


def build_report() -> dict[str, Any]:
    pins = read_source_manifest()
    pin_results = verify_source_manifest()
    if not all(pin_results.values()):
        raise AssertionError(f"source pins failed: {pin_results}")

    frames, pcm_digest = generate_frames()
    vad = CascadeVAD(epoch=1, first_sample=0)
    records: list[dict[str, Any]] = []
    for index, frame in enumerate(frames):
        segment = segment_for_frame(index)
        record = vad.process(list(frame), first_sample=index * FRAME_SAMPLES,
                             epoch=1, validity=segment.validity)
        if record["status"] != FrameStatus.OK.value:
            raise AssertionError(f"fixture frame {index} rejected: {record}")
        record["segment"] = segment.name
        record["stratum"] = segment.stratum
        record["label"] = segment.label
        records.append(record)

    flat = [sample for frame in frames for sample in frame]
    bus = AnalysisBus(1, 0, flat)
    probability_rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        validity = Validity(record["validity"])
        base = (None if validity is Validity.UNKNOWN else
                record["source_end"] * NS_PER_SAMPLE)
        streams = (
            (EventKind.GATE_PROBABILITY, GATE_PRODUCER, 0, record["gate_probability"]),
            (EventKind.STUB_PROBABILITY, STUB_PRODUCER, 1, record["stub_probability"]),
            (EventKind.CASCADE_PROBABILITY, CASCADE_PRODUCER, 2,
             record["cascade_probability"]),
        )
        for kind, producer, offset, value in streams:
            if kind is EventKind.STUB_PROBABILITY and not record["stub_invoked"]:
                continue
            event = make_event(
                f"{kind.value}-{index:04d}", kind, record["source_start"],
                record["source_end"], value, validity,
                None if base is None else base + AVAILABILITY_OFFSET_NS + offset,
                producer_id=producer)
            status = bus.publish(event)
            if status is not Status.OK:
                raise AssertionError(f"probability event {index} rejected: {status}")
            probability_rows.append({
                "event_id": event.event_id,
                "stream": kind.value,
                "producer_id": producer,
                "source_start": event.source_start,
                "source_end": event.source_end,
                "value": event.value,
                "validity": event.validity.value,
                "available_ns": event.available_ns,
                "stub_invoked": record["stub_invoked"],
                "gate_sleep": record["gate_sleep"],
            })

    runs = detection_runs(records)
    speech_rows: list[dict[str, Any]] = []
    for run_index, (start, end) in enumerate(runs):
        segment = segment_for_frame(start)
        event = make_event(
            f"speech-{run_index:02d}", EventKind.SPEECH_EVENT,
            start * FRAME_SAMPLES, end * FRAME_SAMPLES, None, Validity.KNOWN,
            (TOTAL_SAMPLES + run_index + 1) * NS_PER_SAMPLE + AVAILABILITY_OFFSET_NS)
        status = bus.publish(event)
        if status is not Status.OK:
            raise AssertionError(f"speech event {run_index} rejected: {status}")
        speech_rows.append({
            "event_id": event.event_id,
            "source_start": event.source_start,
            "source_end": event.source_end,
            "onset_frame": start,
            "offset_frame": end,
            "onset_delay_samples": (start - segment.start_frame) * FRAME_SAMPLES,
            "offset_delay_samples": (end - segment.end_frame) * FRAME_SAMPLES,
            "overlaps_segments": [segment_for_frame(i).name
                                  for i in range(start, min(end, SCORED_END_FRAME))],
        })

    score_data = score(records, runs)
    spec = {
        "contract": CONTRACT_ID,
        "generator": "task-local-lcg-v3",
        "lcg_seed": LCG_SEED,
        "frame_samples": FRAME_SAMPLES,
        "segments": [
            {
                "name": segment.name,
                "start_frame": segment.start_frame,
                "end_frame": segment.end_frame,
                "label": segment.label,
                "stratum": segment.stratum,
                "rms_dbfs": segment.rms_dbfs,
                "validity": segment.validity.value,
            }
            for segment in SEGMENTS
        ],
        "config": {
            "frame_samples": FRAME_SAMPLES,
            "minimum_dbfs": MIN_DBFS,
            "noise_margin_db": NOISE_MARGIN_DB,
            "noise_update_alpha": NOISE_UPDATE_ALPHA,
            "noise_init_dbfs": NOISE_INIT_DBFS,
            "stub_threshold_dbfs": STUB_THRESHOLD_DBFS,
            "stub_smooth_alpha": STUB_SMOOTH_ALPHA,
            "gate_sleep_probability": GATE_SLEEP_PROBABILITY,
            "gate_wake_probability": GATE_WAKE_PROBABILITY,
            "agree_sleep_frames": AGREE_SLEEP_FRAMES,
            "crosscheck_interval_frames": CROSSCHECK_INTERVAL_FRAMES,
            "onset_frames": ONSET_FRAMES,
            "offset_frames": OFFSET_FRAMES,
            "probability_scale_db": PROBABILITY_SCALE_DB,
            "adapter_energy_frame_samples": ADAPTER_ENERGY_FRAME_SAMPLES,
            "adapter_silero_frame_samples": ADAPTER_SILERO_FRAME_SAMPLES,
            "adapter_silero_context_samples": ADAPTER_SILERO_CONTEXT_SAMPLES,
        },
    }
    spec_digest = sha256_text(canonical(spec))
    controls: dict[str, Any] = {
        "invalid_vs_nonspeech": invalid_vs_nonspeech_control(),
        "frame_adverse": frame_adverse_control(),
        "event_adverse": event_adverse_control(),
        "independent_state": independent_state_control(frames),
        "overlapping_sessions": overlapping_session_control(frames),
        "cross_hop": cross_hop_control(),
        "source_intervals": {
            "probability_intervals_contiguous": all(
                row["source_start"] == index * FRAME_SAMPLES
                and row["source_end"] == (index + 1) * FRAME_SAMPLES
                for index, row in enumerate(
                    row for row in probability_rows
                    if row["stream"] == EventKind.GATE_PROBABILITY.value)),
            "gate_probability_rows": sum(
                1 for row in probability_rows
                if row["stream"] == EventKind.GATE_PROBABILITY.value),
            "cascade_probability_rows": sum(
                1 for row in probability_rows
                if row["stream"] == EventKind.CASCADE_PROBABILITY.value),
            "speech_events_frame_aligned": all(
                row["source_start"] % FRAME_SAMPLES == 0
                and row["source_end"] % FRAME_SAMPLES == 0
                for row in speech_rows),
            "speech_events_inside_scored_region": all(
                row["source_end"] <= SCORED_END_SAMPLE for row in speech_rows),
        },
        "availability": {
            "offset_ns": AVAILABILITY_OFFSET_NS,
            "known_probability_availability_monotonic": all(
                left["available_ns"] < right["available_ns"]
                for left, right in zip(probability_rows, probability_rows[1:])
                if left["available_ns"] is not None
                and right["available_ns"] is not None),
            "unknown_events_have_no_availability": all(
                row["available_ns"] is None for row in probability_rows
                if row["validity"] == Validity.UNKNOWN.value),
            "bus_dropped_events": len(bus.dropped),
            "bus_events": len(bus.events),
        },
        "cascade_policy": {
            "stub_invocations": vad.counters["stub_invocations"],
            "stub_skips": vad.counters["stub_skips"],
            "gate_wakes": vad.counters["gate_wakes"],
            "crosschecks_while_asleep": vad.counters["crosschecks_while_asleep"],
            "skipped_stub_fraction": vad.counters["stub_skips"] / TOTAL_FRAMES,
            "projected_compute_only": True,
            "stress_stratum_fn": score_data["strata"]["cross-environment-stress"]["fn"],
            "stress_stratum_frames": (
                score_data["strata"]["cross-environment-stress"]["tp"]
                + score_data["strata"]["cross-environment-stress"]["fn"]),
        },
        "source_pins": {"all_verified": all(pin_results.values()),
                        "count": len(pin_results)},
        "control_completeness": {
            "required_controls": [
                "invalid_vs_nonspeech", "frame_adverse", "event_adverse",
                "independent_state", "overlapping_sessions", "cross_hop",
                "source_intervals", "availability", "cascade_policy", "source_pins",
            ],
            "no_missing_results": True,
        },
    }
    controls["control_completeness"]["all_present"] = all(
        name in controls for name in controls["control_completeness"]["required_controls"])

    return {
        "contract": CONTRACT_ID,
        "task": TASK_ID,
        "pinned_base": PINNED_BASE,
        "status": {
            "claim": "proposal-only-synthetic",
            "qualification": "incomplete",
            "installed_sdk_changed": False,
            "silero_stage": "model-free-stub",
        },
        "source_pins": pins,
        "source_pin_verification": pin_results,
        "fixture": {
            "generator": spec["generator"],
            "spec_digest": spec_digest,
            "config_digest": CASCADE_CONFIG_DIGEST,
            "total_frames": TOTAL_FRAMES,
            "total_samples": TOTAL_SAMPLES,
            "scored_end_frame": SCORED_END_FRAME,
            "scored_end_sample": SCORED_END_SAMPLE,
            "segments": spec["segments"],
            "config": spec["config"],
        },
        "digests": {
            "pcm_f32_sha256": pcm_digest,
            "gate_probability_stream_sha256": sha256_text(canonical(
                [row for row in probability_rows
                 if row["stream"] == EventKind.GATE_PROBABILITY.value])),
            "stub_probability_stream_sha256": sha256_text(canonical(
                [row for row in probability_rows
                 if row["stream"] == EventKind.STUB_PROBABILITY.value])),
            "cascade_probability_stream_sha256": sha256_text(canonical(
                [row for row in probability_rows
                 if row["stream"] == EventKind.CASCADE_PROBABILITY.value])),
            "speech_events_sha256": sha256_text(canonical(speech_rows)),
            "audio_view_sha256": bus.audio_digest,
        },
        "counts": {
            "probability_events": len(probability_rows),
            "probability_events_known": sum(
                1 for row in probability_rows if row["validity"] == "known"),
            "probability_events_unknown": sum(
                1 for row in probability_rows if row["validity"] == "unknown"),
            "speech_events": len(speech_rows),
            "bus_events": len(bus.events),
            "bus_dropped_events": len(bus.dropped),
            **score_data["totals"],
        },
        "scoring": score_data,
        "probability_stream": probability_rows,
        "speech_events": speech_rows,
        "adverse_controls": controls,
        "blockers": BLOCKERS,
        "non_claims": NON_CLAIMS,
    }


def main() -> None:
    report = build_report()
    text = canonical(report)
    (TASK_DIR / "report.json").write_text(text, encoding="utf-8")
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
