# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the task-local
SDK-F0-CONTOUR-SMOOTHING package.

The exact F0-contour smoother, desired target contour, voicing decision rule,
pitch reference and hash-pinned runtime are absent. The merged research record
(candidate matrix record 56) is ``unavailable/blocked`` and names no smoother,
repository revision, checkpoint, parameter set, target contour or voicing
policy, so none is invented here.

This module never imports a model or audio runtime, never loads or executes a
model, never reads or writes real audio, never downloads anything and never
measures a device clock. It provides four verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, weights, smoother configuration, target contour, voicing
  policy, pitch reference pairs, metric specification, rights, cohort, parity
  and runtime records and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* an exactness admission gate for a would-be smoother specification and a
  fail-closed request admission that accepts only the identity-prosody
  comparison baseline because the candidate smoother is absent;
* a deterministic synthetic identity-prosody accounting control at the public
  v0 geometry (16 kHz mono float32, 160 samples per frame) that checks exact
  source/identity sample preservation and offline-only alignment without
  asserting any candidate geometry or output.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

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
REPORT_SCHEMA = "audio-sdk/f0-contour-smoothing-report/0.1"
CALLER_SCHEMA = (
    "audio-sdk/f0-contour-smoothing/caller-supplied-asset/0.1")

TASK_ID = "SDK-F0-CONTOUR-SMOOTHING"
TITLE = "F0 contour smoothing"
COMPONENT = "f0-contour-smoothing"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "23526250a3a0a66c1f93089ff6fb697b5e776965"
BRANCH = "swarm/SDK-F0-CONTOUR-SMOOTHING"
REVIEWER = "reviewer-F0-CONTOUR-SMOOTHING"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-F0-CONTOUR-SMOOTHING")
TASK_PREFIX = "docs/task-evidence/f0-contour-smoothing/"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_PERIOD_NS = 62500

MICRO_SCALE = 1000000
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
PCM_SAMPLE_CAP = 10000000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

CONTROL_SOURCE_SAMPLES = 32000
CONTROL_ENVELOPE_SAMPLES = 400
CONTROL_VOICED_AMPLITUDE_MICRO = 250000
CONTROL_UNVOICED_AMPLITUDE_MICRO = 50000
CONTROL_NOISE_AMPLITUDE_MICRO = 5000
CONTROL_LOW_PERIOD = 100
CONTROL_HIGH_PERIOD = 60

TASK_KIND = "f0_contour_transformation"
COMPARISON_BASELINE = "identity_prosody"
FIXED_CONTOUR_BASELINE = "fixed_contour_target"
SMOOTHING_TARGET = "contour_smoothing"
CALLER_VARIANT = "offline_whole_utterance"
IDENTITY_LABEL = "identity_prosody"

CANDIDATE_RECORD = 56
CANDIDATE_RECORD_PATH = (
    "research/voice-enhancement-20261101/candidate_matrix.csv")
CANDIDATE_REPORT_PATHS = (
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/"
    "REPORT.md",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
)

MISSING_SOURCE_PATH = "data/checkouts/f0-contour-smoothing"
MISSING_WEIGHTS_PATH = "data/models/f0-contour-smoothing"
SMOOTHER_CONFIG_PATH = "data/references/f0-contour-smoothing/smoother.json"
TARGET_CONTOUR_PATH = (
    "data/references/f0-contour-smoothing/target-contour.json")
VOICING_POLICY_PATH = (
    "data/references/f0-contour-smoothing/voicing-policy.json")
PITCH_REFERENCE_PATH = (
    "data/references/f0-contour-smoothing/pitch-reference-pairs.json")
METRIC_SPEC_PATH = "data/references/f0-contour-smoothing/metric-spec.json"
RIGHTS_RECORD_PATH = "data/rights/f0-contour-smoothing-rights.json"
LICENSE_RECORD_PATH = "data/rights/f0-contour-smoothing-license.json"
COHORT_MANIFEST_PATH = (
    "data/runs/f0-contour-smoothing-cohort/manifest.json")
PARITY_MANIFEST_PATH = (
    "data/runs/f0-contour-smoothing-parity/manifest.json")
RUNTIME_ENV_PATH = "data/envs/f0-contour-smoothing"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"

ARTIFACT_FILES: Tuple[str, ...] = (
    "LICENSES.md",
    "README.md",
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

STABLE_TASK_FIELDS = ("id", "title", "mode", "repository", "component")
MUTABLE_TASK_FIELDS = (
    "status",
    "owner",
    "depends_on",
    "write_scope",
    "deliverable",
    "acceptance",
    "evidence",
    "claim",
    "review",
    "handoff",
    "blocked_reason",
    "dispatch_priority",
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
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/"
    "REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS: Dict[str, str] = {
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "sample_format": SAMPLE_FORMAT,
    "sample_period_ns": SAMPLE_PERIOD_NS,
    "declared_control_geometry_only": True,
    "candidate_geometry": "unestablished",
    "candidate_geometry_asserted": False,
}

BOUNDARY: Dict[str, Any] = {
    "task_local_only": True,
    "installed_v0_unchanged": True,
    "public_api_abi_changed": False,
    "public_c_boundary": (
        "not used: no C provider, header or installed target"),
    "provider_registered": False,
    "provider_intake_complete": False,
    "descriptor_registration": False,
    "descriptor_default_changed": False,
    "enabled_by_default": False,
    "registry_changed": False,
    "shared_cmake_changed": False,
    "ci_changed": False,
    "board_or_handoff_changed": False,
    "real_corpus_or_weights": False,
    "model_or_runtime_loaded": False,
    "real_audio_read": False,
    "listening_or_device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "opt_in_required": True,
    "format": FORMAT,
}

SCOPE: Dict[str, Any] = {
    "write_scope": [TASK_PREFIX],
    "files_written": [
        TASK_PREFIX + "LICENSES.md",
        TASK_PREFIX + "README.md",
        TASK_PREFIX + "contract.json",
        TASK_PREFIX + "contract.json.license",
        TASK_PREFIX + "reference.py",
        TASK_PREFIX + "report.json",
        TASK_PREFIX + "report.json.license",
        TASK_PREFIX + "report.json.sha256",
        TASK_PREFIX + "report.json.sha256.license",
        TASK_PREFIX + "run.py",
        TASK_PREFIX + "SOURCES.sha256",
        TASK_PREFIX + "SOURCES.sha256.license",
        TASK_PREFIX + "test_reference.py",
        TASK_PREFIX + "verify.py",
    ],
    "shared_files_untouched": [
        "CMakeLists.txt",
        "CONTRACTS.md",
        "REUSE.toml",
        "api/include/audio_sdk/provider_v0.h",
        "api/include/audio_sdk/session_v0.h",
        "scripts/ci.py",
    ],
    "network_access": False,
    "downloads": False,
    "real_audio_read": False,
    "executed_candidate_code": False,
    "listening_performed": False,
    "device_timing_measured": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No F0-contour smoother, checkpoint, parameter set, target contour, "
    "voicing policy or pitch extractor is implemented, vendored, downloaded "
    "or executed.",
    "No candidate pitch track, smoothed contour, transformed waveform or "
    "exact numeric output exists.",
    "The synthetic identity control is not candidate output and cannot "
    "qualify any candidate.",
    "No real corpus, transcript, clean target pitch, speech or music file is "
    "read or written.",
    "No pitch error, voicing error, content preservation, identity, "
    "naturalness or intelligibility score is measured.",
    "No listening test, MOS panel, device timing, callback deadline, "
    "first-output or tail latency is measured.",
    "No RTF, CPU, memory, streaming or whole-utterance performance claim is "
    "made for any candidate.",
    "No provider is registered, enabled by default or selected as a default; "
    "there is no automatic discovery or fallback.",
    "The installed v0 contract, public API, C ABI, descriptor registry, "
    "shared build, CI and board/handoff files are unchanged.",
    "No benchmark, qualification, release or production-use claim is made.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "A1", "artifact": "exact smoother identity",
     "detail": "Named algorithm, implementation and full 40-hex source "
               "revision naming the smoother actually evaluated.",
     "status": "absent"},
    {"id": "A2", "artifact": "exact smoother parameters",
     "detail": "Byte-pinned configuration declaring window, order, cutoff, "
               "voicing handling and bounded smoothing parameters.",
     "status": "absent"},
    {"id": "A3", "artifact": "desired target contour definition",
     "detail": "Explicit target F0 contour or transformation rule, with "
               "units, time base, tolerance and fallback.",
     "status": "absent"},
    {"id": "A4", "artifact": "voicing decision reference",
     "detail": "Frozen voiced/unvoiced policy and boundary handling for "
               "onsets, offsets and octave errors.",
     "status": "absent"},
    {"id": "A5", "artifact": "source/target pitch reference pairs",
     "detail": "Rights-cleared pitch tracks or audio pairs under the exact "
               "task condition.",
     "status": "absent"},
    {"id": "A6", "artifact": "metric and tolerance specification",
     "detail": "Task-matched pitch error, voicing error, content and "
               "naturalness metrics with acceptance margins.",
     "status": "absent"},
    {"id": "A7", "artifact": "hash-pinned runtime and environment lock",
     "detail": "Isolated package lock, interpreter and runtime digest.",
     "status": "absent"},
    {"id": "A8", "artifact": "rights, consent and output-use decision",
     "detail": "Code, weights, corpus, reference-voice and derivative-output "
               "terms approved for this workload.",
     "status": "absent"},
    {"id": "A9", "artifact": "frozen task-matched cohort",
     "detail": "Rights-cleared, language/speaker-stratified cohort including "
               "quiet/active, voiced/unvoiced and onset/offset cases.",
     "status": "absent"},
)

