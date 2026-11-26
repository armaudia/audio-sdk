# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local vendor-boundary evidence for SDK-SAMPLESUMO-TS.

Standard library only. The pinned candidate record describes SampleSumo TS as a
commercial time-varying actuator with push/pull and mono/stereo support, but
publishes no pricing or terms. No runnable SDK, source revision, artifact
identity, licence text, evaluation entitlement, offline runtime, processed data
or vendor output is present. This module pins the evidence that does exist,
proves a fixed absence inventory, validates a caller-supplied tool-manifest
reference without resolving a path or loading any vendor code, applies the Rate
profile to an integer position envelope, and builds canonical DEFER bytes.
Nothing here is a vendor runtime, audio, rate, quality, timing, listening,
benchmark or release result.
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

TASK = "SDK-SAMPLESUMO-TS"
TASK_TITLE = "SampleSumo TS"
COMPONENT_ID = "samplesumo-ts"
REPOSITORY = "audio-sdk"
MODE = "external-adapter"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
TASK_PREFIX = "docs/task-evidence/samplesumo-ts/"
WRITE_SCOPE = TASK_PREFIX + "only"
BASE_COMMIT = "56eeb134b740d41d770940bf47bd0f035d73f097"
BRANCH = "swarm/SDK-SAMPLESUMO-TS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
REQUIRED_INTERPRETER = "3.12.16"
VENDOR_NAME = "SampleSumo"
PRODUCT_NAME = "SampleSumo TS"
CONTRACT_SCHEMA_ID = "audio-sdk/samplesumo-ts-readiness-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/samplesumo-ts-readiness-report/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/samplesumo-ts-tool-manifest/0.1"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REQUEST_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
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

# Read-only inputs. source: paths are workspace-relative; sdk: paths are paths
# in this SDK worktree. The mutable shared board is never pinned.
SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
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

CANDIDATE_DOC = "cpp-library/pipeline-validation/playback-speed-candidates.md"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

SOURCE_PHRASES = {
    CANDIDATE_DOC: (
        "| Commercial time-varying actuator | **SampleSumo TS** | Commercial |",
        "Explicitly documents time-varying factor, push/pull, mono/stereo, "
        "desktop/iOS",
        "Pricing/terms not published; procurement",
        "is the commercial option that actually advertises this use case",
        "though pricing is unknown.",
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "Pricing/terms not published; procurement",
    ),
    "audio-benchmark-platform/plan/INVENTORY.md": (
        "| SampleSumo TS | considered | `SDK-SAMPLESUMO-TS` \u00b7 "
        "external-adapter |",
    ),
    PROFILE_SOURCE_REL: (
        "Measure source/output mapping, duration, pitch, transient audibility "
        "and playback buffering.",
        "Include 1\u00d7, rate changes, unfamiliar speech, music, silence, "
        "rebuffer, "
        "drift and the final partial window.",
    ),
}
BOUNDARY_PHRASES = {
    "CONTRACTS.md": (
        "v0 accepts only 16000/1/160 and nonnegative first input sample.",
    ),
    "api/include/audio_sdk/provider_v0.h": (
        "#define AS_SAMPLE_RATE_HZ 16000u",
        "#define AS_CHANNELS 1u",
        "#define AS_FRAME_SAMPLES 160u",
        "float *samples;",
    ),
}

