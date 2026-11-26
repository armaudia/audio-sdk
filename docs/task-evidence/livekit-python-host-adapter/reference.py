# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-LIVEKIT-PYTHON-HOST-ADAPTER.

This module never installs, imports or executes a LiveKit host package, never
loads the audio-sdk native library, never reads real audio and never runs a
room, participant, device or benchmark. No pinned LiveKit host package pair is
present and no package install/download is permitted in this task.

The module pins stable read-only inputs, proves fixed absence probes, models a
caller-supplied host-adapter contract and a structural 48 kHz -> 16 kHz
10 ms frame control at the public SDK v0 geometry, and emits canonical JSON.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                  str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/livekit-python-host-adapter/"

TASK = "SDK-LIVEKIT-PYTHON-HOST-ADAPTER"
TITLE = "LiveKit Python host adapter"
COMPONENT = "livekit-python-host-adapter"
COMPONENT_ID = "livekit-python-host-adapter"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "tool"
PROFILE_KEY = "Tool"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "any_livekit_host_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/livekit-python-host-adapter-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/livekit-python-host-adapter-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/livekit-python-host-adapter-report/0.1"
BASE_COMMIT = "b02dbf12499038abc4f9b6b1c06cdecc76a79dcd"
BRANCH = "swarm/SDK-LIVEKIT-PYTHON-HOST-ADAPTER"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-LIVEKIT-PYTHON-HOST-ADAPTER")
REVIEWER = "reviewer-LIVEKIT-PYTHON-HOST-ADAPTER"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PINNED_PYTHON = "3.12.16"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+){0,3}(?:[-+][A-Za-z0-9.]{1,32})?$")
PYTHON_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
PLATFORM = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
SCOPE_TOKEN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
BUILD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,127}$")
COMMIT_PATTERN = HEX40

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed or installed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "audio-benchmark-platform/audio-sdk/docs/acceptance-matrix.md":
        "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "TEST_PLAN.md":
        "f0508583243ab5decd6d61a6d69c50ecd878c60b32e77bbb0b080c03a11fa4e5",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "bindings/python/pyproject.toml":
        "0f3b1e736dd807a984cbb9daa10cd0ba32668f7833994c3c4f0a5021799c95a4",
    "bindings/python/tests/test_sdk.py":
        "32c4cecab24b00fc3be312f64e9def05a5391b0f475cd9d461321e8fc4d4c101",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
STABLE_TASK_FIELDS = ("acceptance", "component", "deliverable", "depends_on",
                      "evidence", "id", "mode", "repository", "title",
                      "write_scope")
MUTABLE_FIELDS_EXCLUDED = ("blocked_reason", "dispatch_priority", "handoff",
                           "owner", "review", "status")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
ACCEPTANCE_SOURCE_REL = (
    "audio-benchmark-platform/audio-sdk/docs/acceptance-matrix.md")
PROFILE_PHRASES = (
    "version, install location",
    "clean checkout or extracted package",
    "typical CLI/API use",
    "caller-owned inputs",
    "malformed inputs",
    "missing optional selections",
    "compile/build evidence",
    "synthetic runtime evidence",
    "measured workload support",
)

# ---------------------------------------------------------------------------
# Host identity. Only the component name from the board and the SDK's own
# recorded gap are claimed. No LiveKit package, revision, API or geometry is
# asserted as verified.
# ---------------------------------------------------------------------------

HOST_NAME = "LiveKit Python host"
HOST_FAMILY = "livekit_python_host_family"
HOST_GEOMETRY_STATUS = "unestablished"
HOST_API_STATUS = "unverified_no_pinned_package_or_api_record"
HOST_LICENSE_STATUS = "unverified_no_license_record_present"
HOST_PACKAGE_PAIR_PINNED = False
HOST_PACKAGE_IMPORTED = False
SDK_LIBRARY_LOADED = False
TASK_SCOPE = "livekit_python_host_audio_adapter"
TASK_KIND = "caller_clocked_python_host_frame_adapter"
CALLER_VARIANT = "caller_clocked_paced_streaming"
CALLER_SCOPE = TASK_SCOPE

SOURCE_REPORTED_CONTEXT = {
    "label": "source_reported_not_measured_here",
    "source": ACCEPTANCE_SOURCE_REL,
    "source_sha256": SOURCE_PINS[ACCEPTANCE_SOURCE_REL],
    "recorded_gap": (
        "S09 LiveKit host is Blocked / excluded because there is no "
        "pinned/tested LiveKit host package pair, and S-T11 LiveKit is "
        "Excluded because S09 is blocked."),
    "recorded_scope": (
        "The pinned matrix records only the blocked/excluded host row; no "
        "host package version, wheel, runtime, room, participant, conversion "
        "or timing result is recorded."),
    "notes": (
        "This package reads only the pinned acceptance matrix, acceptance "
        "profile, inventory record, SDK test plan and SDK Python binding "
        "source. It does not contact LiveKit, download a package, install a "
        "wheel, create a room or token, read a recording or treat a public "
        "product description as a verified API."),
}

# ---------------------------------------------------------------------------
# Fixed absence probes. No recursive walk and no download. Every probe must
# stay absent.
# ---------------------------------------------------------------------------

HOST_PROBE_PATHS = (
    "data/envs/livekit-host",
    "data/envs/livekit-host/requirements.lock",
    "data/packages/livekit",
    "data/packages/livekit-agents",
    "data/checkouts/livekit-agents",
    "data/checkouts/livekit-python",
    "vendor/livekit",
    "third_party/livekit",
    "deps/livekit",
    "wheels/livekit",
)
SDK_BUILD_PROBE_PATHS = (
    "build/acceptance/python312",
    "build/python-wheel",
    "build/install/lib/libaudio_sdk.dylib",
    "build/install/lib/libaudio_sdk.so",
    "data/installed/audio-sdk-python",
)
RIGHTS_PROBE_PATHS = (
    "data/rights/livekit-host-rights.json",
    "data/rights/livekit-host-audio-rights.json",
    "data/audio/livekit-host-cohort",
)
EVIDENCE_PROBE_PATHS = (
    "data/runs/livekit-host-adapter/manifest.json",
    "data/runs/livekit-host-adapter/geometry.json",
    "data/runs/livekit-host-adapter/session.json",
)
ABSENCE_PROBE_PATHS = (HOST_PROBE_PATHS + SDK_BUILD_PROBE_PATHS
                       + RIGHTS_PROBE_PATHS + EVIDENCE_PROBE_PATHS)
MODULE_PROBES = ("livekit", "livekit.agents", "livekit.rtc", "audio_sdk")

# ---------------------------------------------------------------------------
# Canonical JSON and strict parsing.
# ---------------------------------------------------------------------------


