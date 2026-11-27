# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic blocker evidence for SDK-YOURTTS.

Stdlib-only, fail-closed. No model, weights, runtime, audio, corpus,
listening, timing, benchmark, or release claim. Missing evidence never
qualifies.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

TASK = "SDK-YOURTTS"
COMPONENT_ID = "yourtts"
TASK_TITLE = "YourTTS"
CONTRACT_ID = "audio-sdk/yourtts-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "feasibility"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-YOURTTS"
WRITE_SCOPE = "docs/task-evidence/yourtts/ only"
TASK_PREFIX = "docs/task-evidence/yourtts/"
REQUIRED_INTERPRETER = "3.12.16"

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
        if board.is_file() and (candidate / "reports").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}

BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
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
    "research/voice-enhancement-20261101/repos/yourtts",
    "research/voice-enhancement-20261101/models/yourtts",
    "research/voice-enhancement-20261101/checkpoints/yourtts",
    "data/checkouts/yourtts",
    "data/models/yourtts",
    "data/assets/yourtts",
    "third_party/yourtts",
    "adapters/yourtts",
    "docs/task-evidence/yourtts/weights",
    "docs/task-evidence/yourtts/runtime",
    "docs/task-evidence/yourtts/assets",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--coqui--XTTS-v2",
    "~/.cache/tts/tts_models--multilingual--multi-dataset--your_tts",
    "~/.local/share/tts/tts_models--multilingual--multi-dataset--your_tts",
)

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker groups.",
    "Preserve text and semantic content, identity/similarity and naturalness as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target condition.",
    "Consent, reference availability and output use are independent gates.",
)

REQUIRED_ARTIFACTS = (
    {"id": "ART-01", "kind": "exact_source_and_revision", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Exact YourTTS source at an immutable reviewed revision with LICENSE/NOTICE and archive digest."},
    {"id": "ART-02", "kind": "pinned_weights_or_checkpoint", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Immutable model/checkpoint assets with filename, byte count, SHA-256, format and declared geometry."},
    {"id": "ART-03", "kind": "pinned_runtime", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Locked offline runtime with install digest, deterministic settings, fixed seed and recorded host profile."},
    {"id": "ART-04", "kind": "rights_and_terms_review", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Reviewed source/weight/model-card/output terms covering attribution, redistribution, commercial and voice/output use."},
    {"id": "ART-05", "kind": "rights_cleared_voice_cohort", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Rights-cleared frozen voice cohort with permitted input, target references, language/speaker groups and transcript/reference metadata."},
    {"id": "ART-06", "kind": "approved_reference_and_protocol", "present": False, "verified": False, "blocked": True, "sha256": None, "requirement": "Approved reference parity/protocol separating content, identity/similarity, naturalness and timing on frozen strata."},
)

EXACT_BLOCKERS = (
    {"id": "BLK-01", "artifact_id": "ART-01", "status": "open", "qualifies": False, "statement": "No exact reviewed YourTTS source, immutable revision, LICENSE/NOTICE bundle or archive digest is present in workspace.", "required_action": "Supply exact upstream source at an immutable reviewed revision with LICENSE/NOTICE and archive digest.", "linked_gates": ["RG-01"]},
    {"id": "BLK-02", "artifact_id": "ART-02", "status": "open", "qualifies": False, "statement": "No exact checkpoint/weights, filename, byte count, SHA-256, format or model geometry is present.", "required_action": "Supply immutable checkpoint/weights with exact digests, format and declared geometry.", "linked_gates": ["RG-02"]},
    {"id": "BLK-03", "artifact_id": "ART-03", "status": "open", "qualifies": False, "statement": "No pinned offline runtime, install digest, deterministic settings or host profile is present.", "required_action": "Supply locked offline runtime with install digest, deterministic settings, fixed seed and host profile.", "linked_gates": ["RG-04"]},
    {"id": "BLK-04", "artifact_id": "ART-04", "status": "open", "qualifies": False, "statement": "No reviewed rights/terms decision is staged for source, weights, model card or output/voice use.", "required_action": "Record reviewed attribution, redistribution, commercial and voice/output-use terms for intended artifacts.", "linked_gates": ["RG-03", "RG-05"]},
    {"id": "BLK-05", "artifact_id": "ART-05", "status": "open", "qualifies": False, "statement": "No rights-cleared frozen voice cohort, target references, consent or language/speaker grouping is present.", "required_action": "Supply rights-cleared frozen cohort with permitted input, target references, task/language/speaker groups and consent records.", "linked_gates": ["RG-05", "RG-06"]},
    {"id": "BLK-06", "artifact_id": "ART-06", "status": "open", "qualifies": False, "statement": "No approved reference parity/protocol or separated content/identity/naturalness/timing evidence is present.", "required_action": "Supply approved protocol and independent matched evidence separating content, identity/similarity, naturalness and timing.", "linked_gates": ["RG-06", "RG-07", "RG-08"]},
)

RELEASE_GATES = (
    {"id": "RG-01", "title": "Source revision and license provenance", "status": "blocked", "qualifies": False, "reopen_condition": "Exact source, immutable reviewed revision, LICENSE/NOTICE and archive digest are supplied and reviewed."},
    {"id": "RG-02", "title": "Checkpoint identity and geometry", "status": "blocked", "qualifies": False, "reopen_condition": "Immutable checkpoint/weights with filename, byte count, SHA-256, format and geometry are supplied and verified offline."},
    {"id": "RG-03", "title": "Rights and output terms", "status": "blocked", "qualifies": False, "reopen_condition": "Reviewed source/weight/model-card/output terms settle attribution, redistribution, commercial and voice/output use."},
    {"id": "RG-04", "title": "Pinned runtime and deterministic load", "status": "blocked", "qualifies": False, "reopen_condition": "Locked offline runtime with install digest loads pinned assets deterministically with fixed seed and recorded host profile."},
    {"id": "RG-05", "title": "Consent, reference availability and output use", "status": "blocked", "qualifies": False, "reopen_condition": "Signed consent, reference-availability, output-use and commercial-terms records exist for every required input/output use."},
    {"id": "RG-06", "title": "Frozen voice cohort and separated outcomes", "status": "blocked", "qualifies": False, "reopen_condition": "Rights-cleared frozen cohort with permitted inputs/targets/groups and separated content/identity/naturalness outcomes is supplied."},
    {"id": "RG-07", "title": "Alignment and timing evidence", "status": "blocked", "qualifies": False, "reopen_condition": "Approved protocol records alignment, first-output/tail timing and exact target condition on frozen strata."},
    {"id": "RG-08", "title": "Independent review and release boundary", "status": "blocked", "qualifies": False, "reopen_condition": "Exact-head independent review confirms no default/ABI/shared-build/CI/provider/registry change and no unqualified release claim."},
)

VOICE_PROFILE_ROWS = (
    {"id": "VP-01", "requirement": PROFILE_PHRASES[0], "status": "blocked", "evidence": "No permitted input, target reference, task, language/speaker group or frozen cohort is present."},
    {"id": "VP-02", "requirement": PROFILE_PHRASES[1], "status": "blocked", "evidence": "No matched output exists; content, identity/similarity and naturalness cannot be separated or scored."},
    {"id": "VP-03", "requirement": PROFILE_PHRASES[2], "status": "blocked", "evidence": "No alignment, first-output/tail timing or exact target condition record exists."},
    {"id": "VP-04", "requirement": PROFILE_PHRASES[3], "status": "blocked", "evidence": "No consent, reference-availability or output-use records are staged."},
)

QUALITY_OUTCOME_ROWS = (
    {"id": "QO-01", "outcome": "text/semantic content preservation", "status": "blocked", "value": None, "evidence": "No qualified converted output or transcript/content comparison exists."},
    {"id": "QO-02", "outcome": "identity/similarity", "status": "blocked", "value": None, "evidence": "No target/reference speaker similarity result exists."},
    {"id": "QO-03", "outcome": "naturalness/accent/prosody", "status": "blocked", "value": None, "evidence": "No independent listening or naturalness scoring exists."},
    {"id": "QO-04", "outcome": "consent/reference/output-use clearance", "status": "blocked", "value": None, "evidence": "No rights, consent or output-use records are staged."},
)

TIMING_ROWS = (
    {"id": "TR-01", "metric": "alignment and exact target condition", "status": "blocked", "value": None, "evidence": "No run, alignment map or exact target condition record exists."},
    {"id": "TR-02", "metric": "first-output/tail timing", "status": "blocked", "value": None, "evidence": "No runtime, stream or timing measurement exists."},
    {"id": "TR-03", "metric": "device timing/resources", "status": "blocked", "value": None, "evidence": "No target-device paced run, CPU/memory or deadline data exists."},
    {"id": "TR-04", "metric": "reset/state isolation", "status": "blocked", "value": None, "evidence": "No runtime state or reset verification exists."},
)

NON_CLAIMS = (
    "No YourTTS source, checkpoint, runtime, converted audio, transcript or quality score is bundled.",
    "No model was imported, built, loaded, executed, downloaded or benchmarked.",
    "No audio was read, decoded, played, listened to or scored.",
    "No voice-conversion quality, identity/similarity, naturalness, accent, latency, device-resource, benchmark or release result exists.",
    "No consent, reference-availability or output-use clearance is asserted.",
    "No provider was registered, enabled by default, described in a registry or exposed through installed-v0, an ABI, the shared build or CI.",
    "Paper/research mentions are context only and are not matched evidence for this task.",
    "Missing or blocked evidence does not qualify this component.",
)

ADMISSION_SCHEMA = {
    "manifest_schema_id": "audio-sdk/yourtts-qualification/0.1",
    "policy": "task_local_fail_closed_admission_not_runtime_behavior",
    "manifest_fields": ["schema_id", "cohort_id", "source", "weights", "runtime", "inputs", "controls", "outcomes", "rights"],
    "source_fields": ["revision", "path", "license_id", "license_path", "license_sha256"],
    "weight_fields": ["name", "path", "sha256", "byte_count", "format", "terms_sha256"],
    "runtime_fields": ["python_version", "runtime_name", "runtime_version", "device", "threads", "deterministic_algorithms", "seed", "install_digest"],
    "input_fields": ["id", "path", "sha256", "sample_rate_hz", "channels", "frame_count", "transcript_path", "transcript_sha256", "target_reference_path", "target_reference_sha256", "consent_id", "rights_reference"],
    "control_fields": ["id", "kind", "input_id", "input_sha256"],
    "outcome_fields": ["output_path", "output_sha256", "content_score", "identity_similarity_score", "naturalness_score", "first_output_ms", "tail_ms", "alignment_verified", "nonfinite_count", "sample_count", "output_sample_rate_hz"],
    "rights_fields": ["consent_reference", "reference_availability", "output_use", "commercial_terms_review", "terms_review", "listening_protocol"],
    "weight_formats": ["pytorch_state_dict", "safetensors", "onnx", "checkpoint_dir_manifest"],
    "weight_suffixes": [".pt", ".pth", ".safetensors", ".onnx", ".json"],
    "control_kinds": ["identity_control", "matched_baseline", "mismatched_condition"],
    "input_sample_rates_hz": [16000, 22050, 24000, 44100, 48000],
    "output_sample_rates_hz": [16000, 22050, 24000, 44100, 48000],
    "required_weight_token": "yourtts",
    "python_version_pattern": r"^3\.(10|11|12|13)\.[0-9]+$",
    "runtime_names": ["torch", "coqui-tts", "onnxruntime"],
    "device": "cpu",
    "max_threads": 64,
    "max_seed": 2147483647,
    "max_weight_bytes": 32 * 1024 * 1024 * 1024,
    "max_frame_count": 100_000_000,
    "max_sample_count": 100_000_000,
    "model_executed": False,
    "weights_loaded": False,
    "audio_read": False,
    "network_used": False,
}

REQUIRED_RESULTS = {
    "exact_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "reference_consent_present": False,
    "content_result_present": False,
    "identity_result_present": False,
    "naturalness_result_present": False,
    "alignment_result_present": False,
    "timing_result_present": False,
    "device_timing_result_present": False,
    "listening_result_present": False,
    "release_claim": False,
    "no_result_qualifies": True,
}

SCOPE = {
    "task_local_only": True,
    "exact_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "model_executed": False,
    "weights_loaded": False,
    "audio_read": False,
    "network_used": False,
    "download_attempted": False,
    "quality_scored": False,
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
    "shared_build_change": False,
    "ci_change": False,
    "board_or_handoff_change": False,
}



class Reject(ValueError):
    """Deterministic fail-closed rejection."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"


def canonical_text(obj: Any) -> str:
    return canonical_bytes(obj).decode("utf-8")


def object_digest(obj: Any) -> str:
    return sha256(canonical_bytes(obj))


def _reject_constant(value: str) -> Any:
    raise Reject(f"non-finite JSON constant: {value}")


def _object_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise Reject(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def strict_json_loads(text: str) -> Any:
    value = json.loads(text, parse_constant=_reject_constant, object_pairs_hook=_object_pairs_hook)
    _walk_finite(value)
    return value


def read_strict_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _walk_finite(value: Any) -> None:
    if isinstance(value, float):
        if not (value == value and abs(value) != float("inf")):
            raise Reject("non-finite float")
    elif isinstance(value, dict):
        for v in value.values():
            _walk_finite(v)
    elif isinstance(value, list):
        for v in value:
            _walk_finite(v)


def board_row_projection(path: Path) -> dict[str, Any]:
    data = read_strict_json(path)
    tasks = data.get("tasks", []) if isinstance(data, dict) else []
    for row in tasks:
        if isinstance(row, dict) and row.get("id") == TASK:
            projection = {k: row.get(k) for k in BOARD_ROW_FIELDS}
            if projection != BOARD_ROW_PROJECTION:
                raise Reject("board row projection drifted from pinned stable identity")
            return projection
    raise Reject("board row not found: " + TASK)


def board_row_identity() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    return {
        "task": TASK,
        "board_path": BOARD_TASK_ROW,
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "mutable_fields_excluded": ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority"],
        "projection": projection,
        "projection_sha256": object_digest(projection),
    }


def _probe(path: Path, *, root: str, label: str, display_path: str) -> dict[str, Any]:
    exists = path.exists()
    kind = "missing"
    if exists:
        if path.is_dir():
            kind = "directory"
        elif path.is_file():
            kind = "file"
        else:
            kind = "other"
    return {"id": label, "root": root, "path": display_path, "exists": exists, "kind": kind}


def probe_absence() -> dict[str, Any]:
    probes = []
    for rel in ABSENCE_PROBES:
        probes.append(_probe(AUDIO_ROOT / rel, root="audio_root", label="audio_root:" + rel, display_path=rel))
        probes.append(_probe(WORKTREE / rel, root="worktree", label="worktree:" + rel, display_path=rel))
    for rel in HOME_ABSENCE_PROBES:
        expanded = Path(os.path.expanduser(rel))
        probes.append(_probe(expanded, root="home", label="home:" + rel, display_path=rel))
    present = [p for p in probes if p["exists"]]
    return {
        "summary": {
            "all_probes_absent": len(present) == 0,
            "present_count": len(present),
            "probe_count": len(probes),
            "download_attempted": False,
            "network_used": False,
            "recursive_workspace_walk": False,
        },
        "probes": probes,
    }


def _is_bool(x: Any) -> bool:
    return isinstance(x, bool)


def _is_int(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _is_non_empty_str(x: Any) -> bool:
    return isinstance(x, str) and bool(x.strip())


def _reject(code: str, detail: str) -> tuple[bool, str, str]:
    return False, code, detail


def valid_manifest() -> dict[str, Any]:
    return {
        "schema_id": ADMISSION_SCHEMA["manifest_schema_id"],
        "cohort_id": "synthetic-schema-control",
        "source": {
            "revision": "deadbeef",
            "path": "source/yourtts",
            "license_id": "Apache-2.0",
            "license_path": "source/LICENSE",
            "license_sha256": "0" * 64,
        },
        "weights": [{
            "name": "yourtts-checkpoint.safetensors",
            "path": "weights/yourtts-checkpoint.safetensors",
            "sha256": "1" * 64,
            "byte_count": 1024,
            "format": "safetensors",
            "terms_sha256": "2" * 64,
        }],
        "runtime": {
            "python_version": "3.12.16",
            "runtime_name": "torch",
            "runtime_version": "2.8.0",
            "device": "cpu",
            "threads": 1,
            "deterministic_algorithms": True,
            "seed": 0,
            "install_digest": "3" * 64,
        },
        "inputs": [{
            "id": "in-1",
            "path": "inputs/in-1.wav",
            "sha256": "4" * 64,
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_count": 16000,
            "transcript_path": "inputs/in-1.txt",
            "transcript_sha256": "5" * 64,
            "target_reference_path": "inputs/ref-1.wav",
            "target_reference_sha256": "6" * 64,
            "consent_id": "consent-1",
            "rights_reference": "rights/consent-1.json",
        }],
        "controls": [{
            "id": "ctrl-1",
            "kind": "identity_control",
            "input_id": "in-1",
            "input_sha256": "4" * 64,
        }],
        "outcomes": {
            "output_path": "out/in-1.wav",
            "output_sha256": "7" * 64,
            "content_score": 0.0,
            "identity_similarity_score": 0.0,
            "naturalness_score": 0.0,
            "first_output_ms": 0.0,
            "tail_ms": 0.0,
            "alignment_verified": False,
            "nonfinite_count": 0,
            "sample_count": 16000,
            "output_sample_rate_hz": 16000,
        },
        "rights": {
            "consent_reference": "rights/consent-1.json",
            "reference_availability": "caller_supplied",
            "output_use": "evaluation_only",
            "commercial_terms_review": "pending",
            "terms_review": "pending",
            "listening_protocol": "pending",
        },
    }


def _require_fields(obj: dict[str, Any], fields: list[str] | tuple[str, ...], ctx: str) -> tuple[bool, str, str] | None:
    if set(obj.keys()) != set(fields):
        return _reject("field_set_mismatch", ctx)
    return None


def _check_sha256(value: Any, ctx: str) -> tuple[bool, str, str] | None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        return _reject("invalid_sha256", ctx)
    return None


def _check_nonneg_number(value: Any, ctx: str) -> tuple[bool, str, str] | None:
    if _is_bool(value) or not isinstance(value, (int, float)):
        return _reject("invalid_value", ctx)
    if isinstance(value, float) and (value != value or abs(value) == float("inf")):
        return _reject("nonfinite_value", ctx)
    if float(value) < 0.0:
        return _reject("invalid_value", ctx)
    return None


def validate_manifest(manifest: Any) -> tuple[bool, str, str]:
    if not isinstance(manifest, dict):
        return _reject("invalid_manifest", "manifest must be object")
    err = _require_fields(manifest, ADMISSION_SCHEMA["manifest_fields"], "manifest")
    if err:
        return err
    if manifest.get("schema_id") != ADMISSION_SCHEMA["manifest_schema_id"]:
        return _reject("schema_mismatch", "schema_id")
    if not _is_non_empty_str(manifest.get("cohort_id")):
        return _reject("invalid_value", "cohort_id")
    source = manifest["source"]
    if not isinstance(source, dict):
        return _reject("invalid_value", "source")
    err = _require_fields(source, ADMISSION_SCHEMA["source_fields"], "source")
    if err:
        return err
    for k in ("revision", "path", "license_id", "license_path"):
        if not _is_non_empty_str(source.get(k)):
            return _reject("invalid_value", f"source.{k}")
    err = _check_sha256(source.get("license_sha256"), "source.license_sha256")
    if err:
        return err

    weights = manifest["weights"]
    if not isinstance(weights, list) or not weights:
        return _reject("invalid_value", "weights")
    for i, w in enumerate(weights):
        if not isinstance(w, dict):
            return _reject("invalid_value", f"weights[{i}]")
        err = _require_fields(w, ADMISSION_SCHEMA["weight_fields"], f"weights[{i}]")
        if err:
            return err
        for k in ("name", "path"):
            if not _is_non_empty_str(w.get(k)):
                return _reject("invalid_value", f"weights[{i}].{k}")
        if ADMISSION_SCHEMA["required_weight_token"] not in str(w.get("name", "")).lower() and ADMISSION_SCHEMA["required_weight_token"] not in str(w.get("path", "")).lower():
            return _reject("invalid_value", f"weights[{i}].name/path")
        err = _check_sha256(w.get("sha256"), f"weights[{i}].sha256")
        if err:
            return err
        err = _check_sha256(w.get("terms_sha256"), f"weights[{i}].terms_sha256")
        if err:
            return err
        bc = w.get("byte_count")
        if not _is_int(bc) or bc <= 0 or bc > ADMISSION_SCHEMA["max_weight_bytes"]:
            return _reject("invalid_value", f"weights[{i}].byte_count")
        fmt = w.get("format")
        if fmt not in ADMISSION_SCHEMA["weight_formats"]:
            return _reject("invalid_value", f"weights[{i}].format")
        suffix = Path(str(w.get("path"))).suffix.lower()
        if suffix not in ADMISSION_SCHEMA["weight_suffixes"]:
            return _reject("invalid_value", f"weights[{i}].suffix")

    runtime = manifest["runtime"]
    if not isinstance(runtime, dict):
        return _reject("invalid_value", "runtime")
    err = _require_fields(runtime, ADMISSION_SCHEMA["runtime_fields"], "runtime")
    if err:
        return err
    pv = runtime.get("python_version")
    if not isinstance(pv, str) or not re.fullmatch(ADMISSION_SCHEMA["python_version_pattern"], pv):
        return _reject("invalid_value", "runtime.python_version")
    if runtime.get("runtime_name") not in ADMISSION_SCHEMA["runtime_names"]:
        return _reject("invalid_value", "runtime.runtime_name")
    if not _is_non_empty_str(runtime.get("runtime_version")):
        return _reject("invalid_value", "runtime.runtime_version")
    if runtime.get("device") != ADMISSION_SCHEMA["device"]:
        return _reject("invalid_value", "runtime.device")
    threads = runtime.get("threads")
    if not _is_int(threads) or threads <= 0 or threads > ADMISSION_SCHEMA["max_threads"]:
        return _reject("invalid_value", "runtime.threads")
    if runtime.get("deterministic_algorithms") is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    seed = runtime.get("seed")
    if not _is_int(seed) or seed < 0 or seed > ADMISSION_SCHEMA["max_seed"]:
        return _reject("invalid_value", "runtime.seed")
    err = _check_sha256(runtime.get("install_digest"), "runtime.install_digest")
    if err:
        return err

    inputs = manifest["inputs"]
    if not isinstance(inputs, list) or not inputs:
        return _reject("invalid_value", "inputs")
    input_ids = set()
    for i, inp in enumerate(inputs):
        if not isinstance(inp, dict):
            return _reject("invalid_value", f"inputs[{i}]")
        err = _require_fields(inp, ADMISSION_SCHEMA["input_fields"], f"inputs[{i}]")
        if err:
            return err
        for k in ("id", "path", "transcript_path", "target_reference_path", "consent_id", "rights_reference"):
            if not _is_non_empty_str(inp.get(k)):
                return _reject("invalid_value", f"inputs[{i}].{k}")
        if inp["id"] in input_ids:
            return _reject("duplicate_id", f"inputs[{i}].id")
        input_ids.add(inp["id"])
        for k in ("sha256", "transcript_sha256", "target_reference_sha256"):
            err = _check_sha256(inp.get(k), f"inputs[{i}].{k}")
            if err:
                return err
        sr = inp.get("sample_rate_hz")
        if not _is_int(sr) or sr not in ADMISSION_SCHEMA["input_sample_rates_hz"]:
            return _reject("invalid_value", f"inputs[{i}].sample_rate_hz")
        ch = inp.get("channels")
        if not _is_int(ch) or ch <= 0:
            return _reject("invalid_value", f"inputs[{i}].channels")
        fc = inp.get("frame_count")
        if not _is_int(fc) or fc <= 0 or fc > ADMISSION_SCHEMA["max_frame_count"]:
            return _reject("invalid_value", f"inputs[{i}].frame_count")

    controls = manifest["controls"]
    if not isinstance(controls, list) or not controls:
        return _reject("invalid_value", "controls")
    for i, c in enumerate(controls):
        if not isinstance(c, dict):
            return _reject("invalid_value", f"controls[{i}]")
        err = _require_fields(c, ADMISSION_SCHEMA["control_fields"], f"controls[{i}]")
        if err:
            return err
        for k in ("id", "input_id"):
            if not _is_non_empty_str(c.get(k)):
                return _reject("invalid_value", f"controls[{i}].{k}")
        if c.get("kind") not in ADMISSION_SCHEMA["control_kinds"]:
            return _reject("invalid_value", f"controls[{i}].kind")
        err = _check_sha256(c.get("input_sha256"), f"controls[{i}].input_sha256")
        if err:
            return err
        if c.get("input_id") not in input_ids:
            return _reject("invalid_reference", f"controls[{i}].input_id")

    outcomes = manifest["outcomes"]
    if not isinstance(outcomes, dict):
        return _reject("invalid_value", "outcomes")
    err = _require_fields(outcomes, ADMISSION_SCHEMA["outcome_fields"], "outcomes")
    if err:
        return err
    for k in ("output_path",):
        if not _is_non_empty_str(outcomes.get(k)):
            return _reject("invalid_value", f"outcomes.{k}")
    err = _check_sha256(outcomes.get("output_sha256"), "outcomes.output_sha256")
    if err:
        return err
    for k in ("content_score", "identity_similarity_score", "naturalness_score", "first_output_ms", "tail_ms"):
        err = _check_nonneg_number(outcomes.get(k), f"outcomes.{k}")
        if err:
            return err
    if not _is_bool(outcomes.get("alignment_verified")):
        return _reject("invalid_value", "outcomes.alignment_verified")
    nf = outcomes.get("nonfinite_count")
    if not _is_int(nf) or nf < 0:
        return _reject("invalid_value", "outcomes.nonfinite_count")
    sc = outcomes.get("sample_count")
    if not _is_int(sc) or sc < 0 or sc > ADMISSION_SCHEMA["max_sample_count"]:
        return _reject("invalid_value", "outcomes.sample_count")
    osr = outcomes.get("output_sample_rate_hz")
    if not _is_int(osr) or osr not in ADMISSION_SCHEMA["output_sample_rates_hz"]:
        return _reject("invalid_value", "outcomes.output_sample_rate_hz")

    rights = manifest["rights"]
    if not isinstance(rights, dict):
        return _reject("invalid_value", "rights")
    err = _require_fields(rights, ADMISSION_SCHEMA["rights_fields"], "rights")
    if err:
        return err
    for k in ADMISSION_SCHEMA["rights_fields"]:
        if not _is_non_empty_str(rights.get(k)):
            return _reject("invalid_value", f"rights.{k}")
    return True, "accepted_schema_control", "synthetic schema control only; no runtime/model execution"


def admission_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    good = valid_manifest()
    ok, code, detail = validate_manifest(good)
    cases.append({"id": "CTRL-01", "kind": "control", "manifest": good, "accepted": ok, "code": code, "detail": detail, "qualifies": False, "evidence_class": "synthetic_schema_control_not_evidence"})

    def bad(case_id: str, mutate, expected: str, detail_text: str) -> None:
        m = valid_manifest()
        mutate(m)
        ok2, code2, _ = validate_manifest(m)
        cases.append({"id": case_id, "kind": "adverse", "accepted": ok2, "code": code2, "detail": detail_text, "qualifies": False, "evidence_class": "adverse_rejection", "expected_code": expected})

    bad("ADV-01", lambda m: m.__setitem__("schema_id", "wrong"), "schema_mismatch", "wrong schema")
    bad("ADV-02", lambda m: m.__delitem__("cohort_id"), "field_set_mismatch", "missing field")
    bad("ADV-03", lambda m: m["source"].__setitem__("revision", ""), "invalid_value", "empty revision")
    bad("ADV-04", lambda m: m["weights"].__setitem__(0, {**m["weights"][0], "sha256": "xyz"}), "invalid_sha256", "bad sha")
    bad("ADV-05", lambda m: m["weights"][0].__setitem__("byte_count", True), "invalid_value", "bool byte_count")
    bad("ADV-06", lambda m: m["weights"][0].__setitem__("byte_count", 0), "invalid_value", "zero byte_count")
    bad("ADV-07", lambda m: m["weights"][0].__setitem__("format", "exe"), "invalid_value", "bad format")
    bad("ADV-08", lambda m: (m["weights"][0].__setitem__("name", "not-matching.pt"), m["weights"][0].__setitem__("path", "weights/not-matching.pt")), "invalid_value", "missing token")
    bad("ADV-09", lambda m: m["runtime"].__setitem__("python_version", "2.7.18"), "invalid_value", "bad python")
    bad("ADV-10", lambda m: m["runtime"].__setitem__("device", "cuda"), "invalid_value", "non-cpu")
    bad("ADV-11", lambda m: m["runtime"].__setitem__("deterministic_algorithms", False), "invalid_value", "non-deterministic")
    bad("ADV-12", lambda m: m["runtime"].__setitem__("seed", -1), "invalid_value", "bad seed")
    bad("ADV-13", lambda m: m["inputs"][0].__setitem__("sample_rate_hz", 8000), "invalid_value", "bad sr")
    bad("ADV-14", lambda m: m["inputs"][0].__setitem__("channels", 0), "invalid_value", "bad channels")
    bad("ADV-15", lambda m: m["inputs"][0].__setitem__("frame_count", 0), "invalid_value", "bad frame_count")
    bad("ADV-16", lambda m: m["controls"][0].__setitem__("kind", "unknown"), "invalid_value", "bad control kind")
    bad("ADV-17", lambda m: m["controls"][0].__setitem__("input_id", "missing"), "invalid_reference", "bad input ref")
    bad("ADV-18", lambda m: m["outcomes"].__setitem__("output_sha256", "1"), "invalid_sha256", "bad output sha")
    bad("ADV-19", lambda m: m["outcomes"].__setitem__("alignment_verified", "yes"), "invalid_value", "bad alignment")
    bad("ADV-20", lambda m: m["outcomes"].__setitem__("nonfinite_count", -1), "invalid_value", "bad nonfinite")
    bad("ADV-21", lambda m: m["rights"].__setitem__("consent_reference", ""), "invalid_value", "missing consent")
    bad("ADV-22", lambda m: m.__setitem__("weights", []), "invalid_value", "empty weights")
    bad("ADV-23", lambda m: m.__setitem__("inputs", []), "invalid_value", "empty inputs")
    bad("ADV-24", lambda m: m.__setitem__("controls", []), "invalid_value", "empty controls")
    # duplicate id
    mdup = valid_manifest(); mdup["inputs"].append({**mdup["inputs"][0], "id": "in-1"}); ok2, code2, _ = validate_manifest(mdup)
    cases.append({"id": "ADV-25", "kind": "adverse", "accepted": ok2, "code": code2, "detail": "duplicate input id", "qualifies": False, "evidence_class": "adverse_rejection", "expected_code": "duplicate_id"})
    # nonfinite float
    mnf = valid_manifest(); mnf["outcomes"]["content_score"] = float("nan")
    try:
        _walk_finite(mnf)
        ok3, code3 = True, "accepted"
    except Reject as e:
        ok3, code3 = False, str(e).split(":")[0]
    # validate_manifest catches bool/number/type but NaN in float passes isinstance check; our check catches it
    ok3, code3, _ = validate_manifest(mnf)
    cases.append({"id": "ADV-26", "kind": "adverse", "accepted": ok3, "code": code3, "detail": "nan score", "qualifies": False, "evidence_class": "adverse_rejection", "expected_code": "nonfinite_value"})

    return cases


def admission_summary() -> dict[str, Any]:
    cases = admission_cases()
    accepted = [c for c in cases if c["accepted"]]
    rejected = [c for c in cases if not c["accepted"]]
    control = next(c for c in cases if c["kind"] == "control")
    return {
        "schema": ADMISSION_SCHEMA,
        "control": {k: control[k] for k in ("id", "accepted", "code", "detail", "qualifies", "evidence_class")},
        "cases": [{k: c[k] for k in ("id", "kind", "accepted", "code", "detail", "qualifies", "evidence_class", "expected_code") if k in c} for c in cases],
        "summary": {
            "case_count": len(cases),
            "accepted_schema_controls": len([c for c in accepted if c["kind"] == "control"]),
            "rejected_count": len(rejected),
            "qualifying_results": 0,
            "all_adverse_rejected": all((not c["accepted"]) for c in cases if c["kind"] == "adverse"),
            "control_accepted_but_not_qualifying": control["accepted"] and not control["qualifies"],
        },
    }


def build_contract() -> dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "required_interpreter": REQUIRED_INTERPRETER,
        "board_file_pinned": False,
        "board_row_identity": board_row_identity(),
        "linked_rows": list(LINKED_ROWS),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "profile_phrases": list(PROFILE_PHRASES),
        "required_artifacts": [dict(x) for x in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(x) for x in EXACT_BLOCKERS],
        "release_gates": [dict(x) for x in RELEASE_GATES],
        "voice_profile_rows": [dict(x) for x in VOICE_PROFILE_ROWS],
        "quality_outcome_rows": [dict(x) for x in QUALITY_OUTCOME_ROWS],
        "timing_rows": [dict(x) for x in TIMING_ROWS],
        "required_results": dict(REQUIRED_RESULTS),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
        "admission": admission_summary(),
        "absence_evidence": probe_absence(),
    }


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "schema_id", "contract_id", "task", "title", "component", "profile", "profile_label", "mode",
        "base_commit", "branch", "write_scope", "task_prefix", "decision", "status", "qualification_status",
        "proposal_only", "required_interpreter", "board_file_pinned", "board_row_identity", "linked_rows",
        "source_pins", "boundary_pins", "profile_phrases", "required_artifacts", "exact_blockers",
        "release_gates", "voice_profile_rows", "quality_outcome_rows", "timing_rows", "required_results",
        "scope", "boundary", "non_claims", "admission", "absence_evidence",
    }
    if set(contract.keys()) != required:
        raise Reject("contract field set mismatch")
    if contract["schema_id"] != CONTRACT_SCHEMA_ID or contract["contract_id"] != CONTRACT_ID:
        raise Reject("contract schema mismatch")
    if contract["decision"] != "DEFER" or contract["status"] != "incomplete" or contract["qualification_status"] != "not_qualified":
        raise Reject("contract disposition mismatch")
    if contract["proposal_only"] is not True or contract["board_file_pinned"] is not False:
        raise Reject("contract proposal/board flags")
    if len(contract["release_gates"]) != 8 or not all(g["status"] == "blocked" and g["qualifies"] is False for g in contract["release_gates"]):
        raise Reject("release gates must be 8 blocked")
    if len(contract["exact_blockers"]) != 6 or not all(b["status"] == "open" and b["qualifies"] is False for b in contract["exact_blockers"]):
        raise Reject("blockers must be 6 open")
    adm = contract["admission"]["summary"]
    if adm["qualifying_results"] != 0 or not adm["all_adverse_rejected"] or not adm["control_accepted_but_not_qualifying"]:
        raise Reject("admission summary not fail-closed")
    if not contract["absence_evidence"]["summary"]["all_probes_absent"]:
        raise Reject("absence probes present")


def build_report() -> dict[str, Any]:
    contract = build_contract()
    validate_contract(contract)
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "required_interpreter": REQUIRED_INTERPRETER,
        "contract_sha256": object_digest(contract),
        "board_row_identity": contract["board_row_identity"],
        "linked_rows": contract["linked_rows"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "profile_phrases": contract["profile_phrases"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "voice_profile": {"profile": PROFILE_LABEL, "rows": contract["voice_profile_rows"]},
        "quality_outcomes": contract["quality_outcome_rows"],
        "timing": contract["timing_rows"],
        "required_results": contract["required_results"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "absence_evidence": contract["absence_evidence"],
        "admission": contract["admission"],
        "qualification": {
            "status": "not_qualified",
            "qualified": False,
            "not_qualified": True,
            "decision": "DEFER",
            "all_release_gates_blocked": True,
            "missing_result_promoted": False,
            "reason": "No exact YourTTS source/checkpoint/runtime, no rights-cleared voice cohort, no consent/reference/output-use clearance, and no separated content/identity/naturalness/timing evidence are present.",
        },
        "non_claims": contract["non_claims"],
    }
    return report


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    text = canonical_text(report)
    return text, sha256(text.encode("utf-8"))
