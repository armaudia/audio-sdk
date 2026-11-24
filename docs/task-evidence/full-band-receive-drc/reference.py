# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic full-band receive DRC reference and frozen synthetic fixtures.

This is task-local evidence at a protocol-shaped waveform adapter boundary. It
is causal on the installed 16 kHz/mono/f32/160-sample grid, opt-in, unregistered
and disabled by default. No SDK ABI, descriptor, registry, default or installed
v0 behavior is changed. All signals are generated analytically or with a seeded
LCG; no speech corpus, listening panel, model, licensed runtime or device
measurement is used. Every reported control is SYNTHETIC and non-qualifying.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_CHUNK_SAMPLES = FRAME_SAMPLES * 4
MAX_ABS_INPUT = 4.0
SCHEMA_ID = "audio-sdk/full-band-receive-drc-report/0.1"
ADAPTER_ID = "full-band-receive-drc-reference-v1"
PROVIDER_ID = "full-band-receive-drc-reference-provider/0.1"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
TASK_PREFIX = "docs/task-evidence/full-band-receive-drc/"
TASK = "SDK-FULL-BAND-RECEIVE-DRC-CONTROL"

SOURCE_PINS = {
    "research/listening_intelligibility_20261028.md":
        "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read":
        "934ea753acc6788300a96d413d34fae13f3a32e968f1e397b80edaf940266e21",
    "mutable": True,
    "note": "Mutable board snapshot recorded at task read time; never a gate or a result.",
}

MODE_STAGES = {
    "identity": (False, False),
    "compressor_only": (True, False),
    "limiter_only": (False, True),
    "drc": (True, True),
}
CONFIG_KEYS = (
    "sample_rate_hz", "frame_samples", "max_abs_input", "threshold_db", "ratio",
    "knee_db", "attack_ms", "release_ms", "makeup_db", "ceiling",
    "limiter_attack_ms", "limiter_release_ms",
)
SWEEP_HZ = (125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 7500.0)
LEVEL_DBFS = (-30.0, -18.0, -12.0, -6.0, 0.0)
TMR_DB = (-5.0, 0.0, 5.0)
STEP_ON = 1600
STEP_OFF = 6400


class ConfigError(ValueError):
    pass


class Status(Enum):
    OK = "ok"
    REJECTED_INVALID = "rejected_invalid"
    REJECTED_NONFINITE = "rejected_nonfinite"
    REJECTED_RANGE = "rejected_range"
    REJECTED_SHAPE = "rejected_tensor"
    REJECTED_EPOCH = "rejected_epoch"
    REJECTED_POSITION = "rejected_position"
    REJECTED_SESSION = "rejected_session"
    BLOCKED_MISSING = "blocked_missing_reference"


@dataclass(frozen=True)
class DrcConfig:
    sample_rate_hz: int = SAMPLE_RATE_HZ
    frame_samples: int = FRAME_SAMPLES
    max_abs_input: float = MAX_ABS_INPUT
    threshold_db: float = -18.0
    ratio: float = 3.0
    knee_db: float = 6.0
    attack_ms: float = 10.0
    release_ms: float = 120.0
    makeup_db: float = 2.0
    ceiling: float = 0.95
    limiter_attack_ms: float = 2.0
    limiter_release_ms: float = 60.0

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in CONFIG_KEYS}


DEFAULT_CONFIG = DrcConfig()