REQUEST_FIELDS: Tuple[str, ...] = (
    "task_kind",
    "comparison_baseline",
    "variant",
    "target",
    "sample_rate_hz",
    "channels",
    "sample_format",
    "frame_samples",
    "pcm",
)

CALLER_FILE_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("license_record_path", "license_record_sha256"),
    ("weights_path", "weights_sha256"),
    ("smoother_config_path", "smoother_config_sha256"),
    ("target_contour_path", "target_contour_sha256"),
    ("voicing_policy_path", "voicing_policy_sha256"),
    ("pitch_reference_manifest_path", "pitch_reference_manifest_sha256"),
    ("metric_spec_path", "metric_spec_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("rights_decision_path", "rights_decision_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
)
CALLER_DIR_FIELDS: Tuple[str, ...] = (
    "source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS: Tuple[str, ...] = tuple(
    sha for _, sha in CALLER_FILE_PAIRS)
CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "asset_storage",
    "source_checkout_path",
    "source_revision",
    "runtime_path",
    "smoother_id",
    "task_kind",
    "comparison_baseline",
    "variant",
    "channels",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
) + tuple(path for path, _ in CALLER_FILE_PAIRS) + CALLER_SHA_FIELDS

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "schema_id": CALLER_SCHEMA,
    "asset_storage": "external",
    "fields": list(CALLER_ASSET_FIELDS),
    "file_pairs": [
        {"path_field": path, "sha256_field": sha}
        for path, sha in CALLER_FILE_PAIRS
    ],
    "directory_fields": list(CALLER_DIR_FIELDS),
    "required_revision": "full 40 lowercase hex characters",
    "required_smoother_id": "exact lowercase token, never a placeholder",
    "required_rates": "equal input/output rate, duration preserving",
    "admitted_task_kind": TASK_KIND,
    "admitted_baseline": COMPARISON_BASELINE,
    "admitted_variant": CALLER_VARIANT,
    "admitted_channels": CHANNELS,
    "execution": False,
    "note": (
        "The contract hashes caller files but never imports, executes or "
        "loads the caller's source, weights, configuration, contour, "
        "voicing policy or runtime. A caller manifest is a future intake "
        "shape, not a candidate result."),
}

SMOOTHER_SPEC_FIELDS: Tuple[str, ...] = (
    "smoother_id",
    "algorithm_family",
    "parameters",
    "target_contour_defined",
    "voicing_policy_defined",
    "pitch_extractor_id",
    "metric_ids",
)
PLACEHOLDER_TOKENS = frozenset({
    "unspecified",
    "unknown",
    "tbd",
    "tba",
    "default",
    "generic",
    "none",
    "any",
    "placeholder",
    "todo",
    "na",
})
TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{2,63}$")
PARAMETER_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,47}$")

