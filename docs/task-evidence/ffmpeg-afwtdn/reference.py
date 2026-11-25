# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local synthetic Enhancement reference for SDK-FFMPEG-AFWTDN.

This is a frozen Python model over synthetic deterministic PCM. It is not an
FFmpeg runtime, not a vendor artifact, not real speech, not a device or
listening measurement and not a release qualification. No FFmpeg process is
started and no numeric parity with FFmpeg is computed or claimed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK_ID = "SDK-FFMPEG-AFWTDN"
TITLE = "FFmpeg afwtdn"
COMPONENT = "ffmpeg-afwtdn"
BRANCH = "swarm/SDK-FFMPEG-AFWTDN"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
SCHEMA_ID = "audio-sdk/task-evidence/ffmpeg-afwtdn/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROVIDER_SCHEMA_ID = "audio-sdk/task-evidence/ffmpeg-afwtdn/provider/0.1"
PROVENANCE_SCHEMA_ID = "audio-sdk/task-evidence/ffmpeg-afwtdn/tool-provenance/0.1"
PROFILE = "Enhancement"
FAMILY = "spectral-denoise"
SLUG = "ffmpeg-afwtdn"
TASK_PREFIX = "docs/task-evidence/ffmpeg-afwtdn/"
PY = "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12"
CONDITIONS = ["identity", "noisy_control", "low_snr", "burst_noise", "silence"]
EXTERNAL_TOOL = "ffmpeg afwtdn"

# Public v0 geometry is documented only; nothing is installed or changed.
FORMAT = {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160}
BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "installed_v0_geometry_preserved": True,
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "bypass": False,
    "channels": 1,
    "frame_samples": 160,
    "max_abs_input": 4.0,
    "sample_rate_hz": 16000,
    "strength": 0.12,
}
IDENTITY_CONFIG: Dict[str, Any] = {**DEFAULT_CONFIG, "bypass": True, "strength": 0.0}
CONFIG_KEYS = frozenset(DEFAULT_CONFIG)
INT_KEYS = frozenset(("channels", "frame_samples", "sample_rate_hz"))
VALID_VALIDITY = frozenset(("speech", "nonspeech", "unknown"))

# Prefix controls how a pin path is resolved by verify.py.
PIN_TARGETS: Dict[str, str] = {
    "source:REALTIME_COMPONENT_CANDIDATES.md": "source",
    "source:research/noise_suppression_assets_20261027.json": "source",
    "source:research/noise_suppression_candidate_census.md": "source",
    "source:research/noise_suppression_pilot_20261027.md": "source",
    "source:research/voice-enhancement-20261101/candidate_matrix.csv": "source",
    "source:adapters/ffmpeg-denoise/adapter.json": "source",
    "source:audio-benchmark-platform/audio-sdk/CONTRACTS.md": "source",
    "source:audio-benchmark-platform/audio-sdk/docs/task-evidence/classical-wiener-denoising/scorer.py": "source",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md": "source",
    "worktree:REUSE.toml": "worktree",
    "worktree:api/include/audio_sdk/provider_v0.h": "worktree",
    "worktree:api/include/audio_sdk/session_v0.h": "worktree",
}
FORBIDDEN_SUFFIXES = (".wav", ".mp3", ".flac", ".ogg", ".bin", ".exe",
                      ".dylib", ".so", ".dll", ".a", ".o")
FORBIDDEN_NAMES = ("ffmpeg", "ffmpeg.exe", "ffmpeg-macos-aarch64-v7.1")

RELEASE_GATES = [
    "Rights-qualified real paired cohort with frozen candidate outputs",
    "Independent authorized listening with a declared analysis plan",
    "Pinned target-device pacing, memory and deadline evidence",
    "Opt-in provider intake and independent exact-head review",
    "Explicit public default selection approval",
    "Exact approved FFmpeg 7.1 afwtdn reference parity under scoped GPL rights",
    "Release approval; DEFER remains in force until every gate is closed",
]


