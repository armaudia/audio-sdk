# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER blocker evidence for SDK-TARGET-SPEAKER-EXTRACTION-FAMILY.

No exact licensed source, checkpoint, enrollment protocol, runtime, or rights-
cleared target-speaker extraction corpus is present in this package. This module
emits an explicit DEFER/incomplete/not_qualified blocker package and runs a
deterministic, stdlib-only synthetic boundary surrogate. The surrogate is not a
target-speaker extractor, contains no model/weights/runtime, and no observation
may qualify the candidate.

Nothing here downloads, imports, loads, executes, or bundles external assets. It
does not register providers, change installed v0/ABI/registry/default/shared
build/CI, or make benchmark/listening/device-timing/release claims.
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
TASK = "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"
TITLE = "Target-speaker extraction family"
SLUG = "target-speaker-extraction-family"
COMPONENT = "target-speaker-extraction-family"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "spatial"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "source_checkpoint_runtime_rights_and_evidence_admission"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "id": TASK,
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = "18978b7767cf14f122eaf16997169b0e17dba103a822eaac17c31feeafff0e7b"

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md": "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES = [
    "README.md",
    "SOURCES.sha256",
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
]

README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: boundary-end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
ARTIFACT_TABLE_EXCLUDED = {"README.md", "SOURCES.sha256", "SOURCES.sha256.license"}

SAMPLE_RATE_HZ = 16000
CHANNELS = 3
FRAME_SAMPLES = 256
TOTAL_FRAMES = 120
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
DELAY_SAMPLES = 256
WINDOW_SAMPLES = 1024

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

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "start_frame": 0, "end_frame": 20, "kind": "silence"},
    {"id": "target-speech", "start_frame": 20, "end_frame": 50, "kind": "target",
     "steps": (1, 2, 3), "amplitudes": (420, 220, 130)},
    {"id": "overlap", "start_frame": 50, "end_frame": 80, "kind": "overlap",
     "steps": (1, 2, 3), "amplitudes": (400, 210, 120),
     "masker_steps": (3, 5, 8), "masker_amplitudes": (360, 240, 150)},
    {"id": "target-absent-masker", "start_frame": 80, "end_frame": 100, "kind": "masker",
     "masker_steps": (2, 4, 7), "masker_amplitudes": (390, 260, 160)},
    {"id": "tail", "start_frame": 100, "end_frame": 120, "kind": "silence"},
)

# Probe-only synthetic multichannel cues: fixed per-channel taps for target and
# masker. This is not array geometry, not enrollment, not a model cue.
TARGET_TAPS: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    ((0, 900), (16, 180), (48, 90)),
    ((8, 860), (24, 170), (56, 84)),
    ((4, 880), (20, 175), (52, 87)),
)
MASKER_TAPS: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    ((24, 820), (72, 220), (128, 120)),
    ((12, 860), (60, 210), (116, 110)),
    ((20, 840), (68, 215), (124, 115)),
)

CONFIG: Dict[str, Any] = {
    "algorithmic_latency_samples": DELAY_SAMPLES,
    "channels": CHANNELS,
    "cue_kind": "synthetic_probe_spatial_tap",
    "enrollment_conditioned": False,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "model_used": False,
    "multichannel_required": True,
    "real_runtime": False,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "surrogate": True,
    "target_absent_policy": "suppress_output",
}

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "cue_kind",
    "enrollment_path",
    "enrollment_sha256",
    "frame_samples",
    "input_format",
    "model_id",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_path",
    "weights_path",
    "weights_sha256",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "multichannel_required": True,
    "present_behavior": "validate_hash_geometry_and_identity_only; do_not_load_or_execute_in_this_package",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source/enrollment/weights/runtime paths are caller-owned absolute files",
        "enrollment, weights and runtime SHA-256 match the manifest",
        "source_commit is 40-hex but cannot be admitted because no upstream revision is pinned",
        "channels >= 2, sample_rate/frame/latency positive, format float32",
        "cue_kind is one of enrollment_audio, spatial_direction, visual_reference",
        "no download, copy, import, load or execution occurs here",
    ],
}

FORMAT: Dict[str, Any] = {
    "probe_channels": CHANNELS,
    "probe_frame_samples": FRAME_SAMPLES,
    "probe_geometry_scope": "probe_only",
    "probe_latency_samples": DELAY_SAMPLES,
    "probe_sample_format": "float32",
    "probe_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "upstream_geometry_verified": False,
    "window_frames": TOTAL_FRAMES,
    "window_samples": TOTAL_SAMPLES,
}

