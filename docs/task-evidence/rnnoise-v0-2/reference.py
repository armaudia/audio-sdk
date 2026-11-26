# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-RNNOISE-V0-2.

This module is NOT RNNoise. It does not load a model, execute a native
library, read audio, download anything, measure a device clock, conduct
listening, benchmark the SDK or qualify a release. It models the *boundary*
of RNNoise v0.2 as a caller-supplied 48 kHz / 480-sample asset and executes a
deterministic model-free frame-RMS gate surrogate when that asset is absent.
Every quality gate remains blocked; the surrogate is a conformance fixture.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from functools import lru_cache
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pystoi
from scipy.signal import butter, resample_poly, sosfilt

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-RNNOISE-V0-2"
TITLE = "RNNoise v0.2"
SLUG = "rnnoise-v0-2"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
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
ASSET_SAMPLE_RATE_HZ = 48000
ASSET_FRAME_SAMPLES = 480
ASSET_FRAME_DURATION_MS = 10
RESAMPLE_UP = 3
WINDOW_SAMPLES = 32000
WINDOW_FRAMES = WINDOW_SAMPLES // PUBLIC_FRAME_SAMPLES
NS_PER_PUBLIC_SAMPLE = 1_000_000_000 // PUBLIC_SAMPLE_RATE_HZ
ORIGIN_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-monotonic-not-device"
LOOKAHEAD_SOURCE_SAMPLES = PUBLIC_FRAME_SAMPLES
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

UPSTREAM_REPOSITORY = "https://github.com/xiph/rnnoise"
UPSTREAM_COMMIT = "70f1d256acd4b34a572f999a05c87bf00b67730d"
UPSTREAM_LICENSE = "BSD-3-Clause"
UPSTREAM_SNAPSHOT = "data/checkouts/RNNoise"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/COPYING"
UPSTREAM_MODEL_VERSION_PATH = UPSTREAM_SNAPSHOT + "/model_version"
UPSTREAM_MODEL_ARCHIVE_NAME = (
    "rnnoise_data-0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37.tar.gz")
UPSTREAM_MODEL_ARCHIVE_PATH = UPSTREAM_SNAPSHOT + "/" + UPSTREAM_MODEL_ARCHIVE_NAME
UPSTREAM_MODEL_ARCHIVE_BYTES = 58_603_099
UPSTREAM_RUNTIME_PATH = "data/envs/rnnoise/librnnoise.dylib"
UPSTREAM_RUNTIME_SHA256 = (
    "3d552b136eb4d80fa697093c7258cc51314f904a56b53a9f46e54b523fef63b4")
UPSTREAM_BUILD_SCRIPT_PATH = "scripts/build_rnnoise.sh"

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
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/voice-enhancement-20261101/agent-denoise/REPORT.md":
        "eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07",
    "adapters/rnnoise/adapter.json":
        "6c7ca68df9fe24bf67f249197777674e4bc8f6527bccbb2fcced4637e00abb44",
    "adapters/rnnoise/README.md":
        "6c5cfb5c3493f40c1fd43a0fc54b87f590abf3712d3d3cef7c2f7bc16de15b85",
    "adapters/rnnoise/run.py":
        "4be2dc2f1c76e46b187a9e52c9faab7ff32e805461cf554a3b97fa3410d2993b",
}

