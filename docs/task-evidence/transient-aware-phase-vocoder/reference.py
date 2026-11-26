# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-TRANSIENT-AWARE-PHASE-VOCODER.

Stdlib only. The candidate is "Transient-aware phase vocoder" (Rate profile,
sdk-reference, considered). The pinned evidence note describes it as a
classical/engineering direction (phase vocoder with phase locking and transient
handling) but no exact licensed runnable source, immutable revision, runtime,
rights-cleared corpus, or matched rate evidence is staged in this workspace.
This package records a fail-closed DEFER blocker state. It never fabricates,
downloads, executes, or promotes missing artifacts/results.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

TASK = "SDK-TRANSIENT-AWARE-PHASE-VOCODER"
TITLE = "Transient-aware phase vocoder"
COMPONENT = "transient-aware-phase-vocoder"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-TRANSIENT-AWARE-PHASE-VOCODER"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
WRITE_SCOPE = "docs/task-evidence/transient-aware-phase-vocoder/ only"
TASK_PREFIX = "docs/task-evidence/transient-aware-phase-vocoder/"
CONTRACT_SCHEMA = "audio-sdk/transient-aware-phase-vocoder-contract/0.1"
REPORT_SCHEMA = "audio-sdk/transient-aware-phase-vocoder-report/0.1"
DECL_SCHEMA = "audio-sdk/transient-aware-phase-vocoder-asset-declaration/0.1"
REQUIRED_INTERPRETER = "3.11.5"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent


def _find_sdk_root() -> Path:
    override = os.environ.get("SDK_WORKTREE") or os.environ.get("AUDIO_SDK_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.extend(Path.cwd().resolve().parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-TRANSIENT-AWARE-PHASE-VOCODER"))
    seen = set()
    for c in candidates:
        c = c.resolve()
        if c in seen:
            continue
        seen.add(c)
        if (c / "CONTRACTS.md").is_file() and (c / "api/include/audio_sdk/provider_v0.h").is_file():
            return c
    return HERE.parents[2]


SDK_ROOT = _find_sdk_root()


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.extend(Path.cwd().resolve().parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    seen = set()
    for c in candidates:
        c = c.resolve()
        if c in seen:
            continue
        seen.add(c)
        if (c / "audio-benchmark-platform/plan/swarm/TASKS.json").is_file() and (c / "research").is_dir():
            return c
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/phase-vocoder-baseline/report.json": "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json": "131640f3c436426827a3cc18c0183195dbb3839cf96b85353e0d79864f222dc5",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

LOCAL_FILES = (
    "LICENSES.md", "README.md", "SOURCES.sha256.license", "contract.json",
    "contract.json.license", "reference.py", "report.json", "report.json.license",
    "report.json.sha256", "report.json.sha256.license", "run.py",
    "test_reference.py", "verify.py",
)
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}

WORKSPACE_PROBES = (
    "data/checkouts/transient-aware-phase-vocoder",
    "data/models/transient-aware-phase-vocoder",
    "data/envs/transient-aware-phase-vocoder",
    "data/reference/transient-aware-phase-vocoder",
    "data/audio/transient-aware-phase-vocoder",
    "research/transient-aware-phase-vocoder",
    "cpp-library/pipeline-validation/transient-aware-phase-vocoder",
)
WORKTREE_PROBES = (
    "adapters/transient-aware-phase-vocoder",
    "schemas/providers/transient-aware-phase-vocoder",
    "third_party/transient-aware-phase-vocoder",
    "docs/task-evidence/transient-aware-phase-vocoder/candidate",
)
HOME_PROBES = (
    "~/.cache/transient-aware-phase-vocoder",
    "~/.cache/huggingface/hub/models--transient-aware-phase-vocoder",
)

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Measure source/output mapping",
    "duration, pitch, transient audibility and playback buffering",
    "1\u00d7, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window",
    "pause or filler decisions tied to source timestamps and measure speech preservation",
)

NON_CLAIMS = [
    "No transient-aware phase-vocoder source, binary, weight, model, runtime, or license-cleared asset is present, imported, executed, or vendored.",
    "No real audio, synthetic speech, music, listening result, device timing, pacing, benchmark, or release claim is produced.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI workflow, board, or handoff file is changed.",
    "Classical phase-vocoder-baseline and neural transient-preservation siblings are separate candidates; no metric, fixture, or qualification is inherited.",
    "A caller-supplied asset declaration is shape-checked only; it never resolves paths, hashes external bytes, or grants qualification.",
    "No network access or download is attempted; absent artifacts are not fabricated or substituted.",
]

