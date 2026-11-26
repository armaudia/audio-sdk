# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only blocker evidence for SDK-PYANNOTE-DIARIZATION.

This module never downloads, reads, imports, links or executes pyannote,
pyannote.audio, torch, Hugging Face assets, model weights, audio corpora,
RTTM/UEM references, or diarization runtimes. It records exact absence,
validates a bounded offline admission envelope, and produces a canonical DEFER
report. The envelope is protocol plumbing over synthetic timestamped anonymous
label intervals; it is not diarization, not speaker identity, not DER/JER,
not audio processing, and cannot qualify anything.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-PYANNOTE-DIARIZATION"
COMPONENT_ID = "pyannote-diarization"
TASK_TITLE = "pyannote diarization"
CONTRACT_ID = "audio-sdk/pyannote-diarization-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/pyannote-diarization-envelope/0.1"
PROFILE = "spatial"
PROFILE_LABEL = "Spatial"
MODE = "feasibility"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
BRANCH = "swarm/SDK-PYANNOTE-DIARIZATION"
WRITE_SCOPE = "docs/task-evidence/pyannote-diarization/ only"
TASK_PREFIX = "docs/task-evidence/pyannote-diarization/"
REQUIRED_INTERPRETER = "3.11.5"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
MAX_SAMPLE_COUNT = 192_000
MAX_SEGMENTS = 32
MAX_CONTROLS = 8
RUN_MODES = ("offline",)
CONTROL_KINDS = (
    "candidate",
    "identity_timeline",
    "missing_runtime",
    "nonfinite_rejection",
)
REQUIRED_CONTROL_KINDS = frozenset(CONTROL_KINDS)

