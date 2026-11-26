# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local readiness evidence for SDK-DiffSE.

Standard library only. The catalogued candidate is SNR-Aligned Consistent
Diffusion (DiffSE): an SNR-conditioned one-step consistency diffusion
enhancer. The pinned census names an official repository, a paper, reported
metrics and Drive-folder checkpoints, but no source snapshot, checkpoint byte,
SNR estimator, runtime, licence text, rights-cleared cohort or local result is
present anywhere probed.

This module pins the evidence that does exist, validates a fail-closed
caller-supplied asset declaration without resolving, importing, loading or
executing anything, and builds canonical DEFER bytes. It never runs diffusion,
enhances audio, synthesises a waveform, opens media, performs listening, times
a device or produces a benchmark result.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE"
TASK_TITLE = "SNR-Aligned Consistent Diffusion (DiffSE)"
COMPONENT_ID = "snr-aligned-consistent-diffusion-diffse"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"
WRITE_SCOPE = "docs/task-evidence/snr-aligned-consistent-diffusion-diffse/ only"
TASK_PREFIX = "docs/task-evidence/snr-aligned-consistent-diffusion-diffse/"
CONTRACT_ID = "audio-sdk/diffse-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/diffse-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/diffse-report/0.1"
DECLARATION_SCHEMA_ID = "audio-sdk/diffse-caller-asset/0.1"
BASE_COMMIT = "f93d25f3d455a4278030d1bf0a3338dc6f8b95fe"
BRANCH = "swarm/SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE"
OWNER = "agent-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE"
REVIEWER = "reviewer-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
SOURCE_REPOSITORY = "https://github.com/yh-jun/SNR-Aligned_diffSE"
PAPER_URL = "https://hi.snu.ac.kr/wp-content/uploads/sites/103/2025/09/jun25_interspeech.pdf"
CANDIDATE_NAME = "SNR-Aligned Consistent Diffusion (DiffSE)"
CANDIDATE_FAMILY = "snr_conditioned_one_step_consistency_diffusion"
TASK_GEOMETRY_STATE = "unverified_offline_diffusion_geometry_and_snr_estimator"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PACKAGE = re.compile(r"^[A-Za-z0-9_.+-]+==[A-Za-z0-9_.+-]+$")
SOURCE_PYTHON = re.compile(r"^3\.8\.[0-9]+$")
SAFE_BASENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

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
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
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
INVENTORY_REL = "audio-benchmark-platform/plan/INVENTORY.json"
INVENTORY_MD_REL = "audio-benchmark-platform/plan/INVENTORY.md"
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
CENSUS_REL = "research/noise_suppression_candidate_census.md"
CONTRACT_SOURCE_REL = "audio-benchmark-platform/audio-sdk/CONTRACTS.md"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

