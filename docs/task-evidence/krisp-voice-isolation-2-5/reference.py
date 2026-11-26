# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-KRISP-VOICE-ISOLATION-2-5.

Krisp Voice Isolation 2.5 is a closed commercial SDK. The exact licensed
runtime, vendor SDK documentation, entitlement, DNSMOS-C/NISQA scorer, CC
BY-NC 4.0 corpus and the 265 public vendor outputs are all absent from this
workspace. The merged research record
``research/cpp-library-krisp-benchmark-20261109.md`` records one historical
noncommercial run whose audio was kept under ``/private/tmp`` and was not added
to any repository.

This module therefore never imports a vendor SDK, PyTorch, torchaudio, NumPy,
SoundFile, librosa, DNSMOS or any scoring runtime, never loads or executes a
model, never reads or writes real audio, never downloads anything and never
measures a device clock. It provides three verifiable pieces:

* a fail-closed asset audit over fixed workspace paths that records the absent
  vendor runtime, licence entitlement, SDK terms, scorer checkpoint and
  runtime, corpus, processed outputs, rights approval and comparison manifest,
  and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract for an approved vendor-output
  scoring run, validated without importing or executing anything, with every
  malformed, missing, invalid or nonfinite control rejected;
* a deterministic synthetic scenario-balanced aggregation and PCM accounting
  control that mirrors the documented external comparison geometry without
  asserting any vendor runtime or scorer result.

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

TASK = "SDK-KRISP-VOICE-ISOLATION-2-5"
TITLE = "Krisp Voice Isolation 2.5"
SLUG = "krisp-voice-isolation-2-5"
COMPONENT = "krisp-voice-isolation-2-5"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "f006454da9a72fbfd394e2b5bd05105201a9cd29"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-KRISP-VOICE-ISOLATION-2-5"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-KRISP-VOICE-ISOLATION-2-5")
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "external"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact vendor and data identity recorded by the merged research evidence.
# No source revision exists because Krisp Voice Isolation 2.5 is closed.
UPSTREAM_NAME = "Krisp Voice Isolation 2.5"
UPSTREAM_VENDOR = "Krisp Technologies, Inc."
UPSTREAM_RECORD_NAME = "Krisp Voice Isolation 2.5 Default"
BENCHMARK_URL = "https://krisp.ai/benchmarks/voice-isolation-benchmark/"
VENDOR_RUNTIME_URL = "https://sdk-docs.krisp.ai/"
VENDOR_RUNTIME_VERSION: Optional[str] = None
VENDOR_RUNTIME_PIN_AVAILABLE = False
VENDOR_RUNTIME_PRESENT = False
VENDOR_RUNTIME_GEOMETRY_STATUS = "unestablished"
VENDOR_RUNTIME_GEOMETRY_ASSERTED = False
VENDOR_OUTPUT_SCOPING = "vendor_output_scoring_only"

# Recorded public dataset identities.  These are provenance facts, not local
# artifacts; no file was downloaded, vendored or hashed in this package.
CORPUS_REPOSITORY = "Krisp-AI/VoiceIsolation-Benchmark-Dataset"
CORPUS_REVISION = "626bac8ca07fb9b4846d4f62d27c321753160b36"
CORPUS_FILE_COUNT = 265
CORPUS_SAMPLE_RATE_HZ = 32000
CORPUS_SAMPLE_FORMAT = "pcm16"
CORPUS_LICENSE = "CC BY-NC 4.0"
PROCESSED_REPOSITORY = "Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed"
PROCESSED_REVISION = "8759715197e39e0356125e3f3197a9854c38fa60"
PROCESSED_SUBSET = "vi_2_5_default"
PROCESSED_FILE_COUNT = 265
PROCESSED_BYTES = 647960782
SCORER_NAME = "DNSMOS-C (official NISQA checkpoint)"
SCORER_CHECKPOINT = "runs/NISQA/model_best.pt"
SCORER_CHECKPOINT_SHA256: Optional[str] = None
SCORER_SOURCE = "https://github.com/Hope-Liang/DNSMOS-C"
WER_ENGINE_COUNT = 11
WER_TOOL = "jiwer 4.0.0 with NVIDIA NeMo WFST normalization"

# Control geometry is the public SDK v0 boundary, not vendor runtime geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160

