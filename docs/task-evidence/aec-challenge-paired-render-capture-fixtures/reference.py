# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local declared-identity gate for AEC paired render/capture fixtures.

This module is the bounded, deterministic reference for
``SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES``.  It never loads or
fabricates licensed audio.  It strictly parses the two *local* pilot manifests
and selection CSVs that are present in the research workspace, proves that the
declared synthetic and recorded training subsets are kept separate, and reports
every declared audio item as unverified because the bytes are absent.

The admission gate is deliberately fail-closed: a caller-supplied declaration
may be schema-valid and even digest-verified against caller-owned bytes, but it
can never produce an admitted result here.  Rights approval, a frozen paired
cohort, a pinned scorer and an independent representative result are separate
requirements that this package does not have.

No network access, downloads, audio loading, model invocation, provider
registration, installed-v0 change, benchmark, listening or release claim.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES"
TITLE = "AEC Challenge paired render/capture fixtures"
COMPONENT = "aec-challenge-paired-render-capture-fixtures"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES"
BASE_COMMIT = "7dae8a27c07f9360e6243d226d44e3597ad8560f"
TASK_PREFIX = "docs/task-evidence/aec-challenge-paired-render-capture-fixtures/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SOURCE_REVISION = "8f861f0f8ffca26a3d1d16f17f2594ea89abe7ac"
SOURCE_METADATA_SHA256 = (
    "6b867aa68f510e4bafc9ffa05202930ffc1bb54bb0cffe66aa1ec3bcc606f3e5"
)
SOURCE_REPOSITORY = "https://github.com/microsoft/AEC-Challenge"

SYNTHETIC_MANIFEST = "research/aec_challenge_synthetic_pilot_manifest.json"
RECORDED_MANIFEST = "research/aec_challenge_real_pilot_manifest.json"
SYNTHETIC_SELECTION = "research/aec_challenge_synthetic_pilot_selection.csv"
RECORDED_SELECTION = "research/aec_challenge_real_pilot_selection.csv"
RIGHTS_AUDIT = (
    "realtime-audio-library/research/aec_challenge_rights_audit_20261030.md"
)
SOURCE_CROSSWALK = (
    "realtime-audio-library/research/"
    "aec_challenge_synthetic_pilot_source_crosswalk.csv"
)
SYNTHETIC_REPORT = "reports/aec_challenge_synthetic_pilot_20261028.csv"
RECORDED_REPORT = "reports/aec_challenge_real_pilot_20261028.csv"
RECORDED_SUMMARY = "reports/aec_challenge_real_pilot_summary_20261028.csv"

INSTALLED_V0_SAMPLE_RATE_HZ = 16000
INSTALLED_V0_CHANNELS = 1
INSTALLED_V0_FRAME_SAMPLES = 160
INSTALLED_V0_SAMPLE_FORMAT = "f32"

FIXTURE_SAMPLE_RATE_HZ = 16000
FIXTURE_CHANNELS = 1
ASSUMED_WAV_HEADER_BYTES = 44
MAX_ITEMS = 4096
MAX_FRAMES = 100_000_000
MAX_BYTES = 2_000_000_000

SYNTHETIC_ROLES = (
    "echo_component",
    "far_end_reference",
    "near_end_target",
    "microphone_capture",
)
RECORDED_ROLES = ("far_end_reference", "microphone_capture")
SYNTHETIC_CONDITIONS = ("linear_clean", "nonlinear_clean", "farend_noisy")
SER_VALUES = (-8, -3, 2, 7)
RECORDED_CONDITIONS = (
    "farend_singletalk",
    "farend_singletalk_with_movement",
    "doubletalk",
    "doubletalk_with_movement",
)
RECORDED_ROLE_SUFFIXES = (
    "nearend_singletalk_mic",
    "farend_singletalk_with_movement_lpb",
    "farend_singletalk_with_movement_mic",
    "farend_singletalk_lpb",
    "farend_singletalk_mic",
    "doubletalk_with_movement_lpb",
    "doubletalk_with_movement_mic",
    "doubletalk_lpb",
    "doubletalk_mic",
)

REPORT_SCHEMA = (
    "audio-sdk/aec-challenge-paired-render-capture-fixtures-report/0.1"
)
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
DECLARATION_SCHEMA = "audio-sdk/paired-render-capture-declaration/0.1"

AUDIO_NAME_PATTERN = re.compile(
    r"(echo|farend_speech|nearend_mic|nearend_speech)_fileid_(\d{1,8})\.wav\Z"
)
DECLARED_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]{0,199}\.wav\Z")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
WAV_BASENAME_PATTERN = re.compile(r"[^/\\]{1,200}\Z")

SYNTHETIC_MANIFEST_FIELDS = {
    "source_repository",
    "source_revision",
    "source_metadata_sha256",
    "selection_manifest",
    "selection_manifest_sha256",
    "split",
    "selection",
    "license_note",
    "rights_review",
    "audio_directory",
    "audio_files",
}
SYNTHETIC_ENTRY_FIELDS = {"name", "bytes", "sha256"}
RECORDED_MANIFEST_FIELDS = {
    "dataset",
    "source_repository",
    "source_revision",
    "source_folder",
    "selection_csv",
    "selection_method",
    "blind_test_data_used",
    "license_note",
    "files",
}
RECORDED_ENTRY_FIELDS = {
    "name",
    "sha256",
    "sample_rate_hz",
    "channels",
    "frames",
    "duration_seconds",
}
SYNTHETIC_SELECTION_HEADER = (
    "condition",
    "source_revision",
    "nearend_speaker",
    "nearend_wav_path",
    "nearend_wav_path_noisy",
    "farend_speaker",
    "farend_wav_path",
    "farend_wav_path_noisy",
    "ser",
    "is_farend_nonlinear",
    "is_farend_noisy",
    "is_nearend_noisy",
    "split",
    "fileid",
    "nearend_scale",
)
RECORDED_SELECTION_HEADER = (
    "guid",
    "source_revision",
    "folder",
    "selection_method",
)
DECLARATION_FIELDS = {"schema_id", "subset", "source_revision", "split", "items"}
DECLARATION_ITEM_FIELDS = {
    "group",
    "role",
    "name",
    "sha256",
    "bytes",
    "sample_rate_hz",
    "channels",
    "frames",
}

#: Stable read-only source pins, relative to the workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "research/aec_challenge_synthetic_pilot_manifest.json":
        "38b6bb4939a254d702d2ab12e95fde641957e1ced2b752eb9fb2dd8b215202b6",
    "research/aec_challenge_real_pilot_manifest.json":
        "7fd467330537107873759cdab2b63e59ff0f77e9aca324f8249c7801b109079f",
    "research/aec_challenge_synthetic_pilot_selection.csv":
        "f3d69044e8040613fc31ba0e7438e790289a41f1ac2170582a09e38a0c1322a7",
    "research/aec_challenge_real_pilot_selection.csv":
        "840caee9487c1480cd9b68bd87a3b36233464e706759465d374372cd0ab19585",
    "realtime-audio-library/research/aec_challenge_rights_audit_20261030.md":
        "1f138036f4567b4df173c18ea2dbb7d3c1cc63723e9d0acc6b339dd294b27a0d",
    "realtime-audio-library/research/"
    "aec_challenge_synthetic_pilot_source_crosswalk.csv":
        "0243ba30936ed62e15ccf157bb128c4eee2615e483708e7559c6d18064f068fa",
    "reports/aec_challenge_synthetic_pilot_20261028.csv":
        "f5da248a22a632e7221464c03c2de25386e3c7091ca68c1644f18a34dec39ef5",
    "reports/aec_challenge_real_pilot_20261028.csv":
        "32b41d1cab6b6b28a03cb6db164debfb408441822642c2a0c1a9b42b5889aba3",
    "reports/aec_challenge_real_pilot_summary_20261028.csv":
        "4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7",
}

#: Stable read-only SDK boundary pins, relative to the SDK worktree root.
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

SOURCE_FILES: Tuple[str, ...] = tuple(SOURCE_PINS)
BOUNDARY_FILES: Tuple[str, ...] = tuple(BOUNDARY_PINS)

ARTIFACT_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
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
PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES + ("contract.json",)


class Reject(ValueError):
    """A bounded, deterministic input rejection."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def _strict_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Reject("duplicate_json_key:" + key)
        result[key] = value
    return result


def _strict_constant(token: str) -> None:
    raise Reject("nonfinite_json_constant:" + token)


def parse_strict_json(text: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and non-finite constants."""
    try:
        return json.loads(text, object_pairs_hook=_strict_pairs,
                          parse_constant=_strict_constant)
    except Reject:
        raise
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        raise Reject("invalid_json") from error


