# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic static-gain / ridge held-out reference fixture.

Task-local, optional, unregistered evidence for the audio-sdk public v0
boundary. It models a scalar static-gain provider (one fixed gain per session)
with a peak ceiling, and compares three further strategies on an explicit
frozen train / held-out split:

* ``no_gain`` -- identity control, no ceiling protection;
* ``target_rms`` -- direct dB rule from measured held-out RMS, with ceiling;
* ``ridge`` -- one-feature ridge regression fitted on the train split only;
* ``envelope_agc`` -- stateful attack/release control with peak protection.

The ridge baseline is a *reported estimate*, not a selected default. No default
is chosen or advertised anywhere in this package. Nothing is registered, no
descriptor setting is changed, and installed v0 behavior is untouched. The
candidate status is ``proposal_only_synthetic_incomplete`` / ``not_qualified``
and every missing-result or real-world gate remains blocked.

Only deterministic seeded synthetic signals and the Python standard library
are used. No corpus, download, licensed runtime, device, listening result or
vendor asset is present.
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

CONTRACT_ID = "audio-sdk/ridge-static-gain/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/ridge-static-gain/report/0.1"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
PROVIDER_ID = "dsp.ridge-static-gain-ref.v0"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
BUFFERING_DELAY_SAMPLES = 0  # memoryless scalar gain, D = 0 per CONTRACTS.md

SEED_CORPUS = 20261028
TRAIN_CLIPS = 180
HELD_OUT_CLIPS = 60
CLIP_SAMPLES = 16000
CLIP_FRAMES = CLIP_SAMPLES // FRAME_SAMPLES
PERTURBATION_DB_MIN = -36.0
PERTURBATION_DB_MAX = -12.0
TARGET_RMS_DB = -24.0
TARGET_RMS = 10.0 ** (TARGET_RMS_DB / 20.0)
PEAK_CEILING = 0.85
MAX_GAIN = 64.0
RIDGE_LAMBDA = 1.0e-6
EPS = 1.0e-12

STRATEGY_NO_GAIN = "no_gain"
STRATEGY_TARGET = "target_rms"
STRATEGY_RIDGE = "ridge"
STRATEGY_ENVELOPE = "envelope_agc"
STRATEGIES = (STRATEGY_NO_GAIN, STRATEGY_TARGET, STRATEGY_RIDGE,
              STRATEGY_ENVELOPE)
STATIC_STRATEGIES = (STRATEGY_NO_GAIN, STRATEGY_TARGET, STRATEGY_RIDGE)

FLAG_FINAL_PADDING = 2

# External bytes are resolved relative to /Users/htsakanyan/workspace/audioml;
# worktree-relative pins are resolved relative to the SDK worktree root.
SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "research/level_tone_control_20261028.md",
        "root": "source",
        "sha256": "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
        "summary": "CLN-09/CLN-10 source: static RMS target gain, ridge gain estimate and envelope AGC; source-reported held-out 0.000/3.825/4.414 dB are context only.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 geometry, 160-sample process contract, D=0 source mapping and final-padding rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "DSP acceptance profile: sweeps, steps, impulse, silence, control, gain, headroom, delay, numerical and state evidence.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by this Python model.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary: process, drain, reset, epoch and close semantics.",
    },
    {
        "path": "REUSE.toml",
        "root": "worktree",
        "sha256": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
        "summary": "Aggregate docs/** Apache-2.0 annotation covering this task-local directory.",
    },
)

QUALIFICATION_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "real_speech_benchmark",
        "status": "blocked",
        "reason": "No rights-qualified paired real-speech cohort exists here. The pinned research document says its real-speech benchmark is not established.",
        "reopen": "Freeze a permitted, speaker/session-split paired cohort with fixed crop, RMS target and peak policy.",
    },
    {
        "id": "blinded_listening_quality",
        "status": "blocked",
        "reason": "No consented listeners, WER, intelligibility or listening test was run; synthetic dB error is not a quality claim.",
        "reopen": "Run an independently reviewed blinded listening and intelligibility protocol on permitted material.",
    },
    {
        "id": "pinned_external_controls",
        "status": "blocked",
        "reason": "WebRTC AGC2 and FFmpeg loudness/limiter implementations are literature links in the pinned research note only; no pinned code, version, hash or runtime is installed in this fixture and none was downloaded.",
        "reopen": "Pin exact external control code, version, license, hashes and runtime, then rerun the same frozen cohort.",
    },
    {
        "id": "target_runtime_deadline",
        "status": "blocked",
        "reason": "No paced target-device, deadline, CPU or memory measurement is included; this is a Python reference only.",
        "reopen": "Measure the exact installed build on the target under pacing, load, deadline, CPU and memory budgets.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "No C provider is compiled, registered or packaged. The conceptual ID is unregistered, OFF by default and has empty descriptor settings.",
        "reopen": "Complete opt-in provider intake with independent review, OFF default and empty descriptor settings.",
    },
    {
        "id": "default_selection",
        "status": "blocked",
        "reason": "No default is selected or advertised by this task. Held-out comparisons are reported without ranking any strategy as the shipped choice.",
        "reopen": "Require a jointly reviewed real-speech cohort, listening result, pinned external controls and explicit default-selection approval.",
    },
)

