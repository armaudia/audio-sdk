# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the 2S-Dereverb feasibility lane.

The research note records only the candidate locator
(``https://github.com/sp-uhh/2sderev``), the architecture family
(DNN-supported multichannel WPE plus a single-channel nonlinear postfilter)
and the fact that checkpoints are separately downloaded.  It does not record an
immutable commit, a licence, a checkpoint filename, a byte count or a SHA-256.
No local checkout, checkpoint, runtime or environment exists.

This module therefore emits an explicit ``DEFER`` / ``incomplete`` /
``not_qualified`` blocker package.  It runs a deterministic, stdlib-only
two-stage *boundary surrogate* so that the multichannel geometry, the declared
probe delay, sample conservation, state reset and adverse/missing/invalid/
nonfinite rejection can be checked mechanically.  The surrogate is not
2S-Dereverb, contains no DNN, no weights, no runtime and no real audio, and no
surrogate observation may qualify the candidate.

Nothing here downloads, copies, imports, loads or executes 2S-Dereverb, a
checkpoint, a runtime, a corpus or a device clock.  It does not register a
provider, change installed v0, a descriptor, a registry, a default, a shared
build, a dependency lock or CI, and it makes no benchmark, listening, timing or
release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-2S-DEREVERB"
TITLE = "2S-Dereverb"
SLUG = "2s-dereverb"
COMPONENT = "2s-dereverb"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "0eec1f8f9fa420cbae18501583897f4b5faaaf2d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-2S-DEREVERB"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "source_revision_and_checkpoint_admission"

UPSTREAM_REPOSITORY = "https://github.com/sp-uhh/2sderev"
UPSTREAM_PUBLICATION = (
    "https://www.inf.uni-hamburg.de/en/inst/ab/sp/publications/"
    "tasl2022-dereverberation.html")
# The local research record does not establish any of the values below.  They
# are deliberately null: fabricating a commit, licence or checkpoint digest
# would make this package unsafe to review.
UPSTREAM_COMMIT: str | None = None
UPSTREAM_LICENSE: str | None = None
UPSTREAM_LICENSE_STATUS = "not_established"
UPSTREAM_CHECKPOINT_IDENTITY: str | None = None
UPSTREAM_CHECKPOINT_STATUS = "not_recorded"
UPSTREAM_GEOMETRY_STATUS = "unverified"

SOURCE_CHECKOUT_PATH = "data/checkouts/2sderev"
SOURCE_ADAPTER_PATH = "adapters/2sderev"
MODEL_DIR = "data/models/2sderev"
STAGE1_CHECKPOINT_PATH = MODEL_DIR + "/stage1-multichannel-wpe"
STAGE2_CHECKPOINT_PATH = MODEL_DIR + "/stage2-nonlinear-postfilter"
RUNTIME_ENV_PATH = "data/envs/" + SLUG
DEREVERB_RESEARCH_PATH = "research/dereverberation_candidates_20261028.md"
SURVEY_SOURCES_PATH = "research/category_survey/sources.md"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "id": TASK,
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "70266a37baa44d729445c38b787c1cf8b98847445ab0e9d2ecdf7f558ecf77fe")


def board_row_digest() -> str:
    """Digest only the stable linked-row identity, never the mutable file."""
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Probe geometry (declared probe-only; upstream geometry is not established)
# ---------------------------------------------------------------------------

SAMPLE_RATE_HZ = 16000
CHANNELS = 3
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

