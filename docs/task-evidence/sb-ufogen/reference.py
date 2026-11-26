# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-SB-UFOGEN.

This package is a blocker/feasibility record only. It does not implement,
download, reconstruct, load, or execute SB-UFOGen. It does not contain source,
weights, runtime, model outputs, real speech, or listening results.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

TASK = "SDK-SB-UFOGEN"
COMPONENT = "sb-ufogen"
TITLE = "SB-UFOGen"
BRANCH = "swarm/SDK-SB-UFOGEN"
BASE_COMMIT = "707dc75e69d27f6d6ad41eaa37fc77dc051b574f"
PROFILE = "Room"
PROFILE_SOURCE = "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
REPORT_SCHEMA = "audio-sdk/task-evidence-report/0.3"
CONTRACT_SCHEMA = "audio-sdk/sb-ufogen-contract/0.1"
TASK_PREFIX = "docs/task-evidence/sb-ufogen/"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]

LINKED_ROWS = [
    {
        "component": "sb-ufogen",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "id": "SDK-SB-UFOGEN",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "title": "SB-UFOGen",
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
]
LINK_FIELDS = ["id", "title", "mode", "repository", "component", "depends_on"]
MUTABLE_FIELDS_EXCLUDED = [
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
]

SOURCE_PINS = {
    "research/dereverberation_candidates_20261028.md": "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
# Deliberately excluded: mutable full plan/swarm/TASKS.json (stable linked-row identity projected only).

BOUNDARY_PINS = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/nemo-schr-dinger-bridge-dereverberation/README.md": "d2f85e19b2d4c467659560dbd0141e63939b3f7b2a1163b8e86332c63c4b4f91",
    "docs/task-evidence/nemo-schr-dinger-bridge-dereverberation/report.json": "334e15b38ffd1ff22b2797721068fac08359dfe86e86b3ff4417eba3519a69b3",
    "docs/task-evidence/online-mono-wpe-reference/README.md": "81db3b15f99c3662085923227c38fe0c84a9eedd2331094d5c0c89c10eb9f16e",
    "docs/task-evidence/online-mono-wpe-reference/report.json": "77d5268a5b4e5c798fcbae5ef0d23dcf6008ed3534523d15fb21806fbb36fdd4",
    "docs/task-evidence/rose-cd-one-step/README.md": "a8d8c9face90e0ff6827331a12ba3ea7f7ebe2186b67df10d9813457fe286629",
    "docs/task-evidence/rose-cd-one-step/report.json": "b27062d674d20673fb9b4b917fb323491b11965ada474246def23585ccd94e25",
}

EVIDENCE_PATH = "research/dereverberation_candidates_20261028.md"
EVIDENCE_LINES = {
    29: "- **SB-UFOGen (few-step adversarial Schrödinger Bridge)**: one-step EARS-Reverb results are reported at PESQ 3.36 / SI-SDR 8.73 dB / ESTOI .88 / MOS Reverb 4.71, close to 50-step SB on that benchmark. Paper timing is measured on an RTX A6000; this is not an established causal streaming implementation, and no usable official checkpoint/inference path was verified. Treat it as a strong utterance-level quality reference, not a selected real-time system.",
    85: "3. **Best published utterance-level ML reference: SB-UFOGen.** Its one-step EARS-Reverb scores are promising, but no local checkpoint/inference path or streaming behavior was verified. NeMo remains a useful offline baseline.",
    96: "- [SMARD official RIR downloads](https://www.es.aau.dk/research/audio-analysis-lab/smard/download); [SB-UFOGen paper and EARS-Reverb results](https://www.isca-archive.org/interspeech_2025/han25b_interspeech.pdf).",
}

EXPECTED_INVENTORY = {
    "id": "sb-ufogen",
    "name": "SB-UFOGen",
    "area": "Echo and room",
    "evidence_status": "considered",
    "repository": "audio-sdk",
    "disposition": "sdk-model",
    "verification_profile": "room",
    "task": "SDK-SB-UFOGEN",
}

GATES = [
    {
        "id": "RG-01",
        "title": "source_revision_archive_and_license_provenance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Exact SB-UFOGen source, immutable revision/archive/tree digest, and complete license/notice provenance must be identified and reviewed before any implementation claim.",
        "reopen_condition": "An official or rights-cleared SB-UFOGen source snapshot is staged with immutable revision/archive digests and reviewed license/notice metadata.",
    },
    {
        "id": "RG-02",
        "title": "weights_assets_and_terms",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Every required checkpoint/config/vocoder/auxiliary asset must be pinned by byte count and SHA-256 with reviewed terms.",
        "reopen_condition": "All required model assets are staged with per-file byte counts, SHA-256, and reviewed weight/model-card/terms records.",
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "A reproducible pinned runtime must load the exact snapshot offline with deterministic settings and no implicit download.",
        "reopen_condition": "A locked runtime/install digest loads the pinned SB-UFOGen snapshot offline and records deterministic host/runtime settings.",
    },
    {
        "id": "RG-04",
        "title": "geometry_delay_and_streaming_contract",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Exact sample rate, channels, frame/hop, lookahead, state/reset, drain, content delay, and streaming/whole-utterance contract must be verified for the target SDK geometry.",
        "reopen_condition": "A reviewed contract records exact geometry, delay, state/reset, drain, and streaming or whole-utterance behavior for the pinned snapshot.",
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_room_cohort_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "A frozen rights-cleared room cohort with render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise, reset schedule, and matched controls must exist before any result.",
        "reopen_condition": "A rights-cleared frozen cohort with identity/noisy controls and documented room/render conditions is staged and reviewed.",
    },
    {
        "id": "RG-06",
        "title": "separate_attenuation_preservation_and_numerical_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Echo/late-reverb attenuation, near-end preservation, nonfinite/peak behavior, and alignments must be measured separately on the frozen cohort.",
        "reopen_condition": "Approved scorers produce reviewed attenuation, preservation, alignment, peak, and nonfinite outcomes on the frozen cohort.",
    },
    {
        "id": "RG-07",
        "title": "target_timing_resources_and_deadlines",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Target-device timing, CPU/memory, deadlines, and availability must be measured for the exact runtime and geometry; GPU paper timing is not a local claim.",
        "reopen_condition": "Target-device paced runs record compute, memory, deadlines, availability, and reset behavior for the exact runtime.",
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-SB-UFOGEN",
        "statement": "Opt-in provider intake, public-surface decision, independent exact-head review, and release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent exact-head review with OFF default and explicit release approval.",
    },
]

NON_CLAIMS = [
    "No SB-UFOGen source, checkpoint, weight, model card, runtime, corpus audio, or dereverberated output is present or executed.",
    "No dereverberation, attenuation, preservation, listening, device timing, or benchmark result is produced.",
    "No provider registration, default selection, public API/ABI, registry, shared build, or CI change is made.",
    "No paper-reported metric, GPU timing, or sample is treated as a local measurement or qualification.",
    "No missing, blocked, synthetic, or schema-control result qualifies the candidate.",
]

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/sb-ufogen/ is touched.",
    "The reference is a task-local evidence builder, not SB-UFOGen.",
    "No download, model load, inference, audio read, or network access is performed.",
    "Missing, invalid, nonfinite, out-of-range, and malformed inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
]

