# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the Loudness.ai blocker.

The merged research census describes the ``Loudness.ai AI Noise Remover SDK``
as a local CPU inference SDK with adjustable denoise-only operation and Python
and JavaScript implementations whose official repository is reported MIT, while
bundled speech-engine assets and component/model licences remain separate and
must be read in distribution notices.

No exact SDK source snapshot, licensed runtime, bundled speech-engine asset,
component licence, vendor API/ABI document, rights-cleared speech cohort,
clean-reference set, task-matched baseline, comparison manifest, parity vector
or measured result exists anywhere in this workspace.  This package therefore
does not download, reconstruct, mirror or substitute any of them.

The module provides four verifiable pieces only:

* a fixed-path, fail-closed absence audit for the runtime, source snapshot,
  speech-engine assets, component licences, entitlement, documentation,
  cohort, references, baseline, scorer lock, rights, manifest and parity data;
* a caller-supplied-artifact manifest contract validated without importing,
  linking or executing the vendor SDK, and without reading a model weight;
* a deterministic synthetic identity/noisy-control PCM and exact integer
  frame/duration accounting fixture at the public v0 boundary, labelled as a
  control rather than a denoiser output;
* canonical report/contract builders whose bytes must regenerate identically
  from three cold starts.

Nothing here qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-LOUDNESS-AI-AI-NOISE-REMOVER-SDK"
TITLE = "Loudness.ai AI Noise Remover SDK"
SLUG = "loudness-ai-ai-noise-remover-sdk"
COMPONENT = "loudness-ai-ai-noise-remover-sdk"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "b4960fdba1991a35c07ff7f22cda5257c4749768"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-LOUDNESS-AI-AI-NOISE-REMOVER-SDK"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-LOUDNESS-AI-AI-NOISE-REMOVER-SDK")
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Source-reported product identity.  The census publishes no version, release
# id, artifact digest, runtime geometry, corpus or numeric result.
UPSTREAM_NAME = "Loudness.ai AI Noise Remover SDK"
UPSTREAM_VENDOR = "Loudness.ai"
UPSTREAM_RECORD_NAME = "Loudness.ai AI Noise Remover SDK"
UPSTREAM_REFERENCE = "research/noise_suppression_candidate_census.md:79"
REPORTED_IMPLEMENTATION_LANGUAGES = ("python", "javascript")
REPORTED_SOURCE_LICENSE = (
    "MIT (SDK repository, source-reported; no local copy or licence text is "
    "present and no digest is verifiable)")
REPORTED_COMPONENT_ASSET_TERMS = (
    "bundled speech-engine assets and component/model licences are separate "
    "from the SDK repository and must be read in distribution notices; no "
    "component licence or notice is present")
VENDOR_RUNTIME_VERSION = None
VENDOR_RUNTIME_PIN_AVAILABLE = False
VENDOR_RUNTIME_PRESENT = False
VENDOR_SOURCE_CHECKOUT_AVAILABLE = False
VENDOR_RUNTIME_GEOMETRY_STATUS = "unestablished"
VENDOR_RUNTIME_GEOMETRY_ASSERTED = False
DENOISE_ONLY_SCOPE_RECORDED = True
COMPONENT_ASSET_LICENSE_STATUS = "absent_unverified"

# Public SDK v0 boundary.  This is the local control geometry, not a claim
# about the vendor runtime ABI.
CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
CONTROL_SAMPLE_FORMAT = "f32"

# Fixed workspace paths used by the audit.  Absence is recorded, never filled.
MISSING_RUNTIME_PATH = "data/runtime/loudness-ai-ai-noise-remover-sdk"
MISSING_SOURCE_PATH = "data/checkouts/loudness-ai-ai-noise-remover-sdk"
MISSING_MODEL_PATH = "data/models/loudness-ai-ai-noise-remover-sdk"
MISSING_MODEL_ASSETS_PATH = "data/models/loudness-ai-ai-noise-remover-sdk/assets"
MISSING_COMPONENT_LICENSES_PATH = (
    "data/rights/loudness-ai-ai-noise-remover-sdk-component-licenses")
MISSING_LICENSE_PATH = "data/rights/loudness-ai-ai-noise-remover-sdk-license.json"
MISSING_DOCUMENTATION_PATH = (
    "data/docs/loudness-ai-ai-noise-remover-sdk-api.md")
MISSING_ENV_PATH = "data/envs/loudness-ai-ai-noise-remover-sdk"
MISSING_ENV_LOCK_PATH = (
    "data/envs/loudness-ai-ai-noise-remover-sdk/requirements.lock")
MISSING_COHORT_PATH = "data/corpus/noise-suppression-benchmark"
MISSING_CLEAN_REFERENCE_PATH = "data/corpus/noise-suppression-clean-references"
MISSING_BASELINE_PATH = (
    "data/runs/loudness-ai-ai-noise-remover-sdk/baseline.json")
MISSING_SCORER_LOCK_PATH = "data/envs/noise-suppression-scorer/requirements.lock"
MISSING_OUTPUTS_PATH = "data/runs/loudness-ai-ai-noise-remover-sdk/processed"
MISSING_COMPARISON_PATH = (
    "data/runs/loudness-ai-ai-noise-remover-sdk/manifest.json")
MISSING_PARITY_PATH = "data/runs/loudness-ai-ai-noise-remover-sdk/parity.json"
MISSING_RIGHTS_PATH = "data/rights/loudness-ai-ai-noise-remover-sdk-rights.json"

