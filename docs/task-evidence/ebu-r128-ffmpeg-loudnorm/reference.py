# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic EBU R 128 / FFmpeg loudnorm-target reference fixture.

Task-local, optional, unregistered evidence for the audio-sdk public v0
boundary. No FFmpeg executable, GPL component, downloaded asset, licensed
corpus, device, listening test or network result is used or shipped here. A
local external-tool invocation was attempted first; the exact absence and the
historical FFmpeg 7.1 / GPL-2.0-or-later provenance are recorded in
``TOOL_PROVENANCE`` and in ``tool-provenance.json``.

The algorithm below is a *minimal synthetic loudness-target reference*, not a
BS.1770/EBU Mode meter and not a wrapper around FFmpeg. Its formulas are fully
explicit: a simplified two-biquad K-weighting at 16 kHz, 400 ms/100 ms gated
integrated loudness, a 4x Catmull-Rom true-peak estimate, and one static gain
solved from ``I=-23`` LUFS with a ``TP=-1`` dBTP ceiling. The LRA setting is
recorded but not enforced. Only the final static gain is applied at the public
boundary (16 kHz mono float32, 160 samples per call); analysis is an offline
control-plane pass over the whole synthetic stream.

Status is ``proposal_only_synthetic_incomplete`` / ``not_qualified``. No
provider is compiled, registered, enabled or changed, and no missing result is
allowed to qualify the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

CONTRACT_ID = "audio-sdk/ebu-r128-loudnorm/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/ebu-r128-ffmpeg-loudnorm/report/0.1"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
PROVIDER_ID = "dsp.ebu-r128-loudnorm-ref.v0"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
SAMPLE_FORMAT = "f32"

TARGET_LUFS = -23.0
TARGET_LRA_LU = 7.0
TARGET_TP_DBTP = -1.0
TARGET_TP_LINEAR = 10.0 ** (TARGET_TP_DBTP / 20.0)
TOLERANCE_LU = 0.2
MAX_GAIN = 64.0

BLOCK_SAMPLES = 6400          # 400 ms at 16 kHz
HOP_SAMPLES = 1600            # 100 ms at 16 kHz
ABS_GATE_LUFS = -70.0
REL_GATE_LU = 10.0
OVERSAMPLE = 4

SEED = 20261124
SCORED_FRAMES = 250
SCORED_SAMPLES = SCORED_FRAMES * FRAME_SAMPLES
FINAL_PARTIAL_SAMPLES = 37

FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2
FLAG_CONCEALMENT = 4

K_SHELF_HZ = 1681.97
K_SHELF_GAIN_DB = 4.0
K_HIGHPASS_HZ = 38.0
K_HIGHPASS_Q = 0.5

FREQUENCIES_HZ = (100.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 6000.0)
TONE_SAMPLES = SAMPLE_RATE_HZ
STEP_SEGMENTS = ((0.03, 0.03), (0.03, -0.06), (0.03, 0.015),
                 (0.03, -0.12), (0.03, 0.045), (0.03, -0.02))
SPEECH_REGIONS = (
    (0, 40, "voiced"), (40, 60, "unvoiced"), (60, 70, "silence"),
    (70, 110, "voiced"), (110, 130, "unvoiced"), (130, 140, "silence"),
    (140, 190, "voiced"), (190, 215, "unvoiced"), (215, 230, "silence"),
    (230, 250, "voiced"),
)

SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "root": "source",
        "sha256": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
        "summary": "Row 73 pins the partially evaluated EBU R 128 / FFmpeg 7.1 loudnorm screen and its blockers.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-r128-eval/REPORT.md",
        "root": "source",
        "sha256": "b6afa2b82f888882dd3c7d24d262848aa6218b65d5fb490d88cb007d17b23ef5",
        "summary": "Historical same-implementation two-pass loudnorm protocol, exact binary digest and GPL-2.0-or-later classification.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-r128-eval/results.json",
        "root": "source",
        "sha256": "9bdfef51364931b351d07fb425c7f08f1845b3e1168095369964da746ddfb783",
        "summary": "Historical per-item R128 results and environment record; not rerun or pooled here.",
    },
    {
        "path": "research/voice-enhancement-20261101/agent-r128-independent-audit/REPORT.md",
        "root": "source",
        "sha256": "12616c2eb6b394484f359c910a84dac7b327558b0dbae381906b8b8dc3ad6896",
        "summary": "No independent BS.1770/EBU Mode meter was available; R128 self-measurement is not standards conformance.",
    },
    {
        "path": "research/noise_suppression_assets_20261027.json",
        "root": "source",
        "sha256": "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
        "summary": "Local asset ledger entry: FFmpeg 7.1 imageio-ffmpeg binary, exact digest and GPL-2.0-or-later build/report.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 format, frame geometry, source mapping, flags and reset/validity rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "DSP profile: sweeps, steps, impulses, silence, clean speech/control, gain, response, headroom, delay, numerics and state.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by the Python frame adapter.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary: epoch, reset, close and source mapping semantics.",
    },
)

TOOL_PROVENANCE: dict[str, Any] = {
    "schema_id": SCHEMA_ID + "/tool-provenance",
    "base_commit": BASE_COMMIT,
    "status": "blocked",
    "external_tool_invocations": [
        {
            "argv": ["ffmpeg", "-version"],
            "cwd": "/Users/htsakanyan/workspace/audio/audioml",
            "exception": "FileNotFoundError",
            "message": "[Errno 2] No such file or directory: 'ffmpeg'",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "note": "First external developer-tool invocation; no local executable resolution.",
        },
        {
            "argv": ["which", "-a", "ffmpeg"],
            "cwd": "/Users/htsakanyan/workspace/audio/audioml",
            "returncode": 1,
            "stdout": "",
            "stderr": "",
            "note": "No ffmpeg path on PATH.",
        },
        {
            "argv": [
                "/Users/htsakanyan/workspace/audio/audioml/data/envs/ffmpeg/"
                "lib/python3.11/site-packages/imageio_ffmpeg/binaries/"
                "ffmpeg-macos-aarch64-v7.1", "-version",
            ],
            "cwd": "/Users/htsakanyan/workspace/audio/audioml",
            "exception": "FileNotFoundError",
            "message": "[Errno 2] No such file or directory: "
                       "'/Users/htsakanyan/workspace/audio/audioml/data/envs/"
                       "ffmpeg/lib/python3.11/site-packages/imageio_ffmpeg/"
                       "binaries/ffmpeg-macos-aarch64-v7.1'",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "note": "The historical bundled binary path is absent; no exact local build/configuration output could be captured.",
        },
        {
            "argv": ["which", "-a", "ebur128", "bs1770gain"],
            "cwd": "/Users/htsakanyan/workspace/audio/audioml",
            "returncode": 2,
            "stdout": "",
            "stderr": "",
            "note": "No independent local BS.1770/EBU Mode meter invocation was possible.",
        },
    ],
    "historical_ffmpeg_provenance": {
        "source": "research/voice-enhancement-20261101/agent-r128-eval/REPORT.md; "
                  "research/voice-enhancement-20261101/agent-r128-eval/results.json; "
                  "research/noise_suppression_assets_20261027.json",
        "path": "data/envs/ffmpeg/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1",
        "version": "7.1",
        "binary_sha256": "6d175a4743ca50256e89a8cdd731100f9cee33bd79aeea46894d209410dc6617",
        "binary_bytes": 49368728,
        "license": "GPL-2.0-or-later",
        "dependency_configuration": "GPL-2.0-or-later reported by local asset ledger; exact configure flags not recorded in pinned source",
        "build_configuration": None,
        "configuration_available_locally": False,
        "note": "Historical provenance only. The exact build string and configure flags cannot be recovered from the absent binary; they are not invented here.",
    },
    "synthetic_loudnorm_invocation": {
        "status": "not_run",
        "reason": "No local ffmpeg executable exists in this task environment; no two-pass invocation or generated-WAV measurement was performed.",
    },
    "binary_handling": {
        "vendored": False,
        "downloaded": False,
        "shipped": False,
        "wrapped": False,
        "note": "No FFmpeg binary, GPL component or WAV generated by FFmpeg is present in this evidence directory.",
    },
}