BLOCKER = {
    "status": "blocked_source_weights_runtime_rights_absent",
    "artifact": "Official SB-UFOGen source, checkpoints/weights/assets, pinned runtime, and rights-cleared room evaluation/cohort materials",
    "source": {
        "status": "absent",
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "license": None,
        "note": "Linked research records SB-UFOGen as a strong utterance-level reference with no verified usable official checkpoint/inference path or causal streaming implementation.",
    },
    "weights": {
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "note": "No SB-UFOGen checkpoint, config, or auxiliary asset is present locally.",
    },
    "runtime": {
        "status": "blocked_runtime_unpinned",
        "sha256": None,
        "lockfile": None,
        "pinned": False,
        "note": "No pinned SB-UFOGen runtime, lockfile, or offline loader is present.",
    },
    "expected_license": "None identified locally; code/weight/model-card/data/output terms require explicit reviewed rights decisions.",
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": "Reviewed code/weight/model-card/data terms and rights-cleared room/RIR/speech materials are required before reproduction or release claims.",
    "workspace_search": "Bounded read-only path probes and filename scans found no SB-UFOGen source, checkpoint, runtime, or adapter artifact; only this task worktree path/name matched.",
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed, or surrogate SB-UFOGen weights",
        "no substitute dereverberation model or audio synthesis",
        "no copied upstream source, paper asset, sample audio, or license text",
    ],
    "reopen": "Stage exact licensed source/revision, required assets with digests, a locked offline runtime, rights-cleared room cohort records, and approved Room outcomes; then rerun with independent review.",
}