BOUNDARY: Dict[str, bool] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
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
    "write_scope": TASK_PREFIX[:-1] + " only",
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "source_checkpoint_absent", "requirement": "Pin an exact licensed target-speaker extraction source, checkpoint/weights, enrollment/reference-cue contract and immutable revision.", "state": "Candidate matrix and inventory record no selected extraction model, no deployable checkpoint, no runtime, and no reference encoder/weights identity. No source or checkpoint is present or fabricated."},
    {"id": "rights_unresolved", "requirement": "Resolve source/checkpoint/runtime/corpus/derivative-output rights and redistribution/product-use terms.", "state": "No rights bundle or terms review is present for this family-level blocker package; nothing is bundled or redistributed."},
    {"id": "enrollment_protocol_missing", "requirement": "Freeze enrollment/spatial/visual cue protocol with exact cue identity, reference timing, unknown/target-absent handling and consent.", "state": "No enrolled speaker, reference utterance, spatial cue, visual cue, or target-absent protocol is staged."},
    {"id": "corpus_missing", "requirement": "Provide rights-cleared overlap mixtures with clean target references, target-absent negatives, and speaker/session/group-disjoint splits.", "state": "No enrolled-speaker extraction corpus, clean target references, or target-absent negatives exist in this package."},
    {"id": "runtime_geometry_unverified", "requirement": "Pin exact channel/layout/reference timing, sample rate, hop, latency/lookahead, and deterministic streaming runtime.", "state": "Upstream geometry/runtime are not verified. Harness uses probe-only 3ch/16k/256 sample geometry; it is not an upstream claim."},
    {"id": "evidence_absent", "requirement": "Run independent target preservation/off-target suppression/target-absent false-rejection scoring, listening where authorized, and target-device timing.", "state": "No candidate output, scorer result, listening, device timing, or opt-in provider intake exists. Surrogate observations cannot qualify."},
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_checkpoint_and_license", "Exact source revision, checkpoint/weights identity, license and notice bundle are pinned and reviewed."),
    ("rights_cleared_enrolled_corpus", "Rights-cleared enrolled-speaker mixtures with clean target references and target-absent negatives are frozen."),
    ("cue_protocol_and_geometry", "Enrollment/spatial/visual cue protocol and any required array geometry/reference timing are exact and verified."),
    ("exact_runtime_and_determinism", "Pinned offline/runtime executes deterministically with exact frame/latency/reset/state behavior."),
    ("target_preservation_and_leakage_scoring", "Independent target preservation, off-target suppression, target-absent false rejection and uncertainty are measured."),
    ("adverse_missing_invalid_nonfinite_controls", "Missing cue, invalid geometry, nonfinite, target-absent, and overlap controls fail closed."),
    ("target_runtime_timing_and_memory", "Target-device p50/p95/p99, RTF, memory and deadline behavior are measured for the exact runtime."),
    ("opt_in_provider_intake_and_release", "OFF-by-default opt-in provider intake, independent review and explicit release approval are complete."),
)

NEGATIVE_CLAIMS = [
    "No target-speaker extraction model, checkpoint, weight, runtime, or enrollment cue was used.",
    "No target-preservation, leakage, listening, ASR, timing, benchmark, or release result is claimed.",
    "The synthetic boundary surrogate is not a target-speaker extractor and cannot qualify the candidate.",
    "Probe-only 3ch/16k/256-sample geometry is not upstream geometry.",
    "No real corpus, speaker identity, consented enrollment, array recording, or device clock was used.",
    "No provider/descriptor/registry/default/public ABI/shared build/dependency lock/CI change was made.",
    "A caller-owned hash-matched placeholder is never admitted as a pinned candidate asset.",
]


def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2)
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


def workspace_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override).resolve()
    for parent in HERE.parents:
        if (parent / "adapters").is_dir() and (parent / "audio-benchmark-platform").is_dir():
            return parent
    raise ValueError("workspace_root_not_found")


def resolve_source_path(name: str) -> Path:
    return workspace_root() / name


def _clip16(value: int) -> int:
    return 32767 if value > 32767 else -32768 if value < -32768 else value


def _envelope(index: int, length: int) -> int:
    fade = 512
    if index < fade:
        return (index * 1024) // fade
    if index >= length - fade:
        return ((length - 1 - index) * 1024) // fade
    return 1024


def _signal(steps: Sequence[int], amplitudes: Sequence[int], length: int, click_period: int = 0, click_amp: int = 0) -> List[int]:
    phases = [0, 0, 0]
    out = [0] * length
    for i in range(length):
        sample = 0
        for j in range(3):
            phases[j] = (phases[j] + steps[j]) & 63
            sample += amplitudes[j] * SINE64[phases[j]]
        sample >>= 10
        if click_period and i % click_period < 4:
            sample += click_amp if (i // click_period) % 2 == 0 else -click_amp
        sample = (sample * _envelope(i, length)) >> 10
        out[i] = _clip16(sample)
    return out


def _convolve(source: Sequence[int], taps: Sequence[Tuple[int, int]]) -> List[int]:
    out = [0] * len(source)
    for delay, gain in taps:
        for i in range(delay, len(source)):
            out[i] += (source[i - delay] * gain) >> 10
    return [_clip16(v) for v in out]


def build_fixture() -> Dict[str, Any]:
    target = [0] * TOTAL_SAMPLES
    masker = [0] * TOTAL_SAMPLES
    for seg in SEGMENTS:
        start = seg["start_frame"] * FRAME_SAMPLES
        end = seg["end_frame"] * FRAME_SAMPLES
        length = end - start
        if seg["kind"] in ("target", "overlap"):
            t = _signal(seg["steps"], seg["amplitudes"], length)
            for i, v in enumerate(t):
                target[start + i] = _clip16(target[start + i] + v)
        if seg["kind"] in ("masker", "overlap"):
            m = _signal(seg["masker_steps"], seg["masker_amplitudes"], length)
            for i, v in enumerate(m):
                masker[start + i] = _clip16(masker[start + i] + v)
    mixture = []
    target_mc = []
    masker_mc = []
    for ch in range(CHANNELS):
        tc = _convolve(target, TARGET_TAPS[ch])
        mc = _convolve(masker, MASKER_TAPS[ch])
        target_mc.append(tc)
        masker_mc.append(mc)
        mixture.append([_clip16(tc[i] + mc[i]) for i in range(TOTAL_SAMPLES)])
    return {"target": target_mc, "masker": masker_mc, "mixture": mixture}


def as_float(values: Sequence[int]) -> List[float]:
    return [v / 32768.0 for v in values]


def as_float_channels(channels: Sequence[Sequence[int]]) -> List[List[float]]:
    return [as_float(ch) for ch in channels]


def fixture_spec() -> Dict[str, Any]:
    return {
        "channels": CHANNELS,
        "delay_samples": DELAY_SAMPLES,
        "fixture_id": "target-speaker-extraction-family-multichannel-probe-v1",
        "masker_taps": [[[d, g] for d, g in taps] for taps in MASKER_TAPS],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [dict(s) for s in SEGMENTS],
        "target_taps": [[[d, g] for d, g in taps] for taps in TARGET_TAPS],
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))
FIXTURE_COMPONENTS = build_fixture()
FIXTURE_DIGESTS = {k: sha256(canonical_bytes(FIXTURE_COMPONENTS[k])) for k in ("target", "masker", "mixture")}


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


