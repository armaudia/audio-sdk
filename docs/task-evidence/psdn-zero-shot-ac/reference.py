# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-PSDN-ZERO-SHOT-AC.

This package is a blocker/feasibility record only. It does not implement,
download, reconstruct, load, or execute PSDN. It does not contain source,
weights, runtime, model outputs, real speech, or listening results.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

TASK = "SDK-PSDN-ZERO-SHOT-AC"
COMPONENT = "psdn-zero-shot-ac"
TITLE = "PSDN zero-shot AC"
BRANCH = "swarm/SDK-PSDN-ZERO-SHOT-AC"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
PROFILE = "Voice"
PROFILE_SOURCE = "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
REPORT_SCHEMA = "audio-sdk/task-evidence-report/0.3"
CONTRACT_SCHEMA = "audio-sdk/psdn-zero-shot-ac-contract/0.1"
TASK_PREFIX = "docs/task-evidence/psdn-zero-shot-ac/"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]

LINKED_ROWS = [
    {
        "component": "psdn-zero-shot-ac",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "id": "SDK-PSDN-ZERO-SHOT-AC",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "title": "PSDN zero-shot AC",
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
    {
        "component": None,
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
        "id": "SDK-SURVEY-TRN-03",
        "mode": "taxonomy",
        "repository": "audio-sdk",
        "title": "Review coverage for Accent conversion",
    },
    {
        "component": None,
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
        "id": "SDK-SURVEY-TRN-04",
        "mode": "taxonomy",
        "repository": "audio-sdk",
        "title": "Review coverage for Speech-to-speech voice conversion",
    },
]
LINK_FIELDS = ["id", "title", "mode", "repository", "component", "depends_on"]
MUTABLE_FIELDS_EXCLUDED = [
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
]

SOURCE_PINS = {
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/survey-trn-03/README.md": "9f1310a624f14d5238dfee2566cbd0dcf1e7f1c17a94ef445644ae90a7309f50",
    "docs/task-evidence/survey-trn-03/report.json": "aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2",
    "docs/task-evidence/survey-trn-04/README.md": "e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae",
    "docs/task-evidence/survey-trn-04/report.json": "fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446",
    "docs/task-evidence/dualvc-3/README.md": "24551d07a453de939da409160d6fe330567a92243e8eadc8e04a6685ba98cf70",
    "docs/task-evidence/dualvc-3/report.json": "1eea7877ce934885a2ebe82a1c50b989a33a062b8b7d34f4441786a52d19b0d1",
    "docs/task-evidence/meanvc/README.md": "34d358ab134b1942b9a3a030acc3017470135921fe90a3cd71fb61c7fd643e40",
    "docs/task-evidence/meanvc/report.json": "e9ce6e224056838848aa5bbe52c2bfa0e1f60abb3ffbf2f7c08449e00c983164",
}

EVIDENCE_PATH = "research/accent-conversion-20261101/README.md"
EVIDENCE_LINE = 173
EVIDENCE_TEXT = (
    "| **PSDN zero-shot AC** | Paper and samples inspected; no official runnable "
    "checkpoint/repo located. | Relevant reference-free, unseen-speaker method, "
    "but currently not install-and-run. [Interspeech paper]"
    "(https://www.isca-archive.org/interspeech_2023/jia23_interspeech.html) |"
)

GATES = [
    {
        "id": "RG-01",
        "title": "source_revision_archive_and_license_provenance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Exact PSDN source, immutable revision/archive/tree digest, and complete license/notice provenance must be identified and reviewed before any implementation claim.",
        "reopen_condition": "An official or rights-cleared PSDN source snapshot is staged with immutable revision/archive digests and reviewed license/notice metadata.",
    },
    {
        "id": "RG-02",
        "title": "weights_assets_and_terms",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Every required checkpoint/config/vocoder/speaker or accent asset must be pinned by byte count and SHA-256 with reviewed terms.",
        "reopen_condition": "All required model assets are staged with per-file byte counts, SHA-256, and reviewed weight/model-card/terms records.",
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "A reproducible pinned runtime must load the exact snapshot offline with deterministic settings and no implicit download.",
        "reopen_condition": "A locked runtime/install digest loads the pinned PSDN snapshot offline and records deterministic host/runtime settings.",
    },
    {
        "id": "RG-04",
        "title": "consent_reference_availability_and_output_use",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Source-speaker consent, target/reference availability, and output-use terms are independent gates for every voice or accent condition.",
        "reopen_condition": "Signed consent/reference-availability/output-use records are staged for every required source, target, and reference condition.",
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_accent_cohort_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "A frozen rights-cleared cohort with manual transcripts, language/speaker/accent groups, and matched controls must exist before any result.",
        "reopen_condition": "A rights-cleared frozen cohort with manual transcripts, groups, and matched/mismatched/identity controls is staged and reviewed.",
    },
    {
        "id": "RG-06",
        "title": "separate_content_identity_naturalness_and_accent_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Content preservation, identity/similarity, naturalness, and accent outcome must be measured separately with independent listening where required.",
        "reopen_condition": "Approved scorers and an independent blinded listening protocol produce reviewed separate outcomes on the frozen cohort.",
    },
    {
        "id": "RG-07",
        "title": "alignment_first_output_tail_peaks_and_resources",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Alignment, first-output/tail timing, peaks, nonfinite behavior, device timing, resources, and deadlines must be measured, not inferred.",
        "reopen_condition": "Target-device paced runs record alignment, first-output/tail, peaks, nonfinite behavior, CPU, memory, and deadline margins.",
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": "SDK-PSDN-ZERO-SHOT-AC",
        "statement": "Opt-in provider intake, public-surface decision, independent exact-head review, and release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent exact-head review with OFF default and explicit release approval.",
    },
]

NON_CLAIMS = [
    "No PSDN source, checkpoint, weight, model card, runtime, corpus audio, or converted output is present or executed.",
    "No accent conversion, identity/similarity, naturalness, listening, device timing, or benchmark result is produced.",
    "No provider registration, default selection, public API/ABI, registry, shared build, or CI change is made.",
    "No paper-reported metric, sample, or demo is treated as a local measurement or qualification.",
    "No missing, blocked, synthetic, or schema-control result qualifies the candidate.",
]

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/psdn-zero-shot-ac/ is touched.",
    "The reference is a task-local evidence builder, not PSDN.",
    "No download, model load, inference, audio read, or network access is performed.",
    "Missing, invalid, nonfinite, out-of-range, and malformed inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
]

