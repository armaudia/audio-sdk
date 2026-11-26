# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-BREATH-DETECTOR-REMOVAL.

The task is a breath detector / removal feasibility investigation. The merged
research evidence contains only a synthetic click-gate screen whose record name
mentions breaths but whose reports explicitly state that natural clicks and
breaths were not evaluated. No breath-detector or breath-removal source
checkout, resolved 40-hex revision, model weights, calibration, exact target
definition, natural event labels, rights record, hash-pinned runtime, parity
vector or matched cohort exists in this workspace.

This module therefore never imports NumPy, SciPy, PyTorch, torch, ONNX, a
neural runtime, an audio codec or a device API. It never loads or executes a
breath detector or removal model, never reads or writes real audio, never
downloads anything and never measures a device clock. It provides three
bounded, verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, revision, weights, policy, labels, runtime, licence and rights
  records and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic synthetic oracle-label interval-accounting control that
  checks PCM validity, exact source-sample mapping, breath-policy label
  separation, duration conservation, finite/peak bounds and the declared gate
  mask without performing breath detection or asserting removal quality.

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

TASK = "SDK-BREATH-DETECTOR-REMOVAL"
TITLE = "Breath detector / removal"
SLUG = "breath-detector-removal"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d7f4f9d4426b007be8fc9c24f3a1d58203b69257"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

# The merged evidence does not record a candidate project page, repository or
# resolved revision for breath detection/removal.  None is invented here.
UPSTREAM_NAME = "breath detector / removal (no pinned candidate)"
UPSTREAM_PROJECT_URL: Optional[str] = None
UPSTREAM_REPO_URL: Optional[str] = None
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
TASK_GEOMETRY_STATUS = "unestablished"

# Control geometry is exactly the public SDK v0 input boundary.  The candidate
# geometry beyond that boundary is not established.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_SECONDS = 3
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62_500

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
MISSING_SOURCE_PATH = (
    "research/voice-enhancement-20261101/repos/breath-detector-removal")
MISSING_WEIGHTS_PATH = "data/models/breath-detector-removal"
MISSING_POLICY_PATH = "data/policies/breath-detector-removal-policy.json"
MISSING_LABELS_PATH = "data/labels/breath-events.json"
RUNTIME_ENV_PATH = "data/envs/breath-detector-removal"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
RIGHTS_RECORD_PATH = "data/rights/breath-detector-removal-rights.json"
COHORT_MANIFEST_PATH = (
    "data/runs/breath-detector-removal-cohort/manifest.json")
PARITY_MANIFEST_PATH = (
    "data/runs/breath-detector-removal-parity/manifest.json")