QUALIFICATION_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "local_external_tool",
        "status": "blocked",
        "reason": "ffmpeg is absent; no exact version/configuration output, no synthetic two-pass loudnorm invocation and no GPL dependency build string were captured.",
        "reopen": "Invoke an approved local FFmpeg build, capture its exact version/configuration and hash, review its GPL dependency configuration separately, and only then run a synthetic two-pass loudnorm probe under an approved license.",
    },
    {
        "id": "independent_ebu_meter",
        "status": "blocked",
        "reason": "No independent BS.1770/EBU Mode loudness or true-peak meter is available; the fixture's estimator is not a standards meter.",
        "reopen": "Pin and independently review a licensed standards meter, then remeasure frozen synthetic vectors with an explicit agreement protocol.",
    },
    {
        "id": "ebu_test_set_and_programme_cohort",
        "status": "blocked",
        "reason": "The EBU loudness test set, complete programmes and rights-qualified real speech are not present in this task-local fixture.",
        "reopen": "Freeze an approved test set and complete-programme cohort with rights, target conditions and independent scoring.",
    },
    {
        "id": "dynamic_mode_and_lra_enforcement",
        "status": "blocked",
        "reason": "Only one static gain is implemented; dynamic loudnorm mode and the LRA=7 LU target are recorded but not enforced.",
        "reopen": "Implement and independently test a deterministic dynamic-mode reference with explicit LRA and true-peak interaction before making any matching claim.",
    },
    {
        "id": "live_provider_intake",
        "status": "blocked",
        "reason": "Offline whole-stream analysis cannot be a causal v0 process provider; the conceptual ID is unregistered, OFF by default and has empty descriptor settings.",
        "reopen": "Define, review and opt into an analyzer/host protocol with explicit lookahead, delay and descriptor settings; no automatic registration or default.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "No paced target-device deadline, CPU or memory evidence exists for any implementation of this task.",
        "reopen": "Measure the exact approved runtime on the target under pacing, load and bounded resource budgets.",
    },
)

