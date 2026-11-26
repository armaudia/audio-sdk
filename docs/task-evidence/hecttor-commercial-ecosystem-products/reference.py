# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local vendor-boundary evidence for SDK-HECTTOR-... .

Standard library only. The census names Hecttor Hermes noise cancellation as a
commercial native SDK with two optional denoising model families, a blend
control, six SDK language/platform targets, multiple sample rates and a
denoise-only module configuration. Evaluation access, a license key and a
platform build are supplied through onboarding. The census records no product
release, artifact hash, SDK version, frame/hop/reset contract, telemetry terms,
deployment terms, processed data, vendor output or score.

This module pins the evidence that does exist, proves a fixed absence inventory,
validates a fail-closed caller-supplied vendor-access manifest and a strict
vendor-output bundle without loading or executing anything, and builds canonical
DEFER bytes. Nothing here is a vendor runtime, vendor output, audio, quality,
timing, listening, benchmark or release result.
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

TASK = "SDK-HECTTOR-COMMERCIAL-ECOSYSTEM-PRODUCTS"
TASK_TITLE = "Hecttor / commercial ecosystem products"
COMPONENT_ID = "hecttor-commercial-ecosystem-products"
REPOSITORY = "audio-sdk"
MODE = "external-adapter"
PROFILE = "external"
PROFILE_LABEL = "External"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/hecttor-commercial-ecosystem-products/ only"
TASK_PREFIX = "docs/task-evidence/hecttor-commercial-ecosystem-products/"
CONTRACT_ID = "audio-sdk/hecttor-commercial-ecosystem-products-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/hecttor-commercial-ecosystem-products-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/hecttor-commercial-ecosystem-products-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/hecttor-vendor-access/0.1"
OUTPUT_SCHEMA_ID = "audio-sdk/hecttor-vendor-output/0.1"
BASE_COMMIT = "59971563b2c9cdf7b845e8210dd2697d55b8bc08"
BRANCH = "swarm/SDK-HECTTOR-COMMERCIAL-ECOSYSTEM-PRODUCTS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
REQUIRED_INTERPRETER = "3.12.16"
VENDOR_NAME = "Hecttor"
PRODUCT_FAMILY = "hermes"
PRODUCT_NAME = "Hermes noise cancellation"
REPORTED_PLATFORM_COUNT = 6
REPORTED_MODEL_FAMILIES = 2

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml root without a recursive walk or network use."""
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

# Read-only inputs. source: paths are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is never pinned.
SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
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
    "docs/task-evidence/h-gtcrn/README.md":
        "e36ed7a596a6f9954c492de441486464a8bc2d8fdd02222c5a6a6eb27eec3fe4",
    "docs/task-evidence/h-gtcrn/report.json":
        "d40ed21b30cd44806765aa6d11e3633601fd6b300aeca817572e4e9b2555a788",
    "docs/task-evidence/ai-coustics-quail/README.md":
        "66239ce8eeff8598145c0b356f09c91ece6a53f1cbe425a77e5b3d5bfc8e2781",
    "docs/task-evidence/ai-coustics-quail/report.json":
        "77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0",
    "docs/task-evidence/ai-coustics-rook/README.md":
        "ce038c74b0983d57f9d1d3f75713df810c9e2c5e9a3b79c6710b4012e6f44ff3",
    "docs/task-evidence/ai-coustics-rook/report.json":
        "e69a2bf3dd3e7fd496176c77c04285d9bd5d37f09fd4f76a51be394239832f20",
    "docs/task-evidence/desert-ant-labs-clear/README.md":
        "9be228d342086644c42e8bf6d3cebc8c0800a3050a91b2a7a4ecf55a061914c7",
    "docs/task-evidence/desert-ant-labs-clear/report.json":
        "d25b33e6ca4febbd6ea8af385c3736e96ce45ed31ccb46ad16740a4f81be52ac",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "allowed access",
    "exact candidate or processed data",
    "Separate local runtime, vendor-output scoring and vendor claim",
    "fallback and disclosure",
    "without a licensed runtime, code or asset in the default package",
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
    ".wasm", ".wav", ".weights",
}

# Fixed probes only; no recursive walk. All must remain absent.
WORKSPACE_PROBES = (
    "data/checkouts/hecttor",
    "data/checkouts/hecttor-hermes",
    "data/models/hecttor",
    "data/models/hecttor-hermes",
    "data/envs/hecttor-hermes",
    "data/licenses/hecttor-hermes",
    "data/manifests/hecttor-hermes-access.json",
    "data/reference/hecttor-hermes",
    "research/hecttor",
    "research/hecttor-hermes",
    "reports/hecttor-hermes",
)
WORKTREE_PROBES = (
    "adapters/hecttor-hermes",
    "schemas/providers/hecttor-hermes",
    "third_party/hecttor",
    "third_party/hecttor-hermes",
    "build/check-env/lib/python3.12/site-packages/hecttor",
)
HOME_PROBES = (
    "~/.cache/hecttor",
    "~/.config/hecttor",
    "~/Library/Application Support/Hecttor",
    "~/.cache/huggingface/hub/models--hecttor",
)

NON_CLAIMS = [
    "No Hecttor SDK, vendor binary, model asset, evaluation key, license "
    "text, onboarding record, runtime, processed data, vendor output or score "
    "is present, imported, linked, loaded or executed.",
    "No model inference, audio read or write, listening, paired SI-SDR or "
    "STOI scoring on candidate output, quality score, alignment, content "
    "delay or device-timing measurement is performed.",
    "No vendor claim is verified and no vendor-output scoring exists; the "
    "manifest and output checks are schema objects only.",
    "No product release version, SDK build, platform artifact, byte count, "
    "SHA-256, telemetry term or deployment term is asserted as verified.",
    "No ai-coustics, Desert Ant Labs, H-GTCRN or other sibling vendor/model "
    "result, fixture, checkpoint, term or score is inherited or pooled.",
    "No benchmark, quality, latency, resource, streaming, provider, product "
    "or release claim is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "ai-coustics-quail",
        "task": "SDK-AI-COUSTICS-QUAIL",
        "path": "docs/task-evidence/ai-coustics-quail/report.json",
        "class": "separate_commercial_vendor_component",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different proprietary vendor and model. Its manifest "
                    "shape, absence inventory and admission controls are not "
                    "Hecttor access, runtime, output or rights evidence.",
    },
    {
        "component": "ai-coustics-rook",
        "task": "SDK-AI-COUSTICS-ROOK",
        "path": "docs/task-evidence/ai-coustics-rook/report.json",
        "class": "separate_commercial_vendor_component",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different proprietary vendor and model. No Hecttor "
                    "product identity, access, score or term is inherited.",
    },
    {
        "component": "desert-ant-labs-clear",
        "task": "SDK-DESERT-ANT-LABS-CLEAR",
        "path": "docs/task-evidence/desert-ant-labs-clear/report.json",
        "class": "separate_commercial_vendor_component",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different commercial vendor. Its fallback disclosure "
                    "and controls do not establish Hecttor access or output.",
    },
    {
        "component": "h-gtcrn",
        "task": "SDK-H-GTCRN",
        "path": "docs/task-evidence/h-gtcrn/report.json",
        "class": "separate_open_model_component",
        "decision": "DEFER",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "An open-model feasibility lane, not a licensed vendor "
                    "product; no Hecttor counterpart or result is inferred.",
    },
)

HISTORICAL_EVIDENCE = (
    {
        "source": "research/noise_suppression_candidate_census.md",
        "class": "census_source_lead",
        "admitted_as_result": False,
        "boundary": "Names Hecttor Hermes noise cancellation as a commercial "
                    "native SDK with two optional model families, a blend "
                    "control, six SDK targets, multiple sample rates and "
                    "onboarding-gated access. It records no exact release, "
                    "artifact, term, processed data, output or score.",
    },
    {
        "source": "research/noise_suppression_assets_20261027.json",
        "class": "asset_register_absence",
        "admitted_as_result": False,
        "boundary": "The 20-row local asset register contains no Hecttor "
                    "entry, binary, key, platform build, hash or term.",
    },
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": "Marks hecttor-commercial-ecosystem-products as "
                    "considered, disposition external-adapter and "
                    "verification_profile external; it is not a result.",
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": "Defines the External profile requirements. No External "
                    "measurement, vendor output, fallback run or disclosure "
                    "record exists.",
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
        "all_probes_absent": all(row["present"] is False for row in rows),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "vendor_sdk_or_runtime_imported": False,
        "vendor_runtime_executed": False,
        "weights_loaded": False,
        "vendor_output_read": False,
        "audio_read": False,
    }


def asset_registry() -> dict:
    """Summarize the local asset register without inventing a Hecttor row."""
    path = AUDIO_ROOT / "research/noise_suppression_assets_20261027.json"
    document = read_strict_json(path)
    candidates = document.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("asset_register_candidates_not_list")
    ids = sorted(row.get("id") for row in candidates
                 if isinstance(row, dict) and isinstance(row.get("id"), str))
    if len(ids) != len(set(ids)):
        raise ValueError("asset_register_duplicate_id")
    hecttor_ids = [row_id for row_id in ids
                   if "hecttor" in row_id.lower()
                   or "hermes" in row_id.lower()]
    return {
        "path": "research/noise_suppression_assets_20261027.json",
        "candidate_count": len(ids),
        "candidate_ids_sha256": object_digest(ids),
        "hecttor_entry_present": bool(hecttor_ids),
        "hecttor_candidate_ids": hecttor_ids,
        "asset_identity_available_for_hecttor": False,
        "note": "The register contains 20 open or locally pinned components "
                "and no Hecttor product, vendor binary, evaluation key, "
                "platform build, hash or term.",
    }


def evidence_inputs() -> list[dict]:
    rows: list[dict] = []
    for relative in (
            "research/noise_suppression_candidate_census.md",
            "research/noise_suppression_assets_20261027.json",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/selected_audio_enhancement_candidates.md",
            "audio-benchmark-platform/plan/INVENTORY.json",
            "audio-benchmark-platform/plan/INVENTORY.md",
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "audio-benchmark-platform/plan/audio-sdk/README.md"):
        path = AUDIO_ROOT / relative
        payload = path.read_bytes()
        rows.append({
            "path": relative,
            "sha256": sha256_bytes(payload),
            "mentions_hecttor": (b"Hecttor" in payload
                                 or b"hecttor" in payload
                                 or b"Hermes" in payload
                                 or b"hermes" in payload),
            "is_result": False,
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
# Task, vendor and boundary records.
# ---------------------------------------------------------------------------


def vendor_record() -> dict:
    return {
        "vendor_name": VENDOR_NAME,
        "product_named": PRODUCT_NAME,
        "product_family": PRODUCT_FAMILY,
        "product_count_named_by_source": 1,
        "public_repository": None,
        "public_artifact_locator": None,
        "documentation_reported": True,
        "sdk_languages_platforms_reported": REPORTED_PLATFORM_COUNT,
        "sample_rates_reported": "multiple_unspecified",
        "denoising_model_families_reported": REPORTED_MODEL_FAMILIES,
        "blend_control_reported": True,
        "denoise_only_configuration_reported": True,
        "evaluation_onboarding_required": True,
        "license_key_required": True,
        "telemetry_terms_documented": False,
        "deployment_terms_documented": False,
        "immutable_release_version": None,
        "artifact_sha256": None,
        "terms_text_present": False,
        "license_identity_verified": False,
        "onboarding_approved": False,
        "runtime_pinned": False,
        "artifact_present": False,
        "processed_data_present": False,
        "output_present": False,
        "vendor_claim_verified": False,
        "vendor_output_scored": False,
        "source_or_model_portability_claim": False,
    }


def task_boundary() -> dict:
    return {
        "reported_product": PRODUCT_NAME,
        "reported_model_families": REPORTED_MODEL_FAMILIES,
        "reported_platform_targets": REPORTED_PLATFORM_COUNT,
        "reported_blend_control": True,
        "reported_denoise_only_module": True,
        "reported_sample_rate_hz": None,
        "reported_frame_samples": None,
        "reported_hop_samples": None,
        "reported_reset_contract": None,
        "reported_drain_contract": None,
        "reported_channel_layout": None,
        "reported_latency_ms": None,
        "reported_telemetry_terms": None,
        "exact_release_verified": False,
        "exact_sdk_verified": False,
        "exact_geometry_verified": False,
        "mono_v0_mapping_present": False,
        "source_or_model_portability_claim": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "hop_samples": 160,
        "sample_format": "f32",
        "preserved": True,
        "hecttor_mapping_present": False,
        "vendor_multirate_path_present": False,
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
        "onboarding_approved": False,
        "vendor_artifact_present": False,
        "runtime_present": False,
        "vendor_output_present": False,
        "rights_cleared_processed_data_present": False,
        "result_promoted": False,
        "summary": "Hecttor / commercial ecosystem products names one census "
                   "lead: Hermes noise cancellation, a commercial native SDK "
                   "with two optional model families, a blend control, six "
                   "SDK targets and multiple sample rates. Locally absent and "
                   "unverified: onboarding access, evaluation key, exact "
                   "release/build, terms, runtime, denoise-only isolation, "
                   "processed data, vendor output and score.",
    }


def scope_block() -> dict:
    return {
        "task_local_only": True,
        "network_access": False,
        "vendor_sdk_downloaded": False,
        "vendor_sdk_vendored": False,
        "model_weights_downloaded": False,
        "model_weights_vendored": False,
        "runtime_invoked": False,
        "vendor_runtime_executed": False,
        "real_audio": False,
        "processed_data_present": False,
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
        "vendor_sdk_or_audio_committed": False,
    }


def boundary_block() -> dict:
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
        "vendor_sdk_imported": False,
        "weights_vendored": False,
        "audio_added": False,
        "corpus_added": False,
        "processed_output_added": False,
        "telemetry_integration_added": False,
    }


def rights_gap() -> list[dict]:
    return [
        {"id": "RG-A", "item": "vendor_terms",
         "status": "unverified",
         "requirement": "Reviewed Hecttor product terms for the exact "
                        "release and platform build."},
        {"id": "RG-B", "item": "evaluation_license",
         "status": "unresolved",
         "requirement": "Approved evaluation license and key with scope, "
                        "duration, seats and permitted use."},
        {"id": "RG-C", "item": "telemetry_and_data_handling",
         "status": "unresolved",
         "requirement": "Documented telemetry, data handling, retention and "
                        "offline operation terms for the exact SDK."},
        {"id": "RG-D", "item": "deployment_and_redistribution",
         "status": "unresolved",
         "requirement": "Permitted deployment, redistribution, attribution "
                        "and bundled-asset terms."},
        {"id": "RG-E", "item": "processed_data_output_use",
         "status": "unresolved",
         "requirement": "Rights-cleared input audio, permitted vendor "
                        "processing, output retention and score publication."},
    ]


EXTERNAL_REQUIREMENTS = (
    {
        "id": "EXT-01",
        "requirement": "Document the allowed access and exact candidate or "
                       "processed data.",
        "status": "blocked",
        "evidence": "The census records onboarding-gated evaluation access "
                    "and a key requirement, but no approval, key, product "
                    "release or processed-data set exists locally.",
    },
    {
        "id": "EXT-02",
        "requirement": "Name and pin the exact vendor product, release, SDK "
                       "platform build and artifact identity.",
        "status": "blocked",
        "evidence": "Only the product name and broad capabilities are "
                    "reported; no version, build, byte count or SHA-256.",
    },
    {
        "id": "EXT-03",
        "requirement": "Pin the exact candidate or processed data and its "
                       "provenance.",
        "status": "blocked",
        "evidence": "No input clip, processed output, vendor result bundle "
                    "or provenance record is present.",
    },
    {
        "id": "EXT-04",
        "requirement": "Separate local runtime, vendor-output scoring and "
                       "vendor claim.",
        "status": "documented",
        "evidence": "The report keeps three explicit empty classes and never "
                    "pools them; no member of any class exists.",
    },
    {
        "id": "EXT-05",
        "requirement": "Verify the fallback and disclosure possible without a "
                       "licensed runtime, code or asset in the default "
                       "package.",
        "status": "documented",
        "evidence": "Fallback is limited to fixed absence probes, strict "
                    "shape-only manifest/output validation and an explicit "
                    "DEFER disclosure with no output.",
    },
    {
        "id": "EXT-06",
        "requirement": "Review vendor terms, telemetry, data handling and "
                       "deployment/redistribution.",
        "status": "blocked",
        "evidence": "No terms text, telemetry statement or deployment grant "
                    "is recorded or reviewed.",
    },
    {
        "id": "EXT-07",
        "requirement": "Isolate noise cancellation and disable Voice "
                       "Boost/speed-control at the exact SDK configuration.",
        "status": "blocked",
        "evidence": "The census recommends isolation but no runtime, API "
                    "surface or frozen configuration exists to verify it.",
    },
    {
        "id": "EXT-08",
        "requirement": "Produce matched vendor-output scoring and a separate "
                       "product comparison on an approved runtime.",
        "status": "blocked",
        "evidence": "No approved runtime, vendor output, scorer, cohort, "
                    "control, baseline or measured score exists.",
    },
)


def external_profile_block() -> dict:
    rows = [dict(row) for row in EXTERNAL_REQUIREMENTS]
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": PROFILE_SOURCE_REL,
        "profile_source_check": profile_row_check(),
        "requirement_rows": rows,
        "row_summary": {
            "requirement_count": len(rows),
            "blocked_count": sum(1 for row in rows
                                 if row["status"] == "blocked"),
            "documented_count": sum(1 for row in rows
                                    if row["status"] == "documented"),
            "real_result_count": 0,
            "profile_satisfied": False,
        },
        "approved_access_present": False,
        "exact_product_release_present": False,
        "processed_data_present": False,
        "local_runtime_result_present": False,
        "vendor_output_scoring_present": False,
        "vendor_claim_verified": False,
        "fallback_disclosure_documented": True,
        "telemetry_and_deployment_terms_reviewed": False,
        "denoise_only_isolation_verified": False,
    }


def profile_row_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| External |")]
    return {
        "path": PROFILE_SOURCE_REL,
        "row_count": len(rows),
        "unique_row": len(rows) == 1,
        "phrases_present": [phrase for phrase in PROFILE_PHRASES
                            if len(rows) == 1 and phrase in rows[0]],
        "all_phrases_present": len(rows) == 1 and all(
            phrase in rows[0] for phrase in PROFILE_PHRASES),
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers and gates.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "vendor_access",
         "Approved Hecttor evaluation onboarding for the exact product, with "
         "a named contact, scope, duration, permitted use, evaluation "
         "license text and key reference."),
        ("ART-02", "vendor_release",
         "The exact Hecttor Hermes release and platform build, with version, "
         "ABI, install location, byte counts, SHA-256 values and a signed "
         "artifact manifest."),
        ("ART-03", "runtime_lock",
         "A locked offline host runtime with exact OS, interpreter, vendor "
         "SDK, package versions, device, determinism settings and install "
         "digest."),
        ("ART-04", "rights_bundle",
         "Reviewed vendor, evaluation, telemetry, data-handling, deployment "
         "and redistribution terms, plus output-use and attribution "
         "permissions."),
        ("ART-05", "denoise_only_isolation",
         "Frozen denoise-only configuration with Voice Boost and "
         "speed-control disabled, exact rate/frame/hop/reset/drain contract, "
         "channel layout, blend/model selection and state behavior."),
        ("ART-06", "processed_data",
         "A rights-cleared input cohort with consent and a vendor-processed "
         "output bundle produced on the approved runtime for the frozen "
         "configuration."),
        ("ART-07", "external_results",
         "External results that keep local runtime, vendor-output scoring and "
         "vendor claim separate: controls, baseline, paired metrics where "
         "permitted, preservation, peaks, invalid outputs, alignment, "
         "timing, memory and uncertainty."),
    ]
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "bytes": None,
    } for artifact_id, kind, requirement in rows]


def exact_blockers() -> list[dict]:
    rows = [
        ("BLK-01", "ART-01", ["RG-01", "RG-03"],
         "Approved vendor access and evaluation entitlement",
         "No onboarding approval, evaluation license, key reference, scope, "
         "duration or permitted-use record exists. The census says access is "
         "supplied through onboarding only."),
        ("BLK-02", "ART-02", ["RG-01", "RG-02"],
         "Exact product release and platform artifact",
         "The source names the product and broad capabilities but no "
         "version, ABI, build, platform package, byte count or SHA-256. No "
         "vendor binary or signed manifest is present."),
        ("BLK-03", "ART-03", ["RG-02"],
         "Pinned offline host runtime",
         "No vendor SDK, interpreter lock, package lock, device profile, "
         "determinism setting or installable module exists."),
        ("BLK-04", "ART-04", ["RG-03"],
         "Vendor terms, telemetry and deployment rights",
         "Vendor, evaluation, telemetry, data-handling, deployment, "
         "redistribution and output-use terms are unresolved; no independent "
         "review reference exists."),
        ("BLK-05", "ART-05", ["RG-04"],
         "Denoise-only isolation and release contract",
         "No runtime or API surface exists to verify noise-only isolation, "
         "Voice Boost/speed-control disablement, rate/frame/hop, reset, "
         "drain, channel layout, model selection or blend control."),
        ("BLK-06", "ART-06", ["RG-05", "RG-06", "RG-07"],
         "Rights-cleared processed data, vendor output and separated results",
         "No input cohort, consent, vendor-processed output, approved "
         "runtime, scorer, control, baseline, vendor claim record or measured "
         "external result exists."),
    ]
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": linked_gates,
        "title": title,
        "state": state,
        "status": "open",
        "qualifies": False,
        "required_action": "Supply the named artifact and rights evidence, "
                           "then reproduce and independently review it.",
        "reopen_condition": "Only a caller-supplied exact artifact with "
                            "verified identity and rights can reopen this "
                            "blocker.",
    } for blocker_id, artifact_id, linked_gates, title, state in rows]


def release_gates() -> list[dict]:
    requirements = (
        ("Approved evaluation access, onboarding record, entitlement and "
         "exact Hecttor product/release identity."),
        ("Pinned vendor platform build and offline host runtime with exact "
         "versions, byte counts and SHA-256 values."),
        ("Reviewed vendor, evaluation, telemetry, deployment, "
         "redistribution and output-use terms."),
        ("Verified denoise-only isolation with Voice Boost and speed-control "
         "disabled and a frozen rate/frame/reset/drain contract."),
        ("Rights-cleared input cohort and vendor-processed output produced on "
         "the approved runtime."),
        ("Separated local-runtime, vendor-output-scoring and vendor-claim "
         "records with provenance and no pooling."),
        ("Matched external acceptance results: controls, baseline, paired "
         "metrics where permitted, preservation, peaks, invalid outputs, "
         "alignment, timing and memory."),
        ("Opt-in OFF-by-default provider intake, descriptor/default review, "
         "exact-head independent review and release approval."),
    )
    return [{
        "id": "RG-%02d" % index,
        "requirement": requirement,
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK,
        "reopen_condition": "The requirement is independently reproduced "
                            "with exact access, assets, rights and separated "
                            "external evidence.",
    } for index, requirement in enumerate(requirements, 1)]


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "all_release_gates_blocked": True,
        "real_result_present": False,
        "allowed_access_approved": False,
        "vendor_terms_reviewed": False,
        "exact_product_release": False,
        "sdk_artifact_present": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "telemetry_terms_reviewed": False,
        "deployment_terms_reviewed": False,
        "denoise_only_isolation_verified": False,
        "rights_cleared_processed_data": False,
        "vendor_output_present": False,
        "vendor_claim_verified": False,
        "vendor_output_scored": False,
        "local_runtime_result": False,
        "external_profile_result": False,
        "implementation_present": False,
        "reference_execution_result": False,
        "listening_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "peer_result_inherited": False,
        "reason": "Approved onboarding access, exact release/build, pinned "
                  "runtime, reviewed terms, denoise-only isolation, "
                  "rights-cleared processed data, vendor output, separated "
                  "scoring and independent review are all absent.",
    }


def linked_identity_block() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied vendor access manifest. It validates shape only;
# it never resolves a path, imports a vendor SDK, reads a key or runs a model.
# ---------------------------------------------------------------------------

MANIFEST_TOP_KEYS = ("schema_id", "manifest_id", "vendor", "sdk", "runtime",
                     "input", "controls", "rights")
VENDOR_KEYS = ("vendor_name", "product_family", "product", "release_version",
               "artifact_sha256", "terms_sha256", "onboarding_approved",
               "evaluation_key_sha256")
SDK_KEYS = ("platform", "version", "abi_version", "install_root",
            "telemetry_disclosure", "denoise_only", "voice_boost_disabled",
            "speed_control_disabled")
RUNTIME_KEYS = ("python_version", "host_platform", "device", "lock_sha256",
                "offline_load", "deterministic", "packages")
INPUT_KEYS = ("corpus_id", "split", "clip_count", "channels",
              "sample_rate_hz", "clean_reference", "consent",
              "rights_sha256")
CONTROL_KEYS = ("candidate", "identity_passthrough", "noisy_control",
                "task_matched_baseline", "nonfinite_rejection")
RIGHTS_KEYS = ("vendor_terms", "evaluation_license", "telemetry_terms",
               "deployment_terms", "corpus_rights",
               "clean_reference_permission", "output_use", "redistribution",
               "review_reference")
ALLOWED_RATES = (8000, 16000, 48000)
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "none", "null", "n/a", "noassertion",
}
MAX_PACKAGES = 128
MAX_CLIPS = 100_000


class _Invalid(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _field(prefix: str, name: str) -> str:
    return prefix + "." + name if prefix else name


def _exact_object(value: Any, fields: tuple[str, ...], prefix: str) -> dict:
    if not isinstance(value, dict):
        raise _Invalid("not_object", prefix or "root")
    missing = [name for name in fields if name not in value]
    if missing:
        raise _Invalid("missing_field", _field(prefix, missing[0]))
    unknown = sorted(name for name in value if name not in fields)
    if unknown:
        raise _Invalid("unknown_field", _field(prefix, unknown[0]))
    return value


def _text(value: Any, field: str, limit: int = 240) -> None:
    if not isinstance(value, str):
        raise _Invalid("invalid_text", field)
    if not value.strip():
        raise _Invalid("empty_text", field)
    if len(value) > limit:
        raise _Invalid("out_of_range", field)
    if any(ord(character) < 32 for character in value):
        raise _Invalid("invalid_text", field)
    if value.strip().lower() in UNRESOLVED_VALUES:
        raise _Invalid("unresolved_value", field)


def _slug(value: Any, field: str) -> None:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise _Invalid("invalid_slug", field)


def _sha(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise _Invalid("invalid_sha256", field)


def _hex40(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise _Invalid("invalid_revision", field)


def _version(value: Any, field: str) -> None:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise _Invalid("invalid_version", field)


def _safe_absolute(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise _Invalid("unsafe_path", field)
    if not value.startswith("/") or "\\" in value or "\x00" in value:
        raise _Invalid("unsafe_path", field)
    if any(ord(character) < 32 for character in value):
        raise _Invalid("unsafe_path", field)
    if any(part in ("", ".", "..") for part in value.split("/")[1:]):
        raise _Invalid("unsafe_path", field)


def _bounded_int(value: Any, low: int, high: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _Invalid("invalid_integer", field)
    if value < low or value > high:
        raise _Invalid("out_of_range", field)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise _Invalid("invalid_boolean", field)


def _list(value: Any, field: str, low: int, high: int) -> list:
    if not isinstance(value, list):
        raise _Invalid("not_list", field)
    if len(value) < low:
        raise _Invalid("missing_required_value", field)
    if len(value) > high:
        raise _Invalid("out_of_range", field)
    return value


def _sorted_unique(items: list[dict], key: str, field: str) -> None:
    keys = [item[key] for item in items]
    if len(set(keys)) != len(keys):
        raise _Invalid("duplicate_value", field)
    if keys != sorted(keys):
        raise _Invalid("noncanonical_order", field)


def _reject(code: str, field: str = "") -> dict:
    return {"status": "rejected", "code": code, "field": field}


def _accept(checks: int) -> dict:
    return {"status": "accepted", "checks": checks, "qualifies": False}


def _require_true_map(document: Any, keys: tuple[str, ...],
                      prefix: str) -> int:
    value = _exact_object(document, keys, prefix)
    checks = 0
    for name in keys:
        _boolean(value[name], prefix + "." + name)
        if not value[name]:
            code = "rights_not_cleared" if prefix == "rights" else \
                "missing_required_value"
            raise _Invalid(code, prefix + "." + name)
        checks += 1
    return checks


def validate_manifest(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object", "")
    try:
        assert_no_float(document)
    except ValueError:
        return _reject("float_not_allowed", "")
    try:
        _exact_object(document, MANIFEST_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["manifest_id"], "manifest_id")
        checks += 1

        vendor = _exact_object(document["vendor"], VENDOR_KEYS, "vendor")
        if vendor["vendor_name"] != VENDOR_NAME:
            raise _Invalid("invalid_vendor_name", "vendor.vendor_name")
        if vendor["product_family"] != PRODUCT_FAMILY:
            raise _Invalid("invalid_product_family", "vendor.product_family")
        if vendor["product"] != PRODUCT_FAMILY:
            raise _Invalid("invalid_product", "vendor.product")
        _version(vendor["release_version"], "vendor.release_version")
        _sha(vendor["artifact_sha256"], "vendor.artifact_sha256")
        _sha(vendor["terms_sha256"], "vendor.terms_sha256")
        _boolean(vendor["onboarding_approved"],
                 "vendor.onboarding_approved")
        _sha(vendor["evaluation_key_sha256"],
             "vendor.evaluation_key_sha256")
        checks += 8
        if not vendor["onboarding_approved"]:
            raise _Invalid("access_not_approved", "vendor.onboarding_approved")

        sdk = _exact_object(document["sdk"], SDK_KEYS, "sdk")
        _text(sdk["platform"], "sdk.platform", 120)
        _version(sdk["version"], "sdk.version")
        _text(sdk["abi_version"], "sdk.abi_version", 40)
        _safe_absolute(sdk["install_root"], "sdk.install_root")
        _boolean(sdk["telemetry_disclosure"], "sdk.telemetry_disclosure")
        _boolean(sdk["denoise_only"], "sdk.denoise_only")
        _boolean(sdk["voice_boost_disabled"], "sdk.voice_boost_disabled")
        _boolean(sdk["speed_control_disabled"], "sdk.speed_control_disabled")
        checks += 8
        if not sdk["telemetry_disclosure"]:
            raise _Invalid("telemetry_not_disclosed", "sdk.telemetry_disclosure")
        if not sdk["denoise_only"]:
            raise _Invalid("denoise_not_isolated", "sdk.denoise_only")
        if not sdk["voice_boost_disabled"]:
            raise _Invalid("voice_boost_enabled", "sdk.voice_boost_disabled")
        if not sdk["speed_control_disabled"]:
            raise _Invalid("speed_control_enabled", "sdk.speed_control_disabled")

        runtime = _exact_object(document["runtime"], RUNTIME_KEYS, "runtime")
        if runtime["python_version"] != REQUIRED_INTERPRETER:
            raise _Invalid("wrong_python_version", "runtime.python_version")
        _text(runtime["host_platform"], "runtime.host_platform", 120)
        _text(runtime["device"], "runtime.device", 120)
        _sha(runtime["lock_sha256"], "runtime.lock_sha256")
        _boolean(runtime["offline_load"], "runtime.offline_load")
        _boolean(runtime["deterministic"], "runtime.deterministic")
        packages = _list(runtime["packages"], "runtime.packages", 1,
                         MAX_PACKAGES)
        for index, item in enumerate(packages):
            prefix = "runtime.packages[" + str(index) + "]"
            _exact_object(item, ("name", "version"), prefix)
            _text(item["name"], prefix + ".name", 120)
            _text(item["version"], prefix + ".version", 120)
            checks += 2
        _sorted_unique(packages, "name", "runtime.packages")
        checks += 9
        if not runtime["offline_load"]:
            raise _Invalid("non_offline_runtime", "runtime.offline_load")
        if not runtime["deterministic"]:
            raise _Invalid("nondeterministic_runtime", "runtime.deterministic")

        payload = _exact_object(document["input"], INPUT_KEYS, "input")
        _slug(payload["corpus_id"], "input.corpus_id")
        if payload["split"] not in ("dev", "test", "heldout"):
            raise _Invalid("invalid_split", "input.split")
        _bounded_int(payload["clip_count"], 1, MAX_CLIPS, "input.clip_count")
        _bounded_int(payload["channels"], 1, 32, "input.channels")
        if payload["channels"] != 1:
            raise _Invalid("invalid_channels", "input.channels")
        _bounded_int(payload["sample_rate_hz"], 8000, 192000,
                     "input.sample_rate_hz")
        if payload["sample_rate_hz"] not in ALLOWED_RATES:
            raise _Invalid("unsupported_sample_rate", "input.sample_rate_hz")
        _boolean(payload["clean_reference"], "input.clean_reference")
        _boolean(payload["consent"], "input.consent")
        _sha(payload["rights_sha256"], "input.rights_sha256")
        checks += 9
        if not payload["clean_reference"]:
            raise _Invalid("clean_reference_not_permitted",
                           "input.clean_reference")
        if not payload["consent"]:
            raise _Invalid("rights_not_cleared", "input.consent")

        checks += _require_true_map(document["controls"], CONTROL_KEYS,
                                    "controls")
        rights = _exact_object(document["rights"], RIGHTS_KEYS, "rights")
        checks += 1
        for name in RIGHTS_KEYS[:-1]:
            _boolean(rights[name], "rights." + name)
            if not rights[name]:
                raise _Invalid("rights_not_cleared", "rights." + name)
            checks += 1
        _text(rights["review_reference"], "rights.review_reference", 240)
        checks += 1
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_id": "hecttor-hermes-synthetic-schema-control",
        "vendor": {
            "vendor_name": VENDOR_NAME,
            "product_family": PRODUCT_FAMILY,
            "product": PRODUCT_FAMILY,
            "release_version": "1.0.0",
            "artifact_sha256": "1" * 64,
            "terms_sha256": "2" * 64,
            "onboarding_approved": True,
            "evaluation_key_sha256": "3" * 64,
        },
        "sdk": {
            "platform": "macos-arm64",
            "version": "1.0.0",
            "abi_version": "1",
            "install_root": "/opt/hecttor/hermes/1.0.0",
            "telemetry_disclosure": True,
            "denoise_only": True,
            "voice_boost_disabled": True,
            "speed_control_disabled": True,
        },
        "runtime": {
            "python_version": REQUIRED_INTERPRETER,
            "host_platform": "macos-arm64",
            "device": "cpu",
            "lock_sha256": "9" * 64,
            "offline_load": True,
            "deterministic": True,
            "packages": [{"name": "synthetic-vendor-runtime",
                          "version": "1.0.0"}],
        },
        "input": {
            "corpus_id": "synthetic-schema-control",
            "split": "dev",
            "clip_count": 1,
            "channels": 1,
            "sample_rate_hz": 16000,
            "clean_reference": True,
            "consent": True,
            "rights_sha256": "a" * 64,
        },
        "controls": {name: True for name in CONTROL_KEYS},
        "rights": {
            **{name: True for name in RIGHTS_KEYS[:-1]},
            "review_reference": "synthetic-schema-control-no-review",
        },
    }


# Vendor-output bundle: a caller-signed record of processed data. It is parsed
# and shape-checked only; no audio is opened and no score is computed.

OUTPUT_TOP_KEYS = ("schema_id", "bundle_id", "manifest_sha256", "runtime_kind",
                   "clip_count", "channels", "sample_rate_hz", "outputs",
                   "claim", "rights")
OUTPUT_ROW_KEYS = ("clip_id", "input_sha256", "output_sha256", "byte_count",
                   "finite", "channels", "sample_rate_hz")
OUTPUT_CLAIM_KEYS = ("vendor_claim_reference", "vendor_claim_verified",
                     "scored_locally", "score_sha256")
OUTPUT_RIGHTS_KEYS = ("vendor_output_use", "retention", "publication",
                      "review_reference")
RUNTIME_KINDS = ("vendor_runtime", "vendor_output_only")


def validate_output_bundle(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("bundle_not_object", "")
    try:
        assert_no_float(document)
    except ValueError:
        return _reject("float_not_allowed", "")
    try:
        _exact_object(document, OUTPUT_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != OUTPUT_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["bundle_id"], "bundle_id")
        _sha(document["manifest_sha256"], "manifest_sha256")
        if document["runtime_kind"] not in RUNTIME_KINDS:
            raise _Invalid("invalid_runtime_kind", "runtime_kind")
        _bounded_int(document["clip_count"], 1, MAX_CLIPS, "clip_count")
        _bounded_int(document["channels"], 1, 2, "channels")
        _bounded_int(document["sample_rate_hz"], 8000, 192000,
                     "sample_rate_hz")
        if document["sample_rate_hz"] not in ALLOWED_RATES:
            raise _Invalid("unsupported_sample_rate", "sample_rate_hz")
        checks += 6
        outputs = _list(document["outputs"], "outputs", 1, MAX_CLIPS)
        if len(outputs) != document["clip_count"]:
            raise _Invalid("clip_count_mismatch", "outputs")
        for index, item in enumerate(outputs):
            prefix = "outputs[" + str(index) + "]"
            _exact_object(item, OUTPUT_ROW_KEYS, prefix)
            _slug(item["clip_id"], prefix + ".clip_id")
            _sha(item["input_sha256"], prefix + ".input_sha256")
            _sha(item["output_sha256"], prefix + ".output_sha256")
            _bounded_int(item["byte_count"], 1, 2 ** 40,
                         prefix + ".byte_count")
            _boolean(item["finite"], prefix + ".finite")
            _bounded_int(item["channels"], 1, 2, prefix + ".channels")
            _bounded_int(item["sample_rate_hz"], 8000, 192000,
                         prefix + ".sample_rate_hz")
            if not item["finite"]:
                raise _Invalid("nonfinite_output", prefix + ".finite")
            if item["channels"] != document["channels"]:
                raise _Invalid("channel_mismatch", prefix + ".channels")
            if item["sample_rate_hz"] != document["sample_rate_hz"]:
                raise _Invalid("rate_mismatch", prefix + ".sample_rate_hz")
            checks += 7
        _sorted_unique(outputs, "clip_id", "outputs")
        checks += 1
        claim = _exact_object(document["claim"], OUTPUT_CLAIM_KEYS, "claim")
        _text(claim["vendor_claim_reference"], "claim.vendor_claim_reference")
        _boolean(claim["vendor_claim_verified"],
                 "claim.vendor_claim_verified")
        _boolean(claim["scored_locally"], "claim.scored_locally")
        _sha(claim["score_sha256"], "claim.score_sha256")
        checks += 4
        rights = _exact_object(document["rights"], OUTPUT_RIGHTS_KEYS, "rights")
        checks += 1
        for name in OUTPUT_RIGHTS_KEYS[:-1]:
            _boolean(rights[name], "rights." + name)
            if not rights[name]:
                raise _Invalid("rights_not_cleared", "rights." + name)
            checks += 1
        _text(rights["review_reference"], "rights.review_reference", 240)
        checks += 1
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _output_control() -> dict:
    return {
        "schema_id": OUTPUT_SCHEMA_ID,
        "bundle_id": "hecttor-hermes-synthetic-output-control",
        "manifest_sha256": "b" * 64,
        "runtime_kind": "vendor_output_only",
        "clip_count": 1,
        "channels": 1,
        "sample_rate_hz": 16000,
        "outputs": [{
            "clip_id": "synthetic-clip",
            "input_sha256": "c" * 64,
            "output_sha256": "d" * 64,
            "byte_count": 64000,
            "finite": True,
            "channels": 1,
            "sample_rate_hz": 16000,
        }],
        "claim": {
            "vendor_claim_reference": "synthetic-schema-control-no-claim",
            "vendor_claim_verified": False,
            "scored_locally": False,
            "score_sha256": "e" * 64,
        },
        "rights": {
            "vendor_output_use": True,
            "retention": True,
            "publication": True,
            "review_reference": "synthetic-schema-control-no-review",
        },
    }


def _mutation_case(case_id: str, mutate: Any, code: str,
                   validator: Any = None) -> dict:
    document = copy.deepcopy(
        _manifest_control() if validator is validate_manifest
        else _output_control() if validator is validate_output_bundle
        else _manifest_control())
    mutate(document)
    result = (validator or validate_manifest)(document)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("mutation_case_did_not_reject:" + case_id + ":" +
                         str(result))
    return _case_row(case_id, result, True)


def _raw_case(case_id: str, raw: str, code: str) -> dict:
    try:
        loads_strict(raw)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("raw_case_code_mismatch:" + case_id + ":" +
                             observed) from error
        return _case_row(case_id, _reject(observed), True)
    raise ValueError("raw_case_did_not_reject:" + case_id)


def _case_row(case_id: str, result: dict, synthetic: bool,
              accepted: bool = False) -> dict:
    return {
        "id": case_id,
        "status": "accepted" if accepted else result["status"],
        "code": "none" if accepted else result.get("code", ""),
        "field": "" if accepted else result.get("field", ""),
        "qualifies": False,
        "state_unchanged": not accepted,
        "synthetic_schema_control": synthetic,
    }


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_manifest(_manifest_control()), True,
                         accepted=True)
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_manifest(["not", "a", "manifest"]),
                           True))
    cases.append(_case_row("root-null", validate_manifest(None), True))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"audio-sdk/hecttor-vendor-access/0.1",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"audio-sdk/hecttor-vendor-access/0.1","value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"audio-sdk/hecttor-vendor-access/0.1",'
        '"value":Infinity}',
        "nonfinite_json"))
    cases.append(_mutation_case(
        "float-value", lambda m: m["input"].update(
            {"clip_count": 1.0}), "float_not_allowed", validate_manifest))
    cases.append(_mutation_case(
        "missing-vendor", lambda m: m.pop("vendor"), "missing_field",
        validate_manifest))
    cases.append(_mutation_case(
        "unknown-top-key", lambda m: m.update({"extra": True}),
        "unknown_field", validate_manifest))
    cases.append(_mutation_case(
        "invalid-manifest-id",
        lambda m: m.update({"manifest_id": "Bad ID"}), "invalid_slug",
        validate_manifest))
    cases.append(_mutation_case(
        "invalid-vendor-name",
        lambda m: m["vendor"].update({"vendor_name": "OtherVendor"}),
        "invalid_vendor_name", validate_manifest))
    cases.append(_mutation_case(
        "invalid-product-family",
        lambda m: m["vendor"].update({"product_family": "atlas"}),
        "invalid_product_family", validate_manifest))
    cases.append(_mutation_case(
        "invalid-release-version",
        lambda m: m["vendor"].update({"release_version": "latest"}),
        "invalid_version", validate_manifest))
    cases.append(_mutation_case(
        "invalid-artifact-sha",
        lambda m: m["vendor"].update({"artifact_sha256": "xyz"}),
        "invalid_sha256", validate_manifest))
    cases.append(_mutation_case(
        "invalid-terms-sha",
        lambda m: m["vendor"].update({"terms_sha256": "nothex"}),
        "invalid_sha256", validate_manifest))
    cases.append(_mutation_case(
        "onboarding-not-approved",
        lambda m: m["vendor"].update({"onboarding_approved": False}),
        "access_not_approved", validate_manifest))
    cases.append(_mutation_case(
        "missing-evaluation-key",
        lambda m: m["vendor"].pop("evaluation_key_sha256"), "missing_field",
        validate_manifest))
    cases.append(_mutation_case(
        "empty-sdk-platform",
        lambda m: m["sdk"].update({"platform": ""}), "empty_text",
        validate_manifest))
    cases.append(_mutation_case(
        "relative-install-root",
        lambda m: m["sdk"].update({"install_root": "opt/hecttor"}),
        "unsafe_path", validate_manifest))
    cases.append(_mutation_case(
        "traversal-install-root",
        lambda m: m["sdk"].update({"install_root": "/opt/../etc/hecttor"}),
        "unsafe_path", validate_manifest))
    cases.append(_mutation_case(
        "telemetry-not-disclosed",
        lambda m: m["sdk"].update({"telemetry_disclosure": False}),
        "telemetry_not_disclosed", validate_manifest))
    cases.append(_mutation_case(
        "denoise-not-isolated",
        lambda m: m["sdk"].update({"denoise_only": False}),
        "denoise_not_isolated", validate_manifest))
    cases.append(_mutation_case(
        "voice-boost-enabled",
        lambda m: m["sdk"].update({"voice_boost_disabled": False}),
        "voice_boost_enabled", validate_manifest))
    cases.append(_mutation_case(
        "speed-control-enabled",
        lambda m: m["sdk"].update({"speed_control_disabled": False}),
        "speed_control_enabled", validate_manifest))
    cases.append(_mutation_case(
        "missing-runtime-lock",
        lambda m: m["runtime"].pop("lock_sha256"), "missing_field",
        validate_manifest))
    cases.append(_mutation_case(
        "wrong-python-version",
        lambda m: m["runtime"].update({"python_version": "3.11.0"}),
        "wrong_python_version", validate_manifest))
    cases.append(_mutation_case(
        "non-offline-runtime",
        lambda m: m["runtime"].update({"offline_load": False}),
        "non_offline_runtime", validate_manifest))
    cases.append(_mutation_case(
        "nondeterministic-runtime",
        lambda m: m["runtime"].update({"deterministic": False}),
        "nondeterministic_runtime", validate_manifest))
    cases.append(_mutation_case(
        "empty-runtime-packages",
        lambda m: m["runtime"].update({"packages": []}),
        "missing_required_value", validate_manifest))
    cases.append(_mutation_case(
        "duplicate-package-name",
        lambda m: m["runtime"]["packages"].append(
            {"name": "synthetic-vendor-runtime", "version": "1.0.1"}),
        "duplicate_value", validate_manifest))
    cases.append(_mutation_case(
        "invalid-corpus-split",
        lambda m: m["input"].update({"split": "train"}), "invalid_split",
        validate_manifest))
    cases.append(_mutation_case(
        "zero-clip-count",
        lambda m: m["input"].update({"clip_count": 0}), "out_of_range",
        validate_manifest))
    cases.append(_mutation_case(
        "stereo-input",
        lambda m: m["input"].update({"channels": 2}), "invalid_channels",
        validate_manifest))
    cases.append(_mutation_case(
        "unsupported-sample-rate",
        lambda m: m["input"].update({"sample_rate_hz": 44100}),
        "unsupported_sample_rate", validate_manifest))
    cases.append(_mutation_case(
        "missing-clean-reference",
        lambda m: m["input"].update({"clean_reference": False}),
        "clean_reference_not_permitted", validate_manifest))
    cases.append(_mutation_case(
        "unconsented-input",
        lambda m: m["input"].update({"consent": False}),
        "rights_not_cleared", validate_manifest))
    cases.append(_mutation_case(
        "missing-control",
        lambda m: m["controls"].pop("identity_passthrough"),
        "missing_field", validate_manifest))
    cases.append(_mutation_case(
        "false-control",
        lambda m: m["controls"].update({"task_matched_baseline": False}),
        "missing_required_value", validate_manifest))
    cases.append(_mutation_case(
        "missing-right",
        lambda m: m["rights"].pop("output_use"), "missing_field",
        validate_manifest))
    cases.append(_mutation_case(
        "false-right",
        lambda m: m["rights"].update({"redistribution": False}),
        "rights_not_cleared", validate_manifest))
    cases.append(_mutation_case(
        "unresolved-review-reference",
        lambda m: m["rights"].update({"review_reference": "unknown"}),
        "unresolved_value", validate_manifest))
    cases.append(_mutation_case(
        "nonfinite-output",
        lambda m: m["outputs"][0].update({"finite": False}),
        "nonfinite_output", validate_output_bundle))
    cases.append(_mutation_case(
        "output-clip-count-mismatch",
        lambda m: m.update({"clip_count": 2}), "clip_count_mismatch",
        validate_output_bundle))
    cases.append(_mutation_case(
        "output-channel-mismatch",
        lambda m: m["outputs"][0].update({"channels": 2}),
        "channel_mismatch", validate_output_bundle))
    cases.append(_mutation_case(
        "output-unscored-claim-missing",
        lambda m: m["claim"].pop("score_sha256"), "missing_field",
        validate_output_bundle))
    cases.append(_mutation_case(
        "output-rights-uncleared",
        lambda m: m["rights"].update({"publication": False}),
        "rights_not_cleared", validate_output_bundle))

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    return {
        "cases": cases,
        "controls": admission_contract_block(),
        "output_control": _case_row(
            "accepted-output-schema-control",
            validate_output_bundle(_output_control()), True, accepted=True),
        "output_summary": {
            "schema_control_qualifies": False,
            "scored_locally": False,
            "vendor_output_present": False,
            "audio_read": False,
            "runtime_invoked": False,
        },
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(rejected),
            "accepted_schema_controls": len(accepted_cases),
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "accepted_control_qualifies": False,
            "all_adverse_cases_rejected": len(rejected) == len(cases) - len(
                accepted_cases),
            "runtime_invoked": False,
            "vendor_runtime_executed": False,
            "vendor_output_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
    }


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": "audio-sdk/hecttor-vendor-access-contract/0.1",
        "output_schema_id": OUTPUT_SCHEMA_ID,
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "vendor_fields": list(VENDOR_KEYS),
        "sdk_fields": list(SDK_KEYS),
        "runtime_fields": list(RUNTIME_KEYS),
        "input_fields": list(INPUT_KEYS),
        "control_keys": list(CONTROL_KEYS),
        "right_keys": list(RIGHTS_KEYS),
        "output_row_fields": list(OUTPUT_ROW_KEYS),
        "output_claim_keys": list(OUTPUT_CLAIM_KEYS),
        "output_rights_keys": list(OUTPUT_RIGHTS_KEYS),
        "runtime_kinds": list(RUNTIME_KINDS),
        "allowed_rates_hz": list(ALLOWED_RATES),
        "exact_interpreter": REQUIRED_INTERPRETER,
        "required_channels": 1,
        "max_packages": MAX_PACKAGES,
        "max_clips": MAX_CLIPS,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_vendor_sdk_invoked": False,
        "manifest_validation_only": True,
    }


# ---------------------------------------------------------------------------
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "task_boundary": task_boundary(),
        "vendor_record": vendor_record(),
        "asset_registry": asset_registry(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "external_profile": external_profile_block(),
        "rights_gap": rights_gap(),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "board_row_projection": projection,
        "board_row_sha256": board_row_digest(projection),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "admission_contract": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_files": list(LOCAL_FILES),
        "non_claims": list(NON_CLAIMS),
        "write_scope": WRITE_SCOPE,
        "qualification": qualification_block(),
    }


def build_report() -> dict:
    contract = build_contract()
    probes = all_probes()
    summary = absence_summary(probes)
    if summary["present_count"] != 0:
        raise ValueError("absence_probe_present_reopen_required")
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
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "task_boundary": task_boundary(),
        "vendor_record": vendor_record(),
        "asset_registry": asset_registry(),
        "evidence_inputs": evidence_inputs(),
        "absence_evidence": {
            "workspace_probes": workspace_probes(),
            "worktree_probes": worktree_probes(),
            "home_probes": home_probes(),
            "summary": summary,
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": linked_identity_block(),
        "external_profile": external_profile_block(),
        "external_profile_requirements":
            [dict(row) for row in EXTERNAL_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": [dict(row) for row in HISTORICAL_EVIDENCE],
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "standard_library_only": True,
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                "test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            ],
        },
        "write_scope": WRITE_SCOPE,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    expected = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise ValueError("contract_field_mismatch:" + key)
    if contract.get("proposal_only") is not True \
            or contract.get("incomplete") is not True:
        raise ValueError("contract_disposition_flags")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("source_pins") != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    if contract.get("local_files") != list(LOCAL_FILES):
        raise ValueError("contract_local_files_mismatch")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, row in enumerate(gates, 1):
        if row.get("id") != "RG-%02d" % index:
            raise ValueError("contract_gate_id")
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if row.get("linked_row") != TASK:
            raise ValueError("contract_gate_link")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 7:
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if row.get("present") is not False or row.get("verified") is not False \
                or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    qualification = contract.get("qualification", {})
    if qualification.get("status") != QUALIFICATION_STATUS \
            or qualification.get("all_release_gates_blocked") is not True:
        raise ValueError("contract_qualification_invalid")
    profile = contract.get("external_profile", {})
    rows = profile.get("requirement_rows", [])
    if len(rows) != len(EXTERNAL_REQUIREMENTS) \
            or profile.get("row_summary", {}).get("real_result_count") != 0 \
            or profile.get("row_summary", {}).get("profile_satisfied") is not False:
        raise ValueError("contract_external_profile_invalid")
    assert_no_float(contract)


# ---------------------------------------------------------------------------
# Task-local git scope. The base is the newest merge-base between HEAD and the
# available PR base refs, not a fixed historical commit. This keeps later
# sibling merges out of the comparison while still failing closed on any edit
# outside TASK_PREFIX.
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
