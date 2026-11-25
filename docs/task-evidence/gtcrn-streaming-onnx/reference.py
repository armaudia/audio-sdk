# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local streaming surrogate for SDK-GTCRN-STREAMING-ONNX.

This module models the documented GTCRN streaming ONNX boundary and, because no
model weight, ONNX Runtime package or redistribution right is available here,
runs a deterministic pure-Python spectral surrogate at that boundary. It is a
developer-facing engineering fixture: not the upstream model, not ONNX Runtime,
not real audio, not a device measurement, not a listening result, not a
benchmark and not a release qualification. The caller-supplied-asset path is
declared and fails closed; no production callback is implemented.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import scorer
from scorer import SCORER_ID, si_sdr, stoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK_ID = "SDK-GTCRN-STREAMING-ONNX"
TITLE = "GTCRN streaming ONNX"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
SCHEMA_ID = "audio-sdk/task-evidence/gtcrn-streaming-onnx/report/0.1"
COMPONENT_ID = "gtcrn-streaming-onnx"
REFERENCE_FAMILY = "gtcrn"
FAMILY = "streaming-onnx"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_readiness_incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "provider_registration"
TASK_REL = "docs/task-evidence/gtcrn-streaming-onnx"

# Installed public v0 frontend: documented, unchanged. It is not the model hop.
FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "unchanged_installed_v0_reference",
    "installed_v0_geometry_preserved": True,
    "native_model_geometry": "model_geometry",
}

# Documented upstream streaming boundary from adapters/gtcrn-streaming/run.py.
WINDOW_SAMPLES = 512
HOP_SAMPLES = 256
STFT_BINS = 257
STFT_LOOKAHEAD_SAMPLES = 256
WOLA_SYNTHESIS_DELAY_SAMPLES = 256
CONTENT_DELAY_SAMPLES = WINDOW_SAMPLES
SAMPLE_RATE = 16000
FRAME_HOP_MS = 1000.0 * HOP_SAMPLES / SAMPLE_RATE
STFT_LOOKAHEAD_MS = 1000.0 * STFT_LOOKAHEAD_SAMPLES / SAMPLE_RATE
CONTENT_DELAY_MS = 1000.0 * CONTENT_DELAY_SAMPLES / SAMPLE_RATE
STATE_CACHES = {
    "conv_cache": [2, 1, 16, 16, 33],
    "tra_cache": [2, 3, 1, 1, 16],
    "inter_cache": [2, 1, 33, 16],
}

MODEL_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE,
    "channels": 1,
    "sample_format": "f32",
    "window_samples": WINDOW_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "hop_ms": FRAME_HOP_MS,
    "stft_bins": STFT_BINS,
    "frame_representation": "real_imag",
    "analysis_synthesis_window": "sqrt_periodic_hann_512",
    "stft_lookahead_samples": STFT_LOOKAHEAD_SAMPLES,
    "stft_lookahead_ms": STFT_LOOKAHEAD_MS,
    "wola_synthesis_delay_samples": WOLA_SYNTHESIS_DELAY_SAMPLES,
    "content_delay_samples": CONTENT_DELAY_SAMPLES,
    "content_delay_ms": CONTENT_DELAY_MS,
    "state_caches": STATE_CACHES,
    "state_persisted_across_hops": True,
    "reset_behavior": "explicit_reset_zeroes_all_stream_and_model_state",
    "note": (
        "Sample-count geometry only. The pinned adapter estimates a 16 ms centered-STFT "
        "lookahead; one additional half-window is required to complete 50% overlap-add "
        "synthesis, so this surrogate declares a 32 ms analytical content delay. No "
        "measured timing is claimed."
    ),
}

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "c_public_boundary": False,
    "installed_v0_geometry_preserved": True,
    "evaluation_path": "task_local_python_streaming_surrogate",
    "production_callback_path": "not_implemented",
    "real_asset_required": True,
    "real_asset_present": False,
    "real_runtime_invoked": False,
    "silent_fallback_to_surrogate": False,
}

CONFIG = {"mode": "streaming_surrogate", "asset": "caller_supplied_asset"}
REAL_MODE = "caller_supplied_onnx"
SURROGATE_MODE = "streaming_surrogate"
ASSET_REFERENCE = "caller_supplied_asset"
ASSET_FILENAME = "gtcrn_simple.onnx"
SIGNAL_SAMPLES = 9728  # 38 hops of 256 samples
MAX_ABS_INPUT = 2.0
CONDITIONS = ["identity", "noisy_control", "reverberant_control", "frontend_shape", "silence"]

# Surrogate parameters, frozen before the first run and never tuned on results.
SURROGATE_PARAMETERS = {
    "power_smoothing": 0.75,
    "minimum_gain": 0.125,
    "noise_floor_power": 0.004,
    "clipping_threshold": 0.98,
}

