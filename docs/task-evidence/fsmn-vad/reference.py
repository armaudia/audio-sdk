# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-FSMN-VAD.

This module never loads a model, imports FunASR, reads audio, runs inference,
scores accuracy, performs listening, measures a device or produces a release
claim. The exact FSMN-VAD source, checkpoint and runtime are absent. The module
pins stable read-only inputs, proves the fixed absence probes, exercises a
fail-closed caller-supplied-asset admission schema and emits canonical JSON.
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

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/fsmn-vad/"

TASK = "SDK-FSMN-VAD"
TITLE = "FSMN VAD"
COMPONENT = "fsmn-vad"
COMPONENT_ID = "fsmn-vad"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "analysis"
PROFILE_KEY = "Analysis"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/fsmn-vad-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/fsmn-vad-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/fsmn-vad-report/0.1"
BASE_COMMIT = "77d7800cac82899eb02a8aa55535d00e4faa8946"
BRANCH = "swarm/SDK-FSMN-VAD"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-FSMN-VAD")
REVIEWER = "reviewer-FSMN-VAD"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/plans/F02/vad_sources.md":
        "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
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
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "evidence", "deliverable", "acceptance",
    "write_scope",
)
STABLE_TASK_FIELDS = ("id", "title", "component", "mode", "repository",
                      "depends_on")
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Score timestamped probabilities",
    "event boundaries and detections",
    "quiet and active speech",
    "idle noise",
    "known positives and negatives",
    "onset/offset delay",
    "stratified FN/FP",
    "Separate validity from nonspeech",
    "independent state",
    "exact source intervals",
    "availability",
    "dropped/stale events",
    "cross-hop behavior",
)

# ---------------------------------------------------------------------------
# Exact upstream identity requirements. No revision, digest or file name is
# asserted as present or verified; these are the missing-artifact requirements.
# ---------------------------------------------------------------------------

TOOLKIT_REPOSITORY = "https://github.com/modelscope/FunASR"
STREAMING_VAD_DOCS = ("https://github.com/modelscope/FunASR/blob/main/docs/"
                      "streaming_vad.md")
MODEL_ID = "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"
TASK_KIND = "neural_streaming_voice_activity_endpoint_detection"
CANDIDATE_FAMILY = "FSMN streaming VAD"
LANGUAGE_FOCUS = "Chinese-oriented (census note)"
DECLARED_SAMPLE_RATE_HZ = 16_000
CENSUS_PATH = "research/plans/F02/vad_sources.md"
NOISE_CENSUS_PATH = "research/noise_suppression_candidate_census.md"

SOURCE_PROBE_PATHS = (
    "research/voice-enhancement-20261101/repos/fsmn-vad",
    "research/voice-enhancement-20261101/repos/FunASR",
    "research/voice-enhancement-20261101/repos/funasr",
    "research/fsmn-vad",
    "research/FunASR",
    "data/checkouts/fsmn-vad",
)
WEIGHTS_PROBE_PATHS = (
    "research/voice-enhancement-20261101/models/fsmn-vad",
    "research/models/fsmn-vad",
    "data/models/fsmn-vad",
)
RUNTIME_PROBE_PATHS = (
    "research/voice-enhancement-20261101/envs/fsmn-vad",
    "research/voice-enhancement-20261101/.venv-fsmn-vad",
    "data/envs/fsmn-vad",
    ".venv-fsmn-vad",
    "adapters/fsmn-vad",
)
HOME_PROBE_PATHS = (
    "~/.cache/modelscope/hub/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    "~/.cache/modelscope/hub/models/iic/"
    "speech_fsmn_vad_zh-cn-16k-common-pytorch",
    "~/.cache/huggingface/hub/"
    "models--iic--speech_fsmn_vad_zh-cn-16k-common-pytorch",
    "~/.venvs/fsmn-vad",
    "~/.local/share/fsmn-vad",
)
SOURCE_ROOT_REL = "research/voice-enhancement-20261101/repos"
SCOPE_BASE_REFS = ("origin/main", "main")

NON_CLAIMS = [
    "No FunASR/FSMN-VAD source copy, checkpoint, weight fragment, config, "
    "feature asset, runtime, adapter, corpus, reference, probability vector, "
    "event vector or vendor result is present, loaded, linked or executed by "
    "this package.",
    "No model inference, audio read, audio write, listening, frame-probability "
    "scoring, event-boundary scoring, onset/offset delay, stratified FN/FP, "
    "AUC or device-timing measurement is performed.",
    "No real speech/nonspeech corpus, known positive or negative item, "
    "condition label, language or speaker group or held-out split is used "
    "here.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "single accepted synthetic schema control is not evidence.",
    "No adjacent Silero, WebRTC, fast-vad, adaptive-energy, fixed-RMS, "
    "SpeexDSP, CNN-BiLSTM or CRNN VAD result is inherited, pooled or promoted "
    "to FSMN-VAD.",
    "No benchmark, accuracy, miss-rate, false-alarm, timing, streaming, "
    "resource or release claim is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; the absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "silero-vad-v5-onnx-reference",
        "task": "SDK-SILERO-VAD-V5-ONNX-REFERENCE",
        "path": "docs/task-evidence/silero-vad-v5-onnx-reference/report.json",
        "class": "adjacent_vad_reference",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A separate ONNX Silero reference with its own assets and "
                    "geometry; no FSMN-VAD weight, probability or metric is "
                    "inherited.",
    },
    {
        "component": "silero-vad-6-2-3-reference",
        "task": "SDK-SILERO-VAD-6-2-3-REFERENCE",
        "path": "docs/task-evidence/silero-vad-6-2-3-reference/report.json",
        "class": "adjacent_vad_reference",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different Silero release and runtime; its parity and "
                    "timing evidence do not apply to an FSMN checkpoint.",
    },
    {
        "component": "cnn-bilstm-vad",
        "task": "SDK-CNN-BILSTM-VAD",
        "path": "docs/task-evidence/cnn-bilstm-vad/report.json",
        "class": "adjacent_vad_blocker",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A synthetic two-path control for a different VAD family; "
                    "its surrogate counts are not FSMN-VAD behaviour.",
    },
    {
        "component": "webrtc-vad",
        "task": "SDK-WEBRTC-VAD",
        "path": "docs/task-evidence/webrtc-vad/report.json",
        "class": "adjacent_classical_vad",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A non-learned WebRTC frame detector; its integration "
                    "diagnostics are not FSMN probability or endpoint results.",
    },
    {
        "component": "crnn-vad",
        "task": "SDK-CRNN-VAD",
        "path": "docs/task-evidence/crnn-vad/report.json",
        "class": "adjacent_vad_blocker",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different underspecified neural VAD; no checkpoint, "
                    "state, hop or score transfers to FSMN-VAD.",
    },
)

