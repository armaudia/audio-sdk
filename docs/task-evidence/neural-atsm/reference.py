# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-NEURAL-ATSM.

Standard library only. The catalogued candidate is the Interspeech 2024
"Neural ATSM" system: sentence text -> phoneme-level rate, with learned
upsampling/attention and VAE/flow reconstruction in the full paper stack.
No official runnable code, weight, checkpoint, runtime, licence text,
rights-cleared input or output is present anywhere probed.

This module pins the evidence that does exist, proves a fixed absence
inventory, validates a fail-closed caller-supplied asset declaration without
resolving, importing, loading or executing anything, and builds canonical
DEFER bytes. It never estimates a rate, stretches audio, synthesises speech,
opens media, times a device or produces a benchmark result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-NEURAL-ATSM"
TASK_TITLE = "Neural ATSM"
COMPONENT_ID = "neural-atsm"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/neural-atsm/ only"
TASK_PREFIX = "docs/task-evidence/neural-atsm/"
CONTRACT_ID = "audio-sdk/neural-atsm-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/neural-atsm-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/neural-atsm-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/neural-atsm-asset-declaration/0.1"
BASE_COMMIT = "d2eae1246561fe11c5a3d17733ddd46db53e7803"
BRANCH = "swarm/SDK-NEURAL-ATSM"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
PAPER_URL = "https://www.isca-archive.org/interspeech_2024/lee24m_interspeech.html"
CANDIDATE_NAME = "Neural ATSM"
CANDIDATE_FAMILY = "text_conditioned_phoneme_rate_tsm"
TASK_GEOMETRY_STATE = "mismatch_text_conditioned_renderer_vs_audio_rate_profile"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

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
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md":
        "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
    "research/tsm-followup-20261101/agent-neural/REPORT.md":
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    "research/tsm-followup-20261101/agent-stretchers/REPORT.md":
        "8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb",
    "research/speech-rate-tsm-evaluation-20261101.md":
        "525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d",
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
    "docs/task-evidence/diffatsm/README.md":
        "89a8e7c1bf69dff35149e375ecd81cf5cf27aa0f368c91db95624c84e808f7da",
    "docs/task-evidence/diffatsm/report.json":
        "8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Measure source/output mapping",
    "duration, pitch, transient audibility and playback buffering",
    "1\u00d7, rate changes, unfamiliar speech, music, silence, rebuffer, drift "
    "and the final partial window",
    "pause or filler decisions tied to source timestamps and measure speech "
    "preservation",
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
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h5",
    ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o",
    ".onnx", ".opus", ".otf", ".pcap", ".pcapng", ".pt", ".pth", ".pyc",
    ".safetensors", ".so", ".tar", ".ttf", ".wav", ".wasm", ".weights",
    ".zip",
}

# Fixed probes only; no recursive walk and no network.
WORKSPACE_PROBES = (
    "data/checkouts/neural-atsm",
    "data/checkouts/neural_atsm",
    "data/checkouts/interspeech2024-neural-atsm",
    "data/models/neural-atsm",
    "data/models/neural_atsm",
    "data/envs/neural-atsm",
    "data/envs/neural-atsm-text-frontend",
    "data/reference/neural-atsm",
    "data/audio/neural-atsm",
    "data/runs/neural-atsm",
    "research/neural-atsm",
    "research/tsm-followup-20261101/agent-neural/checkpoints/neural-atsm",
)
WORKTREE_PROBES = (
    "adapters/neural-atsm",
    "schemas/providers/neural-atsm",
    "third_party/neural-atsm",
    "third_party/neural_atsm",
    "build/check-env/lib/python3.12/site-packages/neural_atsm",
)
HOME_PROBES = (
    "~/.cache/neural-atsm",
    "~/.cache/huggingface/hub/models--neural-atsm",
    "~/.cache/huggingface/hub/models--interspeech2024-neural-atsm",
)

NON_CLAIMS = [
    "No Neural ATSM source, code snapshot, weight, checkpoint, phoneme-rate "
    "head, text frontend, VAE/flow decoder or inference config is present, "
    "imported, deserialised, loaded or executed.",
    "No PyTorch, TensorFlow, diffusion, vocoder or text-frontend module is "
    "installed, imported or linked by this package.",
    "No text, phoneme sequence, real audio, corpus, synthetic speech, "
    "resynthesis or candidate output is read, generated or produced.",
    "No Neural ATSM rate, duration, pitch, transient, preservation, "
    "listening, device-timing or benchmark result is reproduced.",
    "The caller-supplied asset declaration is a fail-closed shape check only; "
    "it never resolves a path, hashes an external byte, admits a presence "
    "claim or grants qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build, CI "
    "workflow, board or handoff change exists.",
    "The research prose and paper URL are source-reported context only and "
    "are not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
    "No DiffATSM or other sibling evidence, fixture, checkpoint or metric is "
    "inherited, pooled or treated as a Neural ATSM result.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "research/tsm-followup-20261101/README.md",
        "line": 37,
        "class": "candidate_screen_source_reported",
        "admitted_as_result": False,
        "boundary": "The follow-up scorecard names Neural ATSM as a "
                    "text-conditioned phoneme-rate / learned TSM system, "
                    "inspected at paper and artifact level only, and records "
                    "no runnable lightweight audio-only controller artifact.",
    },
    {
        "source": "research/tsm-followup-20261101/agent-text/REPORT.md",
        "line": 49,
        "class": "artifact_review_source_reported",
        "admitted_as_result": False,
        "boundary": "Records that the Interspeech 2024 system predicts "
                    "phoneme-level rates from text, includes learned audio "
                    "generation/resynthesis, and that no official executable "
                    "lightweight waveform-to-rate module or checkpoint was "
                    "identified in that evaluation.",
    },
    {
        "source": "research/speech-rate-tsm-evaluation-20261101.md",
        "line": 28,
        "class": "initial_screen_source_reported",
        "admitted_as_result": False,
        "boundary": "Describes sentence text -> phoneme-level rate with "
                    "learned upsampling/attention and VAE/flow "
                    "reconstruction, records no official runnable code or "
                    "weights, and marks it research-only / not runnable here.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks neural-atsm as considered, disposition sdk-model "
                    "and verification_profile rate; it is not a result.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines the Rate profile requirements. No rate "
                    "measurement, control, pitch, buffering, preservation or "
                    "device-timing record exists for Neural ATSM.",
    },
)