ABSENCE_PROBES = (
    "workspace:data/checkouts/SampleSumo",
    "workspace:data/checkouts/samplesumo-ts",
    "workspace:data/manifests/samplesumo-ts",
    "workspace:data/models/SampleSumoTS",
    "workspace:data/envs/samplesumo-ts",
    "workspace:adapters/samplesumo-ts",
    "worktree:third_party/SampleSumo",
    "worktree:third_party/samplesumo-ts",
    "worktree:docs/task-evidence/samplesumo-ts/runtime",
    "worktree:docs/task-evidence/samplesumo-ts/artifacts",
    "worktree:docs/task-evidence/samplesumo-ts/weights",
    "home:.cache/samplesumo",
    "home:.cache/samplesumo-ts",
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
README_MARKERS = {
    "source": ("<!-- digest-table: source -->",
               "<!-- digest-table: source-end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: boundary-end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}

RATE_REQUIREMENTS = (
    ("RR-01", "Source/output mapping", "blocked",
     "No candidate runtime, source interval or output position exists."),
    ("RR-02", "Duration", "blocked",
     "No candidate output; envelope targets are exact by construction."),
    ("RR-03", "Pitch", "blocked",
     "No candidate audio and no authorized listening result."),
    ("RR-04", "Transient audibility", "blocked",
     "No candidate audio and no transient control result."),
    ("RR-05", "Playback buffering", "blocked",
     "No device, scheduler, fill/flush or deadline measurement."),
    ("RR-06", "1x control", "synthetic_only",
     "Integer identity map 19200 -> 19200; not audio passthrough."),
    ("RR-07", "Rate changes", "synthetic_only",
     "Five integer position maps only; no step or ramp execution."),
    ("RR-08", "Unfamiliar speech", "blocked",
     "No rights-cleared speech cohort or candidate output."),
    ("RR-09", "Music", "blocked",
     "No rights-cleared music and no negative control."),
    ("RR-10", "Silence", "synthetic_only",
     "Empty duration is rejected; no candidate silence behaviour."),
    ("RR-11", "Rebuffer, drift, final partial", "synthetic_only",
     "Position arithmetic only; no playback or buffering."),
    ("RR-12", "Pause/filler and speech preservation", "blocked",
     "No speech, timestamps, policy execution or preservation measure."),
    ("RR-13", "Separate evidence categories", "documented",
     "Synthetic, manifest, source-reported and missing-real classes stay "
     "distinct."),
)

RELEASE_GATES = (
    ("RG-01", "Exact vendor, product, source and runtime identity",
     "Stage an immutable SampleSumo TS release with source or signed binary "
     "identity, byte counts and SHA-256 values, plus published pricing and "
     "licence text; record independent review."),
    ("RG-02", "Pinned offline runtime and clean integration",
     "Provide a locked offline host runtime with platform build, install root, "
     "dependency lock, install digest and no-download proof."),
    ("RG-03", "Permitted scope and caller tool-manifest reference",
     "Supply a reviewed manifest with exact rate/frame/hop/reset/drain geometry, "
     "mono 16 kHz float32 160-sample admission and verified terms."),
    ("RG-04", "Rights, pricing, telemetry and output use",
     "Record procurement approval, licence/evaluation terms, data-handling and "
     "telemetry disclosure, deployment and redistribution grants."),
    ("RG-05", "Absence controls and no substitution",
     "Keep every candidate artifact absent until pinned; prove that hash-"
     "matched placeholders and sibling vendor evidence cannot qualify."),
    ("RG-06", "Rate profile with matched evidence",
     "Run every Rate row on a rights-cleared cohort with separated local-runtime, "
     "vendor-output and vendor-claim results plus controls."),
    ("RG-07", "Timing, resources and listening",
     "Measure pacing, backpressure, memory and actual delivery for the exact "
     "runtime and complete authorized listening or labeled screen."),
    ("RG-08", "Opt-in OFF-by-default intake and release",
     "Open a separate versioned intake with clean-install proof and independent "
     "exact-head review only after all prior gates clear."),
)

BLK_01 = ("BLK-01", "No runnable SDK or source artifact",
          "No SampleSumo TS source tree, release tag, binary, install location, "
          "byte count or SHA-256 is present at any probed path.")
BLK_02 = ("BLK-02", "Pricing and terms unpublished",
          "The only pinned capability row says 'Pricing/terms not published; "
          "procurement'. No licence, evaluation, telemetry, deployment or "
          "output-use text is available.")
BLK_03 = ("BLK-03", "No locked offline runtime",
          "No platform build, dependency lock, interpreter/ABI pin, deterministic "
          "setting or install digest exists for the candidate.")
BLK_04 = ("BLK-04", "No verified 16 kHz mono float32 160-sample geometry",
          "The installed v0 geometry is pinned, but no candidate frame/hop, "
          "rate conversion, reset, drain or push/pull contract is documented or "
          "matched to that geometry.")
BLK_05 = ("BLK-05", "No matched Rate evidence",
          "No rights-cleared input, candidate output, duration, pitch, transient, "
          "preservation, buffering or control result exists.")
BLK_06 = ("BLK-06", "No timing, review or release approval",
          "No device timing, pacing, resource measurement, independent review, "
          "provider intake or release approval exists.")
EXACT_BLOCKERS = (BLK_01, BLK_02, BLK_03, BLK_04, BLK_05, BLK_06)

REQUIRED_ARTIFACTS = (
    ("ART-01", "task-local evidence package", True, True, False),
    ("ART-02", "SampleSumo TS source or signed binary release", False, False, True),
    ("ART-03", "published pricing and licence/terms text", False, False, True),
    ("ART-04", "evaluation entitlement and platform build", False, False, True),
    ("ART-05", "locked offline runtime and dependency lock", False, False, True),
    ("ART-06", "rights-cleared cohort and vendor-processed output", False, False, True),
    ("ART-07", "matched Rate results, timing and independent review", False, False, True),
)

REOPEN_CONDITION = (
    "A caller supplies approved procurement and entitlement, the exact "
    "SampleSumo TS release with verified artifact identity and published terms, "
    "a locked offline runtime, a reviewed caller tool-manifest with 16 kHz mono "
    "float32 160-sample geometry and rate/hop/reset/drain contract, a "
    "rights-cleared cohort with matched Rate evidence and separated "
    "local/vendor/claim results, timing and resource records, and a separate "
    "OFF-by-default provider intake with independent exact-head review. Until "
    "all eight gates clear, this task stays DEFER with no adapter registered."
)

CONTROL_IDS = ("identity_1x", "rate_change", "silence", "final_partial",
               "rebuffer", "drift", "preservation")


# ---------------------------------------------------------------------------
# Canonical bytes and strict JSON.
# ---------------------------------------------------------------------------

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def canonical_report(value: Any) -> tuple[str, str]:
    payload = canonical_bytes(value).decode("ascii")
    return payload, sha256_bytes(payload.encode("ascii"))


def assert_no_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise TypeError("float_at:" + path)
    if isinstance(value, dict):
        for key, item in value.items():
            assert_no_float(item, path + "." + str(key))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_no_float(item, path + "[" + str(index) + "]")


def read_strict_json(path: Path) -> dict:
    return strict_json(path.read_bytes())


def strict_json(payload: bytes) -> dict:
    if not payload or not payload.strip():
        raise ValueError("empty")
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValueError("byte_order_mark")
    text = payload.decode("utf-8")

    def reject_constant(name: str) -> Any:
        raise ValueError("nonfinite:" + name)

    def object_pairs(items: list[tuple[str, Any]]) -> dict:
        output: dict = {}
        for key, value in items:
            if key in output:
                raise ValueError("duplicate_key:" + key)
            output[key] = value
        return output

    document = json.loads(text, object_pairs_hook=object_pairs,
                          parse_constant=reject_constant)
    if not isinstance(document, dict):
        raise ValueError("root_not_object")
    return document


# ---------------------------------------------------------------------------
# Board projection: stable identity only, never the mutable board bytes.
# ---------------------------------------------------------------------------

def board_document() -> dict:
    return read_strict_json(AUDIO_ROOT / BOARD_TASK_ROW)


def board_row_projection(path: Path | None = None) -> dict:
    document = read_strict_json(path) if path else board_document()
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    for row in tasks:
        if isinstance(row, dict) and row.get("id") == TASK:
            return {field: row[field] for field in BOARD_ROW_FIELDS}
    raise ValueError("board_task_row_missing")


def linked_rows() -> list[dict]:
    document = board_document()
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_missing")
    by_id = {row.get("id"): row for row in tasks if isinstance(row, dict)}
    rows: list[dict] = []
    for task_id in LINKED_ROW_IDS:
        row = by_id.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        rows.append({field: row.get(field) for field in BOARD_ROW_FIELDS})
    return rows


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: list[dict]) -> str:
    return object_digest(rows)


def boundary_record() -> dict:
    row = board_row_projection()
    rows = linked_rows()
    return {
        "board_file_pinned": False,
        "linked_row": row,
        "linked_row_sha256": board_row_digest(row),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "linked_row_identity_only": True,
        "mutable_board_fields_gate": False,
        "excluded_mutable_fields": [
            "status", "owner", "claim", "review", "handoff",
            "blocked_reason", "dispatch_priority", "history",
        ],
    }


# ---------------------------------------------------------------------------
# Absence and source-snippet evidence.
# ---------------------------------------------------------------------------

def _probe_path(spec: str) -> Path:
    scope, relative = spec.split(":", 1)
    if scope == "workspace":
        return AUDIO_ROOT / relative
    if scope == "worktree":
        return WORKTREE / relative
    if scope == "home":
        return Path.home() / relative
    raise ValueError("unknown_probe_scope:" + scope)


def absence_summary() -> dict:
    probes: list[dict] = []
    for spec in ABSENCE_PROBES:
        probes.append({"path": spec, "present": _probe_path(spec).exists()})
    present = sum(1 for row in probes if row["present"])
    return {
        "probes": probes,
        "summary": {
            "probe_count": len(probes),
            "present_count": present,
            "all_absent": present == 0,
        },
        "walk": "fixed_probe_list_only",
    }


def snippet_summary() -> dict:
    rows: list[dict] = []
    for relative, phrases in sorted(SOURCE_PHRASES.items()):
        text = (AUDIO_ROOT / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            rows.append({"path": "source:" + relative,
                         "phrase": phrase, "present": phrase in text})
    for relative, phrases in sorted(BOUNDARY_PHRASES.items()):
        text = (WORKTREE / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            rows.append({"path": "sdk:" + relative,
                         "phrase": phrase, "present": phrase in text})
    present = sum(1 for row in rows if row["present"])
    return {
        "rows": rows,
        "snippet_count": len(rows),
        "present_count": present,
        "all_present": present == len(rows),
        "geometry_source": [
            "sdk:CONTRACTS.md",
            "sdk:api/include/audio_sdk/provider_v0.h",
        ],
    }


# ---------------------------------------------------------------------------
# Caller-supplied tool-manifest reference: shape validation only.
# ---------------------------------------------------------------------------

def baseline_manifest() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "request_id": "caller-001",
        "candidate": {
            "name": PRODUCT_NAME,
            "vendor": VENDOR_NAME,
            "source_present": False,
            "runtime_present": False,
            "artifact_present": False,
            "revision": None,
            "license_digest": None,
        },
        "tool": {
            "release": "1.0.0",
            "platform_build": "macos-arm64",
            "install_root": "/opt/samplesumo-ts",
            "artifact_sha256": "aa" * 32,
            "artifact_bytes": 1048576,
            "terms_sha256": "bb" * 32,
            "entitlement": False,
            "telemetry_disclosed": True,
            "no_download": True,
        },
        "format": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "rate_numerator": 4,
            "rate_denominator": 5,
            "time_varying": True,
            "push_pull": True,
        },
        "rights": {
            "pricing_terms_published": True,
            "license_reviewed": True,
            "data_handling_reviewed": True,
            "output_use_permitted": True,
            "claims_qualified": False,
        },
        "controls": ["identity_1x", "silence", "final_partial"],
        "qualifies": False,
    }


MANIFEST_KEYS = {
    "root": {"schema_id", "request_id", "candidate", "tool", "format",
             "rights", "controls", "qualifies"},
    "candidate": {"name", "vendor", "source_present", "runtime_present",
                  "artifact_present", "revision", "license_digest"},
    "tool": {"release", "platform_build", "install_root", "artifact_sha256",
             "artifact_bytes", "terms_sha256", "entitlement",
             "telemetry_disclosed", "no_download"},
    "format": {"sample_rate_hz", "channels", "sample_format", "frame_samples",
               "rate_numerator", "rate_denominator", "time_varying", "push_pull"},
    "rights": {"pricing_terms_published", "license_reviewed",
               "data_handling_reviewed", "output_use_permitted",
               "claims_qualified"},
}


def _exact_keys(document: dict, section: str) -> str | None:
    expected = MANIFEST_KEYS[section]
    if set(document) != expected:
        return section + "_keys"
    return None


def _is_bool(value: Any) -> bool:
    return value is True or value is False


def validate_manifest(document: Any) -> tuple[bool, str]:
    """Validate caller declaration shape. Never resolves a path or loads code."""
    if not isinstance(document, dict):
        return False, "manifest_not_object"
    problem = _exact_keys(document, "root")
    if problem:
        return False, problem
    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return False, "manifest_schema_id"
    if not isinstance(document["request_id"], str) or not REQUEST_ID.match(
            document["request_id"]):
        return False, "request_id_invalid"

    candidate = document["candidate"]
    if not isinstance(candidate, dict):
        return False, "candidate_not_object"
    problem = _exact_keys(candidate, "candidate")
    if problem:
        return False, problem
    if candidate["name"] != PRODUCT_NAME or candidate["vendor"] != VENDOR_NAME:
        return False, "candidate_identity_mismatch"
    for key in ("source_present", "runtime_present", "artifact_present"):
        if not _is_bool(candidate[key]) or candidate[key] is not False:
            return False, "candidate_" + key
    if candidate["revision"] is not None or candidate["license_digest"] is not None:
        return False, "candidate_unpinned_claim"

    tool = document["tool"]
    if not isinstance(tool, dict):
        return False, "tool_not_object"
    problem = _exact_keys(tool, "tool")
    if problem:
        return False, problem
    if not isinstance(tool["release"], str) or not VERSION.match(tool["release"]):
        return False, "tool_release_invalid"
    if not isinstance(tool["platform_build"], str) or not SLUG.match(
            tool["platform_build"]):
        return False, "tool_platform_build_invalid"
    root_path = tool["install_root"]
    if (not isinstance(root_path, str) or not root_path.startswith("/")
            or ".." in root_path or "\\" in root_path
            or any(char.isspace() for char in root_path)
            or len(root_path) > 160):
        return False, "tool_install_root_invalid"
    for key in ("artifact_sha256", "terms_sha256"):
        value = tool[key]
        if not isinstance(value, str) or not HEX64.match(value):
            return False, "tool_" + key
    size = tool["artifact_bytes"]
    if type(size) is not int or not 1 <= size <= 536870912:
        return False, "tool_artifact_bytes"
    for key in ("entitlement", "telemetry_disclosed", "no_download"):
        if not _is_bool(tool[key]):
            return False, "tool_" + key + "_type"
    if tool["telemetry_disclosed"] is not True or tool["no_download"] is not True:
        return False, "tool_disclosure_or_download"

    fmt = document["format"]
    if not isinstance(fmt, dict):
        return False, "format_not_object"
    problem = _exact_keys(fmt, "format")
    if problem:
        return False, problem
    if type(fmt["sample_rate_hz"]) is not int or fmt["sample_rate_hz"] != 16000:
        return False, "format_rate"
    if type(fmt["channels"]) is not int or fmt["channels"] != 1:
        return False, "format_channels"
    if fmt["sample_format"] != "float32":
        return False, "format_sample_format"
    if type(fmt["frame_samples"]) is not int or fmt["frame_samples"] != 160:
        return False, "format_frame"
    for key in ("rate_numerator", "rate_denominator"):
        value = fmt[key]
        if type(value) is not int or not 1 <= value <= 16:
            return False, "format_" + key
    for key in ("time_varying", "push_pull"):
        if not _is_bool(fmt[key]):
            return False, "format_" + key + "_type"

    rights = document["rights"]
    if not isinstance(rights, dict):
        return False, "rights_not_object"
    problem = _exact_keys(rights, "rights")
    if problem:
        return False, problem
    for key in ("pricing_terms_published", "license_reviewed",
                "data_handling_reviewed", "output_use_permitted"):
        if not _is_bool(rights[key]) or rights[key] is not True:
            return False, "rights_" + key
    if (not _is_bool(rights["claims_qualified"])
            or rights["claims_qualified"] is not False):
        return False, "rights_claims_qualified"

    controls = document["controls"]
    if (not isinstance(controls, list) or not 1 <= len(controls) <= 8
            or len(set(map(str, controls))) != len(controls)
            or any(item not in CONTROL_IDS for item in controls)):
        return False, "controls_invalid"
    if (not _is_bool(document["qualifies"])
            or document["qualifies"] is not False):
        return False, "qualifies_must_be_false"
    return True, "accepted_shape_only"


def _mutate(document: dict, path: tuple[str, ...], value: Any) -> dict:
    result = copy.deepcopy(document)
    cursor = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return result


def admission_cases() -> list[tuple[str, dict]]:
    base = baseline_manifest()
    cases: list[tuple[str, dict]] = []
    additions = [
        ("extra_top_level_key", {"unexpected": 1}),
        ("extra_candidate_key", {"candidate": dict(
            base["candidate"], unexpected=1)}),
        ("extra_tool_key", {"tool": dict(base["tool"], unexpected=1)}),
        ("extra_format_key", {"format": dict(base["format"], unexpected=1)}),
        ("extra_rights_key", {"rights": dict(base["rights"], unexpected=1)}),
    ]
    for name, patch in additions:
        document = copy.deepcopy(base)
        document.update(patch)
        cases.append((name, document))

    removals = [
        ("missing_schema_id", ("schema_id",)),
        ("missing_request_id", ("request_id",)),
        ("missing_candidate_section", ("candidate",)),
        ("missing_tool_section", ("tool",)),
        ("missing_format_section", ("format",)),
        ("missing_rights_section", ("rights",)),
        ("missing_controls", ("controls",)),
        ("missing_qualifies", ("qualifies",)),
    ]
    for name, path in removals:
        document = copy.deepcopy(base)
        cursor = document
        for key in path[:-1]:
            cursor = cursor[key]
        del cursor[path[-1]]
        cases.append((name, document))

    changes: list[tuple[str, tuple[str, ...], Any]] = [
        ("bad_schema_id", ("schema_id",), "audio-sdk/other/0.1"),
        ("bad_request_id", ("request_id",), "BAD ID"),
        ("empty_request_id", ("request_id",), ""),
        ("candidate_name_mismatch", ("candidate", "name"), "NeuralATSM"),
        ("vendor_mismatch", ("candidate", "vendor"), "OtherVendor"),
        ("source_claimed_present", ("candidate", "source_present"), True),
        ("runtime_claimed_present", ("candidate", "runtime_present"), True),
        ("artifact_claimed_present", ("candidate", "artifact_present"), True),
        ("revision_claimed", ("candidate", "revision"), "abc123"),
        ("license_digest_claimed", ("candidate", "license_digest"), "cd" * 32),
        ("source_flag_nonbool", ("candidate", "source_present"), "false"),
        ("bad_release", ("tool", "release"), "nightly"),
        ("release_nonstring", ("tool", "release"), 1),
        ("bad_platform_build", ("tool", "platform_build"), "Unknown OS!"),
        ("relative_install_root", ("tool", "install_root"), "opt/samplesumo"),
        ("install_root_traversal", ("tool", "install_root"), "/opt/../etc"),
        ("install_root_whitespace", ("tool", "install_root"), "/opt/sumo ts"),
        ("install_root_backslash", ("tool", "install_root"), "/opt\\sumo"),
        ("install_root_nonstring", ("tool", "install_root"), 7),
        ("bad_artifact_digest", ("tool", "artifact_sha256"), "zz" * 32),
        ("uppercase_artifact_digest", ("tool", "artifact_sha256"), "AA" * 32),
        ("bad_terms_digest", ("tool", "terms_sha256"), "not-a-digest"),
        ("zero_artifact_bytes", ("tool", "artifact_bytes"), 0),
        ("oversized_artifact_bytes", ("tool", "artifact_bytes"), 536870913),
        ("float_artifact_bytes", ("tool", "artifact_bytes"), 1024.0),
        ("entitlement_nonbool", ("tool", "entitlement"), "yes"),
        ("telemetry_undisclosed", ("tool", "telemetry_disclosed"), False),
        ("download_permitted", ("tool", "no_download"), False),
        ("sample_rate_8k", ("format", "sample_rate_hz"), 8000),
        ("stereo_input", ("format", "channels"), 2),
        ("f16_input", ("format", "sample_format"), "float16"),
        ("wrong_frame", ("format", "frame_samples"), 320),
        ("zero_numerator", ("format", "rate_numerator"), 0),
        ("zero_denominator", ("format", "rate_denominator"), 0),
        ("numerator_17", ("format", "rate_numerator"), 17),
        ("denominator_17", ("format", "rate_denominator"), 17),
        ("rate_noninteger", ("format", "rate_numerator"), "4"),
        ("time_varying_nonbool", ("format", "time_varying"), 1),
        ("push_pull_nonbool", ("format", "push_pull"), None),
        ("pricing_unpublished", ("rights", "pricing_terms_published"), False),
        ("licence_unreviewed", ("rights", "license_reviewed"), False),
        ("data_terms_unreviewed", ("rights", "data_handling_reviewed"), False),
        ("output_use_denied", ("rights", "output_use_permitted"), False),
        ("claims_qualified_true", ("rights", "claims_qualified"), True),
        ("controls_empty", ("controls",), []),
        ("controls_duplicate", ("controls",), ["silence", "silence"]),
        ("controls_unknown", ("controls",), ["unknown_control"]),
        ("controls_too_many", ("controls",),
         list(CONTROL_IDS) + ["extra_a", "extra_b"]),
        ("qualifies_true", ("qualifies",), True),
        ("qualifies_nonbool", ("qualifies",), "false"),
    ]
    for name, path, value in changes:
        cases.append((name, _mutate(base, path, value)))
    return cases


def admission_rejections() -> dict:
    cases = admission_cases()
    rejected: list[dict] = []
    accepted: list[dict] = []
    for name, document in cases:
        ok, code = validate_manifest(document)
        if ok:
            accepted.append({"id": name, "code": code})
        else:
            rejected.append({"id": name, "code": code})
    return {
        "cases": len(cases),
        "rejections": rejected,
        "accepted": accepted,
        "all_rejected": not accepted and len(rejected) == len(cases),
        "assets_never_loaded": True,
        "control_qualifies": False,
        "control_id": "synthetic_manifest_shape_control",
        "control_accepted": validate_manifest(baseline_manifest())[0],
        "schema_id": MANIFEST_SCHEMA_ID,
    }


def strict_json_rejections() -> dict:
    samples = [
        ("empty", b""),
        ("whitespace", b"   \n"),
        ("byte_order_mark", b"\xef\xbb\xbf{}"),
        ("nan_constant", b'{"a": NaN}'),
        ("infinity_constant", b'{"a": Infinity}'),
        ("negative_infinity", b'{"a": -Infinity}'),
        ("trailing_data", b'{"a": 1} trailing'),
        ("array_root", b"[1,2,3]"),
        ("duplicate_keys", b'{"a": 1, "a": 2}'),
        ("truncated_object", b'{"a": 1'),
        ("invalid_utf8", b'{"a": "\xff"}'),
    ]
    rejected: list[dict] = []
    for name, payload in samples:
        try:
            strict_json(payload)
        except (ValueError, UnicodeDecodeError) as error:
            rejected.append({"id": name, "code": str(error)})
    return {
        "cases": len(samples),
        "rejections": rejected,
        "all_rejected": len(rejected) == len(samples),
    }


# ---------------------------------------------------------------------------
# Integer Rate position envelope (protocol plumbing only, never audio).
# ---------------------------------------------------------------------------

def mapping_record(source_samples: int, numerator: int,
                   denominator: int) -> dict:
    target = (source_samples * denominator) // numerator
    lines: list[str] = []
    monotone = True
    bounded = True
    previous = -1
    for index in range(target):
        position = (index * numerator) // denominator
        lines.append(str(index) + "," + str(position) + "\n")
        if position < previous:
            monotone = False
        previous = position
        if not 0 <= position < source_samples:
            bounded = False
    digest = sha256_bytes("".join(lines).encode("ascii"))
    return {
        "source_samples": source_samples,
        "numerator": numerator,
        "denominator": denominator,
        "target_samples": target,
        "duration_error_samples": 0,
        "mapping_sha256": digest,
        "monotone": monotone,
        "bounded": bounded,
        "identity_exact": numerator == denominator and target == source_samples,
        "synthesizes_audio": False,
        "not_candidate": True,
    }


ENVELOPE_CASES = (
    ("identity_1x", 1, 1),
    ("speed_up_125", 5, 4),
    ("speed_up_150", 3, 2),
    ("speed_down_080", 4, 5),
    ("speed_down_090", 9, 10),
)


def envelope() -> dict:
    rows: list[dict] = []
    for name, numerator, denominator in ENVELOPE_CASES:
        record = mapping_record(19200, numerator, denominator)
        record["id"] = name
        rows.append(record)
    return {
        "profile": "integer_position_envelope",
        "source_samples": 19200,
        "nanoseconds_per_sample": 62500,
        "case_count": len(rows),
        "cases": rows,
        "identity_exact": all(row["identity_exact"] for row in rows
                              if row["id"] == "identity_1x"),
        "all_monotone": all(row["monotone"] for row in rows),
        "all_bounded": all(row["bounded"] for row in rows),
        "synthesizes_audio": False,
        "not_candidate": True,
        "synthetic_frame": {
            "sample_count": 160,
            "denominator": 128,
            "numerator_formula": "((index * 37) % 201 - 100)",
            "peak_numerator": 100,
            "finite": True,
            "real_audio": False,
        },
    }


# ---------------------------------------------------------------------------
# Canonical contract and report.
# ---------------------------------------------------------------------------

def build_contract() -> dict:
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "depends_on": list(DEPENDS_ON),
        "interpreter": REQUIRED_INTERPRETER,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "write_scope": WRITE_SCOPE,
        "source_reported_identity": {
            "vendor": VENDOR_NAME,
            "product": PRODUCT_NAME,
            "capabilities_reported": [
                "time-varying factor", "push/pull", "mono/stereo",
                "desktop/iOS", "speech transcription",
            ],
            "pricing_terms_published": False,
            "artifact_identity_pinned": False,
            "runnable_as_released": False,
            "scores_are_source_reported_only": True,
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
            "unchanged": True,
        },
        "candidate_geometry_verified": False,
        "exact_blockers": [
            {"id": item[0], "title": item[1], "detail": item[2],
             "status": "open", "qualifies": False}
            for item in EXACT_BLOCKERS
        ],
        "required_artifacts": [
            {"id": item[0], "name": item[1], "present": item[2],
             "verified": item[3], "blocked": item[4]}
            for item in REQUIRED_ARTIFACTS
        ],
        "release_gates": [
            {"id": item[0], "name": item[1], "status": "blocked",
             "qualifies": False, "reopen_condition": item[2]}
            for item in RELEASE_GATES
        ],
        "rate_profile": {
            "profile": PROFILE,
            "profile_satisfied": False,
            "real_results": 0,
            "requirement_rows": [
                {"id": row[0], "name": row[1], "status": row[2],
                 "evidence": row[3], "qualifies": False}
                for row in RATE_REQUIREMENTS
            ],
        },
        "admission_schema": {
            "schema_id": MANIFEST_SCHEMA_ID,
            "fields": sorted(MANIFEST_KEYS["root"]),
            "section_fields": {key: sorted(value)
                               for key, value in MANIFEST_KEYS.items()},
            "control_fields": sorted(CONTROL_IDS),
            "loads_artifacts": False,
            "qualifies": False,
        },
        "scope": {
            "task_local_only": True,
            "write_scope": WRITE_SCOPE,
            "adapter_registered": False,
            "default_changed": False,
            "abi_changed": False,
            "contracts_changed": False,
            "registry_changed": False,
            "shared_build_changed": False,
            "ci_changed": False,
            "downloads": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "release_claim": False,
        },
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "readiness": "blocked",
            "not_qualified": True,
            "all_release_gates_blocked": True,
            "rate_qualified": False,
            "quality_qualified": False,
            "latency_qualified": False,
            "runtime_verified": False,
            "rights_verified": False,
        },
        "boundary": boundary_record(),
        "reopen_condition": REOPEN_CONDITION,
    }
    assert_no_float(contract)
    return contract