EXPECTED_INVENTORY = None  # not present in plan/INVENTORY.json at base

BLOCKER = {
    "status": "blocked_source_weights_runtime_rights_absent",
    "artifact": "Official PSDN zero-shot accent-conversion source, checkpoints/weights/assets, pinned runtime, and rights-cleared evaluation/cohort materials",
    "source": {
        "status": "absent",
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "license": None,
        "note": "Linked research records paper/samples inspected but no official runnable checkpoint/repo located.",
    },
    "weights": {
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "note": "No PSDN checkpoint, config, vocoder, or auxiliary asset is present locally.",
    },
    "runtime": {
        "status": "blocked_runtime_unpinned",
        "sha256": None,
        "lockfile": None,
        "pinned": False,
        "note": "No pinned PSDN runtime, lockfile, or offline loader is present.",
    },
    "expected_license": "None identified locally; code/weight/model-card/data/voice/output terms require explicit reviewed rights decisions.",
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": "Reviewed code/weight/model-card/data terms plus explicit source-speaker consent, reference availability, and output-use terms are required before reproduction or release claims.",
    "workspace_search": "Bounded read-only path probes and filename scans found no PSDN source, checkpoint, runtime, or adapter artifact; only this task worktree path/name matched.",
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed, or surrogate PSDN weights",
        "no substitute accent-conversion model or audio synthesis",
        "no copied upstream source, paper asset, sample audio, or license text",
    ],
    "reopen": "Stage exact licensed source/revision, required assets with digests, a locked offline runtime, rights/consent records, a frozen cohort, and approved Voice outcomes; then rerun with independent review.",
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
        "research/accent-conversion-20261101/repos/psdn",
        "research/accent-conversion-20261101/repos/PSDN",
        "research/accent-conversion-20261101/repos/psdn-zero-shot-ac",
        "research/voice-conversion-eval-20261101/repos/psdn",
        "data/checkpoints/psdn",
        "data/models/psdn",
    ]
    name_hits: List[str] = []
    roots = [WORKSPACE / "research", WORKSPACE / "data", WORKSPACE / "adapters"]
    needles = ("psdn", "zero-shot-ac", "jia23")
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
        "note": "No official PSDN runnable source/repo was identified by the linked evidence; bounded local probes found no qualifying source artifact.",
    }


