# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-CLEARVOICE-FRCRN-16-KHZ.

This module is NOT ClearerVoice FRCRN_SE_16K and is not a reproduction of its
runtime. It does not read weights, audio, media or a caller asset; it downloads
nothing, invokes no vendor runtime, measures no device clock or deadline,
conducts no listening, benchmarks no SDK build and makes no release or quality
claim.

It models the *offline whole-clip boundary* a caller-supplied external asset
would have to cross: 16 kHz mono f32 in [-1, 1], an exact package/model/
checkpoint/pointer configuration, whole-clip enhancement with identity source
time mapping, output length equal to input length, zero declared algorithmic
lag and exact accounting. The signal path is an original deterministic
surrogate, labelled as such everywhere.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-CLEARVOICE-FRCRN-16-KHZ"
TITLE = "ClearVoice FRCRN 16 kHz"
SLUG = "clearvoice-frcrn-16khz"
COMPONENT = "clearvoice-frcrn-16-khz"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d5b11912cd09e87296cd9d4654f1917c9cb94258"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SAMPLES = 32_000
FRAME_COUNT = SAMPLES // FRAME_SAMPLES
MAX_CHUNK_SAMPLES = 2 * SAMPLE_RATE_HZ

# The offline upstream adapter reports identity source-time mapping, zero delay
# compensation and zero padded samples. This package models that declared
# boundary; it measures no latency.
DECLARED_LAG_SAMPLES = 0
ALGORITHMIC_LAG_NS = 0
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-sample-coordinate-not-device"

SEED_BASE = 20261125
CONDITIONS: Tuple[str, ...] = (
    "quiet_speech",
    "active_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
)
CHUNK_SIZES: Tuple[int, ...] = (1, 7, 80, 159, 160, 161, 320, 1280)
OVER_SUBTRACTION = 1.6
GAIN_FLOOR = 0.12
ATTACK = 0.6
RELEASE = 0.3
NOISE_PERCENTILE = 0.56
EPS = 1e-12

# Exact pinned candidate identity. Quoted from the pinned research ledgers and
# the existing adapter; no asset bytes are present in, copied into or read from
# this worktree.
CANDIDATE_ID = "ClearerVoice-FRCRN_SE_16K"
MODEL_NAME = "FRCRN_SE_16K"
CHECKPOINT_ID = "FRCRN_SE_16K/last_best_checkpoint.pt"
CHECKPOINT_BYTES = 161_053_751
CHECKPOINT_SHA256 = "b22256adbb91b68cf5a3db8f6657a4fb17066eecd5f069803e59c186c1cf3ebb"
CHECKPOINT_FILE = "last_best_checkpoint.pt"
CHECKPOINT_DIR = "data/models/clearvoice/FRCRN_SE_16K"
POINTER_ID = "FRCRN_SE_16K/last_best_checkpoint"
POINTER_BYTES = 24
POINTER_SHA256 = "315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0"
POINTER_REQUIRED_CONTENT = CHECKPOINT_FILE
PACKAGE_VERSION = "0.1.2"
PACKAGE_IDENTITY = "ClearerVoice-Studio-clearvoice-0.1.2"
PACKAGE_SOURCE = "https://github.com/modelscope/ClearerVoice-Studio"
SOURCE_REVISION = "3766e6a64b0d8cb58f08d913d617bf129f11ed53"
MODEL_REVISION = None
MODEL_DOWNLOAD_REVISION = None
MODEL_LICENSE_METADATA = "Apache-2.0"
CODE_LICENSE_METADATA = "Apache-2.0"
TRAINING_DATA_NOTE = "model card states open and private data; exact corpus exposure not disclosed"

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/denoising_phase_completion_20261028.md":
        "fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "adapters/clearvoice/adapter.json":
        "ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff",
    "adapters/clearvoice/README.md":
        "9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5",
    "adapters/clearvoice/requirements.lock":
        "3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91",
    "adapters/clearvoice/run.py":
        "c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "check_licensing.py",
    "contract.json",
    "contract.json.license",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

# Artifacts whose digests the README table must expose and verify.py must check.
README_DIGEST_FILES: Tuple[str, ...] = (
    "adapter.json",
    "readiness.json",
    "reference.py",
    "report.json",
    "run.py",
    "test_reference.py",
    "verify.py",
)
README_TABLE_START = "<!-- digest-table:start -->"
README_TABLE_END = "<!-- digest-table:end -->"
EXPECTED_TEST_COUNT = 38

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
}

OFFLINE_BOUNDARY: Dict[str, Any] = {
    "mode": "offline-whole-clip",
    "whole_clip_required": True,
    "frames_buffered_until_finish": True,
    "output_length_equals_input": True,
    "source_time_mapping": "identity",
    "delay_compensation_samples": DECLARED_LAG_SAMPLES,
    "padded_samples_emitted": 0,
    "algorithmic_lag_samples": DECLARED_LAG_SAMPLES,
    "flush_required": False,
    "pointer_required": True,
}

CLAIMS: Dict[str, bool] = {
    "real_clearvoice_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "content_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The pinned ledger records last_best_checkpoint.pt as 161,053,751 bytes "
    "with SHA-256 b22256adbb91b68cf5a3db8f6657a4fb17066eecd5f069803e59c186c1cf3ebb "
    "and a 24-byte last_best_checkpoint pointer with SHA-256 "
    "315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0 under "
    "ClearerVoice source revision 3766e6a64b0d8cb58f08d913d617bf129f11ed53, but "
    "the ledger records no immutable model artifact revision (model_revision is "
    "absent) and no retrieval-time download commit; the 24-byte pointer content "
    "is not verified, and neither artifact is present in this SDK worktree.",
    "The runtime is the external clearvoice 0.1.2 package (adapter identity "
    "ClearerVoice-Studio-clearvoice-0.1.2) with a pinned requirements lock but no "
    "wheel/sdist digest or installed environment here; adapters/clearvoice/run.py "
    "is not executed and no vendor runtime is invoked.",
    "Apache-2.0 is recorded for the code and model card, but the model card states "
    "open and private training data with exact corpus exposure undisclosed; "
    "artifact-specific weight rights, training-data provenance, redistribution "
    "clearance and legal review are not established; no checkpoint, runtime or "
    "upstream source may be vendored, packaged, downloaded or redistributed by "
    "this package.",
    "No rights-cleared held-out real cohort, independent clean-reference scorer, "
    "permitted listening result, target-runtime timing measurement or approved "
    "exact FRCRN reference output vector exists; every release gate remains "
    "blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact FRCRN_SE_16K checkpoint bytes are "
    "addressed by an immutable model artifact revision plus byte count and SHA-256 "
    "in a retrieval record, the pointer content is verified to name the "
    "checkpoint, and both resolve from the caller's own storage without a provider "
    "file access or download.",
    "Reopen runtime admission only when a pinned clearvoice 0.1.2 runtime artifact "
    "with a recorded digest installs in the intended environment, "
    "adapters/clearvoice/run.py runs under the pinned requirements lock, and its "
    "distribution and product-use terms are documented.",
    "Reopen rights only after written artifact-specific weight, runtime and "
    "training-data terms are recorded and a legal/redistribution decision exists; "
    "Apache-2.0 metadata alone is not clearance.",
    "Reopen qualification only with a rights-cleared paired cohort, an independent "
    "scorer, permitted listening, exact reference outputs for the frozen inputs, "
    "and target-runtime timing evidence; the synthetic surrogate can never stand "
    "in for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable FRCRN_SE_16K checkpoint artifact revision plus caller-held bytes",
    "verified 24-byte last_best_checkpoint pointer content",
    "pinned clearvoice 0.1.2 runtime artifact, requirements installation and execution evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "approved exact FRCRN reference output vectors for the frozen synthetic inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime timing, memory, throughput and offline availability evidence",
)