ABSENCE_PROBES: Tuple[str, ...] = (
    "data/runtime/loudness-ai-ai-noise-remover-sdk",
    "data/runtime/loudness-ai",
    "data/runtime/loudness",
    "data/runtime/Loudness",
    "data/checkouts/loudness-ai-ai-noise-remover-sdk",
    "data/checkouts/loudness-ai",
    "data/checkouts/loudness",
    "data/checkouts/Loudness",
    "data/models/loudness-ai-ai-noise-remover-sdk",
    "data/models/loudness-ai",
    "data/models/loudness",
    "data/weights/loudness",
    "data/envs/loudness-ai-ai-noise-remover-sdk",
    "data/envs/loudness-ai-ai-noise-remover-sdk/requirements.lock",
    "data/envs/loudness",
    "data/corpus/noise-suppression-benchmark",
    "data/corpus/noise-suppression-clean-references",
    "data/runs/loudness-ai-ai-noise-remover-sdk",
    "data/runs/loudness-ai-ai-noise-remover-sdk/processed",
    "data/runs/loudness-ai-ai-noise-remover-sdk/manifest.json",
    "data/runs/loudness-ai-ai-noise-remover-sdk/parity.json",
    "data/rights/loudness-ai-ai-noise-remover-sdk-license.json",
    "data/rights/loudness-ai-ai-noise-remover-sdk-rights.json",
    "data/rights/loudness-ai-ai-noise-remover-sdk-component-licenses",
    "research/loudness-ai-ai-noise-remover-sdk/runtime",
    "research/loudness-ai-ai-noise-remover-sdk/outputs",
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
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
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
}
LOCAL_PIN_PATHS = (
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
    "sdk_v0_sample_format": CONTROL_SAMPLE_FORMAT,
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
    "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
    "vendor_denoise_only_scope_recorded": DENOISE_ONLY_SCOPE_RECORDED,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_implemented": False,
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
    "vendor_outputs_bundled": False,
    "vendor_runtime_linked": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_vendor_outputs": False,
    "real_vendor_runtime": False,
    "release_claim": False,
    "runtime_invoked": False,
    "scorer_executed": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No Loudness.ai SDK, vendor runtime, model asset, component binary or "
    "vendor output is loaded, linked, imported or executed.",
    "No NumPy, SciPy, PyTorch, ONNX Runtime, SoundFile, librosa or vendor SDK "
    "module is imported.",
    "No network request, download, staging, mirror or asset redistribution "
    "occurs.",
    "No real audio, corpus, transcript, clean reference, listening panel, "
    "speaker reference or consent record is consumed.",
    "No SI-SDR, STOI, PESQ, DNSMOS, WER, latency, memory, RTF or device timing "
    "value is measured or claimed here.",
    "The census description and terms caveat are source-reported provenance, "
    "not reproduced evidence.",
    "The synthetic identity control is a pass-through accounting fixture; it "
    "is not a denoiser output, a vendor output or an enhancement result.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "vendor_sdk_source_snapshot",
        "kind": "exact_loudness_ai_sdk_source_snapshot",
        "reported_license": REPORTED_SOURCE_LICENSE,
        "recorded_reference": UPSTREAM_REFERENCE,
        "revision": None,
        "archive_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "vendor_runtime",
        "kind": "exact_licensed_or_approved_runtime_installation",
        "path": MISSING_RUNTIME_PATH,
        "version": None,
        "build_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "speech_engine_assets",
        "kind": "bundled_speech_engine_weights_and_runtime_assets",
        "path": MISSING_MODEL_ASSETS_PATH,
        "per_file_manifest": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "component_asset_licenses",
        "kind": "component_and_model_licenses_notices_and_provenance",
        "path": MISSING_COMPONENT_LICENSES_PATH,
        "terms_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "vendor_license_entitlement",
        "kind": "signed_entitlement_and_vendor_terms",
        "terms_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "vendor_sdk_documentation",
        "kind": "python_and_javascript_api_abi_denoise_only_and_drain_contract",
        "path": MISSING_DOCUMENTATION_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "denoise_only_configuration",
        "kind": "frozen_configuration_excluding_normalization_and_voice_processing",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_cleared_speech_cohort",
        "kind": "permitted_paired_speech_and_noise_cohort_with_consent",
        "path": MISSING_COHORT_PATH,
        "per_file_manifest": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "clean_reference_manifest",
        "kind": "matched_clean_reference_set_for_paired_metrics",
        "path": MISSING_CLEAN_REFERENCE_PATH,
        "per_file_manifest": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "task_matched_baseline",
        "kind": "identity_and_established_denoiser_baseline_manifest",
        "path": MISSING_BASELINE_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "metric_scorer_lock",
        "kind": "hash_pinned_si_sdr_stoi_and_supporting_scorer_environment",
        "path": MISSING_SCORER_LOCK_PATH,
        "lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "comparison_manifest",
        "kind": "frozen_cohort_windowing_failed_item_and_aggregation_manifest",
        "path": MISSING_COMPARISON_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "parity_vector",
        "kind": "approved_exact_runtime_reference_output_and_interval_vector",
        "path": MISSING_PARITY_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_output_use_record",
        "kind": "approved_scoring_publication_and_redistribution_scope",
        "path": MISSING_RIGHTS_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_report",
        "kind": "pinned_source_reported_candidate_census_record",
        "path": "research/noise_suppression_candidate_census.md",
        "line": 79,
        "sha256": SOURCE_PINS["research/noise_suppression_candidate_census.md"],
        "required": True,
        "status": "present_source_report_only",
    },
)

