# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-STREAMVC.

The voice-conversion census records StreamVC as Blocked: the official source
checkout is present at a pinned revision, but it has no obtainable inference
checkpoint or complete weight setup. Its source license is not pinned and the
The S38 paper is a lead only and the unofficial checkout has no trained checkpoint or full streaming inference. This
module never imports a model or audio runtime, never reads or writes real audio,
never downloads anything and never measures a device clock.

It provides:

* a fail-closed source/asset audit of fixed workspace paths;
* a caller-supplied-external-asset manifest contract validated without
  execution, following CONTRACTS.md ``as_asset_v0``;
* a fail-closed request admission that accepts only the identity-source control
  and rejects candidate conversion targets;
* a deterministic synthetic identity accounting control at the public v0
  geometry (16 kHz mono float32, 160 samples per frame);
* canonical report/contract generation and newest-merge-base scope helpers.

Nothing here qualifies the candidate. The decision is DEFER, the evidence is
incomplete and the candidate is not qualified.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(TASK_DIR.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2]))).resolve()
TASK_BOARD_REL = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/streamvc-report/0.1"
CALLER_SCHEMA = "audio-sdk/streamvc/caller-supplied-asset/0.1"

TASK_ID = "SDK-STREAMVC"
TITLE = "StreamVC"
COMPONENT = "streamvc"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "14af17740bf8c571f9a985c88fd56f5b5b8e8ae8"
BRANCH = "swarm/SDK-STREAMVC"
REVIEWER = "reviewer-StreamVC"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-STREAMVC")
TASK_PREFIX = "docs/task-evidence/streamvc/"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_PERIOD_NS = 62500
MICRO_SCALE = 1000000
CONTROL_SAMPLES = 3200
PCM_SAMPLE_CAP = 10000000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

TASK_KIND = "streaming_voice_conversion"
VARIANT = "identity_control"
IDENTITY_TARGET = "identity_source"
CANDIDATE_TARGET = "streamvc_low_latency_conversion"
CALLER_VARIANT = "caller_supplied_external_asset"
ASSET_STORAGE = "external"

INVENTORY_JSON_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
INVENTORY_MD_PATH = "audio-benchmark-platform/plan/INVENTORY.md"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
AUDIO_SDK_README_PATH = "audio-benchmark-platform/plan/audio-sdk/README.md"
VC_CENSUS_PATH = "research/voice-conversion-eval-20261101/README.md"
ACCENT_RECORD_PATH = "research/accent-conversion-20261101/README.md"
CATEGORY_SOURCES_PATH = "research/category_survey/sources.md"
UPSTREAM_SOURCE_PATH = (
    "research/voice-conversion-eval-20261101/repos/streamvc-unofficial")
UPSTREAM_README_PATH = UPSTREAM_SOURCE_PATH + "/README.md"
UPSTREAM_LICENSE_PATH = UPSTREAM_SOURCE_PATH + "/LICENSE"
UPSTREAM_INFER_PATH = UPSTREAM_SOURCE_PATH + "/inference.py"
UPSTREAM_TRAIN_PATH = UPSTREAM_SOURCE_PATH + "/train.py"
UPSTREAM_PREPROCESS_PATH = UPSTREAM_SOURCE_PATH + "/preprocess_dataset.py"
UPSTREAM_REQ_INFER_PATH = UPSTREAM_SOURCE_PATH + "/requirements-inference.txt"
UPSTREAM_REQ_TRAIN_PATH = UPSTREAM_SOURCE_PATH + "/requirements-training.txt"
UPSTREAM_MODEL_PATH = UPSTREAM_SOURCE_PATH + "/streamvc/model.py"
UPSTREAM_REVISION = "a81ef600655d04976699ea6c4663ddc81d8692ba"
UPSTREAM_TREE = "2dcbdb56b106a4abd746f19dab0c3491490273bd"
UPSTREAM_LICENSE = "MIT"

MISSING_CHECKPOINT_PATH = UPSTREAM_SOURCE_PATH + "/checkpoints"
MISSING_WEIGHT_SETUP_PATH = UPSTREAM_SOURCE_PATH + "/weights_manifest.json"
MISSING_RESULT_PATH = "research/voice-conversion-eval-20261101/results/streamvc"
METRIC_SPEC_PATH = "data/references/streamvc/metric-spec.json"
LICENSE_RECORD_PATH = "data/rights/streamvc-license.json"
RIGHTS_RECORD_PATH = "data/rights/streamvc-rights.json"
TARGET_CONSENT_PATH = "data/rights/streamvc-target-reference-consent.json"
COHORT_MANIFEST_PATH = "data/runs/streamvc-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/streamvc-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/streamvc"
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
README_DIGEST_FILES: Tuple[str, ...] = (
    "LICENSES.md",
    "reference.py",
    "report.json",
    "run.py",
    "test_reference.py",
    "verify.py",
)
README_TABLE_START = "<!-- digest-table:start -->"
README_TABLE_END = "<!-- digest-table:end -->"
SOURCES_HEADER = (
    "# SHA-256 pins for SDK-STREAMVC.\n"
    "# source: paths are relative to SOURCE_ROOT; worktree: paths are\n"
    "# relative to the SDK checkout; pkg: paths are relative to this\n"
    "# task-evidence directory. The mutable full TASKS.json and any audio\n"
    "# are never hashed; only the linked-row stable identity is gated."
)

STABLE_TASK_FIELDS = ("id", "title", "mode", "repository", "component")
MUTABLE_TASK_FIELDS = (
    "status", "owner", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff",
    "blocked_reason", "dispatch_priority",
)