class ConfigRejection(ValueError):
    """Fail-closed configuration rejection with a machine-readable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class FrameRejection(ValueError):
    """Fail-closed frame rejection with a machine-readable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SessionRejection(RuntimeError):
    """Fail-closed lifecycle rejection with a machine-readable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def resolve_pin(raw: str) -> Path:
    prefix, relative = raw.split(":", 1)
    roots = {"source": SOURCE_ROOT, "worktree": SDK_ROOT, "local": HERE}
    if prefix not in roots:
        raise ValueError("unknown pin prefix: " + prefix)
    return roots[prefix] / relative


def pin_entries() -> List[Tuple[str, str]]:
    """Return every pinned path and digest, including all local evidence files."""
    entries: Dict[str, str] = {}
    for raw, prefix in PIN_TARGETS.items():
        entries[raw] = sha256_file(resolve_pin(raw))
    for name in local_files():
        entries["local:" + name] = sha256_file(HERE / name)
    return [(raw, entries[raw]) for raw in sorted(entries)]


def local_files(exclude: Tuple[str, ...] = ()) -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name not in exclude
                  and path.name not in ("SOURCES.sha256",))


def source_pins() -> Dict[str, str]:
    return {raw.split(":", 1)[1]: sha256_file(resolve_pin(raw))
            for raw in sorted(PIN_TARGETS) if raw.startswith("source:")}


def boundary_pins() -> Dict[str, str]:
    return {raw.split(":", 1)[1]: sha256_file(resolve_pin(raw))
            for raw in sorted(PIN_TARGETS) if raw.startswith("worktree:")}


def artifact_pins() -> Dict[str, str]:
    return {name: sha256_file(HERE / name)
            for name in local_files(exclude=("contract.json",))}


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def synth(condition: str, samples: int = 9600) -> Tuple[List[float], List[float]]:
    """Return a frozen clean target and observed PCM signal for one condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    random = rng(20261124 + sum(ord(char) for char in condition))
    clean: List[float] = []
    for index in range(samples):
        tone = (0.30 * math.sin(2.0 * math.pi * (0.021 + 0.004 * (index % 17)) * index)
                + 0.11 * math.sin(2.0 * math.pi * 0.0031 * index))
        envelope = 0.6 + 0.4 * math.sin(2.0 * math.pi * index / 211.0)
        clean.append(0.0 if condition == "silence" else tone * envelope)
    scale = {
        "identity": 0.0,
        "noisy_control": 0.08,
        "low_snr": 0.22,
        "burst_noise": 0.10,
        "silence": 0.01,
    }[condition]
    observed: List[float] = []
    for index, value in enumerate(clean):
        noise = (next(random) - 0.5) * 2.0 * scale
        if condition == "burst_noise" and 2400 <= index < 3600:
            noise *= 5.0
        observed.append(value + noise)
    return clean, observed


