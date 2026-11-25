# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the LocalVQE dereverberation-only probe.

This module records the exact LocalVQE compact joint model identity and the
dereverberation-only, zero-far-end-reference engineering scenario as a
caller-supplied external asset.  The exact GGUF model, an admitted isolated
runtime and artifact-specific rights are absent, so the package runs a
deterministic, stdlib-only synthetic boundary surrogate and emits a strict
``DEFER`` / ``incomplete`` / ``not_qualified`` conclusion.

Nothing here downloads, copies, imports, loads or executes LocalVQE, GGML, a
model, a native library, real audio, a corpus or a device clock.  The package
does not register a provider, change the installed v0 path, a descriptor, a
registry, a shared build, a dependency lock or CI, and it does not benchmark or
qualify the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-LOCALVQE-DEREVERBERATION-PROBE"
TITLE = "LocalVQE dereverberation probe"
SLUG = "localvqe-dereverberation-probe"
COMPONENT = "localvqe-dereverberation-probe"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "ccb963f3b05519547328f647dfb0656170c3354b"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-LOCALVQE-DEREVERBERATION-PROBE"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
SCENARIO_ID = "localvqe-dereverb-zero-far-end-probe-v1"

UPSTREAM_REPOSITORY = "https://github.com/localai-org/LocalVQE"
UPSTREAM_COMMIT = "7f61cd05095d42e56a135b303f5bb4d761da22b9"
UPSTREAM_LICENSE = "Apache-2.0"
UPSTREAM_LINE = "compact GTCRN-AEC 49K joint AEC/NS/dereverb line"
MODEL_FILENAME = "localvqe-pi-v1-49k-f32.gguf"
MODEL_PATH = "data/models/localvqe/" + MODEL_FILENAME
MODEL_SHA256 = (
    "0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26")
ECHO_MODEL_FILENAME = "localvqe-pi-aec-v1-49k-f32.gguf"
ECHO_MODEL_PATH = "data/models/localvqe/" + ECHO_MODEL_FILENAME
ECHO_MODEL_SHA256 = (
    "b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8")
LIBRARY_FILENAME = "liblocalvqe.0.1.0.dylib"
LIBRARY_PATH = "data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib"
LIBRARY_SHA256 = (
    "bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298")
RUNTIME_ENV_PATH = "data/envs/" + SLUG
ADAPTER_PATH = "adapters/localvqe/README.md"
ADAPTER_RUN_PATH = "adapters/localvqe/run.py"
ECHO_ADAPTER_PATH = "adapters/localvqe-aec/README.md"
DEREVERB_RESEARCH_PATH = "research/dereverberation_candidates_20261028.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-DUPLEX",
        "SDK-FND-EVIDENCE",
        "SDK-FND-NN",
        "SDK-FND-PROVIDER",
    ],
    "id": TASK,
    "mode": "implementation",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "d7080237af4b67bfb730f127cd743e077e46b348c35c6c2ab58eef6b98b79e90")

def board_row_digest() -> str:
    """Digest only the stable linked-row identity, never the mutable file."""
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Deterministic fixture geometry
# ---------------------------------------------------------------------------

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 256
FRAME_DURATION_MS = 16
TOTAL_FRAMES = 250
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
LATENCY_SAMPLES = 256
LATENCY_MS = 16
EARLY_WINDOW_SAMPLES = 800
EARLY_WINDOW_MS = 50
HISTORY_SAMPLES = 4096

SINE64: Tuple[int, ...] = (
    0, 3212, 6393, 9512, 12539, 15446, 18204, 20787,
    23170, 25329, 27245, 28898, 30273, 31356, 32137, 32609,
    32767, 32609, 32137, 31356, 30273, 28898, 27245, 25329,
    23170, 20787, 18204, 15446, 12539, 9512, 6393, 3212,
    0, -3212, -6393, -9512, -12539, -15446, -18204, -20787,
    -23170, -25329, -27245, -28898, -30273, -31356, -32137, -32609,
    -32767, -32609, -32137, -31356, -30273, -28898, -27245, -25329,
    -23170, -20787, -18204, -15446, -12539, -9512, -6393, -3212,
)

SEGMENT_FRAMES = 50
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "start_frame": 0, "end_frame": 50, "kind": "silence"},
    {"id": "speech-a", "start_frame": 50, "end_frame": 100, "kind": "speech",
     "steps": (1, 2, 3), "amplitudes": (460, 256, 154)},
    {"id": "speech-b", "start_frame": 100, "end_frame": 150, "kind": "speech",
     "steps": (2, 3, 5), "amplitudes": (420, 280, 170),
     "click_period": 1024, "click_amplitude": 9000},
    {"id": "noisy-speech", "start_frame": 150, "end_frame": 200,
     "kind": "speech", "steps": (3, 4, 6), "amplitudes": (440, 250, 160),
     "noise_gain": 2},
    {"id": "tail-after-speech", "start_frame": 200, "end_frame": 250,
     "kind": "silence"},
)

# Early response within the 50 ms target window: (delay_samples, gain/1024).
EARLY_TAPS: Tuple[Tuple[int, int], ...] = (
    (16, 850), (64, 330), (160, 210), (384, 120), (640, 70), (752, 40))
# Late response after 50 ms: (delay_samples, gain/1024), 160-sample spacing.
LATE_TAPS: Tuple[Tuple[int, int], ...] = (
    (800, 230), (960, 184), (1120, 147), (1280, 117), (1440, 94),
    (1600, 75), (1760, 60), (1920, 48), (2080, 38), (2240, 30),
    (2400, 24), (2560, 19), (2720, 15), (2880, 12), (3040, 10),
    (3200, 8))