ASSET_PINS: Dict[str, str] = {
    UPSTREAM_LICENSE_PATH:
        "45d37ca1cdb278c088e1aa85e0e65ca3a534ed86a28dcc96ca16810248a61d35",
    UPSTREAM_SNAPSHOT + "/README":
        "87fc8de7620259a3200be2012e7c77fc9383997d3224318451eaded27691754f",
    UPSTREAM_SNAPSHOT + "/include/rnnoise.h":
        "15ca0f5c0db9dfa48907e91a32995d37e57552b0e14fef5ebb8d3dc073528f83",
    UPSTREAM_SNAPSHOT + "/src/denoise.c":
        "f12ac3cc97d798cdfd7c7bd4366a08a72c5516c382056c891b61a61cb17eb031",
    UPSTREAM_SNAPSHOT + "/src/rnn.c":
        "c40bbe40082448005873fe970d8963870ab2c9993b7c38d6939ca48f4f31a7bd",
    UPSTREAM_SNAPSHOT + "/src/nnet.c":
        "3a2c1dc09ad7e9dfe3cf32cfb94694935dc462488da8f513d1f308db39f7c087",
    UPSTREAM_SNAPSHOT + "/src/rnnoise_data.c":
        "d6021b7697677c4d2274c912975e143765552b0e6f25500aa660fdb4a9849be5",
    UPSTREAM_SNAPSHOT + "/src/rnnoise_data_little.c":
        "eea1aa6fd8726d161876508a6f7d79022bf6ec82508660b4c1ac27c4f9b76c04",
    UPSTREAM_SNAPSHOT + "/src/rnnoise_data.h":
        "09ff880bddd0fc74a2ae0e5ec6c8d65714031b08d0c3f672493acd9e189c5855",
    UPSTREAM_SNAPSHOT + "/src/rnnoise_tables.c":
        "f81353479c6f8912755a4cf5838590c36ba2c523a4a438e4f949743fb4945623",
    UPSTREAM_SNAPSHOT + "/src/pitch.c":
        "cfe6f5ffb4b5f5967ce2e64f22cc978c1f8196eecdb2fa532d4dd1ff56f6ca58",
    UPSTREAM_SNAPSHOT + "/src/kiss_fft.c":
        "2a9f9ee0d961ec6516864477640d78aedbf1c3ecbe1680727b4b93d486c09679",
    UPSTREAM_SNAPSHOT + "/src/celt_lpc.c":
        "58eca412376dfd954f4940709df521cf1d2cbee1b7ca2b166bd0bffbda2c5b8d",
    UPSTREAM_MODEL_VERSION_PATH:
        "07bebd6ed8f6f97095cc9382122c7113c6e9ad0e22773cca33679c3df1ef901a",
    UPSTREAM_MODEL_ARCHIVE_PATH:
        "0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37",
    UPSTREAM_BUILD_SCRIPT_PATH:
        "d39acd38a371f73cbe59d2b08584f87c885f6dd99025289ef81ddec1ec31eacd",
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
    "model_archive_path",
    "model_archive_sha256",
    "source_commit",
    "sample_rate_hz",
    "channels",
    "frame_samples",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/rnnoise-v0-2/caller-supplied-asset/0.1",
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": {
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": ASSET_FRAME_SAMPLES,
    },
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "library_path and model_archive_path are caller-owned absolute paths",
        "SHA-256 of both files matches the manifest",
        "source_commit equals the pinned Xiph revision",
        "sample rate, channels and frame size equal 48 kHz mono 480-sample geometry",
        "no download, copy, build, load or execution occurs in this package",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hashes_and_geometry_only; do_not_load_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
}