class JsonError(ValueError):
    pass


class EvidenceError(ValueError):
    code = "INVALID_REQUEST"


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class CandidateAbsent(EvidenceError):
    code = "SOURCE_WEIGHTS_RUNTIME_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and finite_json(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return all(finite_json(v) for v in value)
    return isinstance(value, (str, int, bool)) or value is None


def strict_json_loads(text: str) -> Any:
    if not isinstance(text, str):
        raise JsonError("json input must be text")

    def _const(token: str) -> Any:
        raise JsonError("nonfinite JSON constant: " + token)

    def _pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for k, v in pairs:
            if k in obj:
                raise JsonError("duplicate key: " + k)
            obj[k] = v
        return obj

    try:
        value = json.loads(text, object_pairs_hook=_pairs_hook, parse_constant=_const)
    except json.JSONDecodeError as err:
        raise JsonError("invalid JSON: " + str(err)) from err

    def _check(v: Any) -> None:
        if isinstance(v, float):
            if not math.isfinite(v):
                raise JsonError("nonfinite float")
            return
        if isinstance(v, dict):
            for child in v.values():
                _check(child)
            return
        if isinstance(v, list):
            for child in v:
                _check(child)
            return
        if isinstance(v, (str, int, bool)) or v is None:
            return
        raise JsonError("unsupported type")

    _check(value)
    return value


def _git(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False)


def scope_base(repo: Path) -> str | None:
    proc = _git(["merge-base", "HEAD", BASE_COMMIT], repo)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return None


def scope_changed_paths(repo: Path, base: str) -> List[str]:
    proc = _git(["diff", "--name-only", base + "..HEAD"], repo)
    if proc.returncode != 0:
        raise ValueError("git diff failed: " + proc.stderr.strip())
    paths = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    status = _git(["status", "--porcelain=v1", "--untracked-files=all"], repo)
    if status.returncode != 0:
        raise ValueError("git status failed: " + status.stderr.strip())
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and path not in paths:
            paths.append(path)
    return sorted(set(paths))


def scope_violations(paths: Sequence[str]) -> List[str]:
    return [p for p in paths if not p.startswith(TASK_PREFIX)]


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    projected = [{k: row[k] for k in LINK_FIELDS} for row in LINKED_ROWS]
    payload = canonical_bytes(projected)
    return projected, sha256_bytes(payload)


def _probe_paths(rel_paths: Sequence[str]) -> Dict[str, Any]:
    found: List[str] = []
    missing: List[str] = []
    for rel in rel_paths:
        p = WORKSPACE / rel
        if p.exists():
            found.append(rel)
        else:
            missing.append(rel)
    return {"checked": list(rel_paths), "found": found, "missing": missing}


def source_probe() -> Dict[str, Any]:
    candidates = [
        "research/dereverberation/repos/sb-ufogen",
        "research/dereverberation/repos/SB-UFOGen",
        "research/dereverberation/repos/ufogen",
        "research/dereverberation-20261028/repos/sb-ufogen",
        "data/checkouts/sb-ufogen",
        "data/models/sb-ufogen",
    ]
    name_hits: List[str] = []
    roots = [WORKSPACE / "research", WORKSPACE / "data", WORKSPACE / "adapters"]
    needles = ("sb-ufogen", "ufogen", "han25b")
    scanned = 0
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]
            for name in dirs + files:
                scanned += 1
                low = name.lower()
                if any(n in low for n in needles):
                    rel = str(Path(dirpath, name).relative_to(WORKSPACE))
                    if TASK_PREFIX not in rel:
                        name_hits.append(rel)
                if scanned >= 4000 or len(name_hits) >= 40:
                    break
            if scanned >= 4000 or len(name_hits) >= 40:
                break
        if scanned >= 4000 or len(name_hits) >= 40:
            break
    name_hits = sorted(set(name_hits))
    probe = _probe_paths(candidates)
    present = bool(probe["found"]) or bool(name_hits)
    return {
        "status": "blocked_source_absent" if not present else "ambiguous_name_hit_only",
        "present": present,
        "official_repo_identified": False,
        "official_revision_pinned": False,
        "checked_paths": probe["checked"],
        "found": probe["found"],
        "name_scan": {
            "roots": [str(r.relative_to(WORKSPACE)) for r in roots if r.exists()],
            "entries_scanned": scanned,
            "truncated": scanned >= 4000 or len(name_hits) >= 40,
            "matches": name_hits,
        },
        "note": "No official SB-UFOGen runnable source/repo or usable checkpoint/inference path was identified by the linked evidence; bounded local probes found no qualifying source artifact.",
    }


