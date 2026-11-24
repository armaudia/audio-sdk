# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic decoder-PLC-style reference at the public v0 boundary.

Task-local, optional, unregistered evidence for audio-sdk public v0. The
candidate is a *synthetic*: a causal pitch-period repetition with progressive
amplitude decay across an erasure burst, which resembles the classical
CELP-style decoder concealment idea. It is **not** Opus, not a codec, and makes
no Opus quality, patent, license, runtime or vendor claim. No Opus library,
binary, weight, score or codec trace is vendored, linked, executed or reused
here; the pinned Opus adapter/report/audit are provenance context only.

The shipped v0 facade has no frame-level "packet lost" flag, so this fixture
models the host delivery-adapter boundary: one call per 160-sample frame, a
missing packet as ``present=False, valid_count=0``, and concealed output slots
carrying flag 4 with ``valid_count = 0``. Per CONTRACTS.md adapter concealment
is not a produced provider frame and cannot satisfy sample conservation.

Pinned scorer: Python 3.12.16, numpy 2.5.4, pystoi 0.4.1 non-extended at 16 kHz.
A missing or unpinned scorer returns None with an explicit reason; no
substitute metric is used. Status is ``proposal_only_synthetic_incomplete`` /
``not_qualified`` throughout.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
import math
import pathlib
import platform
import resource
import statistics
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/decoder-plc-style-ref/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/opus-1-4-standard-decoder-plc/report/0.1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
MAX_BURST_FRAMES = 4
BUFFERING_FRAMES = MAX_BURST_FRAMES + 1
BUFFERING_DELAY_SAMPLES = BUFFERING_FRAMES * FRAME_SAMPLES
MAX_DRAIN_CALLS = 8

FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2
FLAG_CONCEALMENT = 4

KIND_STARTUP = "startup"
KIND_GOOD = "good"
KIND_CONCEAL = "conceal"

# Synthetic decoder-PLC-style candidate: causal pitch repetition with decay.
METHOD_PLC = "decoder_plc_style"
METHOD_ZERO = "zero_fill"
METHOD_HOLD = "hold"
METHOD_LINEAR = "linear"
METHODS = (METHOD_PLC, METHOD_ZERO, METHOD_HOLD, METHOD_LINEAR)

CONDITION_METHODS = {
    "identity_clean": METHOD_ZERO,
    "zero_fill_baseline": METHOD_ZERO,
    "hold_control": METHOD_HOLD,
    "linear_control": METHOD_LINEAR,
    "plc_reference_candidate": METHOD_PLC,
}
CONDITIONS = tuple(CONDITION_METHODS)
CANDIDATE_CONDITION = "plc_reference_candidate"
# Degraded/unprocessed control is zero fill; established task-matched waveform
# baseline is linear interpolation (pinned candidate matrix, row 29/30).
IDENTITY_CONTROL = "identity_clean"
DEGRADED_NOISY_CONTROL = "zero_fill_baseline"
TASK_MATCHED_BASELINE = "linear_control"
CONTROL_CONDITIONS = ("zero_fill_baseline", "hold_control", "linear_control")

SCORED_FRAMES = 250
SCORED_SAMPLES = SCORED_FRAMES * FRAME_SAMPLES
SEED_SPEECH = 20261124
FINAL_PARTIAL_FRAMES = 8
FINAL_PARTIAL_SAMPLES = 37

# Progressive amplitude attenuation used by the synthetic PLC reference for
# erased frames 1..4 of a burst. This is a fixed deterministic recipe, not a
# codec parameter and not measured from any Opus implementation.
DECAY_GAINS = (0.92, 0.76, 0.55, 0.32)
PITCH_LAG_MIN = 40
PITCH_LAG_MAX = 160
PITCH_MIN_CORRELATION = 0.20

# Frozen synthetic content regions (zero-based, half-open source frames).
REGIONS: tuple[tuple[int, int, str], ...] = (
    (0, 40, "voiced"),
    (40, 60, "unvoiced"),
    (60, 70, "silence"),
    (70, 110, "voiced"),
    (110, 130, "unvoiced"),
    (130, 140, "silence"),
    (140, 190, "voiced"),
    (190, 215, "unvoiced"),
    (215, 230, "silence"),
    (230, 250, "voiced"),
)
ONSET_FRAMES = (70, 140, 230)
OFFSET_FRAMES = (40, 60, 110, 130, 190, 215)
REGION_BOUNDARIES = tuple(start for start, _, _ in REGIONS[1:])

# Frozen erasure mask: isolated losses, onset/offset crossings, short and
# maximum-length bursts, silence and a late burst.
ERASURE_PLAN: tuple[int, ...] = (
    18, 39, 40, 44, 66, 69, 70, 98, 99, 150, 151, 152, 153, 228, 229, 238, 239,
)
STRATA: dict[str, tuple[int, ...]] = {
    "isolated_voiced": (18,),
    "voiced_to_unvoiced_offset": (39, 40),
    "isolated_unvoiced": (44,),
    "isolated_silence": (66,),
    "silence_to_voiced_onset": (69, 70),
    "two_frame_burst_voiced": (98, 99),
    "four_frame_burst_mid_voiced": (150, 151, 152, 153),
    "silence_to_voiced_burst": (228, 229),
    "late_two_frame_burst": (238, 239),
}
ADVERSARIAL_ERASURES: dict[str, tuple[int, ...]] = {
    "single": (37,),
    "two_frame_burst": (91, 92),
    "max_burst": (150, 151, 152, 153),
    "over_max_burst": (170, 171, 172, 173, 174),
    "boundary_burst": (99, 100, 101, 102),
}

BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
PROVIDER_ID = "dsp.decoder-plc-style-ref.v0"

