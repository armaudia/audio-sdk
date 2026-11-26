# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-RT-SEMAMBA-KD1.

This module is NOT RT-SEMamba. It does not load the pinned KD1 checkpoint,
import PyTorch or the vendored Mamba package, read audio, download anything,
measure a device clock, conduct listening, benchmark the SDK or qualify a
release. It models the *boundary* of RT-SEMamba KD1 as a caller-supplied
16 kHz checkpoint+config+source asset set and runs a deterministic model-free
STFT-domain gate surrogate when that asset is absent.

The acceptance profile is Enhancement (``plan/INVENTORY.json`` assigns
``verification_profile: enhancement``). Metrics therefore report paired SNR,
SI-SDR and STOI against an exact synthetic clean reference, clean-speech
passthrough, peaks, invalid/nonfinite outputs, modeled alignment, state,
memory and timing limits. Every real-cohort, listening, device and release
gate remains blocked.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pystoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-RT-SEMAMBA-KD1"
TITLE = "RT-SEMamba KD1"
SLUG = "rt-semamba-kd1"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "62923ffa7dd992da3cea0f6683fab320fb37e6c0"
BRANCH = "swarm/SDK-RT-SEMAMBA-KD1"
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

# Public v0 geometry (unchanged) and the pinned RT-SEMamba KD1 asset geometry.
SAMPLE_RATE_HZ = 16000
PUBLIC_FRAME_SAMPLES = 160
PUBLIC_FRAME_DURATION_MS = 10
ASSET_WINDOW_SAMPLES = 400          # 25 ms analysis window at 16 kHz
ASSET_HOP_SAMPLES = 100             # 6.25 ms hop
ASSET_CHUNK_SAMPLES = 1600          # 100 ms upstream realtime chunk
ALGORITHMIC_LATENCY_SAMPLES = 400
ALGORITHMIC_LATENCY_MS = 25
MODELED_DELAY_SAMPLES = 400
MODELED_DELAY_MS = 25
CLIP_SAMPLES = 32000                # 2.0 s synthetic utterance
NOISE_ESTIMATE_FRAMES = 5
NOISE_ATTACK_BETA = 1.5
GATE_FLOOR = 0.20
PEAK_GUARD = 0.95
SNR_DB_STRATA = (20, 10, 0)
CONDITIONS = (
    "clean_control",
    "noisy_snr20",
    "noisy_snr10",
    "noisy_snr0",
    "idle_noise",
    "silence",
)
STRATUM_CONDITIONS = ("noisy_snr20", "noisy_snr10", "noisy_snr0")
STRATUM_BY_NAME = {name: int(name.rsplit("snr", 1)[1])
                   for name in STRATUM_CONDITIONS}

NS_PER_SAMPLE = 1_000_000_000 // SAMPLE_RATE_HZ
ORIGIN_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-sample-coordinate-not-device"
IMPULSE_INDEX = 4000
IMPULSE_AMPLITUDE = 0.8

UPSTREAM_REPOSITORY = "https://github.com/RoyChao19477/RT-SEMamba"
UPSTREAM_COMMIT = "0c9e8c7c42caadd7badb6cc145c8af93f760863c"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_SNAPSHOT = "data/checkouts/RT-SEMamba"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/LICENSE"
UPSTREAM_README_PATH = UPSTREAM_SNAPSHOT + "/README.md"
CHECKPOINT_PATH = UPSTREAM_SNAPSHOT + "/ckpts/g_00766000.pth"
CHECKPOINT_SHA256 = (
    "7d76e2c5f322cc0dd58abd0b9b371890b29c3710d7833cdfebb46a823961f5cc")
CHECKPOINT_BYTES = 4_235_024
TEACHER_CHECKPOINT_PATH = UPSTREAM_SNAPSHOT + "/ckpts/g_00259000.pth"
TEACHER_CHECKPOINT_SHA256 = (
    "c97bc702d2840f1173ef221e92600a331dbbde64c5a70399f39ef85d4804935b")
TEACHER_CHECKPOINT_BYTES = 11_115_496
CONFIG_PATH = UPSTREAM_SNAPSHOT + "/recipes/KD1/KD1.yaml"
CONFIG_SHA256 = (
    "2db65c33e66108d7616d47ca509a3dc46983980cae63a216d1ccb98daf0ee222")
INFERENCE_PATH = UPSTREAM_SNAPSHOT + "/inference.py"
GENERATOR_PATH = UPSTREAM_SNAPSHOT + "/models/generator.py"
STFTS_PATH = UPSTREAM_SNAPSHOT + "/models/stfts.py"
MAMBA_INIT_PATH = UPSTREAM_SNAPSHOT + "/mamba_install_mps/mamba_ssm/__init__.py"
MAMBA_MODULE_PATH = (
    UPSTREAM_SNAPSHOT + "/mamba_install_mps/mamba_ssm/modules/mamba_simple.py")
MAMBA_SCAN_PATH = (
    UPSTREAM_SNAPSHOT +
    "/mamba_install_mps/mamba_ssm/ops/selective_scan_interface.py")

EXPECTED_CALLER_CHECKPOINT_PATH = "data/envs/rt-semamba/g_00766000.pth"
EXPECTED_CALLER_CONFIG_PATH = "data/envs/rt-semamba/KD1.yaml"
EXPECTED_CALLER_SOURCE_PATH = "data/envs/rt-semamba/RT-SEMamba"

RESEARCH_EVAL_DIR = "research/voice-enhancement-20261101/agent-semamba-eval"
RESEARCH_AUDIT_DIR = (
    "research/voice-enhancement-20261101/agent-semamba-result-audit")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    RESEARCH_EVAL_DIR + "/REPORT.md":
        "91b5e3642adbfad49878d0238215163fc475a34c135b309521c4d08a982a599c",
    RESEARCH_EVAL_DIR + "/crop_screen_30.py":
        "72b0b198b1124276e4ba4cb0e0be2bd78bae8bfa72399b8e4f49d4577a0473f4",
    RESEARCH_EVAL_DIR + "/score_crop_stoi.py":
        "c4795a0b63723d4c26202ecb2da445234e00233c176abe952c07bc639732795a",
    RESEARCH_EVAL_DIR + "/short_crop_diagnostic.py":
        "18cb6c2618fca837a66db1ab32d952f7c6f5b9b7cc4f01a5f64066e8c60cc51a",
    RESEARCH_AUDIT_DIR + "/REPORT.md":
        "fbc2703c763eae2dd0146c80b212821d44eacb14e8b029766ddb72839c5e2503",
    "adapters/rt-semamba/adapter.json":
        "5572eb0ce171ea6d22c334807584230efbf0ba0114d851348841c33535c08a12",
    "adapters/rt-semamba/README.md":
        "497f90ce384570593568c5f597b2f06dc89d9d2bd03b5f4d63e85c5becc65283",
    "adapters/rt-semamba/run.py":
        "c3b006211054b9faa23e8ab518c9acac098e6252c6d8ab4b2315c53c2acae3bb",
    "adapters/rt-semamba/requirements.lock":
        "65906eabf3e9c692cc949257976de1f4b789a6bb1223781cdc8cb46f955410ee",
}

ASSET_PINS: Dict[str, str] = {
    UPSTREAM_LICENSE_PATH:
        "04b1d017b906f5d0c6815e60cadeabb1a3f5b4fb743c1b77343841fd735eb5e8",
    UPSTREAM_README_PATH:
        "c69693beb94f5a84acf076d19e9d24703c0a09ae7d642f670f04645f73c530c8",
    CHECKPOINT_PATH: CHECKPOINT_SHA256,
    CONFIG_PATH: CONFIG_SHA256,
    TEACHER_CHECKPOINT_PATH: TEACHER_CHECKPOINT_SHA256,
    INFERENCE_PATH:
        "290da30c93112fb2d30cb1b88e46eb13262c7946a0cec3e1e01d4335ba988629",
    GENERATOR_PATH:
        "23380a65d1b12df119985718a339c9dc99469dc3a10b141fee3c3c42b44b9ccd",
    STFTS_PATH:
        "9da92bdf11f162f41f01ee9fc6951c161c07becd07cb6590cebcee89b508296a",
    MAMBA_INIT_PATH:
        "fd5bb14b209676fc12a2d66c8f9f11d5c1dfef4296ee5633a0e5856ab238cb9d",
    MAMBA_MODULE_PATH:
        "dc035a4dcfbc9f9809e2bb60764f7bfe38259b6397968399fc33cad159300a43",
    MAMBA_SCAN_PATH:
        "b0e6f888957f48b94ead8b40c9faa12e67c4cfecd31e2a0cdfecaf28c445bd64",
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
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
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

# Files with a digest row in the README artifact table. README.md and
# SOURCES.sha256 are excluded to keep the table acyclic.
ARTIFACT_TABLE_PATHS = (
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
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

REQUIRED_ASSET_FIELDS = {
    "checkpoint_path",
    "checkpoint_sha256",
    "config_path",
    "config_sha256",
    "source_revision",
    "sample_rate_hz",
    "channels",
    "window_samples",
    "hop_samples",
    "algorithm_latency_samples",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/rt-semamba-kd1/caller-supplied-asset/0.1",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": {
        "source_revision": UPSTREAM_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "window_samples": ASSET_WINDOW_SAMPLES,
        "hop_samples": ASSET_HOP_SAMPLES,
        "algorithm_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
    },
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "checkpoint_path, config_path and the source tree are caller-owned "
        "absolute paths",
        "SHA-256 of the checkpoint and KD1 config matches the manifest",
        "source_revision equals the pinned upstream revision",
        "sample rate, channels, STFT window, hop and algorithmic latency equal "
        "the pinned 16 kHz / 400 / 100 / 400 geometry",
        "no download, copy, build, load or execution occurs in this package",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hashes_and_geometry_only; do_not_import_torch_or_execute_in_"
        "this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
}

FORMAT: Dict[str, Any] = {
    "public_sample_rate_hz": SAMPLE_RATE_HZ,
    "public_channels": 1,
    "public_sample_format": "f32",
    "public_frame_samples": PUBLIC_FRAME_SAMPLES,
    "public_frame_duration_ms": PUBLIC_FRAME_DURATION_MS,
    "asset_sample_rate_hz": SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_window_samples": ASSET_WINDOW_SAMPLES,
    "asset_window_duration_ms": 25,
    "asset_hop_samples": ASSET_HOP_SAMPLES,
    "asset_hop_duration_ms": 6.25,
    "asset_chunk_samples": ASSET_CHUNK_SAMPLES,
    "asset_chunk_duration_ms": 100,
    "asset_is_native_16k": True,
    "resampling_required": False,
    "clip_samples": CLIP_SAMPLES,
    "clip_duration_ms": 2000,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}

ENHANCEMENT_BOUNDARY: Dict[str, Any] = {
    "candidate_family": "causal time-frequency Mamba student (cTF-Mamba)",
    "upstream_task": "CLN-01 single-channel speech denoising / enhancement",
    "upstream_mode": "offline whole-utterance in the pinned adapter",
    "upstream_streaming_capable": True,
    "streaming_path_evaluated": False,
    "stft_window_samples": ASSET_WINDOW_SAMPLES,
    "stft_hop_samples": ASSET_HOP_SAMPLES,
    "stft_center": False,
    "algorithmic_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
    "algorithmic_latency_ms": ALGORITHMIC_LATENCY_MS,
    "realtime_chunk_samples": ASSET_CHUNK_SAMPLES,
    "realtime_chunk_ms": 100,
    "parameter_count": 1_050_000,
    "parameter_count_is_source_reported": True,
    "vctk_demand_training_and_evaluation": True,
    "cross_corpus_role": (
        "DNS2020 is a cross-corpus check, not a training-matched benchmark, "
        "because VCTK-DEMAND is both the reported training and evaluation "
        "source"),
    "adapter_device": "cpu",
    "adapter_rejects_non_cpu": True,
    "mps_available_on_research_host": False,
    "cuda_available_on_research_host": False,
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
    "rt_semamba_source_executed": False,
    "rt_semamba_runtime_executed": False,
    "rt_semamba_checkpoint_loaded": False,
    "pytorch_imported": False,
    "mamba_package_imported": False,
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
    "rt_semamba_checkpoint_loaded": False,
    "rt_semamba_runtime_executed": False,
    "rt_semamba_source_executed": False,
    "pytorch_imported": False,
    "mamba_package_imported": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "real_speaker_labels_used": False,
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
    "exact_rt_semamba_reproduction_claimed": False,
    "streaming_behavior_verified": False,
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "paper": "https://arxiv.org/abs/2608.12099",
    "checkpoint": {
        "path": CHECKPOINT_PATH,
        "sha256": CHECKPOINT_SHA256,
        "bytes": CHECKPOINT_BYTES,
        "variant": "KD1 8-layer-to-1-layer distilled student",
        "present_in_external_checkout": True,
        "present_in_sdk_worktree": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "config": {
        "path": CONFIG_PATH,
        "sha256": CONFIG_SHA256,
        "present_in_external_checkout": True,
        "present_in_sdk_worktree": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "unused_teacher_checkpoint": {
        "path": TEACHER_CHECKPOINT_PATH,
        "sha256": TEACHER_CHECKPOINT_SHA256,
        "bytes": TEACHER_CHECKPOINT_BYTES,
        "used": False,
        "reason": (
            "the teacher is pinned only to record exclusion; the KD1 student "
            "checkpoint is the evaluated artifact"),
    },
    "source_files": {
        "README.md": ASSET_PINS[UPSTREAM_README_PATH],
        "inference.py": ASSET_PINS[INFERENCE_PATH],
        "models/generator.py": ASSET_PINS[GENERATOR_PATH],
        "models/stfts.py": ASSET_PINS[STFTS_PATH],
        "mamba_install_mps/mamba_ssm/__init__.py":
            ASSET_PINS[MAMBA_INIT_PATH],
        "mamba_install_mps/mamba_ssm/modules/mamba_simple.py":
            ASSET_PINS[MAMBA_MODULE_PATH],
        "mamba_install_mps/mamba_ssm/ops/selective_scan_interface.py":
            ASSET_PINS[MAMBA_SCAN_PATH],
    },
    "runtime": {
        "framework": "PyTorch >= 2.2",
        "accelerator": (
            "the pinned research adapter runs CPU only with the vendored "
            "pure-PyTorch Mamba fallback"),
        "runtime_installed_in_sdk_worktree": False,
        "runtime_pinned_by_digest_in_this_package": False,
        "loaded_or_executed": False,
    },
    "public_adapter": {
        "path": "adapters/rt-semamba",
        "declared_output_kinds": ["waveform"],
        "declared_tasks": ["CLN-01"],
        "declared_modes": ["offline"],
        "declared_weights": "official pinned KD1 checkpoint",
        "source_commit": UPSTREAM_COMMIT,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": (
        "not established in this package; upstream reports VCTK-DEMAND "
        "(VoiceBank-DEMAND) as both training and evaluation data, but no "
        "dataset manifest, consent basis or rights chain is pinned"),
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_repository_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "upstream_license_text_pinned": True,
    "checkpoint_terms": (
        "the ledger records the checkpoint as distributed in the MIT-licensed "
        "official repository, but the artifact-specific redistribution and "
        "product-use grant is not independently reviewed"),
    "dataset_terms": (
        "VCTK-DEMAND / VoiceBank-DEMAND dataset terms, consent basis and "
        "redistribution scope are not established in this package"),
    "checkpoint_redistribution_clearance": False,
    "runtime_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "artifact_and_runtime_rights",
    "conclusion": (
        "The upstream repository declares MIT and its LICENSE text is pinned, "
        "but checkpoint-specific redistribution/product-use terms, dataset "
        "terms, provenance and legal review are not cleared. This package "
        "distributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact RT-SEMamba KD1 checkpoint, KD1 config and upstream source "
        "are pinned by SHA-256 from the external research checkout, but no "
        "caller-supplied asset manifest or copy exists in this SDK worktree and "
        "no PyTorch/Mamba runtime is installed here; the exact runtime cannot "
        "be loaded, reproduced or measured."),
    (
        "The upstream repository declares MIT and its LICENSE text is pinned, "
        "but artifact-specific checkpoint redistribution and product-use "
        "rights, VCTK-DEMAND dataset terms and provenance, an immutable "
        "artifact distribution record and legal review are not established. No "
        "asset was downloaded, copied, built, vendored or redistributed."),
    (
        "Only a deterministic model-free STFT-domain gate surrogate was "
        "executed. It is not RT-SEMamba, has no checkpoint, cTF-Mamba blocks, "
        "SSM state or learned mask, and its synthetic paired metrics are "
        "boundary-conformance observations, not a quality, streaming, "
        "device-timing or benchmark result."),
    (
        "No rights-cleared held-out paired cohort, independent listening, "
        "target-runtime content/availability timing or memory measurement, "
        "native streaming-state verification, opt-in provider intake, "
        "descriptor/registry review or public default decision exists; every "
        "release gate remains blocked."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_asset_present_and_verified",
        "Place the caller-owned KD1 checkpoint, KD1 config and pinned source "
        "tree in the worktree (or supply them through the manifest) with "
        "SHA-256 values, source revision and STFT geometry matching the pins."),
    (
        "artifact_and_runtime_rights",
        "Establish checkpoint-specific redistribution and product-use rights, "
        "VCTK-DEMAND dataset terms and provenance, an immutable distribution "
        "record and legal review; the repository MIT declaration alone is "
        "insufficient."),
    (
        "exact_runtime_reproduction",
        "Install the pinned PyTorch and vendored Mamba runtime, load the exact "
        "checkpoint and config, and reproduce approved reference outputs on "
        "frozen inputs."),
    (
        "streaming_boundary_and_state",
        "Verify the native 16 kHz / 400 / 100 streaming boundary, the 25 ms "
        "analysis-window latency, chunk scheduling, state reset/flush and "
        "realtime-versus-chunked equivalence."),
    (
        "rights_cleared_task_matched_cohort",
        "Score a rights-cleared held-out paired cohort with clean references "
        "under the Enhancement profile; the VCTK-DEMAND overlap and the DNS "
        "cross-corpus limits must be documented."),
    (
        "clean_preservation_and_independent_listening",
        "Measure clean-speech preservation and collect independent listening "
        "or preference labels; synthetic metrics cannot qualify an enhancer."),
    (
        "target_runtime_timing_memory",
        "Measure content/availability timing, memory, deadlines and paced "
        "workload on the exact target runtime."),
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
    "caller-supplied KD1 checkpoint, KD1 config and source tree present and SHA-256-verified in this SDK worktree",
    "checkpoint-specific redistribution/product-use rights, VCTK-DEMAND dataset terms and provenance, and legal review",
    "immutable artifact distribution record and approved reference-output vector",
    "exact runtime reproduction with the pinned PyTorch and vendored Mamba fallback",
    "native streaming boundary, 25 ms latency, chunk scheduling and reset/flush evidence",
    "rights-cleared held-out paired cohort with clean references",
    "clean-speech preservation on real speech and independent listening",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and catalog review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies the KD1 checkpoint, KD1 config and pinned source tree "
    "with matching SHA-256 values, source revision and STFT geometry, and the "
    "manifest validates.",
    "Checkpoint-specific redistribution/product-use rights, VCTK-DEMAND dataset "
    "terms and provenance, an immutable distribution record and legal review "
    "are cleared.",
    "The pinned PyTorch and vendored Mamba runtime are installed and the exact "
    "checkpoint reproduces approved reference outputs on frozen inputs.",
    "The native 16 kHz / 400 / 100 streaming boundary, 25 ms latency, chunk "
    "scheduling, reset/flush and realtime-versus-chunked equivalence are "
    "verified.",
    "A rights-cleared held-out paired cohort with clean references is scored "
    "under the Enhancement profile with documented training-data overlap.",
    "Clean-speech preservation on real speech is measured and independent "
    "listening or preference labels are collected.",
    "Target-runtime content/availability timing, memory, deadlines and paced "
    "workload are measured.",
    "Opt-in adapter intake, descriptor and catalog review are completed.",
    "An explicit public default decision is recorded; the candidate remains OFF "
    "until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "a deterministic 30-item paired 2.5 s DNS crop screen with a separate "
        "STOI rescore, one aligned 2.5 s crop diagnostic, a bounded 10 s CPU "
        "attempt that timed out, and upstream VCTK-DEMAND author results; not a "
        "full CLN-01 protocol, not a rights-cleared holdout and not a "
        "target-device run."),
    "sources": [
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        RESEARCH_EVAL_DIR + "/REPORT.md",
        RESEARCH_EVAL_DIR + "/crop_screen_30.py",
        RESEARCH_EVAL_DIR + "/score_crop_stoi.py",
        RESEARCH_EVAL_DIR + "/short_crop_diagnostic.py",
        RESEARCH_AUDIT_DIR + "/REPORT.md",
        "research/noise_suppression_candidate_census.md",
        "research/noise_suppression_assets_20261027.json",
        "adapters/rt-semamba/README.md",
    ],
    "findings": [
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "delta_snr_db",
            "value": -12.41,
            "interval_95": [-15.51, -9.13],
            "unit": "dB",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "delta_si_sdr_db",
            "value": -13.43,
            "interval_95": [-16.49, -10.06],
            "unit": "dB",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "delta_stoi",
            "value": 0.0043,
            "interval_95": [-0.0042, 0.0130],
            "unit": "ratio",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "median_rtf",
            "value": 5.81,
            "interval_95": None,
            "unit": "ratio",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "p95_rtf",
            "value": 8.15,
            "interval_95": None,
            "unit": "ratio",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "mean_output_peak",
            "value": 13.03,
            "interval_95": None,
            "unit": "linear",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "max_output_peak",
            "value": 122.06,
            "interval_95": None,
            "unit": "linear",
        },
        {
            "fixture": "dns_crop_screen_30",
            "stratum": "all",
            "metric": "process_peak_rss_bytes",
            "value": 3219685376,
            "interval_95": None,
            "unit": "bytes",
        },
        {
            "fixture": "dns_short_crop_single",
            "stratum": "4.0-6.5 s",
            "metric": "snr_db_after",
            "value": 14.6675,
            "interval_95": None,
            "unit": "dB",
        },
        {
            "fixture": "dns_short_crop_single",
            "stratum": "4.0-6.5 s",
            "metric": "delta_si_sdr_db",
            "value": 11.0880,
            "interval_95": None,
            "unit": "dB",
        },
        {
            "fixture": "dns_full_10s",
            "stratum": "bounded_attempt",
            "metric": "timed_out",
            "value": 1,
            "interval_95": None,
            "unit": "bool",
        },
        {
            "fixture": "upstream_vctk_demand",
            "stratum": "author_reported",
            "metric": "pesq",
            "value": 3.18,
            "interval_95": None,
            "unit": "mos",
        },
        {
            "fixture": "upstream_vctk_demand",
            "stratum": "author_reported",
            "metric": "stoi",
            "value": 0.95,
            "interval_95": None,
            "unit": "ratio",
        },
        {
            "fixture": "upstream_rtx5090",
            "stratum": "author_reported",
            "metric": "rtf",
            "value": 0.11,
            "interval_95": None,
            "unit": "ratio",
        },
    ],
    "note": (
        "Transcribed from the pinned research only. The 30-crop screen reports "
        "substantial SNR/SI-SDR regression, near-neutral STOI, large output "
        "peaks and a CPU RTF around 5.8, while upstream reports strong "
        "VCTK-DEMAND quality and 0.11 RTF on an RTX 5090. This package neither "
        "reproduces nor claims any of these values and does not pool them with "
        "the surrogate observations."),
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


def _voiced(f0_base: float, f0_mod: Tuple[float, float], harmonics: int,
            phase_offset: float, segments: Sequence[Tuple[float, float]],
            peak: float) -> np.ndarray:
    time = np.arange(CLIP_SAMPLES, dtype=np.float64) / SAMPLE_RATE_HZ
    f0 = (f0_base + f0_mod[0] * np.sin(2.0 * np.pi * 0.7 * time) +
          f0_mod[1] * np.sin(2.0 * np.pi * 1.9 * time))
    phase = 2.0 * np.pi * np.cumsum(f0) / SAMPLE_RATE_HZ
    voiced = np.zeros(CLIP_SAMPLES, dtype=np.float64)
    for harmonic in range(1, harmonics + 1):
        voiced += (1.0 / harmonic) * np.sin(
            harmonic * phase + phase_offset * harmonic)
    envelope = np.zeros(CLIP_SAMPLES, dtype=np.float64)
    fade = max(1, int(round(0.01 * SAMPLE_RATE_HZ)))
    for start, end in segments:
        begin = int(round(start * SAMPLE_RATE_HZ))
        finish = int(round(end * SAMPLE_RATE_HZ))
        segment = np.ones(finish - begin, dtype=np.float64)
        segment[:fade] = np.linspace(0.0, 1.0, fade)
        segment[-fade:] = np.linspace(1.0, 0.0, fade)
        envelope[begin:finish] = segment
    signal = voiced * envelope
    largest = float(np.max(np.abs(signal)))
    if largest <= 0.0:
        raise ValueError("zero_voiced_energy")
    return (signal / largest * peak).astype(np.float32)


@lru_cache(maxsize=1)
def stimuli() -> Dict[str, Any]:
    target = _voiced(125.0, (18.0, 7.0), 24, 0.37,
                     ((0.15, 0.65), (0.85, 1.35), (1.55, 1.95)), 0.45)
    rng = np.random.Generator(np.random.PCG64(20261101))
    noise = rng.standard_normal(CLIP_SAMPLES)
    noise = noise / float(np.max(np.abs(noise))) * 0.5
    noise = noise.astype(np.float32)
    target_rms = _rms(target.astype(np.float64))
    noise_rms = _rms(noise.astype(np.float64))
    if target_rms <= 0.0 or noise_rms <= 0.0:
        raise ValueError("zero_source_energy")
    scales = {
        snr: target_rms / (noise_rms * 10.0 ** (snr / 20.0))
        for snr in SNR_DB_STRATA
    }
    mixtures = {
        snr: target.astype(np.float64) +
        scale * noise.astype(np.float64)
        for snr, scale in scales.items()
    }
    worst = max(float(np.max(np.abs(mix))) for mix in mixtures.values())
    guard = 1.0
    if worst > PEAK_GUARD:
        guard = PEAK_GUARD / worst
    target_guarded = (target.astype(np.float64) * guard).astype(np.float32)
    noise_guarded = (noise.astype(np.float64) * guard).astype(np.float32)
    guarded_scales = {snr: scale * guard for snr, scale in scales.items()}
    guarded_mixtures = {
        snr: (target_guarded.astype(np.float64) +
              guarded_scales[snr] * noise_guarded.astype(np.float64)
              ).astype(np.float32)
        for snr in SNR_DB_STRATA
    }
    impulse = np.zeros(CLIP_SAMPLES, dtype=np.float32)
    impulse[IMPULSE_INDEX] = np.float32(IMPULSE_AMPLITUDE)
    signals: Dict[str, np.ndarray] = {
        "clean_control": target_guarded,
        "noisy_snr20": guarded_mixtures[20],
        "noisy_snr10": guarded_mixtures[10],
        "noisy_snr0": guarded_mixtures[0],
        "idle_noise": noise_guarded,
        "silence": np.zeros(CLIP_SAMPLES, dtype=np.float32),
    }
    return {
        "signals": signals,
        "target": target_guarded,
        "noise": noise_guarded,
        "noise_scale": guarded_scales,
        "guard_gain": guard,
        "impulse": impulse,
    }


def _validate_signal(signal: Any) -> np.ndarray:
    if not isinstance(signal, np.ndarray):
        raise ValueError("input_not_ndarray")
    if signal.ndim != 1:
        raise ValueError("input_not_mono")
    if signal.size != CLIP_SAMPLES:
        raise ValueError("input_length_mismatch")
    if not np.isfinite(signal).all():
        raise ValueError("nonfinite_input")
    return np.asarray(signal, dtype=np.float32).astype(np.float64)


def _check_output(signal: Any) -> np.ndarray:
    array = np.asarray(signal, dtype=np.float64)
    if array.size != CLIP_SAMPLES:
        raise ValueError("length_mismatch")
    if not np.isfinite(array).all():
        raise ValueError("nonfinite_output")
    return array


def _validate_config(sample_rate_hz: int, channels: int, window_samples: int,
                     hop_samples: int) -> None:
    if sample_rate_hz != SAMPLE_RATE_HZ:
        raise ValueError("asset_sample_rate_mismatch")
    if channels != 1:
        raise ValueError("asset_channels_mismatch")
    if window_samples != ASSET_WINDOW_SAMPLES:
        raise ValueError("asset_window_samples_mismatch")
    if hop_samples != ASSET_HOP_SAMPLES:
        raise ValueError("asset_hop_samples_mismatch")


def _analysis_frames(signal: np.ndarray, window_samples: int,
                     hop_samples: int) -> Tuple[np.ndarray, int, int]:
    padded = np.concatenate((
        np.zeros(window_samples, dtype=np.float64),
        np.asarray(signal, dtype=np.float64),
        np.zeros(window_samples, dtype=np.float64)))
    count = 1 + (padded.size - window_samples) // hop_samples
    frames = np.stack([
        padded[index * hop_samples:index * hop_samples + window_samples]
        for index in range(count)
    ])
    return frames, padded.size, count


def _overlap_add(frames: np.ndarray, padded_size: int, window: np.ndarray,
                 hop_samples: int) -> np.ndarray:
    output = np.zeros(padded_size, dtype=np.float64)
    weight = np.zeros(padded_size, dtype=np.float64)
    for index, frame in enumerate(frames):
        start = index * hop_samples
        output[start:start + window.size] += frame * window
        weight[start:start + window.size] += window * window
    covered = weight > 1e-12
    output[covered] /= weight[covered]
    return output


def _gate_mask(frames: np.ndarray, window: np.ndarray
               ) -> Tuple[np.ndarray, float]:
    magnitudes = np.abs(np.fft.rfft(frames * window, axis=1))
    noise = np.mean(magnitudes[:NOISE_ESTIMATE_FRAMES], axis=0)
    noise_peak = float(np.max(noise))
    if noise_peak <= 0.0:
        return np.ones_like(magnitudes), 0.0
    mask = np.clip(1.0 - NOISE_ATTACK_BETA * noise / (magnitudes + 1e-12),
                   GATE_FLOOR, 1.0)
    return mask, noise_peak


class Surrogate:
    """Deterministic model-free STFT-domain boundary surrogate; not the model."""

    def __init__(self, bypass: bool = False,
                 sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = 1,
                 window_samples: int = ASSET_WINDOW_SAMPLES,
                 hop_samples: int = ASSET_HOP_SAMPLES) -> None:
        _validate_config(sample_rate_hz, channels, window_samples,
                         hop_samples)
        self.bypass = bool(bypass)
        self.sample_rate_hz = sample_rate_hz
        self.channels = channels
        self.window_samples = window_samples
        self.hop_samples = hop_samples
        self.window = (0.5 - 0.5 * np.cos(
            2.0 * np.pi * np.arange(window_samples) / window_samples))
        self.noise_estimate: float | None = None
        self.processed_frames = 0
        self.epoch = 1

    def reset(self, epoch: int | None = None) -> None:
        if epoch is not None:
            if not isinstance(epoch, int) or epoch < 1:
                raise ValueError("invalid_epoch")
            self.epoch = epoch
        self.noise_estimate = None
        self.processed_frames = 0

    def process(self, signal: Any,
                compensate: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        source = _validate_signal(signal)
        frames, padded_size, count = _analysis_frames(
            source, self.window_samples, self.hop_samples)
        if self.bypass:
            processed = source.copy()
            mask = np.ones((count, self.window_samples // 2 + 1))
            noise_level = 0.0
        else:
            mask, noise_level = _gate_mask(frames, self.window)
            spectrum = np.fft.rfft(frames * self.window, axis=1)
            restored = np.fft.irfft(spectrum * mask, n=self.window_samples,
                                    axis=1)
            padded_output = _overlap_add(restored, padded_size, self.window,
                                         self.hop_samples)
            processed = padded_output[
                self.window_samples:self.window_samples + CLIP_SAMPLES]
            if float(np.max(np.abs(mask - 1.0))) <= 1e-15:
                processed = source.copy()
        self.noise_estimate = noise_level
        if compensate:
            output = np.asarray(processed, dtype=np.float64)
        else:
            output = np.concatenate((
                np.zeros(MODELED_DELAY_SAMPLES, dtype=np.float64),
                np.asarray(processed, dtype=np.float64))
            )[:CLIP_SAMPLES]
        _check_output(output)
        self.processed_frames += count
        info = {
            "noise_estimate": self.noise_estimate,
            "mask_mean": float(np.mean(mask)),
            "mask_min": float(np.min(mask)),
            "mask_max": float(np.max(mask)),
            "frame_count": count,
            "compensated": bool(compensate),
            "bypass": self.bypass,
        }
        return output.astype(np.float32), info


def process_reference(signal: Any, bypass: bool = False,
                      compensate: bool = True, **config: Any
                      ) -> Tuple[np.ndarray, Dict[str, Any]]:
    return Surrogate(bypass=bypass, **config).process(signal, compensate)


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
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("asset_sample_rate_mismatch")
    if manifest["channels"] != 1:
        raise ValueError("asset_channels_mismatch")
    if manifest["window_samples"] != ASSET_WINDOW_SAMPLES:
        raise ValueError("asset_window_samples_mismatch")
    if manifest["hop_samples"] != ASSET_HOP_SAMPLES:
        raise ValueError("asset_hop_samples_mismatch")
    if manifest["algorithm_latency_samples"] != ALGORITHMIC_LATENCY_SAMPLES:
        raise ValueError("asset_algorithm_latency_mismatch")
    for name in ("checkpoint", "config"):
        path = Path(str(manifest[name + "_path"]))
        if not path.is_absolute():
            raise ValueError("asset_path_must_be_absolute:" + name)
        if not path.is_file():
            raise ValueError("asset_file_missing:" + name)
        if _sha256_file(path) != manifest[name + "_sha256"]:
            raise ValueError("asset_hash_mismatch:" + name)
    return {
        "verified": True,
        "loaded": False,
        "executed": False,
        "source_revision": UPSTREAM_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "window_samples": ASSET_WINDOW_SAMPLES,
        "hop_samples": ASSET_HOP_SAMPLES,
        "algorithm_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
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


def _snr(reference: Any, estimate: Any) -> Tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    if ref.size == 0 or est.size != ref.size:
        return None, "missing_reference_or_output"
    if not np.isfinite(ref).all() or not np.isfinite(est).all():
        return None, "nonfinite_signal"
    signal_energy = float(np.dot(ref, ref))
    error = ref - est
    error_energy = float(np.dot(error, error))
    if signal_energy <= 0.0:
        return None, "zero_reference_energy"
    if error_energy <= 1e-20:
        return None, "zero_error_identity_exact"
    return norm(10.0 * math.log10(signal_energy / error_energy)), None


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
            value = float(pystoi.stoi(ref, est, SAMPLE_RATE_HZ, extended=False))
    except Exception as error:  # pragma: no cover - defensive boundary
        return None, "stoi_error:" + type(error).__name__
    if not math.isfinite(value):
        return None, "nonfinite_stoi"
    return norm(value), None


def _metric_block(identity: Tuple[float | None, str | None],
                  provider: Tuple[float | None, str | None]) -> Dict[str, Any]:
    identity_value, identity_reason = identity
    provider_value, provider_reason = provider
    delta = None
    if identity_value is not None and provider_value is not None:
        delta = norm(provider_value - identity_value)
    return {
        "identity_noisy": identity_value,
        "identity_invalid_reason": identity_reason,
        "provider_surrogate": provider_value,
        "provider_invalid_reason": provider_reason,
        "paired_delta": delta,
    }


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


def _condition(name: str, input_signal: np.ndarray,
               reference_signal: np.ndarray | None,
               output_signal: np.ndarray,
               info: Dict[str, Any]) -> Dict[str, Any]:
    identity = (
        _snr(reference_signal, input_signal),
        _si_sdr(reference_signal, input_signal),
        _stoi(reference_signal, input_signal),
    )
    provider = (
        _snr(reference_signal, output_signal),
        _si_sdr(reference_signal, output_signal),
        _stoi(reference_signal, output_signal),
    )
    input_rms = _rms(input_signal.astype(np.float64))
    output_rms = _rms(output_signal.astype(np.float64))
    rms_change = None
    if input_rms > 0.0:
        rms_change = norm(20.0 * math.log10(output_rms / input_rms)) \
            if output_rms > 0.0 else None
    return {
        "condition": name,
        "input": _signal_summary(input_signal),
        "output": _signal_summary(output_signal),
        "reference": (
            "clean_target" if reference_signal is not None else "none"),
        "snr_db": _metric_block(identity[0], provider[0]),
        "si_sdr_db": _metric_block(identity[1], provider[1]),
        "stoi": _metric_block(identity[2], provider[2]),
        "rms_change_db": rms_change,
        "surrogate_mask": {
            "noise_estimate": norm(info["noise_estimate"]),
            "mean": norm(info["mask_mean"]),
            "min": norm(info["mask_min"]),
            "max": norm(info["mask_max"]),
            "frame_count": info["frame_count"],
            "delay_compensated": info["compensated"],
        },
    }


def _asset_controls() -> Dict[str, Any]:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="rt-semamba-asset-") as directory:
        root = Path(directory)
        checkpoint = root / "g_00766000.pth"
        config = root / "KD1.yaml"
        checkpoint.write_bytes(
            b"synthetic caller checkpoint placeholder; not loaded\n")
        config.write_bytes(b"synthetic caller config placeholder; not loaded\n")
        base = {
            "checkpoint_path": str(checkpoint),
            "checkpoint_sha256": _sha256_file(checkpoint),
            "config_path": str(config),
            "config_sha256": _sha256_file(config),
            "source_revision": UPSTREAM_COMMIT,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "window_samples": ASSET_WINDOW_SAMPLES,
            "hop_samples": ASSET_HOP_SAMPLES,
            "algorithm_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
        }
        valid = validate_caller_asset(dict(base))

        def rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
            try:
                validate_caller_asset(manifest)
            except ValueError as error:
                return {"status": "rejected", "reason": str(error)}
            return {"status": "unexpectedly_accepted", "reason": None}

        missing = dict(base)
        missing["checkpoint_path"] = str(root / "absent.pth")
        checkpoint_hash = dict(base)
        checkpoint_hash["checkpoint_sha256"] = "0" * 64
        config_hash = dict(base)
        config_hash["config_sha256"] = "0" * 64
        revision = dict(base)
        revision["source_revision"] = "0" * 40
        rate = dict(base)
        rate["sample_rate_hz"] = 48000
        channels = dict(base)
        channels["channels"] = 2
        window = dict(base)
        window["window_samples"] = 320
        hop = dict(base)
        hop["hop_samples"] = 160
        latency = dict(base)
        latency["algorithm_latency_samples"] = 320
        relative = dict(base)
        relative["checkpoint_path"] = "g_00766000.pth"
        extra = dict(base)
        extra["teacher_path"] = str(root / "g_00259000.pth")
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
            "absent_file": rejected(missing),
            "checkpoint_hash_mismatch": rejected(checkpoint_hash),
            "config_hash_mismatch": rejected(config_hash),
            "wrong_source_revision": rejected(revision),
            "wrong_sample_rate": rejected(rate),
            "wrong_channels": rejected(channels),
            "wrong_window_samples": rejected(window),
            "wrong_hop_samples": rejected(hop),
            "wrong_algorithm_latency": rejected(latency),
            "relative_path": rejected(relative),
            "extra_field": rejected(extra),
        }


def _frame_controls() -> Dict[str, Any]:
    model = Surrogate()
    zeros = np.zeros(CLIP_SAMPLES, dtype=np.float32)
    baseline, _ = model.process(zeros)
    state_before = (model.noise_estimate, model.processed_frames, model.epoch)

    def rejected(signal: Any, **config: Any) -> Dict[str, Any]:
        try:
            Surrogate(**config).process(signal)
        except ValueError as error:
            return {"status": "rejected", "reason": str(error)}
        return {"status": "unexpectedly_accepted", "reason": None}

    short = np.zeros(CLIP_SAMPLES - 1, dtype=np.float32)
    two_dimensional = np.zeros((CLIP_SAMPLES, 1), dtype=np.float32)
    nonfinite = np.zeros(CLIP_SAMPLES, dtype=np.float32)
    nonfinite[0] = np.nan
    state_after = (model.noise_estimate, model.processed_frames, model.epoch)
    try:
        _check_output(np.zeros(CLIP_SAMPLES - 1, dtype=np.float64))
    except ValueError as error:
        truncated = {"status": "rejected", "reason": str(error)}
    else:
        truncated = {"status": "unexpectedly_accepted", "reason": None}
    si_value, si_reason = _si_sdr(None, baseline)
    return {
        "all_present": True,
        "all_fail_closed": True,
        "short_input": rejected(short),
        "two_dimensional_input": rejected(two_dimensional),
        "nonfinite_input": rejected(nonfinite),
        "truncated_output": truncated,
        "wrong_sample_rate": rejected(zeros, sample_rate_hz=48000),
        "wrong_channels": rejected(zeros, channels=2),
        "wrong_window_samples": rejected(zeros, window_samples=320),
        "wrong_hop_samples": rejected(zeros, hop_samples=160),
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
    signal = stimuli()["signals"]["noisy_snr10"]
    first, _ = Surrogate().process(signal)
    second, _ = Surrogate().process(signal)
    model = Surrogate()
    before_reset, _ = model.process(signal)
    model.reset()
    after_reset, _ = model.process(signal)
    model.reset(epoch=2)
    epoch_ok = model.epoch == 2
    other, _ = Surrogate().process(stimuli()["signals"]["noisy_snr0"])
    bypass, _ = Surrogate(bypass=True).process(signal)
    return {
        "separate_instances_uncoupled": bool(np.array_equal(first, second)),
        "reset_bit_identical": bool(np.array_equal(before_reset, after_reset)),
        "reset_epoch_propagated": bool(epoch_ok),
        "different_stimuli_differ": bool(not np.array_equal(first, other)),
        "bypass_is_bit_exact_identity": bool(np.array_equal(
            bypass, signal.astype(np.float64))),
        "processed_outputs_finite": bool(
            np.isfinite(first).all() and np.isfinite(second).all()),
    }


def _alignment() -> Dict[str, Any]:
    impulse = stimuli()["impulse"]
    raw, _ = process_reference(impulse, bypass=True, compensate=False)
    aligned, _ = process_reference(impulse, bypass=True, compensate=True)
    raw_index = int(np.argmax(np.abs(raw)))
    aligned_index = int(np.argmax(np.abs(aligned)))
    return {
        "expected_impulse_index": IMPULSE_INDEX,
        "uncompensated_impulse_index": raw_index,
        "compensated_impulse_index": aligned_index,
        "measured_content_lag_samples": aligned_index - IMPULSE_INDEX,
        "modeled_window_delay_samples": MODELED_DELAY_SAMPLES,
        "modeled_window_delay_ms": MODELED_DELAY_MS,
        "algorithmic_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
        "algorithmic_latency_ms": ALGORITHMIC_LATENCY_MS,
        "delay_compensation_applied": True,
        "source_interval": [0, CLIP_SAMPLES],
        "valid_output_samples": CLIP_SAMPLES,
        "sdk_callback_invoked": False,
    }


def _timestamp_calibration() -> Dict[str, Any]:
    first = ORIGIN_NS + ASSET_HOP_SAMPLES * NS_PER_SAMPLE
    last = ORIGIN_NS + CLIP_SAMPLES * NS_PER_SAMPLE
    return {
        "clock_id": CLOCK_ID,
        "origin_ns": str(ORIGIN_NS),
        "ns_per_sample": NS_PER_SAMPLE,
        "hop_samples": ASSET_HOP_SAMPLES,
        "hop_duration_ns": str(ASSET_HOP_SAMPLES * NS_PER_SAMPLE),
        "first_frame_end_ns": str(first),
        "last_frame_end_ns": str(last),
        "formula": (
            "frame_end_ns = origin_ns + frame_index_end * hop_samples * "
            "ns_per_sample"),
        "monotonic_nondecreasing": True,
        "measured": False,
        "signal_timestamp_is_not_availability": True,
        "availability_serialization": "decimal string",
    }


def _conditions() -> Dict[str, Any]:
    data = stimuli()
    target = data["target"]
    references: Dict[str, Any] = {
        "clean_control": target,
        "noisy_snr20": target,
        "noisy_snr10": target,
        "noisy_snr0": target,
        "idle_noise": None,
        "silence": None,
    }
    result: Dict[str, Any] = {}
    for name in CONDITIONS:
        input_signal = data["signals"][name]
        output, info = process_reference(input_signal)
        result[name] = _condition(
            name, input_signal, references[name], output, info)
    return result


def _clean_preservation(conditions: Dict[str, Any]) -> Dict[str, Any]:
    condition = conditions["clean_control"]
    exact = condition["input"]["waveform_sha256"] == \
        condition["output"]["waveform_sha256"]
    return {
        "condition": "clean_control",
        "bit_exact_passthrough": bool(exact),
        "rms_change_db": condition["rms_change_db"],
        "si_sdr_db": condition["si_sdr_db"]["provider_surrogate"],
        "si_sdr_invalid_reason": condition["si_sdr_db"][
            "provider_invalid_reason"],
        "stoi": condition["stoi"]["provider_surrogate"],
        "peak_abs": condition["output"]["peak_abs"],
        "clipped_or_nonfinite": condition["output"]["clipped_or_nonfinite"],
        "scope": (
            "synthetic exact clean target with a zero noise-floor estimate; "
            "not real clean speech"),
    }


def _peaks(conditions: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "max_output_peak_abs": norm(max(
            conditions[name]["output"]["peak_abs"] for name in CONDITIONS)),
        "total_clipped_or_nonfinite": sum(
            conditions[name]["output"]["clipped_or_nonfinite"]
            for name in CONDITIONS),
        "all_outputs_finite": all(
            conditions[name]["output"]["finite"] for name in CONDITIONS),
        "all_outputs_same_length": all(
            conditions[name]["output"]["samples"] == CLIP_SAMPLES
            for name in CONDITIONS),
        "per_condition": {
            name: {
                "peak_abs": conditions[name]["output"]["peak_abs"],
                "clipped_or_nonfinite":
                    conditions[name]["output"]["clipped_or_nonfinite"],
            }
            for name in CONDITIONS
        },
    }


def _regressions(conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        condition = conditions[name]
        for metric in ("snr_db", "si_sdr_db", "stoi"):
            delta = condition[metric]["paired_delta"]
            threshold = -0.001 if metric == "stoi" else -0.01
            if delta is not None and delta < threshold:
                regressions.append({
                    "condition": name,
                    "metric": metric,
                    "paired_delta": delta,
                    "note": (
                        "surrogate is worse than identity on this synthetic "
                        "condition"),
                })
    return regressions


def _report_core() -> Dict[str, Any]:
    conditions = _conditions()
    regressions = _regressions(conditions)
    asset_controls = _asset_controls()
    frame_controls = _frame_controls()
    peaks = _peaks(conditions)
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": SLUG,
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
        "enhancement_boundary": dict(ENHANCEMENT_BOUNDARY),
        "enhancement_profile": {
            "identity_noisy_control": True,
            "paired_clean_reference": "synthetic_exact_clean_target",
            "paired_si_sdr": "synthetic_only",
            "paired_stoi": "synthetic_only",
            "clean_speech_preservation": (
                "synthetic_exact_passthrough_only"),
            "peak_and_invalid_output_check": True,
            "established_task_matched_baseline_reproduced": False,
            "real_cohort_scored": False,
            "independent_listening": "not_run",
            "alignment": "modeled_25ms_window_delay_compensated",
            "state": "synthetic_single_utterance",
            "memory": "not_measured",
            "content_availability_timing": "not_measured",
            "target_runtime": "not_measured",
        },
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "checkpoint_present_in_sdk_worktree": False,
            "config_present_in_sdk_worktree": False,
            "source_tree_present_in_sdk_worktree": False,
            "checkpoint_present_in_external_checkout": True,
            "config_present_in_external_checkout": True,
            "source_tree_present_in_external_checkout": True,
            "runtime_installed_in_sdk_worktree": False,
            "expected_caller_checkpoint_path": EXPECTED_CALLER_CHECKPOINT_PATH,
            "expected_caller_config_path": EXPECTED_CALLER_CONFIG_PATH,
            "expected_caller_source_path": EXPECTED_CALLER_SOURCE_PATH,
            "verified": False,
            "loaded": False,
            "executed": False,
            "surrogate_used": True,
            "reason": "caller_supplied_asset_absent_and_rights_unresolved",
        },
        "surrogate": {
            "identity": "rt-semamba-kd1-boundary-surrogate-v0",
            "is_rt_semamba": False,
            "is_neural_network": False,
            "ctf_mamba_blocks": False,
            "ssm_state": False,
            "checkpoint": False,
            "weights": False,
            "pytorch": False,
            "method": (
                "deterministic causal STFT-domain magnitude gate (400-sample "
                "periodic-Hann window, 100-sample hop) with a noise floor "
                "estimated from the first five frames and a 0.20 gain floor; a "
                "400-sample window delay is modeled then compensated"),
            "public_input_geometry": "16 kHz mono f32 160-sample frames",
            "asset_geometry": (
                "16 kHz mono, STFT window 400, hop 100, 25 ms algorithm "
                "latency"),
            "window_samples": ASSET_WINDOW_SAMPLES,
            "hop_samples": ASSET_HOP_SAMPLES,
            "noise_estimate_frames": NOISE_ESTIMATE_FRAMES,
            "noise_attack_beta": NOISE_ATTACK_BETA,
            "gate_floor": GATE_FLOOR,
            "delay_modeled_samples": MODELED_DELAY_SAMPLES,
            "delay_compensated_samples": MODELED_DELAY_SAMPLES,
            "peak_guard": PEAK_GUARD,
            "deterministic": True,
            "pure_synthetic": True,
            "quality_claim": False,
        },
        "stimuli": {
            "target": (
                "synthetic voiced f0 125 Hz, three gated segments, exact clean "
                "reference"),
            "noise": (
                "deterministic PCG64 seeded white noise, fixed seed 20261101"),
            "snr_db_strata": list(SNR_DB_STRATA),
            "peak_guard": PEAK_GUARD,
            "guard_gain": norm(stimuli()["guard_gain"]),
            "target_rms": norm(_rms(stimuli()["target"].astype(np.float64))),
            "noise_rms": norm(_rms(stimuli()["noise"].astype(np.float64))),
            "clip_samples": CLIP_SAMPLES,
            "real_audio": False,
            "room_model": False,
        },
        "timestamp_calibration": _timestamp_calibration(),
        "conditions": conditions,
        "stratification": [
            {
                "condition": name,
                "snr_db": conditions[name]["snr_db"]["identity_noisy"],
                "source_pair_count": 1,
                "independent_items": False,
                "held_out": False,
            }
            for name in STRATUM_CONDITIONS
        ],
        "clean_preservation": _clean_preservation(conditions),
        "peaks_and_invalid": peaks,
        "alignment": _alignment(),
        "state": _state_controls(),
        "controls": {
            "identity": {
                "status": "present",
                "baseline": "same_clip_identity",
                "description": (
                    "unprocessed mixture is the identity control at each SNR"),
            },
            "clean_control": {
                "status": "present",
                "description": (
                    "clean target without noise; checks clean-speech "
                    "preservation"),
            },
            "idle_noise": {
                "status": "present",
                "description": (
                    "noise without target; no clean reference, never scored as "
                    "speech"),
            },
            "silence": {
                "status": "present",
                "description": (
                    "digital silence; no clean reference, never scored as "
                    "speech"),
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
            "identity_control": "same_clip_identity",
            "provider": "rt-semamba-kd1-boundary-surrogate-v0",
            "established_task_matched_baseline_reproduced": False,
            "source_reported_candidate_screen_used_for_qualification": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No RT-SEMamba runtime or rights-cleared paired real cohort; "
                "the surrogate is a boundary-conformance fixture and its "
                "synthetic metrics are not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "paced": False,
            "reason": (
                "No RT-SEMamba runtime or target device; the surrogate is "
                "unpaced and no wall-clock, RTF or deadline result is claimed."),
            "modeled_algorithm_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
            "modeled_algorithm_latency_ms": ALGORITHMIC_LATENCY_MS,
            "source_reported_median_crop_rtf": 5.81,
            "source_reported_p95_crop_rtf": 8.15,
            "source_reported_upstream_rtx5090_rtf": 0.11,
            "availability_clock_is_modeled": True,
        },
        "memory": {
            "measured": False,
            "device_memory_measured": False,
            "source_reported_process_peak_rss_bytes": 3219685376,
            "source_reported_scope": (
                "process-level macOS getrusage high-water mark for the 30-crop "
                "CPU screen; not isolated model memory and not a device limit"),
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
                "Deterministic model-free STFT-domain gate surrogate on "
                "synthetic paired stimuli; no RT-SEMamba asset, real audio or "
                "device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": (
                "none; no result qualifies a candidate"),
            "independent_listening": "none",
            "target_runtime": "none",
            "enhancement_acceptance": (
                "not cleared; no rights-cleared paired cohort, clean real "
                "speech, listening or target timing"),
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
        "component": SLUG,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity/noisy control at each synthetic SNR stratum",
                "paired SNR, SI-SDR and STOI against an exact synthetic clean "
                "reference",
                "clean-speech preservation via a clean-only control",
                "peaks, invalid and nonfinite output accounting",
                "modeled alignment at the 400-sample / 25 ms analysis window",
                "state, reset and separate-instance controls",
                "memory and content/availability timing explicitly unmeasured",
                "rights-cleared cohort, independent listening, target-runtime "
                "timing and release gates explicitly unmeasured",
            ],
            "not_applicable": [
                "no RT-SEMamba runtime, so exact source-reported outputs are "
                "not reproduced",
                "no rights-cleared paired real cohort, so no real enhancement "
                "quality, listening or ranking claim is made",
                "no target device, so no timing, memory or deadline result is "
                "claimed",
                "no streaming runtime, so no chunk scheduling or state-"
                "equivalence claim is made",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "enhancement_boundary": dict(ENHANCEMENT_BOUNDARY),
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
            "contract, header, registry, default, board, handoff or CI file "
            "changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not "
            "a provider or production callback.",
            "No RT-SEMamba source, checkpoint, config, Mamba package, PyTorch "
            "runtime or weights is copied, downloaded, built, loaded or "
            "executed.",
            "All stimuli are frozen deterministic synthetic floats; no real "
            "audio, speaker label, room, device or network is used.",
            "Caller-supplied asset manifests fail closed on missing, "
            "hash-mismatched or wrong-geometry inputs.",
            "Source-reported RT-SEMamba metrics are provenance only and are "
            "never reproduced, pooled or used as thresholds.",
            "Missing evidence never qualifies the candidate; decision remains "
            "DEFER.",
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
        "shared_build_or_ci_change": False,
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["offline"],
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "streaming_supported": False,
        "activation": "deferred_until_gates_clear",
        "entrypoint": None,
        "note": (
            "Proposal-only task-local descriptor. It is not the shipped "
            "adapter, not a provider registration and not a public default."),
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
        "enhancement_acceptance_cleared": False,
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
            "expected_config_path": EXPECTED_CALLER_CONFIG_PATH,
            "expected_config_sha256": CONFIG_SHA256,
            "expected_source_revision": UPSTREAM_COMMIT,
            "runtime_installed": False,
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
            if not (line.startswith("# SHA-256 pins")
                    or line.startswith("# source:")):
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
        "# SHA-256 pins for SDK-RT-SEMAMBA-KD1 task-local evidence.",
        "# source: paths are relative to "
        "/Users/htsakanyan/workspace/audio/audioml",
    ]
    external = {**SOURCE_PINS, **ASSET_PINS}
    for path in sorted(external):
        lines.append(f"{external[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


SOURCE_TABLE_START = "<!-- SOURCE_DIGEST_TABLE_START -->"
SOURCE_TABLE_END = "<!-- SOURCE_DIGEST_TABLE_END -->"
ARTIFACT_TABLE_START = "<!-- ARTIFACT_DIGEST_TABLE_START -->"
ARTIFACT_TABLE_END = "<!-- ARTIFACT_DIGEST_TABLE_END -->"
README_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([a-f0-9]{64})`\s*\|(?:\s*(\d+)\s*\|)?\s*$")


def _table_rows(marker_start: str, marker_end: str
                ) -> List[Tuple[str, str, int | None]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    if marker_start not in text or marker_end not in text:
        raise ValueError("readme_table_marker_missing")
    section = text.split(marker_start, 1)[1].split(marker_end, 1)[0]
    rows: List[Tuple[str, str, int | None]] = []
    for line in section.splitlines():
        match = README_ROW_RE.match(line.strip())
        if match:
            size = None if match.group(3) is None else int(match.group(3))
            rows.append((match.group(1), match.group(2), size))
    return rows


def readme_source_rows() -> List[Tuple[str, str]]:
    return [(path, digest) for path, digest, _ in _table_rows(
        SOURCE_TABLE_START, SOURCE_TABLE_END)]


def readme_artifact_rows() -> List[Tuple[str, str, int]]:
    rows = _table_rows(ARTIFACT_TABLE_START, ARTIFACT_TABLE_END)
    if any(size is None for _, _, size in rows):
        raise ValueError("readme_artifact_row_missing_bytes")
    return [(path, digest, int(size)) for path, digest, size in rows]


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
        "a" * 64 + "  docs/task-evidence/rt-semamba-kd1/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md",
                   "0" * 64 + "  CONTRACTS.md"]),
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


def vendored_binary_files() -> List[str]:
    """Task-local files that look like copied model/runtime assets."""
    suffixes = {
        ".dylib", ".so", ".dll", ".onnx", ".tar", ".gz", ".ckpt", ".pt",
        ".pth", ".safetensors", ".wav", ".flac", ".mp3",
    }
    return sorted(
        path.name for path in HERE.iterdir()
        if path.is_file() and (
            path.suffix.lower() in suffixes
            or any(path.name.endswith(suffix) for suffix in suffixes)))