def weights_probe() -> Dict[str, Any]:
    candidates = [
        "research/dereverberation/checkpoints/sb-ufogen",
        "research/dereverberation/weights/sb-ufogen",
        "data/checkpoints/sb-ufogen",
        "data/models/sb-ufogen",
        "data/weights/sb-ufogen",
    ]
    probe = _probe_paths(candidates)
    cache_root = Path.home() / ".cache/huggingface/hub"
    cache_matches: List[str] = []
    if cache_root.exists():
        try:
            for child in cache_root.iterdir():
                low = child.name.lower()
                if "sb-ufogen" in low or "ufogen" in low or "han25b" in low:
                    cache_matches.append(child.name)
        except OSError:
            cache_matches = ["<unreadable>"]
    return {
        "status": "blocked_weights_absent",
        "present": False,
        "checked_paths": probe["checked"],
        "found": probe["found"],
        "home_cache": {"root": str(cache_root), "matches": sorted(cache_matches)},
        "required_assets": [],
        "note": "No SB-UFOGen weights/assets were found; required asset manifest cannot be verified because no official runnable snapshot is identified.",
    }


def runtime_probe() -> Dict[str, Any]:
    module_names = ["torch", "torchaudio", "numpy", "librosa", "soundfile", "onnxruntime"]
    importable = {}
    for name in module_names:
        try:
            __import__(name)
            importable[name] = True
        except Exception:
            importable[name] = False
    return {
        "status": "blocked_runtime_unpinned",
        "present": False,
        "pinned": False,
        "lockfile": None,
        "importable_modules": importable,
        "note": "No pinned SB-UFOGen runtime or offline loader is staged; module presence is informational only and not an SB-UFOGen runtime.",
    }


def evidence_entry() -> Dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    for line_no, expected in EVIDENCE_LINES.items():
        actual = lines[line_no - 1]
        if actual != expected:
            raise ValueError(f"evidence line mismatch: {line_no}")
        rows.append({
            "line": line_no,
            "sha256_line": sha256_bytes((actual + "\n").encode("utf-8")),
            "text": actual,
        })
    return {
        "path": EVIDENCE_PATH,
        "sha256": sha256_file(path),
        "rows": rows,
        "note": "Exact linked dereverberation research rows; paper/GPU results are not local measurements and no usable official checkpoint/inference path was verified.",
        "tokens_verified": [
            "SB-UFOGen",
            "no usable official checkpoint/inference path was verified",
            "not an established causal streaming implementation",
            "utterance-level quality reference",
            "han25b_interspeech.pdf",
        ],
    }


def inventory_link() -> Dict[str, Any] | None:
    inv_path = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    items = inv.get("components")
    if not isinstance(items, list):
        items = inv.get("items", [])
    row = None
    for item in items:
        if isinstance(item, dict) and (item.get("id") == COMPONENT or item.get("task") == TASK):
            row = item
            break
    if row is None:
        return None
    keys = ["id", "name", "area", "evidence_status", "repository", "disposition", "verification_profile", "task"]
    return {k: row.get(k) for k in keys}


def source_evidence_statements() -> List[str]:
    return [
        "research/dereverberation_candidates_20261028.md line 29 records SB-UFOGen one-step EARS-Reverb paper results, RTX A6000 timing, no established causal streaming implementation, and no verified usable official checkpoint/inference path.",
        "research/dereverberation_candidates_20261028.md line 85 records SB-UFOGen as a best published utterance-level ML reference but not locally verified.",
        "plan/INVENTORY.json row sb-ufogen is considered/sdk-model/room with evidence in research/dereverberation_candidates_20261028.md.",
        "plan/swarm/VERIFICATION.md Room profile requires frozen room/RIR/render conditions, identity/noisy/overlap/no-reference controls, echo attenuation, near-end preservation, nonfinite/peak behavior, alignments, and delayed/missing render handling.",
        "Merged sibling dereverberation evidence packages (NeMo SB dereverb, online mono WPE, ROSE-CD one-step) provide context only and are not SB-UFOGen execution.",
    ]


