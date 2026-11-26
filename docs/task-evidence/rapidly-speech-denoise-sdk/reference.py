# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only vendor-boundary evidence for SDK-RAPIDLY-....

This module records the Rapidly speech-denoise SDK boundary. The census and the
method/candidate store records describe a commercial on-device denoiser with
48 kHz trained models, 11/21/32/96 ms latency variants, dialogue/noise output
busses and an audible watermark on unlicensed output. No vendor SDK, native
binary, model byte, commercial entitlement, reviewed terms, runtime, corpus,
enhanced output, listening result, device timing, benchmark or release claim is
present in this workspace.

Nothing here downloads, installs, imports, loads or executes a vendor runtime;
no network, audio device or real audio is used. The package produces a strict
DEFER / incomplete / not_qualified readiness record, validates a fail-closed
caller-supplied entitlement manifest without executing it, and proves with
deterministic adverse controls that invalid, missing, watermarked or
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

TASK = "SDK-RAPIDLY-SPEECH-DENOISE-SDK"
TASK_TITLE = "Rapidly speech-denoise SDK"
COMPONENT_ID = "rapidly-speech-denoise-sdk"
REPOSITORY = "audio-sdk"
MODE = "external-adapter"
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/rapidly-speech-denoise-sdk/ only"
TASK_PREFIX = "docs/task-evidence/rapidly-speech-denoise-sdk/"
CONTRACT_ID = "audio-sdk/rapidly-speech-denoise-sdk-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/rapidly-speech-denoise-sdk-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/rapidly-speech-denoise-sdk-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/rapidly-speech-denoise-sdk-caller-asset/0.1"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
BRANCH = "swarm/SDK-RAPIDLY-SPEECH-DENOISE-SDK"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/"
    "audio-sdk/SDK-RAPIDLY-SPEECH-DENOISE-SDK")
REVIEWER = "reviewer-RAPIDLY-SPEECH-DENOISE-SDK"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
REQUIRED_INTERPRETER = "3.12.16"

VENDOR_NAME = "Rapidly"
PRODUCT_NAME = "Rapidly speech-denoise SDK"
IMPLEMENTATION_SOURCE = "https://github.com/rapidly-labs/rapidly-sdk"
MODELS_DOC_SOURCE = "https://www.rapidly.io/docs/sdk/introduction/models"
CENSUS_LINE = 56

REPORTED_TRAINED_RATE_HZ = 48000
REPORTED_LATENCIES_MS = (11, 21, 32, 96)
REPORTED_MODEL_SIZES_KB = (615, 851, 854, 925)
REPORTED_OUTPUT_BUSSES = ("dialogue", "noise")
REPORTED_PLATFORM = "macOS and other desktop/mobile targets"
REPORTED_COMMERCIAL_LICENSE_REQUIRED = True
REPORTED_WATERMARK_WITHOUT_LICENSE = True
REPORTED_CODE_STATE = "available"
REPORTED_WEIGHTS_STATE = "located_unverified"
REPORTED_BENCHMARK_STATE = "not_run"
REPORTED_ELIGIBILITY_STATE = "blocked"
REPORTED_ELIGIBILITY_REASON = (
    "Commercial on-device SDK with bundled denoise models and latency/size "
    "variants. Evaluation without entitlement is audibly watermarked; get a "
    "suitable entitlement and verify terms before product comparison.")

# Installed public v0 geometry. This is a contract fact, not a vendor mapping.
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
    "c85645e6921fd19919c389112656a361e58dc708f4524ced4f766c3a7e2d4d75.jsonl":
        "c85645e6921fd19919c389112656a361e58dc708f4524ced4f766c3a7e2d4d75",
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
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