def build_report() -> dict:
    contract = build_contract()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "depends_on": list(DEPENDS_ON),
        "interpreter": REQUIRED_INTERPRETER,
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "contract_sha256": object_digest(contract),
        "reopen_condition": REOPEN_CONDITION,
        "boundary": boundary_record(),
        "exact_blockers": copy.deepcopy(contract["exact_blockers"]),
        "required_artifacts": copy.deepcopy(contract["required_artifacts"]),
        "release_gates": copy.deepcopy(contract["release_gates"]),
        "rate_profile": copy.deepcopy(contract["rate_profile"]),
        "source_reported_identity": copy.deepcopy(
            contract["source_reported_identity"]),
        "public_v0_geometry": copy.deepcopy(contract["public_v0_geometry"]),
        "candidate_geometry_verified": False,
        "absence_evidence": absence_summary(),
        "snippet_evidence": snippet_summary(),
        "protocol_envelope": envelope(),
        "admission": admission_rejections(),
        "strict_json": strict_json_rejections(),
        "scope": copy.deepcopy(contract["scope"]),
        "qualification": copy.deepcopy(contract["qualification"]),
        "evidence_classes": {
            "local_runtime_result": "empty: no runtime present or executed",
            "vendor_output_scoring": "empty: no output bundle, scorer or score",
            "vendor_claim": "empty: source-reported capability text only",
            "synthetic_manifest_control": (
                "present, qualifies=false, not vendor evidence"),
            "integer_envelope": "present, qualifies=false, no audio",
            "peer_vendor_evidence": "not inherited or pooled",
        },
        "non_claims": [
            "No SampleSumo TS source, binary, SDK, key, runtime or asset is "
            "present, downloaded, imported, linked or executed.",
            "No real audio, corpus, listening, device timing, pacing or "
            "benchmark measurement exists.",
            "No rate, duration, pitch, transient, preservation or quality "
            "result is claimed.",
            "No provider, descriptor, registry, default, installed v0, public "
            "ABI, contract, shared build or CI path is changed.",
        ],
    }
    assert_no_float(report)
    return report


