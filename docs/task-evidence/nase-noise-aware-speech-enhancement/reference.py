# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-NASE.

Standard library only. The catalogued candidate is NASE (Noise-aware Speech
Enhancement): an offline diffusion speech enhancer conditioned by learned
noise-aware BEATs embeddings. The pinned records name an official repository
and a pretrained VoiceBank+DEMAND checkpoint, but no source snapshot, weight
byte, BEATs encoder, runtime, licence text, rights-cleared cohort or local
result is present anywhere probed.

This module pins the evidence that does exist, proves a fixed absence
inventory, validates a fail-closed caller-supplied asset declaration without
resolving, importing, loading or executing anything, and builds canonical
DEFER bytes. It never runs diffusion, enhances audio, synthesises a waveform,
opens media, performs listening, times a device or produces a benchmark result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT"
TASK_TITLE = "NASE (Noise-aware Speech Enhancement)"
COMPONENT_ID = "nase-noise-aware-speech-enhancement"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/nase-noise-aware-speech-enhancement/ only"
TASK_PREFIX = "docs/task-evidence/nase-noise-aware-speech-enhancement/"
CONTRACT_ID = "audio-sdk/nase-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/nase-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/nase-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/nase-caller-asset/0.1"
BASE_COMMIT = "e3e3deccb3c852bce8255305700be219ccceadb8"
BRANCH = "swarm/SDK-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT"
OWNER = "agent-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT"
REVIEWER = "reviewer-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
SOURCE_REPOSITORY = "https://github.com/YUCHEN005/NASE"
CANDIDATE_NAME = "NASE (Noise-aware Speech Enhancement)"
CANDIDATE_FAMILY = "diffusion_noise_aware_beats_conditioning"
TASK_GEOMETRY_STATE = "unverified_offline_diffusion_geometry"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PACKAGE = re.compile(r"^[A-Za-z0-9_.+-]+==[A-Za-z0-9_.+-]+$")
PYTHON = re.compile(r"^3\.12\.[0-9]+$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml root without a recursive walk or network use."""
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


AUDIO_ROOT = _find_audio_root()
SDK_ROOT = WORKTREE

# Read-only inputs. `source:` paths are workspace-relative; `sdk:` paths are
# SDK-worktree-relative. The mutable shared board is never pinned.
SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/evidence/pilot-discovery-20261027/source.txt":
        "3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/"
    "candidate_accounting.csv":
        "7261b99e06460b612dcbebeec3859de60a7040a18444fc19a637ebddc4a58e3c",
    "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/"
    "manifest.json":
        "e6a3e7c07504dd7919fc6314732c1db2e8bd2017c77a94aca1dc457737208440",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
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
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

INVENTORY_REL = "audio-benchmark-platform/plan/INVENTORY.json"
INVENTORY_MD_REL = "audio-benchmark-platform/plan/INVENTORY.md"
ASSET_REGISTRY_REL = "research/noise_suppression_assets_20261027.json"
ACCOUNTING_REL = (
    "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/"
    "candidate_accounting.csv")

EVIDENCE_SNIPPETS = (
    {
        "id": "SNP-01",
        "path": "research/noise_suppression_candidate_census.md",
        "line": 71,
        "contains": (
            "NASE (Noise-aware Speech Enhancement)",
            "Diffusion model conditioned by learned noise-aware BEATs embeddings",
            "offline quality reference",
            "pretrained VoiceBank+DEMAND checkpoint",
        ),
    },
    {
        "id": "SNP-02",
        "path": "research/evidence/pilot-discovery-20261027/source.txt",
        "line": 94,
        "contains": (
            "Twenty-third candidate search pass found NASE",
            "pretrained VoiceBank-DEMAND checkpoint",
            "learned noise-aware BEATs conditioning model",
            "https://github.com/YUCHEN005/NASE",
        ),
    },
    {
        "id": "SNP-03",
        "path": ACCOUNTING_REL,
        "line": 57,
        "contains": (
            "candidate-nase",
            "blocked",
            "located_unverified",
        ),
    },
    {
        "id": "SNP-04",
        "path": INVENTORY_MD_REL,
        "line": 189,
        "contains": (
            "NASE (Noise-aware Speech Enhancement)",
            "SDK-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT",
        ),
    },
)

LOCAL_FILES = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256",
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

EXPECTED_DIR_FILES = frozenset(LOCAL_FILES)

FORBIDDEN_SUFFIXES = frozenset((
    ".7z", ".a", ".bin", ".ckpt", ".dll", ".dylib", ".flac", ".gz", ".h5",
    ".mp3", ".npy", ".npz", ".o", ".ogg", ".onnx", ".pth", ".pt",
    ".safetensors", ".so", ".tar", ".tflite", ".tgz", ".wav", ".whl", ".zip",
))

SOURCE_ARTIFACT_FILES = tuple(
    name for name in LOCAL_FILES if name not in ("README.md", "SOURCES.sha256"))


# ---------------------------------------------------------------------------
# Canonical bytes and strict JSON.
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
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


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


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
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
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned.
# ---------------------------------------------------------------------------


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError("board_row_missing_fields:" + ",".join(missing))
    component = row.get("component")
    if require_component:
        if component != COMPONENT_ID:
            raise ValueError("board_component_mismatch:" + str(component))
    elif component is not None and not isinstance(component, str):
        raise ValueError("board_component_not_string")
    depends_on = row["depends_on"]
    if not isinstance(depends_on, list) or \
            any(not isinstance(item, str) for item in depends_on):
        raise ValueError("board_depends_on_not_string_list")
    return {
        "component": component,
        "depends_on": list(depends_on),
        "id": row["id"],
        "mode": row["mode"],
        "repository": row["repository"],
        "title": row["title"],
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    target = path or (AUDIO_ROOT / BOARD_TASK_ROW)
    document = read_strict_json(target)
    tasks = document.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("board_tasks_not_list")
    for row in tasks:
        if not isinstance(row, dict):
            raise ValueError("board_row_not_object")
    return tasks


def board_row_projection(path: Path | None = None) -> dict:
    tasks = _board_tasks(path)
    matches = [row for row in tasks if row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_task_row_count:" + str(len(matches)))
    return _project(matches[0], require_component=True)


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    tasks = _board_tasks(path)
    by_id = {row.get("id"): row for row in tasks}
    rows: list[dict] = []
    for identifier in LINKED_ROW_IDS:
        row = by_id.get(identifier)
        if row is None:
            raise ValueError("board_linked_row_missing:" + identifier)
        rows.append(_project(row, require_component=(identifier == TASK)))
    return tuple(rows)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(board_row_projection() if projection is None
                         else projection)


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(linked_rows() if rows is None else rows))


# ---------------------------------------------------------------------------
# Git scope helpers.
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if HEX40.match(value) else None


def scope_base(worktree: Path,
               refs: Iterable[str] = ("origin/main", "main")) -> str | None:
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        if result.returncode == 0:
            value = result.stdout.strip()
            if HEX40.match(value):
                return value
    return None


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", base, "HEAD")
    if result.returncode != 0:
        raise ValueError("scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line.strip()]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    return sorted(path for path in paths if not path.startswith(prefix))


# ---------------------------------------------------------------------------
# Fixed absence probes. No recursive walk.
# ---------------------------------------------------------------------------


def _probe(path: Path, label: str, kind: str, display: str) -> dict:
    return {
        "kind": kind,
        "label": label,
        "path": display,
        "present": path.exists(),
        "searched_home_cache": kind == "home",
        "searched_sdk_worktree": kind == "worktree",
        "searched_workspace": kind == "workspace",
    }


def workspace_probes() -> list[dict]:
    root = AUDIO_ROOT
    return [
        _probe(root / "data/checkouts/NASE", "workspace-checkout-upper",
               "workspace", "data/checkouts/NASE"),
        _probe(root / "data/checkouts/nase", "workspace-checkout-lower",
               "workspace", "data/checkouts/nase"),
        _probe(root / "data/models/nase", "workspace-model-lower", "workspace",
               "data/models/nase"),
        _probe(root / "data/models/NASE", "workspace-model-upper", "workspace",
               "data/models/NASE"),
        _probe(root / "third_party/NASE", "workspace-third-party", "workspace",
               "third_party/NASE"),
        _probe(root / "research/nase", "workspace-research", "workspace",
               "research/nase"),
        _probe(root / "research/vendor/NASE", "workspace-research-vendor",
               "workspace", "research/vendor/NASE"),
    ]


def worktree_probes() -> list[dict]:
    root = HERE
    names = (
        ("source", "worktree-source"),
        ("checkpoints", "worktree-checkpoints"),
        ("weights", "worktree-weights"),
        ("runtime", "worktree-runtime"),
        ("beats", "worktree-beats"),
    )
    return [
        _probe(root / name, label, "worktree", TASK_PREFIX + name)
        for name, label in names
    ]


def home_probes() -> list[dict]:
    home = Path.home()
    names = (
        (".cache/huggingface/hub/models--YUCHEN005--NASE", "home-hf-nase"),
        (".cache/huggingface/hub/models--YUCHEN005--NASE-beats",
         "home-hf-nase-beats"),
        (".cache/torch/hub/checkpoints/nase.pt", "home-torch-nase-pt"),
        (".cache/torch/hub/checkpoints/nase.ckpt", "home-torch-nase-ckpt"),
        (".cache/torch/hub/checkpoints/beats.pt", "home-torch-beats"),
        ("NASE", "home-nase-upper"),
        ("nase", "home-nase-lower"),
    )
    return [
        _probe(home / name, label, "home", "~/" + name)
        for name, label in names
    ]


def all_probes() -> list[dict]:
    return workspace_probes() + worktree_probes() + home_probes()


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = all_probes() if probes is None else probes
    present = sorted(row["label"] for row in rows if row["present"])
    return {
        "all_absent": not present,
        "home_probe_count": sum(
            1 for row in rows if row["kind"] == "home"),
        "present": present,
        "probe_count": len(rows),
        "probes": rows,
        "recursive_walk": False,
        "worktree_probe_count": sum(
            1 for row in rows if row["kind"] == "worktree"),
        "workspace_probe_count": sum(
            1 for row in rows if row["kind"] == "workspace"),
    }


# ---------------------------------------------------------------------------
# Source, boundary and README pin handling.
# ---------------------------------------------------------------------------


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows: list[dict] = []
    for relative, expected in sorted(pins.items()):
        path = root / relative
        present = path.is_file()
        observed = sha256_file(path) if present else None
        rows.append({
            "expected_sha256": expected,
            "path": relative,
            "present": present,
            "sha256": observed,
            "matches": present and observed == expected,
        })
    return rows


def _source_manifest_paths() -> list[str]:
    return sorted(list(SOURCE_PINS) + list(BOUNDARY_PINS) + list(LOCAL_FILES))


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-NASE task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
    ]
    for relative, digest in sorted(SOURCE_PINS.items()):
        lines.append("%s  source:%s" % (digest, relative))
    for relative, digest in sorted(BOUNDARY_PINS.items()):
        lines.append("%s  sdk:%s" % (digest, relative))
    for name in LOCAL_FILES:
        if name == "SOURCES.sha256":
            continue
        digest = sha256_file(HERE / name)
        lines.append("%s  %s%s" % (digest, TASK_PREFIX, name))
    return ("\n".join(lines) + "\n").encode("ascii")


TABLE_SECTIONS = ("source", "boundary", "artifacts")


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + relative for relative in SOURCE_PINS},
        "boundary": {"sdk:" + relative for relative in BOUNDARY_PINS},
        "artifacts": set(SOURCE_ARTIFACT_FILES),
    }


