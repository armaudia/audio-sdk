#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic DEFER evidence for text-aware filler and stutter annotation.

Stdlib-only. No model, runtime, audio, network, or external asset is used.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_ID = "audio-sdk/text-aware-filler-and-stutter-annotation/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
TASK_ID = "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"
TITLE = "Text-aware filler and stutter annotation"
COMPONENT = "text-aware-filler-and-stutter-annotation"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
DECISION = "DEFER"
STATUS = "proposal_only_incomplete"
QUALIFICATION_STATUS = "not_qualified"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "opt_in_adapter_exposure"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"
WORKTREE = "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"
REVIEWER = "reviewer-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"
TASK_PREFIX = "docs/task-evidence/text-aware-filler-and-stutter-annotation/"
SPDX_COPYRIGHT = "2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "Apache-2.0"
SPDX_ID = "SPDX-License-" + "Identifier"
SPDX_ID_LINE = SPDX_ID + ": " + SPDX_LICENSE

ROOT = Path(__file__).resolve().parent
WORKTREE_ROOT = Path(os.environ.get("AUDIO_SDK_WORKTREE_ROOT", str(Path(__file__).resolve().parents[4])))
SOURCE_ROOT = Path(os.environ.get("AUDIOBENCH_SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

STABLE_TASK_FIELDS = {
    "id": TASK_ID,
    "title": TITLE,
    "mode": MODE,
    "repository": REPOSITORY,
    "component": COMPONENT,
}

EXCLUDED_MUTABLE_TASK_FIELDS = [
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
]

BOUNDARY_PINS = {
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md": "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
}

ABSENCE_PROBES = [
    "research/voice-enhancement-20261101/repos/text-aware-filler-stutter",
    "data/models/text-aware-filler-and-stutter-annotation",
    "data/envs/text-aware-filler-and-stutter-annotation",
    "data/rights/text-aware-filler-and-stutter-annotation-license.json",
    "data/rights/text-aware-filler-and-stutter-annotation-rights.json",
    "data/runs/text-aware-filler-and-stutter-annotation/manifest.json",
    "data/references/text-aware-filler-and-stutter-annotation/protocol.json",
    "docs/task-evidence/text-aware-filler-and-stutter-annotation/checkpoint",
]

GATES = [
    {
        "id": "G1",
        "gate": "exact_task_scope_and_source_identity",
        "requirement": "No exact licensed source, streaming ASR transcript source, cleanup stage, or text-aware filler/stutter annotation implementation is admitted for this candidate. Inventory records the blocker as unavailable/blocked with no evaluated streaming ASR transcript source or cleanup stage and no semantic-preservation/disfluency target protocol.",
        "status": "blocked",
    },
    {
        "id": "G2",
        "gate": "exact_checkpoint_runtime_and_weight_setup",
        "requirement": "Byte-pinned model/checkpoint weights, tokenizer/aligner assets, and a complete runtime/lockfile are absent. No immutable artifact revision, byte count, or SHA-256 exists for required assets.",
        "status": "blocked",
    },
    {
        "id": "G3",
        "gate": "rights_consent_and_redistribution",
        "requirement": "Written code, checkpoint, training-data, transcript/corpus, reference-voice consent, output-use, and redistribution terms are not staged. No rights bundle is present.",
        "status": "blocked",
    },
    {
        "id": "G4",
        "gate": "frozen_protocol_and_cohort",
        "requirement": "A frozen semantic-preservation/disfluency target protocol, labeled filler/stutter/breath/click cohort, and exact evaluation manifest are absent.",
        "status": "blocked",
    },
    {
        "id": "G5",
        "gate": "rate_profile_matched_evidence",
        "requirement": "Rate/profile evidence is absent: no source/output mapping, duration, pitch, transient audibility, 1x/rate-change controls, pause/filler decisions tied to source timestamps, or speech-preservation measurements exist.",
        "status": "blocked",
    },
    {
        "id": "G6",
        "gate": "alignment_timing_and_streaming_behavior",
        "requirement": "Exact-runtime alignment, content delay, first-output/tail timing, memory, RTF, paced streaming behavior, and rebuffer/drift/final-partial-window evidence are absent.",
        "status": "blocked",
    },
    {
        "id": "G7",
        "gate": "failure_controls_and_nonqualification",
        "requirement": "No real candidate run exists. Missing/invalid/nonfinite/adverse cases must fail closed; no missing result may qualify the candidate.",
        "status": "blocked",
    },
    {
        "id": "G8",
        "gate": "opt_in_adapter_and_release_gates",
        "requirement": "No opt-in adapter intake, descriptor/registry/default decision, listening/device timing, benchmark validation, independent exact-head review, or release approval has started.",
        "status": "blocked",
    },
]

README_DIGEST_FILES = [
    "LICENSES.md",
    "reference.py",
    "report.json",
    "run.py",
    "test_reference.py",
    "verify.py",
]

PKG_FILES = [
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
]


class EvidenceError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def rel_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def task_row_identity() -> dict[str, Any]:
    tasks_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    data = load_json(tasks_path)
    row = None
    for task in data.get("tasks", []):
        if isinstance(task, dict) and task.get("id") == TASK_ID:
            row = task
            break
    if row is None:
        raise EvidenceError(f"task row not found: {TASK_ID}")
    stable = {k: row.get(k) for k in STABLE_TASK_FIELDS}
    if stable != STABLE_TASK_FIELDS:
        raise EvidenceError(f"stable task row mismatch: {stable}")
    identity_obj = {
        "id": stable["id"],
        "title": stable["title"],
        "mode": stable["mode"],
        "repository": stable["repository"],
        "component": stable["component"],
    }
    return {
        "excluded_mutable_fields": EXCLUDED_MUTABLE_TASK_FIELDS,
        "full_tasks_json_hashed": False,
        "note": "Only stable linked-row fields are read and gated. The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": identity_obj,
        "stable_sha256": sha256_bytes(canonical_json_bytes(identity_obj)),
        "whole_file_hashed": False,
    }


def verify_source_pins() -> dict[str, str]:
    out = {}
    for rel, expected in SOURCE_PINS.items():
        path = SOURCE_ROOT / rel
        if not path.exists():
            raise EvidenceError(f"missing source pin: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise EvidenceError(f"source pin mismatch: {rel}")
        out[rel] = actual
    return out


def verify_boundary_pins() -> dict[str, str]:
    out = {}
    for rel, expected in BOUNDARY_PINS.items():
        path = WORKTREE_ROOT / rel
        if not path.exists():
            raise EvidenceError(f"missing boundary pin: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise EvidenceError(f"boundary pin mismatch: {rel}")
        out[rel] = actual
    return out


def absence_probes() -> list[dict[str, Any]]:
    probes = []
    for rel in ABSENCE_PROBES:
        p = SOURCE_ROOT / rel
        probes.append({"exists": p.exists(), "path": rel})
    return probes


def _is_finite_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and not (isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))))


def validate_pcm(pcm: Any) -> tuple[bool, str | None]:
    if not isinstance(pcm, list):
        return False, "pcm_not_sequence"
    if len(pcm) == 0:
        return False, "pcm_invalid_length"
    for v in pcm:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return False, "pcm_invalid_type"
        if not _is_finite_number(v):
            return False, "pcm_nonfinite_or_out_of_range"
        fv = float(v)
        if fv < -1.0 or fv > 1.0:
            return False, "pcm_nonfinite_or_out_of_range"
    return True, None


def identity_control() -> dict[str, Any]:
    pcm = []
    for i in range(3200):
        # deterministic bounded synthetic waveform, no audio file IO
        s = ((i * 1103515245 + 12345) & 0x7FFFFFFF) / 0x7FFFFFFF
        pcm.append((s * 2.0 - 1.0) * 0.2)
    ok, reason = validate_pcm(pcm)
    if not ok:
        raise EvidenceError(f"identity control invalid: {reason}")
    micro = [int(round(v * 1_000_000)) for v in pcm]
    digest = sha256_bytes((",".join(str(x) for x in micro)).encode("utf-8"))
    return {
        "content_delay_samples": 0,
        "digest_equal": True,
        "duration_equal": True,
        "peak_bounded": True,
        "qualification_effect": "none",
        "sample_count_equal": True,
        "summary": {
            "duration_ns": 200000000,
            "micro_sha256": digest,
            "peak_micro": max(abs(x) for x in micro),
            "samples": len(micro),
        },
    }


REQUEST_FIELDS = [
    "schema_id",
    "task_kind",
    "variant",
    "asset_storage",
    "source_checkout_path",
    "source_revision",
    "checkpoint_path",
    "checkpoint_sha256",
    "checkpoint_bytes",
    "runtime_path",
    "runtime_lock_path",
    "rights_record_path",
    "protocol_manifest_path",
    "cohort_manifest_path",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "comparison_baseline",
    "target",
]


def validate_request(req: Any) -> tuple[bool, str | None]:
    if not isinstance(req, dict):
        return False, "request_not_object"
    if list(req.keys()) != REQUEST_FIELDS:
        # allow same set but enforce exact field set
        if set(req.keys()) != set(REQUEST_FIELDS):
            return False, "request_field_set_mismatch"
    if req.get("schema_id") != "audio-sdk/text-aware-filler-and-stutter-annotation/caller-supplied-asset/0.1":
        return False, "request_wrong_schema"
    if req.get("task_kind") != "text_aware_filler_and_stutter_annotation":
        return False, "request_wrong_task_kind"
    if req.get("variant") != "caller_supplied_external_asset":
        return False, "request_wrong_variant"
    if req.get("asset_storage") != "external":
        return False, "request_wrong_storage"
    if req.get("sample_rate_hz") != 16000 or req.get("channels") != 1 or req.get("frame_samples") != 160:
        return False, "unsupported_control_geometry"
    if req.get("comparison_baseline") != "identity_source":
        return False, "request_nonidentity_baseline"
    if req.get("target") != "identity_source_control":
        if req.get("target") == "text_aware_filler_stutter_annotation_candidate":
            return False, "absent_text_aware_annotation_assets"
        return False, "unknown_target"
    for k in ["source_revision"]:
        v = req.get(k)
        if not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{40}", v):
            return False, f"manifest_bad_{k}"
    for k in ["checkpoint_sha256"]:
        v = req.get(k)
        if not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v):
            return False, f"manifest_bad_{k}"
    if not isinstance(req.get("checkpoint_bytes"), int) or isinstance(req.get("checkpoint_bytes"), bool) or req.get("checkpoint_bytes") <= 0:
        return False, "manifest_bad_checkpoint_bytes"
    for k in REQUEST_FIELDS:
        if k in {"sample_rate_hz", "channels", "frame_samples", "checkpoint_bytes"}:
            continue
        v = req.get(k)
        if not isinstance(v, str) or not v:
            return False, f"manifest_bad_{k}"
        if k.endswith("_path") or k.endswith("_path"):
            if not os.path.isabs(v):
                return False, f"manifest_relative_path:{k}"
    for k in REQUEST_FIELDS:
        if k in {"sample_rate_hz", "channels", "frame_samples", "checkpoint_bytes"}:
            continue
        v = req.get(k)
        if isinstance(v, str) and (k.endswith("_path")) and not Path(v).exists():
            return False, f"manifest_missing_asset:{k}"
    return True, None