PEER_SEPARATION = (
    {
        "component": "diffatsm",
        "task": "SDK-DIFFATSM",
        "path": "docs/task-evidence/diffatsm/report.json",
        "class": "separate_neural_tsm_candidate",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "DiffATSM is a distinct raw-audio diffusion TSM system "
                    "with its own forthcoming-implementation blocker. No "
                    "source, checkpoint, PPG model, envelope case, rejection "
                    "count or metric is inherited or pooled here.",
    },
)


# ---------------------------------------------------------------------------
# Strict JSON, canonical bytes and hashing.
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
# Stable board identity. The mutable board file is read, never pinned.
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
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
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
    if result[0]["component"] != COMPONENT_ID:
        raise ValueError("linked_component_mismatch")
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


# ---------------------------------------------------------------------------
# Task-local git scope. The base is the newest merge-base between HEAD and the
# available PR base refs, not a fixed historical commit. Later sibling merges
# stay out of the comparison while any edit outside TASK_PREFIX fails closed.
# ---------------------------------------------------------------------------

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref."""
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
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]



# ---------------------------------------------------------------------------
# Fixed evidence probes. No recursive walk and no network.
# ---------------------------------------------------------------------------


def _probe(path: Path, label: str, workspace: bool, worktree: bool,
           home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def workspace_probes() -> list[dict]:
    return [_probe(AUDIO_ROOT / path, path, True, False, False)
            for path in WORKSPACE_PROBES]


def worktree_probes() -> list[dict]:
    return [_probe(WORKTREE / path, path, False, True, False)
            for path in WORKTREE_PROBES]


def home_probes() -> list[dict]:
    return [_probe(Path(path).expanduser(), path, False, False, True)
            for path in HOME_PROBES]


def all_probes() -> list[dict]:
    return workspace_probes() + worktree_probes() + home_probes()


def absence_summary(probes: list[dict] | None = None) -> dict:
    rows = all_probes() if probes is None else probes
    return {
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for row in rows
                                     if row["searched_workspace"]),
        "worktree_probe_count": sum(1 for row in rows
                                    if row["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for row in rows
                                if row["searched_home_cache"]),
        "present_count": sum(1 for row in rows if row["present"] is not False),
        "all_absent": all(row["present"] is False for row in rows),
        "probes": rows,
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "candidate_module_imported": False,
        "candidate_runtime_executed": False,
        "weights_loaded": False,
        "audio_read": False,
        "text_or_phoneme_input_read": False,
    }


def runtime_readiness() -> dict:
    return {
        "runtime_present": False,
        "runtime_pinned": False,
        "interpreter_pin": REQUIRED_INTERPRETER,
        "candidate_module_available": False,
        "import_attempted": False,
        "text_frontend_present": False,
        "phoneme_rate_head_present": False,
        "upsampling_attention_present": False,
        "vae_or_flow_decoder_present": False,
        "device": None,
        "dtype": None,
        "lock_sha256": None,
        "packages": [],
    }


# ---------------------------------------------------------------------------
# Pins, README digest tables and SOURCES.sha256.
# ---------------------------------------------------------------------------


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows: list[dict] = []
    for relative in sorted(pins):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows.append({
            "path": relative,
            "sha256": pins[relative],
            "actual": actual,
            "verified": actual == pins[relative],
        })
    return rows


def _local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: list[tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if HEX64.fullmatch(digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:"
                f"extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                relative = key[len("source:"):]
                expected_digest = SOURCE_PINS[relative]
                path = AUDIO_ROOT / relative
            elif section == "boundary":
                relative = key[len("sdk:"):]
                expected_digest = BOUNDARY_PINS[relative]
                path = SDK_ROOT / relative
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = [f"| `source:{name}` | `{digest}` |"
                for name, digest in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = [f"| `sdk:{name}` | `{digest}` |"
                for name, digest in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            if name in ARTIFACT_TABLE_EXCLUDED:
                continue
            path = HERE / name
            rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                        f"{path.stat().st_size} |")
    else:
        raise ValueError("unknown_readme_section:" + section)
    return "\n".join(rows)


def update_readme_table(text: str, section: str) -> str:
    block = render_digest_table(section)
    start, end = README_MARKERS[section]
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[:start_index] + start + "\n" + block + "\n" + end + \
        text[end_index:]


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Candidate identity, task geometry and the rate profile.
# ---------------------------------------------------------------------------


def source_reported_identity() -> dict:
    return {
        "candidate": CANDIDATE_NAME,
        "candidate_family": CANDIDATE_FAMILY,
        "venue": "Interspeech 2024",
        "paper_reference": PAPER_URL,
        "source_reported_task": "text-conditioned phoneme-level rate "
                                "prediction plus learned resynthesis",
        "source_reported_stages": [
            "text_frontend",
            "phoneme_rate_predictor",
            "learned_upsampling_attention",
            "vae_or_flow_reconstruction",
        ],
        "text_conditioned": True,
        "audio_only_controller": False,
        "rate_only_estimator": False,
        "input_is_audio": False,
        "output_is_audio": True,
        "official_code_found": False,
        "official_weights_found": False,
        "immutable_revision_recorded": False,
        "license_recorded": False,
        "license_text_staged": False,
        "model_card_staged": False,
        "runnable_as_released": False,
        "source_reported_only": True,
        "identity_verified": False,
    }


def task_geometry() -> dict:
    return {
        "state": TASK_GEOMETRY_STATE,
        "source_reported_input": "sentence text",
        "source_reported_output": "phoneme-level rate and resynthesised audio",
        "source_reported_reconstruction": "learned upsampling/attention with "
                                          "VAE/flow reconstruction",
        "audio_input_path_verified": False,
        "audio_only_controller": False,
        "rate_only_estimator": False,
        "text_input_required": True,
        "sample_rate_hz": None,
        "frame_samples": None,
        "hop_samples": None,
        "channels": None,
        "dtype": None,
        "latency_ms": None,
        "geometry_documented": False,
        "geometry_verified": False,
        "rate_profile_fit": "mismatch",
        "profile_fit_reason": "The Rate profile expects an audio source to a "
                              "stretched audio output with a frozen "
                              "rate/frame/hop geometry. The catalogued "
                              "candidate consumes sentence text and "
                              "resynthesises audio; no audio-in rate "
                              "controller or exact streaming geometry is "
                              "documented.",
    }


RATE_REQUIREMENTS = (
    ("RATE-01", "Source/output mapping for the exact runtime.", "blocked"),
    ("RATE-02", "Target and actual duration for constant and changing rates.",
     "blocked"),
    ("RATE-03", "Pitch preservation or shift for the exact runtime.",
     "blocked"),
    ("RATE-04", "Transient audibility proxy or authorized listening.",
     "blocked"),
    ("RATE-05", "Playback buffering, fill/flush and deadline behaviour.",
     "blocked"),
    ("RATE-06", "1x identity control.", "blocked"),
    ("RATE-07", "Rate changes, including step and ramp profiles.", "blocked"),
    ("RATE-08", "Unfamiliar speech material.", "blocked"),
    ("RATE-09", "Music material and a synthetic music negative control.",
     "blocked"),
    ("RATE-10", "Silence and empty input.", "blocked"),
    ("RATE-11", "Rebuffer, drift and the final partial window.", "blocked"),
    ("RATE-12", "Pause or filler decisions tied to source timestamps and "
                "speech preservation.", "blocked"),
    ("RATE-13", "Separate paired, unpaired, synthetic, human and "
                "source-reported evidence.", "documented"),
)


def rate_profile() -> dict:
    rows = []
    for row_id, requirement, state in RATE_REQUIREMENTS:
        blocked = state == "blocked"
        rows.append({
            "id": row_id,
            "requirement": requirement,
            "status": state,
            "evidence": (
                "No Neural ATSM source, text frontend, phoneme-rate head, "
                "checkpoint, runtime or output exists; the item cannot be "
                "measured. The catalogued task is text-conditioned and does "
                "not expose an audio-in rate controller."
                if blocked else
                "The report keeps source-reported, synthetic-schema, "
                "missing-real and sibling candidate sections separate; no "
                "category is pooled."),
            "qualifies": False,
        })
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": rows,
        "conditions": [
            "identity_1x",
            "rate_changes",
            "unfamiliar_speech",
            "music",
            "silence",
            "rebuffer",
            "drift",
            "final_partial_window",
            "pause_filler_source_timestamps",
        ],
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_results": 0,
        "surrogate_present": False,
        "synthetic_envelope_only": False,
        "candidate_geometry": None,
        "candidate_duration_result": None,
        "candidate_pitch_result": None,
        "candidate_transient_result": None,
        "candidate_preservation_result": None,
        "candidate_buffering_result": None,
        "rate_result_present": False,
    }


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": [phrase for phrase in PROFILE_PHRASES
                            if len(rows) == 1 and phrase in rows[0]],
        "all_phrases_present": len(rows) == 1 and all(
            phrase in rows[0] for phrase in PROFILE_PHRASES),
    }


def matched_evidence() -> dict:
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "candidate_profile_fit": "mismatch",
        "matched_cohort_present": False,
        "matched_baseline_present": False,
        "paired_clean_reference_present": False,
        "source_output_mapping_present": False,
        "same_condition_control_present": False,
        "listening_or_labeled_screen_present": False,
        "evidence_classes": [
            "source_reported_candidate_screen",
            "source_reported_artifact_review",
            "missing_real_candidate_result",
            "separate_sibling_candidate",
            "unchanged_v0_contract",
        ],
        "classes_pooled": False,
        "synthetic_schema_control_counted_as_result": False,
        "required_separation": "Source-reported prose, schema-only "
                               "declarations, missing real measurements and "
                               "sibling candidate evidence stay in distinct "
                               "sections and are never pooled.",
    }


def inventory_record() -> dict:
    document = read_strict_json(AUDIO_ROOT / "audio-benchmark-platform/"
                                           "plan/INVENTORY.json")
    components = document.get("components")
    if not isinstance(components, list):
        raise ValueError("inventory_components_not_list")
    matches = [row for row in components
               if isinstance(row, dict) and row.get("id") == COMPONENT_ID]
    if len(matches) != 1:
        raise ValueError("inventory_row_not_unique")
    row = matches[0]
    if row.get("task") != TASK:
        raise ValueError("inventory_task_mismatch")
    if row.get("name") != TASK_TITLE:
        raise ValueError("inventory_name_mismatch")
    if row.get("verification_profile") != PROFILE:
        raise ValueError("inventory_profile_mismatch")
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "evidence_status": row.get("evidence_status"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
        "evidence": list(row.get("evidence", [])),
        "evidence_count": len(row.get("evidence", [])),
    }


def evidence_snippet_check() -> dict:
    phrases = (
        ("research/tsm-followup-20261101/README.md",
         "no runnable lightweight audio-only controller artifact found"),
        ("research/tsm-followup-20261101/README.md",
         "full stack is text-conditioned and reconstructs audio"),
        ("research/tsm-followup-20261101/agent-text/REPORT.md",
         "No official executable lightweight waveform-to-rate module"),
        ("research/tsm-followup-20261101/agent-text/REPORT.md",
         "Poor fit for audio-only controller"),
        ("research/speech-rate-tsm-evaluation-20261101.md",
         "Sentence text"),
        ("research/speech-rate-tsm-evaluation-20261101.md",
         "No official runnable code/weights found in this review"),
        ("research/speech-rate-tsm-evaluation-20261101.md",
         PAPER_URL),
        ("audio-benchmark-platform/plan/INVENTORY.json",
         "no runnable lightweight audio-only controller artifact found"),
    )
    checks = []
    for relative, phrase in phrases:
        payload = (AUDIO_ROOT / relative).read_text(encoding="utf-8")
        checks.append({
            "path": relative,
            "phrase": phrase,
            "present": phrase in payload,
        })
    return {
        "count": len(checks),
        "checks": checks,
        "all_present": all(row["present"] for row in checks),
    }


# ---------------------------------------------------------------------------
# Boundary and scope records.
# ---------------------------------------------------------------------------


def boundary_block() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "provider_registration": False,
        "adapter_json_added": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "native_engine_built": False,
        "runtime_imported": False,
        "candidate_code_vendored": False,
        "weights_vendored": False,
        "audio_added": False,
        "corpus_added": False,
        "text_or_phoneme_input_added": False,
        "processed_output_added": False,
        "board_or_handoff_changed": False,
        "linked_row": projection,
        "linked_row_sha256": board_row_digest(projection),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "linked_row_identity_only": True,
        "board_file_pinned": False,
        "mutable_board_fields_gate": False,
        "excluded_mutable_fields": [
            "status", "owner", "claim", "review", "handoff",
            "blocked_reason", "dispatch_priority",
        ],
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "network_access": False,
        "candidate_code_downloaded": False,
        "candidate_code_vendored": False,
        "model_weights_downloaded": False,
        "model_weights_vendored": False,
        "runtime_invoked": False,
        "candidate_runtime_executed": False,
        "real_audio": False,
        "text_or_phoneme_input": False,
        "synthetic_speech": False,
        "processed_output_present": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_default": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "peer_evidence_inherited": False,
        "write_scope": WRITE_SCOPE,
    }


def exact_scope_block() -> dict:
    return {
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "only_task_directory_written": True,
        "provider_files_changed": False,
        "adapter_files_changed": False,
        "descriptor_or_registry_changed": False,
        "contracts_header_changed": False,
        "cmake_or_ci_changed": False,
        "board_or_handoff_changed": False,
        "default_selection_changed": False,
        "candidate_code_weights_or_audio_committed": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "sample_format": "float32",
        "unchanged": True,
        "neural_atsm_mapping_present": False,
    }


def disposition_block() -> dict:
    return {
        "task_mode": MODE,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "candidate_artifact_present": False,
        "runtime_present": False,
        "output_present": False,
        "rights_cleared_input_present": False,
        "result_promoted": False,
        "summary": "Neural ATSM is the Interspeech 2024 text-conditioned "
                   "phoneme-rate / learned TSM system. The paper and research "
                   "screens are available as source-reported context only. "
                   "Locally absent and unverified: runnable official code, "
                   "weights, runtime, exact audio geometry, terms, "
                   "rights-cleared text/audio inputs, matched cohort, output "
                   "and rate result.",
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers and gates.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "evidence_register_and_policy_boundary", True,
         "The linked inventory row, pinned Rate acceptance profile, SDK "
         "delivery plan, research findings, task evidence and unchanged v0 "
         "contract boundary."),
        ("ART-02", "exact_upstream_source_snapshot", False,
         "The exact official Neural ATSM source tree at an immutable 40-hex "
         "commit or release tag, including licence text, README, model/API "
         "definitions and a per-file SHA-256 manifest."),
        ("ART-03", "phoneme_rate_and_resynthesis_assets", False,
         "Every text-frontend vocabulary, phoneme-rate head, upsampling or "
         "attention module, VAE/flow decoder, vocoder and inference config "
         "with exact names, revision, byte counts and SHA-256 values."),
        ("ART-04", "pinned_text_and_inference_runtime", False,
         "A locked offline runtime with interpreter, text frontend, package "
         "versions, wheel hashes, platform, device, dtype, determinism "
         "settings and install location."),
        ("ART-05", "rights_cleared_inputs_and_training_data", False,
         "Code, weight, training-data, text-corpus and derived-output terms "
         "plus a digest-pinned, rights-cleared text and speech input set "
         "with consent, acquisition, evaluation and redistribution "
         "decisions."),
        ("ART-06", "reproduced_rate_and_output_results", False,
         "Deterministic reproduced output on the exact runtime with "
         "source/output mapping, duration, pitch, transient, buffering, "
         "silence, rebuffer, drift, final-partial and preservation results."),
        ("ART-07", "provider_intake_and_public_surface", False,
         "A separate versioned OFF-by-default provider intake with "
         "clean-install proof, empty defaults, no shared-build change and "
         "independent exact-head review."),
    ]
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": present,
        "verified": present,
        "blocked": not present,
        "sha256": None,
        "revision": None,
        "bytes": None,
    } for artifact_id, kind, present, requirement in rows]


def exact_blockers() -> list[dict]:
    rows = [
        ("BLK-01", "ART-02", ["RG-01"],
         "No immutable runnable upstream source",
         "The research screens locate the paper and report that no official "
         "executable lightweight waveform-to-rate module or checkpoint was "
         "identified. No official repository, commit, release tag, source "
         "file, licence text or notice is staged at any probed path."),
        ("BLK-02", "ART-03", ["RG-01", "RG-03"],
         "No phoneme-rate or resynthesis asset identity",
         "No text frontend, phoneme-rate head, upsampling/attention module, "
         "VAE/flow decoder, vocoder or config is named. No file name, "
         "revision, byte count, SHA-256 or tensor layout exists, and no "
         "weight byte is present or downloaded."),
        ("BLK-03", "ART-04", ["RG-02"],
         "No pinned runtime or audio task geometry",
         "The candidate is text-conditioned and reconstructs audio; no "
         "audio-in/rate-out geometry, sample rate, frame, hop, channel, "
         "latency, device, dtype or interpreter lock is documented. The "
         "probed interpreter exposes no Neural ATSM module."),
        ("BLK-04", "ART-05", ["RG-04"],
         "No reviewed rights or training-data terms",
         "No code licence, weight term, training-data statement, text-corpus "
         "lineage, attribution bundle, derived-output permission or "
         "redistribution decision is staged or reviewed. No rights-cleared "
         "text or speech input exists."),
        ("BLK-05", "ART-06", ["RG-05", "RG-06"],
         "No reproduced rate or output result",
         "No candidate execution, output hash, source/output mapping, "
         "duration, pitch, transient, buffering, silence, rebuffer, drift, "
         "final-partial or speech-preservation measurement exists. The Rate "
         "profile is unsatisfied and the profile is a poor fit for a "
         "text-conditioned renderer."),
        ("BLK-06", "ART-07", ["RG-07", "RG-08"],
         "No matched cohort, listening, timing or release evidence",
         "No rights-cleared matched cohort, same-condition baseline, "
         "authorized listening or labeled screen, device timing, resource "
         "measurement, benchmark, provider intake or independent review "
         "exists."),
    ]
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": linked_gates,
        "title": title,
        "statement": statement,
        "status": "open",
        "qualifies": False,
        "required_action": "Supply the named artifact and rights evidence at "
                           "an immutable identity, then reproduce and "
                           "independently review it.",
        "reopen_condition": "Only a caller-supplied exact artifact with "
                            "verified identity, terms and matched evidence "
                            "can reopen this blocker.",
    } for blocker_id, artifact_id, linked_gates, title, statement in rows]


RELEASE_GATES = (
    ("source_revision_and_license_provenance",
     "Stage the official source at an immutable revision with complete "
     "licence, notice and README records, then record independent review."),
    ("pinned_runtime_and_offline_install",
     "Provide a locked offline runtime with wheel hashes, install location, "
     "clean-room import digest and exact text-frontend/inference settings."),
    ("phoneme_rate_and_resynthesis_assets",
     "Stage every text-frontend, phoneme-rate, upsampling/attention, "
     "VAE/flow and vocoder asset and verify each byte count and SHA-256."),
    ("rights_cleared_inputs_and_training_data",
     "Freeze permitted, digest-pinned text and speech inputs with corpus, "
     "evaluation, derived-output and redistribution decisions plus weight "
     "and training-data terms."),
    ("reference_execution_and_output_validity",
     "Execute the pinned assets offline and record output hashes, finite and "
     "length behaviour, exact repeats and peak/RSS values."),
    ("rate_profile_against_real_runtime",
     "Run every Rate-profile case on a rights-cleared cohort with 1x, rate "
     "changes, unfamiliar speech, music, silence, rebuffer, drift and the "
     "final partial window."),
    ("mode_platform_timing_resources_and_listening",
     "Measure each mode and platform separately with timing, resources and "
     "pacing, and complete authorized listening or a labeled screen."),
    ("provider_intake_public_surface_and_release",
     "Open a separate versioned OFF-by-default intake with clean-install "
     "proof and independent exact-head review after all prior gates clear."),
)


def release_gates() -> list[dict]:
    projection = board_row_projection()
    return [{
        "id": "RG-%02d" % index,
        "title": title,
        "statement": "No Neural ATSM artifact, runtime, right, matched "
                     "measurement or review satisfies this requirement.",
        "status": "blocked",
        "qualifies": False,
        "linked_row": projection,
        "reopen_condition": reopen,
    } for index, (title, reopen) in enumerate(RELEASE_GATES, 1)]


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "candidate_present": False,
        "source_present": False,
        "source_identity_recorded": False,
        "weights_identified": False,
        "weights_present": False,
        "checkpoint_present": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "geometry_verified": False,
        "license_text_present": False,
        "rights_cleared": False,
        "input_media_present": False,
        "text_or_phoneme_input_present": False,
        "reference_execution_result": False,
        "output_validity_result": False,
        "rate_profile_result": False,
        "duration_result": False,
        "pitch_result": False,
        "transient_result": False,
        "buffering_result": False,
        "preservation_result": False,
        "listening_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "implementation_present": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
        "reason": "Official runnable source, weights, pinned runtime, exact "
                  "audio geometry, reviewed terms, rights-cleared inputs, "
                  "matched cohort, reproduced output and independent review "
                  "are all absent. The text-conditioned renderer is also a "
                  "poor fit for the audio Rate profile.",
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset declaration. Shape only; it never
# resolves a path, hashes an external byte, loads a model or admits a claim.
# ---------------------------------------------------------------------------

DECLARATION_FIELDS = ("schema_id", "declaration_id", "candidate", "source",
                      "weights", "runtime", "geometry", "rights",
                      "disposition")
CANDIDATE_DECL_FIELDS = ("name", "family", "paper_reference",
                         "text_conditioned", "audio_only",
                         "rate_only_estimator")
SOURCE_DECL_FIELDS = ("declared_present", "revision", "license_sha256",
                      "source_sha256")
WEIGHTS_DECL_FIELDS = ("declared_present", "revision", "weights_sha256",
                       "byte_count")
RUNTIME_DECL_FIELDS = ("declared_present", "python_version", "platform",
                       "device", "lock_sha256")
GEOMETRY_DECL_FIELDS = ("declared", "sample_rate_hz", "frame_samples",
                        "hop_samples", "channels")
RIGHTS_DECL_FIELDS = ("code", "weights", "training_data", "inputs",
                      "output_use", "redistribution", "review_reference")
DISPOSITION_DECL_FIELDS = ("decision", "qualifies")


class DeclarationError(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _exact_keys(value: Any, fields: Iterable[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise DeclarationError("not_object", label)
    expected = set(fields)
    actual = set(value)
    if actual - expected:
        raise DeclarationError("unknown_field", label + "." +
                               sorted(actual - expected)[0])
    missing = expected - actual
    if missing:
        raise DeclarationError("missing_field", label + "." +
                               sorted(missing)[0])
    return value


def _bool(value: Any, label: str, expected: bool) -> None:
    if not isinstance(value, bool):
        raise DeclarationError("invalid_boolean", label)
    if value is not expected:
        raise DeclarationError("unverified_claim" if expected is False
                               else "missing_required_value", label)


def _none(value: Any, label: str) -> None:
    if value is not None:
        raise DeclarationError("unverified_claim", label)


def validate_asset_declaration(document: Any) -> dict:
    """Accept only an honest, unpopulated declaration for this candidate.

    Presence claims are rejected because this package cannot verify external
    bytes. A future intake verifies hashes in a separate gate.
    """
    checks = 0
    try:
        assert_no_float(document)
    except TypeError as error:
        raise DeclarationError("float_not_allowed", str(error)) from error
    _exact_keys(document, DECLARATION_FIELDS, "declaration")
    checks += 1
    if document["schema_id"] != DECLARATION_SCHEMA_ID:
        raise DeclarationError("schema_id_mismatch", "schema_id")
    checks += 1
    if not isinstance(document["declaration_id"], str) or \
            not SLUG.fullmatch(document["declaration_id"]):
        raise DeclarationError("invalid_slug", "declaration_id")
    checks += 1

    candidate = _exact_keys(document["candidate"], CANDIDATE_DECL_FIELDS,
                            "candidate")
    if candidate["name"] != CANDIDATE_NAME:
        raise DeclarationError("candidate_name_mismatch", "candidate.name")
    if candidate["family"] != CANDIDATE_FAMILY:
        raise DeclarationError("candidate_family_mismatch", "candidate.family")
    if candidate["paper_reference"] != PAPER_URL:
        raise DeclarationError("paper_reference_mismatch",
                               "candidate.paper_reference")
    _bool(candidate["text_conditioned"], "candidate.text_conditioned", True)
    _bool(candidate["audio_only"], "candidate.audio_only", False)
    _bool(candidate["rate_only_estimator"],
          "candidate.rate_only_estimator", False)
    checks += 6

    source = _exact_keys(document["source"], SOURCE_DECL_FIELDS, "source")
    _bool(source["declared_present"], "source.declared_present", False)
    for name in ("revision", "license_sha256", "source_sha256"):
        _none(source[name], "source." + name)
        checks += 1

    weights = _exact_keys(document["weights"], WEIGHTS_DECL_FIELDS,
                          "weights")
    _bool(weights["declared_present"], "weights.declared_present", False)
    for name in ("revision", "weights_sha256", "byte_count"):
        _none(weights[name], "weights." + name)
        checks += 1

    runtime = _exact_keys(document["runtime"], RUNTIME_DECL_FIELDS,
                          "runtime")
    _bool(runtime["declared_present"], "runtime.declared_present", False)
    for name in ("python_version", "platform", "device", "lock_sha256"):
        _none(runtime[name], "runtime." + name)
        checks += 1

    geometry = _exact_keys(document["geometry"], GEOMETRY_DECL_FIELDS,
                           "geometry")
    _bool(geometry["declared"], "geometry.declared", False)
    for name in ("sample_rate_hz", "frame_samples", "hop_samples",
                 "channels"):
        _none(geometry[name], "geometry." + name)
        checks += 1

    rights = _exact_keys(document["rights"], RIGHTS_DECL_FIELDS, "rights")
    for name in RIGHTS_DECL_FIELDS[:-1]:
        _bool(rights[name], "rights." + name, False)
        checks += 1
    _none(rights["review_reference"], "rights.review_reference")

    disposition = _exact_keys(document["disposition"],
                              DISPOSITION_DECL_FIELDS, "disposition")
    if disposition["decision"] != DECISION:
        raise DeclarationError("premature_decision", "disposition.decision")
    _bool(disposition["qualifies"], "disposition.qualifies", False)
    checks += 2

    return {
        "status": "accepted_unpopulated",
        "checks": checks,
        "qualifies": False,
        "assets_loaded": False,
        "canonical_sha256": object_digest(document),
    }


def declaration_control() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "declaration_id": "neural-atsm-unpopulated-schema-control",
        "candidate": {
            "name": CANDIDATE_NAME,
            "family": CANDIDATE_FAMILY,
            "paper_reference": PAPER_URL,
            "text_conditioned": True,
            "audio_only": False,
            "rate_only_estimator": False,
        },
        "source": {
            "declared_present": False,
            "revision": None,
            "license_sha256": None,
            "source_sha256": None,
        },
        "weights": {
            "declared_present": False,
            "revision": None,
            "weights_sha256": None,
            "byte_count": None,
        },
        "runtime": {
            "declared_present": False,
            "python_version": None,
            "platform": None,
            "device": None,
            "lock_sha256": None,
        },
        "geometry": {
            "declared": False,
            "sample_rate_hz": None,
            "frame_samples": None,
            "hop_samples": None,
            "channels": None,
        },
        "rights": {
            "code": False,
            "weights": False,
            "training_data": False,
            "inputs": False,
            "output_use": False,
            "redistribution": False,
            "review_reference": None,
        },
        "disposition": {"decision": DECISION, "qualifies": False},
    }


def _mutations() -> list[tuple[str, Any]]:
    import copy

    def change(path: tuple[str, ...], value: Any) -> dict:
        document = copy.deepcopy(declaration_control())
        target = document
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return document

    def drop(section: str, key: str) -> dict:
        document = copy.deepcopy(declaration_control())
        del document[section][key]
        return document

    def add(section: str, key: str) -> dict:
        document = copy.deepcopy(declaration_control())
        document[section][key] = None
        return document

    def drop_top(key: str) -> dict:
        document = copy.deepcopy(declaration_control())
        del document[key]
        return document

    return [
        ("root_not_object", []),
        ("root_missing_schema_id", drop_top("schema_id")),
        ("missing_declaration_id", drop_top("declaration_id")),
        ("extra_top_key", change(("extra",), None)),
        ("bad_schema_id", change(("schema_id",), "wrong")),
        ("bad_declaration_id", change(("declaration_id",), "Bad ID")),
        ("wrong_candidate_name", change(("candidate", "name"), "DiffATSM")),
        ("wrong_candidate_family", change(("candidate", "family"),
                                          "raw_audio_diffusion")),
        ("wrong_paper", change(("candidate", "paper_reference"),
                               "https://example.invalid/paper")),
        ("text_conditioned_false",
         change(("candidate", "text_conditioned"), False)),
        ("audio_only_true", change(("candidate", "audio_only"), True)),
        ("rate_only_true",
         change(("candidate", "rate_only_estimator"), True)),
        ("source_present_true", change(("source", "declared_present"), True)),
        ("source_revision_set", change(("source", "revision"), "a" * 40)),
        ("source_license_set",
         change(("source", "license_sha256"), "b" * 64)),
        ("source_digest_set", change(("source", "source_sha256"), "c" * 64)),
        ("weights_present_true",
         change(("weights", "declared_present"), True)),
        ("weights_digest_set",
         change(("weights", "weights_sha256"), "d" * 64)),
        ("weights_bytes_set", change(("weights", "byte_count"), 1)),
        ("runtime_present_true",
         change(("runtime", "declared_present"), True)),
        ("runtime_python_set",
         change(("runtime", "python_version"), REQUIRED_INTERPRETER)),
        ("runtime_platform_set", change(("runtime", "platform"), "macos")),
        ("runtime_lock_set", change(("runtime", "lock_sha256"), "e" * 64)),
        ("geometry_declared_true",
         change(("geometry", "declared"), True)),
        ("geometry_rate_set", change(("geometry", "sample_rate_hz"), 16000)),
        ("geometry_frame_set", change(("geometry", "frame_samples"), 160)),
        ("geometry_hop_set", change(("geometry", "hop_samples"), 160)),
        ("geometry_channels_set", change(("geometry", "channels"), 1)),
        ("rights_code_true", change(("rights", "code"), True)),
        ("rights_weights_true", change(("rights", "weights"), True)),
        ("rights_training_true", change(("rights", "training_data"), True)),
        ("rights_inputs_true", change(("rights", "inputs"), True)),
        ("rights_output_true", change(("rights", "output_use"), True)),
        ("rights_redistribution_true",
         change(("rights", "redistribution"), True)),
        ("rights_review_set",
         change(("rights", "review_reference"), "review-1")),
        ("qualifies_true", change(("disposition", "qualifies"), True)),
        ("premature_admit", change(("disposition", "decision"), "ADMIT")),
        ("missing_weights_section", drop("weights", "declared_present")),
        ("extra_geometry_key", add("geometry", "bit_depth")),
        ("float_value", change(("weights", "byte_count"), 1.5)),
        ("source_not_object", change(("source",), [])),
    ]


def declaration_rejections() -> dict:
    rows: list[dict] = []
    for case_id, document in _mutations():
        try:
            validate_asset_declaration(document)
        except DeclarationError as error:
            rows.append({"id": case_id, "code": error.code,
                         "field": error.field})
        else:
            raise RuntimeError("invalid declaration was accepted: " + case_id)
    return {
        "cases": len(rows),
        "rejections": rows,
        "all_rejected": True,
    }


def strict_json_rejections() -> dict:
    payloads = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_literal", '{"a":NaN}'),
        ("infinity_literal", '{"a":Infinity}'),
        ("negative_infinity_literal", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} trailing'),
        ("byte_order_mark", '\ufeff{"a":1}'),
        ("non_object_root", '[1,2,3]'),
        ("empty_input", "   "),
        ("unterminated", '{"a":'),
    )
    rows: list[dict] = []
    for case_id, payload in payloads:
        try:
            loads_strict(payload)
        except (ValueError, json.JSONDecodeError):
            rows.append({"id": case_id, "rejected": True})
        else:
            raise RuntimeError("strict JSON accepted: " + case_id)
    return {"cases": len(rows), "rejections": rows, "all_rejected": True}


def build_declaration() -> dict:
    valid = validate_asset_declaration(declaration_control())
    rejections = declaration_rejections()
    strict = strict_json_rejections()
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "purpose": "Defines the exact caller-supplied asset declaration a "
                   "future intake must populate and verify externally. This "
                   "package accepts only the unpopulated declaration and "
                   "never resolves or loads an asset.",
        "fields": list(DECLARATION_FIELDS),
        "candidate_fields": list(CANDIDATE_DECL_FIELDS),
        "source_fields": list(SOURCE_DECL_FIELDS),
        "weights_fields": list(WEIGHTS_DECL_FIELDS),
        "runtime_fields": list(RUNTIME_DECL_FIELDS),
        "geometry_fields": list(GEOMETRY_DECL_FIELDS),
        "rights_fields": list(RIGHTS_DECL_FIELDS),
        "disposition_fields": list(DISPOSITION_DECL_FIELDS),
        "accepted_control_sha256": valid["canonical_sha256"],
        "accepted_control_status": valid["status"],
        "accepted_control_checks": valid["checks"],
        "accepted_control_qualifies": valid["qualifies"],
        "presence_claims_rejected": True,
        "assets_loaded": False,
        "rejection_cases": rejections["cases"],
        "rejections": rejections["rejections"],
        "all_rejected": rejections["all_rejected"],
        "strict_json_cases": strict["cases"],
        "strict_json_rejections": strict["rejections"],
        "strict_json_all_rejected": strict["all_rejected"],
    }


# ---------------------------------------------------------------------------
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
    contract = {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "rate_profile": rate_profile(),
        "matched_evidence": matched_evidence(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "asset_declaration_schema": build_declaration(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "absence_summary": absence_summary(),
        "evidence_snippets": evidence_snippet_check(),
        "historical_evidence": [dict(row) for row in HISTORICAL_EVIDENCE],
        "peer_separation": [dict(row) for row in PEER_SEPARATION],
        "non_claims": list(NON_CLAIMS),
    }
    assert_no_float(contract)
    return contract


def build_report() -> dict:
    contract = build_contract()
    contract_digest = object_digest(contract)
    inventory = inventory_record()
    snippets = evidence_snippet_check()
    absence = absence_summary()
    declaration = build_declaration()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "mode": MODE,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "contract_sha256": contract_digest,
        "generated_by": TASK_PREFIX + "run.py",
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "inventory_record": inventory,
        "evidence_presence": {
            "inventory_evidence_path":
                "research/tsm-followup-20261101/README.md",
            "inventory_evidence_line": 37,
            "inventory_evidence_status": inventory["evidence_status"],
            "inventory_disposition": inventory["disposition"],
            "inventory_profile": inventory["verification_profile"],
            "paper_reference_recorded": True,
            "paper_url": PAPER_URL,
            "venue": "Interspeech 2024",
            "source_snapshot_present": False,
            "license_text_present": False,
            "weights_present": False,
            "runtime_present": False,
            "snippet_checks": snippets["checks"],
            "all_snippets_present": snippets["all_present"],
            "snippet_count": snippets["count"],
        },
        "source_reported_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "absence_evidence": absence,
        "runtime_readiness": runtime_readiness(),
        "rate_profile": rate_profile(),
        "matched_evidence": matched_evidence(),
        "asset_declaration": declaration,
        "gates": release_gates(),
        "exact_blockers": exact_blockers(),
        "required_artifacts": required_artifacts(),
        "historical_evidence": [dict(row) for row in HISTORICAL_EVIDENCE],
        "peer_separation": [dict(row) for row in PEER_SEPARATION],
        "non_claims": list(NON_CLAIMS),
        "qualification": qualification_block(),
        "reproduction": {
            "repeat_count": 3,
            "byte_identical": True,
            "interpreter": REQUIRED_INTERPRETER,
            "canonical_json": True,
            "sorted_keys": True,
            "trailing_newline": False,
            "report_sha256_sidecar": "report.json.sha256",
        },
    }
    assert_no_float(report)
    return report


def main() -> int:
    payload, digest = canonical_report(build_report())
    print(payload)
    print("report_sha256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