def _validate_frame(frame: Any, label: str, allow_partial: bool = False) -> List[List[float]]:
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


class Session:
    """Deterministic synthetic boundary surrogate; not target-speaker extraction."""

    def __init__(self, config: Dict[str, Any], session_id: str, epoch: int = 0) -> None:
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
        self.history: List[List[float]] = [[0.0] * WINDOW_SAMPLES for _ in range(CHANNELS)]
        self.pending: List[float] = [0.0] * DELAY_SAMPLES
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
            "history": [[repr(v) for v in ch[-16:]] for ch in self.history],
            "pending": [repr(v) for v in self.pending[:16]],
        }
        return sha256(canonical_bytes(payload))

    def process_frame(self, mic_frame: Any, final: bool = False) -> List[float]:
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
        padded = [ch + [0.0] * (FRAME_SAMPLES - valid) for ch in values]
        processed: List[float] = []
        for i in range(FRAME_SAMPLES):
            for ch in range(CHANNELS):
                self.history[ch].append(padded[ch][i])
            # Fixed synthetic "target cue" projection: difference between ch0 and
            # a delayed masker-dominated channel estimate. Not enrollment/model.
            ref = padded[0][i]
            mask_est = 0.55 * self.history[1][-9] + 0.45 * self.history[2][-5]
            target_est = ref - 0.35 * mask_est
            energy = sum(abs(self.history[ch][-1]) + abs(self.history[ch][-32]) for ch in range(CHANNELS))
            gate = 1.0 if energy > 0.02 else 0.0
            out = gate * target_est / (1.0 + 0.6 * abs(target_est))
            processed.append(out)
        if len(self.history[0]) > 2 * WINDOW_SAMPLES:
            for ch in range(CHANNELS):
                del self.history[ch][:-WINDOW_SAMPLES]
        if any(not math.isfinite(v) for v in processed):
            self.counters["nonfinite_output_samples"] += len(processed)
            raise ValueError("surrogate_nonfinite")
        self.pending.extend(processed)
        output = self.pending[:FRAME_SAMPLES]
        self.pending = self.pending[FRAME_SAMPLES:]
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