STORE_METHOD_ID = "method-rapidly-sdk"
STORE_CANDIDATE_ID = "candidate-rapidly-sdk"

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
    "data/checkouts/rapidly-sdk",
    "data/checkouts/rapidly-speech-denoise-sdk",
    "data/runtimes/rapidly-sdk",
    "data/runtimes/rapidly-speech-denoise-sdk",
    "data/models/rapidly-sdk",
    "data/models/rapidly-speech-denoise-sdk",
    "data/licenses/rapidly-sdk",
    "data/licenses/rapidly-speech-denoise-sdk",
    "data/entitlements/rapidly-sdk.json",
    "data/manifests/rapidly-sdk-access.json",
    "data/runs/rapidly-speech-denoise-sdk/manifest.json",
    "research/voice-enhancement-20261101/repos/rapidly-sdk",
    "research/voice-enhancement-20261101/repos/rapidly-speech-denoise-sdk",
)
WORKTREE_PROBES = (
    "third_party/rapidly-sdk",
    "adapters/rapidly-speech-denoise-sdk",
    "schemas/providers/rapidly-speech-denoise-sdk.descriptor.json",
)
HOME_PROBES = (
    "~/.cache/rapidly",
    "~/.cache/rapidly-sdk",
    "~/Library/Application Support/Rapidly",
    "~/Library/Application Support/rapidly-sdk",
)

NON_CLAIMS = [
    "No Rapidly SDK, native library, model byte, entitlement or vendor runtime is loaded, downloaded, installed or executed.",
    "No network request, account creation, vendor API call, license activation or asset redistribution occurs.",
    "No real audio, rights-cleared cohort, label, listening result, device timing or public benchmark is used.",
    "No unlicensed, watermarked or demo-mode output is treated as valid evidence or as a quality score.",
    "Source-reported and census-reported facts are provenance only and are never reproduced, pooled or qualified here.",
    "No provider, descriptor, registry, default, installed v0 path, ABI, shared build, CI, board, handoff or release changed.",
    "Missing or unentitled vendor assets never qualify the candidate; the decision remains DEFER.",
]

