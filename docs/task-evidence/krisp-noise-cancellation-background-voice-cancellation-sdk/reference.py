# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for

SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK.

The exact licensed Krisp Noise Cancellation / Background Voice Cancellation
SDK, entitlement key, platform build, model bundle and runtime are absent. The
merged research evidence records a documentation-level census entry only:
versioned outbound/inbound noise-cancellation and background-voice-cancellation
model families, sample-rate profiles, CPU tiers and on-request MAX models, with
access available only through a commercial licence. No release version, ABI,
artifact, byte count, SHA-256, term, frame/hop contract, processed data, vendor
output or score is recorded.

This module therefore never imports, links, downloads or executes a vendor SDK,
never loads a model, never reads or writes real audio, never scans a network,
never measures a device clock and never inherits a sibling observation. It
provides three verifiable pieces:

* a fail-closed absence/asset audit over a fixed probe list plus the pinned
  local asset register, recording the missing entitlement, artifact, models,
  runtime, rights, cohort and vendor output;
* a caller-supplied licensed-deployment manifest contract validated without
  execution, with every malformed, missing, invalid or nonfinite case rejected
  before use;
* a deterministic synthetic enhancement accounting control at the public v0
  geometry: identity/noisy passthrough, sample and peak accounting, exact
  energy ratios and frame-causal mapping, explicitly not model output.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK"
TITLE = "Krisp Noise Cancellation / Background Voice Cancellation SDK"
SLUG = "krisp-noise-cancellation-background-voice-cancellation-sdk"
COMPONENT = "krisp-noise-cancellation-background-voice-cancellation-sdk"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "cb3d9812875b741a320c6cfe22de8043952fdd16"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.removeprefix('SDK-')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK")
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"
REQUIRED_INTERPRETER = "3.12.16"

VENDOR = "Krisp"
PRODUCT = SLUG
PRODUCT_RECORD_NAME = (
    "Krisp Noise Cancellation / Background Voice Cancellation SDK")
VENDOR_RECORD_LINE = 78
VENDOR_RECORD_PATH = "research/noise_suppression_candidate_census.md"
ASSET_REGISTER_PATH = "research/noise_suppression_assets_20261027.json"
SIBLING_BENCHMARK_PATH = "research/cpp-library-krisp-benchmark-20261109.md"
VENDOR_DOCUMENTATION_LOCATOR: Optional[str] = None
PRODUCT_REPORTED_FAMILIES = (
    "noise_cancellation",
    "background_voice_cancellation",
)
TASK_SCOPE = "licensed_noise_and_background_voice_cancellation"
TASK_GEOMETRY_STATUS = "unestablished"
REPORTED_RUNTIME_CHARACTER = "commercial_low_latency_call_sdk"
REPORTED_STREAMING = True
LOCAL_RUNTIME_PRESENT = False

# Control geometry is the public SDK v0 boundary, not Krisp geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160

# Fixed workspace paths.  Absence is recorded, not filled.
MISSING_SDK_PATH = "data/sdk/krisp-sdk"
MISSING_MODEL_BUNDLE_PATH = "data/models/krisp"
RUNTIME_ENV_PATH = "data/envs/krisp"
RUNTIME_LOCK_PATH = "data/envs/krisp/sdk.lock"
RIGHTS_RECORD_PATH = "data/rights/krisp-sdk.json"
COHORT_MANIFEST_PATH = "data/runs/krisp-nc-bvc/manifest.json"
VENDOR_OUTPUT_PATH = "data/runs/krisp-nc-bvc/outputs"
RESULTS_PATH = "reports/krisp-nc-bvc"

# Fixed absence probes.  No recursive walk.  Any appearance forces a
# re-evaluation instead of silently promoting the candidate.
WORKSPACE_PROBES: Tuple[str, ...] = (
    "data/checkouts/krisp",
    "data/checkouts/krisp-sdk",
    "data/models/krisp",
    "data/sdk/krisp-sdk",
    "data/envs/krisp",
    "data/licenses/krisp-sdk",
    "data/rights/krisp-sdk.json",
    "data/runs/krisp-nc-bvc",
    "data/runs/krisp-nc-bvc/manifest.json",
    "reports/krisp-nc-bvc",
    "research/krisp",
    "research/krisp-sdk",
)
WORKTREE_PROBES: Tuple[str, ...] = (
    "third_party/krisp",
    "third_party/krisp-sdk",
    "adapters/krisp-noise-cancellation",
    "schemas/providers/krisp",
    "build/check-env/lib/python3.12/site-packages/krisp",
)
HOME_PROBES: Tuple[str, ...] = (
    "~/.cache/krisp",
    "~/.config/krisp",
    "~/Library/Application Support/Krisp",
    "~/Library/Caches/krisp",
    "~/krisp",
)
ABSENCE_PROBES: Tuple[str, ...] = (
    tuple("workspace:" + item for item in WORKSPACE_PROBES)
    + tuple("worktree:" + item for item in WORKTREE_PROBES)
    + tuple("home:" + item for item in HOME_PROBES)
)

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/cpp-library-krisp-benchmark-20261109.md":
        "7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/ai-coustics-quail/README.md":
        "66239ce8eeff8598145c0b356f09c91ece6a53f1cbe425a77e5b3d5bfc8e2781",
    "docs/task-evidence/ai-coustics-quail/report.json":
        "77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0",
    "docs/task-evidence/hecttor-commercial-ecosystem-products/README.md":
        "fc3b8e6ffec88b17129d4ae4b6e877abf487e9492cbe9db0382249163f9930e7",
    "docs/task-evidence/hecttor-commercial-ecosystem-products/report.json":
        "c66f5fb2f76b0b639f6c605c21d9bb6121025cc931a26ab3a253ef3cf1977cb4",
    "docs/task-evidence/hume-octave/README.md":
        "b5c692bf76b0e939efe5f13d68c768b3c207ce7d4b2de02f281c14dee60fb912",
    "docs/task-evidence/hume-octave/report.json":
        "d6c682f7f88fa8c43b253a59de3592f702440c5b0ef988f36d58e3ff6e395a08",
}
LOCAL_PIN_PATHS = (
    "LICENSES.md",
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

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "krisp_geometry_status": TASK_GEOMETRY_STATUS,
    "krisp_geometry_asserted": False,
    "vendor_reported_runtime_character": REPORTED_RUNTIME_CHARACTER,
    "vendor_reported_streaming": REPORTED_STREAMING,
    "vendor_reported_sample_rate_profiles": "multiple_unspecified",
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_mode": "frame_causal_contract_control",
    "control_incremental_streaming": True,
    "task_scope": TASK_SCOPE,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "vendor_sdk_imported": False,
    "vendor_sdk_linked": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "peer_evidence_inherited": False,
    "processed_data_present": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_krisp_runtime": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_output_read": False,
    "vendor_runtime_executed": False,
    "vendor_sdk_imported": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No Krisp SDK, platform build, library, header, entitlement key, model "
    "bundle, licence text, telemetry statement or runtime is present, "
    "imported, linked, loaded or executed.",
    "No network request, download, staging, registration or asset "
    "redistribution occurs.",
    "No real audio, corpus, consent record, vendor-processed output or score "
    "is consumed, produced or read.",
    "No denoising, background-voice cancellation, noise suppression, SI-SDR, "
    "STOI, DNSMOS, PESQ, WER, latency, memory, RTF, listening or device "
    "measurement is performed or claimed.",
    "No Krisp product release, SDK version, ABI, platform package, byte count "
    "or SHA-256 is asserted as verified.",
    "No Krisp Voice Isolation, accent-conversion or public-output-scoring "
    "observation is inherited or pooled; those are separate products and "
    "separate tasks.",
    "No Hecttor, Hume, ai-coustics, Desert Ant Labs, H-GTCRN or other "
    "commercial-vendor or open-model result is inherited, compared or pooled.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "vendor_entitlement",
        "kind": "commercial_license_and_entitlement",
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "exact_release_and_platform_sdk",
        "kind": "versioned_sdk_platform_build",
        "recorded_locator": VENDOR_DOCUMENTATION_LOCATOR,
        "revision": None,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "model_bundle",
        "kind": "noise_cancellation_and_background_voice_cancellation_models",
        "reported_families": list(PRODUCT_REPORTED_FAMILIES),
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "runtime_lock",
        "kind": "locked_offline_host_runtime",
        "path": RUNTIME_LOCK_PATH,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "vendor_terms_record",
        "kind": "vendor_evaluation_telemetry_data_and_deployment_terms",
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "rights_and_consent_record",
        "path": RIGHTS_RECORD_PATH,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "rights_cleared_cohort",
        "path": COHORT_MANIFEST_PATH,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "vendor_output_bundle",
        "path": VENDOR_OUTPUT_PATH,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "separated_external_results",
        "path": RESULTS_PATH,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
)