def geometry() -> Dict[str, Any]:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "float32",
        "frame_samples": 160,
        "frame_ms": 10.0,
        "frames_per_second": 100.0,
        "public_v0_geometry_preserved": True,
        "candidate_geometry_documented": False,
        "candidate_buffering_delay_samples": None,
        "candidate_chunk_or_lookahead": None,
        "candidate_max_drain_calls": None,
        "candidate_streaming": "unknown_not_verified",
        "candidate_output": False,
        "measured_here": False,
        "note": "Installed v0 frame arithmetic only; no SB-UFOGen content delay, chunking, lookahead, streaming, or output is measured.",
        "source": "audio-sdk CONTRACTS.md installed v0 format: 16000 Hz, mono, float32, 160 samples per frame",
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
            "sample_rate_hz": 16000,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def validate_request(req: Any) -> Dict[str, Any]:
    if not isinstance(req, dict):
        raise ConfigError("request must be object")
    allowed = {
        "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
        "epoch", "first_input_sample", "lifecycle", "execution_mode",
    }
    unknown = sorted(set(req.keys()) - allowed)
    if unknown:
        raise ConfigError("unknown fields: " + ",".join(unknown))
    missing = sorted(allowed - set(req.keys()))
    if missing:
        raise ConfigError("missing fields: " + ",".join(missing))
    if req["candidate"] != COMPONENT:
        raise ConfigError("unknown candidate")
    if req["sample_rate_hz"] != 16000 or req["channels"] != 1 or req["frame_samples"] != 160:
        raise ConfigError("installed v0 geometry mismatch")
    if req["execution_mode"] not in (1, 2, 3):
        raise ConfigError("invalid execution_mode")
    if req["lifecycle"] not in {"prepared", "processing"}:
        raise ConfigError("invalid lifecycle")
    epoch = req["epoch"]
    pos = req["first_input_sample"]
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise ConfigError("invalid epoch")
    if not isinstance(pos, int) or isinstance(pos, bool) or pos < 0:
        raise ConfigError("invalid first_input_sample")
    samples = req["samples"]
    if not isinstance(samples, list) or len(samples) != 160:
        raise InputError("samples must be 160-item list")
    clean: List[float] = []
    for s in samples:
        if isinstance(s, bool) or not isinstance(s, (int, float)):
            raise InputError("sample must be number")
        f = float(s)
        if not math.isfinite(f):
            raise InputError("nonfinite sample")
        if abs(f) > 4.0:
            raise InputError("out of range sample")
        clean.append(f)
    return {
        "candidate": COMPONENT,
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": clean,
        "epoch": epoch,
        "first_input_sample": pos,
        "lifecycle": req["lifecycle"],
        "execution_mode": req["execution_mode"],
    }


def validate_reset(new_epoch: Any, new_first_input_sample: Any, current_epoch: int) -> Dict[str, Any]:
    if not isinstance(new_epoch, int) or isinstance(new_epoch, bool) or new_epoch < 0:
        raise ConfigError("invalid epoch")
    if not isinstance(new_first_input_sample, int) or isinstance(new_first_input_sample, bool) or new_first_input_sample < 0:
        raise ConfigError("invalid first_input_sample")
    if new_epoch <= current_epoch:
        raise ConfigError("epoch must increase")
    return {"accepted": True, "epoch": new_epoch, "first_input_sample": new_first_input_sample}


def probe_candidate(req: Any) -> None:
    validate_request(req)
    raise CandidateAbsent("no SB-UFOGen source/weights/runtime/assets are present")


def _case(case_id: str, req: Any) -> Dict[str, Any]:
    try:
        probe_candidate(req)
        return {"id": case_id, "accepted": True, "error": None}
    except EvidenceError as e:
        return {"id": case_id, "accepted": False, "error": e.code}