EVIDENCE_CLASSES = {
    "synthetic_reference": "Generated here from fixed seeds and explicit formulas; no real audio or external tool output.",
    "historical_source_reported": "FFmpeg 7.1 two-pass loudnorm and same-filter results in pinned research are context only, not rerun or pooled.",
    "independent_standard_measurement": "none",
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


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + b"\n"


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def r6(value: Optional[float]) -> Optional[float]:
    if value is None or not math.isfinite(value):
        return None
    return round(value, 6)


def dbfs(value: Optional[float]) -> Optional[float]:
    if value is None or value <= 0.0 or not math.isfinite(value):
        return None
    return r6(20.0 * math.log10(value))


def _high_shelf_coefficients() -> tuple[float, float, float, float, float]:
    gain_linear = 10.0 ** (K_SHELF_GAIN_DB / 40.0)
    omega = 2.0 * math.pi * K_SHELF_HZ / SAMPLE_RATE_HZ
    alpha = math.sin(omega) * math.sqrt(2.0) / 2.0
    cosine = math.cos(omega)
    root = 2.0 * math.sqrt(gain_linear) * alpha
    b0 = gain_linear * ((gain_linear + 1.0)
                        + (gain_linear - 1.0) * cosine + root)
    b1 = -2.0 * gain_linear * ((gain_linear - 1.0)
                               + (gain_linear + 1.0) * cosine)
    b2 = gain_linear * ((gain_linear + 1.0)
                        + (gain_linear - 1.0) * cosine - root)
    a0 = (gain_linear + 1.0) - (gain_linear - 1.0) * cosine + root
    a1 = 2.0 * ((gain_linear - 1.0) - (gain_linear + 1.0) * cosine)
    a2 = (gain_linear + 1.0) - (gain_linear - 1.0) * cosine - root
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def _highpass_coefficients() -> tuple[float, float, float, float, float]:
    omega = 2.0 * math.pi * K_HIGHPASS_HZ / SAMPLE_RATE_HZ
    alpha = math.sin(omega) / (2.0 * K_HIGHPASS_Q)
    cosine = math.cos(omega)
    b0 = (1.0 + cosine) / 2.0
    b1 = -(1.0 + cosine)
    b2 = b0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosine
    a2 = 1.0 - alpha
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


K_SHELF = _high_shelf_coefficients()
K_HIGHPASS = _highpass_coefficients()


def _biquad(coefficients: tuple[float, float, float, float, float],
            values: Sequence[float]) -> list[float]:
    b0, b1, b2, a1, a2 = coefficients
    z1 = 0.0
    z2 = 0.0
    out: list[float] = []
    for value in values:
        y = b0 * value + z1
        z1 = b1 * value - a1 * y + z2
        z2 = b2 * value - a2 * y
        out.append(y)
    return out


def k_weight(values: Sequence[float]) -> list[float]:
    """Simplified 16 kHz two-biquad K-weighting, shelf then high-pass."""
    return _biquad(K_HIGHPASS, _biquad(K_SHELF, values))


def true_peak_4x(values: Sequence[float]) -> float:
    """4x Catmull-Rom peak estimate, including intersample extrema.

    For samples p1,p2 with clamped neighbours p0,p3 and t in [0,1], the
    interpolated value is 0.5*(2*p1 + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t^2
    + (-p0+3*p1-3*p2+p3)*t^3). Fractions 1/4, 1/2 and 3/4 are evaluated for
    every adjacent pair. This is an explicit estimate, not BS.1770 true peak.
    """
    if not values:
        return 0.0
    padded = [0.0] + [float(v) for v in values] + [0.0]
    peak = max(abs(float(v)) for v in values)
    for index in range(1, len(padded) - 2):
        p0, p1, p2, p3 = (padded[index - 1], padded[index],
                          padded[index + 1], padded[index + 2])
        for t in (0.25, 0.5, 0.75):
            t2 = t * t
            t3 = t2 * t
            value = 0.5 * (
                2.0 * p1
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )
            if abs(value) > peak:
                peak = abs(value)
    return peak


def _block_lufs(weighted: Sequence[float]) -> list[Optional[float]]:
    result: list[Optional[float]] = []
    for start in range(0, len(weighted) - BLOCK_SAMPLES + 1, HOP_SAMPLES):
        block = weighted[start:start + BLOCK_SAMPLES]
        mean_square = sum(value * value for value in block) / BLOCK_SAMPLES
        if mean_square <= 0.0:
            result.append(None)
        else:
            result.append(-0.691 + 10.0 * math.log10(mean_square))
    return result


def _gated_lufs(blocks: Sequence[Optional[float]]) -> dict[str, Any]:
    valid = [value for value in blocks if value is not None
             and math.isfinite(value)]
    if not valid:
        return {"integrated": None, "ungated": None, "threshold": None,
                "gated_blocks": 0, "reason": "no_positive_block"}
    linear_mean = sum(10.0 ** ((value + 0.691) / 10.0)
                      for value in valid) / len(valid)
    ungated = -0.691 + 10.0 * math.log10(linear_mean)
    threshold = max(ABS_GATE_LUFS, ungated - REL_GATE_LU)
    gated = [value for value in valid if value >= threshold]
    if not gated:
        return {"integrated": None, "ungated": r6(ungated),
                "threshold": r6(threshold), "gated_blocks": 0,
                "reason": "no_block_above_gate"}
    gated_mean = sum(10.0 ** ((value + 0.691) / 10.0)
                     for value in gated) / len(gated)
    integrated = -0.691 + 10.0 * math.log10(gated_mean)
    ordered = sorted(gated)
    low = ordered[int(0.1 * (len(ordered) - 1))]
    high = ordered[int(0.9 * (len(ordered) - 1))]
    lra = high - low if len(ordered) >= 10 else None
    return {
        "integrated": integrated,
        "ungated": ungated,
        "threshold": threshold,
        "gated_blocks": len(gated),
        "reason": None,
        "lra_estimate": lra,
        "lra_reason": None if lra is not None else "insufficient_gated_blocks",
    }


def analyze(values: Sequence[float]) -> dict[str, Any]:
    """Explicit gated LUFS and 4x true-peak estimate for one synthetic wave."""
    samples = tuple(float(v) for v in values)
    if any(not math.isfinite(v) for v in samples):
        raise ValueError("nonfinite_input")
    if not samples:
        return {"lufs": None, "reason": "empty_input", "blocks": [],
                "true_peak_abs": 0.0, "true_peak_dbtp": None,
                "sample_peak_abs": 0.0, "rms": 0.0, "gated_blocks": 0,
                "ungated_lufs": None, "gate_threshold_lufs": None,
                "lra_estimate": None, "lra_reason": "empty_input"}
    weighted = k_weight(samples)
    blocks = _block_lufs(weighted)
    gating = _gated_lufs(blocks)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    sample_peak = max(abs(value) for value in samples)
    tp = true_peak_4x(samples)
    return {
        "lufs": r6(gating["integrated"]),
        "reason": gating["reason"],
        "blocks": [r6(value) for value in blocks],
        "gated_blocks": gating["gated_blocks"],
        "ungated_lufs": r6(gating["ungated"]),
        "gate_threshold_lufs": r6(gating["threshold"]),
        "lra_estimate": r6(gating.get("lra_estimate")),
        "lra_reason": gating.get("lra_reason"),
        "true_peak_abs": r6(tp),
        "true_peak_dbtp": dbfs(tp),
        "sample_peak_abs": r6(sample_peak),
        "rms": r6(rms),
        "samples": len(samples),
    }


@dataclass(frozen=True)
class GainPlan:
    gain: float
    mode: str
    loudness_gain: Optional[float]
    true_peak_gain: Optional[float]
    limiting_factor: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "gain": r6(self.gain),
            "mode": self.mode,
            "loudness_gain": r6(self.loudness_gain),
            "true_peak_gain": r6(self.true_peak_gain),
            "limiting_factor": self.limiting_factor,
        }


def solve_gain(analysis: dict[str, Any]) -> GainPlan:
    """One static gain: -23 LUFS target, -1 dBTP ceiling, 64x safety cap."""
    peak = float(analysis["true_peak_abs"])
    peak_gain = TARGET_TP_LINEAR / peak if peak > 0.0 else None
    if analysis["lufs"] is None:
        return GainPlan(1.0, "identity_no_gate", None,
                        r6(peak_gain), "no_gated_loudness")
    loudness_gain = 10.0 ** ((TARGET_LUFS - float(analysis["lufs"])) / 20.0)
    gain = min(loudness_gain,
               peak_gain if peak_gain is not None else math.inf,
               MAX_GAIN)
    if gain == loudness_gain:
        mode, factor = "linear_loudness", "loudness_target"
    elif peak_gain is not None and gain == peak_gain:
        mode, factor = "true_peak_limited", "true_peak_ceiling"
    else:
        mode, factor = "max_gain_limited", "gain_safety_cap"
    return GainPlan(gain, mode, r6(loudness_gain), r6(peak_gain), factor)


@dataclass
class FrameResult:
    status: str
    samples: tuple[float, ...] = ()
    produced_count: int = 0
    valid_offset: int = 0
    valid_count: int = 0
    flags: int = 0
    epoch: int = 0
    source_first_sample: int = 0
    queue_depth: int = 0
    reason: str = ""


def form_frames(values: Sequence[float]) -> list[dict[str, Any]]:
    """Caller-owned 160-sample f32 frames with zero-padded final input."""
    frames: list[dict[str, Any]] = []
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = tuple(float(v) for v in values[start:start + FRAME_SAMPLES])
        valid = len(chunk)
        final = valid < FRAME_SAMPLES
        frames.append({
            "first_input_sample": start,
            "samples": chunk + (0.0,) * (FRAME_SAMPLES - valid),
            "valid_count": valid,
            "final": final,
            "flags": FLAG_FINAL_PADDING if final else 0,
            "epoch": 1,
        })
    return frames


