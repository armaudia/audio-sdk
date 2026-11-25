# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-ROSE-CD-RMS-MATCHED.

The task models the *research* ``ROSE-CD input-RMS-matched`` configuration: an
offline whole-clip post-processor that rescales ROSE-CD one-step output so its
root-mean-square level equals the noisy input level, without a clean reference.

The exact licensed checkpoint, the PyTorch runtime and an approved definition of
the RMS-matching recipe are absent.  This module therefore never imports a
neural runtime, never loads a checkpoint and never downloads anything.  It
composes a clearly labelled, model-free surrogate enhancer with the *real*
whole-clip RMS-matching boundary so that at least the post-processing contract
and its invariants are verifiable.  Nothing here qualifies ROSE-CD.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-ROSE-CD-RMS-MATCHED"
TITLE = "ROSE-CD RMS-matched"
SLUG = "rose-cd-rms-matched"
COMPONENT = "rose-cd-rms-matched"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "ab7ce893032ea7771d9d367638e8d09076ff5db3"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    + TASK
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

UPSTREAM_REPOSITORY = "https://github.com/LiangXu123/ROSE-CD"
UPSTREAM_COMMIT = "8a7477f046a133737d6f1744b643fbe3f3ea96cd"
UPSTREAM_LICENSE = "MIT"
CHECKPOINT_REVISION = "1c80e0863c1a8682f52a8e5be2efdf58a130eb62"
CHECKPOINT_FILENAME = "last.ckpt"
CHECKPOINT_PATH = "data/models/rose-cd/" + CHECKPOINT_FILENAME
CHECKPOINT_SHA256 = (
    "5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4")
CHECKPOINT_BYTES = 1313064415
CHECKPOINT_HF_PATH = "logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt"
SOURCE_CHECKOUT_PATH = "data/checkouts/ROSE-CD"
RUNTIME_ENV_PATH = "data/envs/" + SLUG
RUNTIME_DECLARATION = "Python 3.11 + PyTorch/PyTorch-Lightning CPU"

ADAPTER_JSON_PATH = "adapters/rose-cd/adapter.json"
ADAPTER_README_PATH = "adapters/rose-cd/README.md"
ADAPTER_RUN_PATH = "adapters/rose-cd/run.py"
PILOT_PATH = "research/noise_suppression_pilot_20261027.md"
ASSET_LEDGER_PATH = "research/noise_suppression_assets_20261027.json"
CANDIDATE_MATRIX_PATH = "research/voice-enhancement-20261101/candidate_matrix.csv"
CENSUS_PATH = "research/noise_suppression_candidate_census.md"
PHASE_COMPLETION_PATH = "research/denoising_phase_completion_20261028.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
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
    "9994eb124d313f8d8d6e10d625848cd1a594598b4c2b3a68072346ced912513b")

# Geometry: installed v0 stays 16 kHz mono f32 at 160 samples per frame.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
TOTAL_FRAMES = 200
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES

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
    {"id": "silence", "start_frame": 0, "end_frame": 25, "kind": "silence"},
    {"id": "noise-only", "start_frame": 25, "end_frame": 50, "kind": "noise",
     "noise_gain": 2},
    {"id": "speech-a", "start_frame": 50, "end_frame": 100, "kind": "speech",
     "steps": (2, 3, 5), "amplitudes": (55, 28, 15)},
    {"id": "noisy-speech", "start_frame": 100, "end_frame": 150,
     "kind": "speech", "steps": (3, 4, 6), "amplitudes": (50, 26, 14),
     "noise_gain": 2},
    {"id": "speech-b-transient", "start_frame": 150, "end_frame": 200,
     "kind": "speech", "steps": (1, 4, 7), "amplitudes": (48, 29, 16),
     "click_period": 1024, "click_amplitude": 900},
)

CONFIG: Dict[str, Any] = {
    "channels": CHANNELS,
    "execution": "offline_whole_clip",
    "frame_samples": FRAME_SAMPLES,
    "model_used": False,
    "real_runtime": False,
    "rms_match_reference": "noisy_input",
    "rms_match_scope": "whole_clip",
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "variant": "one-step-rms-matched",
}