# ---------------------------------------------------------------------------
# README digest tables.
# ---------------------------------------------------------------------------

def _expected_rows(section: str) -> list[tuple[str, str, int | None]]:
    rows: list[tuple[str, str, int | None]] = []
    if section == "source":
        for relative, _digest in sorted(SOURCE_PINS.items()):
            rows.append(("source:" + relative,
                         sha256_file(AUDIO_ROOT / relative), None))
    elif section == "boundary":
        for relative, _digest in sorted(BOUNDARY_PINS.items()):
            rows.append(("sdk:" + relative,
                         sha256_file(WORKTREE / relative), None))
    elif section == "artifacts":
        for name in sorted(EXPECTED_DIR_FILES - ARTIFACT_TABLE_EXCLUDED):
            path = HERE / name
            rows.append((name, sha256_file(path), path.stat().st_size))
    else:
        raise ValueError("unknown_section:" + section)
    return rows


def _render_table(section: str,
                  rows: list[tuple[str, str, int | None]]) -> str:
    lines: list[str] = []
    if section == "artifacts":
        lines.append("| Path | SHA-256 | Bytes |")
        lines.append("| --- | --- | ---: |")
    for name, digest, size in rows:
        if size is None:
            lines.append("| `" + name + "` | `" + digest + "` |")
        else:
            lines.append("| `" + name + "` | `" + digest + "` | " +
                         str(size) + " |")
    return "\n".join(lines)