# Pinned identities. All paths are relative to SOURCE_ROOT unless prefixed
# with ``worktree:``, in which case they are relative to SDK_ROOT.
SOURCE_PINS: Dict[str, str] = {
    "source:adapters/gtcrn-streaming/run.py":
        "272cea7120a1e21e67c1f6bfcd37848dd79fe5a7910ee79f2d48c6c31f856ec9",
    "source:research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "source:REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
ARTIFACT_PIN_PATHS = (
    f"{TASK_REL}/contract.json",
    f"{TASK_REL}/adapter.json",
    f"{TASK_REL}/provider.json",
    f"{TASK_REL}/asset.json",
    f"{TASK_REL}/scorer.py",
    "docs/task-evidence/online-multichannel-wpe/scorer.py",
    "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json",
)
PIN_RE = re.compile(
    r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|worktree:[^\s]+|docs/[^\s]+|api/[^\s]+|CONTRACTS\.md)$")
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_json(path: Path) -> Any:
    def reject_object_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def reject_constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=reject_object_pairs, parse_constant=reject_constant)


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return SOURCE_ROOT / raw.split(":", 1)[1]
    if raw.startswith("worktree:"):
        return SDK_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Fail closed on malformed, duplicated or out-of-scope manifest entries."""
    pins: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + repr(line))
        raw_path = match.group("path")
        if ".." in Path(raw_path.split(":", 1)[-1]).parts:
            raise ValueError("path_traversal_pin:" + raw_path)
        if raw_path in seen:
            raise ValueError("duplicate_pin:" + raw_path)
        seen.add(raw_path)
        pins.append((line[:64], raw_path))
    return pins


def artifact_pins() -> Dict[str, str]:
    return {path: sha256(pin_path(path).read_bytes()) for path in ARTIFACT_PIN_PATHS}


def sources_bytes() -> bytes:
    """Deterministic manifest; excludes SOURCES.sha256 itself to avoid self-reference."""
    pins: Dict[str, str] = dict(SOURCE_PINS)
    pins.update(BOUNDARY_PINS)
    pins.update(artifact_pins())
    for path in sorted(HERE.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SOURCES.sha256":
            pins[f"{TASK_REL}/{path.name}"] = sha256(path.read_bytes())
    lines = [f"{digest}  {path}" for path, digest in sorted(pins.items())]
    header = (f"# SHA-256 pins for {TASK_ID}. "
              "source: paths are workspace-relative; worktree: and plain paths are "
              "SDK-worktree-relative. Lines are <sha256>  <path>.\n")
    return (header + "\n".join(lines) + "\n").encode("utf-8")


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return frozen synthetic dry target and observed input for one condition."""
    seed = 20261125 + sum(ord(char) for char in condition)
    random = rng(seed)
    clean: List[float] = []
    for index in range(SIGNAL_SAMPLES):
        envelope = 0.62 + 0.24 * math.sin(2.0 * math.pi * index / 2437.0)
        glide = 1.0 + 0.03 * math.sin(2.0 * math.pi * index / 7919.0)
        tone = 0.0
        for harmonic in range(1, 8):
            tone += (0.16 / harmonic) * math.sin(
                2.0 * math.pi * 118.0 * harmonic * glide * index / SAMPLE_RATE)
        sibilant = 0.05 * math.sin(2.0 * math.pi * 3600.0 * index / SAMPLE_RATE)
        clean.append((tone + sibilant) * envelope)
    if condition == "silence":
        return [0.0] * SIGNAL_SAMPLES, [0.0] * SIGNAL_SAMPLES
    if condition == "reverberant_control":
        observed = reverberate(clean)
        clean_rms = math.sqrt(math.fsum(value * value for value in clean) / SIGNAL_SAMPLES)
        wet_rms = math.sqrt(math.fsum(value * value for value in observed) / SIGNAL_SAMPLES)
        scale = clean_rms / wet_rms if wet_rms > 0.0 else 1.0
        for index in range(SIGNAL_SAMPLES):
            observed[index] = observed[index] * scale + (next(random) - 0.5) * 2.0 * 0.01
        return clean, observed
    noise_scale = {
        "identity": 0.008,
        "noisy_control": 0.16,
        "frontend_shape": 0.06,
    }[condition]
    observed = []
    for index, value in enumerate(clean):
        noise = (next(random) - 0.5) * 2.0 * noise_scale
        if condition == "noisy_control" and 3200 <= index < 4096:
            noise *= 3.0
        if condition == "frontend_shape" and 5120 <= index < 6144:
            noise += 0.04 * math.sin(2.0 * math.pi * 1000.0 * index / SAMPLE_RATE)
        observed.append(value + noise)
    return clean, observed


def reverberate(values: List[float]) -> List[float]:
    """Deterministic O(N) synthetic reverberant channel; not a measured RIR."""
    combs = ((1123, 0.66), (1427, 0.62), (1789, 0.58))
    output = [0.0] * len(values)
    for delay, feedback in combs:
        line = [0.0] * delay
        cursor = 0
        for index, value in enumerate(values):
            delayed = line[cursor]
            line[cursor] = value + feedback * delayed
            output[index] += delayed / len(combs)
            cursor = (cursor + 1) % delay
    for index, value in enumerate(values):
        output[index] += 0.7 * value
    return output