# Fixed causal late-reverberation predictor: 72% of the first ten late taps.
PREDICTOR_TAPS: Tuple[Tuple[int, int], ...] = tuple(
    (delay, max(1, (gain * 72) // 100)) for delay, gain in LATE_TAPS[:10])

CONFIG: Dict[str, Any] = {
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "library_used": False,
    "model_used": False,
    "real_runtime": False,
    "reference_mode": "zero_far_end",
    "render_delay_samples": 0,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "variant": "compact-full",
}

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "frame_samples",
    "input_format",
    "library_path",
    "library_sha256",
    "model_path",
    "model_sha256",
    "reference_mode",
    "render_delay_samples",
    "sample_rate_hz",
    "source_commit",
    "variant",
}
PINNED_ASSET_VALUES: Dict[str, Any] = {
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "reference_mode": "zero_far_end",
    "render_delay_samples": 0,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "source_commit": UPSTREAM_COMMIT,
    "variant": "compact-full",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": (
        "validate_hash_geometry_and_scenario_only; do_not_load_or_execute_"
        "in_this_package"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "requires_far_end_reference": False,
    "scenario_reference_mode": "zero_far_end",
    "separate_model_archive_required": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "model_path and library_path are caller-owned absolute paths",
        "SHA-256 of the model file and native library match the manifest",
        "source_commit equals the pinned LocalVQE provenance revision",
        "variant, sample rate, channels, frame size and input format equal "
        "the compact joint model geometry",
        "render_delay_samples is zero and algorithmic_latency_samples is one "
        "256-sample hop",
        "reference_mode is zero_far_end; paired-reference AEC is a separate "
        "task and is rejected here",
        "the pinned model digest is checked separately; a hash-matched "
        "placeholder is never accepted as the pinned joint model",
        "no download, copy, build, import, load or execution occurs in this "
        "package",
    ],
    "weights_embedded_in_wheel": False,
}

FORMAT: Dict[str, Any] = {
    "algorithmic_latency_ms": LATENCY_MS,
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "asset_channels": CHANNELS,
    "asset_frame_duration_ms": FRAME_DURATION_MS,
    "asset_frame_samples": FRAME_SAMPLES,
    "asset_requires_far_end_reference": False,
    "asset_sample_format": "float32",
    "asset_sample_rate_hz": SAMPLE_RATE_HZ,
    "early_window_ms": EARLY_WINDOW_MS,
    "early_window_samples": EARLY_WINDOW_SAMPLES,
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "window_frames": TOTAL_FRAMES,
    "window_samples": TOTAL_SAMPLES,
}

# ---------------------------------------------------------------------------
# Canonical JSON and hashing
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      indent=2)
    return (text + "\n").encode("utf-8")


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def _metric(value: float | None) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("metric_nonfinite")
    rounded = round(value, 9)
    return 0.0 if rounded == 0.0 else rounded


def workspace_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override).resolve()
    for parent in HERE.parents:
        if (parent / "adapters").is_dir() and \
                (parent / "audio-benchmark-platform").is_dir():
            return parent
    raise ValueError("workspace_root_not_found")


def resolve_source_path(name: str) -> Path:
    return workspace_root() / name


# ---------------------------------------------------------------------------
# Deterministic synthetic fixture
# ---------------------------------------------------------------------------


def _clip16(value: int) -> int:
    if value > 32767:
        return 32767
    if value < -32768:
        return -32768
    return value


def _envelope(index: int, length: int) -> int:
    fade = 512
    if index < fade:
        return (index * 1024) // fade
    if index >= length - fade:
        return ((length - 1 - index) * 1024) // fade
    return 1024