ANALYSIS_REQUIREMENTS = (
    ("ANA-01", "Score timestamped probabilities.",
     "No FSMN-VAD probability vector, timestamp grid or exact runtime exists."),
    ("ANA-02", "Score event boundaries and detections.",
     "No start/end sentinel events or detection list is produced or scored."),
    ("ANA-03", "Include quiet and active speech.",
     "No real quiet-speech or active-speech stratum is present."),
    ("ANA-04", "Include idle noise.",
     "No real idle-noise or nonspeech item is present."),
    ("ANA-05", "Include known positives and negatives.",
     "No rights-cleared known-positive or known-negative item exists."),
    ("ANA-06", "Measure onset and offset delay.",
     "No source interval, decision time or delay measurement exists."),
    ("ANA-07", "Report stratified false negatives and false positives.",
     "No continuous truth, scored region or stratified FN/FP count exists."),
    ("ANA-08", "Separate validity from nonspeech.",
     "No validity state, unknown span or excluded region is defined for the "
     "candidate."),
    ("ANA-09", "Verify independent state.",
     "No FSMN recurrent/internal state, session reset or fresh-session parity "
     "record exists."),
    ("ANA-10", "Verify exact source intervals.",
     "No hop, window, timestamp base or half-open sample interval is pinned."),
    ("ANA-11", "Verify availability and dropped/stale events.",
     "No target runtime, deadline, dropped-event or stale-event measurement "
     "exists."),
    ("ANA-12", "Verify cross-hop behavior.",
     "No hop or arbitrary-chunk schedule exists to test cross-hop handling."),
)


# ---------------------------------------------------------------------------
# Strict JSON and canonical bytes.
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


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    return loads_strict(text)


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


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
    board = SOURCE_ROOT / BOARD_TASK_ROW if path is None else Path(path)
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
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    root = by_id.get(TASK)
    if root is None:
        raise ValueError("board_row_absent")
    projection = _project(root, require_component=True)
    result = [projection]
    for dependency in projection["depends_on"]:
        row = by_id.get(dependency)
        if row is None:
            raise ValueError("linked_row_absent:" + dependency)
        result.append(_project(row))
    return tuple(result)


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    value = linked_rows() if rows is None else rows
    return object_digest([dict(row) for row in value])


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


# ---------------------------------------------------------------------------
# Fixed absence probes.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: tuple[str, ...], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        present = ((SOURCE_ROOT / relative).exists()
                   or (WORKTREE / relative).exists())
        if present:
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def _home_rows(paths: tuple[str, ...]) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        path = Path(os.path.expanduser(relative))
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": "home",
            "present": False,
            "searched_home_cache": True,
        })
    return rows


def source_probe() -> dict:
    return {
        "status": "blocked_exact_source_absent",
        "present": False,
        "executed": False,
        "revision_verified": False,
        "license_verified": False,
        "source_root": SOURCE_ROOT_REL,
        "source_root_present": (SOURCE_ROOT / SOURCE_ROOT_REL).is_dir(),
        "toolkit_repository": TOOLKIT_REPOSITORY,
        "candidates": _workspace_rows(SOURCE_PROBE_PATHS, "source"),
    }


def weights_probe() -> dict:
    return {
        "status": "blocked_exact_checkpoint_absent",
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": 0,
        "model_id": MODEL_ID,
        "model_file_requirement":
            "caller-selected checkpoint bundle at an immutable 40-hex "
            "revision; every weight, config, feature asset, model card and "
            "terms file with byte count and SHA-256",
        "candidates": _workspace_rows(WEIGHTS_PROBE_PATHS, "weights"),
        "home_cache": _home_rows(HOME_PROBE_PATHS),
        "files": [
            {"kind": "checkpoint_weights", "present": False, "admitted": False},
            {"kind": "config", "present": False, "admitted": False},
            {"kind": "feature_assets", "present": False, "admitted": False},
            {"kind": "model_card_terms", "present": False, "admitted": False},
        ],
    }


def runtime_probe() -> dict:
    return {
        "status": "blocked_pinned_runtime_absent",
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "package_lock_present": False,
        "imported_or_executed": False,
        "required_runtime": "caller-supplied locked Python and native/ONNX "
                            "runtime; exact interpreter and package versions "
                            "are not asserted here",
        "candidates": _workspace_rows(RUNTIME_PROBE_PATHS, "runtime"),
        "home_candidates": _home_rows(
            ("~/.venvs/fsmn-vad", "~/.local/share/fsmn-vad")),
    }


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    rows.extend(_workspace_rows(SOURCE_PROBE_PATHS, "source"))
    rows.extend(_workspace_rows(WEIGHTS_PROBE_PATHS, "weights"))
    rows.extend(_workspace_rows(RUNTIME_PROBE_PATHS, "runtime"))
    return rows