CALLER_SCALAR_FIELDS = (
    "channels",
    "platform",
    "processing_stage_scope",
    "sample_format",
    "sample_rate_hz",
    "scope",
    "variant",
    "vendor_entitlement_id",
    "vendor_runtime_version",
)
CALLER_FILE_PAIRS = (
    ("vendor_runtime_lock_path", "vendor_runtime_lock_sha256"),
    ("vendor_license_path", "vendor_license_sha256"),
    ("model_assets_manifest_path", "model_assets_manifest_sha256"),
    ("config_path", "config_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("clean_reference_manifest_path", "clean_reference_manifest_sha256"),
    ("scorer_lock_path", "scorer_lock_sha256"),
    ("baseline_manifest_path", "baseline_manifest_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
)
CALLER_DIR_FIELDS = ("vendor_runtime_path", "model_assets_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_ASSET_FIELDS = tuple(sorted(
    CALLER_SCALAR_FIELDS
    + CALLER_DIR_FIELDS
    + tuple(
        field for pair in CALLER_FILE_PAIRS for field in pair)))
CALLER_SCOPE = "denoise_only_offline_comparison"
CALLER_VARIANT = "offline_whole_utterance"
CALLER_STAGE_SCOPE = "denoise_only"
REQUIRED_SAMPLE_RATE_HZ = CONTROL_SAMPLE_RATE_HZ
REQUIRED_SAMPLE_FORMAT = CONTROL_SAMPLE_FORMAT
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
VERSION_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
ENTITLEMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
PLATFORM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-artifact/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_version_entitlement_platform_geometry_"
        "stage_scope_and_offline_variant_only; never import_link_or_execute_"
        "the_vendor_sdk_or_model_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_scope": CALLER_SCOPE,
    "required_variant": CALLER_VARIANT,
    "required_stage_scope": CALLER_STAGE_SCOPE,
    "required_vendor_runtime_version": VENDOR_RUNTIME_VERSION,
    "runtime_version_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "sample_format": REQUIRED_SAMPLE_FORMAT,
        "status": "declared_by_caller_not_vendor_abi_verified",
    },
    "notes": (
        "Every SDK snapshot, runtime file, speech-engine asset manifest, "
        "component licence, entitlement, configuration, cohort, clean "
        "reference, baseline, scorer lock, rights record and parity vector "
        "must exist at an absolute path and match its declared SHA-256 before "
        "a caller may run a denoise-only comparison. Normalization, loudness "
        "control, voice processing and streaming scopes are rejected here. No "
        "vendor version is pinned because no exact runtime or release id is "
        "recorded."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "vendor_source_snapshot_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact Loudness.ai AI Noise Remover SDK source "
            "snapshot (immutable revision or archive), its reported MIT "
            "licence text and a per-file SHA-256 manifest. The merged census "
            "names the product and reported licence only; no checkout exists."),
    },
    {
        "id": "vendor_runtime_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact approved runtime installation with version, "
            "build identity, supported platform set and per-file SHA-256 "
            "manifest. No runtime binary or package is present."),
    },
    {
        "id": "speech_engine_assets_absent",
        "state": "absent",
        "requirement": (
            "Supply the bundled speech-engine weights and runtime assets with "
            "byte counts, per-file hashes and their own component licences. "
            "No weight, graph or binary asset is present or downloaded."),
    },
    {
        "id": "component_licenses_and_notices_absent",
        "state": "absent",
        "requirement": (
            "Clear every bundled component and model licence, notice, "
            "attribution and redistribution term separately from the reported "
            "MIT SDK repository; no licence or notice is present."),
    },
    {
        "id": "entitlement_and_terms_unverified",
        "state": "absent",
        "requirement": (
            "Record the exact entitlement, product-use terms, output "
            "retention, scoring, publication and redistribution approval. No "
            "licence text, grant or entitlement exists."),
    },
    {
        "id": "vendor_api_and_abi_undocumented",
        "state": "absent",
        "requirement": (
            "Document the Python and JavaScript API surfaces, denoise-only "
            "invocation, supported rates/channels/frames, content delay, "
            "state, reset and drain behaviour before any adapter may be "
            "built."),
    },
    {
        "id": "denoise_only_stage_separation_unverified",
        "state": "absent",
        "requirement": (
            "Prove that normalization, loudness control and voice processing "
            "can be disabled and that the measured stage is denoise-only. The "
            "census says the operation is adjustable; it does not publish the "
            "configuration."),
    },
    {
        "id": "rights_cleared_cohort_absent",
        "state": "absent",
        "requirement": (
            "Supply a rights-cleared paired speech/noise cohort with consent, "
            "source intervals, matched clean references and a frozen per-file "
            "manifest. No real audio is present."),
    },
    {
        "id": "task_matched_baseline_and_metrics_absent",
        "state": "absent",
        "requirement": (
            "Run the identity/noisy control, an established task-matched "
            "denoiser baseline, paired SI-SDR and STOI where clean references "
            "are permitted, plus clean-speech preservation, peak and invalid "
            "output checks under a pinned scorer lock."),
    },
    {
        "id": "alignment_state_and_timing_unmeasured",
        "state": "absent",
        "requirement": (
            "Measure alignment, state, memory, content delay and availability "
            "timing for the exact runtime and host. No runtime invocation or "
            "device clock is available."),
    },
    {
        "id": "comparison_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Freeze the comparison manifest, failed-item policy and "
            "aggregation, then supply one approved exact-runtime parity "
            "vector. No manifest or parity result exists."),
    },
    {
        "id": "release_and_public_claim_unapproved",
        "state": "absent",
        "requirement": (
            "Complete opt-in provider intake, independent review, resource "
            "and deadline evidence, and explicit default/release approval. "
            "This package is off by default and makes no release claim."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "vendor_runtime_and_license_identity",
        "The exact SDK source snapshot, runtime version/build, reported MIT "
        "licence text and per-file SHA-256 manifest match pins.",
    ),
    (
        "runtime_and_component_asset_admission",
        "An isolated, hash-pinned runtime and every bundled speech-engine "
        "asset are admitted with component licences and notices on a recorded "
        "platform.",
    ),
    (
        "denoise_only_scope_and_stage_separation",
        "Denoise-only operation is proven, and normalization, loudness control "
        "and voice processing are disabled and accounted separately.",
    ),
    (
        "artifact_cohort_and_output_rights",
        "Cohort, clean-reference, consent, scoring, publication and "
        "redistribution rights are cleared with complete notices.",
    ),
    (
        "exact_reference_parity",
        "One approved runtime output matches the frozen parity vector for one "
        "exact denoise-only configuration.",
    ),
    (
        "enhancement_metrics_and_clean_reference_reproduction",
        "The pinned scorer reproduces paired SI-SDR and STOI, identity/noisy "
        "control and a task-matched baseline on the frozen cohort with "
        "recorded failures.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in adapter intake, licence review, descriptor review and "
        "an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by "
        "default.",
    ),
)