SMOOTHER_SPECIFICATION_GATE: Dict[str, Any] = {
    "schema_id": "audio-sdk/f0-contour-smoothing/smoother-spec/0.1",
    "required_fields": list(SMOOTHER_SPEC_FIELDS),
    "placeholder_tokens_rejected": sorted(PLACEHOLDER_TOKENS),
    "requires_nonempty_exact_parameters": True,
    "requires_target_contour": True,
    "requires_voicing_policy": True,
    "requires_named_pitch_extractor": True,
    "requires_nonempty_unique_metrics": True,
    "candidate_executed": False,
    "qualification_effect": "none",
    "note": (
        "Completeness of a caller-supplied specification is a local intake "
        "gate only. It cannot supply the absent exact implementation, "
        "references, cohort or rights."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "B1", "gate": "exact_smoother_identity_and_source",
     "requirement": (
         "A named smoother implementation with a full 40-hex revision, tree "
         "digest and byte-identical license text. Candidate matrix record 56 "
         "names none.")},
    {"id": "B2", "gate": "exact_smoother_parameters_and_target_contour",
     "requirement": (
         "Byte-pinned smoother parameters, target contour definition, "
         "voicing policy and source/target pitch reference pairs. None is "
         "specified.")},
    {"id": "B3", "gate": "runtime_admission_and_package_lock",
     "requirement": (
         "An isolated, hash-pinned runtime and lock for the exact smoother. "
         "No environment exists.")},
    {"id": "B4", "gate": "artifact_rights_and_corpus_licensing",
     "requirement": (
         "Code, weight, corpus, reference-voice, derivative-output and "
         "redistribution terms cleared for this workload. No rights record "
         "exists.")},
    {"id": "B5", "gate": "frozen_task_matched_pitch_cohort",
     "requirement": (
         "A rights-cleared, language/speaker-stratified cohort with voiced, "
         "unvoiced, onset, offset, quiet and active speech. No cohort "
         "exists.")},
    {"id": "B6", "gate": "pitch_voicing_content_and_naturalness_results",
     "requirement": (
         "Independent pitch error, voicing error, content preservation and "
         "naturalness results against the declared baseline. None exists.")},
    {"id": "B7", "gate": "alignment_timing_and_streaming",
     "requirement": (
         "Exact-runtime content delay, first-output/tail timing, memory, "
         "CPU/RTF and paced streaming behavior. Not measured.")},
    {"id": "B8", "gate": "opt_in_adapter_intake_and_release",
     "requirement": (
         "Opt-in adapter, descriptor/public-surface decision, authorized "
         "listening, benchmark validation, independent exact-head review and "
         "release approval. Not started.")},
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = tuple(
    (item["gate"], item["requirement"]) for item in EXACT_BLOCKERS)

VOICE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("permitted_input_and_target_references", (
        "Permitted input and target pitch references under the exact task "
        "condition."), "absent"),
    ("task_language_speaker_and_prosody_groups", (
        "Frozen task, language, speaker and prosody-condition groups."),
     "absent"),
    ("text_and_semantic_content_preserved", (
        "Text and semantic content preserved as a separate outcome."),
     "not_measured"),
    ("identity_similarity", (
        "Identity/similarity preserved and scored separately."),
     "not_measured"),
    ("target_contour_realization", (
        "Achieved F0 contour and voicing realization against the desired "
        "target."), "not_measured"),
    ("naturalness", (
        "Naturalness scored separately, with permitted listening or an "
        "approved predictive screen."), "not_measured"),
    ("alignment_first_output_and_tail_timing", (
        "Alignment, content delay, first-output and tail timing for the "
        "exact runtime."), "structural_only"),
    ("consent_reference_availability_and_output_use", (
        "Consent, reference availability and output-use gates."), "absent"),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "record": "candidate_matrix.csv record 56",
    "record_status": "unavailable/blocked",
    "record_finding": (
        "No exact smoother or desired contour/voicing reference is "
        "specified; no task accuracy can be calculated."),
    "record_baseline": "Identity prosody; fixed contour target",
    "spatial_trials_note": (
        "No exact smoother, desired target contour, voicing handling or "
        "source/target pitch references; method is underspecified."),
    "transform_space_note": (
        "A pitch-contour postprocessor is a DSP/algorithm family; it needs "
        "pitch extraction, voiced/unvoiced handling and explicit desired "
        "prosody. No single canonical implementation or checkpoint is "
        "specified."),
    "sibling_references_not_substituted": [
        {
            "package": "docs/task-evidence/psola-praat",
            "why_not": (
                "TD-PSOLA time-scale modification, not F0 contour smoothing; "
                "no smoothing target or desired contour."),
        },
        {
            "package": "docs/task-evidence/pitch-period-repeat-plc",
            "why_not": (
                "Packet-loss concealment fixture with an internal period "
                "estimate, not an evaluated F0 smoother or contour target."),
        },
        {
            "package": "docs/task-evidence/emotion-expressive-prosody-"
                       "transformation",
            "why_not": (
                "Separate DEFER row for emotion/style transformation; it "
                "supplies no smoother, target contour or pitch reference."),
        },
        {
            "package": "docs/task-evidence/sylnet",
            "why_not": (
                "Syllable-rate surrogate, not pitch-contour processing."),
        },
    ],
    "provenance_note": (
        "The candidate matrix row is pinned by SHA-256. The named notes are "
        "pinned by SHA-256. No sibling package value is copied into this "
        "report as a candidate metric."),
}

CONTROL_PLAN_PROVENANCE = (
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md Voice profile; "
    "identity-prosody comparison baseline declared by candidate matrix "
    "record 56; local synthetic identity accounting only")

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
    "request_not_object",
    "request_missing_field",
    "request_extra_field",
    "request_wrong_task_kind",
    "request_wrong_variant",
    "request_wrong_format",
    "request_wrong_frame_size",
    "request_channels_zero",
    "request_missing_target",
    "request_unknown_target",
    "request_smoothing_target",
    "request_fixed_contour_target",
    "request_nonidentity_baseline",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_task_kind",
    "manifest_wrong_baseline",
    "manifest_wrong_variant",
    "manifest_channels_zero",
    "manifest_channels_float",
    "manifest_rate_below_range",
    "manifest_rate_above_range",
    "manifest_rate_bool",
    "manifest_rate_mismatch",
    "manifest_placeholder_smoother_id",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
    "manifest_wrong_storage",
    "spec_not_object",
    "spec_missing_field",
    "spec_extra_field",
    "spec_placeholder_smoother_id",
    "spec_invalid_algorithm_family",
    "spec_empty_parameters",
    "spec_float_parameter",
    "spec_zero_parameter",
    "spec_target_contour_false",
    "spec_voicing_policy_false",
    "spec_placeholder_pitch_extractor",
    "spec_empty_metrics",
    "spec_duplicate_metrics",
    "spec_metric_not_string",
)

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


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
    if isinstance(value, float):
        raise ReferenceRejection("noncanonical_float:" + label)
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


# ---------------------------------------------------------------------------
# Fixed-path source, asset and absence audit.
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
    if head.startswith("ref:"):
        ref_path = target / head.split(":", 1)[1].strip()
        if not ref_path.is_file():
            return None
        try:
            head = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
    return head if COMMIT_PATTERN.fullmatch(head) else None


def _license_candidates(repository: Path) -> List[str]:
    names = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.txt")
    found: List[str] = []
    for name in names:
        path = repository / name
        if path.is_file():
            found.append(str(path.relative_to(SOURCE_ROOT)))
    return found


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_SOURCE_PATH,
        SOURCE_ROOT / "data/checkouts/f0-contour-smoothing",
        SOURCE_ROOT / "data/checkouts/pitch-contour-smoothing",
        SOURCE_ROOT / "data/checkouts/f0-smoothing",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
                     "f0-contour-smoothing",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
                     "pitch-contour-smoothing",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_WEIGHTS_PATH,
        SOURCE_ROOT / "data/models/pitch-contour-smoothing",
        SOURCE_ROOT / "data/models/f0-smoothing",
        SOURCE_ROOT / "data/weights/f0-contour-smoothing",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
                     "f0-contour-smoothing/checkpoints",
    ]