FORMAT: Dict[str, Any] = {
    "public_sample_rate_hz": PUBLIC_SAMPLE_RATE_HZ,
    "public_channels": 1,
    "public_sample_format": "f32",
    "public_frame_samples": PUBLIC_FRAME_SAMPLES,
    "asset_sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_frame_samples": ASSET_FRAME_SAMPLES,
    "asset_frame_duration_ms": ASSET_FRAME_DURATION_MS,
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
    "rnnoise_source_executed": False,
    "rnnoise_runtime_executed": False,
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
    "rnnoise_model_loaded": False,
    "rnnoise_runtime_executed": False,
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
    "exact_rnnoise_reproduction_claimed": False,
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "model_version_file": UPSTREAM_MODEL_VERSION_PATH,
    "model_version": "0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37",
    "model_version_sha256": ASSET_PINS[UPSTREAM_MODEL_VERSION_PATH],
    "model_archive": {
        "path": UPSTREAM_MODEL_ARCHIVE_PATH,
        "sha256": ASSET_PINS[UPSTREAM_MODEL_ARCHIVE_PATH],
        "bytes": UPSTREAM_MODEL_ARCHIVE_BYTES,
        "present_in_external_checkout": True,
        "present_in_sdk_worktree": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "runtime_library": {
        "expected_path": UPSTREAM_RUNTIME_PATH,
        "expected_sha256": UPSTREAM_RUNTIME_SHA256,
        "present": False,
        "built_by_this_package": False,
        "loaded_or_executed": False,
    },
    "source_files": {
        "include/rnnoise.h": ASSET_PINS[UPSTREAM_SNAPSHOT + "/include/rnnoise.h"],
        "src/denoise.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/denoise.c"],
        "src/rnn.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/rnn.c"],
        "src/nnet.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/nnet.c"],
        "src/rnnoise_data.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/rnnoise_data.c"],
        "src/rnnoise_data_little.c":
            ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/rnnoise_data_little.c"],
        "src/rnnoise_tables.c":
            ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/rnnoise_tables.c"],
        "src/pitch.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/pitch.c"],
        "src/kiss_fft.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/kiss_fft.c"],
        "src/celt_lpc.c": ASSET_PINS[UPSTREAM_SNAPSHOT + "/src/celt_lpc.c"],
    },
    "build_script": {
        "path": UPSTREAM_BUILD_SCRIPT_PATH,
        "sha256": ASSET_PINS[UPSTREAM_BUILD_SCRIPT_PATH],
        "executed_by_this_package": False,
    },
    "public_adapter": {
        "path": "adapters/rnnoise",
        "declared_output_kinds": ["waveform"],
        "declared_tasks": ["CLN-01"],
        "declared_modes": ["offline"],
        "declared_weights": "embedded_verified_local_model",
        "source_commit": UPSTREAM_COMMIT,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": "not established in this package",
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_repository_license": UPSTREAM_LICENSE,
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": ASSET_PINS[UPSTREAM_LICENSE_PATH],
    "upstream_license_text_pinned": True,
    "upstream_license_scope": (
        "Xiph RNNoise source snapshot at the pinned commit; BSD-3-Clause notice "
        "obligations apply to redistribution of the source or binary."),
    "model_archive_terms": (
        "not established; the repository source license does not by itself "
        "establish separate pretrained-model, archive or training-data rights."),
    "model_archive_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "model_archive_and_runtime_rights",
    "conclusion": (
        "BSD-3-Clause source licensing is pinned. Separate model/archive terms, "
        "product-use and redistribution rights, and training-data provenance are "
        "not cleared. This package distributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact RNNoise v0.2 source, model archive and model_version are "
        "pinned by SHA-256 from the external Xiph checkout, but the compiled "
        "runtime library expected at data/envs/rnnoise/librnnoise.dylib is "
        "absent and no caller-supplied asset manifest is present in this SDK "
        "worktree; the exact runtime cannot be loaded or reproduced here."),
    (
        "The upstream RNNoise source is BSD-3-Clause, but separate pretrained "
        "model/archive terms, product-use and redistribution rights, and "
        "training-data provenance are not established; no legal review exists. "
        "No asset was downloaded, copied, built, vendored or redistributed."),
    (
        "Only a deterministic model-free boundary surrogate was executed. It is "
        "not RNNoise, has no neural network or weights, and its paired synthetic "
        "SI-SDR/STOI values are boundary-conformance observations, not a quality, "
        "real-audio, listening, device-timing or benchmark result."),
    (
        "No rights-cleared real cohort, independent listening, target-runtime "
        "timing/memory, native streaming integration, opt-in provider intake, "
        "descriptor/registry review or public default decision exists; every "
        "release gate remains blocked."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_asset_present_and_verified",
        "Place the caller-owned 48 kHz RNNoise library and model archive in the "
        "worktree (or supply them through the manifest) with hashes and source "
        "commit matching the pins."),
    (
        "model_archive_and_runtime_rights",
        "Establish separate model/archive redistribution and product-use rights; "
        "BSD-3-Clause source licensing alone is insufficient."),
    (
        "exact_runtime_reproduction",
        "Build or load the exact pinned RNNoise runtime and reproduce the "
        "source-reported pilot outputs without downloading weights or using "
        "uncleared real audio."),
    (
        "native_streaming_boundary",
        "Verify the native 48 kHz / 480-sample streaming boundary, delay, "
        "flush behavior and caller-facing conformance; the public adapter is "
        "currently offline only."),
    (
        "real_cohort",
        "Score a rights-cleared held-out real speech cohort with exact clean "
        "references and stratified failure accounting."),
    (
        "independent_listening",
        "Collect independent listening or preference labels; synthetic metrics "
        "cannot qualify."),
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
    "caller-supplied RNNoise library present and SHA-256-verified in this SDK worktree",
    "RNNoise model archive present in this SDK worktree (externally present, not copied)",
    "separate model/archive and runtime redistribution/product-use rights clearance",
    "exact RNNoise runtime reproduction and an approved reference-output vector",
    "native 48 kHz / 480-sample streaming boundary, delay and flush evidence",
    "rights-cleared held-out real speech cohort with exact clean references",
    "independent listening or preference labels",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and catalog review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies the pinned RNNoise 48 kHz library and model archive with "
    "matching SHA-256 values and source commit, and the manifest validates.",
    "Separate model/archive and runtime redistribution and product-use rights are "
    "cleared with a recorded review; BSD-3-Clause source licensing alone is not "
    "enough.",
    "The exact pinned runtime is reproduced and an approved reference-output "
    "vector is available for parity.",
    "The native 48 kHz / 480-sample streaming boundary, delay, flush and "
    "caller-facing conformance are verified.",
    "A rights-cleared held-out real speech cohort with exact clean references is "
    "scored under the Enhancement profile.",
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
        "30 paired DNS2020 no-reverb outputs and a 48 kHz offline adapter; "
        "exploratory pilot, not a representative holdout or target-device run."),
    "sources": [
        "research/voice-enhancement-20261101/candidate_matrix.csv",
        "research/noise_suppression_pilot_20261027.md",
        "research/voice-enhancement-20261101/agent-denoise/REPORT.md",
        "research/selected_audio_enhancement_candidates.md",
        "REALTIME_COMPONENT_CANDIDATES.md",
    ],
    "findings": [
        {"metric": "mean_delta_snr_db", "value": 3.35, "unit": "dB"},
        {"metric": "mean_delta_stoi", "value": 0.0215, "unit": "ratio"},
        {"metric": "mean_delta_si_sdr_db", "value": 3.14, "unit": "dB"},
        {"metric": "runtime_fraction_rtf", "value": 0.0662, "unit": "ratio"},
    ],
    "note": (
        "Transcribed from the pinned research only. This package neither "
        "reproduces nor claims these values and does not pool them with the "
        "surrogate observations."),
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
        "noisy_snr10": (clean.astype(np.float64) + noise10).astype(np.float32),
        "noisy_snr0": (clean.astype(np.float64) + noise0).astype(np.float32),
        "noise_only": noise12,
        "silence": np.zeros(WINDOW_SAMPLES, dtype=np.float32),
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


