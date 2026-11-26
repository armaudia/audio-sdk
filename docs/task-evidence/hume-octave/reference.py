# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the task-local
SDK-HUME-OCTAVE package.

Hume Octave is a vendor-hosted cloud text-to-speech product. The merged
research record (candidate matrix record 55) marks it ``out of scope`` for
microphone input enhancement: it generates a response voice from text and its
time-to-first-byte figure is vendor-reported, not a local measurement. No
vendor entitlement, credential, pinned API contract, data-processing record,
target-voice consent, isolated client runtime, cohort or parity vector exists
in this workspace.

This module never imports a model, TTS or network runtime, never sends a
request, never reads or writes real audio, never downloads anything and never
measures a device clock. It provides four verifiable pieces:

* a fail-closed source/asset/vendor audit over fixed workspace paths that
  records the absent vendor access, contract, terms, consent, runtime, rights,
  cohort and parity records and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a fail-closed target-condition admission that accepts only the declared
  local identity control and rejects every synthesized target voice or
  expressiveness setting because the vendor runtime and entitlement are absent;
* a deterministic synthetic identity accounting control at the public v0
  geometry (16 kHz mono float32, 160 samples per frame) that checks exact
  source/identity sample preservation and offline-only alignment without
  asserting any vendor geometry or generated output.

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

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = Path(
    os.environ.get("SDK_ROOT", str(TASK_DIR.parents[2]))
).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2]))
).resolve()
TASK_BOARD_REL = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/hume-octave-report/0.1"
CALLER_SCHEMA = "audio-sdk/hume-octave/caller-supplied-asset/0.1"

TASK_ID = "SDK-HUME-OCTAVE"
TITLE = "Hume Octave"
COMPONENT = "hume-octave"
REPOSITORY = "audio-sdk"
MODE = "external-adapter"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "59971563b2c9cdf7b845e8210dd2697d55b8bc08"
BRANCH = "swarm/SDK-HUME-OCTAVE"
REVIEWER = "reviewer-HUME-OCTAVE"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    + TASK_ID)
TASK_PREFIX = "docs/task-evidence/hume-octave/"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_PERIOD_NS = 62500

MICRO_SCALE = 1000000
TARGET_EXPRESSIVENESS_FULL = 1000
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
CONTROL_SOURCE_SAMPLES = 32000
CONTROL_LEAD_SAMPLES = 4000
CONTROL_VOICED_END = 24000
CONTROL_TAIL_START = 30000
CONTROL_VOICED_PERIOD = 80
CONTROL_VOICED_AMPLITUDE_MICRO = 300000
CONTROL_NOISE_AMPLITUDE_MICRO = 8000
PCM_SAMPLE_CAP = 10000000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

TASK_KIND = "cloud_text_to_speech_response_voice"
COMPARISON_BASELINE = "local_identity"
CALLER_VARIANT = "offline_whole_utterance"
IDENTITY_LABEL = "identity"
MAX_TARGET_EXPRESSIVENESS = 1000
VENDOR_CONTRACT_REVISION_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:+-]{0,63}$"

CANDIDATE_RECORD = 55
CANDIDATE_RECORD_PATH = (
    "research/voice-enhancement-20261101/candidate_matrix.csv")
CANDIDATE_REPORT_PATHS = (
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
)

MISSING_SOURCE_PATH = "data/checkouts/hume-octave"
MISSING_WEIGHTS_PATH = "data/models/hume-octave"
VENDOR_CONTRACT_PATH = "data/manifests/hume-octave-api-contract.json"
ENTITLEMENT_PATH = "data/credentials/hume-octave-entitlement.json"
VENDOR_TERMS_PATH = "data/rights/hume-octave-vendor-terms.json"
DATA_PROCESSING_PATH = "data/rights/hume-octave-data-processing.json"
VOICE_CONSENT_PATH = "data/rights/hume-octave-voice-consent.json"
RIGHTS_RECORD_PATH = "data/rights/hume-octave-rights.json"
COHORT_MANIFEST_PATH = "data/runs/hume-octave-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/hume-octave-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/hume-octave"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"

ARTIFACT_FILES: Tuple[str, ...] = (
    "README.md",
    "LICENSES.md",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES + ("contract.json",)

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
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
    ),
    "research/voice-enhancement-20261101/"
    "agent-transform-space/REPORT.md": (
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4"
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c"
    ),
    "audio-benchmark-platform/plan/INVENTORY.md": (
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130"
    ),
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": (
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
    ),
    "audio-benchmark-platform/plan/audio-sdk/README.md": (
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06"
    ),
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "audio-benchmark-platform/audio-sdk/README.md": (
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35"
    ),
}

BOUNDARY_PINS: Dict[str, str] = {
    "CMakeLists.txt": (
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04"
    ),
    "CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "REUSE.toml": (
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8"
    ),
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
    "scripts/ci.py": (
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f"
    ),
}

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": SAMPLE_FORMAT,
    "sdk_v0_frame_samples": FRAME_SAMPLES,
    "sdk_v0_sample_period_ns": SAMPLE_PERIOD_NS,
    "candidate_geometry_status": "unestablished",
    "candidate_geometry_asserted": False,
    "target_condition_status": "unestablished",
    "candidate_voice_taxonomy_present": False,
    "control_input_sample_rate_hz": SAMPLE_RATE_HZ,
    "control_output_sample_rate_hz": SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": SAMPLE_FORMAT,
    "control_mode": "offline_whole_utterance",
    "control_incremental_streaming": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "audio_added": False,
    "ci_change": False,
    "client_installed": False,
    "corpus_added": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "model_loaded": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "shared_build_or_ci_change": False,
    "vendor_request_sent": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_candidate_model": False,
    "real_corpus": False,
    "real_weights": False,
    "release_claim": False,
    "runtime_invoked": False,
    "sync_generated": False,
    "task_local_only": True,
    "vendor_request_sent": False,
    "weights_downloaded": False,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No vendor credential, entitlement, API client, model, checkpoint, config, "
    "voice reference or runtime is downloaded, copied, loaded, imported or "
    "executed.",
    "No HTTP, WebSocket, gRPC, SDK or any other network request is sent to the "
    "vendor or anywhere else.",
    "No PyTorch, torchaudio, Transformers, NumPy, SoundFile, vocoder or TTS "
    "runtime is imported.",
    "No real audio, corpus, transcript, target voice, consent record or "
    "listening panel is consumed.",
    "No generated response voice, text/semantic preservation, speaker "
    "similarity, expressiveness realization, naturalness, latency, memory, RTF "
    "or device timing is measured here.",
    "The synthetic identity control is an accounting control, never vendor "
    "output and never generated speech.",
    "The vendor's source-reported time-to-first-byte figure is not reproduced "
    "or presented as a local measurement.",
    "No candidate sample rate, frame size, voice taxonomy, expressiveness "
    "scale, streaming protocol or output geometry is asserted.",
    "No sibling accent, voice-conversion, prosody, emotion or TTS result is "
    "attributed to this row.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "approved_vendor_access",
        "recorded_url": None,
        "credential_present": False,
        "entitlement_record": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "pinned_vendor_contract",
        "api_version": None,
        "model_version": None,
        "endpoint": None,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "vendor_terms_and_data_processing",
        "path": VENDOR_TERMS_PATH,
        "sha256": None,
        "data_processing_path": DATA_PROCESSING_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "generated_output_rights",
        "path": RIGHTS_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "target_voice_reference_and_consent",
        "path": VOICE_CONSENT_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "isolated_client_runtime",
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "voice_cohort",
        "path": COHORT_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "parity_vector",
        "path": PARITY_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "asset_storage",
    "channels",
    "comparison_baseline",
    "data_processing_record_path",
    "data_processing_record_sha256",
    "entitlement_path",
    "entitlement_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
    "target_expressiveness_milli",
    "target_voice_label",
    "task_kind",
    "variant",
    "vendor_contract_path",
    "vendor_contract_revision",
    "vendor_contract_sha256",
    "vendor_terms_path",
    "vendor_terms_sha256",
    "voice_consent_path",
    "voice_consent_sha256",
    "voice_reference_path",
    "voice_reference_sha256",
)