ABSENCE_PROBES: Tuple[str, ...] = (
    "data/checkouts/f0-contour-smoothing",
    "data/checkouts/pitch-contour-smoothing",
    "data/checkouts/f0-smoothing",
    "data/models/f0-contour-smoothing",
    "data/models/pitch-contour-smoothing",
    "data/models/f0-smoothing",
    "data/weights/f0-contour-smoothing",
    "data/references/f0-contour-smoothing/smoother.json",
    "data/references/f0-contour-smoothing/target-contour.json",
    "data/references/f0-contour-smoothing/voicing-policy.json",
    "data/references/f0-contour-smoothing/pitch-reference-pairs.json",
    "data/references/f0-contour-smoothing/metric-spec.json",
    "data/rights/f0-contour-smoothing-rights.json",
    "data/rights/f0-contour-smoothing-license.json",
    "data/envs/f0-contour-smoothing",
    "data/envs/f0-contour-smoothing/requirements.lock",
    "data/runs/f0-contour-smoothing-cohort/manifest.json",
    "data/runs/f0-contour-smoothing-parity/manifest.json",
    TASK_PREFIX + "reference_output.wav",
    TASK_PREFIX + "cohort",
)


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def assert_no_candidate_artifacts(probes: Sequence[Dict[str, Any]]) -> None:
    for item in probes:
        if item.get("exists") is not False:
            raise ReferenceRejection(
                "candidate_artifact_present:" + str(item.get("path")))
    if len(probes) != len(ABSENCE_PROBES):
        raise ReferenceRejection("absence_probe_count_mismatch")


def audit_assets() -> Dict[str, Any]:
    source_paths = _source_candidates()
    present_sources = [path for path in source_paths if path.is_dir()]
    repository = present_sources[0] if present_sources else None
    revision = _read_git_head(repository) if repository is not None else None
    licenses = _license_candidates(repository) if repository is not None else []
    weight_paths = _weights_candidates()
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
        "smoother_config_present": (SOURCE_ROOT / SMOOTHER_CONFIG_PATH).is_file(),
        "target_contour_present": (SOURCE_ROOT / TARGET_CONTOUR_PATH).is_file(),
        "voicing_policy_present": (SOURCE_ROOT / VOICING_POLICY_PATH).is_file(),
        "pitch_reference_present": (SOURCE_ROOT / PITCH_REFERENCE_PATH).is_file(),
        "metric_spec_present": (SOURCE_ROOT / METRIC_SPEC_PATH).is_file(),
        "rights_record_present": (SOURCE_ROOT / RIGHTS_RECORD_PATH).is_file(),
        "license_record_present": (SOURCE_ROOT / LICENSE_RECORD_PATH).is_file(),
        "runtime_env_present": (SOURCE_ROOT / RUNTIME_ENV_PATH).is_dir(),
        "runtime_lock_present": (SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file(),
        "cohort_manifest_present": (
            SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file(),
        "parity_manifest_present": (
            SOURCE_ROOT / PARITY_MANIFEST_PATH).is_file(),
        "reference_audio_present": (
            SOURCE_ROOT / (TASK_PREFIX + "reference_output.wav")).is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "task_kind": TASK_KIND,
            "comparison_baseline": COMPARISON_BASELINE,
            "fixed_contour_baseline": FIXED_CONTOUR_BASELINE,
            "candidate_geometry_status": "unestablished",
            "target_contour_status": "unestablished",
            "voicing_policy_status": "unestablished",
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
            "upstream_revision": None,
        },
    }


