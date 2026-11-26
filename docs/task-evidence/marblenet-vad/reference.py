# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-MARBLENET-VAD.

The exact MarbleNet candidate is a source lead only.  The workspace has no
NVIDIA NeMo checkout, immutable model revision, NGC ``vad_marblenet``
checkpoint, model-card terms, rights record, inference geometry, pinned
runtime, frozen oracle or rights-cleared analysis cohort.  This module
therefore never downloads, reads audio, imports a neural runtime, loads
weights or executes a model.

It provides three verifiable, fail-closed pieces:

* a caller-supplied-reference admission schema that validates exact file
  hashes, geometry, the selected MarbleNet variant and the framewise-versus-
  offline declaration without ever executing the candidate;
* a bounded synthetic analysis-profile control that separates a framewise
  classifier with a fixed left context from a centred offline smoother,
  scores exact half-open sample intervals with unknown regions preserved, and
  reports boundary and availability delay independently;
* a variant-substitution control that proves the general, multilingual and
  telephony leads are distinct identities and are not interchangeable.

Every measured value here is a synthetic contract observation.  Nothing in
this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-MARBLENET-VAD"
TITLE = "MarbleNet VAD"
SLUG = "marblenet-vad"
COMPONENT = "marblenet-vad"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "0cc1e79e592d7fc25f054fcd98824053be281f5e"
BRANCH = "swarm/SDK-MARBLENET-VAD"
REVIEWER = "reviewer-MARBLENET-VAD"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-MARBLENET-VAD")
REPORT_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
ADMISSION_SCHEMA_ID = f"audio-sdk/{SLUG}/admission/0.1"
PROFILE = "analysis"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62_500
SURROGATE_FRAME_SAMPLES = SDK_FRAME_SAMPLES
SURROGATE_TOTAL_FRAMES = 800
SURROGATE_TOTAL_SAMPLES = SURROGATE_TOTAL_FRAMES * SURROGATE_FRAME_SAMPLES
THRESHOLD_MILLI = 500
CAUSAL_CONTEXT_FRAMES = 4
OFFLINE_HALF_WINDOW_FRAMES = 6
OFFLINE_WINDOW_FRAMES = 2 * OFFLINE_HALF_WINDOW_FRAMES + 1


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
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "reports/vad-research/20261028-synthesis-v7.md":
        "2bc353e9d6d648a7e58204e202a5f4a03b75859b58f3fd515ec37216168a5a6c",
    "reports/vad-research/attempt-discovery-20261028-01/findings.md":
        "9d5c555c1c5f2db9ce3eb27da2d3f625c2e25621f6700521f82c8af300ff59d5",
    "reports/vad-research/attempt-neural-01/assessment.md":
        "74232ba9f36976ef1b238bca12305d6c02a614adb73fb2981f6fc3f07133cfe1",
    "reports/vad-research/attempt-open-models-20261028-01/assessment.md":
        "565d4330d625dd8eec9e607811df300749382feffc87ef54d5e4924e09448ad6",
    "research/plans/F02/vad_sources.md":
        "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
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
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "candidate_geometry": "unresolved",
    "candidate_sample_rate_hz": None,
    "candidate_channels": None,
    "candidate_hop_samples": None,
    "candidate_window_samples": None,
    "candidate_lookahead_samples": None,
    "candidate_variant_selected": None,
    "framewise_and_offline_are_separate": True,
    "surrogate_sample_rate_hz": SAMPLE_RATE_HZ,
    "surrogate_channels": CHANNELS,
    "surrogate_hop_samples": SURROGATE_FRAME_SAMPLES,
    "surrogate_threshold_milli": THRESHOLD_MILLI,
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
    "model_variant_selected": False,
    "native_engine_built": False,
    "nemo_dependency_added": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "nemo_runtime_imported": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_marblenet_checkpoint": False,
    "release_claim": False,
    "runtime_imported": False,
    "task_local_only": True,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No MarbleNet source, NeMo checkout, NGC checkpoint, weight, graph or "
    "parameter is loaded or executed.",
    "No PyTorch, NeMo, ONNX Runtime or other neural runtime is imported.",
    "No network request, download, NGC access, staging, cloning or asset "
    "redistribution occurs.",
    "No real audio, corpus, label timeline or device is consumed.",
    "No MarbleNet miss rate, false-alarm rate, AUC, boundary, latency or RTF "
    "is measured here.",
    "The source-reported NGC ``vad_marblenet`` 1.0.0rc1 size of 360.59 kB is "
    "provenance only and is not verified or reproduced.",
    "The general, multilingual and telephony leads are distinct unresolved "
    "checkpoints; none is substituted for another.",
    "No model-card, NGC-term, training-data or weight-rights conclusion is "
    "drawn from the source leads.",
    "The synthetic frame-classifier trace is a contract control, never model "
    "output.",
    "The centred offline smoother is never presented as framewise "
    "availability.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

# ---------------------------------------------------------------------------
# Exact blocker and release-gate model.  Eight gates, all blocked.
# ---------------------------------------------------------------------------

CANDIDATE_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "upstream_implementation_and_revision",
        "kind": "source",
        "required": True,
        "state": "absent",
        "requirement": (
            "Supply the exact reviewed NVIDIA NeMo MarbleNet implementation "
            "at a full 40-hex immutable commit, with the reviewed upstream "
            "license text, a per-file SHA-256 manifest and the frame-VAD API "
            "definitions; do not substitute a mirror or a differently named "
            "architecture."),
        "observed": (
            "The pinned records name NVIDIA/NeMo classification_models.py and "
            "the diarization usage guide, but no checkout, commit, release "
            "tag, code archive or parameter layout exists in the workspace."),
        "gate_ids": ["RG-01"],
    },
    {
        "id": "checkpoint_weights_identity",
        "kind": "weights",
        "required": True,
        "state": "absent",
        "requirement": (
            "Supply the exact caller-selected MarbleNet variant (general, "
            "multilingual or telephony) from an immutable NGC/model revision, "
            "with SHA-256, byte count, weight format, parameter count and "
            "tensor schema; a placeholder, renamed file or cross-variant "
            "substitution is not the pinned candidate."),
        "observed": (
            "No MarbleNet checkpoint, ``.nemo`` archive, weight file, tensor "
            "schema or digest exists at any fixed workspace path. The "
            "source-reported NGC collection size is unverified."),
        "gate_ids": ["RG-01"],
    },
    {
        "id": "artifact_and_training_rights",
        "kind": "rights",
        "required": True,
        "state": "absent",
        "requirement": (
            "Clear NVIDIA NeMo code, NGC checkpoint, model-card, training-"
            "data, corpus, redistribution, derivative-output, account-access "
            "and product-use rights with complete license and notice records; "
            "the repository code license does not by itself establish weight "
            "or NGC terms."),
        "observed": (
            "No MarbleNet/NGC license text, model card, per-weight terms, "
            "training-data statement, notice bundle or product-use decision "
            "is staged."),
        "gate_ids": ["RG-03"],
    },
    {
        "id": "inference_contract_and_geometry",
        "kind": "contract",
        "required": True,
        "state": "absent",
        "requirement": (
            "Document the feature frontend, 16 kHz mono input, analysis "
            "window, frame shift/hop, left context, lookahead, chunking and "
            "padding, output pooling, threshold and smoothing, per-stream "
            "cache reset, state shape and output cadence for the selected "
            "variant, keeping framewise and offline-chunked results separate."),
        "observed": (
            "The pinned records say the model outputs mono 16 kHz frame "
            "predictions and that frame window/shift, lookahead and smoothing "
            "must be preserved, but no exact geometry or inference contract "
            "is verified."),
        "gate_ids": ["RG-04"],
    },
    {
        "id": "pinned_runtime",
        "kind": "runtime",
        "required": True,
        "state": "absent",
        "requirement": (
            "Supply an isolated, hash-pinned runtime with exact NeMo/PyTorch "
            "or reviewed export name/version, Python version, wheel hashes, "
            "platform, deterministic settings and an offline execution "
            "environment."),
        "observed": (
            "No NeMo/Torch runtime environment, package lock, wheel hash or "
            "platform record exists; no neural runtime is imported by this "
            "package."),
        "gate_ids": ["RG-02"],
    },
    {
        "id": "frozen_reference_oracle",
        "kind": "oracle",
        "required": True,
        "state": "absent",
        "requirement": (
            "Freeze caller-supplied PCM, per-frame probabilities, event "
            "intervals and digests for the exact selected variant, with "
            "nonfinite count zero and byte-level reproduction of the "
            "reference output on the exact runtime; oracles from another "
            "variant are rejected."),
        "observed": (
            "No MarbleNet probability vector, event timeline, fresh-session "
            "trace or exact-runtime parity record exists for any variant."),
        "gate_ids": ["RG-02", "RG-06"],
    },
    {
        "id": "rights_cleared_analysis_cohort",
        "kind": "corpus",
        "required": True,
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared held-out cohort with continuous speech "
            "and nonspeech truth, scored regions, unknown spans preserved, "
            "quiet/active/idle/noisy strata, known positives and negatives, "
            "onset and offset labels, sessions and language/speaker groups."),
        "observed": (
            "No cohort is frozen. No MarbleNet-specific labelled corpus is "
            "recorded, and the existing AMI word-span references are not a "
            "continuous-label substitute."),
        "gate_ids": ["RG-05"],
    },
    {
        "id": "target_timing_and_provider_intake",
        "kind": "timing_and_intake",
        "required": True,
        "state": "absent",
        "requirement": (
            "Measure target-device pacing, availability, dropped/stale events, "
            "window/lookahead buffering, resource limits and finite drain for "
            "the selected variant, then complete opt-in provider intake, "
            "descriptor review and independent exact-head release approval."),
        "observed": (
            "No device timing, availability, resource or drain measurement "
            "exists, and no provider intake or independent release review "
            "exists."),
        "gate_ids": ["RG-07", "RG-08"],
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("RG-01",
     "Exact MarbleNet source revision, selected variant checkpoint digest, "
     "byte count, weight format, parameter layout and tensor schema are "
     "pinned to immutable artifacts."),
    ("RG-02",
     "An isolated hash-pinned runtime reproduces an approved exact-runtime "
     "probability and event vector for the selected variant on frozen PCM, "
     "including fresh-session reset and nonfinite rejection."),
    ("RG-03",
     "Code, NGC/weight, model-card, training-data, runtime-dependency, "
     "corpus, access, redistribution, derivative-output and product-use "
     "rights are cleared with complete notices."),
    ("RG-04",
     "The feature frontend, analysis window, hop, context, lookahead, "
     "chunking, pooling, threshold, smoothing, per-stream cache reset and "
     "output cadence are documented; offline results are never presented as "
     "framewise availability."),
    ("RG-05",
     "A rights-cleared held-out cohort with continuous truth, scored regions, "
     "unknown spans, condition strata and known positives/negatives is scored "
     "for exact timestamps, boundary error and stratified FN/FP."),
    ("RG-06",
     "Framewise state, independent per-stream caches, reset, exact source "
     "intervals, dropped/stale events, cross-hop behavior and nonfinite "
     "output are verified at the exact runtime."),
    ("RG-07",
     "Target-device pacing, availability delay, deadline misses, memory and "
     "finite drain are measured on the intended workload with controls."),
    ("RG-08",
     "Explicit opt-in provider intake, descriptor/license review, resource "
     "bounds and independent exact-head release or default-selection approval "
     "are complete; the package remains off by default."),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "no_reviewed_implementation",
        "requirement": (
            "Provide a reviewed runnable MarbleNet implementation from NVIDIA "
            "NeMo and a full 40-hex immutable source revision."),
        "state": (
            "The official repository and frame-VAD API are recorded as leads "
            "only; no checkout, commit, release, version, license text or "
            "per-file digest is staged."),
        "gate_ids": ["RG-01"],
    },
    {
        "id": "no_checkpoint_or_weights",
        "requirement": (
            "Provide the exact selected MarbleNet variant checkpoint with "
            "SHA-256, byte count, parameter layout and tensor schema."),
        "state": (
            "No MarbleNet/NGC checkpoint or weight digest exists in the "
            "workspace; the source-reported collection size is unverified and "
            "no placeholder or cross-variant substitute is accepted."),
        "gate_ids": ["RG-01"],
    },
    {
        "id": "no_runtime_lock",
        "requirement": (
            "Provide an isolated hash-pinned NeMo/PyTorch or reviewed export "
            "runtime, Python version, wheel hashes, platform and "
            "deterministic settings."),
        "state": (
            "No MarbleNet runtime environment or lock exists, and no neural "
            "runtime is imported by this package."),
        "gate_ids": ["RG-02"],
    },
    {
        "id": "no_rights_record",
        "requirement": (
            "Clear code, NGC/weight, model-card, training-data, corpus, "
            "access, redistribution, derivative-output and product-use rights "
            "with notices."),
        "state": (
            "No MarbleNet/NGC license text, model card, per-weight terms or "
            "product-use decision is staged; the repository code license is "
            "unverified and does not establish weight terms."),
        "gate_ids": ["RG-03"],
    },
    {
        "id": "no_geometry_or_inference_contract",
        "requirement": (
            "Document the MarbleNet feature frontend, analysis window, "
            "frame/hop, context, lookahead, chunking, pooling, threshold, "
            "smoothing, per-stream cache and output cadence for both framewise "
            "and offline use."),
        "state": (
            "Only source-reported frame-prediction and window/shift/lookahead "
            "warnings are recorded; no MarbleNet-specific feature, geometry, "
            "lookahead or reset contract is verified."),
        "gate_ids": ["RG-04"],
    },
    {
        "id": "no_frozen_oracle_or_parity",
        "requirement": (
            "Freeze caller-supplied PCM, probabilities, events and digests for "
            "the selected variant and reproduce them byte-for-byte on the "
            "exact runtime."),
        "state": (
            "No MarbleNet probability or event oracle, fresh-session trace or "
            "parity record exists for any variant."),
        "gate_ids": ["RG-02", "RG-06"],
    },
    {
        "id": "no_rights_cleared_cohort",
        "requirement": (
            "Freeze a rights-cleared held-out analysis cohort with continuous "
            "truth, scored regions, unknown spans, strata and boundaries."),
        "state": (
            "No cohort is frozen; no MarbleNet-specific continuous-label "
            "reference exists, and AMI word spans are not a substitute."),
        "gate_ids": ["RG-05"],
    },
    {
        "id": "no_timing_or_intake",
        "requirement": (
            "Measure target-device availability, deadline, resource and drain "
            "behavior and complete opt-in provider intake and release review."),
        "state": (
            "No device timing, availability, resource, drain, provider intake "
            "or independent release review exists."),
        "gate_ids": ["RG-07", "RG-08"],
    },
)

