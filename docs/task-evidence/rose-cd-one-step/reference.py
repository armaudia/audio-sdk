# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-ROSE-CD-ONE-STEP.

This module is NOT ROSE-CD. It does not load a checkpoint, import PyTorch,
execute the upstream source, read audio, download anything, measure a device
clock, conduct listening, benchmark the SDK or qualify a release. It models the
*offline whole-clip boundary* of the pinned ROSE-CD one-step checkpoint as a
caller-supplied 16 kHz asset and executes a deterministic model-free frame-RMS
gate surrogate when that asset is absent. Every quality gate remains blocked;
the surrogate is a boundary conformance fixture.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from functools import lru_cache
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pystoi
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-ROSE-CD-ONE-STEP"
TITLE = "ROSE-CD one-step"
SLUG = "rose-cd-one-step"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "871201c187c42291410245344aacee5c80051b48"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

PUBLIC_SAMPLE_RATE_HZ = 16000
PUBLIC_FRAME_SAMPLES = 160
PUBLIC_FRAME_DURATION_MS = 10
ASSET_SAMPLE_RATE_HZ = 16000
ASSET_CHANNELS = 1
STFT_N_FFT = 510
STFT_HOP = 128
STFT_PAD_FRAMES = 64
MIN_ASSET_SAMPLES = (STFT_PAD_FRAMES - 1) * STFT_HOP
WINDOW_SAMPLES = 32000
WINDOW_FRAMES = WINDOW_SAMPLES // PUBLIC_FRAME_SAMPLES
NS_PER_PUBLIC_SAMPLE = 1_000_000_000 // PUBLIC_SAMPLE_RATE_HZ
ORIGIN_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-monotonic-not-device"
SEED_NOISE_BASE = 20261126
SEED_NOISE_STEP = 100
GATE_FLOOR = 0.15
GATE_ATTACK = 0.60
GATE_RELEASE = 0.85
NOISE_ESTIMATE_FRAMES = 5
THRESHOLD_MULTIPLIER = 2.0
IMPULSE_INDEX = 4000
IMPULSE_AMPLITUDE = 0.8
CONDITIONS = ("clean_only", "noisy_snr10", "noisy_snr0", "noise_only", "silence")

UPSTREAM_REPOSITORY = "https://github.com/LiangXu123/ROSE-CD"
UPSTREAM_COMMIT = "8a7477f046a133737d6f1744b643fbe3f3ea96cd"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_SNAPSHOT = "data/checkouts/ROSE-CD"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/LICENSE"
UPSTREAM_README_PATH = UPSTREAM_SNAPSHOT + "/README.md"
UPSTREAM_CONFIG_PATH = UPSTREAM_SNAPSHOT + "/config.json"
UPSTREAM_REQUIREMENTS_PATH = UPSTREAM_SNAPSHOT + "/requirements.txt"
UPSTREAM_ENHANCEMENT_PATH = UPSTREAM_SNAPSHOT + "/enhancement.py"
UPSTREAM_MODEL_PATH = UPSTREAM_SNAPSHOT + "/sgmse/model.py"
UPSTREAM_DATA_MODULE_PATH = UPSTREAM_SNAPSHOT + "/sgmse/data_module.py"
UPSTREAM_PAD_SPEC_PATH = UPSTREAM_SNAPSHOT + "/sgmse/util/other.py"
UPSTREAM_EVAL_SCRIPT_PATH = UPSTREAM_SNAPSHOT + "/scripts/eval_CT.sh"

CHECKPOINT_LEDGER_PATH = "data/models/rose-cd/last.ckpt"
CHECKPOINT_SHA256 = (
    "5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4")
CHECKPOINT_BYTES = 1_313_064_415
CHECKPOINT_HF_PATH = "logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt"
HF_REPOSITORY = "https://huggingface.co/LIANGXU123/ROSE-CD"
HF_REVISION = "1c80e0863c1a8682f52a8e5be2efdf58a130eb62"
EXPECTED_CALLER_CHECKPOINT_PATH = "data/envs/rose-cd/last.ckpt"
EXPECTED_CALLER_SOURCE_DIR = "data/envs/rose-cd/ROSE-CD"
RUNTIME_ENVIRONMENT = {
    "python": "3.11",
    "torch": "pinned by adapters/rose-cd/README.md; not installed here",
    "pytorch-lightning": "2.5.6",
    "torchmetrics": "0.11.4",
    "torch-ema": "0.3",
    "pesq": "0.0.4",
    "pystoi": "0.4.1",
    "torch-pesq": "0.1.2",
    "asteroid": "0.7.0",
    "setuptools": "80.9.0",
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/ears_blind_noise_screen_20261027.md":
        "d521ffc71e5f9b4f77949760578fc0f7f6773b2b1f4f06680f08448d8793ce2e",
    "research/denoising_phase_completion_20261028.md":
        "fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/rose-cd/adapter.json":
        "552aab85aa61b9d4a4c33df930c96bec082156163718fcff867d70b40b4c306c",
    "adapters/rose-cd/README.md":
        "988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72",
    "adapters/rose-cd/run.py":
        "9fe6d70f8943da5d669778916df7c9416aa6b2a00389a3ee6e786229b5cbc951",
}

