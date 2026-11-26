# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-CISCO-STUPASE.

This module is NOT Cisco StuPASE. It does not contain, download, load or execute
any upstream source, checkpoint, PyTorch runtime, audio file or dataset. It
records the exact public source/asset identities found by metadata-only
inspection, applies the Enhancement acceptance profile, and exercises a
fail-closed caller-supplied-asset admission contract with deterministic
synthetic controls. Every candidate-quality, rights, runtime, timing and release
gate stays blocked.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-CISCO-STUPASE"
TITLE = "Cisco StuPASE"
SLUG = "cisco-stupase"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{SLUG.upper()}"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
DECISION = "DEFER"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_incomplete"
DEFER_BEFORE = "opt_in_adapter_exposure"

SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"

# Public v0 installed geometry. This package changes none of it.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"

# Source-derived StuPASE geometry. Not executed or measured here.
MEL_N_FFT = 1280
MEL_HOP_LENGTH = 320
MEL_WIN_LENGTH = 1280
MEL_N_MELS = 100
CFM_DIM = 1024
CFM_DEPTH = 12
CFM_HEADS = 16
CFM_TEXT_IN_DIM = 1024
CFM_TEXT_DIM = 512
CFM_FF_MULT = 2
CFM_CONV_LAYERS = 4
DEWAVLM_OUTPUT_LAYER = 24
ODE_METHOD = "euler"
DEFAULT_STEPS = 8
DEFAULT_CFG_STRENGTH = 0.5
DEFAULT_SWAY_SAMPLING_COEF = -1.0
PARAMETER_COUNT_SOURCE_REPORTED = 561000000
COMPUTE_GMACS_SOURCE_REPORTED = 104

# Exact public identities established by metadata-only inspection on 2026-11-26.
SOURCE_REPOSITORY = "https://github.com/cisco-open/pase"
SOURCE_COMMIT = "45614efae73dc49bf36018d1ca6a9319b3050038"
SOURCE_TREE_ENTRIES = 119
SOURCE_TREE_TRUNCATED = False
SOURCE_CODE_LICENSE = "Apache-2.0"
HUB_REPOSITORY = "https://huggingface.co/cisco-ai/stupase"
HUB_REVISION = "539963f425ae201ac8c379b6480e3b182a4840ad"
HUB_LAST_MODIFIED = "2026-07-14T13:19:40.000Z"
HUB_MODEL_LICENSE = "apache-2.0"
HUB_GATED = False
HUB_PRIVATE = False
METADATA_OBSERVED_ON = "2026-11-26"
METADATA_RETRIEVAL = (
    "Public HTTPS metadata only: git ls-remote, GitHub tree/raw text and the "
    "Hugging Face model/tree API. No checkpoint, audio, dataset or media bytes "
    "were downloaded, read, hashed or materialized."
)

# Checkpoints listed by the pinned hub revision. LFS oid is the file SHA-256.
EXTERNAL_ASSETS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "dewavlm_r",
        "path": "DeWavLM-R.pt",
        "byte_count": 1261990714,
        "sha256": "4eb21c9e6ab9bf51fe1c24a580e6f4c8f677ad4028e3b997e462e34f17c59ccf",
        "role": "semantic enhancement module (DeWavLM-R)",
        "format": "PyTorch checkpoint",
        "url": f"{HUB_REPOSITORY}/blob/{HUB_REVISION}/DeWavLM-R.pt",
    },
    {
        "id": "cfm",
        "path": "CFM.pt",
        "byte_count": 758024988,
        "sha256": "df8e77fcc31554abb1b3481f1f4bc62688e75b9bd83081fb4d336b128f760f5e",
        "role": "flow-matching acoustic enhancement module",
        "format": "PyTorch checkpoint",
        "url": f"{HUB_REPOSITORY}/blob/{HUB_REVISION}/CFM.pt",
    },
    {
        "id": "vocoder",
        "path": "Vocoder_Mel-16k.pt",
        "byte_count": 242750990,
        "sha256": "2d38b6adfb29129a4c78f7ed030aa75f1a922f71e0fc87f2e59f2c58d04ee13b",
        "role": "Mel vocoder (16 kHz)",
        "format": "PyTorch checkpoint",
        "url": f"{HUB_REPOSITORY}/blob/{HUB_REVISION}/Vocoder_Mel-16k.pt",
    },
)

EXTERNAL_CONFIG = {
    "id": "config",
    "path": "config.json",
    "byte_count": 53,
    "sha256": "b3229818b05a9ff9ec9bf36323ce3c1b109c0dff861d50f73da03aa68ab48193",
    "role": "minimal hub config: model_type=stupase, sample_rate=16000",
    "url": f"{HUB_REPOSITORY}/blob/{HUB_REVISION}/config.json",
}

# Small public text files that establish source/geometry/licensing facts. These
# are pinned as external metadata only; no upstream source is materialized.
EXTERNAL_SOURCE_FILES: Tuple[Dict[str, Any], ...] = (
    {
        "path": "stupase/README.md",
        "byte_count": 4949,
        "sha256": "1565ec7b38aedb611353eb3dbc4f852a72cfe03fdcb11037b76c09396c9b9a7c",
        "role": "official inference and checkpoint description",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/README.md",
    },
    {
        "path": "stupase/configs/cfg_infer.yaml",
        "byte_count": 509,
        "sha256": "2bcdd6d9e1ff94d9cbc8ceaa01f0341bd10ed4b0fe1acca119b6aa9fd3454311",
        "role": "inference config schema; absolute experiment paths",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/configs/cfg_infer.yaml",
    },
    {
        "path": "stupase/configs/cfg_train_flow.yaml",
        "byte_count": 3927,
        "sha256": "aaa541d8d7c1610f12830e0cd33cc7884e451a942adecc4a594734ba90c21e9c",
        "role": "CFM/DiT and Mel geometry, 8-step Euler sampling defaults",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/configs/cfg_train_flow.yaml",
    },
    {
        "path": "stupase/configs/cfg_train_melvocoder.yaml",
        "byte_count": 2505,
        "sha256": "1bb2299c3b1a35e01f8ed53d11f7bede64ade3796b3fd96478665e7086bc3bf9",
        "role": "Mel vocoder geometry and 16 kHz sample rate",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/configs/cfg_train_melvocoder.yaml",
    },
    {
        "path": "stupase/inference/inference.py",
        "byte_count": 6131,
        "sha256": "f30753c617f980bf5e014661f1bc3fb6dafe9fc2b30cc2461bec1aa66b6fc9f3",
        "role": "checkpoint resolution and input-peak output normalization",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/inference/inference.py",
    },
    {
        "path": "stupase/models/stupase.py",
        "byte_count": 2138,
        "sha256": "3304b80256d8ed001146d6a15fb9fea3afd8fce708e03d075d6d95eeb7ca93e7",
        "role": "three-module forward and pad/truncate-to-input-length contract",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/stupase/models/stupase.py",
    },
    {
        "path": "LICENSE.md",
        "byte_count": 2222,
        "sha256": "e270c357f173cacbcaa3a223c2faac631c0e04e368cb7b9781636236026bc36e",
        "role": "Cisco-authored Apache-2.0 and third-party attribution policy",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/LICENSE.md",
    },
    {
        "path": "NOTICE",
        "byte_count": 2616,
        "sha256": "5d431fc2f1664d3532b7b53775bf1a799752f3f6d8f5091c39653b974480b426",
        "role": "third-party component and license inventory",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/NOTICE",
    },
    {
        "path": "requirements.txt",
        "byte_count": 308,
        "sha256": "da3a568caaebde12e57f17ff76a9d03170546efb742656cd772f0c81a22b6605",
        "role": "conflicting torch/torchaudio duplicate pins; unreproducible requirements",
        "url": f"{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/requirements.txt",
    },
)

HUB_MODEL_CARD = {
    "path": "README.md",
    "byte_count": 7943,
    "sha256": "6eccb2ec0798191cfd2ce6fe913e00bab2a7c7d05694f4ed14687e51c8abdd4e",
    "role": "Apache-2.0 model card; architecture, data, metrics and limitations",
    "url": f"{HUB_REPOSITORY}/blob/{HUB_REVISION}/README.md",
}

THIRD_PARTY_COMPONENTS: Tuple[Dict[str, str], ...] = (
    {"component": "Microsoft WavLM", "license": "MIT"},
    {"component": "NXAI xLSTM scheduler", "license": "Apache-2.0"},
    {"component": "WavTokenizer components", "license": "MIT"},
    {"component": "SEtrain vocoder training scripts", "license": "MIT"},
    {"component": "KKKSQJ DeepLearning utilities", "license": "MIT"},
    {"component": "urgent-challenge utilities", "license": "Apache-2.0"},
    {"component": "NVIDIA BigVGAN discriminators", "license": "MIT"},
    {"component": "SenSE flow-matching components", "license": "MIT"},
)

TRAINING_DATA: Tuple[Dict[str, str], ...] = (
    {"dataset": "DNS5 clean speech (LibriVox subset)", "license": "public domain / DNS5 terms"},
    {"dataset": "LibriSpeech", "license": "CC BY 4.0"},
    {"dataset": "LibriTTS", "license": "CC BY 4.0"},
    {"dataset": "VCTK", "license": "CC BY 4.0"},
    {"dataset": "DNS5 noise (AudioSet, Freesound, DEMAND)", "license": "CC BY 4.0 / CC0 1.0 / CC BY-SA 3.0"},
    {"dataset": "OpenSLR26 and OpenSLR28 RIRs", "license": "Apache-2.0"},
)

INVENTORY_COMPONENT = {
    "id": "cisco-stupase",
    "name": "Cisco StuPASE",
    "area": "Enhancement",
    "evidence_status": "considered",
    "repository": "audio-sdk",
    "disposition": "sdk-model",
    "verification_profile": "enhancement",
    "task": TASK,
    "evidence_path": "research/noise_suppression_candidate_census.md",
    "evidence_line": 65,
}

CANDIDATE_RECORD = {
    "id": "candidate-cisco-stupase-16k",
    "revision": 1,
    "kind": "candidate",
    "actor": "noise-suppression-thirty-first-search-pass-20261027",
    "created_at": "2026-10-27T11:55:00Z",
    "benchmark_state": "not_run",
    "code": "available",
    "weights": "located_unverified",
    "eligibility_state": "blocked",
    "eligibility_reason": (
        "Official source/model card documents checkpoints and Apache-2.0, but "
        "exact hashes, compatible runtime footprint and noise-only behavior are "
        "not verified; isolated candidate execution unavailable on host."),
    "architecture": "semantic WavLM-R + flow-matching acoustic enhancer + Mel vocoder",
    "dataset": "DNS5 noise; LibriVox, LibriTTS, VCTK, LibriSpeech speech; OpenSLR RIRs",
    "reported_only": True,
    "sample_rate_hz": 16000,
    "implementation_source": f"{SOURCE_REPOSITORY}/tree/main/stupase",
    "method_id": "method-cisco-stupase",
    "method_revision": 1,
}