REQUIRED_ASSET_FIELDS = {
    "channels",
    "checkpoint_path",
    "checkpoint_revision",
    "checkpoint_sha256",
    "frame_samples",
    "peak_policy",
    "rms_match_reference",
    "rms_match_scope",
    "sample_rate_hz",
    "source_dir",
    "source_revision",
    "variant",
}
PINNED_ASSET_VALUES: Dict[str, Any] = {
    "channels": CHANNELS,
    "checkpoint_revision": CHECKPOINT_REVISION,
    "peak_policy": "unpinned",
    "rms_match_reference": "noisy_input",
    "rms_match_scope": "whole_clip",
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "source_revision": UPSTREAM_COMMIT,
    "variant": "one-step-rms-matched",
}
SOURCE_MARKERS: Tuple[str, ...] = (
    "LICENSE",
    "enhancement.py",
    "sgmse/model.py",
    "sgmse/data_module.py",
    "sgmse/util/other.py",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": (
        "validate_hash_geometry_and_revision_only; do_not_load_or_execute_"
        "in_this_package"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "separate_model_archive_required": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "checkpoint_path and source_dir are caller-owned absolute paths",
        "SHA-256 of the checkpoint file matches the manifest",
        "source_revision equals the pinned ROSE-CD commit",
        "checkpoint_revision equals the pinned Hugging Face revision",
        "sample rate, channels and frame size equal 16 kHz mono / 160",
        "variant is one-step-rms-matched; raw output is a separate task",
        "rms matching is whole_clip against the noisy input, never clean",
        "peak_policy remains unpinned until an approved recipe exists",
        "the pinned digest is checked separately; a placeholder is rejected",
        "no download, copy, import, load or execution occurs in this package",
    ],
    "weights_embedded_in_wheel": False,
}

FORMAT: Dict[str, Any] = {
    "asset_channels": CHANNELS,
    "asset_frame_samples": FRAME_SAMPLES,
    "asset_requires_clean_reference": False,
    "asset_sample_format": "float32",
    "asset_sample_rate_hz": SAMPLE_RATE_HZ,
    "execution_scope": "offline_whole_clip",
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "streaming_capable": False,
    "window_frames": TOTAL_FRAMES,
    "window_samples": TOTAL_SAMPLES,
}

RMS_MATCH_CONTRACT: Dict[str, Any] = {
    "clean_reference_used": False,
    "definition": (
        "output = gain * raw_enhanced, gain = rms(noisy_input) / "
        "rms(raw_enhanced), computed once over the whole clip"),
    "implicit_peak_clamp": False,
    "pinned_recipe": False,
    "reference": "noisy_input",
    "scope": "whole_clip",
    "silence_policy": (
        "zero noisy RMS returns exact zeros with an undefined gain; a zero "
        "enhanced RMS with nonzero noisy RMS is rejected"),
    "streaming_capable": False,
    "unknown_fields": [
        "exact gain formula and numerical precision of the research config",
        "zero/silence and near-zero tolerance policy",
        "peak/clip policy and any gain clamp",
        "per-clip versus per-segment aggregation",
    ],
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "checkpoint_absent",
        "requirement": (
            "Supply the exact ROSE-CD one-step checkpoint "
            f"{CHECKPOINT_HF_PATH} (Hugging Face revision "
            f"{CHECKPOINT_REVISION}) with SHA-256 {CHECKPOINT_SHA256} and "
            f"byte count {CHECKPOINT_BYTES} as a caller-owned external asset, "
            "verified locally without a network download."),
        "state": (
            f"{CHECKPOINT_PATH} is absent from both the research workspace "
            "and this SDK worktree; no caller manifest exists."),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Provide the pinned Python 3.11 PyTorch/PyTorch-Lightning CPU "
            "runtime in an isolated, hash-pinned environment and record the "
            "complete installed dependency set."),
        "state": (
            "PyTorch is not importable from the available Python 3.10, 3.11 "
            f"or 3.12 interpreters and no isolated runtime exists at "
            f"{RUNTIME_ENV_PATH}."),
    },
    {
        "id": "rms_match_recipe_unpublished",
        "requirement": (
            "Publish or approve the exact whole-clip noisy-input RMS-matching "
            "recipe: gain formula, zero/silence policy, near-zero tolerance, "
            "peak/clip policy, aggregation scope and numerical precision."),
        "state": (
            "The research record only states 'whole-clip RMS match to the "
            "noisy input'. No source file pins the gain formula, silence "
            "handling, peak/clip policy or precision, so an exact "
            "reproduction is undefined even with the checkpoint."),
    },
    {
        "id": "artifact_and_data_rights_uncleared",
        "requirement": (
            "Clear artifact-specific checkpoint redistribution and product-use "
            "rights, runtime dependency terms, and the VoiceBank-DEMAND / "
            "EARS-WHAM training-data rights chain with legal review."),
        "state": (
            "MIT source and model-card declarations do not establish "
            "checkpoint-artifact, runtime dependency, training-data or "
            "derivative-output rights; no legal review exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_model_identity",
     "Local checkpoint matches the pinned filename, byte count and SHA-256; "
     "the Hugging Face revision and source commit are immutable and verified "
     "without a download."),
    ("runtime_admission",
     "Hash-pinned isolated Python 3.11 PyTorch/PyTorch-Lightning runtime with "
     "an archived dependency set and recorded platform and flags."),
    ("artifact_rights",
     "Checkpoint, training-data, runtime, corpus, redistribution, product-use "
     "and derivative-output rights cleared with complete notices."),
    ("exact_reference_parity",
     "Approved exact-runtime raw ROSE-CD output vector and byte-level parity on "
     "the declared 16 kHz mono geometry."),
    ("rms_match_recipe_pinned",
     "Exact whole-clip noisy-input RMS-matching recipe, including silence, "
     "near-zero, peak/clip and precision policy, approved and reproducible."),
    ("rights_cleared_real_cohort",
     "Frozen rights-cleared paired DNS2020/EARS cohort with clean references, "
     "identity and raw-vs-matched separation."),
    ("independent_scoring_and_listening",
     "Independent paired SI-SDR/STOI/SNR or permitted listening, including "
     "identity and task-matched baselines, with failure controls."),
    ("target_runtime_timing_and_opt_in_provider",
     "Target-device p50/p95/p99, RTF, memory and deadline, plus opt-in provider "
     "intake, descriptor review and an explicit default decision."),
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
    "neural_runtime_invoked": False,
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
    "No ROSE-CD output, checkpoint, derived weight or PyTorch call was produced.",
    "No denoising, SNR, SI-SDR, STOI, latency, memory or release result is claimed.",
    "The synthetic surrogate is not ROSE-CD and cannot qualify the candidate.",
    "The RMS-matching boundary only rescales an already enhanced clip; it is not a model.",
    "Whole-clip RMS matching is not streaming-capable and has no device-timing result.",
    "No real corpus, clean reference, device clock or listener was used.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "Identity and the raw surrogate are controls; no candidate result is a pass.",
)