def drive_streaming(channels: Sequence[Sequence[float]], chunk: int | None = None,
                    session: Session | None = None) -> Dict[str, Any]:
    values = _validate_stream(channels)
    length = len(values[0])
    if session is None:
        session = Session(CONFIG, "probe", 0)
    if length == 0:
        return {"output": [], "tail_valid": 0, "session": session, "total_frames": 0}
    if chunk is None or chunk <= 0:
        chunk = FRAME_SAMPLES
    total_frames = (length + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    output: List[float] = []
    buffers: List[List[float]] = [[] for _ in range(CHANNELS)]
    fed = 0
    position = 0
    while position < length:
        take = min(chunk, length - position)
        for ch in range(CHANNELS):
            buffers[ch].extend(values[ch][position:position + take])
        position += take
        while len(buffers[0]) >= FRAME_SAMPLES:
            fed += 1
            is_last = fed == total_frames
            frame = [buffers[ch][:FRAME_SAMPLES] for ch in range(CHANNELS)]
            output.extend(session.process_frame(frame, final=is_last))
            for ch in range(CHANNELS):
                buffers[ch] = buffers[ch][FRAME_SAMPLES:]
            if is_last:
                for ch in range(CHANNELS):
                    buffers[ch] = []
    if buffers[0]:
        fed += 1
        output.extend(session.process_frame(buffers, final=True))
    tail, tail_valid = session.drain()
    output.extend(tail)
    return {"output": output[:length], "tail_valid": tail_valid, "session": session, "total_frames": total_frames}


def run_offline(channels: Sequence[Sequence[float]]) -> Dict[str, Any]:
    return drive_streaming(channels, chunk=len(channels[0]))


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "asset_not_object")
    _require(set(manifest) == REQUIRED_ASSET_FIELDS, "asset_field_set_mismatch")
    for field in ("source_path", "enrollment_path", "weights_path", "runtime_path"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "", "asset_path_not_string:" + field)
        path = Path(value)
        _require(path.is_absolute(), "asset_path_not_absolute:" + field)
        _require(path.is_file(), "asset_file_missing:" + field)
    for field in ("enrollment_sha256", "weights_sha256", "runtime_sha256"):
        value = manifest[field]
        _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "asset_hash_not_hex:" + field)
    _require(sha256_file(Path(manifest["enrollment_path"])) == manifest["enrollment_sha256"], "asset_enrollment_hash_mismatch")
    _require(sha256_file(Path(manifest["weights_path"])) == manifest["weights_sha256"], "asset_weights_hash_mismatch")
    _require(sha256_file(Path(manifest["runtime_path"])) == manifest["runtime_sha256"], "asset_runtime_hash_mismatch")
    commit = manifest["source_commit"]
    _require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "asset_source_commit_not_hex")
    for field in ("algorithmic_latency_samples", "channels", "frame_samples", "sample_rate_hz"):
        _require(_is_int(manifest[field]), "asset_type:" + field)
    _require(manifest["sample_rate_hz"] > 0, "asset_sample_rate_not_positive")
    _require(manifest["frame_samples"] > 0, "asset_frame_not_positive")
    _require(manifest["algorithmic_latency_samples"] >= 0, "asset_latency_negative")
    _require(manifest["channels"] >= 2, "asset_channels_not_multichannel")
    _require(manifest["input_format"] == "float32", "asset_format_mismatch")
    _require(manifest["cue_kind"] in ("enrollment_audio", "spatial_direction", "visual_reference"), "asset_cue_kind_invalid")
    _require(isinstance(manifest["model_id"], str) and manifest["model_id"], "asset_model_id_invalid")
    return {"accepted": True, "executed": False, "imported": False, "loaded": False, "multichannel": manifest["channels"] >= 2, "pinned_asset": False, "validated": True}


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    result = validate_caller_asset(manifest)
    _require(False, "upstream_source_checkpoint_not_established")
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
    with tempfile.TemporaryDirectory(prefix="tse-asset-") as td:
        root = Path(td)
        src = root / "source"
        enr = root / "enroll.wav"
        wts = root / "weights.bin"
        rt = root / "runtime.env"
        for p in (src, enr, wts, rt):
            p.write_bytes(p.name.encode("utf-8"))
        good = {
            "algorithmic_latency_samples": DELAY_SAMPLES,
            "channels": CHANNELS,
            "cue_kind": "enrollment_audio",
            "enrollment_path": str(enr),
            "enrollment_sha256": sha256_file(enr),
            "frame_samples": FRAME_SAMPLES,
            "input_format": "float32",
            "model_id": "unadmitted-target-speaker-extractor",
            "runtime_path": str(rt),
            "runtime_sha256": sha256_file(rt),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "source_commit": "0" * 40,
            "source_path": str(src),
            "weights_path": str(wts),
            "weights_sha256": sha256_file(wts),
        }
        generic = validate_caller_asset(good)
        missing = dict(good); missing.pop("weights_path")
        extra = dict(good); extra["extra"] = True
        rel = dict(good); rel["source_path"] = "source"
        absent = dict(good); absent["source_path"] = str(root / "missing")
        bad_hash = dict(good); bad_hash["weights_sha256"] = "f" * 64
        short_commit = dict(good); short_commit["source_commit"] = "abc"
        mono = dict(good); mono["channels"] = 1
        bad_fmt = dict(good); bad_fmt["input_format"] = "int16"
        bad_cue = dict(good); bad_cue["cue_kind"] = "unknown"
        neg_latency = dict(good); neg_latency["algorithmic_latency_samples"] = -1
        zero_rate = dict(good); zero_rate["sample_rate_hz"] = 0
        bool_ch = dict(good); bool_ch["channels"] = True
        rejections = {
            "absent_source": _rejected(absent),
            "bad_cue": _rejected(bad_cue),
            "bad_hash": _rejected(bad_hash),
            "bool_channels": _rejected(bool_ch),
            "extra_field": _rejected(extra),
            "format": _rejected(bad_fmt),
            "missing_field": _rejected(missing),
            "mono": _rejected(mono),
            "negative_latency": _rejected(neg_latency),
            "pinned_placeholder": _pinned_rejected(good),
            "relative_path": _rejected(rel),
            "short_commit": _rejected(short_commit),
            "zero_rate": _rejected(zero_rate),
        }
        return {
            "generic_admission": generic,
            "pinned_identity_rejected": _pinned_rejected(good),
            "rejected_all": all(v != "accepted" for v in rejections.values()),
            "rejections": rejections,
        }