def analysis_window() -> List[float]:
    """sqrt of the periodic Hann window of length 512, exactly sin(pi*n/512)."""
    return [math.sin(math.pi * index / WINDOW_SAMPLES) for index in range(WINDOW_SAMPLES)]


WINDOW = analysis_window()


def _fft(values: List[complex]) -> List[complex]:
    return scorer._fft(values)


def _ifft(values: List[complex]) -> List[complex]:
    return scorer._fft(values, inverse=True)


def transform_spectrum(frame: List[complex], power_state: List[float]
                       ) -> Tuple[List[complex], List[float]]:
    """Deterministic single-frame spectral shrinkage with one-pole power state."""
    spectrum = _fft(list(frame))
    updated: List[float] = []
    shaped: List[complex] = []
    for index in range(STFT_BINS):
        value = spectrum[index]
        power = value.real * value.real + value.imag * value.imag
        smoothed = (SURROGATE_PARAMETERS["power_smoothing"] * power_state[index]
                    + (1.0 - SURROGATE_PARAMETERS["power_smoothing"]) * power)
        updated.append(smoothed)
        gain = smoothed / (smoothed + SURROGATE_PARAMETERS["noise_floor_power"])
        gain = max(SURROGATE_PARAMETERS["minimum_gain"], min(1.0, gain))
        shaped.append(value * gain)
    # Mirror the conjugate half so the inverse transform is real.
    for index in range(STFT_BINS, WINDOW_SAMPLES):
        shaped.append(shaped[WINDOW_SAMPLES - index].conjugate())
    return shaped, updated


class Stream:
    """Stateful hop-256 streaming boundary with WOLA overlap-add state."""

    def __init__(self) -> None:
        self.epoch = 1
        self.next_position = 0
        self.buffer = [0.0] * (WINDOW_SAMPLES - HOP_SAMPLES)
        self.ola = [0.0] * WINDOW_SAMPLES
        self.norm = [0.0] * WINDOW_SAMPLES
        self.power_state = [0.0] * STFT_BINS
        self.hops = 0
        self.finished = False
        self.closed = False
        self.state_hash = self._state()

    def control_state(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "next_position": self.next_position,
            "hops": self.hops,
            "finished": self.finished,
            "closed": self.closed,
            "conv_cache_shape": STATE_CACHES["conv_cache"],
            "tra_cache_shape": STATE_CACHES["tra_cache"],
            "inter_cache_shape": STATE_CACHES["inter_cache"],
            "persistent_buffers": ["analysis_buffer", "ola_accumulator", "window_norm",
                                   "power_state"],
        }

    def _state(self) -> str:
        return sha256(canonical_bytes({
            **{key: value for key, value in self.control_state().items()
               if key != "persistent_buffers"},
            "buffer": [round(value, 12) for value in self.buffer],
            "ola": [round(value, 12) for value in self.ola],
            "norm": [round(value, 12) for value in self.norm],
            "power_state": [round(value, 12) for value in self.power_state],
        }))

    def _reject(self, status: str) -> Dict[str, Any]:
        return {"status": status, "samples": None, "state_digest": self.state_hash}

    def _advance(self, hop: List[float]) -> List[float]:
        self.buffer = (self.buffer + list(hop))[-WINDOW_SAMPLES:]
        frame = [complex(self.buffer[index] * WINDOW[index], 0.0)
                 for index in range(WINDOW_SAMPLES)]
        shaped, self.power_state = transform_spectrum(frame, self.power_state)
        time_frame = _ifft(shaped)
        for index in range(WINDOW_SAMPLES):
            value = time_frame[index].real * WINDOW[index]
            self.ola[index] += value
            self.norm[index] += WINDOW[index] * WINDOW[index]
        block = [self.ola[index] / max(self.norm[index], 1e-12) for index in range(HOP_SAMPLES)]
        self.ola = self.ola[HOP_SAMPLES:] + [0.0] * HOP_SAMPLES
        self.norm = self.norm[HOP_SAMPLES:] + [0.0] * HOP_SAMPLES
        self.hops += 1
        return block

    def process(self, hop: Any, epoch: int, first_sample: int) -> Dict[str, Any]:
        if self.closed or self.finished:
            return self._reject("rejected_session")
        if not isinstance(hop, (list, tuple)) or len(hop) != HOP_SAMPLES:
            return self._reject("rejected_tensor")
        if any(isinstance(value, bool) for value in hop):
            return self._reject("rejected_invalid")
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in hop):
            return self._reject("rejected_nonfinite")
        if any(abs(value) > MAX_ABS_INPUT for value in hop):
            return self._reject("rejected_invalid")
        if epoch != self.epoch:
            return self._reject("rejected_epoch")
        if first_sample != self.next_position:
            return self._reject("rejected_position")
        block = self._advance(hop)
        self.next_position += HOP_SAMPLES
        self.state_hash = self._state()
        if self.hops < 2:
            return {"status": "priming", "samples": None, "state_digest": self.state_hash}
        return {"status": "ok", "samples": block, "state_digest": self.state_hash}

    def finish(self) -> Dict[str, Any]:
        if self.closed or self.finished:
            return {"status": "rejected_session", "samples": None}
        if self.hops < 1:
            self.finished = True
            self.state_hash = self._state()
            return {"status": "ok", "samples": []}
        block = self._advance([0.0] * HOP_SAMPLES)
        self.finished = True
        self.state_hash = self._state()
        return {"status": "ok", "samples": block}

    def close(self) -> None:
        self.closed = True
        self.state_hash = self._state()

    def reset(self, epoch: int, first_sample: int) -> str:
        if self.closed:
            return "rejected_session"
        if epoch <= self.epoch:
            return "rejected_epoch"
        if first_sample < 0:
            return "rejected_position"
        self.__init__()
        self.epoch = epoch
        self.next_position = first_sample
        self.state_hash = self._state()
        return "ok"


def create_controller(config: Any) -> Dict[str, Any]:
    """Strict config admission; the real asset path fails closed without an asset."""
    if not isinstance(config, dict):
        return {"controller": None, "status": "rejected_invalid"}
    keys = set(config)
    if keys != {"mode", "asset"}:
        return {"controller": None,
                "status": "rejected_missing" if keys < {"mode", "asset"} else "rejected_invalid"}
    mode = config["mode"]
    asset = config["asset"]
    if isinstance(mode, float) and not math.isfinite(mode):
        return {"controller": None, "status": "rejected_nonfinite"}
    if not isinstance(mode, str) or not isinstance(asset, str):
        return {"controller": None, "status": "rejected_invalid"}
    if not asset or ".." in Path(asset).parts or Path(asset).is_absolute():
        return {"controller": None, "status": "rejected_invalid"}
    if mode == REAL_MODE:
        # Declared boundary only: no asset, runtime or right is available here.
        return {"controller": None, "status": "rejected_asset_unavailable"}
    if mode != SURROGATE_MODE or asset != ASSET_REFERENCE:
        return {"controller": None, "status": "rejected_invalid"}
    return {"controller": Stream(), "status": "created"}


def run_stream(observed: List[float]) -> Tuple[Optional[List[float]], Dict[str, Any]]:
    input_hops = len(observed) // HOP_SAMPLES
    created = create_controller(CONFIG)
    if created["controller"] is None:
        return None, {"status": created["status"], "hops": 0, "total_advances": 0,
                      "rejections": 1, "priming_hops": 0, "flush_blocks": 0}
    stream: Stream = created["controller"]
    output: List[float] = []
    priming = 0
    for index in range(0, len(observed), HOP_SAMPLES):
        result = stream.process(observed[index:index + HOP_SAMPLES], stream.epoch, index)
        if result["status"] == "priming":
            priming += 1
            continue
        if result["status"] != "ok" or result["samples"] is None:
            return None, {"status": result["status"], "hops": input_hops,
                          "total_advances": stream.hops, "rejections": 1,
                          "priming_hops": priming, "flush_blocks": 0}
        output.extend(result["samples"])
    tail = stream.finish()
    if tail["status"] != "ok" or tail["samples"] is None:
        return None, {"status": tail["status"], "hops": input_hops,
                      "total_advances": stream.hops, "rejections": 1,
                      "priming_hops": priming, "flush_blocks": 0}
    output.extend(tail["samples"])
    if len(output) != len(observed):
        return None, {"status": "rejected_duration", "hops": input_hops,
                      "total_advances": stream.hops, "rejections": 1,
                      "priming_hops": priming, "flush_blocks": 1}
    return output, {"status": "ok", "hops": input_hops,
                    "total_advances": stream.hops, "rejections": 0,
                    "priming_hops": priming, "flush_blocks": 1}


def scored(target: List[float], actual: Optional[List[float]]) -> Dict[str, Any]:
    if actual is None:
        return {"status": "rejected", "si_sdr_db": None, "stoi": None,
                "reason": "invalid_input_rejected"}
    si_value, si_reason = si_sdr(target, actual)
    stoi_value, stoi_reason = stoi(target, actual, SAMPLE_RATE)
    return {
        "status": "scored_synthetic" if si_value is not None and stoi_value is not None else "excluded",
        "si_sdr_db": round(si_value, 6) if si_value is not None and math.isfinite(si_value) else None,
        "stoi": round(stoi_value, 6) if stoi_value is not None and math.isfinite(stoi_value) else None,
        "peak_abs_output": round(max(abs(value) for value in actual), 9),
        "nonfinite_count": sum(1 for value in actual if not math.isfinite(value)),
        "clipping_count": sum(1 for value in actual
                              if abs(value) >= SURROGATE_PARAMETERS["clipping_threshold"]),
        "si_sdr_reason": si_reason,
        "stoi_reason": stoi_reason,
    }