def absence_summary(probes: list[dict]) -> dict:
    return {
        "probe_count": len(probes),
        "present_count": sum(1 for row in probes
                             if row.get("present") is not False),
        "all_probes_absent": all(row.get("present") is False for row in probes),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied-asset admission contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = "audio-sdk/fsmn-vad-reference-bundle/0.1"
MANIFEST_TOP_KEYS = (
    "schema_id", "bundle_id", "source", "weights", "runtime", "geometry",
    "cohort", "conditions", "outcomes", "rights",
)
MAX_MANIFEST_FILES = 32
MAX_MANIFEST_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_COHORT_ITEMS = 10_000
MAX_PACKAGES = 128
MAX_DURATION_MS = 3_600_000
ADMISSIBLE_SAMPLE_RATES = (16_000,)
MAX_HOP_SAMPLES = 4096
CONDITION_KEYS = (
    "stream_probabilities", "event_boundaries", "detections",
    "quiet_and_active_speech", "idle_noise", "known_positives_and_negatives",
    "onset_offset_delay", "stratified_fn_fp", "validity_separation",
    "independent_state", "exact_source_intervals", "availability",
    "dropped_stale_events", "cross_hop_behavior",
)
OUTCOME_KEYS = (
    "timestamped_probabilities", "event_boundaries", "detections",
    "onset_offset_delay", "stratified_fn_fp", "validity", "availability",
    "cross_hop_behavior",
)
RIGHT_KEYS = (
    "code_license", "weights_terms", "training_data_provenance", "corpus_rights",
    "output_use", "redistribution",
)
COHORT_CONDITIONS = (
    "quiet_speech", "active_speech", "idle_noise", "known_positive",
    "known_negative", "mixed",
)
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "none", "null", "n/a", "noassertion",
}


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