CALLER_FILE_PAIRS = (
    ("vendor_contract_path", "vendor_contract_sha256"),
    ("entitlement_path", "entitlement_sha256"),
    ("vendor_terms_path", "vendor_terms_sha256"),
    ("data_processing_record_path", "data_processing_record_sha256"),
    ("voice_reference_path", "voice_reference_sha256"),
    ("voice_consent_path", "voice_consent_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
)
CALLER_DIR_FIELDS = ("runtime_path",)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": CALLER_SCHEMA,
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "asset_storage": "external",
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_vendor_contract_revision_shape_"
        "geometry_task_kind_target_condition_and_offline_variant_only; do_"
        "not_import_execute_or_call_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_task_kind": TASK_KIND,
    "required_comparison_baseline": COMPARISON_BASELINE,
    "required_variant": CALLER_VARIANT,
    "required_vendor_contract_revision": None,
    "vendor_contract_revision_pin_available": False,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_input_hz": None,
        "sample_rate_output_hz": None,
        "status": "unestablished",
    },
    "target_condition": {
        "label_required": True,
        "label_regex": "^[a-z][a-z0-9_]{1,63}$",
        "expressiveness_milli_min": 1,
        "expressiveness_milli_max": MAX_TARGET_EXPRESSIVENESS,
        "voice_taxonomy_asset_required": True,
    },
    "notes": (
        "Every vendor contract, entitlement, terms record, data-processing "
        "record, voice reference, voice consent, rights record and runtime lock "
        "must exist at an absolute path and match its declared SHA-256 before a "
        "caller may send a request. The package never imports, executes or "
        "calls the caller's client. No vendor contract revision is pinned "
        "because none was supplied."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "vendor_entitlement_and_credentials_absent",
        "state": "absent",
        "requirement": (
            "Supply approved vendor access: a written entitlement, an "
            "account/project identifier and caller-owned credentials at a "
            "declared path; the workspace contains no credential, entitlement "
            "or account record for Hume Octave."),
    },
    {
        "id": "pinned_vendor_contract_and_model_version_absent",
        "state": "absent",
        "requirement": (
            "Pin the exact API version, endpoint, model/voice version and "
            "request/response schema as an immutable contract with SHA-256; the "
            "merged record names only the product page, so no contract "
            "revision, endpoint identity or model digest exists."),
    },
    {
        "id": "vendor_terms_data_processing_and_output_rights_uncleared",
        "state": "absent",
        "requirement": (
            "Clear vendor service terms, data-processing/retention terms, "
            "training use, generated-output ownership, redistribution, "
            "product-use and jurisdiction requirements with complete notices; "
            "no terms, data-processing record or output-rights record exists."),
    },
    {
        "id": "consent_cleared_target_voice_absent",
        "state": "absent",
        "requirement": (
            "Supply a consent-cleared target/reference voice and permitted "
            "text, speaker, language and output-use records; no target voice "
            "or consent record is staged."),
    },
    {
        "id": "isolated_client_runtime_and_network_boundary_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned client runtime with a complete "
            "package lock at " + RUNTIME_LOCK_PATH + ", a recorded platform "
            "and an explicit network/egress boundary; no environment, package "
            "pin or lock exists."),
    },
    {
        "id": "voice_cohort_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared task-matched cohort with language, "
            "speaker, text and expressive-target groups, transcripts, "
            "held-out splits and an approved vendor-output parity vector; no "
            "cohort or parity manifest exists."),
    },
    {
        "id": "geometry_alignment_and_streaming_absent",
        "state": "absent",
        "requirement": (
            "Establish the exact output rate, channels, chunking/streaming "
            "mode, content delay, first-output/tail timing, network-inclusive "
            "latency and host memory budget; only a vendor-reported "
            "time-to-first-byte value exists and it is source-reported, not "
            "reproduced here."),
    },
    {
        "id": "opt_in_adapter_intake_and_review_absent",
        "state": "absent",
        "requirement": (
            "Complete opt-in adapter intake, descriptor and public-surface "
            "review, independent exact-head review and explicit release "
            "approval; no adapter, descriptor or review exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_artifact_identity",
        "The exact vendor contract, API version, endpoint, model/voice version, "
        "schema and entitlement identity match immutable digests.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned client runtime with a complete lock and an "
        "explicit network boundary is admitted on a recorded platform.",
    ),
    (
        "artifact_rights_consent_and_output_use",
        "Vendor terms, data-processing/retention, training use, generated-"
        "output ownership, voice consent, redistribution and product-use "
        "rights are cleared with complete notices.",
    ),
    (
        "exact_reference_parity",
        "An approved vendor output and its local identity control match a "
        "frozen vector on one frozen input, text and configuration.",
    ),
    (
        "frozen_voice_cohort",
        "A rights-cleared, label-complete, task-matched held-out cohort covers "
        "language, speaker, text and expressive-target groups.",
    ),
    (
        "content_identity_expressiveness_naturalness_results",
        "Independent results separate text/semantic preservation, voice "
        "identity or similarity, target expressiveness realization and "
        "naturalness.",
    ),
    (
        "alignment_timing_and_streaming",
        "Alignment, first-output/tail timing, chunk/stream behaviour, network-"
        "inclusive latency, memory and device deadlines are measured for the "
        "exact runtime.",
    ),
    (
        "opt_in_adapter_intake_and_release",
        "Opt-in provider/adapter intake, descriptor review, independent "
        "exact-head review and explicit default/release approval are complete.",
    ),
)

