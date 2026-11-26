# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local blocker evidence for SDK-NON-STATIONARY-GABOR-TSM.

Standard library only. The catalogued candidate is the non-stationary Gabor
transform time-scale modifier described by Prusa and Holighaus, "Phase vocoder
done right", EUSIPCO 2017. The only local evidence is the pinned research note
that records the idea, calls it research-grade and warns that reference
implementations may be copyleft (LTFAT is GPL-3.0) and should be treated as
papers rather than vendored code.

No reference implementation, LTFAT or NSGT source tree, wheel, binary,
immutable revision, licence text, runtime, audio, corpus, candidate output or
rate measurement is present anywhere probed. Nothing is fabricated,
reconstructed, mirrored, downloaded or substituted.

This module pins the evidence that does exist, proves a fixed absence
inventory, validates fail-closed caller-supplied declarations without
resolving or loading anything, and builds canonical DEFER bytes. It never
transforms, stretches or resamples audio, opens media, times a device or
produces a benchmark result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-NON-STATIONARY-GABOR-TSM"
TASK_TITLE = "Non-stationary Gabor TSM"
COMPONENT_ID = "non-stationary-gabor-tsm"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/non-stationary-gabor-tsm/ only"
TASK_PREFIX = "docs/task-evidence/non-stationary-gabor-tsm/"
CONTRACT_ID = "audio-sdk/non-stationary-gabor-tsm-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/non-stationary-gabor-tsm-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/non-stationary-gabor-tsm-report/0.1"
DECLARATION_SCHEMA_ID = \
    "audio-sdk/non-stationary-gabor-tsm-asset-declaration/0.1"
RATE_REQUEST_SCHEMA_ID = \
    "audio-sdk/non-stationary-gabor-tsm-rate-request/0.1"
BASE_COMMIT = "feb342c735740f32d64a668cf2234e488cdcdbfe"
BRANCH = "swarm/SDK-NON-STATIONARY-GABOR-TSM"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
PAPER_URL = "https://doi.org/10.23919/EUSIPCO.2017.8081353"
CANDIDATE_NAME = "Non-stationary Gabor TSM"
CANDIDATE_FAMILY = "non_stationary_gabor_transform_tsm"
TASK_GEOMETRY_STATE = "plausible_audio_rate_family_unverified"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
CANONICAL_DECIMAL = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]*[1-9])?$")
RATE_MIN = 1
RATE_MAX = 2
RATE_DENOMINATOR = 2

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
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/speech-rate-tsm-evaluation-20261101.md":
        "525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-stretchers/REPORT.md":
        "8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb",
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
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/diffatsm/report.json":
        "8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a",
    "docs/task-evidence/granular-tsm/report.json":
        "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138",
    "docs/task-evidence/usc-mrate/report.json":
        "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246",
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
    "data/checkouts/nsgt",
    "data/checkouts/ltfat",
    "data/checkouts/ltfatpy",
    "data/checkouts/non-stationary-gabor-tsm",
    "data/envs/nsgt",
    "data/envs/ltfat",
    "data/reference/nsgt",
    "data/reference/ltfat",
    "data/audio/nsgt",
    "data/runs/nsgt",
    "research/nsgt",
    "research/non-stationary-gabor-tsm",
)
WORKTREE_PROBES = (
    "adapters/nsgt",
    "schemas/providers/nsgt",
    "third_party/nsgt",
    "third_party/ltfat",
    "build/check-env/lib/python3.12/site-packages/nsgt",
    "build/check-env/lib/python3.12/site-packages/ltfatpy",
)
HOME_PROBES = (
    "~/.cache/nsgt",
    "~/.cache/ltfat",
)

NON_CLAIMS = [
    "No non-stationary Gabor transform, NSGT or LTFAT source, header, wheel, "
    "binary, object, revision, licence text or notice is present, imported, "
    "linked, deserialised or executed.",
    "No FFT, STFT, phase-vocoder, non-stationary Gabor analysis, dual-window, "
    "coefficient modification, synthesis or resampling routine is implemented "
    "or applied to audio by this package.",
    "No audio, corpus, music, speech, synthetic signal, candidate output or "
    "time-scaled waveform is read, generated, stored or scored.",
    "No rate ratio, duration, pitch, transient, preservation, buffering, "
    "listening, device-timing or benchmark result is reproduced.",
    "The caller-supplied declarations are fail-closed shape checks only; they "
    "never resolve a path, hash an external byte, admit a presence claim, "
    "start a transform or grant qualification.",
    "No provider, descriptor, registry, default, public ABI, installed v0 "
    "path, shared build, CI workflow, board or handoff change exists.",
    "The pinned research note and paper DOI are source-reported context only "
    "and are not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
    "No sibling TSM, estimator, sample-rate converter or diffusion package "
    "result, metric or fixture is inherited, pooled or treated as a "
    "non-stationary Gabor result.",
]