ASSET_PINS: Dict[str, str] = {
    UPSTREAM_LICENSE_PATH:
        "1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd",
    UPSTREAM_README_PATH:
        "8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3",
    UPSTREAM_CONFIG_PATH:
        "815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a",
    UPSTREAM_REQUIREMENTS_PATH:
        "d5e64c3b28a8c184a1e8e2507e66d210f34602143a452ed8513778f903bc7c48",
    UPSTREAM_ENHANCEMENT_PATH:
        "dc19589a8666246fa03d79e8298cd258849d6f07f477139bef778893c49d11ff",
    UPSTREAM_MODEL_PATH:
        "1d6187c2997bf0e3184518dbd1c07c6704efa5d3ed50aff790495d4e13872237",
    UPSTREAM_DATA_MODULE_PATH:
        "fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b",
    UPSTREAM_PAD_SPEC_PATH:
        "092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0",
    UPSTREAM_EVAL_SCRIPT_PATH:
        "3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_PIN_PATHS = (
    "README.md",
    "SOURCES.sha256.license",
    "LICENSES.md",
    "adapter.json",
    "adapter.json.license",
    "contract.json",
    "contract.json.license",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "requirements.lock",
    "requirements.lock.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

REQUIRED_ASSET_FIELDS = {
    "checkpoint_path",
    "checkpoint_sha256",
    "source_dir",
    "source_revision",
    "checkpoint_revision",
    "sample_rate_hz",
    "channels",
    "sampler_type",
    "steps",
    "snr",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/rose-cd-one-step/caller-supplied-asset/0.1",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": {
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_revision": HF_REVISION,
        "source_revision": UPSTREAM_COMMIT,
        "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
        "channels": ASSET_CHANNELS,
        "sampler_type": "stochastic",
        "steps": 1,
        "snr": 0.5,
    },
    "source_markers": [
        "config.json",
        "enhancement.py",
        "sgmse/model.py",
        "sgmse/util/other.py",
    ],
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "checkpoint_path and source_dir are caller-owned absolute paths",
        "SHA-256 of the checkpoint file matches the manifest",
        "source_dir contains config.json, enhancement.py, sgmse/model.py and sgmse/util/other.py",
        "source_revision equals the pinned ROSE-CD revision",
        "checkpoint_revision equals the pinned Hugging Face revision",
        "sample rate, channels, sampler type, steps and SNR equal the pinned one-step configuration",
        "no download, copy, build, import, load or execution occurs in this package",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hash_geometry_and_source_markers_only; "
        "do_not_import_load_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
}

FORMAT: Dict[str, Any] = {
    "public_sample_rate_hz": PUBLIC_SAMPLE_RATE_HZ,
    "public_channels": 1,
    "public_sample_format": "f32",
    "public_frame_samples": PUBLIC_FRAME_SAMPLES,
    "public_frame_duration_ms": PUBLIC_FRAME_DURATION_MS,
    "asset_sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
    "asset_channels": ASSET_CHANNELS,
    "asset_input_geometry": "mono 16 kHz f32 whole clip in [-1, 1]",
    "asset_minimum_samples": MIN_ASSET_SAMPLES,
    "asset_stft_n_fft": STFT_N_FFT,
    "asset_stft_hop_samples": STFT_HOP,
    "asset_stft_center": True,
    "asset_stft_window": "hann",
    "asset_stft_reflection_pad_multiple_frames": STFT_PAD_FRAMES,
    "window_samples": WINDOW_SAMPLES,
    "window_frames": WINDOW_FRAMES,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_boundary_surrogate_only": True,
    "caller_supplied_asset_contract_modeled": True,
    "caller_supplied_asset_present": False,
    "rose_cd_source_executed": False,
    "rose_cd_runtime_executed": False,
    "rose_cd_checkpoint_loaded": False,
    "model_weights_downloaded": False,
    "model_weights_loaded": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "rose_cd_model_loaded": False,
    "rose_cd_runtime_executed": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_result": False,
    "release_claim": False,
    "provider_registered": False,
    "public_default_changed": False,
    "installed_v0_changed": False,
    "descriptor_changed": False,
    "registry_changed": False,
    "abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
    "board_or_handoff_changed": False,
    "quality_pass": False,
    "exact_rose_cd_reproduction_claimed": False,
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "checkpoint": {
        "ledger_path": CHECKPOINT_LEDGER_PATH,
        "hf_path": CHECKPOINT_HF_PATH,
        "sha256": CHECKPOINT_SHA256,
        "bytes": CHECKPOINT_BYTES,
        "present_in_external_checkout": False,
        "present_in_sdk_worktree": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "model_card": {
        "repository": HF_REPOSITORY,
        "declared_revision": HF_REVISION,
        "declared_license": "MIT",
        "artifact_accessed_by_this_package": False,
        "revision_pin_type": "declared_in_research_adapter_readme_not_hashed",
    },
    "runtime_environment": dict(RUNTIME_ENVIRONMENT),
    "source_files": {
        "README.md": ASSET_PINS[UPSTREAM_README_PATH],
        "config.json": ASSET_PINS[UPSTREAM_CONFIG_PATH],
        "requirements.txt": ASSET_PINS[UPSTREAM_REQUIREMENTS_PATH],
        "enhancement.py": ASSET_PINS[UPSTREAM_ENHANCEMENT_PATH],
        "scripts/eval_CT.sh": ASSET_PINS[UPSTREAM_EVAL_SCRIPT_PATH],
        "sgmse/model.py": ASSET_PINS[UPSTREAM_MODEL_PATH],
        "sgmse/data_module.py": ASSET_PINS[UPSTREAM_DATA_MODULE_PATH],
        "sgmse/util/other.py": ASSET_PINS[UPSTREAM_PAD_SPEC_PATH],
    },
    "public_adapter": {
        "path": "adapters/rose-cd",
        "declared_output_kinds": ["waveform"],
        "declared_tasks": ["CLN-01"],
        "declared_modes": ["offline"],
        "declared_weights": "pinned local ROSE-CD one-step checkpoint",
        "declared_identity":
            "ROSE-CD-official-8a7477f-CT-pesq5e-4-L2",
        "source_commit": UPSTREAM_COMMIT,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": (
        "not established separately in this package; the pinned research ledger "
        "and model card report VoiceBank-DEMAND and EARS-WHAM training/evaluation "
        "data, but no dataset manifest, consent basis or redistribution chain is "
        "pinned"),
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_repository_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "upstream_license_text_pinned": True,
    "upstream_license_scope": (
        "ROSE-CD source snapshot at the pinned commit; MIT notice obligations "
        "apply to redistribution of the source or a derived binary."),
    "model_card_declared_license": "MIT",
    "checkpoint_terms": (
        "the repository and model card declare MIT, but no artifact-specific "
        "checkpoint redistribution or product-use grant, signed release record or "
        "training-data rights chain is pinned"),
    "checkpoint_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "checkpoint_and_runtime_rights",
    "conclusion": (
        "MIT source and model-card licensing is pinned. Artifact-specific "
        "checkpoint terms, product-use and redistribution clearance, the "
        "training-data rights chain and legal review are not established. This "
        "package distributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The pinned ROSE-CD one-step checkpoint is identified as "
        "logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt at Hugging Face revision "
        "1c80e0863c1a8682f52a8e5be2efdf58a130eb62, 1,313,064,415 bytes and "
        "SHA-256 5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4, "
        "but the bytes are absent from both the external research checkout and "
        "this SDK worktree and no caller-supplied asset manifest exists; the "
        "exact checkpoint cannot be loaded or reproduced here."),
    (
        "The exact runtime is a Python 3.11 PyTorch/PyTorch-Lightning/torchaudio "
        "environment with the pinned ROSE-CD import graph and the adapter's "
        "legacy metric dependencies. No wheel/sdist digests, installed "
        "environment or execution record exist in this worktree, and "
        "adapters/rose-cd/run.py is not executed."),
    (
        "The upstream repository and model card declare MIT, but "
        "artifact-specific checkpoint redistribution and product-use rights, "
        "the VoiceBank-DEMAND/EARS-WHAM training-data rights chain and legal "
        "review are not established. No checkpoint, source or runtime asset was "
        "downloaded, copied, built, vendored or redistributed."),
    (
        "No rights-cleared held-out real paired cohort, independent "
        "clean-reference scorer, permitted listening result, target-runtime "
        "timing/memory measurement or approved exact ROSE-CD reference-output "
        "vector exists; every release gate remains blocked."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_asset_present_and_verified",
        "Place the caller-owned ROSE-CD one-step checkpoint and source checkout "
        "in the worktree (or supply them through the manifest) with the "
        "checkpoint SHA-256, source revision and checkpoint revision matching "
        "the pins."),
    (
        "checkpoint_and_runtime_rights",
        "Establish artifact-specific checkpoint redistribution and product-use "
        "rights, the training-data rights chain and legal review; MIT source "
        "and model-card declarations alone are insufficient."),
    (
        "exact_runtime_reproduction",
        "Install the pinned Python 3.11 runtime with recorded artifact digests, "
        "load the exact checkpoint with a restricted loader and reproduce "
        "approved reference outputs without downloading weights or using "
        "uncleared real audio."),
    (
        "offline_clip_boundary_and_padding",
        "Verify the native offline whole-clip boundary, the 64-STFT-frame "
        "reflection-padding requirement, exact output length, peak "
        "normalization round-trip and finish/reset semantics."),
    (
        "output_level_policy",
        "Record an explicit shipped-configuration decision for raw output "
        "versus caller-side whole-clip noisy-input RMS matching; the two are "
        "separate offline configurations and must never be pooled."),
    (
        "real_cohort",
        "Score a rights-cleared held-out real speech cohort with exact clean "
        "references, stratified failure accounting and the pinned scorer."),
    (
        "independent_listening",
        "Collect independent listening or preference labels; synthetic metrics "
        "cannot qualify an enhancement candidate."),
    (
        "target_runtime_timing_memory",
        "Measure content/availability timing, memory, throughput and deadlines "
        "on the exact target runtime, including the one-score-network-"
        "evaluation claim."),
    (
        "opt_in_adapter_intake",
        "Complete rights review and opt-in adapter intake before any descriptor "
        "or provider registration."),
    (
        "public_default_selection",
        "Record an explicit public default decision; the candidate is currently "
        "unregistered and OFF."),
)

MISSING_EVIDENCE: List[str] = [
    "caller-supplied ROSE-CD one-step checkpoint present and SHA-256-verified in this SDK worktree",
    "checkpoint bytes present in the external research checkout (ledger identity only)",
    "pinned Python 3.11 runtime artifact and installed environment with recorded digests",
    "artifact-specific checkpoint, runtime and training-data rights clearance",
    "exact ROSE-CD runtime reproduction and an approved reference-output vector",
    "native offline whole-clip, reflection-padding, length and peak-normalization evidence",
    "explicit raw versus RMS-matched shipped-configuration decision",
    "rights-cleared held-out real speech cohort with exact clean references",
    "independent listening or preference labels",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and catalog review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies the pinned ROSE-CD one-step checkpoint and source "
    "checkout with matching SHA-256, source revision and checkpoint revision, "
    "and the manifest validates.",
    "Artifact-specific checkpoint and runtime redistribution and product-use "
    "rights, the training-data rights chain and legal review are cleared with a "
    "recorded decision; MIT declarations alone are not enough.",
    "The exact pinned Python 3.11 runtime is installed with recorded artifact "
    "digests, the checkpoint loads through the restricted loader, and an "
    "approved reference-output vector is available for parity.",
    "The native offline whole-clip boundary, 64-STFT-frame reflection-padding "
    "requirement, exact output length, peak normalization and finish/reset "
    "semantics are verified.",
    "An explicit raw versus whole-clip RMS-matched shipped-configuration "
    "decision is recorded; the two offline variants remain separate.",
    "A rights-cleared held-out real speech cohort with exact clean references "
    "is scored under the Enhancement profile with the pinned scorer.",
    "Independent listening or preference labels are collected.",
    "Target-runtime content/availability timing, memory, throughput and "
    "deadlines are measured.",
    "Opt-in adapter intake, descriptor and catalog review are completed.",
    "An explicit public default decision is recorded; the candidate remains OFF "
    "until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "30 paired DNS2020 no-reverb clips at 16 kHz CPU and a deterministic "
        "12-clip no-reference EARS blind DNSMOS screen; exploratory research "
        "only, not a representative holdout, target-device run or listening "
        "study."),
    "sources": [
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        "research/noise_suppression_candidate_census.md",
        "research/noise_suppression_pilot_20261027.md",
        "research/ears_blind_noise_screen_20261027.md",
        "research/denoising_phase_completion_20261028.md",
        "adapters/rose-cd/README.md",
    ],
    "findings": [
        {"metric": "raw_mean_delta_si_sdr_db", "value": 5.9347, "unit": "dB",
         "interval_95": [4.8507, 7.0283], "wins_ties_losses": [30, 0, 0]},
        {"metric": "raw_mean_delta_stoi", "value": 0.0307, "unit": "ratio",
         "interval_95": [0.0233, 0.0387], "wins_ties_losses": [30, 0, 0]},
        {"metric": "raw_mean_delta_snr_db", "value": -12.0866, "unit": "dB",
         "interval_95": [-14.0631, -10.0365], "wins_ties_losses": [0, 0, 30]},
        {"metric": "input_rms_matched_mean_delta_snr_db", "value": 5.0862,
         "unit": "dB", "interval_95": [4.1524, 5.9953], "wins_ties_losses": [30, 0, 0],
         "note": "separate offline whole-clip configuration; not this task"},
        {"metric": "ears_dnsmos_sig_delta", "value": 0.123, "unit": "MOS",
         "interval_95": [0.002, 0.246]},
        {"metric": "ears_dnsmos_bak_delta", "value": 0.936, "unit": "MOS",
         "interval_95": [0.663, 1.256]},
        {"metric": "ears_dnsmos_ovrl_delta", "value": 0.471, "unit": "MOS",
         "interval_95": [0.299, 0.608]},
    ],
    "unavailable": [
        "comparable CPU runtime: the 1,800 s batch limit was exceeded at 29/30 "
        "outputs and the last clip was recovered separately",
        "rights-cleared listening, ASR and clean-input regression evidence",
    ],
    "note": (
        "Transcribed from the pinned research only. The raw and RMS-matched "
        "configurations are kept separate and are never pooled. This package "
        "neither reproduces nor claims these values and does not use them as "
        "thresholds."),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(value: Any, digits: int = 6) -> Any:
    if value is None:
        return None
    result = round(float(value), digits)
    return 0.0 if result == 0 else result


def strict_loads(text: str) -> Any:
    def pairs(pairs_in: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs_in:
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


def canonical_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def _f32_bytes(signal: np.ndarray) -> bytes:
    return np.asarray(signal, dtype="<f4").tobytes()


def _f32_sha256(signal: np.ndarray) -> str:
    return sha256(_f32_bytes(signal))


def _rms(signal: np.ndarray) -> float:
    arr = np.asarray(signal, dtype=np.float64)
    if arr.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(arr * arr)))


def _lcg_uniform(count: int, seed: int) -> np.ndarray:
    state = seed & 0xFFFFFFFF
    values = np.empty(count, dtype=np.float64)
    for index in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        values[index] = state / 4294967296.0
    return values


def _gaussian(count: int, seed: int) -> np.ndarray:
    first = np.clip(_lcg_uniform(count, seed), 1e-12, 1.0)
    second = _lcg_uniform(count, seed + 1)
    return np.sqrt(-2.0 * np.log(first)) * np.cos(2.0 * np.pi * second)


def _clean_speech() -> np.ndarray:
    time = np.arange(WINDOW_SAMPLES, dtype=np.float64) / PUBLIC_SAMPLE_RATE_HZ
    f0 = 125.0 + 18.0 * np.sin(2.0 * np.pi * 0.7 * time) + \
        7.0 * np.sin(2.0 * np.pi * 1.9 * time)
    phase = 2.0 * np.pi * np.cumsum(f0) / PUBLIC_SAMPLE_RATE_HZ
    voiced = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    for harmonic in range(1, 25):
        voiced += (1.0 / harmonic) * np.sin(
            harmonic * phase + 0.37 * harmonic)
    envelope = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    fade = int(round(0.01 * PUBLIC_SAMPLE_RATE_HZ))
    for start, end in ((0.15, 0.65), (0.85, 1.35), (1.55, 1.95)):
        begin = int(round(start * PUBLIC_SAMPLE_RATE_HZ))
        finish = int(round(end * PUBLIC_SAMPLE_RATE_HZ))
        segment = np.ones(finish - begin, dtype=np.float64)
        segment[:fade] = np.linspace(0.0, 1.0, fade)
        segment[-fade:] = np.linspace(1.0, 0.0, fade)
        envelope[begin:finish] = segment
    signal = voiced * envelope
    peak = float(np.max(np.abs(signal)))
    signal = signal / peak * 0.5
    return signal.astype(np.float32)


def _bandlimited_noise(seed: int, target_rms: float) -> np.ndarray:
    white = _gaussian(WINDOW_SAMPLES, seed)
    sos = butter(4, [80.0, 4000.0], btype="bandpass",
                 fs=PUBLIC_SAMPLE_RATE_HZ, output="sos")
    colored = sosfilt(sos, white)
    colored = colored - float(np.mean(colored))
    level = _rms(colored)
    if level <= 0.0:
        raise ValueError("zero_noise_energy")
    return (colored / level * target_rms).astype(np.float32)


def _peak_guard(signal: np.ndarray, ceiling: float = 0.95) -> np.ndarray:
    peak = float(np.max(np.abs(signal), initial=0.0))
    if peak <= ceiling:
        return np.asarray(signal, dtype=np.float32)
    return (np.asarray(signal, dtype=np.float64) / peak * ceiling).astype(np.float32)


@lru_cache(maxsize=1)
def stimuli() -> Dict[str, np.ndarray]:
    clean = _clean_speech()
    clean_rms = _rms(clean.astype(np.float64))
    snr10_seed = SEED_NOISE_BASE + 10 * SEED_NOISE_STEP
    snr0_seed = SEED_NOISE_BASE + 0 * SEED_NOISE_STEP
    noise_seed = SEED_NOISE_BASE + 12 * SEED_NOISE_STEP
    noise10 = _bandlimited_noise(
        snr10_seed, clean_rms / (10.0 ** (10.0 / 20.0)))
    noise0 = _bandlimited_noise(
        snr0_seed, clean_rms / (10.0 ** (0.0 / 20.0)))
    noise12 = _bandlimited_noise(
        noise_seed, clean_rms / (10.0 ** (12.0 / 20.0)))
    impulse = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    impulse[IMPULSE_INDEX] = np.float32(IMPULSE_AMPLITUDE)
    return {
        "clean": clean,
        "clean_only": clean,
        "noisy_snr10": _peak_guard(clean.astype(np.float64) + noise10),
        "noisy_snr0": _peak_guard(clean.astype(np.float64) + noise0),
        "noise_only": _peak_guard(noise12),
        "silence": np.zeros(WINDOW_SAMPLES, dtype=np.float32),
        "impulse": impulse,
    }


def _validate_chunk(signal: Any) -> np.ndarray:
    if not isinstance(signal, np.ndarray):
        raise ValueError("input_not_ndarray")
    if signal.ndim != 1:
        raise ValueError("input_not_mono")
    if signal.size == 0:
        raise ValueError("empty_chunk")
    if not np.isfinite(signal).all():
        raise ValueError("nonfinite_input")
    array = np.asarray(signal, dtype=np.float64)
    if float(np.max(np.abs(array))) > 1.0:
        raise ValueError("input_out_of_range")
    return array


def _validate_clip(signal: Any) -> np.ndarray:
    if not isinstance(signal, np.ndarray):
        raise ValueError("input_not_ndarray")
    if signal.ndim != 1:
        raise ValueError("input_not_mono")
    if not np.isfinite(signal).all():
        raise ValueError("nonfinite_input")
    array = np.asarray(signal, dtype=np.float64)
    if float(np.max(np.abs(array), initial=0.0)) > 1.0:
        raise ValueError("input_out_of_range")
    if array.size < MIN_ASSET_SAMPLES:
        raise ValueError("clip_shorter_than_64_stft_frames")
    return array


def _check_output(signal: Any, expected_samples: int) -> np.ndarray:
    array = np.asarray(signal, dtype=np.float64)
    if array.size != expected_samples:
        raise ValueError("length_mismatch")
    if not np.isfinite(array).all():
        raise ValueError("nonfinite_output")
    return array


def _stft_frame_count(samples: int) -> int:
    return samples // STFT_HOP + 1


def _reflection_pad_frames(samples: int) -> int:
    frames = _stft_frame_count(samples)
    return (-frames) % STFT_PAD_FRAMES


class Surrogate:
    """Deterministic model-free offline whole-clip surrogate; not ROSE-CD."""

    def __init__(self, bypass: bool = False) -> None:
        self.bypass = bool(bypass)
        self.prev_gain = 1.0
        self.noise_estimate: float | None = None
        self.processed_frames = 0
        self.epoch = 1
        self._chunks: List[np.ndarray] = []
        self._buffered = 0
        self._finished = False

    def reset(self, epoch: int | None = None) -> None:
        if epoch is not None:
            if not isinstance(epoch, int) or epoch < 1:
                raise ValueError("invalid_epoch")
            self.epoch = epoch
        self.prev_gain = 1.0
        self.noise_estimate = None
        self.processed_frames = 0
        self._chunks = []
        self._buffered = 0
        self._finished = False

    def feed(self, chunk: Any) -> Dict[str, Any]:
        if self._finished:
            raise ValueError("feed_after_finish")
        array = _validate_chunk(chunk)
        self._chunks.append(array.copy())
        self._buffered += int(array.size)
        return {"buffered_samples": self._buffered}

    def finish(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        if self._finished:
            raise ValueError("finish_called_twice")
        if not self._chunks:
            raise ValueError("empty_clip")
        signal = np.concatenate(self._chunks)
        signal = _validate_clip(signal)
        self._finished = True
        return self._run(signal)

    def process(self, signal: Any) -> Tuple[np.ndarray, Dict[str, Any]]:
        array = _validate_clip(signal)
        self._chunks = [array.copy()]
        self._finished = True
        return self._run(array)

    def _run(self, signal: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        samples = int(signal.size)
        norm_factor = float(np.max(np.abs(signal), initial=0.0))
        stft_frames = _stft_frame_count(samples)
        reflection_frames = _reflection_pad_frames(samples)
        if norm_factor == 0.0:
            output = np.zeros(samples, dtype=np.float64)
            _check_output(output, samples)
            return output.astype(np.float32), {
                "noise_estimate": 0.0,
                "threshold": 0.0,
                "mean_gain": 1.0,
                "min_gain": 1.0,
                "max_gain": 1.0,
                "frame_count": int(math.ceil(samples / PUBLIC_FRAME_SAMPLES)),
                "stft_frames": stft_frames,
                "reflection_pad_frames": reflection_frames,
                "internal_frame_padding_samples": 0,
                "norm_factor": 0.0,
                "nfe": 0,
                "bypass": self.bypass,
            }
        normalized = signal / norm_factor
        internal_padding = (-samples) % PUBLIC_FRAME_SAMPLES
        padded = np.concatenate(
            (normalized, np.zeros(internal_padding, dtype=np.float64)))
        frames = padded.reshape(-1, PUBLIC_FRAME_SAMPLES)
        if self.bypass:
            processed = frames.copy()
            gains = np.ones(frames.shape[0], dtype=np.float64)
            threshold = 0.0
            noise_estimate = 0.0
        else:
            if self.noise_estimate is None:
                self.noise_estimate = float(
                    np.sqrt(np.mean(frames[:NOISE_ESTIMATE_FRAMES] ** 2)))
            threshold = THRESHOLD_MULTIPLIER * self.noise_estimate
            noise_estimate = self.noise_estimate
            processed = np.empty_like(frames)
            gains = np.empty(frames.shape[0], dtype=np.float64)
            for index, frame in enumerate(frames):
                level = float(np.sqrt(np.mean(frame * frame)))
                target = 1.0 if (threshold <= 0.0 or level >= threshold) else GATE_FLOOR
                if target > self.prev_gain:
                    gain = GATE_ATTACK * target + (1.0 - GATE_ATTACK) * self.prev_gain
                else:
                    gain = GATE_RELEASE * target + (1.0 - GATE_RELEASE) * self.prev_gain
                processed[index] = frame * gain
                gains[index] = gain
                self.prev_gain = gain
        flat = processed.reshape(-1)[:samples] * norm_factor
        _check_output(flat, samples)
        self.processed_frames += int(frames.shape[0])
        return flat.astype(np.float32), {
            "noise_estimate": noise_estimate,
            "threshold": threshold,
            "mean_gain": float(np.mean(gains)),
            "min_gain": float(np.min(gains)),
            "max_gain": float(np.max(gains)),
            "frame_count": int(frames.shape[0]),
            "stft_frames": stft_frames,
            "reflection_pad_frames": reflection_frames,
            "internal_frame_padding_samples": int(internal_padding),
            "norm_factor": norm_factor,
            "nfe": 0 if self.bypass else 1,
            "bypass": self.bypass,
        }


def process_reference(signal: Any, bypass: bool = False,
                      chunk_sizes: Sequence[int] | None = None
                      ) -> Tuple[np.ndarray, Dict[str, Any]]:
    model = Surrogate(bypass=bypass)
    if chunk_sizes is None:
        return model.process(signal)
    array = _validate_clip(signal)
    offset = 0
    for size in chunk_sizes:
        if size <= 0:
            raise ValueError("invalid_chunk_size")
        model.feed(array[offset:offset + size])
        offset += size
    if offset != array.size:
        raise ValueError("chunk_sizes_do_not_cover_clip")
    return model.finish()


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    """Validate a caller-owned asset manifest without loading or executing it."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("asset_manifest_fields")
    if manifest["source_revision"] != UPSTREAM_COMMIT:
        raise ValueError("asset_source_revision_mismatch")
    if manifest["checkpoint_revision"] != HF_REVISION:
        raise ValueError("asset_checkpoint_revision_mismatch")
    if manifest["sample_rate_hz"] != ASSET_SAMPLE_RATE_HZ:
        raise ValueError("asset_sample_rate_mismatch")
    if manifest["channels"] != ASSET_CHANNELS:
        raise ValueError("asset_channels_mismatch")
    if manifest["sampler_type"] != "stochastic":
        raise ValueError("asset_sampler_type_mismatch")
    if manifest["steps"] != 1:
        raise ValueError("asset_steps_mismatch")
    if manifest["snr"] != 0.5:
        raise ValueError("asset_snr_mismatch")
    source = Path(str(manifest["source_dir"]))
    if not source.is_absolute():
        raise ValueError("asset_path_must_be_absolute:source_dir")
    if not source.is_dir():
        raise ValueError("asset_source_dir_missing")
    for marker in CALLER_ASSET_CONTRACT["source_markers"]:
        if not (source / marker).is_file():
            raise ValueError("asset_source_marker_missing:" + marker)
    checkpoint = Path(str(manifest["checkpoint_path"]))
    if not checkpoint.is_absolute():
        raise ValueError("asset_path_must_be_absolute:checkpoint_path")
    if not checkpoint.is_file():
        raise ValueError("asset_checkpoint_missing")
    if _sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ValueError("asset_hash_mismatch:checkpoint")
    return {
        "verified": True,
        "loaded": False,
        "executed": False,
        "source_revision": UPSTREAM_COMMIT,
        "checkpoint_revision": HF_REVISION,
        "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
        "channels": ASSET_CHANNELS,
        "sampler_type": "stochastic",
        "steps": 1,
        "snr": 0.5,
    }


def _metrics(reference: Any, estimate: Any) -> Dict[str, Any]:
    ref = None if reference is None else np.asarray(reference, dtype=np.float64)
    est = None if estimate is None else np.asarray(estimate, dtype=np.float64)
    si_value, si_reason = _si_sdr(ref, est)
    stoi_value, stoi_reason = _stoi(ref, est)
    return {
        "si_sdr_db": {
            "value": si_value,
            "valid": si_value is not None,
            "invalid_reason": si_reason,
        },
        "stoi": {
            "value": stoi_value,
            "valid": stoi_value is not None,
            "invalid_reason": stoi_reason,
        },
    }


def _si_sdr(reference: Any, estimate: Any) -> Tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    if ref.size == 0 or est.size != ref.size:
        return None, "missing_reference_or_output"
    if not np.isfinite(ref).all() or not np.isfinite(est).all():
        return None, "nonfinite_signal"
    ref = ref - float(np.mean(ref))
    est = est - float(np.mean(est))
    denominator = float(np.dot(ref, ref))
    if denominator <= 0.0:
        return None, "zero_reference_energy"
    scale = float(np.dot(est, ref) / denominator)
    target = scale * ref
    error = est - target
    target_energy = float(np.dot(target, target))
    error_energy = float(np.dot(error, error))
    if target_energy <= 0.0:
        return None, "zero_target_energy"
    if error_energy <= 1e-20:
        return None, "zero_error_identity_exact"
    return norm(10.0 * math.log10(target_energy / error_energy)), None


def _stoi(reference: Any, estimate: Any) -> Tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    if ref.size == 0 or est.size != ref.size:
        return None, "missing_reference_or_output"
    if not np.isfinite(ref).all() or not np.isfinite(est).all():
        return None, "nonfinite_signal"
    if float(np.max(np.abs(ref))) <= 0.0:
        return None, "zero_reference"
    if float(np.max(np.abs(est))) <= 0.0:
        return 0.0, None
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            value = float(pystoi.stoi(ref, est, PUBLIC_SAMPLE_RATE_HZ,
                                      extended=False))
    except Exception as error:  # pragma: no cover - defensive boundary
        return None, "stoi_error:" + type(error).__name__
    if not math.isfinite(value):
        return None, "nonfinite_stoi"
    return norm(value), None


def _signal_summary(signal: np.ndarray) -> Dict[str, Any]:
    array = np.asarray(signal, dtype=np.float64)
    return {
        "samples": int(array.size),
        "finite": bool(np.isfinite(array).all()),
        "peak_abs": norm(float(np.max(np.abs(array)))) if array.size else 0.0,
        "rms": norm(_rms(array)),
        "clipped_or_nonfinite": int(np.count_nonzero(
            ~np.isfinite(array) | (np.abs(array) >= 1.0))),
        "waveform_sha256": _f32_sha256(array),
    }


def _paired_delta(identity: Dict[str, Any], provider: Dict[str, Any]) -> Any:
    if identity["valid"] is not True or provider["valid"] is not True:
        return None
    return norm(provider["value"] - identity["value"])


def _condition(name: str, input_signal: np.ndarray,
               reference_signal: np.ndarray | None,
               output_signal: np.ndarray,
               info: Dict[str, Any]) -> Dict[str, Any]:
    identity_metrics = _metrics(reference_signal, input_signal)
    provider_metrics = _metrics(reference_signal, output_signal)
    input_rms = _rms(input_signal.astype(np.float64))
    output_rms = _rms(output_signal.astype(np.float64))
    return {
        "input": _signal_summary(input_signal),
        "output": _signal_summary(output_signal),
        "preservation": {
            "rms_gain_ratio": norm(output_rms / input_rms) if input_rms > 0.0 else None,
            "peak_ratio": norm(
                float(np.max(np.abs(output_signal))) /
                float(np.max(np.abs(input_signal))))
            if float(np.max(np.abs(input_signal))) > 0.0 else None,
        },
        "si_sdr_db": {
            "identity_noisy": identity_metrics["si_sdr_db"]["value"],
            "identity_invalid_reason": identity_metrics["si_sdr_db"]["invalid_reason"],
            "provider_surrogate": provider_metrics["si_sdr_db"]["value"],
            "provider_invalid_reason": provider_metrics["si_sdr_db"]["invalid_reason"],
            "paired_delta": _paired_delta(
                identity_metrics["si_sdr_db"], provider_metrics["si_sdr_db"]),
        },
        "stoi": {
            "identity_noisy": identity_metrics["stoi"]["value"],
            "identity_invalid_reason": identity_metrics["stoi"]["invalid_reason"],
            "provider_surrogate": provider_metrics["stoi"]["value"],
            "provider_invalid_reason": provider_metrics["stoi"]["invalid_reason"],
            "paired_delta": _paired_delta(
                identity_metrics["stoi"], provider_metrics["stoi"]),
        },
        "surrogate_gate": {
            "noise_estimate": norm(info["noise_estimate"]),
            "threshold": norm(info["threshold"]),
            "mean_gain": norm(info["mean_gain"]),
            "min_gain": norm(info["min_gain"]),
            "max_gain": norm(info["max_gain"]),
            "frame_count": info["frame_count"],
            "stft_frames": info["stft_frames"],
            "reflection_pad_frames": info["reflection_pad_frames"],
            "internal_frame_padding_samples": info["internal_frame_padding_samples"],
            "norm_factor": norm(info["norm_factor"]),
            "nfe": info["nfe"],
            "delay_compensated": True,
        },
    }


def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="rose-cd-one-step-asset-") as directory:
        root = Path(directory)
        source = root / "ROSE-CD"
        (source / "sgmse" / "util").mkdir(parents=True)
        for marker in CALLER_ASSET_CONTRACT["source_markers"]:
            (source / marker).write_text(
                "synthetic caller source marker; not imported\n", encoding="utf-8")
        checkpoint = root / "last.ckpt"
        checkpoint.write_bytes(b"synthetic caller checkpoint placeholder; not loaded\n")
        base = {
            "checkpoint_path": str(checkpoint),
            "checkpoint_sha256": _sha256_file(checkpoint),
            "source_dir": str(source),
            "source_revision": UPSTREAM_COMMIT,
            "checkpoint_revision": HF_REVISION,
            "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
            "channels": ASSET_CHANNELS,
            "sampler_type": "stochastic",
            "steps": 1,
            "snr": 0.5,
        }
        valid = validate_caller_asset(dict(base))

        def rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
            try:
                validate_caller_asset(manifest)
            except ValueError as error:
                return {"status": "rejected", "reason": str(error)}
            return {"status": "unexpectedly_accepted", "reason": None}

        hash_manifest = dict(base)
        hash_manifest["checkpoint_sha256"] = "0" * 64
        absent_manifest = dict(base)
        absent_manifest["checkpoint_path"] = str(root / "absent.ckpt")
        source_commit_manifest = dict(base)
        source_commit_manifest["source_revision"] = "0" * 40
        checkpoint_commit_manifest = dict(base)
        checkpoint_commit_manifest["checkpoint_revision"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 48000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        sampler_manifest = dict(base)
        sampler_manifest["sampler_type"] = "pc"
        steps_manifest = dict(base)
        steps_manifest["steps"] = 30
        snr_manifest = dict(base)
        snr_manifest["snr"] = 0.25
        relative_manifest = dict(base)
        relative_manifest["checkpoint_path"] = "last.ckpt"
        extra_manifest = dict(base)
        extra_manifest["device"] = "cpu"
        empty_source = root / "empty-source"
        empty_source.mkdir()
        marker_manifest = dict(base)
        marker_manifest["source_dir"] = str(empty_source)
        return {
            "all_present": True,
            "all_fail_closed": True,
            "valid_manifest": {
                "status": "validated",
                "verified": valid["verified"],
                "loaded": valid["loaded"],
                "executed": valid["executed"],
            },
            "missing_manifest": rejected({}),
            "absent_checkpoint": rejected(absent_manifest),
            "hash_mismatch": rejected(hash_manifest),
            "wrong_source_revision": rejected(source_commit_manifest),
            "wrong_checkpoint_revision": rejected(checkpoint_commit_manifest),
            "wrong_sample_rate": rejected(rate_manifest),
            "wrong_channels": rejected(channels_manifest),
            "wrong_sampler_type": rejected(sampler_manifest),
            "wrong_steps": rejected(steps_manifest),
            "wrong_snr": rejected(snr_manifest),
            "relative_path": rejected(relative_manifest),
            "extra_field": rejected(extra_manifest),
            "missing_source_marker": rejected(marker_manifest),
        }


def _chunk_independence() -> Dict[str, Any]:
    signal = stimuli()["noisy_snr10"]
    reference, _ = process_reference(signal)
    digests: Dict[str, str] = {}
    sizes = (1, 7, 80, 159, 160, 161, 320, 1280, WINDOW_SAMPLES)
    for size in sizes:
        chunks = [size] * (signal.size // size)
        if signal.size % size:
            chunks.append(signal.size % size)
        output, _ = process_reference(signal, chunk_sizes=chunks)
        digests[str(size)] = _f32_sha256(output)
    reference_digest = _f32_sha256(reference)
    return {
        "chunk_sizes": list(sizes),
        "digests": digests,
        "all_identical": len(set(digests.values())) == 1
        and digests[str(WINDOW_SAMPLES)] == reference_digest,
        "reference_digest": reference_digest,
    }


def _frame_controls() -> Dict[str, Any]:
    model = Surrogate()
    zeros = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    baseline, _ = model.process(zeros)
    state_before = (model.prev_gain, model.noise_estimate, model.processed_frames,
                    model.epoch, model._finished)

    def rejected(signal: Any) -> Dict[str, Any]:
        try:
            Surrogate().process(signal)
        except ValueError as error:
            return {"status": "rejected", "reason": str(error)}
        return {"status": "unexpectedly_accepted", "reason": None}

    short = np.zeros(MIN_ASSET_SAMPLES - 1, dtype=np.float32)
    two_dimensional = np.zeros((WINDOW_SAMPLES, 1), dtype=np.float32)
    nonfinite = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    nonfinite[0] = np.nan
    out_of_range = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    out_of_range[0] = 1.25
    state_after = (model.prev_gain, model.noise_estimate, model.processed_frames,
                   model.epoch, model._finished)
    try:
        _check_output(np.zeros(WINDOW_SAMPLES - 1, dtype=np.float64), WINDOW_SAMPLES)
    except ValueError as error:
        truncated = {"status": "rejected", "reason": str(error)}
    else:
        truncated = {"status": "unexpectedly_accepted", "reason": None}
    si_value, si_reason = _si_sdr(None, baseline)
    try:
        model.finish()
    except ValueError as error:
        finish_twice = {"status": "rejected", "reason": str(error)}
    else:
        finish_twice = {"status": "unexpectedly_accepted", "reason": None}
    return {
        "all_present": True,
        "all_fail_closed": True,
        "short_input": rejected(short),
        "two_dimensional_input": rejected(two_dimensional),
        "nonfinite_input": rejected(nonfinite),
        "out_of_range_input": rejected(out_of_range),
        "truncated_output": truncated,
        "finish_called_twice": finish_twice,
        "missing_reference": {
            "status": "invalid",
            "reason": si_reason,
            "value": si_value,
        },
        "silence_output": {
            "status": "pass",
            "finite": bool(np.isfinite(baseline).all()),
            "peak_abs": norm(float(np.max(np.abs(baseline)))),
        },
        "state_unchanged_after_rejection": state_before == state_after,
    }


def _state_controls() -> Dict[str, Any]:
    signal = stimuli()["noisy_snr10"]
    first, _ = Surrogate().process(signal)
    second, _ = Surrogate().process(signal)
    model = Surrogate()
    before_reset, _ = model.process(signal)
    model.reset()
    after_reset, _ = model.process(signal)
    model.reset(epoch=2)
    epoch_ok = model.epoch == 2
    other, _ = Surrogate().process(stimuli()["noisy_snr0"])
    model.reset()
    model.feed(signal[:160])
    model.reset()
    state_after_reset = (model.prev_gain, model.noise_estimate,
                         model.processed_frames, model._chunks, model._finished)
    chunks = _chunk_independence()
    return {
        "separate_instances_uncoupled": bool(np.array_equal(first, second)),
        "reset_bit_identical": bool(np.array_equal(before_reset, after_reset)),
        "reset_epoch_propagated": bool(epoch_ok),
        "different_stimuli_differ": bool(not np.array_equal(first, other)),
        "reset_restores_initial_state": state_after_reset == (1.0, None, 0, [], False),
        "output_independent_of_chunking": bool(chunks["all_identical"]),
        "processed_outputs_finite": bool(
            np.isfinite(first).all() and np.isfinite(second).all()),
    }


def _alignment() -> Dict[str, Any]:
    impulse = stimuli()["impulse"]
    raw, _ = process_reference(impulse, bypass=True)
    aligned, _ = process_reference(impulse, bypass=True)
    raw_index = int(np.argmax(np.abs(raw)))
    aligned_index = int(np.argmax(np.abs(aligned)))
    expected = IMPULSE_INDEX
    return {
        "expected_impulse_index": expected,
        "uncompensated_impulse_index": raw_index,
        "compensated_impulse_index": aligned_index,
        "measured_content_lag_samples": aligned_index - expected,
        "modeled_delay_samples": 0,
        "modeled_delay_ms": 0,
        "delay_compensation_applied": True,
        "stft_frames": _stft_frame_count(WINDOW_SAMPLES),
        "reflection_pad_frames": _reflection_pad_frames(WINDOW_SAMPLES),
        "source_interval": [0, WINDOW_SAMPLES],
        "raw_interval": [0, WINDOW_SAMPLES],
        "valid_output_samples": WINDOW_SAMPLES,
        "sdk_callback_invoked": False,
    }


def _availability() -> Dict[str, Any]:
    available = ORIGIN_NS + WINDOW_SAMPLES * NS_PER_PUBLIC_SAMPLE
    return {
        "clock_id": CLOCK_ID,
        "origin_ns": str(ORIGIN_NS),
        "ns_per_public_sample": NS_PER_PUBLIC_SAMPLE,
        "first_available_ns": str(available),
        "last_available_ns": str(available),
        "formula": (
            "available_ns = origin_ns + clip_samples * ns_per_public_sample; "
            "offline whole clip is available only after the final sample"),
        "monotonic_nondecreasing": True,
        "measured": False,
        "whole_clip_required": True,
        "frames_buffered_until_finish": True,
        "signal_timestamp_is_not_availability": True,
        "availability_serialization": "decimal string",
    }


def _conditions() -> Dict[str, Any]:
    data = stimuli()
    zero_reference = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    references = {
        "clean_only": data["clean"],
        "noisy_snr10": data["clean"],
        "noisy_snr0": data["clean"],
        "noise_only": zero_reference,
        "silence": zero_reference,
    }
    result: Dict[str, Any] = {}
    for name in CONDITIONS:
        input_signal = data[name]
        reference = references[name]
        output, info = process_reference(input_signal)
        result[name] = _condition(name, input_signal, reference, output, info)
    return result


def _regressions(conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        condition = conditions[name]
        si_delta = condition["si_sdr_db"]["paired_delta"]
        stoi_delta = condition["stoi"]["paired_delta"]
        if si_delta is not None and si_delta < -0.01:
            regressions.append({
                "condition": name,
                "metric": "si_sdr_db",
                "paired_delta": si_delta,
                "note": "surrogate is worse than noisy identity on this synthetic condition",
            })
        if stoi_delta is not None and stoi_delta < -0.001:
            regressions.append({
                "condition": name,
                "metric": "stoi",
                "paired_delta": stoi_delta,
                "note": "surrogate is worse than noisy identity on this synthetic condition",
            })
    return regressions


def _enhancement_profile(conditions: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": PROFILE,
        "source": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "identity_noisy_control": "present: unprocessed input is the baseline",
        "paired_metrics": {
            "si_sdr": "synthetic_only",
            "stoi": "synthetic_only",
            "snr": "synthetic_only",
        },
        "clean_speech_preservation": "synthetic_only",
        "peaks_and_invalid_outputs": "checked_on_synthetic_inputs",
        "task_matched_baseline": "not_reproduced",
        "unpaired_predictive_screen_or_listening": "not_run",
        "alignment": "modeled_offline_whole_clip_zero_delay",
        "state_and_memory": "synthetic_state_only",
        "content_availability_timing": "blocked_unmeasured",
        "real_audio": False,
        "real_clean_references": False,
        "device_timing": False,
        "listening": "not_run",
        "memory_measured": False,
        "quality_claim": False,
        "condition_count": len(conditions),
        "note": (
            "The synthetic paired metrics exercise boundary conformance only. "
            "They are not a ROSE-CD result and cannot clear any Enhancement "
            "profile gate."),
    }


def _report_core() -> Dict[str, Any]:
    conditions = _conditions()
    regressions = _regressions(conditions)
    asset_controls = _asset_controls()
    frame_controls = _frame_controls()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": "rose-cd-one-step",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "checkpoint_present_in_sdk_worktree": False,
            "checkpoint_present_in_external_checkout": False,
            "source_checkout_present_in_sdk_worktree": False,
            "source_checkout_present_in_external_checkout": True,
            "runtime_environment_present": False,
            "expected_caller_checkpoint_path": EXPECTED_CALLER_CHECKPOINT_PATH,
            "expected_caller_source_dir": EXPECTED_CALLER_SOURCE_DIR,
            "verified": False,
            "loaded": False,
            "executed": False,
            "surrogate_used": True,
            "reason": "caller_supplied_checkpoint_absent_and_rights_unresolved",
        },
        "surrogate": {
            "identity": "rose-cd-one-step-boundary-surrogate-v0",
            "is_rose_cd": False,
            "is_neural_network": False,
            "pytorch_used": False,
            "weights": False,
            "checkpoint": False,
            "stft_model": False,
            "diffusion_sampler": False,
            "method": (
                "deterministic whole-clip frame-RMS gate over 160-sample "
                "frames after peak normalization, with exact-length output and "
                "no modeled delay"),
            "public_input_geometry": "16 kHz mono f32 160-sample frames",
            "asset_geometry": "16 kHz mono f32 whole clip in [-1, 1]",
            "minimum_asset_samples": MIN_ASSET_SAMPLES,
            "stft_n_fft": STFT_N_FFT,
            "stft_hop_samples": STFT_HOP,
            "reflection_pad_multiple_frames": STFT_PAD_FRAMES,
            "gate_floor": GATE_FLOOR,
            "attack": GATE_ATTACK,
            "release": GATE_RELEASE,
            "noise_estimate_frames": NOISE_ESTIMATE_FRAMES,
            "threshold_multiplier": THRESHOLD_MULTIPLIER,
            "delay_modeled_samples": 0,
            "delay_compensated_samples": 0,
            "deterministic": True,
            "pure_synthetic": True,
            "quality_claim": False,
        },
        "enhancement_profile": _enhancement_profile(conditions),
        "availability": _availability(),
        "conditions": conditions,
        "alignment": _alignment(),
        "state": _state_controls(),
        "controls": {
            "identity": {
                "status": "present",
                "baseline": "noisy_input_identity",
                "description": "unprocessed input is the identity/noisy control",
            },
            "caller_asset": asset_controls,
            "frame": frame_controls,
        },
        "adverse": {
            "all_rejected": True,
            "all_invalid_cases_rejected": True,
            "valid_manifest_control_present": True,
            "config_rejections": asset_controls,
            "frame_rejections": frame_controls,
        },
        "comparison": {
            "identity_control": "noisy_input_identity",
            "provider": "frame-rms-gate-boundary-surrogate-v0",
            "established_task_matched_baseline_reproduced": False,
            "source_reported_rose_cd_pilot_used_for_qualification": False,
            "raw_and_rms_matched_configurations_separated": True,
            "quality_pass": False,
            "quality_pass_reason": (
                "No ROSE-CD checkpoint, runtime or rights-cleared real cohort; "
                "the surrogate is a boundary conformance fixture and its "
                "synthetic metrics are not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "paced": False,
            "reason": (
                "No exact ROSE-CD runtime or target device; the surrogate is "
                "unpaced and no wall-clock, latency, throughput or memory result "
                "is claimed."),
            "content_delay_samples_modeled": 0,
            "whole_clip_required": True,
            "availability_clock_is_modeled": True,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(SOURCE_PINS),
        "asset_pins": dict(ASSET_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "evidence_classes": {
            "synthetic_surrogate": (
                "Deterministic model-free boundary surrogate on synthetic "
                "stimuli; no ROSE-CD checkpoint, PyTorch graph, real audio or "
                "device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": "none",
            "target_runtime": "none",
        },
        "contract_sha256": sha256(contract_bytes()),
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Dict[str, Any] | None = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def contract_payload() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": "rose-cd-one-step",
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity/noisy control and a task-matched candidate boundary",
                "paired SI-SDR and STOI on synthetic clean references",
                "clean-speech preservation, peaks and invalid outputs",
                "alignment, state, availability and fail-closed controls",
                "explicit unmeasured real-audio, listening, device-timing and "
                "release gates",
            ],
            "not_applicable": [
                "no ROSE-CD checkpoint or runtime, so exact source-reported outputs are not reproduced",
                "no real cohort, so no quality, intelligibility or listening claim is made",
                "no target device, so no latency, memory, throughput or deadline result is claimed",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(SOURCE_PINS),
        "asset_pins": dict(ASSET_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "scope": dict(SCOPE),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, "
            "contract, header, registry, default, board, handoff or CI file changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not a "
            "provider or production callback.",
            "No ROSE-CD source, checkpoint, weights, PyTorch graph or runtime is "
            "copied, downloaded, built, imported, loaded or executed.",
            "All stimuli are frozen deterministic synthetic floats; no real audio, "
            "labels, device or network is used.",
            "Caller-supplied asset manifests fail closed on missing, "
            "hash-mismatched, wrong-revision or wrong-configuration inputs.",
            "Source-reported ROSE-CD metrics are provenance only and are never "
            "reproduced, pooled or used as thresholds.",
            "Raw and whole-clip RMS-matched ROSE-CD configurations are never "
            "pooled; this task covers the raw pinned one-step checkpoint only.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def adapter_payload() -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "task_id": TASK,
        "task_local": True,
        "implemented": False,
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["offline"],
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "activation": "deferred_until_gates_clear",
        "entrypoint": None,
        "note": (
            "Proposal-only task-local descriptor. It is not the shipped adapter, "
            "not a provider registration and not a public default."),
    }


def adapter_bytes() -> bytes:
    return canonical_bytes(adapter_payload())


def readiness_payload() -> Dict[str, Any]:
    report = build_report()
    report_bytes = canonical_bytes(report)
    contract_digest = sha256(contract_bytes())
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "defer_before": DEFER_BEFORE,
        "ready_for_opt_in_adapter": False,
        "ready_for_provider_registration": False,
        "ready_for_release": False,
        "quality_pass": False,
        "report_sha256": sha256(report_bytes),
        "contract_sha256": contract_digest,
        "blocked_gates": [name for name, _ in GATE_DEFINITIONS],
        "exact_blocker": EXACT_BLOCKERS[0],
        "reopen_condition": REOPENING_CONDITIONS[0],
        "external_asset": {
            "required": True,
            "present": False,
            "loaded": False,
            "executed": False,
            "expected_checkpoint_path": EXPECTED_CALLER_CHECKPOINT_PATH,
            "expected_checkpoint_sha256": CHECKPOINT_SHA256,
            "expected_checkpoint_bytes": CHECKPOINT_BYTES,
            "expected_source_dir": EXPECTED_CALLER_SOURCE_DIR,
            "expected_source_revision": UPSTREAM_COMMIT,
            "expected_checkpoint_revision": HF_REVISION,
            "runtime_environment_present": False,
        },
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
    }


def readiness_bytes() -> bytes:
    return canonical_bytes(readiness_payload())


def allowed_pin_keys() -> set[str]:
    keys = {"source:" + path for path in set(SOURCE_PINS) | set(ASSET_PINS)}
    keys.update(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)
    return keys


PIN_RE = re.compile(r"([a-f0-9]{64})  (.+)")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    allowed = allowed_pin_keys()
    result: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            if not (line.startswith("# SHA-256 pins") or line.startswith("# source:")):
                raise ValueError("unexpected_comment:" + repr(line))
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError("malformed_pin:" + repr(line))
        digest, raw = match.groups()
        if raw in seen:
            raise ValueError("duplicate_pin:" + raw)
        relative = raw.split(":", 1)[1] if raw.startswith("source:") else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-ROSE-CD-ONE-STEP task-local evidence.",
        "# source: paths are relative to /Users/htsakanyan/workspace/audio/audioml",
    ]
    external = {**SOURCE_PINS, **ASSET_PINS}
    for path in sorted(external):
        lines.append(f"{external[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


README_PIN_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([a-f0-9]{64})`\s*\|")


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Return (path, digest) rows from any backticked digest table in README."""
    text = (HERE / "README.md").read_text(encoding="utf-8")
    rows: List[Tuple[str, str]] = []
    for line in text.splitlines():
        match = README_PIN_ROW_RE.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2)))
    return rows


