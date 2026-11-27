# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local x-vector-speaker-embeddings blocker evidence.

Stdlib-only, deterministic, fail-closed. No model, weights, runtime, audio,
corpus, listening, timing, benchmark, or release claim. Missing evidence never
qualifies.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-X-VECTOR-SPEAKER-EMBEDDINGS"
COMPONENT_ID = "x-vector-speaker-embeddings"
TASK_TITLE = "X-vector speaker embeddings"
CONTRACT_ID = "audio-sdk/x-vector-speaker-embeddings-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "spatial"
PROFILE_LABEL = "Spatial"
MODE = "feasibility"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-X-VECTOR-SPEAKER-EMBEDDINGS"
WRITE_SCOPE = "docs/task-evidence/x-vector-speaker-embeddings/ only"
TASK_PREFIX = "docs/task-evidence/x-vector-speaker-embeddings/"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research/category_registry.json").is_file():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
}

BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {"id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": []},
    {"id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": []},
    {"id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"]},
)

ABSENCE_PROBES = (
    "research/x-vector-speaker-embeddings",
    "research/xvector-speaker-embeddings",
    "research/speaker-embeddings/x-vector",
    "data/checkouts/x-vector-speaker-embeddings",
    "data/models/x-vector-speaker-embeddings",
    "data/assets/x-vector-speaker-embeddings",
    "third_party/x-vector-speaker-embeddings",
    "adapters/x-vector-speaker-embeddings",
    "docs/task-evidence/x-vector-speaker-embeddings/weights",
    "docs/task-evidence/x-vector-speaker-embeddings/runtime",
    "docs/task-evidence/x-vector-speaker-embeddings/assets",
    "docs/task-evidence/x-vector-speaker-embeddings/model",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--speechbrain--spkrec-xvect-voxceleb",
    "~/.cache/torch/hub/checkpoints/xvector",
)

PROFILE_PHRASES = (
    "Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions.",
    "Compare localization/activity/extraction with task-matched held-out labels.",
    "Report leakage, target damage, channel loss, and changes in room/reference conditions.",
)

REQUIRED_ARTIFACTS = (
    {"id": "ART-01", "kind": "exact_model_source_and_revision", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Exact x-vector speaker embedding upstream source at a reviewed immutable revision with LICENSE/NOTICE and archive digest."},
    {"id": "ART-02", "kind": "pinned_weights_or_checkpoint", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Immutable x-vector checkpoint/weights with filename, byte count, SHA-256, format and declared embedding geometry."},
    {"id": "ART-03", "kind": "pinned_runtime", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Locked offline runtime with install digest, deterministic settings, fixed seed and recorded host profile."},
    {"id": "ART-04", "kind": "rights_and_terms_review", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Reviewed source/weight/output terms covering attribution, redistribution, commercial use and speaker-data consent."},
    {"id": "ART-05", "kind": "rights_cleared_cohort", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Rights-cleared frozen cohort with separate speaker roles, enrollment/verification geometry, consent and score-calibration labels."},
    {"id": "ART-06", "kind": "approved_reference_parity_and_protocol", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Approved reference parity vectors and Spatial-profile quality/timing protocol with agreed margins, baselines and calibration."},
)

EXACT_BLOCKERS = (
    {"id": "BLK-01", "artifact_id": "ART-01", "status": "open", "qualifies": False, "statement": "No exact reviewed x-vector speaker embedding source, immutable revision, LICENSE/NOTICE bundle or archive digest is present in workspace.", "required_action": "Supply exact upstream source at an immutable reviewed revision with LICENSE/NOTICE and archive digest.", "linked_gates": ["RG-01"]},
    {"id": "BLK-02", "artifact_id": "ART-02", "status": "open", "qualifies": False, "statement": "No exact checkpoint/weights, filename, byte count, SHA-256, format or embedding geometry is present.", "required_action": "Supply immutable checkpoint/weights with exact digests, format and declared geometry.", "linked_gates": ["RG-02"]},
    {"id": "BLK-03", "artifact_id": "ART-03", "status": "open", "qualifies": False, "statement": "No pinned offline runtime, install digest, deterministic settings or host profile is present.", "required_action": "Supply locked offline runtime with install digest, deterministic settings, fixed seed and host profile.", "linked_gates": ["RG-04"]},
    {"id": "BLK-04", "artifact_id": "ART-04", "status": "open", "qualifies": False, "statement": "No reviewed rights/terms decision is staged for source, weights, speaker data or output use.", "required_action": "Record reviewed attribution, redistribution, commercial and output-use terms with speaker-data consent boundaries.", "linked_gates": ["RG-03", "RG-05"]},
    {"id": "BLK-05", "artifact_id": "ART-05", "status": "open", "qualifies": False, "statement": "No rights-cleared frozen speaker cohort, role separation, enrollment/verification geometry or score-calibration labels are present.", "required_action": "Supply rights-cleared frozen cohort with separate roles, consent, geometry, calibration labels and controls.", "linked_gates": ["RG-06", "RG-07"]},
    {"id": "BLK-06", "artifact_id": "ART-06", "status": "open", "qualifies": False, "statement": "No approved reference parity vectors or Spatial-profile protocol is present.", "required_action": "Supply approved parity vectors and independent Spatial-profile protocol with agreed margins and baselines.", "linked_gates": ["RG-07", "RG-08"]},
)

RELEASE_GATES = (
    {"id": "RG-01", "title": "Source revision and license provenance", "status": "blocked", "qualifies": False, "reopen_condition": "Exact source, immutable reviewed revision, LICENSE/NOTICE and archive digest are supplied and reviewed."},
    {"id": "RG-02", "title": "Checkpoint identity and geometry", "status": "blocked", "qualifies": False, "reopen_condition": "Immutable checkpoint/weights with filename, byte count, SHA-256, format and embedding geometry are supplied and verified offline."},
    {"id": "RG-03", "title": "Rights and output terms", "status": "blocked", "qualifies": False, "reopen_condition": "Reviewed source/weight/data/output terms settle attribution, redistribution, commercial, consent and output use."},
    {"id": "RG-04", "title": "Pinned runtime and deterministic load", "status": "blocked", "qualifies": False, "reopen_condition": "Locked offline runtime with install digest loads pinned assets deterministically with fixed seed and recorded host profile."},
    {"id": "RG-05", "title": "Consent, reference availability and output use", "status": "blocked", "qualifies": False, "reopen_condition": "Signed consent, reference-availability, output-use and commercial-terms records exist for every required input/output use."},
    {"id": "RG-06", "title": "Frozen cohort and controls", "status": "blocked", "qualifies": False, "reopen_condition": "Rights-cleared frozen cohort with separate roles, geometry, calibration labels, strata and controls is supplied."},
    {"id": "RG-07", "title": "Separate spatial quality and timing", "status": "blocked", "qualifies": False, "reopen_condition": "Approved protocol produces reviewed verification/embedding, leakage/damage, calibration and timing on frozen strata."},
    {"id": "RG-08", "title": "Independent review and release boundary", "status": "blocked", "qualifies": False, "reopen_condition": "Exact-head independent review confirms no default/ABI/shared-build/CI/provider/registry change and no unqualified release claim."},
)

SPATIAL_PROFILE_ROWS = (
    {"id": "SP-01", "requirement": PROFILE_PHRASES[0], "status": "blocked", "evidence": "No geometry, layout, timestamp calibration, source/target/reference conditions or permissions record is present."},
    {"id": "SP-02", "requirement": PROFILE_PHRASES[1], "status": "blocked", "evidence": "No task-matched held-out labels or localization/activity/extraction comparison is present."},
    {"id": "SP-03", "requirement": PROFILE_PHRASES[2], "status": "blocked", "evidence": "No leakage, target damage, channel loss or room/reference condition change result is present."},
)

QUALITY_OUTCOME_ROWS = (
    {"id": "QO-01", "outcome": "speaker verification/embedding quality", "status": "blocked", "value": None, "evidence": "No qualified embedding or verification result."},
    {"id": "QO-02", "outcome": "separate roles and score calibration", "status": "blocked", "value": None, "evidence": "No role-separated cohort or calibration scoring result."},
    {"id": "QO-03", "outcome": "leakage/target damage/channel loss", "status": "blocked", "value": None, "evidence": "No spatial/damage scoring result."},
    {"id": "QO-04", "outcome": "validity separated from nonspeech", "status": "blocked", "value": None, "evidence": "No validity-aware scoring result."},
)

TIMING_ROWS = (
    {"id": "TR-01", "metric": "exact source intervals/geometry mapping", "status": "blocked", "value": None, "evidence": "No run, interval map or geometry record."},
    {"id": "TR-02", "metric": "availability/dropped/stale events", "status": "blocked", "value": None, "evidence": "No availability, deadline, dropped or stale event measurement."},
    {"id": "TR-03", "metric": "device timing/resources", "status": "blocked", "value": None, "evidence": "No target-device paced run, CPU/memory or deadline data."},
    {"id": "TR-04", "metric": "independent state/reset behavior", "status": "blocked", "value": None, "evidence": "No independent-state or reset verification exists."},
)

NON_CLAIMS = (
    "No x-vector speaker embedding source, checkpoint, runtime, embedding output, verification score or calibrated result is bundled.",
    "No model was imported, built, loaded, executed, downloaded or benchmarked.",
    "No audio was read, decoded, played, listened to or scored.",
    "No verification, embedding quality, calibration, leakage, target-damage, timing, device-resource, benchmark or release result exists.",
    "No consent, reference-availability or output-use clearance is asserted.",
    "No provider was registered, enabled by default, described in a registry or exposed through installed-v0, an ABI, the shared build or CI.",
    "Category-registry mention is not evidence for this exact candidate implementation.",
    "Missing or blocked evidence does not qualify this component.",
)

ADMISSION_SCHEMA = {
    "manifest_schema_id": "audio-sdk/x-vector-speaker-embeddings-qualification/0.1",
    "policy": "task_local_fail_closed_admission_not_runtime_behavior",
    "manifest_fields": ["schema_id", "cohort_id", "source", "weights", "runtime", "inputs", "controls", "outcomes", "rights"],
    "source_fields": ["revision", "path", "license_id", "license_path", "license_sha256"],
    "weight_fields": ["name", "path", "sha256", "byte_count", "format", "terms_sha256"],
    "runtime_fields": ["python_version", "runtime_name", "runtime_version", "device", "threads", "deterministic_algorithms", "seed", "install_digest"],
    "input_fields": ["id", "path", "sha256", "sample_rate_hz", "channels", "frame_count", "label_path", "label_sha256", "consent_id", "rights_reference"],
    "control_fields": ["id", "kind", "input_id", "input_sha256"],
    "outcome_fields": ["embedding_count", "embedding_dim", "verification_eer", "calibration_ece", "leakage_score", "target_damage_score", "nonfinite_count", "sample_count", "output_sample_rate_hz"],
    "rights_fields": ["consent_reference", "input_availability", "output_use", "commercial_terms_review", "terms_review", "baseline_protocol"],
    "weight_formats": ["pytorch_state_dict", "safetensors", "onnx", "torchscript"],
    "weight_suffixes": [".pt", ".pth", ".safetensors", ".onnx"],
    "control_kinds": ["matched_baseline", "mismatched_condition", "zero_input"],
    "input_sample_rates_hz": [16000],
    "output_sample_rates_hz": [16000],
    "required_weight_token": "xvector",
    "python_version_pattern": r"^3\.(10|11|12|13)\.[0-9]+$",
    "runtime_names": ["torch", "onnxruntime", "speechbrain-torch"],
    "device": "cpu",
    "max_threads": 64,
    "max_seed": 2147483647,
    "max_weight_bytes": 32 * 1024 * 1024 * 1024,
    "max_frame_count": 10_000_000,
    "max_embedding_count": 1_000_000,
    "model_executed": False,
    "weights_loaded": False,
    "feature_input_read": False,
    "audio_read": False,
    "network_used": False,
}

REQUIRED_RESULTS = {
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "reference_consent_present": False,
    "quality_result_present": False,
    "spatial_result_present": False,
    "verification_result_present": False,
    "calibration_result_present": False,
    "leakage_damage_result_present": False,
    "availability_result_present": False,
    "device_timing_result_present": False,
    "benchmark_result_present": False,
    "listening_result_present": False,
    "release_claim": False,
    "no_result_qualifies": True,
}

SCOPE = {
    "task_local_only": True,
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "model_executed": False,
    "weights_loaded": False,
    "audio_read": False,
    "feature_input_read": False,
    "network_used": False,
    "download_attempted": False,
    "quality_scored": False,
    "spatial_scored": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "real_corpus": False,
    "release_claim": False,
}

BOUNDARY = {
    "task_local_only": True,
    "provider_registration": False,
    "default_selected": False,
    "enabled_by_default": False,
    "processor_exposure": False,
    "descriptor_registry_change": False,
    "public_api_abi_change": False,
    "installed_v0_behavior_change": False,
    "shared_cmakelists_change": False,
    "ci_workflow_change": False,
    "real_weights_or_runtime": False,
    "listening": False,
    "files_outside_task_directory_written": False,
}

QUALIFICATION = {
    "status": "not_qualified",
    "not_qualified": True,
    "readiness": "incomplete",
    "real_result_present": False,
    "all_release_gates_blocked": True,
    "exact_model_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "spatial_result": False,
    "verification_result": False,
    "calibration_result": False,
    "leakage_damage_result": False,
    "availability_result": False,
    "device_timing_result": False,
    "benchmark_result": False,
    "listening_result": False,
    "release_claim": False,
    "missing_result_promoted": False,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    body = dict(report)
    body.pop("report_sha256", None)
    text = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_strict_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    value, index = decoder.raw_decode(text)
    if text[index:].strip():
        raise ValueError("trailing_content")
    reject_nonfinite(value)
    return value


def reject_nonfinite(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            reject_nonfinite(child)
        return
    if isinstance(value, list):
        for child in value:
            reject_nonfinite(child)
        return
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("nonfinite")


def source_path(relative: str) -> Path:
    return AUDIO_ROOT / relative


def boundary_path(relative: str) -> Path:
    return WORKTREE / relative


def board_row_identity() -> dict[str, Any]:
    board = read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = board.get("tasks", []) if isinstance(board, dict) else []
    for row in rows:
        if isinstance(row, dict) and row.get("id") == TASK:
            projection = {field: row.get(field) for field in BOARD_ROW_FIELDS}
            return {
                "projection": projection,
                "sha256": object_digest(projection),
                "board_file_pinned": False,
                "board_status_gates_anything": False,
                "gating": "stable_identity_only",
                "linked_rows": [dict(r) for r in LINKED_ROWS],
                "linked_rows_sha256": object_digest([dict(r) for r in LINKED_ROWS]),
            }
    raise RuntimeError("board_row_missing:" + TASK)


def probe_absence() -> dict[str, Any]:
    probes = []
    for relative in ABSENCE_PROBES:
        workspace_path = AUDIO_ROOT / relative
        worktree_path = WORKTREE / relative
        probes.append({"path": relative, "present": workspace_path.exists() or worktree_path.exists(), "searched_workspace": True, "searched_sdk_worktree": True})
    home_probes = []
    for raw in HOME_ABSENCE_PROBES:
        expanded = Path(os.path.expanduser(raw))
        home_probes.append({"path": raw, "present": expanded.exists(), "searched_home_cache": True})
    present = [p["path"] for p in probes + home_probes if p["present"]]
    return {
        "probes": probes,
        "home_probes": home_probes,
        "summary": {
            "all_probes_absent": len(present) == 0,
            "present_count": len(present),
            "present_paths": present,
            "probe_count": len(probes) + len(home_probes),
            "workspace_probe_count": len(probes),
            "home_probe_count": len(home_probes),
            "download_attempted": False,
            "network_used": False,
            "recursive_workspace_walk": False,
            "model_executed": False,
            "weights_loaded": False,
            "audio_read": False,
            "feature_input_read": False,
            "source_or_runtime_imported": False,
        },
    }


# --- git scope helpers (newest merge-base; fail closed) ---

def _git_scope(worktree: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *arguments], capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git_scope(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path, refs: tuple[str, ...] = ("origin/main", "main")) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git_scope(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None or (best != base and _git_scope(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0):
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git_scope(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def _reject(code: str, field: str, case_id: str) -> dict[str, Any]:
    return {"id": case_id, "status": "rejected", "code": code, "field": field, "qualifies": False, "state_unchanged": True}


def _is_hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % length, value) is not None


def _is_slug(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", value) is not None


def _is_canonical_abs(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("/") or "\x00" in value:
        return False
    parts = [p for p in value.split("/") if p]
    return value == "/" + "/".join(parts)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def valid_manifest() -> dict[str, Any]:
    return {
        "schema_id": ADMISSION_SCHEMA["manifest_schema_id"],
        "cohort_id": "x-vector-speaker-embeddings-synthetic-control",
        "source": {
            "revision": "0123456789abcdef0123456789abcdef01234567",
            "path": "/opt/x-vector-speaker-embeddings",
            "license_id": "Apache-2.0",
            "license_path": "/opt/x-vector-speaker-embeddings/LICENSE",
            "license_sha256": "0" * 64,
        },
        "weights": [{
            "name": "xvector-embedding.pt",
            "path": "/opt/x-vector-speaker-embeddings/xvector-embedding.pt",
            "sha256": "1" * 64,
            "byte_count": 1024,
            "format": "pytorch_state_dict",
            "terms_sha256": "2" * 64,
        }],
        "runtime": {
            "python_version": "3.12.3",
            "runtime_name": "torch",
            "runtime_version": "2.4.1",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
            "seed": 0,
            "install_digest": "3" * 64,
        },
        "inputs": [
            {"id": "in-001", "path": "/data/in-001.wav", "sha256": "4" * 64, "sample_rate_hz": 16000, "channels": 1, "frame_count": 16000, "label_path": "/data/in-001.json", "label_sha256": "5" * 64, "consent_id": "consent-a", "rights_reference": "rights-a"},
            {"id": "in-002", "path": "/data/in-002.wav", "sha256": "6" * 64, "sample_rate_hz": 16000, "channels": 1, "frame_count": 16000, "label_path": "/data/in-002.json", "label_sha256": "7" * 64, "consent_id": "consent-b", "rights_reference": "rights-b"},
        ],
        "controls": [
            {"id": "c-match", "kind": "matched_baseline", "input_id": "in-001", "input_sha256": "4" * 64},
            {"id": "c-mismatch", "kind": "mismatched_condition", "input_id": "in-002", "input_sha256": "6" * 64},
            {"id": "c-zero", "kind": "zero_input", "input_id": None, "input_sha256": None},
        ],
        "outcomes": {
            "embedding_count": 2,
            "embedding_dim": 512,
            "verification_eer": 0.1,
            "calibration_ece": 0.05,
            "leakage_score": 0.0,
            "target_damage_score": 0.0,
            "nonfinite_count": 0,
            "sample_count": 16000,
            "output_sample_rate_hz": 16000,
        },
        "rights": {
            "consent_reference": "consent://signed",
            "input_availability": "rights-cleared",
            "output_use": "evaluation-only",
            "commercial_terms_review": "reviewed",
            "terms_review": "reviewed",
            "baseline_protocol": "approved-spatial-protocol",
        },
    }


def validate_manifest(manifest: Any) -> tuple[bool, str, str]:
    if not isinstance(manifest, dict):
        return False, "manifest_not_object", ""
    expected_fields = set(ADMISSION_SCHEMA["manifest_fields"])
    if set(manifest.keys()) != expected_fields:
        for field in ADMISSION_SCHEMA["manifest_fields"]:
            if field not in manifest:
                return False, "missing_field", field
        extra = sorted(set(manifest.keys()) - expected_fields)
        return False, "unknown_field", extra[0] if extra else ""
    if manifest["schema_id"] != ADMISSION_SCHEMA["manifest_schema_id"]:
        return False, "invalid_schema", "schema_id"
    if not isinstance(manifest["cohort_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", manifest["cohort_id"]):
        return False, "invalid_value", "cohort_id"

    source = manifest["source"]
    if not isinstance(source, dict) or set(source.keys()) != set(ADMISSION_SCHEMA["source_fields"]):
        for f in ADMISSION_SCHEMA["source_fields"]:
            if not isinstance(source, dict) or f not in source:
                return False, "missing_field", f"source.{f}"
        extra = sorted(set(source.keys()) - set(ADMISSION_SCHEMA["source_fields"]))
        return False, "unknown_field", f"source.{extra[0]}"
    if not _is_hex(source["revision"], 40):
        return False, "invalid_value", "source.revision"
    if not _is_canonical_abs(source["path"]):
        return False, "invalid_path", "source.path"
    if not isinstance(source["license_id"], str) or not source["license_id"]:
        return False, "invalid_value", "source.license_id"
    if not _is_canonical_abs(source["license_path"]):
        return False, "invalid_path", "source.license_path"
    if not _is_hex(source["license_sha256"], 64):
        return False, "invalid_value", "source.license_sha256"

    weights = manifest["weights"]
    if not isinstance(weights, list) or not weights:
        return False, "invalid_value", "weights"
    names = set(); has_token = False
    for item in weights:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["weight_fields"]):
            for f in ADMISSION_SCHEMA["weight_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"weights.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["weight_fields"]))
            return False, "unknown_field", f"weights.{extra[0]}"
        name = item["name"]
        if not _is_slug(name) or name in names:
            return False, "invalid_value", "weights.name"
        names.add(name)
        if ADMISSION_SCHEMA["required_weight_token"] in name:
            has_token = True
        if not any(name.endswith(s) for s in ADMISSION_SCHEMA["weight_suffixes"]):
            return False, "invalid_value", "weights.suffix_required"
        if not _is_canonical_abs(item["path"]):
            return False, "invalid_path", "weights.path"
        if not _is_hex(item["sha256"], 64) or not _is_hex(item["terms_sha256"], 64):
            return False, "invalid_value", "weights.sha256"
        bc = item["byte_count"]
        if not _is_int(bc) or bc < 1 or bc > ADMISSION_SCHEMA["max_weight_bytes"]:
            return False, "invalid_value", "weights.byte_count"
        if item["format"] not in ADMISSION_SCHEMA["weight_formats"]:
            return False, "invalid_value", "weights.format"
    if not has_token:
        return False, "invalid_value", "weights.required_token"

    runtime = manifest["runtime"]
    if not isinstance(runtime, dict) or set(runtime.keys()) != set(ADMISSION_SCHEMA["runtime_fields"]):
        for f in ADMISSION_SCHEMA["runtime_fields"]:
            if not isinstance(runtime, dict) or f not in runtime:
                return False, "missing_field", f"runtime.{f}"
        extra = sorted(set(runtime.keys()) - set(ADMISSION_SCHEMA["runtime_fields"]))
        return False, "unknown_field", f"runtime.{extra[0]}"
    if not isinstance(runtime["python_version"], str) or not re.fullmatch(ADMISSION_SCHEMA["python_version_pattern"], runtime["python_version"]):
        return False, "invalid_value", "runtime.python_version"
    if runtime["runtime_name"] not in ADMISSION_SCHEMA["runtime_names"]:
        return False, "invalid_value", "runtime.runtime_name"
    if not isinstance(runtime["runtime_version"], str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([A-Za-z0-9.+-]*)?", runtime["runtime_version"]):
        return False, "invalid_value", "runtime.runtime_version"
    if runtime["device"] != ADMISSION_SCHEMA["device"]:
        return False, "invalid_value", "runtime.device"
    if not _is_int(runtime["threads"]) or runtime["threads"] < 1 or runtime["threads"] > ADMISSION_SCHEMA["max_threads"]:
        return False, "invalid_value", "runtime.threads"
    if runtime["deterministic_algorithms"] is not True:
        return False, "invalid_value", "runtime.deterministic_algorithms"
    if not _is_int(runtime["seed"]) or runtime["seed"] < 0 or runtime["seed"] > ADMISSION_SCHEMA["max_seed"]:
        return False, "invalid_value", "runtime.seed"
    if not _is_hex(runtime["install_digest"], 64):
        return False, "invalid_value", "runtime.install_digest"

    inputs = manifest["inputs"]
    if not isinstance(inputs, list) or not inputs:
        return False, "invalid_value", "inputs"
    input_index: dict[str, dict[str, Any]] = {}
    for item in inputs:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["input_fields"]):
            for f in ADMISSION_SCHEMA["input_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"inputs.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["input_fields"]))
            return False, "unknown_field", f"inputs.{extra[0]}"
        iid = item["id"]
        if not _is_slug(iid) or iid in input_index:
            return False, "invalid_value", "inputs.id"
        if not _is_canonical_abs(item["path"]) or not _is_canonical_abs(item["label_path"]):
            return False, "invalid_path", "inputs.path"
        if not _is_hex(item["sha256"], 64) or not _is_hex(item["label_sha256"], 64):
            return False, "invalid_value", "inputs.sha256"
        if not _is_int(item["sample_rate_hz"]) or item["sample_rate_hz"] not in ADMISSION_SCHEMA["input_sample_rates_hz"]:
            return False, "invalid_value", "inputs.sample_rate_hz"
        if not _is_int(item["channels"]) or item["channels"] != 1:
            return False, "invalid_value", "inputs.channels"
        if not _is_int(item["frame_count"]) or item["frame_count"] < 1 or item["frame_count"] > ADMISSION_SCHEMA["max_frame_count"]:
            return False, "invalid_value", "inputs.frame_count"
        for f in ("consent_id", "rights_reference"):
            if not isinstance(item[f], str) or not item[f]:
                return False, "invalid_value", f"inputs.{f}"
        input_index[iid] = item

    controls = manifest["controls"]
    if not isinstance(controls, list) or not controls:
        return False, "invalid_value", "controls"
    kinds = set(); cids = set()
    for item in controls:
        if not isinstance(item, dict) or set(item.keys()) != set(ADMISSION_SCHEMA["control_fields"]):
            for f in ADMISSION_SCHEMA["control_fields"]:
                if not isinstance(item, dict) or f not in item:
                    return False, "missing_field", f"controls.{f}"
            extra = sorted(set(item.keys()) - set(ADMISSION_SCHEMA["control_fields"]))
            return False, "unknown_field", f"controls.{extra[0]}"
        cid = item["id"]
        if not _is_slug(cid) or cid in cids:
            return False, "invalid_value", "controls.id"
        cids.add(cid)
        kind = item["kind"]
        if kind not in ADMISSION_SCHEMA["control_kinds"] or kind in kinds:
            return False, "invalid_value", "controls.kind"
        kinds.add(kind)
        if kind == "zero_input":
            if item["input_id"] is not None or item["input_sha256"] is not None:
                return False, "invalid_value", "controls.zero_input"
        else:
            if item["input_id"] not in input_index:
                return False, "invalid_value", "controls.input_id"
            if item["input_sha256"] != input_index[item["input_id"]]["sha256"]:
                return False, "invalid_value", "controls.input_sha256"
    if kinds != set(ADMISSION_SCHEMA["control_kinds"]):
        return False, "invalid_value", "controls.required"

    outcomes = manifest["outcomes"]
    if not isinstance(outcomes, dict) or set(outcomes.keys()) != set(ADMISSION_SCHEMA["outcome_fields"]):
        for f in ADMISSION_SCHEMA["outcome_fields"]:
            if not isinstance(outcomes, dict) or f not in outcomes:
                return False, "missing_field", f"outcomes.{f}"
        extra = sorted(set(outcomes.keys()) - set(ADMISSION_SCHEMA["outcome_fields"]))
        return False, "unknown_field", f"outcomes.{extra[0]}"
    for f in ("verification_eer", "calibration_ece", "leakage_score", "target_damage_score"):
        if not _is_number(outcomes[f]):
            return False, "nonfinite_value" if isinstance(outcomes[f], float) and not math.isfinite(outcomes[f]) else "invalid_value", f"outcomes.{f}"
    for f in ("embedding_count", "embedding_dim", "nonfinite_count", "sample_count", "output_sample_rate_hz"):
        if not _is_int(outcomes[f]) or outcomes[f] < 0:
            return False, "invalid_value", f"outcomes.{f}"
    if outcomes["embedding_count"] < 1 or outcomes["embedding_count"] > ADMISSION_SCHEMA["max_embedding_count"]:
        return False, "invalid_value", "outcomes.embedding_count"
    if outcomes["embedding_dim"] < 1:
        return False, "invalid_value", "outcomes.embedding_dim"
    if outcomes["nonfinite_count"] != 0:
        return False, "invalid_value", "outcomes.nonfinite_count"
    for f in ("verification_eer", "calibration_ece", "leakage_score", "target_damage_score"):
        if not (0.0 <= float(outcomes[f]) <= 1.0):
            return False, "invalid_value", f"outcomes.{f}"
    if outcomes["sample_count"] < 1:
        return False, "invalid_value", "outcomes.sample_count"
    if outcomes["output_sample_rate_hz"] not in ADMISSION_SCHEMA["output_sample_rates_hz"]:
        return False, "invalid_value", "outcomes.output_sample_rate_hz"

    rights = manifest["rights"]
    if not isinstance(rights, dict) or set(rights.keys()) != set(ADMISSION_SCHEMA["rights_fields"]):
        for f in ADMISSION_SCHEMA["rights_fields"]:
            if not isinstance(rights, dict) or f not in rights:
                return False, "missing_field", f"rights.{f}"
        extra = sorted(set(rights.keys()) - set(ADMISSION_SCHEMA["rights_fields"]))
        return False, "unknown_field", f"rights.{extra[0]}"
    for f in ADMISSION_SCHEMA["rights_fields"]:
        if not isinstance(rights[f], str) or not rights[f]:
            return False, "invalid_value", f"rights.{f}"
    return True, "accepted", ""


def admission_cases() -> list[dict[str, Any]]:
    cases = []

    def add(case_id: str, manifest: Any, expected_ok: bool = False):
        ok, code, field = validate_manifest(manifest)
        if expected_ok:
            if ok:
                cases.append({"id": case_id, "status": "accepted_schema_control", "code": "accepted", "field": "", "qualifies": False, "state_unchanged": True, "evidence_class": "synthetic_schema_control_not_evidence"})
            else:
                cases.append({"id": case_id, "status": "rejected", "code": code, "field": field, "qualifies": False, "state_unchanged": True, "unexpected": "expected_accept"})
        else:
            cases.append(_reject(code if code else "invalid_value", field, case_id))

    for i, v in enumerate([[], None, "x", 1, True], 1):
        add(f"root-{i}", v)
    for field in ADMISSION_SCHEMA["manifest_fields"]:
        m = valid_manifest(); m.pop(field); add(f"missing-{field}", m)
    m = valid_manifest(); m["extra"] = 1; add("unknown-top", m)
    m = valid_manifest(); m["schema_id"] = "wrong"; add("wrong-schema", m)
    m = valid_manifest(); m["cohort_id"] = "Bad"; add("bad-cohort", m)
    for field in ADMISSION_SCHEMA["source_fields"]:
        m = valid_manifest(); m["source"].pop(field); add(f"missing-source-{field}", m)
    m = valid_manifest(); m["source"]["revision"] = "abc"; add("bad-revision", m)
    m = valid_manifest(); m["source"]["path"] = "rel"; add("bad-source-path", m)
    m = valid_manifest(); m["source"]["license_sha256"] = "z"*64; add("bad-source-sha", m)
    m = valid_manifest(); m["weights"] = []; add("weights-empty", m)
    for field in ADMISSION_SCHEMA["weight_fields"]:
        m = valid_manifest(); m["weights"][0].pop(field); add(f"missing-weight-{field}", m)
    m = valid_manifest(); m["weights"][0]["name"] = "other.pt"; add("missing-token", m)
    m = valid_manifest(); m["weights"][0]["name"] = "xvector.bin"; add("bad-suffix", m)
    m = valid_manifest(); m["weights"][0]["path"] = "rel.pt"; add("bad-weight-path", m)
    m = valid_manifest(); m["weights"][0]["sha256"] = "g"*64; add("bad-weight-sha", m)
    m = valid_manifest(); m["weights"][0]["byte_count"] = 0; add("bad-weight-bytes", m)
    m = valid_manifest(); m["weights"][0]["format"] = "pickle"; add("bad-weight-format", m)
    for field in ADMISSION_SCHEMA["runtime_fields"]:
        m = valid_manifest(); m["runtime"].pop(field); add(f"missing-runtime-{field}", m)
    m = valid_manifest(); m["runtime"]["python_version"] = "3.9.0"; add("bad-python", m)
    m = valid_manifest(); m["runtime"]["runtime_name"] = "tensorflow"; add("bad-runtime-name", m)
    m = valid_manifest(); m["runtime"]["runtime_version"] = "latest"; add("bad-runtime-version", m)
    m = valid_manifest(); m["runtime"]["device"] = "cuda"; add("bad-device", m)
    m = valid_manifest(); m["runtime"]["threads"] = 0; add("bad-threads", m)
    m = valid_manifest(); m["runtime"]["deterministic_algorithms"] = False; add("bad-deterministic", m)
    m = valid_manifest(); m["runtime"]["seed"] = -1; add("bad-seed", m)
    m = valid_manifest(); m["runtime"]["install_digest"] = "x"; add("bad-install-digest", m)
    m = valid_manifest(); m["inputs"] = []; add("inputs-empty", m)
    for field in ADMISSION_SCHEMA["input_fields"]:
        m = valid_manifest(); m["inputs"][0].pop(field); add(f"missing-input-{field}", m)
    m = valid_manifest(); m["inputs"][0]["path"] = "rel"; add("bad-input-path", m)
    m = valid_manifest(); m["inputs"][0]["sha256"] = "x"; add("bad-input-sha", m)
    m = valid_manifest(); m["inputs"][0]["sample_rate_hz"] = 8000; add("bad-input-rate", m)
    m = valid_manifest(); m["inputs"][0]["channels"] = 2; add("bad-channels", m)
    m = valid_manifest(); m["inputs"][0]["frame_count"] = 0; add("bad-frame-count", m)
    m = valid_manifest(); m["inputs"][0]["consent_id"] = ""; add("bad-consent", m)
    m = valid_manifest(); m["controls"] = []; add("controls-empty", m)
    for field in ADMISSION_SCHEMA["control_fields"]:
        m = valid_manifest(); m["controls"][0].pop(field); add(f"missing-control-{field}", m)
    m = valid_manifest(); m["controls"][0]["kind"] = "bad"; add("bad-control-kind", m)
    m = valid_manifest(); m["controls"][1]["kind"] = "matched_baseline"; add("dup-control-kind", m)
    m = valid_manifest(); m["controls"] = [c for c in m["controls"] if c["kind"] != "zero_input"]; add("missing-zero", m)
    m = valid_manifest(); m["controls"][0]["input_id"] = "missing"; add("bad-control-input", m)
    m = valid_manifest(); m["controls"][0]["input_sha256"] = "0"*64; add("bad-control-sha", m)
    for field in ADMISSION_SCHEMA["outcome_fields"]:
        m = valid_manifest(); m["outcomes"].pop(field); add(f"missing-outcome-{field}", m)
    m = valid_manifest(); m["outcomes"]["embedding_count"] = 0; add("bad-embedding-count", m)
    m = valid_manifest(); m["outcomes"]["embedding_dim"] = 0; add("bad-embedding-dim", m)
    m = valid_manifest(); m["outcomes"]["verification_eer"] = -0.1; add("bad-eer", m)
    m = valid_manifest(); m["outcomes"]["nonfinite_count"] = 1; add("bad-nonfinite", m)
    m = valid_manifest(); m["outcomes"]["sample_count"] = 0; add("bad-sample-count", m)
    m = valid_manifest(); m["outcomes"]["output_sample_rate_hz"] = 8000; add("bad-output-rate", m)
    for field in ADMISSION_SCHEMA["rights_fields"]:
        m = valid_manifest(); m["rights"].pop(field); add(f"missing-rights-{field}", m)
    m = valid_manifest(); m["rights"]["consent_reference"] = ""; add("bad-rights", m)
    add("schema-control", valid_manifest(), expected_ok=True)
    return cases


def admission_summary() -> dict[str, Any]:
    cases = admission_cases()
    rejected = [c for c in cases if c["status"] == "rejected"]
    accepted = [c for c in cases if c["status"] == "accepted_schema_control"]
    control = dict(accepted[0]) if accepted else {}
    if control:
        control["accepted"] = True
        control["checks"] = len(ADMISSION_SCHEMA["manifest_fields"])
    return {
        "cases": cases,
        "control": control,
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted),
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "network_used": False,
            "model_executed": False,
            "weights_loaded": False,
            "audio_read": False,
            "feature_input_read": False,
            "runtime_invoked": False,
        },
    }


def build_contract() -> dict[str, Any]:
    identity = board_row_identity()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "profile_phrases": list(PROFILE_PHRASES),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "not_qualified": True,
            "qualification_status": "not_qualified",
            "promotion": "defer",
            "production_exposure": "DEFER",
            "registered": False,
            "default_enabled": False,
            "expose_as_processor": False,
            "incomplete": True,
            "missing_result_qualifies": False,
        },
        "exact_scope": "Task-local x-vector-speaker-embeddings blocker evidence: source/absence pins, fail-closed Spatial admission, blocked profile accounting and eight blocked release gates. No model, weights, runtime, cohort or result.",
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": identity["projection"],
        "board_row_sha256": identity["sha256"],
        "linked_rows": identity["linked_rows"],
        "linked_rows_sha256": identity["linked_rows_sha256"],
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "network_used": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "required_artifacts": [dict(a) for a in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "release_gates": [dict(g) for g in RELEASE_GATES],
        "spatial_profile_requirements": [dict(r) for r in SPATIAL_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "admission_contract": ADMISSION_SCHEMA,
        "required_results": REQUIRED_RESULTS,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "qualification": QUALIFICATION,
        "non_claims": list(NON_CLAIMS),
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "preserved": True,
            "sdk_compatible": False,
            "model_io_claimed": False,
            "sdk_callback_invoked": False,
        },
        "reproduction": {
            "cold_start_repeats": 3,
            "commands": ["python3 run.py all", "python3 -m unittest -v test_reference.py", "python3 verify.py"],
            "interpreter": "Python 3.12, standard library only",
            "network_required": False,
            "runtime_required": False,
        },
    }


def validate_contract(contract: dict[str, Any]) -> None:
    expected = build_contract()
    if contract != expected:
        raise ValueError("contract_mismatch")


def build_report() -> dict[str, Any]:
    contract = build_contract()
    identity = board_row_identity()
    absence = probe_absence()
    admission = admission_summary()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": contract["disposition"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "required_artifacts": [dict(a) for a in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "gates": [dict(g) for g in RELEASE_GATES],
        "spatial_profile": {"profile": PROFILE_LABEL, "rows": [dict(r) for r in SPATIAL_PROFILE_ROWS]},
        "quality_outcomes": {"rows": [dict(r) for r in QUALITY_OUTCOME_ROWS]},
        "timing": {"rows": [dict(r) for r in TIMING_ROWS]},
        "admission": admission,
        "absence_evidence": absence,
        "source_pins": {k: {"sha256": v, "actual": sha256_file(source_path(k)), "verified": sha256_file(source_path(k)) == v} for k, v in sorted(SOURCE_PINS.items())},
        "boundary_pins": {k: {"sha256": v, "actual": sha256_file(boundary_path(k)), "verified": sha256_file(boundary_path(k)) == v} for k, v in sorted(BOUNDARY_PINS.items())},
        "linked_row_identity": identity,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "qualification": QUALIFICATION,
        "required_results": REQUIRED_RESULTS,
        "non_claims": list(NON_CLAIMS),
        "reproduction": contract["reproduction"],
        "contract_sha256": object_digest(contract),
    }