OUTPUT_USE_GRANT_PATH = (
    "data/rights/breath-detector-removal-output-use-grant.json")

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    MISSING_SOURCE_PATH,
    "research/voice-enhancement-20261101/repos/breath_detector",
    "research/voice-enhancement-20261101/repos/breath-removal",
    "research/voice-enhancement-20261101/repos/breath_removal",
    "research/voice-enhancement-20261101/repos/breathgate",
    "data/checkouts/breath-detector-removal",
    "data/checkouts/breath-detector",
    "data/checkouts/breath-removal",
    MISSING_WEIGHTS_PATH,
    "data/models/breath-detector",
    "data/models/breath-removal",
    "data/weights/breath-detector-removal",
    RUNTIME_ENV_PATH,
    RUNTIME_LOCK_PATH,
    MISSING_POLICY_PATH,
    MISSING_LABELS_PATH,
    RIGHTS_RECORD_PATH,
    OUTPUT_USE_GRANT_PATH,
    COHORT_MANIFEST_PATH,
    PARITY_MANIFEST_PATH,
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
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md":
        "b8a42f9b0b782ad3aaa0be64da0d23b37c3c54b65a31caf252a4cd2ace88841e",
    "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md":
        "ae4b0065eabbb62fe8880c7a04dee146415d463c5ae6676db6329147a901e1cc",
    "research/voice-enhancement-20261101/agent-matrix-audit/REPORT.md":
        "865b0031d357b7009c2876f997ca188440451fb65d5cef3561e9848f34eaf1d0",
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
    "docs/task-evidence/median-residual-click-gate/README.md":
        "86561ef9f77bc62bcf0f1a090e33908c815d3f6bf09935a1798eb92e4123a389",
    "docs/task-evidence/median-residual-click-gate/adapter.json":
        "0b4f32bed804331ee740d91f076fd531e62293df52a9672ff48894f0cc533bb1",
    "docs/task-evidence/median-residual-click-gate/report.json":
        "d3a619a280bc9a538f6bd1bb643d0919fab53e138a47275710f58c59ac509139",
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
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "task_geometry_status": TASK_GEOMETRY_STATUS,
    "task_geometry_asserted": False,
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_frame_samples": SDK_FRAME_SAMPLES,
    "control_mode": "oracle_label_interval_accounting",
    "control_performs_breath_detection": False,
    "control_performs_model_inference": False,
    "control_uses_oracle_labels": True,
    "control_applies_declared_gate": True,
    "control_output_is_candidate_removal": False,
    "control_is_quality_result": False,
    "control_incremental_streaming": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "abi_change": False,
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
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
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "acoustic_removal_reference_produced": False,
    "breath_detection_performed": False,
    "detector_executed": False,
    "detector_weights_loaded": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_breath_labels": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No breath detector, removal model, classifier or configuration is loaded or executed.",
    "No NumPy, SciPy, PyTorch, torch, ONNX, CUDA, SoundFile or neural runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, natural breath event label or consent record is consumed.",
    "No breath detection precision, recall, false-positive, false-negative, suppression, quality, SI-SDR, STOI, WER, MOS, latency, memory or RTF is measured here.",
    "The synthetic oracle-label interval-accounting control performs no breath detection and is never candidate removal output.",
    "The median-residual click gate and its reports are adjacent transient-interference evidence and are not attributed to breath detection or removal.",
    "The candidate-matrix row name includes breaths, but the merged screen tested synthetic clicks only; natural breaths remain untested.",
    "Breaths may be expressive or linguistic turn cues, so a removal policy and consent/rights review are prerequisites, not implementation details.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "path": MISSING_SOURCE_PATH,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "upstream_revision",
        "recorded_url": None,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "detector_weights",
        "path": MISSING_WEIGHTS_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "exact_runtime",
        "path": RUNTIME_ENV_PATH,
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_license_record",
        "required": True,
        "status": "absent",
    },
    {
        "id": "breath_target_and_policy",
        "path": MISSING_POLICY_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "natural_breath_event_labels",
        "path": MISSING_LABELS_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_output_use",
        "path": RIGHTS_RECORD_PATH,
        "output_use_grant_path": OUTPUT_USE_GRANT_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "cohort_and_parity",
        "cohort_path": COHORT_MANIFEST_PATH,
        "parity_path": PARITY_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "detector_source_path",
    "source_revision",
    "detector_weights_path",
    "detector_weights_sha256",
    "config_path",
    "config_sha256",
    "calibration_path",
    "calibration_sha256",
    "runtime_path",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "license_record_path",
    "license_record_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "breath_policy_path",
    "breath_policy_sha256",
    "event_label_manifest_path",
    "event_label_manifest_sha256",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "parity_vector_path",
    "parity_vector_sha256",
    "output_use_grant_path",
    "output_use_grant_sha256",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("detector_weights_path", "detector_weights_sha256"),
    ("config_path", "config_sha256"),
    ("calibration_path", "calibration_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("breath_policy_path", "breath_policy_sha256"),
    ("event_label_manifest_path", "event_label_manifest_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
    ("output_use_grant_path", "output_use_grant_sha256"),
)
CALLER_DIR_FIELDS = ("detector_source_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "frame_causal_breath_detection_and_removal"

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": (
        "audio-sdk/breath-detector-removal/caller-supplied-asset/0.1"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_geometry_policy_labels_"
        "rights_and_variant_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "frame_samples": SDK_FRAME_SAMPLES,
        "status": (
            "exact_input_boundary_only; candidate detection window, lookahead, "
            "policy and removal geometry unestablished"),
    },
    "breath_policy_required": True,
    "natural_event_labels_required": True,
    "output_use_grant_required": True,
    "notes": (
        "Every detector weight, config, calibration, licence, rights record, "
        "breath policy, natural event label manifest, cohort manifest, parity "
        "vector, runtime lock and output-use grant must exist at an absolute "
        "path and match its declared SHA-256 before a caller may process "
        "audio. No upstream revision is pinned because the merged evidence "
        "records no breath-detector or breath-removal candidate source."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "breath_candidate_source_absent",
        "state": "absent",
        "requirement": (
            "Supply one exact breath detector/removal source checkout at an "
            "immutable 40-hex revision under "
            "research/voice-enhancement-20261101/repos/breath-detector-removal "
            "or data/checkouts/breath-detector-removal; no such checkout "
            "exists in the workspace."),
    },
    {
        "id": "breath_detector_weights_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact detector/classifier/removal weights, model "
            "configuration and calibration with byte counts and SHA-256 "
            "values at one immutable revision; no weight was downloaded or "
            "identified by digest in the merged evidence."),
    },
    {
        "id": "task_geometry_and_policy_unestablished",
        "state": "absent",
        "requirement": (
            "Record the exact sample rate, channels, frame/hop, detection "
            "window, lookahead, content delay, removal gain/attenuation "
            "recipe, final-padding rule and breath target/preservation policy "
            "in a pinned config; the merged evidence contains no candidate "
            "geometry or policy."),
    },
    {
        "id": "runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete lock at "
            "data/envs/breath-detector-removal/requirements.lock and a "
            "recorded platform; no environment, package pin or lock exists."),
    },
    {
        "id": "source_license_unverified",
        "state": "absent",
        "requirement": (
            "Add the upstream artifact licence and terms at the resolved "
            "commit; no licence file, terms statement or redistribution "
            "grant is recorded in the merged evidence or present in the "
            "workspace."),
    },
    {
        "id": "natural_breath_labels_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared natural breath event-label manifest "
            "with exact source intervals, removable versus preserve labels, "
            "speaker/noise strata, known positives and negatives; the merged "
            "click screen explicitly leaves natural clicks and breaths "
            "untested."),
    },
    {
        "id": "rights_and_consent_uncleared",
        "state": "absent",
        "requirement": (
            "Clear voice/breath recording consent, speaker and training-data "
            "rights, source-audio and output-use rights, and redistribution "
            "terms, then add the rights record and output-use grant; no "
            "consent or rights record exists."),
    },
    {
        "id": "removal_parity_and_cohort_absent",
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime detection/removal output plus "
            "a rights-cleared held-out cohort scoring event precision/recall, "
            "stratified FN/FP, speech/consonant preservation, suppression, "
            "peaks, alignment and authorized listening; no output, parity "
            "vector, cohort, timing or benchmark result exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex source revision, detector weights, configuration, "
        "calibration and metadata SHA-256 values and the source licence match "
        "exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform.",
    ),
    (
        "artifact_rights_and_licence",
        "Source, weight, training-data, breath-recording consent, source-audio, "
        "output-use and redistribution rights are cleared with notices.",
    ),
    (
        "breath_target_and_policy",
        "The exact breath target definition and preservation policy are "
        "approved, including expressive/linguistic turn cues and non-removable "
        "breath classes.",
    ),
    (
        "event_label_cohort_and_scoring",
        "A rights-cleared held-out natural breath cohort scores event "
        "precision/recall and stratified false negatives/positives against "
        "known positives, negatives and adjacent speech transients.",
    ),
    (
        "removal_preservation_and_quality",
        "Paired and unpaired evidence separates suppression from speech and "
        "consonant preservation, peaks, nonfinite failures, alignment and "
        "authorized listening.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in provider intake, licence review, descriptor review and "
        "an independent public-surface decision are complete; the component "
        "ships optional only.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

RATE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "source_output_mapping",
        "Measure exact source-sample to output-sample mapping, content delay "
        "and the final partial window for the intended frame path.",
        "structural_only",
    ),
    (
        "duration_and_buffering",
        "Measure duration, playback buffering, fill/flush and rebuffer "
        "behavior under 1x playback.",
        "structural_only",
    ),
    (
        "pitch_and_transient_audibility",
        "Measure pitch and transient audibility for 1x, rate changes, music "
        "and speech.",
        "not_measured",
    ),
    (
        "rate_case_coverage",
        "Include 1x, rate changes, unfamiliar speech, music, silence, "
        "rebuffer, drift and the final partial window.",
        "absent",
    ),
    (
        "source_timestamp_decisions",
        "Keep pause, filler or breath-removal decisions tied to exact source "
        "timestamps rather than a separate wall clock.",
        "synthetic_only",
    ),
    (
        "speech_preservation",
        "Measure speech and consonant preservation for every removal decision.",
        "not_measured",
    ),
    (
        "breath_target_definition",
        "Define the breath target and preservation policy, including "
        "expressive/linguistic turn cues and non-removable classes.",
        "absent",
    ),
    (
        "natural_event_labels",
        "Score natural breath event labels with precision, recall and "
        "stratified false negatives/positives.",
        "absent",
    ),
    (
        "removal_quality_and_listening",
        "Score paired removal quality and authorized listening separately "
        "where permitted references exist.",
        "absent",
    ),
    (
        "resource_and_device_timing",
        "Measure memory, CPU/deadline and actual availability on the intended "
        "device.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "adjacent_sibling_reported_not_measured_here",
    "candidate_matrix_source":
        "research/voice-enhancement-20261101/candidate_matrix.csv",
    "candidate_matrix_sha256": SOURCE_PINS[
        "research/voice-enhancement-20261101/candidate_matrix.csv"],
    "candidate_matrix_record": 38,
    "evidence_line": 39,
    "record_name": "Waveform gates for breaths/clicks",
    "record_status": "partially evaluated",
    "record_finding": (
        "Fixed 7-sample median-residual gate screened on 12 EARS clips with "
        "click widths 1/2/3/5 samples and amplitudes ±0.20/0.40/0.75: 0 "
        "false positives in synthetic conditions, but missed all ±0.20 "
        "clicks and all width-5 pulses; natural clicks and breaths untested."),
    "record_baseline": [
        "Identity",
        "oracle-labelled click interpolation",
        "previous single-sample gate screen",
    ],
    "record_report_paths": [
        "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md",
        "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md",
        "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
        "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
    ],
    "project_url": None,
    "repository_url": None,
    "breath_specific_result_present": False,
    "pinned_candidate_source_present": False,
    "source_reports": [
        {
            "path": (
                "research/voice-enhancement-20261101/agent-segmentation/"
                "REPORT.md"),
            "sha256": SOURCE_PINS[
                "research/voice-enhancement-20261101/agent-segmentation/"
                "REPORT.md"],
            "finding": (
                "No breath-removal candidate/evaluation. A click/transient "
                "category exists separately; breath suppression requires "
                "policy labels because breaths can be expressive or "
                "linguistic turn cues."),
        },
        {
            "path": (
                "research/voice-enhancement-20261101/agent-vad-asr-trials/"
                "REPORT.md"),
            "sha256": SOURCE_PINS[
                "research/voice-enhancement-20261101/agent-vad-asr-trials/"
                "REPORT.md"],
            "finding": (
                "No event-level click/breath truth labels were available; "
                "deleting breaths may remove useful cues and no breath gate "
                "was tested."),
        },
        {
            "path": (
                "research/voice-enhancement-20261101/"
                "agent-click-gate-expanded/REPORT.md"),
            "sha256": SOURCE_PINS[
                "research/voice-enhancement-20261101/"
                "agent-click-gate-expanded/REPORT.md"],
            "finding": (
                "Synthetic click evidence only; does not evaluate natural "
                "clicks, breaths, speech disfluencies or live microphone "
                "use."),
        },
    ],
    "sibling_context_not_attributed": [
        "The median-residual click gate is a transient-interference control; "
        "its synthetic clicks are not breath events and its outputs are not "
        "breath detection or removal results.",
        "The click-gate reports state that natural clicks and breaths remain "
        "untested; the merged row name does not create breath evidence.",
        "The segmentation report records no breath-removal candidate or "
        "evaluation and requires policy labels before breath suppression.",
        "The VAD/ASR report records no event-level breath truth labels and "
        "warns that deleting breaths may remove useful cues.",
        "No upstream breath detector/removal project page, repository or "
        "revision is pinned in the merged evidence.",
    ],
    "notes": (
        "The matrix row name includes breaths, but the merged evaluation is a "
        "synthetic click screen only. No breath detection or removal output, "
        "metric, natural label, policy, source, weight or runtime is "
        "attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_oracle_label_breath_interval_accounting_"
    "not_detector_output")

PCM_SAMPLE_CAP = 10_000_000

# Deterministic oracle label ledger.  These intervals are declared, not
# detected.  They exercise policy separation and exact accounting only.
SYNTHETIC_BREATH_INTERVALS: Tuple[Dict[str, Any], ...] = (
    {"start": 3200, "end": 4800, "label": "breath_removable"},
    {"start": 11200, "end": 12800, "label": "breath_preserve"},
    {"start": 21600, "end": 23200, "label": "breath_removable"},
    {"start": 32000, "end": 33600, "label": "breath_preserve"},
    {"start": 41600, "end": 43200, "label": "breath_removable"},
)

BREATH_LABELS = ("breath_preserve", "breath_removable")
INTERVAL_FIELDS = ("end", "label", "start")

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
    "intervals_not_sequence",
    "intervals_none",
    "intervals_empty",
    "interval_not_object",
    "interval_missing_field",
    "interval_extra_field",
    "interval_bool_start",
    "interval_float_start",
    "interval_negative_start",
    "interval_zero_length",
    "interval_end_before_start",
    "interval_out_of_bounds",
    "interval_overlap",
    "interval_unsorted",
    "interval_unknown_label",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_wrong_rate",
    "manifest_wrong_channels",
    "manifest_wrong_frame_samples",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


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


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Source checkout, asset and absence audit.  Fixed local reads only.
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
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/breath_detector",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/breath-removal",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/breath_removal",
        SOURCE_ROOT / "data/checkouts/breath-detector-removal",
        SOURCE_ROOT / "data/checkouts/breath-detector",
        SOURCE_ROOT / "data/checkouts/breath-removal",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_WEIGHTS_PATH,
        SOURCE_ROOT / "data/models/breath-detector",
        SOURCE_ROOT / "data/models/breath-removal",
        SOURCE_ROOT / "data/weights/breath-detector-removal",
        SOURCE_ROOT / (
            "research/voice-enhancement-20261101/repos/"
            "breath-detector-removal/weights"),
    ]


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
    readme = repository / "README.md" if repository is not None else None
    readme_declares = False
    if readme is not None and readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        readme_declares = ("license" in text or "licence" in text
                           or "copyright" in text)
    weight_paths = _weights_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    output_use_grant = SOURCE_ROOT / OUTPUT_USE_GRANT_PATH
    policy = SOURCE_ROOT / MISSING_POLICY_PATH
    labels = SOURCE_ROOT / MISSING_LABELS_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "source_revision_matches": False,
        "source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.is_dir()}
            for path in source_paths
        ],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "output_use_grant_present": output_use_grant.is_file(),
        "breath_policy_present": policy.is_file(),
        "natural_breath_labels_present": labels.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "upstream_revision": UPSTREAM_REVISION,
            "pinned_candidate_source": False,
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
# Deterministic synthetic PCM and oracle-label breath interval accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_input_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x42524541
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise Reject("sample rate must be an integer")
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("channels must be an integer")
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
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def validate_breath_intervals(intervals: Any,
                              total_samples: int) -> List[Dict[str, Any]]:
    if isinstance(total_samples, bool) or not isinstance(total_samples, int):
        raise Reject("total_samples must be an integer")
    if total_samples <= 0:
        raise Reject("total_samples must be positive")
    if not isinstance(intervals, (list, tuple)):
        raise Reject("intervals must be a sequence")
    if not intervals:
        raise Reject("intervals must be nonempty")
    checked: List[Dict[str, Any]] = []
    previous_end = 0
    previous_start = -1
    for index, item in enumerate(intervals):
        if not isinstance(item, dict):
            raise Reject(f"interval {index} is not an object")
        keys = set(item)
        missing = sorted(set(INTERVAL_FIELDS) - keys)
        extra = sorted(keys - set(INTERVAL_FIELDS))
        if missing:
            raise Reject(
                f"interval {index} missing fields: " + ",".join(missing))
        if extra:
            raise Reject(
                f"interval {index} has unknown fields: " + ",".join(extra))
        start = item["start"]
        end = item["end"]
        label = item["label"]
        if isinstance(start, bool) or not isinstance(start, int):
            raise Reject(f"interval {index} start must be an integer")
        if isinstance(end, bool) or not isinstance(end, int):
            raise Reject(f"interval {index} end must be an integer")
        if start < 0:
            raise Reject(f"interval {index} start is negative")
        if end < start:
            raise Reject(f"interval {index} end is before start")
        if end == start:
            raise Reject(f"interval {index} has zero length")
        if end > total_samples:
            raise Reject(f"interval {index} end exceeds the signal")
        if start < previous_start:
            raise Reject(f"interval {index} is unsorted")
        if start < previous_end:
            raise Reject(f"interval {index} overlaps the previous interval")
        if label not in BREATH_LABELS:
            raise Reject(f"interval {index} label is not an admitted breath label")
        checked.append({"start": start, "end": end, "label": label})
        previous_start = start
        previous_end = end
    return checked