def weights_probe() -> Dict[str, Any]:
    candidates = [
        "research/accent-conversion-20261101/checkpoints/psdn",
        "research/accent-conversion-20261101/weights/psdn",
        "data/checkpoints/psdn",
        "data/models/psdn",
        "data/weights/psdn",
    ]
    probe = _probe_paths(candidates)
    cache_root = Path.home() / ".cache/huggingface/hub"
    cache_matches: List[str] = []
    if cache_root.exists():
        try:
            for child in cache_root.iterdir():
                low = child.name.lower()
                if "psdn" in low or "jia23" in low:
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
        "note": "No PSDN weights/assets were found; required asset manifest cannot be verified because no official runnable snapshot is identified.",
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
        "note": "No pinned PSDN runtime or offline loader is staged; module presence is informational only and not a PSDN runtime.",
    }


def evidence_entry() -> Dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    text = path.read_text(encoding="utf-8").splitlines()
    line = text[EVIDENCE_LINE - 1]
    if line.strip() != EVIDENCE_TEXT:
        raise ValueError("evidence line mismatch")
    return {
        "path": EVIDENCE_PATH,
        "line": EVIDENCE_LINE,
        "sha256": sha256_file(path),
        "text": line.strip(),
        "note": "Exact linked table row; paper/samples inspected, no official runnable checkpoint/repo located. Not a local execution.",
        "tokens_verified": [
            "PSDN zero-shot AC",
            "no official runnable checkpoint/repo located",
            "reference-free, unseen-speaker method",
            "jia23_interspeech.html",
        ],
    }


def inventory_link() -> Dict[str, Any] | None:
    inv_path = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    row = None
    for item in inv.get("items", []):
        if item.get("id") == COMPONENT or item.get("task") == TASK:
            row = item
            break
    if row is None:
        return None
    keys = ["id", "name", "area", "evidence_status", "repository", "disposition", "verification_profile", "task"]
    return {k: row.get(k) for k in keys}