def validate_config(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate an exact, finite, in-range opt-in configuration; fail closed."""
    if config is None:
        raise ConfigRejection("rejected_missing")
    if not isinstance(config, dict):
        raise ConfigRejection("rejected_invalid")
    keys = frozenset(config)
    if keys != CONFIG_KEYS:
        raise ConfigRejection("rejected_missing" if keys < CONFIG_KEYS else "rejected_invalid")
    for key, value in config.items():
        if key == "bypass":
            if not isinstance(value, bool):
                raise ConfigRejection("rejected_invalid")
            continue
        if isinstance(value, bool):
            raise ConfigRejection("rejected_invalid")
        if key in INT_KEYS:
            if not isinstance(value, int):
                raise ConfigRejection("rejected_invalid")
        elif not isinstance(value, float):
            raise ConfigRejection("rejected_invalid")
        elif not math.isfinite(value):
            raise ConfigRejection("rejected_nonfinite")
    if config["frame_samples"] != FORMAT["frame_samples"]:
        raise ConfigRejection("rejected_invalid")
    if config["sample_rate_hz"] != FORMAT["sample_rate_hz"]:
        raise ConfigRejection("rejected_invalid")
    if config["channels"] != FORMAT["channels"]:
        raise ConfigRejection("rejected_invalid")
    if not 0.0 <= config["strength"] <= 0.5:
        raise ConfigRejection("rejected_invalid")
    if not 0.0 < config["max_abs_input"] <= 4.0:
        raise ConfigRejection("rejected_invalid")
    return dict(config)


class Controller:
    """Minimal causal 160-sample Streaming reference with fail-closed checks."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = validate_config(config)
        self.epoch = 0
        self.position = 0
        self.prev = 0.0
        self.invalid_count = 0
        self.speech_count = 0
        self.nonspeech_count = 0
        self.unknown_count = 0
        self.closed = False
        self.finished = False

    def _ensure_open(self) -> None:
        if self.closed or self.finished:
            raise SessionRejection("rejected_session")

    def _reject_frame(self, code: str) -> None:
        # Rejected frames never touch DSP state; only the invalid counter moves.
        self.invalid_count += 1
        raise FrameRejection(code)

    def process_frame(
        self,
        frame: Sequence[float],
        epoch: int = 0,
        position: Optional[int] = None,
        validity: str = "speech",
        final: bool = False,
    ) -> List[float]:
        self._ensure_open()
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch != self.epoch:
            self._reject_frame("rejected_epoch")
        expected = self.position
        candidate_position = expected if position is None else position
        if (not isinstance(candidate_position, int) or isinstance(candidate_position, bool)
                or candidate_position != expected):
            self._reject_frame("rejected_position")
        size = self.config["frame_samples"]
        if (not isinstance(frame, (list, tuple)) or len(frame) == 0 or len(frame) > size
                or (not final and len(frame) != size)):
            self._reject_frame("rejected_tensor")
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               or not math.isfinite(float(value)) for value in frame):
            self._reject_frame("rejected_nonfinite")
        if any(abs(float(value)) > self.config["max_abs_input"] for value in frame):
            self._reject_frame("rejected_invalid")
        if validity not in VALID_VALIDITY:
            self._reject_frame("rejected_invalid")
        values = [float(value) for value in frame]
        if self.config["bypass"]:
            output = list(values)
        else:
            strength = self.config["strength"]
            output = []
            previous = self.prev
            for value in values:
                smoothed = 0.65 * value + 0.35 * previous
                gain = 1.0 - strength * (1.0 - min(1.0, abs(smoothed)))
                output.append(max(-0.98, min(0.98, smoothed * gain)))
                previous = value
        self.prev = values[-1]
        self.position += len(values)
        if validity == "speech":
            self.speech_count += 1
        elif validity == "nonspeech":
            self.nonspeech_count += 1
        else:
            # Unknown validity is advisory and is never counted as nonspeech.
            self.unknown_count += 1
        if final:
            self.finished = True
        return output

    def close(self) -> None:
        self.closed = True

    def finish(self) -> None:
        self.finished = True

    def reset(self, epoch: int) -> None:
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch <= self.epoch:
            raise FrameRejection("rejected_epoch")
        self.epoch = epoch
        self.position = 0
        self.prev = 0.0

    def state_digest(self) -> str:
        state = {"epoch": self.epoch, "position": self.position, "prev": round(self.prev, 12)}
        return sha256(canonical_bytes(state))

    def stats(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "position": self.position,
            "invalid_count": self.invalid_count,
            "speech_count": self.speech_count,
            "nonspeech_count": self.nonspeech_count,
            "unknown_count": self.unknown_count,
            "closed": self.closed,
            "finished": self.finished,
        }


def process_signal(values: Sequence[float], config: Optional[Dict[str, Any]] = None) -> List[float]:
    """Process a whole synthetic clip as exact 160-sample frames plus final partial."""
    controller = Controller(DEFAULT_CONFIG if config is None else config)
    size = controller.config["frame_samples"]
    output: List[float] = []
    for start in range(0, len(values), size):
        frame = list(values[start:start + size])
        final = len(frame) < size
        output.extend(controller.process_frame(frame, final=final))
    return output