def load_strict_json(path: Path) -> Any:
    return parse_strict_json(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_int(value: Any, code: str, low: int, high: int) -> int:
    _require(_is_plain_int(value), code)
    _require(low <= value <= high, code)
    return value


def _as_text(value: Any, code: str, max_length: int = 512) -> str:
    _require(isinstance(value, str), code)
    _require(1 <= len(value) <= max_length, code)
    return value


def _as_sha256(value: Any, code: str = "invalid_sha256") -> str:
    _require(isinstance(value, str), code)
    _require(SHA256_PATTERN.fullmatch(value) is not None, code)
    return value


def _as_revision(value: Any, code: str = "invalid_source_revision") -> str:
    _require(isinstance(value, str), code)
    _require(REVISION_PATTERN.fullmatch(value) is not None, code)
    return value


def _exact_fields(value: Any, expected: Sequence[str], code: str) -> Dict[str, Any]:
    _require(isinstance(value, dict), code)
    _require(set(value) == set(expected), code)
    return value


def _csv_rows(text: str, expected_header: Sequence[str],
              code: str) -> List[List[str]]:
    _require(text.endswith("\n") and "\r" not in text, code)
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as error:
        raise Reject(code) from error
    _require(bool(rows), code)
    _require(tuple(rows[0]) == tuple(expected_header), "selection_header")
    body = rows[1:]
    _require(all(len(row) == len(expected_header) for row in body),
             "selection_row_width")
    _require(all(cell != "" for row in body for cell in row),
             "selection_empty_cell")
    return body


def _parse_revision(value: str, code: str) -> str:
    _require(REVISION_PATTERN.fullmatch(value) is not None, code)
    return value


def _parse_ser(value: str) -> int:
    _require(re.fullmatch(r"-?\d{1,3}", value) is not None, "invalid_ser")
    parsed = int(value)
    _require(parsed in SER_VALUES, "invalid_ser")
    return parsed


def _parse_scale(value: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise Reject("invalid_scale") from error
    _require(math.isfinite(parsed), "invalid_scale")
    _require(0.0 < parsed <= 1.0, "invalid_scale")
    return parsed


def parse_synthetic_selection_text(text: str) -> List[Dict[str, Any]]:
    """Parse the frozen synthetic selection CSV; assert the frozen strata."""
    rows = _csv_rows(text, SYNTHETIC_SELECTION_HEADER, "invalid_selection")
    _require(len(rows) == 12, "selection_row_count")
    records: List[Dict[str, Any]] = []
    seen_ids: set = set()
    for row in rows:
        record = dict(zip(SYNTHETIC_SELECTION_HEADER, row))
        condition = record["condition"]
        _require(condition in SYNTHETIC_CONDITIONS, "invalid_condition")
        _require(_parse_revision(record["source_revision"],
                                 "invalid_source_revision") == SOURCE_REVISION,
                 "selection_revision_mismatch")
        _require(record["split"] == "train", "selection_split_not_train")
        for flag in ("is_farend_nonlinear", "is_farend_noisy", "is_nearend_noisy"):
            _require(record[flag] in {"0", "1"}, "invalid_flag")
        _require(record["is_nearend_noisy"] == "0", "nearend_noise_out_of_scope")
        if condition == "linear_clean":
            _require(record["is_farend_nonlinear"] == "0"
                     and record["is_farend_noisy"] == "0", "condition_flag_mismatch")
        elif condition == "nonlinear_clean":
            _require(record["is_farend_nonlinear"] == "1"
                     and record["is_farend_noisy"] == "0", "condition_flag_mismatch")
        else:
            _require(record["is_farend_noisy"] == "1", "condition_flag_mismatch")
        ser = _parse_ser(record["ser"])
        scale = _parse_scale(record["nearend_scale"])
        fileid = record["fileid"]
        _require(re.fullmatch(r"\d{1,8}", fileid) is not None, "invalid_fileid")
        _require(fileid not in seen_ids, "duplicate_fileid")
        seen_ids.add(fileid)
        for path_field in ("nearend_wav_path", "nearend_wav_path_noisy",
                           "farend_wav_path", "farend_wav_path_noisy"):
            _require(WAV_BASENAME_PATTERN.fullmatch(record[path_field]) is not None,
                     "invalid_source_path")
        records.append({
            "condition": condition,
            "fileid": fileid,
            "ser_db": ser,
            "nearend_scale": scale,
            "farend_nonlinear": record["is_farend_nonlinear"] == "1",
            "farend_noisy": record["is_farend_noisy"] == "1",
            "near_end_speaker": record["nearend_speaker"],
            "far_end_speaker": record["farend_speaker"],
            "split": record["split"],
        })
    records.sort(key=lambda item: item["fileid"])
    for condition in SYNTHETIC_CONDITIONS:
        stratum = [item for item in records if item["condition"] == condition]
        _require(len(stratum) == 4, "stratum_not_four")
        _require(sorted(item["ser_db"] for item in stratum) == list(SER_VALUES),
                 "stratum_ser_mismatch")
    return records


def synthetic_selection() -> Dict[str, Any]:
    path = SOURCE_ROOT / SYNTHETIC_SELECTION
    _require(path.is_file(), "missing_synthetic_selection")
    records = parse_synthetic_selection_text(path.read_text(encoding="utf-8"))
    return {
        "path": SYNTHETIC_SELECTION,
        "sha256": file_digest(path),
        "records": records,
        "strata": {condition: sum(1 for item in records
                                  if item["condition"] == condition)
                   for condition in SYNTHETIC_CONDITIONS},
        "ser_values": sorted({item["ser_db"] for item in records}),
        "scale_min": min(item["nearend_scale"] for item in records),
        "scale_max": max(item["nearend_scale"] for item in records),
        "ledger_sha256": object_digest(records),
    }


def parse_recorded_selection_text(text: str) -> List[Dict[str, Any]]:
    rows = _csv_rows(text, RECORDED_SELECTION_HEADER, "invalid_selection")
    _require(len(rows) == 12, "selection_row_count")
    records: List[Dict[str, Any]] = []
    seen: set = set()
    for row in rows:
        record = dict(zip(RECORDED_SELECTION_HEADER, row))
        _require(_parse_revision(record["source_revision"],
                                 "invalid_source_revision") == SOURCE_REVISION,
                 "selection_revision_mismatch")
        _require(record["folder"] == "datasets/real", "selection_folder_mismatch")
        _require(record["guid"] not in seen, "duplicate_group")
        seen.add(record["guid"])
        records.append({"guid": record["guid"],
                        "selection_method": record["selection_method"]})
    records.sort(key=lambda item: item["guid"])
    methods = {item["selection_method"] for item in records}
    _require(len(methods) == 1, "selection_method_mismatch")
    return records


def recorded_selection() -> Dict[str, Any]:
    path = SOURCE_ROOT / RECORDED_SELECTION
    _require(path.is_file(), "missing_recorded_selection")
    records = parse_recorded_selection_text(path.read_text(encoding="utf-8"))
    return {
        "path": RECORDED_SELECTION,
        "sha256": file_digest(path),
        "records": records,
        "groups": [item["guid"] for item in records],
        "selection_method": records[0]["selection_method"],
    }


def _rights_text_not_approved(text: str, code: str) -> str:
    lowered = text.lower()
    _require("approved" not in lowered, code)
    _require("cleared for" not in lowered, code)
    return text


def parse_synthetic_manifest(value: Any) -> Dict[str, Any]:
    manifest = _exact_fields(value, SYNTHETIC_MANIFEST_FIELDS,
                             "manifest_fields")
    _require(manifest["source_repository"] == SOURCE_REPOSITORY,
             "source_repository_mismatch")
    _require(_as_revision(manifest["source_revision"]) == SOURCE_REVISION,
             "source_revision_mismatch")
    _as_sha256(manifest["source_metadata_sha256"])
    _as_text(manifest["selection"], "manifest_selection", 4096)
    _as_text(manifest["audio_directory"], "manifest_audio_directory", 512)
    _require(not manifest["audio_directory"].startswith("/"),
             "manifest_audio_directory")
    _require(".." not in Path(manifest["audio_directory"]).parts,
             "manifest_audio_directory")
    license_note = _as_text(manifest["license_note"], "manifest_license_note",
                            4096)
    _require("not redistributed" in license_note.lower(),
             "license_note_missing_restriction")
    rights = manifest["rights_review"]
    _require(isinstance(rights, dict), "rights_review_fields")
    _require(set(rights) == {"status", "official_terms", "crosswalk", "open_gaps"},
             "rights_review_fields")
    status = _as_text(rights["status"], "rights_review_status", 4096)
    _rights_text_not_approved(status, "rights_claimed_approved")
    _require("provisional" in status.lower(), "rights_status_not_provisional")
    _require("not rights approval" in status.lower(),
             "rights_status_not_explicit")
    _require(rights["crosswalk"] == SOURCE_CROSSWALK, "crosswalk_mismatch")
    _require(isinstance(rights["open_gaps"], list)
             and 1 <= len(rights["open_gaps"]) <= 64, "rights_open_gaps")
    for gap in rights["open_gaps"]:
        _as_text(gap, "rights_open_gap", 4096)

    _require(manifest["selection_manifest"] == SYNTHETIC_SELECTION,
             "selection_manifest_mismatch")
    selection_path = SOURCE_ROOT / manifest["selection_manifest"]
    _require(selection_path.is_file(), "missing_synthetic_selection")
    _require(_as_sha256(manifest["selection_manifest_sha256"])
             == file_digest(selection_path), "selection_digest_mismatch")

    split = _as_text(manifest["split"], "manifest_split", 512)
    _require(split.lower().startswith("train only"), "split_not_train_only")
    _require("no held-out" in split.lower(), "split_not_train_only")

    entries = manifest["audio_files"]
    _require(isinstance(entries, list) and 1 <= len(entries) <= MAX_ITEMS,
             "audio_files")
    items: List[Dict[str, Any]] = []
    names: set = set()
    pairs: set = set()
    scenarios: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        item = _exact_fields(entry, SYNTHETIC_ENTRY_FIELDS, "audio_entry_fields")
        name = _as_text(item["name"], "invalid_audio_name", 200)
        _require("blind" not in name.lower(), "blind_test_fixture_rejected")
        match = AUDIO_NAME_PATTERN.fullmatch(name)
        _require(match is not None, "invalid_audio_name")
        _require(name not in names, "duplicate_audio_name")
        names.add(name)
        role_prefix, scenario = match.group(1), match.group(2)
        role = {
            "echo": "echo_component",
            "farend_speech": "far_end_reference",
            "nearend_mic": "microphone_capture",
            "nearend_speech": "near_end_target",
        }[role_prefix]
        _require((scenario, role) not in pairs, "duplicate_scenario_role")
        pairs.add((scenario, role))
        byte_count = _as_int(item["bytes"], "invalid_audio_bytes",
                             45, MAX_BYTES)
        _require((byte_count - ASSUMED_WAV_HEADER_BYTES) % 2 == 0,
                 "invalid_audio_bytes")
        digest = _as_sha256(item["sha256"])
        items.append({
            "name": name,
            "role": role,
            "scenario": scenario,
            "bytes": byte_count,
            "sha256": digest,
        })
        scenarios.setdefault(scenario, {})[role] = byte_count
    _require(len(scenarios) == 12, "scenario_count")
    scenario_records: List[Dict[str, Any]] = []
    for scenario in sorted(scenarios):
        roles = scenarios[scenario]
        _require(set(roles) == set(SYNTHETIC_ROLES), "scenario_roles_incomplete")
        spread = max(roles.values()) - min(roles.values())
        _require(spread <= 2, "scenario_length_spread")
        scenario_records.append({
            "scenario": scenario,
            "roles": {role: roles[role] for role in SYNTHETIC_ROLES},
            "declared_byte_spread": spread,
            "roles_complete": True,
        })
    _require({item["scenario"] for item in items}
             == {record["scenario"] for record in scenario_records},
             "scenario_set_mismatch")
    items.sort(key=lambda item: (item["scenario"], item["role"]))
    ledger = sorted(({"name": item["name"], "bytes": item["bytes"],
                      "sha256": item["sha256"]} for item in items),
                    key=lambda item: item["name"])
    return {
        "source_repository": manifest["source_repository"],
        "source_revision": manifest["source_revision"],
        "source_metadata_sha256": manifest["source_metadata_sha256"],
        "selection_manifest": manifest["selection_manifest"],
        "selection_manifest_sha256": manifest["selection_manifest_sha256"],
        "split": split,
        "audio_directory": manifest["audio_directory"],
        "license_note": license_note,
        "rights_review_status": status,
        "rights_open_gaps": list(rights["open_gaps"]),
        "items": items,
        "scenarios": scenario_records,
        "role_counts": {role: sum(1 for item in items if item["role"] == role)
                        for role in SYNTHETIC_ROLES},
        "declared_total_bytes": sum(item["bytes"] for item in items),
        "declared_total_frames": sum(
            (item["bytes"] - ASSUMED_WAV_HEADER_BYTES) // 2 for item in items),
        "declared_audio_parameters": None,
        "ledger_sha256": object_digest(ledger),
    }


def _split_recorded_name(name: str) -> Tuple[str, str]:
    """Return ``(group, suffix_role)`` for a recorded corpus file name."""
    _require("blind" not in name.lower(), "blind_test_fixture_rejected")
    for role in RECORDED_ROLE_SUFFIXES:
        suffix = "_" + role + ".wav"
        if name.endswith(suffix):
            group = name[: -len(suffix)]
            _require(WAV_BASENAME_PATTERN.fullmatch(name) is not None,
                     "invalid_audio_name")
            _require(1 <= len(group) <= 96, "invalid_group")
            return group, role
    raise Reject("invalid_audio_name")


def parse_recorded_manifest(value: Any,
                            selected_groups: Sequence[str]) -> Dict[str, Any]:
    manifest = _exact_fields(value, RECORDED_MANIFEST_FIELDS,
                             "manifest_fields")
    _require(manifest["source_repository"] == SOURCE_REPOSITORY,
             "source_repository_mismatch")
    _require(_as_revision(manifest["source_revision"]) == SOURCE_REVISION,
             "source_revision_mismatch")
    _require(manifest["source_folder"] == "datasets/real",
             "source_folder_mismatch")
    _require(manifest["selection_csv"] == RECORDED_SELECTION,
             "selection_csv_mismatch")
    _require(manifest["blind_test_data_used"] is False,
             "blind_test_data_used")
    _as_text(manifest["dataset"], "manifest_dataset", 512)
    _as_text(manifest["selection_method"], "manifest_selection_method", 4096)
    license_note = _as_text(manifest["license_note"], "manifest_license_note",
                            4096)
    _require("not redistributed" in license_note.lower(),
             "license_note_missing_restriction")
    _require("privacy" in license_note.lower(),
             "license_note_missing_privacy")

    entries = manifest["files"]
    _require(isinstance(entries, list) and 1 <= len(entries) <= MAX_ITEMS,
             "files")
    selected = set(selected_groups)
    items: List[Dict[str, Any]] = []
    groups: Dict[str, Dict[str, Dict[str, Any]]] = {}
    names: set = set()
    for entry in entries:
        item = _exact_fields(entry, RECORDED_ENTRY_FIELDS, "audio_entry_fields")
        name = _as_text(item["name"], "invalid_audio_name", 220)
        _require(name not in names, "duplicate_audio_name")
        names.add(name)
        group, suffix_role = _split_recorded_name(name)
        _require(group in selected, "group_not_selected")
        _require(suffix_role not in groups.get(group, {}),
                 "duplicate_group_role")
        role = ("far_end_reference" if suffix_role.endswith("_lpb")
                else "microphone_capture")
        digest = _as_sha256(item["sha256"])
        rate = _as_int(item["sample_rate_hz"], "unsupported_sample_rate",
                       1, 768_000)
        _require(rate == FIXTURE_SAMPLE_RATE_HZ, "unsupported_sample_rate")
        channels = _as_int(item["channels"], "unsupported_channels", 1, 64)
        _require(channels == FIXTURE_CHANNELS, "unsupported_channels")
        frames = _as_int(item["frames"], "invalid_frames", 1, MAX_FRAMES)
        duration = item["duration_seconds"]
        _require(isinstance(duration, (int, float))
                 and not isinstance(duration, bool), "invalid_duration")
        duration = float(duration)
        _require(math.isfinite(duration) and duration > 0.0, "invalid_duration")
        _require(abs(duration * FIXTURE_SAMPLE_RATE_HZ - frames) <= 1.0,
                 "duration_frame_mismatch")
        record = {
            "name": name,
            "group": group,
            "role": role,
            "slot": suffix_role,
            "sha256": digest,
            "bytes": None,
            "sample_rate_hz": rate,
            "channels": channels,
            "frames": frames,
            "duration_seconds": duration,
        }
        items.append(record)
        groups.setdefault(group, {})[suffix_role] = record
    _require(set(groups) == selected, "group_set_mismatch")
    pair_records: List[Dict[str, Any]] = []
    mismatched = 0
    max_delta = 0
    for group in sorted(groups):
        roles = groups[group]
        _require(len(roles) == 9, "group_roles_incomplete")
        for condition in RECORDED_CONDITIONS:
            mic = roles.get(condition + "_mic")
            lpb = roles.get(condition + "_lpb")
            _require(mic is not None and lpb is not None,
                     "group_roles_incomplete")
            delta = abs(mic["frames"] - lpb["frames"])
            if delta:
                mismatched += 1
                max_delta = max(max_delta, delta)
            pair_records.append({
                "group": group,
                "condition": condition,
                "microphone_frames": mic["frames"],
                "far_end_frames": lpb["frames"],
                "delta_frames": delta,
                "equal_length": delta == 0,
            })
        _require("nearend_singletalk_mic" in roles, "group_roles_incomplete")
    items.sort(key=lambda item: item["name"])
    ledger = sorted(({"name": item["name"], "sha256": item["sha256"],
                      "frames": item["frames"],
                      "sample_rate_hz": item["sample_rate_hz"],
                      "channels": item["channels"],
                      "duration_seconds": item["duration_seconds"]}
                     for item in items), key=lambda item: item["name"])
    return {
        "source_repository": manifest["source_repository"],
        "source_revision": manifest["source_revision"],
        "source_folder": manifest["source_folder"],
        "selection_csv": manifest["selection_csv"],
        "selection_method": manifest["selection_method"],
        "blind_test_data_used": manifest["blind_test_data_used"],
        "license_note": license_note,
        "dataset": manifest["dataset"],
        "items": items,
        "groups": sorted(groups),
        "pairs": pair_records,
        "unequal_pair_count": mismatched,
        "max_pair_delta_frames": max_delta,
        "role_counts": {role: sum(1 for item in items
                                  if item["role"] == role)
                        for role in RECORDED_ROLES},
        "declared_total_frames": sum(item["frames"] for item in items),
        "declared_total_seconds": round(
            sum(item["duration_seconds"] for item in items), 6),
        "local_audio_directory_recorded": False,
        "ledger_sha256": object_digest(ledger),
    }


def synthetic_manifest() -> Dict[str, Any]:
    path = SOURCE_ROOT / SYNTHETIC_MANIFEST
    _require(path.is_file(), "missing_synthetic_manifest")
    parsed = parse_synthetic_manifest(load_strict_json(path))
    parsed["manifest_path"] = SYNTHETIC_MANIFEST
    parsed["manifest_sha256"] = file_digest(path)
    return parsed


def recorded_manifest() -> Dict[str, Any]:
    path = SOURCE_ROOT / RECORDED_MANIFEST
    _require(path.is_file(), "missing_recorded_manifest")
    selection = recorded_selection()
    parsed = parse_recorded_manifest(load_strict_json(path),
                                     selection["groups"])
    parsed["manifest_path"] = RECORDED_MANIFEST
    parsed["manifest_sha256"] = file_digest(path)
    return parsed


def _bounded_probe_paths() -> List[str]:
    return [
        "data/tmp/aec-challenge-synthetic-pilot",
        "data/tmp/aec-challenge-real-pilot",
        "data/checkouts/AEC-Challenge/datasets/synthetic/meta.csv",
        "datasets/synthetic/meta.csv",
    ]


def presence_probe(synthetic: Dict[str, Any],
                   recorded: Dict[str, Any]) -> Dict[str, Any]:
    """Fail closed if any declared fixture byte or upstream metadata appears."""
    directory = SOURCE_ROOT / synthetic["audio_directory"]
    present_synthetic = 0
    if directory.is_dir():
        present_synthetic = sum(
            1 for item in synthetic["items"]
            if (directory / item["name"]).is_file())
    _require(present_synthetic == 0, "declared_fixture_bytes_now_present")

    probed: List[Dict[str, Any]] = []
    for relative in _bounded_probe_paths():
        candidate = SOURCE_ROOT / relative
        exists = candidate.exists()
        _require(not exists, "staged_fixture_or_metadata_present:" + relative)
        probed.append({"path": relative, "present": False})

    return {
        "bounded": True,
        "probed_paths": probed,
        "synthetic": {
            "declared_directory": synthetic["audio_directory"],
            "directory_present": False,
            "declared_files_total": len(synthetic["items"]),
            "declared_files_present": 0,
        },
        "recorded": {
            "declared_local_directory": None,
            "declared_files_total": len(recorded["items"]),
            "declared_files_present": 0,
            "note": "The recorded manifest records no local audio directory; "
                    "the recorded bytes are not staged at any declared path.",
        },
        "upstream_source_metadata": {
            "expected_sha256": SOURCE_METADATA_SHA256,
            "present": False,
            "verified": False,
        },
        "note": "Presence is probed only at the declared directory and the "
                "documented candidate paths. Absence elsewhere is not excluded.",
    }


def validate_declaration(value: Any) -> Dict[str, Any]:
    """Validate a caller-supplied paired declaration. Never admits it."""
    declaration = _exact_fields(value, DECLARATION_FIELDS, "declaration_fields")
    _require(declaration["schema_id"] == DECLARATION_SCHEMA,
             "unexpected_declaration_schema")
    subset = declaration["subset"]
    _require(subset in {"synthetic_train", "recorded_train"}, "invalid_subset")
    _require(_as_revision(declaration["source_revision"])
             == SOURCE_REVISION, "source_revision_mismatch")
    _require(declaration["split"] == "train", "split_not_train")
    allowed = (set(SYNTHETIC_ROLES) if subset == "synthetic_train"
               else set(RECORDED_ROLE_SUFFIXES))
    items = declaration["items"]
    _require(isinstance(items, list) and 1 <= len(items) <= MAX_ITEMS,
             "declaration_items")
    normalized: List[Dict[str, Any]] = []
    names: set = set()
    pairs: set = set()
    groups: Dict[str, set] = {}
    for entry in items:
        item = _exact_fields(entry, DECLARATION_ITEM_FIELDS,
                             "declaration_item_fields")
        group = _as_text(item["group"], "invalid_group", 96)
        _require("/" not in group and "\\" not in group, "invalid_group")
        role = item["role"]
        _require(isinstance(role, str) and role in allowed, "invalid_role")
        name = _as_text(item["name"], "invalid_audio_name", 200)
        _require(DECLARED_NAME_PATTERN.fullmatch(name) is not None,
                 "invalid_audio_name")
        _require("blind" not in name.lower(), "blind_test_fixture_rejected")
        _require(name not in names, "duplicate_audio_name")
        names.add(name)
        _require((group, role) not in pairs, "duplicate_item")
        pairs.add((group, role))
        digest = _as_sha256(item["sha256"])
        if item["bytes"] is None and subset == "recorded_train":
            byte_count = None
        else:
            byte_count = _as_int(item["bytes"], "invalid_audio_bytes", 1,
                                 MAX_BYTES)
        rate = _as_int(item["sample_rate_hz"], "unsupported_sample_rate",
                       1, 768_000)
        _require(rate == FIXTURE_SAMPLE_RATE_HZ, "unsupported_sample_rate")
        channels = _as_int(item["channels"], "unsupported_channels", 1, 64)
        _require(channels == FIXTURE_CHANNELS, "unsupported_channels")
        frames = _as_int(item["frames"], "invalid_frames", 1, MAX_FRAMES)
        normalized.append({"group": group, "role": role, "name": name,
                           "sha256": digest, "bytes": byte_count,
                           "sample_rate_hz": rate, "channels": channels,
                           "frames": frames})
        groups.setdefault(group, set()).add(role)
    required = set(SYNTHETIC_ROLES) if subset == "synthetic_train" \
        else set(RECORDED_ROLE_SUFFIXES)
    for group in sorted(groups):
        _require(groups[group] == required, "group_roles_incomplete")
    normalized.sort(key=lambda item: (item["group"], item["role"]))
    return {
        "schema_id": DECLARATION_SCHEMA,
        "subset": subset,
        "source_revision": declaration["source_revision"],
        "split": declaration["split"],
        "items": normalized,
        "group_count": len(groups),
        "item_count": len(normalized),
        "ledger_sha256": object_digest(normalized),
    }


def verify_declared_files(
    declaration: Dict[str, Any],
    lookup: Callable[[str], Optional[Tuple[bytes, str]]],
) -> Dict[str, Any]:
    """Check caller-owned bytes against declared size and SHA-256.

    ``lookup(name)`` returns ``(bytes, sha256)`` or ``None`` when absent.
    """
    verified = 0
    missing: List[str] = []
    size_mismatch: List[str] = []
    digest_mismatch: List[str] = []
    for item in declaration["items"]:
        found = lookup(item["name"])
        if found is None:
            missing.append(item["name"])
            continue
        data, digest = found
        if item["bytes"] is not None and len(data) != item["bytes"]:
            size_mismatch.append(item["name"])
            continue
        if digest != item["sha256"]:
            digest_mismatch.append(item["name"])
            continue
        verified += 1
    return {
        "verified": verified,
        "total": len(declaration["items"]),
        "missing": sorted(missing),
        "size_mismatch": sorted(size_mismatch),
        "digest_mismatch": sorted(digest_mismatch),
        "bytes_verified": (verified == len(declaration["items"])
                           and not missing and not size_mismatch
                           and not digest_mismatch),
    }


def admission_decision(
    declaration: Any,
    lookup: Callable[[str], Optional[Tuple[bytes, str]]],
    rights_cleared: bool,
) -> Dict[str, Any]:
    """Return a fail-closed decision. There is no admitting branch."""
    normalized = validate_declaration(declaration)
    files = verify_declared_files(normalized, lookup)
    if not files["bytes_verified"]:
        reason = "declared_fixture_bytes_unverified"
        blocked_by = ["fixture_bytes"]
    elif not rights_cleared:
        reason = "rights_not_approved"
        blocked_by = ["rights"]
    else:
        reason = "no_approved_cohort_or_independent_result"
        blocked_by = ["cohort", "scoring", "independent_review"]
    return {
        "decision": "DEFER",
        "qualifies": False,
        "reason": reason,
        "blocked_by": blocked_by,
        "bytes_verified": files["bytes_verified"],
        "rights_cleared": bool(rights_cleared),
        "declaration_ledger_sha256": normalized["ledger_sha256"],
        "item_count": normalized["item_count"],
        "verified": files["verified"],
        "total": files["total"],
        "missing_count": len(files["missing"]),
        "size_mismatch_count": len(files["size_mismatch"]),
        "digest_mismatch_count": len(files["digest_mismatch"]),
    }


def recorded_declaration(recorded: Dict[str, Any]) -> Dict[str, Any]:
    """Build a schema declaration from the live recorded manifest metadata."""
    return {
        "schema_id": DECLARATION_SCHEMA,
        "subset": "recorded_train",
        "source_revision": recorded["source_revision"],
        "split": "train",
        "items": [
            {
                "group": item["group"],
                "role": item["slot"],
                "name": item["name"],
                "sha256": item["sha256"],
                "bytes": None,
                "sample_rate_hz": item["sample_rate_hz"],
                "channels": item["channels"],
                "frames": item["frames"],
            }
            for item in recorded["items"]
        ],
    }


def _recorded_lookup(relative_root: str) -> Callable[
        [str], Optional[Tuple[bytes, str]]]:
    def lookup(name: str) -> Optional[Tuple[bytes, str]]:
        candidate = SOURCE_ROOT / relative_root / name
        if not candidate.is_file():
            return None
        payload = candidate.read_bytes()
        return payload, sha256_bytes(payload)
    return lookup


def declaration_controls(synthetic: Dict[str, Any],
                         recorded: Dict[str, Any]) -> Dict[str, Any]:
    """Live fail-closed controls over the declared metadata. No audio is read."""
    recorded_decl = recorded_declaration(recorded)
    live_decision = admission_decision(
        recorded_decl, _recorded_lookup("datasets/real"), False)

    synthetic_gap_code = None
    try:
        # The synthetic manifest omits rate, channels and frame counts, so it
        # cannot even express the paired declaration schema.
        synthetic_declaration = {
            "schema_id": DECLARATION_SCHEMA,
            "subset": "synthetic_train",
            "source_revision": synthetic["source_revision"],
            "split": "train",
            "items": [
                {
                    "group": item["scenario"],
                    "role": item["role"],
                    "name": item["name"],
                    "sha256": item["sha256"],
                    "bytes": item["bytes"],
                    "sample_rate_hz": None,
                    "channels": None,
                    "frames": None,
                }
                for item in synthetic["items"]
            ],
        }
        admission_decision(synthetic_declaration,
                           _recorded_lookup(synthetic["audio_directory"]),
                           False)
    except Reject as error:
        synthetic_gap_code = error.code

    return {
        "recorded_declaration_live": {
            "status": "deferred",
            "decision": live_decision["decision"],
            "qualifies": live_decision["qualifies"],
            "reason": live_decision["reason"],
            "item_count": live_decision["item_count"],
            "verified": live_decision["verified"],
            "missing_count": live_decision["missing_count"],
            "bytes_verified": live_decision["bytes_verified"],
            "rights_cleared": live_decision["rights_cleared"],
        },
        "synthetic_declaration_gap": {
            "status": "rejected",
            "rejected_code": synthetic_gap_code,
            "note": "The synthetic manifest records no sample rate, channel "
                    "count or frame count, so a paired declaration cannot be "
                    "expressed from it without inference. The gap is recorded, "
                    "not filled by default values.",
        },
        "representative_valid_result": {
            "status": "absent",
            "present": False,
            "qualifies": False,
            "note": "No rights-cleared representative item, paired output or "
                    "scored result exists. A missing result is never promoted.",
        },
        "admission_policy": {
            "always_defer": True,
            "admitting_branch_exists": False,
            "metadata_only_can_qualify": False,
            "caller_bytes_can_qualify_without_rights": False,
            "rights_and_bytes_still_require_cohort_and_review": True,
        },
    }


def _reject_code(callable_: Callable[[], Any]) -> str:
    try:
        callable_()
    except Reject as error:
        return error.code
    return "no_rejection"


def _record(case_id: str, expected: str, action: Callable[[], Any],
            value: Any) -> Dict[str, Any]:
    before = object_digest(value)
    observed = _reject_code(action)
    after = object_digest(value)
    return {
        "case_id": case_id,
        "expected_code": expected,
        "observed_code": observed,
        "status": "rejected" if observed == expected else "unexpected",
        "state_unchanged": before == after,
    }


def _mutated(base: Dict[str, Any],
             mutator: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
    clone = copy.deepcopy(base)
    mutator(clone)
    return clone


def adverse_rejections() -> List[Dict[str, Any]]:
    synthetic = synthetic_manifest()
    recorded = recorded_manifest()
    selection = synthetic_selection()
    recorded_selection_value = recorded_selection()
    base_synthetic = {
        "source_repository": synthetic["source_repository"],
        "source_revision": synthetic["source_revision"],
        "source_metadata_sha256": synthetic["source_metadata_sha256"],
        "selection_manifest": synthetic["selection_manifest"],
        "selection_manifest_sha256": synthetic["selection_manifest_sha256"],
        "split": synthetic["split"],
        "selection": "declared selection text",
        "license_note": synthetic["license_note"],
        "rights_review": {
            "status": "provisional source-family mapping; not rights approval "
                      "or acceptance-data clearance",
            "official_terms": "component terms apply",
            "crosswalk": SOURCE_CROSSWALK,
            "open_gaps": ["gap"],
        },
        "audio_directory": synthetic["audio_directory"],
        "audio_files": [
            {"name": item["name"], "bytes": item["bytes"],
             "sha256": item["sha256"]}
            for item in synthetic["items"]
        ],
    }
    base_recorded = {
        "dataset": recorded["dataset"],
        "source_repository": recorded["source_repository"],
        "source_revision": recorded["source_revision"],
        "source_folder": recorded["source_folder"],
        "selection_csv": recorded["selection_csv"],
        "selection_method": recorded["selection_method"],
        "blind_test_data_used": False,
        "license_note": recorded["license_note"],
        "files": [
            {"name": item["name"], "sha256": item["sha256"],
             "sample_rate_hz": item["sample_rate_hz"],
             "channels": item["channels"], "frames": item["frames"],
             "duration_seconds": item["duration_seconds"]}
            for item in recorded["items"]
        ],
    }
    base_declaration = recorded_declaration(recorded)
    groups = recorded["groups"]

    cases: List[Dict[str, Any]] = []

    def synthetic_case(case_id: str, expected: str,
                       mutator: Callable[[Dict[str, Any]], None]) -> None:
        value = _mutated(base_synthetic, mutator)
        cases.append(_record(
            case_id, expected,
            lambda value=value: parse_synthetic_manifest(value), value))

    def recorded_case(case_id: str, expected: str,
                      mutator: Callable[[Dict[str, Any]], None]) -> None:
        value = _mutated(base_recorded, mutator)
        cases.append(_record(
            case_id, expected,
            lambda value=value: parse_recorded_manifest(value, groups), value))

    def declaration_case(case_id: str, expected: str,
                         mutator: Callable[[Dict[str, Any]], None]) -> None:
        value = _mutated(base_declaration, mutator)
        cases.append(_record(
            case_id, expected,
            lambda value=value: validate_declaration(value), value))

    synthetic_case("synthetic_revision_uppercase", "invalid_source_revision",
                   lambda v: v.__setitem__("source_revision",
                                           SOURCE_REVISION.upper()))
    synthetic_case("synthetic_digest_uppercase", "invalid_sha256",
                   lambda v: v["audio_files"][0].__setitem__(
                       "sha256", v["audio_files"][0]["sha256"].upper()))
    synthetic_case("synthetic_missing_field", "manifest_fields",
                   lambda v: v.pop("split"))
    synthetic_case("synthetic_extra_field", "manifest_fields",
                   lambda v: v.__setitem__("unexpected", True))
    synthetic_case("synthetic_duplicate_name", "duplicate_audio_name",
                   lambda v: v["audio_files"].append(
                       dict(v["audio_files"][0])))
    synthetic_case("synthetic_unknown_role", "invalid_audio_name",
                   lambda v: v["audio_files"][0].__setitem__(
                       "name", "mix_fileid_5450.wav"))
    synthetic_case("synthetic_missing_role", "scenario_roles_incomplete",
                   lambda v: v["audio_files"].pop(0))
    synthetic_case("synthetic_zero_bytes", "invalid_audio_bytes",
                   lambda v: v["audio_files"][0].__setitem__("bytes", 0))
    synthetic_case("synthetic_odd_data", "invalid_audio_bytes",
                   lambda v: v["audio_files"][0].__setitem__("bytes", 321))
    synthetic_case("synthetic_bool_bytes", "invalid_audio_bytes",
                   lambda v: v["audio_files"][0].__setitem__("bytes", True))
    synthetic_case("synthetic_split_test", "split_not_train_only",
                   lambda v: v.__setitem__("split", "test split"))
    synthetic_case("synthetic_selection_stale", "selection_digest_mismatch",
                   lambda v: v.__setitem__("selection_manifest_sha256", "0" * 64))
    synthetic_case("synthetic_rights_approved", "rights_claimed_approved",
                   lambda v: v["rights_review"].__setitem__(
                       "status", "approved for release"))
    synthetic_case("synthetic_scenario_spread", "scenario_length_spread",
                   lambda v: v["audio_files"][0].__setitem__(
                       "bytes", v["audio_files"][0]["bytes"] + 400))
    synthetic_case("synthetic_blind_name", "blind_test_fixture_rejected",
                   lambda v: v["audio_files"][0].__setitem__(
                       "name", "echo_blind_fileid_5450.wav"))
    synthetic_case("synthetic_duplicate_key", "duplicate_json_key:source_revision",
                   lambda v: None)
    cases[-1] = _record(
        "synthetic_duplicate_key", "duplicate_json_key:source_revision",
        lambda: parse_strict_json(
            '{"source_revision":"a","source_revision":"b"}'), {})
    synthetic_case("synthetic_nan_constant", "nonfinite_json_constant:NaN",
                   lambda v: None)
    cases[-1] = _record(
        "synthetic_nan_constant", "nonfinite_json_constant:NaN",
        lambda: parse_strict_json('{"x":NaN}'), {})
    synthetic_case("synthetic_invalid_json", "invalid_json",
                   lambda v: None)
    cases[-1] = _record("synthetic_invalid_json", "invalid_json",
                        lambda: parse_strict_json('{"x":}'), {})

    recorded_case("recorded_blind_flag", "blind_test_data_used",
                  lambda v: v.__setitem__("blind_test_data_used", True))
    recorded_case("recorded_channels", "unsupported_channels",
                  lambda v: v["files"][0].__setitem__("channels", 2))
    recorded_case("recorded_rate", "unsupported_sample_rate",
                  lambda v: v["files"][0].__setitem__("sample_rate_hz", 44100))
    recorded_case("recorded_zero_frames", "invalid_frames",
                  lambda v: v["files"][0].__setitem__("frames", 0))
    recorded_case("recorded_duration_mismatch", "duration_frame_mismatch",
                  lambda v: v["files"][0].__setitem__(
                      "duration_seconds",
                      v["files"][0]["duration_seconds"] + 5.0))
    recorded_case("recorded_missing_role", "group_roles_incomplete",
                  lambda v: v["files"].pop(0))
    recorded_case("recorded_unknown_group", "group_not_selected",
                  lambda v: v["files"][0].__setitem__(
                      "name", "unknown-group_doubletalk_mic.wav"))
    recorded_case("recorded_duplicate_name", "duplicate_audio_name",
                  lambda v: v["files"].append(dict(v["files"][0])))
    recorded_case("recorded_uppercase_digest", "invalid_sha256",
                  lambda v: v["files"][0].__setitem__(
                      "sha256", v["files"][0]["sha256"].upper()))
    recorded_case("recorded_extra_field", "manifest_fields",
                  lambda v: v.__setitem__("extra", 1))

    declaration_case("declaration_bad_schema", "unexpected_declaration_schema",
                     lambda v: v.__setitem__("schema_id", "other/0.1"))
    declaration_case("declaration_unknown_role", "invalid_role",
                     lambda v: v["items"][0].__setitem__("role", "unknown"))
    declaration_case("declaration_subset_mismatch", "invalid_role",
                     lambda v: v["items"][0].__setitem__("role",
                                                         "echo_component"))
    declaration_case("declaration_duplicate_item", "duplicate_audio_name",
                     lambda v: v["items"].append(dict(v["items"][0])))
    declaration_case("declaration_zero_frames", "invalid_frames",
                     lambda v: v["items"][0].__setitem__("frames", 0))
    declaration_case("declaration_channels", "unsupported_channels",
                     lambda v: v["items"][0].__setitem__("channels", 2))
    declaration_case("declaration_rate", "unsupported_sample_rate",
                     lambda v: v["items"][0].__setitem__("sample_rate_hz", 8000))
    declaration_case("declaration_split", "split_not_train",
                     lambda v: v.__setitem__("split", "test"))
    declaration_case("declaration_extra_item_field", "declaration_item_fields",
                     lambda v: v["items"][0].__setitem__("extra", 1))
    declaration_case("declaration_blind_name", "blind_test_fixture_rejected",
                     lambda v: v["items"][0].__setitem__(
                         "name", "blind_doubletalk_mic.wav"))
    declaration_case("declaration_missing_group_role", "group_roles_incomplete",
                     lambda v: v["items"].pop(0))

    selection_text = (SOURCE_ROOT / SYNTHETIC_SELECTION).read_text(
        encoding="utf-8")
    rows = list(csv.reader(io.StringIO(selection_text)))
    cases.append(_record(
        "selection_bad_header", "selection_header",
        lambda: parse_synthetic_selection_text(
            selection_text.replace("condition,", "conditionX,", 1)),
        {}))
    cases.append(_record(
        "selection_bad_ser", "invalid_ser",
        lambda: parse_synthetic_selection_text(
            selection_text.replace(",2,0,0,0,train,", ",99,0,0,0,train,", 1)),
        {}))
    cases.append(_record(
        "selection_bad_condition", "invalid_condition",
        lambda: parse_synthetic_selection_text(
            selection_text.replace("linear_clean", "linear_unknown", 1)),
        {}))
    cases.append(_record(
        "selection_bad_scale", "invalid_scale",
        lambda: parse_synthetic_selection_text(
            selection_text.replace("0.7084622548878267", "1.5", 1)),
        {}))
    cases.append(_record(
        "selection_test_split", "selection_split_not_train",
        lambda: parse_synthetic_selection_text(
            selection_text.replace(",train,5450,", ",test,5450,", 1)),
        {}))
    cases.append(_record(
        "selection_missing_row", "selection_row_count",
        lambda: parse_synthetic_selection_text(
            "\n".join(selection_text.splitlines()[:-1]) + "\n"),
        {}))
    cases.append(_record(
        "recorded_selection_bad_folder", "selection_folder_mismatch",
        lambda: parse_recorded_selection_text(
            (SOURCE_ROOT / RECORDED_SELECTION).read_text(
                encoding="utf-8").replace("datasets/real", "datasets/test", 1)),
        {}))
    cases.append(_record(
        "recorded_selection_bad_group", "duplicate_group",
        lambda: parse_recorded_selection_text(
            (SOURCE_ROOT / RECORDED_SELECTION).read_text(
                encoding="utf-8").replace(recorded_selection_value["groups"][0],
                                          recorded_selection_value["groups"][1],
                                          1)),
        {}))
    cases.append(_record(
        "declaration_over_limit", "declaration_items",
        lambda: validate_declaration({
            "schema_id": DECLARATION_SCHEMA,
            "subset": "recorded_train",
            "source_revision": SOURCE_REVISION,
            "split": "train",
            "items": [],
        }), {}))

    _require(len(rows) == 13, "selection_csv_shape_changed")
    _require(selection["sha256"] == file_digest(SOURCE_ROOT / SYNTHETIC_SELECTION),
             "selection_changed")
    return cases


def release_gates() -> List[Dict[str, Any]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Stage the exact synthetic (48) and recorded (108) "
                           "WAV bytes with the declared SHA-256 values and pass "
                           "the fail-closed admission gate for every item.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Reacquire the pinned upstream meta.csv (SHA-256 "
                           "6b867aa68f510e4bafc9ffa05202930ffc1bb54bb0cffe66aa1"
                           "ec3bcc606f3e5) and reproduce the per-file "
                           "source-to-term crosswalk, including scenario 5561.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Obtain participant consent, privacy/publicity and "
                           "intended-use terms for the recorded device subset.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Obtain an explicit data-owner approval for "
                           "retention, internal evaluation, acceptance use and "
                           "any redistribution scope.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Freeze a rights-cleared paired render/capture "
                           "cohort with an untouched holdout, exact references "
                           "and item digests kept separate from tuning data.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Pin the scorer, metric protocol, aggregation, "
                           "failed-item policy and identity/adverse controls "
                           "for the exact cohort.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Validate one invalid/missing case and one "
                           "representative valid result through the reported "
                           "bundle at the exact head.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Record an explicit opt-in evidence-adapter "
                           "exposure decision and independent review; no "
                           "provider, registry, default, ABI or release change "
                           "before this gate.",
            "status": "blocked",
        },
    ]


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "licensed_audio_fixtures_absent",
            "requirement": "Stage the 48 declared synthetic WAVs under "
                           "data/tmp/aec-challenge-synthetic-pilot and the 108 "
                           "declared recorded WAVs at a declared local path, "
                           "each matching its declared SHA-256, then verify "
                           "every item through the admission gate.",
            "state": "The declared synthetic directory and both documented "
                     "candidate roots are absent; the recorded manifest records "
                     "no local audio directory. Declared items verified: 0 of "
                     "156. No byte is downloaded, copied or inferred.",
        },
        {
            "id": "upstream_source_metadata_absent",
            "requirement": "Provide the upstream datasets/synthetic/meta.csv "
                           "whose SHA-256 is pinned as "
                           "6b867aa68f510e4bafc9ffa05202930ffc1bb54bb0cffe66aa1"
                           "ec3bcc606f3e5, and reproduce the per-file "
                           "speaker/noise source mapping and terms.",
            "state": "The pinned meta.csv is absent locally; the source "
                     "crosswalk is provisional and leaves scenario 5561's "
                     "noise source unidentified. Mapping cannot be "
                     "independently reproduced.",
        },
        {
            "id": "rights_not_approved",
            "requirement": "Record data-owner approval with the exact terms "
                           "for each subset: component attribution/share-alike "
                           "for the synthetic inputs, participant consent, "
                           "privacy/publicity and intended-use for the "
                           "recorded devices, plus acceptance and "
                           "redistribution scope.",
            "state": "No approval record exists. The synthetic subset has only "
                     "a provisional source-family mapping; the recorded subset "
                     "has no participant-level consent, privacy/publicity or "
                     "intended-use terms. Neither subset is cleared for "
                     "acceptance or redistribution.",
        },
        {
            "id": "paired_cohort_holdout_and_scoring_absent",
            "requirement": "Freeze a rights-cleared paired cohort and holdout, "
                           "pin the scorer and metric protocol, define "
                           "aggregation and failed-item handling, and report a "
                           "representative valid result plus an invalid/missing "
                           "control.",
            "state": "Only an invalid/missing control exists (the declared "
                     "recorded items are rejected as unverified). No cohort, "
                     "holdout, scorer, aggregation, AECMOS/listening/ASR "
                     "result or representative valid result exists; prior "
                     "pilot CSVs are not re-executed or adopted.",
        },
        {
            "id": "evidence_adapter_exposure_undecided",
            "requirement": "Complete an opt-in SDK evidence-adapter intake with "
                           "an explicit proceed/defer decision before exposing "
                           "these fixtures to any processor or default path.",
            "state": "Decision is DEFER before "
                     "optional_evidence_adapter_exposure. No provider, "
                     "descriptor, registry entry, installed default, public "
                     "ABI, shared build or CI path is added.",
        },
    ]


def board_row() -> Dict[str, Any]:
    """Read only the stable linked-row identity; never hash the full board."""
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD)
    _require(isinstance(payload, dict) and isinstance(payload.get("tasks"), list),
             "invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    _require(len(rows) == 1, "task_row_not_unique")
    row = rows[0]
    _require(isinstance(row.get("depends_on"), list)
             and all(isinstance(value, str) for value in row["depends_on"]),
             "invalid_task_row")
    stable_fields = {
        "id": row["id"],
        "title": row["title"],
        "repository": row["repository"],
        "mode": row["mode"],
        "depends_on": row["depends_on"],
        "component": row["component"],
    }
    return {
        "stable_fields": stable_fields,
        "stable_sha256": object_digest(stable_fields),
        "full_tasks_json_hashed": False,
        "note": "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never read into, hashed by or "
                "pinned to this package.",
    }


def _verify_pins() -> None:
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)