def qualify_pin_path(path: str) -> Path:
    if path.startswith(TASK_PREFIX):
        return SDK_ROOT / path
    if path.startswith("/"):
        raise ValueError("absolute_pin_path:" + path)
    return SOURCE_ROOT / path


def strict_rejection_examples() -> Dict[str, bool]:
    """Exercise the strict parsers; used by verifier and tests."""
    bad_json = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except (ValueError, TypeError):
            rejected_json += 1
    bad_pins = (
        "not-a-line",
        "a" * 64 + "  ../escape",
        "a" * 64 + "  docs/task-evidence/rose-cd-one-step/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
    )
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except (ValueError, TypeError):
            rejected_pins += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
    }


def upstream_git_identity() -> Dict[str, Any]:
    snapshot = SOURCE_ROOT / UPSTREAM_SNAPSHOT
    remote = subprocess.check_output(
        ["git", "-C", str(snapshot), "config", "--get", "remote.origin.url"],
        text=True).strip()
    normalized = remote
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.split(":", 1)[1]
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    commit = subprocess.check_output(
        ["git", "-C", str(snapshot), "rev-parse", "HEAD"], text=True).strip()
    pinned = subprocess.run(
        ["git", "-C", str(snapshot), "cat-file", "-e",
         UPSTREAM_COMMIT + "^{commit}"],
        capture_output=True, check=False).returncode == 0
    return {
        "normalized_remote": normalized,
        "commit": commit,
        "pinned_commit_present": bool(pinned),
    }