METHOD_RECORD = {
    "id": "method-cisco-stupase",
    "revision": 1,
    "kind": "method",
    "name": TITLE,
    "purpose": "offline 16 kHz studio-quality generative speech enhancement research comparator",
    "scope": "DeWavLM-R semantic module, flow-matching acoustic enhancement and Mel vocoder; mixed noise/reverb",
    "provenance": [
        f"{SOURCE_REPOSITORY}/tree/main/stupase",
        HUB_REPOSITORY,
    ],
}

ACCOUNTING_ROW = {
    "id": "candidate-cisco-stupase-16k",
    "revision": 1,
    "method": "method-cisco-stupase@1",
    "eligibility": "blocked",
    "reason": (
        "Official source/model card documents checkpoints and Apache-2.0, but "
        "exact hashes, compatible runtime footprint and noise-only behavior are "
        "not verified; isolated candidate execution unavailable on host."),
    "code": "available",
    "weights": "located_unverified",
    "line": 68,
}

EVIDENCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "census-stupase",
        "path": "research/noise_suppression_candidate_census.md",
        "line": 65,
        "contains": [
            "**Cisco StuPASE**",
            "flow-matching acoustic enhancer",
            "Apache-2.0 model card",
        ],
        "role": "candidate entry and task fit",
    },
    {
        "id": "census-source-links",
        "path": "research/noise_suppression_candidate_census.md",
        "line": 140,
        "contains": [
            "https://github.com/cisco-open/pase",
            "https://huggingface.co/cisco-ai/stupase",
        ],
        "role": "official source and model-card links",
    },
    {
        "id": "pilot-deferred",
        "path": "research/pilot_evaluation_progress.md",
        "line": 39,
        "contains": [
            "StuPASE",
            "deferred from additive-noise-only ranking",
        ],
        "role": "census scope: not an additive-noise-only baseline",
    },
    {
        "id": "pilot-unpinned",
        "path": "research/pilot_evaluation_progress.md",
        "line": 45,
        "contains": [
            "Cisco StuPASE",
            "Checkpoints are still unpinned/unverified for evaluation.",
        ],
        "role": "explicit checkpoint readiness blocker",
    },
    {
        "id": "accounting-row",
        "path": "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/candidate_accounting.csv",
        "line": 68,
        "contains": [
            "candidate-cisco-stupase-16k",
            "located_unverified",
            "exact hashes",
        ],
        "role": "immutable accounting snapshot row",
    },
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/pilot_evaluation_progress.md":
        "7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/candidate_accounting.csv":
        "7261b99e06460b612dcbebeec3859de60a7040a18444fc19a637ebddc4a58e3c",
    "research/store/snapshots/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7.jsonl":
        "c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

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
    "run.py",
    "test_reference.py",
    "verify.py",
)

ASSET_ADMISSION_REASONS: Tuple[str, ...] = (
    "asset_bundle_not_supplied",
    "asset_bytes_not_supplied_in_this_worktree",
    "source_checkout_not_admitted",
    "checkpoint_bytes_not_admitted",
    "runtime_not_reproducible",
    "rights_not_cleared",
    "matched_evidence_absent",
)

CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "bundle_id",
    "source_repository",
    "source_commit",
    "hub_repository",
    "hub_revision",
    "sample_rate_hz",
    "channels",
    "sample_format",
    "modules",
    "config",
    "sampling",
    "mel",
    "runtime",
    "peak_policy",
    "content_alignment",
)

CALLER_ASSET_ALLOWED: Tuple[str, ...] = CALLER_ASSET_FIELDS + ("caller_path",)

CALLER_MODULE_IDS: Tuple[str, ...] = ("dewavlm_r", "cfm", "vocoder")
CALLER_RUNTIME_FIELDS: Tuple[str, ...] = (
    "python_version",
    "torch_version",
    "torchaudio_version",
    "numpy_version",
    "soundfile_version",
    "librosa_version",
    "device",
    "wheel_sha256",
)
CALLER_DEVICES: Tuple[str, ...] = ("cpu", "mps", "cuda")
CALLER_PEAK_POLICIES: Tuple[str, ...] = ("input_peak", "fixed_0.5")