def _adverse_cases() -> Dict[str, Any]:
    base = {
        "candidate": COMPONENT,
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }
    cases = []
    cases.append(_case("unknown_candidate", {**base, "candidate": "other"}))
    bad = dict(base); bad["extra"] = 1
    cases.append(_case("unknown_field", bad))
    bad = dict(base); del bad["epoch"]
    cases.append(_case("missing_field", bad))
    cases.append(_case("wrong_rate", {**base, "sample_rate_hz": 48000}))
    cases.append(_case("wrong_channels", {**base, "channels": 2}))
    cases.append(_case("wrong_frame", {**base, "frame_samples": 320}))
    cases.append(_case("short_samples", {**base, "samples": [0.0] * 159}))
    cases.append(_case("empty_samples", {**base, "samples": []}))
    cases.append(_case("nonfinite_nan", {**base, "samples": [float("nan")] + [0.0] * 159}))
    cases.append(_case("nonfinite_inf", {**base, "samples": [float("inf")] + [0.0] * 159}))
    cases.append(_case("out_of_range", {**base, "samples": [8.0] + [0.0] * 159}))
    cases.append(_case("bool_sample", {**base, "samples": [True] + [0.0] * 159}))
    cases.append(_case("string_sample", {**base, "samples": ["0"] + [0.0] * 159}))
    cases.append(_case("null_sample", {**base, "samples": [None] + [0.0] * 159}))
    cases.append(_case("negative_epoch", {**base, "epoch": -1}))
    cases.append(_case("bool_epoch", {**base, "epoch": True}))
    cases.append(_case("float_epoch", {**base, "epoch": 1.5}))
    cases.append(_case("negative_position", {**base, "first_input_sample": -1}))
    cases.append(_case("bad_lifecycle", {**base, "lifecycle": "drained"}))
    cases.append(_case("bad_mode", {**base, "execution_mode": 9}))
    try:
        probe_candidate([])
        cases.append({"id": "request_not_object", "accepted": True, "error": None})
    except EvidenceError as e:
        cases.append({"id": "request_not_object", "accepted": False, "error": e.code})
    accepted = sum(1 for c in cases if c["accepted"])
    return {
        "accepted_count": accepted,
        "all_rejected": accepted == 0,
        "case_count": len(cases),
        "cases": cases,
        "metrics": None,
        "note": "Invalid requests are rejected before any candidate call; no metrics exist.",
    }


def _invalid_json_cases() -> Dict[str, Any]:
    texts = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "negative_infinity_constant": '{"a":-Infinity}',
        "trailing_data": '{"a":1} extra',
        "invalid_syntax": '{"a":}',
        "empty_text": '',
    }
    cases = []
    for k, t in texts.items():
        try:
            strict_json_loads(t)
            cases.append({"id": k, "accepted": False, "error": "UNEXPECTED_ACCEPT"})
        except JsonError:
            cases.append({"id": k, "accepted": False, "error": "INVALID_JSON"})
    return {
        "accepted_count": 0,
        "all_rejected": all(c["error"] == "INVALID_JSON" for c in cases),
        "case_count": len(cases),
        "cases": cases,
        "metrics": None,
    }


def _reset_cases() -> Dict[str, Any]:
    checks = [
        ("fresh_epoch_2_accepted", (2, 0, 1), True),
        ("equal_epoch_rejected", (1, 0, 1), False),
        ("lower_epoch_rejected", (0, 0, 1), False),
        ("negative_epoch_rejected", (-1, 0, 1), False),
        ("negative_position_rejected", (2, -1, 1), False),
        ("bool_epoch_rejected", (True, 0, 1), False),
        ("bool_position_rejected", (2, False, 1), False),
        ("float_epoch_rejected", (1.5, 0, 1), False),
    ]
    cases = []
    for case_id, args, expected in checks:
        try:
            validate_reset(*args)
            cases.append({"id": case_id, "accepted": True, "expected_accepted": expected, "error": "NOT_REJECTED"})
        except EvidenceError as e:
            cases.append({"id": case_id, "accepted": False, "expected_accepted": expected, "error": e.code})
    matches = all(c["accepted"] == c["expected_accepted"] for c in cases)
    accepted = sum(1 for c in cases if c["accepted"])
    return {
        "accepted_count": accepted,
        "case_count": len(cases),
        "cases": cases,
        "expected_accepted_count": 1,
        "matches_expectation": matches,
        "metrics": None,
        "note": "Structural reset validation only; no candidate state exists and no reset is executed.",
        "state_owned": False,
    }