class LoudnormFrameAdapter:
    """Offline two-pass gain applied through the public v0 frame geometry.

    The analysis pass is a control-plane operation outside this object. Once
    the static gain is known, every process call consumes exactly 160 padded
    samples, produces exactly 160 samples, has D=0 buffering and maps output
    sample 0 to ``first_input_sample``. No provider is registered and no
    hidden queue or dynamic state exists.
    """

    def __init__(self, gain: float, epoch: int = 1,
                 first_input_sample: int = 0) -> None:
        self._configure(gain, epoch, first_input_sample)

    def _configure(self, gain: float, epoch: int,
                   first_input_sample: int) -> None:
        if not isinstance(gain, (int, float)) or isinstance(gain, bool):
            raise ValueError("invalid_gain")
        gain = float(gain)
        if not math.isfinite(gain) or gain <= 0.0:
            raise ValueError("invalid_gain")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
            raise ValueError("invalid_epoch")
        if (not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool)
                or first_input_sample < 0):
            raise ValueError("invalid_first_input_sample")
        self.gain = gain
        self.epoch = epoch
        self.next_input = first_input_sample
        self.closed = False
        self.final_accepted = False
        self.last_accepted_start: Optional[int] = None
        self.stats = {
            "accepted_frames": 0,
            "accepted_valid_samples": 0,
            "produced_frames": 0,
            "drain_frames": 0,
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
            "rejected_closed": 0,
        }

    def _reject(self, reason: str) -> FrameResult:
        key = "rejected_" + reason
        if key in self.stats:
            self.stats[key] += 1
        return FrameResult(status=key, reason=reason)

    @staticmethod
    def _validate(frame: Any) -> Optional[str]:
        if frame is None:
            return "missing"
        if not isinstance(frame, dict):
            return "shape"
        start = frame.get("first_input_sample")
        valid = frame.get("valid_count")
        values = frame.get("samples")
        if (not isinstance(start, int) or isinstance(start, bool) or start < 0
                or not isinstance(valid, int) or isinstance(valid, bool)
                or not 1 <= valid <= FRAME_SAMPLES):
            return "shape"
        if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
            return "shape"
        if len(values) != FRAME_SAMPLES:
            return "short" if len(values) < FRAME_SAMPLES else "shape"
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               for value in values):
            return "shape"
        converted = tuple(float(value) for value in values)
        if any(not math.isfinite(value) for value in converted):
            return "nonfinite"
        if valid < FRAME_SAMPLES and not bool(frame.get("final", False)):
            return "short"
        if any(value != 0.0 for value in converted[valid:]):
            return "bad_padding"
        return None

    def process(self, frame: Any) -> FrameResult:
        if self.closed:
            return self._reject("closed")
        if self.final_accepted:
            return self._reject("after_final")
        problem = self._validate(frame)
        if problem:
            return self._reject(problem)
        if frame.get("epoch", self.epoch) != self.epoch:
            return self._reject("stale_epoch")
        start = int(frame["first_input_sample"])
        if self.last_accepted_start is not None:
            if start == self.last_accepted_start:
                return self._reject("duplicate")
            if start < self.last_accepted_start:
                return self._reject("out_of_order")
        if start != self.next_input:
            return self._reject("future_packet")
        values = tuple(float(value) * self.gain
                       for value in frame["samples"])
        if any(not math.isfinite(value) for value in values):
            return self._reject("nonfinite")
        valid = int(frame["valid_count"])
        final = bool(frame.get("final", False))
        self.last_accepted_start = start
        self.next_input = start + FRAME_SAMPLES
        self.final_accepted = final
        self.stats["accepted_frames"] += 1
        self.stats["accepted_valid_samples"] += valid
        self.stats["produced_frames"] += 1
        return FrameResult(
            status="ok",
            samples=values,
            produced_count=FRAME_SAMPLES,
            valid_count=valid,
            flags=FLAG_FINAL_PADDING if final and valid < FRAME_SAMPLES else 0,
            epoch=self.epoch,
            source_first_sample=start,
        )

    def drain(self) -> list[FrameResult]:
        if self.closed:
            return [self._reject("closed")]
        return []

    def reset(self, epoch: int, first_input_sample: int) -> FrameResult:
        if self.closed:
            return self._reject("closed")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch <= self.epoch:
            return self._reject("stale_epoch")
        self._configure(self.gain, epoch, first_input_sample)
        return FrameResult(status="ok", epoch=epoch)

    def close(self) -> None:
        self.closed = True


def apply_plan(values: Sequence[float], plan: GainPlan
               ) -> tuple[tuple[float, ...], list[FrameResult],
                          dict[str, int]]:
    frames = form_frames(values)
    adapter = LoudnormFrameAdapter(plan.gain)
    results: list[FrameResult] = []
    try:
        for frame in frames:
            result = adapter.process(frame)
            if result.status != "ok":
                raise AssertionError("frame rejected: " + result.status)
            results.append(result)
        drained = adapter.drain()
        if drained:
            raise AssertionError("unexpected drain output")
    finally:
        stats = dict(adapter.stats)
        adapter.close()
    output = tuple(value for result in results
                   for value in result.samples)[:len(values)]
    if len(output) != len(values):
        raise AssertionError("sample conservation failure")
    return output, results, stats


def sweep_signal(samples: int = TONE_SAMPLES) -> tuple[float, ...]:
    phase = 0.0
    out: list[float] = []
    for index in range(samples):
        frequency = 100.0 + 5900.0 * index / max(samples - 1, 1)
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
        out.append(0.03 * math.sin(phase))
    return tuple(out)


def step_signal(samples: int = SCORED_SAMPLES) -> tuple[float, ...]:
    segments: list[tuple[float, float, float]] = []
    cursor = 0.0
    for duration, amplitude in STEP_SEGMENTS:
        segments.append((cursor, cursor + duration, amplitude))
        cursor += duration
    out: list[float] = []
    for index in range(samples):
        time_s = index / SAMPLE_RATE_HZ
        level = 0.0
        for start, end, amplitude in segments:
            if start <= time_s < end:
                level = amplitude
                break
        out.append(level + 0.0001 * math.sin(
            2.0 * math.pi * 300.0 * time_s))
    return tuple(out)


def impulse_signal(samples: int = SCORED_SAMPLES,
                   peak_index: int = 4000) -> tuple[float, ...]:
    out = [0.0] * samples
    out[peak_index] = 0.5
    return tuple(out)


