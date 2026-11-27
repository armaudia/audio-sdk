# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence reference for whisper-tiny-en-int8-via-sherpa-onnx.

Deterministic, stdlib-only, no network, no model/runtime import or execution.
This package records a DEFER/incomplete/not_qualified research-control outcome.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

TASK_ID = "SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX"
COMPONENT = "whisper-tiny-en-int8-via-sherpa-onnx"
PROFILE = "evidence"
DECISION = "DEFER"
STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX"
TASK_PREFIX = f"docs/task-evidence/{COMPONENT}/"

HERE = Path(__file__).resolve().parent
WORKTREE = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(WORKTREE.parents[2]))).resolve()

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_ROW = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_MD = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

SOURCE_PINS: dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed/README.md": (
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f"
    ),
    INVENTORY_ROW: "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_MD: "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS: dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
}

# Local scratch model bytes are provenance-only probes; they are not vendored,
# not admitted, and not required for qualification.
PROVENANCE_MODEL_FILES: dict[str, dict[str, Any]] = {
    "cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-decoder.int8.onnx": {
        "sha256": "06c0e6ff6348d427e51839219d1c886c18cfdf411e629e33f5e1679bff9c1527",
        "bytes": 89853865,
    },
    "cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-decoder.onnx": {
        "sha256": "54d5a5fd2a757175aeb70a837a8404fc9c31b659610724694f5a0e2c51715f94",
        "bytes": 114504265,
    },
    "cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-encoder.int8.onnx": {
        "sha256": "0ce578b827c94a961aacb8fa14b02f096504b337e5c94be37c36238cbe3e8bc6",
        "bytes": 12937772,
    },
    "cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-encoder.onnx": {
        "sha256": "dc7de696432d97a3d64387800b230ac69d18e5e4efea0eec0613209dd8b7b0c9",
        "bytes": 37647080,
    },
    "cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-tokens.txt": {
        "sha256": "306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930",
        "bytes": 835554,
    },
}