HISTORICAL_EVIDENCE = (
    {
        "source": "cpp-library/pipeline-validation/"
                  "playback-speed-candidates.md",
        "section": "5.9",
        "line": 415,
        "class": "source_reported_candidate_note",
        "admitted_as_result": False,
        "boundary": "Records the paper, the non-stationary Gabor idea, a "
                    "research-grade cost/latency note and the warning that "
                    "reference implementations may be copyleft (LTFAT is "
                    "GPL-3.0) and should be treated as papers, not vendored "
                    "code. It contains no source, revision, binary, runtime, "
                    "fixture, output, rate or quality measurement.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks non-stationary-gabor-tsm as considered, "
                    "disposition sdk-reference and verification_profile rate. "
                    "It is a planning record, not a result.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.md",
        "class": "inventory_index",
        "admitted_as_result": False,
        "boundary": "Lists the same row as considered with the pinned "
                    "research note as its only evidence link.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines the Rate profile requirements. No source/output "
                    "mapping, duration, pitch, transient, buffering, rate, "
                    "rebuffer, drift or preservation measurement exists for "
                    "this candidate.",
    },
    {
        "source": "research/tsm-followup-20261101/README.md",
        "class": "sibling_tsm_evaluation_context",
        "admitted_as_result": False,
        "boundary": "Evaluates other stretchers, estimators and neural TSM "
                    "systems. It does not evaluate a non-stationary Gabor "
                    "transform and none of its metrics is inherited here.",
    },
    {
        "source": "research/speech-rate-tsm-evaluation-20261101.md",
        "class": "sibling_rate_context",
        "admitted_as_result": False,
        "boundary": "Screens rate estimators and selected pitch-preserving "
                    "stretchers. It names no non-stationary Gabor reference "
                    "implementation and no value from it is pooled here.",
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
        "boundary": "DiffATSM is a raw-audio diffusion TSM system with its own "
                    "source/checkpoint/runtime blocker. No model, fixture, "
                    "rejection count or metric is inherited or pooled.",
    },
    {
        "component": "granular-tsm",
        "task": "SDK-GRANULAR-TSM",
        "path": "docs/task-evidence/granular-tsm/report.json",
        "class": "separate_granular_tsm_reference",
        "decision": "synthetic-fixture-only",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "Granular TSM is a distinct time-domain grain overlap-add "
                    "reference with its own fixtures and optional provider. No "
                    "grain, schedule, rate case, vector or score is inherited.",
    },
    {
        "component": "usc-mrate",
        "task": "SDK-USC-MRATE",
        "path": "docs/task-evidence/usc-mrate/report.json",
        "class": "separate_rate_estimator",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "USC mrate measures speech rate; it is not a time-scale "
                    "modifier. No corpus, label, metric or blocker count is "
                    "inherited.",
    },
    {
        "component": "libsamplerate",
        "task": "SDK-LIBSAMPLERATE",
        "path": "docs/task-evidence/libsamplerate/report.json",
        "class": "separate_sample_rate_converter",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "libsamplerate changes sample rate and therefore duration "
                    "at a fixed playback rate; it is not a pitch-preserving "
                    "time-scale modifier. No fixture or metric is inherited.",
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
        "source_read": False,
        "audio_read": False,
    }


def runtime_readiness() -> dict:
    return {
        "runtime_present": False,
        "runtime_pinned": False,
        "interpreter_pin": REQUIRED_INTERPRETER,
        "candidate_module_available": False,
        "import_attempted": False,
        "nsgt_reference_present": False,
        "ltfat_reference_present": False,
        "ltfat_license_reported": "GPL-3.0",
        "license_text_staged": False,
        "fft_dependency_pinned": False,
        "numeric_dependency_pinned": False,
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
        "venue": "EUSIPCO 2017",
        "paper_reference": PAPER_URL,
        "paper_title": "Phase vocoder done right",
        "source_reported_method": "non-stationary Gabor transform with "
                                  "time-varying windows and a well-"
                                  "conditioned inverse",
        "source_reported_goal": "principled spectral time-scale "
                                "modification that avoids the usual phase-"
                                "vocoder heuristics",
        "source_reported_stages": [
            "time_varying_analysis_window_schedule",
            "non_stationary_gabor_transform",
            "well_conditioned_inverse",
            "coefficient_or_phase_modification",
            "synthesis_overlap_add",
        ],
        "source_reported_cost": "higher than a plain STFT; research-grade",
        "reference_implementation_recorded": "LTFAT",
        "reference_license_reported": "GPL-3.0",
        "reference_vendorable": False,
        "official_code_found": False,
        "immutable_revision_recorded": False,
        "license_text_staged": False,
        "runnable_as_released": False,
        "source_reported_only": True,
        "identity_verified": False,
    }


def task_geometry() -> dict:
    return {
        "state": TASK_GEOMETRY_STATE,
        "source_reported_input": "audio waveform",
        "source_reported_output": "time-scaled audio waveform",
        "source_reported_transform": "non-stationary Gabor transform with "
                                     "time-varying windows",
        "audio_input_path_verified": False,
        "audio_output_path_verified": False,
        "sample_rate_hz": None,
        "frame_samples": None,
        "hop_samples": None,
        "channels": None,
        "dtype": None,
        "analysis_window_schedule": None,
        "synthesis_window": None,
        "dual_window_rule": None,
        "transform_length": None,
        "latency_ms": None,
        "reset_and_drain_policy": None,
        "geometry_documented": False,
        "geometry_verified": False,
        "rate_profile_fit": "plausible_unverified",
        "profile_fit_reason": "The catalogue and pinned note describe an "
                              "audio-to-audio spectral stretcher, so the Rate "
                              "profile is a plausible family fit. No exact "
                              "sample rate, frame, hop, window schedule, dual "
                              "window, transform length, latency or reset "
                              "policy is recorded, and no reference runtime "
                              "exists, so the geometry is unverified.",
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
                "No non-stationary Gabor reference source, LTFAT runtime, "
                "window schedule, dual-window rule, audio input or candidate "
                "output exists; the item cannot be measured."
                if blocked else
                "The report keeps source-reported, schema-only, missing-real "
                "and sibling sections separate; no category is pooled."),
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
        "candidate_profile_fit": "plausible_unverified",
        "matched_cohort_present": False,
        "matched_baseline_present": False,
        "paired_clean_reference_present": False,
        "source_output_mapping_present": False,
        "same_condition_control_present": False,
        "listening_or_labeled_screen_present": False,
        "evidence_classes": [
            "source_reported_candidate_note",
            "missing_reference_runtime",
            "schema_only_declaration",
            "separate_sibling_candidate",
            "unchanged_v0_contract",
        ],
        "classes_pooled": False,
        "synthetic_schema_control_counted_as_result": False,
        "required_separation": "Source-reported prose, schema-only "
                               "declarations, missing real measurements and "
                               "sibling evidence stay in distinct sections "
                               "and are never pooled.",
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
    if row.get("disposition") != "sdk-reference":
        raise ValueError("inventory_disposition_mismatch")
    if row.get("evidence_status") != "considered":
        raise ValueError("inventory_evidence_status_mismatch")
    plan_note = row.get("plan_note")
    if plan_note != ("Reproduce the chosen technique on exact rate ratios "
                     "before a streaming API claim."):
        raise ValueError("inventory_plan_note_mismatch")
    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "evidence_status": row.get("evidence_status"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
        "plan_note": plan_note,
        "evidence": list(row.get("evidence", [])),
        "evidence_count": len(row.get("evidence", [])),
    }


def evidence_snippet_check() -> dict:
    phrases = (
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "### 5.9 Non-stationary Gabor / \"phase vocoder done right\""),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "Pr\u016f\u0161a & Holighaus"),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "non-stationary Gabor transform with time-varying windows"),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "well-conditioned inverse"),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "higher than a plain STFT; research-grade"),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "LTFAT is GPL-3.0"),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "treat them as papers, not vendored code"),
        ("audio-benchmark-platform/plan/INVENTORY.md",
         "| Non-stationary Gabor TSM | considered"),
        ("audio-benchmark-platform/plan/INVENTORY.json",
         "\"disposition\": \"sdk-reference\""),
        ("audio-benchmark-platform/plan/INVENTORY.json",
         "\"plan_note\": \"Reproduce the chosen technique on exact rate "
         "ratios before a streaming API claim.\""),
        ("audio-benchmark-platform/plan/swarm/VERIFICATION.md",
         "Measure source/output mapping"),
        ("audio-benchmark-platform/plan/swarm/VERIFICATION.md",
         "final partial window"),
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
        "reference_engine_built": False,
        "runtime_imported": False,
        "candidate_code_vendored": False,
        "license_text_vendored": False,
        "audio_added": False,
        "corpus_added": False,
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
        "license_text_vendored": False,
        "runtime_invoked": False,
        "candidate_runtime_executed": False,
        "real_audio": False,
        "synthetic_audio": False,
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
        "candidate_code_license_or_audio_committed": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "sample_format": "float32",
        "unchanged": True,
        "non_stationary_gabor_mapping_present": False,
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
        "summary": "The non-stationary Gabor / 'phase vocoder done right' "
                   "technique is recorded only as a source-reported paper "
                   "note. Locally absent and unverified: official or "
                   "permissively licensed source, LTFAT reference, immutable "
                   "revision, licence text, dependencies, runtime, exact "
                   "window/hop geometry, rights-cleared audio, matched "
                   "cohort, output and rate result.",
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers and gates.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "evidence_register_and_policy_boundary", True,
         "The linked inventory row, pinned Rate acceptance profile, SDK "
         "delivery plan, research note, sibling separation and unchanged v0 "
         "contract boundary."),
        ("ART-02", "exact_reference_source_snapshot", False,
         "An exact non-stationary Gabor reference source tree at an "
         "immutable 40-hex commit or release tag, with reviewed licence "
         "text, README, transform/window definitions and a per-file SHA-256 "
         "manifest."),
        ("ART-03", "nsgt_or_ltfat_runtime_assets", False,
         "Either a permissively licensed NSGT implementation or an isolated "
         "LTFAT runtime with exact package/wheel hashes, FFT and numeric "
         "dependency pins, platform and install location."),
        ("ART-04", "exact_task_geometry", False,
         "The exact audio-in/audio-out contract: sample rate, channels, "
         "frame, hop, analysis window schedule, synthesis/dual windows, "
         "transform length, coefficient/phase mapping, latency, reset and "
         "drain behaviour."),
        ("ART-05", "rights_cleared_terms_and_inputs", False,
         "Code and dependency terms, including the GPL-3.0 implication of "
         "LTFAT, plus a digest-pinned, rights-cleared audio cohort with "
         "acquisition, evaluation, derived-output and redistribution "
         "decisions."),
        ("ART-06", "reproduced_rate_results", False,
         "Deterministic reproduced output on the exact runtime at exact "
         "constants and step/ramp ratios, with duration, pitch, transient, "
         "buffering, silence, rebuffer, drift, final-partial and "
         "preservation measurements plus finite/length/repeat checks."),
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
         "No exact reference source or immutable revision",
         "No NSGT, non-stationary Gabor or LTFAT checkout, wheel, archive, "
         "header, source file, commit, tag or per-file manifest exists at any "
         "probed path. The pinned research note names only the paper and "
         "warns that reference implementations may be copyleft; it records "
         "no repository or revision."),
        ("BLK-02", "ART-03", ["RG-01", "RG-02", "RG-03"],
         "No pinned or clearly licensed runtime",
         "The recorded reference implementation, LTFAT, is reported as "
         "GPL-3.0. No permissive NSGT implementation is identified, no "
         "licence text is staged, and no isolated GPL-compatible runtime, "
         "package lock, FFT/numeric dependency or install location exists. "
         "No module is available to import."),
        ("BLK-03", "ART-04", ["RG-02"],
         "No exact time-varying transform geometry",
         "The note gives no sample rate, channel count, frame, hop, analysis "
         "window schedule, synthesis or dual-window rule, transform length, "
         "coefficient/phase mapping, latency, reset or drain policy. The "
         "audio-in/audio-out family is plausible but the task geometry is "
         "unverified."),
        ("BLK-04", "ART-05", ["RG-04"],
         "No reviewed rights or rights-cleared audio",
         "No code licence text, dependency notice, GPL-3.0 distribution "
         "decision, corpus permission, output-use grant or redistribution "
         "review is staged. No rights-cleared speech or music input exists."),
        ("BLK-05", "ART-06", ["RG-05", "RG-06"],
         "No reproduced rate or output result",
         "No candidate execution, output hash, source/output mapping, 1x "
         "control, constant ratio, step/ramp ratio, duration, pitch, "
         "transient, buffering, silence, rebuffer, drift, final-partial or "
         "speech-preservation result exists."),
        ("BLK-06", "ART-07", ["RG-07", "RG-08"],
         "No listening, timing, provider intake or release evidence",
         "No authorized listening or labeled screen, device timing, resource "
         "measurement, matched cohort, benchmark, OFF-by-default provider "
         "intake or independent review exists."),
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
     "Stage an exact reference source at an immutable revision with complete "
     "licence, notice and README records, and record an independent review "
     "including the GPL-3.0 implication."),
    ("pinned_runtime_and_offline_install",
     "Provide a locked offline runtime with package/wheel hashes, FFT and "
     "numeric dependency pins, install location and clean-room import "
     "digest."),
    ("transform_assets_and_dependencies",
     "Stage the NSGT or isolated LTFAT transform assets and verify every "
     "window schedule, dual-window, FFT and dependency byte count and "
     "SHA-256."),
    ("rights_cleared_terms_and_inputs",
     "Freeze permitted, digest-pinned audio inputs with corpus, evaluation, "
     "derived-output and redistribution decisions plus code and dependency "
     "terms."),
    ("reference_execution_and_output_validity",
     "Execute the pinned reference offline and record output hashes, finite "
     "and length behaviour, exact repeats, peak/RSS and identity-control "
     "values."),
    ("rate_profile_against_real_runtime",
     "Run every Rate-profile case on a rights-cleared cohort with 1x, exact "
     "constant ratios, step/ramp changes, unfamiliar speech, music, "
     "silence, rebuffer, drift and the final partial window."),
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
        "statement": "No non-stationary Gabor artifact, runtime, right, "
                     "matched measurement or review satisfies this "
                     "requirement.",
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
        "reference_implementation_present": False,
        "license_text_present": False,
        "rights_cleared": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "geometry_verified": False,
        "input_media_present": False,
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
        "reason": "Reference source, permissive or isolated reference "
                  "runtime, exact geometry, reviewed terms, rights-cleared "
                  "inputs, matched cohort, reproduced output and independent "
                  "review are all absent. The GPL-3.0 LTFAT note is a "
                  "rights blocker, not a vendorable asset.",
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset declaration. Shape only; it never
# resolves a path, hashes an external byte, loads a reference or admits a
# claim.
# ---------------------------------------------------------------------------

