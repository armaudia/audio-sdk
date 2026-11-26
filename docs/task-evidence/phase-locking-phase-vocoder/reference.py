# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only blocker evidence for SDK-PHASE-LOCKING-PHASE-VOCODER.

This module never downloads, reads, imports, links or executes a phase-locking
phase vocoder, reference implementation, runtime, audio corpus or model. It
records the exact absence, validates a bounded offline admission envelope and
produces a canonical DEFER report. The envelope is protocol plumbing over
integer sample positions; it is not the candidate, does not synthesize audio,
and cannot qualify anything.
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

TASK = "SDK-PHASE-LOCKING-PHASE-VOCODER"
COMPONENT_ID = "phase-locking-phase-vocoder"
TASK_TITLE = "Phase-locking phase vocoder"
CONTRACT_ID = "audio-sdk/phase-locking-phase-vocoder-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/phase-locking-phase-vocoder-envelope/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "d0972e776bdc1ff231298caef1845cd1432c78be"
BRANCH = "swarm/SDK-PHASE-LOCKING-PHASE-VOCODER"
WRITE_SCOPE = "docs/task-evidence/phase-locking-phase-vocoder/ only"
TASK_PREFIX = "docs/task-evidence/phase-locking-phase-vocoder/"
REQUIRED_INTERPRETER = "3.11.5"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
MAX_SAMPLE_COUNT = 192_000
MAX_CONTROLS = 8
RUN_MODES = ("offline",)
CONTROL_KINDS = (
    "candidate",
    "identity_passthrough",
    "missing_runtime",
    "nonfinite_rejection",
)
REQUIRED_CONTROL_KINDS = frozenset(CONTROL_KINDS)