LOCAL_PIN_FILES = (
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

FORBIDDEN_SUFFIXES = {
    ".onnx", ".pt", ".pth", ".bin", ".safetensors", ".wav", ".mp3", ".flac",
    ".m4a", ".ogg", ".opus", ".mp4", ".zip", ".tar", ".gz", ".bz2", ".dylib",
    ".so", ".dll", ".a", ".lib", ".exe", ".wasm", ".pyc",
}

REQUIRED_BLOCKERS = [
    {
        "id": "B1",
        "title": "exact_source_and_license_unpinned",
        "detail": "No exact sherpa-onnx source revision, archive digest, complete Apache-2.0 license/NOTICE bundle, or third-party notice review is staged.",
        "status": "open",
    },
    {
        "id": "B2",
        "title": "model_identity_and_terms_unreviewed",
        "detail": "Whisper tiny.en int8 ONNX model/tokenizer identity, conversion provenance, and model/output-use/distribution terms are not independently reviewed or admitted.",
        "status": "open",
    },
    {
        "id": "B3",
        "title": "pinned_offline_runtime_absent",
        "detail": "No pinned offline sherpa-onnx runtime/package lock, deterministic install/import/load proof, or clean-room execution record exists.",
        "status": "open",
    },
    {
        "id": "B4",
        "title": "rights_cleared_eval_assets_absent",
        "detail": "No rights-cleared, task-matched audio/transcript cohort with frozen normalization/scorer and representative invalid/missing control is staged.",
        "status": "open",
    },
    {
        "id": "B5",
        "title": "no_reproduced_result_or_timing",
        "detail": "No reproduced transcript-drift run, no target-device timing/resources, no listening, and no benchmark/release evidence exists.",
        "status": "open",
    },
    {
        "id": "B6",
        "title": "intake_and_review_incomplete",
        "detail": "No separate opt-in adapter/provider intake, OFF-by-default registration, or independent exact-head review is present.",
        "status": "open",
    },
]

REQUIRED_GATES = [
    {"id": "RG-01", "title": "source_revision_and_license", "status": "blocked"},
    {"id": "RG-02", "title": "model_asset_identity_and_terms", "status": "blocked"},
    {"id": "RG-03", "title": "pinned_offline_runtime", "status": "blocked"},
    {"id": "RG-04", "title": "rights_cleared_eval_cohort", "status": "blocked"},
    {"id": "RG-05", "title": "reproduced_scoring_with_controls", "status": "blocked"},
    {"id": "RG-06", "title": "target_timing_and_resources", "status": "blocked"},
    {"id": "RG-07", "title": "listening_or_human_review_if_claimed", "status": "blocked"},
    {"id": "RG-08", "title": "opt_in_intake_and_exact_head_review", "status": "blocked"},
]


class ReferenceError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def git_head(root: Path = WORKTREE) -> str:
    env = os.environ.get("EVIDENCE_HEAD")
    if env:
        return env.strip()
    proc = _git(root, "rev-parse", "HEAD")
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def git_branch(root: Path = WORKTREE) -> str:
    env = os.environ.get("EVIDENCE_BRANCH")
    if env:
        return env.strip()
    proc = _git(root, "branch", "--show-current")
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def resolve_scope_base(root: Path = WORKTREE) -> dict[str, Any]:
    for ref in ("origin/main", "main"):
        mb = _git(root, "merge-base", "HEAD", ref)
        if mb.returncode == 0 and mb.stdout.strip():
            return {
                "base_ref": ref,
                "merge_base": mb.stdout.strip(),
                "status": "ok",
            }
    return {
        "base_ref": None,
        "merge_base": None,
        "status": "scope_base_unavailable",
    }


def branch_diff_paths(root: Path = WORKTREE) -> dict[str, Any]:
    base = resolve_scope_base(root)
    if base["status"] != "ok":
        return {**base, "paths": [], "violations": ["scope_base_unavailable"]}
    diff = _git(root, "diff", "--name-only", f"{base['merge_base']}..HEAD")
    if diff.returncode != 0:
        return {**base, "paths": [], "violations": ["scope_base_unavailable"]}
    paths = [p for p in diff.stdout.splitlines() if p.strip()]
    violations = [p for p in paths if not p.startswith(TASK_PREFIX)]
    return {**base, "paths": paths, "violations": violations}


def working_tree_paths(root: Path = WORKTREE) -> list[str]:
    proc = _git(root, "status", "--porcelain", "--untracked-files=all")
    if proc.returncode != 0:
        raise ReferenceError(f"git_status_failed:{proc.stderr.strip()}")
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        entry = line[3:] if len(line) > 3 else ""
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        if entry:
            paths.append(entry)
    return paths


def working_tree_violations(root: Path = WORKTREE) -> list[str]:
    return [p for p in working_tree_paths(root) if not p.startswith(TASK_PREFIX)]


def read_board_row() -> dict[str, Any]:
    data = load_json(AUDIO_ROOT / BOARD_TASK_ROW)
    tasks = data.get("tasks", []) if isinstance(data, dict) else []
    for task in tasks:
        if isinstance(task, dict) and task.get("id") == TASK_ID:
            stable = {
                "id": task.get("id"),
                "title": task.get("title"),
                "repository": task.get("repository"),
                "mode": task.get("mode"),
                "depends_on": task.get("depends_on"),
                "write_scope": task.get("write_scope"),
                "deliverable": task.get("deliverable"),
                "acceptance": task.get("acceptance"),
                "evidence": task.get("evidence"),
                "component": task.get("component"),
            }
            return {
                "board_path": BOARD_TASK_ROW,
                "stable_projection": stable,
                "stable_projection_sha256": sha256_bytes(canonical_bytes(stable)),
                "mutable_status_observed": task.get("status"),
                "note": "Board row is read for stable projection only; mutable status/claim/review fields do not gate evidence.",
            }
    raise ReferenceError("board_row_not_found")


def read_inventory_row() -> dict[str, Any]:
    data = load_json(AUDIO_ROOT / INVENTORY_ROW)
    rows = data.get("components", []) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ReferenceError("inventory_not_list")
    for row in rows:
        if isinstance(row, dict) and row.get("id") == COMPONENT:
            return row
    raise ReferenceError("inventory_row_not_found")


def evidence_profile_row() -> dict[str, Any]:
    text = (AUDIO_ROOT / VERIFICATION_MD).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("| Evidence |"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            return {"profile": "evidence", "row": cells[1] if len(cells) > 1 else ""}
    raise ReferenceError("evidence_profile_missing")


def pin_manifest() -> dict[str, dict[str, str]]:
    manifest: dict[str, dict[str, str]] = {}
    for rel, expected in SOURCE_PINS.items():
        p = AUDIO_ROOT / rel
        manifest[f"source:{rel}"] = {
            "path": rel,
            "sha256": sha256_file(p) if p.exists() else "MISSING",
            "expected": expected,
            "root": "audio_root",
        }
    for rel, expected in BOUNDARY_PINS.items():
        p = WORKTREE / rel
        manifest[f"worktree:{rel}"] = {
            "path": rel,
            "sha256": sha256_file(p) if p.exists() else "MISSING",
            "expected": expected,
            "root": "worktree",
        }
    return manifest


def provenance_model_probe() -> list[dict[str, Any]]:
    rows = []
    for rel, meta in PROVENANCE_MODEL_FILES.items():
        p = AUDIO_ROOT / rel
        exists = p.exists()
        row = {
            "path": rel,
            "exists": exists,
            "expected_sha256": meta["sha256"],
            "expected_bytes": meta["bytes"],
            "observed_sha256": sha256_file(p) if exists else None,
            "observed_bytes": p.stat().st_size if exists else None,
            "role": "provenance_only_not_vendored_not_admitted",
        }
        if exists:
            row["digest_match"] = row["observed_sha256"] == meta["sha256"]
            row["bytes_match"] = row["observed_bytes"] == meta["bytes"]
        rows.append(row)
    return rows


def build_contract() -> dict[str, Any]:
    board = read_board_row()
    inventory = read_inventory_row()
    profile = evidence_profile_row()
    return {
        "schema": "audio-sdk.task-evidence.contract/v1",
        "task_id": TASK_ID,
        "component": COMPONENT,
        "title": inventory.get("name", "Whisper tiny.en int8 via sherpa-onnx"),
        "profile": PROFILE,
        "profile_row": profile["row"],
        "decision": DECISION,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": [TASK_PREFIX],
        "board_projection": board,
        "inventory_row": {
            "id": inventory.get("id"),
            "verification_profile": inventory.get("verification_profile"),
            "disposition": inventory.get("disposition"),
            "evidence_status": inventory.get("evidence_status"),
            "plan_note": inventory.get("plan_note"),
            "task": inventory.get("task"),
        },
        "blockers": REQUIRED_BLOCKERS,
        "release_gates": REQUIRED_GATES,
        "claims": {
            "provider_or_adapter_registered": False,
            "default_changed": False,
            "abi_or_contracts_changed": False,
            "shared_build_or_ci_changed": False,
            "runtime_or_model_downloaded": False,
            "real_audio_or_listening_used": False,
            "device_timing_or_benchmark_claimed": False,
            "release_claimed": False,
        },
        "allowed_evidence": [
            "pinned source provenance",
            "fixed absence probes",
            "deterministic contract/report generation",
            "synthetic schema/admission control only",
        ],
    }


def _admission_case(case_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    required = [
        "source_revision", "source_archive_sha256", "source_license_spdx",
        "model_id", "model_revision", "model_sha256", "tokenizer_sha256",
        "runtime_version", "runtime_lock_sha256", "audio_corpus_id",
        "transcript_manifest_sha256", "scorer_id", "scorer_version",
        "normalization_id", "invalid_control_present", "rights_reviewed",
    ]
    for k in required:
        if k not in manifest:
            reasons.append(f"missing:{k}")
    if manifest.get("source_license_spdx") not in (None, "Apache-2.0"):
        reasons.append("license_not_approved")
    if manifest.get("rights_reviewed") is not True:
        reasons.append("rights_not_reviewed")
    if manifest.get("invalid_control_present") is not True:
        reasons.append("invalid_control_missing")
    for k in ["source_archive_sha256", "model_sha256", "tokenizer_sha256", "runtime_lock_sha256", "transcript_manifest_sha256"]:
        v = manifest.get(k)
        if v is not None and (not isinstance(v, str) or len(v) != 64):
            reasons.append(f"bad_digest:{k}")
    if "model_files" in manifest and not isinstance(manifest["model_files"], list):
        reasons.append("model_files_not_list")
    status = "accepted_for_schema_only" if not reasons else "rejected"
    return {
        "case_id": case_id,
        "status": status,
        "reasons": reasons,
        "qualifies": False,
        "state_advanced": False,
    }


def admission_cases() -> list[dict[str, Any]]:
    valid = {
        "source_revision": "0" * 40,
        "source_archive_sha256": "1" * 64,
        "source_license_spdx": "Apache-2.0",
        "source_notice_sha256": "2" * 64,
        "model_id": "sherpa-onnx-whisper-tiny.en-int8",
        "model_revision": "upstream-revision",
        "model_sha256": "3" * 64,
        "model_files": ["tiny.en-encoder.int8.onnx", "tiny.en-decoder.int8.onnx", "tiny.en-tokens.txt"],
        "tokenizer_sha256": "4" * 64,
        "runtime_version": "sherpa-onnx-pinned",
        "runtime_lock_sha256": "5" * 64,
        "audio_corpus_id": "rights-cleared-corpus",
        "transcript_manifest_sha256": "6" * 64,
        "scorer_id": "wer-normalized",
        "scorer_version": "1",
        "normalization_id": "frozen-text-norm",
        "invalid_control_present": True,
        "rights_reviewed": True,
    }
    cases = [_admission_case("valid-shape-control", dict(valid))]
    missing = dict(valid)
    missing.pop("model_sha256")
    cases.append(_admission_case("missing-model-digest", missing))
    bad_license = dict(valid)
    bad_license["source_license_spdx"] = "UNKNOWN"
    cases.append(_admission_case("unreviewed-license", bad_license))
    no_rights = dict(valid)
    no_rights["rights_reviewed"] = False
    cases.append(_admission_case("rights-unreviewed", no_rights))
    no_control = dict(valid)
    no_control["invalid_control_present"] = False
    cases.append(_admission_case("missing-invalid-control", no_control))
    bad_digest = dict(valid)
    bad_digest["runtime_lock_sha256"] = "abc"
    cases.append(_admission_case("bad-digest-shape", bad_digest))
    for c in cases:
        c["synthetic"] = True
        c["counts_as_qualification"] = False
    return cases


def synthetic_scorer_control() -> dict[str, Any]:
    # Deterministic arithmetic-only control: no audio, no ASR, no model.
    ref = ["the", "quick", "brown", "fox"]
    hyp = ["the", "quick", "red", "fox"]
    edits = 1  # substitution brown->red
    wer = edits / len(ref)
    return {
        "id": "synthetic-wer-arithmetic",
        "synthetic": True,
        "qualifies": False,
        "reference_tokens": ref,
        "hypothesis_tokens": hyp,
        "substitutions": 1,
        "insertions": 0,
        "deletions": 0,
        "wer": wer,
        "note": "Arithmetic control only; not an ASR/model/runtime result.",
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    board = contract["board_projection"]
    inventory = contract["inventory_row"]
    pins = pin_manifest()
    pin_failures = [k for k, v in pins.items() if v["sha256"] != v["expected"]]
    model_probe = provenance_model_probe()
    scope = branch_diff_paths(WORKTREE)
    wt_violations = working_tree_violations(WORKTREE)
    cases = admission_cases()
    control = synthetic_scorer_control()
    all_blocked = all(g["status"] == "blocked" for g in REQUIRED_GATES)
    all_open = all(b["status"] == "open" for b in REQUIRED_BLOCKERS)
    report = {
        "schema": "audio-sdk.task-evidence.report/v1",
        "task_id": TASK_ID,
        "component": COMPONENT,
        "title": contract["title"],
        "profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "head": BASE_COMMIT,
        "write_scope": [TASK_PREFIX],
        "inventory": inventory,
        "board_projection": board,
        "evidence_profile": evidence_profile_row(),
        "pins": pins,
        "pin_failures": pin_failures,
        "provenance_model_probe": model_probe,
        "provenance_model_probe_note": "Local scratch files are hashed for provenance only; they are not vendored, not admitted, and do not clear model identity/rights gates.",
        "scope": {
            "branch_diff": scope,
            "working_tree_violations": wt_violations,
        },
        "blockers": REQUIRED_BLOCKERS,
        "release_gates": REQUIRED_GATES,
        "admission_cases": cases,
        "synthetic_controls": [control],
        "claims": contract["claims"],
        "non_claims": [
            "No ASR/model/runtime executed.",
            "No model weights or runtime vendored or downloaded.",
            "No real audio, listening, device timing, benchmark, or release claim.",
            "No provider/adapter registered or enabled by default.",
            "No ABI/CONTRACTS/shared build/CI/default/registry change.",
        ],
        "summary": {
            "all_release_gates_blocked": all_blocked,
            "all_blockers_open": all_open,
            "pin_failures": len(pin_failures),
            "scope_violations": len(scope.get("violations", [])) + len(wt_violations),
            "qualifying_result_count": 0,
        },
    }
    return report
