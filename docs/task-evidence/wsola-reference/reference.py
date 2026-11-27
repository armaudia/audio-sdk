# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility/blocker evidence for SDK-WSOLA-REFERENCE.

Stdlib only. This package records a strict DEFER: WSOLA reference work is
blocked by the installed v0 fixed 160-frame boundary, absent elastic/variable
output contract, and missing isolated rights-cleared matched runtime evidence
for Sonic/SoundTouch/baseline comparison. No provider is registered or enabled,
no model/runtime/audio is downloaded or executed, and no result qualifies.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-WSOLA-REFERENCE"
TASK_TITLE = "WSOLA reference"
COMPONENT_ID = "wsola-reference"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/wsola-reference/ only"
TASK_PREFIX = "docs/task-evidence/wsola-reference/"
CONTRACT_ID = "audio-sdk/wsola-reference-evidence/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/wsola-reference-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/wsola-reference-report/0.1"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
BRANCH = "swarm/SDK-WSOLA-REFERENCE"
REVIEWER = "reviewer-WSOLA-REFERENCE"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK
)
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


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


AUDIO_ROOT = _find_audio_root()
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(WORKTREE)))

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
STABLE_TASK_FIELDS = (
    "acceptance", "component", "deliverable", "depends_on", "evidence", "id",
    "mode", "repository", "title", "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason", "claim", "dispatch_priority", "handoff", "owner",
    "review", "status",
)

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Measure source/output mapping",
    "duration, pitch, transient audibility and playback buffering",
    "1\u00d7, rate changes, unfamiliar speech, music, silence, rebuffer, drift "
    "and the final partial window",
    "pause or filler decisions tied to source timestamps and measure speech "
    "preservation",
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")
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
    "artifacts": ("<!-- digest-table: artifacts -->", "<!-- digest-table: end -->"),
}

SCOPE_BASE_REFS = ("origin/main", "main")


class ReferenceError(ValueError):
    pass


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
            raise ReferenceError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ReferenceError("nonfinite_json:" + token)


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReferenceError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ReferenceError("invalid_json") from error
    if not isinstance(value, dict):
        raise ReferenceError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def loads_strict(payload: str) -> dict:
    return parse_strict_json_text(payload.encode("utf-8"))


def assert_no_float(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise TypeError("float not allowed: " + path)
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
# Board identity: stable projection only, mutable board file never pinned.
# ---------------------------------------------------------------------------


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ReferenceError("board_tasks_not_list")
    return tasks


def board_row_projection(path: Path | None = None) -> dict:
    rows = [row for row in _board_tasks(path)
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ReferenceError("board_row_not_unique")
    row = rows[0]
    projection = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if projection["component"] != COMPONENT_ID:
        raise ReferenceError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ReferenceError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ReferenceError("board_repository_mismatch")
    if tuple(projection["depends_on"]) != DEPENDS_ON:
        raise ReferenceError("board_depends_on_mismatch")
    return projection


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None else board_row_projection())


# ---------------------------------------------------------------------------
# Scope helpers: newest merge-base with origin/main then main, fail closed.
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path, refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ReferenceError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]


# ---------------------------------------------------------------------------
# Pins / README digest tables / SOURCES.sha256.
# ---------------------------------------------------------------------------