DISPOSITION = (
    "pyannote diarization feasibility blocker. The task requires a runnable "
    "source, exact assets, permitted scope, task geometry and matched "
    "evidence; then reproduction of the exact model/runtime as a "
    "caller-supplied-asset reference and an opt-in SDK adapter only after "
    "prerequisites pass. No exact licensed pyannote diarization source, "
    "immutable revision, model weights, Hugging Face access terms, pinned "
    "offline runtime, rights-cleared diarization corpus, RTTM/UEM reference, "
    "or matched DER/JER/timing result is present or reproducible in this "
    "worktree. Anonymous speaker IDs must remain separate from verification; "
    "no missing, blocked, or source-reported result qualifies."
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT")
    if override:
        return Path(override).resolve()
    for parent in (HERE.parents[3], *HERE.parents):
        if (parent / "audio-benchmark-platform" / "plan" / "INVENTORY.json").is_file():
            return parent
    raise RuntimeError("cannot locate the audioml workspace root")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
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
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
LINKED_ROW_IDS = (
    TASK,
    "SDK-FND-AUDIT",
    "SDK-FND-EVIDENCE",
    "SDK-FND-PROVIDER",
)
MUTABLE_BOARD_FIELDS = (
    "status",
    "owner",
    "claim",
    "review",
    "handoff",
    "blocked_reason",
    "dispatch_priority",
)

MANIFEST_FIELDS = (
    "schema_id", "request_id", "mode", "candidate", "input", "timeline",
    "controls", "rights",
)
CANDIDATE_FIELDS = (
    "name", "source_present", "weights_present", "runtime_present",
    "revision", "license",
)
INPUT_FIELDS = (
    "sample_rate_hz", "channels", "sample_count", "dtype", "finite", "peak",
)
TIMELINE_FIELDS = ("segment_count", "segments_sha256", "anonymous_only", "overlap_allowed")
SEGMENT_FIELDS = ("start_sample", "end_sample", "speaker")
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = (
    "source_terms", "weight_terms", "input_terms", "output_use", "claims_qualified",
)

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SPEAKER_ID = re.compile(r"^spk_[0-9]{2}$")
COMMIT_SHA = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{40}$")
DECIMAL = re.compile(r"^(0|1)(\.[0-9]*[1-9])?$|^0\.[0-9]*[1-9]$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

ABSENCE_PROBES = (
    "workspace:data/checkouts/pyannote-audio",
    "workspace:data/checkouts/pyannote.audio",
    "workspace:data/checkouts/pyannote-diarization",
    "workspace:data/models/pyannote",
    "workspace:data/models/pyannote-audio",
    "workspace:data/envs/pyannote-audio",
    "workspace:data/audio/pyannote-diarization",
    "workspace:research/pyannote-diarization",
    "worktree:third_party/pyannote-audio",
    "worktree:third_party/pyannote",
    "worktree:adapters/pyannote-diarization",
    "worktree:docs/task-evidence/pyannote-diarization/weights",
    "home:.cache/huggingface/hub/models--pyannote--speaker-diarization-3.1",
    "home:.cache/torch/pyannote",
)

EVIDENCE_SNIPPETS = (
    {
        "path": "research/category_registry.json",
        "phrase": "Anonymous speaker diarization",
    },
    {
        "path": "audio-benchmark-platform/plan/INVENTORY.md",
        "phrase": "pyannote diarization",
    },
    {
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "phrase": "SDK-PYANNOTE-DIARIZATION",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "phrase": "SDK-PYANNOTE-DIARIZATION",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "phrase": "Compare localization/activity/extraction with task-matched held-out labels.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "phrase": "Report leakage, target damage, channel loss, and changes in room/reference conditions.",
    },
    {
        "path": "audio-benchmark-platform/plan/audio-sdk/README.md",
        "phrase": "diarization, speaker analysis and ASR adapters",
    },
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise TypeError(f"float not allowed in canonical evidence: {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_floats(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_floats(item, f"{path}[{index}]")


def loads_strict(text: str) -> Any:
    if not text.strip():
        raise ValueError("empty input")
    if text.startswith("\ufeff"):
        raise ValueError("byte order mark")
    if re.search(r'(?<![eE])[+-]?\b(?:NaN|Infinity)\b', text):
        raise ValueError("nonfinite literal")
    decoder = json.JSONDecoder(parse_float=lambda _: (_ for _ in ()).throw(ValueError("float literal")),
                               object_pairs_hook=_object_pairs_hook)
    try:
        value, index = decoder.raw_decode(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid json: {error}") from error
    if text[index:].strip():
        raise ValueError("trailing data")
    if not isinstance(value, dict):
        raise ValueError("top-level must be object")
    _reject_floats(value)
    return value


def _object_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate key")
        obj[key] = value
    return obj


def read_strict_json(path: Path) -> Any:
    return loads_strict(path.read_text(encoding="utf-8"))


class AdmissionError(ValueError):
    def __init__(self, code: str, field: str = "", detail: str = ""):
        self.code = code
        self.field = field
        self.detail = detail
        super().__init__(code)


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdmissionError("not_object", field)
    return value


def _require_keys(obj: dict[str, Any], expected: tuple[str, ...], field: str) -> None:
    keys = tuple(obj.keys())
    missing = [key for key in expected if key not in obj]
    extra = [key for key in keys if key not in expected]
    if missing:
        raise AdmissionError("missing_field", f"{field}.{missing[0]}")
    if extra:
        raise AdmissionError("unknown_field", f"{field}.{extra[0]}")
    if keys != expected:
        raise AdmissionError("field_order_invalid", field)


def _require_slug(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise AdmissionError("invalid_slug", field)
    return value


def _require_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SHA256_HEX.match(value):
        raise AdmissionError("digest_invalid", field)
    return value


def _require_decimal(value: Any, field: str) -> Fraction:
    if not isinstance(value, str) or not DECIMAL.match(value):
        raise AdmissionError("peak_not_canonical", field)
    fraction = Fraction(value)
    if not (Fraction(0, 1) <= fraction <= Fraction(1, 1)):
        raise AdmissionError("peak_out_of_range", field)
    return fraction


def _require_int(value: Any, field: str, *, minimum: int | None = None, maximum: int | None = None) -> int:
    if type(value) is not int:
        raise AdmissionError("not_integer", field)
    if minimum is not None and value < minimum:
        raise AdmissionError("out_of_range", field)
    if maximum is not None and value > maximum:
        raise AdmissionError("out_of_range", field)
    return value


def _require_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise AdmissionError("not_bool", field)
    return value


def board_row_projection(board_path: Path) -> dict[str, Any]:
    data = json.loads(board_path.read_text(encoding="utf-8"))
    rows = data.get("tasks", data if isinstance(data, list) else [])
    for row in rows:
        if row.get("id") == TASK:
            return {field: row[field] for field in BOARD_ROW_FIELDS}
    raise RuntimeError(f"{TASK} row not found")


def board_row_digest(row: dict[str, Any]) -> str:
    return object_digest(row)


def linked_rows() -> list[dict[str, Any]]:
    board = AUDIO_ROOT / BOARD_TASK_ROW
    data = json.loads(board.read_text(encoding="utf-8"))
    rows = data.get("tasks", data if isinstance(data, list) else [])
    by_id = {row.get("id"): row for row in rows}
    projected = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if not row:
            raise RuntimeError(f"linked row missing: {row_id}")
        projected.append({field: row.get(field) for field in BOARD_ROW_FIELDS})
    return projected


def linked_rows_digest(rows: list[dict[str, Any]]) -> str:
    return object_digest(rows)


def evidence_snippet_check() -> dict[str, Any]:
    checks = []
    for snippet in EVIDENCE_SNIPPETS:
        path = AUDIO_ROOT / snippet["path"]
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        present = snippet["phrase"] in text
        checks.append({"path": snippet["path"], "phrase": snippet["phrase"], "present": present})
    return {"checks": checks, "count": len(checks), "all_present": all(item["present"] for item in checks)}


def _probe_present(probe: str) -> bool:
    if probe.startswith("workspace:"):
        return (AUDIO_ROOT / probe.split(":", 1)[1]).exists()
    if probe.startswith("worktree:"):
        return (WORKTREE / probe.split(":", 1)[1]).exists()
    if probe.startswith("home:"):
        return (Path.home() / probe.split(":", 1)[1]).exists()
    return False


def absence_summary() -> dict[str, Any]:
    probes = []
    present_count = 0
    for probe in ABSENCE_PROBES:
        present = _probe_present(probe)
        if present:
            present_count += 1
        probes.append({"path": probe, "present": present})
    return {
        "probe_count": len(probes),
        "present_count": present_count,
        "all_absent": present_count == 0,
        "probes": probes,
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "network_used": False,
        "audio_read": False,
        "candidate_runtime_executed": False,
        "candidate_module_imported": False,
        "download_attempted": False,
    }


def runtime_readiness() -> dict[str, Any]:
    return {
        "runtime_present": False,
        "runtime_pinned": False,
        "any_module_available": False,
        "probed_modules": {
            "pyannote.audio": False,
            "pyannote.core": False,
            "torch": False,
            "huggingface_hub": False,
        },
    }


def segments_digest(segments: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        "".join(f"{s['start_sample']},{s['end_sample']},{s['speaker']}\n" for s in segments).encode("ascii")
    ).hexdigest()


def validate_segments(segments: Any, sample_count: int) -> list[dict[str, Any]]:
    if not isinstance(segments, list) or not segments or len(segments) > MAX_SEGMENTS:
        raise AdmissionError("segments_invalid", "timeline.segments")
    normalized: list[dict[str, Any]] = []
    for index, segment in enumerate(segments):
        field = f"timeline.segments[{index}]"
        obj = _require_object(segment, field)
        _require_keys(obj, SEGMENT_FIELDS, field)
        start = _require_int(obj["start_sample"], f"{field}.start_sample", minimum=0, maximum=sample_count)
        end = _require_int(obj["end_sample"], f"{field}.end_sample", minimum=1, maximum=sample_count)
        if end <= start:
            raise AdmissionError("segment_empty_or_reversed", field)
        speaker = obj["speaker"]
        if not isinstance(speaker, str) or not SPEAKER_ID.match(speaker):
            raise AdmissionError("speaker_not_anonymous_label", f"{field}.speaker")
        normalized.append({"start_sample": start, "end_sample": end, "speaker": speaker})
    for i in range(len(normalized) - 1):
        a, b = normalized[i], normalized[i + 1]
        if (b["start_sample"], b["end_sample"], b["speaker"]) < (a["start_sample"], a["end_sample"], a["speaker"]):
            raise AdmissionError("segments_not_sorted", "timeline.segments")
        if b["start_sample"] < a["end_sample"] and b["speaker"] == a["speaker"]:
            raise AdmissionError("segments_overlap_same_speaker", "timeline.segments")
    return normalized


def envelope_manifest(case_id: str) -> dict[str, Any]:
    sample_count = 19200
    if case_id == "single_speaker":
        segments = [{"start_sample": 0, "end_sample": 16000, "speaker": "spk_00"}]
    elif case_id == "two_speakers":
        segments = [
            {"start_sample": 0, "end_sample": 8000, "speaker": "spk_00"},
            {"start_sample": 8000, "end_sample": 16000, "speaker": "spk_01"},
        ]
    elif case_id == "overlap":
        segments = [
            {"start_sample": 0, "end_sample": 12000, "speaker": "spk_00"},
            {"start_sample": 8000, "end_sample": 16000, "speaker": "spk_01"},
        ]
    elif case_id == "sparse_gap":
        segments = [
            {"start_sample": 1600, "end_sample": 4800, "speaker": "spk_00"},
            {"start_sample": 9600, "end_sample": 12800, "speaker": "spk_01"},
        ]
    else:
        raise ValueError(case_id)
    peak = "0.78125"
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "request_id": case_id,
        "mode": "offline",
        "candidate": {
            "name": COMPONENT_ID,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "revision": None,
            "license": None,
        },
        "input": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_count": sample_count,
            "dtype": "float32",
            "finite": True,
            "peak": peak,
        },
        "timeline": {
            "segment_count": len(segments),
            "segments_sha256": segments_digest(segments),
            "anonymous_only": True,
            "overlap_allowed": any(s["speaker"] != t["speaker"] and max(s["start_sample"], t["start_sample"]) < min(s["end_sample"], t["end_sample"]) for i, s in enumerate(segments) for t in segments[i + 1:]),
        },
        "controls": [
            {"id": "candidate", "kind": "candidate"},
            {"id": "identity", "kind": "identity_timeline"},
            {"id": "missing-runtime", "kind": "missing_runtime"},
            {"id": "nonfinite", "kind": "nonfinite_rejection"},
        ],
        "rights": {
            "source_terms": "not_staged",
            "weight_terms": "not_staged",
            "input_terms": "synthetic_only",
            "output_use": "task_local_evidence_only",
            "claims_qualified": False,
        },
    }


def validate_manifest(manifest: Any) -> dict[str, Any]:
    obj = _require_object(manifest, "manifest")
    _require_keys(obj, MANIFEST_FIELDS, "manifest")
    if obj["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("schema_id_mismatch", "schema_id")
    request_id = _require_slug(obj["request_id"], "request_id")
    if obj["mode"] not in RUN_MODES:
        raise AdmissionError("mode_unsupported", "mode")

    candidate = _require_object(obj["candidate"], "candidate")
    _require_keys(candidate, CANDIDATE_FIELDS, "candidate")
    if candidate["name"] != COMPONENT_ID:
        raise AdmissionError("candidate_name_mismatch", "candidate.name")
    for key in ("source_present", "weights_present", "runtime_present"):
        value = candidate[key]
        if type(value) is not bool:
            raise AdmissionError(f"{key}_not_bool", f"candidate.{key}")
        if value is not False:
            raise AdmissionError(f"{key}_must_be_false", f"candidate.{key}")
    if candidate["revision"] is not None:
        raise AdmissionError("candidate_artifact_unpinned", "candidate.revision")
    if candidate["license"] is not None:
        raise AdmissionError("candidate_artifact_unpinned", "candidate.license")

    input_obj = _require_object(obj["input"], "input")
    _require_keys(input_obj, INPUT_FIELDS, "input")
    sample_rate = _require_int(input_obj["sample_rate_hz"], "input.sample_rate_hz")
    if sample_rate != SAMPLE_RATE_HZ:
        raise AdmissionError("input_rate_unsupported", "input.sample_rate_hz")
    channels = _require_int(input_obj["channels"], "input.channels")
    if channels != CHANNELS:
        raise AdmissionError("input_channels_unsupported", "input.channels")
    sample_count = _require_int(input_obj["sample_count"], "input.sample_count", minimum=1, maximum=MAX_SAMPLE_COUNT)
    if input_obj["dtype"] != "float32":
        raise AdmissionError("input_dtype_unsupported", "input.dtype")
    if _require_bool(input_obj["finite"], "input.finite") is not True:
        raise AdmissionError("input_finite_must_be_true", "input.finite")
    _require_decimal(input_obj["peak"], "input.peak")

    timeline = _require_object(obj["timeline"], "timeline")
    _require_keys(timeline, TIMELINE_FIELDS, "timeline")
    seg_count = _require_int(timeline["segment_count"], "timeline.segment_count", minimum=1, maximum=MAX_SEGMENTS)
    digest = _require_sha256(timeline["segments_sha256"], "timeline.segments_sha256")
    if _require_bool(timeline["anonymous_only"], "timeline.anonymous_only") is not True:
        raise AdmissionError("anonymous_only_must_be_true", "timeline.anonymous_only")
    overlap_allowed = _require_bool(timeline["overlap_allowed"], "timeline.overlap_allowed")

    controls = obj["controls"]
    if not isinstance(controls, list) or not controls or len(controls) > MAX_CONTROLS:
        raise AdmissionError("controls_invalid", "controls")
    seen_ids = set()
    kinds = set()
    for index, control in enumerate(controls):
        field = f"controls[{index}]"
        control_obj = _require_object(control, field)
        _require_keys(control_obj, CONTROL_FIELDS, field)
        control_id = _require_slug(control_obj["id"], f"{field}.id")
        if control_id in seen_ids:
            raise AdmissionError("control_id_duplicate", f"{field}.id")
        seen_ids.add(control_id)
        kind = control_obj["kind"]
        if kind not in CONTROL_KINDS:
            raise AdmissionError("control_kind_unknown", f"{field}.kind")
        kinds.add(kind)
    if not REQUIRED_CONTROL_KINDS.issubset(kinds):
        raise AdmissionError("control_kind_missing", "controls")

    rights = _require_object(obj["rights"], "rights")
    _require_keys(rights, RIGHTS_FIELDS, "rights")
    for key in ("source_terms", "weight_terms", "input_terms", "output_use"):
        value = rights[key]
        if not isinstance(value, str) or not value.strip():
            raise AdmissionError("rights_source_terms_empty" if key == "source_terms" else "rights_missing_keys", f"rights.{key}")
    if _require_bool(rights["claims_qualified"], "rights.claims_qualified") is not False:
        raise AdmissionError("claims_qualified_must_be_false", "rights.claims_qualified")

    # Envelope self-consistency checks for the synthetic reference manifests.
    envelope_segments = {
        "single_speaker": [{"start_sample": 0, "end_sample": 16000, "speaker": "spk_00"}],
        "two_speakers": [{"start_sample": 0, "end_sample": 8000, "speaker": "spk_00"}, {"start_sample": 8000, "end_sample": 16000, "speaker": "spk_01"}],
        "overlap": [{"start_sample": 0, "end_sample": 12000, "speaker": "spk_00"}, {"start_sample": 8000, "end_sample": 16000, "speaker": "spk_01"}],
        "sparse_gap": [{"start_sample": 1600, "end_sample": 4800, "speaker": "spk_00"}, {"start_sample": 9600, "end_sample": 12800, "speaker": "spk_01"}],
    }
    if request_id not in envelope_segments:
        raise AdmissionError("request_id_unknown", "request_id")
    segments = envelope_segments[request_id]
    validated = validate_segments(segments, sample_count)
    if len(validated) != seg_count:
        raise AdmissionError("segment_count_mismatch", "timeline.segment_count")
    if segments_digest(validated) != digest:
        raise AdmissionError("segments_digest_mismatch", "timeline.segments_sha256")
    actual_overlap = any(s["speaker"] != t["speaker"] and max(s["start_sample"], t["start_sample"]) < min(s["end_sample"], t["end_sample"]) for i, s in enumerate(validated) for t in validated[i + 1:])
    if actual_overlap != overlap_allowed:
        raise AdmissionError("overlap_flag_mismatch", "timeline.overlap_allowed")

    return {
        "request_id": request_id,
        "accepted": True,
        "segment_count": seg_count,
        "segments_sha256": digest,
        "overlap_allowed": overlap_allowed,
        "qualified": False,
    }


def admission_rejections() -> dict[str, Any]:
    base = envelope_manifest("single_speaker")
    cases: list[tuple[str, dict[str, Any], str]] = []

    def add(case_id: str, mutator, code: str) -> None:
        manifest = copy.deepcopy(base)
        mutator(manifest)
        cases.append((case_id, manifest, code))

    add("missing_timeline", lambda m: m.pop("timeline"), "missing_field")
    extra = copy.deepcopy(base); extra["extra"] = 1
    cases.append(("extra_top_level_key", extra, "unknown_field"))
    add("bad_schema_id", lambda m: m.__setitem__("schema_id", "bad"), "schema_id_mismatch")
    add("bad_request_id", lambda m: m.__setitem__("request_id", "Bad Id"), "invalid_slug")
    add("unknown_request_id", lambda m: m.__setitem__("request_id", "unknown_case"), "request_id_unknown")
    add("unsupported_mode", lambda m: m.__setitem__("mode", "online"), "mode_unsupported")
    add("candidate_name_mismatch", lambda m: m["candidate"].__setitem__("name", "other"), "candidate_name_mismatch")
    add("candidate_source_claimed", lambda m: m["candidate"].__setitem__("source_present", True), "source_present_must_be_false")
    add("candidate_weights_claimed", lambda m: m["candidate"].__setitem__("weights_present", True), "weights_present_must_be_false")
    add("candidate_runtime_claimed", lambda m: m["candidate"].__setitem__("runtime_present", True), "runtime_present_must_be_false")
    add("candidate_revision_unpinned", lambda m: m["candidate"].__setitem__("revision", "deadbeef"), "candidate_artifact_unpinned")
    add("candidate_license_unpinned", lambda m: m["candidate"].__setitem__("license", "MIT"), "candidate_artifact_unpinned")
    add("candidate_flag_not_bool", lambda m: m["candidate"].__setitem__("source_present", 1), "source_present_not_bool")
    add("input_rate_8k", lambda m: m["input"].__setitem__("sample_rate_hz", 8000), "input_rate_unsupported")
    add("input_stereo", lambda m: m["input"].__setitem__("channels", 2), "input_channels_unsupported")
    add("input_zero_samples", lambda m: m["input"].__setitem__("sample_count", 0), "out_of_range")
    add("input_oversized", lambda m: m["input"].__setitem__("sample_count", MAX_SAMPLE_COUNT + 1), "out_of_range")
    add("input_float_count", lambda m: m["input"].__setitem__("sample_count", 1.5), "not_integer")
    add("input_dtype_f16", lambda m: m["input"].__setitem__("dtype", "float16"), "input_dtype_unsupported")
    add("input_nonfinite", lambda m: m["input"].__setitem__("finite", False), "input_finite_must_be_true")
    add("input_peak_nan", lambda m: m["input"].__setitem__("peak", "NaN"), "peak_not_canonical")
    add("input_peak_over_one", lambda m: m["input"].__setitem__("peak", "1.1"), "peak_out_of_range")
    add("input_peak_not_canonical", lambda m: m["input"].__setitem__("peak", "1.0"), "peak_not_canonical")
    add("timeline_bad_count", lambda m: m["timeline"].__setitem__("segment_count", 2), "segment_count_mismatch")
    add("timeline_bad_digest", lambda m: m["timeline"].__setitem__("segments_sha256", "0" * 64), "segments_digest_mismatch")
    add("timeline_not_anonymous", lambda m: m["timeline"].__setitem__("anonymous_only", False), "anonymous_only_must_be_true")
    add("timeline_overlap_flag_wrong", lambda m: m["timeline"].__setitem__("overlap_allowed", True), "overlap_flag_mismatch")
    add("timeline_digest_bad_hex", lambda m: m["timeline"].__setitem__("segments_sha256", "xyz"), "digest_invalid")
    extra_timeline = copy.deepcopy(base); extra_timeline["timeline"]["extra"] = 1
    cases.append(("timeline_extra_key", extra_timeline, "unknown_field"))
    add("controls_empty", lambda m: m.__setitem__("controls", []), "controls_invalid")
    add("controls_missing_candidate", lambda m: m.__setitem__("controls", [{"id":"x","kind":"identity_timeline"}]), "control_kind_missing")
    add("controls_duplicate_id", lambda m: m.__setitem__("controls", [{"id":"c","kind":"candidate"},{"id":"c","kind":"identity_timeline"},{"id":"m","kind":"missing_runtime"},{"id":"n","kind":"nonfinite_rejection"}]), "control_id_duplicate")
    add("controls_unknown_kind", lambda m: m.__setitem__("controls", [{"id":"c","kind":"candidate"},{"id":"i","kind":"identity_timeline"},{"id":"m","kind":"missing_runtime"},{"id":"n","kind":"other"}]), "control_kind_unknown")
    add("controls_too_many", lambda m: m.__setitem__("controls", [{"id":f"c{i}","kind":"candidate" if i==0 else "identity_timeline" if i==1 else "missing_runtime" if i==2 else "nonfinite_rejection"} for i in range(MAX_CONTROLS + 1)]), "controls_invalid")
    add("rights_claims_qualified", lambda m: m["rights"].__setitem__("claims_qualified", True), "claims_qualified_must_be_false")
    add("rights_empty_source", lambda m: m["rights"].__setitem__("source_terms", ""), "rights_source_terms_empty")
    add("rights_missing_output_use", lambda m: m["rights"].pop("output_use"), "missing_field")
    rights_extra = copy.deepcopy(base); rights_extra["rights"]["extra"] = "x"
    cases.append(("rights_extra_field", rights_extra, "unknown_field"))
    add("controls_not_list", lambda m: m.__setitem__("controls", {}), "controls_invalid")
    add("timeline_not_object", lambda m: m.__setitem__("timeline", []), "not_object")

    rejections = []
    for case_id, manifest, expected in cases:
        try:
            validate_manifest(manifest)
        except AdmissionError as error:
            rejections.append({"id": case_id, "code": error.code, "field": error.field, "expected": expected, "rejected": True})
        else:
            rejections.append({"id": case_id, "code": "accepted", "field": "", "expected": expected, "rejected": False})
    return {
        "cases": len(rejections),
        "all_rejected": all(item["rejected"] and item["code"] == item["expected"] for item in rejections),
        "rejections": rejections,
    }


def strict_json_rejections() -> dict[str, Any]:
    cases = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_literal": '{"a":NaN}',
        "infinity_literal": '{"a":Infinity}',
        "negative_infinity_literal": '{"a":-Infinity}',
        "trailing_data": '{"a":1}x',
        "byte_order_mark": '\ufeff{"a":1}',
        "non_object_root": "[1,2]",
        "empty_input": "  ",
        "unterminated": '{"a":1',
    }
    rows = []
    for case_id, payload in cases.items():
        try:
            loads_strict(payload)
        except ValueError:
            rows.append({"id": case_id, "rejected": True})
        else:
            rows.append({"id": case_id, "rejected": False})
    return {"cases": len(rows), "all_rejected": all(row["rejected"] for row in rows), "rejections": rows}


def protocol_envelope() -> dict[str, Any]:
    cases = []
    for case_id in ("single_speaker", "two_speakers", "overlap", "sparse_gap"):
        manifest = envelope_manifest(case_id)
        accepted = validate_manifest(manifest)
        timeline = manifest["timeline"]
        cases.append({
            "id": case_id,
            "accepted_manifest_sha256": object_digest(manifest),
            "segments_sha256": timeline["segments_sha256"],
            "segment_count": timeline["segment_count"],
            "overlap_allowed": timeline["overlap_allowed"],
            "anonymous_only": timeline["anonymous_only"],
            "accepted": accepted["accepted"],
        })
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "purpose": "Deterministic synthetic timestamped anonymous speaker-label intervals. Protocol plumbing only; not diarization, not DER/JER, not speaker identity, not audio processing.",
        "not_candidate": True,
        "synthesizes_audio": False,
        "loads_model": False,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "case_count": len(cases),
        "cases": cases,
    }


def boundary_block() -> dict[str, Any]:
    linked = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    return {
        "linked_row": linked,
        "linked_row_sha256": board_row_digest(linked),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "projected_fields": list(BOARD_ROW_FIELDS),
        "excluded_mutable_fields": list(MUTABLE_BOARD_FIELDS),
        "board_file_pinned": False,
        "linked_row_identity_only": True,
        "mutable_board_fields_gate": False,
    }


def exact_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "BLK-01",
            "artifact_id": "ART-02",
            "linked_gates": ["RG-01"],
            "qualifies": False,
            "status": "open",
            "statement": "No exact licensed pyannote diarization source, immutable revision, model card, or per-file manifest is staged in this worktree.",
            "required_action": "Stage the exact upstream pyannote.audio/diarization source and model card at an immutable revision with complete license, notice, and attribution records; no download is permitted in this package.",
        },
        {
            "id": "BLK-02",
            "artifact_id": "ART-03",
            "linked_gates": ["RG-01", "RG-02"],
            "qualifies": False,
            "status": "open",
            "statement": "No exact model weights, Hugging Face access terms, or caller-supplied asset manifest is staged or reviewable.",
            "required_action": "Provide reviewed access terms and an exact caller-supplied asset manifest with IDs, byte counts, SHA-256 digests, and immutable source revisions for every required weight/model artifact.",
        },
        {
            "id": "BLK-03",
            "artifact_id": "ART-04",
            "linked_gates": ["RG-02", "RG-03"],
            "qualifies": False,
            "status": "open",
            "statement": "No pinned offline runtime, dependency lock, or clean-room install/import digest is present for pyannote diarization.",
            "required_action": "Provide a locked offline runtime and dependency manifest with wheel/package hashes, install location, clean-room import digest, and no network requirement.",
        },
        {
            "id": "BLK-04",
            "artifact_id": "ART-05",
            "linked_gates": ["RG-04"],
            "qualifies": False,
            "status": "open",
            "statement": "No rights-cleared diarization corpus, RTTM/UEM reference, scoring regions, or derived-output/redistribution decision is staged.",
            "required_action": "Freeze a reviewed rights-cleared corpus with RTTM/UEM/reference labels, scored regions, acquisition/evaluation/derived-output/redistribution decisions, and digest pins.",
        },
        {
            "id": "BLK-05",
            "artifact_id": "ART-06",
            "linked_gates": ["RG-05", "RG-06"],
            "qualifies": False,
            "status": "open",
            "statement": "No deterministic diarization execution, anonymous-label timeline, DER/JER, overlap handling, or control/ablation result exists.",
            "required_action": "Run the pinned candidate offline on rights-cleared inputs with exact hashes, anonymous speaker labels kept separate from identity, DER/JER or task-matched metrics, overlap/online controls, and exact repeats.",
        },
        {
            "id": "BLK-06",
            "artifact_id": "ART-07",
            "linked_gates": ["RG-07", "RG-08"],
            "qualifies": False,
            "status": "open",
            "statement": "No mode/platform timing, resource, pacing, device, listening/labeled-screen, provider-intake, or independent review evidence exists.",
            "required_action": "Measure mode/platform timing and resources, complete authorized listening or labeled screen if used, then open a separate OFF-by-default intake with clean-install proof and independent exact-head review.",
        },
    ]


def release_gates() -> list[dict[str, Any]]:
    task_row = next(row for row in linked_rows() if row["id"] == TASK)
    specs = [
        ("RG-01", "source_revision_and_license_provenance", "No exact source, immutable revision, license text, or notice is staged.", "Stage the exact upstream pyannote source/model card at immutable revision with complete license/notice/attribution and independent review."),
        ("RG-02", "pinned_assets_and_offline_runtime", "No exact weights, Hugging Face terms, pinned runtime, dependency lock, or clean-room install digest is recorded.", "Provide reviewed access terms, caller-supplied asset manifest, and locked offline runtime with hashes and clean-room import digest."),
        ("RG-03", "exact_task_geometry_and_scope", "No exact audio geometry, diarization scope, overlap/online semantics, or anonymous-label boundary is pinned for a runnable candidate.", "Pin sample rate/channels/windowing/latency/reset behavior and preserve anonymous speaker labels separate from verification/identity."),
        ("RG-04", "rights_cleared_corpus_and_references", "No rights-cleared diarization corpus, RTTM/UEM/reference labels, scored regions, or redistribution decision is staged.", "Freeze reviewed rights-cleared inputs/references with acquisition, evaluation, derived-output, and redistribution decisions."),
        ("RG-05", "deterministic_execution_and_output_validity", "No deterministic candidate execution, output hashes, exact repeats, or anonymous-label timeline validity exists.", "Execute pinned candidate offline and record deterministic output hashes, finite/valid timelines, exact repeats, and peak/RSS/resource bounds."),
        ("RG-06", "spatial_profile_and_diarization_metrics", "No Spatial-profile measurement, DER/JER/task-matched metric, overlap control, or identity-separation evidence exists.", "Run every required Spatial-profile case on rights-cleared inputs with task-matched labels, overlap representation, anonymous IDs separate from verification, and controls."),
        ("RG-07", "mode_platform_timing_resources_and_listening", "No mode/platform timing, resources, pacing, device behavior, or authorized listening/labeled screen exists.", "Measure each mode/platform separately with timing, resources, pacing, and complete authorized listening or labeled screen where required."),
        ("RG-08", "provider_intake_public_surface_and_release", "No provider, descriptor, registry entry, default, shared-build change, clean-install proof, or independent review exists.", "Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear."),
    ]
    return [{
        "id": gid, "title": title, "status": "blocked", "qualifies": False,
        "statement": statement, "reopen_condition": reopen, "linked_row": task_row,
    } for gid, title, statement, reopen in specs]


def spatial_profile() -> dict[str, Any]:
    blocked = "No candidate source, runtime, rights-cleared input, reference labels, or output exists; this item cannot be measured."
    reqs = [
        ("SPAT-01", "Geometry/layout/timestamp calibration and task scope for the exact runtime.", "blocked"),
        ("SPAT-02", "Anonymous speaker-label timeline with overlap represented; labels not enrolled identities.", "blocked"),
        ("SPAT-03", "Diarization compared with task-matched held-out labels on scored regions.", "blocked"),
        ("SPAT-04", "DER/JER or task-matched speaker-error metrics with collar/UEM policy recorded.", "blocked"),
        ("SPAT-05", "Leakage/false alarm, missed speech/target damage, and channel-loss/room/reference condition changes.", "blocked"),
        ("SPAT-06", "Online revision behavior and finalization semantics, if claimed.", "blocked"),
        ("SPAT-07", "Silence/empty input and invalid/nonfinite input handling.", "blocked"),
        ("SPAT-08", "Mode/platform timing, resources, pacing, and device behavior.", "blocked"),
        ("SPAT-09", "Separate paired, unpaired, synthetic, human, and source-reported evidence; no missing result promoted.", "documented"),
    ]
    rows = []
    for rid, requirement, status in reqs:
        evidence = blocked
        if rid == "SPAT-09":
            evidence = "Synthetic envelope, admission, source-reported, and missing-real sections stay separate; no category is pooled."
        rows.append({"id": rid, "requirement": requirement, "status": status, "qualifies": False, "evidence": evidence})
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_envelope_only": True,
        "conditions": [
            "anonymous_labels_only", "overlap_represented", "task_matched_labels",
            "scored_regions", "silence_empty", "invalid_nonfinite", "online_revision_if_claimed",
        ],
        "requirement_rows": rows,
        "candidate_der_result": None,
        "candidate_timeline_result": None,
        "candidate_overlap_result": None,
        "candidate_geometry": None,
    }


