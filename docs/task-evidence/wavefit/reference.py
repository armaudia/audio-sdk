# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic WaveFit blocker-evidence reference.

Task-local only. No source, weights, runtime, audio, feature input, network,
or model execution. Missing evidence never qualifies.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-WAVEFIT"
COMPONENT_ID = "wavefit"
TASK_TITLE = "WaveFit"
MODE = "research-control"
PROFILE = "Enhancement"
PROFILE_LABEL = "Enhancement"
BRANCH = "swarm/SDK-WAVEFIT"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.2"
CONTRACT_ID = "audio-sdk/wavefit-readiness/0.1"
MANIFEST_SCHEMA_ID = "audio-sdk/wavefit-qualification/0.1"
WRITE_SCOPE = "docs/task-evidence/wavefit/ only"
TASK_PREFIX = "docs/task-evidence/wavefit/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
}
LINKED_ROWS = (
    dict(BOARD_ROW_PROJECTION),
    {"id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": []},
    {"id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "component": None, "mode": "foundation", "repository": "audio-sdk", "depends_on": []},
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline.",
    "Score paired SI-SDR and STOI where permitted clean references exist.",
    "Measure clean-speech preservation, peaks and invalid outputs.",
    "For unpaired speech use a separately labeled predictive screen or authorized listening.",
    "Report alignment, state, memory and measured content/availability timing for the exact runtime.",
)

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-denoise/REPORT.md": "eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07",
    "research/voice-enhancement-20261101/findings.md": "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
}
BOUNDARY_PINS = {
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
}

ABSENCE_PROBES = (
    "research/voice-enhancement-20261101/repos/wavefit",
    "research/voice-enhancement-20261101/repos/WaveFit",
    "research/voice-enhancement-20261101/models/wavefit",
    "data/assets/wavefit",
    "data/models/wavefit",
    "third_party/wavefit",
    "adapters/wavefit",
    "docs/task-evidence/wavefit/weights",
    "docs/task-evidence/wavefit/runtime",
    "docs/task-evidence/wavefit/assets",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--google--wavefit",
    "~/.cache/huggingface/hub/models--wavefit",
)

REQUIRED_ARTIFACTS = (
    {"id": "ART-01", "kind": "pinned_research_classification", "present": True, "blocked": False, "requirement": "Pinned candidate-matrix/research classification for WaveFit with stable row identity and exact source pins.", "sha256": SOURCE_PINS["research/voice-enhancement-20261101/candidate_matrix.csv"], "verified": True},
    {"id": "ART-02", "kind": "exact_wavefit_source_and_notices", "present": False, "blocked": True, "requirement": "Exact WaveFit source checkout/archive at an immutable revision with license, copyright and notice bundle.", "sha256": None, "verified": False},
    {"id": "ART-03", "kind": "wavefit_weights_snapshot", "present": False, "blocked": True, "requirement": "Immutable WaveFit weights/checkpoint with filename, byte count, SHA-256, format and exact input/output geometry.", "sha256": None, "verified": False},
    {"id": "ART-04", "kind": "pinned_runtime", "present": False, "blocked": True, "requirement": "Locked offline runtime with install digest, exact Python/runtime versions, deterministic settings, fixed seed and recorded host profile.", "sha256": None, "verified": False},
    {"id": "ART-05", "kind": "reviewed_weight_and_output_terms", "present": False, "blocked": True, "requirement": "Reviewed source/weight/model-card/output terms covering attribution, redistribution, commercial and generated-output use.", "sha256": None, "verified": False},
    {"id": "ART-06", "kind": "rights_cleared_task_matched_cohort", "present": False, "blocked": True, "requirement": "Rights-cleared task-matched evaluation cohort with consent, exact protocol, controls and packet-loss/enhancement labels as applicable.", "sha256": None, "verified": False},
)

EXACT_BLOCKERS = (
    {"artifact_id": "ART-02", "id": "BLK-01", "linked_gates": ["RG-01"], "qualifies": False, "required_action": "Supply exact WaveFit source at an immutable revision with reviewed license/copyright/notice bundle.", "statement": "No exact WaveFit source checkout/archive, immutable revision, or license/notice bundle is present.", "status": "open"},
    {"artifact_id": "ART-03", "id": "BLK-02", "linked_gates": ["RG-02"], "qualifies": False, "required_action": "Supply immutable WaveFit weights with filename, byte count, SHA-256, format and exact geometry.", "statement": "No WaveFit weights/checkpoint, filename, byte count, SHA-256, format or exact geometry are present.", "status": "open"},
    {"artifact_id": "ART-04", "id": "BLK-03", "linked_gates": ["RG-04"], "qualifies": False, "required_action": "Supply a locked isolated runtime with install digest, deterministic settings and recorded host profile.", "statement": "No pinned runtime, lock file, install digest or host profile is present.", "status": "open"},
    {"artifact_id": "ART-05", "id": "BLK-04", "linked_gates": ["RG-03", "RG-05"], "qualifies": False, "required_action": "Record reviewed source/weight/model-card/output terms covering attribution, redistribution, commercial and generated-output use.", "statement": "No reviewed weight/model-card/output-use terms are staged.", "status": "open"},
    {"artifact_id": "ART-06", "id": "BLK-05", "linked_gates": ["RG-06", "RG-07", "RG-08"], "qualifies": False, "required_action": "Supply a rights-cleared task-matched cohort and controls with reviewed protocol; WaveFit is classified as neural vocoder, not standalone PLC.", "statement": "No rights-cleared task-matched cohort, consent, controls, or qualified PLC/enhancement protocol exists; pinned research marks WaveFit out of scope for PLC.", "status": "open"},
)