VOICE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "permitted_source_and_target_references",
        "Freeze permitted text, input and target voice references with rights "
        "and consent.",
        "absent",
    ),
    (
        "task_language_and_speaker_groups",
        "Freeze task, language, speaker and expressive-target groups for the "
        "cohort.",
        "absent",
    ),
    (
        "text_and_semantic_preservation",
        "Preserve text and semantic content as its own outcome.",
        "not_measured",
    ),
    (
        "identity_similarity",
        "Measure voice identity or similarity as a separate outcome.",
        "not_measured",
    ),
    (
        "target_voice_and_expressiveness_realization",
        "Measure the intended target voice and expressiveness separately from "
        "content and identity.",
        "not_measured",
    ),
    (
        "naturalness",
        "Measure naturalness as a separate outcome.",
        "not_measured",
    ),
    (
        "alignment_and_output_timing",
        "Record alignment, first-output and tail timing for the exact runtime.",
        "structural_only",
    ),
    (
        "consent_reference_and_output_use",
        "Treat consent, reference availability and output use as independent "
        "gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": CANDIDATE_RECORD_PATH,
    "source_sha256": SOURCE_PINS[CANDIDATE_RECORD_PATH],
    "record": CANDIDATE_RECORD,
    "record_name": TITLE,
    "record_status": "out of scope",
    "finding": (
        "Cloud text-to-speech, not input microphone enhancement; vendor TTFB "
        "is not local."),
    "comparison_baseline": "Local identity; cloud generated response voice",
    "report_paths": list(CANDIDATE_REPORT_PATHS),
    "vendor_reported_ttfb_ms": 300,
    "vendor_timing_label": "vendor_reported_not_measured_here",
    "sibling_context_not_attributed": [
        "No CosyVoice, Kokoro, StyleTTS 2, F5-TTS, Chatterbox or any other "
        "sibling TTS result is attributed to this row.",
        "No accent-conversion, emotion/prosody or voice-conversion result is "
        "attributed to this row.",
        "The research audit did not run a vendor request for this row.",
        "The vendor-stated time-to-first-byte is a product-page claim, not a "
        "local network or device measurement.",
    ],
    "notes": (
        "No vendor credential, entitlement, contract, cohort or output was "
        "acquired. No duration, WER, similarity, expressiveness, naturalness, "
        "latency or RTF value is attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_identity_acceptance_plan_not_vendor_output")

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
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_wrong_task_kind_tts",
    "manifest_wrong_task_kind_enhancement",
    "manifest_wrong_baseline",
    "manifest_channels_zero",
    "manifest_channels_float",
    "manifest_rate_below_range",
    "manifest_rate_above_range",
    "manifest_rate_bool",
    "manifest_empty_voice_label",
    "manifest_bad_voice_label",
    "manifest_expressiveness_zero",
    "manifest_expressiveness_above",
    "manifest_expressiveness_bool",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
    "manifest_missing_consent",
    "manifest_wrong_storage",
    "target_not_object",
    "target_missing_expressiveness",
    "target_unknown_label",
    "target_nonidentity_label",
    "target_expressiveness_not_full",
    "target_wrong_task_kind",
    "target_wrong_variant",
    "target_wrong_baseline",
)

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
LABEL_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
VENDOR_REVISION_PATTERN = re.compile(VENDOR_CONTRACT_REVISION_PATTERN)