REQUIRED_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "ART-01",
        "kind": "vendor_access",
        "requirement": (
            "Approved Krisp commercial licence and entitlement for the exact "
            "noise-cancellation and background-voice-cancellation SDK, with "
            "scope, duration, permitted use and key reference."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-02",
        "kind": "vendor_release",
        "requirement": (
            "The exact product release and platform build with SDK version, "
            "ABI, install layout, byte counts, SHA-256 values and a signed "
            "artifact manifest."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-03",
        "kind": "model_bundle",
        "requirement": (
            "The exact noise-cancellation and background-voice-cancellation "
            "model bundles with selected family, sample-rate profile, CPU "
            "tier or on-request MAX model and per-file digests."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-04",
        "kind": "runtime_lock",
        "requirement": (
            "A locked offline host runtime with exact OS, interpreter/SDK "
            "versions, packages, device, determinism settings and install "
            "digest at data/envs/krisp/sdk.lock."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-05",
        "kind": "rights_bundle",
        "requirement": (
            "Reviewed vendor evaluation, telemetry, data-handling, retention, "
            "offline, deployment, redistribution, attribution and output-use "
            "terms with an independent review reference."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-06",
        "kind": "isolation_configuration",
        "requirement": (
            "Frozen isolated configuration for noise cancellation and "
            "background voice cancellation with other features disabled, "
            "mono channel layout, rate/frame/hop/reset/drain and state "
            "behavior."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-07",
        "kind": "processed_data",
        "requirement": (
            "A rights-cleared input cohort with consent and a vendor-processed "
            "output bundle produced on the approved runtime for the frozen "
            "configuration."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
    {
        "id": "ART-08",
        "kind": "external_results",
        "requirement": (
            "Separated local-runtime, vendor-output-scoring and vendor-claim "
            "records: controls, baseline, paired metrics where permitted, "
            "preservation, peaks, invalid outputs, unpaired screen or "
            "listening, alignment, state, memory and measured timing."),
        "present": False,
        "sha256": None,
        "bytes": None,
        "revision": None,
        "verified": False,
        "blocked": True,
    },
)

CALLER_ASSET_FIELDS = (
    "background_voice_cancellation_enabled",
    "channels",
    "config_path",
    "config_sha256",
    "entitlement_approved",
    "entitlement_id",
    "entitlement_path",
    "entitlement_sha256",
    "install_root",
    "license_record_path",
    "license_record_sha256",
    "model_bundle_path",
    "model_bundle_sha256",
    "noise_cancellation_enabled",
    "other_features_disabled",
    "platform",
    "product",
    "release_version",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "sample_rate_hz",
    "scope",
    "telemetry_disclosure",
    "vendor_terms_path",
    "vendor_terms_sha256",
)

CALLER_FILE_PAIRS = (
    ("config_path", "config_sha256"),
    ("entitlement_path", "entitlement_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("model_bundle_path", "model_bundle_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("vendor_terms_path", "vendor_terms_sha256"),
)
CALLER_DIR_FIELDS = ("install_root",)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_SCOPE = TASK_SCOPE
CALLER_PRODUCT = PRODUCT
ALLOWED_RATES_HZ = (8000, 16000, 32000, 48000)
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
RELEASE_PATTERN = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
PLATFORM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
ENTITLEMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$")
SHA_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/licensed-deployment-manifest/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_exact_fields_bool_flags_entitlement_approval_telemetry_"
        "disclosure_isolation_release_platform_geometry_absolute_paths_and_"
        "sha256; do_not_import_link_or_execute_the_vendor_sdk_here"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_scope": CALLER_SCOPE,
    "required_product": CALLER_PRODUCT,
    "required_channels": CHANNELS,
    "allowed_sample_rates_hz": list(ALLOWED_RATES_HZ),
    "require_noise_cancellation_enabled": True,
    "require_other_features_disabled": True,
    "require_entitlement_approved": True,
    "require_telemetry_disclosure": True,
    "revision_pin_available": False,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_hz": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "notes": (
        "Every config, entitlement, licence record, model bundle, runtime lock "
        "and vendor-terms file must exist at an absolute path and match its "
        "declared SHA-256 before a caller may process audio. No Krisp release "
        "version, ABI, artifact digest, platform package or frame/hop contract "
        "is pinned in the merged evidence, so none is invented."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "vendor_entitlement_absent",
        "state": "absent",
        "requirement": (
            "Supply the approved Krisp commercial licence and entitlement for "
            "the exact noise-cancellation and background-voice-cancellation "
            "SDK, with scope, duration, seats, permitted use and key "
            "reference; no approval, key or licence record exists."),
    },
    {
        "id": "exact_release_artifact_absent",
        "state": "absent",
        "requirement": (
            "Name and pin the exact product release, SDK version, ABI, "
            "platform build, install layout, byte counts and SHA-256 values; "
            "the census records versioned model families but no release "
            "identity or artifact."),
    },
    {
        "id": "model_bundle_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact noise-cancellation and background-voice-"
            "cancellation model bundles, selected family, sample-rate profile, "
            "CPU tier or on-request MAX model, each with byte count and "
            "SHA-256; no model byte is present or identified."),
    },
    {
        "id": "runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide a locked offline host runtime with exact OS, "
            "interpreter/SDK versions, packages, device, determinism settings "
            "and install digest at data/envs/krisp/sdk.lock; no environment "
            "or lock exists."),
    },
    {
        "id": "terms_unreviewed",
        "state": "absent",
        "requirement": (
            "Record and review vendor evaluation, telemetry, data-handling, "
            "retention, offline-operation, deployment, redistribution, "
            "attribution and output-use terms for the exact release; no terms "
            "text or independent review reference exists."),
    },
    {
        "id": "isolation_contract_unverified",
        "state": "absent",
        "requirement": (
            "Freeze the isolated configuration: noise cancellation and "
            "background voice cancellation selection, other features "
            "disabled, channel layout, rate/frame/hop, reset and drain, state "
            "behavior and model switching; no runtime or API surface exists "
            "to verify isolation."),
    },
    {
        "id": "cohort_and_vendor_output_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared input cohort with consent and produce "
            "vendor-processed output on the approved runtime for the frozen "
            "configuration; no input, consent, output bundle or provenance "
            "record exists."),
    },
    {
        "id": "separated_results_absent",
        "state": "absent",
        "requirement": (
            "Produce separated local-runtime, vendor-output-scoring and "
            "vendor-claim records with identity/noisy controls, an established "
            "task-matched baseline, paired SI-SDR/STOI where permitted, "
            "clean-speech preservation, peaks, invalid outputs, a separately "
            "labeled predictive screen or authorized listening, alignment, "
            "state, memory and measured content/availability timing."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "entitlement_and_access",
        "Approved Krisp licence, entitlement, key reference, scope, duration "
        "and permitted use are recorded and independently reviewed.",
    ),
    (
        "exact_release_and_artifact_identity",
        "The exact product release, SDK version, ABI, platform build, byte "
        "counts and SHA-256 values match immutable pins.",
    ),
    (
        "runtime_admission",
        "A locked offline host runtime with exact versions and a recorded "
        "deterministic platform is admitted.",
    ),
    (
        "vendor_terms_and_data_handling",
        "Vendor evaluation, telemetry, data-handling, retention, offline, "
        "deployment, redistribution, attribution and output-use terms are "
        "reviewed.",
    ),
    (
        "isolation_and_release_contract",
        "Noise cancellation and background voice cancellation are isolated, "
        "other features are disabled, and rate/frame/hop/reset/drain/state "
        "behavior is frozen and verified.",
    ),
    (
        "rights_cleared_cohort_and_output",
        "A rights-cleared input cohort with consent and vendor-processed "
        "output on the approved runtime exist with provenance.",
    ),
    (
        "enhancement_evidence_and_separation",
        "Controls, task-matched baseline, paired metrics where permitted, "
        "preservation, peaks, invalid outputs, unpaired screen or authorized "
        "listening, alignment, state, memory and measured timing are recorded "
        "with local-runtime, vendor-output and vendor-claim kept separate.",
    ),
    (
        "opt_in_provider_intake_and_release",
        "Opt-in OFF-by-default provider intake, descriptor/default review, "
        "exact-head independent review and release approval are complete.",
    ),
)

ENHANCEMENT_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "identity_noisy_control",
        "Run an identity/noisy control alongside the candidate.",
        "structural_only",
    ),
    (
        "task_matched_baseline",
        "Compare against an established task-matched baseline.",
        "absent",
    ),
    (
        "paired_si_sdr_and_stoi",
        "Score paired SI-SDR and STOI where permitted clean references exist.",
        "not_measured",
    ),
    (
        "clean_speech_preservation",
        "Measure clean-speech preservation.",
        "not_measured",
    ),
    (
        "peaks_and_invalid_outputs",
        "Measure output peaks and invalid outputs.",
        "structural_only",
    ),
    (
        "unpaired_screen_or_listening",
        "Use a separately labeled predictive screen or authorized listening "
        "for unpaired speech.",
        "absent",
    ),
    (
        "alignment_state_memory",
        "Report alignment, state and memory for the exact runtime.",
        "not_measured",
    ),
    (
        "content_availability_timing",
        "Measure content delay and availability timing for the exact runtime.",
        "not_measured",
    ),
)

PROFILE_PHRASES: Tuple[str, ...] = (
    "identity/noisy control",
    "task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation",
    "peaks and invalid outputs",
    "predictive screen or authorized listening",
    "Report alignment, state, memory",
    "content/availability timing",
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": VENDOR_RECORD_PATH,
    "source_sha256": SOURCE_PINS[VENDOR_RECORD_PATH],
    "record_name": PRODUCT_RECORD_NAME,
    "report_line": VENDOR_RECORD_LINE,
    "finding": (
        "Commercial low-latency call SDK; distinct environmental-noise and "
        "competing-voice model families."),
    "reported_terms": (
        "Official RTC SDK docs enumerate versioned outbound/inbound noise "
        "cancellation and background voice cancellation models, sample-rate "
        "profiles, CPU tiers and on-request MAX models."),
    "reported_capabilities": {
        "model_families": list(PRODUCT_REPORTED_FAMILIES),
        "model_family_count": 2,
        "versioned_models_reported": True,
        "outbound_inbound_reported": True,
        "sample_rate_profiles": "multiple_unspecified",
        "cpu_tiers_reported": True,
        "on_request_max_models_reported": True,
        "runtime_character": REPORTED_RUNTIME_CHARACTER,
        "streaming_reported": REPORTED_STREAMING,
        "access": "licensed_sdk_only",
    },
    "not_reported": [
        "release_version",
        "sdk_version",
        "abi_version",
        "platform_build",
        "artifact_name",
        "artifact_byte_count",
        "artifact_sha256",
        "license_text",
        "telemetry_terms",
        "deployment_terms",
        "channel_layout",
        "frame_samples",
        "hop_samples",
        "reset_contract",
        "drain_contract",
        "latency_ms",
        "processed_data",
        "vendor_output",
        "score",
    ],
    "sibling_context_not_attributed": [
        "research/cpp-library-krisp-benchmark-20261109.md describes Krisp "
        "Voice Isolation 2.5 public outputs (265 files) scored with DNSMOS-C "
        "(3.815 default), a different product from this NC/BVC SDK. Its audio "
        "is not in this repository and no value is inherited here.",
        "The sibling tasks SDK-KRISP-VOICE-ISOLATION-2-5, "
        "SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING and "
        "SDK-KRISP-ACCENT-CONVERSION are separate rows; this branch has no "
        "merged evidence package for any of them and nothing is pooled.",
        "Hecttor, Hume Octave, ai-coustics Quail/Rook, Desert Ant Labs Clear "
        "and H-GTCRN are separate commercial-vendor or open-model blockers; "
        "no manifest shape, control, term or score is Krisp evidence.",
    ],
    "notes": (
        "No Krisp artifact, runtime, processed data, vendor output or score "
        "was acquired. No release, latency, quality or resource value is "
        "attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "synthetic_enhancement_identity_and_energy_accounting_control_"
    "not_vendor_output")
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 2
CONTROL_OUTPUT_SAMPLES = CONTROL_SOURCE_SAMPLES
PCM_SAMPLE_CAP = 10_000_000
CONTROL_GAIN = 0.5

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_wrong_rate",
    "pcm_stereo",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_out_of_range",
    "pcm_bool",
    "pcm_string",
    "json_duplicate_key",
    "json_nonfinite",
    "json_root_list",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_entitlement_not_approved",
    "manifest_telemetry_not_disclosed",
    "manifest_wrong_product",
    "manifest_bad_release_version",
    "manifest_empty_platform",
    "manifest_unsupported_rate",
    "manifest_rate_bool",
    "manifest_rate_nan",
    "manifest_channels_zero",
    "manifest_channels_float",
    "manifest_scope_mismatch",
    "manifest_features_not_disabled",
    "manifest_noise_cancellation_disabled",
    "manifest_bvc_not_bool",
    "manifest_empty_entitlement_id",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3

# Built by adjacent-literal concatenation so no single Python string literal
# contains the contiguous SPDX marker token.
SPDX_COPYRIGHT_KEY = "SPDX-" "FileCopyrightText"
SPDX_LICENSE_KEY = "SPDX-" "License-Identifier"


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


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
    try:
        return json.dumps(_normalize_negzero(value), sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON while rejecting non-finite constants and duplicate keys."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Fixed absence and asset audit.  No recursive walk, no network, no SDK.
# ---------------------------------------------------------------------------

def _probe(item: str) -> Dict[str, Any]:
    location, relative = item.split(":", 1)
    if location == "workspace":
        path = SOURCE_ROOT / relative
    elif location == "worktree":
        path = SDK_ROOT / relative
    else:
        path = Path(os.path.expanduser(relative))
    return {
        "probe": item,
        "location": location,
        "path": relative,
        "present": path.exists(),
    }


def probe_absence() -> List[Dict[str, Any]]:
    return [_probe(item) for item in ABSENCE_PROBES]


def _asset_register() -> Dict[str, Any]:
    path = SOURCE_ROOT / ASSET_REGISTER_PATH
    if not path.is_file():
        return {
            "path": ASSET_REGISTER_PATH,
            "present": False,
            "candidate_count": 0,
            "krisp_entry_present": False,
            "entries_matching_krisp": 0,
            "candidate_ids_sha256": None,
        }
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, Reject):
        return {
            "path": ASSET_REGISTER_PATH,
            "present": True,
            "candidate_count": 0,
            "krisp_entry_present": False,
            "entries_matching_krisp": 0,
            "candidate_ids_sha256": None,
        }
    candidates = document.get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []
    matches = [item for item in candidates
               if isinstance(item, dict)
               and "krisp" in json.dumps(item, sort_keys=True).lower()]
    identifiers = sorted(
        str(item.get("id", "")) for item in candidates if isinstance(item, dict))
    return {
        "path": ASSET_REGISTER_PATH,
        "present": True,
        "candidate_count": len(candidates),
        "krisp_entry_present": bool(matches),
        "entries_matching_krisp": len(matches),
        "candidate_ids_sha256": sha256(canonical_bytes(identifiers)),
    }


def audit_assets() -> Dict[str, Any]:
    probes = probe_absence()
    workspace = {
        relative: (SOURCE_ROOT / relative).exists()
        for relative in WORKSPACE_PROBES
    }
    worktree = {
        relative: (SDK_ROOT / relative).exists()
        for relative in WORKTREE_PROBES
    }
    register = _asset_register()
    return {
        "vendor": VENDOR,
        "product": PRODUCT,
        "sdk_path": MISSING_SDK_PATH,
        "sdk_present": workspace[MISSING_SDK_PATH],
        "model_bundle_path": MISSING_MODEL_BUNDLE_PATH,
        "model_bundle_present": workspace[MISSING_MODEL_BUNDLE_PATH],
        "runtime_env_present": workspace[RUNTIME_ENV_PATH],
        "runtime_lock_present": workspace[RUNTIME_ENV_PATH] and (
            SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file(),
        "rights_record_present": workspace[RIGHTS_RECORD_PATH],
        "cohort_manifest_present": workspace[COHORT_MANIFEST_PATH],
        "vendor_output_present": workspace["data/runs/krisp-nc-bvc"],
        "results_present": workspace["reports/krisp-nc-bvc"],
        "license_record_present": workspace["data/licenses/krisp-sdk"],
        "worktree_asset_paths": worktree,
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["present"] for item in probes),
        "asset_register": register,
        "requested_config": {
            "task_scope": TASK_SCOPE,
            "profile": PROFILE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "runtime_character": REPORTED_RUNTIME_CHARACTER,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "release_pin": None,
        },
    }


def _profile_row() -> Dict[str, Any]:
    relative = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        raise Reject("acceptance profile document is unavailable")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("acceptance profile document unreadable") from error
    rows = [line.strip() for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        raise Reject("expected exactly one Enhancement profile row")
    row = rows[0]
    present = [phrase for phrase in PROFILE_PHRASES if phrase in row]
    return {
        "path": relative,
        "sha256": SOURCE_PINS[relative],
        "row": row,
        "row_count": len(rows),
        "phrases_required": list(PROFILE_PHRASES),
        "phrases_present": present,
        "all_phrases_present": len(present) == len(PROFILE_PHRASES),
    }


def task_row_identity() -> Dict[str, Any]:
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        raise Reject("task board is unavailable at " + relative)
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise Reject("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("linked task row identity mismatch")
    if stable["repository"] != "audio-sdk" or stable["mode"] != MODE:
        raise Reject("linked task row repository/mode mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise Reject("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim reviewer mismatch")
    return {
        "source": relative,
        "gating": "stable_identity_only",
        "whole_file_hashed": False,
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic PCM and enhancement accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_noisy_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x4B524953
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 43, 0.25) + 0.05 * noise)
    return samples


def synthetic_clean_pcm() -> List[float]:
    samples: List[float] = []
    for index in range(CONTROL_SOURCE_SAMPLES):
        samples.append(_triangle(index, 43, 0.25))
    return samples


def identity_control(noisy: Sequence[float]) -> List[float]:
    """Identity/noisy control: a sample-for-sample copy, no model involved."""
    checked = validate_pcm(noisy, CONTROL_SAMPLE_RATE_HZ)
    return list(checked)


def scaled_control(noisy: Sequence[float]) -> List[float]:
    """Exact -6.0206 dB gain control used only for energy accounting."""
    checked = validate_pcm(noisy, CONTROL_SAMPLE_RATE_HZ)
    return [CONTROL_GAIN * value for value in checked]


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if channels != CHANNELS:
        raise Reject("only mono is supported")
    if not isinstance(signal, (list, tuple)):
        raise Reject("signal must be a sample sequence")
    if not signal:
        raise Reject("signal must be nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise Reject("signal exceeds the evidence cap")
    checked: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise Reject(f"sample {index} is not numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise Reject(f"sample {index} is not finite")
        if value < -1.0 or value > 1.0:
            raise Reject(f"sample {index} is outside [-1, 1]")
        checked.append(value)
    return checked


def exact_energy(signal: Sequence[float]) -> Fraction:
    return sum((Fraction(value) * Fraction(value) for value in signal),
               Fraction(0))


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "energy_exact": fraction_text(exact_energy(values)),
        "sha256": sha256(canonical_bytes(list(values))),
    }


def energy_accounting(noisy: Sequence[float],
                      output: Sequence[float]) -> Dict[str, Any]:
    noisy_energy = exact_energy(noisy)
    output_energy = exact_energy(output)
    if noisy_energy == 0:
        raise Reject("noisy control energy is zero")
    ratio = output_energy / noisy_energy
    return {
        "noisy_energy_exact": fraction_text(noisy_energy),
        "output_energy_exact": fraction_text(output_energy),
        "output_to_noisy_energy_ratio": fraction_text(ratio),
        "interpretation": (
            "exact_rational_energy_ratio_for_the_synthetic_control_only"),
        "paired_si_sdr_db": None,
        "paired_stoi": None,
        "metric_status": "not_measured",
    }


def frame_accounting(source_samples: int, output_samples: int) -> Dict[str, Any]:
    if not isinstance(source_samples, int) or isinstance(source_samples, bool):
        raise Reject("source sample count must be an integer")
    if not isinstance(output_samples, int) or isinstance(output_samples, bool):
        raise Reject("output sample count must be an integer")
    if source_samples <= 0 or output_samples <= 0:
        raise Reject("sample counts must be positive")
    if source_samples % SDK_FRAME_SAMPLES != 0:
        raise Reject("source sample count must be a whole number of frames")
    if output_samples != source_samples:
        raise Reject("identity control must conserve samples")
    return {
        "frame_samples": SDK_FRAME_SAMPLES,
        "hop_samples": SDK_FRAME_SAMPLES,
        "frame_count": source_samples // SDK_FRAME_SAMPLES,
        "source_samples": source_samples,
        "output_samples": output_samples,
        "sample_conservation": True,
        "content_delay_samples": 0,
        "content_delay_units": "control_only_not_vendor_timing",
        "source_duration_s": fraction_text(
            Fraction(source_samples, CONTROL_SAMPLE_RATE_HZ)),
        "output_duration_s": fraction_text(
            Fraction(output_samples, CONTROL_SAMPLE_RATE_HZ)),
        "vendor_timing_measured": False,
        "device_timing_measured": False,
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    good_noisy = synthetic_noisy_pcm()
    good_manifest = _shape_only_manifest()
    existing = _existing_file_manifest()

    def case(case_id: str, action) -> Dict[str, Any]:
        try:
            action()
        except Reject as error:
            return {"case": case_id, "result": "rejected",
                    "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case": case_id, "result": "unexpected_error",
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_noisy, 8000)),
        ("pcm_stereo", lambda: validate_pcm(
            good_noisy, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}')),
        ("json_nonfinite", lambda: strict_loads('{"a":Infinity}')),
        ("json_root_list", lambda: strict_loads("[1,2]")),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("config_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "config_path", "config/krisp.json")),
        ("manifest_bad_sha", wrong("config_sha256", "ABC")),
        ("manifest_entitlement_not_approved", wrong(
            "entitlement_approved", False)),
        ("manifest_telemetry_not_disclosed", wrong(
            "telemetry_disclosure", False)),
        ("manifest_wrong_product", wrong("product", "krisp-voice-isolation")),
        ("manifest_bad_release_version", wrong("release_version", "latest")),
        ("manifest_empty_platform", wrong("platform", "")),
        ("manifest_unsupported_rate", wrong("sample_rate_hz", 44100)),
        ("manifest_rate_bool", wrong("sample_rate_hz", True)),
        ("manifest_rate_nan", wrong("sample_rate_hz", math.nan)),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_channels_float", wrong("channels", 1.0)),
        ("manifest_scope_mismatch", wrong("scope", "unlicensed_benchmark")),
        ("manifest_features_not_disabled", wrong(
            "other_features_disabled", False)),
        ("manifest_noise_cancellation_disabled", wrong(
            "noise_cancellation_enabled", False)),
        ("manifest_bvc_not_bool", wrong(
            "background_voice_cancellation_enabled", 1)),
        ("manifest_empty_entitlement_id", wrong("entitlement_id", "")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, config_path=(
                "/nonexistent/krisp-fixtures/config.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, install_root=(
                "/nonexistent/krisp-fixtures/no-sdk")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, config_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case order mismatch")
    pcm_summary(good_noisy, CONTROL_SAMPLE_RATE_HZ)
    pcm_summary(synthetic_clean_pcm(), CONTROL_SAMPLE_RATE_HZ)
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/krisp-evidence-fixture"
    digest = "0" * 64
    return {
        "background_voice_cancellation_enabled": True,
        "channels": CHANNELS,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "entitlement_approved": True,
        "entitlement_id": "eval-0001",
        "entitlement_path": root + "/entitlement.bin",
        "entitlement_sha256": digest,
        "install_root": root + "/sdk",
        "license_record_path": root + "/rights.json",
        "license_record_sha256": digest,
        "model_bundle_path": root + "/models",
        "model_bundle_sha256": digest,
        "noise_cancellation_enabled": True,
        "other_features_disabled": True,
        "platform": "macos-arm64",
        "product": CALLER_PRODUCT,
        "release_version": "0.0.0",
        "runtime_lock_path": root + "/sdk.lock",
        "runtime_lock_sha256": digest,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "telemetry_disclosure": True,
        "vendor_terms_path": root + "/terms.md",
        "vendor_terms_sha256": digest,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading a vendor runtime.  Each pair carries the real digest so a single
    corrupted digest reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "config_path": HERE / "reference.py",
        "entitlement_path": HERE / "contract.json.license",
        "license_record_path": HERE / "LICENSES.md",
        "model_bundle_path": HERE / "run.py",
        "runtime_lock_path": HERE / "SOURCES.sha256.license",
        "vendor_terms_path": HERE / "README.md",
    }
    manifest: Dict[str, Any] = {
        "background_voice_cancellation_enabled": True,
        "channels": CHANNELS,
        "entitlement_approved": True,
        "entitlement_id": "eval-0001",
        "install_root": str(HERE),
        "noise_cancellation_enabled": True,
        "other_features_disabled": True,
        "platform": "macos-arm64",
        "product": CALLER_PRODUCT,
        "release_version": "0.0.0",
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "telemetry_disclosure": True,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(path.read_bytes())
    return manifest


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_MANIFEST_BYTES:
                raise Reject("asset exceeds the evidence cap")
            digest.update(chunk)
    return digest.hexdigest()


def _int_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    return value


def _bool_value(manifest: Dict[str, Any], field: str) -> bool:
    value = manifest[field]
    if not isinstance(value, bool):
        raise Reject("manifest " + field + " must be a boolean")
    return value


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("manifest must be an object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise Reject("manifest missing fields: " + ",".join(missing))
    if extra:
        raise Reject("manifest has unknown fields: " + ",".join(extra))
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
            raise Reject("manifest " + field + " is not a lowercase SHA-256")
    for first, _ in CALLER_FILE_PAIRS:
        value = manifest[first]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + first + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + first + " must be absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    product = manifest["product"]
    if product != CALLER_PRODUCT:
        raise Reject("manifest product mismatch")
    release = manifest["release_version"]
    if not isinstance(release, str) or not RELEASE_PATTERN.fullmatch(release):
        raise Reject("manifest release_version must be semver-like digits")
    platform = manifest["platform"]
    if not isinstance(platform, str) or not PLATFORM_PATTERN.fullmatch(platform):
        raise Reject("manifest platform is invalid")
    entitlement_id = manifest["entitlement_id"]
    if not isinstance(entitlement_id, str) or not ENTITLEMENT_PATTERN.fullmatch(
            entitlement_id):
        raise Reject("manifest entitlement_id is invalid")
    if manifest["scope"] != CALLER_SCOPE:
        raise Reject("manifest scope must be " + CALLER_SCOPE)
    if not _bool_value(manifest, "entitlement_approved"):
        raise Reject("manifest entitlement is not approved")
    if not _bool_value(manifest, "telemetry_disclosure"):
        raise Reject("manifest telemetry disclosure is not present")
    if not _bool_value(manifest, "noise_cancellation_enabled"):
        raise Reject("manifest noise cancellation is not enabled")
    background_voice = _bool_value(
        manifest, "background_voice_cancellation_enabled")
    if not _bool_value(manifest, "other_features_disabled"):
        raise Reject("manifest other vendor features are not disabled")
    sample_rate = _int_value(manifest, "sample_rate_hz")
    if sample_rate not in ALLOWED_RATES_HZ:
        raise Reject("manifest sample_rate_hz is not an admitted rate")
    if _int_value(manifest, "channels") != CHANNELS:
        raise Reject("manifest channels mismatch")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise Reject("manifest " + field + " directory is missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise Reject("manifest " + path_field + " file is missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size
    models = ["noise_cancellation"]
    if background_voice:
        models.append("background_voice_cancellation")
    return {
        "accepted": True,
        "product": product,
        "release_version": release,
        "platform": platform,
        "scope": CALLER_SCOPE,
        "models": models,
        "sample_rate_hz": sample_rate,
        "channels": CHANNELS,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "vendor_sdk_imported": False,
        "vendor_runtime_executed": False,
        "model_executed": False,
    }


def build_control() -> Dict[str, Any]:
    noisy = synthetic_noisy_pcm()
    clean = synthetic_clean_pcm()
    identity = identity_control(noisy)
    scaled = scaled_control(noisy)
    noisy_summary = pcm_summary(noisy, CONTROL_SAMPLE_RATE_HZ)
    identity_summary = pcm_summary(identity, CONTROL_SAMPLE_RATE_HZ)
    scaled_summary = pcm_summary(scaled, CONTROL_SAMPLE_RATE_HZ)
    identity_energy = energy_accounting(noisy, identity)
    scaled_energy = energy_accounting(noisy, scaled)
    frames = frame_accounting(len(noisy), len(identity))
    adverse = run_adverse_controls()
    positive = validate_caller_manifest(_existing_file_manifest())
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "vendor_runtime_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "krisp_geometry_status": TASK_GEOMETRY_STATUS,
            "krisp_geometry_asserted": False,
            "task_scope": TASK_SCOPE,
            "vendor_runtime_character": REPORTED_RUNTIME_CHARACTER,
            "mode": "frame_causal_contract_control",
            "incremental_streaming_supported": True,
        },
        "noisy_pcm": noisy_summary,
        "clean_pcm": pcm_summary(clean, CONTROL_SAMPLE_RATE_HZ),
        "identity_output_pcm": identity_summary,
        "scaled_output_pcm": scaled_summary,
        "identity_energy": identity_energy,
        "scaled_energy": scaled_energy,
        "frames": frames,
        "accepted_control": {
            "id": "synthetic_structure_only_licensed_manifest",
            "accepted": positive["accepted"],
            "product": positive["product"],
            "release_version": positive["release_version"],
            "platform": positive["platform"],
            "scope": positive["scope"],
            "models": positive["models"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "vendor_sdk_imported": positive["vendor_sdk_imported"],
            "vendor_runtime_executed": positive["vendor_runtime_executed"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a Krisp deployment, "
                "and it cannot qualify the candidate."),
        },
        "acceptance_outcomes": [
            {"id": "identity_noisy_control", "measured": False,
             "value": None, "reason": "synthetic passthrough control only"},
            {"id": "task_matched_baseline", "measured": False,
             "value": None, "reason": "no established local baseline run"},
            {"id": "paired_si_sdr_and_stoi", "measured": False,
             "value": None, "reason": "no licensed output or permitted clean set"},
            {"id": "clean_speech_preservation", "measured": False,
             "value": None, "reason": "no real candidate output"},
            {"id": "peaks_and_invalid_outputs", "measured": False,
             "value": None, "reason": "synthetic validity accounting only"},
            {"id": "unpaired_screen_or_listening", "measured": False,
             "value": None, "reason": "no predictive screen or listening panel"},
            {"id": "alignment_state_memory", "measured": False,
             "value": None, "reason": "no vendor runtime or device clock"},
            {"id": "content_availability_timing", "measured": False,
             "value": None, "reason": "no paced vendor runtime measurement"},
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "json_nonfinite",
                "manifest_rate_nan"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo", "manifest_wrong_product",
                "manifest_bad_release_version", "manifest_empty_platform",
                "manifest_unsupported_rate", "manifest_rate_bool",
                "manifest_channels_float", "manifest_bvc_not_bool",
                "manifest_empty_entitlement_id", "manifest_scope_mismatch"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic noisy/identity/scaled PCM accounting only at the public "
            "v0 geometry. It is not Krisp output, not denoised or background-"
            "voice-cancelled audio, not a quality, latency or timing result "
            "and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report and contract model.
# ---------------------------------------------------------------------------

def _qualification_block(gates: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "reason": (
            "The Krisp commercial entitlement, exact release/platform build, "
            "model bundles, locked runtime, reviewed terms, isolated "
            "configuration, rights-cleared cohort, vendor output and separated "
            "enhancement results are absent. No licence, artifact, runtime, "
            "data or score was acquired, so nothing qualifies."),
    }


def _gates() -> List[Dict[str, str]]:
    return [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]


def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["sdk_present"]
        and observed["model_bundle_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["license_record_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["vendor_output_present"]
        and observed["results_present"])
    if complete:
        result = "asset_set_complete_pending_qualification"
    elif observed["sdk_present"]:
        result = "sdk_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "vendor": observed["vendor"],
        "product": observed["product"],
        "sdk_present": observed["sdk_present"],
        "model_bundle_present": observed["model_bundle_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "license_record_present": observed["license_record_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "vendor_output_present": observed["vendor_output_present"],
        "results_present": observed["results_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No Krisp SDK, model bundle, entitlement, runtime, licence, rights "
            "record, cohort, vendor output or result was observed. Textual "
            "mentions in survey documents are not artifacts."),
    }


def _peer_evidence() -> List[Dict[str, Any]]:
    return [
        {
            "component": "hecttor-commercial-ecosystem-products",
            "task": "SDK-HECTTOR-COMMERCIAL-ECOSYSTEM-PRODUCTS",
            "decision": "DEFER",
            "path": "docs/task-evidence/hecttor-commercial-ecosystem-products/"
                    "report.json",
            "class": "separate_commercial_vendor_component",
            "inherited_metrics": False,
            "boundary": (
                "A different proprietary vendor and model. Its manifest shape, "
                "absence inventory and admission controls are not Krisp "
                "access, runtime, output or rights evidence."),
        },
        {
            "component": "hume-octave",
            "task": "SDK-HUME-OCTAVE",
            "decision": "DEFER",
            "path": "docs/task-evidence/hume-octave/report.json",
            "class": "separate_commercial_vendor_component",
            "inherited_metrics": False,
            "boundary": (
                "A different proprietary vendor and model. No Krisp product "
                "identity, entitlement, score or term is inherited."),
        },
        {
            "component": "ai-coustics-quail",
            "task": "SDK-AI-COUSTICS-QUAIL",
            "decision": "DEFER",
            "path": "docs/task-evidence/ai-coustics-quail/report.json",
            "class": "separate_commercial_vendor_component",
            "inherited_metrics": False,
            "boundary": (
                "A different commercial SDK. Its fallback disclosure and "
                "controls do not establish Krisp access or output."),
        },
    ]


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = _gates()
    qualification = _qualification_block(gates)
    profile_row = _profile_row()
    if not profile_row["all_phrases_present"]:
        raise Reject("enhancement profile row is missing required phrases")
    profile_items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in ENHANCEMENT_REQUIREMENTS
    ]
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": qualification,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "vendor_identity": {
            "vendor": VENDOR,
            "product": PRODUCT,
            "record_name": PRODUCT_RECORD_NAME,
            "documentation_locator": VENDOR_DOCUMENTATION_LOCATOR,
            "release_version": None,
            "abi_version": None,
            "artifact_sha256": None,
            "runtime_character": REPORTED_RUNTIME_CHARACTER,
            "streaming_reported": REPORTED_STREAMING,
            "model_families_reported": list(PRODUCT_REPORTED_FAMILIES),
            "model_families_verified": [],
            "entitlement_approved": False,
            "runtime_present": LOCAL_RUNTIME_PRESENT,
            "terms_reviewed": False,
            "telemetry_terms_reviewed": False,
            "deployment_terms_reviewed": False,
            "vendor_output_present": False,
            "vendor_output_scored": False,
            "vendor_claim_verified": False,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "enhancement_profile": {
            "name": PROFILE,
            "source": profile_row["path"],
            "source_sha256": profile_row["sha256"],
            "source_check": profile_row,
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural accounting passes, but no licensed runtime, "
                "rights-cleared cohort, clean reference, control, baseline, "
                "vendor output or score exists, so the enhancement profile is "
                "not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "identity_noisy_control_present": True,
            "frame_mapping_declared": True,
            "scope_mismatch_rejected": True,
            "validator_accepts_well_formed_manifest": True,
            "vendor_output_absent": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "rights_gap": [
            {
                "id": "RG-A",
                "item": "vendor_terms",
                "requirement": (
                    "Reviewed Krisp product terms for the exact release and "
                    "platform build."),
                "status": "unverified",
            },
            {
                "id": "RG-B",
                "item": "evaluation_license",
                "requirement": (
                    "Approved evaluation or commercial licence with scope, "
                    "duration, seats, permitted use and key reference."),
                "status": "unresolved",
            },
            {
                "id": "RG-C",
                "item": "telemetry_and_data_handling",
                "requirement": (
                    "Documented telemetry, data handling, retention and "
                    "offline-operation terms for the exact SDK."),
                "status": "unresolved",
            },
            {
                "id": "RG-D",
                "item": "deployment_and_redistribution",
                "requirement": (
                    "Permitted deployment, redistribution, attribution and "
                    "bundled-model terms."),
                "status": "unresolved",
            },
            {
                "id": "RG-E",
                "item": "processed_data_output_use",
                "requirement": (
                    "Rights-cleared input audio, permitted vendor processing, "
                    "output retention and score publication."),
                "status": "unresolved",
            },
        ],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "asset_registry": audit["observed"]["asset_register"],
        "peer_evidence": _peer_evidence(),
        "merged_sibling_krisp_packages": [],
        "merged_sibling_krisp_note": (
            "This branch contains no merged evidence package for any other "
            "Krisp task; the three sibling Krisp rows and the Krisp Voice "
            "Isolation benchmark are separate and not inherited."),
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SDK_PATH,
            MISSING_MODEL_BUNDLE_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
            VENDOR_OUTPUT_PATH,
            RESULTS_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no vendor SDK, model or audio "
            "runtime is imported.",
            "A fixed probe list is checked for SDK, model, runtime, rights, "
            "cohort and result presence; no recursive walk is performed.",
            "The pinned local asset register is parsed strictly and contains "
            "no Krisp entry.",
            "No source checkout, platform binary or model byte is read, and no "
            "network request, download, audio device, model load or timing run "
            "occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
            "interpreter": REQUIRED_INTERPRETER,
        },
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "standard_library_only": True,
            "network_required": False,
            "runtime_required": False,
            "cold_start_repeats": 3,
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                "test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            ],
        },
    }


def build_contract() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    gates = _gates()
    qualification = _qualification_block(gates)
    return {
        SPDX_COPYRIGHT_KEY: "2026 Tsakanyan Hovhannes",
        SPDX_LICENSE_KEY: "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": (
            f"audio-sdk/{SLUG}-readiness/0.1"),
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": qualification,
        "qualification_status": QUALIFICATION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": identity,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "vendor_identity": {
            "vendor": VENDOR,
            "product": PRODUCT,
            "record_name": PRODUCT_RECORD_NAME,
            "documentation_locator": VENDOR_DOCUMENTATION_LOCATOR,
            "release_version": None,
            "abi_version": None,
            "artifact_sha256": None,
            "runtime_character": REPORTED_RUNTIME_CHARACTER,
            "streaming_reported": REPORTED_STREAMING,
            "model_families_reported": list(PRODUCT_REPORTED_FAMILIES),
            "model_families_verified": [],
            "entitlement_approved": False,
            "runtime_present": LOCAL_RUNTIME_PRESENT,
        },
        "sdk_presence": {
            "path": MISSING_SDK_PATH,
            "present": audit["sdk_present"],
            "model_bundle_present": audit["model_bundle_present"],
            "runtime_env_present": audit["runtime_env_present"],
            "runtime_lock_present": audit["runtime_lock_present"],
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": gates,
        "enhancement_profile_requirements": [
            {"id": item, "requirement": requirement, "status": status}
            for item, requirement, status in ENHANCEMENT_REQUIREMENTS
        ],
        "missing_historical_artifacts": [
            MISSING_SDK_PATH,
            MISSING_MODEL_BUNDLE_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
            VENDOR_OUTPUT_PATH,
            RESULTS_PATH,
        ],
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "standard_library_only": True,
            "regenerate": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                "test_reference.py"),
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar and source manifest "
                "only; no tolerance"),
        },
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "source_asset_license": (
                "unverified; no vendor SDK, licence text, terms statement or "
                "model bundle is present or recorded"),
        },
    }
