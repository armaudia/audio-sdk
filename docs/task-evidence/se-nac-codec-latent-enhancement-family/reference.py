# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only readiness evidence for SDK-SE-NAC-....

This module records the SE-NAC codec-latent enhancement family boundary. The
pinned census and candidate-store snapshots describe a released family of
discrete/continuous and autoregressive/non-autoregressive codec-latent speech
enhancement checkpoints plus an STFT-NAR control, with LibriMix task data and
unverified code/weight identity, terms and sample rate. No source checkout,
model byte, runtime dependency lock, reviewed license, rights-cleared cohort,
enhanced output, listening result, device timing, benchmark or release claim is
present in this workspace.

Nothing here downloads, installs, imports, loads or executes a model, codec or
audio runtime; no network, audio device or real audio is used. The package
produces a strict DEFER / incomplete / not_qualified readiness record, models a
fail-closed caller-supplied-asset manifest without executing it, and proves with
deterministic adverse controls that invalid, missing, unreviewed or
non-16 kHz inputs are rejected.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Task identity and fixed task facts.
# ---------------------------------------------------------------------------

TASK = "SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY"
TASK_TITLE = "SE-NAC codec-latent enhancement family"
COMPONENT_ID = "se-nac-codec-latent-enhancement-family"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/se-nac-codec-latent-enhancement-family/ only"
TASK_PREFIX = "docs/task-evidence/se-nac-codec-latent-enhancement-family/"
CONTRACT_ID = "audio-sdk/se-nac-codec-latent-enhancement-family-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/se-nac-codec-latent-enhancement-family-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/se-nac-codec-latent-enhancement-family-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/se-nac-codec-latent-enhancement-family-caller-asset/0.1"
BASE_COMMIT = "a51e49f718500ec9e81242cf2816f0b576333d00"
BRANCH = "swarm/SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/"
    "audio-sdk/SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY")
REVIEWER = "reviewer-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"

FAMILY_NAME = "SE-NAC codec-latent speech enhancement family"
MODEL_CARD_SOURCE = "https://huggingface.co/SofieneK/SE-NAC"
PAPER_SOURCE = "https://arxiv.org/abs/2510.26299"
CENSUS_LINE = 67

REPORTED_VARIANTS = ("D-AR", "D-NAR", "D-NAR*", "C-AR", "C-NAR", "C-FT",
                     "D-FT", "STFT-NAR")
REPORTED_DATASET = "LibriMix"
REPORTED_SAMPLE_RATE_HZ = None
REPORTED_REPORTED_ONLY = True
REPORTED_CODE_STATE = "available"
REPORTED_WEIGHTS_STATE = "located_unverified"
REPORTED_BENCHMARK_STATE = "not_run"
REPORTED_ELIGIBILITY_STATE = "blocked"
REPORTED_ELIGIBILITY_REASON = (
    "Official checkpoint card and paper are available, but upstream code "
    "linkage, artifact hashes/terms, codec dependencies and local isolated "
    "inference costs are not verified; candidate inference is blocked by "
    "unavailable enforced worker sandbox.")