def _clean_track() -> List[int]:
    track = [0] * TOTAL_SAMPLES
    for segment in SEGMENTS:
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        if segment["kind"] == "silence":
            continue
        phases = [0, 0, 0]
        for offset in range(end - start):
            sample = 0
            for channel in range(3):
                phases[channel] = (phases[channel] + segment["steps"][channel]) \
                    & 63
                sample += segment["amplitudes"][channel] * \
                    SINE64[phases[channel]]
            sample >>= 10
            if "click_period" in segment and offset % segment["click_period"] < 4:
                sign = 1 if (offset // segment["click_period"]) % 2 == 0 else -1
                sample += sign * segment["click_amplitude"]
            sample = (sample * _envelope(offset, end - start)) >> 10
            track[start + offset] = _clip16(sample)
    return track


def _noise_track() -> List[int]:
    noise = [0] * TOTAL_SAMPLES
    seed = 123456789
    for segment in SEGMENTS:
        gain = segment.get("noise_gain")
        if not gain:
            continue
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        for index in range(start, end):
            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            value = ((seed >> 16) % 2001) - 1000
            noise[index] = _clip16(value * gain)
    return noise


def _convolve(clean: Sequence[int], taps: Sequence[Tuple[int, int]]
              ) -> List[int]:
    output = [0] * len(clean)
    for delay, gain in taps:
        for index in range(delay, len(clean)):
            output[index] += (clean[index - delay] * gain) >> 10
    return output


def build_fixture() -> Dict[str, List[int]]:
    clean = _clean_track()
    early = _convolve(clean, EARLY_TAPS)
    late = _convolve(clean, LATE_TAPS)
    noise = _noise_track()
    reverb = [
        _clip16(early[index] + late[index] + noise[index])
        for index in range(TOTAL_SAMPLES)
    ]
    return {"clean": clean, "early": early, "late": late,
            "noise": noise, "reverb": reverb}


def as_float(values: Sequence[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def segment_for_sample(index: int) -> Dict[str, Any]:
    for segment in SEGMENTS:
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        if start <= index < end:
            return segment
    raise ValueError("sample_out_of_range")


def fixture_spec() -> Dict[str, Any]:
    return {
        "early_taps": [list(tap) for tap in EARLY_TAPS],
        "early_window_samples": EARLY_WINDOW_SAMPLES,
        "fixture_id": "localvqe-dereverb-zero-reference-room-fixture-v1",
        "late_taps": [list(tap) for tap in LATE_TAPS],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [dict(segment) for segment in SEGMENTS],
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))


def component_digests(components: Dict[str, List[int]]) -> Dict[str, str]:
    return {
        key: sha256(canonical_bytes(components[key]))
        for key in ("clean", "early", "late", "noise", "reverb")
    }


FIXTURE_COMPONENTS = build_fixture()
FIXTURE_DIGESTS = component_digests(FIXTURE_COMPONENTS)

# ---------------------------------------------------------------------------
# Strict frame and config validation
# ---------------------------------------------------------------------------


def validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    if set(config) != set(CONFIG):
        raise ValueError("config_key_set_mismatch")
    for key, expected in CONFIG.items():
        value = config[key]
        if isinstance(expected, bool):
            if value is not expected:
                raise ValueError("config_mismatch:" + key)
            continue
        if isinstance(value, bool):
            raise ValueError("config_bool:" + key)
        if value != expected:
            raise ValueError("config_mismatch:" + key)


def _validate_frame(frame: Any, label: str, allow_partial: bool = False
                    ) -> List[float]:
    if not isinstance(frame, (list, tuple)):
        raise ValueError(label + "_not_sequence")
    if allow_partial:
        if not 1 <= len(frame) <= FRAME_SAMPLES:
            raise ValueError(label + "_length")
    elif len(frame) != FRAME_SAMPLES:
        raise ValueError(label + "_length")
    values: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError(label + "_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError(label + "_nonfinite")
        if abs(value) > 1.0:
            raise ValueError(label + "_range")
        values.append(value)
    return values


# ---------------------------------------------------------------------------
# Deterministic model-free boundary surrogate
# ---------------------------------------------------------------------------


def _late_estimate(history: Sequence[float]) -> float:
    total = 0.0
    base = len(history)
    for delay, gain in PREDICTOR_TAPS:
        index = base - delay
        if index >= 0:
            total += (gain / 1024.0) * history[index]
    return total


class Session:
    """Stateful one-frame-delayed zero-reference streaming session."""

    def __init__(self, config: Dict[str, Any], session_id: str,
                 epoch: int = 0) -> None:
        validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self.config = dict(config)
        self.session_id = session_id
        self._reset(epoch)

    def _reset(self, epoch: int) -> None:
        self.epoch = epoch
        self.history: List[float] = [0.0] * HISTORY_SAMPLES
        self.pending: List[float] = [0.0] * LATENCY_SAMPLES
        self.frames: List[Dict[str, Any]] = []
        self.closed = False
        self.final_seen = False
        self.drained = False
        self.counters: Dict[str, int] = {
            "accepted_input_samples": 0,
            "discarded_padding_samples": 0,
            "frames": 0,
            "nonfinite_output_samples": 0,
            "produced_output_samples": 0,
            "rejected_calls": 0,
            "valid_output_samples": 0,
        }

    def reset(self, epoch: int) -> None:
        if self.closed:
            raise ValueError("session_closed")
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise ValueError("invalid_epoch")
        if epoch <= self.epoch:
            raise ValueError("epoch_not_greater")
        self._reset(epoch)

    def state_digest(self) -> str:
        payload = {
            "epoch": self.epoch,
            "final_seen": self.final_seen,
            "history": [repr(value) for value in self.history[-64:]],
            "pending": [repr(value) for value in self.pending[:64]],
        }
        return sha256(canonical_bytes(payload))

    def process_frame(self, mic_frame: Any, final: bool = False
                      ) -> List[float]:
        if self.closed:
            self.counters["rejected_calls"] += 1
            raise ValueError("session_closed")
        if self.final_seen:
            self.counters["rejected_calls"] += 1
            raise ValueError("final_already_seen")
        if not isinstance(final, bool):
            self.counters["rejected_calls"] += 1
            raise ValueError("invalid_final_flag")
        try:
            values = _validate_frame(mic_frame, "mic", allow_partial=final)
        except ValueError:
            self.counters["rejected_calls"] += 1
            raise
        valid = len(values)
        padded = values + [0.0] * (FRAME_SAMPLES - valid)
        processed: List[float] = []
        for value in padded:
            estimate = _late_estimate(self.history)
            processed.append(value - estimate)
            self.history.append(value)
        del self.history[:-HISTORY_SAMPLES]
        if any(not math.isfinite(value) for value in processed):
            self.counters["nonfinite_output_samples"] += len(processed)
            raise ValueError("surrogate_nonfinite")
        self.pending.extend(processed)
        output = self.pending[:FRAME_SAMPLES]
        self.pending = self.pending[FRAME_SAMPLES:]
        if len(output) != FRAME_SAMPLES:
            raise ValueError("surrogate_internal_length")
        frame_index = len(self.frames)
        self.counters["accepted_input_samples"] += valid
        self.counters["discarded_padding_samples"] += FRAME_SAMPLES - valid
        self.counters["frames"] += 1
        self.counters["produced_output_samples"] += FRAME_SAMPLES
        self.counters["valid_output_samples"] += FRAME_SAMPLES
        self.frames.append({
            "frame_index": frame_index,
            "input_valid": valid,
            "output_valid": FRAME_SAMPLES,
            "startup": frame_index == 0,
            "source_first_sample": frame_index * FRAME_SAMPLES,
            "final": final,
        })
        if final:
            self.final_seen = True
        return output

    def drain(self) -> Tuple[List[float], int]:
        if self.closed:
            raise ValueError("session_closed")
        if not self.final_seen:
            raise ValueError("drain_before_final")
        if self.drained:
            raise ValueError("drain_twice")
        self.drained = True
        output = self.pending
        self.pending = []
        valid = self.frames[-1]["input_valid"] if self.frames else 0
        self.counters["produced_output_samples"] += FRAME_SAMPLES
        self.counters["valid_output_samples"] += valid
        self.closed = True
        return output, valid

    def report(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "epoch": self.epoch,
            "frames": len(self.frames),
            "session_id": self.session_id,
            "state_digest": self.state_digest(),
        }


def drive_streaming(samples: Sequence[float], chunk: int | None = None,
                    session: Session | None = None) -> Dict[str, Any]:
    if session is None:
        session = Session(CONFIG, "probe", 0)
    if chunk is None or chunk <= 0:
        chunk = FRAME_SAMPLES
    total_frames = (len(samples) + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    output: List[float] = []
    buffer: List[float] = []
    fed = 0
    position = 0
    while position < len(samples):
        take = min(chunk, len(samples) - position)
        buffer.extend(samples[position:position + take])
        position += take
        while len(buffer) >= FRAME_SAMPLES:
            fed += 1
            is_last = fed == total_frames
            output.extend(session.process_frame(
                buffer[:FRAME_SAMPLES], final=is_last))
            buffer = buffer[FRAME_SAMPLES:]
            if is_last:
                buffer = []
    if buffer:
        fed += 1
        output.extend(session.process_frame(buffer, final=True))
    tail, tail_valid = session.drain()
    output.extend(tail)
    return {
        "output": output[:len(samples)],
        "tail_valid": tail_valid,
        "session": session,
        "total_frames": total_frames,
    }


def run_offline(samples: Sequence[float]) -> Dict[str, Any]:
    return drive_streaming(samples, chunk=len(samples))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def si_sdr(estimate: Sequence[float], reference: Sequence[float]
           ) -> float | None:
    if len(estimate) != len(reference):
        raise ValueError("si_sdr_length_mismatch")
    numerator = sum(a * b for a, b in zip(estimate, reference))
    denominator = sum(b * b for b in reference)
    if denominator == 0.0:
        return None
    alpha = numerator / denominator
    noise = 0.0
    target = 0.0
    for a, b in zip(estimate, reference):
        projected = alpha * b
        target += projected * projected
        difference = a - projected
        noise += difference * difference
    if target == 0.0:
        return None
    if noise == 0.0:
        return 120.0
    return 10.0 * math.log10(target / noise)


def projection_drr(signal: Sequence[float], early: Sequence[float],
                   late: Sequence[float]) -> float | None:
    early_energy = sum(value * value for value in early)
    late_energy = sum(value * value for value in late)
    if early_energy == 0.0 or late_energy == 0.0:
        return None
    early_coefficient = sum(a * b for a, b in zip(signal, early)) / early_energy
    late_coefficient = sum(a * b for a, b in zip(signal, late)) / late_energy
    projected_early = early_coefficient * early_coefficient * early_energy
    projected_late = late_coefficient * late_coefficient * late_energy
    if projected_early <= 0.0 or projected_late <= 0.0:
        return None
    return 10.0 * math.log10(projected_early / projected_late)


def metric_block(components: Dict[str, List[int]],
                 output: Sequence[float]) -> Dict[str, Any]:
    scored = TOTAL_SAMPLES - LATENCY_SAMPLES
    reverb = as_float(components["reverb"])
    early = as_float(components["early"])
    late = as_float(components["late"])
    aligned_output = output[LATENCY_SAMPLES:LATENCY_SAMPLES + scored]
    aligned_early = early[:scored]
    aligned_late = late[:scored]
    unaligned_output = list(output[:scored])
    identity = reverb[:scored]
    strata: Dict[str, Any] = {}
    for segment in SEGMENTS:
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        length = min(end, scored) - start
        if length <= 0:
            continue
        out_window = aligned_output[start:start + length]
        ref_window = aligned_early[start:start + length]
        id_window = identity[start:start + length]
        strata[segment["id"]] = {
            "identity_si_sdr_db": _metric(si_sdr(id_window, ref_window)),
            "output_si_sdr_db": _metric(si_sdr(out_window, ref_window)),
            "samples": length,
        }
    silence_output = [
        output[index] for index in range(0, SEGMENT_FRAMES * FRAME_SAMPLES)
    ]
    return {
        "alignment": {
            "aligned_output_si_sdr_db": _metric(
                si_sdr(aligned_output, aligned_early)),
            "unaligned_output_si_sdr_db": _metric(
                si_sdr(unaligned_output, aligned_early)),
        },
        "drr_projection": {
            "identity_drr_db": _metric(
                projection_drr(identity, aligned_early, aligned_late)),
            "output_drr_db": _metric(
                projection_drr(aligned_output, aligned_early, aligned_late)),
        },
        "identity_si_sdr_db": _metric(si_sdr(identity, aligned_early)),
        "max_abs_output": _metric(max(abs(value) for value in output)),
        "nonfinite_output_samples": sum(
            1 for value in output if not math.isfinite(value)),
        "output_peak_clipped_samples": sum(
            1 for value in output if abs(value) > 1.0),
        "output_si_sdr_db": _metric(si_sdr(aligned_output, aligned_early)),
        "scored_samples": scored,
        "silence_exact_zero": all(value == 0.0 for value in silence_output),
        "strata": strata,
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset contract
# ---------------------------------------------------------------------------


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "asset_not_object")
    _require(set(manifest) == REQUIRED_ASSET_FIELDS, "asset_field_set_mismatch")
    for field in ("model_path", "library_path"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "",
                 "asset_path_not_string:" + field)
        path = Path(value)
        _require(path.is_absolute(), "asset_path_not_absolute:" + field)
        _require(path.is_file(), "asset_file_missing:" + field)
    for field in ("model_sha256", "library_sha256"):
        value = manifest[field]
        _require(isinstance(value, str) and
                 re.fullmatch(r"[0-9a-f]{64}", value) is not None,
                 "asset_hash_not_hex:" + field)
    _require(sha256_file(Path(manifest["model_path"])) ==
             manifest["model_sha256"], "asset_model_hash_mismatch")
    _require(sha256_file(Path(manifest["library_path"])) ==
             manifest["library_sha256"], "asset_library_hash_mismatch")
    for field, expected in PINNED_ASSET_VALUES.items():
        _require(manifest[field] == expected, "asset_value_mismatch:" + field)
    return {
        "accepted": True,
        "executed": False,
        "imported": False,
        "loaded": False,
        "pinned_model": False,
        "validated": True,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    result = validate_caller_asset(manifest)
    _require(manifest["model_sha256"] == MODEL_SHA256,
             "asset_model_hash_not_pinned")
    _require(manifest["library_sha256"] == LIBRARY_SHA256,
             "asset_library_hash_not_pinned")
    result["pinned_model"] = True
    result["loaded"] = False
    result["executed"] = False
    return result


def _rejected(manifest: Any) -> str:
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        return str(error)
    return "accepted"


def _asset_controls() -> Dict[str, Any]:
    baseline = {
        "algorithmic_latency_samples": LATENCY_SAMPLES,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "input_format": "float32",
        "reference_mode": "zero_far_end",
        "render_delay_samples": 0,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_commit": UPSTREAM_COMMIT,
        "variant": "compact-full",
    }
    with tempfile.TemporaryDirectory(prefix="localvqe-dereverb-asset-") as name:
        root = Path(name)
        model = root / MODEL_FILENAME
        library = root / LIBRARY_FILENAME
        model.write_bytes(b"caller-owned-placeholder-model")
        library.write_bytes(b"caller-owned-placeholder-library")
        model_hash = sha256_file(model)
        library_hash = sha256_file(library)
        valid = dict(baseline, model_path=str(model),
                     model_sha256=model_hash, library_path=str(library),
                     library_sha256=library_hash)
        generic = validate_caller_asset(valid)
        cases: Dict[str, str] = {}
        missing = dict(valid)
        missing.pop("reference_mode")
        cases["missing_field"] = _rejected(missing)
        cases["relative_path"] = _rejected(
            dict(valid, model_path=MODEL_FILENAME))
        cases["absent_model"] = _rejected(
            dict(valid, model_path=str(root / "absent.gguf")))
        cases["model_hash"] = _rejected(dict(valid, model_sha256="0" * 64))
        cases["library_hash"] = _rejected(
            dict(valid, library_sha256="0" * 64))
        cases["wrong_commit"] = _rejected(dict(valid, source_commit="0" * 40))
        cases["sample_rate"] = _rejected(dict(valid, sample_rate_hz=48000))
        cases["channels"] = _rejected(dict(valid, channels=2))
        cases["frame"] = _rejected(dict(valid, frame_samples=320))
        cases["format"] = _rejected(dict(valid, input_format="int16"))
        cases["variant"] = _rejected(dict(valid, variant="compact-echo-only"))
        cases["variant_dereverb"] = _rejected(
            dict(valid, variant="dereverb-only"))
        cases["paired_reference"] = _rejected(
            dict(valid, reference_mode="paired_reference"))
        cases["render_delay"] = _rejected(
            dict(valid, render_delay_samples=256))
        cases["latency"] = _rejected(
            dict(valid, algorithmic_latency_samples=0))
        cases["extra_field"] = _rejected(dict(valid, extra=True))
        pinned_placeholder = _rejected(
            dict(valid, model_sha256=MODEL_SHA256,
                 library_sha256=LIBRARY_SHA256))
        workspace_manifest = dict(
            valid, model_path=str(resolve_source_path(MODEL_PATH)),
            library_path=str(resolve_source_path(LIBRARY_PATH)),
            model_sha256=MODEL_SHA256, library_sha256=LIBRARY_SHA256)
        cases["workspace_pinned_absent"] = _rejected(workspace_manifest)
        cases["pinned_placeholder"] = pinned_placeholder
    return {
        "generic_admission": generic,
        "rejections": cases,
        "rejected_all": all(value != "accepted" for value in cases.values()),
        "workspace_model_present": resolve_source_path(MODEL_PATH).is_file(),
    }


def config_adverse_control() -> Dict[str, Any]:
    baseline = Session(CONFIG, "probe", 0)
    cases: Dict[str, str] = {}

    def rejected(name: str, config: Dict[str, Any], session_id: str = "x",
                 epoch: int = 0, bool_epoch: bool = False) -> None:
        try:
            Session(config, session_id,
                    True if bool_epoch else epoch)
        except ValueError as error:
            cases[name] = str(error)
        else:
            cases[name] = "accepted"

    rejected("sample_rate", dict(CONFIG, sample_rate_hz=48000))
    rejected("channels", dict(CONFIG, channels=2))
    rejected("format", dict(CONFIG, input_format="int16"))
    rejected("frame", dict(CONFIG, frame_samples=320))
    rejected("latency", dict(CONFIG, algorithmic_latency_samples=0))
    rejected("render_delay", dict(CONFIG, render_delay_samples=256))
    rejected("reference_mode", dict(CONFIG, reference_mode="paired_reference"))
    rejected("variant", dict(CONFIG, variant="compact-echo-only"))
    rejected("real_runtime", dict(CONFIG, real_runtime=True))
    rejected("model_used", dict(CONFIG, model_used=True))
    rejected("library_used", dict(CONFIG, library_used=True))
    rejected("extra", dict(CONFIG, extra=True))
    rejected("session_id", CONFIG, session_id="")
    rejected("negative_epoch", CONFIG, epoch=-1)
    rejected("bool_epoch", CONFIG, bool_epoch=True)
    return {
        "baseline_digest": baseline.state_digest(),
        "rejections": cases,
        "rejected_all": all(value != "accepted" for value in cases.values()),
    }


def _frame_control_session() -> Session:
    return Session(CONFIG, "frame-control", 0)


def frame_adverse_control() -> Dict[str, Any]:
    session = _frame_control_session()
    baseline = session.state_digest()
    cases: Dict[str, str] = {}

    def rejected(name: str, frame: Any, final: bool = False) -> None:
        before = session.counters["accepted_input_samples"]
        try:
            session.process_frame(frame, final=final)
        except ValueError as error:
            cases[name] = str(error)
            if session.state_digest() != baseline or \
                    session.counters["accepted_input_samples"] != before:
                cases[name] += ":state_mutated"
        else:
            cases[name] = "accepted"

    good = [0.0] * FRAME_SAMPLES
    rejected("empty_final", [], final=True)
    rejected("short_nonfinal", [0.0] * (FRAME_SAMPLES - 1))
    rejected("long_nonfinal", [0.0] * (FRAME_SAMPLES + 1))
    rejected("string", "x" * FRAME_SAMPLES)
    rejected("nan", [math.nan] + good[1:])
    rejected("infinity", [math.inf] + good[1:])
    rejected("negative_infinity", [-math.inf] + good[1:])
    rejected("range", [1.5] + good[1:])
    rejected("negative_range", [-1.5] + good[1:])
    rejected("boolean", [True] + good[1:])
    rejected("nested", [[0.0]] + good[1:])
    rejected("none", [None] + good[1:])
    rejected("partial_nonfinal", [0.0] * 128)
    accepted = [0.1] * FRAME_SAMPLES
    output = session.process_frame(accepted, final=False)
    return {
        "accepted_after_rejections": True,
        "accepted_output_length": len(output),
        "counter_after_accept": session.counters["accepted_input_samples"],
        "baseline_digest": baseline,
        "rejections": cases,
        "rejected_all": all(value != "accepted" for value in cases.values()),
    }


def streaming_parity_control(components: Dict[str, List[int]]
                             ) -> Dict[str, Any]:
    samples = as_float(components["reverb"])
    reference = run_offline(samples)
    results: Dict[str, Any] = {}
    for chunk in (160, 480, 800, 320, 256, 137, 641):
        result = drive_streaming(samples, chunk=chunk)
        results[str(chunk)] = {
            "byte_identical": result["output"] == reference["output"],
            "tail_valid": result["tail_valid"],
        }
    return {
        "chunks": results,
        "all_identical": all(item["byte_identical"]
                             for item in results.values()),
        "reference_tail_valid": reference["tail_valid"],
    }


def partial_tail_control(components: Dict[str, List[int]]) -> Dict[str, Any]:
    full = run_offline(as_float(components["reverb"]))
    length = 1000
    partial = run_offline(as_float(components["reverb"])[:length])
    return {
        "expected_tail_valid": length % FRAME_SAMPLES,
        "length_preserved": len(partial["output"]) == length,
        "prefix_matches_full": partial["output"] == full["output"][:length],
        "tail_valid": partial["tail_valid"],
    }


def reset_control(components: Dict[str, List[int]]) -> Dict[str, Any]:
    samples = as_float(components["reverb"])[:FRAME_SAMPLES * 3]
    first = Session(CONFIG, "reset-probe", 1)
    for index in range(3):
        first.process_frame(samples[index * FRAME_SAMPLES:(index + 1) *
                                    FRAME_SAMPLES], final=index == 2)
    first.drain()
    reset_digest = first.state_digest()
    fresh = Session(CONFIG, "reset-probe", 1)
    for index in range(3):
        fresh.process_frame(samples[index * FRAME_SAMPLES:(index + 1) *
                                    FRAME_SAMPLES], final=index == 2)
    fresh.drain()
    stale_session = Session(CONFIG, "reset-probe", 0)
    stale_session.process_frame(samples[:FRAME_SAMPLES])
    before_stale = stale_session.state_digest()
    epoch_cases: Dict[str, str] = {}
    for name, epoch in (("same", 0), ("lower", -1)):
        try:
            stale_session.reset(epoch)
        except ValueError as error:
            epoch_cases[name] = str(error)
        else:
            epoch_cases[name] = "accepted"
    accepted_session = Session(CONFIG, "reset-probe", 1)
    accepted_ok = True
    try:
        accepted_session.reset(2)
    except ValueError:
        accepted_ok = False
    return {
        "epoch_rejections": epoch_cases,
        "fresh_matches_reset": first.state_digest() == fresh.state_digest(),
        "higher_epoch_accepted": accepted_ok,
        "reset_digest": reset_digest,
        "stale_digest_unchanged": stale_session.state_digest() == before_stale,
    }


def best_alignment_lag(signal: Sequence[float], reference: Sequence[float],
                       max_lag: int = 256) -> Dict[str, Any]:
    if len(signal) < len(reference) + max_lag:
        raise ValueError("alignment_length_mismatch")
    length = len(reference)
    best_lag = -1
    best_error = None
    for lag in range(max_lag + 1):
        error = sum(
            (signal[lag + index] - reference[index]) ** 2
            for index in range(length)) / length
        if best_error is None or error < best_error:
            best_error = error
            best_lag = lag
    return {
        "best_lag_samples": best_lag,
        "mean_squared_error": _metric(best_error),
    }


def delay_control(components: Dict[str, List[int]],
                  output: Sequence[float]) -> Dict[str, Any]:
    scored = TOTAL_SAMPLES - LATENCY_SAMPLES
    early = as_float(components["early"])
    reverb = as_float(components["reverb"])
    reference = early[:scored]
    aligned = si_sdr(output[LATENCY_SAMPLES:LATENCY_SAMPLES + scored],
                     reference)
    unaligned = si_sdr(output[:scored], reference)
    aligned_error = sum(
        (output[LATENCY_SAMPLES + index] - reference[index]) ** 2
        for index in range(scored))
    unaligned_error = sum(
        (output[index] - reference[index]) ** 2 for index in range(scored))
    error_ratio = None
    if aligned_error > 0.0 and unaligned_error > 0.0:
        error_ratio = 10.0 * math.log10(unaligned_error / aligned_error)
    return {
        "aligned_si_sdr_db": _metric(aligned),
        "alignment_gain_db": _metric(
            None if aligned is None or unaligned is None
            else aligned - unaligned),
        "error_energy_improvement_db": _metric(error_ratio),
        "identity_best_alignment": best_alignment_lag(
            reverb, reference, max_lag=256),
        "output_best_alignment": best_alignment_lag(
            output, reference, max_lag=256),
        "unaligned_si_sdr_db": _metric(unaligned),
    }


def silence_control() -> Dict[str, Any]:
    length = FRAME_SAMPLES * 2
    result = run_offline([0.0] * length)
    return {
        "exact_zero": all(value == 0.0 for value in result["output"]),
        "length": len(result["output"]),
        "tail_valid": result["tail_valid"],
    }


def impulse_control() -> Dict[str, Any]:
    length = FRAME_SAMPLES * 16
    source_index = 2000
    samples = [0.0] * length
    samples[source_index] = 0.5
    result = run_offline(samples)
    output = result["output"]
    peak_index = max(range(len(output)), key=lambda index: abs(output[index]))
    return {
        "expected_output_index": source_index + LATENCY_SAMPLES,
        "finite": all(math.isfinite(value) for value in output),
        "length": len(output),
        "observed_peak_index": peak_index,
        "peak_value": _metric(output[peak_index]),
        "source_index": source_index,
    }


def nonfinite_counter_control() -> Dict[str, Any]:
    session = Session(CONFIG, "nonfinite-probe", 0)
    frame = [0.0] * FRAME_SAMPLES
    frame[17] = math.nan
    before = dict(session.counters)
    try:
        session.process_frame(frame)
    except ValueError as error:
        reason = str(error)
    else:
        reason = "accepted"
    return {
        "accepted_counter_unchanged": (
            session.counters["accepted_input_samples"] ==
            before["accepted_input_samples"]),
        "counted_as_silence": False,
        "reason": reason,
        "state_digest_unchanged": session.state_digest() == Session(
            CONFIG, "nonfinite-probe", 0).state_digest(),
    }


# ---------------------------------------------------------------------------
# Static evidence model
# ---------------------------------------------------------------------------

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "model_absent",
        "requirement": (
            "Supply the exact LocalVQE compact joint checkpoint "
            "localvqe-pi-v1-49k-f32.gguf with SHA-256 "
            "0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26 "
            "as a caller-owned external asset, verified locally without a "
            "network download."),
        "state": (
            "data/models/localvqe/localvqe-pi-v1-49k-f32.gguf is absent; no "
            "dereverberation-only checkpoint is published upstream, so this "
            "probe can only test a zero-reference use of the joint model."),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Admit an isolated, hash-pinned CPython runtime and a native "
            "liblocalvqe built reproducibly from the pinned source revision; "
            "record the exact archive, build flags, ABI, distribution and "
            "product-use terms."),
        "state": (
            "No data/envs/localvqe-dereverberation-probe environment exists. "
            "A dylib is present in the source checkout, but it was not read, "
            "hashed, loaded or executed here, and observed presence is not "
            "runtime admission or reproducibility evidence."),
    },
    {
        "id": "rights_unresolved",
        "requirement": (
            "Supply written model-weight, training-data, corpus, "
            "redistribution, product-use and derivative-output terms plus the "
            "complete notice bundle for the exact checkpoint and runtime."),
        "state": (
            "The source repository states Apache-2.0, but the checkpoint, "
            "training data, evaluation corpora and native packaging have no "
            "artifact-specific rights record. Nothing may be bundled, "
            "rehosted, rebranded or deployed."),
    },
    {
        "id": "scenario_and_evidence_absent",
        "requirement": (
            "Establish that a zero far-end reference is an intended and valid "
            "dereverberation-only condition, then reproduce approved exact-"
            "runtime outputs and score a rights-cleared paired reverberant/"
            "early-target cohort with independent intrusive metrics or "
            "permitted listening and target-device timing."),
        "state": (
            "The model is trained for joint AEC/NS/dereverberation and the "
            "upstream adapter states that the zero-reference mono screen is "
            "outside the model's intended AEC condition. No exact output "
            "vector, rights-cleared cohort, independent score, listening "
            "result, target timing or provider intake exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_model_identity",
     "Local model file matches the pinned filename, byte count and SHA-256; "
     "provenance revision is immutable and verified without a download."),
    ("runtime_admission",
     "Hash-pinned isolated runtime and reproducibly built native library; "
     "archive, flags, ABI and distribution terms recorded."),
    ("artifact_rights",
     "Checkpoint, training-data, runtime, corpus, redistribution, product-use "
     "and derivative-output rights cleared with complete notices."),
    ("exact_reference_parity",
     "Approved exact-runtime zero-far-end output vector and byte-level parity "
     "on the declared 16 kHz / 256-sample geometry."),
    ("zero_reference_scenario_validity",
     "Evidence that the dereverb-only zero far-end condition is intended, or "
     "reclassification as a paired-reference AEC task with a real render."),
    ("rights_cleared_paired_cohort",
     "Frozen rights-cleared reverberant corpus, measured or frozen RIRs, "
     "early-target definition, strata and exact reset/delay schedule."),
    ("independent_scoring_and_listening",
     "Independent SI-SDR/STOI/SRMR or permitted listening, including identity "
     "and task-matched baselines, with failure and nonfinite controls."),
    ("target_runtime_timing_and_opt_in_provider",
     "Target-device p50/p95/p99, RTF, memory, deadline and one-hop latency, "
     "plus opt-in provider intake, descriptor review and default decision."),
)

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "onnxruntime_invoked": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No LocalVQE output, checkpoint, derived weight or native call was produced.",
    "No dereverberation, echo, noise, quality, latency or release result is claimed.",
    "The synthetic surrogate is not LocalVQE and cannot qualify the candidate.",
    "The zero-far-end condition is an engineering misuse screen, not AEC and not a fair dereverberation benchmark.",
    "No real corpus, room impulse response, audio, device clock or listener was used.",
    "No provider, descriptor, registry, installed v0 path, shared build, dependency lock or CI was changed.",
    "Identity is the only paired control; no candidate result is promoted to a pass.",
)

# Source pins are relative to the research workspace root.
SOURCE_PINS: Dict[str, str] = {
    "adapters/localvqe/README.md":
        "b964486bb1f823f9ce6ad52b10210d04b596a8642bda5b46aedb0532eea808e0",
    "adapters/localvqe/run.py":
        "9f4f331faa5191e05dd8a693d0e0d7f7083b92512059e4320c8269b920c251c6",
    "adapters/localvqe-aec/README.md":
        "61240419dc9d46af2056316f2a7167b833fb80e9d6a4ce8470b94a8cde488cd1",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "data/checkouts/LocalVQE/LICENSE":
        "84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54",
    "data/checkouts/LocalVQE/README.md":
        "2eeed279c971cce67f7897ae51bc9c8552c0e88bdd715d27520f956262d2423c",
    "data/checkouts/LocalVQE/ggml/localvqe_api.h":
        "ef2871bde8cd8fe9aa8cd5c3b7d11cc72efb7bb1cc29f726522ace87ad490877",
    "data/checkouts/LocalVQE/ggml/model_hash.cpp":
        "bbdd538da35f67c70a6726f3c6abf2671e01c5dfb2ce86392ff14acbcc043d58",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# Boundary pins are relative to this SDK worktree.
BOUNDARY_PINS: Dict[str, str] = {
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts", "external")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
    "external": ("<!-- digest-table: external -->",
                 "<!-- digest-table: end -->"),
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}

# ---------------------------------------------------------------------------
# Report, contract and manifest builders
# ---------------------------------------------------------------------------


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "mapped_cases": [
            "frozen synthetic room response, channel, rate, hop and excitation",
            "declared one-hop delay with delay-compensated and unaligned scoring",
            "silence, speech, noisy-speech and decaying-tail strata",
            "early-target SI-SDR against identity on the same window",
            "projection DRR proxy on the identity and surrogate outputs",
            "peak, clipping, silence exactness and nonfinite-output bounds",
            "zero far-end reference misuse screen, explicitly not AEC",
            "reset schedule and offline/streaming parity",
            "fail-closed caller-asset, frame and config controls",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no LocalVQE model or admitted runtime, so no exact output is reproduced",
            "no paired far-end render, so this is not echo cancellation",
            "no measured room or rights-cleared real paired cohort, so no "
            "generalization or quality claim is made",
            "no target device, so no timing, memory or deadline result is claimed",
            "no independent listening, ASR or intrusive perceptual score is performed",
        ],
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    }


def _report_body() -> Dict[str, Any]:
    components = FIXTURE_COMPONENTS
    samples = as_float(components["reverb"])
    offline = run_offline(samples)
    output = offline["output"]
    metrics = metric_block(components, output)
    contract_payload_value = contract_payload()
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:echo_model": {
                "executed": False,
                "expected_path": ECHO_MODEL_PATH,
                "filename": ECHO_MODEL_FILENAME,
                "loaded": False,
                "present": resolve_source_path(ECHO_MODEL_PATH).is_file(),
                "sha256": ECHO_MODEL_SHA256,
            },
            "asset:joint_model": {
                "executed": False,
                "expected_path": MODEL_PATH,
                "filename": MODEL_FILENAME,
                "loaded": False,
                "present": resolve_source_path(MODEL_PATH).is_file(),
                "sha256": MODEL_SHA256,
            },
            "asset:native_runtime": {
                "admitted": False,
                "executed": False,
                "expected_path": LIBRARY_PATH,
                "filename": LIBRARY_FILENAME,
                "hashed_here": False,
                "loaded": False,
                "observed_presence": "not_evaluated",
                "sha256_recorded_identity": LIBRARY_SHA256,
            },
        },
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "component_id": COMPONENT,
        "contract_sha256": sha256(canonical_bytes(contract_payload_value)),
        "controls": {
            "asset": _asset_controls(),
            "config": config_adverse_control(),
            "delay": delay_control(components, output),
            "frame": frame_adverse_control(),
            "impulse": impulse_control(),
            "nonfinite_counter": nonfinite_counter_control(),
            "partial_tail": partial_tail_control(components),
            "reset": reset_control(components),
            "silence": silence_control(),
            "streaming_parity": streaming_parity_control(components),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "fixture": {
            "component_digests": dict(FIXTURE_DIGESTS),
            "early_taps": [list(tap) for tap in EARLY_TAPS],
            "early_window_ms": EARLY_WINDOW_MS,
            "early_window_samples": EARLY_WINDOW_SAMPLES,
            "fixture_id": fixture_spec()["fixture_id"],
            "late_taps": [list(tap) for tap in LATE_TAPS],
            "segments": [dict(segment) for segment in SEGMENTS],
            "spec_digest": FIXTURE_SPEC_DIGEST,
            "total_frames": TOTAL_FRAMES,
            "total_samples": TOTAL_SAMPLES,
        },
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "requirement": requirement, "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "metrics": metrics,
        "missing_results": [
            "exact LocalVQE inference output",
            "zero-far-end scenario validity",
            "rights-cleared paired reverberant/early-target cohort",
            "independent intrusive score or permitted listening",
            "target-device timing, memory and deadline",
            "opt-in provider intake and default decision",
        ],
        "no_missing_result_qualifies_candidate": True,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Admit the exact checkpoint and a hash-pinned runtime, clear "
            "artifact and corpus rights, establish that the zero-reference "
            "dereverberation-only condition is intended or replace it with a "
            "paired-reference task, reproduce exact-runtime outputs, score a "
            "rights-cleared paired cohort with independent metrics or "
            "permitted listening, measure target timing and complete opt-in "
            "provider intake. Until then the candidate stays DEFER, "
            "incomplete and not qualified."),
        "scenario": {
            "algorithmic_latency_ms": LATENCY_MS,
            "algorithmic_latency_samples": LATENCY_SAMPLES,
            "far_end_reference": "zero",
            "id": SCENARIO_ID,
            "is_aec": False,
            "is_joint_full_paired_reference": False,
            "is_pure_dereverberator": False,
            "note": (
                "The joint model is conditional on a far-end playback "
                "reference. Supplying zeros is an engineering misuse screen "
                "for the dereverberation-only question and does not evaluate "
                "AEC or establish a pure dereverberation model."),
        },
        "schema_id": SCHEMA_ID,
        "status": STATUS,
        "surrogate": {
            "delay_samples": LATENCY_SAMPLES,
            "is_localvqe": False,
            "model_free": True,
            "predictor_taps": [list(tap) for tap in PREDICTOR_TAPS],
            "type": "fixed causal late-reverberation subtraction",
        },
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "commit": UPSTREAM_COMMIT,
            "license": UPSTREAM_LICENSE,
            "line": UPSTREAM_LINE,
            "repository": UPSTREAM_REPOSITORY,
        },
    }


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def build_report() -> Dict[str, Any]:
    report = _plain(_report_body())
    if has_negative_zero(report):
        raise ValueError("negative_zero_in_report")
    return report


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)