EVIDENCE_SNIPPETS = (
    {
        "id": "SNP-01",
        "path": CENSUS_REL,
        "line": 36,
        "contains": (
            "SNR-Aligned Consistent Diffusion (DiffSE)",
            "SNR-conditioned, one-step consistency diffusion enhancement",
            "Python 3.8",
            "Drive-folder checkpoints",
            "Input-SNR estimation is required outside oracle-SNR conditions",
            "upstream SGMSE MIT license",
        ),
    },
    {
        "id": "SNP-02",
        "path": INVENTORY_MD_REL,
        "line": 208,
        "contains": (
            "SNR-Aligned Consistent Diffusion (DiffSE)",
            TASK,
        ),
    },
    {
        "id": "SNP-03",
        "path": PROFILE_SOURCE_REL,
        "line": 16,
        "contains": PROFILE_PHRASES,
    },
    {
        "id": "SNP-04",
        "path": CONTRACT_SOURCE_REL,
        "line": 15,
        "contains": (
            "as_asset_v0",
            "The descriptor declares every external asset",
            "caller supplies exactly those assets",
            "Embedded assets are not supported by contract 0.1",
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
WEIGHT_SUFFIXES = (".pt", ".pth", ".ckpt", ".safetensors", ".bin")


# ---------------------------------------------------------------------------
# Canonical bytes and strict JSON.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
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
    return parse_strict_json_text(Path(path).read_bytes())


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


def strict_json_rejections() -> dict:
    texts = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "negative_infinity_constant": '{"a":-Infinity}',
        "trailing_data": '{"a":1} trailing',
        "invalid_syntax": '{"a":}',
        "empty_text": "",
        "float_value": '{"a":1.5}',
        "root_array": '[1,2]',
        "nested_float": '{"a":{"b":2.25}}',
    }
    cases: list[dict] = []
    for name, text in texts.items():
        try:
            loads_strict(text)
            observed = "UNEXPECTED_ACCEPT"
        except (ValueError, TypeError):
            observed = "REJECTED"
        cases.append({"id": name, "observed": observed,
                      "rejected": observed == "REJECTED"})
    return {
        "case_count": len(cases),
        "cases": cases,
        "rejection_cases": sum(1 for item in cases if item["rejected"]),
    }


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
    if not isinstance(depends_on, list) or any(
            not isinstance(item, str) for item in depends_on):
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
    matches = [row for row in _board_tasks(path) if row.get("id") == TASK]
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
# Git scope helpers. Newest merge-base across origin/main then main.
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
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None when no base ref exists or when available bases are not
    ordered by ancestry. The verifier treats None as a fail-closed condition.
    """
    bases: list[str] = []
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        value = result.stdout.strip()
        if result.returncode == 0 and HEX40.match(value):
            bases.append(value)
    unique = list(dict.fromkeys(bases))
    if not unique:
        return None
    if len(unique) == 1:
        return unique[0]
    for candidate in unique:
        others = [item for item in unique if item != candidate]
        if all(_git(worktree, "merge-base", "--is-ancestor", other,
                    candidate).returncode == 0 for other in others):
            return candidate
    return None


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "HEAD")
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
        _probe(root / "data/checkouts/SNR-Aligned_diffSE",
               "workspace-checkout-upper", "workspace",
               "data/checkouts/SNR-Aligned_diffSE"),
        _probe(root / "data/checkouts/snraligned-diffse",
               "workspace-checkout-slug", "workspace",
               "data/checkouts/snraligned-diffse"),
        _probe(root / "data/models/diffse", "workspace-model-slug",
               "workspace", "data/models/diffse"),
        _probe(root / "data/models/SNR-Aligned_diffSE", "workspace-model-upper",
               "workspace", "data/models/SNR-Aligned_diffSE"),
        _probe(root / "third_party/SNR-Aligned_diffSE",
               "workspace-third-party", "workspace",
               "third_party/SNR-Aligned_diffSE"),
        _probe(root / "research/diffse", "workspace-research", "workspace",
               "research/diffse"),
        _probe(root / "research/vendor/SNR-Aligned_diffSE",
               "workspace-research-vendor", "workspace",
               "research/vendor/SNR-Aligned_diffSE"),
    ]


def worktree_probes() -> list[dict]:
    names = (
        ("source", "worktree-source"),
        ("checkpoints", "worktree-checkpoints"),
        ("weights", "worktree-weights"),
        ("runtime", "worktree-runtime"),
        ("snr_est", "worktree-snr-estimator"),
    )
    return [
        _probe(HERE / name, label, "worktree", TASK_PREFIX + name)
        for name, label in names
    ]


def home_probes() -> list[dict]:
    home = Path.home()
    names = (
        (".cache/huggingface/hub/models--yh-jun--SNR-Aligned_diffSE",
         "home-hf-diffse"),
        (".cache/huggingface/hub/models--yh-jun--SNR-Aligned_diffSE-snr-est",
         "home-hf-diffse-snr-est"),
        (".cache/torch/hub/checkpoints/diffse.pt", "home-torch-diffse-pt"),
        (".cache/torch/hub/checkpoints/diffse.ckpt", "home-torch-diffse-ckpt"),
        (".cache/torch/hub/checkpoints/snr_est.pt", "home-torch-snr-est"),
        ("SNR-Aligned_diffSE", "home-diffse-upper"),
        ("diffse", "home-diffse-slug"),
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
        "home_probe_count": sum(1 for row in rows if row["kind"] == "home"),
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


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-DiffSE task-local evidence.",
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
        rows: list[tuple[str, str]] = []
        for line in text[start:end].splitlines():
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
    lines: list[str] = ["", ]
    if section == "source":
        lines.append("| Source pin | SHA-256 |")
        lines.append("| --- | --- |")
        for relative in sorted(SOURCE_PINS):
            lines.append("| `source:%s` | `%s` |" %
                         (relative, sha256_file(AUDIO_ROOT / relative)))
    elif section == "boundary":
        lines.append("| Boundary pin | SHA-256 |")
        lines.append("| --- | --- |")
        for relative in sorted(BOUNDARY_PINS):
            lines.append("| `sdk:%s` | `%s` |" %
                         (relative, sha256_file(WORKTREE / relative)))
    elif section == "artifacts":
        lines.append("| Path | SHA-256 | Bytes |")
        lines.append("| --- | --- | ---: |")
        for name in SOURCE_ARTIFACT_FILES:
            path = HERE / name
            lines.append("| `%s` | `%s` | %d |" %
                         (name, sha256_file(path), path.stat().st_size))
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
        lines = _read_text(snippet["path"]).splitlines()
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
    if entry.get("path") != CENSUS_REL or entry.get("line") != 36:
        raise ValueError("inventory_evidence_link_mismatch")
    if entry.get("record_name") != CANDIDATE_NAME or \
            entry.get("finding") != \
            "SNR-conditioned, one-step consistency diffusion enhancement":
        raise ValueError("inventory_evidence_text_mismatch")
    return {
        "aliases": list(record.get("aliases") or []),
        "area": record["area"],
        "disposition": record["disposition"],
        "evidence_finding": entry["finding"],
        "evidence_line": entry["line"],
        "evidence_path": entry["path"],
        "evidence_record_name": entry["record_name"],
        "evidence_status": record["evidence_status"],
        "id": record["id"],
        "name": record["name"],
        "repository": record["repository"],
        "task": record["task"],
        "verification_profile": record["verification_profile"],
    }


def profile_row_check() -> dict:
    rows = [line for line in _read_text(PROFILE_SOURCE_REL).splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        raise ValueError("profile_row_count:" + str(len(rows)))
    present = [phrase for phrase in PROFILE_PHRASES if phrase in rows[0]]
    return {
        "all_phrases_present": len(present) == len(PROFILE_PHRASES),
        "path": PROFILE_SOURCE_REL,
        "phrases_present": present,
        "row_count": len(rows),
        "unique_row": True,
    }


# ---------------------------------------------------------------------------
# Report blocks.
# ---------------------------------------------------------------------------


def source_reported_identity() -> dict:
    return {
        "admitted_as_result": False,
        "checkpoint_bytes": None,
        "checkpoint_file": None,
        "checkpoint_sha256": None,
        "checkpoint_variant": None,
        "locally_present": False,
        "model_repository": SOURCE_REPOSITORY,
        "model_revision": None,
        "note": (
            "The pinned census reports a 2025 paper/repository, M4-M6 "
            "results, baseline checkpoints and Drive-folder checkpoints. No "
            "commit, file name, byte count, SHA-256, runtime lock, reviewed "
            "licence text, model card or local metric is recorded here."),
        "paper_url": PAPER_URL,
        "qualifies": False,
        "reported_approach": (
            "SNR-conditioned, one-step consistency diffusion enhancement"),
        "reported_channels": None,
        "reported_domain": "VoiceBank-DEMAND / SE-Bridge comparison",
        "reported_mode": "offline_quality_reference_non_streaming_lead",
        "reported_python": "3.8",
        "reported_sample_rate_hz": None,
        "reported_task": "single-channel speech enhancement / noise suppression",
        "snr_estimation": "required outside oracle-SNR conditions",
        "source_license_reported": None,
        "source_license_status": "fork_license_text_not_verified",
        "source_revision": None,
        "source_repository": SOURCE_REPOSITORY,
        "source_repository_source": CENSUS_REL + ":36",
        "status": "source_reported_not_measured_here",
        "upstream_sgmse_mit_not_covering_fork_or_weights": True,
    }


def reported_metrics() -> dict:
    return {
        "admitted_as_result": False,
        "cohort": "VoiceBank-DEMAND (source-reported only)",
        "local_pesq": None,
        "local_stoi": None,
        "note": (
            "The census reports +0.12 PESQ mean over the SE-Bridge baseline on "
            "VoiceBank-DEMAND. That value is source-reported provenance, not "
            "a local measurement and not comparable with project DNS2020 "
            "results."),
        "qualifies": False,
        "source_reported_pesq_delta":
            "+0.12 PESQ mean over SE-Bridge baseline on VoiceBank-DEMAND",
        "status": "source_reported_only_not_measured_here",
    }


def task_geometry() -> dict:
    return {
        "candidate_family": CANDIDATE_FAMILY,
        "exact_geometry_verified": False,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "normalization": None,
        "output_length": None,
        "pacing_policy": None,
        "reported_approach": (
            "SNR-conditioned, one-step consistency diffusion enhancement"),
        "reported_channels": None,
        "reported_domain": "VoiceBank-DEMAND / SE-Bridge comparison",
        "reported_mode": "offline_quality_reference_non_streaming_lead",
        "reported_python": "3.8",
        "reported_sample_rate_hz": None,
        "reported_task": "single-channel speech enhancement / noise suppression",
        "sdk_v0_adapter_mapping_present": False,
        "sdk_v0_frame_samples": 160,
        "sdk_v0_mono_matches_reported": None,
        "sdk_v0_rate_matches_reported": None,
        "snr_conditioning_layout": None,
        "state_reset_policy": None,
        "stft_window_samples": None,
        "status": TASK_GEOMETRY_STATE,
    }


def enhancement_profile() -> dict:
    rows = [
        {
            "evidence": (
                "No identity/noisy control or task-matched SE-Bridge baseline "
                "exists on exact DiffSE assets; no diffusion comparator is run."),
            "id": "ENH-01",
            "requirement": (
                "Identity/noisy control and an established task-matched "
                "baseline."),
            "status": "blocked",
        },
        {
            "evidence": (
                "No rights-cleared 16 kHz paired cohort and no paired SI-SDR "
                "or STOI score."),
            "id": "ENH-02",
            "requirement": (
                "Paired SI-SDR and STOI where permitted clean references "
                "exist."),
            "status": "blocked",
        },
        {
            "evidence": (
                "No preservation, peak, clipping or nonfinite record; "
                "diffusion output is not produced or inspected."),
            "id": "ENH-03",
            "requirement": (
                "Clean-speech preservation, peaks and invalid outputs."),
            "status": "blocked",
        },
        {
            "evidence": "No screen, listening protocol, panel or permission.",
            "id": "ENH-04",
            "requirement": (
                "Separately labeled predictive screen or authorized "
                "listening."),
            "status": "blocked",
        },
        {
            "evidence": (
                "No runtime, alignment, state, memory, sampler timing or "
                "measured content delay."),
            "id": "ENH-05",
            "requirement": (
                "Alignment, state, memory and measured content/availability "
                "timing."),
            "status": "blocked",
        },
        {
            "evidence": (
                "No rate, STFT window, hop, one-step sampler, SNR estimator "
                "layout, oracle-versus-estimated SNR policy, padding, output "
                "length or normalization contract is staged."),
            "id": "ENH-06",
            "requirement": (
                "Offline diffusion and input-SNR estimator geometry, "
                "including sample rate, channels, 160-sample frame mapping, "
                "STFT, sampler, SNR condition, padding, output length and no "
                "streaming lookahead."),
            "status": "blocked",
        },
        {
            "evidence": "No cohort or stratum definition exists.",
            "id": "ENH-07",
            "requirement": (
                "Quiet/active speech, idle noise and onset/offset strata."),
            "status": "blocked",
        },
        {
            "evidence": (
                "The package records absence and separation only; the census "
                "and its +0.12 PESQ line are source-reported provenance and "
                "no result of any class is promoted."),
            "id": "ENH-08",
            "requirement": (
                "Keep paired, unpaired, synthetic, human and source-reported "
                "evidence separate."),
            "status": "documented",
        },
    ]
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
            "blocked_count": sum(1 for row in rows
                                 if row["status"] == "blocked"),
            "documented_count": sum(1 for row in rows
                                    if row["status"] == "documented"),
            "profile_satisfied": False,
            "real_result_count": 0,
            "requirement_count": len(rows),
        },
        "source_reported_metric_present": True,
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
        "descriptor_sample_format": "f32",
        "diffse_mapping_present": False,
        "frame_samples": 160,
        "hop_samples": 160,
        "preserved": True,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
    }


def disposition_block() -> dict:
    return {
        "adapter_present": False,
        "checkpoint_identity_recorded_only": False,
        "checkpoint_present_locally": False,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
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
            "DiffSE is an SNR-conditioned one-step consistency diffusion "
            "enhancer. The pinned census reports M4-M6 results, SE-Bridge "
            "baselines and Drive-folder checkpoints, but no immutable source "
            "revision, checkpoint identity, SNR estimator, runtime, fork "
            "licence text, rights-cleared cohort or local result is present."),
        "task_mode": MODE,
    }


def required_artifacts() -> list[dict]:
    items = (
        ("ART-01", "source_snapshot",
         "The yh-jun/SNR-Aligned_diffSE source at an immutable 40-hex commit "
         "with reviewed fork licence text, notice, per-file SHA-256 and a map "
         "from the model, one-step sampler, SNR estimator and metric scripts "
         "to source files. Upstream SGMSE MIT terms are not substituted."),
        ("ART-02", "checkpoint_bundle",
         "The exact baseline DiffSE checkpoint named by the paper at immutable "
         "identity with file name, byte count, SHA-256, tensor schema, "
         "inference configuration and checkpoint-specific terms; a Drive "
         "folder link is not an immutable artifact."),
        ("ART-03", "snr_estimator_bundle",
         "The exact input-SNR estimator used outside oracle-SNR conditions, "
         "with immutable revision, byte count, SHA-256, feature configuration "
         "and separate terms."),
        ("ART-04", "runtime_lock",
         "A locked offline runtime reconciling the repository's Python 3.8 "
         "prescription with the pinned 3.12.16 evidence interpreter, with "
         "exact package versions, byte counts, SHA-256 values, CPU/MPS device, "
         "determinism and seed policy."),
        ("ART-05", "rights_bundle",
         "Reviewed fork source, DiffSE checkpoint, SNR estimator, SE-Bridge "
         "baseline, VoiceBank-DEMAND and training-data terms; corpus and "
         "clean-reference permission; output use, redistribution and "
         "attribution."),
        ("ART-06", "offline_diffusion_geometry",
         "Frozen offline whole-utterance contract: sample rate, channels, "
         "160-sample frame mapping, STFT window and hop, one-step sampler and "
         "noise schedule, SNR conditioning layout, oracle-versus-estimated "
         "SNR policy, padding, output length, normalization, no streaming "
         "lookahead and fresh state per call."),
        ("ART-07", "rights_cleared_cohort_and_results",
         "A frozen rights-cleared 16 kHz mono cohort with paired clean "
         "references where permitted, quiet/active and idle-noise strata, "
         "onset/offset cases, held-out splits, identity/noisy controls, "
         "SE-Bridge baseline and independent Enhancement, listening, timing "
         "and content-preservation results."),
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
        ("BLK-01", "ART-01", ("RG-01", "RG-04"),
         "Fork source identity and licence text",
         "The census names the repository but explicitly says the repository's "
         "own licence text was not verified. No immutable commit, notice or "
         "per-file digest is staged; the upstream SGMSE MIT licence does not "
         "cover this fork or its weights."),
        ("BLK-02", "ART-02", ("RG-01", "RG-03"),
         "Checkpoint identity, terms and local bytes",
         "The census reports baseline checkpoints exposed through Drive "
         "folders, but records no file name, revision, byte count or SHA-256. "
         "Checkpoint-specific terms and training/test overlap are unresolved."),
        ("BLK-03", "ART-03", ("RG-01", "RG-05"),
         "Input-SNR estimator and oracle-SNR boundary",
         "The census states that input-SNR estimation is required outside "
         "oracle-SNR conditions. No estimator checkpoint, revision, byte "
         "count, SHA-256, feature configuration or separate terms is staged."),
        ("BLK-04", "ART-04", ("RG-02", "RG-07"),
         "Python 3.8 runtime and CPU feasibility",
         "The repository prescribes Python 3.8 while this evidence runtime is "
         "pinned at 3.12.16. No locked framework package set, wheel digests, "
         "offline loader, deterministic one-step sampler, CPU feasibility "
         "measurement or device timing is staged."),
        ("BLK-05", "ART-05", ("RG-03",),
         "Rights bundle for fork, weights, baseline and cohort",
         "Fork licence, checkpoint terms, SE-Bridge baseline terms, "
         "VoiceBank-DEMAND and training-data provenance, clean-reference "
         "permission and output-use rights are unresolved; no rights review "
         "reference exists."),
        ("BLK-06", "ART-06", ("RG-04", "RG-05", "RG-06"),
         "Offline diffusion geometry and conditioned cohort",
         "The evidence reports one-step consistency diffusion but records no "
         "sample rate, STFT window, hop, sampler schedule, SNR conditioning "
         "layout, padding, output length, normalization, 160-sample SDK "
         "mapping, rights-cleared cohort or matched result."),
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
        ("RG-01", "Exact pinned DiffSE fork source with immutable revision, "
                  "reviewed licence text, notice and per-file identity; no "
                  "substitution of upstream SGMSE MIT terms."),
        ("RG-02", "Exact baseline checkpoint and input-SNR estimator with "
                  "byte counts, SHA-256 values, tensor schemas, separate "
                  "terms and a locked offline Python runtime reconciled with "
                  "the repository's Python 3.8 prescription."),
        ("RG-03", "Rights review for fork code, checkpoint, estimator, "
                  "SE-Bridge baseline, VoiceBank-DEMAND, clean references and "
                  "output use."),
        ("RG-04", "Rights-cleared 16 kHz mono cohort with consent, permitted "
                  "clean references and frozen identity/noisy controls."),
        ("RG-05", "Frozen offline one-step diffusion geometry: STFT "
                  "window/hop, sampler schedule, input-SNR conditioning "
                  "layout, oracle-versus-estimated SNR policy, padding, "
                  "output length, normalization, no lookahead and exact "
                  "160-sample SDK frame mapping."),
        ("RG-06", "Enhancement result set: identity/noisy control, "
                  "SE-Bridge task-matched baseline, paired SI-SDR and STOI, "
                  "clean-speech preservation, peaks, invalid and nonfinite "
                  "outputs."),
        ("RG-07", "Independent listening or labeled predictive screen plus "
                  "measured content/availability timing, memory, resources "
                  "and stochastic stability on the exact runtime."),
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
        "checkpoint_identity_verified": False,
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
            "Exact fork source and licence, checkpoint bytes, input-SNR "
            "estimator, runtime, one-step sampler, offline geometry, "
            "rights-cleared cohort, matched evidence and independent review "
            "are all absent. The source-reported PESQ delta is not promoted."),
        "recorded_identity_only": False,
        "reference_execution_result": False,
        "release_claim": False,
        "rights_cleared_cohort": False,
        "runtime_pinned": False,
        "runtime_present": False,
        "source_license_verified": False,
        "source_present": False,
        "snr_estimator_identity_verified": False,
        "source_reported_metric_promoted": False,
        "status": QUALIFICATION_STATUS,
        "weights_identity_verified": False,
        "weights_present_locally": False,
    }


def non_claims() -> list[str]:
    return [
        "No DiffSE source copy, repository snapshot, checkpoint, weight "
        "fragment, input-SNR estimator, sampler configuration, runtime, "
        "corpus, recording, output or vendor result is present, loaded or "
        "executed.",
        "No diffusion inference, audio read or write, listening, paired "
        "SI-SDR or STOI scoring, clean-speech preservation, peak, alignment, "
        "content-delay or device-timing measurement is performed.",
        "No real or synthetic waveform is scored; the admission control is a "
        "schema object only and is marked synthetic_schema_control.",
        "No DiffSE checkpoint file name, byte count, SHA-256 or input-SNR "
        "estimator identity is recorded; the census is a source lead, not a "
        "measurement.",
        "The +0.12 PESQ delta and M4-M6 descriptions are source-reported only "
        "and are not local results, benchmarks or qualification evidence.",
        "No local DNS2020, SE-Bridge, VoiceBank, FastEnhancer, NASE, "
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
        "snr_estimator_present": False,
        "source_present": False,
        "source_reported_python": "3.8",
    }


def recorded_identity() -> dict:
    return {
        "admitted_as_result": False,
        "byte_count_verified_locally": False,
        "checkpoint_bytes": None,
        "checkpoint_file": None,
        "checkpoint_sha256": None,
        "checkpoint_variant": None,
        "digest_verified_locally": False,
        "locally_present": False,
        "locally_verified": False,
        "model_repository": SOURCE_REPOSITORY,
        "model_revision": None,
        "overrides_path": None,
        "paper_url": PAPER_URL,
        "qualifies": False,
        "recorded_by": [CENSUS_REL, INVENTORY_REL, INVENTORY_MD_REL],
        "snr_estimator_sha256": None,
        "source_license_verified": False,
        "source_revision": None,
        "status": "no_checkpoint_or_snr_estimator_identity_recorded_in_merged_evidence",
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset declaration.
# ---------------------------------------------------------------------------


class DeclarationError(ValueError):
    """Deterministic manifest rejection; no asset is opened."""


DECLARATION_TOP = (
    "schema_id", "manifest_id", "source", "checkpoint", "snr_estimator",
    "runtime", "sampler", "geometry", "input", "controls", "rights",
)
SOURCE_FIELDS = (
    "repository", "revision", "license_spdx", "license_sha256", "tree_sha256",
)
CHECKPOINT_FIELDS = (
    "variant", "filename", "revision", "byte_count", "sha256",
    "terms_sha256", "tensor_schema_sha256",
)
SNR_ESTIMATOR_FIELDS = (
    "name", "filename", "revision", "byte_count", "sha256", "terms_sha256",
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
    "mode", "channels", "sample_rate_hz", "frame_samples", "sample_format",
    "stft_window_samples", "hop_samples", "lookahead_samples",
    "whole_utterance", "state_reset", "snr_conditioning_layout",
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
    "source_terms", "checkpoint_terms", "snr_estimator_terms",
    "training_data_terms", "corpus_rights", "clean_reference_permission",
    "output_use", "redistribution", "review_reference",
)
UNRESOLVED = frozenset((
    "", "n/a", "na", "none", "null", "tbd", "todo", "unresolved", "unknown",
))
LICENSES = frozenset((
    "Apache-2.0", "BSD-3-Clause", "CC-BY-4.0", "CC-BY-NC-4.0", "MIT",
    "MPL-2.0", "other-reviewed",
))
PATCH_LEVEL_SOURCE_PYTHON = re.compile(r"^3\.8\.[0-9]+$")


def _exact_keys(value: Any, fields: Iterable[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise DeclarationError(label + "_not_object")
    expected = set(fields)
    observed = set(value)
    if observed - expected:
        raise DeclarationError(label + "_unknown_field")
    if expected - observed:
        raise DeclarationError(label + "_missing_field")
    return value


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise DeclarationError(label + "_not_sha256")
    return value


def _hex40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX40.match(value):
        raise DeclarationError(label + "_not_revision")
    return value


def _int(value: Any, label: str, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or \
            value < low or value > high:
        raise DeclarationError(label + "_out_of_range")
    return value


def _bool(value: Any, label: str, expected: bool) -> bool:
    if not isinstance(value, bool) or value is not expected:
        raise DeclarationError(label + "_not_" + str(expected).lower())
    return value


def _resolved(value: Any, label: str) -> str:
    if not isinstance(value, str) or value.strip().lower() in UNRESOLVED \
            or value.strip().lower().startswith("unresolved"):
        raise DeclarationError(label + "_unresolved")
    return value.strip()


def _slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise DeclarationError(label + "_not_slug")
    return value


def _weight_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SAFE_BASENAME.match(value):
        raise DeclarationError(label + "_unsafe_path")
    if value != Path(value).name or "/" in value or "\\" in value or \
            ".." in value or not value.lower().endswith(WEIGHT_SUFFIXES):
        raise DeclarationError(label + "_unsafe_path")
    return value


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
    if checkpoint["variant"] != "voicebank-demand-one-step":
        raise DeclarationError("checkpoint_variant_mismatch")
    _weight_name(checkpoint["filename"], "checkpoint_filename")
    _hex40(checkpoint["revision"], "checkpoint_revision")
    _int(checkpoint["byte_count"], "checkpoint_byte_count", 1, 1 << 33)
    _hex64(checkpoint["sha256"], "checkpoint_sha256")
    _hex64(checkpoint["terms_sha256"], "checkpoint_terms_sha256")
    _hex64(checkpoint["tensor_schema_sha256"],
           "checkpoint_tensor_schema_sha256")

    estimator = _exact_keys(top["snr_estimator"], SNR_ESTIMATOR_FIELDS,
                            "snr_estimator")
    if estimator["name"] != "input_snr_estimator":
        raise DeclarationError("snr_estimator_name_mismatch")
    _weight_name(estimator["filename"], "snr_estimator_filename")
    _hex40(estimator["revision"], "snr_estimator_revision")
    _int(estimator["byte_count"], "snr_estimator_byte_count", 1, 1 << 33)
    _hex64(estimator["sha256"], "snr_estimator_sha256")
    _hex64(estimator["terms_sha256"], "snr_estimator_terms_sha256")

    runtime = _exact_keys(top["runtime"], RUNTIME_FIELDS, "runtime")
    if not isinstance(runtime["python_version"], str) or not \
            PATCH_LEVEL_SOURCE_PYTHON.match(runtime["python_version"]):
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
    if sampler["kind"] != "diffusion_one_step_consistency":
        raise DeclarationError("sampler_kind_mismatch")
    _int(sampler["steps"], "sampler_steps", 1, 1)
    if sampler["noise_schedule"] not in (
            "linear", "cosine", "sqrt", "sigmoid", "custom_reviewed"):
        raise DeclarationError("sampler_noise_schedule_unresolved")
    _int(sampler["seed"], "sampler_seed", 0, (1 << 32) - 1)
    _bool(sampler["deterministic"], "sampler_deterministic", True)
    _bool(sampler["stochastic"], "sampler_stochastic", False)
    _hex64(sampler["sampler_sha256"], "sampler_sha256")

    geometry = _exact_keys(top["geometry"], GEOMETRY_FIELDS, "geometry")
    if geometry["mode"] != "offline_whole_utterance":
        raise DeclarationError("geometry_mode_mismatch")
    _int(geometry["channels"], "geometry_channels", 1, 1)
    _int(geometry["sample_rate_hz"], "geometry_sample_rate_hz", 16000, 16000)
    _int(geometry["frame_samples"], "geometry_frame_samples", 160, 160)
    if geometry["sample_format"] != "float32":
        raise DeclarationError("geometry_sample_format_mismatch")
    _int(geometry["stft_window_samples"], "geometry_stft_window", 16, 1 << 16)
    _int(geometry["hop_samples"], "geometry_hop", 1, 1 << 15)
    _int(geometry["lookahead_samples"], "geometry_lookahead", 0, 0)
    _bool(geometry["whole_utterance"], "geometry_whole_utterance", True)
    _bool(geometry["state_reset"], "geometry_state_reset", True)
    if geometry["snr_conditioning_layout"] not in (
            "frame_level", "utterance_level", "chunk_level"):
        raise DeclarationError("geometry_snr_conditioning_layout_unresolved")
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


def _control_document() -> dict:
    sha = "0" * 64
    revision = "1" * 40
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "manifest_id": "synthetic-diffse-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": revision,
            "license_spdx": "MIT",
            "license_sha256": sha,
            "tree_sha256": sha,
        },
        "checkpoint": {
            "variant": "voicebank-demand-one-step",
            "filename": "diffse.pt",
            "revision": revision,
            "byte_count": 1,
            "sha256": sha,
            "terms_sha256": sha,
            "tensor_schema_sha256": sha,
        },
        "snr_estimator": {
            "name": "input_snr_estimator",
            "filename": "snr_estimator.pt",
            "revision": revision,
            "byte_count": 1,
            "sha256": sha,
            "terms_sha256": sha,
        },
        "runtime": {
            "python_version": "3.8.20",
            "framework": "pytorch",
            "framework_version": "2.4.1",
            "device": "cpu",
            "lock_sha256": sha,
            "offline_load": True,
            "deterministic": True,
            "packages": ["numpy==1.24.4", "torch==2.4.1"],
        },
        "sampler": {
            "kind": "diffusion_one_step_consistency",
            "steps": 1,
            "noise_schedule": "linear",
            "seed": 0,
            "deterministic": True,
            "stochastic": False,
            "sampler_sha256": sha,
        },
        "geometry": {
            "mode": "offline_whole_utterance",
            "channels": 1,
            "sample_rate_hz": 16000,
            "frame_samples": 160,
            "sample_format": "float32",
            "stft_window_samples": 512,
            "hop_samples": 160,
            "lookahead_samples": 0,
            "whole_utterance": True,
            "state_reset": True,
            "snr_conditioning_layout": "utterance_level",
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
            "snr_estimator_terms": True,
            "training_data_terms": True,
            "corpus_rights": True,
            "clean_reference_permission": True,
            "output_use": True,
            "redistribution": True,
            "review_reference": "synthetic-review-reference",
        },
    }


def declaration_control() -> dict:
    document = _control_document()
    result = validate_asset_declaration(document)
    result["note"] = (
        "Synthetic schema control only. It proves the validator accepts a "
        "well-formed declaration and is not evidence, not an asset and not a "
        "result.")
    result["synthetic_schema_control"] = True
    result["qualifies"] = False
    return result


def declaration_rejections() -> dict:
    mutations = (
        ("top_not_object", lambda d: d.clear(), []),
        ("missing_top_field", lambda d: d.pop("rights"), None),
        ("unknown_top_field", lambda d: d.update(extra=1), None),
        ("schema_id_mismatch", lambda d: d.update(schema_id="other"), None),
        ("manifest_id_bad", lambda d: d.update(manifest_id="../escape"), None),
        ("source_not_object", lambda d: d.update(source=[]), None),
        ("source_unknown_field", lambda d: d["source"].update(extra=1), None),
        ("source_missing_field", lambda d: d["source"].pop("revision"), None),
        ("source_repository_mismatch",
         lambda d: d["source"].update(repository="https://example.invalid"), None),
        ("source_revision_bad",
         lambda d: d["source"].update(revision="deadbeef"), None),
        ("source_license_unresolved",
         lambda d: d["source"].update(license_spdx="unreviewed"), None),
        ("source_license_digest_bad",
         lambda d: d["source"].update(license_sha256="xyz"), None),
        ("source_tree_digest_bad",
         lambda d: d["source"].update(tree_sha256="xyz"), None),
        ("checkpoint_variant_mismatch",
         lambda d: d["checkpoint"].update(variant="raw"), None),
        ("checkpoint_unsafe_filename",
         lambda d: d["checkpoint"].update(filename="../w.pt"), None),
        ("checkpoint_suffix_bad",
         lambda d: d["checkpoint"].update(filename="w.txt"), None),
        ("checkpoint_digest_bad",
         lambda d: d["checkpoint"].update(sha256="xyz"), None),
        ("checkpoint_byte_count_bool",
         lambda d: d["checkpoint"].update(byte_count=True), None),
        ("snr_estimator_name_mismatch",
         lambda d: d["snr_estimator"].update(name="wrong_estimator"), None),
        ("snr_estimator_digest_bad",
         lambda d: d["snr_estimator"].update(sha256="xyz"), None),
        ("snr_estimator_missing",
         lambda d: d.pop("snr_estimator"), None),
        ("runtime_python_mismatch",
         lambda d: d["runtime"].update(python_version="3.12.16"), None),
        ("runtime_framework_mismatch",
         lambda d: d["runtime"].update(framework="tensorflow"), None),
        ("runtime_device_mismatch",
         lambda d: d["runtime"].update(device="npu"), None),
        ("runtime_lock_bad",
         lambda d: d["runtime"].update(lock_sha256="xyz"), None),
        ("runtime_offline_false",
         lambda d: d["runtime"].update(offline_load=False), None),
        ("runtime_packages_unsorted",
         lambda d: d["runtime"].update(packages=["z==1", "a==1"]), None),
        ("sampler_kind_mismatch",
         lambda d: d["sampler"].update(kind="ddim"), None),
        ("sampler_steps_mismatch",
         lambda d: d["sampler"].update(steps=20), None),
        ("sampler_stochastic_true",
         lambda d: d["sampler"].update(stochastic=True), None),
        ("geometry_rate_mismatch",
         lambda d: d["geometry"].update(sample_rate_hz=48000), None),
        ("geometry_frame_mismatch",
         lambda d: d["geometry"].update(frame_samples=320), None),
        ("geometry_lookahead_nonzero",
         lambda d: d["geometry"].update(lookahead_samples=160), None),
        ("geometry_conditioning_unresolved",
         lambda d: d["geometry"].update(snr_conditioning_layout="unknown"), None),
        ("input_pair_count_zero",
         lambda d: d["input"].update(pair_count=0), None),
        ("input_clean_reference_false",
         lambda d: d["input"].update(clean_reference=False), None),
        ("controls_identity_false",
         lambda d: d["controls"].update(identity_passthrough=False), None),
        ("rights_source_terms_false",
         lambda d: d["rights"].update(source_terms=False), None),
        ("rights_review_bad",
         lambda d: d["rights"].update(review_reference="../escape"), None),
    )
    cases: list[dict] = []
    for case_id, mutate, fallback in mutations:
        document = _control_document()
        try:
            mutate(document)
            if fallback == []:
                document.clear()
            validate_asset_declaration(document)
            observed = "UNEXPECTED_ACCEPT"
        except DeclarationError as error:
            observed = error.args[0]
        except (AttributeError, TypeError, KeyError):
            observed = fallback[0] if isinstance(fallback, list) and fallback \
                else "MALFORMED_INPUT"
        cases.append({"id": case_id, "observed": observed,
                      "rejected": observed != "UNEXPECTED_ACCEPT"})
    return {
        "case_count": len(cases),
        "cases": cases,
        "rejected_cases": sum(1 for item in cases if item["rejected"]),
    }


def asset_declaration_block() -> dict:
    control = declaration_control()
    rejections = declaration_rejections()
    strict_json = strict_json_rejections()
    return {
        "accepted_control_is_synthetic_only": control["synthetic_schema_control"],
        "accepted_control_qualifies": control["qualifies"],
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "control_keys": list(CONTROL_FIELDS),
        "contract_id": DECLARATION_SCHEMA_ID,
        "duplicate_keys_rejected": True,
        "exact_interpreter": REQUIRED_INTERPRETER,
        "floats_rejected": True,
        "geometry_fields": list(GEOMETRY_FIELDS),
        "input_fields": list(INPUT_FIELDS),
        "manifest_validation_only": True,
        "max_pairs": 100000,
        "max_weight_bytes": 1 << 33,
        "nonfinite_rejected": True,
        "rejection_cases": rejections["rejected_cases"],
        "required_channels": 1,
        "required_frame_samples": 160,
        "required_sample_format": "float32",
        "required_sample_rate_hz": 16000,
        "required_sampler_kind": "diffusion_one_step_consistency",
        "required_snr_estimator": "input_snr_estimator",
        "required_top_level_fields": list(DECLARATION_TOP),
        "rights_fields": list(RIGHT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "runtime_or_weights_invoked": False,
        "sampler_fields": list(SAMPLER_FIELDS),
        "schema_id": DECLARATION_SCHEMA_ID,
        "snr_estimator_fields": list(SNR_ESTIMATOR_FIELDS),
        "source_fields": list(SOURCE_FIELDS),
        "strict_json_cases": strict_json["rejection_cases"],
        "synthetic_control": control,
        "unknown_fields_rejected": True,
        "unresolved_values_rejected": True,
    }


def admission() -> dict:
    control = declaration_control()
    blockers = [
        "source_license_text_unverified",
        "drive_folder_checkpoint_identity_unpinned",
        "input_snr_estimator_absent",
        "python_3_8_runtime_and_cpu_feasibility_unverified",
        "rights_bundle_absent",
        "offline_diffusion_geometry_and_cohort_absent",
    ]
    return {
        "admissible": False,
        "blockers": blockers,
        "candidate_processing": False,
        "control_accepted": control["accepted"],
        "input_validated": True,
        "metrics": None,
        "note": (
            "A structurally valid declaration is still not admissible: the "
            "exact fork, checkpoint, estimator, runtime, rights, geometry and "
            "matched results are absent. This package has no admitting branch "
            "and no fallback."),
        "qualifies": False,
        "result": None,
        "status": DECISION,
    }


# ---------------------------------------------------------------------------
# Canonical documents.
# ---------------------------------------------------------------------------


def _source_pins() -> dict:
    return dict(sorted(SOURCE_PINS.items()))


def _boundary_pins() -> dict:
    return dict(sorted(BOUNDARY_PINS.items()))


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "admission_contract": asset_declaration_block(),
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
        "defer_before": DEFER_BEFORE,
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
        "owner": OWNER,
        "profile": PROFILE,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification": qualification_block(),
        "qualification_status": QUALIFICATION_STATUS,
        "release_gates": release_gates(),
        "reported_metrics": reported_metrics(),
        "required_artifacts": required_artifacts(),
        "reviewer": REVIEWER,
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
    return {
        "absence_evidence": absence_summary(),
        "admission": admission(),
        "asset_declaration": asset_declaration_block(),
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
        "defer_before": DEFER_BEFORE,
        "disposition": disposition_block(),
        "enhancement_profile": enhancement_profile(),
        "evidence_presence": evidence_presence(),
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": exact_blockers(),
        "exact_scope": exact_scope_block(),
        "gates": release_gates(),
        "incomplete": True,
        "inventory_record": inventory_record(),
        "linked_rows": list(rows),
        "linked_rows_sha256": linked_rows_digest(rows),
        "local_files": list(LOCAL_FILES),
        "mode": MODE,
        "non_claims": non_claims(),
        "owner": OWNER,
        "profile": PROFILE,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification": qualification_block(),
        "qualification_status": QUALIFICATION_STATUS,
        "recorded_identity": recorded_identity(),
        "reported_metrics": reported_metrics(),
        "required_artifacts": required_artifacts(),
        "reviewer": REVIEWER,
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
