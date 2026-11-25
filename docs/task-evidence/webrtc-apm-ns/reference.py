# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, model-free synthetic noise-suppression reference evidence.

This is a *proposal-only* WebRTC-APM-NS-shaped reference. It does not contain,
link, download or emulate the WebRTC APM runtime; the algorithm below is an
explicitly synthetic decision-directed Wiener-style suppressor with a frozen
noise-only calibration prefix. All scores are paired against generated clean
references and are valid only for this synthetic cohort.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Dict, List, Optional, Sequence, Tuple

import fixture
import scorer

ROOT = Path(__file__).resolve().parent
TASK_ID = "SDK-WEBRTC-APM-NS"
CONTRACT_ID = "audio-sdk/webrtc-apm-ns/0.1"
ADAPTER_ID = "webrtc-apm-ns-task-local-evidence-v1"
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FFT_SIZE = 256
FFT_BINS = FFT_SIZE // 2 + 1
NOISE_CALIBRATION_FRAMES = 10
CANDIDATE_VARIANT = "webrtc_ns_l2"
BASELINE_VARIANT = "spectral_subtraction"
CONTROL_VARIANT = "noisy_identity"

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "adapters/webrtc-ns/adapter.json":
        "42aac7a2a0f5709e24785eb87d5922fdd30cabadd54336604ff739dc70fa874a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
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
    "sha256_at_read": "b3e8aa913076c0b0496756cdbd1b717cc9f7e65206824198b33278e70c935294",
    "mutable": True,
    "qualifies_evidence": False,
}

PROCESS_VARIANTS = (
    CONTROL_VARIANT,
    BASELINE_VARIANT,
    "webrtc_ns_l1",
    CANDIDATE_VARIANT,
    "webrtc_ns_l3",
)
LEVEL_FLOORS = {"webrtc_ns_l1": 0.55, CANDIDATE_VARIANT: 0.40, "webrtc_ns_l3": 0.25}
ARTIFACT_FILES = (
    "README.md", "adapter.json", "check_licensing.py", "contract.json", "fixture.py",
    "provider.json", "reference.py", "run.py", "scorer.py", "test_reference.py", "verify.py",
)
DEFAULT_CONFIG: Dict[str, Any] = {
    "fft_size": FFT_SIZE,
    "noise_calibration_frames": NOISE_CALIBRATION_FRAMES,
    "decision_alpha": 0.98,
    "candidate_oversubtraction": 2.0,
    "noise_floor": 1e-10,
    "baseline_oversubtract": 2.0,
    "baseline_gain_floor": 0.04,
    "max_abs_input": 4.0,
}
_NUMERIC_RANGES = {
    "fft_size": (FFT_SIZE, FFT_SIZE),
    "noise_calibration_frames": (1, 40),
    "decision_alpha": (0.0, 0.999),
    "candidate_oversubtraction": (0.5, 3.0),
    "noise_floor": (1e-14, 1e-6),
    "baseline_oversubtract": (0.5, 4.0),
    "baseline_gain_floor": (0.0, 0.25),
    "max_abs_input": (0.25, 16.0),
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected item is ever scored as a success."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse JSON strictly; NaN/Infinity and duplicate keys are not accepted."""
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant,
                      object_pairs_hook=unique_pairs)


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest_values(values: Sequence[float]) -> str:
    payload = struct.pack("<%dd" % len(values), *[float(value) for value in values])
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if config is None:
        return dict(DEFAULT_CONFIG)
    if not isinstance(config, dict) or set(config) != set(DEFAULT_CONFIG):
        raise ReferenceError("invalid_config_keys")
    for key, expected in DEFAULT_CONFIG.items():
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ReferenceError("invalid_config_type:" + key)
        low, high = _NUMERIC_RANGES[key]
        if not low <= value <= high:
            raise ReferenceError("invalid_config_range:" + key)
    if config["fft_size"] != FFT_SIZE:
        raise ReferenceError("fft_size_not_frozen")
    return {key: float(value) for key, value in config.items()}