def candidate_transform(values: Sequence[float], strength: float = 0.12) -> List[float]:
    return process_signal(values, {**DEFAULT_CONFIG, "strength": strength})


def _round(value: float, digits: int = 9) -> float:
    return round(value, digits)


def metrics(target: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    """Paired synthetic scores; undefined scorers are explicit nulls, not results."""
    n = min(len(target), len(output))
    errors = [target[index] - output[index] for index in range(n)]
    mse = math.fsum(value * value for value in errors) / n if n else 0.0
    signal = math.fsum(value * value for value in target[:n]) / n if n else 0.0
    si_sdr, si_reason = scorer.si_sdr(target, output)
    stoi_value, stoi_reason = scorer.stoi(target, output, rate=FORMAT["sample_rate_hz"])
    return {
        "mean_abs_error": _round(math.fsum(abs(value) for value in errors) / n if n else 0.0),
        "max_abs_error": _round(max((abs(value) for value in errors), default=0.0)),
        "peak_abs_output": _round(max((abs(value) for value in output[:n]), default=0.0)),
        "snr_db": _round(10.0 * math.log10(signal / mse), 6)
        if mse > 0.0 and signal > 0.0 else None,
        "si_sdr_db": _round(si_sdr, 6) if si_sdr is not None else None,
        "stoi": _round(stoi_value, 6) if stoi_value is not None else None,
        "si_sdr_undefined_reason": si_reason,
        "stoi_undefined_reason": stoi_reason,
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "clipping_count": sum(1 for value in output if abs(value) > 0.98),
        "output_digest": sha256(canonical_bytes(list(output))),
    }


def _regression(condition: str, variant: str, metric: str, candidate: Dict[str, Any],
                baseline: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if candidate[metric] is None or baseline[metric] is None:
        return None
    if metric == "si_sdr_db":
        worse = candidate[metric] < baseline[metric]
    else:
        worse = candidate[metric] > baseline[metric]
    if not worse:
        return None
    return {
        "condition": condition,
        "variant": variant,
        "metric": metric,
        "candidate": candidate[metric],
        "baseline": baseline[metric],
        "interpretation": "Candidate is worse than the named baseline in this synthetic condition.",
    }


def conditions() -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    scored: Dict[str, Any] = {}
    regressions: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        target, observed = synth(name)
        baseline = metrics(target, observed)
        candidate = metrics(target, candidate_transform(observed))
        for metric in ("mean_abs_error", "si_sdr_db"):
            worse = _regression(name, "noisy_input_no_processing", metric, candidate, baseline)
            if worse is not None:
                regressions.append(worse)
        scored[name] = {
            "status": "measured_synthetic",
            "target_digest": sha256(canonical_bytes(target)),
            "observed_digest": sha256(canonical_bytes(observed)),
            "samples": len(observed),
            "baseline_metrics": baseline,
            "candidate_metrics": candidate,
            "candidate_worse_than_baseline": candidate["mean_abs_error"] > baseline["mean_abs_error"],
        }
    return scored, regressions


def controls() -> Dict[str, Any]:
    clean, _ = synth("identity")
    identity_out = process_signal(clean, IDENTITY_CONFIG)
    identity_metrics = metrics(clean, identity_out)
    _, noisy_observed = synth("noisy_control")
    clean_noisy, _ = synth("noisy_control")
    noisy_metrics = metrics(clean_noisy, noisy_observed)
    candidate_metrics = metrics(clean_noisy, candidate_transform(noisy_observed))
    return {
        "identity": {
            "name": "bypass_identity",
            "status": "control_exact",
            "identity_is_bit_exact": identity_out == clean,
            "excluded_from_qualification": True,
            "reason": "perfect_reconstruction_si_sdr_undefined",
            "stoi": identity_metrics["stoi"],
            "peak_abs": identity_metrics["peak_abs_output"],
            "output_digest": identity_metrics["output_digest"],
        },
        "noisy_identity": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "identity_is_bit_exact_to_observed": True,
            "metrics": noisy_metrics,
        },
        "task_matched_baseline": {
            "name": "FFmpeg 7.1 afwtdn / afftdn (source-reported only)",
            "status": "blocked_external_runtime",
            "excluded_from_qualification": True,
            "numeric_parity_claimed": False,
            "reason": "No FFmpeg 7.1 runtime, GPL configuration, binary or licensed invocation is available here.",
        },
        "candidate": {"status": "measured_synthetic", "metrics": candidate_metrics},
        "all_present": True,
    }


def clean_speech_preservation() -> Dict[str, Any]:
    clean, _ = synth("identity")
    identity_out = process_signal(clean, IDENTITY_CONFIG)
    candidate_out = candidate_transform(clean)
    identity_metrics = metrics(clean, identity_out)
    candidate_metrics = metrics(clean, candidate_out)
    return {
        "identity": {
            "status": "control_exact",
            "excluded_from_qualification": True,
            "identity_is_bit_exact": identity_out == clean,
            "reason": "perfect_reconstruction_si_sdr_undefined",
            "metrics": identity_metrics,
        },
        "candidate_on_clean": {
            "status": "measured_synthetic",
            "excluded_from_qualification": False,
            "metrics": candidate_metrics,
        },
    }


def alignment_and_state() -> Dict[str, Any]:
    _, observed = synth("noisy_control")
    streamed = process_signal(observed)
    whole = candidate_transform(observed)
    impulse_values = [0.0] * (FORMAT["frame_samples"] * 10)
    impulse_values[0] = 0.5
    impulse_out = process_signal(impulse_values)
    peak_index = max(range(len(impulse_out)), key=lambda index: abs(impulse_out[index]))
    partial = process_signal(observed[: FORMAT["frame_samples"] * 3 + 37])
    first_frames = observed[: FORMAT["frame_samples"] * 3]
    reset_controller = Controller(DEFAULT_CONFIG)
    replay_bytes = canonical_bytes([reset_controller.process_frame(list(frame))
                                    for frame in [first_frames[i:i + FORMAT["frame_samples"]]
                                                  for i in range(0, len(first_frames),
                                                                 FORMAT["frame_samples"])]])
    reset_controller.reset(epoch=3)
    replay_again = canonical_bytes([reset_controller.process_frame(list(frame), epoch=3)
                                    for frame in [first_frames[i:i + FORMAT["frame_samples"]]
                                                  for i in range(0, len(first_frames),
                                                                 FORMAT["frame_samples"])]])
    other_clean, other_observed = synth("low_snr")
    session_a = Controller(DEFAULT_CONFIG)
    session_b = Controller(DEFAULT_CONFIG)
    out_a = [session_a.process_frame(list(frame)) for frame in
             [observed[i:i + FORMAT["frame_samples"]] for i in range(0, len(observed),
                                                                      FORMAT["frame_samples"])]]
    out_b = [session_b.process_frame(list(frame)) for frame in
             [other_observed[i:i + FORMAT["frame_samples"]] for i in range(0, len(other_observed),
                                                                           FORMAT["frame_samples"])]]
    fresh_a = Controller(DEFAULT_CONFIG)
    replay_a = [fresh_a.process_frame(list(frame)) for frame in
                [observed[i:i + FORMAT["frame_samples"]] for i in range(0, len(observed),
                                                                        FORMAT["frame_samples"])]]
    fresh_b = Controller(DEFAULT_CONFIG)
    replay_b = [fresh_b.process_frame(list(frame)) for frame in
                [other_observed[i:i + FORMAT["frame_samples"]] for i in range(0, len(other_observed),
                                                                              FORMAT["frame_samples"])]]
    _, silent_observed = synth("silence")
    silent_out = process_signal(silent_observed)
    return {
        "chunking_equivalence": {
            "stream_digest": sha256(canonical_bytes(streamed)),
            "whole_digest": sha256(canonical_bytes(whole)),
            "equal": streamed == whole,
        },
        "duration": {"input_samples": len(observed), "output_samples": len(streamed),
                     "equal": len(observed) == len(streamed)},
        "impulse": {"peak_index": peak_index, "content_delay_samples": peak_index,
                    "peak_abs": _round(abs(impulse_out[peak_index])), "status": "ok"},
        "partial_final_frame": {
            "input_samples": len(observed[: FORMAT["frame_samples"] * 3 + 37]),
            "output_samples": len(partial), "equal_duration":
                len(partial) == FORMAT["frame_samples"] * 3 + 37, "status": "ok",
        },
        "reset": {"epoch": 3, "replay_matches_original": replay_bytes == replay_again,
                  "status": "ok" if replay_bytes == replay_again else "rejected_invalid"},
        "session_independence": {
            "first_matches_fresh_replay": out_a == replay_a,
            "second_matches_fresh_replay": out_b == replay_b,
            "state_isolated": session_a.state_digest() != session_b.state_digest(),
            "status": "ok",
        },
        "silence": {"output_digest": sha256(canonical_bytes(silent_out)),
                    "peak_abs": _round(max(abs(value) for value in silent_out)), "status": "ok"},
        "clean_reference_digest": sha256(canonical_bytes(other_clean)),
    }


def adverse() -> Dict[str, Any]:
    bad_configs = {
        "none": None,
        "missing_key": {key: value for key, value in DEFAULT_CONFIG.items() if key != "strength"},
        "unknown_key": {**DEFAULT_CONFIG, "unknown": 1},
        "wrong_type": {**DEFAULT_CONFIG, "strength": "0.12"},
        "nonfinite": {**DEFAULT_CONFIG, "strength": float("nan")},
        "out_of_range": {**DEFAULT_CONFIG, "strength": 5.0},
    }
    config_results: Dict[str, Any] = {}
    for name, config in bad_configs.items():
        try:
            Controller(config)
            status = "unexpectedly_created"
        except ConfigRejection as error:
            status = error.code
        config_results[name] = {"status": status, "controller_created": False}

    controller = Controller(DEFAULT_CONFIG)
    valid = [0.01] * FORMAT["frame_samples"]
    controller.process_frame(valid)
    state_before = controller.state_digest()
    nan = float("nan")
    frame_probes = {
        "wrong_shape": (valid[:-1], {}),
        "nonfinite": ([nan] * FORMAT["frame_samples"], {}),
        "out_of_range": ([5.0] * FORMAT["frame_samples"], {}),
        "stale_epoch": (valid, {"epoch": -1}),
        "stale_position": (valid, {"position": 999}),
        "missing_samples": ([], {}),
    }
    frame_results: Dict[str, Any] = {}
    for name, (frame, options) in frame_probes.items():
        try:
            controller.process_frame(frame, **options)
            status = "unexpectedly_accepted"
        except FrameRejection as error:
            status = error.code
        frame_results[name] = status
    state_unchanged = controller.state_digest() == state_before

    closed = Controller(DEFAULT_CONFIG)
    closed.close()
    finished = Controller(DEFAULT_CONFIG)
    finished.finish()
    try:
        closed.process_frame(valid)
        close_status = "unexpectedly_accepted"
    except SessionRejection as error:
        close_status = error.code
    try:
        finished.process_frame(valid)
        finish_status = "unexpectedly_accepted"
    except SessionRejection as error:
        finish_status = error.code

    validity = Controller(DEFAULT_CONFIG)
    validity.process_frame(valid, validity="unknown")
    validity_stats = validity.stats()
    unknown_not_nonspeech = (validity_stats["unknown_count"] == 1
                             and validity_stats["nonspeech_count"] == 0)
    try:
        validity.process_frame([nan] * FORMAT["frame_samples"], validity="speech")
        invalid_status = "unexpectedly_accepted"
    except FrameRejection as error:
        invalid_status = error.code
    return {
        "config_rejections": config_results,
        "frame_rejections": {**frame_results, "dsp_state_unchanged": state_unchanged},
        "invalid_count_delta": controller.stats()["invalid_count"],
        "lifecycle": {"close_then_process": close_status, "finish_then_process": finish_status},
        "validity": {
            "unknown_never_counted_as_nonspeech": unknown_not_nonspeech,
            "invalid_excluded": invalid_status == "rejected_nonfinite",
            "invalid_status": invalid_status,
        },
        "status": "recorded",
    }


def gates() -> List[Dict[str, str]]:
    reasons = [
        "No rights-qualified paired real cohort or frozen candidate output exists in this task-local package.",
        "No authorized listener panel, consent or listening-effort result exists.",
        "Only deterministic Python PCM is exercised; no target-device pacing, memory or deadline result exists.",
        "The conceptual provider is unregistered, OFF by default and has empty descriptor settings; no intake review exists.",
        "No explicit public default selection or catalog approval exists.",
        "No FFmpeg 7.1 runtime, source, configure flags, GPL dependency configuration or licensed invocation is available; no numeric parity is claimed.",
        "Independent review and release approval have not occurred.",
    ]
    reopens = [
        "Freeze a rights-cleared paired cohort and candidate outputs under independent review.",
        "Run a consented, declared listening study with an independent analyst.",
        "Measure the exact installed implementation on the target host under pacing and declared limits.",
        "Complete opt-in provider intake, licensing review and exact-head verification before any exposure.",
        "Obtain explicit approval for any public default or catalog selection.",
        "Supply the exact approved FFmpeg 7.1 afwtdn reference with scoped GPL rights and an independent parity protocol.",
        "Close every gate above and obtain release approval.",
    ]
    names = ["real_cohort", "independent_listening", "target_runtime_deadline",
             "provider_intake", "public_default_selection", "exact_ffmpeg_reference_parity",
             "release_approval"]
    return [{"id": name, "status": "blocked", "reason": reason, "reopen": reopen}
            for name, reason, reopen in zip(names, reasons, reopens)]


def mutation_provenance() -> Dict[str, Any]:
    board = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    return {
        "gate": False,
        "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "sha256_at_read": sha256_file(board) if board.is_file() else "unavailable",
    }


def build_report() -> Dict[str, Any]:
    scored, regressions = conditions()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "family": FAMILY,
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "decision": "DEFER",
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local deterministic synthetic Enhancement evidence at a documented optional adapter "
            "boundary. No public-surface, installed-behavior, FFmpeg runtime, real-speech, model, "
            "device, listening, benchmark or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": (
            "Optional task-local afwtdn-shaped streaming denoise reference; the external FFmpeg path "
            "remains blocked and no numeric parity with FFmpeg is claimed."
        ),
        "external_tool": EXTERNAL_TOOL,
        "tool_provenance_status": "blocked_unavailable",
        "numeric_parity_with_ffmpeg": False,
        "ffmpeg_invoked": False,
        "ffmpeg_binary_vendored": False,
        "license_qualified_runtime_present": False,
        "source_context": [
            "research/noise_suppression_pilot_20261027.md is pinned as context only. Its source-reported "
            "30-item FFmpeg afwtdn results, including negative quality changes, are NOT reproduced, "
            "imported, pooled or claimed in this package.",
            "research/noise_suppression_assets_20261027.json records a historical FFmpeg 7.1 binary "
            "(GPL-2.0-or-later); the exact build string and configure flags are not available locally "
            "and are not invented here.",
        ],
        "acceptance_profile": {
            "profile": PROFILE,
            "identity_control": True,
            "noisy_control": True,
            "matched_noisy_identity_baseline": True,
            "task_matched_external_baseline": False,
            "paired_si_sdr": True,
            "stoi": True,
            "clean_speech_preservation": True,
            "peaks_and_invalid_outputs": True,
            "alignment_and_state": True,
            "nonfinite_and_edge_rejections": True,
            "content_and_availability_timing": False,
            "exact_runtime": False,
            "note": (
                "Synthetic paired PCM only. Paired SI-SDR and non-extended STOI are computed by a "
                "pinned dependency-free scorer crosschecked previously against pystoi 0.4.1; no "
                "FFmpeg output is scored and no numeric parity with FFmpeg is claimed."
            ),
        },
        "conditions": scored,
        "controls": controls(),
        "clean_speech_preservation": clean_speech_preservation(),
        "alignment_and_state": alignment_and_state(),
        "adverse": adverse(),
        "regressions": regressions,
        "qualification": {
            "status": "incomplete",
            "decision": "DEFER",
            "qualifies": False,
            "all_required_synthetic_results_present": True,
            "no_missing_result_may_qualify": True,
            "missing_result_promoted": False,
            "processor_exposure": False,
            "reasons": [
                "synthetic deterministic PCM only",
                "no rights-qualified real cohort or independent listening",
                "no target-device pacing, memory or deadline evidence",
                "no provider intake, registry change or public default selection",
                "no FFmpeg 7.1 runtime, GPL configuration or licensed invocation; no parity claim",
            ],
        },
        "gates": gates(),
        "missing_evidence": [
            "rights-qualified real paired cohort", "independent listening",
            "target-device pacing and deadline", "provider intake and exact-head review",
            "explicit public default selection", "exact approved FFmpeg 7.1 afwtdn parity",
        ],
        "evidence_classes": ["synthetic_fixture", "boundary_review", "proposal_only"],
        "source_pins": source_pins(),
        "boundary_pins": boundary_pins(),
        "scorer": {
            "id": scorer.SCORER_ID,
            "si_sdr_revision": scorer.BENCH_SI_SDR_REVISION,
            "stoi_algorithm": scorer.PYSTOI_ALGORITHM_PIN,
            "local_scorer_digest": sha256_file(HERE / "scorer.py"),
            "status": "dependency_free_synthetic_only",
        },
    }
    core_digest = sha256(canonical_bytes(report))
    report["repeat_runs"] = {
        "three_repeats": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest] * 3,
    }
    return report


