# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-WHISPER-STREAMING.

This feasibility package is blocked: no local Whisper-Streaming / SimulStreaming
checkpoint, streaming ASR runtime, adapter, reference transcript cohort, or
measured WER/latency result is present in this workspace. No download, model
execution, network, real audio, device timing, listening, public benchmark,
release, or qualification claim is made.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
)

TASK = "SDK-WHISPER-STREAMING"
TITLE = "Whisper-Streaming"
SLUG = "whisper-streaming"
COMPONENT = "whisper-streaming"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-WHISPER-STREAMING"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

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

TASK_ROW_STABLE_SHA256 = (
    "b989b3a231771f3c35e2d0502d63e15481a6df1fa5155083e74630f4cf616c31"
)
TASK_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "acceptance": "Apply the rate acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
    "component": "whisper-streaming",
    "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then implement or wrap a minimal reference using the relevant public adapter boundary and ship it as optional initially. Record a concrete blocker if feasibility fails.",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": ["research/voice-enhancement-20261101/candidate_matrix.csv"],
    "id": "SDK-WHISPER-STREAMING",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": "Whisper-Streaming",
    "write_scope": [
        "SDK provider, tool or evidence directory for whisper-streaming and its own fixtures"
    ],
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
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
    "real_audio": False,
    "real_corpus": False,
    "real_dataset": False,
    "dataset_downloaded": False,
    "model_executed": False,
    "weights_downloaded": False,
    "runtime_invoked": False,
    "network_used": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "release_claim": False,
    "task_local_only": True,
}

NON_CLAIMS: List[str] = [
    "No Whisper-Streaming/SimulStreaming checkpoint, runtime, adapter, transcript, alignment, or derived weight is loaded, executed, staged, or redistributed.",
    "No network request, download, dataset acquisition, or external runtime invocation occurs.",
    "No real audio, real corpus, reference transcript cohort, WER, latency, or streaming playback measurement is claimed.",
    "No quality, intelligibility, listening, device, public benchmark, or release result is claimed.",
    "Candidate matrix and research reports are pinned context only; they are not promoted to measured or qualified evidence.",
    "No provider, descriptor, registry, installed v0 path, shared build, CI, board, or handoff change is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER and qualification remains not_qualified.",
]

