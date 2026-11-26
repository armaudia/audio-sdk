# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-PCEN-FEATURE-FRONTEND.

PCEN (Per-Channel Energy Normalization) is a feature frontend described in
Wang et al., "Trainable Frontend For Robust and Far-Field Keyword Spotting"
(ICASSP 2017). Merged inventory/research evidence records this component as
considered/catalogued only: no exact licensed reference implementation,
pinned revision, trained/runtime assets, rights record, detection/keyword
cohort, or parity vector is present in this workspace.

This module never imports ML/audio runtimes, never downloads assets, never
reads or writes real audio, never invokes devices, and never measures timing.
It provides: fail-closed absence audit over fixed workspace paths; stable
linked-row TASKS identity projection (never hashing full TASKS.json); a
caller-supplied asset manifest contract validated without execution; and a
deterministic synthetic PCEN-shape accounting control that validates finite
inputs, exact frame accounting, and declared parameter bounds without claiming
model/reference parity or any qualifying result.

Nothing in this package qualifies the candidate. Decision is DEFER.
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

TASK = "SDK-PCEN-FEATURE-FRONTEND"
TITLE = "PCEN feature frontend"
COMPONENT = "pcen-feature-frontend"
TASK_PREFIX = f"docs/task-evidence/{COMPONENT}/"
BASE_COMMIT = "180e2bcd29430280f939f229ab0af2171a57e69f"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = "audio-sdk/task-evidence/pcen-feature-frontend/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

UPSTREAM_NAME = "PCEN (Per-Channel Energy Normalization)"
UPSTREAM_PAPER_URL = "https://research.google/pubs/trainable-frontend-for-robust-and-far-field-keyword-spotting/"
UPSTREAM_PAPER_TITLE = "Trainable Frontend For Robust and Far-Field Keyword Spotting"
UPSTREAM_PAPER_AUTHORS = "Yuxuan Wang, Pascal Getreuer, Thad Hughes, Richard F. Lyon, Rif A. Saurous"
UPSTREAM_PAPER_VENUE = "ICASSP 2017"
UPSTREAM_REFERENCE_URL: Optional[str] = None
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
TASK_GEOMETRY_STATUS = "unestablished"

# Synthetic control geometry only; not asserted PCEN/reference geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_FRAME_SAMPLES = 160
CONTROL_CHANNELS = 1
CONTROL_N_MELS = 40
CONTROL_SECONDS = 1
CONTROL_FRAMES = (CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS) // CONTROL_FRAME_SAMPLES
CONTROL_SAMPLES = CONTROL_FRAMES * CONTROL_FRAME_SAMPLES

RIGHTS_RECORD_PATH = "data/rights/pcen-feature-frontend-rights.json"
COHORT_MANIFEST_PATH = "data/runs/pcen-feature-frontend-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/pcen-feature-frontend-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/pcen-feature-frontend"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
MISSING_SOURCE_PATH = "research/voice-enhancement-20261101/repos/pcen-feature-frontend"
MISSING_WEIGHTS_PATH = "data/models/pcen-feature-frontend"