# Installed public v0 geometry. This is a contract fact, not a model mapping.
V0_SAMPLE_RATE_HZ = 16000
V0_CHANNELS = 1
V0_FRAME_SAMPLES = 160
V0_SAMPLE_FORMAT = "float32"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIO_ROOT")
    candidates = [
        Path(override) if override else None,
        SDK_ROOT.parents[2],
        Path("/Users/htsakanyan/workspace/audio/audioml"),
    ]
    marker = "research/noise_suppression_candidate_census.md"
    for candidate in candidates:
        if candidate is not None and (candidate / marker).is_file():
            return candidate.resolve()
    raise RuntimeError("audioml workspace root is unavailable")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/store/snapshots/"
    "e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380cca1d5dc6537.jsonl":
        "e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380cca1d5dc6537",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS: dict[str, str] = {
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
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

STORE_METHOD_ID = "method-se-nac"
STORE_CANDIDATE_ID = "candidate-se-nac-family"

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

# Fixed probes only; no recursive walk and no network. All must stay absent.
WORKSPACE_PROBES = (
    "data/checkouts/se-nac",
    "data/checkouts/SE-NAC",
    "data/checkouts/se-nac-codec-latent-enhancement-family",
    "data/runtimes/se-nac",
    "data/models/se-nac",
    "data/models/SE-NAC",
    "data/models/se-nac-codec-latent-enhancement-family",
    "data/licenses/se-nac",
    "data/licenses/se-nac-codec-latent-enhancement-family",
    "data/manifests/se-nac-codec-latent-enhancement-family.json",
    "data/runs/se-nac-codec-latent-enhancement-family/manifest.json",
    "research/voice-enhancement-20261101/repos/se-nac",
    "research/voice-enhancement-20261101/repos/SE-NAC",
)
WORKTREE_PROBES = (
    "third_party/se-nac",
    "adapters/se-nac-codec-latent-enhancement-family",
    "schemas/providers/se-nac-codec-latent-enhancement-family.descriptor.json",
)
HOME_PROBES = (
    "~/.cache/se-nac",
    "~/.cache/huggingface/hub/models--SofieneK--SE-NAC",
    "~/Library/Application Support/SE-NAC",
    "~/Library/Application Support/se-nac",
)

NON_CLAIMS = [
    "No SE-NAC source revision, checkpoint byte, codec runtime, dependency "
    "lock, reviewed license or caller asset is loaded, downloaded, installed "
    "or executed.",
    "No network request, Hugging Face download, account creation, model API "
    "call or asset redistribution occurs.",
    "No real audio, rights-cleared cohort, clean reference, label, listening "
    "result, device timing or public benchmark is used.",
    "No source-reported author metric is reproduced, pooled, scored or "
    "promoted to a local result.",
    "Missing, unverified or caller-supplied assets never qualify the "
    "candidate; the decision remains DEFER.",
    "No provider, descriptor, registry, default, installed v0 path, ABI, "
    "shared build, CI, board, handoff or release changed.",
]

PEER_EVIDENCE = (
    "dac-se1",
    "llase-g1",
    "cisco-stupase",
    "dblm-se-1b",
    "survey-rst-03",
)
HISTORICAL_EVIDENCE = (
    "research/noise_suppression_pilot_20261027.md",
    "research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md",
    "research/voice-enhancement-20261101/evaluation_records.md",
)

# ---------------------------------------------------------------------------
# Strict JSON, canonical bytes and digests.
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


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


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
    return text, sha256_bytes((text + "\n").encode("ascii"))


def canonical_report_bytes(report: dict | None = None) -> bytes:
    return (canonical_text(build_report() if report is None else report)
            + "\n").encode("ascii")


def canonical_contract_bytes() -> bytes:
    return (canonical_text(build_contract()) + "\n").encode("ascii")


# ---------------------------------------------------------------------------
# Stable board identity. The mutable TASKS.json bytes are never hashed.
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
# Fixed absence probes. No recursive walk, no network, no model import.
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
    return [_probe(SDK_ROOT / path, path, False, True, False)
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
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
    }


def asset_registry() -> dict:
    """Summarize the local asset register without inventing an SE-NAC entry."""
    path = AUDIO_ROOT / "research/noise_suppression_assets_20261027.json"
    document = read_strict_json(path)
    candidates = document.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("asset_register_candidates_not_list")
    ids = sorted(row.get("id") for row in candidates
                 if isinstance(row, dict) and isinstance(row.get("id"), str))
    if len(ids) != len(set(ids)):
        raise ValueError("asset_register_duplicate_id")
    family_ids = [row_id for row_id in ids
                  if "se-nac" in row_id.lower() or "nac" in row_id.lower()]
    return {
        "path": "research/noise_suppression_assets_20261027.json",
        "candidate_count": len(ids),
        "candidate_ids_sha256": object_digest(ids),
        "family_entry_present": bool(family_ids),
        "family_candidate_ids": family_ids,
        "asset_identity_available_for_family": False,
        "note": "The register contains 20 separately evaluated denoising "
                "assets and no SE-NAC candidate, checkpoint revision, byte "
                "count, SHA-256 or terms record.",
    }


EVIDENCE_INPUT_PATHS = (
    "research/noise_suppression_candidate_census.md",
    "research/noise_suppression_assets_20261027.json",
    "research/voice-enhancement-20261101/candidate_matrix.csv",
    "research/store/snapshots/"
    "e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380cca1d5dc6537.jsonl",
    "audio-benchmark-platform/plan/INVENTORY.json",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
)


def evidence_inputs() -> list[dict]:
    rows: list[dict] = []
    for relative in EVIDENCE_INPUT_PATHS:
        payload = (AUDIO_ROOT / relative).read_bytes()
        rows.append({
            "path": relative,
            "sha256": sha256_bytes(payload),
            "mentions_family": (b"se-nac" in payload.lower()),
            "is_model_result": False,
            "is_rights_record": False,
            "is_asset_identity": False,
        })
    return rows


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
# Task, family and geometry records. Every source-reported fact is labelled.
# ---------------------------------------------------------------------------


def family_record() -> dict:
    return {
        "family_name": FAMILY_NAME,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "model_card_source": MODEL_CARD_SOURCE,
        "paper_source": PAPER_SOURCE,
        "source_revision": None,
        "checkpoint_variant": None,
        "checkpoint_revision": None,
        "checkpoint_sha256": None,
        "checkpoint_byte_count": None,
        "code_state_reported": REPORTED_CODE_STATE,
        "weights_state_reported": REPORTED_WEIGHTS_STATE,
        "benchmark_state_reported": REPORTED_BENCHMARK_STATE,
        "eligibility_state_reported": REPORTED_ELIGIBILITY_STATE,
        "eligibility_reason_reported": REPORTED_ELIGIBILITY_REASON,
        "locally_verified": False,
        "admitted_as_result": False,
        "qualifies": False,
        "note": "All facts come from the pinned census and candidate-store "
                "snapshots. No source revision, checkpoint byte, terms text, "
                "codec runtime or dependency lock is present locally.",
    }


def recorded_identity_block() -> dict:
    return {
        "label": "source_reported_not_locally_verified",
        "census": {
            "path": "research/noise_suppression_candidate_census.md",
            "line": CENSUS_LINE,
            "finding": "Neural audio-codec representation speech enhancement; "
                       "discrete/continuous and autoregressive/"
                       "non-autoregressive variants",
            "reported": "Official model card publishes multiple pretrained "
                        "checkpoints and cites ICASSP 2026; task data is "
                        "LibriMix. Includes a STFT-NAR control variant.",
            "disposition": "Valuable offline architecture-family comparison, "
                           "but codec token generation may be costly and "
                           "output fidelity is a concern. Pin corresponding "
                           "code and weights, validate license/data lineage, "
                           "and assess noise-only behavior, WER/content "
                           "preservation and runtime before selection.",
        },
        "candidate_store": {
            "snapshot": "research/store/snapshots/"
                        "e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380"
                        "cca1d5dc6537.jsonl",
            "method_id": STORE_METHOD_ID,
            "candidate_id": STORE_CANDIDATE_ID,
            "architecture": "neural audio-codec latent speech enhancement; "
                            "AR/NAR discrete/continuous",
            "dataset_reported": REPORTED_DATASET,
            "reported_only": REPORTED_REPORTED_ONLY,
            "sample_rate_hz_reported": REPORTED_SAMPLE_RATE_HZ,
            "variants": list(REPORTED_VARIANTS),
            "code": REPORTED_CODE_STATE,
            "weights": REPORTED_WEIGHTS_STATE,
            "benchmark_state": REPORTED_BENCHMARK_STATE,
            "eligibility_state": REPORTED_ELIGIBILITY_STATE,
            "eligibility_reason": REPORTED_ELIGIBILITY_REASON,
        },
        "candidate_matrix": {
            "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
            "family_row_present": False,
            "note": "No SE-NAC row exists in the pinned matrix; no local "
                    "score, artifact identity or evaluation record is "
                    "attached to this family.",
        },
        "source_reported_scores": None,
        "source_reported_scores_note": (
            "No paper or model-card metric is reproduced, pooled or "
            "qualified as a local result."),
        "locally_verified": False,
        "admitted_as_result": False,
    }


def task_geometry() -> dict:
    return {
        "task": "Offline single-channel codec-latent speech enhancement",
        "reported_sample_rate_hz": REPORTED_SAMPLE_RATE_HZ,
        "reported_channels": None,
        "reported_variants": list(REPORTED_VARIANTS),
        "codec_tokenization_contract": None,
        "model_rate_to_v0_mapping": None,
        "chunk_frame_hop_contract": None,
        "resampler_contract": None,
        "state_reset_tail_pacing_contract": None,
        "verified_here": False,
        "note": "The pinned store records sample_rate_hz=null. No exact "
                "rate, tokenizer, codec dependency, chunk/hop or reset "
                "contract is supplied; the installed v0 path is 16 kHz mono "
                "float32 with 160-sample frames. Geometry compatibility is "
                "not claimed.",
    }


def public_v0_geometry() -> dict:
    return {
        "source": "CONTRACTS.md and api/include/audio_sdk/provider_v0.h",
        "sample_rate_hz": V0_SAMPLE_RATE_HZ,
        "channels": V0_CHANNELS,
        "sample_format": V0_SAMPLE_FORMAT,
        "frame_samples": V0_FRAME_SAMPLES,
        "registered": False,
        "descriptor_settings": {},
        "model_mapping_verified": False,
        "note": "Installed v0 geometry is preserved. This package neither "
                "registers a provider nor changes the installed path.",
    }


def disposition_block() -> dict:
    return {
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "defer_before": "caller_asset_identity_rights_and_geometry_clearance",
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "model_runtime_invoked": False,
        "runtime_invoked": False,
        "model_executed": False,
        "weights_loaded": False,
        "weights_downloaded": False,
        "network_used": False,
        "real_audio": False,
        "real_corpus": False,
        "listening": False,
        "device_timing": False,
        "public_benchmark": False,
        "release_claim": False,
        "caller_asset_present": False,
        "terms_review_performed": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "enabled_by_default": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "abi_change": False,
        "shared_build_or_ci_change": False,
        "asset_bundled": False,
        "adapter_runtime_bundled": False,
        "weights_vendored": False,
        "sdk_callback_invoked": False,
        "production_callback_registered": False,
        "processor_exposure": False,
    }


def exact_scope_block() -> dict:
    return {
        "verified": True,
        "no_source_checkout_executed": True,
        "no_codec_runtime_loaded": True,
        "no_model_byte_opened": True,
        "no_network_request": True,
        "no_audio_device_access": True,
        "no_real_audio_read": True,
        "no_terms_or_secret_record": True,
        "no_registry_or_default_change": True,
        "no_shared_build_or_ci_change": True,
        "only_task_directory_written": True,
    }


def boundary_block() -> dict:
    return {
        "write_scope": WRITE_SCOPE,
        "task_prefix": TASK_PREFIX,
        "read_only_inputs": sorted(SOURCE_PINS) + sorted(BOUNDARY_PINS),
        "mutable_board_file_hashed": False,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
        "peer_components": list(PEER_EVIDENCE),
        "historical_evidence": list(HISTORICAL_EVIDENCE),
        "note": "Peer and historical evidence is context only; no artifact, "
                "score, timing, state model or rights record is inherited.",
    }


def rights_gap() -> list[dict]:
    return [
        {"id": "source_code_terms", "state": "unreviewed",
         "requirement": "Reviewed upstream code terms for an exact, pinned "
                        "source revision."},
        {"id": "checkpoint_terms", "state": "unreviewed",
         "requirement": "Reviewed per-variant checkpoint terms and "
                        "redistribution/output-use conditions."},
        {"id": "training_data_lineage", "state": "unresolved",
         "requirement": "Documented LibriMix and any additional training-data "
                        "lineage with rights and exposure review."},
        {"id": "matched_cohort_rights", "state": "absent",
         "requirement": "Rights-cleared 16 kHz mono held-out cohort with "
                        "clean-reference permission where paired scoring is "
                        "used."},
        {"id": "publication_and_attribution", "state": "unresolved",
         "requirement": "Explicit permission to retain, score and publish "
                        "outputs with required attribution."},
    ]


ENHANCEMENT_REQUIREMENTS = (
    ("identity_noisy_control_and_baseline",
     "Run an identity/noisy control and an established task-matched baseline "
     "on the exact runtime.", "blocked"),
    ("paired_si_sdr_and_stoi",
     "Score paired SI-SDR and STOI where permitted clean references exist.",
     "blocked"),
    ("preservation_peaks_and_invalid_outputs",
     "Measure clean-speech preservation, output peaks and invalid/nonfinite "
     "outputs.", "blocked"),
    ("predictive_screen_or_authorized_listening",
     "For unpaired speech use a separately labelled predictive screen or "
     "authorized listening.", "blocked"),
    ("alignment_state_memory_and_timing",
     "Report alignment, state, memory and measured content/availability "
     "timing for the exact runtime.", "blocked"),
    ("geometry_rate_and_frame_contract",
     "Freeze the caller-supplied model rate, codec/tokenizer revision and "
     "rate/format/frame mapping to exact 16 kHz mono float32 160-sample v0.",
     "blocked"),
    ("quiet_active_idle_and_onset_strata",
     "Stratify by quiet/active speech, idle noise and onset/offset cases on "
     "a held-out cohort.", "blocked"),
    ("evidence_class_separation",
     "Separate paired, unpaired, synthetic, human and source-reported "
     "evidence; label all source-reported facts.", "documented"),
)


def enhancement_profile_block() -> dict:
    rows = [
        {"id": item, "requirement": requirement, "package_status": status,
         "satisfied_for_qualification": False, "qualification_effect": "none"}
        for item, requirement, status in ENHANCEMENT_REQUIREMENTS
    ]
    return {
        "name": PROFILE,
        "label": PROFILE_LABEL,
        "source": PROFILE_SOURCE_REL,
        "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
        "phrases_verified": list(PROFILE_PHRASES),
        "required_items": rows,
        "satisfied_for_qualification": [],
        "unsatisfied_for_qualification": [row["id"] for row in rows],
        "real_runtime_metrics": None,
        "note": "No caller-supplied codec runtime, pinned source/checkpoint, "
                "cohort or paired output exists; the Enhancement profile is "
                "not satisfied.",
    }


def profile_row_check() -> dict:
    text = (AUDIO_ROOT / PROFILE_SOURCE_REL).read_text(encoding="utf-8")
    lines = [line for line in text.splitlines()
             if line.startswith("| Enhancement ")]
    if len(lines) != 1:
        raise ValueError("enhancement_profile_row_not_unique")
    line = lines[0]
    missing = [phrase for phrase in PROFILE_PHRASES if phrase not in line]
    if missing:
        raise ValueError("enhancement_profile_phrase_missing:" + missing[0])
    return {
        "source": PROFILE_SOURCE_REL,
        "row_found": True,
        "phrases_checked": len(PROFILE_PHRASES),
        "phrases_present": True,
        "hmac_claim": False,
    }


def required_artifacts() -> list[dict]:
    specs = (
        ("pinned_source_checkout", "data/checkouts/SE-NAC",
         "Immutable upstream source checkout with exact commit, tree hash "
         "and reviewed code terms."),
        ("source_and_checkpoint_terms", "data/licenses/se-nac",
         "Reviewed source and per-variant checkpoint terms, data lineage "
         "and output-use rights."),
        ("isolated_runtime_lock", "data/runtimes/se-nac",
         "Locked codec/runtime dependencies and enforced isolated worker "
         "sandbox for exact local execution."),
        ("exact_checkpoint", "data/models/SE-NAC",
         "Exact selected checkpoint variant with immutable revision, byte "
         "count and SHA-256."),
        ("rate_and_frame_contract", "data/manifests/se-nac-codec-latent-enhancement-family.json",
         "Frozen model-rate/codec-tokenizer, mono, float32, 160-sample "
         "mapping with resampler, chunk/hop, reset and tail policy."),
        ("rights_cleared_cohort", "data/runs/se-nac-codec-latent-enhancement-family/manifest.json",
         "Rights-cleared 16 kHz mono held-out cohort with quiet/active, idle "
         "noise and onset/offset strata."),
        ("frozen_outputs_and_scores", "data/runs/se-nac-codec-latent-enhancement-family/outputs.json",
         "Frozen matched outputs, identity/noisy controls, baseline and "
         "paired scores on the exact assets."),
        ("timing_and_resources", "data/runs/se-nac-codec-latent-enhancement-family/timing.json",
         "Paced target-device timing, alignment, memory and availability "
         "evidence."),
    )
    return [
        {"id": item, "path": path, "required": True,
         "sha256": None, "bytes": None, "revision": None,
         "locally_verified": False, "admitted_as_result": False,
         "qualifies": False, "requirement": requirement,
         "state": "absent"}
        for item, path, requirement in specs
    ]


def exact_blockers() -> list[dict]:
    return [
        {"id": "BLK-01", "state": "absent",
         "title": "upstream_source_identity_unverified",
         "requirement": "Provide an immutable upstream source checkout with "
                        "exact commit, tree hash, code linkage and byte "
                        "identity. No source checkout is present.",
         "reopen_condition": "Pin and verify the exact source revision and "
                             "reviewed code terms."},
        {"id": "BLK-02", "state": "unreviewed",
         "title": "source_checkpoint_terms_and_data_lineage_unreviewed",
         "requirement": "Review source/checkpoint terms, LibriMix and any "
                        "additional training-data lineage, deployment terms "
                        "and output-use rights. No reviewed record exists.",
         "reopen_condition": "Record reviewed terms, lineage and output "
                             "rights without committing secrets."},
        {"id": "BLK-03", "state": "blocked",
         "title": "runtime_dependencies_and_worker_sandbox_unverified",
         "requirement": "The store records codec dependencies and local "
                        "isolated inference costs as unverified and blocks "
                        "candidate inference on an unavailable enforced "
                        "worker sandbox.",
         "reopen_condition": "Supply a locked runtime and verified isolated "
                             "worker sandbox before executing any variant."},
        {"id": "BLK-04", "state": "absent",
         "title": "checkpoint_identity_unverified",
         "requirement": "Pin the exact checkpoint variant, revision, byte "
                        "count and SHA-256. The store records weights as "
                        "located_unverified.",
         "reopen_condition": "Supply and verify the exact checkpoint bytes "
                             "and variant identifiers."},
        {"id": "BLK-05", "state": "absent",
         "title": "geometry_tokenizer_and_rate_contract_unfrozen",
         "requirement": "The store records sample_rate_hz=null. Freeze the "
                        "exact model rate, codec/tokenizer revision, mono, "
                        "float32, 160-sample mapping and reset/tail policy.",
         "reopen_condition": "Record and verify the exact rate/tokenizer/"
                             "format/frame contract against installed v0."},
        {"id": "BLK-06", "state": "absent",
         "title": "matched_cohort_and_results_absent",
         "requirement": "Provide a rights-cleared 16 kHz mono cohort, "
                        "identity/noisy controls, STFT-NAR and task-matched "
                        "baselines, frozen outputs, paired scores, WER/"
                        "content preservation and noise-only evidence.",
         "reopen_condition": "Reproduce the Enhancement profile on the exact "
                             "pinned runtime with stratified controls."},
        {"id": "BLK-07", "state": "absent",
         "title": "timing_and_state_evidence_absent",
         "requirement": "Measure codec tokenization cost, alignment, state, "
                        "memory and paced content/availability timing for "
                        "the exact runtime.",
         "reopen_condition": "Collect paced target-device timing, cost and "
                             "state evidence independently of compute speed."},
        {"id": "BLK-08", "state": "not_started",
         "title": "adapter_intake_and_release_not_started",
         "requirement": "No opt-in external-adapter intake, descriptor or "
                        "registry review, default decision or public "
                        "benchmark approval exists.",
         "reopen_condition": "Complete independent intake and release review "
                             "after all technical gates clear."},
    ]


RELEASE_GATES = (
    ("source_checkpoint_terms_and_lineage",
     "Reviewed source/checkpoint terms, training-data lineage, deployment "
     "terms and output-use rights are recorded without committed secrets."),
    ("artifact_identity_and_worker_sandbox",
     "Exact source revision, checkpoint variant, SHA-256, byte counts, codec "
     "dependency lock and enforced isolated worker sandbox are verified."),
    ("geometry_tokenizer_and_frame_contract",
     "Exact model rate, codec/tokenizer revision and mono float32 "
     "160-sample mapping with resampler, chunk/hop and reset/tail are frozen."),
    ("rights_cleared_cohort",
     "A rights-cleared 16 kHz mono held-out cohort with paired references "
     "where permitted is available."),
    ("enhancement_profile_quality",
     "Identity/noisy controls, STFT-NAR and task-matched baselines, paired "
     "SI-SDR/STOI, WER/content preservation, peaks, invalid outputs and "
     "strata are scored on the exact runtime."),
    ("paced_target_timing",
     "Codec tokenization cost, alignment, state, memory and paced content/"
     "availability timing are measured on the target device."),
    ("opt_in_adapter_intake",
     "Explicit opt-in external-adapter intake, descriptor/registry review "
     "and independent public-surface decision are complete."),
    ("public_default_and_release",
     "Default selection, resource/deadline evidence and release/public-"
     "benchmark approval are recorded; this package is OFF by default."),
)


def release_gates() -> list[dict]:
    return [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in RELEASE_GATES
    ]


def qualification_block() -> dict:
    gates = release_gates()
    blockers = exact_blockers()
    return {
        "status": QUALIFICATION_STATUS,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": "caller_asset_identity_rights_and_geometry_clearance",
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "blocker_count": len(blockers),
        "blocker_ids": [item["id"] for item in blockers],
        "reason": "No pinned source/checkpoint, reviewed terms and data "
                  "lineage, verified codec runtime/worker sandbox, model "
                  "rate/tokenizer contract, rights-cleared cohort, matched "
                  "Enhancement result or paced timing evidence exists; no "
                  "qualifying result is present.",
    }


def linked_identity_block() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "board_path": BOARD_TASK_ROW,
        "whole_file_hashed": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
        "excluded_mutable_fields": ["status", "owner", "claim", "review",
                                    "handoff", "blocked_reason",
                                    "dispatch_priority"],
        "task_row": projection,
        "task_row_sha256": board_row_digest(projection),
        "linked_row_ids": list(LINKED_ROW_IDS),
        "linked_rows_sha256": linked_rows_digest(rows),
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "worktree": CLAIM_WORKTREE,
            "reviewer": REVIEWER,
        },
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied source/checkpoint manifest validation.
# ---------------------------------------------------------------------------

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