def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": (
                "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never read into, hashed by or "
                "pinned to this package."),
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "requirement": requirement, "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no candidate artifact is downloaded, copied, loaded or executed",
            "no model, runtime or corpus claim is made from observed presence",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the pinned checkpoint and an admitted runtime, clear all "
            "artifact and corpus rights, establish zero-reference scenario "
            "validity or replace it with paired-reference AEC, reproduce exact "
            "outputs, score a rights-cleared cohort independently, measure "
            "target timing and complete opt-in provider intake."),
        "reviewer": REVIEWER,
        "scenario": {
            "far_end_reference": "zero",
            "id": SCENARIO_ID,
            "is_aec": False,
            "is_joint_full_paired_reference": False,
            "is_pure_dereverberator": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "commit": UPSTREAM_COMMIT,
            "license": UPSTREAM_LICENSE,
            "model_filename": MODEL_FILENAME,
            "model_path": MODEL_PATH,
            "model_sha256": MODEL_SHA256,
            "repository": UPSTREAM_REPOSITORY,
            "runtime_env_path": RUNTIME_ENV_PATH,
        },
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


# ---------------------------------------------------------------------------
# SOURCES.sha256 and README digest tables
# ---------------------------------------------------------------------------


def _local_manifest_paths() -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable plan/swarm/TASKS.json is never hashed; only "
        f"board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    for digest, path in rows:
        lines.append(f"{digest}  {path}")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or
                path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS} |
            {"sdk:" + name for name in BOUNDARY_PINS} |
            {TASK_PREFIX + name for name in _local_manifest_paths()})