ABSENCE_PROBES: Tuple[str, ...] = (
    "research/voice-enhancement-20261101/repos/pcen",
    "research/voice-enhancement-20261101/repos/pcen-feature-frontend",
    "research/voice-enhancement-20261101/repos/Per-Channel-Energy-Normalization",
    "research/voice-enhancement-20261101/repos/leaf-audio",
    "research/voice-enhancement-20261101/hf-cache/models--pcen",
    "data/checkouts/pcen",
    "data/checkouts/pcen-feature-frontend",
    "data/models/pcen",
    "data/models/pcen-feature-frontend",
    "data/weights/pcen",
    "data/weights/pcen-feature-frontend",
    "data/envs/pcen-feature-frontend",
    "data/envs/pcen-feature-frontend/requirements.lock",
    RIGHTS_RECORD_PATH,
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
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
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
    "docs/task-evidence/survey-cln-09/README.md":
        "908c42c9e400530ee76463496581ddcd0dbafb5ab70ad901febf268d4c121479",
    "docs/task-evidence/survey-cln-09/report.json":
        "7c4e8f7a29c38970d7ad4a1b1b34e71d62d696a16d4e607c400fae0b685308e1",
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
    "sdk_v0_channels": CONTROL_CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": CONTROL_FRAME_SAMPLES,
    "task_geometry_status": TASK_GEOMETRY_STATUS,
    "task_geometry_asserted": False,
    "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CONTROL_CHANNELS,
    "control_frame_samples": CONTROL_FRAME_SAMPLES,
    "control_n_mels": CONTROL_N_MELS,
    "control_output_kind": "feature_frontend_accounting_only",
    "control_performs_pcen": False,
    "reported_geometry_asserted": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "abi_change": False,
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
    "real_pcen_model": False,
    "release_claim": False,
    "runtime_invoked": False,
    "pcen_performed": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No PCEN reference implementation, model, weights or runtime is loaded or executed.",
    "No TensorFlow, PyTorch, LEAF, KWS runtime, NumPy or audio runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, detection cohort, keyword corpus or labeled event set is consumed.",
    "No detection, keyword-spotting, VAD, EER, AUC, latency, memory or RTF metric is measured.",
    "The synthetic PCEN-shape accounting control performs no PCEN and is never model output.",
    "Source-reported paper context is provenance only, not an established task geometry or local measurement.",
    "Survey-cln-09 evidence is a sibling boundary only; PCEN is not a waveform loudness controller.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "source_checkout", "path": MISSING_SOURCE_PATH, "required": True, "status": "absent", "recorded_url": UPSTREAM_PAPER_URL},
    {"id": "upstream_revision", "recorded_url": UPSTREAM_PAPER_URL, "required": True, "status": "absent", "sha256": None},
    {"id": "inference_weights_or_reference_params", "path": MISSING_WEIGHTS_PATH, "required": True, "status": "absent", "sha256": None},
    {"id": "exact_runtime", "path": RUNTIME_ENV_PATH, "required": True, "status": "absent", "runtime_lock_sha256": None},
    {"id": "source_license_record", "required": True, "status": "absent"},
    {"id": "rights_record", "path": RIGHTS_RECORD_PATH, "required": True, "status": "absent"},
    {"id": "detection_or_keyword_cohort", "path": COHORT_MANIFEST_PATH, "required": True, "status": "absent"},
    {"id": "degradation_and_parity_manifest", "degradation_path": "data/runs/pcen-feature-frontend-cohort/degradation.json", "parity_path": PARITY_MANIFEST_PATH, "required": True, "status": "absent"},
)