ANALYSIS_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("timestamped_probabilities",
     "Per-frame probabilities with exact half-open source intervals.",
     "control_only_structurally_verified"),
    ("event_boundaries_and_detections",
     "Speech event boundaries and detections with exact sample coordinates.",
     "control_only_structurally_verified"),
    ("quiet_and_active_speech",
     "Separate quiet and active speech strata with matched labels.",
     "blocked_no_real_model_or_cohort"),
    ("idle_noise",
     "Idle noise and nonspeech controls, including false-alarm accounting.",
     "blocked_no_real_model_or_cohort"),
    ("known_positives_and_negatives",
     "Known-positive and known-negative cases with explicit controls.",
     "blocked_no_real_model_or_cohort"),
    ("onset_offset_delay",
     "Onset and offset boundary error in samples and milliseconds.",
     "control_only_structurally_verified"),
    ("stratified_false_negatives_false_positives",
     "Stratified FN/FP and totals computed from real labels.",
     "blocked_no_real_model_or_cohort"),
    ("validity_versus_nonspeech",
     "Known nonspeech is scored; invalid or unknown values never become "
     "nonspeech.",
     "control_only_structurally_verified"),
    ("independent_state",
     "Independent per-stream cache and reset for the framewise path.",
     "blocked_no_real_model_or_runtime"),
    ("exact_source_intervals",
     "Every probability and event maps to exact source sample intervals.",
     "control_only_structurally_verified"),
    ("availability_dropped_stale_events",
     "Availability, dropped and stale event accounting on the target runtime.",
     "blocked_no_target_runtime"),
    ("cross_hop_behavior",
     "160-sample SDK hop, the candidate frame shift and offline chunking are "
     "reconciled explicitly.",
     "blocked_no_candidate_geometry"),
)

VARIANTS: Tuple[Dict[str, Any], ...] = (
    {
        "variant": "general",
        "checkpoint_id": "unresolved_general_marblenet",
        "source_reported_version": None,
        "source_note": (
            "The pinned register says an older general checkpoint exists but "
            "does not record its exact identifier, revision or digest."),
    },
    {
        "variant": "multilingual",
        "checkpoint_id": "vad_multilingual_marblenet",
        "source_reported_version": "1.10.0",
        "source_note": (
            "The pinned discovery note names ``vad_multilingual_marblenet`` "
            "1.10.0 in the NeMo model list; the asset itself is absent and "
            "the name is unverified."),
    },
    {
        "variant": "telephony",
        "checkpoint_id": "unresolved_telephony_marblenet",
        "source_reported_version": None,
        "source_note": (
            "The pinned register says a telephony checkpoint exists but does "
            "not record its exact identifier, revision or digest."),
    },
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "marblenet_source_register": {
        "path": "research/plans/F02/vad_sources.md",
        "line": 81,
        "subject": "NVIDIA MarbleNet Frame-VAD",
        "kind": "neural frame classification (CNN frame classifier)",
        "variants": ["general", "multilingual", "telephony"],
        "input": "mono 16 kHz frame predictions (source register)",
        "model_collection": (
            "NGC ``vad_marblenet``; the register reports release 1.0.0rc1 as "
            "360.59 kB; not verified here"),
        "runtime": (
            "NeMo/Torch stack named as a lead; no local install or run"),
        "license_claim": (
            "the register says NGC terms apply unless stated otherwise; no "
            "local license text, model card or weight terms are admitted"),
        "model_repositories": [
            "https://catalog.ngc.nvidia.com/orgs/nvidia/models/vad_marblenet",
            "https://catalog.ngc.nvidia.com/orgs/nvidia/nemo/models/"
            "vad_marblenet/-/collections",
        ],
        "reported_geometry": (
            "frame predictions; frame window, shift, lookahead and smoothing "
            "are not recorded"),
        "reported_metrics": (
            "no independent score is recorded in the workspace and none is "
            "reproduced here"),
        "usable_as_candidate_metric": False,
    },
    "discovery_note": {
        "path": "reports/vad-research/attempt-discovery-20261028-01/"
                "findings.md",
        "line": 13,
        "note": (
            "NeMo code lists ``vad_multilingual_marblenet`` 1.10.0 and older "
            "general/telephony checkpoints; NGC-hosted .nemo checkpoints are "
            "separate assets; no local checkpoint or NeMo/Torch runtime "
            "exists. The note labels the lead runnable only after NGC/model "
            "terms and runtime staging, and explicitly not implemented or "
            "tested. Frame window/shift, lookahead and smoothing must be "
            "preserved."),
    },
    "open_models_assessment": {
        "path": "reports/vad-research/attempt-open-models-20261028-01/"
                "assessment.md",
        "line": 26,
        "note": (
            "Records no local MarbleNet checkpoint and no NeMo/Torch stack; "
            "defers the candidate because of the larger runtime and model "
            "access burden, with frame predictions and unresolved streaming "
            "lookahead, chunking, feature context and CPU cost."),
    },
    "synthesis_v7": {
        "path": "reports/vad-research/20261028-synthesis-v7.md",
        "line": 49,
        "note": (
            "Lists NeMo MarbleNet among researched neural VAD leads and "
            "states that the source-reported values are candidate-selection "
            "leads, not local accuracy evidence."),
    },
    "segmentation_report": {
        "path": "research/voice-enhancement-20261101/agent-segmentation/"
                "REPORT.md",
        "line": 24,
        "note": (
            "Records NeMo MarbleNet as researched but not run, with no local "
            "accuracy evaluation, and warns that a different checkpoint must "
            "not be silently treated as the named architecture."),
    },
    "asr_trials_report": {
        "path": "research/voice-enhancement-20261101/agent-vad-asr-trials/"
                "REPORT.md",
        "line": 10,
        "note": (
            "States that no MarbleNet model weights, checkpoint or adapter are "
            "staged under data/models, data/checkouts, data/wheels or "
            "data/envs; no inference was run."),
    },
    "note": (
        "These values are copied from merged read-only research records. They "
        "are not reproduced, re-scored, re-pinned or promoted by this package. "
        "No revision, file name, byte count or SHA-256 is asserted as verified."),
}