def conditions() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for condition in CONDITIONS:
        target, observed = synth(condition)
        baseline = scored(target, observed)
        candidate, run = run_stream(observed)
        scored_candidate = scored(target, candidate)
        candidate_worse = (
            candidate is not None
            and baseline["si_sdr_db"] is not None
            and scored_candidate["si_sdr_db"] is not None
            and scored_candidate["si_sdr_db"] < baseline["si_sdr_db"]
        )
        result[condition] = {
            "status": ("measured_synthetic" if candidate is not None
                       and scored_candidate["status"] == "scored_synthetic"
                       else "excluded_degenerate"),
            "samples": len(observed),
            "seed": 20261125 + sum(ord(char) for char in condition),
            "baseline_metrics": baseline,
            "candidate_metrics": scored_candidate,
            "candidate_worse_than_baseline": candidate_worse,
            "stream_run": run,
            "alignment": {
                "hop_samples": HOP_SAMPLES,
                "content_delay_samples": CONTENT_DELAY_SAMPLES,
                "measured_timing": False,
            },
        }
    return result


def controls() -> Dict[str, Any]:
    identity_target, identity_input = synth("identity")
    identity_output, _ = run_stream(identity_input)
    noisy_target, noisy_input = synth("noisy_control")
    noisy_output, _ = run_stream(noisy_input)
    return {
        "identity": {
            "name": "identity_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(identity_target, identity_input),
        },
        "named_baseline": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(noisy_target, noisy_input),
        },
        "candidate": {
            "name": "half_window_wola_spectral_shrinkage_surrogate",
            "status": "measured_synthetic",
            "metrics": scored(noisy_target, noisy_output),
        },
        "clean_speech_preservation": {
            "clean_reference": "identity condition synthetic dry target",
            "status": "measured_synthetic",
            "metrics": scored(identity_target, identity_output),
        },
        "all_present": True,
        "excluded_from_qualification": True,
        "note": "Identity, noisy and candidate controls are paired synthetic comparisons only.",
    }


def identity_reconstruction() -> Dict[str, Any]:
    """Analytical check that unit gains reconstruct the input through WOLA."""
    probe = [math.sin(2.0 * math.pi * 173.0 * index / SAMPLE_RATE) for index in range(2048)]
    stream = Stream()
    output: List[float] = []
    saved = SURROGATE_PARAMETERS["minimum_gain"]
    try:
        SURROGATE_PARAMETERS["minimum_gain"] = 1.0
        for index in range(0, len(probe), HOP_SAMPLES):
            result = stream.process(probe[index:index + HOP_SAMPLES], 1, index)
            if result["samples"]:
                output.extend(result["samples"])
        tail = stream.finish()
        if tail["samples"]:
            output.extend(tail["samples"])
    finally:
        SURROGATE_PARAMETERS["minimum_gain"] = saved
    error = max(abs(left - right) for left, right in zip(probe, output)) if output else None
    return {
        "probe_samples": len(probe),
        "output_samples": len(output),
        "max_abs_error": round(error, 12) if error is not None else None,
        "reconstruction_exact": error is not None and error <= 1e-9,
        "gain_override": {"minimum_gain": 1.0},
    }


def adverse() -> Dict[str, Any]:
    config_cases = {
        "missing_asset": {"mode": SURROGATE_MODE},
        "missing_mode": {"asset": ASSET_REFERENCE},
        "unknown_key": {"mode": SURROGATE_MODE, "asset": ASSET_REFERENCE, "extra": True},
        "wrong_type": {"mode": 7, "asset": ASSET_REFERENCE},
        "nonfinite": {"mode": float("nan"), "asset": ASSET_REFERENCE},
        "unknown_mode": {"mode": "not_a_mode", "asset": ASSET_REFERENCE},
        "real_mode_without_asset": {"mode": REAL_MODE, "asset": "gtcrn_simple.onnx"},
        "traversal_asset": {"mode": REAL_MODE, "asset": "../weights.onnx"},
        "absolute_asset": {"mode": REAL_MODE, "asset": "/tmp/weights.onnx"},
    }
    config_rejections = {
        name: {"status": create_controller(config)["status"], "controller_created": False}
        for name, config in config_cases.items()
    }
    created = create_controller(CONFIG)
    stream: Stream = created["controller"]
    hop = [0.0] * HOP_SAMPLES
    before = stream.state_hash

    def frame_case(value: Any, epoch: int = 1, position: int = 0) -> str:
        return stream.process(value, epoch, position)["status"]

    frame_rejections = {
        "wrong_shape": frame_case(hop[:-1]),
        "bool_sample": frame_case([True] * HOP_SAMPLES),
        "nonfinite": frame_case([float("nan")] * HOP_SAMPLES),
        "out_of_range": frame_case([MAX_ABS_INPUT + 1.0] * HOP_SAMPLES),
        "stale_epoch": frame_case(hop, epoch=0),
        "stale_position": frame_case(hop, position=HOP_SAMPLES),
        "missing_samples": frame_case(None),
        "hop_size_160_is_not_project_geometry": frame_case([0.0] * 160),
        "dsp_state_unchanged": stream.state_hash == before,
    }
    close_stream: Stream = create_controller(CONFIG)["controller"]
    close_stream.close()
    close_then_process = close_stream.process(hop, 1, 0)["status"]
    finish_stream: Stream = create_controller(CONFIG)["controller"]
    finish_stream.finish()
    finish_then_process = finish_stream.process(hop, 1, 0)["status"]
    reset_stream: Stream = create_controller(CONFIG)["controller"]
    stale_reset_epoch = reset_stream.reset(1, 0)
    fresh_reset = reset_stream.reset(2, 0)
    stale_reset_position = reset_stream.reset(3, -1)
    return {
        "config_rejections": config_rejections,
        "frame_rejections": frame_rejections,
        "lifecycle": {
            "close_then_process": close_then_process,
            "finish_then_process": finish_then_process,
            "stale_reset_epoch": stale_reset_epoch,
            "stale_reset_position": stale_reset_position,
            "valid_reset": fresh_reset,
        },
        "validity": {
            "nonfinite_never_counted_as_silence": True,
            "invalid_excluded": True,
            "invalid_never_advances_stream_state": True,
            "real_asset_path_never_falls_back": True,
        },
    }