PEER_EVIDENCE = (
    "ai-coustics-quail",
    "ai-coustics-rook",
    "desert-ant-labs-clear",
    "hecttor-commercial-ecosystem-products",
    "krisp-accent-conversion",
    "nvidia-background-noise-removal-v2.1",
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
# Fixed absence probes. No recursive walk, no network, no vendor import.
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
    """Summarize the local asset register without inventing a Rapidly entry."""
    path = AUDIO_ROOT / "research/noise_suppression_assets_20261027.json"
    document = read_strict_json(path)
    candidates = document.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("asset_register_candidates_not_list")
    ids = sorted(row.get("id") for row in candidates
                 if isinstance(row, dict) and isinstance(row.get("id"), str))
    if len(ids) != len(set(ids)):
        raise ValueError("asset_register_duplicate_id")
    rapidly_ids = [row_id for row_id in ids
                   if "rapidly" in row_id.lower()]
    return {
        "path": "research/noise_suppression_assets_20261027.json",
        "candidate_count": len(ids),
        "candidate_ids_sha256": object_digest(ids),
        "rapidly_entry_present": bool(rapidly_ids),
        "rapidly_candidate_ids": rapidly_ids,
        "asset_identity_available_for_rapidly": False,
        "note": "The register contains 20 separate denoising assets and no "
                "Rapidly SDK candidate, model revision, byte count, SHA-256 "
                "or vendor terms.",
    }


EVIDENCE_INPUT_PATHS = (
    "research/noise_suppression_candidate_census.md",
    "research/noise_suppression_assets_20261027.json",
    "research/voice-enhancement-20261101/candidate_matrix.csv",
    "research/store/snapshots/"
    "c85645e6921fd19919c389112656a361e58dc708f4524ced4f766c3a7e2d4d75.jsonl",
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
            "mentions_rapidly": (
                b"rapidly" in payload.lower()
                or b"Rapidly" in payload),
            "is_vendor_result": False,
            "is_entitlement": False,
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
# Task, vendor and geometry records. Every vendor fact is recorded-only.
# ---------------------------------------------------------------------------


def vendor_record() -> dict:
    return {
        "vendor_name": VENDOR_NAME,
        "product": PRODUCT_NAME,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "implementation_source": IMPLEMENTATION_SOURCE,
        "models_documentation": MODELS_DOC_SOURCE,
        "source_repository": IMPLEMENTATION_SOURCE,
        "source_revision": None,
        "release_version": None,
        "artifact_sha256": None,
        "artifact_byte_count": None,
        "code_state_reported": REPORTED_CODE_STATE,
        "weights_state_reported": REPORTED_WEIGHTS_STATE,
        "benchmark_state_reported": REPORTED_BENCHMARK_STATE,
        "eligibility_state_reported": REPORTED_ELIGIBILITY_STATE,
        "eligibility_reason_reported": REPORTED_ELIGIBILITY_REASON,
        "commercial_license_required_reported":
            REPORTED_COMMERCIAL_LICENSE_REQUIRED,
        "watermark_without_license_reported":
            REPORTED_WATERMARK_WITHOUT_LICENSE,
        "locally_verified": False,
        "admitted_as_result": False,
        "qualifies": False,
        "note": "All fields are recorded from the pinned census and candidate "
                "store snapshots. No SDK byte, model byte, revision, terms text "
                "or entitlement is present or locally verified.",
    }


def recorded_identity_block() -> dict:
    return {
        "label": "source_reported_not_locally_verified",
        "census": {
            "path": "research/noise_suppression_candidate_census.md",
            "line": CENSUS_LINE,
            "finding": "On-device commercial denoiser, outputs speech and "
                       "isolated-noise busses",
            "reported": "Official SDK bundles macOS/native binaries and "
                        "models, supports CPU, 48 kHz trained models and "
                        "11/21/32/96 ms latency variants; unlicensed output "
                        "is audibly watermarked.",
            "disposition": "Commercial product comparator only; benchmark "
                           "demo mode cannot yield valid quality scores. "
                           "Requires a suitable model entitlement and "
                           "explicit commercial terms.",
        },
        "candidate_store": {
            "snapshot": "research/store/snapshots/"
                        "c85645e6921fd19919c389112656a361e58dc708f4524ced4f76"
                        "63a7e2d4d75.jsonl",
            "method_id": STORE_METHOD_ID,
            "candidate_id": STORE_CANDIDATE_ID,
            "benchmark_state": REPORTED_BENCHMARK_STATE,
            "eligibility_state": REPORTED_ELIGIBILITY_STATE,
            "weights": REPORTED_WEIGHTS_STATE,
            "commercial_license_required":
                REPORTED_COMMERCIAL_LICENSE_REQUIRED,
            "watermarked_without_license":
                REPORTED_WATERMARK_WITHOUT_LICENSE,
            "trained_rate_hz": REPORTED_TRAINED_RATE_HZ,
            "latency_ms": list(REPORTED_LATENCIES_MS),
            "model_sizes_kb": list(REPORTED_MODEL_SIZES_KB),
            "output_busses": list(REPORTED_OUTPUT_BUSSES),
            "platform": REPORTED_PLATFORM,
        },
        "candidate_matrix": {
            "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
            "rapidly_row_present": False,
            "note": "No Rapidly row exists in the pinned matrix; no local "
                    "score, artifact identity or evaluation record is "
                    "attached to this candidate.",
        },
        "source_reported_scores": None,
        "source_reported_scores_note": (
            "No vendor or source score is reproduced, pooled or qualified."),
        "locally_verified": False,
        "admitted_as_result": False,
    }


def task_geometry() -> dict:
    return {
        "task": "Single-channel speech enhancement / noise suppression",
        "reported_rate_hz": REPORTED_TRAINED_RATE_HZ,
        "reported_channels": 1,
        "reported_latency_variants_ms": list(REPORTED_LATENCIES_MS),
        "reported_model_sizes_kb": list(REPORTED_MODEL_SIZES_KB),
        "reported_output_busses": list(REPORTED_OUTPUT_BUSSES),
        "vendor_rate_to_v0_mapping": None,
        "chunk_frame_hop_contract": None,
        "resampler_contract": None,
        "state_reset_tail_pacing_contract": None,
        "verified_here": False,
        "note": "The vendor models are reported as 48 kHz trained; the "
                "installed v0 path is 16 kHz mono float32 with 160-sample "
                "frames. No rate/format/frame mapping is supplied or "
                "verified, so rate compatibility is not claimed.",
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
        "vendor_mapping_verified": False,
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
        "defer_before": "vendor_terms_entitlement_and_geometry_clearance",
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "vendor_runtime_invoked": False,
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
        "entitlement_present": False,
        "watermark_probe_performed": False,
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
        "no_vendor_library_loaded": True,
        "no_model_byte_opened": True,
        "no_network_request": True,
        "no_audio_device_access": True,
        "no_real_audio_read": True,
        "no_entitlement_or_license_secret": True,
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
        {"id": "vendor_terms", "state": "unreviewed",
         "requirement": "Reviewed commercial SDK/model terms for the exact "
                        "release and intended use."},
        {"id": "commercial_entitlement", "state": "absent",
         "requirement": "A suitable watermark-free model entitlement, "
                        "supplied only through approved runtime mechanisms "
                        "and never committed or logged."},
        {"id": "telemetry_and_deployment_terms", "state": "unreviewed",
         "requirement": "Reviewed telemetry, activation and deployment terms "
                        "for the target platform."},
        {"id": "output_use_and_publication", "state": "unresolved",
         "requirement": "Explicit permission to retain, score and publish "
                        "vendor output."},
        {"id": "redistribution_and_attribution", "state": "unresolved",
         "requirement": "Cleared redistribution of SDK/library/model bytes "
                        "and required attribution."},
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
     "Freeze the 48 kHz-to-16 kHz rate/format/frame contract and the exact "
     "16 kHz mono float32 160-sample v0 mapping.", "blocked"),
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
        "note": "No vendor runtime, entitlement, cohort or paired output "
                "exists; the Enhancement profile is not satisfied.",
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
        ("vendor_sdk_release", "data/runtimes/rapidly-speech-denoise-sdk",
         "Immutable vendor SDK release with exact version, platform, native "
         "library byte count and SHA-256."),
        ("commercial_terms_record", "data/licenses/rapidly-sdk/terms.json",
         "Reviewed vendor SDK/model terms for the exact release and use."),
        ("watermark_free_entitlement",
         "data/entitlements/rapidly-sdk.json",
         "Suitable commercial entitlement proving watermark-free output, "
         "held outside git and never logged."),
        ("exact_model_asset", "data/models/rapidly-speech-denoise-sdk",
         "Exact selected 48 kHz model variant with immutable id, byte count, "
         "SHA-256 and latency variant."),
        ("rate_and_frame_contract", "data/manifests/rapidly-sdk-access.json",
         "Frozen 48 kHz-to-16 kHz, mono, float32, 160-sample mapping with "
         "resampler, chunk/hop, reset and tail policy."),
        ("rights_cleared_cohort", "data/runs/rapidly-speech-denoise-sdk/manifest.json",
         "Rights-cleared 16 kHz mono held-out cohort with quiet/active, idle "
         "noise and onset/offset strata."),
        ("frozen_outputs_and_scores", "data/runs/rapidly-speech-denoise-sdk/outputs.json",
         "Frozen vendor outputs, identity/noisy controls, baseline and "
         "paired scores on the exact assets."),
        ("timing_and_resources", "data/runs/rapidly-speech-denoise-sdk/timing.json",
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
         "title": "vendor_sdk_identity_unverified",
         "requirement": "Provide an immutable Rapidly SDK release: vendor, "
                        "product, version, platform, native library byte "
                        "count and SHA-256. No SDK byte is present.",
         "reopen_condition": "Pin and verify the exact SDK artifact with "
                             "reviewed terms."},
        {"id": "BLK-02", "state": "unreviewed",
         "title": "commercial_terms_and_entitlement_unreviewed",
         "requirement": "Review commercial license, telemetry and deployment "
                        "terms and obtain a suitable model entitlement. No "
                        "terms record or entitlement is present.",
         "reopen_condition": "Record reviewed terms and a watermark-free "
                             "entitlement without committing secrets."},
        {"id": "BLK-03", "state": "blocked",
         "title": "unlicensed_output_is_watermarked",
         "requirement": "The census records audible watermarking without a "
                        "license; demo/unlicensed output cannot yield valid "
                        "quality scores.",
         "reopen_condition": "Prove watermark-free output under an approved "
                             "entitlement before any quality measurement."},
        {"id": "BLK-04", "state": "absent",
         "title": "model_asset_identity_unverified",
         "requirement": "Pin the exact 48 kHz model variant, latency variant, "
                        "revision, byte count and SHA-256. The store records "
                        "weights as located_unverified.",
         "reopen_condition": "Supply and verify the exact model bytes and "
                             "variant identifiers."},
        {"id": "BLK-05", "state": "absent",
         "title": "geometry_and_rate_contract_unfrozen",
         "requirement": "Freeze the 48 kHz-to-16 kHz, mono, float32, "
                        "160-sample mapping, resampler, chunk/hop and reset "
                        "contract. No mapping is supplied.",
         "reopen_condition": "Record and verify the exact rate/format/frame "
                             "contract against the installed v0 geometry."},
        {"id": "BLK-06", "state": "absent",
         "title": "matched_cohort_and_results_absent",
         "requirement": "Provide a rights-cleared 16 kHz mono cohort, "
                        "identity/noisy controls, baseline, frozen outputs, "
                        "paired scores and preservation evidence.",
         "reopen_condition": "Reproduce the Enhancement profile on the exact "
                             "entitled runtime with stratified controls."},
        {"id": "BLK-07", "state": "absent",
         "title": "timing_and_state_evidence_absent",
         "requirement": "Measure alignment, state, memory and paced "
                        "content/availability timing for the exact runtime.",
         "reopen_condition": "Collect paced target-device timing and state "
                             "evidence independently of compute speed."},
        {"id": "BLK-08", "state": "not_started",
         "title": "adapter_intake_and_release_not_started",
         "requirement": "No opt-in external-adapter intake, descriptor or "
                        "registry review, default decision or public "
                        "benchmark approval exists.",
         "reopen_condition": "Complete independent intake and release review "
                             "after all technical gates clear."},
    ]


RELEASE_GATES = (
    ("vendor_terms_and_entitlement",
     "Reviewed SDK/model terms, telemetry/deployment terms and a watermark-"
     "free commercial entitlement are recorded without committed secrets."),
    ("artifact_identity_and_rights",
     "Exact SDK/model artifacts, immutable identifiers, SHA-256, byte counts "
     "and redistribution/output rights are verified."),
    ("rate_and_frame_contract",
     "The 48 kHz-to-16 kHz mono float32 160-sample mapping, resampler, "
     "chunk/hop and reset/tail contract are frozen and verified."),
    ("rights_cleared_cohort",
     "A rights-cleared 16 kHz mono held-out cohort with paired references "
     "where permitted is available."),
    ("enhancement_profile_quality",
     "Identity/noisy controls, baseline, paired SI-SDR/STOI, preservation, "
     "peaks, invalid outputs and strata are scored on the exact runtime."),
    ("paced_target_timing",
     "Alignment, state, memory and paced content/availability timing are "
     "measured on the target device."),
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
        "defer_before": "vendor_terms_entitlement_and_geometry_clearance",
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "blocker_count": len(blockers),
        "blocker_ids": [item["id"] for item in blockers],
        "reason": "No reviewed Rapidly terms/entitlement, verified 48 kHz "
                  "model, rate/format/frame contract, rights-cleared cohort, "
                  "watermark-free output or paced timing evidence exists; no "
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
# Fail-closed caller-supplied entitlement manifest validation.
# ---------------------------------------------------------------------------

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

MANIFEST_TOP_KEYS = ("schema_id", "manifest_id", "vendor", "sdk", "runtime",
                     "geometry", "input", "control", "rights")
VENDOR_KEYS = ("vendor_name", "product", "release_version",
               "implementation_source", "terms_record_path",
               "terms_record_sha256", "entitlement_record_path",
               "entitlement_record_sha256")
SDK_KEYS = ("platform", "version", "abi_version", "install_root",
            "library_sha256")
RUNTIME_KEYS = ("python_version", "host_platform", "device", "lock_sha256",
                "offline")
GEOMETRY_KEYS = ("mode", "channels", "sample_rate_hz", "sample_format",
                 "frame_samples", "model_rate_hz", "rate_contract",
                 "watermark_free_entitlement")
INPUT_KEYS = ("corpus_id", "split", "clip_count", "channels",
              "sample_rate_hz", "rights_cleared")
CONTROL_KEYS = ("identity_passthrough", "noisy_control", "no_real_audio",
                "no_listening", "no_device_timing")
RIGHTS_KEYS = ("vendor_terms", "commercial_entitlement", "telemetry_terms",
               "deployment_terms", "output_use", "publication", "attribution")

UNRESOLVED_VALUES = {"", "NOASSERTION", "TODO", "TBD", "unknown", "UNKNOWN",
                     "none", "NONE", "unverified", "UNVERIFIED"}
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_CLIPS = 100_000
ALLOWED_RATE_CONTRACT = "caller_supplied_48k_to_16k_resampler"
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
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise Invalid("invalid_sha256", field)


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
    """Validate a caller-owned manifest shape without executing any runtime."""
    top = _exact_object(document, MANIFEST_TOP_KEYS, "")
    if top["schema_id"] != MANIFEST_SCHEMA_ID:
        raise Invalid("schema_mismatch", "schema_id")
    _slug(top["manifest_id"], "manifest_id")

    vendor = _exact_object(top["vendor"], VENDOR_KEYS, "vendor")
    if vendor["vendor_name"] != VENDOR_NAME:
        raise Invalid("vendor_mismatch", "vendor.vendor_name")
    if vendor["product"] != PRODUCT_NAME:
        raise Invalid("product_mismatch", "vendor.product")
    if vendor["implementation_source"] != IMPLEMENTATION_SOURCE:
        raise Invalid("source_mismatch", "vendor.implementation_source")
    _version(vendor["release_version"], "vendor.release_version")
    _sha(vendor["terms_record_sha256"], "vendor.terms_record_sha256")
    _sha(vendor["entitlement_record_sha256"], "vendor.entitlement_record_sha256")
    for path_field in ("terms_record_path", "entitlement_record_path"):
        _absolute(vendor[path_field], "vendor." + path_field)
    _file_hash("terms_record_path", "terms_record_sha256", vendor, "vendor")
    _file_hash("entitlement_record_path", "entitlement_record_sha256",
               vendor, "vendor")
    if any(key in vendor for key in ("license_key", "access_key", "token")):
        raise Invalid("secret_field_present", "vendor")

    sdk = _exact_object(top["sdk"], SDK_KEYS, "sdk")
    _slug(sdk["platform"], "sdk.platform")
    _version(sdk["version"], "sdk.version")
    _version(sdk["abi_version"], "sdk.abi_version")
    _absolute(sdk["install_root"], "sdk.install_root", directory=True)
    _sha(sdk["library_sha256"], "sdk.library_sha256")

    runtime = _exact_object(top["runtime"], RUNTIME_KEYS, "runtime")
    if runtime["python_version"] != REQUIRED_INTERPRETER:
        raise Invalid("interpreter_mismatch", "runtime.python_version")
    _slug(runtime["host_platform"], "runtime.host_platform")
    _slug(runtime["device"], "runtime.device")
    _sha(runtime["lock_sha256"], "runtime.lock_sha256")
    _boolean(runtime["offline"], "runtime.offline")
    if runtime["offline"] is not True:
        raise Invalid("offline_required", "runtime.offline")

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
    if geometry["model_rate_hz"] != REPORTED_TRAINED_RATE_HZ:
        raise Invalid("model_rate_mismatch", "geometry.model_rate_hz")
    if geometry["rate_contract"] != ALLOWED_RATE_CONTRACT:
        raise Invalid("rate_contract_mismatch", "geometry.rate_contract")
    _boolean(geometry["watermark_free_entitlement"],
             "geometry.watermark_free_entitlement")
    if geometry["watermark_free_entitlement"] is not True:
        raise Invalid("watermark_not_cleared",
                      "geometry.watermark_free_entitlement")

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
        "vendor": VENDOR_NAME,
        "product": PRODUCT_NAME,
        "runtime_executed": False,
        "vendor_library_loaded": False,
        "model_executed": False,
        "network_used": False,
        "audio_read": False,
        "geometry": {
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "channels": V0_CHANNELS,
            "sample_format": V0_SAMPLE_FORMAT,
            "frame_samples": V0_FRAME_SAMPLES,
            "model_rate_hz": REPORTED_TRAINED_RATE_HZ,
            "rate_contract": ALLOWED_RATE_CONTRACT,
        },
        "qualifies": False,
        "note": "Schema validation only. Acceptance of shape does not "
                "qualify the candidate or admit any output as evidence.",
    }


def _synthetic_manifest(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    terms = root / "terms.json"
    terms.write_bytes(b'{"terms":"recorded"}\n')
    entitlement = root / "entitlement.json"
    entitlement.write_bytes(b'{"entitlement":"watermark_free"}\n')
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "synthetic-rapidly-schema-control",
        "vendor": {
            "vendor_name": VENDOR_NAME,
            "product": PRODUCT_NAME,
            "release_version": "1.0",
            "implementation_source": IMPLEMENTATION_SOURCE,
            "terms_record_path": str(terms),
            "terms_record_sha256": sha256_file(terms),
            "entitlement_record_path": str(entitlement),
            "entitlement_record_sha256": sha256_file(entitlement),
        },
        "sdk": {
            "platform": "macos-arm64",
            "version": "1.0",
            "abi_version": "0.0",
            "install_root": str(root),
            "library_sha256": "0" * 64,
        },
        "runtime": {
            "python_version": REQUIRED_INTERPRETER,
            "host_platform": "macos-arm64",
            "device": "cpu",
            "lock_sha256": "0" * 64,
            "offline": True,
        },
        "geometry": {
            "mode": CALLER_MODE,
            "channels": V0_CHANNELS,
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "sample_format": V0_SAMPLE_FORMAT,
            "frame_samples": V0_FRAME_SAMPLES,
            "model_rate_hz": REPORTED_TRAINED_RATE_HZ,
            "rate_contract": ALLOWED_RATE_CONTRACT,
            "watermark_free_entitlement": True,
        },
        "input": {
            "corpus_id": "synthetic-cohort",
            "split": "heldout",
            "clip_count": 2,
            "channels": V0_CHANNELS,
            "sample_rate_hz": V0_SAMPLE_RATE_HZ,
            "rights_cleared": True,
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

    with tempfile.TemporaryDirectory(prefix="rapidly-control-") as raw:
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
            _case("vendor_mismatch",
                  mutate("vendor", "vendor_name", "OtherVendor"), "rejected"),
            _case("vendor_release_unresolved",
                  mutate("vendor", "release_version", "NOASSERTION"),
                  "rejected"),
            _case("terms_hash_mismatch",
                  mutate("vendor", "terms_record_sha256", "0" * 64),
                  "rejected"),
            _case("entitlement_hash_mismatch",
                  mutate("vendor", "entitlement_record_sha256", "0" * 64),
                  "rejected"),
            _case("entitlement_record_missing",
                  mutate("vendor", "entitlement_record_path",
                         str(root / "absent.json")), "rejected"),
            _case("sdk_version_unresolved",
                  mutate("sdk", "version", "unknown"), "rejected"),
            _case("sdk_install_root_missing",
                  mutate("sdk", "install_root", str(root / "absent")),
                  "rejected"),
            _case("runtime_interpreter_mismatch",
                  mutate("runtime", "python_version", "3.11.5"), "rejected"),
            _case("runtime_online",
                  mutate("runtime", "offline", False), "rejected"),
            _case("geometry_rate_mismatch",
                  mutate("geometry", "sample_rate_hz", 48000), "rejected"),
            _case("geometry_channels_mismatch",
                  mutate("geometry", "channels", 2), "rejected"),
            _case("geometry_format_mismatch",
                  mutate("geometry", "sample_format", "int16"), "rejected"),
            _case("geometry_frame_mismatch",
                  mutate("geometry", "frame_samples", 512), "rejected"),
            _case("geometry_model_rate_mismatch",
                  mutate("geometry", "model_rate_hz", 16000), "rejected"),
            _case("watermark_not_cleared",
                  mutate("geometry", "watermark_free_entitlement", False),
                  "rejected"),
            _case("input_rights_uncleared",
                  mutate("input", "rights_cleared", False), "rejected"),
            _case("input_clip_count_overflow",
                  mutate("input", "clip_count", MAX_CLIPS + 1), "rejected"),
            _case("control_listening_present",
                  mutate("control", "no_listening", False), "rejected"),
            _case("rights_publication_unresolved",
                  mutate("rights", "publication", False), "rejected"),
            _case("drop_vendor_terms_sha",
                  drop("vendor", "terms_record_sha256"), "rejected"),
            _case("duplicate_json_key",
                  lambda: validate_manifest(
                      json.loads('{"schema_id":"a","schema_id":"b"}')),
                  "rejected"),
            _case("float_in_manifest",
                  lambda: validate_manifest(
                      dict(baseline, clip_count=1.0)), "rejected"),
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
        "runtime_is_caller_owned": True,
        "runtime_is_vendored": False,
        "entitlement_must_not_be_committed": True,
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
            "reported_model_rate_hz": REPORTED_TRAINED_RATE_HZ,
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
        "vendor_record": vendor_record(),
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
            "unlicensed_watermarked_output_never_admitted": True,
        },
        "candidate_metrics": None,
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no vendor SDK or audio runtime is used.",
            "Fixed workspace, SDK-worktree and home-cache paths are probed.",
            "No source checkout is executed and no vendor byte is loaded.",
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
        "vendor_record": report["vendor_record"],
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