UPSTREAM_RECORD: Dict[str, Any] = {
    "source_repository": "https://github.com/NVIDIA/NeMo",
    "source_revision": None,
    "source_revision_requirement": "immutable 40-hex upstream commit verified "
                                   "from a reviewable checkout",
    "source_license": None,
    "source_license_requirement": "reviewed upstream license text with exact "
                                  "SPDX identifier and license SHA-256",
    "model_repository": (
        "https://catalog.ngc.nvidia.com/orgs/nvidia/models/vad_marblenet"),
    "model_revision": None,
    "model_revision_requirement": "immutable NGC/model revision for the exact "
                                  "selected variant",
    "model_variants": ["general", "multilingual", "telephony"],
    "model_variants_requirement": (
        "caller-selected exact MarbleNet variant, recorded and never "
        "substituted for another variant"),
    "model_file_requirement": (
        "every weight, config, feature asset, model card and terms file with "
        "byte count and SHA-256"),
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "source register says mono 16 kHz frame predictions; "
                     "SDK v0 remains f32",
    "present": False,
    "executed": False,
    "digest_asserted": False,
    "framewise_and_offline_are_separate": True,
    "variant_substitution_forbidden": True,
}

PEER_EVIDENCE: Tuple[Dict[str, Any], ...] = (
    {
        "task": "SDK-CNN-BILSTM-VAD",
        "component": "cnn-bilstm-vad",
        "path": "docs/task-evidence/cnn-bilstm-vad/report.json",
        "class": "adjacent_neural_vad_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": (
            "A different neural VAD literature lead with no implementation or "
            "checkpoint; its synthetic bidirectional/framewise control is not "
            "MarbleNet."),
    },
    {
        "task": "SDK-CRNN-VAD",
        "component": "crnn-vad",
        "path": "docs/task-evidence/crnn-vad/report.json",
        "class": "architecture_class_vad_blocker",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": (
            "An architecture-class blocker, not a pinned MarbleNet model or "
            "runtime."),
    },
    {
        "task": "SDK-SILERO-VAD-6-2-3-REFERENCE",
        "component": "silero-vad-6-2-3-reference",
        "path": "docs/task-evidence/silero-vad-6-2-3-reference/report.json",
        "class": "adjacent_pinned_neural_reference",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": (
            "A different model with its own ONNX path; no timing, probability, "
            "boundary or accuracy value transfers to MarbleNet."),
    },
    {
        "task": "SDK-WEBRTC-VAD",
        "component": "webrtc-vad",
        "path": "docs/task-evidence/webrtc-vad/report.json",
        "class": "installed_dsp_control",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": (
            "An installed DSP control, not a neural frame classifier; its "
            "detections and cost are not MarbleNet evidence."),
    },
)

# ---------------------------------------------------------------------------
# Fixed synthetic analysis fixture.  Not model input and not real audio.
# ---------------------------------------------------------------------------

SURROGATE_SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "idle-a", "condition": "idle_noise", "start_frame": 0,
     "end_frame": 80, "label": False},
    {"id": "quiet-a", "condition": "quiet_speech", "start_frame": 80,
     "end_frame": 200, "label": True},
    {"id": "idle-b", "condition": "idle_noise", "start_frame": 200,
     "end_frame": 300, "label": False},
    {"id": "active-a", "condition": "active_speech", "start_frame": 300,
     "end_frame": 460, "label": True},
    {"id": "unknown-a", "condition": "unknown_region", "start_frame": 460,
     "end_frame": 520, "label": None},
    {"id": "stress-a", "condition": "stress_noisy_speech", "start_frame": 520,
     "end_frame": 640, "label": True},
    {"id": "idle-c", "condition": "idle_noise", "start_frame": 640,
     "end_frame": 720, "label": False},
    {"id": "active-b", "condition": "active_speech", "start_frame": 720,
     "end_frame": 800, "label": True},
)

# Deterministic integer evidence levels, in milli-probability units.
SEGMENT_LEVEL: Dict[str, int] = {
    "idle_noise": 80,
    "quiet_speech": 610,
    "active_speech": 930,
    "stress_noisy_speech": 640,
    "unknown_region": 450,
}
SEGMENT_JITTER: Dict[str, int] = {
    "idle_noise": 55,
    "quiet_speech": 65,
    "active_speech": 55,
    "stress_noisy_speech": 95,
    "unknown_region": 75,
}
# A deliberate short energy notch inside the first active region.  The
# framewise classifier cannot bridge it with only left context; the centred
# offline path can, at the cost of lookahead.
NOTCH_START_FRAME = 380
NOTCH_END_FRAME = 383
NOTCH_LEVEL = 240
LCG_SEED = 0x4D52424C

ADMISSION_FIELDS = (
    "channels",
    "checkpoint_id",
    "claims_qualified",
    "context_frames",
    "controls_passed",
    "corpus_record_path",
    "corpus_record_sha256",
    "event_oracle_path",
    "event_oracle_sha256",
    "execution_path",
    "frame_samples",
    "frozen_case_count",
    "lookahead_frames",
    "model_hop_samples",
    "model_variant",
    "model_window_samples",
    "nonfinite_count",
    "offline_context_frames",
    "probability_oracle_path",
    "probability_oracle_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_name",
    "runtime_path",
    "runtime_version",
    "sample_rate_hz",
    "schema_id",
    "source_license",
    "source_revision",
    "state_shape",
    "threshold_milli",
    "weights_bytes",
    "weights_format",
    "weights_path",
    "weights_sha256",
)

ADMISSION_SCHEMA: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-reference/0.1",
    "schema_id": ADMISSION_SCHEMA_ID,
    "required_fields": list(ADMISSION_FIELDS),
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "executed_in_this_package": False,
    "upstream_identity_verified": False,
    "accepted_manifest_qualifies": False,
    "synthetic_schema_control_label": "synthetic_schema_control_not_evidence",
    "rules": {
        "source_revision": "full 40 lowercase hex commit",
        "source_license": "nonempty SPDX-style identifier",
        "model_variant": ["general", "multilingual", "telephony"],
        "checkpoint_id": (
            "ASCII [a-z0-9][a-z0-9._-]{0,95}; the selected checkpoint is "
            "never substituted across variants"),
        "weights_format": ["pytorch_state_dict", "safetensors", "onnx"],
        "runtime_name": ["pytorch", "onnxruntime"],
        "runtime_version": "nonempty canonical version token",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "threshold_milli": "integer 1..999; no float threshold",
        "state_shape": "1..8 positive integer dimensions",
        "execution_path": [
            "framewise_causal",
            "framewise_lookahead",
            "offline_chunked",
        ],
        "framewise_causal": "requires zero lookahead and zero offline context",
        "framewise_lookahead": (
            "requires positive lookahead and zero offline context"),
        "offline_chunked": (
            "requires positive offline context, zero lookahead and zero "
            "left-context declaration"),
        "nonfinite_count": 0,
        "frozen_case_count": ">= 8",
        "controls_passed": True,
        "claims_qualified": (
            "must be false; a manifest cannot qualify the candidate"),
        "file_checks": (
            "absolute regular files; every declared SHA-256 must match the "
            "actual bytes; weights byte count must match"),
        "oracle_variant": (
            "probability and event oracles must declare the same "
            "model_variant as the manifest"),
    },
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source revision is a full 40-hex commit and license is recorded",
        "the selected variant and checkpoint ID are declared exactly",
        "weights, runtime lock, probability oracle, event oracle, rights and "
        "corpus records are absolute present files with matching digests",
        "weights byte count matches the declared value",
        "geometry is 16 kHz mono 160-sample SDK frames with a bounded window, "
        "hop, context and lookahead",
        "framewise, lookahead and offline declarations are mutually exclusive",
        "probability values are finite and inside [0,1]; events are ordered "
        "half-open intervals",
        "oracles from a different MarbleNet variant are rejected",
        "rights and corpus records do not claim qualification",
        "no download, copy, import, model load or execution occurs here",
        "schema acceptance never qualifies the candidate",
    ],
}

# ---------------------------------------------------------------------------
# Strict JSON and hashing helpers.
# ---------------------------------------------------------------------------


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(data: bytes) -> str:
    return sha256_bytes(data)


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


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    payload = canonical_bytes(report) + b"\n"
    return payload.decode("utf-8"), sha256_bytes(payload)


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
# Task-row identity: stable linked-row fields only; never the whole file.
# ---------------------------------------------------------------------------

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
    if stable["repository"] != "audio-sdk" or stable["mode"] != "feasibility":
        raise Reject("linked task row repository/mode mismatch")
    if stable["title"] != TITLE:
        raise Reject("linked task row title mismatch")
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
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
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
# Fixed-path artifact audit.  No network, no download, no symlink following.
# ---------------------------------------------------------------------------

AUDIT_PATHS: Tuple[Tuple[str, str], ...] = (
    ("implementation_checkout", "data/checkouts/marblenet"),
    ("weights_directory", "data/models/marblenet"),
    ("ngc_cache", "data/ngc/marblenet"),
    ("runtime_environment", "data/envs/marblenet"),
    ("wheel_cache", "data/wheels/vad-candidates/marblenet"),
    ("analysis_cohort", "data/datasets/marblenet-vad"),
    ("frozen_run", "data/runs/marblenet"),
    ("adapter", "adapters/marblenet"),
    ("rights_record", "licensing/third_party/marblenet"),
)


def _observe_path(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    observation: Dict[str, Any] = {
        "path": relative,
        "present": path.exists(),
        "kind": None,
        "entries": None,
        "bytes": None,
        "sha256": None,
    }
    if not observation["present"]:
        return observation
    if path.is_symlink():
        observation["kind"] = "symlink"
        return observation
    if path.is_dir():
        observation["kind"] = "directory"
        observation["entries"] = sum(1 for _ in path.iterdir())
        return observation
    if path.is_file():
        observation["kind"] = "file"
        data = path.read_bytes()
        observation["bytes"] = len(data)
        observation["sha256"] = sha256_bytes(data)
    return observation


def audit_assets() -> Dict[str, Any]:
    observations = [dict(_observe_path(relative), id=name)
                    for name, relative in AUDIT_PATHS]
    by_id = {item["id"]: item for item in observations}
    any_present = any(item["present"] for item in observations)
    return {
        "observations": observations,
        "any_present": any_present,
        "implementation_present": by_id["implementation_checkout"]["present"],
        "weights_present": by_id["weights_directory"]["present"],
        "ngc_present": by_id["ngc_cache"]["present"],
        "runtime_present": by_id["runtime_environment"]["present"],
        "cohort_present": by_id["analysis_cohort"]["present"],
        "frozen_run_present": by_id["frozen_run"]["present"],
        "rights_present": by_id["rights_record"]["present"],
        "audit_scope": (
            "fixed workspace paths only; no network, no download, no model "
            "load or execution"),
    }


# ---------------------------------------------------------------------------
# Synthetic analysis fixture and two-path contract control.
# ---------------------------------------------------------------------------

def _lcg(state: int) -> Tuple[int, int]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, state


def surrogate_trace() -> List[int]:
    """Return 800 deterministic milli-probability levels; never model output."""
    levels: List[int] = []
    state = LCG_SEED
    for segment in SURROGATE_SEGMENTS:
        condition = segment["condition"]
        base = SEGMENT_LEVEL[condition]
        jitter = SEGMENT_JITTER[condition]
        for _ in range(segment["start_frame"], segment["end_frame"]):
            state, raw = _lcg(state)
            offset = int((raw / 4294967296.0) * (2 * jitter + 1)) - jitter
            levels.append(max(0, min(1000, base + offset)))
    if len(levels) != SURROGATE_TOTAL_FRAMES:
        raise Reject("surrogate trace length mismatch")
    for index in range(NOTCH_START_FRAME, NOTCH_END_FRAME):
        levels[index] = NOTCH_LEVEL
    return levels


def surrogate_labels() -> Tuple[List[Optional[bool]], List[str]]:
    labels: List[Optional[bool]] = []
    conditions: List[str] = []
    for segment in SURROGATE_SEGMENTS:
        count = segment["end_frame"] - segment["start_frame"]
        if count <= 0:
            raise Reject("invalid surrogate segment")
        labels.extend([segment["label"]] * count)
        conditions.extend([segment["condition"]] * count)
    if len(labels) != SURROGATE_TOTAL_FRAMES:
        raise Reject("surrogate labels do not cover every frame")
    return labels, conditions


def _median(values: Sequence[int]) -> int:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def _validate_levels(levels: Any) -> None:
    if not isinstance(levels, (list, tuple)):
        raise Reject("levels must be a sequence")
    if len(levels) != SURROGATE_TOTAL_FRAMES:
        raise Reject("surrogate input length mismatch")
    for index, level in enumerate(levels):
        if type(level) is not int:
            raise Reject(f"level {index} is not an integer milli-probability")
        if not 0 <= level <= 1000:
            raise Reject(f"level {index} is outside [0,1000]")


def causal_decisions(levels: Sequence[int]) -> List[bool]:
    _validate_levels(levels)
    decisions: List[bool] = []
    for index in range(len(levels)):
        window = levels[
            max(0, index - CAUSAL_CONTEXT_FRAMES + 1):index + 1]
        decisions.append(_median(window) >= THRESHOLD_MILLI)
    return decisions


def offline_decisions(levels: Sequence[int]) -> List[bool]:
    _validate_levels(levels)
    decisions: List[bool] = []
    for index in range(len(levels)):
        start = max(0, index - OFFLINE_HALF_WINDOW_FRAMES)
        end = min(len(levels), index + OFFLINE_HALF_WINDOW_FRAMES + 1)
        window = levels[start:end]
        decisions.append(sum(window) >= THRESHOLD_MILLI * len(window))
    return decisions


def _runs(values: Sequence[Optional[bool]],
          positive: bool = True) -> List[Dict[str, int]]:
    runs: List[Dict[str, int]] = []
    start: Optional[int] = None
    for index, value in enumerate(values):
        inside = (value is True) if positive else (value is not True)
        if inside and start is None:
            start = index
        elif not inside and start is not None:
            runs.append({"start_frame": start, "end_frame": index})
            start = None
    if start is not None:
        runs.append({"start_frame": start, "end_frame": len(values)})
    return runs


def score_frames(decisions: Sequence[bool],
                 labels: Sequence[Optional[bool]],
                 conditions: Sequence[str],
                 hop_samples: int = SURROGATE_FRAME_SAMPLES) -> Dict[str, Any]:
    if not (len(decisions) == len(labels) == len(conditions)):
        raise Reject("decision, label and condition lengths differ")
    if type(hop_samples) is not int or hop_samples <= 0:
        raise Reject("hop_samples must be a positive integer")
    totals = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0}
    strata: Dict[str, Dict[str, int]] = {}
    for index, (decision, label, condition) in enumerate(
            zip(decisions, labels, conditions)):
        if decision is not True and decision is not False:
            raise Reject(f"decision {index} is invalid")
        if label is not None and label is not True and label is not False:
            raise Reject(f"label {index} is invalid")
        if not isinstance(condition, str) or not condition:
            raise Reject(f"condition {index} is invalid")
        bucket = strata.setdefault(
            condition, {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0})
        if label is None:
            totals["unknown"] += 1
            bucket["unknown"] += 1
            continue
        if label and decision:
            key = "tp"
        elif label and not decision:
            key = "fn"
        elif not label and decision:
            key = "fp"
        else:
            key = "tn"
        totals[key] += 1
        bucket[key] += 1
    positive = totals["tp"] + totals["fn"]
    negative = totals["fp"] + totals["tn"]
    miss = Fraction(totals["fn"], positive) if positive else Fraction(0, 1)
    false_alarm = (
        Fraction(totals["fp"], negative) if negative else Fraction(0, 1))
    return {
        "counts_frames": dict(totals),
        "counts_samples": {key: value * hop_samples
                           for key, value in totals.items()},
        "positive": positive,
        "negative": negative,
        "miss_rate_fraction": fraction_text(miss),
        "false_alarm_rate_fraction": fraction_text(false_alarm),
        "miss_rate": round(float(miss), 6),
        "false_alarm_rate": round(float(false_alarm), 6),
        "stratified": strata,
    }


def _pair_events(truth: Sequence[Dict[str, int]],
                 hypothesis: Sequence[Dict[str, int]]) -> Dict[str, Any]:
    overlap: List[Tuple[int, int, int, int, int]] = []
    for truth_index, reference in enumerate(truth):
        for hypothesis_index, candidate in enumerate(hypothesis):
            start = max(reference["start_frame"], candidate["start_frame"])
            end = min(reference["end_frame"], candidate["end_frame"])
            samples = (end - start) * SURROGATE_FRAME_SAMPLES
            if samples > 0:
                overlap.append((samples, reference["start_frame"],
                                candidate["start_frame"], truth_index,
                                hypothesis_index))
    overlap.sort(key=lambda item: (-item[0], item[1], item[2]))
    used_truth: set[int] = set()
    used_hypothesis: set[int] = set()
    matched: List[Dict[str, Any]] = []
    onset_errors: List[int] = []
    offset_errors: List[int] = []
    for samples, _, _, truth_index, hypothesis_index in overlap:
        if truth_index in used_truth or hypothesis_index in used_hypothesis:
            continue
        used_truth.add(truth_index)
        used_hypothesis.add(hypothesis_index)
        reference = truth[truth_index]
        candidate = hypothesis[hypothesis_index]
        onset = ((candidate["start_frame"] - reference["start_frame"])
                 * SURROGATE_FRAME_SAMPLES)
        offset = ((candidate["end_frame"] - reference["end_frame"])
                  * SURROGATE_FRAME_SAMPLES)
        onset_errors.append(onset)
        offset_errors.append(offset)
        matched.append({
            "reference_start": reference["start_frame"] * SURROGATE_FRAME_SAMPLES,
            "reference_end": reference["end_frame"] * SURROGATE_FRAME_SAMPLES,
            "hypothesis_start": candidate["start_frame"] * SURROGATE_FRAME_SAMPLES,
            "hypothesis_end": candidate["end_frame"] * SURROGATE_FRAME_SAMPLES,
            "overlap_samples": samples,
            "onset_error_samples": onset,
            "offset_error_samples": offset,
            "onset_error_ms": (onset * 1000) // SAMPLE_RATE_HZ,
            "offset_error_ms": (offset * 1000) // SAMPLE_RATE_HZ,
        })
    unmatched_truth = [index for index in range(len(truth))
                       if index not in used_truth]
    unmatched_hypothesis = [index for index in range(len(hypothesis))
                            if index not in used_hypothesis]
    return {
        "truth_runs": [
            {"start_sample": item["start_frame"] * SURROGATE_FRAME_SAMPLES,
             "end_sample": item["end_frame"] * SURROGATE_FRAME_SAMPLES}
            for item in truth],
        "hypothesis_runs": [
            {"start_sample": item["start_frame"] * SURROGATE_FRAME_SAMPLES,
             "end_sample": item["end_frame"] * SURROGATE_FRAME_SAMPLES}
            for item in hypothesis],
        "matched": matched,
        "unmatched_truth_runs": len(unmatched_truth),
        "unmatched_hypothesis_runs": len(unmatched_hypothesis),
        "onset_errors_samples": onset_errors,
        "offset_errors_samples": offset_errors,
        "onset_median_samples": (_median(onset_errors) if onset_errors else None),
        "offset_median_samples": (_median(offset_errors) if offset_errors else None),
        "onset_p90_abs_samples": _p90_abs(onset_errors),
        "offset_p90_abs_samples": _p90_abs(offset_errors),
        "matching": (
            "one-to-one maximum-overlap pairing; ties by earliest reference "
            "then earliest hypothesis start"),
    }