RELEASE_GATES = (
    {"id": "RG-01", "title": "Source revision and license provenance", "status": "blocked", "qualifies": False, "reopen_condition": "Exact WaveFit source at immutable revision with license/copyright/notice bundle is supplied and reviewed.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-02", "title": "Weights identity and geometry", "status": "blocked", "qualifies": False, "reopen_condition": "Immutable weights with filename, byte count, SHA-256, format and exact input/output geometry are supplied and verified offline.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-03", "title": "Weight, model-card and output terms", "status": "blocked", "qualifies": False, "reopen_condition": "Reviewed terms settle attribution, redistribution, commercial use and output use.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-04", "title": "Pinned runtime and deterministic offline load", "status": "blocked", "qualifies": False, "reopen_condition": "Locked runtime with install digest loads pinned weights offline with deterministic settings, fixed seed and recorded host profile.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-05", "title": "Consent, reference availability and output use", "status": "blocked", "qualifies": False, "reopen_condition": "Signed consent, input/reference availability, output-use and commercial-terms review are recorded for every input and output.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-06", "title": "Rights-cleared task-matched cohort and controls", "status": "blocked", "qualifies": False, "reopen_condition": "Rights-cleared task-matched cohort, exact protocol and identity/noisy/conventional controls are supplied; task fit is established.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-07", "title": "Paired quality, preservation and listening evidence", "status": "blocked", "qualifies": False, "reopen_condition": "Pinned scorers and approved protocol produce paired SI-SDR/STOI, clean-speech preservation, peaks/invalid outputs and required listening/predictive-screen evidence.", "linked_row": dict(BOARD_ROW_PROJECTION)},
    {"id": "RG-08", "title": "Alignment, timing, resources, intake and release", "status": "blocked", "qualifies": False, "reopen_condition": "Target-runtime runs record alignment, state, memory, content/availability timing; separate versioned intake with OFF default and exact-head review passes.", "linked_row": dict(BOARD_ROW_PROJECTION)},
)

ENHANCEMENT_PROFILE_ROWS = (
    {"id": "EP-01", "requirement": "Run identity/noisy control and an established task-matched baseline.", "status": "blocked", "evidence": "No WaveFit run, no identity/noisy control, no task-matched baseline."},
    {"id": "EP-02", "requirement": "Score paired SI-SDR and STOI where permitted clean references exist.", "status": "blocked", "evidence": "No paired clean-reference cohort, SI-SDR or STOI result."},
    {"id": "EP-03", "requirement": "Measure clean-speech preservation, peaks and invalid outputs.", "status": "blocked", "evidence": "No output waveform, preservation metric, peak or invalid-output measurement."},
    {"id": "EP-04", "requirement": "For unpaired speech use a separately labeled predictive screen or authorized listening.", "status": "blocked", "evidence": "No predictive screen, listening protocol or human rating."},
    {"id": "EP-05", "requirement": "Report alignment, state, memory and measured content/availability timing for the exact runtime.", "status": "blocked", "evidence": "No runtime, alignment, state, memory or content/availability timing."},
)

QUALITY_OUTCOME_ROWS = (
    {"id": "QO-01", "outcome": "paired SI-SDR/STOI", "status": "blocked", "value": None, "evidence": "No qualified paired run."},
    {"id": "QO-02", "outcome": "clean-speech preservation", "status": "blocked", "value": None, "evidence": "No qualified preservation measurement."},
    {"id": "QO-03", "outcome": "peaks/invalid outputs", "status": "blocked", "value": None, "evidence": "No qualified output."},
    {"id": "QO-04", "outcome": "predictive screen/listening", "status": "blocked", "value": None, "evidence": "No predictive screen or listening result."},
)

TIMING_ROWS = (
    {"id": "TR-01", "metric": "alignment/content mapping", "status": "blocked", "value": None, "evidence": "No run or alignment measurement."},
    {"id": "TR-02", "metric": "state/memory", "status": "blocked", "value": None, "evidence": "No runtime or memory measurement."},
    {"id": "TR-03", "metric": "content/availability timing", "status": "blocked", "value": None, "evidence": "No target-runtime paced run."},
    {"id": "TR-04", "metric": "benchmark/real-time factor", "status": "blocked", "value": None, "evidence": "No qualified benchmark."},
)

NON_CLAIMS = [
    "No WaveFit source, weights, runtime, audio, feature tensor, waveform or vendor output is bundled.",
    "No source was imported, built, loaded or executed; no weight was loaded and no model was run.",
    "No audio was read, decoded, played, listened to or scored.",
    "No SI-SDR, STOI, preservation, peak, invalid-output, listening, alignment, state, memory, timing, device-timing, benchmark or release result exists.",
    "No consent, reference availability or output-use clearance is asserted.",
    "No upstream license/notice, model-card term or weight/output term is asserted.",
    "No provider was registered, enabled by default, described in a registry or exposed through installed-v0, ABI, shared build or CI.",
    "WaveFit remains classified as neural vocoder / out of scope for standalone PLC by pinned research; this package does not change that classification.",
]

SOURCE_PRESENCE = {
    "present": False, "admitted": False, "verified": False,
    "exact_source_weights_runtime_conjunction_present": False,
    "exact_upstream_source_present": False, "weights_used": False,
    "model_executed": False, "source_kind": "absent",
    "upstream_project": "WaveFit", "upstream_revision": None,
    "present_components": [], "absent_components": [
        "exact_wavefit_source_license_and_notices",
        "wavefit_weights",
        "pinned_runtime",
        "reviewed_weight_and_output_terms",
        "rights_cleared_task_matched_cohort",
    ],
    "reason": "No WaveFit source, weights, runtime, reviewed terms or rights-cleared cohort are present. Pinned research classifies WaveFit as a neural vocoder, not a standalone PLC/enhancement system. Absence is not admission.",
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PYTHON_VERSION = re.compile(r"^3\.(10|11|12|13)\.[0-9]+$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
WEIGHT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Z][A-Za-z0-9]{1,8}){0,3}$")