def repeatability() -> Dict[str, Any]:
    _, observed = synth("identity")
    digests = []
    for _ in range(3):
        output, run = run_stream(observed)
        if output is None:
            raise RuntimeError("repeat surrogate rejected a pinned signal: " + run["status"])
        digests.append(sha256(canonical_bytes(output)))
    return {
        "count": 3,
        "digests": digests,
        "byte_identical": len(set(digests)) == 1,
        "note": "Three fresh streaming controllers over one pinned synthetic probe; no tolerance.",
    }


def gates() -> List[Dict[str, str]]:
    names = [
        "exact_upstream_asset_and_runtime_rights",
        "real_streaming_onnx_parity",
        "held_out_real_paired_denoising_cohort",
        "independent_listening_or_authorized_screen",
        "target_runtime_deadline_and_memory",
        "provider_intake_and_descriptor_review",
        "public_default_selection",
        "exact_approved_external_reference_parity",
    ]
    return [{"name": name, "status": "blocked",
             "reopen_condition": "Independent cleared evidence required; a missing result never qualifies."}
            for name in names]


def acceptance_profile() -> Dict[str, Any]:
    pinned = SOURCE_PINS["source:audio-benchmark-platform/plan/swarm/VERIFICATION.md"]
    return {
        "profile": PROFILE,
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": pinned,
        "mapped_cases": {
            "identity_noisy_control": {
                "evidence": ["controls.identity", "controls.named_baseline",
                             "conditions.identity", "conditions.noisy_control"],
                "status": "measured_synthetic",
            },
            "established_task_matched_baseline": {
                "name": "noisy_input_no_processing",
                "evidence": ["controls.named_baseline"],
                "status": "measured_synthetic",
            },
            "paired_si_sdr_stoi": {
                "evidence": ["conditions.*.baseline_metrics", "conditions.*.candidate_metrics"],
                "status": "measured_synthetic",
                "scorer": SCORER_ID,
                "note": ("Paired synthetic clean references only; the surrogate is not the "
                         "model and no real-speech score is claimed."),
            },
            "clean_speech_preservation": {
                "evidence": ["controls.clean_speech_preservation", "conditions.identity",
                             "identity_reconstruction"],
                "status": "measured_synthetic",
            },
            "peaks_and_invalid_outputs": {
                "evidence": ["conditions.*.candidate_metrics", "adverse"],
                "status": "measured_synthetic",
            },
            "unpaired_speech": {
                "status": "not_applicable",
                "reason": "No licensed unpaired speech, predictive screen or authorized listening was run.",
            },
            "alignment_state_memory_timing": {
                "status": "partial_analytical",
                "alignment": ("hop 256, centered-STFT lookahead 256 samples (16 ms), "
                              "WOLA content delay 512 samples (32 ms) at 16 kHz"),
                "state": ("modeled conv/tra/inter cache shapes plus persistent analysis, "
                          "WOLA and power state; invalid hops never advance state"),
                "memory": "host Python object counts only; no target-device memory result",
                "timing": "no measured content/availability timing for the exact runtime",
            },
        },
        "not_reported": [
            "real model inference", "real paired cohort", "human listening or MOS",
            "target-device pacing or deadline", "installed runtime memory",
            "ONNX Runtime execution", "release qualification",
        ],
    }


