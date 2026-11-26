# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Stdlib-only deterministic reference for SDK-PHONETIC-LATENT-MAPPING DEFER evidence.

This package records phonetic/latent mapping as an underspecified voice-transform
method family. It does not import, build, execute, download, benchmark, or
qualify any encoder, mapper, decoder, vocoder, runtime, or model. All outputs
are synthetic-contract controls or metadata; no result qualifies.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-PHONETIC-LATENT-MAPPING"
TITLE = "Phonetic/latent mapping"
COMPONENT_ID = "phonetic-latent-mapping"
MODE = "feasibility"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
BASE_COMMIT = "ad284fbf3100b646bb3d395262212159512c613f"
BRANCH = "swarm/SDK-PHONETIC-LATENT-MAPPING"
REVIEWER = "reviewer-PHONETIC-LATENT-MAPPING"
CONTRACT_ID = "audio-sdk/phonetic-latent-mapping/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
TASK_PREFIX = "docs/task-evidence/phonetic-latent-mapping/"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

BOARD_ROW_FIELDS = (
    "id",
    "title",
    "repository",
    "mode",
    "depends_on",
    "component",
    "evidence",
)

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

SIBLING_PINS = {
    "docs/task-evidence/hubert-conversion-encoder/report.json":
        "fd208807348762a582a20f2a236fc6f56b5583953bff3845cd63f3f7ab4a17c1",
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/report.json":
        "0a661101a938600bf26a07b18b6ae0d1fa2c94e6db6394d169dc052b8b3d19ef",
    "docs/task-evidence/tokan/report.json":
        "6cd151f2178d95d6e5c98b389a9b71f80097a01efaaa92a4450a7c26db1bcd13",
}

LOCAL_PIN_FILES = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
    "run.py",
)

PROFILE_PHRASES = [
    "permitted input and target references",
    "task and language/speaker groups",
    "text and semantic content",
    "identity/similarity",
    "naturalness",
    "alignment, first-output/tail timing",
    "exact target condition",
    "Consent, reference availability and output use",
]

PRESENCE_PROBES = [
    "third_party/phonetic-latent-mapping",
    "data/checkouts/phonetic-latent-mapping",
    "data/models/phonetic-latent-mapping",
    "data/runtimes/phonetic-latent-mapping",
    "research/phonetic-latent-mapping",
    "docs/task-evidence/phonetic-latent-mapping/runtime",
    "docs/task-evidence/phonetic-latent-mapping/weights",
]

FORBIDDEN_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".m4a", ".aac", ".opus",
    ".onnx", ".pt", ".pth", ".bin", ".safetensors", ".npz",
    ".so", ".dylib", ".dll", ".a", ".tar", ".gz", ".zip", ".7z",
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[A-Za-z0-9.+-]*)?$")
FRACTION = re.compile(r"^(-?[0-9]+)(?:/([1-9][0-9]*))?$")
FRAME_SAMPLES = 160


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_strict_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=_reject_float)


def _reject_float(value: str) -> Any:
    raise ValueError("float_forbidden:" + value)


def _no_floats(value: Any) -> None:
    if type(value) is float:
        raise ValueError("float_forbidden")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non_string_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def parse_fraction(raw: Any, label: str, minimum: Fraction, maximum: Fraction) -> Fraction:
    if not isinstance(raw, str):
        raise ValueError(label + "_not_string")
    match = FRACTION.match(raw)
    if not match:
        raise ValueError(label + "_malformed")
    numerator = int(match.group(1))
    denominator = int(match.group(2) or "1")
    value = Fraction(numerator, denominator)
    if value < minimum or value > maximum:
        raise ValueError(label + "_out_of_range")
    return value


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def board_row_projection(board_path: Path) -> dict[str, Any]:
    rows = json.loads(board_path.read_text(encoding="utf-8"))
    tasks = rows.get("tasks", rows if isinstance(rows, list) else [])
    for row in tasks:
        if row.get("id") == TASK:
            projection = {field: row[field] for field in BOARD_ROW_FIELDS if field in row}
            projection["depends_on"] = list(row.get("depends_on", []))
            projection["evidence"] = list(row.get("evidence", []))
            return projection
    raise ValueError("linked_row_missing")


def board_row_digest(projection: dict[str, Any]) -> str:
    return object_digest(projection)


def verify_pins() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source = {}
    for relative, expected in SOURCE_PINS.items():
        actual = sha256_file(AUDIO_ROOT / relative)
        source[relative] = {"sha256": expected, "actual": actual, "verified": actual == expected}
    boundary = {}
    for relative, expected in BOUNDARY_PINS.items():
        actual = sha256_file(WORKTREE / relative)
        boundary[relative] = {"sha256": expected, "actual": actual, "verified": actual == expected}
    sibling = {}
    for relative, expected in SIBLING_PINS.items():
        actual = sha256_file(WORKTREE / relative)
        sibling[relative] = {"sha256": expected, "actual": actual, "verified": actual == expected}
    return source, boundary, sibling