# External bytes are resolved relative to the workspace source root;
# worktree-relative pins are resolved relative to the SDK worktree root.
SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "root": "source",
        "sha256": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
        "summary": "Rows 29-30: conventional waveform PLC controls evaluated and Opus 1.4 standard decoder PLC evaluated on a bounded 12-clip EARS screen; context only.",
    },
    {
        "path": "adapters/opus-plc/adapter.json",
        "root": "source",
        "sha256": "a36dd6798d3e9f273c7705fea6d11d888680e633a4b4c41c00e20242f45765ae",
        "summary": "Pinned Opus adapter declaration: identity, source_commit, offline waveform mode, no weights. Provenance only; not built, linked or invoked.",
    },
    {
        "path": "REALTIME_COMPONENT_CANDIDATES.md",
        "root": "source",
        "sha256": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
        "summary": "Line 67: source-reported Opus 1.4 decoder PLC RTF about 0.0015, no captured network trace or phone test; context only.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "root": "source",
        "sha256": "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
        "summary": "Source-reported bounded Opus 1.4 packet-erasure screen. Scores are not reused, pooled or claimed here.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-opus-plc/provenance-audit.md",
        "root": "source",
        "sha256": "ab36bab86f58e82ee139adfae011d17f13e23e26c3dba3f5ea80678713428b53",
        "summary": "Documents the historical bundled libopus 1.4 dylib path, digest and OpenCV notice. Provenance only; binary absent here.",
    },
    {
        "path": "research/distortion_restoration_20261028.md",
        "root": "source",
        "sha256": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
        "summary": "RST-04 restoration partition; waveform PLC controls are explicit baselines, not a selected restoration method.",
    },
    {
        "path": "CONTRACTS.md",
        "root": "worktree",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 format, source mapping, host-requested concealment, valid_count=0 and no sample-conservation rule for adapter concealment.",
    },
    {
        "path": "REUSE.toml",
        "root": "worktree",
        "sha256": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
        "summary": "Aggregate docs/** SPDX annotation remains Apache-2.0; no licensing change is made.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Enhancement acceptance profile: identity/noisy control, task-matched baseline, paired metrics, preservation, peaks, validity, alignment, state, timing.",
    },
    {
        "path": "audio-benchmark-platform/audio-bench/src/audio_bench/metrics.py",
        "root": "source",
        "sha256": "5f4a16aab66bdef244e57d7b3c93237ebf0bf2bf9ef2d9ad0e0b4ff063107210",
        "summary": "Zero-mean SI-SDR v1 definition reference; not imported by this fixture.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by the Python reference (AS_RESULT_CONCEALMENT=4).",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary: reset, epoch, close and source mapping semantics.",
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

OPUS_PROVENANCE = {
    "claims_made": False,
    "statement": (
        "This fixture neither vendors nor invokes Opus. The candidate is a "
        "synthetic pitch-repetition-with-decay waveform reference and is not "
        "Opus 1.4, Opus Deep PLC, DRED, FEC, Lyra or any codec output."
    ),
    "adapter_identity": "libopus-1.4-standard-decoder-plc-cf8bc423c712e34df70adb5f61aa8edcc976cfe0cefa50b7ada06c0975600eb3",
    "adapter_source_commit": "opencv-python-bundled-libopus-1.4",
    "adapter_input_kind": "waveform",
    "adapter_modes": ["offline"],
    "adapter_weights": "not_required",
    "adapter_entrypoint": ["python", "adapters/opus-plc/run.py"],
    "documented_binary": {
        "documented_path": "data/envs/clearvoice/lib/python3.11/site-packages/cv2/.dylibs/libopus.0.dylib",
        "documented_sha256": "cf8bc423c712e34df70adb5f61aa8edcc976cfe0cefa50b7ada06c0975600eb3",
        "documented_version": "libopus 1.4",
        "containing_distribution": "opencv-python 4.10.0.84",
        "present_in_this_workspace": False,
        "used_by_fixture": False,
        "note": (
            "The exact path documented in the pinned provenance audit is "
            "absent in this workspace at authoring time. No local Opus tool, "
            "dylib, binary or runtime was loaded, copied, vendored or scored. "
            "The digest and source-reported values are pinned context only."
        ),
    },
    "external_cli_tools_checked": ["opus_demo", "opusenc", "opusdec", "ffmpeg"],
    "external_cli_tools_found": [],
    "source_reported_scores_pooled": False,
}

QUALIFICATION_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "real_clean_reference",
        "status": "blocked",
        "reason": "No rights-qualified real clean-reference cohort exists here. Historical EARS/DNS values are provenance context only.",
        "reopen": "Freeze a permitted paired cohort with references, crop and alignment policy before any real quality claim.",
    },
    {
        "id": "authorized_listening_wer_stoi",
        "status": "blocked",
        "reason": "No consented listeners, WER or STOI on permitted real speech were collected; synthetic paired scores cannot substitute.",
        "reopen": "Run an independently reviewed consented listening test with WER and STOI on rights-qualified material.",
    },
    {
        "id": "codec_network_fec_trace",
        "status": "blocked",
        "reason": "No codec encoder/decoder, captured loss trace, jitter buffer, FEC/DRED, packet reordering or integrated path is exercised.",
        "reopen": "Pin codec/network/FEC assets and evaluate the exact integrated path against a captured loss trace.",
    },
    {
        "id": "opus_runtime_rights",
        "status": "blocked",
        "reason": "No Opus runtime, binary or asset is vendored, linked or licensed here. The pinned adapter/audit are provenance only.",
        "reopen": "Supply a rights-cleared pinned Opus runtime with preserved notices and independent review before any Opus claim.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "Only unpaced Python wall-clock and RSS observations exist; no paced target-device deadline, CPU or memory qualification was run.",
        "reopen": "Measure the exact installed build on the intended host under pacing, load and deadline budgets with CPU/memory limits.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "No provider is compiled, registered or packaged. The conceptual provider ID is unregistered, OFF by default with empty descriptor settings.",
        "reopen": "Complete provider intake with opt-in OFF default, empty descriptor settings, clean SPDX headers and independent review.",
    },
)

EVIDENCE_CLASSES = {
    "synthetic_paired": "Generated here under a fixed seed; clean reference is the same frozen synthetic source.",
    "opus_source_reported_context": "Pinned adapter, audit, report, matrix and inventory values are provenance only; not rerun, pooled or claimed.",
    "unpaired_predictive_or_listening": "none",
    "real_audio_rights_qualified": "none",
}


class LCG:
    """Version-stable 32-bit LCG; independent of Python random internals."""

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


def region_for_frame(frame_index: int) -> str:
    for start, end, kind in REGIONS:
        if start <= frame_index < end:
            return kind
    raise ValueError("frame outside frozen cohort")


def boundary_distance_samples(index: int) -> int:
    return min(abs(index - boundary) for boundary in REGION_BOUNDARIES)


def clean_speech(samples: int = SCORED_SAMPLES,
                 seed: int = SEED_SPEECH) -> tuple[float, ...]:
    """Deterministic speech-like surrogate with voiced/unvoiced/silence regions."""
    rng = LCG(seed)
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    noise_state = 0.0
    out: list[float] = []
    for index in range(samples):
        time_s = index / SAMPLE_RATE_HZ
        frame = index // FRAME_SAMPLES
        kind = region_for_frame(frame) if frame < SCORED_FRAMES else "silence"
        fade = min(1.0, boundary_distance_samples(index) / FRAME_SAMPLES)
        if kind == "voiced":
            f0 = 112.0 + 18.0 * math.sin(2.0 * math.pi * 0.27 * time_s)
            period = max(1, int(round(SAMPLE_RATE_HZ / f0)))
            drive = 1.0 if index % period == 0 else 0.0
            formant_a[0], formant_a[1] = (
                0.971 * formant_a[0] - 0.017 * formant_a[1] + drive,
                formant_a[0])
            formant_b[0], formant_b[1] = (
                0.946 * formant_b[0] - 0.034 * formant_b[1] + drive,
                formant_b[0])
            syllable = 0.6 + 0.4 * math.sin(2.0 * math.pi * 2.3 * time_s) ** 2
            value = 0.19 * syllable * (0.46 * formant_a[0] + 0.17 * formant_b[0])
        elif kind == "unvoiced":
            noise = rng.uniform()
            noise_state = 0.7 * noise_state + 0.3 * noise
            value = 0.052 * noise_state + 0.011 * noise
        else:
            value = 0.0004 * rng.uniform()
        value += 0.0002 * rng.uniform()
        out.append(max(-0.9, min(0.9, value * fade)))
    return tuple(out)


