# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-ACCENTCL.

The exact licensed AccentCL source, its seven class checkpoints, the
Whisper-Large-v3 backbone and a hash-pinned runtime are all absent from this
workspace.  The merged accent-conversion research package records AccentCL as
"Not run" and does not publish an upstream revision, checkpoint filenames,
checkpoint digests or a runtime lock.

This module therefore never imports PyTorch, torchaudio, Transformers, NumPy,
SciPy, SoundFile or any model runtime, never loads or executes a model, never
reads or writes real audio, never downloads anything and never measures a
device clock.  It provides four verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths;
* a caller-supplied-asset manifest contract for the seven checkpoints,
  Whisper-Large-v3 backbone, runtime, rights records and cohort, validated
  without importing or executing anything;
* a deterministic synthetic seven-class classification accounting control
  that exercises label exactness, posterior validity, nonfinite rejection,
  normalization and deterministic argmax including ties;
* the canonical evidence report model.

Nothing in this package qualifies the candidate.  The decision is ``DEFER``.
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

TASK = "SDK-ACCENTCL"
TITLE = "AccentCL"
SLUG = "accentcl"
COMPONENT = "accentcl"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "8d7982e8eb101004e98f8079f1aeaadbe3981f20"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact upstream identity.  The source checkout is absent, so the revision is
# recorded as null rather than invented.  A full 40-hex string is required
# before a caller manifest can be considered for later review.
ACCENTCL_REPO_RELATIVE = "research/accent-conversion-20261101/repos/AccentCL"
ACCENTCL_REPO_URL = "https://github.com/PSI-TAMU/AccentCL"
ACCENTCL_COMMIT: Optional[str] = None
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

# Recorded task geometry.  AccentCL is a seven-class accent classifier that
# depends on a Whisper-Large-v3 backbone.  The merged evidence records only the
# class count and backbone family, not upstream class names or file names.
CLASS_COUNT = 7
WHISPER_MODEL_NAME = "Whisper-Large-v3"
INPUT_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
VARIANT = "offline_whole_utterance"

# Recorded approximate checkpoint size only.  It is not a byte pin.
CHECKPOINT_APPROX_MB_EACH = 2560  # "about 2.56 GB" from merged evidence

# Fixed workspace paths.  Absence is recorded, never filled.
RIGHTS_RECORD_PATH = "data/rights/accentcl-rights.json"
COHORT_MANIFEST_PATH = "data/runs/accentcl-accent-cohort/manifest.json"
LABEL_MAP_PATH = "data/accentcl/class-labels.json"
RUNTIME_ENV_PATH = "data/envs/accentcl"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
CHECKPOINT_DIR_PATH = "checkpoints/accentcl"
MISSING_CHECKPOINT_PATH = CHECKPOINT_DIR_PATH + "/"
RESEARCH_SAMPLE_PATH = "research/accent-conversion-20261101/data/l2accent"

