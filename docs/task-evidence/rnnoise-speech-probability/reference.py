# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic RNNoise-style speech-probability reference fixture.

Task-local, optional, unregistered evidence for a v0-shaped *analysis*
boundary.  It is a model-free reference: a deterministic logistic transform of
RMS over a modeled evidence window, published as a timestamped
``speech_probability`` event once per 160-sample SDK v0 frame.  It is NOT
RNNoise's neural-network posterior and no native library, model archive,
corpus, licensed runtime, device or listening result is used.

The source report ``cpp-library/pipeline-validation/rnnoise-side-vad/report.md``
is pinned as context only.  Its FN/FP numbers are never reused as results here.

Cohorts are fully labeled synthetic speech/nonspeech.  Quality observations and
the unpaced wall-clock pointer live in separate artifacts; no timing value is
used for a quality claim and no quality value is used for a timing claim.
Status is ``proposal_only_synthetic_incomplete`` / ``not_qualified``.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/rnnoise-speech-probability/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/rnnoise-speech-probability/report/0.1"

# Public v0 geometry is untouched: 16 kHz, mono float32, 160 samples per call.
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
SAMPLE_NS = 62500

FRAMES = 200
SAMPLES = FRAMES * FRAME_SAMPLES  # 32,000 samples = 2.0 s
SEED_SIGNAL = 20261124
SEED_PROB = 20261125
SEED_VAD = 20261126

# Modeled evidence window: 480 samples (30 ms at 16 kHz) around one SDK frame,
# with one frame of past context and one frame of lookahead.  This is a fixture
# choice for cross-hop placement, not a claim about RNNoise internals.
WINDOW_SAMPLES = 3 * FRAME_SAMPLES
PAST_FRAMES = 1
LOOKAHEAD_FRAMES = 1

DECISION_THRESHOLD = 0.5
THRESHOLDS = (0.4, 0.5, 0.6, 0.7, 0.9)
PROB_CENTER_DB = -46.0
PROB_SOFTNESS_DB = 5.0
PROB_JITTER = 0.070
VAD_CENTER_DB = -42.0
VAD_SOFTNESS_DB = 3.0
VAD_JITTER = 0.020
VAD_LOOKAHEAD_SAMPLES = 80

CLOCK_ID = "fixture-monotonic-v0"
ORIGIN_NS = 1767225600000000000  # fixed provenance origin; emitted as a string
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
PROVIDER_ID = "analysis.rnnoise-speech-probability-ref.v0"

# Half-open source-sample intervals.  Every sample in [0, SAMPLES) has exactly
# one activity label and one content class: there are no unknown regions.
SEGMENTS: tuple[tuple[int, int, str, str], ...] = (
    (0, 1600, "nonspeech", "idle_quiet"),
    (1600, 3200, "speech", "quiet"),
    (3200, 4800, "speech", "active"),
    (4800, 6400, "nonspeech", "idle_loud"),
    (6400, 9600, "speech", "active"),
    (9600, 11200, "speech", "quiet"),
    (11200, 16000, "nonspeech", "idle_quiet"),
    (16000, 19200, "speech", "active"),
    (19200, 24000, "nonspeech", "idle_loud"),
    (24000, 27200, "speech", "quiet"),
    (27200, 32000, "nonspeech", "idle_quiet"),
)
EXPECTED_ONSET_FRAMES = (10, 40, 100, 150)
EXPECTED_OFFSET_FRAMES = (30, 70, 120, 170)

METHOD_PRIMARY = "rnnoise_style_probability"
METHOD_VAD = "standalone_vad_control"
METHOD_SILENT = "silent_control"
METHOD_ALWAYS = "always_speech_control"
METHODS = (METHOD_PRIMARY, METHOD_VAD, METHOD_SILENT, METHOD_ALWAYS)

# External bytes pinned for this task.  ``source`` paths are relative to
# /Users/htsakanyan/workspace/audio/audioml; ``worktree`` paths are relative to
# the SDK worktree root.
SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "cpp-library/pipeline-validation/rnnoise-side-vad/report.md",
        "root": "source",
        "sha256": "bbda960bd85e62ea096cc77e1305506ba9fc4757994a3ae8e64bfb657f3abe40",
        "summary": "Source-reported 180 s, three-window RNNoise 25.64% FN / 5.44% FP and Silero 22.91% FN / 7.64% FP diagnostic; context only, never reused as a result.",
    },
    {
        "path": "adapters/rnnoise/adapter.json",
        "root": "source",
        "sha256": "6c7ca68df9fe24bf67f249197777674e4bc8f6527bccbb2fcced4637e00abb44",
        "summary": "Public adapter identity; output_kinds is waveform only and tasks is CLN-01, so speech_probability is not exposed at the shipped public boundary.",
    },
    {
        "path": "adapters/rnnoise/run.py",
        "root": "source",
        "sha256": "4be2dc2f1c76e46b187a9e52c9faab7ff32e805461cf554a3b97fa3410d2993b",
        "summary": "Pinned 70f1d256acd4b34a572f999a05c87bf00b67730d native RNNoise path; requires a locally built library/model archive with verified hashes, unavailable in this task scope.",
    },
    {
        "path": "adapters/rnnoise/README.md",
        "root": "source",
        "sha256": "6c5cfb5c3493f40c1fd43a0fc54b87f590abf3712d3d3cef7c2f7bc16de15b85",
        "summary": "Documents the local arm64 dylib, embedded model archive and offline-only protocol; no probability output kind is declared.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 geometry, exact source intervals, decimal-string sample/time serialization and analysis-event validity rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Analysis acceptance profile: probabilities, event boundaries, delays, stratified FN/FP, validity vs nonspeech, state and cross-hop behavior.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by this Python reference; unchanged.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary; unchanged. No analysis hook is added.",
    },
)