ENHANCEMENT_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "identity_or_noisy_control",
        "Run identity/noisy control and an established task-matched baseline.",
        "structural_only",
    ),
    (
        "paired_si_sdr_and_stoi",
        "Score paired SI-SDR and STOI where permitted clean references exist.",
        "not_measured",
    ),
    (
        "clean_speech_preservation",
        "Measure clean-speech preservation separately from noise attenuation.",
        "not_measured",
    ),
    (
        "peaks_and_invalid_outputs",
        "Measure output peaks, invalid intervals and nonfinite failures.",
        "structural_only",
    ),
    (
        "unpaired_predictive_or_listening",
        "For unpaired speech use a separately labelled predictive screen or "
        "authorized listening.",
        "absent",
    ),
    (
        "alignment_state_memory",
        "Report alignment, state and memory for the exact runtime.",
        "not_measured",
    ),
    (
        "content_and_availability_timing",
        "Report measured content and availability timing for the exact "
        "runtime and host.",
        "not_measured",
    ),
    (
        "scope_separation_and_disclosure",
        "Keep local runtime, source-reported claims and any vendor output "
        "distinct and disclose every fallback.",
        "declared_not_verified",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_reproduced_here",
    "source": "research/noise_suppression_candidate_census.md",
    "source_sha256": SOURCE_PINS[
        "research/noise_suppression_candidate_census.md"],
    "source_line": 79,
    "record_name": UPSTREAM_RECORD_NAME,
    "vendor": UPSTREAM_VENDOR,
    "reported_role": (
        "Local CPU inference SDK with adjustable denoise-only operation; "
        "Python and JavaScript implementations."),
    "reported_terms_caveat": (
        "Official MIT SDK repo bundles pinned speech-engine assets; "
        "component/model licenses and provenance remain separate and must be "
        "read in distribution notices."),
    "reported_implementation_languages": list(
        REPORTED_IMPLEMENTATION_LANGUAGES),
    "reported_denoise_only_operable": True,
    "reported_source_license": REPORTED_SOURCE_LICENSE,
    "reported_component_asset_terms": REPORTED_COMPONENT_ASSET_TERMS,
    "reported_numeric_results": [],
    "runtime_version": None,
    "release_id": None,
    "artifact_digest": None,
    "benchmark_url": None,
    "notes": (
        "The census publishes a product description, reported MIT status for "
        "the SDK repository and a caveat that bundled component/model terms "
        "remain separate. It publishes no version, release id, artifact "
        "digest, runtime geometry, corpus, score or timing value. None is "
        "asserted here."),
}

CONTROL_PLAN_PROVENANCE = (
    "synthetic_denoise_only_identity_and_pcm_accounting_control_not_denoiser"
    "_output")
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 3
CONTROL_FRAME_COUNT = CONTROL_SOURCE_SAMPLES // SDK_FRAME_SAMPLES
PCM_SAMPLE_CAP = 10_000_000

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
    "frame_short",
    "frame_long",
    "frame_nan",
    "frame_inf",
    "frames_empty",
    "json_nonfinite_nan",
    "json_nonfinite_inf",
    "json_duplicate_key",
    "json_not_object",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_bad_version",
    "manifest_wrong_scope",
    "manifest_wrong_variant",
    "manifest_wrong_stage_scope",
    "manifest_channels_stereo",
    "manifest_channels_bool",
    "manifest_rate_below_range",
    "manifest_rate_bool",
    "manifest_sample_format",
    "manifest_empty_entitlement",
    "manifest_bad_platform",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

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
# Fixed-path absence audit.  Local reads only; nothing is downloaded.
# ---------------------------------------------------------------------------

def _runtime_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_RUNTIME_PATH,
        SOURCE_ROOT / "data/runtime/loudness-ai",
        SOURCE_ROOT / "data/runtime/loudness",
        SOURCE_ROOT / "data/runtime/Loudness",
    ]


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_SOURCE_PATH,
        SOURCE_ROOT / "data/checkouts/loudness-ai",
        SOURCE_ROOT / "data/checkouts/loudness",
    ]


def _model_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_MODEL_PATH,
        SOURCE_ROOT / MISSING_MODEL_ASSETS_PATH,
        SOURCE_ROOT / "data/models/loudness-ai",
        SOURCE_ROOT / "data/models/loudness",
    ]


def _cohort_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_COHORT_PATH,
        SOURCE_ROOT / MISSING_CLEAN_REFERENCE_PATH,
    ]