MANIFEST_TOP_KEYS = ("schema_id", "manifest_id", "source", "checkpoint",
                     "runtime", "geometry", "input", "control", "rights")
SOURCE_KEYS = ("family_name", "model_card", "paper", "source_commit",
               "source_tree_sha256", "terms_path", "terms_sha256")
CHECKPOINT_KEYS = ("variant", "revision", "weights_path", "weights_sha256",
                   "weights_bytes", "terms_path", "terms_sha256",
                   "runtime_lock_path", "runtime_lock_sha256")
RUNTIME_KEYS = ("python_version", "host_platform", "device", "offline",
                "worker_sandbox")
GEOMETRY_KEYS = ("mode", "channels", "sample_rate_hz", "sample_format",
                 "frame_samples", "model_rate_hz", "rate_contract",
                 "codec_revision")
INPUT_KEYS = ("corpus_id", "split", "clip_count", "channels",
              "sample_rate_hz", "rights_cleared", "clean_reference_permission")
CONTROL_KEYS = ("identity_passthrough", "noisy_control", "no_real_audio",
                "no_listening", "no_device_timing")
RIGHTS_KEYS = ("source_terms", "checkpoint_terms", "training_data_lineage",
               "cohort_rights", "output_use", "publication", "attribution")

UNRESOLVED_VALUES = {"", "NOASSERTION", "TODO", "TBD", "unknown", "UNKNOWN",
                     "none", "NONE", "unverified", "UNVERIFIED"}
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_CLIPS = 100_000
ALLOWED_RATE_CONTRACT = "caller_supplied_pinned_rate_tokenizer_and_frame_contract"
CALLER_MODE = "offline_file"