def _section_bounds(text: str, section: str) -> tuple[int, int]:
    start_marker = "<!-- DIGEST_TABLE_%s_START -->" % section.upper()
    end_marker = "<!-- DIGEST_TABLE_%s_END -->" % section.upper()
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError("digest_table_marker_count:" + section)
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker)
    if end < start:
        raise ValueError("digest_table_order:" + section)
    return start, end


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    parsed: dict[str, list[tuple[str, str]]] = {}
    for section in TABLE_SECTIONS:
        start, end = _section_bounds(text, section)
        block = text[start:end]
        rows: list[tuple[str, str]] = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            key = cells[0].strip("`")
            digest = cells[1].strip("`")
            if HEX64.match(digest):
                rows.append((key, digest))
        parsed[section] = rows
    return parsed


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    counts: dict[str, int] = {}
    for section in TABLE_SECTIONS:
        rows = parsed[section]
        keys = [key for key, _ in rows]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate_readme_row:" + section)
        if set(keys) != expected[section]:
            raise ValueError("readme_row_set_mismatch:" + section)
        for key, digest in rows:
            if section == "source":
                observed = sha256_file(AUDIO_ROOT / key[len("source:"):])
            elif section == "boundary":
                observed = sha256_file(WORKTREE / key[len("sdk:"):])
            else:
                observed = sha256_file(HERE / key)
            if observed != digest:
                raise ValueError("readme_digest_mismatch:" + key)
        counts[section] = len(rows)
    return counts


def render_digest_table(section: str) -> str:
    lines = ["", ]
    if section == "source":
        lines.append("| Source pin | SHA-256 |")
        lines.append("| --- | --- |")
        for relative in sorted(SOURCE_PINS):
            digest = sha256_file(AUDIO_ROOT / relative)
            lines.append("| `source:%s` | `%s` |" % (relative, digest))
    elif section == "boundary":
        lines.append("| Boundary pin | SHA-256 |")
        lines.append("| --- | --- |")
        for relative in sorted(BOUNDARY_PINS):
            digest = sha256_file(WORKTREE / relative)
            lines.append("| `sdk:%s` | `%s` |" % (relative, digest))
    elif section == "artifacts":
        lines.append("| Path | SHA-256 | Bytes |")
        lines.append("| --- | --- | ---: |")
        for name in SOURCE_ARTIFACT_FILES:
            path = HERE / name
            lines.append("| `%s` | `%s` | %d |"
                         % (name, sha256_file(path), path.stat().st_size))
    else:
        raise ValueError("unknown_table_section:" + section)
    lines.append("")
    return "\n".join(lines)


def update_readme_table(text: str, section: str) -> str:
    start, end = _section_bounds(text, section)
    return text[:start] + render_digest_table(section) + text[end:]


def update_readme_tables(text: str) -> str:
    for section in TABLE_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Pinned evidence extraction.
# ---------------------------------------------------------------------------


def _read_text(relative: str) -> str:
    return (AUDIO_ROOT / relative).read_text(encoding="utf-8")


def evidence_presence() -> dict:
    snippets: list[dict] = []
    for snippet in EVIDENCE_SNIPPETS:
        text = _read_text(snippet["path"])
        lines = text.splitlines()
        number = snippet["line"]
        if number < 1 or number > len(lines):
            raise ValueError("snippet_line_out_of_range:" + snippet["id"])
        line = lines[number - 1]
        missing = [needle for needle in snippet["contains"] if needle not in line]
        if missing:
            raise ValueError("snippet_missing:" + snippet["id"] + ":" +
                             "|".join(missing))
        snippets.append({
            "contains": list(snippet["contains"]),
            "id": snippet["id"],
            "line": number,
            "path": snippet["path"],
        })
    return {"snippet_count": len(snippets), "snippets": snippets}