MANIFEST_FIELDS = ("schema_id", "cohort_id", "source", "weights", "runtime", "features", "controls", "outcomes", "rights")
SOURCE_FIELDS = ("revision", "path", "license_id", "license_path", "license_sha256", "upstream_revision", "upstream_license_sha256")
WEIGHT_FIELDS = ("name", "path", "sha256", "byte_count", "format", "terms_sha256")
RUNTIME_FIELDS = ("python_version", "torch_version", "device", "threads", "deterministic_algorithms", "seed", "install_digest")
FEATURE_FIELDS = ("id", "path", "sha256", "sample_rate_hz", "n_mels", "hop_samples", "frame_count", "feature_kind", "consent_id", "rights_reference", "language", "speaker_group")
CONTROL_FIELDS = ("id", "kind", "feature_id", "feature_sha256")
OUTCOME_FIELDS = ("si_sdr_db", "stoi", "pesq", "clean_speech_preservation_db", "peak_abs", "clipped_fraction", "nonfinite_count", "sample_count", "output_sample_rate_hz")
RIGHTS_FIELDS = ("consent_reference", "input_availability", "output_use", "commercial_terms_review", "terms_review", "listening_protocol", "listening_panel_size")
WEIGHT_FORMATS = ("jit_torchscript", "safetensors", "pytorch_state_dict", "onnx", "checkpoint")
WEIGHT_SUFFIXES = (".pt", ".pth", ".safetensors", ".onnx", ".ckpt")
FEATURE_KINDS = ("wav", "mel", "log_mel", "packet_loss_trace")
CONTROL_KINDS = ("identity", "noisy", "conventional_baseline")
INPUT_SAMPLE_RATES = (8000, 16000, 22050, 24000, 44100, 48000)
OUTPUT_SAMPLE_RATES = (8000, 16000, 22050, 24000, 44100, 48000)
MAX_WEIGHT_BYTES = 8_589_934_592
MAX_THREADS = 64
MAX_SEED = 2_147_483_647
MAX_FRAME_COUNT = 1_000_000
MAX_HOP = 2048
MAX_N_MELS = 256
MAX_PEAK = 4
MAX_PANEL = 1000
MAX_SAMPLE_COUNT = 48_000 * 3600
REQUIRED_WEIGHT_TOKEN = "wavefit"


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def loads_strict(text: str) -> Any:
    def reject_const(x: str) -> Any:
        raise ValueError("non_json_constant:" + x)
    decoder = json.JSONDecoder(parse_constant=reject_const)
    value, index = decoder.raw_decode(text)
    if text[index:].strip():
        raise ValueError("trailing_content")
    _no_floats(value)
    return value


def read_strict_json(path: Path) -> Any:
    return loads_strict(path.read_text(encoding="utf-8"))


def _no_floats(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_report:" + (path or "<root>"))
    if isinstance(value, dict):
        for key in sorted(value):
            _no_floats(value[key], (path + "." + str(key)).lstrip("."))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, f"{path}[{index}]")


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual, "verified": True}
    return rows


def board_row_projection() -> dict:
    return dict(BOARD_ROW_PROJECTION)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(dict(BOARD_ROW_PROJECTION) if projection is None else projection)


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS} for row in rows])


def absence_probes(audio_root: Path = AUDIO_ROOT, probes: tuple[str, ...] = ABSENCE_PROBES, worktree: Path | None = None) -> list[dict]:
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        if (Path(audio_root) / relative).exists() or (sdk_root / relative).exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True, "searched_sdk_worktree": True, "present": False})
    return rows


def home_absence_probes(probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = home / relative[2:] if relative.startswith("~/") else Path(relative)
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_home_cache": True, "present": False})
    return rows


def absence_summary(rows: list[dict], home_rows: list[dict]) -> dict:
    all_rows = rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "home_probe_count": len(home_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "feature_input_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field, "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks, "state_unchanged": True}


def _nonfinite_path(value: Any, path: str = "") -> str | None:
    if isinstance(value, float) and not math.isfinite(value):
        return path or "<root>"
    if isinstance(value, dict):
        for key in sorted(value):
            found = _nonfinite_path(value[key], (path + "." + str(key)).lstrip("."))
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, f"{path}[{index}]")
            if found:
                return found
    return None


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    if ".." in Path(value).parts or "~" in value:
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return "missing_field" if set(fields) - set(value) else "unknown_field"
    return ""


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


def _text(value: Any, limit: int = 200) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit and not any(ord(c) < 32 for c in value)


def _slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.match(value))


def _semver(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    m = SEMVER.match(value)
    if not m:
        return None
    return tuple(int(p) for p in m.groups())  # type: ignore[return-value]


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    checks = 0
    nonfinite = _nonfinite_path(document)
    if nonfinite:
        return _reject("nonfinite_value", nonfinite)
    if not isinstance(document, dict):
        return _reject("manifest_not_object")
    if set(document) != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - set(document))
        extra = sorted(set(document) - set(MANIFEST_FIELDS))
        return _reject("missing_field" if missing else "unknown_field", missing[0] if missing else extra[0])
    checks += 1
    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if not _slug(document["cohort_id"]):
        return _reject("invalid_value", "cohort_id")
    checks += 2

    source = document["source"]
    code = _exact_object(source, SOURCE_FIELDS)
    if code:
        return _reject(code, "source")
    if not isinstance(source["revision"], str) or not HEX40.match(source["revision"]):
        return _reject("invalid_value", "source.revision")
    if not _path_is_canonical(source["path"]):
        return _reject("invalid_path", "source.path")
    if not isinstance(source["license_id"], str) or not _text(source["license_id"], 80):
        return _reject("invalid_value", "source.license_id")
    if not _path_is_canonical(source["license_path"]):
        return _reject("invalid_path", "source.license_path")
    if not _sha(source["license_sha256"]):
        return _reject("invalid_value", "source.license_sha256")
    if not isinstance(source["upstream_revision"], str) or not HEX40.match(source["upstream_revision"]):
        return _reject("invalid_value", "source.upstream_revision")
    if not _sha(source["upstream_license_sha256"]):
        return _reject("invalid_value", "source.upstream_license_sha256")
    if probe_paths:
        for field in ("path", "license_path"):
            if not Path(source[field]).is_file():
                return _reject("probe_missing", "source." + field)
    checks += 7

    weights = document["weights"]
    if not isinstance(weights, list) or not weights:
        return _reject("invalid_value", "weights")
    names: set[str] = set()
    for weight in weights:
        code = _exact_object(weight, WEIGHT_FIELDS)
        if code:
            return _reject(code, "weights")
        if not isinstance(weight["name"], str) or not WEIGHT_NAME.match(weight["name"]):
            return _reject("invalid_value", "weights.name")
        if weight["name"] in names:
            return _reject("invalid_value", "weights.name")
        names.add(weight["name"])
        if not _path_is_canonical(weight["path"]):
            return _reject("invalid_path", "weights.path")
        if not _sha(weight["sha256"]):
            return _reject("invalid_value", "weights.sha256")
        if not _is_int(weight["byte_count"]) or not 1 <= weight["byte_count"] <= MAX_WEIGHT_BYTES:
            return _reject("invalid_value", "weights.byte_count")
        if weight["format"] not in WEIGHT_FORMATS:
            return _reject("invalid_value", "weights.format")
        if not _sha(weight["terms_sha256"]):
            return _reject("invalid_value", "weights.terms_sha256")
        if probe_paths and not Path(weight["path"]).is_file():
            return _reject("probe_missing", "weights.path")
    if not any(REQUIRED_WEIGHT_TOKEN in name.lower() for name in names):
        return _reject("invalid_value", "weights.wavefit_required")
    if not any(name.lower().endswith(WEIGHT_SUFFIXES) for name in names):
        return _reject("invalid_value", "weights.suffix_required")
    checks += len(weights) * 7 + 2

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    if _semver(runtime["torch_version"]) is None:
        return _reject("invalid_value", "runtime.torch_version")
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    if not _is_int(runtime["threads"]) or not 1 <= runtime["threads"] <= MAX_THREADS:
        return _reject("invalid_value", "runtime.threads")
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    if not _is_int(runtime["seed"]) or not 0 <= runtime["seed"] <= MAX_SEED:
        return _reject("invalid_value", "runtime.seed")
    if not _sha(runtime["install_digest"]):
        return _reject("invalid_value", "runtime.install_digest")
    checks += 7

    features = document["features"]
    if not isinstance(features, list) or not features:
        return _reject("invalid_value", "features")
    feature_ids: dict[str, str] = {}
    for feature in features:
        code = _exact_object(feature, FEATURE_FIELDS)
        if code:
            return _reject(code, "features")
        if not _slug(feature["id"]) or feature["id"] in feature_ids:
            return _reject("invalid_value", "features.id")
        if not _path_is_canonical(feature["path"]):
            return _reject("invalid_path", "features.path")
        if not _sha(feature["sha256"]):
            return _reject("invalid_value", "features.sha256")
        if not _is_int(feature["sample_rate_hz"]) or feature["sample_rate_hz"] not in INPUT_SAMPLE_RATES:
            return _reject("invalid_value", "features.sample_rate_hz")
        if not _is_int(feature["n_mels"]) or not 1 <= feature["n_mels"] <= MAX_N_MELS:
            return _reject("invalid_value", "features.n_mels")
        if not _is_int(feature["hop_samples"]) or not 1 <= feature["hop_samples"] <= MAX_HOP:
            return _reject("invalid_value", "features.hop_samples")
        if not _is_int(feature["frame_count"]) or not 1 <= feature["frame_count"] <= MAX_FRAME_COUNT:
            return _reject("invalid_value", "features.frame_count")
        if feature["feature_kind"] not in FEATURE_KINDS:
            return _reject("invalid_value", "features.feature_kind")
        for field in ("consent_id", "rights_reference", "speaker_group"):
            if not _slug(feature[field]):
                return _reject("invalid_value", "features." + field)
        if not isinstance(feature["language"], str) or not LANGUAGE.match(feature["language"]):
            return _reject("invalid_value", "features.language")
        feature_ids[feature["id"]] = feature["sha256"]
        if probe_paths and not Path(feature["path"]).is_file():
            return _reject("probe_missing", "features.path")
    checks += len(features) * 12

    controls = document["controls"]
    if not isinstance(controls, list) or not controls:
        return _reject("invalid_value", "controls")
    kinds: set[str] = set()
    control_ids: set[str] = set()
    for control in controls:
        code = _exact_object(control, CONTROL_FIELDS)
        if code:
            return _reject(code, "controls")
        if not _slug(control["id"]) or control["id"] in control_ids:
            return _reject("invalid_value", "controls.id")
        control_ids.add(control["id"])
        if control["kind"] not in CONTROL_KINDS or control["kind"] in kinds:
            return _reject("invalid_value", "controls.kind")
        kinds.add(control["kind"])
        if control["feature_id"] not in feature_ids:
            return _reject("invalid_value", "controls.feature_id")
        if control["feature_sha256"] != feature_ids[control["feature_id"]]:
            return _reject("invalid_value", "controls.feature_sha256")
    if set(CONTROL_KINDS) - kinds:
        return _reject("invalid_value", "controls.required")
    checks += len(controls) * 4 + 1

    outcomes = document["outcomes"]
    code = _exact_object(outcomes, OUTCOME_FIELDS)
    if code:
        return _reject(code, "outcomes")
    if not _is_number(outcomes["si_sdr_db"]) or not -100.0 <= float(outcomes["si_sdr_db"]) <= 100.0:
        return _reject("invalid_value", "outcomes.si_sdr_db")
    if not _is_number(outcomes["stoi"]) or not 0.0 <= float(outcomes["stoi"]) <= 1.0:
        return _reject("invalid_value", "outcomes.stoi")
    if not _is_number(outcomes["pesq"]) or not -0.5 <= float(outcomes["pesq"]) <= 4.5:
        return _reject("invalid_value", "outcomes.pesq")
    if not _is_number(outcomes["clean_speech_preservation_db"]) or not -100.0 <= float(outcomes["clean_speech_preservation_db"]) <= 100.0:
        return _reject("invalid_value", "outcomes.clean_speech_preservation_db")
    if not _is_number(outcomes["peak_abs"]) or not 0.0 <= float(outcomes["peak_abs"]) <= MAX_PEAK:
        return _reject("invalid_value", "outcomes.peak_abs")
    if not _is_number(outcomes["clipped_fraction"]) or not 0.0 <= float(outcomes["clipped_fraction"]) <= 1.0:
        return _reject("invalid_value", "outcomes.clipped_fraction")
    if not _is_int(outcomes["nonfinite_count"]) or outcomes["nonfinite_count"] != 0:
        return _reject("invalid_value", "outcomes.nonfinite_count")
    if not _is_int(outcomes["sample_count"]) or not 1 <= outcomes["sample_count"] <= MAX_SAMPLE_COUNT:
        return _reject("invalid_value", "outcomes.sample_count")
    if not _is_int(outcomes["output_sample_rate_hz"]) or outcomes["output_sample_rate_hz"] not in OUTPUT_SAMPLE_RATES:
        return _reject("invalid_value", "outcomes.output_sample_rate_hz")
    checks += 9

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    for field in ("consent_reference", "input_availability", "output_use", "commercial_terms_review", "terms_review", "listening_protocol"):
        if not _text(rights[field]):
            return _reject("invalid_value", "rights." + field)
    if not _is_int(rights["listening_panel_size"]) or not 1 <= rights["listening_panel_size"] <= MAX_PANEL:
        return _reject("invalid_value", "rights.listening_panel_size")
    checks += 7
    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "revision": "a" * 40,
            "path": "/caller/wavefit/source",
            "license_id": "Apache-2.0",
            "license_path": "/caller/wavefit/LICENSE",
            "license_sha256": "b" * 64,
            "upstream_revision": "c" * 40,
            "upstream_license_sha256": "d" * 64,
        },
        "weights": [
            {"name": "wavefit.ckpt", "path": "/caller/wavefit/wavefit.ckpt", "sha256": "1" * 64, "byte_count": 33554432, "format": "checkpoint", "terms_sha256": "2" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5", "torch_version": "2.5.1", "device": "cpu", "threads": 4,
            "deterministic_algorithms": True, "seed": 1729, "install_digest": "3" * 64,
        },
        "features": [
            {"id": "feat-a", "path": "/caller/wavefit/a.wav", "sha256": "9" * 64, "sample_rate_hz": 16000, "n_mels": 80, "hop_samples": 256, "frame_count": 100, "feature_kind": "wav", "consent_id": "consent-a", "rights_reference": "rights-a", "language": "en-US", "speaker_group": "group-a"},
            {"id": "feat-b", "path": "/caller/wavefit/b.wav", "sha256": "8" * 64, "sample_rate_hz": 16000, "n_mels": 80, "hop_samples": 256, "frame_count": 100, "feature_kind": "wav", "consent_id": "consent-b", "rights_reference": "rights-b", "language": "en-US", "speaker_group": "group-b"},
            {"id": "feat-c", "path": "/caller/wavefit/c.wav", "sha256": "7" * 64, "sample_rate_hz": 16000, "n_mels": 80, "hop_samples": 256, "frame_count": 100, "feature_kind": "wav", "consent_id": "consent-c", "rights_reference": "rights-c", "language": "en-US", "speaker_group": "group-c"},
        ],
        "controls": [
            {"id": "ctl-id", "kind": "identity", "feature_id": "feat-a", "feature_sha256": "9" * 64},
            {"id": "ctl-noisy", "kind": "noisy", "feature_id": "feat-b", "feature_sha256": "8" * 64},
            {"id": "ctl-base", "kind": "conventional_baseline", "feature_id": "feat-c", "feature_sha256": "7" * 64},
        ],
        "outcomes": {
            "si_sdr_db": 10.0, "stoi": 0.9, "pesq": 3.0, "clean_speech_preservation_db": 0.0,
            "peak_abs": 0.9, "clipped_fraction": 0.0, "nonfinite_count": 0, "sample_count": 16000, "output_sample_rate_hz": 16000,
        },
        "rights": {
            "consent_reference": "consent-a", "input_availability": "caller-supplied", "output_use": "research-only",
            "commercial_terms_review": "review-commercial-a", "terms_review": "review-a", "listening_protocol": "protocol-a", "listening_panel_size": 3,
        },
    }