def validate_config(value: Any = None) -> DrcConfig:
    """Strictly validate an opt-in task-local configuration."""
    if value is None:
        return DEFAULT_CONFIG
    if not isinstance(value, Mapping):
        raise ConfigError("config_not_object")
    supplied = dict(value)
    if set(supplied) != set(CONFIG_KEYS):
        raise ConfigError("config_keys_mismatch")
    numbers: Dict[str, float] = {}
    for key in CONFIG_KEYS:
        item = supplied[key]
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ConfigError("config_wrong_type:" + key)
        number = float(item)
        if not math.isfinite(number):
            raise ConfigError("config_nonfinite:" + key)
        numbers[key] = number
    if numbers["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ConfigError("config_rate")
    if numbers["frame_samples"] != FRAME_SAMPLES:
        raise ConfigError("config_frame")
    if not 1.0 <= numbers["max_abs_input"] <= 8.0:
        raise ConfigError("config_max_abs_input")
    if not -60.0 <= numbers["threshold_db"] <= 0.0:
        raise ConfigError("config_threshold")
    if not 1.0 <= numbers["ratio"] <= 20.0:
        raise ConfigError("config_ratio")
    if not 0.0 <= numbers["knee_db"] <= 24.0:
        raise ConfigError("config_knee")
    if not 0.1 <= numbers["attack_ms"] <= 200.0:
        raise ConfigError("config_attack")
    if not numbers["attack_ms"] <= numbers["release_ms"] <= 2000.0:
        raise ConfigError("config_release")
    if not -12.0 <= numbers["makeup_db"] <= 12.0:
        raise ConfigError("config_makeup")
    if not 0.1 <= numbers["ceiling"] <= 1.0:
        raise ConfigError("config_ceiling")
    if not 0.01 <= numbers["limiter_attack_ms"] <= 100.0:
        raise ConfigError("config_limiter_attack")
    if not numbers["limiter_attack_ms"] <= numbers["limiter_release_ms"] <= 1000.0:
        raise ConfigError("config_limiter_release")
    return DrcConfig(**{key: int(numbers[key]) if key in ("sample_rate_hz", "frame_samples")
                        else numbers[key] for key in CONFIG_KEYS})


@dataclass
class DrcState:
    epoch: int = 1
    position: int = 0
    compressor_envelope: float = 0.0
    limiter_envelope: float = 0.0
    frames: int = 0
    samples: int = 0
    invalid_count: int = 0
    limiter_ceiling_exceed_count: int = 0
    hard_clip_count: int = 0
    finished: bool = False
    compressor_gain_trace: List[float] = field(default_factory=list)

    def dsp_fields(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "position": self.position,
            "compressor_envelope": self.compressor_envelope,
            "limiter_envelope": self.limiter_envelope,
            "frames": self.frames,
            "samples": self.samples,
            "limiter_ceiling_exceed_count": self.limiter_ceiling_exceed_count,
            "hard_clip_count": self.hard_clip_count,
            "finished": self.finished,
        }

    def snapshot(self) -> Dict[str, Any]:
        result = self.dsp_fields()
        result["invalid_count"] = self.invalid_count
        result["compressor_envelope"] = scorer.r6(self.compressor_envelope)
        result["limiter_envelope"] = scorer.r6(self.limiter_envelope)
        result["gain_trace_samples"] = len(self.compressor_gain_trace)
        return result


class DrcEngine:
    """Causal sample-wise compressor, optional peak limiter and strict state machine."""

    def __init__(self, config: Any = None, mode: str = "drc"):
        self.config = validate_config(config)
        if mode not in MODE_STAGES:
            raise ConfigError("unknown_mode")
        self.mode = mode
        self.state = DrcState()

    @staticmethod
    def _coefficient(milliseconds: float, rate_hz: int) -> float:
        return 1.0 - math.exp(-1.0 / (milliseconds * rate_hz / 1000.0))

    def _compressor_gain_db(self, level_db: float) -> float:
        cfg = self.config
        knee_half = cfg.knee_db / 2.0
        slope = 1.0 - 1.0 / cfg.ratio
        if knee_half == 0.0 or level_db <= cfg.threshold_db - knee_half:
            return 0.0
        if level_db >= cfg.threshold_db + knee_half:
            return -slope * (level_db - cfg.threshold_db)
        offset = level_db - cfg.threshold_db + knee_half
        return -slope * offset * offset / (2.0 * cfg.knee_db)

    def reset(self, epoch: int) -> Status:
        if (isinstance(epoch, bool) or not isinstance(epoch, int)
                or epoch <= self.state.epoch):
            self.state.invalid_count += 1
            return Status.REJECTED_INVALID
        self.state = DrcState(epoch=epoch)
        return Status.OK

    def finish(self) -> Status:
        self.state.finished = True
        return Status.OK

    def process(self, samples: Any, epoch: Optional[int] = None,
                position: Optional[int] = None) -> Tuple[Status, Tuple[float, ...]]:
        state = self.state
        if state.finished:
            state.invalid_count += 1
            return Status.REJECTED_SESSION, ()
        if epoch is not None and (isinstance(epoch, bool) or epoch != state.epoch):
            state.invalid_count += 1
            return Status.REJECTED_EPOCH, ()
        if position is not None and (isinstance(position, bool) or position != state.position):
            state.invalid_count += 1
            return Status.REJECTED_POSITION, ()
        if (not isinstance(samples, (list, tuple)) or not samples
                or len(samples) > MAX_CHUNK_SAMPLES):
            state.invalid_count += 1
            return Status.REJECTED_SHAPE, ()
        values = []
        for value in samples:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                state.invalid_count += 1
                return Status.REJECTED_NONFINITE, ()
            number = float(value)
            if not math.isfinite(number):
                state.invalid_count += 1
                return Status.REJECTED_NONFINITE, ()
            if abs(number) > self.config.max_abs_input:
                state.invalid_count += 1
                return Status.REJECTED_RANGE, ()
            values.append(number)

        cfg = self.config
        do_compressor, do_limiter = MODE_STAGES[self.mode]
        comp_attack = self._coefficient(cfg.attack_ms, cfg.sample_rate_hz)
        comp_release = self._coefficient(cfg.release_ms, cfg.sample_rate_hz)
        limiter_attack = self._coefficient(cfg.limiter_attack_ms, cfg.sample_rate_hz)
        limiter_release = self._coefficient(cfg.limiter_release_ms, cfg.sample_rate_hz)
        output: List[float] = []
        for value in values:
            comp_envelope = state.compressor_envelope
            if do_compressor:
                coefficient = comp_attack if abs(value) > comp_envelope else comp_release
                comp_envelope += coefficient * (abs(value) - comp_envelope)
                level_db = 20.0 * math.log10(max(comp_envelope, 1e-12))
                gain_db = self._compressor_gain_db(level_db) + cfg.makeup_db
                compressor_gain = 10.0 ** (gain_db / 20.0)
                state.compressor_gain_trace.append(compressor_gain)
            else:
                compressor_gain = 1.0
            state.compressor_envelope = comp_envelope
            before_limiter = value * compressor_gain
            if do_limiter:
                coeff = limiter_attack if abs(before_limiter) > state.limiter_envelope \
                    else limiter_release
                state.limiter_envelope += coeff * (abs(before_limiter) - state.limiter_envelope)
                limiter_gain = min(1.0, cfg.ceiling / max(state.limiter_envelope, 1e-12))
            else:
                limiter_gain = 1.0
            limited = before_limiter * limiter_gain
            if abs(limited) > cfg.ceiling:
                state.limiter_ceiling_exceed_count += 1
                limited = math.copysign(cfg.ceiling, limited)
                state.hard_clip_count += 1
            output.append(limited)
        state.position += len(values)
        state.frames += 1
        state.samples += len(values)
        return Status.OK, tuple(output)

    def snapshot(self) -> Dict[str, Any]:
        return self.state.snapshot()


def process_whole_clip(samples: Sequence[float], config: Any = None,
                       mode: str = "drc", chunk_samples: int = FRAME_SAMPLES
                       ) -> Tuple[Status, Tuple[float, ...]]:
    """Process a whole synthetic clip on the 160-sample grid with one engine."""
    if isinstance(chunk_samples, bool) or not isinstance(chunk_samples, int) \
            or not 1 <= chunk_samples <= MAX_CHUNK_SAMPLES:
        raise ConfigError("invalid_chunk")
    engine = DrcEngine(config=config, mode=mode)
    result: List[float] = []
    for start in range(0, len(samples), chunk_samples):
        status, chunk = engine.process(tuple(samples[start:start + chunk_samples]),
                                       epoch=1, position=start)
        if status is not Status.OK:
            return status, ()
        result.extend(chunk)
    return Status.OK, tuple(result)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tensor_digest(samples: Sequence[float]) -> str:
    """F32 little-endian tensor digest, matching the installed fixture format."""
    digest = hashlib.sha256()
    for value in samples:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("nonfinite_tensor")
        digest.update(struct.pack("<f", number))
    return digest.hexdigest()


def lcg_noise(count: int, seed: int) -> Tuple[float, ...]:
    state = seed & 0xFFFFFFFF
    values: List[float] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        values.append(2.0 * state / 4294967296.0 - 1.0)
    return tuple(values)


def sine(frequency_hz: float, count: int, amplitude: float,
         phase: float = 0.0) -> Tuple[float, ...]:
    return tuple(amplitude * math.sin(2.0 * math.pi * frequency_hz * index
                                      / SAMPLE_RATE_HZ + phase)
                 for index in range(count))


def impulse(count: int = 1600, index: int = FRAME_SAMPLES,
            amplitude: float = 0.8) -> Tuple[float, ...]:
    values = [0.0] * count
    values[index] = amplitude
    return tuple(values)


def silence(count: int = 6400) -> Tuple[float, ...]:
    return (0.0,) * count


def sweep(frequency_hz: float, count: int = 3200,
          amplitude: float = 0.04) -> Tuple[float, ...]:
    return sine(frequency_hz, count, amplitude)


def step_fixture(count: int = 16000) -> Tuple[float, ...]:
    if count < STEP_OFF + 1600:
        raise ValueError("step_fixture_too_short")
    return tuple(0.02 if index < STEP_ON or index >= STEP_OFF else 0.6
                 for index in range(count))


def synthetic_speech(count: int = 16000, seed: int = 4101) -> Tuple[float, ...]:
    """Analytic vowel-like source with deterministic syllabic gating; not speech."""
    noise = lcg_noise(count, seed)
    raw: List[float] = []
    phase = 0.0
    for index in range(count):
        time = index / SAMPLE_RATE_HZ
        fundamental = 118.0 + 12.0 * math.sin(2.0 * math.pi * 1.7 * time) \
            + 5.0 * math.sin(2.0 * math.pi * 0.43 * time)
        phase += 2.0 * math.pi * fundamental / SAMPLE_RATE_HZ
        carrier = sum(math.sin(harmonic * phase + 0.31 * harmonic) / harmonic
                      for harmonic in range(1, 7))
        syllable = 0.15 + 0.85 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 2.3 * time - 0.4))
        breath = 0.6 + 0.4 * math.sin(2.0 * math.pi * 0.37 * time)
        raw.append(syllable * breath * carrier + 0.03 * noise[index])
    return scorer.scale_to_rms(raw, 0.12)