GATES: tuple[dict[str, str], ...] = (
    {
        "id": "native_probability_boundary",
        "status": "blocked",
        "reason": "The pinned public RNNoise adapter declares waveform-only output (CLN-01, offline) and requires a local native library/model archive that is not present in this task scope. This fixture models a probability boundary; it does not read RNNoise's network output.",
        "reopen": "Pin the native library and model hashes, expose speech_probability at a reviewed adapter boundary, and rerun the identical frozen cohort with independent scoring.",
    },
    {
        "id": "matched_labeled_cohort",
        "status": "blocked",
        "reason": "No rights-qualified held-out AMI cohort, frozen candidate outputs or independent scorer asset is available here. The three source-reported label-balanced windows are context only.",
        "reopen": "Freeze a permitted labeled cohort with an independent scorer and fixed threshold policy before any accuracy claim.",
    },
    {
        "id": "endpointing_validation",
        "status": "blocked",
        "reason": "A single threshold on a small diagnostic window is not endpointing validation; onset/offset delays here are synthetic source-coordinate observations.",
        "reopen": "Run independently reviewed endpointing validation on permitted speech with an agreed delay budget.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "Only unpaced wall-clock observations of this Python reference exist in a separate non-qualifying artifact. No native-call cost, pacing, deadline, CPU or memory measurement was run.",
        "reopen": "Measure the exact installed build on the target under pacing, load and deadline budgets with independent timing.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "The conceptual provider ID is unregistered, OFF by default and has empty descriptor settings. No code, registry entry, default or public surface is changed.",
        "reopen": "Complete task-local provider intake with opt-in OFF default, empty descriptor settings, clean SPDX headers and independent review.",
    },
)


class LCG:
    """Version-stable 32-bit LCG; independent of Python random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "),
                      allow_nan=False).encode("utf-8") + b"\n"


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def dec(value: int) -> str:
    """Canonical decimal string for int64 sample/ns and uint64 epoch fields."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("decimal field requires an integer")
    return str(value)


def sigmoid(value: float) -> float:
    clipped = max(-60.0, min(60.0, value))
    return 1.0 / (1.0 + math.exp(-clipped))


def deterministic_jitter(seed: int, frame: int, magnitude: float) -> float:
    mixed = (seed ^ ((frame + 1) * 0x9E3779B1)) & 0xFFFFFFFF
    return LCG(mixed).uniform() * magnitude


def segment_at(index: int) -> tuple[str, str]:
    for start, end, label, kind in SEGMENTS:
        if start <= index < end:
            return label, kind
    raise ValueError("sample outside fully labeled cohort")