def synthetic_gated_output_pcm(signal: Sequence[float],
                               intervals: Sequence[Dict[str, Any]]
                               ) -> List[float]:
    """Apply the declared removable-interval gate.  No detector runs."""
    values = validate_pcm(signal)
    checked = validate_breath_intervals(intervals, len(values))
    gated = list(values)
    for interval in checked:
        if interval["label"] != "breath_removable":
            continue
        for index in range(interval["start"], interval["end"]):
            gated[index] = 0.0
    return gated


def _interval_ledger(intervals: Sequence[Dict[str, Any]]
                     ) -> List[Dict[str, Any]]:
    ledger: List[Dict[str, Any]] = []
    for interval in intervals:
        start = interval["start"]
        end = interval["end"]
        duration = end - start
        ledger.append({
            "start": start,
            "end": end,
            "label": interval["label"],
            "decision": (
                "gate_to_zero" if interval["label"] == "breath_removable"
                else "preserve"),
            "start_ns": str(start * NS_PER_SAMPLE),
            "end_ns": str(end * NS_PER_SAMPLE),
            "duration_ns": str(duration * NS_PER_SAMPLE),
            "duration_s": fraction_text(
                Fraction(duration, CONTROL_SAMPLE_RATE_HZ)),
        })
    return ledger


