# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Stdlib-only deterministic reference for SDK-PBSHIFT DEFER evidence.

This package records the pbshift playback-speed actuator candidate as
source-reported, unadmitted provenance. It does not import, build, execute,
download, benchmark, or qualify pbshift or any browser/runtime. All outputs
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

TASK = "SDK-PBSHIFT"
TITLE = "pbshift"
COMPONENT_ID = "pbshift"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
BASE_COMMIT = "180e2bcd29430280f939f229ab0af2171a57e69f"
BRANCH = "swarm/SDK-PBSHIFT"
REVIEWER = "reviewer-PBSHIFT"
CONTRACT_ID = "audio-sdk/pbshift/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
TASK_PREFIX = "docs/task-evidence/pbshift/"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
CANDIDATE_NOTE = "cpp-library/pipeline-validation/playback-speed-candidates.md"
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
    CANDIDATE_NOTE:
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
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
    "docs/task-evidence/granular-tsm/report.json":
        "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/libsamplerate/report.json":
        "c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc",
    "docs/task-evidence/non-stationary-gabor-tsm/report.json":
        "a89d9e49067e17e850267aaa6c23803d210ce6b503ac241a623aeb295a47dfdf",
    "docs/task-evidence/diffatsm/report.json":
        "8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a",
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/report.json":
        "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4",
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
    "source/output mapping",
    "duration",
    "pitch",
    "transient audibility",
    "playback buffering",
    "1×",
    "rate changes",
    "unfamiliar speech",
    "music",
    "silence",
    "rebuffer",
    "drift",
    "final partial window",
    "speech preservation",
    "source timestamps",
]

LINKED_ROWS = [
    {
        "task": "SDK-GRANULAR-TSM",
        "role": "merged rate/TSM synthetic reference; no pbshift runtime",
        "report_sha256":
            "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138",
    },
    {
        "task": "SDK-PHASE-VOCODER-BASELINE",
        "role": "merged rate/playback baseline; no pbshift runtime",
        "report_sha256":
            "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    },
    {
        "task": "SDK-LIBSAMPLERATE",
        "role": "merged varispeed/resampling reference; pitch changes with rate",
        "report_sha256":
            "c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc",
    },
    {
        "task": "SDK-NON-STATIONARY-GABOR-TSM",
        "role": "merged TSM DEFER evidence; no pbshift runtime",
        "report_sha256":
            "b612d196abaf5034ad1b2cfd991c1bfe18ea86f6f8f77f6b0f111d8f8f0dbf2d",
    },
    {
        "task": "SDK-DIFFATSM",
        "role": "merged TSM DEFER evidence; no pbshift runtime",
        "report_sha256":
            "fe63a55188ad674eea073f611a093e0b9f2f1fbe16f90f53e4f0131a0894d9c4",
    },
    {
        "task": "SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH",
        "role": "merged browser playback DEFER; no pbshift runtime",
        "report_sha256":
            "b2fb1f97e5f4e5e5f6dbfd4a67a7a5ca7df6383f73e2b2e4f4f6f2b0d5cf6f1b",
    },
]

PRESENCE_PROBES = [
    "third_party/pbshift",
    "data/checkouts/pbshift",
    "data/runtimes/pbshift",
    "vendor/pbshift",
    "research/pbshift",
    "docs/task-evidence/pbshift/runtime",
    "cpp-library/pipeline-validation/pbshift",
    "src/pbshift",
    "bindings/pbshift",
    "adapters/pbshift",
]

FORBIDDEN_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".m4a", ".aac", ".opus",
    ".onnx", ".pt", ".pth", ".bin", ".so", ".dylib", ".dll",
    ".a", ".tar", ".gz", ".zip", ".7z",
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[A-Za-z0-9.+-]*)?$")
FRACTION = re.compile(r"^(-?[0-9]+)(?:/([1-9][0-9]*))?$")
FRAME_SAMPLES = 160
RATE_MIN = Fraction(1, 8)
RATE_MAX = Fraction(8, 1)

