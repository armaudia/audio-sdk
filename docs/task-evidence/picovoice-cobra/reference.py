# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-PICOVOICE-COBRA.

Picovoice Cobra is a proprietary voice-activity/probability engine distributed
by Picovoice with vendor runtime, platform libraries, access-key/account terms,
and separate licensing. This workspace has no approved public or user-supplied
Cobra runtime, access key, model/library artifact, rights record, or frozen
held-out cohort outputs. This package never downloads, installs, imports, or
executes Cobra; never uses network/audio devices; never fabricates scores; and
never qualifies the candidate.

It provides: fail-closed absence audit, stable linked-row TASKS identity
projection (never hashing full TASKS.json), a caller-supplied runtime/access-key
manifest contract validated without execution, and deterministic synthetic
adverse controls proving invalid/missing/nonfinite inputs are rejected.
Decision is DEFER; qualification is not_qualified.
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

TASK = "SDK-PICOVOICE-COBRA"
TITLE = "Picovoice Cobra"
COMPONENT = "picovoice-cobra"
TASK_PREFIX = f"docs/task-evidence/{COMPONENT}/"
BASE_COMMIT = "01cc99e1de5b724a3a999e86d85f5771736197ae"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-PICOVOICE-COBRA"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = "audio-sdk/task-evidence/picovoice-cobra/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "vendor_runtime_rights_and_cohort_clearance"

UPSTREAM_NAME = "Picovoice Cobra Voice Activity Detection"
UPSTREAM_VENDOR = "Picovoice Inc."
UPSTREAM_PRODUCT_URL = "https://picovoice.ai/platform/cobra/"
UPSTREAM_DOCS_URL = "https://picovoice.ai/docs/api/cobra-python/"
UPSTREAM_BENCHMARK_URL = "https://picovoice.ai/docs/benchmark/vad/"
UPSTREAM_LICENSE_SUMMARY = (
    "Proprietary Picovoice license/terms; access key required; "
    "redistribution/integration terms must be reviewed before any package use.")
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False

# Synthetic control geometry only; not asserted Cobra/runtime geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_FRAME_SAMPLES = 512
CONTROL_CHANNELS = 1
CONTROL_SECONDS = 1
CONTROL_FRAMES = (CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS) // CONTROL_FRAME_SAMPLES
CONTROL_SAMPLES = CONTROL_FRAMES * CONTROL_FRAME_SAMPLES

MISSING_RUNTIME_PATH = "data/runtimes/picovoice-cobra"
MISSING_ASSET_PATH = "data/models/picovoice-cobra"
RIGHTS_RECORD_PATH = "data/rights/picovoice-cobra-rights.json"
COHORT_MANIFEST_PATH = "data/runs/picovoice-cobra-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/picovoice-cobra-parity/manifest.json"

ABSENCE_PROBES: Tuple[str, ...] = (
    "data/runtimes/picovoice-cobra",
    "data/runtimes/picovoice-cobra/lib",
    "data/models/picovoice-cobra",
    "data/models/picovoice-cobra/cobra.pv",
    "data/envs/picovoice-cobra",
    "data/envs/picovoice-cobra/requirements.lock",
    "data/rights/picovoice-cobra-rights.json",
    "data/runs/picovoice-cobra-cohort/manifest.json",
    "data/runs/picovoice-cobra-parity/manifest.json",
    "research/voice-enhancement-20261101/repos/picovoice-cobra",
    "research/voice-enhancement-20261101/repos/cobra",
)

STABLE_TASK_FIELDS = (
    "acceptance", "component", "deliverable", "depends_on", "evidence", "id",
    "mode", "repository", "title", "write_scope")
MUTABLE_TASK_FIELDS = (
    "blocked_reason", "dispatch_priority", "handoff", "owner", "review", "status")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "reports/vad-research/attempt-discovery-20261028-01/findings.md":
        "9d5c555c1c5f2db9ce3eb27da2d3f625c2e25621f6700521f82c8af300ff59d5",
    "reports/vad-research/chaining-evaluation.md":
        "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
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
    "README.md", "SOURCES.sha256.license", "contract.json",
    "contract.json.license", "reference.py", "report.json",
    "report.json.license", "report.json.sha256", "report.json.sha256.license",
    "run.py", "test_reference.py", "verify.py")

BOUNDARY: Dict[str, Any] = {
    "abi_change": False, "adapter_runtime_bundled": False, "asset_bundled": False,
    "ci_change": False, "default_selected": False, "descriptor_registry_change": False,
    "descriptor_settings": {}, "enabled_by_default": False,
    "installed_v0_behavior_change": False, "network_used": False,
    "processor_exposure": False, "production_callback_registered": False,
    "provider_registration": False, "public_api_abi_change": False,
    "registered": False, "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False, "vendor_runtime_invoked": False,
    "weights_vendored": False,
}
SCOPE: Dict[str, Any] = {
    "device_timing": False, "listening": False, "model_executed": False,
    "network_used": False, "public_benchmark": False, "real_audio": False,
    "real_corpus": False, "real_cobra_runtime": False, "release_claim": False,
    "runtime_invoked": False, "task_local_only": True,
    "vendor_runtime_invoked": False, "weights_downloaded": False,
    "weights_loaded": False,
}
NON_CLAIMS: Tuple[str, ...] = (
    "No Picovoice Cobra runtime, library, SDK package, model, or access key is loaded, downloaded, or executed.",
    "No network request, account creation, vendor API call, or asset redistribution occurs.",
    "No real audio, held-out cohort, label, listening, device timing, or public benchmark is used.",
    "Source-reported/vendor-reported scores are provenance only and are never reproduced, pooled, or qualified here.",
    "The synthetic control is structural accounting only; it performs no VAD and is never Cobra output.",
    "No provider, descriptor, registry, default, installed v0 path, shared build, CI, board, handoff, or release changed.",
    "Missing or unapproved runtime/assets/rights never qualify the candidate; decision remains DEFER.",
)
ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "approved_runtime", "path": MISSING_RUNTIME_PATH, "required": True, "status": "absent", "notes": "Approved Picovoice Cobra runtime/library for the target platform; no runtime is present."},
    {"id": "approved_access_key_policy", "required": True, "status": "absent", "notes": "Explicit approved access-key handling/terms; keys must never be committed or logged."},
    {"id": "model_or_library_artifacts", "path": MISSING_ASSET_PATH, "required": True, "status": "absent", "notes": "Exact vendor model/library artifacts with SHA-256 and byte counts where distributable."},
    {"id": "source_license_and_terms", "required": True, "status": "absent", "notes": "Picovoice terms/license/redistribution review for intended integration and distribution."},
    {"id": "rights_record", "path": RIGHTS_RECORD_PATH, "required": True, "status": "absent"},
    {"id": "held_out_cohort", "path": COHORT_MANIFEST_PATH, "required": True, "status": "absent", "notes": "Rights-cleared, label-complete held-out cohort with frozen outputs and stratified analysis scoring."},
    {"id": "parity_or_reference_outputs", "path": PARITY_MANIFEST_PATH, "required": True, "status": "absent"},
)
EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "vendor_runtime_absent", "state": "absent", "requirement": "Provide an approved Picovoice Cobra runtime/library with exact version, platform, SHA-256, and license/terms review; no runtime is present."},
    {"id": "access_key_and_terms_unapproved", "state": "absent", "requirement": "Provide approved access-key handling and vendor terms for intended integration; no key/terms approval is recorded and keys must never be committed."},
    {"id": "vendor_assets_unpinned", "state": "absent", "requirement": "Provide exact Cobra model/library artifacts or documented vendor-managed immutable identifiers with SHA-256 where distributable; none are pinned locally."},
    {"id": "rights_and_redistribution_uncleared", "state": "absent", "requirement": "Clear code/runtime/model/data/output redistribution and usage rights before any integration or distribution."},
    {"id": "held_out_cohort_absent", "state": "absent", "requirement": "Provide a rights-cleared, label-complete held-out cohort with frozen candidate outputs and stratified analysis scoring; no cohort is present."},
    {"id": "parity_and_quality_absent", "state": "absent", "requirement": "Produce approved reference/parity outputs and analysis-profile quality evidence against the exact runtime; no local output exists."},
    {"id": "timing_and_target_unmeasured", "state": "absent", "requirement": "Measure paced target-device timing/resources under an approved runtime; no timing evidence exists."},
    {"id": "provider_intake_not_started", "state": "absent", "requirement": "Complete opt-in external-adapter intake, descriptor/registry review, and independent public-surface/release decision before any exposure; this package makes no such change."},
)
GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("approved_runtime_and_terms", "An approved Picovoice Cobra runtime, access-key policy, and vendor terms are reviewed for the intended integration."),
    ("artifact_identity_and_rights", "Exact runtime/model/library artifacts or vendor-managed immutable identifiers, SHA-256 where distributable, and rights/redistribution records are complete."),
    ("held_out_cohort_and_labels", "A rights-cleared, label-complete held-out cohort with frozen outputs is available for analysis-profile scoring."),
    ("exact_reference_or_parity_evidence", "Approved reference/parity outputs are captured from the exact runtime/configuration on frozen inputs."),
    ("analysis_profile_quality", "Timestamped probabilities/events, onset/offset, stratified FP/FN, validity separation, and state/interval integrity are scored on the held-out cohort."),
    ("paced_target_timing", "Paced target-device timing/resources and availability are measured independently of compute speed."),
    ("opt_in_adapter_intake", "Explicit opt-in external-adapter intake, descriptor/registry review, and independent public-surface decision are complete."),
    ("public_default_and_release", "Explicit default selection, resource/deadline evidence, and release/public-benchmark approval are recorded; this package is off by default."),
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
    "vendor": UPSTREAM_VENDOR,
    "product_url": UPSTREAM_PRODUCT_URL,
    "docs_url": UPSTREAM_DOCS_URL,
    "benchmark_url": UPSTREAM_BENCHMARK_URL,
    "license_summary": UPSTREAM_LICENSE_SUMMARY,
    "discovery_finding": "reports/vad-research/attempt-discovery-20261028-01/findings.md records Picovoice Cobra as a proprietary VAD with vendor benchmark context; it is not runnable/qualified in this workspace.",
    "chaining_finding": "reports/vad-research/chaining-evaluation.md treats VAD as analysis/advisory boundary context only; no Cobra runtime evidence is present.",
    "notes": "Vendor-reported or source-reported scores are not reproduced, not pooled, and not used as qualification evidence.",
}
ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty", "pcm_not_sequence", "pcm_none", "pcm_wrong_rate", "pcm_stereo",
    "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "pcm_out_of_range", "pcm_bool", "pcm_string",
    "manifest_not_object", "manifest_missing_field", "manifest_extra_field", "manifest_relative_path",
    "manifest_bad_sha", "manifest_wrong_variant", "manifest_missing_asset", "manifest_missing_directory",
    "manifest_hash_mismatch", "manifest_access_key_present",
)
CALLER_ASSET_FIELDS = (
    "access_key_env_var", "access_key_present", "channels", "config_path", "config_sha256",
    "library_path", "library_sha256", "model_path", "model_sha256", "rights_record_path",
    "rights_record_sha256", "runtime_path", "terms_record_path", "terms_record_sha256", "variant")
CALLER_FILE_PAIRS = (
    ("config_path", "config_sha256"), ("library_path", "library_sha256"),
    ("model_path", "model_sha256"), ("rights_record_path", "rights_record_sha256"),
    ("terms_record_path", "terms_record_sha256"))
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_DIR_FIELDS = ("runtime_path",)
CALLER_VARIANT = "caller_supplied_cobra_runtime_reference"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 48000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3
PCM_SAMPLE_CAP = 10_000_000


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
        return {k: _normalize_negzero(v) for k, v in value.items()}
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


def probe_absence() -> List[Dict[str, Any]]:
    return [{"path": relative, "exists": (SOURCE_ROOT / relative).exists()} for relative in ABSENCE_PROBES]


def audit_assets() -> Dict[str, Any]:
    probes = probe_absence()
    runtime = SOURCE_ROOT / MISSING_RUNTIME_PATH
    asset = SOURCE_ROOT / MISSING_ASSET_PATH
    rights = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity = SOURCE_ROOT / PARITY_MANIFEST_PATH
    return {
        "runtime_present": runtime.exists(),
        "asset_present": asset.exists(),
        "rights_record_present": rights.is_file(),
        "cohort_manifest_present": cohort.is_file(),
        "parity_manifest_present": parity.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(not item["exists"] for item in probes),
        "approved_runtime_available": False,
        "access_key_policy_approved": False,
        "vendor_terms_reviewed": False,
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


def _triangle(index: int, period: int, scale: float) -> float:
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_input_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x434F4252
    for index in range(CONTROL_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 41, 0.25) + 0.01 * noise)
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
        "samples": len(values), "sample_rate_hz": sample_rate_hz,
        "channels": CONTROL_CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak, "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
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
    env_name = manifest["access_key_env_var"]
    if not isinstance(env_name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}", env_name):
        raise Reject("manifest access_key_env_var must be an uppercase env var name")
    if manifest["access_key_present"] is not False:
        raise Reject("manifest access_key_present must be false; access keys must never be committed")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int) or channels != CONTROL_CHANNELS:
        raise Reject("manifest channels mismatch")
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
        "accepted": True, "variant": CALLER_VARIANT,
        "access_key_env_var": env_name, "access_key_present": False,
        "channels": CONTROL_CHANNELS, "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes, "runtime_executed": False,
    }