class ReferenceRejection(ValueError):
    """Deterministic rejection that never mutates accepted state."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _reject_if_float(value: Any, label: str) -> None:
    if isinstance(value, float):
        raise ReferenceRejection("noncanonical_float:" + label)


def _check_canonical_value(value: Any, label: str) -> None:
    if value is None or isinstance(value, bool) or isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_canonical_value(item, label + "[" + str(index) + "]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ReferenceRejection("noncanonical_key:" + label)
            _check_canonical_value(item, label + "." + key)
        return
    raise ReferenceRejection("noncanonical_type:" + label)


def canonical_text(value: Any) -> str:
    _check_canonical_value(value, "root")
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def _unique_json_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReferenceRejection("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_json_constant(token: str) -> None:
    raise ReferenceRejection("nonfinite_json_constant:" + token)


def load_strict_json_text(text: str) -> Any:
    if not isinstance(text, str):
        raise ReferenceRejection("json_text_not_string")
    if text.startswith("\ufeff"):
        raise ReferenceRejection("json_bom")
    try:
        return json.loads(text, object_pairs_hook=_unique_json_object,
                          parse_constant=_reject_json_constant)
    except ReferenceRejection:
        raise
    except (ValueError, TypeError) as error:
        raise ReferenceRejection("invalid_json:" + type(error).__name__) from error


def load_strict_json(path: Path) -> Any:
    try:
        payload = Path(path).read_bytes()
    except OSError as error:
        raise ReferenceRejection("missing_file:" + str(path)) from error
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReferenceRejection("invalid_utf8:" + str(path)) from error
    return load_strict_json_text(text)


def require_json_object(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ReferenceRejection("json_not_object")
    return value


def load_strict_json_object_text(text: str) -> Dict[str, Any]:
    return require_json_object(load_strict_json_text(text))


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Fixed-path source, vendor-asset and absence audit.
# ---------------------------------------------------------------------------

def _read_git_head(repository: Path) -> Optional[str]:
    marker = repository / ".git"
    if not marker.exists():
        return None
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if not text.startswith("gitdir:"):
            return None
        target = Path(text.split(":", 1)[1].strip())
        if not target.is_absolute():
            target = (repository / target).resolve()
    else:
        target = marker
    head_path = target / "HEAD"
    if not head_path.is_file():
        return None
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not head.startswith("ref: "):
        return head if COMMIT_PATTERN.fullmatch(head) else None
    ref = head.split(":", 1)[1].strip()
    ref_path = target / ref
    if ref_path.is_file():
        try:
            value = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return value if COMMIT_PATTERN.fullmatch(value) else None
    packed = target / "packed-refs"
    if packed.is_file():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                digest, _, name = line.partition(" ")
                if name == ref and COMMIT_PATTERN.fullmatch(digest):
                    return digest
        except OSError:
            return None
    return None


def _license_candidates(repository: Path) -> List[str]:
    found: List[str] = []
    if not repository.is_dir():
        return found
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING",
                 "COPYING.md", "COPYING.txt", "NOTICE"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_SOURCE_PATH,
        SOURCE_ROOT / "data/checkouts/hume_octave",
        SOURCE_ROOT / "data/checkouts/octave",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "hume-octave",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "hume_octave",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_WEIGHTS_PATH,
        SOURCE_ROOT / "data/models/hume_octave",
        SOURCE_ROOT / "data/models/octave",
        SOURCE_ROOT / "data/weights/hume-octave",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "hume-octave/checkpoints",
    ]


ABSENCE_PROBES: Tuple[str, ...] = (
    "data/checkouts/hume-octave",
    "data/checkouts/hume_octave",
    "data/checkouts/octave",
    "data/models/hume-octave",
    "data/models/hume_octave",
    "data/models/octave",
    "data/weights/hume-octave",
    "data/manifests/hume-octave-api-contract.json",
    "data/credentials/hume-octave-entitlement.json",
    "data/rights/hume-octave-vendor-terms.json",
    "data/rights/hume-octave-data-processing.json",
    "data/rights/hume-octave-voice-consent.json",
    "data/rights/hume-octave-rights.json",
    "data/envs/hume-octave",
    "data/envs/hume-octave/requirements.lock",
    "data/runs/hume-octave-cohort/manifest.json",
    "data/runs/hume-octave-parity/manifest.json",
    TASK_PREFIX + "reference_output.wav",
    TASK_PREFIX + "cohort",
)


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def audit_assets() -> Dict[str, Any]:
    source_paths = _source_candidates()
    present_sources = [path for path in source_paths if path.is_dir()]
    repository = present_sources[0] if present_sources else None
    revision = _read_git_head(repository) if repository is not None else None
    licenses = _license_candidates(repository) if repository is not None else []
    weight_paths = _weights_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    vendor_contract = SOURCE_ROOT / VENDOR_CONTRACT_PATH
    entitlement = SOURCE_ROOT / ENTITLEMENT_PATH
    vendor_terms = SOURCE_ROOT / VENDOR_TERMS_PATH
    data_processing = SOURCE_ROOT / DATA_PROCESSING_PATH
    voice_consent = SOURCE_ROOT / VOICE_CONSENT_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    reference_audio = SOURCE_ROOT / (TASK_PREFIX + "reference_output.wav")
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": False,
        "source_revision_matches": False,
        "source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.is_dir()}
            for path in source_paths
        ],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "vendor_contract_present": vendor_contract.is_file(),
        "entitlement_present": entitlement.is_file(),
        "vendor_terms_present": vendor_terms.is_file(),
        "data_processing_present": data_processing.is_file(),
        "voice_consent_present": voice_consent.is_file(),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "reference_audio_present": reference_audio.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "task_kind": TASK_KIND,
            "comparison_baseline": COMPARISON_BASELINE,
            "geometry_status": "unestablished",
            "target_condition_status": "unestablished",
            "vendor_contract_revision": None,
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
        },
    }


def task_row_identity() -> Dict[str, Any]:
    path = SOURCE_ROOT / TASK_BOARD_REL
    if not path.is_file():
        raise ReferenceRejection("task board is unavailable at " + TASK_BOARD_REL)
    try:
        document = require_json_object(load_strict_json(path))
    except (OSError, UnicodeDecodeError) as error:
        raise ReferenceRejection("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ReferenceRejection("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK_ID or stable["component"] != COMPONENT:
        raise ReferenceRejection("linked task row identity mismatch")
    if stable["repository"] != REPOSITORY or stable["mode"] != MODE:
        raise ReferenceRejection("linked task row repository/mode mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise ReferenceRejection("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise ReferenceRejection("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise ReferenceRejection("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise ReferenceRejection("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise ReferenceRejection("claim reviewer mismatch")
    return {
        "source": TASK_BOARD_REL,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_text(stable).encode("utf-8")),
        "full_tasks_json_hashed": False,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "note": (
            "Only stable linked-row fields are read and gated. The mutable "
            "full plan/swarm/TASKS.json is never hashed, pinned or used as a "
            "digest source."),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic PCM, identity control and target admission.
# ---------------------------------------------------------------------------

def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def _triangle(index: int, period: int) -> float:
    """Zero-mean triangle in [-1, 1]; integer phase arithmetic only."""
    phase = index % period
    return (2 * abs(2 * phase - period) - period) / float(period)


def synthetic_source_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x13579BDF
    amplitude = CONTROL_VOICED_AMPLITUDE_MICRO / MICRO_SCALE
    noise_amplitude = CONTROL_NOISE_AMPLITUDE_MICRO / MICRO_SCALE
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        if index < CONTROL_LEAD_SAMPLES or index >= CONTROL_TAIL_START:
            value = 0.0
        elif index < CONTROL_VOICED_END:
            rising = (index - CONTROL_LEAD_SAMPLES) * MICRO_SCALE
            falling = (CONTROL_VOICED_END - index) * MICRO_SCALE
            ramp = min(MICRO_SCALE, rising // 2000, falling // 2000)
            value = (amplitude * _triangle(index, CONTROL_VOICED_PERIOD)
                     * (ramp / MICRO_SCALE) + noise_amplitude * noise)
        else:
            value = noise_amplitude * noise
        samples.append(value)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise ReferenceRejection("invalid_sample_rate")
    if sample_rate_hz != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_control_sample_rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("invalid_channels")
    if channels != CHANNELS:
        raise ReferenceRejection("only_mono_is_supported")
    if not isinstance(signal, (list, tuple)):
        raise ReferenceRejection("signal_must_be_a_sample_sequence")
    if not signal:
        raise ReferenceRejection("signal_must_be_nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise ReferenceRejection("signal_exceeds_the_evidence_cap")
    checked: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ReferenceRejection(f"sample_{index}_is_not_numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise ReferenceRejection(f"sample_{index}_is_not_finite")
        if value < -1.0 or value > 1.0:
            raise ReferenceRejection(f"sample_{index}_is_outside_finite_range")
        checked.append(value)
    return checked


def _quantized_micro(values: Sequence[float]) -> List[int]:
    return [int(round(value * MICRO_SCALE)) for value in values]


def pcm_summary(signal: Sequence[float],
                sample_rate_hz: int = SAMPLE_RATE_HZ) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_micro": int(round(peak * MICRO_SCALE)),
        "nonfinite_samples": 0,
        "digest_basis": "int_micro_quantized_samples",
        "quantization_micro": MICRO_SCALE,
        "sha256": object_digest(_quantized_micro(values)),
    }


def identity_transform(signal: Any) -> List[float]:
    """The task's declared comparison baseline: local identity, no change."""
    return list(validate_pcm(signal))