DECLARATION_FIELDS = ("schema_id", "declaration_id", "candidate", "source",
                      "reference", "dependencies", "geometry", "rights",
                      "disposition")
CANDIDATE_DECL_FIELDS = ("name", "family", "paper_reference",
                         "audio_in_audio_out", "paper_only")
SOURCE_DECL_FIELDS = ("declared_present", "revision", "license_sha256",
                      "source_sha256")
REFERENCE_DECL_FIELDS = ("declared_present", "implementation", "revision",
                         "license_id", "license_text_sha256",
                         "binary_sha256")
DEPENDENCY_DECL_FIELDS = ("declared_present", "packages", "lock_sha256")
GEOMETRY_DECL_FIELDS = ("declared", "sample_rate_hz", "frame_samples",
                        "hop_samples", "channels", "window_schedule_sha256",
                        "dual_window_sha256")
RIGHTS_DECL_FIELDS = ("code", "reference", "inputs", "output_use",
                      "redistribution", "review_reference")
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
    _bool(candidate["audio_in_audio_out"],
          "candidate.audio_in_audio_out", True)
    _bool(candidate["paper_only"], "candidate.paper_only", True)
    checks += 5

    source = _exact_keys(document["source"], SOURCE_DECL_FIELDS, "source")
    _bool(source["declared_present"], "source.declared_present", False)
    for name in ("revision", "license_sha256", "source_sha256"):
        _none(source[name], "source." + name)
        checks += 1

    reference = _exact_keys(document["reference"], REFERENCE_DECL_FIELDS,
                            "reference")
    _bool(reference["declared_present"], "reference.declared_present", False)
    if reference["implementation"] != "ltfat":
        raise DeclarationError("reference_implementation_mismatch",
                               "reference.implementation")
    for name in ("revision", "license_id", "license_text_sha256",
                 "binary_sha256"):
        _none(reference[name], "reference." + name)
        checks += 1

    dependencies = _exact_keys(document["dependencies"],
                               DEPENDENCY_DECL_FIELDS, "dependencies")
    _bool(dependencies["declared_present"],
          "dependencies.declared_present", False)
    if dependencies["packages"] != []:
        raise DeclarationError("unverified_claim", "dependencies.packages")
    _none(dependencies["lock_sha256"], "dependencies.lock_sha256")
    checks += 2

    geometry = _exact_keys(document["geometry"], GEOMETRY_DECL_FIELDS,
                           "geometry")
    _bool(geometry["declared"], "geometry.declared", False)
    for name in GEOMETRY_DECL_FIELDS[1:]:
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
        "declaration_id": "non-stationary-gabor-tsm-unpopulated-control",
        "candidate": {
            "name": CANDIDATE_NAME,
            "family": CANDIDATE_FAMILY,
            "paper_reference": PAPER_URL,
            "audio_in_audio_out": True,
            "paper_only": True,
        },
        "source": {
            "declared_present": False,
            "revision": None,
            "license_sha256": None,
            "source_sha256": None,
        },
        "reference": {
            "declared_present": False,
            "implementation": "ltfat",
            "revision": None,
            "license_id": None,
            "license_text_sha256": None,
            "binary_sha256": None,
        },
        "dependencies": {
            "declared_present": False,
            "packages": [],
            "lock_sha256": None,
        },
        "geometry": {
            "declared": False,
            "sample_rate_hz": None,
            "frame_samples": None,
            "hop_samples": None,
            "channels": None,
            "window_schedule_sha256": None,
            "dual_window_sha256": None,
        },
        "rights": {
            "code": False,
            "reference": False,
            "inputs": False,
            "output_use": False,
            "redistribution": False,
            "review_reference": None,
        },
        "disposition": {"decision": DECISION, "qualifies": False},
    }