def synthetic_masker(count: int = 16000, seed: int = 5201) -> Tuple[float, ...]:
    """Seeded low-pass noise masker; not an environmental recording."""
    noise = lcg_noise(count, seed)
    smoothed: List[float] = []
    previous = 0.0
    for value in noise:
        previous = 0.82 * previous + 0.18 * value
        smoothed.append(previous)
    return scorer.scale_to_rms(smoothed, 0.1)


def near_clip_speech() -> Tuple[float, ...]:
    return scorer.scale_to_rms(synthetic_speech(), 0.34)


def preclipped_speech() -> Tuple[float, ...]:
    source = synthetic_speech()
    peak = scorer.peak_abs(source)
    return tuple(value * 1.4 / peak for value in source)


def causal_probe_signal(count: int = 960) -> Tuple[float, ...]:
    return synthetic_speech(count=count, seed=7331)


def fixture_generators() -> Dict[str, Any]:
    generators: Dict[str, Any] = {
        "clean_speech": synthetic_speech,
        "synthetic_masker": synthetic_masker,
        "near_clip_speech": near_clip_speech,
        "preclipped_speech": preclipped_speech,
        "impulse": impulse,
        "silence": silence,
        "step": step_fixture,
        "causal_probe": causal_probe_signal,
    }
    for frequency in SWEEP_HZ:
        generators["sweep_small_" + str(int(frequency))] = (
            lambda freq=frequency: sweep(freq, amplitude=0.04))
        generators["sweep_high_" + str(int(frequency))] = (
            lambda freq=frequency: sweep(freq, amplitude=0.5))
    return generators


def fixture_digest() -> str:
    """Digest of every frozen synthetic signal and the fixed DRC parameters."""
    digests = {name: tensor_digest(generator())
               for name, generator in fixture_generators().items()}
    digests["config"] = sha256_text(json.dumps(DEFAULT_CONFIG.to_dict(),
                                               sort_keys=True, separators=(",", ":")))
    return sha256_text(json.dumps(digests, sort_keys=True, separators=(",", ":")))


def repeat_probe() -> Dict[str, Any]:
    """Three genuinely cold-start interpreter passes over one pinned probe."""
    code = (
        "import reference\n"
        "probe = reference.causal_probe_signal()\n"
        "status, output = reference.process_whole_clip(probe)\n"
        "assert status is reference.Status.OK\n"
        "print(reference.tensor_digest(output))\n"
    )
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    digests: List[str] = []
    for _ in range(3):
        completed = subprocess.run([sys.executable, "-c", code], cwd=str(HERE),
                                   capture_output=True, text=True, check=True,
                                   env=environment)
        digests.append(completed.stdout.strip())
    probe = causal_probe_signal()
    return {
        "byte_identical": len(set(digests)) == 1,
        "input_digest": tensor_digest(probe),
        "input_samples": len(probe),
        "note": "three fresh Python interpreters, fresh DrcEngine each pass, exact f32 digests",
        "output_digests": digests,
        "runs": 3,
    }


def _status_name(status: Status) -> str:
    return status.value


