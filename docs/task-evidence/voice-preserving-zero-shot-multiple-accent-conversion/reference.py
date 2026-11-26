# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Static evidence model for SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION.

This module only describes a strict readiness blocker. It contains no paper
implementation, weight, runtime, audio, vendor response or benchmark result.
All generated files are confined to
docs/task-evidence/voice-preserving-zero-shot-multiple-accent-conversion/.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Iterable

TASK = "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"
TITLE = "Voice-Preserving Zero-Shot Multiple Accent Conversion"
COMPONENT = "voice-preserving-zero-shot-multiple-accent-conversion"
MODE = "feasibility"
BRANCH = "swarm/SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"
BASE_COMMIT = "d66fc99e20f21f8458cd0e846567500c1ed90623"
OWNER = "agent-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"
REVIEWER = "reviewer-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"
PROFILE = "Voice"
PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_LINE = 22
PROFILE_ROW = (
    "| Voice | Freeze permitted input and target references, task and "
    "language/speaker groups. Preserve text and semantic content, "
    "identity/similarity and naturalness as separate outcomes. Record "
    "alignment, first-output/tail timing and the exact target condition. "
    "Consent, reference availability and output use are independent gates. |"
)
REQUIRED_INTERPRETER = "3.12.16"
REPORT_SCHEMA = "audio-sdk/voice-preserving-zero-shot-multiple-accent-conversion/report/0.1"
CONTRACT_SCHEMA = "audio-sdk/voice-preserving-zero-shot-multiple-accent-conversion/contract/0.1"
TASK_PREFIX = "docs/task-evidence/voice-preserving-zero-shot-multiple-accent-conversion/"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

EVIDENCE_PATH = "research/accent-conversion-20261101/README.md"
EVIDENCE_LINE = 174
EVIDENCE_TEXT = (
    "| **Voice-Preserving Zero-Shot Multiple Accent Conversion** | "
    "Paper inspected; no official weights/repo located. | Research comparison "
    "only. [Paper](https://arxiv.org/abs/2211.13282) |"
)

LINK_FIELDS = ("id", "title", "mode", "repository", "component", "depends_on")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable",
    "acceptance", "evidence",
)
LINKED_ROWS = (
    {
        "component": COMPONENT,
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "id": TASK,
        "mode": MODE,
        "repository": "audio-sdk",
        "title": TITLE,
    },
    {
        "component": None,
        "depends_on": [],
        "id": "SDK-FND-AUDIT",
        "mode": "foundation",
        "repository": "audio-sdk",
        "title": "Public provider intake and asset boundary",
    },
    {
        "component": None,
        "depends_on": [],
        "id": "SDK-FND-EVIDENCE",
        "mode": "foundation",
        "repository": "audio-sdk",
        "title": "Task-matched conformance and reproducible benchmark evidence",
    },
    {
        "component": None,
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
        "id": "SDK-FND-PROVIDER",
        "mode": "foundation",
        "repository": "audio-sdk",
        "title": "Provider integration boundaries and build fragments",
    },
)

INVENTORY_LINK = {
    "component_id": "voice-preserving-zero-shot-multiple-accent-conversion",
    "name": TITLE,
    "area": "Voice and synthesis",
    "evidence_status": "considered",
    "disposition": "sdk-model",
    "task": TASK,
    "evidence_path": EVIDENCE_PATH,
    "evidence_line": EVIDENCE_LINE,
    "record_name": TITLE,
    "finding": (
        "Paper inspected; no official weights/repo located. Research comparison "
        "only. [Paper](https://arxiv.org/abs/2211.13282)"
    ),
}

NON_CLAIMS = (
    "No paper implementation, provider, adapter, descriptor, registry entry or default is added.",
    "No source, checkpoint, weight, model card, runtime or licence is included.",
    "No network request, download, vendoring or in-process file access is performed.",
    "No corpus audio, converted speech, listening test or device timing is present.",
    "No accent, quality, identity, naturalness, latency, memory or benchmark result is claimed.",
    "No source-reported paper result is treated as matched or comparable evidence.",
    "No public release, qualification, conformance or parity claim is made.",
    "No board, handoff, CI, public ABI, shared build or descriptor change is made.",
)

VOICE_REQUIREMENTS = (
    ("VR-01", "Freeze input, target references, task and language/speaker groups",
     "blocked", "No permitted source clip, target reference, language/speaker grouping or task cohort is staged."),
    ("VR-02", "Separate content, identity/similarity and naturalness outcomes",
     "blocked", "No output or listening result exists; paper context is not matched evidence."),
    ("VR-03", "Record alignment, first-output/tail timing and exact target condition",
     "blocked", "No runnable runtime, no stream, no alignment and no exact target condition."),
    ("VR-04", "Keep consent, reference availability and output use independent",
     "blocked", "No consent, reference availability or output-use permission record is staged."),
)

REQUIRED_ARTIFACTS = (
    ("ART-01", "Exact paper source/runtime identity",
     "No immutable official implementation revision, archive digest, runtime lock or installation location exists."),
    ("ART-02", "Reviewed code and model licence/terms",
     "No official repo/weights licence, model card or redistribution terms are staged."),
    ("ART-03", "Complete external asset manifest",
     "No per-asset ID, byte count, SHA-256, storage=external declaration or caller supply exists."),
    ("ART-04", "Voice cohort, target reference and rights records",
     "No consented cohort, transcript, language/speaker grouping, target reference or output-use permission is staged."),
    ("ART-05", "Matched task evidence and separated outcomes",
     "No run, no alignment, no content/identity/naturalness/accent separation and no independent listening."),
    ("ART-06", "Timing, resource and integration controls",
     "No device timing, first-output/tail measurement, reset checks or OFF-by-default integration review."),
)

BLOCKERS = (
    ("BLK-01", "No official implementation or weights",
     "Research evidence states paper inspected; no official weights/repo located."),
    ("BLK-02", "No asset identity or reviewed terms",
     "No immutable revision, per-file hash, byte count, licence, model card or redistribution terms are staged."),
    ("BLK-03", "No caller-supplied manifest or runtime",
     "No caller tool-manifest reference, pinned runtime digest, offline load path or installation location is supplied."),
    ("BLK-04", "No voice geometry or rights",
     "Task/language/speaker groups, target references, consent and output-use permission are absent."),
    ("BLK-05", "No matched evidence",
     "There is no aligned, separated, listening-verified or device-timed result for this task."),
    ("BLK-06", "No opt-in integration or release approval",
     "No descriptor, provider ID, mode, OFF-by-default intake, exact-head review or release approval exists."),
)

GATES = (
    ("RG-01", "source_runtime_identity_and_license",
     "Immutable source/runtime identity plus reviewed licence/terms must exist before integration.",
     "Caller supplies an immutable official revision/archive digest, pinned runtime lock and reviewed licence/notice/terms."),
    ("RG-02", "external_asset_manifest",
     "Every required external asset must declare ID, byte count, SHA-256 and storage=external.",
     "Caller supplies a complete per-asset manifest with exact bytes and reviewed redistribution terms."),
    ("RG-03", "pinned_offline_load",
     "The exact snapshot must load offline with no implicit download or in-process file access.",
     "A locked runtime loads the pinned assets offline and records deterministic host/runtime settings."),
    ("RG-04", "voice_geometry_and_rights",
     "Permitted input, target reference, task and language/speaker groups must be frozen with independent rights.",
     "A rights-cleared cohort, transcripts, grouping, reference availability and output-use permission are staged."),
    ("RG-05", "matched_outcomes",
     "Content, identity/similarity, naturalness and accent outcomes must be separated and independently listened.",
     "Matched runs and independent listening results are linked with source-reported scores labelled separately."),
    ("RG-06", "timing_and_resource_controls",
     "Alignment, first-output/tail timing, nonfinite checks and resource limits must be recorded.",
     "Device-domain timing, resource accounting, reset and invalid-input controls are pass/fail recorded."),
    ("RG-07", "off_by_default_integration_review",
     "Application-local registration must be opt-in with no automatic discovery or fallback.",
     "An OFF-by-default descriptor/provider/mode entry is reviewed at exact head with no default or registry change."),
    ("RG-08", "release_approval",
     "Public release admission is separate from application-local registration and remains unapproved.",
     "Independent exact-head review and explicit release approval are recorded after all prior gates clear."),
)

TOOL_MANIFEST_REQUIRED_FIELDS = (
    "provider_id", "implementation_id", "implementation_version",
    "source_revision", "source_digest", "runtime_digest", "required_assets",
    "license_notice_refs", "terms_ref", "supported_formats", "target_condition",
)
EXTERNAL_ASSET_FIELDS = ("asset_id", "sha256", "byte_count", "storage")

WORKSPACE_PROBES = (
    "data/checkouts/voice-preserving-zero-shot-multiple-accent-conversion",
    "data/envs/voice-preserving-zero-shot-multiple-accent-conversion",
    "data/models/voice-preserving-zero-shot-multiple-accent-conversion",
    "data/runs/voice-preserving-zero-shot-multiple-accent-conversion",
    "research/voice-preserving-zero-shot-multiple-accent-conversion",
)
WORKTREE_PROBES = (
    "third_party/voice-preserving-zero-shot-multiple-accent-conversion",
    "adapters/voice-preserving-zero-shot-multiple-accent-conversion",
    "bindings/python/voice_preserving_zero_shot_multiple_accent_conversion",
)
HOME_PROBES = (
    "~/.cache/huggingface/hub/models--voice-preserving-zero-shot-multiple-accent-conversion",
    "~/Library/Caches/pip/wheels/voice-preserving-zero-shot-multiple-accent-conversion",
)

LOCAL_FILES = (
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
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
PROHIBITED_SUFFIXES = frozenset({
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav",
    ".weights", ".whl", ".zip", ".gz", ".tar",
})


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def strict_json_loads(text: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def board_link_projection() -> tuple[list[dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ValueError("board_unavailable")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    tasks = board.get("tasks") if isinstance(board, dict) else None
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    by_id = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    links: list[dict[str, Any]] = []
    for expected in LINKED_ROWS:
        row = by_id.get(expected["id"])
        if row is None:
            raise ValueError("linked_row_missing:" + expected["id"])
        projection = {field: row.get(field) for field in LINK_FIELDS}
        if projection != {field: expected[field] for field in LINK_FIELDS}:
            raise ValueError("linked_row_changed:" + expected["id"])
        links.append(projection)
    return links, object_digest(links)


def voice_profile_check() -> dict[str, Any]:
    path = WORKSPACE / PROFILE_SOURCE
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    row = lines[PROFILE_LINE - 1] if len(lines) >= PROFILE_LINE else ""
    phrases = (
        "Freeze permitted input and target references",
        "identity/similarity and naturalness as separate outcomes",
        "first-output/tail timing",
        "Consent, reference availability and output use are independent gates",
    )
    return {
        "source": PROFILE_SOURCE,
        "line": PROFILE_LINE,
        "row": row,
        "expected_row": PROFILE_ROW,
        "phrases": list(phrases),
        "phrases_all_present": row == PROFILE_ROW and all(p in row for p in phrases),
    }


def evidence_entry() -> dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    return {
        "path": EVIDENCE_PATH,
        "line": EVIDENCE_LINE,
        "text": lines[EVIDENCE_LINE - 1] if len(lines) >= EVIDENCE_LINE else "",
        "expected_text": EVIDENCE_TEXT,
        "sha256": SOURCE_PINS[EVIDENCE_PATH],
    }


def probe_rows() -> dict[str, list[dict[str, Any]]]:
    groups = {
        "workspace": [(WORKSPACE / path, path) for path in WORKSPACE_PROBES],
        "worktree": [(SDK_ROOT / path, path) for path in WORKTREE_PROBES],
        "home": [(Path(path).expanduser(), path) for path in HOME_PROBES],
    }
    result: dict[str, list[dict[str, Any]]] = {}
    for group, entries in groups.items():
        result[group] = [
            {"path": label, "present": target.exists() or target.is_symlink()}
            for target, label in entries
        ]
    return result


def absence_summary(probes: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    rows = [row for group in probes.values() for row in group]
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "all_absent": all(row["present"] is False for row in rows),
        "recursive_walk_performed": False,
        "download_performed": False,
    }


def _artifact_rows() -> list[dict[str, Any]]:
    return [{
        "id": identifier, "title": title, "status": "absent",
        "present": False, "verified": False, "gap": gap,
    } for identifier, title, gap in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict[str, Any]]:
    return [{
        "id": identifier, "title": title, "status": "open", "detail": detail,
    } for identifier, title, detail in BLOCKERS]


def _gate_rows() -> list[dict[str, Any]]:
    return [{
        "id": identifier, "title": title, "status": "blocked",
        "qualifies": False, "statement": statement, "reopen_condition": reopen,
    } for identifier, title, statement, reopen in GATES]


def _voice_rows() -> list[dict[str, Any]]:
    return [{
        "id": identifier, "requirement": requirement, "status": status, "detail": detail,
    } for identifier, requirement, status, detail in VOICE_REQUIREMENTS]


def boundary() -> dict[str, Any]:
    return {
        "task_local_write_only": True,
        "write_prefix": TASK_PREFIX,
        "installed_v0_unchanged": True,
        "installed_v0_format": {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        },
        "public_api_abi_changed": False,
        "provider_registered": False,
        "descriptor_or_registry_changed": False,
        "enabled_by_default": False,
        "automatic_discovery_or_fallback": False,
        "shared_cmake_changed": False,
        "ci_changed": False,
        "board_or_handoff_changed": False,
        "vendor_terms_reviewed": False,
        "vendor_source_weights_or_runtime_present": False,
        "real_corpus_audio_present": False,
        "listening_or_device_timing_performed": False,
        "download_or_in_process_file_access": False,
        "benchmark_claim": False,
        "release_claim": False,
    }


def tool_manifest_reference() -> dict[str, Any]:
    return {
        "status": "absent",
        "caller_supplied": False,
        "accepted_manifest_present": False,
        "required_fields": list(TOOL_MANIFEST_REQUIRED_FIELDS),
        "expected_asset_fields": list(EXTERNAL_ASSET_FIELDS),
        "note": (
            "A caller-supplied runtime may be declared only through exact "
            "external assets; no such reference or manifest is staged here."
        ),
    }


def external_assets() -> dict[str, Any]:
    return {
        "status": "absent",
        "declared_count": 0,
        "required_fields": list(EXTERNAL_ASSET_FIELDS),
        "assets": [],
        "caller_supplied_exact_bytes": False,
        "no_fabricated_digest_or_byte_count": True,
    }


def qualification() -> dict[str, Any]:
    return {
        "decision": "DEFER",
        "status": "not_qualified",
        "readiness": "incomplete",
        "evidence_status": "incomplete",
        "proposal_only": True,
        "candidate_qualified": False,
        "all_required_results_present": False,
        "comparison_qualified": False,
        "upstream_parity_claim": False,
    }


def build_contract() -> dict[str, Any]:
    links, link_digest = board_link_projection()
    contract = {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": MODE,
        "repository": "audio-sdk",
        "owner": OWNER,
        "reviewer": REVIEWER,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "profile": PROFILE,
        "profile_source_check": voice_profile_check(),
        "required_interpreter": REQUIRED_INTERPRETER,
        "scope": {
            "included": [TASK_PREFIX],
            "excluded": ["provider", "descriptor", "registry", "default",
                         "public ABI", "shared build", "CI", "board",
                         "handoff", "vendor download"],
        },
        "boundary": boundary(),
        "boundary_pins": dict(sorted(BOUNDARY_PINS.items())),
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "evidence_entry": evidence_entry(),
        "inventory_link": dict(INVENTORY_LINK),
        "linked_rows": links,
        "linked_row_projection_sha256": link_digest,
        "linked_row_fields": list(LINK_FIELDS),
        "mutable_row_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "tool_manifest_reference": tool_manifest_reference(),
        "external_assets": external_assets(),
        "qualification": qualification(),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "voice_requirements": _voice_rows(),
        "non_claims": list(NON_CLAIMS),
        "public_v0_geometry": {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
            "note": "Installed geometry is preserved; no candidate mapping is claimed.",
        },
    }
    return contract


def build_report() -> dict[str, Any]:
    links, link_digest = board_link_projection()
    probes = probe_rows()
    contract = build_contract()
    return {
        "schema_id": REPORT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": MODE,
        "repository": "audio-sdk",
        "owner": OWNER,
        "reviewer": REVIEWER,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "source_reported_scores_labeled_separately": True,
        "profile": PROFILE,
        "profile_source_check": voice_profile_check(),
        "required_interpreter": REQUIRED_INTERPRETER,
        "boundary": boundary(),
        "boundary_pins": dict(sorted(BOUNDARY_PINS.items())),
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "evidence_entry": evidence_entry(),
        "inventory_link": dict(INVENTORY_LINK),
        "linked_rows": links,
        "linked_row_projection_sha256": link_digest,
        "linked_row_fields": list(LINK_FIELDS),
        "mutable_row_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "tool_manifest_reference": tool_manifest_reference(),
        "external_assets": external_assets(),
        "qualification": qualification(),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "voice_requirements": _voice_rows(),
        "absence_evidence": {
            "workspace": probes["workspace"],
            "worktree": probes["worktree"],
            "home": probes["home"],
            "summary": absence_summary(probes),
        },
        "non_claims": list(NON_CLAIMS),
        "contract_digest": object_digest(contract),
    }


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "schema_id", "task", "decision", "status", "evidence_status",
        "qualification", "release_gates", "exact_blockers", "required_artifacts",
        "boundary", "source_pins", "boundary_pins",
    }
    missing = required - set(contract)
    if missing:
        raise ValueError("contract_missing:" + ",".join(sorted(missing)))
    if contract["schema_id"] != CONTRACT_SCHEMA:
        raise ValueError("contract_schema")
    if contract["decision"] != "DEFER":
        raise ValueError("contract_decision")
    if contract["status"] != "proposal_only_incomplete":
        raise ValueError("contract_status")
    if contract["qualification"] != qualification():
        raise ValueError("contract_qualification")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    if any(g["status"] != "blocked" or g["qualifies"] is not False
           for g in contract["release_gates"]):
        raise ValueError("contract_gate_status")
    if not finite_json(contract):
        raise ValueError("contract_nonfinite")


def validate_report(report: dict[str, Any]) -> None:
    required = {
        "schema_id", "task", "decision", "status", "evidence_status",
        "qualification_status", "qualification", "release_gates",
        "exact_blockers", "required_artifacts", "absence_evidence",
    }
    missing = required - set(report)
    if missing:
        raise ValueError("report_missing:" + ",".join(sorted(missing)))
    if report["schema_id"] != REPORT_SCHEMA:
        raise ValueError("report_schema")
    if report["decision"] != "DEFER":
        raise ValueError("report_decision")
    if report["status"] != "proposal_only_incomplete":
        raise ValueError("report_status")
    if report["qualification_status"] != "not_qualified":
        raise ValueError("report_qualification_status")
    if report["qualification"] != qualification():
        raise ValueError("report_qualification")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        raise ValueError("report_missing_result_qualifies")
    if not finite_json(report):
        raise ValueError("report_nonfinite")


def report_bytes() -> bytes:
    report = build_report()
    validate_report(report)
    return canonical_bytes(report) + b"\n"


def _local_manifest_paths() -> list[str]:
    return sorted(name for name in LOCAL_FILES if name != "README.md")


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for path, digest in sorted(SOURCE_PINS.items()):
        rows.append((digest, "source:" + path))
    for path, digest in sorted(BOUNDARY_PINS.items()):
        rows.append((digest, "sdk:" + path))
    for name in _local_manifest_paths():
        target = HERE / name
        if not target.is_file():
            raise ValueError("missing_artifact:" + name)
        rows.append((sha256_file(target), TASK_PREFIX + name))
    rows.append((sha256_file(HERE / "README.md"), TASK_PREFIX + "README.md"))
    return "".join(d + "  " + p + "\n" for d, p in rows).encode("ascii")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if not line:
            continue
        if "  " not in line:
            raise ValueError("malformed_pin_line")
        digest, path = line.split("  ", 1)
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("malformed_digest")
        rows.append((digest, path))
    return rows


# README digest helpers

def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()},
    }


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section, (start, end) in README_MARKERS.items():
        if text.count(start) != 1 or text.count(end) < 1:
            raise ValueError("readme_table_marker:" + section)
        start_index = text.index(start) + len(start)
        end_index = text.index(end, start_index)
        block = text[start_index:end_index]
        rows: list[tuple[str, str]] = []
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not cells or cells[0] in {"Path", "---", "Pin", "Key"}:
                continue
            if section in {"source", "boundary"} and len(cells) >= 2:
                key = cells[0].strip("`")
                digest = cells[1].strip("`")
                rows.append((key, digest))
            elif section == "artifacts" and len(cells) >= 3:
                key = cells[0].strip("`")
                digest = cells[1].strip("`")
                rows.append((key, digest))
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual = {key for key, _ in parsed[section]}
        if actual != expected[section]:
            raise ValueError(
                "readme_key_mismatch:" + section + ":missing="
                + str(sorted(expected[section] - actual))
                + ":extra=" + str(sorted(actual - expected[section])))
        for key, digest in parsed[section]:
            if section == "source":
                path = WORKSPACE / key[len("source:"):]
                wanted = SOURCE_PINS[key[len("source:"):]]
            elif section == "boundary":
                path = SDK_ROOT / key[len("sdk:"):]
                wanted = BOUNDARY_PINS[key[len("sdk:"):]]
            else:
                path = HERE / key
                wanted = sha256_file(path)
            if digest != wanted or not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        path = HERE / key
        size = path.stat().st_size
        line = "| `" + key + "` | `" + sha256_file(path) + "` | " + str(size) + " |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = ["| Pin | SHA-256 |", "| --- | --- |"]
        for name, digest in sorted(SOURCE_PINS.items()):
            rows.append("| `source:" + name + "` | `" + digest + "` |")
        return "\n".join(rows)
    if section == "boundary":
        rows = ["| Pin | SHA-256 |", "| --- | --- |"]
        for name, digest in sorted(BOUNDARY_PINS.items()):
            rows.append("| `sdk:" + name + "` | `" + digest + "` |")
        return "\n".join(rows)
    if section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            path = HERE / name
            rows.append("| `" + name + "` | `" + sha256_file(path)
                        + "` | " + str(path.stat().st_size) + " |")
        return "\n".join(rows)
    raise ValueError("unknown_readme_section:" + section)


def update_readme_table(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1 or text.count(end) < 1:
        raise ValueError("readme_table_marker:" + section)
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    block = render_digest_table(section)
    return (text[:start_index] + start + "\n" + block + "\n" + end
            + text[end_index:])


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# Task-local git scope: newest merge-base with origin/main then main.

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Return the newest merge-base of HEAD and any available base ref."""
    best: str | None = None
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


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