# Early response within the declared 50 ms probe window: (delay, gain/1024).
# Each synthetic microphone has a different direct path and early reflection.
EARLY_TAPS_BY_CHANNEL: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    ((16, 850), (64, 330), (160, 210), (384, 120), (640, 70), (752, 40)),
    ((24, 790), (72, 305), (176, 195), (400, 112), (656, 66), (768, 38)),
    ((8, 830), (56, 345), (148, 220), (368, 128), (624, 72), (736, 44)),
)
# Late response after 50 ms: (delay, gain/1024), 160-sample spacing.
LATE_TAPS_BY_CHANNEL: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    ((800, 230), (960, 184), (1120, 147), (1280, 117), (1440, 94),
     (1600, 75), (1760, 60), (1920, 48), (2080, 38), (2240, 30)),
    ((824, 214), (984, 172), (1144, 138), (1304, 110), (1464, 88),
     (1624, 70), (1784, 56), (1944, 45), (2104, 36), (2264, 29)),
    ((800, 222), (960, 178), (1120, 142), (1280, 113), (1440, 90),
     (1600, 72), (1760, 58), (1920, 46), (2080, 37), (2240, 30)),
)
# Fixed causal multichannel late predictor: 60% of the first six late taps.
PREDICTOR_TAPS_BY_CHANNEL: Tuple[Tuple[Tuple[int, int], ...], ...] = tuple(
    tuple((delay, max(1, (gain * 60) // 100)) for delay, gain in taps[:6])
    for taps in LATE_TAPS_BY_CHANNEL
)

CONFIG: Dict[str, Any] = {
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "model_used": False,
    "multichannel": True,
    "real_runtime": False,
    "reference_channel": 0,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "stage1": "multichannel_late_subtraction_probe",
    "stage2": "single_channel_static_nonlinearity_probe",
    "surrogate": True,
}

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "frame_samples",
    "input_format",
    "reference_channel",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_path",
    "stage1_checkpoint_path",
    "stage1_checkpoint_sha256",
    "stage1_id",
    "stage2_channels",
    "stage2_checkpoint_path",
    "stage2_checkpoint_sha256",
    "stage2_id",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "multichannel_required": True,
    "present_behavior": (
        "validate_hash_geometry_and_stage_identity_only; do_not_load_or_"
        "execute_in_this_package"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "separate_source_and_checkpoint_archive_required": True,
    "stage1": "stage1_multichannel_wpe",
    "stage2": "stage2_nonlinear_postfilter",
    "stage2_channels": 1,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source_path, both checkpoint paths and runtime_path are caller-owned "
        "absolute paths that exist",
        "SHA-256 of both checkpoints and the runtime artifact match the "
        "manifest",
        "source_commit is a 40-hex revision but cannot be admitted because the "
        "upstream revision was never established",
        "channels is at least two; a mono manifest is rejected because this "
        "candidate is conditional on multichannel input",
        "reference_channel is in range and stage2_channels is exactly one",
        "input_format is float32 and all integer geometry fields are positive",
        "stage1_id and stage2_id equal the declared multichannel-WPE and "
        "single-channel-postfilter stage identities",
        "a hash-matched caller placeholder is never accepted as a pinned "
        "2S-Dereverb checkpoint",
        "no download, copy, build, import, load or execution occurs here",
    ],
    "weights_embedded_in_wheel": False,
}

FORMAT: Dict[str, Any] = {
    "early_window_ms": EARLY_WINDOW_MS,
    "early_window_samples": EARLY_WINDOW_SAMPLES,
    "multichannel_required": True,
    "probe_channels": CHANNELS,
    "probe_frame_duration_ms": FRAME_DURATION_MS,
    "probe_frame_samples": FRAME_SAMPLES,
    "probe_geometry_scope": "probe_only",
    "probe_latency_ms": LATENCY_MS,
    "probe_latency_samples": LATENCY_SAMPLES,
    "probe_sample_format": "float32",
    "probe_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "single_channel_postfilter": True,
    "upstream_channel_count": None,
    "upstream_geometry_verified": False,
    "upstream_hop_samples": None,
    "upstream_latency_samples": None,
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
    text = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, indent=2)
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
# Deterministic synthetic multichannel room fixture
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
            for index in range(3):
                phases[index] = (phases[index] + segment["steps"][index]) & 63
                sample += segment["amplitudes"][index] * SINE64[phases[index]]
            sample >>= 10
            if "click_period" in segment and offset % segment["click_period"] < 4:
                sign = 1 if (offset // segment["click_period"]) % 2 == 0 else -1
                sample += sign * segment["click_amplitude"]
            sample = (sample * _envelope(offset, end - start)) >> 10
            track[start + offset] = _clip16(sample)
    return track


def _noise_track(channel: int) -> List[int]:
    noise = [0] * TOTAL_SAMPLES
    seed = 123456789 + channel * 7919
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


def build_fixture() -> Dict[str, Any]:
    clean = _clean_track()
    early = [_convolve(clean, taps) for taps in EARLY_TAPS_BY_CHANNEL]
    late = [_convolve(clean, taps) for taps in LATE_TAPS_BY_CHANNEL]
    noise = [_noise_track(channel) for channel in range(CHANNELS)]
    reverb = [
        [
            _clip16(early[channel][index] + late[channel][index] +
                    noise[channel][index])
            for index in range(TOTAL_SAMPLES)
        ]
        for channel in range(CHANNELS)
    ]
    return {"clean": clean, "early": early, "late": late, "noise": noise,
            "reverb": reverb}


def as_float(values: Sequence[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def as_float_channels(channels: Sequence[Sequence[int]]) -> List[List[float]]:
    return [as_float(channel) for channel in channels]


def fixture_spec() -> Dict[str, Any]:
    return {
        "channel_early_taps": [
            [list(tap) for tap in taps] for taps in EARLY_TAPS_BY_CHANNEL],
        "channel_late_taps": [
            [list(tap) for tap in taps] for taps in LATE_TAPS_BY_CHANNEL],
        "early_window_samples": EARLY_WINDOW_SAMPLES,
        "fixture_id": "2s-dereverb-multichannel-room-fixture-v1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [dict(segment) for segment in SEGMENTS],
        "channels": CHANNELS,
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))


def component_digests(components: Dict[str, Any]) -> Dict[str, str]:
    return {
        key: sha256(canonical_bytes(components[key]))
        for key in ("clean", "early", "late", "noise", "reverb")
    }


FIXTURE_COMPONENTS = build_fixture()
FIXTURE_DIGESTS = component_digests(FIXTURE_COMPONENTS)

# ---------------------------------------------------------------------------
# Strict config and multichannel frame validation
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
                    ) -> List[List[float]]:
    if not isinstance(frame, (list, tuple)):
        raise ValueError(label + "_not_sequence")
    if len(frame) != CHANNELS:
        raise ValueError(label + "_channels_mismatch")
    values: List[List[float]] = []
    lengths = set()
    for channel in frame:
        if not isinstance(channel, (list, tuple)):
            raise ValueError(label + "_channel_not_sequence")
        if allow_partial:
            if not 1 <= len(channel) <= FRAME_SAMPLES:
                raise ValueError(label + "_length")
        elif len(channel) != FRAME_SAMPLES:
            raise ValueError(label + "_length")
        lengths.add(len(channel))
        samples: List[float] = []
        for sample in channel:
            if isinstance(sample, bool) or not isinstance(sample, (int, float)):
                raise ValueError(label + "_type")
            value = float(sample)
            if not math.isfinite(value):
                raise ValueError(label + "_nonfinite")
            if abs(value) > 1.0:
                raise ValueError(label + "_range")
            samples.append(value)
        values.append(samples)
    if len(lengths) != 1:
        raise ValueError(label + "_ragged_channels")
    return values


# ---------------------------------------------------------------------------
# Deterministic two-stage boundary surrogate (not 2S-Dereverb)
# ---------------------------------------------------------------------------


def _late_estimate(history: Sequence[Sequence[float]]) -> float:
    total = 0.0
    for channel in range(CHANNELS):
        values = history[channel]
        base = len(values)
        for delay, gain in PREDICTOR_TAPS_BY_CHANNEL[channel]:
            index = base - delay
            if index >= 0:
                total += (gain / 1024.0) * values[index]
    return total


def _nonlinear(value: float) -> float:
    return value / (1.0 + 0.5 * abs(value))


class Session:
    """Stateful multichannel one-frame-delayed boundary-surrogate session."""

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
        self.history: List[List[float]] = [
            [0.0] * HISTORY_SAMPLES for _ in range(CHANNELS)]
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
            "history": [[repr(value) for value in channel[-32:]]
                        for channel in self.history],
            "pending": [repr(value) for value in self.pending[:32]],
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
        valid = len(values[0])
        padded = [
            channel + [0.0] * (FRAME_SAMPLES - valid) for channel in values]
        processed: List[float] = []
        for index in range(FRAME_SAMPLES):
            reference = padded[0][index]
            estimate = _late_estimate(self.history)
            processed.append(_nonlinear(reference - estimate))
            for channel in range(CHANNELS):
                self.history[channel].append(padded[channel][index])
        if len(self.history[0]) > 2 * HISTORY_SAMPLES:
            for channel in range(CHANNELS):
                del self.history[channel][:-HISTORY_SAMPLES]
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


def _validate_stream(channels: Any) -> List[List[float]]:
    if not isinstance(channels, (list, tuple)):
        raise ValueError("stream_not_sequence")
    if len(channels) != CHANNELS:
        raise ValueError("stream_channels_mismatch")
    result: List[List[float]] = []
    lengths = set()
    for channel in channels:
        if not isinstance(channel, (list, tuple)):
            raise ValueError("stream_channel_not_sequence")
        lengths.add(len(channel))
        values: List[float] = []
        for sample in channel:
            if isinstance(sample, bool) or not isinstance(sample, (int, float)):
                raise ValueError("stream_type")
            value = float(sample)
            if not math.isfinite(value):
                raise ValueError("stream_nonfinite")
            if abs(value) > 1.0:
                raise ValueError("stream_range")
            values.append(value)
        result.append(values)
    if len(lengths) != 1:
        raise ValueError("stream_ragged_channels")
    return result


def drive_streaming(channels: Sequence[Sequence[float]],
                    chunk: int | None = None,
                    session: Session | None = None) -> Dict[str, Any]:
    values = _validate_stream(channels)
    length = len(values[0])
    if session is None:
        session = Session(CONFIG, "probe", 0)
    if length == 0:
        return {"output": [], "tail_valid": 0, "session": session,
                "total_frames": 0}
    if chunk is None or chunk <= 0:
        chunk = FRAME_SAMPLES
    total_frames = (length + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    output: List[float] = []
    buffers: List[List[float]] = [[] for _ in range(CHANNELS)]
    fed = 0
    position = 0
    while position < length:
        take = min(chunk, length - position)
        for channel in range(CHANNELS):
            buffers[channel].extend(values[channel][position:position + take])
        position += take
        while len(buffers[0]) >= FRAME_SAMPLES:
            fed += 1
            is_last = fed == total_frames
            frame = [buffers[channel][:FRAME_SAMPLES]
                     for channel in range(CHANNELS)]
            output.extend(session.process_frame(frame, final=is_last))
            for channel in range(CHANNELS):
                buffers[channel] = buffers[channel][FRAME_SAMPLES:]
            if is_last:
                for channel in range(CHANNELS):
                    buffers[channel] = []
    if buffers[0]:
        fed += 1
        output.extend(session.process_frame(buffers, final=True))
    tail, tail_valid = session.drain()
    output.extend(tail)
    return {
        "output": output[:length],
        "tail_valid": tail_valid,
        "session": session,
        "total_frames": total_frames,
    }


def run_offline(channels: Sequence[Sequence[float]]) -> Dict[str, Any]:
    return drive_streaming(channels, chunk=len(channels[0]))


# ---------------------------------------------------------------------------
# Caller-supplied asset contract
# ---------------------------------------------------------------------------


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "asset_not_object")
    _require(set(manifest) == REQUIRED_ASSET_FIELDS, "asset_field_set_mismatch")
    for field in ("source_path", "stage1_checkpoint_path",
                  "stage2_checkpoint_path", "runtime_path"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "",
                 "asset_path_not_string:" + field)
        path = Path(value)
        _require(path.is_absolute(), "asset_path_not_absolute:" + field)
        _require(path.is_file(), "asset_file_missing:" + field)
    for field in ("stage1_checkpoint_sha256", "stage2_checkpoint_sha256",
                  "runtime_sha256"):
        value = manifest[field]
        _require(isinstance(value, str) and
                 re.fullmatch(r"[0-9a-f]{64}", value) is not None,
                 "asset_hash_not_hex:" + field)
    _require(sha256_file(Path(manifest["stage1_checkpoint_path"])) ==
             manifest["stage1_checkpoint_sha256"],
             "asset_stage1_hash_mismatch")
    _require(sha256_file(Path(manifest["stage2_checkpoint_path"])) ==
             manifest["stage2_checkpoint_sha256"],
             "asset_stage2_hash_mismatch")
    _require(sha256_file(Path(manifest["runtime_path"])) ==
             manifest["runtime_sha256"], "asset_runtime_hash_mismatch")
    commit = manifest["source_commit"]
    _require(isinstance(commit, str) and
             re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
             "asset_source_commit_not_hex")
    for field in ("algorithmic_latency_samples", "channels", "frame_samples",
                  "reference_channel", "sample_rate_hz", "stage2_channels"):
        _require(_is_int(manifest[field]), "asset_type:" + field)
    _require(manifest["sample_rate_hz"] > 0, "asset_sample_rate_not_positive")
    _require(manifest["frame_samples"] > 0, "asset_frame_not_positive")
    _require(manifest["algorithmic_latency_samples"] >= 0,
             "asset_latency_negative")
    _require(manifest["channels"] >= 2, "asset_channels_not_multichannel")
    _require(0 <= manifest["reference_channel"] < manifest["channels"],
             "asset_reference_channel_out_of_range")
    _require(manifest["input_format"] == "float32", "asset_format_mismatch")
    _require(manifest["stage1_id"] == "stage1_multichannel_wpe",
             "asset_stage1_id_mismatch")
    _require(manifest["stage2_id"] == "stage2_nonlinear_postfilter",
             "asset_stage2_id_mismatch")
    _require(manifest["stage2_channels"] == 1,
             "asset_stage2_not_single_channel")
    return {
        "accepted": True,
        "executed": False,
        "imported": False,
        "loaded": False,
        "multichannel": manifest["channels"] >= 2,
        "pinned_asset": False,
        "stage2_single_channel": manifest["stage2_channels"] == 1,
        "validated": True,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    result = validate_caller_asset(manifest)
    _require(UPSTREAM_COMMIT is not None, "upstream_commit_not_established")
    _require(UPSTREAM_CHECKPOINT_IDENTITY is not None,
             "upstream_checkpoint_identity_not_established")
    _require(manifest["source_commit"] == UPSTREAM_COMMIT,
             "asset_source_commit_not_pinned")
    result["pinned_asset"] = True
    result["loaded"] = False
    result["executed"] = False
    return result


def _rejected(manifest: Any) -> str:
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        return str(error)
    return "accepted"


def _pinned_rejected(manifest: Any) -> str:
    try:
        pinned_asset_identity(manifest)
    except ValueError as error:
        return str(error)
    return "accepted"


def _asset_controls() -> Dict[str, Any]:
    geometry = {
        "algorithmic_latency_samples": LATENCY_SAMPLES,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "input_format": "float32",
        "reference_channel": 0,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_commit": "a" * 40,
        "stage1_id": "stage1_multichannel_wpe",
        "stage2_channels": 1,
        "stage2_id": "stage2_nonlinear_postfilter",
    }
    with tempfile.TemporaryDirectory(prefix="2s-dereverb-asset-") as name:
        root = Path(name)
        source = root / "source.txt"
        stage1 = root / "stage1.ckpt"
        stage2 = root / "stage2.ckpt"
        runtime = root / "runtime.bin"
        source.write_bytes(b"caller-owned-placeholder-source")
        stage1.write_bytes(b"caller-owned-placeholder-stage1")
        stage2.write_bytes(b"caller-owned-placeholder-stage2")
        runtime.write_bytes(b"caller-owned-placeholder-runtime")
        valid = dict(
            geometry,
            source_path=str(source),
            stage1_checkpoint_path=str(stage1),
            stage1_checkpoint_sha256=sha256_file(stage1),
            stage2_checkpoint_path=str(stage2),
            stage2_checkpoint_sha256=sha256_file(stage2),
            runtime_path=str(runtime),
            runtime_sha256=sha256_file(runtime),
        )
        generic = validate_caller_asset(valid)
        cases: Dict[str, str] = {}
        missing = dict(valid)
        missing.pop("stage2_id")
        cases["missing_field"] = _rejected(missing)
        cases["relative_path"] = _rejected(
            dict(valid, source_path="source.txt"))
        cases["absent_source"] = _rejected(
            dict(valid, source_path=str(root / "absent.txt")))
        cases["stage1_hash"] = _rejected(
            dict(valid, stage1_checkpoint_sha256="0" * 64))
        cases["stage2_hash"] = _rejected(
            dict(valid, stage2_checkpoint_sha256="0" * 64))
        cases["runtime_hash"] = _rejected(
            dict(valid, runtime_sha256="0" * 64))
        cases["short_commit"] = _rejected(
            dict(valid, source_commit="0" * 39))
        cases["zero_rate"] = _rejected(dict(valid, sample_rate_hz=0))
        cases["zero_frame"] = _rejected(dict(valid, frame_samples=0))
        cases["negative_latency"] = _rejected(
            dict(valid, algorithmic_latency_samples=-1))
        cases["mono"] = _rejected(dict(valid, channels=1))
        cases["reference_out_of_range"] = _rejected(
            dict(valid, reference_channel=CHANNELS))
        cases["format"] = _rejected(dict(valid, input_format="int16"))
        cases["stage1_id"] = _rejected(
            dict(valid, stage1_id="stage1_mono_wpe"))
        cases["stage2_id"] = _rejected(
            dict(valid, stage2_id="stage2_linear_postfilter"))
        cases["stage2_channels"] = _rejected(
            dict(valid, stage2_channels=2))
        cases["bool_channels"] = _rejected(dict(valid, channels=True))
        cases["bool_rate"] = _rejected(dict(valid, sample_rate_hz=True))
        cases["extra_field"] = _rejected(dict(valid, extra=True))
        cases["pinned_placeholder"] = _pinned_rejected(valid)
        workspace = dict(
            valid, source_path=str(resolve_source_path(SOURCE_CHECKOUT_PATH)))
        cases["workspace_source_absent"] = _rejected(workspace)
    return {
        "generic_admission": generic,
        "pinned_identity_rejected": cases["pinned_placeholder"],
        "rejections": cases,
        "rejected_all": all(value != "accepted" for value in cases.values()),
        "workspace_source_present":
            resolve_source_path(SOURCE_CHECKOUT_PATH).exists(),
        "workspace_stage1_present":
            resolve_source_path(STAGE1_CHECKPOINT_PATH).exists(),
        "workspace_stage2_present":
            resolve_source_path(STAGE2_CHECKPOINT_PATH).exists(),
        "workspace_runtime_present":
            resolve_source_path(RUNTIME_ENV_PATH).exists(),
    }


def config_adverse_control() -> Dict[str, Any]:
    baseline = Session(CONFIG, "probe", 0)
    cases: Dict[str, str] = {}

    def rejected(name: str, config: Dict[str, Any], session_id: str = "x",
                 epoch: int = 0, bool_epoch: bool = False) -> None:
        try:
            Session(config, session_id, True if bool_epoch else epoch)
        except ValueError as error:
            cases[name] = str(error)
        else:
            cases[name] = "accepted"

    rejected("sample_rate", dict(CONFIG, sample_rate_hz=48000))
    rejected("mono_channels", dict(CONFIG, channels=1))
    rejected("two_channels", dict(CONFIG, channels=2))
    rejected("format", dict(CONFIG, input_format="int16"))
    rejected("frame", dict(CONFIG, frame_samples=320))
    rejected("latency", dict(CONFIG, algorithmic_latency_samples=0))
    rejected("negative_latency", dict(CONFIG,
                                      algorithmic_latency_samples=-1))
    rejected("multichannel_false", dict(CONFIG, multichannel=False))
    rejected("reference_channel", dict(CONFIG, reference_channel=3))
    rejected("stage1", dict(CONFIG, stage1="mono_wpe"))
    rejected("stage2", dict(CONFIG, stage2="linear_postfilter"))
    rejected("real_runtime", dict(CONFIG, real_runtime=True))
    rejected("model_used", dict(CONFIG, model_used=True))
    rejected("surrogate_false", dict(CONFIG, surrogate=False))
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

    good = [[0.0] * FRAME_SAMPLES for _ in range(CHANNELS)]

    def mutate(channel: int, index: int, value: Any) -> List[List[float]]:
        frame = [list(item) for item in good]
        frame[channel][index] = value
        return frame

    rejected("mono", [[0.0] * FRAME_SAMPLES])
    rejected("two_channels", [[0.0] * FRAME_SAMPLES] * 2)
    rejected("four_channels", [[0.0] * FRAME_SAMPLES] * 4)
    rejected("ragged", [[0.0] * FRAME_SAMPLES,
                        [0.0] * FRAME_SAMPLES,
                        [0.0] * (FRAME_SAMPLES - 1)])
    rejected("empty_final", [[], [], []], final=True)
    rejected("short_nonfinal", [[0.0] * (FRAME_SAMPLES - 1)] * CHANNELS)
    rejected("long_nonfinal", [[0.0] * (FRAME_SAMPLES + 1)] * CHANNELS)
    rejected("string_outer", "x" * FRAME_SAMPLES)
    rejected("string_channel", [good[0], "x" * FRAME_SAMPLES, good[2]])
    rejected("nan_ch0", mutate(0, 3, math.nan))
    rejected("infinity_ch1", mutate(1, 5, math.inf))
    rejected("negative_infinity_ch2", mutate(2, 7, -math.inf))
    rejected("range_ch0", mutate(0, 0, 1.5))
    rejected("negative_range_ch2", mutate(2, 0, -1.5))
    rejected("boolean_ch1", mutate(1, 2, True))
    rejected("nested_ch0", mutate(0, 4, [0.0]))
    rejected("none_ch2", mutate(2, 6, None))
    rejected("partial_nonfinal", [[0.0] * 128 for _ in range(CHANNELS)])
    accepted = [[0.1] * FRAME_SAMPLES for _ in range(CHANNELS)]
    output = session.process_frame(accepted, final=False)
    return {
        "accepted_after_rejections": True,
        "accepted_output_length": len(output),
        "counter_after_accept": session.counters["accepted_input_samples"],
        "baseline_digest": baseline,
        "rejections": cases,
        "rejected_all": all(value != "accepted" for value in cases.values()),
    }


def streaming_parity_control(components: Dict[str, Any]) -> Dict[str, Any]:
    samples = as_float_channels(components["reverb"])
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


def partial_tail_control(components: Dict[str, Any]) -> Dict[str, Any]:
    full = run_offline(as_float_channels(components["reverb"]))
    length = 1000
    partial = run_offline(
        [channel[:length] for channel in
         as_float_channels(components["reverb"])])
    return {
        "expected_tail_valid": length % FRAME_SAMPLES,
        "length_preserved": len(partial["output"]) == length,
        "prefix_matches_full": partial["output"] == full["output"][:length],
        "tail_valid": partial["tail_valid"],
    }


def reset_control(components: Dict[str, Any]) -> Dict[str, Any]:
    samples = as_float_channels(components["reverb"])
    window = [channel[:FRAME_SAMPLES * 3] for channel in samples]
    first = Session(CONFIG, "reset-probe", 1)
    for index in range(3):
        first.process_frame(
            [channel[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
             for channel in window], final=index == 2)
    first.drain()
    reset_digest = first.state_digest()
    fresh = Session(CONFIG, "reset-probe", 1)
    for index in range(3):
        fresh.process_frame(
            [channel[index * FRAME_SAMPLES:(index + 1) * FRAME_SAMPLES]
             for channel in window], final=index == 2)
    fresh.drain()
    stale_session = Session(CONFIG, "reset-probe", 0)
    stale_session.process_frame([channel[:FRAME_SAMPLES] for channel in window])
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


def silence_control() -> Dict[str, Any]:
    length = FRAME_SAMPLES * 2
    result = run_offline([[0.0] * length for _ in range(CHANNELS)])
    return {
        "exact_zero": all(value == 0.0 for value in result["output"]),
        "finite": all(math.isfinite(value) for value in result["output"]),
        "length": len(result["output"]),
        "tail_valid": result["tail_valid"],
    }


def impulse_control() -> Dict[str, Any]:
    length = FRAME_SAMPLES * 16
    source_index = 2000
    channels = [[0.0] * length for _ in range(CHANNELS)]
    channels[0][source_index] = 0.5
    result = run_offline(channels)
    output = result["output"]
    peak_index = max(range(len(output)), key=lambda index: abs(output[index]))
    stage2_peak = output[peak_index]
    return {
        "expected_output_index": source_index + LATENCY_SAMPLES,
        "finite": all(math.isfinite(value) for value in output),
        "length": len(output),
        "nonlinear_peak_reduced": abs(stage2_peak) < 0.5,
        "observed_peak_index": peak_index,
        "peak_value": _metric(stage2_peak),
        "source_index": source_index,
    }


def multichannel_control() -> Dict[str, Any]:
    length = FRAME_SAMPLES * 8
    base = [[0.0] * length for _ in range(CHANNELS)]
    for index in range(length):
        base[0][index] = ((index % 97) - 48) / 4096.0
    first = run_offline(base)
    changed = [list(channel) for channel in base]
    changed[1][512] = 0.25
    second = run_offline(changed)
    mono_rejected = False
    try:
        run_offline([[0.0] * length])
    except ValueError as error:
        mono_rejected = str(error) == "stream_channels_mismatch"
    return {
        "finite": all(math.isfinite(value) for value in second["output"]),
        "mono_rejected": mono_rejected,
        "other_channels_change_output": first["output"] != second["output"],
        "per_channel_geometry": CHANNELS,
    }


def delay_control(impulse: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "declared_latency_ms": LATENCY_MS,
        "declared_latency_samples": LATENCY_SAMPLES,
        "expected_output_index": impulse["expected_output_index"],
        "matches": impulse["observed_peak_index"] ==
                   impulse["expected_output_index"],
        "observed_output_index": impulse["observed_peak_index"],
    }


def nonfinite_counter_control() -> Dict[str, Any]:
    session = Session(CONFIG, "nonfinite-probe", 0)
    frame = [[0.0] * FRAME_SAMPLES for _ in range(CHANNELS)]
    frame[1][17] = math.nan
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
        "id": "source_absent_unpinned",
        "requirement": (
            "Supply the exact 2S-Dereverb source tree at an immutable 40-hex "
            "commit as a caller-owned checkout, with a reviewed licence and "
            "notice bundle, verified locally without a network download."),
        "state": (
            "No checkout exists at data/checkouts/2sderev or adapters/2sderev. "
            "The research record names only https://github.com/sp-uhh/2sderev "
            "and does not record a commit, branch, tag, archive digest or "
            "licence; none is fabricated or downloaded here."),
    },
    {
        "id": "checkpoint_identity_absent",
        "requirement": (
            "Supply the exact multichannel-WPE first-stage checkpoint and the "
            "exact single-channel nonlinear-postfilter second-stage checkpoint "
            "with filename, byte count, SHA-256, acquisition record and "
            "artifact-specific terms."),
        "state": (
            "The research record states only that checkpoints are separately "
            "downloaded. No checkpoint filename, byte count, SHA-256 or local "
            "file exists at data/models/2sderev; nothing was downloaded, "
            "reconstructed or substituted."),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Admit a locked, hash-pinned offline runtime with the exact "
            "framework, dependency and native-library versions required by "
            "the pinned source, plus an install/import digest."),
        "state": (
            "No environment exists at data/envs/2s-dereverb. The upstream "
            "runtime requirements were not established, and no model import "
            "or inference was attempted."),
    },
    {
        "id": "rights_unresolved",
        "requirement": (
            "Supply written source, checkpoint, training-data, corpus, "
            "redistribution, product-use and derivative-output terms plus the "
            "complete notice bundle for the exact source, checkpoints and "
            "runtime."),
        "state": (
            "No licence or terms record is established for the 2S-Dereverb "
            "code, checkpoints, training data or evaluation corpora. Nothing "
            "may be bundled, rehosted, rebranded or deployed."),
    },
    {
        "id": "geometry_and_latency_unverified",
        "requirement": (
            "Pin the exact channel count, reference-channel definition, sample "
            "rate, hop, STFT/WOLA geometry, predictor delay, postfilter state "
            "and total algorithmic latency, then reproduce them on one "
            "declared streaming path."),
        "state": (
            "The research note describes multichannel input and unverified "
            "latency. It records no channel count, sample rate, hop, STFT "
            "window, lookahead, predictor delay or end-to-end latency. This "
            "package's 3-channel 16 kHz/256-sample geometry is a probe-only "
            "harness, not the upstream geometry."),
    },
    {
        "id": "evidence_absent",
        "requirement": (
            "Reproduce approved exact-runtime outputs on a rights-cleared "
            "paired reverberant/early-target cohort, score with independent "
            "intrusive metrics or permitted listening, measure target-device "
            "timing and complete opt-in provider intake."),
        "state": (
            "No exact output vector, rights-cleared cohort, independent score, "
            "listening result, target-device timing, adapter or provider "
            "intake exists. Surrogate observations do not qualify the "
            "candidate."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_revision_and_license",
     "Immutable 40-hex source revision, reviewed licence, notice bundle and "
     "clean checkout verified locally without a download."),
    ("checkpoint_identity_and_terms",
     "Both stage checkpoints match exact filenames, byte counts and SHA-256 "
     "values with reviewed artifact-specific terms."),
    ("pinned_runtime_and_offline_load",
     "Locked offline runtime with exact dependency versions, install/import "
     "digest and a deterministic load of both checkpoints."),
    ("multichannel_geometry_and_latency",
     "Exact channel count, reference channel, rate, hop, STFT/WOLA geometry, "
     "predictor delay and total algorithmic latency are pinned and reproduced."),
    ("exact_reference_parity",
     "Approved exact-runtime output vectors for both stages and byte-level "
     "parity on the declared multichannel streaming path."),
    ("rights_cleared_paired_cohort",
     "Frozen rights-cleared reverberant corpus, measured or frozen RIRs, "
     "early-target definition, strata and reset/delay schedule."),
    ("independent_scoring_and_listening",
     "Independent SI-SDR/STOI/SRMR and identity/task-matched baselines or "
     "permitted listening, including missing, adverse and nonfinite controls."),
    ("target_runtime_timing_and_opt_in_provider",
     "Target-device p50/p95/p99, RTF, memory and deadline behavior, plus "
     "OFF-by-default opt-in provider intake and descriptor review."),
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
    "multichannel_abi_change": False,
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

SCOPE: Dict[str, Any] = {
    "benchmark_run": False,
    "device_timing_measured": False,
    "downloaded": False,
    "implementation_added": False,
    "listening_performed": False,
    "network_used": False,
    "provider_registered": False,
    "public_abi_changed": False,
    "real_assets_used": False,
    "registry_or_default_changed": False,
    "release_claim": False,
    "runtime_executed": False,
    "shared_build_or_ci_changed": False,
    "source_imported": False,
    "task_local_only": True,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX + " only",
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No 2S-Dereverb source, checkpoint, derived weight or runtime call was "
    "produced.",
    "No dereverberation, quality, latency, timing, benchmark or release "
    "result is claimed.",
    "The two-stage boundary surrogate is not 2S-Dereverb and cannot qualify "
    "the candidate.",
    "The 3-channel 16 kHz/256-sample probe geometry is not the unverified "
    "upstream geometry.",
    "No real corpus, room impulse response, audio, device clock or listener "
    "was used.",
    "No provider, descriptor, registry, installed v0 path, default, public "
    "ABI, shared build, dependency lock or CI was changed.",
    "A caller-owned hash-matched placeholder is never admitted as a pinned "
    "checkpoint.",
)

SOURCE_PINS: Dict[str, str] = {
    DEREVERB_RESEARCH_PATH:
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    SURVEY_SOURCES_PATH:
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

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
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}

REQUIRED_REPORT_KEYS = {
    "acceptance_profile", "asset_pins", "base_commit", "board_row",
    "boundary", "branch", "caller_asset_contract", "claim", "component_id",
    "contract_sha256", "controls", "decision", "defer_before",
    "evidence_status", "exact_blockers", "fixture", "format", "gates",
    "metrics", "missing_results", "no_missing_result_qualifies_candidate",
    "negative_claims", "profile", "proposal_only", "qualification",
    "qualification_status", "reopen_condition", "scenario", "schema_id",
    "scope", "status", "surrogate", "task_id", "title", "upstream",
}
REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary",
    "boundary_pins", "branch", "caller_asset_contract", "component_id",
    "decision", "defer_before", "evidence_status", "exact_blockers", "format",
    "gates", "invariants", "local_files", "negative_claims", "profile",
    "proposal_only", "qualification", "qualification_status",
    "reopen_condition", "reviewer", "scenario", "schema_id", "scope",
    "source_pins", "status", "task_id", "title", "upstream",
}

# ---------------------------------------------------------------------------
# Report, contract and manifest builders
# ---------------------------------------------------------------------------


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no exact upstream source, checkpoint or runtime, so no exact "
            "output is reproduced",
            "no echo-only, near-end-only, overlap or no-reference measured case",
            "no early-target SI-SDR, STOI, SRMR or identity comparison against "
            "a real candidate output",
            "no measured room, RIR, delayed/missing render or movement schedule",
            "no independent listening, ASR or target-device timing",
        ],
        "mapped_cases": [
            "frozen synthetic 3-channel room response with early/late/noise "
            "decomposition",
            "declared probe channel count, rate, hop, excitation and one-hop "
            "delay",
            "multichannel input validation and mono rejection",
            "silence, speech, transient and decaying-tail strata",
            "impulse delay mapping and partial-tail preservation",
            "offline/streaming parity across arbitrary chunk sizes",
            "reset schedule and stale-epoch rejection",
            "finite, peak, clipping and silence-exactness bounds",
            "fail-closed caller-asset, config and frame controls",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no real candidate artifact exists to evaluate",
            "the surrogate is not 2S-Dereverb and has no DNN, weights or "
            "runtime",
            "no target device, listener or rights-cleared corpus is available",
        ],
        "source": VERIFICATION_PATH,
    }


def _fixture_block() -> Dict[str, Any]:
    return {
        "channel_early_taps": [
            [list(tap) for tap in taps] for taps in EARLY_TAPS_BY_CHANNEL],
        "channel_late_taps": [
            [list(tap) for tap in taps] for taps in LATE_TAPS_BY_CHANNEL],
        "channels": CHANNELS,
        "component_digests": dict(FIXTURE_DIGESTS),
        "early_window_ms": EARLY_WINDOW_MS,
        "early_window_samples": EARLY_WINDOW_SAMPLES,
        "fixture_id": fixture_spec()["fixture_id"],
        "segments": [dict(segment) for segment in SEGMENTS],
        "spec_digest": FIXTURE_SPEC_DIGEST,
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


def _surrogate_block() -> Dict[str, Any]:
    return {
        "candidate_result": False,
        "delay_samples": LATENCY_SAMPLES,
        "dnn_free": True,
        "is_2s_dereverb": False,
        "model_free": True,
        "note": (
            "The surrogate exists only to exercise the multichannel geometry, "
            "declared delay, state reset and fail-closed controls. It is not "
            "2S-Dereverb and cannot qualify the candidate."),
        "predictor_taps_by_channel": [
            [list(tap) for tap in taps]
            for taps in PREDICTOR_TAPS_BY_CHANNEL],
        "stage1": "multichannel_causal_late_subtraction",
        "stage2": "single_channel_static_nonlinear_compression",
        "type": "fixed two-stage boundary surrogate",
    }


def _metrics_block(components: Dict[str, Any], output: Sequence[float]
                   ) -> Dict[str, Any]:
    scored = TOTAL_SAMPLES - LATENCY_SAMPLES
    return {
        "candidate_result": False,
        "channels": CHANNELS,
        "declared_latency_samples": LATENCY_SAMPLES,
        "max_abs_output": _metric(max(abs(value) for value in output)),
        "multichannel_geometry_exercised": True,
        "nonfinite_output_samples": sum(
            1 for value in output if not math.isfinite(value)),
        "output_peak_clipped_samples": sum(
            1 for value in output if abs(value) > 1.0),
        "scored_samples": scored,
        "silence_exact_zero": all(
            value == 0.0 for value in output[:SEGMENT_FRAMES * FRAME_SAMPLES]),
        "surrogate_only": True,
    }


def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "checkpoints_present": False,
        "exact_result_present": False,
        "geometry_verified": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "release_claim": False,
        "runtime_present": False,
        "source_licensed": False,
        "source_present": False,
        "status": QUALIFICATION,
        "timing_result_present": False,
    }


def _report_body() -> Dict[str, Any]:
    components = FIXTURE_COMPONENTS
    samples = as_float_channels(components["reverb"])
    offline = run_offline(samples)
    output = offline["output"]
    impulse = impulse_control()
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:runtime": {
                "admitted": False,
                "executed": False,
                "expected_path": RUNTIME_ENV_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
            },
            "asset:source_checkout": {
                "executed": False,
                "expected_path": SOURCE_CHECKOUT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(SOURCE_CHECKOUT_PATH).exists(),
            },
            "asset:stage1_checkpoint": {
                "executed": False,
                "expected_path": STAGE1_CHECKPOINT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(STAGE1_CHECKPOINT_PATH).exists(),
            },
            "asset:stage2_checkpoint": {
                "executed": False,
                "expected_path": STAGE2_CHECKPOINT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(STAGE2_CHECKPOINT_PATH).exists(),
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
        "contract_sha256": sha256(canonical_bytes(contract_payload())),
        "controls": {
            "asset": _asset_controls(),
            "config": config_adverse_control(),
            "delay": delay_control(impulse),
            "frame": frame_adverse_control(),
            "impulse": impulse,
            "multichannel": multichannel_control(),
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
        "fixture": _fixture_block(),
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "metrics": _metrics_block(components, output),
        "missing_results": [
            "exact 2S-Dereverb source revision and licence",
            "exact stage-1 multichannel-WPE checkpoint",
            "exact stage-2 single-channel nonlinear-postfilter checkpoint",
            "pinned offline runtime and deterministic load",
            "exact multichannel geometry and total algorithmic latency",
            "exact-runtime output vectors and parity",
            "rights-cleared paired reverberant/early-target cohort",
            "independent intrusive score or permitted listening",
            "target-device timing, memory and deadline",
            "opt-in provider intake and default decision",
        ],
        "no_missing_result_qualifies_candidate": True,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the exact source revision and licence, both stage "
            "checkpoints with byte counts and SHA-256, a locked offline "
            "runtime, the exact multichannel geometry and latency, and clear "
            "artifact and corpus rights. Then reproduce exact-runtime outputs, "
            "score a rights-cleared paired cohort independently or with "
            "permitted listening, measure target timing and complete "
            "OFF-by-default opt-in provider intake. Until then the candidate "
            "stays DEFER, incomplete and not qualified."),
        "scenario": {
            "channels_required": ">=2",
            "far_end_reference": False,
            "id": "2s-dereverb-multichannel-room-blocker-v1",
            "is_aec": False,
            "is_mono_baseline": False,
            "note": (
                "The candidate is a multichannel dereverberation chain with a "
                "single-channel postfilter. No far-end playback reference is "
                "part of this scenario, so it is not AEC and not a mono "
                "baseline."),
            "reference_channel": 0,
            "task_geometry": (
                "multichannel WPE plus single-channel nonlinear postfilter"),
            "upstream_geometry_verified": False,
        },
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "status": STATUS,
        "surrogate": _surrogate_block(),
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_identity": UPSTREAM_CHECKPOINT_IDENTITY,
            "checkpoint_identity_status": UPSTREAM_CHECKPOINT_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": (
                "The local research record names the repository and the "
                "architecture family only. It records no commit, licence, "
                "checkpoint filename, byte count or SHA-256; none is "
                "fabricated here."),
            "publication": UPSTREAM_PUBLICATION,
            "repository": UPSTREAM_REPOSITORY,
            "source_present": False,
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
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no source, checkpoint, weight, runtime or corpus is downloaded, "
            "copied, imported, loaded or executed",
            "no claim is made from observed path presence",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the exact source revision and licence, both stage "
            "checkpoints with pinned byte counts and SHA-256, a locked offline "
            "runtime, the exact multichannel geometry and latency, and clear "
            "artifact and corpus rights. Then reproduce exact-runtime outputs, "
            "score a rights-cleared paired cohort independently or with "
            "permitted listening, measure target timing and complete "
            "OFF-by-default opt-in provider intake."),
        "reviewer": REVIEWER,
        "scenario": {
            "channels_required": ">=2",
            "far_end_reference": False,
            "id": "2s-dereverb-multichannel-room-blocker-v1",
            "is_aec": False,
            "is_mono_baseline": False,
            "reference_channel": 0,
            "task_geometry": (
                "multichannel WPE plus single-channel nonlinear postfilter"),
            "upstream_geometry_verified": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_identity": UPSTREAM_CHECKPOINT_IDENTITY,
            "checkpoint_identity_status": UPSTREAM_CHECKPOINT_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "publication": UPSTREAM_PUBLICATION,
            "repository": UPSTREAM_REPOSITORY,
            "source_present": False,
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
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {
            name for name in _local_manifest_paths()
            if name not in ARTIFACT_TABLE_EXCLUDED
        },
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
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
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