class Invalid(Exception):
    """Fail-closed rejection of an invalid caller-supplied manifest."""

    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _field(prefix: str, name: str) -> str:
    return prefix + "." + name if prefix else name


def _exact_object(value: Any, fields: tuple[str, ...], prefix: str) -> dict:
    if not isinstance(value, dict):
        raise Invalid("not_object", prefix or "root")
    missing = [name for name in fields if name not in value]
    if missing:
        raise Invalid("missing_field", _field(prefix, missing[0]))
    extra = sorted(name for name in value if name not in fields)
    if extra:
        raise Invalid("unknown_field", _field(prefix, extra[0]))
    return value


def _text(value: Any, field: str, limit: int = 240) -> None:
    if not isinstance(value, str):
        raise Invalid("invalid_text", field)
    if not value or len(value) > limit or value in UNRESOLVED_VALUES:
        raise Invalid("invalid_text", field)


def _slug(value: Any, field: str) -> None:
    if not isinstance(value, str) or SLUG.fullmatch(value) is None:
        raise Invalid("invalid_slug", field)


def _sha(value: Any, field: str) -> None:
    if (not isinstance(value, str) or HEX64.fullmatch(value) is None
            or value == "0" * 64):
        raise Invalid("invalid_sha256", field)


def _sha40(value: Any, field: str) -> None:
    if (not isinstance(value, str) or HEX40.fullmatch(value) is None
            or value == "0" * 40):
        raise Invalid("invalid_sha1", field)


