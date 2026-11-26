# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-PYROOMACOUSTICS.

Standard library only. The pinned research registry catalogues three
PyRoomAcoustics source leads (denoise, beamforming and DOA) and the inventory
records a considered sdk-tool row. None of the source, wheel, license text,
installed runtime, room geometry, RIR, labelled array cohort or tool output is
present locally. This module pins the inspection evidence, proves a fixed
absence inventory, exercises a fail-closed caller-supplied tool manifest
without importing or executing anything from the candidate, and builds
canonical DEFER bytes. Synthetic room geometry controls are always labelled
as controls and never as real RIR or reverberation evidence.
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

TASK = "SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS"
TASK_TITLE = "Pyroomacoustics candidate tools"
COMPONENT_ID = "pyroomacoustics-candidate-tools"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "tool"
PROFILE_LABEL = "Tool"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
TASK_PREFIX = "docs/task-evidence/pyroomacoustics-candidate-tools/"
CONTRACT_ID = "audio-sdk/pyroomacoustics-candidate-tools-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/pyroomacoustics-candidate-tools-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/pyroomacoustics-candidate-tools-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/pyroomacoustics-candidate-tools-caller-tool/0.1"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
BRANCH = "swarm/SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS"
WORKTREE_PATH = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                 "audio-sdk/SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS")
REVIEWER = "reviewer-PYROOMACOUSTICS-CANDIDATE-TOOLS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"
UPSTREAM_REPOSITORY = "https://github.com/LCAV/pyroomacoustics"
UPSTREAM_DOCS = "https://pyroomacoustics.readthedocs.io/"
CALLER_PACKAGE = "pyroomacoustics"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SPDX_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,63}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SCHEMA_SLUG = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,95}$")
DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace root by fixed markers, not a walk."""
    override = os.environ.get("SOURCE_ROOT")
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

# Read-only inputs. source: paths are workspace-relative; sdk: paths are
# SDK-worktree-relative. The mutable shared board is never pinned.
SOURCE_PINS = {
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/search_log.jsonl":
        "61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
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
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Record version, install location and provenance",
    "Verify a clean checkout or extracted package",
    "one typical CLI/API use",
    "caller-owned inputs",
    "malformed inputs",
    "missing optional selections",
    "Separate compile/build evidence, synthetic runtime evidence and measured "
    "workload support",
)
ROOM_PHRASES = (
    "Freeze render/reference or measured RIRs",
    "Include echo-only, near-end-only, overlap and no-reference cases",
)
SPATIAL_PHRASES = (
    "Record geometry, layout, timestamp calibration, source/target/reference "
    "conditions and permissions",
    "Report leakage, target damage, channel loss, and changes in room/"
    "reference conditions",
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
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".th",
}

# Fixed probes only; no recursive walk and no download. All must stay absent.
WORKSPACE_PROBES = (
    "data/checkouts/pyroomacoustics",
    "data/checkouts/PyRoomAcoustics",
    "data/checkouts/pyroom_acoustics",
    "data/envs/pyroomacoustics",
    "data/envs/pyroomacoustics/requirements.lock",
    "data/models/pyroomacoustics",
    "data/runs/pyroomacoustics",
    "research/pyroomacoustics",
    "reports/pyroomacoustics",
)
WORKTREE_PROBES = (
    "third_party/pyroomacoustics",
    "third_party/PyRoomAcoustics",
    "adapters/pyroomacoustics",
    "bindings/python/pyroomacoustics",
    "build/check-env/lib/python3.12/site-packages/pyroomacoustics",
)
HOME_PROBES = (
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/pyroomacoustics",
    "~/.cache/pip/wheels/pyroomacoustics",
    "~/Library/Caches/pip/wheels/pyroomacoustics",
)

EVIDENCE_INPUT_PATHS = (
    "research/category_registry.json",
    "research/category_survey/sources.md",
    "research/category_survey/search_log.jsonl",
    "audio_categories.md",
    "research/dereverberation_candidates_20261028.md",
    "REALTIME_COMPONENT_CANDIDATES.md",
    "audio-benchmark-platform/plan/INVENTORY.json",
    "audio-benchmark-platform/plan/INVENTORY.md",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
)

TOOL_REQUIREMENTS = (
    ("TR-01", "Record package version, install location and provenance",
     "blocked", "Three registry leads only; no package revision or install."),
    ("TR-02", "Verify a clean checkout or extracted package",
     "blocked", "No source checkout, wheel or extracted package is present."),
    ("TR-03", "Exercise one typical CLI/API use on caller-owned inputs",
     "blocked", "No runnable source, runtime or caller-owned input set."),
    ("TR-04", "Exercise malformed inputs and missing optional selections",
     "documented", "Schema-only rejection cases; no candidate API invoked."),
    ("TR-05", "Separate compile/build, synthetic runtime and measured workload",
     "blocked", "No build, runtime or workload evidence for the candidate."),
    ("TR-06", "Freeze room geometry, layout and timestamp calibration",
     "blocked", "No calibrated array or room geometry is staged."),
    ("TR-07", "Freeze render/reference or measured RIRs and conditions",
     "blocked", "No RIR byte, excitation or condition manifest is staged."),
    ("TR-08", "Separate leakage, target damage, channel loss and room change",
     "blocked", "No measurement and no held-out labels exist."),
    ("TR-09", "Keep permissions and intended-use rights independent",
     "blocked", "No source, RIR, corpus or output-use rights record."),
)

REQUIRED_ARTIFACTS = (
    ("RA-01", "PyRoomAcoustics immutable source revision and reviewed licence"),
    ("RA-02", "Exact wheel/sdist bytes, digests and transitive runtime lock"),
    ("RA-03", "Isolated pinned interpreter and installed package location"),
    ("RA-04", "Room geometry, microphone array and timestamp calibration"),
    ("RA-05", "Frozen measured or caller-simulated RIR and condition manifest"),
    ("RA-06", "Rights-cleared caller-owned array input and held-out labels"),
    ("RA-07", "Reproducible tool run with controls and invalidity outcomes"),
    ("RA-08", "Opt-in OFF-by-default provider/tool intake and review"),
)

BLOCKERS = (
    ("BLK-01", "RA-01", "Source and licence identity",
     "No immutable 40-hex source revision, source digest or reviewed licence "
     "text exists for the three catalogued leads.",
     ("RG-01", "RG-08")),
    ("BLK-02", "RA-02", "Package and runtime pin",
     "No wheel/sdist bytes, wheel digest, transitive dependency lock or "
     "installed-package location is staged for CPython 3.12.16.",
     ("RG-02", "RG-03")),
    ("BLK-03", "RA-03", "Runnable source verification",
     "No clean checkout/extracted package and no typical API/CLI use exists; "
     "the Tool profile cannot be satisfied.",
     ("RG-03", "RG-04")),
    ("BLK-04", "RA-04", "Room and array geometry",
     "No geometry, layout, array calibration, source/target/reference "
     "conditions or timestamp calibration is supplied.",
     ("RG-05", "RG-06")),
    ("BLK-05", "RA-05", "Matched RIR and spatial evidence",
     "No RIR identity, excitation, delay/movement/noise schedule, held-out "
     "labels or separated room/reference conditions exist.",
     ("RG-06", "RG-07")),
    ("BLK-06", "RA-06", "Rights and caller-owned inputs",
     "No caller-owned input set, consent, corpus/RIR terms or output-use "
     "permission is present; no opt-in intake is approved.",
     ("RG-07", "RG-08")),
)

GATES = (
    ("RG-01", "Reviewed source revision and licence text", "BLK-01",
     "Caller supplies an immutable source revision, digest and reviewed "
     "licence/notice set; independent intake confirms the terms."),
    ("RG-02", "Exact package/dependency identity", "BLK-02",
     "Caller supplies wheel/sdist bytes, digests and a locked runtime for the "
     "exact interpreter and platform."),
    ("RG-03", "Clean checkout and one typical tool use", "BLK-03",
     "A clean checkout or extracted package runs one declared CLI/API case on "
     "caller-owned inputs with recorded version and install location."),
    ("RG-04", "Malformed and missing-option controls", "BLK-03",
     "Malformed inputs and missing optional selections are rejected on the "
     "exact pinned runtime without state advance."),
    ("RG-05", "Frozen room/array geometry", "BLK-04",
     "Caller supplies geometry, layout, calibration and source/target/"
     "reference conditions with timestamp alignment."),
    ("RG-06", "Matched RIR and spatial comparisons", "BLK-05",
     "Caller supplies frozen RIR/excitation/condition manifests, held-out "
     "labels and separated leakage/damage/channel-loss/room-change results."),
    ("RG-07", "Caller input rights and consent", "BLK-06",
     "Caller documents input provenance, consent, RIR/corpus terms and output "
     "use permission independently of any quality result."),
    ("RG-08", "Opt-in provider/tool intake and release approval", "BLK-06",
     "A reviewable opt-in OFF-by-default entry passes exact-head review and "
     "explicit public-default approval before any release claim."),
)

NON_CLAIMS = (
    "No PyRoomAcoustics source copy, wheel, extracted package, runtime, "
    "installed module, room geometry, RIR, audio, label or tool output is "
    "present, imported, loaded or executed.",
    "No beamforming, DOA, denoising or room-simulation algorithm is run; the "
    "admission control is a schema object only.",
    "No synthetic room geometry, impulse response or convolution is treated "
    "as real RIR or reverberation evidence.",
    "No listening, matched scoring, device timing, resource or benchmark "
    "result is produced or inherited from adjacent candidates.",
    "The three catalogued source leads are registry excerpts only; no package "
    "revision, licence text or upstream claim is verified locally.",
    "No real or synthetic waveform is read, written, scored or published in "
    "this task-local package.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
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


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


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
# Pinned document projection, fixed probes and absence evidence.
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
        "all_probes_absent": all(row["present"] is False for row in rows),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "candidate_source_imported": False,
        "candidate_package_importable": False,
        "audio_read": False,
        "room_simulation_executed": False,
    }


def evidence_inputs() -> list[dict]:
    rows: list[dict] = []
    for relative in EVIDENCE_INPUT_PATHS:
        payload = (AUDIO_ROOT / relative).read_bytes()
        lowered = payload.lower()
        rows.append({
            "path": relative,
            "sha256": sha256_bytes(payload),
            "mentions_pyroomacoustics":
                b"pyroomacoustics" in lowered,
            "is_result": False,
        })
    return rows


def registry_leads() -> dict:
    """Extract the three inspected PyRoomAcoustics source leads."""
    registry = read_strict_json(AUDIO_ROOT / "research/category_registry.json")
    sources = {row.get("id"): row for row in registry.get("sources", [])
               if isinstance(row, dict)}
    expected = {
        "S16": ("Pyroomacoustics classical denoising implementations",
                "https://pyroomacoustics.readthedocs.io/en/stable/"
                "pyroomacoustics.denoise.html", "direct"),
        "S24": ("Pyroomacoustics beamforming implementation",
                "https://github.com/LCAV/pyroomacoustics/blob/master/"
                "pyroomacoustics/beamforming.py", "search excerpt"),
        "S26": ("Pyroomacoustics direction-of-arrival methods",
                "https://pyroomacoustics.readthedocs.io/en/pypi-release/"
                "pyroomacoustics.doa.html", "search excerpt"),
    }
    rows: list[dict] = []
    for source_id, (title, url, access) in expected.items():
        row = sources.get(source_id)
        if row is None:
            raise ValueError("registry_source_absent:" + source_id)
        if (row.get("title"), row.get("url"), row.get("access_scope")) != \
                (title, url, access):
            raise ValueError("registry_source_mismatch:" + source_id)
        rows.append({
            "source_id": source_id,
            "title": title,
            "url": url,
            "access_scope": access,
            "locally_verified": False,
            "qualifies": False,
        })
    categories = {row.get("id"): row
                  for row in registry.get("categories", [])
                  if isinstance(row, dict)}
    for category_id in ("CLN-01", "CLN-04", "CLN-07", "CLN-08"):
        if category_id not in categories:
            raise ValueError("registry_category_absent:" + category_id)
    return {
        "path": "research/category_registry.json",
        "lead_count": len(rows),
        "leads": rows,
        "category_ids": ["CLN-01", "CLN-04", "CLN-07", "CLN-08"],
        "revision_or_license_present": False,
        "note": "Registry excerpts only; no package byte, revision or "
                "licence text was inspected locally.",
    }


def inventory_row() -> dict:
    document = read_strict_json(AUDIO_ROOT /
                                "audio-benchmark-platform/plan/INVENTORY.json")
    rows = document.get("components") or document.get("entries") or []
    if not isinstance(rows, list):
        raise ValueError("inventory_rows_not_list")
    matches = [row for row in rows if isinstance(row, dict)
               and row.get("id") == COMPONENT_ID]
    if len(matches) != 1:
        raise ValueError("inventory_row_not_unique")
    row = matches[0]
    projection = {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "evidence_status": row.get("evidence_status"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
        "plan_note": row.get("plan_note"),
    }
    if projection != {
            "id": COMPONENT_ID,
            "name": TASK_TITLE,
            "area": "Runtime and tooling",
            "repository": REPOSITORY,
            "disposition": "sdk-tool",
            "evidence_status": "considered",
            "verification_profile": PROFILE,
            "task": TASK,
            "plan_note": "Use inspected beamforming, RIR and room-simulation "
                         "tools in reproducible benchmark recipes.",
    }:
        raise ValueError("inventory_row_mismatch")
    return projection


def profile_row_check() -> dict:
    source = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = source.read_text(encoding="utf-8")
    result: dict[str, Any] = {
        "path": PROFILE_SOURCE_REL,
        "rows": {},
        "phrases_all_present": True,
    }
    for label, phrases in (("Tool", PROFILE_PHRASES),
                           ("Room", ROOM_PHRASES),
                           ("Spatial", SPATIAL_PHRASES)):
        rows = [line for line in text.splitlines()
                if line.startswith("| " + label + " |")]
        if len(rows) != 1:
            result["phrases_all_present"] = False
            result["rows"][label] = {"row_count": len(rows),
                                     "phrases_present": False}
            continue
        missing = [phrase for phrase in phrases if phrase not in rows[0]]
        result["rows"][label] = {
            "row_count": 1,
            "phrases_present": not missing,
            "missing_phrases": missing,
        }
        if missing:
            result["phrases_all_present"] = False
    return result


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
    return [name for name in LOCAL_FILES if name != "SOURCES.sha256"]


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, digest in SOURCE_PINS.items():
        path = AUDIO_ROOT / relative
        actual = sha256_file(path) if path.is_file() else None
        if actual != digest:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        path = WORKTREE / relative
        actual = sha256_file(path) if path.is_file() else None
        if actual != digest:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((sha256_file(path), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:")
                or path.startswith(TASK_PREFIX)):
            raise ValueError("unknown_pin_prefix:" + str(number))
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


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
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
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
# Caller-supplied tool reference: schema-only admission control.
# ---------------------------------------------------------------------------


class _Invalid(Exception):
    pass


MANIFEST_FIELDS = {
    "schema_id", "manifest_id", "tool", "geometry", "evidence", "inputs",
    "controls", "rights",
}
TOOL_FIELDS = {
    "package_name", "source_revision", "source_sha256", "source_license_spdx",
    "license_text_sha256", "wheel_sha256", "install_location", "interpreter",
    "runtime_packages",
}
RUNTIME_FIELDS = {"numpy", "scipy", "numba"}
GEOMETRY_FIELDS = {
    "sample_rate_hz", "channels", "room_dimensions_m", "microphone_positions_m",
    "source_positions_m", "calibration_sha256", "frame_samples", "hop_samples",
}
EVIDENCE_FIELDS = {
    "rir_sha256", "rir_kind", "conditions_sha256", "geometry_sha256",
    "labels_sha256", "room_count", "simulation_label",
    "simulation_not_real_rir_evidence",
}
INPUT_FIELDS = {"source_id", "rights_sha256", "consent", "caller_owned"}
CONTROL_FIELDS = {
    "identity_control", "noisy_control", "geometry_mismatch_rejection",
    "malformed_input_rejection", "missing_optional_selection_rejection",
    "nonfinite_input_rejection",
}
RIGHT_FIELDS = {"source_terms_verified", "rir_terms_verified",
                "output_use_permitted"}


def _exact_object(value: Any, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise _Invalid(label + "_not_object")
    if set(value) != fields:
        raise _Invalid(label + "_fields")
    return value


def _text(value: Any, field: str, pattern: re.Pattern | None = None,
          limit: int = 240) -> None:
    if not isinstance(value, str) or not value or len(value) > limit:
        raise _Invalid(field + "_invalid_text")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise _Invalid(field + "_invalid_text")


def _sha(value: Any, field: str) -> None:
    _text(value, field, HEX64, 64)


def _revision(value: Any, field: str) -> None:
    _text(value, field, HEX40, 40)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise _Invalid(field + "_not_boolean")


def _integer(value: Any, field: str, low: int, high: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) \
            or value < low or value > high:
        raise _Invalid(field + "_out_of_range")


def _safe_relative(value: Any, field: str) -> None:
    _text(value, field, None, 240)
    if value.startswith(("/", "\\")) or ".." in Path(value).parts \
            or "\\" in value or ":" in value:
        raise _Invalid(field + "_unsafe_path")


def _decimal(value: Any, field: str) -> None:
    _text(value, field, DECIMAL, 40)


def _vector(value: Any, field: str, low: int, high: int) -> list:
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise _Invalid(field + "_bad_vector")
    for index, item in enumerate(value):
        _decimal(item, field + "_" + str(index))
    return value


def validate_manifest(document: Any) -> dict:
    """Fail-closed schema check; never imports, loads or runs anything."""
    try:
        if not isinstance(document, dict):
            raise _Invalid("root_not_object")
        _exact_object(document, MANIFEST_FIELDS, "root")
        _text(document["schema_id"], "schema_id", SCHEMA_SLUG, 96)
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("schema_id_mismatch")
        _text(document["manifest_id"], "manifest_id", SLUG, 64)

        tool = _exact_object(document["tool"], TOOL_FIELDS, "tool")
        if tool["package_name"] != CALLER_PACKAGE:
            raise _Invalid("package_name_mismatch")
        _revision(tool["source_revision"], "source_revision")
        _sha(tool["source_sha256"], "source_sha256")
        _text(tool["source_license_spdx"], "source_license_spdx", SPDX_TOKEN,
              64)
        if tool["source_license_spdx"].upper() in {"NOASSERTION", "UNKNOWN"}:
            raise _Invalid("source_license_unresolved")
        _sha(tool["license_text_sha256"], "license_text_sha256")
        _sha(tool["wheel_sha256"], "wheel_sha256")
        _safe_relative(tool["install_location"], "install_location")
        _text(tool["interpreter"], "interpreter", VERSION, 16)
        if tool["interpreter"] != REQUIRED_INTERPRETER:
            raise _Invalid("interpreter_mismatch")
        runtime = _exact_object(tool["runtime_packages"], RUNTIME_FIELDS,
                                "runtime_packages")
        for name in sorted(runtime):
            entry = _exact_object(runtime[name], {"version", "wheel_sha256"},
                                  "runtime_" + name)
            _text(entry["version"], "runtime_" + name + "_version", VERSION,
                  32)
            _sha(entry["wheel_sha256"], "runtime_" + name + "_wheel_sha256")

        geometry = _exact_object(document["geometry"], GEOMETRY_FIELDS,
                                 "geometry")
        _integer(geometry["sample_rate_hz"], "sample_rate_hz", 16000, 192000)
        if geometry["sample_rate_hz"] != 16000:
            raise _Invalid("sample_rate_mismatch")
        _integer(geometry["channels"], "channels", 2, 32)
        _vector(geometry["room_dimensions_m"], "room_dimensions_m", 3, 3)
        microphones = geometry["microphone_positions_m"]
        if not isinstance(microphones, list) or not 2 <= len(microphones) <= 32:
            raise _Invalid("microphone_positions_m_bad_matrix")
        for index, position in enumerate(microphones):
            _vector(position, "microphone_positions_m_" + str(index), 3, 3)
        sources = geometry["source_positions_m"]
        if not isinstance(sources, list) or not 1 <= len(sources) <= 32:
            raise _Invalid("source_positions_m_bad_matrix")
        for index, position in enumerate(sources):
            _vector(position, "source_positions_m_" + str(index), 3, 3)
        _sha(geometry["calibration_sha256"], "calibration_sha256")
        _integer(geometry["frame_samples"], "frame_samples", 64, 4096)
        _integer(geometry["hop_samples"], "hop_samples", 1, 2048)
        if geometry["hop_samples"] > geometry["frame_samples"]:
            raise _Invalid("hop_exceeds_frame")

        evidence = _exact_object(document["evidence"], EVIDENCE_FIELDS,
                                 "evidence")
        _sha(evidence["rir_sha256"], "rir_sha256")
        _text(evidence["rir_kind"], "rir_kind", None, 32)
        if evidence["rir_kind"] not in ("measured", "caller_simulated"):
            raise _Invalid("rir_kind_invalid")
        for name in ("conditions_sha256", "geometry_sha256", "labels_sha256"):
            _sha(evidence[name], name)
        _integer(evidence["room_count"], "room_count", 1, 1000)
        _text(evidence["simulation_label"], "simulation_label", SLUG, 64)
        if evidence["simulation_label"] not in (
                "synthetic_geometry_control", "measured_rir"):
            raise _Invalid("simulation_label_invalid")
        _boolean(evidence["simulation_not_real_rir_evidence"],
                 "simulation_not_real_rir_evidence")
        if evidence["simulation_not_real_rir_evidence"] is not True:
            raise _Invalid("simulation_claim_promoted")

        inputs = _exact_object(document["inputs"], INPUT_FIELDS, "inputs")
        _text(inputs["source_id"], "source_id", SLUG, 64)
        _sha(inputs["rights_sha256"], "rights_sha256")
        _boolean(inputs["consent"], "consent")
        if inputs["consent"] is not True:
            raise _Invalid("consent_missing")
        _boolean(inputs["caller_owned"], "caller_owned")
        if inputs["caller_owned"] is not True:
            raise _Invalid("caller_ownership_missing")

        controls = _exact_object(document["controls"], CONTROL_FIELDS,
                                 "controls")
        for name in sorted(controls):
            _boolean(controls[name], name)
            if controls[name] is not True:
                raise _Invalid("control_false:" + name)

        rights = _exact_object(document["rights"], RIGHT_FIELDS, "rights")
        for name in sorted(rights):
            _boolean(rights[name], name)
            if rights[name] is not True:
                raise _Invalid("rights_unverified:" + name)
    except _Invalid as error:
        return {
            "status": "rejected",
            "code": str(error),
            "state_unchanged": True,
            "qualifies": False,
        }
    return {
        "status": "accepted",
        "code": "schema_control_only",
        "state_unchanged": True,
        "qualifies": False,
        "synthetic_schema_control": True,
        "not_real_rir_evidence": True,
        "runtime_invoked": False,
    }


def _manifest_control() -> dict:
    digest = "0" * 64
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "synthetic-geometry-control",
        "tool": {
            "package_name": CALLER_PACKAGE,
            "source_revision": "0" * 40,
            "source_sha256": digest,
            "source_license_spdx": "Apache-2.0",
            "license_text_sha256": digest,
            "wheel_sha256": digest,
            "install_location": "build/check-env/pyroomacoustics",
            "interpreter": REQUIRED_INTERPRETER,
            "runtime_packages": {
                name: {"version": "1.0.0", "wheel_sha256": digest}
                for name in sorted(RUNTIME_FIELDS)
            },
        },
        "geometry": {
            "sample_rate_hz": 16000,
            "channels": 2,
            "room_dimensions_m": ["5", "4", "3"],
            "microphone_positions_m": [["1", "2", "1.5"],
                                       ["2", "2", "1.5"]],
            "source_positions_m": [["3", "2", "1.5"]],
            "calibration_sha256": digest,
            "frame_samples": 512,
            "hop_samples": 256,
        },
        "evidence": {
            "rir_sha256": digest,
            "rir_kind": "caller_simulated",
            "conditions_sha256": digest,
            "geometry_sha256": digest,
            "labels_sha256": digest,
            "room_count": 1,
            "simulation_label": "synthetic_geometry_control",
            "simulation_not_real_rir_evidence": True,
        },
        "inputs": {
            "source_id": "caller-owned-control",
            "rights_sha256": digest,
            "consent": True,
            "caller_owned": True,
        },
        "controls": {name: True for name in sorted(CONTROL_FIELDS)},
        "rights": {name: True for name in sorted(RIGHT_FIELDS)},
    }


def _mutate(field: str, value: Any):
    def apply(document: dict) -> None:
        document[field] = value
    return apply


def _mutate_nested(section: str, field: str, value: Any):
    def apply(document: dict) -> None:
        document[section][field] = value
    return apply


def _delete_nested(section: str, field: str):
    def apply(document: dict) -> None:
        document[section].pop(field, None)
    return apply


ADMISSION_CASES = (
    ("AC-01", "accepted_schema_control", None, "accepted"),
    ("RJ-01", "duplicate_json_key", '{"schema_id":"a","schema_id":"b"}',
     "duplicate_json_key"),
    ("RJ-02", "nonfinite_json", '{"schema_id":NaN}', "nonfinite_json"),
    ("RJ-03", "float_not_allowed", '{"schema_id":1.5}', "float_not_allowed"),
    ("RJ-04", "json_root_not_object", "[]", "json_root_not_object"),
    ("RJ-05", "wrong_schema_id",
     _mutate("schema_id", "audio-sdk/unknown/0.1"), "schema_id_mismatch"),
    ("RJ-06", "unresolved_source_license",
     _mutate_nested("tool", "source_license_spdx", "NOASSERTION"),
     "source_license_unresolved"),
    ("RJ-07", "wrong_interpreter",
     _mutate_nested("tool", "interpreter", "3.11.5"),
     "interpreter_mismatch"),
    ("RJ-08", "missing_source_revision",
     _delete_nested("tool", "source_revision"), "tool_fields"),
    ("RJ-09", "unknown_top_level_field", _mutate("unexpected", 1),
     "root_fields"),
    ("RJ-10", "mono_geometry_rejected",
     _mutate_nested("geometry", "channels", 1), "channels_out_of_range"),
    ("RJ-11", "rir_identity_missing",
     _mutate_nested("evidence", "rir_sha256", None), "rir_sha256_invalid_text"),
    ("RJ-12", "geometry_mismatch_control_false",
     _mutate_nested("controls", "geometry_mismatch_rejection", False),
     "control_false:geometry_mismatch_rejection"),
    ("RJ-13", "missing_optional_selection_false",
     _mutate_nested("controls", "missing_optional_selection_rejection", False),
     "control_false:missing_optional_selection_rejection"),
    ("RJ-14", "unconsented_input",
     _mutate_nested("inputs", "consent", False), "consent_missing"),
    ("RJ-15", "output_rights_unverified",
     _mutate_nested("rights", "output_use_permitted", False),
     "rights_unverified:output_use_permitted"),
    ("RJ-16", "unsafe_install_location",
     _mutate_nested("tool", "install_location", "../outside"),
     "install_location_unsafe_path"),
    ("RJ-17", "simulation_claim_promoted",
     _mutate_nested("evidence", "simulation_not_real_rir_evidence", False),
     "simulation_claim_promoted"),
    ("RJ-18", "missing_calibration_identity",
     _delete_nested("geometry", "calibration_sha256"),
     "geometry_fields"),
)


def admission_controls() -> dict:
    rows: list[dict] = []
    for case_id, label, mutation, expected in ADMISSION_CASES:
        if mutation is None:
            document = _manifest_control()
            source = "schema_control"
        elif isinstance(mutation, str):
            document = None
            source = "raw_json"
        else:
            document = copy.deepcopy(_manifest_control())
            mutation(document)
            source = "mutated_schema_control"
        try:
            result = (validate_manifest(document) if document is not None
                      else {"status": "rejected",
                            "code": _raw_failure_code(mutation),
                            "state_unchanged": True,
                            "qualifies": False})
        except ValueError as error:
            result = {"status": "rejected", "code": str(error),
                      "state_unchanged": True, "qualifies": False}
        code = result.get("code", "")
        rows.append({
            "id": case_id,
            "case": label,
            "source": source,
            "status": result["status"],
            "code": code,
            "state_unchanged": result["state_unchanged"],
            "qualifies": result["qualifies"],
            "synthetic_schema_control": result.get(
                "synthetic_schema_control", False),
            "not_real_rir_evidence": result.get("not_real_rir_evidence", False),
            "expected": expected,
            "matches_expected": ((code == expected and
                                  result["status"] == "rejected")
                                 if result["status"] == "rejected"
                                 else result["status"] == expected),
        })
    rejected = [row for row in rows if row["status"] == "rejected"]
    summary = {
        "case_count": len(rows),
        "accepted_schema_controls": len(rows) - len(rejected),
        "qualifying_results": 0,
        "rejected_count": len(rejected),
        "all_cases_match_expected":
            all(row["matches_expected"] for row in rows),
        "all_rejected_state_unchanged":
            all(row["state_unchanged"] for row in rejected),
        "state_advanced_on_rejection": False,
        "runtime_invoked": False,
        "candidate_source_imported": False,
        "audio_read": False,
        "network_used": False,
        "synthetic_control_is_not_real_rir_evidence": True,
    }
    return {"controls": _admission_contract_block(),
            "cases": rows, "summary": summary}


def _raw_failure_code(raw: str) -> str:
    try:
        loads_strict(raw)
    except ValueError as error:
        return str(error).split(":", 1)[0]
    return "raw_case_accepted"


def _admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "validation_only": True,
        "top_level_fields": sorted(MANIFEST_FIELDS),
        "tool_fields": sorted(TOOL_FIELDS),
        "geometry_fields": sorted(GEOMETRY_FIELDS),
        "evidence_fields": sorted(EVIDENCE_FIELDS),
        "input_fields": sorted(INPUT_FIELDS),
        "control_fields": sorted(CONTROL_FIELDS),
        "rights_fields": sorted(RIGHT_FIELDS),
        "required_interpreter": REQUIRED_INTERPRETER,
        "required_channels_min": 2,
        "required_channels_max": 32,
        "required_sample_rate_hz": 16000,
        "float_rejected": True,
        "nonfinite_rejected": True,
        "duplicate_keys_rejected": True,
        "unsafe_path_rejected": True,
        "unresolved_license_rejected": True,
        "synthetic_geometry_control_label_required": True,
        "synthetic_control_qualifies": False,
        "synthetic_control_is_not_real_rir_evidence": True,
        "max_cases": 64,
    }


# ---------------------------------------------------------------------------
# Canonical contract and report.
# ---------------------------------------------------------------------------


def _requirement_rows() -> list[dict]:
    return [{"id": case_id, "requirement": text, "status": status,
             "evidence": evidence, "qualifies": False}
            for case_id, text, status, evidence in TOOL_REQUIREMENTS]


def _artifact_rows() -> list[dict]:
    return [{"id": case_id, "artifact": text, "present": False,
             "verified": False, "sha256": None, "revision": None,
             "bytes": None, "blocked": True}
            for case_id, text in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{"id": case_id, "artifact_id": artifact, "title": title,
             "detail": detail, "status": "open", "qualifies": False,
             "linked_gates": list(gates), "reopen_condition":
             "See the matching release gate in this package."}
            for case_id, artifact, title, detail, gates in BLOCKERS]


def _gate_rows() -> list[dict]:
    return [{"id": case_id, "requirement": text, "status": "blocked",
             "blocked_by": blocker, "qualifies": False,
             "linked_row": TASK, "reopen_condition": reopen}
            for case_id, text, blocker, reopen in GATES]


def task_geometry() -> dict:
    return {
        "task": "Catalogued denoise, beamforming and DOA tooling; "
                "room-simulation/RIR recipe lead",
        "reported_input": "Mono or synchronized microphone array with "
                          "declared geometry",
        "channels_min": 2,
        "channels_max": 32,
        "sample_rate_hz": 16000,
        "frame_samples": None,
        "hop_samples": None,
        "room_dimensions_m": None,
        "microphone_positions_m": None,
        "source_positions_m": None,
        "timestamp_calibration": None,
        "rir_identity": None,
        "excitation": None,
        "delay_movement_noise_schedule": None,
        "held_out_labels": None,
        "exact_geometry_verified": False,
        "sdk_v0_adapter_mapping_present": False,
        "synthetic_geometry_control_present_in_manifest_schema": True,
        "synthetic_control_label": "synthetic_geometry_control",
        "synthetic_control_is_real_rir_evidence": False,
        "note": "The schema control declares an array in a synthetic room. "
                "It is not an RIR, a convolution, a reverberation measurement "
                "or a spatial result.",
    }


def matched_evidence_boundary() -> dict:
    return {
        "adjacent_components": [
            "delay-and-sum-beamformer", "mvdr-beamforming",
            "offline-multichannel-wpe", "online-multichannel-wpe",
            "survey-cln-07", "survey-cln-08",
        ],
        "results_promoted": False,
        "note": "Adjacent synthetic fixtures, WPE screens and survey records "
                "belong to other components. Their scores, room conditions "
                "and timings are not PyRoomAcoustics results.",
        "synthetic_controls_not_real_rir_evidence": True,
    }


def rights_gap() -> list[dict]:
    return [{"id": "RGAP-%02d" % index, "requirement": text,
             "status": "blocked", "qualifies": False}
            for index, text in enumerate((
                "Reviewed PyRoomAcoustics source and wheel licence text",
                "Transitive runtime package licences and notices",
                "Room/RIR corpus terms, attribution and redistribution scope",
                "Caller-owned input consent and speaker privacy",
                "Output use, publication and default-package admission"),
            start=1)]


def qualification_block() -> dict:
    return {
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "all_release_gates_blocked": True,
        "recorded_identity_only": True,
        "schema_control_only": True,
        "real_result_present": False,
        "source_present": False,
        "exact_source_identity": False,
        "source_license_verified": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "wheel_identity_verified": False,
        "room_geometry_verified": False,
        "rir_evidence_present": False,
        "matched_labels_present": False,
        "rights_cleared_inputs": False,
        "implementation_present": False,
        "reference_execution_result": False,
        "tool_profile_result": False,
        "room_spatial_result": False,
        "listening_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
        "synthetic_control_promoted": False,
    }


def disposition_block() -> dict:
    return {
        "component_id": COMPONENT_ID,
        "evidence_status": EVIDENCE_STATUS,
        "disposition": "sdk-tool",
        "verification_profile": PROFILE,
        "inventory_row": inventory_row(),
        "row_digest": object_digest(inventory_row()),
        "is_result": False,
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "write_prefix": TASK_PREFIX,
        "provider_changed": False,
        "descriptor_changed": False,
        "registry_changed": False,
        "default_changed": False,
        "public_header_changed": False,
        "abi_changed": False,
        "shared_cmake_changed": False,
        "ci_workflow_changed": False,
        "installed_v0_behavior_changed": False,
        "board_changed": False,
        "handoff_changed": False,
        "network_used": False,
        "download_attempted": False,
    }


def boundary_block() -> dict:
    return {
        "docs_only": True,
        "task_local_directory": TASK_PREFIX,
        "source_and_boundary_files_read_only": True,
        "mutable_board_never_hashed": True,
        "candidate_code_vendored": False,
        "audio_or_asset_bytes_present": False,
        "reviewers_dispatched": False,
        "merged": False,
    }


def linked_identity_block() -> dict:
    return {
        "board_path": BOARD_TASK_ROW,
        "projection_fields": list(BOARD_ROW_FIELDS),
        "task_projection": board_row_projection(),
        "task_projection_sha256": board_row_digest(),
        "linked_row_count": len(LINKED_ROW_IDS),
        "linked_rows_sha256": linked_rows_digest(),
        "mutable_fields_excluded": True,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task_id": TASK,
        "component_id": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "exact_interpreter": REQUIRED_INTERPRETER,
        "reported_source_leads": registry_leads(),
        "disposition": disposition_block(),
        "scope": scope_block(),
        "exact_scope": {
            "included": [TASK_PREFIX],
            "excluded": ["sdk provider", "descriptor/registry/default",
                         "public ABI", "shared build", "CI", "board/handoff",
                         "real audio", "download"],
        },
        "boundary": boundary_block(),
        "public_v0_geometry": {
            "channels": 1, "sample_rate_hz": 16000, "frame_samples": 160,
            "sample_format": "f32", "note": "Preserved, not mapped to the "
            "multichannel candidate; no descriptor or provider is added.",
        },
        "task_geometry": task_geometry(),
        "matched_evidence_boundary": matched_evidence_boundary(),
        "profile_source_check": profile_row_check(),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": _admission_contract_block(),
        "rights_gap": rights_gap(),
        "qualification": qualification_block(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = build_contract()
    admission = admission_controls()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "component_id": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "contract_sha256": object_digest(contract),
        "disposition": contract["disposition"],
        "boundary": contract["boundary"],
        "scope": contract["scope"],
        "exact_scope": contract["exact_scope"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "task_geometry": contract["task_geometry"],
        "upstream_record": contract["reported_source_leads"],
        "matched_evidence_boundary": contract["matched_evidence_boundary"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "tool_profile": {
            "profile_source": PROFILE_SOURCE_REL,
            "profile_source_check": contract["profile_source_check"],
            "requirement_rows": _requirement_rows(),
            "row_summary": {
                "requirement_count": len(TOOL_REQUIREMENTS),
                "real_result_count": 0,
                "profile_satisfied": False,
            },
        },
        "admission": admission,
        "absence_evidence": {
            "workspace_probes": workspace_probes(),
            "worktree_probes": worktree_probes(),
            "home_probes": home_probes(),
            "summary": absence_summary(),
        },
        "evidence_inputs": evidence_inputs(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "rights_gap": contract["rights_gap"],
        "qualification": contract["qualification"],
        "linked_row_identity": linked_identity_block(),
        "prohibited_claims": list(NON_CLAIMS),
    }


def validate_contract(contract: dict) -> None:
    expected_keys = {
        "schema_id", "contract_id", "task_id", "component_id", "title",
        "mode", "profile", "base_commit", "branch", "exact_interpreter",
        "reported_source_leads", "disposition", "scope", "exact_scope",
        "boundary", "public_v0_geometry", "task_geometry",
        "matched_evidence_boundary", "profile_source_check",
        "required_artifacts", "exact_blockers", "release_gates",
        "admission_contract", "rights_gap", "qualification", "non_claims",
    }
    if set(contract) != expected_keys:
        raise ValueError("contract_fields")
    if contract["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if len(contract["required_artifacts"]) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if len(contract["exact_blockers"]) != len(BLOCKERS):
        raise ValueError("contract_blocker_count")
    if len(contract["release_gates"]) != len(GATES):
        raise ValueError("contract_gate_count")
    if any(row["status"] != "blocked" for row in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if any(row["status"] != "open" for row in contract["exact_blockers"]):
        raise ValueError("contract_blocker_not_open")
    if any(row["present"] is not False or row["verified"] is not False
           for row in contract["required_artifacts"]):
        raise ValueError("contract_artifact_present")
    if contract["profile_source_check"]["phrases_all_present"] is not True:
        raise ValueError("contract_profile_phrases")


# ---------------------------------------------------------------------------
# Task-local git scope. The base is the newest merge-base with a PR base ref.
# ---------------------------------------------------------------------------

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


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
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