CALLER_ASSET_FIELDS = (
    "checkpoint_path", "checkpoint_sha256", "channels", "cohort_manifest_path", "cohort_manifest_sha256",
    "config_path", "config_sha256", "degradation_manifest_path", "degradation_manifest_sha256",
    "frame_samples", "input_sample_rate_hz", "license_record_path", "license_record_sha256",
    "n_mels", "parity_vector_path", "parity_vector_sha256", "rights_record_path", "rights_record_sha256",
    "runtime_lock_path", "runtime_lock_sha256", "runtime_path", "source_checkout_path", "source_revision", "variant",
)
CALLER_FILE_PAIRS = (
    ("checkpoint_path", "checkpoint_sha256"), ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"), ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"), ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("degradation_manifest_path", "degradation_manifest_sha256"), ("parity_vector_path", "parity_vector_sha256"),
)
CALLER_DIR_FIELDS = ("source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_feature_frontend_reference"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
MIN_FRAME_SAMPLES = 80
MAX_FRAME_SAMPLES = 4096
MIN_N_MELS = 1
MAX_N_MELS = 512
MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PCM_SAMPLE_CAP = 10_000_000

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/pcen-feature-frontend/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": "validate_absolute_paths_sha256_revision_shape_declared_geometry_and_offline_variant_only; do_not_import_or_execute_in_this_package",
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CONTROL_CHANNELS,
        "input_sample_rate_hz": None,
        "frame_samples": None,
        "n_mels": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "notes": (
        "Every checkpoint/reference-params file, config, licence, rights record, runtime lock, cohort manifest, "
        "degradation manifest and parity vector must exist at an absolute path and match its declared SHA-256 "
        "before a caller may process audio. No upstream reference revision is pinned because merged evidence "
        "records only paper/inventory context and no exact licensed implementation."
    ),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "source_checkout_absent", "state": "absent", "requirement": "Supply an exact licensed PCEN reference implementation checkout at an immutable 40-hex revision; no checkout or revision is pinned in this workspace."},
    {"id": "reference_assets_absent", "state": "absent", "requirement": "Supply exact reference parameters, configs or trained assets with SHA-256 and byte counts; no PCEN asset is present or identified by digest."},
    {"id": "task_geometry_unestablished", "state": "absent", "requirement": "Record exact sample rate, frame/hop, FFT/mel geometry, PCEN parameters, channels and streaming/windowing contract; paper context is not an established task geometry."},
    {"id": "runtime_absent", "state": "absent", "requirement": "Provide an isolated hash-pinned runtime with a complete lock and recorded platform; no PCEN runtime exists."},
    {"id": "source_license_unverified", "state": "absent", "requirement": "Add upstream reference code/asset licence and terms at the resolved revision; no licence file or redistribution grant is recorded in this workspace."},
    {"id": "rights_and_cohort_uncleared", "state": "absent", "requirement": "Clear code, asset, training-data, source-audio, labels and redistribution rights, then freeze a rights-cleared detection/keyword cohort with timestamps and strata."},
    {"id": "parity_and_quality_absent", "state": "absent", "requirement": "Produce one approved exact-reference output on a frozen caller input plus analysis-profile detection/keyword quality and independent timing evidence; no local output exists."},
    {"id": "provider_intake_not_started", "state": "absent", "requirement": "Complete opt-in provider intake, descriptor/registry review and independent public-surface/release decision before any exposure; this package makes no such change."},
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_and_asset_identity", "The full 40-hex source revision, reference params/config/assets and source licence match exact pins."),
    ("runtime_admission", "An isolated hash-pinned runtime with a complete lock is admitted on a recorded platform."),
    ("artifact_rights_and_licence", "Source, weights/params, training-data, source-audio, labels, output-use and redistribution rights are cleared with notices."),
    ("exact_reference_parity", "An approved exact-reference PCEN output matches the reference on a frozen caller-supplied input for one frozen configuration."),
    ("analysis_cohort_and_scoring", "A rights-cleared held-out detection/keyword cohort scores timestamps, probabilities/events and stratified FP/FN as separate outcomes."),
    ("task_scope_and_geometry", "Input/sample/frame/mel/PCEN geometry and scope are established and PCEN is not misrepresented as a waveform loudness controller."),
    ("opt_in_provider_intake", "Explicit opt-in provider intake, licence review, descriptor review and an independent public-surface decision are complete."),
    ("public_default_and_release", "Explicit default selection, resource/deadline evidence and release or public-benchmark approval are recorded; this package is off by default."),
)

ANALYSIS_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("timestamped_probabilities_or_events", "Score timestamped probabilities, event boundaries or detections on a frozen cohort.", "absent"),
    ("stratified_conditions", "Include quiet/active speech, idle noise, known positives/negatives and onset/offset delay strata.", "absent"),
    ("independent_state_and_intervals", "Verify independent state, exact source intervals, availability and cross-hop behavior.", "absent"),
    ("dropped_stale_events", "Record dropped/stale events and no stale cross-epoch event revival.", "absent"),
    ("nonfinite_and_invalid_rejection", "Reject malformed, missing and nonfinite inputs; keep validity separate from nonspeech.", "structural_only"),
    ("timing_and_resources", "Measure paced target-device timing/resources; separate callback suitability from compute speed.", "not_measured"),
    ("failure_and_control_results", "Record missing, invalid, nonfinite and adverse controls without qualifying the candidate.", "structural_only"),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "paper_title": UPSTREAM_PAPER_TITLE,
    "paper_authors": UPSTREAM_PAPER_AUTHORS,
    "paper_venue": UPSTREAM_PAPER_VENUE,
    "paper_url": UPSTREAM_PAPER_URL,
    "inventory_component_id": COMPONENT,
    "inventory_evidence_status": "considered",
    "inventory_verification_profile": PROFILE,
    "inventory_task": TASK,
    "inventory_note": "Test as a feature stage for detection and keyword spotting. Keep waveform loudness under its own task.",
    "survey_boundary": "survey-cln-09 records PCEN as an adjacent feature frontend, not a waveform loudness controller.",
    "finding": "PCEN is described in ICASSP 2017 as a trainable frontend for robust/far-field keyword spotting. This workspace has no exact licensed reference, revision, assets, runtime, cohort or parity vector.",
    "notes": "No PCEN output, detection score, keyword metric, timing or parity value is attributed to this candidate.",
}

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty", "pcm_not_sequence", "pcm_none", "pcm_wrong_rate", "pcm_stereo",
    "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "pcm_out_of_range", "pcm_bool", "pcm_string",
    "manifest_not_object", "manifest_missing_field", "manifest_extra_field", "manifest_relative_path",
    "manifest_bad_sha", "manifest_short_revision", "manifest_nonhex_revision", "manifest_wrong_variant",
    "manifest_channels_zero", "manifest_frame_zero", "manifest_n_mels_zero", "manifest_rate_below_range",
    "manifest_missing_asset", "manifest_missing_directory", "manifest_hash_mismatch",
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
    if not repository.is_dir():
        return []
    found: List[str] = []
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md", "COPYING.txt", "NOTICE"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/pcen",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/pcen-feature-frontend",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/Per-Channel-Energy-Normalization",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/leaf-audio",
        SOURCE_ROOT / "data/checkouts/pcen",
        SOURCE_ROOT / "data/checkouts/pcen-feature-frontend",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/pcen",
        SOURCE_ROOT / "data/models/pcen-feature-frontend",
        SOURCE_ROOT / "data/weights/pcen",
        SOURCE_ROOT / "data/weights/pcen-feature-frontend",
    ]