def prior_screen_provenance() -> Dict[str, Any]:
    return {
        "source": "research/dereverberation_candidates_20261028.md",
        "sha256": SOURCE_PINS["source:research/dereverberation_candidates_20261028.md"],
        "status": "source_reported_prior_screen",
        "used_for_qualification": False,
        "measured_here": False,
        "reported": {
            "candidate": "gtcrn_simple.onnx (upstream GTCRN streaming ONNX)",
            "paired_cases": 72,
            "median_si_sdr_db": 5.66,
            "identity_median_si_sdr_db": 16.49,
            "paired_si_sdr_wins_over_identity": "0/72",
            "median_rtf": 0.0459,
            "rtf_p90": 0.0489,
            "rtf_max": 0.0723,
            "frame_kernel_median_ms": 0.71,
            "frame_kernel_p95_ms": 1.38,
            "frame_kernel_p99_ms": 5.36,
            "estimated_stft_lookahead_ms": 16,
            "stoi_measured": False,
        },
        "interpretation": (
            "The pinned cross-domain dereverberation screen lost to identity. It does not "
            "qualify GTCRN as a dereverberator and it does not qualify it as a denoiser; "
            "denoising must be validated separately. No number above is reproduced here."
        ),
    }


def independent_timing_evidence() -> Dict[str, Any]:
    return {
        "status": "source_reported_proposal_only",
        "used_for_qualification": False,
        "measured_here": False,
        "target_device": False,
        "references": [
            {
                "source": "REALTIME_COMPONENT_CANDIDATES.md",
                "sha256": SOURCE_PINS["source:REALTIME_COMPONENT_CANDIDATES.md"],
                "statement": ("Stateful spectrum-frame path, median RTF 0.0459, estimated "
                              "16 ms STFT lookahead; local dereverb screen lost to identity."),
            },
            {
                "source": "research/dereverberation_candidates_20261028.md",
                "sha256": SOURCE_PINS["source:research/dereverberation_candidates_20261028.md"],
                "statement": ("Median inference RTF 0.0459, p90 0.0489, max 0.0723 and frame "
                              "kernel p99 5.36 ms against a 16 ms hop on the screen host."),
            },
        ],
        "note": ("Independent provenance only. These values are not reproduced, pooled, "
                 "assigned to this surrogate or used as an acceptance threshold."),
    }


def asset_boundary() -> Dict[str, Any]:
    return {
        "mode": "caller_supplied_asset_reference",
        "expected_filename": ASSET_FILENAME,
        "asset_present": False,
        "asset_sha256": None,
        "asset_byte_size": None,
        "asset_source_uri": None,
        "asset_rights_verified": False,
        "onnx_runtime_available": False,
        "onnx_runtime_invoked": False,
        "real_path_status": "rejected_asset_unavailable",
        "surrogate_path": SURROGATE_MODE,
        "silent_fallback_to_surrogate": False,
        "required_before_real_path": [
            "immutable upstream source revision",
            "immutable weight asset URI and SHA-256",
            "weight license permitting evaluation and redistribution as intended",
            "pinned ONNX Runtime version and redistribution terms",
        ],
        "tensor_contract": {
            "inputs": {
                "mix": {"shape": [1, STFT_BINS, 1, 2], "dtype": "float32"},
                "conv_cache": {"shape": STATE_CACHES["conv_cache"], "dtype": "float32"},
                "tra_cache": {"shape": STATE_CACHES["tra_cache"], "dtype": "float32"},
                "inter_cache": {"shape": STATE_CACHES["inter_cache"], "dtype": "float32"},
            },
            "outputs": {
                "enhanced": {"shape": [1, STFT_BINS, 1, 2], "dtype": "float32"},
                "conv_cache": {"shape": STATE_CACHES["conv_cache"], "dtype": "float32"},
                "tra_cache": {"shape": STATE_CACHES["tra_cache"], "dtype": "float32"},
                "inter_cache": {"shape": STATE_CACHES["inter_cache"], "dtype": "float32"},
            },
            "note": ("Declared from the pinned adapter; not verified against a real model file "
                     "because no asset is present and no download is permitted."),
        },
    }


def readiness() -> Dict[str, Any]:
    blocker = (
        "No exact GTCRN weight asset (for example gtcrn_simple.onnx) with an immutable URI, "
        "SHA-256 and byte size is available, and neither the checkpoint license nor the "
        "ONNX Runtime redistribution terms are cleared for this repository. Downloading "
        "weights or invoking ONNX Runtime is out of scope for this task."
    )
    reopen = (
        "A rights-cleared immutable weight asset plus a pinned ONNX Runtime build is "
        "supplied by an authorized caller with recorded SHA-256, byte size, license and "
        "runtime version; then rerun real streaming parity, a held-out real paired denoising "
        "cohort, independent listening, and target-runtime deadline/memory evidence."
    )
    return {
        "conclusion": "not_ready",
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "exact_external_blocker": blocker,
        "reopen_condition": reopen,
        "asset_available": False,
        "runtime_available": False,
        "rights_cleared": False,
        "synthetic_surrogate_only": True,
        "no_missing_result_qualifies_candidate": True,
    }