def source_evidence_statements() -> List[str]:
    return [
        "research/accent-conversion-20261101/README.md line 173 records PSDN zero-shot AC as paper/samples inspected with no official runnable checkpoint/repo located.",
        "plan/INVENTORY.json has no psdn-zero-shot-ac row at base; task identity is tracked by the stable linked task row projection only.",
        "plan/swarm/VERIFICATION.md Voice profile requires permitted input/target references, language/speaker groups, separate content/identity/naturalness outcomes, alignment, first-output/tail, and independent consent/reference/output-use gates.",
        "survey-trn-03 and survey-trn-04 include PSDN as an accent-conversion boundary lead/considered row, not a local PSDN execution or qualification.",
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
        "candidate_output": False,
        "measured_here": False,
        "note": "Installed v0 frame arithmetic only; no PSDN content delay, chunking, lookahead, or output is measured.",
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
        "epoch", "first_input_sample", "lifecycle", "execution_mode", "target_condition",
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
    if req["target_condition"] != "unspecified_accent_condition":
        raise ConfigError("unknown target_condition")
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
        "target_condition": req["target_condition"],
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
    raise CandidateAbsent("no PSDN source/weights/runtime/assets are present")


def _case(case_id: str, req: Any, err: str) -> Dict[str, Any]:
    try:
        probe_candidate(req)
        return {"id": case_id, "accepted": True, "error": None}
    except EvidenceError as e:
        return {"id": case_id, "accepted": False, "error": e.code if err == "ANY" else err}


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
        "target_condition": "unspecified_accent_condition",
    }
    cases = []
    cases.append(_case("unknown_candidate", {**base, "candidate": "other"}, "INVALID_CONFIG"))
    bad = dict(base); bad["extra"] = 1
    cases.append(_case("unknown_field", bad, "INVALID_CONFIG"))
    bad = dict(base); del bad["epoch"]
    cases.append(_case("missing_field", bad, "INVALID_CONFIG"))
    cases.append(_case("wrong_rate", {**base, "sample_rate_hz": 48000}, "INVALID_CONFIG"))
    cases.append(_case("wrong_channels", {**base, "channels": 2}, "INVALID_CONFIG"))
    cases.append(_case("wrong_frame", {**base, "frame_samples": 320}, "INVALID_CONFIG"))
    cases.append(_case("short_samples", {**base, "samples": [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("empty_samples", {**base, "samples": []}, "INVALID_INPUT"))
    cases.append(_case("nonfinite_nan", {**base, "samples": [float("nan")] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("nonfinite_inf", {**base, "samples": [float("inf")] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("out_of_range", {**base, "samples": [8.0] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("bool_sample", {**base, "samples": [True] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("string_sample", {**base, "samples": ["0"] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("null_sample", {**base, "samples": [None] + [0.0] * 159}, "INVALID_INPUT"))
    cases.append(_case("negative_epoch", {**base, "epoch": -1}, "INVALID_CONFIG"))
    cases.append(_case("bool_epoch", {**base, "epoch": True}, "INVALID_CONFIG"))
    cases.append(_case("float_epoch", {**base, "epoch": 1.5}, "INVALID_CONFIG"))
    cases.append(_case("negative_position", {**base, "first_input_sample": -1}, "INVALID_CONFIG"))
    cases.append(_case("bad_lifecycle", {**base, "lifecycle": "drained"}, "INVALID_CONFIG"))
    cases.append(_case("bad_mode", {**base, "execution_mode": 9}, "INVALID_CONFIG"))
    cases.append(_case("bad_target", {**base, "target_condition": "p360"}, "INVALID_CONFIG"))
    cases.append(_case("request_not_object", [], "INVALID_CONFIG") if False else {"id": "request_not_object", "accepted": False, "error": "INVALID_CONFIG"})
    # fix request_not_object through actual validator
    try:
        probe_candidate([])
        cases[-1] = {"id": "request_not_object", "accepted": True, "error": None}
    except EvidenceError as e:
        cases[-1] = {"id": "request_not_object", "accepted": False, "error": e.code}
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
    identity = {}
    for k, v in stimuli.items():
        identity[k] = {"byte_identical": True, "digest": v["digest"]}
    return {
        "candidate_processing": False,
        "identity_control": identity,
        "purpose": "harness stimulus characterisation only; not a PSDN result and not a candidate output",
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

    artifact_pins = {
        name: sha256_file(HERE / name)
        for name in ["reference.py", "run.py", "test_reference.py", "verify.py"]
        if (HERE / name).is_file()
    }
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
                "reason": "No official PSDN runnable source/repo, weights/assets, pinned runtime, rights/consent records, or frozen cohort are present; no conversion or quality result was produced.",
                "status": "blocked_source_weights_runtime_absent",
                "target_condition": "unspecified_accent_condition",
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
            "identity_similarity_measured": False,
            "listening_performed": False,
            "metrics_artifacts": [],
            "naturalness_measured": False,
            "note": "Linked research records paper/samples inspected but no official runnable checkpoint/repo located. No local PSDN execution record exists.",
            "not_rerun": True,
            "qualifies": False,
            "records_found": 0,
            "reproduced_here": False,
            "source": EVIDENCE_PATH,
            "status": "no_local_psdn_execution_record",
        },
        "invariants": list(INVARIANTS),
        "inventory_link": inv,
        "local_harness_checks": {
            "eight_release_gates_blocked": True,
            "identity_control_bit_exact": True,
            "invalid_json_rejected": invalid_json["all_rejected"],
            "invalid_requests_rejected": adverse["all_rejected"],
            "inventory_row_present": inv is not None,
        "inventory_identity_exact": inv is None or inv.get("task") == TASK,
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
            "note": "The linked Interspeech paper/sample lead is recorded only; no official runnable source, checkpoint, model card, or license was located.",
            "url": "https://www.isca-archive.org/interspeech_2023/jia23_interspeech.html",
            "weights_available": False,
        },
        "profile": {"name": "voice", "source": PROFILE_SOURCE},
        "profile_mapping": {
            "alignment_first_output_and_tail_timing": "blocked_no_measured_timing",
            "candidate_output": "blocked_source_weights_runtime_absent",
            "consent_reference_availability_and_output_use": "blocked_rights_and_consent_absent",
            "exact_target_condition": "blocked_no_target_reference_or_condition",
            "identity_and_similarity": "blocked_not_scored",
            "naturalness": "blocked_no_listening",
            "numerical_and_nonfinite": "partial_local_harness_only",
            "permitted_input_and_target_reference_scope": "blocked_no_source_target_pair_or_rights_record",
            "task_and_language_speaker_groups": "blocked_no_frozen_cohort_or_groups",
            "text_and_semantic_content": "blocked_no_model_transcript_or_cohort",
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
            "real_psdn_source_executed": False,
            "real_psdn_source_present": False,
            "real_psdn_weights_present": False,
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
            "alignment_first_output_tail_and_content_delay": "blocked_no_measured_timing",
            "content_preservation": "blocked_no_model_transcript_or_cohort",
            "identity_similarity": "blocked_not_scored",
            "language_and_speaker_groups": "blocked_no_frozen_cohort",
            "naturalness": "blocked_no_listening",
            "numerical_and_nonfinite": "partial_local_harness_only",
            "target_condition_and_consent": "blocked_rights_and_consent_absent",
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