SOURCE_PINS: Dict[str, str] = {
    INVENTORY_JSON_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    INVENTORY_MD_PATH:
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    AUDIO_SDK_README_PATH:
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    VC_CENSUS_PATH:
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    ACCENT_RECORD_PATH:
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    CATEGORY_SOURCES_PATH:
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    UPSTREAM_README_PATH:
        "a19db11fa46b203bfa51aae0bb9b6f95c72756eef6c27e65886b8614598aaefd",
    UPSTREAM_LICENSE_PATH:
        "6a0a336a16a6d1a2916f7e86b44d305375b31fbd902300ca64a27f5c125460c3",
    UPSTREAM_INFER_PATH:
        "98c8d371701516a6f91e6ac1e95670320ae8be6f0c987d3b5abc37f814bb8c53",
    UPSTREAM_TRAIN_PATH:
        "84978b37c3e9a4d7c61847d89672f452d4b1194229958e8da8d7fdfe3f8c5325",
    UPSTREAM_PREPROCESS_PATH:
        "48c915349b8616ec185f89db2594d09ec8a15c30b7c8e0f27ea5a9f40d1fdeea",
    UPSTREAM_REQ_INFER_PATH:
        "486a64bb160cb7f11283145b281f6bea95839c008ea057176ca913f073bd5f30",
    UPSTREAM_REQ_TRAIN_PATH:
        "8d8b81a72718df74589bdd9f17d9c06950312ba71d7e31d1c92761abfd7d1401",
    UPSTREAM_MODEL_PATH:
        "3a78e96002c2f40081bf1d744009fe05300eb299e6899ab1a55d6090bd342466",
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
    "abi_changed": False,
    "public_c_boundary": "not used: no provider, header or installed target",
    "provider_registered": False,
    "provider_registration": False,
    "provider_intake_complete": False,
    "descriptor_registration": False,
    "descriptor_registry_change": False,
    "descriptor_default_changed": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "registry_changed": False,
    "shared_cmake_changed": False,
    "shared_build_or_ci_change": False,
    "ci_changed": False,
    "installed_v0_behavior_change": False,
    "board_or_handoff_changed": False,
    "asset_bundled": False,
    "weights_vendored": False,
    "runtime_bundled": False,
    "real_corpus_or_weights": False,
    "model_or_runtime_loaded": False,
    "real_audio_read": False,
    "listening_or_device_timing": False,
    "network_used": False,
    "benchmark_claim": False,
    "release_claim": False,
    "opt_in_required": True,
    "format": FORMAT,
}

SCOPE: Dict[str, Any] = {
    "write_scope": [TASK_PREFIX],
    "task_local_only": True,
    "shared_files_untouched": [
        "CMakeLists.txt", "CONTRACTS.md", "REUSE.toml",
        "api/include/audio_sdk/provider_v0.h",
        "api/include/audio_sdk/session_v0.h", "scripts/ci.py",
    ],
    "network_access": False,
    "downloads": False,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "mutations": [],
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "B1", "gate": "exact_task_scope_and_source_identity",
     "requirement": (
         "No trained StreamVC checkpoint exists in the available unofficial "
         "repository and paper-style streaming inference is not fully "
         "implemented. The S38 paper is a lead only; no official runnable "
         "streaming implementation is established by the pinned census.")},
    {"id": "B2", "gate": "exact_inference_checkpoint_and_weight_setup",
     "requirement": (
         "Byte-pinned StreamVC inference weights and a complete weight/setup "
         "manifest are absent. No immutable artifact revision, byte count or "
         "SHA-256 exists for any required checkpoint.")},
    {"id": "B3", "gate": "runtime_admission_and_package_lock",
     "requirement": (
         "An isolated, hash-pinned runtime and lockfile for the exact "
         "StreamVC setup are absent. The unofficial source checkout alone is "
         "not a runnable or qualified environment.")},
    {"id": "B4", "gate": "asset_rights_and_reference_consent",
     "requirement": (
         "Written checkpoint, training-data, reference-voice, target-voice, "
         "derivative-output and redistribution terms are not fully staged. "
         "The unofficial MIT source license is pinned, but no checkpoint or "
         "voice-rights record exists.")},
    {"id": "B5", "gate": "frozen_permitted_target_reference_and_groups",
     "requirement": (
         "No frozen, rights-cleared source/target cohort, speaker/language "
         "groups or exact reference prompts exist for StreamVC.")},
    {"id": "B6", "gate": "voice_outcomes_and_matched_evidence",
     "requirement": (
         "Separate content preservation, identity/similarity, target-voice "
         "realization and naturalness outcomes with matched baselines are not "
         "measured. No StreamVC conversion was executed.")},
    {"id": "B7", "gate": "alignment_timing_and_streaming",
     "requirement": (
         "Exact-runtime alignment, content delay, first-output/tail timing, "
         "memory, RTF and paced streaming behavior are absent. Paper-style "
         "streaming claims are not device measurements.")},
    {"id": "B8", "gate": "opt_in_adapter_and_release_gates",
     "requirement": (
         "No opt-in adapter intake, descriptor decision, authorized "
         "listening, bench validation, independent exact-head review or "
         "release approval has started.")},
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = tuple(
    (item["gate"], item["requirement"]) for item in EXACT_BLOCKERS)