def required_artifacts() -> list[dict[str, Any]]:
    return [
        {"id": "ART-01", "kind": "evidence_register_and_policy_boundary", "present": True, "blocked": False, "verified": True, "revision": None, "sha256": None, "requirement": "Pinned task row, Spatial acceptance profile, SDK delivery plan, inventory/category records, sibling SPK-04 survey, and unchanged v0 contract boundary."},
        {"id": "ART-02", "kind": "exact_upstream_source_or_reference", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Exact licensed pyannote diarization source/reference at immutable revision with license text, notices, and per-file manifest."},
        {"id": "ART-03", "kind": "exact_model_assets_and_access_terms", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Reviewed model/HF access terms and exact caller-supplied asset manifest with IDs, byte counts, SHA-256 digests, and immutable revisions."},
        {"id": "ART-04", "kind": "pinned_runtime_and_dependencies", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Locked offline runtime and dependency manifest with hashes, install location, and clean-room import digest."},
        {"id": "ART-05", "kind": "rights_cleared_corpus_and_references", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Rights-cleared diarization corpus with RTTM/UEM/reference labels, scored regions, and acquisition/evaluation/derived-output/redistribution decisions."},
        {"id": "ART-06", "kind": "reproduced_spatial_results", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Deterministic anonymous-label diarization outputs with DER/JER/task-matched metrics, overlap controls, identity separation, and exact repeats."},
        {"id": "ART-07", "kind": "provider_intake_and_public_surface", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Separate versioned OFF-by-default provider intake with clean-install proof, no shared-build/default change, and independent exact-head review."},
    ]


def source_reported_identity() -> dict[str, Any]:
    return {
        "candidate": TASK_TITLE,
        "source_reported_only": True,
        "verified": False,
        "official_repository": None,
        "immutable_revision_recorded": False,
        "license_recorded": False,
        "license_text_staged": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "runtime_recorded": False,
        "runnable_as_released": False,
        "task": "speaker_diarization",
        "output_kind": "timestamped_anonymous_speaker_labels",
        "anonymous_labels_only": True,
        "overlap_representation_required": True,
        "online_revisions_possible": True,
        "speaker_identity_is_separate_category": True,
        "released_content": [],
        "release_state": "no exact licensed implementation, weights, or rights-cleared corpus staged",
    }


def required_results() -> list[str]:
    return [
        "Exact upstream pyannote source/reference, immutable revision, license text, notices, and model card.",
        "Reviewed Hugging Face/access terms and exact caller-supplied asset manifest with IDs, byte counts, SHA-256 digests, and immutable revisions.",
        "Locked offline runtime with dependency/wheel hashes, install location, and clean-room import digest.",
        "Rights-cleared diarization corpus with RTTM/UEM/reference labels, scored regions, and acquisition/evaluation/derived-output/redistribution decisions.",
        "Deterministic anonymous speaker-label timelines with exact hashes, exact repeats, overlap representation, and identity separation.",
        "DER/JER or task-matched Spatial-profile metrics, controls, and adverse/invalid/nonfinite handling on rights-cleared inputs.",
        "Mode/platform timing, resources, pacing, authorized listening/labeled screen where required, and independent OFF-by-default intake review.",
    ]


def reopening_conditions() -> list[str]:
    return [gate["reopen_condition"] for gate in release_gates()]


def public_v0_geometry() -> dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": "float32",
        "unchanged": True,
    }


def build_contract() -> dict[str, Any]:
    rows = linked_rows()
    task_row = next(row for row in rows if row["id"] == TASK)
    gates = release_gates()
    blockers = exact_blockers()
    artifacts = required_artifacts()
    envelope = protocol_envelope()
    admission = admission_rejections()
    strict = strict_json_rejections()
    absence = absence_summary()
    snippets = evidence_snippet_check()
    sp = spatial_profile()
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": DISPOSITION,
        "boundary": {
            **boundary_block(),
            "task_row": task_row,
        },
        "public_v0_geometry": public_v0_geometry(),
        "source_reported_identity": source_reported_identity(),
        "absence_probes": absence["probes"],
        "evidence_snippets": snippets["checks"],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "candidate_fields": list(CANDIDATE_FIELDS),
            "input_fields": list(INPUT_FIELDS),
            "timeline_fields": list(TIMELINE_FIELDS),
            "segment_fields": list(SEGMENT_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "max_sample_count": MAX_SAMPLE_COUNT,
            "max_segments": MAX_SEGMENTS,
            "max_controls": MAX_CONTROLS,
            "qualifies": False,
        },
        "protocol_envelope": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "case_count": envelope["case_count"],
            "cases": envelope["cases"],
            "not_candidate": True,
            "synthesizes_audio": False,
        },
        "admission": {
            "manifest_cases": admission["cases"],
            "all_rejected": admission["all_rejected"],
            "strict_json_cases": strict["cases"],
            "strict_json_all_rejected": strict["all_rejected"],
        },
        "spatial_profile": sp,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "release_gates": gates,
        "required_results": required_results(),
        "reopening_conditions": reopening_conditions(),
        "non_claims": [
            "No pyannote source, model, weight, runtime, corpus, RTTM/UEM reference, or diarization output is present, imported, loaded, downloaded, or executed.",
            "No DER/JER, speaker-error, overlap, online-revision, device-timing, listening, benchmark, or release result is reproduced.",
            "The synthetic anonymous-label envelope and admission control are protocol plumbing only; they are not diarization and not qualification.",
            "Anonymous speaker labels are not enrolled identities; no speaker identity/verification claim is made.",
            "No provider, descriptor, registry, default, public ABI, shared build, or CI change exists.",
            "Research prose and inventory/category references are source-reported context only and are not promoted to measured evidence.",
        ],
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    absence = absence_summary()
    snippets = evidence_snippet_check()
    admission = admission_rejections()
    strict = strict_json_rejections()
    envelope = protocol_envelope()
    gates = release_gates()
    blockers = exact_blockers()
    artifacts = required_artifacts()
    sp = spatial_profile()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "generated_by": "docs/task-evidence/pyannote-diarization/run.py",
        "disposition": DISPOSITION,
        "boundary": contract["boundary"],
        "boundary_pins": BOUNDARY_PINS,
        "source_pins": SOURCE_PINS,
        "public_v0_geometry": public_v0_geometry(),
        "source_reported_identity": source_reported_identity(),
        "absence_evidence": absence,
        "evidence_presence": {
            "all_snippets_present": snippets["all_present"],
            "snippet_count": snippets["count"],
            "snippets": snippets["checks"],
            "source_present": False,
            "runtime_present": False,
            "weights_present": False,
            "corpus_present": False,
            "license_text_present": False,
        },
        "runtime_readiness": runtime_readiness(),
        "admission": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "manifest_cases": admission["cases"],
            "all_rejected": admission["all_rejected"],
            "rejections": admission["rejections"],
            "strict_json_cases": strict["cases"],
            "strict_json_all_rejected": strict["all_rejected"],
            "strict_json_rejections": strict["rejections"],
            "assets_never_loaded": True,
            "accepts": "Only an offline manifest that declares absent candidate artifacts, canonical anonymous-label fields, and closed rights terms.",
        },
        "protocol_envelope": envelope,
        "spatial_profile": sp,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "gates": gates,
        "release_gates": gates,
        "required_results": required_results(),
        "reopening_conditions": reopening_conditions(),
        "non_claims": contract["non_claims"],
        "qualification": {
            "status": "not_qualified",
            "not_qualified": True,
            "readiness": "incomplete",
            "candidate_present": False,
            "source_present": False,
            "runtime_present": False,
            "weights_present": False,
            "corpus_present": False,
            "license_text_present": False,
            "runtime_pinned": False,
            "real_result_present": False,
            "diarization_result": False,
            "der_jer_result": False,
            "overlap_result": False,
            "online_revision_result": False,
            "device_timing_result": False,
            "listening_result": False,
            "benchmark_result": False,
            "release_claim": False,
            "missing_result_promoted": False,
            "all_release_gates_blocked": True,
        },
        "scope": {
            "task_local_only": True,
            "write_scope": WRITE_SCOPE,
            "installed_v0_changed": False,
            "public_abi_changed": False,
            "provider_registered": False,
            "registry_or_default_changed": False,
            "shared_build_or_ci_changed": False,
            "real_assets_used": False,
            "reference_implemented": False,
            "reference_executed": False,
            "network_used": False,
            "device_timing_measured": False,
            "listening_performed": False,
            "benchmark_run": False,
            "release_claim": False,
        },
        "reproduction": {
            "canonical_json": True,
            "sorted_keys": True,
            "trailing_newline": False,
            "byte_identical": True,
            "repeat_count": 3,
            "report_sha256_sidecar": "report.json.sha256",
            "interpreter": REQUIRED_INTERPRETER,
        },
        "contract_sha256": object_digest(contract),
    }


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)
    return text, hashlib.sha256(text.encode("ascii")).hexdigest()