def _fft_inplace(real: List[float], imag: List[float], inverse: bool = False) -> None:
    size = len(real)
    if size != FFT_SIZE or len(imag) != FFT_SIZE or size & (size - 1):
        raise ReferenceError("invalid_fft_size")
    index = 0
    for position in range(1, size):
        bit = size >> 1
        while index & bit:
            index ^= bit
            bit >>= 1
        index |= bit
        if position < index:
            real[position], real[index] = real[index], real[position]
            imag[position], imag[index] = imag[index], imag[position]
    step = 2
    while step <= size:
        angle = (-2.0 if inverse else 2.0) * math.pi / step
        step_real, step_imag = math.cos(angle), math.sin(angle)
        for start in range(0, size, step):
            root_real, root_imag = 1.0, 0.0
            for offset in range(step // 2):
                left, right = start + offset, start + offset + step // 2
                product_real = real[right] * root_real - imag[right] * root_imag
                product_imag = real[right] * root_imag + imag[right] * root_real
                real[right], imag[right] = real[left] - product_real, imag[left] - product_imag
                real[left] += product_real
                imag[left] += product_imag
                root_real, root_imag = (
                    root_real * step_real - root_imag * step_imag,
                    root_real * step_imag + root_imag * step_real,
                )
        step <<= 1
    if inverse:
        for position in range(size):
            real[position] /= size
            imag[position] /= size


_OVERLAP_SAMPLES = FFT_SIZE - FRAME_SAMPLES
_OUTPUT_OFFSET = _OVERLAP_SAMPLES
# Floored Hann analysis window: invertible at frame edges, unlike a zero-ended
# Hann used without overlap-add. The tail provides causal context, not delay.
_WINDOW = [0.2 + 0.8 * (0.5 - 0.5 * math.cos(2.0 * math.pi * index / (FFT_SIZE - 1)))
           for index in range(FFT_SIZE)]


class Session:
    """Framewise synthetic suppressor with explicit state and rejection controls."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, epoch: int = 1) -> None:
        self.config = validate_config(config)
        self.inject_nonfinite = False
        self.reset(epoch)

    @property
    def memory_floats(self) -> int:
        return len(self.noise_psd) + len(self.prev_gain) + len(self.prev_snr) + len(self.tail)

    def reset(self, epoch: int = 1) -> Dict[str, Any]:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
            raise ReferenceError("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.noise_psd = [0.0] * FFT_BINS
        self.prev_gain = [1.0] * FFT_BINS
        self.prev_snr = [0.0] * FFT_BINS
        self.tail = [0.0] * _OVERLAP_SAMPLES
        self.calibration_frames = 0
        self.invalid_count = 0
        self.closed = False
        return {"status": "reset", "epoch": epoch, "memory_floats": self.memory_floats}

    def drain(self) -> Dict[str, Any]:
        if self.closed:
            raise ReferenceError("closed_session")
        return {"status": "drained", "frames": 0, "samples": []}

    def close(self) -> None:
        self.closed = True

    def _reject(self, reason: str) -> Dict[str, Any]:
        self.invalid_count += 1
        return {"status": "rejected_" + reason, "reason": reason,
                "invalid_count": self.invalid_count, "samples": None}

    def _spectrum(self, frame: Sequence[float]) -> Tuple[List[float], List[float], List[float]]:
        real = [frame[index] * _WINDOW[index] for index in range(FFT_SIZE)]
        imag = [0.0] * FFT_SIZE
        _fft_inplace(real, imag)
        power = [real[bin_index] ** 2 + imag[bin_index] ** 2 for bin_index in range(FFT_BINS)]
        return real, imag, power

    def _gains(self, power: Sequence[float], variant: str) -> List[float]:
        calibrating = self.calibration_frames < self.config["noise_calibration_frames"]
        gains: List[float] = []
        for bin_index in range(FFT_BINS):
            noise = max(self.noise_psd[bin_index], self.config["noise_floor"])
            if calibrating:
                if self.calibration_frames == 0:
                    self.noise_psd[bin_index] = power[bin_index]
                else:
                    self.noise_psd[bin_index] = 0.7 * self.noise_psd[bin_index] + 0.3 * power[bin_index]
            else:
                self.noise_psd[bin_index] = min(self.noise_psd[bin_index],
                                               max(power[bin_index], self.config["noise_floor"]))
            if variant == BASELINE_VARIANT:
                floor = self.config["baseline_gain_floor"]
                reduced = max(power[bin_index] - self.config["baseline_oversubtract"] * noise,
                              floor * power[bin_index])
                gains.append(math.sqrt(max(0.0, reduced) / max(power[bin_index], 1e-18)))
                continue
            posterior = power[bin_index] / noise
            raw_snr = max(0.0, posterior - self.config["candidate_oversubtraction"])
            if calibrating:
                prior = raw_snr
            else:
                prior = (self.config["decision_alpha"] * self.prev_gain[bin_index] ** 2
                         * self.prev_snr[bin_index]
                         + (1.0 - self.config["decision_alpha"]) * raw_snr)
            gain = max(prior / (1.0 + prior), LEVEL_FLOORS[variant])
            self.prev_gain[bin_index] = gain
            self.prev_snr[bin_index] = posterior
            gains.append(gain)
        self.calibration_frames += 1
        return gains

    def _synthesize(self, real: List[float], imag: List[float], gains: Sequence[float]) -> List[float]:
        for bin_index in range(FFT_BINS):
            real[bin_index] *= gains[bin_index]
            imag[bin_index] *= gains[bin_index]
        for bin_index in range(1, FFT_SIZE // 2):
            real[FFT_SIZE - bin_index] = real[bin_index]
            imag[FFT_SIZE - bin_index] = -imag[bin_index]
        _fft_inplace(real, imag, inverse=True)
        return [real[_OUTPUT_OFFSET + index] / _WINDOW[_OUTPUT_OFFSET + index]
                for index in range(FRAME_SAMPLES)]

    def process_frame(self, samples: Sequence[float], epoch: int, position: int,
                      variant: str = CANDIDATE_VARIANT) -> Dict[str, Any]:
        if self.closed:
            return self._reject("closed")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch != self.epoch:
            return self._reject("epoch")
        if isinstance(position, bool) or not isinstance(position, int) or position != self.position:
            return self._reject("position")
        if variant not in PROCESS_VARIANTS:
            return self._reject("variant")
        if not isinstance(samples, (list, tuple)) or len(samples) != FRAME_SAMPLES:
            return self._reject("shape")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in samples):
            return self._reject("type")
        values = [float(value) for value in samples]
        if any(not math.isfinite(value) for value in values):
            return self._reject("nonfinite")
        if any(abs(value) > self.config["max_abs_input"] for value in values):
            return self._reject("range")
        analysis_frame = self.tail + values
        if variant == CONTROL_VARIANT:
            output = values
        else:
            real, imag, power = self._spectrum(analysis_frame)
            output = self._synthesize(real, imag, self._gains(power, variant))
        self.tail = analysis_frame[FRAME_SAMPLES:]
        self.position += 1
        if self.inject_nonfinite:
            output[0] = float("nan")
            return {"status": "invalid_output_nonfinite", "reason": "nonfinite_output",
                    "invalid_count": self.invalid_count + 1, "samples": output}
        finite = all(math.isfinite(value) for value in output)
        peak = max((abs(value) for value in output), default=0.0)
        return {
            "status": "ok" if finite else "invalid_output_nonfinite",
            "reason": None if finite else "nonfinite_output",
            "samples": output,
            "digest": digest_values(output) if finite else None,
            "peak": peak,
            "position": position,
            "invalid_count": self.invalid_count,
        }


def render(variant: str, samples: Optional[Sequence[float]],
           config: Optional[Dict[str, Any]] = None, epoch: int = 1) -> Dict[str, Any]:
    """Render a whole synthetic signal through 160-sample frames."""
    if samples is None:
        return {"status": "blocked", "reason": "missing_input", "samples": None,
                "metrics": None, "digest": None}
    if variant not in PROCESS_VARIANTS:
        return {"status": "blocked", "reason": "unknown_variant", "samples": None,
                "metrics": None, "digest": None}
    if len(samples) % FRAME_SAMPLES:
        return {"status": "rejected_shape", "reason": "partial_frame", "samples": None,
                "metrics": None, "digest": None}
    session = Session(config, epoch=epoch)
    output: List[float] = []
    for position, frame in enumerate(fixture.frame_view(samples)):
        result = session.process_frame(frame, epoch, position, variant)
        if result["status"] != "ok" or result["samples"] is None:
            return {"status": result["status"], "reason": result.get("reason"),
                    "samples": None, "metrics": None, "digest": None}
        output.extend(result["samples"])
    finite = all(math.isfinite(value) for value in output)
    return {
        "status": "ok" if finite else "invalid_output_nonfinite",
        "reason": None if finite else "nonfinite_output",
        "samples": output,
        "digest": digest_values(output) if finite else None,
        "peak": max((abs(value) for value in output), default=0.0),
        "frames": len(output) // FRAME_SAMPLES,
        "finite": finite,
        "invalid_count": session.invalid_count,
        "memory_floats": session.memory_floats,
    }


def score_variant(clean: Optional[Sequence[float]], noisy: Optional[Sequence[float]],
                  rendered: Dict[str, Any]) -> Dict[str, Any]:
    """Paired synthetic scoring; missing or invalid results are never promoted."""
    if clean is None or noisy is None or rendered.get("samples") is None:
        return {"status": "blocked", "reason": "missing_reference_or_output", "metrics": None}
    if rendered.get("status") != "ok" or not rendered.get("finite"):
        return {"status": "invalid_output", "reason": rendered.get("reason", "invalid_output"), "metrics": None}
    output = rendered["samples"]
    si, si_reason = scorer.si_sdr(clean, output)
    raw_si, raw_reason = scorer.si_sdr(clean, noisy)
    stoi, stoi_reason = scorer.stoi_style(clean, output)
    raw_stoi, raw_stoi_reason = scorer.stoi_style(clean, noisy)
    if si_reason == "perfect_reconstruction":
        si_reason = None  # control-only case; SI-SDR is undefined at exact identity
    metrics = {
        "si_sdr_db": si,
        "si_sdr_reason": si_reason,
        "noisy_si_sdr_db": raw_si,
        "delta_si_sdr_db": None if si is None or raw_si is None else si - raw_si,
        "stoi_style": stoi,
        "stoi_style_reason": stoi_reason,
        "noisy_stoi_style": raw_stoi,
        "delta_stoi_style": None if stoi is None or raw_stoi is None else stoi - raw_stoi,
        "peak": rendered["peak"],
        "noisy_peak": max(abs(float(value)) for value in noisy),
        "finite": bool(rendered["finite"]),
        "digest": rendered["digest"],
    }
    reasons = [reason for reason in (si_reason, raw_reason, stoi_reason, raw_stoi_reason) if reason]
    status = "scored" if not reasons and metrics["delta_si_sdr_db"] is not None else "unscored"
    return {"status": status, "reason": reasons[0] if reasons else None, "metrics": metrics,
            "primary_reasons": [raw_reason, raw_stoi_reason]}


def noise_prefix_attenuation(noisy: Sequence[float], output: Sequence[float]) -> float:
    end = fixture.NOISE_PREFIX_SAMPLES
    input_energy = math.fsum(value * value for value in noisy[:end])
    output_energy = math.fsum(value * value for value in output[:end])
    if input_energy <= 0.0 or output_energy <= 0.0:
        return 0.0
    return 10.0 * math.log10(output_energy / input_energy)


def state_evidence() -> Dict[str, Any]:
    """Alignment, independent state, reset replay and unpaced timing labels."""
    items, _ = fixture.cohort()
    samples = items[0]["noisy"]
    first = render(CANDIDATE_VARIANT, samples)
    alternate_config = dict(DEFAULT_CONFIG, noise_calibration_frames=20)
    alternate = render(CANDIDATE_VARIANT, samples, config=alternate_config)
    other = render(CANDIDATE_VARIANT, items[1]["noisy"])
    session = Session()
    first_frames = fixture.frame_view(samples)
    frame_digests: List[str] = []
    frame_outputs: List[float] = []
    for position, frame in enumerate(first_frames):
        result = session.process_frame(frame, 1, position, CANDIDATE_VARIANT)
        frame_digests.append(result["digest"])
        frame_outputs.extend(result["samples"])
    session.reset(epoch=7)
    replay_outputs: List[float] = []
    for position, frame in enumerate(first_frames[:3]):
        replay_frame = session.process_frame(frame, 7, position, CANDIDATE_VARIANT)
        if replay_frame["status"] != "ok":
            raise ReferenceError("replay_failed")
        replay_outputs.extend(replay_frame["samples"])
    replay_digest = digest_values(replay_outputs)
    if replay_digest != digest_values(frame_outputs[:3 * FRAME_SAMPLES]):
        raise ReferenceError("reset_replay_digest_mismatch")
    impulse = [0.0] * 320
    impulse[0] = 0.5
    impulse_out = render(CANDIDATE_VARIANT, impulse)
    peak_index = max(range(len(impulse_out["samples"])), key=lambda index: abs(impulse_out["samples"][index]))
    return {
        "alignment": {
            "content_delay_samples": 0,
            "impulse_peak_index": peak_index,
            "input_frames": first["frames"],
            "output_frames": first["frames"],
            "framewise_stream_digest_equal": digest_values(frame_outputs) == first["digest"],
            "frame_digest_count": len(frame_digests),
            "classification": "synthetic_frame_index_alignment_not_device_measured",
        },
        "state": {
            "independent_state_configuration_digests_differ": first["digest"] != alternate["digest"],
            "different_condition_digest_differs": first["digest"] != other["digest"],
            "reset_epoch_replay_digest": replay_digest,
            "reset_replay_scoped": "first_three_frames_only",
            "invalid_state_mutation": "rejected frames leave PSD, gain and position unchanged",
        },
        "memory": {
            "retained_floats_per_session": first["memory_floats"],
            "classification": "analytic_state_count_not_peak_rss",
            "device_memory_measured": False,
        },
        "timing": {
            "content_timing": "frame-index schedule, 160 samples per frame",
            "availability_timing": "unpaced synchronous call; no queue or device clock",
            "wall_clock_measured": False,
            "target_device_paced": False,
            "classification": "unpaced_synthetic_not_target_device",
        },
    }


def failure_controls() -> Dict[str, Any]:
    """Explicit invalid, missing, stale and nonfinite controls; no silent skips."""
    session = Session()
    valid_frame = [0.01] * FRAME_SAMPLES
    checks: Dict[str, bool] = {}
    checks["wrong_shape"] = session.process_frame([0.0] * 159, 1, 0)["status"] == "rejected_shape"
    checks["nonfinite_input"] = session.process_frame([float("nan")] + [0.0] * 159, 1, 0)["status"] == "rejected_nonfinite"
    checks["wrong_type"] = session.process_frame(["x"] + [0.0] * 159, 1, 0)["status"] == "rejected_type"
    checks["out_of_range"] = session.process_frame([99.0] + [0.0] * 159, 1, 0)["status"] == "rejected_range"
    checks["stale_epoch"] = session.process_frame(valid_frame, 2, 0)["status"] == "rejected_epoch"
    checks["stale_position"] = session.process_frame(valid_frame, 1, 9)["status"] == "rejected_position"
    checks["unknown_variant"] = session.process_frame(valid_frame, 1, 0, "webrtc_runtime")["status"] == "rejected_variant"
    checks["state_unchanged_after_rejections"] = session.position == 0
    checks["invalid_config_key"] = _raises(lambda: validate_config({"fft_size": FFT_SIZE}))
    checks["invalid_config_range"] = _raises(lambda: validate_config(dict(DEFAULT_CONFIG, decision_alpha=2.0)))
    checks["missing_input_blocked"] = render(CANDIDATE_VARIANT, None)["status"] == "blocked"
    checks["missing_reference_blocked"] = score_variant(None, valid_frame, {"status": "ok"})["status"] == "blocked"
    injected = Session()
    injected.inject_nonfinite = True
    bad = injected.process_frame(valid_frame, 1, 0)
    checks["nonfinite_output_rejected"] = bad["status"] == "invalid_output_nonfinite"
    checks["nonfinite_output_unscored"] = score_variant(valid_frame, valid_frame, bad)["status"] == "invalid_output"
    checks["nonfinite_scorer_reason"] = scorer.si_sdr(valid_frame, bad["samples"])[1] == "invalid_input"
    closed = Session()
    closed.close()
    checks["closed_session"] = closed.process_frame(valid_frame, 1, 0)["status"] == "rejected_closed"
    return {
        "checks": checks,
        "all_explicit": all(checks.values()),
        "rejected_count": sum(1 for value in checks.values() if not value),
        "rule": "invalid, missing, stale and nonfinite cases are reported, never dropped or scored as successes",
    }


def _raises(callback: Any) -> bool:
    try:
        callback()
    except ReferenceError:
        return True
    return False


def scorer_validation() -> Dict[str, Any]:
    clean = [0.0, 1.0, 0.0, -1.0, 0.5, -0.5, 0.25, 0.0] * 200
    scaled = [0.37 * value + 1e-4 * math.sin(index) for index, value in enumerate(clean)]
    si_scaled, si_scaled_reason = scorer.si_sdr(clean, scaled)
    si_identity, identity_reason = scorer.si_sdr(clean, clean)
    stoi_identity, _ = scorer.stoi_style(clean, clean)
    deterministic, deterministic_reason = scorer.stoi_style(clean, list(scaled))
    return {
        "scorer_id": scorer.SCORER_ID,
        "si_sdr_revision": scorer.SI_SDR_REVISION,
        "stoi_style_revision": scorer.STOI_STYLE_REVISION,
        "scale_invariant_si_sdr_db": si_scaled,
        "scale_invariant_si_sdr_reason": si_scaled_reason,
        "identity_si_sdr_undefined_reason": identity_reason,
        "identity_stoi_style": stoi_identity,
        "second_stoi_style_pass": deterministic,
        "second_stoi_style_reason": deterministic_reason,
        "dependency_free": True,
        "claim": "synthetic scorer validation only; not pystoi, audio-bench parity or human MOS",
    }


def unpaired_screen() -> Dict[str, Any]:
    """Separate predictive proxy for unpaired synthetic speech; never a quality gate."""
    item = fixture.unpaired()
    noisy = item["noisy"]
    results: Dict[str, Any] = {}
    for variant in (CONTROL_VARIANT, CANDIDATE_VARIANT):
        rendered = render(variant, noisy)
        frames = fixture.frame_view(rendered["samples"])
        active = sum(1 for frame in frames
                     if math.fsum(value * value for value in frame) / FRAME_SAMPLES > 1e-6)
        results[variant] = {
            "digest": rendered["digest"],
            "peak": rendered["peak"],
            "active_frame_fraction": active / len(frames),
            "nonfinite": not rendered["finite"],
        }
    common = set(results)
    return {
        "item_id": item["item_id"],
        "input_digest": item["digest"],
        "has_clean_reference": False,
        "proxy_scores": results,
        "active_frame_fraction_delta": results[CANDIDATE_VARIANT]["active_frame_fraction"]
                                        - results[CONTROL_VARIANT]["active_frame_fraction"],
        "classification": "predictive_proxy_only_not_intelligibility_or_quality",
        "human_listening": False,
        "mos_or_stoi_claim": False,
        "qualifies_candidate": False,
        "common_variants": sorted(common),
    }


def build_report() -> Dict[str, Any]:
    """Build the frozen canonical report; ``run.py`` adds adapter validation."""
    items, pinned = fixture.cohort()
    clean_reference = items[0]["clean"]
    paired: List[Dict[str, Any]] = []
    clean_preservation: List[Dict[str, Any]] = []
    level_noise_prefix: List[Dict[str, Any]] = []
    for item in items:
        noisy = item["noisy"]
        for variant in PROCESS_VARIANTS:
            rendered = render(variant, noisy)
            scored = score_variant(item["clean"], noisy, rendered)
            row = {
                "condition": item["item_id"],
                "snr_db": item["snr_db"],
                "variant": variant,
                "role": ("control" if variant == CONTROL_VARIANT else
                         "task_matched_baseline" if variant == BASELINE_VARIANT else
                         "candidate" if variant == CANDIDATE_VARIANT else "candidate_level_ablation"),
                "status": scored["status"],
                "reason": scored["reason"],
                "metrics": scored["metrics"],
                "output_digest": rendered["digest"],
                "noise_prefix_attenuation_db": noise_prefix_attenuation(noisy, rendered["samples"])
                                               if rendered["samples"] else None,
            }
            paired.append(row)
            if variant in LEVEL_FLOORS:
                level_noise_prefix.append({
                    "condition": item["item_id"], "variant": variant,
                    "noise_prefix_attenuation_db": row["noise_prefix_attenuation_db"],
                    "delta_stoi_style": (scored["metrics"] or {}).get("delta_stoi_style"),
                })
    adverse_results: List[Dict[str, Any]] = []
    for row in paired:
        metrics = row["metrics"] or {}
        for metric_name in ("delta_si_sdr_db", "delta_stoi_style"):
            value = metrics.get(metric_name)
            if value is not None and value <= 0.0 and row["variant"] != CONTROL_VARIANT:
                adverse_results.append({
                    "condition": row["condition"],
                    "variant": row["variant"],
                    "metric": metric_name,
                    "value": value,
                    "classification": "adverse_synthetic_result_retained_not_hidden",
                })
    for variant in PROCESS_VARIANTS:
        rendered = render(variant, clean_reference)
        scored = score_variant(clean_reference, clean_reference, rendered)
        clean_preservation.append({
            "variant": variant,
            "input": "generated_clean_reference",
            "status": scored["status"],
            "reason": scored["reason"],
            "metrics": scored["metrics"],
            "output_digest": rendered["digest"],
        })
    artifact_pins = {name: digest_file(ROOT / name) for name in ARTIFACT_FILES}
    return {
        "schema_id": CONTRACT_ID + "/report",
        "task": TASK_ID,
        "verification_profile": "enhancement",
        "status": "proposal_only_not_qualified",
        "completeness": "incomplete",
        "decision": {
            "disposition": "DEFER",
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "promote": False,
            "release_claim": False,
        },
        "scope": {
            "runtime": "synthetic Python reference only; no WebRTC APM source, binary, wheel or runtime",
            "weights_or_assets": [],
            "downloads": False,
            "real_speech": False,
            "licensed_runtime": False,
            "human_listening": False,
            "target_device_measurement": False,
            "installed_behavior": "unchanged: 16000 Hz mono f32, 160-sample frames",
            "public_api_abi_descriptor_registry_defaults_changed": False,
            "C_boundary_included": False,
        },
        "profile_application": {
            "control": CONTROL_VARIANT,
            "task_matched_baseline": BASELINE_VARIANT,
            "candidate": CANDIDATE_VARIANT,
            "paired_metrics": ["si_sdr_db", "stoi_style"],
            "clean_references": "generated analytic speech; synthetic only",
            "unpaired_screen": "predictive_proxy_only, separately labeled",
            "missing_result_qualifies": False,
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_snapshot": BOARD_SNAPSHOT,
        "artifact_pins": artifact_pins,
        "fixture": {
            "generator": fixture.GENERATOR_ID,
            "seed": fixture.MASTER_SEED,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "samples_per_item": fixture.SAMPLES,
            "frame_samples": FRAME_SAMPLES,
            "noise_prefix_samples": fixture.NOISE_PREFIX_SAMPLES,
            "digests": pinned,
            "contents": "analytic harmonic speech plus seeded shaped noise; no corpus or file I/O",
        },
        "method": {
            "fft_size": FFT_SIZE,
            "noise_calibration": "first 10 frames of noise-only prefix; frozen/min-tracked afterwards",
            "candidate": "synthetic decision-directed Wiener gain with oversubtraction 2.0 and level floors 0.55/0.40/0.25",
            "baseline": "classical spectral subtraction with oversubtraction factor 2.0",
            "causal": True,
            "added_delay_samples": 0,
            "authoritative_webrtc_algorithm_or_level_result": False,
        },
        "paired_results": paired,
        "clean_speech_preservation": clean_preservation,
        "candidate_level_ablation": level_noise_prefix,
        "adverse_results": adverse_results,
        "adverse_result_policy": "negative or non-positive paired deltas are retained and reported; they do not qualify any variant",
        "unpaired_predictive_screen": unpaired_screen(),
        "alignment_state_memory_timing": state_evidence(),
        "failure_controls": failure_controls(),
        "scorer_validation": scorer_validation(),
        "gates": [
            {"gate": "held_out_real_speech_paired_si_sdr_stoi", "status": "not_met"},
            {"gate": "authorized_listening_or_mos", "status": "not_met"},
            {"gate": "real_runtime_version_and_license", "status": "not_met"},
            {"gate": "target_device_pacing_memory_deadline", "status": "not_met"},
            {"gate": "provider_intake_descriptor_catalog_review", "status": "not_met"},
        ],
        "remaining_gates": "DEFER until all gates are met on the exact runtime and workload",
        "non_claims": [
            "No authoritative WebRTC APM NS baseline, level ranking or oracle result is claimed.",
            "No installed v0, provider registry, descriptor, default, ABI or public surface change.",
            "No real speech, licensed runtime, weights, download, listening test or release claim.",
            "No target-device content delay, availability, CPU, memory or deadline measurement.",
        ],
    }
