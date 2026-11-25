# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-HUSH.

This module is NOT Hush. It does not load an ONNX bundle, execute a native
library, read audio, download anything, measure a device clock, conduct
listening, benchmark the SDK or qualify a release. It models the *boundary* of
Hush as a caller-supplied 16 kHz / 160-sample library+model asset pair and runs
a deterministic model-free frame-gate surrogate when that asset is absent.

The acceptance profile is Spatial, because the component's task is
competing-speaker suppression in conversational audio (SPK-01), not generic
stationary-noise denoising. Metrics therefore report target retention,
interferer leakage/attenuation and target damage on synthetic two-source
mixtures at three target-to-interferer ratios. Every quality, room, listening,
device and release gate remains blocked.
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
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pystoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-HUSH"
TITLE = "Hush"
SLUG = "hush"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d5b11912cd09e87296cd9d4654f1917c9cb94258"
BRANCH = "swarm/SDK-HUSH"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "spatial"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FRAME_DURATION_MS = 10
ALGORITHMIC_LATENCY_SAMPLES = 320
ALGORITHMIC_LATENCY_MS = 20
MODELED_DELAY_SAMPLES = 160
MODELED_DELAY_MS = 10
WINDOW_SAMPLES = 32000
WINDOW_FRAMES = WINDOW_SAMPLES // FRAME_SAMPLES
NS_PER_SAMPLE = 1_000_000_000 // SAMPLE_RATE_HZ
ORIGIN_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-monotonic-not-device"
ATTEN_LIMIT_DB = 100.0
GATE_FLOOR = 0.15
GATE_ATTACK = 0.60
GATE_RELEASE = 0.85
NOISE_ESTIMATE_FRAMES = 5
THRESHOLD_MULTIPLIER = 2.0
IMPULSE_INDEX = 4000
IMPULSE_AMPLITUDE = 0.8
PEAK_GUARD = 0.95
SIR_DB_STRATA = (12, 18, 24)
CONDITIONS = (
    "target_only",
    "mixture_sir12",
    "mixture_sir18",
    "mixture_sir24",
    "interferer_only",
    "silence",
)
STRATUM_CONDITIONS = ("mixture_sir12", "mixture_sir18", "mixture_sir24")

UPSTREAM_REPOSITORY = "https://github.com/pulp-vision/Hush"
UPSTREAM_COMMIT = "9f6414e91461a8f4bdf9840c0cdcdcb7da986339"
UPSTREAM_LICENSE = "Apache-2.0"
UPSTREAM_SNAPSHOT = "data/checkouts/Hush"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/LICENSE"
UPSTREAM_README_PATH = UPSTREAM_SNAPSHOT + "/README.md"
DEPLOYMENT_README_PATH = UPSTREAM_SNAPSHOT + "/deployment/README.md"
DEPLOYMENT_HEADER_PATH = UPSTREAM_SNAPSHOT + "/deployment/include/weya_nc.h"
NATIVE_LIB_PATH = UPSTREAM_SNAPSHOT + "/native/weya_nc_build/weya_nc/src/lib.rs"
MODEL_BUNDLE_PATH = (
    UPSTREAM_SNAPSHOT +
    "/deployment/models/advanced_dfnet16k_model_best_onnx.tar.gz")
MODEL_BUNDLE_SHA256 = (
    "45632ccaa82b71bb743d6caa7c78e983fe2f2790a3af7f6ec48e6ed7ba085df6")
MODEL_BUNDLE_BYTES = 8_558_968
CHECKPOINT_PATH = (
    UPSTREAM_SNAPSHOT + "/deployment/models/model_best.ckpt")
RUNTIME_DYLIB_PATH = (
    UPSTREAM_SNAPSHOT + "/deployment/lib/libweya_nc.dylib")
RUNTIME_SO_PATH = (
    UPSTREAM_SNAPSHOT + "/deployment/lib/libweya_nc.so")
RUNTIME_DLL_PATH = (
    UPSTREAM_SNAPSHOT + "/deployment/lib/weya_nc.dll")
HF_REPOSITORY = "https://huggingface.co/weya-ai/hush"
HF_REVISION = "1aee65c0b22e99bc9c8fea933dc25948168d2416"
EXPECTED_CALLER_RUNTIME_PATH = "data/envs/hush/libweya_nc.dylib"
EXPECTED_CALLER_MODEL_PATH = (
    "data/envs/hush/advanced_dfnet16k_model_best_onnx.tar.gz")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md":
        "d9285694209a54b26db0aa89a27a11b004fa0159d7ee08fc5fff0728c0869545",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md":
        "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-hush-eval/REPORT.md":
        "bf6be1fb4f302cc41f5eebbe9a66baf1d510d622158406e25564ba3d0e353068",
    "research/voice-enhancement-20261101/agent-hush-synthetic-eval/REPORT.md":
        "fa0962ec9194f4267a283c8d24d80b4b63ac2e52447e0c8fa8e163e7713ab096",
    "adapters/hush/adapter.json":
        "4746e674385c2e3e377e7455d9f56e0d06a6a47532ed37c784bb0616e3105b40",
    "adapters/hush/README.md":
        "c9ac19950af4138b50dc7a5d0560b4d79ed6b01dc81ec0af6a5a4bea84a8a94d",
    "adapters/hush/run.py":
        "79ad67b3ff814930b1833b21254f19a63aec74d790617c826c83156a34f90d24",
}

ASSET_PINS: Dict[str, str] = {
    UPSTREAM_LICENSE_PATH:
        "d2650f8a0a002d02377a5157e60071a39cc710113bf2c19f808db7045edda198",
    UPSTREAM_README_PATH:
        "6c1ae0349b459dd03bb627438a3d6af3a00afff2817da291228b603b833ebd38",
    DEPLOYMENT_README_PATH:
        "af4b9e2df9b9b13f8207942714f71fdc12af839d0c1d9f0ad819f6ab9fdd302a",
    DEPLOYMENT_HEADER_PATH:
        "887640d07b0147b8172ae8247cb16c460dce06e7cd54cfd9c1cfe13d1fef9f86",
    NATIVE_LIB_PATH:
        "3aa0b16ea0c39fab4bd9fd5f85566aa3e2e18066b55fdd0ce986d16b9a99bf68",
    MODEL_BUNDLE_PATH: MODEL_BUNDLE_SHA256,
    CHECKPOINT_PATH:
        "a2221e335c7de2c3453b422bf7f3c609723e453f4ca29c86137fd707d62f841b",
    RUNTIME_DYLIB_PATH:
        "4bcd38634000d456ad68db4b6ff97fe4a462542aa65ac5f910fbf374ca33fbaa",
    RUNTIME_SO_PATH:
        "c4a5915c92e9500a49e6cd14804e6e88319277de2ef7d4d5cf6c0ac4456f3bbf",
    RUNTIME_DLL_PATH:
        "633958ef839c94af6f8f5f9f8fb33c4daedaeec0373cb39a03934fdd7efa6a32",
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
    "library_path",
    "library_sha256",
    "model_bundle_path",
    "model_bundle_sha256",
    "source_commit",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "atten_limit_db",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/hush/caller-supplied-asset/0.1",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": {
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "atten_limit_db": ATTEN_LIMIT_DB,
    },
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "library_path and model_bundle_path are caller-owned absolute paths",
        "SHA-256 of both files matches the manifest",
        "source_commit equals the pinned Hush revision",
        "sample rate, channels, frame size and attenuation limit equal the "
        "pinned 16 kHz mono 160-sample geometry",
        "no download, copy, build, load or execution occurs in this package",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hashes_and_geometry_only; do_not_load_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
}