MAX_MANIFEST_BYTES = 64 * 1024 ** 3

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
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/evaluate_accent_classifier.py":
        "6f4d3eeffbba628fd94e9fe85656bab1e78ecc9cfb83b9c2329e3981c6b40233",
    "research/accent-conversion-20261101/results/accent-classifier.json":
        "c1f2146f8b7a665bcb8e8cf42b14e2bd31e042d225653f467fef7f692e1d6d2b",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
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
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "classifier_input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
    "classifier_channels": CHANNELS,
    "classifier_input_sample_format": "f32",
    "classifier_class_count": CLASS_COUNT,
    "classifier_backbone": WHISPER_MODEL_NAME,
    "classifier_variant": VARIANT,
    "classifier_streaming": False,
    "classifier_output": "seven_class_posterior_and_argmax",
    "upstream_class_names_known": False,
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
    "real_accentcl_model": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No AccentCL checkpoint or Whisper-Large-v3 weight is loaded or executed.",
    "No PyTorch, torchaudio, Transformers, NumPy, SciPy, SoundFile or model runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, speaker reference or consent record is consumed.",
    "No accent-class accuracy, posterior, calibration, listening, latency, memory or RTF is measured here.",
    "The merged research finding is provenance only and is not reproduced or rescored.",
    "The synthetic seven-class accounting control is a contract control, never model output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "accentcl_source_checkout",
        "repository": ACCENTCL_REPO_URL,
        "revision": None,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No checkout exists under research/accent-conversion-20261101/"
            "repos/AccentCL and no upstream commit is published in the "
            "merged evidence."),
    },
    {
        "id": "seven_class_checkpoints",
        "count": CLASS_COUNT,
        "recorded_size_approx_mb_each": CHECKPOINT_APPROX_MB_EACH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "Exact upstream filenames, URLs and byte digests are unavailable; "
            "only the approximate per-checkpoint size is recorded."),
    },
    {
        "id": "whisper_large_v3_backbone",
        "model": WHISPER_MODEL_NAME,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "The backbone weights, configuration and immutable distribution "
            "revision are absent and unpublished."),
    },
    {
        "id": "exact_runtime",
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No isolated AccentCL environment or lock exists.  The research "
            "host recorded Python 3.11.5, but AccentCL was never run there."),
    },
    {
        "id": "source_license_record",
        "required": True,
        "status": "absent",
        "note": "No upstream licence file or licence review is available.",
    },
    {
        "id": "rights_and_consent_record",
        "path": RIGHTS_RECORD_PATH,
        "required": True,
        "status": "absent",
        "note": (
            "Weight, training-data, speaker-reference, consent, output-use "
            "and redistribution rights are unresolved."),
    },
    {
        "id": "accent_cohort_and_labels",
        "path": COHORT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
        "note": (
            "No rights-cleared accent cohort, class ground truth, language or "
            "speaker grouping exists; only three unused research clips exist."),
    },
    {
        "id": "class_label_map",
        "path": LABEL_MAP_PATH,
        "required": True,
        "status": "absent",
        "note": (
            "The upstream seven class names, ordering and index mapping are "
            "not published in the merged evidence and are not invented here."),
    },
)

CALLER_ASSET_FIELDS = (
    "source_revision",
    "variant",
    "sample_rate_input_hz",
    "channels",
    "class_count",
    "whisper_model",
    "checkpoint_paths",
    "checkpoint_sha256s",
    "whisper_weights_path",
    "whisper_weights_sha256",
    "whisper_config_path",
    "whisper_config_sha256",
    "label_map_path",
    "label_map_sha256",
    "runtime_path",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "license_record_path",
    "license_record_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
)