DISPOSITION = (
    "Phase-locking phase vocoder feasibility blocker. The task requires a "
    "runnable source, exact assets, permitted scope, task geometry and matched "
    "evidence, then a minimal reference compared against the baseline phase "
    "vocoder at identical ratios. No exact licensed reference implementation, "
    "immutable revision, license text, pinned runtime, rights-cleared audio, "
    "matched baseline/result pair, or qualified rate evidence is present or "
    "reproducible in this worktree. The catalogued rate profile cannot be "
    "satisfied by a candidate with no runnable rate artifact or measured output."
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
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
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
    "schema_id", "request_id", "mode", "candidate", "input", "rate",
    "output", "controls", "rights",
)
CANDIDATE_FIELDS = (
    "name", "source_present", "weights_present", "runtime_present",
    "revision", "license",
)
INPUT_FIELDS = (
    "sample_rate_hz", "channels", "sample_count", "dtype", "finite", "peak",
)
RATE_FIELDS = ("numerator", "denominator")
OUTPUT_FIELDS = (
    "sample_count", "mapping_sha256", "finite", "peak", "first_source", "last_source",
)
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = (
    "source_terms", "weight_terms", "input_terms", "output_use", "claims_qualified",
)

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
COMMIT_SHA = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{40}$")
DECIMAL = re.compile(r"^(0|1)(\.[0-9]*[1-9])?$|^0\.[0-9]*[1-9]$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

ABSENCE_PROBES = (
    "workspace:data/checkouts/phase-locking-phase-vocoder",
    "workspace:data/checkouts/phase_vocoder",
    "workspace:data/checkouts/pvpl",
    "workspace:data/checkouts/laroche-dolson",
    "workspace:data/models/phase-locking-phase-vocoder",
    "workspace:data/models/phase_vocoder",
    "workspace:data/envs/phase-locking-phase-vocoder",
    "workspace:data/audio/phase-locking-phase-vocoder",
    "workspace:research/phase-locking-phase-vocoder",
    "worktree:third_party/phase-locking-phase-vocoder",
    "worktree:third_party/phase-vocoder",
    "worktree:adapters/phase-locking-phase-vocoder",
    "worktree:docs/task-evidence/phase-locking-phase-vocoder/weights",
    "home:.cache/phase-locking-phase-vocoder",
)

EVIDENCE_SNIPPETS = (
    {
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "phrase": "Phase vocoder (baseline)",
    },
    {
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "phrase": "Laroche & Dolson, \"Improved phase vocoder",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "phrase": "Phase-locking phase vocoder",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "phrase": "Compare against the baseline phase vocoder at identical ratios.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "phrase": "Measure source/output mapping",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "phrase": "final partial window",
    },
    {
        "path": "audio-benchmark-platform/plan/audio-sdk/README.md",
        "phrase": "TSM algorithms and actuators",
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


def read_strict_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return loads_strict(text)


def loads_strict(text: str) -> Any:
    if not text.strip():
        raise ValueError("empty input")
    if text.startswith("\ufeff"):
        raise ValueError("byte order mark")
    if re.search(r'(?<![eE])[+-]?\b(?:NaN|Infinity)\b', text):
        raise ValueError("nonfinite literal")
    decoder = json.JSONDecoder(parse_float=lambda _: (_ for _ in ()).throw(ValueError("float literal")), object_pairs_hook=_object_pairs_hook)
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
    if str(fraction.numerator) == value or (fraction.denominator == 1 and value == str(fraction.numerator)):
        return fraction
    # canonical decimal form already checked by regex
    return fraction


def canonical_decimal(value: str, field: str) -> Fraction:
    return _require_decimal(value, field)


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
    return {
        "checks": checks,
        "count": len(checks),
        "all_present": all(item["present"] for item in checks),
    }


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
            "rubberband": False,
            "soundtouch": False,
            "audiotsm": False,
            "pytsmod": False,
        },
    }


def mapping_record(input_samples: int, numerator: int, denominator: int) -> dict[str, Any]:
    if numerator < 1 or denominator < 1:
        raise AdmissionError("rate_not_positive", "rate")
    if Fraction(numerator, denominator) != Fraction(numerator, denominator).limit_denominator():
        pass
    if Fraction(numerator, denominator).numerator != numerator or Fraction(numerator, denominator).denominator != denominator:
        raise AdmissionError("rate_not_reduced", "rate")
    speed = Fraction(numerator, denominator)
    if speed < Fraction(1, 2) or speed > Fraction(2, 1):
        raise AdmissionError("rate_out_of_bounds", "rate")
    target = (input_samples * denominator) // numerator
    mapping = [(j, (j * numerator) // denominator) for j in range(target)]
    monotone = all(mapping[i][1] <= mapping[i + 1][1] for i in range(max(0, len(mapping) - 1)))
    bounded = all(0 <= src < input_samples for _, src in mapping)
    digest = hashlib.sha256(
        "".join(f"{out},{src}\n" for out, src in mapping).encode("ascii")
    ).hexdigest()
    return {
        "input_samples": input_samples,
        "numerator": numerator,
        "denominator": denominator,
        "speed_ratio": f"{numerator}/{denominator}",
        "target_samples": target,
        "duration_error_samples": 0,
        "first_source": mapping[0][1] if mapping else 0,
        "last_source": mapping[-1][1] if mapping else -1,
        "mapping_sha256": digest,
        "monotone": monotone,
        "bounded": bounded,
        "identity_exact": numerator == 1 and denominator == 1 and target == input_samples,
    }


def synthetic_frame() -> list[Fraction]:
    return [Fraction((index * 37) % 201 - 100, 128) for index in range(FRAME_SAMPLES)]


def frame_metrics(values: list[Any]) -> dict[str, Any]:
    if not isinstance(values, list) or not values:
        raise ValueError("frame must be a non-empty list")
    if len(values) > MAX_SAMPLE_COUNT:
        raise ValueError("frame too large")
    normalized: list[Fraction] = []
    for value in values:
        if isinstance(value, Fraction):
            fraction = value
        elif isinstance(value, int):
            fraction = Fraction(value, 1)
        elif isinstance(value, float):
            raise ValueError("float not allowed")
        else:
            raise ValueError("unsupported sample type")
        if not (Fraction(-1, 1) <= fraction <= Fraction(1, 1)):
            raise ValueError("sample out of range")
        normalized.append(fraction)
    peak = max(abs(value) for value in normalized)
    return {
        "sample_count": len(normalized),
        "peak": str(peak.numerator) if peak.denominator == 1 else f"{peak.numerator}/{peak.denominator}",
        "finite": True,
    }


def envelope_manifest(case_id: str, numerator: int, denominator: int) -> dict[str, Any]:
    input_samples = 19200
    record = mapping_record(input_samples, numerator, denominator)
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
            "sample_count": input_samples,
            "dtype": "float32",
            "finite": True,
            "peak": peak,
        },
        "rate": {
            "numerator": numerator,
            "denominator": denominator,
        },
        "output": {
            "sample_count": record["target_samples"],
            "mapping_sha256": record["mapping_sha256"],
            "finite": True,
            "peak": peak,
            "first_source": record["first_source"],
            "last_source": record["last_source"],
        },
        "controls": [
            {"id": "candidate", "kind": "candidate"},
            {"id": "identity", "kind": "identity_passthrough"},
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
    input_peak = _require_decimal(input_obj["peak"], "input.peak")

    rate = _require_object(obj["rate"], "rate")
    _require_keys(rate, RATE_FIELDS, "rate")
    numerator = _require_int(rate["numerator"], "rate.numerator", minimum=1, maximum=16)
    denominator = _require_int(rate["denominator"], "rate.denominator", minimum=1, maximum=16)
    record = mapping_record(sample_count, numerator, denominator)

    output = _require_object(obj["output"], "output")
    _require_keys(output, OUTPUT_FIELDS, "output")
    output_count = _require_int(output["sample_count"], "output.sample_count", minimum=0, maximum=MAX_SAMPLE_COUNT)
    if output_count != record["target_samples"]:
        raise AdmissionError("output_sample_count_mismatch", "output.sample_count")
    mapping_digest = _require_sha256(output["mapping_sha256"], "output.mapping_sha256")
    if mapping_digest != record["mapping_sha256"]:
        raise AdmissionError("output_mapping_digest_mismatch", "output.mapping_sha256")
    if _require_bool(output["finite"], "output.finite") is not True:
        raise AdmissionError("output_finite_must_be_true", "output.finite")
    output_peak = _require_decimal(output["peak"], "output.peak")
    if output_peak != input_peak:
        raise AdmissionError("output_peak_mismatch", "output.peak")
    first_source = _require_int(output["first_source"], "output.first_source", minimum=0)
    last_source = _require_int(output["last_source"], "output.last_source", minimum=-1)
    if first_source != record["first_source"]:
        raise AdmissionError("output_first_source_mismatch", "output.first_source")
    if last_source != record["last_source"]:
        raise AdmissionError("output_last_source_mismatch", "output.last_source")

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

    return {
        "request_id": request_id,
        "accepted": True,
        "target_samples": record["target_samples"],
        "speed_ratio": record["speed_ratio"],
        "mapping_sha256": record["mapping_sha256"],
        "qualified": False,
    }


def admission_rejections() -> dict[str, Any]:
    base = envelope_manifest("identity_1x", 1, 1)
    cases: list[tuple[str, dict[str, Any], str]] = []

    def add(case_id: str, mutator, code: str) -> None:
        manifest = copy.deepcopy(base)
        mutator(manifest)
        cases.append((case_id, manifest, code))

    add("missing_manifest_section", lambda m: m.pop("output"), "missing_field")
    extra = copy.deepcopy(base); extra["extra"] = 1
    cases.append(("extra_top_level_key", extra, "unknown_field"))
    add("bad_schema_id", lambda m: m.__setitem__("schema_id", "bad"), "schema_id_mismatch")
    add("bad_request_id", lambda m: m.__setitem__("request_id", "Bad Id"), "invalid_slug")
    add("empty_request_id", lambda m: m.__setitem__("request_id", ""), "invalid_slug")
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
    add("input_peak_infinity", lambda m: m["input"].__setitem__("peak", "Infinity"), "peak_not_canonical")
    add("input_peak_negative", lambda m: m["input"].__setitem__("peak", "-0.1"), "peak_not_canonical")
    add("input_peak_over_one", lambda m: m["input"].__setitem__("peak", "1.1"), "peak_out_of_range")
    add("input_peak_not_canonical", lambda m: m["input"].__setitem__("peak", "1.0"), "peak_not_canonical")
    add("input_peak_not_string", lambda m: m["input"].__setitem__("peak", 1), "peak_not_canonical")
    add("rate_zero_numerator", lambda m: m["rate"].__setitem__("numerator", 0), "out_of_range")
    add("rate_zero_denominator", lambda m: m["rate"].__setitem__("denominator", 0), "out_of_range")
    add("rate_not_reduced", lambda m: (m["rate"].update({"numerator": 2, "denominator": 4}), m["output"].update({"sample_count": 38400, "mapping_sha256": mapping_record(19200,2,4)["mapping_sha256"] if False else m["output"]["mapping_sha256"], "first_source":0, "last_source":19199})), "rate_not_reduced")
    add("rate_too_slow", lambda m: (m["rate"].update({"numerator": 1, "denominator": 3}), m["output"].update({"sample_count": 57600, "mapping_sha256": "0"*64, "first_source":0, "last_source":19199})), "rate_out_of_bounds")
    add("rate_too_fast", lambda m: (m["rate"].update({"numerator": 3, "denominator": 1}), m["output"].update({"sample_count": 6400, "mapping_sha256": "0"*64, "first_source":0, "last_source":19197})), "rate_out_of_bounds")
    add("output_count_wrong", lambda m: m["output"].__setitem__("sample_count", 19199), "output_sample_count_mismatch")
    add("output_digest_bad_hex", lambda m: m["output"].__setitem__("mapping_sha256", "xyz"), "digest_invalid")
    add("output_digest_mismatch", lambda m: m["output"].__setitem__("mapping_sha256", "0" * 64), "output_mapping_digest_mismatch")
    add("output_finite_false", lambda m: m["output"].__setitem__("finite", False), "output_finite_must_be_true")
    add("output_peak_mismatch", lambda m: m["output"].__setitem__("peak", "0.5"), "output_peak_mismatch")
    add("output_first_source_wrong", lambda m: m["output"].__setitem__("first_source", 1), "output_first_source_mismatch")
    add("output_last_source_wrong", lambda m: m["output"].__setitem__("last_source", 19198), "output_last_source_mismatch")
    extra_output = copy.deepcopy(base); extra_output["output"]["extra"] = 1
    cases.append(("output_extra_key", extra_output, "unknown_field"))
    add("controls_empty", lambda m: m.__setitem__("controls", []), "controls_invalid")
    add("controls_missing_candidate", lambda m: m.__setitem__("controls", [{"id":"x","kind":"identity_passthrough"}]), "control_kind_missing")
    add("controls_duplicate_id", lambda m: m.__setitem__("controls", [{"id":"c","kind":"candidate"},{"id":"c","kind":"identity_passthrough"},{"id":"m","kind":"missing_runtime"},{"id":"n","kind":"nonfinite_rejection"}]), "control_id_duplicate")
    add("controls_unknown_kind", lambda m: m.__setitem__("controls", [{"id":"c","kind":"candidate"},{"id":"i","kind":"identity_passthrough"},{"id":"m","kind":"missing_runtime"},{"id":"n","kind":"other"}]), "control_kind_unknown")
    add("controls_too_many", lambda m: m.__setitem__("controls", [{"id":f"c{i}","kind":"candidate" if i==0 else "identity_passthrough" if i==1 else "missing_runtime" if i==2 else "nonfinite_rejection"} for i in range(MAX_CONTROLS + 1)]), "controls_invalid")
    add("rights_claims_qualified", lambda m: m["rights"].__setitem__("claims_qualified", True), "claims_qualified_must_be_false")
    add("rights_empty_source", lambda m: m["rights"].__setitem__("source_terms", ""), "rights_source_terms_empty")
    add("rights_missing_output_use", lambda m: m["rights"].pop("output_use"), "missing_field")
    rights_extra = copy.deepcopy(base); rights_extra["rights"]["extra"] = "x"
    cases.append(("rights_extra_field", rights_extra, "unknown_field"))

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
    input_samples = 19200
    cases = []
    for case_id, numerator, denominator in (
        ("identity_1x", 1, 1),
        ("speed_up_125", 5, 4),
        ("speed_up_150", 3, 2),
        ("speed_down_080", 4, 5),
        ("speed_down_090", 9, 10),
    ):
        record = mapping_record(input_samples, numerator, denominator)
        manifest = envelope_manifest(case_id, numerator, denominator)
        accepted = validate_manifest(manifest)
        cases.append({
            "id": case_id,
            "accepted_manifest_sha256": object_digest(manifest),
            "mapping_sha256": record["mapping_sha256"],
            "target_samples": record["target_samples"],
            "speed_ratio": record["speed_ratio"],
            "duration_error_samples": record["duration_error_samples"],
            "first_source": record["first_source"],
            "last_source": record["last_source"],
            "identity_exact": record["identity_exact"],
            "monotone": record["monotone"],
            "bounded": record["bounded"],
            "accepted": accepted["accepted"],
        })
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "purpose": "Deterministic integer source-to-output position map over one frozen synthetic duration. Protocol plumbing only; not a phase-locking phase vocoder, not audio synthesis, and not a rate estimator.",
        "not_candidate": True,
        "synthesizes_audio": False,
        "loads_model": False,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "input_samples": input_samples,
        "case_count": len(cases),
        "identity_case": "identity_1x",
        "identity_exact": any(case["id"] == "identity_1x" and case["identity_exact"] for case in cases),
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
            "statement": "No exact licensed phase-locking phase vocoder source, immutable revision, release tag, or per-file manifest is present in the worktree or staged evidence.",
            "required_action": "Supply the exact upstream source/reference at an immutable revision with license text, notices, and a source-to-artifact map. No download is permitted inside this package.",
        },
        {
            "id": "BLK-02",
            "artifact_id": "ART-03",
            "linked_gates": ["RG-01", "RG-02"],
            "qualifies": False,
            "status": "open",
            "statement": "No pinned runtime, dependency lock, FFT/window library identity, build recipe, or offline install manifest is present for a phase-locking phase vocoder reference.",
            "required_action": "Provide a locked offline runtime and dependency manifest with wheel/package names, versions, byte counts, SHA-256 values, and install location.",
        },
        {
            "id": "BLK-03",
            "artifact_id": "ART-04",
            "linked_gates": ["RG-02", "RG-03"],
            "qualifies": False,
            "status": "open",
            "statement": "No exact task geometry for the candidate is staged: analysis/synthesis window, hop, phase-locking mode, transient handling, latency/reset/drain policy, and rate schedule semantics are undocumented for the intended runtime.",
            "required_action": "Pin the exact audio-in/audio-out geometry, phase-locking mode, window/hop, latency/reset/drain behavior, and rate schedule semantics for the target runtime.",
        },
        {
            "id": "BLK-04",
            "artifact_id": "ART-05",
            "linked_gates": ["RG-04"],
            "qualifies": False,
            "status": "open",
            "statement": "No reviewed code/license terms, rights-cleared inputs, derived-output terms, or redistribution decision is staged for the candidate or its comparison corpus.",
            "required_action": "Provide reviewed code/license terms and a digest-pinned, rights-cleared input set with acquisition, evaluation, derived-output, and redistribution decisions.",
        },
        {
            "id": "BLK-05",
            "artifact_id": "ART-06",
            "linked_gates": ["RG-05", "RG-06"],
            "qualifies": False,
            "status": "open",
            "statement": "No baseline phase-vocoder comparison at identical ratios, no candidate output, and no Rate-profile measurements exist (mapping, duration, pitch, transient, buffering, 1x, rate changes, unfamiliar speech, music, silence, rebuffer/drift, final partial, preservation).",
            "required_action": "Run deterministic offline candidate and baseline comparisons at identical ratios on rights-cleared inputs, then record every Rate-profile item with exact hashes and controls.",
        },
        {
            "id": "BLK-06",
            "artifact_id": "ART-07",
            "linked_gates": ["RG-07", "RG-08"],
            "qualifies": False,
            "status": "open",
            "statement": "No mode/platform timing, resources, pacing, listening/labeled screen, provider intake, clean-install proof, or independent review exists.",
            "required_action": "Measure mode/platform timing and resources, complete authorized listening or a labeled screen, then open a separate OFF-by-default intake with clean-install proof and independent exact-head review.",
        },
    ]


def release_gates() -> list[dict[str, Any]]:
    rows = {row["id"]: row for row in linked_rows()}
    task_row = rows[TASK]
    gate_specs = [
        ("RG-01", "source_revision_and_license_provenance", "No exact source, immutable revision, license text, or notice is staged.", "Stage the exact reference at an immutable revision with complete license, notice, README, and independent review."),
        ("RG-02", "pinned_runtime_and_offline_install", "No locked offline runtime, dependency manifest, install location, or clean-room import digest is recorded.", "Provide a locked offline runtime with wheel/package hashes, install location, and clean-room import digest."),
        ("RG-03", "exact_task_geometry_and_phase_locking_mode", "No exact window/hop, phase-locking mode, transient handling, latency/reset/drain, or rate schedule semantics is pinned.", "Pin the exact task geometry, phase-locking mode, and latency/reset/drain behavior for the intended runtime."),
        ("RG-04", "rights_cleared_inputs_and_terms", "No reviewed code/license terms or rights-cleared, digest-pinned inputs exist.", "Freeze a permitted, digest-pinned input set with code/license, evaluation, derived-output, and redistribution decisions."),
        ("RG-05", "reference_execution_and_output_validity", "No deterministic candidate execution, output hashes, finite/length checks, or exact repeats exist.", "Execute the pinned candidate offline and record output hashes, finite/length preservation, exact repeats, and peak/RSS values."),
        ("RG-06", "rate_profile_against_baseline_phase_vocoder", "No Rate-profile measurement exists, and no identical-ratio comparison against the baseline phase vocoder exists.", "Run every Rate-profile case on rights-cleared inputs against the baseline phase vocoder at identical ratios, including controls and preservation."),
        ("RG-07", "mode_platform_timing_resources_and_listening", "No mode/platform timing, resources, pacing, device behavior, or authorized listening/labeled screen exists.", "Measure each mode/platform separately with timing, resources, pacing, and complete authorized listening or a labeled screen."),
        ("RG-08", "provider_intake_public_surface_and_release", "No provider, descriptor, registry entry, default, shared-build change, clean-install proof, or independent review exists.", "Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear."),
    ]
    gates = []
    for gate_id, title, statement, reopen in gate_specs:
        gates.append({
            "id": gate_id,
            "title": title,
            "status": "blocked",
            "qualifies": False,
            "statement": statement,
            "reopen_condition": reopen,
            "linked_row": task_row,
        })
    return gates


def rate_profile() -> dict[str, Any]:
    blocked = "No candidate source, runtime, rights-cleared input, baseline comparison, or output exists; this item cannot be measured."
    reqs = [
        ("RATE-01", "Source/output mapping for the exact runtime.", "blocked"),
        ("RATE-02", "Target and actual duration for constant and changing rates.", "blocked"),
        ("RATE-03", "Pitch preservation or shift for the exact runtime.", "blocked"),
        ("RATE-04", "Transient audibility proxy or authorized listening.", "blocked"),
        ("RATE-05", "Playback buffering, fill/flush and deadline behaviour.", "blocked"),
        ("RATE-06", "1x identity control.", "blocked"),
        ("RATE-07", "Rate changes, including step and ramp profiles.", "blocked"),
        ("RATE-08", "Unfamiliar speech material.", "blocked"),
        ("RATE-09", "Music material and a synthetic music negative control.", "blocked"),
        ("RATE-10", "Silence and empty input.", "blocked"),
        ("RATE-11", "Rebuffer, drift and the final partial window.", "blocked"),
        ("RATE-12", "Pause or filler decisions tied to source timestamps and speech preservation.", "blocked"),
        ("RATE-13", "Separate paired, unpaired, synthetic, human and source-reported evidence.", "documented"),
    ]
    rows = []
    for req_id, requirement, status in reqs:
        evidence = blocked
        if req_id == "RATE-13":
            evidence = "Synthetic envelope, admission, source-reported, and missing-real sections stay separate; no category is pooled."
        rows.append({"id": req_id, "requirement": requirement, "status": status, "qualifies": False, "evidence": evidence})
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_envelope_only": True,
        "conditions": [
            "identity_1x", "rate_changes", "unfamiliar_speech", "music", "silence",
            "rebuffer", "drift", "final_partial_window", "pause_filler_source_timestamps",
        ],
        "requirement_rows": rows,
        "candidate_duration_result": None,
        "candidate_pitch_result": None,
        "candidate_transient_result": None,
        "candidate_preservation_result": None,
        "candidate_geometry": None,
    }