def task_row_identity() -> Dict[str, Any]:
    path = SOURCE_ROOT / TASK_BOARD_REL
    if not path.is_file():
        raise ReferenceRejection(
            "task board is unavailable at " + TASK_BOARD_REL)
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
    if stable["title"] != TITLE:
        raise ReferenceRejection("linked task row title mismatch")
    return {
        "source": TASK_BOARD_REL,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(
            canonical_text(stable).encode("utf-8")),
        "full_tasks_json_hashed": False,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "note": (
            "Only stable linked-row fields are read and gated. The mutable "
            "full plan/swarm/TASKS.json is never hashed, pinned or used as a "
            "digest source."),
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic PCM, identity control, admission and specification.
# ---------------------------------------------------------------------------

def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def _triangle(index: int, period: int) -> float:
    """Zero-mean triangle in [-1, 1]; integer phase arithmetic only."""
    phase = index % period
    return (2 * abs(2 * phase - period) - period) / float(period)


def _segment_map() -> Tuple[Tuple[str, int, int], ...]:
    return (
        ("silence_lead", 0, 4000),
        ("voiced_low", 4000, 14000),
        ("voiced_high", 14000, 24000),
        ("unvoiced_noise", 24000, 30000),
        ("silence_tail", 30000, CONTROL_SOURCE_SAMPLES),
    )


def synthetic_source_pcm() -> List[float]:
    """Deterministic 2.0 s stimulus: silence, two voiced periods, unvoiced
    noise and silence. It is a harness stimulus, not candidate output."""
    samples: List[float] = []
    state = 0x0F0C0A11
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        value = 0.0
        if 4000 <= index < 14000:
            rising = (index - 4000) * MICRO_SCALE
            falling = (14000 - index) * MICRO_SCALE
            ramp = min(MICRO_SCALE,
                       rising // CONTROL_ENVELOPE_SAMPLES,
                       falling // CONTROL_ENVELOPE_SAMPLES)
            tone = _triangle(index - 4000, CONTROL_LOW_PERIOD)
            value = (CONTROL_VOICED_AMPLITUDE_MICRO / MICRO_SCALE) * tone * (
                ramp / MICRO_SCALE)
            value += (CONTROL_NOISE_AMPLITUDE_MICRO / MICRO_SCALE) * noise
        elif 14000 <= index < 24000:
            rising = (index - 14000) * MICRO_SCALE
            falling = (24000 - index) * MICRO_SCALE
            ramp = min(MICRO_SCALE,
                       rising // CONTROL_ENVELOPE_SAMPLES,
                       falling // CONTROL_ENVELOPE_SAMPLES)
            tone = _triangle(index - 14000, CONTROL_HIGH_PERIOD)
            value = (CONTROL_VOICED_AMPLITUDE_MICRO / MICRO_SCALE) * tone * (
                ramp / MICRO_SCALE)
            value += (CONTROL_NOISE_AMPLITUDE_MICRO / MICRO_SCALE) * noise
        elif 24000 <= index < 30000:
            value = (CONTROL_UNVOICED_AMPLITUDE_MICRO / MICRO_SCALE) * noise
        samples.append(value)
    if len(samples) != CONTROL_SOURCE_SAMPLES:
        raise ReferenceRejection("synthetic_sample_count_mismatch")
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise ReferenceRejection("pcm_rate_not_integer")
    if sample_rate_hz != SAMPLE_RATE_HZ:
        raise ReferenceRejection("pcm_wrong_rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("pcm_channels_not_integer")
    if channels != CHANNELS:
        raise ReferenceRejection("pcm_wrong_channels")
    if not isinstance(signal, (list, tuple)):
        raise ReferenceRejection("pcm_not_sequence")
    if len(signal) == 0:
        raise ReferenceRejection("pcm_empty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise ReferenceRejection("pcm_over_cap")
    result: List[float] = []
    for index, value in enumerate(signal):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("pcm_value_not_numeric:" + str(index))
        number = float(value)
        if not math.isfinite(number):
            raise ReferenceRejection("pcm_nonfinite:" + str(index))
        if abs(number) > 1.0:
            raise ReferenceRejection("pcm_out_of_range:" + str(index))
        result.append(number)
    return result


def _quantized_micro(values: Sequence[float]) -> List[int]:
    return [int(round(float(value) * MICRO_SCALE)) for value in values]


def pcm_summary(signal: Sequence[float]) -> Dict[str, Any]:
    micro = _quantized_micro(signal)
    digest = hashlib.sha256()
    peak = 0
    energy = 0
    for value in micro:
        digest.update(int(value).to_bytes(4, "little", signed=True))
        magnitude = abs(value)
        if magnitude > peak:
            peak = magnitude
        energy += value * value
    samples = len(micro)
    rms = math.isqrt(energy // samples) if samples else 0
    return {
        "samples": samples,
        "duration_ns": samples * SAMPLE_PERIOD_NS,
        "peak_micro": peak,
        "rms_micro": rms,
        "sha256": digest.hexdigest(),
    }


def identity_transform(signal: Sequence[float]) -> List[float]:
    return [float(value) for value in signal]


def identity_request() -> Dict[str, Any]:
    return {
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "target": IDENTITY_LABEL,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "pcm": synthetic_source_pcm(),
    }


def _require_exact_fields(value: Any, expected: Sequence[str],
                          label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ReferenceRejection(label + "_must_be_object")
    expected_set = set(expected)
    present = set(value)
    missing = sorted(expected_set - present)
    extra = sorted(present - expected_set)
    if missing:
        raise ReferenceRejection(label + "_missing_fields:" + ",".join(missing))
    if extra:
        raise ReferenceRejection(label + "_unknown_fields:" + ",".join(extra))
    return value


def admit_request(request: Any) -> Dict[str, Any]:
    request = _require_exact_fields(request, REQUEST_FIELDS, "request")
    if request["task_kind"] != TASK_KIND:
        raise ReferenceRejection("request_wrong_task_kind")
    if request["variant"] != CALLER_VARIANT:
        raise ReferenceRejection(
            "request_streaming_variant_not_admitted")
    if request["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("request_wrong_sample_format")
    rate = request["sample_rate_hz"]
    if isinstance(rate, bool) or not isinstance(rate, int):
        raise ReferenceRejection("request_rate_not_integer")
    channels = request["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("request_channels_not_integer")
    frame = request["frame_samples"]
    if isinstance(frame, bool) or not isinstance(frame, int):
        raise ReferenceRejection("request_frame_not_integer")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_control_geometry:rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_control_geometry:channels")
    if frame != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_control_geometry:frame")
    pcm = validate_pcm(request["pcm"], rate, channels)
    target = request["target"]
    baseline = request["comparison_baseline"]
    if not isinstance(target, str) or not isinstance(baseline, str):
        raise ReferenceRejection("request_target_or_baseline_not_string")
    if target == SMOOTHING_TARGET:
        raise ReferenceRejection("absent_candidate_smoother")
    if target == FIXED_CONTOUR_BASELINE:
        raise ReferenceRejection("absent_exact_target_contour")
    if target != IDENTITY_LABEL:
        raise ReferenceRejection("unknown_target")
    if baseline != COMPARISON_BASELINE:
        raise ReferenceRejection("baseline_not_identity")
    return {
        "accepted": True,
        "identity_control": True,
        "candidate_smoother_used": False,
        "transformation_performed": False,
        "pcm_samples": len(pcm),
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame,
        "target": target,
        "comparison_baseline": baseline,
        "qualification_effect": "none",
    }


def _exact_token(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ReferenceRejection(label + "_not_string")
    if not TOKEN_PATTERN.fullmatch(value):
        raise ReferenceRejection(label + "_invalid_token")
    if value in PLACEHOLDER_TOKENS:
        raise ReferenceRejection(label + "_is_placeholder")
    return value


def admit_smoother_specification(spec: Any) -> Dict[str, Any]:
    spec = _require_exact_fields(spec, SMOOTHER_SPEC_FIELDS, "spec")
    smoother_id = _exact_token(spec["smoother_id"], "smoother_id")
    family = _exact_token(spec["algorithm_family"], "algorithm_family")
    pitch_extractor = _exact_token(
        spec["pitch_extractor_id"], "pitch_extractor_id")
    parameters = spec["parameters"]
    if not isinstance(parameters, dict) or not parameters:
        raise ReferenceRejection("spec_parameters_not_nonempty_object")
    normalized: Dict[str, Any] = {}
    for key, value in parameters.items():
        if not isinstance(key, str) or not PARAMETER_KEY_PATTERN.fullmatch(key):
            raise ReferenceRejection("spec_parameter_key_invalid")
        if key in PLACEHOLDER_TOKENS:
            raise ReferenceRejection("spec_parameter_key_is_placeholder")
        if isinstance(value, bool):
            raise ReferenceRejection("spec_parameter_value_bool")
        if isinstance(value, float):
            raise ReferenceRejection("spec_parameter_value_float")
        if isinstance(value, int):
            if value < 1:
                raise ReferenceRejection("spec_parameter_value_out_of_range")
            normalized[key] = value
            continue
        if isinstance(value, str):
            normalized[key] = _exact_token(
                value, "spec_parameter_value")
            continue
        raise ReferenceRejection("spec_parameter_value_type")
    if spec["target_contour_defined"] is not True:
        raise ReferenceRejection("spec_target_contour_not_defined")
    if spec["voicing_policy_defined"] is not True:
        raise ReferenceRejection("spec_voicing_policy_not_defined")
    metrics = spec["metric_ids"]
    if not isinstance(metrics, list) or not metrics:
        raise ReferenceRejection("spec_metric_ids_not_nonempty_list")
    seen: List[str] = []
    for item in metrics:
        token = _exact_token(item, "metric_id")
        if token in seen:
            raise ReferenceRejection("spec_metric_ids_duplicate")
        seen.append(token)
    return {
        "accepted": True,
        "smoother_id": smoother_id,
        "algorithm_family": family,
        "pitch_extractor_id": pitch_extractor,
        "parameter_keys": sorted(normalized),
        "metric_ids": seen,
        "target_contour_defined": True,
        "voicing_policy_defined": True,
        "candidate_executed": False,
        "qualification_effect": "none",
    }


# ---------------------------------------------------------------------------
# Caller-supplied-asset manifest contract (never executed).
# ---------------------------------------------------------------------------

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
    manifest = _require_exact_fields(
        manifest, CALLER_ASSET_FIELDS, "manifest")
    if manifest["asset_storage"] != "external":
        raise ReferenceRejection("manifest_asset_storage_must_be_external")
    if manifest["task_kind"] != TASK_KIND:
        raise ReferenceRejection("manifest_wrong_task_kind")
    if manifest["comparison_baseline"] != COMPARISON_BASELINE:
        raise ReferenceRejection("manifest_wrong_baseline")
    if manifest["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("manifest_wrong_variant")
    smoother_id = _exact_token(manifest["smoother_id"], "manifest_smoother_id")
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
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
            raise ReferenceRejection("manifest_" + field + "_must_be_path")
        if not Path(value).is_absolute():
            raise ReferenceRejection(
                "manifest_" + field + "_must_be_absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise ReferenceRejection(
            "manifest_source_revision_must_be_full_40_hex")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("manifest_channels_must_be_integer")
    if channels != CHANNELS:
        raise ReferenceRejection("manifest_channels_mismatch")
    input_rate = _rate_value(manifest, "sample_rate_input_hz")
    output_rate = _rate_value(manifest, "sample_rate_output_hz")
    if input_rate != output_rate:
        raise ReferenceRejection("manifest_rate_must_be_duration_preserving")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise ReferenceRejection(
                "manifest_" + field + "_directory_missing")
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
        "smoother_id": smoother_id,
        "source_revision": revision,
        "revision_caller_declared_not_independently_verified": True,
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "sample_rate_hz": input_rate,
        "channels": CHANNELS,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "audio_read": False,
        "qualification_effect": "none",
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files exist inside this package. It proves
    the intake shape and hash checking without executing anything."""
    assignments = {
        "license_record_path": TASK_DIR / "LICENSES.md",
        "weights_path": TASK_DIR / "reference.py",
        "smoother_config_path": TASK_DIR / "run.py",
        "target_contour_path": TASK_DIR / "contract.json.license",
        "voicing_policy_path": TASK_DIR / "README.md",
        "pitch_reference_manifest_path": TASK_DIR / "verify.py",
        "metric_spec_path": TASK_DIR / "test_reference.py",
        "cohort_manifest_path": TASK_DIR / "SOURCES.sha256.license",
        "rights_decision_path": TASK_DIR / "report.json.license",
        "runtime_lock_path": TASK_DIR / "report.json.sha256.license",
    }
    manifest: Dict[str, Any] = {
        "asset_storage": "external",
        "source_checkout_path": str(TASK_DIR),
        "source_revision": "c" * 40,
        "runtime_path": str(TASK_DIR),
        "smoother_id": "median_filter_exact",
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "channels": CHANNELS,
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = file_digest(path)
    return manifest


def synthetic_complete_spec() -> Dict[str, Any]:
    """A fully specified local intake probe. It is not a candidate."""
    return {
        "smoother_id": "median_filter_exact",
        "algorithm_family": "median_filter",
        "parameters": {"window_frames": 5, "voicing_hold_frames": 2},
        "target_contour_defined": True,
        "voicing_policy_defined": True,
        "pitch_extractor_id": "autocorrelation_40_400hz",
        "metric_ids": ["pitch_rmse_cents", "voicing_error_rate"],
    }


# ---------------------------------------------------------------------------
# Adverse controls.
# ---------------------------------------------------------------------------

def run_adverse_controls() -> List[Dict[str, Any]]:
    good_pcm = synthetic_source_pcm()
    good_request = identity_request()
    good_manifest = _existing_file_manifest()
    good_spec = synthetic_complete_spec()

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

    def request_wrong(key: str, value: Any):
        request = dict(good_request)
        request[key] = value
        return lambda: admit_request(request)

    def request_drop(key: str):
        request = {k: v for k, v in good_request.items() if k != key}
        return lambda: admit_request(request)

    def manifest_wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def manifest_drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    def spec_wrong(key: str, value: Any):
        spec = dict(good_spec)
        spec[key] = value
        return lambda: admit_smoother_specification(spec)

    def spec_drop(key: str):
        spec = {k: v for k, v in good_spec.items() if k != key}
        return lambda: admit_smoother_specification(spec)

    existing = _existing_file_manifest()
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_pcm, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_pcm, SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("request_not_object", lambda: admit_request([])),
        ("request_missing_field", request_drop("frame_samples")),
        ("request_extra_field", lambda: admit_request(
            dict(good_request, extra_field="x"))),
        ("request_wrong_task_kind", request_wrong(
            "task_kind", "text_to_speech")),
        ("request_wrong_variant", request_wrong(
            "variant", "incremental_streaming")),
        ("request_wrong_format", request_wrong("sample_format", "int16")),
        ("request_wrong_frame_size", request_wrong("frame_samples", 320)),
        ("request_channels_zero", request_wrong("channels", 0)),
        ("request_missing_target", request_drop("target")),
        ("request_unknown_target", request_wrong("target", "not_a_target_")),
        ("request_smoothing_target", request_wrong("target", SMOOTHING_TARGET)),
        ("request_fixed_contour_target", request_wrong(
            "target", FIXED_CONTOUR_BASELINE)),
        ("request_nonidentity_baseline", request_wrong(
            "comparison_baseline", FIXED_CONTOUR_BASELINE)),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", manifest_drop("weights_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", manifest_wrong(
            "weights_path", "weights/smoother.bin")),
        ("manifest_bad_sha", manifest_wrong("weights_sha256", "ABC")),
        ("manifest_short_revision", manifest_wrong(
            "source_revision", "2352625")),
        ("manifest_nonhex_revision", manifest_wrong(
            "source_revision", "g" * 40)),
        ("manifest_wrong_task_kind", manifest_wrong(
            "task_kind", "speech_to_speech_voice_conversion")),
        ("manifest_wrong_baseline", manifest_wrong(
            "comparison_baseline", FIXED_CONTOUR_BASELINE)),
        ("manifest_wrong_variant", manifest_wrong(
            "variant", "incremental_streaming")),
        ("manifest_channels_zero", manifest_wrong("channels", 0)),
        ("manifest_channels_float", manifest_wrong("channels", 1.0)),
        ("manifest_rate_below_range", manifest_wrong(
            "sample_rate_input_hz", 4000)),
        ("manifest_rate_above_range", manifest_wrong(
            "sample_rate_output_hz", 384000)),
        ("manifest_rate_bool", manifest_wrong(
            "sample_rate_output_hz", True)),
        ("manifest_rate_mismatch", manifest_wrong(
            "sample_rate_output_hz", 48000)),
        ("manifest_placeholder_smoother_id", manifest_wrong(
            "smoother_id", "unspecified")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, weights_path=(
                "/nonexistent/f0-contour-smoothing/weights.bin")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/f0-contour-smoothing/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, weights_sha256="0" * 64))),
        ("manifest_wrong_storage", manifest_wrong("asset_storage", "vendored")),
        ("spec_not_object", lambda: admit_smoother_specification([])),
        ("spec_missing_field", spec_drop("metric_ids")),
        ("spec_extra_field", lambda: admit_smoother_specification(
            dict(good_spec, extra_field="x"))),
        ("spec_placeholder_smoother_id", spec_wrong(
            "smoother_id", "unspecified")),
        ("spec_invalid_algorithm_family", spec_wrong(
            "algorithm_family", "Median Filter!")),
        ("spec_empty_parameters", spec_wrong("parameters", {})),
        ("spec_float_parameter", spec_wrong(
            "parameters", {"window_frames": 5.0})),
        ("spec_zero_parameter", spec_wrong(
            "parameters", {"window_frames": 0})),
        ("spec_target_contour_false", spec_wrong(
            "target_contour_defined", False)),
        ("spec_voicing_policy_false", spec_wrong(
            "voicing_policy_defined", False)),
        ("spec_placeholder_pitch_extractor", spec_wrong(
            "pitch_extractor_id", "default")),
        ("spec_empty_metrics", spec_wrong("metric_ids", [])),
        ("spec_duplicate_metrics", spec_wrong(
            "metric_ids", ["pitch_rmse_cents", "pitch_rmse_cents"])),
        ("spec_metric_not_string", spec_wrong("metric_ids", ["pitch_rmse", 3])),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_count_mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_ids_mismatch")
    if any(item["result"] != "rejected" for item in results):
        raise ReferenceRejection("adverse_case_not_rejected")
    return results


# ---------------------------------------------------------------------------
# Control and report.
# ---------------------------------------------------------------------------

def duration_accounting(input_samples: int, output_samples: int) -> Dict[str, Any]:
    if input_samples < 0 or output_samples < 0:
        raise ReferenceRejection("negative_sample_count")
    return {
        "input_samples": input_samples,
        "output_samples": output_samples,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "input_duration_ns": input_samples * SAMPLE_PERIOD_NS,
        "output_duration_ns": output_samples * SAMPLE_PERIOD_NS,
        "sample_count_delta": output_samples - input_samples,
        "duration_preserved": input_samples == output_samples,
        "frame_accounting": {
            "frame_samples": FRAME_SAMPLES,
            "complete_frames": input_samples // FRAME_SAMPLES,
            "remainder_samples": input_samples % FRAME_SAMPLES,
        },
    }


def alignment_accounting(output_samples: int) -> Dict[str, Any]:
    return {
        "alignment_basis": "identity_caller_supplied_control",
        "content_delay_samples": 0,
        "content_delay_ns": 0,
        "first_output_input_sample": 0,
        "tail_input_sample": output_samples,
        "incremental_streaming": False,
        "device_clock_used": False,
        "qualification_effect": "none",
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = identity_transform(source)
    source_summary = pcm_summary(source)
    output_summary = pcm_summary(output)
    duration = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    accepted = admit_request(identity_request())
    rejected_targets: List[Dict[str, str]] = []
    for target in (SMOOTHING_TARGET, FIXED_CONTOUR_BASELINE):
        request = identity_request()
        request["target"] = target
        try:
            admit_request(request)
        except ReferenceRejection as error:
            rejected_targets.append({"target": target, "reason": error.code})
    if len(rejected_targets) != 2:
        raise ReferenceRejection("candidate_target_not_rejected")
    accepted_spec = admit_smoother_specification(synthetic_complete_spec())
    rejected_specs: List[Dict[str, str]] = []
    for name, spec in (
        ("placeholder_smoother_id", dict(
            synthetic_complete_spec(), smoother_id="unspecified")),
        ("missing_target_contour", dict(
            synthetic_complete_spec(), target_contour_defined=False)),
        ("missing_parameters", dict(
            synthetic_complete_spec(), parameters={})),
    ):
        try:
            admit_smoother_specification(spec)
        except ReferenceRejection as error:
            rejected_specs.append({"spec": name, "reason": error.code})
    if len(rejected_specs) != 3:
        raise ReferenceRejection("incomplete_spec_not_rejected")
    adverse = run_adverse_controls()
    segments = [
        {"id": name, "start_sample": start, "end_sample": end,
         "samples": end - start}
        for name, start, end in _segment_map()
    ]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "control_label": (
            "caller_supplied_synthetic_identity_prosody_acceptance_control_"
            "not_smoother_output"),
        "geometry": {
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
            "control_sample_format": SAMPLE_FORMAT,
            "candidate_geometry_status": "unestablished",
            "candidate_geometry_asserted": False,
            "target_contour_status": "unestablished",
            "voicing_policy_status": "unestablished",
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "stimulus_segments": segments,
        "source_pcm": source_summary,
        "identity_output_pcm": output_summary,
        "identity_baseline": {
            "baseline": COMPARISON_BASELINE,
            "transformation_performed": False,
            "sample_count_equal": (
                source_summary["samples"] == output_summary["samples"]),
            "duration_equal": (
                source_summary["duration_ns"] == output_summary["duration_ns"]),
            "digest_equal": (
                source_summary["sha256"] == output_summary["sha256"]),
            "peak_bounded": output_summary["peak_micro"] <= MICRO_SCALE,
            "content_delay_samples": 0,
            "qualification_effect": "none",
        },
        "request_admission": {
            "identity_control_accepted": accepted["accepted"],
            "identity_control": accepted["identity_control"],
            "candidate_smoother_used": accepted["candidate_smoother_used"],
            "rejected_targets": rejected_targets,
            "candidate_targets_rejected": len(rejected_targets) == 2,
            "transformation_performed": False,
            "qualification_effect": "none",
        },
        "smoother_specification_gate": {
            "complete_example_accepted": accepted_spec["accepted"],
            "complete_example_label": (
                "synthetic_local_intake_probe_not_candidate_specification"),
            "complete_example_smoother_id": accepted_spec["smoother_id"],
            "parameter_keys": accepted_spec["parameter_keys"],
            "metric_ids": accepted_spec["metric_ids"],
            "candidate_executed": accepted_spec["candidate_executed"],
            "incomplete_examples_rejected": rejected_specs,
            "incomplete_rejected_count": len(rejected_specs),
            "qualification_effect": "none",
        },
        "duration": duration,
        "alignment": alignment,
        "acceptance_outcomes": [
            {
                "id": "permitted_input_and_target_references",
                "measured": False,
                "value": None,
                "reason": "no permitted source/target pitch reference pair",
            },
            {
                "id": "content_preservation",
                "measured": False,
                "value": None,
                "reason": "no real cohort, transcript truth or candidate output",
            },
            {
                "id": "identity_similarity",
                "measured": False,
                "value": None,
                "reason": "no real source/target reference or speaker model",
            },
            {
                "id": "target_contour_realization",
                "measured": False,
                "value": None,
                "reason": "no desired target contour and no candidate pitch track",
            },
            {
                "id": "voicing_error",
                "measured": False,
                "value": None,
                "reason": "no voicing policy reference and no candidate output",
            },
            {
                "id": "naturalness",
                "measured": False,
                "value": None,
                "reason": "no authorized listening or approved predictive screen",
            },
            {
                "id": "alignment_and_timing",
                "measured": False,
                "value": None,
                "reason": "structural offline accounting only; no exact runtime",
            },
            {
                "id": "consent_and_output_use",
                "measured": False,
                "value": None,
                "reason": "rights and consent records absent",
            },
        ],
        "adverse": adverse,
        "adverse_all_rejected": all(
            item["result"] == "rejected" for item in adverse),
        "adverse_case_count": len(adverse),
    }


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> Optional[str]:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> Optional[str]:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
    best: Optional[str] = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    assert_no_candidate_artifacts(audit["absence_probes"])
    if (audit["source_checkout_present"] or audit["weights_present"]
            or audit["smoother_config_present"]
            or audit["target_contour_present"]
            or audit["voicing_policy_present"]
            or audit["pitch_reference_present"]
            or audit["metric_spec_present"]
            or audit["rights_record_present"]
            or audit["license_record_present"]
            or audit["runtime_env_present"]
            or audit["runtime_lock_present"]
            or audit["cohort_manifest_present"]
            or audit["parity_manifest_present"]
            or audit["reference_audio_present"]):
        raise ReferenceRejection("candidate_artifact_appeared")
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
        "repository": REPOSITORY,
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
                "The record names no exact F0-contour smoother, repository "
                "revision, parameter set, desired target contour, voicing "
                "policy, pitch reference pair, metric specification, rights "
                "record, hash-pinned runtime, cohort or parity vector, so "
                "every release gate remains blocked."),
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
        "candidate": {
            "name": TITLE,
            "record": "candidate_matrix.csv record " + str(CANDIDATE_RECORD),
            "record_name": TITLE,
            "record_status": "unavailable/blocked",
            "candidate_kind": "unspecified_algorithm_family",
            "source_record": CANDIDATE_RECORD_PATH,
            "source_record_sha256": SOURCE_PINS[CANDIDATE_RECORD_PATH],
            "report_paths": list(CANDIDATE_REPORT_PATHS),
            "baseline": "Identity prosody; fixed contour target",
            "finding": (
                "No exact smoother or desired contour/voicing reference is "
                "specified; no task accuracy can be calculated."),
            "source_present": False,
            "source_revision": None,
            "source_sha256": None,
            "weights_present": False,
            "weights_sha256": None,
            "smoother_id": None,
            "smoother_parameters_present": False,
            "target_contour_present": False,
            "voicing_policy_present": False,
            "pitch_reference_present": False,
            "metric_spec_present": False,
            "runtime_present": False,
            "geometry_documented": False,
            "implemented_here": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "evidence_status": "blocked",
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "smoother_specification_gate": SMOOTHER_SPECIFICATION_GATE,
        "licensing": {
            "package_license": "Apache-2.0",
            "upstream_license_reported": None,
            "license_text_staged": False,
            "weights_terms_staged": False,
            "training_data_statement_staged": False,
            "reference_voice_consent_staged": False,
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
                "Structural accounting passes, but no real smoother, "
                "permitted pitch reference set, desired contour, voicing "
                "policy, rights-cleared cohort, target runtime or approved "
                "parity exists, so the voice profile is not satisfied for "
                "qualification."),
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
            "candidate_target_rejected_before_processing": True,
            "incomplete_specification_rejected": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_case_count": control["adverse_case_count"],
            "adverse_all_rejected": control["adverse_all_rejected"],
        },
        "gates": gates,
        "release_gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_condition": (
            "Pin the exact licensed F0-contour smoother implementation and "
            "full 40-hex revision with byte-identical license text; supply "
            "byte-pinned parameters, a desired target contour definition, a "
            "voicing policy and rights-cleared source/target pitch reference "
            "pairs; supply a task-matched metric and tolerance specification; "
            "clear code, weight, corpus, reference-voice, derivative-output, "
            "redistribution and product-use rights; freeze a rights-cleared "
            "language/speaker-stratified cohort and parity vector; reproduce "
            "the exact runtime against the identity-prosody and fixed-contour "
            "baselines; measure pitch error, voicing error, content, identity, "
            "naturalness, alignment and device timing; and complete opt-in "
            "adapter intake. Until every condition is closed the candidate "
            "stays DEFER, incomplete and not qualified."),
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            SMOOTHER_CONFIG_PATH,
            TARGET_CONTOUR_PATH,
            VOICING_POLICY_PATH,
            PITCH_REFERENCE_PATH,
            METRIC_SPEC_PATH,
            LICENSE_RECORD_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is "
            "imported.",
            "Fixed workspace paths are probed for source, weights, smoother "
            "configuration, target contour, voicing policy, pitch reference, "
            "metric, rights, runtime and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load, listening "
            "test or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline; no JSON floats"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
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


def build_contract(report: Dict[str, Any],
                   report_digest: str) -> Dict[str, Any]:
    sidecar_digest = sha256_bytes((report_digest + "\n").encode("utf-8"))
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
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
        "blocked_release_gate_count": len(GATE_REQUIREMENTS),
        "qualification": report["qualification"],
        "format": report["format"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "candidate": report["candidate"],
        "asset_requirements": report["asset_requirements"],
        "asset_audit": report["asset_audit"],
        "caller_asset_contract": report["caller_asset_contract"],
        "smoother_specification_gate": report["smoother_specification_gate"],
        "licensing": report["licensing"],
        "voice_profile": report["voice_profile"],
        "reference_protocol": report["reference_protocol"],
        "controls": {
            "identity_baseline_exact": report["controls"][
                "identity_baseline_exact"],
            "candidate_target_rejected_before_processing": report[
                "controls"]["candidate_target_rejected_before_processing"],
            "incomplete_specification_rejected": report["controls"][
                "incomplete_specification_rejected"],
            "adverse_all_rejected": report["controls"]["adverse_all_rejected"],
            "adverse_case_count": report["controls"]["adverse_case_count"],
        },
        "task_row_identity": report["task_row_identity"],
        "board_row": report["task_row_identity"],
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
            "no F0-contour smoother, checkpoint, parameter set, target "
            "contour, voicing policy, pitch reference or runtime is "
            "downloaded, copied, loaded or executed",
            "only the identity-prosody comparison baseline is admitted; "
            "contour smoothing and fixed-contour targets fail closed because "
            "the candidate smoother and target contour are absent",
            "a caller manifest or complete-looking smoother specification "
            "cannot qualify the candidate",
            "no candidate rate, frame, pitch range, voicing rule, contour "
            "taxonomy, timing protocol or output geometry is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-F0-CONTOUR-SMOOTHING.",
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
    "ABSENCE_PROBES",
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
    "SCOPE_BASE_REFS",
    "SOURCE_PINS",
    "TASK_ID",
    "admit_request",
    "admit_smoother_specification",
    "alignment_accounting",
    "artifact_pins",
    "assert_no_candidate_artifacts",
    "audit_assets",
    "build_contract",
    "build_control",
    "build_report",
    "canonical_report",
    "canonical_text",
    "duration_accounting",
    "file_digest",
    "git_commit",
    "identity_request",
    "identity_transform",
    "load_strict_json",
    "load_strict_json_text",
    "object_digest",
    "pcm_summary",
    "probe_absence",
    "run_adverse_controls",
    "scope_base",
    "scope_changed_paths",
    "scope_violations",
    "sha256_bytes",
    "sources_bytes",
    "synthetic_complete_spec",
    "synthetic_source_pcm",
    "task_row_identity",
    "validate_caller_manifest",
    "validate_pcm",
]