# The research record documents 16 kHz mono PCM16 for the same-scorer
# comparison; it does not establish vendor runtime ABI or device timing.
COMPARISON_SAMPLE_RATE_HZ = 16000
COMPARISON_CHANNELS = 1
COMPARISON_SAMPLE_FORMAT = "pcm16"
COMPARISON_GEOMETRY_STATUS = "recorded_for_scoring_only"

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
MISSING_RUNTIME_PATH = "data/runtime/krisp-voice-isolation-2-5"
MISSING_LICENSE_PATH = "data/rights/krisp-voice-isolation-2-5-license.json"
MISSING_SCORER_PATH = "data/models/dnsmos-c/nisqa"
MISSING_SCORER_ENV_PATH = "data/envs/dnsmos-c"
MISSING_SCORER_LOCK_PATH = "data/envs/dnsmos-c/requirements.lock"
MISSING_CORPUS_PATH = "data/corpus/krisp-voice-isolation-benchmark"
MISSING_OUTPUTS_PATH = "data/runs/krisp-voice-isolation-2-5/processed"
MISSING_COMPARISON_PATH = "data/runs/krisp-voice-isolation-2-5/manifest.json"
MISSING_PARITY_PATH = "data/runs/krisp-voice-isolation-2-5/parity.json"
MISSING_RIGHTS_PATH = "data/rights/krisp-voice-isolation-2-5-rights.json"

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    "data/runtime/krisp-voice-isolation-2-5",
    "data/runtime/krisp",
    "data/runtime/Krisp",
    "data/checkouts/krisp-voice-isolation-2-5",
    "data/checkouts/Krisp",
    "data/checkouts/krisp",
    "data/models/krisp",
    "data/models/Krisp",
    "data/models/dnsmos-c",
    "data/models/dnsmos-c/nisqa",
    "data/models/nisqa",
    "data/weights/krisp",
    "data/envs/krisp",
    "data/envs/krisp/requirements.lock",
    "data/envs/dnsmos-c",
    "data/envs/dnsmos-c/requirements.lock",
    "data/corpus/krisp-voice-isolation-benchmark",
    "data/corpus/Krisp-AI/VoiceIsolation-Benchmark-Dataset",
    "data/runs/krisp-voice-isolation-2-5",
    "data/runs/krisp-voice-isolation-2-5/processed",
    "data/runs/krisp-voice-isolation-2-5/manifest.json",
    "data/runs/krisp-voice-isolation-2-5/parity.json",
    "data/rights/krisp-voice-isolation-2-5-license.json",
    "data/rights/krisp-voice-isolation-2-5-rights.json",
    "research/krisp-voice-isolation-2-5/runtime",
    "research/krisp-voice-isolation-2-5/outputs",
    "research/krisp-voice-isolation-2-5/scorer",
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
    "research/cpp-library-krisp-benchmark-20261109.md":
        "7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2",
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
    "comparison_sample_rate_hz": COMPARISON_SAMPLE_RATE_HZ,
    "comparison_channels": COMPARISON_CHANNELS,
    "comparison_sample_format": COMPARISON_SAMPLE_FORMAT,
    "comparison_geometry_status": COMPARISON_GEOMETRY_STATUS,
    "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
    "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
    "vendor_scope": VENDOR_OUTPUT_SCOPING,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
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
    "No Krisp Voice Isolation 2.5 runtime, SDK library, vendor model or "
    "vendor output is loaded, linked or executed.",
    "No PyTorch, torchaudio, NumPy, SoundFile, librosa, DNSMOS, NISQA or "
    "vendor SDK module is imported.",
    "No network request, download, staging, mirror or asset redistribution "
    "occurs.",
    "No real audio, corpus, transcript, listening panel, speaker reference "
    "or consent record is consumed.",
    "No DNSMOS-C, DNSMOS, WER, STOI, SI-SDR, latency, memory, RTF or device "
    "timing value is measured here.",
    "The source-reported vendor and research-record numbers are labelled and "
    "are not reproduced, verified or claimed as this package's results.",
    "The synthetic scoring aggregation is a contract fixture only; it is not "
    "DNSMOS-C, not a vendor score and not audio.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "vendor_runtime",
        "kind": "licensed_krisp_voice_isolation_2_5_sdk_runtime",
        "recorded_url": VENDOR_RUNTIME_URL,
        "version": None,
        "build_sha256": None,
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
        "kind": "sdk_abi_callback_and_processing_contract",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "dnsmos_c_scorer",
        "kind": "official_nisqa_checkpoint_and_feature_extractor",
        "source_url": SCORER_SOURCE,
        "checkpoint": SCORER_CHECKPOINT,
        "checkpoint_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "dnsmos_c_runtime",
        "kind": "hash_pinned_offline_scoring_environment",
        "lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_corpus",
        "repository": CORPUS_REPOSITORY,
        "recorded_revision": CORPUS_REVISION,
        "recorded_file_count": CORPUS_FILE_COUNT,
        "recorded_sample_rate_hz": CORPUS_SAMPLE_RATE_HZ,
        "recorded_sample_format": CORPUS_SAMPLE_FORMAT,
        "recorded_license": CORPUS_LICENSE,
        "local_copy_present": False,
        "per_file_manifest": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "processed_vendor_outputs",
        "repository": PROCESSED_REPOSITORY,
        "recorded_revision": PROCESSED_REVISION,
        "recorded_subset": PROCESSED_SUBSET,
        "recorded_file_count": PROCESSED_FILE_COUNT,
        "recorded_bytes": PROCESSED_BYTES,
        "local_copy_present": False,
        "per_file_manifest": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "corpus_rights_approval",
        "kind": "approved_noncommercial_scoring_and_publication_scope",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "output_redistribution_approval",
        "kind": "vendor_output_redistribution_or_publication_grant",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "comparison_manifest",
        "kind": "frozen_file_scenario_windowing_and_aggregation_manifest",
        "path": MISSING_COMPARISON_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "vendor_claim_record",
        "kind": "pinned_source_reported_vendor_benchmark_record",
        "path": "research/cpp-library-krisp-benchmark-20261109.md",
        "sha256": SOURCE_PINS[
            "research/cpp-library-krisp-benchmark-20261109.md"],
        "required": True,
        "status": "present_source_report_only",
    },
)

CALLER_ASSET_FIELDS = (
    "channels",
    "config_path",
    "config_sha256",
    "corpus_manifest_path",
    "corpus_manifest_sha256",
    "dnsmos_checkpoint_path",
    "dnsmos_checkpoint_sha256",
    "dnsmos_environment_lock_path",
    "dnsmos_environment_lock_sha256",
    "platform",
    "processed_outputs_manifest_path",
    "processed_outputs_manifest_sha256",
    "redistribution_approval_path",
    "redistribution_approval_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "sample_rate_hz",
    "scope",
    "variant",
    "vendor_entitlement_id",
    "vendor_license_path",
    "vendor_license_sha256",
    "vendor_runtime_lock_path",
    "vendor_runtime_lock_sha256",
    "vendor_runtime_path",
    "vendor_runtime_version",
)