def _file_size(path_field: str, size_field: str, obj: dict,
               prefix: str) -> None:
    actual = Path(obj[path_field]).stat().st_size
    if actual != obj[size_field]:
        raise Invalid("size_mismatch", _field(prefix, size_field))


def _version(value: Any, field: str) -> None:
    if not isinstance(value, str) or VERSION.fullmatch(value) is None:
        raise Invalid("invalid_version", field)


def _absolute(value: Any, field: str, directory: bool = False) -> None:
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise Invalid("not_absolute_path", field)
    if ".." in Path(value).parts:
        raise Invalid("unsafe_path", field)
    path = Path(value)
    if directory:
        if not path.is_dir():
            raise Invalid("directory_missing", field)
    elif not path.is_file():
        raise Invalid("file_missing", field)
    elif path.stat().st_size > MAX_FILE_BYTES:
        raise Invalid("file_too_large", field)


def _bounded_int(value: Any, low: int, high: int, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Invalid("invalid_int", field)
    if value < low or value > high:
        raise Invalid("out_of_range", field)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise Invalid("invalid_boolean", field)


def _file_hash(path_field: str, sha_field: str, obj: dict, prefix: str) -> None:
    actual = sha256_file(Path(obj[path_field]))
    if actual != obj[sha_field]:
        raise Invalid("hash_mismatch", _field(prefix, sha_field))


def validate_manifest(document: Any) -> dict:
    """Validate a caller-owned source/checkpoint manifest without execution."""
    top = _exact_object(document, MANIFEST_TOP_KEYS, "")
    if top["schema_id"] != MANIFEST_SCHEMA_ID:
        raise Invalid("schema_mismatch", "schema_id")
    _slug(top["manifest_id"], "manifest_id")

    source = _exact_object(top["source"], SOURCE_KEYS, "source")
    if source["family_name"] != FAMILY_NAME:
        raise Invalid("family_mismatch", "source.family_name")
    if source["model_card"] != MODEL_CARD_SOURCE:
        raise Invalid("model_card_mismatch", "source.model_card")
    if source["paper"] != PAPER_SOURCE:
        raise Invalid("paper_mismatch", "source.paper")
    _sha40(source["source_commit"], "source.source_commit")
    _sha(source["source_tree_sha256"], "source.source_tree_sha256")
    _sha(source["terms_sha256"], "source.terms_sha256")
    _absolute(source["terms_path"], "source.terms_path")
    _file_hash("terms_path", "terms_sha256", source, "source")
    if any(key in source for key in ("token", "access_key", "secret")):
        raise Invalid("secret_field_present", "source")

    checkpoint = _exact_object(top["checkpoint"], CHECKPOINT_KEYS, "checkpoint")
    if checkpoint["variant"] not in REPORTED_VARIANTS:
        raise Invalid("variant_unknown", "checkpoint.variant")
    _sha40(checkpoint["revision"], "checkpoint.revision")
    _sha(checkpoint["weights_sha256"], "checkpoint.weights_sha256")
    _sha(checkpoint["terms_sha256"], "checkpoint.terms_sha256")
    _sha(checkpoint["runtime_lock_sha256"], "checkpoint.runtime_lock_sha256")
    _bounded_int(checkpoint["weights_bytes"], 1, MAX_FILE_BYTES,
                 "checkpoint.weights_bytes")
    for path_field in ("weights_path", "terms_path", "runtime_lock_path"):
        _absolute(checkpoint[path_field], "checkpoint." + path_field)
    _file_hash("weights_path", "weights_sha256", checkpoint, "checkpoint")
    _file_size("weights_path", "weights_bytes", checkpoint, "checkpoint")
    _file_hash("terms_path", "terms_sha256", checkpoint, "checkpoint")
    _file_hash("runtime_lock_path", "runtime_lock_sha256",
               checkpoint, "checkpoint")
    if any(key in checkpoint for key in ("token", "access_key", "secret")):
        raise Invalid("secret_field_present", "checkpoint")

    runtime = _exact_object(top["runtime"], RUNTIME_KEYS, "runtime")
    if runtime["python_version"] != REQUIRED_INTERPRETER:
        raise Invalid("interpreter_mismatch", "runtime.python_version")
    _slug(runtime["host_platform"], "runtime.host_platform")
    _slug(runtime["device"], "runtime.device")
    _boolean(runtime["offline"], "runtime.offline")
    if runtime["offline"] is not True:
        raise Invalid("offline_required", "runtime.offline")
    _boolean(runtime["worker_sandbox"], "runtime.worker_sandbox")
    if runtime["worker_sandbox"] is not True:
        raise Invalid("worker_sandbox_required", "runtime.worker_sandbox")

    geometry = _exact_object(top["geometry"], GEOMETRY_KEYS, "geometry")
    if geometry["mode"] != CALLER_MODE:
        raise Invalid("mode_mismatch", "geometry.mode")
    if geometry["channels"] != V0_CHANNELS:
        raise Invalid("channels_mismatch", "geometry.channels")
    if geometry["sample_rate_hz"] != V0_SAMPLE_RATE_HZ:
        raise Invalid("rate_mismatch", "geometry.sample_rate_hz")
    if geometry["sample_format"] != V0_SAMPLE_FORMAT:
        raise Invalid("format_mismatch", "geometry.sample_format")
    if geometry["frame_samples"] != V0_FRAME_SAMPLES:
        raise Invalid("frame_mismatch", "geometry.frame_samples")
    _bounded_int(geometry["model_rate_hz"], 8000, 192000,
                 "geometry.model_rate_hz")
    _sha40(geometry["codec_revision"], "geometry.codec_revision")
    if geometry["rate_contract"] != ALLOWED_RATE_CONTRACT:
        raise Invalid("rate_contract_mismatch", "geometry.rate_contract")

    input_block = _exact_object(top["input"], INPUT_KEYS, "input")
    _slug(input_block["corpus_id"], "input.corpus_id")
    _slug(input_block["split"], "input.split")
    _bounded_int(input_block["clip_count"], 1, MAX_CLIPS, "input.clip_count")
    if input_block["channels"] != V0_CHANNELS:
        raise Invalid("input_channels_mismatch", "input.channels")
    if input_block["sample_rate_hz"] != V0_SAMPLE_RATE_HZ:
        raise Invalid("input_rate_mismatch", "input.sample_rate_hz")
    _boolean(input_block["rights_cleared"], "input.rights_cleared")
    if input_block["rights_cleared"] is not True:
        raise Invalid("input_rights_required", "input.rights_cleared")
    _boolean(input_block["clean_reference_permission"],
             "input.clean_reference_permission")
    if input_block["clean_reference_permission"] is not True:
        raise Invalid("clean_reference_required",
                      "input.clean_reference_permission")

    control = _exact_object(top["control"], CONTROL_KEYS, "control")
    for key in CONTROL_KEYS:
        _boolean(control[key], "control." + key)
        if control[key] is not True:
            raise Invalid("control_not_true", "control." + key)

    rights = _exact_object(top["rights"], RIGHTS_KEYS, "rights")
    for key in RIGHTS_KEYS:
        _boolean(rights[key], "rights." + key)
        if rights[key] is not True:
            raise Invalid("right_not_cleared", "rights." + key)

    return {
        "accepted": True,
        "synthetic_schema_control": False,
        "manifest_id": top["manifest_id"],
        "family": FAMILY_NAME,
        "variant": checkpoint["variant"],
        "source_or_runtime_imported": False,
        "runtime_executed": False,
        "model_executed": False,
        "network_used": False,
        "audio_read": False,
        "geometry": {
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "channels": V0_CHANNELS,
            "sample_format": V0_SAMPLE_FORMAT,
            "frame_samples": V0_FRAME_SAMPLES,
            "model_rate_hz": geometry["model_rate_hz"],
            "rate_contract": ALLOWED_RATE_CONTRACT,
        },
        "qualifies": False,
        "note": "Schema and caller-file validation only. Acceptance of shape "
                "does not qualify the family or admit any output as evidence.",
    }


def _synthetic_manifest(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    source_terms = root / "source-terms.json"
    source_terms.write_bytes(b'{"source_terms":"recorded"}\n')
    weights = root / "synthetic-weights.bin"
    weights.write_bytes(b"synthetic-not-a-model\n")
    checkpoint_terms = root / "checkpoint-terms.json"
    checkpoint_terms.write_bytes(b'{"checkpoint_terms":"recorded"}\n')
    lock = root / "runtime-lock.json"
    lock.write_bytes(b'{"runtime":"locked"}\n')
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "synthetic-se-nac-schema-control",
        "source": {
            "family_name": FAMILY_NAME,
            "model_card": MODEL_CARD_SOURCE,
            "paper": PAPER_SOURCE,
            "source_commit": "a" * 40,
            "source_tree_sha256": sha256_file(source_terms),
            "terms_path": str(source_terms),
            "terms_sha256": sha256_file(source_terms),
        },
        "checkpoint": {
            "variant": REPORTED_VARIANTS[0],
            "revision": "1" * 40,
            "weights_path": str(weights),
            "weights_sha256": sha256_file(weights),
            "weights_bytes": weights.stat().st_size,
            "terms_path": str(checkpoint_terms),
            "terms_sha256": sha256_file(checkpoint_terms),
            "runtime_lock_path": str(lock),
            "runtime_lock_sha256": sha256_file(lock),
        },
        "runtime": {
            "python_version": REQUIRED_INTERPRETER,
            "host_platform": "macos-arm64",
            "device": "cpu",
            "offline": True,
            "worker_sandbox": True,
        },
        "geometry": {
            "mode": CALLER_MODE,
            "channels": V0_CHANNELS,
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "sample_format": V0_SAMPLE_FORMAT,
            "frame_samples": V0_FRAME_SAMPLES,
            "model_rate_hz": 24000,
            "rate_contract": ALLOWED_RATE_CONTRACT,
            "codec_revision": "2" * 40,
        },
        "input": {
            "corpus_id": "synthetic-cohort",
            "split": "heldout",
            "clip_count": 2,
            "channels": V0_CHANNELS,
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "rights_cleared": True,
            "clean_reference_permission": True,
        },
        "control": {key: True for key in CONTROL_KEYS},
        "rights": {key: True for key in RIGHTS_KEYS},
    }


def _case(case_id: str, action: Any, expected: str) -> dict:
    try:
        action()
    except Invalid as error:
        result = "rejected"
        reason = error.code
    except Exception as error:  # noqa: BLE001
        result = "unexpected_error"
        reason = type(error).__name__ + ":" + str(error)
    else:
        result = "accepted"
        reason = ""
    return {"case": case_id, "result": result, "expected": expected,
            "reason": reason}


def admission_controls() -> dict:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="se-nac-control-") as raw:
        root = Path(raw)
        baseline = _synthetic_manifest(root)

        def mutate(section: str, key: str, value: Any) -> Any:
            document = json.loads(json.dumps(baseline))
            document[section][key] = value
            return lambda: validate_manifest(document)

        def drop(section: str, key: str) -> Any:
            document = json.loads(json.dumps(baseline))
            del document[section][key]
            return lambda: validate_manifest(document)

        cases = [
            _case("manifest_not_object",
                  lambda: validate_manifest([]), "rejected"),
            _case("manifest_missing_field",
                  lambda: validate_manifest(
                      {key: value for key, value in baseline.items()
                       if key != "rights"}), "rejected"),
            _case("manifest_extra_field",
                  lambda: validate_manifest(dict(baseline, extra=True)),
                  "rejected"),
            _case("schema_mismatch",
                  lambda: validate_manifest(dict(
                      baseline, schema_id="audio-sdk/other/0.1")), "rejected"),
            _case("family_mismatch",
                  mutate("source", "family_name", "OtherFamily"), "rejected"),
            _case("model_card_mismatch",
                  mutate("source", "model_card", "https://example.invalid"),
                  "rejected"),
            _case("paper_mismatch",
                  mutate("source", "paper", "https://example.invalid"),
                  "rejected"),
            _case("source_commit_unresolved",
                  mutate("source", "source_commit", "NOASSERTION"),
                  "rejected"),
            _case("source_terms_hash_mismatch",
                  mutate("source", "terms_sha256", "0" * 64), "rejected"),
            _case("source_terms_missing",
                  mutate("source", "terms_path", str(root / "absent.json")),
                  "rejected"),
            _case("variant_unknown",
                  mutate("checkpoint", "variant", "UNKNOWN-VARIANT"),
                  "rejected"),
            _case("checkpoint_revision_unresolved",
                  mutate("checkpoint", "revision", "unknown"), "rejected"),
            _case("weights_hash_mismatch",
                  mutate("checkpoint", "weights_sha256", "0" * 64),
                  "rejected"),
            _case("weights_size_mismatch",
                  mutate("checkpoint", "weights_bytes", 1), "rejected"),
            _case("checkpoint_terms_hash_mismatch",
                  mutate("checkpoint", "terms_sha256", "0" * 64),
                  "rejected"),
            _case("runtime_lock_hash_mismatch",
                  mutate("checkpoint", "runtime_lock_sha256", "0" * 64),
                  "rejected"),
            _case("runtime_interpreter_mismatch",
                  mutate("runtime", "python_version", "3.11.5"), "rejected"),
            _case("runtime_online",
                  mutate("runtime", "offline", False), "rejected"),
            _case("worker_sandbox_off",
                  mutate("runtime", "worker_sandbox", False), "rejected"),
            _case("geometry_rate_mismatch",
                  mutate("geometry", "sample_rate_hz", 48000), "rejected"),
            _case("geometry_channels_mismatch",
                  mutate("geometry", "channels", 2), "rejected"),
            _case("geometry_format_mismatch",
                  mutate("geometry", "sample_format", "int16"), "rejected"),
            _case("geometry_frame_mismatch",
                  mutate("geometry", "frame_samples", 512), "rejected"),
            _case("model_rate_unresolved",
                  mutate("geometry", "model_rate_hz", "unknown"), "rejected"),
            _case("rate_contract_mismatch",
                  mutate("geometry", "rate_contract", "none"), "rejected"),
            _case("input_rights_uncleared",
                  mutate("input", "rights_cleared", False), "rejected"),
            _case("clean_reference_permission_false",
                  mutate("input", "clean_reference_permission", False),
                  "rejected"),
            _case("input_clip_count_overflow",
                  mutate("input", "clip_count", MAX_CLIPS + 1), "rejected"),
            _case("control_listening_present",
                  mutate("control", "no_listening", False), "rejected"),
            _case("rights_publication_unresolved",
                  mutate("rights", "publication", False), "rejected"),
            _case("drop_source_tree_sha",
                  drop("source", "source_tree_sha256"), "rejected"),
            _case("duplicate_json_key",
                  lambda: validate_manifest(
                      json.loads('{"schema_id":"a","schema_id":"b"}')),
                  "rejected"),
            _case("float_in_manifest",
                  mutate("input", "clip_count", 1.0), "rejected"),
            _case("synthetic_schema_control",
                  lambda: validate_manifest(baseline), "accepted"),
        ]
    rejected = [row for row in cases if row["expected"] == "rejected"]
    accepted = [row for row in cases if row["expected"] == "accepted"]
    return {
        "validator": MANIFEST_SCHEMA_ID,
        "runtime_executed": False,
        "case_count": len(cases),
        "cases": cases,
        "rejected_count": len(rejected),
        "accepted_count": len(accepted),
        "all_rejected_rejected": all(
            row["result"] == "rejected" for row in rejected),
        "synthetic_control_accepted": (
            len(accepted) == 1
            and accepted[0]["result"] == "accepted"
            and accepted[0]["case"] == "synthetic_schema_control"),
        "note": "The single accepted control validates schema shape only; it "
                "is synthetic, executes no runtime, and is not evidence.",
    }