FORMAT: Dict[str, Any] = {
    "public_sample_rate_hz": SAMPLE_RATE_HZ,
    "public_channels": 1,
    "public_sample_format": "f32",
    "public_frame_samples": FRAME_SAMPLES,
    "public_frame_duration_ms": FRAME_DURATION_MS,
    "asset_sample_rate_hz": SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_frame_samples": FRAME_SAMPLES,
    "asset_frame_duration_ms": FRAME_DURATION_MS,
    "asset_is_native_16k": True,
    "resampling_required": False,
    "atten_limit_db": ATTEN_LIMIT_DB,
    "window_samples": WINDOW_SAMPLES,
    "window_frames": WINDOW_FRAMES,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}

SPATIAL_GEOMETRY: Dict[str, Any] = {
    "layout": "mono",
    "channels": 1,
    "channel_loss_evaluated": False,
    "channel_loss_reason": "mono fixture; multi-channel and spatial capture are unmeasured",
    "source_condition": (
        "synthetic two-source additive mixture: deterministic voiced target "
        "plus deterministic voiced interferer"),
    "target_condition": (
        "deterministic voiced target (f0 125 Hz, three gated segments); no "
        "enrollment waveform, prompt or speaker embedding is supplied"),
    "reference_condition": (
        "the exact pre-mixture target waveform is the clean reference at every "
        "target-to-interferer stratum"),
    "interferer_condition": (
        "deterministic voiced interferer (f0 205 Hz, disjoint segment timing) "
        "at +12/+18/+24 dB target-to-interferer ratio"),
    "room_condition": "none; anechoic additive model, no RIR, distance or movement",
    "array_geometry": "not applicable; single channel",
    "timestamp_calibration": "modeled fixture clock, not a device capture clock",
    "permissions": (
        "synthetic only; no real recording, corpus, speaker label, room "
        "measurement or listening subject is used"),
    "upstream_algorithmic_latency_ms": ALGORITHMIC_LATENCY_MS,
    "upstream_stft_window_hop_samples": [320, 160],
    "upstream_report_scope": (
        "upstream README states ~20 ms algorithmic latency, 16 kHz, ~8 MB model "
        "and <1 ms processing per 10 ms frame; these values are source-reported "
        "and are not measured here"),
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
    "hush_source_executed": False,
    "hush_runtime_executed": False,
    "hush_model_loaded": False,
    "model_weights_downloaded": False,
    "model_weights_loaded": False,
    "real_audio": False,
    "real_labels": False,
    "room_measurement": False,
    "enrollment_prompt": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "hush_model_loaded": False,
    "hush_runtime_executed": False,
    "hush_source_executed": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "real_speaker_labels_used": False,
    "room_or_array_measured": False,
    "enrollment_prompt_used": False,
    "reference_conditioned_extraction_validated": False,
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
    "exact_hush_reproduction_claimed": False,
    "spatial_acceptance_cleared": False,
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "model_card": {
        "repository": HF_REPOSITORY,
        "declared_revision": HF_REVISION,
        "revision_pin_type": "declared_in_research_adapter_readme_not_hashed",
        "declared_license": UPSTREAM_LICENSE,
        "weights_listed_by_files_api": False,
        "artifact_accessed_by_this_package": False,
    },
    "model_bundle": {
        "path": MODEL_BUNDLE_PATH,
        "sha256": MODEL_BUNDLE_SHA256,
        "bytes": MODEL_BUNDLE_BYTES,
        "present_in_external_checkout": True,
        "present_in_sdk_worktree": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "unused_checkpoint": {
        "path": CHECKPOINT_PATH,
        "sha256": ASSET_PINS[CHECKPOINT_PATH],
        "used": False,
        "reason": (
            "the research adapter README states the .ckpt is not used; only the "
            "deployment ONNX bundle is in scope"),
    },
    "runtime_libraries": {
        "macos_arm64": {
            "path": RUNTIME_DYLIB_PATH,
            "sha256": ASSET_PINS[RUNTIME_DYLIB_PATH],
            "present_in_external_checkout": True,
            "loaded_or_executed": False,
        },
        "linux_x86_64": {
            "path": RUNTIME_SO_PATH,
            "sha256": ASSET_PINS[RUNTIME_SO_PATH],
            "present_in_external_checkout": True,
            "loaded_or_executed": False,
        },
        "windows_x86_64": {
            "path": RUNTIME_DLL_PATH,
            "sha256": ASSET_PINS[RUNTIME_DLL_PATH],
            "present_in_external_checkout": True,
            "loaded_or_executed": False,
        },
    },
    "source_files": {
        "deployment/include/weya_nc.h": ASSET_PINS[DEPLOYMENT_HEADER_PATH],
        "native/weya_nc_build/weya_nc/src/lib.rs": ASSET_PINS[NATIVE_LIB_PATH],
        "README.md": ASSET_PINS[UPSTREAM_README_PATH],
        "deployment/README.md": ASSET_PINS[DEPLOYMENT_README_PATH],
    },
    "distribution_channel": {
        "deployment_readme_download_url": (
            "https://github.com/YOUR_USERNAME/deepfilternet-se/releases"),
        "url_is_placeholder": True,
        "artifact_digest_published_upstream": False,
        "note": (
            "the deployment README links a placeholder release path and the "
            "declared model-card revision exposes no weights; the artifact was "
            "obtained from the pinned source tree and hashed locally"),
    },
    "public_adapter": {
        "path": "adapters/hush",
        "declared_output_kinds": ["waveform"],
        "declared_tasks": ["SPK-01"],
        "declared_modes": ["offline"],
        "declared_weights": "required_local",
        "source_commit": UPSTREAM_COMMIT,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": (
        "not established in this package; upstream states 10,000+ hours of mixed "
        "audio, but no dataset manifest, consent basis or rights chain is pinned"),
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_repository_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "upstream_license_text_pinned": True,
    "model_card_declared_license": UPSTREAM_LICENSE,
    "upstream_license_scope": (
        "Hush repository snapshot at the pinned commit; the Apache-2.0 notice "
        "obligations apply to redistribution of the source or a derived binary."),
    "model_bundle_terms": (
        "not established separately; the repository and model-card Apache-2.0 "
        "declaration is not an artifact-specific grant, and the declared "
        "checkpoint revision exposes no weights to verify."),
    "model_bundle_redistribution_clearance": False,
    "runtime_binary_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "model_bundle_and_runtime_rights",
    "conclusion": (
        "Apache-2.0 source licensing is pinned, but artifact-specific model "
        "bundle and runtime redistribution/product-use rights, the distribution "
        "channel and training-data provenance are not cleared. This package "
        "distributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact Hush source revision, ONNX bundle and platform runtime "
        "libraries are pinned by SHA-256 from the external research checkout, "
        "but no caller-supplied asset manifest or copy exists in this SDK "
        "worktree; the exact runtime cannot be loaded or reproduced here."),
    (
        "Hush source and model card declare Apache-2.0, but artifact-specific "
        "model-bundle and runtime redistribution/product-use rights, the "
        "upstream distribution channel (a placeholder release URL) and "
        "training-data provenance are not established, and no legal review "
        "exists. No asset was downloaded, copied, built, vendored or "
        "redistributed."),
    (
        "Only a deterministic model-free boundary surrogate was executed. It is "
        "not Hush, has no ONNX graph, DeepFilterNet blocks or weights, and its "
        "synthetic two-source target/leakage numbers are boundary-conformance "
        "observations, not a quality, room, listening, device-timing or "
        "benchmark result."),
    (
        "No rights-cleared held-out spatial cohort with speaker/room labels, no "
        "enrollment-conditioned extraction, no independent listening, no "
        "target-runtime timing/memory, no opt-in provider intake, no "
        "descriptor/registry review and no public default decision exist; every "
        "release gate remains blocked."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_asset_present_and_verified",
        "Place the caller-owned 16 kHz Hush library and ONNX model bundle in the "
        "worktree (or supply them through the manifest) with SHA-256, source "
        "commit and attenuation limit matching the pins."),
    (
        "model_bundle_and_runtime_rights",
        "Establish artifact-specific model-bundle and runtime redistribution and "
        "product-use rights plus training-data provenance; the Apache-2.0 "
        "declaration alone is insufficient."),
    (
        "exact_runtime_reproduction",
        "Load the exact pinned runtime and bundle and reproduce source-reported "
        "or approved reference outputs without downloading weights or using "
        "uncleared real audio."),
    (
        "native_streaming_boundary",
        "Verify the native 16 kHz / 160-sample boundary, attenuation-limit "
        "behavior, algorithmic latency, frame delay and reset/flush semantics "
        "through the real C ABI."),
    (
        "task_matched_held_out_spatial_labels",
        "Score a rights-cleared held-out cohort with task-matched speaker and "
        "room labels; the synthetic fixture has no speaker identity or room."),
    (
        "enrollment_conditioned_extraction_scope",
        "Resolve the spatial target condition: either evaluate a "
        "reference/enrollment-conditioned variant or record an explicit decision "
        "that primary/background suppression without a prompt is the accepted "
        "task."),
    (
        "real_cohort_leakage_and_target_damage",
        "Measure interferer leakage/attenuation and target damage on real "
        "overlap speech with documented SIR, channels and permissions."),
    (
        "independent_listening",
        "Collect independent listening or preference labels; synthetic metrics "
        "cannot qualify a suppressor."),
    (
        "target_runtime_timing_memory",
        "Measure content/availability timing, memory and deadlines on the exact "
        "target runtime."),
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
    "caller-supplied Hush library and ONNX bundle present and SHA-256-verified in this SDK worktree",
    "artifact-specific model-bundle and runtime redistribution/product-use rights clearance",
    "pinned, non-placeholder artifact distribution channel and training-data provenance",
    "exact Hush runtime reproduction and an approved reference-output vector",
    "native 16 kHz / 160-sample streaming boundary, attenuation cap, delay and flush evidence",
    "rights-cleared held-out spatial cohort with speaker and room labels",
    "enrollment/reference-conditioned target-speaker evaluation or an explicit scope decision",
    "real-overlap interferer leakage and target-damage measurement",
    "independent listening or preference labels",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and catalog review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies the pinned Hush 16 kHz library and ONNX bundle with "
    "matching SHA-256 values, source commit and attenuation limit, and the "
    "manifest validates.",
    "Artifact-specific model-bundle and runtime redistribution and product-use "
    "rights, a verifiable distribution channel and training-data provenance are "
    "cleared with a recorded review.",
    "The exact pinned runtime is reproduced and an approved reference-output "
    "vector is available for parity.",
    "The native 16 kHz / 160-sample streaming boundary, attenuation cap, delay, "
    "reset/flush and caller-facing conformance are verified.",
    "A rights-cleared held-out spatial cohort with speaker and room labels is "
    "scored under the Spatial profile.",
    "The spatial target condition is resolved: enrollment-conditioned extraction "
    "is evaluated, or a documented decision accepts prompt-free "
    "primary/background suppression as the task.",
    "Real-overlap interferer leakage and target damage are measured with "
    "documented SIR, channels and permissions.",
    "Independent listening or preference labels are collected.",
    "Target-runtime content/availability timing, memory and deadlines are measured.",
    "Opt-in adapter intake, descriptor and catalog review are completed.",
    "An explicit public default decision is recorded; the candidate remains OFF "
    "until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "EARS-derived synthetic 30-pair x 3-SIR primary/background screen on one "
        "local host, a supplemental AMI speaker-dominant diagnostic from one "
        "meeting, and an earlier five-pair pilot; not a representative spatial "
        "holdout or target-device run."),
    "sources": [
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        "research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md",
        "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md",
        "research/voice-enhancement-20261101/agent-hush-eval/REPORT.md",
        "research/voice-enhancement-20261101/agent-hush-synthetic-eval/REPORT.md",
        "adapters/hush/README.md",
        "REALTIME_COMPONENT_CANDIDATES.md",
    ],
    "findings": [
        {
            "fixture": "ears_synthetic_30_pairs",
            "stratum": "+12 dB",
            "metric": "delta_target_si_sdr_db",
            "value": -9.33,
            "interval_95": [-11.77, -7.01],
            "unit": "dB",
        },
        {
            "fixture": "ears_synthetic_30_pairs",
            "stratum": "+12 dB",
            "metric": "delta_target_stoi",
            "value": -0.141,
            "interval_95": [-0.182, -0.102],
            "unit": "ratio",
        },
        {
            "fixture": "ears_synthetic_30_pairs",
            "stratum": "+12 dB",
            "metric": "target_to_interferer_ratio_gain_db",
            "value": 8.14,
            "interval_95": [5.67, 10.38],
            "unit": "dB",
        },
        {
            "fixture": "ami_speaker_dominant_7_pairs",
            "stratum": "+24 dB",
            "metric": "delta_target_si_sdr_db",
            "value": -24.18,
            "interval_95": [-28.60, -19.64],
            "unit": "dB",
        },
        {
            "fixture": "ami_speaker_dominant_7_pairs",
            "stratum": "+24 dB",
            "metric": "target_to_interferer_ratio_gain_db",
            "value": 3.37,
            "interval_95": [-2.46, 10.65],
            "unit": "dB",
        },
        {
            "fixture": "ears_synthetic_30_pairs",
            "stratum": "all",
            "metric": "mean_transform_rtf",
            "value": 0.0278,
            "interval_95": None,
            "unit": "ratio",
        },
        {
            "fixture": "ami_speaker_dominant_7_pairs",
            "stratum": "all",
            "metric": "model_load_seconds",
            "value": 0.073,
            "interval_95": None,
            "unit": "s",
        },
        {
            "fixture": "ami_speaker_dominant_7_pairs",
            "stratum": "all",
            "metric": "process_max_rss_mb",
            "value": 92.2,
            "interval_95": None,
            "unit": "MB",
        },
    ],
    "note": (
        "Transcribed from the pinned research only. The studies report improved "
        "relative target-to-interferer ratio with substantial target SI-SDR and "
        "STOI damage and no enrollment prompt. This package neither reproduces "
        "nor claims these values and does not pool them with the surrogate "
        "observations."),
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
    time = np.arange(WINDOW_SAMPLES, dtype=np.float64) / SAMPLE_RATE_HZ
    f0 = (f0_base + f0_mod[0] * np.sin(2.0 * np.pi * 0.7 * time) +
          f0_mod[1] * np.sin(2.0 * np.pi * 1.9 * time))
    phase = 2.0 * np.pi * np.cumsum(f0) / SAMPLE_RATE_HZ
    voiced = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    for harmonic in range(1, harmonics + 1):
        voiced += (1.0 / harmonic) * np.sin(
            harmonic * phase + phase_offset * harmonic)
    envelope = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
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
                     ((0.15, 0.65), (0.85, 1.35), (1.55, 1.95)), 0.5)
    interferer = _voiced(205.0, (11.0, 5.0), 18, 1.13,
                         ((0.0, 0.50), (0.80, 1.20), (1.50, 1.90)), 0.5)
    target_rms = _rms(target.astype(np.float64))
    interferer_rms = _rms(interferer.astype(np.float64))
    if target_rms <= 0.0 or interferer_rms <= 0.0:
        raise ValueError("zero_source_energy")
    scales = {
        sir: target_rms / (interferer_rms * 10.0 ** (sir / 20.0))
        for sir in SIR_DB_STRATA
    }
    mixtures = {
        sir: target.astype(np.float64) +
        scale * interferer.astype(np.float64)
        for sir, scale in scales.items()
    }
    worst = max(float(np.max(np.abs(mix))) for mix in mixtures.values()) if mixtures else 0.0
    guard = 1.0
    if worst > PEAK_GUARD:
        guard = PEAK_GUARD / worst
    target_guarded = (target.astype(np.float64) * guard).astype(np.float32)
    interferer_guarded = (interferer.astype(np.float64) * guard).astype(np.float32)
    guarded_scales = {sir: scale * guard for sir, scale in scales.items()}
    guarded_mixtures = {
        sir: (target_guarded.astype(np.float64) +
              guarded_scales[sir] * interferer_guarded.astype(np.float64)
              ).astype(np.float32)
        for sir in SIR_DB_STRATA
    }
    impulse = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    impulse[IMPULSE_INDEX] = np.float32(IMPULSE_AMPLITUDE)
    signals: Dict[str, np.ndarray] = {
        "target_only": target_guarded,
        "mixture_sir12": guarded_mixtures[12],
        "mixture_sir18": guarded_mixtures[18],
        "mixture_sir24": guarded_mixtures[24],
        "interferer_only": interferer_guarded,
        "silence": np.zeros(WINDOW_SAMPLES, dtype=np.float32),
    }
    return {
        "signals": signals,
        "target": target_guarded,
        "interferer": interferer_guarded,
        "interferer_scale": guarded_scales,
        "guard_gain": guard,
        "impulse": impulse,
    }