# Source pins are relative to the research workspace root.
SOURCE_PINS: Dict[str, str] = {
    ADAPTER_JSON_PATH:
        "552aab85aa61b9d4a4c33df930c96bec082156163718fcff867d70b40b4c306c",
    ADAPTER_README_PATH:
        "988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72",
    ADAPTER_RUN_PATH:
        "9fe6d70f8943da5d669778916df7c9416aa6b2a00389a3ee6e786229b5cbc951",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    CANDIDATE_MATRIX_PATH:
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    CENSUS_PATH:
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    PHASE_COMPLETION_PATH:
        "fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f",
    ASSET_LEDGER_PATH:
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    PILOT_PATH:
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    SOURCE_CHECKOUT_PATH + "/LICENSE":
        "1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd",
    SOURCE_CHECKOUT_PATH + "/README.md":
        "8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3",
    SOURCE_CHECKOUT_PATH + "/config.json":
        "815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a",
    SOURCE_CHECKOUT_PATH + "/requirements.txt":
        "d5e64c3b28a8c184a1e8e2507e66d210f34602143a452ed8513778f903bc7c48",
    SOURCE_CHECKOUT_PATH + "/enhancement.py":
        "dc19589a8666246fa03d79e8298cd258849d6f07f477139bef778893c49d11ff",
    SOURCE_CHECKOUT_PATH + "/scripts/eval_CT.sh":
        "3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c",
    SOURCE_CHECKOUT_PATH + "/sgmse/model.py":
        "1d6187c2997bf0e3184518dbd1c07c6704efa5d3ed50aff790495d4e13872237",
    SOURCE_CHECKOUT_PATH + "/sgmse/data_module.py":
        "fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b",
    SOURCE_CHECKOUT_PATH + "/sgmse/util/other.py":
        "092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0",
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
    "external": ("<!-- digest-table: external -->", "<!-- digest-table: end -->"),
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}


# ---------------------------------------------------------------------------
# Canonical JSON, hashing and strict parsing
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


def board_row_digest() -> str:
    """Digest only the stable linked-row identity, never the mutable file."""
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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
        if segment["kind"] != "speech":
            continue
        phases = [0, 0, 0]
        for offset in range(end - start):
            sample = 0
            for channel in range(3):
                phases[channel] = (
                    phases[channel] + segment["steps"][channel]) & 63
                sample += segment["amplitudes"][channel] * \
                    SINE64[phases[channel]]
            sample >>= 10
            if "click_period" in segment and \
                    offset % segment["click_period"] < 4:
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


def build_fixture() -> Dict[str, List[int]]:
    clean = _clean_track()
    noise = _noise_track()
    noisy = [_clip16(clean[index] + noise[index])
             for index in range(TOTAL_SAMPLES)]
    return {"clean": clean, "noise": noise, "noisy": noisy}