def admit_target_condition(condition: Any) -> Dict[str, Any]:
    """Fail closed: only the local identity control may be admitted."""
    if not isinstance(condition, dict):
        raise ReferenceRejection("target_condition_not_object")
    expected = {"comparison_baseline", "target_voice_label",
                "target_expressiveness_milli", "task_kind", "variant"}
    present = set(condition)
    if present != expected:
        missing = sorted(expected - present)
        extra = sorted(present - expected)
        raise ReferenceRejection(
            "target_condition_keys_mismatch:"
            + ",".join(missing + extra))
    if condition["task_kind"] != TASK_KIND:
        raise ReferenceRejection("target_condition_wrong_task_kind")
    if condition["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("target_condition_wrong_variant")
    if condition["comparison_baseline"] != COMPARISON_BASELINE:
        raise ReferenceRejection("target_condition_wrong_baseline")
    label = condition["target_voice_label"]
    if not isinstance(label, str) or not LABEL_PATTERN.fullmatch(label):
        raise ReferenceRejection("target_condition_bad_label")
    expressiveness = condition["target_expressiveness_milli"]
    if isinstance(expressiveness, bool) or not isinstance(expressiveness, int):
        raise ReferenceRejection(
            "target_condition_expressiveness_not_integer")
    if expressiveness < 1 or expressiveness > MAX_TARGET_EXPRESSIVENESS:
        raise ReferenceRejection(
            "target_condition_expressiveness_out_of_range")
    if (label != IDENTITY_LABEL
            or expressiveness != TARGET_EXPRESSIVENESS_FULL):
        raise ReferenceRejection(
            "absent_cloud_runtime_and_entitlement:"
            + label + ":" + str(expressiveness))
    return {
        "accepted": True,
        "identity_control": True,
        "generation_performed": False,
        "target_voice_label": label,
        "target_expressiveness_milli": expressiveness,
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "qualification_effect": "none",
        "reason": (
            "local identity is the declared comparison baseline; no vendor "
            "entitlement, pinned contract, voice consent or runtime exists"),
    }


def identity_target_condition() -> Dict[str, Any]:
    return {
        "comparison_baseline": COMPARISON_BASELINE,
        "target_voice_label": IDENTITY_LABEL,
        "target_expressiveness_milli": TARGET_EXPRESSIVENESS_FULL,
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
    }


def duration_accounting(source_samples: int, output_samples: int
                        ) -> Dict[str, Any]:
    for value in (source_samples, output_samples):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ReferenceRejection("sample_count_must_be_integer")
        if value <= 0:
            raise ReferenceRejection("sample_count_must_be_positive")
    source_duration = Fraction(source_samples, SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, SAMPLE_RATE_HZ)
    ratio = output_duration / source_duration
    return {
        "source_samples": source_samples,
        "output_samples": output_samples,
        "source_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "duration_ratio_interpretation": (
            "output_duration_divided_by_source_duration"),
        "sample_delta": output_samples - source_samples,
    }