def _safe_relative(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise _Invalid("unsafe_path", field)
    if value.startswith("/") or "\\" in value or ":" in value:
        raise _Invalid("unsafe_path", field)
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
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


def validate_bundle(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object", "")
    try:
        _exact_object(document, MANIFEST_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["bundle_id"], "bundle_id")
        checks += 1

        source_fields = ("repository", "revision", "license_spdx",
                         "license_sha256")
        source = _exact_object(document["source"], source_fields, "source")
        _text(source["repository"], "source.repository")
        _hex40(source["revision"], "source.revision")
        _text(source["license_spdx"], "source.license_spdx", 80)
        _sha(source["license_sha256"], "source.license_sha256")
        checks += 5

        weights_fields = ("model_id", "revision", "files", "terms_reviewed")
        weights = _exact_object(document["weights"], weights_fields, "weights")
        _text(weights["model_id"], "weights.model_id")
        _hex40(weights["revision"], "weights.revision")
        _boolean(weights["terms_reviewed"], "weights.terms_reviewed")
        files = _list(weights["files"], "weights.files", 1,
                      MAX_MANIFEST_FILES)
        for index, item in enumerate(files):
            prefix = "weights.files[" + str(index) + "]"
            _exact_object(item, ("path", "sha256", "bytes"), prefix)
            _safe_relative(item["path"], prefix + ".path")
            _sha(item["sha256"], prefix + ".sha256")
            _bounded_int(item["bytes"], 1, MAX_MANIFEST_FILE_BYTES,
                         prefix + ".bytes")
            checks += 3
        _sorted_unique(files, "path", "weights.files")
        checks += 4
        if not weights["terms_reviewed"]:
            raise _Invalid("rights_not_cleared", "weights.terms_reviewed")

        runtime_fields = ("python_version", "device", "lock_sha256",
                          "offline_load", "packages")
        runtime = _exact_object(document["runtime"], runtime_fields, "runtime")
        _version(runtime["python_version"], "runtime.python_version")
        _text(runtime["device"], "runtime.device", 120)
        _sha(runtime["lock_sha256"], "runtime.lock_sha256")
        _boolean(runtime["offline_load"], "runtime.offline_load")
        packages = _list(runtime["packages"], "runtime.packages", 1,
                         MAX_PACKAGES)
        for index, item in enumerate(packages):
            prefix = "runtime.packages[" + str(index) + "]"
            _exact_object(item, ("name", "version"), prefix)
            _text(item["name"], prefix + ".name", 120)
            _text(item["version"], prefix + ".version", 120)
            checks += 2
        _sorted_unique(packages, "name", "runtime.packages")
        checks += 4
        if not runtime["offline_load"]:
            raise _Invalid("non_offline_runtime", "runtime.offline_load")

        geometry_fields = ("sample_rate_hz", "channels", "hop_samples",
                           "streaming", "chunk_finalization")
        geometry = _exact_object(document["geometry"], geometry_fields,
                                 "geometry")
        _bounded_int(geometry["sample_rate_hz"], 8_000, 192_000,
                     "geometry.sample_rate_hz")
        if geometry["sample_rate_hz"] not in ADMISSIBLE_SAMPLE_RATES:
            raise _Invalid("out_of_range", "geometry.sample_rate_hz")
        _bounded_int(geometry["channels"], 1, 8, "geometry.channels")
        if geometry["channels"] != 1:
            raise _Invalid("invalid_geometry", "geometry.channels")
        _bounded_int(geometry["hop_samples"], 1, MAX_HOP_SAMPLES,
                     "geometry.hop_samples")
        _boolean(geometry["streaming"], "geometry.streaming")
        _boolean(geometry["chunk_finalization"],
                 "geometry.chunk_finalization")
        checks += 6
        if not geometry["streaming"]:
            raise _Invalid("non_streaming_bundle", "geometry.streaming")
        if not geometry["chunk_finalization"]:
            raise _Invalid("chunk_finalization_not_declared",
                           "geometry.chunk_finalization")

        cohort = _list(document["cohort"], "cohort", 1, MAX_COHORT_ITEMS)
        for index, item in enumerate(cohort):
            prefix = "cohort[" + str(index) + "]"
            _exact_object(item, ("id", "waveform_sha256", "sample_rate_hz",
                                 "duration_ms", "condition", "consent", "split"),
                          prefix)
            _slug(item["id"], prefix + ".id")
            _sha(item["waveform_sha256"], prefix + ".waveform_sha256")
            _bounded_int(item["sample_rate_hz"], 8_000, 192_000,
                         prefix + ".sample_rate_hz")
            if item["sample_rate_hz"] not in ADMISSIBLE_SAMPLE_RATES:
                raise _Invalid("out_of_range", prefix + ".sample_rate_hz")
            _bounded_int(item["duration_ms"], 1, MAX_DURATION_MS,
                         prefix + ".duration_ms")
            if item["condition"] not in COHORT_CONDITIONS:
                raise _Invalid("invalid_condition", prefix + ".condition")
            _boolean(item["consent"], prefix + ".consent")
            if item["split"] not in ("dev", "test", "heldout"):
                raise _Invalid("invalid_split", prefix + ".split")
            if not item["consent"]:
                raise _Invalid("rights_not_cleared", prefix + ".consent")
            checks += 8
        _sorted_unique(cohort, "id", "cohort")
        checks += 1

        checks += _require_true_map(document["conditions"], CONDITION_KEYS,
                                    "conditions")
        checks += _require_true_map(document["outcomes"], OUTCOME_KEYS,
                                    "outcomes")
        checks += _require_true_map(document["rights"], RIGHT_KEYS, "rights")
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _bundle_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "bundle_id": "fsmn-vad-synthetic-schema-control",
        "source": {
            "repository": TOOLKIT_REPOSITORY,
            "revision": "0" * 40,
            "license_spdx": "MIT",
            "license_sha256": "1" * 64,
        },
        "weights": {
            "model_id": MODEL_ID,
            "revision": "2" * 40,
            "files": [
                {
                    "path": "controls/model.onnx",
                    "sha256": "3" * 64,
                    "bytes": 1024,
                }
            ],
            "terms_reviewed": True,
        },
        "runtime": {
            "python_version": "3.12.0",
            "device": "synthetic-cpu-control",
            "lock_sha256": "4" * 64,
            "offline_load": True,
            "packages": [{"name": "onnxruntime", "version": "1.20.0"}],
        },
        "geometry": {
            "sample_rate_hz": 16_000,
            "channels": 1,
            "hop_samples": 160,
            "streaming": True,
            "chunk_finalization": True,
        },
        "cohort": [
            {
                "id": "item-01",
                "waveform_sha256": "5" * 64,
                "sample_rate_hz": 16_000,
                "duration_ms": 1000,
                "condition": "active_speech",
                "consent": True,
                "split": "dev",
            }
        ],
        "conditions": {name: True for name in CONDITION_KEYS},
        "outcomes": {name: True for name in OUTCOME_KEYS},
        "rights": {name: True for name in RIGHT_KEYS},
    }


def _mutation_case(case_id: str, mutate: Any, code: str) -> dict:
    document = copy.deepcopy(_bundle_control())
    mutate(document)
    result = validate_bundle(document)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("mutation_case_did_not_reject:" + case_id + ":" +
                         str(result))
    return _case_row(case_id, result, False)


def _raw_case(case_id: str, raw: str, code: str) -> dict:
    try:
        loads_strict(raw)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("raw_case_code_mismatch:" + case_id + ":" +
                             observed) from error
        return _case_row(case_id, _reject(observed), False)
    raise ValueError("raw_case_did_not_reject:" + case_id)


def _case_row(case_id: str, result: dict, synthetic: bool,
              accepted: bool = False) -> dict:
    return {
        "id": case_id,
        "status": "accepted" if accepted else result["status"],
        "code": result.get("code", "none") if not accepted else "none",
        "field": result.get("field", ""),
        "qualifies": False,
        "state_unchanged": not accepted,
        "synthetic_schema_control": synthetic,
    }


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_bundle(_bundle_control()), True,
                         accepted=True)
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_bundle(["not", "a", "bundle"]), False))
    cases.append(_case_row("root-null", validate_bundle(None), False))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"audio-sdk/fsmn-vad-reference-bundle/0.1",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"audio-sdk/fsmn-vad-reference-bundle/0.1",'
        '"value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"audio-sdk/fsmn-vad-reference-bundle/0.1",'
        '"value":Infinity}',
        "nonfinite_json"))
    cases.append(_mutation_case(
        "invalid-schema-id", lambda m: m.update({"schema_id": "wrong"}),
        "invalid_schema_id"))
    cases.append(_mutation_case(
        "invalid-bundle-id", lambda m: m.update({"bundle_id": "Not A Slug"}),
        "invalid_slug"))
    cases.append(_mutation_case(
        "missing-source", lambda m: m.pop("source"), "missing_field"))
    cases.append(_mutation_case(
        "unknown-top-key", lambda m: m.update({"extra": True}),
        "unknown_field"))
    cases.append(_mutation_case(
        "invalid-source-revision",
        lambda m: m["source"].update({"revision": "abc"}),
        "invalid_revision"))
    cases.append(_mutation_case(
        "invalid-license-sha",
        lambda m: m["source"].update({"license_sha256": "xyz"}),
        "invalid_sha256"))
    cases.append(_mutation_case(
        "empty-weight-files",
        lambda m: m["weights"].update({"files": []}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "unsorted-weight-files",
        lambda m: m["weights"].update({"files": [
            {"path": "b/model.onnx", "sha256": "6" * 64, "bytes": 2},
            {"path": "a/model.onnx", "sha256": "7" * 64, "bytes": 1},
        ]}),
        "noncanonical_order"))
    cases.append(_mutation_case(
        "duplicate-weight-path",
        lambda m: m["weights"]["files"].append(
            dict(m["weights"]["files"][0])),
        "duplicate_value"))
    cases.append(_mutation_case(
        "traversal-weight-path",
        lambda m: m["weights"]["files"][0].update(
            {"path": "../model.onnx"}),
        "unsafe_path"))
    cases.append(_mutation_case(
        "boolean-byte-count",
        lambda m: m["weights"]["files"][0].update({"bytes": True}),
        "invalid_integer"))
    cases.append(_mutation_case(
        "zero-byte-count",
        lambda m: m["weights"]["files"][0].update({"bytes": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "unreviewed-weight-terms",
        lambda m: m["weights"].update({"terms_reviewed": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "missing-runtime-lock",
        lambda m: m["runtime"].pop("lock_sha256"), "missing_field"))
    cases.append(_mutation_case(
        "empty-runtime-device",
        lambda m: m["runtime"].update({"device": "  "}), "empty_text"))
    cases.append(_mutation_case(
        "non-offline-runtime",
        lambda m: m["runtime"].update({"offline_load": False}),
        "non_offline_runtime"))
    cases.append(_mutation_case(
        "duplicate-package-name",
        lambda m: m["runtime"]["packages"].append(
            {"name": "onnxruntime", "version": "1.20.1"}),
        "duplicate_value"))
    cases.append(_mutation_case(
        "unsupported-geometry-rate",
        lambda m: m["geometry"].update({"sample_rate_hz": 44100}),
        "out_of_range"))
    cases.append(_mutation_case(
        "stereo-geometry",
        lambda m: m["geometry"].update({"channels": 2}),
        "invalid_geometry"))
    cases.append(_mutation_case(
        "zero-hop",
        lambda m: m["geometry"].update({"hop_samples": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "non-streaming-geometry",
        lambda m: m["geometry"].update({"streaming": False}),
        "non_streaming_bundle"))
    cases.append(_mutation_case(
        "undeclared-chunk-finalization",
        lambda m: m["geometry"].update({"chunk_finalization": False}),
        "chunk_finalization_not_declared"))
    cases.append(_mutation_case(
        "empty-cohort", lambda m: m["cohort"].clear(),
        "missing_required_value"))
    cases.append(_mutation_case(
        "unsorted-cohort",
        lambda m: m["cohort"].append(dict(
            m["cohort"][0], id="item-00", waveform_sha256="8" * 64)),
        "noncanonical_order"))
    cases.append(_mutation_case(
        "duplicate-cohort-id",
        lambda m: m["cohort"].append(dict(
            m["cohort"][0], waveform_sha256="8" * 64)),
        "duplicate_value"))
    cases.append(_mutation_case(
        "invalid-cohort-sample-rate",
        lambda m: m["cohort"][0].update({"sample_rate_hz": 44100}),
        "out_of_range"))
    cases.append(_mutation_case(
        "zero-duration",
        lambda m: m["cohort"][0].update({"duration_ms": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "invalid-condition",
        lambda m: m["cohort"][0].update({"condition": "music"}),
        "invalid_condition"))
    cases.append(_mutation_case(
        "invalid-split",
        lambda m: m["cohort"][0].update({"split": "train"}),
        "invalid_split"))
    cases.append(_mutation_case(
        "unconsented-cohort-item",
        lambda m: m["cohort"][0].update({"consent": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "missing-condition",
        lambda m: m["conditions"].pop("stream_probabilities"),
        "missing_field"))
    cases.append(_mutation_case(
        "false-condition",
        lambda m: m["conditions"].update({"cross_hop_behavior": False}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "missing-outcome",
        lambda m: m["outcomes"].pop("detections"), "missing_field"))
    cases.append(_mutation_case(
        "false-right",
        lambda m: m["rights"].update({"output_use": False}),
        "rights_not_cleared"))

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    summary = {
        "case_count": len(cases),
        "rejected_count": len(rejected),
        "accepted_schema_controls": len(accepted_cases),
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "accepted_control_qualifies": False,
        "all_adverse_cases_rejected": len(rejected) == len(cases) -
        len(accepted_cases),
        "runtime_invoked": False,
        "weights_loaded": False,
        "audio_read": False,
        "inference_performed": False,
    }
    return {"cases": cases, "controls": admission_contract_block(),
            "summary": summary}


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": "audio-sdk/fsmn-vad-reference-bundle-contract/0.1",
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "condition_keys": list(CONDITION_KEYS),
        "outcome_keys": list(OUTCOME_KEYS),
        "right_keys": list(RIGHT_KEYS),
        "cohort_conditions": list(COHORT_CONDITIONS),
        "admissible_sample_rates_hz": list(ADMISSIBLE_SAMPLE_RATES),
        "max_files": MAX_MANIFEST_FILES,
        "max_file_bytes": MAX_MANIFEST_FILE_BYTES,
        "max_cohort_items": MAX_COHORT_ITEMS,
        "max_duration_ms": MAX_DURATION_MS,
        "max_hop_samples": MAX_HOP_SAMPLES,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_weights_invoked": False,
    }


def strictness_controls() -> dict:
    bad_json = (
        '{"a":1,"a":2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '[]',
        '{"a":1} trailing',
    )
    rejected_json = 0
    for text in bad_json:
        try:
            loads_strict(text)
        except ValueError:
            rejected_json += 1
    bad_pins = (
        "not-a-pin",
        "0" * 64 + " source:one",
        "0" * 63 + "  source:one",
        "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]),
        "0" * 64 + "  other:one",
    )
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = (
        "# no tables",
        "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
        "<!-- digest-table: end -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
        "| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    )
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except ValueError:
            rejected_readme += 1
    return {
        "json_cases": len(bad_json),
        "json_rejected": rejected_json,
        "pin_cases": len(bad_pins),
        "pin_rejected": rejected_pins,
        "readme_cases": len(bad_readme),
        "readme_rejected": rejected_readme,
        "all_adverse_parsers_rejected": (
            rejected_json == len(bad_json)
            and rejected_pins == len(bad_pins)
            and rejected_readme == len(bad_readme)),
    }


# ---------------------------------------------------------------------------
# SOURCES.sha256 and README digest tables.
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


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        "# SHA-256 pins for SDK-FSMN-VAD task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable full plan/swarm/TASKS.json is never hashed; only the "
        "stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  (source:[A-Za-z0-9_./-]+|"
    r"sdk:[A-Za-z0-9_./-]+|docs/task-evidence/fsmn-vad/[A-Za-z0-9_./-]+)$")


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
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = SOURCE_ROOT / key[len("source:"):]
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = WORKTREE / key[len("sdk:"):]
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
# Report blocks.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "source_snapshot",
         "The exact FunASR source checkout at an immutable 40-hex commit, with "
         "reviewed upstream license text, a per-file SHA-256 manifest and the "
         "streaming VAD entry point identified."),
        ("ART-02", "checkpoint_bundle",
         "The caller-selected FSMN-VAD checkpoint bundle "
         "(iic/speech_fsmn_vad_zh-cn-16k-common-pytorch or a caller-pinned "
         "variant) at an immutable 40-hex revision, including every weight, "
         "config, feature asset, model card and terms file with byte count "
         "and SHA-256."),
        ("ART-03", "runtime_lock",
         "A reproducible isolated Python and native/ONNX runtime with exact "
         "interpreter and package versions, a lock SHA-256, an offline load "
         "path and a recorded host profile."),
        ("ART-04", "rights_bundle",
         "Reviewed toolkit, checkpoint and model-card terms, training-data "
         "provenance, corpus rights, output use and redistribution for the "
         "exact assets. FunASR toolkit MIT does not automatically cover the "
         "checkpoint."),
        ("ART-05", "vad_cohort",
         "A frozen rights-cleared speech/nonspeech cohort with continuous "
         "truth, scored regions, preserved unknown spans, condition strata, "
         "known positives and negatives, timestamps and held-out splits."),
        ("ART-06", "vad_results",
         "Independent Analysis results for timestamped probabilities, event "
         "boundaries and detections, quiet/active speech, idle noise, "
         "onset/offset delay, stratified FN/FP, validity separation, "
         "independent state, exact source intervals, availability, "
         "dropped/stale events and cross-hop behavior."),
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
        ("BLK-01", "ART-01", ["RG-01", "RG-04"],
         "The exact FunASR/FSMN-VAD source checkout is absent. No reviewable "
         "tree at a 40-hex commit, upstream license text, per-file SHA-256 "
         "pin or streaming VAD entry point exists in the workspace. The "
         "census records only the toolkit and model identifiers.",
         "Supply the exact FunASR source at an immutable 40-hex commit with "
         "its reviewed license text, per-file SHA-256 pins and the identified "
         "streaming VAD entry point; do not substitute a mirror."),
        ("BLK-02", "ART-02", ["RG-01", "RG-04"],
         "The exact FSMN-VAD checkpoint bundle is absent. No weights, config, "
         "feature assets, model card or terms file for "
         "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch exist at an immutable "
         "40-hex revision with SHA-256 and byte counts; the census names the "
         "model but not a verified artifact.",
         "Supply the caller-selected exact checkpoint bundle at an immutable "
         "40-hex revision, every file with SHA-256 and byte count, and the "
         "reviewed model card and weight terms."),
        ("BLK-03", "ART-03", ["RG-04", "RG-07"],
         "The pinned isolated Python and native/ONNX runtime is absent. No "
         "interpreter, package lock, offline load path or host profile "
         "matching an FSMN-VAD runtime is present, so no probability or event "
         "vector can be reproduced.",
         "Supply a locked, reproducible Python and native/ONNX runtime with "
         "exact interpreter and package versions, lock SHA-256, offline load "
         "path and host profile."),
        ("BLK-04", "ART-04", ["RG-01", "RG-03"],
         "Toolkit, checkpoint and model-card terms, training-data provenance, "
         "corpus rights, output use and redistribution are unresolved. The "
         "FunASR toolkit MIT license does not establish checkpoint rights.",
         "Provide reviewed toolkit and checkpoint terms, training-data "
         "provenance, corpus rights, output use and redistribution approval."),
        ("BLK-05", "ART-05", ["RG-02", "RG-05"],
         "No rights-cleared, consented speech/nonspeech cohort exists. "
         "Continuous truth, scored regions, preserved unknown spans, "
         "condition strata, known positives and negatives, timestamps and "
         "held-out splits are absent.",
         "Supply the frozen permitted cohort with exact geometry, continuous "
         "truth, unknown spans preserved, condition strata and held-out "
         "splits."),
        ("BLK-06", "ART-06", ["RG-02", "RG-05", "RG-06", "RG-07", "RG-08"],
         "No Analysis evidence exists. Timestamped probabilities, event "
         "boundaries and detections, quiet/active speech, idle noise, "
         "onset/offset delay, stratified FN/FP, validity separation, "
         "independent state, exact source intervals, availability, "
         "dropped/stale events and cross-hop behavior are all unmeasured on "
         "the exact runtime.",
         "Run and preserve the independent Analysis protocol and "
         "target-runtime timing on the exact pinned source, checkpoint and "
         "runtime."),
    ]
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": linked_gates,
        "statement": statement,
        "required_action": action,
        "status": "open",
        "qualifies": False,
    } for blocker_id, artifact_id, linked_gates, statement, action in rows]


def release_gates() -> list[dict]:
    rows = [
        ("RG-01", "exact licensed source and checkpoint pinned",
         "The exact source, checkpoint, per-file digests and license terms are "
         "absent.",
         "Supply and pin the exact source and caller-selected checkpoint "
         "bundle with reviewed terms."),
        ("RG-02", "rights-cleared frozen cohort with continuous truth",
         "No rights-cleared speech/nonspeech cohort, continuous truth, unknown "
         "spans or held-out partition exists.",
         "Freeze the permitted cohort with continuous truth and preserved "
         "unknown spans."),
        ("RG-03", "toolkit, checkpoint and corpus rights",
         "Toolkit MIT does not establish checkpoint rights; training-data "
         "provenance, corpus rights and output use are unresolved.",
         "Record reviewed tool, checkpoint, training-data and corpus rights "
         "with notices."),
        ("RG-04", "pinned source, checkpoint, runtime and geometry",
         "No exact source revision, model revision, runtime lock or verified "
         "sample rate, hop, feature frontend, lookahead and threshold policy "
         "is pinned.",
         "Pin the source, checkpoint, runtime and geometry with exact "
         "digests."),
        ("RG-05", "timestamped probabilities, boundaries, detections and "
                  "stratified FN/FP",
         "No probability vector, event boundary, detection, onset/offset "
         "delay or stratified FN/FP result exists.",
         "Score timestamped probabilities, event boundaries and detections "
         "with stratified FN/FP on the frozen cohort."),
        ("RG-06", "state, exact source intervals, availability, dropped/stale "
                  "events and cross-hop behavior",
         "No independent state, exact interval mapping, availability, "
         "dropped/stale-event or cross-hop record exists.",
         "Measure state, exact source intervals, availability, dropped/stale "
         "events and cross-hop behavior on the exact runtime."),
        ("RG-07", "target-device pacing, memory and finite drain",
         "No target-device pacing, availability delay, memory or finite-drain "
         "measurement exists.",
         "Measure pacing, availability delay, memory and finite drain on the "
         "intended workload."),
        ("RG-08", "opt-in provider intake and independent review",
         "No adapter, descriptor, default-off intake decision or independent "
         "exact-head review exists.",
         "Add a task-local opt-in adapter only after RG-01 to RG-07 pass, then "
         "obtain independent exact-head review."),
    ]
    return [{
        "id": gate_id,
        "name": name,
        "status": "blocked",
        "qualifies": False,
        "reason": reason,
        "reopen_condition": reopen,
        "linked_row": _gate_link(),
    } for gate_id, name, reason, reopen in rows]


def historical_evidence_block() -> dict:
    return {
        "status": "no_local_historical_execution_found",
        "qualifies": False,
        "candidate": "FSMN VAD",
        "entries": [],
        "searched_pins": [
            CENSUS_PATH,
            NOISE_CENSUS_PATH,
            "audio-benchmark-platform/plan/INVENTORY.json",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/voice-enhancement-20261101/agent-vad-asr-trials/"
            "REPORT.md",
            "research/voice-enhancement-20261101/agent-segmentation/"
            "REPORT.md",
        ],
        "source_reported_context": {
            "toolkit": "FunASR",
            "model_id": MODEL_ID,
            "task_kind": TASK_KIND,
            "language_focus": LANGUAGE_FOCUS,
            "declared_sample_rate_hz": DECLARED_SAMPLE_RATE_HZ,
            "streaming_endpoint_detector": True,
            "start_end_sentinel_events": True,
            "chunk_finalization_adds_buffering": True,
            "reproduced_here": False,
            "admitted_as_result": False,
        },
        "not_reproduced_here": True,
        "no_values_inferred_from_adjacent_tasks": True,
        "note": "The pinned read-only records contain only an FSMN-VAD lead and "
                "source-reported context. No FSMN-VAD run, output, metric, "
                "corpus or runtime is recorded locally, and no adjacent VAD "
                "value is inherited.",
    }


def analysis_profile_block() -> dict:
    rows = [{
        "id": item_id,
        "requirement": requirement,
        "status": "blocked",
        "evidence": evidence,
        "qualification_effect": "none",
        "satisfied_for_qualification": False,
    } for item_id, requirement, evidence in ANALYSIS_REQUIREMENTS]
    return {
        "name": "analysis",
        "profile": PROFILE_KEY,
        "status": "blocked",
        "source_path": PROFILE_SOURCE_REL,
        "plan_note":
            "Framewise probabilities, event boundaries/detections, "
            "quiet/active speech, idle noise, known positives/negatives, "
            "onset/offset delay, stratified FN/FP, validity separation, "
            "independent state, exact source intervals, availability, "
            "dropped/stale events and cross-hop behavior are all unmeasured; "
            "no streaming or offline path is promoted.",
        "required_items": rows,
        "satisfied_for_qualification": [],
        "real_model_metrics": None,
        "timestamped_probabilities_measured": False,
        "event_boundaries_measured": False,
        "detections_measured": False,
        "quiet_speech_measured": False,
        "active_speech_measured": False,
        "idle_noise_measured": False,
        "known_positives_measured": False,
        "known_negatives_measured": False,
        "onset_offset_delay_measured": False,
        "stratified_fn_fp_measured": False,
        "validity_separation_measured": False,
        "independent_state_measured": False,
        "exact_source_intervals_measured": False,
        "availability_measured": False,
        "dropped_or_stale_events_measured": False,
        "cross_hop_behavior_measured": False,
        "corpus_rights_cleared": False,
        "output_use_cleared": False,
        "qualifies": False,
    }


def profile_source() -> dict:
    path = SOURCE_ROOT / PROFILE_SOURCE_REL
    expected = SOURCE_PINS[PROFILE_SOURCE_REL]
    if not path.is_file():
        raise ValueError("profile_source_missing")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError("profile_source_unpinned")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Analysis |")]
    if len(rows) != 1:
        raise ValueError("analysis_profile_row_not_unique")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("analysis_profile_phrase_missing:" + phrase)
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "path": PROFILE_SOURCE_REL,
        "sha256": actual,
        "row": row,
        "phrases": list(PROFILE_PHRASES),
    }


def disposition_block() -> dict:
    return {
        "promotion": "defer",
        "production_exposure": "DEFER",
        "status": "incomplete",
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "defer_before": DEFER_BEFORE,
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "provider_registration": False,
        "registered": False,
        "default_enabled": False,
        "descriptor_registry_change": False,
        "public_api_abi_change": False,
        "shared_cmakelists_change": False,
        "installed_v0_behavior_change": False,
        "ci_workflow_change": False,
        "board_changed": False,
        "handoff_changed": False,
        "files_outside_task_directory_written": False,
        "task_local_only": True,
    }


def scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "source_present": False,
        "source_executed": False,
        "weights_present": False,
        "weights_read": False,
        "runtime_present": False,
        "runtime_executed": False,
        "inference_performed": False,
        "real_corpus": False,
        "audio_read": False,
        "vad_scored": False,
        "probabilities_scored": False,
        "events_scored": False,
        "stratified_fn_fp_scored": False,
        "listening": False,
        "device_timing": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
        "historical_output_admitted": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "allowed_write_prefix": TASK_PREFIX,
        "provider_registration": False,
        "installed_v0_change": False,
        "public_api_abi_change": False,
        "shared_build_change": False,
        "ci_change": False,
        "board_or_handoff_change": False,
        "real_corpus": False,
        "weights": False,
        "runtime": False,
        "network": False,
        "release_claim": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16_000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def model_geometry() -> dict:
    return {
        "task_kind": TASK_KIND,
        "candidate_family": CANDIDATE_FAMILY,
        "upstream_toolkit": "FunASR",
        "inputs": ["waveform_16khz_mono_streaming_chunks"],
        "output": "frame_probabilities_and_start_end_events",
        "declared_sample_rate_hz": DECLARED_SAMPLE_RATE_HZ,
        "sample_rate_verified": False,
        "sample_rate_source":
            "model identifier names 16k; exact preprocessing, feature "
            "frontend and frame grid are not verified here",
        "channels": 1,
        "channels_verified": False,
        "language_focus": LANGUAGE_FOCUS,
        "streaming_endpoint_detector": True,
        "stateful_ordered_chunks": True,
        "start_end_sentinel_events": True,
        "chunk_finalization_adds_buffering": True,
        "hop_samples": None,
        "lookahead_samples": None,
        "threshold_policy_pinned": False,
        "feature_geometry_pinned": False,
        "installed_v0": False,
        "provider_registered": False,
    }


def upstream_record() -> dict:
    return {
        "toolkit_repository": TOOLKIT_REPOSITORY,
        "streaming_vad_docs": STREAMING_VAD_DOCS,
        "model_id": MODEL_ID,
        "source_revision": None,
        "source_revision_requirement":
            "immutable 40-hex FunASR commit, verified from a reviewable "
            "checkout",
        "source_license": None,
        "source_license_requirement":
            "reviewed upstream license with exact SPDX identifier and license "
            "SHA-256",
        "model_revision": None,
        "model_revision_requirement": "immutable 40-hex checkpoint revision",
        "model_file_requirement":
            "every weight, config, feature asset, model card and terms file "
            "with byte count and SHA-256",
        "declared_sample_rate_hz": DECLARED_SAMPLE_RATE_HZ,
        "channels": 1,
        "task_kind": TASK_KIND,
        "language_focus": LANGUAGE_FOCUS,
        "toolkit_license_reported": "MIT (toolkit only; checkpoint rights "
                                    "unresolved)",
        "checkpoint_rights_status": "unresolved",
        "streaming_endpoint_detector": True,
        "chunk_finalization_adds_buffering": True,
        "present": False,
        "executed": False,
        "digest_asserted": False,
    }


def rights_gap() -> dict:
    return {
        "code_license": "unverified_source_absent",
        "weights_terms": "unresolved",
        "training_data_provenance": "unresolved",
        "corpus_rights": "unresolved",
        "output_use": "unresolved",
        "redistribution": "unresolved",
        "toolkit_mit_covers_checkpoint": False,
        "all_resolved": False,
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "blocked_gate_count": 8,
        "blocked_gate_ids": [row["id"] for row in release_gates()],
        "exact_source_present": False,
        "exact_weights_present": False,
        "exact_runtime_present": False,
        "exact_licensed_conjunction_present": False,
        "rights_cleared": False,
        "vad_cohort_present": False,
        "analysis_evaluation_present": False,
        "timestamped_probabilities_result": False,
        "event_boundary_result": False,
        "detection_result": False,
        "onset_offset_delay_result": False,
        "stratified_fn_fp_result": False,
        "validity_separation_result": False,
        "independent_state_result": False,
        "availability_result": False,
        "cross_hop_result": False,
        "benchmark_result": False,
        "release_qualification_present": False,
        "missing_result_promoted": False,
        "no_missing_result_qualifies_candidate": True,
        "candidate_qualified": False,
        "reason": "Exact source, checkpoint, runtime, rights and cohort are "
                  "absent; no Analysis result exists.",
        "not_qualified": True,
    }


def pin_rows(pins: dict[str, str], root: Path) -> dict:
    rows = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("pinned_bytes_changed:" + relative)
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": True,
        }
    return rows


def linked_identity_block() -> dict:
    projection = board_row_projection()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
    }


def _assert_absence(probes: list[dict]) -> None:
    if any(row.get("present") is not False for row in probes):
        raise ValueError("absence_probe_appeared")


# ---------------------------------------------------------------------------
# Merge-base scope helpers (used by verify.py).
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
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
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
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
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": model_geometry(),
        "upstream_record": upstream_record(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "gates": release_gates(),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "board_row_projection": board_row_projection(),
        "board_row_sha256": board_row_digest(board_row_projection()),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "rights_gap": rights_gap(),
        "analysis_profile": analysis_profile_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "admission_schema": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
        "write_scope": TASK_PREFIX,
        "qualification": qualification_block(),
        "reproduction": {
            "interpreter": "Python 3.12.16",
            "cold_start_regenerations": 3,
            "byte_identical_required": True,
            "network_required": False,
            "runtime_required": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    probes = absence_probes()
    _assert_absence(probes)
    identity = linked_identity_block()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "component_id": COMPONENT_ID,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "format": FORMAT,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": model_geometry(),
        "upstream_record": upstream_record(),
        "source_probe": source_probe(),
        "weights_probe": weights_probe(),
        "runtime_probe": runtime_probe(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": identity,
        "task_row_identity": {
            "source": BOARD_TASK_ROW,
            "stable_fields": identity["projection"],
            "stable_sha256": identity["sha256"],
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_FIELDS_EXCLUDED),
        },
        "analysis_profile": analysis_profile_block(),
        "qualification": qualification_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "strictness": strictness_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, SOURCE_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": "Python 3.12.16",
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3 run.py",
                "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                "test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            ],
        },
        "write_scope": TASK_PREFIX,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("contract_id_mismatch")
    if contract.get("task") != TASK or contract.get("task_id") != TASK:
        raise ValueError("contract_task_mismatch")
    if contract.get("title") != TITLE:
        raise ValueError("contract_title_mismatch")
    if contract.get("component") != COMPONENT:
        raise ValueError("contract_component_mismatch")
    if contract.get("mode") != MODE:
        raise ValueError("contract_mode_mismatch")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch_mismatch")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_mismatch")
    if contract.get("worktree") != CLAIM_WORKTREE:
        raise ValueError("contract_worktree_mismatch")
    if contract.get("reviewer") != REVIEWER:
        raise ValueError("contract_reviewer_mismatch")
    if contract.get("profile") != PROFILE:
        raise ValueError("contract_profile_mismatch")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status_mismatch")
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision_mismatch")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_mismatch")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("source_pins") != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    if [row.get("id") for row in gates] != ["RG-0" + str(i)
                                             for i in range(1, 9)]:
        raise ValueError("contract_gate_ids")
    for row in gates:
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked:" + str(row.get("id")))
        if row.get("linked_row") != _gate_link():
            raise ValueError("contract_gate_link")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open:" + str(row.get("id")))
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 6:
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True):
            raise ValueError("contract_artifact_not_blocked:" +
                             str(row.get("id")))
    qualification = contract.get("qualification", {})
    if (qualification.get("status") != QUALIFICATION_STATUS
            or qualification.get("readiness") != "incomplete"
            or qualification.get("all_release_gates_blocked") is not True
            or qualification.get("candidate_qualified") is not False):
        raise ValueError("contract_qualification_invalid")
    assert_no_float(contract)