def _declaration_mutations() -> list[tuple[str, Any]]:
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
        ("wrong_candidate_name", change(("candidate", "name"), "Granular TSM")),
        ("wrong_candidate_family", change(("candidate", "family"),
                                          "granular_tsm")),
        ("wrong_paper", change(("candidate", "paper_reference"),
                               "https://example.invalid/paper")),
        ("audio_in_audio_out_false",
         change(("candidate", "audio_in_audio_out"), False)),
        ("paper_only_false", change(("candidate", "paper_only"), False)),
        ("source_present_true", change(("source", "declared_present"), True)),
        ("source_revision_set", change(("source", "revision"), "a" * 40)),
        ("source_license_set",
         change(("source", "license_sha256"), "b" * 64)),
        ("source_digest_set", change(("source", "source_sha256"), "c" * 64)),
        ("reference_present_true",
         change(("reference", "declared_present"), True)),
        ("reference_implementation_wrong",
         change(("reference", "implementation"), "nsgt")),
        ("reference_revision_set",
         change(("reference", "revision"), "d" * 40)),
        ("reference_license_set",
         change(("reference", "license_id"), "GPL-3.0")),
        ("reference_license_text_set",
         change(("reference", "license_text_sha256"), "e" * 64)),
        ("reference_binary_set",
         change(("reference", "binary_sha256"), "f" * 64)),
        ("dependencies_present_true",
         change(("dependencies", "declared_present"), True)),
        ("dependencies_packages_set",
         change(("dependencies", "packages"), ["ltfatpy"])),
        ("dependencies_lock_set",
         change(("dependencies", "lock_sha256"), "1" * 64)),
        ("geometry_declared_true", change(("geometry", "declared"), True)),
        ("geometry_rate_set", change(("geometry", "sample_rate_hz"), 16000)),
        ("geometry_frame_set", change(("geometry", "frame_samples"), 160)),
        ("geometry_hop_set", change(("geometry", "hop_samples"), 160)),
        ("geometry_channels_set", change(("geometry", "channels"), 1)),
        ("geometry_window_set",
         change(("geometry", "window_schedule_sha256"), "2" * 64)),
        ("geometry_dual_window_set",
         change(("geometry", "dual_window_sha256"), "3" * 64)),
        ("rights_code_true", change(("rights", "code"), True)),
        ("rights_reference_true", change(("rights", "reference"), True)),
        ("rights_inputs_true", change(("rights", "inputs"), True)),
        ("rights_output_true", change(("rights", "output_use"), True)),
        ("rights_redistribution_true",
         change(("rights", "redistribution"), True)),
        ("rights_review_set",
         change(("rights", "review_reference"), "review-1")),
        ("qualifies_true", change(("disposition", "qualifies"), True)),
        ("premature_admit", change(("disposition", "decision"), "ADMIT")),
        ("missing_reference_section", drop("reference", "declared_present")),
        ("extra_geometry_key", add("geometry", "bit_depth")),
        ("float_value", change(("geometry", "sample_rate_hz"), 16000.0)),
        ("source_not_object", change(("source",), [])),
    ]