CALLER_FILE_PAIRS = (
    ("config_path", "config_sha256"),
    ("corpus_manifest_path", "corpus_manifest_sha256"),
    ("dnsmos_checkpoint_path", "dnsmos_checkpoint_sha256"),
    ("dnsmos_environment_lock_path", "dnsmos_environment_lock_sha256"),
    ("processed_outputs_manifest_path", "processed_outputs_manifest_sha256"),
    ("redistribution_approval_path", "redistribution_approval_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("vendor_license_path", "vendor_license_sha256"),
    ("vendor_runtime_lock_path", "vendor_runtime_lock_sha256"),
)
CALLER_DIR_FIELDS = ("vendor_runtime_path",)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_whole_utterance"
CALLER_SCOPE = "vendor_output_scoring"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
REQUIRED_SAMPLE_RATE_HZ = COMPARISON_SAMPLE_RATE_HZ
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
ENTITLEMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
PLATFORM_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_version_entitlement_platform_geometry_"
        "scope_and_offline_variant_only; do_not_import_link_or_execute_in_"
        "this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_scope": CALLER_SCOPE,
    "required_vendor_runtime_version": VENDOR_RUNTIME_VERSION,
    "runtime_version_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
    "required_geometry": {
        "channels": COMPARISON_CHANNELS,
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "sample_format": COMPARISON_SAMPLE_FORMAT,
        "status": COMPARISON_GEOMETRY_STATUS,
    },
    "notes": (
        "Every vendor runtime file, licence entitlement, configuration, "
        "corpus manifest, processed-output manifest, DNSMOS-C checkpoint, "
        "scoring environment lock, rights record and redistribution approval "
        "must exist at an absolute path and match its declared SHA-256 before "
        "a caller may score outputs. The scope is vendor-output scoring, not "
        "live vendor runtime processing in the default package. No vendor "
        "runtime version is pinned because no licensed runtime or SDK terms "
        "are recorded."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "vendor_runtime_absent",
        "state": "absent",
        "requirement": (
            "Supply the licensed Krisp Voice Isolation 2.5 SDK runtime, its "
            "exact version/build identity and per-file SHA-256 manifest; no "
            "vendor runtime, library, model or entitlement is present."),
    },
    {
        "id": "vendor_license_and_terms_unverified",
        "state": "absent",
        "requirement": (
            "Record the exact commercial entitlement and vendor terms for "
            "local processing, output retention, scoring, publication and "
            "redistribution; no licence text, grant or entitlement exists."),
    },
    {
        "id": "vendor_sdk_abi_undocumented",
        "state": "absent",
        "requirement": (
            "Document the vendor SDK ABI, callback contract, supported "
            "sample rate, channel count, frame size, content delay, reset "
            "and drain behaviour before any isolated adapter may be built."),
    },
    {
        "id": "dnsmos_c_scorer_absent",
        "state": "absent",
        "requirement": (
            "Supply the official DNSMOS-C/NISQA checkpoint at "
            "runs/NISQA/model_best.pt, its feature extractor and the exact "
            "windowing configuration with byte counts and SHA-256 values; no "
            "checkpoint or scorer code is present."),
    },
    {
        "id": "dnsmos_c_runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned offline Python runtime at "
            "data/envs/dnsmos-c/requirements.lock with a recorded platform; "
            "no scoring environment, package lock or interpreter pin exists."),
    },
    {
        "id": "source_corpus_absent",
        "state": "absent",
        "requirement": (
            "Supply the 265-file Krisp-AI/VoiceIsolation-Benchmark-Dataset at "
            "revision 626bac8ca07fb9b4846d4f62d27c321753160b36 with a "
            "per-file SHA-256 manifest and the CC BY-NC 4.0 terms; only the "
            "revision is recorded and no audio is retained."),
    },
    {
        "id": "processed_vendor_outputs_absent",
        "state": "absent",
        "requirement": (
            "Supply the vi_2_5_default subset of "
            "Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed at revision "
            "8759715197e39e0356125e3f3197a9854c38fa60 (265 files, "
            "647,960,782 bytes) with a per-file manifest; no output is "
            "retained or identified by digest."),
    },
    {
        "id": "corpus_and_output_rights_uncleared",
        "state": "absent",
        "requirement": (
            "Clear noncommercial corpus use, vendor-output retention, "
            "scoring, publication and any redistribution with complete "
            "notices; no rights approval or output-use grant exists."),
    },
    {
        "id": "comparison_manifest_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Freeze the exact 265-file list, scenario mapping, segment "
            "windowing, failed-item policy, aggregation and one approved "
            "vendor parity vector; no comparison manifest or parity result "
            "exists."),
    },
    {
        "id": "wer_ensemble_unavailable",
        "state": "absent",
        "requirement": (
            "Reproduce or explicitly defer the 11-configuration WER "
            "ensemble with its transcripts, ASR hypotheses and NeMo WFST "
            "normalization; one local ASR engine cannot reproduce the "
            "vendor aggregate, so WER remains not measured."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "vendor_runtime_and_license_identity",
        "The licensed vendor runtime version, build, per-file SHA-256 "
        "manifest, entitlement and terms match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated, hash-pinned vendor runtime and scoring environment are "
        "admitted on a recorded platform.",
    ),
    (
        "artifact_corpus_and_output_rights",
        "Corpus, transcript, vendor-output, scoring, publication and "
        "redistribution rights are cleared with complete notices.",
    ),
    (
        "exact_reference_parity",
        "One approved vendor-output file matches an approved exact-runtime "
        "reference for one frozen Voice Isolation 2.5 configuration.",
    ),
    (
        "same_scorer_reproduction",
        "The pinned DNSMOS-C scorer reproduces the scenario-balanced "
        "comparison on the frozen 265-file output set with recorded failures.",
    ),
    (
        "scope_and_claim_separation",
        "Local runtime, vendor-output scoring and vendor claims stay "
        "separate, and no source-reported value is presented as reproduced.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in vendor adapter intake, licence review, descriptor "
        "review and an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release "
        "or public-benchmark approval are recorded; this package is off by "
        "default.",
    ),
)