EVIDENCE_CLASSES = {
    "synthetic_paired": "Generated here under fixed seeds; both train and held-out splits are synthetic.",
    "source_reported_context": "0.000/3.825/4.414/2.577 dB values in the pinned research note are context only; not rerun or pooled.",
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

    def unit(self) -> float:
        return 0.5 * (self.uniform() + 1.0)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples."""
    return hashlib.sha256(b"".join(struct.pack("<f", float(v))
                                   for v in values)).hexdigest()


def r6(value: float) -> float:
    return round(float(value), 6)


def dbfs(rms: float) -> float:
    return 20.0 * math.log10(max(float(rms), EPS))


def exact_wave_stats(values: Sequence[float]) -> tuple[float, float]:
    """Unrounded RMS and peak; gain arithmetic must not use report rounding."""
    if not values:
        return 0.0, 0.0
    rms = math.sqrt(sum(v * v for v in values) / len(values))
    peak = max(abs(v) for v in values)
    return rms, peak


def wave_features(values: Sequence[float]) -> dict[str, Any]:
    rms, peak = exact_wave_stats(values)
    return {
        "samples": len(values),
        "rms": r6(rms),
        "rms_dbfs": r6(dbfs(rms)),
        "peak_abs": r6(peak),
        "finite": all(math.isfinite(v) for v in values),
        "nonfinite_count": sum(1 for v in values if not math.isfinite(v)),
        "at_or_above_one_count": sum(1 for v in values
                                     if math.isfinite(v) and abs(v) >= 1.0),
        "digest": tensor_digest(values),
    }


def static_gain(rms: float, peak: float, target: float = TARGET_RMS,
                ceiling: float = PEAK_CEILING,
                max_gain: float = MAX_GAIN) -> tuple[float, bool, Optional[float]]:
    """Direct dB rule with peak ceiling and gain clamp.

    Returns ``(applied_gain, cap_engaged, raw_gain)``. Zero/denormal input has
    no defined gain, so it falls back to identity rather than infinity.
    """
    if not all(math.isfinite(v) for v in (rms, peak, target, ceiling, max_gain)):
        raise ValueError("nonfinite gain input")
    if rms < 0.0 or peak < 0.0 or ceiling <= 0.0 or max_gain <= 0.0 or target <= 0.0:
        raise ValueError("invalid gain input")
    if rms <= EPS or peak <= EPS:
        return 1.0, False, None
    raw = target / rms
    applied = min(raw, ceiling / peak, max_gain)
    return applied, applied < raw - 1e-12, raw


def make_clip(index: int) -> tuple[float, ...]:
    """Frozen harmonic/formant-like one-second surrogate, unique per index."""
    if not 0 <= index < TRAIN_CLIPS + HELD_OUT_CLIPS:
        raise ValueError("clip index outside frozen cohort")
    rng = LCG(SEED_CORPUS + ((index + 1) * 2654435761) & 0xFFFFFFFF)
    f0 = 95.0 + 85.0 * rng.unit()
    phase_a = 2.0 * math.pi * f0 / SAMPLE_RATE_HZ
    phase_b = 2.0 * math.pi * (2.0 * f0) / SAMPLE_RATE_HZ
    syllable_hz = 1.3 + 1.7 * rng.unit()
    offset = math.pi * rng.uniform()
    a = 0.0
    b = 0.0
    out: list[float] = []
    for sample in range(CLIP_SAMPLES):
        time_s = sample / SAMPLE_RATE_HZ
        region = (sample // FRAME_SAMPLES) % 20
        if region in (8, 9, 18, 19):
            value = 0.0018 * rng.uniform()
        elif region in (4, 5, 14, 15):
            value = 0.055 * rng.uniform()
        else:
            envelope = 0.30 + 0.70 * math.sin(
                2.0 * math.pi * syllable_hz * time_s + offset) ** 2
            a += phase_a
            b += phase_b
            if a >= 2.0 * math.pi:
                a -= 2.0 * math.pi
            if b >= 2.0 * math.pi:
                b -= 2.0 * math.pi
            value = 0.30 * envelope * (
                math.sin(a) + 0.45 * math.sin(b) + 0.05 * rng.uniform())
        out.append(max(-0.9, min(0.9, value)))
    return tuple(out)


def perturb(base: Sequence[float], index: int) -> tuple[tuple[float, ...], float, bool]:
    """Apply frozen gain perturbation and an optional overloaded transient."""
    rng = LCG((SEED_CORPUS ^ 0x5BD1E995) + index * 7919)
    perturbation_db = PERTURBATION_DB_MIN + (
        PERTURBATION_DB_MAX - PERTURBATION_DB_MIN) * rng.unit()
    factor = 10.0 ** (perturbation_db / 20.0)
    wave = [v * factor for v in base]
    spiked = index % 7 == 3
    if spiked:
        center = 4000 + (index % 11) * 37
        sign = 1.0 if index % 2 == 0 else -1.0
        wave[center] += sign * 1.1
        wave[center - 1] += sign * 0.24
        wave[center + 1] += sign * 0.24
    return tuple(wave), perturbation_db, spiked


@dataclass(frozen=True)
class GainConfig:
    epoch: int = 1
    first_input_sample: int = 0
    target_rms: float = TARGET_RMS
    ceiling: float = PEAK_CEILING
    max_gain: float = MAX_GAIN
    attack_frames: int = 2
    release_frames: int = 8

    def check(self) -> Optional[str]:
        if not isinstance(self.epoch, int) or isinstance(self.epoch, bool) or self.epoch < 1:
            return "invalid_epoch"
        if (not isinstance(self.first_input_sample, int)
                or isinstance(self.first_input_sample, bool)
                or self.first_input_sample < 0):
            return "invalid_first_input_sample"
        if not math.isfinite(self.target_rms) or self.target_rms <= 0.0:
            return "invalid_target_rms"
        if not math.isfinite(self.ceiling) or self.ceiling <= 0.0:
            return "invalid_ceiling"
        if not math.isfinite(self.max_gain) or self.max_gain <= 0.0:
            return "invalid_max_gain"
        if not 1 <= self.attack_frames <= 64 or not 1 <= self.release_frames <= 64:
            return "invalid_envelope_rate"
        return None


@dataclass
class FrameResult:
    status: str
    samples: tuple[float, ...] = ()
    produced_count: int = 0
    valid_count: int = 0
    flags: int = 0
    epoch: int = 0
    source_first_sample: int = 0
    gain: float = 0.0
    cap_engaged: bool = False
    peak_abs: float = 0.0
    finite: bool = True
    reason: str = ""


class StaticGainSession:
    """Python model of a v0 inline static-gain provider at the facade boundary.

    One call consumes exactly one padded 160-sample frame and produces one
    160-sample frame with ``source_first_sample = first_input_sample`` (D=0).
    Static strategies hold one calibrated/fixed gain for the whole session.
    The ``envelope_agc`` strategy is a stateful control, not the static
    reference: it is included to expose attack/release and peak-protection
    interaction and state transitions.
    """

    def __init__(self, config: Optional[GainConfig] = None,
                 strategy: str = STRATEGY_TARGET,
                 fixed_gain: Optional[float] = None) -> None:
        self.config = config or GainConfig()
        reason = self.config.check()
        if reason:
            raise ValueError(reason)
        if strategy not in STRATEGIES:
            raise ValueError("unknown_gain_strategy")
        if strategy not in STATIC_STRATEGIES and fixed_gain is not None:
            raise ValueError("envelope_has_no_fixed_gain")
        if strategy in STATIC_STRATEGIES:
            if fixed_gain is None:
                fixed_gain = 1.0  # uncalibrated identity until set_fixed_gain
            elif not math.isfinite(fixed_gain) or fixed_gain < 0.0:
                raise ValueError("invalid_fixed_gain")
        self.strategy = strategy
        self.fixed_gain = fixed_gain
        self.closed = False
        self.final_accepted = False
        self.epoch = self.config.epoch
        self.next_input = self.config.first_input_sample
        self.envelope: Optional[float] = None
        self.previous_gain: Optional[float] = None
        self.stats: dict[str, int] = {
            "accepted_frames": 0,
            "accepted_valid_samples": 0,
            "produced_frames": 0,
            "cap_engaged_frames": 0,
            "clipped_samples": 0,
            "nonfinite_outputs": 0,
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
            "backend_failures": 0,
        }

    def _reject(self, reason: str) -> FrameResult:
        key = "rejected_" + reason
        if key in self.stats:
            self.stats[key] += 1
        return FrameResult(status=key, reason=reason)

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
        if not isinstance(valid, int) or isinstance(valid, bool) or not 1 <= valid <= FRAME_SAMPLES:
            return "shape"
        if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
            return "shape"
        if len(values) != FRAME_SAMPLES:
            return "short" if len(values) < FRAME_SAMPLES else "shape"
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in values):
            return "shape"
        as_float = tuple(float(v) for v in values)
        if any(not math.isfinite(v) for v in as_float):
            return "nonfinite"
        if valid < FRAME_SAMPLES and not bool(frame.get("final", False)):
            return "short"
        if any(v != 0.0 for v in as_float[valid:]):
            return "bad_padding"
        return None

    def _frame_gain(self, values: Sequence[float], valid: int) -> tuple[float, bool, Optional[float]]:
        if self.strategy == STRATEGY_NO_GAIN:
            return 1.0, False, None
        if self.strategy in (STRATEGY_TARGET, STRATEGY_RIDGE):
            assert self.fixed_gain is not None
            return self.fixed_gain, False, None
        portion = values[:valid]
        rms = math.sqrt(sum(v * v for v in portion) / valid)
        peak = max((abs(v) for v in portion), default=0.0)
        if self.envelope is None:
            self.envelope = rms
        rate = (self.config.attack_frames if rms > self.envelope
                else self.config.release_frames)
        self.envelope += (rms - self.envelope) / rate
        raw = self.config.target_rms / max(self.envelope, EPS)
        desired = min(raw, self.config.ceiling / max(peak, EPS),
                      self.config.max_gain)
        if self.previous_gain is None:
            applied = desired
        else:
            rate = (self.config.attack_frames if desired > self.previous_gain
                    else self.config.release_frames)
            applied = self.previous_gain + (desired - self.previous_gain) / rate
        # Peak protection is applied after smoothing; a decaying envelope can
        # otherwise momentarily exceed the ceiling. This interaction is the
        # interacting-nonlinearity probe, not a hidden default.
        protected = min(applied, self.config.ceiling / max(peak, EPS),
                        self.config.max_gain)
        self.previous_gain = protected
        return protected, protected < raw - 1e-12, raw

    def process(self, frame: Any) -> FrameResult:
        if self.closed:
            return self._reject("closed")
        if self.final_accepted:
            return self._reject("after_final")
        problem = self._valid_frame(frame)
        if problem:
            return self._reject(problem)
        if frame.get("epoch", self.epoch) != self.epoch:
            return self._reject("stale_epoch")
        start = int(frame["first_input_sample"])
        if self.stats["accepted_frames"] and start == self.next_input - FRAME_SAMPLES:
            return self._reject("duplicate")
        if self.stats["accepted_frames"] and start < self.next_input:
            return self._reject("out_of_order")
        if start != self.next_input:
            return self._reject("future_packet")

        values = tuple(float(v) for v in frame["samples"])
        valid = int(frame["valid_count"])
        gain, cap, _raw = self._frame_gain(values, valid)
        output = tuple(gain * v for v in values)
        peak = max((abs(v) for v in output), default=0.0)
        finite = all(math.isfinite(v) for v in output)
        if not finite:
            self.stats["backend_failures"] += 1
            return FrameResult(status="backend_failure_nonfinite",
                               reason="nonfinite_output")
        if self.strategy != STRATEGY_NO_GAIN and peak > self.config.ceiling + 1e-9:
            self.stats["backend_failures"] += 1
            return FrameResult(status="backend_failure_peak",
                               reason="peak_above_ceiling")
        clipped = sum(1 for v in output if abs(v) >= 1.0)
        self.stats["clipped_samples"] += clipped
        if cap:
            self.stats["cap_engaged_frames"] += 1
        self.stats["accepted_frames"] += 1
        self.stats["accepted_valid_samples"] += valid
        self.stats["produced_frames"] += 1
        self.next_input = start + FRAME_SAMPLES
        self.final_accepted = bool(frame.get("final", False))
        return FrameResult(
            status="ok",
            samples=output,
            produced_count=FRAME_SAMPLES,
            valid_count=valid,
            flags=FLAG_FINAL_PADDING
            if self.final_accepted and valid < FRAME_SAMPLES else 0,
            epoch=self.epoch,
            source_first_sample=start - BUFFERING_DELAY_SAMPLES,
            gain=gain,
            cap_engaged=cap,
            peak_abs=peak,
            finite=finite,
        )

    def drain(self) -> list[FrameResult]:
        """Memoryless provider: no buffered audio, drain reports only EOS."""
        if self.closed:
            return [FrameResult(status="rejected_closed", reason="closed")]
        return [FrameResult(status="end_of_stream", produced_count=0,
                            valid_count=0, epoch=self.epoch)]

    def set_fixed_gain(self, gain: float) -> FrameResult:
        if self.closed or self.stats["accepted_frames"]:
            return FrameResult(status="rejected_state", reason="gain_not_calibrated_prepared")
        if self.strategy not in STATIC_STRATEGIES:
            return FrameResult(status="rejected_state", reason="envelope_has_no_fixed_gain")
        if not math.isfinite(gain) or not 0.0 <= gain <= self.config.max_gain:
            return FrameResult(status="rejected_invalid_gain", reason="invalid_gain")
        self.fixed_gain = gain
        return FrameResult(status="ok", gain=gain)

    def reset(self, epoch: int, first_input_sample: int) -> FrameResult:
        if self.closed:
            return self._reject("closed")
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch <= self.epoch:
            return self._reject("stale_epoch")
        if (not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool)
                or first_input_sample < 0):
            return self._reject("shape")
        self.__init__(GainConfig(epoch=epoch,
                                 first_input_sample=first_input_sample,
                                 target_rms=self.config.target_rms,
                                 ceiling=self.config.ceiling,
                                 max_gain=self.config.max_gain,
                                 attack_frames=self.config.attack_frames,
                                 release_frames=self.config.release_frames),
                      strategy=self.strategy,
                      fixed_gain=self.fixed_gain)
        return FrameResult(status="ok", epoch=epoch)

    def close(self) -> None:
        self.closed = True
        self.fixed_gain = None
        self.envelope = None
        self.previous_gain = None


def frames_from_wave(wave: Sequence[float],
                     start: int = 0) -> list[dict[str, Any]]:
    """One padded 160-sample v0 frame per source frame; final marker honored."""
    frames: list[dict[str, Any]] = []
    for offset in range(0, len(wave), FRAME_SAMPLES):
        chunk = wave[offset:offset + FRAME_SAMPLES]
        valid = len(chunk)
        frames.append({
            "first_input_sample": start + offset,
            "samples": tuple(chunk) + (0.0,) * (FRAME_SAMPLES - valid),
            "valid_count": valid,
            "final": valid < FRAME_SAMPLES,
        })
    return frames


def run_stream(wave: Sequence[float], strategy: str,
               fixed_gain: Optional[float] = None,
               config: Optional[GainConfig] = None,
               epoch: int = 1) -> tuple[list[FrameResult], tuple[float, ...]]:
    """Drive one complete v0 stream and reconstruct emitted samples."""
    cfg = config or GainConfig(epoch=epoch)
    session = StaticGainSession(cfg, strategy, fixed_gain)
    results: list[FrameResult] = []
    output: list[float] = []
    try:
        for frame in frames_from_wave(wave, cfg.first_input_sample):
            item = dict(frame)
            item["epoch"] = cfg.epoch
            result = session.process(item)
            if result.status != "ok":
                raise AssertionError(f"process rejected: {result.status}")
            results.append(result)
            output.extend(result.samples)
        drain = session.drain()
        if len(drain) != 1 or drain[0].status != "end_of_stream":
            raise AssertionError("memoryless drain must report one EOS")
    finally:
        session.close()
    return results, tuple(output)


def fit_ridge(train: Sequence[dict[str, float]]) -> dict[str, Any]:
    """Closed-form one-feature ridge on the train split only."""
    xs = [item["x"] for item in train]
    ys = [item["y"] for item in train]
    if len(xs) < 2:
        raise ValueError("ridge needs at least two training items")
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs) + RIDGE_LAMBDA
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    return {
        "lambda": RIDGE_LAMBDA,
        "feature": "log10(measured clip RMS)",
        "label": "log10(applied static gain from direct rule with peak ceiling)",
        "train_items": len(xs),
        "mean_x": r6(mean_x),
        "mean_y": r6(mean_y),
        "slope": r6(slope),
        "intercept": r6(intercept),
        "train_feature_digest": tensor_digest(xs),
        "train_label_digest": tensor_digest(ys),
    }


def predict_log_gain(model: dict[str, Any], rms: float) -> float:
    return float(model["intercept"]) + float(model["slope"]) * math.log10(max(rms, EPS))


def aggregate(items: Sequence[dict[str, Any]], strategy: str) -> dict[str, Any]:
    errors = [item["abs_error_db"][strategy] for item in items]
    signed = [item["signed_error_db"][strategy] for item in items]
    peaks = [item["peak"][strategy] for item in items]
    return {
        "clips": len(items),
        "mean_abs_rms_error_db": r6(sum(errors) / len(errors)),
        "rms_of_rms_error_db": r6(math.sqrt(sum(v * v for v in signed) / len(signed))),
        "mean_signed_rms_error_db": r6(sum(signed) / len(signed)),
        "max_abs_rms_error_db": r6(max(errors)),
        "max_peak": r6(max(peaks)),
        "clipped_samples": sum(item["clipped_samples"][strategy] for item in items),
        "nonfinite_samples": sum(item["nonfinite"][strategy] for item in items),
        "cap_engaged_clips": sum(1 for item in items
                                 if item["cap_engaged"][strategy]),
        "all_finite": all(item["finite"][strategy] for item in items),
    }


def envelope_steps(wave: Sequence[float], config: GainConfig) -> list[float]:
    """First-frame gain trace of the stateful control on a level-step probe."""
    session = StaticGainSession(config, STRATEGY_ENVELOPE)
    gains: list[float] = []
    for frame in frames_from_wave(wave):
        result = session.process(dict(frame))
        if result.status != "ok":
            raise AssertionError(result.status)
        gains.append(r6(result.gain))
    session.close()
    return gains


def steps_wave(levels_db: Sequence[float] = (-42, -36, -30, -24, -18, -12, -6, -12),
               step_frames: int = 25) -> tuple[float, ...]:
    out: list[float] = []
    for level_db in levels_db:
        amplitude = 0.16 * 10.0 ** (level_db / 20.0)
        for index in range(step_frames * FRAME_SAMPLES):
            out.append(amplitude * math.sin(
                2.0 * math.pi * 220.0 * len(out) / SAMPLE_RATE_HZ))
    return tuple(out)


def sweep_wave(frames: int = 200) -> tuple[float, ...]:
    out: list[float] = []
    phase = 0.0
    total = frames * FRAME_SAMPLES
    for index in range(total):
        fraction = index / total
        frequency = 20.0 * (8000.0 / 20.0) ** fraction
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE_HZ
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi
        out.append(0.22 * math.sin(phase))
    return tuple(out)


def impulse_wave(length_frames: int = 50, at: int = 4000,
                 amplitude: float = 0.5) -> tuple[float, ...]:
    wave = [0.0] * (length_frames * FRAME_SAMPLES)
    wave[at] = amplitude
    return tuple(wave)


def silence_wave(length_frames: int = 50) -> tuple[float, ...]:
    return (0.0,) * (length_frames * FRAME_SAMPLES)


def speech_probe(seed: int = 771, frames: int = 125) -> tuple[float, ...]:
    rng = LCG(seed)
    out: list[float] = []
    phase_a = 0.0
    for index in range(frames * FRAME_SAMPLES):
        frame = index // FRAME_SAMPLES
        region = frame % 20
        if region in (8, 9, 18, 19):
            out.append(0.0015 * rng.uniform())
            continue
        phase_a += 2.0 * math.pi * 128.0 / SAMPLE_RATE_HZ
        if phase_a > 2.0 * math.pi:
            phase_a -= 2.0 * math.pi
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 1.9 * index / SAMPLE_RATE_HZ) ** 2
        out.append(0.24 * envelope * (math.sin(phase_a)
                                      + 0.3 * math.sin(2.0 * phase_a)))
    return tuple(out)


def transient_wave(seed: int = 919) -> tuple[float, ...]:
    rng = LCG(seed)
    wave = []
    for index in range(100 * FRAME_SAMPLES):
        value = 0.18 * math.sin(2.0 * math.pi * 180.0 * index / SAMPLE_RATE_HZ)
        value += 0.01 * rng.uniform()
        if 4800 <= index <= 4803:
            value += (2.2, 1.7, -1.3, 0.8)[index - 4800]
        wave.append(value)
    return tuple(wave)


def build_report() -> dict[str, Any]:
    config = GainConfig()
    train: list[dict[str, float]] = []
    for index in range(TRAIN_CLIPS):
        base = make_clip(index)
        wave, perturbation_db, spiked = perturb(base, index)
        features = wave_features(wave)
        exact_rms, exact_peak = exact_wave_stats(wave)
        gain, cap, raw = static_gain(exact_rms, exact_peak)
        train.append({
            "index": float(index),
            "x": math.log10(exact_rms),
            "y": math.log10(gain),
            "perturbation_db": perturbation_db,
            "input_rms_db": features["rms_dbfs"],
            "input_peak": features["peak_abs"],
            "gain": gain,
            "raw_gain": raw if raw is not None else 0.0,
            "cap": 1.0 if cap else 0.0,
            "spiked": 1.0 if spiked else 0.0,
        })
    model = fit_ridge(train)

    held: list[dict[str, Any]] = []
    for index in range(TRAIN_CLIPS, TRAIN_CLIPS + HELD_OUT_CLIPS):
        base = make_clip(index)
        wave, perturbation_db, spiked = perturb(base, index)
        features = wave_features(wave)
        rms, peak = exact_wave_stats(wave)
        target_gain, target_cap, target_raw = static_gain(rms, peak)
        ridge_raw = 10.0 ** predict_log_gain(model, rms)
        ridge_gain = min(ridge_raw, config.ceiling / max(peak, EPS),
                         config.max_gain)
        ridge_cap = ridge_gain < ridge_raw - 1e-12
        gains = {
            STRATEGY_NO_GAIN: 1.0,
            STRATEGY_TARGET: target_gain,
            STRATEGY_RIDGE: ridge_gain,
        }
        errors: dict[str, float] = {}
        signed: dict[str, float] = {}
        peaks: dict[str, float] = {}
        clipped: dict[str, int] = {}
        nonfinite: dict[str, int] = {}
        finite: dict[str, bool] = {}
        out_digest: dict[str, str] = {}
        out_rms: dict[str, float] = {}
        envelope_cap = False
        for strategy in STRATEGIES:
            stream_results, output = run_stream(wave, strategy,
                                                gains.get(strategy))
            if strategy == STRATEGY_ENVELOPE:
                envelope_cap = any(r.cap_engaged for r in stream_results)
            stats = wave_features(output)
            errors[strategy] = r6(abs(stats["rms_dbfs"] - TARGET_RMS_DB))
            signed[strategy] = r6(stats["rms_dbfs"] - TARGET_RMS_DB)
            peaks[strategy] = stats["peak_abs"]
            clipped[strategy] = stats["at_or_above_one_count"]
            nonfinite[strategy] = stats["nonfinite_count"]
            finite[strategy] = stats["finite"]
            out_digest[strategy] = stats["digest"]
            out_rms[strategy] = stats["rms_dbfs"]
        held.append({
            "clip_index": index,
            "perturbation_db": r6(perturbation_db),
            "transient_overload": spiked,
            "input_rms_db": features["rms_dbfs"],
            "input_peak": peak,
            "input_digest": features["digest"],
            "target_raw_gain": r6(target_raw) if target_raw is not None else None,
            "applied_gain": {key: r6(value) for key, value in gains.items()},
            "cap_engaged": {
                STRATEGY_TARGET: target_cap,
                STRATEGY_RIDGE: ridge_cap,
                STRATEGY_NO_GAIN: False,
                STRATEGY_ENVELOPE: envelope_cap,
            },
            "output_rms_db": out_rms,
            "signed_error_db": signed,
            "abs_error_db": errors,
            "peak": peaks,
            "clipped_samples": clipped,
            "nonfinite": nonfinite,
            "finite": finite,
            "output_digest": out_digest,
        })
    aggregates = {strategy: aggregate(held, strategy) for strategy in STRATEGIES}

    comparisons: dict[str, Any] = {}
    regressions: list[dict[str, Any]] = []
    for strategy in (STRATEGY_RIDGE, STRATEGY_NO_GAIN, STRATEGY_ENVELOPE):
        deltas = {
            str(item["clip_index"]): r6(item["abs_error_db"][strategy]
                                        - item["abs_error_db"][STRATEGY_TARGET])
            for item in held
        }
        worse = [key for key, value in deltas.items() if value > 1e-6]
        comparisons[strategy + "_minus_target_rms"] = {
            "mean_abs_error_delta_db": r6(
                aggregates[strategy]["mean_abs_rms_error_db"]
                - aggregates[STRATEGY_TARGET]["mean_abs_rms_error_db"]),
            "worse_clips": len(worse),
            "no_worse_clips": len(deltas) - len(worse),
            "per_clip_delta_db": deltas,
        }
        for item in held:
            delta = item["abs_error_db"][strategy] - item["abs_error_db"][STRATEGY_TARGET]
            if delta > 1e-6:
                regressions.append({
                    "strategy": strategy,
                    "compared_with": STRATEGY_TARGET,
                    "clip_index": item["clip_index"],
                    "metric": "held_out_abs_rms_error_db",
                    "delta": r6(delta),
                    "interpretation": "strategy worse than direct target-RMS rule",
                })
    for item in held:
        if item["transient_overload"] and item["cap_engaged"][STRATEGY_TARGET]:
            regressions.append({
                "strategy": STRATEGY_TARGET,
                "compared_with": "uncapped_target",
                "clip_index": item["clip_index"],
                "metric": "held_out_abs_rms_error_db",
                "delta": item["abs_error_db"][STRATEGY_TARGET],
                "interpretation": "peak ceiling prevents exact RMS target on overloaded synthetic transient",
            })

    # ---------------------------- DSP probes ----------------------------
    probes: dict[str, Any] = {}
    sweep = sweep_wave()
    sweep_features = wave_features(sweep)
    sweep_rms, sweep_peak = exact_wave_stats(sweep)
    sweep_gain = static_gain(sweep_rms, sweep_peak)[0]
    sweep_results, sweep_out = run_stream(sweep, STRATEGY_TARGET, sweep_gain, config)
    band_ratios: list[float] = []
    for band in range(10):
        lo = band * 20
        hi = lo + 20
        in_slice = sweep[lo * FRAME_SAMPLES:hi * FRAME_SAMPLES]
        out_slice = sweep_out[lo * FRAME_SAMPLES:hi * FRAME_SAMPLES]
        in_rms = exact_wave_stats(in_slice)[0]
        out_rms = exact_wave_stats(out_slice)[0]
        band_ratios.append(r6(out_rms / max(in_rms, EPS)))
    probes["sweep"] = {
        "description": "20 Hz to 8 kHz exponential sine sweep, static gain calibrated once from the whole probe.",
        "source_frames": len(sweep) // FRAME_SAMPLES,
        "static_gain": r6(sweep_gain),
        "band_gain_ratios": band_ratios,
        "response_flatness_db": r6(dbfs(max(band_ratios)) - dbfs(min(band_ratios))),
        "frames": len(sweep_results),
        "output": wave_features(sweep_out),
        "cap_engaged_frames": sum(1 for r in sweep_results if r.cap_engaged),
    }

    steps = steps_wave()
    step_gain = static_gain(*exact_wave_stats(steps))[0]
    step_results, step_out = run_stream(steps, STRATEGY_TARGET, step_gain, config)
    static_step_gains = [r6(result.gain) for result in step_results[::FRAME_SAMPLES // 4]]
    envelope_trace = envelope_steps(steps, config)
    probes["steps"] = {
        "description": "Eight 25-frame level steps from -42 dBFS to -6 dBFS and back; static gain cannot track steps.",
        "source_frames": len(steps) // FRAME_SAMPLES,
        "static_gain": r6(step_gain),
        "per_step_input_rms_db": [
            wave_features(steps[i * 25 * FRAME_SAMPLES:(i + 1) * 25 * FRAME_SAMPLES])["rms_dbfs"]
            for i in range(8)],
        "static_gain_trace_sampled": static_step_gains[:8],
        "static_gain_unique_values": len({result.gain for result in step_results}),
        "envelope_control_first_frame_gain_trace": envelope_trace[:48],
        "envelope_control_unique_gain_values": len(set(envelope_trace)),
        "output": wave_features(step_out),
    }

    impulse = impulse_wave()
    impulse_gain = static_gain(*exact_wave_stats(impulse))[0]
    impulse_results, impulse_out = run_stream(impulse, STRATEGY_TARGET,
                                              impulse_gain, config)
    peak_index = max(range(len(impulse_out)), key=lambda i: abs(impulse_out[i]))
    probes["impulse"] = {
        "description": "Isolated impulse at source sample 4000; verifies zero intrinsic delay and one-to-one frame mapping.",
        "source_peak_index": 4000,
        "measured_output_peak_index": peak_index,
        "measured_content_delay_samples": peak_index - 4000,
        "declared_buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "nonzero_output_samples": sum(1 for v in impulse_out if v != 0.0),
        "source_mapping_checks": all(
            result.source_first_sample == frame["first_input_sample"]
            for result, frame in zip(impulse_results, frames_from_wave(impulse))),
        "gain": r6(impulse_gain),
        "output": wave_features(impulse_out),
    }

    silence = silence_wave()
    silence_results, silence_out = run_stream(silence, STRATEGY_TARGET, 1.0, config)
    probes["silence"] = {
        "description": "All-zero stream: undefined RMS falls back to identity gain, not infinity.",
        "fallback_gain": r6(silence_results[0].gain),
        "output_peak": wave_features(silence_out)["peak_abs"],
        "headroom_linear": config.ceiling,
        "nonfinite_count": wave_features(silence_out)["nonfinite_count"],
        "frames": len(silence_results),
    }

    speech = speech_probe()
    speech_gain = static_gain(*exact_wave_stats(speech))[0]
    speech_results, speech_out = run_stream(speech, STRATEGY_TARGET,
                                            speech_gain, config)
    region_rows: list[dict[str, Any]] = []
    for region in range(20):
        lo = region * FRAME_SAMPLES
        hi = lo + FRAME_SAMPLES
        region_rows.append({
            "region": ("pause_floor" if region in (8, 9, 18, 19)
                       else "unvoiced" if region in (4, 5, 14, 15) else "voiced"),
            "input_rms_db": wave_features(speech[lo:hi])["rms_dbfs"],
            "applied_gain": r6(speech_results[region].gain),
        })
    probes["synthetic_speech"] = {
        "description": "Frozen 125-frame harmonic/formant surrogate with voiced, unvoiced and pause-floor regions.",
        "static_gain": r6(speech_gain),
        "unique_gain_values": len({r.gain for r in speech_results}),
        "per_region": region_rows,
        "noise_floor_note": "A single static scalar scales voiced and pause-floor content equally; SNR is unchanged and no noise gating is applied.",
        "output": wave_features(speech_out),
    }

    no_gain_results, no_gain_out = run_stream(speech, STRATEGY_NO_GAIN, 1.0, config)
    probes["no_gain_control"] = {
        "description": "Identity control on the same frozen speech probe; no peak ceiling.",
        "gain": r6(no_gain_results[0].gain),
        "bit_identical_to_input": no_gain_out == speech,
        "output": wave_features(no_gain_out),
        "unique_gain_values": len({r.gain for r in no_gain_results}),
    }

    transient = transient_wave()
    transient_features = wave_features(transient)
    transient_gain, transient_cap, transient_raw = static_gain(
        *exact_wave_stats(transient))
    transient_results, transient_out = run_stream(transient, STRATEGY_TARGET,
                                                  transient_gain, config)
    transient_output_features = wave_features(transient_out)
    probes["headroom_peak"] = {
        "description": "Tone plus frozen overloaded transient; scalar ceiling cap, never hard clipping.",
        "input_peak": transient_features["peak_abs"],
        "raw_gain": r6(transient_raw) if transient_raw is not None else None,
        "applied_gain": r6(transient_gain),
        "cap_engaged": transient_cap,
        "output_peak": transient_output_features["peak_abs"],
        "headroom_linear": r6(config.ceiling
                              - transient_output_features["peak_abs"]),
        "output_at_or_above_one_count": transient_output_features["at_or_above_one_count"],
        "clipped_frames": sum(1 for r in transient_results
                              if r.peak_abs >= config.ceiling - 1e-9),
    }

    interacting = envelope_steps(transient, config)
    probes["interacting_nonlinearity"] = {
        "description": "Stateful attack/release control plus peak ceiling and gain clamp on the overloaded transient.",
        "first_40_gain_trace": interacting[:40],
        "cap_engaged_frames": sum(1 for g in interacting
                                  if g * transient_features["peak_abs"] >= config.ceiling - 1e-3),
        "unique_gain_values": len(set(interacting)),
        "note": "Smoothing and ceiling interact: the peak cap limits the smoothed target, so the envelope does not reach the RMS target on overloaded frames.",
    }

    # ------------------------ validity and state ------------------------
    final_partial = frames_from_wave(speech[:7 * FRAME_SAMPLES + 37])
    partial_results, partial_out = run_stream(
        speech[:7 * FRAME_SAMPLES + 37], STRATEGY_TARGET, speech_gain, config)
    partial_window = {
        "source_samples": 7 * FRAME_SAMPLES + 37,
        "final_frame_valid_count": final_partial[-1]["valid_count"],
        "final_frame_flagged_final": final_partial[-1]["final"],
        "result_flags": sorted({r.flags for r in partial_results if r.flags}),
        "produced_frames": len(partial_results),
        "valid_content_samples": sum(r.valid_count for r in partial_results),
        "padding_bits_identical": all(
            r.samples[i] == 0.0 for r in partial_results if r.flags
            for i in range(r.valid_count, FRAME_SAMPLES)),
        "output_samples_in_window": len(partial_out),
    }

    short = frames_from_wave(speech[:8 * FRAME_SAMPLES])
    adverse: dict[str, Any] = {}
    probe_session = StaticGainSession(GainConfig(epoch=7),
                                      STRATEGY_TARGET, 1.0)
    baseline = {k: v for k, v in probe_session.stats.items()
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
        result = probe_session.process(frame)
        adverse[name] = {
            "status": result.status,
            "state_unchanged": {k: v for k, v in probe_session.stats.items()
                                if not k.startswith("rejected_")} == baseline,
        }
    probe_session.close()

    order = StaticGainSession(GainConfig(epoch=1), STRATEGY_TARGET, 1.0)
    for frame in short[:2]:
        assert order.process(dict(frame)).status == "ok"
    accepted_after_two = order.stats["accepted_valid_samples"]
    duplicate = order.process(dict(short[1]))
    after_duplicate = order.stats["accepted_valid_samples"]
    out_of_order = order.process(dict(short[0]))
    after_order = order.stats["accepted_valid_samples"]
    recovered = order.process(dict(short[2]))
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
        "first_two_accepted": accepted_after_two == 2 * FRAME_SAMPLES,
        "consistent_counts": order.stats["accepted_valid_samples"]
                             == 3 * FRAME_SAMPLES,
    }
    order.close()
    adverse["closed_rejects_process"] = {
        "status": order.process(dict(short[0])).status,
        "state_unchanged": True,
    }
    final_probe = StaticGainSession(GainConfig(epoch=1), STRATEGY_TARGET, 1.0)
    for frame in frames_from_wave(speech[:8 * FRAME_SAMPLES + 37]):
        final_probe.process(dict(frame))
    adverse["process_after_final"] = {
        "status": final_probe.process(dict(short[0])).status,
        "state_unchanged": final_probe.stats["accepted_valid_samples"]
                           == 8 * FRAME_SAMPLES + 37,
    }
    final_probe.close()

    gain_probe = StaticGainSession(GainConfig(epoch=1), STRATEGY_TARGET)
    for value in (float("nan"), float("inf"), -0.1, config.max_gain + 1.0):
        invalid = gain_probe.set_fixed_gain(value)
        if invalid.status == "ok":
            raise AssertionError("invalid gain accepted")
    adverse["invalid_gain_rejected"] = {
        "status": "rejected_invalid_gain",
        "state_unchanged": (gain_probe.fixed_gain == 1.0
                            and gain_probe.stats["accepted_frames"] == 0),
    }
    gain_probe.close()

    a_results, _ = run_stream(speech[:8 * FRAME_SAMPLES], STRATEGY_TARGET,
                              1.0, config)
    b_results, _ = run_stream(speech[:8 * FRAME_SAMPLES], STRATEGY_TARGET,
                              0.5, config)
    reset_session = StaticGainSession(GainConfig(epoch=1), STRATEGY_TARGET, 1.0)
    for frame in short:
        reset_session.process(dict(frame))
    reset_status = reset_session.reset(2, 0)
    stale_after_reset = reset_session.process({**short[0], "epoch": 1})
    reset_results: list[FrameResult] = []
    for frame in short:
        reset_results.append(reset_session.process({**frame, "epoch": 2}))
    reset_session.close()
    fresh_results, _ = run_stream(speech[:8 * FRAME_SAMPLES], STRATEGY_TARGET,
                                  1.0, config, epoch=2)
    state = {
        "separate_sessions_uncoupled":
            [(r.samples, r.gain) for r in a_results]
            != [(r.samples, r.gain) for r in b_results],
        "reset_accepted": reset_status.status == "ok",
        "stale_epoch_after_reset_rejected":
            stale_after_reset.status == "rejected_stale_epoch",
        "reset_bit_identical_to_fresh_epoch2": [
            (r.samples, r.flags, r.source_first_sample) for r in reset_results
        ] == [(r.samples, r.flags, r.source_first_sample)
              for r in fresh_results],
        "static_gain_invariant_across_frames":
            len({r.gain for r in a_results}) == 1,
        "no_hidden_queue": all(r.produced_count == FRAME_SAMPLES
                               for r in a_results),
        "final_padding_bits_zero": partial_window["padding_bits_identical"],
        "envelope_state_changes_within_stream":
            len(set(envelope_steps(steps, config))) > 1,
    }

    fixture_spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "target_rms_db": TARGET_RMS_DB,
        "peak_ceiling": PEAK_CEILING,
        "max_gain": MAX_GAIN,
        "ridge_lambda": RIDGE_LAMBDA,
        "train_clips": TRAIN_CLIPS,
        "held_out_clips": HELD_OUT_CLIPS,
        "clip_samples": CLIP_SAMPLES,
        "seed": SEED_CORPUS,
        "perturbation_db_range": [PERTURBATION_DB_MIN, PERTURBATION_DB_MAX],
        "source_pins": {pin["path"]: pin["sha256"] for pin in SOURCE_PINS},
        "artifact_pins": {pin["path"]: pin["sha256"] for pin in artifact_pins()},
        "base_commit": BASE_COMMIT,
    }

    all_finite = (all(item["all_finite"] for item in aggregates.values())
                  and probes["impulse"]["output"]["finite"]
                  and probes["synthetic_speech"]["output"]["finite"])
    controls_complete = all(
        item["state_unchanged"] for name, item in adverse.items()
        if name in invalid_frames or name in ("duplicate_packet",
                                              "out_of_order_packet",
                                              "process_after_final"))
    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract": CONTRACT_ID,
        "scope": "optional task-local synthetic static-gain reference; not a release, default or real-audio qualification",
        "profile": "DSP",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "base_commit": BASE_COMMIT,
        "fixture_digest": object_digest(fixture_spec),
        "source_pins": list(SOURCE_PINS),
        "artifact_pins": artifact_pins(),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "samples_per_call": FRAME_SAMPLES,
        },
        "boundary": {
            "provider_id": PROVIDER_ID,
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "default_selected": False,
            "note": "Python model of a v0 inline provider at the public process/drain boundary; no C provider, registry change, public flag or descriptor change.",
        },
        "strategy_settings": {
            "target_rms_db": TARGET_RMS_DB,
            "target_rms_linear": TARGET_RMS,
            "peak_ceiling": PEAK_CEILING,
            "max_gain": MAX_GAIN,
            "ridge_lambda": RIDGE_LAMBDA,
            "envelope_attack_frames": config.attack_frames,
            "envelope_release_frames": config.release_frames,
            "gain_cap_policy": "min(direct_gain, ceiling/input_peak, max_gain); no hard clipping",
        },
        "split": {
            "kind": "deterministic_synthetic_clip_split",
            "seed": SEED_CORPUS,
            "train_clips": TRAIN_CLIPS,
            "held_out_clips": HELD_OUT_CLIPS,
            "train_indices": [0, TRAIN_CLIPS - 1],
            "held_out_indices": [TRAIN_CLIPS, TRAIN_CLIPS + HELD_OUT_CLIPS - 1],
            "overlap": 0,
            "clip_samples": CLIP_SAMPLES,
            "perturbation_db_range": [PERTURBATION_DB_MIN, PERTURBATION_DB_MAX],
            "transient_overload_rule": "clip index % 7 == 3, frozen 1.1-amplitude transient",
            "no_shuffling": True,
        },
        "ridge_fit": model,
        "held_out": {
            "per_clip": held,
            "aggregates": aggregates,
            "comparisons": comparisons,
            "regressions": regressions,
            "all_metrics_available": all(
                item["finite"][strategy] for item in held
                for strategy in STRATEGIES),
        },
        "dsp_probes": probes,
        "final_partial_window": partial_window,
        "adverse": adverse,
        "state": state,
        "controls_complete": controls_complete,
        "all_outputs_finite": all_finite,
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "blockers": [dict(block) for block in QUALIFICATION_BLOCKERS],
        "no_missing_result_qualifies_candidate": True,
    }
    report["qualification_status"] = qualification_state(report)
    return impurity_free(report)


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
    if not all(report["held_out"]["aggregates"][name]["all_finite"]
               for name in STRATEGIES):
        return "not_qualified"
    if not (report["controls_complete"] and report["all_outputs_finite"]
            and all(report["state"].values())):
        return "not_qualified"
    return "proposal_only_synthetic_incomplete"


def impurity_free(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite report value")
    if isinstance(value, dict):
        return {key: impurity_free(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [impurity_free(item) for item in value]
    return value


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + b"\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py <report.json>")
    report = build_report()
    print(f"fixture_digest={report['fixture_digest']}")
    print(f"regressions={len(report['held_out']['regressions'])}")


if __name__ == "__main__":
    main()