def _license_candidates() -> List[str]:
    found: List[str] = []
    for relative in (MISSING_LICENSE_PATH, MISSING_RIGHTS_PATH,
                     MISSING_COMPONENT_LICENSES_PATH):
        if (SOURCE_ROOT / relative).exists():
            found.append(relative)
    return found


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def audit_assets() -> Dict[str, Any]:
    runtime_paths = _runtime_candidates()
    source_paths = _source_candidates()
    model_paths = _model_candidates()
    cohort_paths = _cohort_candidates()
    probes = probe_absence()
    licenses = _license_candidates()
    return {
        "vendor_runtime_path": MISSING_RUNTIME_PATH,
        "vendor_runtime_present": any(path.exists()
                                      for path in runtime_paths),
        "vendor_runtime_version": None,
        "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "vendor_runtime_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in runtime_paths
        ],
        "vendor_source_present": any(path.exists()
                                     for path in source_paths),
        "vendor_source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in source_paths
        ],
        "speech_engine_assets_present": any(path.exists()
                                           for path in model_paths),
        "speech_engine_asset_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in model_paths
        ],
        "vendor_license_files": licenses,
        "vendor_license_present": bool(licenses),
        "component_licenses_present": (
            SOURCE_ROOT / MISSING_COMPONENT_LICENSES_PATH).exists(),
        "documentation_present": (
            SOURCE_ROOT / MISSING_DOCUMENTATION_PATH).is_file(),
        "runtime_env_present": (SOURCE_ROOT / MISSING_ENV_PATH).is_dir(),
        "runtime_lock_present": (
            SOURCE_ROOT / MISSING_ENV_LOCK_PATH).is_file(),
        "cohort_present": any(path.exists() for path in cohort_paths),
        "cohort_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in cohort_paths
        ],
        "baseline_present": (SOURCE_ROOT / MISSING_BASELINE_PATH).is_file(),
        "scorer_lock_present": (
            SOURCE_ROOT / MISSING_SCORER_LOCK_PATH).is_file(),
        "processed_outputs_present": (
            SOURCE_ROOT / MISSING_OUTPUTS_PATH).exists(),
        "rights_record_present": (
            SOURCE_ROOT / MISSING_RIGHTS_PATH).is_file(),
        "comparison_manifest_present": (
            SOURCE_ROOT / MISSING_COMPARISON_PATH).is_file(),
        "parity_manifest_present": (
            SOURCE_ROOT / MISSING_PARITY_PATH).is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "denoise_only_scope_recorded": DENOISE_ONLY_SCOPE_RECORDED,
            "control_geometry": {
                "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
                "channels": CHANNELS,
                "sample_format": CONTROL_SAMPLE_FORMAT,
                "frame_samples": SDK_FRAME_SAMPLES,
            },
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "reported_reference": UPSTREAM_REFERENCE,
        },
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
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic identity control and exact accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_noisy_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x10AD5E55
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def identity_control_pcm() -> List[float]:
    """The identity/noisy control is an exact pass-through, not a denoiser."""
    return list(synthetic_noisy_pcm())


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


def validate_frame(frame: Any) -> List[float]:
    if not isinstance(frame, (list, tuple)):
        raise Reject("frame must be a sample sequence")
    if len(frame) != SDK_FRAME_SAMPLES:
        raise Reject("frame must contain exactly 160 samples")
    return validate_pcm(frame)


def split_frames(signal: Sequence[float]) -> List[List[float]]:
    values = validate_pcm(signal)
    if len(values) % SDK_FRAME_SAMPLES != 0:
        raise Reject("signal length is not a multiple of 160")
    return [
        values[index:index + SDK_FRAME_SAMPLES]
        for index in range(0, len(values), SDK_FRAME_SAMPLES)
    ]


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "sample_format": CONTROL_SAMPLE_FORMAT,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def duration_accounting(source_samples: int, output_samples: int
                        ) -> Dict[str, Any]:
    for value, label in ((source_samples, "source"),
                         (output_samples, "output")):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject(label + " sample count must be an integer")
        if value <= 0:
            raise Reject(label + " sample count must be positive")
    source_duration = Fraction(source_samples, CONTROL_SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, CONTROL_SAMPLE_RATE_HZ)
    ratio = output_duration / source_duration
    return {
        "source_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "duration_ratio_float": float(ratio),
        "duration_ratio_interpretation": (
            "output_duration_divided_by_source_duration"),
    }


def identity_accounting(source: Sequence[float], output: Sequence[float]
                        ) -> Dict[str, Any]:
    left = validate_pcm(source)
    right = validate_pcm(output)
    if len(left) != len(right):
        raise Reject("identity control lengths differ")
    delta = max(abs(a - b) for a, b in zip(left, right))
    if delta != 0.0:
        raise Reject("identity control is not exact")
    return {
        "identity_exact": True,
        "max_abs_difference": delta,
        "source_sha256": sha256(canonical_bytes(list(left))),
        "output_sha256": sha256(canonical_bytes(list(right))),
        "note": (
            "The identity control copies the noisy synthetic source. It is a "
            "control, not a denoiser, vendor output or enhancement result."),
    }