def evidence_profile() -> Dict[str, Any]:
    return {
        "profile": "evidence",
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "pinned_scorer_corpus_and_cohort": {
                "status": "blocked",
                "evidence": "No scorer, rights-cleared corpus or frozen cohort "
                            "is staged; only declared metadata is present.",
            },
            "aggregation_failed_items_and_controls": {
                "status": "blocked",
                "evidence": "No aggregation, failed-item policy or scored "
                            "control result exists.",
            },
            "separation_of_evidence_kinds": {
                "status": "declared_only",
                "evidence": "Synthetic train and recorded train subsets are "
                            "parsed and kept separate with independent ledgers; "
                            "paired/unpaired, synthetic/human and "
                            "source-reported separation is recorded but not "
                            "scored.",
            },
            "invalid_or_missing_case_validated": {
                "status": "recorded",
                "evidence": "The live recorded declaration is rejected because "
                            "0 of 108 declared bytes are present; adverse "
                            "metadata cases are rejected without state change.",
            },
            "representative_valid_result_validated": {
                "status": "blocked",
                "evidence": "No representative valid item or result exists; "
                            "the required valid half of the profile cannot be "
                            "validated.",
            },
            "exact_references_and_rights": {
                "status": "blocked",
                "evidence": "Declared item digests are recorded but unverified; "
                            "no rights approval exists for either subset.",
            },
        },
        "mapped_cases": {
            "synthetic_train_partition": "12 declared scenarios, 48 declared "
                                         "items, four roles each",
            "recorded_train_partition": "12 declared device groups, 108 "
                                        "declared items, nine roles each",
            "live_missing_bytes_control": "recorded declaration rejected with "
                                          "108 of 108 bytes missing",
            "adverse_metadata_controls": "strict schema, digest, split, "
                                         "rate/channel/frame and blindness "
                                         "rejections",
        },
        "not_applicable": [
            "paired SI-SDR/STOI or AECMOS scoring without permitted references "
            "and audio",
            "listening, device timing, benchmark and release qualification",
        ],
    }