def admission_contract_block() -> dict:
    control = admission_controls()
    return {
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "source_assets_are_caller_owned": True,
        "source_assets_are_vendored": False,
        "source_assets_must_not_be_committed": True,
        "absent_behavior": "reject_before_processing",
        "present_behavior": (
            "validate_exact_keys_hashes_geometry_terms_and_rights_without_"
            "execution; do_not_import_or_execute_in_this_package"),
        "top_level_fields": list(MANIFEST_TOP_KEYS),
        "required_geometry": {
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "channels": V0_CHANNELS,
            "sample_format": V0_SAMPLE_FORMAT,
            "frame_samples": V0_FRAME_SAMPLES,
            "model_rate_hz": "caller_declared_bounded_integer",
            "rate_contract": ALLOWED_RATE_CONTRACT,
        },
        "control": control,
        "qualification_effect": "none",
    }


# ---------------------------------------------------------------------------
# Canonical report and contract.
# ---------------------------------------------------------------------------


def build_report() -> dict:
    identity = linked_identity_block()
    audit = absence_summary()
    profile = enhancement_profile_block()
    blockers = exact_blockers()
    gates = release_gates()
    control = admission_controls()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": qualification_block(),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "depends_on": list(DEPENDS_ON),
        "required_interpreter": REQUIRED_INTERPRETER,
        "generated_by": "reference.py",
        "task_row_identity": identity,
        "family_record": family_record(),
        "recorded_identity": recorded_identity_block(),
        "task_geometry": task_geometry(),
        "public_v0_geometry": public_v0_geometry(),
        "disposition": disposition_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "boundary": boundary_block(),
        "rights_gap": rights_gap(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "pin_verification": {
            "source_pin_rows": pin_rows(SOURCE_PINS, AUDIO_ROOT),
            "boundary_pin_rows": pin_rows(BOUNDARY_PINS, SDK_ROOT),
            "all_source_pins_verified": all(
                row["verified"] for row in pin_rows(SOURCE_PINS, AUDIO_ROOT)),
            "all_boundary_pins_verified": all(
                row["verified"] for row in pin_rows(BOUNDARY_PINS, SDK_ROOT)),
        },
        "evidence_inputs": evidence_inputs(),
        "absence_evidence": {"summary": audit, "probes": all_probes()},
        "asset_registry": asset_registry(),
        "enhancement_profile": profile,
        "profile_row_check": profile_row_check(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_conditions": [
            {"blocker_id": item["id"], "condition": item["reopen_condition"]}
            for item in blockers
        ],
        "caller_asset_contract": admission_contract_block(),
        "controls": {
            "adverse": control["cases"],
            "adverse_all_rejected": control["all_rejected_rejected"],
            "synthetic_schema_control_accepted":
                control["synthetic_control_accepted"],
            "missing_result_never_qualifies": True,
            "source_reported_metrics_never_admitted": True,
            "caller_assets_never_auto_registered": True,
        },
        "candidate_metrics": None,
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no codec runtime or audio runtime is used.",
            "Fixed workspace, SDK-worktree and home-cache paths are probed.",
            "No source checkout is executed and no model byte is loaded.",
            "No network request, download, audio device, model load or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract() -> dict:
    report = build_report()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-" "Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "task_row_identity": report["task_row_identity"],
        "scope": report["scope"],
        "boundary": report["boundary"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "family_record": report["family_record"],
        "recorded_identity": report["recorded_identity"],
        "task_geometry": report["task_geometry"],
        "public_v0_geometry": report["public_v0_geometry"],
        "rights_gap": report["rights_gap"],
        "enhancement_profile_requirements": [
            {"id": row["id"], "requirement": row["requirement"],
             "package_status": row["package_status"]}
            for row in report["enhancement_profile"]["required_items"]
        ],
        "required_artifacts": report["required_artifacts"],
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "reopen_conditions": report["reopen_conditions"],
        "caller_asset_contract": report["caller_asset_contract"],
        "reproduction": {
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
            "cold_start_regenerations": 3,
            "command": "python3 run.py all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
        },
        "licensing": {"copyright": "2026 Tsakanyan Hovhannes",
                      "license": "Apache-2.0", "json_sidecars": True},
    }


def validate_contract(contract: dict) -> None:
    expected = build_contract()
    if canonical_text(contract) != canonical_text(expected):
        raise ValueError("contract_not_canonical")


# ---------------------------------------------------------------------------
# Task-local git scope. The base is the newest merge-base between HEAD and the
# available PR base refs (origin/main, then main), never a fixed commit.
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
        if best is None or best == base:
            best = base
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
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]
