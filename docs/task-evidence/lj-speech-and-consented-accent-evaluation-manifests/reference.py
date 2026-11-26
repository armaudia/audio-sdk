# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the LJ Speech and accent task.

The task is to lock source and target-reference provenance separately for the
LJ Speech and L2-ARCTIC accent evaluation, including known source/target
permissions.  The pinned research notes publish prose tables and local clip
copies, but no machine-readable manifest, no per-speaker consent record, no
target-reference provenance record, no terms/redistribution grant, no frozen
cohort and no scoring plan.

Five local clip copies are present and are hash-pinned here as *observations
only*.  They are never decoded, copied into this package, admitted to a cohort
or scored.  The decision is ``DEFER`` and no result qualifies any evaluation.

The module provides four verifiable pieces:

* a fail-closed workspace audit that records present clip bytes and absent
  manifest/consent/rights artifacts at fixed paths;
* a caller-supplied evaluation-manifest contract validated without decoding
  audio, downloading anything or claiming permission;
* a deterministic synthetic manifest/aggregation control that exercises exact
  field, hash, geometry, grouping, missing/invalid/nonfinite rejection and
  evidence-class separation, explicitly labelled as not a real manifest;
* the canonical evidence report model.

Nothing in this package is a real corpus manifest, a consent record or an
evaluation result.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS"
TITLE = "LJ Speech and consented accent evaluation manifests"
SLUG = "lj-speech-and-consented-accent-evaluation-manifests"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "b4960fdba1991a35c07ff7f22cda5257c4749768"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
MODE = "research-control"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "rights_cleared_manifests_and_consent"

INPUT_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
MAX_ASSET_BYTES = 512 * 1024 * 1024
MAX_SOURCE_DURATION_SAMPLES = INPUT_SAMPLE_RATE_HZ * 60 * 60
RELEASE_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")

# ---------------------------------------------------------------------------
# Fixed local observations.  Paths are workspace-relative; absence is recorded
# and presence is hash-pinned, never interpreted as permission.
# ---------------------------------------------------------------------------

SOURCE_CLIP_PATH = (
    "research/voice-conversion-eval-20261101/data/"
    "source_ljspeech_lj001-0001.wav")
TARGET_CLIP_PATH = (
    "research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac")
ACCENT_DIR = "research/accent-conversion-20261101/data/l2accent"
ACCENT_PATHS = (
    ACCENT_DIR + "/ABA_arctic_a0046.wav",
    ACCENT_DIR + "/HJK_arctic_a0103.wav",
    ACCENT_DIR + "/RRBI_arctic_a0391.wav",
)

# These artifacts would have to appear before this blocker may be re-evaluated.
# They are deliberately reserved paths, not fabricated files.
SOURCE_MANIFEST_PATH = (
    "data/manifests/lj-speech-and-accent-eval/source.json")
ACCENT_MANIFEST_PATH = (
    "data/manifests/lj-speech-and-accent-eval/accent-groups.json")
TARGET_MANIFEST_PATH = (
    "data/manifests/lj-speech-and-accent-eval/target-references.json")
COHORT_MANIFEST_PATH = (
    "data/manifests/lj-speech-and-accent-eval/cohort.json")
CONSENT_RECORD_PATH = "data/rights/lj-speech-and-accent-eval/consent.json"
TERMS_RECORD_PATH = "data/rights/lj-speech-and-accent-eval/terms.json"
SCORING_PLAN_PATH = (
    "data/reference/lj-speech-and-accent-eval/scoring-plan.json")
APPROVAL_RECORD_PATH = "data/runs/lj-speech-and-accent-eval/approval.json"

RESERVED_ABSENT_PATHS = (
    SOURCE_MANIFEST_PATH,
    ACCENT_MANIFEST_PATH,
    TARGET_MANIFEST_PATH,
    COHORT_MANIFEST_PATH,
    CONSENT_RECORD_PATH,
    TERMS_RECORD_PATH,
    SCORING_PLAN_PATH,
    APPROVAL_RECORD_PATH,
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
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/data/l2accent/ABA_arctic_a0046.wav":
        "bee4a2b42ef31e3bec2407a0c86d57a80fb5709e0ce19ae2524960797afb1f48",
    "research/accent-conversion-20261101/data/l2accent/HJK_arctic_a0103.wav":
        "136cf347d8ed8e33c1811c9507ee7ff3ccb6bfa7fc7f1ad66e43349cc25ab3c2",
    "research/accent-conversion-20261101/data/l2accent/RRBI_arctic_a0391.wav":
        "90622687e541f0b2ea2893d8125ec27e8600f13e5d085f67c5c6bef3764fe763",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/data/"
    "source_ljspeech_lj001-0001.wav":
        "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b",
    "research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac":
        "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
}
BOUNDARY_PINS: Dict[str, str] = {
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
    "sdk_v0_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": SAMPLE_FORMAT,
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "source_clip_declared_sample_rate_hz": 16000,
    "target_clip_declared_sample_rate_hz": 16000,
    "accent_clip_geometry_recorded": False,
    "sdk_v0_geometry_preserved": True,
    "audio_decoded_here": False,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_code_added": False,
    "adapter_json_added": False,
    "audio_copied_into_package": False,
    "ci_change": False,
    "consent_claimed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "downloads_performed": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "manifests_fabricated": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "rights_approved": False,
    "shared_build_or_ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "clip_bytes_hashed_for_pin": True,
    "consent_record_present": False,
    "device_timing": False,
    "listening": False,
    "manifest_admitted": False,
    "model_executed": False,
    "network_used": False,
    "real_audio_copied": False,
    "real_audio_decoded": False,
    "real_corpus_ingested": False,
    "real_corpus_scored": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No machine-readable source, accent-group, target-reference, cohort, consent, terms or scoring manifest is created here.",
    "No clip is admitted to an evaluation cohort, decoded, resampled, converted or scored.",
    "No audio file is copied into this package; present clip bytes are read only to compute exact SHA-256 observations.",
    "No speaker consent, dataset permission or redistribution grant is inferred from a locally present clip.",
    "No target-reference provenance is invented for the RT-VC demo p360 recording.",
    "No L2-ARCTIC, TokAN-sample or LJ Speech licence is asserted beyond what the pinned research notes state.",
    "No accent group, transcript, duration or speaker identity is invented where the research notes do not record it.",
    "No model, runtime, weight, scorer, listening panel or device clock is used.",
    "No provider, descriptor, registry, installed v0 path, shared build, default or CI change.",
    "No benchmark, quality, latency or release claim is made, and missing evidence never qualifies the evaluation.",
)

# ---------------------------------------------------------------------------
# Observed artifacts.  Presence is a local observation, never an admission.
# ---------------------------------------------------------------------------