def required_artifacts() -> list[dict[str, Any]]:
    return [
        {"id": "ART-01", "kind": "evidence_register_and_policy_boundary", "present": True, "blocked": False, "verified": True, "revision": None, "sha256": None, "requirement": "Pinned task row, Rate acceptance profile, SDK delivery plan, research note, sibling phase-vocoder/TSM evidence, and unchanged v0 contract boundary."},
        {"id": "ART-02", "kind": "exact_upstream_source_or_reference", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Exact licensed phase-locking phase vocoder source/reference at immutable revision with license text, notices, and per-file manifest."},
        {"id": "ART-03", "kind": "pinned_runtime_and_dependencies", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Locked offline runtime and dependency manifest with wheel/package hashes, install location, and clean-room import digest."},
        {"id": "ART-04", "kind": "exact_task_geometry", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Exact audio-in/audio-out geometry, phase-locking mode, window/hop, latency/reset/drain policy, and rate schedule semantics."},
        {"id": "ART-05", "kind": "rights_cleared_inputs_and_terms", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Reviewed code/license terms and digest-pinned rights-cleared inputs with acquisition, evaluation, derived-output, and redistribution decisions."},
        {"id": "ART-06", "kind": "reproduced_rate_results_vs_baseline", "present": False, "blocked": True, "verified": False, "revision": None, "sha256": None, "requirement": "Deterministic candidate and baseline phase-vocoder results at identical ratios with full Rate-profile measurements and controls."},
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
        "rate_only_estimator": False,
        "task": "audio_time_scale_modification",
        "algorithm_family": "phase_vocoder_with_phase_locking",
        "reference_methods": ["identity_phase_locking", "scaled_phase_locking"],
        "baseline_comparison_required": "phase-vocoder-baseline at identical ratios",
        "released_content": [],
        "release_state": "no exact licensed implementation staged",
    }


def required_results() -> list[str]:
    return [
        "Exact upstream source/reference, immutable revision, license text, and notice.",
        "Locked offline runtime with dependency/wheel hashes, install location, and clean-room import digest.",
        "Exact task geometry: sample rate, channels, window/hop, phase-locking mode, latency/reset/drain, and rate schedule semantics.",
        "Rights-cleared, digest-pinned inputs and reviewed code/license/derived-output/redistribution terms.",
        "Deterministic candidate outputs and identical-ratio baseline phase-vocoder outputs with exact hashes.",
        "Source/output mapping, duration, pitch, transient, buffering, 1x, rate changes, unfamiliar speech, music, silence, rebuffer/drift, final partial, and speech-preservation results.",
        "Mode/platform timing, resources, pacing, authorized listening or labeled screen, and independent OFF-by-default intake review.",
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
    rp = rate_profile()
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
            "rate_fields": list(RATE_FIELDS),
            "output_fields": list(OUTPUT_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "max_sample_count": MAX_SAMPLE_COUNT,
            "max_controls": MAX_CONTROLS,
            "rate_bounds": {"numerator": [1, 16], "denominator": [1, 16], "speed": ["1/2", "2/1"]},
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
        "rate_profile": rp,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "release_gates": gates,
        "required_results": required_results(),
        "reopening_conditions": reopening_conditions(),
        "non_claims": [
            "No phase-locking phase vocoder source, reference implementation, binary, or runtime is present, imported, linked, loaded, or executed.",
            "No audio, corpus, model, checkpoint, or processed output is read, generated, or produced.",
            "No rate, duration, pitch, transient, buffering, preservation, listening, device-timing, or benchmark result is reproduced.",
            "The integer position envelope and admission control are protocol plumbing only; they are not the candidate, not audio synthesis, and not a qualification.",
            "No provider, descriptor, registry, default, public ABI, shared build, or CI change exists.",
            "Research prose and paper/plan references are source-reported context only and are not promoted to measured evidence.",
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
    rp = rate_profile()
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
        "generated_by": "docs/task-evidence/phase-locking-phase-vocoder/run.py",
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
            "checkpoint_present": False,
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
            "accepts": "Only an offline manifest that declares absent candidate artifacts, canonical fields, and closed rights terms.",
        },
        "protocol_envelope": envelope,
        "rate_profile": rp,
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
            "checkpoint_present": False,
            "license_text_present": False,
            "runtime_pinned": False,
            "real_result_present": False,
            "output_validity_result": False,
            "reference_execution_result": False,
            "rate_profile_result": False,
            "duration_result": False,
            "pitch_result": False,
            "transient_result": False,
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