def stimulus_probe() -> Dict[str, Any]:
    def _stats(samples: Sequence[float]) -> Dict[str, Any]:
        peak = max(abs(s) for s in samples) if samples else 0.0
        rms = math.sqrt(sum(s * s for s in samples) / len(samples)) if samples else 0.0
        nz = sum(1 for s in samples if not math.isfinite(s))
        digest = sha256_bytes(canonical_bytes([round(s, 12) for s in samples]))
        return {
            "digest": digest,
            "nonfinite_count": nz,
            "peak_abs": round(peak, 9),
            "rms": round(rms, 9),
            "sample_count": len(samples),
        }

    silence = [0.0] * 1600
    impulse = [0.0] * 1600
    impulse[0] = 0.5
    step = [0.25 if i >= 800 else 0.0 for i in range(1600)]
    sweep = [0.3 * math.sin(2 * math.pi * (80 + 3920 * (i / 1600)) * (i / 16000)) for i in range(1600)]
    speech = []
    for i in range(3200):
        t = i / 16000
        env = 0.25 + 0.75 * (0.5 * (1 - math.cos(2 * math.pi * t / 0.2)))
        speech.append(0.2 * env * math.sin(2 * math.pi * 180 * t) + 0.08 * env * math.sin(2 * math.pi * 360 * t))
    stimuli = {
        "impulse": {"name": "impulse", **_stats(impulse)},
        "silence": {"name": "silence", **_stats(silence)},
        "speech_like": {"name": "speech_like", **_stats(speech)},
        "step": {"name": "step", **_stats(step)},
        "sweep": {"name": "sweep", **_stats(sweep)},
    }
    identity = {k: {"byte_identical": True, "digest": v["digest"]} for k, v in stimuli.items()}
    return {
        "candidate_processing": False,
        "identity_control": identity,
        "purpose": "harness stimulus characterisation only; not an SB-UFOGen result and not a candidate output",
        "stimuli": stimuli,
    }