OBSERVED_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "ljspeech_lj001_0001",
        "path": SOURCE_CLIP_PATH,
        "role": "source_speech",
        "speaker_id": None,
        "clip_id": "LJ001-0001",
        "l1_accent_group": None,
        "evidence_class": "real_single_utterance_observed_not_admitted",
        "declared_sha256":
            "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b",
        "declared_by":
            "research/voice-conversion-eval-20261101/README.md fixed-audio table",
        "declared_sample_rate_hz": 16000,
        "reported_duration_seconds": "9.655",
        "provenance_status": (
            "source_reported_lj_speech_1_1_public_domain_not_verified_here"),
        "consent_status": "absent",
        "admitted": False,
    },
    {
        "id": "rtvc_p360_target",
        "path": TARGET_CLIP_PATH,
        "role": "target_reference",
        "speaker_id": "p360",
        "clip_id": "3_to_p360/target",
        "l1_accent_group": None,
        "evidence_class": "real_single_utterance_observed_not_admitted",
        "declared_sha256":
            "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
        "declared_by":
            "research/voice-conversion-eval-20261101/README.md fixed-audio table",
        "declared_sample_rate_hz": 16000,
        "reported_duration_seconds": "3.562",
        "provenance_status":
            "upstream_rtvc_demo_dataset_and_license_unconfirmed",
        "consent_status": "absent",
        "admitted": False,
    },
    {
        "id": "l2_arabic_aba_a0046",
        "path": ACCENT_PATHS[0],
        "role": "accent_source",
        "speaker_id": "ABA",
        "clip_id": "arctic_a0046",
        "l1_accent_group": "arabic",
        "evidence_class": "real_single_utterance_observed_not_admitted",
        "declared_sha256": None,
        "declared_by":
            "local research copy; the pinned README publishes no clip digest",
        "declared_sample_rate_hz": None,
        "reported_duration_seconds": "4.539",
        "provenance_status":
            "reported_tokan_demo_sample_using_l2_arctic_speakers",
        "consent_status": "absent",
        "admitted": False,
    },
    {
        "id": "l2_hindi_rrbi_a0391",
        "path": ACCENT_PATHS[2],
        "role": "accent_source",
        "speaker_id": "RRBI",
        "clip_id": "arctic_a0391",
        "l1_accent_group": "hindi",
        "evidence_class": "real_single_utterance_observed_not_admitted",
        "declared_sha256": None,
        "declared_by":
            "local research copy; the pinned README publishes no clip digest",
        "declared_sample_rate_hz": None,
        "reported_duration_seconds": "3.490",
        "provenance_status":
            "reported_tokan_demo_sample_using_l2_arctic_speakers",
        "consent_status": "absent",
        "admitted": False,
    },
    {
        "id": "l2_korean_hjk_a0103",
        "path": ACCENT_PATHS[1],
        "role": "accent_source",
        "speaker_id": "HJK",
        "clip_id": "arctic_a0103",
        "l1_accent_group": "korean",
        "evidence_class": "real_single_utterance_observed_not_admitted",
        "declared_sha256": None,
        "declared_by":
            "local research copy; the pinned README publishes no clip digest",
        "declared_sample_rate_hz": None,
        "reported_duration_seconds": "3.042",
        "provenance_status":
            "reported_tokan_demo_sample_using_l2_arctic_speakers",
        "consent_status": "absent",
        "admitted": False,
    },
)

# ---------------------------------------------------------------------------
# Caller-supplied manifest contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = (
    "audio-sdk/lj-speech-and-consented-accent-evaluation-manifest/0.1")
EXPECTED_SOURCE_ID = "ljspeech_lj001_0001"
EXPECTED_TARGET_ID = "rtvc_p360"
EXPECTED_ACCENT_MAP = (
    ("ABA", "arctic_a0046", "arabic"),
    ("RRBI", "arctic_a0391", "hindi"),
    ("HJK", "arctic_a0103", "korean"),
)
EXPECTED_L1_GROUPS = ("arabic", "hindi", "korean")

MANIFEST_FIELDS = (
    "schema_id",
    "manifest_id",
    "revision",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "sample_format",
    "source_id",
    "source_path",
    "source_sha256",
    "source_duration_samples",
    "source_transcript",
    "source_license",
    "source_rights_record_sha256",
    "source_redistribution_allowed",
    "target_id",
    "target_path",
    "target_sha256",
    "target_speaker_provenance",
    "target_permission_record_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "terms_record_path",
    "terms_record_sha256",
    "cohort_record_path",
    "cohort_record_sha256",
    "scoring_plan_path",
    "scoring_plan_sha256",
    "accent_entries",
    "approval_record_path",
    "approval_record_sha256",
)

ACCENT_ENTRY_FIELDS = (
    "entry_id",
    "speaker_id",
    "l2_arctic_clip_id",
    "l1_accent_group",
    "path",
    "sha256",
    "duration_samples",
    "transcript",
    "source_url",
    "permission_record_sha256",
)

MANIFEST_CONTRACT: Dict[str, Any] = {
    "contract_id": MANIFEST_SCHEMA_ID,
    "caller_owned": True,
    "vendored": False,
    "manifest_is_not_created_here": True,
    "audio_decoded": False,
    "required_fields": list(MANIFEST_FIELDS),
    "required_accent_entry_fields": list(ACCENT_ENTRY_FIELDS),
    "required_accent_entry_count": 3,
    "required_geometry": {
        "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    },
    "required_source_id": EXPECTED_SOURCE_ID,
    "required_target_id": EXPECTED_TARGET_ID,
    "required_accent_map": [
        {"speaker_id": speaker, "l2_arctic_clip_id": clip,
         "l1_accent_group": group}
        for speaker, clip, group in EXPECTED_ACCENT_MAP
    ],
    "absent_behavior": "reject_before_admission",
    "present_behavior": (
        "validate_exact_fields_absolute_paths_unique_paths_geometry_"
        "sha256_and_closed_accent_map_only;_never_decode_audio_and_never_"
        "grant_permission"),
    "acceptance_effect": (
        "structural acceptance never sets admitted_for_evaluation, "
        "consent_verified, rights_approved, reviewer_approved or "
        "qualification; independent review is always required"),
}

# ---------------------------------------------------------------------------
# Gates and blockers.  Exactly eight remain blocked.
# ---------------------------------------------------------------------------

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "source_manifest_and_exact_identity",
        "A machine-readable source manifest pins the exact LJ Speech clip, "
        "transcript, geometry, byte count, SHA-256, licence and rights record "
        "before any clip is admitted.",
    ),
    (
        "accent_group_manifest_and_l1_labels",
        "A machine-readable accent manifest pins the L2-ARCTIC speaker, clip "
        "identifier, L1 group, source locator, byte count, SHA-256, duration "
        "and transcript for every accent entry.",
    ),
    (
        "target_reference_provenance_and_permission",
        "The target-reference speaker, upstream source, dataset terms, byte "
        "count, SHA-256 and written permission are recorded separately from "
        "the source material.",
    ),
    (
        "speaker_consent_and_output_use",
        "Per-speaker consent covers conversion, accent modification, output "
        "publication, retention and any redistribution for every source, "
        "target and accent speaker.",
    ),
    (
        "dataset_terms_and_redistribution",
        "Dataset terms, attribution, noncommercial limits and redistribution "
        "or publication grants are recorded for each upstream corpus and for "
        "the TokAN sample copies.",
    ),
    (
        "rights_cleared_cohort_and_split",
        "A frozen, rights-cleared cohort records paired/unpaired roles, "
        "held-out speakers or items, negative and quiet controls and the "
        "exact allowed use.",
    ),
    (
        "evidence_separation_scoring_and_controls",
        "A pinned scoring plan separates paired, unpaired, synthetic, human "
        "and source-reported evidence, fixes aggregation and failed-item "
        "handling, and validates one invalid and one valid bundle.",
    ),
    (
        "opt_in_adapter_and_release",
        "An opt-in adapter decision, independent exact-head review, default "
        "policy and release or benchmark approval are recorded; nothing is "
        "registered, enabled or published by this package.",
    ),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_manifest_and_exact_identity_absent",
        "state": "absent",
        "requirement": (
            "Create a machine-readable source manifest for LJ Speech "
            "LJ001-0001 with the exact transcript, geometry, byte count, "
            "SHA-256, licence and rights-record digest; only a research "
            "README prose table exists."),
    },
    {
        "id": "accent_group_manifest_absent",
        "state": "absent",
        "requirement": (
            "Create a machine-readable accent manifest for the ABA, RRBI and "
            "HJK L2-ARCTIC clips with speaker, clip identifier, L1 group, "
            "source locator, byte count, SHA-256, duration and transcript; "
            "three local copies exist without any manifest."),
    },
    {
        "id": "target_reference_provenance_absent",
        "state": "absent",
        "requirement": (
            "Record the p360 target-reference speaker, upstream RT-VC demo "
            "source, dataset terms and written permission; the pinned README "
            "states that dataset/licence provenance is not yet confirmed."),
    },
    {
        "id": "per_speaker_consent_absent",
        "state": "absent",
        "requirement": (
            "Obtain per-speaker consent for LJ001, p360, ABA, RRBI and HJK "
            "covering conversion, accent modification, output publication, "
            "retention and redistribution; no consent record exists."),
    },
    {
        "id": "dataset_terms_and_redistribution_unresolved",
        "state": "absent",
        "requirement": (
            "Record the LJ Speech, L2-ARCTIC and TokAN-sample terms, "
            "attribution, noncommercial boundary and redistribution or "
            "publication grant; the pinned notes report CC BY-NC 4.0 for "
            "L2-ARCTIC and no visible TokAN licence file."),
    },
    {
        "id": "rights_cleared_cohort_and_split_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared cohort with source/target/accent roles, "
            "paired and unpaired items, held-out speakers or items, negative "
            "and quiet controls and the exact permitted use."),
    },
    {
        "id": "evidence_separation_scoring_and_controls_absent",
        "state": "absent",
        "requirement": (
            "Pin the scorer and its revision, manual transcripts and accent "
            "ground truth, aggregation, failed-item policy, evidence-class "
            "separation and one invalid plus one valid bundle path; only a "
            "synthetic structural control exists."),
    },
    {
        "id": "approved_adapter_and_release_absent",
        "state": "absent",
        "requirement": (
            "Record an approved opt-in adapter decision, independent "
            "exact-head review, default policy and release or benchmark "
            "approval; no adapter, registration or release claim exists."),
    },
)