def admission_controls() -> dict:
    control = _manifest_control()
    accepted = validate_manifest(control, probe_paths=False)
    cases: list[dict] = []

    def mutate(case_id: str, fn) -> None:
        document = _manifest_control()
        fn(document)
        result = validate_manifest(document, probe_paths=False)
        cases.append({"id": case_id, "status": "rejected" if not result["accepted"] else "accepted", "code": result["code"], "field": result["field"], "qualifies": False, "state_unchanged": result["state_unchanged"]})

    def set_top(field: str, value: Any):
        return lambda d: d.__setitem__(field, value)

    def del_top(field: str):
        return lambda d: d.__delitem__(field)

    def set_nested(path: tuple, value: Any):
        def apply(d: dict) -> None:
            t = d
            for p in path[:-1]:
                t = t[p]
            t[path[-1]] = value
        return apply

    def del_nested(path: tuple):
        def apply(d: dict) -> None:
            t = d
            for p in path[:-1]:
                t = t[p]
            del t[path[-1]]
        return apply

    for cid, payload in (("root-list", []), ("root-null", None), ("root-string", "x"), ("root-int", 7), ("root-bool", True)):
        result = validate_manifest(payload, probe_paths=False)
        cases.append({"id": cid, "status": "rejected", "code": result["code"], "field": result["field"], "qualifies": False, "state_unchanged": result["state_unchanged"]})
    for field in MANIFEST_FIELDS:
        mutate("missing-" + field, del_top(field))
    mutate("unknown-top-field", set_top("extra", "value"))
    mutate("wrong-schema", set_top("schema_id", "wrong"))
    mutate("cohort-uppercase", set_top("cohort_id", "Bad"))
    mutate("cohort-empty", set_top("cohort_id", ""))
    for field in SOURCE_FIELDS:
        mutate("missing-source-" + field, del_nested(("source", field)))
    mutate("source-revision-short", set_nested(("source", "revision"), "a" * 39))
    mutate("source-path-relative", set_nested(("source", "path"), "rel"))
    mutate("source-path-traversal", set_nested(("source", "path"), "/a/../b"))
    mutate("source-license-sha", set_nested(("source", "license_sha256"), "bad"))
    mutate("weights-empty", set_nested(("weights",), []))
    for field in WEIGHT_FIELDS:
        mutate("missing-weight-" + field, del_nested(("weights", 0, field)))
    mutate("weights-duplicate-name", lambda d: d["weights"].append(dict(d["weights"][0])))
    mutate("weights-missing-wavefit", lambda d: d["weights"].__setitem__(0, dict(d["weights"][0], name="decoder.pt")))
    mutate("weights-bad-suffix", lambda d: d["weights"].__setitem__(0, dict(d["weights"][0], name="wavefit.bin")))
    mutate("weights-sha-uppercase", set_nested(("weights", 0, "sha256"), "A" * 64))
    mutate("weights-byte-zero", set_nested(("weights", 0, "byte_count"), 0))
    mutate("weights-byte-bool", set_nested(("weights", 0, "byte_count"), True))
    mutate("weights-byte-huge", set_nested(("weights", 0, "byte_count"), MAX_WEIGHT_BYTES + 1))
    mutate("weights-format", set_nested(("weights", 0, "format"), "pickle"))
    for field in RUNTIME_FIELDS:
        mutate("missing-runtime-" + field, del_nested(("runtime", field)))
    mutate("runtime-python-old", set_nested(("runtime", "python_version"), "3.9.1"))
    mutate("runtime-torch-bad", set_nested(("runtime", "torch_version"), "torch"))
    mutate("runtime-device-cuda", set_nested(("runtime", "device"), "cuda"))
    mutate("runtime-threads-zero", set_nested(("runtime", "threads"), 0))
    mutate("runtime-threads-bool", set_nested(("runtime", "threads"), True))
    mutate("runtime-deterministic-false", set_nested(("runtime", "deterministic_algorithms"), False))
    mutate("runtime-seed-negative", set_nested(("runtime", "seed"), -1))
    mutate("runtime-seed-bool", set_nested(("runtime", "seed"), True))
    mutate("runtime-install-digest", set_nested(("runtime", "install_digest"), "bad"))
    mutate("features-empty", set_nested(("features",), []))
    for field in FEATURE_FIELDS:
        mutate("missing-feature-" + field, del_nested(("features", 0, field)))
    mutate("features-duplicate-id", lambda d: d["features"].append(dict(d["features"][0])))
    mutate("features-path-relative", set_nested(("features", 0, "path"), "a.wav"))
    mutate("features-sha", set_nested(("features", 0, "sha256"), "bad"))
    mutate("features-rate-bad", set_nested(("features", 0, "sample_rate_hz"), 32000))
    mutate("features-nmels-zero", set_nested(("features", 0, "n_mels"), 0))
    mutate("features-hop-zero", set_nested(("features", 0, "hop_samples"), 0))
    mutate("features-frames-zero", set_nested(("features", 0, "frame_count"), 0))
    mutate("features-kind", set_nested(("features", 0, "feature_kind"), "unknown"))
    mutate("features-language", set_nested(("features", 0, "language"), "English"))
    mutate("controls-empty", set_nested(("controls",), []))
    for field in CONTROL_FIELDS:
        mutate("missing-control-" + field, del_nested(("controls", 0, field)))
    mutate("controls-bad-kind", set_nested(("controls", 0, "kind"), "unknown"))
    mutate("controls-duplicate-kind", set_nested(("controls", 1, "kind"), "identity"))
    mutate("controls-missing-identity", lambda d: d.__setitem__("controls", [r for r in d["controls"] if r["kind"] != "identity"]))
    mutate("controls-missing-noisy", lambda d: d.__setitem__("controls", [r for r in d["controls"] if r["kind"] != "noisy"]))
    mutate("controls-missing-baseline", lambda d: d.__setitem__("controls", [r for r in d["controls"] if r["kind"] != "conventional_baseline"]))
    mutate("controls-unknown-feature", set_nested(("controls", 0, "feature_id"), "feat-missing"))
    mutate("controls-digest-mismatch", set_nested(("controls", 0, "feature_sha256"), "0" * 64))
    for field in OUTCOME_FIELDS:
        mutate("missing-outcome-" + field, del_nested(("outcomes", field)))
    mutate("outcome-sisdr-nan", set_nested(("outcomes", "si_sdr_db"), float("nan")))
    mutate("outcome-sisdr-inf", set_nested(("outcomes", "si_sdr_db"), float("inf")))
    mutate("outcome-sisdr-low", set_nested(("outcomes", "si_sdr_db"), -101.0))
    mutate("outcome-stoi-high", set_nested(("outcomes", "stoi"), 1.1))
    mutate("outcome-pesq-low", set_nested(("outcomes", "pesq"), -0.6))
    mutate("outcome-preserve-high", set_nested(("outcomes", "clean_speech_preservation_db"), 101.0))
    mutate("outcome-peak-high", set_nested(("outcomes", "peak_abs"), MAX_PEAK + 0.1))
    mutate("outcome-clipped-high", set_nested(("outcomes", "clipped_fraction"), 1.1))
    mutate("outcome-nonfinite-count", set_nested(("outcomes", "nonfinite_count"), 1))
    mutate("outcome-sample-zero", set_nested(("outcomes", "sample_count"), 0))
    mutate("outcome-sample-bool", set_nested(("outcomes", "sample_count"), True))
    mutate("outcome-output-rate", set_nested(("outcomes", "output_sample_rate_hz"), 32000))
    for field in RIGHTS_FIELDS:
        mutate("missing-rights-" + field, del_nested(("rights", field)))
    mutate("rights-consent-empty", set_nested(("rights", "consent_reference"), ""))
    mutate("rights-panel-zero", set_nested(("rights", "listening_panel_size"), 0))
    mutate("rights-panel-bool", set_nested(("rights", "listening_panel_size"), True))

    return {
        "control": {"id": "schema-control", "status": "accepted_schema_control", "evidence_class": "synthetic_schema_control_not_evidence", "qualifies": False, "accepted": accepted["accepted"], "checks": accepted["checks"]},
        "cases": cases,
        "summary": {"case_count": len(cases), "rejected_count": sum(1 for c in cases if c["status"] == "rejected"), "accepted_schema_controls": 1, "qualifying_results": 0, "state_advanced_on_rejection": False, "runtime_invoked": False, "audio_read": False, "feature_input_read": False, "weights_loaded": False, "model_executed": False, "network_used": False},
    }


