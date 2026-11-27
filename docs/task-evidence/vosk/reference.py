# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only blocker evidence for SDK-VOSK.

This package is a fail-closed feasibility/readiness handoff. It records exact
external blockers for Vosk as an SDK reference component. It does not download,
execute, load, bundle, or admit Vosk source/runtime/model assets; it does not
register a provider; and it makes no benchmark, device-timing, listening, or
release claim.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-VOSK"
COMPONENT = "vosk"
TITLE = "Vosk"
PROFILE = "Rate"
CONTRACT_ID = "audio-sdk/vosk-feasibility/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
DECISION = "DEFER"
STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-VOSK"
TASK_PREFIX = "docs/task-evidence/vosk/"
SCOPE_BASE_REFS = ("origin/main", "main")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

SOURCE_PINS = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json": "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
}

LINKED_ROWS = [
    {
        "id": "SDK-VOSK",
        "title": "Vosk",
        "component": "vosk",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "evidence": ["cpp-library/pipeline-validation/playback-speed-candidates.md"],
    },
    {
        "id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-PROVIDER",
        "title": "Optional provider packaging, discovery and ABI surface",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
]

RATE_PROFILE_PHRASES = [
    "source/output mapping, duration, pitch, transient audibility and playback buffering",
    "1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window",
    "pause or filler decisions tied to source timestamps and measure speech preservation",
]

RELEASE_GATES = [
    {
        "id": "RG-01",
        "status": "blocked",
        "gate": "exact_source_revision_and_license",
        "qualifies": False,
        "detail": "No exact immutable Vosk source revision, complete license/NOTICE bundle, or reviewed dependency provenance is pinned/admitted in this worktree.",
        "reopen_condition": "Pin exact Vosk source revision(s), complete license/NOTICE texts, dependency provenance, and reviewed redistribution/commercial terms.",
    },
    {
        "id": "RG-02",
        "status": "blocked",
        "gate": "exact_model_assets_and_rights",
        "qualifies": False,
        "detail": "No exact Vosk model archive/checkpoint IDs, immutable digests, model cards/licenses, or reviewed output-use/redistribution rights are admitted.",
        "reopen_condition": "Provide immutable model/archive identity, per-file digests, license/model-card terms, and reviewed acquisition/evaluation/redistribution/output-use decisions.",
    },
    {
        "id": "RG-03",
        "status": "blocked",
        "gate": "pinned_runtime_and_offline_load",
        "qualifies": False,
        "detail": "No pinned offline-installable Vosk runtime/wheel/archive with lock, license text, and deterministic load proof is admitted.",
        "reopen_condition": "Provide pinned runtime archive digests, lockfile, offline install/load proof, and reviewed runtime license/notice bundle.",
    },
    {
        "id": "RG-04",
        "status": "blocked",
        "gate": "adapter_boundary_and_installed_v0_preservation",
        "qualifies": False,
        "detail": "No optional Vosk adapter/provider boundary is implemented or admitted; installed v0 geometry/ABI/default/registry/shared build must remain unchanged until separately approved.",
        "reopen_condition": "Implement a separately reviewed opt-in adapter preserving installed v0 behavior, no default selection, no ABI/registry/shared-build change without approval.",
    },
    {
        "id": "RG-05",
        "status": "blocked",
        "gate": "deterministic_task_local_evidence",
        "qualifies": False,
        "detail": "This package is deterministic blocker evidence only; no qualifying Vosk execution, conformance, or 3x byte-identical runtime output beyond this package exists.",
        "reopen_condition": "Provide deterministic conformance, strict invalid/nonfinite/missing/adverse rejection, and 3x cold-start byte-identical qualifying artifacts from an admitted runtime.",
    },
    {
        "id": "RG-06",
        "status": "blocked",
        "gate": "rate_profile_matched_evidence",
        "qualifies": False,
        "detail": "No Rate-profile matched evidence exists: no source/output mapping, duration/pitch/transient/buffering/rebuffer/drift/final-partial controls, or speech-preservation measurements on an admitted rights-cleared cohort.",
        "reopen_condition": "Produce rights-cleared matched Rate-profile evidence with 1x/rate-change controls, unfamiliar speech/music/silence, rebuffer/drift, final partial window, source-timestamp pause/filler decisions, and measured speech preservation.",
    },
    {
        "id": "RG-07",
        "status": "blocked",
        "gate": "paced_target_timing_and_resources",
        "qualifies": False,
        "detail": "No paced target-device/runtime CPU, memory, deadline, availability, or failure measurements exist for Vosk in this package.",
        "reopen_condition": "Measure paced target-device runtime with CPU, memory, deadline/availability, failure accounting, and exact host/runtime provenance.",
    },
    {
        "id": "RG-08",
        "status": "blocked",
        "gate": "review_ci_release_approval",
        "qualifies": False,
        "detail": "No exact-head independent review, hosted CI, or explicit release approval exists for a Vosk provider.",
        "reopen_condition": "Obtain exact-head independent review, green hosted CI, and explicit release approval before any qualification/release claim.",
    },
]


REQUIRED_ARTIFACTS = [
    {"id": "A01", "artifact": "exact Vosk source revision + complete license/NOTICE/provenance bundle", "present": False, "verified": False, "blocked": True},
    {"id": "A02", "artifact": "exact model archive/checkpoint IDs, immutable digests, model cards/licenses, output-use terms", "present": False, "verified": False, "blocked": True},
    {"id": "A03", "artifact": "pinned runtime/wheel/archive, lock, offline install/load proof", "present": False, "verified": False, "blocked": True},
    {"id": "A04", "artifact": "optional adapter/provider boundary preserving installed v0 behavior", "present": False, "verified": False, "blocked": True},
    {"id": "A05", "artifact": "deterministic conformance + strict adverse/invalid/missing/nonfinite rejection", "present": False, "verified": False, "blocked": True},
    {"id": "A06", "artifact": "rights-cleared matched Rate-profile evidence", "present": False, "verified": False, "blocked": True},
    {"id": "A07", "artifact": "paced target-device timing/resources/failure accounting", "present": False, "verified": False, "blocked": True},
    {"id": "A08", "artifact": "exact-head independent review + hosted CI + explicit release approval", "present": False, "verified": False, "blocked": True},
]

EXACT_BLOCKERS = [
    {"id": "BLK-01", "severity": "blocking", "status": "open", "gate": "RG-01", "summary": "Exact Vosk source/license/NOTICE/provenance not pinned or admitted.", "qualifies": False},
    {"id": "BLK-02", "severity": "blocking", "status": "open", "gate": "RG-02", "summary": "Exact model assets, digests, licenses/model cards, and output-use rights not admitted.", "qualifies": False},
    {"id": "BLK-03", "severity": "blocking", "status": "open", "gate": "RG-03", "summary": "Pinned offline runtime/wheel/archive and deterministic load proof not admitted.", "qualifies": False},
    {"id": "BLK-04", "severity": "blocking", "status": "open", "gate": "RG-04", "summary": "No separately reviewed opt-in adapter boundary; installed v0/default/ABI/registry/shared build must remain unchanged.", "qualifies": False},
    {"id": "BLK-05", "severity": "blocking", "status": "open", "gate": "RG-06", "summary": "No rights-cleared matched Rate-profile evidence (mapping/duration/pitch/transients/buffering/rebuffer/drift/final-partial/speech preservation).", "qualifies": False},
    {"id": "BLK-06", "severity": "blocking", "status": "open", "gate": "RG-07", "summary": "No paced target-device timing/resources/failure accounting.", "qualifies": False},
]

NON_CLAIMS = [
    "No Vosk source, runtime, wheel, model, or asset downloaded, executed, loaded, bundled, or admitted.",
    "No provider registered; no default changed; no public API/ABI/descriptor/registry/shared build/CI changed.",
    "No real audio, corpus, listening, device timing, benchmark, or release claim made.",
    "No absent artifact fabricated, substituted, or inherited from sibling packages as Vosk qualification.",
    "Task-local deterministic evidence only; missing/adverse/invalid results are non-qualifying.",
]


class ReferenceError(ValueError):
    pass


def _reject_float(x: Any) -> Any:
    if isinstance(x, float):
        raise ReferenceError("float_forbidden")
    return x


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_strict_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise ReferenceError(f"duplicate_key:{k}")
            out[k] = v
        return out

    def const_hook(x: str) -> Any:
        raise ReferenceError(f"nonfinite_constant:{x}")

    def float_hook(x: str) -> Any:
        raise ReferenceError(f"float_forbidden:{x}")

    try:
        obj = json.loads(text, object_pairs_hook=pairs_hook, parse_float=float_hook, parse_int=int, parse_constant=const_hook)
    except ValueError as e:
        if isinstance(e, ReferenceError):
            raise
        raise ReferenceError(f"strict_json_error:{e}") from e
    _no_floats(obj)
    return obj


def _no_floats(obj: Any) -> None:
    if isinstance(obj, float):
        raise ReferenceError("float_forbidden")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise ReferenceError("non_string_key")
            _no_floats(v)
    elif isinstance(obj, list):
        for v in obj:
            _no_floats(v)


def resolve_source(rel: str) -> Path:
    return AUDIO_ROOT / rel


def resolve_worktree(rel: str) -> Path:
    return WORKTREE / rel


def stable_row_projection() -> dict[str, Any]:
    row = next(r for r in LINKED_ROWS if r["id"] == TASK)
    return {k: row[k] for k in ["id", "title", "component", "mode", "repository", "depends_on", "evidence"]}


def linked_row_identity() -> dict[str, Any]:
    proj = stable_row_projection()
    return {
        "projection": proj,
        "sha256": sha256_bytes(canonical_bytes(proj)),
        "linked_rows": LINKED_ROWS,
        "linked_rows_sha256": sha256_bytes(canonical_bytes(LINKED_ROWS)),
        "gating": "stable_identity_only",
        "mutable_board_hash_used": False,
        "mutable_board_path_observed": "audio-benchmark-platform/plan/swarm/TASKS.json",
    }


def probe_absence() -> dict[str, Any]:
    probes = [
        "vosk",
        "libvosk.so",
        "libvosk.dylib",
        "libvosk.dll",
        "vosk-model-small-en-us-0.15",
        "vosk-model-en-us-0.22",
    ]
    found: list[str] = []
    for root in [WORKTREE / "third_party", WORKTREE / "adapters", WORKTREE / "models", WORKTREE / "assets"]:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            name = p.name.lower()
            if any(token in name for token in ["vosk", "libvosk"]):
                try:
                    rel = p.relative_to(WORKTREE).as_posix()
                except Exception:
                    rel = str(p)
                found.append(rel)
    return {
        "probe_tokens": probes,
        "workspace_glob_roots": ["third_party", "adapters", "models", "assets"],
        "found": sorted(set(found)),
        "all_absent": len(found) == 0,
        "runtime_import_attempted": False,
        "model_load_attempted": False,
        "audio_read_attempted": False,
        "download_attempted": False,
    }


def build_contract() -> dict[str, Any]:
    lri = linked_row_identity()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "release_claim": False,
            "benchmark_claim": False,
            "timing_claim": False,
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "task_prefix": TASK_PREFIX,
        "scope": {
            "task_local_only": True,
            "provider_registration": False,
            "default_change": False,
            "public_api_abi_change": False,
            "contracts_or_registry_change": False,
            "shared_build_or_ci_change": False,
            "downloads": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark_or_release_claim": False,
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "linked_row_identity": lri,
        "profile_requirements": {
            "name": "Rate",
            "required_phrases": RATE_PROFILE_PHRASES,
            "all_blocked": True,
            "notes": "No admitted Vosk runtime/model/cohort; Rate-profile measurements are blocked/non-qualifying.",
        },
        "required_artifacts": REQUIRED_ARTIFACTS,
        "exact_blockers": EXACT_BLOCKERS,
        "release_gates": RELEASE_GATES,
        "non_claims": NON_CLAIMS,
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    absence = probe_absence()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": DECISION,
        "status": STATUS,
        "qualification": contract["qualification"],
        "linked_row_identity": contract["linked_row_identity"],
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "absence_summary": absence,
        "profile_requirements": contract["profile_requirements"],
        "required_artifacts": REQUIRED_ARTIFACTS,
        "exact_blockers": EXACT_BLOCKERS,
        "release_gates": RELEASE_GATES,
        "scope": contract["scope"],
        "non_claims": NON_CLAIMS,
        "commands": [
            "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 docs/task-evidence/vosk/run.py",
            "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v docs/task-evidence/vosk/test_reference.py",
            "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 docs/task-evidence/vosk/verify.py",
        ],
    }
    report["report_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in report.items() if k != "report_sha256"}))
    return report


def report_digest(report: dict[str, Any]) -> str:
    body = {k: v for k, v in report.items() if k != "report_sha256"}
    return sha256_bytes(canonical_bytes(body))


def sources_manifest() -> str:
    rows: list[tuple[str, str]] = []
    for name in sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name != "SOURCES.sha256"):
        rows.append((name, sha256_file(HERE / name)))
    for rel, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(resolve_source(rel))
        if actual != expected:
            raise ReferenceError(f"source_pin_mismatch:{rel}:{actual}")
        rows.append((f"source:{rel}", actual))
    for rel, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(resolve_worktree(rel))
        if actual != expected:
            raise ReferenceError(f"boundary_pin_mismatch:{rel}:{actual}")
        rows.append((f"boundary:{rel}", actual))
    return "".join(f"{d}  {n}\n" for n, d in rows)


def _git_scope(worktree: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *args], capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    r = _git_scope(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = r.stdout.strip()
    return sha if r.returncode == 0 and sha else None


def scope_base(worktree: Path, refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        r = _git_scope(worktree, "merge-base", "HEAD", ref)
        base = r.stdout.strip()
        if r.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        anc = _git_scope(worktree, "merge-base", "--is-ancestor", best, base)
        if anc.returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    r = _git_scope(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if r.returncode != 0:
        raise ReferenceError("git_scope_diff_failed:" + r.stderr.strip())
    return [line for line in r.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    return [p for p in paths if p and not p.startswith(prefix)]