def pin_rows(pins: dict[str, str], root: Path) -> list[dict]:
    rows = []
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
        path = AUDIO_ROOT / relative
        if not path.is_file() or sha256_file(path) != digest:
            raise ReferenceError("source_pin_unavailable:" + relative)
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        if not path.is_file() or sha256_file(path) != digest:
            raise ReferenceError("boundary_pin_unavailable:" + relative)
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths relative to pinned audioml workspace root.",
        "# sdk: paths relative to this SDK worktree.",
        "# Mutable plan/swarm/TASKS.json is never hashed; only stable linked-row projection is gated.",
        "# SOURCES.sha256 is excluded because it cannot pin its own bytes.",
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
        raise ReferenceError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ReferenceError("readme_marker_missing:" + section)
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
                    raise ReferenceError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ReferenceError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if HEX64.fullmatch(digest) is None:
                raise ReferenceError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({k for k, _ in rows}) != len(rows):
            raise ReferenceError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            raise ReferenceError(
                f"readme_key_mismatch:{section}:missing={sorted(expected[section]-actual_keys)}:extra={sorted(actual_keys-expected[section])}")
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
                raise ReferenceError("readme_digest_mismatch:" + key)
            if not path.is_file() or sha256_file(path) != digest:
                raise ReferenceError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ReferenceError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        return "\n".join(
            f"| `source:{name}` | `{digest}` |"
            for name, digest in sorted(SOURCE_PINS.items()))
    if section == "boundary":
        return "\n".join(
            f"| `sdk:{name}` | `{digest}` |"
            for name, digest in sorted(BOUNDARY_PINS.items()))
    if section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            if name in ARTIFACT_TABLE_EXCLUDED:
                continue
            path = HERE / name
            rows.append(f"| `{name}` | `{sha256_file(path)}` | {path.stat().st_size} |")
        return "\n".join(rows)
    raise ReferenceError("unknown_readme_section:" + section)


def update_readme_table(text: str, section: str) -> str:
    block = render_digest_table(section)
    start, end = README_MARKERS[section]
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[:start_index] + start + "\n" + block + "\n" + end + text[end_index:]


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Evidence records.
# ---------------------------------------------------------------------------


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": [p for p in PROFILE_PHRASES if len(rows) == 1 and p in rows[0]],
        "all_phrases_present": len(rows) == 1 and all(p in rows[0] for p in PROFILE_PHRASES),
    }


def inventory_record() -> dict:
    document = read_strict_json(AUDIO_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    components = document.get("components")
    if not isinstance(components, list):
        raise ReferenceError("inventory_components_not_list")
    matches = [row for row in components
               if isinstance(row, dict) and row.get("id") == COMPONENT_ID]
    if len(matches) != 1:
        raise ReferenceError("inventory_row_not_unique")
    row = matches[0]
    if row.get("task") != TASK:
        raise ReferenceError("inventory_task_mismatch")
    if row.get("verification_profile") != PROFILE:
        raise ReferenceError("inventory_profile_mismatch")
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
    }


def evidence_snippet_check() -> dict:
    checks = []
    spec = [
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "A time stretcher produces a different number of output frames per input block."),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "SoX and FFmpeg contain readable LGPL WSOLA references; the papers are old and the core patents have expired."),
        ("cpp-library/pipeline-validation/playback-speed-candidates.md",
         "a clean, readable WSOLA implementation in `libavfilter`."),
        ("audio-benchmark-platform/plan/swarm/VERIFICATION.md",
         "Measure source/output mapping, duration, pitch, transient audibility and playback buffering"),
        ("audio-benchmark-platform/plan/audio-sdk/README.md",
         "Extend the SDK with public reference providers, analysis adapters, and reusable"),
        ("CONTRACTS.md", "Process input_count is exactly 160."),
    ]
    for relative, phrase in spec:
        if relative == "CONTRACTS.md":
            path = SDK_ROOT / relative
        elif relative in BOUNDARY_PINS:
            path = SDK_ROOT / relative
        else:
            path = AUDIO_ROOT / relative
        payload = path.read_text(encoding="utf-8")
        checks.append({"path": relative, "phrase": phrase, "present": phrase in payload})
    return {
        "count": len(checks),
        "checks": checks,
        "all_present": all(row["present"] for row in checks),
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "sample_format": "float32",
        "elastic_output_supported": False,
        "wsola_reference_mapping_present": False,
        "unchanged": True,
    }