def _core() -> Dict[str, Any]:
    """Deterministic core recomputed three times."""
    synthetic = synthetic_manifest()
    recorded = recorded_manifest()
    synthetic_sel = synthetic_selection()
    recorded_sel = recorded_selection()
    probe = presence_probe(synthetic, recorded)
    controls = declaration_controls(synthetic, recorded)
    adverse = adverse_rejections()

    _require(all(case["status"] == "rejected" for case in adverse),
             "adverse_case_not_rejected")
    _require(all(case["state_unchanged"] for case in adverse),
             "adverse_case_mutated_state")
    _require(controls["recorded_declaration_live"]["decision"] == "DEFER",
             "live_declaration_admitted")
    _require(controls["synthetic_declaration_gap"]["rejected_code"]
             == "unsupported_sample_rate", "synthetic_gap_not_rejected")

    return {
        "synthetic": synthetic,
        "recorded": recorded,
        "synthetic_selection": synthetic_sel,
        "recorded_selection": recorded_sel,
        "probe": probe,
        "controls": controls,
        "adverse": adverse,
    }


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    first = _core()
    digests = [object_digest(first)]
    for _ in range(2):
        digests.append(object_digest(_core()))
    _require(len(set(digests)) == 1, "core_not_repeatable")

    core = first
    synthetic = core["synthetic"]
    recorded = core["recorded"]
    controls = core["controls"]
    adverse = core["adverse"]

    source_pin_digests = {
        "synthetic_manifest": synthetic["manifest_sha256"],
        "recorded_manifest": recorded["manifest_sha256"],
        "synthetic_selection": core["synthetic_selection"]["sha256"],
        "recorded_selection": core["recorded_selection"]["sha256"],
        "rights_audit": SOURCE_PINS[RIGHTS_AUDIT],
        "source_crosswalk": SOURCE_PINS[SOURCE_CROSSWALK],
    }
    for relative in (SYNTHETIC_REPORT, RECORDED_REPORT, RECORDED_SUMMARY):
        _require(relative in SOURCE_PINS, "missing_report_pin")

    return {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "proposal_only": True,
        "decision": "DEFER",
        "defer_before": "optional_evidence_adapter_exposure",
        "scope": (
            "Task-local declared-identity audit of the Microsoft AEC Challenge "
            "synthetic and recorded training pilot metadata that is present in "
            "the research workspace. No licensed audio bytes, upstream "
            "meta.csv, rights approval, scorer, cohort, listening, device "
            "timing, benchmark or release result is present."
        ),
        "acceptance_profile": evidence_profile(),
        "format": {
            "installed_v0_sample_rate_hz": INSTALLED_V0_SAMPLE_RATE_HZ,
            "installed_v0_channels": INSTALLED_V0_CHANNELS,
            "installed_v0_frame_samples": INSTALLED_V0_FRAME_SAMPLES,
            "installed_v0_sample_format": INSTALLED_V0_SAMPLE_FORMAT,
            "installed_v0_geometry_unchanged": True,
            "fixture_sample_rate_hz": FIXTURE_SAMPLE_RATE_HZ,
            "fixture_channels": FIXTURE_CHANNELS,
            "synthetic_declared_audio_parameters": None,
            "recorded_declared_sample_rate_hz": FIXTURE_SAMPLE_RATE_HZ,
            "recorded_declared_channels": FIXTURE_CHANNELS,
            "assumed_wav_header_bytes": ASSUMED_WAV_HEADER_BYTES,
            "sample_format_source": "recorded manifest declares rate/channels; "
                                    "the synthetic manifest declares bytes only",
        },
        "source_and_metadata": {
            "source_repository": SOURCE_REPOSITORY,
            "source_revision": SOURCE_REVISION,
            "declared_source_metadata_sha256": SOURCE_METADATA_SHA256,
            "source_metadata_present": False,
            "source_metadata_verified": False,
            "digests": source_pin_digests,
            "prior_reported_aggregates": {
                "synthetic_report": {
                    "path": SYNTHETIC_REPORT,
                    "sha256": SOURCE_PINS[SYNTHETIC_REPORT],
                },
                "recorded_report": {
                    "path": RECORDED_REPORT,
                    "sha256": SOURCE_PINS[RECORDED_REPORT],
                },
                "recorded_summary": {
                    "path": RECORDED_SUMMARY,
                    "sha256": SOURCE_PINS[RECORDED_SUMMARY],
                },
                "reexecuted": False,
                "adopted": False,
                "note": "Prior research aggregates are pinned provenance only. "
                        "They were produced before this task package, are not "
                        "re-executed here and are not attributed to it.",
            },
        },
        "fixture_partitions": {
            "synthetic_train": {
                "subset": "synthetic_train",
                "declared_source_revision": synthetic["source_revision"],
                "manifest_path": synthetic["manifest_path"],
                "manifest_sha256": synthetic["manifest_sha256"],
                "selection_path": synthetic["selection_manifest"],
                "selection_sha256": synthetic["selection_manifest_sha256"],
                "scenario_count": len(synthetic["scenarios"]),
                "item_count": len(synthetic["items"]),
                "role_counts": synthetic["role_counts"],
                "strata": core["synthetic_selection"]["strata"],
                "ser_values": core["synthetic_selection"]["ser_values"],
                "near_end_scale_min": core["synthetic_selection"]["scale_min"],
                "near_end_scale_max": core["synthetic_selection"]["scale_max"],
                "declared_total_bytes": synthetic["declared_total_bytes"],
                "declared_total_frames_inferred": synthetic[
                    "declared_total_frames"],
                "declared_audio_parameters": None,
                "split": synthetic["split"],
                "items_present": 0,
                "items_verified": 0,
                "ledger_sha256": synthetic["ledger_sha256"],
                "rights_status": "provisional_source_family_mapping_not_approved",
                "items": synthetic["items"],
            },
            "recorded_train": {
                "subset": "recorded_train",
                "declared_source_revision": recorded["source_revision"],
                "manifest_path": recorded["manifest_path"],
                "manifest_sha256": recorded["manifest_sha256"],
                "selection_path": recorded["selection_csv"],
                "selection_sha256": core["recorded_selection"]["sha256"],
                "group_count": len(recorded["groups"]),
                "item_count": len(recorded["items"]),
                "role_counts": recorded["role_counts"],
                "declared_total_frames": recorded["declared_total_frames"],
                "declared_total_seconds": recorded["declared_total_seconds"],
                "sample_rate_hz": FIXTURE_SAMPLE_RATE_HZ,
                "channels": FIXTURE_CHANNELS,
                "blind_test_data_used": recorded["blind_test_data_used"],
                "local_audio_directory_recorded": recorded[
                    "local_audio_directory_recorded"],
                "items_present": 0,
                "items_verified": 0,
                "ledger_sha256": recorded["ledger_sha256"],
                "rights_status": "not_cleared_no_participant_terms",
                "items": recorded["items"],
            },
            "pooling": {
                "subsets_pooled": False,
                "cross_subset_deduplication": False,
                "note": "Synthetic train and recorded train are kept separate "
                        "with independent manifests, ledgers and rights states.",
            },
        },
        "pair_structure": {
            "synthetic_scenarios": synthetic["scenarios"],
            "synthetic_all_roles_complete": True,
            "synthetic_max_byte_spread": max(
                scenario["declared_byte_spread"]
                for scenario in synthetic["scenarios"]),
            "recorded_groups": len(recorded["groups"]),
            "recorded_conditions": list(RECORDED_CONDITIONS),
            "recorded_pair_count": len(recorded["pairs"]),
            "recorded_unequal_pair_count": recorded["unequal_pair_count"],
            "recorded_max_pair_delta_frames": recorded[
                "max_pair_delta_frames"],
            "recorded_pairs": recorded["pairs"],
            "tail_policy": "Declared unequal microphone/loopback tails require "
                           "an explicit truncation policy at evaluation; the "
                           "policy is declared upstream but not re-executed or "
                           "verified here.",
        },
        "presence_probe": core["probe"],
        "admission_controls": controls,
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "rights": {
            "status": "not_approved",
            "code_license": "MIT applies to the AEC-Challenge repository code "
                            "only; it does not license the recordings",
            "synthetic_subset": {
                "status": "provisional_source_family_mapping_not_approved",
                "crosswalk_path": SOURCE_CROSSWALK,
                "crosswalk_sha256": SOURCE_PINS[SOURCE_CROSSWALK],
                "rights_audit_path": RIGHTS_AUDIT,
                "rights_audit_sha256": SOURCE_PINS[RIGHTS_AUDIT],
                "attribution_or_share_alike_record": False,
                "unidentified_source_case": "scenario 5561",
                "approval": False,
            },
            "recorded_subset": {
                "status": "not_cleared",
                "participant_consent": False,
                "privacy_or_publicity_grant": False,
                "intended_use_grant": False,
                "rights_audit_path": RIGHTS_AUDIT,
                "rights_audit_sha256": SOURCE_PINS[RIGHTS_AUDIT],
                "approval": False,
            },
            "acceptance_use": False,
            "redistribution": False,
            "approval_record": None,
        },
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "qualification": {
            "status": "not_qualified",
            "decision": "DEFER",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "fixture_bytes_verified": False,
            "rights_approved": False,
            "paired_cohort_frozen": False,
            "scorer_pinned": False,
            "representative_valid_result": False,
            "invalid_or_missing_control": True,
            "provider_intake": False,
            "release_claim": False,
        },
        "boundary": {
            "provider_registration": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "default_selected": False,
            "enabled_by_default": False,
            "processor_exposure": False,
            "adapter_added": False,
            "shared_build_or_ci_change": False,
            "sdk_data_dir_added": False,
            "asset_bundled": False,
            "weights_vendored": False,
            "audio_loaded": False,
            "audio_executed": False,
            "network_used": False,
            "board_or_handoff_changed": False,
        },
        "board_row": board_row(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "core_digests": digests,
            "synthetic_ledger_sha256": synthetic["ledger_sha256"],
            "recorded_ledger_sha256": recorded["ledger_sha256"],
        },
        "negative_claims": [
            "No licensed audio byte, upstream meta.csv, model, runtime, "
            "weight, real corpus or device was loaded, copied or executed.",
            "No rights approval, qualified paired result, listening result, "
            "device timing, benchmark or release claim exists.",
            "No provider registration, descriptor, registry, installed v0, "
            "public ABI, shared build, CI or default change exists.",
            "Prior pilot CSVs are pinned provenance only and are not "
            "re-executed, adopted or pooled with this package.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08: stage and verify the exact declared "
            "WAV bytes, reproduce the upstream source/term crosswalk, obtain "
            "participant and data-owner approvals, freeze a rights-cleared "
            "paired cohort with an untouched holdout, pin the scorer and "
            "aggregation, validate a representative result at the exact head, "
            "and record an explicit opt-in evidence-adapter exposure decision."
        ),
    }


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def artifact_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        path = HERE / name
        _require(path.is_file(), "missing_artifact:" + name)
        pins[TASK_PREFIX + name] = file_digest(path)
    return pins