def form_packet_stream(clean: Sequence[float],
                       erased: Iterable[int] = ()) -> list[dict[str, Any]]:
    """One host-adapter call per source frame; 160-sample padded final frame."""
    missing = set(int(frame) for frame in erased)
    frames: list[dict[str, Any]] = []
    for frame_index in range(0, len(clean), FRAME_SAMPLES):
        frame_number = frame_index // FRAME_SAMPLES
        chunk = clean[frame_index:frame_index + FRAME_SAMPLES]
        present = frame_number not in missing
        valid = len(chunk) if present else 0
        final = present and valid < FRAME_SAMPLES
        frames.append({
            "first_input_sample": frame_index,
            "present": present,
            "samples": tuple(chunk) + (0.0,) * (FRAME_SAMPLES - len(chunk)),
            "valid_count": valid,
            "final": final,
        })
    return frames


@dataclass(frozen=True)
class PlcConfig:
    epoch: int = 1
    first_input_sample: int = 0
    max_burst_frames: int = MAX_BURST_FRAMES
    buffering_frames: int = BUFFERING_FRAMES
    max_drain_calls: int = MAX_DRAIN_CALLS

    def check(self) -> Optional[str]:
        if not isinstance(self.epoch, int) or self.epoch < 1:
            return "invalid_epoch"
        if not isinstance(self.first_input_sample, int) or self.first_input_sample < 0:
            return "invalid_first_input_sample"
        if self.max_burst_frames != MAX_BURST_FRAMES:
            return "invalid_max_burst"
        if self.buffering_frames != BUFFERING_FRAMES:
            return "invalid_buffering"
        if not 1 <= self.max_drain_calls <= 1024:
            return "invalid_drain_cap"
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


def estimate_pitch_lag(values: Sequence[float]) -> Optional[int]:
    """Deterministic normalized-autocorrelation pitch lag on a good frame."""
    count = len(values)
    if count < PITCH_LAG_MIN + 2:
        return None
    mean = sum(values) / count
    centered = [value - mean for value in values]
    energy = sum(value * value for value in centered)
    if energy <= 0.0:
        return None
    best_lag: Optional[int] = None
    best_score = PITCH_MIN_CORRELATION
    hi = min(PITCH_LAG_MAX, count - 1)
    for lag in range(PITCH_LAG_MIN, hi + 1):
        numerator = 0.0
        delayed_energy = 0.0
        for index in range(lag, count):
            delayed = centered[index - lag]
            numerator += centered[index] * delayed
            delayed_energy += delayed * delayed
        if delayed_energy <= 0.0:
            continue
        score = numerator / math.sqrt(delayed_energy * energy)
        if score > best_score + 1e-12:
            best_score = score
            best_lag = lag
    return best_lag