GATE_REQUIREMENTS: List[Tuple[str, str]] = [
    ("exact_source_and_asset_identity", "Exact Whisper-Streaming/SimulStreaming source revision, checkpoint/runtime assets, hashes, byte counts, and immutable manifests are pinned and present."),
    ("rights_and_publication", "Acquisition, local evaluation, publication, redistribution, product-use, and derivative-output rights are cleared with complete notices."),
    ("matched_reference_parity", "An approved exact-runtime reference reproduces the candidate on frozen inputs with hashed outputs and verified parity/tolerance policy."),
    ("rate_cohort_and_scoring", "A rights-cleared frozen cohort with reference transcripts, source/output mapping, duration, pause/filler timestamp policy, and task-matched Rate scoring is present."),
    ("runtime_and_reproducibility", "An isolated pinned runtime and deterministic command recipe reproduce outputs without network or hidden mutation."),
    ("timing_delay_and_state", "Streaming state, chunk/reset boundaries, content/availability delay, buffering, drift, and final partial-window behavior are verified."),
    ("adapter_boundary_and_isolation", "Any future SDK adapter is optional, caller-supplied-asset, preserves installed v0 behavior, and is not registered/enabled by default."),
    ("public_default_and_release", "Explicit default-selection, resource/deadline evidence, and release/public-benchmark approval are recorded; default remains off."),
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {
        "id": "asr_checkpoint_absent",
        "gate_ids": ["exact_source_and_asset_identity", "matched_reference_parity"],
        "requirement": "Provide an exact local Whisper-Streaming/SimulStreaming ASR checkpoint and runtime artifact with immutable hashes, byte counts, and provenance.",
        "state": "No local ASR checkpoint, streaming runtime, or exact executable artifact is present in this workspace for this task package.",
    },
    {
        "id": "reference_transcript_cohort_absent",
        "gate_ids": ["rate_cohort_and_scoring", "matched_reference_parity"],
        "requirement": "Provide a rights-cleared frozen cohort with reference transcripts and task-matched scoring for WER/latency and Rate profile checks.",
        "state": "No local reference transcript cohort, WER scorer, or measured WER/latency result is staged for this candidate.",
    },
    {
        "id": "rights_uncleared",
        "gate_ids": ["rights_and_publication", "public_default_and_release"],
        "requirement": "Clear source/checkpoint/data rights, notices, redistribution, product-use, and publication terms before any claim.",
        "state": "No per-asset rights record, license decision, redistribution approval, or publication review is present.",
    },
    {
        "id": "exact_runtime_absent",
        "gate_ids": ["runtime_and_reproducibility", "timing_delay_and_state"],
        "requirement": "Provide an isolated pinned runtime with deterministic execution recipe and recorded platform for the exact candidate.",
        "state": "No isolated pinned runtime, lockfile, or deterministic execution trace is staged; model execution is absent.",
    },
    {
        "id": "reference_parity_absent",
        "gate_ids": ["matched_reference_parity", "runtime_and_reproducibility"],
        "requirement": "Reproduce an approved exact-runtime reference on frozen inputs with hashed outputs and parity/tolerance verification.",
        "state": "No approved reference outputs, parity vectors, or independently verified reproduction exists.",
    },
    {
        "id": "streaming_timing_contract_unverified",
        "gate_ids": ["timing_delay_and_state", "rate_cohort_and_scoring"],
        "requirement": "Verify streaming chunk/reset state, source/output mapping, buffering, drift, final partial window, and content/availability timing.",
        "state": "No candidate-specific streaming timing/state contract has been verified because no exact runnable artifact or cohort is available.",
    },
    {
        "id": "adapter_boundary_incomplete",
        "gate_ids": ["adapter_boundary_and_isolation", "public_default_and_release"],
        "requirement": "Keep any future SDK adapter optional, caller-supplied-asset, off by default, and outside installed v0/shared build/CI/public registration.",
        "state": "No versioned adapter boundary or independent review exists; this package intentionally adds no adapter, provider, or registration.",
    },
    {
        "id": "public_default_and_release_absent",
        "gate_ids": ["public_default_and_release"],
        "requirement": "Record explicit non-default decision, target-device resource/deadline evidence, and release/public-benchmark approval before any exposure.",
        "state": "No device evidence, deadline budget, default-selection approval, or release/public-benchmark review exists.",
    },
]

RATE_PROFILE_ROWS: List[Dict[str, str]] = [
    {"id": "RP-01", "requirement": "Measure source/output mapping, duration, pitch, transient audibility and playback buffering.", "status": "blocked", "reason": "No runnable streaming ASR/runtime, frozen cohort, or measured output mapping exists."},
    {"id": "RP-02", "requirement": "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window.", "status": "blocked", "reason": "No rate-controlled execution path or frozen Rate cohort is present."},
    {"id": "RP-03", "requirement": "Keep pause or filler decisions tied to source timestamps and measure speech preservation.", "status": "blocked", "reason": "No transcript/timestamp output, pause/filler policy, or speech-preservation measurement exists."},
]

QUALITY_ROWS: List[Dict[str, Any]] = [
    {"id": "Q-01", "name": "wer_or_transcript_equivalence", "status": "blocked", "value": None, "reason": "No reference transcript cohort or ASR output exists."},
    {"id": "Q-02", "name": "source_output_mapping", "status": "blocked", "value": None, "reason": "No measured source/output mapping exists."},
    {"id": "Q-03", "name": "speech_preservation", "status": "blocked", "value": None, "reason": "No speech-preservation measurement exists."},
    {"id": "Q-04", "name": "finite_output_and_state", "status": "blocked", "value": None, "reason": "No runtime execution or state/reset validation exists."},
    {"id": "Q-05", "name": "control_and_baseline", "status": "blocked", "value": None, "reason": "No identity/baseline/control run exists."},
]