CALLER_FILE_PAIRS = (
    ("whisper_weights_path", "whisper_weights_sha256"),
    ("whisper_config_path", "whisper_config_sha256"),
    ("label_map_path", "label_map_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("consent_record_path", "consent_record_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/accentcl/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_geometry_and_offline_variant_only;"
        "_do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": VARIANT,
    "required_source_revision": ACCENTCL_COMMIT,
    "revision_policy": (
        "A caller must supply a full 40-hex upstream commit, but no upstream "
        "commit has been observed or approved.  Structural acceptance never "
        "sets revision_pinned or qualification."),
    "required_geometry": {
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "class_count": CLASS_COUNT,
    },
    "required_whisper_model": WHISPER_MODEL_NAME,
    "checkpoint_count": CLASS_COUNT,
    "notes": (
        "All seven class checkpoints, the Whisper-Large-v3 weights and config, "
        "label map, runtime lock, licence, consent and cohort record must exist "
        "at absolute paths and match their declared SHA-256 before a caller may "
        "process audio.  The validator never imports the source or a runtime."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_checkout_absent",
        "state": "absent",
        "requirement": (
            "Supply a checkout of PSI-TAMU/AccentCL at one full 40-hex upstream "
            "commit; no AccentCL checkout exists in the workspace or this "
            "worktree and the merged evidence publishes no revision."),
    },
    {
        "id": "seven_checkpoint_digests_unpublished",
        "state": "absent",
        "requirement": (
            "Publish exact filenames, byte counts and SHA-256 values for all "
            "seven accent-class checkpoints; the merged evidence records only "
            "approximately 2.56 GB per checkpoint."),
    },
    {
        "id": "whisper_large_v3_absent",
        "state": "absent",
        "requirement": (
            "Supply the Whisper-Large-v3 backbone weights and configuration "
            "with exact byte counts, SHA-256 values and an immutable "
            "distribution revision."),
    },
    {
        "id": "runtime_unpinned_and_absent",
        "state": "absent",
        "requirement": (
            "Provide a hash-pinned isolated AccentCL runtime with a complete "
            "lock at data/envs/accentcl/requirements.lock on a recorded "
            "platform; no AccentCL environment was ever created."),
    },
    {
        "id": "source_license_absent",
        "state": "absent",
        "requirement": (
            "Add and review the upstream source and weight licence; no "
            "AccentCL licence file, model card terms or redistribution grant "
            "has been observed."),
    },
    {
        "id": "rights_and_consent_uncleared",
        "state": "absent",
        "requirement": (
            "Clear weight, training-data, speech-corpus, speaker-reference, "
            "consent, output-use and redistribution rights with complete "
            "notices."),
    },
    {
        "id": "accent_cohort_and_labels_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared accent cohort with exact class labels, "
            "class ordering, language and speaker groups, and held-out ground "
            "truth; no label map or cohort manifest exists."),
    },
    {
        "id": "approved_reference_parity_absent",
        "state": "absent",
        "requirement": (
            "Produce an approved exact-runtime AccentCL parity vector on frozen "
            "16 kHz mono PCM for one frozen checkpoint set, including the "
            "seven-class posterior, argmax and fresh-process reset."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex AccentCL revision, seven checkpoint SHA-256 values, "
        "Whisper-Large-v3 manifest, label map and source licence match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform.",
    ),
    (
        "artifact_rights_and_consent",
        "Source, weight, training-data, speech-corpus, consent, output-use and "
        "redistribution rights are cleared with complete notices.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime seven-class posterior and argmax match the "
        "reference on frozen 16 kHz mono PCM for one frozen checkpoint set.",
    ),
    (
        "accent_cohort_and_scoring",
        "A rights-cleared held-out cohort scores accuracy, macro-F1, "
        "calibration and per-class confusion with frozen language and speaker "
        "groups.",
    ),
    (
        "offline_classification_separation",
        "The offline whole-utterance classifier is reproduced and never "
        "presented as incremental streaming; first-output and tail timing are "
        "measured if an adapter is ever proposed.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in adapter intake, licence review, descriptor review and "
        "an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

VOICE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "permitted_source_and_target_references",
        "Freeze permitted input and target references with rights and consent.",
        "absent",
    ),
    (
        "task_language_and_speaker_groups",
        "Freeze task, language and speaker groups for the cohort.",
        "absent",
    ),
    (
        "text_and_semantic_preservation",
        "Preserve text and semantic content as its own outcome.",
        "not_measured",
    ),
    (
        "identity_similarity",
        "Measure identity or similarity to the target as a separate outcome.",
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
        "Treat consent, reference availability and output use as independent gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": "research/accent-conversion-20261101/README.md",
    "source_sha256": SOURCE_PINS[
        "research/accent-conversion-20261101/README.md"],
    "candidate": "AccentCL",
    "official_repository": ACCENTCL_REPO_URL,
    "reported_status": "Not run",
    "reported_class_count": CLASS_COUNT,
    "reported_checkpoint_size_approx_gb_each": 2.56,
    "reported_backbone": WHISPER_MODEL_NAME,
    "reported_host": "Apple M1 Mac, 8 GB RAM, Python 3.11.5",
    "reported_reason": (
        "Not practical to download and run on this 8 GB / low-free-disk host."),
    "notes": (
        "The merged research package never downloaded, loaded or executed "
        "AccentCL.  No accuracy, posterior, calibration, listening, latency, "
        "memory or RTF result exists for AccentCL in that evidence."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_seven_class_classification_accounting_control"
    "_not_model_output")

# Synthetic placeholder labels.  They are deliberately not upstream accents.
SYNTHETIC_LABELS: Tuple[str, ...] = tuple(
    f"synthetic_class_{index}" for index in range(CLASS_COUNT))
SYNTHETIC_WEIGHTS: Tuple[int, ...] = (295, 145, 120, 110, 105, 115, 110)
TIE_WEIGHTS: Tuple[int, ...] = (500, 500, 0, 0, 0, 0, 0)

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "scores_empty",
    "scores_not_sequence",
    "scores_none",
    "scores_six",
    "scores_eight",
    "scores_nan",
    "scores_pos_inf",
    "scores_neg_inf",
    "scores_above_one",
    "scores_negative",
    "scores_bool",
    "scores_string",
    "scores_sum_not_one",
    "labels_six",
    "labels_eight",
    "labels_empty",
    "labels_empty_string",
    "labels_duplicate",
    "labels_non_ascii",
    "labels_non_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_wrong_revision",
    "manifest_wrong_class_count",
    "manifest_wrong_whisper_model",
    "manifest_wrong_variant",
    "manifest_wrong_rate",
    "manifest_missing_asset",
    "manifest_duplicate_checkpoint",
)


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


# ---------------------------------------------------------------------------
# Source checkout and asset audit.  Fixed local reads only; no network.
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
                 "COPYING.md", "COPYING.txt"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _checkpoint_files() -> List[str]:
    directory = SOURCE_ROOT / CHECKPOINT_DIR_PATH
    if not directory.is_dir():
        return []
    allowed = (".pt", ".pth", ".ckpt", ".bin", ".safetensors")
    return sorted(path.name for path in directory.iterdir()
                  if path.is_file() and path.suffix.lower() in allowed)


def _whisper_cache_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "research/accent-conversion-20261101/hf-cache/hub"
        / "models--openai--whisper-large-v3",
        SOURCE_ROOT / "research/accent-conversion-20261101/hf-cache"
        / "models--openai--whisper-large-v3",
        SOURCE_ROOT / "data/models/whisper-large-v3",
    ]


def _research_clip_count() -> int:
    directory = SOURCE_ROOT / RESEARCH_SAMPLE_PATH
    if not directory.is_dir():
        return 0
    return len([path for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() == ".wav"])


def audit_assets() -> Dict[str, Any]:
    repository = SOURCE_ROOT / ACCENTCL_REPO_RELATIVE
    revision = _read_git_head(repository) if repository.is_dir() else None
    licenses = _license_candidates(repository)
    readme = repository / "README.md"
    readme_declares = False
    if readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        readme_declares = ("license" in text or "licence" in text
                           or "copyright" in text)
    checkpoint_files = _checkpoint_files()
    return {
        "source_checkout_path": ACCENTCL_REPO_RELATIVE,
        "source_checkout_present": repository.is_dir(),
        "source_revision": revision,
        "source_revision_pinned": (
            revision is not None and revision == ACCENTCL_COMMIT),
        "source_file_pins_defined": False,
        "source_files_checked": 0,
        "source_file_pins_match": False,
        "source_file_mismatches": [],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "checkpoint_dir_present": (SOURCE_ROOT / CHECKPOINT_DIR_PATH).is_dir(),
        "checkpoint_files_found": checkpoint_files,
        "checkpoint_file_count": len(checkpoint_files),
        "all_checkpoints_present": len(checkpoint_files) >= CLASS_COUNT,
        "whisper_cache_present": any(
            path.exists() for path in _whisper_cache_candidates()),
        "runtime_env_present": (SOURCE_ROOT / RUNTIME_ENV_PATH).is_dir(),
        "runtime_lock_present": (SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file(),
        "rights_record_present": (SOURCE_ROOT / RIGHTS_RECORD_PATH).is_file(),
        "cohort_manifest_present": (
            SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file(),
        "label_map_present": (SOURCE_ROOT / LABEL_MAP_PATH).is_file(),
        "research_demo_audio_clip_count": _research_clip_count(),
        "requested_config": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "class_count": CLASS_COUNT,
            "backbone": WHISPER_MODEL_NAME,
            "variant": VARIANT,
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
# Deterministic synthetic seven-class classification accounting.
# ---------------------------------------------------------------------------

def synthetic_scores() -> List[float]:
    return [weight / 1000.0 for weight in SYNTHETIC_WEIGHTS]


def tie_scores() -> List[float]:
    return [weight / 1000.0 for weight in TIE_WEIGHTS]


def validate_label_set(labels: Any) -> List[str]:
    if not isinstance(labels, (list, tuple)):
        raise Reject("labels must be a sequence")
    if len(labels) != CLASS_COUNT:
        raise Reject("labels must contain exactly seven entries")
    checked: List[str] = []
    for index, label in enumerate(labels):
        if not isinstance(label, str):
            raise Reject(f"label {index} is not a string")
        if not label or not label.strip():
            raise Reject(f"label {index} is empty")
        if not label.isascii():
            raise Reject(f"label {index} is not ASCII")
        if label in checked:
            raise Reject(f"label {index} is a duplicate")
        checked.append(label)
    return checked


def label_map_digest(labels: Any) -> str:
    return sha256(canonical_bytes(validate_label_set(labels)))


def validate_class_scores(scores: Any,
                          require_normalized: bool = True) -> List[float]:
    if not isinstance(scores, (list, tuple)):
        raise Reject("scores must be a sequence")
    if len(scores) != CLASS_COUNT:
        raise Reject("scores must contain exactly seven values")
    checked: List[float] = []
    for index, score in enumerate(scores):
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise Reject(f"score {index} is not numeric")
        value = float(score)
        if not math.isfinite(value):
            raise Reject(f"score {index} is not finite")
        if value < 0.0 or value > 1.0:
            raise Reject(f"score {index} is outside [0, 1]")
        checked.append(value)
    if require_normalized:
        total = math.fsum(checked)
        if abs(total - 1.0) > 1e-9:
            raise Reject("scores do not sum to one")
    return checked


def argmax_index(scores: Any) -> int:
    checked = validate_class_scores(scores)
    best_index = 0
    best_value = checked[0]
    for index, value in enumerate(checked[1:], start=1):
        if value > best_value:
            best_index = index
            best_value = value
    return best_index


def classification_record(scores: Any,
                          labels: Sequence[str] = SYNTHETIC_LABELS
                          ) -> Dict[str, Any]:
    checked = validate_class_scores(scores)
    checked_labels = validate_label_set(labels)
    ordered = sorted(checked, reverse=True)
    top = ordered[0]
    second = ordered[1]
    index = argmax_index(checked)
    ties = [position for position, value in enumerate(checked)
            if value == top]
    return {
        "class_index": index,
        "class_label": checked_labels[index],
        "top_score": f"{top:.6f}",
        "second_score": f"{second:.6f}",
        "margin": f"{top - second:.6f}",
        "tie": len(ties) > 1,
        "tie_indices": ties,
        "tie_rule": "lowest_index_wins",
        "posterior_sha256": sha256(canonical_bytes(
            [f"{value:.6f}" for value in checked])),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_scores = synthetic_scores()
    good_labels = list(SYNTHETIC_LABELS)
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

    duplicate_checkpoints = list(good_manifest["checkpoint_paths"])
    duplicate_checkpoints[1] = duplicate_checkpoints[0]

    cases = [
        ("scores_empty", lambda: validate_class_scores([])),
        ("scores_not_sequence", lambda: validate_class_scores(b"1234567")),
        ("scores_none", lambda: validate_class_scores(None)),
        ("scores_six", lambda: validate_class_scores(good_scores[:6])),
        ("scores_eight", lambda: validate_class_scores(good_scores + [0.0])),
        ("scores_nan", lambda: validate_class_scores(
            [0.5, 0.5, math.nan, 0.0, 0.0, 0.0, 0.0])),
        ("scores_pos_inf", lambda: validate_class_scores(
            [0.5, 0.5, math.inf, 0.0, 0.0, 0.0, 0.0])),
        ("scores_neg_inf", lambda: validate_class_scores(
            [0.5, 0.5, -math.inf, 0.0, 0.0, 0.0, 0.0])),
        ("scores_above_one", lambda: validate_class_scores(
            [0.5, 0.5, 1.5, 0.0, 0.0, 0.0, 0.0])),
        ("scores_negative", lambda: validate_class_scores(
            [0.5, 0.5, -0.5, 0.5, 0.0, 0.0, 0.0])),
        ("scores_bool", lambda: validate_class_scores(
            [0.5, 0.5, True, 0.0, 0.0, 0.0, 0.0])),
        ("scores_string", lambda: validate_class_scores(
            [0.5, 0.5, "0.0", 0.0, 0.0, 0.0, 0.0])),
        ("scores_sum_not_one", lambda: validate_class_scores(
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])),
        ("labels_six", lambda: validate_label_set(good_labels[:6])),
        ("labels_eight", lambda: validate_label_set(good_labels + ["x"])),
        ("labels_empty", lambda: validate_label_set([])),
        ("labels_empty_string", lambda: validate_label_set(
            ["a", "b", "c", "d", "e", "f", ""])),
        ("labels_duplicate", lambda: validate_label_set(
            ["a", "a", "b", "c", "d", "e", "f"])),
        ("labels_non_ascii", lambda: validate_label_set(
            ["a", "b", "c", "d", "e", "f", "class\u00e9"])),
        ("labels_non_string", lambda: validate_label_set(
            ["a", "b", "c", "d", "e", "f", 7])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("cohort_manifest_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "whisper_weights_path", "weights/whisper.bin")),
        ("manifest_bad_sha", wrong("whisper_weights_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "abcdef")),
        ("manifest_wrong_revision", wrong("source_revision", "A" * 40)),
        ("manifest_wrong_class_count", wrong("class_count", 6)),
        ("manifest_wrong_whisper_model", wrong(
            "whisper_model", "whisper-tiny")),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_wrong_rate", wrong("sample_rate_input_hz", 22050)),
        ("manifest_missing_asset", wrong(
            "whisper_weights_path",
            "/nonexistent/accentcl-evidence-fixture/whisper-weights.bin")),
        ("manifest_duplicate_checkpoint", wrong(
            "checkpoint_paths", duplicate_checkpoints)),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It only exercises fail-closed shape checks.  Validation reaches the
    missing-asset branch before any file is read.
    """

    root = "/nonexistent/accentcl-evidence-fixture"
    digest = "0" * 64
    checkpoint_paths = [f"{root}/class-{index}.pt"
                        for index in range(CLASS_COUNT)]
    return {
        "source_revision": "a" * 40,
        "variant": VARIANT,
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "class_count": CLASS_COUNT,
        "whisper_model": WHISPER_MODEL_NAME,
        "checkpoint_paths": checkpoint_paths,
        "checkpoint_sha256s": [digest] * CLASS_COUNT,
        "whisper_weights_path": root + "/whisper-large-v3.bin",
        "whisper_weights_sha256": digest,
        "whisper_config_path": root + "/whisper-config.json",
        "whisper_config_sha256": digest,
        "label_map_path": root + "/class-labels.json",
        "label_map_sha256": digest,
        "runtime_path": root + "/runtime",
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "consent_record_path": root + "/consent.json",
        "consent_record_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
    }


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


def _absolute_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise Reject("manifest " + field + " must be a path string")
    path = Path(value)
    if not path.is_absolute():
        raise Reject("manifest " + field + " must be absolute")
    return path


def _sha_value(value: Any, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise Reject("manifest " + field + " is not a lowercase SHA-256")
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

    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    if manifest["variant"] != VARIANT:
        raise Reject("manifest variant must be " + VARIANT)
    if manifest["whisper_model"] != WHISPER_MODEL_NAME:
        raise Reject("manifest whisper_model must be " + WHISPER_MODEL_NAME)
    for field, expected_value in (
            ("sample_rate_input_hz", INPUT_SAMPLE_RATE_HZ),
            ("channels", CHANNELS),
            ("class_count", CLASS_COUNT)):
        value = manifest[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("manifest " + field + " must be an integer")
        if value != expected_value:
            raise Reject("manifest " + field + " mismatch")

    checkpoint_paths = manifest["checkpoint_paths"]
    checkpoint_shas = manifest["checkpoint_sha256s"]
    if not isinstance(checkpoint_paths, list) or not isinstance(
            checkpoint_shas, list):
        raise Reject("manifest checkpoint lists must be arrays")
    if len(checkpoint_paths) != CLASS_COUNT or len(checkpoint_shas) != (
            CLASS_COUNT):
        raise Reject("manifest must list exactly seven checkpoints")
    resolved_checkpoints: List[Path] = []
    for index, (path_value, sha_value) in enumerate(
            zip(checkpoint_paths, checkpoint_shas)):
        path = _absolute_path(path_value, f"checkpoint_paths[{index}]")
        _sha_value(sha_value, f"checkpoint_sha256s[{index}]")
        resolved_checkpoints.append(path)
    if len(set(str(path) for path in resolved_checkpoints)) != CLASS_COUNT:
        raise Reject("manifest checkpoint_paths must be unique")

    for sha_field in CALLER_SHA_FIELDS:
        _sha_value(manifest[sha_field], sha_field)
    file_paths: List[Tuple[str, Path]] = []
    for path_field, sha_field in CALLER_FILE_PAIRS:
        file_paths.append(
            (path_field, _absolute_path(manifest[path_field], path_field)))
    runtime_path = _absolute_path(manifest["runtime_path"], "runtime_path")

    for field, path in file_paths:
        if not path.is_file():
            raise Reject("manifest " + field + " file is missing")
    for path in resolved_checkpoints:
        if not path.is_file():
            raise Reject("manifest checkpoint file is missing")
    if not runtime_path.is_dir():
        raise Reject("manifest runtime_path directory is missing")

    total_bytes = 0
    for index, (path, declared) in enumerate(
            zip(resolved_checkpoints, checkpoint_shas)):
        if _hash_file(path) != declared:
            raise Reject(f"manifest checkpoint_sha256s[{index}] mismatch")
        total_bytes += path.stat().st_size
    for path_field, path in file_paths:
        if _hash_file(path) != manifest[
                path_field.replace("_path", "_sha256")]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size

    return {
        "accepted": True,
        "accepted_for_qualification": False,
        "source_revision": revision,
        "revision_pinned": False,
        "variant": VARIANT,
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "class_count": CLASS_COUNT,
        "whisper_model": WHISPER_MODEL_NAME,
        "checkpoints_checked": CLASS_COUNT,
        "files_checked": len(file_paths),
        "directories_checked": 1,
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "qualification_effect": "none",
    }


def build_control() -> Dict[str, Any]:
    labels = list(SYNTHETIC_LABELS)
    scores = synthetic_scores()
    record = classification_record(scores, labels)
    tie_record = classification_record(tie_scores(), labels)
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "class_count": CLASS_COUNT,
        "variant": VARIANT,
        "geometry": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "class_count": CLASS_COUNT,
            "backbone": WHISPER_MODEL_NAME,
            "mode": VARIANT,
            "incremental_streaming": False,
        },
        "synthetic_label_set": labels,
        "synthetic_label_set_is_placeholder": True,
        "upstream_label_names_available": False,
        "synthetic_scores": [f"{value:.3f}" for value in scores],
        "scores_sha256": sha256(canonical_bytes(
            [f"{value:.3f}" for value in scores])),
        "classification": record,
        "tie_control": tie_record,
        "acceptance_outcomes": [
            {
                "id": "accent_class_posterior",
                "measured": False,
                "value": None,
                "reason": "no checkpoint, backbone runtime or cohort",
            },
            {
                "id": "text_and_semantic_preservation",
                "measured": False,
                "value": None,
                "reason": "classifier path produces no converted speech",
            },
            {
                "id": "identity_similarity",
                "measured": False,
                "value": None,
                "reason": "no speaker reference, embedder runtime or consent",
            },
            {
                "id": "naturalness",
                "measured": False,
                "value": None,
                "reason": "no generated audio and no authorized listener panel",
            },
            {
                "id": "calibration_and_threshold",
                "measured": False,
                "value": None,
                "reason": "no held-out labeled cohort or frozen operating point",
            },
            {
                "id": "alignment_and_output_timing",
                "measured": False,
                "value": None,
                "reason": "structural offline statement only; no device clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "scores_nan", "scores_pos_inf", "scores_neg_inf"],
            "invalid_rejected": [
                "scores_above_one", "scores_negative", "scores_bool",
                "scores_string", "scores_sum_not_one", "labels_non_ascii",
                "labels_non_string"],
            "missing_rejected": [
                "scores_empty", "scores_none", "scores_not_sequence",
                "labels_empty", "manifest_missing_field",
                "manifest_missing_asset"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic seven-class accounting control only.  The label names "
            "are placeholders, the scores are hand-written weights and no "
            "AccentCL or Whisper runtime exists.  This is not model output, "
            "not a classification accuracy or calibration result and cannot "
            "qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision_pinned"]
        and observed["license_file_present"]
        and observed["all_checkpoints_present"]
        and observed["whisper_cache_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["label_map_present"])
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
        "source_revision_pinned": observed["source_revision_pinned"],
        "license_present": observed["license_file_present"],
        "all_checkpoints_present": observed["all_checkpoints_present"],
        "whisper_cache_present": observed["whisper_cache_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "label_map_present": observed["label_map_present"],
        "checkpoint_file_count": observed["checkpoint_file_count"],
        "research_demo_audio_clip_count": observed[
            "research_demo_audio_clip_count"],
        "observed": observed,
        "note": (
            "A source checkout, checkpoint or runtime appearing does not "
            "publish a digest, a licence, a rights record, a cohort or a "
            "parity vector.  Presence never qualifies the candidate."),
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
                "No AccentCL source checkout, seven class checkpoints, "
                "Whisper-Large-v3 backbone, hash-pinned runtime, licence, "
                "rights record, label map, accent cohort or approved parity "
                "vector exists.  The merged research package never ran the "
                "model."),
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
        "source_checkout": {
            "path": ACCENTCL_REPO_RELATIVE,
            "repository": ACCENTCL_REPO_URL,
            "revision": ACCENTCL_COMMIT,
            "revision_pinned": False,
            "class_count": CLASS_COUNT,
            "backbone": WHISPER_MODEL_NAME,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "voice_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "applicable_outcome": (
                "seven-class accent posterior and argmax; no speech is "
                "converted or synthesized"),
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural accounting passes, but no real model, licensed "
                "reference set, consent record, rights-cleared cohort, target "
                "runtime or approved parity exists, so the voice profile is "
                "not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_classification_separation_declared": True,
            "upstream_label_names_not_invented": True,
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
            MISSING_CHECKPOINT_PATH,
            RUNTIME_LOCK_PATH,
            LABEL_MAP_PATH,
            COHORT_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "No network request, download, audio device, model load or timing run occurs.",
            "The synthetic label set is an explicit placeholder, not upstream class names.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }
