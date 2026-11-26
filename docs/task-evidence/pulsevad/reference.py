# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-PULSEVAD.

PulseVAD is a tiny causal VAD candidate described upstream as a 2,118-parameter
model with 200 ms non-overlapping windows and ONNX/TorchScript/C assets. This
workspace has no pinned source revision, no exact weights/runtime, no license
review artifact, no rights-cleared cohort, no parity output, and no paced
timing evidence. This package never downloads, installs, imports, or executes
PulseVAD; never uses network/audio devices; never fabricates scores; and never
qualifies the candidate.

It provides: fail-closed absence audit, stable linked-row TASKS identity
projection (never hashing full TASKS.json), a caller-supplied asset/runtime
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
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-PULSEVAD"
TITLE = "PulseVAD"
COMPONENT = "pulsevad"
TASK_PREFIX = f"docs/task-evidence/{COMPONENT}/"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-PULSEVAD"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = "audio-sdk/task-evidence/pulsevad/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "exact_source_weights_runtime_rights_and_cohort_clearance"

UPSTREAM_NAME = "PulseVAD"
UPSTREAM_VENDOR = "AydinAdnan / upstream PulseVAD project"
UPSTREAM_REPO_URL = "https://github.com/AydinAdnan/PulseVAD"
UPSTREAM_LICENSE_SUMMARY = (
    "Upstream repository claims MIT; no local pinned revision, license text, "
    "artifact digest, or redistribution review is staged in this workspace.")
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False

# Synthetic control geometry only; not asserted PulseVAD/runtime geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_FRAME_SAMPLES = 3200  # 200 ms, matches reported upstream window only as a control shape
CONTROL_CHANNELS = 1
CONTROL_SECONDS = 1
CONTROL_FRAMES = (CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS) // CONTROL_FRAME_SAMPLES
CONTROL_SAMPLES = CONTROL_FRAMES * CONTROL_FRAME_SAMPLES

MISSING_RUNTIME_PATH = "data/runtimes/pulsevad"
MISSING_ASSET_PATH = "data/models/pulsevad"
RIGHTS_RECORD_PATH = "data/rights/pulsevad-rights.json"
COHORT_MANIFEST_PATH = "data/runs/pulsevad-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/pulsevad-parity/manifest.json"

ABSENCE_PROBES: Tuple[str, ...] = (
    "data/runtimes/pulsevad",
    "data/models/pulsevad",
    "data/models/pulsevad/pulsevad.onnx",
    "data/models/pulsevad/pulsevad.pt",
    "data/envs/pulsevad",
    "data/envs/pulsevad/requirements.lock",
    "data/rights/pulsevad-rights.json",
    "data/runs/pulsevad-cohort/manifest.json",
    "data/runs/pulsevad-parity/manifest.json",
    "research/voice-enhancement-20261101/repos/PulseVAD",
    "research/voice-enhancement-20261101/repos/pulsevad",
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
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "reports/vad-research/attempt-discovery-20261028-01/findings.md":
        "9d5c555c1c5f2db9ce3eb27da2d3f625c2e25621f6700521f82c8af300ff59d5",
    "reports/vad-research/chaining-evaluation.md":
        "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "reports/vad-research/attempt-neural-01/assessment.md":
        "74232ba9f36976ef1b238bca12305d6c02a614adb73fb2981f6fc3f07133cfe1",
    "reports/vad-research/attempt-open-models-20261028-01/assessment.md":
        "565d4330d625dd8eec9e607811df300749382feffc87ef54d5e4924e09448ad6",
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
    "real_corpus": False, "real_pulsevad_runtime": False, "release_claim": False,
    "runtime_invoked": False, "task_local_only": True,
    "vendor_runtime_invoked": False, "weights_downloaded": False,
    "weights_loaded": False,
}
NON_CLAIMS: Tuple[str, ...] = (
    "No PulseVAD source checkout, runtime, model, ONNX/TorchScript/C asset, or weight is loaded, downloaded, or executed.",
    "No network request, repository clone, package install, or asset redistribution occurs.",
    "No real audio, held-out cohort, label, listening, device timing, or public benchmark is used.",
    "Source-reported/upstream-reported scores are provenance only and are never reproduced, pooled, or qualified here.",
    "The synthetic control is structural accounting only; it performs no VAD and is never PulseVAD output.",
    "No provider, descriptor, registry, default, installed v0 path, shared build, CI, board, handoff, or release changed.",
    "Missing or unapproved runtime/assets/rights never qualify the candidate; decision remains DEFER.",
)
ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "pinned_source_revision", "required": True, "status": "absent", "notes": "Exact upstream PulseVAD source revision with reviewed license text and per-file digests; no local checkout is pinned."},
    {"id": "exact_runtime_or_asset", "path": MISSING_RUNTIME_PATH, "required": True, "status": "absent", "notes": "Approved runtime or exact ONNX/TorchScript/C asset for the target platform with SHA-256 and execution contract; none present."},
    {"id": "model_weights_identity", "path": MISSING_ASSET_PATH, "required": True, "status": "absent", "notes": "Exact model/weight/graph identity, byte count, SHA-256, and interface contract; none pinned locally."},
    {"id": "source_license_and_terms", "required": True, "status": "absent", "notes": "Reviewed upstream license/redistribution/notice terms for code and assets; claim is not accepted as evidence."},
    {"id": "rights_record", "path": RIGHTS_RECORD_PATH, "required": True, "status": "absent"},
    {"id": "held_out_cohort", "path": COHORT_MANIFEST_PATH, "required": True, "status": "absent", "notes": "Rights-cleared, label-complete held-out cohort with frozen outputs and stratified analysis scoring."},
    {"id": "parity_or_reference_outputs", "path": PARITY_MANIFEST_PATH, "required": True, "status": "absent"},
)
EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "source_revision_unpinned", "state": "absent", "requirement": "Provide an exact reviewed PulseVAD source revision with immutable commit, license text, and per-file digests; no local pinned source exists."},
    {"id": "runtime_or_asset_absent", "state": "absent", "requirement": "Provide an approved runtime or exact ONNX/TorchScript/C asset with platform, version, SHA-256, and execution contract; no runtime/asset is present."},
    {"id": "weights_or_graph_unpinned", "state": "absent", "requirement": "Provide exact model/weight/graph identity with SHA-256, byte count, and input/output contract; no pinned local artifact exists."},
    {"id": "rights_and_redistribution_uncleared", "state": "absent", "requirement": "Clear code/model/data/output redistribution and usage rights before any integration or distribution."},
    {"id": "held_out_cohort_absent", "state": "absent", "requirement": "Provide a rights-cleared, label-complete held-out cohort with frozen candidate outputs and stratified analysis scoring; no cohort is present."},
    {"id": "parity_and_quality_absent", "state": "absent", "requirement": "Produce approved reference/parity outputs and analysis-profile quality evidence against the exact runtime; no local output exists."},
    {"id": "timing_and_target_unmeasured", "state": "absent", "requirement": "Measure paced target-device timing/resources including the 200 ms window buffering floor under an approved runtime; no timing evidence exists."},
    {"id": "provider_intake_not_started", "state": "absent", "requirement": "Complete opt-in external-adapter/provider intake, descriptor/registry review, and independent public-surface/release decision before any exposure; this package makes no such change."},
)
GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_and_license", "An exact reviewed PulseVAD source revision, license text, and redistribution terms are pinned for intended use."),
    ("artifact_identity_and_rights", "Exact runtime/model/graph artifacts or immutable identifiers, SHA-256 where distributable, and rights/redistribution records are complete."),
    ("held_out_cohort_and_labels", "A rights-cleared, label-complete held-out cohort with frozen outputs is available for analysis-profile scoring."),
    ("exact_reference_or_parity_evidence", "Approved reference/parity outputs are captured from the exact runtime/configuration on frozen inputs."),
    ("analysis_profile_quality", "Timestamped probabilities/events, onset/offset, stratified FP/FN, validity separation, and state/interval integrity are scored on the held-out cohort."),
    ("paced_target_timing", "Paced target-device timing/resources and availability, including 200 ms window buffering implications, are measured independently of compute speed."),
    ("opt_in_adapter_intake", "Explicit opt-in adapter/provider intake, descriptor/registry review, and independent public-surface decision are complete."),
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
    "upstream_name": UPSTREAM_NAME,
    "upstream_vendor": UPSTREAM_VENDOR,
    "repo_url": UPSTREAM_REPO_URL,
    "license_summary": UPSTREAM_LICENSE_SUMMARY,
    "discovery_finding": "reports/vad-research/attempt-discovery-20261028-01/findings.md records PulseVAD as potentially runnable but not implemented/tested, with a 200 ms window buffering floor and unpinned revision/assets.",
    "neural_assessment": "reports/vad-research/attempt-neural-01/assessment.md records no local model/dependency and treats author-reported numbers as unverified.",
    "open_models_assessment": "reports/vad-research/attempt-open-models-20261028-01/assessment.md records no local package/graph and requires pinning revision/hash/dependencies before use.",
    "candidate_matrix": "research/voice-enhancement-20261101/candidate_matrix.csv row 8 lists PulseVAD as unavailable/blocked with no exact weights, source checkout, or adapter staged.",
    "notes": "Upstream/source-reported scores and claims are not reproduced, not pooled, and not used as qualification evidence.",
}
ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty", "pcm_not_sequence", "pcm_none", "pcm_wrong_rate", "pcm_stereo",
    "pcm_nan", "pcm_pos_inf", "pcm_neg_inf", "pcm_out_of_range", "pcm_bool", "pcm_string",
    "manifest_not_object", "manifest_missing_field", "manifest_extra_field", "manifest_relative_path",
    "manifest_bad_sha", "manifest_wrong_variant", "manifest_missing_asset", "manifest_missing_directory",
    "manifest_hash_mismatch",
)
CALLER_ASSET_FIELDS = (
    "channels", "config_path", "config_sha256", "model_path", "model_sha256",
    "rights_record_path", "rights_record_sha256", "runtime_path", "source_revision",
    "terms_record_path", "terms_record_sha256", "variant")