def silence_signal(samples: int = SCORED_SAMPLES) -> tuple[float, ...]:
    return (0.0,) * samples


def tone(frequency_hz: float, amplitude: float = 0.05,
         samples: int = TONE_SAMPLES) -> tuple[float, ...]:
    return tuple(amplitude * math.sin(
        2.0 * math.pi * frequency_hz * index / SAMPLE_RATE_HZ)
        for index in range(samples))


def intersample_signal(samples: int = SCORED_SAMPLES) -> tuple[float, ...]:
    out = [0.0] * samples
    for index in range(1000, min(samples, 1000 + 4 * 200), 4):
        out[index] = 0.4
        out[index + 1] = 0.4
    return tuple(out)


def sparse_intersample_signal(samples: int = SCORED_SAMPLES,
                              pulses: int = 10) -> tuple[float, ...]:
    """Sparse high-crest pairs whose cubic peak exceeds the sample peak."""
    out = [0.0] * samples
    for index in range(pulses):
        start = 1000 + index * 1600
        out[start] = 0.9
        out[start + 1] = 0.9
    return tuple(out)


def speech_signal(samples: int = SCORED_SAMPLES, seed: int = SEED
                  ) -> tuple[float, ...]:
    """Frozen voiced/unvoiced/silence surrogate, not recorded speech."""
    rng = LCG(seed)
    formant_a = [0.0, 0.0]
    formant_b = [0.0, 0.0]
    noise_state = 0.0
    boundaries = tuple(start for start, _, _ in SPEECH_REGIONS[1:])
    out: list[float] = []
    for index in range(samples):
        time_s = index / SAMPLE_RATE_HZ
        frame = index // FRAME_SAMPLES
        kind = "silence"
        for start, end, label in SPEECH_REGIONS:
            if start <= frame < end:
                kind = label
                break
        fade = min(1.0, min(abs(index - boundary)
                            for boundary in boundaries) / FRAME_SAMPLES)
        if kind == "voiced":
            f0 = 118.0 + 16.0 * math.sin(2.0 * math.pi * 0.31 * time_s)
            period = max(1, int(round(SAMPLE_RATE_HZ / f0)))
            drive = 1.0 if index % period == 0 else 0.0
            formant_a = (0.972 * formant_a[0] - 0.018 * formant_a[1] + drive,
                         formant_a[0])
            formant_b = (0.947 * formant_b[0] - 0.035 * formant_b[1] + drive,
                         formant_b[0])
            syllable = 0.6 + 0.4 * math.sin(
                2.0 * math.pi * 2.1 * time_s) ** 2
            value = 0.20 * syllable * (0.45 * formant_a[0]
                                       + 0.18 * formant_b[0])
        elif kind == "unvoiced":
            noise = rng.uniform()
            noise_state = 0.7 * noise_state + 0.3 * noise
            value = 0.055 * noise_state + 0.012 * noise
        else:
            value = 0.0004 * rng.uniform()
        value += 0.0002 * rng.uniform()
        out.append(max(-0.9, min(0.9, value * fade)))
    return tuple(out)


def run_condition(values: Sequence[float], mode: str,
                  fixed_gain: Optional[float] = None) -> dict[str, Any]:
    """One offline analysis pass plus one bounded frame-application pass."""
    before = analyze(values)
    if mode == "candidate":
        plan = solve_gain(before)
    elif mode == "identity":
        plan = GainPlan(1.0, "control_identity", None, None, "none")
    elif mode == "fixed_gain":
        if fixed_gain is None:
            raise ValueError("fixed_gain_required")
        plan = GainPlan(float(fixed_gain), "control_fixed_gain", None, None,
                        "none")
    elif mode == "sample_peak":
        peak = float(before["sample_peak_abs"])
        gain = TARGET_TP_LINEAR / peak if peak > 0.0 else 1.0
        plan = GainPlan(gain, "control_sample_peak", None, None, "none")
    else:
        raise ValueError("unknown_condition_mode")
    output, results, stats = apply_plan(values, plan)
    after = analyze(output)
    input_rms = float(before["rms"])
    output_rms = float(after["rms"])
    measured_ratio = output_rms / input_rms if input_rms > 0.0 else None
    expected_ratio = float(plan.gain)
    gain_error_db = (20.0 * math.log10(measured_ratio / expected_ratio)
                     if measured_ratio is not None and measured_ratio > 0.0
                     else None)
    errors = []
    if after["reason"]:
        errors.append(after["reason"])
    if output_rms == 0.0 and input_rms > 0.0:
        errors.append("zero_output")
    return {
        "mode": mode,
        "plan": plan.as_dict(),
        "input_analysis": before,
        "output_analysis": after,
        "input_digest": tensor_digest(values),
        "output_digest": tensor_digest(output),
        "target_error_lu": (r6(float(after["lufs"]) - TARGET_LUFS)
                            if after["lufs"] is not None else None),
        "true_peak_headroom_db": (r6(TARGET_TP_DBTP - float(after["true_peak_dbtp"]))
                                  if after["true_peak_dbtp"] is not None else None),
        "rms_gain_ratio": r6(measured_ratio),
        "gain_error_db": r6(gain_error_db),
        "finite_output": all(math.isfinite(value) for value in output),
        "at_or_above_one_count": sum(1 for value in output
                                     if math.isfinite(value)
                                     and abs(value) >= 1.0),
        "counts": {
            "source_samples": len(values),
            "output_samples": len(output),
            "frames": len(results),
            "valid_samples": sum(result.valid_count for result in results),
            "accepted_frames": stats["accepted_frames"],
            "produced_frames": stats["produced_frames"],
            "rejections": sum(value for key, value in stats.items()
                              if key.startswith("rejected_")),
        },
        "source_mapping_ok": all(
            result.source_first_sample == index * FRAME_SAMPLES
            and result.produced_count == FRAME_SAMPLES
            and result.valid_offset == 0
            for index, result in enumerate(results)),
        "buffering_delay_samples": 0,
        "invalid_reasons": errors,
        "output_samples": output,
    }


def public_summary(condition: dict[str, Any]) -> dict[str, Any]:
    """Drop raw waveform; keep deterministic measurements and digests."""
    return {key: value for key, value in condition.items()
            if key != "output_samples"}


def peak_index(values: Sequence[float]) -> int:
    return max(range(len(values)), key=lambda index: abs(values[index]))