EXTERNAL_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "allowed_access_and_exact_data",
        "Document the allowed access and the exact candidate or processed "
        "data.",
        "absent",
    ),
    (
        "runtime_output_and_claim_separation",
        "Separate local runtime, vendor-output scoring and vendor claim.",
        "structural_only",
    ),
    (
        "fallback_and_disclosure_without_runtime",
        "Verify what fallback and disclosure are possible without a licensed "
        "runtime, code or asset in the default package.",
        "declared_not_verified",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_reproduced_here",
    "source": "research/cpp-library-krisp-benchmark-20261109.md",
    "source_sha256": SOURCE_PINS[
        "research/cpp-library-krisp-benchmark-20261109.md"],
    "record_name": UPSTREAM_RECORD_NAME,
    "vendor": UPSTREAM_VENDOR,
    "benchmark_url": BENCHMARK_URL,
    "corpus": {
        "repository": CORPUS_REPOSITORY,
        "revision": CORPUS_REVISION,
        "file_count": CORPUS_FILE_COUNT,
        "sample_rate_hz": CORPUS_SAMPLE_RATE_HZ,
        "sample_format": CORPUS_SAMPLE_FORMAT,
        "license": CORPUS_LICENSE,
    },
    "processed_outputs": {
        "repository": PROCESSED_REPOSITORY,
        "revision": PROCESSED_REVISION,
        "subset": PROCESSED_SUBSET,
        "file_count": PROCESSED_FILE_COUNT,
        "bytes": PROCESSED_BYTES,
    },
    "scorer": {
        "name": SCORER_NAME,
        "checkpoint": SCORER_CHECKPOINT,
        "source": SCORER_SOURCE,
        "checkpoint_sha256": SCORER_CHECKPOINT_SHA256,
        "local_present": False,
    },
    "vendor_published_dnsmos_c": {
        "work": 3.96,
        "call_center": 4.02,
        "phone_calls": 3.45,
        "raw_baseline_overall": 3.40,
        "label": "vendor_published_not_reproduced_here",
    },
    "research_record_reported_dnsmos_c": {
        "work": {"raw": 3.374, "krisp_default": 3.944, "basic_v1": 3.575,
                 "voice_focus_v1": 3.636},
        "call_center": {"raw": 3.600, "krisp_default": 4.018,
                        "basic_v1": 3.794, "voice_focus_v1": 3.829},
        "phone_calls": {"raw": 3.133, "krisp_default": 3.482,
                        "basic_v1": 3.189, "voice_focus_v1": 3.457},
        "scenario_average": {"raw": 3.369, "krisp_default": 3.815,
                             "basic_v1": 3.519, "voice_focus_v1": 3.641},
        "label": "historical_research_record_not_reproduced_here",
    },
    "vendor_published_wer": {
        "work": {"raw": 0.3184, "krisp_default": 0.0630},
        "call_center": {"raw": 0.2383, "krisp_default": 0.0686},
        "phone_calls": {"raw": 0.0348, "krisp_default": 0.0391},
        "all_files": {"raw": 0.2324, "krisp_default": 0.0624},
        "engine_count": WER_ENGINE_COUNT,
        "tool": WER_TOOL,
        "local_audio_enhance_wer": None,
        "label": "vendor_published_not_reproduced_here",
    },
    "sibling_context_not_attributed": [
        "The sibling Krisp accent-conversion task and the Krisp noise-"
        "cancellation task are separate vendor observations; no accent, "
        "noise-cancellation or VI score is inherited here.",
        "The cpp-library basic.v1 and voice_focus.v1 preset values belong to "
        "the historical research record, not to this SDK evidence package.",
        "The 265 processed outputs are Krisp vendor outputs; they are not "
        "audio_enhance or SDK provider outputs.",
        "No WER value is produced for audio_enhance or the SDK; the vendor "
        "11-engine aggregate remains unrun.",
    ],
    "notes": (
        "Every number above is source-reported. None was reproduced, checked "
        "against local audio or scored in this package. The research record "
        "kept its downloaded audio under /private/tmp and did not add it to "
        "the repository, so no retained path or per-file digest exists."),
}

CONTROL_PLAN_PROVENANCE = (
    "synthetic_vendor_output_scoring_accounting_control_not_scorer_output")

CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 3
CONTROL_OUTPUT_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 2
PCM_SAMPLE_CAP = 10_000_000
SCENARIOS: Tuple[str, ...] = ("work", "call_center", "phone_calls")
SYNTHETIC_SCENARIO_SCORES: Dict[str, Tuple[str, ...]] = {
    "work": ("3", "4", "4"),
    "call_center": ("4", "4", "5"),
    "phone_calls": ("2", "3", "4"),
}
MIN_SCORE = Fraction(1)
MAX_SCORE = Fraction(5)

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
    "score_not_mapping",
    "score_missing_scenario",
    "score_extra_scenario",
    "score_empty_scenario",
    "score_nan",
    "score_pos_inf",
    "score_neg_inf",
    "score_out_of_range",
    "score_bool",
    "score_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_bad_version",
    "manifest_wrong_scope",
    "manifest_wrong_variant",
    "manifest_channels_zero",
    "manifest_rate_below_range",
    "manifest_rate_bool",
    "manifest_empty_entitlement",
    "manifest_bad_platform",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

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
# Vendor runtime, asset and absence audit.  Fixed local reads only.
# ---------------------------------------------------------------------------

def _runtime_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/runtime/krisp-voice-isolation-2-5",
        SOURCE_ROOT / "data/runtime/krisp",
        SOURCE_ROOT / "data/runtime/Krisp",
        SOURCE_ROOT / "data/checkouts/krisp-voice-isolation-2-5",
        SOURCE_ROOT / "data/checkouts/Krisp",
    ]


def _scorer_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/dnsmos-c",
        SOURCE_ROOT / "data/models/dnsmos-c/nisqa",
        SOURCE_ROOT / "data/models/nisqa",
        SOURCE_ROOT / "data/checkouts/DNSMOS-C",
        SOURCE_ROOT / "data/checkouts/dnsmos-c",
    ]


def _corpus_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/corpus/krisp-voice-isolation-benchmark",
        SOURCE_ROOT / "data/corpus/Krisp-AI/VoiceIsolation-Benchmark-Dataset",
        SOURCE_ROOT / "data/checkouts/VoiceIsolation-Benchmark-Dataset",
    ]


def _output_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/runs/krisp-voice-isolation-2-5/processed",
        SOURCE_ROOT / "data/runs/krisp-voice-isolation-2-5/outputs",
        SOURCE_ROOT / "data/checkouts/VoiceIsolation-Benchmark-Dataset-Processed",
    ]


def _license_candidates() -> List[str]:
    found: List[str] = []
    for relative in (MISSING_LICENSE_PATH, MISSING_RIGHTS_PATH):
        path = SOURCE_ROOT / relative
        if path.is_file():
            found.append(relative)
    return found


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def audit_assets() -> Dict[str, Any]:
    runtime_paths = _runtime_candidates()
    scorer_paths = _scorer_candidates()
    corpus_paths = _corpus_candidates()
    output_paths = _output_candidates()
    runtime_env = SOURCE_ROOT / MISSING_SCORER_ENV_PATH
    runtime_lock = SOURCE_ROOT / MISSING_SCORER_LOCK_PATH
    rights_record = SOURCE_ROOT / MISSING_RIGHTS_PATH
    comparison_manifest = SOURCE_ROOT / MISSING_COMPARISON_PATH
    parity_manifest = SOURCE_ROOT / MISSING_PARITY_PATH
    licenses = _license_candidates()
    probes = probe_absence()
    return {
        "vendor_runtime_path": MISSING_RUNTIME_PATH,
        "vendor_runtime_present": any(path.is_dir() for path in runtime_paths),
        "vendor_runtime_version": None,
        "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "vendor_runtime_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in runtime_paths
        ],
        "vendor_license_files": licenses,
        "vendor_license_present": bool(licenses),
        "scorer_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in scorer_paths
        ],
        "scorer_present": any(path.exists() for path in scorer_paths),
        "scorer_checkpoint_sha256": None,
        "scorer_env_present": runtime_env.is_dir(),
        "scorer_lock_present": runtime_lock.is_file(),
        "corpus_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in corpus_paths
        ],
        "corpus_present": any(path.exists() for path in corpus_paths),
        "output_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in output_paths
        ],
        "processed_outputs_present": any(path.exists()
                                         for path in output_paths),
        "rights_record_present": rights_record.is_file(),
        "comparison_manifest_present": comparison_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "vendor_scope": VENDOR_OUTPUT_SCOPING,
            "comparison_geometry": {
                "sample_rate_hz": COMPARISON_SAMPLE_RATE_HZ,
                "channels": COMPARISON_CHANNELS,
                "sample_format": COMPARISON_SAMPLE_FORMAT,
                "status": COMPARISON_GEOMETRY_STATUS,
            },
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "corpus_revision": CORPUS_REVISION,
            "processed_revision": PROCESSED_REVISION,
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
# Deterministic synthetic PCM, scoring accounting and acceptance controls.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_source_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x70CAB1E5
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def synthetic_output_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x5EED70CA
    for index in range(CONTROL_OUTPUT_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 41, 0.25) + 0.02 * noise)
    return samples


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


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "sample_format": "f32",
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def duration_accounting(source_samples: int, output_samples: int
                        ) -> Dict[str, Any]:
    if not isinstance(source_samples, int) or isinstance(source_samples, bool):
        raise Reject("source sample count must be an integer")
    if not isinstance(output_samples, int) or isinstance(output_samples, bool):
        raise Reject("output sample count must be an integer")
    if source_samples <= 0 or output_samples <= 0:
        raise Reject("sample counts must be positive")
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


def alignment_accounting(output_samples: int) -> Dict[str, Any]:
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "first_output_sample": 0,
        "first_output_delay_samples": 0,
        "tail_samples": output_samples,
        "whole_clip_required": True,
        "note": (
            "No vendor runtime exists, so vendor alignment and device timing "
            "are not measured. This declares the offline-only accounting "
            "boundary for the synthetic control; it is not a vendor or device "
            "timing result."),
    }