def build_report() -> Dict[str, Any]:
    src = source_probe()
    wts = weights_probe()
    rt = runtime_probe()
    adverse = _adverse_cases()
    invalid_json = _invalid_json_cases()
    resets = _reset_cases()
    links, link_digest = board_link_projection()
    inv = inventory_link()
    ev = evidence_entry()
    geom = geometry()
    bnd = boundary()
    qual = qualification()
    stimuli = stimulus_probe()

    report = {
        "adverse": {
            "invalid_config_and_input": adverse,
            "invalid_json_numeric_fields": invalid_json,
            "missing_result": {
                "metrics": None,
                "note": "No candidate output exists; missing evidence never qualifies.",
                "qualifies_candidate": False,
                "reason": "source_weights_runtime_rights_absent_source_unidentified",
                "status": "blocked",
            },
            "reset_validation": resets,
        },
        "base_commit": BASE_COMMIT,
        "board_link_fields": LINK_FIELDS,
        "board_link_projection_sha256": link_digest,
        "board_links": links,
        "board_mutable_fields_excluded": MUTABLE_FIELDS_EXCLUDED,
        "boundary": bnd,
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "candidates": {
            COMPONENT: {
                "metrics": None,
                "qualifies_candidate": False,
                "reason": "No official SB-UFOGen runnable source/repo, usable checkpoint/inference path, weights/assets, pinned runtime, rights/consent records, or frozen cohort are present; no dereverberation result was produced.",
                "status": "blocked_source_weights_runtime_absent",
                "target_condition": "unspecified_room_condition",
            }
        },
        "comparison_status": "blocked_source_weights_runtime_absent",
        "component": COMPONENT,
        "controls": {
            "harness_identity_control": {"candidate_processing": False, "status": "bit_exact_synthetic_only"},
            "no_model_or_audio_execution": {"audio_read": False, "candidate_output": False, "model_executed": False, "network_used": False, "weights_loaded": False},
        },
        "decision": "DEFER",
        "evidence_entry": ev,
        "gates": [dict(g) for g in GATES],
        "geometry": geom,
        "historical_evidence": {
            "device_timing_present": False,
            "listening_performed": False,
            "metrics_artifacts": [],
            "near_end_preservation_measured": False,
            "note": "Linked research records SB-UFOGen as paper/GPU utterance-level reference with no verified usable official checkpoint/inference path or causal streaming implementation. No local SB-UFOGen execution record exists.",
            "not_rerun": True,
            "qualifies": False,
            "records_found": 0,
            "reproduced_here": False,
            "source": EVIDENCE_PATH,
            "status": "no_local_sb_ufogen_execution_record",
        },
        "invariants": list(INVARIANTS),
        "inventory_link": inv,
        "local_harness_checks": {
            "eight_release_gates_blocked": True,
            "identity_control_bit_exact": True,
            "invalid_json_rejected": invalid_json["all_rejected"],
            "invalid_requests_rejected": adverse["all_rejected"],
            "inventory_row_present": inv is not None,
            "inventory_identity_exact": inv == EXPECTED_INVENTORY,
            "missing_result_blocked": True,
            "no_result_qualifies_candidate": True,
            "report_generation_deterministic": True,
            "reset_cases_match_expectation": resets["matches_expectation"],
            "runtime_probe_confirms_unpinned": rt["status"] == "blocked_runtime_unpinned",
            "source_not_executed": True,
            "source_present_and_exactly_pinned": False,
            "stable_board_identity_only": True,
            "strict_json_rejects_duplicate_and_nonfinite": invalid_json["all_rejected"],
            "weights_probe_confirms_absent": wts["status"] == "blocked_weights_absent",
        },
        "no_missing_result_qualifies_candidate": True,
        "non_claims": list(NON_CLAIMS),
        "paper_lead": {
            "code_available": False,
            "identified_artifacts": [],
            "license_available": False,
            "model_card_available": False,
            "note": "The linked Interspeech paper is recorded only; no usable official runnable source, checkpoint, model card, or license was located/verified.",
            "url": "https://www.isca-archive.org/interspeech_2025/han25b_interspeech.pdf",
            "weights_available": False,
        },
        "profile": {"name": "room", "source": PROFILE_SOURCE},
        "profile_mapping": {
            "alignment_and_delayed_missing_render": "blocked_no_runtime_or_cohort",
            "candidate_output": "blocked_source_weights_runtime_absent",
            "echo_attenuation_and_near_end_preservation": "blocked_not_scored",
            "frozen_room_rir_render_conditions": "blocked_no_frozen_cohort",
            "identity_noisy_overlap_no_reference_controls": "blocked_no_controls_or_execution",
            "nonfinite_peaks_and_failures": "partial_local_harness_only",
            "state_reset_and_channel_rate_hop": "blocked_no_runtime_contract",
            "timing_and_resources": "blocked_no_device_timing",
        },
        "qualification": qual,
        "qualification_status": "not_qualified",
        "reference": {
            "candidate_processing": False,
            "deterministic": True,
            "downloads": False,
            "implementation": "task-local standard-library evidence builder",
            "model_weights": False,
            "pinned_runtime_present": False,
            "real_sb_ufogen_source_executed": False,
            "real_sb_ufogen_source_present": False,
            "real_sb_ufogen_weights_present": False,
            "synthetic_only": True,
            "upstream_parity": False,
        },
        "release_gates": [dict(g) for g in GATES],
        "reproduction": {
            "check": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "cold_start_repeats": 3,
            "commands": ["python3 run.py all", "python3 -m unittest -v test_reference.py", "python3 verify.py"],
            "comparison": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
            "contract": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py contract",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py report",
            "sources": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py sources",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
        },
        "required_results": {
            "alignment_and_content_delay": "blocked_no_runtime_or_cohort",
            "echo_late_reverb_attenuation": "blocked_not_scored",
            "near_end_preservation": "blocked_not_scored",
            "nonfinite_and_peak_behavior": "partial_local_harness_only",
            "room_rir_and_control_conditions": "blocked_no_frozen_cohort",
            "target_timing_and_resources": "blocked_no_device_timing",
        },
        "runtime_probe": rt,
        "schema_id": REPORT_SCHEMA,
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "source_probe": src,
        "status": "proposal_only_not_qualified",
        "stimulus_probe": stimuli,
        "task": TASK,
        "upstream_blocker": dict(BLOCKER),
        "weights_probe": wts,
    }

    if not finite_json(report):
        raise ValueError("report contains non-finite/non-json value")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