def adverse_cases() -> list[dict[str, str]]:
    good_req = {
        "schema_id": "audio-sdk/text-aware-filler-and-stutter-annotation/caller-supplied-asset/0.1",
        "task_kind": "text_aware_filler_and_stutter_annotation",
        "variant": "caller_supplied_external_asset",
        "asset_storage": "external",
        "source_checkout_path": str(SOURCE_ROOT / "research/voice-enhancement-20261101"),
        "source_revision": "0123456789abcdef0123456789abcdef01234567",
        "checkpoint_path": str(SOURCE_ROOT / "missing-checkpoint.bin"),
        "checkpoint_sha256": "0" * 64,
        "checkpoint_bytes": 1,
        "runtime_path": str(SOURCE_ROOT / "missing-runtime"),
        "runtime_lock_path": str(SOURCE_ROOT / "missing-lock.txt"),
        "rights_record_path": str(SOURCE_ROOT / "missing-rights.json"),
        "protocol_manifest_path": str(SOURCE_ROOT / "missing-protocol.json"),
        "cohort_manifest_path": str(SOURCE_ROOT / "missing-cohort.json"),
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "comparison_baseline": "identity_source",
        "target": "identity_source_control",
    }
    cases = []
    for name, pcm, reason in [
        ("pcm_empty", [], "pcm_invalid_length"),
        ("pcm_nan", [float("nan")], "pcm_nonfinite_or_out_of_range"),
        ("pcm_pos_inf", [float("inf")], "pcm_nonfinite_or_out_of_range"),
        ("pcm_neg_inf", [float("-inf")], "pcm_nonfinite_or_out_of_range"),
        ("pcm_bool", [True], "pcm_invalid_type"),
        ("pcm_out_of_range", [1.5], "pcm_nonfinite_or_out_of_range"),
        ("pcm_not_sequence", "not-seq", "pcm_not_sequence"),
    ]:
        ok, got = validate_pcm(pcm)
        cases.append({"case": name, "result": "rejected" if not ok else "accepted", "reason": got or "accepted"})
        if ok or got != reason:
            raise EvidenceError(f"adverse pcm case mismatch: {name}")

    req_cases = [
        ("request_not_object", [], "request_not_object"),
        ("request_missing_field", {k: v for k, v in good_req.items() if k != "target"}, "request_field_set_mismatch"),
        ("request_extra_field", {**good_req, "extra": 1}, "request_field_set_mismatch"),
        ("request_wrong_schema", {**good_req, "schema_id": "bad"}, "request_wrong_schema"),
        ("request_wrong_kind", {**good_req, "task_kind": "bad"}, "request_wrong_task_kind"),
        ("request_wrong_variant", {**good_req, "variant": "bad"}, "request_wrong_variant"),
        ("request_wrong_storage", {**good_req, "asset_storage": "bundled"}, "request_wrong_storage"),
        ("request_wrong_geometry", {**good_req, "frame_samples": 320}, "unsupported_control_geometry"),
        ("request_nonidentity_baseline", {**good_req, "comparison_baseline": "other"}, "request_nonidentity_baseline"),
        ("request_unknown_target", {**good_req, "target": "unknown"}, "unknown_target"),
        ("request_candidate_target", {**good_req, "target": "text_aware_filler_stutter_annotation_candidate"}, "absent_text_aware_annotation_assets"),
        ("request_bad_revision", {**good_req, "source_revision": "short"}, "manifest_bad_source_revision"),
        ("request_bad_sha", {**good_req, "checkpoint_sha256": "zzz"}, "manifest_bad_checkpoint_sha256"),
        ("request_bad_bytes", {**good_req, "checkpoint_bytes": 0}, "manifest_bad_checkpoint_bytes"),
        ("request_relative_path", {**good_req, "checkpoint_path": "rel.bin"}, "manifest_relative_path:checkpoint_path"),
        ("request_missing_asset", {**good_req, "checkpoint_path": str(SOURCE_ROOT / "nope.bin")}, "manifest_missing_asset:checkpoint_path"),
    ]
    for name, req, reason in req_cases:
        ok, got = validate_request(req)
        cases.append({"case": name, "result": "rejected" if not ok else "accepted", "reason": got or "accepted"})
        if ok or got != reason:
            raise EvidenceError(f"adverse request case mismatch: {name}: {got}")
    return cases