def _engine_snapshot_after_rejections() -> Dict[str, Any]:
    engine = DrcEngine()
    admitted_status, _ = engine.process((0.01,) * FRAME_SAMPLES, epoch=1, position=0)
    before = engine.state.dsp_fields()
    next_position = engine.state.position
    # Every rejection below must fail validation only. The out-of-range probe
    # uses 5.0, above the configured +-4.0 limit, so it cannot silently advance
    # DSP state.
    cases = {
        "nonfinite": ((float("nan"),) * FRAME_SAMPLES, 1, next_position),
        "out_of_range": ((5.0,) * FRAME_SAMPLES, 1, next_position),
        "wrong_shape": ((0.01,) * (MAX_CHUNK_SAMPLES + 1), 1, next_position),
        "missing_samples": (None, 1, next_position),
        "stale_epoch": ((0.01,) * FRAME_SAMPLES, 2, next_position),
        "stale_position": ((0.01,) * FRAME_SAMPLES, 1, 0),
    }
    results: Dict[str, Any] = {}
    for name, (samples, epoch, position) in cases.items():
        status, _ = engine.process(samples, epoch=epoch, position=position)
        results[name] = _status_name(status)
    unchanged = engine.state.dsp_fields() == before
    final_status = _status_name(engine.finish())
    reuse_status = _status_name(engine.process((0.01,) * FRAME_SAMPLES,
                                               epoch=1, position=next_position)[0])
    return {
        "admitted_first_frame_status": _status_name(admitted_status),
        "dsp_state_unchanged": unchanged,
        "finalize_status": final_status,
        "finished_reuse_status": reuse_status,
        "frame_rejections": results,
        "invalid_count_delta": engine.state.invalid_count,
        "out_of_range_probe_abs": 5.0,
        "max_abs_input": engine.config.max_abs_input,
    }


def _config_rejections() -> Dict[str, Any]:
    cases: Dict[str, Any] = {
        "missing_key": {key: value for key, value in DEFAULT_CONFIG.to_dict().items()
                        if key != "threshold_db"},
        "unknown_key": {**DEFAULT_CONFIG.to_dict(), "extra": 1},
        "wrong_type": {**DEFAULT_CONFIG.to_dict(), "ratio": "three"},
        "out_of_range": {**DEFAULT_CONFIG.to_dict(), "ratio": 0.5},
        "nonfinite": {**DEFAULT_CONFIG.to_dict(), "attack_ms": float("nan")},
    }
    results: Dict[str, Any] = {}
    for name, value in cases.items():
        try:
            validate_config(value)
            results[name] = "accepted"
        except ConfigError as error:
            results[name] = "rejected_invalid:" + str(error).split(":", 1)[0]
    try:
        DrcEngine(mode="unknown")
        results["unknown_mode"] = "accepted"
    except ConfigError:
        results["unknown_mode"] = "rejected_invalid"
    return {key: {"status": value, "controller_created": value == "accepted"}
            for key, value in results.items()}


def _state_transitions() -> Dict[str, Any]:
    probe = causal_probe_signal()
    expected_status, expected = process_whole_clip(probe)
    engine = DrcEngine()
    chunks = [160, 320, 480]
    chunked_output: List[float] = []
    statuses: List[str] = []
    cursor = 0
    for chunk in chunks:
        status, output = engine.process(probe[cursor:cursor + chunk], epoch=1, position=cursor)
        statuses.append(_status_name(status))
        chunked_output.extend(output)
        cursor += chunk
    stale_epoch_status = _status_name(
        engine.process((0.01,) * FRAME_SAMPLES, epoch=2, position=cursor)[0])
    stale_position_status = _status_name(
        engine.process((0.01,) * FRAME_SAMPLES, epoch=1, position=0)[0])
    reset_status = _status_name(engine.reset(epoch=3))
    repeated_reset_status = _status_name(engine.reset(epoch=3))
    replay_engine = DrcEngine()
    replay_status, replay = process_whole_clip(probe)
    equal_chunk_digests = {
        "chunk_160": tensor_digest(process_whole_clip(probe, chunk_samples=160)[1]),
        "chunk_320": tensor_digest(process_whole_clip(probe, chunk_samples=320)[1]),
        "chunk_480": tensor_digest(process_whole_clip(probe, chunk_samples=480)[1]),
        "whole_clip": tensor_digest(expected),
    }
    prefix = probe[:FRAME_SAMPLES * 8]
    future_a = prefix + tuple(0.9 for _ in range(FRAME_SAMPLES))
    future_b = prefix + tuple(-0.9 for _ in range(FRAME_SAMPLES))
    prefix_status, prefix_output = process_whole_clip(prefix)
    status_a, output_a = process_whole_clip(future_a)
    status_b, output_b = process_whole_clip(future_b)
    emitted_count = len(prefix_output)
    other_engine = DrcEngine()
    _, other_output = process_whole_clip(probe)
    return {
        "chunk_statuses": statuses,
        "chunked_matches_whole": tensor_digest(tuple(chunked_output)) == tensor_digest(expected),
        "chunked_digests": equal_chunk_digests,
        "causality_probe": {
            "emitted_frames_compared": 8,
            "future_frame_differs": tensor_digest(output_a) != tensor_digest(output_b),
            "prefix_byte_identical": tensor_digest(output_a[:emitted_count]) ==
                tensor_digest(output_b[:emitted_count]) ==
                tensor_digest(prefix_output),
            "status": "ok" if prefix_status is Status.OK and status_a is Status.OK
                and status_b is Status.OK else "failed",
        },
        "independent_sessions": {
            "outputs_identical_by_deterministic_design":
                tensor_digest(expected) == tensor_digest(other_output),
            "state_isolated": engine.state.epoch == 3 and replay_engine.state.epoch == 1,
            "status": "ok",
        },
        "reset": {
            "replay_digest": tensor_digest(replay),
            "replay_matches_original": tensor_digest(replay) == tensor_digest(expected),
            "repeated_reset_status": repeated_reset_status,
            "reset_epoch": 3,
            "reset_status": reset_status,
            "status": "ok" if reset_status == "ok" and replay_status is Status.OK else "failed",
        },
        "stale_epoch_status": stale_epoch_status,
        "stale_position_status": stale_position_status,
        "status": "ok" if expected_status is Status.OK else _status_name(expected_status),
    }