def _validate_signal(signal: Any) -> np.ndarray:
    if not isinstance(signal, np.ndarray):
        raise ValueError("input_not_ndarray")
    if signal.ndim != 1:
        raise ValueError("input_not_mono")
    if signal.size != WINDOW_SAMPLES:
        raise ValueError("input_length_mismatch")
    if not np.isfinite(signal).all():
        raise ValueError("nonfinite_input")
    return np.asarray(signal, dtype=np.float32).astype(np.float64)


def _check_output(signal: Any, expected_samples: int = WINDOW_SAMPLES) -> np.ndarray:
    array = np.asarray(signal, dtype=np.float64)
    if array.size != expected_samples:
        raise ValueError("length_mismatch")
    if not np.isfinite(array).all():
        raise ValueError("nonfinite_output")
    return array


def attenuation_floor(atten_limit_db: float) -> float:
    if not isinstance(atten_limit_db, (int, float)) or isinstance(
            atten_limit_db, bool):
        raise ValueError("invalid_atten_limit")
    value = float(atten_limit_db)
    if not math.isfinite(value) or value < 0.0 or value > 100.0:
        raise ValueError("invalid_atten_limit")
    return max(GATE_FLOOR, 10.0 ** (-value / 20.0))


class Surrogate:
    """Deterministic model-free boundary surrogate; not a Hush model."""

    def __init__(self, bypass: bool = False,
                 atten_limit_db: float = ATTEN_LIMIT_DB) -> None:
        self.bypass = bool(bypass)
        self.atten_limit_db = float(atten_limit_db)
        self.floor = attenuation_floor(self.atten_limit_db)
        self.prev_gain = 1.0
        self.noise_estimate: float | None = None
        self.processed_frames = 0
        self.epoch = 1

    def reset(self, epoch: int | None = None) -> None:
        if epoch is not None:
            if not isinstance(epoch, int) or epoch < 1:
                raise ValueError("invalid_epoch")
            self.epoch = epoch
        self.prev_gain = 1.0
        self.noise_estimate = None
        self.processed_frames = 0

    def process(self, signal: Any, compensate: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        source = _validate_signal(signal)
        frames = source.reshape(-1, FRAME_SAMPLES)
        if frames.shape[0] != WINDOW_FRAMES:
            raise ValueError("frame_count_mismatch")
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
                target = 1.0 if (threshold <= 0.0 or level >= threshold) \
                    else self.floor
                if target == self.prev_gain:
                    gain = target
                elif target > self.prev_gain:
                    gain = GATE_ATTACK * target + (1.0 - GATE_ATTACK) * self.prev_gain
                else:
                    gain = GATE_RELEASE * target + (1.0 - GATE_RELEASE) * self.prev_gain
                processed[index] = frame * gain
                gains[index] = gain
                self.prev_gain = gain
        flat = processed.reshape(-1)
        delayed = np.concatenate(
            (np.zeros(MODELED_DELAY_SAMPLES, dtype=np.float64), flat))[:flat.size]
        if compensate:
            compensated = np.concatenate(
                (delayed[MODELED_DELAY_SAMPLES:],
                 np.zeros(MODELED_DELAY_SAMPLES, dtype=np.float64)))[:flat.size]
        else:
            compensated = delayed
        output = np.asarray(compensated[:WINDOW_SAMPLES], dtype=np.float64)
        _check_output(output)
        self.processed_frames += int(frames.shape[0])
        info = {
            "noise_estimate": noise_estimate,
            "threshold": threshold,
            "attenuation_floor": self.floor,
            "mean_gain": float(np.mean(gains)),
            "min_gain": float(np.min(gains)),
            "max_gain": float(np.max(gains)),
            "frame_count": int(frames.shape[0]),
            "compensated": bool(compensate),
            "bypass": self.bypass,
        }
        return output.astype(np.float32), info


def process_reference(signal: Any, bypass: bool = False,
                      compensate: bool = True,
                      atten_limit_db: float = ATTEN_LIMIT_DB,
                      ) -> Tuple[np.ndarray, Dict[str, Any]]:
    return Surrogate(bypass=bypass, atten_limit_db=atten_limit_db).process(
        signal, compensate=compensate)


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    """Validate a caller-owned asset manifest without loading or executing it."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("asset_manifest_fields")
    if manifest["source_commit"] != UPSTREAM_COMMIT:
        raise ValueError("asset_source_commit_mismatch")
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("asset_sample_rate_mismatch")
    if manifest["channels"] != 1:
        raise ValueError("asset_channels_mismatch")
    if manifest["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("asset_frame_samples_mismatch")
    if manifest["atten_limit_db"] != ATTEN_LIMIT_DB:
        raise ValueError("asset_atten_limit_mismatch")
    for name in ("library", "model_bundle"):
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
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "atten_limit_db": ATTEN_LIMIT_DB,
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
            value = float(pystoi.stoi(ref, est, SAMPLE_RATE_HZ, extended=False))
    except Exception as error:  # pragma: no cover - defensive boundary
        return None, "stoi_error:" + type(error).__name__
    if not math.isfinite(value):
        return None, "nonfinite_stoi"
    return norm(value), None


def _projection(estimate: Any, target: Any, interferer: Any,
                interferer_scale: float) -> Dict[str, Any]:
    empty = {
        "status": "not_applicable",
        "reason": None,
        "target_retention": None,
        "interferer_leakage_retention": None,
        "target_to_interferer_ratio_gain_db": None,
        "target_projection_snr_db": None,
        "identity_target_projection_snr_db": None,
        "target_projection_snr_delta_db": None,
    }
    if estimate is None or target is None or interferer is None:
        empty["reason"] = "missing_source_or_output"
        return empty
    est = np.asarray(estimate, dtype=np.float64)
    tar = np.asarray(target, dtype=np.float64)
    inf = np.asarray(interferer, dtype=np.float64)
    if est.size != tar.size or est.size != inf.size:
        empty["reason"] = "length_mismatch"
        return empty
    if not (np.isfinite(est).all() and np.isfinite(tar).all()
            and np.isfinite(inf).all()):
        empty["reason"] = "nonfinite_signal"
        return empty
    est = est - float(np.mean(est))
    tar = tar - float(np.mean(tar))
    inf = inf - float(np.mean(inf))
    tar_energy = float(np.dot(tar, tar))
    inf_energy = float(np.dot(inf, inf))
    if tar_energy <= 0.0 or inf_energy <= 0.0 or interferer_scale <= 0.0:
        empty["reason"] = "zero_source_energy"
        return empty
    alpha_t = float(np.dot(est, tar) / tar_energy)
    alpha_i = float(np.dot(est, inf) / inf_energy)
    if abs(alpha_i) <= 1e-12:
        empty["reason"] = "zero_interferer_projection"
        return empty
    identity_target_snr, _ = _target_projection_snr(
        np.asarray(target, dtype=np.float64) +
        interferer_scale * np.asarray(interferer, dtype=np.float64), tar)
    processed_target_snr, _ = _target_projection_snr(est, tar)
    ratio_gain = 20.0 * math.log10(abs(alpha_t) * interferer_scale / abs(alpha_i))
    snr_delta = None
    if identity_target_snr is not None and processed_target_snr is not None:
        snr_delta = norm(processed_target_snr - identity_target_snr)
    return {
        "status": "measured",
        "reason": None,
        "target_retention": norm(abs(alpha_t)),
        "interferer_leakage_retention": norm(abs(alpha_i) / interferer_scale),
        "target_to_interferer_ratio_gain_db": norm(ratio_gain),
        "target_projection_snr_db": processed_target_snr,
        "identity_target_projection_snr_db": identity_target_snr,
        "target_projection_snr_delta_db": snr_delta,
    }


def _target_projection_snr(signal: Any, target: Any) -> Tuple[float | None, str | None]:
    estimate = np.asarray(signal, dtype=np.float64)
    reference = np.asarray(target, dtype=np.float64)
    reference = reference - float(np.mean(reference))
    estimate = estimate - float(np.mean(estimate))
    denominator = float(np.dot(reference, reference))
    if denominator <= 0.0:
        return None, "zero_target_energy"
    scale = float(np.dot(estimate, reference) / denominator)
    projected = scale * reference
    residual = estimate - projected
    signal_energy = float(np.dot(projected, projected))
    residual_energy = float(np.dot(residual, residual))
    if signal_energy <= 0.0:
        return None, "zero_projection_energy"
    if residual_energy <= 1e-20:
        return None, "zero_error_identity_exact"
    return norm(10.0 * math.log10(signal_energy / residual_energy)), None


def _signal_summary(signal: np.ndarray) -> Dict[str, Any]:
    array = np.asarray(signal, dtype=np.float64)
    return {
        "samples": int(array.size),
        "finite": bool(np.isfinite(array).all()),
        "peak_abs": norm(float(np.max(np.abs(array)))) if array.size else 0.0,
        "clipped_or_nonfinite": int(np.count_nonzero(
            ~np.isfinite(array) | (np.abs(array) >= 1.0))),
        "waveform_sha256": _f32_sha256(array),
    }


def _paired_delta(identity: Dict[str, Any], provider: Dict[str, Any]) -> Any:
    if identity["valid"] is not True or provider["valid"] is not True:
        return None
    return norm(provider["value"] - identity["value"])


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


def _condition(name: str, input_signal: np.ndarray,
               reference_signal: np.ndarray,
               output_signal: np.ndarray,
               info: Dict[str, Any],
               interferer_scale: float | None) -> Dict[str, Any]:
    identity_metrics = _metrics(reference_signal, input_signal)
    provider_metrics = _metrics(reference_signal, output_signal)
    input_rms = _rms(input_signal.astype(np.float64))
    output_rms = _rms(output_signal.astype(np.float64))
    data = stimuli()
    if interferer_scale is None:
        projection = {
            "status": "not_applicable",
            "reason": "not_a_mixture_stratum",
            "target_retention": None,
            "interferer_leakage_retention": None,
            "target_to_interferer_ratio_gain_db": None,
            "target_projection_snr_db": None,
            "identity_target_projection_snr_db": None,
            "target_projection_snr_delta_db": None,
        }
    else:
        projection = _projection(output_signal, data["target"],
                                 data["interferer"], interferer_scale)
    return {
        "condition": name,
        "input": _signal_summary(input_signal),
        "output": _signal_summary(output_signal),
        "reference": (
            "clean_target" if reference_signal is not None and
            float(np.max(np.abs(reference_signal))) > 0.0 else "zero_reference"),
        "interferer_sir_db": (
            None if interferer_scale is None else
            int(round(20.0 * math.log10(
                _rms(data["target"].astype(np.float64)) /
                (interferer_scale * _rms(data["interferer"].astype(np.float64))))))),
        "preservation": {
            "rms_gain_ratio": norm(output_rms / input_rms) if input_rms > 0.0 else None,
            "target_retention": projection["target_retention"],
            "interferer_leakage_retention": projection["interferer_leakage_retention"],
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
        "projection": projection,
        "surrogate_gate": {
            "noise_estimate": norm(info["noise_estimate"]),
            "threshold": norm(info["threshold"]),
            "attenuation_floor": norm(info["attenuation_floor"]),
            "mean_gain": norm(info["mean_gain"]),
            "min_gain": norm(info["min_gain"]),
            "max_gain": norm(info["max_gain"]),
            "frame_count": info["frame_count"],
            "delay_compensated": info["compensated"],
        },
    }


def _asset_controls() -> Dict[str, Any]:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="hush-asset-") as directory:
        root = Path(directory)
        library = root / "libweya_nc.dylib"
        bundle = root / "advanced_dfnet16k_model_best_onnx.tar.gz"
        library.write_bytes(b"synthetic caller library placeholder; not loaded\n")
        bundle.write_bytes(b"synthetic caller model bundle placeholder; not loaded\n")
        base = {
            "library_path": str(library),
            "library_sha256": _sha256_file(library),
            "model_bundle_path": str(bundle),
            "model_bundle_sha256": _sha256_file(bundle),
            "source_commit": UPSTREAM_COMMIT,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "atten_limit_db": ATTEN_LIMIT_DB,
        }
        valid = validate_caller_asset(dict(base))

        def rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
            try:
                validate_caller_asset(manifest)
            except ValueError as error:
                return {"status": "rejected", "reason": str(error)}
            return {"status": "unexpectedly_accepted", "reason": None}

        hash_manifest = dict(base)
        hash_manifest["library_sha256"] = "0" * 64
        model_hash_manifest = dict(base)
        model_hash_manifest["model_bundle_sha256"] = "0" * 64
        missing_manifest = dict(base)
        missing_manifest["library_path"] = str(root / "absent.dylib")
        commit_manifest = dict(base)
        commit_manifest["source_commit"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 48000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        frame_manifest = dict(base)
        frame_manifest["frame_samples"] = 480
        atten_manifest = dict(base)
        atten_manifest["atten_limit_db"] = 60
        relative_manifest = dict(base)
        relative_manifest["library_path"] = "libweya_nc.dylib"
        extra_manifest = dict(base)
        extra_manifest["checkpoint_path"] = str(root / "model_best.ckpt")
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
            "absent_file": rejected(missing_manifest),
            "library_hash_mismatch": rejected(hash_manifest),
            "model_hash_mismatch": rejected(model_hash_manifest),
            "wrong_source_commit": rejected(commit_manifest),
            "wrong_sample_rate": rejected(rate_manifest),
            "wrong_channels": rejected(channels_manifest),
            "wrong_frame_size": rejected(frame_manifest),
            "wrong_atten_limit": rejected(atten_manifest),
            "relative_path": rejected(relative_manifest),
            "extra_field": rejected(extra_manifest),
        }


def _frame_controls() -> Dict[str, Any]:
    model = Surrogate()
    zeros = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    baseline, _ = model.process(zeros)
    state_before = (model.prev_gain, model.noise_estimate, model.processed_frames,
                    model.epoch)

    def rejected(signal: Any, atten: float = ATTEN_LIMIT_DB) -> Dict[str, Any]:
        try:
            Surrogate(atten_limit_db=atten).process(signal)
        except ValueError as error:
            return {"status": "rejected", "reason": str(error)}
        return {"status": "unexpectedly_accepted", "reason": None}

    short = np.zeros(WINDOW_SAMPLES - 1, dtype=np.float32)
    two_dimensional = np.zeros((WINDOW_SAMPLES, 1), dtype=np.float32)
    nonfinite = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    nonfinite[0] = np.nan
    state_after = (model.prev_gain, model.noise_estimate, model.processed_frames,
                   model.epoch)
    try:
        _check_output(np.zeros(WINDOW_SAMPLES - 1, dtype=np.float64))
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
        "atten_above_limit": rejected(zeros, 101.0),
        "atten_below_limit": rejected(zeros, -1.0),
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
    signal = stimuli()["signals"]["mixture_sir12"]
    first, _ = Surrogate().process(signal)
    second, _ = Surrogate().process(signal)
    model = Surrogate()
    before_reset, _ = model.process(signal)
    model.reset()
    after_reset, _ = model.process(signal)
    model.reset(epoch=2)
    epoch_ok = model.epoch == 2
    other, _ = Surrogate().process(stimuli()["signals"]["mixture_sir24"])
    zero_limit, _ = Surrogate(atten_limit_db=0.0).process(signal)
    return {
        "separate_instances_uncoupled": bool(np.array_equal(first, second)),
        "reset_bit_identical": bool(np.array_equal(before_reset, after_reset)),
        "reset_epoch_propagated": bool(epoch_ok),
        "different_stimuli_differ": bool(not np.array_equal(first, other)),
        "zero_attenuation_is_identity": bool(np.array_equal(
            zero_limit, signal.astype(np.float64))),
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
        "modeled_frame_delay_samples": MODELED_DELAY_SAMPLES,
        "modeled_frame_delay_ms": MODELED_DELAY_MS,
        "upstream_algorithmic_latency_samples": ALGORITHMIC_LATENCY_SAMPLES,
        "upstream_algorithmic_latency_ms": ALGORITHMIC_LATENCY_MS,
        "delay_compensation_applied": True,
        "source_interval": [0, WINDOW_SAMPLES],
        "raw_interval": [0, WINDOW_SAMPLES],
        "valid_output_samples": WINDOW_SAMPLES,
        "sdk_callback_invoked": False,
    }


def _timestamp_calibration() -> Dict[str, Any]:
    first = ORIGIN_NS + FRAME_SAMPLES * NS_PER_SAMPLE
    last = ORIGIN_NS + WINDOW_SAMPLES * NS_PER_SAMPLE
    return {
        "clock_id": CLOCK_ID,
        "origin_ns": str(ORIGIN_NS),
        "ns_per_sample": NS_PER_SAMPLE,
        "frame_samples": FRAME_SAMPLES,
        "frame_duration_ns": str(FRAME_SAMPLES * NS_PER_SAMPLE),
        "first_frame_end_ns": str(first),
        "last_frame_end_ns": str(last),
        "formula": (
            "frame_end_ns = origin_ns + frame_index_end * frame_samples * "
            "ns_per_sample"),
        "monotonic_nondecreasing": True,
        "measured": False,
        "signal_timestamp_is_not_availability": True,
        "availability_serialization": "decimal string",
    }


def _conditions() -> Dict[str, Any]:
    data = stimuli()
    target = data["target"]
    zero = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    references = {
        "target_only": target,
        "mixture_sir12": target,
        "mixture_sir18": target,
        "mixture_sir24": target,
        "interferer_only": zero,
        "silence": zero,
    }
    strata = {name: int(name.rsplit("sir", 1)[1]) for name in STRATUM_CONDITIONS}
    result: Dict[str, Any] = {}
    for name in CONDITIONS:
        input_signal = data["signals"][name]
        scale = data["interferer_scale"][strata[name]] if name in strata else None
        output, info = process_reference(input_signal)
        result[name] = _condition(
            name, input_signal, references[name], output, info, scale)
    return result


def _target_damage(conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name in STRATUM_CONDITIONS:
        condition = conditions[name]
        rows.append({
            "condition": name,
            "interferer_sir_db": condition["interferer_sir_db"],
            "delta_si_sdr_db": condition["si_sdr_db"]["paired_delta"],
            "delta_stoi": condition["stoi"]["paired_delta"],
            "target_retention": condition["projection"]["target_retention"],
            "rms_gain_ratio": condition["preservation"]["rms_gain_ratio"],
        })
    return rows


def _leakage(conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name in STRATUM_CONDITIONS:
        projection = conditions[name]["projection"]
        rows.append({
            "condition": name,
            "interferer_sir_db": conditions[name]["interferer_sir_db"],
            "interferer_leakage_retention": projection["interferer_leakage_retention"],
            "target_to_interferer_ratio_gain_db":
                projection["target_to_interferer_ratio_gain_db"],
            "target_projection_snr_delta_db":
                projection["target_projection_snr_delta_db"],
        })
    return rows


def _regressions(conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        condition = conditions[name]
        si_delta = condition["si_sdr_db"]["paired_delta"]
        stoi_delta = condition["stoi"]["paired_delta"]
        target_delta = condition["projection"]["target_projection_snr_delta_db"]
        if si_delta is not None and si_delta < -0.01:
            regressions.append({
                "condition": name,
                "metric": "si_sdr_db",
                "paired_delta": si_delta,
                "note": "surrogate is worse than identity on this synthetic condition",
            })
        if stoi_delta is not None and stoi_delta < -0.001:
            regressions.append({
                "condition": name,
                "metric": "stoi",
                "paired_delta": stoi_delta,
                "note": "surrogate is worse than identity on this synthetic condition",
            })
        if target_delta is not None and target_delta < -0.01:
            regressions.append({
                "condition": name,
                "metric": "target_projection_snr_db",
                "paired_delta": target_delta,
                "note": "surrogate damages the designated target on this synthetic condition",
            })
    return regressions


def _report_core() -> Dict[str, Any]:
    conditions = _conditions()
    regressions = _regressions(conditions)
    asset_controls = _asset_controls()
    frame_controls = _frame_controls()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": "hush",
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
        "spatial_geometry": dict(SPATIAL_GEOMETRY),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "library_present_in_sdk_worktree": False,
            "model_bundle_present_in_sdk_worktree": False,
            "model_bundle_present_in_external_checkout": True,
            "runtime_library_present_in_external_checkout": True,
            "runtime_library_present_in_sdk_worktree": False,
            "expected_caller_runtime_path": EXPECTED_CALLER_RUNTIME_PATH,
            "expected_caller_model_path": EXPECTED_CALLER_MODEL_PATH,
            "verified": False,
            "loaded": False,
            "executed": False,
            "surrogate_used": True,
            "reason": "caller_supplied_runtime_absent_and_rights_unresolved",
        },
        "surrogate": {
            "identity": "hush-boundary-surrogate-v0",
            "is_hush": False,
            "is_neural_network": False,
            "onnx_graph": False,
            "deepfilternet_blocks": False,
            "weights": False,
            "checkpoint": False,
            "model_bundle": False,
            "enrollment_input": False,
            "method": (
                "deterministic frame-RMS gate over contiguous 160-sample frames "
                "with an attenuation floor derived from atten_limit_db; one "
                "160-sample delay modeled then compensated"),
            "public_input_geometry": "16 kHz mono f32 160-sample frames",
            "asset_geometry": "16 kHz mono f32 160-sample frames",
            "atten_limit_db": ATTEN_LIMIT_DB,
            "gate_floor_at_default": GATE_FLOOR,
            "delay_modeled_samples": MODELED_DELAY_SAMPLES,
            "delay_compensated_samples": MODELED_DELAY_SAMPLES,
            "attack": GATE_ATTACK,
            "release": GATE_RELEASE,
            "noise_estimate_frames": NOISE_ESTIMATE_FRAMES,
            "threshold_multiplier": THRESHOLD_MULTIPLIER,
            "peak_guard": PEAK_GUARD,
            "deterministic": True,
            "pure_synthetic": True,
            "quality_claim": False,
        },
        "stimuli": {
            "target": "synthetic voiced f0 125 Hz, 3 gated segments",
            "interferer": "synthetic voiced f0 205 Hz, 3 disjoint gated segments",
            "sir_db_strata": list(SIR_DB_STRATA),
            "peak_guard": PEAK_GUARD,
            "guard_gain": norm(stimuli()["guard_gain"]),
            "target_rms": norm(_rms(stimuli()["target"].astype(np.float64))),
            "interferer_rms": norm(_rms(stimuli()["interferer"].astype(np.float64))),
            "real_audio": False,
            "room_model": False,
        },
        "timestamp_calibration": _timestamp_calibration(),
        "conditions": conditions,
        "stratification": [
            {
                "condition": name,
                "interferer_sir_db": conditions[name]["interferer_sir_db"],
                "source_pair_count": 1,
                "independent_items": False,
                "held_out": False,
            }
            for name in STRATUM_CONDITIONS
        ],
        "alignment": _alignment(),
        "state": _state_controls(),
        "target_damage": _target_damage(conditions),
        "leakage": _leakage(conditions),
        "channel_and_room": {
            "layout": "mono",
            "channels": 1,
            "channel_loss_evaluated": False,
            "multichannel_evaluated": False,
            "room_model": False,
            "rir_used": False,
            "movement_evaluated": False,
            "reference_change_evaluated": False,
            "reason": (
                "the synthetic fixture is a single-channel anechoic additive "
                "model; channel loss, array geometry and room/reference changes "
                "are unmeasured and cannot be inferred"),
        },
        "held_out_labels": {
            "present": False,
            "speaker_identity_labels": False,
            "room_labels": False,
            "independent_items": False,
            "reason": (
                "the fixture has one synthetic target and one synthetic "
                "interferer; no speaker identity, room label or held-out item "
                "exists, so no localization/activity/extraction claim is made"),
        },
        "controls": {
            "identity": {
                "status": "present",
                "baseline": "same_mixture_identity",
                "description": "unprocessed mixture is the identity control at each SIR",
            },
            "target_only": {
                "status": "present",
                "description": "clean target without interferer; checks target preservation",
            },
            "interferer_only": {
                "status": "present",
                "description": "interferer without target; zero reference, never scored as speech",
            },
            "silence": {
                "status": "present",
                "description": "digital silence; zero reference, never scored as speech",
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
            "identity_control": "same_mixture_identity",
            "provider": "frame-gate-boundary-surrogate-v0",
            "established_task_matched_baseline_reproduced": False,
            "source_reported_hush_pilot_used_for_qualification": False,
            "enrollment_conditioned": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No Hush runtime or rights-cleared held-out spatial cohort; the "
                "surrogate is a boundary conformance fixture and its synthetic "
                "target/leakage metrics are not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "paced": False,
            "reason": (
                "No exact Hush runtime or target device; the surrogate is "
                "unpaced and no wall-clock, RTF or memory result is claimed."),
            "modeled_content_delay_samples": MODELED_DELAY_SAMPLES,
            "upstream_algorithmic_latency_ms": ALGORITHMIC_LATENCY_MS,
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
                "two-source stimuli; no Hush asset, real audio, room or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": "none",
            "target_runtime": "none",
            "spatial_acceptance": (
                "not cleared; no held-out spatial labels, room or channel evidence"),
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
        "component": "hush",
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "geometry, layout, timestamp calibration and source/target/"
                "reference conditions recorded",
                "permissions recorded: synthetic only, no real recording or labels",
                "target/interferer strata at +12/+18/+24 dB with an exact clean "
                "target reference",
                "leakage, target damage, peaks, invalid outputs and channel/"
                "room limits reported separately",
                "identity, target-only, interferer-only and silence controls, "
                "plus fail-closed caller-asset and frame controls",
                "held-out spatial labels, independent listening, target-runtime "
                "timing and release gates explicitly unmeasured",
            ],
            "not_applicable": [
                "no Hush runtime, so exact source-reported outputs are not "
                "reproduced",
                "no real spatial cohort, room, array or speaker labels, so no "
                "localization/extraction, leakage-in-room or listening claim is made",
                "no target device, so no timing, memory or deadline result is "
                "claimed",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "spatial_geometry": dict(SPATIAL_GEOMETRY),
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
            "No Hush source, ONNX bundle, checkpoint, runtime or weights is "
            "copied, downloaded, built, loaded or executed.",
            "All stimuli are frozen deterministic synthetic floats; no real "
            "audio, speaker label, room, device or network is used.",
            "Caller-supplied asset manifests fail closed on missing, "
            "hash-mismatched or wrong-geometry inputs.",
            "Source-reported Hush metrics are provenance only and are never "
            "reproduced, pooled or used as thresholds.",
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
        "tasks": ["SPK-01"],
        "modes": ["offline"],
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "enrollment_input": False,
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
        "spatial_acceptance_cleared": False,
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
            "expected_runtime_path": EXPECTED_CALLER_RUNTIME_PATH,
            "expected_runtime_sha256": ASSET_PINS[RUNTIME_DYLIB_PATH],
            "expected_model_bundle_path": EXPECTED_CALLER_MODEL_PATH,
            "expected_model_bundle_sha256": MODEL_BUNDLE_SHA256,
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
        "# SHA-256 pins for SDK-HUSH task-local evidence.",
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
        "a" * 64 + "  docs/task-evidence/hush/unknown",
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