def breath_interval_accounting(signal: Any,
                               intervals: Any) -> Dict[str, Any]:
    """Exact oracle-label interval accounting.  No detection or model runs."""
    values = validate_pcm(signal)
    checked = validate_breath_intervals(intervals, len(values))
    gated = synthetic_gated_output_pcm(values, checked)
    removable = [item for item in checked
                 if item["label"] == "breath_removable"]
    preserved = [item for item in checked
                 if item["label"] == "breath_preserve"]
    removable_indices = set()
    for item in removable:
        removable_indices.update(range(item["start"], item["end"]))
    preserved_indices = set()
    for item in preserved:
        preserved_indices.update(range(item["start"], item["end"]))
    changed = [index for index, (before, after) in enumerate(zip(values, gated))
               if before != after]
    changed_set = set(changed)
    changed_outside_removable = sorted(changed_set - removable_indices)
    changed_in_preserved = sorted(changed_set & preserved_indices)
    removable_samples = sum(item["end"] - item["start"]
                            for item in removable)
    preserved_samples = sum(item["end"] - item["start"]
                            for item in preserved)
    breath_samples = removable_samples + preserved_samples
    duration = Fraction(len(values), CONTROL_SAMPLE_RATE_HZ)
    return {
        "input_samples": len(values),
        "output_samples": len(gated),
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "duration_s": fraction_text(duration),
        "output_duration_s": fraction_text(
            Fraction(len(gated), CONTROL_SAMPLE_RATE_HZ)),
        "duration_ratio": "1",
        "duration_conserved": len(gated) == len(values),
        "source_clock_ns_per_sample": NS_PER_SAMPLE,
        "removable_breath_samples": removable_samples,
        "preserved_breath_samples": preserved_samples,
        "breath_samples": breath_samples,
        "non_breath_samples": len(values) - breath_samples,
        "removable_breath_duration_s": fraction_text(
            Fraction(removable_samples, CONTROL_SAMPLE_RATE_HZ)),
        "preserved_breath_duration_s": fraction_text(
            Fraction(preserved_samples, CONTROL_SAMPLE_RATE_HZ)),
        "changed_samples": len(changed),
        "already_zero_removable_samples": removable_samples - len(
            changed_set & removable_indices),
        "changed_samples_outside_removable": len(changed_outside_removable),
        "changed_samples_in_preserved_breath": len(changed_in_preserved),
        "interval_ledger": _interval_ledger(checked),
        "decision_timestamps_tied_to_source": True,
        "detector_executed": False,
        "performs_breath_detection": False,
        "performs_model_inference": False,
        "uses_oracle_labels": True,
        "is_candidate_removal_output": False,
        "qualification_effect": "none",
        "note": (
            "Oracle labels are declared, not detected. The gate is a "
            "deterministic accounting surrogate, not candidate removal "
            "output and not a quality, preservation or listening result."),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_input = synthetic_input_pcm()
    good_intervals = [dict(item) for item in SYNTHETIC_BREATH_INTERVALS]
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

    existing = _existing_file_manifest()
    total = len(good_input)
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_input, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_input, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("intervals_not_sequence",
         lambda: validate_breath_intervals(b"\x00", total)),
        ("intervals_none", lambda: validate_breath_intervals(None, total)),
        ("intervals_empty", lambda: validate_breath_intervals([], total)),
        ("interval_not_object", lambda: validate_breath_intervals([1], total)),
        ("interval_missing_field", lambda: validate_breath_intervals(
            [{"start": 0, "end": 1}], total)),
        ("interval_extra_field", lambda: validate_breath_intervals(
            [{"start": 0, "end": 1, "label": "breath_removable",
              "extra": 1}], total)),
        ("interval_bool_start", lambda: validate_breath_intervals(
            [{"start": True, "end": 1, "label": "breath_removable"}], total)),
        ("interval_float_start", lambda: validate_breath_intervals(
            [{"start": 0.0, "end": 1, "label": "breath_removable"}], total)),
        ("interval_negative_start", lambda: validate_breath_intervals(
            [{"start": -1, "end": 1, "label": "breath_removable"}], total)),
        ("interval_zero_length", lambda: validate_breath_intervals(
            [{"start": 10, "end": 10, "label": "breath_removable"}], total)),
        ("interval_end_before_start", lambda: validate_breath_intervals(
            [{"start": 10, "end": 9, "label": "breath_removable"}], total)),
        ("interval_out_of_bounds", lambda: validate_breath_intervals(
            [{"start": 0, "end": total + 1,
              "label": "breath_removable"}], total)),
        ("interval_overlap", lambda: validate_breath_intervals(
            [{"start": 0, "end": 10, "label": "breath_removable"},
             {"start": 5, "end": 15, "label": "breath_preserve"}], total)),
        ("interval_unsorted", lambda: validate_breath_intervals(
            [{"start": 20, "end": 30, "label": "breath_removable"},
             {"start": 0, "end": 10, "label": "breath_preserve"}], total)),
        ("interval_unknown_label", lambda: validate_breath_intervals(
            [{"start": 0, "end": 1, "label": "click"}], total)),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("breath_policy_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "detector_weights_path", "weights/breath.bin")),
        ("manifest_bad_sha", wrong("detector_weights_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "7dae8a2")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "offline_batch_removal")),
        ("manifest_wrong_rate", wrong("sample_rate_hz", 48000)),
        ("manifest_wrong_channels", wrong("channels", 2)),
        ("manifest_wrong_frame_samples", wrong("frame_samples", 512)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, detector_weights_path=(
                "/nonexistent/breath-evidence/weights.bin")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/breath-evidence/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, detector_weights_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case order mismatch")
    if any(item["result"] != "rejected" for item in results):
        raise Reject("an adverse control was not rejected")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/breath-detector-removal-evidence-fixture"
    digest = "0" * 64
    return {
        "detector_source_path": root + "/source",
        "source_revision": "0" * 40,
        "detector_weights_path": root + "/weights.bin",
        "detector_weights_sha256": digest,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "calibration_path": root + "/calibration.json",
        "calibration_sha256": digest,
        "runtime_path": root + "/runtime",
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "breath_policy_path": root + "/breath-policy.json",
        "breath_policy_sha256": digest,
        "event_label_manifest_path": root + "/breath-events.json",
        "event_label_manifest_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "output_use_grant_path": root + "/output-use-grant.json",
        "output_use_grant_sha256": digest,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading a model.  Duplicate paths are allowed; each pair carries the real
    digest so a single corrupted digest reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "detector_weights_path": HERE / "reference.py",
        "config_path": HERE / "README.md",
        "calibration_path": HERE / "verify.py",
        "runtime_lock_path": HERE / "run.py",
        "license_record_path": HERE / "test_reference.py",
        "rights_record_path": HERE / "reference.py",
        "breath_policy_path": HERE / "README.md",
        "event_label_manifest_path": HERE / "verify.py",
        "cohort_manifest_path": HERE / "run.py",
        "parity_vector_path": HERE / "test_reference.py",
        "output_use_grant_path": HERE / "reference.py",
    }
    manifest: Dict[str, Any] = {
        "detector_source_path": str(HERE),
        "source_revision": "a" * 40,
        "runtime_path": str(SDK_ROOT),
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "variant": CALLER_VARIANT,
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


def _int_field(manifest: Dict[str, Any], field: str) -> int:
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
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    sample_rate = _int_field(manifest, "sample_rate_hz")
    if sample_rate != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz mismatch")
    channels = _int_field(manifest, "channels")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    frame_samples = _int_field(manifest, "frame_samples")
    if frame_samples != SDK_FRAME_SAMPLES:
        raise Reject("manifest frame_samples mismatch")
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
        "source_revision": revision,
        "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "variant": CALLER_VARIANT,
        "sample_rate_hz": sample_rate,
        "channels": CHANNELS,
        "frame_samples": frame_samples,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "breath_policy_checked": True,
        "natural_event_labels_checked": True,
        "output_use_grant_checked": True,
        "detector_executed": False,
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_input_pcm()
    intervals = [dict(item) for item in SYNTHETIC_BREATH_INTERVALS]
    accounting = breath_interval_accounting(source, intervals)
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    gated = synthetic_gated_output_pcm(source, intervals)
    gated_summary = pcm_summary(gated, CONTROL_SAMPLE_RATE_HZ)
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "detector_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "oracle_label_interval_accounting",
            "incremental_streaming": False,
            "performs_breath_detection": False,
            "performs_model_inference": False,
            "uses_oracle_labels": True,
        },
        "input_pcm": source_summary,
        "declared_gated_output_pcm": gated_summary,
        "oracle_labels": [
            dict(item) for item in SYNTHETIC_BREATH_INTERVALS
        ],
        "accounting": accounting,
        "rate_profile_controls": {
            "source_output_mapping": (
                "exact integer sample mapping only; no playback or device map"),
            "duration_conserved": accounting["duration_conserved"],
            "source_clock_ns_per_sample": NS_PER_SAMPLE,
            "decisions_tied_to_source_timestamps": True,
            "playback_rate_cases_measured": False,
            "pitch_measured": False,
            "transient_audibility_measured": False,
            "speech_preservation_measured": False,
            "device_buffering_measured": False,
        },
        "acceptance_outcomes": [
            {
                "id": "breath_event_validity_and_timestamps",
                "measured": False,
                "value": None,
                "reason": "oracle-label structural accounting only; no detector",
            },
            {
                "id": "detection_precision_recall",
                "measured": False,
                "value": None,
                "reason": "no detector, natural labels or candidate source",
            },
            {
                "id": "removal_suppression_depth",
                "measured": False,
                "value": None,
                "reason": "no candidate removal output",
            },
            {
                "id": "speech_consonant_preservation",
                "measured": False,
                "value": None,
                "reason": "synthetic oracle gate only; no natural speech or listener",
            },
            {
                "id": "duration_and_source_mapping",
                "measured": False,
                "value": None,
                "reason": "structural accounting only; no runtime",
            },
            {
                "id": "pitch_and_transient_audibility",
                "measured": False,
                "value": None,
                "reason": "no rate run or perceptual measurement",
            },
            {
                "id": "playback_buffering_and_deadline",
                "measured": False,
                "value": None,
                "reason": "no runtime or device clock",
            },
            {
                "id": "quality_and_listening",
                "measured": False,
                "value": None,
                "reason": "no authorized listening panel or clean reference",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "interval_bool_start", "interval_float_start",
                "interval_negative_start", "interval_zero_length",
                "interval_end_before_start", "interval_out_of_bounds",
                "interval_overlap", "interval_unsorted",
                "interval_unknown_label",
                "manifest_wrong_variant", "manifest_wrong_rate",
                "manifest_wrong_channels", "manifest_wrong_frame_samples",
            ],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "intervals_none", "intervals_empty",
                "interval_missing_field", "manifest_missing_field",
                "manifest_missing_asset", "manifest_missing_directory",
            ],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic oracle-label interval-accounting control only. It "
            "performs no breath detection, no model inference and no candidate "
            "acoustic removal evaluation; it is not real speech, not a quality "
            "or timing result and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report and contract models.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision"] is not None
        and observed["license_file_present"]
        and observed["weights_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["output_use_grant_present"]
        and observed["breath_policy_present"]
        and observed["natural_breath_labels_present"]
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
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "license_present": observed["license_file_present"],
        "weights_present": observed["weights_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "output_use_grant_present": observed["output_use_grant_present"],
        "breath_policy_present": observed["breath_policy_present"],
        "natural_breath_labels_present": observed[
            "natural_breath_labels_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No breath detector/removal source, revision, weight, policy, "
            "natural event label, runtime, licence, rights record, output-use "
            "grant, cohort or parity vector was observed. The median-residual "
            "click gate is adjacent transient-interference provenance, not "
            "breath evidence."),
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
        for item, requirement, status in RATE_REQUIREMENTS
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
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "reason": (
                "No breath detector/removal source checkout, full upstream "
                "revision, detector weights, exact target/policy geometry, "
                "hash-pinned runtime, licence, natural breath event labels, "
                "rights record, output-use grant, rights-cleared cohort, "
                "parity vector or local detection/removal output exists. The "
                "merged matrix row is a synthetic click screen that explicitly "
                "leaves natural breaths untested."),
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
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "project_url": UPSTREAM_PROJECT_URL,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "pinned_candidate_source_present": False,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "rate_profile": {
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
                "Only synthetic structural accounting passes. No candidate "
                "runtime, natural breath labels, rate/playback cases, pitch, "
                "transient audibility, speech preservation, device timing or "
                "authorized listening exists, so the rate profile is not "
                "satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "oracle_label_separation_declared": True,
            "detector_absent_and_not_executed": True,
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
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            MISSING_POLICY_PATH,
            MISSING_LABELS_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            RIGHTS_RECORD_PATH,
            OUTPUT_USE_GRANT_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no detector, model or audio runtime is imported.",
            "Fixed workspace paths are probed for source, weights, policy, labels, runtime, rights and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load or timing run occurs.",
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
    report = build_report()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
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
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": report["task_row_identity"],
        "scope": report["scope"],
        "boundary": report["boundary"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_checkout": {
            "path": MISSING_SOURCE_PATH,
            "present": False,
            "project_url": None,
            "repository_url": None,
            "revision": None,
            "revision_pin_available": False,
        },
        "upstream_identity": report["upstream_identity"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "rate_profile_requirements": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "package_status": item["package_status"],
            }
            for item in report["rate_profile"]["required_items"]
        ],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "reproduction": {
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
            "cold_start_regenerations": 3,
            "command": "python3 run.py all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
        },
        "licensing": {
            "copyright": "2026 Tsakanyan Hovhannes",
            "license": "Apache-2.0",
            "json_sidecars": True,
        },
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