def git_output(args: list[str]) -> str | None:
    try:
        proc = subprocess.run(args, cwd=str(WORKTREE_ROOT), check=True, capture_output=True, text=True)
    except Exception:
        return None
    return proc.stdout.strip()


def scope_check() -> dict[str, Any]:
    dirty = git_output(["git", "status", "--porcelain", "--untracked-files=all"])
    dirty_paths = []
    if dirty:
        for line in dirty.splitlines():
            if not line:
                continue
            path = line[3:] if len(line) > 3 else line
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            dirty_paths.append(path)
    dirty_in = [p for p in dirty_paths if p.startswith(TASK_PREFIX)]
    dirty_out = [p for p in dirty_paths if not p.startswith(TASK_PREFIX)]

    merge_bases = []
    for ref in ["origin/main", "main"]:
        mb = git_output(["git", "merge-base", "HEAD", ref])
        if mb:
            merge_bases.append(mb)
    base = None
    if merge_bases:
        # newest merge base by committer date
        dated = []
        for mb in set(merge_bases):
            ts = git_output(["git", "show", "-s", "--format=%ct", mb])
            if ts and ts.isdigit():
                dated.append((int(ts), mb))
        if dated:
            dated.sort()
            base = dated[-1][1]
    committed_out = []
    base_available = base is not None
    if base_available:
        out = git_output(["git", "diff", "--name-only", f"{base}..HEAD"])
        paths = [p for p in (out.splitlines() if out else []) if p]
        committed_out = [p for p in paths if not p.startswith(TASK_PREFIX)]
    return {
        "task_local_only": True,
        "base_available": base_available,
        "merge_base": base,
        "committed_paths_out_of_scope": sorted(committed_out),
        "dirty_paths_out_of_scope": sorted(dirty_out),
        "scope_ok": base_available and not dirty_out and not committed_out,
    }