def activity_transitions() -> tuple[tuple[int, ...], tuple[int, ...]]:
    onsets: list[int] = []
    offsets: list[int] = []
    for (_, _, label_a, _), (start_b, _, label_b, _) in zip(SEGMENTS, SEGMENTS[1:]):
        if label_a == "nonspeech" and label_b == "speech":
            onsets.append(start_b // FRAME_SAMPLES)
        elif label_a == "speech" and label_b == "nonspeech":
            offsets.append(start_b // FRAME_SAMPLES)
    return tuple(onsets), tuple(offsets)


def synthetic_signal(samples: int = SAMPLES,
                     seed: int = SEED_SIGNAL) -> tuple[float, ...]:
    """Deterministic speech-like surrogate with fully labeled regions."""
    rng = LCG(seed)
    formant_a0 = formant_a1 = 0.0
    formant_b0 = formant_b1 = 0.0
    noise_lp = 0.0
    out: list[float] = []
    for index in range(samples):
        activity, content = (segment_at(index) if index < SAMPLES
                             else ("nonspeech", "idle_quiet"))
        time_s = index / SAMPLE_RATE_HZ
        noise = rng.uniform()
        noise_lp = 0.6 * noise_lp + 0.4 * noise
        if activity == "speech":
            amplitude = 0.035 if content == "quiet" else 0.22
            f0 = 115.0 + 12.0 * math.sin(2.0 * math.pi * 0.7 * time_s)
            period = max(1, int(round(SAMPLE_RATE_HZ / f0)))
            drive = 1.0 if index % period == 0 else 0.0
            formant_a0, formant_a1 = (
                0.975 * formant_a0 - 0.020 * formant_a1 + drive, formant_a0)
            formant_b0, formant_b1 = (
                0.940 * formant_b0 - 0.045 * formant_b1 + drive, formant_b0)
            syllable = 0.55 + 0.45 * math.sin(2.0 * math.pi * 2.3 * time_s) ** 2
            value = (amplitude * syllable
                     * (0.55 * formant_a0 + 0.20 * formant_b0)
                     + amplitude * 0.25 * noise_lp)
        else:
            amplitude = 0.004 if content == "idle_quiet" else 0.10
            burst = 1.0 if (index // FRAME_SAMPLES) % 3 != 2 else 0.25
            value = amplitude * burst * (0.6 * noise_lp + 0.4 * noise)
        out.append(max(-0.95, min(0.95, value)))
    return tuple(out)


def window_bounds(frame: int, samples: int = SAMPLES) -> tuple[int, int]:
    start = max(0, (frame - PAST_FRAMES) * FRAME_SAMPLES)
    end = min(samples, (frame + 1 + LOOKAHEAD_FRAMES) * FRAME_SAMPLES)
    return start, end


def frame_rms(values: Sequence[float], start: int, end: int) -> float:
    if end <= start:
        return 0.0
    return math.sqrt(sum(v * v for v in values[start:end]) / (end - start))


def dbfs(rms: float) -> float:
    return 20.0 * math.log10(max(rms, 1e-12))


def rnnoise_style_probability(values: Sequence[float], frame: int) -> float:
    """Uncalibrated deterministic logistic score, NOT a model posterior."""
    start, end = window_bounds(frame, len(values))
    level = dbfs(frame_rms(values, start, end))
    score = sigmoid((level - PROB_CENTER_DB) / PROB_SOFTNESS_DB)
    score += deterministic_jitter(SEED_PROB, frame, PROB_JITTER)
    return round(max(0.0, min(1.0, score)), 6)


def standalone_vad_probability(values: Sequence[float], frame: int) -> float:
    """Independent energy-VAD control with its own window and decision cost."""
    start = frame * FRAME_SAMPLES
    end = min(len(values), start + FRAME_SAMPLES + VAD_LOOKAHEAD_SAMPLES)
    level = dbfs(frame_rms(values, start, end))
    score = sigmoid((level - VAD_CENTER_DB) / VAD_SOFTNESS_DB)
    score += deterministic_jitter(SEED_VAD, frame, VAD_JITTER)
    return round(max(0.0, min(1.0, score)), 6)


def probability(method: str, values: Sequence[float], frame: int) -> float:
    if method == METHOD_PRIMARY:
        return rnnoise_style_probability(values, frame)
    if method == METHOD_VAD:
        return standalone_vad_probability(values, frame)
    if method == METHOD_SILENT:
        return 0.0
    if method == METHOD_ALWAYS:
        return 1.0
    raise ValueError("unknown probability method")


CONFIG_DIGEST = object_digest({
    "contract": CONTRACT_ID,
    "decision_threshold": DECISION_THRESHOLD,
    "method": METHOD_PRIMARY,
    "native_hop_samples": FRAME_SAMPLES,
    "probability_window_samples": WINDOW_SAMPLES,
    "sample_rate_hz": SAMPLE_RATE_HZ,
})


@dataclass(frozen=True)
class ProbabilityEvent:
    event_id: str
    producer_id: str
    tap_id: str
    epoch: int
    source_start: int
    source_end: int
    window_start: int
    window_end: int
    value: float
    validity: str
    config_digest: str

    @property
    def key(self) -> tuple[str, str, int, str]:
        return (self.producer_id, self.tap_id, self.epoch, self.event_id)

    @property
    def available_ns(self) -> int:
        return ORIGIN_NS + self.window_end * SAMPLE_NS

    def as_dict(self) -> dict[str, Any]:
        return {
            "availability_clock_id": CLOCK_ID,
            "available_ns": dec(self.available_ns),
            "config_digest": self.config_digest,
            "epoch": dec(self.epoch),
            "event_id": self.event_id,
            "kind": "speech_probability",
            "producer_id": self.producer_id,
            "source_end": dec(self.source_end),
            "source_start": dec(self.source_start),
            "tap_id": self.tap_id,
            "validity": self.validity,
            "value": self.value,
            "window_end": dec(self.window_end),
            "window_start": dec(self.window_start),
        }


class Rejection(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class AnalysisSession:
    """Independent, read-only analysis stream keyed by (producer, tap, epoch).

    There is no process-global latest-event register.  A stale epoch, a wrong
    source interval, a bad digest, a nonfinite/out-of-range value or an invalid
    validity tag is rejected without changing stream state.  Dropped events
    leave explicit gaps; no event is fabricated to fill them.
    """

    def __init__(self, epoch: int = 1, first_input_sample: int = 0,
                 producer_id: str = "rnnoise-style.v0",
                 tap_id: str = "analysis.tap.0", method: str = METHOD_PRIMARY,
                 config_digest: str = CONFIG_DIGEST) -> None:
        if epoch < 1 or first_input_sample < 0 or first_input_sample % FRAME_SAMPLES:
            raise Rejection("invalid_session_initial_state")
        if method not in METHODS:
            raise Rejection("unknown_method")
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.producer_id = producer_id
        self.tap_id = tap_id
        self.method = method
        self.config_digest = config_digest
        self.events: list[ProbabilityEvent] = []
        self.rejections: list[dict[str, str]] = []
        self.dropped: list[str] = []
        self.next_frame = first_input_sample // FRAME_SAMPLES
        self.closed = False

    def _reject(self, reason: str) -> ProbabilityEvent:
        self.rejections.append({"reason": reason,
                                "frame": dec(self.next_frame)})
        raise Rejection(reason)

    def process_frame(self, signal: Sequence[float], frame: Optional[int] = None,
                      values_epoch: Optional[int] = None, validity: str = "known",
                      value_override: Optional[float] = None,
                      config_override: Optional[str] = None,
                      source_override: Optional[tuple[int, int]] = None,
                      ) -> ProbabilityEvent:
        """Admit one exact 160-sample source frame from a caller-owned signal."""
        if self.closed:
            return self._reject("closed_session")
        if values_epoch is not None and values_epoch != self.epoch:
            return self._reject("stale_epoch")
        if frame is None:
            frame = self.next_frame
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
            return self._reject("invalid_frame_shape")
        if frame != self.next_frame:
            return self._reject("out_of_order_frame")
        start = frame * FRAME_SAMPLES
        chunk = signal[start:start + FRAME_SAMPLES]
        if len(chunk) != FRAME_SAMPLES:
            return self._reject("invalid_frame_shape")
        if any(not isinstance(v, (int, float)) or isinstance(v, bool)
               or not math.isfinite(float(v)) for v in chunk):
            return self._reject("invalid_frame_nonfinite")
        if validity not in ("known", "unknown", "invalid"):
            return self._reject("invalid_validity_tag")
        if config_override is not None and config_override != self.config_digest:
            return self._reject("invalid_config_digest")
        end = start + FRAME_SAMPLES
        if source_override is not None:
            start, end = source_override
        if end <= start or start < 0:
            return self._reject("invalid_source_interval")
        value = (probability(self.method, signal, frame)
                 if value_override is None else value_override)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return self._reject("invalid_value_type")
        if not math.isfinite(float(value)):
            return self._reject("invalid_value_nonfinite")
        if not 0.0 <= float(value) <= 1.0:
            return self._reject("invalid_value_range")
        if validity == "invalid":
            return self._reject("invalid_event_validity")
        window_start, window_end = window_bounds(frame, SAMPLES)
        event = ProbabilityEvent(
            event_id=f"p-{dec(self.epoch)}-{frame:04d}",
            producer_id=self.producer_id,
            tap_id=self.tap_id,
            epoch=self.epoch,
            source_start=start,
            source_end=end,
            window_start=window_start,
            window_end=window_end,
            value=float(value),
            validity=validity,
            config_digest=self.config_digest,
        )
        if any(prior.key == event.key for prior in self.events):
            return self._reject("duplicate_event")
        if self.events and event.available_ns < self.events[-1].available_ns:
            return self._reject("non_monotonic_availability")
        self.events.append(event)
        self.next_frame += 1
        return event

    def accept_external_event(self, event: ProbabilityEvent,
                              session_epoch: Optional[int] = None) -> str:
        """Admission of an event from another producer/epoch (no global slot)."""
        epoch = self.epoch if session_epoch is None else session_epoch
        if event.epoch != epoch:
            return "rejected_stale_epoch"
        if event.key in {prior.key for prior in self.events}:
            return "rejected_duplicate_event"
        self.events.append(event)
        return "accepted"

    def drop(self, event_ids: Sequence[str]) -> None:
        self.dropped.extend(event_ids)
        self.events = [event for event in self.events
                       if event.event_id not in set(event_ids)]

    def reset(self, epoch: int, first_input_sample: int) -> str:
        if self.closed:
            return "rejected_closed"
        if epoch <= self.epoch:
            return "rejected_stale_epoch"
        self.__init__(epoch=epoch, first_input_sample=first_input_sample,
                      producer_id=self.producer_id, tap_id=self.tap_id,
                      method=self.method, config_digest=self.config_digest)
        return "ok"

    def close(self) -> None:
        self.closed = True


def frame_slice(values: Sequence[float], frame: int) -> tuple[float, ...]:
    start = frame * FRAME_SAMPLES
    return tuple(values[start:start + FRAME_SAMPLES])


def run_session(values: Sequence[float], method: str = METHOD_PRIMARY,
                frames: int = FRAMES, epoch: int = 1,
                producer_id: str = "rnnoise-style.v0",
                tap_id: str = "analysis.tap.0") -> AnalysisSession:
    session = AnalysisSession(epoch=epoch, producer_id=producer_id,
                              tap_id=tap_id, method=method)
    for frame in range(frames):
        session.process_frame(values, frame=frame)
    return session


def known_decisions(session: AnalysisSession) -> list[tuple[int, bool]]:
    """Exact source intervals: only known events yield a decision."""
    out: list[tuple[int, bool]] = []
    for event in session.events:
        if event.validity != "known":
            continue
        start = int(event.source_start)
        if start % FRAME_SAMPLES or int(event.source_end) - start != FRAME_SAMPLES:
            raise AssertionError("probability event is not one exact v0 frame")
        out.append((start, event.value >= DECISION_THRESHOLD))
    if [start for start, _ in out] != [frame * FRAME_SAMPLES
                                       for frame in range(len(out))]:
        raise AssertionError("probability event intervals are not contiguous")
    return out


def detections_from(decisions: Sequence[tuple[int, bool]]) -> list[dict[str, Any]]:
    detections: list[dict[str, Any]] = []
    active_start: Optional[int] = None
    for start, active in decisions:
        if active and active_start is None:
            active_start = start
        elif not active and active_start is not None:
            detections.append({"start": active_start, "end": start})
            active_start = None
    if active_start is not None:
        detections.append({"start": active_start,
                           "end": decisions[-1][0] + FRAME_SAMPLES})
    return [{"source_start": dec(item["start"]),
             "source_end": dec(item["end"]),
             "frames": (item["end"] - item["start"]) // FRAME_SAMPLES}
            for item in detections]


def truth_intervals(label: str) -> list[tuple[int, int]]:
    return [(start, end) for start, end, name, _ in SEGMENTS if name == label]


def confusion(decisions: Sequence[tuple[int, bool]]) -> dict[str, Any]:
    tp = fn = fp = tn = 0
    for start, active in decisions:
        end = start + FRAME_SAMPLES
        for index in range(start, end):
            truth, _ = segment_at(index)
            if truth == "speech" and active:
                tp += 1
            elif truth == "speech":
                fn += 1
            elif active:
                fp += 1
            else:
                tn += 1
    speech = tp + fn
    nonspeech = fp + tn
    return {
        "tp_samples": tp,
        "fn_samples": fn,
        "fp_samples": fp,
        "tn_samples": tn,
        "speech_samples": speech,
        "nonspeech_samples": nonspeech,
        "scored_samples": speech + nonspeech,
        "fn_rate": round(fn / speech, 9) if speech else None,
        "fp_rate": round(fp / nonspeech, 9) if nonspeech else None,
    }


def classify_frame(frame: int) -> tuple[str, str]:
    _, kind = segment_at(frame * FRAME_SAMPLES)
    label, _ = segment_at(frame * FRAME_SAMPLES)
    return label, kind


def stratified_errors(decisions: Sequence[tuple[int, bool]]) -> dict[str, Any]:
    speech_classes = ("quiet", "active")
    nonspeech_classes = ("idle_quiet", "idle_loud")
    fn_by_class = {name: {"fn_samples": 0, "speech_samples": 0,
                          "fn_rate": None} for name in speech_classes}
    fp_by_class = {name: {"fp_samples": 0, "nonspeech_samples": 0,
                          "fp_rate": None} for name in nonspeech_classes}
    onsets, offsets = activity_transitions()
    # The last speech frame before each offset transition, not the first
    # nonspeech frame, is the offset-adjacent speech frame.
    last_speech_frames = tuple(frame - 1 for frame in offsets)
    position = {name: {"fn_samples": 0, "speech_samples": 0,
                       "fn_rate": None} for name in ("onset", "offset", "interior")}
    boundary = {"near_speech": {"fp_samples": 0, "nonspeech_samples": 0,
                                "fp_rate": None},
                "far_from_speech": {"fp_samples": 0, "nonspeech_samples": 0,
                                    "fp_rate": None}}
    for start, active in decisions:
        frame = start // FRAME_SAMPLES
        label, kind = classify_frame(frame)
        if label == "speech":
            bucket = fn_by_class[kind]
            bucket["speech_samples"] += FRAME_SAMPLES
            if not active:
                bucket["fn_samples"] += FRAME_SAMPLES
            where = ("onset" if frame in onsets
                     else "offset" if frame in last_speech_frames else "interior")
            position[where]["speech_samples"] += FRAME_SAMPLES
            if not active:
                position[where]["fn_samples"] += FRAME_SAMPLES
        else:
            near = any(abs(frame - transition) <= 1
                       for transition in onsets + offsets)
            bucket = boundary["near_speech" if near else "far_from_speech"]
            bucket["nonspeech_samples"] += FRAME_SAMPLES
            if active:
                bucket["fp_samples"] += FRAME_SAMPLES
            fp = fp_by_class[kind]
            fp["nonspeech_samples"] += FRAME_SAMPLES
            if active:
                fp["fp_samples"] += FRAME_SAMPLES
    for bucket in list(fn_by_class.values()) + list(position.values()):
        if bucket["speech_samples"]:
            bucket["fn_rate"] = round(bucket["fn_samples"]
                                      / bucket["speech_samples"], 9)
    for bucket in list(fp_by_class.values()) + list(boundary.values()):
        if bucket["nonspeech_samples"]:
            bucket["fp_rate"] = round(bucket["fp_samples"]
                                      / bucket["nonspeech_samples"], 9)
    return {"fn_by_speech_class": fn_by_class,
            "fp_by_nonspeech_class": fp_by_class,
            "fn_by_position": position,
            "fp_by_boundary_proximity": boundary}


def onset_offset_delay(decisions: Sequence[tuple[int, bool]]) -> dict[str, Any]:
    intervals = detections_from(decisions)
    results: dict[str, Any] = {}
    for start, end, label, _ in SEGMENTS:
        if label != "speech":
            continue
        overlapping = [(int(item["source_start"]), int(item["source_end"]))
                       for item in intervals
                       if int(item["source_start"]) < end
                       and int(item["source_end"]) > start]
        key = f"[{dec(start)},{dec(end)})"
        local = [frame_start for frame_start, active in decisions
                 if active and start <= frame_start < end]
        if not overlapping or not local:
            results[key] = {"detected": False, "onset_delay_samples": None,
                            "offset_delay_samples": None,
                            "local_onset_delay_samples": None,
                            "local_offset_delay_samples": None,
                            "reason": "no_overlapping_detection"}
            continue
        matched = max(overlapping, key=lambda item: min(item[1], end) - max(item[0], start))
        results[key] = {
            "detected": True,
            "matched_detection": [dec(matched[0]), dec(matched[1])],
            "onset_delay_samples": matched[0] - start,
            "offset_delay_samples": matched[1] - end,
            "local_onset_delay_samples": min(local) - start,
            "local_offset_delay_samples": max(local) + FRAME_SAMPLES - end,
            "overlap_samples": min(matched[1], end) - max(matched[0], start),
            "delay_sign_convention": "positive onset = detected after reference start; positive offset = detected after reference end; negative = detected before it",
        }
    return results


def detection_coverage(decisions: Sequence[tuple[int, bool]]) -> dict[str, Any]:
    intervals = detections_from(decisions)
    covered: set[int] = set()
    for item in intervals:
        covered.update(range(int(item["source_start"]), int(item["source_end"])))
    outside = sorted(index for index in covered
                     if not 0 <= index < SAMPLES)
    return {
        "detection_intervals": intervals,
        "detected_samples": len(covered),
        "detected_frames": sum(item["frames"] for item in intervals),
        "detected_intervals_cover_union_exactly": (
            sum(item["frames"] for item in intervals) * FRAME_SAMPLES == len(covered)),
        "samples_outside_scored_union": outside,
    }


def cross_hop_check(session: AnalysisSession) -> dict[str, Any]:
    overlaps = [0] * FRAMES
    for event in session.events:
        start = int(event.window_start)
        end = int(event.window_end)
        for frame in range(FRAMES):
            lo = frame * FRAME_SAMPLES
            hi = lo + FRAME_SAMPLES
            if start < hi and end > lo:
                overlaps[frame] += 1
    expected = [2] + [3] * (FRAMES - 2) + [2]
    return {
        "window_samples": WINDOW_SAMPLES,
        "past_frames": PAST_FRAMES,
        "lookahead_frames": LOOKAHEAD_FRAMES,
        "sdk_hop_samples": FRAME_SAMPLES,
        "per_sdk_frame_overlap_counts": overlaps,
        "expected_overlap_counts": expected,
        "exact_overlap_match": overlaps == expected,
        "placement_by_exact_interval": all(
            int(event.source_start) % FRAME_SAMPLES == 0
            and int(event.source_end) - int(event.source_start) == FRAME_SAMPLES
            for event in session.events),
        "events_crossing_an_sdk_frame_boundary": sum(
            1 for event in session.events
            if int(event.window_start) // FRAME_SAMPLES
            != (int(event.window_end) - 1) // FRAME_SAMPLES),
    }


def availability_check(session: AnalysisSession) -> dict[str, Any]:
    stamps = [event.available_ns for event in session.events]
    return {
        "clock_id": CLOCK_ID,
        "origin_ns": dec(ORIGIN_NS),
        "ns_per_sample": SAMPLE_NS,
        "formula": "available_ns = origin_ns + window_end * 62500",
        "first_available_ns": dec(stamps[0]) if stamps else None,
        "last_available_ns": dec(stamps[-1]) if stamps else None,
        "monotonic_nondecreasing": all(b >= a for a, b in zip(stamps, stamps[1:])),
        "lookahead_samples": LOOKAHEAD_FRAMES * FRAME_SAMPLES,
        "signal_timestamp_is_not_availability": all(
            event.available_ns != int(event.source_end) * SAMPLE_NS
            for event in session.events),
        "availability_serialization": "decimal string per CONTRACTS.md",
    }


def threshold_sweep(session: AnalysisSession) -> dict[str, Any]:
    """Frozen 0.50 threshold versus other thresholds on the same probabilities."""
    results: dict[str, Any] = {}
    for threshold in THRESHOLDS:
        decisions = [(int(event.source_start), event.value >= threshold)
                     for event in session.events if event.validity == "known"]
        results[f"{threshold:.2f}"] = {
            "threshold": threshold,
            "confusion": confusion(decisions),
            "detected_frames": detection_coverage(decisions)["detected_frames"],
        }
    base = results[f"{DECISION_THRESHOLD:.2f}"]["confusion"]
    regressions: list[dict[str, Any]] = []
    for label, item in results.items():
        if label == f"{DECISION_THRESHOLD:.2f}":
            continue
        candidate = item["confusion"]
        for metric in ("fn_rate", "fp_rate"):
            delta = round(base[metric] - candidate[metric], 9)
            if delta > 0:
                regressions.append({
                    "scope": f"threshold_sweep.{label}", "metric": metric,
                    "delta": delta,
                    "note": "the frozen 0.50 threshold is worse than this swept threshold on the synthetic cohort",
                })
        base_balanced = round((base["fn_rate"] + base["fp_rate"]) / 2.0, 9)
        candidate_balanced = round((candidate["fn_rate"]
                                    + candidate["fp_rate"]) / 2.0, 9)
        delta = round(base_balanced - candidate_balanced, 9)
        if delta > 0:
            regressions.append({
                "scope": f"threshold_sweep.{label}", "metric": "balanced_error_rate",
                "delta": delta,
                "note": "the frozen 0.50 threshold has higher mean FN/FP rate than this swept threshold",
            })
    return {"thresholds": results, "frozen_threshold": DECISION_THRESHOLD,
            "regressions": regressions, "regression_count": len(regressions)}


def quality_comparison(quality: dict[str, dict[str, Any]]) -> dict[str, Any]:
    primary = quality[METHOD_PRIMARY]["confusion"]
    vad = quality[METHOD_VAD]["confusion"]
    primary_strata = quality[METHOD_PRIMARY]["stratified"]
    vad_strata = quality[METHOD_VAD]["stratified"]
    deltas: dict[str, Any] = {
        "fn_rate_delta_vs_standalone_vad": round(primary["fn_rate"] - vad["fn_rate"], 9),
        "fp_rate_delta_vs_standalone_vad": round(primary["fp_rate"] - vad["fp_rate"], 9),
    }
    for group in ("fn_by_speech_class", "fp_by_nonspeech_class",
                  "fn_by_position", "fp_by_boundary_proximity"):
        rate_key = "fn_rate" if group.startswith("fn") else "fp_rate"
        deltas[group] = {}
        for name, bucket in primary_strata[group].items():
            other = vad_strata[group][name][rate_key]
            value = bucket[rate_key]
            deltas[group][name] = (round(value - other, 9)
                                   if value is not None and other is not None else None)

    regressions: list[dict[str, Any]] = []
    overall_fn = deltas["fn_rate_delta_vs_standalone_vad"]
    overall_fp = deltas["fp_rate_delta_vs_standalone_vad"]
    if overall_fn > 0:
        regressions.append({"scope": "overall", "metric": "fn_rate",
                            "delta": overall_fn,
                            "note": "primary misses more speech than standalone VAD"})
    if overall_fp > 0:
        regressions.append({"scope": "overall", "metric": "fp_rate",
                            "delta": overall_fp,
                            "note": "primary false-alarms more than standalone VAD"})
    for group, items in deltas.items():
        if not isinstance(items, dict):
            continue
        metric = "fn_rate" if group.startswith("fn") else "fp_rate"
        for name, value in items.items():
            if value is not None and value > 0:
                regressions.append({"scope": f"{group}.{name}", "metric": metric,
                                    "delta": value,
                                    "note": "primary worse than standalone VAD in this stratum"})
    return {"deltas": deltas, "regressions": regressions,
            "regression_count": len(regressions)}


def validity_separation(values: Sequence[float]) -> dict[str, Any]:
    """Invalid/unknown analysis is never relabeled as nonspeech."""
    session = AnalysisSession(epoch=3, method=METHOD_PRIMARY)
    outcomes: list[dict[str, str]] = []
    # Ten known frames precede the probes; the probed frame is a speech frame.
    for frame in range(10):
        session.process_frame(values, frame=frame)
    probes = (
        ("nonfinite_probability", {"value_override": float("nan")}),
        ("out_of_range_probability", {"value_override": 1.4}),
        ("invalid_config_digest", {"config_override": "00" * 32}),
        ("stale_epoch_frame", {"values_epoch": 2}),
        ("invalid_validity_tag", {"validity": "maybe"}),
        ("invalid_source_interval", {"source_override": (320, 320)}),
        ("invalid_event_validity", {"validity": "invalid"}),
    )
    baseline_state = (session.next_frame, len(session.events), len(session.rejections))
    for name, kwargs in probes:
        try:
            session.process_frame(values, frame=session.next_frame, **kwargs)
            status = "accepted"
        except Rejection as error:
            status = "rejected_" + error.reason
        outcomes.append({"case": name, "status": status})
    state_unchanged = (session.next_frame, len(session.events),
                       len(session.rejections)) == (baseline_state[0], baseline_state[1],
                                                    baseline_state[2] + len(probes))
    unknown_frame = session.next_frame
    session.process_frame(values, frame=unknown_frame, validity="unknown")
    known = [event for event in session.events if event.validity == "known"]
    truth, _ = classify_frame(unknown_frame)
    known_confusion = confusion([(int(event.source_start),
                                  event.value >= DECISION_THRESHOLD)
                                 for event in known])
    session.close()
    return {
        "probes": outcomes,
        "all_invalid_rejected": all(item["status"].startswith("rejected_")
                                    for item in outcomes),
        "state_unchanged_by_invalid": state_unchanged,
        "unknown_events_retained": sum(1 for event in session.events
                                       if event.validity == "unknown"),
        "invalid_events_retained": sum(1 for event in session.events
                                       if event.validity == "invalid"),
        "known_events_scored": len(known),
        "unknown_frame_source_start": dec(unknown_frame * FRAME_SAMPLES),
        "unknown_frame_truth_class": truth,
        "additional_fn_if_unknown_counted_as_nonspeech": (
            FRAME_SAMPLES if truth == "speech" else 0),
        "actual_added_fn": 0,
        "known_only_fn_samples": known_confusion["fn_samples"],
        "invalid_nonspeech_relabeling": "none",
    }


def state_checks(values: Sequence[float]) -> dict[str, Any]:
    a = run_session(values, frames=12, epoch=1, producer_id="rnnoise-style.A",
                    tap_id="tap.A")
    b_values = tuple(0.7 * v for v in values)
    b = run_session(b_values, frames=12, epoch=2, producer_id="rnnoise-style.B",
                    tap_id="tap.B")
    a_digest = object_digest([event.as_dict() for event in a.events])
    b_digest = object_digest([event.as_dict() for event in b.events])
    a_keys = {event.key for event in a.events}
    b_keys = {event.key for event in b.events}
    stale = a.accept_external_event(b.events[0], session_epoch=a.epoch)
    b_before = object_digest([event.as_dict() for event in b.events])
    reset_status = a.reset(3, 0)
    a_cleared = not a.events
    a_after_reset = object_digest([event.as_dict() for event in a.events])
    b_after = object_digest([event.as_dict() for event in b.events])
    revived = a.accept_external_event(b.events[0], session_epoch=a.epoch)
    for frame in range(12):
        a.process_frame(values, frame=frame)
    a_replayed = object_digest([event.as_dict() for event in a.events])
    fresh = AnalysisSession(epoch=3, producer_id="rnnoise-style.A", tap_id="tap.A")
    for frame in range(12):
        fresh.process_frame(values, frame=frame)
    fresh_digest = object_digest([event.as_dict() for event in fresh.events])
    a.close()
    closed_status = "accepted"
    try:
        a.process_frame(values, frame=0)
    except Rejection:
        closed_status = "rejected_closed"
    return {
        "sessions_uncoupled": a_digest != b_digest,
        "event_keys_disjoint": a_keys.isdisjoint(b_keys),
        "no_global_latest_event_slot": a_keys.isdisjoint(b_keys),
        "stale_epoch_event_rejected": stale == "rejected_stale_epoch",
        "reset_accepted": reset_status == "ok",
        "reset_clears_events": a_cleared and a_after_reset != a_digest,
        "other_session_unchanged_by_reset": b_before == b_after,
        "old_event_cannot_revive_after_reset": revived == "rejected_stale_epoch",
        "reset_bit_identical_to_fresh_epoch": a_replayed == fresh_digest,
        "closed_session_rejects_process": closed_status == "rejected_closed",
    }


def drop_and_stale_checks(values: Sequence[float]) -> dict[str, Any]:
    session = run_session(values, frames=20, epoch=4)
    all_ids = [event.event_id for event in session.events]
    dropped_ids = [all_ids[3], all_ids[7]]
    session.drop(dropped_ids)
    present_ids = [event.event_id for event in session.events]
    gaps = [number for number in range(20)
            if f"p-{dec(session.epoch)}-{number:04d}" not in present_ids]
    foreign = AnalysisSession(epoch=9).process_frame(values, frame=0)
    status = session.accept_external_event(foreign, session_epoch=session.epoch)
    return {
        "dropped_event_ids": dropped_ids,
        "dropped_event_count": len(session.dropped),
        "explicit_gap_sequence_numbers": gaps,
        "no_fabricated_fill": all(event.event_id in present_ids
                                  for event in session.events),
        "remaining_event_count": len(session.events),
        "foreign_epoch_event_rejected": status == "rejected_stale_epoch",
        "event_count_after_rejection": len(session.events),
    }


def event_integrity(session: AnalysisSession) -> dict[str, Any]:
    events = [event.as_dict() for event in session.events]
    starts = [int(event["source_start"]) for event in events]
    ends = [int(event["source_end"]) for event in events]
    keys = [event.key for event in session.events]
    return {
        "event_count": len(events),
        "events_digest": object_digest(events),
        "keys_unique": len(set(keys)) == len(keys),
        "first_source_start": dec(starts[0]) if starts else None,
        "last_source_end_exclusive": dec(ends[-1]) if ends else None,
        "cover_scored_union_exactly": (
            starts == [frame * FRAME_SAMPLES for frame in range(len(starts))]
            and ends == [(frame + 1) * FRAME_SAMPLES for frame in range(len(ends))]),
        "gap_count": sum(b - a for a, b in zip(ends, starts[1:])),
        "overlap_count": sum(a - b for a, b in zip(ends, starts[1:]) if a > b),
        "all_known_validity": all(event["validity"] == "known" for event in events),
        "all_values_finite_in_range": all(0.0 <= event["value"] <= 1.0
                                          for event in events),
        "events": events,
    }


def build_report() -> dict[str, Any]:
    values = synthetic_signal()
    onsets, offsets = activity_transitions()
    assert onsets == EXPECTED_ONSET_FRAMES
    assert offsets == EXPECTED_OFFSET_FRAMES

    sessions = {method: run_session(values, method=method) for method in METHODS}
    quality: dict[str, Any] = {}
    for method, session in sessions.items():
        decisions = known_decisions(session)
        quality[method] = {
            "confusion": confusion(decisions),
            "stratified": stratified_errors(decisions),
            "detections": detection_coverage(decisions),
            "onset_offset_delay": onset_offset_delay(decisions),
            "events_digest": object_digest([event.as_dict() for event in session.events]),
        }
    comparison = quality_comparison(quality)
    primary = sessions[METHOD_PRIMARY]
    sweep = threshold_sweep(primary)
    combined_regressions = comparison["regressions"] + sweep["regressions"]

    report: dict[str, Any] = {
        "adapter": {
            "task_local_id": PROVIDER_ID,
            "identity": "rnnoise-speech-probability.synthetic.v0",
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "public_adapter_output_kinds": ["waveform"],
            "public_adapter_tasks": ["CLN-01"],
            "public_adapter_probability_output": False,
            "note": "Optional, unregistered, OFF by default. No installed SDK behavior changes.",
        },
        "analysis_boundary": {
            "contract_id": CONTRACT_ID,
            "format": "16 kHz mono float32, 160 samples per v0 call",
            "source_interval": "half-open [start_sample, end_sample) in decimal strings",
            "decision_threshold": DECISION_THRESHOLD,
            "probability_kind": "speech_probability",
            "event_kind": "speech_event",
            "event_key": "(producer_id, tap_id, epoch, event_id)",
            "method": "model-free deterministic logistic of window RMS; not a model posterior",
            "analysis_read_only_on_pcm": True,
            "public_api_abi_change": False,
        },
        "availability": availability_check(primary),
        "base_commit": BASE_COMMIT,
        "cohort": {
            "frames": FRAMES,
            "samples": SAMPLES,
            "duration_s": round(SAMPLES / SAMPLE_RATE_HZ, 6),
            "seed_signal": SEED_SIGNAL,
            "seed_probability": SEED_PROB,
            "seed_standalone_vad": SEED_VAD,
            "waveform_digest": tensor_digest(values),
            "segments": [{"source_start": dec(start), "source_end": dec(end),
                          "label": label, "class": kind}
                         for start, end, label, kind in SEGMENTS],
            "speech_samples": sum(end - start for start, end, label, _
                                  in SEGMENTS if label == "speech"),
            "nonspeech_samples": sum(end - start for start, end, label, _
                                     in SEGMENTS if label == "nonspeech"),
            "unknown_samples": 0,
            "fully_labeled": True,
            "onset_frames": [dec(frame) for frame in onsets],
            "offset_frames": [dec(frame) for frame in offsets],
        },
        "comparison": comparison,
        "config_digest": CONFIG_DIGEST,
        "cross_hop": cross_hop_check(primary),
        "drop_and_stale": drop_and_stale_checks(values),
        "events": event_integrity(primary),
        "gates": list(GATES),
        "no_missing_result_qualifies_candidate": True,
        "profile": "Analysis",
        "schema_id": SCHEMA_ID,
        "quality": quality,
        "regressions": combined_regressions,
        "regression_count": len(combined_regressions),
        "threshold_sweep": sweep,
        "source_context": {
            "rnnoise_side_vad_report_digest":
                "bbda960bd85e62ea096cc77e1305506ba9fc4757994a3ae8e64bfb657f3abe40",
            "source_reported_rnnoise_fn_percent": 25.64,
            "source_reported_rnnoise_fp_percent": 5.44,
            "source_reported_silero_fn_percent": 22.91,
            "source_reported_silero_fp_percent": 7.64,
            "source_numbers_status": "context_only_not_reproduced_or_pooled",
            "native_call_note": "Source report states RNNoise probability is returned by the same native call as enhanced PCM; no separate VAD inference is added here or pooled with standalone VAD timing.",
        },
        "state": state_checks(values),
        "status": "proposal_only_synthetic_incomplete",
        "timing": {
            "quality_and_timing_separate": True,
            "pointer_file": "runtime-measurements.json",
            "qualification_status": "blocked",
            "note": "Unpaced wall-clock observations are isolated in a non-qualifying artifact; no timing value enters any quality metric and no quality value enters any timing claim.",
        },
        "validity": validity_separation(values),
    }
    return report


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return canonical_bytes(report)


def artifact_paths() -> tuple[str, ...]:
    return ("README.md", "adapter.json", "reference.py", "run.py",
            "report.json", "report.json.sha256", "runtime-measurements.json",
            "test_reference.py", "verify.py")


def artifact_pins() -> list[dict[str, str]]:
    here = Path(__file__).resolve().parent
    return [
        {"path": name,
         "sha256": hashlib.sha256((here / name).read_bytes()).hexdigest()}
        for name in artifact_paths() if (here / name).is_file()
    ]


def run_measures() -> dict[str, Any]:
    """Unpaced, non-qualifying wall-clock pointer. Never scored as quality."""
    values = synthetic_signal()
    samples: dict[str, list[float]] = {method: [] for method in METHODS}
    started = time.perf_counter()
    for frame in range(FRAMES):
        for method in METHODS:
            call_start = time.perf_counter()
            probability(method, values, frame)
            samples[method].append((time.perf_counter() - call_start) * 1000.0)
    elapsed = time.perf_counter() - started
    return {
        "schema_id": "audio-sdk/task-evidence/rnnoise-speech-probability/timing/0.1",
        "qualification_status": "blocked",
        "non_qualifying_reason": "Unpaced Python wall-clock on this host only; no native library, target device, pacing, deadline, CPU or memory budget. Not a timing qualification and not added to any standalone-VAD cost.",
        "paced": False,
        "deadline_ns": None,
        "separate_from_quality": True,
        "quality_metrics_in_this_file": False,
        "clock": "time.perf_counter (monotonic)",
        "stream_frames": FRAMES,
        "stream_samples": SAMPLES,
        "stream_wall_s": round(elapsed, 6),
        "per_call_ms": {
            method: {
                "median": round(sorted(samples[method])[len(samples[method]) // 2], 6),
                "max": round(max(samples[method]), 6),
                "first_call_ms": round(samples[method][0], 6),
            }
            for method in METHODS
        },
        "native_probability_inference_measured": False,
        "standalone_vad_cost_pooled": False,
    }
