# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local blocker evidence for SDK-OPTFRACTASII-APPROXIMATION.

Standard library only. This package records that no exact licensed
OptFractASII/NELE source snapshot, runtime, rights-cleared cohort, or
device/listening evidence is present. It never downloads, imports candidate
code, reads audio, or promotes source-reported research to a qualified result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-OPTFRACTASII-APPROXIMATION"
TASK_TITLE = "OptFractASII approximation"
COMPONENT_ID = "optfractasii-approximation"
REPOSITORY = "audio-sdk"
MODE = "research-control"
PROFILE = "dsp"
PROFILE_LABEL = "DSP"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/optfractasii-approximation/ only"
TASK_PREFIX = "docs/task-evidence/optfractasii-approximation/"
CONTRACT_ID = "audio-sdk/optfractasii-approximation-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/optfractasii-approximation-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/optfractasii-approximation-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/optfractasii-approximation-asset-declaration/0.1"
BASE_COMMIT = "0b0f2dee5902278fcea1a47f576b4df70e99ab3a"
BRANCH = "swarm/SDK-OPTFRACTASII-APPROXIMATION"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
REQUIRED_INTERPRETER = "3.11.5"
CANDIDATE_NAME = "OptFractASII approximation"
SPDX_LICENSE_IDENTIFIER = "SPDX-License-" + "Identifier: Apache-2.0"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


def _find_sdk_root() -> Path:
    override = os.environ.get("SDK_WORKTREE")
    if override:
        return Path(override).resolve()
    for candidate in HERE.parents:
        if (candidate / "CONTRACTS.md").is_file() and (candidate / "api/include/audio_sdk").is_dir():
            return candidate.resolve()
    return HERE.parents[2].resolve()


AUDIO_ROOT = _find_audio_root()
SDK_ROOT = _find_sdk_root()
WORKTREE = SDK_ROOT

SOURCE_PINS = {
    "research/listening_intelligibility_20261028.md":
        "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
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
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control",
    "gain, response, attack/release where applicable, headroom, delay and numerical behavior",
    "state transitions and interacting nonlinear configurations",
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
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->", "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h5", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".otf", ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".tar", ".ttf", ".wav", ".wasm", ".weights", ".zip",
}

WORKSPACE_PROBES = (
    "data/checkouts/optfractasii",
    "data/checkouts/OptFractASII",
    "data/models/optfractasii",
    "data/envs/optfractasii",
    "data/audio/optfractasii",
    "data/runs/optfractasii",
    "research/optfractasii",
    "research/voice-enhancement-20261101/optfractasii",
)
WORKTREE_PROBES = (
    "adapters/optfractasii-approximation",
    "schemas/providers/optfractasii-approximation",
    "third_party/optfractasii",
    "third_party/OptFractASII",
    "build/check-env/lib/python3.11/site-packages/optfractasii",
)
HOME_PROBES = (
    "~/.cache/optfractasii",
    "~/.cache/huggingface/hub/models--optfractasii",
)

NON_CLAIMS = [
    "No exact licensed OptFractASII source snapshot, binary, model, or runtime is present, imported, executed, or redistributed.",
    "No real speech, masker, listening panel, hearing profile, or rights-cleared cohort is present or fabricated.",
    "No STOI/ESTOI, intelligibility, MOS, device timing, CPU, deadline, memory, or benchmark result is reproduced by this package.",
    "The pinned research note is source-reported context only; its local approximation numbers are not promoted to release-quality or qualification evidence.",
    "No provider registration, descriptor, registry, default, public ABI, shared build, CI workflow, board, or handoff change exists.",
    "The caller-supplied asset declaration is a fail-closed shape check only; it never resolves paths, hashes external bytes, or grants qualification.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored, or substituted.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "research/listening_intelligibility_20261028.md",
        "line": 4,
        "class": "source_reported_research_note",
        "admitted_as_result": False,
        "boundary": "Reports a small objective benchmark with fixed spectral tilt ranking first by mean STOI/ESTOI in that screen; explicitly states no deployment candidate is selected and no listener test was run.",
    },
    {
        "source": "research/listening_intelligibility_20261028.md",
        "line": 20,
        "class": "source_reported_algorithm_note",
        "admitted_as_result": False,
        "boundary": "Describes a local noise-aware water-filling inspired by OptFractASII as an approximation, not a faithful reproduction; no exact licensed upstream artifact is identified.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks optfractasii-approximation as evaluated research-control with DSP profile; it is not a qualified release result.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines DSP profile requirements; no DSP measurement in this package satisfies qualification.",
    },
)