def boundary_block() -> dict:
    projection = board_row_projection()
    return {
        "provider_registration": False,
        "adapter_json_added": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "candidate_code_vendored": False,
        "weights_vendored": False,
        "audio_added": False,
        "network_used": False,
        "board_or_handoff_changed": False,
        "linked_row": projection,
        "linked_row_sha256": board_row_digest(projection),
        "linked_row_identity_only": True,
        "board_file_pinned": False,
        "mutable_board_fields_gate": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "network_access": False,
        "download_attempted": False,
        "candidate_code_downloaded": False,
        "candidate_code_vendored": False,
        "runtime_executed": False,
        "real_audio": False,
        "synthetic_audio_committed_as_result": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "write_scope": WRITE_SCOPE,
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
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "summary": (
            "WSOLA reference is a rate-profile feasibility task blocked by "
            "installed v0 fixed 160-sample frame contract, absent elastic/variable "
            "output adapter contract, and missing isolated rights-cleared matched "
            "runtime evidence for Sonic, SoundTouch and fixed-rate baseline "
            "comparison. No implementation, runtime, real audio, or qualification "
            "claim is made."
        ),
    }


# ---------------------------------------------------------------------------
# Blockers, gates, rate profile.
# ---------------------------------------------------------------------------


EXACT_BLOCKERS = [
    {
        "id": "elastic_output_contract_absent",
        "gates": ["RG-01", "RG-03", "RG-05"],
        "statement": "Installed v0 process contract is fixed at 160 input and 160 output samples; WSOLA requires variable output per input and elastic/drain semantics.",
        "required_action": "Add a reviewed versioned elastic-output/variable-frame adapter contract with deterministic drain, reset, and timing semantics before implementation.",
    },
    {
        "id": "isolated_reference_runtime_absent",
        "gates": ["RG-02", "RG-04", "RG-05"],
        "statement": "No isolated pinned runtime/build for WSOLA, Sonic, SoundTouch, and fixed-rate baseline comparison is present in this worktree/package.",
        "required_action": "Provide isolated, pinned, reproducible runtimes/builds for each compared candidate with immutable revisions and exact commands.",
    },
    {
        "id": "rights_and_license_uncleared",
        "gates": ["RG-02", "RG-07", "RG-08"],
        "statement": "Sonic/SoundTouch/fixed-rate baseline comparison has not been rights/license reviewed for this repository boundary and release posture.",
        "required_action": "Record reviewed license/redistribution/product-use terms and required notices for each compared implementation.",
    },
    {
        "id": "matched_rate_evidence_absent",
        "gates": ["RG-04", "RG-06", "RG-08"],
        "statement": "No rights-cleared matched rate cohort, outputs, or listening/screen evidence exists for WSOLA reference comparison.",
        "required_action": "Run frozen matched rate cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, and preservation metrics.",
    },
]

RELEASE_GATES = [
    ("RG-01", "elastic_output_contract", "A versioned elastic-output/variable-frame contract exists, is reviewed, and preserves v0 behavior unchanged."),
    ("RG-02", "exact_source_runtime_identity", "WSOLA/Sonic/SoundTouch/fixed-rate baseline sources, revisions, builds, licenses, and runtime commands are pinned and reviewed."),
    ("RG-03", "adapter_boundary_and_isolation", "Optional caller-supplied/opt-in adapter boundary is isolated, OFF by default, unregistered, and outside shared build/CI/public defaults."),
    ("RG-04", "matched_rate_reference_execution", "Deterministic matched execution exists on frozen inputs with hashed outputs and exact source/output mapping."),
    ("RG-05", "state_reset_drain_timing", "Reset, drain, end-of-stream, sample-time mapping, and availability/content delay are verified on the exact runtime."),
    ("RG-06", "rate_profile_evidence", "Rate profile evidence covers 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, and speech preservation."),
    ("RG-07", "rights_and_publication", "All code/data/output rights and publication/release terms are reviewed and recorded."),
    ("RG-08", "public_default_and_release", "No public default/release/benchmark claim is made without independent review and all prior gates passing."),
]