def rights_gap() -> Dict[str, Any]:
    return {
        "blocked": True,
        "exact_upstream_source_revision_verified": False,
        "model_weight_terms_verified": False,
        "onnx_runtime_redistribution_terms_verified": False,
        "real_model_weights_present": False,
        "vendor_runtime_invoked": False,
        "source_pin": "adapters/gtcrn-streaming/run.py",
        "source_sha256": SOURCE_PINS["source:adapters/gtcrn-streaming/run.py"],
        "statement": (
            "The pinned adapter demonstrates a local evaluation path and the pinned research "
            "note calls the upstream code MIT, but no weight file, checkpoint license text or "
            "ONNX Runtime redistribution grant is present here. No weight is downloaded, "
            "vendored or redistributed."
        ),
        "consequence": (
            "No vendoring, installed provider, registry entry, descriptor, default or release "
            "claim is permitted until exact source, weight and runtime rights are cleared."
        ),
    }


def scorer_provenance() -> Dict[str, Any]:
    vectors = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json"
    payload = strict_json(vectors)
    if not isinstance(payload, list):
        raise ValueError("crosscheck vectors root is not a list")
    return {
        "scorer_id": SCORER_ID,
        "algorithm": "non-extended pystoi 0.4.1 port and zero-mean SI-SDR",
        "inherited_from": "docs/task-evidence/online-multichannel-wpe/scorer.py",
        "inherited_sha256": sha256(
            (SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py").read_bytes()),
        "relationship": "algorithm byte-identical except SCORER_ID",
        "crosscheck_vectors_pin": ARTIFACT_PIN_PATHS[-1],
        "crosscheck_vectors_sha256": sha256(vectors.read_bytes()),
        "crosscheck_vector_count": len(payload),
        "max_abs_si_sdr_delta": max(float(item["si_sdr_abs_delta"]) for item in payload),
        "max_abs_stoi_delta": max(float(item["stoi_abs_delta"]) for item in payload),
        "crosscheck_scope": (
            "Six synthetic vectors inherited from the merged scorer; external numpy/pystoi "
            "values were not rerun here."
        ),
        "used_as_oracle": False,
    }


def build_report() -> Dict[str, Any]:
    condition_map = conditions()
    regressions = []
    for name, value in condition_map.items():
        candidate = value["candidate_metrics"]
        baseline = value["baseline_metrics"]
        if value["candidate_worse_than_baseline"]:
            regressions.append({
                "condition": name,
                "metric": "si_sdr_db",
                "candidate": candidate["si_sdr_db"],
                "baseline": baseline["si_sdr_db"],
                "interpretation": ("Surrogate is worse than the named noisy-input baseline "
                                   "in this synthetic condition."),
            })
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT_ID,
        "reference_family": REFERENCE_FAMILY,
        "family": FAMILY,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local deterministic synthetic evidence at the documented GTCRN streaming "
            "ONNX boundary. No real model, runtime, media, device, listening, benchmark, "
            "provider, installed-behavior or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "model_geometry": MODEL_GEOMETRY,
        "asset_boundary": asset_boundary(),
        "deliverable": (
            "Caller-supplied-asset reference boundary plus a deterministic streaming "
            "surrogate and a strict not-ready conclusion with the exact external blocker."
        ),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": artifact_pins(),
        "acceptance_profile": acceptance_profile(),
        "conditions": condition_map,
        "controls": controls(),
        "identity_reconstruction": identity_reconstruction(),
        "adverse": adverse(),
        "repeatability": repeatability(),
        "regressions": regressions,
        "gates": gates(),
        "independent_timing_evidence": independent_timing_evidence(),
        "prior_screen_provenance": prior_screen_provenance(),
        "readiness": readiness(),
        "rights_gap": rights_gap(),
        "scorer": scorer_provenance(),
        "surrogate_parameters": dict(SURROGATE_PARAMETERS),
        "surrogate_limitations": [
            "The surrogate is not the model: it applies fixed spectral shrinkage, not learned weights.",
            "Synthetic harmonic and white-noise probes do not represent real speech, noise or rooms.",
            "Exact WOLA identity reconstruction is a structural check, not a quality or denoising result.",
            "No measured timing, memory, device, listening, benchmark or release evidence exists.",
        ],
        "missing_evidence": [
            "rights-cleared exact weight asset and ONNX Runtime build",
            "real streaming ONNX parity",
            "held-out real paired denoising cohort",
            "independent listening or authorized predictive screen",
            "target runtime deadline and memory",
            "provider intake and descriptor review",
            "public default selection",
            "exact approved external reference parity",
        ],
        "negative_claims": {
            "real_model_weights": False,
            "real_media": False,
            "device_timing": False,
            "listening_result": False,
            "benchmark_claim": False,
            "release_claim": False,
            "onnx_runtime_invoked": False,
            "provider_registration": False,
            "public_api_abi_change": False,
            "installed_v0_behavior_change": False,
        },
        "evidence_classes": ["synthetic_fixture", "boundary_review",
                             "source_reported_provenance", "readiness_conclusion"],
    }