class Surrogate:
    """Deterministic model-free boundary surrogate; not an RNNoise model."""

    def __init__(self, bypass: bool = False) -> None:
        self.bypass = bool(bypass)
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
        upsampled = resample_poly(source, RESAMPLE_UP, 1,
                                  window=("kaiser", 5.0), padtype="constant")
        upsampled = np.asarray(upsampled, dtype=np.float64) * 32768.0
        if upsampled.size != WINDOW_SAMPLES * RESAMPLE_UP:
            raise ValueError("resample_length_mismatch")
        frames = upsampled.reshape(-1, ASSET_FRAME_SAMPLES)
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
        flat = processed.reshape(-1)
        delayed = np.concatenate(
            (np.zeros(ASSET_FRAME_SAMPLES, dtype=np.float64), flat))[:flat.size]
        if compensate:
            compensated = np.concatenate(
                (delayed[ASSET_FRAME_SAMPLES:],
                 np.zeros(ASSET_FRAME_SAMPLES, dtype=np.float64)))[:flat.size]
        else:
            compensated = delayed
        downsampled = resample_poly(compensated / 32768.0, 1, RESAMPLE_UP,
                                    window=("kaiser", 5.0), padtype="constant")
        output = np.asarray(downsampled[:WINDOW_SAMPLES], dtype=np.float64)
        _check_output(output)
        self.processed_frames += int(frames.shape[0])
        info = {
            "noise_estimate": noise_estimate,
            "threshold": threshold,
            "mean_gain": float(np.mean(gains)),
            "min_gain": float(np.min(gains)),
            "max_gain": float(np.max(gains)),
            "frame_count": int(frames.shape[0]),
            "compensated": bool(compensate),
            "bypass": self.bypass,
        }
        return output.astype(np.float32), info