def _sweep_measurements() -> Dict[str, Any]:
    small_rows: List[Dict[str, Any]] = []
    high_rows: List[Dict[str, Any]] = []
    for frequency in SWEEP_HZ:
        for amplitude, target in ((0.04, small_rows), (0.5, high_rows)):
            signal = sweep(frequency, amplitude=amplitude)
            status, output = process_whole_clip(signal)
            if status is not Status.OK:
                raise RuntimeError("sweep_failed:" + status.value)
            row = {"input": signal, "output": output, "amplitude": amplitude,
                   "frequency_hz": frequency}
            if amplitude == 0.04:
                row["expected_gain_db"] = DEFAULT_CONFIG.makeup_db
            target.append(row)
    return {
        "high_level": scorer.frequency_response(high_rows, SAMPLE_RATE_HZ),
        "note": "Steady-state RMS gain on analytic tones; no spectrum analyzer, speech or listening.",
        "small_signal": scorer.frequency_response(small_rows, SAMPLE_RATE_HZ),
        "status": "measured",
    }


def _step_measurements() -> Dict[str, Any]:
    signal = step_fixture()
    results: Dict[str, Any] = {}
    for mode in ("compressor_only", "drc", "limiter_only"):
        status, output = process_whole_clip(signal, mode=mode)
        if status is not Status.OK:
            raise RuntimeError("step_failed:" + status.value)
        response = scorer.step_response(signal, output, SAMPLE_RATE_HZ, STEP_ON, STEP_OFF)
        if mode == "limiter_only":
            response["note"] = "No limiting is expected at 0.6 peak under a 0.95 ceiling."
        results[mode] = {
            "gain": scorer.gain_metrics(signal, output),
            "headroom": scorer.headroom(output, DEFAULT_CONFIG.ceiling),
            "response": response,
        }
    return {"boundaries_samples": [STEP_ON, STEP_OFF], "modes": results, "status": "measured"}


def _impulse_measurement() -> Dict[str, Any]:
    signal = impulse()
    status, output = process_whole_clip(signal)
    if status is not Status.OK:
        raise RuntimeError("impulse_failed")
    return {
        "delay": scorer.delay_samples(signal, output),
        "headroom": scorer.headroom(output, DEFAULT_CONFIG.ceiling),
        "output_peak_abs": scorer.r6(scorer.peak_abs(output)),
        "status": "measured",
    }


def _silence_measurement() -> Dict[str, Any]:
    signal = silence()
    status, output = process_whole_clip(signal)
    if status is not Status.OK:
        raise RuntimeError("silence_failed")
    return {
        "frames": len(signal) // FRAME_SAMPLES,
        "nonfinite_count": scorer.nonfinite_count(output),
        "output_digest": tensor_digest(output),
        "peak_abs": scorer.r6(scorer.peak_abs(output)),
        "status": "measured",
    }


def _clean_speech_measurement() -> Dict[str, Any]:
    signal = synthetic_speech()
    status, output = process_whole_clip(signal)
    if status is not Status.OK:
        raise RuntimeError("clean_speech_failed")
    return {
        "identity_control": {
            "excluded_from_qualification": True,
            "gain": scorer.gain_metrics(signal, signal),
            "output_digest": tensor_digest(signal),
            "reason": "bit_exact_sanity_control_only",
        },
        "receive_drc": {
            "excluded_from_qualification": False,
            "gain": scorer.gain_metrics(signal, output),
            "headroom": scorer.headroom(output, DEFAULT_CONFIG.ceiling),
            "output_digest": tensor_digest(output),
        },
        "status": "measured",
    }


def _engine_whole_clip(signal: Sequence[float], mode: str = "drc"
                       ) -> Tuple[Status, Tuple[float, ...], Dict[str, Any]]:
    """Process a clip with an owned engine so its true state snapshot is kept."""
    engine = DrcEngine(mode=mode)
    output: List[float] = []
    for start in range(0, len(signal), FRAME_SAMPLES):
        status, chunk = engine.process(tuple(signal[start:start + FRAME_SAMPLES]),
                                       epoch=1, position=start)
        if status is not Status.OK:
            return status, (), engine.snapshot()
        output.extend(chunk)
    return Status.OK, tuple(output), engine.snapshot()


def _clip_measurements() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for name, signal in (("near_clip", near_clip_speech()),
                         ("preclipped_input", preclipped_speech())):
        status, output, snapshot = _engine_whole_clip(signal)
        if status is not Status.OK:
            raise RuntimeError("clip_failed:" + name)
        headroom = scorer.headroom(output, DEFAULT_CONFIG.ceiling)
        results[name] = {
            "engine_hard_clip_count": snapshot["hard_clip_count"],
            "engine_snapshot": snapshot,
            "headroom": headroom,
            "input_peak_abs": scorer.r6(scorer.peak_abs(signal)),
            "output_peak_abs": scorer.r6(scorer.peak_abs(output)),
            "peak_reduction_db": scorer.r6(scorer.db_ratio(
                scorer.peak_abs(output), scorer.peak_abs(signal))),
            "status": "measured",
        }
    return {"modes": results, "status": "measured"}


def _ceiling_clamp_probe() -> Dict[str, Any]:
    """Honest probe: identity/off mode still clamps content above the ceiling."""
    signal = sine(1000.0, 3200, 1.5)
    results: Dict[str, Any] = {}
    for mode in MODE_STAGES:
        status, output, snapshot = _engine_whole_clip(signal, mode=mode)
        if status is not Status.OK:
            raise RuntimeError("ceiling_probe_failed:" + mode)
        results[mode] = {
            "bit_exact_to_input": tensor_digest(output) == tensor_digest(signal),
            "engine_hard_clip_count": snapshot["hard_clip_count"],
            "input_peak_abs": scorer.r6(scorer.peak_abs(signal)),
            "output_peak_abs": scorer.r6(scorer.peak_abs(output)),
            "status": "measured",
        }
    return {
        "claim": ("At peaks above the 0.95 ceiling the identity/off stage is NOT "
                  "bit-exact: the shared safety clamp is applied in every mode."),
        "input_samples": len(signal),
        "modes": results,
        "off_is_bit_exact_below_ceiling": _off_on_probe()["off_is_bit_exact_identity"],
        "status": "measured",
    }