PEER_SEPARATION = (
    {
        "component": "fixed-six-band-spectral-tilt",
        "task": "SDK-FIXED-SIX-BAND-SPECTRAL-TILT",
        "path": "docs/task-evidence/fixed-six-band-spectral-tilt/README.md",
        "class": "separate_dsp_reference",
        "decision": "synthetic-evidence-only",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Fixed six-band spectral tilt is a separate deterministic DSP reference with its own synthetic evidence; its results are not inherited as OptFractASII qualification.",
    },
    {
        "component": "noise-aware-shaping-plus-drc",
        "task": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC",
        "path": "plan/swarm/handoffs/SDK-NOISE-AWARE-SHAPING-PLUS-DRC.md",
        "class": "separate_blocked_research_control",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Noise-aware shaping plus DRC is a related but distinct blocked research-control package; no blocker count, gate, or metric is inherited.",
    },
)


# ---------------------------------------------------------------------------
# Strict JSON / canonical
# ---------------------------------------------------------------------------

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def assert_no_float(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise TypeError("float not allowed in canonical evidence: " + path)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non-string key at " + path)
            assert_no_float(item, path + "/" + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_no_float(item, path + "/" + str(index))


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Board identity
# ---------------------------------------------------------------------------

def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path) if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    if tuple(projection["depends_on"]) != DEPENDS_ON:
        raise ValueError("board_depends_on_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    result: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_absent:" + row_id)
        result.append(_project(row, require_component=row_id == TASK))
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


# ---------------------------------------------------------------------------
# Git scope
# ---------------------------------------------------------------------------
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments], capture_output=True, text=True, encoding="utf-8", errors="replace")


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", ref + "^{commit}")
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def scope_base(worktree: Path, refs: Iterable[str] = SCOPE_BASE_REFS) -> str | None:
    candidates: list[tuple[int, str]] = []
    for ref in refs:
        mb = _git(worktree, "merge-base", "HEAD", ref)
        if mb.returncode != 0:
            continue
        base = mb.stdout.strip()
        if not base:
            continue
        count = _git(worktree, "rev-list", "--count", base + "..HEAD")
        if count.returncode != 0:
            continue
        try:
            distance = int(count.stdout.strip())
        except ValueError:
            continue
        candidates.append((distance, base))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][1]


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", base + "..HEAD")
    if result.returncode != 0:
        raise ValueError("scope_diff_failed")
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(set(paths))


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    violations: list[str] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
            continue
        violations.append("base_out_of_scope_change:" + normalized)
    return sorted(violations)


# ---------------------------------------------------------------------------
# Absence probes
# ---------------------------------------------------------------------------