def alignment_accounting() -> Dict[str, Any]:
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "control_first_output_sample": 0,
        "control_first_output_delay_samples": 0,
        "control_tail_samples": 0,
        "vendor_runtime_alignment_measured": False,
        "vendor_content_delay_measured": False,
        "device_timing_measured": False,
        "note": (
            "No vendor runtime exists, so vendor alignment, content delay and "
            "device timing are not measured. The zero delay describes the "
            "synthetic identity control only."),
    }


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It exercises fail-closed shape checks only.  Validation reaches the
    missing-asset branch before any file is read.
    """

    root = "/nonexistent/loudness-ai-noise-remover-evidence-fixture"
    digest = "0" * 64
    manifest: Dict[str, Any] = {
        "channels": CHANNELS,
        "platform": "macos-arm64",
        "processing_stage_scope": CALLER_STAGE_SCOPE,
        "sample_format": REQUIRED_SAMPLE_FORMAT,
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "variant": CALLER_VARIANT,
        "vendor_entitlement_id": "loudness-entitlement-0001",
        "vendor_runtime_version": "1.0.0",
        "vendor_runtime_path": root + "/runtime",
        "model_assets_path": root + "/assets",
    }
    for path_field, sha_field in CALLER_FILE_PAIRS:
        manifest[path_field] = root + "/" + path_field.replace("_path", ".bin")
        manifest[sha_field] = digest
    return manifest


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises path, directory and SHA-256 validation without reading audio,
    importing a vendor SDK or loading a model.  Files may be reused; every
    digest is the real package-file digest so one corrupted value reaches the
    mismatch branch.
    """

    assignments = {
        "vendor_runtime_lock_path": HERE / "reference.py",
        "vendor_license_path": HERE / "README.md",
        "model_assets_manifest_path": HERE / "run.py",
        "config_path": HERE / "verify.py",
        "cohort_manifest_path": HERE / "test_reference.py",
        "clean_reference_manifest_path": HERE / "contract.json.license",
        "scorer_lock_path": HERE / "report.json.license",
        "baseline_manifest_path": HERE / "report.json.sha256.license",
        "rights_record_path": HERE / "SOURCES.sha256.license",
        "parity_vector_path": HERE / "README.md",
    }
    manifest: Dict[str, Any] = {
        "channels": CHANNELS,
        "platform": "macos-arm64",
        "processing_stage_scope": CALLER_STAGE_SCOPE,
        "sample_format": REQUIRED_SAMPLE_FORMAT,
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "variant": CALLER_VARIANT,
        "vendor_entitlement_id": "loudness-entitlement-0001",
        "vendor_runtime_version": "1.0.0",
        "vendor_runtime_path": str(HERE),
        "model_assets_path": str(HERE),
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(
            path.read_bytes())
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


def _integer_field(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
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
    for field in tuple(field for field, _ in CALLER_FILE_PAIRS) \
            + CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    version = manifest["vendor_runtime_version"]
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise Reject("manifest vendor_runtime_version is invalid")
    if VENDOR_RUNTIME_PIN_AVAILABLE is False and VENDOR_RUNTIME_VERSION is not None:
        raise Reject("inconsistent runtime version pin state")
    entitlement = manifest["vendor_entitlement_id"]
    if not isinstance(entitlement, str) or not ENTITLEMENT_PATTERN.fullmatch(
            entitlement):
        raise Reject("manifest vendor_entitlement_id is invalid")
    platform = manifest["platform"]
    if not isinstance(platform, str) or not PLATFORM_PATTERN.fullmatch(platform):
        raise Reject("manifest platform is invalid")
    channels = _integer_field(manifest, "channels")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    sample_rate = _integer_field(manifest, "sample_rate_hz")
    if sample_rate < MIN_SAMPLE_RATE_HZ or sample_rate > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz is outside the admitted range")
    if sample_rate != REQUIRED_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz is not the control rate")
    if manifest["sample_format"] != REQUIRED_SAMPLE_FORMAT:
        raise Reject("manifest sample_format must be " + REQUIRED_SAMPLE_FORMAT)
    if manifest["scope"] != CALLER_SCOPE:
        raise Reject("manifest scope must be " + CALLER_SCOPE)
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
    if manifest["processing_stage_scope"] != CALLER_STAGE_SCOPE:
        raise Reject("manifest processing_stage_scope must be "
                     + CALLER_STAGE_SCOPE)
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise Reject("manifest " + field + " directory is missing")
    total_bytes = 0
    checked_paths: List[str] = []
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise Reject("manifest " + path_field + " file is missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size
        checked_paths.append(path_field)
    return {
        "accepted": True,
        "accepted_for_qualification": False,
        "vendor_runtime_approved": False,
        "asset_license_approved": False,
        "runtime_version_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "vendor_runtime_version_declared": version,
        "scope": CALLER_SCOPE,
        "variant": CALLER_VARIANT,
        "stage_scope": CALLER_STAGE_SCOPE,
        "sample_rate_hz": sample_rate,
        "sample_format": REQUIRED_SAMPLE_FORMAT,
        "channels": CHANNELS,
        "platform": platform,
        "files_checked": len(checked_paths),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "vendor_runtime_imported": False,
        "scorer_executed": False,
        "qualification_effect": "none",
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_signal = synthetic_noisy_pcm()
    good_frame = good_signal[:SDK_FRAME_SAMPLES]
    good_manifest = _shape_only_manifest()
    existing = _existing_file_manifest()

    def case(case_id: str, action) -> Dict[str, str]:
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
        ("pcm_wrong_rate", lambda: validate_pcm(good_signal, 8000)),
        ("pcm_stereo", lambda: validate_pcm(
            good_signal, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("frame_short", lambda: validate_frame(good_frame[:159])),
        ("frame_long", lambda: validate_frame(good_frame + [0.0])),
        ("frame_nan", lambda: validate_frame([math.nan] * SDK_FRAME_SAMPLES)),
        ("frame_inf", lambda: validate_frame([math.inf] * SDK_FRAME_SAMPLES)),
        ("frames_empty", lambda: split_frames([])),
        ("json_nonfinite_nan", lambda: strict_loads('{"a":NaN}')),
        ("json_nonfinite_inf", lambda: strict_loads('{"a":Infinity}')),
        ("json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}')),
        ("json_not_object", lambda: strict_loads("[]")),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("config_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "config_path", "configs/loudness-denoise.json")),
        ("manifest_bad_sha", wrong("config_sha256", "ABC")),
        ("manifest_bad_version", wrong("vendor_runtime_version", "1.0")),
        ("manifest_wrong_scope", wrong(
            "scope", "denoise_plus_normalization")),
        ("manifest_wrong_variant", wrong(
            "variant", "incremental_streaming")),
        ("manifest_wrong_stage_scope", wrong(
            "processing_stage_scope", "denoise_and_loudness")),
        ("manifest_channels_stereo", wrong("channels", 2)),
        ("manifest_channels_bool", wrong("channels", True)),
        ("manifest_rate_below_range", wrong("sample_rate_hz", 4000)),
        ("manifest_rate_bool", wrong("sample_rate_hz", True)),
        ("manifest_sample_format", wrong("sample_format", "pcm16")),
        ("manifest_empty_entitlement", wrong("vendor_entitlement_id", "")),
        ("manifest_bad_platform", wrong("platform", "macOS ARM64")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, config_path=(
                "/nonexistent/loudness-fixtures/config.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, vendor_runtime_path=(
                "/nonexistent/loudness-fixtures/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, config_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case set mismatch")
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_noisy_pcm()
    output = identity_control_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output, CONTROL_SAMPLE_RATE_HZ)
    frames = split_frames(output)
    durations = duration_accounting(len(source), len(output))
    identity = identity_accounting(source, output)
    alignment = alignment_accounting()
    adverse = run_adverse_controls()
    positive = validate_caller_manifest(_existing_file_manifest())
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "scorer": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_sample_format": CONTROL_SAMPLE_FORMAT,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "control_frame_count": len(frames),
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
            "denoise_only_scope_recorded": DENOISE_ONLY_SCOPE_RECORDED,
        },
        "source_pcm": source_summary,
        "identity_output_pcm": output_summary,
        "duration": durations,
        "identity": identity,
        "alignment": alignment,
        "frame_accounting": {
            "frame_samples": SDK_FRAME_SAMPLES,
            "frame_count": len(frames),
            "total_samples": sum(len(frame) for frame in frames),
            "exact_partition": sum(len(frame) for frame in frames)
            == len(output),
            "all_frames_validated": True,
        },
        "accepted_control": {
            "id": "synthetic_structure_only_manifest",
            "accepted": positive["accepted"],
            "accepted_for_qualification": (
                positive["accepted_for_qualification"]),
            "vendor_runtime_approved": positive["vendor_runtime_approved"],
            "asset_license_approved": positive["asset_license_approved"],
            "scope": positive["scope"],
            "variant": positive["variant"],
            "stage_scope": positive["stage_scope"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "model_executed": positive["model_executed"],
            "vendor_runtime_imported": positive["vendor_runtime_imported"],
            "scorer_executed": positive["scorer_executed"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a vendor runtime, "
                "not a model asset set and not a denoiser output, and it "
                "cannot qualify the candidate."),
        },
        "acceptance_outcomes": [
            {
                "id": "identity_or_noisy_control",
                "measured": False,
                "value": None,
                "reason": (
                    "only a synthetic pass-through control exists; no real "
                    "noisy cohort"),
            },
            {
                "id": "task_matched_baseline",
                "measured": False,
                "value": None,
                "reason": "no baseline manifest, runtime or baseline output",
            },
            {
                "id": "paired_si_sdr",
                "measured": False,
                "value": None,
                "reason": (
                    "no clean references, scorer lock or runtime; not "
                    "computed"),
            },
            {
                "id": "paired_stoi",
                "measured": False,
                "value": None,
                "reason": (
                    "no clean references, scorer lock or runtime; not "
                    "computed"),
            },
            {
                "id": "clean_speech_preservation",
                "measured": False,
                "value": None,
                "reason": "no clean speech cohort or runtime",
            },
            {
                "id": "peaks_and_invalid_outputs",
                "measured": False,
                "value": None,
                "reason": (
                    "synthetic PCM validation only; no vendor output"),
            },
            {
                "id": "unpaired_predictive_or_listening",
                "measured": False,
                "value": None,
                "reason": "no predictive scorer or authorized listening",
            },
            {
                "id": "alignment_state_memory",
                "measured": False,
                "value": None,
                "reason": "no vendor runtime invocation",
            },
            {
                "id": "content_and_availability_timing",
                "measured": False,
                "value": None,
                "reason": "no vendor runtime invocation and no device clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "frame_nan",
                "frame_inf", "json_nonfinite_nan", "json_nonfinite_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo", "frame_short", "frame_long",
                "manifest_channels_stereo", "manifest_channels_bool",
                "manifest_rate_below_range", "manifest_rate_bool",
                "manifest_sample_format", "manifest_bad_version",
                "manifest_empty_entitlement", "manifest_bad_platform",
                "manifest_wrong_scope", "manifest_wrong_variant",
                "manifest_wrong_stage_scope"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "frames_empty", "manifest_missing_field",
                "manifest_missing_asset", "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic identity/noisy-control PCM and exact frame accounting "
            "at the public v0 boundary only. It is not a denoiser output, not "
            "a vendor output, not an SI-SDR/STOI result and cannot qualify "
            "the candidate."),
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
            "The exact Loudness.ai SDK source snapshot, runtime, bundled "
            "speech-engine assets, component licences, entitlement and API/ABI "
            "documentation are absent; no rights-cleared cohort, clean "
            "references, baseline, scorer lock, comparison manifest or parity "
            "vector exists, and no denoise-only output or metric was produced. "
            "The census description is source-reported only."),
    }


def _gates() -> List[Dict[str, str]]:
    return [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]


def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["vendor_source_present"]
        and observed["vendor_runtime_present"]
        and observed["speech_engine_assets_present"]
        and observed["component_licenses_present"]
        and observed["vendor_license_present"]
        and observed["documentation_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["cohort_present"]
        and observed["baseline_present"]
        and observed["scorer_lock_present"]
        and observed["rights_record_present"]
        and observed["comparison_manifest_present"]
        and observed["parity_manifest_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["vendor_runtime_present"]:
        result = "runtime_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "vendor_source_present": observed["vendor_source_present"],
        "vendor_runtime_present": observed["vendor_runtime_present"],
        "vendor_runtime_version": observed["vendor_runtime_version"],
        "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "speech_engine_assets_present": (
            observed["speech_engine_assets_present"]),
        "component_licenses_present": observed["component_licenses_present"],
        "vendor_license_present": observed["vendor_license_present"],
        "documentation_present": observed["documentation_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "cohort_present": observed["cohort_present"],
        "baseline_present": observed["baseline_present"],
        "scorer_lock_present": observed["scorer_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "comparison_manifest_present": observed["comparison_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No SDK source, runtime, speech-engine asset, component licence, "
            "entitlement, API document, environment, cohort, reference, "
            "baseline, scorer lock, rights record, comparison manifest or "
            "parity vector was observed. The census record is provenance only."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = _gates()
    qualification = _qualification_block(gates)
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
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "vendor": UPSTREAM_VENDOR,
            "record_name": UPSTREAM_RECORD_NAME,
            "recorded_reference": UPSTREAM_REFERENCE,
            "benchmark_url": None,
            "reported_implementation_languages": list(
                REPORTED_IMPLEMENTATION_LANGUAGES),
            "reported_denoise_only_operable": DENOISE_ONLY_SCOPE_RECORDED,
            "reported_source_license": REPORTED_SOURCE_LICENSE,
            "reported_component_asset_terms": REPORTED_COMPONENT_ASSET_TERMS,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
            "vendor_runtime_present": VENDOR_RUNTIME_PRESENT,
            "vendor_source_checkout_available": (
                VENDOR_SOURCE_CHECKOUT_AVAILABLE),
            "component_asset_license_status": COMPONENT_ASSET_LICENSE_STATUS,
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "enhancement_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_enhancement_metrics": None,
            "separation": {
                "identity_noisy_control": "synthetic_structural_only",
                "vendor_runtime": "absent",
                "vendor_output": "absent",
                "task_matched_baseline": "absent",
                "source_reported_claim": "product_description_only",
                "default_package_fallback": (
                    "no runtime, code, corpus, asset, reference, output, "
                    "scorer or claim is bundled or substituted"),
                "disclosure": (
                    "The only source description is labelled "
                    "source_reported_not_reproduced_here; no metric is shown."),
            },
            "note": (
                "The enhancement profile is not satisfied for qualification: "
                "no permitted cohort, clean references, exact runtime, "
                "baseline, scorer or measured comparison exists."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "denoise_only_scope_rejected_when_wrong": True,
            "stage_scope_mismatch_rejected": True,
            "validator_accepts_well_formed_manifest": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_RUNTIME_PATH,
            MISSING_SOURCE_PATH,
            MISSING_MODEL_PATH,
            MISSING_MODEL_ASSETS_PATH,
            MISSING_COMPONENT_LICENSES_PATH,
            MISSING_LICENSE_PATH,
            MISSING_DOCUMENTATION_PATH,
            MISSING_ENV_PATH,
            MISSING_ENV_LOCK_PATH,
            MISSING_COHORT_PATH,
            MISSING_CLEAN_REFERENCE_PATH,
            MISSING_BASELINE_PATH,
            MISSING_SCORER_LOCK_PATH,
            MISSING_OUTPUTS_PATH,
            MISSING_COMPARISON_PATH,
            MISSING_PARITY_PATH,
            MISSING_RIGHTS_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model, scorer, vendor SDK or "
            "audio runtime is imported.",
            "Fixed workspace paths are probed for source, runtime, assets, "
            "component licences, entitlement, documentation, cohort, "
            "references, baseline, scorer lock, rights, outputs and parity.",
            "No vendor library is linked, no asset byte is read and no audio "
            "is opened.",
            "No network request, download, audio device, model load or timing "
            "run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
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
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": qualification,
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
        "vendor_runtime": {
            "path": MISSING_RUNTIME_PATH,
            "present": audit["vendor_runtime_present"],
            "version": audit["vendor_runtime_version"],
            "version_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
            "source_checkout_present": audit["vendor_source_present"],
            "documentation_present": audit["documentation_present"],
            "geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
        },
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "vendor": UPSTREAM_VENDOR,
            "record_name": UPSTREAM_RECORD_NAME,
            "recorded_reference": UPSTREAM_REFERENCE,
            "reported_implementation_languages": list(
                REPORTED_IMPLEMENTATION_LANGUAGES),
            "reported_source_license": REPORTED_SOURCE_LICENSE,
            "reported_component_asset_terms": REPORTED_COMPONENT_ASSET_TERMS,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
            "vendor_source_checkout_available": (
                VENDOR_SOURCE_CHECKOUT_AVAILABLE),
            "component_asset_license_status": COMPONENT_ASSET_LICENSE_STATUS,
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
            MISSING_RUNTIME_PATH,
            MISSING_SOURCE_PATH,
            MISSING_MODEL_PATH,
            MISSING_MODEL_ASSETS_PATH,
            MISSING_COMPONENT_LICENSES_PATH,
            MISSING_LICENSE_PATH,
            MISSING_DOCUMENTATION_PATH,
            MISSING_ENV_PATH,
            MISSING_ENV_LOCK_PATH,
            MISSING_COHORT_PATH,
            MISSING_CLEAN_REFERENCE_PATH,
            MISSING_BASELINE_PATH,
            MISSING_SCORER_LOCK_PATH,
            MISSING_OUTPUTS_PATH,
            MISSING_COMPARISON_PATH,
            MISSING_PARITY_PATH,
            MISSING_RIGHTS_PATH,
        ],
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py all"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
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
                "unverified; no SDK source or runtime is present, the SDK "
                "repository is reported MIT by the census, and bundled "
                "speech-engine/component/model terms are absent"),
        },
    }