VOICE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("permitted_input_and_target_references", (
        "Permitted source speech and target reference under the exact "
        "task condition."), "absent"),
    ("task_language_speaker_groups", (
        "Frozen task, language and speaker groups."), "absent"),
    ("text_and_semantic_content_preserved", (
        "Text and semantic content preserved as a separate outcome."),
     "not_measured"),
    ("identity_similarity", (
        "Identity/similarity preserved and scored separately."),
     "not_measured"),
    ("voice_conversion_target_realization", (
        "Target-voice realization scored against the exact target reference."),
     "not_measured"),
    ("naturalness", (
        "Naturalness scored separately by permitted listening or an "
        "approved predictive screen."), "not_measured"),
    ("alignment_first_output_and_tail_timing", (
        "Alignment, content delay, first-output and tail timing for the "
        "exact runtime."), "structural_only"),
    ("consent_reference_availability_and_output_use", (
        "Consent, reference availability and output-use gates."),
     "absent"),
)

ASSET_REQUIREMENTS: Tuple[Dict[str, str], ...] = (
    {"id": "A1", "name": "streamvc_checkpoint", "storage": "external",
     "status": "absent", "exact_path": MISSING_CHECKPOINT_PATH},
    {"id": "A2", "name": "complete_weight_setup", "storage": "external",
     "status": "absent", "exact_path": MISSING_WEIGHT_SETUP_PATH},
    {"id": "A3", "name": "runtime_environment", "storage": "external",
     "status": "absent", "exact_path": RUNTIME_ENV_PATH},
    {"id": "A4", "name": "source_license_record", "storage": "external",
     "status": "absent", "exact_path": LICENSE_RECORD_PATH},
    {"id": "A5", "name": "rights_record", "storage": "external",
     "status": "absent", "exact_path": RIGHTS_RECORD_PATH},
    {"id": "A6", "name": "target_reference_consent", "storage": "external",
     "status": "absent", "exact_path": TARGET_CONSENT_PATH},
    {"id": "A7", "name": "cohort_manifest", "storage": "external",
     "status": "absent", "exact_path": COHORT_MANIFEST_PATH},
    {"id": "A8", "name": "metric_specification", "storage": "external",
     "status": "absent", "exact_path": METRIC_SPEC_PATH},
)

CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "schema_id", "task_kind", "variant", "asset_storage",
    "source_checkout_path", "source_revision", "source_tree_sha256",
    "checkpoint_path", "checkpoint_sha256", "checkpoint_bytes",
    "weight_setup_manifest_path", "weight_setup_sha256",
    "weight_setup_bytes", "runtime_path", "runtime_lock_path",
    "source_license_record_path", "checkpoint_license_record_path",
    "rights_record_path", "target_reference_consent_path",
    "cohort_manifest_path", "target_reference_path",
    "target_reference_sha256", "target_reference_bytes",
    "metric_spec_path", "sample_rate_input_hz", "sample_rate_output_hz",
    "channels", "frame_samples", "comparison_baseline",
)

CALLER_FILE_PAIRS: Tuple[Tuple[str, Optional[str]], ...] = (
    ("checkpoint_path", "checkpoint_sha256"),
    ("weight_setup_manifest_path", "weight_setup_sha256"),
    ("runtime_lock_path", None),
    ("source_license_record_path", None),
    ("checkpoint_license_record_path", None),
    ("rights_record_path", None),
    ("target_reference_consent_path", None),
    ("cohort_manifest_path", None),
    ("target_reference_path", "target_reference_sha256"),
    ("metric_spec_path", None),
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "schema_id": CALLER_SCHEMA,
    "task_kind": TASK_KIND,
    "variant": CALLER_VARIANT,
    "asset_storage": ASSET_STORAGE,
    "required_fields": list(CALLER_ASSET_FIELDS),
    "requires_absolute_paths": True,
    "requires_byte_counts": True,
    "requires_sha256": True,
    "requires_40_hex_source_revision": True,
    "source_revision": UPSTREAM_REVISION,
    "source_tree_sha256": UPSTREAM_TREE,
    "source_license": UPSTREAM_LICENSE,
    "sample_rate_input_hz": SAMPLE_RATE_HZ,
    "sample_rate_output_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "comparison_baseline": IDENTITY_TARGET,
    "candidate_executed": False,
    "audio_read": False,
    "model_executed": False,
    "qualification_effect": "none",
    "note": (
        "A structurally valid caller manifest is an intake control only. It "
        "does not supply absent bytes, rights, consent, matched evidence or "
        "qualification. No provider file access, download or model load is "
        "permitted by CONTRACTS.md as_asset_v0."),
}

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "voice_census": VC_CENSUS_PATH,
    "voice_census_sha256": SOURCE_PINS[VC_CENSUS_PATH],
    "voice_census_line": 21,
    "streamvc_ledger_row": (
        "| StreamVC | Mobile streaming VC reference | repos/streamvc-unofficial "
        "| No trained checkpoint | Blocked | Upstream author states there is no "
        "trained checkpoint and the paper's streaming inference is not implemented. |"),
    "category_source_s38": CATEGORY_SOURCES_PATH,
    "category_source_s38_sha256": SOURCE_PINS[CATEGORY_SOURCES_PATH],
    "paper_lead": "https://arxiv.org/html/2401.03078v1",
    "upstream_repo": "https://github.com/yuval-reshef/StreamVC",
    "inventory_status": "blocked",
    "inventory_json_sha256": SOURCE_PINS[INVENTORY_JSON_PATH],
    "profile_source": VERIFICATION_PATH,
    "profile_source_sha256": SOURCE_PINS[VERIFICATION_PATH],
    "revisit_condition_from_census": (
        "Revisit when an official or verified runnable StreamVC checkpoint, "
        "complete weight setup and streaming inference path become available."),
}

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty", "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "pcm_bool",
    "pcm_out_of_range", "pcm_not_sequence", "request_not_object",
    "request_missing_field", "request_extra_field", "request_wrong_kind",
    "request_wrong_variant", "request_wrong_geometry",
    "request_unknown_target", "request_candidate_target",
    "request_nonidentity_baseline", "manifest_not_object",
    "manifest_missing_field", "manifest_extra_field",
    "manifest_relative_path", "manifest_bad_sha", "manifest_short_revision",
    "manifest_wrong_geometry", "manifest_placeholder_checkpoint",
    "manifest_wrong_storage", "manifest_wrong_task_kind",
    "manifest_missing_asset", "manifest_hash_mismatch",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No StreamVC conversion was executed.",
    "The pinned unofficial source checkout is source provenance only.",
    "No inference checkpoint, complete weight setup or runtime was downloaded, vendored or loaded.",
    "No source-reported StreamVC number is reused as a measured metric.",
    "No paper-style streaming claim is treated as a measured latency or timing result.",
    "This package does not read or write real audio.",
    "No consented cohort, licensed target reference or rights record was accepted.",
    "No listening panel, human rating or predictive quality score was run.",
    "No device, first-output, tail or streaming timing was measured.",
    "No SDK provider, descriptor, registry or default was changed.",
    "No public ABI, CONTRACTS.md, shared build or CI file was changed.",
    "No board, handoff, benchmark submission or release claim was made.",
)

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER_TOKENS = frozenset(
    ("unspecified", "unknown", "placeholder", "none", "default", "todo"))