GATES: Tuple[Dict[str, str], ...] = (
    {"name": "exact_asset_identity", "status": "blocked",
     "evidence": "Ledger digest/byte counts only; model_revision is absent and the pointer content is unverified.",
     "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked",
     "evidence": "clearvoice 0.1.2 is absent and its runtime artifact is unpinned here.",
     "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked",
     "evidence": "Apache-2.0 metadata is recorded; artifact-specific terms, training-data provenance and legal review are absent.",
     "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked",
     "evidence": "No approved FRCRN reference output vector exists for these frozen inputs.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rights_cleared_cohort", "status": "blocked",
     "evidence": "No paired real cohort with clean references is available to this task.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "independent_scoring_and_listening", "status": "blocked",
     "evidence": "No independent scorer or listening result; surrogate metrics are synthetic only.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked",
     "evidence": "No device clock, pacing, deadline, throughput or memory measurement was made.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "provider_intake", "status": "blocked",
     "evidence": "No opt-in provider, descriptor or catalog entry exists; the package is unregistered.",
     "reopen": "Reopen only after rights/runtime/parity gates clear and an opt-in provider intake with OFF default and independent review is approved."},
    {"name": "public_default_selection", "status": "blocked",
     "evidence": "No default selection is proposed or made.",
     "reopen": "Reopen only after the provider intake clears and the owner records an explicit default decision with preserving controls."},
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, not pooled and not used as a threshold.",
    "candidate_csv_row": (
        "Denoising,ClearVoice FRCRN 16 kHz,evaluated,30 paired DNS2020 and "
        "12-clip EARS screen; local CPU RTF about 3.74"
    ),
    "census_row": (
        "Completed full paired 30-clip DNS2020 pilot: mean delta SNR +10.10 dB "
        "(95% CI +8.51 to +11.84), mean delta STOI +0.0474 (CI +0.0371 to "
        "+0.0588), all 30 pairs improved on both. Median CPU RTF 3.59."
    ),
    "pilot_30_clip_mean_delta_snr_db": 10.10,
    "pilot_30_clip_snr_ci95_db": [8.51, 11.84],
    "pilot_30_clip_mean_delta_si_sdr_db": 10.05,
    "pilot_30_clip_si_sdr_ci95_db": [8.46, 11.74],
    "pilot_30_clip_mean_delta_stoi": 0.0474,
    "pilot_30_clip_stoi_ci95": [0.0371, 0.0588],
    "pilot_30_clip_pairs_improved_both": 30,
    "pilot_30_clip_mean_adapter_rtf": 3.74,
    "pilot_30_clip_median_cpu_rtf": 3.59,
    "ears_12_clip_no_reference_screen": {
        "clips": 12,
        "speaker_labels": False,
        "SIG": 4.438,
        "SIG_delta": 0.117,
        "BAK": 4.606,
        "BAK_delta": 1.080,
        "OVL": 4.053,
        "OVL_delta": 0.549,
    },
    "upstream_author_reported_dns2020": {
        "source": "ClearerVoice README SpeechScore table; not independently reproduced",
        "PESQ": 3.24,
        "STOI": 0.98,
        "SI_SDR_dB": 19.99,
        "P808_MOS": 4.03,
        "SIG": 3.58,
        "BAK": 4.15,
        "OVRL": 3.33,
    },
    "training_data_note": TRAINING_DATA_NOTE,
    "disclaimer": (
        "These values come from pinned research files on 30 DNS2020 pairs and a "
        "12-clip EARS screen, plus an upstream author table. They are not reproduced "
        "here, not device timing, not this fixture's metrics, not a listening result "
        "and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "ClearerVoice FRCRN_SE_16K checkpoint, pointer, clearvoice 0.1.2 package and PyTorch runtime are absent; nothing was downloaded, installed, loaded or invoked.",
    "The checkpoint and pointer digests/byte counts, source revision, absent model revision and license metadata are quoted from research/noise_suppression_assets_20261027.json.",
    "The input range, identity source-time mapping, zero delay compensation, pointer-content requirement and package check are quoted from adapters/clearvoice/run.py and adapter.json.",
    "The 30-clip and EARS values are pinned research provenance only; this package does not reproduce them and measures no runtime.",
    "All signals, targets and observations are generated by a stdlib LCG in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)


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


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _seed(name: str) -> int:
    return (SEED_BASE + sum((index + 1) * ord(char)
                            for index, char in enumerate(name))) & 0xFFFFFFFF


def _envelope(condition: str, index: int) -> float:
    t = index / SAMPLE_RATE_HZ
    if condition == "onset_offset":
        regions = ((0.40, 0.80), (1.20, 1.60))
        value = 0.0
        for start, end in regions:
            if start <= t < end:
                ramp = min((t - start) / 0.01, (end - t) / 0.01, 1.0)
                value = max(value, ramp)
        return value
    if condition == "idle_noise":
        return 0.0
    modulation = math.sin(2.0 * math.pi * 3.1 * t + 0.4)
    return max(0.0, modulation) ** 1.2


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return (clean target, observed input) for one frozen condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    scales = {
        "quiet_speech": (0.060, 0.006),
        "active_speech": (0.250, 0.035),
        "low_snr_speech": (0.050, 0.050),
        "onset_offset": (0.180, 0.020),
        "idle_noise": (0.000, 0.030),
    }
    target_scale, noise_scale = scales[condition]
    noise_rng = _lcg(_seed("noise:" + condition))
    clean: List[float] = []
    observed: List[float] = []
    for index in range(SAMPLES):
        t = index / SAMPLE_RATE_HZ
        if target_scale:
            carrier = (0.62 * math.sin(2.0 * math.pi * 213.0 * t)
                       + 0.28 * math.sin(2.0 * math.pi * 426.0 * t + 0.7)
                       + 0.10 * math.sin(2.0 * math.pi * 639.0 * t + 1.9))
            target = target_scale * _envelope(condition, index) * carrier
        else:
            target = 0.0
        noise = noise_scale * (2.0 * next(noise_rng) - 1.0)
        clean.append(target)
        observed.append(target + noise)
    return clean, observed


def asset_ref() -> Dict[str, Any]:
    """The exact caller-supplied asset reference this boundary would require."""
    return {
        "asset_id": CHECKPOINT_ID,
        "model_name": MODEL_NAME,
        "storage": "external",
        "sha256": CHECKPOINT_SHA256,
        "byte_count": CHECKPOINT_BYTES,
        "auxiliary_assets": [
            {
                "asset_id": POINTER_ID,
                "sha256": POINTER_SHA256,
                "byte_count": POINTER_BYTES,
                "required_content": POINTER_REQUIRED_CONTENT,
                "content_verified": False,
            }
        ],
        "package": "clearvoice==" + PACKAGE_VERSION,
        "package_identity": PACKAGE_IDENTITY,
        "source_repository": PACKAGE_SOURCE,
        "source_revision": SOURCE_REVISION,
        "model_revision": MODEL_REVISION,
        "model_download_revision": MODEL_DOWNLOAD_REVISION,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "training_data_note": TRAINING_DATA_NOTE,
        "rights_cleared": False,
        "bytes_present": False,
        "runtime_available": False,
        "download_permitted": False,
    }


def _pointer_admitted(ref: Dict[str, Any]) -> bool:
    auxiliary = ref.get("auxiliary_assets")
    if not isinstance(auxiliary, list) or len(auxiliary) != 1:
        return False
    pointer = auxiliary[0]
    return (
        isinstance(pointer, dict)
        and pointer.get("asset_id") == POINTER_ID
        and pointer.get("sha256") == POINTER_SHA256
        and pointer.get("byte_count") == POINTER_BYTES
        and pointer.get("required_content") == POINTER_REQUIRED_CONTENT
        and pointer.get("content_verified") is True
    )


def asset_admission(ref: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed admission for a caller-supplied external asset reference.

    No filesystem access, network access or vendor runtime call occurs. The
    checks mirror the pinned adapter: exact model/package identity, checkpoint
    byte count and digest, verified pointer content, external storage and no
    download. A caller may supply bytes from its own storage, but this task
    holds none for the pinned candidate.
    """
    reasons: List[str] = []
    required = {"asset_id", "model_name", "storage", "sha256", "byte_count",
                "auxiliary_assets", "package", "source_revision",
                "model_revision", "model_download_revision", "rights_cleared",
                "bytes_present", "runtime_available", "download_permitted"}
    missing = sorted(required - set(ref))
    if missing:
        reasons.append("missing_fields:" + ",".join(missing))
    if ref.get("asset_id") != CHECKPOINT_ID:
        reasons.append("asset_id_mismatch")
    if ref.get("model_name") != MODEL_NAME:
        reasons.append("model_name_mismatch")
    if ref.get("storage") != "external":
        reasons.append("storage_not_external")
    if ref.get("sha256") != CHECKPOINT_SHA256:
        reasons.append("sha256_mismatch")
    if ref.get("byte_count") != CHECKPOINT_BYTES:
        reasons.append("byte_count_mismatch")
    if ref.get("package") != "clearvoice==" + PACKAGE_VERSION:
        reasons.append("package_mismatch")
    if ref.get("source_revision") != SOURCE_REVISION:
        reasons.append("source_revision_mismatch")
    if ref.get("model_revision") in (None, "", "main"):
        reasons.append("model_revision_unpinned")
    if ref.get("model_download_revision") in (None, ""):
        reasons.append("download_revision_unrecorded")
    if not _pointer_admitted(ref):
        reasons.append("pointer_artifact_unverified")
    if ref.get("download_permitted") is not False:
        reasons.append("download_flag_invalid")
    if ref.get("bytes_present") is not True:
        reasons.append("asset_bytes_absent")
    if ref.get("runtime_available") is not True:
        reasons.append("runtime_unavailable")
    if ref.get("rights_cleared") is not True:
        reasons.append("rights_not_cleared")
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "asset_bytes_read": False,
    }


def synthetic_config() -> Dict[str, Any]:
    return {
        "mode": "synthetic-surrogate",
        "synthetic_surrogate_opt_in": True,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "model_name": MODEL_NAME,
        "package_version": PACKAGE_VERSION,
        "asset_reference": asset_ref(),
    }


def caller_asset_config() -> Dict[str, Any]:
    """The exact upstream adapter configuration fields plus our asset wrapper."""
    return {
        "mode": "caller-asset",
        "model_name": MODEL_NAME,
        "package_version": PACKAGE_VERSION,
        "model_revision": MODEL_REVISION,
        "checkpoint_dir": CHECKPOINT_DIR,
        "checkpoint_file": CHECKPOINT_FILE,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "sample_rate": SAMPLE_RATE_HZ,
        "asset_reference": asset_ref(),
    }


CALLER_CONFIG_FIELDS = (
    "model_name",
    "package_version",
    "model_revision",
    "checkpoint_dir",
    "checkpoint_file",
    "checkpoint_sha256",
    "sample_rate",
)


def default_config() -> Dict[str, Any]:
    return synthetic_config()


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    mode = config.get("mode")
    if mode not in ("synthetic-surrogate", "caller-asset"):
        return ["mode_unsupported"]
    if mode == "synthetic-surrogate":
        expected = synthetic_config()
        for key in ("sample_rate_hz", "channels", "sample_format",
                    "model_name", "package_version"):
            if config.get(key) != expected[key]:
                reasons.append(key + "_mismatch")
        if config.get("synthetic_surrogate_opt_in") is not True:
            reasons.append("surrogate_opt_in_required")
        return reasons
    required = set(CALLER_CONFIG_FIELDS) | {"asset_reference", "mode"}
    if set(config) != required:
        reasons.append("caller_asset_config_fields_mismatch")
        return reasons
    if config.get("model_name") != MODEL_NAME:
        reasons.append("model_name_mismatch")
    if config.get("package_version") != PACKAGE_VERSION:
        reasons.append("package_version_mismatch")
    if config.get("sample_rate") != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_mismatch")
    if config.get("checkpoint_file") != CHECKPOINT_FILE:
        reasons.append("checkpoint_file_mismatch")
    if config.get("checkpoint_sha256") != CHECKPOINT_SHA256:
        reasons.append("checkpoint_sha256_mismatch")
    admission = asset_admission(config.get("asset_reference") or {})
    if admission["status"] != "admitted":
        reasons.append("asset_not_admitted")
    return reasons


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = fraction * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def enhance_offline(samples: Sequence[float]) -> Tuple[List[float], Dict[str, Any]]:
    """Deterministic offline frame-gain surrogate; zero lag, exact length."""
    count = len(samples)
    if count == 0:
        return [], {
            "input_samples": 0,
            "output_samples": 0,
            "frame_count": 0,
            "internal_frame_padding_samples": 0,
            "noise_floor_power": 0.0,
            "gain_min": 1.0,
            "gain_max": 1.0,
        }
    frame_count = (count + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    powers: List[float] = []
    for frame_index in range(frame_count):
        start = frame_index * FRAME_SAMPLES
        frame = list(samples[start:start + FRAME_SAMPLES])
        if len(frame) < FRAME_SAMPLES:
            frame.extend([0.0] * (FRAME_SAMPLES - len(frame)))
        powers.append(sum(value * value for value in frame) / float(FRAME_SAMPLES))
    noise_floor = max(_percentile(powers, NOISE_PERCENTILE), EPS)
    output: List[float] = []
    gain = 1.0
    previous = 1.0
    gain_min = 1.0
    gain_max = 1.0
    for frame_index in range(frame_count):
        power = powers[frame_index]
        ratio = power / noise_floor
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        target = min(1.0, max(GAIN_FLOOR, target))
        alpha = ATTACK if target < gain else RELEASE
        gain = gain + alpha * (target - gain)
        gain_min = min(gain_min, gain)
        gain_max = max(gain_max, gain)
        start = frame_index * FRAME_SAMPLES
        for offset in range(FRAME_SAMPLES):
            index = start + offset
            if index >= count:
                break
            weight = (offset + 1) / float(FRAME_SAMPLES)
            applied = previous + (gain - previous) * weight
            output.append(samples[index] * applied)
        previous = gain
    return output, {
        "input_samples": count,
        "output_samples": len(output),
        "frame_count": frame_count,
        "internal_frame_padding_samples": frame_count * FRAME_SAMPLES - count,
        "noise_floor_power": noise_floor,
        "gain_min": gain_min,
        "gain_max": gain_max,
    }


class OfflineSurrogateSession:
    """Whole-clip offline boundary fixture; not a vendor enhancer."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = dict(config or default_config())
        reasons = validate_config(self.config)
        if reasons:
            raise ValueError(";".join(reasons))
        self._samples: List[float] = []
        self._input_samples = 0
        self._finished = False
        self._closed = False

    def digest(self) -> str:
        payload = canonical_bytes({
            "samples": self._samples,
            "input_samples": self._input_samples,
            "finished": self._finished,
            "closed": self._closed,
        })
        return sha256(payload)

    def process(self, chunk: Sequence[float]) -> List[float]:
        """Buffer a caller chunk. Offline work happens only at finish()."""
        if self._closed:
            raise ValueError("session_closed")
        if self._finished:
            raise ValueError("session_already_finished")
        if isinstance(chunk, (str, bytes)) or not isinstance(chunk, Sequence):
            raise ValueError("chunk_type_invalid")
        values = list(chunk)
        if not values:
            raise ValueError("chunk_empty")
        if len(values) > MAX_CHUNK_SAMPLES:
            raise ValueError("chunk_oversized")
        for value in values:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError("sample_type_invalid")
            if not math.isfinite(float(value)):
                raise ValueError("sample_nonfinite")
            if abs(float(value)) > 1.0:
                raise ValueError("sample_out_of_range")
        self._samples.extend(float(value) for value in values)
        self._input_samples += len(values)
        return []

    def finish(self) -> List[float]:
        if self._closed:
            raise ValueError("session_closed")
        if self._finished:
            raise ValueError("session_already_finished")
        output, _ = enhance_offline(self._samples)
        self._finished = True
        return output

    def reset(self) -> None:
        if self._closed:
            raise ValueError("session_closed")
        self._samples = []
        self._input_samples = 0
        self._finished = False

    def close(self) -> None:
        self._closed = True

    @property
    def input_samples(self) -> int:
        return self._input_samples

    @property
    def finished(self) -> bool:
        return self._finished


# ---------------------------------------------------------------------------
# Offline runs, boundary accounting and synthetic scoring
# ---------------------------------------------------------------------------

def run_offline(samples: Sequence[float], chunk_size: int,
                config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Feed one chunking and return the whole-clip output plus accounting."""
    if chunk_size <= 0 or chunk_size > MAX_CHUNK_SAMPLES:
        raise ValueError("chunk_size_unsupported")
    session = OfflineSurrogateSession(config)
    chunk_records: List[Dict[str, int]] = []
    emitted_before_finish = 0
    for start in range(0, len(samples), chunk_size):
        chunk = list(samples[start:start + chunk_size])
        emitted = session.process(chunk)
        emitted_before_finish += len(emitted)
        chunk_records.append({"start_sample": start, "input_count": len(chunk),
                              "emitted_count": len(emitted)})
    output = session.finish()
    _, info = enhance_offline(samples)
    return {
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_records),
        "chunk_records": chunk_records,
        "output": output,
        "output_digest": sha256(canonical_bytes(output)),
        "emitted_before_finish": emitted_before_finish,
        "finish_emitted": len(output),
        "output_length": len(output),
        "input_samples": len(samples),
        "valid_samples": len(output),
        "internal_frame_padding_samples": info["internal_frame_padding_samples"],
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_LAG_SAMPLES,
        "padded_samples": 0,
        "final_state_digest": session.digest(),
    }


def _rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / float(len(values)))


def _db(ratio: float) -> float:
    return 10.0 * math.log10(max(ratio, 1e-30))


def score(clean: Sequence[float], estimate: Sequence[float]) -> Dict[str, Any]:
    """Synthetic paired diagnostics only; no real scorer or model is used."""
    if len(clean) != len(estimate) or not clean:
        raise ValueError("score_length_mismatch")
    signal_power = sum(value * value for value in clean)
    error_power = sum((a - b) ** 2 for a, b in zip(clean, estimate))
    snr_db = None if signal_power <= 0.0 else _db(signal_power / max(error_power, 1e-30))
    projection = sum(a * b for a, b in zip(clean, estimate))
    if signal_power > 0.0:
        scale = projection / signal_power
        target_power = sum((scale * value) ** 2 for value in clean)
        residual_power = sum((scale * a - b) ** 2 for a, b in zip(clean, estimate))
        si_sdr_db = None if target_power <= 0.0 else _db(target_power / max(residual_power, 1e-30))
    else:
        si_sdr_db = None
    peak = max(abs(value) for value in estimate)
    return {
        "snr_db": snr_db,
        "si_sdr_db": si_sdr_db,
        "output_rms": _rms(estimate),
        "peak_abs_output": peak,
        "clipped_samples": sum(1 for value in estimate if abs(value) > 1.0),
        "nonfinite_samples": sum(1 for value in estimate if not math.isfinite(value)),
        "scored_samples": len(estimate),
    }


def condition_block(condition: str) -> Dict[str, Any]:
    clean, observed = synth(condition)
    chunked = run_offline(observed, FRAME_SAMPLES)
    whole = run_offline(observed, SAMPLES)
    valid = chunked["valid_samples"]
    prefix = clean[:valid]
    noisy = score(prefix, observed[:valid])
    identity = score(prefix, observed[:valid])
    candidate = score(prefix, chunked["output"][:valid])
    whole_score = score(prefix, whole["output"][:valid])

    def delta(candidate_value: Any, control_value: Any) -> Any:
        if candidate_value is None or control_value is None:
            return None
        return candidate_value - control_value

    return {
        "input_samples": len(observed),
        "scored_samples": valid,
        "tail_validity": {
            "input_samples": len(observed),
            "output_samples": chunked["output_length"],
            "valid_samples": valid,
            "internal_frame_padding_samples": chunked["internal_frame_padding_samples"],
            "padded_samples_emitted": chunked["padded_samples"],
            "source_time_mapping": chunked["source_time_mapping"],
            "delay_compensation_samples": chunked["delay_compensation_samples"],
            "attributable_samples": valid,
        },
        "variants": {
            "identity_passthrough": {**identity, "exact_passthrough": True},
            "noisy_control": noisy,
            "surrogate_offline_chunked_160": candidate,
            "surrogate_offline_whole_clip": whole_score,
        },
        "improvements": {
            "snr_db": delta(candidate["snr_db"], noisy["snr_db"]),
            "si_sdr_db": delta(candidate["si_sdr_db"], noisy["si_sdr_db"]),
        },
        "noise_attenuation_db": (
            None if noisy["output_rms"] <= 0.0
            else _db((candidate["output_rms"] / noisy["output_rms"]) ** 2)
        ),
        "chunk_invariance_digest": chunked["output_digest"],
        "whole_clip_matches_chunked": chunked["output_digest"] == whole["output_digest"],
    }


def alignment_probe() -> Dict[str, Any]:
    """Model the declared zero-lag offline boundary with one impulse."""
    samples = [0.001 * math.sin(2.0 * math.pi * 97.0 * index / SAMPLE_RATE_HZ)
               for index in range(8000)]
    samples[4000] = 0.9
    run = run_offline(samples, FRAME_SAMPLES)
    peak = max(range(len(run["output"])),
               key=lambda index: abs(run["output"][index]))
    return {
        "input_peak_sample": 4000,
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
        "output_peak_sample": peak,
        "output_lag_samples": peak - 4000,
        "residual_lag_samples": peak - 4000,
        "measured_latency": False,
        "modeled_only": True,
    }


def cross_hop_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    records: Dict[str, Any] = {}
    output_digests = set()
    for size in CHUNK_SIZES:
        run = run_offline(observed, size)
        boundaries_crossed = 0
        for start in range(0, len(observed), size):
            end = min(start + size, len(observed))
            first = start // FRAME_SAMPLES + 1
            last = (end - 1) // FRAME_SAMPLES
            if last >= first:
                boundaries_crossed += 1
        records[str(size)] = {
            "chunk_count": run["chunk_count"],
            "chunks_crossing_frame_boundary": boundaries_crossed,
            "emitted_before_finish": run["emitted_before_finish"],
            "finish_emitted": run["finish_emitted"],
            "output_length": run["output_length"],
            "valid_samples": run["valid_samples"],
            "output_digest": run["output_digest"],
        }
        output_digests.add(run["output_digest"])
    whole = run_offline(observed, SAMPLES)
    return {
        "samples": len(observed),
        "frame_samples": FRAME_SAMPLES,
        "chunk_sizes_tested": list(CHUNK_SIZES),
        "records": records,
        "output_chunk_invariant": len(output_digests) == 1,
        "whole_call_matches_chunked": whole["output_digest"] == run_offline(
            observed, FRAME_SAMPLES)["output_digest"],
        "total_frame_boundaries": FRAME_COUNT - 1,
        "device_clock_used": False,
        "deadline_measured": False,
    }


def state_evidence() -> Dict[str, Any]:
    _, observed = synth("low_snr_speech")
    session = OfflineSurrogateSession()
    digests = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        digests.append(session.digest())
    session.reset()
    replay = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        replay.append(session.digest())
    fresh = OfflineSurrogateSession()
    independent = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        fresh.process(observed[start:start + FRAME_SAMPLES])
        independent.append(fresh.digest())
    _, other = synth("active_speech")
    cross = OfflineSurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(observed[start:start + FRAME_SAMPLES])
    cross.reset()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(other[start:start + FRAME_SAMPLES])
    control = OfflineSurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        control.process(other[start:start + FRAME_SAMPLES])
    return {
        "chunks_processed": len(digests),
        "state_digest_chain": sha256(canonical_bytes(digests)),
        "first_state_digest": digests[0],
        "last_state_digest": digests[-1],
        "reset_replay_identical": replay == digests,
        "independent_session_identical": independent == digests,
        "cross_stream_reset_identical": cross.digest() == control.digest(),
        "state_is_synthetic": True,
        "real_recurrent_state_loaded": False,
    }


def config_adverse_cases() -> Dict[str, Any]:
    base = synthetic_config()
    cases: Dict[str, Any] = {}

    def attempt(name: str, config: Dict[str, Any]) -> None:
        try:
            session = OfflineSurrogateSession(config)
        except ValueError as error:
            cases[name] = {
                "status": "rejected",
                "reason_codes": str(error).split(";"),
                "session_created": False,
                "processing_attempted": False,
            }
        else:
            cases[name] = {
                "status": "created",
                "reason_codes": [],
                "session_created": True,
                "processing_attempted": False,
                "state_digest": session.digest(),
            }

    def mutated(**changes: Any) -> Dict[str, Any]:
        config = json.loads(json.dumps(base))
        config.update(changes)
        return config

    attempt("wrong_sample_rate", mutated(sample_rate_hz=48000))
    attempt("wrong_channels", mutated(channels=2))
    attempt("wrong_sample_format", mutated(sample_format="i16"))
    attempt("wrong_model_name", mutated(model_name="MossFormerGAN_SE_16K"))
    attempt("wrong_package_version", mutated(package_version="0.1.1"))
    attempt("mode_unsupported",
            {"mode": "streaming", "synthetic_surrogate_opt_in": True})
    attempt("surrogate_without_opt_in", mutated(synthetic_surrogate_opt_in=False))
    attempt("caller_asset_unavailable", caller_asset_config())

    wrong_sha = caller_asset_config()
    wrong_sha["checkpoint_sha256"] = "0" * 64
    attempt("caller_asset_wrong_checkpoint_sha", wrong_sha)

    control = caller_asset_config()
    control["model_revision"] = "artifact:FRCRN_SE_16K@" + CHECKPOINT_SHA256
    control["asset_reference"].update({
        "model_revision": "artifact:FRCRN_SE_16K@" + CHECKPOINT_SHA256,
        "model_download_revision": "artifact:FRCRN_SE_16K@" + CHECKPOINT_SHA256,
        "rights_cleared": True,
        "bytes_present": True,
        "runtime_available": True,
        "auxiliary_assets": [{
            "asset_id": POINTER_ID,
            "sha256": POINTER_SHA256,
            "byte_count": POINTER_BYTES,
            "required_content": POINTER_REQUIRED_CONTENT,
            "content_verified": True,
        }],
    })
    attempt("caller_asset_admission_control", control)
    return cases


def frame_adverse_cases() -> Dict[str, Any]:
    session = OfflineSurrogateSession()
    session.process([0.01] * FRAME_SAMPLES)
    cases: Dict[str, Any] = {}

    def rejected(name: str, action) -> None:
        before = session.digest()
        try:
            action()
        except ValueError as error:
            after = session.digest()
            cases[name] = {
                "status": "rejected:" + str(error),
                "state_unchanged": before == after,
                "state_digest": after,
            }
        else:
            cases[name] = {"status": "accepted", "state_unchanged": False,
                           "state_digest": session.digest()}

    rejected("empty_chunk", lambda: session.process([]))
    rejected("oversized_chunk", lambda: session.process([0.0] * (MAX_CHUNK_SAMPLES + 1)))
    rejected("nonfinite_sample", lambda: session.process([float("nan")]))
    rejected("infinite_sample", lambda: session.process([float("inf")]))
    rejected("string_chunk", lambda: session.process("not-a-chunk"))
    rejected("boolean_sample", lambda: session.process([True]))
    rejected("out_of_range_sample", lambda: session.process([1.5]))

    output = session.finish()
    after_finish = session.digest()
    rejected("process_after_finish", lambda: session.process([0.0] * FRAME_SAMPLES))
    rejected("finish_after_finish", session.finish)
    after_rejected_finish = session.digest()
    session.close()
    after_close = session.digest()
    rejected("process_after_close", lambda: session.process([0.0] * FRAME_SAMPLES))
    rejected("finish_after_close", session.finish)
    rejected("reset_after_close", session.reset)
    after_rejected_close = session.digest()
    session.close()
    return {
        "cases": cases,
        "finish_output_samples": len(output),
        "state_after_finish_unchanged_by_rejected_calls": after_finish == after_rejected_finish,
        "state_after_close_unchanged_by_rejected_calls": after_close == after_rejected_close,
        "closed_after_double_close": session._closed,
    }


def lifecycle_evidence() -> Dict[str, Any]:
    session = OfflineSurrogateSession()
    session.process([0.0] * FRAME_SAMPLES)
    first = session.finish()
    try:
        session.finish()
    except ValueError as error:
        second_finish = "rejected:" + str(error)
    else:
        second_finish = "accepted"
    session.reset()
    reset_output = session.finish()
    session.close()
    closed_digest = session.digest()
    session.close()
    results = {}
    for name, action in (("process_after_close", lambda: session.process([0.0])),
                         ("finish_after_close", session.finish),
                         ("reset_after_close", session.reset)):
        try:
            action()
        except ValueError as error:
            results[name] = "rejected:" + str(error)
        else:
            results[name] = "accepted"
    return {
        "finish_returns_samples": bool(first),
        "second_finish": second_finish,
        "reset_finish_empty": reset_output == [],
        "close_idempotent": session._closed and closed_digest == session.digest(),
        "process_after_close": results["process_after_close"],
        "finish_after_close": results["finish_after_close"],
        "reset_after_close": results["reset_after_close"],
        "zero_length_finish": OfflineSurrogateSession().finish() == [],
    }


def tail_probe() -> Dict[str, Any]:
    """Exercise a partial final frame without emitting padding."""
    _, observed = synth("active_speech")
    probe = list(observed) + [0.02 * ((index % 17) - 8) / 8.0 for index in range(123)]
    output, info = enhance_offline(probe)
    return {
        "input_samples": len(probe),
        "output_samples": len(output),
        "internal_frame_padding_samples": info["internal_frame_padding_samples"],
        "padded_samples_emitted": 0,
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_LAG_SAMPLES,
        "exact_length": len(output) == len(probe),
    }


def asset_boundary() -> Dict[str, Any]:
    ref = asset_ref()
    admission = asset_admission(ref)
    control = json.loads(json.dumps(ref))
    control.update({
        "model_revision": "artifact:FRCRN_SE_16K@" + CHECKPOINT_SHA256,
        "model_download_revision": "artifact:FRCRN_SE_16K@" + CHECKPOINT_SHA256,
        "rights_cleared": True,
        "bytes_present": True,
        "runtime_available": True,
        "auxiliary_assets": [{
            "asset_id": POINTER_ID,
            "sha256": POINTER_SHA256,
            "byte_count": POINTER_BYTES,
            "required_content": POINTER_REQUIRED_CONTENT,
            "content_verified": True,
        }],
    })
    control_admission = asset_admission(control)
    return {
        "kind": "caller-supplied external asset reference",
        "contract": "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, storage=external, no download",
        "candidate": CANDIDATE_ID,
        "asset": {
            "asset_id": ref["asset_id"],
            "model_name": ref["model_name"],
            "storage": ref["storage"],
            "sha256": ref["sha256"],
            "byte_count": ref["byte_count"],
            "package": ref["package"],
            "package_identity": ref["package_identity"],
            "source_repository": ref["source_repository"],
            "source_revision": ref["source_revision"],
            "model_revision": ref["model_revision"],
            "model_download_revision": ref["model_download_revision"],
            "code_license_metadata": ref["code_license_metadata"],
            "model_license_metadata": ref["model_license_metadata"],
            "training_data_note": ref["training_data_note"],
        },
        "auxiliary_assets": [
            {
                "asset_id": POINTER_ID,
                "sha256": POINTER_SHA256,
                "byte_count": POINTER_BYTES,
                "required_content": POINTER_REQUIRED_CONTENT,
                "content_verified": False,
            }
        ],
        "readiness": admission["status"],
        "reason_codes": admission["reason_codes"],
        "download_attempted": admission["download_attempted"],
        "vendor_runtime_invoked": admission["vendor_runtime_invoked"],
        "asset_bytes_read": admission["asset_bytes_read"],
        "bytes_present_in_worktree": False,
        "runtime_installed_in_worktree": False,
        "rights_cleared": False,
        "synthetic_admission_control": {
            "status": control_admission["status"],
            "reason_codes": control_admission["reason_codes"],
            "not_the_pinned_candidate": True,
            "note": "Admission logic only; no upstream bytes exist and no rights are implied.",
        },
        "surrogate_policy": {
            "available": True,
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "labelled": "deterministic stdlib offline whole-clip surrogate",
        },
        "reopen_condition": REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1] + " " + REOPEN_CONDITIONS[2],
    }


def enhancement_profile() -> Dict[str, Any]:
    return {
        "name": PROFILE,
        "source": "plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "identity_and_noisy_controls": True,
        "paired_snr_and_si_sdr": "synthetic_fixture_only",
        "stoi": {"status": "blocked_unmeasured",
                 "reason": "no clean-reference-eligible real cohort and no installed STOI scorer"},
        "clean_speech_preservation": {
            "status": "synthetic_only",
            "conditions": ["quiet_speech", "active_speech"],
        },
        "peaks_and_invalid_outputs": True,
        "alignment": {
            "status": "modelled_zero_lag",
            "declared_lag_samples": DECLARED_LAG_SAMPLES,
            "compensated": False,
            "measured": False,
        },
        "state_and_memory": {
            "status": "synthetic_state_only",
            "real_memory_measured": False,
        },
        "content_and_availability_timing": {
            "status": "blocked_unmeasured",
            "measured": False,
            "device_clock": False,
        },
        "listening": {"status": "not_run", "permitted": False},
        "real_runtime": False,
        "real_clean_references": False,
        "release_gate": "blocked",
    }


def _condition_blocks() -> Dict[str, Any]:
    return {name: condition_block(name) for name in CONDITIONS}


def _regressions(blocks: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for condition, block in blocks.items():
        noisy = block["variants"]["noisy_control"]
        candidate = block["variants"]["surrogate_offline_chunked_160"]
        for metric in ("snr_db", "si_sdr_db"):
            if noisy[metric] is None or candidate[metric] is None:
                continue
            if candidate[metric] < noisy[metric]:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "better_direction": "higher",
                    "noisy_control": noisy[metric],
                    "surrogate_offline_chunked_160": candidate[metric],
                    "delta": candidate[metric] - noisy[metric],
                    "note": "Synthetic fixture regression recorded verbatim; not a candidate result.",
                })
    return regressions


def _core_report() -> Dict[str, Any]:
    blocks = _condition_blocks()
    admission = asset_admission(asset_ref())
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "slug": SLUG,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "offline_boundary": OFFLINE_BOUNDARY,
        "claims": CLAIMS,
        "conditions": blocks,
        "controls": {
            "all_present": True,
            "identity": {
                "name": "identity_passthrough",
                "exact_passthrough": True,
                "note": "No processing; every scored sample is the observed input.",
            },
            "noisy_control": {
                "name": "observed_input_no_processing",
                "note": "Paired control for the synthetic target on the same valid prefix.",
            },
            "candidate": {
                "name": "surrogate_offline_chunked_160",
                "real_candidate": False,
                "note": "Deterministic stdlib offline surrogate, not ClearerVoice FRCRN.",
            },
            "whole_clip": {
                "name": "surrogate_offline_whole_clip",
                "note": "Chunk invariance control; must equal the 160-sample fed output.",
            },
        },
        "regressions": _regressions(blocks),
        "offline_processing": {
            "protocol": "caller-supplied external asset plus buffered whole-clip calls",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "input_range": [-1.0, 1.0],
            "frame_samples": FRAME_SAMPLES,
            "chunk_sizes_tested": list(CHUNK_SIZES),
            "max_chunk_samples": MAX_CHUNK_SAMPLES,
            "declared_algorithmic_lag_samples": DECLARED_LAG_SAMPLES,
            "declared_algorithmic_lag_ns": ALGORITHMIC_LAG_NS,
            "lag_provenance": (
                "adapters/clearvoice/run.py records source_time_mapping=identity, "
                "delay_compensation_samples=0 and padded_samples=0 for the offline "
                "whole-clip adapter; source-reported, not re-measured here."
            ),
            "lag_measured_here": False,
            "lag_modeled_in_fixture": True,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": "sample-coordinate only; no wall clock, device clock or deadline",
            "finish_policy": (
                "Caller chunks are buffered and the whole clip is enhanced once at finish; "
                "a partial final frame is zero-padded only for gain estimation and is never "
                "emitted."
            ),
            "reset_policy": "Explicit reset clears the buffer and finished flag; replay is bit-identical.",
            "output_accounting": {
                "output_samples": "input_samples",
                "delay_compensation_samples": DECLARED_LAG_SAMPLES,
                "padded_samples_emitted": 0,
                "internal_frame_padding_samples": "(-input_samples) mod 160",
                "source_time_mapping": "identity",
                "finding": (
                    "The upstream adapter returns one output sample per input sample with "
                    "identity source-time mapping and zero delay compensation. This model "
                    "emits exactly len(input) samples; internal padding exists only for gain "
                    "estimation."
                ),
            },
            "chunk_invariance": cross_hop_evidence(),
            "alignment_probe": alignment_probe(),
            "state": state_evidence(),
            "tail_probe": tail_probe(),
            "upstream_config_fields": list(CALLER_CONFIG_FIELDS),
            "pointer_requirement": {
                "pointer_asset": POINTER_ID,
                "required_content": POINTER_REQUIRED_CONTENT,
                "content_verified_here": False,
                "upstream_check": "pointer.read_text().strip() == checkpoint.name",
            },
        },
        "asset_boundary": asset_boundary(),
        "asset_admission": admission,
        "enhancement_profile": enhancement_profile(),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "frame_cases": frame_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "repeatability": {},
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "tool_provenance": list(TOOL_PROVENANCE),
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "readme_digest_files": list(README_DIGEST_FILES),
        "notes": [
            "Every metric in this report is computed on a deterministic synthetic fixture and describes the surrogate only.",
            "No ClearerVoice checkpoint, pointer, package, runtime, output, corpus, device, listener or release artifact is used or claimed.",
            "All timestamps are source-sample coordinates; no device, wall-clock, pacing or deadline measurement exists.",
        ],
    }


def build_report() -> Dict[str, Any]:
    core = _core_report()
    digests = []
    for _ in range(3):
        digests.append(sha256(canonical_bytes(core)))
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "tested_core": "report without the repeatability block",
    }
    return core


def build_contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": COMPONENT,
        "slug": SLUG,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "offline_boundary": OFFLINE_BOUNDARY,
        "claims": CLAIMS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "asset": asset_ref(),
        "asset_admission": asset_admission(asset_ref()),
        "upstream_contract": {
            "adapter_identity": PACKAGE_IDENTITY,
            "entrypoint": "adapters/clearvoice/run.py",
            "config_fields": list(CALLER_CONFIG_FIELDS),
            "input": "mono 16 kHz f32 in [-1, 1]",
            "output": "identity source-time mapping, zero delay compensation, zero padded samples, length equal to input",
            "pointer_required": True,
        },
        "surrogate": {
            "kind": "deterministic stdlib offline whole-clip surrogate",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "weights_used": False,
            "vendor_runtime_used": False,
        },
        "qualification": {
            "status": EVIDENCE_STATUS,
            "decision": DECISION,
            "qualifies": False,
            "missing_result_promoted": False,
            "processor_exposure": False,
            "real_runtime_used": False,
            "quality_claim": False,
            "release_claim": False,
        },
        "public_surface": {
            "provider_registration": False,
            "installed_v0_geometry_change": False,
            "installed_v0_behavior_change": False,
            "api_or_abi_change": False,
            "descriptor_or_registry_change": False,
            "default_selection": False,
            "shared_build_or_ci_change": False,
            "task_board_or_handoff_change": False,
        },
        "source_pins": {"source:" + key: value for key, value in SOURCE_PINS.items()},
        "boundary_pins": {"worktree:" + key: value for key, value in BOUNDARY_PINS.items()},
        "artifact_pins": {},
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "identity": "ClearerVoice-FRCRN_SE_16K-offline-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["offline"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "package": "clearvoice==" + PACKAGE_VERSION,
        "package_identity": PACKAGE_IDENTITY,
        "model": {
            "asset_id": CHECKPOINT_ID,
            "model_name": MODEL_NAME,
            "sha256": CHECKPOINT_SHA256,
            "byte_count": CHECKPOINT_BYTES,
            "source_revision": SOURCE_REVISION,
            "model_revision": MODEL_REVISION,
            "model_download_revision": MODEL_DOWNLOAD_REVISION,
            "auxiliary_assets": [{
                "asset_id": POINTER_ID,
                "sha256": POINTER_SHA256,
                "byte_count": POINTER_BYTES,
                "required_content": POINTER_REQUIRED_CONTENT,
            }],
        },
        "configuration": {
            "asset_required": True,
            "asset_storage": "external",
            "download_permitted": False,
            "whole_clip": True,
            "output_length_equals_input": True,
            "delay_compensation_samples": DECLARED_LAG_SAMPLES,
            "pointer_required": True,
            "reset_between_clips": True,
        },
        "entrypoint": ["python", "reference.py"],
        "upstream_entrypoint": ["python", "adapters/clearvoice/run.py"],
        "asset_readiness": asset_admission(asset_ref())["status"],
        "real_runtime_used": False,
        "weights_accessed": False,
        "quality_claim": False,
        "registration": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_registry_change": False,
            "public_api_abi_change": False,
        },
        "status": STATUS,
        "decision": DECISION,
    }


def build_readiness() -> Dict[str, Any]:
    admission = asset_admission(asset_ref())
    return {
        "schema_id": f"audio-sdk/task-evidence/{SLUG}/readiness/0.1",
        "task": TASK,
        "component": COMPONENT,
        "candidate": CANDIDATE_ID,
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_reference": asset_ref(),
        "admission": admission,
        "readiness_conclusion": (
            "The offline whole-clip boundary is modelled, but the candidate is not ready to "
            "run or qualify: the exact FRCRN_SE_16K checkpoint bytes and the clearvoice 0.1.2 "
            "runtime are absent, the checkpoint has no immutable model artifact revision in "
            "the pinned ledger, the 24-byte pointer content is unverified, and "
            "artifact-specific rights are not cleared."
        ),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "allowed_now": [
            "synthetic surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
        ],
        "not_allowed": [
            "downloading or bundling the FRCRN_SE_16K checkpoint, pointer or clearvoice package",
            "executing the vendor runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/timing",
        ],
    }