def expected_readme_keys() -> Dict[str, set[str]]:
    external = {
        "asset:echo_model": ECHO_MODEL_SHA256,
        "asset:joint_model": MODEL_SHA256,
        "asset:native_runtime_identity": LIBRARY_SHA256,
    }
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {
            name for name in _local_manifest_paths()
            if name not in ARTIFACT_TABLE_EXCLUDED
        },
        "external": set(external),
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: List[Tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or \
                        re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = resolve_source_path(key[len("source:"):])
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = SDK_ROOT / key[len("sdk:"):]
            elif section == "artifacts":
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            else:
                expected_digest = {
                    "asset:echo_model": ECHO_MODEL_SHA256,
                    "asset:joint_model": MODEL_SHA256,
                    "asset:native_runtime_identity": LIBRARY_SHA256,
                }[key]
                path = None
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if path is not None and path.is_file() and \
                    sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start = text.index(README_MARKERS["artifacts"][0])
    end = text.index(README_MARKERS["artifacts"][1], start) + \
        len(README_MARKERS["artifacts"][1])
    return text[:start] + block + text[end:]


# ---------------------------------------------------------------------------
# Strict rejection self-checks
# ---------------------------------------------------------------------------


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a":1,"a":2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '[]',
        '{"a":1} trailing',
    ]
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            rejected_json += 1
    bad_pins = [
        "not-a-pin",
        "0" * 64 + " source:one",
        "0" * 63 + "  source:one",
        "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]),
        "0" * 64 + "  other:one",
    ]
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = [
        "# no tables",
        "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
        "<!-- digest-table: end -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
        "| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    ]
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except ValueError:
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