def alignment_accounting(output_samples: int) -> Dict[str, Any]:
    if isinstance(output_samples, bool) or not isinstance(output_samples, int):
        raise ReferenceRejection("output_sample_count_must_be_integer")
    if output_samples <= 0:
        raise ReferenceRejection("output_sample_count_must_be_positive")
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "incremental_streaming": False,
        "first_output_sample": 0,
        "first_output_delay_samples": 0,
        "tail_samples": output_samples,
        "whole_clip_required": True,
        "measured": False,
        "network_inclusive_latency_measured": False,
        "note": (
            "No vendor runtime or entitlement exists, so alignment is not "
            "measured. This declares the offline-only accounting boundary; it "
            "is not device, network or first-output timing."),
    }


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent."""
    root = "/nonexistent/hume-octave-evidence-fixture"
    digest = "0" * 64
    return {
        "asset_storage": "external",
        "channels": CHANNELS,
        "comparison_baseline": COMPARISON_BASELINE,
        "data_processing_record_path": root + "/data-processing.json",
        "data_processing_record_sha256": digest,
        "entitlement_path": root + "/entitlement.json",
        "entitlement_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
        "target_expressiveness_milli": 700,
        "target_voice_label": "identity",
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
        "vendor_contract_path": root + "/api-contract.json",
        "vendor_contract_revision": "2026-11-01",
        "vendor_contract_sha256": digest,
        "vendor_terms_path": root + "/vendor-terms.json",
        "vendor_terms_sha256": digest,
        "voice_consent_path": root + "/consent.json",
        "voice_consent_sha256": digest,
        "voice_reference_path": root + "/target.wav",
        "voice_reference_sha256": digest,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package."""
    assignments = {
        "vendor_contract_path": TASK_DIR / "reference.py",
        "entitlement_path": TASK_DIR / "run.py",
        "vendor_terms_path": TASK_DIR / "LICENSES.md",
        "data_processing_record_path": TASK_DIR / "README.md",
        "voice_reference_path": TASK_DIR / "reference.py",
        "voice_consent_path": TASK_DIR / "contract.json.license",
        "rights_record_path": TASK_DIR / "verify.py",
        "runtime_lock_path": TASK_DIR / "test_reference.py",
    }
    manifest: Dict[str, Any] = {
        "asset_storage": "external",
        "channels": CHANNELS,
        "comparison_baseline": COMPARISON_BASELINE,
        "runtime_path": str(SDK_ROOT),
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
        "target_expressiveness_milli": 700,
        "target_voice_label": "identity",
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
        "vendor_contract_revision": "2026-11-01",
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = file_digest(path)
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
                raise ReferenceRejection("asset_exceeds_the_evidence_cap")
            digest.update(chunk)
    return digest.hexdigest()


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReferenceRejection("manifest_" + field + "_must_be_integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise ReferenceRejection("manifest_" + field + "_outside_range")
    return value


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("manifest_must_be_object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise ReferenceRejection("manifest_missing_fields:" + ",".join(missing))
    if extra:
        raise ReferenceRejection("manifest_unknown_fields:" + ",".join(extra))
    if manifest["asset_storage"] != "external":
        raise ReferenceRejection("manifest_asset_storage_must_be_external")
    if manifest["task_kind"] != TASK_KIND:
        raise ReferenceRejection("manifest_wrong_task_kind")
    if manifest["comparison_baseline"] != COMPARISON_BASELINE:
        raise ReferenceRejection("manifest_wrong_baseline")
    if manifest["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("manifest_wrong_variant")
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not re.fullmatch(
                r"[0-9a-f]{64}", value):
            raise ReferenceRejection(
                "manifest_" + field + "_is_not_lowercase_sha256")
    for path_field, _ in CALLER_FILE_PAIRS:
        value = manifest[path_field]
        if not isinstance(value, str) or not value:
            raise ReferenceRejection(
                "manifest_" + path_field + "_must_be_path")
        if not Path(value).is_absolute():
            raise ReferenceRejection(
                "manifest_" + path_field + "_must_be_absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise ReferenceRejection(
                "manifest_" + field + "_must_be_path")
        if not Path(value).is_absolute():
            raise ReferenceRejection(
                "manifest_" + field + "_must_be_absolute")
    revision = manifest["vendor_contract_revision"]
    if not isinstance(revision, str) or not VENDOR_REVISION_PATTERN.fullmatch(
            revision):
        raise ReferenceRejection(
            "manifest_vendor_contract_revision_invalid")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("manifest_channels_must_be_integer")
    if channels != CHANNELS:
        raise ReferenceRejection("manifest_channels_mismatch")
    input_rate = _rate_value(manifest, "sample_rate_input_hz")
    output_rate = _rate_value(manifest, "sample_rate_output_hz")
    label = manifest["target_voice_label"]
    if not isinstance(label, str) or not LABEL_PATTERN.fullmatch(label):
        raise ReferenceRejection("manifest_target_voice_label_invalid")
    expressiveness = manifest["target_expressiveness_milli"]
    if isinstance(expressiveness, bool) or not isinstance(expressiveness, int):
        raise ReferenceRejection(
            "manifest_target_expressiveness_not_integer")
    if expressiveness < 1 or expressiveness > MAX_TARGET_EXPRESSIVENESS:
        raise ReferenceRejection(
            "manifest_target_expressiveness_out_of_range")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise ReferenceRejection("manifest_" + field + "_directory_missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise ReferenceRejection("manifest_" + path_field + "_missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise ReferenceRejection(
                "manifest_" + path_field + "_sha256_mismatch")
        total_bytes += path.stat().st_size
    return {
        "accepted": True,
        "vendor_contract_revision": revision,
        "vendor_contract_revision_pin_available": False,
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "sample_rate_input_hz": input_rate,
        "sample_rate_output_hz": output_rate,
        "channels": CHANNELS,
        "target_voice_label": label,
        "target_expressiveness_milli": expressiveness,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "audio_read": False,
        "network_used": False,
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    good_source = synthetic_source_pcm()
    good_manifest = _shape_only_manifest()

    def case(case_id: str, action) -> Dict[str, Any]:
        try:
            action()
        except ReferenceRejection as error:
            return {"case": case_id, "result": "rejected",
                    "reason": error.code}
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

    def wrong_target(key: str, value: Any):
        condition = identity_target_condition()
        condition[key] = value
        return lambda: admit_target_condition(condition)

    def drop_target(key: str):
        condition = identity_target_condition()
        condition.pop(key)
        return lambda: admit_target_condition(condition)

    existing = _existing_file_manifest()
    nonidentity = identity_target_condition()
    nonidentity["target_voice_label"] = "expressive"
    nonidentity["target_expressiveness_milli"] = 800
    reduced = identity_target_condition()
    reduced["target_expressiveness_milli"] = 500

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_source, SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("vendor_contract_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "vendor_contract_path", "contracts/octave.json")),
        ("manifest_bad_sha", wrong("vendor_contract_sha256", "ABC")),
        ("manifest_short_revision", wrong(
            "vendor_contract_revision", "")),
        ("manifest_nonhex_revision", wrong(
            "vendor_contract_revision", "bad revision!")),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_wrong_task_kind_tts", wrong(
            "task_kind", "text_to_speech")),
        ("manifest_wrong_task_kind_enhancement", wrong(
            "task_kind", "microphone_input_enhancement")),
        ("manifest_wrong_baseline", wrong(
            "comparison_baseline", "vendor_generated_voice")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_channels_float", wrong("channels", 1.0)),
        ("manifest_rate_below_range", wrong("sample_rate_input_hz", 4000)),
        ("manifest_rate_above_range", wrong("sample_rate_output_hz", 384000)),
        ("manifest_rate_bool", wrong("sample_rate_output_hz", True)),
        ("manifest_empty_voice_label", wrong("target_voice_label", "")),
        ("manifest_bad_voice_label", wrong(
            "target_voice_label", "Expressive!")),
        ("manifest_expressiveness_zero", wrong(
            "target_expressiveness_milli", 0)),
        ("manifest_expressiveness_above", wrong(
            "target_expressiveness_milli", MAX_TARGET_EXPRESSIVENESS + 1)),
        ("manifest_expressiveness_bool", wrong(
            "target_expressiveness_milli", True)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, vendor_contract_path=(
                "/nonexistent/hume-octave/api-contract.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/hume-octave/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, vendor_contract_sha256="0" * 64))),
        ("manifest_missing_consent", lambda: validate_caller_manifest(
            dict(existing, voice_consent_path=(
                "/nonexistent/hume-octave/consent.json")))),
        ("manifest_wrong_storage", wrong("asset_storage", "vendored")),
        ("target_not_object", lambda: admit_target_condition([])),
        ("target_missing_expressiveness", drop_target(
            "target_expressiveness_milli")),
        ("target_unknown_label", wrong_target(
            "target_voice_label", "not_a_real_label_")),
        ("target_nonidentity_label", lambda: admit_target_condition(
            nonidentity)),
        ("target_expressiveness_not_full", lambda: admit_target_condition(
            reduced)),
        ("target_wrong_task_kind", wrong_target(
            "task_kind", "text_to_speech")),
        ("target_wrong_variant", wrong_target(
            "variant", "incremental_streaming")),
        ("target_wrong_baseline", wrong_target(
            "comparison_baseline", "vendor_generated_voice")),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_count_mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_ids_mismatch")
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = identity_transform(source)
    source_summary = pcm_summary(source)
    output_summary = pcm_summary(output)
    duration = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    accepted = admit_target_condition(identity_target_condition())
    rejected_names: List[str] = []
    for label, expressiveness in (
            ("expressive", 800), ("calm", 500), ("narration", 1000)):
        condition = identity_target_condition()
        condition["target_voice_label"] = label
        condition["target_expressiveness_milli"] = expressiveness
        try:
            admit_target_condition(condition)
        except ReferenceRejection:
            rejected_names.append(label)
    if len(rejected_names) != 3:
        raise ReferenceRejection("nonidentity_target_not_rejected")
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
            "control_sample_format": SAMPLE_FORMAT,
            "candidate_geometry_status": "unestablished",
            "candidate_geometry_asserted": False,
            "target_condition_status": "unestablished",
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "source_pcm": source_summary,
        "identity_output_pcm": output_summary,
        "identity_baseline": {
            "baseline": COMPARISON_BASELINE,
            "generation_performed": False,
            "sample_count_equal": (
                source_summary["samples"] == output_summary["samples"]),
            "duration_equal": (
                source_summary["duration_s"] == output_summary["duration_s"]),
            "digest_equal": (
                source_summary["sha256"] == output_summary["sha256"]),
            "peak_bounded": output_summary["peak_micro"] <= MICRO_SCALE,
            "content_delay_samples": 0,
            "qualification_effect": "none",
        },
        "target_condition_admission": {
            "identity_control_accepted": accepted["accepted"],
            "identity_control": accepted["identity_control"],
            "accepted_labels": [IDENTITY_LABEL],
            "rejected_examples": rejected_names,
            "nonidentity_rejected": len(rejected_names) == 3,
            "generation_performed": False,
            "requires_absent_vendor_runtime": True,
            "qualification_effect": "none",
        },
        "duration": duration,
        "alignment": alignment,
        "acceptance_outcomes": [
            {
                "id": "text_and_semantic_preservation",
                "measured": False,
                "value": None,
                "reason": "no vendor output, transcript truth or cohort",
            },
            {
                "id": "voice_identity_similarity",
                "measured": False,
                "value": None,
                "reason": (
                    "no permitted voice reference or speaker embedder "
                    "runtime"),
            },
            {
                "id": "target_voice_and_expressiveness_realization",
                "measured": False,
                "value": None,
                "reason": (
                    "no voice taxonomy, expressiveness scale or vendor "
                    "output"),
            },
            {
                "id": "naturalness",
                "measured": False,
                "value": None,
                "reason": "no authorized listening panel",
            },
            {
                "id": "alignment_and_output_timing",
                "measured": False,
                "value": None,
                "reason": "structural offline accounting only; no network clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "manifest_channels_zero", "manifest_channels_float",
                "manifest_rate_below_range", "manifest_rate_above_range",
                "manifest_rate_bool", "manifest_empty_voice_label",
                "manifest_bad_voice_label", "manifest_expressiveness_zero",
                "manifest_expressiveness_above",
                "manifest_expressiveness_bool",
                "target_unknown_label", "target_expressiveness_not_full"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory", "manifest_missing_consent",
                "target_missing_expressiveness"],
            "fail_closed_target_rejected": [
                "target_nonidentity_label", "target_wrong_task_kind",
                "target_wrong_variant", "target_wrong_baseline"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic local identity accounting control only at the public v0 "
            "geometry. It is not vendor output, not generated speech, not "
            "transformed audio, not a quality or timing result and cannot "
            "qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision"] is not None
        and observed["license_file_present"]
        and observed["weights_present"]
        and observed["vendor_contract_present"]
        and observed["entitlement_present"]
        and observed["vendor_terms_present"]
        and observed["data_processing_present"]
        and observed["voice_consent_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["source_checkout_present"]:
        result = "source_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "source_present": observed["source_checkout_present"],
        "source_revision": observed["source_revision"],
        "source_revision_pin_available": False,
        "license_present": observed["license_file_present"],
        "weights_present": observed["weights_present"],
        "vendor_contract_present": observed["vendor_contract_present"],
        "entitlement_present": observed["entitlement_present"],
        "vendor_terms_present": observed["vendor_terms_present"],
        "data_processing_present": observed["data_processing_present"],
        "voice_consent_present": observed["voice_consent_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "reference_audio_present": observed["reference_audio_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No vendor contract, entitlement, terms, data-processing record, "
            "voice consent, runtime, licence, rights record, cohort or parity "
            "manifest was observed."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]
    profile_items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in VOICE_REQUIREMENTS
    ]
    return {
        "schema_id": REPORT_SCHEMA,
        "task_id": TASK_ID,
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
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "real_candidate_metrics": False,
            "reason": (
                "Hume Octave is a vendor-hosted cloud text-to-speech service. "
                "No entitlement, credential, pinned API contract, terms or "
                "data-processing record, consent-cleared voice, isolated "
                "client runtime, cohort, parity vector or exact geometry "
                "exists, so every release gate remains blocked."),
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "board_row": identity,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "candidate": {
            "name": TITLE,
            "record": "candidate_matrix.csv record " + str(CANDIDATE_RECORD),
            "record_name": TITLE,
            "record_status": "out of scope",
            "candidate_kind": "cloud_text_to_speech_service",
            "source_record": CANDIDATE_RECORD_PATH,
            "source_record_sha256": SOURCE_PINS[CANDIDATE_RECORD_PATH],
            "report_paths": list(CANDIDATE_REPORT_PATHS),
            "baseline": "Local identity; cloud generated response voice",
            "finding": (
                "Cloud text-to-speech, not input microphone enhancement; "
                "vendor TTFB is not local."),
            "source_present": False,
            "source_revision": None,
            "source_sha256": None,
            "weights_present": False,
            "weights_sha256": None,
            "vendor_contract_present": False,
            "entitlement_present": False,
            "vendor_terms_present": False,
            "data_processing_present": False,
            "runtime_present": False,
            "voice_taxonomy_present": False,
            "consent_cleared_voice_present": False,
            "geometry_documented": False,
            "network_protocol_documented": False,
            "implemented_here": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "evidence_status": "blocked",
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "licensing": {
            "package_license": "Apache-2.0",
            "upstream_license_reported": None,
            "license_text_staged": False,
            "weights_terms_staged": False,
            "vendor_terms_staged": False,
            "data_processing_staged": False,
            "training_data_statement_staged": False,
            "target_voice_consent_staged": False,
            "output_use_reviewed": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "corpus_rights_reviewed": False,
            "review_status": "blocked",
        },
        "voice_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural accounting passes, but no vendor runtime, "
                "permitted reference set, voice taxonomy, consent record, "
                "rights-cleared cohort or approved parity exists, so the voice "
                "profile is not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "identity_baseline_exact": (
                control["identity_baseline"]["digest_equal"]),
            "nonidentity_target_rejected_before_processing": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "network_request_sent": False,
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "release_gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_condition": (
            "Obtain approved vendor entitlement and credentials; pin the exact "
            "API version, endpoint, model/voice version and request/response "
            "schema with digests; clear vendor terms, data-processing and "
            "retention, training use, generated-output ownership, "
            "redistribution and product-use rights; secure a consent-cleared "
            "target voice; admit an isolated hash-pinned client runtime with a "
            "recorded platform and network boundary; freeze a rights-cleared "
            "task-matched cohort and parity vector; reproduce vendor output "
            "against the local identity control; measure content, identity, "
            "expressiveness, naturalness, alignment, network-inclusive timing "
            "and memory; and complete opt-in adapter intake. Until every "
            "condition is closed the candidate stays DEFER, incomplete and "
            "not qualified."),
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            VENDOR_CONTRACT_PATH,
            ENTITLEMENT_PATH,
            VENDOR_TERMS_PATH,
            DATA_PROCESSING_PATH,
            VOICE_CONSENT_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
            RUNTIME_ENV_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model, audio or network runtime "
            "is imported.",
            "Fixed workspace paths are probed for vendor contract, "
            "entitlement, terms, data processing, consent, runtime, rights and "
            "cohort presence.",
            "No client is installed and no request is sent.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load or timing "
            "run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline; no JSON floats"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract(report: Dict[str, Any], report_digest: str) -> Dict[str, Any]:
    sidecar_digest = sha256_bytes((report_digest + "\n").encode("utf-8"))
    return {
        "SPDX-" "FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-" "License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "version": VERSION,
        "mode": MODE,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "write_scope": TASK_PREFIX,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": report["qualification"],
        "format": report["format"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "candidate": report["candidate"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": report["caller_asset_contract"],
        "licensing": report["licensing"],
        "voice_profile": report["voice_profile"],
        "reference_protocol": report["reference_protocol"],
        "controls": {
            "identity_baseline_exact": report["controls"][
                "identity_baseline_exact"],
            "nonidentity_target_rejected_before_processing": report[
                "controls"]["nonidentity_target_rejected_before_processing"],
            "adverse_all_rejected": report["controls"]["adverse_all_rejected"],
            "adverse_case_count": len(report["controls"]["adverse"]),
            "network_request_sent": False,
        },
        "board_row": report["board_row"],
        "task_row_identity": report["task_row_identity"],
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
        "gates": report["gates"],
        "release_gates": report["release_gates"],
        "exact_blockers": report["exact_blockers"],
        "reopen_condition": report["reopen_condition"],
        "reopen_conditions": report["reopen_conditions"],
        "negative_claims": report["non_claims"],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "determinism": report["determinism"],
        "reproduction": {
            "cold_start_regenerations": 3,
            "generator": "run.py",
            "check_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check",
            "verify_command": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no vendor credential, entitlement, client, model, voice, "
            "contract or runtime is downloaded, copied, loaded or executed",
            "no network request is sent to the vendor or anywhere else",
            "only the local identity control is admitted; every synthesized "
            "voice or expressiveness target fails closed because the vendor "
            "runtime and entitlement are absent",
            "no candidate rate, chunking, voice taxonomy, expressiveness "
            "scale, timing protocol or output geometry is asserted",
            "the vendor-reported time-to-first-byte is not presented as a "
            "local measurement",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def artifact_pins(report_digest: str, sidecar_digest: str) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        if name == "report.json":
            pins[TASK_PREFIX + name] = report_digest
        elif name == "report.json.sha256":
            pins[TASK_PREFIX + name] = sidecar_digest
        else:
            pins[TASK_PREFIX + name] = file_digest(TASK_DIR / name)
    return pins


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-HUME-OCTAVE.",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are",
        "# relative to the SDK checkout; pkg: paths are relative to this",
        "# task-evidence directory. The mutable full plan/swarm/TASKS.json is",
        "# never hashed; only the linked-row stable identity is gated.",
    ]
    for path, digest in sorted(SOURCE_PINS.items()):
        lines.append(f"{digest}  source:{path}")
    for path, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  worktree:{path}")
    for name in sorted(PIN_FILES):
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = TASK_DIR / name
            if not full.is_file():
                raise ReferenceRejection("missing_artifact:" + name)
            digest = file_digest(full)
        lines.append(f"{digest}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "ADVERSE_CASE_IDS",
    "BASE_COMMIT",
    "BOUNDARY",
    "BOUNDARY_PINS",
    "CALLER_ASSET_CONTRACT",
    "COMPONENT",
    "CONTROL_PLAN_PROVENANCE",
    "DECISION",
    "EXACT_BLOCKERS",
    "GATE_REQUIREMENTS",
    "MODE",
    "PROFILE",
    "ReferenceRejection",
    "SCOPE",
    "SOURCE_PINS",
    "TASK_ID",
    "admit_target_condition",
    "alignment_accounting",
    "artifact_pins",
    "audit_assets",
    "build_contract",
    "build_control",
    "build_report",
    "canonical_report",
    "canonical_text",
    "duration_accounting",
    "file_digest",
    "identity_target_condition",
    "identity_transform",
    "load_strict_json",
    "load_strict_json_text",
    "object_digest",
    "pcm_summary",
    "run_adverse_controls",
    "sha256_bytes",
    "sources_bytes",
    "synthetic_source_pcm",
    "task_row_identity",
    "validate_caller_manifest",
    "validate_pcm",
]