def as_float(values: Sequence[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def fixture_spec() -> Dict[str, Any]:
    return {
        "fixture_id": "rose-cd-rms-matched-dns-like-clip-v1",
        "frame_samples": FRAME_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [dict(segment) for segment in SEGMENTS],
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))


def component_digests(components: Dict[str, List[int]]) -> Dict[str, str]:
    return {key: sha256(canonical_bytes(components[key]))
            for key in ("clean", "noise", "noisy")}


FIXTURE_COMPONENTS = build_fixture()
FIXTURE_DIGESTS = component_digests(FIXTURE_COMPONENTS)


# ---------------------------------------------------------------------------
# Clone validation and the whole-clip RMS-matching boundary
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


def validate_clip(clip: Any, label: str = "clip") -> List[float]:
    if not isinstance(clip, (list, tuple)):
        raise ValueError(label + "_not_sequence")
    if not clip:
        raise ValueError(label + "_empty")
    values: List[float] = []
    for sample in clip:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError(label + "_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError(label + "_nonfinite")
        if abs(value) > 1.0:
            raise ValueError(label + "_range")
        values.append(value)
    return values


def rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rms_match(enhanced: Any, reference: Any) -> Dict[str, Any]:
    """Scale an enhanced clip so its whole-clip RMS equals the reference RMS.

    This is a pure, deterministic post-processor.  It never looks at a clean
    signal and it cannot stream: the gain depends on the complete clip.
    """
    enhanced_values = validate_clip(enhanced, "enhanced")
    reference_values = validate_clip(reference, "reference")
    if len(enhanced_values) != len(reference_values):
        raise ValueError("rms_match_length_mismatch")
    reference_rms = rms(reference_values)
    enhanced_rms = rms(enhanced_values)
    if reference_rms == 0.0:
        return {
            "gain": None,
            "defined": False,
            "matched": [0.0] * len(enhanced_values),
            "reference_rms": 0.0,
        }
    if enhanced_rms == 0.0:
        raise ValueError("rms_match_zero_enhanced")
    gain = reference_rms / enhanced_rms
    if not math.isfinite(gain) or gain <= 0.0:
        raise ValueError("rms_match_invalid_gain")
    matched = [gain * value for value in enhanced_values]
    if any(not math.isfinite(value) for value in matched):
        raise ValueError("rms_match_nonfinite_output")
    return {
        "gain": gain,
        "defined": True,
        "matched": matched,
        "reference_rms": reference_rms,
    }


# ---------------------------------------------------------------------------
# Deterministic model-free surrogate enhancer
# ---------------------------------------------------------------------------


def frame_noise_floor(values: Sequence[float]) -> float:
    """Minimum non-zero 160-sample frame RMS, used as a fixed noise floor."""
    floor = math.inf
    for start in range(0, len(values) - FRAME_SAMPLES + 1, FRAME_SAMPLES):
        frame = values[start:start + FRAME_SAMPLES]
        value = rms(frame)
        if value > 1e-12 and value < floor:
            floor = value
    if not math.isfinite(floor):
        return 0.0
    return floor


def surrogate_enhance(values: Sequence[float]) -> Dict[str, Any]:
    """Fixed whole-clip per-frame Wiener-amplitude gate; not ROSE-CD."""
    noise_floor = frame_noise_floor(values)
    noise_var = noise_floor * noise_floor
    gains: List[float] = []
    output: List[float] = []
    for start in range(0, len(values), FRAME_SAMPLES):
        frame = values[start:start + FRAME_SAMPLES]
        variance = sum(value * value for value in frame) / len(frame)
        if variance <= 0.0:
            gain = 0.0
        elif variance <= noise_var:
            gain = 0.0
        else:
            gain = math.sqrt(1.0 - noise_var / variance)
        gains.append(gain)
        output.extend(gain * value for value in frame)
    if any(not math.isfinite(value) for value in output):
        raise ValueError("surrogate_nonfinite")
    return {"frame_gains": gains, "noise_floor_rms": noise_floor,
            "output": output}


def process_offline(noisy: Any, config: Any = None) -> Dict[str, Any]:
    validate_config(CONFIG if config is None else config)
    values = validate_clip(noisy, "noisy")
    surrogate = surrogate_enhance(values)
    match = rms_match(surrogate["output"], values)
    return {
        "frame_gains": surrogate["frame_gains"],
        "gain": match["gain"],
        "matched": match["matched"],
        "matched_defined": match["defined"],
        "noise_floor_rms": surrogate["noise_floor_rms"],
        "raw": surrogate["output"],
    }


# ---------------------------------------------------------------------------
# Metrics
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


def snr_db(estimate: Sequence[float], reference: Sequence[float]
           ) -> float | None:
    if len(estimate) != len(reference):
        raise ValueError("snr_length_mismatch")
    signal = sum(value * value for value in reference)
    error = sum((a - b) ** 2 for a, b in zip(estimate, reference))
    if signal == 0.0:
        return None
    if error == 0.0:
        return 120.0
    return 10.0 * math.log10(signal / error)


def correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right):
        raise ValueError("correlation_length_mismatch")
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    covariance = sum((a - mean_left) * (b - mean_right)
                     for a, b in zip(left, right))
    left_energy = sum((a - mean_left) ** 2 for a in left)
    right_energy = sum((b - mean_right) ** 2 for b in right)
    if left_energy == 0.0 or right_energy == 0.0:
        return None
    return covariance / math.sqrt(left_energy * right_energy)


def peak(values: Sequence[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def clipped_count(values: Sequence[float]) -> int:
    return sum(1 for value in values if abs(value) >= 1.0)


def nonfinite_count(values: Sequence[float]) -> int:
    return sum(1 for value in values if not math.isfinite(value))


def metric_block(clean: Sequence[float], noisy: Sequence[float],
                 run: Dict[str, Any]) -> Dict[str, Any]:
    raw = run["raw"]
    matched = run["matched"]
    identity_si_sdr = si_sdr(noisy, clean)
    raw_si_sdr = si_sdr(raw, clean)
    matched_si_sdr = si_sdr(matched, clean)
    raw_snr = snr_db(raw, clean)
    matched_snr = snr_db(matched, clean)
    return {
        "identity": {
            "si_sdr_db": _metric(identity_si_sdr),
            "snr_db": _metric(snr_db(noisy, clean)),
            "rms": _metric(rms(noisy)),
            "peak": _metric(peak(noisy)),
        },
        "raw_surrogate": {
            "si_sdr_db": _metric(raw_si_sdr),
            "snr_db": _metric(snr_db(raw, clean)),
            "rms": _metric(rms(raw)),
            "peak": _metric(peak(raw)),
            "clipped_samples": clipped_count(raw),
            "nonfinite_samples": nonfinite_count(raw),
        },
        "rms_matched_surrogate": {
            "si_sdr_db": _metric(matched_si_sdr),
            "snr_db": _metric(snr_db(matched, clean)),
            "rms": _metric(rms(matched)),
            "peak": _metric(peak(matched)),
            "clipped_samples": clipped_count(matched),
            "nonfinite_samples": nonfinite_count(matched),
        },
        "si_sdr_delta_matched_minus_raw_db": _metric(
            None if raw_si_sdr is None or matched_si_sdr is None
            else matched_si_sdr - raw_si_sdr),
        "snr_delta_matched_minus_raw_db": _metric(
            None if raw_snr is None or matched_snr is None
            else matched_snr - raw_snr),
        "max_abs_output": _metric(max(peak(raw), peak(matched))),
        "scored_samples": TOTAL_SAMPLES,
        "clean_reference_used_for_scoring_only": True,
    }


# ---------------------------------------------------------------------------
# Controls (adverse/missing/invalid/nonfinite)
# ---------------------------------------------------------------------------


def _rejected(manifest: Any) -> str:
    try:
        validate_caller_asset(manifest)
    except (ValueError, OSError):
        return "rejected"
    return "accepted"


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_key_set_mismatch")
    for key, expected in PINNED_ASSET_VALUES.items():
        if manifest[key] != expected:
            raise ValueError("manifest_pin_mismatch:" + key)
    if isinstance(manifest["frame_samples"], bool) or \
            manifest["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("manifest_pin_mismatch:frame_samples")
    checkpoint = Path(manifest["checkpoint_path"])
    source = Path(manifest["source_dir"])
    if not checkpoint.is_absolute() or not checkpoint.is_file():
        raise ValueError("checkpoint_path")
    if not source.is_absolute() or not source.is_dir():
        raise ValueError("source_dir")
    if sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ValueError("checkpoint_sha256")
    return {
        "accepted": True,
        "executed": False,
        "imported": False,
        "loaded": False,
        "pinned_model": (
            manifest["checkpoint_sha256"] == CHECKPOINT_SHA256 and
            checkpoint.stat().st_size == CHECKPOINT_BYTES),
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    result = validate_caller_asset(manifest)
    if manifest["checkpoint_sha256"] != CHECKPOINT_SHA256:
        raise ValueError("checkpoint_not_pinned")
    checkpoint = Path(manifest["checkpoint_path"])
    if checkpoint.stat().st_size != CHECKPOINT_BYTES:
        raise ValueError("checkpoint_byte_count")
    source = Path(manifest["source_dir"])
    for marker in SOURCE_MARKERS:
        if not (source / marker).is_file():
            raise ValueError("source_marker_missing:" + marker)
    result["pinned_model"] = True
    return result


def _asset_controls() -> Dict[str, Any]:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="rose-cd-rms-asset-") as name:
        root = Path(name)
        checkpoint = root / CHECKPOINT_FILENAME
        checkpoint.write_bytes(b"caller-owned-placeholder-checkpoint")
        source = root / "ROSE-CD"
        source.mkdir()
        for marker in SOURCE_MARKERS:
            target = source / marker
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"marker")
        base = {
            "channels": CHANNELS,
            "checkpoint_path": str(checkpoint),
            "checkpoint_revision": CHECKPOINT_REVISION,
            "checkpoint_sha256": sha256_file(checkpoint),
            "frame_samples": FRAME_SAMPLES,
            "peak_policy": "unpinned",
            "rms_match_reference": "noisy_input",
            "rms_match_scope": "whole_clip",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "source_dir": str(source),
            "source_revision": UPSTREAM_COMMIT,
            "variant": "one-step-rms-matched",
        }
        rejections = {
            "extra_field": _rejected(dict(base, extra=True)),
            "missing_field": _rejected({k: v for k, v in base.items()
                                        if k != "peak_policy"}),
            "relative_checkpoint": _rejected(
                dict(base, checkpoint_path=CHECKPOINT_FILENAME)),
            "relative_source": _rejected(
                dict(base, source_dir=SOURCE_CHECKOUT_PATH)),
            "absent_checkpoint": _rejected(
                dict(base, checkpoint_path=str(root / "absent.ckpt"))),
            "checkpoint_hash_mismatch": _rejected(
                dict(base, checkpoint_sha256="0" * 64)),
            "wrong_source_revision": _rejected(
                dict(base, source_revision="0" * 40)),
            "wrong_checkpoint_revision": _rejected(
                dict(base, checkpoint_revision="0" * 40)),
            "wrong_sample_rate": _rejected(dict(base, sample_rate_hz=48000)),
            "wrong_channels": _rejected(dict(base, channels=2)),
            "wrong_frame": _rejected(dict(base, frame_samples=256)),
            "raw_variant": _rejected(dict(base, variant="one-step")),
            "streaming_scope": _rejected(
                dict(base, rms_match_scope="streaming")),
            "clean_reference": _rejected(
                dict(base, rms_match_reference="clean_input")),
            "guessed_peak_policy": _rejected(
                dict(base, peak_policy="clip_to_unity")),
        }
        accepted = validate_caller_asset(base)
    return {
        "generic_admission": accepted,
        "rejected_all": all(value == "rejected"
                            for value in rejections.values()),
        "rejections": rejections,
        "workspace_checkpoint_present": resolve_source_path(
            CHECKPOINT_PATH).is_file(),
    }


def config_adverse_control() -> Dict[str, Any]:
    baseline = process_offline(as_float(FIXTURE_COMPONENTS["noisy"]))
    baseline_digest = sha256(canonical_bytes(
        [repr(value) for value in baseline["matched"]]))
    cases = {
        "extra_field": dict(CONFIG, extra=True),
        "missing_field": {k: v for k, v in CONFIG.items() if k != "variant"},
        "sample_rate": dict(CONFIG, sample_rate_hz=48000),
        "channels": dict(CONFIG, channels=2),
        "frame": dict(CONFIG, frame_samples=256),
        "streaming_execution": dict(CONFIG, execution="streaming"),
        "clean_reference": dict(CONFIG, rms_match_reference="clean_input"),
        "frame_scope": dict(CONFIG, rms_match_scope="frame"),
        "raw_variant": dict(CONFIG, variant="one-step"),
        "real_runtime": dict(CONFIG, real_runtime=True),
        "model_used": dict(CONFIG, model_used=True),
    }
    rejected = 0
    for value in cases.values():
        try:
            validate_config(value)
        except ValueError:
            rejected += 1
    return {
        "baseline_digest": baseline_digest,
        "rejected_all": rejected == len(cases),
        "rejections": {name: "rejected" for name in cases},
    }


def shape_control() -> Dict[str, Any]:
    good = as_float(FIXTURE_COMPONENTS["noisy"])
    bad = {
        "empty": [],
        "not_sequence": "samples",
        "nan": good[:64] + [math.nan] + good[65:],
        "infinity": good[:64] + [math.inf] + good[65:],
        "boolean": good[:64] + [True] + good[65:],
        "out_of_range": good[:64] + [1.5] + good[65:],
    }
    rejected = 0
    for value in bad.values():
        try:
            validate_clip(value)
        except ValueError:
            rejected += 1
    match_rejected = 0
    midpoint = TOTAL_SAMPLES // 2
    for enhanced, reference in (
            (good[:64], good),
            ([0.0] * 64, good[midpoint:midpoint + 64]),
            ([math.nan] * 64, good[midpoint:midpoint + 64])):
        try:
            rms_match(enhanced, reference)
        except ValueError:
            match_rejected += 1
    return {
        "clip_rejected_all": rejected == len(bad),
        "clip_rejections": {name: "rejected" for name in bad},
        "rms_match_rejected_all": match_rejected == 3,
        "rms_match_rejections": {
            "length_mismatch": "rejected",
            "zero_enhanced": "rejected",
            "nonfinite_enhanced": "rejected",
        },
    }


def silence_control() -> Dict[str, Any]:
    silence = [0.0] * (FRAME_SAMPLES * 4)
    result = process_offline(silence)
    return {
        "exact_zero": all(value == 0.0 for value in result["matched"]),
        "gain_defined": result["matched_defined"],
        "length": len(result["matched"]),
        "policy": "zero_reference_returns_zero_output",
    }


def invariance_control() -> Dict[str, Any]:
    clean = as_float(FIXTURE_COMPONENTS["clean"])
    noisy = as_float(FIXTURE_COMPONENTS["noisy"])
    run = process_offline(noisy)
    raw_si_sdr = si_sdr(run["raw"], clean)
    matched_si_sdr = si_sdr(run["matched"], clean)
    reference_rms = rms(noisy)
    matched_rms = rms(run["matched"])
    return {
        "correlation_matched_raw": _metric(correlation(run["matched"],
                                                       run["raw"])),
        "gain": _metric(run["gain"]),
        "gain_matches_rms_ratio": run["gain"] == reference_rms / rms(run["raw"]),
        "matched_rms_equals_noisy_rms": abs(matched_rms - reference_rms) <= \
            1e-12 * max(1.0, reference_rms),
        "reference_rms": _metric(reference_rms),
        "matched_rms": _metric(matched_rms),
        "si_sdr_delta_db": _metric(matched_si_sdr - raw_si_sdr),
        "si_sdr_invariant": abs(matched_si_sdr - raw_si_sdr) < 1e-9,
    }


def whole_clip_scope_control() -> Dict[str, Any]:
    noisy = as_float(FIXTURE_COMPONENTS["noisy"])
    full = process_offline(noisy)
    prefix = noisy[:TOTAL_SAMPLES // 2]
    half = process_offline(prefix)
    return {
        "full_gain": _metric(full["gain"]),
        "prefix_gain": _metric(half["gain"]),
        "gains_differ": full["gain"] != half["gain"],
        "prefix_matches_full": half["matched"] == full["matched"][:len(prefix)],
        "streaming_capable": False,
        "whole_clip_only": True,
    }


def scale_restoration_control() -> Dict[str, Any]:
    """Injected -12 dB scale control for the post-processor, not a model result."""
    noisy = as_float(FIXTURE_COMPONENTS["noisy"])
    raw = process_offline(noisy)["raw"]
    injected_gain = 0.251188643150958
    attenuated = [injected_gain * value for value in raw]
    matched = rms_match(attenuated, noisy)
    applied = rms(matched["matched"]) / rms(attenuated)
    return {
        "attenuation_gain_db": _metric(20.0 * math.log10(injected_gain)),
        "applied_gain_db": _metric(20.0 * math.log10(applied)),
        "restored_rms_equals_noisy_rms": abs(
            rms(matched["matched"]) - rms(noisy)) <= 1e-12 * max(1.0, rms(noisy)),
        "si_sdr_preserved": abs(
            (si_sdr(matched["matched"], noisy) or 0.0) -
            (si_sdr(attenuated, noisy) or 0.0)) < 1e-9,
        "label": "injected_scale_control_not_a_model_result",
    }


def determinism_control() -> Dict[str, Any]:
    noisy = as_float(FIXTURE_COMPONENTS["noisy"])
    digests = []
    for _ in range(3):
        run = process_offline(noisy)
        digests.append(sha256(canonical_bytes(
            [repr(value) for value in run["matched"]])))
    return {
        "digests": digests,
        "identical": len(set(digests)) == 1,
        "runs": len(digests),
    }


# ---------------------------------------------------------------------------
# Report and contract builders
# ---------------------------------------------------------------------------


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "mapped_cases": [
            "identity / noisy control on the same frozen clip",
            "raw surrogate enhancer as the task-linked baseline",
            "whole-clip noisy-input RMS matching as the second stage",
            "paired SI-SDR and SNR against the synthetic clean reference",
            "clean-speech waveform preservation under positive gain",
            "peak, clipping, silence and nonfinite-output checks",
            "whole-clip scope and explicit non-streaming conclusion",
            "fail-closed caller-asset, config, shape and nonfinite controls",
            "deterministic three-run regeneration of the matched output",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no exact ROSE-CD checkpoint or runtime, so no ROSE-CD output is "
            "reproduced",
            "no real corpus or clean reference, so no quality or generalization "
            "claim is made",
            "STOI is not implemented here; no intelligibility number is reported",
            "no target device, so no timing, memory or deadline result is "
            "claimed",
            "no independent listening, ASR or intrusive perceptual score is "
            "performed",
        ],
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    }


def _report_body() -> Dict[str, Any]:
    components = FIXTURE_COMPONENTS
    clean = as_float(components["clean"])
    noisy = as_float(components["noisy"])
    run = process_offline(noisy)
    metrics = metric_block(clean, noisy, run)
    contract_payload_value = contract_payload()
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:checkpoint": {
                "byte_count": CHECKPOINT_BYTES,
                "executed": False,
                "expected_path": CHECKPOINT_PATH,
                "filename": CHECKPOINT_FILENAME,
                "huggingface_path": CHECKPOINT_HF_PATH,
                "loaded": False,
                "present": resolve_source_path(CHECKPOINT_PATH).is_file(),
                "revision": CHECKPOINT_REVISION,
                "sha256": CHECKPOINT_SHA256,
            },
            "asset:runtime": {
                "admitted": False,
                "declaration": RUNTIME_DECLARATION,
                "executed": False,
                "expected_path": RUNTIME_ENV_PATH,
                "present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
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
            "determinism": determinism_control(),
            "invariance": invariance_control(),
            "scale_restoration": scale_restoration_control(),
            "shape": shape_control(),
            "silence": silence_control(),
            "whole_clip_scope": whole_clip_scope_control(),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "fixture": {
            "component_digests": dict(FIXTURE_DIGESTS),
            "fixture_id": fixture_spec()["fixture_id"],
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
            "exact ROSE-CD one-step inference output",
            "approved exact RMS-matching recipe",
            "rights-cleared real paired cohort",
            "independent intrusive score, STOI or permitted listening",
            "target-device timing, memory and deadline",
            "opt-in provider intake and default decision",
        ],
        "no_missing_result_qualifies_candidate": True,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the pinned checkpoint and a hash-pinned Python 3.11 "
            "PyTorch runtime, clear artifact and data rights, approve the exact "
            "whole-clip RMS-matching recipe, reproduce exact-runtime outputs, "
            "score a rights-cleared paired cohort independently, measure "
            "target timing and complete opt-in provider intake. Until then the "
            "candidate stays DEFER, incomplete and not qualified."),
        "rms_match": {
            "contract": dict(RMS_MATCH_CONTRACT),
            "gain": _metric(run["gain"]),
            "matched_defined": run["matched_defined"],
            "matched_rms": metrics["rms_matched_surrogate"]["rms"],
            "raw_rms": metrics["raw_surrogate"]["rms"],
            "reference_rms": metrics["identity"]["rms"],
            "peak_after_match": metrics["rms_matched_surrogate"]["peak"],
            "implicit_peak_clamp": False,
        },
        "schema_id": SCHEMA_ID,
        "status": STATUS,
        "surrogate": {
            "frame_gains_digest": sha256(canonical_bytes(
                [repr(value) for value in run["frame_gains"]])),
            "is_rose_cd": False,
            "model_free": True,
            "noise_floor_rms": _metric(run["noise_floor_rms"]),
            "type": "fixed whole-clip per-frame Wiener-amplitude gate",
        },
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "checkpoint_huggingface_path": CHECKPOINT_HF_PATH,
            "checkpoint_revision": CHECKPOINT_REVISION,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "commit": UPSTREAM_COMMIT,
            "license": UPSTREAM_LICENSE,
            "repository": UPSTREAM_REPOSITORY,
            "source_present": resolve_source_path(
                SOURCE_CHECKOUT_PATH + "/.git").exists(),
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
            "RMS matching is whole-clip and is never described as streaming",
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
            "artifact and data rights, approve the RMS-matching recipe, "
            "reproduce exact outputs, score a rights-cleared cohort "
            "independently, measure target timing and complete opt-in provider "
            "intake."),
        "reviewer": REVIEWER,
        "rms_match_contract": dict(RMS_MATCH_CONTRACT),
        "schema_id": CONTRACT_SCHEMA_ID,
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "checkpoint_filename": CHECKPOINT_FILENAME,
            "checkpoint_path": CHECKPOINT_PATH,
            "checkpoint_revision": CHECKPOINT_REVISION,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "commit": UPSTREAM_COMMIT,
            "license": UPSTREAM_LICENSE,
            "repository": UPSTREAM_REPOSITORY,
            "runtime_env_path": RUNTIME_ENV_PATH,
            "source_checkout_path": SOURCE_CHECKOUT_PATH,
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
        "# Full mutable plan/swarm/TASKS.json is never hashed; only "
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
        "asset:checkpoint": CHECKPOINT_SHA256,
        "asset:runtime_identity": sha256(
            canonical_bytes({"declaration": RUNTIME_DECLARATION,
                             "path": RUNTIME_ENV_PATH})),
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
                    "asset:checkpoint": CHECKPOINT_SHA256,
                    "asset:runtime_identity": sha256(canonical_bytes(
                        {"declaration": RUNTIME_DECLARATION,
                         "path": RUNTIME_ENV_PATH})),
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