def _probe(path: Path, label: str, workspace: bool, worktree: bool, home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def workspace_probes() -> list[dict]:
    return [_probe(AUDIO_ROOT / rel, rel, True, False, False) for rel in WORKSPACE_PROBES]


def worktree_probes() -> list[dict]:
    return [_probe(SDK_ROOT / rel, rel, False, True, False) for rel in WORKTREE_PROBES]


def home_probes() -> list[dict]:
    home = Path.home()
    return [_probe(home / rel.replace("~/", ""), rel, False, False, True) for rel in HOME_PROBES]


def all_probes() -> list[dict]:
    return workspace_probes() + worktree_probes() + home_probes()


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = list(probes if probes is not None else all_probes())
    present = [row["path"] for row in rows if row["present"]]
    return {
        "all_absent": not present,
        "present_count": len(present),
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for r in rows if r["searched_workspace"]),
        "worktree_probe_count": sum(1 for r in rows if r["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for r in rows if r["searched_home_cache"]),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "network_used": False,
        "download_attempted": False,
        "audio_read": False,
        "candidate_runtime_executed": False,
        "candidate_module_imported": False,
        "weights_loaded": False,
        "probes": rows,
        "present_paths": present,
    }


# ---------------------------------------------------------------------------
# Pins / manifests / README
# ---------------------------------------------------------------------------

def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows = []
    for rel, expected in sorted(pins.items()):
        path = root / rel
        present = path.is_file()
        actual = sha256_file(path) if present else None
        rows.append({
            "path": rel,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "present": present,
            "matches": present and actual == expected,
        })
    return rows


def _local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir() if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    lines = []
    for name in _local_manifest_paths():
        lines.append(f"{sha256_file(HERE / name)}  {name}\n")
    return "".join(lines).encode("ascii")


def expected_readme_keys() -> dict[str, set[str]]:
    source = {f"source:{p}" for p in SOURCE_PINS}
    boundary = {f"boundary:{p}" for p in BOUNDARY_PINS}
    artifacts = {f"artifact:{p.name}" for p in HERE.iterdir() if p.is_file() and p.name not in ARTIFACT_TABLE_EXCLUDED}
    return {"source": source, "boundary": boundary, "artifacts": artifacts}


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if start not in text or end not in text:
        raise ValueError(f"missing_readme_marker:{section}")
    s = text.index(start) + len(start)
    e = text.index(end, s)
    return text[s:e]


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: list[tuple[str, str]] = []
        for raw in _section_text(text, section).splitlines():
            line = raw.strip()
            if not line.startswith("|") or line.startswith("| ---"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2 or cells[0] in {"key", "path"} or cells[1] == "sha256":
                continue
            digest = cells[1].strip("` ")
            key = cells[0].strip("` ")
            if HEX64.fullmatch(digest):
                rows.append((key, digest))
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    counts = {}
    for section in README_SECTIONS:
        rows = parsed[section]
        keys = [k for k, _ in rows]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate_readme_key:{section}")
        if set(keys) != expected[section]:
            raise ValueError(f"readme_keys_mismatch:{section}")
        for key, digest in rows:
            if section == "source":
                rel = key.removeprefix("source:")
                actual = sha256_file(AUDIO_ROOT / rel)
            elif section == "boundary":
                rel = key.removeprefix("boundary:")
                actual = sha256_file(SDK_ROOT / rel)
            else:
                rel = key.removeprefix("artifact:")
                actual = sha256_file(HERE / rel)
            if actual != digest:
                raise ValueError(f"readme_digest_mismatch:{section}:{rel}")
        counts[section] = len(rows)
    return counts


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = [(f"source:{p}", d) for p, d in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = [(f"boundary:{p}", d) for p, d in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = []
        for p in sorted(HERE.iterdir(), key=lambda x: x.name):
            if p.is_file() and p.name not in ARTIFACT_TABLE_EXCLUDED:
                rows.append((f"artifact:{p.name}", sha256_file(p)))
    else:
        raise ValueError("unknown_section")
    lines = ["| key | sha256 |", "| --- | --- |"]
    for k, d in rows:
        lines.append(f"| `{k}` | `{d}` |")
    return "\n".join(lines)


def update_readme_table(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    s = text.index(start) + len(start)
    e = text.index(end, s)
    return text[:s] + "\n" + render_digest_table(section) + "\n" + text[e:]


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Identity / geometry / profile
# ---------------------------------------------------------------------------

def source_reported_identity() -> dict:
    return {
        "candidate": CANDIDATE_NAME,
        "candidate_family": "near_end_listening_enhancement",
        "named_upstream_method": "OptFractASII (source-reported inspiration only)",
        "method_reference": "Villani et al., Interspeech 2025 (cited in pinned note; not independently fetched or verified here)",
        "local_implementation_name": "OptFractASII approximation",
        "exact_upstream_source_present": False,
        "exact_upstream_revision_recorded": False,
        "license_recorded": False,
        "license_text_staged": False,
        "runnable_as_released": False,
        "source_reported_only": True,
        "identity_verified": False,
    }


def task_geometry() -> dict:
    return {
        "state": "unverified_source_reported_local_approximation",
        "task_kind": "receiver_side_near_end_listening_enhancement",
        "audio_input_expected": True,
        "audio_output_expected": True,
        "sample_rate_hz": None,
        "frame_samples": None,
        "channels": None,
        "lookahead_ms": None,
        "content_delay_documented": False,
        "causality_documented": False,
        "energy_preservation_contract_documented": False,
        "geometry_verified": False,
        "profile_fit_reason": "The candidate is a DSP-style receiver-side audio transform in principle, but no exact licensed implementation, runtime geometry, delay contract, or qualified DSP measurement is present in this package.",
        "dsp_profile_fit": "unverified",
    }


DSP_REQUIREMENTS = (
    ("DSP-01", "Sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control.", "blocked"),
    ("DSP-02", "Gain, response, attack/release where applicable, headroom, delay and numerical behavior.", "blocked"),
    ("DSP-03", "State transitions and interacting nonlinear configurations.", "blocked"),
    ("DSP-04", "Identity/fixed-tilt/DRC controls compared on held-out maskers with equalized target energy.", "blocked"),
    ("DSP-05", "Separate source-reported research, synthetic controls, and missing real/listening/device evidence.", "documented"),
)


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| DSP |")]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": [p for p in PROFILE_PHRASES if len(rows) == 1 and p in rows[0]],
        "all_phrases_present": len(rows) == 1 and all(p in rows[0] for p in PROFILE_PHRASES),
    }


def dsp_profile() -> dict:
    rows = []
    for row_id, requirement, state in DSP_REQUIREMENTS:
        blocked = state == "blocked"
        rows.append({
            "id": row_id,
            "requirement": requirement,
            "status": state,
            "evidence": (
                "No exact licensed implementation, pinned runtime, rights-cleared cohort, or qualified measurement exists in this package; the item cannot be measured or qualified."
                if blocked else
                "This report keeps source-reported research, schema-only declarations, missing real measurements, and sibling DSP references in distinct sections and never pools them."),
            "qualifies": False,
        })
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": rows,
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_results": 0,
        "source_reported_results": 0,
        "qualified_result_present": False,
    }


def matched_evidence() -> dict:
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "candidate_profile_fit": "unverified",
        "matched_cohort_present": False,
        "matched_baseline_present": False,
        "held_out_maskers_present": False,
        "energy_equalized_comparison_present": False,
        "listener_study_present": False,
        "device_timing_present": False,
        "evidence_classes": [
            "source_reported_research_note",
            "inventory_scope",
            "acceptance_profile_scope",
            "missing_exact_artifact",
            "missing_rights_cleared_cohort",
            "separate_dsp_reference",
            "unchanged_v0_contract",
        ],
        "required_separation": "Source-reported research, schema-only declarations, missing real measurements, and sibling DSP/reference packages stay in distinct sections and are never pooled.",
        "synthetic_schema_control_counted_as_result": False,
        "classes_pooled": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed asset declaration
# ---------------------------------------------------------------------------

def accepted_unpopulated_declaration() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "declaration_id": "optfractasii-approximation-unpopulated",
        "candidate": {
            "name": CANDIDATE_NAME,
            "family": "near_end_listening_enhancement",
            "exact_upstream_source": False,
            "local_approximation_only": True,
            "audio_input": True,
            "audio_output": True,
        },
        "source": {
            "declared_present": False,
            "revision": None,
            "license_sha256": None,
            "source_sha256": None,
        },
        "runtime": {
            "declared_present": False,
            "python_version": None,
            "platform": None,
            "device": None,
            "lock_sha256": None,
        },
        "cohort": {
            "declared_present": False,
            "rights_cleared": False,
            "target_speech_sha256": None,
            "masker_sha256": None,
        },
        "rights": {
            "code": False,
            "weights": False,
            "inputs": False,
            "output_use": False,
            "redistribution": False,
            "review_reference": None,
        },
        "disposition": {
            "decision": DECISION,
            "qualifies": False,
        },
    }


ASSET_DECLARATION_REJECTIONS = (
    ("root_not_object", "declaration", "not_object", []),
    ("root_missing_schema_id", "declaration.schema_id", "missing_field", ["schema_id"]),
    ("missing_declaration_id", "declaration.declaration_id", "missing_field", ["declaration_id"]),
    ("extra_top_key", "declaration.extra", "unknown_field", ["__extra__"]),
    ("bad_schema_id", "schema_id", "schema_id_mismatch", ["schema_id_bad"]),
    ("bad_declaration_id", "declaration_id", "invalid_slug", ["declaration_id_bad"]),
    ("wrong_candidate_name", "candidate.name", "candidate_name_mismatch", ["candidate_name"]),
    ("wrong_candidate_family", "candidate.family", "candidate_family_mismatch", ["candidate_family"]),
    ("source_present_true", "source.declared_present", "unverified_claim", ["source_present"]),
    ("source_revision_set", "source.revision", "unverified_claim", ["source_revision"]),
    ("source_digest_set", "source.source_sha256", "unverified_claim", ["source_digest"]),
    ("runtime_present_true", "runtime.declared_present", "unverified_claim", ["runtime_present"]),
    ("runtime_lock_set", "runtime.lock_sha256", "unverified_claim", ["runtime_lock"]),
    ("cohort_present_true", "cohort.declared_present", "unverified_claim", ["cohort_present"]),
    ("cohort_rights_true", "cohort.rights_cleared", "unverified_claim", ["cohort_rights"]),
    ("rights_code_true", "rights.code", "unverified_claim", ["rights_code"]),
    ("rights_inputs_true", "rights.inputs", "unverified_claim", ["rights_inputs"]),
    ("rights_redistribution_true", "rights.redistribution", "unverified_claim", ["rights_redistribution"]),
    ("rights_review_set", "rights.review_reference", "unverified_claim", ["rights_review"]),
    ("qualifies_true", "disposition.qualifies", "unverified_claim", ["qualifies_true"]),
    ("premature_admit", "disposition.decision", "premature_decision", ["premature_admit"]),
    ("missing_source_section", "source.declared_present", "missing_field", ["missing_source"]),
    ("source_not_object", "source", "not_object", ["source_not_object"]),
    ("float_value", "float not allowed in canonical evidence: /cohort/declared_present", "float_not_allowed", ["float_value"]),
)


STRICT_JSON_REJECTIONS = (
    ("duplicate_key", b'{"a":1,"a":2}'),
    ("nan_literal", b'{"a":NaN}'),
    ("infinity_literal", b'{"a":Infinity}'),
    ("negative_infinity_literal", b'{"a":-Infinity}'),
    ("trailing_data", b'{"a":1}x'),
    ("byte_order_mark", b'\xef\xbb\xbf{"a":1}'),
    ("non_object_root", b'[1]'),
    ("empty_input", b''),
    ("unterminated", b'{"a":1'),
)


def _mutate_declaration(case_id: str) -> Any:
    d = accepted_unpopulated_declaration()
    if case_id == "root_missing_schema_id":
        del d["schema_id"]
    elif case_id == "missing_declaration_id":
        del d["declaration_id"]
    elif case_id == "extra_top_key":
        d["extra"] = "x"
    elif case_id == "bad_schema_id":
        d["schema_id"] = "wrong"
    elif case_id == "bad_declaration_id":
        d["declaration_id"] = "Bad Id"
    elif case_id == "wrong_candidate_name":
        d["candidate"]["name"] = "wrong"
    elif case_id == "wrong_candidate_family":
        d["candidate"]["family"] = "wrong"
    elif case_id == "source_present_true":
        d["source"]["declared_present"] = True
    elif case_id == "source_revision_set":
        d["source"]["revision"] = "deadbeef"
    elif case_id == "source_digest_set":
        d["source"]["source_sha256"] = "0" * 64
    elif case_id == "runtime_present_true":
        d["runtime"]["declared_present"] = True
    elif case_id == "runtime_lock_set":
        d["runtime"]["lock_sha256"] = "0" * 64
    elif case_id == "cohort_present_true":
        d["cohort"]["declared_present"] = True
    elif case_id == "cohort_rights_true":
        d["cohort"]["rights_cleared"] = True
    elif case_id == "rights_code_true":
        d["rights"]["code"] = True
    elif case_id == "rights_inputs_true":
        d["rights"]["inputs"] = True
    elif case_id == "rights_redistribution_true":
        d["rights"]["redistribution"] = True
    elif case_id == "rights_review_set":
        d["rights"]["review_reference"] = "review"
    elif case_id == "qualifies_true":
        d["disposition"]["qualifies"] = True
    elif case_id == "premature_admit":
        d["disposition"]["decision"] = "ADMIT"
    elif case_id == "missing_source_section":
        del d["source"]
    elif case_id == "source_not_object":
        d["source"] = []
    elif case_id == "float_value":
        d["cohort"]["declared_present"] = 1.5
    return d


def validate_asset_declaration(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ValueError("not_object:declaration")
    allowed_top = {"schema_id", "declaration_id", "candidate", "source", "runtime", "cohort", "rights", "disposition"}
    for key in value:
        if key not in allowed_top:
            raise ValueError(f"unknown_field:declaration.{key}")
    for key in allowed_top:
        if key not in value:
            raise ValueError(f"missing_field:declaration.{key}")
    if value["schema_id"] != DECLARATION_SCHEMA_ID:
        raise ValueError("schema_id_mismatch:schema_id")
    if not isinstance(value["declaration_id"], str) or not SLUG.fullmatch(value["declaration_id"]):
        raise ValueError("invalid_slug:declaration_id")
    candidate = value["candidate"]
    if not isinstance(candidate, dict):
        raise ValueError("not_object:candidate")
    expected_candidate = accepted_unpopulated_declaration()["candidate"]
    if set(candidate.keys()) != set(expected_candidate.keys()):
        for k in candidate.keys() - set(expected_candidate.keys()):
            raise ValueError(f"unknown_field:candidate.{k}")
        for k in set(expected_candidate.keys()) - set(candidate.keys()):
            raise ValueError(f"missing_field:candidate.{k}")
    for k, v in expected_candidate.items():
        if candidate.get(k) != v:
            code = "candidate_name_mismatch" if k == "name" else "candidate_family_mismatch" if k == "family" else "unverified_claim" if k in {"exact_upstream_source"} else "missing_required_value"
            raise ValueError(f"{code}:candidate.{k}")
    for section, fields in {
        "source": ["declared_present", "revision", "license_sha256", "source_sha256"],
        "runtime": ["declared_present", "python_version", "platform", "device", "lock_sha256"],
        "cohort": ["declared_present", "rights_cleared", "target_speech_sha256", "masker_sha256"],
        "rights": ["code", "weights", "inputs", "output_use", "redistribution", "review_reference"],
        "disposition": ["decision", "qualifies"],
    }.items():
        obj = value[section]
        if not isinstance(obj, dict):
            raise ValueError(f"not_object:{section}")
        if set(obj.keys()) != set(fields):
            for k in obj.keys() - set(fields):
                raise ValueError(f"unknown_field:{section}.{k}")
            for k in set(fields) - set(obj.keys()):
                raise ValueError(f"missing_field:{section}.{k}")
        expected = accepted_unpopulated_declaration()[section]
        for k, v in expected.items():
            if obj.get(k) != v:
                if section == "disposition" and k == "decision":
                    raise ValueError(f"premature_decision:{section}.{k}")
                raise ValueError(f"unverified_claim:{section}.{k}")
    assert_no_float(value)
    return {"accepted": True, "status": "accepted_unpopulated"}


def asset_declaration_summary() -> dict:
    accepted = accepted_unpopulated_declaration()
    accepted_result = validate_asset_declaration(accepted)
    rejections = []
    for case_id, field, code, _ in ASSET_DECLARATION_REJECTIONS:
        try:
            if case_id == "root_not_object":
                validate_asset_declaration([])
            else:
                validate_asset_declaration(_mutate_declaration(case_id))
            rejected = False
            actual = "accepted"
        except Exception as exc:  # noqa: BLE001
            rejected = True
            actual = str(exc)
        rejections.append({"id": case_id, "field": field, "code": code, "rejected": rejected, "detail": actual})
    strict = []
    for case_id, payload in STRICT_JSON_REJECTIONS:
        try:
            parse_strict_json_text(payload)
            rejected = False
        except Exception:  # noqa: BLE001
            rejected = True
        strict.append({"id": case_id, "rejected": rejected})
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "accepted_control": accepted,
        "accepted_control_status": accepted_result["status"],
        "accepted_control_sha256": object_digest(accepted),
        "accepted_control_qualifies": False,
        "presence_claims_rejected": True,
        "rejection_cases": len(rejections),
        "all_rejected": all(r["rejected"] for r in rejections),
        "rejections": [{k: r[k] for k in ("id", "field", "code")} for r in rejections],
        "strict_json_cases": len(strict),
        "strict_json_all_rejected": all(r["rejected"] for r in strict),
        "strict_json_rejections": strict,
    }


# ---------------------------------------------------------------------------
# Blockers / gates / report
# ---------------------------------------------------------------------------

REQUIRED_ARTIFACTS = (
    {"id": "ART-01", "kind": "evidence_register_and_policy_boundary", "present": True, "blocked": False, "verified": True, "bytes": None, "revision": None, "sha256": None, "requirement": "Pinned research note, inventory row, DSP profile, and unchanged SDK boundary files."},
    {"id": "ART-02", "kind": "exact_upstream_source_snapshot", "present": False, "blocked": True, "verified": False, "bytes": None, "revision": None, "sha256": None, "requirement": "Exact upstream OptFractASII source or faithful local reproduction recipe at immutable revision with license/notice and per-file hashes."},
    {"id": "ART-03", "kind": "pinned_runtime_and_geometry", "present": False, "blocked": True, "verified": False, "bytes": None, "revision": None, "sha256": None, "requirement": "Pinned offline runtime, exact sample rate/frame/channel/lookahead/delay/energy contract, and deterministic install/run manifest."},
    {"id": "ART-04", "kind": "rights_cleared_cohort", "present": False, "blocked": True, "verified": False, "bytes": None, "revision": None, "sha256": None, "requirement": "Rights-cleared target speech, independent masker corpus, consent/hearing-profile/output-use decisions, and immutable manifests."},
    {"id": "ART-05", "kind": "matched_dsp_measurements", "present": False, "blocked": True, "verified": False, "bytes": None, "revision": None, "sha256": None, "requirement": "DSP-profile measurements: sweeps/steps/impulses/silence/clean speech, gain/response/headroom/delay/numerical behavior, state/nonlinear interactions, and held-out masker controls with energy equalization."},
    {"id": "ART-06", "kind": "listener_device_release_evidence", "present": False, "blocked": True, "verified": False, "bytes": None, "revision": None, "sha256": None, "requirement": "Authorized listening or labeled screen, device timing/CPU/deadline/memory, and independent OFF-by-default release review."},
)

EXACT_BLOCKERS = (
    {"id": "BLK-01", "artifact_id": "ART-02", "title": "No exact licensed upstream artifact", "status": "open", "linked_gates": ["RG-01", "RG-02"], "qualifies": False, "statement": "No exact immutable OptFractASII upstream source snapshot, license text, notice bundle, algorithm identifier, filterbank/importance table, or faithful reproduction recipe is present locally.", "required_action": "Supply exact immutable upstream artifact or faithful reproduction recipe with reviewed license/notice and per-file hashes.", "reopen_condition": "Only a caller-supplied exact artifact with verified identity, terms, and independent review can reopen this blocker."},
    {"id": "BLK-02", "artifact_id": "ART-03", "title": "No pinned runtime or geometry", "status": "open", "linked_gates": ["RG-03"], "qualifies": False, "statement": "No pinned offline runtime, sample-rate/frame/channel/lookahead/content-delay/energy contract, or deterministic install/run manifest is present.", "required_action": "Provide a locked offline runtime and exact task geometry manifest with deterministic execution evidence.", "reopen_condition": "Reopen only with pinned runtime hashes, geometry manifest, and reproducible execution logs."},
    {"id": "BLK-03", "artifact_id": "ART-04", "title": "No rights-cleared cohort", "status": "open", "linked_gates": ["RG-04"], "qualifies": False, "statement": "No rights-cleared target speech, independent masker corpus, consent/hearing-profile/output-use permission, or immutable cohort manifest is present.", "required_action": "Supply rights-cleared cohort manifests and written permissions for evaluation and derived outputs.", "reopen_condition": "Reopen only with reviewed rights/consent manifests and immutable cohort hashes."},
    {"id": "BLK-04", "artifact_id": "ART-05", "title": "No qualified DSP measurements", "status": "open", "linked_gates": ["RG-05", "RG-06"], "qualifies": False, "statement": "No DSP-profile measurement run exists for the exact candidate: no sweeps/steps/impulses/silence/clean-speech controls, no gain/response/headroom/delay/numerical behavior, no state/nonlinear interaction evidence, and no held-out masker comparison with equalized energy.", "required_action": "Run DSP profile on exact pinned artifact/runtime/cohort with identity, fixed tilt, and DRC controls and equalized energy.", "reopen_condition": "Reopen only with reproducible DSP measurements tied to pinned artifacts and cohort."},
    {"id": "BLK-05", "artifact_id": "ART-06", "title": "No listener/device/release evidence", "status": "open", "linked_gates": ["RG-07", "RG-08"], "qualifies": False, "statement": "No authorized listening or labeled screen, no device timing/CPU/deadline/memory measurement, and no independent OFF-by-default release review exists.", "required_action": "Provide authorized listening/screen, device measurements, and independent OFF-by-default review after prior gates clear.", "reopen_condition": "Reopen only with reviewed listener/device evidence and independent release review."},
)

RELEASE_GATES = (
    ("exact_artifact_identity_and_license", "Supply exact immutable upstream artifact or faithful reproduction recipe with reviewed license/notice and per-file hashes."),
    ("source_reported_note_not_promoted", "Keep the pinned research note source-reported; do not promote it to qualification without exact artifact/runtime/cohort evidence."),
    ("pinned_runtime_and_geometry", "Provide locked offline runtime and exact geometry/delay/energy contract with deterministic execution logs."),
    ("rights_cleared_cohort", "Provide rights-cleared target/masker cohort, consent/hearing-profile/output-use decisions, and immutable manifests."),
    ("dsp_profile_measurements", "Run DSP profile measurements with required controls and equalized energy on pinned artifacts."),
    ("held_out_masker_comparison", "Compare identity, fixed tilt, and DRC/related controls on held-out maskers with independent review."),
    ("listener_device_timing", "Provide authorized listening/labeled screen and device timing/CPU/deadline/memory evidence."),
    ("independent_release_review", "Obtain independent OFF-by-default review after all prior gates clear; keep public surface unchanged until then."),
)


def release_gates() -> list[dict]:
    gates = []
    for index, (title, reopen) in enumerate(RELEASE_GATES, 1):
        gates.append({
            "id": f"RG-{index:02d}",
            "title": title,
            "status": "blocked",
            "qualifies": False,
            "statement": "No exact OptFractASII artifact, runtime, right, matched measurement, or review satisfies this requirement.",
            "reopen_condition": reopen,
            "linked_row": {
                "id": TASK,
                "title": TASK_TITLE,
                "component": COMPONENT_ID,
                "mode": MODE,
                "repository": REPOSITORY,
                "depends_on": list(DEPENDS_ON),
            },
        })
    return gates


def qualification() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "not_qualified": True,
        "readiness": "incomplete",
        "reason": "Exact licensed artifact, pinned runtime/geometry, rights-cleared cohort, DSP measurements, listener/device evidence, and independent review are absent.",
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "synthetic_result_present": False,
        "source_reported_result_present": True,
        "source_reported_result_qualifies": False,
        "release_claim": False,
        "benchmark_claim": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "depends_on": list(DEPENDS_ON),
        "linked_row": board_row_projection(),
        "linked_rows": list(linked_rows()),
        "linked_row_sha256": board_row_digest(),
        "linked_rows_sha256": linked_rows_digest(),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "absence_summary": absence_summary(),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "dsp_profile": dsp_profile(),
        "matched_evidence": matched_evidence(),
        "asset_declaration_schema": asset_declaration_summary(),
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "release_gates": release_gates(),
        "qualification": qualification(),
        "non_claims": list(NON_CLAIMS),
        "historical_evidence": list(HISTORICAL_EVIDENCE),
        "peer_separation": list(PEER_SEPARATION),
        "exact_scope": {
            "task_prefix": TASK_PREFIX,
            "only_task_directory_written": True,
            "board_or_handoff_changed": False,
            "provider_files_changed": False,
            "descriptor_or_registry_changed": False,
            "contracts_header_changed": False,
            "cmake_or_ci_changed": False,
            "default_selection_changed": False,
            "candidate_code_weights_or_audio_committed": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    text, digest = canonical_text(contract), sha256_bytes(canonical_bytes(contract))
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "depends_on": list(DEPENDS_ON),
        "linked_row": contract["linked_row"],
        "linked_rows": contract["linked_rows"],
        "linked_row_sha256": contract["linked_row_sha256"],
        "linked_rows_sha256": contract["linked_rows_sha256"],
        "boundary": {
            "linked_row_identity_only": True,
            "mutable_board_fields_gate": False,
            "excluded_mutable_fields": ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority"],
            "board_or_handoff_changed": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "installed_v0_behavior_change": False,
            "candidate_code_vendored": False,
            "weights_vendored": False,
            "audio_added": False,
            "runtime_imported": False,
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "source_pin_rows": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pin_rows": pin_rows(BOUNDARY_PINS, SDK_ROOT),
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "absence_evidence": absence_summary(),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "dsp_profile": dsp_profile(),
        "matched_evidence": matched_evidence(),
        "asset_declaration": asset_declaration_summary(),
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "release_gates": release_gates(),
        "qualification": qualification(),
        "non_claims": list(NON_CLAIMS),
        "historical_evidence": list(HISTORICAL_EVIDENCE),
        "peer_separation": list(PEER_SEPARATION),
        "exact_scope": contract["exact_scope"],
        "reproduction": {
            "byte_identical": True,
            "canonical_json": True,
            "interpreter": REQUIRED_INTERPRETER,
            "repeat_count": 3,
            "report_sha256_sidecar": "report.json.sha256",
            "sorted_keys": True,
            "trailing_newline": False,
        },
        "disposition": {
            "decision": DECISION,
            "status": STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "proposal_only": True,
            "incomplete": True,
            "not_qualified": True,
            "result_promoted": False,
            "candidate_artifact_present": False,
            "runtime_present": False,
            "rights_cleared_input_present": False,
            "output_present": False,
            "release_claim": False,
        },
        "contract_sha256": digest,
    }
    return report


if __name__ == "__main__":
    print(canonical_report()[0])