CALLER_FILE_PAIRS = (
    ("config_path", "config_sha256"), ("model_path", "model_sha256"),
    ("rights_record_path", "rights_record_sha256"), ("terms_record_path", "terms_record_sha256"))
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_DIR_FIELDS = ("runtime_path",)
CALLER_VARIANT = "caller_supplied_pulsevad_reference"
PCM_SAMPLE_CAP = 10_000_000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3


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
    return {
        "runtime_present": (SOURCE_ROOT / MISSING_RUNTIME_PATH).exists(),
        "asset_present": (SOURCE_ROOT / MISSING_ASSET_PATH).exists(),
        "rights_record_present": (SOURCE_ROOT / RIGHTS_RECORD_PATH).is_file(),
        "cohort_manifest_present": (SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file(),
        "parity_manifest_present": (SOURCE_ROOT / PARITY_MANIFEST_PATH).is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(not item["exists"] for item in probes),
        "approved_runtime_available": False,
        "source_revision_pinned": False,
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
    state = 0x50564D31
    for index in range(CONTROL_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 61, 0.22) + 0.008 * noise)
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
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int) or channels != CONTROL_CHANNELS:
        raise Reject("manifest channels mismatch")
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise Reject("manifest source_revision must be a 40-hex commit")
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
        "channels": CONTROL_CHANNELS, "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes, "runtime_executed": False,
    }


def _shape_only_manifest() -> Dict[str, Any]:
    root = "/nonexistent/pulsevad-fixture"
    digest = "0" * 64
    return {
        "channels": CONTROL_CHANNELS,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "model_path": root + "/pulsevad.onnx",
        "model_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_path": root + "/runtime",
        "source_revision": "0" * 40,
        "terms_record_path": root + "/terms.json",
        "terms_record_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    assignments = {
        "config_path": HERE / "README.md" if (HERE / "README.md").is_file() else HERE / "reference.py",
        "model_path": HERE / "reference.py",
        "rights_record_path": HERE / "run.py" if (HERE / "run.py").is_file() else HERE / "reference.py",
        "terms_record_path": HERE / "verify.py" if (HERE / "verify.py").is_file() else HERE / "reference.py",
    }
    manifest: Dict[str, Any] = {
        "channels": CONTROL_CHANNELS,
        "runtime_path": str(SDK_ROOT),
        "source_revision": "0" * 40,
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
        ("manifest_missing_asset", lambda: validate_caller_manifest(dict(existing, model_path="/nonexistent/pulsevad.onnx"))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(dict(existing, runtime_path="/nonexistent/runtime"))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(dict(existing, model_sha256="0" * 64))),
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
        "plan_source": "caller_supplied_synthetic_structural_accounting_not_pulsevad_output",
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
            "declared_output_kind": "vad_probability_or_event_per_window",
            "vad_performed": False,
            "note": "Declared shape accounting only. No PulseVAD runtime, model, probability, event, or timing is produced.",
        },
        "adverse": adverse,
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": ["pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": ["pcm_bool", "pcm_string", "pcm_out_of_range", "pcm_wrong_rate", "pcm_stereo", "manifest_wrong_variant"],
            "missing_rejected": ["pcm_empty", "pcm_none", "pcm_not_sequence", "manifest_missing_field", "manifest_missing_asset", "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "qualification_effect": "none",
        "note": "Synthetic structural control only. It performs no VAD, is not PulseVAD output, not real audio, not quality/timing evidence, and cannot qualify the candidate.",
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
            "reason": "No pinned PulseVAD source, exact runtime/weights, rights-cleared cohort, parity, or paced timing evidence is present; no qualifying result exists.",
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
            "repo_url": UPSTREAM_REPO_URL,
            "license_summary": UPSTREAM_LICENSE_SUMMARY,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["absence_probes"],
        "caller_asset_contract": {
            "contract_id": "audio-sdk/pulsevad/caller-supplied-reference/0.1",
            "runtime_is_caller_owned": True,
            "runtime_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_absolute_paths_sha256_and_revision_without_execution; do_not_import_or_execute_in_this_package",
            "required_fields": list(CALLER_ASSET_FIELDS),
            "required_variant": CALLER_VARIANT,
            "notes": "Runtime/model/config/rights/terms files must exist at absolute paths with matching SHA-256 and a 40-hex source_revision before any future processing. No execution occurs in this package.",
        },
        "analysis_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in profile_items],
            "real_runtime_metrics": None,
            "note": "Structural controls pass, but no pinned PulseVAD source/runtime/weights, rights-cleared cohort, parity, or paced timing exists; analysis profile is not satisfied for qualification.",
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


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
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
