# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic autoregressive PLC reference fixture.

Task-local, optional, unregistered evidence for the audio-sdk v0 public
provider boundary. The reference implements a causal all-pole (LPC/AR)
forward predictor for erased 160-sample frames and compares it with the
zero-fill noisy control and the established linear-interpolation and
task-matched autoregressive controls from the pinned source evidence.

No corpus, weights, download, codec runtime, licensed runtime, device or
listening result is used. STOI requires the pinned Python 3.12 scorer
environment; a missing or unpinned scorer is never silently substituted.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import resource
import statistics
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/autoregressive-plc/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/autoregressive-plc/report/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_BURST_FRAMES = 4
BUFFERING_FRAMES = MAX_BURST_FRAMES + 1
BUFFERING_DELAY_SAMPLES = BUFFERING_FRAMES * FRAME_SAMPLES
MAX_DRAIN_CALLS = 8

# Model-free all-pole control, order 16 and 8*order context, matching the
# pinned historical AR waveform control algorithm family (not its weights).
AR_ORDER = 16
AR_CONTEXT_SAMPLES = 8 * AR_ORDER
AR_RIDGE_RELATIVE = 1e-5
AR_RIDGE_ABSOLUTE = 1e-10
AR_BOUND_FACTOR = 1.5
AR_OUTPUT_CLAMP = 0.99

FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2
FLAG_CONCEALMENT = 4

KIND_STARTUP = "startup"
KIND_GOOD = "good"
KIND_CONCEAL = "conceal"
METHODS = ("zero_fill", "linear", "ar")

SCORED_FRAMES = 250
SCORED_SAMPLES = SCORED_FRAMES * FRAME_SAMPLES
SEED_SPEECH = 20261125
SEED_NOISE = 5151

# Zero-based source-frame indices. Same mask as the linear-interpolation
# fixture so the established baseline is directly comparable; the speech
# surrogate uses an independent seed in this fixture.
ERASURE_PLAN: tuple[int, ...] = (
    20, 60, 61, 80, 140, 200, 201, 202, 203,
)
STRATA: dict[str, tuple[int, ...]] = {
    "isolated": (20, 80, 140),
    "two_frame_burst": (60, 61),
    "four_frame_burst": (200, 201, 202, 203),
}
ADVERSARIAL_ERASURES: dict[str, tuple[int, ...]] = {
    "single": (37,),
    "two_frame_burst": (91, 92),
    "max_burst": (150, 151, 152, 153),
    "over_max_burst": (170, 171, 172, 173, 174),
    "boundary_burst": (99, 100, 101, 102),
}

BASE_COMMIT = "9677040cba2929f9936eaa565f200f585d5270a8"
PROVIDER_ID = "dsp.autoregressive-plc-ref.v0"
BASELINE_COMMIT = "03519fb4451a4555c4d1b226cc40d27e4cd7eaa7"
BASELINE_PATH = "docs/task-evidence/linear-interpolation-plc/fixture.py"
BASELINE_SHA256 = "35054c6f79279d9ab64b301a2f2c24dbfdbf776c4e579fe4e9f5d3ede7129e61"

SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "sha256": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
        "summary": "Record 28: Generative PLC / Complex-Bin2bin is unavailable/blocked and AR proxies are not that candidate; record 29: conventional waveform PLC controls include an autoregressive control on a 12-clip erasure screen.",
    },
    {
        "path": "REALTIME_COMPONENT_CANDIDATES.md",
        "sha256": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
        "summary": "Packet-loss-concealment inventory: autoregressive prediction RTF about 0.0057-0.0093, linear about 0.00008, zero-fill about 0.00001; no network trace.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 format, exact source mapping, concealment valid_count=0, state/reset/epoch and timing rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Enhancement acceptance profile: identity/noisy control, task-matched baseline, paired SI-SDR/STOI, preservation, peaks, state, memory and timing.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "sha256": "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
        "summary": "Source-reported 12-clip codec-matched AR/linear/zero-fill controls; pinned context only, not rerun or pooled here.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary; source pin defines the v0 geometry and result flags mirrored by the Python reference.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary; reset/close/epoch/source-mapping semantics are mirrored by the Python reference.",
    },
)

SCORER_PINS: tuple[dict[str, Any], ...] = (
    {
        "id": "pystoi",
        "version": "0.4.1",
        "module": "pystoi/stoi.py",
        "sha256": "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658",
        "mode": "non-extended",
    },
    {
        "id": "numpy",
        "version": "2.5.4",
        "module": "numpy",
        "sha256": None,
        "mode": "required by pinned pystoi",
    },
)

QUALIFICATION_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "real_clean_reference",
        "status": "blocked",
        "reason": "No rights-qualified real clean-reference cohort is available in this task-local fixture. EARS/DNS source values remain source-reported only.",
        "reopen": "Freeze a permitted paired cohort, references, crop and alignment policy before any real quality claim.",
    },
    {
        "id": "authorized_listening",
        "status": "blocked",
        "reason": "No authorized listeners, MUSHRA registration or listening results were collected; the blocked Generative PLC candidate is not represented.",
        "reopen": "Register and run an independently reviewed listening test with consent and output-use permissions.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "Only unpaced wall-clock observations of this Python reference runtime are reported. No paced target-device, installed-provider or deadline qualification was run.",
        "reopen": "Measure the exact installed build on the intended host with pacing, load, buffer and deadline budgets.",
    },
    {
        "id": "codec_network_pipeline",
        "status": "blocked",
        "reason": "No codec-native PLC, captured network trace, jitter buffer, FEC/DRED, stereo path or mobile pipeline is included.",
        "reopen": "Pin codec/network/pipeline assets and test the exact integrated path.",
    },
    {
        "id": "generative_plc_assets",
        "status": "blocked",
        "reason": "No exact staged checkpoint or runtime for Generative PLC / Complex-Bin2bin; this fixture is the model-free AR control only.",
        "reopen": "Pin exact licensed checkpoint, runtime and codec-aligned packet-loss benchmark before evaluating that candidate.",
    },
)