def declaration_rejections() -> dict:
    rows: list[dict] = []
    for case_id, document in _declaration_mutations():
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
        "reference_fields": list(REFERENCE_DECL_FIELDS),
        "dependency_fields": list(DEPENDENCY_DECL_FIELDS),
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
# Fail-closed rate-request schema. It validates exact-adverse inputs and then
# still defers because the reference runtime and audio are absent. It never
# reads, transforms, resamples or scores audio.
# ---------------------------------------------------------------------------

RATE_REQUEST_FIELDS = ("schema_id", "request_id", "input", "rate", "runtime",
                       "disposition")
INPUT_FIELDS = ("declared_present", "sample_rate_hz", "channels",
                "frame_samples", "frame_count", "sha256")
RATE_FIELDS = ("ratio", "mode", "schedule")
SCHEDULE_FIELDS = ("at_source_sample", "ratio")
RATE_RUNTIME_FIELDS = ("declared_present", "implementation", "revision",
                       "lock_sha256")
RATE_MODES = ("constant", "step", "ramp")


class RateRequestError(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _rate_value(value: Any, label: str) -> int:
    """Return the ratio in half-units, rejecting noncanonical or nonfinite."""
    if value is None:
        raise RateRequestError("missing_rate", label)
    if not isinstance(value, str):
        raise RateRequestError("rate_not_canonical_string", label)
    if value.lower() in ("nan", "inf", "+inf", "-inf", "infinity",
                         "-infinity"):
        raise RateRequestError("nonfinite_rate", label)
    if CANONICAL_DECIMAL.fullmatch(value) is None:
        raise RateRequestError("rate_not_canonical", label)
    whole, _, fraction = value.partition(".")
    if fraction and fraction.endswith("0"):
        raise RateRequestError("rate_redundant_zero", label)
    units = int(whole) * RATE_DENOMINATOR
    if fraction:
        units += int((fraction + "00")[:2])
        if len(fraction) > 2:
            raise RateRequestError("rate_too_precise", label)
    if units < RATE_MIN * RATE_DENOMINATOR or \
            units > RATE_MAX * RATE_DENOMINATOR:
        raise RateRequestError("rate_out_of_range", label)
    return units


def validate_rate_request(document: Any) -> dict:
    """Validate an exact rate request, then defer without executing.

    The package cannot verify input bytes or a reference runtime, so even a
    structurally valid unpopulated request returns a non-qualifying DEFER.
    """
    try:
        return _validate_rate_request(document)
    except DeclarationError as error:
        raise RateRequestError(error.code, error.field) from error


def _validate_rate_request(document: Any) -> dict:
    checks = 0
    try:
        assert_no_float(document)
    except TypeError as error:
        raise RateRequestError("float_not_allowed", str(error)) from error
    _exact_keys(document, RATE_REQUEST_FIELDS, "request")
    checks += 1
    if document["schema_id"] != RATE_REQUEST_SCHEMA_ID:
        raise RateRequestError("schema_id_mismatch", "schema_id")
    checks += 1
    if not isinstance(document["request_id"], str) or \
            not SLUG.fullmatch(document["request_id"]):
        raise RateRequestError("invalid_slug", "request_id")
    checks += 1

    audio_input = _exact_keys(document["input"], INPUT_FIELDS, "input")
    _bool(audio_input["declared_present"], "input.declared_present", False)
    for name in INPUT_FIELDS[1:]:
        _none(audio_input[name], "input." + name)
        checks += 1

    rate = _exact_keys(document["rate"], RATE_FIELDS, "rate")
    ratio_units = _rate_value(rate["ratio"], "rate.ratio")
    checks += 1
    if rate["mode"] not in RATE_MODES:
        raise RateRequestError("invalid_rate_mode", "rate.mode")
    checks += 1
    schedule = rate["schedule"]
    if not isinstance(schedule, list) or not schedule:
        raise RateRequestError("invalid_schedule", "rate.schedule")
    previous = -1
    for index, point in enumerate(schedule):
        label = "rate.schedule.%d" % index
        _exact_keys(point, SCHEDULE_FIELDS, label)
        position = point["at_source_sample"]
        if not isinstance(position, int) or isinstance(position, bool) or \
                position < 0:
            raise RateRequestError("invalid_schedule_position",
                                   label + ".at_source_sample")
        if position <= previous:
            raise RateRequestError("non_increasing_schedule",
                                   label + ".at_source_sample")
        if index == 0 and position != 0:
            raise RateRequestError("schedule_must_start_at_zero",
                                   label + ".at_source_sample")
        _rate_value(point["ratio"], label + ".ratio")
        previous = position
        checks += 2
    if rate["mode"] == "constant" and len(schedule) != 1:
        raise RateRequestError("constant_schedule_not_one_point",
                               "rate.schedule")
    if rate["mode"] in ("step", "ramp") and len(schedule) < 2:
        raise RateRequestError("dynamic_schedule_too_short", "rate.schedule")
    checks += 2

    runtime = _exact_keys(document["runtime"], RATE_RUNTIME_FIELDS,
                          "runtime")
    _bool(runtime["declared_present"], "runtime.declared_present", False)
    if runtime["implementation"] != "ltfat":
        raise RateRequestError("runtime_implementation_mismatch",
                               "runtime.implementation")
    for name in ("revision", "lock_sha256"):
        _none(runtime[name], "runtime." + name)
        checks += 1

    disposition = _exact_keys(document["disposition"],
                              DISPOSITION_DECL_FIELDS, "disposition")
    if disposition["decision"] != DECISION:
        raise RateRequestError("premature_decision",
                               "disposition.decision")
    _bool(disposition["qualifies"], "disposition.qualifies", False)
    checks += 2

    return {
        "status": "deferred_missing_reference",
        "checks": checks,
        "ratio_units": ratio_units,
        "executed": False,
        "audio_read": False,
        "transform_applied": False,
        "qualifies": False,
        "canonical_sha256": object_digest(document),
    }


def rate_request_control() -> dict:
    return {
        "schema_id": RATE_REQUEST_SCHEMA_ID,
        "request_id": "non-stationary-gabor-tsm-unpopulated-rate-control",
        "input": {
            "declared_present": False,
            "sample_rate_hz": None,
            "channels": None,
            "frame_samples": None,
            "frame_count": None,
            "sha256": None,
        },
        "rate": {
            "ratio": "1",
            "mode": "constant",
            "schedule": [{"at_source_sample": 0, "ratio": "1"}],
        },
        "runtime": {
            "declared_present": False,
            "implementation": "ltfat",
            "revision": None,
            "lock_sha256": None,
        },
        "disposition": {"decision": DECISION, "qualifies": False},
    }


def _rate_request_mutations() -> list[tuple[str, Any]]:
    import copy

    def change(path: tuple[str, ...], value: Any) -> dict:
        document = copy.deepcopy(rate_request_control())
        target = document
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return document

    def drop(section: str, key: str) -> dict:
        document = copy.deepcopy(rate_request_control())
        del document[section][key]
        return document

    def drop_top(key: str) -> dict:
        document = copy.deepcopy(rate_request_control())
        del document[key]
        return document

    return [
        ("root_not_object", []),
        ("missing_schema_id", drop_top("schema_id")),
        ("missing_request_id", drop_top("request_id")),
        ("missing_input_section", drop_top("input")),
        ("missing_rate_section", drop_top("rate")),
        ("missing_runtime_section", drop_top("runtime")),
        ("missing_disposition_section", drop_top("disposition")),
        ("extra_top_key", change(("extra",), None)),
        ("bad_schema_id", change(("schema_id",), "wrong")),
        ("bad_request_id", change(("request_id",), "Bad ID")),
        ("input_present_true", change(("input", "declared_present"), True)),
        ("input_rate_set", change(("input", "sample_rate_hz"), 16000)),
        ("input_channels_set", change(("input", "channels"), 1)),
        ("input_frame_set", change(("input", "frame_samples"), 160)),
        ("input_count_set", change(("input", "frame_count"), 1)),
        ("input_digest_set", change(("input", "sha256"), "a" * 64)),
        ("missing_input_key", drop("input", "sha256")),
        ("input_not_object", change(("input",), [])),
        ("rate_missing_ratio", drop("rate", "ratio")),
        ("rate_missing_mode", drop("rate", "mode")),
        ("rate_missing_schedule", drop("rate", "schedule")),
        ("rate_null", change(("rate", "ratio"), None)),
        ("rate_integer", change(("rate", "ratio"), 1)),
        ("rate_float", change(("rate", "ratio"), 1.0)),
        ("rate_nan_lower", change(("rate", "ratio"), "nan")),
        ("rate_nan_mixed", change(("rate", "ratio"), "NaN")),
        ("rate_infinity", change(("rate", "ratio"), "Infinity")),
        ("rate_negative_infinity",
         change(("rate", "ratio"), "-Infinity")),
        ("rate_inf", change(("rate", "ratio"), "inf")),
        ("rate_empty", change(("rate", "ratio"), "")),
        ("rate_zero", change(("rate", "ratio"), "0")),
        ("rate_negative", change(("rate", "ratio"), "-1")),
        ("rate_exponent", change(("rate", "ratio"), "1e0")),
        ("rate_plus", change(("rate", "ratio"), "+1")),
        ("rate_leading_zero", change(("rate", "ratio"), "01")),
        ("rate_redundant_zero", change(("rate", "ratio"), "1.00")),
        ("rate_below_range", change(("rate", "ratio"), "0.25")),
        ("rate_above_range", change(("rate", "ratio"), "2.5")),
        ("rate_far_above_range", change(("rate", "ratio"), "3")),
        ("mode_invalid", change(("rate", "mode"), "speed")),
        ("schedule_empty", change(("rate", "schedule"), [])),
        ("schedule_not_list", change(("rate", "schedule"), {})),
        ("schedule_item_not_object",
         change(("rate", "schedule"), ["1"])),
        ("schedule_extra_key",
         change(("rate", "schedule"),
                [{"at_source_sample": 0, "ratio": "1", "extra": 1}])),
        ("schedule_first_not_zero",
         change(("rate", "schedule"),
                [{"at_source_sample": 1, "ratio": "1"}])),
        ("schedule_negative_position",
         change(("rate", "schedule"),
                [{"at_source_sample": -1, "ratio": "1"}])),
        ("schedule_float_position",
         change(("rate", "schedule"),
                [{"at_source_sample": 0.0, "ratio": "1"}])),
        ("schedule_nonincreasing",
         change(("rate", "schedule"),
                [{"at_source_sample": 0, "ratio": "1"},
                 {"at_source_sample": 0, "ratio": "1"}])),
        ("schedule_ratio_bad",
         change(("rate", "schedule"),
                [{"at_source_sample": 0, "ratio": "nan"}])),
        ("constant_schedule_two_points",
         change(("rate", "schedule"),
                [{"at_source_sample": 0, "ratio": "1"},
                 {"at_source_sample": 160, "ratio": "1"}])),
        ("dynamic_schedule_one_point",
         change(("rate", "mode"), "step")),
        ("runtime_present_true",
         change(("runtime", "declared_present"), True)),
        ("runtime_implementation_wrong",
         change(("runtime", "implementation"), "nsgt")),
        ("runtime_revision_set", change(("runtime", "revision"), "b" * 40)),
        ("runtime_lock_set",
         change(("runtime", "lock_sha256"), "c" * 64)),
        ("qualifies_true", change(("disposition", "qualifies"), True)),
        ("premature_admit", change(("disposition", "decision"), "ADMIT")),
        ("extra_disposition_key", change(("disposition", "extra"), None)),
    ]


def rate_request_rejections() -> dict:
    rows: list[dict] = []
    for case_id, document in _rate_request_mutations():
        try:
            validate_rate_request(document)
        except RateRequestError as error:
            rows.append({"id": case_id, "code": error.code,
                         "field": error.field})
        else:
            raise RuntimeError("invalid rate request was accepted: " + case_id)
    return {
        "cases": len(rows),
        "rejections": rows,
        "all_rejected": True,
    }


def build_rate_request() -> dict:
    valid = validate_rate_request(rate_request_control())
    rejected = rate_request_rejections()
    return {
        "schema_id": RATE_REQUEST_SCHEMA_ID,
        "purpose": "Defines an exact rate-ratio request shape for a future "
                   "intake. Every structurally valid request still returns "
                   "DEFER because no reference runtime or audio is present. "
                   "No audio is read and no transform is applied.",
        "fields": list(RATE_REQUEST_FIELDS),
        "input_fields": list(INPUT_FIELDS),
        "rate_fields": list(RATE_FIELDS),
        "schedule_fields": list(SCHEDULE_FIELDS),
        "runtime_fields": list(RATE_RUNTIME_FIELDS),
        "modes": list(RATE_MODES),
        "ratio_min": "0.5",
        "ratio_max": "2",
        "canonical_ratio_only": True,
        "nonfinite_rejected": True,
        "accepted_control_sha256": valid["canonical_sha256"],
        "accepted_control_status": valid["status"],
        "accepted_control_checks": valid["checks"],
        "accepted_control_qualifies": valid["qualifies"],
        "accepted_control_executed": valid["executed"],
        "rejection_cases": rejected["cases"],
        "rejections": rejected["rejections"],
        "all_rejected": rejected["all_rejected"],
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
        "rate_request_schema": build_rate_request(),
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
    rate_request = build_rate_request()
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
                "cpp-library/pipeline-validation/"
                "playback-speed-candidates.md",
            "inventory_evidence_section": "5.9",
            "inventory_evidence_line": 415,
            "inventory_evidence_status": inventory["evidence_status"],
            "inventory_disposition": inventory["disposition"],
            "inventory_profile": inventory["verification_profile"],
            "inventory_plan_note": inventory["plan_note"],
            "paper_reference_recorded": True,
            "paper_url": PAPER_URL,
            "venue": "EUSIPCO 2017",
            "source_snapshot_present": False,
            "license_text_present": False,
            "reference_runtime_present": False,
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
        "rate_request": rate_request,
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