def _level_masker_control() -> Dict[str, Any]:
    clean = synthetic_speech()
    masker = synthetic_masker()
    identity_digest = tensor_digest(clean)
    conditions: Dict[str, Any] = {}
    for level in LEVEL_DBFS:
        target_input = scorer.scale_to_rms(clean, 10.0 ** (level / 20.0))
        input_rms = scorer.rms(target_input)
        status, output = process_whole_clip(target_input)
        if status is not Status.OK:
            raise RuntimeError("level_control_failed")
        gain = scorer.gain_metrics(target_input, output)
        for tmr in TMR_DB:
            metrics = scorer.masker_control_metrics(
                output, masker, tmr, input_rms, target_input)
            key = "level_" + str(int(level)) + "_dbfs_tmr_" + str(int(tmr)) + "_db"
            conditions[key] = {
                "identity_input_digest": identity_digest,
                "input_level_dbfs": level,
                "metrics": metrics,
                "receive_drc_gain": gain,
                "status": "measured" if metrics["status"] == "measured" else "blocked",
            }
    return {
        "claim": "SYNTHETIC level/TMR control only; non-human, non-predictive, non-qualifying.",
        "conditions": conditions,
        "control_design": {
            "identity_target": "unprocessed deterministic speech-like target at the same level",
            "levels_dbfs_rms": list(LEVEL_DBFS),
            "masker": "seeded low-pass LCG noise; not a recorded masker",
            "tmr_db": list(TMR_DB),
            "target_power_restored_before_mixing": True,
        },
        "excluded_from_qualification": True,
        "status": "measured_synthetic_non_qualifying",
    }


def _interacting_configurations() -> Dict[str, Any]:
    signal = near_clip_speech()
    masker = synthetic_masker()
    results: Dict[str, Any] = {}
    for mode in ("identity", "compressor_only", "limiter_only", "drc"):
        status, output, snapshot = _engine_whole_clip(signal, mode=mode)
        if status is not Status.OK:
            raise RuntimeError("interaction_failed:" + mode)
        head = scorer.headroom(output, DEFAULT_CONFIG.ceiling)
        entry = {
            "engine_hard_clip_count": snapshot["hard_clip_count"],
            "gain": scorer.gain_metrics(signal, output),
            "headroom": head,
            "mode": mode,
            "output_digest": tensor_digest(output),
        }
        if mode == "drc":
            mixed = scorer.mix_at_tmr(output, masker, 0.0, target_rms=scorer.rms(signal))
            entry["masker_control"] = {
                "measured_tmr_db": scorer.r6(mixed["measured_tmr_db"]),
                "mixture_headroom": scorer.headroom(mixed["mixture"]),
                "requested_tmr_db": 0.0,
                "status": "measured_synthetic_non_qualifying",
            }
        results[mode] = entry
    return {
        "claim": "Compressor, limiter and receiver-side masker control interact on synthetic signals only.",
        "modes": results,
        "status": "measured",
    }


def _off_on_probe() -> Dict[str, Any]:
    probe = causal_probe_signal()
    off_status, off = process_whole_clip(probe, mode="identity")
    on_status, on = process_whole_clip(probe, mode="drc")
    return {
        "input_digest": tensor_digest(probe),
        "input_samples": len(probe),
        "off_is_bit_exact_identity": tensor_digest(off) == tensor_digest(probe),
        "off_output_digest": tensor_digest(off),
        "on_differs_from_off": tensor_digest(on) != tensor_digest(off),
        "on_output_digest": tensor_digest(on),
        "status": "ok" if off_status is Status.OK and on_status is Status.OK else "failed",
    }


ARTIFACT_FILES = (
    "reference.py", "scorer.py", "run.py", "fixture.py", "test_reference.py",
    "verify.py", "check_licensing.py", "contract.json", "adapter.json", "provider.json",
)

QUALIFICATION_GATES = (
    {
        "id": "authorized_real_listening",
        "status": "blocked",
        "reason": "No listener panel, hearing profile, listening-effort measure or consented real-speech test exists in this task-local package.",
        "reopen": "Run an independently reviewed, consented listening study on rights-qualified speech with a declared analysis plan.",
    },
    {
        "id": "real_speech_paired_cohort",
        "status": "blocked",
        "reason": "No corpus, permitted real speech, STOI/ESTOI scorer run or held-out paired cohort is used; the pinned research document is context only.",
        "reopen": "Freeze a rights-cleared paired cohort, masker set, level grid and scoring protocol, then report paired results independently.",
    },
    {
        "id": "target_runtime_pacing",
        "status": "blocked",
        "reason": "Only deterministic Python waveform processing is exercised; no target-device CPU, memory, deadline or paced 160-sample-grid evidence exists.",
        "reopen": "Measure the exact installed implementation on the target host under pacing, load and declared resource limits.",
    },
    {
        "id": "provider_intake_and_exposure",
        "status": "blocked",
        "reason": "The conceptual provider is unregistered, OFF by default and has empty descriptor settings; no SDK ABI, registry, default or public catalog change is made.",
        "reopen": "Complete opt-in provider intake with independent review, SPDX/license checks and exact-head verification before any exposure.",
    },
    {
        "id": "representative_synthetic_control_fidelity",
        "status": "blocked",
        "reason": "The level/masker control uses analytic speech-like tones and seeded low-pass noise, not recorded maskers or a validated intelligibility predictor.",
        "reopen": "Reproduce the control on a permitted paired corpus with an independently pinned scorer before treating any score as a selection signal.",
    },
)


def artifact_pins() -> Dict[str, str]:
    """Digests of task-local implementation and manifest bytes (no self-pin)."""
    return {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in ARTIFACT_FILES
    }


def _regression(entry_id: str, condition: str, metric: str,
                observed: Optional[float], baseline: Optional[float],
                interpretation: str) -> Dict[str, Any]:
    return {
        "baseline": baseline,
        "condition": condition,
        "delta": scorer.delta_opt(observed, baseline),
        "entry_id": entry_id,
        "excluded_from_qualification": True,
        "interpretation": interpretation,
        "metric": metric,
        "observed": observed,
    }