def _p90_abs(values: Sequence[int]) -> Optional[int]:
    if not values:
        return None
    ordered = sorted(abs(value) for value in values)
    rank = max(0, math.ceil(0.9 * len(ordered)) - 1)
    return ordered[rank]


def _path_control(decisions: Sequence[bool],
                  labels: Sequence[Optional[bool]],
                  conditions: Sequence[str],
                  lookahead_frames: int) -> Dict[str, Any]:
    metrics = score_frames(decisions, labels, conditions)
    truth = _runs(labels, positive=True)
    # Boundary diagnostics are computed only on scored regions: a hypothesis
    # event inside an unknown span is not evidence of a false alarm.
    scored_decisions = [
        decision if label is not None else False
        for decision, label in zip(decisions, labels)]
    hypothesis = _runs(scored_decisions, positive=True)
    boundary = _pair_events(truth, hypothesis)
    return {
        "decisions_sha256": sha256_bytes(canonical_bytes(list(decisions))),
        "decision_count": len(decisions),
        "positive_frames": sum(1 for item in decisions if item),
        "lookahead_frames": lookahead_frames,
        "lookahead_samples": lookahead_frames * SURROGATE_FRAME_SAMPLES,
        "decision_available_at": (
            "end of frame k" if lookahead_frames == 0
            else f"end of frame k+{lookahead_frames}"),
        "metrics": metrics,
        "boundary": boundary,
        "qualification_effect": "none",
    }