EVIDENCE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "scorer_pin",
        "Pin the exact scorer, revision, mode and permitted use before scoring.",
        "absent",
    ),
    (
        "corpus_pin",
        "Pin the corpus and clip set with exact byte counts and SHA-256.",
        "partial_observations_only",
    ),
    (
        "cohort_pin",
        "Freeze the cohort, roles, held-out split and controls.",
        "absent",
    ),
    (
        "aggregation_plan",
        "Fix aggregation before seeing results and never pool evidence classes.",
        "absent",
    ),
    (
        "failed_item_policy",
        "Record failed, missing and excluded items explicitly.",
        "absent",
    ),
    (
        "controls",
        "Validate one invalid/missing case and one representative valid result.",
        "structural_only",
    ),
    (
        "paired_unpaired_separation",
        "Preserve paired, unpaired, synthetic, human and source-reported separation.",
        "structural_only",
    ),
    (
        "source_reported_label",
        "Keep source-reported claims labelled and out of local measurements.",
        "preserved",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "primary_source": "research/voice-conversion-eval-20261101/README.md",
    "primary_source_sha256": SOURCE_PINS[
        "research/voice-conversion-eval-20261101/README.md"],
    "secondary_source": "research/accent-conversion-20261101/README.md",
    "secondary_source_sha256": SOURCE_PINS[
        "research/accent-conversion-20261101/README.md"],
    "ljspeech_status": (
        "local clean-real-voice reference documented as LJ Speech 1.1 "
        "LJ001-0001; the dataset page is reported to describe the recordings "
        "as public domain"),
    "ljspeech_transcript": (
        "Printing, in the only sense with which we are at present concerned, "
        "differs from most if not from all the arts and crafts represented in "
        "the Exhibition."),
    "target_reference_status": (
        "RT-VC upstream demo 3_to_p360/target.flac; dataset and licence "
        "provenance are explicitly not yet confirmed"),
    "accent_status": (
        "three clips from the TokAN demo sample set, reported to use "
        "L2-ARCTIC speakers ABA, RRBI and HJK; the official corpus terms are "
        "reported as CC BY-NC 4.0 and the three clips are a small smoke slice"),
    "accent_classifier_status": (
        "the six-class accent classifier is a directional proxy trained "
        "mainly on native-speaker Common Voice; it is not L2-ARCTIC ground "
        "truth and does not include Korean-accented English"),
    "listening_status": "blinded human listening remains outstanding",
    "licence_status": (
        "the TokAN repository is reported to have no visible licence file; "
        "resolve provenance and licensing before product use"),
    "notes": (
        "The pinned research notes retain local run results for several "
        "models.  None of those results is reproduced, rescored or promoted "
        "here.  No source-reported value qualifies this evidence task."),
}

# ---------------------------------------------------------------------------
# Deterministic synthetic manifest/aggregation control.
# ---------------------------------------------------------------------------

CONTROL_ID = (
    "synthetic_lj_accent_manifest_structural_control_uses_declared_ids_and_"
    "analytic_payloads_not_real_data")
SYNTHETIC_ROOT = "/synthetic/lj-accent-manifest-control"
EVIDENCE_CLASSES = (
    "paired", "unpaired", "synthetic", "human", "source_reported")

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_bad_schema",
    "manifest_empty_id",
    "manifest_bad_revision",
    "manifest_wrong_rate",
    "manifest_bool_rate",
    "manifest_nonfinite_rate",
    "manifest_wrong_channels",
    "manifest_wrong_frame",
    "manifest_wrong_sample_format",
    "manifest_wrong_source_id",
    "manifest_empty_transcript",
    "manifest_non_ascii_transcript",
    "manifest_empty_license",
    "manifest_bad_source_sha",
    "manifest_wrong_source_hash",
    "manifest_relative_source_path",
    "manifest_duplicate_path",
    "manifest_missing_source_asset",
    "manifest_nonfinite_duration",
    "manifest_bool_duration",
    "manifest_negative_duration",
    "manifest_zero_duration",
    "manifest_redistribution_not_bool",
    "manifest_wrong_target_id",
    "manifest_missing_target_asset",
    "manifest_target_hash_mismatch",
    "manifest_empty_provenance",
    "manifest_missing_consent_asset",
    "manifest_missing_terms_asset",
    "manifest_missing_cohort_asset",
    "manifest_missing_scoring_asset",
    "manifest_missing_approval_asset",
    "manifest_consent_hash_mismatch",
    "accent_not_sequence",
    "accent_count_two",
    "accent_count_four",
    "accent_duplicate_speaker",
    "accent_unknown_group",
    "accent_wrong_speaker",
    "accent_wrong_clip",
    "accent_missing_field",
    "accent_extra_field",
    "accent_relative_path",
    "accent_nonfinite_duration",
    "accent_negative_duration",
    "accent_empty_transcript",
    "accent_duplicate_path",
    "accent_missing_asset",
    "accent_hash_mismatch",
    "accent_bad_permission_sha",
)