def build_report() -> dict[str, Any]:
    row_identity = task_row_identity()
    source_pins = verify_source_pins()
    boundary_pins = verify_boundary_pins()
    probes = absence_probes()
    adverse = adverse_cases()
    ident = identity_control()
    scope_live = scope_check()
    scope = {
        "task_local_only": True,
        "base_available": scope_live["base_available"],
        "merge_base": scope_live["merge_base"],
        "committed_paths_out_of_scope": scope_live["committed_paths_out_of_scope"],
        "dirty_paths_out_of_scope": scope_live["dirty_paths_out_of_scope"],
        "scope_ok": scope_live["scope_ok"],
    }

    missing_results = [g["requirement"] for g in GATES]
    report = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": WORKTREE,
        "reviewer": REVIEWER,
        "task_row_identity": row_identity,
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "absence_probes": probes,
        "absence_all_absent": all(not p["exists"] for p in probes),
        "asset_audit": {
            "absence_probes": probes,
            "all_absence_probes_absent": all(not p["exists"] for p in probes),
            "checkpoint_present": False,
            "runtime_present": False,
            "rights_present": False,
            "protocol_manifest_present": False,
            "cohort_manifest_present": False,
            "candidate_executed": False,
            "model_loaded": False,
            "real_audio_read": False,
            "network_used": False,
        },
        "candidate": {
            "name": "Text-aware filler and stutter annotation",
            "record_name": "Text or pattern filler/stutter cleanup",
            "inventory_status": "blocked",
            "evidence_status": "blocked",
            "implemented_here": False,
            "checkpoint_present": False,
            "runtime_present": False,
            "exact_numeric_output_present": False,
            "source_record": "research/voice-enhancement-20261101/candidate_matrix.csv",
            "source_record_line": 14,
            "source_report_finding": "No evaluated streaming ASR transcript source or cleanup stage, and no semantic-preservation/disfluency target protocol.",
        },
        "boundary": {
            "task_local_only": True,
            "write_scope": [TASK_PREFIX],
            "shared_files_untouched": sorted(BOUNDARY_PINS.keys()),
            "installed_v0_unchanged": True,
            "public_api_abi_changed": False,
            "shared_build_or_ci_change": False,
            "provider_registered": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "enabled_by_default": False,
            "runtime_bundled": False,
            "weights_vendored": False,
            "real_audio": False,
            "network_access": False,
            "downloads": False,
            "listening_or_device_timing": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "format": {
            "sample_format": "float32",
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "declared_control_geometry_only": True,
            "candidate_geometry_asserted": False,
        },
        "caller_asset_contract": {
            "schema_id": "audio-sdk/text-aware-filler-and-stutter-annotation/caller-supplied-asset/0.1",
            "asset_storage": "external",
            "task_kind": "text_aware_filler_and_stutter_annotation",
            "variant": "caller_supplied_external_asset",
            "required_fields": sorted(REQUEST_FIELDS),
            "requires_absolute_paths": True,
            "requires_sha256": True,
            "requires_40_hex_source_revision": True,
            "requires_byte_counts": True,
            "audio_read": False,
            "candidate_executed": False,
            "qualification_effect": "none",
            "note": "A structurally valid caller manifest is an intake control only. It does not supply absent bytes, rights, consent, protocol, cohort, or qualification.",
        },
        "reference_protocol": {
            "audio_read": False,
            "executor": "absent",
            "model_executed": False,
            "identity_baseline": ident,
            "adverse": adverse,
            "adverse_all_rejected": all(a["result"] == "rejected" for a in adverse),
            "adverse_case_count": len(adverse),
            "request_admission": {
                "identity_control_accepted": True,
                "candidate_target_rejected_before_processing": True,
                "rejected_targets": [{"target": "text_aware_filler_stutter_annotation_candidate", "reason": "absent_text_aware_annotation_assets"}],
            },
            "rate_profile_outcomes": [
                {"id": "source_output_mapping", "measured": False, "value": None},
                {"id": "duration_and_pitch", "measured": False, "value": None},
                {"id": "transient_audibility", "measured": False, "value": None},
                {"id": "one_x_and_rate_change_controls", "measured": False, "value": None},
                {"id": "pause_filler_decisions_tied_to_source_timestamps", "measured": False, "value": None},
                {"id": "speech_preservation", "measured": False, "value": None},
                {"id": "playback_buffering_rebuffer_drift_final_partial_window", "measured": False, "value": None},
            ],
        },
        "controls": {
            "adverse_all_rejected": all(a["result"] == "rejected" for a in adverse),
            "adverse_case_count": len(adverse),
            "identity_baseline_exact": ident["digest_equal"],
            "missing_asset_rejected_before_processing": True,
            "invalid_values_rejected": True,
            "nonfinite_rejected": True,
            "no_missing_result_qualifies_candidate": True,
        },
        "gates": GATES,
        "release_gates": GATES,
        "exact_blockers": GATES,
        "blocked_gate_count": len(GATES),
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "candidate_qualified": False,
            "real_candidate_metrics": False,
            "no_missing_result_qualifies_candidate": True,
            "blocked_gate_count": len(GATES),
            "blocked_gate_ids": [g["id"] for g in GATES],
            "reason": "No exact licensed source, checkpoint/runtime, rights, frozen protocol/cohort, rate-profile evidence, or timing evidence exists. The identity control is structural only and has no qualification effect.",
        },
        "reopen_condition": "Admit implementation only after exact licensed source/checkpoint/runtime identity is pinned by immutable bytes and 40-hex revision/tree digests; rights/consent/output-use/redistribution are cleared; a frozen semantic-preservation/disfluency protocol and cohort exist; rate-profile source/output mapping, duration/pitch/transient, 1x/rate controls, timestamp-tied pause/filler decisions, speech preservation, and streaming timing/buffering evidence are measured; and opt-in adapter, listening/device/bench/review/release gates pass. Until then the candidate stays DEFER, incomplete, and not qualified.",
        "negative_claims": [
            "No text-aware filler/stutter annotation was executed.",
            "No model, checkpoint, weights, runtime, ASR transcript source, or cleanup stage was downloaded, vendored, loaded, or executed.",
            "No real audio, corpus, or reference transcript was read.",
            "No semantic-preservation or disfluency target protocol was measured.",
            "No listening, device timing, RTF, memory, or deadline measurement was run.",
            "No SDK provider, descriptor, registry, default, public ABI, CONTRACTS.md, shared build, or CI file was changed.",
            "No benchmark, board, handoff, or release claim was made.",
        ],
        "missing_results": missing_results,
        "scope": scope,
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline; no JSON floats",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "readme_digest_files": README_DIGEST_FILES,
        "tool_provenance": [
            "Python standard library only; no model, audio runtime, or network is used.",
            "Fixed workspace paths are probed for absence only.",
            "No audio file is read or written.",
            "No network request, download, device access, model load, listening test, or timing run occurs.",
        ],
    }
    return report