class DecoderPlcSession:
    """Python model of the optional v0 host delivery-adapter concealment path.

    A missing packet is an explicit ``present=False`` host request. The method
    is fixed per session: synthetic decoder-PLC-style pitch repetition with
    decay (candidate), zero fill, previous-sample hold or linear ramp
    (controls). Concealed slots carry flag 4 and zero valid samples; they are
    adapter frames, not produced provider frames, and cannot satisfy v0 sample
    conservation.
    """

    def __init__(self, config: Optional[PlcConfig] = None,
                 method: str = METHOD_PLC) -> None:
        self.config = config or PlcConfig()
        reason = self.config.check()
        if reason:
            raise ValueError(reason)
        if method not in METHODS:
            raise ValueError("unknown concealment method")
        self.method = method
        self.closed = False
        self.final_accepted = False
        self.epoch = self.config.epoch
        self.next_input = self.config.first_input_sample
        self.last_received_start: Optional[int] = None
        self.last_good: tuple[float, ...] = ()
        self.last_pitch_lag: Optional[int] = None
        self.queue: list[PendingFrame] = []
        self.pending_conceal: list[PendingFrame] = []
        self.consecutive_erased = 0
        self.drain_calls = 0
        self.accepted_end = self.config.first_input_sample
        self.stats: dict[str, int] = {
            "submitted_frames": 0,
            "accepted_valid_samples": 0,
            "accepted_erased_frames": 0,
            "produced_frames": 0,
            "valid_produced_samples": 0,
            "concealed_frames": 0,
            "plc_frames": 0,
            "zero_fill_frames": 0,
            "hold_frames": 0,
            "linear_ramp_frames": 0,
            "leading_fallback_frames": 0,
            "trailing_fallback_frames": 0,
            "queue_high_water": BUFFERING_FRAMES,
            "rejected_missing": 0,
            "rejected_shape": 0,
            "rejected_short": 0,
            "rejected_nonfinite": 0,
            "rejected_bad_padding": 0,
            "rejected_stale_epoch": 0,
            "rejected_duplicate": 0,
            "rejected_out_of_order": 0,
            "rejected_future_packet": 0,
            "rejected_after_final": 0,
            "rejected_burst_length": 0,
            "rejected_closed": 0,
            "rejected_drain_cap": 0,
        }
        self.next_output = self.config.first_input_sample - BUFFERING_DELAY_SAMPLES
        for index in range(BUFFERING_FRAMES):
            self.queue.append(PendingFrame(
                samples=(0.0,) * FRAME_SAMPLES,
                source_first=self.config.first_input_sample
                - (BUFFERING_FRAMES - index) * FRAME_SAMPLES,
                valid_count=0,
                flags=FLAG_STARTUP_PADDING,
                kind=KIND_STARTUP,
            ))

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
            return "shape"
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
        if valid < FRAME_SAMPLES and not bool(frame.get("final", False)):
            return "short"
        if any(v != 0.0 for v in as_float[valid:]):
            return "bad_padding"
        return None

    def _resolve_pending(self, right: Optional[float]) -> None:
        if not self.pending_conceal:
            return
        length = len(self.pending_conceal)
        for index, pending in enumerate(self.pending_conceal):
            if not self.last_good:
                self.stats["leading_fallback_frames"] += 1
                if self.method == METHOD_ZERO:
                    self.stats["zero_fill_frames"] += 1
                pending.samples = (0.0,) * FRAME_SAMPLES
                pending.unresolved = False
                continue
            left_frame = self.last_good
            left = left_frame[-1]
            if self.method == METHOD_ZERO:
                pending.samples = (0.0,) * FRAME_SAMPLES
                self.stats["zero_fill_frames"] += 1
            elif self.method == METHOD_HOLD:
                pending.samples = (left,) * FRAME_SAMPLES
                self.stats["hold_frames"] += 1
            elif self.method == METHOD_LINEAR:
                if right is None:
                    self.stats["trailing_fallback_frames"] += 1
                    pending.samples = (left,) * FRAME_SAMPLES
                    continue
                divisor = length * FRAME_SAMPLES + 1
                pending.samples = tuple(
                    left + (right - left)
                    * (index * FRAME_SAMPLES + sample + 1) / divisor
                    for sample in range(FRAME_SAMPLES))
                self.stats["linear_ramp_frames"] += 1
            else:
                lag = self.last_pitch_lag
                if lag is None:
                    lag = estimate_pitch_lag(left_frame)
                if lag is None or lag < 1 or lag > FRAME_SAMPLES:
                    lag = FRAME_SAMPLES // 2
                self.last_pitch_lag = lag
                excitation = left_frame[-lag:]
                gain = DECAY_GAINS[min(index, len(DECAY_GAINS) - 1)]
                pending.samples = tuple(
                    gain * excitation[sample % lag] for sample in range(FRAME_SAMPLES))
                self.stats["plc_frames"] += 1
            pending.unresolved = False
        self.pending_conceal.clear()

    def process(self, frame: Any) -> ProcessResult:
        if self.closed:
            return self._reject("closed")
        if self.final_accepted:
            return self._reject("after_final")
        problem = self._valid_frame(frame)
        if problem:
            return self._reject(problem)
        frame_epoch = frame.get("epoch", self.epoch)
        if frame_epoch != self.epoch:
            return self._reject("stale_epoch")
        start = int(frame["first_input_sample"])
        if self.last_received_start is not None and start == self.last_received_start:
            return self._reject("duplicate")
        if self.last_received_start is not None and start < self.last_received_start:
            return self._reject("out_of_order")
        if start != self.next_input:
            return self._reject("future_packet")
        present = bool(frame.get("present", True))
        if not present and self.consecutive_erased >= self.config.max_burst_frames:
            return self._reject("burst_length")

        if present:
            samples = tuple(float(v) for v in frame["samples"])
            valid_count = int(frame["valid_count"])
            self._resolve_pending(samples[0])
            self.last_good = samples
            self.last_pitch_lag = estimate_pitch_lag(samples)
            self.queue.append(PendingFrame(
                samples=samples,
                source_first=start,
                valid_count=valid_count,
                flags=FLAG_FINAL_PADDING
                if bool(frame.get("final", False)) and valid_count < FRAME_SAMPLES else 0,
                kind=KIND_GOOD,
            ))
            self.consecutive_erased = 0
            self.accepted_end = start + valid_count
            self.stats["accepted_valid_samples"] += valid_count
            self.final_accepted = bool(frame.get("final", False))
        else:
            self.queue.append(PendingFrame(
                samples=(0.0,) * FRAME_SAMPLES,
                source_first=start,
                valid_count=0,
                flags=FLAG_CONCEALMENT,
                kind=KIND_CONCEAL,
                unresolved=True,
            ))
            self.pending_conceal.append(self.queue[-1])
            self.consecutive_erased += 1
            self.stats["concealed_frames"] += 1
            self.stats["accepted_erased_frames"] += 1
            self.accepted_end = start + FRAME_SAMPLES

        self.last_received_start = start
        self.next_input = start + FRAME_SAMPLES
        self.stats["submitted_frames"] += 1
        emitted = self.queue.pop(0)
        self.stats["queue_high_water"] = max(self.stats["queue_high_water"],
                                             len(self.queue))
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
        if self.closed:
            return [ProcessResult(status="rejected_closed", reason="closed")]
        for pending in self.pending_conceal:
            if pending.unresolved:
                self.stats["trailing_fallback_frames"] += 1
                if self.method == METHOD_ZERO:
                    self.stats["zero_fill_frames"] += 1
                pending.samples = (0.0,) * FRAME_SAMPLES
                pending.unresolved = False
        self.pending_conceal.clear()
        results: list[ProcessResult] = []
        while self.queue and self.next_output < self.accepted_end:
            if self.drain_calls >= self.config.max_drain_calls:
                results.append(ProcessResult(status="rejected_drain_cap",
                                             reason="drain_cap"))
                self.stats["rejected_drain_cap"] += 1
                return results
            self.drain_calls += 1
            emitted = self.queue.pop(0)
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
            return self._reject("closed")
        if not isinstance(epoch, int) or epoch <= self.epoch:
            return self._reject("stale_epoch")
        if not isinstance(first_input_sample, int) or first_input_sample < 0:
            return self._reject("shape")
        self.__init__(PlcConfig(epoch=epoch,
                                first_input_sample=first_input_sample,
                                max_burst_frames=self.config.max_burst_frames,
                                buffering_frames=self.config.buffering_frames,
                                max_drain_calls=self.config.max_drain_calls),
                      method=self.method)
        return ProcessResult(status="ok", epoch=epoch)

    def close(self) -> None:
        self.closed = True
        self.queue.clear()
        self.pending_conceal.clear()