def _shape_only_manifest() -> Dict[str, Any]:
    root = "/nonexistent/picovoice-cobra-fixture"
    digest = "0" * 64
    return {
        "access_key_env_var": "PICOVOICE_ACCESS_KEY",
        "access_key_present": False,
        "channels": CONTROL_CHANNELS,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "library_path": root + "/libcobra.so",
        "library_sha256": digest,
        "model_path": root + "/cobra.pv",
        "model_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_path": root + "/runtime",
        "terms_record_path": root + "/terms.json",
        "terms_record_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    assignments = {
        "config_path": HERE / "README.md",
        "library_path": HERE / "reference.py",
        "model_path": HERE / "verify.py",
        "rights_record_path": HERE / "run.py",
        "terms_record_path": HERE / "test_reference.py",
    }
    manifest: Dict[str, Any] = {
        "access_key_env_var": "PICOVOICE_ACCESS_KEY",
        "access_key_present": False,
        "channels": CONTROL_CHANNELS,
        "runtime_path": str(SDK_ROOT),
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
        ("manifest_missing_field", drop("model_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(dict(good_manifest, access_key="secret"))),
        ("manifest_relative_path", wrong("config_path", "config.json")),
        ("manifest_bad_sha", wrong("model_sha256", "ABC")),
        ("manifest_wrong_variant", wrong("variant", "streaming")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(dict(existing, model_path="/nonexistent/cobra.pv"))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(dict(existing, runtime_path="/nonexistent/runtime"))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(dict(existing, model_sha256="0" * 64))),
        ("manifest_access_key_present", wrong("access_key_present", True)),
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
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse if item["result"] == "rejected"]
    return {
        "runtime_executed": False,
        "executor": "absent",
        "plan_source": "caller_supplied_synthetic_structural_accounting_not_cobra_output",
        "geometry": {
            "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_frame_samples": CONTROL_FRAME_SAMPLES,
            "control_total_samples": CONTROL_SAMPLES,
            "control_performs_vad": False,
        },
        "input_pcm": source_summary,
        "shape_ledger": {
            "input_samples": len(source),
            "frame_samples": CONTROL_FRAME_SAMPLES,
            "frame_count": len(source) // CONTROL_FRAME_SAMPLES,
            "remainder_samples": len(source) % CONTROL_FRAME_SAMPLES,
            "declared_output_kind": "voice_probability_per_frame",
            "vad_performed": False,
            "note": "Declared shape accounting only. No Cobra runtime, model, probability, event, or timing is produced.",
        },
        "adverse": adverse,
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": ["pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": ["pcm_bool", "pcm_string", "pcm_out_of_range", "pcm_wrong_rate", "pcm_stereo", "manifest_wrong_variant"],
            "missing_rejected": ["pcm_empty", "pcm_none", "pcm_not_sequence", "manifest_missing_field", "manifest_missing_asset", "manifest_missing_directory"],
            "secret_rejected": ["manifest_access_key_present"],
            "rejected_cases": rejected,
        },
        "qualification_effect": "none",
        "note": "Synthetic structural control only. It performs no VAD, is not Cobra output, not real audio, not quality/timing evidence, and cannot qualify the candidate.",
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
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
            "reason": "No approved Picovoice Cobra runtime, access-key/terms approval, rights-cleared cohort, parity, or paced timing evidence is present; no qualifying result exists.",
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "vendor": UPSTREAM_VENDOR,
            "product_url": UPSTREAM_PRODUCT_URL,
            "docs_url": UPSTREAM_DOCS_URL,
            "benchmark_url": UPSTREAM_BENCHMARK_URL,
            "license_summary": UPSTREAM_LICENSE_SUMMARY,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["absence_probes"],
        "caller_asset_contract": {
            "contract_id": "audio-sdk/picovoice-cobra/caller-supplied-runtime/0.1",
            "runtime_is_caller_owned": True,
            "runtime_is_vendored": False,
            "access_key_must_not_be_committed": True,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_absolute_paths_sha256_and_terms_records_without_execution; do_not_import_or_execute_in_this_package",
            "required_fields": list(CALLER_ASSET_FIELDS),
            "required_variant": CALLER_VARIANT,
            "notes": "Runtime/library/model/config/rights/terms files must exist at absolute paths with matching SHA-256 before any future processing. Access keys must be supplied only through approved runtime mechanisms and never recorded in manifests, reports, logs, or git.",
        },
        "analysis_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in profile_items],
            "real_runtime_metrics": None,
            "note": "Structural controls pass, but no approved Cobra runtime, rights-cleared cohort, parity, or paced timing exists; analysis profile is not satisfied for qualification.",
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": all(item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [{"gate_id": gate, "condition": requirement} for gate, requirement in GATE_REQUIREMENTS],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [MISSING_RUNTIME_PATH, MISSING_ASSET_PATH, RIGHTS_RECORD_PATH, COHORT_MANIFEST_PATH, PARITY_MANIFEST_PATH],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no vendor runtime, audio runtime, or network is used.",
            "Fixed workspace paths are probed for runtime, assets, rights, cohort, and parity presence.",
            "No source checkout is executed and no runtime/model byte is loaded for inference.",
            "No network request, download, audio device, model load, or timing run occurs.",
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
        "upstream_identity": report["upstream_identity"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": report["caller_asset_contract"],
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