def build_state_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    clean = speech_signal()
    frames = form_frames(clean[:8 * FRAME_SAMPLES])
    adapter = LoudnormFrameAdapter(candidate["plan"]["gain"])
    for frame in frames:
        if adapter.process(frame).status != "ok":
            raise AssertionError("state setup rejected")
    reset = adapter.reset(2, 0)
    stale = adapter.process({**frames[0], "epoch": 1})
    reset_results = [adapter.process({**frame, "epoch": 2})
                     for frame in frames]
    reset_results.extend(adapter.drain())
    reset_tuples = [(result.samples, result.flags, result.source_first_sample)
                    for result in reset_results]
    fresh = LoudnormFrameAdapter(candidate["plan"]["gain"], epoch=2)
    fresh_results = [fresh.process({**frame, "epoch": 2})
                     for frame in frames]
    fresh_tuples = [(result.samples, result.flags, result.source_first_sample)
                    for result in fresh_results]
    drain_results = adapter.drain()
    adapter.close()
    after_close = adapter.process(frames[0])
    fresh.close()

    other = LoudnormFrameAdapter(candidate["plan"]["gain"] * 0.5)
    baseline = dict(other.stats)
    invalid = {
        "missing_frame": None,
        "wrong_shape": {"first_input_sample": 0, "samples": ((0.0,),) * FRAME_SAMPLES},
        "short_frame": {"first_input_sample": 0,
                        "samples": (0.0,) * (FRAME_SAMPLES - 1)},
        "nonfinite_frame": {"first_input_sample": 0,
                            "samples": (float("nan"),) * FRAME_SAMPLES},
        "bad_padding": {**frames[0], "valid_count": 10, "final": True,
                        "samples": (0.1,) * 10 + (0.2,) * (FRAME_SAMPLES - 10)},
        "stale_epoch": {**frames[0], "epoch": 99},
    }
    invalid_results = {}
    for name, frame in invalid.items():
        result = other.process(frame)
        invalid_results[name] = {
            "status": result.status,
            "non_rejected_counters_unchanged": {
                key: value for key, value in other.stats.items()
                if not key.startswith("rejected_")
            } == {key: value for key, value in baseline.items()
                  if not key.startswith("rejected_")},
        }
    first = other.process(frames[0])
    duplicate = other.process(frames[0])
    future = other.process({**frames[2], "first_input_sample": 320})
    second = other.process(frames[1])
    out_of_order = other.process(frames[0])
    final_valid = other.process({**frames[0], "first_input_sample": 2 * FRAME_SAMPLES,
                                 "final": True, "valid_count": 37,
                                 "samples": (0.01,) * 37 + (0.0,) * 123})
    after_final_frame = {**frames[0], "first_input_sample": 3 * FRAME_SAMPLES}
    after_final = other.process(after_final_frame)
    accepted_before_final = 2
    invalid_results["duplicate_frame"] = {
        "status": duplicate.status,
        "non_rejected_counters_unchanged": other.stats["accepted_frames"] == 1,
    }
    invalid_results["future_packet"] = {
        "status": future.status,
        "non_rejected_counters_unchanged": other.stats["accepted_frames"] == 1,
    }
    invalid_results["out_of_order_frame"] = {
        "status": out_of_order.status,
        "non_rejected_counters_unchanged":
            other.stats["accepted_frames"] == accepted_before_final,
    }
    invalid_results["process_after_final"] = {
        "status": after_final.status,
        "final_accepted": final_valid.status == "ok"
        and final_valid.valid_count == 37
        and final_valid.flags == FLAG_FINAL_PADDING
        and second.status == "ok",
    }
    other.close()
    invalid_results["closed_rejects_process"] = {
        "status": other.process(frames[0]).status,
        "non_rejected_counters_unchanged": True,
    }
    invalid_results["invalid_reset_epoch"] = {
        "status": LoudnormFrameAdapter(1.0).reset(0, 0).status,
        "non_rejected_counters_unchanged": True,
    }
    return {
        "invalid_cases": invalid_results,
        "reset_accepted": reset.status == "ok",
        "stale_epoch_after_reset_rejected":
            stale.status == "rejected_stale_epoch",
        "reset_bit_identical_to_fresh_epoch2": reset_tuples == fresh_tuples,
        "closed_session_rejects_process": after_close.status == "rejected_closed",
        "sessions_independent": adapter.stats["produced_frames"] == 8
        and fresh.stats["produced_frames"] == 8,
        "first_valid_frame_accepted": first.status == "ok",
        "drain_frames": len(drain_results),
        "buffering_delay_samples": 0,
        "queue_depth": 0,
    }


def build_report() -> dict[str, Any]:
    clean = speech_signal()
    candidate = run_condition(clean, "candidate")
    identity = run_condition(clean, "identity")
    fixed = run_condition(clean, "fixed_gain", fixed_gain=10.0 ** (6.0 / 20.0))
    peak_control = run_condition(clean, "sample_peak")

    conditions = {
        "identity_control": public_summary(identity),
        "fixed_plus_6db_control": public_summary(fixed),
        "sample_peak_control": public_summary(peak_control),
        "candidate_linear_loudnorm_ref": public_summary(candidate),
    }

    frequency_response: dict[str, Any] = {}
    for frequency in FREQUENCIES_HZ:
        wave = tone(frequency)
        result = run_condition(wave, "candidate")
        frequency_response[str(int(frequency))] = {
            "frequency_hz": frequency,
            "applied_gain": result["plan"]["gain"],
            "measured_rms_ratio": result["rms_gain_ratio"],
            "gain_error_db": result["gain_error_db"],
            "gain_mode": result["plan"]["mode"],
            "true_peak_headroom_db": result["true_peak_headroom_db"],
        }
    sweep = sweep_signal()
    sweep_result = run_condition(sweep, "candidate")
    step_wave = step_signal()
    step_result = run_condition(step_wave, "candidate")
    rms_ratios = [float(value["measured_rms_ratio"])
                  for value in frequency_response.values()
                  if value["measured_rms_ratio"] is not None]
    response_deviation = max(abs(float(value["gain_error_db"]))
                             for value in frequency_response.values()
                             if value["gain_error_db"] is not None)

    impulse = impulse_signal()
    impulse_result = run_condition(impulse, "candidate")
    impulse_input_peak = peak_index(impulse)
    impulse_output_peak = peak_index(impulse_result["output_samples"])
    delay = {
        "declared_buffering_delay_samples": 0,
        "measured_impulse_lag_samples": impulse_output_peak
        - impulse_input_peak,
        "expected_impulse_lag_samples": 0,
        "impulse_input_peak_index": impulse_input_peak,
        "impulse_output_peak_index": impulse_output_peak,
        "source_mapping_ok": all(
            condition["source_mapping_ok"]
            for condition in conditions.values()),
        "analysis_lookahead": "whole synthetic programme before first process call; "
                              "control-plane only, not audio delay",
        "pass": impulse_output_peak - impulse_input_peak == 0
        and all(condition["source_mapping_ok"]
                for condition in conditions.values()),
    }

    silent = silence_signal()
    silent_result = run_condition(silent, "candidate")
    intersample = intersample_signal()
    intersample_before = analyze(intersample)
    intersample_result = run_condition(intersample, "candidate")
    sparse = sparse_intersample_signal()
    sparse_before = analyze(sparse)
    sparse_result = run_condition(sparse, "candidate")
    near_silence = run_condition(tone(1000.0, amplitude=0.001), "candidate")
    full_scale = run_condition(tone(1000.0, amplitude=0.9), "candidate")
    partial = run_condition(speech_signal()[:8 * FRAME_SAMPLES
                                            + FINAL_PARTIAL_SAMPLES],
                            "candidate")
    state = build_state_evidence(candidate)
    nonfinite_error = _nonfinite_error()
    numerical = {
        "silence": {
            "loudness": silent_result["input_analysis"]["lufs"],
            "reason": silent_result["input_analysis"]["reason"],
            "gain_mode": silent_result["plan"]["mode"],
            "gain": silent_result["plan"]["gain"],
            "output_peak": silent_result["output_analysis"]["sample_peak_abs"],
            "finite": silent_result["finite_output"],
        },
        "intersample_peak": {
            "input_sample_peak": intersample_before["sample_peak_abs"],
            "input_true_peak_estimate": intersample_before["true_peak_abs"],
            "overshoot_db": dbfs(intersample_before["true_peak_abs"] /
                                 float(intersample_before["sample_peak_abs"])),
            "output_sample_peak": intersample_result["output_analysis"][
                "sample_peak_abs"],
            "output_true_peak_estimate": intersample_result[
                "output_analysis"]["true_peak_abs"],
            "headroom_db": intersample_result["true_peak_headroom_db"],
            "gain_mode": intersample_result["plan"]["mode"],
        },
        "sparse_intersample_ceiling": {
            "input_sample_peak": sparse_before["sample_peak_abs"],
            "input_true_peak_estimate": sparse_before["true_peak_abs"],
            "overshoot_db": dbfs(sparse_before["true_peak_abs"] /
                                 float(sparse_before["sample_peak_abs"])),
            "gain_mode": sparse_result["plan"]["mode"],
            "gain": sparse_result["plan"]["gain"],
            "output_true_peak_dbtp": sparse_result["output_analysis"][
                "true_peak_dbtp"],
            "headroom_db": sparse_result["true_peak_headroom_db"],
            "target_error_lu": sparse_result["target_error_lu"],
        },
        "near_silence_gain_cap": {
            "input_lufs": near_silence["input_analysis"]["lufs"],
            "gain_mode": near_silence["plan"]["mode"],
            "gain": near_silence["plan"]["gain"],
            "limiting_factor": near_silence["plan"]["limiting_factor"],
            "target_error_lu": near_silence["target_error_lu"],
        },
        "full_scale_tone": {
            "gain_mode": full_scale["plan"]["mode"],
            "gain": full_scale["plan"]["gain"],
            "output_true_peak_dbtp": full_scale["output_analysis"][
                "true_peak_dbtp"],
            "headroom_db": full_scale["true_peak_headroom_db"],
            "at_or_above_one_count": full_scale["at_or_above_one_count"],
            "finite": full_scale["finite_output"],
        },
        "nonfinite_analysis": {
            "status": "rejected",
            "reason": str(nonfinite_error),
        },
        "determinism": {
            "generator_digest_repeated": tensor_digest(clean)
            == tensor_digest(speech_signal()),
            "canonical_bytes_repeated": canonical_bytes(candidate["plan"])
            == canonical_bytes(solve_gain(analyze(clean)).as_dict()),
        },
    }

    regressions: list[dict[str, Any]] = []
    for name, condition in conditions.items():
        error = condition["target_error_lu"]
        if error is not None and abs(error) > TOLERANCE_LU:
            regressions.append({
                "condition": name,
                "metric": "target_error_lu",
                "value": error,
                "tolerance_lu": TOLERANCE_LU,
                "interpretation": "outside the historical +/-0.2 LU target tolerance",
            })
        if condition["true_peak_headroom_db"] is not None \
                and condition["true_peak_headroom_db"] < 0.0:
            regressions.append({
                "condition": name,
                "metric": "true_peak_headroom_db",
                "value": condition["true_peak_headroom_db"],
                "interpretation": "estimated true peak above the -1 dBTP cap",
            })
    for name, item in (("impulse", impulse_result),
                       ("intersample_peak", intersample_result),
                       ("sparse_intersample_ceiling", sparse_result),
                       ("near_silence", near_silence),
                       ("full_scale_tone", full_scale)):
        if item["target_error_lu"] is not None \
                and abs(item["target_error_lu"]) > TOLERANCE_LU:
            regressions.append({
                "condition": name,
                "metric": "target_error_lu",
                "value": item["target_error_lu"],
                "interpretation": "true-peak or gain-safety cap prevented the loudness target",
            })
    regressions.append({
        "condition": "all_conditions",
        "metric": "lra_target",
        "value": TARGET_LRA_LU,
        "interpretation": "LRA setting is recorded but not implemented or enforced",
    })
    regressions.append({
        "condition": "all_conditions",
        "metric": "dynamic_mode",
        "value": None,
        "interpretation": "dynamic loudnorm mode is not implemented; only one static gain is evaluated",
    })

    gates: dict[str, dict[str, Any]] = {}
    for blocker in QUALIFICATION_BLOCKERS:
        gates[blocker["id"]] = {
            "status": blocker["status"],
            "reason": blocker["reason"],
            "reopen": blocker["reopen"],
        }
    gates["public_frame_boundary"] = {
        "status": "pass",
        "reason": "160-sample f32 frames, exact source mapping, validity/epoch/reset/close checks in synthetic state evidence.",
        "reopen": "Not a release gate; independent review still required for any provider intake.",
    }
    gates["dsp_profile_synthetic"] = {
        "status": "pass",
        "reason": "Sweeps, steps, impulse, silence, synthetic speech, control, gain/response, headroom, true peak, delay, numerics and state are recorded.",
        "reopen": "Not a release gate; real programme and independent-meter evidence remain blocked.",
    }
    gates["gpl_binary_exclusion"] = {
        "status": "pass",
        "reason": "No FFmpeg binary, GPL component, licensed asset or generated WAV is vendored, downloaded, shipped or wrapped in this evidence directory.",
        "reopen": "Not a release gate; separate license review is required before any external runtime is used.",
    }

    artifact_names = ("reference.py", "run.py", "test_reference.py",
                      "verify.py", "tool-provenance.json")
    here = Path(__file__).resolve().parent
    artifact_pins = [
        {"path": name,
         "sha256": hashlib.sha256((here / name).read_bytes()).hexdigest(),
         "kind": "task_fixture"}
        for name in artifact_names
    ]
    fixture_spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "target_lufs": TARGET_LUFS,
        "target_lra_lu": TARGET_LRA_LU,
        "target_tp_dbtp": TARGET_TP_DBTP,
        "tolerance_lu": TOLERANCE_LU,
        "max_gain": MAX_GAIN,
        "block_samples": BLOCK_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "absolute_gate_lufs": ABS_GATE_LUFS,
        "relative_gate_lu": REL_GATE_LU,
        "k_weighting": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "high_shelf_hz": K_SHELF_HZ,
            "high_shelf_gain_db": K_SHELF_GAIN_DB,
            "highpass_hz": K_HIGHPASS_HZ,
            "highpass_q": K_HIGHPASS_Q,
            "coefficients": [list(K_SHELF), list(K_HIGHPASS)],
            "note": "Simplified two-biquad approximation; not an EBU Mode K-weighting implementation.",
        },
        "true_peak": {
            "oversample": OVERSAMPLE,
            "interpolator": "Catmull-Rom cubic at t=1/4,1/2,3/4",
            "note": "Explicit intersample estimate; not BS.1770 true peak.",
        },
        "seed": SEED,
        "scored_frames": SCORED_FRAMES,
        "regions": [list(region) for region in SPEECH_REGIONS],
        "frequencies_hz": list(FREQUENCIES_HZ),
        "sparse_intersample_pulses": 10,
        "source_pins": {pin["path"]: pin["sha256"] for pin in SOURCE_PINS},
        "artifact_pins": {pin["path"]: pin["sha256"] for pin in artifact_pins},
        "base_commit": BASE_COMMIT,
    }
    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": "optional task-local synthetic loudness-target reference; not a standards meter, FFmpeg wrapper, release or real-audio qualification",
        "profile": "DSP",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "base_commit": BASE_COMMIT,
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": [dict(pin) for pin in SOURCE_PINS],
        "artifact_pins": artifact_pins,
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "buffering_delay_samples": 0,
        },
        "boundary": {
            "provider_id": PROVIDER_ID,
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "note": "Python model of an offline host analyzer plus a static-gain frame adapter at the public v0 geometry; no C provider, registry change or public flag.",
        },
        "targets": {
            "integrated_lufs": TARGET_LUFS,
            "lra_lu": TARGET_LRA_LU,
            "true_peak_dbtp": TARGET_TP_DBTP,
            "tolerance_lu": TOLERANCE_LU,
            "lra_enforced": False,
            "dynamic_mode_supported": False,
        },
        "ffmpeg_provenance": dict(TOOL_PROVENANCE),
        "cohort": {
            "kind": "deterministic_synthetic_paired",
            "frames": SCORED_FRAMES,
            "samples": SCORED_SAMPLES,
            "duration_seconds": r6(SCORED_SAMPLES / SAMPLE_RATE_HZ),
            "clean_digest": tensor_digest(clean),
            "seed": SEED,
            "regions": [list(region) for region in SPEECH_REGIONS],
        },
        "conditions": conditions,
        "sweeps": {
            "frequencies": frequency_response,
            "chirp": public_summary(sweep_result),
            "rms_ratio_min": r6(min(rms_ratios)) if rms_ratios else None,
            "rms_ratio_max": r6(max(rms_ratios)) if rms_ratios else None,
            "max_abs_gain_error_db": r6(response_deviation),
        },
        "steps": public_summary(step_result),
        "impulse": public_summary(impulse_result),
        "silence": public_summary(silent_result),
        "control": {
            "identity": public_summary(identity),
            "fixed_plus_6db": public_summary(fixed),
            "sample_peak": public_summary(peak_control),
            "tone_1khz": public_summary(run_condition(tone(1000.0),
                                                       "candidate")),
        },
        "headroom_and_true_peak": numerical,
        "final_partial_window": public_summary(partial),
        "delay": delay,
        "state": state,
        "numerical_behavior": numerical,
        "regressions": regressions,
        "gates": gates,
        "controls_all_pass": all(
            isinstance(value, dict) and value.get("status", "").startswith(
                "rejected_")
            for value in state["invalid_cases"].values()),
        "alignment_pass": delay["pass"],
        "state_pass": state["reset_accepted"]
        and state["reset_bit_identical_to_fresh_epoch2"]
        and state["closed_session_rejects_process"],
        "all_outputs_finite": all(
            condition["finite_output"] for condition in conditions.values())
        and impulse_result["finite_output"]
        and silent_result["finite_output"],
        "all_valid_frames_conserved": all(
            condition["counts"]["valid_samples"]
            == condition["counts"]["source_samples"]
            and condition["source_mapping_ok"]
            for condition in conditions.values()),
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "blockers": [dict(blocker) for blocker in QUALIFICATION_BLOCKERS],
        "no_missing_result_qualifies_candidate": True,
        "note": "Synthetic observations only. Historical FFmpeg same-filter results are pinned context and are not rerun, pooled or qualified here.",
    }
    return impurity_free(report)