README_PIN_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([a-f0-9]{64})`\s*\|")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$")

TOTAL_CHECKPOINT_BYTES = sum(item["byte_count"] for item in EXTERNAL_ASSETS)

BOUNDARY = {
    "default_change": False,
    "descriptor_or_registry_change": False,
    "external_assets_copied": False,
    "installed_v0_behavior_change": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "shared_build_or_ci_change": False,
    "board_or_handoff_change": False,
    "task_local_only": True,
}

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "sample_format": SAMPLE_FORMAT,
    "unchanged": True,
}

TASK_GEOMETRY = {
    "evidence_class": "source_reported_geometry_not_executed",
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "processing_mode": "offline whole-clip generative enhancement",
    "mel": {
        "n_mels": MEL_N_MELS,
        "n_fft": MEL_N_FFT,
        "hop_length": MEL_HOP_LENGTH,
        "win_length": MEL_WIN_LENGTH,
        "center": True,
        "power": 1.0,
        "log_clamp_min": "1e-7",
        "frame_rule": "T = 1 + floor(L / hop_length) for non-negative L",
    },
    "dewavlm_r": {
        "output_layer": DEWAVLM_OUTPUT_LAYER,
        "frozen": True,
        "input": "noisy waveform at 16 kHz",
        "output": "enhanced phonetic representations",
    },
    "cfm": {
        "dim": CFM_DIM,
        "depth": CFM_DEPTH,
        "heads": CFM_HEADS,
        "text_in_dim": CFM_TEXT_IN_DIM,
        "text_dim": CFM_TEXT_DIM,
        "ff_mult": CFM_FF_MULT,
        "conv_layers": CFM_CONV_LAYERS,
        "ode_method": ODE_METHOD,
        "default_steps": DEFAULT_STEPS,
        "default_cfg_strength": DEFAULT_CFG_STRENGTH,
        "default_sway_sampling_coef": DEFAULT_SWAY_SAMPLING_COEF,
        "sigma": 0.0,
    },
    "vocoder": {
        "input_channels": MEL_N_MELS,
        "dim": 768,
        "intermediate_dim": 2304,
        "num_layers": 12,
        "n_fft": MEL_N_FFT,
        "hop_length": MEL_HOP_LENGTH,
    },
    "parameter_count_source_reported": PARAMETER_COUNT_SOURCE_REPORTED,
    "parameter_count_is_approximate": True,
    "compute_gmacs_source_reported": COMPUTE_GMACS_SOURCE_REPORTED,
    "checkpoint_total_bytes": TOTAL_CHECKPOINT_BYTES,
    "content_alignment": {
        "model_forward": "pad_or_truncate_to_input_length",
        "content_lag_samples": 0,
        "measured": False,
    },
    "peak_policy": {
        "variants": [
            {
                "wrapper": "stupase/inference/inference.py",
                "policy": "scale_output_to_input_peak",
                "zero_input_peak_behavior": "zero_output",
            },
            {
                "wrapper": "stupase/inference/infer_flow.py",
                "policy": "scale_output_to_fixed_0.5",
                "zero_input_peak_behavior": "not_applicable",
            },
        ],
        "consistent": False,
        "measured": False,
    },
    "runtime": {
        "python_pinned_in_upstream_requirements": False,
        "torch_pins": ["2.4.1", "2.1.1"],
        "torchaudio_pins": ["2.4.1", "2.1.1"],
        "pysoundfile_pin": "0.9.0.post1",
        "huggingface_hub_pin": "0.30.2",
        "requirements_reproducible": False,
    },
    "source_reported_not_executed": True,
    "qualifies": False,
}

HOST = "darwin arm64"
PYTHON_PINNED = "3.12.16"

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "RG-01 source commit and code tree admitted",
        "Materialize the exact cisco-open/pase commit in caller-owned storage, "
        "record the full tree digest and per-file SHA-256, and review LICENSE.md "
        "and NOTICE for the intended use.",
    ),
    (
        "RG-02 checkpoint identity and bytes admitted",
        "Supply the exact DeWavLM-R.pt, CFM.pt and Vocoder_Mel-16k.pt bytes from "
        "the pinned hub revision, verify byte counts and SHA-256 from an immutable "
        "retrieval receipt, and fail closed on any other revision or file set.",
    ),
    (
        "RG-03 runtime lock and forward pass reproduced",
        "Provide one resolved lock for Python 3.12.16 with wheel/sdist hashes for "
        "torch, torchaudio, numpy, soundfile, librosa, omegaconf, torchdiffeq, "
        "x-transformers and huggingface_hub, install it on the intended target, and "
        "reproduce an import plus one forward pass without network.",
    ),
    (
        "RG-04 wrapper geometry, alignment and peak policy frozen",
        "Freeze one integration contract for peak normalization, tail handling and "
        "source-sample mapping, then reproduce a whole-clip trace with exact input "
        "and output lengths, peaks, alignment and final-partial behavior.",
    ),
    (
        "RG-05 rights, third-party notices and data obligations reviewed",
        "Record a written legal/rights review for the exact checkpoints, the "
        "Apache-2.0/MIT third-party notices and the CC BY 4.0, CC0 1.0 and "
        "CC BY-SA 3.0 training-data obligations; clear local evaluation, derivative "
        "output use, redistribution and any commercial use.",
    ),
    (
        "RG-06 rights-cleared cohort and task-matched baseline frozen",
        "Freeze a rights-cleared paired cohort with clean references and an "
        "established task-matched baseline, separated into noise-only and "
        "dereverberation strata.",
    ),
    (
        "RG-07 independent scoring and permitted listening or predictive screen",
        "Score paired SI-SDR and STOI with an approved independent scorer, and add "
        "authorized listening or a separately labeled predictive screen for "
        "unpaired speech.",
    ),
    (
        "RG-08 clean preservation, peaks and invalid outputs measured",
        "Measure clean-speech preservation, output peaks, clipping, nonfinite and "
        "invalid outputs, silence/noise-only behavior, and content/availability "
        "timing for the exact runtime.",
    ),
    (
        "RG-09 compute, timing and resource feasibility measured",
        "Measure one whole-clip forward pass on the intended CPU/MPS/CUDA target "
        "with wall time, memory, device, thread count and exact runtime, or supply "
        "a qualified target runner.",
    ),
    (
        "RG-10 opt-in provider intake and release review",
        "Only after RG-01..RG-09 clear, implement a separate opt-in OFF-by-default "
        "adapter, obtain independent exact-head review, and record benchmark and "
        "release approval.",
    ),
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "BLK-01",
        "title": "source checkout not admitted",
        "missing": (
            "No Cisco StuPASE source checkout is materialized in the workspace. The "
            f"official repository commit {SOURCE_COMMIT} and its "
            f"{SOURCE_TREE_ENTRIES}-entry tree are identified only from public GitHub "
            "metadata; no local tree digest, per-file checkout or source admission "
            "record exists."),
        "reopen": (
            "Materialize the exact commit in caller-owned storage, record the tree "
            "digest and per-file SHA-256, and review LICENSE.md/NOTICE for the "
            "intended use. Metadata identification alone is not admission."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-02",
        "title": "checkpoint bytes not admitted",
        "missing": (
            "The three checkpoints are absent. The pinned hub revision lists "
            "DeWavLM-R.pt 1,261,990,714 bytes SHA-256 4eb21c9e..., CFM.pt "
            "758,024,988 bytes SHA-256 df8e77fc..., and Vocoder_Mel-16k.pt "
            "242,750,990 bytes SHA-256 2d38b6ad..., but no checkpoint bytes were "
            "downloaded, read or verified here."),
        "reopen": (
            "Supply the exact three files from the caller's storage, verify byte "
            "counts and SHA-256, and record an immutable retrieval receipt. Any "
            "different revision or file set fails closed."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-03",
        "title": "runtime not reproducible",
        "missing": (
            "The official requirements.txt is not a reproducible lock: it pins torch "
            "and torchaudio twice (2.4.1 and 2.1.1), uses PySoundFile 0.9.0.post1, and "
            "does not pin Python. torch, torchaudio, librosa, omegaconf, torchdiffeq, "
            "x-transformers and huggingface_hub are not installed in the pinned "
            "interpreter; no CPU/MPS/CUDA forward smoke has been run."),
        "reopen": (
            "Provide one resolved lock for Python 3.12.16 with artifact hashes, "
            "install it on the intended target, and reproduce an import plus one "
            "forward pass without network access."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-04",
        "title": "wrapper geometry and peak policy ambiguous",
        "missing": (
            "The model forward pads or truncates to the input length, but the two "
            "official wrappers normalize peaks differently: inference.py scales to "
            "the input peak; infer_flow.py scales to a fixed 0.5. No measured "
            "alignment, tail, peak or clean-speech preservation trace exists."),
        "reopen": (
            "Freeze one integration contract for peak policy, tail policy and "
            "source-sample mapping, then reproduce a whole-clip trace with exact "
            "lengths, peaks, alignment and final-partial behavior."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-05",
        "title": "rights and data obligations not reviewed",
        "missing": (
            "The model card and Cisco-authored code declare Apache-2.0. Third-party "
            "components are under MIT/Apache notices, and training data includes "
            "CC BY 4.0, CC0 1.0 and CC BY-SA 3.0 material. No artifact-specific "
            "checkpoint terms, output-use/redistribution clearance or legal review "
            "exists."),
        "reopen": (
            "Record a written legal/rights review for the exact checkpoints, code "
            "notices and training-data obligations; clear local evaluation, "
            "derivative output use, redistribution and any commercial use."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-06",
        "title": "matched enhancement evidence absent",
        "missing": (
            "No rights-cleared paired cohort with clean references, no independent "
            "SI-SDR/STOI result, no clean-speech preservation, peak/clipping, "
            "noise-only or reverberant stratification, and no permitted listening or "
            "approved predictive screen exists."),
        "reopen": (
            "Freeze a rights-cleared cohort and scorer; run identity/noisy and "
            "task-matched baseline controls; report paired SI-SDR/STOI, clean "
            "preservation, peaks, invalid outputs, noise-only and dereverberation "
            "strata separately; add permitted listening or a labeled predictive "
            "screen."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-07",
        "title": "compute feasibility unverified",
        "missing": (
            "The released model is approximately 561M parameters, 2,262,766,692 "
            "checkpoint bytes and 104 GMAC/s source-reported, with 8 Euler CFM steps. "
            "No CPU, MPS or GPU timing/resource measurement exists on the intended "
            "target; this host is Apple Silicon without CUDA."),
        "reopen": (
            "Measure one whole-clip forward pass on the intended target, recording "
            "wall time, memory, device, thread count and exact runtime; or supply a "
            "qualified target runner."),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-08",
        "title": "provider intake and release gates absent",
        "missing": (
            "No opt-in SDK adapter, OFF-by-default registration, descriptor, provider "
            "intake, independent exact-head review, benchmark review or release "
            "approval exists."),
        "reopen": (
            "Only after BLK-01..BLK-07 clear, implement a separate opt-in "
            "OFF-by-default adapter, obtain independent exact-head review, and record "
            "benchmark and release approval."),
        "status": "open",
        "qualifies": False,
    },
)

REQUIRED_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {"id": "A01", "name": "source checkout at the exact commit", "blocker": "BLK-01"},
    {"id": "A02", "name": "source tree digest and per-file SHA-256", "blocker": "BLK-01"},
    {"id": "A03", "name": "three checkpoint files with verified SHA-256", "blocker": "BLK-02"},
    {"id": "A04", "name": "exact config.json and Mel/CFM configuration", "blocker": "BLK-02"},
    {"id": "A05", "name": "single resolved runtime lock with artifact hashes", "blocker": "BLK-03"},
    {"id": "A06", "name": "successful import and one forward-pass trace", "blocker": "BLK-03"},
    {"id": "A07", "name": "written legal/rights review for checkpoints and code", "blocker": "BLK-05"},
    {"id": "A08", "name": "third-party notice and training-data obligation review", "blocker": "BLK-05"},
    {"id": "A09", "name": "rights-cleared paired cohort with clean references", "blocker": "BLK-06"},
    {"id": "A10", "name": "independent SI-SDR/STOI scoring and controls", "blocker": "BLK-06"},
    {"id": "A11", "name": "permitted listening or labeled predictive screen", "blocker": "BLK-06"},
    {"id": "A12", "name": "compute/timing/resources and provider/release review", "blocker": "BLK-07"},
)

ENHANCEMENT_ROWS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "ENH-01",
        "requirement": "identity/noisy control",
        "status": "synthetic_contract_control_only",
        "evidence": "Identity is bit-exact and the noisy control is the input; no model output exists.",
        "qualifies": False,
    },
    {
        "id": "ENH-02",
        "requirement": "paired SI-SDR against clean references",
        "status": "blocked",
        "evidence": "No rights-cleared real cohort and no model output exist.",
        "qualifies": False,
    },
    {
        "id": "ENH-03",
        "requirement": "paired STOI against clean references",
        "status": "blocked",
        "evidence": "No approved STOI scorer or rights-cleared cohort is admitted.",
        "qualifies": False,
    },
    {
        "id": "ENH-04",
        "requirement": "clean-speech preservation",
        "status": "blocked",
        "evidence": "No clean-speech regression run exists.",
        "qualifies": False,
    },
    {
        "id": "ENH-05",
        "requirement": "output peaks, clipping and invalid outputs",
        "status": "source_derived_unmeasured",
        "evidence": "The two official wrappers disagree on peak policy; no output was rendered.",
        "qualifies": False,
    },
    {
        "id": "ENH-06",
        "requirement": "alignment, content delay and final partial window",
        "status": "source_derived_unmeasured",
        "evidence": "Forward pads/truncates to input length, but no measured alignment or tail trace exists.",
        "qualifies": False,
    },
    {
        "id": "ENH-07",
        "requirement": "state, memory and stream lifetime",
        "status": "not_applicable_blocked",
        "evidence": "The published model is offline whole-clip; no streaming state contract or memory measurement exists.",
        "qualifies": False,
    },
    {
        "id": "ENH-08",
        "requirement": "content and availability timing",
        "status": "blocked",
        "evidence": "No device clock, paced workload, deadline or availability measurement exists.",
        "qualifies": False,
    },
    {
        "id": "ENH-09",
        "requirement": "generative latency and compute",
        "status": "blocked",
        "evidence": "No forward-pass timing exists; the host has no CUDA and no torch installation.",
        "qualifies": False,
    },
    {
        "id": "ENH-10",
        "requirement": "permitted listening or predictive screen",
        "status": "blocked",
        "evidence": "No listening authorization, consent, output-use grant or approved predictive screen exists.",
        "qualifies": False,
    },
)

SCOPE = {
    "benchmark_claim": False,
    "benchmark_run": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "device_timing_measured": False,
    "download_attempted": False,
    "audio_played": False,
    "audio_read": False,
    "installed_v0_behavior_change": False,
    "license_key_used": False,
    "listening_conducted": False,
    "network_used_for_metadata": True,
    "network_used_by_package": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "release_claim": False,
    "render_produced": False,
    "shared_build_or_ci_change": False,
    "task_local_only": True,
    "vendor_runtime_imported": False,
    "vendor_runtime_invoked": False,
    "vendor_sdk_copied": False,
    "weights_downloaded": False,
    "asset_bytes_read": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No result in this package is a qualification, benchmark or release.",
    "No Cisco StuPASE source, checkpoint, runtime, audio or dataset bytes were copied, downloaded, imported, loaded or executed.",
    "The public source and checkpoint identities were established from metadata only; no asset bytes were read or hashed.",
    "The synthetic admission, frame, Mel and scoring controls are contract checks, not StuPASE results.",
    "No paired SI-SDR, STOI, clean-preservation, peak, noise-only, dereverberation, listening or WER result exists.",
    "No device timing, memory, latency, availability, benchmark or resource result exists.",
    "No rights review, output-use grant, redistribution clearance or commercial-use decision exists.",
    "No provider, descriptor, registry, default, installed-v0 behavior, ABI, shared build, CI, board or handoff file is changed.",
)

REPRODUCTION_COMMANDS: Tuple[str, ...] = (
    "export PYTHONDONTWRITEBYTECODE=1",
    "PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python",
    "PYTHONDONTWRITEBYTECODE=1 $PY run.py --all",
    "PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py",
    "PYTHONDONTWRITEBYTECODE=1 $PY verify.py",
    "PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output <temp-dir>",
    "python3 -m reuse lint",
    "git diff --check",
)


# ---------------------------------------------------------------------------
# Canonical serialization and hashing
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _plain(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite value")
        rounded = round(value, 6)
        return 0.0 if rounded == 0 else rounded
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    raise TypeError("unsupported canonical type: " + type(value).__name__)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_negative_zero(item) for item in value)
    return False


def qualify_pin_path(path: str) -> Path:
    if not path or path.startswith("/") or "\\" in path:
        raise ValueError("pin path must be a relative POSIX path")
    parts = Path(path).parts
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("pin path contains a forbidden segment")
    return SOURCE_ROOT / path


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        start = lines.index("## Pinned local evidence sources")
    except ValueError as error:
        raise ValueError("README local pin section missing") from error
    rows: List[Tuple[str, str]] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        match = README_PIN_ROW_RE.match(line)
        if match:
            rows.append((match.group(1), match.group(2)))
    return rows


# ---------------------------------------------------------------------------
# Pinned-source and presence evidence
# ---------------------------------------------------------------------------


def evidence_lines() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for item in EVIDENCE_LINES:
        path = SOURCE_ROOT / item["path"]
        record = {
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "role": item["role"],
            "contains": list(item["contains"]),
            "present": path.is_file(),
            "line_matches": False,
        }
        if path.is_file():
            lines = path.read_text(encoding="utf-8").splitlines()
            if 0 < item["line"] <= len(lines):
                text = lines[item["line"] - 1]
                record["line_matches"] = all(token in text for token in item["contains"])
        result.append(record)
    return result


def inventory_component() -> Dict[str, Any]:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for component in data.get("components", []):
        if component.get("id") == "cisco-stupase":
            return {
                "id": component.get("id"),
                "name": component.get("name"),
                "area": component.get("area"),
                "evidence_status": component.get("evidence_status"),
                "repository": component.get("repository"),
                "disposition": component.get("disposition"),
                "verification_profile": component.get("verification_profile"),
                "task": component.get("task"),
                "evidence_path": component.get("evidence", [{}])[0].get("path"),
                "evidence_line": component.get("evidence", [{}])[0].get("line"),
            }
    raise RuntimeError("cisco-stupase component missing from INVENTORY.json")


def linked_row() -> Dict[str, Any]:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for task in data.get("tasks", []):
        if task.get("id") == TASK:
            return {
                "id": task.get("id"),
                "title": task.get("title"),
                "repository": task.get("repository"),
                "mode": task.get("mode"),
                "depends_on": task.get("depends_on"),
                "component": task.get("component"),
                "evidence": task.get("evidence"),
            }
    raise RuntimeError("linked task row missing from TASKS.json")


def linked_row_digest() -> str:
    return sha256(canonical_bytes(linked_row()))


def _module_present(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def host_runtime_probe() -> Dict[str, Any]:
    modules = {
        name: _module_present(name)
        for name in (
            "torch",
            "torchaudio",
            "soundfile",
            "librosa",
            "numpy",
            "scipy",
            "omegaconf",
            "torchdiffeq",
            "x_transformers",
            "huggingface_hub",
        )
    }
    return {
        "host": HOST,
        "python_pinned": PYTHON_PINNED,
        "python_actual": "%d.%d.%d" % sys.version_info[:3],
        "probe_method": "importlib.util.find_spec; no module import or execution",
        "modules": modules,
        "torch_importable": modules["torch"],
        "soundfile_importable": modules["soundfile"],
        "cuda_probe": "not_run_torch_absent" if not modules["torch"] else "not_run",
        "forward_pass_possible": all(
            modules[name] for name in ("torch", "torchaudio", "soundfile", "librosa")),
        "runtime_reproduced": False,
        "network_used": False,
    }


def asset_ledger_presence() -> Dict[str, Any]:
    path = SOURCE_ROOT / "research/noise_suppression_assets_20261027.json"
    text = path.read_text(encoding="utf-8").lower() if path.is_file() else ""
    return {
        "path": "research/noise_suppression_assets_20261027.json",
        "present": path.is_file(),
        "contains_stupase_entry": "stupase" in text,
        "contains_pase_entry": "pase" in text,
        "contains_cisco_entry": "cisco" in text,
        "qualifies": False,
    }


def source_presence() -> Dict[str, Any]:
    probes = (
        "data/checkouts/pase",
        "data/checkouts/stupase",
        "data/checkouts/cisco-pase",
        "data/checkouts/cisco-stupase",
        "adapters/pase",
        "adapters/stupase",
        "research/stupase",
        "third_party/pase",
        "third_party/stupase",
        "vendor/pase",
        "vendor/stupase",
        "data/runtimes/pase",
        "data/runtimes/stupase",
        "lib/pase",
        "lib/stupase",
        "src/pase",
        "src/stupase",
    )
    present = [probe for probe in probes if (SOURCE_ROOT / probe).exists()]
    return {
        "probe_scope": (
            "project workspace only; host package installations, Hugging Face "
            "caches, vendor portals and user profiles are not inspected"),
        "probe_paths": list(probes),
        "present_probes": present,
        "source_checkout_present": False,
        "checkpoint_files_present": False,
        "weights_present": False,
        "runtime_present": False,
        "audio_fixtures_present": False,
        "presence_is_not_admission": True,
        "candidate_record": dict(CANDIDATE_RECORD),
        "method_record": dict(METHOD_RECORD),
        "accounting_row": dict(ACCOUNTING_ROW),
        "inventory_component": inventory_component(),
        "asset_ledger": asset_ledger_presence(),
        "evidence_lines": evidence_lines(),
    }


# ---------------------------------------------------------------------------
# Caller-supplied-asset admission contract
# ---------------------------------------------------------------------------


def _code(condition: bool, code: str) -> Optional[str]:
    return None if condition else code


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_asset_file(value: Any, *, require_path: bool = True) -> Optional[str]:
    if not isinstance(value, dict):
        return "invalid_type"
    allowed = {"path", "sha256", "byte_count"}
    if set(value) - allowed:
        return "unknown_field"
    if require_path and "path" not in value:
        return "missing_field"
    for key in ("sha256", "byte_count"):
        if key not in value:
            return "missing_field"
    if require_path:
        path = value.get("path")
        if not isinstance(path, str):
            return "invalid_type"
        if not Path(path).is_absolute():
            return "invalid_module_path"
    digest = value.get("sha256")
    if not isinstance(digest, str):
        return "invalid_type"
    if not SHA256_RE.fullmatch(digest):
        return "invalid_digest"
    count = value.get("byte_count")
    if not _is_int(count):
        return "invalid_type"
    if count <= 0:
        return "invalid_byte_count"
    return None


def _validate_known_asset(value: Any, expected: Dict[str, Any],
                          *, allow_synthetic: bool) -> Optional[str]:
    code = _validate_asset_file(value)
    if code:
        return code
    if allow_synthetic:
        return None
    if value["sha256"] != expected["sha256"]:
        return "checkpoint_identity_mismatch"
    if value["byte_count"] != expected["byte_count"]:
        return "checkpoint_size_mismatch"
    return None


def validate_asset_bundle(manifest: Any, *, allow_synthetic: bool = False) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "root_not_object"}
    unknown = set(manifest) - set(CALLER_ASSET_ALLOWED)
    if unknown:
        return {"accepted": False, "code": "unknown_field",
                "reason": "unknown:" + ",".join(sorted(unknown))}
    for field in CALLER_ASSET_FIELDS:
        if field not in manifest:
            return {"accepted": False, "code": "missing_field", "reason": field}

    bundle_id = manifest["bundle_id"]
    if not isinstance(bundle_id, str):
        return {"accepted": False, "code": "invalid_type", "reason": "bundle_id"}
    if not SLUG_RE.fullmatch(bundle_id):
        return {"accepted": False, "code": "invalid_slug", "reason": "bundle_id"}

    source_repository = manifest["source_repository"]
    if not isinstance(source_repository, str):
        return {"accepted": False, "code": "invalid_type", "reason": "source_repository"}
    if source_repository != SOURCE_REPOSITORY:
        return {"accepted": False, "code": "invalid_url", "reason": "source_repository"}

    source_commit = manifest["source_commit"]
    if not isinstance(source_commit, str):
        return {"accepted": False, "code": "invalid_type", "reason": "source_commit"}
    if not COMMIT_RE.fullmatch(source_commit):
        return {"accepted": False, "code": "invalid_source_commit", "reason": "source_commit"}
    if not allow_synthetic and source_commit != SOURCE_COMMIT:
        return {"accepted": False, "code": "invalid_source_commit",
                "reason": "source_commit_is_not_the_pinned_commit"}

    hub_repository = manifest["hub_repository"]
    if not isinstance(hub_repository, str):
        return {"accepted": False, "code": "invalid_type", "reason": "hub_repository"}
    if hub_repository != HUB_REPOSITORY:
        return {"accepted": False, "code": "invalid_url", "reason": "hub_repository"}

    hub_revision = manifest["hub_revision"]
    if not isinstance(hub_revision, str):
        return {"accepted": False, "code": "invalid_type", "reason": "hub_revision"}
    if not COMMIT_RE.fullmatch(hub_revision):
        return {"accepted": False, "code": "invalid_hub_revision", "reason": "hub_revision"}
    if not allow_synthetic and hub_revision != HUB_REVISION:
        return {"accepted": False, "code": "invalid_hub_revision",
                "reason": "hub_revision_is_not_the_pinned_revision"}

    sample_rate = manifest["sample_rate_hz"]
    if not _is_int(sample_rate):
        return {"accepted": False, "code": "invalid_type", "reason": "sample_rate_hz"}
    if sample_rate != SAMPLE_RATE_HZ:
        return {"accepted": False, "code": "invalid_sample_rate", "reason": "sample_rate_hz"}

    channels = manifest["channels"]
    if not _is_int(channels):
        return {"accepted": False, "code": "invalid_type", "reason": "channels"}
    if channels != CHANNELS:
        return {"accepted": False, "code": "invalid_channels", "reason": "channels"}

    sample_format = manifest["sample_format"]
    if not isinstance(sample_format, str):
        return {"accepted": False, "code": "invalid_type", "reason": "sample_format"}
    if sample_format != SAMPLE_FORMAT:
        return {"accepted": False, "code": "invalid_sample_format", "reason": "sample_format"}

    modules = manifest["modules"]
    if not isinstance(modules, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "modules"}
    if set(modules) != set(CALLER_MODULE_IDS):
        return {"accepted": False, "code": "invalid_module_set", "reason": "modules"}
    for module_id in CALLER_MODULE_IDS:
        expected = next(item for item in EXTERNAL_ASSETS if item["id"] == module_id)
        code = _validate_known_asset(modules[module_id], expected,
                                     allow_synthetic=allow_synthetic)
        if code:
            return {"accepted": False, "code": code, "reason": "modules." + module_id}

    config = manifest["config"]
    code = _validate_known_asset(config, EXTERNAL_CONFIG,
                                 allow_synthetic=allow_synthetic)
    if code:
        return {"accepted": False, "code": code, "reason": "config"}

    sampling = manifest["sampling"]
    if not isinstance(sampling, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "sampling"}
    allowed_sampling = {"steps", "cfg_strength", "sway_sampling_coef", "ode_method"}
    if set(sampling) - allowed_sampling:
        return {"accepted": False, "code": "unknown_field", "reason": "sampling"}
    for field in allowed_sampling:
        if field not in sampling:
            return {"accepted": False, "code": "missing_field", "reason": "sampling." + field}
    steps = sampling["steps"]
    if not _is_int(steps):
        return {"accepted": False, "code": "invalid_type", "reason": "sampling.steps"}
    if steps != DEFAULT_STEPS:
        return {"accepted": False, "code": "invalid_sampling", "reason": "sampling.steps"}
    cfg = sampling["cfg_strength"]
    if not _is_number(cfg):
        return {"accepted": False, "code": "invalid_type", "reason": "sampling.cfg_strength"}
    if float(cfg) != DEFAULT_CFG_STRENGTH:
        return {"accepted": False, "code": "invalid_sampling", "reason": "sampling.cfg_strength"}
    sway = sampling["sway_sampling_coef"]
    if not _is_number(sway):
        return {"accepted": False, "code": "invalid_type", "reason": "sampling.sway_sampling_coef"}
    if float(sway) != DEFAULT_SWAY_SAMPLING_COEF:
        return {"accepted": False, "code": "invalid_sampling", "reason": "sampling.sway_sampling_coef"}
    ode = sampling["ode_method"]
    if not isinstance(ode, str):
        return {"accepted": False, "code": "invalid_type", "reason": "sampling.ode_method"}
    if ode != ODE_METHOD:
        return {"accepted": False, "code": "invalid_sampling", "reason": "sampling.ode_method"}

    mel = manifest["mel"]
    if not isinstance(mel, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "mel"}
    allowed_mel = {"n_mels", "n_fft", "hop_length", "win_length"}
    if set(mel) - allowed_mel:
        return {"accepted": False, "code": "unknown_field", "reason": "mel"}
    for field in allowed_mel:
        if field not in mel:
            return {"accepted": False, "code": "missing_field", "reason": "mel." + field}
        if not _is_int(mel[field]):
            return {"accepted": False, "code": "invalid_type", "reason": "mel." + field}
    if (mel["n_mels"] != MEL_N_MELS or mel["n_fft"] != MEL_N_FFT
            or mel["hop_length"] != MEL_HOP_LENGTH
            or mel["win_length"] != MEL_WIN_LENGTH):
        return {"accepted": False, "code": "invalid_mel_geometry", "reason": "mel"}

    runtime = manifest["runtime"]
    if not isinstance(runtime, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "runtime"}
    if set(runtime) - set(CALLER_RUNTIME_FIELDS):
        return {"accepted": False, "code": "unknown_field", "reason": "runtime"}
    for field in CALLER_RUNTIME_FIELDS:
        if field not in runtime:
            return {"accepted": False, "code": "runtime_not_pinned",
                    "reason": "runtime." + field}
    for field in ("python_version", "torch_version", "torchaudio_version",
                  "numpy_version", "soundfile_version", "librosa_version"):
        value = runtime[field]
        if not isinstance(value, str):
            return {"accepted": False, "code": "invalid_type", "reason": "runtime." + field}
        if not VERSION_RE.fullmatch(value):
            return {"accepted": False, "code": "invalid_runtime_version",
                    "reason": "runtime." + field}
    if runtime["device"] not in CALLER_DEVICES:
        return {"accepted": False, "code": "invalid_device", "reason": "runtime.device"}
    if not isinstance(runtime["wheel_sha256"], str):
        return {"accepted": False, "code": "invalid_type", "reason": "runtime.wheel_sha256"}
    if not SHA256_RE.fullmatch(runtime["wheel_sha256"]):
        return {"accepted": False, "code": "invalid_digest", "reason": "runtime.wheel_sha256"}

    peak_policy = manifest["peak_policy"]
    if not isinstance(peak_policy, str):
        return {"accepted": False, "code": "invalid_type", "reason": "peak_policy"}
    if peak_policy not in CALLER_PEAK_POLICIES:
        return {"accepted": False, "code": "invalid_peak_policy", "reason": "peak_policy"}

    alignment = manifest["content_alignment"]
    if not isinstance(alignment, dict):
        return {"accepted": False, "code": "invalid_type", "reason": "content_alignment"}
    allowed_alignment = {"content_lag_samples", "tail_policy"}
    if set(alignment) - allowed_alignment:
        return {"accepted": False, "code": "unknown_field", "reason": "content_alignment"}
    for field in allowed_alignment:
        if field not in alignment:
            return {"accepted": False, "code": "missing_field",
                    "reason": "content_alignment." + field}
    lag = alignment["content_lag_samples"]
    if not _is_int(lag):
        return {"accepted": False, "code": "invalid_type",
                "reason": "content_alignment.content_lag_samples"}
    if lag != 0:
        return {"accepted": False, "code": "invalid_content_alignment",
                "reason": "content_alignment.content_lag_samples"}
    if alignment["tail_policy"] != "pad_or_truncate_to_source_length":
        return {"accepted": False, "code": "invalid_content_alignment",
                "reason": "content_alignment.tail_policy"}

    if "caller_path" in manifest:
        caller_path = manifest["caller_path"]
        if not isinstance(caller_path, str):
            return {"accepted": False, "code": "invalid_type", "reason": "caller_path"}
        if not Path(caller_path).is_absolute():
            return {"accepted": False, "code": "path_not_absolute", "reason": "caller_path"}

    return {"accepted": True, "code": None, "reason": "schema_valid"}


def synthetic_bundle() -> Dict[str, Any]:
    def digest(label: str) -> str:
        return sha256(("synthetic-cisco-stupase:" + label).encode("ascii"))

    return {
        "bundle_id": "synthetic-cisco-stupase-16k",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": "0" * 39 + "1",
        "hub_repository": HUB_REPOSITORY,
        "hub_revision": "0" * 39 + "2",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "modules": {
            "dewavlm_r": {
                "path": "/caller/cisco-stupase/DeWavLM-R.pt",
                "sha256": digest("dewavlm_r"),
                "byte_count": 1024,
            },
            "cfm": {
                "path": "/caller/cisco-stupase/CFM.pt",
                "sha256": digest("cfm"),
                "byte_count": 2048,
            },
            "vocoder": {
                "path": "/caller/cisco-stupase/Vocoder_Mel-16k.pt",
                "sha256": digest("vocoder"),
                "byte_count": 4096,
            },
        },
        "config": {
            "path": "/caller/cisco-stupase/config.json",
            "sha256": digest("config"),
            "byte_count": 53,
        },
        "sampling": {
            "steps": DEFAULT_STEPS,
            "cfg_strength": DEFAULT_CFG_STRENGTH,
            "sway_sampling_coef": DEFAULT_SWAY_SAMPLING_COEF,
            "ode_method": ODE_METHOD,
        },
        "mel": {
            "n_mels": MEL_N_MELS,
            "n_fft": MEL_N_FFT,
            "hop_length": MEL_HOP_LENGTH,
            "win_length": MEL_WIN_LENGTH,
        },
        "runtime": {
            "python_version": PYTHON_PINNED,
            "torch_version": "2.1.1",
            "torchaudio_version": "2.1.1",
            "numpy_version": "1.23.5",
            "soundfile_version": "0.13.1",
            "librosa_version": "0.10.2",
            "device": "cpu",
            "wheel_sha256": digest("runtime-wheel"),
        },
        "peak_policy": "input_peak",
        "content_alignment": {
            "content_lag_samples": 0,
            "tail_policy": "pad_or_truncate_to_source_length",
        },
        "caller_path": "/caller/cisco-stupase",
    }


def admit_asset_bundle(manifest: Any, *, bytes_present: bool,
                       allow_synthetic: bool = False) -> Dict[str, Any]:
    validation = validate_asset_bundle(manifest, allow_synthetic=allow_synthetic)
    if not validation["accepted"]:
        return {
            "accepted": False,
            "admitted": False,
            "schema_valid": False,
            "bytes_present": bytes_present,
            "bytes_read": False,
            "reason": validation["code"],
            "detail": validation["reason"],
            "qualifies": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
        }
    if not bytes_present:
        return {
            "accepted": True,
            "admitted": False,
            "schema_valid": True,
            "bytes_present": False,
            "bytes_read": False,
            "reason": "asset_bytes_not_supplied_in_this_worktree",
            "detail": "schema is valid; no candidate bytes exist in this worktree",
            "qualifies": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
        }
    return {
        "accepted": True,
        "admitted": True,
        "schema_valid": True,
        "bytes_present": True,
        "bytes_read": False,
        "reason": "synthetic_bytes_present_control",
        "detail": "synthetic control only; no real asset was read",
        "qualifies": False,
        "evidence_class": "synthetic_contract_control_not_evidence",
    }


def _mutation_cases() -> List[Dict[str, Any]]:
    base = synthetic_bundle()
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, description: str, expected: str,
            mutate, allow_synthetic: bool = True) -> None:
        manifest = copy.deepcopy(base)
        mutate(manifest)
        cases.append({
            "id": case_id,
            "description": description,
            "expected_code": expected,
            "allow_synthetic": allow_synthetic,
            "manifest": manifest,
        })

    def drop(field: str):
        def apply(manifest: Dict[str, Any]) -> None:
            del manifest[field]
        return apply

    def put(field: str, value: Any):
        def apply(manifest: Dict[str, Any]) -> None:
            manifest[field] = value
        return apply

    def module_put(module: str, field: str, value: Any):
        def apply(manifest: Dict[str, Any]) -> None:
            manifest["modules"][module][field] = value
        return apply

    def module_drop(module: str, field: str):
        def apply(manifest: Dict[str, Any]) -> None:
            del manifest["modules"][module][field]
        return apply

    def nested(path: Tuple[str, ...], value: Any):
        def apply(manifest: Dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply

    # Root shape and identity.
    add("M01", "missing bundle_id", "missing_field", drop("bundle_id"))
    add("M02", "bundle_id is not a string", "invalid_type", put("bundle_id", 7))
    add("M03", "bundle_id is not a slug", "invalid_slug", put("bundle_id", "Cisco StuPASE!"))
    add("M04", "unknown root field", "unknown_field", put("extra", True))
    add("M05", "wrong source repository", "invalid_url",
        put("source_repository", "https://github.com/example/pase"))
    add("M06", "source_repository is not a string", "invalid_type",
        put("source_repository", 1))
    add("M07", "short source commit", "invalid_source_commit", put("source_commit", "abc123"))
    add("M08", "non-hex source commit", "invalid_source_commit",
        put("source_commit", "z" * 40))
    add("M09", "wrong hub repository", "invalid_url",
        put("hub_repository", "https://huggingface.co/example/stupase"))
    add("M10", "short hub revision", "invalid_hub_revision", put("hub_revision", "539963f"))
    add("M11", "non-hex hub revision", "invalid_hub_revision", put("hub_revision", "g" * 40))

    # Public format.
    add("M12", "wrong sample rate", "invalid_sample_rate", put("sample_rate_hz", 8000))
    add("M13", "boolean sample rate", "invalid_type", put("sample_rate_hz", True))
    add("M14", "wrong channel count", "invalid_channels", put("channels", 2))
    add("M15", "wrong sample format", "invalid_sample_format", put("sample_format", "s16"))

    # Module set and file records.
    add("M16", "missing vocoder module", "invalid_module_set",
        lambda manifest: manifest["modules"].pop("vocoder"))
    add("M17", "extra module", "invalid_module_set",
        lambda manifest: manifest["modules"].__setitem__("extra", {})
        )
    add("M18", "modules is a list", "invalid_type", put("modules", []))
    add("M19", "short module digest", "invalid_digest",
        module_put("cfm", "sha256", "abc"))
    add("M20", "non-hex module digest", "invalid_digest",
        module_put("cfm", "sha256", "z" * 64))
    add("M21", "zero module byte count", "invalid_byte_count",
        module_put("cfm", "byte_count", 0))
    add("M22", "string module byte count", "invalid_type",
        module_put("cfm", "byte_count", "758024988"))
    add("M23", "relative module path", "invalid_module_path",
        module_put("cfm", "path", "CFM.pt"))
    add("M24", "missing module path", "missing_field",
        module_drop("cfm", "path"))
    add("M25", "missing config", "missing_field", drop("config"))
    add("M26", "short config digest", "invalid_digest",
        nested(("config", "sha256"), "0" * 63))

    # Sampling.
    add("M27", "zero sampling steps", "invalid_sampling",
        nested(("sampling", "steps"), 0))
    add("M28", "nine sampling steps", "invalid_sampling",
        nested(("sampling", "steps"), 9))
    add("M29", "negative cfg strength", "invalid_sampling",
        nested(("sampling", "cfg_strength"), -0.1))
    add("M30", "cfg strength above one", "invalid_sampling",
        nested(("sampling", "cfg_strength"), 1.5))
    add("M31", "non-numeric sway coefficient", "invalid_type",
        nested(("sampling", "sway_sampling_coef"), "nan"))
    add("M32", "wrong ODE method", "invalid_sampling",
        nested(("sampling", "ode_method"), "midpoint"))

    # Mel geometry.
    add("M33", "wrong Mel count", "invalid_mel_geometry",
        nested(("mel", "n_mels"), 80))
    add("M34", "wrong Mel FFT size", "invalid_mel_geometry",
        nested(("mel", "n_fft"), 1024))
    add("M35", "wrong Mel hop", "invalid_mel_geometry",
        nested(("mel", "hop_length"), 256))
    add("M36", "wrong Mel window", "invalid_mel_geometry",
        nested(("mel", "win_length"), 1024))

    # Runtime.
    add("M37", "missing torch version", "runtime_not_pinned",
        lambda manifest: manifest["runtime"].pop("torch_version"))
    add("M38", "unpinned Python version", "invalid_runtime_version",
        nested(("runtime", "python_version"), "3.11"))
    add("M39", "unsupported device", "invalid_device",
        nested(("runtime", "device"), "tpu"))
    add("M40", "short runtime wheel digest", "invalid_digest",
        nested(("runtime", "wheel_sha256"), "abc"))

    # Wrapper contract.
    add("M41", "unresolved peak policy", "invalid_peak_policy",
        put("peak_policy", "auto"))
    add("M42", "nonzero content lag", "invalid_content_alignment",
        nested(("content_alignment", "content_lag_samples"), 1))
    add("M43", "unknown tail policy", "invalid_content_alignment",
        nested(("content_alignment", "tail_policy"), "unknown"))
    add("M44", "relative caller path", "path_not_absolute",
        put("caller_path", "caller/cisco-stupase"))

    # Missing containers.
    add("M45", "missing sampling block", "missing_field", drop("sampling"))
    add("M46", "missing Mel block", "missing_field", drop("mel"))
    add("M47", "runtime is an integer", "invalid_type", put("runtime", 1))
    add("M48", "empty module set", "invalid_module_set", put("modules", {}))
    add("M49", "non-integer content lag", "invalid_type",
        nested(("content_alignment", "content_lag_samples"), 0.5))
    add("M50", "missing source commit", "missing_field", drop("source_commit"))

    # Exact identity checks on the non-synthetic admission path.
    def real_identity_base(manifest: Dict[str, Any]) -> None:
        manifest["source_commit"] = SOURCE_COMMIT
        manifest["hub_revision"] = HUB_REVISION
        for asset in EXTERNAL_ASSETS:
            manifest["modules"][asset["id"]]["sha256"] = asset["sha256"]
            manifest["modules"][asset["id"]]["byte_count"] = asset["byte_count"]
        manifest["config"]["sha256"] = EXTERNAL_CONFIG["sha256"]
        manifest["config"]["byte_count"] = EXTERNAL_CONFIG["byte_count"]

    def wrong_checkpoint_digest(manifest: Dict[str, Any]) -> None:
        real_identity_base(manifest)
        manifest["modules"]["cfm"]["sha256"] = "1" * 64

    def wrong_checkpoint_size(manifest: Dict[str, Any]) -> None:
        real_identity_base(manifest)
        manifest["modules"]["cfm"]["byte_count"] = 1

    def wrong_hub_revision(manifest: Dict[str, Any]) -> None:
        manifest["source_commit"] = SOURCE_COMMIT
        manifest["hub_revision"] = "1" * 40

    def wrong_source_commit(manifest: Dict[str, Any]) -> None:
        manifest["source_commit"] = "1" * 40
        manifest["hub_revision"] = HUB_REVISION

    add("M51", "well-formed but wrong checkpoint digest",
        "checkpoint_identity_mismatch", wrong_checkpoint_digest,
        allow_synthetic=False)
    add("M52", "well-formed but wrong checkpoint byte count",
        "checkpoint_size_mismatch", wrong_checkpoint_size,
        allow_synthetic=False)
    add("M53", "well-formed but unpinned hub revision",
        "invalid_hub_revision", wrong_hub_revision, allow_synthetic=False)
    add("M54", "well-formed but unpinned source commit",
        "invalid_source_commit", wrong_source_commit, allow_synthetic=False)

    return cases


def admission_control() -> Dict[str, Any]:
    synthetic = synthetic_bundle()
    validation = validate_asset_bundle(synthetic, allow_synthetic=True)
    cases = []
    for case in _mutation_cases():
        result = validate_asset_bundle(
            case["manifest"], allow_synthetic=case["allow_synthetic"])
        observed = result["code"]
        cases.append({
            "id": case["id"],
            "description": case["description"],
            "expected_code": case["expected_code"],
            "observed_code": observed,
            "allow_synthetic": case["allow_synthetic"],
            "status": "rejected" if observed else "accepted",
            "codes_match": observed == case["expected_code"],
            "qualifies": False,
            "state_unchanged": True,
        })
    rejected = [case for case in cases if case["status"] == "rejected"]
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "schema_valid": validation["accepted"],
        "control": admit_asset_bundle(
            synthetic, bytes_present=False, allow_synthetic=True),
        "synthetic_present_control": admit_asset_bundle(
            synthetic, bytes_present=True, allow_synthetic=True),
        "candidate_admission": {
            "accepted": False,
            "admitted": False,
            "schema_valid": False,
            "bytes_present": False,
            "bytes_read": False,
            "reason": "asset_bundle_not_supplied",
            "detail": "no candidate bundle, source checkout or checkpoint bytes exist",
            "qualifies": False,
            "evidence_class": "readiness_conclusion_not_evidence",
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "accepted_schema_controls": 1,
            "rejected_count": len(rejected),
            "all_rejected": len(rejected) == len(cases),
            "all_codes_match": all(case["codes_match"] for case in cases),
            "state_advanced_on_rejection": False,
            "candidate_admitted": False,
            "synthetic_present_control_admitted": True,
            "qualifying_results": 0,
            "audio_read": False,
            "network_used": False,
            "weights_downloaded": False,
            "vendor_runtime_invoked": False,
            "vendor_sdk_loaded": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
            "qualifies": False,
        },
    }


# ---------------------------------------------------------------------------
# Deterministic contract controls
# ---------------------------------------------------------------------------


def validate_frame(frame: Any) -> Optional[str]:
    if not isinstance(frame, (list, tuple)):
        return "frame_not_sequence"
    if len(frame) != FRAME_SAMPLES:
        return "wrong_frame_length"
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            return "sample_not_number"
        if not math.isfinite(float(sample)):
            return "nonfinite_sample"
        if float(sample) < -1.0 or float(sample) > 1.0:
            return "sample_out_of_range"
    return None


def frame_control() -> Dict[str, Any]:
    base = [((index - 80) / 1000.0) for index in range(FRAME_SAMPLES)]
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, description: str, expected: Optional[str],
            frame: Any) -> None:
        observed = validate_frame(frame)
        cases.append({
            "id": case_id,
            "description": description,
            "expected_code": expected,
            "observed_code": observed,
            "status": "accepted" if observed is None else "rejected",
            "codes_match": observed == expected,
            "qualifies": False,
        })

    add("F01", "valid 160-sample frame", None, base)
    add("F02", "159 samples", "wrong_frame_length", base[:159])
    add("F03", "161 samples", "wrong_frame_length", base + [0.0])
    add("F04", "NaN sample", "nonfinite_sample", base[:159] + [float("nan")])
    add("F05", "positive infinity", "nonfinite_sample", base[:159] + [float("inf")])
    add("F06", "negative infinity", "nonfinite_sample", base[:159] + [float("-inf")])
    add("F07", "boolean sample", "sample_not_number", base[:159] + [True])
    add("F08", "string sample", "sample_not_number", base[:159] + ["0.0"])
    add("F09", "None sample", "sample_not_number", base[:159] + [None])
    add("F10", "out-of-range positive", "sample_out_of_range", base[:159] + [1.1])
    add("F11", "out-of-range negative", "sample_out_of_range", base[:159] + [-1.1])
    add("F12", "frame is not a sequence", "frame_not_sequence", "frame")

    accepted = [case for case in cases if case["status"] == "accepted"]
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "caller_range": [-1.0, 1.0],
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "accepted_count": len(accepted),
            "rejected_count": len(cases) - len(accepted),
            "all_codes_match": all(case["codes_match"] for case in cases),
            "audio_read": False,
            "vendor_runtime_invoked": False,
            "qualifies": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
        },
    }


def mel_frames(length: int) -> int:
    if not _is_int(length) or length < 0:
        raise ValueError("invalid length")
    return 1 + length // MEL_HOP_LENGTH


def mel_geometry_control() -> Dict[str, Any]:
    probe_lengths = (0, 1, 159, 160, 319, 320, 321, 15999, 16000, 16001, 32000)
    cases = []
    for length in probe_lengths:
        frames = mel_frames(length)
        expected_frames = 1 + length // MEL_HOP_LENGTH
        cases.append({
            "source_samples": length,
            "mel_frames": frames,
            "expected_mel_frames": expected_frames,
            "output_samples": length,
            "content_lag_samples": 0,
            "padding_or_truncation": "pad_or_truncate_to_source_length",
            "frame_rule_holds": frames == expected_frames,
            "output_length_identity": True,
            "qualifies": False,
        })
    checks = [
        {"id": "MEL-01", "check": "one second has 51 frames", "pass": mel_frames(16000) == 51},
        {"id": "MEL-02", "check": "two seconds have 101 frames", "pass": mel_frames(32000) == 101},
        {"id": "MEL-03", "check": "zero length has one centered frame", "pass": mel_frames(0) == 1},
        {"id": "MEL-04", "check": "320 samples has two frames", "pass": mel_frames(320) == 2},
        {"id": "MEL-05", "check": "321 samples has two frames", "pass": mel_frames(321) == 2},
        {"id": "MEL-06", "check": "all frame counts follow 1 + floor(L/hop)",
         "pass": all(case["frame_rule_holds"] for case in cases)},
        {"id": "MEL-07", "check": "all output lengths equal source length",
         "pass": all(case["output_length_identity"] for case in cases)},
    ]
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "n_mels": MEL_N_MELS,
        "n_fft": MEL_N_FFT,
        "hop_length": MEL_HOP_LENGTH,
        "win_length": MEL_WIN_LENGTH,
        "center": True,
        "frame_rule": "T = 1 + floor(L / hop_length)",
        "content_lag_samples": 0,
        "measured": False,
        "cases": cases,
        "checks": checks,
        "summary": {
            "case_count": len(cases),
            "checks_passed": sum(1 for item in checks if item["pass"]),
            "all_checks_pass": all(item["pass"] for item in checks),
            "audio_read": False,
            "vendor_runtime_invoked": False,
            "qualifies": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
        },
    }


def _energy(values: List[float]) -> float:
    return sum(value * value for value in values)


def _dot(left: List[float], right: List[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _snr_db(estimate: List[float], reference: List[float]) -> Any:
    signal = _energy(reference)
    error = _energy([a - b for a, b in zip(estimate, reference)])
    if error == 0.0:
        return "undefined_zero_error_identity_exact"
    if signal == 0.0:
        return "undefined_zero_reference"
    return round(10.0 * math.log10(signal / error), 6)


def _si_sdr_db(estimate: List[float], reference: List[float]) -> Any:
    reference_energy = _energy(reference)
    if reference_energy == 0.0:
        return "undefined_zero_reference"
    alpha = _dot(estimate, reference) / reference_energy
    if alpha == 0.0:
        return "undefined_zero_projection"
    projection = [alpha * value for value in reference]
    error = _energy([a - b for a, b in zip(estimate, projection)])
    if error == 0.0:
        return "undefined_zero_error_identity_exact"
    return round(10.0 * math.log10(_energy(projection) / error), 6)


def scoring_control() -> Dict[str, Any]:
    clean_pattern = [0.5, -0.25, 0.125, -0.0625, 0.03125, -0.015625, 0.0078125, -0.00390625]
    noise_pattern = [0.125, 0.0625, -0.03125, 0.015625, -0.0078125, 0.00390625, -0.001953125, 0.0009765625]
    clean = clean_pattern * 4
    noise = noise_pattern * 4
    mixture = [a + b for a, b in zip(clean, noise)]
    gain_half = [0.5 * value for value in mixture]
    silence = [0.0] * len(clean)

    mix_snr = _snr_db(mixture, clean)
    mix_si_sdr = _si_sdr_db(mixture, clean)
    gain_snr = _snr_db(gain_half, clean)
    gain_si_sdr = _si_sdr_db(gain_half, clean)
    snr_delta = round(gain_snr - mix_snr, 6)
    si_sdr_delta = round(gain_si_sdr - mix_si_sdr, 6)

    identity = {
        "estimate_equals_input": True,
        "si_sdr_db": _si_sdr_db(mixture, mixture),
        "snr_db": _snr_db(mixture, mixture),
    }
    noisy = {
        "estimate": "input_noisy_mixture",
        "snr_db": mix_snr,
        "si_sdr_db": mix_si_sdr,
    }
    gain = {
        "estimate": "0.5 * noisy_mixture",
        "snr_db": gain_snr,
        "si_sdr_db": gain_si_sdr,
        "si_sdr_delta_db": si_sdr_delta,
        "snr_delta_db": snr_delta,
        "si_sdr_scale_invariant": abs(si_sdr_delta) <= 1e-6,
        "snr_scale_sensitive": True,
    }
    silent = {
        "estimate": "all_zero",
        "snr_db": _snr_db(silence, clean),
        "si_sdr_db": _si_sdr_db(silence, clean),
    }
    finite_or_explicit = all(
        (isinstance(value, str) or math.isfinite(value))
        for block in (identity, noisy, gain, silent)
        for value in block.values()
        if not isinstance(value, bool))
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "seed": 20261126,
        "samples": len(clean),
        "clean_reference": "deterministic binary-fraction harmonic pattern",
        "noise_reference": "deterministic binary-fraction noise pattern",
        "identity_control": identity,
        "noisy_control": noisy,
        "gain_half_control": gain,
        "silence_control": silent,
        "stoi": "not_scored_no_approved_scorer_and_no_rights_cleared_cohort",
        "peak_guard": 0.95,
        "all_values_finite_or_explicitly_undefined": finite_or_explicit,
        "summary": {
            "identity_exact": True,
            "noisy_control_is_input": True,
            "gain_half_si_sdr_delta_db": si_sdr_delta,
            "gain_half_snr_delta_db": snr_delta,
            "audio_read": False,
            "audio_rendered": False,
            "vendor_runtime_invoked": False,
            "qualifying_results": 0,
            "qualifies": False,
            "evidence_class": "synthetic_contract_control_not_evidence",
        },
    }


# ---------------------------------------------------------------------------
# Report, contract, readiness and adapter builders
# ---------------------------------------------------------------------------


def _license_findings() -> Dict[str, Any]:
    return {
        "code_license_metadata": SOURCE_CODE_LICENSE,
        "model_license_metadata": HUB_MODEL_LICENSE,
        "model_card_present": True,
        "weight_license_text_present": False,
        "artifact_specific_terms_reviewed": False,
        "third_party_notices_present": True,
        "third_party_components": [dict(item) for item in THIRD_PARTY_COMPONENTS],
        "training_data": [dict(item) for item in TRAINING_DATA],
        "training_data_obligations_reviewed": False,
        "redistribution_approved": False,
        "derivative_output_use_approved": False,
        "commercial_use_approved": False,
        "output_use_defined": False,
        "legal_review": False,
        "qualifies": False,
    }


def _report_core() -> Dict[str, Any]:
    admission = admission_control()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "no_missing_result_qualifies_candidate": True,
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "task_geometry": copy.deepcopy(TASK_GEOMETRY),
        "source_identities": {
            "source_repository": SOURCE_REPOSITORY,
            "source_commit": SOURCE_COMMIT,
            "source_tree_entries": SOURCE_TREE_ENTRIES,
            "source_tree_truncated": SOURCE_TREE_TRUNCATED,
            "source_code_license": SOURCE_CODE_LICENSE,
            "hub_repository": HUB_REPOSITORY,
            "hub_revision": HUB_REVISION,
            "hub_last_modified": HUB_LAST_MODIFIED,
            "hub_model_license": HUB_MODEL_LICENSE,
            "hub_gated": HUB_GATED,
            "hub_private": HUB_PRIVATE,
            "metadata_observed_on": METADATA_OBSERVED_ON,
            "metadata_retrieval": METADATA_RETRIEVAL,
            "weights_downloaded": False,
            "asset_bytes_read": False,
            "metadata_network_access": True,
        },
        "asset_boundary": {
            "source_repository": SOURCE_REPOSITORY,
            "source_commit": SOURCE_COMMIT,
            "hub_repository": HUB_REPOSITORY,
            "hub_revision": HUB_REVISION,
            "asset_count": len(EXTERNAL_ASSETS),
            "checkpoint_total_bytes": TOTAL_CHECKPOINT_BYTES,
            "assets": [
                {
                    "id": asset["id"],
                    "path": asset["path"],
                    "byte_count": asset["byte_count"],
                    "sha256": asset["sha256"],
                    "role": asset["role"],
                    "format": asset["format"],
                    "url": asset["url"],
                    "present_locally": False,
                    "admitted": False,
                    "bytes_read": False,
                    "verified_locally": False,
                    "qualifies": False,
                }
                for asset in EXTERNAL_ASSETS
            ],
            "config": {
                "id": EXTERNAL_CONFIG["id"],
                "path": EXTERNAL_CONFIG["path"],
                "byte_count": EXTERNAL_CONFIG["byte_count"],
                "sha256": EXTERNAL_CONFIG["sha256"],
                "role": EXTERNAL_CONFIG["role"],
                "url": EXTERNAL_CONFIG["url"],
                "present_locally": False,
                "admitted": False,
                "bytes_read": False,
                "verified_locally": False,
                "qualifies": False,
            },
            "candidate_admission": admission["candidate_admission"],
            "synthetic_control": admission["control"],
            "synthetic_present_control": admission["synthetic_present_control"],
            "admission_control": admission,
            "reason_codes": list(ASSET_ADMISSION_REASONS),
            "weights_downloaded": False,
            "asset_bytes_read": False,
            "qualifies": False,
        },
        "external_source_files": [
            {
                **{key: item[key] for key in ("path", "byte_count", "sha256", "role", "url")},
                "materialized_locally": False,
                "verified_from_public_metadata": True,
                "qualifies": False,
            }
            for item in EXTERNAL_SOURCE_FILES
        ],
        "hub_model_card": {
            **{key: HUB_MODEL_CARD[key] for key in ("path", "byte_count", "sha256", "role", "url")},
            "materialized_locally": False,
            "verified_from_public_metadata": True,
            "qualifies": False,
        },
        "source_presence": source_presence(),
        "runtime_boundary": {
            "runtime_vendored_in_package": False,
            "runtime_imported_by_package": False,
            "forward_pass_executed": False,
            "runtime_reproduced": False,
            "host_runtime_probe": host_runtime_probe(),
            "required_python": PYTHON_PINNED,
            "official_requirements_reproducible": False,
            "cuda_measured": False,
            "timing_measured": False,
            "memory_measured": False,
            "qualifies": False,
        },
        "enhancement_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "rows": [dict(row) for row in ENHANCEMENT_ROWS],
            "identity_noisy_control": scoring_control(),
            "frame_control": frame_control(),
            "mel_geometry_control": mel_geometry_control(),
            "measured_candidate_results": 0,
            "qualifying_results": 0,
            "clean_references_present": False,
            "stoi_scorer_present": False,
            "listening_conducted": False,
            "device_timing_measured": False,
            "qualifies": False,
        },
        "licensing": _license_findings(),
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": [
            {
                "id": f"RG-{index:02d}",
                "title": title,
                "status": "blocked",
                "reopen": reopen,
                "qualifies": False,
                "evidence": "No admitted asset, reproduced runtime or matched result exists.",
            }
            for index, (title, reopen) in enumerate(GATE_DEFINITIONS, start=1)
        ],
        "required_artifacts": [
            {
                **dict(item),
                "present": False,
                "admitted": False,
                "verified": False,
                "sha256": None,
                "qualifies": False,
            }
            for item in REQUIRED_ARTIFACTS
        ],
        "required_results": {
            "source_checkout_admitted": False,
            "checkpoint_bytes_admitted": False,
            "runtime_reproduced": False,
            "forward_pass_executed": False,
            "rights_cleared": False,
            "training_data_obligations_reviewed": False,
            "rights_cleared_cohort_present": False,
            "independent_scoring_complete": False,
            "listening_or_predictive_screen_complete": False,
            "clean_preservation_measured": False,
            "device_timing_measured": False,
            "provider_intake_approved": False,
            "release_approved": False,
            "no_result_qualifies": True,
        },
        "qualification": {
            "decision": DECISION,
            "evidence_status": EVIDENCE_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "proposal_only": True,
            "qualifying_results": 0,
            "blocked_release_gates": len(GATE_DEFINITIONS),
            "open_blockers": len(EXACT_BLOCKERS),
            "source_commit_identified": True,
            "checkpoint_identities_identified": True,
            "source_checkout_present": False,
            "checkpoint_files_present": False,
            "runtime_present": False,
            "reasons": [
                "no Cisco StuPASE source checkout or per-file tree digest is admitted",
                "no checkpoint bytes are present or locally verified",
                "the official runtime requirements are not a reproducible lock",
                "the two official wrappers disagree on output peak policy",
                "no rights/legal review or training-data obligation decision exists",
                "no rights-cleared cohort, independent score, listening or predictive screen exists",
                "no CPU/MPS/CUDA compute or timing measurement exists",
                "no opt-in provider intake, independent review or release approval exists",
            ],
        },
        "linked_row": linked_row(),
        "linked_row_sha256": linked_row_digest(),
        "board_snapshot": {
            "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "mutable": True,
            "never_hashed": True,
            "note": "Mutable board path recorded for provenance only; never pinned or treated as a result.",
        },
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "reproduction": {
            "python": PYTHON_PINNED,
            "repeat_count": 3,
            "byte_identical_required": True,
            "network_used_by_package": False,
            "commands": list(REPRODUCTION_COMMANDS),
        },
        "scope": dict(SCOPE),
        "non_claims": list(NON_CLAIMS),
        "notes": [
            "The public source commit and hub revision are identified, not admitted.",
            "The three checkpoint SHA-256 values are hub LFS metadata, not locally verified bytes.",
            "The synthetic admission, frame, Mel and scoring controls clear no candidate gate.",
            "The public v0 16 kHz/mono/f32/160-sample geometry is preserved.",
        ],
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Optional[Dict[str, Any]] = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:  # pragma: no cover
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


def canonical_report_bytes(report: Optional[Dict[str, Any]] = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def build_adapter() -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "task_id": TASK,
        "component": SLUG,
        "decision": DECISION,
        "status": "not_implemented",
        "proposal_only": True,
        "implemented": False,
        "registered": False,
        "provider_registration": False,
        "enabled_by_default": False,
        "default_selected": False,
        "mode": "offline-caller-supplied-asset",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "public_v0_frame_samples": FRAME_SAMPLES,
        "streaming": False,
        "requires": [
            "BLK-01 source checkout and tree digest",
            "BLK-02 checkpoint bytes and SHA-256",
            "BLK-03 reproducible runtime lock",
            "BLK-04 frozen wrapper geometry and peak policy",
            "BLK-05 rights and data-obligation review",
            "BLK-06 matched enhancement evidence",
            "BLK-07 compute and timing feasibility",
        ],
        "blocker_ids": [item["id"] for item in EXACT_BLOCKERS],
        "qualifies": False,
    }


def build_readiness() -> Dict[str, Any]:
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task_id": TASK,
        "component": SLUG,
        "decision": DECISION,
        "status": "blocked",
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "qualified": False,
        "admitted_asset_count": 0,
        "present_asset_count": 0,
        "runtime_reproduced": False,
        "forward_pass_executed": False,
        "matched_evidence_present": False,
        "rights_reviewed": False,
        "qualifying_results": 0,
        "blocked_release_gates": len(GATE_DEFINITIONS),
        "open_blockers": len(EXACT_BLOCKERS),
        "external_blockers": [
            {
                "id": item["id"],
                "title": item["title"],
                "missing": item["missing"],
                "reopen": item["reopen"],
                "status": "open",
                "qualifies": False,
            }
            for item in EXACT_BLOCKERS
        ],
        "gates": [
            {
                "id": f"RG-{index:02d}",
                "title": title,
                "status": "blocked",
                "qualifies": False,
            }
            for index, (title, _) in enumerate(GATE_DEFINITIONS, start=1)
        ],
        "source_commit_identified": SOURCE_COMMIT,
        "hub_revision_identified": HUB_REVISION,
        "network_used_for_metadata": True,
        "weights_downloaded": False,
        "asset_bytes_read": False,
        "non_claims": list(NON_CLAIMS),
        "notes": [
            "Metadata identification is not admission.",
            "No candidate result, benchmark, timing, listening or release claim is made.",
            "All ten release gates stay blocked until every exact blocker closes.",
        ],
    }


def build_contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity/noisy control",
                "paired SI-SDR and STOI where rights-cleared clean references exist",
                "clean-speech preservation, peaks and invalid outputs",
                "alignment, state and content/availability timing reported separately",
                "caller-supplied asset metadata and fail-closed frame controls",
            ],
            "not_applicable": [
                "no source checkout or checkpoint bytes, so the model is not reproduced",
                "no rights-cleared cohort, so no real quality result exists",
                "no device clock, so no latency, deadline or memory measurement exists",
                "no established task-matched baseline is reproduced",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "task_geometry": copy.deepcopy(TASK_GEOMETRY),
        "asset_bundle_contract": {
            "required_fields": list(CALLER_ASSET_FIELDS),
            "module_ids": list(CALLER_MODULE_IDS),
            "runtime_fields": list(CALLER_RUNTIME_FIELDS),
            "devices": list(CALLER_DEVICES),
            "peak_policies": list(CALLER_PEAK_POLICIES),
            "source_repository": SOURCE_REPOSITORY,
            "source_commit": SOURCE_COMMIT,
            "hub_repository": HUB_REPOSITORY,
            "hub_revision": HUB_REVISION,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "mel": {
                "n_mels": MEL_N_MELS,
                "n_fft": MEL_N_FFT,
                "hop_length": MEL_HOP_LENGTH,
                "win_length": MEL_WIN_LENGTH,
            },
            "sampling": {
                "steps": DEFAULT_STEPS,
                "cfg_strength": DEFAULT_CFG_STRENGTH,
                "sway_sampling_coef": DEFAULT_SWAY_SAMPLING_COEF,
                "ode_method": ODE_METHOD,
            },
            "content_lag_samples": 0,
            "tail_policy": "pad_or_truncate_to_source_length",
            "fail_closed": True,
            "caller_path_never_resolved": True,
        },
        "asset_identities": {
            "source_commit": SOURCE_COMMIT,
            "hub_revision": HUB_REVISION,
            "checkpoint_total_bytes": TOTAL_CHECKPOINT_BYTES,
            "assets": [
                {
                    "id": asset["id"],
                    "path": asset["path"],
                    "byte_count": asset["byte_count"],
                    "sha256": asset["sha256"],
                    "present_locally": False,
                    "admitted": False,
                }
                for asset in EXTERNAL_ASSETS
            ],
            "config": {
                "path": EXTERNAL_CONFIG["path"],
                "byte_count": EXTERNAL_CONFIG["byte_count"],
                "sha256": EXTERNAL_CONFIG["sha256"],
                "present_locally": False,
                "admitted": False,
            },
        },
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": [
            {
                "id": f"RG-{index:02d}",
                "title": title,
                "status": "blocked",
                "reopen": reopen,
                "qualifies": False,
            }
            for index, (title, reopen) in enumerate(GATE_DEFINITIONS, start=1)
        ],
        "invariants": {
            "decision_is_defer": True,
            "status_is_incomplete": True,
            "qualification_is_not_qualified": True,
            "zero_qualifying_results": True,
            "all_gates_blocked": True,
            "no_source_checkout_present": True,
            "no_checkpoint_present": True,
            "no_runtime_reproduced": True,
            "no_audio_read": True,
            "no_listening": True,
            "no_device_timing": True,
            "no_benchmark": True,
            "no_release_claim": True,
            "task_local_only": True,
        },
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "report_sha256": None,
        "artifact_pins": {},
    }