def _score_fraction(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise Reject("score must not be a boolean")
    if isinstance(value, Fraction):
        score = value
    elif isinstance(value, int):
        score = Fraction(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise Reject("score is not finite")
        score = Fraction(str(value))
    elif isinstance(value, str):
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
            raise Reject("score string is not a plain nonnegative decimal")
        score = Fraction(value)
    else:
        raise Reject("score must be an integer, decimal or fraction")
    if score < MIN_SCORE or score > MAX_SCORE:
        raise Reject("score is outside the 1-5 scale")
    return score


def scenario_balanced_mean(scores: Any) -> Dict[str, Any]:
    """Equal-weight mean of per-scenario means, exactly as documented.

    The three scenarios carry equal weight regardless of file count.  This is
    a scoring-accounting control only; no scorer is invoked.
    """

    if not isinstance(scores, dict):
        raise Reject("scenario scores must be a mapping")
    present = set(scores)
    expected = set(SCENARIOS)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise Reject("missing scenarios: " + ",".join(missing))
    if extra:
        raise Reject("unknown scenarios: " + ",".join(extra))
    scenario_means: Dict[str, Any] = {}
    mean_values: List[Fraction] = []
    for scenario in SCENARIOS:
        values = scores[scenario]
        if not isinstance(values, (list, tuple)):
            raise Reject("scenario " + scenario + " must be a score list")
        if not values:
            raise Reject("scenario " + scenario + " is empty")
        checked = [_score_fraction(value) for value in values]
        mean = sum(checked, Fraction(0)) / len(checked)
        scenario_means[scenario] = {
            "count": len(checked),
            "mean": fraction_text(mean),
            "mean_float": float(mean),
        }
        mean_values.append(mean)
    overall = sum(mean_values, Fraction(0)) / len(mean_values)
    return {
        "scenarios": scenario_means,
        "overall": {
            "mean": fraction_text(overall),
            "mean_float": float(overall),
        },
        "aggregation": "unweighted_mean_of_three_scenario_means",
        "label": CONTROL_PLAN_PROVENANCE,
        "qualification_effect": "none",
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_source = synthetic_source_pcm()
    good_output = synthetic_output_pcm()
    good_scores = {name: list(values)
                   for name, values in SYNTHETIC_SCENARIO_SCORES.items()}
    good_manifest = _shape_only_manifest()

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

    def scores_with(key: str, value: Any):
        scores = dict(good_scores)
        scores[key] = value
        return lambda: scenario_balanced_mean(scores)

    existing = _existing_file_manifest()
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_stereo", lambda: validate_pcm(
            good_source, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("score_not_mapping", lambda: scenario_balanced_mean([])),
        ("score_missing_scenario", lambda: scenario_balanced_mean(
            {key: value for key, value in good_scores.items()
             if key != "phone_calls"})),
        ("score_extra_scenario", lambda: scenario_balanced_mean(
            dict(good_scores, music=["4"]))),
        ("score_empty_scenario", scores_with("work", [])),
        ("score_nan", scores_with("work", [math.nan])),
        ("score_pos_inf", scores_with("work", [math.inf])),
        ("score_neg_inf", scores_with("work", [-math.inf])),
        ("score_out_of_range", scores_with("work", ["5.5"])),
        ("score_bool", scores_with("work", [True])),
        ("score_string", scores_with("work", ["great"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("config_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "config_path", "configs/krisp-vi-2.5.json")),
        ("manifest_bad_sha", wrong("config_sha256", "ABC")),
        ("manifest_bad_version", wrong("vendor_runtime_version", "2.5")),
        ("manifest_wrong_scope", wrong("scope", "vendor_runtime_adapter")),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_rate_below_range", wrong("sample_rate_hz", 4000)),
        ("manifest_rate_bool", wrong("sample_rate_hz", True)),
        ("manifest_empty_entitlement", wrong("vendor_entitlement_id", "")),
        ("manifest_bad_platform", wrong("platform", "macOS ARM64")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, config_path=(
                "/nonexistent/krisp-vi-fixtures/config.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, vendor_runtime_path=(
                "/nonexistent/krisp-vi-fixtures/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, config_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    good = pcm_summary(good_source, CONTROL_SAMPLE_RATE_HZ)
    good_out = pcm_summary(good_output, CONTROL_SAMPLE_RATE_HZ)
    if good["samples"] != CONTROL_SOURCE_SAMPLES:
        raise Reject("synthetic source control mismatch")
    if good_out["samples"] != CONTROL_OUTPUT_SAMPLES:
        raise Reject("synthetic output control mismatch")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/krisp-voice-isolation-2-5-evidence-fixture"
    digest = "0" * 64
    return {
        "channels": COMPARISON_CHANNELS,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "corpus_manifest_path": root + "/corpus-manifest.json",
        "corpus_manifest_sha256": digest,
        "dnsmos_checkpoint_path": root + "/model_best.pt",
        "dnsmos_checkpoint_sha256": digest,
        "dnsmos_environment_lock_path": root + "/requirements.lock",
        "dnsmos_environment_lock_sha256": digest,
        "platform": "macos-arm64",
        "processed_outputs_manifest_path": root + "/outputs-manifest.json",
        "processed_outputs_manifest_sha256": digest,
        "redistribution_approval_path": root + "/redistribution.json",
        "redistribution_approval_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "variant": CALLER_VARIANT,
        "vendor_entitlement_id": "krisp-entitlement-0001",
        "vendor_license_path": root + "/license.txt",
        "vendor_license_sha256": digest,
        "vendor_runtime_lock_path": root + "/runtime.lock",
        "vendor_runtime_lock_sha256": digest,
        "vendor_runtime_path": root + "/runtime",
        "vendor_runtime_version": "2.5.0",
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio,
    importing a vendor runtime or loading a scorer.  Duplicate paths are
    allowed; each pair carries the real digest so a single corrupted digest
    reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "config_path": HERE / "reference.py",
        "corpus_manifest_path": HERE / "README.md",
        "dnsmos_checkpoint_path": HERE / "run.py",
        "dnsmos_environment_lock_path": HERE / "SOURCES.sha256.license",
        "processed_outputs_manifest_path": HERE / "LICENSES.md",
        "redistribution_approval_path": HERE / "contract.json.license",
        "rights_record_path": HERE / "LICENSES.md",
        "vendor_license_path": HERE / "README.md",
        "vendor_runtime_lock_path": HERE / "SOURCES.sha256.license",
    }
    manifest: Dict[str, Any] = {
        "channels": COMPARISON_CHANNELS,
        "platform": "macos-arm64",
        "sample_rate_hz": REQUIRED_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "variant": CALLER_VARIANT,
        "vendor_entitlement_id": "krisp-entitlement-0001",
        "vendor_runtime_path": str(SDK_ROOT),
        "vendor_runtime_version": "2.5.0",
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


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest " + field + " is outside the admitted range")
    if value != REQUIRED_SAMPLE_RATE_HZ:
        raise Reject("manifest " + field + " is not the comparison rate")
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
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
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
    version = manifest["vendor_runtime_version"]
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise Reject("manifest vendor_runtime_version is invalid")
    entitlement = manifest["vendor_entitlement_id"]
    if not isinstance(entitlement, str) or not ENTITLEMENT_PATTERN.fullmatch(
            entitlement):
        raise Reject("manifest vendor_entitlement_id is invalid")
    platform = manifest["platform"]
    if not isinstance(platform, str) or not PLATFORM_PATTERN.fullmatch(platform):
        raise Reject("manifest platform is invalid")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("manifest channels must be an integer")
    if channels != COMPARISON_CHANNELS:
        raise Reject("manifest channels mismatch")
    sample_rate = _rate_value(manifest, "sample_rate_hz")
    if manifest["scope"] != CALLER_SCOPE:
        raise Reject("manifest scope must be " + CALLER_SCOPE)
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
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
    return {
        "accepted": True,
        "vendor_runtime_version": version,
        "runtime_version_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "variant": CALLER_VARIANT,
        "scope": CALLER_SCOPE,
        "sample_rate_hz": sample_rate,
        "channels": COMPARISON_CHANNELS,
        "platform": platform,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "vendor_runtime_imported": False,
        "scorer_executed": False,
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = synthetic_output_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output, CONTROL_SAMPLE_RATE_HZ)
    durations = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    scoring = scenario_balanced_mean(
        {name: list(values)
         for name, values in SYNTHETIC_SCENARIO_SCORES.items()})
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
            "control_sample_format": "f32",
            "recorded_comparison_sample_rate_hz": COMPARISON_SAMPLE_RATE_HZ,
            "recorded_comparison_channels": COMPARISON_CHANNELS,
            "recorded_comparison_sample_format": COMPARISON_SAMPLE_FORMAT,
            "recorded_comparison_status": COMPARISON_GEOMETRY_STATUS,
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
            "vendor_scope": VENDOR_OUTPUT_SCOPING,
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "source_pcm": source_summary,
        "output_pcm": output_summary,
        "duration": durations,
        "alignment": alignment,
        "synthetic_scoring": scoring,
        "accepted_control": {
            "id": "synthetic_structure_only_manifest",
            "accepted": positive["accepted"],
            "vendor_runtime_version": positive["vendor_runtime_version"],
            "scope": positive["scope"],
            "variant": positive["variant"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "model_executed": positive["model_executed"],
            "vendor_runtime_imported": positive["vendor_runtime_imported"],
            "scorer_executed": positive["scorer_executed"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a vendor runtime, "
                "not a scorer asset set and not a vendor output, and it cannot "
                "qualify the candidate."),
        },
        "acceptance_outcomes": [
            {
                "id": "same_scorer_dnsmos_c",
                "measured": False,
                "value": None,
                "reason": "no scorer checkpoint, runtime, corpus or outputs",
            },
            {
                "id": "scenario_balanced_aggregation",
                "measured": False,
                "value": None,
                "reason": (
                    "synthetic accounting shape only; no real per-file score"),
            },
            {
                "id": "wer_ensemble",
                "measured": False,
                "value": None,
                "reason": (
                    "11-configuration vendor aggregate is not reproducible "
                    "with the locally available ASR; not run"),
            },
            {
                "id": "vendor_runtime_timing",
                "measured": False,
                "value": None,
                "reason": "no licensed vendor runtime; no device clock",
            },
            {
                "id": "listening_or_naturalness",
                "measured": False,
                "value": None,
                "reason": "no authorized listening panel",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf",
                "score_nan", "score_pos_inf", "score_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "score_out_of_range", "score_bool", "score_string",
                "manifest_channels_zero", "manifest_rate_below_range",
                "manifest_rate_bool", "manifest_bad_version",
                "manifest_empty_entitlement", "manifest_bad_platform",
                "manifest_wrong_scope", "manifest_wrong_variant"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "score_missing_scenario", "score_empty_scenario",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic PCM and scoring-accounting controls only at the public "
            "v0 boundary and the recorded 16 kHz mono comparison geometry. "
            "They are not vendor output, not DNSMOS-C, not WER, not a quality "
            "or timing result and cannot qualify the candidate."),
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
            "The licensed Krisp Voice Isolation 2.5 runtime, entitlement and "
            "SDK terms are absent, as are the DNSMOS-C/NISQA checkpoint and "
            "scoring runtime, the CC BY-NC 4.0 corpus, the 265 processed "
            "vendor outputs, rights approval, comparison manifest and parity "
            "vector; the 11-engine WER ensemble is unrun and all vendor "
            "numbers remain source-reported."),
    }


def _gates() -> List[Dict[str, str]]:
    return [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]


def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["vendor_runtime_present"]
        and observed["vendor_license_present"]
        and observed["scorer_present"]
        and observed["scorer_env_present"]
        and observed["scorer_lock_present"]
        and observed["corpus_present"]
        and observed["processed_outputs_present"]
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
        "vendor_runtime_present": observed["vendor_runtime_present"],
        "vendor_runtime_version": observed["vendor_runtime_version"],
        "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
        "vendor_license_present": observed["vendor_license_present"],
        "scorer_present": observed["scorer_present"],
        "scorer_env_present": observed["scorer_env_present"],
        "scorer_lock_present": observed["scorer_lock_present"],
        "corpus_present": observed["corpus_present"],
        "processed_outputs_present": observed["processed_outputs_present"],
        "rights_record_present": observed["rights_record_present"],
        "comparison_manifest_present": observed["comparison_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No vendor runtime, entitlement, scorer checkpoint, scoring "
            "environment, corpus, processed output, rights record, comparison "
            "manifest or parity vector was observed. The historical research "
            "record and its source-reported numbers are provenance only."),
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
        for item, requirement, status in EXTERNAL_REQUIREMENTS
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
            "benchmark_url": BENCHMARK_URL,
            "vendor_runtime_url": VENDOR_RUNTIME_URL,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
            "vendor_runtime_present": False,
            "vendor_source_checkout_available": False,
            "vendor_scope": VENDOR_OUTPUT_SCOPING,
            "vendor_runtime_geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "vendor_runtime_geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
            "comparison_geometry": {
                "sample_rate_hz": COMPARISON_SAMPLE_RATE_HZ,
                "channels": COMPARISON_CHANNELS,
                "sample_format": COMPARISON_SAMPLE_FORMAT,
                "status": COMPARISON_GEOMETRY_STATUS,
            },
            "corpus_revision": CORPUS_REVISION,
            "processed_outputs_revision": PROCESSED_REVISION,
            "corpus_license": CORPUS_LICENSE,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "external_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_external_metrics": None,
            "separation": {
                "local_vendor_runtime": "absent",
                "vendor_output_scoring": "not_run",
                "vendor_claim": "source_reported_only",
                "default_package_fallback": (
                    "no vendor runtime, code, corpus, output, scorer or "
                    "claim is bundled or substituted"),
                "disclosure": (
                    "Every vendor and historical research number is labelled "
                    "source_reported_not_reproduced_here"),
            },
            "note": (
                "The external profile is not satisfied for qualification: no "
                "approved access, exact local data, licensed runtime, scorer "
                "or approved parity exists."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "scope_mismatch_rejected": True,
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
            MISSING_LICENSE_PATH,
            MISSING_SCORER_PATH,
            MISSING_SCORER_ENV_PATH,
            MISSING_SCORER_LOCK_PATH,
            MISSING_CORPUS_PATH,
            MISSING_OUTPUTS_PATH,
            MISSING_COMPARISON_PATH,
            MISSING_PARITY_PATH,
            MISSING_RIGHTS_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model, scorer, vendor SDK or "
            "audio runtime is imported.",
            "Fixed workspace paths are probed for runtime, licence, scorer, "
            "environment, corpus, outputs, rights and parity presence.",
            "No vendor library is linked, no checkpoint byte is read and no "
            "audio is opened.",
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
            "documentation_url": VENDOR_RUNTIME_URL,
            "geometry_status": VENDOR_RUNTIME_GEOMETRY_STATUS,
            "geometry_asserted": VENDOR_RUNTIME_GEOMETRY_ASSERTED,
        },
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "vendor": UPSTREAM_VENDOR,
            "record_name": UPSTREAM_RECORD_NAME,
            "benchmark_url": BENCHMARK_URL,
            "vendor_runtime_version": VENDOR_RUNTIME_VERSION,
            "vendor_runtime_pin_available": VENDOR_RUNTIME_PIN_AVAILABLE,
            "vendor_source_checkout_available": False,
            "vendor_scope": VENDOR_OUTPUT_SCOPING,
            "comparison_geometry": {
                "sample_rate_hz": COMPARISON_SAMPLE_RATE_HZ,
                "channels": COMPARISON_CHANNELS,
                "sample_format": COMPARISON_SAMPLE_FORMAT,
                "status": COMPARISON_GEOMETRY_STATUS,
            },
            "corpus_revision": CORPUS_REVISION,
            "processed_outputs_revision": PROCESSED_REVISION,
            "corpus_license": CORPUS_LICENSE,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": gates,
        "external_profile_requirements": [
            {"id": item, "requirement": requirement, "status": status}
            for item, requirement, status in EXTERNAL_REQUIREMENTS
        ],
        "missing_historical_artifacts": [
            MISSING_RUNTIME_PATH,
            MISSING_LICENSE_PATH,
            MISSING_SCORER_PATH,
            MISSING_SCORER_ENV_PATH,
            MISSING_SCORER_LOCK_PATH,
            MISSING_CORPUS_PATH,
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
                "unverified; the vendor runtime and SDK terms are absent and "
                "the public corpus is CC BY-NC 4.0 with no local copy"),
        },
    }