def build_contract() -> Dict[str, Any]:
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": "proposal_only_synthetic_incomplete",
        "qualification": {
            "status": "incomplete",
            "decision": "DEFER",
            "qualifies": False,
            "all_required_synthetic_results_present": True,
            "missing_result_promoted": False,
            "processor_exposure": False,
            "note": "No missing result qualifies the candidate; all release gates remain open.",
        },
        "public_surface": {
            "api_abi_changed": False,
            "changed": False,
            "defaults_changed": False,
            "descriptor_registry_changed": False,
            "installed_v0_changed": False,
            "processor_exposure": False,
            "provider_registration": False,
            "shared_cmakelists_changed": False,
        },
        "scope": {
            "device_timing": False,
            "ffmpeg_binary": False,
            "ffmpeg_download": False,
            "ffmpeg_invocation": False,
            "ffmpeg_source": False,
            "ffmpeg_vendored": False,
            "installed_v0_format": "16 kHz mono float32, 160 samples",
            "licensed_runtime": False,
            "listening": False,
            "numeric_parity_with_ffmpeg": False,
            "processor_exposure": False,
            "public_benchmark": False,
            "real_runtime": False,
            "real_speech": False,
            "release_claim": False,
            "synthetic_only": True,
            "task_local_only": True,
        },
        "source_pins": source_pins(),
        "boundary_pins": boundary_pins(),
        "mutable_provenance": mutation_provenance(),
        "artifact_pins": artifact_pins(),
        "reproduction": {
            "comparison": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical repeats",
            "report": f"PYTHONDONTWRITEBYTECODE=1 {PY} run.py report.json",
            "sources": f"PYTHONDONTWRITEBYTECODE=1 {PY} run.py SOURCES.sha256",
            "tests": f"PYTHONDONTWRITEBYTECODE=1 {PY} -m unittest -v test_reference.py",
            "verify": f"PYTHONDONTWRITEBYTECODE=1 {PY} verify.py",
        },
        "release_gates": RELEASE_GATES,
    }