# ---------------------------------------------------------------------------
# Provenance / presence
# ---------------------------------------------------------------------------

def candidate_note_probe() -> dict[str, Any]:
    matrix = AUDIO_ROOT / "research/voice-enhancement-20261101/candidate_matrix.csv"
    space = AUDIO_ROOT / "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"
    trials = AUDIO_ROOT / "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md"
    matrix_text = matrix.read_text(encoding="utf-8")
    space_text = space.read_text(encoding="utf-8")
    trials_text = trials.read_text(encoding="utf-8")
    row = None
    for line in matrix_text.splitlines():
        if line.startswith("Voice transformation,Phonetic/latent mapping,"):
            row = line
            break
    return {
        "candidate_matrix_row": row,
        "candidate_matrix_path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "candidate_matrix_sha256": sha256_file(matrix),
        "space_report_path": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "space_report_sha256": sha256_file(space),
        "space_statement_present": "Phonetic/latent mapping | researched but not run" in space_text,
        "trials_report_path": "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md",
        "trials_report_sha256": sha256_file(trials),
        "trials_statement_present": "Phonetic/latent mapping | No specified encoder→mapper→decoder, checkpoint or target identity." in trials_text,
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
        "method_family_underspecified": True,
        "frozen_encoder_mapper_decoder_present": False,
        "checkpoint_present": False,
        "target_identity_present": False,
        "runtime_present": False,
        "rights_reviewed": False,
        "not_reproduced_here": True,
    }


def source_presence() -> dict[str, Any]:
    probes = {probe: (AUDIO_ROOT / probe).exists() for probe in PRESENCE_PROBES}
    note = candidate_note_probe()
    present = [name for name, exists in probes.items() if exists]
    exact_present = any(probes.values())
    return {
        "admitted": False,
        "candidate_note_present": note["candidate_matrix_row"] is not None,
        "method_family_underspecified": True,
        "encoder_present": False,
        "mapper_present": False,
        "decoder_or_vocoder_present": False,
        "frozen_checkpoint_present": False,
        "runtime_present": exact_present,
        "source_tree_present": exact_present,
        "weights_present": False,
        "pinned_manifest_present": False,
        "pinned_license_text_present": False,
        "pinned_build_present": False,
        "rights_cleared_cohort_present": False,
        "target_identity_present": False,
        "target_audio_present": False,
        "listening_record_present": False,
        "device_timing_record_present": False,
        "measured_trace_present": False,
        "exact_licensed_source_weights_runtime_present": False,
        "download_attempted": False,
        "network_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "audio_played": False,
        "benchmark_run": False,
        "qualifies": False,
        "presence_is_not_admission": True,
        "probe_scope": "project workspace only; no OS install or network lookup",
        "presence_probes": list(PRESENCE_PROBES),
        "present_probes": present,
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic controls (not evidence)
# ---------------------------------------------------------------------------

def _synthetic_frame(seed: int = 0x12345678) -> list[float]:
    state = seed & 0x7FFFFFFF
    values: list[float] = []
    for _ in range(FRAME_SAMPLES):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        sample = ((state >> 8) % 65536) - 32768
        values.append(sample / 32768.0)
    return values


def validate_frame(samples: Any) -> dict[str, Any]:
    if not isinstance(samples, list):
        raise ValueError("frame_not_list")
    if len(samples) != FRAME_SAMPLES:
        raise ValueError("frame_length")
    peak = 0
    for value in samples:
        if type(value) is bool:
            raise ValueError("frame_bool")
        if not isinstance(value, (int, float)):
            raise ValueError("frame_non_numeric")
        if not math.isfinite(value):
            raise ValueError("frame_nonfinite")
        if abs(value) > 1.0:
            raise ValueError("frame_out_of_range")
        quantised = int(round(float(value) * 32768))
        quantised = max(-32768, min(32767, quantised))
        peak = max(peak, abs(quantised))
    payload = struct.pack("<" + "f" * FRAME_SAMPLES, *[float(v) for v in samples])
    return {
        "frame_samples": FRAME_SAMPLES,
        "peak_int16": peak,
        "digest_sha256": hashlib.sha256(payload).hexdigest(),
        "finite": True,
        "qualifies": False,
    }


def frame_control() -> dict[str, Any]:
    frame = _synthetic_frame()
    accepted = validate_frame(frame)

    def replaced(index: int, value: Any) -> list[Any]:
        candidate = list(frame)
        candidate[index] = value
        return candidate

    cases = [
        ("nan", replaced(0, float("nan")), "frame_nonfinite"),
        ("positive_infinity", replaced(0, float("inf")), "frame_nonfinite"),
        ("negative_infinity", replaced(0, float("-inf")), "frame_nonfinite"),
        ("boolean", replaced(0, True), "frame_bool"),
        ("string", replaced(0, "0.0"), "frame_non_numeric"),
        ("none", replaced(0, None), "frame_non_numeric"),
        ("short_159", frame[:-1], "frame_length"),
        ("long_161", frame + [0.0], "frame_length"),
        ("empty", [], "frame_length"),
        ("out_of_range", replaced(0, 8.5), "frame_out_of_range"),
        ("nested", replaced(0, [0.0]), "frame_non_numeric"),
        ("not_list", "frame", "frame_not_list"),
    ]
    rejected = []
    for case_id, candidate, expected in cases:
        try:
            validate_frame(candidate)
        except ValueError as error:
            actual = str(error)
            rejected.append({
                "id": case_id, "status": "rejected" if actual == expected else "wrong_code",
                "code": actual, "expected_code": expected, "qualifies": False, "state_unchanged": True,
            })
        else:
            rejected.append({
                "id": case_id, "status": "unexpectedly_admitted", "code": "",
                "expected_code": expected, "qualifies": False, "state_unchanged": False,
            })
    rejected.sort(key=lambda row: row["id"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "deterministic frame validation and finite-range rejection",
        "accepted": {**accepted, "qualifies": False},
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for r in rejected if r["status"] == "rejected"),
            "all_rejected": all(r["status"] == "rejected" for r in rejected),
            "all_codes_match": all(r["code"] == r["expected_code"] for r in rejected),
            "qualifying_results": 0, "audio_read": False, "audio_written": False, "network_used": False,
        },
        "qualifies": False,
    }