def build_contract() -> Dict[str, Any]:
    """Build contract.json after report.json and its sidecar are written."""
    pins = artifact_pins()
    gates = release_gates()
    blockers = exact_blockers()
    stable = board_row()
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "proposal_only": True,
        "decision": "DEFER",
        "defer_before": "optional_evidence_adapter_exposure",
        "qualification_status": "not_qualified",
        "verification_profile": "evidence",
        "scope": {
            "benchmark_claim": False,
            "device_timing": False,
            "listening": False,
            "network_access": False,
            "numeric_parity_claim": False,
            "processor_exposure": False,
            "public_default": False,
            "real_audio": False,
            "real_corpus": False,
            "real_speech": False,
            "release_claim": False,
            "runtime_invocation": False,
            "rights_approved": False,
            "synthetic_only": True,
            "task_local_only": True,
            "weights": False,
        },
        "format": {
            "installed_v0_sample_rate_hz": INSTALLED_V0_SAMPLE_RATE_HZ,
            "installed_v0_channels": INSTALLED_V0_CHANNELS,
            "installed_v0_frame_samples": INSTALLED_V0_FRAME_SAMPLES,
            "installed_v0_sample_format": INSTALLED_V0_SAMPLE_FORMAT,
            "installed_v0_geometry_preserved": True,
            "fixture_sample_rate_hz": FIXTURE_SAMPLE_RATE_HZ,
            "fixture_channels": FIXTURE_CHANNELS,
            "synthetic_declared_audio_parameters": None,
            "declaration_schema": DECLARATION_SCHEMA,
        },
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "abi_major": 0,
            "abi_minor": 1,
            "registration": "none; no provider, descriptor, registry entry or "
                            "installed default is added",
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "shared_build_or_ci_changed": False,
        },
        "reference": {
            "reference_id": "aec-paired-fixture-declared-identity-gate-v1",
            "modes": ["declared_partition_audit", "fail_closed_admission_gate"],
            "audio_loaded": False,
            "audio_downloaded": False,
            "fixture_bytes_present": False,
            "rights_approved": False,
            "admitting_branch_exists": False,
            "metadata_only_can_qualify": False,
            "model_weights": False,
            "registered": False,
            "default_enabled": False,
        },
        "board_row": stable,
        "exact_blockers": blockers,
        "release_gates": gates,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": pins,
        "negative_claims": [
            "No licensed audio, upstream meta.csv, runtime, model or device "
            "was loaded, copied or executed.",
            "No qualified paired result, listening, device timing, benchmark "
            "or release claim exists.",
            "No provider registration, installed v0, ABI, registry, default, "
            "shared build or CI change exists.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08 with exact verified fixture bytes, a "
            "reproduced source/term crosswalk, participant and data-owner "
            "approval, a frozen rights-cleared cohort and holdout, a pinned "
            "scorer, a representative exact-head result and an explicit "
            "opt-in evidence-adapter exposure decision."
        ),
    }


def sources_bytes() -> bytes:
    """Regenerate SOURCES.sha256 bytes from hard pins plus live artifacts."""
    _verify_pins()
    for name in PIN_FILES:
        _require((HERE / name).is_file(), "missing_artifact:" + name)

    lines = [
        "# SHA-256 pins for " + TASK_ID
        + "; source: paths are workspace-relative, others SDK-worktree-relative."
    ]
    for path in SOURCE_FILES:
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in BOUNDARY_FILES:
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in PIN_FILES:
        lines.append(f"{file_digest(HERE / name)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