def admission_contract_block() -> dict:
    return {
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "source_fields": list(SOURCE_FIELDS),
        "weight_fields": list(WEIGHT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "feature_fields": list(FEATURE_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "weight_formats": list(WEIGHT_FORMATS),
        "weight_suffixes": list(WEIGHT_SUFFIXES),
        "feature_kinds": list(FEATURE_KINDS),
        "required_weight_token": REQUIRED_WEIGHT_TOKEN,
        "upstream_project": "WaveFit",
        "upstream_revision": None,
        "device": "cpu",
        "python_version_pattern": PYTHON_VERSION.pattern,
        "torch_version_policy": "pinned_semver_recorded_by_caller",
        "input_sample_rates_hz": list(INPUT_SAMPLE_RATES),
        "output_sample_rates_hz": list(OUTPUT_SAMPLE_RATES),
        "max_weight_bytes": MAX_WEIGHT_BYTES, "max_threads": MAX_THREADS, "max_seed": MAX_SEED,
        "max_frame_count": MAX_FRAME_COUNT, "max_hop_samples": MAX_HOP, "max_n_mels": MAX_N_MELS,
        "max_peak": MAX_PEAK, "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "audio_read": False, "feature_input_read": False, "weights_loaded": False, "model_executed": False, "network_used": False,
    }


def _public_v0_geometry() -> dict:
    return {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32", "frame_samples": 160, "preserved": True, "sdk_callback_invoked": False, "model_io_claimed": False, "sdk_compatible": False}


def _scope() -> dict:
    return {"task_local_only": True, "source_present": False, "exact_upstream_source_present": False, "weights_present": False, "runtime_present": False, "weights_loaded": False, "model_executed": False, "real_corpus": False, "audio_read": False, "feature_input_read": False, "listening": False, "quality_scored": False, "device_timing": False, "benchmark": False, "download_attempted": False, "network_used": False, "release_claim": False}


def _boundary() -> dict:
    return {"task_local_only": True, "files_outside_task_directory_written": False, "provider_registration": False, "descriptor_registry_change": False, "installed_v0_behavior_change": False, "public_api_abi_change": False, "shared_cmakelists_change": False, "ci_workflow_change": False, "default_selected": False, "enabled_by_default": False, "processor_exposure": False, "listening": False, "real_weights_or_runtime": False}


def _disposition() -> dict:
    return {"decision": "DEFER", "status": "incomplete", "proposal_only": True, "incomplete": True, "not_qualified": True, "qualification_status": "not_qualified", "promotion": "defer", "registered": False, "default_enabled": False, "expose_as_processor": False, "production_exposure": "DEFER", "missing_result_qualifies": False}


def _qualification() -> dict:
    return {"status": "not_qualified", "readiness": "incomplete", "not_qualified": True, "real_result_present": False, "quality_result": False, "paired_quality_result": False, "preservation_result": False, "peak_invalid_result": False, "listening_result": False, "alignment_result": False, "timing_result": False, "device_timing_result": False, "benchmark_result": False, "release_claim": False, "source_present": False, "exact_upstream_source_present": False, "weights_present": False, "runtime_present": False, "all_release_gates_blocked": True, "missing_result_promoted": False}


def _required_results() -> dict:
    return {"quality_result_present": False, "paired_quality_result_present": False, "preservation_result_present": False, "peak_invalid_result_present": False, "listening_result_present": False, "alignment_result_present": False, "timing_result_present": False, "device_timing_result_present": False, "benchmark_result_present": False, "exact_upstream_source_present": False, "weights_present": False, "runtime_present": False, "release_claim": False, "no_result_qualifies": True}


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID, "contract_id": CONTRACT_ID, "task": TASK, "component": COMPONENT_ID, "title": TASK_TITLE,
        "mode": MODE, "branch": BRANCH, "base_commit": BASE_COMMIT, "profile": PROFILE_LABEL, "profile_key": PROFILE.lower(),
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md", "profile_phrases": list(PROFILE_PHRASES),
        "decision": "DEFER", "status": "incomplete", "qualification_status": "not_qualified", "proposal_only": True,
        "write_scope": WRITE_SCOPE,
        "exact_scope": "Task-local WaveFit research-control blocker evidence: absence pins, fail-closed enhancement admission, blocked profile accounting and eight blocked release gates. No model, weights, runtime, cohort or result.",
        "public_v0_geometry": _public_v0_geometry(), "source_pins": SOURCE_PINS, "boundary_pins": BOUNDARY_PINS,
        "board_file_pinned": False, "board_row_fields": list(BOARD_ROW_FIELDS), "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION), "linked_rows": [dict(r) for r in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(), "board_status_is_observation_only": True,
        "absence_policy": {"any_present_probe_blocks_shipping": True, "download_attempted": False, "network_used": False, "fixed_probe_list_only": True, "recursive_workspace_walk": False},
        "absence_probes": list(ABSENCE_PROBES), "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "upstream_project": "WaveFit", "upstream_revision": None,
        "required_weight_files": ["exact WaveFit checkpoint selected for qualification, with immutable source/revision, filename, byte count, SHA-256 and format", "exact input/output geometry and runtime config required by that checkpoint"],
        "source_presence": SOURCE_PRESENCE, "required_artifacts": [dict(r) for r in REQUIRED_ARTIFACTS], "exact_blockers": [dict(r) for r in EXACT_BLOCKERS],
        "release_gates": [dict(r) for r in RELEASE_GATES], "enhancement_profile_requirements": [dict(r) for r in ENHANCEMENT_PROFILE_ROWS],
        "quality_outcomes": [dict(r) for r in QUALITY_OUTCOME_ROWS], "timing_requirements": [dict(r) for r in TIMING_ROWS],
        "admission_contract": admission_contract_block(), "non_claims": list(NON_CLAIMS), "scope": _scope(), "boundary": _boundary(),
        "disposition": _disposition(), "qualification": _qualification(), "required_results": _required_results(),
        "reproduction": {"interpreter": "Python 3.12, standard library only", "commands": ["python3 run.py all", "python3 -m unittest -v test_reference.py", "python3 verify.py"], "cold_start_repeats": 3, "network_required": False, "runtime_required": False},
    }


CONTRACT_FIELDS = tuple(build_contract().keys())


def validate_contract(document: dict) -> None:
    if set(document) != set(CONTRACT_FIELDS):
        missing = sorted(set(CONTRACT_FIELDS) - set(document))
        extra = sorted(set(document) - set(CONTRACT_FIELDS))
        raise ValueError("contract_field_mismatch:" + (missing[0] if missing else extra[0]))
    _no_floats(document)
    if document["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if document["task"] != TASK or document["component"] != COMPONENT_ID:
        raise ValueError("contract_identity_mismatch")
    if document["decision"] != "DEFER" or document["status"] != "incomplete" or document["qualification_status"] != "not_qualified":
        raise ValueError("contract_disposition_mismatch")
    if document["proposal_only"] is not True or document["board_file_pinned"] is not False:
        raise ValueError("contract_flags_mismatch")
    if document["board_row_projection"] != BOARD_ROW_PROJECTION or document["board_row_sha256"] != board_row_digest(BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_projection_mismatch")
    if document["linked_rows_sha256"] != linked_rows_digest():
        raise ValueError("contract_linked_rows_mismatch")
    if len(document["release_gates"]) != 8 or len(document["required_artifacts"]) != 6 or len(document["exact_blockers"]) != 5:
        raise ValueError("contract_count_mismatch")
    for i, gate in enumerate(document["release_gates"], 1):
        if gate["id"] != f"RG-{i:02d}" or gate["status"] != "blocked" or gate["qualifies"] is not False:
            raise ValueError("contract_gate_not_blocked")
    if not document["required_artifacts"][0]["present"]:
        raise ValueError("contract_research_artifact_missing")
    for a in document["required_artifacts"][1:]:
        if a["present"] is not False or a["blocked"] is not True:
            raise ValueError("contract_artifact_not_blocked")
    for b in document["exact_blockers"]:
        if b["status"] != "open" or b["qualifies"] is not False:
            raise ValueError("contract_blocker_not_open")
    for row in document["enhancement_profile_requirements"]:
        if row["status"] != "blocked":
            raise ValueError("contract_profile_not_blocked")
    if document["admission_contract"] != admission_contract_block():
        raise ValueError("contract_admission_contract_mismatch")
    if document["source_pins"] != SOURCE_PINS or document["boundary_pins"] != BOUNDARY_PINS:
        raise ValueError("contract_pins_mismatch")
    for section in ("scope", "boundary"):
        for k, v in document[section].items():
            if k == "task_local_only":
                if v is not True:
                    raise ValueError("contract_scope_mismatch:" + k)
            elif v is not False:
                raise ValueError("contract_" + section + "_claim:" + k)


def build_report() -> dict:
    contract = build_contract()
    source_rows = pin_rows(SOURCE_PINS, AUDIO_ROOT)
    boundary_rows = pin_rows(BOUNDARY_PINS, WORKTREE)
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
    admission = admission_controls()
    if not admission["control"]["accepted"]:
        raise ValueError("schema_control_not_accepted")
    for case in admission["cases"]:
        if case["status"] != "rejected":
            raise ValueError("admission_case_not_rejected:" + case["id"])
    return {
        "schema_id": REPORT_SCHEMA_ID, "task": TASK, "component": COMPONENT_ID, "title": TASK_TITLE,
        "profile": PROFILE_LABEL, "profile_key": PROFILE.lower(), "branch": BRANCH, "base_commit": BASE_COMMIT,
        "decision": "DEFER", "status": "incomplete", "qualification_status": "not_qualified", "proposal_only": True,
        "disposition": _disposition(), "qualification": _qualification(), "contract_sha256": object_digest(contract),
        "source_pins": source_rows, "boundary_pins": boundary_rows, "source_presence": SOURCE_PRESENCE,
        "absence_evidence": {"summary": absence_summary(workspace_rows, home_rows), "probes": workspace_rows, "home_probes": home_rows},
        "admission": admission, "required_artifacts": contract["required_artifacts"], "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "enhancement_profile": {"profile": PROFILE_LABEL, "rows": contract["enhancement_profile_requirements"]},
        "quality_outcomes": {"rows": contract["quality_outcomes"]}, "timing": {"rows": contract["timing_requirements"]},
        "linked_row_identity": {"projection": dict(BOARD_ROW_PROJECTION), "sha256": board_row_digest(BOARD_ROW_PROJECTION), "linked_rows": [dict(r) for r in LINKED_ROWS], "linked_rows_sha256": linked_rows_digest(), "gating": "stable_identity_only", "board_file_pinned": False, "board_status_gates_anything": False},
        "required_results": contract["required_results"], "scope": contract["scope"], "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"], "non_claims": contract["non_claims"], "reproduction": contract["reproduction"],
    }


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    report = build_report() if document is None else document
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


LOCAL_PIN_PATHS = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "LICENSES.md",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
ARTIFACT_TABLE_EXCLUDED = {"README.md", "SOURCES.sha256"}


def build_artifacts() -> dict[str, bytes]:
    contract = build_contract()
    report = build_report()
    validate_contract(contract)
    report_text, report_digest = canonical_report(report)
    return {
        "contract.json": canonical_bytes(contract),
        "report.json": report_text.encode("utf-8"),
        "report.json.sha256": f"{report_digest}  report.json\n".encode("ascii"),
    }


def write_artifacts() -> dict[str, str]:
    artifacts = build_artifacts()
    for name, payload in artifacts.items():
        (HERE / name).write_bytes(payload)
    sources = sources_bytes()
    (HERE / "SOURCES.sha256").write_bytes(sources)
    out = {name: hashlib.sha256(payload).hexdigest() for name, payload in artifacts.items()}
    out["SOURCES.sha256"] = hashlib.sha256(sources).hexdigest()
    return out


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(SOURCE_PINS.items()):
        actual = sha256_file(AUDIO_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        actual = sha256_file(WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append(("sdk:" + relative, actual))
    artifacts = build_artifacts()
    # include all local files that exist, except SOURCES.sha256 itself
    for name in LOCAL_PIN_PATHS:
        if name == "SOURCES.sha256":
            continue
        if name in artifacts:
            payload = artifacts[name]
        else:
            path = HERE / name
            if not path.is_file():
                raise ValueError("local_pin_missing:" + name)
            payload = path.read_bytes()
        rows.append((TASK_PREFIX + name, hashlib.sha256(payload).hexdigest()))
    lines = [
        "# SHA-256 pins for SDK-WAVEFIT task-local readiness evidence.",
        "# source: paths are relative to AUDIO_ROOT; sdk: paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only its stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


# ---------------------------------------------------------------------------
# README digest validation
# ---------------------------------------------------------------------------

README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: source:end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: boundary:end -->"),
    "artifacts": ("<!-- digest-table: artifacts -->", "<!-- digest-table: artifacts:end -->"),
}


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        start, end = README_MARKERS[section]
        if text.count(start) != 1 or text.count(end) != 1:
            raise ValueError("readme_marker_count:" + section)
        block = text.split(start, 1)[1].split(end, 1)[0]
        rows = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            digest = cells[1].strip("`") if len(cells) > 1 else ""
            if not HEX64.match(digest):
                raise ValueError("readme_bad_digest:" + section)
            rows.append((key, digest))
        if len({k for k, _ in rows}) != len(rows):
            raise ValueError("readme_duplicate_row:" + section)
        result[section] = rows
    return result


def expected_readme_rows() -> dict[str, list[tuple[str, str]]]:
    source = [(f"source:{k}", v) for k, v in sorted(SOURCE_PINS.items())]
    boundary = [(f"sdk:{k}", v) for k, v in sorted(BOUNDARY_PINS.items())]
    artifacts = build_artifacts()
    art_rows = []
    for name in LOCAL_PIN_PATHS:
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        if name in artifacts:
            payload = artifacts[name]
        else:
            pth = HERE / name
            payload = pth.read_bytes() if pth.is_file() else b""
        art_rows.append((TASK_PREFIX + name, hashlib.sha256(payload).hexdigest()))
    return {"source": source, "boundary": boundary, "artifacts": art_rows}


def verify_readme_digests(text: str | None = None) -> dict[str, int]:
    readme = (HERE / "README.md").read_text(encoding="utf-8") if text is None else text
    parsed = parse_readme_digest_tables(readme)
    expected = expected_readme_rows()
    for section in README_SECTIONS:
        if parsed[section] != expected[section]:
            raise ValueError("readme_digest_mismatch:" + section)
    return {s: len(parsed[s]) for s in README_SECTIONS}