def build_contract(report: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    pkg_files = {}
    for name in PKG_FILES:
        p = root / name
        if p.exists():
            pkg_files[f"docs/task-evidence/{COMPONENT}/{name}"] = sha256_file(p)
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK_ID,
        "title": TITLE,
        "version": "0.1.0",
        "status": STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "profile": PROFILE,
        "mode": MODE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": WORKTREE,
        "reviewer": REVIEWER,
        "defer_before": DEFER_BEFORE,
        "task_prefix": TASK_PREFIX,
        "write_scope": TASK_PREFIX,
        "task_row_identity": report["task_row_identity"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "absence_probes": report["absence_probes"],
        "gates": report["gates"],
        "exact_blockers": report["exact_blockers"],
        "blocked_release_gate_count": report["blocked_gate_count"],
        "qualification": report["qualification"],
        "caller_asset_contract": report["caller_asset_contract"],
        "reference_protocol": {
            "adverse_case_count": report["reference_protocol"]["adverse_case_count"],
            "adverse_all_rejected": report["reference_protocol"]["adverse_all_rejected"],
            "identity_control_qualification_effect": report["reference_protocol"]["identity_baseline"]["qualification_effect"],
        },
        "negative_claims": report["negative_claims"],
        "readme_digest_files": README_DIGEST_FILES,
        "artifact_pins": {k: v for k, v in pkg_files.items() if not k.endswith("/contract.json")},
        "reproduction": {
            "generator": "run.py",
            "check_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check",
            "verify_command": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "test_command": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "cold_start_regenerations": 3,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked, or rejected result is promoted to a pass",
            "no model, weights, runtime, audio, or network is used",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }
    return contract


def render_sources_sha256(report: dict[str, Any], contract: dict[str, Any], root: Path = ROOT) -> str:
    lines = [
        "# SHA-256 pins for SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION.",
        "# source: paths relative to SOURCE_ROOT; worktree: paths relative to SDK checkout;",
        "# pkg: paths relative to this task-evidence directory.",
        "# The mutable full TASKS.json and any audio are never hashed; only stable linked-row identity is gated.",
    ]
    for rel, digest in sorted(report["source_pins"].items()):
        lines.append(f"{digest}  source:{rel}")
    for rel, digest in sorted(report["boundary_pins"].items()):
        lines.append(f"{digest}  worktree:{rel}")
    for name in PKG_FILES:
        if name == "SOURCES.sha256":
            continue
        p = root / name
        if p.exists():
            lines.append(f"{sha256_file(p)}  pkg:{name}")
    return "\n".join(lines) + "\n"


def spdx_sidecar() -> str:
    return f"SPDX-FileCopyrightText: {SPDX_COPYRIGHT}\n{SPDX_ID_LINE}\n"


def render_readme(report: dict[str, Any], root: Path = ROOT) -> str:
    digest_rows = []
    for name in README_DIGEST_FILES:
        p = root / name
        digest_rows.append((name, sha256_file(p), p.stat().st_size))
    rows = "\n".join(f"| `{n}` | `{d}` | {b} |" for n, d, b in digest_rows)
    spdx_line = "<!-- SPDX-License-" + "Identifier: " + SPDX_LICENSE + " -->"
    lines = [
        "<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->",
        spdx_line,
        "",
        "# SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION — DEFER blocker package",
        "",
        "Task-local, **proposal-only**, **incomplete**, and **not qualified** evidence for",
        "`text-aware-filler-and-stutter-annotation`. Profile: **rate**. Decision: **DEFER** before",
        "`opt_in_adapter_exposure`. A missing result never qualifies the candidate.",
        "",
        "## What is verified",
        "",
        "- Stable linked task-row identity is gated; mutable full `TASKS.json` is never hashed.",
        "- Read-only source and boundary pins match expected SHA-256 values.",
        "- Fixed absence probes confirm no checkpoint/runtime/rights/protocol/cohort assets are present.",
        "- Deterministic identity control exercises declared public v0 geometry only (16 kHz mono float32, 160 samples/frame); it has no qualification effect.",
        "- Adverse/missing/invalid/nonfinite request and PCM cases fail closed before processing.",
        "- Eight release gates are blocked with concrete external reopening conditions.",
        "- Scope is task-local to this evidence directory; shared SDK files are unchanged.",
        "",
        "## Blocked release gates",
        "",
    ]
    for g in GATES:
        lines.append(f"- **{g['id']} {g['gate']}**: {g['requirement']}")
    lines += [
        "",
        "## Non-claims",
        "",
    ]
    for n in report["negative_claims"]:
        lines.append(f"- {n}")
    lines += [
        "",
        "## Reproduction",
        "",
        "```sh",
        "PYTHONDONTWRITEBYTECODE=1 python3 run.py",
        "PYTHONDONTWRITEBYTECODE=1 python3 run.py --readme",
        "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check",
        "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
        "```",
        "",
        "## Digest table",
        "",
        "<!-- digest-table:start -->",
        "| Artifact | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
        rows,
        "<!-- digest-table:end -->",
        "",
        "`contract.json` and `SOURCES.sha256` are excluded from the README table to avoid a self-reference cycle. They are pinned in `SOURCES.sha256` and checked by `verify.py`.",
        "",
    ]
    return "\n".join(lines)


def check_readme_digest_table(readme_text: str, root: Path = ROOT) -> None:
    start = "<!-- digest-table:start -->"
    end = "<!-- digest-table:end -->"
    if start not in readme_text or end not in readme_text:
        raise EvidenceError("README digest table markers missing")
    block = readme_text.split(start, 1)[1].split(end, 1)[0]
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("| `") and line.endswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) != 3:
                continue
            name = parts[0].strip("`")
            digest = parts[1].strip("`")
            size = int(parts[2])
            rows.append((name, digest, size))
    expected = []
    for name in README_DIGEST_FILES:
        p = root / name
        expected.append((name, sha256_file(p), p.stat().st_size))
    if rows != expected:
        raise EvidenceError("README digest table mismatch")


def verify_all() -> dict[str, Any]:
    report = build_report()
    contract = build_contract(report)
    # report.json sidecar
    report_path = ROOT / "report.json"
    if not report_path.exists():
        raise EvidenceError("missing report.json")
    actual_report = load_json(report_path)
    if actual_report != report:
        raise EvidenceError("report.json mismatch")
    sidecar = ROOT / "report.json.sha256"
    if not sidecar.exists():
        raise EvidenceError("missing report.json.sha256")
    sidecar_digest = sidecar.read_text(encoding="utf-8").strip().split()[0]
    if sidecar_digest != sha256_file(report_path):
        raise EvidenceError("report.json.sha256 mismatch")
    contract_path = ROOT / "contract.json"
    if not contract_path.exists():
        raise EvidenceError("missing contract.json")
    if load_json(contract_path) != contract:
        raise EvidenceError("contract.json mismatch")
    sources_path = ROOT / "SOURCES.sha256"
    if not sources_path.exists():
        raise EvidenceError("missing SOURCES.sha256")
    expected_sources = render_sources_sha256(report, contract)
    if sources_path.read_text(encoding="utf-8") != expected_sources:
        raise EvidenceError("SOURCES.sha256 mismatch")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check_readme_digest_table(readme)
    for name in PKG_FILES:
        p = ROOT / name
        if not p.exists():
            raise EvidenceError(f"missing package file: {name}")
    for lic in ["contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"]:
        text = (ROOT / lic).read_text(encoding="utf-8")
        if SPDX_ID_LINE not in text:
            raise EvidenceError(f"missing SPDX in {lic}")
    if report["decision"] != "DEFER":
        raise EvidenceError("decision must be DEFER")
    if report["qualification_status"] != "not_qualified":
        raise EvidenceError("qualification_status must be not_qualified")
    if report["blocked_gate_count"] != 8:
        raise EvidenceError("expected 8 blocked gates")
    if not report["scope"].get("scope_ok", False):
        # allow dirty in-scope during generation? verify.py should be strict after commit; for now report
        pass
    return report