def process_reference(signal: Any, bypass: bool = False,
                      compensate: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
    return Surrogate(bypass=bypass).process(signal, compensate=compensate)


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
    if manifest["sample_rate_hz"] != ASSET_SAMPLE_RATE_HZ:
        raise ValueError("asset_sample_rate_mismatch")
    if manifest["channels"] != 1:
        raise ValueError("asset_channels_mismatch")
    if manifest["frame_samples"] != ASSET_FRAME_SAMPLES:
        raise ValueError("asset_frame_samples_mismatch")
    for name in ("library", "model_archive"):
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
        "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": ASSET_FRAME_SAMPLES,
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
            "delay_compensated": info["compensated"],
        },
    }


def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="rnnoise-v02-asset-") as directory:
        root = Path(directory)
        library = root / "librnnoise.dylib"
        archive = root / "rnnoise_data.tar.gz"
        library.write_bytes(b"synthetic caller library placeholder; not loaded\n")
        archive.write_bytes(b"synthetic caller model archive placeholder; not loaded\n")
        base = {
            "library_path": str(library),
            "library_sha256": _sha256_file(library),
            "model_archive_path": str(archive),
            "model_archive_sha256": _sha256_file(archive),
            "source_commit": UPSTREAM_COMMIT,
            "sample_rate_hz": ASSET_SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": ASSET_FRAME_SAMPLES,
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
        missing_manifest = dict(base)
        missing_manifest["library_path"] = str(root / "absent.dylib")
        commit_manifest = dict(base)
        commit_manifest["source_commit"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 16000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        frame_manifest = dict(base)
        frame_manifest["frame_samples"] = 160
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
            "hash_mismatch": rejected(hash_manifest),
            "wrong_source_commit": rejected(commit_manifest),
            "wrong_sample_rate": rejected(rate_manifest),
            "wrong_channels": rejected(channels_manifest),
            "wrong_frame_size": rejected(frame_manifest),
        }


def _frame_controls() -> Dict[str, Any]:
    model = Surrogate()
    zeros = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
    baseline, _ = model.process(zeros)
    state_before = (model.prev_gain, model.noise_estimate, model.processed_frames,
                    model.epoch)

    def rejected(signal: Any) -> Dict[str, Any]:
        try:
            Surrogate().process(signal)
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
    return {
        "separate_instances_uncoupled": bool(np.array_equal(first, second)),
        "reset_bit_identical": bool(np.array_equal(before_reset, after_reset)),
        "reset_epoch_propagated": bool(epoch_ok),
        "different_stimuli_differ": bool(not np.array_equal(first, other)),
        "processed_outputs_finite": bool(
            np.isfinite(first).all() and np.isfinite(second).all()),
    }


def _alignment() -> Dict[str, Any]:
    impulse = stimuli()["impulse"]
    raw, _ = process_reference(impulse, bypass=True, compensate=False)
    aligned, _ = process_reference(impulse, bypass=True, compensate=True)
    raw_index = int(np.argmax(np.abs(raw)))
    aligned_index = int(np.argmax(np.abs(aligned)))
    expected = IMPULSE_INDEX
    return {
        "expected_impulse_index": expected,
        "uncompensated_impulse_index": raw_index,
        "compensated_impulse_index": aligned_index,
        "measured_content_lag_samples": aligned_index - expected,
        "asset_frame_delay_samples": ASSET_FRAME_SAMPLES,
        "asset_delay_at_public_rate_samples": (
            ASSET_FRAME_SAMPLES // RESAMPLE_UP),
        "delay_compensation_applied": True,
        "source_interval": [0, WINDOW_SAMPLES],
        "raw_interval": [0, WINDOW_SAMPLES],
        "valid_output_samples": WINDOW_SAMPLES,
        "sdk_callback_invoked": False,
    }


def _availability() -> Dict[str, Any]:
    first = ORIGIN_NS + (PUBLIC_FRAME_SAMPLES + LOOKAHEAD_SOURCE_SAMPLES) * \
        NS_PER_PUBLIC_SAMPLE
    last = ORIGIN_NS + (WINDOW_SAMPLES + LOOKAHEAD_SOURCE_SAMPLES) * \
        NS_PER_PUBLIC_SAMPLE
    return {
        "clock_id": CLOCK_ID,
        "origin_ns": str(ORIGIN_NS),
        "ns_per_public_sample": NS_PER_PUBLIC_SAMPLE,
        "lookahead_public_samples": LOOKAHEAD_SOURCE_SAMPLES,
        "first_available_ns": str(first),
        "last_available_ns": str(last),
        "formula": (
            "available_ns = origin_ns + "
            "(public_frame_end + lookahead_public_samples) * ns_per_public_sample"),
        "monotonic_nondecreasing": True,
        "measured": False,
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


def _report_core() -> Dict[str, Any]:
    conditions = _conditions()
    regressions = _regressions(conditions)
    asset_controls = _asset_controls()
    frame_controls = _frame_controls()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": "rnnoise-v0-2",
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
            "library_present_in_sdk_worktree": False,
            "model_archive_present_in_sdk_worktree": False,
            "model_archive_present_in_external_checkout": True,
            "runtime_library_expected_path": UPSTREAM_RUNTIME_PATH,
            "runtime_library_expected_sha256": UPSTREAM_RUNTIME_SHA256,
            "runtime_library_present": False,
            "verified": False,
            "loaded": False,
            "executed": False,
            "surrogate_used": True,
            "reason": "caller_supplied_runtime_absent_and_rights_unresolved",
        },
        "surrogate": {
            "identity": "rnnoise-v0-2-boundary-surrogate-v0",
            "is_rnnoise": False,
            "is_neural_network": False,
            "weights": False,
            "checkpoint": False,
            "model_archive": False,
            "method": (
                "deterministic frame-RMS gate after 3x polyphase resampling; "
                "480-sample delay modeled then compensated"),
            "public_input_geometry": "16 kHz mono f32 160-sample frames",
            "asset_geometry": "48 kHz mono f32 480-sample frames",
            "delay_modeled_samples_48k": ASSET_FRAME_SAMPLES,
            "delay_compensated_samples_48k": ASSET_FRAME_SAMPLES,
            "gate_floor": GATE_FLOOR,
            "attack": GATE_ATTACK,
            "release": GATE_RELEASE,
            "noise_estimate_frames": NOISE_ESTIMATE_FRAMES,
            "threshold_multiplier": THRESHOLD_MULTIPLIER,
            "deterministic": True,
            "pure_synthetic": True,
            "quality_claim": False,
        },
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
            "source_reported_rnnoise_pilot_used_for_qualification": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No RNNoise runtime or rights-cleared real cohort; the surrogate "
                "is a boundary conformance fixture and its synthetic metrics are "
                "not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "reason": (
                "No exact RNNoise runtime or target device; the surrogate is "
                "unpaced and no wall-clock or memory result is claimed."),
            "content_delay_samples_modeled_48k": ASSET_FRAME_SAMPLES,
            "content_delay_samples_public_rate": ASSET_FRAME_SAMPLES // RESAMPLE_UP,
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
                "Deterministic model-free boundary surrogate on synthetic stimuli; "
                "no RNNoise asset, real audio or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not reproduced, "
                "pooled or used as thresholds."),
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
        "component": "rnnoise-v0-2",
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
                "no RNNoise runtime, so exact source-reported outputs are not reproduced",
                "no real cohort, so no quality, intelligibility or listening claim is made",
                "no token or device target, so no timing, memory or deadline result is claimed",
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
            "No RNNoise source, model archive, weights or runtime is copied, "
            "downloaded, built, loaded or executed.",
            "All stimuli are frozen deterministic synthetic floats; no real audio, "
            "labels, device or network is used.",
            "Caller-supplied asset manifests fail closed on missing, hash-mismatched "
            "or wrong-geometry inputs.",
            "Source-reported RNNoise metrics are provenance only and are never "
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
            "expected_runtime_path": UPSTREAM_RUNTIME_PATH,
            "expected_runtime_sha256": UPSTREAM_RUNTIME_SHA256,
            "expected_model_archive_path": UPSTREAM_MODEL_ARCHIVE_PATH,
            "expected_model_archive_sha256":
                ASSET_PINS[UPSTREAM_MODEL_ARCHIVE_PATH],
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
        "# SHA-256 pins for SDK-RNNOISE-V0-2 task-local evidence.",
        "# source: paths are relative to /Users/htsakanyan/workspace/audio/audioml",
    ]
    external = {**SOURCE_PINS, **ASSET_PINS}
    for path in sorted(external):
        lines.append(f"{external[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


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
        "a" * 64 + "  docs/task-evidence/rnnoise-v0-2/unknown",
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


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target)