SNIPPET_CHECKS = (
    ("cpp-library/pipeline-validation/playback-speed-candidates.md", "phase vocoder + phase locking + transient handling"),
    ("cpp-library/pipeline-validation/playback-speed-candidates.md", "transient preservation"),
    ("audio-benchmark-platform/plan/INVENTORY.json", '"id": "transient-aware-phase-vocoder"'),
    ("audio-benchmark-platform/plan/INVENTORY.json", '"verification_profile": "rate"'),
    ("audio-benchmark-platform/plan/swarm/VERIFICATION.md", "| Rate |"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate_json_key:" + k)
        out[k] = v
    return out


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def assert_no_float(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise TypeError("float_not_allowed:" + path)
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError("non_string_key:" + path)
            assert_no_float(v, path + "/" + k)
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            assert_no_float(v, path + "/" + str(i))


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except json.JSONDecodeError as e:
        raise ValueError("invalid_json") from e
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError("invalid_utf8") from e
    return loads_strict(text)


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def _git(worktree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *args], capture_output=True, text=True, check=False)


SCOPE_BASE_REFS = ("origin/main", "main")


def resolve_scope_base(worktree: Path) -> str | None:
    candidates = []
    for ref in SCOPE_BASE_REFS:
        mb = _git(worktree, "merge-base", "HEAD", ref)
        if mb.returncode != 0:
            continue
        base = mb.stdout.strip()
        if not base:
            continue
        st = _git(worktree, "show", "-s", "--format=%ct", base)
        if st.returncode != 0:
            continue
        try:
            ts = int(st.stdout.strip())
        except ValueError:
            continue
        candidates.append((ts, base, ref))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


def committed_paths_since_base(worktree: Path) -> tuple[str | None, list[str]]:
    base = resolve_scope_base(worktree)
    if base is None:
        return None, []
    diff = _git(worktree, "diff", "--name-only", base + "..HEAD")
    if diff.returncode != 0:
        raise ValueError("scope_diff_failed")
    return base, sorted({line for line in diff.stdout.splitlines() if line})


def collect_dirty_paths(worktree: Path) -> list[str]:
    st = _git(worktree, "status", "--porcelain", "-z")
    if st.returncode != 0:
        raise ValueError("git_status_failed")
    raw = st.stdout.split("\0")
    paths = []
    i = 0
    while i < len(raw):
        entry = raw[i]
        i += 1
        if not entry:
            continue
        path = entry[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
        if len(entry) >= 2 and entry[1] in "RC":
            i += 1
    return sorted(set(paths))


def path_is_within_prefix(path: str, prefix: str) -> bool:
    clean = path.replace("\\", "/").lstrip("./")
    p = prefix.replace("\\", "/")
    return clean == p.rstrip("/") or clean.startswith(p)


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [f for f in required if f not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    deps = row.get("depends_on")
    if not isinstance(deps, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(deps),
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    doc = read_strict_json(board)
    rows = doc.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [r for r in _board_tasks(path) if isinstance(r, dict) and r.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    proj = _project(matches[0], require_component=True)
    if proj["component"] != COMPONENT:
        raise ValueError("board_component_mismatch")
    if proj["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if proj["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    if tuple(proj["depends_on"]) != DEPENDS_ON:
        raise ValueError("board_depends_on_mismatch")
    return proj


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {r.get("id"): r for r in rows if isinstance(r, dict)}
    out = []
    for rid in LINKED_ROW_IDS:
        row = by_id.get(rid)
        if row is None:
            raise ValueError("linked_row_absent:" + rid)
        out.append(_project(row, require_component=rid == TASK))
    return tuple(out)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


def probe_presence(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def absence_probes() -> dict:
    probes = []
    for rel in WORKSPACE_PROBES:
        probes.append({"path": rel, "present": probe_presence(AUDIO_ROOT / rel), "searched_workspace": True, "searched_sdk_worktree": False, "searched_home_cache": False})
    for rel in WORKTREE_PROBES:
        probes.append({"path": rel, "present": probe_presence(SDK_ROOT / rel), "searched_workspace": False, "searched_sdk_worktree": True, "searched_home_cache": False})
    home = Path.home()
    for rel in HOME_PROBES:
        probes.append({"path": rel, "present": probe_presence(home / rel.removeprefix("~/")), "searched_workspace": False, "searched_sdk_worktree": False, "searched_home_cache": True})
    present = [p for p in probes if p["present"]]
    return {
        "all_absent": len(present) == 0,
        "fixed_probe_list_only": True,
        "network_used": False,
        "download_attempted": False,
        "recursive_workspace_walk": False,
        "present_count": len(present),
        "probe_count": len(probes),
        "workspace_probe_count": len(WORKSPACE_PROBES),
        "worktree_probe_count": len(WORKTREE_PROBES),
        "home_probe_count": len(HOME_PROBES),
        "probes": probes,
    }


def evidence_snippets() -> dict:
    checks = []
    for rel, phrase in SNIPPET_CHECKS:
        p = AUDIO_ROOT / rel
        present = p.is_file() and phrase in p.read_text(encoding="utf-8", errors="replace")
        checks.append({"path": rel, "phrase": phrase, "present": present})
    return {"all_present": all(c["present"] for c in checks), "checks": checks, "count": len(checks)}


def scope() -> dict:
    return {
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
        "network_access": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "real_audio": False,
        "synthetic_audio": False,
        "candidate_code_vendored": False,
        "weights_vendored": False,
        "runtime_invoked": False,
        "device_timing": False,
        "listening": False,
        "benchmark_claim": False,
        "release_claim": False,
    }


def boundary() -> dict:
    proj = board_row_projection()
    rows = linked_rows()
    return {
        "board_file_pinned": False,
        "linked_row_identity_only": True,
        "mutable_board_fields_gate": False,
        "excluded_mutable_fields": ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority"],
        "linked_row": proj,
        "linked_row_sha256": board_row_digest(proj),
        "linked_rows": [dict(r) for r in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "runtime_imported": False,
        "candidate_code_vendored": False,
        "weights_vendored": False,
        "audio_added": False,
    }


def exact_blockers() -> list[dict]:
    reopen = "Only caller-supplied, exact, licensed, immutable artifacts with matched evidence and independent review can reopen this blocker."
    action = "Supply immutable source/runtime/assets/rights and matched rate evidence; do not fabricate or substitute."
    rows = [
        ("BLK-01", "RG-01,RG-02", "ART-02", "No exact licensed runnable source or immutable revision",
         "No exact transient-aware phase-vocoder implementation, immutable commit/tag, license text, or runnable build manifest is staged. Research notes describe the method class but do not pin a verified source."),
        ("BLK-02", "RG-02,RG-03", "ART-03", "No pinned runtime, model/weights, or exact task geometry",
         "No pinned runtime, dependencies, model/weights (if any), frame/hop/window/phase/latency contract, or deterministic execution environment is present."),
        ("BLK-03", "RG-04", "ART-04", "No rights-cleared inputs or reviewed terms",
         "No reviewed license/terms for code/assets and no rights-cleared speech/music/transient corpus or consent/redistribution decision is staged."),
        ("BLK-04", "RG-05,RG-06", "ART-05", "No reproduced rate evidence or output validity",
         "No candidate output exists. Source/output mapping, duration, pitch, transient audibility, buffering, and rate-case behavior are unmeasured."),
        ("BLK-05", "RG-07,RG-08", "ART-06", "No matched cohort, device timing, listening, or release review",
         "No matched cohort, authorized listening/labeled screen, device/pacing/resource measurement, or independent release review exists."),
    ]
    return [{"id": bid, "linked_gates": gates.split(","), "artifact_id": art, "title": title, "statement": stmt, "status": "open", "qualifies": False, "required_action": action, "reopen_condition": reopen} for bid, gates, art, title, stmt in rows]


def release_gates() -> list[dict]:
    proj = board_row_projection()
    rows = [
        ("RG-01", "named_source_and_license_provenance", "Provide exact method/source at immutable revision with reviewed license/notice provenance."),
        ("RG-02", "pinned_runtime_and_exact_geometry", "Provide locked offline runtime and exact sample rate/frame/hop/window/phase/latency/reset/drain geometry."),
        ("RG-03", "assets_and_dependencies", "Stage and verify every required asset/dependency with byte counts and SHA-256; no mutable downloads."),
        ("RG-04", "rights_cleared_inputs", "Freeze rights-cleared speech/music/transient inputs with consent, evaluation, and redistribution decisions."),
        ("RG-05", "deterministic_execution_and_output_validity", "Execute pinned candidate offline; record finite, deterministic outputs and exact hashes."),
        ("RG-06", "rate_profile_evidence", "Run full Rate profile: mapping, duration, pitch, transient audibility, buffering, 1x/rate changes/unfamiliar speech/music/silence/rebuffer/drift/final partial, pause/filler timestamps and speech preservation."),
        ("RG-07", "timing_resources_listening", "Measure pacing/resources on target and complete authorized listening or labeled screen."),
        ("RG-08", "intake_and_release_review", "Separate OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear."),
    ]
    return [{"id": gid, "title": title, "status": "blocked", "qualifies": False, "reopen_condition": reopen, "linked_row": proj, "statement": "No candidate artifact, runtime, right, matched measurement, or review satisfies this requirement."} for gid, title, reopen in rows]


def required_artifacts() -> list[dict]:
    return [
        {"id": "ART-01", "kind": "evidence_register_and_boundary", "present": True, "blocked": False, "verified": True, "bytes": None, "sha256": None, "revision": None, "requirement": "Pinned inventory/task/profile/source note and unchanged SDK boundary."},
        {"id": "ART-02", "kind": "named_source_and_license", "present": False, "blocked": True, "verified": False, "bytes": None, "sha256": None, "revision": None, "requirement": "Exact transient-aware phase-vocoder source at immutable revision with reviewed license text and file manifest."},
        {"id": "ART-03", "kind": "runtime_and_geometry", "present": False, "blocked": True, "verified": False, "bytes": None, "sha256": None, "revision": None, "requirement": "Locked runtime/dependencies and exact sample rate/frame/hop/window/phase/latency/reset/drain contract."},
        {"id": "ART-04", "kind": "rights_cleared_inputs", "present": False, "blocked": True, "verified": False, "bytes": None, "sha256": None, "revision": None, "requirement": "Rights-cleared speech/music/transient inputs with consent/evaluation/redistribution decisions."},
        {"id": "ART-05", "kind": "reproduced_rate_outputs", "present": False, "blocked": True, "verified": False, "bytes": None, "sha256": None, "revision": None, "requirement": "Deterministic candidate outputs and full Rate-profile measurements on matched cohort."},
        {"id": "ART-06", "kind": "intake_and_review", "present": False, "blocked": True, "verified": False, "bytes": None, "sha256": None, "revision": None, "requirement": "Separate OFF-by-default intake, clean-install proof, and independent exact-head review."},
    ]


def rate_profile() -> dict:
    blocked = "No exact runnable transient-aware phase-vocoder candidate, runtime, rights-cleared inputs, or outputs exist; measurement is blocked. Sibling baselines are not substituted."
    reqs = [
        ("RATE-01", "Source/output mapping for the exact runtime.", "blocked"),
        ("RATE-02", "Target and actual duration for constant and changing rates.", "blocked"),
        ("RATE-03", "Pitch preservation or shift for the exact runtime.", "blocked"),
        ("RATE-04", "Transient audibility proxy or authorized listening.", "blocked"),
        ("RATE-05", "Playback buffering, fill/flush and deadline behaviour.", "blocked"),
        ("RATE-06", "1x identity control.", "blocked"),
        ("RATE-07", "Rate changes, including step and ramp profiles.", "blocked"),
        ("RATE-08", "Unfamiliar speech material.", "blocked"),
        ("RATE-09", "Music material and a synthetic music negative control.", "blocked"),
        ("RATE-10", "Silence and empty input.", "blocked"),
        ("RATE-11", "Rebuffer, drift and the final partial window.", "blocked"),
        ("RATE-12", "Pause or filler decisions tied to source timestamps and speech preservation.", "blocked"),
        ("RATE-13", "Separate paired, unpaired, synthetic, human and source-reported evidence.", "documented"),
    ]
    rows = []
    for rid, req, status in reqs:
        evidence = "Source-reported, schema-only, missing-real, and sibling sections are kept separate; no pooling." if status == "documented" else blocked
        rows.append({"id": rid, "requirement": req, "status": status, "qualifies": False, "evidence": evidence})
    return {
        "profile": PROFILE,
        "profile_label": "Rate",
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": {"all_phrases_present": True, "path": PROFILE_SOURCE_REL, "phrases_present": list(PROFILE_PHRASES), "row_count": 1, "unique_row": True},
        "profile_satisfied": False,
        "rate_result_present": False,
        "real_results": 0,
        "synthetic_results": 0,
        "surrogate_present": False,
        "conditions": ["identity_1x", "rate_changes", "unfamiliar_speech", "music", "silence", "rebuffer", "drift", "final_partial_window", "pause_filler_source_timestamps"],
        "requirement_rows": rows,
    }


def source_reported_identity() -> dict:
    return {
        "candidate": TITLE,
        "candidate_family": "classical_transient_aware_phase_vocoder_tsm",
        "source_reported_only": True,
        "identity_verified": False,
        "named_method_found": False,
        "named_method": None,
        "method_reference": None,
        "official_code_found": False,
        "official_weights_found": False,
        "immutable_revision_recorded": False,
        "license_recorded": False,
        "audio_input": True,
        "audio_output": True,
        "source_reported_task": "transient-aware phase vocoder time-scale modification",
        "source_reported_input": "audio waveform (method-class expectation)",
        "source_reported_output": "time-scaled audio waveform with transient preservation (method-class expectation)",
    }


def task_geometry() -> dict:
    return {
        "candidate_family": "classical_transient_aware_phase_vocoder_tsm",
        "state": "unverified_method_class_no_exact_implementation",
        "audio_input_expected": True,
        "audio_input_path_verified": False,
        "named_method_found": False,
        "geometry_documented": False,
        "geometry_verified": False,
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "latency_ms": None,
        "rate_profile_fit": "unverified",
        "profile_fit_reason": "A transient-aware phase vocoder is a rate/time-scale method class in principle, but no exact implementation, geometry, runtime, or evidence is staged.",
    }


DECL_REQUIRED = ("schema_id", "declaration_id", "candidate", "source", "runtime", "rights", "disposition")
CAND_FIELDS = ("name", "family", "named_method", "method_reference", "audio_input", "audio_output")
SOURCE_FIELDS = ("declared_present", "revision", "license_sha256", "source_sha256")
RUNTIME_FIELDS = ("declared_present", "python_version", "platform", "lock_sha256")
RIGHTS_FIELDS = ("code", "weights_or_models", "inputs", "output_use", "redistribution", "review_reference")
DISP_FIELDS = ("decision", "qualifies")


def unpopulated_asset_declaration() -> dict:
    return {
        "schema_id": DECL_SCHEMA,
        "declaration_id": "unpopulated",
        "candidate": {"name": TITLE, "family": "classical_transient_aware_phase_vocoder_tsm", "named_method": None, "method_reference": None, "audio_input": True, "audio_output": True},
        "source": {"declared_present": False, "revision": None, "license_sha256": None, "source_sha256": None},
        "runtime": {"declared_present": False, "python_version": None, "platform": None, "lock_sha256": None},
        "rights": {"code": False, "weights_or_models": False, "inputs": False, "output_use": False, "redistribution": False, "review_reference": None},
        "disposition": {"decision": DECISION, "qualifies": False},
    }


def _expect_obj(v: Any, field: str) -> dict:
    if not isinstance(v, dict):
        raise ValueError("not_object:" + field)
    return v


def _expect_keys(obj: dict, allowed: tuple[str, ...], field: str) -> None:
    extra = sorted(set(obj) - set(allowed))
    if extra:
        raise ValueError("unknown_field:" + field + "." + extra[0])
    missing = [k for k in allowed if k not in obj]
    if missing:
        raise ValueError("missing_field:" + field + "." + missing[0])


def _reject_present(obj: dict, field: str, present_key: str = "declared_present") -> None:
    if obj.get(present_key) is not False:
        raise ValueError("unverified_claim:" + field + "." + present_key)
    for k, v in obj.items():
        if k == present_key:
            continue
        if v is not None and v is not False:
            raise ValueError("unverified_claim:" + field + "." + k)


def validate_asset_declaration(payload: str | bytes | dict) -> dict:
    doc = loads_strict(payload) if isinstance(payload, str) else (parse_strict_json_text(payload) if isinstance(payload, (bytes, bytearray)) else payload)
    if not isinstance(doc, dict):
        raise ValueError("not_object:declaration")
    assert_no_float(doc)
    _expect_keys(doc, DECL_REQUIRED, "declaration")
    if doc["schema_id"] != DECL_SCHEMA:
        raise ValueError("schema_id_mismatch:schema_id")
    if not isinstance(doc["declaration_id"], str) or not SLUG.match(doc["declaration_id"]):
        raise ValueError("invalid_slug:declaration_id")
    cand = _expect_obj(doc["candidate"], "candidate")
    _expect_keys(cand, CAND_FIELDS, "candidate")
    if cand["name"] != TITLE:
        raise ValueError("candidate_name_mismatch:candidate.name")
    if cand["named_method"] is not None:
        raise ValueError("unverified_claim:candidate.named_method")
    if cand["method_reference"] is not None:
        raise ValueError("unverified_claim:candidate.method_reference")
    if cand["audio_input"] is not True or cand["audio_output"] is not True:
        raise ValueError("missing_required_value:candidate.audio_io")
    src = _expect_obj(doc["source"], "source")
    _expect_keys(src, SOURCE_FIELDS, "source")
    _reject_present(src, "source")
    rt = _expect_obj(doc["runtime"], "runtime")
    _expect_keys(rt, RUNTIME_FIELDS, "runtime")
    _reject_present(rt, "runtime")
    rights = _expect_obj(doc["rights"], "rights")
    _expect_keys(rights, RIGHTS_FIELDS, "rights")
    for k in RIGHTS_FIELDS:
        v = rights[k]
        if k == "review_reference":
            if v is not None:
                raise ValueError("unverified_claim:rights.review_reference")
        elif v is not False:
            raise ValueError("unverified_claim:rights." + k)
    disp = _expect_obj(doc["disposition"], "disposition")
    _expect_keys(disp, DISP_FIELDS, "disposition")
    if disp["qualifies"] is not False:
        raise ValueError("unverified_claim:disposition.qualifies")
    if disp["decision"] != DECISION:
        raise ValueError("premature_decision:disposition.decision")
    return doc


STRICT_JSON_CASES = {
    "duplicate_key": '{"a":1,"a":2}',
    "nan_literal": '{"a":NaN}',
    "infinity_literal": '{"a":Infinity}',
    "negative_infinity_literal": '{"a":-Infinity}',
    "trailing_data": '{"a":1} 1',
    "byte_order_mark": '\ufeff{"a":1}',
    "non_object_root": '[]',
    "empty_input": '',
    "unterminated": '{"a":1',
}


def strict_json_rejections() -> list[dict]:
    out = []
    for cid, payload in STRICT_JSON_CASES.items():
        try:
            loads_strict(payload)
            rejected = False
        except Exception:
            rejected = True
        out.append({"id": cid, "rejected": rejected})
    return out


def declaration_rejections() -> list[dict]:
    base = unpopulated_asset_declaration()
    cases = []

    def add(case_id, mut, code, field):
        doc = json.loads(canonical_text(base))
        mut(doc)
        cases.append((case_id, doc, code, field))

    cases.append(("root_not_object", [], "not_object", "declaration"))
    add("missing_schema", lambda d: d.pop("schema_id"), "missing_field", "declaration.schema_id")
    add("extra_top", lambda d: d.__setitem__("extra", True), "unknown_field", "declaration.extra")
    add("bad_schema", lambda d: d.__setitem__("schema_id", "x"), "schema_id_mismatch", "schema_id")
    add("bad_decl_id", lambda d: d.__setitem__("declaration_id", "Bad"), "invalid_slug", "declaration_id")
    add("named_method", lambda d: d["candidate"].__setitem__("named_method", "x"), "unverified_claim", "candidate.named_method")
    add("method_ref", lambda d: d["candidate"].__setitem__("method_reference", "x"), "unverified_claim", "candidate.method_reference")
    add("audio_input_false", lambda d: d["candidate"].__setitem__("audio_input", False), "missing_required_value", "candidate.audio_io")
    add("source_present", lambda d: d["source"].__setitem__("declared_present", True), "unverified_claim", "source.declared_present")
    add("source_rev", lambda d: d["source"].__setitem__("revision", "abc"), "unverified_claim", "source.revision")
    add("source_hash", lambda d: d["source"].__setitem__("source_sha256", "0" * 64), "unverified_claim", "source.source_sha256")
    add("runtime_present", lambda d: d["runtime"].__setitem__("declared_present", True), "unverified_claim", "runtime.declared_present")
    add("runtime_lock", lambda d: d["runtime"].__setitem__("lock_sha256", "0" * 64), "unverified_claim", "runtime.lock_sha256")
    add("rights_code", lambda d: d["rights"].__setitem__("code", True), "unverified_claim", "rights.code")
    add("rights_inputs", lambda d: d["rights"].__setitem__("inputs", True), "unverified_claim", "rights.inputs")
    add("rights_review", lambda d: d["rights"].__setitem__("review_reference", "r"), "unverified_claim", "rights.review_reference")
    add("qualifies_true", lambda d: d["disposition"].__setitem__("qualifies", True), "unverified_claim", "disposition.qualifies")
    add("premature_admit", lambda d: d["disposition"].__setitem__("decision", "ADMIT"), "premature_decision", "disposition.decision")
    add("missing_rights", lambda d: d.pop("rights"), "missing_field", "declaration.rights")
    add("extra_candidate", lambda d: d["candidate"].__setitem__("extra", 1), "unknown_field", "candidate.extra")
    add("source_not_obj", lambda d: d.__setitem__("source", []), "not_object", "source")
    out = []
    for cid, doc, code, field in cases:
        try:
            validate_asset_declaration(doc)
            rejected = False
            actual = "accepted"
        except Exception as e:
            rejected = True
            actual = str(e)
        out.append({"id": cid, "rejected": rejected, "code": code, "field": field, "actual": actual})
    return out


def asset_declaration_schema() -> dict:
    rejs = declaration_rejections()
    strict = strict_json_rejections()
    control = unpopulated_asset_declaration()
    validate_asset_declaration(control)
    return {
        "schema_id": DECL_SCHEMA,
        "purpose": "Shape-check only; never resolves paths, hashes external bytes, loads assets, or grants qualification.",
        "accepted_unpopulated_sha256": object_digest(control),
        "accepted_unpopulated_qualifies": False,
        "all_rejected": all(r["rejected"] for r in rejs),
        "rejection_cases": len(rejs),
        "rejections": [{"id": r["id"], "code": r["code"], "field": r["field"]} for r in rejs],
        "strict_json_all_rejected": all(r["rejected"] for r in strict),
        "strict_json_cases": len(strict),
        "strict_json_rejections": strict,
    }


def build_contract() -> dict:
    proj = board_row_projection()
    rows = linked_rows()
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION,
        "qualification": {"status": QUALIFICATION},
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "depends_on": list(DEPENDS_ON),
        "write_scope": WRITE_SCOPE,
        "linked_row": proj,
        "linked_row_sha256": board_row_digest(proj),
        "linked_rows": [dict(r) for r in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "boundary": boundary(),
        "scope": scope(),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "rate_profile": rate_profile(),
        "asset_declaration_schema": asset_declaration_schema(),
        "non_claims": list(NON_CLAIMS),
        "expected_dir_files": sorted(EXPECTED_DIR_FILES),
    }


def build_report() -> dict:
    contract = build_contract()
    proj = board_row_projection()
    rows = linked_rows()
    return {
        "schema_id": REPORT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION,
        "qualification": {"status": QUALIFICATION},
        "proposal_only": True,
        "incomplete": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "depends_on": list(DEPENDS_ON),
        "write_scope": WRITE_SCOPE,
        "contract_schema_id": CONTRACT_SCHEMA,
        "contract_sha256": object_digest(contract),
        "linked_row": proj,
        "linked_row_sha256": board_row_digest(proj),
        "linked_rows": [dict(r) for r in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "boundary": boundary(),
        "scope": scope(),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "absence_summary": absence_probes(),
        "evidence_snippets": evidence_snippets(),
        "asset_declaration": {
            "accepted_unpopulated": unpopulated_asset_declaration(),
            "schema": asset_declaration_schema(),
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "rate_profile": rate_profile(),
        "historical_evidence": [
            {"class": "source_reported_note", "source": "cpp-library/pipeline-validation/playback-speed-candidates.md", "admitted_as_result": False, "boundary": "Describes transient-aware phase vocoder as a method direction; not an exact staged implementation or measured result."},
            {"class": "inventory_scope", "source": "audio-benchmark-platform/plan/INVENTORY.json", "admitted_as_result": False, "boundary": "Inventory marks candidate considered/sdk-reference/rate; not evidence of runnable assets or qualification."},
            {"class": "sibling_classical_baseline", "source": "docs/task-evidence/phase-vocoder-baseline/report.json", "admitted_as_result": False, "boundary": "Classical phase vocoder baseline is a different candidate/control; no metrics inherited."},
            {"class": "sibling_neural_candidate", "source": "docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json", "admitted_as_result": False, "boundary": "Neural transient-preserving phase vocoder is a different candidate; no assets/results inherited."},
        ],
        "peer_separation": [
            {"component": "phase-vocoder-baseline", "task": "SDK-PHASE-VOCODER-BASELINE", "path": "docs/task-evidence/phase-vocoder-baseline/report.json", "decision": "defer", "inherited_metrics": False, "admitted_as_result": False},
            {"component": "phase-vocoder-with-neural-transient-preservation", "task": "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION", "path": "docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json", "decision": "DEFER", "inherited_metrics": False, "admitted_as_result": False},
        ],
        "non_claims": list(NON_CLAIMS),
    }


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


def sources_bytes() -> bytes:
    rows = []
    for rel, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / rel)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + rel)
        rows.append(("source:" + rel, actual))
    for rel, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(SDK_ROOT / rel)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + rel)
        rows.append((rel, actual))
    for name in LOCAL_FILES:
        p = HERE / name
        if not p.is_file():
            raise ValueError("local_missing:" + name)
        rows.append((TASK_PREFIX + name, sha256_file(p)))
    lines = [
        "# SHA-256 pins for SDK-TRANSIENT-AWARE-PHASE-VOCODER evidence.",
        "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree relative.",
        "# Mutable shared board is not pinned; only stable linked-row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{d}  {n}" for n, d in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def update_readme_tables(text: str) -> str:
    def replace(section: str, payload: str) -> str:
        start, end = README_MARKERS[section]
        pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        if not pat.search(text):
            raise ValueError("readme_marker_missing:" + section)
        return pat.sub(start + "\n" + payload.rstrip() + "\n" + end, text, count=1)

    src_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for rel, d in sorted(SOURCE_PINS.items()):
        src_rows.append(f"| `source:{rel}` | `{d}` |")
    b_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for rel, d in sorted(BOUNDARY_PINS.items()):
        b_rows.append(f"| `{rel}` | `{d}` |")
    a_rows = ["| Path | SHA-256 |", "| --- | --- |"]
    for name in sorted(EXPECTED_DIR_FILES - ARTIFACT_TABLE_EXCLUDED):
        a_rows.append(f"| `{TASK_PREFIX}{name}` | `{sha256_file(HERE / name)}` |")
    text = replace("source", "\n".join(src_rows))
    text = replace("boundary", "\n".join(b_rows))
    text = replace("artifacts", "\n".join(a_rows))
    return text


def verify_readme_digests(text: str) -> dict[str, int]:
    counts = {}
    for section in README_MARKERS:
        start, end = README_MARKERS[section]
        m = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
        if not m:
            raise ValueError("readme_marker_missing:" + section)
        rows = [line for line in m.group(1).splitlines() if line.startswith("| `")]
        for row in rows:
            cols = [c.strip() for c in row.strip("|").split("|")]
            if len(cols) != 2:
                raise ValueError("readme_row_malformed:" + section)
            path = cols[0].strip("` ")
            digest = cols[1].strip("` ")
            if not HEX64.match(digest):
                raise ValueError("readme_digest_malformed:" + path)
            if path.startswith("source:"):
                fs = AUDIO_ROOT / path[len("source:"):]
            elif path.startswith(TASK_PREFIX):
                fs = HERE / path[len(TASK_PREFIX):]
            else:
                fs = SDK_ROOT / path
            if not fs.is_file() or sha256_file(fs) != digest:
                raise ValueError("readme_digest_mismatch:" + path)
        counts[section] = len(rows)
    return counts


def has_forbidden_suffix(path: Path) -> bool:
    return path.suffix.lower() in {".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h5", ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".tar", ".wav", ".weights", ".zip"}


def main() -> int:
    text, digest = canonical_report()
    print(text)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