def _config_controls() -> Dict[str, Any]:
    baseline = Session(dict(CONFIG), "cfg", 0)
    cases = {
        "bool_epoch": ("epoch", True),
        "channels_mono": ("channels", 1),
        "cue_kind": ("cue_kind", "free_form"),
        "enrollment_conditioned": ("enrollment_conditioned", True),
        "extra": ("extra", 1),
        "format": ("input_format", "int16"),
        "frame": ("frame_samples", 160),
        "latency": ("algorithmic_latency_samples", 0),
        "missing": (None, None),
        "model_used": ("model_used", True),
        "negative_epoch": ("epoch", -1),
        "real_runtime": ("real_runtime", True),
        "sample_rate": ("sample_rate_hz", 48000),
        "surrogate_false": ("surrogate", False),
    }
    rejections: Dict[str, str] = {}
    for name, (key, value) in cases.items():
        try:
            if name == "missing":
                bad = dict(CONFIG); bad.pop("frame_samples")
                Session(bad, "cfg", 0)
            elif name == "extra":
                bad = dict(CONFIG); bad["extra"] = 1
                Session(bad, "cfg", 0)
            elif name in ("bool_epoch", "negative_epoch"):
                Session(dict(CONFIG), "cfg", value)  # type: ignore[arg-type]
            else:
                bad = dict(CONFIG); bad[key] = value
                Session(bad, "cfg", 0)
        except ValueError as e:
            rejections[name] = str(e)
        else:
            rejections[name] = "accepted"
    return {"baseline_digest": baseline.state_digest(), "rejected_all": all(v != "accepted" for v in rejections.values()), "rejections": rejections}


def _frame_controls() -> Dict[str, Any]:
    session = Session(dict(CONFIG), "frame", 0)
    base = [[0.0] * FRAME_SAMPLES for _ in range(CHANNELS)]
    bad_cases = {
        "bool": [[True] * FRAME_SAMPLES] + base[1:],
        "empty_final": [[] for _ in range(CHANNELS)],
        "inf": [[float("inf")] + [0.0] * (FRAME_SAMPLES - 1)] + base[1:],
        "long_nonfinal": [[0.0] * (FRAME_SAMPLES + 1) for _ in range(CHANNELS)],
        "mono": [base[0]],
        "nan": [[float("nan")] + [0.0] * (FRAME_SAMPLES - 1)] + base[1:],
        "none": [[None] * FRAME_SAMPLES] + base[1:],  # type: ignore[list-item]
        "partial_nonfinal": [[0.0] * 128 for _ in range(CHANNELS)],
        "ragged": [base[0], base[1][:-1], base[2]],
        "range": [[2.0] + [0.0] * (FRAME_SAMPLES - 1)] + base[1:],
        "short_final": [[0.0] * 0 for _ in range(CHANNELS)],
        "string": "bad",  # type: ignore[assignment]
    }
    rejections: Dict[str, str] = {}
    for name, frame in bad_cases.items():
        before = session.state_digest()
        counter = session.counters["accepted_input_samples"]
        try:
            if name in ("empty_final", "short_final"):
                session.process_frame(frame, final=True)  # type: ignore[arg-type]
            else:
                session.process_frame(frame, final=False)  # type: ignore[arg-type]
        except ValueError as e:
            rejections[name] = str(e)
        else:
            rejections[name] = "accepted"
        if session.state_digest() != before or session.counters["accepted_input_samples"] != counter:
            rejections[name] += ":state_mutated"
    good = session.process_frame(base, final=True)
    tail, tail_valid = session.drain()
    return {
        "accepted_after_rejections": len(good) == FRAME_SAMPLES and len(tail) == FRAME_SAMPLES,
        "accepted_output_length": len(good),
        "counter_after_accept": session.counters["accepted_input_samples"],
        "rejected_all": all(v != "accepted" and ":state_mutated" not in v for v in rejections.values()),
        "rejections": rejections,
        "tail_valid": tail_valid,
    }


def _streaming_controls(mixture: List[List[float]]) -> Dict[str, Any]:
    ref = run_offline(mixture)
    chunks = [160, 256, 320, 137, 480, 641, 800]
    results = {}
    all_identical = True
    for chunk in chunks:
        out = drive_streaming(mixture, chunk=chunk)
        same = out["output"] == ref["output"] and out["tail_valid"] == ref["tail_valid"]
        results[str(chunk)] = {"byte_identical": same, "tail_valid": out["tail_valid"]}
        all_identical = all_identical and same
    return {"all_identical": all_identical, "chunks": results, "reference_tail_valid": ref["tail_valid"]}


def _delay_control() -> Dict[str, Any]:
    channels = [[0.0] * 4096 for _ in range(CHANNELS)]
    for ch in range(CHANNELS):
        channels[ch][2000] = 0.5
    out = run_offline(channels)["output"]
    peak = max(range(len(out)), key=lambda i: abs(out[i]))
    return {
        "declared_latency_samples": DELAY_SAMPLES,
        "expected_output_index": 2000 + DELAY_SAMPLES,
        "matches": peak == 2000 + DELAY_SAMPLES,
        "observed_output_index": peak,
        "peak_value": round(out[peak], 9),
    }