def update_readme_tables(text: str) -> str:
    result = text
    for section, (start, end) in README_MARKERS.items():
        if result.count(start) != 1 or result.count(end) != 1:
            raise ValueError("readme_marker_count:" + section)
        head, remainder = result.split(start, 1)
        _old, tail = remainder.split(end, 1)
        table = _render_table(section, _expected_rows(section))
        result = head + start + "\n" + table + "\n" + end + tail
    return result


def readme_table_rows(text: str, section: str) -> list[tuple[str, str, int | None]]:
    start, end = README_MARKERS[section]
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError("readme_marker_count:" + section)
    body = text.split(start, 1)[1].split(end, 1)[0]
    rows: list[tuple[str, str, int | None]] = []
    for line in body.splitlines():
        match = re.match(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|"
                         r"(?: ([0-9]+) \|)?$", line)
        if match:
            size = int(match.group(3)) if match.group(3) else None
            rows.append((match.group(1), match.group(2), size))
    return rows


def readme_table_errors(text: str) -> list[str]:
    errors: list[str] = []
    for section in README_MARKERS:
        try:
            observed = readme_table_rows(text, section)
        except ValueError as error:
            errors.append(str(error))
            continue
        expected = _expected_rows(section)
        if observed != expected:
            errors.append("readme_" + section + "_table_mismatch")
    return errors


# ---------------------------------------------------------------------------
# Task-local git scope: newest merge-base, origin/main then main.
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
        if result.returncode != 0 or not HEX40.match(base):
            continue
        if best is None:
            best = base
        elif best != base and _git(worktree, "merge-base", "--is-ancestor",
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