def _regressions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Record adverse or losing synthetic observations verbatim; never filter."""
    out: List[Dict[str, Any]] = []
    clean_gain = payload["measurements"]["clean_speech"]["receive_drc"]["gain"]
    out.append(_regression(
        "clean_speech_rms_loss", "clean_speech_synthetic", "rms_gain_db",
        clean_gain["rms_gain_db"], 0.0,
        "Receive DRC lowers synthetic speech RMS versus the bit-exact identity control."))
    out.append(_regression(
        "clean_speech_peak_loss", "clean_speech_synthetic", "peak_gain_db",
        clean_gain["peak_gain_db"], 0.0,
        "Peak level is reduced; waveform shape is not preserved."))
    responses = payload["measurements"]["steps"]["modes"]["drc"]["response"]
    out.append(_regression(
        "step_level_drop", "step_drc", "gain_db_during_minus_before",
        scorer.r6(responses["gain_db_during"] - responses["gain_db_before"]), 0.0,
        "The high step is attenuated strongly; gain recovery after the step is incomplete."))
    out.append(_regression(
        "attack_slower_than_configured", "step_drc", "attack_ms",
        responses["attack_ms"], DEFAULT_CONFIG.attack_ms,
        "Windowed step estimator reports a slower attack than the configured 10 ms."))
    out.append(_regression(
        "release_slower_than_configured", "step_drc", "release_ms",
        responses["release_ms"], DEFAULT_CONFIG.release_ms,
        "Windowed step estimator reports a slower release than the configured 120 ms."))
    small = {row["frequency_hz"]: row["gain_db"]
             for row in payload["measurements"]["sweeps"]["small_signal"]}
    high = payload["measurements"]["sweeps"]["high_level"]
    worst = min(((row["gain_db"] - small[row["frequency_hz"]], row["frequency_hz"])
                 for row in high if row["gain_db"] is not None
                 and small.get(row["frequency_hz"]) is not None),
                key=lambda pair: pair[0])
    out.append(_regression(
        "high_level_sweep_gain_reduction", "sweep_" + str(int(worst[1])) + "_hz",
        "gain_db_vs_small_signal", scorer.r6(worst[0]), 0.0,
        "Large-amplitude tones are compressed by up to this much versus small-signal gain."))
    for name in ("near_clip", "preclipped_input"):
        entry = payload["measurements"]["clip_and_headroom"]["modes"][name]
        out.append(_regression(
            name + "_peak_reduction", name, "peak_reduction_db",
            entry["peak_reduction_db"], 0.0,
            "Output peak is lower than input peak; intended level management is still a measured level change."))
    for mode in ("identity", "limiter_only"):
        probe = payload["ceiling_clamp_probe"]["modes"][mode]
        if not probe["bit_exact_to_input"] or probe["engine_hard_clip_count"] > 0:
            out.append(_regression(
                "ceiling_clamp_" + mode, "above_ceiling_sine_" + mode,
                "hard_clip_count", float(probe["engine_hard_clip_count"]), 0.0,
                "Even the off/identity stage clamps content above the shared 0.95 ceiling; "
                "bit-exact identity holds only below the ceiling."))
    conditions = payload["near_end_listening_baseline_synthetic_control"]["conditions"]
    worst_headroom = min((values["metrics"]["mixture_headroom_to_full_scale_db"], key)
                         for key, values in conditions.items()
                         if values["metrics"]["mixture_headroom_to_full_scale_db"] is not None)
    out.append(_regression(
        "masker_control_headroom_deficit", worst_headroom[1],
        "mixture_headroom_to_full_scale_db", worst_headroom[0], 0.0,
        "Equal-power restoration after compression can drive the synthetic mixture above full scale."))
    over_scale = [key for key, values in conditions.items()
                  if values["metrics"]["mixture_peak_abs"] >= 1.0]
    if over_scale:
        out.append({
            "condition": "level_and_tmr_grid",
            "count": len(over_scale),
            "entry_id": "masker_mixture_over_full_scale",
            "excluded_from_qualification": True,
            "interpretation": "Mixture peak reached or exceeded 1.0 in these synthetic conditions.",
            "items": sorted(over_scale),
        })
    band_deltas = [(values["metrics"]["delta_mixture_high_over_low_db"], key)
                   for key, values in conditions.items()
                   if values["metrics"]["delta_mixture_high_over_low_db"] is not None]
    if band_deltas:
        worst_band = min(band_deltas)
        if worst_band[0] < 0:
            out.append(_regression(
                "masker_high_band_energy_loss", worst_band[1],
                "delta_mixture_high_over_low_db", worst_band[0], 0.0,
                "Negative delta means less high-frequency band energy than the identity target control."))
    emi_deltas = [(values["metrics"]["delta_mixture_envelope_modulation_index"], key)
                  for key, values in conditions.items()
                  if values["metrics"]["delta_mixture_envelope_modulation_index"] is not None]
    if emi_deltas:
        worst_emi = min(emi_deltas)
        if worst_emi[0] < 0:
            out.append(_regression(
                "masker_envelope_modulation_loss", worst_emi[1],
                "delta_mixture_envelope_modulation_index", worst_emi[0], 0.0,
                "Negative delta means lower envelope modulation than the identity target control."))
    interactions = payload["interacting_nonlinear_configurations"]["modes"]
    for mode in ("identity", "limiter_only"):
        clips = interactions[mode]["engine_hard_clip_count"]
        if clips > 0:
            out.append(_regression(
                "interacting_mode_clamps_" + mode, mode, "engine_hard_clip_count",
                float(clips), 0.0,
                "Near-clip input is clamped at the ceiling by the shared safety path in this stage combination."))
    return out


def build_report() -> Dict[str, Any]:
    """Build the complete canonical synthetic evidence report."""
    payload: Dict[str, Any] = {
        "adapter": {
            "identity": ADAPTER_ID,
            "protocol_version": 1,
            "registration": "unregistered-developer-only",
            "supported_controls": list(MODE_STAGES),
        },
        "adverse": {
            "config_rejections": _config_rejections(),
            "frame_rejections": _engine_snapshot_after_rejections(),
            "missing_reference": {
                "excluded_from_qualification": True,
                "metrics": None,
                "reason": "missing_reference",
                "status": "blocked",
            },
            "status": "recorded",
        },
        "alignment_and_state": {
            "causal_content_delay_samples": 0,
            "duration_equal": True,
            "state_transitions": _state_transitions(),
            "status": "ok",
        },
        "artifact_pins": {},
        "board_snapshot": BOARD_SNAPSHOT,
        "boundary_pins": BOUNDARY_PINS,
        "config": {
            **DEFAULT_CONFIG.to_dict(),
            "limiter_enabled_by_default": False,
            "mode_stages": {name: list(stages) for name, stages in MODE_STAGES.items()},
            "processing": "causal sample-wise envelope detection, soft-knee full-band compressor, optional peak limiter",
        },
        "contract": "audio-sdk/full-band-receive-drc/0.1",
        "dsp_profile": {
            "claim": "dsp acceptance structure applied to frozen synthetic fixtures only",
            "mapped_cases": {
                "clean_speech_synthetic": "measurements.clean_speech",
                "impulses": "measurements.impulse",
                "intelligibility_or_load_control": "near_end_listening_baseline_synthetic_control",
                "silence": "measurements.silence",
                "steps": "measurements.steps",
                "sweeps": "measurements.sweeps",
            },
            "measured": ["attack_release", "delay", "frequency_response", "gain",
                         "headroom", "numerical_behavior"],
            "not_reported": ["human intelligibility", "real-speech STOI/ESTOI", "MOS",
                             "target-device timing", "release qualification"],
            "profile": "dsp",
            "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "state_transitions": "alignment_and_state.state_transitions",
            "interacting_nonlinear_configurations": "interacting_nonlinear_configurations",
        },
        "fixture_digest": fixture_digest(),
        "format": {
            "channels": 1,
            "content_delay_samples": 0,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": FRAME_SAMPLES,
            "max_abs_input": MAX_ABS_INPUT,
            "processing_mode": "causal_frame_streaming",
            "realtime_v0_provider": False,
            "sample_format": "f32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "interacting_nonlinear_configurations": _interacting_configurations(),
        "measurements": {
            "clean_speech": _clean_speech_measurement(),
            "clip_and_headroom": _clip_measurements(),
            "impulse": _impulse_measurement(),
            "silence": _silence_measurement(),
            "steps": _step_measurements(),
            "sweeps": _sweep_measurements(),
        },
        "near_end_listening_baseline_synthetic_control": _level_masker_control(),
        "off_on_probe": _off_on_probe(),
        "provider": {
            "c_abi_or_sdk_default_change": False,
            "default_enabled": False,
            "descriptor_settings": {},
            "identity": PROVIDER_ID,
            "manifest": "provider.json",
            "opt_in_required": True,
            "registered": False,
        },
        "qualification": {
            "all_required_synthetic_results_present": True,
            "decision": "DEFER",
            "excluded_from_qualification": [
                "all adverse controls", "bit-exact identity control",
                "missing-reference blocked case", "synthetic level/masker control",
            ],
            "no_missing_result_may_qualify": True,
            "processor_exposure": "deferred_until_independent_review",
            "readiness": "incomplete",
            "reasons": [
                "fully synthetic analytic and seeded-noise fixtures only",
                "no authorized listening, real speech, corpus or intelligibility prediction",
                "no target-device CPU, memory, deadline or pacing result",
                "no provider intake, descriptor, registry or public catalog review",
                "opt-in unregistered reference with no installed behavior change",
            ],
            "required_results": {
                "adverse_controls": True,
                "attack_release": True,
                "clean_speech_synthetic": True,
                "delay_and_alignment": True,
                "frequency_response": True,
                "gain_and_headroom": True,
                "interacting_nonlinear_configurations": True,
                "level_and_masker_controls": True,
                "nonfinite_and_clipping": True,
                "state_transitions": True,
            },
            "status": "not_qualified",
        },
        "remaining_gates": [
            "Authorized listening protocol with licensed real speech, listeners and declared analysis.",
            "Held-out paired real-speech benchmark with frozen content, masks and level controls.",
            "Target-device causal CPU, memory, deadline and pacing evidence on the 160-sample grid.",
            "Provider intake, license, descriptor, registry and public catalog review before any exposure.",
            "Exact-head independent review and hosted CI for any future processor exposure.",
        ],
        "repeatability": repeat_probe(),
        "schema_id": SCHEMA_ID,
        "scorer": {
            "crosscheck": "Deterministic self-consistency only; no external oracle, STOI, ESTOI or MOS.",
            "metrics": ["gain", "frequency_response", "attack_release", "headroom",
                        "delay", "nonfinite", "band_energy", "envelope_modulation_index"],
            "scorer_id": scorer.SCORER_ID,
            "status": "dependency_free",
        },
        "scope": ("Synthetic task-local receive DRC evidence at an opt-in protocol-shaped "
                  "waveform adapter boundary; no public-surface, installed-behavior, "
                  "listening, device, model or release claim."),
        "source_evidence_statements": [
            "research/listening_intelligibility_20261028.md is pinned as context only. Its "
            "source-reported objective predictor values are NOT reproduced, reused, pooled "
            "or claimed in this package; no numeric listening result is imported here.",
            "That source reports no listener study, hearing profile, listening-effort measure "
            "or broad held-out benchmark and selects no deployment candidate; authorized "
            "listening remains a separate blocked gate.",
            "This package reproduces only the protocol shape (identity and DRC controls, "
            "level and masker sweeps, equal target-power restoration) with synthetic "
            "instrumented metrics; it produces no intelligibility, quality or release score.",
        ],
        "source_pins": SOURCE_PINS,
        "status": "proposal_only_not_qualified",
    }
    payload["artifact_pins"] = artifact_pins()
    payload["ceiling_clamp_probe"] = _ceiling_clamp_probe()
    payload["gates"] = [dict(gate) for gate in QUALIFICATION_GATES]
    payload["regressions"] = _regressions(payload)
    payload["regression_count"] = len(payload["regressions"])
    payload["candidate_status"] = "proposal_only_not_qualified"
    payload["qualification_status"] = "not_qualified"
    payload["no_missing_result_qualifies_candidate"] = True
    return payload


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {k: _normalize_negzero(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(v) for v in value]
    return value


def canonical_report(report: Mapping[str, Any]) -> Tuple[str, str]:
    normalized = _normalize_negzero(report)
    text = json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