def build_surrogate_control() -> Dict[str, Any]:
    levels = surrogate_trace()
    labels, conditions = surrogate_labels()
    causal = causal_decisions(levels)
    offline = offline_decisions(levels)
    causal_control = _path_control(causal, labels, conditions, 0)
    offline_control = _path_control(
        offline, labels, conditions, OFFLINE_HALF_WINDOW_FRAMES)
    active = [decision for decision, label in zip(causal, labels)
              if label is not None]
    all_speech = score_frames(
        [True] * SURROGATE_TOTAL_FRAMES, labels, conditions)
    all_nonspeech = score_frames(
        [False] * SURROGATE_TOTAL_FRAMES, labels, conditions)
    return {
        "model_executed": False,
        "executor": "absent",
        "surrogate": True,
        "label": "synthetic_frame_classifier_control_not_marblenet",
        "fixture": {
            "name": "synthetic-analysis-control",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "hop_samples": SURROGATE_FRAME_SAMPLES,
            "total_frames": SURROGATE_TOTAL_FRAMES,
            "total_samples": SURROGATE_TOTAL_SAMPLES,
            "scored_frames": sum(1 for label in labels if label is not None),
            "unknown_frames": sum(1 for label in labels if label is None),
            "notch_frames": [NOTCH_START_FRAME, NOTCH_END_FRAME],
            "segments": [dict(segment) for segment in SURROGATE_SEGMENTS],
            "trace_sha256": sha256_bytes(canonical_bytes(levels)),
            "truth_sha256": sha256_bytes(canonical_bytes(labels)),
            "condition_sha256": sha256_bytes(canonical_bytes(conditions)),
        },
        "threshold_milli": THRESHOLD_MILLI,
        "paths": {
            "framewise_causal": {
                **causal_control,
                "window": (
                    f"{CAUSAL_CONTEXT_FRAMES}-frame left-context median"),
                "bidirectional": False,
            },
            "bidirectional_offline": {
                **offline_control,
                "window": (
                    f"{OFFLINE_WINDOW_FRAMES}-frame centred mean with "
                    f"{OFFLINE_HALF_WINDOW_FRAMES}-frame lookahead"),
                "bidirectional": True,
            },
        },
        "availability": {
            "separation_declared": True,
            "framewise_available": True,
            "offline_available": False,
            "offline_framewise_claim": False,
            "causal_decision_available_at": "end of frame k",
            "offline_decision_available_at": (
                f"end of frame k+{OFFLINE_HALF_WINDOW_FRAMES}"),
            "causal_lookahead_samples": 0,
            "offline_lookahead_samples": (
                OFFLINE_HALF_WINDOW_FRAMES * SURROGATE_FRAME_SAMPLES),
            "offline_lookahead_ns": (
                OFFLINE_HALF_WINDOW_FRAMES * SURROGATE_FRAME_SAMPLES
                * NS_PER_SAMPLE),
            "note": (
                "The centred path is an offline structural control. Its "
                "boundary values are not operational latency and it is not a "
                "framewise-available candidate."),
        },
        "controls": {
            "always_speech": all_speech,
            "always_nonspeech": all_nonspeech,
            "all_decisions_active_positive_count": sum(active),
        },
        "qualification_effect": "none",
        "note": (
            "Synthetic contract control only. It is not MarbleNet output, not "
            "a real cohort result and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Variant-substitution control.  Distinct identities; never interchangeable.
# ---------------------------------------------------------------------------

def variant_identities() -> List[Dict[str, Any]]:
    identities: List[Dict[str, Any]] = []
    for item in VARIANTS:
        identity = {
            "model_variant": item["variant"],
            "checkpoint_id": item["checkpoint_id"],
            "source_reported_version": item["source_reported_version"],
            "state": "absent",
            "verified": False,
        }
        identities.append({
            **identity,
            "identity_sha256": sha256_bytes(canonical_bytes(identity)),
        })
    return identities


def build_variant_separation_control() -> Dict[str, Any]:
    identities = variant_identities()
    digests = [item["identity_sha256"] for item in identities]
    if len(set(digests)) != len(digests):
        raise Reject("MarbleNet variant identities are not distinct")
    substitution_rejected = False
    try:
        _validate_variant_token(
            {"model_variant": "multilingual",
             "checkpoint_id": "vad_multilingual_marblenet"},
            expected_variant="telephony")
    except Reject:
        substitution_rejected = True
    return {
        "variants": identities,
        "declared_variant_count": len(identities),
        "identity_digests_distinct": True,
        "interchangeable": False,
        "substitution_rejected": substitution_rejected,
        "synthetic_control": True,
        "qualification_effect": "none",
        "note": (
            "The general, multilingual and telephony leads are distinct "
            "unresolved identities. No checkpoint, revision or digest is "
            "asserted; a cross-variant oracle or file is rejected."),
    }


# ---------------------------------------------------------------------------
# Caller-supplied-reference admission.  Validation only; never execution.
# ---------------------------------------------------------------------------

PROBABILITY_ORACLE_SCHEMA = f"audio-sdk/{SLUG}/probability-oracle/0.1"
EVENT_ORACLE_SCHEMA = f"audio-sdk/{SLUG}/event-oracle/0.1"
WEIGHTS_FORMATS = ("pytorch_state_dict", "safetensors", "onnx")
RUNTIME_NAMES = ("pytorch", "onnxruntime")
VARIANT_NAMES = tuple(item["variant"] for item in VARIANTS)
EXECUTION_PATHS = ("framewise_causal", "framewise_lookahead",
                   "offline_chunked")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")
LICENSE_PATTERN = re.compile(r"[A-Za-z0-9.+-]{1,64}")
VERSION_PATTERN = re.compile(r"[A-Za-z0-9.+_-]{1,64}")
CHECKPOINT_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}")


def _absolute_file(manifest: Dict[str, Any], field: str) -> Path:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not raw:
        raise Reject(f"{field} must be a nonempty string")
    path = Path(raw)
    if not path.is_absolute():
        raise Reject(f"{field} must be an absolute path")
    if not path.is_file():
        raise Reject(f"{field} does not exist")
    return path


def _sha_field(manifest: Dict[str, Any], field: str) -> str:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not SHA256_PATTERN.fullmatch(raw):
        raise Reject(f"{field} must be 64 lowercase hex characters")
    return raw


def _int_field(manifest: Dict[str, Any], field: str, low: int,
               high: int) -> int:
    raw = manifest.get(field)
    if type(raw) is not int:
        raise Reject(f"{field} must be an integer")
    if not low <= raw <= high:
        raise Reject(f"{field} is outside [{low},{high}]")
    return raw


def _strict_object_file(path: Path, label: str) -> Dict[str, Any]:
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject(f"{label} is unreadable") from error
    return document


def _variant_name(manifest: Dict[str, Any],
                  expected_variant: Optional[str] = None) -> str:
    variant = manifest.get("model_variant")
    if variant not in VARIANT_NAMES:
        raise Reject("model_variant is unsupported")
    if expected_variant is not None and variant != expected_variant:
        raise Reject("oracle model_variant differs from the manifest")
    return variant


def _validate_variant_token(manifest: Dict[str, Any],
                            expected_variant: Optional[str] = None) -> str:
    variant = _variant_name(manifest, expected_variant)
    checkpoint = manifest.get("checkpoint_id")
    if (not isinstance(checkpoint, str)
            or not CHECKPOINT_PATTERN.fullmatch(checkpoint)):
        raise Reject("checkpoint_id is not a canonical identifier")
    return variant


def _validate_probability_oracle(path: Path,
                                 expected_variant: Optional[str] = None) -> None:
    document = _strict_object_file(path, "probability oracle")
    if set(document) != {"schema_id", "model_variant", "frames",
                         "nonfinite_count"}:
        raise Reject("probability oracle fields differ")
    if document.get("schema_id") != PROBABILITY_ORACLE_SCHEMA:
        raise Reject("probability oracle schema mismatch")
    _variant_name(document, expected_variant)
    frames = document.get("frames")
    if not isinstance(frames, list) or not frames:
        raise Reject("probability oracle frames must be a nonempty list")
    if type(document.get("nonfinite_count")) is not int:
        raise Reject("probability oracle nonfinite_count must be an integer")
    if document["nonfinite_count"] != 0:
        raise Reject("probability oracle reports nonfinite values")
    for index, value in enumerate(frames):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Reject(f"probability oracle frame {index} is not a number")
        number = float(value)
        if not math.isfinite(number) or not 0.0 <= number <= 1.0:
            raise Reject(f"probability oracle frame {index} is invalid")


def _validate_event_oracle(path: Path,
                           expected_variant: Optional[str] = None) -> None:
    document = _strict_object_file(path, "event oracle")
    if set(document) != {"schema_id", "model_variant", "events"}:
        raise Reject("event oracle fields differ")
    if document.get("schema_id") != EVENT_ORACLE_SCHEMA:
        raise Reject("event oracle schema mismatch")
    _variant_name(document, expected_variant)
    events = document.get("events")
    if not isinstance(events, list):
        raise Reject("event oracle events must be a list")
    previous_end = -1
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != {
                "start_sample", "end_sample"}:
            raise Reject(f"event oracle event {index} fields differ")
        start = event["start_sample"]
        end = event["end_sample"]
        if type(start) is not int or type(end) is not int:
            raise Reject(f"event oracle event {index} is not integer")
        if start < 0 or end <= start:
            raise Reject(f"event oracle event {index} interval is invalid")
        if start < previous_end:
            raise Reject(f"event oracle event {index} overlaps or is unordered")
        previous_end = end


def _validate_rights_record(path: Path, label: str) -> None:
    document = _strict_object_file(path, label)
    if not isinstance(document.get("license"), str) or not document["license"]:
        raise Reject(label + " license is missing")
    if document.get("claims_qualified") is not False:
        raise Reject(label + " must not claim qualification")


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("caller manifest must be a JSON object")
    if set(manifest) != set(ADMISSION_FIELDS):
        missing = sorted(set(ADMISSION_FIELDS) - set(manifest))
        extra = sorted(set(manifest) - set(ADMISSION_FIELDS))
        raise Reject(f"caller manifest fields differ missing={missing} extra={extra}")
    if manifest.get("schema_id") != ADMISSION_SCHEMA_ID:
        raise Reject("schema_id mismatch")
    revision = manifest.get("source_revision")
    if not isinstance(revision, str) or not REVISION_PATTERN.fullmatch(revision):
        raise Reject("source_revision must be a full 40-hex commit")
    license_value = manifest.get("source_license")
    if (not isinstance(license_value, str)
            or not LICENSE_PATTERN.fullmatch(license_value)):
        raise Reject("source_license is not a canonical SPDX-style token")
    variant = _validate_variant_token(manifest)
    if manifest.get("weights_format") not in WEIGHTS_FORMATS:
        raise Reject("weights_format is unsupported")
    if manifest.get("runtime_name") not in RUNTIME_NAMES:
        raise Reject("runtime_name is unsupported")
    version = manifest.get("runtime_version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise Reject("runtime_version is not a canonical version token")
    if manifest.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise Reject("sample_rate_hz must be 16000")
    if manifest.get("channels") != CHANNELS:
        raise Reject("channels must be 1")
    if manifest.get("frame_samples") != SDK_FRAME_SAMPLES:
        raise Reject("frame_samples must be 160")
    _int_field(manifest, "model_hop_samples", 1, SAMPLE_RATE_HZ)
    _int_field(manifest, "model_window_samples", 1, SAMPLE_RATE_HZ * 60)
    context = _int_field(manifest, "context_frames", 0, 1024)
    offline_context = _int_field(manifest, "offline_context_frames", 0, 1024)
    lookahead = _int_field(manifest, "lookahead_frames", 0, 1024)
    execution_path = manifest.get("execution_path")
    if not isinstance(execution_path, str):
        raise Reject("execution_path must be a string")
    if execution_path not in EXECUTION_PATHS:
        raise Reject("execution_path is unsupported")
    if execution_path == "framewise_causal":
        if lookahead != 0 or offline_context != 0:
            raise Reject(
                "framewise_causal requires zero lookahead and zero offline "
                "context")
        framewise_available = True
    elif execution_path == "framewise_lookahead":
        if lookahead < 1 or offline_context != 0:
            raise Reject(
                "framewise_lookahead requires positive lookahead and zero "
                "offline context")
        framewise_available = True
    else:
        if offline_context < 1 or lookahead != 0 or context != 0:
            raise Reject(
                "offline_chunked requires positive offline context, zero "
                "lookahead and zero left context")
        framewise_available = False
    shape = manifest.get("state_shape")
    if not isinstance(shape, list) or not 1 <= len(shape) <= 8:
        raise Reject("state_shape must be a list of 1..8 dimensions")
    for index, dimension in enumerate(shape):
        if type(dimension) is not int or not 1 <= dimension <= 65536:
            raise Reject(f"state_shape dimension {index} is invalid")
    _int_field(manifest, "threshold_milli", 1, 999)
    if _int_field(manifest, "nonfinite_count", 0, 0) != 0:
        raise Reject("nonfinite_count must be zero")
    if _int_field(manifest, "frozen_case_count", 8, 100000) < 8:
        raise Reject("frozen_case_count must be at least 8")
    if manifest.get("controls_passed") is not True:
        raise Reject("controls_passed must be true")
    if manifest.get("claims_qualified") is not False:
        raise Reject("a caller manifest must not claim qualification")
    weights_path = _absolute_file(manifest, "weights_path")
    lock_path = _absolute_file(manifest, "runtime_lock_path")
    probability_path = _absolute_file(manifest, "probability_oracle_path")
    event_path = _absolute_file(manifest, "event_oracle_path")
    rights_path = _absolute_file(manifest, "rights_record_path")
    corpus_path = _absolute_file(manifest, "corpus_record_path")
    runtime_path = manifest.get("runtime_path")
    if not isinstance(runtime_path, str) or not Path(runtime_path).is_absolute():
        raise Reject("runtime_path must be an absolute path")
    if not Path(runtime_path).is_dir():
        raise Reject("runtime_path does not exist")
    weights_sha = _sha_field(manifest, "weights_sha256")
    lock_sha = _sha_field(manifest, "runtime_lock_sha256")
    probability_sha = _sha_field(manifest, "probability_oracle_sha256")
    event_sha = _sha_field(manifest, "event_oracle_sha256")
    rights_sha = _sha_field(manifest, "rights_record_sha256")
    corpus_sha = _sha_field(manifest, "corpus_record_sha256")
    weights_bytes = _int_field(manifest, "weights_bytes", 1, 2 ** 40)
    checks = (
        (weights_path, weights_sha, "weights file"),
        (lock_path, lock_sha, "runtime lock"),
        (probability_path, probability_sha, "probability oracle"),
        (event_path, event_sha, "event oracle"),
        (rights_path, rights_sha, "rights record"),
        (corpus_path, corpus_sha, "corpus record"),
    )
    for path, digest, label in checks:
        if sha256_bytes(path.read_bytes()) != digest:
            raise Reject(label + " SHA-256 mismatch")
    if len(weights_path.read_bytes()) != weights_bytes:
        raise Reject("weights_bytes does not match the file")
    _validate_probability_oracle(probability_path, expected_variant=variant)
    _validate_event_oracle(event_path, expected_variant=variant)
    _validate_rights_record(rights_path, "rights record")
    _validate_rights_record(corpus_path, "corpus record")
    return {
        "accepted": True,
        "executed": False,
        "loaded": False,
        "imported": False,
        "upstream_identity_verified": False,
        "qualifies": False,
        "separation": {
            "execution_path": execution_path,
            "model_variant": variant,
            "context_frames": context,
            "lookahead_frames": lookahead,
            "offline_context_frames": offline_context,
            "framewise_available": framewise_available,
            "framewise_claim_allowed": framewise_available,
            "variant_substitution_allowed": False,
        },
        "weights_sha256": weights_sha,
        "weights_bytes": weights_bytes,
        "runtime_name": manifest["runtime_name"],
        "runtime_version": version,
        "source_revision": revision,
        "source_license": license_value,
        "note": (
            "Schema, geometry and local file hashes only. This cannot certify "
            "upstream identity, rights, parity or accuracy, and acceptance "
            "never qualifies the candidate."),
    }


# ---------------------------------------------------------------------------
# Adverse controls.  Each case is actually invoked and must fail closed.
# ---------------------------------------------------------------------------

def _synthetic_admission_tree(root: Path) -> Dict[str, Any]:
    runtime = root / "runtime"
    runtime.mkdir()
    weights = root / "weights.bin"
    weights.write_bytes(b"MARBLENET-SYNTHETIC-PLACEHOLDER-NOT-A-CHECKPOINT\n")
    lock = root / "requirements.lock"
    lock.write_bytes(b"synthetic-runtime==0.0.0\n")
    probability = root / "probability.json"
    probability.write_text(canonical_text({
        "schema_id": PROBABILITY_ORACLE_SCHEMA,
        "model_variant": "multilingual",
        "frames": [0.0, 0.25, 0.5, 0.75, 1.0],
        "nonfinite_count": 0,
    }), encoding="utf-8")
    event = root / "events.json"
    event.write_text(canonical_text({
        "schema_id": EVENT_ORACLE_SCHEMA,
        "model_variant": "multilingual",
        "events": [{"start_sample": 0, "end_sample": 800},
                   {"start_sample": 1600, "end_sample": 2400}],
    }), encoding="utf-8")
    rights = root / "rights.json"
    rights.write_text(canonical_text({
        "license": "Apache-2.0", "claims_qualified": False,
    }), encoding="utf-8")
    corpus = root / "corpus.json"
    corpus.write_text(canonical_text({
        "license": "CC-BY-4.0", "claims_qualified": False,
    }), encoding="utf-8")
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "source_revision": "0" * 40,
        "source_license": "Apache-2.0",
        "model_variant": "multilingual",
        "checkpoint_id": "vad_multilingual_marblenet",
        "weights_path": str(weights),
        "weights_sha256": sha256_bytes(weights.read_bytes()),
        "weights_bytes": len(weights.read_bytes()),
        "weights_format": "pytorch_state_dict",
        "runtime_path": str(runtime),
        "runtime_name": "pytorch",
        "runtime_version": "2.7.0",
        "runtime_lock_path": str(lock),
        "runtime_lock_sha256": sha256_bytes(lock.read_bytes()),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "model_hop_samples": 160,
        "model_window_samples": 400,
        "context_frames": 4,
        "offline_context_frames": 0,
        "lookahead_frames": 2,
        "execution_path": "framewise_lookahead",
        "state_shape": [256, 2],
        "threshold_milli": THRESHOLD_MILLI,
        "probability_oracle_path": str(probability),
        "probability_oracle_sha256": sha256_bytes(probability.read_bytes()),
        "event_oracle_path": str(event),
        "event_oracle_sha256": sha256_bytes(event.read_bytes()),
        "nonfinite_count": 0,
        "rights_record_path": str(rights),
        "rights_record_sha256": sha256_bytes(rights.read_bytes()),
        "corpus_record_path": str(corpus),
        "corpus_record_sha256": sha256_bytes(corpus.read_bytes()),
        "frozen_case_count": 8,
        "controls_passed": True,
        "claims_qualified": False,
    }


def run_admission_controls() -> Dict[str, Any]:
    cases: List[Tuple[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="marblenet-admission-") as raw:
        root = Path(raw)
        base = _synthetic_admission_tree(root)

        def mutated(**changes: Any) -> Dict[str, Any]:
            item = copy.deepcopy(base)
            item.update(changes)
            return item

        def mismatched_oracle(name: str, field: str, variant: str) -> Any:
            schema = (PROBABILITY_ORACLE_SCHEMA if field ==
                      "probability" else EVENT_ORACLE_SCHEMA)
            payload: Dict[str, Any] = {
                "schema_id": schema, "model_variant": variant}
            if field == "probability":
                payload.update({"frames": [0.0, 0.5, 1.0],
                                "nonfinite_count": 0})
            else:
                payload.update({"events": [{"start_sample": 0,
                                           "end_sample": 160}]})
            path = _write_temp_json(root, name, payload)
            if field == "probability":
                return mutated(probability_oracle_path=str(path),
                               probability_oracle_sha256=sha256(
                                   path.read_bytes()))
            return mutated(event_oracle_path=str(path),
                           event_oracle_sha256=sha256(path.read_bytes()))

        cases.extend([
            ("strict_json_duplicate_key",
             lambda: strict_loads('{"a":1,"a":2}')),
            ("strict_json_nonfinite",
             lambda: strict_loads('{"a":NaN}')),
            ("strict_json_not_object",
             lambda: strict_loads("[1,2]")),
            ("surrogate_bad_length",
             lambda: causal_decisions([0, 1, 2])),
            ("surrogate_nonfinite_level",
             lambda: offline_decisions([0] * 799 + [math.nan])),
            ("surrogate_boolean_level",
             lambda: causal_decisions([False] * 799 + [True])),
            ("surrogate_out_of_range_level",
             lambda: offline_decisions([0] * 799 + [1001])),
            ("score_decision_not_boolean",
             lambda: score_frames([1] * 4, [True] * 4, ["x"] * 4)),
            ("score_label_invalid",
             lambda: score_frames([True] * 4, ["speech"] * 4, ["x"] * 4)),
            ("score_condition_empty",
             lambda: score_frames([True] * 4, [True] * 4, [""] * 4)),
            ("score_length_mismatch",
             lambda: score_frames([True], [True, False], ["x", "y"])),
            ("score_zero_hop",
             lambda: score_frames([True] * 4, [True] * 4, ["x"] * 4, 0)),
            ("manifest_not_object", lambda: validate_caller_manifest([])),
            ("manifest_missing_field",
             lambda: validate_caller_manifest({"schema_id": ADMISSION_SCHEMA_ID})),
            ("manifest_extra_field",
             lambda: validate_caller_manifest(mutated(unknown_field=1))),
            ("manifest_bad_schema",
             lambda: validate_caller_manifest(mutated(schema_id="wrong"))),
            ("manifest_short_revision",
             lambda: validate_caller_manifest(mutated(source_revision="0" * 39))),
            ("manifest_uppercase_revision",
             lambda: validate_caller_manifest(
                 mutated(source_revision="A" * 40))),
            ("manifest_empty_license",
             lambda: validate_caller_manifest(mutated(source_license=""))),
            ("manifest_bad_weights_format",
             lambda: validate_caller_manifest(mutated(weights_format="pickle"))),
            ("manifest_bad_runtime_name",
             lambda: validate_caller_manifest(mutated(runtime_name="vendor"))),
            ("manifest_bad_runtime_version",
             lambda: validate_caller_manifest(mutated(runtime_version="2 7"))),
            ("manifest_bad_variant",
             lambda: validate_caller_manifest(mutated(model_variant="large"))),
            ("manifest_uppercase_checkpoint_id",
             lambda: validate_caller_manifest(
                 mutated(checkpoint_id="MarbleNet"))),
            ("manifest_empty_checkpoint_id",
             lambda: validate_caller_manifest(mutated(checkpoint_id=""))),
            ("manifest_checkpoint_id_too_long",
             lambda: validate_caller_manifest(
                 mutated(checkpoint_id="m" * 97))),
            ("manifest_bad_execution_path",
             lambda: validate_caller_manifest(
                 mutated(execution_path="batch"))),
            ("manifest_nonstring_execution_path",
             lambda: validate_caller_manifest(mutated(execution_path=1))),
            ("manifest_causal_with_lookahead",
             lambda: validate_caller_manifest(
                 mutated(execution_path="framewise_causal"))),
            ("manifest_lookahead_without_lookahead",
             lambda: validate_caller_manifest(
                 mutated(lookahead_frames=0))),
            ("manifest_offline_without_context",
             lambda: validate_caller_manifest(
                 mutated(execution_path="offline_chunked"))),
            ("manifest_offline_with_lookahead",
             lambda: validate_caller_manifest(
                 mutated(execution_path="offline_chunked",
                         offline_context_frames=6))),
            ("manifest_offline_with_left_context",
             lambda: validate_caller_manifest(
                 mutated(execution_path="offline_chunked",
                         offline_context_frames=6, lookahead_frames=0))),
            ("manifest_causal_with_offline_context",
             lambda: validate_caller_manifest(
                 mutated(execution_path="framewise_causal",
                         lookahead_frames=0, offline_context_frames=2))),
            ("manifest_negative_context",
             lambda: validate_caller_manifest(mutated(context_frames=-1))),
            ("manifest_offline_context_too_large",
             lambda: validate_caller_manifest(
                 mutated(offline_context_frames=1025))),
            ("manifest_lookahead_too_large",
             lambda: validate_caller_manifest(
                 mutated(lookahead_frames=1025))),
            ("manifest_zero_hop",
             lambda: validate_caller_manifest(mutated(model_hop_samples=0))),
            ("manifest_hop_too_large",
             lambda: validate_caller_manifest(
                 mutated(model_hop_samples=SAMPLE_RATE_HZ + 1))),
            ("manifest_zero_window",
             lambda: validate_caller_manifest(
                 mutated(model_window_samples=0))),
            ("manifest_window_too_large",
             lambda: validate_caller_manifest(
                 mutated(model_window_samples=SAMPLE_RATE_HZ * 60 + 1))),
            ("manifest_wrong_rate",
             lambda: validate_caller_manifest(mutated(sample_rate_hz=8000))),
            ("manifest_stereo",
             lambda: validate_caller_manifest(mutated(channels=2))),
            ("manifest_wrong_frame",
             lambda: validate_caller_manifest(mutated(frame_samples=256))),
            ("manifest_empty_state_shape",
             lambda: validate_caller_manifest(mutated(state_shape=[]))),
            ("manifest_zero_state_dimension",
             lambda: validate_caller_manifest(mutated(state_shape=[0]))),
            ("manifest_boolean_state_dimension",
             lambda: validate_caller_manifest(mutated(state_shape=[True]))),
            ("manifest_threshold_bool",
             lambda: validate_caller_manifest(mutated(threshold_milli=True))),
            ("manifest_threshold_zero",
             lambda: validate_caller_manifest(mutated(threshold_milli=0))),
            ("manifest_threshold_float",
             lambda: validate_caller_manifest(mutated(threshold_milli=0.5))),
            ("manifest_nonfinite_count",
             lambda: validate_caller_manifest(mutated(nonfinite_count=1))),
            ("manifest_too_few_cases",
             lambda: validate_caller_manifest(mutated(frozen_case_count=7))),
            ("manifest_controls_failed",
             lambda: validate_caller_manifest(mutated(controls_passed=False))),
            ("manifest_claims_qualified",
             lambda: validate_caller_manifest(mutated(claims_qualified=True))),
            ("manifest_relative_weights_path",
             lambda: validate_caller_manifest(
                 mutated(weights_path="relative/weights.bin"))),
            ("manifest_missing_weights_path",
             lambda: validate_caller_manifest(
                 mutated(weights_path=str(root / "absent.bin")))),
            ("manifest_relative_runtime_path",
             lambda: validate_caller_manifest(
                 mutated(runtime_path="relative/runtime"))),
            ("manifest_missing_runtime_path",
             lambda: validate_caller_manifest(
                 mutated(runtime_path=str(root / "absent-runtime")))),
            ("manifest_wrong_weights_hash",
             lambda: validate_caller_manifest(
                 mutated(weights_sha256="0" * 64))),
            ("manifest_wrong_weights_bytes",
             lambda: validate_caller_manifest(mutated(weights_bytes=1))),
            ("manifest_wrong_lock_hash",
             lambda: validate_caller_manifest(
                 mutated(runtime_lock_sha256="0" * 64))),
            ("manifest_wrong_rights_hash",
             lambda: validate_caller_manifest(
                 mutated(rights_record_sha256="0" * 64))),
            ("manifest_wrong_probability_hash",
             lambda: validate_caller_manifest(
                 mutated(probability_oracle_sha256="0" * 64))),
            ("manifest_wrong_event_hash",
             lambda: validate_caller_manifest(
                 mutated(event_oracle_sha256="0" * 64))),
            ("manifest_nonfinite_probability",
             lambda: _validate_probability_oracle(
                 _write_temp_json(root, "bad-prob.json", {
                     "schema_id": PROBABILITY_ORACLE_SCHEMA,
                     "model_variant": "multilingual",
                     "frames": [math.nan],
                     "nonfinite_count": 0}))),
            ("manifest_probability_out_of_range",
             lambda: _validate_probability_oracle(
                 _write_temp_json(root, "range-prob.json", {
                     "schema_id": PROBABILITY_ORACLE_SCHEMA,
                     "model_variant": "multilingual",
                     "frames": [1.5],
                     "nonfinite_count": 0}))),
            ("manifest_probability_variant_mismatch",
             lambda: validate_caller_manifest(
                 mismatched_oracle("telephony-prob.json", "probability",
                                   "telephony"))),
            ("manifest_event_overlap",
             lambda: _validate_event_oracle(
                 _write_temp_json(root, "overlap-event.json", {
                     "schema_id": EVENT_ORACLE_SCHEMA,
                     "model_variant": "multilingual",
                     "events": [{"start_sample": 0, "end_sample": 10},
                                {"start_sample": 5, "end_sample": 20}]}))),
            ("manifest_event_inverted",
             lambda: _validate_event_oracle(
                 _write_temp_json(root, "inverted-event.json", {
                     "schema_id": EVENT_ORACLE_SCHEMA,
                     "model_variant": "multilingual",
                     "events": [{"start_sample": 10, "end_sample": 5}]}))),
            ("manifest_event_variant_mismatch",
             lambda: validate_caller_manifest(
                 mismatched_oracle("telephony-event.json", "event",
                                   "telephony"))),
            ("manifest_rights_claims_qualified",
             lambda: _validate_rights_record(
                 _write_temp_json(root, "bad-rights.json", {
                     "license": "Apache-2.0", "claims_qualified": True}),
                 "rights record")),
            ("manifest_corpus_claims_qualified",
             lambda: _validate_rights_record(
                 _write_temp_json(root, "bad-corpus.json", {
                     "license": "CC-BY-4.0", "claims_qualified": True}),
                 "corpus record")),
        ])
        results: List[Dict[str, str]] = []
        for name, function in cases:
            try:
                function()
            except (Reject, OSError, ValueError):
                results.append({"case": name, "result": "rejected"})
            else:
                results.append({"case": name, "result": "accepted"})
        positive = validate_caller_manifest(base)
    return {
        "positive_control": {
            "label": "synthetic_schema_control_not_evidence",
            "accepted": positive["accepted"],
            "qualifies": positive["qualifies"],
            "executed": positive["executed"],
            "upstream_identity_verified": positive["upstream_identity_verified"],
            "execution_path": positive["separation"]["execution_path"],
            "model_variant": positive["separation"]["model_variant"],
            "lookahead_frames": positive["separation"]["lookahead_frames"],
            "framewise_available": positive["separation"]["framewise_available"],
        },
        "adverse": results,
        "adverse_count": len(results),
        "adverse_all_rejected": all(
            item["result"] == "rejected" for item in results),
    }


def _write_temp_json(root: Path, name: str, value: Any) -> Path:
    path = root / name
    path.write_text(canonical_text(value), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Report and contract models.
# ---------------------------------------------------------------------------

def _audit_summary() -> Dict[str, Any]:
    live = audit_assets()
    return {
        "qualified": False,
        "audit_result": "absent" if not live["any_present"] else "partial_unqualified",
        "any_present": live["any_present"],
        "implementation_present": live["implementation_present"],
        "weights_present": live["weights_present"],
        "ngc_present": live["ngc_present"],
        "runtime_present": live["runtime_present"],
        "cohort_present": live["cohort_present"],
        "frozen_run_present": live["frozen_run_present"],
        "rights_present": live["rights_present"],
        "observed": live,
        "note": (
            "Presence is not qualification. A file, weight or runtime appearing "
            "at a fixed path does not establish upstream identity, rights, "
            "parity or accuracy."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _audit_summary()
    surrogate = build_surrogate_control()
    variants = build_variant_separation_control()
    admission = run_admission_controls()
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
        for item, requirement, status in ANALYSIS_REQUIREMENTS
    ]
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
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
                "The exact MarbleNet variant implementation, checkpoint, "
                "rights record, inference geometry, pinned runtime, frozen "
                "oracle, rights-cleared analysis cohort and target timing are "
                "absent."),
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
        "candidate_requirements": [dict(item) for item in CANDIDATE_REQUIREMENTS],
        "asset_audit": audit,
        "admission_schema": ADMISSION_SCHEMA,
        "admission_controls": admission,
        "variant_separation": variants,
        "analysis_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "plan_note": (
                "Keep framewise and offline-chunked paths separate; exact "
                "variant weight, revision, runtime and geometry pins are "
                "absent."),
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural controls pass, but no real model, rights-cleared "
                "cohort, target runtime or approved parity exists, so the "
                "analysis profile is not satisfied for qualification."),
        },
        "reference_protocol": surrogate,
        "controls": {
            "unknown_never_counted_as_nonspeech": True,
            "invalid_values_rejected": True,
            "known_zero_counted_as_nonspeech": True,
            "missing_result_never_qualifies": True,
            "offline_never_presented_as_framewise": True,
            "variant_substitution_rejected": (
                variants["substitution_rejected"]),
            "adverse_all_rejected": admission["adverse_all_rejected"],
            "adverse_count": admission["adverse_count"],
            "admission_positive_control_qualifies": False,
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "upstream_record": UPSTREAM_RECORD,
        "peer_evidence": [dict(item) for item in PEER_EVIDENCE],
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            "data/checkouts/marblenet",
            "data/models/marblenet",
            "data/ngc/marblenet",
            "data/envs/marblenet",
            "data/datasets/marblenet-vad",
            "data/runs/marblenet",
            "licensing/third_party/marblenet",
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no neural runtime is imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "The admission schema validates local file hashes; it never loads "
            "or executes a model.",
            "No network request, download, audio device, model load or timing "
            "run occurs.",
            "The synthetic frame-classifier control uses integer levels and "
            "deterministic LCG state.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract(report: Dict[str, Any], report_digest: str) -> Dict[str, Any]:
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": "feasibility",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": report["task_row_identity"],
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "candidate_requirements": [dict(item) for item in CANDIDATE_REQUIREMENTS],
        "upstream_record": report["upstream_record"],
        "peer_evidence": report["peer_evidence"],
        "admission_schema": ADMISSION_SCHEMA,
        "variant_separation": report["variant_separation"],
        "surrogate_protocol": {
            "label": "synthetic_frame_classifier_control_not_marblenet",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "hop_samples": SURROGATE_FRAME_SAMPLES,
            "total_frames": SURROGATE_TOTAL_FRAMES,
            "total_samples": SURROGATE_TOTAL_SAMPLES,
            "threshold_milli": THRESHOLD_MILLI,
            "causal_context_frames": CAUSAL_CONTEXT_FRAMES,
            "causal_lookahead_frames": 0,
            "offline_window_frames": OFFLINE_WINDOW_FRAMES,
            "offline_lookahead_frames": OFFLINE_HALF_WINDOW_FRAMES,
            "unknown_region": [460, 520],
            "notch_frames": [NOTCH_START_FRAME, NOTCH_END_FRAME],
            "qualification_effect": "none",
            "note": (
                "The centred path is offline only; the framewise path is the "
                "only framewise-available structural control. Neither is the "
                "candidate."),
        },
        "gates": report["gates"],
        "exact_blockers": report["exact_blockers"],
        "reopen_conditions": report["reopen_conditions"],
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "generator": "run.py",
            "cold_start_regenerations": 3,
            "byte_identical_required": True,
            "report_sha256": report_digest,
            "command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py",
        },
    }