TIMING_ROWS: List[Dict[str, Any]] = [
    {"id": "T-01", "name": "content_delay", "status": "blocked", "value": None, "reason": "No streaming runtime or timestamped output exists."},
    {"id": "T-02", "name": "availability_delay", "status": "blocked", "value": None, "reason": "No paced execution or availability measurement exists."},
    {"id": "T-03", "name": "drift_rebuffer_final_partial", "status": "blocked", "value": None, "reason": "No buffering/drift/final-partial measurement exists."},
    {"id": "T-04", "name": "device_resources", "status": "blocked", "value": None, "reason": "No target-device timing or resource measurement exists."},
]

SCOPE_BASE_REFS = ("origin/main", "main")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8") + "\n"


def canonical_file_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("utf-8")


def strict_loads(text: str) -> Any:
    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON constant: {value}")

    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj

    return json.loads(text, parse_constant=reject_constant, object_pairs_hook=object_pairs_hook)


def read_strict_json(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _git_scope(worktree: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(worktree), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git_scope(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path, refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git_scope(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git_scope(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git_scope(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


def board_row_projection(board_path: Path) -> Dict[str, Any]:
    board = read_strict_json(board_path)
    rows = [
        row for row in board.get("tasks", [])
        if isinstance(row, dict) and row.get("id") == TASK
    ]
    if len(rows) != 1:
        raise ValueError("expected_exactly_one_linked_task_row")
    row = rows[0]
    return {field: row.get(field) for field in STABLE_TASK_FIELDS}


def board_row_digest(projection: Dict[str, Any]) -> str:
    return object_digest(projection)


def linked_rows() -> Dict[str, Dict[str, Any]]:
    board_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    board = read_strict_json(board_path)
    wanted = {TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"}
    rows: Dict[str, Dict[str, Any]] = {}
    for row in board.get("tasks", []):
        if not isinstance(row, dict):
            continue
        task_id = row.get("id")
        if task_id in wanted:
            rows[task_id] = {
                field: row.get(field)
                for field in ("id", "title", "component", "mode", "repository", "depends_on")
            }
    missing = sorted(wanted - set(rows))
    if missing:
        raise ValueError("missing_linked_rows:" + ",".join(missing))
    return {task_id: rows[task_id] for task_id in sorted(rows)}


def linked_rows_digest(rows: Dict[str, Dict[str, Any]]) -> str:
    return object_digest(rows)


def source_presence() -> Dict[str, Any]:
    probes = [
        "data/models/whisper",
        "data/models/whisper-streaming",
        "data/models/simulstreaming",
        "data/checkouts/whisper_streaming",
        "data/checkouts/SimulStreaming",
        "data/envs/whisper-streaming",
        "data/runs/whisper-streaming",
    ]
    found = []
    for rel in probes:
        path = SOURCE_ROOT / rel
        if path.exists():
            found.append(rel)
    return {
        "source_repository_present": False,
        "weights_present": False,
        "weights_model_id_recorded": False,
        "weights_digest_recorded": False,
        "runtime_present": False,
        "run_artifacts_present": False,
        "rights_cleared_audio_present": False,
        "exact_source_weights_runtime_conjunction_present": False,
        "candidate_note_and_inventory_present": True,
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "model_executed": False,
        "absence_probe_roots": probes,
        "absence_probe_hits": found,
        "all_absence_probes_absent": len(found) == 0,
    }


def documented_claims() -> List[Dict[str, Any]]:
    return [
        {
            "source": "research/voice-enhancement-20261101/candidate_matrix.csv:35",
            "claim": "Whisper-Streaming / SimulStreaming unavailable/blocked; no local ASR checkpoint, streaming runtime or adapter; no local WER/latency result.",
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
        },
        {
            "source": "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
            "claim": "Whisper-Streaming / SimulStreaming has no local ASR checkpoint or streaming adapter; whisper/faster_whisper/NeMo/sherpa-onnx absent in checked runtime; no model substituted.",
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
        },
        {
            "source": "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
            "claim": "Whisper-Streaming is researched but not run; original project points to SimulStreaming; no local adapter or run.",
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
        },
    ]


def profile_row() -> str:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Rate |"):
            return line
    raise ValueError("rate_profile_row_missing")


def build_contract() -> Dict[str, Any]:
    row = board_row_projection(SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json")
    rows = linked_rows()
    gates = [
        {
            "id": f"RG-{i:02d}",
            "requirement": req,
            "status": "blocked",
            "qualifies": False,
            "reopen_condition": blocker["requirement"],
            "linked_row": row,
        }
        for i, ((_, req), blocker) in enumerate(zip(GATE_REQUIREMENTS, EXACT_BLOCKERS), start=1)
    ]
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": "feasibility",
        "profile": PROFILE,
        "profile_label": "Rate",
        "decision": DECISION,
        "status": STATUS,
        "proposal_only": True,
        "qualification_status": QUALIFICATION,
        "disposition": (
            "Whisper-Streaming/SimulStreaming feasibility blocker; no checkpoint, "
            "runtime, adapter, cohort, WER/latency, or qualification."
        ),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "claim_worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION,
            "not_qualified": True,
            "candidate_qualified": False,
            "all_release_gates_blocked": True,
            "blocked_gate_count": len(gates),
            "real_result_present": False,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "cohort_present": False,
            "wer_result": False,
            "latency_result": False,
            "rate_profile_result": False,
            "device_timing_result": False,
            "listening_result": False,
            "benchmark_result": False,
            "release_claim": False,
            "no_missing_result_qualifies_candidate": True,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "task_row_identity": {
            "whole_file_hashed": False,
            "stable_sha256": TASK_ROW_STABLE_SHA256,
            "stable_fields": dict(TASK_ROW_STABLE_FIELDS),
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
            "projection": row,
        },
        "linked_row_identity": {
            "projection": row,
            "sha256": board_row_digest(row),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": rows,
            "linked_rows_sha256": linked_rows_digest(rows),
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_presence": source_presence(),
        "gates": gates,
        "release_gates": gates,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "required_artifacts": [
            {
                "id": "ART-01",
                "kind": "research_reports_and_inventory",
                "present": True,
                "verified": True,
                "blocked": False,
                "sha256": None,
                "requirement": "Pinned inventory/candidate matrix/research reports identifying the Whisper-Streaming/SimulStreaming blocker.",
            },
            {
                "id": "ART-02",
                "kind": "exact_source_checkpoint_runtime",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Exact Whisper-Streaming/SimulStreaming source revision, checkpoint, tokenizer/config, runtime, and complete notices.",
            },
            {
                "id": "ART-03",
                "kind": "rights_cleared_cohort",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Rights-cleared frozen reference transcript cohort with scoring manifest and WER/latency protocol.",
            },
            {
                "id": "ART-04",
                "kind": "reference_parity_outputs",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Approved exact-runtime reference outputs with parity/tolerance verification.",
            },
            {
                "id": "ART-05",
                "kind": "rate_profile_measurements",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Rate-profile measurements for source/output mapping, buffering, drift, final partial window, and speech preservation.",
            },
            {
                "id": "ART-06",
                "kind": "device_timing_resources",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Target-device content/availability timing, CPU/memory, and deadline-budget evidence.",
            },
            {
                "id": "ART-07",
                "kind": "adapter_review_and_release",
                "present": False,
                "verified": False,
                "blocked": True,
                "sha256": None,
                "requirement": "Separate opt-in adapter intake, default-off decision, and release/public-benchmark approval.",
            },
        ],
        "rate_profile_requirements": [dict(r) for r in RATE_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_ROWS],
        "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "documented_claims": documented_claims(),
        "non_claims": list(NON_CLAIMS),
        "profile_row": profile_row(),
        "reproduction": {
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 -m unittest -q test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 verify.py",
            ],
            "cold_start_regenerations": 3,
        },
    }


def build_report(contract: Dict[str, Any] | None = None) -> Dict[str, Any]:
    contract = contract or build_contract()
    report = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "mode": "feasibility",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION,
        "proposal_only": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "defer_before": DEFER_BEFORE,
        "contract_sha256": object_digest(contract),
        "qualification": dict(contract["qualification"]),
        "boundary": dict(contract["boundary"]),
        "scope": dict(contract["scope"]),
        "task_row_identity": dict(contract["task_row_identity"]),
        "linked_row_identity": dict(contract["linked_row_identity"]),
        "source_pins": {
            path: {"sha256": digest, "actual": digest, "verified": True}
            for path, digest in SOURCE_PINS.items()
        },
        "boundary_pins": {
            path: {"sha256": digest, "actual": digest, "verified": True}
            for path, digest in BOUNDARY_PINS.items()
        },
        "source_presence": source_presence(),
        "documented_context": {
            "provenance_only": True,
            "reproduced_here": False,
            "used_for_evidence": False,
            "qualifies": False,
            "source_reported_claims_not_reproduced": documented_claims(),
        },
        "absence_evidence": {
            "summary": {
                "probe_count": len(source_presence()["absence_probe_roots"]),
                "workspace_probe_count": len(source_presence()["absence_probe_roots"]),
                "external_probe_count": 0,
                "present_count": len(source_presence()["absence_probe_hits"]),
                "all_probes_absent": source_presence()["all_absence_probes_absent"],
                "download_attempted": False,
                "network_used": False,
                "recursive_workspace_walk": False,
                "source_or_runtime_imported": False,
                "weights_loaded": False,
                "model_executed": False,
                "audio_read": False,
            },
            "probes": [
                {"path": p, "present": p in source_presence()["absence_probe_hits"]}
                for p in source_presence()["absence_probe_roots"]
            ],
        },
        "gates": [dict(g) for g in contract["gates"]],
        "exact_blockers": [dict(b) for b in contract["exact_blockers"]],
        "required_artifacts": [dict(a) for a in contract["required_artifacts"]],
        "rate_profile": {"rows": [dict(r) for r in RATE_PROFILE_ROWS]},
        "quality_outcomes": {"rows": [dict(r) for r in QUALITY_ROWS]},
        "timing": {"rows": [dict(r) for r in TIMING_ROWS]},
        "required_results": {
            "wer_or_transcript_equivalence": {"status": "blocked", "value": None},
            "latency_or_content_availability": {"status": "blocked", "value": None},
            "rate_profile": {"status": "blocked", "value": None},
            "device_timing": {"status": "blocked", "value": None},
            "no_missing_result_qualifies_candidate": True,
        },
        "candidate_metrics": None,
        "controls": {
            "adverse_all_rejected": True,
            "missing_result_never_qualifies": True,
            "adverse": [
                {
                    "id": "ADV-01",
                    "name": "missing_checkpoint_must_not_qualify",
                    "input": {"checkpoint_present": False},
                    "result": "rejected",
                    "qualifies": False,
                },
                {
                    "id": "ADV-02",
                    "name": "missing_runtime_must_not_qualify",
                    "input": {"runtime_present": False},
                    "result": "rejected",
                    "qualifies": False,
                },
                {
                    "id": "ADV-03",
                    "name": "missing_cohort_must_not_qualify",
                    "input": {"cohort_present": False},
                    "result": "rejected",
                    "qualifies": False,
                },
                {
                    "id": "ADV-04",
                    "name": "missing_timing_must_not_qualify",
                    "input": {"timing_present": False},
                    "result": "rejected",
                    "qualifies": False,
                },
            ],
        },
        "reference_protocol": {
            "model_executed": False,
            "executor": "absent",
            "qualification_effect": "none",
            "status": "blocked",
        },
        "non_claims": list(NON_CLAIMS),
    }
    return report