def _nonfinite_error() -> Exception:
    try:
        analyze((float("nan"),) * FRAME_SAMPLES)
    except Exception as error:  # noqa: BLE001 - explicit validity probe
        return error
    raise AssertionError("nonfinite analysis was not rejected")


def impurity_free(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite report value")
    if isinstance(value, dict):
        return {key: impurity_free(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [impurity_free(item) for item in value]
    return value


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: reference.py <report.json> [tool-provenance.json]")
    report_path = Path(sys.argv[1])
    provenance_path = (Path(sys.argv[2]) if len(sys.argv) == 3
                       else report_path.parent / "tool-provenance.json")
    report = build_report()
    report_path.write_bytes(canonical_report_bytes(report))
    provenance_path.write_bytes(json.dumps(
        TOOL_PROVENANCE, sort_keys=True, indent=2, ensure_ascii=False,
        allow_nan=False).encode("utf-8") + b"\n")
    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    print("report_sha256=" + digest)
    print("fixture_digest=" + report["fixture_digest"])
    print("qualification_status=" + report["qualification_status"]
          + " controls_all_pass=" + str(report["controls_all_pass"])
          + " alignment_pass=" + str(report["alignment_pass"])
          + " state_pass=" + str(report["state_pass"])
          + " regressions=" + str(len(report["regressions"])))


if __name__ == "__main__":
    main()