# ---------------------------------------------------------------------------
# SOURCES.sha256 manifest.
# ---------------------------------------------------------------------------

SOURCES_HEADER = (
    "# SHA-256 pins for SDK-MARBLENET-VAD.",
    "# source: paths are relative to SOURCE_ROOT; worktree: paths are",
    "# relative to the SDK checkout; pkg: paths are relative to this",
    "# task-evidence directory. The mutable full plan/swarm/TASKS.json is",
    "# never hashed; only the linked-row stable identity is gated.",
    "",
)


def sources_bytes(generated: Dict[str, bytes]) -> bytes:
    lines: List[str] = list(SOURCES_HEADER)
    for relative, digest in sorted(SOURCE_PINS.items()):
        path = SOURCE_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"source pin target missing: {relative}")
        if sha256_bytes(path.read_bytes()) != digest:
            raise ValueError(f"source pin digest changed: {relative}")
        lines.append(f"{digest}  source:{relative}")
    for relative, digest in sorted(BOUNDARY_PINS.items()):
        path = SDK_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"worktree pin target missing: {relative}")
        if sha256_bytes(path.read_bytes()) != digest:
            raise ValueError(f"worktree pin digest changed: {relative}")
        lines.append(f"{digest}  worktree:{relative}")
    for name in LOCAL_PIN_PATHS:
        if name in generated:
            data = generated[name]
        else:
            path = HERE / name
            if not path.is_file():
                raise FileNotFoundError(f"package pin target missing: {name}")
            data = path.read_bytes()
        lines.append(f"{sha256_bytes(data)}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