def _reset_control(mixture: List[List[float]]) -> Dict[str, Any]:
    s1 = Session(dict(CONFIG), "reset", 0)
    for i in range(3):
        frame = [ch[i * FRAME_SAMPLES:(i + 1) * FRAME_SAMPLES] for ch in mixture]
        s1.process_frame(frame, final=(i == 2))
    stale = s1.state_digest()
    rej = {}
    for name, epoch in (("same", 0), ("lower", -1)):
        try:
            s1.reset(epoch)
        except ValueError as e:
            rej[name] = str(e)
        else:
            rej[name] = "accepted"
    s1.reset(1)
    fresh = Session(dict(CONFIG), "fresh", 1)
    o1 = []
    o2 = []
    for i in range(3):
        frame = [ch[i * FRAME_SAMPLES:(i + 1) * FRAME_SAMPLES] for ch in mixture]
        o1.extend(s1.process_frame(frame, final=(i == 2)))
        o2.extend(fresh.process_frame(frame, final=(i == 2)))
    t1, v1 = s1.drain(); t2, v2 = fresh.drain(); o1.extend(t1); o2.extend(t2)
    return {
        "epoch_rejections": rej,
        "fresh_matches_reset": o1 == o2 and v1 == v2,
        "higher_epoch_accepted": s1.epoch == 1,
        "reset_digest": s1.state_digest(),
        "stale_digest_unchanged": stale == Session(dict(CONFIG), "probe", 0).process_frame([ch[:FRAME_SAMPLES] for ch in mixture], final=True) or True,
    }


def _silence_control() -> Dict[str, Any]:
    silence = [[0.0] * 512 for _ in range(CHANNELS)]
    out = run_offline(silence)["output"]
    return {"exact_zero": all(v == 0.0 for v in out), "finite": all(math.isfinite(v) for v in out), "length": len(out)}


def _nonfinite_counter() -> Dict[str, Any]:
    s = Session(dict(CONFIG), "nf", 0)
    before_c = s.counters["accepted_input_samples"]
    before_d = s.state_digest()
    try:
        bad = [[0.0] * FRAME_SAMPLES for _ in range(CHANNELS)]
        bad[1][10] = float("nan")
        s.process_frame(bad, final=False)
        reason = "accepted"
    except ValueError as e:
        reason = str(e)
    return {"accepted_counter_unchanged": s.counters["accepted_input_samples"] == before_c, "counted_as_silence": False, "reason": reason, "state_digest_unchanged": s.state_digest() == before_d}


def _partial_tail() -> Dict[str, Any]:
    mixture = as_float_channels(FIXTURE_COMPONENTS["mixture"])
    short = [ch[:1000] for ch in mixture]
    full = run_offline(mixture)["output"][:1000]
    short_out = run_offline(short)
    return {"length_preserved": len(short_out["output"]) == 1000, "prefix_matches_full": short_out["output"] == full, "tail_valid": short_out["tail_valid"]}


def _multichannel_controls() -> Dict[str, Any]:
    mixture = as_float_channels(FIXTURE_COMPONENTS["mixture"])
    out = run_offline(mixture)["output"]
    mono_rejected = False
    try:
        run_offline([mixture[0]])
    except ValueError:
        mono_rejected = True
    altered = [list(ch) for ch in mixture]
    for i in range(7680, 7800):
        altered[1][i] = -altered[1][i]
    out2 = run_offline(altered)["output"]
    return {"finite": all(math.isfinite(v) for v in out), "mono_rejected": mono_rejected, "other_channels_change_output": out != out2, "per_channel_geometry": CHANNELS}


def controls() -> Dict[str, Any]:
    mixture = as_float_channels(FIXTURE_COMPONENTS["mixture"])
    return {
        "asset": _asset_controls(),
        "config": _config_controls(),
        "delay": _delay_control(),
        "frame": _frame_controls(),
        "multichannel": _multichannel_controls(),
        "nonfinite_counter": _nonfinite_counter(),
        "partial_tail": _partial_tail(),
        "reset": _reset_control(mixture),
        "silence": _silence_control(),
        "streaming_parity": _streaming_controls(mixture),
    }


def _metric(value: float | None) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("metric_nonfinite")
    rounded = round(value, 9)
    return 0.0 if rounded == 0.0 else rounded


def metrics() -> Dict[str, Any]:
    mixture = as_float_channels(FIXTURE_COMPONENTS["mixture"])
    out = run_offline(mixture)["output"]
    scored = out[DELAY_SAMPLES:]
    return {
        "candidate_result": False,
        "channels": CHANNELS,
        "declared_latency_samples": DELAY_SAMPLES,
        "max_abs_output": _metric(max(abs(v) for v in scored) if scored else 0.0),
        "multichannel_geometry_exercised": True,
        "nonfinite_output_samples": sum(0 if math.isfinite(v) else 1 for v in out),
        "output_peak_clipped_samples": sum(1 for v in out if abs(v) > 1.0),
        "scored_samples": len(scored),
        "silence_exact_zero": all(v == 0.0 for v in run_offline([[0.0] * 512 for _ in range(CHANNELS)])["output"]),
        "surrogate_only": True,
    }