class LCG:
    """Version-stable 32-bit LCG; no dependence on Python random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clean_speech(samples: int = SCORED_SAMPLES,
                 seed: int = SEED_SPEECH) -> tuple[float, ...]:
    """Deterministic speech-like surrogate; not recorded speech."""
    rng = LCG(seed)
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    out: list[float] = []
    for index in range(samples):
        time_s = index / SAMPLE_RATE_HZ
        frame = index // FRAME_SAMPLES
        syllable = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.3 * time_s - 0.6)
        pause = 0.0 if frame % 53 in (49, 50, 51, 52) else 1.0
        envelope = (0.035 + 0.22 * syllable * syllable) * pause
        envelope *= min(1.0, index / 320.0, (samples - index) / 320.0)
        f0 = 108.0 + 26.0 * math.sin(2.0 * math.pi * 0.37 * time_s)
        period = max(1, int(round(SAMPLE_RATE_HZ / f0)))
        drive = (1.0 if index % period == 0 else 0.0) + 0.03 * rng.uniform()
        formant_a[0], formant_a[1] = (
            0.972 * formant_a[0] - 0.018 * formant_a[1] + drive,
            formant_a[0])
        formant_b[0], formant_b[1] = (
            0.947 * formant_b[0] - 0.035 * formant_b[1] + drive,
            formant_b[0])
        value = envelope * (0.45 * formant_a[0] + 0.18 * formant_b[0])
        value += 0.0015 * rng.uniform()
        out.append(max(-0.95, min(0.95, value)))
    return tuple(out)


def form_packet_stream(clean: Sequence[float],
                       erased: Iterable[int] = (),
                       method: str = "ar") -> list[dict[str, Any]]:
    """Build one source-frame record for every 160-sample interval.

    Erased packets are explicit ``present=False`` concealment requests from
    the modeled host delivery adapter; omitting a call would leave an
    unrecoverable output-slot hole in v0.
    """
    if method not in METHODS:
        raise ValueError("unknown concealment method")
    missing = set(int(frame) for frame in erased)
    frames: list[dict[str, Any]] = []
    for frame_index in range(0, len(clean), FRAME_SAMPLES):
        frame_number = frame_index // FRAME_SAMPLES
        present = frame_number not in missing
        chunk = clean[frame_index:frame_index + FRAME_SAMPLES]
        valid = len(chunk) if present else 0
        frames.append({
            "first_input_sample": frame_index,
            "present": present,
            "samples": (tuple(chunk) + (0.0,) * (FRAME_SAMPLES - valid)
                        if present else (0.0,) * FRAME_SAMPLES),
            "valid_count": valid,
            "final": present and valid < FRAME_SAMPLES,
            "method": method,
        })
    return frames


@dataclass
class PlcConfig:
    epoch: int = 1
    first_input_sample: int = 0
    max_burst_frames: int = MAX_BURST_FRAMES
    buffering_frames: int = BUFFERING_FRAMES
    max_drain_calls: int = MAX_DRAIN_CALLS
    ar_order: int = AR_ORDER
    ar_context_samples: int = AR_CONTEXT_SAMPLES
    ar_ridge_relative: float = AR_RIDGE_RELATIVE
    ar_ridge_absolute: float = AR_RIDGE_ABSOLUTE
    ar_bound_factor: float = AR_BOUND_FACTOR
    ar_output_clamp: float = AR_OUTPUT_CLAMP

    def check(self) -> Optional[str]:
        if not isinstance(self.epoch, int) or self.epoch < 1:
            return "rejected_invalid_epoch"
        if not isinstance(self.first_input_sample, int) or self.first_input_sample < 0:
            return "rejected_invalid_first_input_sample"
        if self.max_burst_frames != MAX_BURST_FRAMES:
            return "rejected_invalid_max_burst"
        if self.buffering_frames != BUFFERING_FRAMES:
            return "rejected_invalid_buffering"
        if not isinstance(self.max_drain_calls, int) or not 1 <= self.max_drain_calls <= 1024:
            return "rejected_invalid_drain_cap"
        if self.ar_order != AR_ORDER or self.ar_context_samples != AR_CONTEXT_SAMPLES:
            return "rejected_invalid_ar_model"
        if self.ar_ridge_relative != AR_RIDGE_RELATIVE or self.ar_ridge_absolute != AR_RIDGE_ABSOLUTE:
            return "rejected_invalid_ar_regularization"
        if self.ar_bound_factor != AR_BOUND_FACTOR or self.ar_output_clamp != AR_OUTPUT_CLAMP:
            return "rejected_invalid_ar_bounds"
        return None


@dataclass
class PendingFrame:
    samples: tuple[float, ...]
    source_first: int
    valid_count: int
    flags: int
    kind: str
    unresolved: bool = False


@dataclass
class ProcessResult:
    status: str
    samples: tuple[float, ...] = ()
    produced_count: int = 0
    valid_offset: int = 0
    valid_count: int = 0
    flags: int = 0
    epoch: int = 0
    source_first_sample: int = 0
    queue_depth: int = 0
    kind: str = ""
    reason: str = ""

    @property
    def is_concealment(self) -> bool:
        return bool(self.flags & FLAG_CONCEALMENT)


def solve_toeplitz(autocorr: Sequence[float], order: int,
                   ridge: float) -> Optional[tuple[float, ...]]:
    """Solve R a = r with R[i][j] = autocorr[abs(i-j)] and diagonal ridge.

    Pure-Python Gaussian elimination with partial pivoting. Returns None for
    singular or nonfinite systems so the caller can fall back to zero-fill.
    """
    size = order
    matrix = [[autocorr[abs(i - j)] for j in range(size)]
              for i in range(size)]
    for i in range(size):
        matrix[i][i] += ridge
    rhs = [autocorr[i + 1] for i in range(size)]
    if any(not math.isfinite(v) for row in matrix for v in row) or any(
            not math.isfinite(v) for v in rhs):
        return None
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(matrix[row][column]))
        if abs(matrix[pivot][column]) < 1e-14:
            return None
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            rhs[column], rhs[pivot] = rhs[pivot], rhs[column]
        pivot_value = matrix[column][column]
        for row in range(column + 1, size):
            factor = matrix[row][column] / pivot_value
            if not math.isfinite(factor):
                return None
            for col in range(column, size):
                matrix[row][col] -= factor * matrix[column][col]
            rhs[row] -= factor * rhs[column]
    solution = [0.0] * size
    for row in range(size - 1, -1, -1):
        value = rhs[row]
        for col in range(row + 1, size):
            value -= matrix[row][col] * solution[col]
        solution[row] = value / matrix[row][row]
        if not math.isfinite(solution[row]):
            return None
    return tuple(solution)


class AutoRegressivePlcSession:
    """Python model of the optional v0 delivery-adapter concealment boundary.

    Every source frame has one process call. A missing packet is an explicit
    ``present=False`` request from the host delivery adapter. The AR predictor
    is causal: concealed samples are synthesized from preceding received or
    synthesized samples only. The 5-frame output buffer is an explicit host
    adapter scheduling choice that keeps source slots one-to-one with output
    frames; it is not an intrinsic AR-algorithm delay.
    """

    def __init__(self, config: Optional[PlcConfig] = None) -> None:
        self.config = config or PlcConfig()
        reason = self.config.check()
        if reason:
            raise ValueError(reason)
        self.closed = False
        self.epoch = self.config.epoch
        self.next_input = self.config.first_input_sample
        self.next_output = self.config.first_input_sample - BUFFERING_DELAY_SAMPLES
        self.accepted_end = self.config.first_input_sample
        self.last_received_start: Optional[int] = None
        self.have_last = False
        self.last_good: tuple[float, ...] = ()
        self.ar_history: list[float] = []
        self.queue: list[PendingFrame] = []
        self.pending_conceal: list[PendingFrame] = []
        self.consecutive_erased = 0
        self.drain_calls = 0
        self.stats: dict[str, int] = {
            "submitted_frames": 0,
            "accepted_valid_samples": 0,
            "produced_frames": 0,
            "valid_produced_samples": 0,
            "concealed_frames": 0,
            "unresolved_leading_frames": 0,
            "unresolved_trailing_frames": 0,
            "zero_fill_frames": 0,
            "linear_fill_frames": 0,
            "ar_synth_frames": 0,
            "ar_solver_fallback_frames": 0,
            "ar_clamped_samples": 0,
            "rejected_missing": 0,
            "rejected_shape": 0,
            "rejected_short": 0,
            "rejected_nonfinite": 0,
            "rejected_stale_epoch": 0,
            "rejected_duplicate": 0,
            "rejected_out_of_order": 0,
            "rejected_burst_length": 0,
            "rejected_closed": 0,
            "rejected_after_final": 0,
            "rejected_bad_padding": 0,
        }
        for index in range(BUFFERING_FRAMES):
            self._enqueue(PendingFrame(
                samples=(0.0,) * FRAME_SAMPLES,
                source_first=self.config.first_input_sample
                - (BUFFERING_FRAMES - index) * FRAME_SAMPLES,
                valid_count=0,
                flags=FLAG_STARTUP_PADDING,
                kind=KIND_STARTUP,
            ))

    def _enqueue(self, frame: PendingFrame) -> None:
        self.queue.append(frame)

    def _pop(self) -> PendingFrame:
        return self.queue.pop(0)

    def _reject(self, reason: str) -> ProcessResult:
        key = "rejected_" + reason
        if key in self.stats:
            self.stats[key] += 1
        return ProcessResult(status=key, reason=reason)

    @staticmethod
    def _valid_frame(frame: Any) -> Optional[str]:
        if frame is None:
            return "missing"
        if not isinstance(frame, dict):
            return "shape"
        start = frame.get("first_input_sample")
        values = frame.get("samples")
        valid = frame.get("valid_count", FRAME_SAMPLES)
        if not isinstance(start, int) or isinstance(start, bool) or start < 0:
            return "shape"
        if not isinstance(valid, int) or isinstance(valid, bool) or not 0 <= valid <= FRAME_SAMPLES:
            return "shape"
        present = bool(frame.get("present", True))
        if not present:
            return None if valid == 0 else "shape"
        if valid == 0:
            return "short" if values is not None else "shape"
        if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
            return "shape"
        if len(values) != FRAME_SAMPLES:
            return "short" if len(values) < FRAME_SAMPLES else "shape"
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in values):
            return "shape"
        try:
            as_float = tuple(float(v) for v in values)
        except (TypeError, ValueError, OverflowError):
            return "shape"
        if any(not math.isfinite(v) for v in as_float):
            return "nonfinite"
        final = bool(frame.get("final", False))
        if valid < FRAME_SAMPLES and not final:
            return "short"
        if any(v != 0.0 for v in as_float[valid:]):
            return "bad_padding"
        return None

    def _update_history(self, samples: Sequence[float]) -> None:
        self.ar_history.extend(float(v) for v in samples)
        excess = len(self.ar_history) - AR_CONTEXT_SAMPLES
        if excess > 0:
            del self.ar_history[:excess]

    def _ar_synthesize(self, count: int) -> tuple[float, ...]:
        """Causal all-pole forward prediction with bounded, clamped output."""
        order = self.config.ar_order
        context = self.ar_history[-self.config.ar_context_samples:]
        if len(context) < order + 2:
            self.stats["ar_solver_fallback_frames"] += 1
            return (0.0,) * count
        mean = sum(context) / len(context)
        centered = [v - mean for v in context]
        autocorr = tuple(
            sum(centered[i] * centered[i + lag] for i in range(len(centered) - lag))
            for lag in range(order + 1))
        ridge = (autocorr[0] * self.config.ar_ridge_relative
                 + self.config.ar_ridge_absolute)
        coeff = solve_toeplitz(autocorr, order, ridge)
        if coeff is None:
            self.stats["ar_solver_fallback_frames"] += 1
            return (0.0,) * count
        self.stats["ar_synth_frames"] += 1
        history = list(centered[-order:])
        bound = max(AR_BOUND_FACTOR * max(abs(v) for v in centered), 1e-6)
        clamp = self.config.ar_output_clamp
        out: list[float] = []
        for _ in range(count):
            prediction = sum(coeff[i] * history[-1 - i] for i in range(order))
            prediction = max(-bound, min(bound, prediction))
            value = prediction + mean
            if value < -clamp or value > clamp:
                value = max(-clamp, min(clamp, value))
                self.stats["ar_clamped_samples"] += 1
            out.append(value)
            history.append(prediction)
            history.pop(0)
        self._update_history(out)
        return tuple(out)

    def _resolve_pending(self, right: float, method: str) -> None:
        """Fill buffered linear-interpolation frames once the right endpoint is known."""
        if not self.pending_conceal:
            return
        length = len(self.pending_conceal)
        for index, pending in enumerate(self.pending_conceal):
            if not self.have_last:
                self.stats["unresolved_leading_frames"] += 1
                continue
            left = self.last_good[-1]
            divisor = length * FRAME_SAMPLES + 1
            pending.samples = tuple(
                left + (right - left)
                * (index * FRAME_SAMPLES + sample + 1) / divisor
                for sample in range(FRAME_SAMPLES))
            pending.unresolved = False
            self.stats["linear_fill_frames"] += 1
        self.pending_conceal.clear()

    def process(self, frame: Any) -> ProcessResult:
        if self.closed:
            return self._reject("closed")
        problem = self._valid_frame(frame)
        if problem:
            return self._reject(problem)
        epoch = frame.get("epoch", self.epoch)
        if epoch != self.epoch:
            return self._reject("stale_epoch")
        start = int(frame["first_input_sample"])
        if self.last_received_start is not None and start <= self.last_received_start:
            reason = "duplicate" if start == self.last_received_start else "out_of_order"
            return self._reject(reason)
        if start != self.next_input:
            return self._reject("shape")
        present = bool(frame.get("present", True))
        if not present and self.consecutive_erased >= self.config.max_burst_frames:
            return self._reject("burst_length")
        method = frame.get("method", "ar")
        if method not in METHODS:
            return self._reject("shape")

        flags = FLAG_FINAL_PADDING if (frame.get("final")
                                      and int(frame["valid_count"]) < FRAME_SAMPLES) else 0
        if present:
            samples = tuple(float(v) for v in frame["samples"])
            valid_count = int(frame["valid_count"])
            if method == "linear":
                self._resolve_pending(samples[0], method)
            self._enqueue(PendingFrame(
                samples=samples,
                source_first=start,
                valid_count=valid_count,
                flags=flags,
                kind=KIND_GOOD,
            ))
            self._update_history(samples[:valid_count])
            self.have_last = True
            self.last_good = samples[:valid_count]
            self.consecutive_erased = 0
            self.accepted_end = start + valid_count
            self.stats["accepted_valid_samples"] += valid_count
        else:
            if method == "ar":
                conceal_samples = self._ar_synthesize(FRAME_SAMPLES)
                unresolved = False
            elif method == "zero_fill":
                conceal_samples = (0.0,) * FRAME_SAMPLES
                self.stats["zero_fill_frames"] += 1
                unresolved = False
            else:
                conceal_samples = (0.0,) * FRAME_SAMPLES
                unresolved = True
            pending = PendingFrame(
                samples=conceal_samples,
                source_first=start,
                valid_count=0,
                flags=FLAG_CONCEALMENT,
                kind=KIND_CONCEAL,
                unresolved=unresolved,
            )
            self._enqueue(pending)
            if method == "linear":
                self.pending_conceal.append(pending)
            self.consecutive_erased += 1
            self.stats["concealed_frames"] += 1
            self.accepted_end = start + FRAME_SAMPLES

        self.last_received_start = start
        self.next_input = start + FRAME_SAMPLES
        self.stats["submitted_frames"] += 1

        emitted = self._pop()
        if emitted.source_first != start - BUFFERING_DELAY_SAMPLES:
            raise AssertionError("source mapping drift")
        self.next_output = emitted.source_first + FRAME_SAMPLES
        self.stats["produced_frames"] += 1
        self.stats["valid_produced_samples"] += emitted.valid_count
        return ProcessResult(
            status="ok",
            samples=emitted.samples,
            produced_count=FRAME_SAMPLES,
            valid_offset=0,
            valid_count=emitted.valid_count,
            flags=emitted.flags,
            epoch=self.epoch,
            source_first_sample=emitted.source_first,
            queue_depth=len(self.queue),
            kind=emitted.kind,
        )

    def drain(self) -> list[ProcessResult]:
        results: list[ProcessResult] = []
        if self.closed:
            return [ProcessResult(status="rejected_closed", reason="closed")]
        remaining = sum(1 for frame in self.pending_conceal if frame.unresolved)
        self.stats["unresolved_trailing_frames"] += remaining
        self.pending_conceal.clear()
        while self.queue and self.next_output < self.accepted_end:
            if self.drain_calls >= self.config.max_drain_calls:
                results.append(ProcessResult(status="rejected_drain_cap",
                                             reason="drain_cap"))
                return results
            self.drain_calls += 1
            emitted = self._pop()
            if emitted.source_first != self.next_output:
                raise AssertionError("drain source mapping drift")
            self.next_output = emitted.source_first + FRAME_SAMPLES
            self.stats["produced_frames"] += 1
            self.stats["valid_produced_samples"] += emitted.valid_count
            results.append(ProcessResult(
                status="ok",
                samples=emitted.samples,
                produced_count=FRAME_SAMPLES,
                valid_offset=0,
                valid_count=emitted.valid_count,
                flags=emitted.flags,
                epoch=self.epoch,
                source_first_sample=emitted.source_first,
                queue_depth=len(self.queue),
                kind=emitted.kind,
            ))
        return results

    def reset(self, epoch: int, first_input_sample: int) -> ProcessResult:
        if self.closed:
            return ProcessResult(status="rejected_closed", reason="closed")
        if not isinstance(epoch, int) or epoch <= self.epoch:
            return ProcessResult(status="rejected_stale_epoch", reason="stale_epoch")
        if not isinstance(first_input_sample, int) or first_input_sample < 0:
            return ProcessResult(status="rejected_shape", reason="shape")
        self.__init__(PlcConfig(epoch=epoch, first_input_sample=first_input_sample,
                                max_burst_frames=self.config.max_burst_frames,
                                buffering_frames=self.config.buffering_frames,
                                max_drain_calls=self.config.max_drain_calls))
        return ProcessResult(status="ok", epoch=epoch)

    def close(self) -> None:
        self.closed = True
        self.queue.clear()


def run_stream(frames: Sequence[dict[str, Any]],
               config: Optional[PlcConfig] = None,
               measure: bool = False) -> tuple[list[ProcessResult], dict[str, Any]]:
    """Drive one complete stream and return raw results plus envelope metadata."""
    session = AutoRegressivePlcSession(config)
    results: list[ProcessResult] = []
    durations: list[float] = []
    start_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    wall_start = time.perf_counter()
    first_valid_s: Optional[float] = None
    drain_results: list[ProcessResult] = []
    drain_wall = 0.0
    wall = 0.0
    try:
        for index, frame in enumerate(frames):
            item = dict(frame)
            item.setdefault("epoch", session.epoch)
            t0 = time.perf_counter()
            result = session.process(item)
            durations.append(time.perf_counter() - t0)
            if result.status != "ok":
                raise AssertionError(f"process rejected at {index}: {result.status}")
            if first_valid_s is None and result.valid_count:
                first_valid_s = time.perf_counter() - wall_start
            results.append(result)
        drain_start = time.perf_counter()
        drain_results = session.drain()
        drain_wall = time.perf_counter() - drain_start
        for result in drain_results:
            if result.status != "ok":
                raise AssertionError(f"drain rejected: {result.status}")
            if first_valid_s is None and result.valid_count:
                first_valid_s = time.perf_counter() - wall_start
            results.append(result)
        wall = time.perf_counter() - wall_start
    finally:
        end_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        session.close()
    envelope = {
        "process_frames": len(frames),
        "drain_frames": len(drain_results),
        "stream_wall_s": round(wall, 6),
        "drain_wall_s": round(drain_wall, 6),
        "maxrss_delta_bytes": end_rss - start_rss,
        "first_valid_output_s": (round(first_valid_s, 6)
                                 if first_valid_s is not None else None),
        "first_valid_output_call_index": next(
            (i for i, r in enumerate(results) if r.valid_count), None),
        "process_duration_ms": {
            "median": round(1000.0 * statistics.median(durations), 6),
            "max": round(1000.0 * max(durations), 6),
        },
        "measured": measure,
    }
    return results, envelope


def reconstruct(results: Sequence[ProcessResult], expected_samples: int) -> list[float]:
    """Assemble the developer scoring waveform from raw output frames."""
    out: list[float] = []
    for result in results:
        out.extend(result.samples)
    if len(out) < BUFFERING_DELAY_SAMPLES + expected_samples:
        raise AssertionError("truncated raw output")
    return out[BUFFERING_DELAY_SAMPLES:BUFFERING_DELAY_SAMPLES + expected_samples]


def si_sdr_db(reference: Optional[Sequence[float]],
              estimate: Optional[Sequence[float]]) -> tuple[Optional[float], Optional[str]]:
    """Zero-mean v1 SI-SDR; no centering-free or filter-based variant."""
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    if len(reference) != len(estimate):
        return None, "length_mismatch"
    if not reference or not all(math.isfinite(v) for v in reference) or not all(
            math.isfinite(v) for v in estimate):
        return None, "invalid_input"
    count = len(reference)
    ref_mean = sum(reference) / count
    est_mean = sum(estimate) / count
    ref = [v - ref_mean for v in reference]
    est = [v - est_mean for v in estimate]
    denom = sum(v * v for v in ref)
    if denom == 0.0:
        return None, "zero_reference"
    scale = sum(x * y for x, y in zip(est, ref)) / denom
    projection = [scale * v for v in ref]
    target_energy = sum(v * v for v in projection)
    residual_energy = sum((x - y) ** 2 for x, y in zip(est, projection))
    if target_energy == 0.0:
        return None, "zero_projection"
    if residual_energy == 0.0:
        return None, "exact_reconstruction"
    return round(10.0 * math.log10(target_energy / residual_energy), 6), None


def stoi_score(reference: Optional[Sequence[float]],
               estimate: Optional[Sequence[float]]) -> tuple[Optional[float], Optional[str]]:
    """Pinned pystoi 0.4.1 non-extended scorer; never silently substituted."""
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    if len(reference) != len(estimate) or not reference:
        return None, "invalid_input"
    if not all(math.isfinite(v) for v in reference) or not all(
            math.isfinite(v) for v in estimate) or not any(reference):
        return None, "invalid_input"
    try:
        import numpy as np  # noqa: PLC0415 - pinned environment only
        from pystoi import stoi  # noqa: PLC0415 - pinned environment only
        import importlib.metadata  # noqa: PLC0415
        import inspect  # noqa: PLC0415
        import pathlib  # noqa: PLC0415
        if importlib.metadata.version("pystoi") != "0.4.1" or np.__version__ != "2.5.4":
            return None, "unpinned_scorer"
        module = pathlib.Path(inspect.getfile(stoi))
        digest = hashlib.sha256(module.read_bytes()).hexdigest()
        expected = next(p["sha256"] for p in SCORER_PINS if p["id"] == "pystoi")
        if digest != expected:
            return None, "unpinned_scorer"
        value = float(stoi(np.asarray(reference, dtype=np.float64),
                           np.asarray(estimate, dtype=np.float64),
                           SAMPLE_RATE_HZ, extended=False))
    except ImportError:
        return None, "missing_pinned_scorer"
    except Exception:
        return None, "metric_undefined"
    if not math.isfinite(value):
        return None, "metric_undefined"
    return round(value, 6), None


def features(values: Sequence[float]) -> dict[str, Any]:
    peak = max((abs(v) for v in values), default=0.0)
    rms = math.sqrt(sum(v * v for v in values) / max(len(values), 1))
    return {
        "samples": len(values),
        "finite": all(math.isfinite(v) for v in values),
        "peak_abs": round(peak, 6),
        "rms": round(rms, 6),
        "nonfinite_count": sum(1 for v in values if not math.isfinite(v)),
        "at_or_above_one_count": sum(1 for v in values
                                     if math.isfinite(v) and abs(v) >= 1.0),
        "digest": tensor_digest(values),
    }


def rmse_over(reference: Sequence[float], estimate: Sequence[float],
              indices: Iterable[int]) -> Optional[float]:
    errors = [float(reference[i] - estimate[i]) ** 2 for i in indices
              if 0 <= i < min(len(reference), len(estimate))]
    if not errors:
        return None
    return round(math.sqrt(sum(errors) / len(errors)), 6)


def concealed_intervals(results: Sequence[ProcessResult]) -> list[list[int]]:
    return [[result.source_first_sample,
             result.source_first_sample + FRAME_SAMPLES]
            for result in results if result.is_concealment]


def score_condition(clean: Sequence[float],
                    reconstructed: Sequence[float],
                    results: Sequence[ProcessResult],
                    noisy_reference: Sequence[float]) -> dict[str, Any]:
    identity_si, identity_reason = si_sdr_db(clean, noisy_reference)
    candidate_si, candidate_reason = si_sdr_db(clean, reconstructed)
    identity_stoi, identity_stoi_reason = stoi_score(clean, noisy_reference)
    candidate_stoi, candidate_stoi_reason = stoi_score(clean, reconstructed)
    si_delta = (round(candidate_si - identity_si, 6)
                if candidate_si is not None and identity_si is not None else None)
    stoi_delta = (round(candidate_stoi - identity_stoi, 6)
                  if candidate_stoi is not None and identity_stoi is not None else None)
    ranges = concealed_intervals(results)
    erased_indices = [i for lo, hi in ranges for i in range(lo, hi)]
    lost_rmse = rmse_over(clean, reconstructed, erased_indices)
    valid_indices = [i for i in range(len(clean))
                     if not any(lo <= i < hi for lo, hi in ranges)]
    valid_si, valid_reason = si_sdr_db([clean[i] for i in valid_indices],
                                       [reconstructed[i] for i in valid_indices])
    valid_mismatches = sum(1 for i in valid_indices
                           if reconstructed[i] != clean[i])
    ref_power = sum(v * v for v in noisy_reference) / len(noisy_reference)
    out_power = sum(v * v for v in reconstructed) / len(reconstructed)
    reasons = [r for r in (identity_reason, candidate_reason, identity_stoi_reason,
                           candidate_stoi_reason)
               if r and r != "exact_reconstruction"]
    return {
        "si_sdr_db": {
            "identity_noisy": identity_si,
            "candidate": candidate_si,
            "paired_delta": si_delta,
            "invalid_reasons": [r for r in (identity_reason, candidate_reason) if r],
        },
        "stoi": {
            "identity_noisy": identity_stoi,
            "candidate": candidate_stoi,
            "paired_delta": stoi_delta,
            "invalid_reasons": [r for r in (identity_stoi_reason,
                                            candidate_stoi_reason) if r],
        },
        "clean_preservation": {
            "valid_intervals_si_sdr": valid_si,
            "invalid_reasons": [valid_reason] if valid_reason else [],
            "valid_sample_mismatches": valid_mismatches,
            "valid_samples_bit_identical": valid_mismatches == 0,
            "rms_gain_ratio": (round(math.sqrt(out_power / ref_power), 6)
                               if ref_power > 0 else None),
        },
        "lost_region": {"concealed_rmse": lost_rmse},
        "input": features(noisy_reference),
        "output": features(reconstructed),
        "counts": {
            "produced_frames": len(results),
            "valid_content_samples": sum(r.valid_count for r in results),
            "concealed_frames": sum(1 for r in results if r.is_concealment),
            "final_valid_samples": results[-1].valid_count if results else 0,
        },
        "all_metrics_available": not reasons,
    }


def decoded_intervals(results: Sequence[ProcessResult]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for result in results:
        kind = result.kind
        start = result.source_first_sample
        if runs and runs[-1]["kind"] == kind and runs[-1]["end"] == start:
            run = runs[-1]
            run["end"] = start + FRAME_SAMPLES
            run["frames"] += 1
            run["valid_count_sum"] += result.valid_count
            run["flags"].update([result.flags])
        else:
            runs.append({
                "kind": kind,
                "start": start,
                "end": start + FRAME_SAMPLES,
                "frames": 1,
                "valid_count_sum": result.valid_count,
                "flags": {result.flags},
            })
    for run in runs:
        run["flags"] = sorted(run["flags"])
    decoded = [r for r in results if r.kind in (KIND_GOOD, KIND_CONCEAL)]
    return {
        "runs": runs,
        "first_decoded_source_sample": decoded[0].source_first_sample if decoded else None,
        "last_decoded_source_sample_exclusive": (
            decoded[-1].source_first_sample + FRAME_SAMPLES if decoded else None),
        "decoded_frames": len(decoded),
        "decoded_samples": len(decoded) * FRAME_SAMPLES,
        "decoded_duration_s": round(len(decoded) * FRAME_SAMPLES / SAMPLE_RATE_HZ, 6),
        "valid_content_samples": sum(r.valid_count for r in decoded),
        "concealed_frames": sum(1 for r in decoded if r.is_concealment),
        "invalid_zero_length_frames": sum(1 for r in decoded
                                          if r.produced_count != FRAME_SAMPLES),
    }


def impurity_free(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite report value")
    if isinstance(value, dict):
        return {key: impurity_free(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [impurity_free(item) for item in value]
    return value


def build_report(boundary_smoke_path: Optional[Path] = None) -> dict[str, Any]:
    """Generate the canonical deterministic report object."""
    clean = clean_speech()
    erased = set(ERASURE_PLAN)
    inputs = {
        "identity_clean": form_packet_stream(clean, ()),
        "zero_fill_noisy_control": form_packet_stream(clean, erased, method="zero_fill"),
        "linear_interpolation_baseline": form_packet_stream(clean, erased, method="linear"),
        "autoregressive_plc": form_packet_stream(clean, erased, method="ar"),
    }
    results = {name: run_stream(frames)[0] for name, frames in inputs.items()}
    waves = {name: reconstruct(items, len(clean))
             for name, items in results.items()}
    noisy = waves["zero_fill_noisy_control"]
    conditions = {
        name: score_condition(
            clean, waves[name], results[name],
            clean if name == "identity_clean" else noisy)
        for name in inputs
    }

    erased_indices = [frame * FRAME_SAMPLES + sample
                      for frame in ERASURE_PLAN for sample in range(FRAME_SAMPLES)]
    stratification: dict[str, Any] = {}
    for name, frames in STRATA.items():
        indices = [frame * FRAME_SAMPLES + sample
                   for frame in frames for sample in range(FRAME_SAMPLES)]
        stratification[name] = {
            "erased_frames": list(frames),
            "erased_samples": len(indices),
            "per_condition_rmse": {
                condition: rmse_over(clean, waves[condition], indices)
                for condition in inputs
            },
            "per_frame_rmse": {
                condition: {
                    str(frame): rmse_over(
                        clean, waves[condition],
                        range(frame * FRAME_SAMPLES, (frame + 1) * FRAME_SAMPLES))
                    for frame in frames
                }
                for condition in inputs
            },
        }
    erasure_stratification = {
        "strata": stratification,
        "all_erased_indices": erased_indices,
        "all_erased_samples": len(erased_indices),
        "identity_is_exact_on_erased_intervals": all(
            clean[i] == waves["identity_clean"][i] for i in erased_indices),
    }

    intervals = {name: decoded_intervals(items) for name, items in results.items()}
    availability = {
        name: {
            "produced_frames": len(items),
            "first_valid_output_call_index": next(
                (i for i, r in enumerate(items) if r.valid_count), None),
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "duration_semantics": "one 160-sample output slot per source frame; "
                                  "startup/drain slots are padding, concealed slots "
                                  "carry flag 4 and valid_count 0",
        }
        for name, items in results.items()
    }

    impulse = [0.0] * len(clean)
    impulse[4000] = 0.8
    impulse_frames = form_packet_stream(impulse, ())
    impulse_results, _ = run_stream(impulse_frames)
    impulse_raw = [v for result in impulse_results for v in result.samples]
    peak_index = max(range(len(impulse_raw)),
                     key=lambda index: abs(impulse_raw[index]))
    alignment = {
        "declared_buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "declared_buffering_delay_frames": BUFFERING_FRAMES,
        "ar_algorithm_intrinsic_delay_samples": 0,
        "raw_source_origin_sample": -BUFFERING_DELAY_SAMPLES,
        "measured_raw_peak_index": peak_index,
        "expected_raw_peak_index": BUFFERING_DELAY_SAMPLES + 4000,
        "measured_content_lag_samples": peak_index
        - (BUFFERING_DELAY_SAMPLES + 4000),
        "source_interval": [0, len(clean)],
        "raw_interval": [-BUFFERING_DELAY_SAMPLES,
                         -BUFFERING_DELAY_SAMPLES + len(impulse_raw)],
        "valid_output_samples": sum(r.valid_count
                                    for r in results["identity_clean"]),
        "source_mapping_checks": all(
            r.source_first_sample == frame["first_input_sample"]
            - BUFFERING_DELAY_SAMPLES
            for r, frame in zip(results["identity_clean"], inputs["identity_clean"])),
    }

    short = form_packet_stream(clean[:FRAME_SAMPLES * 8], ())
    a_results, _ = run_stream(short)
    b_results, _ = run_stream([
        {**frame, "samples": tuple(0.7 * v for v in frame["samples"])}
        for frame in short])
    reset_session = AutoRegressivePlcSession(PlcConfig(epoch=1))
    for frame in short:
        reset_session.process(dict(frame))
    reset_status = reset_session.reset(2, 0)
    stale_after_reset = reset_session.process({**short[0], "epoch": 1})
    reset_results: list[ProcessResult] = []
    for frame in short:
        reset_results.append(reset_session.process({**frame, "epoch": 2}))
    reset_results.extend(reset_session.drain())
    fresh_results, _ = run_stream(short, PlcConfig(epoch=2))
    reset_session.close()
    closed_result = reset_session.process(dict(short[0]))
    live_session = AutoRegressivePlcSession(PlcConfig(epoch=1))
    for frame in inputs["autoregressive_plc"]:
        live_session.process(dict(frame))
    live_session.drain()
    live_history_len = len(live_session.ar_history)
    live_queue_depth = len(live_session.queue)
    live_session.close()
    state_observations = {
        "ar_history_samples_after_250_frames": live_history_len,
        "queue_depth_after_drain": live_queue_depth,
        "max_queue_depth_during_process": max(r.queue_depth
                                              for r in results["autoregressive_plc"]),
    }
    state = {
        "separate_sessions_uncoupled": [v for v in a_results] != [v for v in b_results],
        "reset_accepted": reset_status.status == "ok",
        "stale_epoch_after_reset_rejected": stale_after_reset.status
        == "rejected_stale_epoch",
        "reset_bit_identical_to_fresh_epoch2": [
            (r.samples, r.flags, r.source_first_sample) for r in reset_results
        ] == [(r.samples, r.flags, r.source_first_sample) for r in fresh_results],
        "closed_session_rejects_process": closed_result.status == "rejected_closed",
        "memory_bounded_by_context": live_history_len == AR_CONTEXT_SAMPLES,
        "bounded_queue_depth": all(r.queue_depth <= BUFFERING_FRAMES
                                   for r in results["autoregressive_plc"]),
    }

    adverse: dict[str, Any] = {}

    def stream_state(session: AutoRegressivePlcSession) -> dict[str, int]:
        return {key: value for key, value in session.stats.items()
                if not key.startswith("rejected_")}

    probe = AutoRegressivePlcSession(PlcConfig(epoch=7))
    baseline_before = stream_state(probe)
    adverse["missing_frame"] = {
        "status": probe.process(None).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["wrong_frame_shape"] = {
        "status": probe.process({"first_input_sample": 0,
                                 "samples": ((0.0,),) * FRAME_SAMPLES}).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["short_frame"] = {
        "status": probe.process({"first_input_sample": 0,
                                 "samples": (0.0,) * (FRAME_SAMPLES - 1)}).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["zero_length_frame"] = {
        "status": probe.process({"first_input_sample": 0,
                                 "samples": (), "valid_count": 0}).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["nonfinite_input"] = {
        "status": probe.process({"first_input_sample": 0,
                                 "samples": (float("nan"),) * FRAME_SAMPLES}).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["stale_epoch"] = {
        "status": probe.process({**short[0], "epoch": 6}).status,
        "state_unchanged": stream_state(probe) == baseline_before,
    }
    adverse["invalid_epoch"] = {
        "status": AutoRegressivePlcSession(PlcConfig()).reset(0, 0).status,
        "state_unchanged": True,
    }
    good_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    first_ok = good_probe.process(dict(short[0]))
    second_ok = good_probe.process(dict(short[1]))
    accepted_after_two = good_probe.stats["accepted_valid_samples"]
    duplicate = good_probe.process(dict(short[1]))
    accepted_after_duplicate = good_probe.stats["accepted_valid_samples"]
    out_of_order = good_probe.process(dict(short[0]))
    after_order = good_probe.stats["accepted_valid_samples"]
    valid_after_order = good_probe.process(dict(short[2]))
    adverse["duplicate_packet"] = {
        "status": duplicate.status,
        "state_unchanged": accepted_after_duplicate == accepted_after_two,
    }
    adverse["out_of_order_packet"] = {
        "status": out_of_order.status,
        "state_unchanged": after_order == accepted_after_two,
    }
    adverse["order_recovery"] = {
        "status": valid_after_order.status,
        "accepted_valid_samples": good_probe.stats["accepted_valid_samples"],
        "consistent_counts": after_order == 2 * FRAME_SAMPLES
        and good_probe.stats["accepted_valid_samples"] == 3 * FRAME_SAMPLES,
        "first_ok": first_ok.status == "ok" and second_ok.status == "ok",
    }
    good_probe.close()

    burst_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 160],
                                    ADVERSARIAL_ERASURES["max_burst"], method="ar"):
        burst_probe.process(dict(frame))
    burst_probe.drain()
    max_burst_stats = dict(burst_probe.stats)
    burst_probe.close()

    boundary_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 160],
                                    ADVERSARIAL_ERASURES["boundary_burst"],
                                    method="ar"):
        boundary_probe.process(dict(frame))
    boundary_probe.drain()
    boundary_concealed = boundary_probe.stats["concealed_frames"]
    boundary_probe.close()

    over_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    over_before = over_probe.stats.copy()
    over_statuses = [
        over_probe.process({"first_input_sample": index * FRAME_SAMPLES,
                            "present": False,
                            "samples": (0.0,) * FRAME_SAMPLES,
                            "valid_count": 0,
                            "method": "ar",
                            "epoch": 1}).status
        for index in range(MAX_BURST_FRAMES + 1)
    ]
    over_probe.close()
    leading_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    leading_process = leading_probe.process({
        "first_input_sample": 0,
        "present": False,
        "samples": (0.0,) * FRAME_SAMPLES,
        "valid_count": 0,
        "method": "ar",
        "epoch": 1})
    leading_drain = leading_probe.drain()
    leading_stats = dict(leading_probe.stats)
    leading_probe.close()
    leading_conceal = [r for r in leading_drain if r.is_concealment]
    trailing_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 40], (38, 39),
                                    method="linear"):
        trailing_probe.process(dict(frame))
    trailing_probe.drain()
    trailing_stats = dict(trailing_probe.stats)
    trailing_probe.close()

    conceal_probe = AutoRegressivePlcSession(PlcConfig(epoch=1))
    conceal_results: list[ProcessResult] = []
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 40], (10,), method="ar"):
        conceal_results.append(conceal_probe.process(dict(frame)))
    conceal_results.extend(conceal_probe.drain())
    conceal_probe.close()
    conceal_flags = [r.flags for r in conceal_results if r.is_concealment]
    valid_content_samples = sum(r.valid_count for r in conceal_results)
    zero_not_counted = bool(conceal_flags) and all(
        r.valid_count == 0 for r in conceal_results if r.is_concealment)

    adverse["erase_burst_length"] = {
        "max_concealed_burst_frames": MAX_BURST_FRAMES,
        "max_burst_concealed_frames": max_burst_stats["concealed_frames"],
        "max_burst_ar_synth_frames": max_burst_stats["ar_synth_frames"],
        "over_max_status": over_statuses[-1],
        "over_max_accepted": over_statuses[:MAX_BURST_FRAMES]
        == ["ok"] * MAX_BURST_FRAMES,
        "over_max_state_unchanged": over_probe.stats["accepted_valid_samples"]
        == over_before["accepted_valid_samples"],
    }
    adverse["erase_boundary"] = {
        "leading_erasure_status": leading_process.status,
        "leading_zero_valid_output": bool(leading_conceal)
        and all(r.valid_count == 0 for r in leading_conceal),
        "leading_ar_synth_frames": leading_stats["ar_synth_frames"],
        "leading_ar_fallback_frames": leading_stats["ar_solver_fallback_frames"],
        "leading_zero_fill_fallback_explicit": leading_stats["ar_synth_frames"] == 0
        and leading_stats["ar_solver_fallback_frames"] == 1,
        "trailing_unresolved_frames": trailing_stats["unresolved_trailing_frames"],
        "boundary_burst_plan": list(ADVERSARIAL_ERASURES["boundary_burst"]),
        "boundary_burst_concealed": boundary_concealed,
    }
    adverse["concealment_zero_valid_output"] = {
        "concealment_flags": sorted(set(conceal_flags)),
        "concealment_valid_count_zero": zero_not_counted,
        "valid_content_samples": valid_content_samples,
        "concealment_excluded_from_valid_content": zero_not_counted
        and valid_content_samples == 39 * FRAME_SAMPLES,
        "produced_frames_include_concealment": len(conceal_results) > 0,
    }
    adverse["final_short_frame"] = {
        "samples": form_packet_stream(clean[:FRAME_SAMPLES * 8 + 37], ())[-1][
            "valid_count"],
        "accepted_valid_samples": 8 * FRAME_SAMPLES + 37,
    }
    ar_session_stats: dict[str, dict[str, int]] = {}
    for name, frames in inputs.items():
        run_session = AutoRegressivePlcSession(PlcConfig(epoch=1))
        for frame in frames:
            run_session.process(dict(frame))
        run_session.drain()
        ar_session_stats[name] = {
            key: value for key, value in run_session.stats.items()
            if key.startswith("ar_") or key in ("concealed_frames",
                                                "unresolved_trailing_frames")
        }
        run_session.close()
    adverse["ar_state_and_output"] = {
        "per_condition": ar_session_stats,
        "causal_synthesis_count": ar_session_stats["autoregressive_plc"]["ar_synth_frames"],
        "finite_clamped_output": conditions["autoregressive_plc"]["output"]["finite"]
        and conditions["autoregressive_plc"]["output"]["at_or_above_one_count"] == 0,
    }

    boundary: dict[str, Any] = {
        "provider_id": PROVIDER_ID,
        "base_commit": BASE_COMMIT,
        "smoke_status": "not_recorded",
        "smoke_path": "boundary-smoke.json",
        "smoke_sha256": None,
    }
    if boundary_smoke_path is not None and boundary_smoke_path.is_file():
        raw = boundary_smoke_path.read_bytes()
        payload = json.loads(raw)
        boundary = {
            "provider_id": PROVIDER_ID,
            "base_commit": BASE_COMMIT,
            "smoke_status": payload.get("result"),
            "smoke_path": boundary_smoke_path.name,
            "smoke_sha256": hashlib.sha256(raw).hexdigest(),
            "off_output_digest": payload.get("off_output_digest"),
            "on_output_digest": payload.get("on_output_digest"),
            "ctest_passed": payload.get("ctest_passed"),
        }

    source_pin_digests = {pin["path"]: pin["sha256"] for pin in SOURCE_PINS}
    fixture_spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "buffering_frames": BUFFERING_FRAMES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "max_burst_frames": MAX_BURST_FRAMES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "ar_order": AR_ORDER,
        "ar_context_samples": AR_CONTEXT_SAMPLES,
        "ar_ridge_relative": AR_RIDGE_RELATIVE,
        "ar_ridge_absolute": AR_RIDGE_ABSOLUTE,
        "ar_bound_factor": AR_BOUND_FACTOR,
        "ar_output_clamp": AR_OUTPUT_CLAMP,
        "scored_frames": SCORED_FRAMES,
        "erasure_plan": list(ERASURE_PLAN),
        "strata": STRATA,
        "adversarial_erasures": ADVERSARIAL_ERASURES,
        "seeds": {"speech": SEED_SPEECH, "noise": SEED_NOISE},
        "source_pins": source_pin_digests,
        "scorer_pins": [dict(pin) for pin in SCORER_PINS],
        "baseline_pin": {
            "commit": BASELINE_COMMIT,
            "path": BASELINE_PATH,
            "sha256": BASELINE_SHA256,
        },
        "base_commit": BASE_COMMIT,
    }

    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": "optional task-local synthetic reference; not a release or real-audio qualification",
        "profile": "Enhancement",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "base_commit": BASE_COMMIT,
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": list(SOURCE_PINS),
        "scorer_pins": [dict(pin) for pin in SCORER_PINS],
        "baseline_pin": fixture_spec["baseline_pin"],
        "boundary": boundary,
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "max_burst_frames": MAX_BURST_FRAMES,
            "ar_order": AR_ORDER,
            "ar_context_samples": AR_CONTEXT_SAMPLES,
        },
        "cohort": {
            "kind": "deterministic_synthetic_paired",
            "frames": SCORED_FRAMES,
            "samples": len(clean),
            "duration_seconds": round(len(clean) / SAMPLE_RATE_HZ, 6),
            "clean_digest": tensor_digest(clean),
            "speech_seed": SEED_SPEECH,
            "erased_frames": list(ERASURE_PLAN),
            "erased_frame_count": len(ERASURE_PLAN),
            "erased_sample_count": len(ERASURE_PLAN) * FRAME_SAMPLES,
        },
        "conditions": conditions,
        "erasure_stratification": erasure_stratification,
        "decoded_intervals": intervals,
        "availability": availability,
        "alignment": alignment,
        "state": state,
        "state_observations": state_observations,
        "adverse": adverse,
        "controls_all_pass": all(
            item.get("state_unchanged", True) for item in adverse.values()
            if isinstance(item, dict)),
        "alignment_pass": alignment["measured_content_lag_samples"] == 0
        and alignment["source_mapping_checks"],
        "state_pass": all(state.values()),
        "all_metrics_available": all(
            item["all_metrics_available"] for item in conditions.values()),
        "all_outputs_finite": all(item["output"]["finite"]
                                  for item in conditions.values())
        and all(item["output"]["at_or_above_one_count"] == 0
                for item in conditions.values()),
        "evidence_classes": {
            "synthetic_paired": "Generated here under a fixed seed; clean reference is the same synthetic source.",
            "historical_source_reported": "Opus PLC, candidate-matrix AR and RTF values are pinned context only; not rerun or pooled.",
            "unpaired_predictive_or_listening": "none",
            "real_audio_rights_qualified": "none",
        },
        "blockers": list(QUALIFICATION_BLOCKERS),
        "measurement_pointer": {
            "path": "runtime-measurements.json",
            "non_deterministic": True,
            "note": "Unpaced wall-clock and RSS observations for the exact Python reference runtime; not a deadline or target-device claim.",
        },
        "no_missing_result_qualifies_candidate": True,
    }
    return impurity_free(report)


def build_runtime_measurements() -> dict[str, Any]:
    """Collect non-deterministic envelope timing for the exact Python runtime."""
    clean = clean_speech()
    erased = set(ERASURE_PLAN)
    frames = {
        "identity_clean": form_packet_stream(clean, ()),
        "zero_fill_noisy_control": form_packet_stream(clean, erased, method="zero_fill"),
        "linear_interpolation_baseline": form_packet_stream(clean, erased, method="linear"),
        "autoregressive_plc": form_packet_stream(clean, erased, method="ar"),
    }
    envelopes = {name: run_stream(items, measure=True)[1]
                 for name, items in frames.items()}
    return {
        "schema_id": SCHEMA_ID + "/runtime-measurements",
        "non_deterministic": True,
        "base_commit": BASE_COMMIT,
        "runtime": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "numpy": "2.5.4",
            "pystoi": "0.4.1",
        },
        "pacing": "unpaced",
        "load": "one synthetic stream at a time, no competing load",
        "deadline_ns": None,
        "qualification_status": "blocked",
        "per_condition": envelopes,
        "note": "ru_maxrss is a coarse process high-water mark; availability is elapsed time to the first frame with valid samples. Neither is a target timing claim.",
    }


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + b"\n"


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit(
            "usage: fixture.py <report.json> <runtime-measurements.json> "
            "[boundary-smoke.json]")
    report_path, measurements_path = map(Path, sys.argv[1:3])
    boundary_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    report = build_report(boundary_path)
    measurements = build_runtime_measurements()
    report_path.write_bytes(canonical_report_bytes(report))
    measurements_path.write_bytes(
        json.dumps(measurements, sort_keys=True, indent=2, ensure_ascii=False,
                   allow_nan=False).encode("utf-8") + b"\n")
    print(f"report_sha256={hashlib.sha256(report_path.read_bytes()).hexdigest()}")
    print(f"fixture_digest={report['fixture_digest']}")
    print(f"all_metrics_available={report['all_metrics_available']} "
          f"controls_all_pass={report['controls_all_pass']} "
          f"alignment_pass={report['alignment_pass']} state_pass={report['state_pass']} "
          f"all_outputs_finite={report['all_outputs_finite']}")


if __name__ == "__main__":
    main()