MANIFEST_FIELDS = (
    "algorithm_license_id", "algorithm_license_sha256", "algorithm_revision",
    "algorithm_source_sha256", "api_surface", "audio", "controls", "mapping",
    "rights", "run_id", "runtime", "schema_id",
)
AUDIO_FIELDS = (
    "channels", "fixture_id", "frame_samples", "sample_rate_hz", "sha256",
    "total_samples",
)
MAPPING_FIELDS = (
    "final_partial_window", "map_contiguous", "output_duration_samples",
    "pitch_ratio", "playback_rate", "preserves_pitch",
    "source_duration_samples",
)
CONTROL_FIELDS = ("id", "kind", "passes")
RIGHTS_FIELDS = (
    "algorithm_license_reviewed", "commercial_use_approved", "consent_recorded",
    "listening_protocol_approved", "output_use_defined",
)
RUNTIME_FIELDS = (
    "automation", "automation_version", "deterministic", "host_arch",
    "host_os", "offline_render", "sample_rate_hz",
)
SCHEMA_MANIFEST_ID = "audio-sdk/pbshift/admission/0.1"
HOST_OSES = {"linux", "macos", "windows"}
HOST_ARCHES = {"arm64", "x86_64"}
AUTOMATIONS = {"none", "cmake-ctest", "playwright", "custom"}
ALGORITHM_LICENSES = {"MIT", "Apache-2.0", "BSD-3-Clause"}
AUDIO_SAMPLE_RATES = {16000, 24000, 44100, 48000}
AUDIO_CHANNELS = {1}
AUDIO_FRAME_SAMPLES = {128, 160}
CONTROL_KINDS = {
    "identity_1x", "rate_change", "final_partial_window", "pitch_ratio",
    "rebuffer", "mapping_contiguous",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _exact_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise ValueError(label + "_not_int")
    if value < minimum or value > maximum:
        raise ValueError(label + "_out_of_range")
    return value


def _choice_int(value: Any, label: str, allowed: set[int]) -> int:
    if type(value) is not int:
        raise ValueError(label + "_not_int")
    if value not in allowed:
        raise ValueError(label)
    return value


def linked_rows_digest() -> str:
    return object_digest(LINKED_ROWS)


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
    path = AUDIO_ROOT / CANDIDATE_NOTE
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    recorded = []
    line_no = None
    for i, line in enumerate(lines, start=1):
        if "pbshift" in line and "Speech actuator" in line:
            recorded.append(line)
            if line_no is None:
                line_no = i
        elif "pbshift" in line and line_no is not None and len(recorded) < 3:
            recorded.append(line)
    link_line = None
    for i, line in enumerate(lines, start=1):
        if "https://github.com/pbtechlab/pbshift" in line:
            link_line = i
            break
    statement = (
        "pbshift is source-reported as an MIT C++17 streaming actuator with "
        "pitch-synchronous voice path, 0.25-4x rate, automatable rate, and "
        "vendor-reported Live latency 56-64 ms at 48 kHz; the candidate note "
        "marks it pre-1.0, unproven, and not independently tested."
    )
    return {
        "path": CANDIDATE_NOTE,
        "sha256": sha256_file(path),
        "present": path.is_file(),
        "line": line_no,
        "link_line": link_line,
        "recorded_lines": recorded,
        "statement": statement,
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
        "algorithm_specified": False,
        "runtime_identity_recorded": False,
        "license_reviewed": False,
        "measured_result_recorded": False,
        "not_reproduced_here": True,
        "network_used_here": False,
    }


def source_presence() -> dict[str, Any]:
    probes = {probe: (AUDIO_ROOT / probe).exists() for probe in PRESENCE_PROBES}
    note = candidate_note_probe()
    present = [name for name, exists in probes.items() if exists]
    exact_present = any(probes[p] for p in (
        "third_party/pbshift", "data/checkouts/pbshift", "data/runtimes/pbshift",
        "vendor/pbshift", "research/pbshift"))
    return {
        "admitted": False,
        "candidate_note_present": note["present"],
        "candidate_note_records_unproven": True,
        "candidate_note_records_mit_claim": True,
        "pbshift_runtime_present": exact_present,
        "pbshift_source_present": exact_present,
        "pbshift_binary_present": False,
        "pbshift_weights_present": False,
        "pinned_manifest_present": False,
        "pinned_license_text_present": False,
        "pinned_build_present": False,
        "cohort_present": False,
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


def license_marker_probe() -> dict[str, Any]:
    return {
        "algorithm_license_reviewed": False,
        "algorithm_source_present": False,
        "mit_claim_recorded": True,
        "mit_claim_verified": False,
        "commercial_use_approved": False,
        "redistribution_approved": False,
        "output_use_defined": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic controls (not evidence)
# ---------------------------------------------------------------------------

def _synthetic_frame() -> list[float]:
    state = 0x12345678
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
        quantised = int(round(value * 32768))
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


def map_playback(total_samples: int, playback_rate: str, preserves_pitch: bool,
                 segments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    total = _exact_int(total_samples, "mapping_source_duration_samples", 1, 1_000_000_000)
    rate = parse_fraction(playback_rate, "mapping_playback_rate", RATE_MIN, RATE_MAX)
    if type(preserves_pitch) is not bool:
        raise ValueError("mapping_preserves_pitch_not_bool")
    if segments is None:
        segments = [{"start_sample": 0, "end_sample": total, "rate": _fraction_text(rate)}]
    records = []
    cursor = Fraction(0, 1)
    last_end = 0
    for index, seg in enumerate(segments):
        if set(seg) != {"start_sample", "end_sample", "rate"}:
            raise ValueError("mapping_segment_fields")
        start = _exact_int(seg["start_sample"], "mapping_segment_start", 0, total)
        end = _exact_int(seg["end_sample"], "mapping_segment_end", 0, total)
        if start != last_end or end <= start:
            raise ValueError("mapping_map_contiguous")
        seg_rate = parse_fraction(seg["rate"], "mapping_segment_rate", RATE_MIN, RATE_MAX)
        out_start = cursor
        cursor += Fraction(end - start, 1) / seg_rate
        records.append({
            "index": index, "start_sample": start, "end_sample": end,
            "rate": _fraction_text(seg_rate),
            "output_start": _fraction_text(out_start),
            "output_end": _fraction_text(cursor),
            "qualifies": False,
        })
        last_end = end
    if last_end != total:
        raise ValueError("mapping_map_contiguous")
    pitch_ratio = Fraction(1, 1) if preserves_pitch else rate
    floor_out = int(cursor.numerator // cursor.denominator)
    ceil_out = floor_out if cursor.denominator == 1 else floor_out + 1
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "total_samples": total,
        "rate": _fraction_text(rate),
        "preserves_pitch": preserves_pitch,
        "pitch_ratio": _fraction_text(pitch_ratio),
        "output_duration": _fraction_text(cursor),
        "output_duration_samples_floor": floor_out,
        "output_duration_samples_ceil": ceil_out,
        "duration_identity": cursor == Fraction(total, 1),
        "source_mapping_contiguous": True,
        "final_partial_window": {
            "block_samples": 1600,
            "final_window_samples": total % 1600 or 1600,
            "partial": total % 1600 != 0,
        },
        "records": records,
        "qualifies": False,
    }


def gate_control() -> dict[str, Any]:
    cases = []
    def add(case_id: str, total: int, rate: str, preserve: bool, segments=None):
        cases.append({
            "id": case_id,
            "evidence_class": "synthetic_contract_control_not_evidence",
            "mapping": map_playback(total, rate, preserve, segments),
            "qualifies": False,
        })
    add("identity_1x_preserve", 16000, "1", True)
    add("identity_final_partial_preserve", 16165, "1", True)
    add("faster_3_2_preserve", 16000, "3/2", True)
    add("slower_3_4_preserve", 16000, "3/4", True)
    add("varispeed_5_4_unpreserved", 16000, "5/4", False)
    add("rate_change_schedule", 16000, "1", True, [
        {"start_sample": 0, "end_sample": 4000, "rate": "1"},
        {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
        {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
    ])
    identity_passes = sum(1 for c in cases if c["mapping"]["duration_identity"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "declared playback-rate duration/pitch arithmetic only; no pbshift runtime, no resampler, no TSM algorithm, no measured waveform",
        "rate_bounds": {"min": _fraction_text(RATE_MIN), "max": _fraction_text(RATE_MAX)},
        "cases": cases,
        "frame": frame_control(),
        "summary": {
            "case_count": len(cases),
            "identity_passes": identity_passes,
            "explicit_nonidentity_controls": len(cases) - identity_passes,
            "qualifying_results": 0,
            "runtime_imported": False, "audio_read": False, "audio_played": False,
            "pitch_measured": False, "network_used": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Admission controls (fail-closed)
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


def validate_manifest(manifest: Any) -> dict[str, Any]:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != SCHEMA_MANIFEST_ID:
        raise ValueError("manifest_schema_id")
    _slug(root["run_id"], "run_id")
    _hex(root["algorithm_revision"], "algorithm_revision", re.compile(r"^[0-9a-f]{40}$"))
    if root["algorithm_license_id"] not in ALGORITHM_LICENSES:
        raise ValueError("algorithm_license_id")
    _hex(root["algorithm_license_sha256"], "algorithm_license_sha256", HEX64)
    _hex(root["algorithm_source_sha256"], "algorithm_source_sha256", HEX64)
    _slug(root["api_surface"], "api_surface")

    audio = _exact_keys(root["audio"], AUDIO_FIELDS, "audio")
    _slug(audio["fixture_id"], "audio_fixture_id")
    _hex(audio["sha256"], "audio_sha256", HEX64)
    _choice_int(audio["sample_rate_hz"], "audio_sample_rate", AUDIO_SAMPLE_RATES)
    _choice_int(audio["channels"], "audio_channels", AUDIO_CHANNELS)
    _choice_int(audio["frame_samples"], "audio_frame_samples", AUDIO_FRAME_SAMPLES)
    total = _exact_int(audio["total_samples"], "audio_total_samples", 1, 1_000_000_000)

    mapping = _exact_keys(root["mapping"], MAPPING_FIELDS, "mapping")
    rate = parse_fraction(mapping["playback_rate"], "mapping_playback_rate", RATE_MIN, RATE_MAX)
    if type(mapping["preserves_pitch"]) is not bool:
        raise ValueError("mapping_preserves_pitch_not_bool")
    source_duration = _exact_int(mapping["source_duration_samples"], "mapping_source_duration_samples", 1, 1_000_000_000)
    output_duration = _exact_int(mapping["output_duration_samples"], "mapping_output_duration_samples", 0, 8_000_000_000)
    if source_duration != total:
        raise ValueError("mapping_source_duration_mismatch")
    expected = Fraction(source_duration, 1) / rate
    if expected.denominator != 1:
        raise ValueError("mapping_noninteger_duration")
    if output_duration != int(expected):
        raise ValueError("mapping_duration_mismatch")
    pitch = parse_fraction(mapping["pitch_ratio"], "mapping_pitch_ratio", RATE_MIN, RATE_MAX)
    expected_pitch = Fraction(1, 1) if mapping["preserves_pitch"] else rate
    if pitch != expected_pitch:
        raise ValueError("mapping_pitch_ratio")
    if mapping["map_contiguous"] is not True:
        raise ValueError("mapping_map_contiguous")
    if mapping["final_partial_window"] is not True:
        raise ValueError("mapping_final_partial_window")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["automation"] not in AUTOMATIONS:
        raise ValueError("runtime_automation")
    if not isinstance(runtime["automation_version"], str) or not SEMVER.match(runtime["automation_version"]):
        raise ValueError("runtime_automation_version")
    if runtime["host_os"] not in HOST_OSES:
        raise ValueError("runtime_host_os")
    if runtime["host_arch"] not in HOST_ARCHES:
        raise ValueError("runtime_host_arch")
    for field in ("offline_render", "deterministic"):
        if runtime[field] is not True:
            raise ValueError("runtime_" + field)
    _choice_int(runtime["sample_rate_hz"], "runtime_sample_rate", AUDIO_SAMPLE_RATES)

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

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS:
        if rights[field] is not True:
            raise ValueError("rights_" + field)

    return {
        "admitted": True,
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "run_id": root["run_id"],
        "mapping_digest": object_digest(mapping),
        "control_count": len(controls),
        "duration_identity": output_duration == source_duration,
        "rate": _fraction_text(rate),
        "pitch_ratio": _fraction_text(pitch),
    }


def _base_manifest() -> dict[str, Any]:
    def syn(name: str) -> str:
        return hashlib.sha256(("synthetic:" + name).encode("ascii")).hexdigest()
    return {
        "schema_id": SCHEMA_MANIFEST_ID,
        "run_id": "synthetic-schema-control",
        "algorithm_revision": "0" * 40,
        "algorithm_license_id": "MIT",
        "algorithm_license_sha256": syn("license"),
        "algorithm_source_sha256": syn("source"),
        "api_surface": "pbshift-v0-streaming",
        "audio": {
            "fixture_id": "synthetic-schema-fixture",
            "sha256": syn("fixture"),
            "sample_rate_hz": 48000,
            "channels": 1,
            "frame_samples": 160,
            "total_samples": 16000,
        },
        "mapping": {
            "playback_rate": "5/4",
            "preserves_pitch": True,
            "source_duration_samples": 16000,
            "output_duration_samples": 12800,
            "pitch_ratio": "1",
            "map_contiguous": True,
            "final_partial_window": True,
        },
        "runtime": {
            "automation": "cmake-ctest",
            "automation_version": "3.29.0",
            "host_os": "linux",
            "host_arch": "x86_64",
            "offline_render": True,
            "deterministic": True,
            "sample_rate_hz": 48000,
        },
        "controls": [
            {"id": "control-identity", "kind": "identity_1x", "passes": True},
            {"id": "control-rate", "kind": "rate_change", "passes": True},
            {"id": "control-final", "kind": "final_partial_window", "passes": True},
            {"id": "control-pitch", "kind": "pitch_ratio", "passes": True},
            {"id": "control-rebuffer", "kind": "rebuffer", "passes": True},
            {"id": "control-map", "kind": "mapping_contiguous", "passes": True},
        ],
        "rights": {
            "algorithm_license_reviewed": True,
            "commercial_use_approved": True,
            "consent_recorded": True,
            "listening_protocol_approved": True,
            "output_use_defined": True,
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
        ("manifest_schema", "manifest_schema_id", setter(("schema_id",), "audio-sdk/other/0.1")),
        ("run_id", "run_id", setter(("run_id",), "Bad Id")),
        ("algorithm_revision_short", "algorithm_revision_malformed", setter(("algorithm_revision",), "a" * 39)),
        ("algorithm_license", "algorithm_license_id", setter(("algorithm_license_id",), "proprietary")),
        ("algorithm_license_digest", "algorithm_license_sha256_malformed", setter(("algorithm_license_sha256",), "z" * 64)),
        ("algorithm_source_digest", "algorithm_source_sha256_malformed", setter(("algorithm_source_sha256",), "A" * 64)),
        ("api_surface", "api_surface", setter(("api_surface",), "Bad Surface")),
        ("audio_fixture_id", "audio_fixture_id", setter(("audio", "fixture_id"), "Bad Fixture")),
        ("audio_sha", "audio_sha256_malformed", setter(("audio", "sha256"), "g" * 64)),
        ("audio_sample_rate", "audio_sample_rate", setter(("audio", "sample_rate_hz"), 22050)),
        ("audio_channels", "audio_channels", setter(("audio", "channels"), 3)),
        ("audio_frame_samples", "audio_frame_samples", setter(("audio", "frame_samples"), 100)),
        ("audio_total", "audio_total_samples_out_of_range", setter(("audio", "total_samples"), 0)),
        ("mapping_rate_malformed", "mapping_playback_rate_malformed", setter(("mapping", "playback_rate"), "1/0")),
        ("mapping_rate_zero", "mapping_playback_rate_out_of_range", setter(("mapping", "playback_rate"), "0")),
        ("mapping_rate_high", "mapping_playback_rate_out_of_range", setter(("mapping", "playback_rate"), "9")),
        ("mapping_preserve_bool", "mapping_preserves_pitch_not_bool", setter(("mapping", "preserves_pitch"), "yes")),
        ("mapping_source_mismatch", "mapping_source_duration_mismatch", setter(("mapping", "source_duration_samples"), 8000)),
        ("mapping_duration", "mapping_duration_mismatch", setter(("mapping", "output_duration_samples"), 16000)),
        ("mapping_noninteger", "mapping_noninteger_duration", lambda m: (m["audio"].update({"total_samples": 16001}), m["mapping"].update({"source_duration_samples": 16001}))),
        ("mapping_pitch", "mapping_pitch_ratio", setter(("mapping", "pitch_ratio"), "5/4")),
        ("mapping_contiguous", "mapping_map_contiguous", setter(("mapping", "map_contiguous"), False)),
        ("mapping_final", "mapping_final_partial_window", setter(("mapping", "final_partial_window"), False)),
        ("runtime_automation", "runtime_automation", setter(("runtime", "automation"), "manual")),
        ("runtime_automation_version", "runtime_automation_version", setter(("runtime", "automation_version"), "3")),
        ("runtime_host_os", "runtime_host_os", setter(("runtime", "host_os"), "ios")),
        ("runtime_host_arch", "runtime_host_arch", setter(("runtime", "host_arch"), "riscv64")),
        ("runtime_offline", "runtime_offline_render", setter(("runtime", "offline_render"), False)),
        ("runtime_deterministic", "runtime_deterministic", setter(("runtime", "deterministic"), False)),
        ("runtime_sample_rate", "runtime_sample_rate", setter(("runtime", "sample_rate_hz"), 22050)),
        ("controls_missing", "controls_count", lambda m: m["controls"].pop()),
        ("controls_duplicate_kind", "control_kind_duplicate", setter(("controls", 1, "kind"), "identity_1x")),
        ("controls_duplicate_id", "control_id_duplicate", setter(("controls", 1, "id"), "control-identity")),
        ("controls_unknown_kind", "control_kind", setter(("controls", 0, "kind"), "music")),
        ("controls_not_passed", "control_not_passed", setter(("controls", 0, "passes"), False)),
        ("rights_consent", "rights_consent_recorded", setter(("rights", "consent_recorded"), False)),
        ("rights_commercial", "rights_commercial_use_approved", setter(("rights", "commercial_use_approved"), False)),
        ("rights_unknown_field", "rights_fields", setter(("rights", "extra"), "x")),
        ("audio_unknown_field", "audio_fields", setter(("audio", "extra"), "x")),
        ("mapping_unknown_field", "mapping_fields", setter(("mapping", "extra"), "x")),
        ("runtime_unknown_field", "runtime_fields", setter(("runtime", "extra"), "x")),
        ("control_unknown_field", "control_fields", setter(("controls", 0, "extra"), "x")),
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
            "run_id": control["run_id"], "rate": control["rate"],
            "pitch_ratio": control["pitch_ratio"], "duration_identity": control["duration_identity"],
            "mapping_digest": control["mapping_digest"],
        },
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for r in rejected if r["status"] == "rejected"),
            "all_rejected": all(r["status"] == "rejected" for r in rejected),
            "all_codes_match": all(r["code"] == r["expected_code"] for r in rejected),
            "accepted_schema_controls": 1, "qualifying_results": 0,
            "state_advanced_on_rejection": False, "runtime_imported": False,
            "audio_read": False, "audio_played": False, "pitch_measured": False, "network_used": False,
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
        "audio_read": False, "audio_played": False, "pitch_measured": False,
        "listening_conducted": False, "device_timing_measured": False, "benchmark_run": False,
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
        "The candidate note reports pbshift as pre-1.0, unproven, and not independently tested; that is provenance only, not a measurement.",
        "No pbshift source, binary, runtime, model, or build was present in the project workspace, copied, imported, built, executed, or downloaded.",
        "No playback-rate, TSM, pitch, transient, buffering, rebuffer, drift, or speech-preservation result was measured.",
        "No audio was read or played; no rights-cleared speech, music, or silence cohort, consent record, or output-use grant is present.",
        "No listening panel, target-device timing, resource measurement, benchmark, or release review was performed.",
        "No provider, descriptor, registry, default, installed-v0, ABI, shared-build, CI, board, or handoff file is changed.",
    ]


def _required_results() -> dict[str, bool]:
    return {
        "pbshift_source_tree_admitted": False,
        "pbshift_license_and_notice_admitted": False,
        "pinned_build_and_runtime_manifest_admitted": False,
        "official_api_and_geometry_contract_admitted": False,
        "measured_playback_trace_present": False,
        "pitch_and_transient_measurement_present": False,
        "rights_cleared_cohort_present": False,
        "rate_acceptance_profile_measured": False,
        "speech_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def _required_artifacts() -> list[dict[str, Any]]:
    presence = source_presence()
    return [
        {"id": "A01", "name": "pinned pbshift source tree and revision", "present": presence["pbshift_source_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-01"},
        {"id": "A02", "name": "pbshift LICENSE/NOTICE and dependency license bundle", "present": presence["pinned_license_text_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-01"},
        {"id": "A03", "name": "pinned build/runtime manifest and offline host profile", "present": presence["pinned_manifest_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-02"},
        {"id": "A04", "name": "official pbshift API/geometry/rate semantics", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-02"},
        {"id": "A05", "name": "measured playback trace with 1x/rate-change/final-partial", "present": presence["measured_trace_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-03"},
        {"id": "A06", "name": "rights-cleared speech/music/silence playback cohort", "present": presence["cohort_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-04"},
        {"id": "A07", "name": "approved pitch/transient scorer and preservation labels", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-04"},
        {"id": "A08", "name": "listening and target-device timing/resources record", "present": presence["listening_record_present"] or presence["device_timing_record_present"], "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-05"},
        {"id": "A09", "name": "SDK provider intake, opt-in boundary, and release review", "present": False, "verified": False, "licensed": False, "admitted": False, "blocked": True, "sha256": None, "blocker": "BLK-06"},
    ]


def _exact_blockers() -> list[dict[str, Any]]:
    return [
        {"id": "BLK-01", "artifact_id": "A01", "status": "open", "qualifies": False,
         "missing": "Pinned pbshift source tree, exact revision, complete LICENSE/NOTICE, vendored dependency terms (including Signalsmith Stretch/pffft claims), and a reviewed redistribution/commercial-use record are absent from the project workspace.",
         "required_action": "Supply the exact pbshift source revision, tree digest, complete license/notice bundle, dependency licenses, and a reviewed redistribution/commercial-use decision."},
        {"id": "BLK-02", "artifact_id": "A03", "status": "open", "qualifies": False,
         "missing": "Pinned build/runtime manifest, reproducible offline host profile, exact API/geometry semantics for feed/available/read, rate-change behavior, final-partial handling, and sample-rate/channel support are absent.",
         "required_action": "Supply a pinned build/host manifest and authoritative API/geometry contract covering 1x, rate changes, final partial, channels, and sample rates."},
        {"id": "BLK-03", "artifact_id": "A05", "status": "open", "qualifies": False,
         "missing": "No measured pbshift playback trace exists: no 1x control, source/output mapping, duration error, rate-change behavior, rebuffer/drift, or final-partial measurement.",
         "required_action": "Provide deterministic measured traces on the pinned build covering 1x, rate changes, final partial, buffering/rebuffer, and drift."},
        {"id": "BLK-04", "artifact_id": "A06", "status": "open", "qualifies": False,
         "missing": "No rights-cleared speech/music/silence cohort, consent/output-use terms, approved pitch/transient scorer, preservation labels, or independent listening protocol is present.",
         "required_action": "Supply an immutable consented cohort, output-use terms, approved pitch/transient/scoring protocol, and independent preservation labels/listening plan."},
        {"id": "BLK-05", "artifact_id": "A08", "status": "open", "qualifies": False,
         "missing": "No target-device timing, CPU/memory, real-time pacing, or resource evidence exists; candidate-note latency numbers are source-reported and not remeasured here.",
         "required_action": "Measure target-device timing/resources under the intended workload and record exact host/runtime identity."},
        {"id": "BLK-06", "artifact_id": "A09", "status": "open", "qualifies": False,
         "missing": "No separate SDK provider intake, opt-in registration boundary, OFF-default review, or release decision exists; this package makes no provider/ABI/default change.",
         "required_action": "Complete separate opt-in adapter/provider intake with OFF default, explicit registration, and release review before any qualification claim."},
    ]


def _rate_profile_rows() -> list[dict[str, Any]]:
    rows = [
        ("RATE-01", "1x control", "No measured 1x pbshift playback control."),
        ("RATE-02", "source/output mapping and rate changes", "Synthetic arithmetic only; no pbshift source-to-output trace."),
        ("RATE-03", "duration identity and error", "No measured pbshift output duration or error."),
        ("RATE-04", "pitch", "No rendered waveform, pitch tracker, or preserves-pitch measurement."),
        ("RATE-05", "transient audibility", "No waveform, transient analysis, or listening."),
        ("RATE-06", "playback buffering, rebuffer and drift", "No runtime clock, buffering, fill/flush, or drift run."),
        ("RATE-07", "unfamiliar speech, music and silence", "No rights-cleared stratified playback cohort exists."),
        ("RATE-08", "final partial window and speech preservation", "Synthetic final-window arithmetic only; no runtime render or preservation score."),
    ]
    return [{"id": rid, "requirement": req, "status": "blocked", "qualifies": False, "evidence": ev} for rid, req, ev in rows]


def _rate_outcomes() -> list[dict[str, Any]]:
    return [{"id": row["id"].replace("RATE", "OUT"), "requirement": row["requirement"], "status": "blocked", "value": None, "qualifies": False} for row in _rate_profile_rows()]


def _release_gates(projection: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        ("RG-01", "pinned source and license", "Exact pbshift revision, tree digest, complete license/notice bundle, and dependency license review."),
        ("RG-02", "pinned build and API/geometry contract", "Pinned build/host manifest and authoritative API/geometry/rate/final-partial contract."),
        ("RG-03", "measured deterministic traces", "Measured 1x/rate-change/final-partial/buffering/drift traces on pinned build."),
        ("RG-04", "rights-cleared playback cohort", "Immutable consented speech/music/silence cohort with output-use terms and matched controls."),
        ("RG-05", "pitch/transient/preservation scoring", "Approved pitch/transient scorer, preservation labels, and independent listening."),
        ("RG-06", "rate acceptance profile", "Measured duration, pitch, transient, buffering, rebuffer, drift, and speech preservation across required strata."),
        ("RG-07", "target-device timing and resources", "Target-device timing/CPU/memory under intended workload with exact host/runtime identity."),
        ("RG-08", "opt-in intake and release", "Separate opt-in provider intake, OFF default, registration boundary, benchmark/release review."),
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
    markers = license_marker_probe()
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
            "qualifying_results": 0, "blocked_release_gates": 8, "open_blockers": 6,
            "candidate_note_present": presence["candidate_note_present"],
            "licensed_implementation_runtime_present": False,
            "pbshift_runtime_present": presence["pbshift_runtime_present"],
            "reasons": [
                "no pinned pbshift source tree, revision, or complete license/notice bundle",
                "no pinned build/runtime manifest or authoritative API/geometry contract",
                "no measured playback trace, rate-change, or final-partial result",
                "no rights-cleared cohort, pitch/transient scoring, or listening result",
                "no target-device timing/resource measurement",
                "no opt-in provider intake or release review",
            ],
        },
        "scope": _scope(), "boundary": _boundary(),
        "public_v0_geometry": {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160},
        "non_claims": _non_claims(),
        "profile_phrases": list(PROFILE_PHRASES),
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_pins": SOURCE_PINS, "boundary_pins": BOUNDARY_PINS, "sibling_pins": SIBLING_PINS,
        "source_presence": presence, "license_findings": markers,
        "observed_provenance": {
            "candidate_note": note,
            "sibling_evidence": [dict(row) for row in LINKED_ROWS],
            "synthetic_frame_digest": frame_control()["accepted"]["digest_sha256"],
        },
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "release_gates": _release_gates(projection),
        "rate_profile_requirements": _rate_profile_rows(),
        "rate_outcomes": _rate_outcomes(),
        "required_results": _required_results(),
        "linked_row_projection": projection,
        "linked_row_fields": list(BOARD_ROW_FIELDS),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
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
        "source_presence": presence, "license_findings": contract["license_findings"],
        "observed_provenance": contract["observed_provenance"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {"profile": PROFILE, "profile_label": PROFILE_LABEL, "source": contract["profile_source"], "rows": contract["rate_profile_requirements"]},
        "rate_outcomes": {"rows": contract["rate_outcomes"]},
        "gate_control": gate_control(),
        "admission": admission_controls(),
        "linked_row_identity": {
            "projection": contract["linked_row_projection"],
            "sha256": board_row_digest(contract["linked_row_projection"]),
            "fields": contract["linked_row_fields"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": contract["linked_rows"],
            "linked_rows_sha256": contract["linked_rows_sha256"],
        },
        "required_results": contract["required_results"],
        "reproduction": contract["reproduction"],
    }


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = ("contract_id", "schema_id", "task", "component", "decision", "status", "qualification_status", "proposal_only", "qualification", "release_gates", "exact_blockers", "required_artifacts", "rate_profile_requirements", "rate_outcomes", "linked_row_projection", "board_file_pinned")
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
    if len(contract["exact_blockers"]) != 6:
        raise ValueError("contract_blockers")
    if len(contract["required_artifacts"]) != 9:
        raise ValueError("contract_artifacts")
    if len(contract["rate_profile_requirements"]) != 8 or len(contract["rate_outcomes"]) != 8:
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