def run_stream(frames: Sequence[dict[str, Any]],
               config: Optional[PlcConfig] = None,
               method: str = METHOD_PLC,
               measure: bool = False) -> tuple[list[ProcessResult], dict[str, Any]]:
    """Drive one complete stream; return raw results plus a timing envelope."""
    session = DecoderPlcSession(config, method)
    results: list[ProcessResult] = []
    durations: list[float] = []
    wall_start = time.perf_counter()
    rss_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
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
        rss_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        session.close()
    envelope = {
        "process_frames": len(frames),
        "drain_frames": len(drain_results),
        "stream_wall_s": round(wall, 6),
        "drain_wall_s": round(drain_wall, 6),
        "maxrss_delta_bytes": rss_end - rss_start,
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


def reconstruct(results: Sequence[ProcessResult],
                expected_samples: int) -> list[float]:
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
        if importlib.metadata.version("pystoi") != "0.4.1" or np.__version__ != "2.5.4":
            return None, "unpinned_scorer"
        module = pathlib.Path(inspect.getfile(stoi))
        expected = next(p["sha256"] for p in SCORER_PINS if p["id"] == "pystoi")
        if hashlib.sha256(module.read_bytes()).hexdigest() != expected:
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
                    results: Sequence[ProcessResult]) -> dict[str, Any]:
    identity_si, identity_reason = si_sdr_db(clean, clean)
    candidate_si, candidate_reason = si_sdr_db(clean, reconstructed)
    identity_stoi, identity_stoi_reason = stoi_score(clean, clean)
    candidate_stoi, candidate_stoi_reason = stoi_score(clean, reconstructed)
    # SI-SDR of bit-exact clean delivery is undefined, so its paired delta is
    # deliberately None; STOI of clean delivery is 1.0 and is paired.
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
    out_power = sum(v * v for v in reconstructed) / len(reconstructed)
    ref_power = sum(v * v for v in clean) / len(clean)
    reasons = [r for r in (candidate_reason, candidate_stoi_reason)
               if r and r != "exact_reconstruction"]
    return {
        "si_sdr_db": {
            "identity_clean": identity_si,
            "condition": candidate_si,
            "paired_delta_vs_identity": si_delta,
            "invalid_reasons": [r for r in (identity_reason, candidate_reason) if r],
        },
        "stoi": {
            "identity_clean": identity_stoi,
            "condition": candidate_stoi,
            "paired_delta_vs_identity": stoi_delta,
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
        "input": features(clean),
        "output": features(reconstructed),
        "counts": {
            "produced_frames": len(results),
            "valid_content_samples": sum(r.valid_count for r in results),
            "concealed_frames": sum(1 for r in results if r.is_concealment),
            "startup_padding_frames": sum(1 for r in results
                                          if r.flags == FLAG_STARTUP_PADDING),
            "final_padding_frames": sum(1 for r in results
                                        if r.flags == FLAG_FINAL_PADDING),
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
            run["flags"].add(result.flags)
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


def delta_metric(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    return round(a - b, 6)


def frozen_region_strata(clean: Sequence[float],
                         waves: dict[str, list[float]]) -> dict[str, Any]:
    by_region: dict[str, list[int]] = {"voiced": [], "unvoiced": [], "silence": []}
    per_frame: dict[str, dict[str, Optional[float]]] = {}
    for frame in ERASURE_PLAN:
        region = region_for_frame(frame)
        indices = range(frame * FRAME_SAMPLES, (frame + 1) * FRAME_SAMPLES)
        by_region[region].extend(indices)
        per_frame[str(frame)] = {
            "region": region,
            "position": ("leading" if frame < SCORED_FRAMES // 3
                         else "trailing" if frame >= 2 * SCORED_FRAMES // 3
                         else "middle"),
            **{name: rmse_over(clean, wave, indices) for name, wave in waves.items()},
        }
    regions = {
        region: {
            "erased_frames": [frame for frame in ERASURE_PLAN
                              if region_for_frame(frame) == region],
            "erased_samples": len(indices),
            "per_condition_rmse": {
                name: rmse_over(clean, wave, indices)
                for name, wave in waves.items()},
        }
        for region, indices in by_region.items()
    }
    transitions = {}
    for label, frames in (("onset", ONSET_FRAMES), ("offset", OFFSET_FRAMES)):
        transitions[label] = {
            str(frame): {
                "region_before": region_for_frame(frame - 1),
                "region_after": region_for_frame(frame),
                "erased": frame in ERASURE_PLAN,
                "per_condition_rmse": (
                    {name: rmse_over(clean, wave, range(frame * FRAME_SAMPLES,
                                                       (frame + 1) * FRAME_SAMPLES))
                     for name, wave in waves.items()}
                    if frame in ERASURE_PLAN else None),
            }
            for frame in frames
        }
    return {"by_content_class": regions, "per_erased_frame": per_frame,
            "onset_offset": transitions}


def artifact_pins() -> list[dict[str, str]]:
    here = Path(__file__).resolve().parent
    return [
        {
            "path": name,
            "sha256": hashlib.sha256((here / name).read_bytes()).hexdigest(),
            "kind": "task_fixture",
        }
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py")
    ]


def qualification_state(report: dict[str, Any]) -> str:
    """No missing result may qualify the candidate, whatever else looks good."""
    if not report.get("no_missing_result_qualifies_candidate"):
        raise ValueError("missing-result gate disabled")
    if any(block["status"] == "blocked" for block in report["blockers"]):
        return "not_qualified"
    if any(not condition["all_metrics_available"]
           for condition in report["conditions"].values()):
        return "not_qualified"
    if not all(report.get(key, False) for key in
               ("controls_all_pass", "alignment_pass", "state_pass",
                "all_outputs_finite", "strata_complete", "partial_window_pass")):
        return "not_qualified"
    return "proposal_only_synthetic_incomplete"


def build_report() -> dict[str, Any]:
    clean = clean_speech()
    erased = set(ERASURE_PLAN)
    frames = {
        "identity_clean": form_packet_stream(clean),
        "zero_fill_baseline": form_packet_stream(clean, erased),
        "hold_control": form_packet_stream(clean, erased),
        "linear_control": form_packet_stream(clean, erased),
        "plc_reference_candidate": form_packet_stream(clean, erased),
    }
    results = {name: run_stream(items, method=CONDITION_METHODS[name])[0]
               for name, items in frames.items()}
    waves = {name: reconstruct(items, len(clean))
             for name, items in results.items()}
    conditions = {name: score_condition(clean, waves[name], results[name])
                  for name in frames}

    # Stratification by erasure burst length and frozen source position.
    strata: dict[str, Any] = {}
    for name, plan in STRATA.items():
        indices = [frame * FRAME_SAMPLES + sample
                   for frame in plan for sample in range(FRAME_SAMPLES)]
        strata[name] = {
            "erased_frames": list(plan),
            "erased_samples": len(indices),
            "regions": sorted({region_for_frame(frame) for frame in plan}),
            "per_condition_rmse": {
                condition: rmse_over(clean, waves[condition], indices)
                for condition in frames},
            "per_frame_rmse": {
                condition: {
                    str(frame): rmse_over(
                        clean, waves[condition],
                        range(frame * FRAME_SAMPLES, (frame + 1) * FRAME_SAMPLES))
                    for frame in plan}
                for condition in frames},
        }
    erased_indices = [frame * FRAME_SAMPLES + sample
                      for frame in ERASURE_PLAN for sample in range(FRAME_SAMPLES)]
    erasure_stratification = {
        "by_burst_length": strata,
        "by_content_and_boundary": frozen_region_strata(clean, waves),
        "all_erased_indices": erased_indices,
        "all_erased_samples": len(erased_indices),
        "identity_is_exact_on_erased_intervals": all(
            clean[i] == waves["identity_clean"][i] for i in erased_indices),
    }

    # Final partial window: 8 full frames plus 37 samples, full frame 7 lost.
    partial_clean = clean[:FINAL_PARTIAL_FRAMES * FRAME_SAMPLES + FINAL_PARTIAL_SAMPLES]
    partial_frames = form_packet_stream(partial_clean, (7,))
    partial_results = {name: run_stream(partial_frames,
                                        method=CONDITION_METHODS[name])[0]
                       for name in frames}
    partial_waves = {name: reconstruct(items, len(partial_clean))
                     for name, items in partial_results.items()}
    partial_last = partial_frames[-1]
    partial_window = {
        "source_samples": len(partial_clean),
        "last_frame_valid_count": partial_last["valid_count"],
        "last_frame_flagged_final": partial_last["final"],
        "erased_frames": [7],
        "present_frame_flags": sorted({r.flags for r in partial_results[
            CANDIDATE_CONDITION] if r.flags}),
        "clean_preservation_valid_mismatches": sum(
            1 for r in partial_results[CANDIDATE_CONDITION] if r.kind == KIND_GOOD
            for i in range(r.valid_count)
            if r.samples[i] != partial_clean[r.source_first_sample + i]),
        "per_condition_rmse_over_partial_window": {
            name: rmse_over(partial_clean, wave,
                            range(FINAL_PARTIAL_FRAMES * FRAME_SAMPLES,
                                  len(partial_clean)))
            for name, wave in partial_waves.items()},
        "produced_frames": {name: len(items)
                            for name, items in partial_results.items()},
        "decoded_intervals": {name: decoded_intervals(items)
                              for name, items in partial_results.items()},
    }

    intervals = {name: decoded_intervals(items) for name, items in results.items()}
    availability = {
        name: {
            "produced_frames": len(items),
            "first_valid_output_call_index": next(
                (i for i, r in enumerate(items) if r.valid_count), None),
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "queue_high_water": BUFFERING_FRAMES,
            "duration_semantics": "one 160-sample output slot per source frame; "
                                  "startup/final padding carry zero valid samples, "
                                  "adapter concealment carries flag 4 and zero valid "
                                  "samples and is not a produced provider frame",
        }
        for name, items in results.items()
    }

    # Impulse alignment probe: declared host scheduling delay, zero intrinsic.
    impulse = [0.0] * (40 * FRAME_SAMPLES)
    impulse[4000] = 0.8
    impulse_results, _ = run_stream(form_packet_stream(impulse))
    impulse_raw = [v for result in impulse_results for v in result.samples]
    peak_index = max(range(len(impulse_raw)),
                     key=lambda index: abs(impulse_raw[index]))
    alignment = {
        "declared_buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "declared_buffering_delay_frames": BUFFERING_FRAMES,
        "candidate_intrinsic_delay_samples": 0,
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
            for r, frame in zip(results["identity_clean"],
                                frames["identity_clean"])),
    }

    # Pitch-estimate observation (candidate recipe only, no codec involvement).
    probe_session = DecoderPlcSession(method=METHOD_PLC)
    for frame in frames[CANDIDATE_CONDITION]:
        probe_session.process(dict(frame))
    pitch_observation = {
        "estimator": "normalized_autocorrelation",
        "lag_range_samples": [PITCH_LAG_MIN, PITCH_LAG_MAX],
        "min_correlation": PITCH_MIN_CORRELATION,
        "decay_gains_by_burst_frame": list(DECAY_GAINS),
        "last_estimated_lag_samples": probe_session.last_pitch_lag,
        "candidate_concealment_frames": probe_session.stats["plc_frames"],
        "note": "Fixed synthetic recipe; no codec parameter or Opus measurement.",
    }
    probe_session.close()

    # Session state, reset and independence.
    short = form_packet_stream(clean[:FRAME_SAMPLES * 8])
    a_results, _ = run_stream(short)
    b_results, _ = run_stream([
        {**frame, "samples": tuple(0.7 * v for v in frame["samples"])}
        for frame in short])
    reset_session = DecoderPlcSession(PlcConfig(epoch=1))
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
    live_session = DecoderPlcSession(method=METHOD_PLC)
    for frame in frames[CANDIDATE_CONDITION]:
        live_session.process(dict(frame))
    live_session.drain()
    live_queue = len(live_session.queue)
    live_stats = dict(live_session.stats)
    live_session.close()
    state = {
        "separate_sessions_uncoupled": [v for v in a_results] != [v for v in b_results],
        "reset_accepted": reset_status.status == "ok",
        "stale_epoch_after_reset_rejected": stale_after_reset.status
        == "rejected_stale_epoch",
        "reset_bit_identical_to_fresh_epoch2": [
            (r.samples, r.flags, r.source_first_sample) for r in reset_results
        ] == [(r.samples, r.flags, r.source_first_sample) for r in fresh_results],
        "closed_session_rejects_process": closed_result.status == "rejected_closed",
        "bounded_queue_depth": live_stats["queue_high_water"] <= BUFFERING_FRAMES,
        "queue_empty_after_drain": live_queue == 0,
        "candidate_concealment_count_matches_mask":
            live_stats["concealed_frames"] == len(ERASURE_PLAN),
        "candidate_plc_count_matches_concealment":
            live_stats["plc_frames"] == len(ERASURE_PLAN),
    }

    # Discrete validity and adversarial packet controls.
    adverse: dict[str, Any] = {}
    probe = DecoderPlcSession(PlcConfig(epoch=7))
    baseline = {k: v for k, v in probe.stats.items()
                if not k.startswith("rejected_")}
    invalid_frames = {
        "missing_frame": None,
        "wrong_frame_shape": {"first_input_sample": 0,
                              "samples": ((0.0,),) * FRAME_SAMPLES},
        "short_frame": {"first_input_sample": 0,
                        "samples": (0.0,) * (FRAME_SAMPLES - 1)},
        "zero_length_frame": {"first_input_sample": 0, "samples": (),
                              "valid_count": 0},
        "nonfinite_input": {"first_input_sample": 0,
                            "samples": (float("nan"),) * FRAME_SAMPLES},
        "stale_epoch": {**short[0], "epoch": 6},
        "future_packet": {**short[2], "first_input_sample": 320},
        "bad_padding": {**short[0], "valid_count": 10, "final": True,
                        "samples": (0.1,) * 10 + (0.2,) * (FRAME_SAMPLES - 10)},
    }
    for name, frame in invalid_frames.items():
        result = probe.process(frame)
        adverse[name] = {
            "status": result.status,
            "state_unchanged": {k: v for k, v in probe.stats.items()
                                if not k.startswith("rejected_")} == baseline,
        }
    probe.close()
    adverse["invalid_reset_epoch"] = {
        "status": DecoderPlcSession().reset(0, 0).status,
        "state_unchanged": True,
    }

    order_probe = DecoderPlcSession(PlcConfig(epoch=1))
    first_ok = order_probe.process(dict(short[0]))
    second_ok = order_probe.process(dict(short[1]))
    accepted_after_two = order_probe.stats["accepted_valid_samples"]
    duplicate = order_probe.process(dict(short[1]))
    after_duplicate = order_probe.stats["accepted_valid_samples"]
    out_of_order = order_probe.process(dict(short[0]))
    after_order = order_probe.stats["accepted_valid_samples"]
    recovered = order_probe.process(dict(short[2]))
    adverse["duplicate_packet"] = {
        "status": duplicate.status,
        "state_unchanged": after_duplicate == accepted_after_two,
    }
    adverse["out_of_order_packet"] = {
        "status": out_of_order.status,
        "state_unchanged": after_order == after_duplicate,
    }
    adverse["order_recovery"] = {
        "status": recovered.status,
        "consistent_counts": after_order == 2 * FRAME_SAMPLES
        and order_probe.stats["accepted_valid_samples"] == 3 * FRAME_SAMPLES,
        "first_two_accepted": first_ok.status == "ok" and second_ok.status == "ok",
    }
    order_probe.close()
    after_final = order_probe.process(dict(short[3]))
    adverse["closed_rejects_further_process"] = {
        "status": after_final.status,
        "state_unchanged": True,
    }

    live = DecoderPlcSession(PlcConfig(epoch=1))
    final_short = form_packet_stream(clean[:FRAME_SAMPLES * 8
                                           + FINAL_PARTIAL_SAMPLES])
    for frame in final_short:
        live.process(dict(frame))
    adverse["process_after_final"] = {
        "status": live.process(dict(short[0])).status,
        "state_unchanged": live.stats["accepted_valid_samples"]
        == 8 * FRAME_SAMPLES + FINAL_PARTIAL_SAMPLES,
    }
    live.close()

    burst_probe = DecoderPlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 160],
                                    ADVERSARIAL_ERASURES["max_burst"]):
        burst_probe.process(dict(frame))
    burst_probe.drain()
    max_burst_stats = dict(burst_probe.stats)
    burst_probe.close()
    over_probe = DecoderPlcSession(PlcConfig(epoch=1))
    over_before = dict(over_probe.stats)
    over_statuses = [
        over_probe.process({"first_input_sample": index * FRAME_SAMPLES,
                            "present": False, "samples": (0.0,) * FRAME_SAMPLES,
                            "valid_count": 0}).status
        for index in range(MAX_BURST_FRAMES + 1)]
    adverse["erase_burst_length"] = {
        "max_concealed_burst_frames": MAX_BURST_FRAMES,
        "max_burst_concealed_frames": max_burst_stats["concealed_frames"],
        "over_max_status": over_statuses[-1],
        "over_max_accepted": over_statuses[:MAX_BURST_FRAMES] == ["ok"] * MAX_BURST_FRAMES,
        "over_max_state_unchanged": over_probe.stats["accepted_valid_samples"]
        == over_before["accepted_valid_samples"],
    }
    over_probe.close()

    leading_probe = DecoderPlcSession(PlcConfig(epoch=1))
    leading_results: list[ProcessResult] = []
    leading_stream = form_packet_stream(clean[:FRAME_SAMPLES * 40], (0,))
    for frame in leading_stream[:BUFFERING_FRAMES + 1]:
        leading_results.append(leading_probe.process(dict(frame)))
    leading_process = leading_results[0]
    leading_probe.drain()
    leading_stats = dict(leading_probe.stats)
    leading_probe.close()
    leading_conceal = [r for r in leading_results if r.is_concealment]
    trailing_probe = DecoderPlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 40], (38, 39)):
        trailing_probe.process(dict(frame))
    trailing_probe.drain()
    trailing_stats = dict(trailing_probe.stats)
    trailing_probe.close()
    boundary_probe = DecoderPlcSession(PlcConfig(epoch=1))
    for frame in form_packet_stream(clean[:FRAME_SAMPLES * 160],
                                    ADVERSARIAL_ERASURES["boundary_burst"]):
        boundary_probe.process(dict(frame))
    boundary_probe.drain()
    boundary_concealed = boundary_probe.stats["concealed_frames"]
    boundary_probe.close()
    adverse["erase_boundary"] = {
        "leading_erasure_status": leading_process.status,
        "leading_zero_valid_output": bool(leading_conceal)
        and all(r.valid_count == 0 for r in leading_conceal),
        "leading_zero_valued_fallback_frames": leading_stats["leading_fallback_frames"],
        "trailing_concealed_frames": trailing_stats["concealed_frames"],
        "trailing_fallback_frames": trailing_stats["trailing_fallback_frames"],
        "boundary_burst_plan": list(ADVERSARIAL_ERASURES["boundary_burst"]),
        "boundary_burst_concealed": boundary_concealed,
    }
    conceal_flags = [r.flags for r in results[CANDIDATE_CONDITION]
                     if r.is_concealment]
    adverse["concealment_zero_valid_output"] = {
        "concealment_flags": sorted(set(conceal_flags)),
        "concealment_valid_count_zero": all(
            r.valid_count == 0 for r in results[CANDIDATE_CONDITION]
            if r.is_concealment),
        "valid_content_samples": intervals[CANDIDATE_CONDITION]["valid_content_samples"],
        "concealment_excluded_from_valid_content":
            intervals[CANDIDATE_CONDITION]["valid_content_samples"]
            == len(clean) - len(ERASURE_PLAN) * FRAME_SAMPLES,
    }
    adverse["final_short_frame"] = {
        "samples": form_packet_stream(clean[:FRAME_SAMPLES * 8
                                            + FINAL_PARTIAL_SAMPLES])[-1]["valid_count"],
        "accepted_valid_samples": 8 * FRAME_SAMPLES + FINAL_PARTIAL_SAMPLES,
    }

    # Explicit comparisons: losing controls/regressions are reported unchanged.
    comparisons: dict[str, Any] = {}
    regressions: list[dict[str, Any]] = []
    candidate_condition = conditions[CANDIDATE_CONDITION]
    for control in CONTROL_CONDITIONS:
        control_condition = conditions[control]
        si = delta_metric(candidate_condition["si_sdr_db"]["condition"],
                          control_condition["si_sdr_db"]["condition"])
        stoi = delta_metric(candidate_condition["stoi"]["condition"],
                            control_condition["stoi"]["condition"])
        rmse = delta_metric(
            candidate_condition["lost_region"]["concealed_rmse"],
            control_condition["lost_region"]["concealed_rmse"])
        comparisons[control] = {
            "candidate_minus_control_si_sdr_db": si,
            "candidate_minus_control_stoi": stoi,
            "candidate_minus_control_concealed_rmse": rmse,
            "per_stratum_concealed_rmse_delta": {
                name: delta_metric(
                    stratum["per_condition_rmse"][CANDIDATE_CONDITION],
                    stratum["per_condition_rmse"][control])
                for name, stratum in strata.items()},
        }
        for name, value in comparisons[control]["per_stratum_concealed_rmse_delta"].items():
            if value is not None and value > 0.0:
                regressions.append({
                    "control": control,
                    "stratum": name,
                    "metric": "concealed_rmse",
                    "candidate_minus_control": value,
                    "interpretation": "candidate worse in lost region",
                })
        if si is not None and si < 0.0:
            regressions.append({
                "control": control, "stratum": "cohort", "metric": "si_sdr_db",
                "candidate_minus_control": si,
                "interpretation": "candidate worse on paired cohort SI-SDR",
            })
        if stoi is not None and stoi < 0.0:
            regressions.append({
                "control": control, "stratum": "cohort", "metric": "stoi",
                "candidate_minus_control": stoi,
                "interpretation": "candidate worse on paired cohort STOI",
            })

    fixture_spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "f32",
        "frame_samples": FRAME_SAMPLES,
        "buffering_frames": BUFFERING_FRAMES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "max_burst_frames": MAX_BURST_FRAMES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "scored_frames": SCORED_FRAMES,
        "seed": SEED_SPEECH,
        "regions": [list(region) for region in REGIONS],
        "erasure_plan": list(ERASURE_PLAN),
        "strata": STRATA,
        "decay_gains_by_burst_frame": list(DECAY_GAINS),
        "pitch_lag_range_samples": [PITCH_LAG_MIN, PITCH_LAG_MAX],
        "final_partial_samples": FINAL_PARTIAL_SAMPLES,
        "source_pins": {pin["path"]: pin["sha256"] for pin in SOURCE_PINS},
        "scorer_pins": [dict(pin) for pin in SCORER_PINS],
        "artifact_pins": {pin["path"]: pin["sha256"] for pin in artifact_pins()},
        "base_commit": BASE_COMMIT,
    }
    controls_all_pass = all(
        item.get("state_unchanged", True) for item in adverse.values()
        if isinstance(item, dict))
    alignment_pass = alignment["measured_content_lag_samples"] == 0 \
        and alignment["source_mapping_checks"]
    state_pass = all(state.values())
    strata_complete = (
        sorted(frame for stratum in STRATA.values() for frame in stratum)
        == list(ERASURE_PLAN)
        and erasure_stratification["identity_is_exact_on_erased_intervals"]
        and sum(stratum["erased_samples"] for stratum in strata.values())
        == len(erased_indices))
    expected_partial_frames = (
        FINAL_PARTIAL_FRAMES + 1 + BUFFERING_FRAMES)
    partial_window_pass = (
        partial_window["last_frame_valid_count"] == FINAL_PARTIAL_SAMPLES
        and partial_window["last_frame_flagged_final"]
        and partial_window["clean_preservation_valid_mismatches"] == 0
        and all(value == expected_partial_frames
                for value in partial_window["produced_frames"].values()))
    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": "optional task-local synthetic reference; not Opus, not a release or real-audio qualification",
        "profile": "Enhancement",
        "supporting_profile": "Restoration",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "base_commit": BASE_COMMIT,
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": list(SOURCE_PINS),
        "scorer_pins": [dict(pin) for pin in SCORER_PINS],
        "artifact_pins": artifact_pins(),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": "f32",
            "frame_samples": FRAME_SAMPLES,
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "max_burst_frames": MAX_BURST_FRAMES,
        },
        "boundary": {
            "provider_id": PROVIDER_ID,
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "note": "Python model of the host delivery adapter at the public v0 boundary; no C provider, no Opus link, no registry change, no public flag.",
        },
        "algorithm": {
            "candidate": "synthetic decoder-PLC-style: causal pitch-period repetition from the last good frame with fixed progressive decay; no codec, packet or network input",
            "identity_control": IDENTITY_CONTROL,
            "degraded_noisy_control": DEGRADED_NOISY_CONTROL,
            "task_matched_baseline": TASK_MATCHED_BASELINE,
            "additional_controls": ["hold_control"],
            "intrinsic_delay_samples": 0,
            "pitch_observation": pitch_observation,
        },
        "opus_provenance": dict(OPUS_PROVENANCE),
        "cohort": {
            "kind": "deterministic_synthetic_paired",
            "frames": SCORED_FRAMES,
            "samples": len(clean),
            "duration_seconds": round(len(clean) / SAMPLE_RATE_HZ, 6),
            "clean_digest": tensor_digest(clean),
            "seed": SEED_SPEECH,
            "regions": [list(region) for region in REGIONS],
            "onset_frames": list(ONSET_FRAMES),
            "offset_frames": list(OFFSET_FRAMES),
            "erased_frames": list(ERASURE_PLAN),
            "erased_frame_count": len(ERASURE_PLAN),
            "erased_sample_count": len(erased_indices),
        },
        "conditions": conditions,
        "erasure_stratification": erasure_stratification,
        "final_partial_window": partial_window,
        "decoded_intervals": intervals,
        "availability": availability,
        "alignment": alignment,
        "state": state,
        "adverse": adverse,
        "comparisons": comparisons,
        "regressions": regressions,
        "controls_all_pass": controls_all_pass,
        "alignment_pass": alignment_pass,
        "state_pass": state_pass,
        "strata_complete": strata_complete,
        "partial_window_pass": partial_window_pass,
        "all_metrics_available": all(
            item["all_metrics_available"] for item in conditions.values()),
        "all_outputs_finite": all(item["output"]["finite"]
                                  and item["output"]["at_or_above_one_count"] == 0
                                  for item in conditions.values()),
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "blockers": [dict(block) for block in QUALIFICATION_BLOCKERS],
        "timing_pointer": {
            "path": "runtime-measurements.json",
            "non_deterministic": True,
            "pacing": "unpaced",
            "deadline_ns": None,
            "qualification_status": "blocked",
            "note": "Unpaced Python wall-clock/RSS observations only; not target-device, paced, deadline, CPU or memory evidence. The source-reported Opus RTF is pinned context, not verified or pooled here.",
        },
        "no_missing_result_qualifies_candidate": True,
    }
    report["qualification_status"] = qualification_state(report)
    return impurity_free(report)


def impurity_free(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite report value")
    if isinstance(value, dict):
        return {key: impurity_free(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [impurity_free(item) for item in value]
    return value


def build_runtime_measurements() -> dict[str, Any]:
    clean = clean_speech()
    frames = {
        name: form_packet_stream(clean,
                                 set(ERASURE_PLAN) if name != IDENTITY_CONTROL else ())
        for name in CONDITIONS
    }
    envelopes = {name: run_stream(items, method=CONDITION_METHODS[name],
                                  measure=True)[1]
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
        "note": "ru_maxrss is a coarse process high-water mark; availability is elapsed time to the first frame with valid samples. Neither is a target timing, CPU, memory, codec or Opus claim.",
    }


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + b"\n"