class ReferenceRejection(ValueError):
    """Deterministic rejection that never mutates accepted state."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _check_canonical_value(value: Any, label: str) -> None:
    if isinstance(value, float):
        raise ReferenceRejection("noncanonical_float:" + label)
    if value is None or isinstance(value, bool) or isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_canonical_value(item, "%s[%d]" % (label, index))
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


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


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


def _read_git_head(repository: Path) -> Optional[str]:
    marker = repository / ".git"
    if not marker.exists():
        return None
    if marker.is_file():
        text = marker.read_text(encoding="utf-8").strip()
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
    head = head_path.read_text(encoding="utf-8").strip()
    if head.startswith("ref:"):
        ref_path = target / head.split(":", 1)[1].strip()
        if not ref_path.is_file():
            return None
        head = ref_path.read_text(encoding="utf-8").strip()
    return head if COMMIT_PATTERN.fullmatch(head) else None


ABSENCE_PROBES: Tuple[str, ...] = (
    MISSING_CHECKPOINT_PATH,
    MISSING_WEIGHT_SETUP_PATH,
    MISSING_RESULT_PATH,
    METRIC_SPEC_PATH,
    RIGHTS_RECORD_PATH,
    LICENSE_RECORD_PATH,
    TARGET_CONSENT_PATH,
    COHORT_MANIFEST_PATH,
    PARITY_MANIFEST_PATH,
    RUNTIME_ENV_PATH,
    RUNTIME_LOCK_PATH,
    TASK_PREFIX + "checkpoint",
    TASK_PREFIX + "converted",
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
    checkout = SOURCE_ROOT / UPSTREAM_SOURCE_PATH
    present = checkout.is_dir()
    revision = _read_git_head(checkout) if present else None
    tree_result = _git(checkout, "rev-parse", "HEAD^{tree}") if present else None
    tree = tree_result.stdout.strip() if tree_result is not None and (
        tree_result.returncode == 0) else None
    licenses = []
    if present:
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
            if (checkout / name).is_file():
                licenses.append(UPSTREAM_SOURCE_PATH + "/" + name)
    probes = probe_absence()
    return {
        "upstream_source_path": UPSTREAM_SOURCE_PATH,
        "source_checkout_present": present,
        "source_revision": revision,
        "source_revision_expected": UPSTREAM_REVISION,
        "source_revision_matches": revision == UPSTREAM_REVISION,
        "source_tree": tree,
        "source_tree_expected": UPSTREAM_TREE,
        "source_tree_matches": tree == UPSTREAM_TREE,
        "source_license": UPSTREAM_LICENSE,
        "source_license_paths": licenses,
        "source_license_confirmed": bool(licenses),
        "source_is_exact_inference_system": False,
        "source_runnable_not_demonstrated": True,
        "checkpoint_path": MISSING_CHECKPOINT_PATH,
        "checkpoint_present": (SOURCE_ROOT / MISSING_CHECKPOINT_PATH).exists(),
        "weight_setup_path": MISSING_WEIGHT_SETUP_PATH,
        "weight_setup_present": (
            SOURCE_ROOT / MISSING_WEIGHT_SETUP_PATH).is_file(),
        "target_reference_path": TARGET_CONSENT_PATH,
        "target_reference_present": False,
        "target_reference_rights_confirmed": False,
        "target_reference_read_by_package": False,
        "metric_spec_present": (SOURCE_ROOT / METRIC_SPEC_PATH).is_file(),
        "rights_record_present": (SOURCE_ROOT / RIGHTS_RECORD_PATH).is_file(),
        "license_record_present": (SOURCE_ROOT / LICENSE_RECORD_PATH).is_file(),
        "target_consent_present": (SOURCE_ROOT / TARGET_CONSENT_PATH).is_file(),
        "cohort_manifest_present": (
            SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file(),
        "parity_manifest_present": (
            SOURCE_ROOT / PARITY_MANIFEST_PATH).is_file(),
        "runtime_env_present": (SOURCE_ROOT / RUNTIME_ENV_PATH).is_dir(),
        "runtime_lock_present": (SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file(),
        "reference_audio_present": (
            SOURCE_ROOT / (TASK_PREFIX + "converted")).exists(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "task_kind": TASK_KIND,
            "comparison_baseline": IDENTITY_TARGET,
            "candidate_target": CANDIDATE_TARGET,
            "candidate_geometry_status": "unestablished",
                        "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
        },
    }


def task_row_identity() -> Dict[str, Any]:
    path = SOURCE_ROOT / TASK_BOARD_REL
    if not path.is_file():
        raise ReferenceRejection("task board is unavailable at " + TASK_BOARD_REL)
    document = require_json_object(load_strict_json(path))
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ReferenceRejection("expected exactly one linked task row")
    stable = {field: rows[0].get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK_ID or stable["component"] != COMPONENT:
        raise ReferenceRejection("linked task row identity mismatch")
    if stable["repository"] != REPOSITORY or stable["mode"] != MODE:
        raise ReferenceRejection("linked task row repository/mode mismatch")
    if stable["title"] != TITLE:
        raise ReferenceRejection("linked task row title mismatch")
    return {
        "source": TASK_BOARD_REL,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_text(stable).encode("utf-8")),
        "full_tasks_json_hashed": False,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "note": (
            "Only stable linked-row fields are read and gated. The mutable "
            "full plan/swarm/TASKS.json is never hashed or pinned."),
    }


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_source_pcm() -> List[float]:
    state = 20261126
    values: List[float] = []
    for index in range(CONTROL_SAMPLES):
        state, noise = _lcg(state)
        envelope = 0.25 if (index // 400) % 2 == 0 else 0.05
        value = envelope * math.sin(index * 0.07) + 0.01 * noise
        values.append(max(-1.0, min(1.0, value)))
    return values


def validate_pcm(values: Any) -> List[float]:
    if not isinstance(values, (list, tuple)):
        raise ReferenceRejection("pcm_not_sequence")
    if not values or len(values) > PCM_SAMPLE_CAP:
        raise ReferenceRejection("pcm_invalid_length")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("pcm_invalid_type")
        if not math.isfinite(value) or abs(value) > 1.0:
            raise ReferenceRejection("pcm_nonfinite_or_out_of_range")
    return list(values)


def identity_transform(values: Sequence[float]) -> List[float]:
    return list(validate_pcm(values))


def pcm_summary(values: Sequence[float]) -> Dict[str, Any]:
    valid = validate_pcm(values)
    micros = [int(round(value * MICRO_SCALE)) for value in valid]
    return {
        "samples": len(valid),
        "duration_ns": len(valid) * SAMPLE_PERIOD_NS,
        "peak_micro": max(abs(value) for value in micros),
        "micro_sha256": sha256_bytes(
            ",".join(str(value) for value in micros).encode("ascii")),
    }


REQUEST_FIELDS = frozenset((
    "task_kind", "variant", "comparison_baseline", "target",
    "sample_rate_hz", "channels", "frame_samples", "pcm",
))


def identity_request() -> Dict[str, Any]:
    return {
        "task_kind": TASK_KIND,
        "variant": VARIANT,
        "comparison_baseline": IDENTITY_TARGET,
        "target": IDENTITY_TARGET,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "pcm": synthetic_source_pcm(),
    }


def admit_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ReferenceRejection("request_not_object")
    if set(request) != REQUEST_FIELDS:
        raise ReferenceRejection("request_field_set_mismatch")
    if request["task_kind"] != TASK_KIND:
        raise ReferenceRejection("request_wrong_task_kind")
    if request["variant"] != VARIANT:
        raise ReferenceRejection("request_wrong_variant")
    if request["comparison_baseline"] != IDENTITY_TARGET:
        raise ReferenceRejection("request_nonidentity_baseline")
    for field, expected in (("sample_rate_hz", SAMPLE_RATE_HZ),
                            ("channels", CHANNELS),
                            ("frame_samples", FRAME_SAMPLES)):
        value = request[field]
        if isinstance(value, bool) or not isinstance(value, int) or value != expected:
            raise ReferenceRejection("unsupported_control_geometry:" + field)
    target = request["target"]
    if target == CANDIDATE_TARGET:
        raise ReferenceRejection("absent_streamvc_checkpoint")
    if target != IDENTITY_TARGET:
        raise ReferenceRejection("unknown_target")
    pcm = validate_pcm(request["pcm"])
    return {
        "accepted": True,
        "identity_control": True,
        "candidate_executed": False,
        "model_executed": False,
        "qualification_effect": "none",
        "samples": len(pcm),
    }


def _require_exact_field_set(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("manifest_not_object")
    if set(manifest) != set(CALLER_ASSET_FIELDS):
        raise ReferenceRejection("manifest_field_set_mismatch")
    return manifest


def _require_absolute_file(path_value: Any, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise ReferenceRejection("manifest_invalid_path:" + label)
    path = Path(path_value)
    if not path.is_absolute() or ".." in path.parts:
        raise ReferenceRejection("manifest_relative_path:" + label)
    if not path.is_file():
        raise ReferenceRejection("manifest_missing_asset:" + label)
    return path


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    value = _require_exact_field_set(manifest)
    if value["schema_id"] != CALLER_SCHEMA:
        raise ReferenceRejection("manifest_wrong_schema")
    if value["task_kind"] != TASK_KIND:
        raise ReferenceRejection("manifest_wrong_task_kind")
    if value["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("manifest_wrong_variant")
    if value["asset_storage"] != ASSET_STORAGE:
        raise ReferenceRejection("manifest_wrong_storage")
    if value["comparison_baseline"] != IDENTITY_TARGET:
        raise ReferenceRejection("manifest_wrong_baseline")
    revision = value["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise ReferenceRejection("manifest_bad_source_revision")
    source = value["source_checkout_path"]
    if not isinstance(source, str) or not Path(source).is_absolute():
        raise ReferenceRejection("manifest_relative_path:source_checkout_path")
    if not Path(source).is_dir():
        raise ReferenceRejection("manifest_missing_asset:source_checkout_path")
    tree_digest = value["source_tree_sha256"]
    if (not isinstance(tree_digest, str)
            or not SHA_PATTERN.fullmatch(tree_digest)):
        raise ReferenceRejection("manifest_bad_sha:source_tree_sha256")
    runtime = value["runtime_path"]
    if not isinstance(runtime, str) or not Path(runtime).is_absolute():
        raise ReferenceRejection("manifest_relative_path:runtime_path")
    if not Path(runtime).is_dir():
        raise ReferenceRejection("manifest_missing_asset:runtime_path")
    for field, expected in (("sample_rate_input_hz", SAMPLE_RATE_HZ),
                            ("sample_rate_output_hz", SAMPLE_RATE_HZ),
                            ("channels", CHANNELS),
                            ("frame_samples", FRAME_SAMPLES)):
        actual = value[field]
        if isinstance(actual, bool) or not isinstance(actual, int) or actual != expected:
            raise ReferenceRejection("manifest_wrong_geometry:" + field)
    for path_field, hash_field in CALLER_FILE_PAIRS:
        path = _require_absolute_file(value[path_field], path_field)
        if hash_field is not None:
            digest = value[hash_field]
            if not isinstance(digest, str) or not SHA_PATTERN.fullmatch(digest):
                raise ReferenceRejection("manifest_bad_sha:" + hash_field)
            if file_digest(path) != digest:
                raise ReferenceRejection("manifest_hash_mismatch:" + path_field)
    for byte_field in ("checkpoint_bytes", "weight_setup_bytes",
                       "target_reference_bytes"):
        count = value[byte_field]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ReferenceRejection("manifest_bad_byte_count:" + byte_field)
        if count > MAX_MANIFEST_BYTES:
            raise ReferenceRejection("manifest_byte_count_too_large:" + byte_field)
    if str(value["checkpoint_path"]).lower().endswith("unspecified"):
        raise ReferenceRejection("manifest_placeholder_checkpoint")
    return {
        "accepted": True,
        "files_checked": len(CALLER_FILE_PAIRS),
        "model_executed": False,
        "audio_read": False,
        "qualification_effect": "none",
    }


def synthetic_caller_manifest(root: Path) -> Dict[str, Any]:
    """Build a shape-only fixture; every path is caller-owned and synthetic."""
    root = Path(root)
    source = root / "source"
    runtime = root / "runtime"
    source.mkdir(exist_ok=True)
    runtime.mkdir(exist_ok=True)
    manifest: Dict[str, Any] = {
        "schema_id": CALLER_SCHEMA,
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
        "asset_storage": ASSET_STORAGE,
        "source_checkout_path": str(source),
        "source_revision": "a" * 40,
        "source_tree_sha256": "b" * 64,
        "runtime_path": str(runtime),
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "comparison_baseline": IDENTITY_TARGET,
        "checkpoint_bytes": 16,
        "weight_setup_bytes": 16,
        "target_reference_bytes": 16,
    }
    for path_field, hash_field in CALLER_FILE_PAIRS:
        path = root / (path_field + ".bin")
        path.write_bytes(("synthetic-" + path_field).encode("ascii"))
        manifest[path_field] = str(path)
        if hash_field is not None:
            manifest[hash_field] = file_digest(path)
    return manifest


def run_adverse_controls() -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    def reject(case: str, operation: Any, *arguments: Any) -> None:
        try:
            operation(*arguments)
        except ReferenceRejection as error:
            results.append({"case": case, "result": "rejected",
                            "reason": error.code})
        else:
            results.append({"case": case, "result": "accepted",
                            "reason": "guard_failed"})

    reject("pcm_empty", validate_pcm, [])
    reject("pcm_nan", validate_pcm, [0.0, float("nan")])
    reject("pcm_pos_inf", validate_pcm, [float("inf")])
    reject("pcm_neg_inf", validate_pcm, [float("-inf")])
    reject("pcm_bool", validate_pcm, [True])
    reject("pcm_out_of_range", validate_pcm, [1.5])
    reject("pcm_not_sequence", validate_pcm, b"\x00")
    reject("request_not_object", admit_request, [])
    for case, field, value in (
            ("request_missing_field", "pcm", None),
            ("request_extra_field", "extra", 1),
            ("request_wrong_kind", "task_kind", "other"),
            ("request_wrong_variant", "variant", "streaming"),
            ("request_wrong_geometry", "frame_samples", 320),
            ("request_unknown_target", "target", "magic"),
            ("request_candidate_target", "target", CANDIDATE_TARGET),
            ("request_nonidentity_baseline", "comparison_baseline", "other")):
        request = identity_request()
        if case == "request_missing_field":
            request.pop(field)
        else:
            request[field] = value
        reject(case, admit_request, request)
    with tempfile.TemporaryDirectory(prefix="streamvc-adverse-") as raw:
        root = Path(raw)
        base = synthetic_caller_manifest(root)
        reject("manifest_not_object", validate_caller_manifest, [])
        for case, field, value in (
                ("manifest_missing_field", "runtime_lock_path", None),
                ("manifest_extra_field", "extra", 1),
                ("manifest_relative_path", "checkpoint_path", "rel.bin"),
                ("manifest_bad_sha", "checkpoint_sha256", "0" * 64),
                ("manifest_short_revision", "source_revision", "abc"),
                ("manifest_wrong_geometry", "channels", 2),
                ("manifest_placeholder_checkpoint", "checkpoint_path",
                 "/tmp/unspecified"),
                ("manifest_wrong_storage", "asset_storage", "embedded"),
                ("manifest_wrong_task_kind", "task_kind", "other")):
            manifest = dict(base)
            if case == "manifest_missing_field":
                manifest.pop(field)
            else:
                manifest[field] = value
            reject(case, validate_caller_manifest, manifest)
        manifest = dict(base)
        (root / "checkpoint_path.bin").unlink()
        reject("manifest_missing_asset", validate_caller_manifest, manifest)
        manifest = dict(base)
        manifest["weight_setup_sha256"] = "0" * 64
        reject("manifest_hash_mismatch", validate_caller_manifest, manifest)
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = identity_transform(source)
    first = pcm_summary(source)
    second = pcm_summary(output)
    adverse = run_adverse_controls()
    return {
        "executor": "absent",
        "model_executed": False,
        "audio_read": False,
        "identity_baseline": {
            "sample_count_equal": first["samples"] == second["samples"],
            "duration_equal": first["duration_ns"] == second["duration_ns"],
            "digest_equal": first["micro_sha256"] == second["micro_sha256"],
            "peak_bounded": first["peak_micro"] <= MICRO_SCALE,
            "content_delay_samples": 0,
            "qualification_effect": "none",
            "summary": first,
        },
        "request_admission": {
            "identity_control_accepted": admit_request(
                identity_request())["accepted"],
            "candidate_smoother_used": False,
            "candidate_conversion_used": False,
            "rejected_targets": [
                {"target": CANDIDATE_TARGET, "reason": "absent_streamvc_checkpoint"},
            ],
        },
        "geometry": {
            "declared_control_geometry_only": True,
            "candidate_geometry_asserted": False,
            "candidate_geometry_status": "unestablished",
                        "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
        },
        "acceptance_outcomes": [
            {"id": item[0], "measured": False, "value": None}
            for item in VOICE_REQUIREMENTS
        ],
        "adverse": adverse,
        "adverse_all_rejected": all(
            item["result"] == "rejected" for item in adverse),
        "adverse_case_count": len(adverse),
    }


SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> Optional[str]:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> Optional[str]:
    """Newest merge-base of HEAD and an available PR base ref."""
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
        elif best != base and _git(worktree, "merge-base", "--is-ancestor",
                                   best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    assert_no_candidate_artifacts(audit["absence_probes"])
    if (not audit["source_revision_matches"]
            or not audit["source_tree_matches"]
            or audit["checkpoint_present"]
            or audit["weight_setup_present"]
            or audit["metric_spec_present"] or audit["rights_record_present"]
            or audit["license_record_present"]
            or audit["target_consent_present"]
            or audit["cohort_manifest_present"]
            or audit["parity_manifest_present"]
            or audit["runtime_env_present"] or audit["runtime_lock_present"]
            or audit["reference_audio_present"]):
        raise ReferenceRejection("candidate_artifact_or_source_drift")
    control = build_control()
    gates = [
        {"id": item["id"], "gate": item["gate"],
         "requirement": item["requirement"], "status": "blocked"}
        for item in EXACT_BLOCKERS
    ]
    profile_items = [
        {"id": item, "requirement": requirement, "package_status": status,
         "satisfied_for_qualification": False, "qualification_effect": "none"}
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
                "The unofficial StreamVC source is pinned, but no trained "
                "checkpoint or complete weight setup is available and paper-"
                "style streaming inference is not implemented. No conversion, "
                "timing or quality outcome was measured."),
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
        "readme_digest_files": list(README_DIGEST_FILES),
        "candidate": {
            "name": TITLE,
            "record_name": "StreamVC",
            "inventory_status": "blocked",
            "source_record": VC_CENSUS_PATH,
            "source_record_sha256": SOURCE_PINS[VC_CENSUS_PATH],
            "source_record_line": 21,
            "candidate_kind": "unofficial_source_checkpoint_blocked_streaming_vc",
            "source_revision": UPSTREAM_REVISION,
            "source_tree_sha256": UPSTREAM_TREE,
            "source_license": UPSTREAM_LICENSE,
            "source_present": audit["source_checkout_present"],
            "runtime_present": False,
            "weights_present": False,
            "checkpoint_present": False,
            "weight_setup_present": False,
            "target_reference_rights_confirmed": False,
            "geometry_documented": False,
            "implemented_here": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "evidence_status": "blocked",
            "finding": (
                "Official source checkout has example audio/code but no "
                "obtainable inference checkpoint or complete weight setup."),
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "licensing": {
            "package_license": "Apache-2.0",
            "upstream_source_license": UPSTREAM_LICENSE,
            "upstream_license_text_pinned": True,
            "checkpoint_terms_staged": False,
            "complete_weight_setup_terms_staged": False,
            "training_data_statement_staged": False,
            "target_reference_rights_provenance_confirmed": False,
            "reference_voice_consent_staged": False,
            "output_use_reviewed": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "review_status": "blocked",
        },
        "voice_profile": {
            "name": PROFILE,
            "source": VERIFICATION_PATH,
            "source_sha256": SOURCE_PINS[VERIFICATION_PATH],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "The Voice profile is applied as a gate ledger. Structural "
                "identity accounting passes, but the target reference rights "
                "are unconfirmed and no StreamVC runtime, consented cohort, "
                "matched voice evidence or timing measurement exists."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "identity_baseline_exact": control["identity_baseline"]["digest_equal"],
            "candidate_target_rejected_before_processing": True,
            "incomplete_manifest_rejected": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_case_count": control["adverse_case_count"],
            "adverse_all_rejected": control["adverse_all_rejected"],
        },
        "gates": gates,
        "release_gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "external_blocker": (
            "No trained StreamVC checkpoint exists in the pinned unofficial "
            "repository and paper-style streaming inference is not implemented. "
            "The S38 paper is a lead only; exact checkpoint, runtime, rights, "
            "cohort and matched evidence remain absent."),
        "reopen_condition": (
            "Admit implementation only after caller-owned immutable bytes and "
            "a 40-hex source revision plus tree digest pin the exact licensed "
            "StreamVC checkpoint and complete weight setup; written code, "
            "checkpoint, training-data, reference-voice consent, output-use "
            "and redistribution rights are cleared; a hash-pinned isolated "
            "runtime and requirements lock install and reproduce the exact "
            "upstream path; a rights-cleared cohort with frozen target "
            "references and metric specification exists; and separate content, "
            "identity, target-voice and naturalness outcomes plus alignment, "
            "timing, authorized listening, bench validation, independent "
            "exact-head review and release approval are complete. Until then "
            "the candidate stays DEFER, incomplete and not qualified."),
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_CHECKPOINT_PATH, MISSING_WEIGHT_SETUP_PATH,
            MISSING_RESULT_PATH, METRIC_SPEC_PATH, LICENSE_RECORD_PATH,
            RIGHTS_RECORD_PATH, TARGET_CONSENT_PATH, COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH, RUNTIME_ENV_PATH, RUNTIME_LOCK_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "Fixed workspace paths are probed for assets and rights records.",
            "The pinned StreamVC source checkout is not executed.",
            "No target reference is recorded or read by this package; "
            "not read or hashed by this package.",
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
    sidecar_digest = sha256_bytes((report_digest + "\n").encode("ascii"))
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
        "licensing": report["licensing"],
        "voice_profile": report["voice_profile"],
        "reference_protocol": report["reference_protocol"],
        "controls": {
            "identity_baseline_exact": report["controls"][
                "identity_baseline_exact"],
            "candidate_target_rejected_before_processing": report[
                "controls"]["candidate_target_rejected_before_processing"],
            "incomplete_manifest_rejected": report["controls"][
                "incomplete_manifest_rejected"],
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
        "external_blocker": report["external_blocker"],
        "reopen_condition": report["reopen_condition"],
        "reopen_conditions": report["reopen_conditions"],
        "negative_claims": report["non_claims"],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "readme_digest_files": list(README_DIGEST_FILES),
        "determinism": report["determinism"],
        "reproduction": {
            "cold_start_regenerations": 3,
            "generator": "run.py",
            "check_command": (
                "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check"),
            "verify_command": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no StreamVC checkpoint, complete weight setup, runtime or audio "
            "data is downloaded, copied, loaded or executed",
            "only the identity-source control is admitted; candidate "
            "conversion targets fail closed because the exact assets are absent",
            "a structurally valid caller manifest cannot qualify the candidate",
            "no candidate rate, frame, target-voice taxonomy, timing "
            "protocol or output geometry is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
            "the merge-base diff must contain no path outside TASK_PREFIX",
        ],
    }


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = SOURCES_HEADER.splitlines()
    for path, digest in sorted(SOURCE_PINS.items()):
        lines.append("%s  source:%s" % (digest, path))
    for path, digest in sorted(BOUNDARY_PINS.items()):
        lines.append("%s  worktree:%s" % (digest, path))
    for name in sorted(PIN_FILES):
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = TASK_DIR / name
            if not full.is_file():
                raise ReferenceRejection("missing_artifact:" + name)
            digest = file_digest(full)
        lines.append("%s  pkg:%s" % (digest, name))
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "ABSENCE_PROBES", "ADVERSE_CASE_IDS", "ARTIFACT_FILES", "BASE_COMMIT",
    "BOUNDARY", "BOUNDARY_PINS", "CALLER_ASSET_CONTRACT",
    "CALLER_ASSET_FIELDS", "CALLER_FILE_PAIRS", "CANDIDATE_TARGET", "DECISION",
    "EXACT_BLOCKERS", "GATE_REQUIREMENTS", "README_DIGEST_FILES",
    "README_TABLE_END", "README_TABLE_START", "SCOPE", "SCOPE_BASE_REFS",
    "SOURCE_PINS", "SOURCES_HEADER", "CANDIDATE_TARGET", "UPSTREAM_LICENSE",
    "UPSTREAM_REVISION", "UPSTREAM_TREE",
    "TASK_ID", "TASK_PREFIX", "VOICE_REQUIREMENTS", "ReferenceRejection",
    "admit_request", "artifact_pins", "assert_no_candidate_artifacts",
    "audit_assets", "build_contract", "build_control", "build_report",
    "canonical_report", "canonical_text", "file_digest", "git_commit",
    "identity_request", "identity_transform", "load_strict_json",
    "load_strict_json_text", "object_digest", "pcm_summary", "probe_absence",
    "run_adverse_controls", "scope_base", "scope_changed_paths",
    "scope_violations", "sha256_bytes", "sources_bytes",
    "synthetic_caller_manifest", "synthetic_source_pcm", "task_row_identity",
    "validate_caller_manifest", "validate_pcm",
]