def probe_absence() -> List[Dict[str, Any]]:
    return [{"path": relative, "exists": (SOURCE_ROOT / relative).exists()} for relative in ABSENCE_PROBES]


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
        readme_declares = ("license" in text or "licence" in text or "copyright" in text)
    weight_paths = _weights_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "source_revision_matches": False,
        "source_candidates": [{"path": str(path.relative_to(SOURCE_ROOT)), "present": path.is_dir()} for path in source_paths],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "weights_candidates": [{"path": str(path.relative_to(SOURCE_ROOT)), "present": path.exists()} for path in weight_paths],
        "weights_present": any(path.exists() for path in weight_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(not item["exists"] for item in probes),
        "requested_config": {
            "reported_method": "per_channel_energy_normalization_feature_frontend",
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_frame_samples": CONTROL_FRAME_SAMPLES,
            "control_n_mels": CONTROL_N_MELS,
            "upstream_revision": UPSTREAM_REVISION,
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
    rows = [row for row in document.get("tasks", []) if isinstance(row, dict) and row.get("id") == TASK]
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
    for field, expected in (("base_commit", BASE_COMMIT), ("branch", BRANCH), ("worktree", CLAIM_WORKTREE), ("reviewer", REVIEWER)):
        if claim.get(field) != expected:
            raise Reject("claim " + field + " mismatch")
    return {
        "source": relative,
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {k: claim[k] for k in ("base_commit", "branch", "worktree", "reviewer")},
    }


# ---------------------------------------------------------------------------
# Synthetic PCM and deterministic PCEN-shape accounting (no PCEN performed).
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_input_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x5043454E
    for index in range(CONTROL_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CONTROL_CHANNELS) -> List[float]:
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if channels != CONTROL_CHANNELS:
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
        "channels": CONTROL_CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def pcen_shape_ledger(input_samples: int, sample_rate_hz: int, frame_samples: int,
                      n_mels: int) -> Dict[str, Any]:
    for name, value in (("input_samples", input_samples), ("sample_rate_hz", sample_rate_hz),
                        ("frame_samples", frame_samples), ("n_mels", n_mels)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject(name + " must be an integer")
        if value <= 0:
            raise Reject(name + " must be positive")
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if frame_samples < MIN_FRAME_SAMPLES or frame_samples > MAX_FRAME_SAMPLES:
        raise Reject("frame_samples outside admitted range")
    if n_mels < MIN_N_MELS or n_mels > MAX_N_MELS:
        raise Reject("n_mels outside admitted range")
    frame_count = input_samples // frame_samples
    remainder = input_samples % frame_samples
    return {
        "input_samples": input_samples,
        "sample_rate_hz": sample_rate_hz,
        "frame_samples": frame_samples,
        "n_mels": n_mels,
        "frame_count": frame_count,
        "remainder_samples": remainder,
        "declared_output_shape": [frame_count, n_mels],
        "declared_output_values": frame_count * n_mels,
        "pcen_performed": False,
        "note": "Declared shape accounting only. No PCEN, FFT, mel filterbank, smoothing or model inference runs.",
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


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest " + field + " is outside the admitted range")
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
        if not isinstance(value, str) or not value or not Path(value).is_absolute():
            raise Reject("manifest " + first + " must be absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value or not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int) or channels != CONTROL_CHANNELS:
        raise Reject("manifest channels mismatch")
    input_rate = _rate_value(manifest, "input_sample_rate_hz")
    frame_samples = manifest["frame_samples"]
    if isinstance(frame_samples, bool) or not isinstance(frame_samples, int) or frame_samples < MIN_FRAME_SAMPLES or frame_samples > MAX_FRAME_SAMPLES:
        raise Reject("manifest frame_samples outside admitted range")
    n_mels = manifest["n_mels"]
    if isinstance(n_mels, bool) or not isinstance(n_mels, int) or n_mels < MIN_N_MELS or n_mels > MAX_N_MELS:
        raise Reject("manifest n_mels outside admitted range")
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
        "accepted": True, "source_revision": revision, "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "variant": CALLER_VARIANT, "input_sample_rate_hz": input_rate, "channels": CONTROL_CHANNELS,
        "frame_samples": frame_samples, "n_mels": n_mels, "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS), "total_asset_bytes": total_bytes, "model_executed": False,
    }


def _shape_only_manifest() -> Dict[str, Any]:
    root = "/nonexistent/pcen-evidence-fixture"
    digest = "0" * 64
    return {
        "channels": CONTROL_CHANNELS,
        "checkpoint_path": root + "/checkpoint.bin",
        "checkpoint_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "degradation_manifest_path": root + "/degradation.json",
        "degradation_manifest_sha256": digest,
        "frame_samples": CONTROL_FRAME_SAMPLES,
        "input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "n_mels": CONTROL_N_MELS,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    assignments = {
        "checkpoint_path": HERE / "reference.py",
        "config_path": HERE / "README.md",
        "license_record_path": HERE / "verify.py",
        "rights_record_path": HERE / "run.py",
        "runtime_lock_path": HERE / "test_reference.py",
        "cohort_manifest_path": HERE / "reference.py",
        "degradation_manifest_path": HERE / "run.py",
        "parity_vector_path": HERE / "README.md",
    }
    manifest: Dict[str, Any] = {
        "channels": CONTROL_CHANNELS,
        "runtime_path": str(SDK_ROOT),
        "input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "frame_samples": CONTROL_FRAME_SAMPLES,
        "n_mels": CONTROL_N_MELS,
        "source_checkout_path": str(HERE),
        "source_revision": "a" * 40,
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(path.read_bytes())
    return manifest


def run_adverse_controls() -> List[Dict[str, str]]:
    good_input = synthetic_input_pcm()
    good_manifest = _shape_only_manifest()

    def case(case_id: str, action) -> Dict[str, str]:
        try:
            action()
        except Reject as error:
            return {"case": case_id, "result": "rejected", "reason": str(error)}
        except Exception as error:  # noqa: BLE001
            return {"case": case_id, "result": "unexpected_error", "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    existing = _existing_file_manifest()
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
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("checkpoint_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong("checkpoint_path", "checkpoints/pcen.bin")),
        ("manifest_bad_sha", wrong("checkpoint_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "abc123")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "streaming")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_frame_zero", wrong("frame_samples", 0)),
        ("manifest_n_mels_zero", wrong("n_mels", 0)),
        ("manifest_rate_below_range", wrong("input_sample_rate_hz", 4000)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(dict(existing, checkpoint_path="/nonexistent/pcen/checkpoint.bin"))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(dict(existing, runtime_path="/nonexistent/pcen/runtime"))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(dict(existing, checkpoint_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    summary = pcm_summary(good_input, CONTROL_SAMPLE_RATE_HZ)
    if summary["samples"] != CONTROL_SAMPLES:
        raise Reject("synthetic input control mismatch")
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_input_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    ledger = pcen_shape_ledger(len(source), CONTROL_SAMPLE_RATE_HZ, CONTROL_FRAME_SAMPLES, CONTROL_N_MELS)
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": "caller_supplied_synthetic_pcen_shape_accounting_not_model_output",
        "geometry": {
            "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_frame_samples": CONTROL_FRAME_SAMPLES,
            "control_n_mels": CONTROL_N_MELS,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "offline_feature_frontend_shape_accounting",
            "incremental_streaming": False,
            "performs_pcen": False,
        },
        "input_pcm": source_summary,
        "shape_ledger": ledger,
        "acceptance_outcomes": [
            {"id": "validity_and_nonfinite", "measured": False, "value": None, "reason": "synthetic validity control only; no model output"},
            {"id": "timestamped_probabilities_or_events", "measured": False, "value": None, "reason": "no detection/keyword scorer or model output"},
            {"id": "stratified_fp_fn", "measured": False, "value": None, "reason": "no rights-cleared cohort"},
            {"id": "onset_offset_delay", "measured": False, "value": None, "reason": "no timestamped reference or output"},
            {"id": "state_and_interval_integrity", "measured": False, "value": None, "reason": "no runtime state machine"},
            {"id": "timing_and_resources", "measured": False, "value": None, "reason": "no runtime or device clock"},
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": ["pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": ["pcm_bool", "pcm_string", "pcm_out_of_range", "pcm_wrong_rate", "pcm_stereo", "manifest_channels_zero", "manifest_frame_zero", "manifest_n_mels_zero", "manifest_rate_below_range"],
            "missing_rejected": ["pcm_empty", "pcm_none", "pcm_not_sequence", "manifest_missing_field", "manifest_missing_asset", "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": "Synthetic PCEN-shape accounting control only. It performs no PCEN, FFT, mel filterbank, smoothing, detection or model inference, is not PCEN output, not real audio, not a quality or timing result and cannot qualify the candidate.",
    }


# ---------------------------------------------------------------------------
# Report and contract models.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"] and observed["source_revision"] is not None
        and observed["license_file_present"] and observed["weights_present"]
        and observed["runtime_env_present"] and observed["runtime_lock_present"]
        and observed["rights_record_present"] and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["source_checkout_present"]:
        result = "source_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False, "audit_result": result, "source_present": observed["source_checkout_present"],
        "source_revision": observed["source_revision"], "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "license_present": observed["license_file_present"], "weights_present": observed["weights_present"],
        "runtime_env_present": observed["runtime_env_present"], "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"], "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"], "observed": observed,
        "note": "No PCEN source, revision, reference assets, runtime, licence, rights record, cohort or parity vector was observed. Survey/paper context is not executable evidence.",
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = [{"id": gate, "requirement": requirement, "status": "blocked"} for gate, requirement in GATE_REQUIREMENTS]
    profile_items = [
        {"id": item, "requirement": requirement, "package_status": status, "satisfied_for_qualification": False, "qualification_effect": "none"}
        for item, requirement, status in ANALYSIS_REQUIREMENTS
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
            "reason": "The PCEN reference implementation, revision, assets/weights, exact geometry, runtime, licence, rights, detection/keyword cohort and parity evidence are absent; no qualifying result exists.",
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
            "paper_title": UPSTREAM_PAPER_TITLE,
            "paper_authors": UPSTREAM_PAPER_AUTHORS,
            "paper_venue": UPSTREAM_PAPER_VENUE,
            "paper_url": UPSTREAM_PAPER_URL,
            "reference_url": UPSTREAM_REFERENCE_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "reported_geometry_asserted": False,
            "geometry_status": TASK_GEOMETRY_STATUS,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "analysis_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": "Structural accounting passes, but no real PCEN reference, licensed assets, rights-cleared cohort, runtime or approved parity exists, so the analysis profile is not satisfied for qualification.",
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": all(item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [{"gate_id": gate, "condition": requirement} for gate, requirement in GATE_REQUIREMENTS],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [MISSING_SOURCE_PATH, MISSING_WEIGHTS_PATH, RIGHTS_RECORD_PATH, COHORT_MANIFEST_PATH, PARITY_MANIFEST_PATH],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "Fixed workspace paths are probed for source, assets, runtime, rights and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract() -> Dict[str, Any]:
    report = build_report()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-" "Identifier": "Apache-2.0",
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
        "source_checkout": {"path": MISSING_SOURCE_PATH, "present": False, "paper_url": UPSTREAM_PAPER_URL, "reference_url": UPSTREAM_REFERENCE_URL, "revision": None, "revision_pin_available": False},
        "upstream_identity": report["upstream_identity"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "analysis_profile_requirements": [{"id": item["id"], "requirement": item["requirement"], "package_status": item["package_status"]} for item in report["analysis_profile"]["required_items"]],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "reproduction": {
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
            "cold_start_regenerations": 3,
            "command": "python3 run.py all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
        },
        "licensing": {"copyright": "2026 Tsakanyan Hovhannes", "license": "Apache-2.0", "json_sidecars": True},
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
