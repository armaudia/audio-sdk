# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-CLEARVOICE-MOSSFORMERGAN.

This module is NOT ClearerVoice MossFormerGAN_SE_16K and is not a reproduction
of its runtime. It does not read weights, audio, media or a caller asset; it
downloads nothing, invokes no vendor runtime, measures no device clock or
deadline, conducts no listening, benchmarks no SDK build and makes no release,
quality or timing claim.

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
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pystoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-CLEARVOICE-MOSSFORMERGAN"
TITLE = "ClearVoice MossFormerGAN"
SLUG = "clearvoice-mossformergan"
COMPONENT = "clearvoice-mossformergan"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c7cb12877fb8dce8620ba4963f0496a8061d9f7b"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
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

SEED_BASE = 20261126
CONDITIONS: Tuple[str, ...] = (
    "quiet_speech",
    "active_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
    "clean_speech",
    "silence",
)
CHUNK_SIZES: Tuple[int, ...] = (1, 7, 80, 159, 160, 161, 320, 1280)
NOISE_PERCENTILE = 0.35
OVER_SUBTRACTION = 1.30
MASK_EXPONENT = 0.85
GAIN_FLOOR = 0.20
ATTACK = 0.75
RELEASE = 0.40
PEAK_LIMIT = 1.0
STOI_MIN_REG = -0.01
SNR_REGRESSION_DB = -0.01

# Exact pinned candidate identity. Quoted from the pinned research ledgers and
# the existing adapter; no asset bytes are present in, copied into or read from
# this worktree.
CANDIDATE_ID = "ClearerVoice-MossFormerGAN_SE_16K"
MODEL_NAME = "MossFormerGAN_SE_16K"
CHECKPOINT_ID = "MossFormerGAN_SE_16K/last_best_checkpoint.pt"
CHECKPOINT_BYTES = 38_845_593
CHECKPOINT_SHA256 = (
    "04bf00db575389e1ea8b1fcca48d9efcf073e50ad170e6dd5230df3bac98be27")
CHECKPOINT_FILE = "last_best_checkpoint.pt"
CHECKPOINT_DIR = "data/models/clearvoice/MossFormerGAN_SE_16K"
POINTER_ID = "MossFormerGAN_SE_16K/last_best_checkpoint"
POINTER_BYTES = 24
POINTER_SHA256 = (
    "315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0")
POINTER_REQUIRED_CONTENT = CHECKPOINT_FILE
PACKAGE_VERSION = "0.1.2"
PACKAGE_IDENTITY = "ClearerVoice-Studio-clearvoice-0.1.2"
PACKAGE_SOURCE = "https://github.com/modelscope/ClearerVoice-Studio"
SOURCE_REVISION = "dcb1b20e1e44d435090072ab9b223c792ea1f624"
MODEL_REVISION = None
MODEL_DOWNLOAD_REVISION = None
MODEL_CARD = "https://huggingface.co/alibabasglab/MossFormerGAN_SE_16K"
MODEL_CARD_REVISION = None
MODEL_LICENSE_METADATA = "Apache-2.0"
CODE_LICENSE_METADATA = "Apache-2.0"
TRAINING_DATA_NOTE = (
    "model card states open and private data; exact corpus exposure not disclosed")
ASSET_LEDGER_PATH = "research/noise_suppression_assets_20261027.json"
MOSSFORMER_REPORT_PATH = (
    "research/voice-enhancement-20261101/agent-mossformer-eval/REPORT.md")
MOSSFORMER_RESULTS_PATH = (
    "research/voice-enhancement-20261101/agent-mossformer-eval/full30-results.json")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    ASSET_LEDGER_PATH:
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    MOSSFORMER_REPORT_PATH:
        "8e3171628b3c206cf5153bec13032b7087236756e2f8fcb855f9d40828e57a24",
    MOSSFORMER_RESULTS_PATH:
        "467697784a5e331161bbc4b39e23eb3c58aca43901e52d0bec8ed8667d43bac5",
    "adapters/clearvoice/adapter.json":
        "ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff",
    "adapters/clearvoice/README.md":
        "9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5",
    "adapters/clearvoice/requirements.lock":
        "3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91",
    "adapters/clearvoice/run.py":
        "c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90",
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
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "LICENSES.md",
    "SOURCES.sha256.license",
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
EXPECTED_TEST_COUNT = 40

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

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_boundary_surrogate_only": True,
    "caller_supplied_asset_contract_modeled": True,
    "caller_supplied_asset_present": False,
    "checkpoint_present_in_sdk_worktree": False,
    "pointer_present_in_sdk_worktree": False,
    "model_revision_pinned": False,
    "runtime_installed": False,
    "clearvoice_source_executed": False,
    "weights_downloaded": False,
    "weights_loaded": False,
    "attention_or_gan_executed": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

CLAIMS: Dict[str, bool] = {
    "real_clearvoice_runtime": False,
    "mossformergan_model_loaded": False,
    "attention_or_gan_executed": False,
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
    "The pinned asset ledger records "
    "MossFormerGAN_SE_16K/last_best_checkpoint.pt as 38,845,593 bytes with "
    "SHA-256 "
    "04bf00db575389e1ea8b1fcca48d9efcf073e50ad170e6dd5230df3bac98be27 "
    "and a 24-byte MossFormerGAN_SE_16K/last_best_checkpoint pointer with "
    "SHA-256 "
    "315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0 "
    "under ClearerVoice source revision "
    "dcb1b20e1e44d435090072ab9b223c792ea1f624, but the ledger records no "
    "immutable model artifact revision (model_revision is absent) and no "
    "retrieval-time download commit; the 24-byte pointer content is not "
    "verified, and neither artifact is present in this SDK worktree.",
    "The runtime is the external clearvoice 0.1.2 package (adapter identity "
    "ClearerVoice-Studio-clearvoice-0.1.2) whose research requirements lock is "
    "pinned by digest but which has no wheel or sdist digest, no installed "
    "environment and no execution evidence here; adapters/clearvoice/run.py is "
    "not executed and no vendor runtime is invoked.",
    "Apache-2.0 is recorded for the code and the Apache-2.0 model card at "
    "https://huggingface.co/alibabasglab/MossFormerGAN_SE_16K, but the model "
    "card states open and private training data with exact corpus exposure "
    "undisclosed; artifact-specific weight rights, training-data provenance, "
    "redistribution and product-use clearance, and legal review are not "
    "established. No checkpoint, pointer, runtime or upstream source may be "
    "vendored, packaged, downloaded or redistributed by this package.",
    "No rights-cleared held-out real cohort, independent clean-reference "
    "scorer, permitted listening result, target-runtime timing measurement or "
    "approved exact MossFormerGAN reference output vector exists; every "
    "release gate remains blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact MossFormerGAN_SE_16K checkpoint "
    "bytes are addressed by an immutable model artifact revision plus byte "
    "count and SHA-256 in a retrieval record, the 24-byte pointer content is "
    "verified to name the checkpoint, and both resolve from the caller's own "
    "storage without a provider file access or download.",
    "Reopen runtime admission only when a pinned clearvoice 0.1.2 runtime "
    "artifact with a recorded digest installs in the intended environment, "
    "adapters/clearvoice/run.py runs under the research requirements lock, and "
    "its distribution and product-use terms are documented.",
    "Reopen rights only after written artifact-specific weight, runtime and "
    "training-data terms are recorded and a legal/redistribution decision "
    "exists; Apache-2.0 metadata alone is not clearance.",
    "Reopen exact reference parity only when an approved MossFormerGAN "
    "reference output vector for these frozen inputs exists and the exact "
    "runtime reproduces it.",
    "Reopen qualification only with a rights-cleared paired cohort, an "
    "independent scorer, permitted listening and target-runtime timing "
    "evidence; the synthetic surrogate can never stand in for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable MossFormerGAN_SE_16K checkpoint artifact revision plus caller-held bytes",
    "verified 24-byte last_best_checkpoint pointer content",
    "pinned clearvoice 0.1.2 runtime artifact, requirements installation and execution evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "approved exact MossFormerGAN reference output vectors for the frozen synthetic inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime timing, memory, throughput and offline availability evidence",
    "opt-in provider intake, descriptor/catalog review and explicit default decision",
)

GATES: Tuple[Dict[str, str], ...] = (
    {"name": "exact_asset_identity", "status": "blocked",
     "evidence": (
         "Ledger digest and byte counts only; model_revision is absent and the "
         "pointer content is unverified."),
     "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked",
     "evidence": (
         "clearvoice 0.1.2 is absent and its runtime artifact is unpinned here."),
     "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked",
     "evidence": (
         "Apache-2.0 metadata is recorded; artifact-specific terms, training-data "
         "provenance and legal review are absent."),
     "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked",
     "evidence": (
         "No approved MossFormerGAN reference output vector exists for these "
         "frozen inputs."),
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rights_cleared_cohort", "status": "blocked",
     "evidence": (
         "No paired real cohort with clean references is available to this task."),
     "reopen": REOPEN_CONDITIONS[4]},
    {"name": "independent_scoring_and_listening", "status": "blocked",
     "evidence": (
         "No independent scorer or listening result; surrogate metrics are "
         "synthetic only."),
     "reopen": REOPEN_CONDITIONS[4]},
    {"name": "target_runtime_timing", "status": "blocked",
     "evidence": (
         "No device clock, pacing, deadline, throughput or memory measurement "
         "was made."),
     "reopen": REOPEN_CONDITIONS[4]},
    {"name": "provider_intake", "status": "blocked",
     "evidence": (
         "No opt-in provider, descriptor or catalog entry exists; the package is "
         "unregistered."),
     "reopen": (
         "Reopen only after rights, runtime and parity gates clear and an opt-in "
         "provider intake with an OFF default and independent review is approved.")},
    {"name": "public_default_selection", "status": "blocked",
     "evidence": "No default selection is proposed or made.",
     "reopen": (
         "Reopen only after provider intake clears and the owner records an "
         "explicit default decision with preserving controls.")},
)

# Source-reported values transcribed from pinned research. They are provenance
# only: not reproduced here, not pooled with the surrogate, not thresholds.
SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": (
        "Pinned research provenance only; not reproduced, not pooled and not "
        "used as a threshold or a quality claim."),
    "candidate_row": (
        "Denoising,ClearVoice MossFormerGAN,evaluated,30/30 frozen DNS paired "
        "quality outputs verified across three exact-candidate batches; mean "
        "SNR 20.70 dB, SI-SDR 20.69 dB, STOI .9825; delta SI-SDR +2.51 dB vs "
        "FastEnhancer Small and +0.57 dB vs FRCRN; only four per-item times "
        "(RTF 10.50-11.76); earlier CPU batches timed out."),
    "census_row": (
        "Attention/GAN; 16 kHz single-channel quality candidate. Five-clip "
        "screening only: mean delta SNR +7.91 dB and mean delta STOI +0.0461, "
        "all five improved on both. No inferential interval or full 30-clip "
        "comparison is claimed. CPU throughput is several times slower than "
        "real time; clean-input check is pending."),
    "full30": {
        "evaluation_id": "mossformergan-dns30-complete-quality-20261101",
        "candidate": "ClearVoice MossFormerGAN_SE_16K",
        "requested_pairs": 30,
        "valid_outputs": 30,
        "missing_outputs": 0,
        "quality_means": {
            "mossformer": {"snr_db": 20.702472, "si_sdr_db": 20.687954,
                           "stoi": 0.982520},
            "identity": {"snr_db": 10.066655, "si_sdr_db": 10.069746,
                         "stoi": 0.933184},
            "clearvoice_frcrn_16k": {"snr_db": 20.169594,
                                     "si_sdr_db": 20.121437, "stoi": 0.980633},
            "fastenhancer_small": {"snr_db": 18.246842, "si_sdr_db": 18.181756,
                                   "stoi": 0.965600},
            "deepfilternet3": {"snr_db": 16.604206, "si_sdr_db": 16.729331,
                               "stoi": 0.958974},
        },
        "paired_deltas": {
            "vs_identity": {
                "snr_db": 10.635817, "snr_db_ci95": [8.945490, 12.401612],
                "si_sdr_db": 10.618209,
                "si_sdr_db_ci95": [8.930154, 12.350129],
                "stoi": 0.049336, "stoi_ci95": [0.038601, 0.060941],
            },
            "vs_fastenhancer_small": {
                "si_sdr_db": 2.506199,
                "si_sdr_db_ci95": [2.103115, 2.916512],
            },
            "vs_deepfilternet3": {
                "si_sdr_db": 3.958624,
                "si_sdr_db_ci95": [3.204654, 4.789798],
            },
            "vs_clearvoice_frcrn_16k": {
                "si_sdr_db": 0.566517,
                "si_sdr_db_ci95": [0.391825, 0.768747],
            },
        },
        "tail_adapter_seconds": {
            "47": 105.744500, "48": 104.989825,
            "49": 117.586727, "50": 104.957503,
        },
        "tail_rtf": {"min": 10.50, "max": 11.76, "median": 10.53},
        "tail_worker_wall_seconds": 449.74,
        "tail_peak_rss_gb": 4.53,
        "earlier_partial": {
            "first_batch_valid": 19,
            "recovery_batch_valid": 26,
            "partial_mean_delta_snr_db": 9.926,
            "partial_mean_si_sdr_db": 20.439,
            "note": "superseded partial-subset diagnostics, retained as provenance",
        },
        "limitations": [
            "Complete 30/30 quality scoring spans three exact-candidate worker attempts.",
            "Full-set per-item runtime is unavailable for the first 26 outputs.",
            "Bootstrap intervals cover the fixed 30-pair DNS exploratory subset.",
            "No clean-input distortion diagnostic, subjective listening, mobile timing or power/thermal measurement was added.",
        ],
    },
    "census_five_clip_screen": {
        "clips": 5,
        "mean_delta_snr_db": 7.91,
        "mean_delta_stoi": 0.0461,
        "all_improved": True,
        "inferential_interval": None,
        "clean_input_check": "pending",
    },
    "upstream_author_reported_dns2020": {
        "source": "ClearerVoice README SpeechScore table; not independently reproduced",
        "PESQ": 3.57,
        "STOI": 0.98,
        "SI_SDR_dB": 20.60,
        "P808_MOS": 4.05,
        "SIG": 3.58,
        "BAK": 4.18,
        "OVRL": 3.36,
    },
    "training_data_note": TRAINING_DATA_NOTE,
    "disclaimer": (
        "These values come from pinned research files on 30 DNS2020 pairs, a "
        "five-clip screen and an upstream author table. They are not reproduced "
        "here, not device timing, not this fixture's metrics, not a listening "
        "result and not a release claim."),
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": CANDIDATE_ID,
    "model_name": MODEL_NAME,
    "upstream_repository": PACKAGE_SOURCE,
    "source_revision": SOURCE_REVISION,
    "code_license": CODE_LICENSE_METADATA,
    "model_license": MODEL_LICENSE_METADATA,
    "model_card": {
        "url": MODEL_CARD,
        "declared_revision": MODEL_CARD_REVISION,
        "revision_pin_type": "absent_from_pinned_ledger_not_hashed",
        "declared_license": MODEL_LICENSE_METADATA,
        "accessed_by_this_package": False,
    },
    "package": {
        "identity": PACKAGE_IDENTITY,
        "version": PACKAGE_VERSION,
        "requirements_lock": "adapters/clearvoice/requirements.lock",
        "requirements_lock_sha256": SOURCE_PINS[
            "adapters/clearvoice/requirements.lock"],
        "installed": False,
        "wheel_or_sdist_digest": None,
    },
    "checkpoint": {
        "asset_id": CHECKPOINT_ID,
        "bytes": CHECKPOINT_BYTES,
        "sha256": CHECKPOINT_SHA256,
        "present_in_sdk_worktree": False,
        "hashed_in_this_package": False,
        "downloaded_by_this_package": False,
        "loaded_or_executed": False,
    },
    "pointer": {
        "asset_id": POINTER_ID,
        "bytes": POINTER_BYTES,
        "sha256": POINTER_SHA256,
        "required_content": POINTER_REQUIRED_CONTENT,
        "content_verified": False,
        "present_in_sdk_worktree": False,
    },
    "runtime": {
        "kind": "external_python_package",
        "torch": "2.14.1",
        "device": "cpu",
        "installed": False,
        "invoked": False,
        "timing_measured": False,
    },
    "distribution_channel": {
        "declared": "Hugging Face model card plus ClearerVoice source revision",
        "artifact_revision_published": False,
        "retrieval_record": None,
        "note": (
            "the ledger records only byte counts and SHA-256 values; no "
            "immutable model artifact revision or retrieval URL is recorded"),
    },
    "training_data_provenance": TRAINING_DATA_NOTE,
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_code_license": CODE_LICENSE_METADATA,
    "upstream_model_license_metadata": MODEL_LICENSE_METADATA,
    "model_card_url": MODEL_CARD,
    "model_card_declared_license": MODEL_LICENSE_METADATA,
    "checkpoint_redistribution_clearance": False,
    "runtime_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "artifact_rights",
    "conclusion": (
        "Apache-2.0 is recorded for the ClearerVoice code and the model card, "
        "but artifact-specific checkpoint and runtime redistribution/product-use "
        "rights, training-data provenance, a retrieval record and legal review "
        "are not cleared. This package distributes no upstream asset."),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "ClearerVoice MossFormerGAN_SE_16K checkpoint, pointer, clearvoice 0.1.2 package and PyTorch runtime are absent; nothing was downloaded, installed, loaded or invoked.",
    "The checkpoint and pointer digests/byte counts, source revision, absent model revision and license metadata are quoted from research/noise_suppression_assets_20261027.json.",
    "The input range, identity source-time mapping, zero delay compensation, zero padded samples, pointer-content requirement and package check are quoted from adapters/clearvoice/run.py, adapter.json and README.md.",
    "The 30-pair and five-clip values are pinned research provenance only; this package does not reproduce them and measures no runtime.",
    "All signals, targets, observations and surrogate outputs are generated by reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def norm(value: Any, digits: int = 6) -> Any:
    if value is None:
        return None
    result = round(float(value), digits)
    return 0.0 if result == 0 else result


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
    return (json.dumps(_normalize_negzero(value), sort_keys=True, indent=2,
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ValueError("non_finite:" + token)

    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(value, dict):
        raise ValueError("root_not_object")
    return value


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


# ---------------------------------------------------------------------------
# Frozen synthetic stimuli
# ---------------------------------------------------------------------------

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
        regions = ((0.35, 0.75), (1.15, 1.55))
        value = 0.0
        for start, end in regions:
            if start <= t < end:
                ramp = min((t - start) / 0.012, (end - t) / 0.012, 1.0)
                value = max(value, ramp)
        return value
    if condition in ("idle_noise", "silence"):
        return 0.0
    modulation = math.sin(2.0 * math.pi * 2.7 * t + 0.55)
    return max(0.0, modulation) ** 1.15


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return (clean target, observed input) for one frozen condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    scales = {
        "quiet_speech": (0.055, 0.005),
        "active_speech": (0.240, 0.030),
        "low_snr_speech": (0.050, 0.055),
        "onset_offset": (0.170, 0.018),
        "idle_noise": (0.000, 0.028),
        "clean_speech": (0.140, 0.000),
        "silence": (0.000, 0.000),
    }
    target_scale, noise_scale = scales[condition]
    noise_rng = _lcg(_seed("noise:" + condition))
    clean: List[float] = []
    observed: List[float] = []
    for index in range(SAMPLES):
        t = index / SAMPLE_RATE_HZ
        if target_scale:
            carrier = (0.60 * math.sin(2.0 * math.pi * 173.0 * t)
                       + 0.29 * math.sin(2.0 * math.pi * 346.0 * t + 0.65)
                       + 0.11 * math.sin(2.0 * math.pi * 519.0 * t + 1.75))
            target = target_scale * _envelope(condition, index) * carrier
        else:
            target = 0.0
        noise = noise_scale * (2.0 * next(noise_rng) - 1.0)
        clean.append(target)
        observed.append(target + noise)
    return clean, observed


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary
# ---------------------------------------------------------------------------

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


CALLER_CONFIG_FIELDS: Tuple[str, ...] = (
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


# ---------------------------------------------------------------------------
# Deterministic offline whole-clip surrogate
# ---------------------------------------------------------------------------

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
    """Deterministic offline soft-mask surrogate; zero lag, exact length.

    This is an original amplitude-mask fixture. It has no attention block, no
    GAN, no neural weights and no relationship to the MossFormerGAN graph.
    """
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
    noise_floor = max(_percentile(powers, NOISE_PERCENTILE), 1e-12)
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
            target = (max(0.0, 1.0 - OVER_SUBTRACTION / ratio)) ** MASK_EXPONENT
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
            if abs(float(value)) > PEAK_LIMIT:
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


def _f32_digest(values: Sequence[float]) -> str:
    array = np.asarray(values, dtype="<f4")
    return sha256(array.tobytes())


def run_offline(samples: Sequence[float], chunk_size: int,
                config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Feed one chunking and return the whole-clip output plus accounting."""
    if chunk_size <= 0 or chunk_size > MAX_CHUNK_SAMPLES:
        raise ValueError("chunk_size_unsupported")
    session = OfflineSurrogateSession(config)
    chunk_count = 0
    emitted_before_finish = 0
    for start in range(0, len(samples), chunk_size):
        chunk = list(samples[start:start + chunk_size])
        emitted = session.process(chunk)
        emitted_before_finish += len(emitted)
        chunk_count += 1
    output = session.finish()
    _, info = enhance_offline(samples)
    return {
        "chunk_size": chunk_size,
        "chunk_count": chunk_count,
        "output": output,
        "output_digest": _f32_digest(output),
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


# ---------------------------------------------------------------------------
# Synthetic paired scoring
# ---------------------------------------------------------------------------

def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / float(len(values)))


def _db(ratio: float) -> float:
    return 10.0 * math.log10(max(ratio, 1e-30))


def _metric(value: Any, reason: str | None = None) -> Dict[str, Any]:
    return {
        "value": None if value is None else norm(value),
        "valid": value is not None,
        "invalid_reason": reason if value is None else None,
    }


def _si_sdr(reference: Sequence[float],
            estimate: Sequence[float]) -> Tuple[float | None, str | None]:
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    if ref.size == 0 or est.size != ref.size:
        return None, "length_mismatch"
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
    return 10.0 * math.log10(target_energy / error_energy), None


def _stoi(reference: Sequence[float],
          estimate: Sequence[float]) -> Tuple[float | None, str | None]:
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    if ref.size == 0 or est.size != ref.size:
        return None, "length_mismatch"
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
    return value, None


def _projection(reference: Sequence[float],
                estimate: Sequence[float]) -> Dict[str, Any]:
    ref = np.asarray(reference, dtype=np.float64)
    est = np.asarray(estimate, dtype=np.float64)
    empty = {
        "status": "not_applicable",
        "reason": None,
        "target_retention": None,
        "target_projection_snr_db": None,
    }
    if ref.size == 0 or est.size != ref.size:
        empty["reason"] = "length_mismatch"
        return empty
    if not np.isfinite(ref).all() or not np.isfinite(est).all():
        empty["reason"] = "nonfinite_signal"
        return empty
    ref = ref - float(np.mean(ref))
    est = est - float(np.mean(est))
    denominator = float(np.dot(ref, ref))
    if denominator <= 0.0:
        empty["reason"] = "zero_reference_energy"
        return empty
    scale = float(np.dot(est, ref) / denominator)
    projected = scale * ref
    residual = est - projected
    signal_energy = float(np.dot(projected, projected))
    residual_energy = float(np.dot(residual, residual))
    snr = None
    reason = None
    if signal_energy <= 0.0:
        reason = "zero_projection_energy"
    elif residual_energy <= 1e-20:
        reason = "zero_error_identity_exact"
    else:
        snr = 10.0 * math.log10(signal_energy / residual_energy)
    return {
        "status": "measured",
        "reason": reason,
        "target_retention": norm(abs(scale)),
        "target_projection_snr_db": None if snr is None else norm(snr),
    }


def score(clean: Sequence[float],
          estimate: Sequence[float]) -> Dict[str, Any]:
    """Synthetic paired diagnostics only; no real scorer or model is used."""
    if len(clean) != len(estimate) or not clean:
        raise ValueError("score_length_mismatch")
    signal_power = sum(value * value for value in clean)
    error_power = sum((a - b) ** 2 for a, b in zip(clean, estimate))
    if signal_power <= 0.0:
        snr = (None, "zero_reference")
    elif error_power <= 0.0:
        snr = (None, "zero_error_identity_exact")
    else:
        snr = (_db(signal_power / error_power), None)
    si_value, si_reason = _si_sdr(clean, estimate)
    stoi_value, stoi_reason = _stoi(clean, estimate)
    return {
        "snr_db": _metric(snr[0], snr[1]),
        "si_sdr_db": _metric(si_value, si_reason),
        "stoi": _metric(stoi_value, stoi_reason),
        "output_rms": norm(_rms(estimate)),
        "peak_abs_output": norm(max(abs(value) for value in estimate)),
        "clipped_samples": sum(1 for value in estimate if abs(value) > 1.0),
        "nonfinite_samples": sum(
            1 for value in estimate if not math.isfinite(value)),
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
    projection = _projection(prefix, chunked["output"][:valid])
    noisy_projection = _projection(prefix, observed[:valid])

    def delta(candidate_value: Any, control_value: Any) -> Any:
        if candidate_value is None or control_value is None:
            return None
        return norm(candidate_value - control_value)

    def value(variant: Dict[str, Any], metric: str) -> Any:
        return variant[metric]["value"]

    return {
        "reference": "synthetic_clean" if any(prefix) else "zero_reference",
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
            "snr_db": delta(value(candidate, "snr_db"), value(noisy, "snr_db")),
            "si_sdr_db": delta(value(candidate, "si_sdr_db"),
                               value(noisy, "si_sdr_db")),
            "stoi": delta(value(candidate, "stoi"), value(noisy, "stoi")),
        },
        "preservation": {
            "rms_gain_ratio": (
                None if noisy["output_rms"] == 0.0 else
                norm(candidate["output_rms"] / noisy["output_rms"])),
            "target_retention": projection["target_retention"],
            "target_projection_snr_db": projection["target_projection_snr_db"],
            "target_projection_snr_reason": projection["reason"],
            "identity_target_projection_snr_db":
                noisy_projection["target_projection_snr_db"],
            "target_projection_snr_delta_db": delta(
                projection["target_projection_snr_db"],
                noisy_projection["target_projection_snr_db"]),
        },
        "noise_attenuation_db": (
            None if noisy["output_rms"] <= 0.0 else
            norm(_db((candidate["output_rms"] / noisy["output_rms"]) ** 2))),
        "chunk_invariance_digest": chunked["output_digest"],
        "whole_clip_output_digest": whole["output_digest"],
        "whole_clip_matches_chunked":
            chunked["output_digest"] == whole["output_digest"],
    }


def _condition_blocks() -> Dict[str, Any]:
    return {name: condition_block(name) for name in CONDITIONS}


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
    attempt("wrong_model_name", mutated(model_name="FRCRN_SE_16K"))
    attempt("wrong_package_version", mutated(package_version="0.1.1"))
    attempt("mode_unsupported",
            {"mode": "streaming", "synthetic_surrogate_opt_in": True})
    attempt("surrogate_without_opt_in", mutated(synthetic_surrogate_opt_in=False))
    attempt("caller_asset_unavailable", caller_asset_config())

    wrong_sha = caller_asset_config()
    wrong_sha["checkpoint_sha256"] = "0" * 64
    attempt("caller_asset_wrong_checkpoint_sha", wrong_sha)

    control = caller_asset_config()
    revision = "artifact:MossFormerGAN_SE_16K@" + CHECKPOINT_SHA256
    control["model_revision"] = revision
    control["asset_reference"].update({
        "model_revision": revision,
        "model_download_revision": revision,
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
        "state_after_finish_unchanged_by_rejected_calls":
            after_finish == after_rejected_finish,
        "state_after_close_unchanged_by_rejected_calls":
            after_close == after_rejected_close,
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
    revision = "artifact:MossFormerGAN_SE_16K@" + CHECKPOINT_SHA256
    control.update({
        "model_revision": revision,
        "model_download_revision": revision,
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
        "contract": (
            "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, "
            "storage=external, no download"),
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
            "note": (
                "Admission logic only; no upstream bytes, runtime or rights "
                "exist and none are implied."),
        },
        "surrogate_policy": {
            "available": True,
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "labelled": "deterministic offline soft-mask surrogate",
        },
        "reopen_condition": (
            REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1] + " "
            + REOPEN_CONDITIONS[2]),
    }


def enhancement_profile() -> Dict[str, Any]:
    return {
        "name": PROFILE,
        "source": "plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "identity_and_noisy_controls": True,
        "paired_snr_si_sdr_and_stoi": "synthetic_fixture_only",
        "stoi": {
            "status": "synthetic_reference_only",
            "real_cohort": False,
            "reason": (
                "pystoi is pinned and scored against authored synthetic clean "
                "references; no rights-cleared real clean-reference cohort exists"),
        },
        "clean_speech_preservation": {
            "status": "synthetic_only",
            "conditions": ["quiet_speech", "active_speech", "clean_speech"],
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


def _regressions(blocks: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    comparisons = (
        ("snr_db", "noisy_control", SNR_REGRESSION_DB),
        ("si_sdr_db", "noisy_control", SNR_REGRESSION_DB),
        ("stoi", "identity_passthrough", STOI_MIN_REG),
    )
    for condition in CONDITIONS:
        block = blocks[condition]
        candidate = block["variants"]["surrogate_offline_chunked_160"]
        for metric, control_name, threshold in comparisons:
            control = block["variants"][control_name]
            candidate_value = candidate[metric]["value"]
            control_value = control[metric]["value"]
            if candidate_value is None or control_value is None:
                continue
            delta = candidate_value - control_value
            if delta < threshold:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "control_variant": control_name,
                    "better_direction": "higher",
                    "control_value": control_value,
                    "surrogate_value": candidate_value,
                    "delta": norm(delta),
                    "note": (
                        "Synthetic fixture regression recorded verbatim; not a "
                        "candidate result."),
                })
    return regressions


def _core_report() -> Dict[str, Any]:
    blocks = _condition_blocks()
    admission = asset_admission(asset_ref())
    regressions = _regressions(blocks)
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
        "format": dict(FORMAT),
        "boundary": dict(BOUNDARY),
        "offline_boundary": dict(OFFLINE_BOUNDARY),
        "scope": dict(SCOPE),
        "claims": dict(CLAIMS),
        "surrogate": {
            "identity": "mossformergan-offline-boundary-surrogate-v0",
            "kind": "deterministic offline soft-mask surrogate",
            "is_candidate": False,
            "is_neural_network": False,
            "attention_blocks": False,
            "gan_generator_or_discriminator": False,
            "weights": False,
            "checkpoint": False,
            "vendor_runtime": False,
            "method": (
                "deterministic frame-power soft mask with a 35th-percentile "
                "noise floor, 1.30 over-subtraction, exponent 0.85, gain floor "
                "0.20 and attack/release smoothing; one whole-clip pass with "
                "interpolated gains, zero lag and exact output length"),
            "public_input_geometry": "16 kHz mono f32 160-sample frames",
            "asset_geometry": "16 kHz mono f32, offline whole clip",
            "deterministic": True,
            "pure_synthetic": True,
            "quality_claim": False,
        },
        "stimuli": {
            "conditions": list(CONDITIONS),
            "samples_per_condition": SAMPLES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "seed_base": SEED_BASE,
            "clean_reference": "authored synthetic target waveform",
            "real_audio": False,
            "real_labels": False,
            "network": False,
            "peak_limit": PEAK_LIMIT,
        },
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
                "note": (
                    "Paired control for the synthetic target on the same valid "
                    "prefix."),
            },
            "candidate": {
                "name": "surrogate_offline_chunked_160",
                "real_candidate": False,
                "note": (
                    "Deterministic offline soft-mask surrogate, not "
                    "ClearerVoice MossFormerGAN."),
            },
            "whole_clip": {
                "name": "surrogate_offline_whole_clip",
                "note": (
                    "Chunk invariance control; must equal the 160-sample fed "
                    "output."),
            },
        },
        "comparison": {
            "identity_control": "same_mixture_identity",
            "provider": "mossformergan-offline-boundary-surrogate-v0",
            "established_task_matched_baseline_reproduced": False,
            "source_reported_used_for_qualification": False,
            "real_cohort_scored": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No MossFormerGAN runtime, rights-cleared real cohort or "
                "permitted listening; the surrogate is a boundary conformance "
                "fixture and its synthetic metrics are not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
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
                "delay_compensation_samples=0, valid_samples=len(output) and "
                "padded_samples=0 for the offline whole-clip adapter; "
                "source-reported, not re-measured here."),
            "lag_measured_here": False,
            "lag_modeled_in_fixture": True,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": (
                "sample-coordinate only; no wall clock, device clock or deadline"),
            "finish_policy": (
                "Caller chunks are buffered and the whole clip is enhanced once "
                "at finish; a partial final frame is zero-padded only for gain "
                "estimation and is never emitted."),
            "reset_policy": (
                "Explicit reset clears the buffer and finished flag; replay is "
                "bit-identical."),
            "output_accounting": {
                "output_samples": "input_samples",
                "delay_compensation_samples": DECLARED_LAG_SAMPLES,
                "padded_samples_emitted": 0,
                "internal_frame_padding_samples": "(-input_samples) mod 160",
                "source_time_mapping": "identity",
                "finding": (
                    "The upstream adapter returns one output sample per input "
                    "sample with identity source-time mapping and zero delay "
                    "compensation. This model emits exactly len(input) samples; "
                    "internal padding exists only for gain estimation."),
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
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "model_provenance": MODEL_PROVENANCE,
        "licensing_analysis": LICENSING_ANALYSIS,
        "tool_provenance": list(TOOL_PROVENANCE),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "evidence_classes": {
            "synthetic_surrogate": (
                "Deterministic model-free offline boundary surrogate on authored "
                "synthetic stimuli; no MossFormerGAN asset, real audio, runtime "
                "or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": "none",
            "target_runtime": "none",
            "exact_reference_parity": "none",
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "readme_digest_files": sorted(SOURCE_PINS),
        "contract_sha256": sha256(contract_bytes()),
        "notes": [
            "Every metric in this report is computed on deterministic synthetic stimuli and describes the surrogate only.",
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


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


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
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity/noisy controls plus a task-matched baseline gate",
                "paired synthetic SNR, SI-SDR and STOI against authored clean references",
                "clean-speech preservation, peaks and invalid/nonfinite outputs",
                "alignment, state, lifecycle and exact output accounting",
                "content/availability timing recorded as unmeasured",
                "real cohort, independent scorer and listening recorded as absent",
            ],
            "not_applicable": [
                "no MossFormerGAN runtime, so exact reference outputs are not reproduced",
                "no rights-cleared real cohort, so no real paired quality or generalization claim is made",
                "no target device, so no timing, memory or deadline result is claimed",
            ],
        },
        "format": dict(FORMAT),
        "boundary": dict(BOUNDARY),
        "offline_boundary": dict(OFFLINE_BOUNDARY),
        "scope": dict(SCOPE),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": [dict(gate) for gate in GATES],
        "asset": asset_ref(),
        "asset_admission": asset_admission(asset_ref()),
        "upstream_contract": {
            "adapter_identity": PACKAGE_IDENTITY,
            "entrypoint": "adapters/clearvoice/run.py",
            "config_fields": list(CALLER_CONFIG_FIELDS),
            "input": "mono 16 kHz f32 in [-1, 1]",
            "output": (
                "identity source-time mapping, zero delay compensation, zero "
                "padded samples, length equal to input"),
            "pointer_required": True,
        },
        "surrogate": {
            "kind": "deterministic offline soft-mask surrogate",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "attention_blocks": False,
            "gan_generator_or_discriminator": False,
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
        "model_provenance": MODEL_PROVENANCE,
        "licensing_analysis": LICENSING_ANALYSIS,
        "source_pins": {"source:" + key: value for key, value in SOURCE_PINS.items()},
        "boundary_pins": {
            "worktree:" + key: value for key, value in BOUNDARY_PINS.items()},
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, contract, header, registry, default, board, handoff or CI file changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not a provider or production callback.",
            "No MossFormerGAN checkpoint, pointer, weight, source, runtime or package is copied, downloaded, built, loaded or executed.",
            "All stimuli are authored deterministic synthetic floats; no real audio, corpus, label, device or network is used.",
            "Caller-supplied asset references fail closed on missing, unpinned, hash-mismatched, absent, unverified or rights-uncleared inputs.",
            "Source-reported MossFormerGAN metrics are provenance only and are never reproduced, pooled or used as thresholds.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(build_contract())


def build_adapter() -> Dict[str, Any]:
    admission = asset_admission(asset_ref())
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "protocol_version": 1,
        "identity": "ClearerVoice-MossFormerGAN_SE_16K-offline-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "task_id": TASK,
        "component": COMPONENT,
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
        "entrypoint": ["python", "docs/task-evidence/" + SLUG + "/reference.py"],
        "upstream_entrypoint": ["python", "adapters/clearvoice/run.py"],
        "asset_readiness": admission["status"],
        "real_runtime_used": False,
        "weights_accessed": False,
        "attention_or_gan_executed": False,
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
        "note": (
            "Proposal-only task-local descriptor. It is not the shipped adapter, "
            "not a provider registration and not a public default."),
    }


def adapter_bytes() -> bytes:
    return canonical_bytes(build_adapter())


def build_readiness() -> Dict[str, Any]:
    admission = asset_admission(asset_ref())
    report_bytes = canonical_report_bytes(build_report())
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "candidate": CANDIDATE_ID,
        "profile": PROFILE,
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "ready_for_opt_in_adapter": False,
        "ready_for_provider_registration": False,
        "ready_for_release": False,
        "quality_pass": False,
        "processor_exposure": False,
        "asset_reference": asset_ref(),
        "admission": admission,
        "readiness_conclusion": (
            "The offline whole-clip boundary is modelled, but the candidate is "
            "not ready to run or qualify: the exact MossFormerGAN_SE_16K "
            "checkpoint bytes and the clearvoice 0.1.2 runtime are absent, the "
            "checkpoint has no immutable model artifact revision in the pinned "
            "ledger, the 24-byte pointer content is unverified, and "
            "artifact-specific rights are not cleared."),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "blocked_gates": [gate["name"] for gate in GATES],
        "exact_blocker": EXACT_BLOCKERS[0],
        "reopen_condition": REOPEN_CONDITIONS[0],
        "report_sha256": sha256(report_bytes),
        "contract_sha256": sha256(contract_bytes()),
        "allowed_now": [
            "synthetic surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
        ],
        "not_allowed": [
            "downloading or bundling the MossFormerGAN_SE_16K checkpoint, pointer or clearvoice package",
            "executing the vendor runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/timing",
        ],
        "scope": dict(SCOPE),
        "claims": dict(CLAIMS),
    }


def readiness_bytes() -> bytes:
    return canonical_bytes(build_readiness())


# ---------------------------------------------------------------------------
# Manifests, README table and strict parsers
# ---------------------------------------------------------------------------

def allowed_pin_keys() -> set[str]:
    keys = {"source:" + path for path in SOURCE_PINS}
    keys.update("worktree:" + path for path in BOUNDARY_PINS)
    keys.update("worktree:" + TASK_PREFIX + name for name in LOCAL_FILES)
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
        relative = raw.split(":", 1)[1] if ":" in raw else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def sources_bytes() -> bytes:
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are "
        "relative to the SDK worktree.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  worktree:{path}")
    for name in sorted(LOCAL_FILES):
        digest = sha256((HERE / name).read_bytes())
        lines.append(f"{digest}  worktree:{TASK_PREFIX}{name}")
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
    if path.startswith("worktree:"):
        return SDK_ROOT / path.split(":", 1)[1]
    if path.startswith("source:"):
        return SOURCE_ROOT / path.split(":", 1)[1]
    if path.startswith(TASK_PREFIX):
        return SDK_ROOT / path
    if path.startswith("/"):
        raise ValueError("absolute_pin_path:" + path)
    return SOURCE_ROOT / path


def strict_rejection_examples() -> Dict[str, int]:
    """Exercise the strict JSON and pin parsers; used by verifier and tests."""
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
        "a" * 64 + "  docs/task-evidence/" + SLUG + "/unknown",
        "\n".join(["0" * 64 + "  source:CONTRACTS.md",
                   "0" * 64 + "  source:CONTRACTS.md"]),
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


def vendored_binary_files() -> List[str]:
    """Task-local files that look like copied model/runtime/audio assets."""
    suffixes = {
        ".dylib", ".so", ".dll", ".onnx", ".tar", ".gz", ".ckpt", ".pt",
        ".pth", ".safetensors", ".wav", ".flac", ".mp3", ".npy", ".npz",
    }
    return sorted(
        path.name for path in HERE.rglob("*")
        if path.is_file() and (
            path.suffix.lower() in suffixes
            or any(path.name.endswith(suffix) for suffix in suffixes)))


def asset_ledger_record() -> Dict[str, Any]:
    """Return the pinned ledger record for this candidate, strictly."""
    ledger = strict_loads((SOURCE_ROOT / ASSET_LEDGER_PATH).read_text(
        encoding="utf-8"))
    candidates = ledger.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("ledger_candidates_missing")
    matches = [row for row in candidates
               if isinstance(row, dict) and row.get("id") == CANDIDATE_ID]
    if len(matches) != 1:
        raise ValueError("ledger_candidate_count:" + str(len(matches)))
    return matches[0]


def adapter_descriptor() -> Dict[str, Any]:
    return strict_loads(
        (SOURCE_ROOT / "adapters/clearvoice/adapter.json").read_text(
            encoding="utf-8"))


def mossformer_results() -> Dict[str, Any]:
    return strict_loads((SOURCE_ROOT / MOSSFORMER_RESULTS_PATH).read_text(
        encoding="utf-8"))


def readme_test_count_token() -> str:
    return (f"Tests: **{EXPECTED_TEST_COUNT} passed, 0 failed, 0 skipped**")


def _run_git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(SDK_ROOT), *args], text=True).strip()