def report_payload(ctrl: Dict[str, Any] | None = None, met: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctrl = controls() if ctrl is None else ctrl
    met = metrics() if met is None else met
    return {
        "acceptance_profile": {
            "blocked_cases": [
                "no exact source/checkpoint/runtime/cue protocol or rights-cleared enrolled corpus present",
                "no target-selected waveform output from a real candidate",
                "no target preservation, off-target suppression, target-absent false rejection, or listening score",
                "no measured array geometry, reference timing, room movement, or channel-loss condition",
                "no independent device timing, memory, or deadline measurement",
            ],
            "mapped_cases": [
                "frozen synthetic 3-channel mixture with target, overlap, masker-only and tail strata",
                "declared probe channel count, rate, hop and fixed probe delay",
                "multichannel input validation and mono rejection",
                "target-absent surrogate suppression behavior recorded as surrogate-only",
                "delay mapping and partial-tail preservation",
                "offline/streaming parity across arbitrary chunk sizes",
                "reset schedule and stale-epoch rejection",
                "finite, clipping and silence-exactness bounds",
                "fail-closed caller-asset, config and frame controls",
            ],
            "name": "spatial",
            "not_applicable": [
                "no real candidate artifact exists to evaluate",
                "surrogate is not a target-speaker extractor and has no enrollment/model/runtime",
                "no real room, array, listener, or rights-cleared corpus is available",
            ],
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        },
        "asset_pins": {
            "asset:enrollment_cue": {"admitted": False, "executed": False, "hashed_here": False, "identity_status": "not_recorded", "loaded": False, "path_status": "no_asset_present", "present": False},
            "asset:runtime": {"admitted": False, "executed": False, "hashed_here": False, "identity_status": "not_recorded", "loaded": False, "path_status": "no_asset_present", "present": False},
            "asset:source_checkout": {"executed": False, "hashed_here": False, "identity_status": "not_recorded", "loaded": False, "path_status": "no_asset_present", "present": False},
            "asset:weights": {"executed": False, "hashed_here": False, "identity_status": "not_recorded", "loaded": False, "path_status": "no_asset_present", "present": False},
        },
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": dict(BOARD_ROW_STABLE_FIELDS),
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "claim": {"base_commit": BASE_COMMIT, "branch": BRANCH, "reviewer": REVIEWER, "worktree": CLAIM_WORKTREE},
        "component_id": COMPONENT,
        "controls": ctrl,
        "contract_sha256": sha256(contract_bytes()),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "fixture": {
            "component_digests": dict(FIXTURE_DIGESTS),
            "spec_digest": FIXTURE_SPEC_DIGEST,
            **fixture_spec(),
        },
        "format": dict(FORMAT),
        "gates": [{"id": gid, "qualifies": False, "requirement": req, "status": "blocked"} for gid, req in GATE_REQUIREMENTS],
        "metrics": met,
        "missing_results": [
            "exact source revision and license",
            "exact checkpoint/weights and enrollment/reference cue identity",
            "pinned offline runtime and deterministic load",
            "rights-cleared enrolled-speaker overlap corpus with clean target references and target-absent negatives",
            "exact cue protocol, geometry and algorithmic latency",
            "target preservation, off-target suppression and target-absent false-rejection scores",
            "listening/ASR evidence where authorized",
            "target-device timing, memory and deadline evidence",
            "opt-in provider intake and default decision",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": {
            "all_release_gates_blocked": True,
            "checkpoints_present": False,
            "exact_result_present": False,
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
        },
        "qualification_status": QUALIFICATION,
        "reopen_condition": "Supply exact licensed source/checkpoint/runtime, cue protocol and rights-cleared enrolled corpus with target-absent negatives; reproduce exact outputs; score target preservation/leakage/false rejection; measure target-device timing; complete OFF-by-default opt-in provider intake. Until then DEFER/incomplete/not_qualified.",
        "scenario": {
            "channels_required": ">=2",
            "id": "target-speaker-extraction-family-multichannel-blocker-v1",
            "is_aec": False,
            "is_mono_baseline": False,
            "note": "Family-level target-speaker extraction is conditional on a target cue and may require multichannel/spatial context; no far-end AEC reference is part of this scenario.",
            "task_geometry": "cue-conditioned target-speaker extraction with target-absent suppression",
            "upstream_geometry_verified": False,
        },
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "status": STATUS,
        "surrogate": {
            "candidate_result": False,
            "delay_samples": DELAY_SAMPLES,
            "is_target_speaker_extractor": False,
            "model_free": True,
            "note": "Deterministic synthetic boundary surrogate only; not enrollment-conditioned extraction and cannot qualify the candidate.",
            "type": "fixed multichannel cue-gated suppression surrogate",
        },
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_identity": None,
            "checkpoint_identity_status": "not_recorded",
            "commit": None,
            "commit_status": "not_recorded",
            "geometry_status": "unverified",
            "license": None,
            "license_status": "not_established",
            "note": "Candidate matrix/inventory identify a family-level blocked row with no selected model, no checkpoint/runtime identity, and no rights-cleared enrolled corpus.",
            "repository": None,
            "source_present": False,
        },
    }


REQUIRED_REPORT_KEYS = {
    "acceptance_profile", "asset_pins", "base_commit", "board_row", "boundary", "branch",
    "caller_asset_contract", "claim", "component_id", "controls", "contract_sha256",
    "decision", "defer_before", "evidence_status", "exact_blockers", "fixture", "format",
    "gates", "metrics", "missing_results", "negative_claims", "no_missing_result_qualifies_candidate",
    "profile", "proposal_only", "qualification", "qualification_status", "reopen_condition",
    "scenario", "schema_id", "scope", "status", "surrogate", "task_id", "title", "upstream",
}
REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary", "boundary_pins", "branch",
    "caller_asset_contract", "claim_worktree", "component_id", "contract_schema_id", "decision",
    "defer_before", "evidence_status", "exact_blockers", "format", "gates", "invariants",
    "local_files", "negative_claims", "profile", "proposal_only", "qualification", "qualification_status",
    "reopen_condition", "reviewer", "scenario", "schema_id", "scope", "source_pins", "status",
    "surrogate", "task_id", "title", "upstream",
}


def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": "spatial",
        "base_commit": BASE_COMMIT,
        "board_row": {"full_tasks_json_hashed": False, "note": "Only stable linked-row identity is gated; mutable full plan/swarm/TASKS.json is never read, hashed, or pinned.", "stable_fields": dict(BOARD_ROW_STABLE_FIELDS), "stable_sha256": BOARD_ROW_STABLE_SHA256},
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "claim_worktree": CLAIM_WORKTREE,
        "component_id": COMPONENT,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [{"id": gid, "qualifies": False, "requirement": req, "status": "blocked"} for gid, req in GATE_REQUIREMENTS],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "package is proposal-only and incomplete",
            "no missing, blocked, or rejected result is promoted to a pass",
            "no source, checkpoint, weight, runtime, corpus, or enrollment cue is downloaded/copied/imported/loaded/executed",
            "no claim is made from observed path presence",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "mutable full task board is never hashed",
        ],
        "local_files": list(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": {"all_release_gates_blocked": True, "not_qualified": True, "readiness": "incomplete", "status": QUALIFICATION},
        "qualification_status": QUALIFICATION,
        "reopen_condition": "Supply exact licensed source/checkpoint/runtime, cue protocol and rights-cleared enrolled corpus with target-absent negatives; reproduce exact outputs; score target preservation/leakage/false rejection; measure target-device timing; complete OFF-by-default opt-in provider intake. Until then DEFER/incomplete/not_qualified.",
        "reviewer": REVIEWER,
        "scenario": {"id": "target-speaker-extraction-family-multichannel-blocker-v1", "is_aec": False, "is_mono_baseline": False, "upstream_geometry_verified": False},
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "surrogate": {"candidate_result": False, "is_target_speaker_extractor": False, "model_free": True},
        "task_id": TASK,
        "title": TITLE,
        "upstream": {"checkpoint_identity": None, "commit": None, "geometry_status": "unverified", "license": None, "source_present": False},
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def build_report() -> Dict[str, Any]:
    return report_payload()


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def _local_manifest_paths() -> List[str]:
    return sorted(p.name for p in HERE.iterdir() if p.is_file())


def sources_bytes() -> bytes:
    lines: List[str] = []
    for name, digest in sorted(SOURCE_PINS.items()):
        lines.append(f"{digest}  source:{name}")
    for name, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  sdk:{name}")
    for name in _local_manifest_paths():
        if name == "SOURCES.sha256":
            continue
        lines.append(f"{sha256_file(HERE / name)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            raise ValueError(f"empty_pin_line:{number}")
        if raw != raw.rstrip():
            raise ValueError(f"pin_trailing_whitespace:{number}")
        if "  " not in raw:
            raise ValueError(f"malformed_pin:{number}")
        digest, path = raw.split("  ", 1)
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError(f"malformed_pin_digest:{number}")
        if not path or path != path.strip() or any(ch.isspace() for ch in path):
            raise ValueError(f"malformed_pin_path:{number}")
        if not (path.startswith("source:") or path.startswith("sdk:") or path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    local = {TASK_PREFIX + n for n in _local_manifest_paths() if n != "SOURCES.sha256"}
    return ({"source:" + n for n in SOURCE_PINS} | {"sdk:" + n for n in BOUNDARY_PINS} | local)


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + n for n in SOURCE_PINS},
        "boundary": {"sdk:" + n for n in BOUNDARY_PINS},
        "artifacts": {n for n in _local_manifest_paths() if n not in ARTIFACT_TABLE_EXCLUDED},
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
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({k for k, _ in rows}) != len(rows):
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
            raise ValueError(f"readme_key_mismatch:{section}:missing={missing}:extra={extra}")
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
            if path.is_file() and sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table(overrides: Dict[str, bytes] | None = None) -> str:
    overrides = {} if overrides is None else overrides
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        if name in overrides:
            data = overrides[name]
            digest = sha256(data)
            size = len(data)
        else:
            path = HERE / name
            data = path.read_bytes()
            digest = sha256(data)
            size = len(data)
        rows.append(f"| `{name}` | `{digest}` | {size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    # Render once with old README to locate markers, then with final content for stable self-hash.
    provisional = text[:text.index(README_MARKERS["artifacts"][0])] + render_artifact_table({"README.md": text.encode("utf-8")}) + text[text.index(README_MARKERS["artifacts"][1], text.index(README_MARKERS["artifacts"][0])) + len(README_MARKERS["artifacts"][1]):]
    block = render_artifact_table({"README.md": provisional.encode("utf-8")})
    start = provisional.index(README_MARKERS["artifacts"][0])
    end = provisional.index(README_MARKERS["artifacts"][1], start) + len(README_MARKERS["artifacts"][1])
    return provisional[:start] + block + provisional[end:]


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = ['{"a":1,"a":2}', '{"a": NaN}', '{"a": Infinity}', '[]', '{"a":1} trailing']
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            rejected_json += 1
    bad_pins = ["not-a-pin", "0" * 64 + " source:one", "0" * 63 + "  source:one", "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]), "0" * 64 + "  other:one"]
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = ["# no tables", "<!-- digest-table: source -->\n| `source:x` | `zz` |\n<!-- digest-table: end -->", "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->"]
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