RATE_REQUIREMENTS = [
    ("RATE-01", "Source/output mapping for exact runtime.", "blocked"),
    ("RATE-02", "Duration/pitch/transient audibility and playback buffering.", "blocked"),
    ("RATE-03", "1x control.", "blocked"),
    ("RATE-04", "Rate changes.", "blocked"),
    ("RATE-05", "Unfamiliar speech, music, silence.", "blocked"),
    ("RATE-06", "Rebuffer, drift and final partial window.", "blocked"),
    ("RATE-07", "Pause/filler decisions tied to source timestamps and speech preservation.", "blocked"),
    ("RATE-08", "Separate evidence classes; no missing result qualifies.", "documented"),
]


def rate_profile() -> dict:
    rows = []
    for rid, requirement, state in RATE_REQUIREMENTS:
        rows.append({
            "id": rid,
            "requirement": requirement,
            "status": state,
            "qualifies": False,
            "evidence": (
                "No runtime, no matched cohort, no output; not measured."
                if state == "blocked" else
                "Report keeps missing-real, source-reported, and boundary evidence separate."),
        })
    return {
        "profile": PROFILE,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "rows": rows,
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_results": 0,
        "surrogate_present": False,
    }


def release_gates() -> list[dict]:
    projection = board_row_projection()
    return [{
        "id": gid,
        "title": title,
        "status": "blocked",
        "qualifies": False,
        "linked_row": projection,
        "requirement": requirement,
        "reopen_condition": requirement,
    } for gid, title, requirement in RELEASE_GATES]


def exact_blockers() -> list[dict]:
    return [{
        "id": row["id"],
        "status": "open",
        "qualifies": False,
        "gates": list(row["gates"]),
        "statement": row["statement"],
        "required_action": row["required_action"],
    } for row in EXACT_BLOCKERS]


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "candidate_qualified": False,
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "no_missing_result_qualifies_candidate": True,
        "blocked_gate_count": len(RELEASE_GATES),
        "blocked_gate_ids": [g[0] for g in RELEASE_GATES],
        "reason": disposition_block()["summary"],
    }


# ---------------------------------------------------------------------------
# Report / contract builders.
# ---------------------------------------------------------------------------


NON_CLAIMS = [
    "No WSOLA/Sonic/SoundTouch/fixed-rate baseline implementation is added, built, executed, or vendored.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI, or installed v0 behavior changes.",
    "No real audio, corpus, listening, device timing, benchmark, or release claim.",
    "No network/download is attempted; absent runtimes/assets are not fabricated.",
    "Missing results do not qualify the candidate; decision is DEFER/not_qualified.",
]


def build_contract(report: dict | None = None) -> dict:
    r = build_report() if report is None else report
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": DECISION,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "write_scope": TASK_PREFIX,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": r["task_row_identity"],
        "public_v0_geometry": r["public_v0_geometry"],
        "gates": r["gates"],
        "exact_blockers": r["exact_blockers"],
        "qualification": r["qualification"],
        "boundary": r["boundary"],
        "scope": r["scope"],
        "reproduction": r["reproduction"],
    }
    assert_no_float(contract)
    return contract


def build_report() -> dict:
    projection = board_row_projection()
    snippets = evidence_snippet_check()
    inventory = inventory_record()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "task_id": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": "Rate",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": {
            "board_path": BOARD_TASK_ROW,
            "stable_fields": projection,
            "stable_sha256": board_row_digest(projection),
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        },
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "inventory_record": inventory,
        "evidence_presence": {
            "snippets": snippets["checks"],
            "snippet_count": snippets["count"],
            "all_snippets_present": snippets["all_present"],
            "profile_source_check": profile_row_check(),
        },
        "rate_profile": rate_profile(),
        "gates": release_gates(),
        "exact_blockers": exact_blockers(),
        "qualification": qualification_block(),
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "pythonhashseed": "0",
            "pythondontwritebytecode": "1",
            "canonical_json": True,
            "sorted_keys": True,
            "cold_start_regenerations": 3,
        },
    }
    assert_no_float(report)
    return report


def main() -> int:
    text, digest = canonical_report(build_report())
    print(text)
    print("report_sha256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