class InvalidInput(ValueError):
    """Fail-closed rejection for malformed or unsupported input."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    payload = report if report is not None else build_report()
    text = canonical_text(payload) + "\n"
    return text, sha256_bytes(text.encode("ascii"))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise InvalidInput("non_finite_json:" + token)


def loads_strict(payload: str) -> dict:
    value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                       parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise InvalidInput("expected_json_object")
    return value


def read_strict_json(path: Path) -> dict:
    return loads_strict(path.read_text(encoding="utf-8"))


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise InvalidInput("float_value_not_permitted")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Board identity and profile provenance. The mutable full TASKS.json is never
# hashed; only the linked-row stable identity enters canonical bytes.
# ---------------------------------------------------------------------------


def _board_tasks(path: Path | None = None) -> list[dict]:
    target = path if path is not None else SOURCE_ROOT / BOARD_TASK_ROW
    if not target.is_file():
        raise InvalidInput("task_board_unavailable")
    document = read_strict_json(target)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise InvalidInput("task_board_tasks_missing")
    return [row for row in tasks if isinstance(row, dict)]


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = tuple(row for row in _board_tasks(path) if row.get("id") == TASK)
    if len(rows) != 1:
        raise InvalidInput("expected_exactly_one_linked_task_row")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    row = linked_rows(path)[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise InvalidInput("linked_task_row_identity_mismatch")
    if stable["repository"] != REPOSITORY or stable["mode"] != MODE:
        raise InvalidInput("linked_task_row_repository_or_mode_mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise InvalidInput("linked_task_row_claim_missing")
    expected = {
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
    }
    for key, value in expected.items():
        if claim.get(key) != value:
            raise InvalidInput("linked_task_row_claim_mismatch:" + key)
    return {
        "source": BOARD_TASK_ROW,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_FIELDS_EXCLUDED),
        "claim": expected,
    }


def task_row_identity() -> dict:
    projection = board_row_projection()
    projection["stable_fields"] = dict(projection["stable_fields"])
    projection["claim"] = dict(projection["claim"])
    return projection


def linked_row_identity() -> dict:
    identity = task_row_identity()
    return {
        "source": identity["source"],
        "stable_sha256": identity["stable_sha256"],
        "whole_file_hashed": False,
        "mutable_fields_never_gate": list(MUTABLE_FIELDS_EXCLUDED),
    }


def profile_source() -> dict:
    path = SOURCE_ROOT / PROFILE_SOURCE_REL
    if not path.is_file():
        raise InvalidInput("profile_source_missing")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Tool |")]
    if len(rows) != 1:
        raise InvalidInput("tool_profile_row_count")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise InvalidInput("tool_profile_phrase_missing:" + phrase)
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "row": row,
        "source": PROFILE_SOURCE_REL,
        "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
    }


def acceptance_matrix_evidence() -> dict:
    path = SOURCE_ROOT / ACCEPTANCE_SOURCE_REL
    if not path.is_file():
        raise InvalidInput("acceptance_matrix_missing")
    lines = path.read_text(encoding="utf-8").splitlines()
    s09 = [line for line in lines if line.startswith("| S09 LiveKit host |")]
    st11 = [line for line in lines if line.startswith("| S-T11 LiveKit |")]
    if len(s09) != 1 or len(st11) != 1:
        raise InvalidInput("acceptance_matrix_livekit_row_count")
    if "No pinned/tested LiveKit host package pair" not in s09[0]:
        raise InvalidInput("acceptance_matrix_s09_blocker_missing")
    if "S09 blocked" not in st11[0]:
        raise InvalidInput("acceptance_matrix_st11_blocker_missing")
    return {
        "path": ACCEPTANCE_SOURCE_REL,
        "sha256": SOURCE_PINS[ACCEPTANCE_SOURCE_REL],
        "s09_row": s09[0],
        "st11_row": st11[0],
        "recorded_blocker": "No pinned/tested LiveKit host package pair; no claim",
        "s09_state": "Blocked / excluded",
        "st11_state": "Excluded",
        "evidence_status": "recorded_absence_not_runtime_evidence",
    }


# ---------------------------------------------------------------------------
# Fixed absence, module and runtime audit.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: Iterable[str], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        present = ((SOURCE_ROOT / relative).exists()
                   or (WORKTREE / relative).exists())
        if present:
            raise InvalidInput("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    rows.extend(_workspace_rows(HOST_PROBE_PATHS, "host_package"))
    rows.extend(_workspace_rows(SDK_BUILD_PROBE_PATHS, "sdk_build"))
    rows.extend(_workspace_rows(RIGHTS_PROBE_PATHS, "rights"))
    rows.extend(_workspace_rows(EVIDENCE_PROBE_PATHS, "evidence"))
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows
                             if row.get("present") is not False),
        "all_probes_absent": all(row.get("present") is False for row in rows),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "home_cache_scanned": False,
        "network_used": False,
        "download_attempted": False,
        "package_install_attempted": False,
    }


def module_absence_probes() -> list[dict]:
    rows: list[dict] = []
    for name in MODULE_PROBES:
        try:
            spec = importlib.util.find_spec(name)
        except ModuleNotFoundError:
            spec = None
        if spec is not None:
            raise InvalidInput("module_present_reopen_required:" + name)
        rows.append({"module": name, "spec_present": False,
                     "imported_by_this_package": False})
    return rows


def module_absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows
                             if row.get("spec_present") is not False),
        "all_modules_absent": all(row.get("spec_present") is False
                                  for row in rows),
        "import_attempted_by_probe": False,
        "network_used": False,
    }


def host_probe() -> dict:
    probes = _workspace_rows(HOST_PROBE_PATHS, "host_package")
    return {
        "status": "blocked_pinned_host_package_pair_absent",
        "present": False,
        "host_package_pair_pinned": HOST_PACKAGE_PAIR_PINNED,
        "package_pair_pinned": HOST_PACKAGE_PAIR_PINNED,
        "host_package_imported": HOST_PACKAGE_IMPORTED,
        "host_lock_present": False,
        "host_wheel_or_sdist_present": False,
        "host_install_tree_present": False,
        "host_api_surface_verified": False,
        "host_geometry_status": HOST_GEOMETRY_STATUS,
        "host_license_status": HOST_LICENSE_STATUS,
        "required_host": (
            "One exact LiveKit Python host package pair at an immutable "
            "version with a recorded wheel/sdist platform artifact, "
            "per-file SHA-256, lock file, install tree, licence record and "
            "reviewed API surface for Python 3.12.16"),
        "candidates": probes,
    }


def sdk_build_probe() -> dict:
    probes = _workspace_rows(SDK_BUILD_PROBE_PATHS, "sdk_build")
    return {
        "status": "blocked_installed_sdk_binding_and_native_library_absent",
        "pinned_runtime_present": False,
        "installed_wheel_present": False,
        "native_library_present": False,
        "sdk_build_id_present": False,
        "audio_sdk_imported": False,
        "sdk_library_loaded": SDK_LIBRARY_LOADED,
        "environment_variable_audio_sdk_library_set":
            bool(os.environ.get("AUDIO_SDK_LIBRARY")),
        "required_sdk": (
            "The audio-sdk Python binding installed from an exact pinned "
            "commit with a matching native library, contract version 0.1 and "
            "a recorded build ID"),
        "candidates": probes,
    }


def rights_probe() -> dict:
    probes = _workspace_rows(RIGHTS_PROBE_PATHS, "rights")
    return {
        "status": "blocked_rights_cleared_host_audio_absent",
        "rights_cleared_audio_present": False,
        "participant_media_scope_present": False,
        "room_or_token_present": False,
        "real_audio_used": False,
        "redistribution_grant": False,
        "candidates": probes,
    }


def evidence_probe() -> dict:
    probes = _workspace_rows(EVIDENCE_PROBE_PATHS, "evidence")
    return {
        "status": "blocked_host_adapter_evidence_absent",
        "cohort_manifest_present": False,
        "geometry_record_present": False,
        "session_record_present": False,
        "matched_evidence_present": False,
        "candidates": probes,
    }


def runtime_probe() -> dict:
    version = ".".join(str(part) for part in sys.version_info[:3])
    return {
        "status": "pinned_python_present_host_packages_absent",
        "interpreter_version": version,
        "pinned_python_required": PINNED_PYTHON,
        "pinned_python_match": version == PINNED_PYTHON,
        "platform": sys.platform,
        "host_package_imported": HOST_PACKAGE_IMPORTED,
        "sdk_library_loaded": SDK_LIBRARY_LOADED,
        "network_used": False,
        "package_install_attempted": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied host-adapter contract. Validation hashes caller files but
# never imports or executes the host package, the SDK binding or audio.
# ---------------------------------------------------------------------------

CALLER_ASSET_FIELDS = (
    "audio_manifest_path",
    "audio_manifest_sha256",
    "channels_host",
    "channels_sdk",
    "frame_samples_host",
    "frame_samples_sdk",
    "host_install_path",
    "host_license_record_path",
    "host_license_record_sha256",
    "host_package_lock_path",
    "host_package_lock_sha256",
    "host_package_version",
    "host_shift_samples",
    "host_wheel_manifest_path",
    "host_wheel_manifest_sha256",
    "platform",
    "provider_delay_samples",
    "provider_id",
    "python_version",
    "rights_cleared_audio_acknowledged",
    "rights_record_path",
    "rights_record_sha256",
    "sample_format_host",
    "sample_rate_host_hz",
    "sample_rate_sdk_hz",
    "scope",
    "sdk_build_id",
    "sdk_contract_version",
    "sdk_library_path",
    "sdk_library_sha256",
    "variant",
)
CALLER_FILE_PAIRS = (
    ("audio_manifest_path", "audio_manifest_sha256"),
    ("host_license_record_path", "host_license_record_sha256"),
    ("host_package_lock_path", "host_package_lock_sha256"),
    ("host_wheel_manifest_path", "host_wheel_manifest_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("sdk_library_path", "sdk_library_sha256"),
)
CALLER_DIR_FIELDS = ("host_install_path",)
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
MIN_CHANNELS = 1
MAX_CHANNELS = 8
MAX_FRAME_SAMPLES = 192000 // 100
MAX_DELAY_SAMPLES = 16000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3
SDK_CONTRACT_VERSION = "0.1"
SDK_SAMPLE_RATE_HZ = 16000
SDK_CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SDK_FRAME_MS = 10
HOST_SHIFT_MS = 30
HOST_SHIFT_SAMPLES = 480
STARTUP_INVALID_FRAMES = 3
STARTUP_INVALID_SAMPLES = STARTUP_INVALID_FRAMES * SDK_FRAME_SAMPLES
WRONG_LENGTH_VECTORS = (159, 160, 161, 320, 480, 800)
REQUIRED_REJECTED_LENGTHS = (161, 320, 800)
PROVIDERS = (
    ("dsp.highpass80.v0", 0),
    ("speex.ns.v0", 160),
)

CALLER_ASSET_CONTRACT = {
    "contract_id": f"audio-sdk/{COMPONENT}/caller-supplied-host-adapter/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_host_version_python_version_platform_"
        "sdk_identity_provider_delay_scope_variant_10ms_geometry_and_integer_"
        "decimation_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_scope": CALLER_SCOPE,
    "required_python_version": PINNED_PYTHON,
    "required_sdk_contract_version": SDK_CONTRACT_VERSION,
    "required_sdk_geometry": {
        "sample_rate_hz": SDK_SAMPLE_RATE_HZ,
        "channels": SDK_CHANNELS,
        "sample_format": "f32",
        "frame_samples": SDK_FRAME_SAMPLES,
        "frame_ms": SDK_FRAME_MS,
    },
    "required_host_geometry": {
        "status": HOST_GEOMETRY_STATUS,
        "asserted": False,
        "sample_format": "s16",
        "frame_ms": SDK_FRAME_MS,
        "frame_samples": "sample_rate_host_hz // 100",
        "integer_decimation_required": True,
    },
    "required_host_shift_samples": HOST_SHIFT_SAMPLES,
    "required_host_shift_ms": HOST_SHIFT_MS,
    "required_rights_cleared_audio_acknowledged": True,
    "notes": (
        "A caller may validate a manifest only when the exact LiveKit host "
        "package pair, lock, wheel manifest, licence record, rights record, "
        "audio manifest, pinned Python 3.12.16, installed SDK library and "
        "recorded provider delay are all present at absolute paths and match "
        "their declared SHA-256. The package never imports, installs or "
        "executes the host package, the SDK binding or audio. No LiveKit "
        "version or API surface is pinned because none is present."),
}

CALLER_ASSET_REQUIREMENTS = (
    {
        "id": "pinned_livekit_host_package_pair",
        "required": True,
        "status": "absent",
        "revision": None,
        "note": (
            "No LiveKit host package version, wheel, sdist, lock file, "
            "install tree or per-file SHA-256 is present."),
    },
    {
        "id": "installed_sdk_python_binding",
        "required": True,
        "status": "absent",
        "sha256": None,
        "note": (
            "No installed audio-sdk Python wheel or native library with a "
            "recorded build ID exists at the pinned base in this worktree."),
    },
    {
        "id": "host_api_and_geometry_record",
        "required": True,
        "status": "absent",
        "note": (
            "No pinned LiveKit API record establishes frame size, sample "
            "rate, channel count, sample format, pacing, reset or close "
            "behaviour."),
    },
    {
        "id": "rights_cleared_host_audio",
        "required": True,
        "status": "absent",
        "note": (
            "No rights-cleared participant media, room/token scope, audio "
            "cohort or output-use grant is present."),
    },
    {
        "id": "host_adapter_evidence",
        "required": True,
        "status": "absent",
        "note": (
            "No pinned 10 ms pacing run, conversion record, cancellation "
            "record, drain record or matched host evidence exists."),
    },
    {
        "id": "tool_acceptance_evidence",
        "required": True,
        "status": "absent",
        "note": (
            "No clean host checkout, typical CLI/API use, caller-owned input "
            "run or measured workload support exists."),
    },
    {
        "id": "independent_review",
        "required": True,
        "status": "absent",
        "note": "No independent exact-head review is recorded.",
    },
)

# ---------------------------------------------------------------------------
# Tool acceptance profile. Every item remains blocked, partial or not measured.
# ---------------------------------------------------------------------------

TOOL_REQUIREMENTS = (
    ("version_install_location_provenance",
     "Record the host package version, install location and provenance.",
     "blocked"),
    ("clean_checkout_or_extracted_package",
     "Verify a clean checkout or extracted host package.",
     "blocked"),
    ("typical_cli_or_api_use",
     "Verify one typical host CLI or API use.",
     "not_measured"),
    ("caller_owned_inputs",
     "Verify caller-owned inputs without bundling them.",
     "blocked"),
    ("malformed_inputs",
     "Verify malformed input rejection.",
     "partial_synthetic"),
    ("missing_optional_selections",
     "Verify missing optional selections fail closed.",
     "partial_synthetic"),
    ("build_synthetic_measured_separation",
     "Separate compile/build, synthetic runtime and measured workload "
     "evidence.",
     "separated_in_package_only"),
    ("measured_workload_support",
     "Record measured workload support for the exact host runtime.",
     "blocked"),
)

# ---------------------------------------------------------------------------
# Structural host geometry control. This is integer accounting and s16
# validation at a labelled common WebRTC geometry, not a LiveKit measurement.
# ---------------------------------------------------------------------------

CONTROL_HOST_SAMPLE_RATE_HZ = 48000
CONTROL_HOST_CHANNELS = 1
CONTROL_HOST_SAMPLE_FORMAT = "s16"
CONTROL_HOST_FRAME_SAMPLES = CONTROL_HOST_SAMPLE_RATE_HZ // 100
CONTROL_HOST_FRAME_MS = 10
CONTROL_DECIMATION = CONTROL_HOST_SAMPLE_RATE_HZ // SDK_SAMPLE_RATE_HZ
CONTROL_SDK_FRAME_SAMPLES = CONTROL_HOST_FRAME_SAMPLES // CONTROL_DECIMATION
CONTROL_PLAN_PROVENANCE = (
    "structural_48k_to_16k_10ms_control_not_livekit_execution")
CONTROL_FRAMES = (1, 3, 30, 100, 600)
PCM_SAMPLE_CAP = 10_000_000


def validate_s16_frame(samples: Any,
                       expected: int = CONTROL_HOST_FRAME_SAMPLES) -> list[int]:
    if not isinstance(samples, (list, tuple)):
        raise InvalidInput("host_frame_must_be_a_sample_sequence")
    if not samples:
        raise InvalidInput("host_frame_must_be_nonempty")
    if len(samples) != expected:
        raise InvalidInput("host_frame_length_must_be_" + str(expected))
    if len(samples) > PCM_SAMPLE_CAP:
        raise InvalidInput("host_frame_exceeds_evidence_cap")
    checked: list[int] = []
    for index, sample in enumerate(samples):
        if type(sample) is not int:
            raise InvalidInput(f"sample_{index}_is_not_an_integer")
        if sample < -32768 or sample > 32767:
            raise InvalidInput(f"sample_{index}_is_outside_s16_range")
        checked.append(sample)
    return checked


def synthetic_host_frame() -> list[int]:
    return [((index * 37 + 11) % 65536) - 32768
            for index in range(CONTROL_HOST_FRAME_SAMPLES)]


def convert_host_frame(samples: Any) -> list[float]:
    """Structural integer decimation followed by s16 -> f32 scaling."""
    checked = validate_s16_frame(samples)
    converted = [float(value) / 32768.0
                 for value in checked[::CONTROL_DECIMATION]]
    if len(converted) != SDK_FRAME_SAMPLES:
        raise InvalidInput("decimation_did_not_produce_160_samples")
    if any(not math.isfinite(value) for value in converted):
        raise InvalidInput("nonfinite_conversion_output")
    return converted


def packing_accounting(host_frames: int) -> dict:
    if type(host_frames) is not int or host_frames <= 0:
        raise InvalidInput("host_frames_must_be_a_positive_integer")
    host_samples = host_frames * CONTROL_HOST_FRAME_SAMPLES
    sdk_samples = host_frames * CONTROL_SDK_FRAME_SAMPLES
    return {
        "host_frames": host_frames,
        "host_samples": host_samples,
        "sdk_samples": sdk_samples,
        "host_duration_ms": host_frames * CONTROL_HOST_FRAME_MS,
        "sdk_frame_count": host_frames,
        "exact": (host_samples % CONTROL_DECIMATION == 0
                  and sdk_samples == host_frames * SDK_FRAME_SAMPLES),
    }


def shift_model(provider_id: str) -> dict:
    delays = {name: delay for name, delay in PROVIDERS}
    if provider_id not in delays:
        raise InvalidInput("unknown_provider")
    delay = delays[provider_id]
    total = HOST_SHIFT_SAMPLES + delay + STARTUP_INVALID_SAMPLES
    return {
        "provider_id": provider_id,
        "host_shift_samples": HOST_SHIFT_SAMPLES,
        "host_shift_ms": HOST_SHIFT_MS,
        "provider_delay_samples": delay,
        "startup_invalid_frames": STARTUP_INVALID_FRAMES,
        "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
        "modeled_invalid_prefix_samples": total,
        "modeled_invalid_prefix_ms": fraction_text(
            Fraction(total, SDK_SAMPLE_RATE_HZ) * 1000),
        "source_order_policy": "preserve",
        "measured": False,
        "qualification_effect": "none",
    }


def wrong_length_decision(length: int) -> dict:
    if type(length) is not int or length < 0:
        raise InvalidInput("frame_length_must_be_a_nonnegative_integer")
    accepted = length == SDK_FRAME_SAMPLES
    return {
        "length": length,
        "accepted": accepted,
        "reason": "exactly_160_sdk_samples" if accepted else
                  "wrong_sdk_frame_length",
    }


def validate_sdk_frame_length(samples: Any) -> int:
    if not isinstance(samples, (list, tuple)):
        raise InvalidInput("sdk_frame_must_be_a_sample_sequence")
    if len(samples) != SDK_FRAME_SAMPLES:
        raise InvalidInput("wrong_sdk_frame_length")
    return len(samples)


def run_adverse_controls() -> list[dict]:
    good_manifest = _shape_only_manifest()
    existing = _existing_file_manifest()

    def case(case_id: str, action) -> dict:
        try:
            action()
        except InvalidInput as error:
            return {"case": case_id, "result": "rejected",
                    "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case": case_id, "result": "unexpected_error",
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {key2: value for key2, value in good_manifest.items()
                    if key2 != key}
        return lambda: validate_caller_manifest(manifest)

    cases = [
        ("host_frame_not_sequence", lambda: validate_s16_frame(b"\x00\x00")),
        ("host_frame_empty", lambda: validate_s16_frame([])),
        ("host_frame_none", lambda: validate_s16_frame(None)),
        ("host_frame_bool_sample",
         lambda: validate_s16_frame([0] * 479 + [True])),
        ("host_frame_float_sample",
         lambda: validate_s16_frame([0] * 479 + [0.5])),
        ("host_frame_above_s16",
         lambda: validate_s16_frame([0] * 479 + [32768])),
        ("host_frame_below_s16",
         lambda: validate_s16_frame([0] * 479 + [-32769])),
        ("host_frame_wrong_length",
         lambda: validate_s16_frame([0] * 161)),
        ("sdk_length_161_rejected",
         lambda: validate_sdk_frame_length([0] * 161)),
        ("wrong_length_320_rejected",
         lambda: validate_sdk_frame_length([0] * 320)),
        ("wrong_length_800_rejected",
         lambda: validate_sdk_frame_length([0] * 800)),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("sdk_library_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_duplicate_key",
         lambda: loads_strict('{"a":1,"a":2}')),
        ("manifest_relative_path", wrong(
            "sdk_library_path", "libaudio_sdk.dylib")),
        ("manifest_bad_sha", wrong("sdk_library_sha256", "ABC")),
        ("manifest_wrong_scope", wrong("scope", "voice_conversion")),
        ("manifest_wrong_variant", wrong("variant", "offline_whole_clip")),
        ("manifest_python_version", wrong("python_version", "3.11.5")),
        ("manifest_host_version", wrong("host_package_version", "")),
        ("manifest_bad_platform", wrong("platform", "Mac OS X")),
        ("manifest_host_channels_zero", wrong("channels_host", 0)),
        ("manifest_host_channels_bool", wrong("channels_host", True)),
        ("manifest_host_rate_range", wrong(
            "sample_rate_host_hz", 4000)),
        ("manifest_frame_not_10ms", wrong("frame_samples_host", 441)),
        ("manifest_non_integer_decimation", wrong(
            "sample_rate_host_hz", 44100)),
        ("manifest_sdk_rate", wrong("sample_rate_sdk_hz", 48000)),
        ("manifest_sdk_channels", wrong("channels_sdk", 2)),
        ("manifest_sdk_frame", wrong("frame_samples_sdk", 480)),
        ("manifest_host_shift", wrong("host_shift_samples", 160)),
        ("manifest_provider_unknown", wrong(
            "provider_id", "unknown.provider.v0")),
        ("manifest_delay_mismatch", wrong(
            "provider_delay_samples", 160)),
        ("manifest_sdk_contract", wrong("sdk_contract_version", "0.2")),
        ("manifest_sdk_build_empty", wrong("sdk_build_id", "")),
        ("manifest_rights_not_acknowledged", wrong(
            "rights_cleared_audio_acknowledged", False)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, sdk_library_path=(
                "/nonexistent/livekit-host-fixtures/libaudio_sdk.dylib")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, host_install_path=(
                "/nonexistent/livekit-host-fixtures/no-install")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, sdk_library_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise InvalidInput("adverse_case_count_mismatch")
    return results


ADVERSE_CASE_IDS = (
    "host_frame_not_sequence",
    "host_frame_empty",
    "host_frame_none",
    "host_frame_bool_sample",
    "host_frame_float_sample",
    "host_frame_above_s16",
    "host_frame_below_s16",
    "host_frame_wrong_length",
    "sdk_length_161_rejected",
    "wrong_length_320_rejected",
    "wrong_length_800_rejected",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_duplicate_key",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_wrong_scope",
    "manifest_wrong_variant",
    "manifest_python_version",
    "manifest_host_version",
    "manifest_bad_platform",
    "manifest_host_channels_zero",
    "manifest_host_channels_bool",
    "manifest_host_rate_range",
    "manifest_frame_not_10ms",
    "manifest_non_integer_decimation",
    "manifest_sdk_rate",
    "manifest_sdk_channels",
    "manifest_sdk_frame",
    "manifest_host_shift",
    "manifest_provider_unknown",
    "manifest_delay_mismatch",
    "manifest_sdk_contract",
    "manifest_sdk_build_empty",
    "manifest_rights_not_acknowledged",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)


def _shape_only_manifest() -> dict:
    root = "/nonexistent/livekit-host-adapter-evidence-fixture"
    digest = "0" * 64
    return {
        "audio_manifest_path": root + "/audio.json",
        "audio_manifest_sha256": digest,
        "channels_host": CONTROL_HOST_CHANNELS,
        "channels_sdk": SDK_CHANNELS,
        "frame_samples_host": CONTROL_HOST_FRAME_SAMPLES,
        "frame_samples_sdk": SDK_FRAME_SAMPLES,
        "host_install_path": root + "/install",
        "host_license_record_path": root + "/host-license.json",
        "host_license_record_sha256": digest,
        "host_package_lock_path": root + "/host.lock",
        "host_package_lock_sha256": digest,
        "host_package_version": "0.0.0",
        "host_shift_samples": HOST_SHIFT_SAMPLES,
        "host_wheel_manifest_path": root + "/wheels.json",
        "host_wheel_manifest_sha256": digest,
        "platform": "macos_arm64",
        "provider_delay_samples": 0,
        "provider_id": "dsp.highpass80.v0",
        "python_version": PINNED_PYTHON,
        "rights_cleared_audio_acknowledged": True,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "sample_format_host": CONTROL_HOST_SAMPLE_FORMAT,
        "sample_rate_host_hz": CONTROL_HOST_SAMPLE_RATE_HZ,
        "sample_rate_sdk_hz": SDK_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "sdk_build_id": "synthetic-structure-only-build",
        "sdk_contract_version": SDK_CONTRACT_VERSION,
        "sdk_library_path": root + "/libaudio_sdk.dylib",
        "sdk_library_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> dict:
    assignments = {
        "audio_manifest_path": HERE / "LICENSES.md",
        "host_license_record_path": HERE / "LICENSES.md",
        "host_package_lock_path": HERE / "SOURCES.sha256.license",
        "host_wheel_manifest_path": HERE / "contract.json.license",
        "rights_record_path": HERE / "LICENSES.md",
        "sdk_library_path": HERE / "reference.py",
    }
    manifest: dict[str, Any] = {
        "channels_host": CONTROL_HOST_CHANNELS,
        "channels_sdk": SDK_CHANNELS,
        "frame_samples_host": CONTROL_HOST_FRAME_SAMPLES,
        "frame_samples_sdk": SDK_FRAME_SAMPLES,
        "host_install_path": str(HERE),
        "host_package_version": "0.0.0",
        "host_shift_samples": HOST_SHIFT_SAMPLES,
        "platform": "macos_arm64",
        "provider_delay_samples": 0,
        "provider_id": "dsp.highpass80.v0",
        "python_version": PINNED_PYTHON,
        "rights_cleared_audio_acknowledged": True,
        "sample_format_host": CONTROL_HOST_SAMPLE_FORMAT,
        "sample_rate_host_hz": CONTROL_HOST_SAMPLE_RATE_HZ,
        "sample_rate_sdk_hz": SDK_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "sdk_build_id": "synthetic-structure-only-build",
        "sdk_contract_version": SDK_CONTRACT_VERSION,
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256_file(path)
    return manifest


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_MANIFEST_BYTES:
                raise InvalidInput("asset_exceeds_evidence_cap")
            digest.update(chunk)
    return digest.hexdigest()


def _bounded_int(manifest: dict, field: str, low: int, high: int) -> int:
    value = manifest[field]
    if type(value) is not int:
        raise InvalidInput("manifest_" + field + "_must_be_an_integer")
    if value < low or value > high:
        raise InvalidInput("manifest_" + field + "_outside_admitted_range")
    return value


def _path_field(manifest: dict, field: str) -> Path:
    value = manifest[field]
    if not isinstance(value, str) or not value:
        raise InvalidInput("manifest_" + field + "_must_be_a_path_string")
    path = Path(value)
    if not path.is_absolute():
        raise InvalidInput("manifest_" + field + "_must_be_absolute")
    return path


def validate_caller_manifest(manifest: Any) -> dict:
    if not isinstance(manifest, dict):
        raise InvalidInput("manifest_must_be_an_object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise InvalidInput("manifest_missing_fields:" + ",".join(missing))
    if extra:
        raise InvalidInput("manifest_has_unknown_fields:" + ",".join(extra))
    for _, sha_field in CALLER_FILE_PAIRS:
        value = manifest[sha_field]
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise InvalidInput(
                "manifest_" + sha_field + "_is_not_a_lowercase_sha256")
    for path_field, _ in CALLER_FILE_PAIRS:
        _path_field(manifest, path_field)
    for field in CALLER_DIR_FIELDS:
        _path_field(manifest, field)
    version = manifest["host_package_version"]
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise InvalidInput("manifest_host_package_version_is_invalid")
    python_version = manifest["python_version"]
    if (not isinstance(python_version, str)
            or not PYTHON_VERSION.fullmatch(python_version)):
        raise InvalidInput("manifest_python_version_is_invalid")
    if python_version != PINNED_PYTHON:
        raise InvalidInput("manifest_python_version_must_be_" + PINNED_PYTHON)
    platform = manifest["platform"]
    if not isinstance(platform, str) or not PLATFORM.fullmatch(platform):
        raise InvalidInput("manifest_platform_is_invalid")
    scope = manifest["scope"]
    if not isinstance(scope, str) or not SCOPE_TOKEN.fullmatch(scope):
        raise InvalidInput("manifest_scope_is_invalid")
    if scope != CALLER_SCOPE:
        raise InvalidInput("manifest_scope_must_be_" + CALLER_SCOPE)
    if manifest["variant"] != CALLER_VARIANT:
        raise InvalidInput("manifest_variant_must_be_" + CALLER_VARIANT)
    if manifest["rights_cleared_audio_acknowledged"] is not True:
        raise InvalidInput("manifest_rights_cleared_audio_not_acknowledged")
    if manifest["sample_format_host"] != CONTROL_HOST_SAMPLE_FORMAT:
        raise InvalidInput("manifest_sample_format_host_must_be_s16")
    if manifest["sdk_contract_version"] != SDK_CONTRACT_VERSION:
        raise InvalidInput(
            "manifest_sdk_contract_version_must_be_" + SDK_CONTRACT_VERSION)
    build_id = manifest["sdk_build_id"]
    if not isinstance(build_id, str) or not BUILD_ID.fullmatch(build_id):
        raise InvalidInput("manifest_sdk_build_id_is_invalid")
    channels_host = _bounded_int(manifest, "channels_host",
                                 MIN_CHANNELS, MAX_CHANNELS)
    channels_sdk = _bounded_int(manifest, "channels_sdk",
                                SDK_CHANNELS, SDK_CHANNELS)
    sample_host = _bounded_int(manifest, "sample_rate_host_hz",
                               MIN_SAMPLE_RATE_HZ, MAX_SAMPLE_RATE_HZ)
    sample_sdk = _bounded_int(manifest, "sample_rate_sdk_hz",
                              SDK_SAMPLE_RATE_HZ, SDK_SAMPLE_RATE_HZ)
    frame_host = _bounded_int(manifest, "frame_samples_host",
                              1, MAX_FRAME_SAMPLES)
    frame_sdk = _bounded_int(manifest, "frame_samples_sdk",
                             SDK_FRAME_SAMPLES, SDK_FRAME_SAMPLES)
    shift = _bounded_int(manifest, "host_shift_samples",
                         HOST_SHIFT_SAMPLES, HOST_SHIFT_SAMPLES)
    delay = _bounded_int(manifest, "provider_delay_samples",
                         0, MAX_DELAY_SAMPLES)
    if sample_host % 100 != 0:
        raise InvalidInput("manifest_host_rate_not_divisible_by_100")
    if frame_host != sample_host // 100:
        raise InvalidInput("manifest_host_frame_is_not_10_ms")
    if sample_host % SDK_SAMPLE_RATE_HZ != 0:
        raise InvalidInput("manifest_host_rate_not_integer_decimation")
    if sample_host // SDK_SAMPLE_RATE_HZ > 12:
        raise InvalidInput("manifest_host_rate_decimation_too_large")
    if channels_sdk != SDK_CHANNELS:
        raise InvalidInput("manifest_sdk_channels_must_be_one")
    if frame_sdk != SDK_FRAME_SAMPLES:
        raise InvalidInput("manifest_sdk_frame_must_be_160")
    if shift != HOST_SHIFT_SAMPLES:
        raise InvalidInput("manifest_host_shift_must_be_480")
    provider = manifest["provider_id"]
    delays = {name: value for name, value in PROVIDERS}
    if not isinstance(provider, str) or provider not in delays:
        raise InvalidInput("manifest_provider_id_is_invalid")
    if delay != delays[provider]:
        raise InvalidInput("manifest_provider_delay_does_not_match_provider")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise InvalidInput("manifest_" + field + "_directory_is_missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise InvalidInput("manifest_" + path_field + "_file_is_missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise InvalidInput("manifest_" + path_field + "_sha256_mismatch")
        total_bytes += path.stat().st_size
    decimation = sample_host // SDK_SAMPLE_RATE_HZ
    return {
        "accepted": True,
        "host_package_version": version,
        "python_version": python_version,
        "platform": platform,
        "variant": CALLER_VARIANT,
        "scope": CALLER_SCOPE,
        "provider_id": provider,
        "provider_delay_samples": delay,
        "sample_rate_host_hz": sample_host,
        "channels_host": channels_host,
        "frame_samples_host": frame_host,
        "frame_ms": frame_host * 1000 // sample_host,
        "sample_rate_sdk_hz": sample_sdk,
        "channels_sdk": channels_sdk,
        "frame_samples_sdk": frame_sdk,
        "host_shift_samples": shift,
        "integer_decimation": decimation,
        "sdk_build_id": build_id,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "host_package_imported": False,
        "sdk_library_loaded": False,
        "audio_read": False,
    }


def build_control() -> dict:
    frame = synthetic_host_frame()
    converted = convert_host_frame(frame)
    packing = [packing_accounting(count) for count in CONTROL_FRAMES]
    shifts = [shift_model(name) for name, _ in PROVIDERS]
    lengths = [wrong_length_decision(length)
               for length in WRONG_LENGTH_VECTORS]
    rejected = [row["length"] for row in lengths if not row["accepted"]]
    adverse = run_adverse_controls()
    positive = validate_caller_manifest(_existing_file_manifest())
    return {
        "host_package_loaded": False,
        "sdk_library_loaded": False,
        "real_audio_used": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_host_sample_rate_hz": CONTROL_HOST_SAMPLE_RATE_HZ,
            "control_host_channels": CONTROL_HOST_CHANNELS,
            "control_host_sample_format": CONTROL_HOST_SAMPLE_FORMAT,
            "control_host_frame_samples": CONTROL_HOST_FRAME_SAMPLES,
            "control_host_frame_ms": CONTROL_HOST_FRAME_MS,
            "control_integer_decimation": CONTROL_DECIMATION,
            "control_sdk_sample_rate_hz": SDK_SAMPLE_RATE_HZ,
            "control_sdk_channels": SDK_CHANNELS,
            "control_sdk_frame_samples": SDK_FRAME_SAMPLES,
            "control_frame_ms": SDK_FRAME_MS,
            "livekit_geometry_status": HOST_GEOMETRY_STATUS,
            "livekit_geometry_asserted": False,
            "livekit_execution": False,
            "task_scope": TASK_SCOPE,
            "task_kind": TASK_KIND,
        },
        "conversion": {
            "host_input_samples": len(frame),
            "sdk_output_samples": len(converted),
            "decimation": CONTROL_DECIMATION,
            "scale_denominator": 32768,
            "nonfinite_output_count": sum(
                1 for value in converted if not math.isfinite(value)),
            "host_numerator_sha256": sha256_bytes(canonical_bytes(frame)),
            "sdk_numerator_sha256": sha256_bytes(
                canonical_bytes(frame[::CONTROL_DECIMATION])),
            "float_values_retained_in_report": False,
            "measured": False,
            "qualification_effect": "none",
        },
        "packing": packing,
        "shift_models": shifts,
        "wrong_lengths": lengths,
        "required_rejected_lengths": list(REQUIRED_REJECTED_LENGTHS),
        "required_rejected_lengths_all_rejected":
            all(length in rejected for length in REQUIRED_REJECTED_LENGTHS),
        "accepted_control": {
            "id": "synthetic_structure_only_manifest",
            "accepted": positive["accepted"],
            "host_package_version": positive["host_package_version"],
            "python_version": positive["python_version"],
            "platform": positive["platform"],
            "scope": positive["scope"],
            "variant": positive["variant"],
            "provider_id": positive["provider_id"],
            "integer_decimation": positive["integer_decimation"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "host_package_imported": positive["host_package_imported"],
            "sdk_library_loaded": positive["sdk_library_loaded"],
            "audio_read": positive["audio_read"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a LiveKit install, "
                "not an SDK wheel and not a rights-cleared audio set."),
        },
        "policy_checks": [
            {"id": "source_order", "policy": "preserve",
             "verified": False},
            {"id": "host_shift_plus_provider_delay",
             "policy": "explicit_30_ms_host_shift_plus_D", "verified": False},
            {"id": "startup_invalid", "policy": "first_three_sdk_frames",
             "verified": False},
            {"id": "wrong_lengths", "policy": "reject_161_320_800",
             "verified": False},
            {"id": "finite_conversion", "policy": "reject_nonfinite",
             "verified": False},
            {"id": "event_loop", "policy": "no_wait_for_inference",
             "verified": False},
            {"id": "missed_output_or_admission", "policy": "stop",
             "verified": False},
            {"id": "stale_epoch", "policy": "no_old_epoch_output",
             "verified": False},
            {"id": "abrupt_close", "policy": "record_cancelled_tail",
             "verified": False},
            {"id": "managed_close", "policy": "bounded_drain_then_close",
             "verified": False},
        ],
        "acceptance_outcomes": [
            {"id": "typical_api_use", "measured": False, "value": None,
             "reason": "no host package, room or participant"},
            {"id": "conversion_contract", "measured": False, "value": None,
             "reason": "structural integer decimation only"},
            {"id": "capture_contract", "measured": False, "value": None,
             "reason": "no audio capture and no rights-cleared media"},
            {"id": "pacing", "measured": False, "value": None,
             "reason": "no 10 ms host clock or device run"},
            {"id": "cancellation", "measured": False, "value": None,
             "reason": "no pending inference or live session"},
            {"id": "safe_termination", "measured": False, "value": None,
             "reason": "policy table only; no host session"},
            {"id": "measured_workload", "measured": False, "value": None,
             "reason": "no workload, resource or deadline measurement"},
        ],
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Structural s16 validation and integer 48 kHz -> 16 kHz "
            "decimation accounting only, plus a fail-closed caller manifest. "
            "It is not LiveKit execution, not a host capture, not resampling "
            "quality, not a pacing or device result and not a release claim."),
    }


# ---------------------------------------------------------------------------
# Gates, blockers and artifacts.
# ---------------------------------------------------------------------------

GATE_REQUIREMENTS = (
    ("RG-01", "pinned_livekit_host_package_pair",
     "One exact LiveKit Python host package pair is pinned by immutable "
     "version, wheel/sdist platform artifact, per-file SHA-256, lock file and "
     "install tree."),
    ("RG-02", "installed_sdk_python_binding",
     "The audio-sdk Python binding and matching native library are built and "
     "installed from an exact SDK commit with contract 0.1 and a recorded "
     "build ID."),
    ("RG-03", "rights_cleared_audio_and_participant_scope",
     "Rights-cleared participant media, room/token scope, output-use and "
     "redistribution terms are recorded without bundling audio."),
    ("RG-04", "host_api_and_geometry_lock",
     "A pinned LiveKit API record fixes frame size, sample rate, channel "
     "count, sample format, pacing, reset and close behaviour."),
    ("RG-05", "conversion_and_capture_contract",
     "One typical host API use verifies s16-to-f32 conversion, exact "
     "resampling/rechunking, source order and the explicit 30 ms host shift "
     "plus provider delay D."),
    ("RG-06", "lifecycle_cancellation_and_safe_termination",
     "Participant reset, cancellation with pending work, expected output "
     "unavailable, queue full, malformed format, stale epoch, abrupt close "
     "and managed drain/close are tested on the pinned host."),
    ("RG-07", "tool_acceptance_profile_and_matched_evidence",
     "The Tool profile is satisfied with version, install location, clean "
     "package, caller-owned inputs, malformed inputs, missing selections and "
     "measured workload support, keeping build, synthetic and measured "
     "evidence separate."),
    ("RG-08", "independent_review_and_release",
     "Independent exact-head review, explicit default decision and release "
     "or public-benchmark approval are recorded; this package is off by "
     "default."),
)

EXACT_BLOCKERS = (
    ("BLK-01", "RG-01", "pinned_host_package_pair_absent",
     "Supply one exact LiveKit Python host package pair with immutable "
     "version, wheel/sdist platform artifact, per-file SHA-256, lock file and "
     "install tree; no host package, lock or wheel is present and package "
     "install/download is prohibited in this task."),
    ("BLK-02", "RG-02", "installed_sdk_binding_absent",
     "Build and install the audio-sdk Python binding with its matching native "
     "library from an exact commit and record contract 0.1 plus the build ID; "
     "no build, wheel or installed binding exists at the pinned base in this "
     "worktree."),
    ("BLK-03", "RG-03", "rights_cleared_audio_absent",
     "Provide rights-cleared participant media, room/token scope, output-use "
     "and redistribution terms; real audio is prohibited in this task and no "
     "rights record or media is present."),
    ("BLK-04", "RG-04", "host_api_and_geometry_unverified",
     "Pin the LiveKit API record and establish frame size, sample rate, "
     "channel count, sample format, pacing, reset and close behaviour; no host "
     "API or geometry is verified here."),
    ("BLK-05", "RG-05", "conversion_and_capture_unverified",
     "Run one typical host API use with exact conversion/rechunking and "
     "source-order accounting; only structural integer arithmetic exists."),
    ("BLK-06", "RG-06", "lifecycle_and_termination_unverified",
     "Exercise participant reset, cancellation with pending work, missing "
     "output, queue full, malformed format, stale epoch, abrupt close and "
     "managed drain/close on the pinned host; none is executed."),
    ("BLK-07", "RG-07", "tool_profile_and_measured_workload_absent",
     "Complete the Tool profile with a clean package, typical use, "
     "caller-owned inputs and measured workload support; no measured result "
     "exists and the package is synthetic-only."),
    ("BLK-08", "RG-08", "review_default_and_release_absent",
     "Complete independent exact-head review, default selection and release "
     "or public-benchmark approval; none is present and this package is off "
     "by default."),
)

REQUIRED_ARTIFACTS = (
    ("ART-01", "pinned_host_package_pair",
     "The exact LiveKit Python host package pair, immutable versions, "
     "wheel/sdist artifacts, lock file, install tree and per-file SHA-256."),
    ("ART-02", "installed_sdk_binding",
     "The installed audio-sdk Python binding, matching native library, "
     "contract 0.1 and exact build ID."),
    ("ART-03", "rights_record_and_audio",
     "Rights-cleared participant media and room/token scope with output-use "
     "and redistribution terms, stored outside the package."),
    ("ART-04", "host_api_and_geometry_record",
     "The pinned LiveKit API and geometry record including pacing, reset and "
     "close semantics."),
    ("ART-05", "conversion_and_capture_record",
     "A conversion/rechunking and capture record with exact source order, "
     "host shift, provider delay and frame counts."),
    ("ART-06", "lifecycle_and_termination_record",
     "Reset, cancellation, missing-output, queue-full, malformed, stale "
     "epoch, abrupt-close and managed drain/close records."),
    ("ART-07", "tool_acceptance_and_workload",
     "Clean-package, typical-use, caller-owned input, malformed input, "
     "missing-selection and measured workload evidence."),
    ("ART-08", "review_and_release",
     "Independent exact-head review, default decision and release or "
     "public-benchmark approval."),
)

DISPOSITION = {
    "decision": DECISION,
    "status": "incomplete",
    "qualification_status": QUALIFICATION_STATUS,
    "proposal_only": True,
    "incomplete": True,
    "not_qualified": True,
    "missing_result_qualifies": False,
    "default_enabled": False,
    "registered": False,
    "expose_as_host_adapter": False,
    "production_exposure": "DEFER",
    "promotion": "defer",
    "defer_before": DEFER_BEFORE,
}

SCOPE = {
    "task_local_only": True,
    "host_package_installed": False,
    "host_package_imported": False,
    "host_package_executed": False,
    "sdk_library_loaded": False,
    "sdk_callback_invoked": False,
    "real_audio": False,
    "real_corpus": False,
    "real_speech": False,
    "network_used": False,
    "download_attempted": False,
    "package_install_attempted": False,
    "audio_read": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "benchmark_claim": False,
    "latency_claim": False,
    "release_claim": False,
}

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_build_or_ci_change": False,
    "installed_v0_behavior_change": False,
    "adapter_json_added": False,
    "provider_json_added": False,
    "network_used": False,
    "host_package_vendored": False,
    "wheel_committed": False,
    "audio_committed": False,
    "descriptor_settings": {},
}

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": SDK_SAMPLE_RATE_HZ,
    "channels": SDK_CHANNELS,
    "sample_format": "f32",
    "frame_samples": SDK_FRAME_SAMPLES,
    "frame_ms": SDK_FRAME_MS,
    "unchanged": True,
}

NON_CLAIMS = (
    "No LiveKit host package, wheel, sdist, lock file or install tree is "
    "installed, downloaded, imported, executed or vendored.",
    "No audio-sdk native library or installed Python binding is loaded or "
    "invoked.",
    "No room, token, participant, track, device, capture or real audio is "
    "used.",
    "No network request, package index access, download or install occurs.",
    "No LiveKit API, frame geometry, sample rate, channel count, sample "
    "format or pacing is verified.",
    "The conversion control is structural integer decimation at a labelled "
    "48 kHz -> 16 kHz geometry; it is not resampling quality or host output.",
    "No cancellation, drain, close, device timing, latency, memory, RTF or "
    "deadline result is measured.",
    "No listening, public benchmark, quality score or release result is "
    "claimed.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "Missing evidence never qualifies the candidate; the decision remains "
    "DEFER and the qualification remains not_qualified.",
)

RIGHTS_GAP = {
    "status": "blocked",
    "rights_cleared_audio_present": False,
    "participant_media_scope_present": False,
    "room_or_token_present": False,
    "output_use_grant": False,
    "redistribution_grant": False,
    "attribution_terms": None,
    "host_license_record_present": False,
    "note": (
        "The pinned acceptance matrix records that the LiveKit host row is "
        "blocked/excluded for want of a pinned/tested host package pair. No "
        "rights record, participant scope, room/token, media or output-use "
        "grant is present. The blocker is provenance/install/geometry/rights, "
        "not a recorded commercial licence conclusion."),
}


# ---------------------------------------------------------------------------
# Merge-base scope helpers (used by verify.py and the regression tests).
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
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
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
# README digest tables. Every digest is machine-checked.
# ---------------------------------------------------------------------------

README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})


def local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  (source:[A-Za-z0-9_./-]+|"
    r"sdk:[A-Za-z0-9_./-]+|" + re.escape(TASK_PREFIX) +
    r"[A-Za-z0-9_./-]+)$")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = match.groups()
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS}
            | {"sdk:" + name for name in BOUNDARY_PINS}
            | {TASK_PREFIX + name for name in local_manifest_paths()})


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in local_manifest_paths()
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
            if not HEX64.fullmatch(digest):
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
                path = SOURCE_ROOT / relative
            elif section == "boundary":
                relative = key[len("sdk:"):]
                expected_digest = BOUNDARY_PINS[relative]
                path = WORKTREE / relative
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file():
                raise ValueError("readme_pin_target_missing:" + key)
            if sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start_marker, end_marker = README_MARKERS["artifacts"]
    start = text.index(start_marker)
    end = text.index(end_marker, start) + len(end_marker)
    return text[:start] + block + text[end:]


# ---------------------------------------------------------------------------
# Report and contract.
# ---------------------------------------------------------------------------


def _tool_profile_block() -> dict:
    items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in TOOL_REQUIREMENTS
    ]
    return {
        "name": PROFILE,
        "key": PROFILE_KEY,
        "source": PROFILE_SOURCE_REL,
        "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
        "required_items": items,
        "satisfied_for_qualification": [],
        "unsatisfied_for_qualification": [item["id"] for item in items],
        "measured_workload_result": None,
        "note": (
            "The fail-closed manifest, malformed-input rejection and missing-"
            "selection checks are synthetic structural controls. There is no "
            "pinned host package, clean checkout, typical host use, caller-"
            "owned audio or measured workload, so the Tool profile is not "
            "satisfied for qualification."),
    }


def _qualification_block(gates: list[dict]) -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "reason": (
            "No pinned or tested LiveKit Python host package pair exists, "
            "the installed audio-sdk Python binding/native library is absent "
            "at the pinned base in this worktree, no rights-cleared audio or "
            "participant scope is present, and no host API, geometry, "
            "conversion, cancellation, drain or measured workload evidence "
            "exists. Package installs and downloads are prohibited in this "
            "task, and the pinned acceptance matrix already records S09 as "
            "blocked/excluded."),
    }


def _gates() -> list[dict]:
    return [
        {"id": gate_id, "gate": name, "requirement": requirement,
         "status": "blocked"}
        for gate_id, name, requirement in GATE_REQUIREMENTS
    ]


def _blockers() -> list[dict]:
    return [
        {"id": blocker_id, "gate_id": gate_id, "state": "open",
         "requirement": requirement}
        for blocker_id, gate_id, _, requirement in EXACT_BLOCKERS
    ]


def _artifacts() -> list[dict]:
    return [
        {"id": artifact_id, "kind": kind, "requirement": requirement,
         "status": "absent"}
        for artifact_id, kind, requirement in REQUIRED_ARTIFACTS
    ]


def _reopen_conditions() -> list[dict]:
    return [
        {"gate_id": gate_id, "condition": requirement}
        for gate_id, _, requirement in GATE_REQUIREMENTS
    ]


def feasibility_verification() -> dict:
    return {
        "runnable_source": {
            "status": "absent",
            "host_package_pair_present": False,
            "sdk_binding_importable": False,
            "detail": (
                "No LiveKit host package pair and no installed audio-sdk "
                "binding/native library exist in this worktree."),
        },
        "exact_assets": {
            "status": "absent",
            "host_asset_count": 0,
            "sdk_build_asset_count": 0,
            "rights_asset_count": 0,
            "detail": (
                "No host wheel/sdist/lock/install tree, SDK build artifact or "
                "rights-cleared media is present."),
        },
        "permitted_scope": {
            "status": "task_local_evidence_only",
            "write_scope": TASK_PREFIX,
            "provider_registration": False,
            "default_selection": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "board_or_handoff_change": False,
        },
        "host_adapter_geometry": {
            "sdk_status": "source_verified",
            "host_status": HOST_GEOMETRY_STATUS,
            "sdk_sample_rate_hz": SDK_SAMPLE_RATE_HZ,
            "sdk_channels": SDK_CHANNELS,
            "sdk_frame_samples": SDK_FRAME_SAMPLES,
            "sdk_frame_ms": SDK_FRAME_MS,
            "host_shift_samples": HOST_SHIFT_SAMPLES,
            "host_shift_ms": HOST_SHIFT_MS,
            "livekit_api_verified": False,
            "livekit_execution": False,
            "structural_control_only": True,
        },
        "matched_evidence": {
            "status": "absent",
            "pacing_runs": 0,
            "pacing_seconds_measured": 0,
            "conversion_records": 0,
            "lifecycle_records": 0,
            "measured_workload": False,
            "detail": (
                "No 10 ms host pacing, conversion, capture, reset, "
                "cancellation, drain or workload record exists."),
        },
        "conclusion": "defer_external_blocker",
        "qualification_effect": "none",
    }


def _host_source_block() -> dict:
    return {
        "name": HOST_NAME,
        "family": HOST_FAMILY,
        "task_kind": TASK_KIND,
        "task_scope": TASK_SCOPE,
        "host_package_pair_pinned": HOST_PACKAGE_PAIR_PINNED,
        "host_package_version": None,
        "host_package_sha256": None,
        "host_package_imported": HOST_PACKAGE_IMPORTED,
        "host_api_status": HOST_API_STATUS,
        "host_geometry_status": HOST_GEOMETRY_STATUS,
        "host_license_status": HOST_LICENSE_STATUS,
        "sdk_library_loaded": SDK_LIBRARY_LOADED,
        "pinned_python": PINNED_PYTHON,
    }


def _asset_audit_block() -> dict:
    probes = absence_probes()
    summary = absence_summary(probes)
    modules = module_absence_probes()
    module_summary = module_absence_summary(modules)
    return {
        "qualified": False,
        "audit_result": "absent",
        "host": host_probe(),
        "sdk_build": sdk_build_probe(),
        "rights": rights_probe(),
        "evidence": evidence_probe(),
        "runtime": runtime_probe(),
        "absence": summary,
        "module_absence": module_summary,
        "observed_absence_probes": probes,
        "observed_module_probes": modules,
        "note": (
            "No LiveKit host package, lock, wheel, install tree, host API "
            "record, installed audio-sdk binding/native library, rights "
            "record or audio cohort was observed. The pinned acceptance "
            "matrix and SDK test plan are provenance, not an asset or a "
            "grant."),
    }


def _geometry_block() -> dict:
    return {
        "host_geometry_status": HOST_GEOMETRY_STATUS,
        "host_geometry_asserted": False,
        "livekit_execution": False,
        "livekit_frame_size_verified": False,
        "livekit_sample_rate_verified": False,
        "livekit_sample_format_verified": False,
        "livekit_channel_count_verified": False,
        "livekit_pacing_verified": False,
        "sdk_geometry_source": (
            "TEST_PLAN.md S-T11 plus bindings/python/audio_sdk/__init__.py"),
        "sdk_geometry_source_verified": True,
        "sdk_sample_rate_hz": SDK_SAMPLE_RATE_HZ,
        "sdk_channels": SDK_CHANNELS,
        "sdk_sample_format": "f32",
        "sdk_frame_samples": SDK_FRAME_SAMPLES,
        "sdk_frame_ms": SDK_FRAME_MS,
        "sdk_synchronous_mode_only": True,
        "host_shift_samples": HOST_SHIFT_SAMPLES,
        "host_shift_ms": HOST_SHIFT_MS,
        "startup_invalid_frames": STARTUP_INVALID_FRAMES,
        "wrong_lengths_rejected": list(REQUIRED_REJECTED_LENGTHS),
        "source_order_policy": "preserve",
        "event_loop_wait_for_inference_policy": "forbidden",
        "event_loop_wait_verified": False,
        "modeled_only": True,
        "note": (
            "The SDK boundary is pinned by the SDK test plan and binding "
            "source. LiveKit's own frame size, sample rate, sample format, "
            "channel count and pacing are not verified. The package does not "
            "assert LiveKit geometry."),
    }


def build_report() -> dict:
    identity = task_row_identity()
    gates = _gates()
    control = build_control()
    audit = _asset_audit_block()
    profile = _tool_profile_block()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "disposition": dict(DISPOSITION),
        "qualification": _qualification_block(gates),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "task_row_identity": identity,
        "linked_row_identity": linked_row_identity(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "host_source": _host_source_block(),
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "acceptance_matrix_evidence": acceptance_matrix_evidence(),
        "feasibility_verification": feasibility_verification(),
        "geometry": _geometry_block(),
        "tool_profile": profile,
        "asset_requirements": [dict(item) for item in CALLER_ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_evidence": audit["absence"],
        "absence_probes": audit["observed_absence_probes"],
        "module_absence": audit["module_absence"],
        "module_probes": audit["observed_module_probes"],
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "reference_protocol": control,
        "controls": {
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
            "adverse": control["adverse"],
            "adverse_case_count": len(control["adverse"]),
            "nonfinite_rejected": True,
            "wrong_lengths_rejected": control[
                "required_rejected_lengths_all_rejected"],
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "scope_mismatch_rejected": True,
            "variant_mismatch_rejected": True,
            "python_version_mismatch_rejected": True,
            "host_geometry_mismatch_rejected": True,
            "provider_delay_mismatch_rejected": True,
            "rights_acknowledgement_required": True,
            "validator_accepts_well_formed_manifest": True,
            "absence_probes_all_absent":
                audit["absence"]["all_probes_absent"],
            "host_modules_all_absent":
                audit["module_absence"]["all_modules_absent"],
            "host_package_never_imported": True,
            "sdk_library_never_loaded": True,
            "audio_never_read": True,
        },
        "required_artifacts": _artifacts(),
        "gates": gates,
        "remaining_gates": [
            {"id": gate["id"], "requirement": gate["requirement"],
             "status": "blocked"} for gate in gates],
        "exact_blockers": _blockers(),
        "reopen_conditions": _reopen_conditions(),
        "rights_gap": dict(RIGHTS_GAP),
        "candidate_metrics": None,
        "missing_historical_artifacts": list(ABSENCE_PROBE_PATHS),
        "non_claims": list(NON_CLAIMS),
        "prohibited_claims": list(NON_CLAIMS),
        "exact_scope": {
            "write_scope": TASK_PREFIX,
            "task_local_only": True,
            "adapter_added": False,
            "provider_added": False,
            "package_added": False,
            "wheel_added": False,
            "audio_added": False,
            "build_added": False,
        },
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar, README digest table "
                "and source manifest only; no tolerance"),
        },
        "tool_provenance": [
            "Python standard library only; no LiveKit host package, SDK "
            "binding, native library or audio runtime is imported.",
            "Fixed workspace paths are probed for host package, SDK build, "
            "rights and evidence presence; no recursive walk is performed.",
            "Interpreter module probes use importlib.util.find_spec only; no "
            "module import, package install or download occurs.",
            "No room, token, participant, media, device, engine load or "
            "timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, ensure_ascii=True, "
                "allow_nan=False, trailing newline"),
            "integers_only": True,
            "cold_start_regenerations_required": 3,
            "pinned_python": PINNED_PYTHON,
            "report_bytes_generated_by": "run.py",
        },
        "licensing": {
            "package_license": "Apache-2.0",
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "host_license": (
                "unverified; no LiveKit package or licence record is present "
                "or copied"),
        },
    }


def build_contract() -> dict:
    identity = task_row_identity()
    gates = _gates()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": dict(DISPOSITION),
        "qualification": _qualification_block(gates),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "task_row_identity": identity,
        "linked_row_identity": linked_row_identity(),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "host_source": _host_source_block(),
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "acceptance_matrix_evidence": acceptance_matrix_evidence(),
        "feasibility_verification": feasibility_verification(),
        "geometry": _geometry_block(),
        "tool_profile_requirements": [
            {"id": item, "requirement": requirement, "status": status}
            for item, requirement, status in TOOL_REQUIREMENTS
        ],
        "asset_requirements": [dict(item) for item in CALLER_ASSET_REQUIREMENTS],
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "required_artifacts": _artifacts(),
        "gates": gates,
        "exact_blockers": _blockers(),
        "reopen_conditions": _reopen_conditions(),
        "rights_gap": dict(RIGHTS_GAP),
        "missing_historical_artifacts": list(ABSENCE_PROBE_PATHS),
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar, README digest table "
                "and source manifest only; no tolerance"),
        },
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "host_license": (
                "unverified; no LiveKit package or licence record is present "
                "or copied"),
        },
    }