def _rms(values: list[float]) -> float:
    return math.sqrt(sum(v * v for v in values) / len(values))


def gate_control() -> dict[str, Any]:
    frame = _synthetic_frame()
    same = _synthetic_frame()
    other = _synthetic_frame(0x76543210)
    identity = same == frame
    distinct = other != frame
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "deterministic synthetic frame identity/control only; no phonetic mapping, no model, no audio transform",
        "frame": frame_control(),
        "identity_control": {
            "same_seed_equal": identity,
            "different_seed_distinct": distinct,
            "frame_digest": hashlib.sha256(struct.pack("<" + "f" * FRAME_SAMPLES, *frame)).hexdigest(),
            "other_digest": hashlib.sha256(struct.pack("<" + "f" * FRAME_SAMPLES, *other)).hexdigest(),
            "rms_q32768": int(round(_rms(frame) * 32768)),
            "qualifies": False,
        },
        "summary": {
            "qualifying_results": 0,
            "runtime_imported": False,
            "audio_read": False,
            "audio_played": False,
            "pitch_measured": False,
            "network_used": False,
            "candidate_executed": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Admission controls
# ---------------------------------------------------------------------------

def _exact_keys(value: Any, fields: tuple[str, ...], label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(label + "_not_object")
    if set(value) != set(fields):
        raise ValueError(label + "_fields")
    return value


def _hex(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.match(value):
        raise ValueError(label + "_malformed")
    return value


def _slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise ValueError(label)
    return value


MANIFEST_FIELDS = (
    "schema_id", "run_id", "candidate_revision", "license_id", "license_sha256",
    "source_sha256", "weights_sha256", "runtime_sha256", "rights", "cohort",
    "target", "controls", "runtime",
)
RIGHTS_FIELDS = (
    "license_reviewed", "weights_terms_reviewed", "commercial_use_approved",
    "derived_output_approved", "redistribution_approved", "consent_recorded",
)
COHORT_FIELDS = ("id", "sha256", "sample_rate_hz", "channels", "sample_count")
TARGET_FIELDS = ("id", "sha256", "speaker_id", "language", "consent_recorded")
CONTROL_FIELDS = ("id", "kind", "passes")
RUNTIME_FIELDS = (
    "automation", "automation_version", "deterministic", "offline", "host_os", "host_arch",
)
SCHEMA_MANIFEST_ID = "audio-sdk/phonetic-latent-mapping/admission/0.1"
HOST_OSES = {"linux", "macos", "windows"}
HOST_ARCHES = {"arm64", "x86_64"}
AUTOMATIONS = {"none", "cmake-ctest", "custom"}
LICENSES = {"MIT", "Apache-2.0", "BSD-3-Clause"}
CONTROL_KINDS = {
    "identity", "rights", "cohort", "target", "semantic", "timing",
}


def validate_manifest(manifest: Any) -> dict[str, Any]:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != SCHEMA_MANIFEST_ID:
        raise ValueError("manifest_schema_id")
    _slug(root["run_id"], "run_id")
    _hex(root["candidate_revision"], "candidate_revision", re.compile(r"^[0-9a-f]{40}$"))
    if root["license_id"] not in LICENSES:
        raise ValueError("license_id")
    for field in ("license_sha256", "source_sha256", "weights_sha256", "runtime_sha256"):
        _hex(root[field], field, HEX64)

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS:
        if rights[field] is not True:
            raise ValueError("rights_" + field)

    cohort = _exact_keys(root["cohort"], COHORT_FIELDS, "cohort")
    _slug(cohort["id"], "cohort_id")
    _hex(cohort["sha256"], "cohort_sha256", HEX64)
    if cohort["sample_rate_hz"] != 16000:
        raise ValueError("cohort_sample_rate_hz")
    if cohort["channels"] != 1:
        raise ValueError("cohort_channels")
    if type(cohort["sample_count"]) is not int or cohort["sample_count"] <= 0 or cohort["sample_count"] > 1_000_000_000:
        raise ValueError("cohort_sample_count")

    target = _exact_keys(root["target"], TARGET_FIELDS, "target")
    _slug(target["id"], "target_id")
    _hex(target["sha256"], "target_sha256", HEX64)
    _slug(target["speaker_id"], "target_speaker_id")
    _slug(target["language"], "target_language")
    if target["consent_recorded"] is not True:
        raise ValueError("target_consent_recorded")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["automation"] not in AUTOMATIONS:
        raise ValueError("runtime_automation")
    if not isinstance(runtime["automation_version"], str) or not SEMVER.match(runtime["automation_version"]):
        raise ValueError("runtime_automation_version")
    if runtime["host_os"] not in HOST_OSES:
        raise ValueError("runtime_host_os")
    if runtime["host_arch"] not in HOST_ARCHES:
        raise ValueError("runtime_host_arch")
    if runtime["deterministic"] is not True:
        raise ValueError("runtime_deterministic")
    if runtime["offline"] is not True:
        raise ValueError("runtime_offline")

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("controls_count")
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for entry in controls:
        row = _exact_keys(entry, CONTROL_FIELDS, "control")
        _slug(row["id"], "control_id")
        if row["id"] in seen_ids:
            raise ValueError("control_id_duplicate")
        seen_ids.add(row["id"])
        if row["kind"] not in CONTROL_KINDS:
            raise ValueError("control_kind")
        if row["kind"] in seen_kinds:
            raise ValueError("control_kind_duplicate")
        seen_kinds.add(row["kind"])
        if row["passes"] is not True:
            raise ValueError("control_not_passed")

    return {
        "admitted": True,
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "run_id": root["run_id"],
        "mapping_digest": object_digest({"cohort": cohort, "target": target}),
    }


def _base_manifest() -> dict[str, Any]:
    def syn(name: str) -> str:
        return hashlib.sha256(("synthetic:" + name).encode("ascii")).hexdigest()
    return {
        "schema_id": SCHEMA_MANIFEST_ID,
        "run_id": "synthetic-schema-control",
        "candidate_revision": "0" * 40,
        "license_id": "MIT",
        "license_sha256": syn("license"),
        "source_sha256": syn("source"),
        "weights_sha256": syn("weights"),
        "runtime_sha256": syn("runtime"),
        "rights": {field: True for field in RIGHTS_FIELDS},
        "cohort": {
            "id": "synthetic-cohort",
            "sha256": syn("cohort"),
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_count": 16000,
        },
        "target": {
            "id": "synthetic-target",
            "sha256": syn("target"),
            "speaker_id": "synthetic-speaker",
            "language": "en-us",
            "consent_recorded": True,
        },
        "controls": [
            {"id": "c-identity", "kind": "identity", "passes": True},
            {"id": "c-rights", "kind": "rights", "passes": True},
            {"id": "c-cohort", "kind": "cohort", "passes": True},
            {"id": "c-target", "kind": "target", "passes": True},
            {"id": "c-semantic", "kind": "semantic", "passes": True},
            {"id": "c-timing", "kind": "timing", "passes": True},
        ],
        "runtime": {
            "automation": "none",
            "automation_version": "0.0.0",
            "deterministic": True,
            "offline": True,
            "host_os": "linux",
            "host_arch": "x86_64",
        },
    }


def _mutations() -> list[tuple[str, str, Any]]:
    def setter(path: tuple[Any, ...], value: Any):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply
    def deleter(path: tuple[str, ...]):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            del target[path[-1]]
        return apply
    return [
        ("manifest_missing_rights", "manifest_fields", deleter(("rights",))),
        ("manifest_unknown_field", "manifest_fields", setter(("extra",), True)),
        ("manifest_schema", "manifest_schema_id", setter(("schema_id",), "other")),
        ("run_id", "run_id", setter(("run_id",), "Bad Id")),
        ("candidate_revision_short", "candidate_revision_malformed", setter(("candidate_revision",), "a" * 39)),
        ("license_id", "license_id", setter(("license_id",), "Proprietary")),
        ("license_sha", "license_sha256_malformed", setter(("license_sha256",), "z" * 64)),
        ("source_sha", "source_sha256_malformed", setter(("source_sha256",), "z" * 64)),
        ("weights_sha", "weights_sha256_malformed", setter(("weights_sha256",), "z" * 64)),
        ("runtime_sha", "runtime_sha256_malformed", setter(("runtime_sha256",), "z" * 64)),
        ("rights_not_reviewed", "rights_license_reviewed", setter(("rights", "license_reviewed"), False)),
        ("rights_no_consent", "rights_consent_recorded", setter(("rights", "consent_recorded"), False)),
        ("rights_unknown_field", "rights_fields", setter(("rights", "extra"), True)),
        ("cohort_id", "cohort_id", setter(("cohort", "id"), "Bad Id")),
        ("cohort_sha", "cohort_sha256_malformed", setter(("cohort", "sha256"), "x" * 64)),
        ("cohort_rate", "cohort_sample_rate_hz", setter(("cohort", "sample_rate_hz"), 48000)),
        ("cohort_channels", "cohort_channels", setter(("cohort", "channels"), 2)),
        ("cohort_samples", "cohort_sample_count", setter(("cohort", "sample_count"), 0)),
        ("target_sha", "target_sha256_malformed", setter(("target", "sha256"), "x" * 64)),
        ("target_speaker", "target_speaker_id", setter(("target", "speaker_id"), "Bad Speaker")),
        ("target_language", "target_language", setter(("target", "language"), "Bad Language")),
        ("target_consent", "target_consent_recorded", setter(("target", "consent_recorded"), False)),
        ("runtime_automation", "runtime_automation", setter(("runtime", "automation"), "manual")),
        ("runtime_automation_version", "runtime_automation_version", setter(("runtime", "automation_version"), "bad")),
        ("runtime_host_os", "runtime_host_os", setter(("runtime", "host_os"), "ios")),
        ("runtime_host_arch", "runtime_host_arch", setter(("runtime", "host_arch"), "riscv")),
        ("runtime_deterministic", "runtime_deterministic", setter(("runtime", "deterministic"), False)),
        ("runtime_offline", "runtime_offline", setter(("runtime", "offline"), False)),
        ("controls_missing", "controls_count", lambda m: m["controls"].pop()),
        ("controls_duplicate_kind", "control_kind_duplicate", setter(("controls", 1, "kind"), "identity")),
        ("controls_duplicate_id", "control_id_duplicate", setter(("controls", 1, "id"), "c-identity")),
        ("controls_unknown_kind", "control_kind", setter(("controls", 0, "kind"), "unknown")),
        ("controls_not_passed", "control_not_passed", setter(("controls", 0, "passes"), False)),
    ]


def admission_controls() -> dict[str, Any]:
    base = _base_manifest()
    control = validate_manifest(base)
    rejected = []
    for case_id, code, mutate in _mutations():
        candidate = json.loads(json.dumps(base))
        mutate(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            actual = str(error)
            rejected.append({
                "id": case_id, "status": "rejected" if actual == code else "wrong_code",
                "code": actual, "expected_code": code, "qualifies": False, "state_unchanged": True,
            })
        else:
            rejected.append({
                "id": case_id, "status": "unexpectedly_admitted", "code": "",
                "expected_code": code, "qualifies": False, "state_unchanged": False,
            })
    rejected.sort(key=lambda row: row["id"])
    return {
        "control": {
            "id": "synthetic_schema_control", "accepted": True, "admitted": True,
            "qualifies": False, "evidence_class": control["evidence_class"],
            "run_id": control["run_id"], "mapping_digest": control["mapping_digest"],
        },
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for r in rejected if r["status"] == "rejected"),
            "all_rejected": all(r["status"] == "rejected" for r in rejected),
            "all_codes_match": all(r["code"] == r["expected_code"] for r in rejected),
            "accepted_schema_controls": 1, "qualifying_results": 0,
            "state_advanced_on_rejection": False, "runtime_imported": False,
            "audio_read": False, "audio_played": False, "network_used": False,
        },
    }


# ---------------------------------------------------------------------------
# Contract / report
# ---------------------------------------------------------------------------

def _scope() -> dict[str, Any]:
    return {
        "task_local_only": True, "directory": TASK_PREFIX,
        "provider_registration": False, "descriptor_registry_change": False,
        "installed_v0_behavior_change": False, "public_api_abi_change": False,
        "shared_build_or_ci_change": False, "default_selected": False,
        "benchmark_claim": False, "release_claim": False,
        "network_used": False, "download_attempted": False,
        "runtime_imported": False, "runtime_built": False, "runtime_executed": False,
        "audio_read": False, "audio_played": False, "listening_conducted": False,
        "device_timing_measured": False, "benchmark_run": False,
        "real_corpus_or_weights": False,
    }


def _boundary() -> dict[str, Any]:
    return {
        "installed_v0_geometry": {
            "sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160, "unchanged": True,
        },
        "provider_or_abi_change": False, "descriptor_or_registry_change": False,
        "default_change": False, "shared_build_or_ci_change": False,
        "board_or_handoff_change": False, "external_assets_copied": False,
    }


def _non_claims() -> list[str]:
    return [
        "No result in this package is a qualification, benchmark or release.",
        "Phonetic/latent mapping is treated as an underspecified method family, not an admitted implementation.",
        "No encoder, mapper, decoder, vocoder, checkpoint, runtime, or converted audio is present, loaded, executed, or simulated.",
        "No rights-cleared input/target/reference corpus, consent record, or output-use grant is present.",
        "No identity/similarity, naturalness, semantic, intelligibility, timing, listening, device, or benchmark measurement was made.",
        "No provider, descriptor, registry, default, installed-v0, ABI, shared-build, CI, board, or handoff file is changed.",
        "No missing result qualifies anything.",
    ]


def _required_results() -> dict[str, bool]:
    return {
        "method_family_frozen": False,
        "exact_source_revision_pinned": False,
        "exact_weights_and_runtime_pinned": False,
        "rights_and_consent_reviewed": False,
        "rights_cleared_cohort_present": False,
        "reference_execution_present": False,
        "voice_profile_measured": False,
        "target_device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def _required_artifacts() -> list[dict[str, Any]]:
    presence = source_presence()
    return [
        {"id": "A01", "name": "frozen method identity: encoder/mapper/decoder/vocoder and exact revision", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-01"},
        {"id": "A02", "name": "pinned checkpoint/weights with file names, byte counts and SHA-256", "present": presence["frozen_checkpoint_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-02"},
        {"id": "A03", "name": "pinned offline runtime and deterministic execution recipe", "present": presence["runtime_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-03"},
        {"id": "A04", "name": "rights-cleared input, target-reference, consent and output-use records", "present": presence["rights_cleared_cohort_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-04"},
        {"id": "A05", "name": "reproduced deterministic converted outputs and exact metadata", "present": presence["measured_trace_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-05"},
        {"id": "A06", "name": "voice-profile measurements: semantic, identity/similarity, naturalness, timing", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-05"},
        {"id": "A07", "name": "target-device timing, memory and callback suitability evidence", "present": presence["device_timing_record_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-06"},
        {"id": "A08", "name": "independent listening or labeled screen and negative controls", "present": presence["listening_record_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-06"},
        {"id": "A09", "name": "separate opt-in provider intake, OFF default, and release review", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-07"},
    ]


def _exact_blockers() -> list[dict[str, Any]]:
    return [
        {"id": "BLK-01", "artifact_id": "A01", "status": "open", "qualifies": False,
         "missing": "Method family is underspecified: no frozen encoder, mapper, decoder/vocoder, target identity, or exact revision is recorded.",
         "required_action": "Freeze the exact encoder-mapper-decoder/vocoder system, target identity/accent, revision, and license terms."},
        {"id": "BLK-02", "artifact_id": "A02", "status": "open", "qualifies": False,
         "missing": "No checkpoint, weight file, config, or asset manifest with byte counts and SHA-256 is present.",
         "required_action": "Stage exact checkpoints/configs with immutable revision, byte counts, and SHA-256; review weight and dependency terms."},
        {"id": "BLK-03", "artifact_id": "A03", "status": "open", "qualifies": False,
         "missing": "No pinned offline runtime, lockfile, or deterministic execution recipe is present.",
         "required_action": "Provide a locked offline runtime and exact deterministic execution recipe with clean-room install proof."},
        {"id": "BLK-04", "artifact_id": "A04", "status": "open", "qualifies": False,
         "missing": "No rights-cleared input/target-reference cohort, consent, or output-use/redistribution decision is present.",
         "required_action": "Provide digest-pinned rights-cleared inputs/targets, consent, and output-use/redistribution decisions."},
        {"id": "BLK-05", "artifact_id": "A05", "status": "open", "qualifies": False,
         "missing": "No deterministic converted outputs or voice-profile measurements exist.",
         "required_action": "Reproduce deterministic outputs and measure semantic content, identity/similarity, naturalness, alignment, and timing on the frozen system."},
        {"id": "BLK-06", "artifact_id": "A07", "status": "open", "qualifies": False,
         "missing": "No target-device timing, memory, callback-suitability, listening, or labeled-screen evidence exists.",
         "required_action": "Measure target-device timing/resources and complete authorized listening or a labeled screen with negative controls."},
        {"id": "BLK-07", "artifact_id": "A09", "status": "open", "qualifies": False,
         "missing": "No separate opt-in provider intake, OFF-default boundary, or independent release review exists.",
         "required_action": "Open a separate OFF-by-default intake with clean-install proof and independent exact-head review after prior gates clear."},
    ]


def _voice_profile_rows() -> list[dict[str, Any]]:
    rows = [
        ("VOICE-01", "permitted input and target references", "No rights-cleared input or target reference is staged."),
        ("VOICE-02", "task and language/speaker groups", "No cohort, language/speaker groups, or task labels are staged."),
        ("VOICE-03", "text and semantic content", "No converted output or semantic/content evaluation exists."),
        ("VOICE-04", "identity/similarity", "No target identity, speaker similarity, or identity-preservation measurement exists."),
        ("VOICE-05", "naturalness", "No naturalness or listening/labeled screen evidence exists."),
        ("VOICE-06", "alignment, first-output/tail timing", "No runtime output, alignment, or timing measurement exists."),
        ("VOICE-07", "exact target condition", "No frozen target condition, accent, or voice identity is specified."),
        ("VOICE-08", "consent, reference availability and output use", "No consent, reference availability, or output-use decision is recorded."),
    ]
    return [{"id": rid, "requirement": req, "status": "blocked", "qualifies": False, "evidence": ev} for rid, req, ev in rows]


def _release_gates(projection: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        ("RG-01", "frozen method identity and source pin", "Exact encoder-mapper-decoder/vocoder revision, license/notice, and target identity."),
        ("RG-02", "pinned checkpoints and offline runtime", "Exact checkpoints/configs, byte counts/SHA-256, locked runtime, and deterministic recipe."),
        ("RG-03", "rights, consent and cohort", "Rights-cleared input/target cohorts, consent, output-use, and redistribution decisions."),
        ("RG-04", "deterministic reference execution", "Reproducible converted outputs with exact metadata and deterministic reruns."),
        ("RG-05", "voice semantic and identity quality", "Semantic/content, identity/similarity, and naturalness measurements on frozen cohorts."),
        ("RG-06", "alignment and timing", "Alignment, first-output/tail timing, and final-output validity."),
        ("RG-07", "target-device and listening evidence", "Target-device timing/memory/callback suitability and authorized listening/labeled screen."),
        ("RG-08", "opt-in intake and release review", "Separate OFF-by-default provider intake, clean-install proof, and independent exact-head review."),
    ]
    return [{"id": gid, "title": title, "status": "blocked", "qualifies": False, "reopen_condition": cond, "linked_row": dict(projection)} for gid, title, cond in rows]


def _reproduction() -> dict[str, Any]:
    return {
        "python": "3.12 or newer, standard library only",
        "commands": [
            "export PYTHONDONTWRITEBYTECODE=1",
            "python3 run.py all",
            "python3 -m unittest -v test_reference.py",
            "python3 verify.py",
        ],
        "repeat_count": 3, "byte_identical_required": True, "network_used": False,
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    presence = source_presence()
    note = candidate_note_probe()
    return {
        "contract_id": CONTRACT_ID,
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK, "title": TITLE, "component": COMPONENT_ID,
        "mode": MODE, "profile": PROFILE, "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT, "branch": BRANCH, "reviewer": REVIEWER,
        "decision": "DEFER", "status": "incomplete", "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": {
            "decision": "DEFER", "status": "incomplete", "proposal_only": True,
            "qualification_status": "not_qualified", "blocked_before": "implementation_or_intake",
            "qualifying_results": 0, "blocked_release_gates": 8,
        },
        "qualification": {
            "status": "not_qualified", "evidence_status": "incomplete", "proposal_only": True,
            "qualifying_results": 0, "blocked_release_gates": 8, "open_blockers": 7,
            "candidate_note_present": presence["candidate_note_present"],
            "method_family_underspecified": True,
            "exact_licensed_source_weights_runtime_present": False,
            "reasons": [
                "method family underspecified: no frozen encoder-mapper-decoder, checkpoint, or target identity",
                "no exact source revision, license review, or checkpoint manifest",
                "no pinned offline runtime or deterministic execution recipe",
                "no rights-cleared input/target cohort, consent, or output-use decision",
                "no deterministic converted outputs or voice-profile measurements",
                "no target-device timing, memory, callback, or listening evidence",
                "no opt-in provider intake or independent release review",
            ],
        },
        "scope": _scope(), "boundary": _boundary(),
        "public_v0_geometry": {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160},
        "non_claims": _non_claims(),
        "profile_phrases": list(PROFILE_PHRASES),
        "profile_source": PROFILE_SOURCE,
        "source_pins": SOURCE_PINS, "boundary_pins": BOUNDARY_PINS, "sibling_pins": SIBLING_PINS,
        "source_presence": presence,
        "observed_provenance": {"candidate_note": note},
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "release_gates": _release_gates(projection),
        "voice_profile_requirements": _voice_profile_rows(),
        "required_results": _required_results(),
        "linked_row_projection": projection,
        "linked_row_fields": list(BOARD_ROW_FIELDS),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "reproduction": _reproduction(),
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    contract_sha = object_digest(contract)
    source_pins, boundary_pins, sibling_pins = verify_pins()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK, "title": TITLE, "component": COMPONENT_ID, "mode": MODE,
        "profile": PROFILE, "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT, "branch": BRANCH,
        "decision": "DEFER", "status": "incomplete", "qualification_status": "not_qualified",
        "proposal_only": True, "contract_sha256": contract_sha,
        "disposition": contract["disposition"], "qualification": contract["qualification"],
        "scope": contract["scope"], "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"], "non_claims": contract["non_claims"],
        "source_pins": source_pins, "boundary_pins": boundary_pins, "sibling_pins": sibling_pins,
        "source_presence": presence,
        "observed_provenance": contract["observed_provenance"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "voice_profile": {"profile": PROFILE, "profile_label": PROFILE_LABEL, "source": contract["profile_source"], "rows": contract["voice_profile_requirements"]},
        "gate_control": gate_control(),
        "admission": admission_controls(),
        "linked_row_identity": {
            "projection": contract["linked_row_projection"],
            "sha256": board_row_digest(contract["linked_row_projection"]),
            "fields": contract["linked_row_fields"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "required_results": contract["required_results"],
        "reproduction": contract["reproduction"],
    }


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "contract_id", "schema_id", "task", "component", "decision", "status",
        "qualification_status", "proposal_only", "qualification", "release_gates",
        "exact_blockers", "required_artifacts", "voice_profile_requirements",
        "linked_row_projection", "board_file_pinned",
    )
    for field in required:
        if field not in contract:
            raise ValueError("contract_field_missing:" + field)
    if contract["task"] != TASK or contract["component"] != COMPONENT_ID:
        raise ValueError("contract_identity")
    if contract["decision"] != "DEFER" or contract["status"] != "incomplete" or contract["qualification_status"] != "not_qualified" or contract["proposal_only"] is not True:
        raise ValueError("contract_disposition")
    gates = contract["release_gates"]
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gates")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}" or gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate:" + str(index))
    if len(contract["exact_blockers"]) != 7:
        raise ValueError("contract_blockers")
    if len(contract["required_artifacts"]) != 9:
        raise ValueError("contract_artifacts")
    if len(contract["voice_profile_requirements"]) != 8:
        raise ValueError("contract_rows")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    for pins in (contract["source_pins"], contract["boundary_pins"], contract["sibling_pins"]):
        if BOARD_TASK_ROW in pins:
            raise ValueError("mutable_board_pinned")


def verify_sources_manifest(payload: bytes) -> None:
    lines = payload.decode("ascii").splitlines()
    if not lines or not lines[0].startswith("# SHA-256 pins for "):
        raise ValueError("sources_header")
    seen: set[str] = set()
    for line in lines:
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if not HEX64.match(digest):
            raise ValueError("sources_digest")
        if name in seen:
            raise ValueError("sources_duplicate")
        seen.add(name)
    expected = {"source:" + n for n in SOURCE_PINS}
    expected |= {"boundary:" + n for n in BOUNDARY_PINS}
    expected |= {"sibling:" + n for n in SIBLING_PINS}
    expected |= {TASK_PREFIX + n for n in LOCAL_PIN_FILES}
    if seen != expected:
        raise ValueError("sources_set")
    if TASK_PREFIX + "SOURCES.sha256" in seen:
        raise ValueError("sources_self_pinned")