def inventory_record() -> dict:
    document = read_strict_json(AUDIO_ROOT / INVENTORY_REL)
    found: list[dict] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("id") == COMPONENT_ID:
                found.append(value)
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(document)
    if len(found) != 1:
        raise ValueError("inventory_record_count:" + str(len(found)))
    record = found[0]
    expected = {
        "area": "Enhancement",
        "disposition": "sdk-model",
        "evidence_status": "considered",
        "name": CANDIDATE_NAME,
        "repository": REPOSITORY,
        "task": TASK,
        "verification_profile": PROFILE,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ValueError("inventory_field_mismatch:" + key)
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or len(evidence) != 1:
        raise ValueError("inventory_evidence_count")
    entry = evidence[0]
    if entry.get("path") != "research/noise_suppression_candidate_census.md" \
            or entry.get("line") != 71:
        raise ValueError("inventory_evidence_link_mismatch")
    return {
        "aliases": list(record.get("aliases") or []),
        "area": record["area"],
        "disposition": record["disposition"],
        "evidence_line": entry["line"],
        "evidence_path": entry["path"],
        "evidence_status": record["evidence_status"],
        "finding": entry.get("finding"),
        "id": record["id"],
        "name": record["name"],
        "repository": record["repository"],
        "task": record["task"],
        "verification_profile": record["verification_profile"],
    }


def profile_row_check() -> dict:
    text = _read_text(PROFILE_SOURCE_REL)
    rows = [line for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        raise ValueError("profile_row_count:" + str(len(rows)))
    row = rows[0]
    present = [phrase for phrase in PROFILE_PHRASES if phrase in row]
    return {
        "all_phrases_present": len(present) == len(PROFILE_PHRASES),
        "path": PROFILE_SOURCE_REL,
        "phrases_present": present,
        "row_count": len(rows),
        "unique_row": True,
    }


def asset_registry() -> dict:
    document = read_strict_json(AUDIO_ROOT / ASSET_REGISTRY_REL)
    candidates = document.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("asset_registry_candidates_missing")
    identifiers: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(
                candidate.get("id"), str):
            raise ValueError("asset_registry_candidate_malformed")
        identifiers.append(candidate["id"])
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("asset_registry_duplicate_id")
    nase = sorted(item for item in identifiers if "nase" in item.lower())
    return {
        "candidate_count": len(identifiers),
        "candidate_ids_sha256": object_digest(sorted(identifiers)),
        "nase_candidate_ids": nase,
        "nase_entry_present": bool(nase),
        "note": (
            "The register contains separate denoising assets and no NASE "
            "source, checkpoint, BEATs encoder, revision, byte count, "
            "SHA-256 or terms entry."),
        "path": ASSET_REGISTRY_REL,
    }


def accounting_row() -> dict:
    text = _read_text(ACCOUNTING_REL)
    lines = text.splitlines()
    header = lines[0].split(",")
    matches = [line for line in lines[1:] if line.startswith("candidate-nase,")]
    if len(matches) != 1:
        raise ValueError("accounting_nase_row_count:" + str(len(matches)))
    # The reason field is quoted and contains commas, so only the fixed
    # columns before it and the two trailing columns are read positionally.
    row = matches[0]
    prefix = row.split('"', 1)[0].rstrip(",").split(",")
    suffix = row.rsplit('"', 1)[1].lstrip(",").split(",")
    if len(prefix) != 4 or len(suffix) != 2:
        raise ValueError("accounting_nase_row_shape")
    return {
        "code": suffix[0],
        "eligibility": prefix[3],
        "header": header,
        "id": prefix[0],
        "method": prefix[2],
        "reason": row.split('"', 1)[1].rsplit('"', 1)[0],
        "revision": int(prefix[1]),
        "weights": suffix[1],
    }


# ---------------------------------------------------------------------------
# Report blocks.
# ---------------------------------------------------------------------------


def source_reported_identity() -> dict:
    return {
        "admitted_as_result": False,
        "beats_checkpoint_identity": None,
        "checkpoint_bytes": None,
        "checkpoint_file": None,
        "checkpoint_sha256": None,
        "checkpoint_variant": None,
        "conditioning_encoder": "learned noise-aware BEATs embeddings",
        "locally_present": False,
        "model_repository": SOURCE_REPOSITORY,
        "model_revision": None,
        "note": (
            "The census and discovery log name the repository, a pretrained "
            "VoiceBank+DEMAND checkpoint, test samples and metric scripts. "
            "No commit, file name, byte count, SHA-256, BEATs checkpoint, "
            "licence text, model card or metric table is recorded in the "
            "pinned evidence."),
        "paper_url": None,
        "qualifies": False,
        "reported_approach": (
            "diffusion model conditioned by learned noise-aware BEATs "
            "embeddings"),
        "reported_channels": 1,
        "reported_domain": "VoiceBank+DEMAND",
        "reported_metrics": None,
        "reported_mode": "offline_quality_reference_non_streaming_lead",
        "reported_sample_rate_hz": None,
        "reported_task": "single-channel speech enhancement / noise "
                         "suppression",
        "source_license_reported": None,
        "source_license_status": "not_recorded",
        "source_revision": None,
        "source_repository": SOURCE_REPOSITORY,
        "source_repository_source": (
            "research/noise_suppression_candidate_census.md:71 and "
            "research/evidence/pilot-discovery-20261027/source.txt:94"),
        "status": "source_reported_not_measured_here",
    }


def task_geometry() -> dict:
    return {
        "conditioning_encoder": "BEATs (learned noise-aware conditioning)",
        "conditioning_layout": None,
        "diffusion_noise_schedule": None,
        "diffusion_sampler_steps": None,
        "exact_geometry_verified": False,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "normalization": None,
        "output_length": None,
        "pacing_policy": None,
        "reported_approach": (
            "diffusion model conditioned by learned noise-aware BEATs "
            "embeddings"),
        "reported_channels": 1,
        "reported_domain": "VoiceBank+DEMAND",
        "reported_mode": "offline_quality_reference_non_streaming_lead",
        "reported_sample_rate_hz": None,
        "reported_task": "single-channel speech enhancement / noise "
                         "suppression",
        "sdk_v0_adapter_mapping_present": False,
        "sdk_v0_mono_matches_reported": True,
        "sdk_v0_rate_matches_reported": None,
        "state_reset_policy": None,
        "stft_window_samples": None,
    }


def enhancement_profile() -> dict:
    rows = [
        {
            "evidence": (
                "No identity/noisy control or task-matched baseline exists on "
                "exact NASE assets; no diffusion comparator is run."),
            "id": "ENH-01",
            "requirement": "Identity/noisy control and an established "
                           "task-matched baseline.",
            "status": "blocked",
        },
        {
            "evidence": "No rights-cleared 16 kHz paired cohort and no score.",
            "id": "ENH-02",
            "requirement": "Paired SI-SDR and STOI where permitted clean "
                           "references exist.",
            "status": "blocked",
        },
        {
            "evidence": (
                "No preservation, peak, clipping or nonfinite record; "
                "diffusion output is not produced or inspected."),
            "id": "ENH-03",
            "requirement": "Clean-speech preservation, peaks and invalid "
                           "outputs.",
            "status": "blocked",
        },
        {
            "evidence": "No screen, listening protocol, panel or permission.",
            "id": "ENH-04",
            "requirement": "Separately labeled predictive screen or "
                           "authorized listening.",
            "status": "blocked",
        },
        {
            "evidence": (
                "No runtime, alignment, state, memory, sampler timing or "
                "measured content delay."),
            "id": "ENH-05",
            "requirement": "Alignment, state, memory and measured "
                           "content/availability timing.",
            "status": "blocked",
        },
        {
            "evidence": (
                "The evidence records an offline diffusion approach but no "
                "rate, channels, STFT window, hop, sampler steps, noise "
                "schedule, BEATs conditioning layout, padding, output length "
                "or normalization contract."),
            "id": "ENH-06",
            "requirement": "Offline diffusion geometry and BEATs conditioning "
                           "contract, including sample rate, channels, STFT, "
                           "sampler, padding, output length and no streaming "
                           "lookahead.",
            "status": "blocked",
        },
        {
            "evidence": "No cohort or stratum definition exists.",
            "id": "ENH-07",
            "requirement": "Quiet/active speech, idle noise and onset/offset "
                           "strata.",
            "status": "blocked",
        },
        {
            "evidence": (
                "The package records absence and separation only; the census "
                "is a source lead and no result of any class is promoted."),
            "id": "ENH-08",
            "requirement": "Keep paired, unpaired, synthetic, human and "
                           "source-reported evidence separate.",
            "status": "documented",
        },
    ]
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    documented = sum(1 for row in rows if row["status"] == "documented")
    return {
        "clean_speech_preservation_present": False,
        "identity_control_present": False,
        "listening_present": False,
        "paired_si_sdr_stoi": "blocked_no_rights_cleared_16khz_clean_references",
        "peaks_and_invalid_present": False,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": rows,
        "rights_independent_gates_present": False,
        "row_summary": {
            "blocked_count": blocked,
            "documented_count": documented,
            "profile_satisfied": False,
            "real_result_count": 0,
            "requirement_count": len(rows),
        },
        "task_matched_baseline_present": False,
        "timing_present": False,
    }


def boundary_block() -> dict:
    return {
        "adapter_json_added": False,
        "audio_added": False,
        "corpus_added": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "native_engine_built": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "runtime_imported": False,
        "shared_build_or_ci_change": False,
        "weights_vendored": False,
    }


def scope_block() -> dict:
    return {
        "benchmark_claim": False,
        "board_or_handoff_change": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "device_timing": False,
        "listening": False,
        "model_executed": False,
        "network_access": False,
        "peer_evidence_inherited": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "public_default": False,
        "real_audio": False,
        "real_corpus": False,
        "release_claim": False,
        "runtime_invoked": False,
        "shared_build_or_ci_change": False,
        "source_vendored": False,
        "task_local_only": True,
        "weights_downloaded": False,
        "weights_vendored": False,
    }


def exact_scope_block() -> dict:
    return {
        "adapter_files_changed": False,
        "board_or_handoff_changed": False,
        "cmake_or_ci_changed": False,
        "contracts_header_changed": False,
        "default_selection_changed": False,
        "descriptor_or_registry_changed": False,
        "only_task_directory_written": True,
        "provider_files_changed": False,
        "task_prefix": TASK_PREFIX,
        "weights_or_audio_committed": False,
        "write_scope": WRITE_SCOPE,
    }


def public_v0_geometry() -> dict:
    return {
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "nase_mapping_present": False,
        "preserved": True,
        "sample_format": "f32",
        "sample_rate_hz": 16000,
    }


def disposition_block() -> dict:
    return {
        "adapter_present": False,
        "checkpoint_identity_recorded_only": False,
        "checkpoint_present_locally": False,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "incomplete": True,
        "output_present": False,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "result_promoted": False,
        "rights_cleared_cohort_present": False,
        "runtime_present": False,
        "source_present": False,
        "status": STATUS,
        "summary": (
            "NASE is an offline diffusion enhancer conditioned by learned "
            "noise-aware BEATs embeddings. The pinned census and discovery "
            "log name an official repository, a pretrained VoiceBank+DEMAND "
            "checkpoint, test samples and metric scripts, but no immutable "
            "revision, checkpoint or BEATs identity, runtime, diffusion "
            "geometry, rights-cleared cohort or local result is present."),
        "task_mode": MODE,
    }


def required_artifacts() -> list[dict]:
    items = (
        ("ART-01", "source_snapshot",
         "The YUCHEN005/NASE source at an immutable 40-hex commit with "
         "reviewed licence text, notice, per-file SHA-256 and a map from the "
         "model, diffusion sampler, metric scripts and test samples to "
         "source files."),
        ("ART-02", "checkpoint_bundle",
         "The exact pretrained VoiceBank+DEMAND NASE checkpoint at immutable "
         "identity with file name, byte count, SHA-256, tensor schema, "
         "inference configuration and checkpoint-specific terms."),
        ("ART-03", "conditioning_encoder_bundle",
         "The exact BEATs conditioning encoder checkpoint and its feature "
         "extraction configuration, at immutable identity with file name, "
         "byte count, SHA-256, tensor schema and separate terms."),
        ("ART-04", "runtime_lock",
         "A locked offline runtime with exact interpreter, framework and "
         "package versions, byte counts, SHA-256 values, CPU/MPS device, "
         "determinism and seed policy and a recorded supported platform."),
        ("ART-05", "rights_bundle",
         "Reviewed source, NASE checkpoint, BEATs encoder, training-data and "
         "VoiceBank+DEMAND terms; corpus and clean-reference permission; "
         "output use, redistribution and attribution."),
        ("ART-06", "offline_diffusion_geometry",
         "Frozen offline whole-utterance contract: sample rate, channels, "
         "STFT window and hop, sampler steps and noise schedule, BEATs "
         "conditioning layout, padding, output length, normalization, no "
         "streaming lookahead and fresh state per call."),
        ("ART-07", "rights_cleared_cohort_and_results",
         "A frozen rights-cleared 16 kHz mono cohort with paired clean "
         "references where permitted, quiet/active and idle-noise strata, "
         "onset/offset cases, held-out splits, controls, baseline and "
         "independent Enhancement, listening, timing and content-preservation "
         "results."),
    )
    return [{
        "blocked": True,
        "bytes": None,
        "id": identifier,
        "kind": kind,
        "present": False,
        "requirement": requirement,
        "revision": None,
        "sha256": None,
        "verified": False,
    } for identifier, kind, requirement in items]


def exact_blockers() -> list[dict]:
    items = (
        ("BLK-01", "ART-01", ("RG-01", "RG-04"), "Source identity and code licence",
         "No NASE source snapshot, immutable revision, reviewed licence text, "
         "notice or per-file digest is staged. The census names the "
         "repository as an official research repo but records no licence."),
        ("BLK-02", "ART-02", ("RG-01", "RG-03"),
         "Checkpoint identity, terms and local bytes",
         "The census says a pretrained VoiceBank+DEMAND checkpoint exists, "
         "but no file name, revision, byte count or SHA-256 is recorded; "
         "checkpoint-specific terms and training/test overlap are unresolved."),
        ("BLK-03", "ART-03", ("RG-01", "RG-03"),
         "BEATs conditioning encoder identity and terms",
         "The evidence names a learned noise-aware BEATs conditioning model "
         "but records no encoder checkpoint, revision, byte count, SHA-256, "
         "feature configuration or separate terms."),
        ("BLK-04", "ART-04", ("RG-02",),
         "Pinned offline runtime and sampler",
         "No NASE runtime, interpreter lock, framework package, wheel, "
         "device profile, diffusion sampler, step count, noise schedule, "
         "seed policy or determinism setting exists."),
        ("BLK-05", "ART-05", ("RG-03",),
         "Rights bundle",
         "Source, NASE checkpoint, BEATs encoder, VoiceBank+DEMAND "
         "training-data, corpus, clean-reference and output-use terms are "
         "unresolved; no rights review reference exists."),
        ("BLK-06", "ART-06", ("RG-04", "RG-05"),
         "Offline diffusion geometry and conditioned cohort",
         "The evidence records an offline diffusion approach but no sample "
         "rate, STFT window, hop, sampler, conditioning layout, padding, "
         "output length or normalization, and no rights-cleared cohort or "
         "matched result."),
    )
    return [{
        "artifact_id": artifact,
        "id": identifier,
        "linked_gates": list(gates),
        "qualifies": False,
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity and "
            "rights can reopen this blocker."),
        "required_action": (
            "Supply the named artifact and rights evidence, then reproduce and "
            "independently review it."),
        "state": state,
        "status": "open",
        "title": title,
    } for identifier, artifact, gates, title, state in items]


def release_gates() -> list[dict]:
    items = (
        ("RG-01", "Exact pinned NASE source with immutable revision, "
                  "reviewed licence text, notice and per-file identity."),
        ("RG-02", "Exact pretrained VoiceBank+DEMAND checkpoint and exact "
                  "BEATs conditioning encoder, with byte counts, SHA-256 "
                  "values, tensor schemas and separate terms."),
        ("RG-03", "Locked offline runtime with deterministic seeded diffusion "
                  "sampler, exact package locks and a recorded supported "
                  "CPU/MPS platform."),
        ("RG-04", "Rights-cleared 16 kHz cohort with consent and permitted "
                  "clean references."),
        ("RG-05", "Frozen offline whole-utterance diffusion geometry: STFT "
                  "window/hop, sampler steps and noise schedule, BEATs "
                  "conditioning layout, padding, output length, normalization "
                  "and no streaming lookahead."),
        ("RG-06", "Enhancement result set: identity/noisy control, "
                  "task-matched baseline, paired metrics, clean-speech "
                  "preservation, peaks, invalid and nonfinite outputs."),
        ("RG-07", "Independent listening or labeled predictive screen plus "
                  "measured content/availability timing, memory, resources "
                  "and stochastic stability."),
        ("RG-08", "Opt-in OFF-by-default provider intake, descriptor/default "
                  "review, exact-head independent review and release "
                  "approval."),
    )
    return [{
        "id": identifier,
        "linked_row": TASK,
        "qualifies": False,
        "reopen_condition": (
            "The requirement is independently reproduced with exact assets, "
            "rights and matched evidence."),
        "requirement": requirement,
        "status": "blocked",
    } for identifier, requirement in items]


def qualification_block() -> dict:
    return {
        "all_release_gates_blocked": True,
        "asset_registry_entry_present": False,
        "benchmark_result": False,
        "beats_identity_verified": False,
        "device_timing_result": False,
        "diffusion_sampler_verified": False,
        "enhancement_profile_result": False,
        "exact_source_identity": False,
        "implementation_present": False,
        "listening_result": False,
        "missing_result_promoted": False,
        "offline_diffusion_geometry_verified": False,
        "output_validity_result": False,
        "peer_result_inherited": False,
        "real_result_present": False,
        "reason": (
            "Exact source and licence, NASE checkpoint bytes, BEATs encoder, "
            "runtime, diffusion sampler, offline geometry, rights-cleared "
            "cohort, matched evidence and independent review are all absent. "
            "No checkpoint identity is recorded."),
        "recorded_identity_only": False,
        "reference_execution_result": False,
        "release_claim": False,
        "rights_cleared_cohort": False,
        "runtime_pinned": False,
        "runtime_present": False,
        "source_license_verified": False,
        "source_present": False,
        "status": QUALIFICATION_STATUS,
        "weights_identity_verified": False,
        "weights_present_locally": False,
    }


def non_claims() -> list[str]:
    return [
        "No NASE source copy, repository snapshot, checkpoint, weight "
        "fragment, BEATs encoder, sampler configuration, runtime, corpus, "
        "recording, output or vendor result is present, loaded or executed.",
        "No diffusion inference, audio read or write, listening, paired "
        "SI-SDR or STOI scoring, clean-speech preservation, peak, alignment, "
        "content-delay or device-timing measurement is performed.",
        "No real or synthetic waveform is scored; the admission control is a "
        "schema object only and is marked synthetic_schema_control.",
        "No NASE checkpoint file name, byte count, SHA-256 or BEATs encoder "
        "identity is recorded; the census is a source lead, not a measurement.",
        "No local DNS result, VoiceBank score, FastEnhancer, LaCo-SENet, "
        "MP-SENet, ConvFSENet, GTCRN, DeepFilterNet3, ROSE-CD or other peer "
        "result is inherited or pooled.",
        "No benchmark, quality, latency, resource, stochastic-stability, "
        "streaming, provider or release claim is made; DEFER remains in force.",
        "No provider, descriptor, registry, default, public header, ABI, "
        "shared CMake, CI workflow, installed-v0 behavior, board or handoff "
        "is changed.",
        "No network access or download is attempted; absent artifacts are not "
        "fabricated, reconstructed, mirrored or substituted.",
    ]


def runtime_readiness() -> dict:
    return {
        "beats_encoder_present": False,
        "checkpoint_present": False,
        "device": None,
        "deterministic_seed_policy": None,
        "framework": None,
        "framework_version": None,
        "importable_module": False,
        "noise_schedule": None,
        "python_version": None,
        "runtime_present": False,
        "sampler_steps": None,
        "source_present": False,
    }


def recorded_identity() -> dict:
    return {
        "admitted_as_result": False,
        "beats_checkpoint_sha256": None,
        "byte_count_verified_locally": False,
        "checkpoint_bytes": None,
        "checkpoint_dir": None,
        "checkpoint_path": None,
        "checkpoint_sha256": None,
        "checkpoint_variant": None,
        "digest_verified_locally": False,
        "locally_present": False,
        "locally_verified": False,
        "manifest_path": None,
        "model_repository": SOURCE_REPOSITORY,
        "model_revision": None,
        "overrides_path": None,
        "qualifies": False,
        "recorded_by": [
            "research/noise_suppression_candidate_census.md",
            "research/evidence/pilot-discovery-20261027/source.txt",
            ACCOUNTING_REL,
            INVENTORY_REL,
        ],
        "status": "no_checkpoint_or_beats_identity_recorded_in_merged_evidence",
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset declaration.
# ---------------------------------------------------------------------------

DECLARATION_TOP = (
    "schema_id", "manifest_id", "source", "checkpoint", "conditioning_encoder",
    "runtime", "sampler", "geometry", "input", "controls", "rights",
)
SOURCE_FIELDS = (
    "repository", "revision", "license_spdx", "license_sha256", "tree_sha256",
)
CHECKPOINT_FIELDS = (
    "variant", "filename", "revision", "byte_count", "sha256",
    "terms_sha256", "tensor_schema_sha256",
)
ENCODER_FIELDS = (
    "name", "filename", "revision", "byte_count", "sha256", "license_spdx",
    "terms_sha256",
)
RUNTIME_FIELDS = (
    "python_version", "framework", "framework_version", "device",
    "lock_sha256", "offline_load", "deterministic", "packages",
)
SAMPLER_FIELDS = (
    "kind", "steps", "noise_schedule", "seed", "deterministic", "stochastic",
    "sampler_sha256",
)
GEOMETRY_FIELDS = (
    "mode", "channels", "sample_rate_hz", "sample_format",
    "stft_window_samples", "hop_samples", "lookahead_samples",
    "whole_utterance", "state_reset", "conditioning_layout",
    "output_length_policy",
)
INPUT_FIELDS = (
    "corpus_id", "split", "pair_count", "channels", "sample_rate_hz",
    "clean_reference", "consent", "rights_sha256",
)
CONTROL_FIELDS = (
    "identity_passthrough", "noisy_control", "task_matched_baseline",
    "nonfinite_rejection", "content_preservation_protocol",
)
RIGHT_FIELDS = (
    "source_terms", "checkpoint_terms", "encoder_terms", "training_data_terms",
    "corpus_rights", "clean_reference_permission", "output_use",
    "redistribution", "review_reference",
)

UNRESOLVED = frozenset((
    "", "n/a", "na", "none", "null", "tbd", "todo", "unresolved", "unknown",
))
LICENSES = frozenset((
    "Apache-2.0", "BSD-3-Clause", "CC-BY-4.0", "CC-BY-NC-4.0", "MIT",
    "MPL-2.0", "other-reviewed",
))
SAFE_BASENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
WEIGHT_SUFFIXES = (".pt", ".pth", ".ckpt", ".safetensors", ".bin")


class DeclarationError(ValueError):
    """A caller-supplied declaration failed the strict admission schema."""


def _exact_keys(value: Any, fields: Iterable[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise DeclarationError(label + "_not_object")
    expected = list(fields)
    observed = list(value)
    if sorted(observed) != sorted(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise DeclarationError(
            label + "_keys_mismatch:m=" + ",".join(missing) +
            ":x=" + ",".join(extra))
    if observed != expected:
        raise DeclarationError(label + "_keys_not_sorted_unique")
    return value


def _int(value: Any, label: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DeclarationError(label + "_not_integer")
    if value < low or value > high:
        raise DeclarationError(label + "_out_of_range")
    return value


def _bool(value: Any, label: str, expected: bool) -> None:
    if value is not expected:
        raise DeclarationError(label + "_not_" + str(expected).lower())


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise DeclarationError(label + "_not_sha256_hex")
    return value


def _hex40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX40.match(value):
        raise DeclarationError(label + "_not_revision_hex")
    return value


def _resolved(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise DeclarationError(label + "_not_string")
    text = value.strip()
    if text.lower() in UNRESOLVED or text.lower().startswith("unresolved"):
        raise DeclarationError(label + "_unresolved")
    return text


def _slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise DeclarationError(label + "_not_slug")
    return value


def _basename(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SAFE_BASENAME.match(value):
        raise DeclarationError(label + "_unsafe_path")
    if value != Path(value).name or "/" in value or "\\" in value or \
            ".." in value:
        raise DeclarationError(label + "_unsafe_path")
    return value


def _weight_name(value: Any, label: str) -> str:
    name = _basename(value, label)
    if not name.lower().endswith(WEIGHT_SUFFIXES):
        raise DeclarationError(label + "_unexpected_suffix")
    return name


def validate_asset_declaration(document: Any) -> dict:
    """Validate a caller-supplied manifest without opening any asset."""
    top = _exact_keys(document, DECLARATION_TOP, "top")
    if top["schema_id"] != DECLARATION_SCHEMA_ID:
        raise DeclarationError("schema_id_mismatch")
    _slug(top["manifest_id"], "manifest_id")

    source = _exact_keys(top["source"], SOURCE_FIELDS, "source")
    if source["repository"] != SOURCE_REPOSITORY:
        raise DeclarationError("source_repository_mismatch")
    _hex40(source["revision"], "source_revision")
    if source["license_spdx"] not in LICENSES:
        raise DeclarationError("source_license_unresolved")
    _hex64(source["license_sha256"], "source_license_sha256")
    _hex64(source["tree_sha256"], "source_tree_sha256")

    checkpoint = _exact_keys(top["checkpoint"], CHECKPOINT_FIELDS, "checkpoint")
    _slug(checkpoint["variant"], "checkpoint_variant")
    _weight_name(checkpoint["filename"], "checkpoint_filename")
    _hex40(checkpoint["revision"], "checkpoint_revision")
    _int(checkpoint["byte_count"], "checkpoint_byte_count", 1, 1 << 33)
    _hex64(checkpoint["sha256"], "checkpoint_sha256")
    _hex64(checkpoint["terms_sha256"], "checkpoint_terms_sha256")
    _hex64(checkpoint["tensor_schema_sha256"],
           "checkpoint_tensor_schema_sha256")

    encoder = _exact_keys(top["conditioning_encoder"], ENCODER_FIELDS,
                          "conditioning_encoder")
    if encoder["name"] != "BEATs":
        raise DeclarationError("conditioning_encoder_name_not_beats")
    _weight_name(encoder["filename"], "encoder_filename")
    _hex40(encoder["revision"], "encoder_revision")
    _int(encoder["byte_count"], "encoder_byte_count", 1, 1 << 33)
    _hex64(encoder["sha256"], "encoder_sha256")
    if encoder["license_spdx"] not in LICENSES:
        raise DeclarationError("encoder_license_unresolved")
    _hex64(encoder["terms_sha256"], "encoder_terms_sha256")

    runtime = _exact_keys(top["runtime"], RUNTIME_FIELDS, "runtime")
    if not isinstance(runtime["python_version"], str) or \
            not PYTHON.match(runtime["python_version"]):
        raise DeclarationError("runtime_python_version_mismatch")
    if runtime["framework"] not in ("pytorch", "torch"):
        raise DeclarationError("runtime_framework_mismatch")
    _resolved(runtime["framework_version"], "runtime_framework_version")
    if runtime["device"] not in ("cpu", "mps", "cuda"):
        raise DeclarationError("runtime_device_mismatch")
    _hex64(runtime["lock_sha256"], "runtime_lock_sha256")
    _bool(runtime["offline_load"], "runtime_offline_load", True)
    _bool(runtime["deterministic"], "runtime_deterministic", True)
    packages = runtime["packages"]
    if not isinstance(packages, list) or not packages:
        raise DeclarationError("runtime_packages_missing")
    if packages != sorted(set(packages)):
        raise DeclarationError("runtime_packages_not_sorted_unique")
    for package in packages:
        if not isinstance(package, str) or not PACKAGE.match(package):
            raise DeclarationError("runtime_package_malformed")

    sampler = _exact_keys(top["sampler"], SAMPLER_FIELDS, "sampler")
    if sampler["kind"] != "diffusion_offline":
        raise DeclarationError("sampler_kind_mismatch")
    _int(sampler["steps"], "sampler_steps", 1, 1000)
    if sampler["noise_schedule"] not in (
            "linear", "cosine", "sqrt", "sigmoid", "custom_reviewed"):
        raise DeclarationError("sampler_noise_schedule_unresolved")
    _int(sampler["seed"], "sampler_seed", 0, (1 << 32) - 1)
    _bool(sampler["deterministic"], "sampler_deterministic", True)
    _bool(sampler["stochastic"], "sampler_stochastic", True)
    _hex64(sampler["sampler_sha256"], "sampler_sha256")

    geometry = _exact_keys(top["geometry"], GEOMETRY_FIELDS, "geometry")
    if geometry["mode"] != "offline_whole_utterance":
        raise DeclarationError("geometry_mode_mismatch")
    _int(geometry["channels"], "geometry_channels", 1, 1)
    _int(geometry["sample_rate_hz"], "geometry_sample_rate_hz", 16000, 16000)
    if geometry["sample_format"] != "f32":
        raise DeclarationError("geometry_sample_format_mismatch")
    _int(geometry["stft_window_samples"], "geometry_stft_window", 16, 1 << 16)
    _int(geometry["hop_samples"], "geometry_hop", 1, 1 << 15)
    _int(geometry["lookahead_samples"], "geometry_lookahead", 0, 0)
    _bool(geometry["whole_utterance"], "geometry_whole_utterance", True)
    _bool(geometry["state_reset"], "geometry_state_reset", True)
    if geometry["conditioning_layout"] not in ("frame_level",
                                               "utterance_level",
                                               "chunk_level"):
        raise DeclarationError("geometry_conditioning_layout_unresolved")
    if geometry["output_length_policy"] not in ("match_input", "padded_crop"):
        raise DeclarationError("geometry_output_length_unresolved")

    item = _exact_keys(top["input"], INPUT_FIELDS, "input")
    _slug(item["corpus_id"], "input_corpus_id")
    _slug(item["split"], "input_split")
    _int(item["pair_count"], "input_pair_count", 1, 100000)
    _int(item["channels"], "input_channels", 1, 1)
    _int(item["sample_rate_hz"], "input_sample_rate_hz", 16000, 16000)
    _bool(item["clean_reference"], "input_clean_reference", True)
    _bool(item["consent"], "input_consent", True)
    _hex64(item["rights_sha256"], "input_rights_sha256")

    controls = _exact_keys(top["controls"], CONTROL_FIELDS, "controls")
    for field in CONTROL_FIELDS:
        _bool(controls[field], "controls_" + field, True)

    rights = _exact_keys(top["rights"], RIGHT_FIELDS, "rights")
    for field in RIGHT_FIELDS[:-1]:
        _bool(rights[field], "rights_" + field, True)
    _slug(rights["review_reference"], "rights_review_reference")

    return {
        "accepted": True,
        "manifest_id": top["manifest_id"],
        "opens_asset_bytes": False,
        "qualifies": False,
        "runtime_or_weights_invoked": False,
        "schema_id": DECLARATION_SCHEMA_ID,
    }


def declaration_control() -> dict:
    sha = "0" * 64
    revision = "1" * 40
    document = {
        "schema_id": DECLARATION_SCHEMA_ID,
        "manifest_id": "synthetic-nase-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": revision,
            "license_spdx": "MIT",
            "license_sha256": sha,
            "tree_sha256": sha,
        },
        "checkpoint": {
            "variant": "voicebank-demand",
            "filename": "nase.pt",
            "revision": revision,
            "byte_count": 1,
            "sha256": sha,
            "terms_sha256": sha,
            "tensor_schema_sha256": sha,
        },
        "conditioning_encoder": {
            "name": "BEATs",
            "filename": "beats.pt",
            "revision": revision,
            "byte_count": 1,
            "sha256": sha,
            "license_spdx": "MIT",
            "terms_sha256": sha,
        },
        "runtime": {
            "python_version": "3.12.16",
            "framework": "pytorch",
            "framework_version": "2.4.1",
            "device": "cpu",
            "lock_sha256": sha,
            "offline_load": True,
            "deterministic": True,
            "packages": ["numpy==1.26.4", "torch==2.4.1"],
        },
        "sampler": {
            "kind": "diffusion_offline",
            "steps": 1,
            "noise_schedule": "linear",
            "seed": 0,
            "deterministic": True,
            "stochastic": True,
            "sampler_sha256": sha,
        },
        "geometry": {
            "mode": "offline_whole_utterance",
            "channels": 1,
            "sample_rate_hz": 16000,
            "sample_format": "f32",
            "stft_window_samples": 512,
            "hop_samples": 160,
            "lookahead_samples": 0,
            "whole_utterance": True,
            "state_reset": True,
            "conditioning_layout": "utterance_level",
            "output_length_policy": "match_input",
        },
        "input": {
            "corpus_id": "synthetic-control",
            "split": "control",
            "pair_count": 1,
            "channels": 1,
            "sample_rate_hz": 16000,
            "clean_reference": True,
            "consent": True,
            "rights_sha256": sha,
        },
        "controls": {
            "identity_passthrough": True,
            "noisy_control": True,
            "task_matched_baseline": True,
            "nonfinite_rejection": True,
            "content_preservation_protocol": True,
        },
        "rights": {
            "source_terms": True,
            "checkpoint_terms": True,
            "encoder_terms": True,
            "training_data_terms": True,
            "corpus_rights": True,
            "clean_reference_permission": True,
            "output_use": True,
            "redistribution": True,
            "review_reference": "synthetic-review-reference",
        },
    }
    result = validate_asset_declaration(document)
    result["note"] = (
        "Synthetic schema control only. It proves the validator accepts a "
        "well-formed declaration and is not evidence, not an asset and not a "
        "result.")
    result["synthetic_schema_control"] = True
    result["qualifies"] = False
    return result


def _mutations() -> list[tuple[str, Any]]:
    base = declaration_control()
    # Rebuild from the source document, not the control wrapper.
    sha = "0" * 64
    revision = "1" * 40
    source = {
        "schema_id": DECLARATION_SCHEMA_ID,
        "manifest_id": "synthetic-nase-control",
        "source": {"repository": SOURCE_REPOSITORY, "revision": revision,
                   "license_spdx": "MIT", "license_sha256": sha,
                   "tree_sha256": sha},
        "checkpoint": {"variant": "voicebank-demand", "filename": "nase.pt",
                       "revision": revision, "byte_count": 1, "sha256": sha,
                       "terms_sha256": sha, "tensor_schema_sha256": sha},
        "conditioning_encoder": {"name": "BEATs", "filename": "beats.pt",
                                 "revision": revision, "byte_count": 1,
                                 "sha256": sha, "license_spdx": "MIT",
                                 "terms_sha256": sha},
        "runtime": {"python_version": "3.12.16", "framework": "pytorch",
                    "framework_version": "2.4.1", "device": "cpu",
                    "lock_sha256": sha, "offline_load": True,
                    "deterministic": True,
                    "packages": ["numpy==1.26.4", "torch==2.4.1"]},
        "sampler": {"kind": "diffusion_offline", "steps": 1,
                    "noise_schedule": "linear", "seed": 0,
                    "deterministic": True, "stochastic": True,
                    "sampler_sha256": sha},
        "geometry": {"mode": "offline_whole_utterance", "channels": 1,
                     "sample_rate_hz": 16000, "sample_format": "f32",
                     "stft_window_samples": 512, "hop_samples": 160,
                     "lookahead_samples": 0, "whole_utterance": True,
                     "state_reset": True,
                     "conditioning_layout": "utterance_level",
                     "output_length_policy": "match_input"},
        "input": {"corpus_id": "synthetic-control", "split": "control",
                  "pair_count": 1, "channels": 1, "sample_rate_hz": 16000,
                  "clean_reference": True, "consent": True,
                  "rights_sha256": sha},
        "controls": {"identity_passthrough": True, "noisy_control": True,
                     "task_matched_baseline": True,
                     "nonfinite_rejection": True,
                     "content_preservation_protocol": True},
        "rights": {"source_terms": True, "checkpoint_terms": True,
                   "encoder_terms": True, "training_data_terms": True,
                   "corpus_rights": True, "clean_reference_permission": True,
                   "output_use": True, "redistribution": True,
                   "review_reference": "synthetic-review-reference"},
    }
    mutations: list[tuple[str, Any]] = []

    def mutate(label: str, path: tuple[str, ...], value: Any) -> None:
        document = copy.deepcopy(source)
        target = document
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append((label, document))

    def drop(label: str, path: tuple[str, ...]) -> None:
        document = copy.deepcopy(source)
        target = document
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
        mutations.append((label, document))

    drop("missing_top_field", ("rights",))
    mutate("unknown_top_field", ("extra",), 1)
    mutate("source_revision_short", ("source", "revision"), "abc")
    mutate("source_license_unresolved", ("source", "license_spdx"),
           "unresolved")
    mutate("source_license_digest_missing", ("source", "license_sha256"), None)
    mutate("source_tree_digest_bad", ("source", "tree_sha256"), "zz")
    mutate("checkpoint_digest_bad", ("checkpoint", "sha256"), "ABC")
    mutate("checkpoint_bytes_float", ("checkpoint", "byte_count"), 1.5)
    mutate("checkpoint_terms_missing", ("checkpoint", "terms_sha256"), None)
    mutate("checkpoint_filename_unsafe", ("checkpoint", "filename"),
           "../../nase.pt")
    mutate("encoder_name_wrong", ("conditioning_encoder", "name"), "wav2vec")
    mutate("encoder_digest_missing", ("conditioning_encoder", "sha256"), None)
    mutate("runtime_deterministic_false", ("runtime", "deterministic"), False)
    mutate("runtime_offline_false", ("runtime", "offline_load"), False)
    mutate("runtime_packages_missing", ("runtime", "packages"), [])
    mutate("runtime_python_wrong", ("runtime", "python_version"), "3.11.9")
    mutate("sampler_steps_zero", ("sampler", "steps"), 0)
    mutate("sampler_seed_missing", ("sampler", "seed"), None)
    mutate("sampler_kind_streaming", ("sampler", "kind"), "streaming")
    mutate("sampler_schedule_unresolved", ("sampler", "noise_schedule"),
           "unknown")
    mutate("geometry_sample_rate_8000", ("geometry", "sample_rate_hz"), 8000)
    mutate("geometry_channels_stereo", ("geometry", "channels"), 2)
    mutate("geometry_mode_streaming", ("geometry", "mode"), "streaming")
    mutate("geometry_lookahead_160", ("geometry", "lookahead_samples"), 160)
    mutate("geometry_state_reset_false", ("geometry", "state_reset"), False)
    mutate("geometry_layout_unresolved", ("geometry", "conditioning_layout"),
           "unknown")
    mutate("input_consent_false", ("input", "consent"), False)
    mutate("input_clean_reference_false", ("input", "clean_reference"), False)
    mutate("input_pair_count_zero", ("input", "pair_count"), 0)
    mutate("input_rate_wrong", ("input", "sample_rate_hz"), 48000)
    mutate("controls_baseline_false", ("controls", "task_matched_baseline"),
           False)
    mutate("rights_redistribution_false", ("rights", "redistribution"), False)
    mutate("rights_training_data_false", ("rights", "training_data_terms"),
           False)
    mutate("rights_review_missing", ("rights", "review_reference"), None)
    mutate("nonfinite_checkpoint_bytes", ("checkpoint", "byte_count"),
           float("inf"))
    # `base` is unused as a document, but asserting it is accepted keeps the
    # control and the mutation source from drifting apart.
    if not base.get("accepted"):
        raise ValueError("declaration_control_rejected")
    return mutations


def declaration_rejections() -> dict:
    cases: list[dict] = []
    for label, document in _mutations():
        try:
            validate_asset_declaration(document)
        except (DeclarationError, ValueError):
            cases.append({"case": label, "rejected": True})
        else:
            cases.append({"case": label, "rejected": False})
    failed = [case["case"] for case in cases if not case["rejected"]]
    if failed:
        raise ValueError("declaration_rejections_not_rejected:"
                         + ",".join(failed))
    return {
        "accepted_control": declaration_control(),
        "accepted_control_qualifies": False,
        "cases": cases,
        "rejection_cases": len(cases),
    }


def strict_json_rejections() -> dict:
    payloads = {
        "duplicate_keys": '{"a":1,"a":2}',
        "infinity": '{"a":Infinity}',
        "nan": '{"a":NaN}',
        "negative_infinity": '{"a":-Infinity}',
        "root_array": '[1,2,3]',
        "root_number": '1',
        "trailing_data": '{"a":1}{"b":2}',
        "float_value": '{"a":1.5}',
        "invalid_json": '{"a":}',
        "empty_document": '',
    }
    cases: list[dict] = []
    for label, payload in payloads.items():
        try:
            loads_strict(payload)
        except (ValueError, TypeError):
            cases.append({"case": label, "rejected": True})
        else:
            cases.append({"case": label, "rejected": False})
    failed = [case["case"] for case in cases if not case["rejected"]]
    if failed:
        raise ValueError("strict_json_not_rejected:" + ",".join(failed))
    return {"cases": cases, "rejection_cases": len(cases)}


def asset_declaration_block() -> dict:
    control = declaration_control()
    rejections = declaration_rejections()
    strict = strict_json_rejections()
    return {
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "contract_id": DECLARATION_SCHEMA_ID,
        "control_keys": list(CONTROL_FIELDS),
        "duplicate_keys_rejected": True,
        "encoder_fields": list(ENCODER_FIELDS),
        "exact_interpreter": REQUIRED_INTERPRETER,
        "floats_rejected": True,
        "geometry_fields": list(GEOMETRY_FIELDS),
        "input_fields": list(INPUT_FIELDS),
        "manifest_validation_only": True,
        "max_pairs": 100000,
        "max_weight_bytes": 1 << 33,
        "nonfinite_rejected": True,
        "rejection_cases": rejections["rejection_cases"],
        "required_channels": 1,
        "required_conditioning_encoder": "BEATs",
        "required_lookahead_samples": 0,
        "required_mode": "offline_whole_utterance",
        "required_sample_rate_hz": 16000,
        "required_sampler_kind": "diffusion_offline",
        "required_top_level_fields": list(DECLARATION_TOP),
        "rights_fields": list(RIGHT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "runtime_or_weights_invoked": False,
        "sampler_fields": list(SAMPLER_FIELDS),
        "schema_id": DECLARATION_SCHEMA_ID,
        "source_fields": list(SOURCE_FIELDS),
        "strict_json_cases": strict["rejection_cases"],
        "synthetic_control": control,
        "unknown_fields_rejected": True,
        "unresolved_values_rejected": True,
    }


# ---------------------------------------------------------------------------
# Canonical documents.
# ---------------------------------------------------------------------------


def _boundary_pins() -> dict:
    return dict(sorted(BOUNDARY_PINS.items()))


def _source_pins() -> dict:
    return dict(sorted(SOURCE_PINS.items()))


def _reported_metrics() -> dict:
    return {
        "admitted_as_result": False,
        "cohort": None,
        "note": (
            "No NASE metric, metric table or checkpoint manifest is recorded "
            "in the pinned evidence. No upstream value is quoted and no local "
            "score exists."),
        "pesq": None,
        "qualifies": False,
        "stoi": None,
        "status": "no_metric_recorded",
    }


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "admission_contract": asset_declaration_block(),
        "asset_registry": asset_registry(),
        "base_commit": BASE_COMMIT,
        "board_file_pinned": False,
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "board_status_is_observation_only": True,
        "boundary": boundary_block(),
        "boundary_pins": _boundary_pins(),
        "branch": BRANCH,
        "candidate": source_reported_identity(),
        "component": COMPONENT_ID,
        "contract_id": CONTRACT_ID,
        "decision": DECISION,
        "disposition": disposition_block(),
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": exact_blockers(),
        "exact_scope": exact_scope_block(),
        "incomplete": True,
        "linked_rows": list(rows),
        "linked_rows_sha256": linked_rows_digest(rows),
        "local_files": list(LOCAL_FILES),
        "mode": MODE,
        "non_claims": non_claims(),
        "profile": PROFILE,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification": qualification_block(),
        "qualification_status": QUALIFICATION_STATUS,
        "release_gates": release_gates(),
        "reported_metrics": _reported_metrics(),
        "required_artifacts": required_artifacts(),
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": scope_block(),
        "source_pins": _source_pins(),
        "status": STATUS,
        "task": TASK,
        "task_geometry": task_geometry(),
        "title": CANDIDATE_NAME,
        "write_scope": WRITE_SCOPE,
    }


def build_report() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    profile = enhancement_profile()
    gates = release_gates()
    blockers = exact_blockers()
    artifacts = required_artifacts()
    qualification = qualification_block()
    return {
        "absence_evidence": absence_summary(),
        "accounting_row": accounting_row(),
        "asset_declaration": asset_declaration_block(),
        "asset_registry": asset_registry(),
        "base_commit": BASE_COMMIT,
        "board_file_pinned": False,
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "board_status_is_observation_only": True,
        "boundary": boundary_block(),
        "boundary_pins": _boundary_pins(),
        "branch": BRANCH,
        "candidate": source_reported_identity(),
        "component": COMPONENT_ID,
        "decision": DECISION,
        "disposition": disposition_block(),
        "enhancement_profile": profile,
        "evidence_presence": evidence_presence(),
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": blockers,
        "exact_scope": exact_scope_block(),
        "gates": gates,
        "incomplete": True,
        "inventory_record": inventory_record(),
        "linked_rows": list(rows),
        "linked_rows_sha256": linked_rows_digest(rows),
        "local_files": list(LOCAL_FILES),
        "mode": MODE,
        "non_claims": non_claims(),
        "profile": PROFILE,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification": qualification,
        "qualification_status": QUALIFICATION_STATUS,
        "recorded_identity": recorded_identity(),
        "reported_metrics": _reported_metrics(),
        "required_artifacts": artifacts,
        "runtime_readiness": runtime_readiness(),
        "schema_id": REPORT_SCHEMA_ID,
        "scope": scope_block(),
        "source_pins": _source_pins(),
        "status": STATUS,
        "task": TASK,
        "task_geometry": task_geometry(),
        "title": CANDIDATE_NAME,
        "upstream_record": source_reported_identity(),
        "write_scope": WRITE_SCOPE,
    }