class Reject(ValueError):
    """Fail-closed rejection for malformed, missing or unqualified input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def _sha256_file(path: Path) -> Tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_ASSET_BYTES:
                raise Reject("asset exceeds the evidence cap: " + str(path))
            digest.update(chunk)
    return digest.hexdigest(), total


# ---------------------------------------------------------------------------
# Workspace audit.  Fixed local reads only; no decode, copy, network or model.
# ---------------------------------------------------------------------------

def _accent_file_names() -> List[str]:
    directory = SOURCE_ROOT / ACCENT_DIR
    if not directory.is_dir():
        return []
    return sorted(path.name for path in directory.iterdir()
                  if path.is_file())


def audit_workspace() -> Dict[str, Any]:
    artifacts: List[Dict[str, Any]] = []
    for spec in OBSERVED_ARTIFACTS:
        relative = spec["path"]
        path = SOURCE_ROOT / relative
        present = path.is_file()
        digest: Optional[str] = None
        byte_count: Optional[int] = None
        if present:
            digest, byte_count = _sha256_file(path)
        pinned = SOURCE_PINS.get(relative)
        declared = spec["declared_sha256"]
        artifacts.append({
            "id": spec["id"],
            "path": relative,
            "role": spec["role"],
            "speaker_id": spec["speaker_id"],
            "clip_id": spec["clip_id"],
            "l1_accent_group": spec["l1_accent_group"],
            "evidence_class": spec["evidence_class"],
            "present": present,
            "byte_count": byte_count,
            "observed_sha256": digest,
            "pin_sha256": pinned,
            "pin_matches": present and pinned is not None and digest == pinned,
            "declared_sha256": declared,
            "declared_matches": (
                None if declared is None else present and digest == declared),
            "declared_by": spec["declared_by"],
            "declared_sample_rate_hz": spec["declared_sample_rate_hz"],
            "reported_duration_seconds": spec["reported_duration_seconds"],
            "provenance_status": spec["provenance_status"],
            "consent_status": spec["consent_status"],
            "admitted": False,
        })

    absent = [relative for relative in RESERVED_ABSENT_PATHS
              if not (SOURCE_ROOT / relative).exists()]
    present_reserved = [relative for relative in RESERVED_ABSENT_PATHS
                        if (SOURCE_ROOT / relative).exists()]
    names = _accent_file_names()
    return {
        "observed_artifacts": artifacts,
        "observed_clip_count": len([item for item in artifacts
                                    if item["present"]]),
        "admitted_clip_count": 0,
        "accent_clip_dir": ACCENT_DIR,
        "accent_clip_names": names,
        "accent_clip_count": len(names),
        "reserved_absent_paths": absent,
        "reserved_present_paths": present_reserved,
        "source_manifest_present": (SOURCE_ROOT / SOURCE_MANIFEST_PATH).exists(),
        "accent_manifest_present": (SOURCE_ROOT / ACCENT_MANIFEST_PATH).exists(),
        "target_manifest_present": (SOURCE_ROOT / TARGET_MANIFEST_PATH).exists(),
        "cohort_manifest_present": (SOURCE_ROOT / COHORT_MANIFEST_PATH).exists(),
        "consent_record_present": (SOURCE_ROOT / CONSENT_RECORD_PATH).exists(),
        "terms_record_present": (SOURCE_ROOT / TERMS_RECORD_PATH).exists(),
        "scoring_plan_present": (SOURCE_ROOT / SCORING_PLAN_PATH).exists(),
        "approval_record_present": (SOURCE_ROOT / APPROVAL_RECORD_PATH).exists(),
        "audio_decoded": False,
        "audio_copied": False,
        "network_used": False,
    }


def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_workspace()
    complete = (
        not observed["reserved_present_paths"]
        and observed["source_manifest_present"]
        and observed["accent_manifest_present"]
        and observed["target_manifest_present"]
        and observed["cohort_manifest_present"]
        and observed["consent_record_present"]
        and observed["terms_record_present"]
        and observed["scoring_plan_present"]
        and observed["approval_record_present"])
    if observed["reserved_present_paths"]:
        result = "reserved_artifact_present_reopen_required"
    elif complete:
        result = "manifest_set_complete_pending_review"
    elif observed["observed_clip_count"] > 0:
        result = "observed_unmanifested_unconsented"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "observed_clip_count": observed["observed_clip_count"],
        "admitted_clip_count": 0,
        "accent_clip_count": observed["accent_clip_count"],
        "source_manifest_present": observed["source_manifest_present"],
        "accent_manifest_present": observed["accent_manifest_present"],
        "target_manifest_present": observed["target_manifest_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "consent_present": observed["consent_record_present"],
        "terms_present": observed["terms_record_present"],
        "scoring_plan_present": observed["scoring_plan_present"],
        "approval_present": observed["approval_record_present"],
        "reserved_present_paths": observed["reserved_present_paths"],
        "observed": observed,
        "note": (
            "Five local clip copies are observed and hash-pinned.  Presence "
            "is not a manifest, consent record, licence grant or admission.  "
            "No clip enters a cohort and no result is produced."),
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
# Manifest validation.  A caller must supply every file; this package never
# creates a manifest, decodes audio or grants permission.
# ---------------------------------------------------------------------------

class _DiskResolver:
    def read(self, path: Path) -> bytes:
        if not path.is_file():
            raise Reject("manifest asset file is missing: " + str(path))
        if path.stat().st_size > MAX_ASSET_BYTES:
            raise Reject("manifest asset exceeds the evidence cap: " + str(path))
        return path.read_bytes()


class _MemoryResolver:
    def __init__(self, files: Dict[str, bytes]) -> None:
        self.files = dict(files)

    def read(self, path: Path) -> bytes:
        key = str(path)
        if key not in self.files:
            raise Reject("manifest asset file is missing: " + str(path))
        return self.files[key]


def _reject(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def _ascii_text(value: Any, field: str, maximum: int,
                allow_empty: bool = False) -> str:
    _reject(isinstance(value, str), "manifest " + field + " must be a string")
    assert isinstance(value, str)
    _reject(value.isascii(), "manifest " + field + " must be ASCII")
    _reject(len(value) <= maximum, "manifest " + field + " is too long")
    if not allow_empty:
        _reject(bool(value.strip()), "manifest " + field + " is empty")
    return value


def _int_value(value: Any, field: str, minimum: int,
               maximum: int) -> int:
    _reject(isinstance(value, int) and not isinstance(value, bool),
            "manifest " + field + " must be an integer")
    assert isinstance(value, int)
    _reject(minimum <= value <= maximum,
            "manifest " + field + " is outside the declared bounds")
    return value


def _sha_value(value: Any, field: str) -> str:
    _reject(isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value)),
            "manifest " + field + " is not a lowercase SHA-256")
    assert isinstance(value, str)
    return value


def _absolute_path(value: Any, field: str) -> Path:
    _reject(isinstance(value, str) and bool(value),
            "manifest " + field + " must be a path string")
    assert isinstance(value, str)
    path = Path(value)
    _reject(path.is_absolute(), "manifest " + field + " must be absolute")
    return path


def _accent_projection(entries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    projected = []
    for entry in entries:
        projected.append({
            "speaker_id": entry["speaker_id"],
            "l2_arctic_clip_id": entry["l2_arctic_clip_id"],
            "l1_accent_group": entry["l1_accent_group"],
            "sha256": entry["sha256"],
            "duration_samples": entry["duration_samples"],
        })
    projected.sort(key=lambda item: (item["speaker_id"],
                                     item["l2_arctic_clip_id"]))
    return projected


def validate_manifest(manifest: Any, resolver: Any) -> Dict[str, Any]:
    _reject(isinstance(manifest, dict), "manifest must be an object")
    assert isinstance(manifest, dict)
    expected = set(MANIFEST_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    _reject(not missing, "manifest missing fields: " + ",".join(missing))
    _reject(not extra, "manifest has unknown fields: " + ",".join(extra))

    _reject(manifest["schema_id"] == MANIFEST_SCHEMA_ID,
            "manifest schema_id mismatch")
    manifest_id = manifest["manifest_id"]
    _reject(isinstance(manifest_id, str)
            and bool(RELEASE_TOKEN.fullmatch(manifest_id)),
            "manifest manifest_id is not an exact ASCII token")
    revision = manifest["revision"]
    _reject(isinstance(revision, str)
            and bool(RELEASE_TOKEN.fullmatch(revision)),
            "manifest revision is not an exact ASCII token")

    _int_value(manifest["sample_rate_hz"], "sample_rate_hz",
               INPUT_SAMPLE_RATE_HZ, INPUT_SAMPLE_RATE_HZ)
    _int_value(manifest["channels"], "channels", CHANNELS, CHANNELS)
    _int_value(manifest["frame_samples"], "frame_samples",
               SDK_FRAME_SAMPLES, SDK_FRAME_SAMPLES)
    _reject(manifest["sample_format"] == SAMPLE_FORMAT,
            "manifest sample_format must be " + SAMPLE_FORMAT)

    _reject(manifest["source_id"] == EXPECTED_SOURCE_ID,
            "manifest source_id mismatch")
    _ascii_text(manifest["source_transcript"], "source_transcript", 4096)
    _ascii_text(manifest["source_license"], "source_license", 256)
    _sha_value(manifest["source_sha256"], "source_sha256")
    _sha_value(manifest["source_rights_record_sha256"],
               "source_rights_record_sha256")
    _int_value(manifest["source_duration_samples"],
               "source_duration_samples", 1, MAX_SOURCE_DURATION_SAMPLES)
    _reject(isinstance(manifest["source_redistribution_allowed"], bool),
            "manifest source_redistribution_allowed must be a boolean")

    _reject(manifest["target_id"] == EXPECTED_TARGET_ID,
            "manifest target_id mismatch")
    _sha_value(manifest["target_sha256"], "target_sha256")
    _sha_value(manifest["target_permission_record_sha256"],
               "target_permission_record_sha256")
    _ascii_text(manifest["target_speaker_provenance"],
                "target_speaker_provenance", 512)

    for field in ("consent_record_sha256", "terms_record_sha256",
                  "cohort_record_sha256", "scoring_plan_sha256",
                  "approval_record_sha256"):
        _sha_value(manifest[field], field)

    entries = manifest["accent_entries"]
    _reject(isinstance(entries, list),
            "manifest accent_entries must be a sequence")
    assert isinstance(entries, list)
    _reject(len(entries) == 3,
            "manifest accent_entries must contain exactly three entries")
    expected_map = {(speaker, clip, group)
                    for speaker, clip, group in EXPECTED_ACCENT_MAP}
    seen_pairs: set[Tuple[str, str]] = set()
    entry_ids: set[str] = set()
    for index, entry in enumerate(entries):
        _reject(isinstance(entry, dict),
                f"accent entry {index} must be an object")
        assert isinstance(entry, dict)
        entry_missing = sorted(set(ACCENT_ENTRY_FIELDS) - set(entry))
        entry_extra = sorted(set(entry) - set(ACCENT_ENTRY_FIELDS))
        _reject(not entry_missing,
                f"accent entry {index} missing fields: "
                + ",".join(entry_missing))
        _reject(not entry_extra,
                f"accent entry {index} has unknown fields: "
                + ",".join(entry_extra))
        entry_id = _ascii_text(entry["entry_id"],
                               f"accent entry {index} entry_id", 64)
        _reject(entry_id not in entry_ids,
                "accent entry_id is duplicated: " + entry_id)
        entry_ids.add(entry_id)
        speaker = _ascii_text(entry["speaker_id"],
                              f"accent entry {index} speaker_id", 64)
        clip = _ascii_text(entry["l2_arctic_clip_id"],
                           f"accent entry {index} l2_arctic_clip_id", 64)
        group = _ascii_text(entry["l1_accent_group"],
                            f"accent entry {index} l1_accent_group", 64)
        _reject((speaker, clip, group) in expected_map,
                f"accent entry {index} is outside the closed accent map")
        _reject((speaker, clip) not in seen_pairs,
                "accent speaker/clip pair is duplicated: " + speaker)
        seen_pairs.add((speaker, clip))
        _sha_value(entry["sha256"], f"accent entry {index} sha256")
        _sha_value(entry["permission_record_sha256"],
                   f"accent entry {index} permission_record_sha256")
        _int_value(entry["duration_samples"],
                   f"accent entry {index} duration_samples",
                   1, MAX_SOURCE_DURATION_SAMPLES)
        _ascii_text(entry["transcript"],
                    f"accent entry {index} transcript", 4096)
        _ascii_text(entry["source_url"],
                    f"accent entry {index} source_url", 512)
    _reject(seen_pairs == {(speaker, clip)
                           for speaker, clip, _group in EXPECTED_ACCENT_MAP},
            "manifest accent entries do not cover the closed accent map")

    path_fields = (
        ("source_path", "source_sha256"),
        ("target_path", "target_sha256"),
        ("consent_record_path", "consent_record_sha256"),
        ("terms_record_path", "terms_record_sha256"),
        ("cohort_record_path", "cohort_record_sha256"),
        ("scoring_plan_path", "scoring_plan_sha256"),
        ("approval_record_path", "approval_record_sha256"),
    )
    files: List[Tuple[str, Path, str]] = []
    for path_field, sha_field in path_fields:
        files.append((path_field,
                      _absolute_path(manifest[path_field], path_field),
                      sha_field))
    for index, entry in enumerate(entries):
        files.append((f"accent entry {index} path",
                      _absolute_path(entry["path"],
                                     f"accent entry {index} path"),
                      "sha256"))
    resolved = [str(path) for _field, path, _sha in files]
    _reject(len(set(resolved)) == len(resolved),
            "manifest asset paths must be unique")

    total_bytes = 0
    for field, path, _sha_field in files:
        try:
            data = resolver.read(path)
        except OSError as error:
            raise Reject("manifest " + field + " is unreadable") from error
        _reject(len(data) <= MAX_ASSET_BYTES,
                "manifest " + field + " exceeds the evidence cap")
        total_bytes += len(data)

    for field, path, sha_field in files:
        declared = (manifest[sha_field] if sha_field in manifest
                    else entries[int(field.split()[2])]["sha256"])
        actual = sha256(resolver.read(path))
        _reject(actual == declared,
                "manifest " + field + " SHA-256 mismatch")

    accent_projection = _accent_projection(entries)
    projection = {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": manifest["manifest_id"],
        "revision": manifest["revision"],
        "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "source_id": manifest["source_id"],
        "source_sha256": manifest["source_sha256"],
        "source_duration_samples": manifest["source_duration_samples"],
        "target_id": manifest["target_id"],
        "target_sha256": manifest["target_sha256"],
        "accent_entries": accent_projection,
        "consent_record_sha256": manifest["consent_record_sha256"],
        "terms_record_sha256": manifest["terms_record_sha256"],
        "cohort_record_sha256": manifest["cohort_record_sha256"],
        "scoring_plan_sha256": manifest["scoring_plan_sha256"],
        "approval_record_sha256": manifest["approval_record_sha256"],
    }
    group_counts = {group: 0 for group in EXPECTED_L1_GROUPS}
    for entry in entries:
        group_counts[entry["l1_accent_group"]] += 1
    return {
        "accepted": True,
        "admitted_for_evaluation": False,
        "accepted_for_qualification": False,
        "consent_verified": False,
        "rights_approved": False,
        "reviewer_approved": False,
        "adjudication": "structural_only_requires_independent_review",
        "manifest_id": manifest["manifest_id"],
        "revision": manifest["revision"],
        "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "source_id": manifest["source_id"],
        "target_id": manifest["target_id"],
        "accent_entry_count": len(entries),
        "accent_group_counts": group_counts,
        "files_checked": len(files),
        "total_asset_bytes": total_bytes,
        "manifest_projection_sha256": sha256(canonical_bytes(projection)),
        "audio_decoded": False,
        "qualification_effect": "none",
    }


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    return validate_manifest(manifest, _DiskResolver())


# ---------------------------------------------------------------------------
# Deterministic synthetic fixture.  Payloads are analytic; the declared IDs are
# the task's declared IDs, but this is explicitly not a real manifest.
# ---------------------------------------------------------------------------

def _synthetic_payload(name: str) -> bytes:
    return ("synthetic-manifest-control:" + name).encode("ascii")


def _synthetic_file(name: str) -> str:
    return f"{SYNTHETIC_ROOT}/{name}"


def _synthetic_files() -> Dict[str, bytes]:
    names = (
        "source_lj001_0001.wav",
        "target_p360.flac",
        "ABA_arctic_a0046.wav",
        "RRBI_arctic_a0391.wav",
        "HJK_arctic_a0103.wav",
        "consent.json",
        "terms.json",
        "cohort.json",
        "scoring-plan.json",
        "approval.json",
    )
    return {_synthetic_file(name): _synthetic_payload(name) for name in names}


def _synthetic_manifest() -> Dict[str, Any]:
    entries = []
    for speaker, clip, group in EXPECTED_ACCENT_MAP:
        name = f"{speaker}_{clip}.wav"
        entries.append({
            "entry_id": f"synthetic_accent_{speaker.lower()}",
            "speaker_id": speaker,
            "l2_arctic_clip_id": clip,
            "l1_accent_group": group,
            "path": _synthetic_file(name),
            "sha256": sha256(_synthetic_payload(name)),
            "duration_samples": 16000 + len(group),
            "transcript": f"Synthetic {group} control transcript.",
            "source_url": "https://example.invalid/synthetic-control",
            "permission_record_sha256":
                sha256(("synthetic-permission:" + speaker).encode("ascii")),
        })
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "synthetic-control-manifest",
        "revision": "0.0.1-synthetic",
        "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "source_id": EXPECTED_SOURCE_ID,
        "source_path": _synthetic_file("source_lj001_0001.wav"),
        "source_sha256": sha256(_synthetic_payload("source_lj001_0001.wav")),
        "source_duration_samples": 154480,
        "source_transcript": "Synthetic source control transcript.",
        "source_license": "synthetic-control-only",
        "source_rights_record_sha256":
            sha256(b"synthetic-source-rights"),
        "source_redistribution_allowed": False,
        "target_id": EXPECTED_TARGET_ID,
        "target_path": _synthetic_file("target_p360.flac"),
        "target_sha256": sha256(_synthetic_payload("target_p360.flac")),
        "target_speaker_provenance":
            "synthetic control target provenance; not a real speaker",
        "target_permission_record_sha256":
            sha256(b"synthetic-target-permission"),
        "consent_record_path": _synthetic_file("consent.json"),
        "consent_record_sha256": sha256(_synthetic_payload("consent.json")),
        "terms_record_path": _synthetic_file("terms.json"),
        "terms_record_sha256": sha256(_synthetic_payload("terms.json")),
        "cohort_record_path": _synthetic_file("cohort.json"),
        "cohort_record_sha256": sha256(_synthetic_payload("cohort.json")),
        "scoring_plan_path": _synthetic_file("scoring-plan.json"),
        "scoring_plan_sha256":
            sha256(_synthetic_payload("scoring-plan.json")),
        "accent_entries": entries,
        "approval_record_path": _synthetic_file("approval.json"),
        "approval_record_sha256": sha256(_synthetic_payload("approval.json")),
    }


def validate_synthetic_manifest() -> Dict[str, Any]:
    return validate_manifest(_synthetic_manifest(),
                             _MemoryResolver(_synthetic_files()))


# ---------------------------------------------------------------------------
# Evidence aggregation control.
# ---------------------------------------------------------------------------

AGGREGATE_FIELDS = (
    "entry_id", "l1_accent_group", "evidence_class", "status",
    "value", "reason")


def aggregate_evidence(records: Any) -> Dict[str, Any]:
    _reject(isinstance(records, list), "aggregation records must be a list")
    assert isinstance(records, list)
    seen: set[str] = set()
    by_class = {name: 0 for name in EVIDENCE_CLASSES}
    by_group = {name: 0 for name in EXPECTED_L1_GROUPS}
    measured: List[str] = []
    not_measured: List[str] = []
    failed: List[str] = []
    projection: List[Dict[str, Any]] = []
    for index, record in enumerate(records):
        _reject(isinstance(record, dict),
                f"aggregation record {index} must be an object")
        assert isinstance(record, dict)
        _reject(set(record) == set(AGGREGATE_FIELDS),
                f"aggregation record {index} fields mismatch")
        entry_id = _ascii_text(record["entry_id"],
                               f"aggregation record {index} entry_id", 64)
        _reject(entry_id not in seen,
                "aggregation entry_id is duplicated: " + entry_id)
        seen.add(entry_id)
        group = record["l1_accent_group"]
        _reject(isinstance(group, str) and group in EXPECTED_L1_GROUPS,
                f"aggregation record {index} l1_accent_group is unknown")
        evidence_class = record["evidence_class"]
        _reject(isinstance(evidence_class, str)
                and evidence_class in EVIDENCE_CLASSES,
                f"aggregation record {index} evidence_class is unknown")
        status = record["status"]
        _reject(status in ("measured", "not_measured", "failed"),
                f"aggregation record {index} status is unknown")
        value = record["value"]
        reason = record["reason"]
        _reject(isinstance(reason, str),
                f"aggregation record {index} reason must be a string")
        if status == "measured":
            _reject(isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(float(value)),
                    f"aggregation record {index} value must be finite")
            _reject(not reason.strip(),
                    f"aggregation record {index} measured reason must be empty")
            measured.append(entry_id)
        elif status == "not_measured":
            _reject(value is None,
                    f"aggregation record {index} value must be null")
            _reject(not reason.strip(),
                    f"aggregation record {index} reason must be empty")
            not_measured.append(entry_id)
        else:
            _reject(value is None,
                    f"aggregation record {index} failed value must be null")
            _reject(bool(reason.strip()),
                    f"aggregation record {index} failed reason must be present")
            failed.append(entry_id)
        by_class[evidence_class] += 1
        by_group[group] += 1
        projection.append({
            "entry_id": entry_id,
            "l1_accent_group": group,
            "evidence_class": evidence_class,
            "status": status,
            "value": None if value is None else float(value),
        })
    projection.sort(key=lambda item: item["entry_id"])
    return {
        "record_count": len(records),
        "by_evidence_class": by_class,
        "by_l1_accent_group": by_group,
        "measured_entry_ids": sorted(measured),
        "not_measured_entry_ids": sorted(not_measured),
        "failed_entry_ids": sorted(failed),
        "pooled_across_evidence_classes": False,
        "aggregate_sha256": sha256(canonical_bytes(projection)),
    }


def _control_records() -> List[Dict[str, Any]]:
    return [
        {
            "entry_id": "synthetic_arabic",
            "l1_accent_group": "arabic",
            "evidence_class": "synthetic",
            "status": "not_measured",
            "value": None,
            "reason": "",
        },
        {
            "entry_id": "synthetic_hindi",
            "l1_accent_group": "hindi",
            "evidence_class": "synthetic",
            "status": "not_measured",
            "value": None,
            "reason": "",
        },
        {
            "entry_id": "synthetic_korean",
            "l1_accent_group": "korean",
            "evidence_class": "synthetic",
            "status": "not_measured",
            "value": None,
            "reason": "",
        },
        {
            "entry_id": "synthetic_missing_consent_failure",
            "l1_accent_group": "arabic",
            "evidence_class": "synthetic",
            "status": "failed",
            "value": None,
            "reason": "synthetic missing-consent control",
        },
    ]


def _invoke(case_id: str, action: Any) -> Dict[str, str]:
    try:
        action()
    except Reject as error:
        return {"case": case_id, "result": "rejected", "reason": str(error)}
    except Exception as error:  # noqa: BLE001 - recorded, never swallowed
        return {"case": case_id, "result": "unexpected_error",
                "reason": type(error).__name__ + ": " + str(error)}
    return {"case": case_id, "result": "accepted", "reason": ""}


def run_adverse_controls() -> List[Dict[str, str]]:
    import copy

    files = _synthetic_files()

    def mutated(mutator: Any) -> Any:
        manifest = copy.deepcopy(_synthetic_manifest())
        mutator(manifest)
        return lambda: validate_manifest(
            manifest, _MemoryResolver(files))

    def drop(field: str) -> Any:
        return mutated(lambda manifest: manifest.pop(field))

    def put(field: str, value: Any) -> Any:
        def apply(manifest: Dict[str, Any]) -> None:
            manifest[field] = value
        return mutated(apply)

    def accent(index: int, field: str, value: Any) -> Any:
        def apply(manifest: Dict[str, Any]) -> None:
            manifest["accent_entries"][index][field] = value
        return mutated(apply)

    def accent_drop(index: int, field: str) -> Any:
        def apply(manifest: Dict[str, Any]) -> None:
            manifest["accent_entries"][index].pop(field)
        return mutated(apply)

    def accent_count(count: int) -> Any:
        def apply(manifest: Dict[str, Any]) -> None:
            manifest["accent_entries"] = manifest["accent_entries"][:count]
        return mutated(apply)

    cases = [
        ("manifest_not_object", lambda: validate_manifest(
            [], _MemoryResolver(files))),
        ("manifest_missing_field", drop("approval_record_sha256")),
        ("manifest_extra_field", put("extra_field", "x")),
        ("manifest_bad_schema", put("schema_id", "audio-sdk/other/0.1")),
        ("manifest_empty_id", put("manifest_id", "")),
        ("manifest_bad_revision", put("revision", "bad revision")),
        ("manifest_wrong_rate", put("sample_rate_hz", 22050)),
        ("manifest_bool_rate", put("sample_rate_hz", True)),
        ("manifest_nonfinite_rate", put("sample_rate_hz", math.nan)),
        ("manifest_wrong_channels", put("channels", 2)),
        ("manifest_wrong_frame", put("frame_samples", 80)),
        ("manifest_wrong_sample_format", put("sample_format", "s16")),
        ("manifest_wrong_source_id", put("source_id", "other_source")),
        ("manifest_empty_transcript", put("source_transcript", "")),
        ("manifest_non_ascii_transcript",
         put("source_transcript", "caf\u00e9")),
        ("manifest_empty_license", put("source_license", "")),
        ("manifest_bad_source_sha", put("source_sha256", "ABC")),
        ("manifest_wrong_source_hash", put("source_sha256", "0" * 64)),
        ("manifest_relative_source_path",
         put("source_path", "relative.wav")),
        ("manifest_duplicate_path", mutated(
            lambda manifest: manifest.__setitem__(
                "target_path", manifest["source_path"]))),
        ("manifest_missing_source_asset",
         put("source_path", _synthetic_file("missing-source.wav"))),
        ("manifest_nonfinite_duration",
         put("source_duration_samples", math.nan)),
        ("manifest_bool_duration", put("source_duration_samples", True)),
        ("manifest_negative_duration",
         put("source_duration_samples", -1)),
        ("manifest_zero_duration", put("source_duration_samples", 0)),
        ("manifest_redistribution_not_bool",
         put("source_redistribution_allowed", "yes")),
        ("manifest_wrong_target_id", put("target_id", "other_target")),
        ("manifest_missing_target_asset",
         put("target_path", _synthetic_file("missing-target.flac"))),
        ("manifest_target_hash_mismatch",
         put("target_sha256", "0" * 64)),
        ("manifest_empty_provenance",
         put("target_speaker_provenance", "")),
        ("manifest_missing_consent_asset",
         put("consent_record_path", _synthetic_file("missing-consent.json"))),
        ("manifest_missing_terms_asset",
         put("terms_record_path", _synthetic_file("missing-terms.json"))),
        ("manifest_missing_cohort_asset",
         put("cohort_record_path", _synthetic_file("missing-cohort.json"))),
        ("manifest_missing_scoring_asset",
         put("scoring_plan_path", _synthetic_file("missing-scoring.json"))),
        ("manifest_missing_approval_asset",
         put("approval_record_path", _synthetic_file("missing-approval.json"))),
        ("manifest_consent_hash_mismatch",
         put("consent_record_sha256", "0" * 64)),
        ("accent_not_sequence",
         put("accent_entries", "not-a-list")),
        ("accent_count_two", accent_count(2)),
        ("accent_count_four",
         mutated(lambda manifest: manifest["accent_entries"].append(
             copy.deepcopy(manifest["accent_entries"][0])))),
        ("accent_duplicate_speaker",
         accent(1, "speaker_id", "ABA")),
        ("accent_unknown_group",
         accent(0, "l1_accent_group", "klingon")),
        ("accent_wrong_speaker",
         accent(0, "speaker_id", "ZZZ")),
        ("accent_wrong_clip",
         accent(0, "l2_arctic_clip_id", "arctic_a9999")),
        ("accent_missing_field",
         accent_drop(0, "permission_record_sha256")),
        ("accent_extra_field",
         accent(0, "extra_field", "x")),
        ("accent_relative_path",
         accent(0, "path", "relative.wav")),
        ("accent_nonfinite_duration",
         accent(0, "duration_samples", math.nan)),
        ("accent_negative_duration",
         accent(0, "duration_samples", -1)),
        ("accent_empty_transcript",
         accent(0, "transcript", "")),
        ("accent_duplicate_path",
         accent(1, "path", _synthetic_file("ABA_arctic_a0046.wav"))),
        ("accent_missing_asset",
         accent(0, "path", _synthetic_file("missing-accent.wav"))),
        ("accent_hash_mismatch",
         accent(0, "sha256", "0" * 64)),
        ("accent_bad_permission_sha",
         accent(0, "permission_record_sha256", "not-a-sha")),
    ]
    results = [_invoke(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case order mismatch")
    return results


def build_control() -> Dict[str, Any]:
    import copy

    files = _synthetic_files()
    valid = validate_synthetic_manifest()
    invalid_manifest = copy.deepcopy(_synthetic_manifest())
    invalid_manifest.pop("consent_record_sha256")
    invalid = _invoke(
        "missing_consent_record_field",
        lambda: validate_manifest(invalid_manifest, _MemoryResolver(files)))
    missing_manifest = copy.deepcopy(_synthetic_manifest())
    missing_manifest["target_path"] = _synthetic_file("missing-target.flac")
    missing = _invoke(
        "missing_target_file",
        lambda: validate_manifest(missing_manifest, _MemoryResolver(files)))
    nonfinite_manifest = copy.deepcopy(_synthetic_manifest())
    nonfinite_manifest["sample_rate_hz"] = math.nan
    nonfinite = _invoke(
        "nonfinite_sample_rate",
        lambda: validate_manifest(nonfinite_manifest, _MemoryResolver(files)))
    adverse = run_adverse_controls()
    aggregation = aggregate_evidence(_control_records())
    return {
        "control_id": CONTROL_ID,
        "model_executed": False,
        "executor": "absent",
        "qualification_effect": "none",
        "synthetic_fixture_is_not_a_real_manifest": True,
        "real_data_admitted": False,
        "declared_ids_are_task_ids_not_provenance": True,
        "geometry": {
            "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "entry_counts": {"source": 1, "accent": 3, "target": 1},
        "accent_group_counts": valid["accent_group_counts"],
        "valid_case": {
            "case": "complete_synthetic_manifest_shape",
            "result": "accepted" if valid["accepted"] else "rejected",
            "admitted_for_evaluation": valid["admitted_for_evaluation"],
            "accepted_for_qualification": valid["accepted_for_qualification"],
            "manifest_projection_sha256":
                valid["manifest_projection_sha256"],
            "files_checked": valid["files_checked"],
        },
        "invalid_case": invalid,
        "missing_case": missing,
        "nonfinite_case": nonfinite,
        "aggregation": aggregation,
        "adverse": adverse,
        "evidence_class_counts": {
            name: 0 for name in EVIDENCE_CLASSES if name != "synthetic"},
        "note": (
            "Synthetic structural control only.  Payloads are analytic and "
            "the paths are memory-resident placeholders.  The declared IDs "
            "are the task's recorded identifiers, not proof of provenance.  "
            "Acceptance never admits real data and never qualifies a result."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_manifest",
        "path": SOURCE_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": "No source manifest exists; only a research README prose table.",
    },
    {
        "id": "accent_group_manifest",
        "path": ACCENT_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "Three local accent copies exist without a manifest, consent or "
            "published digest."),
    },
    {
        "id": "target_reference_provenance",
        "path": TARGET_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "The target clip is hash-pinned, but its dataset and licence "
            "provenance remain unconfirmed."),
    },
    {
        "id": "consent_record",
        "path": CONSENT_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": "No per-speaker consent for conversion or output use exists.",
    },
    {
        "id": "terms_and_redistribution_record",
        "path": TERMS_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No attribution, noncommercial boundary or redistribution grant "
            "record exists."),
    },
    {
        "id": "cohort_and_held_out_split",
        "path": COHORT_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": "No frozen cohort, roles, held-out split or controls exist.",
    },
    {
        "id": "scoring_ground_truth_plan",
        "path": SCORING_PLAN_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No pinned scorer, manual transcript, accent ground truth, "
            "aggregation or failed-item policy exists."),
    },
    {
        "id": "adapter_and_release_approval",
        "path": APPROVAL_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No opt-in adapter decision, independent review, default policy "
            "or release approval exists."),
    },
)


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
        for item, requirement, status in EVIDENCE_REQUIREMENTS
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
            "reason": (
                "No machine-readable source, accent-group, target-reference, "
                "consent, terms, cohort, scoring or approval manifest exists. "
                "Five local clip copies are present and hash-pinned as "
                "observations only; target provenance is unconfirmed, the "
                "L2-ARCTIC copies carry no per-speaker consent, the TokAN "
                "sample copy has no visible licence and no redistribution "
                "grant exists.  No clip is admitted and no metric is "
                "measured."),
        },
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
        "manifest_contract": MANIFEST_CONTRACT,
        "observed_artifacts": audit["observed"]["observed_artifacts"],
        "asset_audit": audit,
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "evidence_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_measurements": None,
            "scorer_pin": None,
            "cohort_pin": None,
            "aggregation_plan": None,
            "note": (
                "The evidence profile requires a pinned scorer, corpus and "
                "cohort, aggregation, failed items and controls, plus one "
                "invalid/missing and one representative valid case through the "
                "reported bundle.  Only source observations and a synthetic "
                "structural control exist; nothing is satisfied for "
                "qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
            "invalid_case_rejected": (
                control["invalid_case"]["result"] == "rejected"),
            "missing_case_rejected": (
                control["missing_case"]["result"] == "rejected"),
            "nonfinite_case_rejected": (
                control["nonfinite_case"]["result"] == "rejected"),
            "missing_result_never_qualifies": True,
            "real_data_not_admitted": True,
            "manifests_not_fabricated": True,
            "consent_not_inferred": True,
            "evidence_classes_not_pooled": True,
            "adverse": control["adverse"],
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": list(RESERVED_ABSENT_PATHS),
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no audio codec, model or scoring runtime is imported.",
            "Present clip bytes are read at fixed workspace paths solely to compute SHA-256 observations; no audio is decoded, copied or played.",
            "No network request, download, corpus staging, consent inference or rights grant occurs.",
            "The synthetic manifest control uses analytic payloads in memory and never touches real files.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }
